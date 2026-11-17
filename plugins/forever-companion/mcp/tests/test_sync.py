"""Tests de la synchro sur un faux dossier WoW construit à partir des fixtures."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import sync  # noqa: E402
from luasv import loads  # noqa: E402

FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"
ACC = "123456#1"


class TestSync(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.wow = self.tmp / "World of Warcraft" / "_forever_"
        acc = self.wow / "WTF" / "Account" / ACC
        (acc / "SavedVariables").mkdir(parents=True)
        shutil.copy(FIXTURES / "account_SavedVariables_ForeverScribe.lua", acc / "SavedVariables" / sync.SV_NAME)
        self.sv = acc / "93" / "Brannok-Durn" / "SavedVariables" / sync.SV_NAME
        self.sv.parent.mkdir(parents=True)
        # CRLF comme le client Windows
        self.sv.write_bytes((FIXTURES / "character_SavedVariables_ForeverScribe.lua").read_bytes().replace(b"\n", b"\r\n"))
        (acc / "93" / "Elwyna-Lor").mkdir(parents=True)
        self.data = self.tmp / "perso"
        self.data.mkdir()
        (self.data / sync.CONFIG_NAME).write_text(json.dumps(
            {"wowPaths": [str(self.wow.parent)], "accounts": {ACC: "Pierre"}}), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_first_sync_then_unchanged(self):
        rep = sync.sync(self.data)
        self.assertEqual(rep["updated"], ["Pierre/Brannok-EU"], rep)
        cdir = self.data / "Pierre" / "Brannok-EU"
        for f in ("etat.json", "profil.md", "journal.md", "objectifs.md"):
            self.assertTrue((cdir / f).exists(), f)
        self.assertEqual(len(list((cdir / "historique").glob("*.json"))), 1)
        self.assertIn("Première capture", (cdir / "journal.md").read_text(encoding="utf-8"))
        self.assertEqual([u["dir"] for u in rep["uncaptured"]], ["Elwyna-Lor"])
        rep2 = sync.sync(self.data)
        self.assertEqual(rep2["updated"], [])
        self.assertEqual(rep2["unchanged"], 1)

    def test_notes_kept_and_journal_diff(self):
        sync.sync(self.data)
        cdir = self.data / "Pierre" / "Brannok-EU"
        prof = cdir / "profil.md"
        prof.write_text(prof.read_text(encoding="utf-8") + "\n- ma note perso\n", encoding="utf-8")
        text = self.sv.read_text(encoding="utf-8")
        text = text.replace('["level"] = 25', '["level"] = 26')
        db = loads(text)["ForeverScribeCharDB"]
        self.assertEqual(db["progression"]["level"], 26)
        text = text.replace('["rank"] = 106', '["rank"] = 112')
        self.sv.write_text(text, encoding="utf-8")
        sync.sync(self.data)
        self.assertIn("- ma note perso", prof.read_text(encoding="utf-8"))
        journal = (cdir / "journal.md").read_text(encoding="utf-8")
        self.assertIn("Travail du cuir : 106 → 112", journal)
        self.assertIn("Niveau 26 atteint", journal)

    def test_logout_zeros_repaired(self):
        sync.sync(self.data)
        text = self.sv.read_text(encoding="utf-8")
        text = text.replace('["xpMax"] = 34000', '["xpMax"] = 0').replace('["health"] = 922', '["health"] = 0')
        self.sv.write_text(text, encoding="utf-8")
        rep = sync.sync(self.data)
        self.assertIn("progression", rep.get("repaired", {}).get("Pierre/Brannok-EU", []))
        etat = json.loads((self.data / "Pierre" / "Brannok-EU" / "etat.json").read_text(encoding="utf-8"))
        self.assertEqual(etat["data"]["progression"]["xpMax"], 34000)
        self.assertEqual(etat["data"]["stats"]["health"], 922)

    def test_register_account_moves_folder(self):
        (self.data / sync.CONFIG_NAME).write_text(json.dumps({"wowPaths": [str(self.wow)]}), encoding="utf-8")
        rep = sync.sync(self.data)
        self.assertEqual(rep["updated"], ["Compte-123456-1/Brannok-EU"])
        store = sync.Store(self.data)
        msg = store.register_account("123456#1", "Lucas")
        self.assertIn("Lucas", msg)
        self.assertTrue((self.data / "Lucas" / "Brannok-EU" / "etat.json").exists())
        c, err = store.resolve("Lucas/Brannok-EU")
        self.assertIsNotNone(c, err)

    def test_legacy_migration(self):
        legacy = self.data / "Brannok"
        legacy.mkdir()
        (legacy / "profil.md").write_text("# Profil — Brannok\n- vieux\n", encoding="utf-8")
        (legacy / "objectifs.md").write_text("# Objectifs\n- monter 60\n", encoding="utf-8")
        (legacy / "journal.md").write_text("# Journal\n- 2026-11-12 : début\n", encoding="utf-8")
        rep = sync.sync(self.data)
        self.assertEqual(rep["migrated"], ["Brannok → Pierre/Brannok-EU"])
        cdir = self.data / "Pierre" / "Brannok-EU"
        self.assertFalse(legacy.exists())
        self.assertIn("monter 60", (cdir / "objectifs.md").read_text(encoding="utf-8"))
        self.assertIn("2026-11-12 : début", (cdir / "journal.md").read_text(encoding="utf-8"))
        self.assertTrue((cdir / "archive" / "profil-avant-addon.md").exists())


if __name__ == "__main__":
    unittest.main()
