"""XP nécessaire pour atteindre un niveau cible.

Source 1 : table LevelExperience du client Forever (copiée dans la base locale, table xp_levels).
Source 2 (repli) : table de Classic Era, identique au client Forever à la date du relevé (1-60).
Bibliothèque standard uniquement.
"""
from typing import Any, Dict, Optional, Tuple

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


# ---------------------------------------------------------------------------
# XP des quêtes
# ---------------------------------------------------------------------------
# XP « pleine » d'une quête normale selon son niveau. [Classic · estimation] : la vraie valeur dépend de
# la quête (difficulté propre, absente de la base locale) ; repères calés sur des récompenses relevées
# en jeu dans Forever (niv. 9 : 775, niv. 10 : 850, niv. 12 : 1150) et sur les ordres de grandeur de
# Classic Era. Écart attendu : environ ±30 % (quêtes d'escorte, de messager ou d'élite).
QUEST_XP_ANCHORS = [(1, 100), (2, 170), (3, 250), (4, 330), (5, 420), (6, 500), (7, 580), (8, 680), (9, 775),
                    (10, 850), (12, 1150), (14, 1300), (16, 1450), (18, 1600), (20, 1800), (22, 2000),
                    (25, 2350), (28, 2650), (30, 2900), (35, 3400), (40, 3950), (45, 4450), (50, 5000),
                    (55, 5600), (58, 6100), (60, 6600)]
# Réduction quand le perso dépasse le niveau de la quête (Classic, cmangos Quest::XPValue) :
# jusqu'à +5 niveaux 100 %, +6 80 %, +7 60 %, +8 40 %, +9 20 %, au-delà 10 %.
QUEST_XP_FACTORS = {6: 0.8, 7: 0.6, 8: 0.4, 9: 0.2}
MAX_LEVEL = 60


def _round_xp(v: float) -> int:
    """Arrondi de lecture (multiple de 5, 10, 25 ou 50 selon la taille) : une estimation n'est pas au point près."""
    step = 5 if v <= 100 else 10 if v <= 500 else 25 if v <= 1000 else 50
    return int(round(v / step) * step)


def quest_base_xp(quest_level: Any) -> Optional[int]:
    """XP pleine estimée d'une quête de ce niveau (interpolation linéaire des repères), None si inconnu."""
    try:
        q = int(quest_level)
    except (TypeError, ValueError):
        return None
    if q <= 0:
        return None
    pts = QUEST_XP_ANCHORS
    if q <= pts[0][0]:
        return pts[0][1]
    if q >= pts[-1][0]:
        return pts[-1][1]
    for (l1, x1), (l2, x2) in zip(pts, pts[1:]):
        if l1 <= q <= l2:
            return _round_xp(x1 + (x2 - x1) * (q - l1) / (l2 - l1))
    return None


def quest_xp_factor(player_level: Any, quest_level: Any) -> float:
    """Part de l'XP pleine reçue selon l'écart de niveau (1.0 jusqu'à +5, puis 0.8 … 0.1)."""
    try:
        d = int(player_level) - int(quest_level)
    except (TypeError, ValueError):
        return 1.0
    if d <= 5:
        return 1.0
    return QUEST_XP_FACTORS.get(d, 0.1)


def quest_xp(quest_level: Any, player_level: Any, base: Optional[int] = None,
             max_level: Any = MAX_LEVEL) -> Optional[int]:
    """XP estimée pour ce perso (réduction selon l'écart de niveau, 0 au niveau maximum)."""
    try:
        if player_level and int(player_level) >= int(max_level or MAX_LEVEL):
            return 0
    except (TypeError, ValueError):
        pass
    full = base if base is not None else quest_base_xp(quest_level)
    if full is None:
        return None
    f = quest_xp_factor(player_level, quest_level) if player_level else 1.0
    return full if f >= 1 else _round_xp(full * f)


def level_after(level: int, xp: int, xp_max: Optional[int], gain: int,
                table: Dict[int, int], max_level: int = MAX_LEVEL) -> Tuple[int, float]:
    """Niveau atteint après `gain` XP : (niveau, fraction du niveau suivant déjà faite, 0-1)."""
    lvl, cur = int(level), int(xp or 0) + int(gain or 0)
    need = int(xp_max) if xp_max else table.get(lvl, 0)
    while need and cur >= need and lvl < max_level:
        cur -= need
        lvl += 1
        need = table.get(lvl, 0)
    if lvl >= max_level or not need:
        return lvl, 0.0
    return lvl, cur / need
