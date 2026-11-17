"""Parseur des fichiers SavedVariables de World of Warcraft.

Le jeu écrit des affectations Lua de la forme ``Nom = { ["clé"] = valeur, ... }``.
Ce module les lit sans exécuter de code, avec la bibliothèque standard uniquement.

Conversion vers Python :
- table dont les clés sont exactement 1..n  -> list
- table vide ``{}``                          -> dict vide (utiliser ``as_list``)
- autre table                                -> dict (clés int ou str)
- nil -> None, true/false -> bool, nombres -> int ou float

Usage :
    from luasv import load_file
    data = load_file(path)          # {"ForeverScribeCharDB": {...}}
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Dict, List, Union

__all__ = ["LuaParseError", "loads", "load_file", "as_list"]


class LuaParseError(ValueError):
    """Erreur de syntaxe dans un fichier SavedVariables."""

    def __init__(self, message: str, text: str, pos: int):
        line = text.count("\n", 0, pos) + 1
        col = pos - (text.rfind("\n", 0, pos) + 1) + 1
        super().__init__(f"{message} (ligne {line}, colonne {col})")
        self.line = line
        self.col = col


_NUMBER_RE = re.compile(
    r"""
    0[xX][0-9a-fA-F]+(?:\.[0-9a-fA-F]*)?(?:[pP][+-]?\d+)?   # hexadécimal
    | (?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?                  # décimal
    """,
    re.VERBOSE,
)
_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_SIMPLE_ESCAPES = {
    "n": b"\n", "t": b"\t", "r": b"\r", "a": b"\a", "b": b"\b",
    "f": b"\f", "v": b"\v", "\\": b"\\", '"': b'"', "'": b"'", "\n": b"\n",
}
_KEYWORDS = {"nil": None, "true": True, "false": False}


class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.n = len(text)

    # -- utilitaires -------------------------------------------------------
    def error(self, message: str) -> LuaParseError:
        return LuaParseError(message, self.text, self.pos)

    def skip(self) -> None:
        """Saute les blancs et les commentaires (--, --[[ ]], --[==[ ]==])."""
        text, n = self.text, self.n
        while self.pos < n:
            c = text[self.pos]
            if c in " \t\r\n\f\v﻿":
                self.pos += 1
            elif text.startswith("--", self.pos):
                self.pos += 2
                m = re.match(r"\[(=*)\[", text[self.pos:self.pos + 64])
                if m:
                    close = "]" + m.group(1) + "]"
                    end = text.find(close, self.pos)
                    if end < 0:
                        raise self.error("commentaire long non fermé")
                    self.pos = end + len(close)
                else:
                    end = text.find("\n", self.pos)
                    self.pos = n if end < 0 else end + 1
            else:
                break

    def peek(self) -> str:
        self.skip()
        return self.text[self.pos] if self.pos < self.n else ""

    def expect(self, ch: str) -> None:
        if self.peek() != ch:
            raise self.error(f"'{ch}' attendu")
        self.pos += 1

    # -- valeurs ------------------------------------------------------------
    def value(self) -> Any:
        c = self.peek()
        if c == "{":
            return self.table()
        if c in "\"'":
            return self.string()
        if c == "[" and re.match(r"\[=*\[", self.text[self.pos:self.pos + 64]):
            return self.long_string()
        if c == "-" or c == "." or c.isdigit():
            return self.number()
        m = _NAME_RE.match(self.text, self.pos)
        if m:
            word = m.group(0)
            if word in _KEYWORDS:
                self.pos = m.end()
                return _KEYWORDS[word]
            if word == "math":  # math.huge écrit par certains clients
                m2 = re.match(r"math\.huge", self.text[self.pos:])
                if m2:
                    self.pos += m2.end()
                    return math.inf
            if word in ("inf", "nan"):
                self.pos = m.end()
                return math.inf if word == "inf" else math.nan
        raise self.error("valeur attendue")

    def number(self) -> Union[int, float]:
        sign = 1
        if self.text[self.pos] == "-":
            sign = -1
            self.pos += 1
            self.skip()
            # -inf / -math.huge
            if self.text.startswith("math.huge", self.pos):
                self.pos += len("math.huge")
                return -math.inf
            if self.text.startswith("inf", self.pos):
                self.pos += 3
                return -math.inf
            # 1.#INF / -1.#IND (anciens clients Windows)
        m = _NUMBER_RE.match(self.text, self.pos)
        if not m:
            raise self.error("nombre invalide")
        raw = m.group(0)
        self.pos = m.end()
        if self.text.startswith("#INF", self.pos) or self.text.startswith("#IND", self.pos):
            special = self.text[self.pos:self.pos + 4]
            self.pos += 4
            return sign * math.inf if special == "#INF" else math.nan
        if raw[:2] in ("0x", "0X"):
            if "." in raw or "p" in raw or "P" in raw:
                return sign * float.fromhex(raw)
            return sign * int(raw, 16)
        if any(ch in raw for ch in ".eE"):
            return sign * float(raw)
        return sign * int(raw)

    def string(self) -> str:
        text = self.text
        quote = text[self.pos]
        self.pos += 1
        out = bytearray()
        start = self.pos
        while True:
            if self.pos >= self.n:
                raise self.error("chaîne non fermée")
            c = text[self.pos]
            if c == quote:
                out += text[start:self.pos].encode("utf-8")
                self.pos += 1
                break
            if c == "\\":
                out += text[start:self.pos].encode("utf-8")
                self.pos += 1
                out += self.escape()
                start = self.pos
                continue
            if c == "\n":
                raise self.error("retour à la ligne dans une chaîne")
            self.pos += 1
        return out.decode("utf-8", errors="replace")

    def escape(self) -> bytes:
        text = self.text
        if self.pos >= self.n:
            raise self.error("échappement incomplet")
        c = text[self.pos]
        if c == "\r":  # \ suivi de CRLF
            self.pos += 1
            if text.startswith("\n", self.pos):
                self.pos += 1
            return b"\n"
        if c in _SIMPLE_ESCAPES:
            self.pos += 1
            return _SIMPLE_ESCAPES[c]
        if c.isdigit():
            m = re.match(r"\d{1,3}", text[self.pos:self.pos + 3])
            self.pos += m.end()
            val = int(m.group(0))
            if val > 255:
                raise self.error("échappement décimal > 255")
            return bytes([val])
        if c == "x":
            m = re.match(r"x([0-9a-fA-F]{2})", text[self.pos:self.pos + 3])
            if not m:
                raise self.error("échappement \\x invalide")
            self.pos += 3
            return bytes([int(m.group(1), 16)])
        if c == "z":
            self.pos += 1
            while self.pos < self.n and text[self.pos] in " \t\r\n\f\v":
                self.pos += 1
            return b""
        if c == "u":
            m = re.match(r"u\{([0-9a-fA-F]+)\}", text[self.pos:self.pos + 12])
            if not m:
                raise self.error("échappement \\u invalide")
            self.pos += m.end()
            return chr(int(m.group(1), 16)).encode("utf-8")
        # échappement inconnu : Lua refuserait, on garde le caractère
        self.pos += 1
        return c.encode("utf-8")

    def long_string(self) -> str:
        m = re.match(r"\[(=*)\[", self.text[self.pos:self.pos + 64])
        close = "]" + m.group(1) + "]"
        start = self.pos + m.end()
        if self.text.startswith("\r\n", start):
            start += 2
        elif self.text.startswith("\n", start):
            start += 1
        end = self.text.find(close, start)
        if end < 0:
            raise self.error("chaîne longue non fermée")
        self.pos = end + len(close)
        return self.text[start:end]

    def table(self) -> Union[Dict[Any, Any], List[Any]]:
        self.expect("{")
        result: Dict[Any, Any] = {}
        array_index = 1
        while True:
            c = self.peek()
            if c == "}":
                self.pos += 1
                break
            if c == "":
                raise self.error("table non fermée")
            if c == "[" and not re.match(r"\[=*\[", self.text[self.pos:self.pos + 64]):
                self.pos += 1
                key = self.value()
                self.expect("]")
                self.expect("=")
                val = self.value()
                if isinstance(key, float) and key.is_integer():
                    key = int(key)
                if val is not None:
                    result[key] = val
            else:
                m = _NAME_RE.match(self.text, self.pos)
                after = None
                if m and m.group(0) not in _KEYWORDS:
                    save = self.pos
                    self.pos = m.end()
                    if self.peek() == "=":
                        after = m.group(0)
                    else:
                        self.pos = save
                if after is not None:
                    self.pos += 1  # '='
                    val = self.value()
                    if val is not None:
                        result[after] = val
                else:
                    val = self.value()
                    if val is not None:
                        result[array_index] = val
                    array_index += 1
            sep = self.peek()
            if sep in ",;":
                self.pos += 1
            elif sep != "}":
                raise self.error("',' ou '}' attendu")
        return _normalize(result)

    # -- fichier ------------------------------------------------------------
    def chunk(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        while self.peek():
            m = _NAME_RE.match(self.text, self.pos)
            if not m:
                raise self.error("nom de variable attendu")
            name = m.group(0)
            self.pos = m.end()
            self.expect("=")
            out[name] = self.value()
            if self.peek() == ";":
                self.pos += 1
        return out


def _normalize(table: Dict[Any, Any]) -> Union[Dict[Any, Any], List[Any]]:
    """Transforme une table 1..n en liste."""
    n = len(table)
    if n and all(isinstance(k, int) and not isinstance(k, bool) for k in table):
        keys = sorted(table)
        if keys[0] == 1 and keys[-1] == n:
            return [table[i] for i in range(1, n + 1)]
    return table


def as_list(value: Any) -> List[Any]:
    """Renvoie toujours une liste : ``{}`` et ``None`` -> [], dict à clés entières -> valeurs triées."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        if not value:
            return []
        if all(isinstance(k, int) for k in value):
            return [value[k] for k in sorted(value)]
        return list(value.values())
    return [value]


def loads(text: str) -> Dict[str, Any]:
    """Analyse le contenu d'un fichier SavedVariables et renvoie {variable: valeur}."""
    if text.startswith("﻿"):
        text = text[1:]
    return _Parser(text).chunk()


def load_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Lit un fichier SavedVariables (UTF-8, LF ou CRLF)."""
    raw = Path(path).read_bytes()
    return loads(raw.decode("utf-8", errors="replace"))


if __name__ == "__main__":  # python3 luasv.py fichier.lua -> JSON
    import json
    import sys

    for p in sys.argv[1:]:
        print(json.dumps(load_file(p), ensure_ascii=False, indent=1, default=str))
