"""Accès en lecture seule à la base locale du jeu (gamedata/forever-<locale>.sqlite).

La base est construite chez chaque joueur par `gamedata/build.py` à partir des fichiers de son
client WoW Forever (tables DB2 + correctifs du serveur). Ce module ne fait que la lire.
Schéma : docs/schema-gamedb.md.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

import formats as F

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
BADGE = "[Forever · base locale]"

INVTYPE = {1: "INVTYPE_HEAD", 2: "INVTYPE_NECK", 3: "INVTYPE_SHOULDER", 4: "INVTYPE_BODY", 5: "INVTYPE_CHEST",
           6: "INVTYPE_WAIST", 7: "INVTYPE_LEGS", 8: "INVTYPE_FEET", 9: "INVTYPE_WRIST", 10: "INVTYPE_HAND",
           11: "INVTYPE_FINGER", 12: "INVTYPE_TRINKET", 13: "INVTYPE_WEAPON", 14: "INVTYPE_SHIELD",
           15: "INVTYPE_RANGED", 16: "INVTYPE_CLOAK", 17: "INVTYPE_2HWEAPON", 18: "INVTYPE_BAG",
           19: "INVTYPE_TABARD", 20: "INVTYPE_ROBE", 21: "INVTYPE_WEAPONMAINHAND", 22: "INVTYPE_WEAPONOFFHAND",
           23: "INVTYPE_HOLDABLE", 24: "INVTYPE_AMMO", 25: "INVTYPE_THROWN", 26: "INVTYPE_RANGEDRIGHT",
           27: "INVTYPE_QUIVER", 28: "INVTYPE_RELIC"}

# emplacement du perso -> InventoryType possibles
SLOT_INVTYPES = {
    "HeadSlot": [1], "NeckSlot": [2], "ShoulderSlot": [3], "BackSlot": [16], "ChestSlot": [5, 20],
    "WristSlot": [9], "HandsSlot": [10], "WaistSlot": [6], "LegsSlot": [7], "FeetSlot": [8],
    "Finger0Slot": [11], "Finger1Slot": [11], "Trinket0Slot": [12], "Trinket1Slot": [12],
    "MainHandSlot": [13, 17, 21], "SecondaryHandSlot": [13, 14, 22, 23], "RangedSlot": [15, 25, 26],
}
# emplacements regroupés (un seul passage pour les deux anneaux, les deux bijoux)
UPGRADE_SLOTS = ["HeadSlot", "NeckSlot", "ShoulderSlot", "BackSlot", "ChestSlot", "WristSlot", "HandsSlot",
                 "WaistSlot", "LegsSlot", "FeetSlot", "Finger0Slot", "Trinket0Slot", "MainHandSlot",
                 "SecondaryHandSlot", "RangedSlot"]

STAT_KEYS = {"str": "STRENGTH", "agi": "AGILITY", "sta": "STAMINA", "int": "INTELLECT", "spi": "SPIRIT",
             "ap": "ATTACK_POWER", "rap": "RANGED_ATTACK_POWER", "spell_power": "SPELL_POWER",
             "healing": "HEALING_POWER", "crit": "CRIT_RATING", "hit": "HIT_RATING",
             "defense": "DEFENSE_SKILL_RATING", "dodge": "DODGE_RATING", "parry": "PARRY_RATING",
             "block": "BLOCK_RATING", "block_value": "BLOCK_VALUE", "fire_res": "FIRE_RESISTANCE",
             "frost_res": "FROST_RESISTANCE", "nature_res": "NATURE_RESISTANCE", "shadow_res": "SHADOW_RESISTANCE",
             "arcane_res": "ARCANE_RESISTANCE", "holy_res": "HOLY_RESISTANCE"}
STAT_ALIASES = {"force": "str", "agilite": "agi", "agi": "agi", "endurance": "sta", "endu": "sta",
                "intelligence": "int", "int": "int", "esprit": "spi", "pa": "ap", "puissance d attaque": "ap",
                "pa distance": "rap", "puissance des sorts": "spell_power", "crit": "crit", "critique": "crit",
                "toucher": "hit", "for": "str", "end": "sta", "esp": "spi"}
QUALITY = {0: "médiocre", 1: "commun", 2: "inhabituel", 3: "rare", 4: "épique", 5: "légendaire"}
QUALITY_ALIASES = {"gris": 0, "mediocre": 0, "blanc": 1, "commun": 1, "vert": 2, "inhabituel": 2,
                   "bleu": 3, "rare": 3, "violet": 4, "epique": 4}
CLASS_IDS = {"WARRIOR": 1, "PALADIN": 2, "HUNTER": 3, "ROGUE": 4, "PRIEST": 5, "SHAMAN": 7, "MAGE": 8,
             "WARLOCK": 9, "DRUID": 11}
ORIGIN_FR = {"client": "fichiers du jeu", "modifie": "modifié par Forever", "ajoute": "fourni par le serveur Forever",
             "cache": "cache des quêtes"}
# objets de test ou retirés du jeu, à ne jamais proposer
JUNK_MARKERS = ("[périmé]", "[perime]", "(old)", " old", "test ", "[dnt]", "deprecated", "monster -", "[ph]",
                "unused", "qa ")


def build_command() -> str:
    return f'cd "{PLUGIN_ROOT}" && python3 -m gamedata.build'


MISSING_MSG = (
    "La base locale du jeu n'est pas encore construite. Elle se construit une fois, en quelques secondes, "
    "à partir des fichiers de ton client WoW Forever (lecture seule) :\n\n    {cmd}\n\n"
    "(depuis le dépôt : python3 tools/gamedata/build_db.py). Ensuite, ces outils répondent sans recherche web."
)


def find_db_path(data_dir: Optional[Path]) -> Optional[Path]:
    env = os.environ.get("FOREVER_GAMEDB")
    if env:  # chemin imposé (tests, autre emplacement) : rien d'autre n'est cherché
        p = Path(env).expanduser()
        return p if p.is_file() else None
    roots = []
    if data_dir:
        roots.append(Path(data_dir).parent / "gamedata")
    roots.append(Path.home() / "WowForever" / "gamedata")
    for r in roots:
        for name in ("forever-frFR.sqlite",):
            if (r / name).is_file():
                return r / name
        hits = sorted(r.glob("forever-*.sqlite")) if r.is_dir() else []
        if hits:
            return hits[0]
    return None


class GameDBMissing(Exception):
    pass


class GameDB:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.con = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.meta = {r["key"]: r["value"] for r in self.con.execute("SELECT key, value FROM meta")}

    def q(self, sql: str, args: tuple = ()) -> List[sqlite3.Row]:
        return self.con.execute(sql, args).fetchall()

    def header(self) -> str:
        return (f"_{BADGE} build {self.meta.get('build', '?')}, base construite le "
                f"{(self.meta.get('built_at') or '?')[:10]}._")

    # -- objets -------------------------------------------------------------------
    def item(self, item_id: int) -> Optional[sqlite3.Row]:
        rows = self.q("SELECT * FROM items WHERE id = ?", (int(item_id),))
        return rows[0] if rows else None

    def items_by_name(self, name: str, limit: int = 10) -> List[sqlite3.Row]:
        n = F.norm_key(name)
        exact = self.q("SELECT * FROM items WHERE name_norm = ? ORDER BY ilvl DESC LIMIT ?", (n, limit))
        if exact:
            return exact
        like = "%" + "%".join(n.split()) + "%"
        return self.q("SELECT * FROM items WHERE name_norm LIKE ? ORDER BY length(name), ilvl DESC LIMIT ?",
                      (like, limit))

    def sources(self, item_id: int) -> List[sqlite3.Row]:
        return self.q("SELECT * FROM item_sources WHERE item_id = ?", (int(item_id),))

    def loot_of(self, item_id: int) -> List[sqlite3.Row]:
        return self.q("SELECT l.*, d.name AS dungeon, e.name AS boss FROM dungeon_loot l "
                      "LEFT JOIN dungeons d ON d.map_id = l.map_id LEFT JOIN encounters e ON e.id = l.encounter_id "
                      "WHERE l.item_id = ?", (int(item_id),))


def is_junk(row: Any) -> bool:
    n = (row["name"] or "").lower()
    return not n or any(m in n for m in JUNK_MARKERS)


def stats_of(row: Any) -> Dict[str, int]:
    try:
        return json.loads(row["stats_json"]) if row["stats_json"] else {}
    except ValueError:
        return {}


def to_addon_item(row: Any) -> Dict[str, Any]:
    """Ligne de la base -> objet au format de l'addon (réutilise gear.evaluate)."""
    stats: Dict[str, Any] = {}
    for k, v in stats_of(row).items():
        if k not in STAT_KEYS and k not in ("bonus_armor", "mana", "health", "haste", "expertise", "resilience",
                                            "spell_damage", "spell_pen"):
            continue  # type de stat inconnu : ignoré plutôt qu'affiché brut
        stats[f"ITEM_MOD_{STAT_KEYS.get(k, k.upper())}_SHORT"] = v
    if row["armor"]:
        stats["RESISTANCE0_NAME"] = row["armor"]
    return {"itemId": row["id"], "name": row["name"], "classId": row["class_id"], "subclassId": row["subclass_id"],
            "equipLoc": INVTYPE.get(row["inventory_type"], ""), "requiredLevel": row["req_level"],
            "itemLevel": row["ilvl"], "quality": row["quality"], "dps": row["dps"], "stats": stats}


def stats_line(row: Any) -> str:
    parts = []
    if row["dps"]:
        parts.append(f"{row['dmg_min']}-{row['dmg_max']} dégâts, vitesse {F.fr_num(row['speed'], 2)}, "
                     f"{F.fr_num(row['dps'], 1)} DPS")
    if row["armor"]:
        parts.append(f"{row['armor']} armure")
    st = F.stats_text(F.item_stats(to_addon_item(row)))
    if st:
        parts.append(st)
    return ", ".join(parts) or "aucune stat"


def item_title(row: Any) -> str:
    q = QUALITY.get(row["quality"], "?")
    bits = [row["kind"] or "", row["slot_fr"] or ""]
    kind = " · ".join(b for b in bits if b)
    return (f"**{row['name']}** (id {row['id']}) — {q}, niv. d'objet {row['ilvl']}, niveau requis "
            f"{row['req_level'] or 1}" + (f", {kind}" if kind else ""))


def origin_note(row: Any) -> str:
    return ORIGIN_FR.get(row["origin"], row["origin"] or "?")
