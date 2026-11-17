"""Mémoire de recherche : les trouvailles de l'agent, gardées chez le joueur.

Un fichier Markdown par sujet dans `<dossier de données>/connaissances/` (à côté de `perso/`,
ex. ~/WowForever/connaissances/), avec un en-tête :

    ---
    sujet: Casques en cuir niveau 20-30 (Alliance)
    mots-cles: casque, tete, cuir, niveau 25, alliance
    sources: https://…, https://…
    certitude: probable
    date: 2026-11-17
    version-jeu: 1.60.1
    ---
    (contenu)

Rien n'est envoyé ailleurs : c'est un simple dossier de fichiers texte.
"""

from __future__ import annotations

import os
import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CERTAINTIES = ("sûr", "probable", "à vérifier")
STOP = {"le", "la", "les", "de", "des", "du", "un", "une", "et", "ou", "a", "au", "aux", "en", "pour", "mon",
        "ma", "mes", "est", "il", "y", "que", "qui", "quoi", "quel", "quelle", "quels", "quelles", "ce",
        "cette", "dans", "sur", "avec", "je", "tu", "on", "pas", "plus", "niveau", "niv"}


def knowledge_dir(data_dir: Path) -> Path:
    env = os.environ.get("FOREVER_KNOWLEDGE_DIR")
    if env:
        return Path(env).expanduser()
    return Path(data_dir).parent / "connaissances"


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def _slug(text: str) -> str:
    return re.sub(r"\s+", "-", _norm(text))[:70] or "note"


def _terms(text: str) -> List[str]:
    out = []
    for w in _norm(text).split():
        if w in STOP:
            continue
        if len(w) > 1 or w.isdigit():
            out.append(w[:-1] if len(w) > 4 and w.endswith("s") else w)
    return out


def parse(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    meta: Dict[str, Any] = {}
    body = text
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    meta["body"] = body.strip()
    meta["file"] = path.name
    return meta


def search(data_dir: Path, question: str, limit: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
    folder = knowledge_dir(data_dir)
    if not folder.exists():
        return []
    q = set(_terms(question))
    if not q:
        return []
    scored = []
    for path in sorted(folder.glob("*.md")):
        try:
            note = parse(path)
        except OSError:
            continue
        head = set(_terms(note.get("sujet", "") + " " + note.get("mots-cles", "")))
        body = set(_terms(note.get("body", "")))
        score = 3 * len(q & head) + len(q & body)
        if score:
            scored.append((score / max(len(q), 1), note))
    scored.sort(key=lambda x: (x[0], x[1].get("date", "")), reverse=True)
    return scored[:limit]


def save(data_dir: Path, subject: str, content: str, sources: Optional[List[str]] = None,
         certainty: str = "probable", keywords: Optional[List[str]] = None,
         game_version: Optional[str] = None, today: Optional[date] = None) -> Path:
    if not subject.strip() or not content.strip():
        raise ValueError("sujet et contenu requis")
    cert = certainty.strip().lower()
    if not any(cert.startswith(c) for c in CERTAINTIES):
        raise ValueError(f"certitude attendue : {', '.join(CERTAINTIES)} (avec une précision facultative)")
    folder = knowledge_dir(data_dir)
    folder.mkdir(parents=True, exist_ok=True)
    day = (today or date.today()).isoformat()
    path = folder / f"{day}-{_slug(subject)}.md"
    n = 2
    while path.exists():
        path = folder / f"{day}-{_slug(subject)}-{n}.md"
        n += 1
    def one_line(v: str) -> str:
        return " ".join(str(v).split())  # pas de retour à la ligne dans l'en-tête

    subject = one_line(subject)
    sources = [one_line(x) for x in (sources or []) if str(x).strip()]
    keywords = [one_line(x) for x in keywords] if keywords else None
    kw = ", ".join(keywords) if keywords else ", ".join(sorted(set(_terms(subject))))
    lines = ["---", f"sujet: {subject}", f"mots-cles: {kw}",
             f"sources: {', '.join(sources or [])}", f"certitude: {one_line(certainty)}", f"date: {day}"]
    if game_version:
        lines.append(f"version-jeu: {game_version}")
    lines += ["---", "", content.strip(), ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
