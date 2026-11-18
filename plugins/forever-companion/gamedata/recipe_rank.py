"""Rang requis des recettes (compétence minimale), quand le client Forever ne le donne pas.

Les fichiers du client Forever mettent `SkillLineAbility.MinSkillLineRank` à 1 pour presque
toutes les recettes. On reconstitue le rang, de la source la plus sûre à la moins sûre :

1. `client`     : `MinSkillLineRank` > 1 (rare, donnée exacte) ;
2. `objet`      : rang inscrit dans les fichiers du client sur un objet lié à la recette —
                  le patron/schéma/plan qui l'apprend (`RequiredSkillRank` de « Patron : X »),
                  sinon l'objet fabriqué quand il exige ce métier (lunettes d'ingénieur, bandages…).
                  Sur les recettes Classic connues, ces deux rangs sont celui de la recette ;
3. `estimation` : 5 × niveau de l'objet fabriqué (plafonné à 300) quand ce niveau dépasse 1 ;
                  sinon le plus haut rang des composants (rang de la recette du même métier qui
                  les fabrique, ou 5 × (niveau d'objet − 5) pour une matière brute : l'étoffe de lin
                  ou le pacifique, niveau 5, servent dès le rang 1).

Couleurs Classic (`colors` : {sort: (jaune, grise, apprise d'office)}, table `recipe_colors` de la base,
téléchargée chez le joueur par `recipe_colors.py` depuis SkillLineAbility de Classic Era) : une recette apprise d'office
avec le métier (AcquireMethod 1 : Rouleau d'étoffe de lin, Poudre d'explosion basique…) est au rang 1
(source `client`) ; une estimation est ramenée dans [jaune − 10, jaune] de Classic (une recette
n'est jamais orange au-delà de sa jaune ; l'écart habituel est de 0 à 30 points). Sans ces couleurs
(table absente : réseau indisponible au build), ces deux règles ne s'appliquent pas.

Le défaut corrigé : l'ancienne estimation (5 × niveau de l'objet) donnait ≈5 à toutes les recettes
dont l'objet fabriqué est de niveau 1 (feux d'artifice, objets de fête, vêtements, objets ajoutés
par Forever…), même quand elles demandent 225 ou 275 de compétence.

Module sans dépendance : utilisé par `build.py` (construction de la base) et par le serveur MCP
(`mcp/professions_plan.py`), qui recalcule le rang à la lecture pour les bases déjà construites.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

Colors = Mapping[int, Tuple[int, int, bool]]

MAX_RANK = 300
# Version de la logique : entre dans l'empreinte de build.py pour reconstruire les bases anciennes.
RANK_LOGIC_VERSION = 3
CLASSIC_SPELL_MAX = 400000  # au-delà : sorts de Season of Discovery ou ajoutés par Forever

_BRACKETS = re.compile(r"^\s*(\[[^\]]*\]\s*)+")


def pattern_target(name: Optional[str]) -> Optional[str]:
    """« Patron : Cape noire en cuir » -> « Cape noire en cuir » ; None si le nom n'a pas de « : »."""
    if not name or ":" not in name:
        return None
    rest = name.split(":", 1)[1].strip()
    return _BRACKETS.sub("", rest).strip() or None


def is_obsolete(name: Optional[str]) -> bool:
    """Objet marqué [PÉRIMÉ], [VIEUX], [DEPRECATED], zz… dans les fichiers du client."""
    n = (name or "").strip()
    return n.startswith("[") or n.lower().startswith(("zz", "inutilis", "unused", "old"))


def _ilvl_rank(ilvl: Any) -> Optional[int]:
    try:
        v = int(ilvl or 0)
    except (TypeError, ValueError):
        return None
    return min(MAX_RANK, 5 * v) if v > 1 else None


def _raw_rank(ilvl: Any) -> Optional[int]:
    """Rang plancher suggéré par une matière brute : 5 × (niveau − 5), au moins 1 (lin, pacifique : 1)."""
    try:
        v = int(ilvl or 0)
    except (TypeError, ValueError):
        return None
    return max(1, min(MAX_RANK, 5 * (v - 5))) if v > 1 else None


def _spell_of(r: Dict[str, Any]) -> Optional[int]:
    if r.get("spell_id"):
        return int(r["spell_id"])
    k = r.get("key")
    return int(k[0]) if isinstance(k, tuple) and k and isinstance(k[0], int) else None


def classic_of(r: Dict[str, Any], colors: Optional[Colors]) -> Optional[Tuple[int, int, bool]]:
    """(jaune, grise, apprise d'office) de Classic pour une recette de Classic, sinon None.

    colors : {sort: (jaune, grise, apprise d'office)} (table recipe_colors) ; None ou vide : aucune."""
    sid = _spell_of(r)
    if not colors or not sid or not r.get("classic", True) or sid >= CLASSIC_SPELL_MAX:
        return None
    return colors.get(sid)


