"""Outil `map` : PNG, repères, recadrage, lecture des /way, choix de la zone, réponse MCP avec image.
Carte synthétique (aucune donnée du jeu).

    cd plugins/forever-companion/mcp && python3 -m unittest tests.test_worldmap
"""
import base64
import os
os.environ.setdefault("FOREVER_WEB_LOOKUP", "0")
import shutil
import struct
import sys
import unittest
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import e2e_stdio as E  # noqa: E402
import server  # noqa: E402
import sync  # noqa: E402
import worldmap as W  # noqa: E402

GREY = (120, 110, 90)


def read_png(data):
    """Décodeur PNG minimal (RGB 8 bits, filtres 0 et 1) pour vérifier les pixels."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, w, h = 8, b"", 0, 0
    while pos < len(data):
        n = struct.unpack(">I", data[pos:pos + 4])[0]
        tag, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        if tag == b"IHDR":
            w, h = struct.unpack(">II", body[:8])
        elif tag == b"IDAT":
            idat += body
        pos += 12 + n
    raw, out, stride = zlib.decompress(idat), bytearray(), w * 3
    for y in range(h):
        f, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if f == 1:
            for i in range(3, stride):
                line[i] = (line[i] + line[i - 3]) & 255
        out += line
    return w, h, out


def pixel(img, x, y):
    w, _, rgb = img
    return tuple(rgb[(y * w + x) * 3:(y * w + x) * 3 + 3])


def grey_map(w=1002, h=668):
    return w, h, bytearray(bytes(GREY) * (w * h))


INDEX = {"maps": {"1437": {"name": "Les Paluns", "type": 3, "parent": 1415, "width": 1002, "height": 668},
                  "1426": {"name": "Dun Morogh", "type": 3, "parent": 1415, "width": 1002, "height": 668},
                  "9999": {"name": "Paluns des essais", "type": 5, "parent": 1437, "width": 1002, "height": 668}},
         "areas": {"11": 1437}}


class FakeMaps:
    def __init__(self):
        self.calls = []

    def index(self):
        return INDEX

    def image(self, mid):
        self.calls.append(mid)
        return grey_map() if str(mid) in INDEX["maps"] else None


class TestImage(unittest.TestCase):
    def test_png_roundtrip(self):
        w, h = 16, 16
        rgb = bytes((i * 7) & 255 for i in range(w * h * 3))
        img = read_png(W.png_bytes(w, h, rgb))
        self.assertEqual((img[0], img[1]), (16, 16))
        self.assertEqual(bytes(img[2]), rgb)

    def test_marker_at_way_coordinates(self):
        w, h, rgb = grey_map()
        W2, H2, png = W.render(w, h, rgb, [{"x": 50, "y": 50}], "zone")
        img = read_png(png)
        self.assertEqual((W2, H2), (1002, 668))
        self.assertEqual(pixel(img, 501, 334), W.RED)       # centre du repère = x% de 1002, y% de 668
        self.assertEqual(pixel(img, 501 + 9, 334), W.WHITE)  # anneau blanc
        self.assertEqual(pixel(img, 501 + 12, 334), W.BLACK)
        self.assertEqual(pixel(img, 501 + 20, 334), GREY)
        self.assertEqual(pixel(img, 10, 10), GREY)

    def test_numbered_markers_and_player(self):
        w, h, rgb = grey_map()
        _, _, png = W.render(w, h, rgb, [{"x": 10, "y": 60}, {"x": 90, "y": 20}], "zone", player=(50, 50))
        img = read_png(png)
        self.assertEqual(pixel(img, 501, 334), W.BLUE)
        # chiffre « 1 » blanc dessiné dans le premier repère : il reste du rouge et du blanc
        cx, cy = round(10 * 10.02), round(60 * 6.68)
        colors = {pixel(img, cx + dx, cy + dy) for dx in range(-6, 7) for dy in range(-6, 7)}
        self.assertIn(W.WHITE, colors)
        self.assertIn(W.RED, colors)

    def test_auto_frame_zooms_on_close_points(self):
        x0, y0, cw, ch, k = W.frame(1002, 668, [(38.1, 50.2), (36.5, 46.8)])
        self.assertEqual(k, 2)
        self.assertLess(cw, 600)
        self.assertAlmostEqual(cw / ch, 1002 / 668, places=1)
        px, py = 38.1 * 10.02, 50.2 * 6.68
        self.assertTrue(x0 <= px <= x0 + cw and y0 <= py <= y0 + ch)
        w, h, rgb = grey_map()
        W2, H2, png = W.render(w, h, rgb, [{"x": 38.1, "y": 50.2}], "auto")
        img = read_png(png)
        x0b, y0b, _, _, _ = W.frame(1002, 668, [(38.1, 50.2)])
        self.assertEqual(pixel(img, round((38.1 * 10.02 - x0b) * 2), round((50.2 * 6.68 - y0b) * 2)), W.RED)
        self.assertGreater(W2, 600)

    def test_far_points_keep_whole_zone(self):
        self.assertEqual(W.frame(1002, 668, [(5, 5), (95, 90)]), (0, 0, 1002, 668, 1))
        self.assertEqual(W.frame(1002, 668, [(5, 5)], "zone"), (0, 0, 1002, 668, 1))

    def test_frame_clamped_to_map(self):
        x0, y0, cw, ch, _ = W.frame(1002, 668, [(1, 99)])
        self.assertEqual(x0, 0)
        self.assertEqual(y0 + ch, 668)


class TestParsing(unittest.TestCase):
    def test_parse_way_strings(self):
        self.assertEqual(W.parse_point("/way 38.1 50.2 Whelgar"),
                         ({"x": 38.1, "y": 50.2, "label": "Whelgar"}, None, None))
        self.assertEqual(W.parse_point("/way #1437 10 60")[2], 1437)
        pt, zone, _ = W.parse_point("/way Les Paluns 10,5 60 Port")
        self.assertEqual((pt["x"], zone, pt["label"]), (10.5, "Les Paluns", "Port"))
        self.assertEqual(W.parse_point({"x": "12", "y": 34, "label": "Brannok"})[0],
                         {"x": 12.0, "y": 34.0, "label": "Brannok"})
        self.assertEqual(W.parse_point("pas de chiffres"), (None, None, None))

    def test_resolve_zone(self):
        self.assertEqual(W.resolve_zone(INDEX, "Les Paluns"), 1437)
        self.assertEqual(W.resolve_zone(INDEX, "paluns"), 1437)          # sans article, type zone d'abord
        self.assertEqual(W.resolve_zone(INDEX, "Wetlands"), 1437)        # nom anglais
        self.assertEqual(W.resolve_zone(INDEX, 1426), 1426)
        self.assertEqual(W.resolve_zone(INDEX, "11"), 1437)              # id de zone (AreaTable)
        self.assertIsNone(W.resolve_zone(INDEX, "Atlantide"))
        self.assertIsNone(W.resolve_zone(INDEX, "Durotar"))              # nom connu mais carte absente


class TestTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = E.build_sandbox()
        cls.old = os.environ.get("FOREVER_GAMEDB")
        os.environ["FOREVER_GAMEDB"] = str(cls.tmp / "none.sqlite")
        cls.srv = server.Server(sync.Store(cls.tmp / "perso"))
        cls.out = cls.tmp / "gamedata"
        cls.srv.tools._maps = FakeMaps()
        cls.srv.tools._gamedata_dir = lambda: cls.out

    @classmethod
    def tearDownClass(cls):
        if cls.old is None:
            os.environ.pop("FOREVER_GAMEDB", None)
        else:
            os.environ["FOREVER_GAMEDB"] = cls.old
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def call(self, **args):
        r = self.srv.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                             "params": {"name": "map", "arguments": args}})
        return r["result"]

    def test_listed_with_short_description(self):
        tools = self.srv.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
        t = next(t for t in tools if t["name"] == "map")
        self.assertLess(len(t["description"]), 140)

    def test_text_and_image(self):
        res = self.call(zone="Les Paluns", points=["/way 38.1 50.2 Whelgar", {"x": 10, "y": 60, "label": "Menethil"}], lang="fr")
        self.assertFalse(res["isError"], res)
        text, image = res["content"]
        self.assertIn("Les Paluns (uiMap 1437)", text["text"])
        self.assertIn("1. Whelgar · `/way 38.1 50.2`", text["text"])
        self.assertIn("2. Menethil", text["text"])
        self.assertIn("Point bleu : ta position (9.5 58.3)", text["text"])   # perso aux Paluns
        self.assertEqual(image["type"], "image")
        self.assertEqual(image["mimeType"], "image/png")
        png = base64.b64decode(image["data"])
        path = Path(text["text"].split("Fichier : ")[1].strip())
        self.assertTrue(path.is_file())
        self.assertEqual(path.read_bytes(), png)
        self.assertTrue(str(path).startswith(str(self.out / "cartes")))

    def test_zone_by_english_name_and_errors(self):
        res = self.call(zone="Dun Morogh", points=["/way 46 52"], lang="en")
        self.assertFalse(res["isError"])
        self.assertIn("Map: Dun Morogh (uiMap 1426)", res["content"][0]["text"])
        self.assertNotIn("Blue dot", res["content"][0]["text"])           # perso ailleurs
        res = self.call(zone="Atlantide", points=["/way 1 1"], lang="fr")
        self.assertTrue(res["isError"])
        self.assertIn("Zone inconnue", res["content"][0]["text"])
        res = self.call(zone=1437, points=["/way 120 5"], lang="fr")
        self.assertTrue(res["isError"])
        res = self.call(zone=1437, points=[f"/way {i} {i}" for i in range(10)], lang="fr")
        self.assertTrue(res["isError"])

    def test_default_zone_is_current(self):
        res = self.call(lang="fr")
        self.assertFalse(res["isError"])
        self.assertIn("Les Paluns", res["content"][0]["text"])

    def test_points_without_zone_refused(self):
        # Le perso est aux Paluns : un /way sans zone ne doit pas être posé d'office sur sa carte.
        res = self.call(points=["/way 38.1 50.2 Whelgar"], lang="fr")
        self.assertTrue(res["isError"])
        self.assertIn("Précise la zone", res["content"][0]["text"])
        res = self.call(points=["/way 38.1 50.2"], lang="en")
        self.assertIn("Give the zone", res["content"][0]["text"])
        res = self.call(points=["/way #1437 38.1 50.2"], lang="fr")      # uiMapID dans le /way : accepté
        self.assertFalse(res["isError"], res)


if __name__ == "__main__":
    unittest.main()
