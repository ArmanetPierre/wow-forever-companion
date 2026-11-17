"""Synchronisation des captures ForeverScribe vers le dossier perso/.

Pour chaque compte WoW et chaque personnage capturé par l'addon :
- perso/<Utilisateur>/<Nom>-<Région>/etat.json      état complet (dernière capture)
- perso/<Utilisateur>/<Nom>-<Région>/profil.md      section auto régénérée, notes conservées
- perso/<Utilisateur>/<Nom>-<Région>/journal.md     section auto : changements détectés
- perso/<Utilisateur>/<Nom>-<Région>/historique/AAAA-MM-JJ.json   dernier instantané du jour

Dossier perso/ (ordre de recherche) :
1. variable d'environnement FOREVER_DATA_DIR
2. ./perso dans le dossier de travail, s'il existe
3. ~/WowForever/perso

Usage en ligne de commande :
    python3 sync.py                 synchronise ce qui a changé
    python3 sync.py --force         resynchronise tout
    python3 sync.py --data-dir DIR  utilise un autre dossier perso/
    python3 sync.py --wow PATH      ajoute un dossier du jeu à la configuration
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import formats as F  # noqa: E402
import i18n as I  # noqa: E402
from i18n import T  # noqa: E402
from luasv import LuaParseError, as_list, load_file  # noqa: E402

SV_NAME = "ForeverScribe.lua"
AUTO_START = "<!-- auto:debut -->"
AUTO_END = "<!-- auto:fin -->"
CONFIG_NAME = "config.json"
STATE_NAME = ".sync-state.json"


# ----------------------------------------------------------------------------
# Emplacements
# ----------------------------------------------------------------------------

def resolve_data_dir(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("FOREVER_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve()
    local = Path.cwd() / "perso"
    if local.is_dir():
        return local.resolve()
    return (Path.home() / "WowForever" / "perso").resolve()


def normalize_wow_path(path: Path) -> Optional[Path]:
    """Accepte le dossier du jeu ou son sous-dossier _forever_ ; renvoie celui qui contient WTF/."""
    p = Path(path).expanduser()
    for cand in (p, p / "_forever_"):
        if (cand / "WTF").is_dir() or (cand / "Interface").is_dir():
            return cand
    return None


def detect_wow_paths() -> List[Path]:
    """Cherche WoW Forever aux emplacements habituels (macOS, Windows, Linux/Wine)."""
    home = Path.home()
    cands: List[Path] = [
        Path("/Applications/World of Warcraft"),
        home / "Applications" / "World of Warcraft",
    ]
    if os.name == "nt":
        for drive in "CDEFG":
            for pf in ("Program Files (x86)", "Program Files", "Games", ""):
                cands.append(Path(f"{drive}:/") / pf / "World of Warcraft")
    globs = [
        "Games/*/drive_c/Program Files*/World of Warcraft",
        ".wine/drive_c/Program Files*/World of Warcraft",
        ".local/share/wineprefixes/*/drive_c/Program Files*/World of Warcraft",
        ".local/share/lutris/prefixes/*/drive_c/Program Files*/World of Warcraft",
        ".steam/steam/steamapps/compatdata/*/pfx/drive_c/Program Files*/World of Warcraft",
        ".local/share/Steam/steamapps/compatdata/*/pfx/drive_c/Program Files*/World of Warcraft",
        ".var/app/com.usebottles.bottles/data/bottles/bottles/*/drive_c/Program Files*/World of Warcraft",
    ]
    if os.name != "nt":
        for pattern in globs:
            cands.extend(home.glob(pattern))
    out: List[Path] = []
    for c in cands:
        n = normalize_wow_path(c)
        if n and n not in out:
            out.append(n)
    return out


def safe_name(text: str) -> str:
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f#]+', "-", str(text)).strip(" .-")
    return s or "inconnu"


# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    os.replace(tmp, path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load_config(data_dir: Path) -> Dict[str, Any]:
    cfg = load_json(data_dir / CONFIG_NAME, {})
    cfg.setdefault("version", 1)
    cfg.setdefault("wowPaths", [])
    cfg.setdefault("accounts", {})
    cfg.setdefault("characters", {})
    cfg.setdefault("active", None)
    return cfg


def save_config(data_dir: Path, cfg: Dict[str, Any]) -> None:
    write_json(data_dir / CONFIG_NAME, cfg)


def wow_paths(cfg: Dict[str, Any]) -> List[Path]:
    paths = [normalize_wow_path(Path(p)) for p in cfg.get("wowPaths", [])]
    paths = [p for p in paths if p]
    if not paths:
        paths = detect_wow_paths()
        if paths:
            cfg["wowPaths"] = [str(p) for p in paths]
    return paths


def user_for_account(cfg: Dict[str, Any], account: str) -> str:
    user = cfg["accounts"].get(account)
    if not user:
        user = "Compte-" + safe_name(account)
        cfg["accounts"][account] = user
        cfg.setdefault("accountsPending", [])
        if account not in cfg["accountsPending"]:
            cfg["accountsPending"].append(account)
    return user


# ----------------------------------------------------------------------------
# Lecture du dossier WTF
# ----------------------------------------------------------------------------

def scan_wow(wow: Path) -> List[Dict[str, Any]]:
    """Liste les comptes, l'index de l'addon et les dossiers de persos (capturés ou non)."""
    accounts = []
    base = wow / "WTF" / "Account"
    if not base.is_dir():
        return accounts
    for acc_dir in sorted(p for p in base.iterdir() if p.is_dir() and p.name != "SavedVariables"):
        acc = {"account": acc_dir.name, "dir": acc_dir, "wow": wow,
               "index": acc_dir / "SavedVariables" / SV_NAME, "chars": []}
        for realm_dir in sorted(p for p in acc_dir.iterdir() if p.is_dir() and p.name != "SavedVariables"):
            for char_dir in sorted(p for p in realm_dir.iterdir() if p.is_dir()):
                sv = char_dir / "SavedVariables" / SV_NAME
                acc["chars"].append({"realmDir": realm_dir.name, "dirName": char_dir.name,
                                     "sv": sv if sv.is_file() else None})
        accounts.append(acc)
    return accounts


def file_signature(path: Path) -> Dict[str, Any]:
    st = path.stat()
    return {"mtime_ns": st.st_mtime_ns, "size": st.st_size}


def sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


# ----------------------------------------------------------------------------
# Détection des changements (journal automatique)
# ----------------------------------------------------------------------------

def _by(items: Iterable[Dict[str, Any]], key: str) -> Dict[Any, Dict[str, Any]]:
    return {it.get(key): it for it in items if isinstance(it, dict) and it.get(key) is not None}


def diff_states(old: Optional[Dict[str, Any]], new: Dict[str, Any],
                zones_seen: Optional[set] = None) -> List[str]:
    """Liste des changements notables entre deux captures, dans la langue de sortie courante."""
    g = F.g
    if not old:
        ident = g(new, "identity", default={})
        return [T("Première capture par l'addon : {race} {cls} niveau {level} · {zone} · {n} quêtes en cours · "
                  "{done} terminées", race=ident.get('race', '?'), cls=ident.get('class', '?'),
                  level=g(new, 'progression', 'level') or ident.get('level', '?'),
                  zone=g(new, 'position', 'zone', default='?'), n=g(new, 'quests', 'count', default='?'),
                  done=g(new, 'questsCompleted', 'count', default='?'))]
    ev: List[str] = []

    # Niveau
    lo, ln = g(old, "progression", "level"), g(new, "progression", "level")
    if isinstance(lo, int) and isinstance(ln, int) and ln > lo:
        ev.append(T("**Niveau {n} atteint**", n=ln) + (f" (+{ln - lo})" if ln - lo > 1 else ""))

    # Quêtes rendues / abandonnées
    old_log = _by(as_list(g(old, "quests", "list")), "id")
    new_log = _by(as_list(g(new, "quests", "list")), "id")
    old_done = set(as_list(g(old, "questsCompleted", "ids")))
    new_done = set(as_list(g(new, "questsCompleted", "ids")))
    turned_in = new_done - old_done
    if g(new, "questsCompleted") and g(old, "questsCompleted"):
        names = [old_log[q]["title"] for q in sorted(turned_in) if q in old_log]
        unknown = len(turned_in) - len(names)
        for n in names:
            ev.append(T("Quête rendue : {title}", title=n))
        if unknown > 0:
            ev.append(T("{n} autre(s) quête(s) terminée(s)", n=unknown))
    if g(new, "quests") and g(old, "quests"):
        for qid, q in old_log.items():
            if qid not in new_log and qid not in turned_in and qid not in new_done:
                ev.append(T("Quête retirée du journal (abandonnée ?) : {title}", title=q.get('title')))
        for qid, q in new_log.items():
            if q.get("complete") and qid in old_log and not old_log[qid].get("complete"):
                ev.append(T("Objectifs remplis, à rendre : {title}", title=q.get('title')))

    # Équipement
    so = g(old, "equipment", "slots", default={}) or {}
    sn = g(new, "equipment", "slots", default={}) or {}
    if so or sn:
        for slot, lab in F.slots_localized():
            a, b = so.get(slot), sn.get(slot)
            ida = a.get("itemId") if a else None
            idb = b.get("itemId") if b else None
            if idb and idb != ida:
                txt = T("Équipé ({slot}) : {name}", slot=lab, name=b.get('name')) + f" (ilvl {b.get('itemLevel', '?')}"
                if b.get("dps"):
                    txt += f", {F.num(b['dps'], 1)} DPS"
                txt += ")"
                if a:
                    txt += T(" à la place de {name}", name=a.get('name'))
                ev.append(txt)

    # Métiers
    po = _by(as_list(g(old, "professions", "professions")), "name")
    pn = _by(as_list(g(new, "professions", "professions")), "name")
    for name, p in pn.items():
        if name not in po:
            if po or g(old, "professions"):
                ev.append(T("Nouveau métier : {name} ({rank}/{max})", name=name, rank=p.get('rank'), max=p.get('max')))
        else:
            ro, rn = po[name].get("rank"), p.get("rank")
            if isinstance(ro, int) and isinstance(rn, int) and rn != ro:
                ev.append(f"{name}{F.sep()}{ro} → {rn}" + (f" (max {p.get('max')})" if p.get("max") != po[name].get("max") else ""))
            elif p.get("max") != po[name].get("max"):
                ev.append(T("{name} : plafond porté à {max}", name=name, max=p.get('max')))

    # Zone
    zn = g(new, "position", "zone")
    if zn and zn != g(old, "position", "zone"):
        if zones_seen is None or zn not in zones_seen:
            ev.append(T("Nouvelle zone : {zone}", zone=zn))

    # Réputations
    ro_ = _by(as_list(g(old, "reputations", "list")), "name")
    for name, f in _by(as_list(g(new, "reputations", "list")), "name").items():
        if name in ro_ and f.get("standing") != ro_[name].get("standing"):
            ev.append(T("Réputation {name} : {a} → {b}", name=name, a=ro_[name].get('standing'), b=f.get('standing')))
        elif name not in ro_ and ro_:
            ev.append(T("Nouvelle réputation : {name} ({standing})", name=name, standing=f.get('standing')))

    # Talents
    to_ = {n.get("nodeId"): n for n in as_list(g(old, "talents", "nodes"))}
    tn = {n.get("nodeId"): n for n in as_list(g(new, "talents", "nodes"))}
    if g(old, "talents") and g(new, "talents"):
        for nid, n in tn.items():
            r_old = to_.get(nid, {}).get("rank", 0)
            if n.get("rank", 0) != r_old:
                ev.append(f"Talent {n.get('name')}{F.sep()}{r_old} → {n.get('rank')}/{n.get('maxRank')}")
        for nid, n in to_.items():
            if nid not in tn:
                ev.append(T("Talent retiré : {name}", name=n.get('name')))
        if g(new, "talents", "specName") != g(old, "talents", "specName"):
            ev.append(T("Spé : {a} → {b}", a=g(old, 'talents', 'specName'), b=g(new, 'talents', 'specName')))

    # Sorts appris
    def spell_ids(db: Dict[str, Any]) -> Dict[Any, str]:
        out = {}
        for ln_ in as_list(g(db, "spells", "lines")):
            for s in as_list(ln_.get("spells")):
                out[s.get("spellId")] = f"{s.get('name')}" + (f" ({s['subName']})" if s.get("subName") else "")
        return out

    if g(old, "spells") and g(new, "spells"):
        so_, sn_ = spell_ids(old), spell_ids(new)
        learned = [sn_[k] for k in sn_ if k not in so_]
        if learned:
            ev.append(T("Nouveau(x) sort(s) : {list}", list=", ".join(learned[:10])) + (" …" if len(learned) > 10 else ""))

    # Familier
    po_, pn_ = g(old, "pet", "current", "level"), g(new, "pet", "current", "level")
    if isinstance(po_, int) and isinstance(pn_, int) and pn_ > po_ and \
            g(old, "pet", "current", "name") == g(new, "pet", "current", "name"):
        ev.append(T("Familier {name} niveau {level}", name=g(new, 'pet', 'current', 'name'), level=pn_))
    return ev


# ----------------------------------------------------------------------------
# Valeurs vides écrites à la déconnexion
# ----------------------------------------------------------------------------

def _torn(domain: str, data: Any, db: Dict[str, Any]) -> bool:
    """Vrai si le domaine a été relu pendant la déconnexion (le jeu renvoie alors des zéros)."""
    g = F.g
    if not isinstance(data, dict) or not data:
        return False
    if domain == "progression":
        return (data.get("xpMax") or 0) == 0 and (data.get("level") or 0) < (data.get("maxLevel") or 60)
    if domain == "stats":
        return (data.get("health") or 0) == 0
    if domain == "bags":
        return (data.get("totalSlots") or 0) == 0
    if domain == "money":
        return (data.get("copper") or 0) == 0 and _torn("bags", g(db, "bags"), db)
    if domain == "position":
        return data.get("x") is None and data.get("mapId") is None
    if domain == "pet":
        return not data.get("active") and not data.get("hasPetUI") and _torn("stats", g(db, "stats"), db)
    return False


TORN_DOMAINS = ("progression", "stats", "bags", "money", "position", "pet")


def repair_logout(db: Dict[str, Any], previous: Optional[Dict[str, Any]]) -> List[str]:
    """Remplace les domaines vidés à la déconnexion par la capture précédente valable."""
    if not previous:
        return []
    fixed = []
    torn = {dom for dom in TORN_DOMAINS if _torn(dom, db.get(dom), db)}
    for dom in TORN_DOMAINS:
        if dom in torn and previous.get(dom) and not _torn(dom, previous.get(dom), previous):
            if dom == "progression":
                keep = dict(previous[dom])
                if isinstance(db[dom].get("timePlayed"), dict):
                    keep["timePlayed"] = db[dom]["timePlayed"]  # le temps de jeu reste valable
                db[dom] = keep
            elif dom == "position":
                keep = dict(previous[dom])
                for k in ("zone", "subZone", "realZone", "bind"):
                    if db[dom].get(k):
                        keep[k] = db[dom][k]
                if keep.get("zone") != previous[dom].get("zone"):
                    keep.pop("x", None), keep.pop("y", None)
                db[dom] = keep
            else:
                db[dom] = previous[dom]
            ts = F.g(previous, "meta", "domainsUpdatedAt", dom)
            if ts and isinstance(F.g(db, "meta", "domainsUpdatedAt"), dict):
                db["meta"]["domainsUpdatedAt"][dom] = ts
            fixed.append(dom)
    if fixed:
        db.setdefault("meta", {})["repairedFromPrevious"] = fixed
    return fixed


# ----------------------------------------------------------------------------
# Fichiers markdown
# ----------------------------------------------------------------------------

def replace_auto(text: str, block: str) -> str:
    start, end = text.find(AUTO_START), text.find(AUTO_END)
    if start >= 0 and end > start:
        return text[:start] + AUTO_START + "\n" + block.rstrip() + "\n" + text[end:]
    return None  # type: ignore[return-value]


def write_profile(path: Path, db: Dict[str, Any], source: Dict[str, Any]) -> None:
    ident = F.g(db, "identity", default={})
    block = F.render_profile_auto(db, source)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if text:
        new = replace_auto(text, block)
        if new is None:
            # profil sans balises : on garde l'ancien contenu comme notes
            lines = text.splitlines()
            body = "\n".join(lines[1:]).strip() if lines and lines[0].startswith("# ") else text.strip()
            new = (T("# Profil — {name}-{suffix} ({region})", name=ident.get('name'), suffix=ident.get('suffix'),
                     region=ident.get('region')) + "\n\n"
                   f"{AUTO_START}\n{block}{AUTO_END}\n\n" + T("## Mes notes") + "\n\n"
                   + T("### Ancien profil (avant l'addon)") + f"\n\n{body}\n")
    else:
        new = (T("# Profil — {name}-{suffix} ({region})", name=ident.get('name'), suffix=ident.get('suffix'),
                 region=ident.get('region')) + "\n\n"
               f"{AUTO_START}\n{block}{AUTO_END}\n\n" + T("## Mes notes") + "\n\n"
               + T("<!-- Tes notes à la main : jamais modifiées par la synchro. -->") + "\n")
    if new != text:
        write_text(path, new)


# Les balises auto:debut / auto:fin restent identiques dans les deux langues (compatibilité).
JOURNAL_TEMPLATE_EN = """# Journal — {name}

