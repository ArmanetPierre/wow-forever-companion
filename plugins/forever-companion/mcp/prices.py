"""Historique des prix de l'hôtel des ventes relevés par ForeverScribe (stockage côté serveur).

L'addon écrit au niveau du compte (ForeverScribeDB.auction) le dernier relevé par royaume et faction :
    auction = { ["<royaume>|<faction>"] = { lastScan = epoch,
                items = { [itemId] = { min = cuivre, med = cuivre|nil, n = enchères, qty = quantité, t = epoch } } } }

La synchro (sync.py) fusionne ce relevé dans un historique, dans le dossier de données du joueur
(jamais dans le dépôt), un fichier par royaume et faction, partagé par tous les persos et comptes :
    <dossier perso>/prix/<royaume>-<faction>.json
    { "schema": 1, "realm": "...", "faction": "Alliance", "lastScan": epoch,
      "items": { "<itemId>": { "AAAA-MM-JJ": { "min": c, "med": c|null, "qty": n, "n": n, "t": epoch } } } }
Une entrée par objet et par jour (le relevé le plus récent du jour l'emporte) ; les jours de plus de
KEEP_DAYS jours sont supprimés. Bibliothèque standard uniquement.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PRICES_DIR = "prix"
KEEP_DAYS = 60
AH_CUT = 0.05      # commission de l'hôtel des ventes sur une vente (Classic : 5 %) [Classic]
OLD_DAYS = 3       # au-delà, un prix est signalé comme ancien


def _safe(text: str) -> str:
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f#]+', "-", str(text)).strip(" .-")
    return s or "inconnu"


def norm_realm(text: Any) -> str:
    """« CAMWOW EU4 Realm 6 PvP » et « CAMWOWEU4Realm6PvP » donnent la même clé."""
    return re.sub(r"[^0-9a-z]+", "", str(text or "").lower())


def day_of(epoch: float) -> str:
    return datetime.fromtimestamp(float(epoch)).strftime("%Y-%m-%d")


def file_for(data_dir: Path, realm: str, faction: str) -> Path:
    return Path(data_dir) / PRICES_DIR / (_safe(f"{realm}-{faction}") + ".json")


def _read(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _write(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
    for attempt in range(5):  # Windows : fichier verrouillé un instant par un antivirus
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.1 * (attempt + 1))


def _int(v: Any) -> Optional[int]:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def merge_scan(hist: Dict[str, Any], scan: Dict[str, Any], now: Optional[float] = None) -> bool:
    """Fusionne un relevé {lastScan, items} dans l'historique ; True si quelque chose a changé."""
    now = now or time.time()
    items = hist.setdefault("items", {})
    changed = False
    last = _int(scan.get("lastScan"))
    raw = scan.get("items") or {}
    pairs = raw.items() if isinstance(raw, dict) else enumerate(raw, 1)
    for iid, e in pairs:
        if not isinstance(e, dict) or _int(iid) is None:
            continue
        mn = _int(e.get("min"))
        t = _int(e.get("t")) or last
        if not mn or mn <= 0 or not t:
            continue
        entry = {"min": mn, "med": _int(e.get("med")), "qty": _int(e.get("qty")) or 0,
                 "n": _int(e.get("n")) or 0, "t": t}
        days = items.setdefault(str(int(iid)), {})
        day = day_of(t)
        prev = days.get(day)
        if prev and (prev.get("t") or 0) >= t:
            continue
        days[day] = entry
        changed = True
    if last and last > (hist.get("lastScan") or 0):
        hist["lastScan"] = last
        changed = True
    # élagage : jours de plus de KEEP_DAYS jours, objets vides
    cutoff = day_of(now - KEEP_DAYS * 86400)
    for iid in list(items):
        days = items[iid]
        for d in [d for d in days if d < cutoff]:
            del days[d]
            changed = True
        if not days:
            del items[iid]
            changed = True
    return changed


def merge_auction(data_dir: Path, auction: Any, now: Optional[float] = None) -> List[str]:
    """Fusionne ForeverScribeDB.auction (absent ou vide : rien) ; renvoie les fichiers mis à jour."""
    if not isinstance(auction, dict):
        return []
    updated = []
    for key, scan in auction.items():
        if not isinstance(scan, dict) or "|" not in str(key):
            continue
        realm, faction = str(key).rsplit("|", 1)
        path = file_for(data_dir, realm, faction)
        hist = _read(path) or {"schema": 1, "realm": realm, "faction": faction, "items": {}}
        if merge_scan(hist, scan, now):
            _write(path, hist)
            updated.append(path.name)
    return updated


def load(data_dir: Path, realm: Any, faction: Any, realm_alt: Any = None) -> Optional[Dict[str, Any]]:
    """Historique du royaume et de la faction du perso (nom du royaume avec ou sans espaces). Royaume
    absent de la capture (GetRealmName vide) : relevés de la même faction les plus récents, marqués
    `realmGuessed`."""
    if not faction:
        return None
    if realm:
        direct = _read(file_for(data_dir, str(realm), str(faction)))
        if direct:
            return direct
    folder = Path(data_dir) / PRICES_DIR
    if not folder.is_dir():
        return None
    want = {norm_realm(realm), norm_realm(realm_alt)} - {""}
    same_faction = []
    for p in sorted(folder.glob("*.json")):
        h = _read(p)
        if not h or norm_realm(h.get("faction")) != norm_realm(faction):
            continue
        if norm_realm(h.get("realm")) in want:
            return h
        same_faction.append(h)
    if not want and same_faction:
        best = max(same_faction, key=lambda h: h.get("lastScan") or 0)
        return {**best, "realmGuessed": True}
    return None


class Market:
    """Lecture d'un historique : dernier prix, médiane des derniers jours, fraîcheur."""

    def __init__(self, hist: Optional[Dict[str, Any]], now: Optional[float] = None):
        self.hist = hist or {}
        self.items: Dict[str, Dict[str, Any]] = self.hist.get("items") or {}
        self.now = now or time.time()

    def __bool__(self) -> bool:
        return bool(self.items)

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def last_scan(self) -> Optional[int]:
        ts = [e.get("t") or 0 for days in self.items.values() for e in days.values()]
        return max(ts) if ts else self.hist.get("lastScan")

    def latest(self, iid: Any) -> Optional[Dict[str, Any]]:
        days = self.items.get(str(iid))
        if not days:
            return None
        day = max(days)
        return {**days[day], "day": day}

    def buy(self, iid: Any) -> Optional[int]:
        """Prix d'achat unitaire : le plus bas du dernier relevé."""
        e = self.latest(iid)
        return e["min"] if e else None

    def sell_net(self, iid: Any) -> Optional[int]:
        """Revente unitaire nette de la commission HV (au prix le plus bas du dernier relevé)."""
        e = self.latest(iid)
        return int(e["min"] * (1 - AH_CUT)) if e else None

    def trend(self, iid: Any, days: int = 14) -> Tuple[Optional[int], int]:
        """(médiane des prix les plus bas journaliers sur `days` jours, nombre de jours relevés)."""
        d = self.items.get(str(iid)) or {}
        cutoff = day_of(self.now - days * 86400)
        mins = sorted(e["min"] for k, e in d.items() if k >= cutoff and e.get("min"))
        if not mins:
            return None, 0
        return mins[len(mins) // 2], len(mins)

    def age_days(self, iid: Any) -> Optional[float]:
        e = self.latest(iid)
        return (self.now - e["t"]) / 86400 if e and e.get("t") else None
