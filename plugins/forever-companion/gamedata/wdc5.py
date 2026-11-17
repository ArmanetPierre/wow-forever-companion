"""Lecteur minimal de fichiers DB2 (format WDC5) piloté par les définitions WoWDBDefs.

Bibliothèque standard Python uniquement. Prototype de l'étude de faisabilité.

    from wdc5 import read_table
    rows = read_table("ItemSparse.db2", "ItemSparse.dbd", build="1.60.1.70938")

Couvre : sections, ID en ligne ou en liste, table de copie, tables d'enregistrements
denses et creuses (offset map), compression bitpacked / common / pallet / pallet array,
chaînes (table de chaînes ou en ligne), tableaux, relation non en ligne.
Les sections chiffrées dont la clé manque sont ignorées (le client les remplit de zéros).
"""
import re
import struct
from pathlib import Path

HEADER = struct.Struct("<4sI128sIIIIIIIIIHHIIIIIII")
SECTION = struct.Struct("<QIIIIIIII")


# ---------------------------------------------------------------- WoWDBDefs
def parse_dbd(path):
    """Retourne (types des colonnes, liste des blocs de version)."""
    text = Path(path).read_text(encoding="utf-8")
    col_types, blocks = {}, []
    cur = None
    section = None
    for raw in text.splitlines():
        line = raw.split("//")[0].rstrip()
        if not line.strip():
            if section == "block" and cur is not None and cur["fields"]:
                blocks.append(cur)
                cur, section = None, None
            continue
        if line == "COLUMNS":
            section = "columns"
            continue
        if line.startswith(("LAYOUT", "BUILD", "COMMENT")):
            if section != "block" or cur is None or cur["fields"]:
                if cur is not None and cur["fields"]:
                    blocks.append(cur)
                cur = {"layouts": set(), "builds": [], "fields": []}
                section = "block"
            if line.startswith("LAYOUT"):
                cur["layouts"].update(h.strip().upper() for h in line[6:].split(","))
            elif line.startswith("BUILD"):
                cur["builds"].append(line[5:].strip())
            continue
        if section == "columns":
            m = re.match(r"(\w+)(?:<[^>]*>)?\s+(\w+)", line.strip())
            if m:
                col_types[m.group(2)] = m.group(1)
        elif section == "block":
            m = re.match(r"(?:\$([\w,]+)\$)?(\w+)(?:<(u?)(\d+)>)?(?:\[(\d+)\])?", line.strip())
            if not m:
                continue
            anns = set((m.group(1) or "").split(",")) - {""}
            name = m.group(2)
            cur["fields"].append({
                "name": name,
                "type": col_types.get(name, "int"),
                "unsigned": m.group(3) == "u",
                "bits": int(m.group(4)) if m.group(4) else 32,
                "array": int(m.group(5)) if m.group(5) else 1,
                "id": "id" in anns,
                "noninline": "noninline" in anns,
                "relation": "relation" in anns,
            })
    if cur is not None and cur["fields"]:
        blocks.append(cur)
    return col_types, blocks


def _build_matches(spec, build):
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = (p.strip() for p in part.split("-"))
            if _vkey(lo) <= _vkey(build) <= _vkey(hi):
                return True
        elif part == build:
            return True
    return False


def _vkey(v):
    return tuple(int(x) for x in v.split("."))


def pick_block(blocks, layout_hash, build=None):
    lh = f"{layout_hash:08X}"
    cands = [b for b in blocks if lh in b["layouts"]]
    if build:
        exact = [b for b in cands if any(_build_matches(s, build) for s in b["builds"])]
        if exact:
            return exact[0]
    if cands:
        return cands[0]
    raise ValueError(f"aucune définition pour le layout {lh}")


# ---------------------------------------------------------------- bits
def _bits(buf, bit_offset, nbits):
    start = bit_offset >> 3
    end = (bit_offset + nbits + 7) >> 3
    val = int.from_bytes(buf[start:end], "little") >> (bit_offset & 7)
    return val & ((1 << nbits) - 1)


def _signed(v, nbits):
    return v - (1 << nbits) if nbits and v & (1 << (nbits - 1)) else v


def _cstr(buf, pos):
    end = buf.index(b"\0", pos)
    return buf[pos:end].decode("utf-8", "replace"), end + 1


