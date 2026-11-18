"""Paliers, formateurs et parcours de montée d'un métier (outil `professions`).

- Paliers (Apprenti, Compagnon, Expert, Artisan) : seuils de Classic, absents des fichiers du client
  Forever (les sorts de rang existent mais sans compétence ni niveau requis) → toujours marqués
  « [Classic] à vérifier ». Le palier suivant est comparé à la compétence et au niveau du perso.
- Formateurs : PNJ de QuestieDB (`q_npcs`, drapeau formateur 0x10, titre du métier), amis de la
  faction du perso, du plus proche au plus lointain, avec `/way` (`q_spawns`).
- Parcours : de la compétence actuelle à la cible, la recette la moins chère qui donne encore des
  points (orange ou jaune de préférence), couleurs, nombre de fabrications estimé, composants,
  prix marchand (`items.buy_price` + vendeurs `q_items.vendors`) et revente marchand du produit
  (`items.sell_price`). Aucun prix d'hôtel des ventes n'existe dans la base : jamais inventé.
- Rang requis des recettes : recalculé à la lecture avec `gamedata/recipe_rank.py` (même logique
  que la construction de la base), pour que les bases construites avant la correction en profitent.
- Couleurs Classic (jaune, grise, apprise d'office) : table `recipe_colors` de la base, téléchargée chez
  le joueur au build (gamedata/recipe_colors.py). Table absente : couleurs estimées ≈ (prudentes).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import formats as F
import i18n as I
from i18n import T
from i18n_en import EN
from luasv import as_list

_PLUGIN = str(Path(__file__).resolve().parents[1])
if _PLUGIN not in sys.path:
    sys.path.insert(0, _PLUGIN)
from gamedata import recipe_colors as RC  # noqa: E402
from gamedata import recipe_rank as RR  # noqa: E402

# (clé, compétence requise, niveau requis, compétence max) — Classic Era, non vérifié dans Forever
TIERS = [("apprenti", 1, 5, 75), ("compagnon", 50, 10, 150), ("expert", 125, 20, 225), ("artisan", 200, 35, 300)]
TIER_LABEL = {"apprenti": "Apprenti", "compagnon": "Compagnon", "expert": "Expert", "artisan": "Artisan"}

# mots du titre (<…>) des formateurs, normalisés (FR et EN), par métier (ID Classic)
TRAINER_WORDS = {
    165: ("artisans du cuir", "artisan du cuir", "leatherworker", "leatherworking"),
    202: ("ingenieurs", "ingenieur", "engineer", "engineering"),
    164: ("forgerons", "forgeron", "blacksmith", "blacksmithing"),
    197: ("tailleurs", "tailleur", "tailor", "tailoring"),
    171: ("alchimistes", "alchimiste", "alchemist", "alchemy"),
    333: ("enchanteurs", "enchanteur", "enchanter", "enchanting"),
    186: ("mineurs", "mineur", "miner", "mining"),
    182: ("herboristes", "herboriste", "herbalist", "herbalism"),
    393: ("depeceurs", "depeceur", "skinner", "skinning"),
    185: ("cuisiniers", "cuisinier", "cook", "cooking", "chef"),
    129: ("premiers soins", "medecin", "chirurgien", "first aid", "physician", "surgeon", "doctor"),
    356: ("pecheurs", "pecheur", "fisherman", "fishing", "angler"),
}
SPEC_WORDS = ("gnome", "gobelin", "goblin", "gnomish", "tribal", "elementaire", "elemental", "ecailles", "dragonscale",
              "tisse", "weaver", "fabricant", "armorsmith", "weaponsmith", "forgeron d armes", "armes")
TRAINER_FLAG = 16
# recettes de Season of Discovery présentes dans le client (sorts 400000-1228999, origine client) :
# absentes de Classic et non vérifiées dans Forever, exclues du parcours
SOD_SPELLS = (400000, 1229000)
MAX_SEGMENTS = 30
STICKY = 1.35
GREEN_PENALTY = 2.5
# métiers de récolte (ID Classic) : pas de parcours de recettes, règles de montée à la place
GATHERING = (182, 186, 393, 356)
SECONDARY = (185, 129, 356)
# familles d'artisanat (classe 7) où une recette « un seul composant de la même famille » est une conversion
# (cuir léger ← lanières, cuir moyen ← cuir léger, essences, barres transmutées, éléments) : matière brute
CONVERT_SUBCLASSES = (6, 7, 10, 12)


def tier_index_of_max(max_rank: Any) -> int:
    """Palier actuel (0 = rien, 1 = Apprenti … 4 = Artisan) d'après la compétence max capturée."""
    try:
        m = int(max_rank or 0)
    except (TypeError, ValueError):
        return 0
    idx = 0
    for i, t in enumerate(TIERS, 1):
        if m >= t[3]:
            idx = i
    return idx


def tier_label(i: int) -> str:
    return T(TIER_LABEL[TIERS[i - 1][0]]) if 1 <= i <= len(TIERS) else "?"


def tier_status(rank: Optional[int], max_rank: Optional[int], level: Optional[int]) -> Dict[str, Any]:
    """Palier actuel, palier suivant et si ses conditions sont remplies (seuils Classic)."""
    cur = tier_index_of_max(max_rank) if rank is not None else 0
    out: Dict[str, Any] = {"current": cur, "next": None}
    if cur >= len(TIERS):
        return out
    key, need_skill, need_level, new_max = TIERS[cur]
    skill = rank or 0
    out["next"] = {"index": cur + 1, "skill": need_skill, "level": need_level, "max": new_max,
                   "skill_ok": (skill >= need_skill) if cur else True,
                   "level_ok": (level is None) or level >= need_level,
                   "missing": max(0, need_skill - skill) if cur else 0}
    return out


def tier_lines(rank: Optional[int], max_rank: Optional[int], level: Optional[int], learned: bool) -> List[str]:
    st = tier_status(rank if learned else None, max_rank if learned else None, level)
    cur, nxt = st["current"], st["next"]
    lines = [T("**Paliers** [Classic] à vérifier dans Forever (le client ne donne ni compétence ni niveau requis) :")]
    lines.append(T("- Apprenti 1-75 (niv. 5) · Compagnon jusqu'à 150 (compétence 50, niv. 10) · Expert jusqu'à 225 "
                   "(compétence 125, niv. 20) · Artisan jusqu'à 300 (compétence 200, niv. 35)."))
    if learned:
        lines.append(T("- Palier actuel : {tier} ({rank}/{max}).", tier=tier_label(cur), rank=rank, max=max_rank))
    if not nxt:
        lines.append(T("- Palier maximal atteint."))
        return lines
    name = tier_label(nxt["index"])
    if not learned:
        lines.append(T("- Pas encore appris : {tier} chez un formateur (niveau {lvl} requis{ok}).", tier=name,
                       lvl=nxt["level"], ok=T(", OK") if nxt["level_ok"] else T(", pas encore atteint")))
        return lines
    sk = (T("compétence OK ({rank}/{need})", rank=rank, need=nxt["skill"]) if nxt["skill_ok"] else
          T("compétence : pas encore : {rank}/{need} (encore {n} points)", rank=rank, need=nxt["skill"],
            n=nxt["missing"]))
    lv = (T("niveau OK ({lvl}/{need})", lvl=level, need=nxt["level"]) if nxt["level_ok"] else
          T("niveau : pas encore : {lvl}/{need}", lvl=level, need=nxt["level"]))
    lines.append(T("- Palier suivant : {tier} (max {max}) — {skill} ; {level}.", tier=name, max=nxt["max"], skill=sk,
                   level=lv))
    return lines


def tier_verdict(prof_name: str, rank: Optional[int], max_rank: Optional[int], level: Optional[int],
                 gathering: bool = False) -> Optional[str]:
    """Verdict sur la formation : None si rien à signaler (palier max ou pas encore proche)."""
    st = tier_status(rank, max_rank, level)
    nxt = st["next"]
    if not nxt or not st["current"]:
        return None
    name = tier_label(nxt["index"])
    if nxt["skill_ok"] and nxt["level_ok"]:
        return T("{prof} {rank}/{max} : tu peux prendre {tier} chez le formateur (compétence {need} et niveau {lvl} "
                 "requis [Classic])", prof=prof_name, rank=rank, max=max_rank, tier=name, need=nxt["skill"],
                 lvl=nxt["level"])
    if not nxt["skill_ok"] and gathering:
        return T("{prof} {rank}/{max} : pas encore {tier} — il faut {need} de compétence (encore {n} points), "
                 "monte d'abord en récoltant", prof=prof_name, rank=rank, max=max_rank, tier=name,
                 need=nxt["skill"], n=nxt["missing"])
    if not nxt["skill_ok"]:
        return T("{prof} {rank}/{max} : pas encore {tier} — il faut {need} de compétence (encore {n} points), "
                 "monte d'abord avec le parcours ci-dessous", prof=prof_name, rank=rank, max=max_rank, tier=name,
                 need=nxt["skill"], n=nxt["missing"])
    return T("{prof} {rank}/{max} : {tier} demande le niveau {lvl} [Classic]", prof=prof_name, rank=rank,
             max=max_rank, tier=name, lvl=nxt["level"])


