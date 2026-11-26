"""Outil `market` et historique des prix HV (prices.py, sync.py).

Tout est inventé : base SQLite minimale (schéma de gamedata/build.py), relevés HV fictifs, perso fictif
Brannok (Nain Chasseur 25, compte 123456789#1, GUID Player-1234-0A1B2C3D) et un second perso fictif.
"""
import json
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")  # jamais de réseau dans les tests
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MCP = HERE.parent
sys.path.insert(0, str(MCP))
sys.path.insert(0, str(MCP.parent))

import formats as F  # noqa: E402
import gamedb as GDB  # noqa: E402
import i18n as I  # noqa: E402
import market as M  # noqa: E402
import prices as PR  # noqa: E402
import professions_plan as PP  # noqa: E402
import server  # noqa: E402
import sync  # noqa: E402
from gamedata import build as B  # noqa: E402
from gamedata import questie as Q  # noqa: E402
from gamedata import recipe_colors as RC  # noqa: E402
from questdb_tools import QuestDBToolsMixin  # noqa: E402

ACC = "123456789#1"
GUID = "Player-1234-0A1B2C3D"
REALM = "CAMWOW EU4 Realm 6 PvP"
DAY = 86400


def item(iid, name, cls=7, sub=0, sell=10, buy=40, quality=1, req=1, inv=None, armor=None, agi=None, sta=None,
         item_set=None):
    row = [None] * 36
    row[0], row[1], row[2], row[3], row[4], row[5] = iid, name, B.norm(name), quality, max(req + 5, 5), req
    row[6], row[7], row[9], row[12], row[18], row[19] = cls, sub, inv, armor, agi, sta
    stats = {k: v for k, v in (("agi", agi), ("sta", sta)) if v}
    row[25], row[26] = json.dumps(stats) if stats else None, -1
    row[28], row[29], row[30], row[35] = sell, buy, item_set, "client"
    return row


ITEMS = [
    item(9001, "Cuir d'essai", 7, 6, sell=10, buy=0),
    item(9002, "Fil d'essai", 7, 0, sell=25, buy=100),
    item(9003, "Bottes d'essai", 4, 2, sell=300, quality=2, req=20, inv=8, armor=40, agi=5, sta=3, item_set=77),
    item(9004, "Gants d'essai", 4, 2, sell=200, quality=2, req=22, inv=10, armor=30, agi=4, item_set=77),
    item(9005, "Cape d'essai", 4, 1, sell=150, quality=2, req=18, inv=16, armor=10, sta=4),
]
# (sort, nom, objet fabriqué, rang, composants) ; couleurs Classic : (sort, jaune, grise)
RECIPES = [
    (6101, "Bottes d'essai", 9003, 100, [(9001, 4), (9002, 1)]),
    (6102, "Gants d'essai", 9004, 100, [(9001, 2), (9002, 2)]),
    (6103, "Cape d'essai", 9005, 90, [(9001, 3)]),
]
COLORS = [(6101, 115, 135, 0), (6102, 120, 140, 0), (6103, 110, 130, 0)]


def make_db(path):
    con = sqlite3.connect(path)
    con.executescript(B.SCHEMA)
    con.executescript(Q.SCHEMA)
    con.executescript(RC.SCHEMA)
    con.executemany("INSERT INTO meta VALUES (?,?)", [("build", "0.0.0.1"), ("locale", "frFR")])
    con.executemany("INSERT INTO professions VALUES (?,?,?,?)",
                    [(165, "Travail du cuir", "travail du cuir", 11), (393, "Dépeçage", "depecage", 11)])
    con.executemany("INSERT INTO zones VALUES (?,?,?,?,?)", [(1, "Val d'essai", "val d essai", 0, 0)])
    con.executemany(f"INSERT INTO items VALUES ({','.join('?' * 36)})", ITEMS)
    names = {r[0]: r[1] for r in ITEMS}
    con.executemany("INSERT INTO recipes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
        (sid, 165, name, B.norm(name), rank, None, None, None, 1, 0, made, 1,
         json.dumps([{"item_id": i, "count": c, "name": names[i]} for i, c in reag], ensure_ascii=False),
         "client", rank, "client") for sid, name, made, rank, reag in RECIPES])
    con.executemany("INSERT INTO recipe_colors VALUES (?,?,?,?)", COLORS)
    con.execute("INSERT INTO q_npcs (id, name, name_norm, subname, zone_id, friendly, npc_flags, spawn_count) "
                "VALUES (504, 'Marchand Delta', 'marchand delta', 'Fournitures', 1, 'A', 6, 1)")
    con.execute("INSERT INTO q_spawns VALUES ('npc', 504, 1, 11.0, 21.0)")
    con.execute("INSERT INTO q_items (id, name, npc_drops, vendors) VALUES (9002, 'Trial Thread', NULL, '[504]')")
    con.commit()
    con.close()


