"""Outils MCP des quêtes et PNJ, adossés aux tables q_* (QuestieDB) de la base locale :
get_quest_info (enrichi), find_quests, find_npc. Lecture seule.

Les tables q_* sont ajoutées à forever-<locale>.sqlite par gamedata/questie.py (téléchargement chez le
joueur, jamais redistribué). Sans elles, get_quest_info retombe sur le cache des quêtes du client.
"""

from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Optional, Set, Tuple

import formats as F
import gamedb as GDB
from i18n import T
from luasv import as_list

BADGE_FR = "[Forever · QuestieDB]"

# Bits de requiredRaces (QuestieDB) : race du client (raceFile) -> bit ; Éolides (Skyborne) : bits 32/33.
RACE_BITS = {"Human": 1, "Orc": 2, "Dwarf": 4, "NightElf": 8, "Scourge": 16, "Undead": 16, "Tauren": 32,
             "Gnome": 64, "Troll": 128}
ALLIANCE_MASK = 1 | 4 | 8 | 64 | (1 << 32)
HORDE_MASK = 2 | 16 | 32 | 128 | (1 << 33)
PLAYABLE_MASK = ALLIANCE_MASK | HORDE_MASK
SPECIAL_REPEATABLE = 1
# QuestSort (zoneOrSort < 0) des fêtes et événements saisonniers : jamais proposés par find_quests
SEASONAL_SORTS = {22, 41, 284, 364, 366, 369, 370, 374, 375, 376, 1002, 1003, 1004, 1005, 1006, 1007}


def qbadge() -> str:
    return T(BADGE_FR)


def _loads(v: Any) -> Any:
    if not v:
        return None
    try:
        return json.loads(v)
    except ValueError:
        return None


def _ids(v: Any) -> List[int]:
    return [int(x) for x in (_loads(v) or []) if isinstance(x, (int, float))]


