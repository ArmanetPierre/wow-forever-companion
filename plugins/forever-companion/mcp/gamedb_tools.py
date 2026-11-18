"""Outils MCP adossés à la base locale du jeu : find_items, get_item, find_upgrades,
get_dungeon_loot, find_recipes (lecture seule). Quêtes et PNJ : questdb_tools.py."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

import formats as F
import gamedb as GDB
import gear as G
import dungeons as DG
import professions_plan as PP
from i18n import T
from luasv import as_list


def _cap1(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def db_at_level(db: Dict[str, Any], level: int) -> Dict[str, Any]:
    """Copie légère du perso avec un autre niveau (évaluer un objet « pour plus tard »)."""
    out = dict(db)
    prog = dict(db.get("progression") or {})
    prog["level"] = level
    out["progression"] = prog
    ident = dict(db.get("identity") or {})
    ident["level"] = level
    out["identity"] = ident
    return out


class GameDBToolsMixin:
    """Mélangé à Tools (server.py) : utilise self.store et self._char."""

    _gdb: Optional[GDB.GameDB] = None
    _gdb_path = None

    # -- accès ---------------------------------------------------------------------
    def gamedb(self, required: bool = True) -> Optional[GDB.GameDB]:
        path = GDB.find_db_path(getattr(self.store, "data_dir", None), getattr(self, "_locale", None))
        if path is None:
            if required:
                raise self.ToolError(GDB.missing_message())
            return None
        if self._gdb is None or self._gdb_path != path:
            self._gdb = GDB.GameDB(path)
            self._gdb_path = path
        return self._gdb

    def _db_char(self, args: Dict[str, Any]):
        try:
            return self._char(args)
        except Exception:
            return None, None

    # -- find_items ----------------------------------------------------------------
    def find_items(self, args: Dict[str, Any]) -> str:
        gdb = self.gamedb()
        where, params = ["1=1"], []
        if args.get("nom"):
            n = F.norm_key(args["nom"])
            where.append("name_norm LIKE ?")
            params.append("%" + "%".join(n.split()) + "%")
        if args.get("emplacement"):
            slot = self._slot_key(args["emplacement"])
            inv = GDB.SLOT_INVTYPES.get(slot) or []
            where.append(f"inventory_type IN ({','.join('?' * len(inv))})")
            params += inv
        if args.get("type"):
            parsed = G.parse_type(args["type"])
            if parsed:
                cid, subs = parsed
                where.append(f"class_id = ? AND subclass_id IN ({','.join('?' * len(subs))})")
                params += [cid, *subs]
            else:
                slot = F.SLOT_ALIASES.get(F.norm_key(args["type"]))
                inv = GDB.SLOT_INVTYPES.get(slot) if slot else None
                if not inv:
                    raise self.ToolError(T("Type « {type} » inconnu. Exemples : cuir, maille, arc, fusil, arbalète, "
                                           "dague, épée, bâton, anneau, cape (ou en anglais : leather, mail, bow, "
                                           "gun, crossbow, dagger…).", type=args["type"]))
                where.append(f"inventory_type IN ({','.join('?' * len(inv))})")
                params += inv
        if args.get("niveau_min") is not None:
            where.append("req_level >= ?")
            params.append(int(args["niveau_min"]))
        if args.get("niveau_max") is not None:
            where.append("req_level <= ?")
            params.append(int(args["niveau_max"]))
        if args.get("qualite_min") is not None:
            where.append("quality >= ?")
            params.append(self._quality(args["qualite_min"]))
        stat = None
        if args.get("stat"):
            stat = GDB.STAT_ALIASES.get(F.norm_key(args["stat"]), F.norm_key(args["stat"]))
            where.append("stats_json LIKE ?")
            params.append(f'%"{stat}"%')
        if args.get("forever_seulement"):
            where.append("origin IN ('modifie', 'ajoute')")
        limit = max(1, min(int(args.get("limite") or 15), 50))
        order = "req_level DESC, ilvl DESC" if not args.get("nom") else "length(name), ilvl DESC"
        rows = [r for r in gdb.q(f"SELECT * FROM items WHERE {' AND '.join(where)} ORDER BY {order} LIMIT ?",
                                 (*params, limit * 3)) if GDB.plausible_item(r)]
        if stat:
            rows.sort(key=lambda r: -(GDB.stats_of(r).get(stat) or 0))
        rows = rows[:limit]
        if not rows:
            return gdb.header() + "\n\n" + T("Aucun objet ne correspond à ces critères dans la base locale.")
        lines = [gdb.header(), "", T("{n} objet(s) :", n=len(rows)), ""]
        for r in rows:
            lines.append(f"- {GDB.item_title(r)}{F.sep()}{GDB.stats_line(r)}")
        lines.append("\n_" + T("Détail et sources d'un objet : get_item. La base contient tous les objets définis "
                                "par le client, y compris certains jamais obtenables : vérifie la source avant de "
                                "conseiller.") + "_")
        return "\n".join(lines)

    # -- get_item ------------------------------------------------------------------
    def get_item(self, args: Dict[str, Any]) -> str:
        gdb = self.gamedb()
        rows = []
        if args.get("itemId"):
            r = gdb.item(int(args["itemId"]))
            rows = [r] if r else []
        elif args.get("nom"):
            rows = gdb.items_by_name(args["nom"], 6)
        else:
            raise self.ToolError(T("Donne l'itemId ou le nom de l'objet."))
        if not rows:
            raise self.ToolError(T("Objet introuvable dans la base locale (vérifie l'orthographe, ou cherche avec "
                                   "find_items)."))
        r = rows[0]
        lines = [gdb.header(), "", GDB.item_title(r), f"- {GDB.stats_line(r)}",
                 T("- Origine des données : {origin} {badge}", origin=GDB.origin_note(r), badge=GDB.badge())]
        if not GDB.plausible_item(r):
            lines.append(T("- **Objet probablement inobtenable** (objet de test, stats ou niveau d'objet hors du "
                           "jeu) : ne le conseille pas."))
        if r["sell_price"]:
            lines.append(T("- Prix de vente au marchand : {price}", price=F.money(r['sell_price'])))
        if r["allowable_class"] not in (None, -1, 0):
            lines.append(T("- Réservé à certaines classes (masque {mask})", mask=r['allowable_class']))
        srcs = gdb.sources(r["id"])
        loot = gdb.loot_of(r["id"])
        if srcs or loot:
            lines.append(T("- Sources :"))
            for s in srcs:
                detail = source_detail(s['detail'])
                if s["source_type"] == "artisanat":
                    detail = re.sub(r"\s*\((?:compétence|skill) 1\)", "", detail)
                lines.append(f"  - {source_type(s['source_type'])}{F.sep()}{s['source_name']} — {detail}")
        else:
            char_s, db_s = self._db_char(args)
            qs = self.item_source(gdb, r["id"], self.player_zone_ids(gdb, db_s)) \
                if hasattr(self, "item_source") else ""
            if qs:
                lines.append(T("- Source [Forever · QuestieDB] : {src}", src=qs[3:]))
            else:
                lines.append(T("- Source : non répertoriée dans la base (butin, quête ou marchand). Cherche dans la "
                               "mémoire de recherche puis sur le web."))
        made = gdb.q("SELECT r.*, p.name AS prof FROM recipes r JOIN professions p ON p.id = r.profession_id "
                     "WHERE r.item_id = ?", (r["id"],))
        char0, db0 = self._db_char(args)
        for m in made:
            lines.append(T("- Fabriqué par {prof} : {name} (rang ≈ {rank}{est})", prof=m['prof'], name=m['name'],
                           rank=m['rank_est'], est=T(" estimé") if m['rank_source'] == 'estimation' else ""))
        gap = self.craft_gap_text(self.craft_info(gdb, db0, r["id"])) if made and db0 else ""
        if gap:
            lines.append(T("- Pour toi : {gap}", gap=gap))
        used = gdb.q("SELECT r.name, p.name AS prof FROM recipes r JOIN professions p ON p.id = r.profession_id "
                     "WHERE r.reagents_json LIKE ? LIMIT 8", (f'%"item_id": {r["id"]},%',))
        if used:
            lines.append(T("- Composant de : {list}", list=", ".join(f"{u['name']} ({u['prof']})" for u in used)))
        char, db = self._db_char(args)
        if db and r["inventory_type"] in GDB.INVTYPE and r["inventory_type"] not in (0, 18, 24, 27):
            ev = G.evaluate(db, GDB.to_addon_item(r))
            if ev.get("slot") or ev.get("verdict"):
                txt = G.gain_text(ev)
                lines.append(T("- Pour {name} : {verdict}", name=F.g(db, 'identity', 'name'), verdict=ev['verdict'])
                             + (f" ({txt})" if txt else "") + (f" · {ev['reason']}" if ev.get("reason") else ""))
        if len(rows) > 1:
            lines.append(T("\nAutres objets au nom proche : {list}",
                           list=", ".join(f"{o['name']} (id {o['id']})" for o in rows[1:])))
        return "\n".join(lines)

    # -- artisanat : la recette est-elle à portée du perso ? -------------------------
    @staticmethod
    def player_prof_rank(db: Optional[Dict[str, Any]], prof_name: Any) -> Optional[int]:
        """Rang du perso dans un métier (None si le métier n'est pas appris ou pas capturé)."""
        n = F.norm_key(prof_name)
        for p in as_list(F.g(db or {}, "professions", "professions")):
            if F.norm_key(p.get("name")) == n:
                return int(p.get("rank") or 0)
        return None

    def craft_info(self, gdb: GDB.GameDB, db: Optional[Dict[str, Any]], item_id: int) -> Optional[Dict[str, Any]]:
        """Recette qui fabrique l'objet : {prof, rank, est, have}. have = rang du perso (None si pas le métier)."""
        rows = gdb.q("SELECT r.rank_est, r.min_rank, r.rank_source, p.name AS prof FROM recipes r "
                     "JOIN professions p ON p.id = r.profession_id WHERE r.item_id = ? ORDER BY r.rank_est",
                     (int(item_id),))
        if not rows:
            return None
        r = rows[0]
        rank = r["rank_est"] or (r["min_rank"] if (r["min_rank"] or 0) > 1 else None)
        return {"prof": r["prof"], "rank": rank, "est": r["rank_source"] == "estimation",
                "have": self.player_prof_rank(db, r["prof"])}

    @staticmethod
    def craft_gap_text(ci: Optional[Dict[str, Any]]) -> str:
        """« Travail du cuir ≈150 requis, tu es à 106 » ; vide si la recette est à portée ou inconnue."""
        if not ci or not ci.get("rank"):
            return ""
        if ci["have"] is None:
            return T("{prof} ≈{rank} requis (métier non appris)", prof=ci["prof"], rank=ci["rank"])
        if ci["have"] < ci["rank"]:
            return T("{prof} ≈{rank} requis, tu es à {have}", prof=ci["prof"], rank=ci["rank"], have=ci["have"])
        return ""

    # -- find_upgrades -------------------------------------------------------------
    def upgrade_candidates(self, gdb: GDB.GameDB, db: Dict[str, Any], args: Dict[str, Any]):
        """Calcule les améliorations par emplacement. Renvoie (ranked, ctx) :
        ranked = [(slot, [ev…])] trié par meilleur gain ; ctx = bornes utilisées (niveaux, qualité, équipé)."""
        cls = F.g(db, "identity", "classFile") or ""
        level = int(F.g(db, "progression", "level") or F.g(db, "identity", "level") or 1)
        marge = int(args.get("marge_niveau") or 0)
        lmax = int(args["niveau_max"]) if args.get("niveau_max") is not None else level + marge
        lmin = max(1, lmax - int(args.get("ecart") or 12))
        qmin = self._quality(args.get("qualite_min", 2))
        per_slot = max(1, min(int(args.get("par_emplacement") or 3), 10))
        slots = [self._slot_key(args["emplacement"])] if args.get("emplacement") else GDB.UPGRADE_SLOTS
        class_bit = 1 << (GDB.CLASS_IDS.get(cls, 0) - 1) if cls in GDB.CLASS_IDS else 0
        eq = F.g(db, "equipment", "slots", default={}) or {}
        equipped = {it.get("itemId") for it in eq.values() if isinstance(it, dict)}
        faction = str(F.g(db, "identity", "faction") or "") if db else ""
        out: Dict[str, List[Dict[str, Any]]] = {}
        for slot in slots:
            inv = GDB.SLOT_INVTYPES.get(slot) or []
            rows = gdb.q(f"SELECT * FROM items WHERE inventory_type IN ({','.join('?' * len(inv))}) "
                         f"AND {GDB.EFFECTIVE_REQ_SQL} BETWEEN ? AND ? AND quality >= ? AND quality <= 5",
                         (*inv, lmin, lmax, qmin))
            cands = []
            for r in rows:
                if GDB.is_junk(r) or r["id"] in equipped:
                    continue
                ac = r["allowable_class"]
                if class_bit and ac not in (None, -1, 0) and not (ac & class_bit):
                    continue
                item = GDB.to_addon_item(r)
                if not item["stats"] and not item["dps"]:
                    continue
                req, estimated = GDB.effective_req(r)
                # niveau_max au-delà du niveau du perso : on évalue l'objet au niveau où il deviendra portable
                ev = G.evaluate(db_at_level(db, req) if req > level else db, item)
                if req > level:
                    ev["later"] = req
                if estimated:
                    ev["req_estimated"] = req
                if ev.get("code") not in G.USEFUL:
                    continue
                if ev.get("slot") not in (slot, "Finger1Slot" if slot == "Finger0Slot" else None,
                                          "Trinket1Slot" if slot == "Trinket0Slot" else None):
                    continue
                ev["row"] = r
                if not GDB.plausible_item(r):
                    continue
                if not gdb.sources(r["id"]) and (r["quality"] or 0) >= 3 and (r["req_level"] or 0) <= 1:
                    continue        # épique ou rare de niveau 1 sans source : objet de test ou inobtenable
                if estimated and not gdb.sources(r["id"]) and not (
                        hasattr(self, "item_source") and self.item_source(gdb, r["id"], None, short=True)):
                    continue        # niveau requis absent et aucune source : objet Forever non vérifiable
                if faction and hasattr(self, "other_faction_vendor_only") and not any(
                        s_["source_type"] != "vendeur" for s_ in gdb.sources(r["id"])) \
                        and self.other_faction_vendor_only(gdb, r["id"], faction):
                    continue        # vendu seulement par l'autre faction
                ci = self.craft_info(gdb, db, r["id"]) if any(
                    s_["source_type"] == "artisanat" for s_ in gdb.sources(r["id"])) else None
                ev["craft_gap"] = self.craft_gap_text(ci)
                cands.append(ev)
            cands.sort(key=lambda e: (bool(e.get("later")), bool(e.get("craft_gap")), -e["score"]))
            now = [e for e in cands if not e.get("later")][:per_slot]
            later = [e for e in cands if e.get("later")][:per_slot]
            if now or later:
                out[slot] = now + later
        ranked = sorted(out.items(), key=lambda kv: (bool(kv[1][0].get("later")), bool(kv[1][0].get("craft_gap")),
                                                     -kv[1][0]["score"]))
        return ranked, {"cls": cls, "level": level, "lmin": lmin, "lmax": lmax, "qmin": qmin, "eq": eq}

    def upgrade_line(self, gdb: GDB.GameDB, ev: Dict[str, Any], sources: int = 2) -> str:
        r = ev["row"]
        srcs = gdb.sources(r["id"])
        src = "; ".join(f"{source_type(s['source_type'])}{F.sep()}{s['source_name']}" for s in srcs[:sources])
        if not src and hasattr(self, "item_source"):
            src = self.item_source(gdb, r["id"], None, short=True)[3:]
        src = src or T("source non répertoriée")
        txt = G.gain_text(ev)
        gap = ev.get("craft_gap")
        req, estimated = GDB.effective_req(r)
        req_txt = T("≈{n} (estimé)", n=req) if estimated else req
        later = T(" — **portable au niveau {n}**", n=ev["later"]) if ev.get("later") else ""
        return (T("- {name} (id {id}, {quality}, niv. {req}) — {stats} → {verdict}", name=r['name'],
                  id=r['id'], quality=GDB.quality_name(r['quality']), req=req_txt,
                  stats=GDB.stats_line(r), verdict=ev['verdict'])
                + (f" ({txt})" if txt else "") + f" · {src}" + (f" — **{gap}**" if gap else "") + later)

    def find_upgrades(self, args: Dict[str, Any]) -> str:
        gdb = self.gamedb()
        char, db = self._char(args)
        ranked, c = self.upgrade_candidates(gdb, db, args)
        eq = c["eq"]
        lines = [gdb.header(),
                 T("Améliorations possibles pour **{name}** ({cls}, niveau {level}) — objets de niveau requis {lmin} "
                   "à {lmax}, qualité {quality} ou mieux :", name=F.g(db, 'identity', 'name'),
                   cls=F.g(db, 'identity', 'class') or c["cls"].lower(), level=c["level"], lmin=c["lmin"],
                   lmax=c["lmax"], quality=GDB.quality_name(c["qmin"])), ""]
        if not ranked:
            lines.append(T("Aucune amélioration trouvée dans la base locale avec ces critères "
                           "(élargis avec marge_niveau ou qualite_min)."))
        for slot, evs in ranked:
            cur = eq.get(slot) or (eq.get("Finger1Slot") if slot == "Finger0Slot" else None)
            lines.append(T("**{slot}** (équipé : {name})", slot=F.slot_label(slot),
                           name=(cur or {}).get('name') or T("rien")))
            for ev in evs:
                lines.append(self.upgrade_line(gdb, ev))
            lines.append("")
        lines.append("_" + T("Stats calculées depuis les fichiers du jeu et les correctifs Forever (exactes sur les "
                             "objets vérifiés). Un objet de la base n'est pas forcément obtenable : pour une « source "
                             "non répertoriée », vérifie où il tombe (mémoire de recherche, puis web) avant de "
                             "l'annoncer. Les objets à suffixe aléatoire (« … de l'aigle ») n'ont pas de stats de "
                             "base et sont ignorés. Maîtrises d'armes/armures selon Classic.") + "_")
        return self._head(db, *lines)

    # -- get_dungeon_loot ----------------------------------------------------------
    def get_dungeon_loot(self, args: Dict[str, Any]) -> str:
        gdb = self.gamedb()
        name = args.get("donjon") or ""
        n = F.norm_key(name)
        if not n:
            lines = [gdb.header(), "", T("**Donjons et raids de Forever**, par niveau conseillé :")]
            for kind, label in (("dungeon", T("Donjons (5 joueurs)")), ("raid", T("Raids"))):
                lines.append(f"\n**{label}**")
                for d in sorted((x for x in DG.instances() if x.get("kind") == kind),
                                key=lambda x: (x.get("min") or 0, x.get("max") or 0)):
                    other = d["fr"] if DG.loc(d, "name") == d["en"] else d["en"]
                    lines.append(f"- {DG.loc(d, 'name')} ({other}) — {DG.levels_text(d)} {DG.badge(d)}")
            lines.append("\n_" + T("Les cartes de test et de Season of Discovery présentes dans le client sont "
                                    "masquées. Fourchettes Classic : à vérifier dans Forever.") + "_")
            return "\n".join(lines)
        ref = DG.by_name(name)
        rows = []
        if ref and ref.get("map_id") is not None:
            rows = gdb.q("SELECT * FROM dungeons WHERE map_id = ?", (ref["map_id"],))
        if not rows:
            for pattern in GDB.like_patterns(name):
                rows = [r for r in gdb.q("SELECT * FROM dungeons WHERE name_norm LIKE ? ORDER BY length(name)",
                                         (pattern,)) if not DG.is_test_map(r["name"])]
                if rows:
                    break
        if rows and not ref:
            ref = DG.by_map(rows[0]["map_id"])
        if not rows and not ref:
            raise self.ToolError(T("Donjon « {name} » introuvable. Appelle dungeon sans paramètre pour la liste.",
                                   name=name))
        if not rows:  # donjon Forever connu par la table de référence, absent des fichiers du client
            lines = [gdb.header(), "", T("**{name}** ({en}) — {levels} {badge}", name=DG.loc(ref, "name"),
                                         en=ref["en"] if DG.loc(ref, "name") != ref["en"] else ref["fr"],
                                         levels=DG.levels_text(ref), badge=DG.badge(ref))]
            if ref.get("zone"):
                lines.append(T("- Zone : {zone}", zone=DG.loc(ref, "zone")))
            if ref.get("note"):
                lines.append(f"- {DG.loc(ref, 'note')}")
            gl = self.guide_dungeon_loot(gdb, args, ref, {})
            if gl:
                lines += gl
            else:
                lines.append(T("- Boss et butin : pas dans les fichiers du client. Mémoire de recherche (search), puis "
                               "web ; un export en jeu du Journal des donjons par l'addon est prévu."))
            return "\n".join(lines)
        d = rows[0]
        seen_boss: set = set()
        bosses = []
        for b in gdb.q("SELECT * FROM encounters WHERE map_id = ? ORDER BY order_index, id", (d["map_id"],)):
            k = F.norm_key(b["name"])
            if k and k not in seen_boss:
                seen_boss.add(k)
                bosses.append(b)
        kind = "raid" if d["instance_type"] == 2 else T("donjon")
        title = T("**{name}** ({kind}, carte {map}) {badge}", name=d['name'], kind=kind, map=d['map_id'],
                  badge=GDB.badge())
        lines = [gdb.header(), "", title]
        if ref:
            lines.append(T("- {levels} {badge}", levels=_cap1(DG.levels_text(ref)), badge=DG.badge(ref)))
            if ref.get("note"):
                lines.append(f"- {DG.loc(ref, 'note')}")
        if bosses:
            lines.append(T("Boss ({n}) : {list}", n=len(bosses), list=", ".join(b["name"] for b in bosses)))
        loot = gdb.q("SELECT l.*, i.*, e.name AS boss FROM dungeon_loot l JOIN items i ON i.id = l.item_id "
                     "LEFT JOIN encounters e ON e.id = l.encounter_id WHERE l.map_id = ? "
                     "ORDER BY e.order_index, i.inventory_type", (d["map_id"],))
        if loot:
            char, db = self._db_char(args)
            lines.append("")
            cur_boss = object()
            for r in loot:
                if r["boss"] != cur_boss:
                    lines.append(f"**{r['boss'] or T('Butin commun')}**")
                    cur_boss = r["boss"]
                verdict = ""
                if db:
                    ev = G.evaluate(db, GDB.to_addon_item(r))
                    verdict = f" → {ev['verdict']}" + (f" ({G.gain_text(ev)})" if G.gain_text(ev) else "")
                lines.append(T("- {name} ({slot}, niv. {req}) — {stats}", name=r['name'],
                               slot=GDB.slot_label(r) or GDB.kind_label(r), req=r['req_level'],
                               stats=GDB.stats_line(r)) + verdict)
        else:
            qloot = self.guide_dungeon_loot(gdb, args, ref, {b["id"]: b["name"] for b in bosses}) \
                or self.questie_dungeon_loot(gdb, args, [d["name"]] + ([ref["fr"]] if ref else []),
                                             [b["name"] for b in bosses])
            if qloot:
                lines += qloot
            else:
                lines.append(T("\nButin : **pas dans les fichiers du client Forever** (le Journal des donjons n'y est "
                               "pas rempli). Pour le butin par boss : mémoire de recherche (search_knowledge), puis "
                               "web ; un export en jeu du Journal des donjons par l'addon est prévu."))
        if len(rows) > 1:
            lines.append(T("\nAutres correspondances : {list}", list=", ".join(r["name"] for r in rows[1:6])))
        return "\n".join(lines)

    @staticmethod
    def loot_verdict(db: Optional[Dict[str, Any]], row: Any) -> str:
        """« → amélioration (+1,2 DPS) » ; un objet de niveau trop haut est jugé au niveau requis
        (« → au niveau 28 : amélioration ») au lieu d'un « pas pour toi » qui ne dit rien du butin."""
        if not db:
            return ""
        item = GDB.to_addon_item(row)
        ev = G.evaluate(db, item)
        prefix = ""
        lvl = F.g(db, "progression", "level") or F.g(db, "identity", "level") or 0
        req = item.get("requiredLevel") or 0
        if ev.get("code") == "not_for_you" and isinstance(lvl, int) and req > lvl:
            future = dict(db)
            future["progression"] = dict(db.get("progression") or {}, level=req)
            if isinstance(db.get("identity"), dict):
                future["identity"] = dict(db["identity"], level=req)
            ev2 = G.evaluate(future, item)
            if ev2.get("code") != "not_for_you":
                ev, prefix = ev2, T("au niveau {n} : ", n=req)
        if not ev.get("verdict"):
            return ""
        return f" → {prefix}{ev['verdict']}" + (f" ({G.gain_text(ev)})" if G.gain_text(ev) else "")

    def guide_dungeon_loot(self, gdb: GDB.GameDB, args: Dict[str, Any], ref: Optional[Dict[str, Any]],
                           enc_names: Dict[int, str]) -> List[str]:
        """Butin par boss et mécaniques d'après le guide sourcé de donjons.json (donjons propres à Forever).

        Les itemId du guide sont lus dans la base locale : stats exactes du client, verdict pour le perso."""
        g = DG.guide(ref)
        if not g:
            return []
        from i18n import get_lang
        char, db = self._db_char(args)
        en = get_lang() == "en"
        out = [""]
        ent = g.get("entree")
        if isinstance(ent, dict) and (ent.get("texte") or ent.get("way")):
            text = (ent.get("texte_en") if en else None) or ent.get("texte") or ""
            zone = (ent.get("zone_en") if en else None) or ent.get("zone") or ""
            where = (f" — {zone}" if zone else "") + (f" · `/way {ent['way']}`" if ent.get("way") else "")
            if ent.get("rencontre_way"):
                where += T(" ; pierre de rencontre au pied du chemin `/way {way}`", way=ent["rencontre_way"])
            out.append(T("**Entrée** [Forever · {src}] : {text}", text=text,
                         src=DG.sources_label(ent.get("sources"), ent.get("certitude"))) + where)
        out.append(T("**Butin et mécaniques par boss** [Forever · {src}] — objets lus dans la base locale "
                     "(stats exactes), à confirmer en jeu :", src=DG.guide_source(g)))
        for b in g.get("boss") or []:
            name = b.get("en") or "?"
            local = enc_names.get(b.get("encounter")) if b.get("encounter") else None
            title = name if en or not local else f"{local} ({name})"
            mech = (b.get("mecaniques_en") if en else None) or b.get("mecaniques")
            out.append(f"- **{title}**" + (f" — {mech}" if mech else ""))
            items = []
            for it in b.get("butin") or []:
                row = gdb.item(int(it["id"])) if isinstance(it, dict) and it.get("id") else None
                if row:
                    items.append(row)
                elif isinstance(it, dict) and it.get("en"):
                    out.append(T("  - {name} (id {id}) — absent de la base locale", name=it["en"], id=it.get("id")))
            for it in items:
                verdict = self.loot_verdict(db, it)
                out.append(T("  - {name} ({slot}, {quality}, niv. {req}, id {id}) — {stats}", name=it["name"],
                             slot=GDB.kind_slot(it, ", ") or "?",
                             quality=GDB.quality_name(it["quality"]), req=it["req_level"], id=it["id"],
                             stats=GDB.stats_line(it)) + verdict)
        note = (g.get("note_en") if en else None) or g.get("note")
        if note:
            out.append(f"- {note}")
        dang = g.get("dangers")
        if isinstance(dang, dict) and dang.get("liste"):
            out.append(T("**Dangers hors boss (trash)** [Forever · {src}] :",
                         src=DG.sources_label(dang.get("sources"), dang.get("certitude"))))
            for d in dang["liste"]:
                txt = (d.get("en") if en else None) or d.get("fr") if isinstance(d, dict) else d
                if txt:
                    out.append(f"- {txt}")
        out.append("_" + T("Source : {url}", url=g.get("source") or "?") + "_")
        return out

    def instance_npcs(self, gdb: GDB.GameDB, names: List[str]) -> List[Any]:
        """PNJ QuestieDB d'une instance, d'après la zone (AreaTable) qui porte son nom."""
        if not hasattr(self, "_zone_ids") or not self.has_table(gdb, "q_npcs"):
            return []
        for nm in names:
            zids = self._zone_ids(gdb, nm)
            if zids:
                ph = ",".join("?" * len(zids))
                rows = gdb.q(f"SELECT * FROM q_npcs WHERE zone_id IN ({ph})", tuple(zids))
                if rows:
                    return rows
        return []

    def questie_dungeon_loot(self, gdb: GDB.GameDB, args: Dict[str, Any], names: List[str],
                             boss_names: List[str], per_boss: int = 6) -> List[str]:
        """Butin des boss d'après les drops QuestieDB (listes adaptées de Classic) : objets équipables, notés."""
        npcs = self.instance_npcs(gdb, names)
        wanted = {F.norm_key(b) for b in boss_names if b}

        def is_boss(n: Any) -> bool:
            keys = {F.norm_key(n["name"]), F.norm_key(n["name_loc"])}
            return bool(keys & wanted) or any(k and w and (k.startswith(w) or w.startswith(k))
                                             for k in keys for w in wanted) or (n["rank"] or 0) == 2
        bosses = [n for n in npcs if is_boss(n)]
        # boss des rencontres du client (DungeonEncounter) retrouvés par leur nom dans QuestieDB : la zone QuestieDB
        # d'un PNJ d'instance est souvent vide ou différente de celle de l'AreaTable (Gnomeregan, Zul'Farrak…)
        have = {b["id"] for b in bosses}
        if self.has_table(gdb, "q_npcs"):
            for w in wanted:
                if not w:
                    continue
                for n in gdb.q("SELECT * FROM q_npcs WHERE name_norm = ? OR name_norm LIKE ? OR name_norm LIKE ? "
                               "ORDER BY rank DESC LIMIT 3", (w, w + "|%", "%|" + w)):
                    if n["id"] not in have and (n["friendly"] or "") == "":
                        have.add(n["id"])
                        bosses.append(n)
                        break
        if not bosses:
            return []
        char, db = self._db_char(args)
        out = ["", T("**Butin des boss** [Forever · QuestieDB] — listes de Classic reprises par QuestieDB, à "
                     "confirmer en jeu :")]
        shown = 0
        for b in bosses:
            rows = gdb.q("SELECT q.id, q.npc_drops FROM q_items q WHERE q.npc_drops LIKE ?", (f"%{b['id']}%",))
            ids = [r["id"] for r in rows if b["id"] in _jids(r["npc_drops"]) and len(_jids(r["npc_drops"])) <= 5]
            items = []
            for iid in ids:
                it = gdb.item(iid)
                if (it and it["inventory_type"] in GDB.INVTYPE and it["inventory_type"] not in (0, 18, 24, 27)
                        and (it["quality"] or 0) >= 2 and GDB.plausible_item(it)):
                    items.append(it)
            if not items:
                continue
            items.sort(key=lambda it: (-(it["quality"] or 0), it["inventory_type"]))
            lines = []
            for it in items[:per_boss]:
                verdict = self.loot_verdict(db, it)
                lines.append(T("  - {name} ({slot}, niv. {req}) — {stats}", name=it["name"],
                               slot=GDB.slot_label(it) or GDB.kind_label(it), req=it["req_level"],
                               stats=GDB.stats_line(it)) + verdict)
            out.append(f"- **{b['name_loc'] or b['name']}**" + (T(" (+{n} autres)", n=len(items) - per_boss)
                                                                  if len(items) > per_boss else ""))
            out += lines
            shown += 1
        return out if shown else []

    # -- find_recipes --------------------------------------------------------------
    def find_recipes(self, args: Dict[str, Any]) -> str:
        gdb = self.gamedb()
        metier = args.get("metier") or ""
        char, db = self._db_char(args)
        rank_now = None
        if not metier and db:
            profs = as_list(F.g(db, "professions", "professions"))
            if profs:
                metier = profs[0].get("name") or ""
        if not metier:
            raise self.ToolError(T("Indique le métier (ex. « Travail du cuir »)."))
        profs = []
        pid = PROFESSION_IDS.get(F.norm_key(metier))
        if pid:  # nom du métier dans l'autre langue que celle du jeu : on passe par l'ID
            profs = gdb.q("SELECT p.*, (SELECT count(*) FROM recipes r WHERE r.profession_id = p.id) AS n "
                          "FROM professions p WHERE id = ?", (pid,))
        if not profs or not profs[0]["n"]:
            n = F.norm_key(metier)
            profs = gdb.q("SELECT p.*, (SELECT count(*) FROM recipes r WHERE r.profession_id = p.id) AS n "
                          "FROM professions p WHERE name_norm LIKE ? ORDER BY n DESC", ("%" + n + "%",))
        if not profs or not profs[0]["n"]:
            raise self.ToolError(T("Métier « {name} » introuvable ou sans recette dans la base.", name=metier))
        prof = profs[0]
        if db:
            for p in as_list(F.g(db, "professions", "professions")):
                if p.get("skillLineId") == prof["id"] or F.norm_key(p.get("name")) == prof["name_norm"]:
                    rank_now = p.get("rank")
        rmin = int(args["rang_min"]) if args.get("rang_min") is not None else (max(1, rank_now - 15) if rank_now else 1)
        rmax = int(args["rang_max"]) if args.get("rang_max") is not None else ((rank_now + 45) if rank_now else 300)
        limit = max(1, min(int(args.get("limite") or 40), 120))
        # rang recalculé à la lecture (gamedata/recipe_rank.py), comme le parcours de `professions`
        ranks = PP.profession_ranks(gdb, prof["id"])
        allrows = gdb.q("SELECT r.*, i.name AS item_name, i.quality, i.req_level, i.slot_fr, i.kind, i.stats_json, "
                        "i.class_id, i.subclass_id, i.inventory_type, "
                        "i.armor, i.dps, i.dmg_min, i.dmg_max, i.speed, i.id AS iid, i.origin AS iorigin "
                        "FROM recipes r LEFT JOIN items i ON i.id = r.item_id WHERE r.profession_id = ?",
                        (prof["id"],))
        ranked = []
        for r in allrows:
            rank, src = ranks.get(r["spell_id"], (None, None))
            if not rank:  # logique recalculée sans réponse : valeur de la base
                rank, src = r["rank_est"], r["rank_source"]
            if rank is not None and rmin <= rank <= rmax:
                ranked.append((int(rank), src, r))
        ranked.sort(key=lambda x: (x[0], str(x[2]["name"] or "")))
        rows = ranked[:limit]
        lines = [gdb.header(), "",
                 T("**{prof}** — recettes de rang ≈ {rmin} à {rmax}", prof=prof['name'], rmin=rmin, rmax=rmax)
                 + (T(" (ton rang : {rank})", rank=rank_now) if rank_now else "") + f" {GDB.badge()}", ""]
        if not rows:
            lines.append(T("Aucune recette dans cette tranche."))
        for rank, src, r in rows:
            reag = json.loads(r["reagents_json"] or "[]")
            reag_txt = ", ".join(f"{x['count']} {x.get('name') or x['item_id']}" for x in reag) or "?"
            est = "≈" if src == "estimation" else ""
            forever = " · Forever" if (r["iorigin"] in ("ajoute",) and (r["iid"] or 0) > 200000) else ""
            what = ""
            if r["item_name"]:
                what = f" → {r['item_name']}"
                slot = GDB.slot_label(r)
                if slot:
                    label = GDB.kind_slot(r, " ")
                    what += f" ({label}, " \
                            + T("niv. {n}", n=r['req_level'])
                    st = F.stats_text(F.item_stats(GDB.to_addon_item(r_as_item(r))))
                    what += (f", {st}" if st else "") + ")"
            lines.append(f"- {est}{rank} · **{r['name']}**{what}{forever} — {reag_txt}")
        lines.append("\n_" + T("Rang requis : le client Forever ne le donne presque jamais ; il est repris du "
                                "patron, schéma ou plan qui apprend la recette, ou de l'objet fabriqué quand il "
                                "exige ce métier. Sinon « ≈ » = estimation (5 × niveau de l'objet fabriqué, ou rang "
                                "de ses composants), à confirmer chez le formateur. Une recette rapporte des points tant qu'elle n'est pas grise ; ouvre la "
                                "fenêtre du métier en jeu pour que l'addon capture les couleurs exactes. Les sources "
                                "des recettes (formateur, marchand, butin) ne sont pas dans la base.") + "_")
        return "\n".join(lines)

    # -- enrichissement des autres outils --------------------------------------------
    def enrich_rewards(self, db: Dict[str, Any]) -> int:
        """Complète les stats des récompenses de quête manquantes à partir de la base."""
        gdb = self.gamedb(required=False)
        if not gdb:
            return 0
        n = 0
        for q in as_list(F.g(db, "quests", "list")):
            r = q.get("rewards")
            if not isinstance(r, dict):
                continue
            for kind in ("choices", "items"):
                for it in as_list(r.get(kind)):
                    if not isinstance(it, dict) or not it.get("itemId") or it.get("stats"):
                        continue
                    row = gdb.item(it["itemId"])
                    if not row:
                        continue
                    base = GDB.to_addon_item(row)
                    for k in ("stats", "dps", "classId", "subclassId", "equipLoc", "requiredLevel"):
                        if not it.get(k) and base.get(k):
                            it[k] = base[k]
                    n += 1
        return n

    def overview_upgrades(self, db: Dict[str, Any], limit: int = 4) -> List[str]:
        gdb = self.gamedb(required=False)
        if not gdb:
            return [T("- Base du jeu absente : les pistes d'amélioration (find_upgrades) demandent de la construire "
                      "une fois : `{cmd}`.", cmd=GDB.build_command())]
        try:
            text = self.find_upgrades({"perso": F.g(db, "identity", "name"), "par_emplacement": 1})
        except Exception:
            return []
        picks = [ln for ln in text.splitlines() if ln.startswith("- ") and "→" in ln][:limit]
        if not picks:
            return []
        return [T("\n**Pistes d'amélioration {badge}** (détail : find_upgrades) :", badge=GDB.badge())] + picks

    # -- utilitaires ---------------------------------------------------------------
    def _slot_key(self, raw: str) -> str:
        slot = raw if raw in F.SLOT_FR else F.SLOT_ALIASES.get(F.norm_key(raw))
        if not slot:
            raise self.ToolError(T("Emplacement « {slot} » inconnu. Exemples : tête, cou, distance, main droite, "
                                   "doigt (ou head, neck, ranged, main hand, finger).", slot=raw))
        return slot

    def _quality(self, v: Any) -> int:
        if isinstance(v, int):
            return v
        s = F.norm_key(str(v))
        if s.isdigit():
            return int(s)
        return GDB.QUALITY_ALIASES.get(s, 2)


# Métiers par nom (français et anglais, normalisés) -> SkillLine ID : permet de demander « Leatherworking »
# sur une base construite depuis un client français, et inversement.
PROFESSION_IDS = {
    "travail du cuir": 165, "leatherworking": 165, "depecage": 393, "skinning": 393, "cuisine": 185,
    "cooking": 185, "forge": 164, "blacksmithing": 164, "alchimie": 171, "alchemy": 171, "couture": 197,
    "tailoring": 197, "ingenierie": 202, "engineering": 202, "enchantement": 333, "enchanting": 333,
    "minage": 186, "mining": 186, "herboristerie": 182, "herbalism": 182, "peche": 356, "fishing": 356,
    "secourisme": 129, "first aid": 129,
}


def _jids(v: Any) -> List[int]:
    try:
        x = json.loads(v) if isinstance(v, str) and v else (v or [])
    except ValueError:
        return []
    return [int(i) for i in x if isinstance(i, (int, float))]


def source_type(code: Any) -> str:
    from i18n import L

    return L("source_type", code, code or "?")


def source_detail(text: Any) -> str:
    """Détail d'une source écrit par build.py : « Nom (compétence 75) » -> « Nom (skill 75) » en anglais."""
    s = str(text or "")
    return s.replace("(compétence ", T("(compétence ")) if s else "?"


def r_as_item(r: Any) -> Dict[str, Any]:
    """Ligne recette+objet -> dict compatible avec gamedb.to_addon_item."""
    return {"id": r["iid"], "name": r["item_name"], "class_id": r["class_id"], "subclass_id": r["subclass_id"],
            "inventory_type": r["inventory_type"], "req_level": r["req_level"], "ilvl": None, "quality": r["quality"],
            "dps": r["dps"], "armor": r["armor"], "stats_json": r["stats_json"]}
