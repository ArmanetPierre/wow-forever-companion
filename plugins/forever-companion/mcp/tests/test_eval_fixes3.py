"""Tests des corrections issues de la troisième passe d'évaluation (données synthétiques, perso fictif Brannok)."""
import copy
import json
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")  # jamais de réseau dans les tests
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1] / "gamedata" / "tests"))

import synthetic as SY  # noqa: E402
import gamedb as GDB  # noqa: E402
import gamedb_tools as GT  # noqa: E402
import gear as G  # noqa: E402
import i18n as I  # noqa: E402
import knowledge as K  # noqa: E402
import server  # noqa: E402

FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"


def row(**kw):
    """Ligne façon sqlite3.Row (keys() + accès par clé)."""
    class R(dict):
        def keys(self):  # noqa: D401
            return list(super().keys())
    return R(kw)


class EffectiveRequiredLevel(unittest.TestCase):
    def test_added_item_without_req_is_estimated_from_ilvl(self):
        self.assertEqual(GDB.effective_req(row(req_level=1, ilvl=33, origin="ajoute")), (28, True))
        self.assertEqual(GDB.effective_req(row(req_level=0, ilvl=33, origin="ajoute")), (28, True))

    def test_client_items_keep_their_level(self):
        self.assertEqual(GDB.effective_req(row(req_level=1, ilvl=33, origin="client")), (1, False))
        self.assertEqual(GDB.effective_req(row(req_level=22, ilvl=27, origin="ajoute")), (22, False))
        self.assertEqual(GDB.effective_req(row(req_level=1, ilvl=5, origin="ajoute")), (1, False))

    def test_sql_and_python_agree(self):
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE items (req_level INT, ilvl INT, origin TEXT)")
        cases = [(1, 33, "ajoute"), (1, 33, "client"), (22, 27, "ajoute"), (None, 40, "ajoute"), (0, 8, "ajoute")]
        con.executemany("INSERT INTO items VALUES (?,?,?)", cases)
        sql = [r[0] for r in con.execute(f"SELECT {GDB.EFFECTIVE_REQ_SQL} FROM items")]
        py = [GDB.effective_req(row(req_level=a, ilvl=b, origin=c))[0] for a, b, c in cases]
        self.assertEqual(sql, py)

    def test_db_at_level_is_a_shallow_copy(self):
        db = {"identity": {"name": "Brannok", "level": 25}, "progression": {"level": 25, "xp": 3}}
        later = GT.db_at_level(db, 30)
        self.assertEqual((later["identity"]["level"], later["progression"]["level"]), (30, 30))
        self.assertEqual(later["progression"]["xp"], 3)
        self.assertEqual(db["progression"]["level"], 25)


class AlreadyWorn(unittest.TestCase):
    def hunter(self, slots):
        return {"identity": {"name": "Brannok", "classFile": "HUNTER", "level": 25},
                "progression": {"level": 25}, "equipment": {"slots": slots}, "stats": {}}

    def test_same_item_already_worn(self):
        item = {"itemId": 4242, "name": "Coiffe test", "classId": 4, "subclassId": 1, "equipLoc": "INVTYPE_HEAD",
                "requiredLevel": 20, "stats": {"ITEM_MOD_AGILITY_SHORT": 5}}
        db = self.hunter({"HeadSlot": dict(item)})
        ev = G.evaluate(db, item)
        self.assertEqual(ev["code"], "already_worn")
        self.assertNotIn("second_copy", ev)

    def test_second_copy_for_the_other_slot_of_a_pair(self):
        item = {"itemId": 4243, "name": "Anneau test", "classId": 4, "subclassId": 0, "equipLoc": "INVTYPE_FINGER",
                "requiredLevel": 20, "stats": {"ITEM_MOD_AGILITY_SHORT": 5}}
        db = self.hunter({"Finger0Slot": dict(item)})
        ev = G.evaluate(db, item)
        self.assertNotEqual(ev["code"], "already_worn")
        self.assertTrue(ev.get("second_copy"))
        self.assertIn("2e exemplaire", ev["verdict"])


class QuestBugById(unittest.TestCase):
    def test_only_the_listed_step_inherits_the_bug(self):
        self.assertIsNotNone(K.quest_bug("La Confrérie défias", quest_id=155))
        self.assertIsNone(K.quest_bug("La Confrérie défias", quest_id=141))
        self.assertIsNone(K.quest_bug("La Confrérie défias", quest_id=166))

    def test_title_alone_still_warns(self):
        self.assertIsNotNone(K.quest_bug("La Confrérie défias"))
        self.assertIsNotNone(K.quest_bug("Hors du fort", quest_id=898))

    def test_label_has_no_id(self):
        for b in K.known_quest_bugs():
            self.assertNotIn("(id ", b.get("label", "") or "")


