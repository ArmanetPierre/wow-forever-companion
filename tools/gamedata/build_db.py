#!/usr/bin/env python3
"""Construit la base locale du jeu WoW Forever : voir plugins/forever-companion/gamedata/build.py.

    python3 tools/gamedata/build_db.py [--wow DOSSIER] [--data-dir DOSSIER] [--locale frFR] [--force]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "plugins" / "forever-companion"))

from gamedata.build import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
