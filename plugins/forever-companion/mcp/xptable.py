"""XP nécessaire pour atteindre un niveau cible.

Source 1 : table LevelExperience du client Forever (copiée dans la base locale, table xp_levels).
Source 2 (repli) : table de Classic Era, identique au client Forever à la date du relevé (1-60).
Bibliothèque standard uniquement.
"""
from typing import Dict, Optional, Tuple

# XP pour passer du niveau N au niveau N+1 (Classic Era, niveaux 1 à 59)
CLASSIC_XP = [400, 900, 1400, 2100, 2800, 3600, 4500, 5400, 6500, 7600, 8800, 10100, 11400, 12900, 14400,
              16000, 17700, 19400, 21300, 23200, 25200, 27300, 29400, 31700, 34000, 36400, 38900, 41400, 44300,
              47400, 50800, 54500, 58600, 62800, 67100, 71600, 76100, 80800, 85700, 90700, 95800, 101000,
              106300, 111800, 117500, 123200, 129100, 135100, 141200, 147500, 153900, 160400, 167100, 173900,
              180800, 187900, 195000, 202300, 209800]
CLASSIC_TABLE: Dict[int, int] = {i + 1: v for i, v in enumerate(CLASSIC_XP)}


def table_from_db(gdb) -> Optional[Dict[int, int]]:
    """Table xp_levels de la base locale, ou None si la base ne l'a pas (base construite avant 0.9.0)."""
    if gdb is None:
        return None
    try:
        rows = gdb.con.execute("SELECT level, xp FROM xp_levels").fetchall()
    except Exception:
        return None
    return {int(r[0]): int(r[1]) for r in rows} or None


def xp_to_target(level: int, xp: int, xp_max: Optional[int], target: int,
                 table: Dict[int, int]) -> Tuple[Optional[int], int]:
    """XP restante jusqu'au niveau `target` : (total ou None si un palier manque, niveau max couvert)."""
    if target <= level:
        return 0, level
    left = (xp_max if xp_max else table.get(level, 0)) - (xp or 0)
    for lvl in range(level + 1, target):
        if lvl not in table:
            return None, lvl
        left += table[lvl]
    return left, target
