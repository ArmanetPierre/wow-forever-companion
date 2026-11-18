"""Caches du client (Cache/WDB/<locale>/*.wdb) ajoutés à la base locale, en lecture seule.

    python3 -m gamedata.clientcache [--data-dir DOSSIER] [--wow DOSSIER] [--locale frFR]

Le client garde ce que le joueur a déjà vu : texte complet des quêtes (questcache.wdb), noms des
créatures (creaturecache.wdb) et des objets du monde (gameobjectcache.wdb). Pour les quêtes ajoutées
par Forever, absentes de QuestieDB, c'est la seule source locale de leur texte, qui nomme souvent le
donneur, le receveur et les lieux.

Tables ajoutées à forever-<locale>.sqlite (recréées à chaque appel, quelques millisecondes) :
c_quests (id, title, title_norm, objectives, description), c_creatures (id, name, subname,
name_norm), c_objects (id, name, name_norm). La signature des fichiers est gardée dans
meta.clientcache_sig : rien n'est relu si les caches n'ont pas changé. Rien n'est écrit dans le
dossier du jeu.
"""
from __future__ import annotations

import argparse
import sys
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .wdb import read_quest_cache, read_wdb

FILES = ("questcache.wdb", "creaturecache.wdb", "gameobjectcache.wdb")
SCHEMA = """
DROP TABLE IF EXISTS c_quests;
DROP TABLE IF EXISTS c_creatures;
DROP TABLE IF EXISTS c_objects;
CREATE TABLE c_quests (id INTEGER PRIMARY KEY, title TEXT, title_norm TEXT, objectives TEXT, description TEXT);
CREATE TABLE c_creatures (id INTEGER PRIMARY KEY, name TEXT, subname TEXT, name_norm TEXT);
CREATE TABLE c_objects (id INTEGER PRIMARY KEY, name TEXT, name_norm TEXT);
CREATE INDEX c_quests_title ON c_quests(title_norm);
CREATE INDEX c_creatures_name ON c_creatures(name_norm);
CREATE INDEX c_objects_name ON c_objects(name_norm);
"""
# Un nom lisible : lettres, au moins 3 caractères, pas un chemin de fichier ni un identifiant technique.
NAME_RE = re.compile(r"^[^\x00-\x1f/\\]{3,80}$")


_LIGATURES = str.maketrans({"œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE", "ß": "ss", "’": " ", "ʼ": " "})

def norm(text: Any) -> str:
    s = unicodedata.normalize("NFKD", (str(text or "")).translate(_LIGATURES)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def signature(wdb_dir: Path) -> str:
    parts = []
    for name in FILES:
        p = wdb_dir / name
        if p.is_file():
            st = p.stat()
            parts.append(f"{name}={st.st_size}:{int(st.st_mtime)}")
    return ";".join(parts)


def _name(strings: List[str], i: int) -> Optional[str]:
    if len(strings) <= i:
        return None
    s = strings[i].strip()
    return s if NAME_RE.match(s) and any(c.isalpha() for c in s) else None


def names(path: Path, with_subname: bool) -> List[Tuple]:
    """[(id, nom, sous-titre?)] d'un cache de créatures ou d'objets : premières chaînes lisibles."""
    if not path.is_file():
        return []
    _header, entries = read_wdb(path)
    out = []
    for e in entries:
        name = _name(e["strings"], 0)
        if not name:
            continue
        if with_subname:
            sub = _name(e["strings"], 1)
            out.append((e["id"], name, sub if sub and len(sub) <= 40 else None, norm(name)))
        else:
            out.append((e["id"], name, norm(name)))
    return out


def current_sig(con: sqlite3.Connection) -> Optional[str]:
    try:
        row = con.execute("SELECT value FROM meta WHERE key = 'clientcache_sig'").fetchone()
    except sqlite3.Error:
        return None
    return row[0] if row else None


def refresh(db_path: Path, wdb_dir: Path, force: bool = False) -> Optional[Dict[str, int]]:
    """Recrée les tables c_* depuis les caches du client. None si rien n'a changé ou rien à lire."""
    db_path, wdb_dir = Path(db_path), Path(wdb_dir)
    if not db_path.is_file() or not wdb_dir.is_dir():
        return None
    sig = signature(wdb_dir)
    if not sig:
        return None
    con = sqlite3.connect(str(db_path))
    try:
        if not force and current_sig(con) == sig:
            return None
        quests = read_quest_cache(wdb_dir / "questcache.wdb") if (wdb_dir / "questcache.wdb").is_file() else {}
        creatures = names(wdb_dir / "creaturecache.wdb", True)
        objects = names(wdb_dir / "gameobjectcache.wdb", False)
        con.executescript(SCHEMA)
        con.executemany("INSERT OR REPLACE INTO c_quests VALUES (?,?,?,?,?)",
                        [(qid, t, norm(t), o, d) for qid, (t, o, d) in quests.items()])
        con.executemany("INSERT OR REPLACE INTO c_creatures VALUES (?,?,?,?)", creatures)
        con.executemany("INSERT OR REPLACE INTO c_objects VALUES (?,?,?)", objects)
        con.execute("INSERT OR REPLACE INTO meta VALUES ('clientcache_sig', ?)", (sig,))
        con.commit()
        return {"quests": len(quests), "creatures": len(creatures), "objects": len(objects)}
    finally:
        con.close()


def main(argv=None) -> int:
    from .build import default_data_root, detect_locale, detect_wow, flavor_dir

    ap = argparse.ArgumentParser(description="Ajoute les caches du client (quêtes, créatures, objets vus) à la base.")
    ap.add_argument("--wow", help="dossier du jeu")
    ap.add_argument("--data-dir", help="dossier de données (défaut ~/WowForever)")
    ap.add_argument("--locale", help="langue du client (défaut : celle du client installé)")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    for _stream in (sys.stdout, sys.stderr):  # sortie redirigée sous Windows = cp1252
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    wow = Path(a.wow).expanduser() if a.wow else detect_wow()
    if wow and wow.name == "_forever_":
        wow = wow.parent
    if not wow:
        raise SystemExit("Jeu introuvable : indique son dossier avec --wow.")
    locale = a.locale or detect_locale(wow)[0]
    root = Path(a.data_dir).expanduser() if a.data_dir else default_data_root()
    db_path = root / "gamedata" / f"forever-{locale}.sqlite"
    counts = refresh(db_path, flavor_dir(wow) / "Cache" / "WDB" / locale, force=a.force)
    print(f"Caches du client : {counts}" if counts else "Caches du client déjà à jour (ou absents).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
