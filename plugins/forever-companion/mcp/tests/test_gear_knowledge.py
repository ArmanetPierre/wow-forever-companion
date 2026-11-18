"""Tests des règles d'équipement (gear.py) et de la mémoire de recherche (knowledge.py)."""
import copy
import json
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")  # jamais de réseau dans les tests
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import gear as G  # noqa: E402
import knowledge as K  # noqa: E402

FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"


def load_db():
    return json.loads((FIXTURES / "character.json").read_text(encoding="utf-8"))


def armor(sub, loc, level=20, **stats):
    return {"classId": 4, "subclassId": sub, "equipLoc": loc, "requiredLevel": level, "name": "test",
            "stats": stats}


class TestProficiency(unittest.TestCase):
    def test_hunter_mail_before_40(self):
        ok, why = G.proficiency("HUNTER", 25, armor(3, "INVTYPE_HEAD"))
        self.assertFalse(ok)
        self.assertIn("40", why)
        self.assertTrue(G.proficiency("HUNTER", 40, armor(3, "INVTYPE_HEAD"))[0])

    def test_mage_leather_and_cloak(self):
        self.assertFalse(G.proficiency("MAGE", 30, armor(2, "INVTYPE_CHEST"))[0])
        self.assertTrue(G.proficiency("MAGE", 30, armor(1, "INVTYPE_CLOAK"))[0])

    def test_required_level_and_game_flag(self):
        self.assertFalse(G.proficiency("HUNTER", 20, armor(2, "INVTYPE_HAND", level=25))[0])
        item = armor(2, "INVTYPE_HAND")
        item["usable"] = False
        self.assertFalse(G.proficiency("HUNTER", 25, item)[0])

    def test_weapons(self):
        bow = {"classId": 2, "subclassId": 2, "equipLoc": "INVTYPE_RANGED"}
        self.assertTrue(G.proficiency("HUNTER", 25, bow)[0])
        self.assertFalse(G.proficiency("PRIEST", 25, bow)[0])

    def test_dual_wield_slots(self):
        sword = {"equipLoc": "INVTYPE_WEAPON"}
        self.assertEqual(G.target_slots("HUNTER", 15, sword), ["MainHandSlot"])
        self.assertEqual(G.target_slots("HUNTER", 25, sword), ["MainHandSlot", "SecondaryHandSlot"])


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.db = load_db()

    def test_fixture_quest_rewards(self):
        pairs = G.quest_rewards(self.db)
        q, r = next((q, r) for q, r in pairs if r.get("choices"))
        best, evals = G.best_choice(self.db, r)
        by_name = {e["item"]["name"]: e for e in evals}
        self.assertEqual(best["item"]["name"], "Arc des marais")  # vrai gain > emplacement vide minime
        self.assertEqual(by_name["Arc des marais"]["verdict"], "amélioration")
        self.assertEqual(by_name["Gants de pisteur"]["verdict"], "emplacement vide : à équiper")
        self.assertEqual(by_name["Potion de soins"]["verdict"], "non équipable")
        self.assertTrue(by_name["Potion de soins"]["fixed"])

    def test_not_for_you(self):
        ev = G.evaluate(self.db, armor(3, "INVTYPE_HEAD", Agi=10))
        self.assertEqual(ev["verdict"], "pas pour toi")

    def test_gain_14_ap_per_dps(self):
        # +7 Agi pour un chasseur = 14 PA distance = 1 DPS
        slots = self.db["equipment"]["slots"]
        empty = next(s for s in ("HeadSlot", "NeckSlot", "ShoulderSlot") if not slots.get(s))
        loc = {"HeadSlot": "INVTYPE_HEAD", "NeckSlot": "INVTYPE_NECK", "ShoulderSlot": "INVTYPE_SHOULDER"}[empty]
        item = {"classId": 4, "subclassId": 2 if empty != "NeckSlot" else 0, "equipLoc": loc,
                "stats": {"ITEM_MOD_AGILITY_SHORT": 7}}
        ev = G.evaluate(self.db, item)
        self.assertAlmostEqual(ev["gain"]["ranged"], 1.0, places=3)

    def test_empty_slots_skip_shirt(self):
        db = copy.deepcopy(self.db)
        db["equipment"]["slots"].pop("ShirtSlot", None)
        self.assertNotIn("Chemise", G.empty_slots(db))


class TestKnowledge(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.data = self.tmp / "perso"
        self.data.mkdir()
        os.environ.pop("FOREVER_KNOWLEDGE_DIR", None)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_save_then_search(self):
        p = K.save(self.data, "Casques en cuir niveau 20-30", "Quasiment rien avant 30.\nHeaume d'exemple.",
                   sources=["https://exemple.org/a"], certainty="probable [Classic, à confirmer dans Forever]",
                   today=date(2026, 11, 17))
        self.assertEqual(p.parent, self.tmp / "connaissances")
        self.assertEqual(p.name, "2026-11-17-casques-en-cuir-niveau-20-30.md")
        note = K.parse(p)
        self.assertEqual(note["certitude"], "probable [Classic, à confirmer dans Forever]")
        self.assertEqual(note["sources"], "https://exemple.org/a")
        hits = K.search(self.data, "y a-t-il des casques à mon niveau ?")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0][1]["sujet"], "Casques en cuir niveau 20-30")
        self.assertEqual(K.search(self.data, "familier bonheur"), [])

    def test_same_subject_twice_and_validation(self):
        a = K.save(self.data, "Sujet", "un", today=date(2026, 1, 1))
        b = K.save(self.data, "Sujet", "deux", today=date(2026, 1, 1))
        self.assertNotEqual(a, b)
        with self.assertRaises(ValueError):
            K.save(self.data, "Sujet", "x", certainty="peut-être")
        with self.assertRaises(ValueError):
            K.save(self.data, "", "x")

    def test_header_stays_one_line(self):
        p = K.save(self.data, "Sujet\nsur deux lignes", "corps", sources=["a\nb"])
        note = K.parse(p)
        self.assertEqual(note["sujet"], "Sujet sur deux lignes")
        self.assertEqual(note["body"], "corps")

    def test_env_override(self):
        other = self.tmp / "ailleurs"
        os.environ["FOREVER_KNOWLEDGE_DIR"] = str(other)
        try:
            self.assertEqual(K.knowledge_dir(self.data), other)
        finally:
            os.environ.pop("FOREVER_KNOWLEDGE_DIR", None)


if __name__ == "__main__":
    unittest.main()
