"""Tests de la base locale du jeu : DBCache.bin, correctifs, calcul des stats, cache des
quêtes, écriture SQLite. Données synthétiques uniquement (aucune donnée du jeu).

    python3 -m unittest discover -s plugins/forever-companion/gamedata/tests
"""
import sqlite3
import struct
import tempfile
import unittest
from pathlib import Path

import synthetic as SY  # noqa: E402  (ajoute le dossier du plugin au chemin)
from gamedata import dbcache, stats as S, wdb, wdc5  # noqa: E402
from gamedata.build import detect_locale, read_build_info  # noqa: E402

DBD = """COLUMNS
int ID
locstring Display_lang
int ItemLevel
float DmgVariance
int StatPercentEditor
int<Other::ID> ParentID

LAYOUT 0BADF00D
BUILD 9.9.9.1
$noninline,id$ID<32>
Display_lang
ItemLevel<u16>
DmgVariance
StatPercentEditor<32>[2]
$noninline,relation$ParentID<32>
"""


class TestLocale(unittest.TestCase):
    """Langue du client : Config.wtf, puis .build.info, puis enUS (fichiers synthétiques)."""

    BUILD_INFO = ("Branch!STRING:0|Tags!STRING:0|Version!STRING:0|Product!STRING:0\n"
                  "eu|OSX x86_64 EU? {loc} speech?:OSX x86_64 EU? {loc} text?|1.60.1.70938|wowf\n")

    def make(self, config=None, tags_locale=None):
        root = Path(tempfile.mkdtemp())
        (root / "_forever_" / "WTF").mkdir(parents=True)
        if config is not None:
            (root / "_forever_" / "WTF" / "Config.wtf").write_text(config, encoding="utf-8")
        if tags_locale:
            (root / ".build.info").write_text(self.BUILD_INFO.format(loc=tags_locale), encoding="utf-8")
        return root

    def test_config_wtf_first(self):
        root = self.make('SET gxApi "metal"\nSET textLocale "enUS"\nSET audioLocale "frFR"\n', "frFR")
        self.assertEqual(detect_locale(root), ("enUS", "Config.wtf"))

    def test_build_info_tags(self):
        root = self.make('SET gxApi "metal"\n', "deDE")
        self.assertEqual(detect_locale(root), ("deDE", ".build.info"))

    def test_default_english(self):
        self.assertEqual(detect_locale(self.make()), ("enUS", "défaut"))


