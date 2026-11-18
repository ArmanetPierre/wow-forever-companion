"""Arbre de talents : construction de la table `talents` (gamedata/talents.py) et vue arbre (talents_tree.py).

Fixtures synthétiques (aucune donnée de joueur, aucune donnée du client) : perso fictif Brannok,
Nain Chasseur 25.
"""
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MCP = HERE.parent
sys.path.insert(0, str(MCP))
sys.path.insert(0, str(MCP.parent))

import gamedb as GDB  # noqa: E402
import i18n as I  # noqa: E402
import talents_tree as TT  # noqa: E402
from gamedata import talents as TL  # noqa: E402


class FakeTables:
    """Imite GameTables.get() : {table: {id: ligne}}."""

    def __init__(self, tables, origins=None):
        self.tables = tables
        self.origins = origins or {}

    def get(self, name):
        if name not in self.tables:
            raise KeyError(name)
        return self.tables[name]


def fake_client():
    """Arbre de chasseur réduit : 2 branches, 3 rangées, un prérequis, un nœud retiré."""
    nodes, entries, defs, nxe, gxn = {}, {}, {}, {}, {}
    spells = {}

    def node(nid, x, y, maxr, name, groups):
        nodes[nid] = {"ID": nid, "TraitTreeID": 1091, "PosX": x, "PosY": y, "Type": 0, "Flags": 0}
        entries[nid + 1000] = {"ID": nid + 1000, "TraitDefinitionID": nid + 2000, "MaxRanks": maxr}
        defs[nid + 2000] = {"ID": nid + 2000, "SpellID": nid + 3000, "OverrideName_lang": ""}
        spells[nid + 3000] = {"Name_lang": name}
        nxe[nid] = {"ID": nid, "TraitNodeID": nid, "TraitNodeEntryID": nid + 1000, "Index": 0}
        for g in groups:
            gxn[len(gxn) + 1] = {"TraitNodeGroupID": g, "TraitNodeID": nid}

    # branche A (groupe 10) : rangée 0, rangée 1 (5 pts, groupe 11), rangée 2 (10 pts, groupe 12)
    node(1, 1020, 2130, 5, "Aspects mortels", [10, 20, 21])
    node(2, 1620, 2130, 5, "Peau épaisse", [10, 20, 21])
    node(3, 1020, 2730, 2, "Science des chemins", [10, 11, 21])
    node(4, 1620, 3330, 1, "Intimidation", [10, 12])
    node(5, 1620, 39300, 5, "Talent retiré", [10, 12])          # hors de l'arbre
    # branche B (groupe 30, à droite)
    node(6, 5020, 2130, 5, "Trait de choc amélioré", [30])
    conds = {1: {"ID": 1, "CondType": 0, "SpentAmountRequired": 5, "TraitNodeGroupID": 20},
             2: {"ID": 2, "CondType": 0, "SpentAmountRequired": 10, "TraitNodeGroupID": 21},
             3: {"ID": 3, "CondType": 0, "SpentAmountRequired": 0, "TraitNodeGroupID": 0}}
    gxc = {1: {"TraitNodeGroupID": 11, "TraitCondID": 1}, 2: {"TraitNodeGroupID": 12, "TraitCondID": 2},
           3: {"TraitNodeGroupID": 30, "TraitCondID": 3}}  # condition à 0 point : reste une branche
    edges = {1: {"LeftTraitNodeID": 3, "RightTraitNodeID": 4, "Type": 2},
             2: {"LeftTraitNodeID": 4, "RightTraitNodeID": 3, "Type": 2},   # remonte : ignoré
             3: {"LeftTraitNodeID": 1, "RightTraitNodeID": 2, "Type": 0}}   # visuel : ignoré
    return FakeTables({
        "SkillLineXTraitTree": {1: {"SkillLineID": 50, "TraitTreeID": 1091}},
        "TraitNode": nodes, "TraitNodeEntry": entries, "TraitDefinition": defs,
        "TraitNodeXTraitNodeEntry": nxe, "TraitNodeGroupXTraitNode": gxn,
        "TraitNodeGroupXTraitCond": gxc, "TraitCond": conds, "TraitEdge": edges,
        "TalentTab": {361: {"Name_lang": "Maîtrise des bêtes", "ClassMask": 4, "OrderIndex": 0},
                      363: {"Name_lang": "Précision", "ClassMask": 4, "OrderIndex": 1}},
        "SpellName": spells,
    }, origins={"TraitNode": {4: "modifie"}})


def make_db(path, with_talents=True):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany("INSERT INTO meta VALUES (?,?)", [("schema_version", "4" if with_talents else "3"),
                                                       ("build", "1.60.1.0"), ("locale", "frFR")])
    if with_talents:
        TL.write(con, fake_client(), "frFR")
    con.commit()
    con.close()


def capture(nodes, available=0):
    return {"identity": {"name": "Brannok", "classId": 3, "classFile": "HUNTER", "level": 25},
            "talents": {"treeId": 1091, "spent": sum(n["rank"] for n in nodes), "unspent": available,
                        "currencies": [{"id": 3820, "available": available, "spent": 0, "max": 16}],
                        "nodes": nodes}}


