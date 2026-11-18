"""Tests des corrections issues de la première passe d'évaluation (données synthétiques, perso fictif Brannok)."""
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")  # jamais de réseau dans les tests
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import dungeons as DG  # noqa: E402
import formats as F  # noqa: E402
import gamedb as GDB  # noqa: E402
import gear as G  # noqa: E402
import knowledge as K  # noqa: E402
import server  # noqa: E402


def bag(name, class_id, count=1, sub=None, item_id=None):
    return {"name": name, "classId": class_id, "subClassId": sub, "count": count, "itemId": item_id}


def brannok(**extra):
    db = {
        "identity": {"name": "Brannok", "race": "Nain", "class": "Chasseur", "level": 25, "ruleset": "PvP",
                     "account": "123456789#1", "guid": "Player-1234-0A1B2C3D"},
        "progression": {"level": 25},
        "position": {"zone": "Les Paluns"},
        "pet": {"active": True, "current": {
            "name": "Griffe", "family": "Félin", "level": 24, "food": ["Viande", "Poisson"],
            "loyalty": "(Niveau de loyauté 6) Meilleur ami", "happiness": {"level": 3, "damagePct": 125},
            "trainingPoints": {"total": 120, "spent": 76, "available": 44}}},
        "bags": {"containers": {"0": {"items": [
            bag("Poisson-lune sauté", 0, 10, 5),
            bag("Huile de foie de poisson", 0, 3, 8),
            bag("Jus de melon", 0, 3, 5),
            bag("Viande de condor coriace", 7, 1, 8),
            bag("Foie de Broche-tripes", 7, 6, 8),
            bag("Rapport de Shaw", 12),
            bag("Barrette inconnue", 12),
        ]}}},
        "quests": {"list": [
            {"title": "Goulash des Carmines", "objectives": [{"text": "Viande de condor coriace\xa0: 1/5"}]},
            {"title": "La Confrérie défias",
             "objectives": [{"text": "Apporter le Rapport de Shaw à Gryan Stoutmantle."}]},
        ]},
    }
    db.update(extra)
    return db


def tools(db):
    t = server.Tools.__new__(server.Tools)
    t.store = SimpleNamespace(data_dir=Path("/nonexistent"))
    t._gdb = None
    t.gamedb = lambda required=True: None
    t._char = lambda args: ({}, db)
    return t


class PrivacyAndHeader(unittest.TestCase):
    def test_mask_account(self):
        self.assertEqual(F.mask_account("123456789#1"), "••••#1")
        self.assertEqual(F.mask_account(None), "?")
        self.assertNotIn("123456789", F.mask_account("123456789"))

    def test_header_shows_ruleset(self):
        h = F.header(brannok())
        self.assertIn("Les Paluns · PvP", h)
        db = brannok()
        db["identity"]["hardcore"] = True
        self.assertIn("PvP Hardcore", F.header(db))


class PetFood(unittest.TestCase):
    def test_diet_by_item_class_and_quest_items_kept(self):
        t = tools(brannok())
        food = t.pet_food_in_bags(t._char({})[1], t._char({})[1]["pet"]["current"])
        joined = " | ".join(food)
        self.assertIn("Poisson-lune sauté ×10", joined)
        self.assertIn("Foie de Broche-tripes ×6", joined)            # viande crue (7/8)
        self.assertNotIn("Huile", joined)                             # huile : pas de la nourriture
        self.assertNotIn("Jus de melon", joined)                      # boisson
        self.assertNotIn("condor", joined)                            # demandé par une quête du journal
        self.assertTrue(any("condor" in k for k in t.pet_food_kept))

    def test_training_points_formula(self):
        out = tools(brannok()).tool_pet({})
        self.assertIn("24 × 5 = 120 (loyauté au maximum)", out)
        self.assertIn("Gardés pour une quête du journal", out)


class BagsQuestItems(unittest.TestCase):
    def test_quest_items_matched_to_log(self):
        db = brannok()
        uses = tools(db).quest_item_uses(db)
        self.assertEqual(uses[F.norm_key("Rapport de Shaw")], "La Confrérie défias")
        self.assertEqual(uses[F.norm_key("Viande de condor coriace")], "Goulash des Carmines")
        out = tools(db).tool_bags({})
        self.assertIn("Rapport de Shaw → La Confrérie défias", out)
        self.assertIn("ne cite** (à rendre, à utiliser ou début de quête : vérifie avant de jeter) : Barrette inconnue",
                      out)


class DungeonReference(unittest.TestCase):
    def test_names_levels_and_status(self):
        d = DG.by_name("hall of thanes")
        self.assertEqual((d["min"], d["max"], d["badge"]), (13, 18, "forever"))
        self.assertEqual(DG.by_name("Mortemines")["en"], "The Deadmines")
        mc = DG.by_name("Coeur du Magma")
        self.assertFalse(DG.is_open(mc))
        self.assertIn("pas encore ouvert", DG.verdict(mc, 60, "Cœur du Magma"))
        self.assertIn("ouvre le 09/12/2026", DG.status_text(DG.by_name("Onyxia's Lair")))

    def test_verdict_by_level(self):
        d = DG.by_name("Excavations : les Paluns")
        self.assertIn("c'est le bon moment", DG.verdict(d, 25, "Excavations"))
        self.assertIn("encore tôt", DG.verdict(d, 20, "Excavations"))
        self.assertIn("trop bas pour toi", DG.verdict(d, 40, "Excavations"))

    def test_test_maps(self):
        self.assertTrue(DG.is_test_map("Test Dungeon"))
        self.assertTrue(DG.is_test_map("CashTest"))
        self.assertTrue(DG.is_test_map("<unused> Monastery"))
        self.assertFalse(DG.is_test_map("Mortemines"))


class KnowledgeIndex(unittest.TestCase):
    def test_known_quest_bug(self):
        b = K.quest_bug("The Defias Brotherhood")
        self.assertIsNotNone(b)

    def test_plugin_sections_found(self):
        hits = K.search_plugin("hardcore")
        self.assertTrue(hits)


class ItemsAndGear(unittest.TestCase):
    def test_plausible_item(self):
        ok = {"id": 1, "name": "Casque solide", "quality": 2, "ilvl": 25, "req_level": 20, "stats_json": "{}"}
        self.assertTrue(GDB.plausible_item(ok))
        self.assertFalse(GDB.plausible_item(dict(ok, ilvl=120)))
        self.assertFalse(GDB.plausible_item(dict(ok, name="Test Helm")))

    def test_weakest_twin_slot_prefers_empty(self):
        db = {"identity": {"classFile": "HUNTER", "class": "Chasseur"}, "progression": {"level": 25},
              "equipment": {"slots": {"Finger0Slot": {"name": "Anneau", "stats": {"agilite": 3}}}}}
        self.assertEqual(G.weakest_slot(db, ["Finger0Slot", "Finger1Slot"], {"stats": {"agilite": 2}}),
                         "Finger1Slot")


if __name__ == "__main__":
    unittest.main()
