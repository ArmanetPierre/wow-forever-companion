"""Carte d'une zone avec repères numérotés, en PNG (outil `map`).

Les cartes viennent du client du joueur (gamedata/maps.py, lecture seule) et sont mises en cache
dans <data>/gamedata/maps/. L'image rendue est écrite dans <data>/gamedata/cartes/ et renvoyée
au client MCP (contenu image). Python standard uniquement : PNG écrit à la main, repères et
chiffres dessinés pixel par pixel.

Coordonnées : celles de /way, en pourcentage de la carte (0-100), origine en haut à gauche.
"""
from __future__ import annotations

import hashlib
import re
import struct
import sys
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import formats as F
import gamedb as GDB
from i18n import T

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MAX_POINTS = 9
KEEP_RENDERS = 40

# Noms anglais des cartes Classic (uiMapID) : un client français n'a que les noms français.
EN_NAMES = {
    1411: "Durotar", 1412: "Mulgore", 1413: "The Barrens", 1414: "Kalimdor", 1415: "Eastern Kingdoms",
    1416: "Alterac Mountains", 1417: "Arathi Highlands", 1418: "Badlands", 1419: "Blasted Lands",
    1420: "Tirisfal Glades", 1421: "Silverpine Forest", 1422: "Western Plaguelands",
    1423: "Eastern Plaguelands", 1424: "Hillsbrad Foothills", 1425: "The Hinterlands", 1426: "Dun Morogh",
    1427: "Searing Gorge", 1428: "Burning Steppes", 1429: "Elwynn Forest", 1430: "Deadwind Pass",
    1431: "Duskwood", 1432: "Loch Modan", 1433: "Redridge Mountains", 1434: "Stranglethorn Vale",
    1435: "Swamp of Sorrows", 1436: "Westfall", 1437: "Wetlands", 1438: "Teldrassil", 1439: "Darkshore",
    1440: "Ashenvale", 1441: "Thousand Needles", 1442: "Stonetalon Mountains", 1443: "Desolace",
    1444: "Feralas", 1445: "Dustwallow Marsh", 1446: "Tanaris", 1447: "Azshara", 1448: "Felwood",
    1449: "Un'Goro Crater", 1450: "Moonglade", 1451: "Silithus", 1452: "Winterspring",
    1453: "Stormwind City", 1454: "Orgrimmar", 1455: "Ironforge", 1456: "Thunder Bluff",
    1457: "Darnassus", 1458: "Undercity", 1459: "Alterac Valley", 1460: "Warsong Gulch",
    1461: "Arathi Basin", 947: "Azeroth",
}
EXTRA_ALIASES = {"stormwind": 1453, "hurlevent": 1453, "barrens": 1413, "tarides": 1413,
                 "stv": 1434, "strangleronce": 1434, "pitons du tonnerre": 1456, "les pitons du tonnerre": 1456}

# ---------------------------------------------------------------------------
# Image : PNG, recadrage, agrandissement, repères
# ---------------------------------------------------------------------------


def png_bytes(w: int, h: int, rgb: bytes) -> bytes:
    """RGB 8 bits -> PNG (filtre « Sub » par ligne : bien plus compact qu'aucun filtre sur une carte)."""
    stride = w * 3
    raw = bytearray()
    for y in range(h):
        line = rgb[y * stride:(y + 1) * stride]
        raw.append(1)
        prev = bytes(3) + bytes(line[:-3])
        raw += bytes((a - b) & 255 for a, b in zip(line, prev))
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b""))


def crop(w: int, h: int, rgb: bytes, x0: int, y0: int, cw: int, ch: int) -> bytearray:
    out = bytearray(cw * ch * 3)
    for y in range(ch):
        s = ((y0 + y) * w + x0) * 3
        out[y * cw * 3:(y + 1) * cw * 3] = rgb[s:s + cw * 3]
    return out


def upscale(w: int, h: int, rgb: bytes, k: int) -> bytearray:
    """Agrandissement entier au plus proche voisin."""
    if k <= 1:
        return bytearray(rgb)
    out = bytearray()
    for y in range(h):
        line = rgb[y * w * 3:(y + 1) * w * 3]
        big = bytearray()
        for x in range(w):
            big += line[x * 3:x * 3 + 3] * k
        out += bytes(big) * k
    return out


