"""Quêtes propres à Forever : mémoire des quêtes (fusion, synchro), fiches sans QuestieDB, Wowhead simulé.

Aucun accès réseau : le client Wowhead reçoit une fonction `fetch` factice.
"""
import copy
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1] / "gamedata" / "tests"))

import synthetic as SY  # noqa: E402
import luasv  # noqa: E402
import questmemory as QM  # noqa: E402
import server  # noqa: E402
import sync  # noqa: E402
import wowhead as WH  # noqa: E402

FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"
ACC = "123456789#1"
NPC_777 = {"name": "Pêcheur égaré", "tooltip": "",
           "map": {"zone": 1, "coords": {"0": [[20, 30], [21, 30], [60, 60]]}}}
QUEST_95000 = {"name": "Quête lointaine",
               "tooltip": "<table><tr><td><b>Quête lointaine</b></td></tr><tr><td>Level 28</td></tr></table>"
                          "<table></table>Tuer 3 vases.<br><br>Requirements: rien"}


def fixture_memory():
    return luasv.load_file(FIXTURES / "account_SavedVariables_ForeverScribe.lua")["ForeverScribeDB"]["questMemory"]


class MergeTest(unittest.TestCase):
    def test_fixture_shape(self):
        m = QM.merge([fixture_memory()])
        self.assertEqual(set(m["quests"]), {"289", "90001", "90002", "90003", "90004", "90005"})
        self.assertEqual(QM.title_of(m["npcs"]["90100"], "frFR"), "Garde Brumebarbe")
        self.assertEqual(len(m["quests"]["289"]["objectives"]["1"]["points"]), 5)
        self.assertTrue(m["quests"]["289"]["turnedIn"])

    def test_turnin_beats_listed_and_latest_position_wins(self):
        a = {"quests": {7: {"ends": [{"kind": "npc", "id": 1, "via": "listed", "mapId": 1437, "x": 10, "y": 10,
                                      "at": 100}]}}}
        b = {"quests": {"7": {"ends": {1: {"kind": "npc", "id": 1, "via": "turnin", "mapId": 1437, "x": 50,
                                           "y": 50, "at": 50}}}}}
        c = {"quests": [None] * 6 + [{"ends": [{"kind": "npc", "id": 1, "via": "accept", "mapId": 1437,
                                                "x": 30, "y": 30, "at": 200}]}]}   # liste Lua : indice 7
        m = QM.merge([a, b, c])
        end = m["quests"]["7"]["ends"]
        self.assertEqual(len(end), 1)
        self.assertEqual(end[0]["via"], "turnin")
        self.assertEqual((end[0]["x"], end[0]["at"]), (30, 200))

    def test_points_deduplicated_across_accounts(self):
        p = {"mapId": 1437, "x": 40.0, "y": 40.0}
        a = {"npcs": {5: {"names": {"frFR": "Bob"}, "points": [p]}}}
        b = {"npcs": {5: {"names": {"enUS": "Bob"}, "points": [{"mapId": 1437, "x": 40.5, "y": 40.5},
                                                              {"mapId": 1437, "x": 70, "y": 70}]}}}
        m = QM.merge([a, b])
        self.assertEqual(len(m["npcs"]["5"]["points"]), 2)
        self.assertEqual(set(m["npcs"]["5"]["names"]), {"frFR", "enUS"})
        self.assertTrue(QM.is_empty(QM.merge([None, {}])))


class WowheadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Path(self.tmp.name) / ".cache" / "wowhead"
        self.calls = []
        WH._down_until = 0.0
        self.old_interval, WH.MIN_INTERVAL = WH.MIN_INTERVAL, 0.0
        self.old_env = os.environ.pop("FOREVER_WEB_LOOKUP", None)

    def tearDown(self):
        WH.MIN_INTERVAL = self.old_interval
        if self.old_env is not None:
            os.environ["FOREVER_WEB_LOOKUP"] = self.old_env
        self.tmp.cleanup()

    def fetch(self, url):
        self.calls.append(url)
        if "/npc/777?" in url:
            return NPC_777
        if "/npc/666?" in url:
            raise OSError("timeout")
        return None

    def test_parsing(self):
        self.assertEqual(WH.position(NPC_777), (1, 21.0, 30.0, 3))
        self.assertIsNone(WH.position({"name": "x"}))
        s = WH.quest_summary(QUEST_95000)
        self.assertEqual((s["name"], s["level"], s["objective"]), ("Quête lointaine", 28, "Tuer 3 vases."))

    def test_cache_budget_missing_and_backoff(self):
        wh = WH.Wowhead(self.cache, "frFR", fetch=self.fetch)
        self.assertEqual(wh.get("npc", 777)["name"], "Pêcheur égaré")
        self.assertIn("dataEnv=16&locale=2", self.calls[0])
        self.assertIsNone(wh.get("npc", 1))                       # absent : noté dans le cache
        self.assertTrue((self.cache / "npc-1-frFR.json").is_file())
        wh2 = WH.Wowhead(self.cache, "frFR", fetch=self.fetch)
        self.assertEqual(wh2.get("npc", 777)["name"], "Pêcheur égaré")
        self.assertIsNone(wh2.get("npc", 1))
        self.assertEqual(len(self.calls), 2)                     # tout vient du cache
        for i in range(10, 20):
            wh2.get("npc", i)
        self.assertEqual(wh2.used, WH.BUDGET)                      # budget par appel d'outil
        self.assertIsNone(wh2.get("quest", "abc"))
        self.assertIsNone(wh2.get("item", 5))                     # type refusé
        wh3 = WH.Wowhead(self.cache, "frFR", fetch=self.fetch)
        self.assertIsNone(wh3.get("npc", 666))                    # erreur réseau…
        self.assertIsNone(wh3.get("npc", 30))                     # … puis plus d'essai
        self.assertEqual(wh3.used, 1)
        self.assertFalse((self.cache / "npc-666-frFR.json").exists())

    def test_disabled(self):
        self.assertIsNone(WH.Wowhead(self.cache, "frFR", enabled=False, fetch=self.fetch).get("npc", 777))
        os.environ["FOREVER_WEB_LOOKUP"] = "0"
        try:
            self.assertIsNone(WH.Wowhead(self.cache, "frFR", fetch=self.fetch).get("npc", 777))
        finally:
            os.environ.pop("FOREVER_WEB_LOOKUP")
        self.assertEqual(self.calls, [])


