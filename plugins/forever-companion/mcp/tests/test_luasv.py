"""Tests du parseur SavedVariables : python3 -m unittest discover -s tests"""
import json
import os
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from luasv import LuaParseError, as_list, load_file, loads  # noqa: E402

REPO = HERE.parents[3]
FIXTURES = REPO / "addon" / "tests" / "fixtures"
# Test facultatif sur un vrai fichier : FOREVER_REAL_SV=<chemin vers .../SavedVariables/ForeverScribe.lua>
REAL = Path(os.environ.get("FOREVER_REAL_SV", "/nonexistent"))


def norm(x):
    """Rend comparables la sortie du parseur et le JSON de référence ({} == [], 3.0 == 3)."""
    if isinstance(x, dict):
        return {str(k): norm(v) for k, v in x.items()} if x else None
    if isinstance(x, list):
        return [norm(v) for v in x] if x else None
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


class TestSyntax(unittest.TestCase):
    def test_scalars(self):
        d = loads('A = { ["s"] = "x", ["i"] = 42, ["n"] = -3, ["f"] = 2.5, ["e"] = 1e5, ["neg"] = -1.25e-3, '
                  '["t"] = true, ["fa"] = false, ["nil"] = nil, ["hex"] = 0x1F }')["A"]
        self.assertEqual(d, {"s": "x", "i": 42, "n": -3, "f": 2.5, "e": 100000.0, "neg": -0.00125,
                             "t": True, "fa": False, "hex": 31})

    def test_escapes(self):
        d = loads(r'A = "a\"b\\c\nd\t\065\x42\u{E9}\
e"')["A"]
        self.assertEqual(d, 'a"b\\c\nd\tABé\ne')

    def test_utf8_decimal_escapes(self):
        # « é » écrit octet par octet
        self.assertEqual(loads(r'A = "\195\169"')["A"], "é")

    def test_lists_and_mixed(self):
        self.assertEqual(loads('A = { 1, 2, 3, }')["A"], [1, 2, 3])
        self.assertEqual(loads('A = { [1] = "a", [2] = "b" }')["A"], ["a", "b"])
        self.assertEqual(loads('A = { [2] = "b", [5] = "c" }')["A"], {2: "b", 5: "c"})
        self.assertEqual(loads('A = { x = 1; y = { } }')["A"], {"x": 1, "y": {}})
        self.assertEqual(as_list(loads('A = {}')["A"]), [])

    def test_comments_crlf_bom_multiple(self):
        text = "﻿-- commentaire\r\nA = {\r\n\t[\"k\"] = 1, --[[ long ]]\r\n}\r\nB = \"z\"\r\n"
        self.assertEqual(loads(text), {"A": {"k": 1}, "B": "z"})

    def test_long_string_and_inf(self):
        d = loads('A = { [[ligne\nautre]], math.huge, -math.huge }')["A"]
        self.assertEqual(d[0], "ligne\nautre")
        self.assertTrue(math.isinf(d[1]) and d[2] < 0)

    def test_errors(self):
        for bad in ('A = {', 'A = { ["x"] 1 }', 'A = "abc', '= 1'):
            with self.assertRaises(LuaParseError):
                loads(bad)


class TestFixtures(unittest.TestCase):
    def test_character_fixture_matches_json(self):
        parsed = load_file(FIXTURES / "character_SavedVariables_ForeverScribe.lua")["ForeverScribeCharDB"]
        ref = json.loads((FIXTURES / "character.json").read_text(encoding="utf-8"))
        self.assertEqual(norm(parsed), norm(ref))

    def test_account_fixture(self):
        db = load_file(FIXTURES / "account_SavedVariables_ForeverScribe.lua")["ForeverScribeDB"]
        self.assertEqual(db["schemaVersion"], 1)
        self.assertIn("Player-1234-0A1B2C3D", db["characters"])

    @unittest.skipUnless(REAL.exists(), "définir FOREVER_REAL_SV pour tester un vrai fichier")
    def test_real_file(self):
        db = load_file(REAL)["ForeverScribeCharDB"]
        self.assertTrue(db["identity"]["name"])
        self.assertTrue(db["meta"]["guid"].startswith("Player-"))
        self.assertGreater(len(as_list(db["quests"]["list"])), 0)
        self.assertTrue(all(isinstance(s, dict) for s in db["equipment"]["slots"].values()))


if __name__ == "__main__":
    unittest.main()
