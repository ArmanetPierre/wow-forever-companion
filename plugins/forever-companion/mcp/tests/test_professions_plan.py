"""Outil `professions` : rang des recettes, paliers, formateurs, parcours de montée et prix marchands.

Base SQLite entièrement inventée (schéma de gamedata/build.py + tables QuestieDB), perso fictif
Brannok (Nain Chasseur 25, Alliance).
"""
import ast
import json
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")  # jamais de réseau dans les tests
import sqlite3
import string
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
import professions_plan as PP  # noqa: E402
from gamedata import build as B  # noqa: E402
from gamedata import questie as Q  # noqa: E402
from gamedata import recipe_colors as RC  # noqa: E402
from gamedata import recipe_rank as RR  # noqa: E402
from i18n_en import EN  # noqa: E402
from questdb_tools import QuestDBToolsMixin  # noqa: E402


def item(iid, name, ilvl, cls=7, sub=0, sell=10, buy=40, skill=None, skill_rank=None, origin="client"):
    row = [None] * 36
    row[0], row[1], row[2], row[3], row[4], row[5] = iid, name, B.norm(name), 1, ilvl, 0
    row[6], row[7], row[28], row[29], row[32], row[33], row[35] = cls, sub, sell, buy, skill, skill_rank, origin
    return row


ITEMS = [
    item(2001, "Cuir d'essai", 5, sell=10),
    item(2002, "Fil d'essai", 5, sell=25, buy=100),
    item(2003, "Bottes d'essai", 20, cls=4, sell=300),
    item(2004, "Patron : Cape d'essai", 25, cls=9, sub=1, buy=500, skill=165, skill_rank=125),
    item(2005, "Cape d'essai", 30, cls=4, sell=400),
    item(2006, "Fusée d'essai", 1, cls=15),
    item(2007, "Poudre d'essai", 6),
    item(2008, "Cuir épais d'essai", 50, sell=30),
    item(2009, "Lunettes d'essai", 20, cls=4, skill=165, skill_rank=90, sell=200),
    item(2011, "Pétard d'essai", 3, skill=165, skill_rank=1),
    item(2012, "Gants du Vide d'essai", 10, cls=4),
]
# (sort, nom, objet fabriqué, composants)
RECIPES = [
    (6001, "Bottes d'essai", 2003, [(2001, 4), (2002, 1)]),
    (6002, "Cape d'essai", 2005, [(2001, 6), (2002, 2)]),
    (6003, "Fusée d'essai", 2006, [(2008, 1)]),
    (6004, "Lunettes d'essai", 2009, [(2001, 2)]),
    (6005, "Poudre d'essai", 2007, [(2001, 1)]),
    (6006, "Pétard d'essai", 2011, [(2007, 1), (2001, 1)]),
    (430000, "Gants du Vide d'essai", 2012, [(2001, 1)]),  # Season of Discovery (origine client) : exclue
]
NPCS = [  # id, nom, titre, zone, faction, drapeaux
    (501, "Formatrice Alpha", "Artisan du cuir - Expert", 2, "A", 19),
    (502, "Formateur Beta", "Artisan du cuir - Compagnon", 1, "A", 19),
    (503, "Formateur Gamma", "Artisan du cuir - Expert", 3, "H", 19),
    (504, "Marchand Delta", "Fournitures d'artisan du cuir", 1, "A", 6),
    (505, "Marchande Epsilon", "Foire d'essai", 3, "AH", 4),
]
# couleurs Classic inventées (table recipe_colors) : (sort, jaune, grise, apprise d'office)
COLORS = [(6005, 15, 35, 1), (6001, 100, 140, 0)]
SPAWNS = [(501, 2, 40.0, 50.0), (502, 1, 10.0, 20.0), (503, 3, 70.0, 70.0), (504, 1, 11.0, 21.0),
          (505, 3, 80.0, 80.0)]


