"""Arbre de talents complet du perso : table `talents` de la base locale + talents capturés par l'addon.

Pour chaque branche : talents par rangée avec rang actuel/max, marqués pris au max, disponibles
maintenant (`*`) ou bloqués (`x` : points de la rangée ou prérequis), et les points libres.
Règles (Forever, système C_Traits) : une rangée s'ouvre après N points dans la branche
(`req_points`) ; un prérequis (`prereqs`, trait de type 2) est rempli quand un des talents parents
est au rang max (type 3 : tous). Schéma : docs/schema-gamedb.md, table `talents`.
"""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Dict, List, Optional

import formats as F
from i18n import T
from luasv import as_list


def has_table(gdb: Any) -> bool:
    try:
        return bool(gdb.q("SELECT 1 FROM sqlite_master WHERE type='table' AND name='talents'"))
    except Exception:
        return False


def load(gdb: Any, tree_id: Optional[int] = None, class_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Lignes de l'arbre (par treeId capturé, sinon par classe)."""
    rows: List[Any] = []
    if tree_id:
        rows = gdb.q("SELECT * FROM talents WHERE tree_id = ?", (int(tree_id),))
    if not rows and class_id:
        rows = gdb.q("SELECT * FROM talents WHERE class_id = ?", (int(class_id),))
    return [dict(r) for r in rows]


def build_nodes(rows: List[Dict[str, Any]], captured: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Nœuds de l'arbre avec le rang actuel (capture par nodeId, sinon par sort ou nom)."""
    nodes: Dict[int, Dict[str, Any]] = {}
    for r in sorted(rows, key=lambda r: (r["node_id"], r.get("choice") or 0)):
        n = nodes.setdefault(r["node_id"], dict(r, entries=[], rank=0, entry_taken=None))
        n["entries"].append(r)
    by_spell = {e["spell_id"]: n for n in nodes.values() for e in n["entries"] if e.get("spell_id")}
    by_name = {F.norm_key(e["name"]): n for n in nodes.values() for e in n["entries"]
               if e.get("name") and not n["hidden"]}
    for c in captured:
        if not isinstance(c, dict):
            continue
        n = nodes.get(c.get("nodeId")) or by_spell.get(c.get("spellId")) or by_name.get(F.norm_key(c.get("name") or ""))
        if n is None:
            continue
        n["rank"] = int(c.get("rank") or 0)
        if c.get("maxRank"):
            n["max_rank"] = int(c["maxRank"])
        n["entry_taken"] = c.get("entryId")
        n["captured_name"] = c.get("name")
    return nodes


def node_name(n: Dict[str, Any]) -> str:
    ents = n["entries"]
    if n.get("entry_taken"):
        ents = [e for e in ents if e["entry_id"] == n["entry_taken"]] or ents
    names = [e.get("name") for e in ents if e.get("name")]
    return " / ".join(names) or n.get("captured_name") or f"#{n['node_id']}"


def analyse(nodes: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Points par branche et statut de chaque nœud : max, dispo (peut recevoir un point), rangee, prereq."""
    spent: Dict[Any, int] = defaultdict(int)
    for n in nodes.values():
        spent[n["tab"]] += n["rank"]
    for n in nodes.values():
        maxr = n.get("max_rank") or 1
        pre = json.loads(n["prereqs"]) if n.get("prereqs") else []
        parents = [(nodes.get(p), typ) for p, typ in pre]
        parents = [(p, typ) for p, typ in parents if p is not None]
        sufficient = [p for p, typ in parents if typ != 3]
        required = [p for p, typ in parents if typ == 3]
        ok_pre = (not sufficient or any(p["rank"] >= (p.get("max_rank") or 1) for p in sufficient)) and \
            all(p["rank"] >= (p.get("max_rank") or 1) for p in required)
        n["missing_parents"] = [] if ok_pre else [p for p in sufficient + required
                                                  if p["rank"] < (p.get("max_rank") or 1)]
        if n["rank"] >= maxr:
            n["status"] = "max"
        elif spent[n["tab"]] < (n.get("req_points") or 0):
            n["status"] = "rangee"
        elif not ok_pre:
            n["status"] = "prereq"
        else:
            n["status"] = "dispo"
    return dict(spent)


def _talent(n: Dict[str, Any]) -> str:
    s = f"{node_name(n)} {n['rank']}/{n.get('max_rank') or 1}"
    if n["status"] == "dispo":
        return s + " *"
    if n["status"] == "prereq":
        s += " x"
    if n["status"] in ("prereq", "rangee") and n["missing_parents"]:
        s += " " + T("(après {list})", list=", ".join(
            f"{node_name(p)} {p.get('max_rank') or 1}/{p.get('max_rank') or 1}" for p in n["missing_parents"]))
    return s


def render(gdb: Any, db: Dict[str, Any], detail: str = "court") -> List[str]:
    """Vue `arbre` de l'outil talents ; lignes Markdown, courte par défaut."""
    if gdb is None:
        return ["", T("_Arbre de talents : la base locale du jeu n'est pas construite._")]
    if not has_table(gdb):
        return ["", T("_Arbre de talents absent de la base locale (base trop ancienne) : reconstruis-la "
                      "(`{cmd} --force`)._", cmd=_build_cmd())]
    t = F.g(db, "talents", default={}) or {}
    rows = load(gdb, t.get("treeId"), F.g(db, "identity", "classId"))
    if not rows:
        return ["", T("_Arbre de talents introuvable pour cette classe dans la base locale._")]
    nodes = build_nodes(rows, as_list(t.get("nodes")))
    spent = analyse(nodes)
    free = sum(int(c.get("available") or 0) for c in as_list(t.get("currencies")) if isinstance(c, dict))
    if not free and t.get("unspent"):
        free = int(t["unspent"])
    tabs: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
    for n in nodes.values():
        if not n["hidden"] or n["rank"]:
            tabs[n["tab"]].append(n)
    total = sum(spent.values())
    lines = ["", "**" + T("Arbre de talents") + "** " + gdb.header() + " — "
             + T("{spent} points dépensés, {free} libre(s).", spent=total, free=free),
             "_" + T("Rang actuel/max · * disponible maintenant · x bloqué (points de la rangée ou prérequis).")
             + "_"]
    full = detail == "complet"
    main_tab = max(spent, key=lambda k: spent[k]) if total else None
    for tab in sorted(tabs, key=lambda k: (k is None, k if k is not None else 0)):
        tn = sorted(tabs[tab], key=lambda n: (n["tier"] if n["tier"] is not None else 99, n["col"] or 0))
        name = tn[0].get("tab_name") or T("Branche {n}", n=(tab or 0) + 1)
        pts = spent.get(tab, 0)
        if not pts and not full:
            opened = [_talent(n) for n in tn if n["status"] == "dispo"]
            lines.append("**" + name + "** — " + T("0 pt · ouvert : {list}", list=", ".join(opened) or "—"))
            continue
        lines.append("**" + name + "** — " + T("{n} pts", n=pts))
        rows_by_tier: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
        for n in tn:
            rows_by_tier[n["tier"]].append(n)
        locked_shown = 0
        for tier in sorted(rows_by_tier, key=lambda k: 99 if k is None else k):
            row = rows_by_tier[tier]
            req = max((n.get("req_points") or 0) for n in row)
            if req and pts < req and not full and tab != main_tab:
                locked_shown += 1
                if locked_shown > 1:  # branche secondaire : la première rangée fermée suffit
                    rest = [t for t in rows_by_tier if t is not None and t > tier]
                    lines.append("- " + T("… {n} rangée(s) de plus", n=len(rest) + 1))
                    break
            if tier is None:
                head = T("Retirés")
            elif req and pts < req:
                head = T("Rangée {r} ({req} pts, il en manque {m})", r=tier + 1, req=req, m=req - pts)
            elif req:
                head = T("Rangée {r} ({req} pts)", r=tier + 1, req=req)
            else:
                head = T("Rangée {r}", r=tier + 1)
            lines.append(f"- {head} : " + ", ".join(_talent(n) for n in row))
    if not full:
        lines.append("_" + T("Branches sans point résumées ; arbre:complet pour tout l'arbre.") + "_")
    return lines


def _build_cmd() -> str:
    import gamedb as GDB
    return GDB.build_command()
