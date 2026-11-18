"""Outil `quests` : résolution des noms de zone (FR, EN, « FR (EN) », sans accents) et XP des quêtes.

Base synthétique qui reproduit le piège du client frFR : plusieurs lignes AreaTable du même nom, dont
une seule (l'id de QuestieDB) porte les quêtes — « Bois de la Pénombre » 16148 sans quête contre
« Bois de la Pénombre (Duskwood) » 10. Si la vraie base du joueur est présente, elle est aussi balayée
(lecture seule).

    cd plugins/forever-companion/mcp && python3 -m unittest tests.test_quest_zone_xp
"""
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")
import re
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent / "gamedata" / "tests"))
sys.path.insert(0, str(HERE))

import formats as F  # noqa: E402
import gamedb as GDB  # noqa: E402
import server  # noqa: E402
import synthetic as SY  # noqa: E402
import xptable as X  # noqa: E402

# (id, nom du client frFR) : doublons réels de l'AreaTable de Forever
ZONES = [(10, "Bois de la Pénombre (Duskwood)"), (16119, "Bois de la Pénombre (Duskwood)"),
         (16148, "Bois de la Pénombre"), (11, "Les Paluns"), (16732, "Excavations : les Paluns"),
         (12, "Forêt d'Elwynn"), (16118, "Forêt d’Elwynn"), (16147, "Forêt d’Elwynn"),
         (148, "Sombrivage (Darkshore)"), (44, "Les Carmines"), (16113, "Les Carmines"),
         (95, "Canyons des Carmines"), (40, "Marche de l'Ouest (Westfall)")]
QUESTS_BY_ZONE = {10: 5, 11: 3, 12: 4, 148: 2, 44: 3, 40: 2}
PAIRS = [  # (FR, EN, id QuestieDB attendu)
    ("Bois de la Pénombre", "Duskwood", 10),
    ("bois de la penombre", "Bois de la Pénombre (Duskwood)", 10),
    ("Forêt d'Elwynn", "Elwynn Forest", 12),
    ("Foret d’Elwynn", "Elwynn", 12),
    ("Les Paluns", "Wetlands", 11),
    ("Paluns", "Les Paluns (Wetlands)", 11),
    ("Sombrivage", "Darkshore", 148),
    ("Les Carmines", "Redridge Mountains", 44),
    ("Carmines", "Redridge", 44),
    ("Marche de l'Ouest", "Westfall", 40),
]
REAL_DB = Path.home() / "WowForever" / "gamedata" / "forever-frFR.sqlite"


def add_zones(path):
    con = sqlite3.connect(str(path))
    con.executemany("INSERT OR REPLACE INTO zones (id, name, name_norm) VALUES (?, ?, ?)",
                    [(i, n, F.norm_key(n)) for i, n in ZONES])
    qid = 9000
    for zid, n in QUESTS_BY_ZONE.items():
        for k in range(n):
            qid += 1
            con.execute("INSERT INTO q_quests (id, name, name_loc, name_norm, req_level, level, zone_id, races, "
                        "classes, start_npcs) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, '[1]')",
                        (qid, f"Quest {qid}", f"Quête {qid}", f"quete {qid}", 1, 20 + k, zid))
    con.commit()
    con.close()


def char(level=25, quests=()):
    """Brannok, Nain Chasseur fictif."""
    return {"identity": {"name": "Brannok", "level": level, "race": "Nain", "raceFile": "Dwarf",
                         "classFile": "HUNTER", "faction": "Alliance"},
            "progression": {"level": level, "maxLevel": 60, "xp": 27088, "xpMax": 34000},
            "position": {"zone": "Les Paluns"},
            "quests": {"count": len(quests), "max": 20, "trivialRange": 6, "list": list(quests)}}


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.tmp.name) / "gamedata" / "forever-frFR.sqlite"
        SY.make_db_with_questie(cls.db_path)
        add_zones(cls.db_path)
        cls.old_env = os.environ.get("FOREVER_GAMEDB")
        os.environ["FOREVER_GAMEDB"] = str(cls.db_path)
        server.Tools._qzone_alias_cache.clear()

    @classmethod
    def tearDownClass(cls):
        if cls.old_env is None:
            os.environ.pop("FOREVER_GAMEDB", None)
        else:
            os.environ["FOREVER_GAMEDB"] = cls.old_env
        server.Tools._qzone_alias_cache.clear()
        cls.tmp.cleanup()

    def tools(self, db=None):
        t = server.Tools.__new__(server.Tools)
        t.store = SimpleNamespace(data_dir=Path(self.tmp.name) / "perso")
        t._gdb = None
        t._char = lambda args: ({}, db)
        return t


