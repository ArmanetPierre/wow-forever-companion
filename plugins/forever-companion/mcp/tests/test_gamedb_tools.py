"""Tests des outils adossés à la base locale du jeu, sur une petite base synthétique."""
import copy
import json
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")  # jamais de réseau dans les tests
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1] / "gamedata" / "tests"))

import synthetic as SY  # noqa: E402
import server  # noqa: E402

FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"


def fixture_db():
    return json.loads((FIXTURES / "character.json").read_text(encoding="utf-8"))


class GameDBToolsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.tmp.name) / "gamedata" / "forever-frFR.sqlite"
        SY.make_db(cls.db_path)
        cls.old_env = os.environ.get("FOREVER_GAMEDB")
        os.environ["FOREVER_GAMEDB"] = str(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        if cls.old_env is None:
            os.environ.pop("FOREVER_GAMEDB", None)
        else:
            os.environ["FOREVER_GAMEDB"] = cls.old_env
        cls.tmp.cleanup()

    def tools(self, db=None):
        t = server.Tools.__new__(server.Tools)
        t.store = SimpleNamespace(data_dir=Path(self.tmp.name) / "perso")
        t._gdb = None
        data = db if db is not None else fixture_db()
        t._char = lambda args: ({}, data)
        return t

    def test_find_items_filters_junk_and_stat(self):
        out = self.tools().find_items({"stat": "agilite", "niveau_max": 30})
        self.assertIn("Casque d'essai", out)
        self.assertNotIn("PÉRIMÉ", out)
        self.assertIn("[Forever · base locale]", out)

    def test_get_item(self):
        out = self.tools().get_item({"nom": "casque d essai"})
        self.assertIn("20 armure", out)
        self.assertIn("+10 Agi", out)
        self.assertIn("donjon : Donjon d'essai", out)
        self.assertIn("emplacement vide", out)
        out = self.tools().get_item({"itemId": 1006})
        self.assertIn("Composant de : Ceinture fabriquée (Travail du cuir)", out)
        with self.assertRaises(server.ToolError):
            self.tools().get_item({"itemId": 999999})

    def test_find_upgrades(self):
        out = self.tools().find_upgrades({})
        self.assertIn("Casque d'essai", out)          # tête vide chez le perso d'exemple
        self.assertNotIn("Arc trop haut", out)        # niveau requis 40
        self.assertNotIn("Gants de mailles", out)     # maille avant 40 [Classic]
        self.assertNotIn("Bâton de mage", out)        # réservé à une autre classe
        self.assertNotIn("PÉRIMÉ", out)
        out = self.tools().find_upgrades({"emplacement": "tête"})
        self.assertIn("Tête", out)
        self.assertNotIn("Fusil d'essai", out)

    def test_dungeon_loot(self):
        out = self.tools().get_dungeon_loot({"donjon": "donjon d essai"})
        self.assertIn("Boss d'essai", out)
        self.assertIn("Casque d'essai", out)
        out = self.tools().get_dungeon_loot({"donjon": "crypte"})
        self.assertIn("Gardien muet", out)
        self.assertIn("pas dans les fichiers du client", out)
        lst = self.tools().get_dungeon_loot({})
        # liste de référence (knowledge/donjons.json) : donjons Forever et raids avec leur statut
        self.assertIn("Salle des Thanes (Hall of Thanes) — niveaux 13-18 [Forever]", lst)
        self.assertIn("Cœur du Magma (Molten Core) — raid 40 joueurs, niveau 60, pas encore ouvert", lst)
        self.assertNotIn("Test Dungeon", lst)

    def test_find_recipes_uses_character_rank(self):
        out = self.tools().find_recipes({})
        self.assertIn("Travail du cuir", out)
        self.assertIn("ton rang : 106", out)
        self.assertIn("≈110 · **Ceinture fabriquée**", out)
        self.assertIn("4 Cuir d'essai", out)

    def test_quest_info(self):
        out = self.tools().get_quest_info({"questId": 1})
        self.assertIn("Quête d'essai", out)
        self.assertIn("Tuer 5 loups", out)
        self.assertIn("pas encore été vue", self.tools().get_quest_info({"questId": 2}))

    def test_enrich_rewards(self):
        db = fixture_db()
        q = db["quests"]["list"][0]
        q["rewards"] = {"choices": [{"itemId": 1001, "name": "Casque d'essai"}], "items": []}
        n = self.tools(db).enrich_rewards(db)
        self.assertEqual(n, 1)
        self.assertEqual(q["rewards"]["choices"][0]["equipLoc"], "INVTYPE_HEAD")

    def test_missing_db_message(self):
        os.environ["FOREVER_GAMEDB"] = str(Path(self.tmp.name) / "absente.sqlite")
        try:
            t = self.tools()
            with self.assertRaises(server.ToolError) as ctx:
                t.find_items({"nom": "x"})
            self.assertIn("gamedata.build", str(ctx.exception))
            self.assertIn("construire", "\n".join(t.overview_upgrades(fixture_db())))
        finally:
            os.environ["FOREVER_GAMEDB"] = str(self.db_path)


if __name__ == "__main__":
    unittest.main()
