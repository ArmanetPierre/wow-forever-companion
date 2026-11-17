"""Mise en forme des données ForeverScribe en texte français compact.

Utilisé à la fois par le serveur MCP (réponses des outils) et par la synchro
(sections automatiques de profil.md).
"""

from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from luasv import as_list

# ----------------------------------------------------------------------------
# Libellés
# ----------------------------------------------------------------------------

SLOTS: List[Tuple[str, str]] = [
    ("HeadSlot", "Tête"), ("NeckSlot", "Cou"), ("ShoulderSlot", "Épaules"),
    ("BackSlot", "Dos"), ("ChestSlot", "Torse"), ("ShirtSlot", "Chemise"),
    ("TabardSlot", "Tabard"), ("WristSlot", "Poignets"), ("HandsSlot", "Mains"),
    ("WaistSlot", "Taille"), ("LegsSlot", "Jambes"), ("FeetSlot", "Pieds"),
    ("Finger0Slot", "Doigt 1"), ("Finger1Slot", "Doigt 2"),
    ("Trinket0Slot", "Bijou 1"), ("Trinket1Slot", "Bijou 2"),
    ("MainHandSlot", "Main droite"), ("SecondaryHandSlot", "Main gauche"),
    ("RangedSlot", "Distance"),
]
SLOT_FR = dict(SLOTS)

# Synonymes acceptés pour désigner un emplacement
SLOT_ALIASES = {
    "tete": "HeadSlot", "casque": "HeadSlot", "head": "HeadSlot",
    "cou": "NeckSlot", "collier": "NeckSlot", "amulette": "NeckSlot", "neck": "NeckSlot",
    "epaules": "ShoulderSlot", "epaulieres": "ShoulderSlot", "shoulder": "ShoulderSlot",
    "dos": "BackSlot", "cape": "BackSlot", "back": "BackSlot",
    "torse": "ChestSlot", "plastron": "ChestSlot", "tunique": "ChestSlot", "chest": "ChestSlot",
    "chemise": "ShirtSlot", "tabard": "TabardSlot",
    "poignets": "WristSlot", "brassards": "WristSlot", "wrist": "WristSlot",
    "mains": "HandsSlot", "gants": "HandsSlot", "hands": "HandsSlot",
    "taille": "WaistSlot", "ceinture": "WaistSlot", "waist": "WaistSlot",
    "jambes": "LegsSlot", "pantalon": "LegsSlot", "jambieres": "LegsSlot", "legs": "LegsSlot",
    "pieds": "FeetSlot", "bottes": "FeetSlot", "chaussures": "FeetSlot", "feet": "FeetSlot",
    "doigt": "Finger0Slot", "doigt1": "Finger0Slot", "doigt 1": "Finger0Slot", "anneau": "Finger0Slot",
    "bague": "Finger0Slot", "doigt2": "Finger1Slot", "doigt 2": "Finger1Slot",
    "bijou": "Trinket0Slot", "bijou1": "Trinket0Slot", "bijou 1": "Trinket0Slot",
    "bijou2": "Trinket1Slot", "bijou 2": "Trinket1Slot", "trinket": "Trinket0Slot",
    "main droite": "MainHandSlot", "arme": "MainHandSlot", "mainhand": "MainHandSlot",
    "arme de melee": "MainHandSlot", "melee": "MainHandSlot",
    "main gauche": "SecondaryHandSlot", "offhand": "SecondaryHandSlot", "bouclier": "SecondaryHandSlot",
    "distance": "RangedSlot", "arme a distance": "RangedSlot", "ranged": "RangedSlot",
    "arc": "RangedSlot", "fusil": "RangedSlot", "arbalete": "RangedSlot", "baguette": "RangedSlot",
}