class ZoneResolutionTest(Base):
    def test_fr_equals_en(self):
        t = self.tools()
        gdb = t.questdb()
        for fr, en, zid in PAIRS:
            with self.subTest(fr=fr, en=en):
                self.assertEqual(t._zone_ids(gdb, fr), [zid])
                self.assertEqual(t._zone_ids(gdb, en), [zid])

    def test_prefers_questie_row_over_same_name_row_without_quests(self):
        t = self.tools()
        gdb = t.questdb()
        # 16148 « Bois de la Pénombre » correspond exactement mais n'a aucune quête : jamais choisie
        self.assertNotIn(16148, t._zone_ids(gdb, "Bois de la Pénombre"))
        self.assertEqual(t._zone_ids(gdb, "Inconnue du bataillon"), [])

    def test_available_quests_same_count_fr_en(self):
        t = self.tools(db=None)
        for fr, en, zid in PAIRS:
            with self.subTest(fr=fr):
                a = t.find_quests({"zone": fr, "limite": 50})
                b = t.find_quests({"zone": en, "limite": 50})
                n = re.search(r"\*\*(\d+) quêtes\*\*", a)
                self.assertIsNotNone(n, a)
                self.assertEqual(int(n.group(1)), QUESTS_BY_ZONE[zid])
                self.assertEqual(a, b)


@unittest.skipUnless(REAL_DB.exists(), "base locale du joueur absente")
class RealDatabaseZonesTest(unittest.TestCase):
    """Balayage sur la vraie base (lecture seule) : chaque nom FR et EN tombe sur les mêmes zones, non vides."""

    def test_real_pairs(self):
        t = server.Tools.__new__(server.Tools)
        gdb = GDB.GameDB(REAL_DB)
        pairs = [("Bois de la Pénombre", "Duskwood"), ("Forêt d'Elwynn", "Elwynn Forest"),
                 ("Les Paluns", "Wetlands"), ("Sombrivage", "Darkshore"), ("Les Carmines", "Redridge Mountains"),
                 ("Marche de l'Ouest", "Westfall"), ("Vallée de Strangleronce", "Stranglethorn Vale"),
                 ("Les Tarides", "The Barrens"), ("Loch Modan", "Loch Modan")]
        for fr, en in pairs:
            with self.subTest(fr=fr):
                ids = t._zone_ids(gdb, fr)
                self.assertTrue(ids)
                self.assertEqual(ids, t._zone_ids(gdb, en))
                self.assertTrue(gdb.q("SELECT 1 FROM q_quests WHERE zone_id = ? LIMIT 1", (ids[0],)))


class QuestXPTest(Base):
    def test_reduction_by_level_gap(self):
        base = X.quest_base_xp(20)
        self.assertEqual(X.quest_xp(20, 25), base)            # +5 : pleine
        self.assertEqual(X.quest_xp(20, 26), X._round_xp(base * 0.8))
        self.assertEqual(X.quest_xp(20, 27), X._round_xp(base * 0.6))
        self.assertEqual(X.quest_xp(20, 28), X._round_xp(base * 0.4))
        self.assertEqual(X.quest_xp(20, 29), X._round_xp(base * 0.2))
        self.assertEqual(X.quest_xp(20, 35), X._round_xp(base * 0.1))
        self.assertEqual(X.quest_xp(55, 60), 0)               # niveau maximum
        self.assertIsNone(X.quest_xp(None, 25))
        self.assertTrue(X.quest_base_xp(10) < X.quest_base_xp(30) < X.quest_base_xp(60))

    def test_level_after(self):
        self.assertEqual(X.level_after(25, 27088, 34000, 6912, X.CLASSIC_TABLE), (26, 0.0))
        lvl, frac = X.level_after(25, 27088, 34000, 6912 + 18200, X.CLASSIC_TABLE)
        self.assertEqual(lvl, 26)
        self.assertAlmostEqual(frac, 0.5)

    def test_real_reward_preferred_and_totals(self):
        quests = [
            {"id": 1, "title": "Ennemis du port", "level": 25, "complete": True, "category": "Les Paluns",
             "rewards": {"xp": 1800}},
            {"id": 2, "title": "Quête sans capture", "level": 25, "complete": True, "category": "Les Paluns"},
            {"id": 3, "title": "Vieille quête", "level": 14, "complete": False, "category": "Les Paluns"},
        ]
        db = char(25, quests)
        t = self.tools(db)
        self.assertEqual(t.journal_quest_xp(db, quests[0]), (1800, True))
        self.assertEqual(t.journal_quest_xp(db, quests[1]), (X.quest_base_xp(25), False))
        self.assertEqual(t.journal_xp_tag(db, quests[0]), " · 1 800 XP")
        self.assertIn("≈", t.journal_xp_tag(db, quests[1]))
        text = "\n".join(t.journal_xp_lines(db, quests))
        total = F.num(1800 + X.quest_base_xp(25))
        self.assertIn(f"ces 2 rendus ≈ **{total} XP**", text)
        self.assertIn("niveau atteint ≈ **25** (+92 %)", text)
        self.assertIn("XP du jeu pour 1, estimée pour 1 [Classic · estimation]", text)
        self.assertIn("**Grises, à abandonner**", text)
        self.assertIn("Vieille quête (14", text)
        self.assertNotIn("Ennemis du port (25", text.split("Grises")[1])

    def test_available_quests_show_xp(self):
        out = self.tools(char(20)).find_quests({"zone": "Duskwood", "limite": 50})
        self.assertRegex(out, r"\(9001, niv\. 20[^)]*\).* · ≈ " + re.escape(F.num(X.quest_base_xp(20))) + " XP")
        self.assertIn("**XP** : ces 5 quêtes ≈", out)