class TestBuildRows(unittest.TestCase):
    def setUp(self):
        self.rows = {r[0]: r for r in TL.talent_rows(fake_client(), "frFR")}

    def test_tabs_tiers_columns(self):
        r = self.rows[1]
        self.assertEqual((r[3], r[4], r[5], r[6], r[7], r[8]), (3, 0, "Maîtrise des bêtes", 0, 0, 5))
        self.assertEqual((self.rows[4][6], self.rows[4][7]), (2, 1))
        self.assertEqual((self.rows[6][4], self.rows[6][5], self.rows[6][6]), (1, "Précision", 0))

    def test_points_required_and_prereqs(self):
        self.assertEqual(self.rows[3][13], 5)
        self.assertEqual(self.rows[4][13], 10)
        self.assertEqual(self.rows[4][14], "[[3, 2]]")
        self.assertIsNone(self.rows[3][14])   # trait qui remonte ignoré
        self.assertIsNone(self.rows[2][14])   # trait visuel ignoré

    def test_hidden_node_and_origin(self):
        self.assertEqual(self.rows[5][15], 1)
        self.assertIsNone(self.rows[5][6])
        self.assertEqual(self.rows[4][18], "modifie")
        self.assertEqual(self.rows[1][18], "client")
        self.assertIsNone(self.rows[1][11])   # pas de nom anglais dans un client frFR
        self.assertEqual(TL.talent_rows(fake_client(), "enUS")[0][11], TL.talent_rows(fake_client(), "enUS")[0][10])

    def test_client_without_trait_tables(self):
        self.assertEqual(TL.talent_rows(FakeTables({}), "frFR"), [])


class TestTreeView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        make_db(cls.tmp / "new.sqlite")
        make_db(cls.tmp / "old.sqlite", with_talents=False)
        cls.gdb = GDB.GameDB(cls.tmp / "new.sqlite")
        cls.old = GDB.GameDB(cls.tmp / "old.sqlite")

    @classmethod
    def tearDownClass(cls):
        cls.gdb.con.close()
        cls.old.con.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def render(self, nodes, available=0, detail="court", gdb=None):
        with I.using("fr"):
            return "\n".join(TT.render(gdb or self.gdb, capture(nodes, available), detail))

    def test_status(self):
        nodes = TT.build_nodes(TT.load(self.gdb, 1091), [
            {"nodeId": 1, "rank": 5, "maxRank": 5}, {"nodeId": 2, "rank": 1, "maxRank": 3}])
        TT.analyse(nodes)
        self.assertEqual(nodes[1]["status"], "max")
        self.assertEqual(nodes[2]["status"], "dispo")
        self.assertEqual(nodes[3]["status"], "dispo")      # 6 points dans la branche ≥ 5
        self.assertEqual(nodes[4]["status"], "rangee")     # 10 points requis
        self.assertEqual(nodes[6]["status"], "dispo")

    def test_prereq_blocks_until_parent_maxed(self):
        taken = [{"nodeId": 1, "rank": 5}, {"nodeId": 2, "rank": 4}, {"nodeId": 3, "rank": 1}, {"nodeId": 6, "rank": 1}]
        nodes = TT.build_nodes(TT.load(self.gdb, 1091), taken)
        TT.analyse(nodes)
        self.assertEqual(nodes[4]["status"], "prereq")
        taken[2]["rank"] = 2
        nodes = TT.build_nodes(TT.load(self.gdb, 1091), taken)
        TT.analyse(nodes)
        self.assertEqual(nodes[4]["status"], "dispo")

    def test_match_by_spell_or_name_when_node_unknown(self):
        nodes = TT.build_nodes(TT.load(self.gdb, 1091), [{"nodeId": 999, "spellId": 3006, "rank": 2},
                                                          {"name": "Peau epaisse", "rank": 1}])
        self.assertEqual(nodes[6]["rank"], 2)
        self.assertEqual(nodes[2]["rank"], 1)

    def test_render_short(self):
        text = self.render([{"nodeId": 1, "rank": 3, "maxRank": 5}], available=1)
        self.assertIn("3 points dépensés, 1 libre(s)", text)
        self.assertIn("**Maîtrise des bêtes** — 3 pts", text)
        self.assertIn("Aspects mortels 3/5 *", text)
        self.assertIn("Rangée 2 (5 pts, il en manque 2)", text)
        self.assertIn("**Précision** — 0 pt · ouvert : Trait de choc amélioré 0/5 *", text)
        self.assertNotIn("Talent retiré", text)
        self.assertIn("Intimidation 0/1 (après Science des chemins 2/2)", text)

    def test_render_full_and_english(self):
        text = self.render([], detail="complet")
        self.assertIn("**Précision** — 0 pts", text)
        I.MISSING.clear()
        with I.using("en"):
            en = "\n".join(TT.render(self.gdb, capture([{"nodeId": 1, "rank": 1}]), "court"))
        self.assertIn("Talent tree", en)
        self.assertIn("Row 2 (5 pts, 4 missing)", en)
        self.assertEqual(I.MISSING, set())

    def test_old_database_asks_for_rebuild(self):
        text = self.render([], gdb=self.old)
        self.assertIn("reconstruis-la", text)
        self.assertIn("--force", text)

    def test_no_database(self):
        with I.using("fr"):
            self.assertIn("pas construite", "\n".join(TT.render(None, capture([]))))


if __name__ == "__main__":
    unittest.main()
