"""Données de test entièrement inventées (aucune donnée extraite du jeu).

`FakeTables` imite GameTables ; `make_db(path, locale)` écrit une petite base SQLite avec
build.build_database, utilisée par les tests de gamedata et des outils MCP. Avec locale="enUS",
les noms (objets, sorts, métiers, donjons, quêtes) sont en anglais, comme sur un client anglais.
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

# Noms d'un client anglais (mêmes IDs) — inventés eux aussi
EN_NAMES = {
    1001: "Trial Helm", 1002: "Trial Rifle", 1003: "Boots [DEPRECATED] of Trial", 1004: "Bow Too High",
    1005: "Trial Mail Gloves", 1006: "Trial Leather", 1007: "Crafted Belt", 1008: "Trial Mage Staff",
    1009: "Humbert's Trial Helm",
}
EN_OTHER = {"spell": {5001: "Crafted Belt", 5002: "Trial Frostbolt"}, "skill": {165: "Leatherworking", 6: "Frost"},
            "area": {1: "Trial Vale"}, "map": {9001: "Trial Dungeon", 9002: "Lootless Crypt", 0: "Continent"},
            "boss": {7001: "Trial Boss", 7002: "Silent Warden"}}
ITEMS_EN_ONLY = {1009: (sparse(1009, "Humbert's Trial Helm", 30, 24, 3, 1, [(3, 6000), (7, 4000)]), (4, 2))}

RANDPROP = {lvl: {"ID": lvl, "Good": [20, 15, 11, 8, 6], "Superior": [26, 20, 15, 11, 8],
                  "Epic": [32, 24, 18, 13, 10]} for lvl in (10, 22, 30)}


class FakeTables:
    def __init__(self, locale="frFR"):
        items = dict(ITEMS)
        if locale != "frFR":
            items.update(ITEMS_EN_ONLY)
        sp = {i: dict(s, Display_lang=EN_NAMES.get(i, s["Display_lang"])) if locale != "frFR" else s
              for i, (s, _) in items.items()}
        it = {i: {"ID": i, "ClassID": c, "SubclassID": sc} for i, (_, (c, sc)) in items.items()}
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
            "LevelExperience": {i: {"ID": i, "Level": i, "ContentSetID": 0, "Experience": 1000 * i}
                                for i in range(1, 31)},
        }
        self.stats = {n: {"client": len(t), "added": 0, "replaced": 0, "removed": 0, "undecodable": 0,
                          "total": len(t)} for n, t in self._t.items()}
        self.origins = {"ItemSparse": {1001: "ajoute"}}
        self.hotfix_header = {"build": 1, "entries": 1}
        if locale != "frFR":
            for sid, n in EN_OTHER["spell"].items():
                self._t["SpellName"][sid]["Name_lang"] = n
            for sid, n in EN_OTHER["skill"].items():
                self._t["SkillLine"][sid]["DisplayName_lang"] = n
            for aid, n in EN_OTHER["area"].items():
                self._t["AreaTable"][aid]["AreaName_lang"] = n
            for mid, n in EN_OTHER["map"].items():
                self._t["Map"][mid]["MapName_lang"] = n
            for eid, n in EN_OTHER["boss"].items():
                self._t["DungeonEncounter"][eid]["Name_lang"] = n

    def get(self, name):
        return self._t[name]


QUEST_CACHE = {1: ("Quête d'essai", "Tuer 5 loups d'essai.", "")}
QUEST_CACHE_EN = {1: ("Trial Quest", "Kill 5 Trial Wolves.", "")}


def make_db(path, locale="frFR"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return build.build_database(FakeTables(locale), path, QUEST_CACHE if locale == "frFR" else QUEST_CACHE_EN,
                                {"schema_version": build.SCHEMA_VERSION, "fingerprint": "test", "build": "0.0.0.1",
                                 "locale": locale, "built_at": "2026-01-01T00:00:00"})


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


# --- QuestieDB synthétique (format des fichiers de Questie, contenu inventé) ---------
ALLIANCE_RACES = 1 + 4 + 8 + 64 + (1 << 32)
HORDE_RACES = 2 + 16 + 32 + 128 + (1 << 33)
# quêtes : name, startedBy, finishedBy, requiredLevel, questLevel, requiredRaces, requiredClasses,
# objectivesText, triggerEnd, objectives, sourceItemId, preQuestGroup, preQuestSingle, childQuests,
# inGroupWith, exclusiveTo, zoneOrSort, requiredSkill, requiredMinRep, requiredMaxRep,
# requiredSourceItems, nextQuestInChain, questFlags, specialFlags, parentQuest, reputationReward
QUESTIE_QUESTS = f"""
[19] = {{"Old Trial",{{{{501}}}},{{{{501}}}},1,5,{ALLIANCE_RACES},nil,{{"Done long ago."}},nil,nil,nil,nil,nil,nil,nil,nil,1}},
[101] = {{"Trial Hunt",{{{{501}}}},{{{{502}}}},8,10,{ALLIANCE_RACES},nil,{{"Kill Trial Wolves and bring 5 Trial Fangs."}},{{"Scout the Trial Ridge",{{[1]={{{{55.5,66.6}}}}}}}},{{{{{{503,nil}}}},nil,{{{{2001}}}}}},nil,nil,nil,nil,nil,nil,1,nil,nil,nil,nil,nil,8,2,nil,{{{{72,250}}}}}},
[102] = {{"Trial Follow-up",{{{{502}}}},{{{{502}}}},9,11,{ALLIANCE_RACES},nil,{{"Report back."}},nil,nil,nil,nil,{{101}},nil,nil,nil,1}},
[103] = {{"Horde Trial",{{{{501}}}},{{{{501}}}},8,10,{HORDE_RACES},nil,{{"For the Horde."}},nil,nil,nil,nil,nil,nil,nil,nil,1}},
[104] = {{"Trial Letter",{{nil,nil,{{2002}}}},{{nil,{{601}}}},8,9,0,nil,{{"Open the Trial Chest."}},nil,nil,2002,nil,nil,nil,nil,nil,1}},
[105] = {{"Trial Festival",{{{{504}}}},{{{{504}}}},1,10,0,nil,{{"Celebrate."}},nil,nil,nil,nil,nil,nil,nil,nil,-22}},
[106] = {{"Trial Peak",{{{{501}}}},{{{{501}}}},30,32,0,nil,{{"Much later."}},nil,nil,nil,nil,nil,nil,nil,nil,1}},
"""
# PNJ : name, minLevelHealth, maxLevelHealth, minLevel, maxLevel, rank, spawns, waypoints, zoneID,
# questStarts, questEnds, factionID, friendlyToFaction, subName, npcFlags
QUESTIE_NPCS = """
[501] = {'Trial Giver',100,100,20,20,0,{[1]={{10.0,20.0}}},nil,1,{19,101,103,106},{19,103,106},12,"A","Trial Master",2},
[502] = {'Trial Receiver',100,100,20,20,0,{[1]={{12.5,22.5}}},nil,1,{102},{101,102},12,"A",nil,2},
[503] = {'Trial Wolf',80,90,7,8,0,{[1]={{40.0,40.0},{41.0,41.0},{42.0,40.0},{70.0,90.0}},[2]={{5.0,5.0}}},nil,1,nil,nil,32,nil,nil,0},
[504] = {'Festival Giver',100,100,20,20,0,{[1]={{30.0,30.0}}},nil,1,{105},{105},12,"AH",nil,2},
"""
QUESTIE_OBJECTS = """
[601] = {"Trial Chest",nil,{104},{[1]={{80.0,10.0}}},1},
"""
# objets : name, npcDrops, objectDrops, itemDrops, startQuest, questRewards, flags, foodType, itemLevel,
# requiredLevel, ammoType, class, subClass, vendors, relatedQuests
QUESTIE_ITEMS = """
[2001] = {'Trial Fang',{503},nil,nil,nil,nil,nil,nil,1,0,0,12,0},
[2002] = {'Trial Letter',{503},nil,nil,104,nil,nil,nil,1,0,0,12,0},
[2003] = {'Plain Thing',nil,nil,nil,nil,nil,nil,nil,1,0,0,12,0},
"""
QUESTIE_L10N_FR = {
    "quests": """
