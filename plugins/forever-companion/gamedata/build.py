"""Construit la base locale du jeu WoW Forever (SQLite), chez chaque joueur.

    python3 tools/gamedata/build_db.py [--wow DOSSIER] [--data-dir DOSSIER] [--locale enUS] [--force]

Langue : par défaut celle du client (textLocale de _forever_/WTF/Config.wtf, sinon les tags de
.build.info, sinon enUS). La base s'appelle forever-<locale>.sqlite ; les noms d'objets, de quêtes
et de zones y sont dans cette langue. --locale force une autre langue installée.

Étapes (rien n'est jamais écrit dans le dossier du jeu) :
1. trouve le jeu et sa version (.build.info) ;
2. prépare CascLib (téléchargée depuis GitHub et compilée une fois dans <data>/gamedata/.cache/) ;
3. récupère les définitions WoWDBDefs (manifeste + fichiers .dbd utiles) ;
4. lit les tables DB2 du client, applique les correctifs du serveur (DBCache.bin) ;
5. calcule stats, armure et dégâts des objets, relie recettes, donjons, quêtes ;
6. écrit <data>/gamedata/forever-<locale>.sqlite (schéma : docs/schema-gamedb.md) ;
7. ajoute les quêtes, PNJ et positions de QuestieDB, téléchargés depuis GitHub à une révision fixée
   (gamedata/questie.py, jamais redistribués ici) ; --no-questie pour s'en passer.

Idempotent : si la version du jeu, les correctifs et le schéma n'ont pas changé, la base
n'est pas reconstruite (--force pour la refaire).
"""
import argparse
import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import time
import unicodedata
import re
import urllib.request
from pathlib import Path

from . import stats as S
from .casc import CascStorage
from .tables import GameTables
from .wdb import read_quest_cache

SCHEMA_VERSION = 2
CASCLIB_REPO = "https://github.com/ladislav-zezula/CascLib"
WOWDBDEFS_RAW = "https://raw.githubusercontent.com/wowdev/WoWDBDefs/master"
PRODUCT = "wowf"

TABLES = [
    "ItemSparse", "Item", "RandPropPoints", "ItemDamageRanged", "ItemDamageOneHand", "ItemDamageTwoHand",
    "ItemDamageThrown", "ItemDamageWand", "ItemArmorTotal", "ItemArmorQuality", "ArmorLocation",
    "ItemArmorShield", "ItemSet", "SkillLine", "SkillLineAbility", "SpellEffect", "SpellReagents",
    "SpellName", "SpellLevels", "AreaTable", "Map", "DungeonEncounter", "QuestV2", "ChrClasses",
    "JournalInstance", "JournalEncounter", "JournalEncounterItem",
]
OPTIONAL_TABLES = {"JournalInstance", "JournalEncounter", "JournalEncounterItem", "ChrClasses", "ItemSet"}

PROFESSION_CATEGORIES = (9, 11)   # SkillLine.CategoryID : secondaires, métiers
EFFECT_CREATE_ITEM = 24

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE items (
  id INTEGER PRIMARY KEY, name TEXT, name_norm TEXT, quality INTEGER, ilvl INTEGER, req_level INTEGER,
  class_id INTEGER, subclass_id INTEGER, kind TEXT, inventory_type INTEGER, slot TEXT, slot_fr TEXT,
  armor INTEGER, dmg_min INTEGER, dmg_max INTEGER, speed REAL, dps REAL,
  str INTEGER, agi INTEGER, sta INTEGER, int INTEGER, spi INTEGER, ap INTEGER, rap INTEGER,
  spell_power INTEGER, stats_json TEXT, allowable_class INTEGER, bonding INTEGER,
  sell_price INTEGER, buy_price INTEGER, item_set INTEGER, start_quest INTEGER,
  required_skill INTEGER, required_skill_rank INTEGER, max_stack INTEGER, origin TEXT
);
CREATE TABLE item_sources (item_id INTEGER, source_type TEXT, source_id INTEGER, source_name TEXT, detail TEXT);
CREATE TABLE spells (id INTEGER PRIMARY KEY, name TEXT, spell_level INTEGER, origin TEXT);
CREATE TABLE professions (id INTEGER PRIMARY KEY, name TEXT, name_norm TEXT, category INTEGER);
CREATE TABLE recipes (
  spell_id INTEGER, profession_id INTEGER, name TEXT, name_norm TEXT, min_rank INTEGER,
  yellow INTEGER, green INTEGER, grey INTEGER, skill_ups INTEGER, acquire_method INTEGER,
  item_id INTEGER, item_count INTEGER, reagents_json TEXT, origin TEXT, rank_est INTEGER, rank_source TEXT,
  PRIMARY KEY (spell_id, profession_id)
);
CREATE TABLE zones (id INTEGER PRIMARY KEY, name TEXT, name_norm TEXT, parent_id INTEGER, continent_id INTEGER);
CREATE TABLE dungeons (map_id INTEGER PRIMARY KEY, name TEXT, name_norm TEXT, instance_type INTEGER,
                       max_players INTEGER, origin TEXT);