RESIST_FR = {1: "Sacré", 2: "Feu", 3: "Nature", 4: "Givre", 5: "Ombre", 6: "Arcanes"}
STAT_FR = {
    "STRENGTH": "For", "AGILITY": "Agi", "STAMINA": "End", "INTELLECT": "Int",
    "SPIRIT": "Esp", "ATTACK_POWER": "PA", "RANGED_ATTACK_POWER": "PA distance",
    "SPELL_POWER": "Puiss. des sorts", "HEALING_POWER": "Soins", "CRIT_RATING": "Crit",
    "HIT_RATING": "Toucher", "DEFENSE_SKILL_RATING": "Défense", "DODGE_RATING": "Esquive",
    "PARRY_RATING": "Parade", "BLOCK_RATING": "Blocage", "BLOCK_VALUE": "Valeur de blocage",
    "MANA_REGENERATION": "Mana/5 s", "HEALTH_REGENERATION": "PV/5 s",
    "FIRE_RESISTANCE": "Rés. feu", "FROST_RESISTANCE": "Rés. givre",
    "NATURE_RESISTANCE": "Rés. nature", "SHADOW_RESISTANCE": "Rés. ombre",
    "ARCANE_RESISTANCE": "Rés. arcanes", "HOLY_RESISTANCE": "Rés. sacré",
    "DAMAGE_PER_SECOND": "DPS",
}
STAT_ORDER = ["Agi", "For", "End", "Int", "Esp", "PA", "PA distance", "Crit", "Toucher"]

QUALITY_FR = {0: "médiocre", 1: "commun", 2: "inhabituel", 3: "rare", 4: "épique", 5: "légendaire",
              6: "artefact", 7: "héritage"}
HAPPINESS_FR = {1: "mécontent", 2: "content", 3: "heureux"}
ROLE_FR = {"DAMAGER": "DPS", "TANK": "Tank", "HEALER": "Soins"}
PROF_SLOT_FR = {"primary1": "principal", "primary2": "principal", "cooking": "secondaire",
                "fishing": "secondaire", "firstAid": "secondaire", "archaeology": "secondaire"}


# ----------------------------------------------------------------------------
# Outils de formatage
# ----------------------------------------------------------------------------

def fr_num(value: Any, decimals: int = 0) -> str:
    """12345.6 -> '12 345,6' (espace fine insécable évitée pour rester lisible partout)."""
    if value is None:
        return "?"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    s = f"{v:,.{decimals}f}".replace(",", " ").replace(".", ",")
    if decimals and "," in s:
        s = s.rstrip("0").rstrip(",")
    return s


def pct(part: Any, total: Any, decimals: int = 0) -> str:
    try:
        return fr_num(100.0 * float(part) / float(total), decimals) + " %"
    except (TypeError, ValueError, ZeroDivisionError):
        return "?"


def duration(seconds: Any) -> str:
    """173365 -> '48 h 09 min'."""
    try:
        s = int(seconds)
    except (TypeError, ValueError):
        return "?"
    if s < 60:
        return f"{s} s"
    m = s // 60
    if m < 60:
        return f"{m} min"
    h, m = divmod(m, 60)
    if h < 48:
        return f"{h} h {m:02d} min"
    d, h = divmod(h, 24)
    return f"{d} j {h} h"