## My notes
<!-- Your own notes, newest first. Never modified by the sync. -->

## Automatic journal
{start}
<!-- Written after each in-game sync; newest first. -->
{end}
"""

JOURNAL_TEMPLATE = """# Journal — {name}

## Mes notes
<!-- Tes notes à la main, le plus récent en haut. Jamais modifiées par la synchro. -->

## Journal automatique
{start}
<!-- Écrit par la synchro après chaque synchro en jeu ; le plus récent en haut. -->
{end}
"""


def append_journal(path: Path, name: str, stamp: str, events: List[str]) -> None:
    if not events:
        return
    text = path.read_text(encoding="utf-8") if path.exists() else \
        journal_template().format(name=name, start=AUTO_START, end=AUTO_END)
    new_lines = [f"- {stamp} · {e}" for e in events]
    start, end = text.find(AUTO_START), text.find(AUTO_END)
    if start < 0 or end < start:
        text = text.rstrip() + "\n\n" + T("## Journal automatique") + "\n" + AUTO_START + "\n" + AUTO_END + "\n"
        start, end = text.find(AUTO_START), text.find(AUTO_END)
    inner = text[start + len(AUTO_START):end].strip("\n").splitlines()
    comments = [ln for ln in inner if ln.startswith("<!--")]
    entries = [ln for ln in inner if ln.strip() and not ln.startswith("<!--")]
    block = "\n".join(comments + new_lines + entries)
    write_text(path, text[:start] + AUTO_START + "\n" + block + "\n" + text[end:])


def add_manual_notes(text: str, lines: List[str]) -> str:
    """Ajoute des lignes dans la section « Mes notes » du journal (sans doublons)."""
    new = [ln for ln in lines if ln not in text]
    if not new:
        return text
    rows = text.splitlines()
    try:
        i = next(k for k, r in enumerate(rows) if r.strip() in NOTES_HEADINGS)
    except StopIteration:
        return text.rstrip() + "\n\n" + T("## Mes notes") + "\n" + "\n".join(new) + "\n"
    j = i + 1
    while j < len(rows) and rows[j].startswith("<!--"):
        j += 1
    rows[j:j] = new
    return "\n".join(rows) + "\n"


NOTES_HEADINGS = ("## Mes notes", "## My notes")


def journal_template() -> str:
    return JOURNAL_TEMPLATE_EN if I.get_lang() == "en" else JOURNAL_TEMPLATE


def objectives_template() -> str:
    return OBJECTIFS_TEMPLATE_EN if I.get_lang() == "en" else OBJECTIFS_TEMPLATE


OBJECTIFS_TEMPLATE_EN = """# Goals — {name}