def make_db(path):
    con = sqlite3.connect(path)
    con.executescript(B.SCHEMA)
    con.executescript(Q.SCHEMA)
    con.executemany("INSERT INTO meta VALUES (?,?)", [("build", "0.0.0.1"), ("locale", "frFR")])
    con.executemany("INSERT INTO professions VALUES (?,?,?,?)",
                    [(165, "Travail du cuir", "travail du cuir", 11), (2945, "Travail du cuir", "travail du cuir", 11),
                     (202, "Ingénierie", "ingenierie", 11)])
    con.executemany("INSERT INTO zones VALUES (?,?,?,?,?)",
                    [(1, "Val d'essai", "val d essai", 0, 0), (2, "Cité d'essai", "cite d essai", 0, 0),
                     (3, "Île lointaine", "ile lointaine", 0, 1)])
    con.executemany(f"INSERT INTO items VALUES ({','.join('?' * 36)})", ITEMS)
    names = {r[0]: r[1] for r in ITEMS}
    con.executemany("INSERT INTO recipes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
        (sid, 165, name, B.norm(name), 1, None, None, None, 1, 0, made, 1,
         json.dumps([{"item_id": i, "count": c, "name": names[i]} for i, c in reag], ensure_ascii=False),
         "client", 5, "estimation") for sid, name, made, reag in RECIPES])
    con.executescript(RC.SCHEMA)
    con.executemany("INSERT INTO recipe_colors VALUES (?,?,?,?)", COLORS)
    con.executemany("INSERT INTO q_npcs (id, name, name_norm, subname, zone_id, friendly, npc_flags, spawn_count) "
                    "VALUES (?,?,?,?,?,?,?,1)", [(i, n, B.norm(n), s, z, f, fl) for i, n, s, z, f, fl in NPCS])
    con.executemany("INSERT INTO q_spawns VALUES ('npc',?,?,?,?)", SPAWNS)
    con.executemany("INSERT INTO q_items (id, name, npc_drops, vendors) VALUES (?,?,?,?)",
                    [(2002, "Trial Thread", None, "[504]"), (2004, "Pattern: Trial Cloak", None, "[504]"),
                     (2001, "Trial Leather", "[900]", "[505]")])
    con.commit()
    con.close()


class FakeTools(QuestDBToolsMixin):
    """Juste ce que professions_plan utilise : where, label, _zone_ids (QuestDBToolsMixin)."""


def brannok(rank=106, max_rank=150, level=25, zone="Val d'essai"):
    prof = {"name": "Travail du cuir", "skillLineId": 165, "rank": rank, "max": max_rank, "slot": "primary1"}
    db = {"identity": {"name": "Brannok", "faction": "Alliance", "level": level},
          "progression": {"level": level}, "position": {"zone": zone},
          "professions": {"professions": [prof]}}
    return db, prof


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        path = Path(cls.tmp.name) / "forever-frFR.sqlite"
        make_db(path)
        cls.gdb = GDB.GameDB(path)
        cls.tools = FakeTools()

    @classmethod
    def tearDownClass(cls):
        cls.gdb.con.close()
        cls.tmp.cleanup()

    def catalog(self, db=None):
        return PP.Catalog(self.tools, self.gdb, 165, PP.Place(self.tools, self.gdb, db or brannok()[0]))


