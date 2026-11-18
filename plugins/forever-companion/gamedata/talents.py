"""Arbres de talents des classes (table `talents` de la base locale).

Forever 1.60 n'utilise plus les anciennes tables Talent / TalentTab de Classic (encore présentes dans
le client, mais périmées : talents retirés, rangs différents) : l'interface et l'addon passent par le
système des traits (`C_Traits`). Les arbres viennent donc des DB2 Trait* du client, correctifs du
serveur (DBCache.bin) compris :

- SkillLineXTraitTree : arbre de chaque classe (par sa ligne de compétence) ;
- TraitNode (position) → TraitNodeXTraitNodeEntry → TraitNodeEntry (rang max) → TraitDefinition (sort) ;
- TraitNodeGroupXTraitNode + TraitNodeGroupXTraitCond + TraitCond : la branche (groupe sans exigence de
  points qui réunit le plus de nœuds) et les points à dépenser dans la branche pour ouvrir la rangée ;
- TraitEdge : prérequis (type 2 « suffisant » : un parent au rang max suffit ; type 3 « requis ») ;
- TalentTab : nom des trois branches (ordre de gauche à droite).

Rangée = (PosY − PosY minimal de l'arbre) / 600 ; colonne = (PosX − PosX minimal de la branche) / 600.
Les nœuds placés hors de l'arbre (coordonnée > 20 000) sont des talents retirés par Forever :
`hidden` = 1. Schéma : docs/schema-gamedb.md.
"""
import json
from collections import defaultdict

TABLES = ["SkillLineXTraitTree", "TraitNode", "TraitNodeEntry", "TraitDefinition", "TraitNodeXTraitNodeEntry",
          "TraitNodeGroupXTraitNode", "TraitNodeGroupXTraitCond", "TraitCond", "TraitEdge", "TalentTab"]

# Ligne de compétence de l'arbre (SkillLineXTraitTree.SkillLineID) -> ChrClasses.ID
CLASS_BY_SKILLLINE = {26: 1, 184: 2, 50: 3, 38: 4, 613: 5, 373: 7, 237: 8, 354: 9, 574: 11}

SCHEMA = """
CREATE TABLE IF NOT EXISTS talents (
  node_id INTEGER, entry_id INTEGER, tree_id INTEGER, class_id INTEGER, tab INTEGER, tab_name TEXT,
  tier INTEGER, col INTEGER, max_rank INTEGER, spell_id INTEGER, name TEXT, name_en TEXT, choice INTEGER,
  req_points INTEGER, prereqs TEXT, hidden INTEGER, pos_x INTEGER, pos_y INTEGER, origin TEXT,
  PRIMARY KEY (node_id, entry_id)
);
CREATE INDEX IF NOT EXISTS talents_class ON talents(class_id, tab, tier, col);
CREATE INDEX IF NOT EXISTS talents_tree ON talents(tree_id);
"""

STEP = 600            # écart entre deux rangées ou deux colonnes
HIDDEN_LIMIT = 20000  # au-delà : nœud rangé hors de l'arbre (talent retiré)
EDGE_PREREQ = (2, 3)  # 2 suffisant (un parent au max suffit), 3 requis ; 0 = trait visuel seulement


def _get(T, name):
    try:
        return T.get(name) or {}
    except Exception:  # table absente du client ou du manifeste : pas d'arbre
        return {}


