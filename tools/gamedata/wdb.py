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
