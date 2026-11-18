"""Import QuestieDB (gamedata/questie.py) sur des fichiers synthétiques au format de Questie."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

import synthetic as SY  # noqa: E402  (ajoute le dossier du plugin au chemin)
from gamedata import questie as Q  # noqa: E402


class QuestieImportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "gamedata" / "forever-frFR.sqlite"

    def tearDown(self):
        self.tmp.cleanup()

    def test_extract_table_positional_with_holes(self):
        text = 'X.data = [[return {\n[7] = {"A",nil,{1,2}},\n[9] = {"B"},\n}]]'
        t = Q.extract_table(text, "X.data")
        self.assertEqual(Q.f(t[7], 1), "A")
        self.assertIsNone(Q.f(t[7], 2))
        self.assertEqual(Q.f(t[7], 3), [1, 2])
        self.assertEqual(Q.f(t[9], 1), "B")
        with self.assertRaises(ValueError):
            Q.extract_table("rien", "X.data")

    def test_import_counts_and_fields(self):
        counts = SY.make_db_with_questie(self.db)
        self.assertEqual(counts["quests"], 7)
        self.assertEqual(counts["npcs"], 4)
        self.assertEqual(counts["quests_translated"], 2)
        self.assertEqual(counts["items"], 3)          # objet sans source gardé pour son nom anglais
        con = sqlite3.connect(str(self.db))
        self.assertEqual(con.execute("SELECT name, npc_drops, vendors, start_quest FROM q_items WHERE id = 2003")
                         .fetchone(), ("Plain Thing", None, None, None))
        self.assertEqual(con.execute("SELECT npc_drops FROM q_items WHERE id = 2001").fetchone()[0], "[503]")
        name, loc, norm, races, pre = con.execute(
            "SELECT name, name_loc, name_norm, races, pre_single FROM q_quests WHERE id = 101").fetchone()
        self.assertEqual((name, loc), ("Trial Hunt", "Chasse d'essai"))
        self.assertIn("chasse d essai", norm)
        self.assertEqual(races, SY.ALLIANCE_RACES)
        self.assertIsNone(pre)
        self.assertEqual(con.execute("SELECT pre_single FROM q_quests WHERE id = 102").fetchone()[0], "[101]")
        self.assertEqual(con.execute("SELECT sort_id, zone_id FROM q_quests WHERE id = 105").fetchone(), (22, None))
        self.assertEqual(con.execute("SELECT start_items, end_objects FROM q_quests WHERE id = 104").fetchone(),
                         ("[2002]", "[601]"))
        self.assertEqual(con.execute("SELECT subname, spawn_count FROM q_npcs WHERE id = 501").fetchone(),
                         ("Maître d'essai", 1))
        self.assertEqual(con.execute("SELECT count(*) FROM q_spawns WHERE kind='npc' AND id=503").fetchone()[0], 5)
        meta = dict(con.execute("SELECT key, value FROM meta WHERE key LIKE 'questie_%'"))
        self.assertEqual(meta["questie_commit"], "testcommit")
        self.assertIn("jamais redistribué", meta["questie_license"])
        # la base du client est intacte
        self.assertTrue(con.execute("SELECT count(*) FROM items").fetchone()[0] > 0)
        con.close()
        self.assertEqual(Q.current_commit(self.db), "testcommit")

    def test_run_is_idempotent_and_reimports(self):
        SY.make_db_with_questie(self.db)
        cache = self.db.parent / ".cache"
        self.assertIsNone(Q.run(self.db, cache, "frFR", offline=True, commit="testcommit"))
        counts = Q.run(self.db, cache, "frFR", force=True, offline=True, commit="testcommit")
        self.assertEqual(counts["quests"], 7)

    def test_offline_without_files_fails_and_english_skips_l10n(self):
        with self.assertRaises(FileNotFoundError):
            Q.fetch(Path(self.tmp.name) / "vide", "frFR", commit="absent", offline=True)
        SY.make_db(self.db, "enUS")
        SY.write_questie(self.db.parent / ".cache", "enUS")
        files = Q.fetch(self.db.parent / ".cache", "enUS", commit="testcommit", offline=True)
        self.assertNotIn("l10n_quests", files)
        counts = Q.import_into(self.db, files, commit="testcommit")
        self.assertEqual(counts["quests_translated"], 0)

    def test_thin_and_spawn_points(self):
        pts = Q.spawn_points({1: [[1, 2], [3, 4]], 2: [[-1, 5]]})
        self.assertEqual(pts, {1: [(1.0, 2.0), (3.0, 4.0)]})
        self.assertEqual(len(Q.thin([(i, i) for i in range(100)], 10)), 10)


if __name__ == "__main__":
    unittest.main()
