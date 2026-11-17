#!/usr/bin/env python3
"""forever-mcp : serveur MCP (stdio) qui donne à Claude l'état réel des persos WoW Forever.

Lit les captures de l'addon ForeverScribe (via sync.py) et expose des outils :
list_characters, set_active_character, register_account, get_character, get_stats,
get_equipment, get_talents, get_spells, get_quests, get_professions, get_inventory,
get_reputations, get_pet, get_progress, compare_item, compare_characters,
get_quest_rewards, get_overview, search_knowledge, save_knowledge.

Protocole : JSON-RPC 2.0, un message par ligne sur stdin/stdout (transport stdio MCP).
Bibliothèque standard Python uniquement (3.9+).
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import formats as F  # noqa: E402
import gear as G  # noqa: E402
import knowledge as K  # noqa: E402
from luasv import as_list  # noqa: E402
from sync import Store, diff_states, load_json  # noqa: E402

SERVER_NAME = "forever-mcp"
SERVER_VERSION = "0.4.0"
SUPPORTED_PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
AP_PER_DPS = 14.0  # confirmé par l'infobulle de Forever (17/11/2026)

INSTRUCTIONS = (
    "État réel des personnages WoW Forever du joueur, capturé en jeu par l'addon ForeverScribe. "
    "Utilise ces outils AVANT de répondre à une question qui dépend du perso (niveau, zone, équipement, "
    "quêtes, métiers, talents, familier). Sans paramètre `perso`, l'outil vise le perso actif "
    "(le dernier capturé). Cite toujours la fraîcheur indiquée dans l'en-tête ; si elle dépasse une heure, "
    "propose au joueur de synchroniser en jeu (Ctrl+Maj+S, /sync ou le bouton ForeverScribe). "
    "Pour une question générale, commence par get_overview (un seul appel). Avant toute recherche web, "
    "consulte search_knowledge ; après une trouvaille utile, enregistre-la avec save_knowledge."
)

PERSO = {"type": "string", "description": "Perso visé : nom (Brannok), Nom-Région, Utilisateur/Nom ou GUID. "
                                          "Facultatif : par défaut le perso actif."}


# ----------------------------------------------------------------------------
# Outils
# ----------------------------------------------------------------------------

class Tools:
    def __init__(self, store: Store):
        self.store = store

    # -- utilitaires -----------------------------------------------------------
    def _char(self, args: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        char, err = self.store.resolve(args.get("perso"))
        if not char:
            raise ToolError(err)
        db = self.store.load(char)
        if not db:
            raise ToolError(f"Aucune donnée synchronisée pour {char.get('name')}. Synchronise en jeu (Ctrl+Maj+S ou /sync).")
        return char, db

    @staticmethod
    def _head(db: Dict[str, Any], *lines: str) -> str:
        out = [F.header(db)]
        rep = F.g(db, "meta", "repairedFromPrevious")
        if rep:
            out.append(f"_Note : {', '.join(rep)} repris de la capture précédente (valeurs vides à la déconnexion)._")
        return "\n".join(out + [""] + [ln for ln in lines if ln is not None])

    # -- liste et sélection ----------------------------------------------------
    def list_characters(self, args: Dict[str, Any]) -> str:
        chars = self.store.characters()
        active = self.store.active()
        cfg = self.store.config
        lines = []
        if not chars:
            lines.append("Aucun perso connu. En jeu : active l'addon ForeverScribe, connecte un perso, puis Ctrl+Maj+S (ou /sync).")
        by_user: Dict[str, List[Dict[str, Any]]] = {}
        for c in chars:
            by_user.setdefault(c.get("user", "?"), []).append(c)
        for user, lst in by_user.items():
            lines.append(f"**{user}**")
            for c in lst:
                mark = " ← actif" if active and c["guid"] == active["guid"] else ""
                if c.get("captured"):
                    lines.append(f"- {c.get('name')}-{c.get('suffix')} ({c.get('region')}, {c.get('ruleset', '?')}) · "
                                 f"{c.get('race')} {c.get('class')} {c.get('level')} · {c.get('zone') or '?'} · "
                                 f"capturé {F.age(c.get('lastCapture'))}{mark}")
                else:
                    lines.append(f"- {c.get('name')}-{c.get('suffix')} · {c.get('race')} {c.get('class')} "
                                 f"{c.get('level')} · connu de l'addon mais pas encore synchronisé (connecte-le puis Ctrl+Maj+S (ou /sync))")
        unc = self.store.last_report.get("uncaptured") or []
        if unc:
            lines.append("\nPersos présents dans le jeu mais jamais capturés par l'addon : " + ", ".join(
                f"{u['dir']} ({u['user']})" for u in unc) + ". Connecte-les avec ForeverScribe actif, puis Ctrl+Maj+S (ou /sync).")
        pending = cfg.get("accountsPending") or []
        if pending:
            lines.append("\nComptes sans prénom : " + ", ".join(
                f"{a} (affiché « {cfg['accounts'].get(a)} »)" for a in pending)
                + ". Demande au joueur à qui ils appartiennent, puis register_account.")
        lines.append(f"\nDossier des données : {self.store.data_dir}")
        return "\n".join(lines)

    def set_active_character(self, args: Dict[str, Any]) -> str:
        if not args.get("perso"):
            raise ToolError("Indique le perso : nom, Nom-Région ou Utilisateur/Nom.")
        char, err = self.store.resolve(args["perso"])
        if not char:
            raise ToolError(err)
        self.store.set_active(char)
        return (f"Perso actif : {char.get('name')}-{char.get('suffix')} ({char.get('user')}). "
                "Il le reste jusqu'à ce qu'un autre perso soit capturé plus récemment.")

    def register_account(self, args: Dict[str, Any]) -> str:
        if not args.get("account") or not args.get("user"):
            raise ToolError("Paramètres requis : account (dossier WTF/Account) et user (prénom).")
        return self.store.register_account(args["account"], args["user"])

    # -- fiches ------------------------------------------------------------------
    def get_character(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        q = F.g(db, "quests", default={})
        done = [x for x in as_list(q.get("list")) if x.get("complete")]
        prof = ", ".join(f"{p.get('name')} {p.get('rank')}/{p.get('max')}"
                         for p in as_list(F.g(db, "professions", "professions"))) or "aucun"
        pet = F.g(db, "pet", "current") if F.g(db, "pet", "active") else F.g(db, "pet", "lastSeen")
        eq = F.g(db, "equipment", "slots", default={}) or {}
        weapons = []
        for slot in ("RangedSlot", "MainHandSlot", "SecondaryHandSlot"):
            it = eq.get(slot)
            if it and it.get("dps"):
                weapons.append(f"{F.SLOT_FR[slot]} : {it.get('name')} ({F.fr_num(it['dps'], 1)} DPS)")
        lines = [
            *F.render_identity(db),
            *F.render_progression(db),
            *F.render_position(db),
            *F.render_combat(db)[:4],
            "- Armes : " + (" · ".join(weapons) or "?"),
            f"- Métiers : {prof}",
            (f"- Familier : {pet.get('name')} ({pet.get('family')}) niveau {pet.get('level')}"
             + ("" if F.g(db, 'pet', 'active') else " — renvoyé") if pet else "- Familier : aucun"),
            *F.render_bags_summary(db),
            f"- Quêtes : {q.get('count', '?')}/{q.get('max', '?')} dans le journal, {len(done)} à rendre · "
            f"{F.g(db, 'questsCompleted', 'count', default='?')} terminées au total",
        ]
        probs = F.problems(db)
        if probs:
            lines.append("- Données non lues : " + " ; ".join(probs))
        reason = F.g(db, "meta", "lastSyncReason")
        lines.append(f"\nCompte {char.get('account')} ({char.get('user')}) · capture du "
                     f"{F.local_time(F.captured_at(db))}" + (f" · origine : {reason}" if reason else ""))
        return self._head(db, *lines)

    def get_stats(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        st = F.g(db, "stats", default={})
        extra = []
        r = st.get("ranged") or {}
        if r.get("attackPower") is not None:
            extra.append(f"- Valeur de la PA à distance : {F.fr_num(r['attackPower'] / AP_PER_DPS, 1)} DPS "
                         f"(14 PA = 1 DPS, confirmé dans Forever)")
            extra.append(f"- Munitions : {'oui' if r.get('usesAmmo') else 'non'}")
        extra.append(f"- Régénération de mana : {F.fr_num(F.g(st, 'manaRegen', 'base'), 1)} (hors incantation)")
        extra.append(f"- Défense : {st.get('defense', '?')} · crit des sorts {F.fr_num(F.g(st, 'spell', 'crit'), 1)} %")
        return self._head(db, f"_Stats capturées {F.domain_age(db, 'stats')}._", *F.render_combat(db), *extra)

    def get_equipment(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        return self._head(db, f"_Équipement capturé {F.domain_age(db, 'equipment')}._",
                          *F.render_equipment_table(db, show_tooltip=bool(args.get("details"))))

    def get_talents(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        cur = as_list(F.g(db, "talents", "currencies"))
        extra = [f"- Points : {c.get('spent')}/{c.get('max')} dépensés, {c.get('available')} disponibles" for c in cur]
        return self._head(db, f"_Talents capturés {F.domain_age(db, 'talents')}._", *F.render_talents(db), *extra)

    def get_spells(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        return self._head(db, f"_Sorts capturés {F.domain_age(db, 'spells')}._",
                          *F.render_spells(db, args.get("ligne")))

    def get_quests(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        has_rewards = bool(G.quest_rewards(db))
        note = "" if has_rewards else (" Récompenses inconnues : elles apparaissent avec l'addon 1.2 "
                                       "après une synchro (Ctrl+Maj+S).")
        return self._head(db, f"_Journal capturé {F.domain_age(db, 'quests')}. Couleurs : difficulté par rapport "
                              "au niveau du perso. `/way` = coordonnées sur la carte de la quête." + note + "_",
                          *F.render_quests(db, args.get("zone"), bool(args.get("en_cours_seulement")),
                                           reward_line=lambda q: reward_summary(db, q)))

    # -- récompenses et vue d'ensemble -------------------------------------------
    def get_quest_rewards(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        pairs = G.quest_rewards(db)
        if not pairs:
            return self._head(db, "Récompenses de quête inconnues : elles sont capturées par l'addon "
                                  "ForeverScribe 1.2 ou plus. Mets l'addon à jour, puis synchronise en jeu "
                                  "(Ctrl+Maj+S). En attendant, ne présente pas de récompense comme certaine.")
        zone = args.get("zone")
        if zone:
            z = F.norm_key(zone)
            pairs = [(q, r) for q, r in pairs if z in F.norm_key(q.get("category")) or z in F.norm_key(q.get("title"))]
        only_done = bool(args.get("a_rendre"))
        if only_done:
            pairs = [(q, r) for q, r in pairs if q.get("complete")]
        ups_done, ups_open, rest = [], [], []
        for q, r in pairs:
            best, evals = G.best_choice(db, r)
            (ups_done if (best and q.get("complete")) else ups_open if best else rest).append((q, r, best, evals))
        lines = []
        if ups_done:
            lines.append("**À rendre maintenant, avec une amélioration :**")
            for q, r, best, _ in sorted(ups_done, key=lambda x: -x[2]["score"]):
                lines.append(f"- **{q.get('title')}** → {reward_pick(best)}" + quest_where(q))
        if ups_open:
            lines.append("\n**En cours, avec une amélioration à la clé :**")
            for q, r, best, _ in sorted(ups_open, key=lambda x: -x[2]["score"]):
                lines.append(f"- **{q.get('title')}** (niv. {q.get('level')}) → {reward_pick(best)}" + quest_where(q))
        if not ups_done and not ups_open:
            lines.append("**Aucune récompense de quête connue n'améliore ton équipement.**")
        lines.append("\nDétail par quête :")
        for q, r, best, evals in [*ups_done, *ups_open, *rest]:
            state = " ✔ à rendre" if q.get("complete") else ""
            money_xp = ", ".join(x for x in (F.money(r.get("money")) if r.get("money") else "",
                                               f"{F.fr_num(r.get('xp'))} XP" if r.get("xp") else "") if x)
            lines.append(f"- **{q.get('title')}** (niv. {q.get('level')}){state}" + (f" · {money_xp}" if money_xp else ""))
            for ev in evals:
                it = ev["item"]
                tag = "fixe" if ev.get("fixed") else "au choix"
                lines.append(f"  - {tag} : {it.get('name')} ({G.describe(it)}) — {ev['verdict']}"
                             + (f" ({G.gain_text(ev)})" if G.gain_text(ev) and ev.get("slot") else "")
                             + (f" · {ev['reason']}" if ev.get("reason") and ev["verdict"] == "pas pour toi" else ""))
            for f in as_list(r.get("factions")):
                lines.append(f"  - réputation : {f.get('name') or f.get('factionId')} +{F.fr_num(f.get('amount'))}")
            if r.get("pending"):
                lines.append("  - _un objet n'était pas encore chargé par le jeu : resynchronise pour le détail_")
        missing = [q for q in as_list(F.g(db, "quests", "list")) if not isinstance(q.get("rewards"), dict)]
        if missing:
            lines.append(f"\n_{len(missing)} quête(s) sans récompenses capturées (journal ouvert pendant la capture, "
                         "ou capture ancienne) : resynchronise._")
        lines.append("\n_Gains estimés en coups blancs (14 PA = 1 DPS, confirmé) ; maîtrises d'armes et d'armures "
                     "selon Classic, à vérifier dans Forever — le drapeau « utilisable » du jeu prime._")
        return self._head(db, f"_Journal capturé {F.domain_age(db, 'quests')}._", *lines)

    def get_overview(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        q = F.g(db, "quests", default={})
        qlist = as_list(q.get("list"))
        done = [x for x in qlist if x.get("complete")]
        eq = F.g(db, "equipment", "slots", default={}) or {}
        weapons = []
        for slot in ("RangedSlot", "MainHandSlot", "SecondaryHandSlot"):
            it = eq.get(slot)
            if it:
                weapons.append(f"{F.SLOT_FR[slot]} : {it.get('name')}"
                               + (f" ({F.fr_num(it['dps'], 1)} DPS)" if it.get("dps") else ""))
        lines = [
            *F.render_identity(db)[:2],
            *F.render_progression(db)[:1],
            *F.render_position(db)[:1],
            *F.render_combat(db)[:2],
            "- Armes : " + (" · ".join(weapons) or "aucune"),
        ]
        empty = G.empty_slots(db)
        if empty:
            lines.append(f"- Emplacements vides : {', '.join(empty)} — vide ne veut pas dire faible : ne conseille "
                         "pas de les remplir sans un objet précis disponible à ce niveau (récompense, donjon, "
                         "artisanat, marchand).")
        lines += F.render_bags_summary(db)
        lines.append(f"- Quêtes : {q.get('count', '?')}/{q.get('max', '?')}"
                     + (" (journal plein)" if q.get("count") and q.get("count") == q.get("max") else "")
                     + f", {len(done)} à rendre")
        pairs = G.quest_rewards(db)
        if done:
            lines.append("\n**Quêtes à rendre :**")
            for x in done[:15]:
                best = G.best_choice(db, x["rewards"])[0] if isinstance(x.get("rewards"), dict) else None
                lines.append(f"- {x.get('title')}" + quest_where(x) + (f" → {reward_pick(best)}" if best else ""))
        if pairs:
            ups = []
            for qq, r in pairs:
                best = G.best_choice(db, r)[0]
                if best and not qq.get("complete"):
                    ups.append((qq, best))
            if ups:
                lines.append("\n**Améliorations à gagner en finissant des quêtes en cours :**")
                for qq, best in sorted(ups, key=lambda x: -x[1]["score"])[:5]:
                    lines.append(f"- {qq.get('title')} (niv. {qq.get('level')}) → {reward_pick(best)}")
        else:
            lines.append("\n_Récompenses de quête inconnues (addon antérieur à 1.2) : synchronise avec l'addon à jour._")
        probs = F.problems(db)
        if probs:
            lines.append("- Données non lues : " + " ; ".join(probs))
        lines.append("\nPour le détail : get_equipment, get_inventory, get_quest_rewards, get_talents, get_professions.")
        return self._head(db, *lines)

    # -- mémoire de recherche ------------------------------------------------------
    def search_knowledge(self, args: Dict[str, Any]) -> str:
        question = (args.get("question") or "").strip()
        if not question:
            raise ToolError("Indique la question ou les mots-clés à chercher.")
        hits = K.search(self.store.data_dir, question, int(args.get("limite") or 5))
        folder = K.knowledge_dir(self.store.data_dir)
        if not hits:
            return (f"Rien dans la mémoire de recherche pour « {question} » ({folder}). "
                    "Cherche ailleurs (knowledge/ du plugin, puis le web), puis enregistre la trouvaille "
                    "avec save_knowledge.")
        out = [f"Mémoire de recherche ({folder}) — {len(hits)} note(s) :"]
        for score, note in hits:
            body = note.get("body", "")
            if len(body) > 1200:
                body = body[:1200].rsplit(" ", 1)[0] + " …"
            out.append(f"\n### {note.get('sujet', note['file'])}\n"
                       f"_{note.get('date', '?')} · certitude : {note.get('certitude', '?')} · "
                       f"sources : {note.get('sources') or 'non notées'} · fichier {note['file']}_\n\n{body}")
        out.append("\n_Une note « probable » ou ancienne se recoupe avant d'être affirmée ; une note contredite "
                   "par le jeu se corrige avec save_knowledge._")
        return "\n".join(out)

    def save_knowledge(self, args: Dict[str, Any]) -> str:
        try:
            path = K.save(self.store.data_dir, args.get("sujet") or "", args.get("contenu") or "",
                          sources=as_list(args.get("sources")), certainty=args.get("certitude") or "probable",
                          keywords=as_list(args.get("mots_cles")) or None,
                          game_version=args.get("version_jeu"))
        except ValueError as exc:
            raise ToolError(str(exc))
        return f"Enregistré dans la mémoire de recherche : {path}"

    def get_professions(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        lines = F.render_professions(db, with_recipes=True)
        skills = as_list(F.g(db, "professions", "skills"))
        weap = [s for s in skills if "arme" in F.norm_key(s.get("category")) or "weapon" in F.norm_key(s.get("category"))]
        if weap:
            lines.append("\nCompétences d'armes : " + ", ".join(f"{s.get('name')} {s.get('rank')}/{s.get('max')}" for s in weap))
        return self._head(db, f"_Métiers capturés {F.domain_age(db, 'professions')}._", *lines)

    def get_inventory(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        return self._head(db, f"_Sacs capturés {F.domain_age(db, 'bags')}._",
                          *F.render_inventory(db, include_bank=args.get("banque", True)))

    def get_reputations(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        cur = as_list(F.g(db, "currencies", "list"))
        extra = []
        if cur:
            extra.append("\nMonnaies : " + ", ".join(f"{c.get('name')} {F.fr_num(c.get('quantity'))}"
                                                    + (f"/{F.fr_num(c['max'])}" if c.get("max") else "") for c in cur))
        return self._head(db, f"_Réputations capturées {F.domain_age(db, 'reputations')}._",
                          *F.render_reputations(db), *extra)

    def get_pet(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        if F.g(db, "identity", "classFile") != "HUNTER" and not F.g(db, "pet", "hasPetUI"):
            return self._head(db, "Ce perso n'a pas de familier de chasseur.")
        return self._head(db, f"_Familier capturé {F.domain_age(db, 'pet')}._", *F.render_pet(db))

    # -- progression ----------------------------------------------------------------
    def get_progress(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        folder = self.store.folder(char)
        since_raw = (args.get("depuis") or "").strip().lower()
        today = datetime.now().date()
        if since_raw in ("", "semaine"):
            since = today - timedelta(days=7)
        elif since_raw in ("aujourd'hui", "aujourdhui", "today"):
            since = today
        elif since_raw in ("hier", "yesterday"):
            since = today - timedelta(days=1)
        else:
            try:
                since = datetime.strptime(since_raw[:10], "%Y-%m-%d").date()
            except ValueError:
                raise ToolError("Format de date attendu : AAAA-MM-JJ, « hier », « aujourd'hui » ou « semaine ».")
        snaps = sorted((folder / "historique").glob("*.json"))
        base = None
        before = [s for s in snaps if s.stem < since.isoformat()]
        if before:
            base = load_json(before[-1], {}).get("data")
            base_label = f"fin de journée du {before[-1].stem}"
        elif snaps:
            base = load_json(snaps[0], {}).get("data")
            base_label = f"première capture ({snaps[0].stem})"
        lines = []
        if base is None or base is db:
            lines.append("Pas encore d'historique : il se construit à chaque synchro (un instantané par jour).")
        else:
            events = diff_states(base, db)
            lp, ln = F.g(base, "progression", "level"), F.g(db, "progression", "level")
            tp0, tp1 = F.g(base, "progression", "timePlayed", "total"), F.g(db, "progression", "timePlayed", "total")
            lines.append(f"Depuis la {base_label} :")
            played = f"temps de jeu +{F.duration(tp1 - tp0)}" if tp0 and tp1 and tp1 > tp0 else ""
            if lp and ln and ln != lp:
                lines.append(f"- Niveau {lp} → {ln}" + (f" · {played}" if played else ""))
            elif played:
                lines.append(f"- {played.capitalize()}")
            m0, m1 = F.g(base, "money", "copper"), F.g(db, "money", "copper")
            if isinstance(m0, int) and isinstance(m1, int) and m0 != m1:
                lines.append(f"- Argent : {F.money(m0)} → {F.money(m1)}")
            lines += [f"- {e}" for e in events]
            if len(lines) == 1:
                lines.append("- Aucun changement notable.")
        journal = folder / "journal.md"
        if journal.exists():
            recent = [ln for ln in journal.read_text(encoding="utf-8").splitlines()
                      if ln.startswith("- ") and ln[2:12] >= since.isoformat()]
            if recent:
                lines.append("\nJournal sur la période :")
                lines += recent[:40]
        return self._head(db, *lines)

    # -- comparaisons ----------------------------------------------------------------
    def compare_item(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        cls = F.g(db, "identity", "classFile") or ""
        eq = F.g(db, "equipment", "slots", default={}) or {}
        cand: Dict[str, Any] = {}
        name = args.get("nom") or "objet proposé"
        # objet désigné par son ID
        if args.get("itemId"):
            iid = int(args["itemId"])
            found = next(((s, it) for s, it in eq.items() if it.get("itemId") == iid), None)
            if found:
                cand = dict(found[1])
                name = cand.get("name", name)
                args.setdefault("emplacement", found[0])
            else:
                where = None
                for dom in ("bags", "bank"):
                    for c in (F.g(db, dom, "containers", default={}) or {}).values():
                        for it in as_list(c.get("items")):
                            if it.get("itemId") == iid:
                                where = (dom, it)
                if where:
                    name = where[1].get("name", name)
                if not any(args.get(k) is not None for k in ("dps", "agilite", "force", "endurance", "intelligence",
                                                               "esprit", "pa", "pa_distance", "armure")):
                    raise ToolError(f"Je connais « {name} » ({'dans tes sacs' if where else 'objet inconnu'}) mais pas "
                                    "ses stats : l'addon ne lit les stats que des objets équipés. Donne-moi ses stats "
                                    "(DPS, agilité, PA…) en paramètres.")
        stats = {
            "Agi": args.get("agilite"), "For": args.get("force"), "End": args.get("endurance"),
            "Int": args.get("intelligence"), "Esp": args.get("esprit"), "PA": args.get("pa"),
            "PA distance": args.get("pa_distance"), "Armure": args.get("armure"),
        }
        cstats = F.item_stats(cand) if cand else {}
        for k, v in stats.items():
            if v is not None:
                cstats[k] = float(v)
        dps = args.get("dps")
        if dps is None and args.get("degats_min") is not None and args.get("degats_max") is not None and args.get("vitesse"):
            dps = (float(args["degats_min"]) + float(args["degats_max"])) / 2 / float(args["vitesse"])
        if dps is None and cand.get("dps"):
            dps = cand["dps"]
        # emplacement
        slot = None
        raw_slot = args.get("emplacement")
        if raw_slot:
            slot = raw_slot if raw_slot in F.SLOT_FR else F.SLOT_ALIASES.get(F.norm_key(raw_slot))
            if not slot:
                raise ToolError(f"Emplacement « {raw_slot} » inconnu. Exemples : distance, main droite, tête, doigt 2.")
        elif dps is not None:
            slot = "RangedSlot" if cls == "HUNTER" else "MainHandSlot"
        else:
            raise ToolError("Indique l'emplacement (ex. « distance », « mains », « doigt 1 »).")
        cur = eq.get(slot) or {}
        ostats = F.item_stats(cur)
        odps = cur.get("dps") or 0.0

        # coefficients (hypothèses Classic, vérifiées pour le chasseur par la fiche du perso) : voir gear.py
        def delta(k: str) -> float:
            return float(cstats.get(k, 0) or 0) - float(ostats.get(k, 0) or 0)

        est = G.estimate(db, slot, cstats, float(dps) if dps is not None else None, cur)
        ranged_slot = slot == "RangedSlot"
        melee_slot = slot in ("MainHandSlot", "SecondaryHandSlot")
        d_rdps, d_mdps = est["ranged"], est["melee"]
        r_now = F.g(db, "stats", "ranged", "dps")
        m_now = F.g(db, "stats", "melee", "dps")

        rows = ["| | Équipé : " + (cur.get("name") or "rien") + f" | {name} |", "|---|---|---|"]
        if ranged_slot or melee_slot:
            rows.append(f"| DPS de l'arme | {F.fr_num(odps, 1) if odps else '—'} | "
                        f"{F.fr_num(dps, 1) if dps is not None else '?'} |")
        keys = sorted(set(cstats) | set(ostats), key=lambda k: (F.STAT_ORDER.index(k) if k in F.STAT_ORDER else 50, k))
        for k in keys:
            rows.append(f"| {k} | {F.fr_num(ostats.get(k, 0), 1)} | {F.fr_num(cstats.get(k, 0), 1)} |")
        main_is_ranged = cls == "HUNTER" or ranged_slot
        if r_now is not None and (main_is_ranged or abs(d_rdps) > 0.05):
            rows.append(f"| **DPS à distance (coups blancs)** | {F.fr_num(r_now, 1)} | "
                        f"**≈ {F.fr_num(r_now + d_rdps, 1)}** ({'+' if d_rdps >= 0 else ''}{F.fr_num(d_rdps, 1)}) |")
        if m_now is not None and (not main_is_ranged or melee_slot or abs(d_mdps) > 0.05):
            rows.append(f"| DPS en mêlée (coups blancs) | {F.fr_num(m_now, 1)} | "
                        f"≈ {F.fr_num(m_now + d_mdps, 1)} ({'+' if d_mdps >= 0 else ''}{F.fr_num(d_mdps, 1)}) |")
        key_delta = d_rdps if main_is_ranged else d_mdps
        base_dps = (r_now if main_is_ranged else m_now) or 0
        pct_txt = f" ({'+' if key_delta >= 0 else ''}{F.fr_num(100 * key_delta / base_dps, 1)} %)" if base_dps else ""
        if key_delta > 0.3:
            verdict = f"**À prendre : environ {('+' if key_delta >= 0 else '')}{F.fr_num(key_delta, 1)} DPS{pct_txt}.**"
        elif key_delta < -0.3:
            verdict = f"**À ne pas équiper : environ {F.fr_num(key_delta, 1)} DPS{pct_txt}.**"
        else:
            verdict = "**Quasi équivalent en dégâts** : départage avec l'endurance ou l'armure."
        notes = [
            "Hypothèses : 14 PA = 1 DPS (confirmé dans Forever) ; "
            + ({"HUNTER": "1 Agi = 2 PA à distance et 1 PA en mêlée, 1 For = 1 PA en mêlée (cohérent avec la fiche du perso)"}
               .get(cls, "conversions For/Agi → PA reprises de Classic, à vérifier dans Forever")) + ".",
            "Non chiffré : le crit apporté par l'Agilité, les effets spéciaux (« Chance quand vous touchez… »).",
        ]
        if delta("End"):
            notes.append(f"Endurance : {'+' if delta('End') > 0 else ''}{F.fr_num(delta('End'))} (≈ {F.fr_num(delta('End') * 10)} PV, hypothèse Classic).")
        wskill = weapon_skill_note(db, args.get("type_arme") or name or "", slot)
        if wskill:
            notes.insert(0, wskill)
        if cur.get("requiredLevel") is not None and args.get("niveau_requis") and int(args["niveau_requis"]) > (F.g(db, "progression", "level") or 0):
            notes.append(f"Niveau requis {args['niveau_requis']} : pas encore équipable.")
        return self._head(db, verdict, "", *rows, "", *[f"- {n}" for n in notes])

    def compare_characters(self, args: Dict[str, Any]) -> str:
        chars = [c for c in self.store.characters() if c.get("captured")]
        if args.get("persos"):
            wanted = []
            for q in args["persos"]:
                c, err = self.store.resolve(q)
                if not c:
                    raise ToolError(err)
                wanted.append(c)
            chars = wanted
        if not chars:
            raise ToolError("Aucun perso capturé.")
        rows = ["| Perso | Joueur | Classe | Niveau | Zone | ilvl | Argent | Métiers | Capturé |",
                "|---|---|---|---|---|---|---|---|---|"]
        prof_index: Dict[str, List[str]] = {}
        for c in chars:
            db = self.store.load(c) or {}
            profs = as_list(F.g(db, "professions", "professions"))
            for p in profs:
                prof_index.setdefault(p.get("name"), []).append(f"{c.get('name')} {p.get('rank')}/{p.get('max')}")
            prof_txt = ", ".join(f"{p.get('name')} {p.get('rank')}" for p in profs) or "—"
            rows.append(
                f"| {c.get('name')}-{c.get('suffix')} | {c.get('user')} | {F.g(db, 'identity', 'race', default='?')} "
                f"{F.g(db, 'identity', 'class', default='?')} | {F.g(db, 'progression', 'level', default='?')} | "
                f"{F.g(db, 'position', 'zone', default='?')} | {F.fr_num(F.g(db, 'stats', 'itemLevel', 'equipped'), 1)} | "
                f"{F.money(F.g(db, 'money', 'copper'))} | {prof_txt} | {F.age(F.captured_at(db))} |")
        lines = rows
        if prof_index:
            lines.append("\nQui fait quoi :")
            for prof, who in sorted(prof_index.items()):
                lines.append(f"- {prof} : {', '.join(who)}")
        return "\n".join(lines)


WEAPON_SKILLS = [("arbal", "arbaletes"), ("arc", "arcs"), ("fusil", "armes a feu"), ("arme a feu", "armes a feu"),
                 ("epee", "epees"), ("hache", "haches"), ("dague", "dagues"), ("masse", "masses"),
                 ("hast", "armes d hast"), ("baton", "batons"), ("poing", "armes de pugilat"),
                 ("lance", "armes de jet"), ("baguette", "baguettes")]


def weapon_skill_note(db: Dict[str, Any], text: str, slot: str) -> Optional[str]:
    """Avertit si la compétence d'arme correspondant au type proposé est basse."""
    if slot not in ("RangedSlot", "MainHandSlot", "SecondaryHandSlot"):
        return None
    key = F.norm_key(text)
    target = next((sk for kw, sk in WEAPON_SKILLS if kw in key), None)
    if not target:
        return None
    for s in as_list(F.g(db, "professions", "skills")):
        if F.norm_key(s.get("name")).startswith(target):
            rank, mx = s.get("rank") or 0, s.get("max") or 0
            if mx and rank < 0.8 * mx:
                return (f"**Attention, compétence {s.get('name')} : {rank}/{mx}.** Avec une compétence basse, beaucoup "
                        f"de tirs ou de coups ratent au début : le gain réel n'arrive qu'après l'avoir montée en "
                        f"l'utilisant [Classic · probable dans Forever, la compétence existe en jeu].")
            return None
    return (f"Compétence d'arme pour « {text} » introuvable dans la capture : vérifie en jeu que tu sais "
            f"l'utiliser (maître d'armes).")