def medoid(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Point le plus central d'un nuage (point réel, donc atteignable) ; ≤ 40 points par zone."""
    if len(points) <= 2:
        return points[0]
    return min(points, key=lambda p: sum(math.hypot(p[0] - q[0], p[1] - q[1]) for q in points))


class QuestCtx:
    """Ce que l'on sait du perso pour filtrer les quêtes."""

    def __init__(self, db: Optional[Dict[str, Any]]):
        self.db = db
        ident = F.g(db, "identity") or {}
        self.name = ident.get("name")
        self.level = F.g(db, "progression", "level") or ident.get("level")
        self.faction = ident.get("faction")
        self.race_bit = RACE_BITS.get(ident.get("raceFile") or "")
        cid = GDB.CLASS_IDS.get(ident.get("classFile") or "")
        self.class_bit = (1 << (cid - 1)) if cid else None
        self.done: Set[int] = set(int(i) for i in as_list(F.g(db, "questsCompleted", "ids")) if isinstance(i, int))
        self.known_done = bool(F.g(db, "questsCompleted"))
        self.log: Dict[int, Dict[str, Any]] = {}
        for q in as_list(F.g(db, "quests", "list")):
            qid = q.get("id") or q.get("questId")
            if isinstance(qid, int):
                self.log[qid] = q
        self.trivial = F.g(db, "quests", "trivialRange") or 6

    @property
    def faction_mask(self) -> int:
        if self.faction == "Alliance":
            return ALLIANCE_MASK
        if self.faction == "Horde":
            return HORDE_MASK
        return PLAYABLE_MASK

    def race_ok(self, races: Optional[int]) -> bool:
        races = int(races or 0)
        if not races or not (races & PLAYABLE_MASK) or (races & PLAYABLE_MASK) == PLAYABLE_MASK:
            return True
        if self.race_bit:
            return bool(races & self.race_bit)
        return bool(races & self.faction_mask)

    def class_ok(self, classes: Optional[int]) -> bool:
        return not classes or not self.class_bit or bool(int(classes) & self.class_bit)

    def status(self, qid: int) -> Optional[str]:
        if qid in self.done:
            return "done"
        if qid in self.log:
            return "complete" if self.log[qid].get("complete") else "log"
        return None


class QuestDBToolsMixin:
    """Mélangé à Tools (server.py), après GameDBToolsMixin : utilise self.gamedb et self._db_char."""

    _qzone_cache: Dict[str, Dict[int, str]] = {}

    # -- accès ---------------------------------------------------------------------
    def questdb(self, required: bool = True) -> Optional[GDB.GameDB]:
        gdb = self.gamedb(required=required)
        if gdb is None:
            return None
        if not gdb.q("SELECT 1 FROM sqlite_master WHERE type='table' AND name='q_quests'"):
            if required:
                raise self.ToolError(T(
                    "Les quêtes et PNJ de QuestieDB ne sont pas encore dans la base locale. Ajoute-les une fois "
                    "(téléchargement depuis GitHub, quelques secondes) :\n\n    {cmd}", cmd=questie_command()))
            return None
        return gdb

    def _zones(self, gdb: GDB.GameDB) -> Dict[int, str]:
        key = str(gdb.path)
        if key not in self._qzone_cache:
            self._qzone_cache[key] = {r["id"]: r["name"] for r in gdb.q("SELECT id, name FROM zones")}
        return self._qzone_cache[key]

    def zone_name(self, gdb: GDB.GameDB, zid: Any) -> str:
        return self._zones(gdb).get(zid) or T("zone {id}", id=zid)

    def _zone_ids(self, gdb: GDB.GameDB, name: str) -> List[int]:
        """Zones (AreaTable) dont le nom correspond, en priorité celles qui ont des quêtes."""
        n = F.norm_key(name)
        if not n:
            return []
        rows = gdb.q("SELECT id FROM zones WHERE name_norm = ?", (n,))
        if not rows:
            for pattern in GDB.like_patterns(name):
                rows = gdb.q("SELECT id FROM zones WHERE name_norm LIKE ? ORDER BY length(name)", (pattern,))
                if rows:
                    break
        ids = [r["id"] for r in rows]
        with_quests = [z for z in ids if gdb.q("SELECT 1 FROM q_quests WHERE zone_id = ? LIMIT 1", (z,))]
        return with_quests or ids

    # -- positions -----------------------------------------------------------------
    def where(self, gdb: GDB.GameDB, kind: str, rid: int, prefer_zone: Optional[List[int]] = None,
              max_zones: int = 2) -> List[str]:
        """« Les Paluns · `/way 38.9 52.4` (12 points) » pour un PNJ ou un objet."""
        rows = gdb.q("SELECT zone_id, x, y FROM q_spawns WHERE kind = ? AND id = ?", (kind, int(rid)))
        by_zone: Dict[int, List[Tuple[float, float]]] = {}
        for r in rows:
            by_zone.setdefault(r["zone_id"], []).append((r["x"], r["y"]))
        order = sorted(by_zone, key=lambda z: (0 if prefer_zone and z in prefer_zone else 1, -len(by_zone[z])))
        out = []
        for z in order[:max_zones]:
            x, y = medoid(by_zone[z])
            n = len(by_zone[z])
            out.append(f"{self.zone_name(gdb, z)} · `/way {x:.1f} {y:.1f}`"
                       + (T(" ({n} points)", n=n) if n > 1 else ""))
        return out

    def npc(self, gdb: GDB.GameDB, nid: int) -> Optional[Any]:
        rows = gdb.q("SELECT * FROM q_npcs WHERE id = ?", (int(nid),))
        return rows[0] if rows else None

    def obj(self, gdb: GDB.GameDB, oid: int) -> Optional[Any]:
        rows = gdb.q("SELECT * FROM q_objects WHERE id = ?", (int(oid),))
        return rows[0] if rows else None

    @staticmethod
    def label(row: Any) -> str:
        return (row["name_loc"] or row["name"]) if row else "?"

    def item_name(self, gdb: GDB.GameDB, iid: int) -> str:
        it = gdb.item(iid)
        if it and it["name"]:
            return it["name"]
        rows = gdb.q("SELECT name FROM q_items WHERE id = ?", (int(iid),))
        return rows[0]["name"] if rows and rows[0]["name"] else T("objet {id}", id=iid)

    def quest_title(self, gdb: GDB.GameDB, qid: int) -> str:
        rows = gdb.q("SELECT name, name_loc FROM q_quests WHERE id = ?", (int(qid),))
        if rows:
            return rows[0]["name_loc"] or rows[0]["name"]
        rows = gdb.q("SELECT title FROM quests WHERE id = ?", (int(qid),))
        return (rows[0]["title"] if rows and rows[0]["title"] else None) or T("quête {id}", id=qid)

    def actor_line(self, gdb: GDB.GameDB, q: Any, which: str, zones: Optional[List[int]] = None) -> List[str]:
        """Donneur (start) ou receveur (end) : PNJ, objet, ou objet de l'inventaire."""
        out = []
        for nid in _ids(q[f"{which}_npcs"])[:2]:
            n = self.npc(gdb, nid)
            if not n:
                out.append(T("PNJ {id}", id=nid))
                continue
            sub = f" <{n['subname']}>" if n["subname"] else ""
            loc = self.where(gdb, "npc", nid, zones, max_zones=1)
            out.append(f"**{self.label(n)}**{sub}" + (f" — {loc[0]}" if loc else ""))
        for oid in _ids(q[f"{which}_objects"])[:2]:
            o = self.obj(gdb, oid)
            loc = self.where(gdb, "object", oid, zones, max_zones=1)
            out.append(T("objet **{name}**", name=self.label(o) if o else oid) + (f" — {loc[0]}" if loc else ""))
        if which == "start":
            for iid in _ids(q["start_items"])[:2]:
                out.append(T("objet de l'inventaire **{name}** (id {id}) : clic droit dessus pour lancer la quête",
                             name=self.item_name(gdb, iid), id=iid))
        return out

    def status_text(self, ctx: Optional[QuestCtx], qid: int) -> str:
        if not ctx or not ctx.db:
            return ""
        st = ctx.status(qid)
        if st == "done":
            return T("faite")
        if st == "complete":
            return T("dans ton journal, à rendre")
        if st == "log":
            return T("dans ton journal")
        return T("pas faite") if ctx.known_done else ""

    # -- get_quest_info --------------------------------------------------------------
    def quest_rows_by(self, gdb: GDB.GameDB, qid: Any, title: Any) -> List[Any]:
        if qid:
            return gdb.q("SELECT * FROM q_quests WHERE id = ?", (int(qid),))
        n = F.norm_key(title)
        rows = gdb.q("SELECT * FROM q_quests WHERE name_norm = ? OR name_norm LIKE ? OR name_norm LIKE ? "
                     "ORDER BY level", (n, n + "|%", "%|" + n))
        if rows:
            return rows
        for pattern in GDB.like_patterns(title):
            rows = gdb.q("SELECT * FROM q_quests WHERE name_norm LIKE ? ORDER BY length(name), level LIMIT 6",
                         (pattern,))
            if rows:
                return rows
        return []

    def quest_sheet(self, gdb: GDB.GameDB, q: Any, ctx: Optional[QuestCtx]) -> List[str]:
        qid = q["id"]
        title = q["name_loc"] or q["name"]
        zones = [q["zone_id"]] if q["zone_id"] else None
        head = T("**{title}** (id {id}) — niveau {level}, requis {req}", title=title, id=qid,
                 level=q["level"] or "?", req=q["req_level"] or 1)
        if q["zone_id"]:
            head += f", {self.zone_name(gdb, q['zone_id'])}"
        st = self.status_text(ctx, qid)
        if st:
            head += f" · {st}"
        lines = [head + f" {qbadge()}"]
        if q["name_loc"] and q["name"] and q["name_loc"] != q["name"]:
            lines.append(T("- Titre anglais : {name}", name=q["name"]))
        restr = []
        races = int(q["races"] or 0)
        if races and (races & PLAYABLE_MASK) != PLAYABLE_MASK:
            if not races & HORDE_MASK:
                restr.append("Alliance")
            elif not races & ALLIANCE_MASK:
                restr.append("Horde")
            else:
                restr.append(T("certaines races"))
        if q["classes"]:
            restr.append(T("classe réservée"))
        if ctx and ctx.db and (not ctx.race_ok(q["races"]) or not ctx.class_ok(q["classes"])):
            restr.append(T("**pas pour ce perso**"))
        if q["special_flags"] and int(q["special_flags"]) & SPECIAL_REPEATABLE:
            restr.append(T("répétable"))
        if q["sort_id"] in SEASONAL_SORTS:
            restr.append(T("événement saisonnier"))
        skill = _loads(q["required_skill"])
        if skill:
            restr.append(T("métier requis (compétence {id}, rang {rank})", id=skill[0],
                           rank=skill[1] if len(skill) > 1 else "?"))
        if restr:
            lines.append(T("- Conditions : {list}", list=", ".join(restr)))
        start = self.actor_line(gdb, q, "start", zones)
        if start:
            lines.append(T("- Donneur : {who}", who=" ; ".join(start)))
        end = self.actor_line(gdb, q, "end", zones)
        if end:
            lines.append(T("- À rendre à : {who}", who=" ; ".join(end)))
        texts = _loads(q["objectives_text"]) or []
        if texts:
            lines.append(T("- Objectif : {text}", text=F.clean_text(" ".join(texts))))
        lines.extend(self.objective_lines(gdb, q, zones))
        lines.extend(self.chain_lines(gdb, q, ctx))
        rep = _loads(q["rep_reward"]) or []
        if rep:
            lines.append(T("- Réputation : {list}", list=", ".join(
                f"{T('faction {id}', id=r[0])} +{r[1]}" for r in rep if r and r[0])))
        return lines

    def objective_lines(self, gdb: GDB.GameDB, q: Any, zones: Optional[List[int]]) -> List[str]:
        o = _loads(q["objectives_json"]) or {}
        out = []
        for nid, text in o.get("creatures", [])[:4]:
            n = self.npc(gdb, nid)
            name = text or self.label(n)
            lvl = ""
            if n and n["min_level"]:
                lvl = T(" (niv. {a}-{b})", a=n["min_level"], b=n["max_level"] or n["min_level"]) \
                    if n["max_level"] and n["max_level"] != n["min_level"] else T(" (niv. {a})", a=n["min_level"])
            loc = self.where(gdb, "npc", nid, zones)
            out.append(T("  - tuer **{name}**{lvl}", name=name, lvl=lvl) + (" — " + " ; ".join(loc) if loc else ""))
        for oid, text in o.get("objects", [])[:4]:
            ob = self.obj(gdb, oid)
            loc = self.where(gdb, "object", oid, zones)
            out.append(T("  - utiliser **{name}**", name=text or self.label(ob))
                       + (" — " + " ; ".join(loc) if loc else ""))
        for iid, text in o.get("items", [])[:4]:
            out.append(T("  - récupérer **{name}**", name=text or self.item_name(gdb, iid))
                       + self.item_source(gdb, iid, zones))
        for kc in o.get("killcredit", [])[:2]:
            ids, base, text = (kc + [None, None, None])[:3]
            n = self.npc(gdb, base) if base else None
            loc = self.where(gdb, "npc", base, zones) if base else []
            out.append(T("  - **{name}**", name=text or self.label(n)) + (" — " + " ; ".join(loc) if loc else ""))
        trig = _loads(q["trigger_json"])
        if trig and trig.get("spawns"):
            z, pts = next(iter(trig["spawns"].items()))
            if pts:
                x, y = pts[0]
                out.append(T("  - explorer : {text} — {zone} · `/way {x} {y}`", text=trig.get("text") or "?",
                             zone=self.zone_name(gdb, int(z)), x=f"{x:.1f}", y=f"{y:.1f}"))
        return out

    def item_source(self, gdb: GDB.GameDB, iid: int, zones: Optional[List[int]]) -> str:
        rows = gdb.q("SELECT * FROM q_items WHERE id = ?", (int(iid),))
        if not rows:
            return ""
        r = rows[0]
        npcs, objs, vendors = _ids(r["npc_drops"]), _ids(r["object_drops"]), _ids(r["vendors"])
        bits = []
        if npcs:
            names = [self.label(self.npc(gdb, n)) for n in npcs[:3]]
            loc = self.where(gdb, "npc", npcs[0], zones, max_zones=1)
            more = T(" et {n} autres", n=len(npcs) - 3) if len(npcs) > 3 else ""
            bits.append(T("sur {names}{more}", names=", ".join(names), more=more) + (f", {loc[0]}" if loc else ""))
        if objs:
            ob = self.obj(gdb, objs[0])
            loc = self.where(gdb, "object", objs[0], zones, max_zones=1)
            bits.append(T("dans {name}", name=self.label(ob)) + (f", {loc[0]}" if loc else ""))
        if vendors:
            n = self.npc(gdb, vendors[0])
            bits.append(T("vendu par {name}", name=self.label(n)))
        return (" — " + " ; ".join(bits)) if bits else ""

    def chain_lines(self, gdb: GDB.GameDB, q: Any, ctx: Optional[QuestCtx]) -> List[str]:
        out = []

        def fmt(ids: List[int]) -> str:
            parts = []
            for i in ids[:5]:
                st = self.status_text(ctx, i)
                parts.append(f"*{self.quest_title(gdb, i)}* ({i}{', ' + st if st else ''})")
            return ", ".join(parts)

        pre_single, pre_group = _ids(q["pre_single"]), _ids(q["pre_group"])
        if pre_single:
            out.append(T("- Prérequis (une seule suffit) : {list}", list=fmt(pre_single)) if len(pre_single) > 1
                       else T("- Prérequis : {list}", list=fmt(pre_single)))
        if pre_group:
            out.append(T("- Prérequis (toutes) : {list}", list=fmt(pre_group)))
        if q["breadcrumb_for"]:
            out.append(T("- Quête d'introduction (facultative) qui mène à : {list}", list=fmt([q["breadcrumb_for"]])))
        if q["parent"]:
            out.append(T("- Fait partie de : {list}", list=fmt([q["parent"]])))
        nxt = gdb.q("SELECT id, pre_single, pre_group FROM q_quests WHERE pre_single LIKE ? OR pre_group LIKE ? "
                    "LIMIT 20", (f"%{q['id']}%", f"%{q['id']}%"))
        nxt_ids = [r["id"] for r in nxt if q["id"] in _ids(r["pre_single"]) + _ids(r["pre_group"])][:5]
        if nxt_ids:
            out.append(T("- Suite : {list}", list=fmt(nxt_ids)))
        excl = _ids(q["exclusive_to"])
        if excl:
            out.append(T("- Exclusive avec : {list}", list=fmt(excl)))
        return out

    def get_quest_info(self, args: Dict[str, Any]) -> str:
        qid = args.get("questId")
        title = args.get("titre") or args.get("title")
        if not qid and not title:
            raise self.ToolError(T("Donne le questId ou le titre de la quête."))
        gdb = self.gamedb()
        qdb = self.questdb(required=False)
        char, db = self._db_char(args)
        ctx = QuestCtx(db) if db else None
        rows = self.quest_rows_by(qdb, qid, title) if qdb else []
        if not rows:
            text = self.quest_info_client(gdb, qid, title, db)
            if not qdb:
                text += "\n\n_" + T("Donneur, niveau, objectifs localisés et chaîne : ajoute QuestieDB à la base "
                                    "(`{cmd}`).", cmd=questie_command()) + "_"
            return text
        lines = [gdb.header() + " " + qbadge(), ""]
        for q in rows[:3]:
            lines.extend(self.quest_sheet(qdb, q, ctx))
            lines.append("")
        if len(rows) > 3:
            lines.append(T("_Autres quêtes du même nom : {list}._", list=", ".join(str(r["id"]) for r in rows[3:8])))
        logq = ctx.log.get(rows[0]["id"]) if ctx else None
        if logq:
            lines.append(T("Dans ton journal : **{title}** (niv. {level})", title=logq.get("title"),
                           level=logq.get("level")) + (T(" — à rendre") if logq.get("complete") else ""))
            for o in as_list(logq.get("objectives")):
                lines.append(f"- {F.clean_text(o.get('text'))}" + (" ✔" if o.get("finished") else ""))
        lines.append("_" + T("Source : QuestieDB (communauté Questie), révision {rev} ; positions en % de la carte "
                             "de la zone. Une quête refaite par Forever peut différer : vérifie en jeu si un "
                             "détail ne colle pas.", rev=(qdb.meta.get("questie_commit") or "?")[:10]) + "_")
        return "\n".join(lines)

    def quest_info_client(self, gdb: GDB.GameDB, qid: Any, title: Any, db: Optional[Dict[str, Any]]) -> str:
        """Repli sans QuestieDB : titre et objectif du cache du client, état dans le journal."""
        rows = []
        if qid:
            rows = gdb.q("SELECT * FROM quests WHERE id = ?", (int(qid),))
        else:
            for pattern in GDB.like_patterns(title):
                rows = gdb.q("SELECT * FROM quests WHERE title_norm LIKE ? ORDER BY length(title) LIMIT 5",
                             (pattern,))
                if rows:
                    break
        logq = None
        if db:
            for q in as_list(F.g(db, "quests", "list")):
                lid = q.get("id") or q.get("questId")
                if (qid and lid == int(qid)) or (title and F.norm_key(title) in F.norm_key(q.get("title"))):
                    logq = q
                    break
        if not rows and not logq:
            raise self.ToolError(T("Quête inconnue de la base locale (le client ne connaît que les titres des quêtes "
                                   "déjà vues) et absente du journal. Cherche dans la mémoire, puis sur le web."))
        lines = [gdb.header(), ""]
        for r in rows[:3]:
            lines.append(f"**{r['title'] or T('(titre inconnu)')}** (id {r['id']}) — {GDB.origin_note(r)} "
                         f"{GDB.badge()}")
            if r["objectives"]:
                lines.append(T("- Objectif : {text}", text=F.clean_text(r['objectives'])))
            if not r["title"]:
                lines.append(T("- Titre et texte inconnus localement : la quête n'a pas encore été vue en jeu."))
        if logq:
            lines.append(T("\nDans ton journal : **{title}** (niv. {level})", title=logq.get('title'),
                           level=logq.get('level')) + (T(" — à rendre") if logq.get("complete") else ""))
            for o in as_list(logq.get("objectives")):
                lines.append(f"- {F.clean_text(o.get('text'))}" + (" ✔" if o.get("finished") else ""))
        lines.append("\n_" + T("Ni donneur ni chaîne connus localement pour cette quête (absente de QuestieDB ou "
                                "QuestieDB non importé) : get_quests pour celles du journal, sinon mémoire puis web.")
                     + "_")
        return "\n".join(lines)

    # -- find_quests -----------------------------------------------------------------
    def available(self, q: Any, ctx: QuestCtx) -> bool:
        qid = q["id"]
        if qid in ctx.done or qid in ctx.log:
            return False
        if not ctx.race_ok(q["races"]) or not ctx.class_ok(q["classes"]):
            return False
        if q["sort_id"] in SEASONAL_SORTS:
            return False
        if q["max_level"] and ctx.level and ctx.level > q["max_level"]:
            return False
        pre_single, pre_group = _ids(q["pre_single"]), _ids(q["pre_group"])
        if pre_single and not any(p in ctx.done for p in pre_single):
            return False
        if pre_group and not all(p in ctx.done for p in pre_group):
            return False
        for e in _ids(q["exclusive_to"]):
            if e in ctx.done or e in ctx.log:
                return False
        if q["next_in_chain"] and (q["next_in_chain"] in ctx.done or q["next_in_chain"] in ctx.log):
            return False
        if q["breadcrumb_for"] and (q["breadcrumb_for"] in ctx.done or q["breadcrumb_for"] in ctx.log):
            return False
        if q["parent"] and q["parent"] not in ctx.log:
            return False
        if not (_ids(q["start_npcs"]) or _ids(q["start_objects"]) or _ids(q["start_items"])):
            return False
        return True

    def find_quests(self, args: Dict[str, Any]) -> str:
        gdb = self.questdb()
        char, db = self._db_char(args)
        ctx = QuestCtx(db)
        zone = args.get("zone") or F.g(db, "position", "zone")
        if not zone:
            raise self.ToolError(T("Précise la zone (aucun perso synchronisé pour la deviner)."))
        zids = self._zone_ids(gdb, zone)
        if not zids:
            raise self.ToolError(T("Zone « {zone} » inconnue de la base (nom dans la langue du jeu).", zone=zone))
        level = ctx.level
        lmin = args.get("niveau_min")
        lmax = args.get("niveau_max")
        if lmin is None and level:
            lmin = max(1, level - int(ctx.trivial))
        if lmax is None and level:
            lmax = level + 3
        limit = int(args.get("limite") or 15)
        ph = ",".join("?" * len(zids))
        cand = gdb.q(f"SELECT * FROM q_quests WHERE zone_id IN ({ph}) OR id IN ("
                     f"SELECT CAST(j.value AS INTEGER) FROM q_npcs n, json_each(n.starts) j "
                     f"WHERE n.id IN (SELECT id FROM q_spawns WHERE kind='npc' AND zone_id IN ({ph}))) "
                     f"ORDER BY level, req_level", tuple(zids) * 2)
        avail, later = [], []
        for q in cand:
            if db and not self.available(q, ctx):
                continue
            lvl = q["level"] or 0
            req = q["req_level"] or 1
            if lmax is not None and req > lmax:
                later.append(q)
                continue
            if lmin is not None and lvl and lvl < lmin:
                continue
            avail.append(q)
        zname = self.zone_name(gdb, zids[0])
        if db:
            head = T("**{n} quêtes disponibles** pour {name} (niv. {level}) dans **{zone}**, niveaux {a}-{b}",
                     n=len(avail), name=ctx.name, level=level, zone=zname, a=lmin, b=lmax)
        else:
            head = T("**{n} quêtes** dans **{zone}**", n=len(avail), zone=zname)
        lines = [gdb.header() + " " + qbadge(), "", head + f" {qbadge()}", ""]
        for q in avail[:limit]:
            lines.append(self.quest_line(gdb, q, zids, ctx))
        if len(avail) > limit:
            lines.append(T("- … et {n} autres (limite={limit}).", n=len(avail) - limit, limit=limit))
        if later:
            lines.append(T("\n_Plus tard ({n}) : {list}._", n=len(later), list=", ".join(
                f"{r['name_loc'] or r['name']} ({T('requis {n}', n=r['req_level'])})" for r in later[:5])))
        if ctx.log:
            ready = [q for q in ctx.log.values() if q.get("complete")]
            if ready:
                lines.append(T("\n**À rendre d'abord** : {list}.", list=", ".join(q.get("title") or "?" for q in ready)))
        notes = [T("Filtre : race, classe, prérequis faits, quêtes déjà faites ou dans le journal exclues.")]
        if db and not ctx.known_done:
            notes.append(T("Quêtes terminées non capturées : la liste peut contenir des quêtes déjà faites."))
        notes.append(T("Couverture QuestieDB partielle pour les quêtes ajoutées par Forever."))
        lines.append("\n_" + " ".join(notes) + "_")
        return "\n".join(lines)

    def quest_line(self, gdb: GDB.GameDB, q: Any, zids: List[int], ctx: Optional[QuestCtx]) -> str:
        title = q["name_loc"] or q["name"]
        lvl = T("niv. {level}", level=q["level"] or "?")
        if q["req_level"] and q["req_level"] != q["level"]:
            lvl += T(", requis {n}", n=q["req_level"])
        start = self.actor_line(gdb, q, "start", zids)
        text = f"- **{title}** ({q['id']}, {lvl})"
        if start:
            text += T(" — donneur : {who}", who=start[0])
        pre = _ids(q["pre_single"]) + _ids(q["pre_group"])
        if pre:
            text += T(" · suite de *{title}*", title=self.quest_title(gdb, pre[0]))
        if q["special_flags"] and int(q["special_flags"]) & SPECIAL_REPEATABLE:
            text += T(" · répétable")
        return text

    # -- find_npc ------------------------------------------------------------------
    def find_npc(self, args: Dict[str, Any]) -> str:
        gdb = self.questdb()
        name = args.get("nom") or args.get("name")
        nid = args.get("npcId")
        if not name and not nid:
            raise self.ToolError(T("Donne le nom (ou npcId) du PNJ, du monstre ou de l'objet à trouver."))
        char, db = self._db_char(args)
        ctx = QuestCtx(db) if db else None
        prefer = None
        if db and F.g(db, "position", "zone"):
            prefer = self._zone_ids(gdb, F.g(db, "position", "zone"))
        limit = int(args.get("limite") or 5)
        if nid:
            npcs = gdb.q("SELECT * FROM q_npcs WHERE id = ?", (int(nid),))
            objs = []
        else:
            npcs, objs = self._search(gdb, "q_npcs", name, limit), self._search(gdb, "q_objects", name, limit)
        if not npcs and not objs:
            raise self.ToolError(T("Aucun PNJ ni objet « {name} » dans QuestieDB (nom dans la langue du jeu ou en "
                                   "anglais).", name=name or nid))
        lines = [gdb.header() + " " + qbadge(), ""]
        for n in npcs[:limit]:
            sub = f" <{n['subname']}>" if n["subname"] else ""
            lvl = ""
            if n["min_level"]:
                lvl = T(", niv. {a}", a=n["min_level"]) if not n["max_level"] or n["max_level"] == n["min_level"] \
                    else T(", niv. {a}-{b}", a=n["min_level"], b=n["max_level"])
            fr = {"A": "Alliance", "H": "Horde", "AH": T("Alliance et Horde")}.get(n["friendly"] or "",
                                                                                   T("hostile"))
            lines.append(T("**{name}**{sub} (PNJ {id}{lvl}, {friendly})", name=self.label(n), sub=sub, id=n["id"],
                           lvl=lvl, friendly=fr))
            loc = self.where(gdb, "npc", n["id"], prefer, max_zones=3)
            lines.append(T("- Où : {where}", where=" ; ".join(loc) if loc else T("position inconnue")))
            lines.extend(self._quest_refs(gdb, n, ctx))
        for o in objs[:limit]:
            lines.append(T("**{name}** (objet {id})", name=self.label(o), id=o["id"]))
            loc = self.where(gdb, "object", o["id"], prefer, max_zones=3)
            lines.append(T("- Où : {where}", where=" ; ".join(loc) if loc else T("position inconnue")))
            lines.extend(self._quest_refs(gdb, o, ctx))
        lines.append("_" + T("Positions en % de la carte de la zone (/way). Plusieurs points : le plus central est "
                             "indiqué.") + "_")
        return "\n".join(lines)

    def _search(self, gdb: GDB.GameDB, table: str, name: str, limit: int) -> List[Any]:
        n = F.norm_key(name)
        rows = gdb.q(f"SELECT * FROM {table} WHERE name_norm = ? OR name_norm LIKE ? OR name_norm LIKE ? "
                     f"ORDER BY spawn_count DESC LIMIT ?", (n, n + "|%", "%|" + n, limit))
        if rows:
            return rows
        for pattern in GDB.like_patterns(name):
            rows = gdb.q(f"SELECT * FROM {table} WHERE name_norm LIKE ? ORDER BY length(name), spawn_count DESC "
                         f"LIMIT ?", (pattern, limit))
            if rows:
                return rows
        return []

    def _quest_refs(self, gdb: GDB.GameDB, row: Any, ctx: Optional[QuestCtx]) -> List[str]:
        out = []
        for key, label in (("starts", T("Donne")), ("ends", T("Reçoit"))):
            ids = _ids(row[key])
            if not ids:
                continue
            parts = []
            for i in ids[:6]:
                st = self.status_text(ctx, i)
                parts.append(f"*{self.quest_title(gdb, i)}* ({i}{', ' + st if st else ''})")
            more = T(" et {n} autres", n=len(ids) - 6) if len(ids) > 6 else ""
            out.append(f"- {label} : " + ", ".join(parts) + more)
        return out


def questie_command() -> str:
    return f'cd "{GDB.PLUGIN_ROOT}" && python3 -m gamedata.questie'
