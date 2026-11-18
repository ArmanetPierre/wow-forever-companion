"""Cartes des zones, tirées des fichiers du client (lecture seule) et mises en cache chez le joueur.

    python3 -m gamedata.maps                 # index des cartes + toutes les cartes de zone
    python3 -m gamedata.maps --zone 1437     # une seule carte

Chaîne du client : UiMap (nom, type) -> UiMapXMapArt -> UiMapArt (style) -> UiMapArtStyleLayer
(taille 1002 x 668, tuiles 256) -> UiMapArtTile (FileDataID des tuiles BLP). Le fond est un
parchemin presque vide : le détail de chaque sous-zone est une superposition « découverte »
(WorldMapOverlay + WorldMapOverlayTile), posée ici comme si toute la zone était explorée. Les
tuiles sont décodées (gamedata/blp.py) puis assemblées en une image RGB.

Cache (jamais dans le dépôt, jamais dans le dossier du jeu) :
    <data>/gamedata/maps/<build>/index.json      uiMapID -> nom, type, parent, tuiles
    <data>/gamedata/maps/<build>/<uiMapID>.rgbz  RGB brut compressé (zlib), largeur x hauteur de l'index
"""
import json
import sys
import time
import zlib
from pathlib import Path

from . import blp

TABLES = ["UiMap", "UiMapXMapArt", "UiMapArt", "UiMapArtStyleLayer", "UiMapArtTile", "UiMapAssignment",
          "WorldMapOverlay", "WorldMapOverlayTile"]
MAP_TYPES = {1: "monde", 2: "continent", 3: "zone", 4: "donjon", 5: "micro", 6: "orpheline"}
BACKGROUND = (24, 20, 16)   # fond sous les pixels transparents des tuiles
INDEX_VERSION = 2   # 2 : zones découvertes (WorldMapOverlay) superposées


def maps_dir(gamedata_dir, build):
    return Path(gamedata_dir) / "maps" / build


def build_index(T):
    """Index des cartes à partir des tables (GameTables). Ne lit aucune texture."""
    uimap = T.get("UiMap")
    xart = T.get("UiMapXMapArt")
    art = T.get("UiMapArt")
    styles = T.get("UiMapArtStyleLayer")
    tiles = T.get("UiMapArtTile")
    def optional(name):
        try:
            return T.get(name)
        except Exception:
            return {}
    assign = optional("UiMapAssignment")
    overlays_by_art = {}
    otiles = {}
    for t in optional("WorldMapOverlayTile").values():
        if t.get("LayerIndex", 0) == 0:
            otiles.setdefault(t["WorldMapOverlayID"], []).append([t["RowIndex"], t["ColIndex"], t["FileDataID"]])
    for o in sorted(optional("WorldMapOverlay").values(), key=lambda r: r["ID"]):
        tl = otiles.get(o["ID"])
        if tl and o.get("UiMapArtID"):
            overlays_by_art.setdefault(o["UiMapArtID"], []).append(
                [o.get("OffsetX", 0), o.get("OffsetY", 0), o.get("TextureWidth", 0), o.get("TextureHeight", 0),
                 sorted(tl)])
    style_layer = {}
    for s in styles.values():
        if s.get("LayerIndex", 0) == 0:
            style_layer[s["UiMapArtStyleID"]] = s
    tiles_by_art = {}
    for t in tiles.values():
        if t.get("LayerIndex", 0) == 0:
            tiles_by_art.setdefault(t["UiMapArtID"], []).append(t)
    art_by_map = {}
    for x in sorted(xart.values(), key=lambda r: (r.get("PhaseID", 0), r["ID"])):
        art_by_map.setdefault(x["UiMapID"], x["UiMapArtID"])   # phase 0 d'abord
    maps = {}
    for mid, m in uimap.items():
        aid = art_by_map.get(mid)
        a = art.get(aid) if aid else None
        layer = style_layer.get(a["UiMapArtStyleID"]) if a else None
        tl = tiles_by_art.get(aid, [])
        if not layer or not tl:
            continue
        maps[str(mid)] = {
            "name": m.get("Name_lang") or "", "type": m.get("Type"), "parent": m.get("ParentUiMapID"),
            "width": layer["LayerWidth"], "height": layer["LayerHeight"],
            "tile_w": layer["TileWidth"], "tile_h": layer["TileHeight"],
            "tiles": sorted([t["RowIndex"], t["ColIndex"], t["FileDataID"]] for t in tl),
            "overlays": overlays_by_art.get(aid, []),
        }
    areas = {}
    for a in sorted(assign.values(), key=lambda r: (r.get("OrderIndex", 0), r["ID"])):
        area, mid = a.get("AreaID"), a.get("UiMapID")
        if area and str(mid) in maps:
            areas.setdefault(str(area), mid)
    return {"version": INDEX_VERSION, "maps": maps, "areas": areas}


