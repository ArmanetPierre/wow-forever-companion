"""Recherche du dossier de WoW Forever sur macOS, Windows et Linux (Wine, Lutris, Proton, Bottles).

Une seule source de vérité, partagée par sync.py (synchro des SavedVariables) et
gamedata/build.py / clientcache.py (base locale du jeu). Bibliothèque standard uniquement ;
`winreg` n'existe que sous Windows et n'est importé que là.

Deux notions :
- racine du jeu : le dossier « World of Warcraft » (contient .build.info et Data/) ;
- dossier de saveur : `_forever_` (contient WTF/, Interface/, Cache/).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Callable, Iterable, List, Optional

FLAVOR = "_forever_"
GAME_DIR = "World of Warcraft"

# Clés de registre écrites par le Battle.net (HKLM, vue 32 bits sous Windows 64 bits).
REGISTRY_KEYS = (
    r"SOFTWARE\WOW6432Node\Blizzard Entertainment\World of Warcraft",
    r"SOFTWARE\Blizzard Entertainment\World of Warcraft",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\World of Warcraft",
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\World of Warcraft",
)
REGISTRY_VALUES = ("InstallPath", "InstallLocation")

# Motifs sous le dossier personnel, Linux (préfixes Wine) et macOS.
HOME_GLOBS = (
    "Games/*/drive_c/Program Files*/World of Warcraft",
    ".wine/drive_c/Program Files*/World of Warcraft",
    ".local/share/wineprefixes/*/drive_c/Program Files*/World of Warcraft",
    ".local/share/lutris/prefixes/*/drive_c/Program Files*/World of Warcraft",
    ".var/app/net.lutris.Lutris/data/lutris/prefixes/*/drive_c/Program Files*/World of Warcraft",
    ".steam/steam/steamapps/compatdata/*/pfx/drive_c/Program Files*/World of Warcraft",
    ".local/share/Steam/steamapps/compatdata/*/pfx/drive_c/Program Files*/World of Warcraft",
    ".var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/*/pfx/drive_c/Program Files*/World of Warcraft",
    ".local/share/bottles/bottles/*/drive_c/Program Files*/World of Warcraft",
    ".var/app/com.usebottles.bottles/data/bottles/bottles/*/drive_c/Program Files*/World of Warcraft",
)
LUTRIS_GAME_DIRS = (
    ".config/lutris/games",
    ".local/share/lutris/games",
    ".var/app/net.lutris.Lutris/config/lutris/games",
    ".var/app/net.lutris.Lutris/data/lutris/games",
)
PREFIX_RE = re.compile(r"^\s*prefix:\s*(.+?)\s*$", re.M)


def _dedupe(paths: Iterable[Path]) -> List[Path]:
    out: List[Path] = []
    seen = set()
    for p in paths:
        key = os.path.normcase(str(p))
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def windows_registry_roots(opener: Optional[Callable[[str, str], Optional[str]]] = None) -> List[Path]:
    """Dossiers déclarés dans le registre. `opener(key, value)` sert aux tests."""
    if opener is None:
        try:
            import winreg  # type: ignore[import-not-found]
        except ImportError:
            return []

        def opener(key: str, value: str) -> Optional[str]:  # type: ignore[no-redef]
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as k:  # type: ignore[attr-defined]
                    return str(winreg.QueryValueEx(k, value)[0])  # type: ignore[attr-defined]
            except OSError:
                return None

    out: List[Path] = []
    for key in REGISTRY_KEYS:
        for value in REGISTRY_VALUES:
            found = opener(key, value)
            if found:
                out.append(Path(found.strip().strip('"')))
    return out


def battlenet_roots(appdata: Optional[str] = None) -> List[Path]:
    """Dossier d'installation par défaut du Battle.net (%APPDATA%\\Battle.net\\Battle.net.config)."""
    appdata = appdata if appdata is not None else os.environ.get("APPDATA", "")
    if not appdata:
        return []
    cfg = Path(appdata) / "Battle.net" / "Battle.net.config"
    try:
        data = json.loads(cfg.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return []
    out: List[Path] = []
    install = (data.get("Client") or {}).get("Install") or {} if isinstance(data, dict) else {}
    base = install.get("DefaultInstallPath") if isinstance(install, dict) else None
    if isinstance(base, str) and base:
        out.append(Path(base) / GAME_DIR)
        out.append(Path(base))
    return out


def lutris_prefix_roots(home: Path) -> List[Path]:
    """Préfixes déclarés dans les fiches de jeu Lutris (clé `prefix:`, lue sans module yaml)."""
    out: List[Path] = []
    for rel in LUTRIS_GAME_DIRS:
        d = home / rel
        if not d.is_dir():
            continue
        for yml in sorted(d.glob("*.y*ml")):
            try:
                text = yml.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in PREFIX_RE.finditer(text):
                prefix = Path(m.group(1).strip().strip("'\"")).expanduser()
                out.extend(sorted(prefix.glob("drive_c/Program Files*/" + GAME_DIR)))
    return out


def candidate_roots(home: Optional[Path] = None, windows: Optional[bool] = None,
                    registry: Optional[Callable[[str, str], Optional[str]]] = None,
                    appdata: Optional[str] = None, volumes: Optional[Path] = None,
                    applications: Optional[Path] = None, drives: str = "CDEFGHIJ") -> List[Path]:
    """Dossiers « World of Warcraft » possibles, du plus probable au moins probable.

    Les paramètres servent aux tests (arborescences simulées) ; par défaut, la machine courante.
    """
    home = home or Path.home()
    windows = (os.name == "nt") if windows is None else windows
    cands: List[Path] = []
    if windows:
        cands.extend(windows_registry_roots(registry))
        cands.extend(battlenet_roots(appdata))
        for drive in drives:
            for pf in ("Program Files (x86)", "Program Files", "Games", "Jeux", "Blizzard", ""):
                cands.append(Path(f"{drive}:/") / pf / GAME_DIR)
    else:
        apps = applications if applications is not None else Path("/Applications")
        cands.extend([apps / GAME_DIR, home / "Applications" / GAME_DIR])
        vol = volumes if volumes is not None else Path("/Volumes")
        if vol.is_dir():
            cands.extend(sorted(vol.glob("*/" + GAME_DIR)))
            cands.extend(sorted(vol.glob("*/Applications/" + GAME_DIR)))
        cands.extend(lutris_prefix_roots(home))
        for pattern in HOME_GLOBS:
            cands.extend(sorted(home.glob(pattern)))
    return _dedupe(cands)


def normalize_wow_path(path: Path) -> Optional[Path]:
    """Accepte le dossier du jeu ou son sous-dossier _forever_ ; renvoie celui qui contient WTF/."""
    p = Path(path).expanduser()
    for cand in (p, p / FLAVOR):
        try:
            if (cand / "WTF").is_dir() or (cand / "Interface").is_dir():
                return cand
        except OSError:
            continue
    return None


def detect_wow_paths(**kw) -> List[Path]:
    """Dossiers de saveur trouvés (ceux qui contiennent WTF/ ou Interface/)."""
    out: List[Path] = []
    for c in candidate_roots(**kw):
        n = normalize_wow_path(c)
        if n and n not in out:
            out.append(n)
    return out


def is_game_root(path: Path) -> bool:
    try:
        return (path / ".build.info").is_file() and (path / "Data").is_dir()
    except OSError:
        return False


def game_root_of(path: Path) -> Optional[Path]:
    """Racine du jeu à partir du dossier du jeu ou de _forever_."""
    p = Path(path).expanduser()
    for cand in (p, p.parent):
        if is_game_root(cand):
            return cand
    return None


def detect_game_root(**kw) -> Optional[Path]:
    """Première racine du jeu (avec .build.info et Data/) trouvée."""
    for c in candidate_roots(**kw):
        root = game_root_of(c)
        if root:
            return root
    return None
