"""Outils MCP adossés à la base locale du jeu : find_items, get_item, find_upgrades,
get_dungeon_loot, find_recipes, get_quest_info (lecture seule)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import formats as F
import gamedb as GDB
import gear as G
from luasv import as_list


class GameDBToolsMixin:
    """Mélangé à Tools (server.py) : utilise self.store et self._char."""

    _gdb: Optional[GDB.GameDB] = None
    _gdb_path = None

    # -- accès ---------------------------------------------------------------------
    def gamedb(self, required: bool = True) -> Optional[GDB.GameDB]:
        path = GDB.find_db_path(getattr(self.store, "data_dir", None))
        if path is None:
            if required:
                raise self.ToolError(GDB.MISSING_MSG.format(cmd=GDB.build_command()))
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
            where.append("lower(kind) LIKE ?")
            params.append("%" + F.norm_key(args["type"])[:5] + "%")
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
                                 (*params, limit * 3)) if not GDB.is_junk(r)]
        if stat:
            rows.sort(key=lambda r: -(GDB.stats_of(r).get(stat) or 0))
        rows = rows[:limit]
        if not rows:
            return gdb.header() + "\n\nAucun objet ne correspond à ces critères dans la base locale."
        lines = [gdb.header(), "", f"{len(rows)} objet(s) :", ""]
        for r in rows:
            lines.append(f"- {GDB.item_title(r)} : {GDB.stats_line(r)}")
        lines.append("\n_Détail et sources d'un objet : get_item. La base contient tous les objets définis par le "
                     "client, y compris certains jamais obtenables : vérifie la source avant de conseiller._")
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
            raise self.ToolError("Donne l'itemId ou le nom de l'objet.")
        if not rows:
            raise self.ToolError("Objet introuvable dans la base locale (vérifie l'orthographe, ou cherche avec find_items).")
        r = rows[0]
        lines = [gdb.header(), "", GDB.item_title(r), f"- {GDB.stats_line(r)}",
                 f"- Origine des données : {GDB.origin_note(r)} {GDB.BADGE}"]
        if r["sell_price"]:
            lines.append(f"- Prix de vente au marchand : {F.money(r['sell_price'])}")
        if r["allowable_class"] not in (None, -1, 0):
            lines.append(f"- Réservé à certaines classes (masque {r['allowable_class']})")
        srcs = gdb.sources(r["id"])
        loot = gdb.loot_of(r["id"])
        if srcs or loot:
            lines.append("- Sources :")
            for s in srcs:
                lines.append(f"  - {s['source_type']} : {s['source_name']} — {s['detail']}")
        else:
            lines.append("- Source : non répertoriée dans la base (butin, quête ou marchand). Cherche dans la mémoire "
                         "de recherche puis sur le web.")
        made = gdb.q("SELECT r.*, p.name AS prof FROM recipes r JOIN professions p ON p.id = r.profession_id "
                     "WHERE r.item_id = ?", (r["id"],))
        for m in made:
            lines.append(f"- Fabriqué par {m['prof']} : {m['name']} (rang ≈ {m['rank_est']}"
                         f"{' estimé' if m['rank_source'] == 'estimation' else ''})")
        used = gdb.q("SELECT r.name, p.name AS prof FROM recipes r JOIN professions p ON p.id = r.profession_id "
                     "WHERE r.reagents_json LIKE ? LIMIT 8", (f'%"item_id": {r["id"]},%',))
        if used:
            lines.append("- Composant de : " + ", ".join(f"{u['name']} ({u['prof']})" for u in used))
        char, db = self._db_char(args)
        if db and r["inventory_type"] in GDB.INVTYPE and r["inventory_type"] not in (0, 18, 24, 27):
            ev = G.evaluate(db, GDB.to_addon_item(r))
            if ev.get("slot") or ev.get("verdict"):
                txt = G.gain_text(ev)
                lines.append(f"- Pour {F.g(db, 'identity', 'name')} : {ev['verdict']}"
                             + (f" ({txt})" if txt else "") + (f" · {ev['reason']}" if ev.get("reason") else ""))
        if len(rows) > 1:
            lines.append("\nAutres objets au nom proche : " + ", ".join(f"{o['name']} (id {o['id']})" for o in rows[1:]))
        return "\n".join(lines)

    # -- find_upgrades -------------------------------------------------------------
    def find_upgrades(self, args: Dict[str, Any]) -> str:
        gdb = self.gamedb()
        char, db = self._char(args)
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
        out: Dict[str, List[Dict[str, Any]]] = {}
        for slot in slots:
            inv = GDB.SLOT_INVTYPES.get(slot) or []
            rows = gdb.q(f"SELECT * FROM items WHERE inventory_type IN ({','.join('?' * len(inv))}) "
                         "AND req_level BETWEEN ? AND ? AND quality >= ? AND quality <= 5",
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
                ev = G.evaluate(db, item)
                if ev.get("verdict") not in ("amélioration", "emplacement vide : à équiper",
                                             "léger plus (endurance/armure)"):
                    continue
                if ev.get("slot") not in (slot, "Finger1Slot" if slot == "Finger0Slot" else None,
                                          "Trinket1Slot" if slot == "Trinket0Slot" else None):
                    continue
                ev["row"] = r
                cands.append(ev)
            cands.sort(key=lambda e: -e["score"])
            if cands:
                out[slot] = cands[:per_slot]
        lines = [gdb.header(),
                 f"Améliorations possibles pour **{F.g(db, 'identity', 'name')}** ({cls.lower()}, niveau {level}) — "
                 f"objets de niveau requis {lmin} à {lmax}, qualité {GDB.QUALITY.get(qmin)} ou mieux :", ""]
        if not out:
            lines.append("Aucune amélioration trouvée dans la base locale avec ces critères "
                         "(élargis avec marge_niveau ou qualite_min).")
        ranked = sorted(out.items(), key=lambda kv: -kv[1][0]["score"])
        for slot, evs in ranked:
            cur = eq.get(slot) or (eq.get("Finger1Slot") if slot == "Finger0Slot" else None)
            lines.append(f"**{F.SLOT_FR.get(slot, slot)}** (équipé : {(cur or {}).get('name') or 'rien'})")
            for ev in evs:
                r = ev["row"]
                srcs = gdb.sources(r["id"])
                src = "; ".join(f"{s['source_type']} : {s['source_name']}" for s in srcs[:2]) \
                    or "source non répertoriée"
                txt = G.gain_text(ev)
                lines.append(f"- {r['name']} (id {r['id']}, {GDB.QUALITY.get(r['quality'])}, niv. {r['req_level']}) — "
                             f"{GDB.stats_line(r)} → {ev['verdict']}" + (f" ({txt})" if txt else "")
                             + f" · {src}")
            lines.append("")
        lines.append("_Stats calculées depuis les fichiers du jeu et les correctifs Forever (exactes sur les objets "
                     "vérifiés). Un objet de la base n'est pas forcément obtenable : pour une « source non "
                     "répertoriée », vérifie où il tombe (mémoire de recherche, puis web) avant de l'annoncer. "
                     "Les objets à suffixe aléatoire (« … de l'aigle ») n'ont pas de stats de base et sont ignorés. "
                     "Maîtrises d'armes/armures selon Classic._")
        return self._head(db, *lines)

    # -- get_dungeon_loot ----------------------------------------------------------
    def get_dungeon_loot(self, args: Dict[str, Any]) -> str:
        gdb = self.gamedb()
        name = args.get("donjon") or ""
        n = F.norm_key(name)
        if not n:
            rows = gdb.q("SELECT d.*, (SELECT count(*) FROM encounters e WHERE e.map_id = d.map_id) AS bosses "
                         "FROM dungeons d ORDER BY d.instance_type, d.name")
            lines = [gdb.header(), "", "Donjons et raids connus du client :"]
            for d in rows:
                kind = "raid" if d["instance_type"] == 2 else "donjon"
                lines.append(f"- {d['name']} ({kind}, carte {d['map_id']}, {d['bosses']} boss)")
            return "\n".join(lines)
        rows = gdb.q("SELECT * FROM dungeons WHERE name_norm LIKE ? ORDER BY length(name)",
                     ("%" + "%".join(n.split()) + "%",))
        if not rows:
            raise self.ToolError(f"Donjon « {name} » introuvable dans la base. Appelle get_dungeon_loot sans "
                                 "paramètre pour la liste.")
        d = rows[0]
        bosses = gdb.q("SELECT * FROM encounters WHERE map_id = ? ORDER BY order_index, id", (d["map_id"],))
        kind = "raid" if d["instance_type"] == 2 else "donjon"
        lines = [gdb.header(), "", f"**{d['name']}** ({kind}, carte {d['map_id']}) {GDB.BADGE}"]
        if bosses:
            lines.append("Boss : " + ", ".join(b["name"] for b in bosses))
        loot = gdb.q("SELECT l.*, i.*, e.name AS boss FROM dungeon_loot l JOIN items i ON i.id = l.item_id "
                     "LEFT JOIN encounters e ON e.id = l.encounter_id WHERE l.map_id = ? "
                     "ORDER BY e.order_index, i.inventory_type", (d["map_id"],))
        if loot:
            char, db = self._db_char(args)
            lines.append("")
            cur_boss = object()
            for r in loot:
                if r["boss"] != cur_boss:
                    lines.append(f"**{r['boss'] or 'Butin commun'}**")
                    cur_boss = r["boss"]
                verdict = ""
                if db:
                    ev = G.evaluate(db, GDB.to_addon_item(r))
                    verdict = f" → {ev['verdict']}" + (f" ({G.gain_text(ev)})" if G.gain_text(ev) else "")
                lines.append(f"- {r['name']} ({r['slot_fr'] or r['kind'] or ''}, niv. {r['req_level']}) — "
                             f"{GDB.stats_line(r)}{verdict}")
        else:
            lines.append("\nButin : **pas dans les fichiers du client Forever** (le Journal des donjons n'y est pas "
                         "rempli). Pour le butin par boss : mémoire de recherche (search_knowledge), puis web ; "
                         "un export en jeu du Journal des donjons par l'addon est prévu.")
        if len(rows) > 1:
            lines.append("\nAutres correspondances : " + ", ".join(r["name"] for r in rows[1:6]))
        return "\n".join(lines)

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
            raise self.ToolError("Indique le métier (ex. « Travail du cuir »).")
        n = F.norm_key(metier)
        profs = gdb.q("SELECT p.*, (SELECT count(*) FROM recipes r WHERE r.profession_id = p.id) AS n "
                      "FROM professions p WHERE name_norm LIKE ? ORDER BY n DESC", ("%" + n + "%",))
        if not profs or not profs[0]["n"]:
            raise self.ToolError(f"Métier « {metier} » introuvable ou sans recette dans la base.")
        prof = profs[0]
        if db:
            for p in as_list(F.g(db, "professions", "professions")):
                if F.norm_key(p.get("name")) == prof["name_norm"]:
                    rank_now = p.get("rank")
        rmin = int(args["rang_min"]) if args.get("rang_min") is not None else (max(1, rank_now - 15) if rank_now else 1)
        rmax = int(args["rang_max"]) if args.get("rang_max") is not None else ((rank_now + 45) if rank_now else 300)
        limit = max(1, min(int(args.get("limite") or 40), 120))
        rows = gdb.q("SELECT r.*, i.name AS item_name, i.quality, i.req_level, i.slot_fr, i.kind, i.stats_json, "
                     "i.armor, i.dps, i.dmg_min, i.dmg_max, i.speed, i.id AS iid, i.origin AS iorigin "
                     "FROM recipes r LEFT JOIN items i ON i.id = r.item_id "
                     "WHERE r.profession_id = ? AND r.rank_est BETWEEN ? AND ? ORDER BY r.rank_est, r.name LIMIT ?",
                     (prof["id"], rmin, rmax, limit))
        lines = [gdb.header(), "",
                 f"**{prof['name']}** — recettes de rang ≈ {rmin} à {rmax}"
                 + (f" (ton rang : {rank_now})" if rank_now else "") + f" {GDB.BADGE}", ""]
        if not rows:
            lines.append("Aucune recette dans cette tranche.")
        for r in rows:
            reag = json.loads(r["reagents_json"] or "[]")
            reag_txt = ", ".join(f"{x['count']} {x.get('name') or x['item_id']}" for x in reag) or "?"
            est = "≈" if r["rank_source"] == "estimation" else ""
            forever = " · Forever" if (r["iorigin"] in ("ajoute",) and (r["iid"] or 0) > 200000) else ""
            what = ""
            if r["item_name"]:
                what = f" → {r['item_name']}"
                if r["slot_fr"]:
                    what += f" ({r['kind'] or ''} {r['slot_fr']}, niv. {r['req_level']}"
                    st = F.stats_text(F.item_stats(GDB.to_addon_item(r_as_item(r))))
                    what += (f", {st}" if st else "") + ")"
            lines.append(f"- {est}{r['rank_est']} · **{r['name']}**{what}{forever} — {reag_txt}")
        lines.append("\n_Rang requis : le client Forever ne le fournit pas ; « ≈ » = estimation 5 × niveau de "
                     "l'objet fabriqué (juste sur les recettes Classic vérifiées, à confirmer chez le formateur). "
                     "Une recette rapporte des points tant qu'elle n'est pas grise ; ouvre la fenêtre du métier en "
                     "jeu pour que l'addon capture les couleurs exactes. Les sources des recettes (formateur, "
                     "marchand, butin) ne sont pas dans la base._")
        return "\n".join(lines)

    # -- get_quest_info -------------------------------------------------------------
    def get_quest_info(self, args: Dict[str, Any]) -> str:
        gdb = self.gamedb()
        qid = args.get("questId")
        title = args.get("titre")
        rows = []
        if qid:
            rows = gdb.q("SELECT * FROM quests WHERE id = ?", (int(qid),))
        elif title:
            n = F.norm_key(title)
            rows = gdb.q("SELECT * FROM quests WHERE title_norm LIKE ? ORDER BY length(title) LIMIT 5",
                         ("%" + "%".join(n.split()) + "%",))
        else:
            raise self.ToolError("Donne le questId ou le titre de la quête.")
        char, db = self._db_char(args)
        logq = None
        if db:
            for q in as_list(F.g(db, "quests", "list")):
                if (qid and q.get("questId") == int(qid)) or (title and F.norm_key(title) in F.norm_key(q.get("title"))):
                    logq = q
                    break
        if not rows and not logq:
            raise self.ToolError("Quête inconnue de la base locale (le client ne connaît que les titres des quêtes "
                                 "déjà vues) et absente du journal. Cherche dans la mémoire, puis sur le web.")
        lines = [gdb.header(), ""]
        for r in rows[:3]:
            lines.append(f"**{r['title'] or '(titre inconnu)'}** (id {r['id']}) — {GDB.origin_note(r)} {GDB.BADGE}")
            if r["objectives"]:
                lines.append(f"- Objectif : {F.clean_text(r['objectives'])}")
            if not r["title"]:
                lines.append("- Titre et texte inconnus localement : la quête n'a pas encore été vue en jeu.")
        if logq:
            lines.append(f"\nDans ton journal : **{logq.get('title')}** (niv. {logq.get('level')})"
                         + (" — à rendre" if logq.get("complete") else ""))
            for o in as_list(logq.get("objectives")):
                lines.append(f"- {o.get('text')}" + (" ✔" if o.get("finished") else ""))
        lines.append("\n_Les fichiers du client ne contiennent ni le niveau, ni le donneur, ni les récompenses des "
                     "quêtes : get_quests/get_quest_rewards pour celles du journal, sinon mémoire puis web._")
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
            return ["- Base du jeu absente : les pistes d'amélioration (find_upgrades) demandent de la construire "
                    f"une fois : `{GDB.build_command()}`."]
        try:
            text = self.find_upgrades({"perso": F.g(db, "identity", "name"), "par_emplacement": 1})
        except Exception:
            return []
        picks = [ln for ln in text.splitlines() if ln.startswith("- ") and "→" in ln][:limit]
        if not picks:
            return []
        return [f"\n**Pistes d'amélioration {GDB.BADGE}** (détail : find_upgrades) :"] + picks

    # -- utilitaires ---------------------------------------------------------------
    def _slot_key(self, raw: str) -> str:
        slot = raw if raw in F.SLOT_FR else F.SLOT_ALIASES.get(F.norm_key(raw))
        if not slot:
            raise self.ToolError(f"Emplacement « {raw} » inconnu. Exemples : tête, cou, distance, main droite, doigt.")
        return slot

    def _quality(self, v: Any) -> int:
        if isinstance(v, int):
            return v
        s = F.norm_key(str(v))
        if s.isdigit():
            return int(s)
        return GDB.QUALITY_ALIASES.get(s, 2)


def r_as_item(r: Any) -> Dict[str, Any]:
    """Ligne recette+objet -> dict compatible avec gamedb.to_addon_item."""
    return {"id": r["iid"], "name": r["item_name"], "class_id": None, "subclass_id": None,
            "inventory_type": None, "req_level": r["req_level"], "ilvl": None, "quality": r["quality"],
            "dps": r["dps"], "armor": r["armor"], "stats_json": r["stats_json"]}
