"""Wowhead Forever à la demande : une infobulle par id manquant, seulement quand une question le demande.

Sert à placer un PNJ ou un objet que ni QuestieDB ni la mémoire des quêtes ne situent (PNJ et
quêtes ajoutés par Forever), ou à nommer une quête jamais vue. Règles :

- une requête par id, sur l'infobulle JSON publique (`nether.wowhead.com/tooltip/<type>/<id>`,
  `dataEnv=16` = Forever), jamais de liste ni d'aspiration ;
- au plus `BUDGET` requêtes par appel d'outil, une seconde au moins entre deux requêtes, délai court ;
- résultat gardé dans `<gamedata>/.cache/wowhead/` (absence comprise, revérifiée après 7 jours) ;
- User-Agent générique, aucune donnée du joueur dans l'URL ;
- désactivé par `"web_lookup": false` dans `perso/config.json` ou `FOREVER_WEB_LOOKUP=0` ;
- après une erreur réseau, plus d'essai pendant 10 minutes.

Rien de Wowhead n'est copié dans le dépôt : le cache vit dans le dossier de données du joueur.
"""

from __future__ import annotations

import html
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

URL = "https://nether.wowhead.com/tooltip/{kind}/{id}?dataEnv=16&locale={loc}"
LOCALES = {"enUS": 0, "enGB": 0, "koKR": 1, "frFR": 2, "deDE": 3, "zhCN": 4, "esES": 6, "esMX": 6, "ruRU": 8,
           "ptBR": 10, "itIT": 11}
USER_AGENT = "Mozilla/5.0 (compatible; forever-companion)"
TIMEOUT = 4.0
MIN_INTERVAL = 1.0
BUDGET = 3
MISSING_TTL = 7 * 86400
BACKOFF = 600
KINDS = ("npc", "object", "quest")

_last_request = 0.0
_down_until = 0.0


def default_fetch(url: str) -> Optional[Dict[str, Any]]:
    """GET JSON ; None si l'id n'existe pas (404 ou réponse vide). Lève OSError si le réseau échoue."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read(200_000)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise OSError(f"HTTP {exc.code}") from exc
    data = json.loads(raw.decode("utf-8")) if raw.strip() else None
    return data if isinstance(data, dict) and data.get("name") else None


class Wowhead:
    def __init__(self, cache_dir: Optional[Path], locale: Optional[str], enabled: bool = True,
                 fetch: Callable[[str], Optional[Dict[str, Any]]] = default_fetch):
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.locale = locale or "enUS"
        self.enabled = enabled and os.environ.get("FOREVER_WEB_LOOKUP", "1") not in ("0", "false", "no")
        self.fetch = fetch
        self.budget = BUDGET
        self.used = 0

    def reset(self) -> None:
        self.budget = BUDGET

    def _path(self, kind: str, rid: int) -> Optional[Path]:
        if not self.cache_dir:
            return None
        return self.cache_dir / f"{kind}-{int(rid)}-{self.locale}.json"

    def cached(self, kind: str, rid: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """(trouvé dans le cache, données) — données None = absent de Wowhead (encore valable)."""
        p = self._path(kind, rid)
        if not p or not p.is_file():
            return False, None
        try:
            entry = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False, None
        if entry.get("missing"):
            return (time.time() - (entry.get("at") or 0) < MISSING_TTL), None
        return True, entry.get("data")

    def get(self, kind: str, rid: Any) -> Optional[Dict[str, Any]]:
        """Infobulle (dict) d'un PNJ, objet du monde ou quête ; None si inconnue ou indisponible."""
        global _last_request, _down_until
        try:
            rid = int(rid)
        except (TypeError, ValueError):
            return None
        if kind not in KINDS or rid <= 0:
            return None
        hit, data = self.cached(kind, rid)
        if hit:
            return data
        if not self.enabled or self.budget <= 0 or time.time() < _down_until:
            return None
        wait = MIN_INTERVAL - (time.time() - _last_request)
        if wait > 0:
            time.sleep(wait)
        self.budget -= 1
        self.used += 1
        _last_request = time.time()
        url = URL.format(kind=kind, id=rid, loc=LOCALES.get(self.locale, 0))
        try:
            data = self.fetch(url)
        except (OSError, ValueError):
            _down_until = time.time() + BACKOFF
            return None
        p = self._path(kind, rid)
        if p:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                entry = {"at": int(time.time()), "kind": kind, "id": rid}
                entry.update({"data": data} if data else {"missing": True})
                with open(p, "w", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(entry, ensure_ascii=False))
            except OSError:
                pass
        return data


def position(data: Optional[Dict[str, Any]]) -> Optional[Tuple[int, float, float, int]]:
    """(id de zone AreaTable, x, y, nombre de points) d'une infobulle de PNJ ou d'objet."""
    m = (data or {}).get("map") or {}
    zone = m.get("zone")
    coords = m.get("coords") or {}
    pts: List[Tuple[float, float]] = []
    for floor in (coords.values() if isinstance(coords, dict) else [coords]):
        for c in floor or []:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                pts.append((float(c[0]), float(c[1])))
    if not zone or not pts:
        return None
    if len(pts) > 2:
        best = min(pts, key=lambda p: sum(abs(p[0] - q[0]) + abs(p[1] - q[1]) for q in pts))
    else:
        best = pts[0]
    return int(zone), best[0], best[1], len(pts)


def _strip(fragment: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", fragment)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"[ \t]+", " ", html.unescape(text)).strip()


def quest_summary(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """{name, level, objective} d'une infobulle de quête."""
    if not data or not data.get("name"):
        return None
    tip = data.get("tooltip") or ""
    lvl = re.search(r"(?:Level|Niveau|Stufe|Nivel)\s*(\d+)", tip)
    body = tip.split("</table>", 2)[-1] if tip.count("</table>") >= 2 else tip
    text = _strip(body)
    objective = text.split("\n\n")[0].strip() if text else ""
    req = re.split(r"\n\s*(?:Requirements|Conditions|Voraussetzungen)\s*:?", text, maxsplit=1)
    if len(req) == 2:
        objective = req[0].strip()
    return {"name": data["name"], "level": int(lvl.group(1)) if lvl else None, "objective": objective}