class TestRecipeRank(unittest.TestCase):
    def test_sources_in_order(self):
        items = {1: {"ilvl": 1}, 2: {"ilvl": 50}, 3: {"ilvl": 30}, 4: {"ilvl": 20, "required_skill": 202,
                                                                         "required_skill_rank": 215},
                 5: {"ilvl": 6}, 6: {"ilvl": 3, "required_skill": 202, "required_skill_rank": 1},
                 7: {"ilvl": 22}}
        recipes = [
            {"key": "client", "profession_id": 202, "name": "A", "min_rank": 180, "item_id": 7, "reagents": []},
            {"key": "patron", "profession_id": 202, "name": "Cape", "min_rank": 1, "item_id": 3, "reagents": []},
            {"key": "objet", "profession_id": 202, "name": "Coiffe", "min_rank": 1, "item_id": 4, "reagents": []},
            {"key": "ilvl", "profession_id": 202, "name": "Ceinture", "min_rank": 1, "item_id": 7, "reagents": []},
            # objet fabriqué de niveau 1 (feux d'artifice…) : l'ancienne estimation donnait 5
            {"key": "fusee", "profession_id": 202, "name": "Fusée", "min_rank": 1, "item_id": 1,
             "reagents": [{"item_id": 2}]},
            # composant estimé 30 mais consommé par une recette de rang 1 lu dans le client
            {"key": "poudre", "profession_id": 202, "name": "Poudre", "min_rank": 1, "item_id": 5, "reagents": []},
            {"key": "petard", "profession_id": 202, "name": "Pétard", "min_rank": 1, "item_id": 6,
             "reagents": [{"item_id": 5}]},
        ]
        out = RR.assign_ranks(recipes, items.get, lambda p, n: 125 if n == "Cape" else None,
                              lambda p, skill: skill == 202)
        self.assertEqual(out["client"], (180, "client"))
        self.assertEqual(out["patron"], (125, "objet"))
        self.assertEqual(out["objet"], (215, "objet"))
        self.assertEqual(out["ilvl"], (110, "estimation"))
        self.assertEqual(out["fusee"], (225, "estimation"))
        self.assertEqual(out["poudre"], (1, "estimation"))
        self.assertEqual(out["petard"], (1, "objet"))

    def test_trainer_rank_1_recipes_stay_at_1(self):
        """Recettes apprises d'office (couleurs Classic, AcquireMethod 1) : rang 1, même si leurs composants
        (matière brute de niveau 5) suggéraient ≈25 ; estimations bornées dans [jaune − 10, jaune].
        Sorts et couleurs inventés."""
        colors = {7001: (25, 60, True), 7002: (20, 40, True), 7004: (105, 140, False), 7005: (195, 230, False)}
        items = {8001: {"ilvl": 5}, 8002: {"ilvl": 10}, 8003: {"ilvl": 5}, 8009: {"ilvl": 1}, 8004: {"ilvl": 5},
                 8005: {"ilvl": 21}, 8006: {"ilvl": 15}}
        recipes = [
            # produit niveau 10 (≈50 à l'ancienne), apprise d'office
            {"key": (7001, 197), "profession_id": 197, "name": "Rouleau d'essai", "item_id": 8002,
             "reagents": [{"item_id": 8001}]},
            {"key": (7002, 202), "profession_id": 202, "name": "Poudre d'essai", "item_id": 8004,
             "reagents": [{"item_id": 8003}]},
            # recette ajoutée par Forever (sort > 400000), produit niveau 1, composant brut niveau 5
            {"key": (1245250, 171), "profession_id": 171, "name": "Élixir d'essai", "item_id": 8009,
             "reagents": [{"item_id": 8003}], "classic": False},
            # estimation 105 (niveau 21), jaune Classic 105 : reste ≤ jaune
            {"key": (7004, 202), "profession_id": 202, "name": "Tube d'essai", "item_id": 8005, "reagents": []},
            # estimation trop basse (≈75) remontée à jaune Classic − 10 = 185
            {"key": (7005, 202), "profession_id": 202, "name": "Tube fin d'essai", "item_id": 8006,
             "reagents": []},
        ]
        out = RR.assign_ranks(recipes, items.get, lambda p, n: None, lambda p, skill: False, colors)
        self.assertEqual(out[(7001, 197)], (1, "client"))
        self.assertEqual(out[(7002, 202)], (1, "client"))
        self.assertEqual(out[(1245250, 171)], (1, "estimation"))
        self.assertEqual(out[(7004, 202)], (105, "estimation"))
        self.assertEqual(out[(7005, 202)], (185, "estimation"))
        self.assertEqual(RR.classic_of({"spell_id": 7002}, colors), (20, 40, True))
        self.assertIsNone(RR.classic_of({"spell_id": 1245250}, colors))
        # sans couleurs Classic (table absente) : estimations brutes, aucune recette d'office
        bare = RR.assign_ranks(recipes, items.get, lambda p, n: None, lambda p, skill: False)
        self.assertEqual(bare[(7001, 197)], (50, "estimation"))
        self.assertEqual(bare[(7005, 202)], (75, "estimation"))
        self.assertIsNone(RR.classic_of({"spell_id": 7002}, None))

    def test_other_skill_on_product_is_ignored(self):
        items = {1: {"ilvl": 30, "required_skill": 356, "required_skill_rank": 100}}
        out = RR.assign_ranks([{"key": 1, "profession_id": 202, "name": "Leurre", "item_id": 1, "reagents": []}],
                              items.get, lambda p, n: None, lambda p, skill: skill == 202)
        self.assertEqual(out[1], (150, "estimation"))

    def test_pattern_names(self):
        self.assertEqual(RR.pattern_target("Patron : Cape noire en cuir"), "Cape noire en cuir")
        self.assertEqual(RR.pattern_target("Schematic: Blue Firework"), "Blue Firework")
        self.assertEqual(RR.pattern_target("[PÉRIMÉ] Patron : [VIEUX] Gants"), "Gants")
        self.assertIsNone(RR.pattern_target("Cuir léger"))
        self.assertTrue(RR.is_obsolete("[PÉRIMÉ] Patron : X"))