def age(epoch: Any, now: Optional[float] = None) -> str:
    """Âge d'une capture : 'il y a 3 min'."""
    try:
        delta = (now or time.time()) - float(epoch)
    except (TypeError, ValueError):
        return "date inconnue"
    if delta < 0:
        delta = 0
    if delta < 90:
        return "il y a moins de 2 min"
    if delta < 3600:
        return f"il y a {int(delta // 60)} min"
    if delta < 86400:
        h = int(delta // 3600)
        m = int((delta % 3600) // 60)
        return f"il y a {h} h {m:02d}" if m else f"il y a {h} h"
    days = int(delta // 86400)
    return f"il y a {days} jour{'s' if days > 1 else ''}"


def local_time(epoch: Any, fmt: str = "%d/%m/%Y %H:%M") -> str:
    try:
        return datetime.fromtimestamp(float(epoch)).strftime(fmt)
    except (TypeError, ValueError, OSError):
        return "?"


def money(copper: Any) -> str:
    try:
        c = int(copper)
    except (TypeError, ValueError):
        return "?"
    g, rest = divmod(c, 10000)
    s, c = divmod(rest, 100)
    parts = []
    if g:
        parts.append(f"{g} po")
    if s or g:
        parts.append(f"{s} pa")
    parts.append(f"{c} pc")
    return " ".join(parts)


def clean_text(text: Any) -> str:
    """Nettoie les codes du jeu : |4singulier:pluriel; , couleurs, retours à la ligne."""
    if text is None:
        return ""
    s = str(text)
    s = re.sub(r"\s*\|4([^:;|]*):([^;|]*);", "", s)  # « personnage tué » redondant
    s = re.sub(r"\|c[nN]?[0-9A-Za-z_]*:?", "", s)
    s = re.sub(r"\|r", "", s)
    s = re.sub(r"\|H[^|]*\|h(\[[^\]]*\])\|h", r"\1", s)
    s = s.replace("\r", " ").replace("\n", " ").replace("\xa0", " ")
    return re.sub(r"\s{2,}", " ", s).strip()


def norm_key(text: Any) -> str:
    """Minuscules sans accents ni ponctuation, pour comparer des noms."""
    import unicodedata

    s = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def stat_label(key: str) -> Optional[str]:
    """ITEM_MOD_AGILITY_SHORT -> 'Agi' ; RESISTANCE0_NAME -> 'Armure'."""
    m = re.match(r"RESISTANCE(\d)_NAME", key)
    if m:
        n = int(m.group(1))
        return "Armure" if n == 0 else "Rés. " + RESIST_FR.get(n, str(n)).lower()
    k = re.sub(r"^ITEM_MOD_", "", key)
    k = re.sub(r"_SHORT$|_NAME$", "", k)
    return STAT_FR.get(k, k.replace("_", " ").capitalize())


def item_stats(item: Dict[str, Any]) -> Dict[str, float]:
    """Stats d'un objet avec libellés français, sans doublons de résistance."""
    out: Dict[str, float] = {}
    raw = item.get("stats") or {}
    if not isinstance(raw, dict):
        return out
    for key, val in raw.items():
        label = stat_label(str(key))
        if not label or not isinstance(val, (int, float)):
            continue
        if label in out and label.startswith("Rés."):
            continue  # ITEM_MOD_FIRE_RESISTANCE et RESISTANCE2_NAME décrivent la même chose
        out[label] = out.get(label, 0) + val
    return out


def stats_text(stats: Dict[str, float], with_armor: bool = False) -> str:
    keys = sorted(stats, key=lambda k: (STAT_ORDER.index(k) if k in STAT_ORDER else 50, k))
    parts = []
    for k in keys:
        if k == "Armure" and not with_armor:
            continue
        v = stats[k]
        parts.append(f"{'+' if v > 0 else ''}{fr_num(v, 1)} {k}")
    return ", ".join(parts)


# ----------------------------------------------------------------------------
# Accès sûr aux données
# ----------------------------------------------------------------------------

def g(data: Any, *path: Any, default: Any = None) -> Any:
    cur = data
    for p in path:
        if isinstance(cur, dict):
            cur = cur.get(p)
        elif isinstance(cur, list) and isinstance(p, int) and 0 <= p < len(cur):
            cur = cur[p]
        else:
            return default
        if cur is None:
            return default
    return cur


def captured_at(db: Dict[str, Any]) -> Optional[float]:
    return g(db, "meta", "capturedAt")


def domain_age(db: Dict[str, Any], domain: str, now: Optional[float] = None) -> str:
    ts = g(db, "meta", "domainsUpdatedAt", domain)
    return age(ts, now) if ts else "jamais capturé"


# ----------------------------------------------------------------------------
# Blocs communs
# ----------------------------------------------------------------------------

def label(db: Dict[str, Any]) -> str:
    ident = g(db, "identity", default={})
    return f"{ident.get('name', '?')}-{ident.get('suffix', '?')}"


def header(db: Dict[str, Any], now: Optional[float] = None) -> str:
    """'Brannok · Nain Chasseur 25 · Les Paluns · capturé il y a 3 min'."""
    ident = g(db, "identity", default={})
    level = g(db, "progression", "level") or ident.get("level", "?")
    zone = g(db, "position", "zone") or g(db, "position", "mapName") or "zone inconnue"
    cap = captured_at(db)
    text = f"{ident.get('name', '?')} · {ident.get('race', '?')} {ident.get('class', '?')} {level} · {zone}"
    text += f" · capturé {age(cap, now)}" if cap else " · jamais capturé"
    if cap and (now or time.time()) - cap > 3600:
        text += " (Ctrl+Maj+S en jeu pour actualiser)"
    return text


def problems(db: Dict[str, Any]) -> List[str]:
    meta = g(db, "meta", default={})
    out = []
    for dom, err in (meta.get("errors") or {}).items():
        out.append(f"{dom} : erreur ({clean_text(g(err, 'message', default=err))})")
    for dom, lst in (meta.get("missing") or {}).items():
        lst = as_list(lst)
        if lst:
            out.append(f"{dom} : fonctions absentes ({', '.join(map(str, lst[:5]))})")
    for dom, lst in (meta.get("callErrors") or {}).items():
        lst = as_list(lst)
        if lst:
            out.append(f"{dom} : {len(lst)} appel(s) en erreur")
    return out


# ----------------------------------------------------------------------------
# Rendus par domaine
# ----------------------------------------------------------------------------

def render_identity(db: Dict[str, Any]) -> List[str]:
    ident = g(db, "identity", default={})
    prog = g(db, "progression", default={})
    tal = g(db, "talents", default={})
    lines = [
        f"- **{label(db)}** · {ident.get('race', '?')} {ident.get('class', '?')} niveau "
        f"{prog.get('level', ident.get('level', '?'))} · {ident.get('faction', '?')} · "
        f"{ident.get('region', '?')} · ruleset {ident.get('ruleset', '?')}"
        + (" · Hardcore" if ident.get("hardcore") else ""),
    ]
    guild = ident.get("guild")
    lines.append(f"- Guilde : {guild.get('name')} ({guild.get('rank', '?')})" if isinstance(guild, dict)
                 else "- Guilde : aucune")
    if tal:
        lines.append(
            f"- Spé : {tal.get('specName', '?')} ({ROLE_FR.get(tal.get('role'), tal.get('role', '?'))}) · "
            f"{tal.get('spent', '?')} points de talent dépensés, {tal.get('unspent', '?')} libre(s)")
    return lines


def render_progression(db: Dict[str, Any]) -> List[str]:
    p = g(db, "progression", default={})
    if not p:
        return ["- Progression : jamais capturée"]
    lines = []
    if p.get("level") == p.get("maxLevel"):
        lines.append(f"- Niveau maximum ({p.get('level')})")
    else:
        rested = p.get("xpRested") or 0
        rs = g(p, "restState", "name")
        lines.append(
            f"- XP : {fr_num(p.get('xp'))} / {fr_num(p.get('xpMax'))} ({pct(p.get('xp'), p.get('xpMax'), 1)})"
            f" · reste {fr_num((p.get('xpMax') or 0) - (p.get('xp') or 0))}"
            + (f" · repos {fr_num(rested)}" if rested else "")
            + (f" · {rs}" if rs else "")
            + (" · au repos" if p.get("isResting") else ""))
    tp = p.get("timePlayed") or {}
    if tp:
        lines.append(f"- Temps de jeu : {duration(tp.get('total'))} ({duration(tp.get('level'))} à ce niveau)")
    return lines


def way(pos: Dict[str, Any]) -> str:
    if not isinstance(pos, dict) or pos.get("x") is None:
        return ""
    return f"{fr_num(pos.get('x'), 1)} / {fr_num(pos.get('y'), 1)}"


def render_position(db: Dict[str, Any]) -> List[str]:
    pos = g(db, "position", default={})
    if not pos:
        return ["- Position : jamais capturée"]
    where = pos.get("zone") or pos.get("mapName") or "?"
    if pos.get("subZone"):
        where += f" — {pos['subZone']}"
    coords = way(pos)
    line = f"- {where}" + (f" ({coords} · `/way {pos.get('x')} {pos.get('y')}`)" if coords else "")
    if g(pos, "instance", "inInstance"):
        line += f" · en instance : {g(pos, 'instance', 'name')} {g(pos, 'instance', 'difficultyName', default='')}"
    line += f" · foyer : {pos.get('bind', '?')}"
    return [line]


def render_combat(db: Dict[str, Any]) -> List[str]:
    st = g(db, "stats", default={})
    if not st:
        return ["- Stats : jamais capturées"]
    prim = st.get("primary") or {}

    def ps(name: str) -> str:
        return fr_num(g(prim, name, "effective"))

    r, m = st.get("ranged") or {}, st.get("melee") or {}
    lines = [
        f"- Caractéristiques : For {ps('strength')} · Agi {ps('agility')} · End {ps('stamina')} · "
        f"Int {ps('intellect')} · Esp {ps('spirit')}",
        f"- PV {fr_num(st.get('health'))} · {g(st, 'power', 'token', default='ressource').capitalize()} "
        f"{fr_num(g(st, 'power', 'max'))} · armure {fr_num(g(st, 'armor', 'effective'))} · "
        f"ilvl moyen {fr_num(g(st, 'itemLevel', 'equipped'), 1)}",
    ]
    if r.get("attackPower") is not None and r.get("speed"):
        lines.append(
            f"- Distance : PA {fr_num(r.get('attackPower'))} ({fr_num(r.get('attackPowerBase'))}"
            f" + {fr_num(r.get('attackPowerPos'))}) · {fr_num(r.get('minDamage'))}–{fr_num(r.get('maxDamage'))}"
            f" toutes les {fr_num(r.get('speed'), 2)} s ({fr_num(r.get('dps'), 1)} DPS hors crit)"
            f" · crit {fr_num(r.get('crit'), 1)} %")
    if m.get("attackPower") is not None:
        lines.append(
            f"- Mêlée : PA {fr_num(m.get('attackPower'))} · {fr_num(m.get('minDamage'))}–{fr_num(m.get('maxDamage'))}"
            f" toutes les {fr_num(m.get('speed'), 2)} s ({fr_num(m.get('dps'), 1)} DPS) · crit {fr_num(m.get('crit'), 1)} %"
            f" · esquive {fr_num(m.get('dodge'), 1)} % · parade {fr_num(m.get('parry'), 1)} %")
    res = st.get("resistances") or {}
    nz = {k: v for k, v in res.items() if v}
    if nz:
        names = {"holy": "sacré", "fire": "feu", "nature": "nature", "frost": "givre",
                 "shadow": "ombre", "arcane": "arcanes"}
        lines.append("- Résistances : " + ", ".join(f"{names.get(k, k)} {v}" for k, v in nz.items()))
    return lines


def render_equipment_table(db: Dict[str, Any], show_tooltip: bool = False) -> List[str]:
    eq = g(db, "equipment", default={})
    slots = eq.get("slots") or {}
    if not slots:
        return ["- Équipement : jamais capturé"]
    lines = ["| Emplacement | Objet | ilvl | Stats | Durabilité |", "|---|---|---|---|---|"]
    low = []
    for slot, fr in SLOTS:
        it = slots.get(slot)
        if not it:
            continue
        st = item_stats(it)
        stxt = stats_text(st)
        if it.get("dps"):
            stxt = f"{fr_num(it['dps'], 1)} DPS" + (", " + stxt if stxt else "")
        d = it.get("durability") or {}
        dtxt = f"{d.get('current')}/{d.get('max')}" if d.get("max") else "—"
        if d.get("max") and d.get("current", 0) / d["max"] < 0.25:
            low.append(fr)
        q = QUALITY_FR.get(it.get("quality"), "")
        name = it.get("name") or f"objet {it.get('itemId')}"
        lines.append(f"| {fr} | {name}{' (' + q + ')' if q in ('rare', 'épique', 'légendaire') else ''} "
                     f"| {it.get('itemLevel', '?')} | {stxt or '—'} | {dtxt} |")
        if show_tooltip and it.get("tooltip"):
            lines.append(f"|  | _{clean_text(' · '.join(map(str, as_list(it['tooltip'])[1:])))}_ |  |  |  |")
    if eq.get("repairCost"):
        lines.append(f"\nRéparation complète : {money(eq['repairCost'])}.")
    if low:
        lines.append(f"Durabilité faible : {', '.join(low)}.")
    return lines


def render_talents(db: Dict[str, Any]) -> List[str]:
    t = g(db, "talents", default={})
    if not t:
        return ["- Talents : jamais capturés"]
    lines = [f"- Spé : {t.get('specName', '?')} ({ROLE_FR.get(t.get('role'), t.get('role', '?'))}) · "
             f"{t.get('spent', '?')} points dépensés, {t.get('unspent', '?')} libre(s) · "
             f"{t.get('numSpecs', 1)} spé(s) disponible(s)"]
    nodes = as_list(t.get("nodes"))
    if nodes:
        nodes = sorted(nodes, key=lambda n: (n.get("posY", 0), n.get("posX", 0)))
        lines.append("- Talents pris : " + ", ".join(
            f"{n.get('name', n.get('nodeId'))} {n.get('rank', '?')}/{n.get('maxRank', '?')}" for n in nodes))
    return lines


def render_professions(db: Dict[str, Any], with_recipes: bool = False) -> List[str]:
    pr = g(db, "professions", default={})
    profs = as_list(pr.get("professions"))
    if not profs:
        return ["- Métiers : aucun capturé"]
    lines = ["| Métier | Type | Niveau |", "|---|---|---|"]
    for p in profs:
        lines.append(f"| {p.get('name')} | {PROF_SLOT_FR.get(p.get('slot'), '')} | "
                     f"{p.get('rank')}/{p.get('max')}"
                     + (f" (+{p['modifier']})" if p.get("modifier") else "") + " |")
    recipes = g(db, "recipes", default={})
    if with_recipes:
        if not recipes:
            lines.append("\nRecettes : jamais capturées (ouvre la fenêtre du métier en jeu, puis Ctrl+Maj+S (ou /sync)).")
        for prof, info in (recipes or {}).items():
            recs = as_list(info.get("recipes"))
            colors = {0: "orange", 1: "jaune", 2: "verte", 3: "grise"}
            useful = [r for r in recs if r.get("learned") and r.get("difficulty") in (0, 1)]
            lines.append(f"\n**{prof}** : {len(recs)} recettes connues "
                         f"(capturé {age(info.get('capturedAt'))}).")
            if useful:
                lines.append("Recettes qui font encore monter le métier : " + ", ".join(
                    f"{r.get('name')} ({colors.get(r.get('difficulty'))}"
                    + (f", {r['available']} faisables" if r.get("available") else "") + ")"
                    for r in useful[:25]))
    elif recipes:
        lines.append(f"\nRecettes capturées pour : {', '.join(recipes)}.")
    return lines


def render_pet(db: Dict[str, Any]) -> List[str]:
    pet = g(db, "pet", default={})
    if not pet:
        return ["- Familier : jamais capturé"]
    cur = pet.get("current") if pet.get("active") else None
    lines = []
    shown = cur or pet.get("lastSeen")
    if shown:
        hap = g(shown, "happiness", "level")
        tp = shown.get("trainingPoints") or {}
        status = "actif" if cur else f"renvoyé (vu {age(pet.get('lastSeenAt'))})"
        lines.append(
            f"- {shown.get('name', '?')} ({shown.get('family', '?')}) niveau {shown.get('level', '?')}, {status}"
            + (f" · {HAPPINESS_FR.get(hap, hap)} ({g(shown, 'happiness', 'damagePct')} % dégâts)" if hap else "")
            + (f" · {clean_text(shown.get('loyalty'))}" if shown.get("loyalty") else ""))
        if shown.get("xpMax"):
            lines.append(f"- XP familier : {fr_num(shown.get('xp'))} / {fr_num(shown.get('xpMax'))}"
                         f" · points de dressage {tp.get('available', '?')} libres sur {tp.get('total', '?')}")
        if shown.get("food"):
            lines.append(f"- Mange : {', '.join(as_list(shown.get('food')))}")
        abil = [a for a in as_list(shown.get("abilities"))
                if "Posture" not in str(a.get("subName", "")) and "Commande" not in str(a.get("subName", ""))]
        if abil:
            lines.append("- Techniques : " + ", ".join(
                f"{a.get('name')}" + (f" ({a['subName']})" if a.get("subName") else "") for a in abil))
    else:
        lines.append("- Pas de familier actif")
    stabled = as_list(g(pet, "stable", "stabled"))
    if stabled:
        lines.append("- À l'écurie : " + ", ".join(
            f"{s.get('name')} ({s.get('family')} {s.get('level')})" for s in stabled))
    return lines


def render_bags_summary(db: Dict[str, Any]) -> List[str]:
    b = g(db, "bags", default={})
    lines = [f"- Argent : {g(db, 'money', 'text') or money(g(db, 'money', 'copper'))}"]
    if b:
        free, total = b.get("freeSlots"), b.get("totalSlots")
        lines.append(f"- Sacs : {free} place(s) libre(s) sur {total}"
                     + (" — presque pleins" if isinstance(free, int) and free <= 3 else ""))
        ammo = b.get("ammo") or {}
        if ammo.get("total") is not None:
            detail = ", ".join(f"{k} ×{v}" for k, v in (ammo.get("items") or {}).items())
            lines.append(f"- Munitions : {fr_num(ammo.get('total'))}" + (f" ({detail})" if detail else ""))
    return lines


def quest_color(level: Any, player_level: Any, trivial: Any = 6) -> str:
    try:
        d = int(level) - int(player_level)
    except (TypeError, ValueError):
        return "?"
    if d >= 5:
        return "rouge"
    if d >= 3:
        return "orange"
    if d >= -2:
        return "jaune"
    if -d > int(trivial or 6):
        return "grise"
    return "verte"


def quest_line(q: Dict[str, Any], player_level: Any, trivial: Any) -> str:
    state = " ✔ à rendre" if q.get("complete") else (" ✘ échouée" if q.get("failed") else "")
    tag = f" [{q['tag']}]" if q.get("tag") else ""
    objs = []
    for o in as_list(q.get("objectives")):
        txt = clean_text(o.get("text"))
        if o.get("need") and o.get("have") is not None and not txt:
            txt = f"{o.get('have')}/{o.get('need')}"
        if txt and not o.get("done"):
            objs.append(txt)
    pos = q.get("position") or {}
    loc = f" · `/way {pos.get('x')} {pos.get('y')}`" if pos.get("x") is not None else ""
    line = (f"- **{q.get('title')}** (niv. {q.get('level')}, {quest_color(q.get('level'), player_level, trivial)})"
            f"{tag}{state}{loc}")
    if objs and not q.get("complete"):
        line += " — " + " ; ".join(objs)
    return line


def render_quests(db: Dict[str, Any], zone: Optional[str] = None, only_open: bool = False) -> List[str]:
    qs = g(db, "quests", default={})
    lst = as_list(qs.get("list"))
    plevel = g(db, "progression", "level") or g(db, "identity", "level")
    trivial = qs.get("trivialRange", 6)
    if zone:
        z = norm_key(zone)
        lst = [q for q in lst if z in norm_key(q.get("category")) or z in norm_key(q.get("title"))]
    if only_open:
        lst = [q for q in lst if not q.get("complete")]
    lines = [f"Journal : {qs.get('count', len(as_list(qs.get('list'))))}/{qs.get('max', '?')} quêtes"
             + (" — **journal plein**, impossible d'en prendre d'autres" if qs.get("count") and qs.get("count") == qs.get("max") else "")
             + f" · {g(db, 'questsCompleted', 'count', default='?')} quêtes terminées au total"]
    done = [q for q in lst if q.get("complete")]
    if done and not only_open:
        lines.append(f"À rendre ({len(done)}) : " + ", ".join(q.get("title") for q in done))
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for q in lst:
        groups.setdefault(q.get("category") or "Autres", []).append(q)
    for cat, qlist in groups.items():
        lines.append(f"\n**{cat}**")
        for q in sorted(qlist, key=lambda x: (x.get("level") or 0)):
            lines.append(quest_line(q, plevel, trivial))
    if zone and not lst:
        lines.append(f"Aucune quête du journal ne correspond à « {zone} ».")
    return lines


def render_reputations(db: Dict[str, Any]) -> List[str]:
    r = g(db, "reputations", default={})
    lst = as_list(r.get("list"))
    if not lst:
        return ["- Réputations : jamais capturées"]
    lines = ["| Faction | Groupe | Palier | Progression |", "|---|---|---|---|"]
    for f in sorted(lst, key=lambda x: (-(x.get("reaction") or 0), -(x.get("value") or 0))):
        lines.append(f"| {f.get('name')} | {f.get('category', '')} | {f.get('standing', '?')} | "
                     f"{f.get('progress', '')} |")
    for mj in as_list(r.get("major")):
        lines.append(f"- {mj.get('name')} : rang {mj.get('renownLevel')} "
                     f"({mj.get('renownXp')}/{mj.get('renownXpMax')})")
    return lines


def render_spells(db: Dict[str, Any], line_filter: Optional[str] = None) -> List[str]:
    sp = g(db, "spells", default={})
    lines = []
    for ln in as_list(sp.get("lines")):
        if line_filter and norm_key(line_filter) not in norm_key(ln.get("name")):
            continue
        items = []
        for s in as_list(ln.get("spells")):
            if s.get("offSpec"):
                continue
            sub = s.get("subName")
            items.append(f"{s.get('name')}" + (f" ({sub})" if sub and sub not in ("Passif",) else "")
                         + (" [passif]" if s.get("passive") else ""))
        lines.append(f"**{ln.get('name')}** ({len(items)}) : " + ", ".join(items))
    return lines or ["- Sorts : jamais capturés"]


def render_inventory(db: Dict[str, Any], include_bank: bool = True) -> List[str]:
    lines = render_bags_summary(db)
    for title, dom in (("Sacs", "bags"), ("Banque", "bank")):
        if dom == "bank" and not include_bank:
            continue
        data = g(db, dom, default={})
        if not data:
            if dom == "bank":
                lines.append("\nBanque : jamais capturée (ouvre ta banque en jeu, puis Ctrl+Maj+S (ou /sync)).")
            continue
        extra = f" (capturée {age(data.get('capturedAt'))})" if dom == "bank" and data.get("capturedAt") else ""
        lines.append(f"\n**{title}**{extra}")
        conts = data.get("containers") or {}
        for cid in sorted(conts, key=lambda c: int(c) if str(c).lstrip("-").isdigit() else 99):
            c = conts[cid]
            items = as_list(c.get("items"))
            agg: Dict[str, int] = {}
            for it in items:
                agg[it.get("name") or f"objet {it.get('itemId')}"] = agg.get(it.get("name") or f"objet {it.get('itemId')}", 0) + (it.get("count") or 1)
            content = ", ".join(f"{n}" + (f" ×{k}" if k > 1 else "") for n, k in agg.items()) or "vide"
            lines.append(f"- {c.get('name') or 'Conteneur ' + str(cid)} ({c.get('free', '?')}/{c.get('slots', '?')} libres) : {content}")
    return lines


# ----------------------------------------------------------------------------
# Profil complet (section auto de profil.md)
# ----------------------------------------------------------------------------

def render_profile_auto(db: Dict[str, Any], source: Dict[str, Any]) -> str:
    cap = captured_at(db)
    parts = [
        f"> Généré automatiquement depuis l'addon ForeverScribe · capture du {local_time(cap)} "
        f"(heure de l'ordinateur) · compte {source.get('account', '?')}.",
        "> Ne modifie pas cette section : elle est réécrite à chaque synchro. Tes notes vont en bas.",
        "", "## Identité", *render_identity(db),
        "", "## Progression", *render_progression(db),
        "", "## Position", *render_position(db),
        "", "## Combat", *render_combat(db),
        "", "## Équipement", *render_equipment_table(db),
        "", "## Talents", *render_talents(db),
        "", "## Métiers", *render_professions(db),
        "", "## Familier", *render_pet(db),
        "", "## Sacs et argent", *render_bags_summary(db),
        "", "## Quêtes", *render_quests(db),
        "", "## Réputations", *render_reputations(db),
    ]
    probs = problems(db)
    if probs:
        parts += ["", "## Données non lues par l'addon", *[f"- {p}" for p in probs]]
    return "\n".join(parts).strip() + "\n"