def assign_ranks(recipes: List[Dict[str, Any]], item: Callable[[int], Optional[Dict[str, Any]]],
                 pattern_rank: Callable[[int, str], Optional[int]],
                 same_skill: Callable[[int, Any], bool], colors: Optional[Colors] = None
                 ) -> Dict[Any, Tuple[Optional[int], Optional[str]]]:
    """Rang (valeur, source) de chaque recette.

    recipes : dicts {key, profession_id, name, min_rank, item_id, reagents: [{item_id}], classic} —
              classic (défaut vrai) : recette de Classic (sort < 400000), seule à contraindre ses composants ;
    item(id) -> {ilvl, required_skill, required_skill_rank} ou None ;
    pattern_rank(profession_id, nom de la recette) -> rang du patron qui l'apprend ou None ;
    same_skill(profession_id, required_skill) -> l'objet exige-t-il ce métier (ou son jumeau) ?
    colors : couleurs Classic {sort: (jaune, grise, apprise d'office)} (table recipe_colors), facultatives.
    """
    out: Dict[Any, Tuple[Optional[int], Optional[str]]] = {}
    pending = []
    for r in recipes:
        key, pid = r["key"], r["profession_id"]
        if (r.get("min_rank") or 0) > 1:
            out[key] = (int(r["min_rank"]), "client")
            continue
        cc = classic_of(r, colors)
        if cc and cc[2]:  # apprise d'office avec le métier (Classic) : rang 1
            out[key] = (1, "client")
            continue
        pr = pattern_rank(pid, r.get("name") or "")
        if pr:
            out[key] = (min(MAX_RANK, int(pr)), "objet")
            continue
        made = item(r["item_id"]) if r.get("item_id") else None
        if made:
            rs, rr = made.get("required_skill"), made.get("required_skill_rank") or 0
            if rr > 0 and (not rs or same_skill(pid, rs)):
                out[key] = (min(MAX_RANK, int(rr)), "objet")
                continue
            est = _ilvl_rank(made.get("ilvl"))
            if est:
                out[key] = (est, "estimation")
                continue
        pending.append(r)
    # Repli sur les composants : rang de la recette du même métier qui les fabrique, sinon leur niveau.
    by_product: Dict[Tuple[int, int], int] = {}
    for r in recipes:
        val = out.get(r["key"])
        if val and val[0] and r.get("item_id"):
            k = (r["profession_id"], r["item_id"])
            by_product[k] = min(by_product.get(k, MAX_RANK), val[0])
    for r in pending:
        ranks = []
        for g in r.get("reagents") or []:
            iid = g.get("item_id")
            if not iid:
                continue
            if (r["profession_id"], iid) in by_product:
                ranks.append(by_product[(r["profession_id"], iid)])
                continue
            it = item(iid)
            est = _raw_rank(it.get("ilvl")) if it else None
            if est:
                ranks.append(est)
        out[r["key"]] = (max(ranks), "estimation") if ranks else (None, None)
    # Cohérence : un composant fabriqué par le même métier s'apprend au plus tard au rang de la recette
    # (au rang lu dans le client) qui le consomme — ex. Poudre d'explosion basique ≤ Dynamite basique (1).
    cap: Dict[Tuple[int, int], int] = {}
    for r in recipes:
        val = out.get(r["key"])
        if not val or val[1] not in ("client", "objet") or not r.get("classic", True):
            continue  # recettes ajoutées (camp de Forever…) : leurs rangs ne contraignent pas Classic
        for g in r.get("reagents") or []:
            k = (r["profession_id"], g.get("item_id"))
            cap[k] = min(cap.get(k, MAX_RANK), val[0])
    for r in recipes:
        val = out.get(r["key"])
        k = (r["profession_id"], r.get("item_id"))
        if val and val[1] == "estimation" and k in cap and cap[k] < val[0]:
            out[r["key"]] = (cap[k], "estimation")
    # Bornes Classic : une estimation reste dans [jaune − 10, jaune] de Classic.
    for r in recipes:
        val = out.get(r["key"])
        cc = classic_of(r, colors)
        if not val or val[1] != "estimation" or not val[0] or not cc or not cc[0]:
            continue
        out[r["key"]] = (max(1, min(val[0], cc[0]), cc[0] - 10), "estimation")
    return out


def pattern_index(patterns: Iterable[Tuple[str, Any, Any]], norm: Callable[[str], str]) -> Dict[Tuple[Any, str], int]:
    """(nom du patron, required_skill, required_skill_rank) -> {(métier, nom normalisé de la recette): rang}.

    Les patrons [PÉRIMÉ] comptent aussi : leur rang reste celui de la recette."""
    idx: Dict[Tuple[Any, str], int] = {}
    for name, skill, rank in patterns:
        target = pattern_target(name)
        if not target or not skill or not rank:
            continue
        k = (skill, norm(target))
        if k not in idx or is_obsolete(name) is False:
            idx[k] = int(rank)
    return idx