DIGITS = {  # police 3 x 5
    "0": ("111", "101", "101", "101", "111"), "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"), "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"), "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"), "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"), "9": ("111", "101", "111", "001", "111"),
}
RED = (214, 38, 38)
BLUE = (36, 110, 230)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def _put(rgb: bytearray, w: int, h: int, x: int, y: int, color: Tuple[int, int, int]) -> None:
    if 0 <= x < w and 0 <= y < h:
        o = (y * w + x) * 3
        rgb[o:o + 3] = bytes(color)


def draw_marker(rgb: bytearray, w: int, h: int, cx: int, cy: int, label: str = "",
                color: Tuple[int, int, int] = RED, radius: int = 10) -> None:
    """Disque coloré cerclé de blanc puis de noir, chiffre blanc au centre."""
    r_out, r_white = radius + 2, radius
    for dy in range(-r_out, r_out + 1):
        for dx in range(-r_out, r_out + 1):
            d2 = dx * dx + dy * dy
            if d2 > r_out * r_out:
                continue
            c = BLACK if d2 > r_white * r_white else WHITE if d2 > (radius - 2) ** 2 else color
            _put(rgb, w, h, cx + dx, cy + dy, c)
    text = label[:2]
    if not text:
        return
    s = 2 if len(text) == 1 else 1
    gw = 3 * s * len(text) + s * (len(text) - 1)
    x0, y0 = cx - gw // 2, cy - (5 * s) // 2
    for i, ch in enumerate(text):
        glyph = DIGITS.get(ch)
        if not glyph:
            continue
        gx = x0 + i * 4 * s
        for row, bits in enumerate(glyph):
            for col, b in enumerate(bits):
                if b == "1":
                    for yy in range(s):
                        for xx in range(s):
                            _put(rgb, w, h, gx + col * s + xx, y0 + row * s + yy, WHITE)


def frame(w: int, h: int, pts: List[Tuple[float, float]], mode: str = "auto") -> Tuple[int, int, int, int, int]:
    """(x0, y0, largeur, hauteur, agrandissement) de la zone à montrer."""
    if mode == "zone" or not pts:
        return 0, 0, w, h, 1
    xs = [p[0] * w / 100 for p in pts]
    ys = [p[1] * h / 100 for p in pts]
    pad = 90
    cw = max(int(max(xs) - min(xs)) + 2 * pad, 440)
    ch = max(int(max(ys) - min(ys)) + 2 * pad, 300)
    # format de la carte (3:2) pour que l'image reste lisible
    if cw / ch > w / h:
        ch = int(cw * h / w)
    else:
        cw = int(ch * w / h)
    if cw >= w * 0.7 or ch >= h * 0.7:
        return 0, 0, w, h, 1
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    x0 = int(min(max(cx - cw / 2, 0), w - cw))
    y0 = int(min(max(cy - ch / 2, 0), h - ch))
    k = 2 if cw <= 560 else 1
    return x0, y0, cw, ch, k


def render(w: int, h: int, rgb: bytes, points: List[Dict[str, Any]], mode: str = "auto",
           player: Optional[Tuple[float, float]] = None) -> Tuple[int, int, bytes]:
    """Image finale : (largeur, hauteur, PNG). points : [{x, y}] en pourcentage, numérotés dans l'ordre."""
    pts = [(float(p["x"]), float(p["y"])) for p in points]
    framed = pts + ([player] if player else [])
    x0, y0, cw, ch, k = frame(w, h, framed, mode)
    img = upscale(cw, ch, crop(w, h, rgb, x0, y0, cw, ch), k)
    W, H = cw * k, ch * k

    def to_px(x: float, y: float) -> Tuple[int, int]:
        return int(round((x * w / 100 - x0) * k)), int(round((y * h / 100 - y0) * k))

    grow = 4 * (k - 1)   # repères un peu plus gros sur une carte agrandie
    if player:
        px, py = to_px(*player)
        draw_marker(img, W, H, px, py, "", BLUE, radius=7 + grow)
    for i, (x, y) in enumerate(pts, 1):
        px, py = to_px(x, y)
        draw_marker(img, W, H, px, py, str(i) if len(pts) > 1 else "", RED, radius=10 + grow)
    return W, H, png_bytes(W, H, img)


