"""Caches du client (questcache, creaturecache, gameobjectcache) ajoutés à la base : données inventées."""
import sqlite3
import struct
import tempfile
import unittest
from pathlib import Path

import synthetic as SY  # noqa: E402  (ajoute le dossier du plugin au chemin)
from gamedata import clientcache as CC  # noqa: E402


def wdb_bytes(magic, records):
    """records : {id: [chaînes]} — corps = 4 octets de champs puis chaînes terminées par \\0."""
    out = bytearray(magic + struct.pack("<I", 1) + b"RFrf" + struct.pack("<II", 0, 12) + bytes(4))
    for rid, strings in records.items():
        body = b"\x07\x00\x00\x00" + b"".join(s.encode("utf-8") + b"\0" for s in strings)
        out += struct.pack("<II", rid, len(body)) + body
    return bytes(out)


class ClientCacheTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.db = root / "gamedata" / "forever-frFR.sqlite"
        SY.make_db(self.db)
        self.wdb = root / "WDB" / "frFR"
        self.wdb.mkdir(parents=True)
        (self.wdb / "questcache.wdb").write_bytes(SY.questcache_bytes({
            90001: SY.quest_record("Peaux de raptor", "Rapporter 8 peaux.", "Va voir le Chef de port Halvard."),
        }))
        (self.wdb / "creaturecache.wdb").write_bytes(wdb_bytes(b"BOMW", {
            90100: ["Garde Brumebarbe", "Capitaine"],
            90101: ["Chef de port Halvard"],
            5: ["\x01\x02"],                       # rien de lisible : ignoré
        }))
        (self.wdb / "gameobjectcache.wdb").write_bytes(wdb_bytes(b"BOGW", {90200: ["Coffre englouti"]}))

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self, sql):
        con = sqlite3.connect(str(self.db))
        try:
            return con.execute(sql).fetchall()
        finally:
            con.close()

    def test_refresh_then_skip_until_changed(self):
        counts = CC.refresh(self.db, self.wdb)
        self.assertEqual(counts, {"quests": 1, "creatures": 2, "objects": 1})
        self.assertEqual(self.rows("SELECT title, title_norm, objectives FROM c_quests WHERE id = 90001"),
                         [("Peaux de raptor", "peaux de raptor", "Rapporter 8 peaux.")])
        self.assertIn((90100, "Garde Brumebarbe", "Capitaine", "garde brumebarbe"),
                      self.rows("SELECT * FROM c_creatures"))
        self.assertEqual(self.rows("SELECT name_norm FROM c_objects"), [("coffre englouti",)])
        self.assertIsNone(CC.refresh(self.db, self.wdb))          # signature inchangée
        self.assertEqual(CC.refresh(self.db, self.wdb, force=True)["creatures"], 2)
        # la base d'origine reste intacte
        self.assertTrue(self.rows("SELECT COUNT(*) FROM quests")[0][0] >= 1)

    def test_missing_inputs(self):
        self.assertIsNone(CC.refresh(self.db, Path(self.tmp.name) / "absent"))
        self.assertIsNone(CC.refresh(Path(self.tmp.name) / "absent.sqlite", self.wdb))


if __name__ == "__main__":
    unittest.main()
