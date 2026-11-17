"""Mise en forme des données ForeverScribe en texte compact (français ou anglais).

Utilisé à la fois par le serveur MCP (réponses des outils) et par la synchro
(sections automatiques de profil.md). La langue de sortie vient de i18n (``T``, ``L``) ;
les noms venus du jeu (objets, quêtes, zones) restent dans la langue du client.
"""

from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from i18n import LABELS, L, T, get_lang, labels
from luasv import as_list

# ----------------------------------------------------------------------------
# Libellés
# ----------------------------------------------------------------------------

SLOT_ORDER: List[str] = [
    "HeadSlot", "NeckSlot", "ShoulderSlot", "BackSlot", "ChestSlot", "ShirtSlot", "TabardSlot", "WristSlot",
    "HandsSlot", "WaistSlot", "LegsSlot", "FeetSlot", "Finger0Slot", "Finger1Slot", "Trinket0Slot",
    "Trinket1Slot", "MainHandSlot", "SecondaryHandSlot", "RangedSlot",
]
# compatibilité : libellés français fixes (la sortie passe par slot_label)
SLOT_FR: Dict[str, str] = {
    "HeadSlot": "Tête", "NeckSlot": "Cou", "ShoulderSlot": "Épaules", "BackSlot": "Dos", "ChestSlot": "Torse",
    "ShirtSlot": "Chemise", "TabardSlot": "Tabard", "WristSlot": "Poignets", "HandsSlot": "Mains",
    "WaistSlot": "Taille", "LegsSlot": "Jambes", "FeetSlot": "Pieds", "Finger0Slot": "Doigt 1",
    "Finger1Slot": "Doigt 2", "Trinket0Slot": "Bijou 1", "Trinket1Slot": "Bijou 2",
    "MainHandSlot": "Main droite", "SecondaryHandSlot": "Main gauche", "RangedSlot": "Distance",
}
SLOTS: List[Tuple[str, str]] = [(s, SLOT_FR[s]) for s in SLOT_ORDER]


def slot_label(slot: str) -> str:
    """HeadSlot -> 'Tête' / 'Head' selon la langue de sortie."""
    return L("slot", slot, slot)


def slots_localized() -> List[Tuple[str, str]]:
    return [(s, slot_label(s)) for s in SLOT_ORDER]


# Synonymes acceptés pour désigner un emplacement (français et anglais, clés normalisées par norm_key)
SLOT_ALIASES = {
    "tete": "HeadSlot", "casque": "HeadSlot", "heaume": "HeadSlot", "head": "HeadSlot", "helm": "HeadSlot",
    "helmet": "HeadSlot",
    "cou": "NeckSlot", "collier": "NeckSlot", "amulette": "NeckSlot", "neck": "NeckSlot", "necklace": "NeckSlot",
    "amulet": "NeckSlot",
    "epaules": "ShoulderSlot", "epaulieres": "ShoulderSlot", "shoulder": "ShoulderSlot",
    "shoulders": "ShoulderSlot",
    "dos": "BackSlot", "cape": "BackSlot", "back": "BackSlot", "cloak": "BackSlot",
    "torse": "ChestSlot", "plastron": "ChestSlot", "tunique": "ChestSlot", "robe": "ChestSlot",
    "chest": "ChestSlot", "tunic": "ChestSlot",
    "chemise": "ShirtSlot", "shirt": "ShirtSlot", "tabard": "TabardSlot",
    "poignets": "WristSlot", "brassards": "WristSlot", "wrist": "WristSlot", "wrists": "WristSlot",
    "bracers": "WristSlot",
    "mains": "HandsSlot", "gants": "HandsSlot", "hands": "HandsSlot", "hand": "HandsSlot", "gloves": "HandsSlot",
    "taille": "WaistSlot", "ceinture": "WaistSlot", "waist": "WaistSlot", "belt": "WaistSlot",
    "jambes": "LegsSlot", "pantalon": "LegsSlot", "jambieres": "LegsSlot", "legs": "LegsSlot",
    "pants": "LegsSlot", "leggings": "LegsSlot",
    "pieds": "FeetSlot", "bottes": "FeetSlot", "chaussures": "FeetSlot", "feet": "FeetSlot", "boots": "FeetSlot",
    "doigt": "Finger0Slot", "doigt1": "Finger0Slot", "doigt 1": "Finger0Slot", "anneau": "Finger0Slot",
    "bague": "Finger0Slot", "doigt2": "Finger1Slot", "doigt 2": "Finger1Slot",
    "finger": "Finger0Slot", "finger 1": "Finger0Slot", "finger1": "Finger0Slot", "ring": "Finger0Slot",
    "ring 1": "Finger0Slot", "finger 2": "Finger1Slot", "finger2": "Finger1Slot", "ring 2": "Finger1Slot",
    "bijou": "Trinket0Slot", "bijou1": "Trinket0Slot", "bijou 1": "Trinket0Slot",
    "bijou2": "Trinket1Slot", "bijou 2": "Trinket1Slot", "trinket": "Trinket0Slot",
    "trinket 1": "Trinket0Slot", "trinket1": "Trinket0Slot", "trinket 2": "Trinket1Slot", "trinket2": "Trinket1Slot",
    "main droite": "MainHandSlot", "arme": "MainHandSlot", "mainhand": "MainHandSlot", "main hand": "MainHandSlot",
    "arme de melee": "MainHandSlot", "melee": "MainHandSlot", "weapon": "MainHandSlot",
    "melee weapon": "MainHandSlot",
    "main gauche": "SecondaryHandSlot", "offhand": "SecondaryHandSlot", "off hand": "SecondaryHandSlot",
    "bouclier": "SecondaryHandSlot", "shield": "SecondaryHandSlot",
    "distance": "RangedSlot", "arme a distance": "RangedSlot", "ranged": "RangedSlot",
    "ranged weapon": "RangedSlot",
    "arc": "RangedSlot", "fusil": "RangedSlot", "arbalete": "RangedSlot", "baguette": "RangedSlot",
    "bow": "RangedSlot", "gun": "RangedSlot", "crossbow": "RangedSlot", "wand": "RangedSlot",
    "thrown": "RangedSlot",
}