def _blit(out, w, h, rgba, src_w, x0, y0, cw, ch, opaque_bg=None):
    """Pose une texture RGBA (cw x ch utiles) en (x0, y0) sur l'image RGB, avec son alpha."""
    if x0 < 0:
        cw, sx = cw + x0, -x0
        x0 = 0
    else:
        sx = 0
    cw, ch = min(cw, w - x0), min(ch, h - y0)
    for y in range(max(0, -y0), ch):
        src = rgba[(y * src_w + sx) * 4:(y * src_w + sx + cw) * 4]
        dst = ((y0 + y) * w + x0) * 3
        alpha = src[3::4]
        if not alpha:
            continue
        line = bytearray(cw * 3)
        line[0::3], line[1::3], line[2::3] = src[0::4], src[1::4], src[2::4]
        if min(alpha) < 255:
            under = out[dst:dst + cw * 3]
            for i, a in enumerate(alpha):
                if a < 255:
                    j = i * 3
                    for c in (j, j + 1, j + 2):
                        line[c] = (line[c] * a + under[c] * (255 - a)) // 255
        out[dst:dst + cw * 3] = line


def compose(entry, read_tile):
    """Assemble fond et zones découvertes. read_tile(fdid) -> octets BLP. Renvoie (w, h, RGB)."""
    w, h, tw, th = entry["width"], entry["height"], entry["tile_w"], entry["tile_h"]
    out = bytearray(bytes(BACKGROUND) * (w * h))

    def tile(fdid):
        try:
            return blp.decode(read_tile(fdid))
        except (OSError, blp.BLPError):
            return None  # tuile manquante : ce qui est dessous reste

    for row, col, fdid in entry["tiles"]:
        got = tile(fdid)
        if got and col * tw < w and row * th < h:
            _blit(out, w, h, got[2], got[0], col * tw, row * th, got[0], got[1])
    for ox, oy, ow, oh, tiles in entry.get("overlays", []):
        for row, col, fdid in tiles:
            got = tile(fdid)
            if not got:
                continue
            tw_, th_, rgba = got
            x0, y0 = ox + col * 256, oy + row * 256
            cw = min(tw_, (ow or tw_) - col * 256)
            ch = min(th_, (oh or th_) - row * 256)
            if cw > 0 and ch > 0 and x0 < w and y0 < h:
                _blit(out, w, h, rgba, tw_, x0, y0, cw, ch)
    return w, h, out


def save_map(mdir, mid, w, h, rgb):
    mdir.mkdir(parents=True, exist_ok=True)
    tmp = mdir / f"{mid}.rgbz.tmp"
    tmp.write_bytes(zlib.compress(bytes(rgb), 6))
    tmp.replace(mdir / f"{mid}.rgbz")


def load_map(mdir, mid, entry):
    p = Path(mdir) / f"{mid}.rgbz"
    if not p.is_file():
        return None
    rgb = zlib.decompress(p.read_bytes())
    if len(rgb) != entry["width"] * entry["height"] * 3:
        return None
    return entry["width"], entry["height"], bytearray(rgb)


