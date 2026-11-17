"""Output language of the MCP server (French or English).

Two different languages are at play and must not be confused:
- the *game language* (client locale, e.g. frFR, enUS): names that come from the game
  (items, quests, zones, spells, professions) always stay in that language;
- the *answer language* (``fr`` or ``en``): the labels, headings, advice and errors written
  by this server. It follows, in order: the ``lang`` argument of a tool call, then
  ``answer_language`` in ``perso/config.json``, then the client locale of the character
  (frFR -> fr, anything else -> en).

Source strings are written in French in the code and wrapped in ``T()``; the English
catalog (``i18n_en.py``) maps each French template to its English version. A test checks
that every literal passed to ``T()`` has an English entry.

Labels keyed by game IDs (slots, stats, qualities…) live in ``LABELS`` below.
"""

from __future__ import annotations

import contextlib
import contextvars
from typing import Any, Dict, Iterator, Optional

from i18n_en import EN

SUPPORTED = ("fr", "en")
DEFAULT = "fr"
_LANG: contextvars.ContextVar[str] = contextvars.ContextVar("forever_lang", default=DEFAULT)
MISSING: set = set()  # French templates without an English entry met at run time (debug)


def norm_lang(value: Any) -> Optional[str]:
    """'en', 'en-US', 'enUS', 'English', 'anglais' -> 'en' ; 'fr', 'frFR', 'français' -> 'fr'."""
    if not value:
        return None
    v = str(value).strip().lower().replace("_", "-")
    if v.startswith(("fr", "français", "francais", "french")):
        return "fr"
    if v.startswith(("en", "anglais", "english")):
        return "en"
    return None


def lang_from_locale(locale: Any) -> Optional[str]:
    """Client locale (GetLocale) -> answer language: frFR -> fr, any other known locale -> en."""
    if not locale:
        return None
    loc = str(locale)
    return "fr" if loc.lower().startswith("fr") else "en"


def get_lang() -> str:
    return _LANG.get()


def set_lang(lang: Optional[str]) -> contextvars.Token:
    return _LANG.set(norm_lang(lang) or DEFAULT)


@contextlib.contextmanager
def using(lang: Optional[str]) -> Iterator[str]:
    token = set_lang(lang)
    try:
        yield get_lang()
    finally:
        _LANG.reset(token)


def T(source: str, /, **kw: Any) -> str:
    """Translates a French template into the current language, then formats it with ``kw``."""
    tpl = source
    if _LANG.get() == "en":
        tpl = EN.get(source)
        if tpl is None:
            MISSING.add(source)
            tpl = source
    return tpl.format(**kw) if kw else tpl


# ----------------------------------------------------------------------------
# Labels keyed by game IDs or internal codes
# ----------------------------------------------------------------------------