class TestEnglishDatabase(unittest.TestCase):
    def test_english_names_and_search_norm(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "forever-enUS.sqlite"
            SY.make_db(path, "enUS")
            con = sqlite3.connect(path)
            row = con.execute("SELECT name, name_norm FROM items WHERE id = 1009").fetchone()
            self.assertEqual(row, ("Humbert's Trial Helm", "humbert s trial helm"))
            self.assertEqual(con.execute("SELECT value FROM meta WHERE key='locale'").fetchone()[0], "enUS")
            self.assertEqual(con.execute("SELECT name FROM professions WHERE id = 165").fetchone()[0],
                             "Leatherworking")
            con.close()


class TestDBCache(unittest.TestCase):
    def test_header_and_entries(self):
        data = SY.dbcache_bytes([
            (1, 0xAAAA, 10, 1, b"old"),
            (5, 0xAAAA, 10, 1, b"new"),
            (2, 0xAAAA, 10, 1, b"stale"),   # push plus ancien : ignoré
            (1, 0xAAAA, 11, 2, b""),
            (1, 0xBBBB, 12, 3, b"x"),
        ], build_no=4242)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "DBCache.bin"
            p.write_bytes(data)
            header, tables = dbcache.read_dbcache(p)
            self.assertEqual(header["build"], 4242)
            self.assertEqual(header["entries"], 5)
            self.assertEqual(tables[0xAAAA][10], (1, b"new"))
            self.assertEqual(tables[0xAAAA][11][0], dbcache.STATUS_DELETED)
            _, only = dbcache.read_dbcache(p, wanted_hashes={0xBBBB})
            self.assertEqual(list(only), [0xBBBB])

    def test_bad_magic(self):
        with self.assertRaises(ValueError):
            dbcache.read_header(b"NOPE" + bytes(40))

    def test_decode_hotfix_record(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "T.dbd"
            p.write_text(DBD, encoding="utf-8")
            _, blocks = wdc5.parse_dbd(p)
            block = wdc5.pick_block(blocks, 0x0BADF00D, "9.9.9.1")
        body = "Épée d'essai".encode() + b"\0" + struct.pack("<H", 27) + struct.pack("<f", 0.5) \
            + struct.pack("<ii", 6666, -1) + struct.pack("<I", 77)
        row, used = wdc5.decode_hotfix_record(block, body, 4242)
        self.assertEqual(used, len(body))
        self.assertEqual(row["ID"], 4242)
        self.assertEqual(row["Display_lang"], "Épée d'essai")
        self.assertEqual(row["ItemLevel"], 27)
        self.assertAlmostEqual(row["DmgVariance"], 0.5)
        self.assertEqual(row["StatPercentEditor"], [6666, -1])
        self.assertEqual(row["ParentID"], 77)


class TestStats(unittest.TestCase):
    rp = SY.RANDPROP[30]

    def test_budget_columns(self):
        self.assertEqual(S.budget(self.rp, 2, 1), 20)    # tête, inhabituel
        self.assertEqual(S.budget(self.rp, 3, 26), 8)    # fusil, rare
        self.assertEqual(S.budget(self.rp, 4, 11), 18)   # doigt, épique
        self.assertIsNone(S.budget(self.rp, 2, 0))

    def test_item_stats_rounding(self):
        it = SY.sparse(1, "x", 30, 25, 2, 1, [(3, 5000), (7, 2250)])
        self.assertEqual(S.item_stats(it, self.rp), {3: 10, 7: 5})  # 20×0,225 = 4,5 → 5 (arrondi au plus proche)
        self.assertEqual(S.item_stats(it, None), {})

    def test_weapon_damage(self):
        sp, (c, sc) = SY.ITEMS[1002]
        tables = SY.FakeTables()
        lo, hi, speed, dps = S.weapon_damage(sp, {"ClassID": c, "SubclassID": sc},
                                             {"ItemDamageRanged": tables.get("ItemDamageRanged")})
        self.assertEqual((lo, hi, speed), (15, 25, 2.0))   # 10 DPS × 2 s = 20 ; ×0,75 et ×1,25
        self.assertEqual(dps, 10.0)
        self.assertIsNone(S.weapon_damage(sp, {"ClassID": 4, "SubclassID": 2}, {}))

    def test_armor(self):
        t = SY.FakeTables()
        arm = {n: t.get(n) for n in ("ItemArmorTotal", "ItemArmorQuality", "ArmorLocation", "ItemArmorShield")}
        helm, _ = SY.ITEMS[1001]
        self.assertEqual(S.armor_value(helm, {"ClassID": 4, "SubclassID": 2}, arm), 20)   # 200 × 1,0 × 0,1
        cloak = SY.sparse(9, "cape", 30, 20, 3, 16)
        self.assertEqual(S.armor_value(cloak, {"ClassID": 4, "SubclassID": 1}, arm), 2)   # 50 × 1,1 × 0,04
        self.assertIsNone(S.armor_value(helm, {"ClassID": 2, "SubclassID": 3}, arm))


class TestQuestCache(unittest.TestCase):
    def test_titles(self):
        data = SY.questcache_bytes({7: SY.quest_record("Les loups d'essai", "Tuer 5 loups.", "Une histoire."),
                                    8: b"\x00" * 30})
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "questcache.wdb"
            p.write_bytes(data)
            q = wdb.read_quest_cache(p)
        self.assertEqual(q[7], ("Les loups d'essai", "Tuer 5 loups.", "Une histoire."))
        self.assertNotIn(8, q)


class TestBuild(unittest.TestCase):
    def test_build_info(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / ".build.info").write_text(
                "Branch!STRING:0|Version!STRING:0|Product!STRING:0\neu|9.9.9.1|wow\neu|1.2.3.4|wowf\n")
            self.assertEqual(read_build_info(d), "1.2.3.4")

    def test_database(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "forever-frFR.sqlite"
            counts = SY.make_db(p)
            self.assertEqual(counts["items"], len(SY.ITEMS))
            con = sqlite3.connect(p)
            con.row_factory = sqlite3.Row
            helm = con.execute("SELECT * FROM items WHERE id = 1001").fetchone()
            self.assertEqual((helm["agi"], helm["sta"], helm["armor"], helm["slot_fr"], helm["origin"]),
                             (10, 10, 20, "Tête", "ajoute"))
            gun = con.execute("SELECT * FROM items WHERE id = 1002").fetchone()
            self.assertEqual((gun["dmg_min"], gun["dmg_max"], gun["dps"], gun["kind"]), (15, 25, 10.0, "Fusil"))
            rec = con.execute("SELECT * FROM recipes").fetchall()
            self.assertEqual(len(rec), 1)   # la ligne « Givre » n'est pas un métier
            self.assertEqual((rec[0]["item_id"], rec[0]["rank_est"], rec[0]["rank_source"]), (1007, 110, "estimation"))
            self.assertIn("Cuir d'essai", rec[0]["reagents_json"])
            src = con.execute("SELECT source_type FROM item_sources WHERE item_id = 1001").fetchone()
            self.assertEqual(src[0], "donjon")
            self.assertEqual(con.execute("SELECT count(*) FROM dungeons").fetchone()[0], 2)
            q = con.execute("SELECT * FROM quests WHERE id = 1").fetchone()
            self.assertEqual(q["title"], "Quête d'essai")
            self.assertEqual(con.execute("SELECT value FROM meta WHERE key='fingerprint'").fetchone()[0], "test")
            con.close()
            SY.make_db(p)   # reconstruction au même endroit : remplace proprement
            self.assertFalse(p.with_suffix(".sqlite.tmp").exists())


if __name__ == "__main__":
    unittest.main()
