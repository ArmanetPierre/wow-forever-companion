"""Règles d'équipement et estimation du gain d'un objet (partagé par compare_item,
get_quest_rewards et get_overview).

Les tables de maîtrise viennent de WoW Classic : Forever reprend les classes de Classic,
mais rien n'est confirmé objet par objet. Chaque conseil qui s'appuie dessus le signale.
Le drapeau `usable` lu en jeu (GetQuestLogChoiceInfo) prime toujours sur ces tables.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import formats as F
from luasv import as_list

AP_PER_DPS = 14.0  # confirmé par l'infobulle de Forever (17/11/2026)

# ---------------------------------------------------------------------------
# Maîtrises par classe [Classic · à vérifier dans Forever]
# classId 4 = armure (1 tissu, 2 cuir, 3 maille, 4 plaques, 6 bouclier, 0 divers : bijoux, anneaux…)
# classId 2 = arme (0 hache 1M, 1 hache 2M, 2 arc, 3 fusil, 4 masse 1M, 5 masse 2M, 6 arme d'hast,
#                   7 épée 1M, 8 épée 2M, 10 bâton, 13 pugilat, 15 dague, 16 arme de jet,
#                   18 arbalète, 19 baguette, 20 canne à pêche)
# ---------------------------------------------------------------------------
ARMOR_NAMES = {0: "divers", 1: "tissu", 2: "cuir", 3: "maille", 4: "plaques", 6: "bouclier"}
WEAPON_NAMES = {0: "hache à une main", 1: "hache à deux mains", 2: "arc", 3: "fusil", 4: "masse à une main",
                5: "masse à deux mains", 6: "arme d'hast", 7: "épée à une main", 8: "épée à deux mains",
                10: "bâton", 13: "arme de pugilat", 15: "dague", 16: "arme de jet", 18: "arbalète",
                19: "baguette", 20: "canne à pêche"}

# armure : sous-classe -> niveau minimum (0 = dès le départ)
ARMOR = {
    "WARRIOR": {1: 0, 2: 0, 3: 0, 4: 40, 6: 0},
    "PALADIN": {1: 0, 2: 0, 3: 0, 4: 40, 6: 0},
    "HUNTER": {1: 0, 2: 0, 3: 40},
    "SHAMAN": {1: 0, 2: 0, 3: 40, 6: 0},
    "ROGUE": {1: 0, 2: 0},
    "DRUID": {1: 0, 2: 0},
    "MAGE": {1: 0}, "PRIEST": {1: 0}, "WARLOCK": {1: 0},
}
WEAPONS = {
    "WARRIOR": {0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 13, 15, 16, 18},
    "PALADIN": {0, 1, 4, 5, 6, 7, 8},
    "HUNTER": {0, 1, 2, 3, 6, 7, 8, 10, 13, 15, 16, 18},
    "SHAMAN": {0, 1, 4, 5, 10, 13, 15},
    "ROGUE": {2, 3, 4, 7, 13, 15, 16, 18},
    "DRUID": {4, 5, 10, 13, 15},
    "MAGE": {7, 10, 15, 19}, "PRIEST": {4, 10, 15, 19}, "WARLOCK": {7, 10, 15, 19},
}
DUAL_WIELD = {"WARRIOR": 20, "ROGUE": 10, "HUNTER": 20}  # niveau d'apprentissage (Classic)

EQUIPLOC_SLOTS = {
    "INVTYPE_HEAD": ["HeadSlot"], "INVTYPE_NECK": ["NeckSlot"], "INVTYPE_SHOULDER": ["ShoulderSlot"],
    "INVTYPE_CLOAK": ["BackSlot"], "INVTYPE_CHEST": ["ChestSlot"], "INVTYPE_ROBE": ["ChestSlot"],
    "INVTYPE_BODY": ["ShirtSlot"], "INVTYPE_TABARD": ["TabardSlot"], "INVTYPE_WRIST": ["WristSlot"],
    "INVTYPE_HAND": ["HandsSlot"], "INVTYPE_WAIST": ["WaistSlot"], "INVTYPE_LEGS": ["LegsSlot"],
    "INVTYPE_FEET": ["FeetSlot"], "INVTYPE_FINGER": ["Finger0Slot", "Finger1Slot"],
    "INVTYPE_TRINKET": ["Trinket0Slot", "Trinket1Slot"],
    "INVTYPE_WEAPON": ["MainHandSlot", "SecondaryHandSlot"], "INVTYPE_2HWEAPON": ["MainHandSlot"],
    "INVTYPE_WEAPONMAINHAND": ["MainHandSlot"], "INVTYPE_WEAPONOFFHAND": ["SecondaryHandSlot"],
    "INVTYPE_SHIELD": ["SecondaryHandSlot"], "INVTYPE_HOLDABLE": ["SecondaryHandSlot"],
    "INVTYPE_RANGED": ["RangedSlot"], "INVTYPE_RANGEDRIGHT": ["RangedSlot"], "INVTYPE_THROWN": ["RangedSlot"],
    "INVTYPE_RELIC": ["RangedSlot"],
}


def item_kind(item: Dict[str, Any]) -> str:
    """Texte court : « cuir », « arc », « anneau »…"""
    cid, sid = item.get("classId"), item.get("subclassId")
    if cid == 2:
        return WEAPON_NAMES.get(sid, item.get("subType") or "arme")
    if cid == 4:
        if sid == 0:
            return {"INVTYPE_FINGER": "anneau", "INVTYPE_NECK": "collier", "INVTYPE_TRINKET": "bijou",
                    "INVTYPE_CLOAK": "cape", "INVTYPE_HOLDABLE": "tenu en main gauche"}.get(item.get("equipLoc"), "divers")
        if item.get("equipLoc") == "INVTYPE_CLOAK":
            return "cape"
        return ARMOR_NAMES.get(sid, item.get("subType") or "armure")
    return (item.get("subType") or item.get("type") or "objet").lower()


def proficiency(cls: str, level: int, item: Dict[str, Any]) -> Tuple[Optional[bool], str]:
    """(portable ?, raison). None = inconnu. Le drapeau `usable` du jeu prime."""
    req = item.get("requiredLevel") or 0
    if req and level and req > level:
        return False, f"niveau requis {req}"
    if item.get("usable") is False:
        return False, "le jeu l'indique inutilisable pour ce perso"
    cid, sid = item.get("classId"), item.get("subclassId")
    if cid == 4 and sid not in (None, 0) and item.get("equipLoc") != "INVTYPE_CLOAK":
        table = ARMOR.get(cls)
        if table is None:
            return None, "classe inconnue"
        if sid not in table:
            return False, f"{ARMOR_NAMES.get(sid, 'armure')} non portable par la classe [Classic]"
        if level and table[sid] > level:
            return False, f"{ARMOR_NAMES.get(sid)} portable seulement au niveau {table[sid]} [Classic]"
    if cid == 2 and sid is not None and sid != 20:
        allowed = WEAPONS.get(cls)
        if allowed is None:
            return None, "classe inconnue"
        if sid not in allowed:
            return False, f"{WEAPON_NAMES.get(sid, 'arme')} non maîtrisée par la classe [Classic]"
    if item.get("usable") is True:
        return True, "utilisable (indiqué par le jeu)"
    return True, ""


def target_slots(cls: str, level: int, item: Dict[str, Any]) -> List[str]:
    slots = list(EQUIPLOC_SLOTS.get(item.get("equipLoc") or "", []))
    if item.get("equipLoc") == "INVTYPE_WEAPON":
        dw = DUAL_WIELD.get(cls)
        if not dw or (level and level < dw):
            slots = ["MainHandSlot"]
    return slots


def estimate(db: Dict[str, Any], slot: str, cand_stats: Dict[str, float], cand_dps: Optional[float],
             current: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    """Gain estimé (coups blancs) si l'objet remplace celui de `slot`."""
    cls = F.g(db, "identity", "classFile") or ""
    eq = F.g(db, "equipment", "slots", default={}) or {}
    cur = current if current is not None else (eq.get(slot) or {})
    ostats = F.item_stats(cur)
    odps = float(cur.get("dps") or 0.0)
    rap_agi = {"HUNTER": 2, "WARRIOR": 1, "ROGUE": 1}.get(cls, 0)
    map_str = {"WARRIOR": 2, "PALADIN": 2, "SHAMAN": 2, "DRUID": 2}.get(cls, 1)
    map_agi = {"HUNTER": 1, "ROGUE": 1}.get(cls, 0)

    def delta(k: str) -> float:
        return float(cand_stats.get(k, 0) or 0) - float(ostats.get(k, 0) or 0)

    d_rap = delta("Agi") * rap_agi + delta("PA") + delta("PA distance")
    d_map = delta("Agi") * map_agi + delta("For") * map_str + delta("PA")
    ranged_slot = slot == "RangedSlot"
    melee_slot = slot in ("MainHandSlot", "SecondaryHandSlot")
    d_r = d_rap / AP_PER_DPS + ((float(cand_dps) - odps) if (ranged_slot and cand_dps is not None) else 0.0)
    d_m = d_map / AP_PER_DPS + ((float(cand_dps) - odps) if (melee_slot and cand_dps is not None) else 0.0)
    main_ranged = cls == "HUNTER" or ranged_slot
    r_now = F.g(db, "stats", "ranged", "dps")
    m_now = F.g(db, "stats", "melee", "dps")
    key = d_r if main_ranged else d_m
    base = (r_now if main_ranged else m_now) or 0
    return {
        "ranged": d_r, "melee": d_m, "key": key, "pct": (100.0 * key / base) if base else 0.0,
        "stamina": delta("End"), "armor": delta("Armure"), "int": delta("Int"), "spi": delta("Esp"),
        "main_ranged": 1.0 if main_ranged else 0.0, "empty": 0.0 if cur else 1.0,
        "r_now": r_now if r_now is not None else float("nan"), "m_now": m_now if m_now is not None else float("nan"),
        "odps": odps,
    }


