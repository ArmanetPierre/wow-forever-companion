"""Décodage des textures BLP2 du client (cartes du monde), en Python standard.

    w, h, rgba = decode(data)        # rgba : bytearray de w*h*4 octets, ligne par ligne

Formats pris en charge (premier niveau de mip seulement) :
- compression 1 : palette 256 couleurs + alpha 0, 1, 4 ou 8 bits ;
- compression 2 : DXT1, DXT3, DXT5 ;
- compression 3 : BGRA 8 bits par canal.
"""
import struct

HEADER = struct.Struct("<4sIBBBBII")
HEADER_SIZE = 20 + 16 * 4 * 2 + 256 * 4   # en-tête, offsets et tailles des mips, palette


class BLPError(ValueError):
    pass


def _rgb565(c):
    r = (c >> 11) & 31
    g = (c >> 5) & 63
    b = c & 31
    return (r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)


def _color_table(c0, c1, dxt1):
    r0, g0, b0 = _rgb565(c0)
    r1, g1, b1 = _rgb565(c1)
    if c0 > c1 or not dxt1:
        return ((r0, g0, b0, 255), (r1, g1, b1, 255),
                ((2 * r0 + r1) // 3, (2 * g0 + g1) // 3, (2 * b0 + b1) // 3, 255),
                ((r0 + 2 * r1) // 3, (g0 + 2 * g1) // 3, (b0 + 2 * b1) // 3, 255))
    return ((r0, g0, b0, 255), (r1, g1, b1, 255),
            ((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2, 255), (0, 0, 0, 0))


def _dxt(src, w, h, kind):
    """kind : 1, 3 ou 5. Renvoie un bytearray RGBA."""
    out = bytearray(w * h * 4)
    bw, bh = max(1, (w + 3) // 4), max(1, (h + 3) // 4)
    block = 8 if kind == 1 else 16
    need = bw * bh * block
    if len(src) < need:
        raise BLPError(f"données DXT{kind} tronquées ({len(src)} < {need})")
    unpack_c = struct.Struct("<HHI").unpack_from
    pos = 0
    cache = {}
    for by in range(bh):
        for bx in range(bw):
            alphas = None
            if kind == 3:
                bits = int.from_bytes(src[pos:pos + 8], "little")
                alphas = [((bits >> (4 * i)) & 15) * 17 for i in range(16)]
                pos += 8
            elif kind == 5:
                a0, a1 = src[pos], src[pos + 1]
                bits = int.from_bytes(src[pos + 2:pos + 8], "little")
                if a0 > a1:
                    pal = [a0, a1] + [((7 - i) * a0 + i * a1) // 7 for i in range(1, 7)]
                else:
                    pal = [a0, a1] + [((5 - i) * a0 + i * a1) // 5 for i in range(1, 5)] + [0, 255]
                alphas = [pal[(bits >> (3 * i)) & 7] for i in range(16)]
                pos += 8
            c0, c1, idx = unpack_c(src, pos)
            pos += 8
            key = (c0, c1)
            table = cache.get(key)
            if table is None:
                table = cache[key] = [bytes(c) for c in _color_table(c0, c1, kind == 1)]
            x0, y0 = bx * 4, by * 4
            for py in range(4):
                y = y0 + py
                if y >= h:
                    break
                row = (y * w + x0) * 4
                for px in range(4):
                    if x0 + px >= w:
                        break
                    i = py * 4 + px
                    o = row + px * 4
                    out[o:o + 4] = table[(idx >> (2 * i)) & 3]
                    if alphas is not None:
                        out[o + 3] = alphas[i]
    return out


def _palette(src, pal, w, h, alpha_depth):
    n = w * h
    if len(src) < n:
        raise BLPError("données de palette tronquées")
    out = bytearray(n * 4)
    colors = [bytes((pal[i + 2], pal[i + 1], pal[i], 255)) for i in range(0, 1024, 4)]
    for p in range(n):
        out[p * 4:p * 4 + 4] = colors[src[p]]
    if alpha_depth:
        a = src[n:]
        for p in range(n):
            if alpha_depth == 8:
                v = a[p] if p < len(a) else 255
            elif alpha_depth == 4:
                b = a[p >> 1] if (p >> 1) < len(a) else 255
                v = ((b >> 4) if p & 1 else (b & 15)) * 17
            else:  # 1 bit
                b = a[p >> 3] if (p >> 3) < len(a) else 255
                v = 255 if (b >> (p & 7)) & 1 else 0
            out[p * 4 + 3] = v
    return out


def _bgra(src, w, h):
    n = w * h * 4
    if len(src) < n:
        raise BLPError("données BGRA tronquées")
    out = bytearray(src[:n])
    out[0::4], out[2::4] = src[2:n:4], src[0:n:4]
    return out


def decode(data):
    """BLP2 -> (largeur, hauteur, RGBA). Lève BLPError si le format n'est pas reconnu."""
    if len(data) < HEADER_SIZE:
        raise BLPError("fichier BLP trop court")
    magic, _typ, comp, alpha_depth, alpha_type, _mips, w, h = HEADER.unpack_from(data, 0)
    if magic != b"BLP2":
        raise BLPError(f"signature inattendue {magic!r}")
    offsets = struct.unpack_from("<16I", data, 20)
    sizes = struct.unpack_from("<16I", data, 84)
    off, size = offsets[0], sizes[0]
    if not off or off + size > len(data):
        raise BLPError("premier niveau de mip absent ou tronqué")
    src = data[off:off + size]
    if comp == 2:
        if alpha_type == 7:
            kind = 5
        elif alpha_type == 1:
            kind = 3
        else:
            kind = 1
        return w, h, _dxt(src, w, h, kind)
    if comp == 1:
        return w, h, _palette(src, data[148:148 + 1024], w, h, alpha_depth)
    if comp == 3:
        return w, h, _bgra(src, w, h)
    raise BLPError(f"compression BLP {comp} non prise en charge")


def encode_dxt1_block(c0, c1, indices):
    """Bloc DXT1 (tests) : deux couleurs 565 et 16 indices 0-3."""
    bits = 0
    for i, v in enumerate(indices):
        bits |= (v & 3) << (2 * i)
    return struct.pack("<HHI", c0, c1, bits)


def make_blp(w, h, comp, payload, alpha_depth=0, alpha_type=0, palette=b""):
    """Fabrique un BLP2 minimal (un seul mip) : utilisé par les tests, données synthétiques."""
    head = HEADER.pack(b"BLP2", 1, comp, alpha_depth, alpha_type, 0, w, h)
    offsets = [HEADER_SIZE] + [0] * 15
    sizes = [len(payload)] + [0] * 15
    pal = (palette + b"\0" * 1024)[:1024]
    return head + struct.pack("<16I", *offsets) + struct.pack("<16I", *sizes) + pal + payload