class TestTiers(unittest.TestCase):
    def test_expert_needs_125(self):
        st = PP.tier_status(106, 150, 25)
        self.assertEqual(st["current"], 2)
        self.assertEqual(st["next"]["index"], 3)
        self.assertFalse(st["next"]["skill_ok"])
        self.assertEqual(st["next"]["missing"], 19)
        text = "\n".join(PP.tier_lines(106, 150, 25, True))
        self.assertIn("pas encore : 106/125", text)
        self.assertIn("[Classic]", text)
        verdict = PP.tier_verdict("Travail du cuir", 106, 150, 25)
        self.assertIn("pas encore Expert", verdict)
        self.assertIn("19", verdict)

    def test_ready_and_level_gate(self):
        self.assertIn("tu peux prendre Expert", PP.tier_verdict("Travail du cuir", 130, 150, 25))
        st = PP.tier_status(205, 225, 30)
        self.assertTrue(st["next"]["skill_ok"])
        self.assertFalse(st["next"]["level_ok"])
        self.assertIn("niveau 35", PP.tier_verdict("Travail du cuir", 205, 225, 30))
        self.assertIsNone(PP.tier_verdict("Travail du cuir", 250, 300, 60))

    def test_not_learned(self):
        st = PP.tier_status(None, None, 45)
        self.assertEqual(st["current"], 0)
        self.assertEqual(st["next"]["index"], 1)
        self.assertIn("Pas encore appris", "\n".join(PP.tier_lines(0, None, 45, False)))

    def test_trainer_titles(self):
        self.assertEqual(PP.trainer_tier("Artisan du cuir - Expert", 165), (3, False))
        self.assertEqual(PP.trainer_tier("Artisan du cuir - Artisan", 165), (4, False))
        self.assertEqual(PP.trainer_tier("Ingénieur - Compagnon", 202), (2, False))
        self.assertEqual(PP.trainer_tier("Journeyman Leatherworker", 165), (2, False))
        self.assertEqual(PP.trainer_tier("Maître des Artisans du cuir", 165)[0], None)
        self.assertTrue(PP.trainer_tier("Artisan du cuir - Maître écailles de dragon", 165)[1])
        self.assertTrue(PP.is_trainer_for("Artisan du cuir - Expert", 165))
        self.assertFalse(PP.is_trainer_for("Ingénieur - Expert", 165))


