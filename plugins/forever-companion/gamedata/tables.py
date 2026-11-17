"""Tables du jeu = DB2 du client + correctifs du serveur (DBCache.bin).

    tables = GameTables(casc, defs_dir, build, dbcache_path)
    items = tables.get("ItemSparse")   # {id: {colonne: valeur}}

Les DB2 sont lus dans le stockage CASC local, décodés avec les définitions WoWDBDefs,
puis les correctifs valides remplacent ou ajoutent des enregistrements ; les correctifs
« supprimé » retirent l'enregistrement.
"""
import json
from pathlib import Path

from . import dbcache, wdc5


class GameTables:
    def __init__(self, casc, defs_dir, build, dbcache_path=None, raw_cache_dir=None):
        self.casc = casc
        self.defs_dir = Path(defs_dir)
        self.build = build
        manifest = json.loads((self.defs_dir / "manifest.json").read_text(encoding="utf-8"))
        self.manifest = {e["tableName"]: e for e in manifest}
        self.raw_cache_dir = Path(raw_cache_dir) if raw_cache_dir else None
        self._cache = {}
        self.stats = {}
        self.origins = {}  # {table: {id: 'ajoute' | 'modifie'}} : enregistrements venus des correctifs
        self.hotfix_header = None
        self._hotfixes = {}
        if dbcache_path and Path(dbcache_path).exists():
            self.hotfix_header, self._hotfixes = dbcache.read_dbcache(dbcache_path)

    def _db2_bytes(self, name):
        entry = self.manifest.get(name)
        if not entry or not entry.get("db2FileDataID"):
            raise KeyError(f"table inconnue du manifeste : {name}")
        fdid = entry["db2FileDataID"]
        if self.raw_cache_dir:
            p = self.raw_cache_dir / f"{name}.db2"
            if p.exists():
                return p.read_bytes()
        data = self.casc.read(fdid)
        if self.raw_cache_dir:
            self.raw_cache_dir.mkdir(parents=True, exist_ok=True)
            (self.raw_cache_dir / f"{name}.db2").write_bytes(data)
        return data

    def get(self, name):
        if name in self._cache:
            return self._cache[name]
        dbd = self.defs_dir / "definitions" / f"{name}.dbd"
        data = self._db2_bytes(name)
        rows, info = wdc5.read_table(data, dbd, self.build)
        _, blocks = wdc5.parse_dbd(dbd)
        block = wdc5.pick_block(blocks, wdc5.layout_hash_of(data), self.build)
        base = len(rows)
        added = replaced = removed = bad = 0
        origin = {}
        thash = self.manifest[name].get("tableHash")
        fixes = self._hotfixes.get(int(thash, 16), {}) if thash else {}
        for rid, (status, body) in fixes.items():
            if status == dbcache.STATUS_VALID:
                try:
                    row, used = wdc5.decode_hotfix_record(block, body, rid)
                except Exception:
                    bad += 1
                    continue
                if used != len(body):
                    bad += 1
                    continue
                if rid in rows:
                    replaced += 1
                    origin[rid] = "modifie"
                else:
                    added += 1
                    origin[rid] = "ajoute"
                rows[rid] = row
            elif status == dbcache.STATUS_DELETED and rid in rows:
                del rows[rid]
                removed += 1
        self.stats[name] = {"client": base, "added": added, "replaced": replaced,
                            "removed": removed, "undecodable": bad, "total": len(rows)}
        self.origins[name] = origin
        self._cache[name] = rows
        return rows
