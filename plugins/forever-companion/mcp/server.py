#!/usr/bin/env python3
"""forever-mcp: MCP server (stdio) that gives Claude the real state of the player's WoW Forever characters.

Reads the ForeverScribe addon captures (through sync.py) and exposes tools:
list_characters, set_active_character, register_account, get_character, get_stats,
get_equipment, get_talents, get_spells, get_quests, get_professions, get_inventory,
get_reputations, get_pet, get_progress, compare_item, compare_characters,
get_quest_rewards, get_overview, search_knowledge, save_knowledge; and, when the local game
database is built (gamedata/build.py): find_items, get_item, find_upgrades, get_dungeon_loot,
find_recipes, get_quest_info, find_quests, find_npc (quests and NPCs from QuestieDB, downloaded on
the player's machine by gamedata/questie.py).

Output language: French or English (see i18n.py). Every tool accepts an optional `lang`
argument ("fr" / "en"); otherwise `answer_language` from perso/config.json, otherwise the
client locale of the character (frFR -> fr, any other -> en). Game names (items, quests,
zones) always stay in the game client's language.

Protocol: JSON-RPC 2.0, one message per line on stdin/stdout (MCP stdio transport).
Python standard library only (3.9+).
"""

from __future__ import annotations

import base64
import json
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import formats as F  # noqa: E402
import gamedb as GDB  # noqa: E402
import gear as G  # noqa: E402
import i18n as I  # noqa: E402
from gamedb_tools import GameDBToolsMixin  # noqa: E402
from intent_tools import IntentToolsMixin  # noqa: E402
from questdb_tools import QuestDBToolsMixin  # noqa: E402
from forever_quests import ForeverQuestsMixin  # noqa: E402
from worldmap import WorldMapToolsMixin  # noqa: E402
from i18n import T  # noqa: E402
import knowledge as K  # noqa: E402
from luasv import as_list  # noqa: E402
from sync import Store, diff_states, load_json  # noqa: E402

SERVER_NAME = "forever-mcp"
SERVER_VERSION = "0.10.0"
SUPPORTED_PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
AP_PER_DPS = 14.0  # confirmé par l'infobulle de Forever (17/11/2026)

RULES_FILE = Path(__file__).resolve().parents[1] / "knowledge" / "regles-forever.md"


def _rules() -> str:
    """Règles Forever toujours chargées (knowledge/regles-forever.md, sans son en-tête de fichier)."""
    try:
        text = RULES_FILE.read_text(encoding="utf-8")
    except OSError:
        return ""
    body = text.split("\n## ", 1)
    return ("## " + body[1]).strip() if len(body) == 2 else text.strip()


INSTRUCTIONS = (
    "Real state of the player's WoW Forever characters (ForeverScribe addon) plus a local game database "
    "(client files, Forever hotfixes, QuestieDB). One intent tool answers most questions in ONE call: overview "
    "(what to do now, precomputed at each sync), gear, quests, npc, item, professions, pet, talents, dungeon, "
    "bags, reputations, characters, map (zone map PNG with /way markers), search (any name, FR/EN, notes included: before any web search), "
    "save_knowledge (after a web finding). Without `perso` a tool targets the active character. Pass "
    "`lang` = language of the question; game names stay in the client's language. Tools start with a one-line "
    "verdict: reuse or refine it. Rules below (French) apply in every answer.\n\n"
) + _rules()

PERSO = {"type": "string", "description": "default: active character"}
LANG = {"type": "string", "enum": ["en", "fr"]}
DETAIL = {"type": "string", "description": "court (default) | normal | complet"}


# ----------------------------------------------------------------------------
# Outils
# ----------------------------------------------------------------------------