# Clés internes des stats (indépendantes de la langue). Les libellés : i18n LABELS["stat"].
RESIST_KEYS = {1: "HOLY_RESISTANCE", 2: "FIRE_RESISTANCE", 3: "NATURE_RESISTANCE", 4: "FROST_RESISTANCE",
               5: "SHADOW_RESISTANCE", 6: "ARCANE_RESISTANCE"}
STAT_ORDER = ["AGILITY", "STRENGTH", "STAMINA", "INTELLECT", "SPIRIT", "ATTACK_POWER", "RANGED_ATTACK_POWER",
              "CRIT_RATING", "HIT_RATING"]

# compatibilité (anciens noms) : vues françaises
STAT_FR = dict(LABELS["fr"]["stat"])
QUALITY_FR = dict(LABELS["fr"]["quality"])


# ----------------------------------------------------------------------------
# Outils de formatage (selon la langue de sortie)
# ----------------------------------------------------------------------------

def num(value: Any, decimals: int = 0) -> str:
    """12345.6 -> '12 345,6' (fr) ou '12,345.6' (en)."""
    if value is None:
        return "?"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    s = f"{v:,.{decimals}f}"
    if get_lang() == "en":
        if decimals and "." in s:
            s = s.rstrip("0").rstrip(".")
        return s
    s = s.replace(",", " ").replace(".", ",")
    if decimals and "," in s:
        s = s.rstrip("0").rstrip(",")
    return s


fr_num = num  # ancien nom, gardé pour compatibilité


def pct(part: Any, total: Any, decimals: int = 0) -> str:
    try:
        return num(100.0 * float(part) / float(total), decimals) + ("%" if get_lang() == "en" else " %")
    except (TypeError, ValueError, ZeroDivisionError):
        return "?"


def sep() -> str:
    """Séparateur « libellé : valeur » : ' : ' en français, ': ' en anglais."""
    return ": " if get_lang() == "en" else " : "


def semi() -> str:
    return "; " if get_lang() == "en" else " ; "


def pct_sign() -> str:
    return "%" if get_lang() == "en" else " %"


def duration(seconds: Any) -> str:
    """173365 -> '48 h 09 min' (fr) ou '48 h 09 min' / '2 d 0 h' (en)."""
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
    return T("{d} j {h} h", d=d, h=h)