def character(name, guid, cls_file, cls, level, profs=None, recipes=None, bags=None):
    return {"meta": {"guid": guid, "locale": "frFR"}, "identity": {"name": name, "guid": guid, "realm": REALM, "faction": "Alliance",
                                                 "classFile": cls_file, "class": cls, "level": level,
                                                 "suffix": "Durn", "region": "EU"},
            "progression": {"level": level}, "position": {"zone": "Val d'essai"},
            "professions": {"professions": profs or []}, "recipes": recipes or {},
            "bags": {"containers": {"0": {"items": bags or []}}}, "equipment": {"slots": {}}}


BRANNOK = character(
    "Brannok", GUID, "HUNTER", "Chasseur", 25,
    profs=[{"name": "Travail du cuir", "skillLineId": 165, "rank": 106, "max": 150, "slot": "primary1"},
           {"name": "Dépeçage", "skillLineId": 393, "rank": 141, "max": 150, "slot": "primary2"}],
    recipes={"Travail du cuir": {"professionId": 165, "capturedAt": 1794937957, "recipes": [
        {"name": "Bottes d'essai", "learned": True, "difficulty": 0},
        {"name": "Gants d'essai", "learned": True, "difficulty": 0}]}},
    bags=[{"itemId": 9001, "count": 50, "classId": 7, "subclassId": 6}])
SECOND = character("Brindille", "Player-1234-0B2C3D4E", "MAGE", "Mage", 22)


def scan(prices, t):
    return {"lastScan": t, "items": {iid: {"min": p, "med": p + 5, "n": 3, "qty": 20, "t": t}
                                     for iid, p in prices.items()}}