## Main goal
- to fill in (tell the agent what you want to achieve)

## Play style
- Pace:
- Group or solo:
- What I like / dislike:
"""

OBJECTIFS_TEMPLATE = """# Objectifs — {name}

## Objectif principal
- à remplir (dis à l'agent ce que tu veux accomplir)

## Style de jeu
- Rythme :
- En groupe ou solo :
- Ce que j'aime / n'aime pas :
"""


# ----------------------------------------------------------------------------
# Migration de l'ancienne organisation perso/<Perso>/
# ----------------------------------------------------------------------------

def migrate_legacy(data_dir: Path, cfg: Dict[str, Any], report: Dict[str, Any]) -> None:
    """perso/Brannok/ (ancienne organisation) -> perso/<Utilisateur>/<Nom>-<Région>/."""
    users = {u for u in cfg["accounts"].values()}
    for legacy in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        if legacy.name in users or legacy.name.startswith(".") or not (legacy / "profil.md").exists():
            continue
        target = None
        for guid, ch in cfg["characters"].items():
            if F.norm_key(ch.get("name")) == F.norm_key(legacy.name):
                target = data_dir / ch["user"] / ch["folder"]
                break
        if not target or not target.exists():
            continue
        archive = target / "archive"
        archive.mkdir(exist_ok=True)
        copies: List[Tuple[Path, Path]] = []
        # objectifs.md : on garde la version manuelle
        if (legacy / "objectifs.md").exists():
            dst = target / "objectifs.md"
            if dst.exists():
                shutil.copy2(dst, archive / "objectifs-genere.md")
            shutil.copy2(legacy / "objectifs.md", dst)
            copies.append((legacy / "objectifs.md", dst))
        # journal.md : les anciennes lignes deviennent des notes manuelles
        if (legacy / "journal.md").exists():
            old_lines = [ln for ln in (legacy / "journal.md").read_text(encoding="utf-8").splitlines()
                         if ln.startswith("- ")]
            jpath = target / "journal.md"
            text = jpath.read_text(encoding="utf-8") if jpath.exists() else \
                journal_template().format(name=legacy.name, start=AUTO_START, end=AUTO_END)
            text = add_manual_notes(text, old_lines)
            write_text(jpath, text)
            shutil.copy2(legacy / "journal.md", archive / "journal-avant-addon.md")
            copies.append((legacy / "journal.md", archive / "journal-avant-addon.md"))
        # profil.md : archivé (remplacé par les vraies données)
        shutil.copy2(legacy / "profil.md", archive / "profil-avant-addon.md")
        copies.append((legacy / "profil.md", archive / "profil-avant-addon.md"))
        for extra in legacy.iterdir():
            if extra.name not in ("profil.md", "objectifs.md", "journal.md"):
                dst = archive / extra.name
                if extra.is_dir():
                    shutil.copytree(extra, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(extra, dst)
                    copies.append((extra, dst))
        if all(dst.exists() and src.read_bytes() == dst.read_bytes() for src, dst in copies):
            shutil.rmtree(legacy)
            report["migrated"].append(f"{legacy.name} → {target.relative_to(data_dir)}")
        else:
            report["errors"].append(f"migration de {legacy.name} : copie non vérifiée, ancien dossier conservé")


# ----------------------------------------------------------------------------
# Synchro
# ----------------------------------------------------------------------------

def char_folder(cfg: Dict[str, Any], guid: str, ident: Dict[str, Any], user: str) -> str:
    existing = cfg["characters"].get(guid)
    if existing and existing.get("folder"):
        return existing["folder"]
    base = safe_name(f"{ident.get('name', 'Perso')}-{ident.get('region', 'XX')}")
    taken = {c.get("folder") for g_, c in cfg["characters"].items() if c.get("user") == user and g_ != guid}
    if base in taken:
        base = safe_name(f"{ident.get('name')}-{ident.get('suffix')}-{ident.get('region')}")
    return base


def sync(data_dir: Optional[Path] = None, force: bool = False) -> Dict[str, Any]:
    data_dir = data_dir or resolve_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_config(data_dir)
    state = load_json(data_dir / STATE_NAME, {})
    report: Dict[str, Any] = {"dataDir": str(data_dir), "updated": [], "unchanged": 0, "journal": {},
                              "errors": [], "migrated": [], "uncaptured": [], "wowPaths": []}
    paths = wow_paths(cfg)
    report["wowPaths"] = [str(p) for p in paths]
    if not paths:
        report["errors"].append("dossier de WoW Forever introuvable : indique-le avec `sync.py --wow <chemin>`")
    known_guids = set()
    for wow in paths:
        for acc in scan_wow(wow):
            user = user_for_account(cfg, acc["account"])
            # index du compte
            index_chars: Dict[str, Any] = {}
            if acc["index"].is_file():
                try:
                    index_chars = (load_file(acc["index"]).get("ForeverScribeDB") or {}).get("characters") or {}
                except (LuaParseError, OSError) as exc:
                    report["errors"].append(f"index {acc['account']} : {exc}")
            for guid, entry in index_chars.items():
                known_guids.add(guid)
                c = cfg["characters"].setdefault(guid, {})
                c.update({"user": user, "account": acc["account"], "name": entry.get("name"),
                          "suffix": entry.get("suffix"), "region": entry.get("region"),
                          "race": entry.get("race"), "class": entry.get("class"),
                          "level": entry.get("level"), "zone": entry.get("zone"),
                          "ruleset": entry.get("ruleset"), "lastCapture": entry.get("lastCapture")})
                c.setdefault("folder", char_folder(cfg, guid, entry, user))
                c.setdefault("captured", False)
            # fichiers par perso
            for ch in acc["chars"]:
                sv = ch["sv"]
                if not sv:
                    report["uncaptured"].append({"account": acc["account"], "user": user, "dir": ch["dirName"]})
                    continue
                key = str(sv)
                sig = file_signature(sv)
                prev = state.get(key, {})
                guid_prev = prev.get("guid")
                etat_ok = guid_prev and (data_dir / cfg["characters"].get(guid_prev, {}).get("user", "?") /
                                         cfg["characters"].get(guid_prev, {}).get("folder", "?") / "etat.json").exists()
                if not force and etat_ok and prev.get("mtime_ns") == sig["mtime_ns"] and prev.get("size") == sig["size"]:
                    report["unchanged"] += 1
                    continue
                digest = sha1(sv)
                if not force and etat_ok and prev.get("sha1") == digest:
                    state[key] = {**prev, **sig}
                    report["unchanged"] += 1
                    continue
                try:
                    db = load_file(sv).get("ForeverScribeCharDB")
                except (LuaParseError, OSError) as exc:
                    report["errors"].append(f"{ch['dirName']} : fichier illisible ({exc})")
                    continue
                if not isinstance(db, dict) or not db.get("identity"):
                    report["errors"].append(f"{ch['dirName']} : capture vide (fais /scribe puis Ctrl+Maj+S (ou /sync))")
                    continue
                ident = db.get("identity") or {}
                guid = F.g(db, "meta", "guid") or ident.get("guid") or \
                    f"{ident.get('region')}/{ident.get('name')}/{ident.get('suffix')}"
                known_guids.add(guid)
                folder = char_folder(cfg, guid, ident, user)
                cdir = data_dir / user / folder
                cdir.mkdir(parents=True, exist_ok=True)
                etat_path = cdir / "etat.json"
                old = load_json(etat_path, {}).get("data") if etat_path.exists() else None
                previous = old
                if previous is None or not F.g(previous, "meta", "guid"):
                    bak = sv.with_name(sv.name + ".bak")
                    if bak.is_file():
                        try:
                            previous = load_file(bak).get("ForeverScribeCharDB")
                        except (LuaParseError, OSError):
                            previous = None
                lang = I.norm_lang(cfg.get("answer_language")) or I.lang_from_locale(F.game_locale(db)) \
                    or I.DEFAULT
                with I.using(lang):  # fichiers générés (profil, journal) dans la langue du joueur
                    fixed = repair_logout(db, previous)
                    if fixed:
                        report.setdefault("repaired", {})[f"{user}/{folder}"] = fixed
                    suivi = load_json(cdir / ".suivi.json", {"zones": []})
                    zones = set(suivi.get("zones", []))
                    events = diff_states(old, db, zones)
                    zn = F.g(db, "position", "zone")
                    if zn:
                        zones.add(zn)
                    source = {"account": acc["account"], "user": user, "wowPath": str(wow),
                              "svFile": str(sv), "syncedAt": int(time.time())}
                    write_json(etat_path, {"schema": 1, "source": source, "data": db})
                    cap = F.captured_at(db) or time.time()
                    write_json(cdir / "historique" / (F.local_time(cap, "%Y-%m-%d") + ".json"),
                               {"capturedAt": cap, "data": db})
                    write_profile(cdir / "profil.md", db, source)
                    if not (cdir / "objectifs.md").exists():
                        write_text(cdir / "objectifs.md", objectives_template().format(name=ident.get("name")))
                    append_journal(cdir / "journal.md", ident.get("name", "?"), F.local_time(cap, "%Y-%m-%d %H:%M"), events)
                    write_json(cdir / ".suivi.json", {"zones": sorted(zones)})
                    c = cfg["characters"].setdefault(guid, {})
                    c.update({"user": user, "account": acc["account"], "folder": folder,
                              "name": ident.get("name"), "suffix": ident.get("suffix"), "region": ident.get("region"),
                              "race": ident.get("race"), "class": ident.get("class"),
                              "level": F.g(db, "progression", "level") or ident.get("level"),
                              "zone": zn, "ruleset": ident.get("ruleset"), "lastCapture": cap, "captured": True})
                    state[key] = {**sig, "sha1": digest, "guid": guid}
                    report["updated"].append(f"{user}/{folder}")
                    if events:
                        report["journal"][f"{user}/{folder}"] = events
    # persos connus seulement par un dossier WTF : on retire ceux que l'index connaît
    report["uncaptured"] = [u for u in report["uncaptured"]
                            if not any(F.norm_key(c.get("name")) == F.norm_key(u["dir"].split("-")[0]) and c.get("captured")
                                       for c in cfg["characters"].values())]
    try:
        migrate_legacy(data_dir, cfg, report)
    except OSError as exc:
        report["errors"].append(f"migration : {exc}")
    save_config(data_dir, cfg)
    write_json(data_dir / STATE_NAME, state)
    return report


# ----------------------------------------------------------------------------
# Accès aux données pour le serveur
# ----------------------------------------------------------------------------

class Store:
    """Vue des persos synchronisés + résolution du perso demandé."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or resolve_data_dir()
        self.last_report: Dict[str, Any] = {}

    def refresh(self, force: bool = False) -> Dict[str, Any]:
        self.last_report = sync(self.data_dir, force=force)
        return self.last_report

    @property
    def config(self) -> Dict[str, Any]:
        return load_config(self.data_dir)

    def characters(self) -> List[Dict[str, Any]]:
        out = []
        for guid, c in self.config["characters"].items():
            out.append({"guid": guid, **c})
        out.sort(key=lambda c: -(c.get("lastCapture") or 0))
        return out

    def load(self, char: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        path = self.data_dir / char["user"] / char["folder"] / "etat.json"
        etat = load_json(path, None)
        return etat.get("data") if etat else None

    def folder(self, char: Dict[str, Any]) -> Path:
        return self.data_dir / char["user"] / char["folder"]

    def active(self) -> Optional[Dict[str, Any]]:
        chars = [c for c in self.characters() if c.get("captured")]
        if not chars:
            return None
        latest = chars[0]
        act = self.config.get("active") or {}
        chosen = next((c for c in chars if c["guid"] == act.get("guid")), None)
        if chosen and (act.get("setAt") or 0) >= (latest.get("lastCapture") or 0):
            return chosen
        return latest

    def resolve(self, query: Optional[str]) -> Tuple[Optional[Dict[str, Any]], str]:
        """Trouve un perso par GUID, nom, Nom-Région, Utilisateur/Nom… Renvoie (perso, message d'erreur)."""
        if not query:
            act = self.active()
            return (act, "") if act else (None, T("Aucun perso capturé. En jeu : active ForeverScribe, puis Ctrl+Maj+S (ou /sync)."))
        q = F.norm_key(query)
        chars = self.characters()
        exact = [c for c in chars if q in (F.norm_key(c["guid"]), F.norm_key(c.get("name")),
                                           F.norm_key(c.get("folder")), F.norm_key(f"{c.get('user')}/{c.get('folder')}"),
                                           F.norm_key(f"{c.get('name')}-{c.get('suffix')}"))]
        if not exact:
            exact = [c for c in chars if q in F.norm_key(f"{c.get('user')} {c.get('name')} {c.get('suffix')} {c.get('folder')}")]
        if not exact:
            return None, T("Perso « {q} » inconnu. Utilise list_characters.", q=query)
        if len(exact) > 1:
            return None, T("Plusieurs persos correspondent : {list}. Précise.", list=", ".join(
                f"{c.get('user')}/{c.get('folder')}" for c in exact))
        c = exact[0]
        if not c.get("captured"):
            return None, T("{name} n'a pas encore été capturé : connecte-le en jeu avec ForeverScribe actif, puis "
                           "Ctrl+Maj+S (ou /sync).", name=c.get('name'))
        return c, ""

    def set_active(self, char: Dict[str, Any]) -> None:
        cfg = self.config
        cfg["active"] = {"guid": char["guid"], "setAt": int(time.time())}
        save_config(self.data_dir, cfg)

    def register_account(self, account: str, user: str) -> str:
        cfg = self.config
        user = safe_name(user)
        if account not in cfg["accounts"]:
            matches = [a for a in cfg["accounts"] if F.norm_key(account) in F.norm_key(a)]
            if len(matches) != 1:
                return T("Compte « {acc} » inconnu. Comptes : {list}.", acc=account,
                         list=", ".join(cfg['accounts']) or T("aucun"))
            account = matches[0]
        old_user = cfg["accounts"][account]
        if old_user == user:
            return T("Le compte {acc} est déjà rattaché à {user}.", acc=account, user=user)
        cfg["accounts"][account] = user
        cfg["accountsPending"] = [a for a in cfg.get("accountsPending", []) if a != account]
        src_root, dst_root = self.data_dir / old_user, self.data_dir / user
        moved = []
        for guid, c in cfg["characters"].items():
            if c.get("account") != account:
                continue
            src, dst = src_root / c["folder"], dst_root / c["folder"]
            if src.exists():
                if dst.exists():
                    return T("Le dossier {path} existe déjà : déplace-le à la main puis recommence.", path=dst)
                dst_root.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                moved.append(c["folder"])
            c["user"] = user
        if src_root.exists() and not any(src_root.iterdir()):
            src_root.rmdir()
        state = load_json(self.data_dir / STATE_NAME, {})
        save_config(self.data_dir, cfg)
        write_json(self.data_dir / STATE_NAME, state)
        return T("Compte {acc} rattaché à {user}", acc=account, user=user) + (
            T(" ; dossiers déplacés : {list}.", list=", ".join(moved)) if moved else ".")


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Synchronise les captures ForeverScribe vers perso/.")
    ap.add_argument("command", nargs="?", default="sync", choices=["sync"])
    ap.add_argument("--data-dir", help="dossier perso/ (défaut : FOREVER_DATA_DIR, ./perso, ~/WowForever/perso)")
    ap.add_argument("--wow", action="append", help="dossier du jeu (World of Warcraft ou _forever_)")
    ap.add_argument("--account", nargs=2, metavar=("COMPTE", "UTILISATEUR"), action="append",
                    help="rattache un compte WTF à un prénom")
    ap.add_argument("--force", action="store_true", help="resynchronise même sans changement")
    args = ap.parse_args(argv)
    data_dir = resolve_data_dir(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    if args.wow or args.account:
        cfg = load_config(data_dir)
        for w in args.wow or []:
            n = normalize_wow_path(Path(w))
            if not n:
                print(f"Pas de dossier WTF/ dans {w}", file=sys.stderr)
                return 2
            if str(n) not in cfg["wowPaths"]:
                cfg["wowPaths"].append(str(n))
        for acc, user in args.account or []:
            cfg["accounts"][acc] = safe_name(user)
            cfg["accountsPending"] = [a for a in cfg.get("accountsPending", []) if a != acc]
        save_config(data_dir, cfg)
    rep = sync(data_dir, force=args.force)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 1 if rep["errors"] and not rep["updated"] else 0


if __name__ == "__main__":
    sys.exit(main())