def reward_pick(ev: Optional[Dict[str, Any]]) -> str:
    if not ev:
        return ""
    it = ev["item"]
    gain = G.gain_text(ev)
    where = f"{ev.get('slot_fr', '?')}" + (f", remplace {ev['replaces']}" if ev.get("replaces") else ", emplacement vide")
    return (f"**{it.get('name')}** ({G.describe(it)}) — {ev['verdict']}"
            + (f", {gain}" if gain else "") + f" [{where}]" + (" (fixe)" if ev.get("fixed") else " (au choix)"))


def quest_where(q: Dict[str, Any]) -> str:
    pos = q.get("position") or {}
    return f" · `/way {pos.get('x')} {pos.get('y')}`" if pos.get("x") is not None else ""


def reward_summary(db: Dict[str, Any], q: Dict[str, Any]) -> Optional[str]:
    r = q.get("rewards")
    if not isinstance(r, dict):
        return None
    best, evals = G.best_choice(db, r)
    bits = []
    if best:
        bits.append("à prendre : " + reward_pick(best))
    elif evals:
        names = ", ".join(e["item"].get("name") or "?" for e in evals[:4])
        bits.append(f"objets : {names} (rien de mieux pour toi)")
    if r.get("money"):
        bits.append(F.money(r["money"]))
    if r.get("xp"):
        bits.append(f"{F.fr_num(r['xp'])} XP")
    return ("Récompense : " + " · ".join(bits)) if bits else None


