"""Tests de la langue de sortie (fr / en) et de la prise en charge d'un client anglais (enUS).

- catalogue : chaque texte passé à T() a sa traduction anglaise, avec les mêmes {champs} ;
- même capture (client frFR) rendue en français et en anglais : libellés traduits, noms du jeu inchangés ;
- capture d'un client anglais (enUS) : sortie anglaise par défaut, français sur demande ;
- base du jeu anglaise (synthétique) : filtres bilingues, recherche « humberts helm », choix de la base ;
- logique qui ne dépend plus du texte français (verdicts, compétences d'armes, types).
"""
import ast
import json
import os
import re
import shutil
import string
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
MCP = HERE.parent
sys.path.insert(0, str(MCP))
sys.path.insert(0, str(MCP.parent / "gamedata" / "tests"))
sys.path.insert(0, str(HERE))

import e2e_stdio as E  # noqa: E402
import formats as F  # noqa: E402
import gamedb as GDB  # noqa: E402
import gear as G  # noqa: E402
import i18n as I  # noqa: E402
import server  # noqa: E402
import sync  # noqa: E402
import synthetic as SY  # noqa: E402
from i18n_en import EN  # noqa: E402

FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"
EN_LUA = FIXTURES / "character_SavedVariables_ForeverScribe.enUS.lua"
EN_JSON = FIXTURES / "character.enUS.json"
MODULES = ["formats.py", "gear.py", "gamedb.py", "gamedb_tools.py", "server.py", "sync.py", "knowledge.py"]
FMT = string.Formatter()


def fields(text):
    return {f for _, f, _, _ in FMT.parse(text) if f}


def t_literals():
    for mod in MODULES:
        for node in ast.walk(ast.parse((MCP / mod).read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                fn = node.func
                name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
                if name == "T":
                    yield mod, node.args[0].value


def sandbox(lua: Path, config_extra=None) -> Path:
    tmp = E.build_sandbox()
    char = next((tmp / "World of Warcraft" / "_forever_" / "WTF" / "Account").rglob("Brannok-Durn"))
    shutil.copy(lua, char / "SavedVariables" / "ForeverScribe.lua")
    if config_extra:
        cfg = json.loads((tmp / "perso" / "config.json").read_text(encoding="utf-8"))
        cfg.update(config_extra)
        (tmp / "perso" / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    return tmp


def call(srv, name, **args):
    r = srv.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}})
    res = r["result"]
    return res["content"][0]["text"], res["isError"]


class TestCatalog(unittest.TestCase):
    def test_every_literal_has_english(self):
        missing = [(m, k) for m, k in t_literals() if k not in EN]
        self.assertEqual(missing, [], "textes sans traduction anglaise dans i18n_en.py")

    def test_placeholders_match(self):
        bad = [(k, v) for k, v in EN.items() if fields(k) != fields(v)]
        self.assertEqual(bad, [])

    def test_english_has_no_obvious_french(self):
        french = re.compile(r"\b(le|la|les|des|une|est|pour|avec|dans|quête|niveau|emplacement|capturé)\b", re.I)
        offenders = [v for v in EN.values() if french.search(re.sub(r"\{[^}]*\}", "", v))]
        # les exemples de valeurs françaises acceptées sont volontaires
        offenders = [v for v in offenders if "French" not in v and "tête" not in v and "Les " not in v]
        self.assertEqual(offenders, [])

    def test_lang_normalisation(self):
        self.assertEqual(I.norm_lang("en-US"), "en")
        self.assertEqual(I.norm_lang("English"), "en")
        self.assertEqual(I.norm_lang("frFR"), "fr")
        self.assertIsNone(I.norm_lang("de"))
        self.assertEqual(I.lang_from_locale("frFR"), "fr")
        self.assertEqual(I.lang_from_locale("enUS"), "en")
        self.assertEqual(I.lang_from_locale("deDE"), "en")