class TestCatalogAndPath(Base):
    def test_ranks_recomputed_at_read_time(self):
        ranks = {r["name"]: (r["rank"], r["source"]) for r in self.catalog().recipes}
        self.assertEqual(ranks["Cape d'essai"], (125, "objet"))         # rang du patron
        self.assertEqual(ranks["Lunettes d'essai"], (90, "objet"))      # objet qui exige le métier
        self.assertEqual(ranks["Bottes d'essai"], (100, "estimation"))  # 5 × niveau 20
        self.assertEqual(ranks["Fusée d'essai"], (225, "estimation"))   # composants (et non 5)

    def test_profession_ranks_helper(self):
        ranks = PP.profession_ranks(self.gdb, 165)
        self.assertEqual(ranks[6002], (125, "objet"))
        self.assertEqual(ranks[6003], (225, "estimation"))

    def test_find_recipes_uses_recomputed_rank(self):
        """La base garde rank_est = 5 (ancienne règle) : find_recipes affiche le rang recalculé."""
        import server
        from types import SimpleNamespace
        old = os.environ.get("FOREVER_GAMEDB")
        os.environ["FOREVER_GAMEDB"] = str(Path(self.tmp.name) / "forever-frFR.sqlite")
        try:
            t = server.Tools.__new__(server.Tools)
            t.store = SimpleNamespace(data_dir=Path(self.tmp.name) / "perso")
            t._gdb = None
            t._char = lambda args: ({}, brannok()[0])
            out = t.find_recipes({"metier": "Travail du cuir", "rang_min": 100, "rang_max": 200})
            low = t.find_recipes({"metier": "Travail du cuir", "rang_min": 1, "rang_max": 10})
        finally:
            if old is None:
                os.environ.pop("FOREVER_GAMEDB", None)
            else:
                os.environ["FOREVER_GAMEDB"] = old
        self.assertIn("- 125 · **Cape d'essai**", out)
        self.assertIn("- ≈100 · **Bottes d'essai**", out)   # estimation : 5 × niveau 20
        self.assertNotIn("Lunettes d'essai", out)            # 90, sous la tranche
        self.assertNotIn("Fusée d'essai", out)       # ≈225, hors tranche
        self.assertNotIn("Cape d'essai", low)        # plus à 5
        self.assertNotIn("5 × niveau de l'objet fabriqué (juste", out)
        self.assertIn("patron, schéma ou plan", out)

    def test_trainers_faction_and_tier(self):
        db, _ = brannok()
        place = PP.Place(self.tools, self.gdb, db)
        names = [t["row"]["name"] for t in PP.find_trainers(self.tools, self.gdb, 165, place, min_tier=3)]
        self.assertEqual(names, ["Formatrice Alpha"])  # Beta : Compagnon seulement ; Gamma : Horde
        lines = "\n".join(PP.trainer_lines(self.tools, self.gdb, 165, place, 3))
        self.assertIn("Cité d'essai · `/way 40.0 50.0`", lines)
        names = [t["row"]["name"] for t in PP.find_trainers(self.tools, self.gdb, 2945, place, min_tier=2)]
        self.assertEqual(names[0], "Formateur Beta")  # même zone d'abord ; ID jumeau Forever accepté

    def test_vendor_and_far_vendor(self):
        cat = self.catalog()
        v = cat.buyable(2002)
        self.assertEqual((v["price"], v["npc"]["name"]), (100, "Marchand Delta"))
        self.assertIsNotNone(cat.vendor(2001))
        self.assertIsNone(cat.buyable(2001))  # vendu seulement sur un autre continent et se récolte

    def test_path(self):
        cat = self.catalog()
        segs = PP.plan_path(cat, 106, 150)
        self.assertTrue(segs)
        self.assertEqual(segs[0]["from"], 106)
        self.assertEqual(segs[-1]["to"], 150)
        used = {s["rec"]["name"] for s in segs if s["rec"]}
        self.assertNotIn("Gants du Vide d'essai", used)
        for s in segs:
            if s["rec"]:
                self.assertLessEqual(s["rec"]["rank"], s["from"])
                self.assertLess(s["from"], s["rec"]["grey"])

    def test_crafts_formula(self):
        rec = {"rank": 100, "yellow": 125, "green": 137, "grey": 150, "skill_ups": 1, "colors_src": "classic"}
        self.assertEqual(PP.crafts_per_point(110, rec), 1.0)
        self.assertAlmostEqual(PP.crafts_per_point(140, rec), 2.5)
        self.assertEqual(PP.crafts_per_point(150, rec), float("inf"))
        self.assertEqual(PP.crafts_per_point(170, rec), float("inf"))
        self.assertEqual(PP.color_at(130, rec), 1)
        # couleurs estimées (≈) : prudence, plus utilisée dès la verte
        est = dict(rec, colors_src="est")
        self.assertEqual(PP.crafts_per_point(137, est), float("inf"))
        self.assertLess(PP.crafts_per_point(136, est), float("inf"))
        self.assertEqual(PP.est_colors(100), (120, 130, 140))

    def test_path_never_grey_and_prefers_orange_yellow(self):
        cat = self.catalog()
        for start, target in ((1, 75), (106, 150), (150, 225)):
            for s in PP.plan_path(cat, start, target):
                rec = s["rec"]
                if not rec:
                    continue
                for skill in range(s["from"], s["to"]):
                    self.assertLess(skill, rec["grey"], (rec["name"], skill))
                    self.assertNotEqual(PP.color_at(skill, rec), 3)
                    if rec["colors_src"] == "est":
                        self.assertLess(PP.color_at(skill, rec), 2, (rec["name"], skill))

    def test_classic_colors_used_for_known_spells(self):
        """Couleurs lues dans la table recipe_colors de la base (valeurs inventées du fixture)."""
        cat = self.catalog()
        self.assertEqual(PP.classic_colors(self.gdb)[6001], (100, 140, False))
        by = {r["spell_id"]: r for r in cat.recipes}
        self.assertEqual(by[6001]["colors_src"], "classic")
        self.assertEqual((by[6001]["yellow"], by[6001]["green"], by[6001]["grey"]), (100, 120, 140))
        self.assertEqual(by[6005]["rank"], 1)          # apprise d'office (fixture)
        self.assertEqual(by[6002]["colors_src"], "est")
        self.assertTrue(all(r["colors_src"] in ("client", "classic", "est") for r in cat.recipes))

    def test_fallback_without_recipe_colors_table(self):
        """Base sans table recipe_colors (réseau absent au build) : couleurs estimées ≈, aucune erreur."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "forever-frFR.sqlite"
            make_db(path)
            con = sqlite3.connect(path)
            con.execute("DROP TABLE recipe_colors")
            con.commit()
            con.close()
            gdb = GDB.GameDB(path)
            try:
                self.assertEqual(PP.classic_colors(gdb), {})
                cat = PP.Catalog(self.tools, gdb, 165, PP.Place(self.tools, gdb, brannok()[0]))
                self.assertTrue(cat.recipes)
                self.assertTrue(all(r["colors_src"] == "est" for r in cat.recipes))
                for s in PP.plan_path(cat, 1, 75):
                    if s["rec"]:
                        for skill in range(s["from"], s["to"]):
                            self.assertLess(PP.color_at(skill, s["rec"]), 2)
            finally:
                gdb.con.close()

    def test_totals_expand_intermediates(self):
        """Pétard d'essai ← Poudre d'essai (même métier) ← Cuir d'essai : la poudre part en « à fabriquer »,
        le cuir en matière brute ; la poudre produite par une étape précédente est déduite."""
        cat = self.catalog()
        by = {r["name"]: r for r in cat.recipes}
        craft, raw, via = PP.expand_steps(cat, [(by["Pétard d'essai"], 5)])
        self.assertEqual(craft, {2007: 5})
        self.assertEqual(raw, {2001: 10})              # 5 directs + 5 pour la poudre
        self.assertEqual(via[2007]["name"], "Poudre d'essai")
        craft, raw, _ = PP.expand_steps(cat, [(by["Poudre d'essai"], 3), (by["Pétard d'essai"], 5)])
        self.assertEqual(craft, {2007: 2})             # 3 poudres déjà faites à l'étape 1
        self.assertEqual(raw, {2001: 3 + 5 + 2})
        lines = "\n".join(PP.totals_lines(self.tools, cat, [(by["Pétard d'essai"], 5)], {}))
        self.assertIn("À fabriquer en route", lines)
        self.assertIn("5 Poudre d'essai", lines)
        self.assertIn("À acheter ou récolter", lines)
        self.assertIn("10 Cuir d'essai", lines)
        self.assertNotIn("Total des composants", lines)

    def test_report_leatherworking_106(self):
        db, prof = brannok()
        lines, verdict = PP.professions_report(self.tools, self.gdb, db, 165, "Travail du cuir", prof,
                                               {2001: 7}, {}, None)
        text = "\n".join(lines)
        self.assertIn("pas encore : 106/125", text)
        self.assertIn("pas encore Expert", verdict)
        self.assertIn("Formatrice Alpha", text)
        self.assertIn("Parcours de 106 à 150", text)
        self.assertIn("marchand 1 pa 0 pc pièce", text)
        self.assertIn("Revente marchand du produit", text)
        self.assertIn("(tu en as 7)", text)
        self.assertIn("Aucun prix d'hôtel des ventes", text)

    def test_report_not_learned_from_1(self):
        db, _ = brannok()
        db["professions"]["professions"] = []
        lines, verdict = PP.professions_report(self.tools, self.gdb, db, 165, "Travail du cuir", None, {}, {}, None)
        text = "\n".join(lines)
        self.assertIsNone(verdict)
        self.assertIn("Parcours de 1 à", text)
        self.assertIn("Pas encore appris", text)

    def test_english_output_has_no_missing_text(self):
        db, prof = brannok()
        I.MISSING.clear()
        with I.using("en"):
            lines, verdict = PP.professions_report(self.tools, self.gdb, db, 165, "Travail du cuir", prof, {}, {},
                                                   None)
        text = "\n".join(lines)
        self.assertIn("not yet: 106/125", text)
        self.assertIn("Path from 106 to 150", text)
        self.assertEqual({m for m in I.MISSING if m in PP.PLAN_EN}, set())


class TestGatheringAndPrimaries(Base):
    def test_skinning_rule(self):
        self.assertEqual(PP.skinning_max_level(1), 10)
        self.assertEqual(PP.skinning_max_level(50), 15)
        self.assertEqual(PP.skinning_max_level(100), 20)
        self.assertEqual(PP.skinning_max_level(141), 28)
        self.assertEqual(PP.skinning_max_level(300), 60)

    def test_gathering_report_has_rules_not_recipes(self):
        db, _ = brannok()
        prof = {"name": "Herboristerie", "skillLineId": 182, "rank": 60, "max": 75, "slot": "primary2"}
        lines, verdict = PP.professions_report(self.tools, self.gdb, db, 182, "Herboristerie", prof, {}, {}, None)
        text = "\n".join(lines)
        self.assertIn("métier de récolte", text)
        self.assertIn("Rang requis par nœud", text)
        self.assertNotIn("Parcours de", text)
        lines, _ = PP.professions_report(self.tools, self.gdb, db, 393, "Dépeçage",
                                         {"name": "Dépeçage", "skillLineId": 393, "rank": 141, "max": 150}, {}, {},
                                         None)
        text = "\n".join(lines)
        self.assertIn("jusqu'au niveau 28", text)
        self.assertNotIn("Parcours de", text)

    def test_two_primaries(self):
        profs = [{"name": "Travail du cuir", "skillLineId": 165, "slot": "primary1"},
                 {"name": "Dépeçage", "skillLineId": 393, "slot": "primary2"},
                 {"name": "Cuisine", "skillLineId": 185, "slot": "secondary"}]
        msg = PP.primary_conflict(self.gdb, 202, profs)
        self.assertIn("2 métiers principaux (Travail du cuir, Dépeçage)", msg)
        self.assertIsNone(PP.primary_conflict(self.gdb, 185, profs))       # Cuisine : secondaire
        self.assertIsNone(PP.primary_conflict(self.gdb, 202, profs[1:]))   # un seul principal


class TestCatalogI18n(unittest.TestCase):
    def test_every_literal_has_english(self):
        fmt = string.Formatter()
        tree = ast.parse((MCP / "professions_plan.py").read_text(encoding="utf-8"))
        missing, bad = [], []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "T" and node.args \
                    and isinstance(node.args[0], ast.Constant):
                k = node.args[0].value
                if k not in EN:
                    missing.append(k)
                elif {f for _, f, _, _ in fmt.parse(k) if f} != {f for _, f, _, _ in fmt.parse(EN[k]) if f}:
                    bad.append(k)
        self.assertEqual(missing, [])
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
