"""Données de test entièrement inventées (aucune donnée extraite du jeu).

`FakeTables` imite GameTables ; `make_db(path)` écrit une petite base SQLite avec
build.build_database, utilisée par les tests de gamedata et des outils MCP.
"""
import struct
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
if str(PLUGIN) not in sys.path:
    sys.path.insert(0, str(PLUGIN))

from gamedata import build  # noqa: E402

NO_STAT = [(-1, 0)] * 10


def sparse(iid, name, ilvl, req, quality, inv, stats=(), delay=0, var=0.0, allowable=-1, sell=100):
    st = list(stats) + NO_STAT[len(stats):]
    return {"ID": iid, "Display_lang": name, "ItemLevel": ilvl, "RequiredLevel": req, "OverallQualityID": quality,
            "InventoryType": inv, "StatModifier_bonusStat": [t for t, _ in st],
            "StatPercentEditor": [p for _, p in st], "ItemDelay": delay, "DmgVariance": var,
            "AllowableClass": allowable, "Bonding": 1, "SellPrice": sell, "BuyPrice": sell * 4, "ItemSet": 0,
            "StartQuestID": 0, "RequiredSkill": 0, "RequiredSkillRank": 0, "Stackable": 1}


ITEMS = {
    1001: (sparse(1001, "Casque d'essai", 30, 25, 2, 1, [(3, 5000), (7, 5000)]), (4, 2)),
    1002: (sparse(1002, "Fusil d'essai", 30, 24, 3, 26, [(3, 10000)], delay=2000, var=0.5), (2, 3)),
    1003: (sparse(1003, "Bottes [PÉRIMÉ] d'essai", 30, 20, 3, 8, [(3, 10000)]), (4, 2)),
    1004: (sparse(1004, "Arc trop haut", 30, 40, 3, 15, [(3, 10000)], delay=2000, var=0.5), (2, 2)),
    1005: (sparse(1005, "Gants de mailles d'essai", 30, 20, 2, 10, [(3, 10000)]), (4, 3)),
    1006: (sparse(1006, "Cuir d'essai", 10, 0, 1, 0), (7, 6)),
    1007: (sparse(1007, "Ceinture fabriquée", 22, 17, 2, 6, [(3, 10000)]), (4, 2)),
    1008: (sparse(1008, "Bâton de mage d'essai", 30, 20, 3, 17, [(5, 10000)], delay=3000, var=0.4, allowable=128),
           (2, 10)),
}

RANDPROP = {lvl: {"ID": lvl, "Good": [20, 15, 11, 8, 6], "Superior": [26, 20, 15, 11, 8],
                  "Epic": [32, 24, 18, 13, 10]} for lvl in (10, 22, 30)}