# ---------------------------------------------------------------------------
# formateurs

def trainer_tier(subname: str, pid: int) -> Tuple[Optional[int], bool]:
    """(palier max enseigné, formateur de spécialisation) d'après le titre du PNJ ; palier None = non précisé."""
    s = F.norm_key(subname)
    for w in sorted(TRAINER_WORDS.get(pid, ()), key=len, reverse=True):
        s = s.replace(w, " ", 1) if w in s else s
    words = set(s.split())
    spec = any(w in s for w in SPEC_WORDS)
    if words & {"compagnon", "journeyman"}:
        return 2, spec
    if "expert" in words:
        return 3, spec
    if "artisan" in words:
        return 4, spec
    if words & {"apprenti", "apprentie", "apprentice"}:
        return 1, spec
    if (words & {"maitre", "master", "grand", "grande"}) and not s.strip().startswith(("maitre des", "maitresse des")):
        return 4, spec
    return None, spec


def is_trainer_for(subname: Any, pid: int) -> bool:
    s = F.norm_key(subname)
    return bool(s) and any(w in s for w in TRAINER_WORDS.get(pid, ()))


def classic_id(gdb: Any, pid: int) -> int:
    """ID Classic (165…) d'un métier, même si on a l'ID Forever jumeau (2945…)."""
    if pid in TRAINER_WORDS:
        return pid
    rows = gdb.q("SELECT p2.id FROM professions p1 JOIN professions p2 ON p2.name_norm = p1.name_norm "
                 "WHERE p1.id = ? ORDER BY p2.id", (pid,))
    return next((r["id"] for r in rows if r["id"] in TRAINER_WORDS), pid)


def twin_ids(gdb: Any, pid: int) -> List[int]:
    rows = gdb.q("SELECT p2.id FROM professions p1 JOIN professions p2 ON p2.name_norm = p1.name_norm "
                 "WHERE p1.id = ? ORDER BY p2.id", (pid,))
    return sorted({pid, *(r["id"] for r in rows)})