class ToolError(Exception):
    pass


def schema(props: Dict[str, Any], required: Optional[List[str]] = None) -> Dict[str, Any]:
    s: Dict[str, Any] = {"type": "object", "properties": props, "additionalProperties": False}
    if required:
        s["required"] = required
    return s


TOOL_DEFS: List[Dict[str, Any]] = [
    {"name": "list_characters", "title": "Persos connus",
     "description": "Liste tous les persos de tous les joueurs (comptes) avec niveau, zone, fraîcheur de la capture "
                    "et le perso actif. À appeler quand on ne sait pas de quel perso il s'agit.",
     "inputSchema": schema({})},
    {"name": "set_active_character", "title": "Changer de perso actif",
     "description": "Change le perso visé par défaut (ex. « je joue mon mage »). Reste actif jusqu'à ce qu'un autre "
                    "perso soit capturé plus récemment.",
     "inputSchema": schema({"perso": PERSO}, ["perso"])},
    {"name": "register_account", "title": "Nommer un compte",
     "description": "Rattache un compte WoW (dossier WTF/Account/<compte>) à un prénom, pour séparer les joueurs "
                    "qui partagent l'ordinateur. Déplace les dossiers des persos de ce compte.",
     "inputSchema": schema({"account": {"type": "string", "description": "dossier du compte, ex. 123456789#1"},
                            "user": {"type": "string", "description": "prénom du joueur, ex. Pierre"}},
                           ["account", "user"])},
    {"name": "get_character", "title": "Fiche du perso",
     "description": "Fiche synthétique : identité, niveau et XP, position avec coordonnées, stats clés, armes, métiers, "
                    "familier, argent, sacs, quêtes. Premier outil à appeler pour toute question sur le perso.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_stats", "title": "Stats détaillées",
     "description": "Caractéristiques, PA mêlée et distance, dégâts, vitesse, crit, esquive, armure, résistances.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_equipment", "title": "Équipement",
     "description": "Objets équipés par emplacement : nom, niveau d'objet, stats, DPS des armes, durabilité, coût de réparation.",
     "inputSchema": schema({"perso": PERSO, "details": {"type": "boolean", "description": "ajoute le texte des infobulles"}})},
    {"name": "get_talents", "title": "Talents",
     "description": "Spé, points dépensés et libres, talents pris avec leur rang.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_spells", "title": "Sorts connus",
     "description": "Livre de sorts par ligne (Maîtrise des bêtes, Précision, Survie…) avec les rangs, pour savoir quoi "
                    "aller apprendre chez le maître de classe.",
     "inputSchema": schema({"perso": PERSO, "ligne": {"type": "string", "description": "filtre sur une ligne de sorts"}})},
    {"name": "get_quests", "title": "Journal de quêtes",
     "description": "Quêtes en cours groupées par zone : niveau, couleur de difficulté, objectifs et progression, "
                    "coordonnées /way, quêtes à rendre, nombre de quêtes terminées.",
     "inputSchema": schema({"perso": PERSO,
                            "zone": {"type": "string", "description": "filtre : zone ou mot du titre"},
                            "en_cours_seulement": {"type": "boolean", "description": "masque les quêtes à rendre"}})},
    {"name": "get_professions", "title": "Métiers",
     "description": "Métiers et niveaux, recettes connues (si la fenêtre du métier a été ouverte) et celles qui font "
                    "encore monter le métier, compétences d'armes.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_inventory", "title": "Sacs et banque",
     "description": "Argent, places libres, munitions, contenu des sacs et de la banque (si elle a été ouverte).",
     "inputSchema": schema({"perso": PERSO, "banque": {"type": "boolean", "description": "inclure la banque (défaut : oui)"}})},
    {"name": "get_reputations", "title": "Réputations",
     "description": "Réputations par faction (palier et progression) et monnaies.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_pet", "title": "Familier",
     "description": "Familier du chasseur : famille, niveau, XP, bonheur, loyauté, points de dressage, nourriture, "
                    "techniques, et familiers à l'écurie.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_progress", "title": "Progression",
     "description": "Ce qui a changé depuis une date (niveaux, quêtes rendues, objets, métiers, réputations, talents), "
                    "à partir de l'historique quotidien et du journal automatique.",
     "inputSchema": schema({"perso": PERSO,
                            "depuis": {"type": "string",
                                       "description": "AAAA-MM-JJ, « hier », « aujourd'hui » ou « semaine » (défaut)"}})},
    {"name": "compare_item", "title": "Comparer un objet",
     "description": "Compare un objet (stats données en paramètres, ou itemId d'un objet équipé) à celui porté au même "
                    "emplacement : tableau des stats et DPS effectif estimé (14 PA = 1 DPS, confirmé dans Forever).",
     "inputSchema": schema({
         "perso": PERSO,
         "emplacement": {"type": "string", "description": "distance, main droite, main gauche, tête, mains, doigt 1… "
                                                          "(défaut pour une arme : distance pour un chasseur)"},
         "nom": {"type": "string", "description": "nom de l'objet proposé"},
         "itemId": {"type": "integer"},
         "dps": {"type": "number", "description": "DPS de l'arme"},
         "degats_min": {"type": "number"}, "degats_max": {"type": "number"},
         "vitesse": {"type": "number", "description": "vitesse de l'arme en secondes"},
         "agilite": {"type": "number"}, "force": {"type": "number"}, "endurance": {"type": "number"},
         "intelligence": {"type": "number"}, "esprit": {"type": "number"},
         "pa": {"type": "number", "description": "puissance d'attaque (mêlée et distance)"},
         "pa_distance": {"type": "number", "description": "puissance d'attaque à distance seulement"},
         "armure": {"type": "number"}, "niveau_requis": {"type": "integer"},
         "type_arme": {"type": "string", "description": "arc, fusil, arbalète, épée, hache, dague, masse, bâton… "
                                                        "(sert à vérifier la compétence d'arme)"},
     })},
    {"name": "get_overview", "title": "Vue d'ensemble",
     "description": "En un seul appel : fiche du perso, armes, emplacements vides, sacs, quêtes à rendre avec la "
                    "meilleure récompense pour ce perso, améliorations à gagner en finissant des quêtes, fraîcheur. "
                    "Premier appel conseillé pour « évalue mon stuff », « je fais quoi ? », ou toute question générale.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_quest_rewards", "title": "Récompenses de quête",
     "description": "Récompenses des quêtes du journal (objets au choix et fixes, argent, XP, réputation), évaluées "
                    "pour ce perso : maîtrise d'arme/armure, emplacement, gain estimé par rapport à l'équipé. "
                    "Met en avant les quêtes à rendre qui donnent une amélioration.",
     "inputSchema": schema({"perso": PERSO,
                            "zone": {"type": "string", "description": "filtre : zone ou mot du titre"},
                            "a_rendre": {"type": "boolean", "description": "seulement les quêtes à rendre"}})},
    {"name": "search_knowledge", "title": "Chercher dans la mémoire de recherche",
     "description": "Cherche dans les trouvailles déjà enregistrées par l'agent (dossier connaissances/ du joueur). "
                    "À appeler AVANT toute recherche web : une même question ne doit pas être recherchée deux fois.",
     "inputSchema": schema({"question": {"type": "string", "description": "question ou mots-clés"},
                            "limite": {"type": "integer", "description": "nombre de notes (défaut 5)"}},
                           ["question"])},
    {"name": "save_knowledge", "title": "Enregistrer une trouvaille",
     "description": "Enregistre une trouvaille utile (après une recherche web ou une vérification en jeu) dans la "
                    "mémoire de recherche du joueur, avec ses sources et sa certitude, pour ne pas la rechercher "
                    "à nouveau. Une note par sujet ; contenu factuel et court.",
     "inputSchema": schema({"sujet": {"type": "string", "description": "titre court, ex. « Casques cuir niveau 20-30 (Alliance) »"},
                            "contenu": {"type": "string", "description": "la trouvaille en Markdown (objets nommés, niveaux, sources de loot, /way)"},
                            "sources": {"type": "array", "items": {"type": "string"}, "description": "URL ou « vu en jeu »"},
                            "certitude": {"type": "string", "description": "« sûr », « probable » ou « à vérifier » (+ précision, ex. « probable [Classic] »)"},
                            "mots_cles": {"type": "array", "items": {"type": "string"}},
                            "version_jeu": {"type": "string", "description": "ex. 1.60.1"}},
                           ["sujet", "contenu", "certitude"])},
    {"name": "compare_characters", "title": "Comparer les persos",
     "description": "Tableau de tous les persos (ou d'une sélection) : classe, niveau, zone, ilvl, argent, métiers, "
                    "et qui a quel métier (utile pour savoir qui peut fabriquer un objet).",
     "inputSchema": schema({"persos": {"type": "array", "items": {"type": "string"},
                                       "description": "noms des persos (défaut : tous)"}})},
]


