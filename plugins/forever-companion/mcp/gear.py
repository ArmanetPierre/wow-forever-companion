"""Règles d'équipement et estimation du gain d'un objet (partagé par compare_item,
get_quest_rewards et get_overview).

Les tables de maîtrise viennent de WoW Classic : Forever reprend les classes de Classic,
mais rien n'est confirmé objet par objet. Chaque conseil qui s'appuie dessus le signale.
Le drapeau `usable` lu en jeu (GetQuestLogChoiceInfo) prime toujours sur ces tables.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import formats as F
from i18n import L, T
from luasv import as_list

AP_PER_DPS = 14.0  # confirmé par l'infobulle de Forever (17/11/2026)

# ---------------------------------------------------------------------------
# Maîtrises par classe [Classic · à vérifier dans Forever]
# classId 4 = armure (1 tissu, 2 cuir, 3 maille, 4 plaques, 6 bouclier, 0 divers : bijoux, anneaux…)
# classId 2 = arme (0 hache 1M, 1 hache 2M, 2 arc, 3 fusil, 4 masse 1M, 5 masse 2M, 6 arme d'hast,
#                   7 épée 1M, 8 épée 2M, 10 bâton, 13 pugilat, 15 dague, 16 arme de jet,
#                   18 arbalète, 19 baguette, 20 canne à pêche)
# ---------------------------------------------------------------------------
# libellés (selon la langue de sortie) : i18n LABELS["armor"] et LABELS["weapon"]


def armor_name(sid: Any, default: str = "") -> str:
    return L("armor", sid, default or T("armure"))


def weapon_name(sid: Any, default: str = "") -> str:
    return L("weapon", sid, default or T("arme"))


# Compétence d'arme (SkillLine) par sous-classe d'arme [Classic, identique dans Forever]
WEAPON_SKILL_IDS = {0: 44, 1: 172, 2: 45, 3: 46, 4: 54, 5: 160, 6: 229, 7: 43, 8: 55, 10: 136, 13: 473,
                    15: 173, 16: 176, 18: 226, 19: 228}

# Mots (français et anglais, normalisés) -> (classId, sous-classes) ; sert aux filtres et à type_arme
TYPE_KEYWORDS = [
    (("arbalete", "crossbow"), 2, (18,)),
    (("arc", "bow", "longbow"), 2, (2,)),
    (("fusil", "arme a feu", "armes a feu", "gun", "firearm", "rifle"), 2, (3,)),
    (("epee a deux mains", "two handed sword", "2h sword"), 2, (8,)),
    (("epee", "sword"), 2, (7, 8)),
    (("hache a deux mains", "two handed axe", "2h axe"), 2, (1,)),
    (("hache", "axe"), 2, (0, 1)),
    (("masse a deux mains", "two handed mace", "2h mace"), 2, (5,)),
    (("masse", "mace"), 2, (4, 5)),
    (("dague", "poignard", "dagger"), 2, (15,)),
    (("arme d hast", "hast", "polearm"), 2, (6,)),
    (("baton", "staff", "stave"), 2, (10,)),
    (("pugilat", "poing", "fist", "fist weapon"), 2, (13,)),
    (("arme de jet", "jet", "thrown", "throwing"), 2, (16,)),
    (("baguette", "wand"), 2, (19,)),
    (("canne a peche", "fishing pole"), 2, (20,)),
    (("tissu", "cloth"), 4, (1,)),
    (("cuir", "leather"), 4, (2,)),
    (("maille", "mail", "chain"), 4, (3,)),
    (("plaque", "plate"), 4, (4,)),
    (("bouclier", "shield"), 4, (6,)),
]


def _singular_tokens(text: str) -> str:
    return " ".join(w[:-1] if len(w) > 3 and w.endswith(("s", "x")) else w for w in F.norm_key(text).split())


def parse_type(text: Any) -> Optional[Tuple[int, Tuple[int, ...]]]:
    """'arbalète', 'crossbow', 'cuir', 'leather', 'Two-Handed Sword'… -> (classId, sous-classes)."""
    n = f" {_singular_tokens(text)} "
    if not n.strip():
        return None
    for words, cid, subs in TYPE_KEYWORDS:
        for w in words:
            if f" {_singular_tokens(w)} " in n:
                return cid, subs
    return None

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
        return weapon_name(sid, item.get("subType") or "")
    if cid == 4:
        if sid == 0:
            return L("misc_kind", item.get("equipLoc"), L("armor", 0))
        if item.get("equipLoc") == "INVTYPE_CLOAK":
            return L("misc_kind", "INVTYPE_CLOAK")
        return armor_name(sid, item.get("subType") or "")
    return (item.get("subType") or item.get("type") or T("objet")).lower()


def proficiency(cls: str, level: int, item: Dict[str, Any]) -> Tuple[Optional[bool], str]:
    """(portable ?, raison). None = inconnu. Le drapeau `usable` du jeu prime."""
    req = item.get("requiredLevel") or 0
    if req and level and req > level:
        return False, T("niveau requis {n}", n=req)
    if item.get("usable") is False:
        return False, T("le jeu l'indique inutilisable pour ce perso")
    cid, sid = item.get("classId"), item.get("subclassId")
    if cid == 4 and sid not in (None, 0) and item.get("equipLoc") != "INVTYPE_CLOAK":
        table = ARMOR.get(cls)
        if table is None:
            return None, T("classe inconnue")
        if sid not in table:
            return False, T("{kind} non portable par la classe [Classic]", kind=armor_name(sid))
        if level and table[sid] > level:
            return False, T("{kind} portable seulement au niveau {n} [Classic]", kind=armor_name(sid), n=table[sid])
    if cid == 2 and sid is not None and sid != 20:
        allowed = WEAPONS.get(cls)
        if allowed is None:
            return None, T("classe inconnue")
        if sid not in allowed:
            return False, T("{kind} non maîtrisée par la classe [Classic]", kind=weapon_name(sid))
    if item.get("usable") is True:
        return True, T("utilisable (indiqué par le jeu)")
    return True, ""


def target_slots(cls: str, level: int, item: Dict[str, Any]) -> List[str]:
    slots = list(EQUIPLOC_SLOTS.get(item.get("equipLoc") or "", []))
    if item.get("equipLoc") == "INVTYPE_WEAPON":
        dw = DUAL_WIELD.get(cls)
        if not dw or (level and level < dw):
            slots = ["MainHandSlot"]
    return slots


TWIN_SLOTS = ("Finger0Slot", "Finger1Slot", "Trinket0Slot", "Trinket1Slot")


def weakest_slot(db: Dict[str, Any], slots: List[str], item: Dict[str, Any]) -> str:
    """Emplacement à remplacer parmi des jumeaux (doigts, bijoux, armes) : vide d'abord, sinon le plus faible,
    c'est-à-dire celui où l'objet proposé rapporte le plus."""
    if len(slots) <= 1:
        return slots[0] if slots else ""
    eq = F.g(db, "equipment", "slots", default={}) or {}
    for s in slots:
        if not eq.get(s):
            return s
    cls = F.g(db, "identity", "classFile") or ""
    cstats = F.item_stats(item)
    dps = float(item["dps"]) if item.get("dps") else None

    def gain(s: str) -> float:
        est = estimate(db, s, cstats, dps, eq.get(s))
        main = est["ranged"] if cls == "HUNTER" else est["melee"]
        stam = float(cstats.get("STAMINA", 0) or 0) - float(F.item_stats(eq.get(s) or {}).get("STAMINA", 0) or 0)
        return main + 0.01 * stam

    return max(slots, key=gain)


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

    d_rap = delta("AGILITY") * rap_agi + delta("ATTACK_POWER") + delta("RANGED_ATTACK_POWER")
    d_map = delta("AGILITY") * map_agi + delta("STRENGTH") * map_str + delta("ATTACK_POWER")
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
        "stamina": delta("STAMINA"), "armor": delta("ARMOR"), "int": delta("INTELLECT"), "spi": delta("SPIRIT"),
        "main_ranged": 1.0 if main_ranged else 0.0, "empty": 0.0 if cur else 1.0,
        "r_now": r_now if r_now is not None else float("nan"), "m_now": m_now if m_now is not None else float("nan"),
        "odps": odps,
    }


CASTERS = {"MAGE", "PRIEST", "WARLOCK"}
PHYSICAL = {"HUNTER", "ROGUE", "WARRIOR"}
PHYS_STATS = {"AGILITY", "STRENGTH", "ATTACK_POWER", "RANGED_ATTACK_POWER"}
CAREFUL_AIM = ("visee minutieuse", "careful aim")


def caster_stat(k: str) -> bool:
    return k in ("INTELLECT", "SPIRIT") or any(w in k for w in ("SPELL", "HEAL", "MANA"))


def careful_aim(db: Dict[str, Any]) -> int:
    """Rang du talent Forever « Visée minutieuse » (Int convertie en PA distance), 0 s'il n'est pas capturé."""
    for n in F.g(db, "talents", "nodes", default=[]) or []:
        if isinstance(n, dict) and F.norm_key(n.get("name") or "") in CAREFUL_AIM:
            return int(n.get("rank") or 0)
    return 0


def off_role(db: Dict[str, Any], stats: Dict[str, float]) -> List[str]:
    """Stats de l'objet toutes inutiles pour la classe (sorts pour un chasseur, Agi/For pour un mage) :
    renvoie leurs clés, sinon []. Classes hybrides : jamais hors rôle."""
    cls = F.g(db, "identity", "classFile") or ""
    keys = [k for k in stats if k != "ARMOR" and not k.endswith("_RESISTANCE") and stats[k]]
    if not keys:
        return []
    if cls in PHYSICAL:
        useless = [k for k in keys if caster_stat(k) and not (k == "INTELLECT" and careful_aim(db) > 0)]
    elif cls in CASTERS:
        useless = [k for k in keys if k in PHYS_STATS]
    else:
        return []
    # objet de soigneur avec un peu d'endurance : hors rôle si les stats inutiles dominent
    wasted = sum(abs(float(stats[k])) for k in useless)
    kept = sum(abs(float(stats[k])) for k in keys if k not in useless)
    return useless if useless and wasted > kept else []


USEFUL = ("upgrade", "empty_slot", "minor_plus")


def _verdict(out: Dict[str, Any], code: str, **kw: Any) -> None:
    out.update(code=code, verdict=L("verdict", code, code), **kw)


def evaluate(db: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
    """Évalue un objet pour le perso : code (upgrade, empty_slot, minor_plus, worse, equivalent,
    not_for_you, not_equippable), verdict (libellé dans la langue de sortie), emplacement, gain, raison."""
    cls = F.g(db, "identity", "classFile") or ""
    level = F.g(db, "progression", "level") or F.g(db, "identity", "level") or 0
    out: Dict[str, Any] = {"name": item.get("name") or T("objet {id}", id=item.get("itemId")), "kind": item_kind(item)}
    slots = target_slots(cls, level, item)
    if not slots:
        _verdict(out, "not_equippable", score=-99.0, reason=T("ce n'est pas un équipement"))
        return out
    ok, why = proficiency(cls, level, item)
    if ok is False:
        _verdict(out, "not_for_you", score=-50.0, reason=why, slot=slots[0])
        return out
    eq = F.g(db, "equipment", "slots", default={}) or {}
    stats = F.item_stats(item)
    useless = [] if item.get("dps") else off_role(db, stats)
    if useless:
        _verdict(out, "not_for_you", score=-20.0, slot=slots[0], slot_fr=F.slot_label(slots[0]),
                 reason=T("stats sans effet pour ta classe ({stats})",
                          stats=", ".join(F.stat_name(k) for k in useless)))
        return out
    iid = item.get("itemId")
    worn_in = [s for s, it in eq.items() if isinstance(it, dict) and iid and it.get("itemId") == iid]
    if worn_in:
        # même objet déjà porté : un 2e exemplaire ne vaut que pour l'autre emplacement d'une paire
        others = [s for s in slots if s not in worn_in]
        if not others:
            _verdict(out, "already_worn", score=-1.0, slot=worn_in[0], slot_fr=F.slot_label(worn_in[0]),
                     slot_label=F.slot_label(worn_in[0]),
                     reason=T("déjà porté ({slot})", slot=F.slot_label(worn_in[0])))
            return out
        slots = others
    best = None
    for s in slots:
        est = estimate(db, s, stats, item.get("dps"))
        if best is None or est["key"] > best[1]["key"] or (est["empty"] and not best[1]["empty"]):
            best = (s, est)
    slot, est = best  # type: ignore[misc]
    cur = eq.get(slot)
    out.update(slot=slot, slot_fr=F.slot_label(slot), slot_label=F.slot_label(slot), gain=est,
               replaces=(cur or {}).get("name"))
    caster = cls in CASTERS
    if caster:
        score = est["int"] + est["spi"] * 0.5 + est["stamina"] * 0.5 + est["armor"] * 0.01
        if est["empty"] and stats:
            code = "empty_slot"
        elif score > 1:
            code = "upgrade"
        elif score < -1:
            code = "worse"
        else:
            code = "equivalent"
        _verdict(out, code, score=score, reason=T("classe de lanceur de sorts : Int/Esprit/Endurance comptés"))
    else:
        key = est["key"]
        score = key + est["stamina"] * 0.02 + est["armor"] * 0.002
        ca = careful_aim(db) if cls == "HUNTER" else 0
        if ca and est["int"]:
            # Visée minutieuse convertit l'Int en PA distance ; coefficient Forever inconnu : départage seulement
            score += est["int"] * 0.01
            why = T("Intelligence comptée en départage seulement : Visée minutieuse {r}/5 la convertit en PA distance, "
                    "coefficient Forever non vérifié [Forever · probable]", r=ca)
        if est["empty"] and (item.get("dps") or key > 0 or est["stamina"] > 0 or est["armor"] > 0
                             or (ca and est["int"] > 0)):
            code = "empty_slot"
            score += 0.1  # départage à gain égal, sans écraser une vraie amélioration ailleurs
        elif key > 0.3:
            code = "upgrade"
        elif key < -0.3:
            code = "worse"
        elif est["stamina"] > 0 or est["armor"] > 0 or (ca and est["int"] > 0):
            code = "minor_plus"
        else:
            code = "equivalent"
        _verdict(out, code, score=score, reason=why)
    if worn_in and out.get("code") in USEFUL:
        out["verdict"] = T("déjà porté ({worn}) ; un 2e exemplaire en {slot} : {verdict}",
                           worn=F.slot_label(worn_in[0]), slot=F.slot_label(slot), verdict=out["verdict"])
        out["second_copy"] = True
    return out


def gain_text(ev: Dict[str, Any]) -> str:
    est = ev.get("gain") or {}
    parts = []
    if "key" in est and abs(est["key"]) >= 0.05:
        parts.append(f"{'+' if est['key'] >= 0 else ''}{F.num(est['key'], 1)} DPS")
    if est.get("stamina"):
        parts.append(f"{'+' if est['stamina'] > 0 else ''}{F.num(est['stamina'])} {F.stat_name('STAMINA')}")
    if est.get("armor"):
        parts.append(f"{'+' if est['armor'] > 0 else ''}{F.num(est['armor'])} {F.stat_name('ARMOR').lower()}")
    return ", ".join(parts)


def describe(item: Dict[str, Any]) -> str:
    st = F.stats_text(F.item_stats(item))
    bits = [item_kind(item)]
    if item.get("dps"):
        bits.append(f"{F.num(item['dps'], 1)} DPS")
    if st:
        bits.append(st)
    if item.get("requiredLevel"):
        bits.append(T("niv. {n}", n=item['requiredLevel']))
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
    useful = [e for e in evals if e.get("code") in USEFUL]
    best = max(useful, key=lambda e: e["score"]) if useful else None
    return best, evals


def empty_slots(db: Dict[str, Any]) -> List[str]:
    eq = F.g(db, "equipment", "slots", default={}) or {}
    skip = {"ShirtSlot", "TabardSlot"}
    return [lab for slot, lab in F.slots_localized() if slot not in skip and not eq.get(slot)]


def reward_pick(ev: Optional[Dict[str, Any]]) -> str:
    if not ev:
        return ""
    it = ev["item"]
    gain = gain_text(ev)
    where = f"{ev.get('slot_label', ev.get('slot_fr', '?'))}" + (
        T(", remplace {name}", name=ev['replaces']) if ev.get("replaces") else T(", emplacement vide"))
    return (f"**{it.get('name')}** ({describe(it)}) — {ev['verdict']}"
            + (f", {gain}" if gain else "") + f" [{where}]" + (T(" (fixe)") if ev.get("fixed") else T(" (au choix)")))


def quest_where(q: Dict[str, Any]) -> str:
    pos = q.get("position") or {}
    return f" · `/way {pos.get('x')} {pos.get('y')}`" if pos.get("x") is not None else ""
