"""Couleurs Classic des recettes (jaune, grise) et recettes apprises d'office, téléchargées chez le joueur.

Le client Forever ne renseigne pas `SkillLineAbility.TrivialSkillLineRankLow/High` (jaune/grise) ni
`AcquireMethod`. On les reprend de la même table du client **Classic Era**, exportée en CSV par
wago.tools à un build fixé (WAGO_BUILD). Ces valeurs ne sont **pas** redistribuées par ce dépôt :
le CSV est téléchargé chez le joueur dans <data>/gamedata/.cache/wago/, lu comme des données, et
résumé dans la table `recipe_colors` de sa base locale (schéma : docs/schema-gamedb.md).

Ce sont des valeurs [Classic], vraies dans Forever tant que la recette n'a pas été modifiée.
Verte = milieu jaune-grise (règle du jeu). Réseau absent ou CSV illisible : la base se construit
sans la table et `recipe_rank.py` / `mcp/professions_plan.py` retombent sur leurs estimations.

    python3 -m gamedata.recipe_colors CSV     # vérifie un CSV (nombre de lignes retenues)
"""
from __future__ import annotations

import csv
import io
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple, Union

WAGO_BUILD = "1.15.9.70576"   # Classic Era, build exporté le 2026-10-26
WAGO_URL = "https://wago.tools/db2/SkillLineAbility/csv?build={build}"
SOURCE = "wago.tools — SkillLineAbility (WoW Classic Era {build})"
LICENSE_NOTE = ("Données du client WoW Classic Era (© Blizzard Entertainment), exportées par wago.tools ; "
                "téléchargées chez le joueur, jamais redistribuées par forever-companion.")
# Métiers Classic dont on garde les recettes (ID de SkillLine) : secourisme, forge, travail du cuir,
# alchimie, cuisine, minage (fonte), couture, ingénierie, enchantement.
PROFESSION_SKILLS = frozenset({129, 164, 165, 171, 185, 186, 197, 202, 333})
ACQUIRE_TRAINER_RANK1 = 1     # AcquireMethod 1 : apprise avec le métier, au rang 1
REQUIRED_COLUMNS = ("SkillLine", "Spell", "AcquireMethod", "TrivialSkillLineRankLow", "TrivialSkillLineRankHigh")
TIMEOUT = 60

SCHEMA = """
DROP TABLE IF EXISTS recipe_colors;
CREATE TABLE recipe_colors (spell_id INTEGER PRIMARY KEY, yellow INTEGER, grey INTEGER, trainer_rank1 INTEGER);
"""

Colors = Dict[int, Tuple[int, int, bool]]


def log(msg: str) -> None:
    print(msg, flush=True)


def cache_file(cache: Path, build: str = WAGO_BUILD) -> Path:
    return Path(cache) / "wago" / f"SkillLineAbility-{build}.csv"


def download(cache: Path, build: str = WAGO_BUILD) -> Path:
    """Télécharge le CSV dans le cache s'il n'y est pas encore ; renvoie son chemin."""
    dest = cache_file(cache, build)
    if dest.is_file() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(WAGO_URL.format(build=build), headers={"User-Agent": "forever-companion-gamedata"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = r.read()
    tmp = dest.with_suffix(".csv.tmp")
    tmp.write_bytes(data)
    tmp.replace(dest)
    return dest


def parse_csv(source: Union[Path, str, Iterable[str]]) -> Colors:
    """CSV SkillLineAbility -> {sort: (jaune, grise, apprise d'office)}.

    Garde les lignes des métiers Classic qui ont des couleurs ou sont apprises d'office. Jaune/grise
    valent 0 si inconnues. Lève ValueError si une colonne attendue manque."""
    if isinstance(source, Path):
        text = source.read_text(encoding="utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
    elif isinstance(source, str):
        reader = csv.DictReader(io.StringIO(source.lstrip("﻿")))
    else:
        reader = csv.DictReader(source)
    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError("colonnes absentes du CSV SkillLineAbility : " + ", ".join(missing))
    out: Colors = {}
    for row in reader:
        try:
            skill, spell = int(row["SkillLine"]), int(row["Spell"])
            low, high = int(row["TrivialSkillLineRankLow"] or 0), int(row["TrivialSkillLineRankHigh"] or 0)
            trainer = int(row["AcquireMethod"] or 0) == ACQUIRE_TRAINER_RANK1
        except (TypeError, ValueError):
            continue
        if skill not in PROFESSION_SKILLS or spell <= 0 or not (low or high or trainer):
            continue
        out.setdefault(spell, (low, high, trainer))
    return out


def load(cache: Path, offline: bool = False) -> Colors:
    """Couleurs Classic depuis le cache (téléchargées si besoin). Échec : {} et un message, jamais d'exception."""
    try:
        path = cache_file(cache) if offline else download(cache)
        if not path.is_file():
            log("• Couleurs Classic des recettes : CSV absent du cache (hors ligne) ; estimations ≈.")
            return {}
        colors = parse_csv(path)
        if not colors:
            raise ValueError("aucune recette lue")
        return colors
    except Exception as exc:  # réseau, CSV illisible… : la base se construit sans la table
        log(f"• Couleurs Classic des recettes non téléchargées ({exc}) : la base se construit sans "
            "la table recipe_colors (rangs et couleurs estimés ≈) ; elle sera ajoutée à la prochaine construction.")
        return {}


def fingerprint_part(colors: Colors) -> str:
    return f"recipe_colors={WAGO_BUILD}:{len(colors)}" if colors else "recipe_colors=absent"


def write(con: sqlite3.Connection, colors: Colors) -> int:
    """Écrit la table recipe_colors (rien si `colors` est vide : la table reste absente)."""
    if not colors:
        con.execute("DROP TABLE IF EXISTS recipe_colors")
        return 0
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO recipe_colors VALUES (?,?,?,?)",
                    [(s, y or None, g or None, 1 if t else 0) for s, (y, g, t) in sorted(colors.items())])
    return len(colors)


def meta(colors: Colors) -> Dict[str, str]:
    if not colors:
        return {"recipe_colors_source": "absent"}
    return {"recipe_colors_source": SOURCE.format(build=WAGO_BUILD),
            "recipe_colors_url": WAGO_URL.format(build=WAGO_BUILD),
            "recipe_colors_build": WAGO_BUILD, "recipe_colors_license": LICENSE_NOTE,
            "recipe_colors_imported_at": time.strftime("%Y-%m-%dT%H:%M:%S")}


def read(q) -> Colors:
    """Lit recipe_colors avec `q(sql) -> lignes` (sqlite3 ou GameDB.q) ; {} si la table manque."""
    try:
        rows = q("SELECT spell_id, yellow, grey, trainer_rank1 FROM recipe_colors")
    except sqlite3.Error:
        return {}
    return {int(r[0]): (int(r[1] or 0), int(r[2] or 0), bool(r[3])) for r in rows}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage : python3 -m gamedata.recipe_colors FICHIER.csv")
    log(f"{len(parse_csv(Path(sys.argv[1])))} recettes retenues")
