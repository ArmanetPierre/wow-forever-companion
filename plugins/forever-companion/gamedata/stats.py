"""Calcul des caractéristiques d'un objet à partir des tables du jeu.

Le client moderne ne stocke pas « +3 Agilité » mais une répartition (StatPercentEditor,
en dix-millièmes) appliquée à un budget qui dépend du niveau d'objet, de la qualité et de
l'emplacement (table RandPropPoints). Les dégâts d'une arme viennent des tables
ItemDamage* (DPS par niveau d'objet et qualité), de la vitesse et de la variance.

Formules validées sur les objets réels capturés par l'addon (voir docs/schema-gamedb.md).
"""
import math

# Types de stats (ItemSparse.StatModifier_bonusStat) → clé courte, libellé FR.
STAT_NAMES = {
    0: ("mana", "Mana"), 1: ("health", "Vie"), 3: ("agi", "Agilité"), 4: ("str", "Force"),
    5: ("int", "Intelligence"), 6: ("spi", "Esprit"), 7: ("sta", "Endurance"),
    12: ("defense", "Défense"), 13: ("dodge", "Esquive"), 14: ("parry", "Parade"),
    15: ("block", "Blocage"), 16: ("hit_melee", "Toucher (mêlée)"), 17: ("hit_ranged", "Toucher (distance)"),
    18: ("hit_spell", "Toucher (sorts)"), 19: ("crit_melee", "Critique (mêlée)"),
    20: ("crit_ranged", "Critique (distance)"), 21: ("crit_spell", "Critique (sorts)"),
    31: ("hit", "Toucher"), 32: ("crit", "Critique"), 35: ("resilience", "Résilience"),
    36: ("haste", "Hâte"), 37: ("expertise", "Expertise"), 38: ("ap", "Puissance d'attaque"),
    39: ("rap", "Puissance d'attaque à distance"), 41: ("healing", "Soins"), 42: ("spell_damage", "Dégâts des sorts"),
    45: ("spell_power", "Puissance des sorts"), 47: ("spell_pen", "Pénétration des sorts"),
    48: ("block_value", "Valeur de blocage"), 50: ("bonus_armor", "Armure bonus"),
    51: ("fire_res", "Résistance au Feu"), 52: ("frost_res", "Résistance au Givre"),
    53: ("holy_res", "Résistance au Sacré"), 54: ("shadow_res", "Résistance à l'Ombre"),
    55: ("nature_res", "Résistance à la Nature"), 56: ("arcane_res", "Résistance aux Arcanes"),
}

# InventoryType → colonne du budget RandPropPoints (0 à 4).
BUDGET_SLOT = {
    1: 0, 5: 0, 7: 0, 20: 0, 17: 0, 15: 0,        # tête, torse, jambes, robe, deux mains, arc
    3: 1, 6: 1, 8: 1, 10: 1, 12: 1,                 # épaules, taille, pieds, mains, bijou
    2: 2, 9: 2, 11: 2, 16: 2, 14: 2, 23: 2,         # cou, poignets, doigt, dos, bouclier, main gauche
    13: 3, 21: 3, 22: 3,                            # une main, main droite, main gauche (arme)
    26: 4, 25: 4, 28: 4,                            # fusil/arbalète/baguette, armes de jet, relique
}

INVENTORY_TYPES = {
    0: ("", "Non équipable"), 1: ("head", "Tête"), 2: ("neck", "Cou"), 3: ("shoulder", "Épaules"),
    4: ("shirt", "Chemise"), 5: ("chest", "Torse"), 6: ("waist", "Taille"), 7: ("legs", "Jambes"),
    8: ("feet", "Pieds"), 9: ("wrist", "Poignets"), 10: ("hands", "Mains"), 11: ("finger", "Doigt"),
    12: ("trinket", "Bijou"), 13: ("weapon", "Une main"), 14: ("shield", "Bouclier"),
    15: ("ranged", "À distance"), 16: ("back", "Dos"), 17: ("2hweapon", "Deux mains"),
    18: ("bag", "Sac"), 19: ("tabard", "Tabard"), 20: ("chest", "Torse (robe)"),
    21: ("mainhand", "Main droite"), 22: ("offhand", "Main gauche"), 23: ("holdable", "Tenu en main gauche"),
    24: ("ammo", "Munitions"), 25: ("thrown", "Armes de jet"), 26: ("ranged", "À distance"),
    27: ("quiver", "Carquois"), 28: ("relic", "Relique"),
}

QUALITY_NAMES = {0: "Médiocre", 1: "Commun", 2: "Inhabituel", 3: "Rare", 4: "Épique",
                 5: "Légendaire", 6: "Artefact", 7: "Héritage"}

# Table de dégâts selon (classe d'objet 2 = arme, sous-classe).
WEAPON_DAMAGE_TABLE = {
    0: "ItemDamageOneHand", 4: "ItemDamageOneHand", 7: "ItemDamageOneHand", 13: "ItemDamageOneHand",
    15: "ItemDamageOneHand", 11: "ItemDamageOneHand",                    # haches, masses, épées, pugilat, dagues
    1: "ItemDamageTwoHand", 5: "ItemDamageTwoHand", 6: "ItemDamageTwoHand", 8: "ItemDamageTwoHand",
    10: "ItemDamageTwoHand", 17: "ItemDamageTwoHand", 20: "ItemDamageTwoHand",  # 2M, armes d'hast, bâtons
    2: "ItemDamageRanged", 3: "ItemDamageRanged", 18: "ItemDamageRanged",  # arcs, fusils, arbalètes
    16: "ItemDamageThrown", 19: "ItemDamageWand",
}