class KindSlotLabel(unittest.TestCase):
    def test_slot_not_repeated_when_in_the_kind(self):
        I.set_lang("fr")
        r = row(class_id=2, subclass_id=4, inventory_type=13)   # masse à une main
        label = GDB.kind_slot(r, " ")
        self.assertEqual(label.lower().count("une main"), 1, label)
        title_bits = GDB.kind_slot(r)
        self.assertNotIn("·", title_bits)

    def test_armor_keeps_its_slot(self):
        I.set_lang("fr")
        r = row(class_id=4, subclass_id=3, inventory_type=9)    # maille, poignets
        self.assertEqual(GDB.kind_slot(r, " "), "maille poignets")


class QuestieBacked(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.tmp.name) / "gamedata" / "forever-frFR.sqlite"
        SY.make_db_with_questie(cls.db_path)
        con = sqlite3.connect(cls.db_path)
        cols = [r[1] for r in con.execute("PRAGMA table_info(items)")]
        base = {"id": 2001, "name": "Croc d'essai", "name_norm": "croc d'essai", "quality": 1, "ilvl": 1,
                "req_level": 0}
        keep = {k: v for k, v in base.items() if k in cols}
        con.execute(f"INSERT OR REPLACE INTO items ({','.join(keep)}) VALUES ({','.join('?' * len(keep))})",
                    tuple(keep.values()))
        con.commit()
        con.close()
        cls.old_env = os.environ.get("FOREVER_GAMEDB")
        os.environ["FOREVER_GAMEDB"] = str(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        if cls.old_env is None:
            os.environ.pop("FOREVER_GAMEDB", None)
        else:
            os.environ["FOREVER_GAMEDB"] = cls.old_env
        cls.tmp.cleanup()

    def setUp(self):
        I.set_lang("fr")

    def char(self, log=()):
        db = copy.deepcopy(json.loads((FIXTURES / "character.json").read_text(encoding="utf-8")))
        db["progression"]["level"] = 10
        db["questsCompleted"] = {"count": 1, "ids": [19]}
        db["quests"]["list"] = [{"id": qid, "title": f"Q{qid}", "level": lvl, "complete": False, "objectives": []}
                                for qid, lvl in log]
        db["position"]["zone"] = "Val d'essai"
        return db

    def tools(self, db=None):
        t = server.Tools.__new__(server.Tools)
        t.store = SimpleNamespace(data_dir=Path(self.tmp.name) / "perso")
        t._gdb = None
        data = db if db is not None else self.char()
        t._char = lambda args: ({}, data)
        return t

    def test_item_by_english_name(self):
        gdb = GDB.GameDB(self.db_path)
        rows = gdb.items_by_name("Trial Fang")
        self.assertEqual([r["id"] for r in rows], [2001])
        self.assertEqual(gdb.items_by_name("Nothing at all"), [])

    def test_quest_level_from_the_log_wins(self):
        t = self.tools(self.char(log=[(101, 14)]))
        out = t.get_quest_info({"questId": 101})
        self.assertIn("niveau 14", out)
        self.assertIn("dans QuestieDB", out)
        self.assertNotIn("(niv. 14)", out)   # plus de 2e niveau en pied

    def test_available_count_is_the_filtered_total(self):
        t = self.tools()
        t.find_quests({"limite": 1})
        n, _later = t.last_available
        t2 = self.tools()
        t2.find_quests({"limite": 50})
        self.assertEqual(n, t2.last_available[0])

    def test_technical_npcs_are_dropped(self):
        t = self.tools()
        gdb = t.questdb()
        rows = [{"id": 999001, "name": "World Paladin Trainer"}, {"id": 999002, "name": "[PH] Truc"},
                {"id": 999003, "name": "ZZOLD GUARD"}, {"id": 503, "name": "Trial Wolf"},
                {"id": 999004, "name": "Sans position"}]
        kept = [r["name"] for r in t.clean_npcs(gdb, rows)]
        self.assertEqual(kept, ["Trial Wolf", "Sans position"])

    def test_raid_access_chain_for_the_characters_faction(self):
        t = self.tools()
        db = self.char()
        db["identity"]["faction"] = "Alliance"
        acc = {"Alliance": {"debut": 101, "fin": 102, "etapes": 2}, "Horde": {"debut": 102, "fin": 101, "etapes": 9}}
        lines = t.access_chain_lines(t.questdb(), db, acc)
        text = "\n".join(lines)
        self.assertIn("Alliance : 2 étapes", text)
        self.assertNotIn("Horde", text)
        self.assertIn("Suite d'essai", text)
        self.assertEqual(t.access_chain_lines(t.questdb(), db, {"Alliance": {"debut": 1, "fin": 2}}), [])

    def test_npc_found_by_its_subtitle(self):
        out = self.tools().find_npc({"nom": "maître d'essai"})
        self.assertIn("Donneur d'essai", out)


if __name__ == "__main__":
    unittest.main()