# ---------------------------------------------------------------------------
# Accès au client (CascLib), à la demande
# ---------------------------------------------------------------------------

class ClientMaps:
    """Ouvre le stockage du client à la première carte manquante, puis le garde ouvert."""

    def __init__(self, gamedata_dir, wow_root=None, log=None):
        from . import build as B
        self.B = B
        self.gamedata_dir = Path(gamedata_dir)
        self.cache = self.gamedata_dir / ".cache"
        self.wow = Path(wow_root) if wow_root else B.detect_wow()
        if not self.wow or not (self.wow / ".build.info").is_file():
            raise FileNotFoundError("jeu introuvable (dossier avec .build.info)")
        self.build = B.read_build_info(self.wow)
        self.locale = B.detect_locale(self.wow)[0]
        self.mdir = maps_dir(self.gamedata_dir, self.build)
        self.log = log or (lambda m: None)
        self._casc = None
        self._index = None

    def _storage(self):
        if self._casc is None:
            from .casc import CascStorage
            lib = self.B.find_casclib(self.cache)
            if not lib:
                raise FileNotFoundError("CascLib absente : construis d'abord la base locale (python3 -m gamedata.build)")
            self._casc = CascStorage(lib, str(self.wow), self.B.PRODUCT, self.locale)
        return self._casc

    def close(self):
        if self._casc is not None:
            self._casc.close()
            self._casc = None

    def index(self):
        if self._index is not None:
            return self._index
        p = self.mdir / "index.json"
        if p.is_file():
            try:
                idx = json.loads(p.read_text(encoding="utf-8"))
                if idx.get("version") == INDEX_VERSION:
                    self._index = idx
                    return idx
            except ValueError:
                pass
        from .tables import GameTables
        defs = self.B.ensure_wowdbdefs(self.cache, TABLES)
        dbcache = self.B.flavor_dir(self.wow) / "Cache" / "ADB" / self.locale / "DBCache.bin"
        T = GameTables(self._storage(), defs, self.build, dbcache if dbcache.is_file() else None,
                       self.cache / "raw" / self.build)
        idx = build_index(T)
        idx.update({"build": self.build, "locale": self.locale, "built_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
        self.mdir.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
        self._index = idx
        return idx

    def image(self, mid):
        """(w, h, RGB) de la carte uiMapID, extraite et mise en cache au premier appel."""
        entry = self.index()["maps"].get(str(mid))
        if not entry:
            return None
        got = load_map(self.mdir, mid, entry)
        if got:
            return got
        w, h, rgb = compose(entry, self._storage().read)
        save_map(self.mdir, mid, w, h, rgb)
        return w, h, rgb


def main(argv=None):
    import argparse
    from . import build as B
    ap = argparse.ArgumentParser(description="Extrait les cartes des zones du client WoW Forever (lecture seule).")
    ap.add_argument("--wow", help="dossier du jeu")
    ap.add_argument("--data-dir", help="dossier de données (contient perso/ ; défaut ~/WowForever)")
    ap.add_argument("--zone", type=int, action="append", help="uiMapID (répétable) ; défaut : toutes les zones")
    a = ap.parse_args(argv)
    B.utf8_console()
    root = Path(a.data_dir).expanduser() if a.data_dir else B.default_data_root()
    cm = ClientMaps(root / "gamedata", Path(a.wow).expanduser() if a.wow else None)
    t0 = time.time()
    try:
        idx = cm.index()
        ids = a.zone or [int(k) for k, v in idx["maps"].items() if v["type"] in (3, 4)]
        done = 0
        for mid in ids:
            if cm.image(mid):
                done += 1
        print(f"{len(idx['maps'])} cartes indexées, {done} prêtes en {time.time() - t0:.0f} s · {cm.mdir}")
    finally:
        cm.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
