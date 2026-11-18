"""Vérifie la forme d'une réponse du compagnon (charte v0.8). Bibliothèque standard uniquement.

Contrôles (chacun oui/non) :
- verdict : la première ligne non vide est une phrase en gras (« **…** ») ;
- badge : une source est citée, entre crochets ([Forever · base locale], [Classic · …]) ou en
  forme naturelle (« _Base locale Forever · sûr_ », « QuestieDB », « souvenir Classic ») ;
- liste noire : aucune tournure « IA » de knowledge/voix.md (FR et EN) ;
- emojis : aucun (✔ toléré pour une quête à rendre) ;
- longueur : 20 lignes non vides au plus.

Usage :
    python3 docs/evals/verifie_reponse.py reponse.md [autre.md …]
    pbpaste | python3 docs/evals/verifie_reponse.py -
Code de sortie 0 si tout passe, 1 sinon.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

BLACKLIST = [
    "excellente question", "bonne question", "je serais ravi", "n'hésite pas", "n’hésite pas",
    "si tu as d'autres questions", "si tu as d’autres questions", "en résumé", "pour conclure",
    "il est important de noter", "il convient de", "j'espère que cela", "j’espère que cela",
    "great question", "feel free to", "i'd be happy to", "i’d be happy to", "in summary",
    "it's important to note", "it’s important to note", "i hope this helps",
]
BADGE = re.compile(
    r"\[(Forever|Classic|Retail)[^\]]*\]"
    r"|base locale|local DB|QuestieDB|souvenir Classic|Classic, à vérifier|source Forever|ta capture"
    r"|character data|check in game",
    re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-⛿✀-➿]")
MAX_LINES = 20


def check(text: str) -> List[Tuple[str, bool, str]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    first = lines[0].lstrip("> ").strip() if lines else ""
    low = text.lower()
    bad = [w for w in BLACKLIST if w in low]
    emojis = [e for e in EMOJI.findall(text) if e != "✔"]
    return [
        ("verdict en première ligne", first.startswith("**") and first.count("**") >= 2, first[:80]),
        ("badge de source", bool(BADGE.search(text)), ""),
        ("liste noire", not bad, ", ".join(bad)),
        ("emojis", not emojis, " ".join(emojis)),
        (f"≤ {MAX_LINES} lignes", len(lines) <= MAX_LINES, f"{len(lines)} lignes"),
    ]


def main(argv: List[str]) -> int:
    for _stream in (sys.stdout, sys.stderr):  # sortie redirigée sous Windows = cp1252
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    if not argv:
        print(__doc__)
        return 2
    ok_all = True
    for name in argv:
        text = sys.stdin.read() if name == "-" else Path(name).read_text(encoding="utf-8")
        res = check(text)
        ok = all(r[1] for r in res)
        ok_all &= ok
        print(f"{'OK ' if ok else 'ÉCHEC'} {name}")
        for label, passed, info in res:
            print(f"  {'✔' if passed else '✘'} {label}" + (f" — {info}" if info and not passed else ""))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
