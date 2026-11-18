"""Quêtes, PNJ et objets de WoW Forever depuis QuestieDB, fusionnés dans la base locale du joueur.

    python3 -m gamedata.questie [--data-dir DOSSIER] [--locale frFR] [--force] [--offline]

QuestieDB (https://github.com/Questie/QuestieDB) maintient une base des quêtes de Forever : donneur,
receveur, niveaux, races et classes, objectifs, prérequis et suites, positions des PNJ et des objets.
Ces fichiers ne sont **pas** redistribués par ce dépôt (licence non déclarée sur GitHub, projet
Questie sous GPLv3) : ils sont téléchargés chez le joueur, à une révision fixée (QUESTIE_COMMIT),
dans <data>/gamedata/.cache/questie/<commit>/, puis lus comme des données (jamais exécutés) avec
le parseur Lua de mcp/luasv.py. Les noms traduits viennent des fichiers l10n de Questie.

Tables ajoutées à forever-<locale>.sqlite : q_quests, q_npcs, q_objects, q_spawns, q_items (schéma :
docs/schema-gamedb.md). Rien n'est écrit dans le dossier du jeu.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

_MCP = Path(__file__).resolve().parents[1] / "mcp"
if str(_MCP) not in sys.path:
    sys.path.insert(0, str(_MCP))
import luasv  # noqa: E402

QUESTIE_REPO = "https://github.com/Questie/QuestieDB"
QUESTIE_COMMIT = "e1652ce62113c152da682baf2d6fb85f1396bcfb"   # master du 2026-11-16
QUESTIE_RAW = "https://raw.githubusercontent.com/Questie/QuestieDB/{commit}/{path}"
QUESTIE_SCHEMA = 3   # 3 : q_items garde tous les objets nommés (recherche par nom anglais)
DATA_FILES = {
    "quests": "data/Forever/foreverQuestDB.lua",
    "npcs": "data/Forever/foreverNpcDB.lua",
    "objects": "data/Forever/foreverObjectDB.lua",
    "items": "data/Forever/foreverItemDB.lua",
}
L10N_FILES = {
    "quests": "l10n/Forever/lookupQuests/{locale}.lua",
    "npcs": "l10n/Forever/lookupNpcs/{locale}.lua",
    "objects": "l10n/Forever/lookupObjects/{locale}.lua",
}
L10N_LOCALES = {"deDE", "esES", "esMX", "frFR", "koKR", "ptBR", "ruRU", "zhCN", "zhTW"}
DATA_MARKERS = {"quests": "QuestieDB.questData", "npcs": "QuestieDB.npcData", "objects": "QuestieDB.objectData",
                "items": "QuestieDB.itemData"}
L10N_MARKERS = {"quests": "questLookup", "npcs": "npcNameLookup", "objects": "objectLookup"}
LICENSE_NOTE = ("QuestieDB (github.com/Questie/QuestieDB) — licence non déclarée sur GitHub, projet Questie "
                "sous GPLv3 ; téléchargé chez le joueur, jamais redistribué par forever-companion.")

# Clés de questKeys / npcKeys / objectKeys (positions dans les tables de Questie)
QK = {"name": 1, "startedBy": 2, "finishedBy": 3, "requiredLevel": 4, "questLevel": 5, "requiredRaces": 6,
      "requiredClasses": 7, "objectivesText": 8, "triggerEnd": 9, "objectives": 10, "sourceItemId": 11,
      "preQuestGroup": 12, "preQuestSingle": 13, "childQuests": 14, "inGroupWith": 15, "exclusiveTo": 16,
      "zoneOrSort": 17, "requiredSkill": 18, "requiredMinRep": 19, "requiredMaxRep": 20,
      "requiredSourceItems": 21, "nextQuestInChain": 22, "questFlags": 23, "specialFlags": 24,
      "parentQuest": 25, "reputationReward": 26, "breadcrumbForQuestId": 27, "breadcrumbs": 28,
      "extraObjectives": 29, "requiredSpell": 30, "requiredSpecialization": 31, "requiredMaxLevel": 32}
NK = {"name": 1, "minLevel": 4, "maxLevel": 5, "rank": 6, "spawns": 7, "waypoints": 8, "zoneID": 9,
      "questStarts": 10, "questEnds": 11, "factionID": 12, "friendlyToFaction": 13, "subName": 14,
      "npcFlags": 15}
OK = {"name": 1, "questStarts": 2, "questEnds": 3, "spawns": 4, "zoneID": 5}
IK = {"name": 1, "npcDrops": 2, "objectDrops": 3, "itemDrops": 4, "startQuest": 5, "questRewards": 6,
      "vendors": 14, "relatedQuests": 15}

SCHEMA = """
DROP TABLE IF EXISTS q_quests;
DROP TABLE IF EXISTS q_npcs;
DROP TABLE IF EXISTS q_objects;
DROP TABLE IF EXISTS q_spawns;
DROP TABLE IF EXISTS q_items;
CREATE TABLE q_quests (
  id INTEGER PRIMARY KEY, name TEXT, name_loc TEXT, name_norm TEXT, req_level INTEGER, level INTEGER,
  max_level INTEGER, races INTEGER, classes INTEGER, objectives_text TEXT, zone_id INTEGER, sort_id INTEGER,
  start_npcs TEXT, start_objects TEXT, start_items TEXT, end_npcs TEXT, end_objects TEXT,
  objectives_json TEXT, trigger_json TEXT, source_item INTEGER, pre_group TEXT, pre_single TEXT,
  next_in_chain INTEGER, exclusive_to TEXT, parent INTEGER, children TEXT, breadcrumb_for INTEGER,
  breadcrumbs TEXT, required_skill TEXT, rep_reward TEXT, special_flags INTEGER, quest_flags INTEGER
);
CREATE TABLE q_npcs (
  id INTEGER PRIMARY KEY, name TEXT, name_loc TEXT, name_norm TEXT, subname TEXT, min_level INTEGER,
  max_level INTEGER, rank INTEGER, zone_id INTEGER, friendly TEXT, npc_flags INTEGER, starts TEXT, ends TEXT,
  spawn_count INTEGER
);
CREATE TABLE q_objects (
  id INTEGER PRIMARY KEY, name TEXT, name_loc TEXT, name_norm TEXT, zone_id INTEGER, starts TEXT, ends TEXT,
  spawn_count INTEGER
);
CREATE TABLE q_spawns (kind TEXT, id INTEGER, zone_id INTEGER, x REAL, y REAL);
CREATE TABLE q_items (
  id INTEGER PRIMARY KEY, name TEXT, npc_drops TEXT, object_drops TEXT, item_drops TEXT, vendors TEXT,
  start_quest INTEGER, quest_rewards TEXT, related_quests TEXT
);
CREATE INDEX q_quests_name ON q_quests(name_norm);
CREATE INDEX q_quests_zone ON q_quests(zone_id, level);
CREATE INDEX q_npcs_name ON q_npcs(name_norm);
CREATE INDEX q_objects_name ON q_objects(name_norm);
CREATE INDEX q_spawns_ref ON q_spawns(kind, id);
"""
MAX_SPAWNS_PER_ZONE = 40   # au-delà, points répartis sur l'ensemble (pour /way, quelques points suffisent)


_LIGATURES = str.maketrans({"œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE", "ß": "ss", "’": " ", "ʼ": " "})

def norm(text: Any) -> str:
    s = unicodedata.normalize("NFKD", (str(text or "")).translate(_LIGATURES)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def log(msg: str) -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Lecture des fichiers Lua de Questie (données seulement)
# ---------------------------------------------------------------------------

def extract_table(text: str, marker: str) -> Dict[Any, Any]:
    """Table renvoyée par la chaîne longue `[[return {...}]]` qui suit `marker`."""
    i = text.find(marker)
    if i < 0:
        raise ValueError(f"marqueur {marker!r} introuvable")
    m = re.compile(r"\[(=*)\[").search(text, i)
    if not m:
        raise ValueError(f"chaîne longue introuvable après {marker!r}")
    close = "]" + m.group(1) + "]"
    j = text.find(close, m.end())
    if j < 0:
        raise ValueError("chaîne longue non fermée")
    body = text[m.end():j].strip()
    if not body.startswith("return"):
        raise ValueError("la chaîne longue ne commence pas par return")
    p = luasv._Parser(body[len("return"):])
    p.skip()
    value = p.table()
    if isinstance(value, list):  # ids 1..n consécutifs (fixtures)
        value = {i + 1: v for i, v in enumerate(value)}
    return value


def f(t: Any, i: int) -> Any:
    """Champ positionnel i (1-based) d'une table Lua lue par luasv (liste, ou dict s'il y a des trous)."""
    if isinstance(t, list):
        return t[i - 1] if 0 < i <= len(t) else None
    if isinstance(t, dict):
        return t.get(i)
    return None


def ints(v: Any) -> List[int]:
    out = []
    for x in luasv.as_list(v):
        if isinstance(x, (int, float)) and not isinstance(x, bool):
            out.append(int(x))
    return out


def js(v: Any) -> Optional[str]:
    if v is None or v == [] or v == {}:
        return None
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def spawn_points(spawns: Any) -> Dict[int, List[Tuple[float, float]]]:
    """{zone: [(x, y), …]} depuis {[zone] = {{x, y}, …}}."""
    out: Dict[int, List[Tuple[float, float]]] = {}
    if not isinstance(spawns, (dict, list)):
        return out
    items = spawns.items() if isinstance(spawns, dict) else enumerate(spawns, 1)
    for zone, pts in items:
        if not isinstance(zone, int):
            continue
        for pt in luasv.as_list(pts):
            x, y = f(pt, 1), f(pt, 2)
            if isinstance(x, (int, float)) and isinstance(y, (int, float)) and x >= 0 and y >= 0:
                out.setdefault(zone, []).append((round(float(x), 1), round(float(y), 1)))
    return out


def thin(points: List[Tuple[float, float]], k: int = MAX_SPAWNS_PER_ZONE) -> List[Tuple[float, float]]:
    if len(points) <= k:
        return points
    step = len(points) / k
    return [points[int(i * step)] for i in range(k)]


# ---------------------------------------------------------------------------
# Téléchargement (chez le joueur, révision fixée)
# ---------------------------------------------------------------------------

def _download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "forever-companion-gamedata"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    tmp = dest.with_suffix(dest.suffix + ".part")
    tmp.write_bytes(data)
    tmp.replace(dest)


def fetch(cache: Path, locale: str, commit: str = QUESTIE_COMMIT, offline: bool = False) -> Dict[str, Path]:
    """Télécharge (une fois) les fichiers utiles dans cache/questie/<commit>/. Renvoie {clé: chemin}."""
    root = cache / "questie" / commit
    root.mkdir(parents=True, exist_ok=True)
    wanted = {k: p for k, p in DATA_FILES.items()}
    if locale in L10N_LOCALES:
        wanted.update({f"l10n_{k}": p.format(locale=locale) for k, p in L10N_FILES.items()})
    out = {}
    for key, rel in wanted.items():
        dest = root / rel.replace("/", "__")
        if not dest.is_file():
            if offline:
                if key.startswith("l10n_"):
                    continue
                raise FileNotFoundError(f"{dest} absent (mode --offline)")
            log(f"  téléchargement QuestieDB : {rel}")
            try:
                _download(QUESTIE_RAW.format(commit=commit, path=rel), dest)
            except Exception as exc:
                if key.startswith("l10n_"):  # traduction facultative
                    log(f"  (traduction {rel} indisponible : {exc})")
                    continue
                raise
        out[key] = dest
    return out


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_files(files: Dict[str, Path]) -> Dict[str, Dict[Any, Any]]:
    out = {}
    for key, marker in DATA_MARKERS.items():
        out[key] = extract_table(_read(files[key]), marker)
    for key, marker in L10N_MARKERS.items():
        p = files.get(f"l10n_{key}")
        out[f"l10n_{key}"] = extract_table(_read(p), marker) if p else {}
    return out


def quest_rows(data: Dict[Any, Any], loc: Dict[Any, Any]) -> List[tuple]:
    rows = []
    for qid, q in data.items():
        if not isinstance(qid, int) or not isinstance(q, (list, dict)):
            continue
        name = f(q, QK["name"])
        lq = loc.get(qid)
        name_loc = f(lq, 1) if lq is not None else None
        obj_loc = f(lq, 2) if lq is not None else None
        texts = luasv.as_list(obj_loc) or luasv.as_list(f(q, QK["objectivesText"]))
        texts = [t for t in texts if isinstance(t, str) and t.strip()]
        started, finished = f(q, QK["startedBy"]), f(q, QK["finishedBy"])
        zone = f(q, QK["zoneOrSort"])
        zone = int(zone) if isinstance(zone, (int, float)) else None
        flags = f(q, QK["specialFlags"])
        qflags = f(q, QK["questFlags"])
        rows.append((
            qid, name, name_loc, norm(name) + ("|" + norm(name_loc) if name_loc else ""),
            f(q, QK["requiredLevel"]), f(q, QK["questLevel"]), f(q, QK["requiredMaxLevel"]),
            f(q, QK["requiredRaces"]) or 0, f(q, QK["requiredClasses"]) or 0, js(texts),
            zone if zone and zone > 0 else None, -zone if zone and zone < 0 else None,
            js(ints(f(started, 1))), js(ints(f(started, 2))), js(ints(f(started, 3))),
            js(ints(f(finished, 1))), js(ints(f(finished, 2))),
            js(objectives(f(q, QK["objectives"]))), js(trigger(f(q, QK["triggerEnd"]))),
            f(q, QK["sourceItemId"]), js(ints(f(q, QK["preQuestGroup"]))), js(ints(f(q, QK["preQuestSingle"]))),
            f(q, QK["nextQuestInChain"]) or None, js(ints(f(q, QK["exclusiveTo"]))), f(q, QK["parentQuest"]) or None,
            js(ints(f(q, QK["childQuests"]))), f(q, QK["breadcrumbForQuestId"]) or None,
            js(ints(f(q, QK["breadcrumbs"]))), js(luasv.as_list(f(q, QK["requiredSkill"])) or None),
            js([[f(r, 1), f(r, 2)] for r in luasv.as_list(f(q, QK["reputationReward"]))]),
            int(flags) if isinstance(flags, (int, float)) else 0,
            int(qflags) if isinstance(qflags, (int, float)) else 0,
        ))
    return rows


def objectives(o: Any) -> Dict[str, Any]:
    """Objectifs typés : {creatures: [[id, texte]], objects: […], items: […], reputation: [faction, valeur],
    killcredit: [[[ids], baseId, texte]], spells: [[spell, texte, item]]}."""
    if not isinstance(o, (list, dict)):
        return {}
    out: Dict[str, Any] = {}
    for idx, key in ((1, "creatures"), (2, "objects"), (3, "items")):
        lst = []
        for e in luasv.as_list(f(o, idx)):
            i = f(e, 1)
            if isinstance(i, (int, float)):
                lst.append([int(i), f(e, 2) if isinstance(f(e, 2), str) else None])
        if lst:
            out[key] = lst
    rep = f(o, 4)
    if rep:
        out["reputation"] = [f(rep, 1), f(rep, 2)]
    kc = []
    for e in luasv.as_list(f(o, 5)):
        kc.append([ints(f(e, 1)), f(e, 2), f(e, 3) if isinstance(f(e, 3), str) else None])
    if kc:
        out["killcredit"] = kc
    sp = []
    for e in luasv.as_list(f(o, 6)):
        sp.append([f(e, 1), f(e, 2) if isinstance(f(e, 2), str) else None, f(e, 3)])
    if sp:
        out["spells"] = sp
    return out


def trigger(t: Any) -> Optional[Dict[str, Any]]:
    """Objectif d'exploration : {text, spawns: {zone: [[x, y]]}}."""
    if not isinstance(t, (list, dict)):
        return None
    pts = spawn_points(f(t, 2))
    return {"text": f(t, 1), "spawns": {str(z): thin(p, 5) for z, p in pts.items()}}