CREATE TABLE encounters (id INTEGER PRIMARY KEY, map_id INTEGER, name TEXT, order_index INTEGER, origin TEXT);
CREATE TABLE dungeon_loot (map_id INTEGER, encounter_id INTEGER, item_id INTEGER, source TEXT);
CREATE TABLE quests (id INTEGER PRIMARY KEY, title TEXT, title_norm TEXT, objectives TEXT, origin TEXT);
CREATE INDEX items_name ON items(name_norm);
CREATE INDEX items_slot ON items(inventory_type, req_level);
CREATE INDEX items_class ON items(class_id, subclass_id);
CREATE INDEX item_sources_item ON item_sources(item_id);
CREATE INDEX recipes_prof ON recipes(profession_id, rank_est);
CREATE INDEX recipes_item ON recipes(item_id);
CREATE INDEX encounters_map ON encounters(map_id);
CREATE INDEX loot_map ON dungeon_loot(map_id);
CREATE INDEX loot_item ON dungeon_loot(item_id);
CREATE INDEX quests_title ON quests(title_norm);
"""

SLOT_KEYS = {1: ("HeadSlot", "Tête"), 2: ("NeckSlot", "Cou"), 3: ("ShoulderSlot", "Épaules"),
             4: ("ShirtSlot", "Chemise"), 5: ("ChestSlot", "Torse"), 6: ("WaistSlot", "Taille"),
             7: ("LegsSlot", "Jambes"), 8: ("FeetSlot", "Pieds"), 9: ("WristSlot", "Poignets"),
             10: ("HandsSlot", "Mains"), 11: ("FingerSlot", "Doigt"), 12: ("TrinketSlot", "Bijou"),
             13: ("OneHand", "Une main"), 14: ("SecondaryHandSlot", "Bouclier"), 15: ("RangedSlot", "Distance"),
             16: ("BackSlot", "Dos"), 17: ("TwoHand", "Deux mains"), 19: ("TabardSlot", "Tabard"),
             20: ("ChestSlot", "Torse"), 21: ("MainHandSlot", "Main droite"), 22: ("SecondaryHandSlot", "Main gauche"),
             23: ("SecondaryHandSlot", "Tenu en main gauche"), 25: ("RangedSlot", "Armes de jet"),
             26: ("RangedSlot", "Distance"), 28: ("RangedSlot", "Relique")}


def norm(text):
    s = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Emplacements
# ---------------------------------------------------------------------------

def default_data_root():
    env = os.environ.get("FOREVER_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve().parent
    if (Path.cwd() / "perso").is_dir():
        return Path.cwd().resolve()
    return Path.home() / "WowForever"


def detect_wow():
    home = Path.home()
    cands = [Path("/Applications/World of Warcraft"), home / "Applications" / "World of Warcraft",
             Path("C:/Program Files (x86)/World of Warcraft"), Path("C:/Program Files/World of Warcraft"),
             home / "Games" / "world-of-warcraft" / "drive_c" / "Program Files (x86)" / "World of Warcraft",
             home / ".wine" / "drive_c" / "Program Files (x86)" / "World of Warcraft"]
    for c in cands:
        if (c / ".build.info").is_file() and (c / "Data").is_dir():
            return c
    return None


def read_build_info(wow_root, product=PRODUCT):
    lines = (Path(wow_root) / ".build.info").read_text(encoding="utf-8", errors="replace").splitlines()
    head = [h.split("!")[0] for h in lines[0].split("|")]
    for ln in lines[1:]:
        row = dict(zip(head, ln.split("|")))
        if row.get("Product") == product and row.get("Version"):
            return row["Version"]
    raise SystemExit(f"Version de {product} introuvable dans {wow_root}/.build.info")


def flavor_dir(wow_root):
    return Path(wow_root) / "_forever_"


LOCALE_RE = re.compile(r"^[a-z]{2}[A-Z]{2}$")


def detect_locale(wow_root, product=PRODUCT):
    """Langue du client : textLocale de WTF/Config.wtf, sinon tag « xxXX text? » de .build.info, sinon enUS.

    Renvoie (locale, origine). Lecture seule.
    """
    cfg = flavor_dir(wow_root) / "WTF" / "Config.wtf"
    if cfg.is_file():
        for ln in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r'\s*SET\s+textLocale\s+"?([A-Za-z]{4})"?', ln)
            if m and LOCALE_RE.match(m.group(1)):
                return m.group(1), "Config.wtf"
    info = Path(wow_root) / ".build.info"
    if info.is_file():
        lines = info.read_text(encoding="utf-8", errors="replace").splitlines()
        head = [h.split("!")[0] for h in lines[0].split("|")] if lines else []
        for ln in lines[1:]:
            row = dict(zip(head, ln.split("|")))
            if row.get("Product") != product:
                continue
            m = re.search(r"\b([a-z]{2}[A-Z]{2}) text\?", row.get("Tags", ""))
            if m:
                return m.group(1), ".build.info"
    return "enUS", "défaut"


# ---------------------------------------------------------------------------
# Dépendances : CascLib et WoWDBDefs
# ---------------------------------------------------------------------------

LIB_NAMES = ("casc.framework/casc", "libcasc.dylib", "libcasc.so", "libcasc.so.1", "casc.dll", "CascLib.dll")


def find_casclib(cache):
    root = cache / "casclib"
    for name in LIB_NAMES:
        p = root / name
        if p.is_file():
            return p
    return None


def ensure_casclib(cache):
    lib = find_casclib(cache)
    if lib:
        return lib
    if platform.system() == "Windows":
        raise SystemExit(
            "CascLib n'est pas encore préparée. Sous Windows : installe CMake et Visual Studio Build Tools, puis\n"
            f"  git clone --depth 1 {CASCLIB_REPO} \"{cache / 'casclib' / 'src'}\"\n"
            f"  cmake -S \"{cache / 'casclib' / 'src'}\" -B \"{cache / 'casclib' / 'build'}\" -DCASC_BUILD_SHARED_LIB=ON -DCMAKE_POLICY_VERSION_MINIMUM=3.5\n"
            f"  cmake --build \"{cache / 'casclib' / 'build'}\" --config Release\n"
            f"et copie casc.dll dans \"{cache / 'casclib'}\". Relance ensuite cette commande.")
    for tool in ("git", "cmake"):
        if not shutil.which(tool):
            raise SystemExit(f"« {tool} » est nécessaire pour préparer CascLib (une seule fois). "
                             "macOS : xcode-select --install puis brew install cmake ; Linux : apt install git cmake build-essential.")
    src = cache / "casclib" / "src"
    build = cache / "casclib" / "build"
    if not (src / "CMakeLists.txt").is_file():
        log(f"• Téléchargement de CascLib ({CASCLIB_REPO})…")
        src.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", CASCLIB_REPO, str(src)], check=True)
    log("• Compilation de CascLib…")
    subprocess.run(["cmake", "-S", str(src), "-B", str(build), "-DCASC_BUILD_SHARED_LIB=ON",
                    "-DCASC_BUILD_STATIC_LIB=OFF", "-DCMAKE_BUILD_TYPE=Release",
                    "-DCMAKE_POLICY_VERSION_MINIMUM=3.5"], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run(["cmake", "--build", str(build), "--config", "Release", "-j", "4"], check=True,
                   stdout=subprocess.DEVNULL)
    for name in LIB_NAMES:
        hits = sorted(build.rglob(Path(name).name))
        for h in hits:
            if name.startswith("casc.framework") and h.parent.name != "casc.framework":
                continue
            if h.is_file():
                if name.startswith("casc.framework"):
                    shutil.copytree(h.parent, cache / "casclib" / "casc.framework", dirs_exist_ok=True, symlinks=True)
                else:
                    shutil.copy2(h, cache / "casclib" / Path(name).name)
                return find_casclib(cache)
    raise SystemExit("Compilation de CascLib terminée mais bibliothèque introuvable.")


def _download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "forever-companion-gamedata"})
    with urllib.request.urlopen(req, timeout=60) as r:
        dest.write_bytes(r.read())


def ensure_wowdbdefs(cache, tables):
    defs = cache / "wowdbdefs"
    if not (defs / "manifest.json").is_file():
        log("• Téléchargement du manifeste WoWDBDefs…")
        _download(f"{WOWDBDEFS_RAW}/manifest.json", defs / "manifest.json")
        (defs / "REVISION").write_text("master " + time.strftime("%Y-%m-%d") + "\n")
    for t in tables:
        p = defs / "definitions" / f"{t}.dbd"
        if not p.is_file():
            log(f"• Téléchargement de la définition {t}.dbd…")
            _download(f"{WOWDBDEFS_RAW}/definitions/{t}.dbd", p)
    return defs


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def fingerprint(build, dbcache, questcache, defs):
    parts = [f"schema={SCHEMA_VERSION}", f"build={build}"]
    for p in (dbcache, questcache):
        if p and p.is_file():
            st = p.stat()
            parts.append(f"{p.name}={st.st_size}:{int(st.st_mtime)}")
    rev = defs / "REVISION"
    if rev.is_file():
        parts.append("defs=" + rev.read_text().strip())
    return ";".join(parts)


def current_fingerprint(db_path):
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        row = con.execute("SELECT value FROM meta WHERE key='fingerprint'").fetchone()
        con.close()
        return row[0] if row else None
    except sqlite3.Error:
        return None


def item_rows(T):
    sparse, items, rp = T.get("ItemSparse"), T.get("Item"), T.get("RandPropPoints")
    dmg = {n: T.get(n) for n in ("ItemDamageRanged", "ItemDamageOneHand", "ItemDamageTwoHand",
                                 "ItemDamageThrown", "ItemDamageWand")}
    arm = {n: T.get(n) for n in ("ItemArmorTotal", "ItemArmorQuality", "ArmorLocation", "ItemArmorShield")}
    origin = dict(T.origins.get("Item", {}))
    origin.update(T.origins.get("ItemSparse", {}))
    for iid, s in sparse.items():
        it = items.get(iid) or {}
        st = S.item_stats(s, rp.get(s.get("ItemLevel")))
        wd = S.weapon_damage(s, it, dmg)
        armor = S.armor_value(s, it, arm)
        inv = s.get("InventoryType", 0)
        cid, sub = it.get("ClassID"), it.get("SubclassID")
        if cid == 2:
            kind = S.WEAPON_SUBCLASS_NAMES.get(sub, "Arme")
        elif cid == 4:
            kind = "Cape" if inv == 16 else S.ARMOR_SUBCLASS_NAMES.get(sub, "Armure")
        else:
            kind = None
        slot, slot_fr = SLOT_KEYS.get(inv, (None, None))
        named = {S.STAT_NAMES.get(t, (str(t),))[0]: v for t, v in st.items()}
        yield (iid, s.get("Display_lang"), norm(s.get("Display_lang")), s.get("OverallQualityID"),
               s.get("ItemLevel"), s.get("RequiredLevel"), cid, sub, kind, inv, slot, slot_fr, armor,
               wd[0] if wd else None, wd[1] if wd else None, wd[2] if wd else None, wd[3] if wd else None,
               named.get("str"), named.get("agi"), named.get("sta"), named.get("int"), named.get("spi"),
               named.get("ap"), named.get("rap"), named.get("spell_power"),
               json.dumps(named, ensure_ascii=False) if named else None,
               s.get("AllowableClass"), s.get("Bonding"), s.get("SellPrice"), s.get("BuyPrice"),
               s.get("ItemSet") or None, s.get("StartQuestID") or None, s.get("RequiredSkill") or None,
               s.get("RequiredSkillRank") or None, s.get("Stackable"), origin.get(iid, "client"))


def build_database(T, db_path, quests_cache, meta):
    tmp = db_path.with_suffix(".sqlite.tmp")
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(tmp)
    con.executescript(SCHEMA)
    counts = {}

    rows = list(item_rows(T))
    con.executemany(f"INSERT INTO items VALUES ({','.join('?' * 36)})", rows)
    counts["items"] = len(rows)
    item_names = {r[0]: r[1] for r in rows}
    item_ilvl = {r[0]: r[4] for r in rows}

    # sorts
    names = T.get("SpellName")
    levels = {}
    for r in T.get("SpellLevels").values():
        if not r.get("DifficultyID"):
            levels[r.get("SpellID")] = r.get("SpellLevel") or r.get("BaseLevel")
    sp_origin = T.origins.get("SpellName", {})
    con.executemany("INSERT INTO spells VALUES (?,?,?,?)",
                    [(sid, r.get("Name_lang"), levels.get(sid), sp_origin.get(sid, "client")) for sid, r in names.items()])
    counts["spells"] = len(names)

    # métiers et recettes
    skill = T.get("SkillLine")
    profs = {sid: r for sid, r in skill.items() if r.get("CategoryID") in PROFESSION_CATEGORIES}
    con.executemany("INSERT INTO professions VALUES (?,?,?,?)",
                    [(sid, r.get("DisplayName_lang"), norm(r.get("DisplayName_lang")), r.get("CategoryID"))
                     for sid, r in profs.items()])
    creates = {}
    for e in T.get("SpellEffect").values():
        if e.get("Effect") == EFFECT_CREATE_ITEM and e.get("EffectItemType") and not e.get("DifficultyID"):
            creates.setdefault(e["SpellID"], (e["EffectItemType"], max(1, int(round(e.get("EffectBasePointsF") or 1)))))
    reagents = {}
    for r in T.get("SpellReagents").values():
        reagents[r.get("SpellID")] = [{"item_id": i, "count": c, "name": item_names.get(i)}
                                      for i, c in zip(r.get("Reagent") or [], r.get("ReagentCount") or []) if i]
    sla_origin = T.origins.get("SkillLineAbility", {})
    rec_rows, src_rows = {}, []
    for aid, a in T.get("SkillLineAbility").items():
        pid, sid = a.get("SkillLine"), a.get("Spell")
        if pid not in profs or not sid:
            continue
        low, high = a.get("TrivialSkillLineRankLow") or 0, a.get("TrivialSkillLineRankHigh") or 0
        green = (low + high) // 2 if low and high else None
        made = creates.get(sid)
        name = (names.get(sid) or {}).get("Name_lang")
        # Le rang requis n'est pas dans les fichiers du client Forever (1 partout, sauf exceptions) :
        # repli sur ≈ 5 × niveau de l'objet fabriqué (vérifié sur des recettes Classic connues).
        if (a.get("MinSkillLineRank") or 0) > 1:
            rank_est, rank_src = a["MinSkillLineRank"], "client"
        elif made and item_ilvl.get(made[0]):
            rank_est, rank_src = max(1, 5 * item_ilvl[made[0]]), "estimation"
        else:
            rank_est, rank_src = None, None
        rec_rows[(sid, pid)] = (sid, pid, name, norm(name), a.get("MinSkillLineRank"), low or None, green, high or None,
                                a.get("NumSkillUps"), a.get("AcquireMethod"), made[0] if made else None,
                                made[1] if made else None,
                                json.dumps(reagents.get(sid, []), ensure_ascii=False),
                                sla_origin.get(aid) or sp_origin.get(sid, "client"), rank_est, rank_src)
        if made:
            src_rows.append((made[0], "artisanat", sid, profs[pid].get("DisplayName_lang"),
                             f"{name} (compétence {a.get('MinSkillLineRank')})"))  # traduit à l'affichage
    con.executemany(f"INSERT OR REPLACE INTO recipes VALUES ({','.join('?' * 16)})", list(rec_rows.values()))
    con.executemany("INSERT INTO item_sources VALUES (?,?,?,?,?)", src_rows)
    counts["professions"], counts["recipes"] = len(profs), len(rec_rows)

    # zones
    areas = T.get("AreaTable")
    con.executemany("INSERT INTO zones VALUES (?,?,?,?,?)",
                    [(aid, r.get("AreaName_lang"), norm(r.get("AreaName_lang")), r.get("ParentAreaID"),
                      r.get("ContinentID")) for aid, r in areas.items()])
    counts["zones"] = len(areas)

    # donjons, rencontres, butin
    maps = T.get("Map")
    map_origin = T.origins.get("Map", {})
    dun = [(mid, r.get("MapName_lang"), norm(r.get("MapName_lang")), r.get("InstanceType"), r.get("MaxPlayers"),
            map_origin.get(mid, "client")) for mid, r in maps.items() if r.get("InstanceType") in (1, 2)]
    con.executemany("INSERT INTO dungeons VALUES (?,?,?,?,?,?)", dun)
    de_origin = T.origins.get("DungeonEncounter", {})
    enc = [(eid, r.get("MapID"), r.get("Name_lang"), r.get("OrderIndex"), de_origin.get(eid, "client"))
           for eid, r in T.get("DungeonEncounter").items()]
    con.executemany("INSERT INTO encounters VALUES (?,?,?,?,?)", enc)
    loot = []
    try:
        ji, je, jei = T.get("JournalInstance"), T.get("JournalEncounter"), T.get("JournalEncounterItem")
        for r in jei.values():
            e = je.get(r.get("JournalEncounterID")) or {}
            inst = ji.get(e.get("JournalInstanceID")) or {}
            loot.append((inst.get("MapID"), e.get("DungeonEncounterID"), r.get("ItemID"), "journal"))
    except Exception:
        pass
    con.executemany("INSERT INTO dungeon_loot VALUES (?,?,?,?)", loot)
    src_rows = []
    enc_names = {e[0]: e[2] for e in enc}
    dun_names = {d[0]: d[1] for d in dun}
    for mid, eid, iid, _ in loot:
        src_rows.append((iid, "donjon", mid, dun_names.get(mid), enc_names.get(eid)))
    con.executemany("INSERT INTO item_sources VALUES (?,?,?,?,?)", src_rows)
    counts["dungeons"], counts["encounters"], counts["dungeon_loot"] = len(dun), len(enc), len(loot)

    # quêtes : ids du client + titres du cache des quêtes déjà vues
    q_origin = T.origins.get("QuestV2", {})
    qrows = {}
    for qid in T.get("QuestV2"):
        qrows[qid] = [qid, None, None, None, q_origin.get(qid, "client")]
    for qid, (title, obj, _desc) in quests_cache.items():
        row = qrows.setdefault(qid, [qid, None, None, None, "cache"])
        row[1], row[2], row[3] = title, norm(title), obj
    con.executemany("INSERT INTO quests VALUES (?,?,?,?,?)", [tuple(r) for r in qrows.values()])
    counts["quests"], counts["quest_titles"] = len(qrows), len(quests_cache)

    meta = dict(meta)
    meta["counts"] = json.dumps(counts)
    meta["hotfixes"] = json.dumps(T.stats)
    con.executemany("INSERT INTO meta VALUES (?,?)", [(k, str(v)) for k, v in meta.items()])
    con.commit()
    con.execute("VACUUM")
    con.close()
    os.replace(tmp, db_path)
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Construit la base locale du jeu WoW Forever (SQLite).")
    ap.add_argument("--wow", help="dossier du jeu (celui qui contient Data/ et _forever_/)")
    ap.add_argument("--data-dir", help="dossier de données (contient perso/ ; défaut ~/WowForever)")
    ap.add_argument("--locale", help="langue du client, ex. frFR, enUS, deDE (défaut : celle du client installé)")
    ap.add_argument("--force", action="store_true", help="reconstruit même si la base est à jour")
    ap.add_argument("--no-questie", action="store_true",
                    help="n'ajoute pas les quêtes et PNJ de QuestieDB (téléchargés depuis GitHub)")
    a = ap.parse_args(argv)
    t0 = time.time()

    wow = Path(a.wow).expanduser() if a.wow else detect_wow()
    if wow and wow.name == "_forever_":
        wow = wow.parent
    if not wow or not (wow / ".build.info").is_file():
        raise SystemExit("Jeu introuvable : indique son dossier avec --wow \"/chemin/World of Warcraft\".")
    build = read_build_info(wow)
    flav = flavor_dir(wow)
    if a.locale:
        if not LOCALE_RE.match(a.locale):
            raise SystemExit(f"--locale attend un code comme frFR ou enUS (reçu : {a.locale}).")
        locale, locale_src = a.locale, "--locale"
    else:
        locale, locale_src = detect_locale(wow)
    root = Path(a.data_dir).expanduser() if a.data_dir else default_data_root()
    out_dir = root / "gamedata"
    cache = out_dir / ".cache"
    db_path = out_dir / f"forever-{locale}.sqlite"
    dbcache = flav / "Cache" / "ADB" / locale / "DBCache.bin"
    questcache = flav / "Cache" / "WDB" / locale / "questcache.wdb"
    log(f"WoW Forever {build} · {wow}")
    log(f"Langue : {locale} ({locale_src})")
    log(f"Base : {db_path}")

    lib = ensure_casclib(cache)
    defs = ensure_wowdbdefs(cache, TABLES)
    fp = fingerprint(build, dbcache, questcache, defs)
    if not a.force and db_path.is_file() and current_fingerprint(db_path) == fp:
        log("Base déjà à jour (même version du jeu et mêmes correctifs). --force pour la reconstruire.")
        return _questie_step(a, db_path, cache, locale)
    out_dir.mkdir(parents=True, exist_ok=True)

    with CascStorage(lib, str(wow), PRODUCT, locale) as casc:
        T = GameTables(casc, defs, build, dbcache if dbcache.is_file() else None, cache / "raw" / build)
        if T.hotfix_header:
            log(f"• Correctifs : {T.hotfix_header['entries']} entrées (DBCache.bin, build {T.hotfix_header['build']})")
        else:
            log("• Pas de DBCache.bin : base construite sans les correctifs de Forever (lance le jeu une fois).")
        for t in TABLES:
            try:
                T.get(t)
            except Exception as exc:
                if t in OPTIONAL_TABLES:
                    T._cache[t] = {}
                    log(f"  (table {t} indisponible : {exc})")
                else:
                    raise
        quests = read_quest_cache(questcache) if questcache.is_file() else {}
        meta = {"schema_version": SCHEMA_VERSION, "fingerprint": fp, "build": build, "locale": locale,
                "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "dbcache_build": (T.hotfix_header or {}).get("build"),
                "dbcache_entries": (T.hotfix_header or {}).get("entries"),
                "note_loot": "Le Journal des donjons n'est pas dans les fichiers du client Forever : "
                             "dungeon_loot ne se remplit qu'avec un export en jeu."}
        counts = build_database(T, db_path, quests, meta)

    size = db_path.stat().st_size / 1e6
    hf = T.stats.get("ItemSparse", {})
    log(f"✓ Base écrite en {time.time() - t0:.0f} s ({size:.1f} Mo)")
    log(f"  objets {counts['items']} (dont {hf.get('added', 0)} ajoutés et {hf.get('replaced', 0)} modifiés par Forever)")
    log(f"  recettes {counts['recipes']} · métiers {counts['professions']} · sorts {counts['spells']}")
    log(f"  donjons {counts['dungeons']} · boss {counts['encounters']} · butin de donjon {counts['dungeon_loot']}")
    log(f"  zones {counts['zones']} · quêtes {counts['quests']} (titres connus : {counts['quest_titles']})")
    return _questie_step(a, db_path, cache, locale, force=True)


def _questie_step(a, db_path, cache, locale, force=False):
    """Quêtes, PNJ et positions de QuestieDB (téléchargés chez le joueur) : voir gamedata/questie.py."""
    if a.no_questie:
        log("• QuestieDB ignoré (--no-questie) : get_quest_info, find_quests et find_npc seront limités.")
        return 0
    from . import questie
    try:
        questie.run(db_path, cache, locale, force=force or a.force)
    except Exception as exc:  # la base du client reste utilisable sans QuestieDB
        log(f"• QuestieDB non importé ({exc}). Relance plus tard : python3 -m gamedata.questie")
    return 0


if __name__ == "__main__":
    sys.exit(main())
