"""Tests des corrections issues de la deuxième passe d'évaluation (données synthétiques, perso fictif Brannok)."""
import copy
import json
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")  # jamais de réseau dans les tests
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1]))

import dungeons as DG  # noqa: E402
import formats as F  # noqa: E402
import gear as G  # noqa: E402
import i18n as I  # noqa: E402
import intent_tools as IT  # noqa: E402
import knowledge as K  # noqa: E402
import server  # noqa: E402
import xptable as X  # noqa: E402
from gamedata.tests import synthetic as SY  # noqa: E402

FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"


def hunter(**extra):
    db = {"identity": {"name": "Brannok", "classFile": "HUNTER", "level": 25},
          "progression": {"level": 25, "xp": 27088, "xpMax": 34000, "xpRested": 500},
          "equipment": {"slots": {"Finger1Slot": {"name": "Anneau de quartz", "stats": {"ITEM_MOD_INTELLECT_SHORT": 3}}}},
          "stats": {"ranged": {"dps": 40.0}, "melee": {"dps": 20.0}}}
    db.update(extra)
    return db


def ring(**stats):
    return {"name": "Anneau test", "classId": 4, "subclassId": 0, "equipLoc": "INVTYPE_FINGER", "requiredLevel": 20,
            "stats": {f"ITEM_MOD_{k}_SHORT": v for k, v in stats.items()}}


def head(**stats):
    return {"name": "Coiffe test", "classId": 4, "subclassId": 1, "equipLoc": "INVTYPE_HEAD", "requiredLevel": 20,
            "stats": {f"ITEM_MOD_{k}_SHORT": v for k, v in stats.items()}}


CAREFUL = {"nodes": [{"name": "Visée minutieuse", "rank": 2, "maxRank": 5, "spellId": 1}]}


class Normalisation(unittest.TestCase):
    def test_ligatures_and_apostrophes(self):
        self.assertEqual(F.norm_key("Cœur de raptor"), "coeur de raptor")
        self.assertEqual(F.norm_key("Anneau de quartz d’intelligence"), F.norm_key("Anneau de quartz d'intelligence"))

    def test_search_terms_stem_and_phrases(self):
        terms = K._aterms("Les champs de bataille et les bateaux")
        self.assertIn("bg", terms)
        self.assertIn(K._stem("bateau"), terms)
        self.assertNotIn("les", terms)
        self.assertEqual(K._stem("changer"), K._stem("changement"))


class KnowledgeSections(unittest.TestCase):
    def test_short_title(self):
        self.assertEqual(IT.short_title("**Rulesets** — PvE, PvP"), "Rulesets")

    def test_clip_never_inside_a_table(self):
        body = "\n".join(["intro"] * 5 + ["| a | b |", "|---|---|"] + [f"| {i} | x |" for i in range(400)] + ["fin"])
        out = IT.clip_section(body, limit=200, hard=100000)
        self.assertTrue(out.splitlines()[-1].startswith("| ") or "fin" in out)
        self.assertEqual(out.count("|---|---|"), 1)
        small = IT.clip_section("court")
        self.assertEqual(small, "court")

    def test_clip_says_what_is_left(self):
        body = "\n".join(f"ligne {i} " + "x" * 80 for i in range(200))
        out = IT.clip_section(body, limit=500, hard=1000)
        self.assertIn("section coupée", out)


class DungeonLanguage(unittest.TestCase):
    def test_loc_follows_language(self):
        d = {"fr": "Les Paluns", "en": "Wetlands", "zone": "Les Paluns", "zone_en": "Wetlands"}
        with I.using("en"):
            self.assertEqual(DG.loc(d, "name"), "Wetlands")
            self.assertEqual(DG.loc(d, "zone"), "Wetlands")
        with I.using("fr"):
            self.assertEqual(DG.loc(d, "zone"), "Les Paluns")
        self.assertEqual(DG.loc({"zone": "Rives Claires"}, "zone"), "Rives Claires")