def npc_rows(data: Dict[Any, Any], loc: Dict[Any, Any]) -> Tuple[List[tuple], List[tuple]]:
    rows, spawns = [], []
    for nid, n in data.items():
        if not isinstance(nid, int) or not isinstance(n, (list, dict)):
            continue
        name = f(n, NK["name"])
        ln = loc.get(nid)
        name_loc = f(ln, 1) if isinstance(ln, (list, dict)) else (ln if isinstance(ln, str) else None)
        sub_loc = f(ln, 2) if isinstance(ln, (list, dict)) else None
        pts = spawn_points(f(n, NK["spawns"]))
        if not pts:
            pts = spawn_points(f(n, NK["waypoints"]))
        total = 0
        for z, p in pts.items():
            total += len(p)
            spawns.extend(("npc", nid, z, x, y) for x, y in thin(p))
        zone = f(n, NK["zoneID"])
        rows.append((nid, name, name_loc, norm(name) + ("|" + norm(name_loc) if name_loc else ""),
                     sub_loc or f(n, NK["subName"]), f(n, NK["minLevel"]), f(n, NK["maxLevel"]), f(n, NK["rank"]),
                     int(zone) if isinstance(zone, (int, float)) and zone else None, f(n, NK["friendlyToFaction"]),
                     f(n, NK["npcFlags"]), js(ints(f(n, NK["questStarts"]))), js(ints(f(n, NK["questEnds"]))), total))
    return rows, spawns


