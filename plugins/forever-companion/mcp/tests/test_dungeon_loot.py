"""Butin par boss des donjons (guides sourcés de donjons.json, QuestieDB par nom de rencontre) et recherche
par nom anglais. Base synthétique, guide de test écrit dans un dossier temporaire ; rien de réel."""
import json
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")  # jamais de réseau dans les tests
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[1] / "gamedata" / "tests"))

import synthetic as SY  # noqa: E402
import server  # noqa: E402
import dungeons as DG  # noqa: E402

FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"
REAL_GUIDES = DG.PATH

GUIDE = {
    "_doc": "test",
    "instances": [
        {"fr": "Crypte sans butin", "en": "Lootless Crypt", "map_id": 9002, "kind": "dungeon", "min": 20,
         "max": 26, "badge": "forever"},
    ],
    "guides": {
        "Lootless Crypt": {
            "source": "https://example.test/guide/lootless-crypt", "date": "2026-11-14", "certitude": "probable",
            "note": "Note d'essai.", "note_en": "Trial note.",
            "entree": {"texte": "en haut du sentier d'essai", "texte_en": "at the top of the trial path",
                       "zone": "Val d'essai", "zone_en": "Trial Vale", "way": "48.1 56.5", "rencontre_way": "53.9 65.4",
                       "certitude": "probable", "sources": ["https://www.example.test/a", "https://other.test/b"]},
            "dangers": {"certitude": "probable", "sources": ["https://example.test/guide/lootless-crypt"],
                        "liste": [{"fr": "Hautes herbes : rôdeurs invisibles par 3.",
                                   "en": "Tall grass: invisible lurkers in packs of 3."},
                                  {"fr": "Gardien : Frappe mortelle et Filet.", "en": "Warder: Mortal Strike and Net."}]},
            "boss": [{"en": "Silent Warden", "encounter": 7002,
                      "butin": [{"id": 1002, "en": "Trial Rifle"}, {"id": 1004, "en": "Bow Too High"},
                                {"id": 999998, "en": "Ghost Relic"}],
                      "mecaniques": "Frappe d'essai (cône frontal).", "mecaniques_en": "Trial Smash (frontal cone)."},
                     {"en": "Unnamed Horror", "butin": [], "mecaniques": "Boss de quête."}],
            "quetes": [{"en": "Trial Errand", "donneur_en": "Nobody Here", "lieu": "Val d'essai",
                        "lieu_en": "Trial Vale", "faction": "Alliance", "id": 4242, "fr": "Course d'essai",
                        "rendu": "dans le donjon : corps du frère", "rendu_en": "inside the dungeon: the brother's body",
                        "rendu_way": "10.0 20.0", "rendu_zone": "Val d'essai"},
                       {"en": "Trial Hides", "donneur_en": "Nobody Here", "lieu": "Val d'essai", "faction": "Alliance",
                        "id": 4243, "fr": "Peaux d'essai", "objectif": "rapporter 4 Peaux de raptor d'essai",
                        "objectif_en": "bring 4 Trial Raptor Hides", "rendu": "Tanneur d'essai, Port d'essai",
                        "rendu_way": "1.0 2.0", "prerequis": {"en": "Young Trial Skins", "id": 4300}},
                       {"en": "Horde Errand", "donneur_en": "", "lieu": "ailleurs", "lieu_en": "elsewhere",
                        "faction": "Horde"}],
        }
    },
}


def fixture_db():
    db = json.loads((FIXTURES / "character.json").read_text(encoding="utf-8"))
    db.setdefault("quests", {}).setdefault("list", []).append({"id": 4242, "title": "Course d'essai",
                                                               "complete": True,
                                                               "position": {"mapId": 1437, "x": 48.2, "y": 56.5}})
    db["questsCompleted"] = {"ids": [4300]}
    return db


def _insert(con, table, **values):
    cols = [r[1] for r in con.execute(f"PRAGMA table_info({table})")]
    row = {c: None for c in cols}
    row.update(values)
    con.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                [row[c] for c in cols])


class DungeonLootTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.db_path = base / "gamedata" / "forever-frFR.sqlite"
        SY.make_db_with_questie(cls.db_path)
        con = sqlite3.connect(str(cls.db_path))
        # boss d'une instance que QuestieDB ne rattache à aucune zone : retrouvé par le nom de la rencontre
        _insert(con, "q_npcs", id=9100, name="Silent Warden", name_loc="Gardien muet",
                name_norm="silent warden|gardien muet", rank=1, friendly="")
        _insert(con, "q_items", id=1001, name="Trial Helm", npc_drops=json.dumps([9100]))
        # objet fabriqué sans source QuestieDB : nom anglais déduit du patron (même id dans les deux langues)
        _insert(con, "items", id=1010, name="Patron : Ceinture fabriquée", name_norm="patron ceinture fabriquee",
                quality=1, ilvl=22, req_level=0, class_id=9, inventory_type=0, origin="client")
        _insert(con, "q_items", id=1010, name="Pattern: Crafted Belt")
        # prérequis d'une quête de guide (Young Crocolisk Skins → Highland Hides, en version d'essai)
        _insert(con, "q_quests", id=4300, name="Young Trial Skins", name_loc="Jeunes peaux d'essai",
                name_norm="jeunes peaux d essai", level=20)
        con.commit()
        con.close()
        cls.guide_path = base / "donjons.json"
        cls.guide_path.write_text(json.dumps(GUIDE, ensure_ascii=False), encoding="utf-8")
        DG.PATH = cls.guide_path
        DG._CACHE.clear()
        cls.old_env = os.environ.get("FOREVER_GAMEDB")
        os.environ["FOREVER_GAMEDB"] = str(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        DG.PATH = REAL_GUIDES
        DG._CACHE.clear()
        if cls.old_env is None:
            os.environ.pop("FOREVER_GAMEDB", None)
        else:
            os.environ["FOREVER_GAMEDB"] = cls.old_env
        cls.tmp.cleanup()

    def tools(self):
        t = server.Tools.__new__(server.Tools)
        t.store = SimpleNamespace(data_dir=Path(self.tmp.name) / "perso")
        t._gdb = None
        data = fixture_db()
        t._char = lambda args: ({}, data)
        return t

    def test_guide_loot_per_boss(self):
        out = self.tools().get_dungeon_loot({"donjon": "Crypte sans butin"})
        self.assertIn("**Butin et mécaniques par boss** [Forever · guide example.test du 14/11/2026, probable]", out)
        self.assertIn("**Gardien muet (Silent Warden)** — Frappe d'essai (cône frontal).", out)
        self.assertIn("Fusil d'essai (fusil, Distance, rare, niv. 24, id 1002)", out)  # stats de la base locale
        self.assertIn("Ghost Relic (id 999998) — absent de la base locale", out)
        self.assertIn("**Unnamed Horror** — Boss de quête.", out)
        self.assertIn("Note d'essai.", out)
        self.assertIn("Source : https://example.test/guide/lootless-crypt", out)
        self.assertNotIn("pas dans les fichiers du client", out)

    def test_loot_judged_at_required_level(self):
        out = self.tools().get_dungeon_loot({"donjon": "Crypte sans butin"})
        line = next(x for x in out.splitlines() if "Arc trop haut" in x)
        self.assertIn("→ au niveau 40 : ", line)   # chasseur 25 : jugé au niveau requis, pas « pas pour toi »
        self.assertNotIn("pas pour toi", line)

    def test_guide_quests_in_dungeon_tool(self):
        out = self.tools().tool_dungeon({"donjon": "Crypte sans butin"})
        self.assertIn("Quêtes du donjon [Forever · guide example.test du 14/11/2026, probable]", out)
        self.assertIn("*Course d'essai* (Trial Errand) ✔ à rendre — donneur : **Nobody Here** — Val d'essai", out)
        self.assertNotIn("Horde Errand", out)  # perso d'exemple Alliance

    def test_guide_turnin_distinct_from_giver(self):
        out = self.tools().tool_dungeon({"donjon": "Crypte sans butin"})
        line = next(x for x in out.splitlines() if "Course d'essai" in x and "donneur" in x)
        giver, _, turnin = line.partition("**rendu** :")
        self.assertIn("donneur : **Nobody Here** — Val d'essai", giver)
        self.assertNotIn("/way", giver)  # le lieu du donneur n'est jamais présenté comme lieu de rendu
        self.assertIn("dans le donjon : corps du frère", turnin)
        # quête finie : le point lu dans le journal du perso l'emporte sur le /way du guide
        self.assertIn("point du jeu (ton journal) : ", turnin)
        self.assertIn("`/way 48.2 56.5`", turnin)
        self.assertNotIn("10.0 20.0", turnin)

    def test_guide_objective_and_prerequisite(self):
        out = self.tools().tool_dungeon({"donjon": "Crypte sans butin"})
        line = next(x for x in out.splitlines() if "Peaux d'essai" in x)
        self.assertIn("objectif : rapporter 4 Peaux de raptor d'essai", line)
        self.assertIn("prérequis : *Jeunes peaux d'essai* (4300) ✔ faite", line)
        self.assertIn("**rendu** : Tanneur d'essai, Port d'essai ; `/way 1.0 2.0`", line)

    def test_guide_entrance_and_dangers(self):
        out = self.tools().get_dungeon_loot({"donjon": "Crypte sans butin"})
        self.assertIn("**Entrée** [Forever · example.test, other.test · probable] : en haut du sentier d'essai — "
                      "Val d'essai · `/way 48.1 56.5` ; pierre de rencontre au pied du chemin `/way 53.9 65.4`", out)
        self.assertIn("**Dangers hors boss (trash)** [Forever · example.test · probable] :", out)
        self.assertIn("- Gardien : Frappe mortelle et Filet.", out)
        import i18n as I
        with I.using("en"):
            out = self.tools().get_dungeon_loot({"donjon": "Lootless Crypt"})
        self.assertIn("**Entrance** [Forever · example.test, other.test · probable]: at the top of the trial path", out)
        self.assertIn("- Tall grass: invisible lurkers in packs of 3.", out)

    def test_english_output(self):
        import i18n as I
        with I.using("en"):
            out = self.tools().get_dungeon_loot({"donjon": "Lootless Crypt"})
        self.assertIn("**Loot and mechanics per boss** [Forever · example.test guide of 14/11/2026, probable]", out)
        self.assertIn("**Silent Warden** — Trial Smash (frontal cone).", out)
        self.assertIn("Trial note.", out)

    def test_questie_boss_by_encounter_name(self):
        t = self.tools()
        gdb = t.gamedb()
        out = t.questie_dungeon_loot(gdb, {}, ["Nulle part"], ["Gardien muet"])
        self.assertIn("**Gardien muet**", "\n".join(out))
        self.assertIn("Casque d'essai", "\n".join(out))

    def test_search_english_dungeon_item(self):
        out = self.tools().tool_search({"texte": "Trial Rifle"})
        self.assertIn("Objet de donjon : **Fusil d'essai** (Trial Rifle, id 1002) — Crypte sans butin, Gardien muet",
                      out)

    def test_search_english_crafted_item(self):
        out = self.tools().tool_search({"texte": "Crafted Belt", "type": "objet"})
        first = next(x for x in out.splitlines() if x.startswith("- "))
        self.assertIn("**Ceinture fabriquée** (id 1007", first)


class RealGuidesTest(unittest.TestCase):
    """Cohérence de knowledge/donjons.json : guides rattachés, sourcés, itemId et noms anglais présents."""

    def test_guides_well_formed(self):
        data = json.loads(REAL_GUIDES.read_text(encoding="utf-8"))
        names = {d["en"] for d in data["instances"]}
        self.assertTrue(data.get("guides"))
        for key, g in data["guides"].items():
            self.assertIn(key, names)
            self.assertTrue(str(g.get("source", "")).startswith("https://"), key)
            self.assertRegex(g.get("date", ""), r"^\d{4}-\d{2}-\d{2}$")
            self.assertIn(g.get("certitude"), ("sûr", "probable", "à vérifier"))
            seen = set()
            for b in g["boss"]:
                self.assertTrue(b.get("en") and b.get("mecaniques"), key)
                for it in b.get("butin") or []:
                    self.assertIsInstance(it["id"], int)
                    self.assertTrue(it["en"])
                    self.assertNotIn(it["id"], seen)
                    seen.add(it["id"])
            for q in g.get("quetes") or []:
                self.assertTrue(q.get("en") and q.get("faction"), key)
                pre = q.get("prerequis")
                if pre is not None:
                    self.assertIsInstance(pre.get("id"), int, q["en"])
            for block in ("entree", "dangers"):
                if block in g:
                    self.assertTrue(g[block].get("sources"), key)
                    self.assertIn(g[block].get("certitude"), ("sûr", "probable", "à vérifier"))
                    for u in g[block]["sources"]:
                        self.assertTrue(u.startswith("https://"), u)

    def test_excavation_quests_fixed(self):
        """Erreurs relevées en jeu : Highland Hides demande des peaux de raptor des fourrés (pas de crocilisque,
        c'est son prérequis 484) ; Songblade Search se rend dans le donjon, pas chez le donneur des Carmines."""
        data = json.loads(REAL_GUIDES.read_text(encoding="utf-8"))
        g = data["guides"]["Excavation Site: Wetlands"]
        q = {x["en"]: x for x in g["quetes"]}
        hides = q["Highland Hides"]
        self.assertNotIn("crocilisque", json.dumps(hides, ensure_ascii=False).replace("Young Crocolisk", ""))
        self.assertIn("raptor des fourrés", hides["objectif"])
        self.assertEqual(hides["prerequis"]["id"], 484)
        song = q["Songblade Search"]
        self.assertIn("donjon", song["rendu"])
        self.assertNotIn("Carmines", song["rendu"])
        self.assertTrue(g["entree"]["way"] and g["dangers"]["liste"])


if __name__ == "__main__":
    unittest.main()