[101] = {"Chasse d'essai", {"Tuer des loups d'essai et rapporter 5 crocs d'essai."}},
[102] = {"Suite d'essai", {"Faire votre rapport."}},
""",
    "npcs": """
[501] = {"Donneur d'essai","Maître d'essai"},
[503] = {"Loup d'essai",nil},
""",
    "objects": """
[601] = "Coffre d'essai",
""",
}


def _questie_lua(module, marker, body):
    return (f"-- fichier de test (format QuestieDB, contenu inventé)\nlocal QuestieDB = QuestieLoader:ImportModule"
            f"(\"{module}\");\n\n{marker} = [[return {{{body}}}]]\n")


def write_questie(cache_dir, locale="frFR", commit="testcommit"):
    """Écrit des fichiers QuestieDB synthétiques là où questie.fetch les cherche (mode hors ligne)."""
    from gamedata import questie as Q

    root = Path(cache_dir) / "questie" / commit
    root.mkdir(parents=True, exist_ok=True)
    data = {"quests": ("QuestieDB.questData", QUESTIE_QUESTS), "npcs": ("QuestieDB.npcData", QUESTIE_NPCS),
            "objects": ("QuestieDB.objectData", QUESTIE_OBJECTS), "items": ("QuestieDB.itemData", QUESTIE_ITEMS)}
    for key, (marker, body) in data.items():
        (root / Q.DATA_FILES[key].replace("/", "__")).write_text(_questie_lua("QuestieDB", marker, body),
                                                                encoding="utf-8")
    if locale == "frFR":
        markers = {"quests": 'l10n.questLookup["frFR"] = loadstring(', "npcs": 'l10n.npcNameLookup["frFR"] = loadstring(',
                   "objects": 'l10n.objectLookup["frFR"] = loadstring('}
        for key, marker in markers.items():
            text = (f'if GetLocale() ~= "frFR" then\n    return\nend\n{marker}[[return {{{QUESTIE_L10N_FR[key]}}}]])\n')
            (root / Q.L10N_FILES[key].format(locale=locale).replace("/", "__")).write_text(text, encoding="utf-8")
    return root


def make_db_with_questie(path, locale="frFR"):
    """Base synthétique + tables QuestieDB synthétiques."""
    from gamedata import questie as Q

    path = Path(path)
    make_db(path, locale)
    cache = path.parent / ".cache"
    write_questie(cache, locale)
    files = Q.fetch(cache, locale, commit="testcommit", offline=True)
    return Q.import_into(path, files, commit="testcommit")