def object_rows(data: Dict[Any, Any], loc: Dict[Any, Any]) -> Tuple[List[tuple], List[tuple]]:
    rows, spawns = [], []
    for oid, o in data.items():
        if not isinstance(oid, int) or not isinstance(o, (list, dict)):
            continue
        name = f(o, OK["name"])
        name_loc = loc.get(oid) if isinstance(loc.get(oid), str) else None
        pts = spawn_points(f(o, OK["spawns"]))
        total = 0
        for z, p in pts.items():
            total += len(p)
            spawns.extend(("object", oid, z, x, y) for x, y in thin(p))
        zone = f(o, OK["zoneID"])
        rows.append((oid, name, name_loc, norm(name) + ("|" + norm(name_loc) if name_loc else ""),
                     int(zone) if isinstance(zone, (int, float)) and zone else None,
                     js(ints(f(o, OK["questStarts"]))), js(ints(f(o, OK["questEnds"]))), total))
    return rows, spawns


def item_rows(data: Dict[Any, Any]) -> List[tuple]:
    """Nom anglais et sources des objets (butin de PNJ ou d'objet, marchands, quête lancée).

    Tous les objets nommés sont gardés, même sans source (colonnes de sources à NULL) : le nom anglais
    sert à la recherche (« Heavy Linen Bandage » sur un client frFR)."""
    rows = []
    for iid, it in data.items():
        if not isinstance(iid, int) or not isinstance(it, (list, dict)):
            continue
        cols = [ints(f(it, IK[k])) for k in ("npcDrops", "objectDrops", "itemDrops", "vendors")]
        start = f(it, IK["startQuest"])
        rewards, related = ints(f(it, IK["questRewards"])), ints(f(it, IK["relatedQuests"]))
        name = f(it, IK["name"])
        if not any(cols) and not start and not rewards and not related and not isinstance(name, str):
            continue
        rows.append((iid, name if isinstance(name, str) else None, *[js(c) for c in cols],
                     int(start) if isinstance(start, (int, float)) and start else None, js(rewards), js(related)))
    return rows


