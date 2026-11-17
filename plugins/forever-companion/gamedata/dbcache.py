"""Lecture des correctifs du client (Cache/ADB/<locale>/DBCache.bin), en lecture seule.

Le serveur de WoW Forever envoie au client des correctifs (« hotfixes ») qui ajoutent ou
remplacent des enregistrements des tables DB2 : nouveaux objets, objets refaits, quêtes…
Le client les garde dans DBCache.bin. Ce module les lit ; `wdc5.decode_hotfix_record`
décode chaque enregistrement avec la même définition que la table DB2.
Les hash de tables viennent du manifeste WoWDBDefs (champ tableHash).

Format (version 9) :
    en-tête : "XFTH", version uint32, build uint32, hash de vérification (32 octets)
    entrées : "XFTH", région int32, push int32, id unique uint32, hash de table uint32,
              id d'enregistrement uint32, taille uint32, statut uint8 (+3 octets), données

Statuts : 1 = valide, 2 = enregistrement supprimé, 3 = invalide, 4 = non public.
Pour un même (table, id), l'entrée la plus récente (push le plus grand, puis la dernière
lue) l'emporte.
"""
import struct
from pathlib import Path

MAGIC = b"XFTH"
ENTRY = struct.Struct("<4siiIIIII")
STATUS_VALID, STATUS_DELETED, STATUS_INVALID, STATUS_NOT_PUBLIC = 1, 2, 3, 4


def read_header(data):
    if data[:4] != MAGIC:
        raise ValueError("DBCache.bin : signature XFTH absente")
    version, build = struct.unpack_from("<II", data, 4)
    if version < 9:
        raise ValueError(f"DBCache.bin version {version} non gérée (9 attendue)")
    return {"version": version, "build": build}, 12 + 32


def read_dbcache(path, wanted_hashes=None):
    """Retourne (en-tête, {hash_table: {record_id: (statut, données)}}).

    `wanted_hashes` : ensemble de hash de tables à garder (None = toutes).
    """
    data = Path(path).read_bytes()
    header, pos = read_header(data)
    tables = {}
    order = {}
    n = 0
    while pos + ENTRY.size <= len(data):
        magic, _region, push, _uniq, thash, rid, size, status = ENTRY.unpack_from(data, pos)
        if magic != MAGIC:
            raise ValueError(f"DBCache.bin : entrée invalide à l'octet {pos}")
        body = data[pos + ENTRY.size:pos + ENTRY.size + size]
        pos += ENTRY.size + size
        n += 1
        if wanted_hashes is not None and thash not in wanted_hashes:
            continue
        key = (thash, rid)
        prev = order.get(key)
        if prev is not None and prev > push:
            continue
        order[key] = push
        tables.setdefault(thash, {})[rid] = (status & 0xFF, body)
    header["entries"] = n
    return header, tables