def round_half_up(x):
    return int(math.floor(x + 0.5))


def budget(randprop_row, quality, inventory_type):
    """Budget de stats pour un objet (RandPropPoints), ou None si non applicable."""
    if randprop_row is None:
        return None
    col = BUDGET_SLOT.get(inventory_type)
    if col is None:
        return None
    if quality >= 4:
        arr = randprop_row.get("EpicF") or randprop_row.get("Epic")
    elif quality == 3:
        arr = randprop_row.get("SuperiorF") or randprop_row.get("Superior")
    else:
        arr = randprop_row.get("GoodF") or randprop_row.get("Good")
    return float(arr[col]) if arr else None


def item_stats(sparse, randprop_row):
    """{type de stat: valeur} calculé pour une ligne d'ItemSparse."""
    stats = {}
    types = sparse.get("StatModifier_bonusStat") or []
    pcts = sparse.get("StatPercentEditor") or []
    b = budget(randprop_row, sparse.get("OverallQualityID", 0), sparse.get("InventoryType", 0))
    if not b:
        return stats
    for t, p in zip(types, pcts):
        if t is None or t < 0 or not p:
            continue
        v = round_half_up(p * b / 10000.0)
        if v:
            stats[t] = stats.get(t, 0) + v
    return stats


def weapon_damage(sparse, item_row, damage_tables):
    """(min, max, vitesse en s, DPS) pour une arme, ou None.

    DPS de base = ItemDamage<table>[ilvl].Quality[qualité] ; dégâts moyens = DPS × vitesse ;
    min = arrondi inférieur de moyen × (1 − variance/2), max = arrondi de moyen × (1 + variance/2).
    """
    if not item_row or item_row.get("ClassID") != 2:
        return None
    table = WEAPON_DAMAGE_TABLE.get(item_row.get("SubclassID"))
    delay = sparse.get("ItemDelay") or 0
    if not table or not delay:
        return None
    row = damage_tables.get(table, {}).get(sparse.get("ItemLevel"))
    if not row:
        return None
    q = sparse.get("OverallQualityID", 0)
    qual = row.get("Quality") or []
    if q >= len(qual):
        return None
    dps = qual[q]
    speed = delay / 1000.0
    avg = dps * speed
    var = sparse.get("DmgVariance") or 0.0
    lo = int(math.floor(avg * (1 - var / 2)))
    hi = round_half_up(avg * (1 + var / 2))
    real_dps = (lo + hi) / 2 / speed if speed else 0
    return lo, hi, speed, round(real_dps, 2)


# Sous-classe d'armure (classe d'objet 4) → colonne d'ItemArmorTotal et d'ArmorLocation.
ARMOR_MATERIAL = {1: ("Cloth", "Clothmodifier"), 2: ("Leather", "Leathermodifier"),
                  3: ("Mail", "Chainmodifier"), 4: ("Plate", "Platemodifier")}
ARMOR_SUBCLASS_NAMES = {0: "Divers", 1: "Tissu", 2: "Cuir", 3: "Mailles", 4: "Plaques", 6: "Bouclier",
                        7: "Libram", 8: "Idole", 9: "Totem"}
WEAPON_SUBCLASS_NAMES = {0: "Hache à une main", 1: "Hache à deux mains", 2: "Arc", 3: "Fusil",
                         4: "Masse à une main", 5: "Masse à deux mains", 6: "Arme d'hast",
                         7: "Épée à une main", 8: "Épée à deux mains", 10: "Bâton", 13: "Arme de pugilat",
                         14: "Divers", 15: "Dague", 16: "Armes de jet", 18: "Arbalète", 19: "Baguette",
                         20: "Canne à pêche"}


def armor_value(sparse, item_row, tables):
    """Armure de base d'une pièce d'armure ou d'un bouclier, ou None.

    `tables` : dict avec ItemArmorTotal, ItemArmorQuality, ArmorLocation, ItemArmorShield
    (indexés par id = niveau d'objet, ou InventoryType pour ArmorLocation).
    Armure = ItemArmorTotal[ilvl].<matière> × ItemArmorQuality[ilvl].Qualitymod[qualité]
             × ArmorLocation[emplacement].<matière>modifier, arrondi ; les capes utilisent le tissu.
    Bouclier = ItemArmorShield[ilvl].Quality[qualité].
    """
    if not item_row or item_row.get("ClassID") != 4:
        return None
    ilvl = sparse.get("ItemLevel")
    q = sparse.get("OverallQualityID", 0)
    sub = item_row.get("SubclassID")
    inv = sparse.get("InventoryType", 0)
    if sub == 6:
        row = tables.get("ItemArmorShield", {}).get(ilvl)
        qual = (row or {}).get("Quality") or []
        return int(qual[q]) if q < len(qual) else None
    mat = ARMOR_MATERIAL.get(1 if inv == 16 else sub)
    total = tables.get("ItemArmorTotal", {}).get(ilvl)
    qmod = tables.get("ItemArmorQuality", {}).get(ilvl)
    loc = tables.get("ArmorLocation", {}).get(5 if inv == 20 else inv)
    if not mat or not total or not qmod or not loc:
        return None
    qm = qmod.get("Qualitymod") or []
    if q >= len(qm):
        return None
    v = total[mat[0]] * qm[q] * loc[mat[1]]
    return round_half_up(v) if v else None
