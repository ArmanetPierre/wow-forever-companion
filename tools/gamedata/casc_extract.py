"""Extrait des fichiers DB2 du stockage CASC local de WoW Forever (lecture seule).

Prototype de l'étude de faisabilité. S'appuie sur CascLib (github.com/ladislav-zezula/CascLib)
compilé en bibliothèque partagée, appelée via ctypes.

    python3 -I casc_extract.py --casclib <chemin de la lib casc> \
        --wow "/Applications/World of Warcraft" --product wowf \
        --out <dossier de sortie> itemsparse item journalencounteritem ...

Les noms sont des tables (sans extension) ; le fichier lu est dbfilesclient/<nom>.db2.
On peut aussi passer un FileDataID numérique (ex. 1572924).
Le dossier du jeu n'est jamais modifié.
"""
import argparse
import ctypes
import sys
from pathlib import Path

CASC_LOCALE_FRFR = 0x10
CASC_LOCALE_ALL = 0xFFFFFFFF
CASC_OPEN_BY_NAME = 0x0
CASC_OPEN_BY_FILEID = 0x3
CASC_OVERCOME_ENCRYPTED = 0x20


def load_lib(path):
    lib = ctypes.CDLL(str(path))
    lib.CascOpenStorage.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p)]
    lib.CascOpenStorage.restype = ctypes.c_bool
    lib.CascOpenFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                                 ctypes.POINTER(ctypes.c_void_p)]
    lib.CascOpenFile.restype = ctypes.c_bool
    lib.CascGetFileSize64.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint64)]
    lib.CascGetFileSize64.restype = ctypes.c_bool
    lib.CascReadFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
    lib.CascReadFile.restype = ctypes.c_bool
    lib.CascCloseFile.argtypes = [ctypes.c_void_p]
    lib.CascCloseStorage.argtypes = [ctypes.c_void_p]
    lib.GetCascError.restype = ctypes.c_uint32
    return lib


def read_file(lib, storage, key):
    handle = ctypes.c_void_p()
    if isinstance(key, int):
        ok = lib.CascOpenFile(storage, ctypes.c_void_p(key), CASC_LOCALE_ALL,
                              CASC_OPEN_BY_FILEID | CASC_OVERCOME_ENCRYPTED, ctypes.byref(handle))
    else:
        name = key.encode()
        ok = lib.CascOpenFile(storage, ctypes.c_char_p(name), CASC_LOCALE_ALL,
                              CASC_OPEN_BY_NAME | CASC_OVERCOME_ENCRYPTED, ctypes.byref(handle))
    if not ok:
        raise OSError(f"ouverture impossible de {key} (erreur CascLib {lib.GetCascError()})")
    try:
        size = ctypes.c_uint64()
        lib.CascGetFileSize64(handle, ctypes.byref(size))
        buf = ctypes.create_string_buffer(size.value)
        read = ctypes.c_uint32()
        if not lib.CascReadFile(handle, buf, size.value, ctypes.byref(read)):
            raise OSError(f"lecture impossible de {key} (erreur CascLib {lib.GetCascError()})")
        return buf.raw[:read.value]
    finally:
        lib.CascCloseFile(handle)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--casclib", required=True, help="chemin de la bibliothèque CascLib (.dylib/.so/.dll)")
    ap.add_argument("--wow", required=True, help="dossier racine de World of Warcraft (celui qui contient Data/)")
    ap.add_argument("--product", default="wowf", help="code produit CASC (wowf = WoW Forever)")
    ap.add_argument("--out", required=True)
    ap.add_argument("tables", nargs="+")
    args = ap.parse_args(argv)

    lib = load_lib(args.casclib)
    storage = ctypes.c_void_p()
    params = f"{args.wow}*{args.product}".encode()
    if not lib.CascOpenStorage(params, CASC_LOCALE_FRFR, ctypes.byref(storage)):
        sys.exit(f"Stockage CASC introuvable : {args.wow} ({args.product}), erreur {lib.GetCascError()}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    status = 0
    try:
        for t in args.tables:
            key = int(t) if t.isdigit() else f"dbfilesclient/{t.lower()}.db2"
            try:
                data = read_file(lib, storage, key)
            except OSError as e:
                print(f"ÉCHEC {t} : {e}")
                status = 1
                continue
            name = f"{t}.db2" if not t.isdigit() else f"fdid-{t}.db2"
            (out / name).write_bytes(data)
            print(f"OK {t} : {len(data):,} octets, signature {data[:4]!r}")
    finally:
        lib.CascCloseStorage(storage)
    return status


if __name__ == "__main__":
    sys.exit(main())