class TestFormatting(unittest.TestCase):
    def test_numbers_money_age(self):
        with I.using("fr"):
            self.assertEqual(F.num(12345.6, 1), "12 345,6")
            self.assertEqual(F.money(40015), "4 po 0 pa 15 pc")
            self.assertEqual(F.age(100, now=100 + 600), "il y a 10 min")
        with I.using("en"):
            self.assertEqual(F.num(12345.6, 1), "12,345.6")
            self.assertEqual(F.money(40015), "4 g 0 s 15 c")
            self.assertEqual(F.age(100, now=100 + 600), "10 min ago")
            self.assertEqual(F.age(0, now=3 * 86400), "3 days ago")
            self.assertEqual(F.slot_label("HeadSlot"), "Head")
        self.assertEqual(I.get_lang(), "fr")  # le contexte est bien rétabli

    def test_item_stats_are_language_independent(self):
        it = {"stats": {"ITEM_MOD_AGILITY_SHORT": 5, "RESISTANCE0_NAME": 40, "ITEM_MOD_FIRE_RESISTANCE_SHORT": 3,
                        "RESISTANCE2_NAME": 3}}
        st = F.item_stats(it)
        self.assertEqual(st, {"AGILITY": 5, "ARMOR": 40, "FIRE_RESISTANCE": 3})
        with I.using("fr"):
            self.assertEqual(F.stats_text(st), "+5 Agi, +3 Rés. feu")
        with I.using("en"):
            self.assertEqual(F.stats_text(st, with_armor=True), "+5 Agi, +40 Armor, +3 Fire res.")


class TestGearLogic(unittest.TestCase):
    def setUp(self):
        self.db = json.loads((FIXTURES / "character.json").read_text(encoding="utf-8"))

    def test_verdict_code_same_in_both_languages(self):
        item = {"classId": 4, "subclassId": 3, "equipLoc": "INVTYPE_HEAD", "name": "x", "stats": {}}
        with I.using("fr"):
            fr = G.evaluate(self.db, item)
        with I.using("en"):
            en = G.evaluate(self.db, item)
        self.assertEqual((fr["code"], en["code"]), ("not_for_you", "not_for_you"))
        self.assertEqual((fr["verdict"], en["verdict"]), ("pas pour toi", "not for you"))
        self.assertIn("40", en["reason"])

    def test_parse_type_bilingual(self):
        for words, expected in ((("arbalète", "Crossbow", "crossbows"), (2, (18,))),
                                (("cuir", "Leather"), (4, (2,))),
                                (("Two-Handed Sword", "épée à deux mains"), (2, (8,))),
                                (("arme à feu", "gun"), (2, (3,)))):
            for w in words:
                self.assertEqual(G.parse_type(w), expected, w)
        self.assertIsNone(G.parse_type("arcane"))  # « arc » ne doit pas matcher un mot plus long

    def test_weapon_skill_by_id_or_name(self):
        db = json.loads(json.dumps(self.db))
        db["professions"]["skills"] = [{"name": "Crossbows", "skillId": 226, "rank": 1, "max": 125}]
        for text in ("arbalète", "crossbow"):
            note = server.weapon_skill_note(db, text, "RangedSlot")
            self.assertIn("1/125", note)
        db["professions"]["skills"] = [{"name": "Arbalètes", "rank": 5, "max": 125}]  # sans ID : par le nom
        self.assertIn("5/125", server.weapon_skill_note(db, "Crossbow", "RangedSlot"))
        bow = {"classId": 2, "subclassId": 18}
        self.assertIn("5/125", server.weapon_skill_note(db, "Objet sans type dans le nom", "RangedSlot", bow))