# ----------------------------------------------------------------------------
# Boucle JSON-RPC
# ----------------------------------------------------------------------------

class Server:
    def __init__(self, store: Optional[Store] = None):
        self.store = store or Store()
        self.tools = Tools(self.store)
        self.last_sync = 0.0

    def log(self, msg: str) -> None:
        print(f"[{SERVER_NAME}] {msg}", file=sys.stderr, flush=True)

    def ensure_sync(self) -> None:
        # la synchro ne relit que les fichiers modifiés : peu coûteuse
        if time.time() - self.last_sync < 2:
            return
        try:
            rep = self.store.refresh()
            if rep.get("updated"):
                self.log(f"synchro : {', '.join(rep['updated'])}")
            for e in rep.get("errors", []):
                self.log(f"synchro : {e}")
        except Exception as exc:  # la synchro ne doit jamais casser un outil
            self.log(f"synchro impossible : {exc}")
        self.last_sync = time.time()

    def handle(self, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = msg.get("method")
        mid = msg.get("id")
        if mid is None:  # notification
            return None
        try:
            if method == "initialize":
                requested = (msg.get("params") or {}).get("protocolVersion")
                version = requested if requested in SUPPORTED_PROTOCOLS else SUPPORTED_PROTOCOLS[0]
                result: Any = {
                    "protocolVersion": version,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": SERVER_NAME, "title": "WoW Forever : état des persos",
                                   "version": SERVER_VERSION},
                    "instructions": INSTRUCTIONS,
                }
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": TOOL_DEFS}
            elif method == "tools/call":
                params = msg.get("params") or {}
                name = params.get("name")
                args = params.get("arguments") or {}
                fn: Optional[Callable[[Dict[str, Any]], str]] = getattr(self.tools, name, None) \
                    if name in {t["name"] for t in TOOL_DEFS} else None
                if not fn:
                    return self.error(mid, -32602, f"Outil inconnu : {name}")
                self.ensure_sync()
                try:
                    text = fn(args)
                    result = {"content": [{"type": "text", "text": text}], "isError": False}
                except ToolError as exc:
                    result = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
                except Exception as exc:
                    self.log(traceback.format_exc())
                    result = {"content": [{"type": "text", "text": f"Erreur interne de {name} : {exc}"}], "isError": True}
            elif method in ("resources/list", "prompts/list"):
                result = {method.split("/")[0]: []}
            else:
                return self.error(mid, -32601, f"Méthode inconnue : {method}")
        except Exception as exc:
            self.log(traceback.format_exc())
            return self.error(mid, -32603, str(exc))
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    @staticmethod
    def error(mid: Any, code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

    def serve(self) -> None:
        stdin = sys.stdin.buffer
        out = sys.stdout
        self.log(f"démarré · données : {self.store.data_dir}")
        for raw in stdin:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                out.write(json.dumps(self.error(None, -32700, "JSON invalide")) + "\n")
                out.flush()
                continue
            batch = msg if isinstance(msg, list) else [msg]
            responses = [r for r in (self.handle(m) for m in batch if isinstance(m, dict)) if r]
            if responses:
                payload = responses if isinstance(msg, list) else responses[0]
                out.write(json.dumps(payload, ensure_ascii=False) + "\n")
                out.flush()


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except AttributeError:
        pass
    Server().serve()


if __name__ == "__main__":
    main()