class XpToLevel(unittest.TestCase):
    def test_classic_table(self):
        total, reached = X.xp_to_target(25, 27088, 34000, 40, X.CLASSIC_TABLE)
        self.assertEqual(reached, 40)
        self.assertEqual(total, 6912 + sum(X.CLASSIC_TABLE[lv] for lv in range(26, 40)))
        self.assertEqual(X.xp_to_target(25, 0, None, 25, X.CLASSIC_TABLE), (0, 25))

    def test_gap_in_table(self):
        total, reached = X.xp_to_target(25, 0, 34000, 40, {25: 34000, 26: 1})
        self.assertIsNone(total)
        self.assertEqual(reached, 27)

    def test_overview_progress_lines(self):
        t = server.Tools.__new__(server.Tools)
        t.gamedb = lambda required=True: None
        lines = t._xp_target_lines(hunter(), 27)
        self.assertIn("[Classic · probable]", lines[0])
        self.assertIn(F.num(6912 + 36400), lines[0])
        self.assertTrue(any("500" in ln for ln in lines))
        self.assertIn("déjà atteint", t._xp_target_lines(hunter(), 20)[0])

    def test_db_table_preferred(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p = Path(tmp.name) / "g.sqlite"
        SY.make_db(p)
        gdb = SimpleNamespace(con=sqlite3.connect(str(p)))
        table = X.table_from_db(gdb)
        self.assertEqual(table[25], 25000)  # table LevelExperience synthétique (1000 × niveau)
        self.assertIsNone(X.table_from_db(SimpleNamespace(con=sqlite3.connect(":memory:"))))


class GearRole(unittest.TestCase):
    def test_healer_item_not_for_hunter(self):
        ev = G.evaluate(hunter(), head(STAMINA=11, HEALING=16, SPELL_POWER=5))
        self.assertEqual(ev["code"], "not_for_you")
        self.assertIn("ta classe", ev["reason"])

    def test_agility_item_fills_empty_slot(self):
        ev = G.evaluate(hunter(), head(AGILITY=7, STAMINA=8))
        self.assertEqual(ev["code"], "empty_slot")

    def test_resistance_only_is_not_an_empty_slot_pick(self):
        ev = G.evaluate(hunter(), head(SHADOW_RESISTANCE=5))
        self.assertNotEqual(ev["code"], "empty_slot")

    def test_intellect_needs_careful_aim(self):
        self.assertEqual(G.off_role(hunter(), {"INTELLECT": 5}), ["INTELLECT"])
        self.assertEqual(G.off_role(hunter(talents=CAREFUL), {"INTELLECT": 5}), [])
        self.assertEqual(G.careful_aim(hunter(talents=CAREFUL)), 2)
        self.assertEqual(G.careful_aim(hunter()), 0)

    def test_hybrids_never_off_role(self):
        db = hunter()
        db["identity"]["classFile"] = "DRUID"
        self.assertEqual(G.off_role(db, {"INTELLECT": 5, "SPIRIT": 5}), [])

    def test_mage_ignores_agility(self):
        db = hunter()
        db["identity"]["classFile"] = "MAGE"
        self.assertEqual(G.off_role(db, {"AGILITY": 5}), ["AGILITY"])

    def _verdict(self, db, cand_stats, cur_stats):
        def delta(k):
            return float(cand_stats.get(k, 0)) - float(cur_stats.get(k, 0))
        return server.Tools._tie_verdict(db, "HUNTER", delta, cand_stats, None)

    def test_tie_verdict_off_role(self):
        v = self._verdict(hunter(), {"SPELL_POWER": 5, "INTELLECT": 2}, {"INTELLECT": 3})
        self.assertTrue(v.startswith("**") and v.endswith("**"))
        self.assertIn("garde l'objet équipé", v)

    def test_tie_verdict_no_fake_tiebreak(self):
        v = self._verdict(hunter(), {"FIRE_RESISTANCE": 5}, {})
        self.assertNotIn("endurance", v.lower())
        self.assertIn("aucune différence chiffrable", v)

    def test_tie_verdict_stamina_and_careful_aim(self):
        v = self._verdict(hunter(), {"STAMINA": 4}, {})
        self.assertIn("nouvel objet", v)
        v = self._verdict(hunter(talents=CAREFUL), {"INTELLECT": 2}, {"INTELLECT": 3})
        self.assertIn("Visée minutieuse 2/5", v)
        self.assertIn("objet équipé", v)
        # surtout de la puissance des sorts : hors rôle même avec le talent
        v = self._verdict(hunter(talents=CAREFUL), {"INTELLECT": 2, "SPELL_POWER": 5}, {"INTELLECT": 3})
        self.assertIn("sans effet pour ta classe", v)


class QuestieSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.tmp.name) / "gamedata" / "forever-frFR.sqlite"
        SY.make_db_with_questie(cls.db_path)
        con = sqlite3.connect(str(cls.db_path))
        cols = [r[1] for r in con.execute("PRAGMA table_info(q_quests)")]
        row = list(con.execute("SELECT * FROM q_quests WHERE id = 101").fetchone())
        row[cols.index("id")] = 107  # homonyme de « Trial Hunt »
        con.execute(f"INSERT INTO q_quests VALUES ({','.join('?' * len(cols))})", row)
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

    def tools(self, log=()):
        db = copy.deepcopy(json.loads((FIXTURES / "character.json").read_text(encoding="utf-8")))
        db["progression"]["level"] = 10
        db["questsCompleted"] = {"count": 1, "ids": [19]}
        db["quests"]["list"] = [{"id": q, "title": "Chasse d'essai", "level": 10, "complete": False,
                                 "objectives": []} for q in log]
        t = server.Tools.__new__(server.Tools)
        t.store = SimpleNamespace(data_dir=Path(self.tmp.name) / "perso")
        t._gdb = None
        t._char = lambda args: ({}, db)
        t._db_char = lambda args: ({}, db)
        return t

    def test_item_source_from_npc_drops(self):
        t = self.tools()
        src = t.item_source(t.gamedb(), 2001, None)
        self.assertIn("Loup d'essai", src)
        self.assertIn("7-8", src)

    def test_homonym_journal_quest_first(self):
        t = self.tools(log=(107,))
        out = t.get_quest_info({"titre": "Chasse d'essai"})
        self.assertIn("(id 107)", out)
        self.assertIn("Autres quêtes du même nom : 101", out)
        self.assertNotIn("(id 101)", out)
        self.assertNotIn("questId:107", out)


if __name__ == "__main__":
    unittest.main()