def _has_table(gdb: Any, name: str) -> bool:
    return bool(gdb.q("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)))


def classic_colors(gdb: Any) -> Dict[int, Tuple[int, int, bool]]:
    """{sort: (jaune, grise, apprise d'office)} de la table recipe_colors ({} si absente), lu une fois par base."""
    cached = getattr(gdb, "_recipe_colors", None)
    if cached is None:
        cached = RC.read(gdb.q) if _has_table(gdb, "recipe_colors") else {}
        try:
            gdb._recipe_colors = cached
        except AttributeError:
            pass
    return cached


def _load_rank_items(gdb: Any, ids, items: Dict[int, Any]) -> None:
    """Complète `items` (id -> ligne) avec le niveau et la compétence requise des objets voulus."""
    ids = [i for i in ids if i and i not in items]
    for k in range(0, len(ids), 500):
        chunk = ids[k:k + 500]
        for it in gdb.q(f"SELECT id, name, ilvl, required_skill, required_skill_rank, sell_price, buy_price, "
                        f"class_id, subclass_id "
                        f"FROM items WHERE id IN ({','.join('?' * len(chunk))})", tuple(chunk)):
            items[it["id"]] = it


def recipe_ranks(gdb: Any, pids: List[int], rows: List[Any], items: Dict[int, Any]
                 ) -> Tuple[Dict[Tuple[int, int], Tuple[Optional[int], Optional[str]]], List[Any]]:
    """Rang requis recalculé (gamedata/recipe_rank.py) des recettes `rows` des métiers `pids`.

    items : objets déjà chargés (fabriqués et composants). Renvoie ({(spell_id, profession_id): (rang,
    source)}, patrons/schémas/plans de ces métiers) — source « client », « objet » ou « estimation »."""
    ph = ",".join("?" * len(pids))
    # patrons, schémas, plans… (classe 9) qui exigent ce métier : rang et vendeurs
    pats = gdb.q(f"SELECT id, name, required_skill, required_skill_rank, buy_price FROM items "
                 f"WHERE class_id = 9 AND required_skill IN ({ph})", tuple(pids))
    pidx = RR.pattern_index([(p["name"], p["required_skill"], p["required_skill_rank"]) for p in pats],
                            F.norm_key)
    inputs = [{"key": (r["spell_id"], r["profession_id"]), "profession_id": r["profession_id"], "name": r["name"],
               "min_rank": r["min_rank"], "item_id": r["item_id"],
               "reagents": json.loads(r["reagents_json"] or "[]"),
               "classic": r["spell_id"] < RR.CLASSIC_SPELL_MAX} for r in rows]
    ranks = RR.assign_ranks(
        inputs, lambda i: dict(items[i]) if i in items else None,
        lambda p, name: next((pidx[(t, F.norm_key(name))] for t in pids if (t, F.norm_key(name)) in pidx), None),
        lambda p, skill: skill in pids, classic_colors(gdb))
    return ranks, pats


def profession_ranks(gdb: Any, pid: int) -> Dict[int, Tuple[Optional[int], Optional[str]]]:
    """{spell_id: (rang, source)} des recettes du métier `pid`, rang recalculé à la lecture
    (y compris sur une base construite avant la correction de recipe_rank.py)."""
    pids = twin_ids(gdb, pid)
    rows = gdb.q(f"SELECT spell_id, profession_id, name, min_rank, item_id, reagents_json FROM recipes "
                 f"WHERE profession_id IN ({','.join('?' * len(pids))})", tuple(pids))
    items: Dict[int, Any] = {}
    ids = set()
    for r in rows:
        if r["item_id"]:
            ids.add(r["item_id"])
        for g in json.loads(r["reagents_json"] or "[]"):
            ids.add(g["item_id"])
    _load_rank_items(gdb, ids, items)
    ranks, _ = recipe_ranks(gdb, pids, rows, items)
    return {sid: v for (sid, p), v in ranks.items() if p == pid}


class Place:
    """Où est le perso : zone (AreaTable) et continent, pour classer formateurs et vendeurs."""

    def __init__(self, tools: Any, gdb: Any, db: Optional[Dict[str, Any]]):
        self.zones: List[int] = []
        self.continent: Optional[int] = None
        self.faction = {"Alliance": "A", "Horde": "H"}.get(str(F.g(db, "identity", "faction") or "")) if db else None
        zone = (F.g(db, "position", "realZone") or F.g(db, "position", "zone")) if db else None
        if zone:
            try:
                self.zones = tools._zone_ids(gdb, zone)
            except Exception:
                self.zones = [r["id"] for r in gdb.q("SELECT id FROM zones WHERE name_norm = ?", (F.norm_key(zone),))]
        if self.zones:
            row = gdb.q("SELECT continent_id FROM zones WHERE id = ?", (self.zones[0],))
            self.continent = row[0]["continent_id"] if row else None
        # lieu du foyer (pierre de foyer) : aussi « tout près »
        bind = F.g(db, "position", "bind") if db else None
        self.bind_zones = [r["id"] for r in gdb.q("SELECT id FROM zones WHERE name_norm = ?", (F.norm_key(bind),))] \
            if bind else []
        self._cont: Dict[int, Optional[int]] = {}

    def continent_of(self, gdb: Any, zid: Any) -> Optional[int]:
        if zid not in self._cont:
            row = gdb.q("SELECT continent_id FROM zones WHERE id = ?", (zid,)) if zid else []
            self._cont[zid] = row[0]["continent_id"] if row else None
        return self._cont[zid]

    def distance(self, gdb: Any, zid: Any) -> int:
        """0 même zone ou zone du foyer, 1 même continent, 2 ailleurs ou inconnu."""
        if zid in self.zones or zid in self.bind_zones:
            return 0
        c = self.continent_of(gdb, zid)
        return 1 if c is not None and c == self.continent else 2

    def own_faction_only(self, fr: Any) -> bool:
        """PNJ réservé à la faction du perso (territoire de sa faction, souvent plus proche de ses villes)."""
        return bool(self.faction) and str(fr or "").upper() == self.faction

    def friendly(self, fr: Any) -> bool:
        return not self.faction or self.faction in str(fr or "").upper()


def find_trainers(tools: Any, gdb: Any, pid: int, place: Place, min_tier: int = 1,
                  limit: int = 4) -> List[Dict[str, Any]]:
    """Formateurs du métier, amis de la faction, qui enseignent au moins `min_tier` (ou palier non précisé)."""
    if not _has_table(gdb, "q_npcs"):
        return []
    cid = classic_id(gdb, pid)
    rows = gdb.q("SELECT * FROM q_npcs WHERE (npc_flags & ?) != 0 AND subname IS NOT NULL AND subname != '' "
                 "AND spawn_count > 0", (TRAINER_FLAG,))
    found = []
    for n in rows:
        if not is_trainer_for(n["subname"], cid) or not place.friendly(n["friendly"]):
            continue
        tier, spec = trainer_tier(n["subname"], cid)
        if tier is not None and tier < min_tier:
            continue
        found.append({"row": n, "tier": tier, "spec": spec, "dist": place.distance(gdb, n["zone_id"])})
    # palier connu et suffisant d'abord, puis le plus proche ; spécialisations en dernier
    found.sort(key=lambda t: (t["spec"], t["tier"] is None, t["dist"], not place.own_faction_only(t["row"]["friendly"]),
                              -(t["row"]["spawn_count"] or 0),
                              t["row"]["id"]))
    return found[:limit]


def trainer_lines(tools: Any, gdb: Any, pid: int, place: Place, min_tier: int) -> List[str]:
    trainers = find_trainers(tools, gdb, pid, place, min_tier)
    if not trainers:
        return [T("- Formateurs : aucun trouvé dans QuestieDB pour ta faction (cherche « formateur » auprès d'un garde).")]
    out = [T("**Formateurs** ({tier} ou plus, ta faction, du plus proche au plus loin) [QuestieDB] :",
             tier=tier_label(min_tier))]
    for t in trainers:
        n = t["row"]
        loc = tools.where(gdb, "npc", n["id"], place.zones, max_zones=1)
        taught = tier_label(t["tier"]) if t["tier"] else T("palier max non précisé")
        out.append(T("- {name} <{sub}> — enseigne jusqu'à {tier} — {where}", name=tools.label(n), sub=n["subname"],
                     tier=taught, where=loc[0] if loc else T("position inconnue")))
    return out


# ---------------------------------------------------------------------------
# recettes : rang, couleurs, coût

def est_colors(rank: int) -> Tuple[int, int, int]:
    """Couleurs (jaune, verte, grise) estimées quand ni le client Forever ni Classic ne les donnent.

    Estimation prudente (quartile bas des écarts des recettes Classic) : jaune +20, verte +30, grise +40.
    Le parcours n'utilise une recette aux couleurs estimées que tant qu'elle est orange ou jaune."""
    return rank + 20, rank + 30, rank + 40


def crafts_per_point(skill: int, rec: Dict[str, Any]) -> float:
    """Fabrications attendues pour gagner un point à `skill` = 1 / espérance de points d'une fabrication.

    Formule Classic : orange 1 point ; de jaune à grise, chance = (gris − compétence) / (gris − jaune).
    Jamais au-delà de la grise ; couleurs estimées (≈) : jamais au-delà de la verte (prudence)."""
    o, y, gr = rec["rank"], rec["yellow"], rec["grey"]
    stop = rec["green"] if rec.get("colors_src") == "est" else gr
    if skill < o or skill >= stop or skill >= gr:
        return math.inf
    ups = max(1, rec.get("skill_ups") or 1)
    if skill < y:
        return 1.0 / ups
    chance = (gr - skill) / max(1, gr - y)
    return 1.0 / max(chance, 0.05) / ups


def color_at(skill: int, rec: Dict[str, Any]) -> int:
    """0 orange, 1 jaune, 2 verte, 3 grise (indisponible si skill < rang : -1)."""
    if skill < rec["rank"]:
        return -1
    if skill < rec["yellow"]:
        return 0
    if skill < rec["green"]:
        return 1
    if skill < rec["grey"]:
        return 2
    return 3


class Catalog:
    """Recettes d'un métier avec rang recalculé, patrons, sources marchandes et coût des composants."""

    def __init__(self, tools: Any, gdb: Any, pid: int, place: Place):
        self.tools, self.gdb, self.place = tools, gdb, place
        self.pids = twin_ids(gdb, pid)
        ph = ",".join("?" * len(self.pids))
        rows = gdb.q(f"SELECT r.*, i.name AS item_name, i.sell_price AS item_sell, i.origin AS iorigin "
                     f"FROM recipes r LEFT JOIN items i ON i.id = r.item_id WHERE r.profession_id IN ({ph})",
                     tuple(self.pids))
        self.items: Dict[int, Any] = {}
        ids = set()
        for r in rows:
            if r["item_id"]:
                ids.add(r["item_id"])
            for g in json.loads(r["reagents_json"] or "[]"):
                ids.add(g["item_id"])
        self._load_items(ids)
        ranks, pats = recipe_ranks(gdb, self.pids, rows, self.items)
        self.patterns: Dict[str, List[Any]] = {}
        for p in pats:
            tgt = RR.pattern_target(p["name"])
            if tgt:
                self.patterns.setdefault(F.norm_key(tgt), []).append(p)
        self.recipes: List[Dict[str, Any]] = []
        for r in rows:
            rank, src = ranks.get((r["spell_id"], r["profession_id"]), (None, None))
            if not rank or not r["name"] or not r["item_id"]:
                continue
            cc = RR.classic_of({"spell_id": r["spell_id"]}, classic_colors(gdb))
            if r["yellow"] and r["grey"]:
                csrc, (y, g, gr) = "client", (r["yellow"], r["green"] or (r["yellow"] + r["grey"]) // 2, r["grey"])
            elif cc and cc[0] and cc[1]:
                csrc, (y, g, gr) = "classic", (cc[0], (cc[0] + cc[1]) // 2, cc[1])
            else:
                csrc, (y, g, gr) = "est", est_colors(rank)
            if y < rank:  # rang lu au-dessus de la jaune Classic : la recette reste orange jusqu'à son rang
                y, g, gr = rank, max(g, rank + (gr - y) // 2), max(gr, rank + (gr - y))
            rec = {"spell_id": r["spell_id"], "name": r["name"], "rank": rank, "source": src, "yellow": y,
                   "green": g, "grey": gr, "colors_src": csrc, "colors_client": csrc != "est",
                   "skill_ups": r["skill_ups"] or 1,
                   "item_id": r["item_id"], "item_name": r["item_name"] or r["name"], "item_count": r["item_count"] or 1,
                   "item_sell": r["item_sell"] or 0, "reagents": json.loads(r["reagents_json"] or "[]"),
                   "origin": r["origin"], "iorigin": r["iorigin"],
                   "patterns": self.patterns.get(F.norm_key(r["name"]), [])}
            self.recipes.append(rec)
        self.by_product: Dict[int, List[Dict[str, Any]]] = {}
        for rec in self.recipes:
            self.by_product.setdefault(rec["item_id"], []).append(rec)
        self._vendor: Dict[int, Optional[Dict[str, Any]]] = {}
        self._cost: Dict[int, Tuple[float, bool]] = {}
        self._sub: Dict[int, Optional[Dict[str, Any]]] = {}
        self._smelt: Dict[int, bool] = {}

    def _load_items(self, ids) -> None:
        _load_rank_items(self.gdb, ids, self.items)

    def item_name(self, iid: int, fallback: Any = None) -> str:
        it = self.items.get(iid)
        return (it["name"] if it else None) or fallback or str(iid)

    # -- sources -------------------------------------------------------------------------------
    def vendor(self, iid: int) -> Optional[Dict[str, Any]]:
        """Vendeur ami le plus proche (QuestieDB) et prix d'achat marchand, ou None."""
        if iid in self._vendor:
            return self._vendor[iid]
        self._vendor[iid] = None
        it = self.items.get(iid)
        if it is None:
            self._load_items([iid])
            it = self.items.get(iid)
        price = it["buy_price"] if it is not None else None
        if not price or not _has_table(self.gdb, "q_items"):
            return None
        row = self.gdb.q("SELECT * FROM q_items WHERE id = ?", (int(iid),))
        vids = [int(v) for v in (json.loads(row[0]["vendors"]) if row and row[0]["vendors"] else [])]
        if not vids:
            return None
        other = any(row[0][k] not in (None, "", "[]") for k in ("npc_drops", "object_drops", "item_drops"))
        best = None
        for k in range(0, len(vids), 400):
            chunk = vids[k:k + 400]
            for n in self.gdb.q(f"SELECT * FROM q_npcs WHERE id IN ({','.join('?' * len(chunk))}) AND spawn_count > 0",
                                tuple(chunk)):
                if not self.place.friendly(n["friendly"]):
                    continue
                key = (self.place.distance(self.gdb, n["zone_id"]), -(n["spawn_count"] or 0), n["id"])
                if best is None or key < best[0]:
                    best = (key, n)
        if best is None:
            return None
        # Marchand sur un autre continent (Foire de Sombrelune…) pour un objet qui se récolte ou se ramasse :
        # pas une source pratique, seulement mentionnée.
        far = best[0][0] >= 2 and other
        self._vendor[iid] = {"price": price, "npc": best[1], "count": len(vids), "far": far}
        return self._vendor[iid]

    def buyable(self, iid: int) -> Optional[Dict[str, Any]]:
        v = self.vendor(iid)
        return v if v and not v["far"] else None

    def unit_cost(self, iid: int, depth: int = 0) -> Tuple[float, bool]:
        """(coût d'un exemplaire, connu en prix marchand ?). Sans marchand : composant fabriqué par ce
        métier (coût de sa recette), sinon valeur interne = prix de revente marchand × 4 — sert seulement
        à classer les recettes, jamais affichée comme un prix."""
        if iid in self._cost:
            return self._cost[iid]
        v = self.buyable(iid)
        if v:
            self._cost[iid] = (float(v["price"]), True)
            return self._cost[iid]
        if depth < 2 and iid in self.by_product:
            best = None
            for rec in self.by_product[iid]:
                if rec["rank"] > 300:
                    continue
                c = sum(g["count"] * self.unit_cost(g["item_id"], depth + 1)[0] for g in rec["reagents"])
                c /= max(1, rec["item_count"])
                best = c if best is None else min(best, c)
            if best is not None:
                self._cost[iid] = (best, False)
                return self._cost[iid]
        it = self.items.get(iid)
        sell = (it["sell_price"] if it is not None else 0) or 0
        self._cost[iid] = (max(20.0, 4.0 * sell), False)
        return self._cost[iid]

    def recipe_cost(self, rec: Dict[str, Any]) -> float:
        if "cost" not in rec:
            rec["cost"] = sum(g["count"] * self.unit_cost(g["item_id"])[0] for g in rec["reagents"])
        return rec["cost"]

    def acquisition(self, rec: Dict[str, Any]) -> Tuple[str, float]:
        """(« formateur » | « patron-marchand » | « patron » | « inconnue », pénalité de classement)."""
        if rec["patterns"]:
            live = [p for p in rec["patterns"] if not RR.is_obsolete(p["name"])]
            if not live:
                return "perime", math.inf
            if any(self.buyable(p["id"]) for p in live):
                return "patron-marchand", 1.3
            return "patron", 4.0
        if rec["spell_id"] >= 1000000:
            return "inconnue", 2.5
        return "formateur", 1.0

    def sub_recipe(self, iid: int) -> Optional[Dict[str, Any]]:
        """Recette du même métier qui fabrique ce composant (rang le plus bas), sauf simple conversion
        (cuir léger ← lanières, essences, transmutations : on les récolte ou on les achète)."""
        if iid in self._sub:
            return self._sub[iid]
        best = None
        it = self.items.get(iid)
        for rec in self.by_product.get(iid, []):
            if not self.usable(rec) or self.acquisition(rec)[1] == math.inf:
                continue
            if any(g["item_id"] == iid for g in rec["reagents"]):
                continue
            src = self.items.get(rec["reagents"][0]["item_id"]) if len(rec["reagents"]) == 1 else None
            if it is not None and src is not None and it["class_id"] == 7 and it["subclass_id"] in CONVERT_SUBCLASSES \
                    and src["class_id"] == 7 and src["subclass_id"] == it["subclass_id"]:
                continue  # conversion d'un seul composant de la même famille (cuirs, essences…) : matière brute
            if best is None or (rec["rank"], rec["spell_id"]) < (best["rank"], best["spell_id"]):
                best = rec
        self._sub[iid] = best
        return best

    def smelted(self, iid: int) -> bool:
        """Barre obtenue par la fonte (métier Minage) ?"""
        if iid not in self._smelt:
            self._smelt[iid] = bool(self.gdb.q(
                "SELECT 1 FROM recipes r JOIN professions p ON p.id = r.profession_id "
                "WHERE r.item_id = ? AND p.id IN (186, 2946) LIMIT 1", (int(iid),)))
        return self._smelt[iid]

    def usable(self, rec: Dict[str, Any]) -> bool:
        lo, hi = SOD_SPELLS
        if lo <= rec["spell_id"] < hi and rec["origin"] == "client" and rec["iorigin"] in (None, "client"):
            return False
        if RR.is_obsolete(rec["name"]) or not rec["reagents"]:
            return False
        if any(g["item_id"] not in self.items for g in rec["reagents"]):
            return False  # composant inconnu de la base : recette inexploitable
        return rec["rank"] <= 300


# ---------------------------------------------------------------------------
# parcours

def plan_path(cat: Catalog, start: int, target: int, captured: Optional[Dict[str, int]] = None
              ) -> List[Dict[str, Any]]:
    """Segments [{from, to, rec, crafts}] : à chaque point, la recette au meilleur coût par point
    (coût × fabrications attendues pour un point), jamais grise, orange/jaune de préférence."""
    recs = [r for r in cat.recipes if cat.usable(r)]
    for r in recs:
        r["acq"], r["penalty"] = cat.acquisition(r)
    recs = [r for r in recs if r["penalty"] != math.inf]
    segs: List[Dict[str, Any]] = []
    skill = max(1, start)

    def score_of(r: Dict[str, Any]) -> float:
        cpp = crafts_per_point(skill, r)
        if cpp == math.inf:
            return math.inf
        if captured and captured.get(F.norm_key(r["name"])) == 3 and skill == start:
            return math.inf  # grise d'après les couleurs capturées en jeu
        # orange/jaune d'abord : une verte ne sert que faute de mieux ; rang estimé légèrement pénalisé
        col = color_at(skill, r)
        return (cat.recipe_cost(r) + 5.0) * cpp * r["penalty"] * (GREEN_PENALTY if col == 2 else 1.0) \
            * (1.1 if r["source"] == "estimation" else 1.0)

    while skill < target:
        best, best_score = None, math.inf
        for r in recs:
            score = score_of(r)
            if score < best_score:
                best, best_score = r, score
        # garder la recette en cours tant qu'elle reste presque aussi bonne (moins d'allers-retours)
        prev = segs[-1]["rec"] if segs else None
        if best is not None and prev is not None and prev is not best and score_of(prev) <= best_score * STICKY:
            best = prev
        if best is None:
            segs.append({"from": skill, "to": target, "rec": None, "crafts": 0})
            break
        cpp = crafts_per_point(skill, best)
        if segs and segs[-1]["rec"] is best:
            segs[-1]["to"] = skill + 1
            segs[-1]["crafts"] += cpp
        else:
            segs.append({"from": skill, "to": skill + 1, "rec": best, "crafts": cpp})
        skill += 1
    return segs


def _merge_small(segs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fusionne les tronçons d'un seul point dans le précédent quand c'est la même recette plus loin."""
    out: List[Dict[str, Any]] = []
    for s in segs:
        if out and s["rec"] is not None and out[-1]["rec"] is s["rec"]:
            out[-1]["to"], out[-1]["crafts"] = s["to"], out[-1]["crafts"] + s["crafts"]
        else:
            out.append(dict(s))
    return out


def _rank_text(rec: Dict[str, Any]) -> str:
    mark = {"client": "", "objet": "", "estimation": "≈"}.get(rec["source"], "≈")
    return mark + str(rec["rank"])


def _colors_text(rec: Dict[str, Any]) -> str:
    est = "" if rec["colors_client"] else "≈"
    return T("orange {o} · jaune {y} · verte {g} · grise {gr}", o=rec["rank"], y=f"{est}{rec['yellow']}",
             g=f"{est}{rec['green']}", gr=f"{est}{rec['grey']}")


def plan_lines(tools: Any, cat: Catalog, start: int, target: int, counts: Dict[int, int],
               boundaries: Optional[List[Tuple[int, int]]] = None, captured: Optional[Dict[str, int]] = None,
               level: Optional[int] = None) -> List[str]:
    segs = _merge_small(plan_path(cat, start, target, captured))
    lines = [T("**Parcours de {start} à {target}** (recette la moins chère qui donne encore des points ; "
               "nombre de fabrications estimé) :", start=start, target=target)]
    steps: List[Tuple[Dict[str, Any], int]] = []
    shown = 0
    for s in segs:
        if s["rec"] is None:
            lines.append(T("- {a} → {b} : aucune recette connue de la base ne donne de points ici.", a=s["from"],
                           b=s["to"]))
            nxt = sorted((r for r in cat.recipes if cat.usable(r) and r["rank"] > s["from"]),
                         key=lambda r: (r["rank"], r["name"]))[:6]
            if nxt:
                lines.append("  " + T("Prochaines recettes (rang requis) : {list}.", list=", ".join(
                    f"{r['name']} ({_rank_text(r)})" for r in nxt)))
            continue
        if shown >= MAX_SEGMENTS:
            lines.append(T("- … suite tronquée : relance avec `cible` plus bas ou depuis {a}.", a=s["from"]))
            break
        shown += 1
        rec = s["rec"]
        crafts = max(1, math.ceil(s["crafts"] - 1e-9))
        c0, c1 = color_at(s["from"], rec), color_at(max(s["from"], s["to"] - 1), rec)
        col = I.L("recipe_color", c0, "?") + ("" if c1 == c0 else " → " + I.L("recipe_color", c1, "?"))
        train = ""
        for at, idx in boundaries or []:
            if s["from"] <= at < s["to"]:
                _k, need, lvl, _mx = TIERS[idx - 1]
                train += T(" — à {n} : formateur, palier {tier}", n=at, tier=tier_label(idx))
                if level is not None and level < lvl:
                    train += T(" (niveau {lvl} requis [Classic], tu es {cur})", lvl=lvl, cur=level)
        acq = {"formateur": T("formateur [Classic]"), "patron-marchand": T("patron vendu par un marchand"),
               "patron": T("patron (butin ou réputation, pas de marchand connu)"),
               "inconnue": T("source inconnue (recette Forever)")}.get(rec["acq"], "?")
        lines.append(T("{n}. **{a} → {b}** · {name} (rang {rank}, {acq}) · ~{crafts} fabrications · {col}{train}",
                       n=shown, a=s["from"], b=s["to"], name=rec["name"], rank=_rank_text(rec), acq=acq, crafts=crafts,
                       col=col, train=train))
        lines.append("   " + T("Couleurs : {colors}", colors=_colors_text(rec)))
        parts = []
        for g in rec["reagents"]:
            iid, qty = g["item_id"], g["count"] * crafts
            name = cat.item_name(iid, g.get("name"))
            have = T(" (tu en as {n})", n=counts[iid]) if counts.get(iid) else ""
            v = cat.buyable(iid)
            if v:
                parts.append(T("{qty} {name}{have} — marchand {price} pièce", qty=qty, name=name, have=have,
                               price=F.money(v["price"])))
            elif iid in cat.by_product:
                parts.append(T("{qty} {name}{have} — à fabriquer (même métier) ou à récolter", qty=qty, name=name,
                               have=have))
            else:
                parts.append(T("{qty} {name}{have} — à récolter ou acheter à l'HV", qty=qty, name=name, have=have))
        lines.append("   " + T("Composants : {list}", list="; ".join(parts)))
        steps.append((rec, crafts))
        if rec["acq"] == "patron-marchand":
            p = next(p for p in rec["patterns"] if not RR.is_obsolete(p["name"]) and cat.buyable(p["id"]))
            v = cat.buyable(p["id"])
            loc = tools.where(cat.gdb, "npc", v["npc"]["id"], cat.place.zones, max_zones=1)
            lines.append("   " + T("À apprendre avec : {name}, {price} chez {npc}{where}", name=p["name"], price=F.money(v["price"]),
                                    npc=tools.label(v["npc"]), where=(", " + loc[0]) if loc else ""))
        if rec["item_sell"]:
            lines.append("   " + T("Revente marchand du produit : {price} pièce ({name}).",
                                    price=F.money(rec["item_sell"]), name=rec["item_name"]))
    if steps:
        lines += totals_lines(tools, cat, steps, counts)
    lines.append("_" + T("Rang requis : sans « ≈ », lu dans les fichiers du client (recette, patron ou objet "
                         "fabriqué, ou recette apprise d'office au rang 1) ; « ≈ » = estimation (niveau de l'objet "
                         "fabriqué ou de ses composants, ramené sous la jaune de Classic). Couleurs sans « ≈ » : "
                         "valeurs [Classic] de la recette (non modifiées dans Forever, sauf exception) ; « ≈ » : "
                         "estimation prudente (jaune +20, verte +30, grise +40) et recette utilisée seulement tant "
                         "qu'elle est orange ou jaune. Jamais de recette grise. Fabrications = espérance de points : "
                         "orange 1 point, puis chance (gris − compétence) / (gris − jaune). Aucun prix d'hôtel des "
                         "ventes n'existe dans la base : seuls les prix marchands sont donnés.") + "_")
    return lines


def expand_steps(cat: Catalog, steps: List[Tuple[Dict[str, Any], int]]
                 ) -> Tuple[Dict[int, int], Dict[int, int], Dict[int, Dict[str, Any]]]:
    """Déroule les composants du parcours jusqu'aux matières brutes.

    Les composants fabriqués par le même métier (poudres, boulons, rouleaux d'étoffe…) sont remplacés
    par leurs propres composants, récursivement ; les produits des étapes précédentes servent d'abord
    (la poudre fabriquée de 1 à 30 alimente les bombes suivantes). Renvoie (à fabriquer {objet: qté},
    matières brutes {objet: qté}, recette retenue pour chaque intermédiaire)."""
    stock: Dict[int, int] = {}
    craft: Dict[int, int] = {}
    raw: Dict[int, int] = {}
    via: Dict[int, Dict[str, Any]] = {}

    def need(iid: int, qty: int, depth: int) -> None:
        take = min(stock.get(iid, 0), qty)
        if take:
            stock[iid] -= take
            qty -= take
        if qty <= 0:
            return
        sub = cat.sub_recipe(iid) if depth < 4 else None
        if sub is None:
            raw[iid] = raw.get(iid, 0) + qty
            return
        per = max(1, sub["item_count"])
        n = math.ceil(qty / per)
        craft[iid] = craft.get(iid, 0) + n * per
        via[iid] = sub
        stock[iid] = stock.get(iid, 0) + n * per - qty
        for g in sub["reagents"]:
            need(g["item_id"], g["count"] * n, depth + 1)

    for rec, crafts in steps:
        for g in rec["reagents"]:
            need(g["item_id"], g["count"] * crafts, 0)
        stock[rec["item_id"]] = stock.get(rec["item_id"], 0) + crafts * max(1, rec["item_count"])
    return craft, raw, via


def totals_lines(tools: Any, cat: Catalog, steps: List[Tuple[Dict[str, Any], int]],
                 counts: Dict[int, int]) -> List[str]:
    """Deux listes : intermédiaires à fabriquer en route, matières brutes à acheter ou récolter."""
    craft, raw, via = expand_steps(cat, steps)

    def have(i: int) -> str:
        return T(" (tu en as {n})", n=counts[i]) if counts.get(i) else ""

    out: List[str] = []
    if craft:
        out.append(T("\n**À fabriquer en route** (même métier, en plus des étapes ; les produits des étapes "
                     "précédentes sont déjà déduits) : {list}.", list=", ".join(
                         T("{qty} {name}{have} ({recipe})", qty=q, name=cat.item_name(i), have=have(i),
                           recipe=via[i]["name"]) if F.norm_key(via[i]["name"]) != F.norm_key(cat.item_name(i))
                         else T("{qty} {name}{have}", qty=q, name=cat.item_name(i), have=have(i))
                         for i, q in sorted(craft.items(), key=lambda x: -x[1]))))
    vendor_total = 0
    parts, vend = [], []
    for i, q in sorted(raw.items(), key=lambda x: -x[1]):
        v = cat.buyable(i)
        if v:
            vendor_total += v["price"] * q
            src = T("marchand {price} pièce", price=F.money(v["price"]))
            if len(vend) < 6:
                loc = tools.where(cat.gdb, "npc", v["npc"]["id"], cat.place.zones, max_zones=1)
                vend.append(T("{item} : {npc}{where}", item=cat.item_name(i), npc=tools.label(v["npc"]),
                              where=(" — " + loc[0]) if loc else ""))
        elif cat.smelted(i):
            src = T("à acheter à l'HV, ou minerai à fondre si Minage")
        else:
            src = T("à récolter ou acheter à l'HV")
        parts.append(T("{qty} {name}{have} — {src}", qty=q, name=cat.item_name(i), have=have(i), src=src))
    out.append(T("**À acheter ou récolter** (matières brutes, total du parcours) :"))
    out += ["- " + p for p in parts]
    if vendor_total:
        out.append(T("Coût des composants achetables chez un marchand : {price} (prix marchand du client).",
                     price=F.money(vendor_total)))
    if vend:
        out.append(T("Marchands les plus proches (ta faction) [QuestieDB] : {list}.", list=" ; ".join(vend)))
    return out


def target_for(rank: int, max_rank: Optional[int], level: Optional[int], learned: bool) -> int:
    """Cible par défaut : fin du palier actuel ; au palier plein, fin du palier suivant que le niveau permet."""
    allowed = 0
    for _k, _s, need_level, mx in TIERS:
        if level is None or level >= need_level:
            allowed = mx
    allowed = allowed or 75
    if not learned:
        return min(allowed, 150)
    if max_rank and rank < max_rank:
        return int(max_rank)
    return min(allowed, (max_rank or 75) + 75)


def captured_colors(captured: Optional[Dict[str, Any]]) -> Dict[str, int]:
    out = {}
    for r in as_list((captured or {}).get("recipes")):
        if r.get("name") and r.get("difficulty") is not None:
            out[F.norm_key(r["name"])] = r["difficulty"]
    return out


# ---------------------------------------------------------------------------
# métiers de récolte : règles de montée (pas de parcours de recettes)

# (objet récolté, compétence requise) — Classic Era, à vérifier dans Forever
HERB_NODES = [(2447, 1), (765, 1), (2449, 15), (785, 50), (2450, 70), (3820, 85), (2453, 100), (3355, 115),
              (3369, 120), (3356, 125), (3357, 150), (3818, 160), (3821, 170), (3358, 185), (3819, 195),
              (4625, 205), (8831, 210), (8836, 220), (8838, 230), (8839, 235), (8845, 245), (8846, 250),
              (13464, 260), (13463, 270), (13465, 280), (13466, 285), (13467, 290), (13468, 300)]
ORE_NODES = [(2770, 1), (2771, 65), (2775, 75), (2772, 125), (2776, 155), (3858, 175), (7911, 230), (11370, 230),
             (10620, 245)]
# bêtes dépeçables (nom anglais de QuestieDB, mots entiers)
BEAST_WORDS = {"boar", "wolf", "worg", "bear", "grizzly", "spider", "tarantula", "widow", "recluse", "raptor", "lion",
               "lioness", "tiger", "panther", "jaguar", "lynx", "puma", "prowler", "stalker", "crocolisk", "gorilla",
               "silverback", "bat", "hyena", "vulture", "buzzard", "hawk", "condor", "turtle", "tortoise", "kodo",
               "plainstrider", "strider", "scorpid", "basilisk", "threshadon", "hippogryph", "serpent", "yeti",
               "devilsaur", "stegodon", "pterrordax", "ravasaur", "stag", "coyote", "jackal", "zhevra", "nightsaber",
               "frostsaber", "saber", "mountainlion", "lizard", "thunderhawk", "screecher", "shardtooth", "chimaera",
               "wyvern", "cougar", "mastiff", "dimetrodon"}


def skinning_max_level(skill: int) -> int:
    """Niveau max d'une bête dépeçable (Classic) : (niveau − 10) × 10 jusqu'au niveau 20, puis niveau × 5."""
    return max(10, skill // 10 + 10) if skill < 100 else skill // 5


def _zones_by_spawns(gdb: Any, place: Place, kind: str, ids: List[int], limit: int = 3
                     ) -> List[Tuple[int, int]]:
    """[(zone, apparitions)] des PNJ/objets `ids`, du plus proche (zone du perso, continent) au plus loin."""
    if not ids or not _has_table(gdb, "q_spawns"):
        return []
    count: Dict[int, int] = {}
    for k in range(0, len(ids), 400):
        chunk = ids[k:k + 400]
        for r in gdb.q(f"SELECT zone_id, count(*) AS n FROM q_spawns WHERE kind = ? AND id IN "
                       f"({','.join('?' * len(chunk))}) GROUP BY zone_id", (kind, *chunk)):
            if r["zone_id"]:
                count[r["zone_id"]] = count.get(r["zone_id"], 0) + r["n"]
    order = sorted(count, key=lambda z: (place.distance(gdb, z), -count[z]))
    return [(z, count[z]) for z in order[:limit]]


def _node_zones(tools: Any, gdb: Any, place: Place, iid: int) -> str:
    if not _has_table(gdb, "q_items"):
        return ""
    row = gdb.q("SELECT object_drops FROM q_items WHERE id = ?", (iid,))
    objs = [int(o) for o in (json.loads(row[0]["object_drops"]) if row and row[0]["object_drops"] else [])]
    zones = _zones_by_spawns(gdb, place, "object", objs, 3)
    return ", ".join(tools.zone_name(gdb, z) for z, _n in zones)


def _item_names(gdb: Any, ids: List[int]) -> Dict[int, str]:
    rows = gdb.q(f"SELECT id, name FROM items WHERE id IN ({','.join('?' * len(ids))})", tuple(ids))
    return {r["id"]: r["name"] for r in rows}


def gathering_lines(tools: Any, gdb: Any, cid: int, pid: int, prof_name: str, skill: int, level: Optional[int],
                    place: Place) -> List[str]:
    """Règles de montée d'un métier de récolte (Classic, à vérifier), prochains paliers, zones proches."""
    lines = ["", T("**{prof}** : métier de récolte, il monte en récoltant — pas de parcours de recettes. "
                   "Règles [Classic] à vérifier dans Forever :", prof=prof_name)]
    if cid in (182, 186):
        nodes = HERB_NODES if cid == 182 else ORE_NODES
        names = _item_names(gdb, [i for i, _r in nodes])
        lines.append(T("- Points : un nœud donne 1 point à coup sûr de son rang requis à +25 environ, souvent "
                       "jusqu'à +50, rarement jusqu'à +100, plus rien ensuite (orange/jaune/vert/gris)."))
        lines.append(T("- Rang requis par nœud : {list}.", list=" · ".join(
            f"{names.get(i, i)} {r}" for i, r in nodes)))
        good = [(i, r) for i, r in nodes if r <= skill < r + 50]
        if good:
            lines.append(T("- À {skill}, nœuds qui rapportent bien (orange/jaune) :", skill=skill))
            for i, r in sorted(good, key=lambda x: -x[1])[:4]:
                z = _node_zones(tools, gdb, place, i)
                lines.append(f"  - {names.get(i, i)} ({r})" + (T(" — zones proches [QuestieDB] : {z}", z=z) if z
                                                              else ""))
        nxt = next(((i, r) for i, r in nodes if r > skill), None)
        if nxt:
            z = _node_zones(tools, gdb, place, nxt[0])
            lines.append(T("- Prochain nœud : {name} à {rank} (encore {n} points)", name=names.get(nxt[0], nxt[0]),
                           rank=nxt[1], n=nxt[1] - skill) + (T(" — zones proches [QuestieDB] : {z}", z=z) if z
                                                               else "") + ".")
        if cid == 186:
            lines.append(T("- La fonte (barres) donne aussi des points tant qu'elle n'est pas grise."))
    elif cid == 393:
        mx = skinning_max_level(skill)
        lo = max(1, mx - 5)
        lines.append(T("- Règle : compétence requise = (niveau − 10) × 10 jusqu'au niveau 20, puis niveau × 5. "
                       "À {skill}, tu dépèces les bêtes jusqu'au niveau {max} ; les plus proches de ce niveau "
                       "({lo}-{max}) rapportent le plus, les bêtes bien plus basses deviennent grises.",
                       skill=skill, max=mx, lo=lo))
        lines.append(T("- On dépèce les bêtes (et quelques dragonkins) après les avoir tuées ; chaque dépeçage "
                       "orange ou jaune donne 1 point, presque toujours."))
        if level is not None and mx > level + 2:
            lines.append(T("- Ton niveau ({lvl}) limite plus que ta compétence : vise des bêtes de ton niveau.",
                           lvl=level))
            mx, lo = level + 1, max(1, level - 4)
        lines += skinning_zones(tools, gdb, place, lo, mx)
    elif cid == 356:
        lines.append(T("- Chaque poisson pêché donne des points : 1 par prise au début, puis de moins en moins "
                       "(plusieurs prises par point au-delà de ~150). Sous la compétence d'une zone, les poissons "
                       "s'échappent souvent : monte dans les zones de bas niveau d'abord."))
        lines.append(T("- La Pêche est un métier secondaire : elle ne compte pas dans les deux métiers principaux."))
    return lines


def skinning_zones(tools: Any, gdb: Any, place: Place, lo: int, hi: int) -> List[str]:
    """Zones proches avec des bêtes non élites de niveau lo..hi (QuestieDB : nom anglais, niveau, zone)."""
    if not _has_table(gdb, "q_npcs"):
        return [T("- (QuestieDB absente : pas de zones proposées.)")]
    rows = gdb.q("SELECT * FROM q_npcs WHERE max_level >= ? AND min_level <= ? AND (rank IS NULL OR rank = 0) "
                 "AND (subname IS NULL OR subname = '') AND spawn_count > 0 AND COALESCE(friendly, '') IN ('', 'AH')",
                 (lo, hi))
    beasts = [n for n in rows if set(F.norm_key(n["name"]).split()) & BEAST_WORDS]
    if not beasts:
        return [T("- Aucune bête de niveau {lo}-{hi} trouvée dans QuestieDB.", lo=lo, hi=hi)]
    by_zone: Dict[int, List[Any]] = {}
    ids = [n["id"] for n in beasts]
    spawn_zone: Dict[int, Dict[int, int]] = {}
    for k in range(0, len(ids), 400):
        chunk = ids[k:k + 400]
        for r in gdb.q(f"SELECT id, zone_id, count(*) AS n FROM q_spawns WHERE kind = 'npc' AND id IN "
                       f"({','.join('?' * len(chunk))}) GROUP BY id, zone_id", tuple(chunk)):
            spawn_zone.setdefault(r["zone_id"], {})[r["id"]] = r["n"]
    names = {n["id"]: n for n in beasts}
    for z, mobs in spawn_zone.items():
        if z:
            by_zone[z] = sorted(mobs, key=lambda i: -mobs[i])
    order = sorted(by_zone, key=lambda z: (place.distance(gdb, z), -sum(spawn_zone[z].values())))[:4]
    out = [T("- Zones proches avec des bêtes de niveau {lo}-{hi} [QuestieDB] :", lo=lo, hi=hi)]
    for z in order:
        mobs = by_zone[z][:3]
        out.append("  - " + tools.zone_name(gdb, z) + " : " + ", ".join(
            f"{tools.label(names[i])} ({names[i]['min_level']}-{names[i]['max_level']})" for i in mobs))
    return out


def camp_lines(cat: "Catalog") -> List[str]:
    """Objets de campement (recettes ajoutées par Forever) d'un métier de récolte, cités à part."""
    camp = sorted((r for r in cat.recipes if r["spell_id"] >= RR.CLASSIC_SPELL_MAX), key=lambda r: r["rank"])
    if not camp:
        return []
    return [T("- Autres recettes de ce métier ajoutées par Forever (campement, fontes nouvelles… : objets à "
              "fabriquer, pas un parcours de montée) : {list}.",
              list=", ".join(f"{r['name']} ({_rank_text(r)})" for r in camp))]


def smelting_lines(cat: "Catalog", skill: int) -> List[str]:
    smelt = sorted((r for r in cat.recipes if r["spell_id"] < RR.CLASSIC_SPELL_MAX and r["colors_src"] != "est"),
                   key=lambda r: r["rank"])
    ok = [r for r in smelt if r["rank"] <= skill < r["grey"]]
    if not ok:
        return []
    return [T("- Fonte qui donne encore des points à {skill} : {list}.", skill=skill, list=", ".join(
        f"{r['name']} (rang {_rank_text(r)}, grise {r['grey']})" for r in ok))]


# ---------------------------------------------------------------------------
# traductions anglaises de ce module (fusionnées dans le catalogue au chargement)

PLAN_EN = {
    "Apprenti": "Apprentice", "Compagnon": "Journeyman", "Expert": "Expert", "Artisan": "Artisan",
    "**Paliers** [Classic] à vérifier dans Forever (le client ne donne ni compétence ni niveau requis) :":
        "**Tiers** [Classic], to check in Forever (the client gives neither required skill nor level):",
    "- Apprenti 1-75 (niv. 5) · Compagnon jusqu'à 150 (compétence 50, niv. 10) · Expert jusqu'à 225 "
    "(compétence 125, niv. 20) · Artisan jusqu'à 300 (compétence 200, niv. 35).":
        "- Apprentice 1-75 (lvl 5) · Journeyman up to 150 (skill 50, lvl 10) · Expert up to 225 "
        "(skill 125, lvl 20) · Artisan up to 300 (skill 200, lvl 35).",
    "- Palier actuel : {tier} ({rank}/{max}).": "- Current tier: {tier} ({rank}/{max}).",
    "- Palier maximal atteint.": "- Highest tier reached.",
    "- Pas encore appris : {tier} chez un formateur (niveau {lvl} requis{ok}).":
        "- Not learned yet: {tier} at a trainer (level {lvl} required{ok}).",
    ", OK": ", OK", ", pas encore atteint": ", not reached yet",
    "compétence OK ({rank}/{need})": "skill OK ({rank}/{need})",
    "compétence : pas encore : {rank}/{need} (encore {n} points)": "skill: not yet: {rank}/{need} ({n} more points)",
    "niveau OK ({lvl}/{need})": "level OK ({lvl}/{need})",
    "niveau : pas encore : {lvl}/{need}": "level: not yet: {lvl}/{need}",
    "- Palier suivant : {tier} (max {max}) — {skill} ; {level}.": "- Next tier: {tier} (max {max}) — {skill}; {level}.",
    "{prof} {rank}/{max} : tu peux prendre {tier} chez le formateur (compétence {need} et niveau {lvl} "
    "requis [Classic])":
        "{prof} {rank}/{max}: you can train {tier} at the trainer (skill {need} and level {lvl} required [Classic])",
    "{prof} {rank}/{max} : pas encore {tier} — il faut {need} de compétence (encore {n} points), "
    "monte d'abord avec le parcours ci-dessous":
        "{prof} {rank}/{max}: not {tier} yet — it needs {need} skill ({n} more points), level up first with the "
        "path below",
    "{prof} {rank}/{max} : {tier} demande le niveau {lvl} [Classic]":
        "{prof} {rank}/{max}: {tier} requires level {lvl} [Classic]",
    "- Formateurs : aucun trouvé dans QuestieDB pour ta faction (cherche « formateur » auprès d'un garde).":
        "- Trainers: none found in QuestieDB for your faction (ask a guard for \"trainer\").",
    "**Formateurs** ({tier} ou plus, ta faction, du plus proche au plus loin) [QuestieDB] :":
        "**Trainers** ({tier} or higher, your faction, nearest first) [QuestieDB]:",
    "palier max non précisé": "highest tier not stated",
    "- {name} <{sub}> — enseigne jusqu'à {tier} — {where}": "- {name} <{sub}> — teaches up to {tier} — {where}",
    "position inconnue": "unknown position",
    "**Parcours de {start} à {target}** (recette la moins chère qui donne encore des points ; "
    "nombre de fabrications estimé) :":
        "**Path from {start} to {target}** (cheapest recipe that still gives points; estimated number of crafts):",
    "- {a} → {b} : aucune recette connue de la base ne donne de points ici.":
        "- {a} → {b}: no recipe known to the database gives points here.",
    "Prochaines recettes (rang requis) : {list}.": "Next recipes (required skill): {list}.",
    "- … suite tronquée : relance avec `cible` plus bas ou depuis {a}.":
        "- … truncated: call again with a lower `cible` or from {a}.",
    " — à {n} : formateur, palier {tier}": " — at {n}: trainer, {tier} tier",
    " (niveau {lvl} requis [Classic], tu es {cur})": " (level {lvl} required [Classic], you are {cur})",
    "formateur [Classic]": "trainer [Classic]",
    "patron vendu par un marchand": "pattern sold by a vendor",
    "patron (butin ou réputation, pas de marchand connu)": "pattern (drop or reputation, no known vendor)",
    "source inconnue (recette Forever)": "unknown source (Forever recipe)",
    "{n}. **{a} → {b}** · {name} (rang {rank}, {acq}) · ~{crafts} fabrications · {col}{train}":
        "{n}. **{a} → {b}** · {name} (skill {rank}, {acq}) · ~{crafts} crafts · {col}{train}",
    "Couleurs : {colors}": "Colors: {colors}",
    "orange {o} · jaune {y} · verte {g} · grise {gr}": "orange {o} · yellow {y} · green {g} · grey {gr}",
    " (tu en as {n})": " (you have {n})",
    "{qty} {name}{have} — marchand {price} pièce": "{qty} {name}{have} — vendor {price} each",
    "{qty} {name}{have} — à fabriquer (même métier) ou à récolter":
        "{qty} {name}{have} — to craft (same profession) or gather",
    "{qty} {name}{have} — à récolter ou acheter à l'HV": "{qty} {name}{have} — gather it or buy it at the AH",
    "Composants : {list}": "Reagents: {list}",
    "À apprendre avec : {name}, {price} chez {npc}{where}": "Learned from: {name}, {price} from {npc}{where}",
    "Revente marchand du produit : {price} pièce ({name}).": "Product vendor sell price: {price} each ({name}).",
    "Coût des composants achetables chez un marchand : {price} (prix marchand du client).":
        "Cost of the vendor-bought reagents: {price} (client vendor prices).",
    "{name} n'a pas {prof} : paliers, formateurs et parcours depuis 1 ci-dessous ; pour un autre perso "
    "du compte, characters action:activer":
        "{name} does not have {prof}: tiers, trainers and a path from 1 below; for another character of the "
        "account, characters action:activer",
    "{item} : {npc}{where}": "{item}: {npc}{where}",
    "Marchands les plus proches (ta faction) [QuestieDB] : {list}.": "Nearest vendors (your faction) [QuestieDB]: {list}.",
    "Rang requis : sans « ≈ », lu dans les fichiers du client (recette, patron ou objet "
    "fabriqué, ou recette apprise d'office au rang 1) ; « ≈ » = estimation (niveau de l'objet "
    "fabriqué ou de ses composants, ramené sous la jaune de Classic). Couleurs sans « ≈ » : "
    "valeurs [Classic] de la recette (non modifiées dans Forever, sauf exception) ; « ≈ » : "
    "estimation prudente (jaune +20, verte +30, grise +40) et recette utilisée seulement tant "
    "qu'elle est orange ou jaune. Jamais de recette grise. Fabrications = espérance de points : "
    "orange 1 point, puis chance (gris − compétence) / (gris − jaune). Aucun prix d'hôtel des "
    "ventes n'existe dans la base : seuls les prix marchands sont donnés.":
        "Required skill: without \"≈\", read from the client files (recipe, pattern, crafted item, or recipe "
        "learned with the profession at 1); \"≈\" = estimate (item level of the product or its reagents, kept "
        "below the Classic yellow). Colors without \"≈\": the recipe's [Classic] values (unchanged in Forever "
        "unless stated); \"≈\": cautious estimate (yellow +20, green +30, grey +40) and the recipe is only used "
        "while orange or yellow. Never a grey recipe. Crafts = expected points: orange 1 point, then chance "
        "(grey − skill) / (grey − yellow). There are no auction house prices in the database: only vendor "
        "prices are given.",
    "**{prof}** : métier de récolte, il monte en récoltant — pas de parcours de recettes. "
    "Règles [Classic] à vérifier dans Forever :":
        "**{prof}**: gathering profession, it levels by gathering — no recipe path. [Classic] rules, to check in "
        "Forever:",
    "- Points : un nœud donne 1 point à coup sûr de son rang requis à +25 environ, souvent "
    "jusqu'à +50, rarement jusqu'à +100, plus rien ensuite (orange/jaune/vert/gris).":
        "- Points: a node always gives 1 point from its required skill to about +25, often up to +50, rarely up "
        "to +100, nothing afterwards (orange/yellow/green/grey).",
    "- Rang requis par nœud : {list}.": "- Required skill per node: {list}.",
    "- À {skill}, nœuds qui rapportent bien (orange/jaune) :": "- At {skill}, nodes that give good points "
                                                                "(orange/yellow):",
    " — zones proches [QuestieDB] : {z}": " — nearby zones [QuestieDB]: {z}",
    "- Prochain nœud : {name} à {rank} (encore {n} points)": "- Next node: {name} at {rank} ({n} more points)",
    "- La fonte (barres) donne aussi des points tant qu'elle n'est pas grise.":
        "- Smelting (bars) also gives points while it is not grey.",
    "- Règle : compétence requise = (niveau − 10) × 10 jusqu'au niveau 20, puis niveau × 5. "
    "À {skill}, tu dépèces les bêtes jusqu'au niveau {max} ; les plus proches de ce niveau "
    "({lo}-{max}) rapportent le plus, les bêtes bien plus basses deviennent grises.":
        "- Rule: required skill = (level − 10) × 10 up to level 20, then level × 5. At {skill}, you can skin "
        "beasts up to level {max}; those closest to it ({lo}-{max}) give the most, much lower ones turn grey.",
    "- On dépèce les bêtes (et quelques dragonkins) après les avoir tuées ; chaque dépeçage "
    "orange ou jaune donne 1 point, presque toujours.":
        "- You skin beasts (and a few dragonkin) after killing them; each orange or yellow skinning almost always "
        "gives 1 point.",
    "- Ton niveau ({lvl}) limite plus que ta compétence : vise des bêtes de ton niveau.":
        "- Your level ({lvl}) limits you more than your skill: aim for beasts of your level.",
    "- Chaque poisson pêché donne des points : 1 par prise au début, puis de moins en moins "
    "(plusieurs prises par point au-delà de ~150). Sous la compétence d'une zone, les poissons "
    "s'échappent souvent : monte dans les zones de bas niveau d'abord.":
        "- Every catch gives points: 1 per catch at first, then less and less (several catches per point above "
        "~150). Below a zone's skill, fish often get away: level up in low-level zones first.",
    "- La Pêche est un métier secondaire : elle ne compte pas dans les deux métiers principaux.":
        "- Fishing is a secondary profession: it does not count towards the two primary professions.",
    "- (QuestieDB absente : pas de zones proposées.)": "- (No QuestieDB: no zones suggested.)",
    "- Aucune bête de niveau {lo}-{hi} trouvée dans QuestieDB.": "- No level {lo}-{hi} beast found in QuestieDB.",
    "- Zones proches avec des bêtes de niveau {lo}-{hi} [QuestieDB] :":
        "- Nearby zones with level {lo}-{hi} beasts [QuestieDB]:",
    "- Autres recettes de ce métier ajoutées par Forever (campement, fontes nouvelles… : objets à "
    "fabriquer, pas un parcours de montée) : {list}.":
        "- Other recipes of this profession added by Forever (camp, new smelting…: items to craft, not a "
        "levelling path): {list}.",
    "- Fonte qui donne encore des points à {skill} : {list}.": "- Smelting that still gives points at {skill}: {list}.",
    "{prof} {rank}/{max} : pas encore {tier} — il faut {need} de compétence (encore {n} points), "
    "monte d'abord en récoltant":
        "{prof} {rank}/{max}: not {tier} yet — it needs {need} skill ({n} more points), gather first",
    "{name} n'a pas {prof} : paliers, formateurs et règles de montée ci-dessous ; pour un autre perso "
    "du compte, characters action:activer":
        "{name} does not have {prof}: tiers, trainers and levelling rules below; for another character of the "
        "account, characters action:activer",
    "tu as déjà 2 métiers principaux ({a}, {b}) : il faut en oublier un pour en apprendre un autre":
        "you already have 2 primary professions ({a}, {b}): you must unlearn one to learn another",
    "\n**À fabriquer en route** (même métier, en plus des étapes ; les produits des étapes "
    "précédentes sont déjà déduits) : {list}.":
        "\n**To craft along the way** (same profession, on top of the steps; products of earlier steps are "
        "already deducted): {list}.",
    "{qty} {name}{have} ({recipe})": "{qty} {name}{have} ({recipe})",
    "{qty} {name}{have}": "{qty} {name}{have}",
    "**À acheter ou récolter** (matières brutes, total du parcours) :":
        "**To buy or gather** (raw materials, whole path):",
    "marchand {price} pièce": "vendor {price} each",
    "à acheter à l'HV, ou minerai à fondre si Minage": "buy at the AH, or ore to smelt if you have Mining",
    "à récolter ou acheter à l'HV": "gather it or buy it at the AH",
    "{qty} {name}{have} — {src}": "{qty} {name}{have} — {src}",
}
for _k, _v in PLAN_EN.items():
    EN.setdefault(_k, _v)


# ---------------------------------------------------------------------------
# point d'entrée pour tool_professions

def profession_id(gdb: Any, name: str) -> Optional[int]:
    """ID du métier d'après son nom dans la langue de la base (celui qui a le plus de recettes)."""
    rows = gdb.q("SELECT p.id, (SELECT count(*) FROM recipes r WHERE r.profession_id = p.id) AS n "
                 "FROM professions p WHERE name_norm LIKE ? ORDER BY n DESC, p.id", ("%" + F.norm_key(name) + "%",))
    return rows[0]["id"] if rows else None


def not_learned_verdict(char_name: Optional[str], prof: str, gathering: bool = False) -> str:
    if gathering:
        return T("{name} n'a pas {prof} : paliers, formateurs et règles de montée ci-dessous ; pour un autre perso "
                 "du compte, characters action:activer", name=char_name or T("ce perso"), prof=prof)
    return T("{name} n'a pas {prof} : paliers, formateurs et parcours depuis 1 ci-dessous ; pour un autre perso "
             "du compte, characters action:activer", name=char_name or T("ce perso"), prof=prof)


def is_gathering(gdb: Any, pid: Optional[int]) -> bool:
    return bool(pid) and classic_id(gdb, int(pid)) in GATHERING


def primary_conflict(gdb: Any, wanted_pid: Optional[int], profs: List[Dict[str, Any]]) -> Optional[str]:
    """« tu as déjà 2 métiers principaux (X, Y) : … » quand le métier voulu est principal et que le perso
    en a déjà deux (Cuisine, Secourisme et Pêche sont secondaires ; le Dépeçage est principal)."""
    def cid(p: Any) -> Optional[int]:
        try:
            return classic_id(gdb, int(p)) if gdb is not None else int(p)
        except (TypeError, ValueError):
            return None
    if not wanted_pid or cid(wanted_pid) in SECONDARY:
        return None
    prim = []
    for p in profs:
        slot = str(p.get("slot") or "")
        c = cid(p.get("skillLineId"))
        if (slot.startswith("primary") if slot else (c is not None and c not in SECONDARY)) and c not in SECONDARY:
            prim.append(p.get("name") or "?")
    if len(prim) < 2:
        return None
    return T("tu as déjà 2 métiers principaux ({a}, {b}) : il faut en oublier un pour en apprendre un autre",
             a=prim[0], b=prim[1])


def professions_report(tools: Any, gdb: Any, db: Optional[Dict[str, Any]], pid: int, prof_name: str,
                       prof: Optional[Dict[str, Any]], counts: Dict[int, int], args: Dict[str, Any],
                       captured: Optional[Dict[str, Any]] = None) -> Tuple[List[str], Optional[str]]:
    """(lignes : paliers, formateurs, parcours ; verdict de formation ou None)."""
    level = F.g(db, "identity", "level") or F.g(db, "progression", "level") if db else None
    try:
        level = int(level) if level is not None else None
    except (TypeError, ValueError):
        level = None
    learned = prof is not None
    rank = int(prof.get("rank") or 0) if learned else 0
    max_rank = int(prof.get("max") or 0) if learned else None
    place = Place(tools, gdb, db)
    lines: List[str] = [""]
    lines += tier_lines(rank, max_rank, level, learned)
    st = tier_status(rank if learned else None, max_rank, level)
    want_tier = st["next"]["index"] if st["next"] else len(TIERS)
    lines += trainer_lines(tools, gdb, pid, place, want_tier)
    cid = classic_id(gdb, pid)
    verdict = tier_verdict(prof_name, rank, max_rank, level, cid in GATHERING) if learned else None
    cat = Catalog(tools, gdb, pid, place)
    if cid in GATHERING or not cat.recipes:
        lines += gathering_lines(tools, gdb, cid, pid, prof_name, rank if learned and rank else 1, level, place)
        if cid == 186:
            lines += smelting_lines(cat, rank if learned and rank else 1)
        lines += camp_lines(cat)
        return lines, verdict
    start = rank if learned and rank else 1
    target = args.get("cible")
    try:
        target = int(target) if target is not None else target_for(start, max_rank, level, learned)
    except (TypeError, ValueError):
        target = target_for(start, max_rank, level, learned)
    target = max(start + 1, min(300, target))
    # paliers à prendre en route : (compétence max du palier en cours, palier suivant)
    cur = tier_index_of_max(max_rank) if learned else 1
    boundaries = [(TIERS[i][3], i + 2) for i in range(max(cur, 1) - 1, len(TIERS) - 1) if TIERS[i][3] < target]
    lines.append("")
    lines += plan_lines(tools, cat, start, target, counts, boundaries, captured_colors(captured), level)
    return lines, verdict
