"""Accès en lecture seule à la base locale du jeu (gamedata/forever-<locale>.sqlite).

La base est construite chez chaque joueur par `gamedata/build.py` à partir des fichiers de son
client WoW Forever (tables DB2 + correctifs du serveur). Ce module ne fait que la lire.
Schéma : docs/schema-gamedb.md.
"""

from __future__ import annotations

import json
import re
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import formats as F
from i18n import L, T

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
BADGE_FR = "[Forever · base locale]"
BADGE_EN = "[Forever · local DB]"


def badge() -> str:
    """Badge des données issues de la base locale, dans la langue de sortie."""
    return T(BADGE_FR)


BADGE = BADGE_FR  # compatibilité ; la sortie passe par badge()

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
# filtres acceptés en français et en anglais (clés normalisées par norm_key)
STAT_ALIASES = {"force": "str", "agilite": "agi", "agi": "agi", "endurance": "sta", "endu": "sta",
                "intelligence": "int", "int": "int", "esprit": "spi", "pa": "ap", "puissance d attaque": "ap",
                "pa distance": "rap", "puissance des sorts": "spell_power", "crit": "crit", "critique": "crit",
                "toucher": "hit", "for": "str", "end": "sta", "esp": "spi",
                "strength": "str", "str": "str", "agility": "agi", "stamina": "sta", "sta": "sta",
                "intellect": "int", "spirit": "spi", "spi": "spi", "ap": "ap", "attack power": "ap",
                "rap": "rap", "ranged ap": "rap", "ranged attack power": "rap", "spell power": "spell_power",
                "sp": "spell_power", "healing": "healing", "soins": "healing", "critical": "crit",
                "critical strike": "crit", "hit": "hit", "defense": "defense", "defence": "defense",
                "dodge": "dodge", "esquive": "dodge", "parry": "parry", "parade": "parry", "block": "block",
                "blocage": "block", "armor": "bonus_armor", "armure": "bonus_armor"}
# compatibilité : libellés français fixes ; la sortie passe par quality_name()
QUALITY = {0: "médiocre", 1: "commun", 2: "inhabituel", 3: "rare", 4: "épique", 5: "légendaire"}
QUALITY_ALIASES = {"gris": 0, "mediocre": 0, "blanc": 1, "commun": 1, "vert": 2, "inhabituel": 2,
                   "bleu": 3, "rare": 3, "violet": 4, "epique": 4, "orange": 5, "legendaire": 5,
                   "grey": 0, "gray": 0, "poor": 0, "white": 1, "common": 1, "green": 2, "uncommon": 2,
                   "blue": 3, "purple": 4, "epic": 4, "legendary": 5}


def quality_name(q: Any) -> str:
    return L("quality", q, "?")
CLASS_IDS = {"WARRIOR": 1, "PALADIN": 2, "HUNTER": 3, "ROGUE": 4, "PRIEST": 5, "SHAMAN": 7, "MAGE": 8,
             "WARLOCK": 9, "DRUID": 11}
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


def missing_message() -> str:
    return T(MISSING_MSG, cmd=build_command())


def find_db_path(data_dir: Optional[Path], locale: Optional[str] = None) -> Optional[Path]:
    """Base de la langue du client du perso (forever-<locale>.sqlite), sinon n'importe quelle base présente.

    `locale` = meta.locale de la capture (frFR, enUS…). Ordre : variable FOREVER_GAMEDB (chemin imposé),
    puis <data>/../gamedata/ et ~/WowForever/gamedata/ ; dans chaque dossier, la base de cette langue
    d'abord, puis la plus récente des autres.
    """
    env = os.environ.get("FOREVER_GAMEDB")
    if env:  # chemin imposé (tests, autre emplacement) : rien d'autre n'est cherché
        p = Path(env).expanduser()
        return p if p.is_file() else None
    roots = []
    if data_dir:
        roots.append(Path(data_dir).parent / "gamedata")
    home = Path.home() / "WowForever" / "gamedata"
    if home not in roots:
        roots.append(home)
    if locale:
        for r in roots:
            if (r / f"forever-{locale}.sqlite").is_file():
                return r / f"forever-{locale}.sqlite"
    for r in roots:
        hits = sorted(r.glob("forever-*.sqlite"), key=lambda h: -h.stat().st_mtime) if r.is_dir() else []
        if hits:
            return hits[0]
    return None


class GameDBMissing(Exception):
    pass