class Tools(IntentToolsMixin, ForeverQuestsMixin, QuestDBToolsMixin, GameDBToolsMixin, WorldMapToolsMixin):
    server_version = SERVER_VERSION

    def __init__(self, store: Store):
        self.store = store
        self._locale: Optional[str] = None
        self._pre: Optional[Tuple[str, Dict[str, Any]]] = None

    # -- langue ------------------------------------------------------------------
    def prepare(self, args: Dict[str, Any]) -> str:
        """Retire `lang` des arguments, repère la langue du client du perso visé ; renvoie la langue de sortie."""
        explicit = I.norm_lang(args.pop("lang", None))
        self._locale, self._pre = None, None
        self._call_stamp = object()  # budget Wowhead remis à zéro à chaque appel d'outil
        try:
            char, _ = self.store.resolve(args.get("perso"))
            if char:
                db = self.store.load(char)
                if db:
                    self._pre = (char["guid"], db)
                    self._locale = F.game_locale(db)
        except Exception:  # la langue ne doit jamais casser un outil
            pass
        if explicit:
            return explicit
        try:
            configured = I.norm_lang(self.store.config.get("answer_language"))
        except Exception:
            configured = None
        return configured or I.lang_from_locale(self._locale) or "en"

    # -- utilitaires -----------------------------------------------------------
    def _char(self, args: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        char, err = self.store.resolve(args.get("perso"))
        if not char:
            raise ToolError(err)
        pre = getattr(self, "_pre", None)
        db = pre[1] if pre and pre[0] == char.get("guid") else self.store.load(char)
        if not db:
            raise ToolError(T("Aucune donnée synchronisée pour {name}. Synchronise en jeu (Ctrl+Maj+S ou /sync).",
                              name=char.get('name')))
        return char, db

    @staticmethod
    def _head(db: Dict[str, Any], *lines: str) -> str:
        """En-tête d'une ligne (nom, niveau, âge de la capture) : l'en-tête complet est dans overview."""
        return "\n".join([F.header_short(db), ""] + [ln for ln in lines if ln is not None])

    @staticmethod
    def _head_full(db: Dict[str, Any], *lines: str) -> str:
        out = [F.header(db)]
        rep = F.g(db, "meta", "repairedFromPrevious")
        if rep:
            out.append("_" + T("Note : {domains} repris de la capture précédente (valeurs vides à la déconnexion).",
                               domains=", ".join(rep)) + "_")
        return "\n".join(out + [""] + [ln for ln in lines if ln is not None])

    # -- liste et sélection ----------------------------------------------------
    def list_characters(self, args: Dict[str, Any]) -> str:
        chars = self.store.characters()
        active = self.store.active()
        cfg = self.store.config
        lines = []
        if not chars:
            lines.append(T("Aucun perso connu. En jeu : active l'addon ForeverScribe, connecte un perso, puis "
                           "Ctrl+Maj+S (ou /sync)."))
        by_user: Dict[str, List[Dict[str, Any]]] = {}
        for c in chars:
            by_user.setdefault(c.get("user", "?"), []).append(c)
        for user, lst in by_user.items():
            lines.append(f"**{user}**")
            for c in lst:
                mark = T(" ← actif") if active and c["guid"] == active["guid"] else ""
                if c.get("captured"):
                    lines.append(f"- {c.get('name')}-{c.get('suffix')} ({c.get('region')}, {c.get('ruleset', '?')}) · "
                                 f"{c.get('race')} {c.get('class')} {c.get('level')} · {c.get('zone') or '?'} · "
                                 + T("capturé {age}", age=F.age(c.get('lastCapture'))) + mark)
                else:
                    lines.append(f"- {c.get('name')}-{c.get('suffix')} · {c.get('race')} {c.get('class')} "
                                 f"{c.get('level')} · " + T("connu de l'addon mais pas encore synchronisé "
                                                           "(connecte-le puis Ctrl+Maj+S (ou /sync))"))
        unc = self.store.last_report.get("uncaptured") or []
        if unc:
            lines.append(T("\nPersos présents dans le jeu mais jamais capturés par l'addon : {list}. Connecte-les "
                           "avec ForeverScribe actif, puis Ctrl+Maj+S (ou /sync).",
                           list=", ".join(f"{u['dir']} ({u['user']})" for u in unc)))
        pending = cfg.get("accountsPending") or []
        if pending:
            lines.append(T("\nComptes sans prénom : {list}. Demande au joueur à qui ils appartiennent, puis "
                           "register_account.", list=", ".join(
                               T("{acc} (affiché « {name} »)", acc=a, name=cfg['accounts'].get(a)) for a in pending)))
        lines.append(T("\nDossier des données : {path}", path=self.store.data_dir))
        return "\n".join(lines)

    def set_active_character(self, args: Dict[str, Any]) -> str:
        if not args.get("perso"):
            raise ToolError(T("Indique le perso : nom, Nom-Région ou Utilisateur/Nom."))
        char, err = self.store.resolve(args["perso"])
        if not char:
            raise ToolError(err)
        self.store.set_active(char)
        return T("Perso actif : {name}-{suffix} ({user}). Il le reste jusqu'à ce qu'un autre perso soit capturé "
                 "plus récemment.", name=char.get('name'), suffix=char.get('suffix'), user=char.get('user'))

    def register_account(self, args: Dict[str, Any]) -> str:
        if not args.get("account") or not args.get("user"):
            raise ToolError(T("Paramètres requis : account (dossier WTF/Account) et user (prénom)."))
        return self.store.register_account(args["account"], args["user"])

    # -- fiches ------------------------------------------------------------------
    def get_character(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        q = F.g(db, "quests", default={})
        done = [x for x in as_list(q.get("list")) if x.get("complete")]
        prof = ", ".join(f"{p.get('name')} {p.get('rank')}/{p.get('max')}"
                         for p in as_list(F.g(db, "professions", "professions"))) or T("aucun")
        pet = F.g(db, "pet", "current") if F.g(db, "pet", "active") else F.g(db, "pet", "lastSeen")
        eq = F.g(db, "equipment", "slots", default={}) or {}
        weapons = []
        for slot in ("RangedSlot", "MainHandSlot", "SecondaryHandSlot"):
            it = eq.get(slot)
            if it and it.get("dps"):
                weapons.append(f"{F.slot_label(slot)}{F.sep()}{it.get('name')} ({F.num(it['dps'], 1)} DPS)")
        if pet:
            pet_line = T("- Familier : {name} ({family}) niveau {level}", name=pet.get('name'),
                         family=pet.get('family'), level=pet.get('level')) \
                + ("" if F.g(db, 'pet', 'active') else T(" — renvoyé"))
        else:
            pet_line = T("- Familier : aucun")
        lines = [
            *F.render_identity(db),
            *F.render_progression(db),
            *F.render_position(db),
            *F.render_combat(db)[:4],
            T("- Armes : {list}", list=" · ".join(weapons) or "?"),
            T("- Métiers : {list}", list=prof),
            pet_line,
            *F.render_bags_summary(db),
            T("- Quêtes : {n}/{max} dans le journal, {done} à rendre · {total} terminées au total",
              n=q.get('count', '?'), max=q.get('max', '?'), done=len(done),
              total=F.g(db, 'questsCompleted', 'count', default='?')),
        ]
        probs = F.problems(db)
        if probs:
            lines.append(T("- Données non lues : {list}", list=F.semi().join(probs)))
        reason = F.g(db, "meta", "lastSyncReason")
        lines.append(T("\nCompte {account} · capture du {time}", account=F.mask_account(char.get('account')),
                       time=F.local_time(F.captured_at(db)))
                     + (T(" · origine : {reason}", reason=reason) if reason else "")
                     + T(" · langue du jeu : {locale}", locale=F.game_locale(db) or "?"))
        return self._head_full(db, *lines)

    def get_stats(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        st = F.g(db, "stats", default={})
        extra = []
        r = st.get("ranged") or {}
        if r.get("attackPower") is not None:
            extra.append(T("- Valeur de la PA à distance : {dps} DPS (14 PA = 1 DPS, confirmé dans Forever)",
                           dps=F.num(r['attackPower'] / AP_PER_DPS, 1)))
            extra.append(T("- Munitions : {yes}", yes=T("oui") if r.get('usesAmmo') else T("non")))
        extra.append(T("- Régénération de mana : {n} (hors incantation)", n=F.num(F.g(st, 'manaRegen', 'base'), 1)))
        extra.append(T("- Défense : {def} · crit des sorts {crit}{pc}", **{"def": st.get('defense', '?')},
                       crit=F.num(F.g(st, 'spell', 'crit'), 1), pc=F.pct_sign()))
        return self._head(db, "_" + T("Stats capturées {age}.", age=F.domain_age(db, 'stats')) + "_",
                          *F.render_combat(db), *extra)

    def get_equipment(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        return self._head(db, "_" + T("Équipement capturé {age}.", age=F.domain_age(db, 'equipment')) + "_",
                          *F.render_equipment_table(db, show_tooltip=bool(args.get("details"))))

    def get_talents(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        cur = as_list(F.g(db, "talents", "currencies"))
        extra = [T("- Points : {spent}/{max} dépensés, {free} disponibles", spent=c.get('spent'), max=c.get('max'),
                   free=c.get('available')) for c in cur]
        tree = args.get("arbre")
        if tree:  # arbre complet de la classe (table talents de la base locale) : talents_tree.py
            import talents_tree as TT
            full = str(tree).lower() == "complet" or args.get("detail") == "complet"
            extra += TT.render(self.gamedb(required=False), db, "complet" if full else "court")
        return self._head(db, "_" + T("Talents capturés {age}.", age=F.domain_age(db, 'talents')) + "_",
                          *F.render_talents(db), *extra)

    def get_spells(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        return self._head(db, "_" + T("Sorts capturés {age}.", age=F.domain_age(db, 'spells')) + "_",
                          *F.render_spells(db, args.get("ligne")))

    def get_quests(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        has_rewards = bool(G.quest_rewards(db))
        note = "" if has_rewards else T(" Récompenses inconnues : elles apparaissent avec l'addon 1.2 après une "
                                        "synchro (Ctrl+Maj+S).")
        return self._head(db, "_" + T("Journal capturé {age}. Couleurs : difficulté par rapport au niveau du perso. "
                                      "`/way` = coordonnées sur la carte de la quête.",
                                      age=F.domain_age(db, 'quests')) + note + "_",
                          *F.render_quests(db, args.get("zone"), bool(args.get("en_cours_seulement")),
                                           reward_line=lambda q: reward_summary(db, q),
                                           where=lambda q: self.turnin_where(db, q)))

    # -- récompenses et vue d'ensemble -------------------------------------------
    def get_quest_rewards(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        self.enrich_rewards(db)
        pairs = G.quest_rewards(db)
        if not pairs:
            return self._head(db, T("Récompenses de quête inconnues : elles sont capturées par l'addon "
                                    "ForeverScribe 1.2 ou plus. Mets l'addon à jour, puis synchronise en jeu "
                                    "(Ctrl+Maj+S). En attendant, ne présente pas de récompense comme certaine."))
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
            lines.append(T("**À rendre maintenant, avec une amélioration :**"))
            for q, r, best, _ in sorted(ups_done, key=lambda x: -x[2]["score"]):
                lines.append(f"- **{q.get('title')}** → {reward_pick(best)}" + self.turnin_where(db, q))
        if ups_open:
            lines.append(T("\n**En cours, avec une amélioration à la clé :**"))
            for q, r, best, _ in sorted(ups_open, key=lambda x: -x[2]["score"]):
                lines.append(f"- **{q.get('title')}** (" + T("niv. {n}", n=q.get('level')) + f") → {reward_pick(best)}"
                             + self.turnin_where(db, q))
        if not ups_done and not ups_open:
            lines.append(T("**Aucune récompense de quête connue n'améliore ton équipement.**"))
        lines.append(T("\nDétail par quête :"))
        for q, r, best, evals in [*ups_done, *ups_open, *rest]:
            state = T(" ✔ à rendre") if q.get("complete") else ""
            money_xp = ", ".join(x for x in (F.money(r.get("money")) if r.get("money") else "",
                                               f"{F.num(r.get('xp'))} XP" if r.get("xp") else "") if x)
            lines.append(f"- **{q.get('title')}** (" + T("niv. {n}", n=q.get('level')) + f"){state}"
                         + (f" · {money_xp}" if money_xp else ""))
            for ev in evals:
                it = ev["item"]
                tag = T("fixe") if ev.get("fixed") else T("au choix")
                lines.append(f"  - {tag}{F.sep()}{it.get('name')} ({G.describe(it)}) — {ev['verdict']}"
                             + (f" ({G.gain_text(ev)})" if G.gain_text(ev) and ev.get("slot") else "")
                             + (f" · {ev['reason']}" if ev.get("reason") and ev.get("code") == "not_for_you" else ""))
            for f in as_list(r.get("factions")):
                lines.append(T("  - réputation : {name} +{n}", name=f.get('name') or f.get('factionId'),
                               n=F.num(f.get('amount'))))
            if r.get("pending"):
                lines.append("  - _" + T("un objet n'était pas encore chargé par le jeu : resynchronise pour le "
                                         "détail") + "_")
        missing = [q for q in as_list(F.g(db, "quests", "list")) if not isinstance(q.get("rewards"), dict)]
        if missing:
            lines.append("\n_" + T("{n} quête(s) sans récompenses capturées (journal ouvert pendant la capture, "
                                   "ou capture ancienne) : resynchronise.", n=len(missing)) + "_")
        lines.append("\n_" + T("Gains estimés en coups blancs (14 PA = 1 DPS, confirmé) ; maîtrises d'armes et "
                               "d'armures selon Classic, à vérifier dans Forever — le drapeau « utilisable » du jeu "
                               "prime.") + "_")
        return self._head(db, "_" + T("Journal capturé {age}.", age=F.domain_age(db, 'quests')) + "_", *lines)

    def get_overview(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        self.enrich_rewards(db)
        q = F.g(db, "quests", default={})
        qlist = as_list(q.get("list"))
        done = [x for x in qlist if x.get("complete")]
        eq = F.g(db, "equipment", "slots", default={}) or {}
        weapons = []
        for slot in ("RangedSlot", "MainHandSlot", "SecondaryHandSlot"):
            it = eq.get(slot)
            if it:
                weapons.append(f"{F.slot_label(slot)}{F.sep()}{it.get('name')}"
                               + (f" ({F.num(it['dps'], 1)} DPS)" if it.get("dps") else ""))
        lines = [
            *F.render_identity(db)[:2],
            *F.render_progression(db)[:1],
            *F.render_position(db)[:1],
            *F.render_combat(db)[:2],
            T("- Armes : {list}", list=" · ".join(weapons) or T("aucune")),
        ]
        empty = G.empty_slots(db)
        if empty:
            lines.append(T("- Emplacements vides : {list} — vide ne veut pas dire faible : ne conseille pas de les "
                           "remplir sans un objet précis disponible à ce niveau (récompense, donjon, artisanat, "
                           "marchand).", list=", ".join(empty)))
        lines += F.render_bags_summary(db)
        lines.append(T("- Quêtes : {n}/{max}", n=q.get('count', '?'), max=q.get('max', '?'))
                     + (T(" (journal plein)") if q.get("count") and q.get("count") == q.get("max") else "")
                     + T(", {n} à rendre", n=len(done)))
        pairs = G.quest_rewards(db)
        if done:
            lines.append(T("\n**Quêtes à rendre :**"))
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
                lines.append(T("\n**Améliorations à gagner en finissant des quêtes en cours :**"))
                for qq, best in sorted(ups, key=lambda x: -x[1]["score"])[:5]:
                    lines.append(f"- {qq.get('title')} (" + T("niv. {n}", n=qq.get('level')) + f") → {reward_pick(best)}")
        else:
            lines.append("\n_" + T("Récompenses de quête inconnues (addon antérieur à 1.2) : synchronise avec "
                                   "l'addon à jour.") + "_")
        lines += self.overview_upgrades(db)
        probs = F.problems(db)
        if probs:
            lines.append(T("- Données non lues : {list}", list=F.semi().join(probs)))
        lines.append(T("\nPour le détail : get_equipment, get_inventory, get_quest_rewards, get_talents, "
                       "get_professions, find_upgrades."))
        return self._head_full(db, *lines)

    # -- mémoire de recherche ------------------------------------------------------
    def search_knowledge(self, args: Dict[str, Any]) -> str:
        question = (args.get("question") or "").strip()
        if not question:
            raise ToolError(T("Indique la question ou les mots-clés à chercher."))
        hits = K.search(self.store.data_dir, question, int(args.get("limite") or 5))
        folder = K.knowledge_dir(self.store.data_dir)
        if not hits:
            return T("Rien dans la mémoire de recherche pour « {q} » ({folder}). Cherche ailleurs (knowledge/ du "
                     "plugin, puis le web), puis enregistre la trouvaille avec save_knowledge.",
                     q=question, folder=folder)
        out = [T("Mémoire de recherche ({folder}) — {n} note(s) :", folder=folder, n=len(hits))]
        for score, note in hits:
            body = note.get("body", "")
            if len(body) > 1200:
                body = body[:1200].rsplit(" ", 1)[0] + " …"
            out.append(f"\n### {note.get('sujet', note['file'])}\n_"
                       + T("{date} · certitude : {cert} · sources : {src} · fichier {file}",
                           date=note.get('date', '?'), cert=note.get('certitude', '?'),
                           src=note.get('sources') or T("non notées"), file=note['file'])
                       + f"_\n\n{body}")
        out.append("\n_" + T("Une note « probable » ou ancienne se recoupe avant d'être affirmée ; une note "
                             "contredite par le jeu se corrige avec save_knowledge.") + "_")
        return "\n".join(out)

    def save_knowledge(self, args: Dict[str, Any]) -> str:
        try:
            path = K.save(self.store.data_dir, args.get("sujet") or "", args.get("contenu") or "",
                          sources=as_list(args.get("sources")), certainty=args.get("certitude") or "probable",
                          keywords=as_list(args.get("mots_cles")) or None,
                          game_version=args.get("version_jeu"))
        except ValueError as exc:
            raise ToolError(str(exc))
        return T("Enregistré dans la mémoire de recherche : {path}", path=path)

    def get_professions(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        lines = F.render_professions(db, with_recipes=True)
        skills = as_list(F.g(db, "professions", "skills"))
        weapon_ids = set(G.WEAPON_SKILL_IDS.values())
        weap = [s for s in skills if s.get("skillId") in weapon_ids or "arme" in F.norm_key(s.get("category"))
                or "weapon" in F.norm_key(s.get("category"))]
        if weap:
            lines.append(T("\nCompétences d'armes : {list}",
                           list=", ".join(f"{s.get('name')} {s.get('rank')}/{s.get('max')}" for s in weap)))
        return self._head(db, "_" + T("Métiers capturés {age}.", age=F.domain_age(db, 'professions')) + "_", *lines)

    def get_inventory(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        return self._head(db, "_" + T("Sacs capturés {age}.", age=F.domain_age(db, 'bags')) + "_",
                          *F.render_inventory(db, include_bank=args.get("banque", True)))

    def get_reputations(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        cur = as_list(F.g(db, "currencies", "list"))
        extra = []
        if cur:
            extra.append(T("\nMonnaies : {list}", list=", ".join(
                f"{c.get('name')} {F.num(c.get('quantity'))}" + (f"/{F.num(c['max'])}" if c.get("max") else "")
                for c in cur)))
        return self._head(db, "_" + T("Réputations capturées {age}.", age=F.domain_age(db, 'reputations')) + "_",
                          *F.render_reputations(db), *extra)

    def get_pet(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        if F.g(db, "identity", "classFile") != "HUNTER" and not F.g(db, "pet", "hasPetUI"):
            return self._head(db, T("Ce perso n'a pas de familier de chasseur."))
        return self._head(db, "_" + T("Familier capturé {age}.", age=F.domain_age(db, 'pet')) + "_", *F.render_pet(db))

    # -- progression ----------------------------------------------------------------
    def get_progress(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        folder = self.store.folder(char)
        since_raw = (args.get("depuis") or "").strip().lower()
        today = datetime.now().date()
        if since_raw in ("", "semaine", "week", "last week", "this week"):
            since = today - timedelta(days=7)
        elif since_raw in ("aujourd'hui", "aujourdhui", "today"):
            since = today
        elif since_raw in ("hier", "yesterday"):
            since = today - timedelta(days=1)
        else:
            try:
                since = datetime.strptime(since_raw[:10], "%Y-%m-%d").date()
            except ValueError:
                raise ToolError(T("Format de date attendu : AAAA-MM-JJ, « hier », « aujourd'hui » ou « semaine »."))
        snaps = sorted((folder / "historique").glob("*.json"))
        base = None
        before = [s for s in snaps if s.stem < since.isoformat()]
        if before:
            base = load_json(before[-1], {}).get("data")
            base_label = T("fin de journée du {date}", date=before[-1].stem)
        elif snaps:
            base = load_json(snaps[0], {}).get("data")
            base_label = T("première capture ({date})", date=snaps[0].stem)
        lines = []
        if base is None or base is db:
            lines.append(T("Pas encore d'historique : il se construit à chaque synchro (un instantané par jour)."))
        else:
            events = diff_states(base, db)
            lp, ln = F.g(base, "progression", "level"), F.g(db, "progression", "level")
            tp0, tp1 = F.g(base, "progression", "timePlayed", "total"), F.g(db, "progression", "timePlayed", "total")
            lines.append(T("Depuis la {label} :", label=base_label))
            played = T("temps de jeu +{d}", d=F.duration(tp1 - tp0)) if tp0 and tp1 and tp1 > tp0 else ""
            if lp and ln and ln != lp:
                lines.append(T("- Niveau {a} → {b}", a=lp, b=ln) + (f" · {played}" if played else ""))
            elif played:
                lines.append(f"- {played[:1].upper()}{played[1:]}")
            m0, m1 = F.g(base, "money", "copper"), F.g(db, "money", "copper")
            if isinstance(m0, int) and isinstance(m1, int) and m0 != m1:
                lines.append(T("- Argent : {a} → {b}", a=F.money(m0), b=F.money(m1)))
            lines += [f"- {e}" for e in events]
            if len(lines) == 1:
                lines.append(T("- Aucun changement notable."))
        if args.get("niveau_cible"):
            lines[:0] = self._xp_target_lines(db, args["niveau_cible"]) + [""]
        journal = folder / "journal.md"
        if journal.exists():
            recent = [ln for ln in journal.read_text(encoding="utf-8").splitlines()
                      if ln.startswith("- ") and ln[2:12] >= since.isoformat()]
            if recent:
                lines.append(T("\nJournal sur la période :"))
                lines += recent[:40]
        return self._head(db, *lines)

    def _xp_target_lines(self, db: Dict[str, Any], target: Any) -> List[str]:
        import xptable as X
        try:
            target = int(target)
        except (TypeError, ValueError):
            raise ToolError(T("niveau_cible attend un nombre (ex. 40)."))
        level = int(F.g(db, "progression", "level") or 0)
        xp, xp_max = F.g(db, "progression", "xp") or 0, F.g(db, "progression", "xpMax")
        table = X.table_from_db(self.gamedb(required=False))
        badge = T("[Forever · base locale] table LevelExperience du client") if table else \
            T("[Classic · probable] table de Classic Era, base locale sans table d'XP (reconstruis-la)")
        table = table or X.CLASSIC_TABLE
        if target <= level:
            return [T("**XP jusqu'au niveau {t}** : déjà atteint (niveau {l}).", t=target, l=level)]
        total, reached = X.xp_to_target(level, xp, xp_max, target, table)
        if total is None:
            return [T("**XP jusqu'au niveau {t}** : table connue seulement jusqu'au niveau {r} {badge}.",
                      t=target, r=reached, badge=badge)]
        cur_left = (xp_max or table.get(level, 0)) - xp
        out = [T("**XP jusqu'au niveau {t}** : {n} XP {badge}.", t=target, n=F.num(total), badge=badge)]
        if target - 1 > level:
            out.append(T("- Détail : {left} pour finir le niveau {l}, puis {rest} pour les niveaux {a} à {b}.",
                         left=F.num(cur_left), l=level, rest=F.num(total - cur_left), a=level + 1, b=target - 1))
        if xp_max and table.get(level) and xp_max != table[level]:
            out.append(T("- Attention : ton jeu demande {a} XP pour ce niveau, la table {b} : écart à signaler.",
                          a=F.num(xp_max), b=F.num(table[level])))
        rest = F.g(db, "progression", "xpRested")
        if isinstance(rest, (int, float)) and rest > 0:
            out.append(T("- XP reposée en réserve : {n} (double l'XP des monstres jusqu'à épuisement).", n=F.num(rest)))
        return out

    # -- comparaisons ----------------------------------------------------------------
    def compare_item(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        cls = F.g(db, "identity", "classFile") or ""
        eq = F.g(db, "equipment", "slots", default={}) or {}
        cand: Dict[str, Any] = {}
        name = args.get("nom") or T("objet proposé")
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
                gdb = self.gamedb(required=False)
                row = gdb.item(iid) if gdb else None
                if row:
                    cand = GDB.to_addon_item(row)
                    name = row["name"]
                    if row["req_level"]:
                        args.setdefault("niveau_requis", row["req_level"])
                    if not args.get("emplacement"):
                        slots = G.target_slots(cls, F.g(db, "progression", "level") or 0, cand)
                        if slots:
                            args["emplacement"] = G.weakest_slot(db, slots, cand)
                elif not any(args.get(k) is not None for k in ("dps", "agilite", "force", "endurance", "intelligence",
                                                                 "esprit", "pa", "pa_distance", "armure")):
                    raise ToolError(T("Je connais « {name} » ({where}) mais pas ses stats : l'addon ne lit les stats "
                                      "que des objets équipés et la base locale du jeu n'est pas construite. "
                                      "Donne-moi ses stats (DPS, agilité, PA…) en paramètres, ou construis la "
                                      "base : {cmd}", name=name,
                                      where=T("dans tes sacs") if where else T("objet inconnu"),
                                      cmd=GDB.build_command()))
        stats = {
            "AGILITY": args.get("agilite"), "STRENGTH": args.get("force"), "STAMINA": args.get("endurance"),
            "INTELLECT": args.get("intelligence"), "SPIRIT": args.get("esprit"), "ATTACK_POWER": args.get("pa"),
            "RANGED_ATTACK_POWER": args.get("pa_distance"), "ARMOR": args.get("armure"),
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
                raise ToolError(T("Emplacement « {slot} » inconnu. Exemples : distance, main droite, tête, doigt 2 "
                                  "(ou ranged, main hand, head, finger 2).", slot=raw_slot))
        elif dps is not None:
            slot = "RangedSlot" if cls == "HUNTER" else "MainHandSlot"
        else:
            raise ToolError(T("Indique l'emplacement (ex. « distance », « mains », « doigt 1 »)."))
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
        pc = F.pct_sign()

        rows = [T("| | Équipé : {name} | {cand} |", name=cur.get("name") or T("rien"), cand=name), "|---|---|---|"]
        if ranged_slot or melee_slot:
            rows.append(T("| DPS de l'arme | {a} | {b} |", a=F.num(odps, 1) if odps else '—',
                          b=F.num(dps, 1) if dps is not None else '?'))
        keys = sorted(set(cstats) | set(ostats), key=F.stat_sort_key)
        for k in keys:
            rows.append(f"| {F.stat_name(k)} | {F.num(ostats.get(k, 0), 1)} | {F.num(cstats.get(k, 0), 1)} |")
        main_is_ranged = cls == "HUNTER" or ranged_slot
        if r_now is not None and (main_is_ranged or abs(d_rdps) > 0.05):
            rows.append(T("| **DPS à distance (coups blancs)** | {now} | **≈ {new}** ({sign}{delta}) |",
                          now=F.num(r_now, 1), new=F.num(r_now + d_rdps, 1), sign='+' if d_rdps >= 0 else '',
                          delta=F.num(d_rdps, 1)))
        if m_now is not None and (not main_is_ranged or melee_slot or abs(d_mdps) > 0.05):
            rows.append(T("| DPS en mêlée (coups blancs) | {now} | ≈ {new} ({sign}{delta}) |",
                          now=F.num(m_now, 1), new=F.num(m_now + d_mdps, 1), sign='+' if d_mdps >= 0 else '',
                          delta=F.num(d_mdps, 1)))
        key_delta = d_rdps if main_is_ranged else d_mdps
        base_dps = (r_now if main_is_ranged else m_now) or 0
        pct_txt = f" ({'+' if key_delta >= 0 else ''}{F.num(100 * key_delta / base_dps, 1)}{pc})" if base_dps else ""
        plevel = F.g(db, "progression", "level") or 0
        req = int(args.get("niveau_requis") or cand.get("requiredLevel") or 0)
        wst = weapon_skill_state(db, args.get("type_arme") or name or "", slot, cand)
        low_skill = wst if (wst and wst[0] and wst[2] and wst[1] < 0.5 * wst[2]) else None
        if key_delta > 0.3 and req > plevel:
            verdict = T("**Pas encore : niveau {n} requis, ensuite environ {sign}{delta} DPS{pct}.**", n=req,
                        sign='+', delta=F.num(key_delta, 1), pct=pct_txt)
            if low_skill:
                verdict = verdict[:-3] + T(" (et compétence {name} à {rank}/{max})", name=low_skill[0],
                                           rank=low_skill[1], max=low_skill[2]) + ".**"
        elif key_delta > 0.3 and low_skill:
            verdict = T("**À prendre, mais compétence {name} à {rank}/{max} : environ +{delta} DPS{pct} une fois "
                        "montée, beaucoup de coups ratés d'ici là.**", name=low_skill[0], rank=low_skill[1],
                        max=low_skill[2], delta=F.num(key_delta, 1), pct=pct_txt)
        elif key_delta > 0.3:
            verdict = T("**À prendre : environ {sign}{delta} DPS{pct}.**", sign='+' if key_delta >= 0 else '',
                        delta=F.num(key_delta, 1), pct=pct_txt)
        elif key_delta < -0.3:
            verdict = T("**À ne pas équiper : environ {delta} DPS{pct}.**", delta=F.num(key_delta, 1), pct=pct_txt)
        else:
            verdict = self._tie_verdict(db, cls, delta, cstats, dps)
        conv = T("1 Agi = 2 PA à distance et 1 PA en mêlée, 1 For = 1 PA en mêlée (cohérent avec la fiche du perso)") \
            if cls == "HUNTER" else T("conversions For/Agi → PA reprises de Classic, à vérifier dans Forever")
        notes = [
            T("Hypothèses : 14 PA = 1 DPS (confirmé dans Forever) ; {conv}.", conv=conv),
            T("Non chiffré : le crit apporté par l'Agilité, les effets spéciaux (« Chance quand vous touchez… »)."),
        ]
        if delta("STAMINA"):
            notes.append(T("Endurance : {sign}{n} (≈ {hp} PV, hypothèse Classic).",
                           sign='+' if delta('STAMINA') > 0 else '', n=F.num(delta('STAMINA')),
                           hp=F.num(delta('STAMINA') * 10)))
        wskill = weapon_skill_note(db, args.get("type_arme") or name or "", slot, cand)
        if wskill:
            notes.insert(0, wskill)
        if req > plevel:
            notes.append(T("Niveau requis {n} : pas encore équipable.", n=req))
        if slot in G.TWIN_SLOTS:
            notes.append(T("Comparé à {slot}, le plus faible des deux emplacements.", slot=F.slot_label(slot)))
        return self._head(db, verdict, "", *rows, "", *[f"- {n}" for n in notes])

    @staticmethod
    def _tie_verdict(db: Dict[str, Any], cls: str, delta: Any, cstats: Dict[str, float], dps: Any) -> str:
        """Verdict quand l'écart de DPS est nul : départage seulement sur une stat que l'un des deux objets a."""
        useless = [] if dps else G.off_role(db, cstats)
        if useless:
            return T("**Rien pour toi en dégâts : {stats} sans effet pour ta classe ; garde l'objet équipé.**",
                     stats=", ".join(F.stat_name(k) for k in useless))
        ties = []
        if delta("STAMINA"):
            ties.append(("STAMINA", delta("STAMINA")))
        if delta("ARMOR"):
            ties.append(("ARMOR", delta("ARMOR") / 10.0))
        ca = G.careful_aim(db) if cls == "HUNTER" else 0
        if ca and delta("INTELLECT"):
            ties.append(("INTELLECT", delta("INTELLECT")))
        if not ties:
            return T("**Équivalent : aucune différence chiffrable entre les deux ; garde l'objet équipé.**")
        k, v = max(ties, key=lambda t: abs(t[1]))
        raw = delta(k)
        what = f"{'+' if raw > 0 else ''}{F.num(raw)} {F.stat_name(k)}"
        if k == "INTELLECT":
            what += T(" (Visée minutieuse {r}/5, effet non chiffré [Forever · probable])", r=ca)
        return (T("**Équivalent en dégâts, léger avantage au nouvel objet : {what}.**", what=what) if v > 0 else
                T("**Équivalent en dégâts, léger avantage à l'objet équipé : {what} pour le nouveau.**", what=what))

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
            raise ToolError(T("Aucun perso capturé."))
        rows = [T("| Perso | Joueur | Classe | Niveau | Zone | ilvl | Argent | Métiers | Capturé |"),
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
                f"{F.g(db, 'position', 'zone', default='?')} | {F.num(F.g(db, 'stats', 'itemLevel', 'equipped'), 1)} | "
                f"{F.money(F.g(db, 'money', 'copper'))} | {prof_txt} | {F.age(F.captured_at(db))} |")
        lines = rows
        if prof_index:
            lines.append(T("\nQui fait quoi :"))
            for prof, who in sorted(prof_index.items()):
                lines.append(f"- {prof}{F.sep()}{', '.join(who)}")
        return "\n".join(lines)


# Noms des compétences d'armes (repli quand la capture n'a pas l'ID de compétence), français et anglais
WEAPON_SKILL_NAMES = {
    44: ("haches", "haches a une main", "axes", "one handed axes"),
    172: ("haches a deux mains", "two handed axes"), 45: ("arcs", "bows"), 46: ("armes a feu", "guns"),
    54: ("masses", "masses a une main", "maces", "one handed maces"),
    160: ("masses a deux mains", "two handed maces"), 229: ("armes d hast", "polearms"),
    43: ("epees", "epees a une main", "swords", "one handed swords"),
    55: ("epees a deux mains", "two handed swords"), 136: ("batons", "staves"),
    473: ("armes de pugilat", "fist weapons"), 173: ("dagues", "daggers"), 176: ("armes de jet", "thrown"),
    226: ("arbaletes", "crossbows"), 228: ("baguettes", "wands"),
}


def weapon_skill_state(db: Dict[str, Any], text: str, slot: str,
                       item: Optional[Dict[str, Any]] = None) -> Optional[Tuple[Any, int, int]]:
    """(nom, rang, max) de la compétence d'arme du type proposé ; (None, 0, 0) si introuvable ; None si sans objet.

    Le type vient de l'objet (classId 2 + subclassId) ou du texte (« arbalète », « crossbow »…) ;
    la compétence est retrouvée par son ID (SkillLine), sinon par son nom dans l'une des deux langues.
    """
    if slot not in ("RangedSlot", "MainHandSlot", "SecondaryHandSlot"):
        return None
    subs: Tuple[int, ...] = ()
    if item and item.get("classId") == 2 and item.get("subclassId") is not None:
        subs = (int(item["subclassId"]),)
    else:
        parsed = G.parse_type(text)
        if parsed and parsed[0] == 2:
            subs = parsed[1]
    skill_ids = {G.WEAPON_SKILL_IDS[s] for s in subs if s in G.WEAPON_SKILL_IDS}
    if not skill_ids:
        return None
    names = {n for sid in skill_ids for n in WEAPON_SKILL_NAMES.get(sid, ())}
    for s in as_list(F.g(db, "professions", "skills")):
        if s.get("skillId") in skill_ids or F.norm_key(s.get("name")) in names:
            return s.get("name"), int(s.get("rank") or 0), int(s.get("max") or 0)
    return (None, 0, 0)


def weapon_skill_note(db: Dict[str, Any], text: str, slot: str,
                      item: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Avertit si la compétence d'arme correspondant au type proposé est basse."""
    st = weapon_skill_state(db, text, slot, item)
    if st is None:
        return None
    name, rank, mx = st
    if name is None:
        return T("Compétence d'arme pour « {text} » introuvable dans la capture : vérifie en jeu que tu sais "
                 "l'utiliser (maître d'armes).", text=text)
    if mx and rank < 0.8 * mx:
        return T("**Attention, compétence {name} : {rank}/{max}.** Avec une compétence basse, beaucoup de "
                 "tirs ou de coups ratent au début : le gain réel n'arrive qu'après l'avoir montée en "
                 "l'utilisant [Classic · probable dans Forever, la compétence existe en jeu].",
                 name=name, rank=rank, max=mx)
    return None


reward_pick = G.reward_pick
quest_where = G.quest_where


def reward_summary(db: Dict[str, Any], q: Dict[str, Any]) -> Optional[str]:
    r = q.get("rewards")
    if not isinstance(r, dict):
        return None
    best, evals = G.best_choice(db, r)
    bits = []
    if best:
        bits.append(T("à prendre : {pick}", pick=reward_pick(best)))
    elif evals:
        names = ", ".join(e["item"].get("name") or "?" for e in evals[:4])
        bits.append(T("objets : {names} (rien de mieux pour toi)", names=names))
    if r.get("money"):
        bits.append(F.money(r["money"]))
    if r.get("xp"):
        bits.append(f"{F.num(r['xp'])} XP")
    return T("Récompense : {list}", list=" · ".join(bits)) if bits else None


class ToolError(Exception):
    pass


Tools.ToolError = ToolError  # utilisé par GameDBToolsMixin


def schema(props: Dict[str, Any], required: Optional[List[str]] = None) -> Dict[str, Any]:
    s: Dict[str, Any] = {"type": "object", "properties": {**props, "lang": LANG}, "additionalProperties": False}
    if required:
        s["required"] = required
    return s


SLOT = {"type": "string", "description": "slot, FR or EN: tête/head, distance/ranged, main droite/main hand, "
                                         "doigt 1/finger 1, bijou/trinket…"}

TOOL_DEFS: List[Dict[str, Any]] = [
    {"name": "overview",
     "description": "START HERE. Verdict + digest precomputed at sync: turn-ins by zone with best reward, top "
                    "upgrades with source, quests nearby, next step, bags, ammo, pet, professions. "
                    "vue=fiche|stats|progres: full sheet, stats, progress since `depuis`.",
     "inputSchema": schema({"perso": PERSO, "detail": DETAIL,
                            "vue": {"type": "string", "description": "resume (default) | fiche | stats | progres"},
                            "depuis": {"type": "string", "description": "progress since: YYYY-MM-DD, hier, semaine"},
                            "niveau_cible": {"type": "integer", "description": "progres: XP left to reach this level"}})},
    {"name": "gear",
     "description": "Worn gear + upgrades ranked by DPS gain (quest rewards, bags, local DB with source). "
                    "`emplacement` = one slot. `objet` and/or `stats` = compare an item with the worn one.",
     "inputSchema": schema({"perso": PERSO, "emplacement": SLOT, "detail": DETAIL,
                            "objet": {"type": ["string", "integer"], "description": "item name or itemId to compare"},
                            "stats": {"type": "object", "description": "dps, agilite, endurance, pa, armure, type_arme…"},
                            "niveau_max": {"type": "integer", "description": "max required level"},
                            "qualite_min": {"type": "string", "description": "vert/green, bleu/blue…"}})},
    {"name": "quests",
     "description": "Quest log (turn-ins first, best reward, /way). `quete`/`questId` = one quest: giver, "
                    "objectives with /way, chain. `disponibles` = quests to pick up in a zone. `a_rendre` = "
                    "turn-ins with rewards rated.",
     "inputSchema": schema({"perso": PERSO, "detail": DETAIL,
                            "quete": {"type": "string", "description": "quest title (game language or English)"},
                            "questId": {"type": "integer"},
                            "zone": {"type": "string", "description": "zone filter (default for disponibles: current)"},
                            "disponibles": {"type": "boolean"}, "a_rendre": {"type": "boolean"}})},
    {"name": "npc",
     "description": "Where an NPC, mob or object is (/way), level, quests.",
     "inputSchema": schema({"nom": {"type": "string"}, "npcId": {"type": "integer"}, "perso": PERSO})},
    {"name": "item",
     "description": "Item sheet (stats, sources, verdict) by `itemId`/`nom`; with filters = item search.",
     "inputSchema": schema({"itemId": {"type": "integer"}, "nom": {"type": "string"}, "perso": PERSO,
                            "emplacement": SLOT, "type": {"type": "string", "description": "cuir/leather, arc/bow…"},
                            "niveau_min": {"type": "integer"}, "niveau_max": {"type": "integer"},
                            "qualite_min": {"type": "string"}, "stat": {"type": "string"},
                            "forever_seulement": {"type": "boolean"}, "limite": {"type": "integer"}})},
    {"name": "professions",
     "description": "Skill levels, next tier (skill/level required, met or not), nearest trainers (/way), "
                    "cheapest level-up path (colors, crafts, reagents, vendor prices). Works for unlearned ones.",
     "inputSchema": schema({"perso": PERSO, "metier": {"type": "string", "description": "FR or EN name"},
                            "cible": {"type": "integer", "description": "target skill of the path (default: end "
                                                                         "of current tier)"},
                            "rang_min": {"type": "integer", "description": "with rang_max: raw recipe list"},
                            "rang_max": {"type": "integer"}})},
    {"name": "pet",
     "description": "Pet happiness, loyalty, XP, training points, abilities, diet and matching food in bags.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "talents",
     "description": "Spec, talent points, chosen talents. `arbre` = full class tree: rank/max per row, "
                    "available now or locked. `sorts` adds the spellbook (`ligne` = one line).",
     "inputSchema": schema({"perso": PERSO, "arbre": {"type": ["boolean", "string"],
                                                      "description": "true | complet (all branches)"},
                            "sorts": {"type": "boolean"}, "ligne": {"type": "string"}})},
    {"name": "dungeon",
     "description": "Dungeon or raid: loot per boss with stats and verdict for the character (judged at its "
                    "required level), boss mechanics, quests (log, to pick up, giver /way), quest level range. "
                    "One call is enough: don't look items up one by one. No name = list of dungeons.",
     "inputSchema": schema({"donjon": {"type": "string"}, "perso": PERSO})},
    {"name": "bags",
     "description": "Money, bag space, ammo, bags and bank content, gear in bags worth equipping, grey items.",
     "inputSchema": schema({"perso": PERSO, "banque": {"type": "boolean"}})},
    {"name": "reputations",
     "description": "Reputation per faction and currencies.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "search",
     "description": "Any name, FR or EN (English names matched by id, Forever dungeon loot included), accents "
                    "optional: items, quests, NPCs, zones, dungeons, recipes, research notes, your log and bags. A "
                    "clear hit returns its sheet. Use BEFORE any web search.",
     "inputSchema": schema({"texte": {"type": "string"}, "type": {"type": "string", "description":
                                                               "item, quete, pnj, zone, donjon, recette, note"},
                            "limite": {"type": "integer"}, "perso": PERSO}, ["texte"])},
    {"name": "save_knowledge",
     "description": "Save a web or in-game finding with sources and certainty (one short note per topic).",
     "inputSchema": schema({"sujet": {"type": "string"}, "contenu": {"type": "string", "description": "Markdown"},
                            "sources": {"type": "array", "items": {"type": "string"}},
                            "certitude": {"type": "string", "description": "sûr/sure, probable, à vérifier/to check"},
                            "mots_cles": {"type": "array", "items": {"type": "string"}},
                            "version_jeu": {"type": "string"}}, ["sujet", "contenu", "certitude"])},
    {"name": "map",
     "description": "PNG map of a zone with numbered markers (and you, in blue). Use when giving a /way the "
                    "player must find.",
     "inputSchema": schema({"points": {"type": "array", "description": "\"/way 38.1 50.2 Whelgar\" or {x, y, label}",
                                       "items": {"type": ["string", "object"]}},
                            "zone": {"type": ["string", "integer"], "description": "name or uiMapID of the /way (required with points)"},
                            "cadre": {"type": "string", "description": "auto (zoom on markers) | zone"},
                            "perso": PERSO})},
    {"name": "characters",
     "description": "List characters; action=activer|comparer|rattacher (account + user).",
     "inputSchema": schema({"action": {"type": "string"}, "perso": PERSO,
                            "persos": {"type": "array", "items": {"type": "string"}},
                            "account": {"type": "string"}, "user": {"type": "string"}})},
]

# Outils de la v0.7 : toujours appelables (compatibilité des skills et habitudes), mais plus listés.
LEGACY_TOOLS = {
    "list_characters", "set_active_character", "register_account", "get_character", "get_stats", "get_equipment",
    "get_talents", "get_spells", "get_quests", "get_professions", "get_inventory", "get_reputations", "get_pet",
    "get_progress", "compare_item", "get_overview", "get_quest_rewards", "search_knowledge", "find_upgrades",
    "find_items", "get_item", "get_dungeon_loot", "find_recipes", "get_quest_info", "find_quests", "find_npc",
    "compare_characters",
}
CALLABLE = {t["name"] for t in TOOL_DEFS} | LEGACY_TOOLS


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
                self.log(f"sync: {', '.join(rep['updated'])}")
                try:  # résumé précalculé (overview) des persos mis à jour
                    self.tools.refresh_digests(rep["updated"])
                except Exception as exc:
                    self.log(f"digest failed: {exc}")
            for e in rep.get("errors", []):
                self.log(f"sync: {e}")
        except Exception as exc:  # la synchro ne doit jamais casser un outil
            self.log(f"sync failed: {exc}")
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
                    "serverInfo": {"name": SERVER_NAME, "title": "WoW Forever: character state",
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
                args = dict(params.get("arguments") or {})
                fn: Optional[Callable[[Dict[str, Any]], str]] = (
                    getattr(self.tools, f"tool_{name}", None) or getattr(self.tools, name, None)) \
                    if name in CALLABLE else None
                if not fn:
                    return self.error(mid, -32602, f"Unknown tool: {name}")
                self.ensure_sync()
                lang = self.tools.prepare(args)
                with I.using(lang):
                    try:
                        out = fn(args)
                        if isinstance(out, dict):  # texte + image (outil map)
                            content = [{"type": "text", "text": out["text"]}]
                            if out.get("image"):
                                content.append({"type": "image", "mimeType": "image/png",
                                                "data": base64.b64encode(out["image"]).decode("ascii")})
                            result = {"content": content, "isError": False}
                        else:
                            result = {"content": [{"type": "text", "text": out}], "isError": False}
                    except ToolError as exc:
                        result = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
                    except Exception as exc:
                        self.log(traceback.format_exc())
                        result = {"content": [{"type": "text", "text": T("Erreur interne de {tool} : {err}",
                                                                         tool=name, err=exc)}], "isError": True}
            elif method in ("resources/list", "prompts/list"):
                result = {method.split("/")[0]: []}
            else:
                return self.error(mid, -32601, f"Method not found: {method}")
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
        self.log(f"started · data: {self.store.data_dir}")
        for raw in stdin:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                out.write(json.dumps(self.error(None, -32700, "Parse error: invalid JSON")) + "\n")
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
        # UTF-8 et « \n » quel que soit l'OS : le transport MCP stdio découpe sur \n
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # journaux lisibles par le client
    except AttributeError:
        pass
    Server().serve()


if __name__ == "__main__":
    main()