# ---------------------------------------------------------------------------
# Points et zones
# ---------------------------------------------------------------------------

WAY_RE = re.compile(r"^\s*/?(?:way|tway)?\s*(?:#(\d+)\s+)?(.*?)\s*(-?\d+(?:[.,]\d+)?)[\s,]+(-?\d+(?:[.,]\d+)?)\s*(.*)$",
                    re.I)


def parse_point(p: Any) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[int]]:
    """Point {x, y, label} ou texte « /way [#id] [zone] x y [libellé] ». Renvoie (point, zone, uiMapID)."""
    if isinstance(p, dict):
        try:
            x, y = float(p.get("x")), float(p.get("y"))
        except (TypeError, ValueError):
            return None, None, None
        label = p.get("label") or p.get("libelle") or p.get("nom") or ""
        return {"x": x, "y": y, "label": str(label)}, None, None
    m = WAY_RE.match(str(p or ""))
    if not m:
        return None, None, None
    mid = int(m.group(1)) if m.group(1) else None
    zone = m.group(2).strip() or None
    x, y = float(m.group(3).replace(",", ".")), float(m.group(4).replace(",", "."))
    return {"x": x, "y": y, "label": m.group(5).strip()}, zone, mid


def resolve_zone(index: Dict[str, Any], zone: Any) -> Optional[int]:
    """uiMapID à partir d'un id, d'un nom (langue du client ou anglais) ou d'un id de zone (AreaTable)."""
    maps = index.get("maps", {})
    if zone is None or zone == "":
        return None
    s = str(zone).strip().lstrip("#")
    if s.isdigit():
        if s in maps:
            return int(s)
        area = index.get("areas", {}).get(s)
        return int(area) if area else None
    key = F.norm_key(s)
    names: Dict[str, int] = {}
    for mid, e in maps.items():
        names.setdefault(F.norm_key(e.get("name")), int(mid))
    for mid, n in EN_NAMES.items():
        if str(mid) in maps:
            names.setdefault(F.norm_key(n), mid)
    for a, mid in EXTRA_ALIASES.items():
        names.setdefault(a, mid)
    if key in names:
        return names[key]
    # sans article (« Les Paluns » / « Paluns », « The Barrens ») puis inclusion
    strip = lambda k: re.sub(r"^(les|le|la|l|the)\s+", "", k)  # noqa: E731
    for n, mid in names.items():
        if strip(n) == strip(key):
            return mid
    hits = sorted({mid for n, mid in names.items() if key and (key in n or strip(n) in key)},
                  key=lambda m: (maps.get(str(m), {}).get("type") != 3, m))
    return hits[0] if hits else None


# ---------------------------------------------------------------------------
# Accès aux cartes : cache seul, ou client
# ---------------------------------------------------------------------------

class CachedMaps:
    """Cartes déjà extraites (sans le jeu) : la version la plus récente du cache."""

    def __init__(self, mdir: Path):
        import json
        self.mdir = mdir
        self._index = json.loads((mdir / "index.json").read_text(encoding="utf-8"))

    def index(self) -> Dict[str, Any]:
        return self._index

    def image(self, mid: int):
        from gamedata import maps as M
        entry = self._index["maps"].get(str(mid))
        return M.load_map(self.mdir, mid, entry) if entry else None


def open_maps(gamedata_dir: Path):
    if str(PLUGIN_ROOT) not in sys.path:
        sys.path.insert(0, str(PLUGIN_ROOT))
    from gamedata import maps as M
    try:
        return M.ClientMaps(gamedata_dir)
    except (FileNotFoundError, OSError, SystemExit):
        root = Path(gamedata_dir) / "maps"
        cached = sorted((p for p in root.glob("*/index.json")), key=lambda p: -p.stat().st_mtime) \
            if root.is_dir() else []
        if cached:
            return CachedMaps(cached[0].parent)
        raise


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", F.norm_key(text)).strip("-") or "carte"