class GameDB:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.con = sqlite3.connect(Path(self.path).resolve().as_uri() + "?mode=ro", uri=True,
                                   check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        # fold(x) : même normalisation que les colonnes *_norm, pour les colonnes qui n'en ont pas (sorts, sous-titres)
        try:
            self.con.create_function("fold", 1, F.norm_key, deterministic=True)
        except (TypeError, sqlite3.NotSupportedError):  # Python < 3.8 ou SQLite ancien
            self.con.create_function("fold", 1, F.norm_key)
        self.meta = {r["key"]: r["value"] for r in self.con.execute("SELECT key, value FROM meta")}

    def q(self, sql: str, args: tuple = ()) -> List[sqlite3.Row]:
        return self.con.execute(sql, args).fetchall()

    @property
    def locale(self) -> Optional[str]:
        return self.meta.get("locale")

    def header(self) -> str:
        return "_" + T("{badge} build {build}", badge=badge(), build=self.meta.get('build', '?')) + "_"

    def header_full(self) -> str:
        return "_" + T("{badge} build {build}, base construite le {date} (langue du jeu : {locale}).",
                       badge=badge(), build=self.meta.get('build', '?'),
                       date=(self.meta.get('built_at') or '?')[:10], locale=self.meta.get('locale', '?')) + "_"

    # -- objets -------------------------------------------------------------------
    def item(self, item_id: int) -> Optional[sqlite3.Row]:
        rows = self.q("SELECT * FROM items WHERE id = ?", (int(item_id),))
        return rows[0] if rows else None

    def items_by_name(self, name: str, limit: int = 10) -> List[sqlite3.Row]:
        n = F.norm_key(name)
        exact = self.q("SELECT * FROM items WHERE name_norm = ? ORDER BY ilvl DESC LIMIT ?", (n, limit))
        if exact:
            return exact
        for pattern in like_patterns(name):
            rows = self.q("SELECT * FROM items WHERE name_norm LIKE ? ORDER BY length(name), ilvl DESC LIMIT ?",
                          (pattern, limit))
            if rows:
                return rows
        return self.items_by_english_name(name, limit)

    def items_by_english_name(self, name: str, limit: int = 10) -> List[sqlite3.Row]:
        """Repli : nom anglais (QuestieDB enUS), pour « Copper Shortsword » sur un client frFR."""
        for pattern in [F.norm_key(name)] + like_patterns(name):
            try:
                rows = self.q("SELECT i.* FROM q_items q JOIN items i ON i.id = q.id WHERE fold(q.name) "
                              + ("= ?" if "%" not in pattern else "LIKE ?")
                              + " ORDER BY length(q.name), i.ilvl DESC LIMIT ?", (pattern, limit))
            except sqlite3.Error:   # base sans QuestieDB
                return []
            if rows:
                return rows
        return []

    def sources(self, item_id: int) -> List[sqlite3.Row]:
        return self.q("SELECT * FROM item_sources WHERE item_id = ?", (int(item_id),))

    def loot_of(self, item_id: int) -> List[sqlite3.Row]:
        return self.q("SELECT l.*, d.name AS dungeon, e.name AS boss FROM dungeon_loot l "
                      "LEFT JOIN dungeons d ON d.map_id = l.map_id LEFT JOIN encounters e ON e.id = l.encounter_id "
                      "WHERE l.item_id = ?", (int(item_id),))


def like_patterns(text: Any) -> List[str]:
    """Motifs LIKE pour une recherche par nom, du plus strict au plus large.

    « humberts helm » doit trouver « Humbert's Helm » (normalisé « humbert s helm ») : le second motif
    retire le s final des mots (possessif anglais, pluriels français et anglais).
    """
    n = F.norm_key(text)
    if not n:
        return []
    out = ["%" + "%".join(n.split()) + "%"]
    loose = "%" + "%".join(w[:-1] if len(w) > 3 and w.endswith("s") else w for w in n.split()) + "%"
    if loose not in out:
        out.append(loose)
    return out


_TEST_WORD = re.compile(r"(?<![a-zà-ÿ])(test|tst|dnd|nyi)(?![a-zà-ÿ])", re.I)
# Stats qui n'existent pas dans un jeu de type Classic : objet de test ou repris de retail, pas obtenable.
RETAIL_STATS = {"haste", "expertise", "versatility", "mastery"}


def is_junk(row: Any) -> bool:
    n = (row["name"] or "").lower()
    return not n or any(m in n for m in JUNK_MARKERS) or bool(_TEST_WORD.search(n))


# Niveau requis absent (1) sur des objets ajoutés par Forever : on l'estime depuis le niveau d'objet
# (écart moyen observé dans la base : ilvl - 5 pour les verts et les bleus).
REQ_FROM_ILVL = 5
# Seulement pour les objets ajoutés par Forever : certains objets Classic n'ont réellement aucun niveau requis.
EFFECTIVE_REQ_SQL = (f"(CASE WHEN COALESCE(req_level, 0) <= 1 AND COALESCE(ilvl, 0) > 10 AND origin = 'ajoute' "
                     f"THEN ilvl - {REQ_FROM_ILVL} ELSE req_level END)")


def effective_req(row: Any) -> Tuple[int, bool]:
    """(niveau requis, estimé ?) : estime le niveau requis quand le client dit 1 pour un objet de haut niveau."""
    keys = row.keys() if hasattr(row, "keys") else []
    req = (row["req_level"] if "req_level" in keys else 0) or 0
    ilvl = (row["ilvl"] if "ilvl" in keys else 0) or 0
    origin = row["origin"] if "origin" in keys else None
    if req <= 1 and ilvl > 10 and origin == "ajoute":
        return max(1, int(ilvl) - REQ_FROM_ILVL), True
    return int(req), False


def plausible_item(row: Any) -> bool:
    """Faux pour un objet sans doute inobtenable : stats de retail, niveau d'objet aberrant."""
    if is_junk(row):
        return False
    keys = row.keys()
    stats = stats_of(row) if "stats_json" in keys else {}
    if any(k in RETAIL_STATS for k in stats):
        return False
    ilvl = (row["ilvl"] if "ilvl" in keys else 0) or 0
    req = (row["req_level"] if "req_level" in keys else 0) or 0
    if ilvl > 100 or (ilvl > 90 and req < 55):
        return False
    return True


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
            "equipLoc": INVTYPE.get(row["inventory_type"], ""), "requiredLevel": effective_req(row)[0],
            "itemLevel": row["ilvl"], "quality": row["quality"], "dps": row["dps"], "stats": stats}