def age(epoch: Any, now: Optional[float] = None) -> str:
    """Âge d'une capture : 'il y a 3 min' / '3 min ago'."""
    try:
        delta = (now or time.time()) - float(epoch)
    except (TypeError, ValueError):
        return T("date inconnue")
    if delta < 0:
        delta = 0
    if delta < 90:
        return T("il y a moins de 2 min")
    if delta < 3600:
        return T("il y a {m} min", m=int(delta // 60))
    if delta < 86400:
        h = int(delta // 3600)
        m = int((delta % 3600) // 60)
        return T("il y a {h} h {m:02d}", h=h, m=m) if m else T("il y a {h} h", h=h)
    days = int(delta // 86400)
    return T("il y a {n} jours", n=days) if days > 1 else T("il y a 1 jour")


def local_time(epoch: Any, fmt: Optional[str] = None) -> str:
    if fmt is None:
        fmt = "%Y-%m-%d %H:%M" if get_lang() == "en" else "%d/%m/%Y %H:%M"
    try:
        return datetime.fromtimestamp(float(epoch)).strftime(fmt)
    except (TypeError, ValueError, OSError):
        return "?"


def money(copper: Any) -> str:
    try:
        c = int(copper)
    except (TypeError, ValueError):
        return "?"
    g_, rest = divmod(c, 10000)
    s, c = divmod(rest, 100)
    units = ("g", "s", "c") if get_lang() == "en" else ("po", "pa", "pc")
    parts = []
    if g_:
        parts.append(f"{g_} {units[0]}")
    if s or g_:
        parts.append(f"{s} {units[1]}")
    parts.append(f"{c} {units[2]}")
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
    """Minuscules sans accents ni ponctuation, pour comparer des noms (toutes langues latines)."""
    import unicodedata

    s = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def stat_key(key: str) -> Optional[str]:
    """ITEM_MOD_AGILITY_SHORT -> 'AGILITY' ; RESISTANCE0_NAME -> 'ARMOR' ; RESISTANCE2_NAME -> 'FIRE_RESISTANCE'."""
    m = re.match(r"RESISTANCE(\d)_NAME", key)
    if m:
        n = int(m.group(1))
        return "ARMOR" if n == 0 else RESIST_KEYS.get(n, f"RESISTANCE{n}")
    k = re.sub(r"^ITEM_MOD_", "", key)
    return re.sub(r"_SHORT$|_NAME$", "", k)


def stat_name(key: str) -> str:
    """Clé interne -> libellé court dans la langue de sortie ('AGILITY' -> 'Agi')."""
    return L("stat", key) or key.replace("_", " ").capitalize()


def stat_label(key: str) -> Optional[str]:
    """ITEM_MOD_AGILITY_SHORT -> 'Agi' ; RESISTANCE0_NAME -> 'Armure' / 'Armor'."""
    k = stat_key(key)
    return stat_name(k) if k else None


def item_stats(item: Dict[str, Any]) -> Dict[str, float]:
    """Stats d'un objet par clé interne (AGILITY, ARMOR…), sans doublons de résistance."""
    out: Dict[str, float] = {}
    raw = item.get("stats") or {}
    if not isinstance(raw, dict):
        return out
    for key, val in raw.items():
        k = stat_key(str(key))
        if not k or not isinstance(val, (int, float)):
            continue
        if k in out and k.endswith("_RESISTANCE"):
            continue  # ITEM_MOD_FIRE_RESISTANCE et RESISTANCE2_NAME décrivent la même chose
        out[k] = out.get(k, 0) + val
    return out


def stat_sort_key(k: str) -> Tuple[int, str]:
    return (STAT_ORDER.index(k) if k in STAT_ORDER else 50, k)


def stats_text(stats: Dict[str, float], with_armor: bool = False) -> str:
    parts = []
    for k in sorted(stats, key=stat_sort_key):
        if k == "ARMOR" and not with_armor:
            continue
        v = stats[k]
        parts.append(f"{'+' if v > 0 else ''}{num(v, 1)} {stat_name(k)}")
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


def game_locale(db: Optional[Dict[str, Any]]) -> Optional[str]:
    """Langue du client au moment de la capture (frFR, enUS…)."""
    return g(db, "meta", "locale") if isinstance(db, dict) else None


def domain_age(db: Dict[str, Any], domain: str, now: Optional[float] = None) -> str:
    ts = g(db, "meta", "domainsUpdatedAt", domain)
    return age(ts, now) if ts else T("jamais capturé")


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
    zone = g(db, "position", "zone") or g(db, "position", "mapName") or T("zone inconnue")
    cap = captured_at(db)
    text = f"{ident.get('name', '?')} · {ident.get('race', '?')} {ident.get('class', '?')} {level} · {zone}"
    text += T(" · capturé {age}", age=age(cap, now)) if cap else T(" · jamais capturé")
    if cap and (now or time.time()) - cap > 3600:
        text += T(" (Ctrl+Maj+S en jeu pour actualiser)")
    return text


def problems(db: Dict[str, Any]) -> List[str]:
    meta = g(db, "meta", default={})
    out = []
    for dom, err in (meta.get("errors") or {}).items():
        out.append(T("{dom} : erreur ({msg})", dom=dom, msg=clean_text(g(err, 'message', default=err))))
    for dom, lst in (meta.get("missing") or {}).items():
        lst = as_list(lst)
        if lst:
            out.append(T("{dom} : fonctions absentes ({fns})", dom=dom, fns=", ".join(map(str, lst[:5]))))
    for dom, lst in (meta.get("callErrors") or {}).items():
        lst = as_list(lst)
        if lst:
            out.append(T("{dom} : {n} appel(s) en erreur", dom=dom, n=len(lst)))
    return out


# ----------------------------------------------------------------------------
# Rendus par domaine
# ----------------------------------------------------------------------------

def render_identity(db: Dict[str, Any]) -> List[str]:
    ident = g(db, "identity", default={})
    prog = g(db, "progression", default={})
    tal = g(db, "talents", default={})
    lines = [
        T("- **{label}** · {race} {cls} niveau {level} · {faction} · {region} · ruleset {ruleset}",
          label=label(db), race=ident.get('race', '?'), cls=ident.get('class', '?'),
          level=prog.get('level', ident.get('level', '?')), faction=ident.get('faction', '?'),
          region=ident.get('region', '?'), ruleset=ident.get('ruleset', '?'))
        + (" · Hardcore" if ident.get("hardcore") else ""),
    ]
    guild = ident.get("guild")
    lines.append(T("- Guilde : {name} ({rank})", name=guild.get('name'), rank=guild.get('rank', '?'))
                 if isinstance(guild, dict) else T("- Guilde : aucune"))
    if tal:
        lines.append(T("- Spé : {spec} ({role}) · {spent} points de talent dépensés, {free} libre(s)",
                       spec=tal.get('specName', '?'), role=L("role", tal.get('role'), tal.get('role', '?')),
                       spent=tal.get('spent', '?'), free=tal.get('unspent', '?')))
    return lines


def render_progression(db: Dict[str, Any]) -> List[str]:
    p = g(db, "progression", default={})
    if not p:
        return [T("- Progression : jamais capturée")]
    lines = []
    if p.get("level") == p.get("maxLevel"):
        lines.append(T("- Niveau maximum ({level})", level=p.get('level')))
    else:
        rested = p.get("xpRested") or 0
        rs = g(p, "restState", "name")
        lines.append(
            T("- XP : {xp} / {max} ({pct}) · reste {left}", xp=num(p.get('xp')), max=num(p.get('xpMax')),
              pct=pct(p.get('xp'), p.get('xpMax'), 1), left=num((p.get('xpMax') or 0) - (p.get('xp') or 0)))
            + (T(" · repos {n}", n=num(rested)) if rested else "")
            + (f" · {rs}" if rs else "")
            + (T(" · au repos") if p.get("isResting") else ""))
    tp = p.get("timePlayed") or {}
    if tp:
        lines.append(T("- Temps de jeu : {total} ({level} à ce niveau)", total=duration(tp.get('total')),
                       level=duration(tp.get('level'))))
    return lines


def way(pos: Dict[str, Any]) -> str:
    if not isinstance(pos, dict) or pos.get("x") is None:
        return ""
    return f"{num(pos.get('x'), 1)} / {num(pos.get('y'), 1)}"


def render_position(db: Dict[str, Any]) -> List[str]:
    pos = g(db, "position", default={})
    if not pos:
        return [T("- Position : jamais capturée")]
    where = pos.get("zone") or pos.get("mapName") or "?"
    if pos.get("subZone"):
        where += f" — {pos['subZone']}"
    coords = way(pos)
    line = f"- {where}" + (f" ({coords} · `/way {pos.get('x')} {pos.get('y')}`)" if coords else "")
    if g(pos, "instance", "inInstance"):
        line += T(" · en instance : {name} {diff}", name=g(pos, 'instance', 'name'),
                  diff=g(pos, 'instance', 'difficultyName', default=''))
    line += T(" · foyer : {bind}", bind=pos.get('bind', '?'))
    return [line]


def render_combat(db: Dict[str, Any]) -> List[str]:
    st = g(db, "stats", default={})
    if not st:
        return [T("- Stats : jamais capturées")]
    prim = st.get("primary") or {}

    def ps(name: str) -> str:
        return num(g(prim, name, "effective"))

    r, m = st.get("ranged") or {}, st.get("melee") or {}
    pc = pct_sign()
    lines = [
        T("- Caractéristiques : For {str} · Agi {agi} · End {sta} · Int {int} · Esp {spi}",
          str=ps('strength'), agi=ps('agility'), sta=ps('stamina'), int=ps('intellect'), spi=ps('spirit')),
        T("- PV {hp} · {power} {pmax} · armure {armor} · ilvl moyen {ilvl}", hp=num(st.get('health')),
          power=str(g(st, 'power', 'token', default=T('ressource'))).capitalize(), pmax=num(g(st, 'power', 'max')),
          armor=num(g(st, 'armor', 'effective')), ilvl=num(g(st, 'itemLevel', 'equipped'), 1)),
    ]
    if r.get("attackPower") is not None and r.get("speed"):
        lines.append(T("- Distance : PA {ap} ({base} + {pos}) · {min}–{max} toutes les {speed} s ({dps} DPS hors crit)"
                       " · crit {crit}{pc}", ap=num(r.get('attackPower')), base=num(r.get('attackPowerBase')),
                       pos=num(r.get('attackPowerPos')), min=num(r.get('minDamage')), max=num(r.get('maxDamage')),
                       speed=num(r.get('speed'), 2), dps=num(r.get('dps'), 1), crit=num(r.get('crit'), 1), pc=pc))
    if m.get("attackPower") is not None:
        lines.append(T("- Mêlée : PA {ap} · {min}–{max} toutes les {speed} s ({dps} DPS) · crit {crit}{pc}"
                       " · esquive {dodge}{pc} · parade {parry}{pc}", ap=num(m.get('attackPower')),
                       min=num(m.get('minDamage')), max=num(m.get('maxDamage')), speed=num(m.get('speed'), 2),
                       dps=num(m.get('dps'), 1), crit=num(m.get('crit'), 1), dodge=num(m.get('dodge'), 1),
                       parry=num(m.get('parry'), 1), pc=pc))
    res = st.get("resistances") or {}
    nz = {k: v for k, v in res.items() if v}
    if nz:
        lines.append(T("- Résistances : {list}", list=", ".join(f"{L('resist', k, k)} {v}" for k, v in nz.items())))
    return lines


def render_equipment_table(db: Dict[str, Any], show_tooltip: bool = False) -> List[str]:
    eq = g(db, "equipment", default={})
    slots = eq.get("slots") or {}
    if not slots:
        return [T("- Équipement : jamais capturé")]
    lines = [T("| Emplacement | Objet | ilvl | Stats | Durabilité |"), "|---|---|---|---|---|"]
    low = []
    for slot, lab in slots_localized():
        it = slots.get(slot)
        if not it:
            continue
        st = item_stats(it)
        stxt = stats_text(st)
        if it.get("dps"):
            stxt = f"{num(it['dps'], 1)} DPS" + (", " + stxt if stxt else "")
        d = it.get("durability") or {}
        dtxt = f"{d.get('current')}/{d.get('max')}" if d.get("max") else "—"
        if d.get("max") and d.get("current", 0) / d["max"] < 0.25:
            low.append(lab)
        qid = it.get("quality")
        q = L("quality", qid, "") if isinstance(qid, int) and qid >= 3 else ""
        name = it.get("name") or T("objet {id}", id=it.get('itemId'))
        lines.append(f"| {lab} | {name}{' (' + q + ')' if q else ''} "
                     f"| {it.get('itemLevel', '?')} | {stxt or '—'} | {dtxt} |")
        if show_tooltip and it.get("tooltip"):
            lines.append(f"|  | _{clean_text(' · '.join(map(str, as_list(it['tooltip'])[1:])))}_ |  |  |  |")
    if eq.get("repairCost"):
        lines.append(T("\nRéparation complète : {cost}.", cost=money(eq['repairCost'])))
    if low:
        lines.append(T("Durabilité faible : {slots}.", slots=", ".join(low)))
    return lines


def render_talents(db: Dict[str, Any]) -> List[str]:
    t = g(db, "talents", default={})
    if not t:
        return [T("- Talents : jamais capturés")]
    lines = [T("- Spé : {spec} ({role}) · {spent} points dépensés, {free} libre(s) · {n} spé(s) disponible(s)",
               spec=t.get('specName', '?'), role=L("role", t.get('role'), t.get('role', '?')),
               spent=t.get('spent', '?'), free=t.get('unspent', '?'), n=t.get('numSpecs', 1))]
    nodes = as_list(t.get("nodes"))
    if nodes:
        nodes = sorted(nodes, key=lambda n: (n.get("posY", 0), n.get("posX", 0)))
        lines.append(T("- Talents pris : {list}", list=", ".join(
            f"{n.get('name', n.get('nodeId'))} {n.get('rank', '?')}/{n.get('maxRank', '?')}" for n in nodes)))
    return lines


def render_professions(db: Dict[str, Any], with_recipes: bool = False) -> List[str]:
    pr = g(db, "professions", default={})
    profs = as_list(pr.get("professions"))
    if not profs:
        return [T("- Métiers : aucun capturé")]
    lines = [T("| Métier | Type | Niveau |"), "|---|---|---|"]
    for p in profs:
        lines.append(f"| {p.get('name')} | {L('prof_slot', p.get('slot'), '')} | "
                     f"{p.get('rank')}/{p.get('max')}"
                     + (f" (+{p['modifier']})" if p.get("modifier") else "") + " |")
    recipes = g(db, "recipes", default={})
    if with_recipes:
        if not recipes:
            lines.append(T("\nRecettes : jamais capturées (ouvre la fenêtre du métier en jeu, puis Ctrl+Maj+S (ou /sync))."))
        for prof, info in (recipes or {}).items():
            recs = as_list(info.get("recipes"))
            useful = [r for r in recs if r.get("learned") and r.get("difficulty") in (0, 1)]
            lines.append(T("\n**{prof}** : {n} recettes connues (capturé {age}).", prof=prof, n=len(recs),
                           age=age(info.get('capturedAt'))))
            if useful:
                lines.append(T("Recettes qui font encore monter le métier : {list}", list=", ".join(
                    f"{r.get('name')} ({L('recipe_color', r.get('difficulty'), '?')}"
                    + (T(", {n} faisables", n=r['available']) if r.get("available") else "") + ")"
                    for r in useful[:25])))
    elif recipes:
        lines.append(T("\nRecettes capturées pour : {list}.", list=", ".join(recipes)))
    return lines


# sous-noms des actions de familier qui ne sont pas des techniques (postures, ordres), toutes langues
PET_NON_ABILITY = ("posture", "commande", "stance", "command")
PASSIVE_SUBNAMES = ("passif", "passive")


def render_pet(db: Dict[str, Any]) -> List[str]:
    pet = g(db, "pet", default={})
    if not pet:
        return [T("- Familier : jamais capturé")]
    cur = pet.get("current") if pet.get("active") else None
    lines = []
    shown = cur or pet.get("lastSeen")
    if shown:
        hap = g(shown, "happiness", "level")
        tp = shown.get("trainingPoints") or {}
        status = T("actif") if cur else T("renvoyé (vu {age})", age=age(pet.get('lastSeenAt')))
        lines.append(
            T("- {name} ({family}) niveau {level}, {status}", name=shown.get('name', '?'),
              family=shown.get('family', '?'), level=shown.get('level', '?'), status=status)
            + (T(" · {mood} ({pct}{pc} dégâts)", mood=L("happiness", hap, hap),
                 pct=g(shown, 'happiness', 'damagePct'), pc=pct_sign()) if hap else "")
            + (f" · {clean_text(shown.get('loyalty'))}" if shown.get("loyalty") else ""))
        if shown.get("xpMax"):
            lines.append(T("- XP familier : {xp} / {max} · points de dressage {free} libres sur {total}",
                           xp=num(shown.get('xp')), max=num(shown.get('xpMax')), free=tp.get('available', '?'),
                           total=tp.get('total', '?')))
        if shown.get("food"):
            lines.append(T("- Mange : {list}", list=", ".join(as_list(shown.get('food')))))
        abil = [a for a in as_list(shown.get("abilities"))
                if not any(w in norm_key(a.get("subName")) for w in PET_NON_ABILITY)]
        if abil:
            lines.append(T("- Techniques : {list}", list=", ".join(
                f"{a.get('name')}" + (f" ({a['subName']})" if a.get("subName") else "") for a in abil)))
    else:
        lines.append(T("- Pas de familier actif"))
    stabled = as_list(g(pet, "stable", "stabled"))
    if stabled:
        lines.append(T("- À l'écurie : {list}", list=", ".join(
            f"{s.get('name')} ({s.get('family')} {s.get('level')})" for s in stabled)))
    return lines


def render_bags_summary(db: Dict[str, Any]) -> List[str]:
    b = g(db, "bags", default={})
    # money.text vient du jeu (langue du client) : on le reformate dans la langue de sortie
    cop = g(db, "money", "copper")
    lines = [T("- Argent : {money}", money=money(cop) if cop is not None else (g(db, 'money', 'text') or "?"))]
    if b:
        free, total = b.get("freeSlots"), b.get("totalSlots")
        lines.append(T("- Sacs : {free} place(s) libre(s) sur {total}", free=free, total=total)
                     + (T(" — presque pleins") if isinstance(free, int) and free <= 3 else ""))
        ammo = b.get("ammo") or {}
        if ammo.get("total") is not None:
            detail = ", ".join(f"{k} ×{v}" for k, v in (ammo.get("items") or {}).items())
            lines.append(T("- Munitions : {n}", n=num(ammo.get('total'))) + (f" ({detail})" if detail else ""))
    return lines


def quest_color_key(level: Any, player_level: Any, trivial: Any = 6) -> Optional[str]:
    """Code de difficulté : red, orange, yellow, green, grey (None si inconnu)."""
    try:
        d = int(level) - int(player_level)
    except (TypeError, ValueError):
        return None
    if d >= 5:
        return "red"
    if d >= 3:
        return "orange"
    if d >= -2:
        return "yellow"
    if -d > int(trivial or 6):
        return "grey"
    return "green"


def quest_color(level: Any, player_level: Any, trivial: Any = 6) -> str:
    key = quest_color_key(level, player_level, trivial)
    return L("quest_color", key, "?") if key else "?"


def quest_line(q: Dict[str, Any], player_level: Any, trivial: Any) -> str:
    state = T(" ✔ à rendre") if q.get("complete") else (T(" ✘ échouée") if q.get("failed") else "")
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
    line = T("- **{title}** (niv. {level}, {color})", title=q.get('title'), level=q.get('level'),
             color=quest_color(q.get('level'), player_level, trivial)) + f"{tag}{state}{loc}"
    if objs and not q.get("complete"):
        line += " — " + semi().join(objs)
    return line


def render_quests(db: Dict[str, Any], zone: Optional[str] = None, only_open: bool = False,
                  reward_line: Optional[Any] = None) -> List[str]:
    qs = g(db, "quests", default={})
    lst = as_list(qs.get("list"))
    plevel = g(db, "progression", "level") or g(db, "identity", "level")
    trivial = qs.get("trivialRange", 6)
    if zone:
        z = norm_key(zone)
        lst = [q for q in lst if z in norm_key(q.get("category")) or z in norm_key(q.get("title"))]
    if only_open:
        lst = [q for q in lst if not q.get("complete")]
    full = qs.get("count") and qs.get("count") == qs.get("max")
    lines = [T("Journal : {n}/{max} quêtes", n=qs.get('count', len(as_list(qs.get('list')))), max=qs.get('max', '?'))
             + (T(" — **journal plein**, impossible d'en prendre d'autres") if full else "")
             + T(" · {n} quêtes terminées au total", n=g(db, 'questsCompleted', 'count', default='?'))]
    done = [q for q in lst if q.get("complete")]
    if done and not only_open:
        lines.append(T("À rendre ({n}) : {list}", n=len(done), list=", ".join(q.get("title") for q in done)))
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for q in lst:
        groups.setdefault(q.get("category") or T("Autres"), []).append(q)
    for cat, qlist in groups.items():
        lines.append(f"\n**{cat}**")
        for q in sorted(qlist, key=lambda x: (x.get("level") or 0)):
            lines.append(quest_line(q, plevel, trivial))
            extra = reward_line(q) if reward_line else None
            if extra:
                lines.append(f"  - {extra}")
    if zone and not lst:
        lines.append(T("Aucune quête du journal ne correspond à « {zone} ».", zone=zone))
    return lines


def render_reputations(db: Dict[str, Any]) -> List[str]:
    r = g(db, "reputations", default={})
    lst = as_list(r.get("list"))
    if not lst:
        return [T("- Réputations : jamais capturées")]
    lines = [T("| Faction | Groupe | Palier | Progression |"), "|---|---|---|---|"]
    for f in sorted(lst, key=lambda x: (-(x.get("reaction") or 0), -(x.get("value") or 0))):
        lines.append(f"| {f.get('name')} | {f.get('category', '')} | {f.get('standing', '?')} | "
                     f"{f.get('progress', '')} |")
    for mj in as_list(r.get("major")):
        lines.append(T("- {name} : rang {level} ({xp}/{max})", name=mj.get('name'), level=mj.get('renownLevel'),
                       xp=mj.get('renownXp'), max=mj.get('renownXpMax')))
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
            items.append(f"{s.get('name')}" + (f" ({sub})" if sub and norm_key(sub) not in PASSIVE_SUBNAMES else "")
                         + (T(" [passif]") if s.get("passive") else ""))
        lines.append(f"**{ln.get('name')}** ({len(items)}){sep()}" + ", ".join(items))
    return lines or [T("- Sorts : jamais capturés")]


def render_inventory(db: Dict[str, Any], include_bank: bool = True) -> List[str]:
    lines = render_bags_summary(db)
    for title, dom in ((T("Sacs"), "bags"), (T("Banque"), "bank")):
        if dom == "bank" and not include_bank:
            continue
        data = g(db, dom, default={})
        if not data:
            if dom == "bank":
                lines.append(T("\nBanque : jamais capturée (ouvre ta banque en jeu, puis Ctrl+Maj+S (ou /sync))."))
            continue
        extra = T(" (capturée {age})", age=age(data.get('capturedAt'))) if dom == "bank" and data.get("capturedAt") else ""
        lines.append(f"\n**{title}**{extra}")
        conts = data.get("containers") or {}
        for cid in sorted(conts, key=lambda c: int(c) if str(c).lstrip("-").isdigit() else 99):
            c = conts[cid]
            items = as_list(c.get("items"))
            agg: Dict[str, int] = {}
            for it in items:
                nm = it.get("name") or T("objet {id}", id=it.get('itemId'))
                agg[nm] = agg.get(nm, 0) + (it.get("count") or 1)
            content = ", ".join(f"{n}" + (f" ×{k}" if k > 1 else "") for n, k in agg.items()) or T("vide")
            lines.append(T("- {name} ({free}/{slots} libres) : {content}",
                           name=c.get('name') or T("Conteneur {id}", id=cid), free=c.get('free', '?'),
                           slots=c.get('slots', '?'), content=content))
    return lines


# ----------------------------------------------------------------------------
# Profil complet (section auto de profil.md)
# ----------------------------------------------------------------------------

def render_profile_auto(db: Dict[str, Any], source: Dict[str, Any]) -> str:
    cap = captured_at(db)
    parts = [
        T("> Généré automatiquement depuis l'addon ForeverScribe · capture du {time} (heure de l'ordinateur) · "
          "compte {account}.", time=local_time(cap), account=source.get('account', '?')),
        T("> Ne modifie pas cette section : elle est réécrite à chaque synchro. Tes notes vont en bas."),
        "", T("## Identité"), *render_identity(db),
        "", T("## Progression"), *render_progression(db),
        "", T("## Position"), *render_position(db),
        "", T("## Combat"), *render_combat(db),
        "", T("## Équipement"), *render_equipment_table(db),
        "", T("## Talents"), *render_talents(db),
        "", T("## Métiers"), *render_professions(db),
        "", T("## Familier"), *render_pet(db),
        "", T("## Sacs et argent"), *render_bags_summary(db),
        "", T("## Quêtes"), *render_quests(db),
        "", T("## Réputations"), *render_reputations(db),
    ]
    probs = problems(db)
    if probs:
        parts += ["", T("## Données non lues par l'addon"), *[f"- {p}" for p in probs]]
    return "\n".join(parts).strip() + "\n"