class WorldMapToolsMixin:
    """Mélangé à Tools (server.py) : outil `map`."""

    _maps = None

    def _gamedata_dir(self) -> Path:
        path = GDB.find_db_path(getattr(self.store, "data_dir", None), getattr(self, "_locale", None))
        if path is None:
            raise self.ToolError(GDB.missing_message())
        return path.parent

    def _map_source(self):
        if self._maps is None:
            try:
                self._maps = open_maps(self._gamedata_dir())
            except self.ToolError:
                raise
            except Exception as exc:
                raise self.ToolError(T("Cartes indisponibles : {err}", err=exc))
        return self._maps

    def map(self, args: Dict[str, Any]) -> Dict[str, Any]:
        src = self._map_source()
        index = src.index()
        raw = args.get("points") or args.get("way") or []
        if isinstance(raw, (str, dict)):
            raw = [raw]
        points, zone_hint, mid_hint = [], None, None
        for p in raw:
            pt, z, mid = parse_point(p)
            if pt is None:
                raise self.ToolError(T("Point illisible : {p}. Attendu : {{x, y, label}} ou « /way x y ».", p=p))
            if not (0 <= pt["x"] <= 100 and 0 <= pt["y"] <= 100):
                raise self.ToolError(T("Coordonnées hors carte : {x} {y} (0 à 100).", x=pt["x"], y=pt["y"]))
            points.append(pt)
            zone_hint = zone_hint or z
            mid_hint = mid_hint or mid
        if len(points) > MAX_POINTS:
            raise self.ToolError(T("{n} points : {max} au plus par carte.", n=len(points), max=MAX_POINTS))
        db = None
        try:
            _, db = self._char(args)
        except Exception:
            pass
        pos = (db or {}).get("position") or {}
        zone = args.get("zone") or mid_hint or zone_hint
        if points and not zone:
            # Sans zone, un /way serait posé sur la carte où se trouve le perso, souvent la mauvaise.
            raise self.ToolError(T("Précise la zone de ces /way (nom ou uiMapID) : sans elle, le repère "
                                   "serait posé sur la carte où se trouve le perso."))
        mid =resolve_zone(index, zone) if zone else (pos.get("mapId") if str(pos.get("mapId")) in index["maps"]
                                                       else None)
        if not mid:
            if zone:
                raise self.ToolError(T("Zone inconnue des cartes du client : {zone}.", zone=zone))
            raise self.ToolError(T("Indique la zone (nom ou uiMapID)."))
        entry = index["maps"][str(mid)]
        got = src.image(mid)
        if not got:
            raise self.ToolError(T("Carte de {zone} absente du client.", zone=entry["name"]))
        w, h, rgb = got
        player = None
        if pos.get("mapId") == mid and pos.get("x") is not None and args.get("moi", True):
            player = (float(pos["x"]), float(pos["y"]))
        mode = "zone" if args.get("cadre") == "zone" else "auto"
        W, H, png = render(w, h, rgb, points, mode, player)
        out_dir = self._gamedata_dir() / "cartes"
        out_dir.mkdir(parents=True, exist_ok=True)
        tag = hashlib.sha1(repr((mid, points, player, mode)).encode()).hexdigest()[:8]
        out = out_dir / f"{slug(entry['name'])}-{tag}.png"
        out.write_bytes(png)
        for old in sorted(out_dir.glob("*.png"), key=lambda p: -p.stat().st_mtime)[KEEP_RENDERS:]:
            try:
                old.unlink()
            except OSError:
                pass
        lines = [T("Carte : {zone} (uiMap {id}) · {w}×{h} · [Forever · client]", zone=entry["name"], id=mid,
                   w=W, h=H)]
        for i, p in enumerate(points, 1):
            num = f"{i}. " if len(points) > 1 else T("Repère : ")
            lines.append(f"{num}{p['label'] or '—'} · `/way {p['x']:g} {p['y']:g}`")
        if player:
            lines.append(T("Point bleu : ta position ({x:g} {y:g}).", x=player[0], y=player[1]))
        lines.append(T("Fichier : {path}", path=out))
        return {"text": "\n".join(lines), "image": png}