class TestHistory(unittest.TestCase):
    def test_one_entry_per_day_latest_wins_and_pruning(self):
        now = time.time()
        hist = {}
        self.assertTrue(PR.merge_scan(hist, scan({9001: 30}, int(now - 2 * DAY)), now))
        self.assertTrue(PR.merge_scan(hist, scan({9001: 12}, int(now - 70 * DAY)), now))  # trop vieux : élagué
        early, late = int(now - 3600 * 2), int(now - 3600)
        if PR.day_of(early) != PR.day_of(late):
            early = late - 60
        PR.merge_scan(hist, scan({9001: 25}, late), now)
        self.assertFalse(PR.merge_scan(hist, scan({9001: 99}, early), now))  # plus ancien le même jour : ignoré
        days = hist["items"]["9001"]
        self.assertEqual(len(days), 2)
        self.assertEqual(days[PR.day_of(late)]["min"], 25)
        m = PR.Market(hist, now)
        self.assertEqual(m.buy(9001), 25)
        self.assertEqual(m.sell_net(9001), int(25 * 0.95))
        self.assertEqual(m.trend(9001)[1], 2)
        self.assertLess(m.age_days(9001), 1)

    def test_merge_files_shared_by_realm_and_faction(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            self.assertEqual(PR.merge_auction(data, None), [])
            t = int(time.time())
            PR.merge_auction(data, {f"{REALM}|Alliance": scan({9001: 30}, t)})
            PR.merge_auction(data, {f"{REALM}|Alliance": scan({9002: 90}, t), f"{REALM}|Horde": scan({9001: 1}, t)})
            files = sorted(p.name for p in (data / "prix").iterdir())
            self.assertEqual(files, [f"{REALM}-Alliance.json", f"{REALM}-Horde.json"])
            h = PR.load(data, REALM, "Alliance")
            self.assertEqual(set(h["items"]), {"9001", "9002"})
            self.assertEqual(PR.load(data, "CAMWOWEU4Realm6PvP", "Alliance")["realm"], REALM)
            guessed = PR.load(data, "", "Alliance")  # royaume absent de la capture
            self.assertTrue(guessed.get("realmGuessed"))

    def test_sync_reads_account_auction(self):
        with tempfile.TemporaryDirectory() as tmp:
            wow = Path(tmp) / "World of Warcraft" / "_forever_"
            t = int(time.time()) - 60
            for acc in (ACC, "123456789#2"):
                sv = wow / "WTF" / "Account" / acc / "SavedVariables"
                sv.mkdir(parents=True)
                iid = 9001 if acc == ACC else 9002
                sv.joinpath("ForeverScribe.lua").write_text(
                    'ForeverScribeDB = {\n\t["auction"] = {\n\t\t["%s|Alliance"] = {\n\t\t\t["lastScan"] = %d,\n'
                    '\t\t\t["items"] = {\n\t\t\t\t[%d] = { ["min"] = 21, ["med"] = 35, ["n"] = 28, ["qty"] = 410, '
                    '["t"] = %d },\n\t\t\t},\n\t\t},\n\t},\n}\n' % (REALM, t, iid, t), encoding="utf-8")
            data = Path(tmp) / "perso"
            data.mkdir()
            (data / "config.json").write_text(json.dumps({"wowPaths": [str(wow.parent)]}), encoding="utf-8")
            rep = sync.sync(data)
            self.assertIn(f"{REALM}-Alliance.json", rep.get("prices", []))
            h = PR.load(data, REALM, "Alliance")
            self.assertEqual(set(h["items"]), {"9001", "9002"})  # deux comptes, un seul fichier
            self.assertEqual(h["items"]["9001"][PR.day_of(t)], {"min": 21, "med": 35, "qty": 410, "n": 28, "t": t})
            self.assertNotIn("prices", sync.sync(data))  # rien de neuf : pas de réécriture


class FakeTools(QuestDBToolsMixin):
    pass


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.dbp = root / "gamedata" / "forever-frFR.sqlite"
        cls.dbp.parent.mkdir()
        make_db(cls.dbp)
        cls.gdb = GDB.GameDB(cls.dbp)
        cls.data = root / "perso"
        chars = {}
        for db in (BRANNOK, SECOND):
            name = db["identity"]["name"]
            folder = cls.data / "Alex" / f"{name}-EU"
            folder.mkdir(parents=True)
            (folder / "etat.json").write_text(json.dumps({"schema": 1, "data": db}), encoding="utf-8")
            chars[db["identity"]["guid"]] = {"user": "Alex", "account": ACC, "folder": f"{name}-EU", "name": name,
                                             "captured": True, "lastCapture": 1794937957 - len(chars)}
        (cls.data / "config.json").write_text(json.dumps({"accounts": {ACC: "Alex"}, "characters": chars}),
                                              encoding="utf-8")
        cls._env = os.environ.get("FOREVER_GAMEDB")
        os.environ["FOREVER_GAMEDB"] = str(cls.dbp)
        cls.tools = server.Tools(sync.Store(cls.data))

    @classmethod
    def tearDownClass(cls):
        if cls._env is None:
            os.environ.pop("FOREVER_GAMEDB", None)
        else:
            os.environ["FOREVER_GAMEDB"] = cls._env
        cls.gdb.con.close()
        if cls.tools._gdb is not None:
            cls.tools._gdb.con.close()
        cls.tmp.cleanup()

    def set_prices(self, prices, days_ago=1):
        folder = self.data / "prix"
        if folder.exists():
            for p in folder.iterdir():
                p.unlink()
        if prices:
            PR.merge_auction(self.data, {f"{REALM}|Alliance": scan(prices, int(time.time() - days_ago * DAY))})

    def run_tool(self, **args):
        lang = self.tools.prepare(args)
        with I.using(lang):
            return self.tools.tool_market(args)

    def catalog(self, prices=None):
        market = PR.Market({"items": {str(k): {PR.day_of(time.time()): {"min": v, "t": int(time.time())}}
                                      for k, v in (prices or {}).items()}})
        return M.MarketCatalog(FakeTools(), self.gdb, 165, PP.Place(FakeTools(), self.gdb, BRANNOK), market)


class TestCosts(Base):
    def test_unit_cost_cheapest_source_and_resale(self):
        cat = self.catalog()
        self.assertEqual(cat.unit_cost(9002), (100.0, True))
        self.assertEqual(cat.source(9002), "marchand")
        self.assertFalse(cat.unit_cost(9001)[1])              # ni marchand ni HV : inconnu
        self.assertEqual(cat.resale(9004), (200, "marchand"))
        cat = self.catalog({9002: 60, 9001: 5, 9004: 2000})
        self.assertEqual(cat.unit_cost(9002), (60.0, True))    # HV moins cher que le marchand
        self.assertEqual(cat.source(9002), "hv")
        self.assertEqual(cat.resale(9004), (1900, "hv"))       # 2000 − 5 % de commission

    def test_cost_per_point_counts_resale_and_stock(self):
        # cuir cher : Cape (3 cuirs − 150 de revente) = 150 net par point, Bottes et Gants 200
        segs = M.plan_cheapest(self.catalog({9001: 100}), 106, 110, {})
        self.assertEqual(segs[0]["rec"]["name"], "Cape d'essai")
        self.assertAlmostEqual(segs[0]["buy"] - segs[0]["resale"], 4 * 150)
        # Gants revendus 2000 à l'HV : ils se remboursent, choisis
        segs = M.plan_cheapest(self.catalog({9001: 100, 9004: 2000}), 106, 110, {})
        self.assertEqual([s["rec"]["name"] for s in segs], ["Gants d'essai"])
        self.assertAlmostEqual(segs[0]["buy"], 4 * (2 * 100 + 2 * 100))
        # cuir en sacs : gratuit, seuls les composants hors stock sont achetés
        segs = M.plan_cheapest(self.catalog({9001: 100}), 106, 110, {9001: 50})
        rec = segs[0]["rec"]
        extra = sum(g["count"] * 100 for g in rec["reagents"] if g["item_id"] == 9002)
        self.assertAlmostEqual(segs[0]["buy"], 4 * extra)


class TestTool(Base):
    def test_without_prices(self):
        self.set_prices({})
        out = self.run_tool(perso="Brannok", cible=110)
        self.assertIn("Aucun prix HV relevé", out)
        self.assertIn("**À chercher à l'HV en priorité**", out)
        self.assertIn("Cuir d'essai (id 9001)", out)
        self.assertIn("prix marchands seulement", out)
        self.assertNotIn("HV 2", out)           # aucun prix HV daté : jamais inventé
        self.assertNotIn("tes relevés HV", out)
        self.assertIn("pièce (marchand)", out)    # revente marchand, base locale
        self.assertIn("déjà en sacs", out)        # cuir en stock

    def test_with_prices_profit_net_of_cut(self):
        self.set_prices({9001: 5, 9004: 2000, 9003: 900})
        out = self.run_tool(perso="Brannok", cible=110)
        day = M.price_day(PR.day_of(time.time() - DAY))
        self.assertIn(f"[Forever · tes relevés HV du {day}]", out)
        # Gants : vend 2000 − 5 % = 1900, coûte 2 × 5 + 2 × 100 = 210 → 1690
        self.assertIn("Gants d'essai (connue) : vend 19 pa 0 pc, coûte 2 pa 10 pc → **16 pa 90 pc**", out)
        self.assertIn("meilleure vente : Gants d'essai", out)
        self.assertIn("**Vendre brut ou fabriquer ?**", out)
        self.assertIn("Cuir d'essai ×50 : **fabriquer Gants d'essai**", out)
        self.assertNotIn("⚠", out)

    def test_old_prices_flagged(self):
        self.set_prices({9001: 5, 9004: 2000}, days_ago=5)
        out = self.run_tool(perso="Brannok", vue="profit")
        self.assertIn("⚠ relevé de plus de 3 jours", out)
        self.assertIn("⚠5 j", out)

    def test_gear_for_self_and_secondary_character(self):
        self.set_prices({9003: 900})
        out = self.run_tool(perso="Brannok", vue="equipement")
        self.assertIn("**Équipement fabricable pour Brannok**", out)
        self.assertIn("Bottes d'essai", out)
        self.assertIn("**pièce d'ensemble** (autres pièces : Gants d'essai)", out)
        self.assertIn("faisable", out)
        out = self.run_tool(perso="Brannok", pour="Brindille", vue="equipement")
        self.assertIn("**Équipement fabricable pour Brindille**", out)
        self.assertIn("Cape d'essai", out)       # tissu (cape) : portable par un mage
        self.assertNotIn("Bottes d'essai", out)  # cuir : pas pour un mage

    def test_bags_and_english(self):
        self.set_prices({9001: 5, 9004: 2000})
        out = self.run_tool(perso="Brannok", vue="sacs")
        self.assertIn("Cuir d'essai ×50 : fabriquer Gants d'essai", out)
        out = self.run_tool(perso="Brannok", vue="profit", lang="en")
        self.assertIn("**Profitability**", out)
        self.assertIn("[Forever · your AH scans of", out)

    def test_browse_view_is_a_floor_price(self):
        """n = 0 (vue de navigation de l'API moderne) : prix plancher, volume = qty seulement."""
        t = int(time.time() - DAY)
        self.set_prices({})
        PR.merge_auction(self.data, {f"{REALM}|Alliance": {"lastScan": t, "items": {
            9004: {"min": 2000, "n": 0, "qty": 3, "t": t}, 9001: {"min": 5, "med": 6, "n": 4, "qty": 80, "t": t}}}})
        out = self.run_tool(perso="Brannok", vue="profit")
        self.assertIn("3 en vente, prix plancher (vue de navigation)", out)

    def test_skilltype_from_capture_wins(self):
        """Recettes 1.5 : skillType = couleur réelle en jeu ; « trivial » (grise) exclut la recette au départ."""
        cap = M.MarketToolsMixin._market_captured(
            {"recipes": {"Travail du cuir": {"professionId": 165, "recipes": [
                {"name": "Gants d'essai", "spellId": 6102, "learned": True, "skillType": "trivial",
                 "difficulty": 0}]}}}, 165, 165, "Travail du cuir")
        self.assertEqual(cap["recipes"][0]["difficulty"], 3)
        segs = M.plan_cheapest(self.catalog({9001: 5, 9004: 2000}), 106, 107, {}, PP.captured_colors(cap))
        self.assertNotEqual(segs[0]["rec"]["name"], "Gants d'essai")
        # « easy » (verte) alors que l'estimation la dit orange : chance de point réduite
        green = M._real_colors(next(r for r in self.catalog().recipes if r["name"] == "Gants d'essai"), 106,
                               {F.norm_key("Gants d'essai"): 2})
        self.assertEqual(PP.color_at(106, green), 2)
        self.assertGreater(PP.crafts_per_point(106, green), 1.5)

    def test_bad_view_and_gathering(self):
        with self.assertRaises(server.ToolError):
            self.run_tool(perso="Brannok", vue="nimporte")
        with self.assertRaises(server.ToolError):
            self.run_tool(perso="Brannok", metier="Dépeçage")


if __name__ == "__main__":
    unittest.main()