LABELS: Dict[str, Dict[str, Dict[Any, str]]] = {
    "fr": {
        "slot": {"HeadSlot": "Tête", "NeckSlot": "Cou", "ShoulderSlot": "Épaules", "BackSlot": "Dos",
                 "ChestSlot": "Torse", "ShirtSlot": "Chemise", "TabardSlot": "Tabard", "WristSlot": "Poignets",
                 "HandsSlot": "Mains", "WaistSlot": "Taille", "LegsSlot": "Jambes", "FeetSlot": "Pieds",
                 "Finger0Slot": "Doigt 1", "Finger1Slot": "Doigt 2", "Trinket0Slot": "Bijou 1",
                 "Trinket1Slot": "Bijou 2", "MainHandSlot": "Main droite", "SecondaryHandSlot": "Main gauche",
                 "RangedSlot": "Distance"},
        "invtype": {1: "Tête", 2: "Cou", 3: "Épaules", 4: "Chemise", 5: "Torse", 6: "Taille", 7: "Jambes",
                    8: "Pieds", 9: "Poignets", 10: "Mains", 11: "Doigt", 12: "Bijou", 13: "Une main",
                    14: "Bouclier", 15: "Distance", 16: "Dos", 17: "Deux mains", 18: "Sac", 19: "Tabard",
                    20: "Torse", 21: "Main droite", 22: "Main gauche", 23: "Tenu en main gauche",
                    24: "Munitions", 25: "Armes de jet", 26: "Distance", 27: "Carquois", 28: "Relique"},
        "stat": {"STRENGTH": "For", "AGILITY": "Agi", "STAMINA": "End", "INTELLECT": "Int", "SPIRIT": "Esp",
                 "ATTACK_POWER": "PA", "RANGED_ATTACK_POWER": "PA distance", "SPELL_POWER": "Puiss. des sorts",
                 "HEALING_POWER": "Soins", "CRIT_RATING": "Crit", "HIT_RATING": "Toucher",
                 "DEFENSE_SKILL_RATING": "Défense", "DODGE_RATING": "Esquive", "PARRY_RATING": "Parade",
                 "BLOCK_RATING": "Blocage", "BLOCK_VALUE": "Valeur de blocage", "MANA_REGENERATION": "Mana/5 s",
                 "HEALTH_REGENERATION": "PV/5 s", "FIRE_RESISTANCE": "Rés. feu", "FROST_RESISTANCE": "Rés. givre",
                 "NATURE_RESISTANCE": "Rés. nature", "SHADOW_RESISTANCE": "Rés. ombre",
                 "ARCANE_RESISTANCE": "Rés. arcanes", "HOLY_RESISTANCE": "Rés. sacré", "DAMAGE_PER_SECOND": "DPS",
                 "BONUS_ARMOR": "Armure bonus", "SPELL_DAMAGE": "Dégâts des sorts", "MANA": "Mana",
                 "HEALTH": "Vie", "HASTE": "Hâte", "EXPERTISE": "Expertise", "RESILIENCE": "Résilience",
                 "SPELL_PEN": "Pénétration des sorts", "ARMOR": "Armure"},
        "resist": {"holy": "sacré", "fire": "feu", "nature": "nature", "frost": "givre", "shadow": "ombre",
                   "arcane": "arcanes"},
        "quality": {0: "médiocre", 1: "commun", 2: "inhabituel", 3: "rare", 4: "épique", 5: "légendaire",
                    6: "artefact", 7: "héritage"},
        "happiness": {1: "mécontent", 2: "content", 3: "heureux"},
        "role": {"DAMAGER": "DPS", "TANK": "Tank", "HEALER": "Soins"},
        "prof_slot": {"primary1": "principal", "primary2": "principal", "cooking": "secondaire",
                      "fishing": "secondaire", "firstAid": "secondaire", "archaeology": "secondaire"},
        "quest_color": {"red": "rouge", "orange": "orange", "yellow": "jaune", "grey": "grise", "green": "verte"},
        "recipe_color": {0: "orange", 1: "jaune", 2: "verte", 3: "grise"},
        "armor": {0: "divers", 1: "tissu", 2: "cuir", 3: "maille", 4: "plaques", 6: "bouclier"},
        "weapon": {0: "hache à une main", 1: "hache à deux mains", 2: "arc", 3: "fusil", 4: "masse à une main",
                   5: "masse à deux mains", 6: "arme d'hast", 7: "épée à une main", 8: "épée à deux mains",
                   10: "bâton", 13: "arme de pugilat", 15: "dague", 16: "arme de jet", 18: "arbalète",
                   19: "baguette", 20: "canne à pêche"},
        "misc_kind": {"INVTYPE_FINGER": "anneau", "INVTYPE_NECK": "collier", "INVTYPE_TRINKET": "bijou",
                      "INVTYPE_CLOAK": "cape", "INVTYPE_HOLDABLE": "tenu en main gauche"},
        "verdict": {"upgrade": "amélioration", "empty_slot": "emplacement vide : à équiper",
                    "minor_plus": "léger plus (endurance/armure)", "worse": "moins bien",
                    "equivalent": "équivalent", "not_for_you": "pas pour toi", "not_equippable": "non équipable"},
        "origin": {"client": "fichiers du jeu", "modifie": "modifié par Forever",
                   "ajoute": "fourni par le serveur Forever", "cache": "cache des quêtes"},
        "source_type": {"artisanat": "artisanat", "donjon": "donjon"},
    },
    "en": {
        "slot": {"HeadSlot": "Head", "NeckSlot": "Neck", "ShoulderSlot": "Shoulders", "BackSlot": "Back",
                 "ChestSlot": "Chest", "ShirtSlot": "Shirt", "TabardSlot": "Tabard", "WristSlot": "Wrists",
                 "HandsSlot": "Hands", "WaistSlot": "Waist", "LegsSlot": "Legs", "FeetSlot": "Feet",
                 "Finger0Slot": "Finger 1", "Finger1Slot": "Finger 2", "Trinket0Slot": "Trinket 1",
                 "Trinket1Slot": "Trinket 2", "MainHandSlot": "Main hand", "SecondaryHandSlot": "Off hand",
                 "RangedSlot": "Ranged"},
        "invtype": {1: "Head", 2: "Neck", 3: "Shoulders", 4: "Shirt", 5: "Chest", 6: "Waist", 7: "Legs",
                    8: "Feet", 9: "Wrists", 10: "Hands", 11: "Finger", 12: "Trinket", 13: "One-hand",
                    14: "Shield", 15: "Ranged", 16: "Back", 17: "Two-hand", 18: "Bag", 19: "Tabard",
                    20: "Chest", 21: "Main hand", 22: "Off hand", 23: "Held in off-hand",
                    24: "Ammo", 25: "Thrown", 26: "Ranged", 27: "Quiver", 28: "Relic"},
        "stat": {"STRENGTH": "Str", "AGILITY": "Agi", "STAMINA": "Sta", "INTELLECT": "Int", "SPIRIT": "Spi",
                 "ATTACK_POWER": "AP", "RANGED_ATTACK_POWER": "Ranged AP", "SPELL_POWER": "Spell power",
                 "HEALING_POWER": "Healing", "CRIT_RATING": "Crit", "HIT_RATING": "Hit",
                 "DEFENSE_SKILL_RATING": "Defense", "DODGE_RATING": "Dodge", "PARRY_RATING": "Parry",
                 "BLOCK_RATING": "Block", "BLOCK_VALUE": "Block value", "MANA_REGENERATION": "Mana/5s",
                 "HEALTH_REGENERATION": "HP/5s", "FIRE_RESISTANCE": "Fire res.", "FROST_RESISTANCE": "Frost res.",
                 "NATURE_RESISTANCE": "Nature res.", "SHADOW_RESISTANCE": "Shadow res.",
                 "ARCANE_RESISTANCE": "Arcane res.", "HOLY_RESISTANCE": "Holy res.", "DAMAGE_PER_SECOND": "DPS",
                 "BONUS_ARMOR": "Bonus armor", "SPELL_DAMAGE": "Spell damage", "MANA": "Mana",
                 "HEALTH": "Health", "HASTE": "Haste", "EXPERTISE": "Expertise", "RESILIENCE": "Resilience",
                 "SPELL_PEN": "Spell penetration", "ARMOR": "Armor"},
        "resist": {"holy": "holy", "fire": "fire", "nature": "nature", "frost": "frost", "shadow": "shadow",
                   "arcane": "arcane"},
        "quality": {0: "poor", 1: "common", 2: "uncommon", 3: "rare", 4: "epic", 5: "legendary",
                    6: "artifact", 7: "heirloom"},
        "happiness": {1: "unhappy", 2: "content", 3: "happy"},
        "role": {"DAMAGER": "DPS", "TANK": "Tank", "HEALER": "Healer"},
        "prof_slot": {"primary1": "primary", "primary2": "primary", "cooking": "secondary",
                      "fishing": "secondary", "firstAid": "secondary", "archaeology": "secondary"},
        "quest_color": {"red": "red", "orange": "orange", "yellow": "yellow", "grey": "grey", "green": "green"},
        "recipe_color": {0: "orange", 1: "yellow", 2: "green", 3: "grey"},
        "armor": {0: "misc", 1: "cloth", 2: "leather", 3: "mail", 4: "plate", 6: "shield"},
        "weapon": {0: "one-handed axe", 1: "two-handed axe", 2: "bow", 3: "gun", 4: "one-handed mace",
                   5: "two-handed mace", 6: "polearm", 7: "one-handed sword", 8: "two-handed sword",
                   10: "staff", 13: "fist weapon", 15: "dagger", 16: "thrown weapon", 18: "crossbow",
                   19: "wand", 20: "fishing pole"},
        "misc_kind": {"INVTYPE_FINGER": "ring", "INVTYPE_NECK": "necklace", "INVTYPE_TRINKET": "trinket",
                      "INVTYPE_CLOAK": "cloak", "INVTYPE_HOLDABLE": "held in off-hand"},
        "verdict": {"upgrade": "upgrade", "empty_slot": "empty slot: equip it",
                    "minor_plus": "small plus (stamina/armor)", "worse": "worse",
                    "equivalent": "equivalent", "not_for_you": "not for you", "not_equippable": "not equippable"},
        "origin": {"client": "game files", "modifie": "modified by Forever",
                   "ajoute": "provided by the Forever server", "cache": "quest cache"},
        "source_type": {"artisanat": "crafting", "donjon": "dungeon"},
    },
}


def L(table: str, key: Any, default: Any = None) -> Any:
    """Label of ``key`` in ``table`` for the current language (falls back to French, then default)."""
    lang = _LANG.get()
    val = LABELS.get(lang, {}).get(table, {}).get(key)
    if val is None:
        val = LABELS[DEFAULT].get(table, {}).get(key)
    return default if val is None else val


def labels(table: str) -> Dict[Any, str]:
    return LABELS.get(_LANG.get(), LABELS[DEFAULT]).get(table, {})
