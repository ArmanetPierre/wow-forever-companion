"""Accès en lecture seule au stockage CASC local de WoW Forever, via CascLib.

CascLib (github.com/ladislav-zezula/CascLib, licence MIT) est compilée en bibliothèque
partagée par `build.py` puis appelée ici avec ctypes. Le dossier du jeu n'est jamais
modifié : on ouvre le stockage et on lit des fichiers par FileDataID.

    with CascStorage(lib, "/Applications/World of Warcraft", "wowf") as casc:
        data = casc.read(1572924)   # ItemSparse.db2
"""
import ctypes

CASC_LOCALE_ALL = 0xFFFFFFFF
CASC_LOCALES = {"enUS": 0x2, "koKR": 0x4, "frFR": 0x10, "deDE": 0x20, "zhCN": 0x40, "esES": 0x80,
                "zhTW": 0x100, "enGB": 0x200, "esMX": 0x1000, "ruRU": 0x2000, "ptBR": 0x4000,
                "itIT": 0x8000}
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


class CascStorage:
    def __init__(self, lib_path, wow_root, product="wowf", locale="enUS"):
        self.lib = load_lib(lib_path)
        self.handle = ctypes.c_void_p()
        params = f"{wow_root}*{product}".encode()
        loc = CASC_LOCALES.get(locale, CASC_LOCALES["enUS"])
        self.locale_mask = loc
        if not self.lib.CascOpenStorage(params, loc, ctypes.byref(self.handle)):
            raise OSError(f"stockage CASC introuvable : {wow_root} ({product}), "
                          f"erreur CascLib {self.lib.GetCascError()}")

    def read(self, file_data_id):
        lib = self.lib
        fh = ctypes.c_void_p()
        flags = CASC_OPEN_BY_FILEID | CASC_OVERCOME_ENCRYPTED
        # la version du fichier dans la langue du client d'abord (tables *_lang), sinon n'importe laquelle
        if not lib.CascOpenFile(self.handle, ctypes.c_void_p(file_data_id), self.locale_mask, flags, ctypes.byref(fh)) \
                and not lib.CascOpenFile(self.handle, ctypes.c_void_p(file_data_id), CASC_LOCALE_ALL, flags,
                                         ctypes.byref(fh)):
            raise OSError(f"fichier {file_data_id} introuvable (erreur CascLib {lib.GetCascError()})")
        try:
            size = ctypes.c_uint64()
            lib.CascGetFileSize64(fh, ctypes.byref(size))
            buf = ctypes.create_string_buffer(size.value)
            read = ctypes.c_uint32()
            if not lib.CascReadFile(fh, buf, size.value, ctypes.byref(read)):
                raise OSError(f"lecture impossible de {file_data_id} (erreur CascLib {lib.GetCascError()})")
            return buf.raw[:read.value]
        finally:
            lib.CascCloseFile(fh)

    def close(self):
        if self.handle:
            self.lib.CascCloseStorage(self.handle)
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