class SyncMemoryTest(unittest.TestCase):
    def test_sync_writes_memory_once(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            wow = tmp / "World of Warcraft" / "_forever_"
            acc = wow / "WTF" / "Account" / ACC / "SavedVariables"
            acc.mkdir(parents=True)
            shutil.copy(FIXTURES / "account_SavedVariables_ForeverScribe.lua", acc / sync.SV_NAME)
            data = tmp / "perso"
            data.mkdir()
            (data / sync.CONFIG_NAME).write_text(json.dumps({"wowPaths": [str(wow.parent)],
                                                             "accounts": {ACC: "Alex"}}), encoding="utf-8")
            sync.sync(data)
            path = QM.path_for(data, "Alex")
            mem = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(mem["quests"]["90001"]["starts"][0]["id"], 90100)
            before = path.stat().st_mtime_ns
            time.sleep(0.01)
            sync.sync(data)
            self.assertEqual(path.stat().st_mtime_ns, before)       # contenu inchangé : pas réécrit
        finally:
            shutil.rmtree(tmp)


class ForeverSheetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.db_path = root / "gamedata" / "forever-frFR.sqlite"
        SY.make_db(cls.db_path)                                    # sans QuestieDB : quêtes de Forever
        mem = QM.merge([fixture_memory()])
        mem["quests"]["90006"] = {"titles": {"frFR": "Le pêcheur perdu"}, "ends": [], "offeredBy": [],
                                  "objectives": {}, "starts": [{"kind": "npc", "id": 777, "via": "accept"}]}
        cls.data = root / "perso"
        (cls.data / "Alex").mkdir(parents=True)
        QM.path_for(cls.data, "Alex").write_text(json.dumps(mem), encoding="utf-8")
        cls.char = json.loads((FIXTURES / "character.json").read_text(encoding="utf-8"))
        cls.old = {k: os.environ.get(k) for k in ("FOREVER_GAMEDB", "FOREVER_WEB_LOOKUP")}
        os.environ["FOREVER_GAMEDB"] = str(cls.db_path)
        os.environ.pop("FOREVER_WEB_LOOKUP", None)
        cls.old_interval, WH.MIN_INTERVAL = WH.MIN_INTERVAL, 0.0

    @classmethod
    def tearDownClass(cls):
        for k, v in cls.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        WH.MIN_INTERVAL = cls.old_interval
        cls.tmp.cleanup()

    def setUp(self):
        self.calls = []
        WH._down_until = 0.0

    def fetch(self, url):
        self.calls.append(url)
        if "/npc/777?" in url:
            return NPC_777
        if "/quest/95000?" in url:
            return QUEST_95000
        return None

    def tools(self, config=None):
        t = server.Tools.__new__(server.Tools)
        t.store = SimpleNamespace(data_dir=self.data, config=config or {})
        t._gdb = None
        t._char = lambda args: ({"user": "Alex"}, copy.deepcopy(self.char))
        t._wh_fetch = self.fetch
        t._call_stamp = object()
        return t

    def test_observed_giver_and_turnin(self):
        out = self.tools().get_quest_info({"questId": 90001})
        self.assertIn("Donneur : **Garde Brumebarbe** — Les Paluns · `/way 37.0 20.0` [Forever · observé en jeu]", out)
        self.assertIn("À rendre à : **Chef de port Halvard** — Les Paluns · `/way 10.0 60.0` "
                      "[Forever · observé en jeu] (probable)", out)
        out = self.tools().get_quest_info({"questId": 289})
        self.assertIn("À rendre à : **Chef de port Halvard**", out)
        self.assertNotIn("(probable)", out)                       # receveur certain : le probable disparaît
        self.assertIn("objectif 1 avancé en jeu ici : Les Paluns · `/way 50.0 40.0` (5 points)", out)
        out = self.tools().get_quest_info({"questId": 90002})
        self.assertIn("Donneur : objet **Coffre englouti**", out)
        out = self.tools().get_quest_info({"questId": 90003})
        self.assertIn("clic droit dessus pour lancer la quête", out)
        out = self.tools().get_quest_info({"titre": "rumeurs du port"})
        self.assertIn("Proposée par : **Garde Brumebarbe**", out)
        self.assertEqual(self.calls, [])                           # tout est local : aucune requête

    def test_wowhead_fills_gaps_then_cache(self):
        out = self.tools().get_quest_info({"questId": 90006})
        self.assertIn("Donneur : **Pêcheur égaré** — Val d'essai · `/way 21.0 30.0` (3 points) [Wowhead Forever]",
                      out)
        out = self.tools().get_quest_info({"questId": 95000})
        self.assertIn("**Quête lointaine** (id 95000) — niveau 28", out)
        self.assertIn("Objectif : Tuer 3 vases.", out)
        n = len(self.calls)
        self.tools().get_quest_info({"questId": 90006})
        self.assertEqual(len(self.calls), n)                       # relu depuis le cache

    def test_web_lookup_off(self):
        shutil.rmtree(self.db_path.parent / ".cache", ignore_errors=True)
        t = self.tools({"web_lookup": False})
        try:
            out = t.get_quest_info({"questId": 95000})
        except server.ToolError:
            out = ""
        self.assertNotIn("Quête lointaine", out)
        self.assertEqual(self.calls, [])

    def test_npc_and_search(self):
        out = self.tools().find_npc({"nom": "Halvard"})
        self.assertIn("**Chef de port Halvard** (PNJ 90101)", out)
        self.assertIn("Reçoit : *Purger la contrée* (289", out)
        self.assertIn("Donne : *Patrouille des quais* (90005", out)
        self.assertNotIn("QuestieDB]", out.split("\n")[0])


if __name__ == "__main__":
    unittest.main()
