"""Lecture des caches WDB du client (Cache/WDB/<locale>/*.wdb), en lecture seule.

Ces fichiers contiennent les quêtes, créatures, objets de décor… que le joueur a déjà
rencontrés. Format : en-tête de 24 octets puis entrées (id uint32, taille uint32, données).
Le contenu des données est propre à chaque cache et à chaque version du client ; ce
prototype en extrait seulement les chaînes lisibles (titres, noms).

    python3 -I wdb.py <fichier.wdb> [--limit 20]
"""
import argparse
import re
import struct
from pathlib import Path

STR_RE = re.compile(rb"[\x20-\x7e\xc2-\xf4][\x20-\x7e\x80-\xbf\xc2-\xf4]{3,}")


def read_wdb(path):
    data = Path(path).read_bytes()
    magic, build, locale, rec_size, version = struct.unpack_from("<4sI4sII", data, 0)
    header = {"magic": magic[::-1].decode(), "build": build, "locale": locale[::-1].decode(),
              "record_size": rec_size, "version": version}
    pos, entries = 24, []
    while pos + 8 <= len(data):
        eid, size = struct.unpack_from("<II", data, pos)
        if eid == 0 and size == 0:
            break
        body = data[pos + 8:pos + 8 + size]
        strings = []
        for m in STR_RE.finditer(body):
            try:
                strings.append(m.group().decode("utf-8"))
            except UnicodeDecodeError:
                pass
        entries.append({"id": eid, "size": size, "strings": strings})
        pos += 8 + size
    return header, entries


def _bits(buf, n, off):
    v = 0
    for k in range(n):
        byte = buf[(off + k) // 8]
        v = (v << 1) | ((byte >> (7 - ((off + k) % 8))) & 1)
    return v


def _text(raw):
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if s and all(c >= " " or c in "\n\r\t" for c in s) else None


def quest_texts(body):
    """(titre, objectifs, description) d'une entrée de questcache.wdb, ou None.

    Les longueurs des textes sont empaquetées sur 12 octets juste avant le titre
    (titre 9 bits, objectifs 12 bits, description 12 bits…), puis les textes se suivent.
    On cherche la première position où ce paquet décrit des textes UTF-8 lisibles.
    """
    for t in range(12, len(body)):
        pack = body[t - 12:t]
        lt, lo, ld = _bits(pack, 9, 0), _bits(pack, 12, 9), _bits(pack, 12, 21)
        if lt < 2 or t + lt + lo + ld > len(body):
            continue
        title = _text(body[t:t + lt])
        obj = _text(body[t + lt:t + lt + lo]) if lo else ""
        if not title or obj is None:
            continue
        desc = _text(body[t + lt + lo:t + lt + lo + ld]) if ld else ""
        if desc is None:
            continue
        return title, obj, desc
    return None


def read_quest_cache(path):
    """{id de quête: (titre, objectifs, description)} depuis questcache.wdb."""
    data = Path(path).read_bytes()
    out = {}
    pos = 24
    while pos + 8 <= len(data):
        eid, size = struct.unpack_from("<II", data, pos)
        if eid == 0 and size == 0:
            break
        texts = quest_texts(data[pos + 8:pos + 8 + size])
        if texts:
            out[eid] = texts
        pos += 8 + size
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--limit", type=int, default=20)
    a = ap.parse_args()
    header, entries = read_wdb(a.path)
    print(header, f"{len(entries)} entrées")
    for e in entries[:a.limit]:
        print(e["id"], e["strings"][:3])


if __name__ == "__main__":
    main()