class FakeTables:
    def __init__(self):
        sp = {i: s for i, (s, _) in ITEMS.items()}
        it = {i: {"ID": i, "ClassID": c, "SubclassID": sc} for i, (_, (c, sc)) in ITEMS.items()}
        self._t = {
            "ItemSparse": sp, "Item": it, "RandPropPoints": RANDPROP,
            "ItemDamageRanged": {30: {"ID": 30, "Quality": [5.0, 6.0, 8.0, 10.0, 12.0, 12.0, 12.0]}},
            "ItemDamageOneHand": {}, "ItemDamageTwoHand": {30: {"ID": 30, "Quality": [8.0, 9.0, 10.0, 12.0, 14.0, 14.0, 14.0]}},
            "ItemDamageThrown": {}, "ItemDamageWand": {},
            "ItemArmorTotal": {lvl: {"ID": lvl, "Cloth": 50.0, "Leather": 200.0, "Mail": 400.0, "Plate": 800.0}
                               for lvl in (22, 30)},
            "ItemArmorQuality": {lvl: {"ID": lvl, "Qualitymod": [0.9, 0.95, 1.0, 1.1, 1.2, 1.2, 1.2]} for lvl in (22, 30)},
            "ArmorLocation": {k: {"ID": k, "Clothmodifier": m, "Leathermodifier": m, "Chainmodifier": m,
                                  "Platemodifier": m, "Modifier": m}
                              for k, m in {1: 0.1, 5: 0.2, 6: 0.05, 8: 0.08, 10: 0.07, 16: 0.04}.items()},
            "ItemArmorShield": {},
            "ItemSet": {},
            "SkillLine": {165: {"ID": 165, "DisplayName_lang": "Travail du cuir", "CategoryID": 11},
                          6: {"ID": 6, "DisplayName_lang": "Givre", "CategoryID": 7}},
            "SkillLineAbility": {1: {"ID": 1, "SkillLine": 165, "Spell": 5001, "MinSkillLineRank": 1,
                                     "TrivialSkillLineRankLow": 0, "TrivialSkillLineRankHigh": 0,
                                     "NumSkillUps": 1, "AcquireMethod": 0},
                                 2: {"ID": 2, "SkillLine": 6, "Spell": 5002, "MinSkillLineRank": 1}},
            "SpellEffect": {1: {"ID": 1, "SpellID": 5001, "Effect": 24, "EffectItemType": 1007,
                                "EffectBasePointsF": 1.0, "DifficultyID": 0}},
            "SpellReagents": {1: {"ID": 1, "SpellID": 5001, "Reagent": [1006, 0, 0, 0, 0, 0, 0, 0],
                                  "ReagentCount": [4, 0, 0, 0, 0, 0, 0, 0]}},
            "SpellName": {5001: {"ID": 5001, "Name_lang": "Ceinture fabriquée"},
                          5002: {"ID": 5002, "Name_lang": "Éclair de givre d'essai"}},
            "SpellLevels": {1: {"ID": 1, "SpellID": 5002, "SpellLevel": 4, "BaseLevel": 4, "DifficultyID": 0}},
            "AreaTable": {1: {"ID": 1, "AreaName_lang": "Val d'essai", "ParentAreaID": 0, "ContinentID": 0}},
            "Map": {9001: {"ID": 9001, "MapName_lang": "Donjon d'essai", "InstanceType": 1, "MaxPlayers": 5},
                    9002: {"ID": 9002, "MapName_lang": "Crypte sans butin", "InstanceType": 1, "MaxPlayers": 5},
                    0: {"ID": 0, "MapName_lang": "Continent", "InstanceType": 0}},
            "DungeonEncounter": {7001: {"ID": 7001, "MapID": 9001, "Name_lang": "Boss d'essai", "OrderIndex": 0},
                                 7002: {"ID": 7002, "MapID": 9002, "Name_lang": "Gardien muet", "OrderIndex": 0}},
            "QuestV2": {1: {"ID": 1}, 2: {"ID": 2}},
            "ChrClasses": {},
            "JournalInstance": {1: {"ID": 1, "MapID": 9001}},
            "JournalEncounter": {1: {"ID": 1, "JournalInstanceID": 1, "DungeonEncounterID": 7001}},
            "JournalEncounterItem": {1: {"ID": 1, "JournalEncounterID": 1, "ItemID": 1001}},
        }
        self.stats = {n: {"client": len(t), "added": 0, "replaced": 0, "removed": 0, "undecodable": 0,
                          "total": len(t)} for n, t in self._t.items()}
        self.origins = {"ItemSparse": {1001: "ajoute"}}
        self.hotfix_header = {"build": 1, "entries": 1}

    def get(self, name):
        return self._t[name]


QUEST_CACHE = {1: ("Quête d'essai", "Tuer 5 loups d'essai.", "")}


def make_db(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return build.build_database(FakeTables(), path, QUEST_CACHE,
                                {"schema_version": build.SCHEMA_VERSION, "fingerprint": "test", "build": "0.0.0.1",
                                 "locale": "frFR", "built_at": "2026-01-01T00:00:00"})


# --- DBCache.bin synthétique --------------------------------------------------------
def dbcache_bytes(entries, build_no=1):
    """entries : [(push, hash_table, record_id, statut, données)]."""
    out = bytearray(b"XFTH" + struct.pack("<II", 9, build_no) + bytes(32))
    for i, (push, thash, rid, status, body) in enumerate(entries):
        out += struct.pack("<4siiIIIII", b"XFTH", 1, push, i + 1, thash, rid, len(body), status) + body
    return bytes(out)


# --- questcache.wdb synthétique -----------------------------------------------------
def _pack_bits(fields):
    bits = "".join(format(v, f"0{n}b") for v, n in fields)
    bits += "0" * (-len(bits) % 8)
    return int(bits, 2).to_bytes(len(bits) // 8, "big")


def quest_record(title, objectives, description=""):
    t, o, d = (s.encode("utf-8") for s in (title, objectives, description))
    pack = _pack_bits([(len(t), 9), (len(o), 12), (len(d), 12), (0, 9), (0, 10), (0, 8), (0, 10), (0, 8), (0, 11)])
    pack = pack.ljust(12, b"\0")[:12]
    return b"\x05\x00\x00\x00" * 6 + pack + t + o + d


def questcache_bytes(records):
    out = bytearray(b"TSQW" + struct.pack("<I", 1) + b"RFrf" + struct.pack("<II", 0, 12) + bytes(4))
    for qid, body in records.items():
        out += struct.pack("<II", qid, len(body)) + body
    return bytes(out)
