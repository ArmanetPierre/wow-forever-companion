#!/usr/bin/env python3
"""Exporte les cartes du site depuis le cache de cartes du compagnon (lecture seule).

Les cartes viennent du client World of Warcraft du mainteneur, extraites par
`python3 -m gamedata.maps --zone 1437 --zone 1415` (plugin forever-companion). Ce script les
écrit telles quelles en WebP dans site/public/maps/ : pixels d'origine, pleine taille, sans
recadrage ni retouche. Le site recadre, zoome et assombrit en CSS.

Usage : python3 site/scripts/build-maps.py [--cache DOSSIER] [--quality 82]
Défaut du cache : ~/WowForever/gamedata/maps/<version la plus récente>.
Dépendance : Pillow (outil de construction du site seulement, pas du compagnon).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "public" / "maps"
# uiMapID -> (fichier, qualité WebP)
MAPS = {1437: ("paluns.webp", None), 1415: ("royaumes-de-l-est.webp", 70)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", help="dossier d'une version du cache (contient index.json)")
    ap.add_argument("--quality", type=int, default=82)
    a = ap.parse_args()
    try:
        from PIL import Image
    except ImportError:
        print("Pillow requis : python3 -m pip install pillow", file=sys.stderr)
        return 1
    sys.path.insert(0, str(ROOT / "plugins" / "forever-companion"))
    from gamedata import maps as M

    if a.cache:
        mdir = Path(a.cache).expanduser()
    else:
        base = Path.home() / "WowForever" / "gamedata" / "maps"
        found = sorted(base.glob("*/index.json"), key=lambda p: p.stat().st_mtime)
        if not found:
            print(f"aucun cache de cartes dans {base}", file=sys.stderr)
            return 1
        mdir = found[-1].parent
    index = json.loads((mdir / "index.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for mid, (name, q) in MAPS.items():
        entry = index["maps"].get(str(mid))
        got = M.load_map(mdir, mid, entry) if entry else None
        if not got:
            print(f"carte {mid} absente du cache : python3 -m gamedata.maps --zone {mid}", file=sys.stderr)
            return 1
        w, h, rgb = got
        dest = OUT / name
        Image.frombytes("RGB", (w, h), bytes(rgb)).save(dest, "WEBP", quality=q or a.quality, method=6)
        print(f"{mid} {entry['name']} {w}x{h} -> {dest.relative_to(ROOT)} ({dest.stat().st_size // 1024} Ko)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
