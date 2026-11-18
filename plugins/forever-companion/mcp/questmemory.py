"""Mémoire des quêtes vues en jeu (addon 1.4, `ForeverScribeDB.questMemory`, docs/schema.md § 7).

L'addon note, pour tout un compte, qui donne et qui reçoit chaque quête (avec la position du joueur
au moment du dialogue), les quêtes qu'un PNJ propose et où les objectifs avancent. La synchro fusionne
les comptes d'un même utilisateur dans `perso/<Utilisateur>/memoire-quetes.json` :

- union des entrées, dédoublonnées par `kind` + `id` ;
- pour une même entrée, la position la plus récente (`at`) l'emporte ;
- `via = "turnin"` (receveur certain) prime sur `accept`, qui prime sur `listed` (probable) ;
- points des objectifs, PNJ et objets : union, deux points à moins de 1,5 % comptent pour un.

Ce fichier reste dans le dossier du joueur : jamais dans le dépôt.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

MEMORY_FILE = "memoire-quetes.json"
FORMAT = 1
VIA_RANK = {"turnin": 3, "accept": 2, "listed": 1}
NEAR = 1.5          # % de carte : deux points plus proches comptent pour un
MAX_ACTORS = 3
MAX_OFFERED = 5
MAX_OBJ_POINTS = 12
MAX_POINTS = 8

# UiMapID (C_Map) des zones de Classic -> id AreaTable (table `zones` de la base locale). Ce sont des
# identifiants publics et stables ; ils servent à nommer la zone d'un point noté par l'addon.
UIMAP_ZONE = {
    1411: 14, 1412: 215, 1413: 17, 1416: 36, 1417: 45, 1418: 3, 1419: 4, 1420: 85, 1421: 130, 1422: 28,
    1423: 139, 1424: 267, 1425: 47, 1426: 1, 1427: 51, 1428: 46, 1429: 12, 1430: 41, 1431: 10, 1432: 38,
    1433: 44, 1434: 33, 1435: 8, 1436: 40, 1437: 11, 1438: 141, 1439: 148, 1440: 331, 1441: 400, 1442: 406,
    1443: 405, 1444: 357, 1445: 15, 1446: 440, 1447: 16, 1448: 361, 1449: 490, 1450: 493, 1451: 1377,
    1452: 618, 1453: 1519, 1454: 1637, 1455: 1537, 1456: 1638, 1457: 1657, 1458: 1497, 1459: 2597,
    1460: 3277, 1461: 3358,
}


def entries(v: Any) -> Iterable[Tuple[Any, Any]]:
    """(clé, valeur) d'une table Lua lue par luasv : liste (indices 1..n) ou dict."""
    if isinstance(v, list):
        return ((i + 1, x) for i, x in enumerate(v) if x is not None)
    if isinstance(v, dict):
        return v.items()
    return ()


def seq(v: Any) -> List[Any]:
    return [x for _, x in entries(v) if isinstance(x, dict)]


def _int(k: Any) -> Optional[int]:
    try:
        return int(k)
    except (TypeError, ValueError):
        return None


def _has_pos(p: Dict[str, Any]) -> bool:
    return isinstance(p.get("x"), (int, float)) and isinstance(p.get("y"), (int, float))


def add_point(points: List[Dict[str, Any]], p: Dict[str, Any], cap: int) -> None:
    if not _has_pos(p):
        return
    for q in points:
        if q.get("mapId") == p.get("mapId") and math.hypot(q["x"] - p["x"], q["y"] - p["y"]) < NEAR:
            return
    if len(points) < cap:
        points.append({k: p[k] for k in ("mapId", "x", "y") if p.get(k) is not None})


def _merge_actors(dst: List[Dict[str, Any]], src: List[Dict[str, Any]], cap: int) -> None:
    for a in src:
        if a.get("id") is None:
            continue
        cur = next((d for d in dst if d.get("kind") == a.get("kind") and d.get("id") == a.get("id")), None)
        if cur is None:
            if len(dst) < cap:
                dst.append({k: v for k, v in a.items() if v is not None})
            continue
        if VIA_RANK.get(a.get("via"), 0) > VIA_RANK.get(cur.get("via"), 0):
            cur["via"] = a.get("via")
        if _has_pos(a) and (not _has_pos(cur) or (a.get("at") or 0) >= (cur.get("at") or 0)):
            for k in ("mapId", "x", "y", "at"):
                if a.get(k) is not None:
                    cur[k] = a[k]
            cur.pop("instance", None)
        elif a.get("instance") and not _has_pos(cur):
            cur["instance"] = True


