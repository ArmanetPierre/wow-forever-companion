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
from questdb_tools import QuestDBToolsMixin  # noqa: E402
from i18n import T  # noqa: E402
import knowledge as K  # noqa: E402
from luasv import as_list  # noqa: E402
from sync import Store, diff_states, load_json  # noqa: E402

SERVER_NAME = "forever-mcp"
SERVER_VERSION = "0.7.0"
SUPPORTED_PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
AP_PER_DPS = 14.0  # confirmé par l'infobulle de Forever (17/11/2026)

INSTRUCTIONS = (
    "Real state of the player's WoW Forever characters, captured in game by the ForeverScribe addon. "
    "Call these tools BEFORE answering any question that depends on the character (level, zone, gear, "
    "quests, professions, talents, pet). Without `perso`, a tool targets the active character (the most "
    "recently captured one). Always quote the freshness shown in the header; if it is older than one hour, "
    "offer the player to sync in game (Ctrl+Shift+S, /sync or the ForeverScribe button). "
    "For a general question, start with get_overview (a single call). Before any web search, check "
    "search_knowledge; after a useful finding, store it with save_knowledge. "
    "For game data (items, stats, upgrades, recipes, dungeons, quests), query the local game database first "
    "(find_upgrades, find_items, get_item, find_recipes, get_dungeon_loot): it comes from the "
    "Forever client files and its hotfixes, badge [Forever · local DB] / [Forever · base locale]. "
    "For quests and NPCs (giver, turn-in, objectives and where, /way, chain, prerequisites, quests available "
    "here, where is an NPC), use get_quest_info, find_quests and find_npc before any web search: QuestieDB data "
    "merged into the local DB, badge [Forever · QuestieDB]. "
    "Language: pass `lang` = \"en\" or \"fr\" (the language of the player's question) to every tool; labels, "
    "headings and advice follow it. Names coming from the game (items, quests, zones, spells) stay in the "
    "game client's language — quote them as they are. Search parameters accept French and English values "
    "(e.g. slot \"head\"/\"tête\", type \"crossbow\"/\"arbalète\", quality \"blue\"/\"bleu\")."
)

PERSO = {"type": "string", "description": "Target character: name (Brannok), Name-Region, User/Name or GUID. "
                                          "Optional: defaults to the active character."}
LANG = {"type": "string", "enum": ["en", "fr"],
        "description": "Output language (labels, headings, advice): the language of the player's question. "
                       "Default: answer_language in config.json, else the game client language. "
                       "Game names stay in the client's language."}


# ----------------------------------------------------------------------------
# Outils
# ----------------------------------------------------------------------------

class Tools(QuestDBToolsMixin, GameDBToolsMixin):
    def __init__(self, store: Store):
        self.store = store
        self._locale: Optional[str] = None
        self._pre: Optional[Tuple[str, Dict[str, Any]]] = None

    # -- langue ------------------------------------------------------------------
    def prepare(self, args: Dict[str, Any]) -> str:
        """Retire `lang` des arguments, repère la langue du client du perso visé ; renvoie la langue de sortie."""
        explicit = I.norm_lang(args.pop("lang", None))
        self._locale, self._pre = None, None
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
        lines.append(T("\nCompte {account} ({user}) · capture du {time}", account=char.get('account'),
                       user=char.get('user'), time=F.local_time(F.captured_at(db)))
                     + (T(" · origine : {reason}", reason=reason) if reason else "")
                     + T(" · langue du jeu : {locale}", locale=F.game_locale(db) or "?"))
        return self._head(db, *lines)

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
                                           reward_line=lambda q: reward_summary(db, q)))

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
                lines.append(f"- **{q.get('title')}** → {reward_pick(best)}" + quest_where(q))
        if ups_open:
            lines.append(T("\n**En cours, avec une amélioration à la clé :**"))
            for q, r, best, _ in sorted(ups_open, key=lambda x: -x[2]["score"]):
                lines.append(f"- **{q.get('title')}** (" + T("niv. {n}", n=q.get('level')) + f") → {reward_pick(best)}"
                             + quest_where(q))
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
        return self._head(db, *lines)

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
        journal = folder / "journal.md"
        if journal.exists():
            recent = [ln for ln in journal.read_text(encoding="utf-8").splitlines()
                      if ln.startswith("- ") and ln[2:12] >= since.isoformat()]
            if recent:
                lines.append(T("\nJournal sur la période :"))
                lines += recent[:40]
        return self._head(db, *lines)

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
                            args["emplacement"] = slots[0]
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
        if key_delta > 0.3:
            verdict = T("**À prendre : environ {sign}{delta} DPS{pct}.**", sign='+' if key_delta >= 0 else '',
                        delta=F.num(key_delta, 1), pct=pct_txt)
        elif key_delta < -0.3:
            verdict = T("**À ne pas équiper : environ {delta} DPS{pct}.**", delta=F.num(key_delta, 1), pct=pct_txt)
        else:
            verdict = T("**Quasi équivalent en dégâts** : départage avec l'endurance ou l'armure.")
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
        if args.get("niveau_requis") and int(args["niveau_requis"]) > (F.g(db, "progression", "level") or 0):
            notes.append(T("Niveau requis {n} : pas encore équipable.", n=args['niveau_requis']))
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