class TestSameCaptureTwoLanguages(unittest.TestCase):
    """Client frFR : la même capture, rendue en français puis en anglais."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = E.build_sandbox()
        cls.old = os.environ.get("FOREVER_GAMEDB")
        os.environ["FOREVER_GAMEDB"] = str(cls.tmp / "none.sqlite")  # pas de base du jeu
        cls.srv = server.Server(sync.Store(cls.tmp / "perso"))

    @classmethod
    def tearDownClass(cls):
        if cls.old is None:
            os.environ.pop("FOREVER_GAMEDB", None)
        else:
            os.environ["FOREVER_GAMEDB"] = cls.old
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_default_follows_client_locale(self):
        text, _ = call(self.srv, "get_equipment")
        self.assertIn("| Emplacement | Objet |", text)

    def test_equipment(self):
        fr, _ = call(self.srv, "get_equipment", lang="fr")
        en, _ = call(self.srv, "get_equipment", lang="en")
        self.assertIn("| Emplacement | Objet |", fr)
        self.assertIn("| Slot | Item | ilvl | Stats | Durability |", en)
        self.assertIn("| Ranged | Fusil à canon double (rare)", en)  # nom du jeu inchangé, libellé traduit
        self.assertIn("| Distance | Fusil à canon double (rare)", fr)
        self.assertIn("captured", en)

    def test_overview_and_rewards(self):
        en, _ = call(self.srv, "get_overview", lang="en")
        for s in ("- Empty slots:", "**Quests to turn in:**", "Arc des marais", "upgrade", "[Ranged, replaces"):
            self.assertIn(s, en)
        rw, _ = call(self.srv, "get_quest_rewards", lang="en")
        self.assertIn("not equippable", rw)
        self.assertIn("empty slot: equip it", rw)
        self.assertNotIn("à rendre", rw)

    def test_compare_item_english_inputs(self):
        en, err = call(self.srv, "compare_item", lang="en", nom="Test crossbow", emplacement="ranged", dps=15.2,
                       pa_distance=12, type_arme="crossbow")
        self.assertFalse(err)
        self.assertIn("**Take it: about +", en)
        self.assertIn("| Ranged AP |", en)
        fr, _ = call(self.srv, "compare_item", lang="fr", nom="Test", emplacement="distance", dps=15.2, pa_distance=12)
        self.assertIn("**À prendre : environ +", fr)
        self.assertIn("| PA distance |", fr)

    def test_errors_are_translated(self):
        text, err = call(self.srv, "get_character", lang="en", perso="nobody")
        self.assertTrue(err)
        self.assertIn('Unknown character "nobody"', text)
        text, err = call(self.srv, "find_items", lang="en", nom="x")
        self.assertTrue(err)
        self.assertIn("The local game database is not built yet", text)

    def test_tools_list_accepts_lang(self):
        r = self.srv.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        for t in r["result"]["tools"]:
            self.assertIn("lang", t["inputSchema"]["properties"], t["name"])

    def test_every_tool_runs_in_english_without_missing_text(self):
        I.MISSING.clear()
        for name, args in E.CALLS:
            if name in ("save_knowledge", "register_account"):
                continue
            call(self.srv, name, lang="en", **args)
        self.assertEqual(I.MISSING, set())


class TestEnglishClient(unittest.TestCase):
    """Capture d'un client anglais (enUS) + base du jeu anglaise."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = sandbox(EN_LUA)
        cls.db_path = cls.tmp / "gamedata" / "forever-enUS.sqlite"
        SY.make_db(cls.db_path, "enUS")
        cls.old = os.environ.pop("FOREVER_GAMEDB", None)
        cls.srv = server.Server(sync.Store(cls.tmp / "perso"))

    @classmethod
    def tearDownClass(cls):
        if cls.old is not None:
            os.environ["FOREVER_GAMEDB"] = cls.old
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_default_language_is_english(self):
        text, _ = call(self.srv, "get_character")
        self.assertIn("Dwarf Hunter", text)
        self.assertIn("- Weapons:", text)
        self.assertIn("game language: enUS", text)
        fr, _ = call(self.srv, "get_character", lang="fr")
        self.assertIn("- Armes :", fr)
        self.assertIn("Double-barreled Shotgun", fr)  # noms du jeu en anglais, même en réponse française

    def test_profile_and_journal_written_in_english(self):
        folder = next((self.tmp / "perso").rglob("profil.md")).parent
        prof = (folder / "profil.md").read_text(encoding="utf-8")
        self.assertIn("## Equipment", prof)
        self.assertIn("## My notes", prof)
        self.assertIn("<!-- auto:debut -->", prof)  # balises inchangées (compatibilité)
        self.assertIn("## Automatic journal", (folder / "journal.md").read_text(encoding="utf-8"))
        self.assertIn("# Goals", (folder / "objectifs.md").read_text(encoding="utf-8"))

    def test_answer_language_from_config(self):
        tmp = sandbox(EN_LUA, {"answer_language": "fr"})
        try:
            srv = server.Server(sync.Store(tmp / "perso"))
            text, _ = call(srv, "get_equipment")
            self.assertIn("| Emplacement |", text)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_db_chosen_by_locale(self):
        self.assertEqual(GDB.find_db_path(self.tmp / "perso", "enUS"), self.db_path)
        other = self.tmp / "gamedata" / "forever-frFR.sqlite"
        SY.make_db(other, "frFR")
        try:
            self.assertEqual(GDB.find_db_path(self.tmp / "perso", "frFR"), other)
            self.assertEqual(GDB.find_db_path(self.tmp / "perso", "enUS"), self.db_path)
            text, _ = call(self.srv, "get_item", itemId=1001)
            self.assertIn("Trial Helm", text)  # perso enUS -> base enUS
        finally:
            other.unlink()

    def test_bilingual_filters(self):
        for t in ("leather", "cuir"):
            text, err = call(self.srv, "find_items", type=t, niveau_max=30)
            self.assertFalse(err, text)
            self.assertIn("Trial Helm", text)
            self.assertNotIn("Trial Mail Gloves", text)
        for slot in ("head", "tête", "helm"):
            text, _ = call(self.srv, "find_items", emplacement=slot)
            self.assertIn("Trial Helm", text)
        for q in ("blue", "bleu"):
            text, _ = call(self.srv, "find_items", qualite_min=q, emplacement="head")
            self.assertIn("Humbert's Trial Helm", text)
            self.assertNotIn("(id 1001)", text)
        text, _ = call(self.srv, "find_items", stat="agility", niveau_max=30)
        self.assertIn("[Forever · local DB]", text)
        text, err = call(self.srv, "find_items", type="spaceship")
        self.assertTrue(err)

    def test_name_search_possessive(self):
        text, err = call(self.srv, "get_item", nom="humberts trial helm")
        self.assertFalse(err, text)
        self.assertIn("**Humbert's Trial Helm**", text)
        self.assertIn("leather · Head", text)  # type et emplacement calculés depuis les IDs

    def test_recipes_by_english_or_french_profession(self):
        for name in ("Leatherworking", "Travail du cuir"):
            text, err = call(self.srv, "find_recipes", metier=name)
            self.assertFalse(err, text)
            self.assertIn("**Leatherworking**", text)
            self.assertIn("Crafted Belt", text)
        text, _ = call(self.srv, "get_item", itemId=1007)
        self.assertIn("crafting: Leatherworking — Crafted Belt (skill 1)", text)

    def test_upgrades_and_dungeon(self):
        text, _ = call(self.srv, "find_upgrades")
        self.assertIn("Possible upgrades for **Brannok** (Hunter", text)
        self.assertIn("**Head** (equipped: nothing)", text)
        text, _ = call(self.srv, "get_dungeon_loot", donjon="trial dungeon")
        self.assertIn("**Trial Dungeon** (dungeon, map 9001)", text)

    def test_quest_info_english(self):
        text, _ = call(self.srv, "get_quest_info", titre="trial quest")
        self.assertIn("**Trial Quest**", text)
        self.assertIn("- Objective: Kill 5 Trial Wolves.", text)


class TestGameDBMixinDirect(unittest.TestCase):
    """Les outils appelés sans passer par Server (tests existants) restent en français."""

    def test_default_french(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "forever-frFR.sqlite"
            SY.make_db(p)
            os.environ["FOREVER_GAMEDB"] = str(p)
            try:
                t = server.Tools.__new__(server.Tools)
                t.store = SimpleNamespace(data_dir=Path(d) / "perso")
                t._gdb = None
                data = json.loads((FIXTURES / "character.json").read_text(encoding="utf-8"))
                t._char = lambda args: ({}, data)
                self.assertIn("[Forever · base locale]", t.find_items({"type": "leather"}))
            finally:
                os.environ.pop("FOREVER_GAMEDB", None)


if __name__ == "__main__":
    unittest.main()