# ---------------------------------------------------------------- lecture
def read_table(db2_path, dbd_path, build=None, locale_index=0):
    data = db2_path if isinstance(db2_path, (bytes, bytearray)) else Path(db2_path).read_bytes()
    (magic, _ver, _schema, rec_count, field_count, rec_size, str_size, _thash, layout_hash,
     min_id, max_id, _loc, flags, id_index, total_fields, _bdo, _lookup, fsi_size, common_size,
     pallet_size, section_count) = HEADER.unpack_from(data, 0)
    if magic != b"WDC5":
        raise ValueError(f"format non géré : {magic!r}")
    _, blocks = parse_dbd(dbd_path)
    block = pick_block(blocks, layout_hash, build)
    if rec_count == 0 or section_count == 0:
        # Table vide dans le client : son contenu arrive par les correctifs (DBCache.bin) ou le serveur.
        return {}, {"layout": f"{layout_hash:08X}", "records": 0, "sparse": bool(flags & 1),
                    "sections": section_count, "builds": block["builds"]}
    pos = HEADER.size
    sections = []
    for _ in range(section_count):
        sections.append(SECTION.unpack_from(data, pos))
        pos += SECTION.size
    pos += 4 * field_count  # field_structure (taille, position) : redondant avec storage info
    storage = []
    for _ in range(fsi_size // 24):
        storage.append(struct.unpack_from("<HHIIIII", data, pos))
        pos += 24
    pallet_base = pos
    pos += pallet_size
    common_base = pos
    pos += common_size

    # Offsets des blocs pallet/common par champ.
    pallet_off, common_off, p, c = [], [], 0, 0
    commons = []
    for (_fo, _fs, add, stype, v1, v2, v3) in storage:
        pallet_off.append(p)
        common_off.append(c)
        if stype in (3, 4):
            p += add
        if stype == 2:
            entries = {}
            for k in range(add // 8):
                cid, cval = struct.unpack_from("<II", data, common_base + c + 8 * k)
                entries[cid] = cval
            commons.append(entries)
            c += add
        else:
            commons.append(None)

    inline = [f for f in block["fields"] if not f["noninline"]]
    if len(inline) != len(storage):
        raise ValueError(f"définition incohérente : {len(inline)} champs en ligne pour {len(storage)} stockés")
    rel_field = next((f for f in block["fields"] if f["relation"] and f["noninline"]), None)
    id_field = next((f for f in block["fields"] if f["id"]), None)
    sparse = bool(flags & 1)

    # Tampon virtuel pour les chaînes (tables denses) : tous les enregistrements puis toutes les chaînes.
    total_records = sum(s[2] for s in sections)
    records_bytes = total_records * rec_size
    string_blob = bytearray()
    for s in sections:
        if not sparse:
            off = s[1] + s[2] * rec_size
            string_blob += data[off:off + s[3]]
    rows = {}
    global_index = 0
    for (tact, foff, srec, sstr, rec_end, idl_size, rel_size, om_count, copy_count) in sections:
        if srec == 0:
            continue
        # Lecture des blocs de fin de section.
        if sparse:
            p = rec_end
        else:
            p = foff + srec * rec_size + sstr
        ids = list(struct.unpack_from(f"<{idl_size // 4}I", data, p)) if idl_size else []
        p += idl_size
        copies = [struct.unpack_from("<II", data, p + 8 * k) for k in range(copy_count)]
        p += 8 * copy_count
        offset_map = [struct.unpack_from("<IH", data, p + 6 * k) for k in range(om_count)]
        p += 6 * om_count
        relation = {}
        if rel_size:
            n, _mn, _mx = struct.unpack_from("<III", data, p)
            for k in range(n):
                fid, ridx = struct.unpack_from("<II", data, p + 12 + 8 * k)
                relation[ridx] = fid
            p += rel_size
        om_ids = list(struct.unpack_from(f"<{om_count}I", data, p)) if (sparse and om_count) else []

        encrypted_empty = tact != 0
        for i in range(srec):
            if sparse:
                roff, rlen = offset_map[i]
                rec = data[roff:roff + rlen]
            else:
                roff = foff + i * rec_size
                rec = data[roff:roff + rec_size]
            if encrypted_empty and not any(rec):
                global_index += 1
                continue
            row = {}
            if sparse:
                cur = 0
                for f in inline:
                    vals = []
                    for _ in range(f["array"]):
                        if f["type"] in ("string", "locstring"):
                            s, cur = _cstr(rec, cur)
                            vals.append(s)
                        elif f["type"] == "float":
                            vals.append(struct.unpack_from("<f", rec, cur)[0])
                            cur += 4
                        else:
                            nb = f["bits"] // 8
                            v = int.from_bytes(rec[cur:cur + nb], "little", signed=not f["unsigned"])
                            vals.append(v)
                            cur += nb
                    row[f["name"]] = vals if f["array"] > 1 else vals[0]
            else:
                for fi, f in enumerate(inline):
                    fo, fs, add, stype, v1, v2, v3 = storage[fi]
                    vals = []
                    if stype == 0:
                        esize = fs // f["array"] if f["array"] else fs
                        for a in range(f["array"]):
                            bo = fo + a * esize
                            if f["type"] in ("string", "locstring"):
                                v = _bits(rec, bo, 32)
                                vpos = global_index * rec_size + (bo >> 3) + v - records_bytes
                                vals.append(_cstr(string_blob, vpos)[0] if v and 0 <= vpos < len(string_blob) else "")
                            elif f["type"] == "float":
                                vals.append(struct.unpack("<f", _bits(rec, bo, 32).to_bytes(4, "little"))[0])
                            else:
                                v = _bits(rec, bo, esize)
                                vals.append(v if f["unsigned"] else _signed(v, esize))
                    elif stype in (1, 5):
                        v = _bits(rec, fo, v2)
                        vals.append(_signed(v, v2) if stype == 5 else v)
                    elif stype == 2:
                        rid = ids[i] if ids else None
                        vals.append(commons[fi].get(rid, v1))
                    elif stype == 3:
                        idx = _bits(rec, fo, v2)
                        vals.append(struct.unpack_from("<I", data, pallet_base + pallet_off[fi] + idx * 4)[0])
                    elif stype == 4:
                        idx = _bits(rec, fo, v2)
                        base = pallet_base + pallet_off[fi] + idx * 4 * v3
                        vals = list(struct.unpack_from(f"<{v3}I", data, base))
                    if f["type"] == "float" and stype != 0:
                        vals = [struct.unpack("<f", (x & 0xFFFFFFFF).to_bytes(4, "little"))[0] for x in vals]
                    elif not f["unsigned"] and stype in (2, 3, 4):
                        vals = [_signed(x & ((1 << f["bits"]) - 1), f["bits"]) for x in vals]
                    row[f["name"]] = vals if f["array"] > 1 else (vals[0] if vals else None)
            if ids:
                rid = ids[i]
            elif om_ids:
                rid = om_ids[i]
            elif id_field and not id_field["noninline"]:
                rid = row.get(id_field["name"])
            else:
                rid = None
            if id_field:
                row[id_field["name"]] = rid
            if rel_field is not None:
                row[rel_field["name"]] = relation.get(i)
            rows[rid] = row
            global_index += 1
        for new_id, old_id in copies:
            if old_id in rows:
                r = dict(rows[old_id])
                if id_field:
                    r[id_field["name"]] = new_id
                rows[new_id] = r
    return rows, {"layout": f"{layout_hash:08X}", "records": rec_count, "sparse": sparse,
                  "sections": section_count, "builds": block["builds"]}


# ---------------------------------------------------------------- correctifs
def layout_hash_of(db2_path_or_bytes):
    data = db2_path_or_bytes if isinstance(db2_path_or_bytes, (bytes, bytearray)) \
        else Path(db2_path_or_bytes).read_bytes()
    return HEADER.unpack_from(data, 0)[8]


def decode_hotfix_record(block, data, record_id):
    """Décode un enregistrement de correctif (DBCache.bin).

    Les données suivent l'ordre des champs en ligne de la définition, sans compression :
    entiers à leur taille déclarée, flottants sur 4 octets, chaînes terminées par un zéro.
    Un champ de relation non en ligne, s'il existe, suit à la fin sur 4 octets.
    """
    row = {}
    cur = 0
    for f in block["fields"]:
        if f["noninline"]:
            continue
        vals = []
        for _ in range(f["array"]):
            if f["type"] in ("string", "locstring"):
                s, cur = _cstr(data, cur)
                vals.append(s)
            elif f["type"] == "float":
                vals.append(struct.unpack_from("<f", data, cur)[0])
                cur += 4
            else:
                nb = f["bits"] // 8
                vals.append(int.from_bytes(data[cur:cur + nb], "little", signed=not f["unsigned"]))
                cur += nb
        row[f["name"]] = vals if f["array"] > 1 else vals[0]
    for f in block["fields"]:
        if f["id"]:
            row[f["name"]] = record_id
        elif f["relation"] and f["noninline"]:
            row[f["name"]] = int.from_bytes(data[cur:cur + 4], "little") if cur + 4 <= len(data) else None
            cur += 4
    return row, cur