class QuestGivenElsewhereTest(unittest.TestCase):
    """QuestieDB range une quête par catégorie du journal (zone_id), pas par lieu du donneur : « Le tord-boyaux
    de MacKreel » (647) est classée aux Paluns mais Foggy MacKreel est dans les Hautes-terres Arathies. L'outil
    `quests` ne doit pas la proposer dans la liste des Paluns."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.tmp.name) / "gamedata" / "forever-frFR.sqlite"
        SY.make_db_with_questie(cls.db_path)
        add_zones(cls.db_path)
        con = sqlite3.connect(str(cls.db_path))
        con.execute("INSERT OR REPLACE INTO zones (id, name, name_norm) VALUES (45, 'Hautes-terres Arathies', "
                    "'hautes-terres arathies')")
        for qid, name, npc in ((9701, "Le tord-boyaux d'essai", 9801), (9702, "Course des Paluns", 9802),
                               (9703, "Donneur sans position", 9803)):
            con.execute("INSERT INTO q_quests (id, name, name_loc, name_norm, req_level, level, zone_id, races, "
                        "classes, start_npcs) VALUES (?, ?, ?, ?, 20, 24, 11, 0, 0, ?)",
                        (qid, name, name, F.norm_key(name), f"[{npc}]"))
        con.executemany("INSERT INTO q_spawns (kind, id, zone_id, x, y) VALUES ('npc', ?, ?, ?, ?)",
                        [(9801, 45, 43.2, 92.6), (9802, 11, 10.0, 60.0), (9802, 45, 50.0, 50.0)])
        con.commit()
        con.close()
        cls.old_env = os.environ.get("FOREVER_GAMEDB")
        os.environ["FOREVER_GAMEDB"] = str(cls.db_path)
        server.Tools._qzone_alias_cache.clear()

    @classmethod
    def tearDownClass(cls):
        if cls.old_env is None:
            os.environ.pop("FOREVER_GAMEDB", None)
        else:
            os.environ["FOREVER_GAMEDB"] = cls.old_env
        server.Tools._qzone_alias_cache.clear()
        cls.tmp.cleanup()

    def test_quest_given_in_other_zone_not_listed(self):
        t = Base.tools(self, char(25))
        out = t.find_quests({"zone": "Les Paluns", "limite": 50})
        listed = out.split("Classées dans cette zone")[0]
        self.assertNotIn("tord-boyaux d'essai", listed)
        self.assertIn("Course des Paluns", listed)        # un donneur sur deux dans la zone : gardée
        self.assertIn("Donneur sans position", listed)    # aucune position connue : rien ne la place ailleurs
        self.assertIn("_Classées dans cette zone par QuestieDB mais données ailleurs (1) : "
                      "Le tord-boyaux d'essai (Hautes-terres Arathies)._", out)
        avail, *_ = t.available_quests(t.questdb(), char(25), {"zone": "Wetlands"})
        self.assertNotIn(9701, [q["id"] for q in avail])

    @unittest.skipUnless(REAL_DB.exists(), "base locale du joueur absente")
    def test_real_mackreel(self):
        os.environ["FOREVER_GAMEDB"] = str(REAL_DB)
        server.Tools._qzone_alias_cache.clear()
        try:
            t = Base.tools(self, char(25))
            gdb = t.questdb()
            row = gdb.q("SELECT * FROM q_quests WHERE id = 647")
            if not row:
                self.skipTest("quête 647 absente de cette base")
            self.assertTrue(t.starts_elsewhere(gdb, row[0], t._zone_ids(gdb, "Les Paluns")))
        finally:
            os.environ["FOREVER_GAMEDB"] = str(self.db_path)
            server.Tools._qzone_alias_cache.clear()


if __name__ == "__main__":
    unittest.main()