def weapon_skill_note(db: Dict[str, Any], text: str, slot: str,
                      item: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Avertit si la compétence d'arme correspondant au type proposé est basse.

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
            rank, mx = s.get("rank") or 0, s.get("max") or 0
            if mx and rank < 0.8 * mx:
                return T("**Attention, compétence {name} : {rank}/{max}.** Avec une compétence basse, beaucoup de "
                         "tirs ou de coups ratent au début : le gain réel n'arrive qu'après l'avoir montée en "
                         "l'utilisant [Classic · probable dans Forever, la compétence existe en jeu].",
                         name=s.get('name'), rank=rank, max=mx)
            return None
    return T("Compétence d'arme pour « {text} » introuvable dans la capture : vérifie en jeu que tu sais l'utiliser "
             "(maître d'armes).", text=text)


def reward_pick(ev: Optional[Dict[str, Any]]) -> str:
    if not ev:
        return ""
    it = ev["item"]
    gain = G.gain_text(ev)
    where = f"{ev.get('slot_label', ev.get('slot_fr', '?'))}" + (
        T(", remplace {name}", name=ev['replaces']) if ev.get("replaces") else T(", emplacement vide"))
    return (f"**{it.get('name')}** ({G.describe(it)}) — {ev['verdict']}"
            + (f", {gain}" if gain else "") + f" [{where}]" + (T(" (fixe)") if ev.get("fixed") else T(" (au choix)")))


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


SLOT_HELP = ("slot, French or English: head/tête, neck/cou, shoulders/épaules, back/dos, chest/torse, "
             "wrists/poignets, hands/mains, waist/taille, legs/jambes, feet/pieds, finger 1/doigt 1, "
             "trinket/bijou, main hand/main droite, off hand/main gauche, ranged/distance")

TOOL_DEFS: List[Dict[str, Any]] = [
    {"name": "list_characters", "title": "Known characters",
     "description": "Lists every character of every player (account) with level, zone, capture freshness and "
                    "the active character. Call it when you don't know which character is meant.",
     "inputSchema": schema({})},
    {"name": "set_active_character", "title": "Change active character",
     "description": "Changes the default target character (e.g. \"I'm playing my mage\"). Stays active until "
                    "another character is captured more recently.",
     "inputSchema": schema({"perso": PERSO}, ["perso"])},
    {"name": "register_account", "title": "Name an account",
     "description": "Links a WoW account (folder WTF/Account/<account>) to a first name, to separate players "
                    "who share the computer. Moves that account's character folders.",
     "inputSchema": schema({"account": {"type": "string", "description": "account folder, e.g. 123456789#1"},
                            "user": {"type": "string", "description": "player's first name, e.g. Alex"}},
                           ["account", "user"])},
    {"name": "get_character", "title": "Character sheet",
     "description": "Summary sheet: identity, level and XP, position with coordinates, key stats, weapons, "
                    "professions, pet, money, bags, quests, game language. First tool for any character question.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_stats", "title": "Detailed stats",
     "description": "Attributes, melee and ranged attack power, damage, speed, crit, dodge, armor, resistances.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_equipment", "title": "Equipment",
     "description": "Equipped items per slot: name, item level, stats, weapon DPS, durability, repair cost.",
     "inputSchema": schema({"perso": PERSO, "details": {"type": "boolean", "description": "adds tooltip text"}})},
    {"name": "get_talents", "title": "Talents",
     "description": "Spec, spent and free points, chosen talents with their rank.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_spells", "title": "Known spells",
     "description": "Spellbook by line (e.g. Beast Mastery, Marksmanship, Survival) with ranks, to know what to "
                    "learn at the class trainer.",
     "inputSchema": schema({"perso": PERSO, "ligne": {"type": "string",
                                                      "description": "filter on a spell line (game language)"}})},
    {"name": "get_quests", "title": "Quest log",
     "description": "Current quests grouped by zone: level, difficulty colour, objectives and progress, /way "
                    "coordinates, quests ready to turn in, number of completed quests.",
     "inputSchema": schema({"perso": PERSO,
                            "zone": {"type": "string", "description": "filter: zone or word of the title"},
                            "en_cours_seulement": {"type": "boolean",
                                                   "description": "hide quests ready to turn in (in progress only)"}})},
    {"name": "get_professions", "title": "Professions",
     "description": "Professions and skill levels, known recipes (if the profession window was opened) and those "
                    "that still give skill points, weapon skills.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_inventory", "title": "Bags and bank",
     "description": "Money, free slots, ammo, content of bags and bank (if it was opened).",
     "inputSchema": schema({"perso": PERSO, "banque": {"type": "boolean", "description": "include the bank (default: yes)"}})},
    {"name": "get_reputations", "title": "Reputations",
     "description": "Reputation per faction (standing and progress) and currencies.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_pet", "title": "Pet",
     "description": "Hunter pet: family, level, XP, happiness, loyalty, training points, food, abilities, "
                    "stabled pets.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_progress", "title": "Progress",
     "description": "What changed since a date (levels, quests turned in, items, professions, reputations, "
                    "talents), from the daily history and the automatic journal.",
     "inputSchema": schema({"perso": PERSO,
                            "depuis": {"type": "string",
                                       "description": "since: YYYY-MM-DD, \"yesterday\"/\"hier\", "
                                                      "\"today\"/\"aujourd'hui\" or \"week\"/\"semaine\" (default)"}})},
    {"name": "compare_item", "title": "Compare an item",
     "description": "Compares an item (stats given as parameters, or itemId of an equipped/bag item or of the "
                    "local game database) with the one worn in the same slot: stats table and estimated effective "
                    "DPS (14 AP = 1 DPS, confirmed in Forever).",
     "inputSchema": schema({
         "perso": PERSO,
         "emplacement": {"type": "string", "description": SLOT_HELP + " (default for a weapon: ranged for a hunter)"},
         "nom": {"type": "string", "description": "name of the offered item"},
         "itemId": {"type": "integer"},
         "dps": {"type": "number", "description": "weapon DPS"},
         "degats_min": {"type": "number", "description": "min damage"},
         "degats_max": {"type": "number", "description": "max damage"},
         "vitesse": {"type": "number", "description": "weapon speed in seconds"},
         "agilite": {"type": "number", "description": "agility"}, "force": {"type": "number", "description": "strength"},
         "endurance": {"type": "number", "description": "stamina"},
         "intelligence": {"type": "number", "description": "intellect"},
         "esprit": {"type": "number", "description": "spirit"},
         "pa": {"type": "number", "description": "attack power (melee and ranged)"},
         "pa_distance": {"type": "number", "description": "ranged attack power only"},
         "armure": {"type": "number", "description": "armor"},
         "niveau_requis": {"type": "integer", "description": "required level"},
         "type_arme": {"type": "string", "description": "weapon type, French or English: bow/arc, gun/fusil, "
                                                        "crossbow/arbalète, sword/épée, axe/hache, dagger/dague, "
                                                        "mace/masse, staff/bâton… (used to check the weapon skill)"},
     })},
    {"name": "get_overview", "title": "Overview",
     "description": "In one call: character sheet, weapons, empty slots, bags, quests to turn in with the best "
                    "reward for this character, upgrades to earn by finishing quests, freshness. Recommended first "
                    "call for \"rate my gear\", \"what should I do?\", or any general question.",
     "inputSchema": schema({"perso": PERSO})},
    {"name": "get_quest_rewards", "title": "Quest rewards",
     "description": "Rewards of the logged quests (choice and fixed items, money, XP, reputation), evaluated for "
                    "this character: weapon/armor proficiency, slot, estimated gain over the equipped item. "
                    "Highlights quests to turn in that give an upgrade.",
     "inputSchema": schema({"perso": PERSO,
                            "zone": {"type": "string", "description": "filter: zone or word of the title"},
                            "a_rendre": {"type": "boolean", "description": "only quests ready to turn in"}})},
    {"name": "search_knowledge", "title": "Search the research memory",
     "description": "Searches the findings already saved by the agent (the player's connaissances/ folder). "
                    "Call it BEFORE any web search: the same question must never be researched twice.",
     "inputSchema": schema({"question": {"type": "string", "description": "question or keywords"},
                            "limite": {"type": "integer", "description": "number of notes (default 5)"}},
                           ["question"])},
    {"name": "save_knowledge", "title": "Save a finding",
     "description": "Saves a useful finding (after a web search or an in-game check) in the player's research "
                    "memory, with sources and certainty, so it is not researched again. One note per topic; "
                    "short and factual.",
     "inputSchema": schema({"sujet": {"type": "string", "description": "short title, e.g. \"Leather helms level 20-30 (Alliance)\""},
                            "contenu": {"type": "string", "description": "the finding in Markdown (named items, levels, loot sources, /way)"},
                            "sources": {"type": "array", "items": {"type": "string"}, "description": "URL or \"seen in game\""},
                            "certitude": {"type": "string", "description": "certainty: \"sure\"/\"sûr\", \"probable\" or \"to check\"/\"à vérifier\" (+ detail, e.g. \"probable [Classic]\")"},
                            "mots_cles": {"type": "array", "items": {"type": "string"}, "description": "keywords"},
                            "version_jeu": {"type": "string", "description": "game version, e.g. 1.60.1"}},
                           ["sujet", "contenu", "certitude"])},
    {"name": "find_upgrades", "title": "Gear upgrades (local DB)",
     "description": "Searches the local game database for items the character can wear (class, level, "
                    "proficiencies) that improve each slot, ranked by estimated gain, with their source when known. "
                    "Call it for \"rate my gear\", \"what to upgrade\", \"a helm at my level?\".",
     "inputSchema": schema({"perso": PERSO,
                            "emplacement": {"type": "string", "description": SLOT_HELP + " (default: all)"},
                            "marge_niveau": {"type": "integer", "description": "levels above the character (default 0)"},
                            "niveau_max": {"type": "integer", "description": "maximum required level (overrides the margin)"},
                            "ecart": {"type": "integer", "description": "levels below the maximum to include (default 12)"},
                            "qualite_min": {"type": "string", "description": "minimum quality: green/vert (default), blue/bleu, purple/violet… or 0-4"},
                            "par_emplacement": {"type": "integer", "description": "items per slot (default 3)"}})},
    {"name": "find_items", "title": "Search items (local DB)",
     "description": "Item search in the local game database (client files + Forever hotfixes) by name (game "
                    "language), slot, type, required level, quality or stat. Stats, armor and DPS computed.",
     "inputSchema": schema({"nom": {"type": "string", "description": "item name or part of it (game language)"},
                            "emplacement": {"type": "string", "description": SLOT_HELP},
                            "type": {"type": "string", "description": "French or English: leather/cuir, mail/maille, "
                                                                      "cloth/tissu, plate/plaques, gun/fusil, bow/arc, "
                                                                      "crossbow/arbalète, dagger/dague, ring/anneau…"},
                            "niveau_min": {"type": "integer", "description": "minimum required level"},
                            "niveau_max": {"type": "integer", "description": "maximum required level"},
                            "qualite_min": {"type": "string", "description": "minimum quality (green/vert, blue/bleu… or 0-5)"},
                            "stat": {"type": "string", "description": "agility/agilite, strength/force, stamina/endurance, ap/pa…"},
                            "forever_seulement": {"type": "boolean", "description": "only items created or modified by Forever"},
                            "limite": {"type": "integer", "description": "max results"}})},
    {"name": "get_item", "title": "Item sheet (local DB)",
     "description": "Full item sheet: stats, armor, damage, required level, data origin (client or Forever "
                    "hotfix), known sources, recipe that makes it, recipes that use it, and verdict for the character.",
     "inputSchema": schema({"itemId": {"type": "integer"}, "nom": {"type": "string", "description": "item name (game language)"},
                            "perso": PERSO})},
    {"name": "get_dungeon_loot", "title": "Dungeon: bosses and loot (local DB)",
     "description": "Bosses of a dungeon or raid (including Forever's new dungeons) and its loot when known, "
                    "evaluated for the character. Without parameter: list of dungeons and raids.",
     "inputSchema": schema({"donjon": {"type": "string", "description": "dungeon name (game language)"}, "perso": PERSO})},
    {"name": "find_recipes", "title": "Profession recipes (local DB)",
     "description": "Recipes of a profession by rank (≈ estimated), with the crafted item and its stats, and the "
                    "reagents. Default: the character's main profession, around its current rank.",
     "inputSchema": schema({"metier": {"type": "string", "description": "profession, French or English "
                                                                       "(Leatherworking/Travail du cuir…)"},
                            "rang_min": {"type": "integer", "description": "minimum rank"},
                            "rang_max": {"type": "integer", "description": "maximum rank"},
                            "limite": {"type": "integer", "description": "max results"}, "perso": PERSO})},
    {"name": "get_quest_info", "title": "Quest sheet (local DB + QuestieDB)",
     "description": "Everything about one quest: level, required level, zone, faction/class restrictions, quest "
                    "giver and turn-in NPC with /way coordinates, objectives with where to find the mobs, objects "
                    "and items (drops, vendors), prerequisites, next quest in the chain, breadcrumbs, and the "
                    "character's status (done, in log, ready to turn in). Search by id or title (game language "
                    "or English).",
     "inputSchema": schema({"questId": {"type": "integer"},
                            "titre": {"type": "string", "description": "quest title (game language or English)"},
                            "perso": PERSO})},
    {"name": "find_quests", "title": "Available quests in a zone (QuestieDB)",
     "description": "Quests the character can pick up in a zone (default: current zone) around its level: race, "
                    "class and prerequisites checked, quests already done or in the log removed. Each with the "
                    "quest giver and /way. Call it for \"what quests here?\", \"where to quest at my level?\".",
     "inputSchema": schema({"zone": {"type": "string", "description": "zone name (game language); default: current zone"},
                            "niveau_min": {"type": "integer", "description": "minimum quest level (default: grey limit)"},
                            "niveau_max": {"type": "integer", "description": "maximum required level (default: level + 3)"},
                            "limite": {"type": "integer", "description": "max quests listed (default 15)"},
                            "perso": PERSO})},
    {"name": "find_npc", "title": "Find an NPC, mob or object (QuestieDB)",
     "description": "Where an NPC, a monster or a world object is (zone and /way, current zone first), its level, "
                    "title and the quests it gives or receives. Name in the game language or English.",
     "inputSchema": schema({"nom": {"type": "string", "description": "NPC, mob or object name"},
                            "npcId": {"type": "integer"},
                            "limite": {"type": "integer", "description": "max results (default 5)"},
                            "perso": PERSO})},
    {"name": "compare_characters", "title": "Compare characters",
     "description": "Table of all characters (or a selection): class, level, zone, ilvl, money, professions, and "
                    "who has which profession (useful to know who can craft an item).",
     "inputSchema": schema({"persos": {"type": "array", "items": {"type": "string"},
                                       "description": "character names (default: all)"}})},
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
                self.log(f"sync: {', '.join(rep['updated'])}")
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
                fn: Optional[Callable[[Dict[str, Any]], str]] = getattr(self.tools, name, None) \
                    if name in {t["name"] for t in TOOL_DEFS} else None
                if not fn:
                    return self.error(mid, -32602, f"Unknown tool: {name}")
                self.ensure_sync()
                lang = self.tools.prepare(args)
                with I.using(lang):
                    try:
                        text = fn(args)
                        result = {"content": [{"type": "text", "text": text}], "isError": False}
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
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except AttributeError:
        pass
    Server().serve()


if __name__ == "__main__":
    main()