def _latest(a: Optional[Dict[str, Any]], b: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(b, dict) or not _has_pos(b):
        return a
    if a is None or (b.get("at") or 0) >= (a.get("at") or 0):
        return {k: b[k] for k in ("mapId", "x", "y", "at") if b.get(k) is not None}
    return a


def merge(memories: Iterable[Any]) -> Dict[str, Any]:
    """Fusionne des `questMemory` (un par compte) en un dict JSON (clés de quêtes et PNJ en texte)."""
    out: Dict[str, Any] = {"format": FORMAT, "updatedAt": 0, "quests": {}, "npcs": {}, "objects": {}}
    for mem in memories:
        if not isinstance(mem, dict):
            continue
        out["updatedAt"] = max(out["updatedAt"], mem.get("updatedAt") or 0)
        for k, q in entries(mem.get("quests")):
            qid = _int(k)
            if qid is None or not isinstance(q, dict):
                continue
            d = out["quests"].setdefault(str(qid), {"titles": {}, "starts": [], "ends": [], "offeredBy": [],
                                                    "objectives": {}})
            d["titles"].update({lc: t for lc, t in entries(q.get("titles")) if isinstance(t, str) and t})
            for key in ("level", "frequency"):
                if q.get(key):
                    d[key] = max(d.get(key) or 0, q[key])
            if q.get("repeatable"):
                d["repeatable"] = True
            if q.get("turnedIn"):
                d["turnedIn"] = True
            if q.get("firstSeen"):
                d["firstSeen"] = min(d.get("firstSeen") or q["firstSeen"], q["firstSeen"])
            if q.get("lastSeen"):
                d["lastSeen"] = max(d.get("lastSeen") or 0, q["lastSeen"])
            _merge_actors(d["starts"], seq(q.get("starts")), MAX_ACTORS)
            _merge_actors(d["ends"], seq(q.get("ends")), MAX_ACTORS)
            _merge_actors(d["offeredBy"], seq(q.get("offeredBy")), MAX_OFFERED)
            for ik, o in entries(q.get("objectives")):
                if not isinstance(o, dict):
                    continue
                od = d["objectives"].setdefault(str(ik), {"points": []})
                for key in ("type", "need"):
                    if o.get(key) is not None:
                        od[key] = o[key]
                for p in seq(o.get("points")):
                    add_point(od["points"], p, MAX_OBJ_POINTS)
            for key in ("poi", "waypoint"):
                v = _latest(d.get(key), q.get(key))
                if v:
                    d[key] = v
        for table in ("npcs", "objects"):
            for k, n in entries(mem.get(table)):
                nid = _int(k)
                if nid is None or not isinstance(n, dict):
                    continue
                d = out[table].setdefault(str(nid), {"names": {}, "points": []})
                d["names"].update({lc: t for lc, t in entries(n.get("names")) if isinstance(t, str) and t})
                if n.get("lastSeen"):
                    d["lastSeen"] = max(d.get("lastSeen") or 0, n["lastSeen"])
                for p in seq(n.get("points")):
                    add_point(d["points"], p, MAX_POINTS)
    return out


def is_empty(mem: Dict[str, Any]) -> bool:
    return not (mem.get("quests") or mem.get("npcs") or mem.get("objects"))


def path_for(data_dir: Path, user: str) -> Path:
    return Path(data_dir) / user / MEMORY_FILE


def title_of(entry: Dict[str, Any], locale: Optional[str]) -> Optional[str]:
    titles = entry.get("titles") or entry.get("names") or {}
    if locale and titles.get(locale):
        return titles[locale]
    return next(iter(titles.values()), None)


def medoid(points: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    pts = [p for p in points if _has_pos(p)]
    if not pts:
        return None
    if len(pts) <= 2:
        return pts[0]
    return min(pts, key=lambda p: sum(math.hypot(p["x"] - q["x"], p["y"] - q["y"]) for q in pts))
