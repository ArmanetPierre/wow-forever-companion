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


_LIGATURES = str.maketrans({"œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE", "ß": "ss", "’": " ", "ʼ": " "})

def knowledge_dir(data_dir: Path) -> Path:
    env = os.environ.get("FOREVER_KNOWLEDGE_DIR")
    if env:
        return Path(env).expanduser()
    return Path(data_dir).parent / "connaissances"


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFKD", (text or "").translate(_LIGATURES)).encode("ascii", "ignore").decode().lower()
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


def search(data_dir: Path, question: str, limit: int = 5,
           min_cover: float = 0.0) -> List[Tuple[float, Dict[str, Any]]]:
    """Notes de la mémoire de recherche. min_cover = part des mots de la question qui doivent apparaître
    (titre, mots-clés ou corps) ; une note sans aucun mot dans son titre doit les contenir tous."""
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
        cover = len(q & (head | body)) / len(q)
        if min_cover and (cover < min_cover or (not q & head and cover < 1)):
            continue
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
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    return path


# ---------------------------------------------------------------------------- connaissances du plugin
PLUGIN_KNOWLEDGE = Path(__file__).resolve().parent.parent / "knowledge"
PLUGIN_FILES = ("forever-essentiels.md", "regles-forever.md", "formules.md")
# Synonymes FR / EN / abréviations de joueurs, pour retrouver une section quelle que soit la langue.
ALIASES = {
    "hc": "hardcore", "skyborne": "eolide", "eolides": "eolide", "legacy": "heritage", "dual": "double",
    "spec": "spe", "specialisation": "spe", "respec": "respe", "layer": "layering", "couche": "layering",
    "layers": "layering", "mount": "monture", "ruleset": "ruleset", "pvp": "jcj", "rp": "jdr",
    "summoning": "invocation", "summon": "invocation", "attunement": "harmonisation", "dungeon": "donjon",
    "dungeons": "donjon", "raids": "raid", "bug": "bug", "bugged": "bug", "buguee": "bug", "buguees": "bug",
}


# Mots vides supplémentaires (FR familier + EN) pour la recherche dans les connaissances du plugin.
STOP_PLUS = STOP | {
    "the", "an", "of", "to", "in", "on", "for", "is", "are", "my", "i", "do", "does", "how", "what", "when",
    "where", "can", "it", "and", "or", "with", "at", "from", "be", "you", "your", "me", "there", "any", "get",
    "faut", "comment", "ca", "cela", "etre", "avoir", "peut", "peux", "combien", "quand", "ou", "si", "se",
    "son", "sa", "ses", "nos", "vos", "leur", "mais", "donc", "alors", "aussi", "encore", "deja", "toujours",
    "faire", "fait", "va", "vais", "veux", "dois", "doit", "sont", "ai", "as", "suis", "es", "ne", "me", "te",
    "moi", "toi", "lui", "elle", "nous", "vous", "ils", "elles", "par", "chez", "vers", "entre", "sans",
}
# Expressions ramenées à un seul terme avant découpage (FR / EN), pour que « battleground queue » et
# « file d'attente de champ de bataille » se rejoignent.
PHRASES = (
    ("champs de bataille", "bg"), ("champ de bataille", "bg"), ("battlegrounds", "bg"), ("battleground", "bg"),
    ("file d attente", "file"), ("queue", "file"), ("double specialisation", "doublespe"),
    ("double spe", "doublespe"), ("dual spec", "doublespe"), ("dual specialization", "doublespe"),
    ("pierre d invocation", "invocation"), ("pierres d invocation", "invocation"),
    ("summoning stones", "invocation"), ("summoning stone", "invocation"), ("self found", "selffound"),
    ("auto suffisant", "selffound"), ("hotel des ventes", "hdv"), ("auction house", "hdv"), ("ah", "hdv"),
)
_SUFFIXES = ("ements", "ement", "ations", "ation", "ees", "ee", "er", "ez", "e")


def _stem(w: str) -> str:
    """Racinisation très simple (bateaux→bateau, changer/changement→chang, montures→montur)."""
    if len(w) > 4 and w[-1] in "sx":
        w = w[:-1]
    for suf in _SUFFIXES:
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w