def talent_rows(T, locale="frFR"):
    """Lignes de la table `talents` (une par entrée de nœud ; un nœud à choix a plusieurs entrées)."""
    trees = {}
    for r in _get(T, "SkillLineXTraitTree").values():
        cls = CLASS_BY_SKILLLINE.get(r.get("SkillLineID"))
        if cls and r.get("TraitTreeID"):
            trees[r["TraitTreeID"]] = cls
    if not trees:
        return []
    nodes = {nid: r for nid, r in _get(T, "TraitNode").items() if r.get("TraitTreeID") in trees}
    entries, defs = _get(T, "TraitNodeEntry"), _get(T, "TraitDefinition")
    spell_names = _get(T, "SpellName")
    node_entries = defaultdict(list)
    for r in _get(T, "TraitNodeXTraitNodeEntry").values():
        if r.get("TraitNodeID") in nodes:
            node_entries[r["TraitNodeID"]].append((r.get("Index") or 0, r.get("TraitNodeEntryID")))
    group_nodes, node_groups = defaultdict(set), defaultdict(set)
    for r in _get(T, "TraitNodeGroupXTraitNode").values():
        if r.get("TraitNodeID") in nodes:
            group_nodes[r["TraitNodeGroupID"]].add(r["TraitNodeID"])
            node_groups[r["TraitNodeID"]].add(r["TraitNodeGroupID"])
    conds = _get(T, "TraitCond")
    group_conds = defaultdict(list)
    for r in _get(T, "TraitNodeGroupXTraitCond").values():
        c = conds.get(r.get("TraitCondID"))
        if c:
            group_conds[r["TraitNodeGroupID"]].append(c)
    prereqs = defaultdict(list)
    for r in _get(T, "TraitEdge").values():
        if r.get("Type") in EDGE_PREREQ and r.get("RightTraitNodeID") in nodes:
            prereqs[r["RightTraitNodeID"]].append([r.get("LeftTraitNodeID"), r.get("Type")])
    tabs_db = defaultdict(list)
    for tid, r in _get(T, "TalentTab").items():
        tabs_db[r.get("ClassMask")].append((r.get("OrderIndex") or 0, r.get("Name_lang")))

    def hidden(r):
        return int(abs(r.get("PosX") or 0) > HIDDEN_LIMIT or abs(r.get("PosY") or 0) > HIDDEN_LIMIT)

    # branche : groupe sans condition qui réunit le plus de nœuds de l'arbre
    tab_group = {}
    for nid in nodes:
        free = [g for g in node_groups[nid]
                if not any(c.get("SpentAmountRequired") for c in group_conds.get(g, []))]
        if free:
            tab_group[nid] = max(free, key=lambda g: (len(group_nodes[g]), -g))

    origins = {}
    for t in ("TraitNode", "TraitNodeEntry", "TraitDefinition", "TraitNodeXTraitNodeEntry"):
        origins[t] = getattr(T, "origins", {}).get(t, {})

    out = []
    for tree_id, cls in trees.items():
        tnodes = [nid for nid in nodes if nodes[nid].get("TraitTreeID") == tree_id]
        visible = [nid for nid in tnodes if not hidden(nodes[nid])]
        if not visible:
            continue
        min_y = min(nodes[n].get("PosY") or 0 for n in visible)
        by_group = defaultdict(list)
        for nid in visible:
            by_group[tab_group.get(nid)].append(nid)
        order = sorted((g for g in by_group if g is not None),
                       key=lambda g: sum(nodes[n]["PosX"] for n in by_group[g]) / len(by_group[g]))
        tab_index = {g: i for i, g in enumerate(order)}
        tab_min_x = {g: min(nodes[n]["PosX"] for n in by_group[g]) for g in order}
        names = [n for _, n in sorted(tabs_db.get(1 << (cls - 1), []))]
        for nid in tnodes:
            r = nodes[nid]
            g = tab_group.get(nid)
            tab = tab_index.get(g)
            hid = hidden(r) or tab is None
            req = 0
            for grp in node_groups[nid]:
                for c in group_conds.get(grp, []):
                    if c.get("CondType") == 0 and c.get("SpentAmountRequired"):
                        req = max(req, c["SpentAmountRequired"])
            tier = None if hid else int(round(((r.get("PosY") or 0) - min_y) / STEP))
            col = None if hid else int(round(((r.get("PosX") or 0) - tab_min_x[g]) / STEP))
            # un prérequis est toujours plus haut dans l'arbre : les traits qui remontent sont visuels
            pre = [p for p in prereqs.get(nid, []) if p[0] in nodes and
                   (tier is None or (nodes[p[0]].get("PosY") or 0) < (r.get("PosY") or 0))]
            ents = sorted(node_entries.get(nid, []))
            for choice, (_, eid) in enumerate(ents):
                e = entries.get(eid) or {}
                d = defs.get(e.get("TraitDefinitionID")) or {}
                sid = d.get("SpellID") or None
                name = d.get("OverrideName_lang") or (spell_names.get(sid) or {}).get("Name_lang")
                modified = any(k in origins[t] for t, k in (("TraitNode", nid), ("TraitNodeEntry", eid),
                                                              ("TraitDefinition", e.get("TraitDefinitionID"))))
                out.append((nid, eid, tree_id, cls, tab, names[tab] if tab is not None and tab < len(names) else None,
                            tier, col, e.get("MaxRanks"), sid, name, name if locale == "enUS" else None,
                            choice if len(ents) > 1 else 0, req,
                            json.dumps(sorted(pre)) if pre else None,
                            int(hid), r.get("PosX"), r.get("PosY"), "modifie" if modified else "client"))
    return out


def write(con, T, locale="frFR"):
    """Crée et remplit la table `talents` ; renvoie le nombre de lignes (0 si le client n'a pas d'arbre)."""
    con.executescript(SCHEMA)
    rows = talent_rows(T, locale)
    con.execute("DELETE FROM talents")
    con.executemany(f"INSERT OR REPLACE INTO talents VALUES ({','.join('?' * 19)})", rows)
    return len(rows)
