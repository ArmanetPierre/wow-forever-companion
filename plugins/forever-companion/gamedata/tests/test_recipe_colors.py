"""Couleurs Classic des recettes (gamedata/recipe_colors.py) : import d'un CSV inventé, écriture de la
table recipe_colors, repli sans réseau. Aucune donnée du jeu : lignes et valeurs inventées.

    python3 -m unittest discover -s plugins/forever-companion/gamedata/tests
"""
import sqlite3
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

import synthetic as SY  # noqa: E402  (ajoute le dossier du plugin au chemin)
from gamedata import build, recipe_colors as RC  # noqa: E402

# Ordre des colonnes de l'export wago.tools (High avant Low), valeurs inventées.
CSV = """ID,SkillLine,Spell,MinSkillLineRank,ClassMask,SupercedesSpell,AcquireMethod,TrivialSkillLineRankHigh,TrivialSkillLineRankLow,Flags,NumSkillUps
1,165,5001,1,0,0,1,60,25,0,1
2,202,9101,1,0,0,0,140,100,0,1
3,202,9102,1,0,0,0,0,0,0,1
4,186,9103,1,0,0,1,0,0,0,1
5,6,9104,1,128,0,1,0,0,0,1
6,40,9105,1,0,0,0,175,125,0,1
7,202,9101,1,0,0,0,999,999,0,1
"""


class TestParse(unittest.TestCase):
    def test_parse_keeps_profession_rows(self):
        c = RC.parse_csv(CSV)
        self.assertEqual(c[5001], (25, 60, True))
        self.assertEqual(c[9101], (100, 140, False))   # première ligne gardée
        self.assertEqual(c[9103], (0, 0, True))        # apprise d'office, sans couleurs
        self.assertNotIn(9102, c)                      # ni couleurs ni apprise d'office
        self.assertNotIn(9104, c)                      # pas un métier (sort de classe)
        self.assertNotIn(9105, c)                      # métier hors liste
        self.assertEqual(len(c), 3)

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            RC.parse_csv("ID,Spell\n1,2\n")

    def test_bom_and_path(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.csv"
            p.write_text("﻿" + CSV, encoding="utf-8")
            self.assertEqual(len(RC.parse_csv(p)), 3)


class TestLoad(unittest.TestCase):
    def test_cached_csv_used_without_network(self):
        with tempfile.TemporaryDirectory() as d:
            f = RC.cache_file(Path(d))
            f.parent.mkdir(parents=True)
            f.write_text(CSV, encoding="utf-8")
            with mock.patch.object(urllib.request, "urlopen", side_effect=AssertionError("réseau")):
                self.assertEqual(RC.load(Path(d))[5001], (25, 60, True))

    def test_network_failure_returns_empty(self):
        with tempfile.TemporaryDirectory() as d, mock.patch("sys.stdout"):
            with mock.patch.object(urllib.request, "urlopen", side_effect=OSError("hors ligne")):
                self.assertEqual(RC.load(Path(d)), {})
            self.assertEqual(RC.load(Path(d), offline=True), {})
            self.assertFalse(RC.cache_file(Path(d)).exists())

    def test_download_writes_cache(self):
        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return CSV.encode("utf-8")

        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(urllib.request, "urlopen", return_value=Resp()) as m:
                colors = RC.load(Path(d))
            req = m.call_args[0][0]
            self.assertEqual(req.get_header("User-agent"), "forever-companion-gamedata")
            self.assertIn(RC.WAGO_BUILD, req.full_url)
            self.assertEqual(m.call_args[1]["timeout"], RC.TIMEOUT)
            self.assertEqual(len(colors), 3)
            self.assertTrue(RC.cache_file(Path(d)).is_file())

    def test_fingerprint_part(self):
        self.assertEqual(RC.fingerprint_part({}), "recipe_colors=absent")
        self.assertIn(RC.WAGO_BUILD, RC.fingerprint_part({1: (1, 2, False)}))


class TestDatabase(unittest.TestCase):
    def _build(self, path, colors):
        return build.build_database(SY.FakeTables("frFR"), path, SY.QUEST_CACHE,
                                    {"schema_version": build.SCHEMA_VERSION, "fingerprint": "test",
                                     "build": "0.0.0.1", "locale": "frFR"}, colors)

    def test_table_written_and_ranks_use_colors(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "forever-frFR.sqlite"
            counts = self._build(p, RC.parse_csv(CSV))
            self.assertEqual(counts["recipe_colors"], 3)
            con = sqlite3.connect(p)
            self.assertEqual(con.execute("SELECT yellow, grey, trainer_rank1 FROM recipe_colors WHERE spell_id=5001")
                             .fetchone(), (25, 60, 1))
            self.assertEqual(con.execute("SELECT yellow, grey FROM recipe_colors WHERE spell_id=9103").fetchone(),
                             (None, None))
            # recette apprise d'office : rang 1 lu (au lieu de l'estimation 110)
            self.assertEqual(con.execute("SELECT rank_est, rank_source FROM recipes WHERE spell_id=5001").fetchone(),
                             (1, "client"))
            meta = dict(con.execute("SELECT key, value FROM meta"))
            self.assertIn("wago.tools", meta["recipe_colors_source"])
            self.assertIn("jamais redistribuées", meta["recipe_colors_license"])
            con.close()

    def test_without_colors_no_table(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "forever-frFR.sqlite"
            counts = self._build(p, {})
            self.assertEqual(counts["recipe_colors"], 0)
            con = sqlite3.connect(p)
            self.assertIsNone(con.execute("SELECT 1 FROM sqlite_master WHERE name='recipe_colors'").fetchone())
            self.assertEqual(con.execute("SELECT rank_source FROM recipes WHERE spell_id=5001").fetchone()[0],
                             "estimation")
            self.assertEqual(dict(con.execute("SELECT key, value FROM meta"))["recipe_colors_source"], "absent")
            self.assertEqual(RC.read(con.execute), {})
            con.close()


if __name__ == "__main__":
    unittest.main()
