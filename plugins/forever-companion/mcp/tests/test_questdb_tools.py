"""get_quest_info, find_quests, find_npc sur une base synthétique avec tables QuestieDB inventées."""
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
import i18n as I  # noqa: E402
import server  # noqa: E402

FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"


def char(level=10, completed=(19,), log=()):
    db = json.loads((FIXTURES / "character.json").read_text(encoding="utf-8"))
    db = copy.deepcopy(db)
    db["progression"]["level"] = level
    db["questsCompleted"] = {"count": len(completed), "ids": list(completed)}
    db["quests"]["list"] = [{"id": qid, "title": f"Q{qid}", "level": 10, "complete": done, "objectives": []}
                            for qid, done in log]
    db["position"]["zone"] = "Val d'essai"
    return db


class QuestDBToolsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.tmp.name) / "gamedata" / "forever-frFR.sqlite"
        SY.make_db_with_questie(cls.db_path)
        cls.bare = Path(cls.tmp.name) / "bare" / "forever-frFR.sqlite"
        SY.make_db(cls.bare)
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
        data = db if db is not None else char()
        t._char = lambda args: ({}, data)
        return t

    def test_quest_sheet(self):
        out = self.tools().get_quest_info({"questId": 101})
        self.assertIn("**Chasse d'essai** (id 101) — niveau 10, requis 8, Val d'essai · pas faite", out)
        self.assertIn("Titre anglais : Trial Hunt", out)
        self.assertIn("Donneur : **Donneur d'essai** <Maître d'essai> — Val d'essai · `/way 10.0 20.0`", out)
        self.assertIn("À rendre à : **Trial Receiver**", out)
        self.assertIn("tuer **Loup d'essai** (niv. 7-8) — Val d'essai · `/way 41.0 41.0` (4 points)", out)
        self.assertIn("récupérer **Trial Fang** — sur Loup d'essai", out)
        self.assertIn("explorer : Scout the Trial Ridge", out)
        self.assertIn("Suite : *Suite d'essai* (102, pas faite)", out)
        self.assertIn("[Forever · QuestieDB]", out)
        self.assertIn("Conditions : Alliance", out)

    def test_quest_by_title_any_language_and_prereq(self):
        for title in ("suite d essai", "Trial Follow-up"):
            out = self.tools().get_quest_info({"titre": title})
            self.assertIn("Prérequis : *Chasse d'essai* (101, pas faite)", out)
        out = self.tools().get_quest_info({"questId": 104})
        self.assertIn("objet de l'inventaire", out)
        self.assertIn("objet **Coffre d'essai** — Val d'essai · `/way 80.0 10.0`", out)
        out = self.tools(char(log=[(101, True)])).get_quest_info({"questId": 101})
        self.assertIn("dans ton journal, à rendre", out)

    def test_quest_info_falls_back_to_client_cache(self):
        os.environ["FOREVER_GAMEDB"] = str(self.bare)
        try:
            out = self.tools().get_quest_info({"questId": 1})
            self.assertIn("Quête d'essai", out)
            self.assertIn("python3 -m gamedata.questie", out)
            with self.assertRaises(server.ToolError):
                self.tools().find_quests({})
        finally:
            os.environ["FOREVER_GAMEDB"] = str(self.db_path)

    def test_find_quests_filters(self):
        out = self.tools().find_quests({})
        self.assertIn("Chasse d'essai", out)          # disponible
        self.assertIn("Trial Letter", out)            # lancée par un objet
        self.assertNotIn("Suite d'essai", out)        # prérequis 101 pas fait
        self.assertNotIn("Horde Trial", out)          # autre faction
        self.assertNotIn("Old Trial", out)            # déjà faite
        self.assertNotIn("Trial Festival", out)       # saisonnière
        self.assertIn("Plus tard (1) : Trial Peak", out)
        out = self.tools(char(completed=(19, 101))).find_quests({"zone": "val d essai"})
        self.assertIn("Suite d'essai", out)
        self.assertIn("suite de *Chasse d'essai*", out)
        self.assertNotIn("**Chasse d'essai**", out)
        out = self.tools(char(log=[(101, False)])).find_quests({})
        self.assertNotIn("**Chasse d'essai**", out)   # déjà dans le journal
        with self.assertRaises(server.ToolError):
            self.tools().find_quests({"zone": "Zone qui n'existe pas"})

    def test_find_npc(self):
        out = self.tools().find_npc({"nom": "loup d essai"})
        self.assertIn("**Loup d'essai** (PNJ 503, niv. 7-8, hostile)", out)
        self.assertIn("Val d'essai · `/way 41.0 41.0` (4 points)", out)
        out = self.tools().find_npc({"nom": "Trial Giver"})
        self.assertIn("Donne : *Old Trial* (19, faite), *Chasse d'essai* (101, pas faite)", out)
        out = self.tools().find_npc({"nom": "coffre"})
        self.assertIn("**Coffre d'essai** (objet 601)", out)
        with self.assertRaises(server.ToolError):
            self.tools().find_npc({"nom": "personne"})

    def test_english_output(self):
        with I.using("en"):
            out = self.tools().get_quest_info({"questId": 101})
            self.assertIn("— level 10, requires 8", out)
            self.assertIn("Quest giver: **Trial Giver**", out)  # noms anglais de QuestieDB en anglais
            self.assertIn("- Title in your game: Chasse d'essai", out)
            self.assertIn("kill **Trial Wolf** (lvl 7-8)", out)
            self.assertIn("from Trial Wolf (lvl 7-8)", out)
            out = self.tools().find_quests({})
            self.assertIn("quests available** for", out)
            out = self.tools().find_npc({"nom": "Trial Wolf"})
            self.assertIn("- Where: Val d'essai · `/way 41.0 41.0`", out)


if __name__ == "__main__":
    unittest.main()
