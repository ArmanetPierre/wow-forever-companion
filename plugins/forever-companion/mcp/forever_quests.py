"""Quêtes propres à Forever (absentes de QuestieDB) : fusion des sources locales et de Wowhead à la demande.

Ordre de confiance, du plus sûr au moins sûr (docs/conception/plan-quetes-forever.md) :

1. **observé en jeu** : mémoire des quêtes de l'addon (perso/<Utilisateur>/memoire-quetes.json) —
   donneur et receveur réels, avec la position du joueur au moment du dialogue ;
2. **QuestieDB** (tables q_*) ;
3. **cache du client** (tables c_*, gamedata/clientcache.py) : texte de la quête ; les PNJ et lieux
   qu'il nomme sont rapprochés par leur nom, donc **probables** ;
4. **Wowhead Forever** (wowhead.py) : position d'un PNJ ou d'un objet que rien d'autre ne situe, nom
   d'une quête jamais vue ; une requête par id, seulement pour la question posée.

Mélangé à Tools (server.py) avant QuestDBToolsMixin, dont il utilise where(), npc(), status_text().
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

import formats as F
import gamedb as GDB
import gear as G
import questmemory as QM
import wowhead as WH
from i18n import T
from luasv import as_list
from sync import load_json

BADGE_SEEN_FR = "[Forever · observé en jeu]"
BADGE_CACHE_FR = "[Forever · cache du client]"
BADGE_WOWHEAD = "[Wowhead Forever]"
MAX_MENTIONS = 4
MAX_PLACES = 4
DESC_CHARS = 280


def badge_seen() -> str:
    return T(BADGE_SEEN_FR)


def badge_cache() -> str:
    return T(BADGE_CACHE_FR)


class ForeverQuestsMixin:
    _mem_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
    _names_cache: Dict[str, Dict[str, Any]] = {}

    # -- accès -------------------------------------------------------------------
    def quest_memory(self, char: Optional[Dict[str, Any]] = None,
                     db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mémoire des quêtes de l'utilisateur du perso (vide si l'addon 1.4 n'a encore rien noté)."""
        user = (char or {}).get("user")
        if not user and db:
            guid = F.g(db, "meta", "guid")
            try:
                user = (self.store.config.get("characters", {}).get(guid) or {}).get("user")
            except Exception:
                user = None
        if not user:
            return {}
        path = QM.path_for(self.store.data_dir, user)
        try:
            mtime = path.stat().st_mtime
        except OSError:
            return {}
        cached = self._mem_cache.get(str(path))
        if cached and cached[0] == mtime:
            return cached[1]
        data = load_json(path, {}) or {}
        self._mem_cache[str(path)] = (mtime, data)
        return data

    def memory_mtime(self, char: Optional[Dict[str, Any]], db: Optional[Dict[str, Any]]) -> int:
        self.quest_memory(char, db)
        user = (char or {}).get("user")
        try:
            return int(QM.path_for(self.store.data_dir, user).stat().st_mtime) if user else 0
        except OSError:
            return 0

    def web(self, gdb: Optional[GDB.GameDB]) -> WH.Wowhead:
        """Client Wowhead du présent appel (budget remis à zéro à chaque outil)."""
        wh = getattr(self, "_wh", None)
        stamp = getattr(self, "_call_stamp", None)
        if wh is None or getattr(self, "_wh_stamp", None) != stamp:
            try:
                enabled = self.store.config.get("web_lookup", True) is not False
            except Exception:
                enabled = True
            locale = getattr(self, "_locale", None) or (gdb.meta.get("locale") if gdb else None)
            cache = gdb.path.parent / ".cache" / "wowhead" if gdb else None
            wh = WH.Wowhead(cache, locale, enabled=enabled, fetch=getattr(self, "_wh_fetch", WH.default_fetch))
            self._wh, self._wh_stamp = wh, stamp
        return wh

    @staticmethod
    def has_table(gdb: Optional[GDB.GameDB], name: str) -> bool:
        return bool(gdb and gdb.q("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)))

    # -- zones et positions --------------------------------------------------------
    def map_zone_name(self, gdb: Optional[GDB.GameDB], map_id: Any, db: Optional[Dict[str, Any]] = None) -> str:
        zid = QM.UIMAP_ZONE.get(map_id) if isinstance(map_id, int) else None
        if zid and gdb:
            rows = gdb.q("SELECT name FROM zones WHERE id = ?", (zid,))
            if rows and rows[0]["name"]:
                return rows[0]["name"]
        if db and F.g(db, "position", "mapId") == map_id:
            return F.g(db, "position", "zone") or T("carte {id}", id=map_id)
        return T("carte {id}", id=map_id)

    def point_text(self, gdb: Optional[GDB.GameDB], p: Dict[str, Any], db: Optional[Dict[str, Any]] = None,
                   n: int = 1) -> str:
        return f"{self.map_zone_name(gdb, p.get('mapId'), db)} · `/way {p['x']:.1f} {p['y']:.1f}`" \
            + (T(" ({n} points)", n=n) if n > 1 else "")

    def points_text(self, gdb: Optional[GDB.GameDB], points: List[Dict[str, Any]],
                    db: Optional[Dict[str, Any]] = None, max_maps: int = 2) -> List[str]:
        by_map: Dict[Any, List[Dict[str, Any]]] = {}
        for p in points:
            if isinstance(p, dict) and p.get("x") is not None:
                by_map.setdefault(p.get("mapId"), []).append(p)
        out = []
        for _m, pts in sorted(by_map.items(), key=lambda kv: -len(kv[1]))[:max_maps]:
            out.append(self.point_text(gdb, QM.medoid(pts), db, len(pts)))
        return out

    def wowhead_where(self, gdb: Optional[GDB.GameDB], kind: str, rid: Any) -> Optional[str]:
        if not gdb or kind not in ("npc", "object"):
            return None
        data = self.web(gdb).get(kind, rid)
        pos = WH.position(data)
        if not pos:
            return None
        zid, x, y, n = pos
        rows = gdb.q("SELECT name FROM zones WHERE id = ?", (zid,))
        zone = rows[0]["name"] if rows and rows[0]["name"] else T("zone {id}", id=zid)
        return f"{zone} · `/way {x:.1f} {y:.1f}`" + (T(" ({n} points)", n=n) if n > 1 else "") \
            + f" {WH_BADGE()}"

    # -- noms des PNJ, objets et objets d'inventaire ---------------------------------
    def actor_name(self, gdb: Optional[GDB.GameDB], kind: str, rid: Any, mem: Dict[str, Any]) -> Optional[str]:
        loc = getattr(self, "_locale", None)
        table = {"npc": "npcs", "object": "objects"}.get(kind)
        if table:
            m = (mem.get(table) or {}).get(str(rid))
            if m:
                name = QM.title_of(m, loc)
                if name:
                    return name
        if not gdb:
            return None
        if kind == "item":
            it = gdb.item(int(rid))
            return it["name"] if it and it["name"] else None
        for t, col in ((("c_creatures", "name"), ("q_npcs", "coalesce(name_loc, name)")) if kind == "npc" else
                       (("c_objects", "name"), ("q_objects", "coalesce(name_loc, name)"))):
            if self.has_table(gdb, t):
                rows = gdb.q(f"SELECT {col} AS n FROM {t} WHERE id = ?", (int(rid),))
                if rows and rows[0]["n"]:
                    return rows[0]["n"]
        return None

    def actor_where(self, gdb: Optional[GDB.GameDB], kind: str, rid: Any, mem: Dict[str, Any],
                    db: Optional[Dict[str, Any]], own: Optional[Dict[str, Any]] = None,
                    web: bool = True) -> Optional[str]:
        """Position d'un PNJ ou objet : vue en jeu > QuestieDB > Wowhead."""
        if own and own.get("x") is not None:
            return self.point_text(gdb, own, db) + f" {badge_seen()}"
        table = {"npc": "npcs", "object": "objects"}.get(kind)
        m = (mem.get(table) or {}).get(str(rid)) if table else None
        if m and m.get("points"):
            pts = self.points_text(gdb, m["points"], db, 1)
            if pts:
                return pts[0] + f" {badge_seen()}"
        if gdb and kind in ("npc", "object") and self.has_table(gdb, "q_spawns"):
            loc = self.where(gdb, kind, int(rid), None, max_zones=1)
            if loc:
                return loc[0] + " [Forever · QuestieDB]"
        if web:
            return self.wowhead_where(gdb, kind, rid)
        return None

    def actor_text(self, gdb: Optional[GDB.GameDB], a: Dict[str, Any], mem: Dict[str, Any],
                   db: Optional[Dict[str, Any]]) -> str:
        kind, rid = a.get("kind") or "npc", a.get("id")
        name = self.actor_name(gdb, kind, rid, mem)
        if kind == "item":
            return T("objet de l'inventaire **{name}** (id {id}) : clic droit dessus pour lancer la quête",
                     name=name or T("objet {id}", id=rid), id=rid)
        where = self.actor_where(gdb, kind, rid, mem, db, own=a)
        if not name and gdb:                                # nom donné par Wowhead (déjà en cache, sans requête)
            name = (self.web(gdb).cached(kind, rid)[1] or {}).get("name")
        label = f"**{name}**" if name else (T("PNJ {id}", id=rid) if kind == "npc" else T("objet {id}", id=rid))
        if kind == "object":
            label = T("objet **{name}**", name=name or rid)
        if not where and a.get("instance"):
            where = T("en instance")
        return label + (f" — {where}" if where else "")

    # -- PNJ et lieux nommés dans un texte ----------------------------------------
    def _name_index(self, gdb: GDB.GameDB) -> Dict[str, Any]:
        key = f"{gdb.path}:{gdb.path.stat().st_mtime if gdb.path.exists() else 0}"
        if key in self._names_cache:
            return self._names_cache[key]
        names: List[Tuple[str, str, int, str]] = []   # (norm, kind, id, nom affiché)
        if self.has_table(gdb, "c_creatures"):
            names += [(r["name_norm"], "npc", r["id"], r["name"]) for r in
                      gdb.q("SELECT id, name, name_norm FROM c_creatures")]
        if self.has_table(gdb, "c_objects"):
            names += [(r["name_norm"], "object", r["id"], r["name"]) for r in
                      gdb.q("SELECT id, name, name_norm FROM c_objects")]
        if self.has_table(gdb, "q_npcs"):
            for r in gdb.q("SELECT id, coalesce(name_loc, name) AS name, name_norm FROM q_npcs"):
                for part in str(r["name_norm"] or "").split("|"):
                    names.append((part.strip(), "npc", r["id"], r["name"]))
        good = [(n, k, i, d) for n, k, i, d in names if n and (len(n) >= 10 or (" " in n and len(n) >= 6))]
        first: Dict[str, List[Tuple[str, int, str]]] = {}
        for n, k, i, d in good:
            if k == "npc" and " " in n:
                w = n.split()[0]
                if len(w) >= 5:
                    lst = first.setdefault(w, [])
                    if all(x[1] != i for x in lst):
                        lst.append((k, i, d))
        zrows = gdb.q("SELECT name, name_norm FROM zones")
        # lieux : noms de plusieurs mots ou longs (« Ruines » seul est trop vague)
        zones = [(r["name_norm"], r["name"]) for r in zrows
                 if r["name_norm"] and ((" " in r["name_norm"] and len(r["name_norm"]) >= 8)
                                        or len(r["name_norm"]) >= 9)]
        place_words = {w for r in zrows for w in str(r["name_norm"] or "").split()}
        first = {w: v for w, v in first.items() if w not in place_words}
        idx = {"names": good, "first": first, "zones": zones}
        self._names_cache.clear()
        self._names_cache[key] = idx
        return idx

    def mentions(self, gdb: GDB.GameDB, text: str, mem: Dict[str, Any], skip: str = ""
                 ) -> Tuple[List[Tuple[str, int, str]], List[str]]:
        """PNJ (kind, id, nom) et lieux nommés dans un texte de quête, rapprochés par leur nom."""
        tn = f" {F.norm_key(text)} "
        skip_n = F.norm_key(skip)
        idx = self._name_index(gdb)
        found: List[Tuple[str, int, str]] = []
        seen_ids, seen_names = set(), set()
        cands = list(idx["names"])
        for table, kind in (("npcs", "npc"), ("objects", "object")):
            for k, m in (mem.get(table) or {}).items():
                for nm in (m.get("names") or {}).values():
                    n = F.norm_key(nm)
                    if n and len(n) >= 6:
                        cands.append((n, kind, int(k), nm))
        for n, kind, rid, disp in sorted(cands, key=lambda c: -len(c[0])):
            if (kind, rid) in seen_ids or n == skip_n or n in seen_names:
                continue
            if f" {n} " in tn and not any(n in s for s in seen_names):
                found.append((kind, rid, disp))
                seen_ids.add((kind, rid))
                seen_names.add(n)
        # prénoms seuls (« l'ancien Thundris ») : un seul PNJ connu commence par ce mot
        import re
        for w in re.findall(r"\b([A-ZÀ-Ý][\w’'-]{4,})", text):
            wn = F.norm_key(w)
            if not wn or any(wn in s for s in seen_names):
                continue
            lst = idx["first"].get(wn) or []
            if len(lst) == 1 and (lst[0][0], lst[0][1]) not in seen_ids:
                found.append(lst[0])
                seen_ids.add((lst[0][0], lst[0][1]))
                seen_names.add(wn)
        places = []
        for n, name in sorted(idx["zones"], key=lambda z: -len(z[0])):
            if f" {n} " in tn and name not in places and not any(n in F.norm_key(p) for p in places) \
                    and not any(n in s for s in seen_names):
                places.append(name)
        return found[:MAX_MENTIONS], places[:MAX_PLACES]

    # -- fiche d'une quête Forever -----------------------------------------------
    def forever_quest_ids(self, gdb: GDB.GameDB, qid: Any, title: Any, db: Optional[Dict[str, Any]],
                          mem: Dict[str, Any]) -> List[int]:
        if qid:
            return [int(qid)]
        n = F.norm_key(title)
        if not n:
            return []
        exact, loose = [], []

        def add(i: Any, name: Any) -> None:
            try:
                i = int(i)
            except (TypeError, ValueError):
                return
            nn = F.norm_key(name)
            if not nn:
                return
            if nn == n:
                if i not in exact:
                    exact.append(i)
            elif n in nn or all(t in nn for t in n.split()):
                if i not in loose:
                    loose.append(i)

        for q in as_list(F.g(db, "quests", "list")) if db else []:
            add(q.get("id") or q.get("questId"), q.get("title"))
        for k, q in (mem.get("quests") or {}).items():
            for t in (q.get("titles") or {}).values():
                add(k, t)
        for table, col in (("c_quests", "title"), ("quests", "title")):
            if self.has_table(gdb, table):
                for pattern in GDB.like_patterns(title):
                    rows = gdb.q(f"SELECT id, {col} AS t FROM {table} WHERE title_norm LIKE ? LIMIT 12", (pattern,))
                    for r in rows:
                        add(r["id"], r["t"])
                    if rows:
                        break
        return (exact + [i for i in loose if i not in exact])[:5]

    def forever_quest_info(self, gdb: GDB.GameDB, qid: Any, title: Any, char: Optional[Dict[str, Any]],
                           db: Optional[Dict[str, Any]], ctx: Any) -> str:
        """Fiche d'une quête absente de QuestieDB (ou base sans QuestieDB)."""
        mem = self.quest_memory(char, db)
        ids = self.forever_quest_ids(gdb, qid, title, db, mem)
        sheets: List[List[str]] = []
        for i in ids[:2]:
            sheet = self.forever_sheet(gdb, i, char, db, mem, ctx)
            if sheet:
                sheets.append(sheet)
        if not sheets:
            raise self.ToolError(T("Quête inconnue : ni dans ton journal, ni vue en jeu, ni dans QuestieDB, ni sur "
                                   "Wowhead. Vérifie le titre (langue du jeu) ou donne son questId ; sinon mémoire "
                                   "(search), puis web."))
        lines = [gdb.header(), ""]
        for s in sheets:
            lines += s + [""]
        if len(ids) > 2:
            lines.append(T("_Autres quêtes du même nom : {list}._", list=", ".join(str(i) for i in ids[2:])))
        return "\n".join(lines).rstrip()

    def forever_sheet(self, gdb: GDB.GameDB, qid: int, char: Optional[Dict[str, Any]],
                      db: Optional[Dict[str, Any]], mem: Dict[str, Any], ctx: Any) -> List[str]:
        loc = getattr(self, "_locale", None)
        logq = None
        for q in as_list(F.g(db, "quests", "list")) if db else []:
            if (q.get("id") or q.get("questId")) == qid:
                logq = q
                break
        mq = (mem.get("quests") or {}).get(str(qid)) or {}
        cq = None
        if self.has_table(gdb, "c_quests"):
            rows = gdb.q("SELECT * FROM c_quests WHERE id = ?", (qid,))
            cq = rows[0] if rows else None
        client = gdb.q("SELECT * FROM quests WHERE id = ?", (qid,))
        client = client[0] if client else None
        title = (logq or {}).get("title") or QM.title_of(mq, loc) or (cq["title"] if cq else None) \
            or (client["title"] if client and client["title"] else None)
        objective = (cq["objectives"] if cq and cq["objectives"] else None) or \
            (client["objectives"] if client and client["objectives"] else None)
        sources: List[str] = []
        wh_quest = None
        if not title:
            wh_quest = WH.quest_summary(self.web(gdb).get("quest", qid))
            if wh_quest:
                title, objective = wh_quest["name"], wh_quest.get("objective") or objective
                sources.append(WH_BADGE())
            elif client:
                return [f"**{T('(titre inconnu)')}** (id {qid}) — {GDB.origin_note(client)} {GDB.badge()}",
                        T("- Titre et texte inconnus localement : la quête n'a pas encore été vue en jeu.")]
            else:
                return []
        level = (logq or {}).get("level") or mq.get("level") or (wh_quest or {}).get("level")
        head = f"**{title}** (id {qid})"
        if level:
            head += " — " + T("niveau {level}", level=level)
        if logq and logq.get("category"):
            head += f", {logq['category']}"
        st = self.status_text(ctx, qid) if ctx else ""
        if st:
            head += f" · {st}"
        lines: List[str] = []
        # donneur
        starts = mq.get("starts") or []
        if starts:
            lines.append(T("- Donneur : {who}", who=" ; ".join(self.actor_text(gdb, a, mem, db) for a in starts[:2])))
            sources.append(badge_seen())
        elif mq.get("offeredBy"):
            who = " ; ".join(self.actor_text(gdb, a, mem, db) for a in mq["offeredBy"][:2])
            lines.append(T("- Proposée par : {who}", who=who))
            sources.append(badge_seen())
        # receveur
        ends = sorted(mq.get("ends") or [], key=lambda a: -QM.VIA_RANK.get(a.get("via"), 0))
        if any(a.get("via") == "turnin" for a in ends):     # receveur certain : les « probables » sont du bruit
            ends = [a for a in ends if a.get("via") == "turnin"]
        if ends:
            parts = []
            for a in ends[:2]:
                txt = self.actor_text(gdb, a, mem, db)
                if a.get("via") == "listed":
                    txt += " " + T("(probable)")
                parts.append(txt)
            lines.append(T("- À rendre à : {who}", who=" ; ".join(parts)))
            if badge_seen() not in sources:
                sources.append(badge_seen())
        elif mq.get("waypoint"):
            lines.append(T("- Point de rendu (jeu) : {where}", where=self.point_text(gdb, mq["waypoint"], db))
                         + f" {badge_seen()}")
        # objectif et progression
        if objective:
            lines.append(T("- Objectif : {text}", text=F.clean_text(objective)))
        log_obj = [F.clean_text(o.get("text")) for o in as_list((logq or {}).get("objectives")) if o.get("text")]
        if logq:
            for o in as_list(logq.get("objectives")):
                txt = F.clean_text(o.get("text"))
                if txt and F.norm_key(txt) != F.norm_key(F.clean_text(objective)):
                    lines.append(f"  - {txt}" + (" ✔" if o.get("finished") else ""))
        for ik, o in sorted((mq.get("objectives") or {}).items()):
            pts = self.points_text(gdb, o.get("points") or [], db)
            if pts:
                lines.append(T("  - objectif {n} avancé en jeu ici : {where}", n=ik, where=" ; ".join(pts))
                             + f" {badge_seen()}")
        pos = (logq or {}).get("position") or {}
        if pos.get("x") is not None:
            label = T("- Point sur la carte du jeu (à rendre)") if logq.get("complete") else \
                T("- Point sur la carte du jeu (objectif)")
            lines.append(label + " : " + self.point_text(gdb, pos, db) + " [Forever · données perso]")
        elif mq.get("poi") and not mq.get("objectives"):
            lines.append(T("- Point sur la carte du jeu : {where}", where=self.point_text(gdb, mq["poi"], db))
                         + f" {badge_seen()}")
        # texte du cache : PNJ et lieux cités
        text = " ".join(x for x in ((cq["objectives"] if cq else None), (cq["description"] if cq else None),
                                    objective, *log_obj) if x)
        if text:
            if cq:
                sources.append(badge_cache())
            known = {(a.get("kind") or "npc", a.get("id")) for a in starts + ends + (mq.get("offeredBy") or [])}
            npcs, places = self.mentions(gdb, text, mem, skip=title)
            ment = []
            for kind, rid, name in npcs:
                if (kind, rid) in known:
                    continue
                where = self.actor_where(gdb, kind, rid, mem, db, web=not (starts and ends))
                ment.append(f"**{name}**" + (f" — {where}" if where else ""))
            if ment:
                lines.append(T("- Cités dans le texte (probable) : {list}", list=" ; ".join(ment)))
            if places:
                lines.append(T("- Lieux cités : {list}", list=", ".join(places)))
            desc = cq["description"] if cq and cq["description"] else ""
            if desc:
                short = F.clean_text(desc).replace("\n", " ")
                short = short[:DESC_CHARS].rsplit(" ", 1)[0] + " …" if len(short) > DESC_CHARS else short
                lines.append(T("- Texte : « {text} »", text=short))
        if any(WH_BADGE() in ln for ln in lines) and WH_BADGE() not in sources:
            sources.append(WH_BADGE())
        if logq:
            sources.append("[Forever · données perso]")
        lines.insert(0, head + (" " + " ".join(dict.fromkeys(sources)) if sources else ""))
        if not starts and not ends:
            lines.append("_" + T("Donneur et receveur pas encore vus en jeu : l'addon (1.4) les note au prochain "
                                 "dialogue. « Probable » = rapproché par le nom cité dans le texte.") + "_")
        return lines

    # -- quêtes vues proposées dans une zone -----------------------------------------
    def observed_offers(self, gdb: Optional[GDB.GameDB], db: Optional[Dict[str, Any]], mem: Dict[str, Any],
                        ctx: Any, map_id: Any = None, skip: Optional[set] = None) -> List[str]:
        """Quêtes vues proposées par un PNJ de la carte courante, ni faites ni dans le journal."""
        map_id = map_id or F.g(db, "position", "mapId")
        if not mem or not map_id:
            return []
        loc = getattr(self, "_locale", None)
        out = []
        for k, q in (mem.get("quests") or {}).items():
            qid = int(k)
            if skip and qid in skip:
                continue
            if ctx and ctx.status(qid):
                continue
            actors = (q.get("offeredBy") or []) + (q.get("starts") or [])
            here = None
            for a in actors:
                if a.get("mapId") == map_id and a.get("x") is not None:
                    here = a
                    break
                m = (mem.get("npcs") or {}).get(str(a.get("id"))) if a.get("kind", "npc") == "npc" else None
                pts = [p for p in (m or {}).get("points") or [] if p.get("mapId") == map_id]
                if pts:
                    here = {**a, **QM.medoid(pts)}
                    break
            if not here:
                continue
            title = QM.title_of(q, loc) or T("quête {id}", id=qid)
            name = self.actor_name(gdb, here.get("kind") or "npc", here.get("id"), mem) or "?"
            lvl = T(", niv. {level}", level=q["level"]) if q.get("level") else ""
            out.append(f"**{title}** ({qid}{lvl}) — " + T("donneur : **{name}**", name=name)
                       + f" · `/way {here['x']:.1f} {here['y']:.1f}` {badge_seen()}")
        return out

    def turnin_where(self, db: Dict[str, Any], q: Dict[str, Any], mem: Optional[Dict[str, Any]] = None) -> str:
        """« · Zone · `/way …` » d'une quête du journal, toujours avec la carte.

        Quête terminée : receveur vu au rendu > receveur QuestieDB > receveur probable vu en jeu >
        point du client. Le point du client (prochain point de passage) n'est pas toujours le PNJ de rendu.
        """
        gdb = self.gamedb(required=False)
        pos = q.get("position") or {}
        if q.get("complete"):
            mem = mem if mem is not None else self.quest_memory(None, db)
            mq = (mem.get("quests") or {}).get(str(q.get("id") or q.get("questId"))) or {}
            ends = sorted(mq.get("ends") or [], key=lambda a: -QM.VIA_RANK.get(a.get("via"), 0))
            certain = [a for a in ends if a.get("via") == "turnin"]
            probable = [a for a in ends if a.get("via") != "turnin"]
            for a in certain:
                line = self._actor_turnin(gdb, a, mem, db)
                if line:
                    return line
            qid = q.get("id") or q.get("questId")
            if gdb and qid and self.has_table(gdb, "q_quests"):
                rows = gdb.q("SELECT * FROM q_quests WHERE id = ?", (int(qid),))
                if rows:
                    zid = QM.UIMAP_ZONE.get(pos.get("mapId")) if isinstance(pos.get("mapId"), int) else None
                    who = self.actor_line(gdb, rows[0], "end", [zid] if zid else None)
                    if who:
                        return " · " + T("à rendre à {who}", who=who[0])
            for a in probable:
                line = self._actor_turnin(gdb, a, mem, db)
                if line:
                    return line
            if not pos.get("x") and mq.get("waypoint"):
                pos = mq["waypoint"]
        if pos.get("x") is not None and pos.get("y") is not None:
            return " · " + self.point_text(gdb, pos, db)
        return ""

    def _actor_turnin(self, gdb: Optional[GDB.GameDB], a: Dict[str, Any], mem: Dict[str, Any],
                      db: Dict[str, Any]) -> str:
        name = self.actor_name(gdb, a.get("kind") or "npc", a.get("id"), mem)
        where = self.actor_where(gdb, a.get("kind") or "npc", a.get("id"), mem, db, own=a, web=False)
        if name or where:
            return " · " + T("à rendre à **{name}**", name=name or "?") + (f" — {where}" if where else "")
        return ""

    # -- PNJ vus en jeu ou dans le cache du client (outil npc) ------------------------
    def forever_npc_lines(self, gdb: Optional[GDB.GameDB], name: Optional[str], nid: Any,
                          char: Optional[Dict[str, Any]], db: Optional[Dict[str, Any]], ctx: Any,
                          skip: Optional[set] = None, limit: int = 5) -> List[str]:
        """PNJ et objets absents de QuestieDB : mémoire des quêtes, cache du client, Wowhead."""
        mem = self.quest_memory(char, db)
        found: List[Tuple[str, int, str]] = []
        skip = skip or set()
        n = F.norm_key(name)

        def match(nm: Any) -> bool:
            nn = F.norm_key(nm)
            return bool(nn) and (nn == n or n in nn or all(t in nn for t in n.split()))

        for table, kind in (("npcs", "npc"), ("objects", "object")):
            for k, m in (mem.get(table) or {}).items():
                if (nid and int(k) == int(nid)) or (n and any(match(v) for v in (m.get("names") or {}).values())):
                    found.append((kind, int(k), QM.title_of(m, getattr(self, "_locale", None)) or "?"))
        for table, kind in (("c_creatures", "npc"), ("c_objects", "object")):
            if not self.has_table(gdb, table):
                continue
            if nid:
                rows = gdb.q(f"SELECT id, name FROM {table} WHERE id = ?", (int(nid),))
            else:
                rows = []
                for pattern in GDB.like_patterns(name):
                    rows = gdb.q(f"SELECT id, name FROM {table} WHERE name_norm LIKE ? ORDER BY length(name) LIMIT 8",
                                 (pattern,))
                    if rows:
                        break
            found += [(kind, r["id"], r["name"]) for r in rows]
        lines: List[str] = []
        seen = set()
        for kind, rid, nm in found:
            if (kind, rid) in seen or (kind, rid) in skip:
                continue
            seen.add((kind, rid))
            if len(seen) > limit:
                break
            label = T("**{name}** (PNJ {id})", name=nm, id=rid) if kind == "npc" else \
                T("**{name}** (objet {id})", name=nm, id=rid)
            where = self.actor_where(gdb, kind, rid, mem, db)
            lines.append(label)
            lines.append(T("- Où : {where}", where=where or T("position inconnue")))
            gives, takes = [], []
            for k, q in (mem.get("quests") or {}).items():
                title = QM.title_of(q, getattr(self, "_locale", None)) or k
                st = self.status_text(ctx, int(k)) if ctx else ""
                txt = f"*{title}* ({k}{', ' + st if st else ''})"
                if any(a.get("id") == rid and (a.get("kind") or "npc") == kind
                       for a in (q.get("starts") or []) + (q.get("offeredBy") or [])):
                    gives.append(txt)
                if any(a.get("id") == rid and (a.get("kind") or "npc") == kind for a in q.get("ends") or []):
                    takes.append(txt)
            if gives:
                lines.append(T("- Donne : {list}", list=", ".join(gives[:6])) + f" {badge_seen()}")
            if takes:
                lines.append(T("- Reçoit : {list}", list=", ".join(takes[:6])) + f" {badge_seen()}")
        return lines


def WH_BADGE() -> str:  # noqa: N802 — badge sans traduction (nom propre)
    return BADGE_WOWHEAD


def web_disabled_env() -> bool:
    return os.environ.get("FOREVER_WEB_LOOKUP", "1") in ("0", "false", "no")
