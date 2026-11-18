"""Cartes des zones : décodage BLP2, index des tables UiMap, assemblage fond + zones découvertes.
Textures et tables entièrement synthétiques (aucune donnée du jeu).

    python3 -m unittest discover -s plugins/forever-companion/gamedata/tests
"""
import struct
import tempfile
import unittest
from pathlib import Path

import synthetic as SY  # noqa: F401,E402  (ajoute le dossier du plugin au chemin)
from gamedata import blp, maps  # noqa: E402

RED565, BLUE565 = 0xF800, 0x001F


def dxt1(w, h, c0, c1, idx=0):
    block = blp.encode_dxt1_block(c0, c1, [idx] * 16)
    return blp.make_blp(w, h, 2, block * ((w // 4) * (h // 4)))


def bgra(w, h, b, g, r, a=255):
    return blp.make_blp(w, h, 3, bytes((b, g, r, a)) * (w * h))


class TestBLP(unittest.TestCase):
    def test_dxt1_colors(self):
        w, h, px = blp.decode(dxt1(8, 4, RED565, BLUE565, 0))
        self.assertEqual((w, h), (8, 4))
        self.assertEqual(tuple(px[0:4]), (255, 0, 0, 255))
        _, _, px = blp.decode(dxt1(4, 4, RED565, BLUE565, 1))
        self.assertEqual(tuple(px[-4:]), (0, 0, 255, 255))
        # index 2 avec c0 > c1 : 2/3 c0 + 1/3 c1
        _, _, px = blp.decode(dxt1(4, 4, RED565, BLUE565, 2))
        self.assertEqual(tuple(px[0:4]), (170, 0, 85, 255))

    def test_dxt1_transparent_when_c0_le_c1(self):
        _, _, px = blp.decode(dxt1(4, 4, BLUE565, RED565, 3))
        self.assertEqual(px[3], 0)

    def test_dxt1_per_pixel_index(self):
        idx = [0] * 15 + [1]
        data = blp.make_blp(4, 4, 2, blp.encode_dxt1_block(RED565, BLUE565, idx))
        _, _, px = blp.decode(data)
        self.assertEqual(tuple(px[:3]), (255, 0, 0))
        self.assertEqual(tuple(px[15 * 4:15 * 4 + 3]), (0, 0, 255))

    def test_dxt5_alpha(self):
        alpha = bytes((200, 10)) + (0).to_bytes(6, "little")   # tous les indices à 0 -> 200
        block = alpha + blp.encode_dxt1_block(RED565, BLUE565, [0] * 16)
        _, _, px = blp.decode(blp.make_blp(4, 4, 2, block, alpha_depth=8, alpha_type=7))
        self.assertEqual(tuple(px[0:4]), (255, 0, 0, 200))

    def test_bgra_uncompressed(self):
        _, _, px = blp.decode(bgra(2, 2, 10, 20, 30, 40))
        self.assertEqual(tuple(px[0:4]), (30, 20, 10, 40))

    def test_palette(self):
        pal = bytes((0, 0, 255, 0)) + bytes((0, 255, 0, 0))   # BGRA : rouge, vert
        data = blp.make_blp(2, 1, 1, bytes((1, 0)), palette=pal)
        _, _, px = blp.decode(data)
        self.assertEqual(tuple(px), (0, 255, 0, 255, 255, 0, 0, 255))

    def test_rejects_garbage(self):
        with self.assertRaises(blp.BLPError):
            blp.decode(b"NOPE" + bytes(2000))
        with self.assertRaises(blp.BLPError):
            blp.decode(blp.make_blp(8, 8, 2, b"\0" * 8))   # DXT tronqué


class FakeTables:
    def __init__(self, tables):
        self.tables = tables

    def get(self, name):
        if name not in self.tables:
            raise KeyError(name)
        return self.tables[name]


def fake_tables():
    return FakeTables({
        "UiMap": {9001: {"ID": 9001, "Name_lang": "Val d'essai", "Type": 3, "ParentUiMapID": 9000},
                  9002: {"ID": 9002, "Name_lang": "Sans art", "Type": 3, "ParentUiMapID": 9000}},
        "UiMapXMapArt": {1: {"ID": 1, "UiMapID": 9001, "UiMapArtID": 50, "PhaseID": 0}},
        "UiMapArt": {50: {"ID": 50, "UiMapArtStyleID": 1}},
        "UiMapArtStyleLayer": {1: {"ID": 1, "UiMapArtStyleID": 1, "LayerIndex": 0, "LayerWidth": 6,
                                   "LayerHeight": 4, "TileWidth": 4, "TileHeight": 4}},
        "UiMapArtTile": {1: {"ID": 1, "UiMapArtID": 50, "RowIndex": 0, "ColIndex": 0, "LayerIndex": 0,
                             "FileDataID": 100},
                         2: {"ID": 2, "UiMapArtID": 50, "RowIndex": 0, "ColIndex": 1, "LayerIndex": 0,
                             "FileDataID": 101}},
        "UiMapAssignment": {1: {"ID": 1, "AreaID": 77, "UiMapID": 9001, "OrderIndex": 0}},
        "WorldMapOverlay": {1: {"ID": 1, "UiMapArtID": 50, "OffsetX": 1, "OffsetY": 1, "TextureWidth": 2,
                                "TextureHeight": 2}},
        "WorldMapOverlayTile": {1: {"ID": 1, "WorldMapOverlayID": 1, "RowIndex": 0, "ColIndex": 0,
                                    "LayerIndex": 0, "FileDataID": 200}},
    })


class TestIndexAndCompose(unittest.TestCase):
    def test_index(self):
        idx = maps.build_index(fake_tables())
        self.assertEqual(list(idx["maps"]), ["9001"])   # carte sans texture ignorée
        e = idx["maps"]["9001"]
        self.assertEqual((e["width"], e["height"], e["name"]), (6, 4, "Val d'essai"))
        self.assertEqual(e["tiles"], [[0, 0, 100], [0, 1, 101]])
        self.assertEqual(e["overlays"], [[1, 1, 2, 2, [[0, 0, 200]]]])
        self.assertEqual(idx["areas"], {"77": 9001})

    def test_index_without_overlay_tables(self):
        t = fake_tables()
        del t.tables["WorldMapOverlay"]
        self.assertEqual(maps.build_index(t)["maps"]["9001"]["overlays"], [])

    def test_compose_tiles_overlay_and_missing(self):
        e = maps.build_index(fake_tables())["maps"]["9001"]
        files = {100: bgra(4, 4, 0, 0, 255),            # rouge
                 101: bgra(4, 4, 255, 0, 0),            # bleu, coupé à 2 colonnes (largeur 6)
                 200: bgra(4, 4, 0, 255, 0, 255)}       # zone découverte verte 2 x 2 en (1, 1)

        def read(fdid):
            if fdid not in files:
                raise OSError("absent")
            return files[fdid]
        w, h, rgb = maps.compose(e, read)
        px = lambda x, y: tuple(rgb[(y * w + x) * 3:(y * w + x) * 3 + 3])  # noqa: E731
        self.assertEqual((w, h, len(rgb)), (6, 4, 72))
        self.assertEqual(px(0, 0), (255, 0, 0))
        self.assertEqual(px(5, 3), (0, 0, 255))
        self.assertEqual(px(1, 1), (0, 255, 0))
        self.assertEqual(px(2, 2), (0, 255, 0))
        self.assertEqual(px(3, 3), (255, 0, 0))        # hors de la zone découverte (2 x 2)
        del files[101]
        _, _, rgb = maps.compose(e, read)
        self.assertEqual(tuple(rgb[(0 * 6 + 5) * 3:(0 * 6 + 5) * 3 + 3]), maps.BACKGROUND)

    def test_alpha_blend(self):
        e = maps.build_index(fake_tables())["maps"]["9001"]
        files = {100: bgra(4, 4, 0, 0, 200), 101: bgra(4, 4, 0, 0, 200), 200: bgra(4, 4, 0, 0, 0, 0)}
        w, _, rgb = maps.compose(e, files.__getitem__)
        self.assertEqual(tuple(rgb[(1 * w + 1) * 3:(1 * w + 1) * 3 + 3]), (200, 0, 0))   # transparent : dessous

    def test_cache_roundtrip(self):
        e = maps.build_index(fake_tables())["maps"]["9001"]
        with tempfile.TemporaryDirectory() as d:
            rgb = bytearray(range(72))
            maps.save_map(Path(d), 9001, 6, 4, rgb)
            self.assertEqual(maps.load_map(Path(d), 9001, e), (6, 4, rgb))
            self.assertIsNone(maps.load_map(Path(d), 9002, e))


if __name__ == "__main__":
    unittest.main()