CASTERS = {"MAGE", "PRIEST", "WARLOCK"}


def evaluate(db: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
    """Évalue un objet pour le perso : verdict, emplacement, gain, raison."""
    cls = F.g(db, "identity", "classFile") or ""
    level = F.g(db, "progression", "level") or F.g(db, "identity", "level") or 0
    out: Dict[str, Any] = {"name": item.get("name") or f"objet {item.get('itemId')}", "kind": item_kind(item)}
    slots = target_slots(cls, level, item)
    if not slots:
        out.update(verdict="non équipable", score=-99.0, reason="ce n'est pas un équipement")
        return out
    ok, why = proficiency(cls, level, item)
    if ok is False:
        out.update(verdict="pas pour toi", score=-50.0, reason=why, slot=slots[0])
        return out
    eq = F.g(db, "equipment", "slots", default={}) or {}
    stats = F.item_stats(item)
    best = None
    for s in slots:
        est = estimate(db, s, stats, item.get("dps"))
        if best is None or est["key"] > best[1]["key"] or (est["empty"] and not best[1]["empty"]):
            best = (s, est)
    slot, est = best  # type: ignore[misc]
    cur = eq.get(slot)
    out.update(slot=slot, slot_fr=F.SLOT_FR.get(slot, slot), gain=est, replaces=(cur or {}).get("name"))
    caster = cls in CASTERS
    if caster:
        score = est["int"] + est["spi"] * 0.5 + est["stamina"] * 0.5 + est["armor"] * 0.01
        if est["empty"] and stats:
            verdict = "emplacement vide : à équiper"
        elif score > 1:
            verdict = "amélioration"
        elif score < -1:
            verdict = "moins bien"
        else:
            verdict = "équivalent"
        out.update(verdict=verdict, score=score, reason="classe de lanceur de sorts : Int/Esprit/Endurance comptés")
    else:
        key = est["key"]
        score = key + est["stamina"] * 0.02 + est["armor"] * 0.002
        if est["empty"] and (stats or item.get("dps")):
            verdict = "emplacement vide : à équiper"
            score += 0.1  # départage à gain égal, sans écraser une vraie amélioration ailleurs
        elif key > 0.3:
            verdict = "amélioration"
        elif key < -0.3:
            verdict = "moins bien"
        elif est["stamina"] > 0 or est["armor"] > 0:
            verdict = "léger plus (endurance/armure)"
        else:
            verdict = "équivalent"
        out.update(verdict=verdict, score=score, reason=why)
    return out


def gain_text(ev: Dict[str, Any]) -> str:
    est = ev.get("gain") or {}
    parts = []
    if "key" in est and abs(est["key"]) >= 0.05:
        parts.append(f"{'+' if est['key'] >= 0 else ''}{F.fr_num(est['key'], 1)} DPS")
    if est.get("stamina"):
        parts.append(f"{'+' if est['stamina'] > 0 else ''}{F.fr_num(est['stamina'])} End")
    if est.get("armor"):
        parts.append(f"{'+' if est['armor'] > 0 else ''}{F.fr_num(est['armor'])} armure")
    return ", ".join(parts)


def describe(item: Dict[str, Any]) -> str:
    st = F.stats_text(F.item_stats(item))
    bits = [item_kind(item)]
    if item.get("dps"):
        bits.append(f"{F.fr_num(item['dps'], 1)} DPS")
    if st:
        bits.append(st)
    if item.get("requiredLevel"):
        bits.append(f"niv. {item['requiredLevel']}")
    return ", ".join(bits)


def quest_rewards(db: Dict[str, Any]) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """[(quête, récompenses)] pour les quêtes dont les récompenses ont été capturées."""
    out = []
    for q in as_list(F.g(db, "quests", "list")):
        r = q.get("rewards")
        if isinstance(r, dict):
            out.append((q, r))
    return out


def best_choice(db: Dict[str, Any], rewards: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """Meilleur objet (au choix ou fixe) pour le perso + toutes les évaluations."""
    evals = []
    for kind in ("choices", "items"):
        for it in as_list(rewards.get(kind)):
            ev = evaluate(db, it)
            ev["item"] = it
            ev["fixed"] = kind == "items"
            evals.append(ev)
    useful = [e for e in evals if e.get("verdict") in ("amélioration", "emplacement vide : à équiper",
                                                         "léger plus (endurance/armure)")]
    best = max(useful, key=lambda e: e["score"]) if useful else None
    return best, evals


def empty_slots(db: Dict[str, Any]) -> List[str]:
    eq = F.g(db, "equipment", "slots", default={}) or {}
    skip = {"ShirtSlot", "TabardSlot"}
    return [fr for slot, fr in F.SLOTS if slot not in skip and not eq.get(slot)]