def current_commit(db_path: Path) -> Optional[str]:
    try:
        con = sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True)
        row = con.execute("SELECT value FROM meta WHERE key='questie_commit'").fetchone()
        sch = con.execute("SELECT value FROM meta WHERE key='questie_schema'").fetchone()
        con.close()
        if row and sch and sch[0] == str(QUESTIE_SCHEMA):
            return row[0]
    except sqlite3.Error:
        pass
    return None


def import_into(db_path: Path, files: Dict[str, Path], commit: str = QUESTIE_COMMIT) -> Dict[str, int]:
    """Ajoute (ou remplace) les tables q_* dans la base. Renvoie les comptes."""
    t = load_files(files)
    qrows = quest_rows(t["quests"], t["l10n_quests"])
    nrows, nsp = npc_rows(t["npcs"], t["l10n_npcs"])
    orows, osp = object_rows(t["objects"], t["l10n_objects"])
    irows = item_rows(t["items"])
    con = sqlite3.connect(str(db_path))
    try:
        con.executescript(SCHEMA)
        con.executemany(f"INSERT INTO q_quests VALUES ({','.join('?' * 32)})", qrows)
        con.executemany(f"INSERT INTO q_npcs VALUES ({','.join('?' * 14)})", nrows)
        con.executemany(f"INSERT INTO q_objects VALUES ({','.join('?' * 8)})", orows)
        con.executemany("INSERT INTO q_spawns VALUES (?,?,?,?,?)", nsp + osp)
        con.executemany("INSERT INTO q_items VALUES (?,?,?,?,?,?,?,?,?)", irows)
        counts = {"items": len(irows), "quests": len(qrows), "npcs": len(nrows), "objects": len(orows), "spawns": len(nsp) + len(osp),
                  "quests_translated": sum(1 for r in qrows if r[2])}
        meta = {"questie_commit": commit, "questie_schema": str(QUESTIE_SCHEMA), "questie_source": QUESTIE_REPO,
                "questie_license": LICENSE_NOTE, "questie_imported_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "questie_counts": json.dumps(counts)}
        con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        con.executemany("INSERT OR REPLACE INTO meta VALUES (?,?)", list(meta.items()))
        con.commit()
        con.execute("VACUUM")
    finally:
        con.close()
    return counts


def run(db_path: Path, cache: Path, locale: str, force: bool = False, offline: bool = False,
        commit: str = QUESTIE_COMMIT) -> Optional[Dict[str, int]]:
    """Étape QuestieDB de build.py : rien si la base contient déjà cette révision (sauf force)."""
    if not force and current_commit(db_path) == commit:
        log(f"• QuestieDB déjà importé (révision {commit[:10]}).")
        return None
    t0 = time.time()
    files = fetch(cache, locale, commit, offline)
    counts = import_into(db_path, files, commit)
    log(f"• QuestieDB {commit[:10]} : {counts['quests']} quêtes (traduites : {counts['quests_translated']}), "
        f"{counts['npcs']} PNJ, {counts['objects']} objets, {counts['spawns']} positions "
        f"en {time.time() - t0:.0f} s")
    return counts


def main(argv: Optional[Iterable[str]] = None) -> int:
    from . import build as B

    ap = argparse.ArgumentParser(description="Ajoute les quêtes et PNJ de QuestieDB à la base locale existante.")
    ap.add_argument("--data-dir", help="dossier de données (défaut ~/WowForever)")
    ap.add_argument("--locale", help="langue de la base (défaut : toutes les bases forever-*.sqlite trouvées)")
    ap.add_argument("--force", action="store_true", help="réimporte même si la révision est déjà présente")
    ap.add_argument("--offline", action="store_true", help="n'utilise que les fichiers déjà téléchargés")
    a = ap.parse_args(list(argv) if argv is not None else None)
    for _stream in (sys.stdout, sys.stderr):  # sortie redirigée sous Windows = cp1252
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    root = Path(a.data_dir).expanduser() if a.data_dir else B.default_data_root()
    out = root / "gamedata"
    dbs = [out / f"forever-{a.locale}.sqlite"] if a.locale else sorted(out.glob("forever-*.sqlite"))
    dbs = [d for d in dbs if d.is_file()]
    if not dbs:
        raise SystemExit("Aucune base forever-<langue>.sqlite : construis-la d'abord (python3 -m gamedata.build).")
    for db in dbs:
        locale = db.stem.split("-", 1)[1]
        log(f"Base : {db}")
        run(db, out / ".cache", locale, force=a.force, offline=a.offline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