def stats_line(row: Any) -> str:
    parts = []
    if row["dps"]:
        parts.append(T("{min}-{max} dégâts, vitesse {speed}, {dps} DPS", min=row['dmg_min'], max=row['dmg_max'],
                       speed=F.num(row['speed'], 2), dps=F.num(row['dps'], 1)))
    if row["armor"]:
        parts.append(T("{n} armure", n=row['armor']))
    st = F.stats_text(F.item_stats(to_addon_item(row)))
    if st:
        parts.append(st)
    return ", ".join(parts) or T("aucune stat")


def _col(row: Any, key: str) -> Any:
    try:
        return row[key]
    except (IndexError, KeyError):
        return None


def kind_label(row: Any) -> str:
    """Type d'objet (« cuir », « leather », « arc »…) calculé depuis les IDs, dans la langue de sortie."""
    import gear as G  # import local : gear importe formats, pas gamedb

    cid = _col(row, "class_id")
    if cid not in (2, 4):
        return ""
    return G.item_kind({"classId": cid, "subclassId": _col(row, "subclass_id"),
                        "equipLoc": INVTYPE.get(_col(row, "inventory_type"), "")})


def slot_label(row: Any) -> str:
    """Emplacement (« Tête », « Head »…) depuis InventoryType, dans la langue de sortie."""
    inv = _col(row, "inventory_type")
    return L("invtype", inv, "") if inv else ""


def kind_slot(row: Any, sep: str = " · ") -> str:
    """Type + emplacement, sans répéter l'emplacement s'il est déjà dans le type
    (« épée à une main » et non « épée à une main · Une main »)."""
    kind, slot = kind_label(row), slot_label(row)
    if kind and slot and F.norm_key(slot) in F.norm_key(kind):
        slot = ""
    if kind and sep == " ":
        slot = slot.lower()
    return sep.join(b for b in (kind, slot) if b)


def item_title(row: Any) -> str:
    q = quality_name(row["quality"])
    kind = kind_slot(row)
    return T("**{name}** (id {id}) — {quality}, niv. d'objet {ilvl}, niveau requis {req}",
             name=row['name'], id=row['id'], quality=q, ilvl=row['ilvl'], req=row['req_level'] or 1) \
        + (f", {kind}" if kind else "")


def origin_note(row: Any) -> str:
    return L("origin", row["origin"], row["origin"] or "?")
