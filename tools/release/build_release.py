#!/usr/bin/env python3
"""Fabrique les archives d'installation en un clic, attachées aux GitHub Releases.

    python3 tools/release/build_release.py [--out dist]

Produit, dans dist/ (ignoré par git) :
- WoW-Forever-Companion-macOS.zip   : « Installer WoW Forever Companion.command » + files/
- WoW-Forever-Companion-Windows.zip : « Installer WoW Forever Companion.cmd » + files/

files/ contient seulement ce que l'installateur utilise : l'addon ForeverScribe, le plugin
(pour la détection du jeu et la base locale), tools/gamedata, perso.example, install/ et la
licence. La liste vient de git (fichiers suivis ou nouveaux non ignorés) : rien de perso/,
aucune donnée de joueur, aucun fichier ignoré. Bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
MAC_ZIP = "WoW-Forever-Companion-macOS.zip"
WIN_ZIP = "WoW-Forever-Companion-Windows.zip"
TOP = "WoW Forever Companion"
LAUNCHER_MAC = "Installer WoW Forever Companion.command"
LAUNCHER_WIN = "Installer WoW Forever Companion.cmd"

INCLUDE = (
    "addon/ForeverScribe/",
    "plugins/forever-companion/",
    "tools/gamedata/",
    "perso.example/",
    "install/install.sh",
    "install/install.ps1",
    "LICENSE",
)
EXCLUDE_PARTS = ("/tests/", "__pycache__", ".DS_Store")
# Garde-fou : jamais de données de joueur dans une archive publique.
FORBIDDEN = ("perso/", "WTF/", "SavedVariables", ".sqlite")
EXECUTABLE = ("install/install.sh",)


def repo_files(root: Path) -> List[str]:
    """Fichiers suivis + nouveaux fichiers non ignorés, chemins POSIX relatifs à la racine."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, check=True, capture_output=True,
    ).stdout.decode("utf-8")
    return sorted(p for p in out.split("\0") if p and (root / p).is_file())


def payload(files: List[str]) -> List[str]:
    keep = []
    for f in files:
        if not any(f == inc or (inc.endswith("/") and f.startswith(inc)) for inc in INCLUDE):
            continue
        if any(x in "/" + f for x in EXCLUDE_PARTS):
            continue
        if any(x in f for x in FORBIDDEN) and not f.startswith("perso.example/"):
            raise SystemExit(f"refusé : {f} ressemble à une donnée de joueur")
        keep.append(f)
    return keep


def _info(name: str, mode: int) -> zipfile.ZipInfo:
    zi = zipfile.ZipInfo(name, date_time=time.localtime(time.time())[:6])
    zi.compress_type = zipfile.ZIP_DEFLATED
    zi.create_system = 3  # Unix : les permissions de external_attr sont lues par unzip et Archive Utility
    zi.external_attr = (0o100000 | mode) << 16
    return zi


def _crlf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def build(out_dir: Path, root: Path = ROOT) -> List[Path]:
    files = payload(repo_files(root))
    version = json.loads((root / "plugins/forever-companion/.claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    out_dir.mkdir(parents=True, exist_ok=True)
    readme = (
        f"WoW Forever Companion {version}\n\n"
        "FR — Double-clique sur l'installateur. Il installe l'addon, le plugin Claude Code et ton\n"
        "dossier de joueur, puis te dit quoi faire. Relance-le pour mettre à jour.\n"
        "macOS : la première fois, macOS bloque le fichier (pas encore signé) : ouvre Réglages\n"
        "système › Confidentialité et sécurité, puis clique sur « Ouvrir quand même ». Ou, dans le\n"
        "Terminal : xattr -dr com.apple.quarantine <ce dossier décompressé>.\n"
        "La commande en une ligne évite le problème :\n"
        "  curl -fsSL https://raw.githubusercontent.com/ArmanetPierre/wow-forever-companion/main/install/install.sh | bash\n"
        "Il te faut Python 3.9+ (https://www.python.org/downloads/, l'installateur ne l'installe pas)\n"
        "et Claude Code (proposé seulement après ta confirmation).\n"
        "Windows : si SmartScreen s'affiche, « Informations complémentaires » > « Exécuter quand même ».\n\n"
        "EN — Double-click the installer. It installs the addon, the Claude Code plugin and your\n"
        "player folder, then tells you what to do next. Run it again to update.\n"
        "macOS: the first time, macOS blocks it (not signed yet): open System Settings ›\n"
        "Privacy & Security, then click \"Open Anyway\". Or, in Terminal:\n"
        "xattr -dr com.apple.quarantine <this unzipped folder>.\n"
        "The one-line command avoids the problem:\n"
        "  curl -fsSL https://raw.githubusercontent.com/ArmanetPierre/wow-forever-companion/main/install/install.sh | bash\n"
        "You need Python 3.9+ (https://www.python.org/downloads/, the installer does not install it)\n"
        "and Claude Code (offered only after you confirm).\n"
        "Windows: if SmartScreen shows up, \"More info\" > \"Run anyway\".\n\n"
        "https://github.com/ArmanetPierre/wow-forever-companion\n"
    )
    made = []
    for zip_name, launcher, windows in ((MAC_ZIP, LAUNCHER_MAC, False), (WIN_ZIP, LAUNCHER_WIN, True)):
        path = out_dir / zip_name
        if path.exists():
            path.unlink()
        with zipfile.ZipFile(path, "w") as z:
            data = (root / "install/launchers" / launcher).read_bytes()
            z.writestr(_info(f"{TOP}/{launcher}", 0o755), _crlf(data) if windows else data)
            text = readme.encode("utf-8")
            z.writestr(_info(f"{TOP}/{'LISEZ-MOI - README.txt'}", 0o644), _crlf(text) if windows else text)
            for f in files:
                data = (root / f).read_bytes()
                if windows and f.endswith((".ps1", ".cmd", ".bat")):
                    data = _crlf(data)
                mode = 0o755 if f in EXECUTABLE else 0o644
                z.writestr(_info(f"{TOP}/files/{f}", mode), data)
        made.append(path)
    return made


def main(argv: List[str] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(ROOT / "dist"), help="dossier de sortie (défaut : dist/)")
    a = ap.parse_args(argv)
    for p in build(Path(a.out)):
        with zipfile.ZipFile(p) as z:
            n = len(z.namelist())
        print(f"{p}  ({p.stat().st_size // 1024} Ko, {n} fichiers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