def _aterms(text: str) -> List[str]:
    t = " " + _norm(text) + " "
    for a, b in PHRASES:
        t = t.replace(f" {a} ", f" {b} ")
    out = []
    for w in t.split():
        if w in STOP_PLUS or (len(w) < 2 and not w.isdigit()):
            continue
        w = ALIASES.get(w, w)
        out.append(_stem(w))
    return out


_SECTIONS: Dict[str, Any] = {}


def plugin_sections(folder: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Sections ##/### des fichiers de connaissances du plugin (faits Forever sourcés), mises en cache."""
    folder = folder or PLUGIN_KNOWLEDGE
    out: List[Dict[str, Any]] = []
    for name in PLUGIN_FILES:
        path = folder / name
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        key = str(path)
        cached = _SECTIONS.get(key)
        if cached and cached[0] == mtime:
            out += cached[1]
            continue
        secs: List[Dict[str, Any]] = []
        cur: Optional[Dict[str, Any]] = None
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(#{2,3})\s+(.*)$", line)
            if m:
                cur = {"file": name, "title": m.group(2).strip(), "lines": []}
                secs.append(cur)
            elif cur is not None:
                cur["lines"].append(line)
        for sec in secs:
            sec["body"] = "\n".join(sec.pop("lines")).strip()
            sec["head_terms"] = set(_aterms(sec["title"]))
            sec["body_terms"] = set(_aterms(sec["body"]))
        _SECTIONS[key] = (mtime, secs)
        out += secs
    return out


def search_plugin(question: str, limit: int = 3, folder: Optional[Path] = None
                  ) -> List[Tuple[float, Dict[str, Any]]]:
    """Sections des connaissances du plugin qui couvrent la question (au moins 60 % de ses mots)."""
    q = set(_aterms(question))
    if not q:
        return []
    scored = []
    for sec in plugin_sections(folder):
        head, body = sec["head_terms"], sec["body_terms"]
        hit = q & (head | body)
        cover = len(hit) / len(q)
        if not ((q & head and cover >= 0.5) or cover >= 0.75):
            continue
        scored.append(((2 * len(q & head) + len(hit)) / len(q), sec))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]


def known_quest_bugs(folder: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Lignes du tableau « Quêtes buguées connues » : noms FR/EN normalisés, problème, statut, date de l'état."""
    for sec in plugin_sections(folder):
        if not _norm(sec["title"]).startswith("quetes buguees"):
            continue
        m = re.search(r"(\d{2}/\d{2}/\d{4})", sec["title"])
        date = m.group(1) if m else "?"
        out = []
        for line in sec["body"].splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 4 or cells[0].startswith("---") or _norm(cells[0]).startswith("quete"):
                continue
            ids = {int(x) for x in re.findall(r"\bid\s+(\d+)", cells[0])}
            label = re.sub(r"\s*\((?:id\s+\d+)[^)]*\)", "", cells[0]).strip()
            names = [_norm(x) for x in re.split(r"[/,]|…", label) if _norm(x)]
            out.append({"names": names, "ids": ids, "label": label, "zone": cells[1], "problem": cells[2],
                        "status": cells[3], "date": date})
        return out
    return []


def quest_bug(title: Any, folder: Optional[Path] = None, quest_id: Any = None) -> Optional[Dict[str, Any]]:
    """Bug connu d'une quête. Quand la ligne du tableau donne des ids (une seule étape d'une chaîne touchée),
    seul l'id correspondant compte : les autres quêtes du même titre n'héritent pas du bug."""
    n = _norm(str(title or ""))
    try:
        qid = int(quest_id) if quest_id not in (None, "") else None
    except (TypeError, ValueError):
        qid = None
    for b in known_quest_bugs(folder):
        if b.get("ids"):
            if qid is not None and qid in b["ids"]:
                return b
            if qid is None and n and n in b["names"]:
                return b    # titre seul (pas d'id) : on signale, l'appelant précise l'étape
            continue
        if n and n in b["names"]:
            return b
    return None
