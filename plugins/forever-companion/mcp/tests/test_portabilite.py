"""Portabilité : recherche du jeu (arborescences simulées), écritures, URI SQLite, objets de l'autre faction."""
import json
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")  # jamais de réseau dans les tests
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1]))

import server  # noqa: E402
import sync  # noqa: E402
import wowpaths as W  # noqa: E402
from gamedata.tests import synthetic as SY  # noqa: E402


def make_game(root: Path, with_wtf: bool = True) -> Path:
    """Crée un faux dossier « World of Warcraft » (racine + _forever_)."""
    root.mkdir(parents=True, exist_ok=True)
    (root / ".build.info").write_text("Product!STRING:0|Version!STRING:0\nwowf|1.60.1.70938\n", encoding="utf-8")
    (root / "Data").mkdir(exist_ok=True)
    flav = root / "_forever_"
    (flav / ("WTF" if with_wtf else "Interface")).mkdir(parents=True, exist_ok=True)
    return root


class GameDetection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.vol = self.base / "Volumes"

    def tearDown(self):
        self.tmp.cleanup()

    def detect(self, **kw):
        kw.setdefault("home", self.home)
        kw.setdefault("windows", False)
        kw.setdefault("volumes", self.vol)
        kw.setdefault("applications", self.base / "Applications")
        return W.detect_wow_paths(**kw)

    def test_nothing_found(self):
        self.assertEqual(self.detect(), [])
        self.assertIsNone(W.detect_game_root(home=self.home, windows=False, volumes=self.vol,
                                                   applications=self.base / "Applications"))

    def test_wine_prefix(self):
        g = make_game(self.home / ".wine" / "drive_c" / "Program Files (x86)" / "World of Warcraft")
        self.assertEqual(self.detect(), [g / "_forever_"])
        self.assertEqual(W.detect_game_root(home=self.home, windows=False, volumes=self.vol,
                                                   applications=self.base / "Applications"), g)

    def test_lutris_prefix_from_game_file(self):
        prefix = self.base / "anywhere" / "my wow prefix"
        g = make_game(prefix / "drive_c" / "Program Files (x86)" / "World of Warcraft")
        games = self.home / ".config" / "lutris" / "games"
        games.mkdir(parents=True)
        (games / "world-of-warcraft-1700000000.yml").write_text(
            "name: World of Warcraft\ngame:\n  exe: drive_c/x.exe\n  prefix: '" + str(prefix) + "'\n",
            encoding="utf-8")
        self.assertIn(g / "_forever_", self.detect())

    def test_lutris_prefix_with_tilde(self):
        g = make_game(self.home / "Jeux" / "wow" / "drive_c" / "Program Files" / "World of Warcraft")
        games = self.home / ".local" / "share" / "lutris" / "games"
        games.mkdir(parents=True)
        (games / "wow.yml").write_text("game:\n  prefix: ~/Jeux/wow\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"HOME": str(self.home), "USERPROFILE": str(self.home)}):
            self.assertIn(g / "_forever_", self.detect())

    def test_proton_and_bottles(self):
        p = make_game(self.home / ".local/share/Steam/steamapps/compatdata/123/pfx/drive_c/Program Files (x86)"
                      / "World of Warcraft")
        b = make_game(self.home / ".var/app/com.usebottles.bottles/data/bottles/bottles/WoW/drive_c/Program Files"
                      / "World of Warcraft", with_wtf=False)
        found = self.detect()
        self.assertIn(p / "_forever_", found)
        self.assertIn(b / "_forever_", found)

    def test_macos_external_volume(self):
        g = make_game(self.vol / "Jeux" / "World of Warcraft")
        self.assertEqual(self.detect(), [g / "_forever_"])

    def test_windows_registry_and_battlenet(self):
        reg_game = make_game(self.base / "D_drive" / "Blizzard" / "World of Warcraft")
        bnet_base = self.base / "E_drive" / "Games"
        bnet_game = make_game(bnet_base / "World of Warcraft")
        appdata = self.base / "AppData" / "Roaming"
        (appdata / "Battle.net").mkdir(parents=True)
        (appdata / "Battle.net" / "Battle.net.config").write_text(
            "﻿" + json.dumps({"Client": {"Install": {"DefaultInstallPath": str(bnet_base)}}}), encoding="utf-8")

        def registry(key, value):
            if "Blizzard Entertainment" in key and value == "InstallPath":
                return f'"{reg_game}"'
            return None

        found = W.detect_wow_paths(home=self.home, windows=True, registry=registry, appdata=str(appdata), drives="")
        self.assertEqual(found, [reg_game / "_forever_", bnet_game / "_forever_"])
        self.assertEqual(W.detect_game_root(home=self.home, windows=True, registry=registry,
                                            appdata=str(appdata), drives=""), reg_game)

    def test_broken_battlenet_config_is_ignored(self):
        appdata = self.base / "AppData"
        (appdata / "Battle.net").mkdir(parents=True)
        (appdata / "Battle.net" / "Battle.net.config").write_text("{pas du json", encoding="utf-8")
        self.assertEqual(W.battlenet_roots(str(appdata)), [])
        self.assertEqual(W.windows_registry_roots(lambda k, v: None), [])

    def test_game_root_of_flavor_dir(self):
        g = make_game(self.base / "World of Warcraft")
        self.assertEqual(W.game_root_of(g / "_forever_"), g)
        self.assertEqual(W.game_root_of(g), g)

    def test_sync_and_build_share_detection(self):
        from gamedata import build
        self.assertIs(sync.detect_wow_paths, W.detect_wow_paths)
        self.assertIs(sync.normalize_wow_path, W.normalize_wow_path)
        with mock.patch.object(W, "candidate_roots", return_value=[make_game(self.base / "X" / "World of Warcraft")]):
            self.assertEqual(build.detect_wow(), self.base / "X" / "World of Warcraft")


class Writes(unittest.TestCase):
    def test_lf_line_endings_and_retry(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sub" / "profil.md"
            sync.write_text(p, "a\nb\n")
            self.assertEqual(p.read_bytes(), b"a\nb\n")
            sync.write_json(p.with_suffix(".json"), {"é": 1})
            self.assertNotIn(b"\r\n", p.with_suffix(".json").read_bytes())
            calls = {"n": 0}
            real = os.replace

            def flaky(src, dst):
                calls["n"] += 1
                if calls["n"] < 3:
                    raise PermissionError("verrouillé")
                return real(src, dst)

            with mock.patch.object(sync.os, "replace", side_effect=flaky), mock.patch.object(sync.time, "sleep"):
                sync.write_text(p, "c\n")
            self.assertEqual(p.read_text(encoding="utf-8"), "c\n")
            self.assertEqual(calls["n"], 3)


class SqliteUri(unittest.TestCase):
    def test_path_with_hash_and_percent(self):
        import gamedb as GDB
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / "Jeux #1 100%"
            db_path = folder / "gamedata" / "forever-frFR.sqlite"
            SY.make_db(db_path)
            before = sorted(p.name for p in folder.rglob("*"))
            gdb = GDB.GameDB(db_path)
            self.assertTrue(gdb.q("SELECT count(*) AS n FROM items")[0]["n"] > 0)
            self.assertEqual(sorted(p.name for p in folder.rglob("*")), before)  # aucun fichier parasite


class OtherFactionVendor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_path = Path(cls.tmp.name) / "gamedata" / "forever-frFR.sqlite"
        SY.make_db_with_questie(cls.db_path)
        con = sqlite3.connect(str(cls.db_path))
        ncols = [r[1] for r in con.execute("PRAGMA table_info(q_npcs)")]
        icols = [r[1] for r in con.execute("PRAGMA table_info(q_items)")]

        def npc(nid, name, friendly):
            row = {c: None for c in ncols}
            row.update(id=nid, name=name, friendly=friendly)
            con.execute(f"INSERT INTO q_npcs ({','.join(ncols)}) VALUES ({','.join('?' * len(ncols))})",
                        [row[c] for c in ncols])

        def item(iid, vendors, drops=None):
            row = {c: None for c in icols}
            row.update(id=iid, name=f"Item {iid}", vendors=json.dumps(vendors),
                       npc_drops=json.dumps(drops) if drops else None)
            con.execute(f"INSERT INTO q_items ({','.join(icols)}) VALUES ({','.join('?' * len(icols))})",
                        [row[c] for c in icols])

        npc(9001, "Horde Quartermaster", "H")
        npc(9002, "Neutral Goblin", "AH")
        npc(9003, "Alliance Quartermaster", "A")
        item(8001, [9001])               # seulement la Horde
        item(8002, [9001, 9002])         # un marchand neutre aussi
        item(8003, [9001], drops=[503])  # aussi en butin
        item(8004, [9003])               # Alliance
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

    def test_vendor_faction(self):
        t = server.Tools.__new__(server.Tools)
        t.store = SimpleNamespace(data_dir=Path(self.tmp.name) / "perso")
        t._gdb = None
        gdb = t.gamedb()
        self.assertTrue(t.other_faction_vendor_only(gdb, 8001, "Alliance"))
        self.assertFalse(t.other_faction_vendor_only(gdb, 8001, "Horde"))
        self.assertFalse(t.other_faction_vendor_only(gdb, 8002, "Alliance"))
        self.assertFalse(t.other_faction_vendor_only(gdb, 8003, "Alliance"))
        self.assertTrue(t.other_faction_vendor_only(gdb, 8004, "Horde"))
        self.assertFalse(t.other_faction_vendor_only(gdb, 8001, ""))
        self.assertFalse(t.other_faction_vendor_only(gdb, 2003, "Alliance"))  # aucun marchand


if __name__ == "__main__":
    unittest.main()
