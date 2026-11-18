"""Outils d'intention du serveur MCP (v0.8) : un appel par question courante.

Chaque outil répond à une intention du joueur et fait côté serveur les croisements que l'agent
faisait en plusieurs appels :

- overview     : résumé précalculé à chaque synchro (resume.json dans le dossier du perso) ;
- gear         : équipement + améliorations (récompenses, sacs, base locale) + comparaison d'un objet ;
- quests       : journal, quêtes à rendre, fiche d'une quête, quêtes disponibles ;
- item, npc, dungeon, professions, pet, talents, bags, reputations, characters ;
- search       : recherche globale par nom (FR/EN, avec ou sans accents) dans la base, les notes
                 et les données du perso ; un résultat net renvoie directement sa fiche.

Les anciens outils (get_overview, find_upgrades…) restent appelables : ce module s'appuie sur eux.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import formats as F
import gamedb as GDB
import gear as G
import i18n as I
import knowledge as K
import dungeons as DG
from gamedb_tools import PROFESSION_IDS as PROF_IDS
import professions_plan as PP
from i18n import T
from luasv import as_list
from sync import load_json, write_json

DIGEST_FILE = "resume.json"
DIGEST_VERSION = 2
# Empreinte du code du serveur : un résumé calculé par une version antérieure du code est recalculé.
try:
    from pathlib import Path as _P
    CODE_STAMP = str(int(max(f.stat().st_mtime for f in _P(__file__).resolve().parent.glob("*.py"))))
except (OSError, ValueError):
    CODE_STAMP = "?"
DETAILS = ("court", "normal", "complet")
DETAIL_ALIASES = {"court": "court", "short": "court", "bref": "court", "brief": "court", "normal": "normal",
                  "complet": "complet", "full": "complet", "complete": "complet", "long": "complet",
                  "detail": "complet", "detaille": "complet"}
LIMITS = {"court": {"turnin": 6, "ups": 3, "avail": 3, "per_slot": 1, "slots": 6},
          "normal": {"turnin": 15, "ups": 5, "avail": 6, "per_slot": 1, "slots": 17},
          "complet": {"turnin": 40, "ups": 8, "avail": 12, "per_slot": 3, "slots": 17}}
VOICES = {"joueur": "joueur", "player": "joueur", "pnj": "pnj", "npc": "pnj", "neutre": "neutre",
          "neutral": "neutre"}
VOICE_EN = {"joueur": "player", "pnj": "NPC", "neutre": "neutral"}

# Régime du familier (libellés du jeu, FR/EN) -> mots qui reconnaissent la nourriture dans les sacs.
DIET_WORDS = {
    "viande": ("viande", "cote", "jambon", "cuisse", "steak", "saucisse", "chair", "meat", "chop", "ham", "flank",
               "steak", "sausage", "haunch", "rib"),
    "meat": ("viande", "cote", "jambon", "cuisse", "steak", "saucisse", "chair", "meat", "chop", "ham", "flank",
             "sausage", "haunch", "rib"),
    "poisson": ("poisson", "saumon", "truite", "anguille", "fish", "salmon", "trout", "eel", "snapper", "catfish"),
    "fish": ("poisson", "saumon", "truite", "anguille", "fish", "salmon", "trout", "eel", "snapper", "catfish"),
    "pain": ("pain", "miche", "biscuit", "gateau", "bread", "loaf", "muffin", "cake", "roll"),
    "bread": ("pain", "miche", "biscuit", "gateau", "bread", "loaf", "muffin", "cake", "roll"),
    "fromage": ("fromage", "cheese", "brie", "cheddar"),
    "cheese": ("fromage", "cheese", "brie", "cheddar"),
    "fruit": ("pomme", "melon", "baie", "banane", "apple", "melon", "berry", "banana", "peach", "fruit"),
    "champignon": ("champignon", "mushroom", "morille", "morel", "cap"),
    "fungus": ("champignon", "mushroom", "morille", "morel", "cap"),
}

# boissons et huiles : jamais de la nourriture de familier, même si le nom contient « poisson » ou un fruit
DRINK_WORDS = ("jus", "eau", "lait", "the", "cidre", "vin", "biere", "huile", "juice", "water", "milk", "tea",
               "cider", "wine", "ale", "oil", "potion", "elixir")


def detail_of(args: Dict[str, Any], default: str = "court") -> str:
    return DETAIL_ALIASES.get(F.norm_key(args.get("detail")), default)


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


class IntentToolsMixin:
    """Mélangé à Tools (server.py) : utilise self.store, self._char, les outils historiques et la base locale."""

    # -- voix --------------------------------------------------------------------
    def voice(self) -> str:
        try:
            cfg = self.store.config
        except Exception:
            return "joueur"
        return VOICES.get(F.norm_key(cfg.get("voix") or cfg.get("voice")), "joueur")

    def voice_label(self) -> str:
        v = self.voice()
        return VOICE_EN.get(v, v) if I.get_lang() == "en" else v

    # -- characters --------------------------------------------------------------
    def tool_characters(self, args: Dict[str, Any]) -> str:
        action = F.norm_key(args.get("action"))
        if action in ("activer", "active", "set active", "set", "choisir", "select"):
            return self.set_active_character(args)
        if action in ("comparer", "compare"):
            return self.compare_characters(args)
        if action in ("rattacher", "register", "nommer", "name"):
            return self.register_account(args)
        return self.list_characters(args)

    # -- overview (résumé précalculé) --------------------------------------------
    def tool_overview(self, args: Dict[str, Any]) -> str:
        vue = F.norm_key(args.get("vue") or args.get("view"))
        if vue in ("fiche", "sheet", "character", "perso"):
            return self.get_character(args)
        if vue in ("stats", "statistiques"):
            return self.get_stats(args)
        if vue in ("progres", "progress", "progression") or args.get("depuis") or args.get("niveau_cible"):
            return self.get_progress(args)
        char, db = self._char(args)
        detail = detail_of(args)
        digest = self.digest(char, db)
        body = (digest.get("text", {}).get(I.get_lang()) or {}).get(detail) or ""
        head = F.header(db) + T(" · voix : {voice}", voice=self.voice_label())
        rep = F.g(db, "meta", "repairedFromPrevious")
        if rep:
            head += "\n_" + T("Note : {domains} repris de la capture précédente (valeurs vides à la déconnexion).",
                              domains=", ".join(rep)) + "_"
        return body.replace("{HEAD}", head, 1)

    def digest_key(self, db: Dict[str, Any], char: Optional[Dict[str, Any]] = None) -> str:
        gdb = self.gamedb(required=False)
        gpart = ""
        if gdb:
            try:
                gpart = f"{gdb.path.name}:{int(gdb.path.stat().st_mtime)}"
            except OSError:
                gpart = gdb.path.name
        mem = self.memory_mtime(char, db) if char else 0
        return (f"{DIGEST_VERSION}|{getattr(self, 'server_version', '?')}|{CODE_STAMP}|{F.captured_at(db)}|"
                f"{gpart}|{mem}")

    def digest(self, char: Dict[str, Any], db: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        """Résumé du perso (resume.json dans son dossier), recalculé si la capture ou la base ont changé."""
        path = self.store.folder(char) / DIGEST_FILE
        key = self.digest_key(db, char)
        if not force:
            cached = load_json(path, {}) if path.exists() else {}
            if cached.get("key") == key and cached.get("text"):
                return cached
        texts: Dict[str, Dict[str, str]] = {}
        for lang in I.SUPPORTED:
            with I.using(lang):
                sec = self.digest_sections(db, char)
                texts[lang] = {d: self.render_digest(sec, d) for d in DETAILS}
        data = {"version": DIGEST_VERSION, "key": key, "builtAt": int(time.time()),
                "capturedAt": F.captured_at(db), "text": texts}
        try:
            write_json(path, data)
        except OSError:
            pass
        return data

    def refresh_digests(self, updated: List[str]) -> List[str]:
        """Appelé après une synchro : recalcule le résumé des persos mis à jour ("user/dossier")."""
        done = []
        for c in self.store.characters():
            if f"{c.get('user')}/{c.get('folder')}" not in updated:
                continue
            db = self.store.load(c)
            if not db:
                continue
            saved = (self._locale, self._pre)
            try:
                self._locale, self._pre = F.game_locale(db), (c.get("guid"), db)
                self.digest(c, db, force=True)
                done.append(f"{c.get('user')}/{c.get('folder')}")
            finally:
                self._locale, self._pre = saved
        return done

    def digest_sections(self, db: Dict[str, Any], char: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calcule tout ce que le résumé affiche, dans la langue courante (listes complètes, coupées au rendu)."""
        self.enrich_rewards(db)
        mem = self.quest_memory(char, db)
        q = F.g(db, "quests", default={})
        qlist = as_list(q.get("list"))
        done = [x for x in qlist if x.get("complete")]
        cls = F.g(db, "identity", "classFile") or ""
        sec: Dict[str, Any] = {"turnin": [], "ups": [], "avail": [], "state": [], "next": [], "issues": [],
                               "verdict_parts": []}
        # quêtes à rendre, groupées par zone, avec la meilleure récompense
        groups: Dict[str, List[str]] = {}
        turnin_ups = 0
        for x in done:
            best = G.best_choice(db, x["rewards"])[0] if isinstance(x.get("rewards"), dict) else None
            turnin_ups += 1 if best else 0
            groups.setdefault(x.get("category") or T("Autres"), []).append(
                f"{x.get('title')}" + self.turnin_where(db, x, mem) + (f" → {G.reward_pick(best)}" if best else ""))
        sec["turnin"] = sorted(groups.items(), key=lambda kv: -len(kv[1]))
        # améliorations : récompenses des quêtes en cours, objets des sacs, base locale
        ups: List[Tuple[float, str]] = []
        for qq, r in G.quest_rewards(db):
            if qq.get("complete"):
                continue
            best = G.best_choice(db, r)[0]
            if best:
                ups.append((best["score"], T("finir *{quest}* (niv. {n}) → {pick}", quest=qq.get("title"),
                                             n=qq.get("level"), pick=G.reward_pick(best))))
        for score, line, _ev in self.bag_upgrades(db):
            ups.append((score + 0.5, line))  # déjà en main : passe devant à gain égal
        gdb = self.gamedb(required=False)
        if gdb:
            try:
                ranked, _ = self.upgrade_candidates(gdb, db, {"par_emplacement": 3})
                for slot, evs in ranked:
                    # résumé : seulement les objets dont on connaît la source (les autres sont dans gear)
                    ev = next((e for e in evs if gdb.sources(e["row"]["id"])), None)
                    if ev:
                        ups.append((ev["score"], self.upgrade_line(gdb, ev, sources=1)[2:]))
            except Exception:
                pass
        ups.sort(key=lambda x: -x[0])
        sec["ups"] = [line for _, line in ups]
        # quêtes disponibles dans la zone (QuestieDB)
        zone = F.g(db, "position", "zone")
        qdb = self.questdb(required=False) if gdb else None
        if qdb and zone:
            try:
                avail, _later, zids, ctx, _a, _b = self.available_quests(qdb, db, {})
                sec["avail"] = [self.quest_line(qdb, x, zids, ctx)[2:] for x in avail]
                sec["avail_zone"] = self.zone_name(qdb, zids[0])
                sec["avail"] += self.observed_offers(qdb, db, mem, ctx, skip={x["id"] for x in avail})
            except Exception:
                pass
        # état : sacs, munitions, familier, métiers
        b = F.g(db, "bags", default={}) or {}
        free = b.get("freeSlots")
        ammo = F.g(b, "ammo", "total")
        bag_line = T("Sacs : {free} place(s) libre(s) sur {total}", free=free if free is not None else "?",
                     total=b.get("totalSlots", "?"))
        if ammo is not None and F.g(db, "stats", "ranged", "usesAmmo") is not False and cls == "HUNTER":
            bag_line += T(" · munitions {n}", n=F.num(ammo))
        sec["state"].append(bag_line + " · " + T("argent {money}", money=F.money(F.g(db, "money", "copper"))))
        pet_low = False
        if cls == "HUNTER" and F.g(db, "pet", "hasPetUI") is not False:
            p = F.g(db, "pet", "current") if F.g(db, "pet", "active") else None
            if p:
                hap = F.g(p, "happiness", "level")
                pet_low = isinstance(hap, int) and hap < 3
                food = self.pet_food_in_bags(db, p)
                sec["state"].append(
                    T("Familier : {name} niv. {level}, {mood}", name=p.get("name"), level=p.get("level"),
                      mood=I.L("happiness", hap, "?"))
                    + (T(" · nourriture en sacs : {list}", list=", ".join(food)) if food
                       else T(" · aucune nourriture adaptée en sacs ({diet})",
                              diet=", ".join(as_list(p.get("food"))) or "?")))
        for pr in as_list(F.g(db, "professions", "professions")):
            rank, mx = pr.get("rank") or 0, pr.get("max") or 0
            line = f"{pr.get('name')} {rank}/{mx}"
            if mx and mx < 300 and rank >= mx - 10:
                line += T(" — palier bientôt atteint : rang suivant chez le formateur")
            sec.setdefault("profs", []).append(line)
        if sec.get("profs"):
            sec["state"].append(T("Métiers : {list}", list=" · ".join(sec["profs"])))
        # prochaine étape
        p = F.g(db, "progression", default={}) or {}
        level = p.get("level") or 0
        if level and p.get("maxLevel") and level < p["maxLevel"]:
            left = (p.get("xpMax") or 0) - (p.get("xp") or 0)
            sec["next"].append(T("{left} XP avant le niveau {n}", left=F.num(left), n=level + 1)
                               + (T(" (repos : {n})", n=F.num(p.get("xpRested"))) if p.get("xpRested") else ""))
            if level % 2 == 1:
                sec["next"].append(T("au niveau {n}, passe chez ton maître de classe (nouveaux rangs) "
                                     "[Classic · probable]", n=level + 1))
            else:
                sec["next"].append(T("niveau pair : nouveaux rangs de sorts chez ton maître de classe "
                                     "[Classic · probable]"))
        sec["issues"] = F.problems(db)
        # verdict (une ligne)
        parts = sec["verdict_parts"]
        full = q.get("count") and q.get("count") == q.get("max")
        if done:
            where = ", ".join(f"{z} {len(v)}" for z, v in sec["turnin"][:2])
            parts.append((T("rends ta quête terminée ({where})", where=where) if len(done) == 1 else
                          T("rends tes {n} quêtes terminées ({where})", n=len(done), where=where))
                         + ((T(" : elle donne une amélioration") if len(done) == 1 else
                             T(", dont {n} avec une amélioration", n=turnin_ups)) if turnin_ups else ""))
        if full:
            parts.append(T("ton journal est plein : termine ou abandonne avant d'en prendre d'autres"))
        if isinstance(free, int) and free <= 3:
            parts.append(T("fais de la place dans tes sacs"))
        if pet_low:
            parts.append(T("nourris ton familier"))
        if cls == "HUNTER" and isinstance(ammo, int) and ammo < 200:
            parts.append(T("rachète des munitions"))
        if not done and not full and sec["avail"]:
            parts.append(T("prends les quêtes de {zone} ({n} pour ton niveau)", zone=sec.get("avail_zone"),
                           n=len(sec["avail"])))
        if not parts and sec["next"]:
            parts.append(T("continue à monter : {next}", next=sec["next"][0]))
        if not parts:
            parts.append(T("rien d'urgent : choisis ton prochain objectif"))
        return sec

    def render_digest(self, sec: Dict[str, Any], detail: str) -> str:
        lim = LIMITS[detail]
        parts = sec["verdict_parts"][:3]
        lines = ["**" + T("Verdict :") + "** " + _cap("; ".join(parts)) + ".", "{HEAD}", ""]
        if sec["next"]:
            lines.append(T("**Prochaine étape** : {list}.", list="; ".join(sec["next"])))
        if sec["turnin"]:
            lines.append(T("\n**Quêtes à rendre**"))
            shown = 0
            for zone, qs in sec["turnin"]:
                if shown >= lim["turnin"]:
                    break
                take = qs[:lim["turnin"] - shown]
                shown += len(take)
                lines.append(f"- **{zone}** ({len(qs)}) : " + " ; ".join(take)
                             + (T(" ; et {n} autres", n=len(qs) - len(take)) if len(qs) > len(take) else ""))
            total = sum(len(v) for _, v in sec["turnin"])
            if total > shown:
                lines.append(T("- … {n} autres quêtes à rendre (quests a_rendre:true).", n=total - shown))
        if sec["ups"]:
            lines.append(T("\n**Améliorations à portée**"))
            lines += [f"- {u}" for u in sec["ups"][:lim["ups"]]]
        if sec["avail"]:
            lines.append(T("\n**Quêtes à prendre dans {zone}** [Forever · QuestieDB]", zone=sec.get("avail_zone")))
            lines += [f"- {a}" for a in sec["avail"][:lim["avail"]]]
            if len(sec["avail"]) > lim["avail"]:
                lines.append(T("- … et {n} autres (quests disponibles:true).", n=len(sec["avail"]) - lim["avail"]))
        if sec["state"]:
            lines.append(T("\n**État**"))
            lines += [f"- {s}" for s in sec["state"]]
        if sec["issues"] and detail != "court":
            lines.append(T("- Données non lues : {list}", list=F.semi().join(sec["issues"])))
        if detail == "court":
            lines.append("\n_" + T("Détail : gear, quests, professions, pet ; overview detail:complet pour tout.")
                         + "_")
        return "\n".join(lines)

    # -- croisements communs -----------------------------------------------------
    def _bag_items(self, db: Dict[str, Any], bank: bool = False) -> List[Dict[str, Any]]:
        out = []
        for dom in ("bags", "bank") if bank else ("bags",):
            for c in (F.g(db, dom, "containers", default={}) or {}).values():
                out += [it for it in as_list(c.get("items")) if isinstance(it, dict)]
        return out

    def bag_upgrades(self, db: Dict[str, Any]) -> List[Tuple[float, str, Dict[str, Any]]]:
        """Équipements déjà dans les sacs qui amélioreraient le perso (stats lues dans la base locale)."""
        gdb = self.gamedb(required=False)
        out = []
        seen = set()
        for it in self._bag_items(db, bank=True):
            if it.get("classId") not in (2, 4) or it.get("itemId") in seen:
                continue
            seen.add(it.get("itemId"))
            item = dict(it)
            if gdb and it.get("itemId") and not it.get("stats"):
                row = gdb.item(it["itemId"])
                if row:
                    item.update({k: v for k, v in GDB.to_addon_item(row).items() if v})
            if not item.get("stats") and not item.get("dps"):
                continue
            ev = G.evaluate(db, item)
            if ev.get("code") in G.USEFUL:
                txt = G.gain_text(ev)
                ev["line"] = T("**{name}** déjà dans tes sacs → {verdict}", name=item.get("name"),
                               verdict=ev["verdict"]) + (f" ({txt})" if txt else "") + f" [{ev.get('slot_label')}]"
                out.append((ev["score"], ev["line"], ev))
        return sorted(out, key=lambda x: -x[0])

    def quest_item_uses(self, db: Dict[str, Any]) -> Dict[str, str]:
        """Objets que le journal de quêtes demande : nom normalisé → titre de la quête (objectifs « Nom : x/y »
        ou objet cité dans le texte d'un objectif)."""
        out: Dict[str, str] = {}
        names = {F.norm_key(it.get("name")): it.get("name") for it in self._bag_items(db, bank=True) if it.get("name")}
        for q in as_list(F.g(db, "quests", "list")):
            for o in as_list(q.get("objectives")):
                txt = str(o.get("text") or "") if isinstance(o, dict) else str(o)
                head = F.norm_key(re.split(r"\s*[:：]\s*\d", txt.replace("\xa0", " "), maxsplit=1)[0])
                low = F.norm_key(txt)
                for n in names:
                    if n and (n == head or (len(n) > 5 and n in low)):
                        out.setdefault(n, q.get("title") or "?")
        return out

    def pet_food_in_bags(self, db: Dict[str, Any], pet: Dict[str, Any]) -> List[str]:
        """Nourriture des sacs que le familier mange : plats (0/5) et viandes crues (7/8), triés par efficacité.

        Le type vient de la classe d'objet de la base locale (viande crue = 7/8), puis du nom pour les plats ;
        boissons et huiles exclues. Efficacité [Classic] : objet de niveau ≥ niveau du familier − 10 = plein effet,
        jusqu'à − 30 effet réduit, en dessous le familier refuse.
        """
        diets = {F.norm_key(d) for d in as_list(pet.get("food"))}
        diets = {"viande" if d == "meat" else "poisson" if d == "fish" else d for d in diets}
        words = {d: set(DIET_WORDS.get(d, ())) for d in diets}
        fish = set(DIET_WORDS["poisson"])
        gdb = self.gamedb(required=False)
        plvl = pet.get("level") if isinstance(pet.get("level"), int) else None
        found: Dict[str, List[Any]] = {}
        keep = self.quest_item_uses(db)
        self.pet_food_kept = sorted({f"{it.get('name')} ({keep[F.norm_key(it.get('name'))]})"
                                     for it in self._bag_items(db) if F.norm_key(it.get("name")) in keep
                                     and it.get("classId") in (0, 7)})
        for it in self._bag_items(db):
            if it.get("classId") not in (0, 7) or F.norm_key(it.get("name")) in keep:
                continue
            row = gdb.item(it["itemId"]) if gdb and it.get("itemId") else None
            cls = (row["class_id"], row["subclass_id"]) if row else (it.get("classId"), it.get("subClassId"))
            name = F.norm_key(it.get("name"))
            toks = name.split()
            if any(w in toks for w in DRINK_WORDS):
                continue
            if cls == (7, 8):
                kind = "poisson" if any(w in toks for w in fish) else "viande"
                ok = kind in diets
            elif cls[0] == 0 and cls[1] in (5, None):
                ok = any(any(w in toks or name.startswith(w) for w in ws) for ws in words.values())
            else:
                ok = False
            if not ok:
                continue
            ilvl = row["ilvl"] if row else it.get("itemLevel")
            e = found.setdefault(it.get("name"), [0, ilvl])
            e[0] += it.get("count") or 1
        out = []
        for n, (c, ilvl) in sorted(found.items(), key=lambda x: -(x[1][1] or 0)):
            tag = ""
            if plvl and isinstance(ilvl, int):
                if ilvl < plvl - 30:
                    tag = T(" (niv. {n} : il n'en veut plus)", n=ilvl)
                elif ilvl < plvl - 10:
                    tag = T(" (niv. {n} : peu efficace)", n=ilvl)
            out.append(f"{n} ×{c}{tag}")
        return out

    # -- gear ----------------------------------------------------------------------
    STAT_KEYS = {"dps": "dps", "agilite": "agilite", "agility": "agilite", "agi": "agilite", "force": "force",
                 "strength": "force", "str": "force", "endurance": "endurance", "stamina": "endurance",
                 "sta": "endurance", "intelligence": "intelligence", "intellect": "intelligence",
                 "int": "intelligence", "esprit": "esprit", "spirit": "esprit", "pa": "pa", "ap": "pa",
                 "attack power": "pa", "pa distance": "pa_distance", "rap": "pa_distance",
                 "ranged attack power": "pa_distance", "armure": "armure", "armor": "armure",
                 "degats min": "degats_min", "min damage": "degats_min", "degats max": "degats_max",
                 "max damage": "degats_max", "vitesse": "vitesse", "speed": "vitesse",
                 "niveau requis": "niveau_requis", "required level": "niveau_requis",
                 "type arme": "type_arme", "weapon type": "type_arme", "type": "type_arme"}

    def tool_gear(self, args: Dict[str, Any]) -> str:
        obj = args.get("objet") if args.get("objet") is not None else args.get("nom")
        if obj is not None or args.get("itemId") or args.get("stats"):
            return self._gear_compare(args, obj)
        char, db = self._char(args)
        detail = detail_of(args)
        lim = LIMITS[detail]
        gdb = self.gamedb(required=False)
        lines: List[str] = []
        slot = self._slot_key(args["emplacement"]) if args.get("emplacement") else None
        eq = F.g(db, "equipment", "slots", default={}) or {}
        best_action: Optional[str] = None
        # récompenses de quête (à rendre d'abord) et sacs
        self.enrich_rewards(db)
        quest_ups = []
        for qq, r in G.quest_rewards(db):
            best = G.best_choice(db, r)[0]
            if best and (not slot or best.get("slot") == slot):
                quest_ups.append((qq, best))
        quest_ups.sort(key=lambda x: (not x[0].get("complete"), -x[1]["score"]))
        bag_ups = [b for b in self.bag_upgrades(db) if not slot or b[2].get("slot") == slot]
        if slot:
            cur = eq.get(slot)
            lines.append(T("**{slot}** — équipé : {item}", slot=F.slot_label(slot),
                           item=f"{cur.get('name')} ({G.describe(cur)})" if cur else T("rien")))
        elif detail == "court":
            worn = []
            for s, lab in F.slots_localized():
                it = eq.get(s)
                if it and s not in ("ShirtSlot", "TabardSlot"):
                    worn.append(f"{lab} {it.get('name')}" + (f" ({F.num(it['dps'], 1)} DPS)" if it.get("dps") else ""))
            lines.append(T("Équipé : {list}", list=" · ".join(worn) or T("rien")))
            empty = G.empty_slots(db)
            if empty:
                lines.append(T("Vides : {list} (vide ne veut pas dire faible : rien à conseiller sans objet précis).",
                               list=", ".join(empty)))
        else:
            lines += F.render_equipment_table(db, show_tooltip=detail == "complet")
        if quest_ups:
            lines.append(T("\n**Par les quêtes** (à rendre d'abord)"))
            for qq, best in quest_ups[:lim["ups"]]:
                state = T(" ✔ à rendre") if qq.get("complete") else T(" (en cours)")
                lines.append(f"- *{qq.get('title')}*{state}{G.quest_where(qq)} → {G.reward_pick(best)}")
            q0, b0 = quest_ups[0]
            best_action = (T("rends *{quest}* pour **{item}**", quest=q0.get("title"), item=b0["item"].get("name"))
                           if q0.get("complete") else
                           T("termine *{quest}* pour **{item}**", quest=q0.get("title"), item=b0["item"].get("name"))) \
                + (f" ({G.gain_text(b0)})" if G.gain_text(b0) else "")
        if bag_ups:
            lines.append(T("\n**Déjà dans tes sacs**"))
            lines += [f"- {ln}" for _, ln, _ev in bag_ups[:lim["ups"]]]
            if not best_action:
                ev = bag_ups[0][2]
                best_action = T("équipe **{item}**, déjà dans tes sacs ({slot}, {gain})", item=ev.get("name"),
                                slot=ev.get("slot_label"), gain=G.gain_text(ev) or ev["verdict"])
        if gdb:
            a = {"par_emplacement": 3 if slot else lim["per_slot"]}
            for k in ("niveau_max", "marge_niveau", "qualite_min"):
                if args.get(k) is not None:
                    a[k] = args[k]
            if slot:
                a["emplacement"] = slot
            ranked, c = self.upgrade_candidates(gdb, db, a)
            lines.append(T("\n**Dans la base locale** (niveau requis {lmin}-{lmax}) {badge}", lmin=c["lmin"],
                           lmax=c["lmax"], badge=GDB.badge()))
            if not ranked:
                lines.append(T("- Rien de mieux que ton équipement à ce niveau."))
            sourced, unknown, later = [], [], []
            for s_, evs in ranked[:lim["slots"]]:
                for ev in evs:
                    if ev.get("later"):
                        later.append(ev)
                        continue
                    has_src = gdb.sources(ev["row"]["id"]) or self.item_source(gdb, ev["row"]["id"], None, short=True)
                    (sourced if has_src else unknown).append(ev)
            if not (sourced or unknown) and later:
                lines.append(T("- Rien de mieux à ton niveau actuel."))
            lines += [self.upgrade_line(gdb, ev, sources=1) for ev in sourced]
            if unknown:
                if sourced:
                    lines.append(T("- Source inconnue (à vérifier avant d'en parler) :"))
                keep = unknown if detail == "complet" else unknown[:3]
                lines += [("  " if sourced else "") + self.upgrade_line(gdb, ev, sources=1) for ev in keep]
                if len(unknown) > len(keep):
                    lines.append(T("  - … et {n} autres (detail:complet).", n=len(unknown) - len(keep)))
            if later:
                later.sort(key=lambda e: (e["later"], -e["score"]))
                lines.append(T("\n**Plus tard** (niveau {a} à {b})", a=c["level"] + 1, b=c["lmax"]))
                keep_l = later if detail == "complet" else later[:max(3, lim["ups"])]
                lines += [self.upgrade_line(gdb, ev, sources=1) for ev in keep_l]
                if len(later) > len(keep_l):
                    lines.append(T("  - … et {n} autres (detail:complet).", n=len(later) - len(keep_l)))
            if (sourced or unknown or later) and not best_action:
                ev = (sourced or unknown or later)[0]
                srcs = gdb.sources(ev["row"]["id"])
                best_action = (T("vise **{item}** au niveau {n} ({slot}, {gain})", item=ev["row"]["name"],
                                 n=ev["later"], slot=ev.get("slot_label"), gain=G.gain_text(ev) or ev["verdict"])
                               if ev.get("later") else
                               T("vise **{item}** ({slot}, {gain})", item=ev["row"]["name"],
                                 slot=ev.get("slot_label"), gain=G.gain_text(ev) or ev["verdict"])) \
                    + (f" — {srcs[0]['source_name']}" if srcs else T(" — source à vérifier"))
            lines.append("_" + T("Objets de la base pas forcément obtenables : « source non répertoriée » = vérifier où "
                                 "il tombe avant de l'annoncer. Maîtrises d'armes et d'armures selon Classic.") + "_")
        else:
            lines.append(T("\n_Base du jeu absente : pistes d'amélioration limitées aux quêtes et aux sacs. "
                           "Construis-la une fois : `{cmd}`._", cmd=GDB.build_command()))
        verdict = best_action or (T("rien de mieux en vue pour cet emplacement") if slot else
                                  T("ton équipement est à jour pour ton niveau"))
        return "**" + T("Verdict :") + "** " + _cap(verdict) + ".\n" + self._head(db, *lines)

    def _gear_compare(self, args: Dict[str, Any], obj: Any) -> str:
        a: Dict[str, Any] = {k: args[k] for k in ("perso", "emplacement", "itemId") if args.get(k) is not None}
        stats = args.get("stats") if isinstance(args.get("stats"), dict) else {}
        for k, v in stats.items():
            key = self.STAT_KEYS.get(F.norm_key(k))
            if key and v is not None:
                a[key] = v
        if obj is not None and not a.get("itemId"):
            if isinstance(obj, int) or str(obj).strip().isdigit():
                a["itemId"] = int(obj)
            else:
                a["nom"] = str(obj)
                has_stats = any(a.get(k) is not None for k in ("dps", "agilite", "force", "endurance", "intelligence",
                                                                "esprit", "pa", "pa_distance", "armure"))
                if not has_stats:
                    iid = self._item_id_by_name(args, str(obj))
                    if iid:
                        a["itemId"] = iid
        text = self.compare_item(a)
        # verdict de compare_item remonté en première ligne, comme les autres outils
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            if ln.startswith("**") and ln.endswith("**") and i < 4:
                verdict = ln.strip("*").strip().rstrip(".")
                del lines[i]
                if i < len(lines) and i > 0 and not lines[i].strip() and not lines[i - 1].strip():
                    del lines[i]
                return "**" + T("Verdict :") + "** " + verdict + ".\n" + "\n".join(lines)
        return text

    def _item_id_by_name(self, args: Dict[str, Any], name: str) -> Optional[int]:
        char, db = self._db_char(args)
        n = F.norm_key(name)
        for it in (self._bag_items(db, bank=True) if db else []):
            if F.norm_key(it.get("name")) == n and it.get("itemId"):
                return int(it["itemId"])
        gdb = self.gamedb(required=False)
        if gdb:
            rows = gdb.items_by_name(name, 1)
            if rows:
                return int(rows[0]["id"])
        return None

    # -- item ----------------------------------------------------------------------
    def tool_item(self, args: Dict[str, Any]) -> str:
        filters = ("emplacement", "type", "niveau_min", "niveau_max", "qualite_min", "stat", "forever_seulement")
        if any(args.get(k) not in (None, "", False) for k in filters) or args.get("liste"):
            return self.find_items(args)
        return self.get_item(args)

    # -- quests --------------------------------------------------------------------
    def tool_quests(self, args: Dict[str, Any]) -> str:
        if args.get("questId") or args.get("quete") or args.get("titre"):
            a = {"questId": args.get("questId"), "titre": args.get("quete") or args.get("titre"),
                 "perso": args.get("perso")}
            return self.get_quest_info({k: v for k, v in a.items() if v is not None})
        detail = detail_of(args)
        vue = F.norm_key(args.get("vue"))  # alias tolérés : vue:disponibles, vue:a_rendre
        if vue in ("disponibles", "disponible", "available"):
            args = dict(args, disponibles=True)
        elif vue in ("a rendre", "turn ins", "turnins"):
            args = dict(args, a_rendre=True)
        if args.get("disponibles"):
            a = {k: args[k] for k in ("zone", "niveau_min", "niveau_max", "perso") if args.get(k) is not None}
            a["limite"] = LIMITS[detail]["avail"] * 3 if "limite" not in args else args["limite"]
            text = self.find_quests(a)
            n, later = getattr(self, "last_available", (0, 0))
            verdict = (T("1 quête à prendre") if n == 1 else T("{n} quêtes à prendre", n=n) if n else
                       T("rien à prendre pour ton niveau, d'autres quêtes plus tard") if later else
                       T("aucune quête connue ici dans QuestieDB (couverture partielle pour Forever)"))
            return "**" + T("Verdict :") + "** " + _cap(verdict) + ".\n" + text
        if args.get("a_rendre") or detail == "complet":
            a = {k: args[k] for k in ("zone", "perso") if args.get(k) is not None}
            if args.get("a_rendre"):
                a["a_rendre"] = True
            char, db = self._char(args)
            self.enrich_rewards(db)
            if not G.quest_rewards(db):
                # Récompenses pas encore capturées : on garde le journal, la note passe en pied.
                return self._quests_short(args)
            return self._quests_verdict(args) + self.get_quest_rewards(a) + self._quests_xp_footer(args)
        if detail == "normal":
            return self._quests_verdict(args) + self.get_quests(args) + self._quests_xp_footer(args)
        return self._quests_short(args)

    def _quests_xp_footer(self, args: Dict[str, Any]) -> str:
        """Totaux d'XP du journal et quêtes grises, ajoutés aux vues détaillées (get_quests, get_quest_rewards)."""
        char, db = self._char(args)
        lst = as_list(F.g(db, "quests", "list"))
        if args.get("zone"):
            z = F.norm_key(args["zone"])
            lst = [q for q in lst if z in F.norm_key(q.get("category")) or z in F.norm_key(q.get("title"))]
        if args.get("a_rendre"):
            lst = [q for q in lst if q.get("complete")]
        lines = self.journal_xp_lines(db, lst)
        return ("\n" + "\n".join(lines)) if lines else ""

    def _quests_verdict(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        qs = F.g(db, "quests", default={})
        lst = as_list(qs.get("list"))
        if args.get("zone"):
            z = F.norm_key(args["zone"])
            lst = [q for q in lst if z in F.norm_key(q.get("category")) or z in F.norm_key(q.get("title"))]
        return "**" + T("Verdict :") + "** " + _cap(self._quests_verdict_text(qs, lst)) + ".\n"

    @staticmethod
    def _quests_verdict_text(qs: Dict[str, Any], lst: List[Dict[str, Any]]) -> str:
        done = [q for q in lst if q.get("complete")]
        verdict = (T("rends ta quête terminée") if len(done) == 1 else
                   T("rends tes {n} quêtes terminées", n=len(done)) if done else
                   T("aucune quête à rendre : avance les quêtes en cours"))
        if qs.get("count") and qs.get("count") == qs.get("max"):
            verdict += T(" ; journal plein")
        return verdict

    def _quests_short(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        self.enrich_rewards(db)
        qs = F.g(db, "quests", default={})
        lst = as_list(qs.get("list"))
        if args.get("zone"):
            z = F.norm_key(args["zone"])
            lst = [q for q in lst if z in F.norm_key(q.get("category")) or z in F.norm_key(q.get("title"))]
        plevel = F.g(db, "progression", "level")
        trivial = qs.get("trivialRange", 6)
        done = [q for q in lst if q.get("complete")]
        full = qs.get("count") and qs.get("count") == qs.get("max")
        verdict = self._quests_verdict_text(qs, lst)
        lines = [T("Journal : {n}/{max} quêtes", n=qs.get("count", len(lst)), max=qs.get("max", "?"))
                 + (T(" — **journal plein**, impossible d'en prendre d'autres") if full else "")]
        if done:
            lines.append(T("\n**À rendre ({n})**", n=len(done)))
            for q in done:
                best = G.best_choice(db, q["rewards"])[0] if isinstance(q.get("rewards"), dict) else None
                lines.append(f"- **{q.get('title')}** ({q.get('category') or '?'}){self.turnin_where(db, q)}"
                             + self.journal_xp_tag(db, q) + (f" → {G.reward_pick(best)}" if best else ""))
        groups: Dict[str, List[str]] = {}
        for q in lst:
            if q.get("complete"):
                continue
            groups.setdefault(q.get("category") or T("Autres"), []).append(
                f"{q.get('title')} ({q.get('level')}, {F.quest_color(q.get('level'), plevel, trivial)}"
                f"{self.journal_xp_tag(db, q)})" + self.turnin_where(db, q))
        if groups:
            lines.append(T("\n**En cours**"))
            for cat, items in groups.items():
                lines.append(f"- **{cat}** : " + " ; ".join(items))
        lines += self.journal_xp_lines(db, lst)
        if args.get("zone") and not lst:
            lines.append(T("Aucune quête du journal ne correspond à « {zone} ».", zone=args["zone"]))
        if G.quest_rewards(db):
            lines.append("\n_" + T("Objectifs et récompenses : quests detail:normal ; une quête : quests "
                                     "quete:<titre>.") + "_")
        else:
            lines.append("\n_" + T("Récompenses : pas capturées pour ce perso (addon antérieur à 1.2), donc pas "
                                     "de notation possible : synchronise en jeu avec l'addon à jour. Objectifs : quests "
                                     "detail:normal ; une quête : quests quete:<titre>.") + "_")
        return "**" + T("Verdict :") + "** " + _cap(verdict) + ".\n" + self._head(db, *lines)

    # -- npc -----------------------------------------------------------------------
    def tool_npc(self, args: Dict[str, Any]) -> str:
        return self.find_npc(args)

    # -- bags ----------------------------------------------------------------------
    def tool_bags(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        lines = F.render_inventory(db, include_bank=args.get("banque", True))
        ups = self.bag_upgrades(db)
        if ups:
            lines.append(T("\n**À équiper**"))
            lines += [f"- {ln}" for _, ln, _ev in ups[:5]]
        grey = [it for it in self._bag_items(db) if it.get("quality") == 0]
        if grey:
            lines.append(T("\n**À vendre (gris)** : {list}", list=", ".join(
                f"{it.get('name')} ×{it.get('count') or 1}" for it in grey[:12])))
        uses = self.quest_item_uses(db)
        qitems, orphans = [], []
        for it in self._bag_items(db):
            n = F.norm_key(it.get("name"))
            if n in uses:
                qitems.append(f"{it.get('name')} → {uses[n]}")
            elif it.get("classId") == 12:
                orphans.append(it.get("name"))
        if qitems:
            lines.append(T("\n**Pour tes quêtes en cours** : {list}", list=", ".join(dict.fromkeys(qitems))))
        if orphans:
            lines.append(T("**Objets de quête qu'aucun objectif du journal ne cite** (à rendre, à utiliser ou "
                           "début de quête : vérifie avant de jeter) : {list}", list=", ".join(dict.fromkeys(orphans))))
        return self._head(db, "_" + T("Sacs capturés {age}.", age=F.domain_age(db, 'bags')) + "_", *lines)

    # -- professions ---------------------------------------------------------------
    def tool_professions(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        lines = F.render_professions(db, with_recipes=False)
        wanted = args.get("metier")
        profs = as_list(F.g(db, "professions", "professions"))
        prof = None
        if wanted:
            n = F.norm_key(wanted)
            pid = PROF_IDS.get(n)
            prof = next((p for p in profs if p.get("skillLineId") == pid or F.norm_key(p.get("name")) == n), None)
        elif profs:
            prof = next((p for p in profs if str(p.get("slot", "")).startswith("primary")), profs[0])
        counts: Dict[int, int] = {}
        for it in self._bag_items(db, bank=True):
            if it.get("itemId"):
                counts[it["itemId"]] = counts.get(it["itemId"], 0) + (it.get("count") or 1)
        name = (prof or {}).get("name") or wanted
        rank = (prof or {}).get("rank")
        captured = (F.g(db, "recipes", default={}) or {}).get(name) if name else None
        if captured:
            recs = as_list(captured.get("recipes"))
            ups = [r for r in recs if r.get("learned") and (r.get("difficulty") is not None) and r["difficulty"] < 3]
            ups.sort(key=lambda r: r.get("difficulty", 9))
            lines.append(T("\n**{prof} : recettes connues qui rapportent encore des points** (couleurs du jeu, "
                           "capturées {age})", prof=name, age=F.age(captured.get("capturedAt"))))
            for r in ups[:12]:
                lines.append(f"- {r.get('name')} ({I.L('recipe_color', r.get('difficulty'), '?')})"
                             + (T(" · faisable maintenant") if r.get("craftable") else ""))
            if not ups:
                lines.append(T("- Aucune : toutes tes recettes sont grises, il en faut de nouvelles."))
        gdb = self.gamedb(required=False)
        tier_verdict = None
        if gdb and name:
            if args.get("rang_min") is not None or args.get("rang_max") is not None:
                try:  # liste brute des recettes d'une tranche de rang (demande explicite)
                    a = {"metier": name, "perso": args.get("perso"), "limite": 12,
                         **{k: args[k] for k in ("rang_min", "rang_max") if args.get(k) is not None}}
                    body = [ln for ln in self.find_recipes(a).splitlines()[2:] if ln.strip()]
                    if detail_of(args) != "complet":
                        body = [ln for ln in body if not ln.startswith("_")]
                    lines.append("")
                    lines += [self._mark_reagents(ln, gdb, counts) if ln.startswith("- ") else ln for ln in body]
                except Exception as exc:
                    if not isinstance(exc, self.ToolError):
                        raise
            pid = (prof or {}).get("skillLineId") or PROF_IDS.get(F.norm_key(name)) or PP.profession_id(gdb, name)
            if pid:  # paliers, formateurs et parcours de montée (professions_plan.py)
                more, tier_verdict = PP.professions_report(self, gdb, db, pid, name, prof, counts, args, captured)
                lines += more
        if tier_verdict:
            verdict = tier_verdict
            if captured and any(r.get("craftable") and r.get("learned") and (r.get("difficulty") or 3) < 3
                                for r in as_list(captured.get("recipes"))):
                verdict += " ; " + T("tu peux monter {prof} tout de suite avec ce que tu as en sacs", prof=name)
        elif rank and (prof or {}).get("max") and rank >= prof["max"] - 10 and prof["max"] < 300:
            verdict = T("{prof} {rank}/{max} : va chez le formateur prendre le rang suivant", prof=name, rank=rank,
                        max=prof["max"])
        elif captured and any(r.get("craftable") and r.get("learned") and (r.get("difficulty") or 3) < 3
                              for r in as_list(captured.get("recipes"))):
            verdict = T("tu peux monter {prof} tout de suite avec ce que tu as en sacs", prof=name)
        elif wanted and not prof:
            wpid = PROF_IDS.get(F.norm_key(wanted)) or (PP.profession_id(gdb, wanted) if gdb else None)
            verdict = PP.not_learned_verdict(F.g(db, "identity", "name"), wanted,
                                             bool(gdb) and PP.is_gathering(gdb, wpid))
        elif name:
            verdict = (T("{prof} {rank} : récolte les composants des prochaines recettes", prof=name, rank=rank)
                       if rank else T("{prof} : récolte les composants des prochaines recettes", prof=name))
        else:
            verdict = T("aucun métier capturé")
        if wanted and not prof:  # deux métiers principaux déjà appris : à dire en premier
            conflict = PP.primary_conflict(gdb, PROF_IDS.get(F.norm_key(wanted)) or (
                PP.profession_id(gdb, wanted) if gdb else None), profs)
            if conflict:
                verdict = conflict + " ; " + verdict
        return "**" + T("Verdict :") + "** " + _cap(verdict) + ".\n" + self._head(
            db, "_" + T("Métiers capturés {age}.", age=F.domain_age(db, 'professions')) + "_", *lines)

    @staticmethod
    def _mark_reagents(line: str, gdb: GDB.GameDB, counts: Dict[int, int]) -> str:
        """Ajoute « (tu en as N) » derrière les composants présents dans les sacs ou la banque."""
        if not counts:
            return line
        import re
        names = []
        for iid, n in counts.items():
            row = gdb.item(iid)
            if row and row["name"]:
                names.append((row["name"], n))
        # Nom complet seulement (« 4 Peau légère traitée » ne marque pas « Peau légère »).
        for name, n in sorted(names, key=lambda x: -len(x[0])):
            line = re.sub(r"(?<=\d )" + re.escape(name) + r"(?=,|$)",
                          lambda m: m.group(0) + " " + T("(tu en as {n})", n=n), line, count=1)
        return line

    # -- pet -----------------------------------------------------------------------
    def tool_pet(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        text = self.get_pet(args)
        p = F.g(db, "pet", "current") if F.g(db, "pet", "active") else None
        if not p:
            return text
        food = self.pet_food_in_bags(db, p)
        hap = F.g(p, "happiness", "level")
        extra = [T("- Nourriture adaptée dans tes sacs : {list}", list=", ".join(food)) if food else
                 T("- Aucune nourriture adaptée dans tes sacs (régime : {diet}) : achète-en chez un aubergiste ou "
                   "un vendeur de nourriture.", diet=", ".join(as_list(p.get("food"))) or "?")]
        kept = getattr(self, "pet_food_kept", None)
        if kept:
            extra.append(T("- Gardés pour une quête du journal (ne les donne pas) : {list}", list=", ".join(kept)))
        tp = F.g(p, "trainingPoints", "available")
        m = re.search(r"(\d+)", str(p.get("loyalty") or ""))
        if m and isinstance(p.get("level"), int):
            loy = int(m.group(1))
            line = T("- Points de dressage = niveau × (loyauté − 1) = {lvl} × {k} = {n}",
                     lvl=p["level"], k=loy - 1, n=p["level"] * (loy - 1))
            line += T(" (loyauté au maximum)") if loy >= 6 else T(" ; +{n} par rang de loyauté gagné", n=p["level"])
            extra.append(line)
        if hap == 3:
            verdict = T("{name} est heureux ({pct} % de dégâts)", name=p.get("name"),
                        pct=F.g(p, "happiness", "damagePct", default="?"))
        else:
            verdict = T("nourris {name} : il n'est pas heureux, il perd des dégâts et de la loyauté",
                        name=p.get("name"))
        if tp:
            verdict += T(" ; {n} points de dressage à dépenser", n=tp)
        return "**" + T("Verdict :") + "** " + _cap(verdict) + ".\n" + text + "\n" + "\n".join(extra)

    # -- talents -------------------------------------------------------------------
    def tool_talents(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        text = self.get_talents(args)
        if args.get("sorts") or args.get("ligne") or detail_of(args) == "complet":
            spells = self.get_spells(args)
            text += "\n\n" + "\n".join(spells.splitlines()[1:])
        free = sum(int(c.get("available") or 0) for c in as_list(F.g(db, "talents", "currencies"))
                   if isinstance(c, dict))
        if free == 1:
            verdict = T("1 point de talent à dépenser")
        elif free:
            verdict = T("{n} points de talent à dépenser", n=free)
        else:
            verdict = T("aucun point de talent libre pour l'instant")
        if not args.get("arbre"):
            text += "\n_" + T("Arbre complet (talents disponibles, bloqués, rangées) : arbre:true.") + "_"
        return "**" + T("Verdict :") + "** " + _cap(verdict) + ".\n" + text

    # -- dungeon -------------------------------------------------------------------
    def tool_dungeon(self, args: Dict[str, Any]) -> str:
        text = self.get_dungeon_loot(args)
        name = args.get("donjon")
        if not name:
            return text
        char, db = self._db_char(args)
        ref = DG.by_name(name)
        names = {F.norm_key(name)} | (ref["_names"] if ref else set())
        extra: List[str] = []
        qrange: Optional[Tuple[int, int]] = None
        logq: List[Dict[str, Any]] = []
        gdb = self.questdb(required=False)
        zids: List[int] = []
        rows: List[Any] = []
        if gdb:
            try:
                for nm in [name] + ([ref["fr"]] if ref else []):
                    zids = self._zone_ids(gdb, nm)
                    if zids:
                        break
                if zids:
                    ph = ",".join("?" * len(zids))
                    rows = gdb.q(f"SELECT * FROM q_quests WHERE zone_id IN ({ph}) ORDER BY level", tuple(zids))
            except Exception:
                rows = []
        # quêtes dont un objectif vise un PNJ de l'instance (ou un objet qu'il laisse tomber), où qu'on les prenne
        if gdb and (rows or ref):
            try:
                inst = self.instance_npcs(gdb, [name] + ([ref["fr"]] if ref else []))
                have = {r["id"] for r in rows}
                lo = (ref or {}).get("min") or min([r["level"] for r in rows if r["level"]] or [1])
                hi = (ref or {}).get("max") or max([r["level"] for r in rows if r["level"]] or [60])
                for r in self.quests_targeting(gdb, {n["id"] for n in inst}):
                    if r["id"] not in have and lo - 4 <= (r["level"] or lo) <= hi + 4:
                        rows.append(r)
                        have.add(r["id"])
            except Exception:
                pass
        dungeon_qids = {r["id"] for r in rows}
        if db:
            for q in as_list(F.g(db, "quests", "list")):
                cat = F.norm_key(q.get("category"))
                qid = q.get("id") or q.get("questId")
                if (cat and any(x and x in cat for x in names)) or qid in dungeon_qids \
                        or (gdb and qid and self._chain_reaches(gdb, int(qid), dungeon_qids)):
                    logq.append(q)
            if logq:
                extra.append(T("\n**Dans ton journal pour ce donjon** (chaînes comprises) : {list}", list=", ".join(
                    f"{q.get('title')}" + (T(" ✔ à rendre") if q.get("complete") else "") for q in logq)))
        lv = [r["level"] for r in rows if r["level"]]
        if lv:
            qrange = (min(lv), max(lv))
            extra.append(T("- Niveau des quêtes du donjon : {a}-{b} [Forever · QuestieDB]", a=min(lv), b=max(lv)))
        if db and rows:
            try:
                from questdb_tools import QuestCtx
                ctx = QuestCtx(db)
                ok, seen_ok = [], set()
                for r in rows:
                    st = ctx.status(r["id"])
                    if st in ("done", "log", "complete"):
                        continue
                    start = self.chain_start(gdb, r, ctx)
                    if start is not None and start["id"] not in seen_ok and self.available(start, ctx):
                        seen_ok.add(start["id"])
                        ok.append(start)
                if (ref or {}).get("kind") == "raid":
                    # raid : seules comptent les quêtes données par un PNJ ou un objet du monde ; une quête lancée
                    # par un objet de butin (guide, feuille…) n'a rien à voir avec l'accès
                    ok = [r for r in ok if _jids(r["start_npcs"]) or _jids(r["start_objects"])]
                if ok:
                    extra.append(T("- Quêtes à prendre avant d'y aller (début de chaîne compris) :"))
                    extra += ["  " + self.quest_line(gdb, r, zids, ctx).lstrip() for r in ok[:6]]
            except Exception:
                pass
        acc = (ref or {}).get("acces_quetes") or {}
        if acc and gdb:
            extra += self.access_chain_lines(gdb, db, acc)
        extra += self.guide_quest_lines(gdb, db, ref)
        bugs = []
        for q in logq + [{"title": r["name_loc"] or r["name"], "id": r["id"]} for r in rows]:
            b = K.quest_bug(q.get("title"), quest_id=q.get("id") or q.get("questId"))
            if b and b not in bugs:
                bugs.append(b)
        for b in bugs:
            extra.append(T("- Problème connu (au {date}) : *{quest}* — {problem} ({status})", date=b["date"],
                           quest=b["label"], problem=b["problem"], status=b["status"]))
        lvl = F.g(db, "progression", "level") if db else None
        if db:
            extra.append(T("- Ton niveau : {n}. Équipement et améliorations : gear.", n=lvl))
        return self._dungeon_verdict(text, lvl, qrange, ref) + text + ("\n" + "\n".join(extra) if extra else "")

    def guide_quest_lines(self, gdb: Optional[GDB.GameDB], db: Optional[Dict[str, Any]],
                          ref: Optional[Dict[str, Any]]) -> List[str]:
        """Quêtes d'un donjon propre à Forever d'après le guide sourcé (donjons.json) : absentes de QuestieDB.
        Donneur placé par QuestieDB (nom anglais) quand il y est, sinon le lieu donné par le guide (le lieu du
        guide est toujours celui du DONNEUR). Le rendu est affiché à part : guide, journal du perso, mémoire des
        quêtes, QuestieDB (end_npcs)."""
        g = DG.guide(ref)
        if not g or not g.get("quetes"):
            return []
        en = I.get_lang() == "en"
        faction = str(F.g(db, "identity", "faction") or "") if db else ""
        ctx = None
        if db:
            try:
                from questdb_tools import QuestCtx
                ctx = QuestCtx(db)
            except Exception:
                ctx = None
        out = [T("- Quêtes du donjon [Forever · {src}] (nom anglais du guide quand le titre en jeu n'est pas "
                 "connu) :", src=DG.guide_source(g))]
        for q in g["quetes"]:
            fac = str(q.get("faction") or "")
            if faction and fac and faction not in fac:
                continue
            place = (q.get("lieu_en") if en else None) or q.get("lieu") or ""
            who = ""
            giver = q.get("donneur_en") or ""
            if giver and gdb:
                try:
                    rows = gdb.q("SELECT * FROM q_npcs WHERE name = ? ORDER BY spawn_count DESC", (giver,))
                except Exception:
                    rows = []
                if rows:
                    loc = self.where(gdb, "npc", rows[0]["id"], max_zones=1)
                    who = f"**{self.label(rows[0])}**" + (f" — {loc[0]}" if loc else (f" — {place}" if place else ""))
            if not who:
                who = (f"**{giver}** — " if giver else "") + place
            note = (q.get("note_en") if en else None) or q.get("note")
            title = f"*{q['en']}*" if en or not q.get("fr") else f"*{q['fr']}* ({q['en']})"
            jq = None
            if q.get("id") and db:
                for x in as_list(F.g(db, "quests", "list")):
                    if (x.get("id") or x.get("questId")) == q["id"]:
                        jq = x
                        title += T(" ✔ à rendre") if x.get("complete") else T(" (dans ton journal)")
                        break
            line = f"  - {title}" + (f" ({fac})" if not faction and fac else "") \
                + (T(" — donneur : {who}", who=who) if giver else f" — {who}")
            obj = (q.get("objectif_en") if en else None) or q.get("objectif")
            if obj:
                line += T(" · objectif : {text}", text=obj)
            pre = self.guide_prereq(gdb, q.get("prerequis"), ctx)
            if pre:
                line += pre
            turnin = self.guide_turnin(gdb, db, q, jq)
            if turnin:
                line += T(" · **rendu** : {where}", where=turnin)
            nxt = (q.get("suite_en") if en else None) or q.get("suite")
            if nxt:
                line += T(" · suite : {text}", text=nxt)
            out.append(line + (f" · {note}" if note else ""))
        return out if len(out) > 1 else []

    def guide_prereq(self, gdb: Optional[GDB.GameDB], pre: Any, ctx: Any) -> str:
        """« · prérequis : *Les peaux de jeune crocilisque* (484) ✔ faite » d'après l'id QuestieDB du guide."""
        if not isinstance(pre, dict) or not (pre.get("id") or pre.get("en")):
            return ""
        name = pre.get("en") or ""
        if pre.get("id") and gdb:
            try:
                name = self.quest_title(gdb, int(pre["id"])) or name
            except Exception:
                pass
        st = ctx.status(int(pre["id"])) if ctx and pre.get("id") else None
        state = {"done": T(" ✔ faite"), "log": T(" (dans ton journal)"),
                 "complete": T(" ✔ à rendre")}.get(st or "", "")
        return T(" · prérequis : *{name}*", name=name) + (f" ({pre['id']})" if pre.get("id") else "") + state

    def guide_turnin(self, gdb: Optional[GDB.GameDB], db: Optional[Dict[str, Any]], q: Dict[str, Any],
                     jq: Optional[Dict[str, Any]]) -> str:
        """Rendu d'une quête de guide, distinct du donneur. Ordre : receveur vu en jeu (mémoire des quêtes) ou
        QuestieDB (end_npcs), texte du guide, puis le point du journal du perso (quête finie) ou celui du guide."""
        en = I.get_lang() == "en"
        parts: List[str] = []
        qid = q.get("id")
        seen = ""
        if qid and db:
            try:
                if jq and jq.get("complete"):
                    seen = self.turnin_where(db, jq).lstrip(" ·")
                else:
                    mem = self.quest_memory(None, db)
                    mq = (mem.get("quests") or {}).get(str(qid)) or {}
                    for a in mq.get("ends") or []:
                        if a.get("via") == "turnin":
                            seen = self._actor_turnin(gdb, a, mem, db).lstrip(" ·")
                            if seen:
                                break
            except Exception:
                seen = ""
        if not seen and qid and gdb:
            try:
                rows = gdb.q("SELECT * FROM q_quests WHERE id = ?", (int(qid),))
                who = self.actor_line(gdb, rows[0], "end") if rows else []
                if who:
                    seen = T("à rendre à {who}", who=who[0])
            except Exception:
                pass
        text = (q.get("rendu_en") if en else None) or q.get("rendu")
        if text:
            parts.append(text)
        if seen:
            # le journal donne le prochain point de passage : pour une quête finie dans une instance, l'entrée
            parts.append(seen if seen.startswith(T("à rendre à {who}", who="").strip()) else T("point du jeu (ton journal) : {where}",
                                                                          where=seen))
        elif q.get("rendu_way"):
            zone = (q.get("rendu_zone_en") if en else None) or q.get("rendu_zone") or ""
            parts.append((f"{zone} · " if zone else "") + f"`/way {q['rendu_way']}`")
        return " ; ".join(parts)

    def access_chain_lines(self, gdb: GDB.GameDB, db: Optional[Dict[str, Any]],
                           acc: Dict[str, Any]) -> List[str]:
        """Chaîne d'harmonisation d'un raid (début, fin, nombre d'étapes), pour la faction du perso ou les deux."""
        faction = str(F.g(db, "identity", "faction") or "") if db else ""
        keys = [faction] if faction in acc else list(acc)
        out = [T("- **Chaîne d'harmonisation** (par personnage) [Forever · QuestieDB] :")]
        try:
            from questdb_tools import QuestCtx
            ctx = QuestCtx(db) if db else None
        except Exception:
            ctx = None
        for fac in keys:
            ch = acc[fac]
            first = gdb.q("SELECT * FROM q_quests WHERE id = ?", (ch["debut"],))
            last = gdb.q("SELECT * FROM q_quests WHERE id = ?", (ch["fin"],))
            if not first:
                continue
            start_line = self.quest_line(gdb, first[0], [], ctx).lstrip().lstrip("- ") if ctx else \
                (first[0]["name_loc"] or first[0]["name"])
            end_name = (last[0]["name_loc"] or last[0]["name"]) if last else "?"
            done = bool(ctx and ctx.status(ch["fin"]) == "done")
            out.append(T("  - {faction} : {n} étapes environ. Départ : {start}. Aboutit à *{end}* (id {id}){done}",
                         faction=fac, n=ch.get("etapes", "?"), start=start_line, end=end_name, id=ch["fin"],
                         done=T(" ✔ faite") if done else ""))
        return out if len(out) > 1 else []

    def quests_targeting(self, gdb: GDB.GameDB, npc_ids: set) -> List[Any]:
        """Quêtes QuestieDB dont un objectif vise un de ces PNJ, ou un objet qu'ils laissent tomber."""
        if not npc_ids:
            return []
        key = str(gdb.path)
        cache = getattr(self, "_objective_index", None)
        if not cache or cache[0] != key:
            idx = []
            for r in gdb.q("SELECT id, objectives_json FROM q_quests WHERE objectives_json IS NOT NULL"):
                try:
                    o = json.loads(r["objectives_json"]) or {}
                except ValueError:
                    continue
                crea = {int(c[0]) for c in o.get("creatures", []) if c and c[0]}
                for kc in o.get("killcredit", []):
                    if kc and len(kc) > 1 and kc[1]:
                        crea.add(int(kc[1]))
                items = {int(i[0]) for i in o.get("items", []) if i and i[0]}
                idx.append((r["id"], crea, items))
            cache = (key, idx)
            self._objective_index = cache
        drops: Dict[int, set] = {}
        out_ids = set()
        for qid, crea, items in cache[1]:
            if crea & npc_ids:
                out_ids.add(qid)
                continue
            for iid in items:
                if iid not in drops:
                    rr = gdb.q("SELECT npc_drops FROM q_items WHERE id = ?", (iid,))
                    drops[iid] = set(_jids(rr[0]["npc_drops"])) if rr else set()
                inside = drops[iid] & npc_ids
                if inside and len(inside) * 2 >= len(drops[iid]):  # objet surtout lâché dans l'instance
                    out_ids.add(qid)
                    break
        if not out_ids:
            return []
        ph = ",".join("?" * len(out_ids))
        return gdb.q(f"SELECT * FROM q_quests WHERE id IN ({ph}) ORDER BY level", tuple(out_ids))

    def chain_start(self, gdb: GDB.GameDB, q: Any, ctx: Any, depth: int = 8) -> Optional[Any]:
        """Premier maillon pas encore fait de la chaîne qui mène à cette quête (elle-même si aucun)."""
        cur = q
        for _ in range(depth):
            pre = [p for p in _jids(cur["pre_single"]) + _jids(cur["pre_group"]) if ctx.status(p) != "done"]
            if not pre:
                return cur
            rows = gdb.q("SELECT * FROM q_quests WHERE id = ?", (pre[0],))
            if not rows:
                return cur
            if ctx.status(pre[0]) in ("log", "complete"):
                return None  # la chaîne est déjà en cours dans le journal
            cur = rows[0]
        return cur

    def _chain_reaches(self, gdb: GDB.GameDB, qid: int, targets: set, depth: int = 6) -> bool:
        """Vrai si la chaîne de la quête (suite, quêtes qui l'ont en prérequis) mène à une quête du donjon."""
        if not targets:
            return False
        frontier, seen = [qid], {qid}
        for _ in range(depth):
            nxt = []
            for q in frontier:
                rows = gdb.q("SELECT next_in_chain FROM q_quests WHERE id = ?", (q,))
                cand = [rows[0]["next_in_chain"]] if rows and rows[0]["next_in_chain"] else []
                cand += [r["id"] for r in gdb.q(
                    "SELECT id FROM q_quests WHERE pre_single LIKE ? OR pre_group LIKE ?", (f"%{q}%", f"%{q}%"))
                    if q in _int_ids(r)]
                for c in cand:
                    if c in targets:
                        return True
                    if c not in seen:
                        seen.add(c)
                        nxt.append(c)
            frontier = nxt
            if not frontier:
                break
        return False

    @staticmethod
    def _dungeon_verdict(text: str, lvl: Any, qrange: Optional[Tuple[int, int]],
                         ref: Optional[Dict[str, Any]] = None) -> str:
        import re
        m = re.search(r"^\*\*(.+?)\*\* \(", text, re.M)
        name = (DG.loc(ref, "name") if ref else None) or (m.group(1) if m else "")
        if not name:
            return ""
        if ref and ref.get("min") is not None:
            verdict = DG.verdict(ref, lvl, name)
        elif qrange and isinstance(lvl, int):
            a, b = qrange
            verdict = T("{name} : quêtes niv. {a}-{b}, toi {lvl} : niveau du donjon inconnu, vise le niveau des "
                        "quêtes", name=name, a=a, b=b, lvl=lvl)
        else:
            verdict = T("{name} : donjon de groupe, niveau conseillé inconnu de la base", name=name)
        return "**" + T("Verdict :") + "** " + verdict + ".\n"

    # -- reputations ---------------------------------------------------------------
    def tool_reputations(self, args: Dict[str, Any]) -> str:
        return self.get_reputations(args)

    # -- search --------------------------------------------------------------------
    def tool_search(self, args: Dict[str, Any]) -> str:
        text = (args.get("texte") or args.get("query") or args.get("nom") or args.get("question") or "").strip()
        if not text:
            raise self.ToolError(T("Indique le nom ou les mots à chercher."))
        kind_filter = F.norm_key(args.get("type"))
        limit = max(1, min(int(args.get("limite") or 8), 30))
        n = F.norm_key(text)
        toks = [t for t in n.split() if t]
        like = "%" + "%".join(toks) + "%"
        hits: List[Tuple[float, str, str, Dict[str, Any]]] = []  # (score, kind, line, ref)

        def score(name_norm: str) -> float:
            """Correspondance par mots entiers ou débuts de mots (« layer » ne trouve pas « flayer »)."""
            parts = [p.strip() for p in str(name_norm or "").split("|")]
            best = 0.0
            for p in parts:
                words = p.split()
                if p == n:
                    best = max(best, 3.0)
                elif p.startswith(n + " ") or (p.startswith(n) and len(toks) > 1):
                    best = max(best, 2.0 - len(p) / 200)
                elif f" {n} " in f" {p} ":
                    best = max(best, 1.5 - len(p) / 200)
                elif all(any(w.startswith(t) for w in words) for t in toks):
                    best = max(best, (1.0 if p.startswith(toks[0]) else 0.9) - len(p) / 200)
            return best

        def want(kind: str) -> bool:
            return not kind_filter or kind_filter in KIND_ALIASES.get(kind, (kind,))

        char, db = self._db_char(args)
        # ouverture directe d'une section de connaissance par son titre (commande donnée en pied de liste)
        if want("knowledge"):
            try:
                for sec in K.plugin_sections():
                    tn = F.norm_key(sec["title"])
                    if n and (tn == n or F.norm_key(short_title(sec["title"])) == n
                              or (kind_filter and len(n) >= 6 and tn.startswith(n))):
                        return self._knowledge_sheet(sec)
            except Exception:
                pass
        faction = str(F.g(db, "identity", "faction") or "")[:1].upper() if db else ""
        # données du perso
        if db and want("perso"):
            for q in as_list(F.g(db, "quests", "list")):
                s = score(F.norm_key(q.get("title")))
                if s:
                    hits.append((s + 0.6, "perso", T("Quête de ton journal : **{title}** ({state})",
                                                     title=q.get("title"),
                                                     state=T("à rendre") if q.get("complete") else T("en cours"))
                                 + G.quest_where(q), {"tool": "quests", "quete": q.get("title")}))
            for it in self._bag_items(db, bank=True):
                s = score(F.norm_key(it.get("name")))
                if s:
                    hits.append((s + 0.4, "perso", T("Dans tes sacs : **{name}** ×{n}", name=it.get("name"),
                                                     n=it.get("count") or 1), {"tool": "item", "itemId": it.get("itemId")}))
        # quêtes vues en jeu (mémoire de l'addon 1.4)
        if want("quest"):
            mem = self.quest_memory(char, db)
            for k, q in (mem.get("quests") or {}).items():
                for title in set((q.get("titles") or {}).values()):
                    s = score(F.norm_key(title))
                    if s:
                        hits.append((s + 0.05, "quest", T("Quête vue en jeu : **{name}** (id {id}) → quests questId:{id}",
                                                          name=title, id=k),
                                     {"tool": "quest", "id": int(k), "name": title}))
                        break
        # connaissances du plugin (faits Forever sourcés : rulesets, donjons, bugs, voyages…)
        if want("knowledge"):
            try:
                for sc, sec in K.search_plugin(text, 3):
                    full = set(K._aterms(text)) <= sec["head_terms"]
                    short = short_title(sec["title"])
                    hits.append(((3.0 if full else 1.0 + min(sc, 3.0) / 2), "knowledge",
                                 T("Connaissance Forever : **{title}** → search texte:\"{title}\" type:connaissance",
                                   title=short), {"tool": "knowledge", "section": sec}))
            except Exception:
                pass
        # dungeons Forever et Classic de la table de référence (noms FR/EN, niveaux)
        if want("dungeon"):
            for d in DG.find(text, 3):
                hits.append((2.9 if F.norm_key(text) in d["_names"] else 2.0, "dungeon",
                             T("Donjon : **{name}** ({levels}) → dungeon donjon:{name}", name=d["fr"],
                               levels=DG.levels_text(d)), {"tool": "dungeon", "id": d.get("map_id"),
                                                           "name": d["fr"]}))
        # mémoire de recherche
        if want("note"):
            try:
                for sc, note in K.search(self.store.data_dir, text, 3, min_cover=0.6):
                    hits.append((1.2 + min(sc, 1.0) / 10, "note", T("Note : **{title}** ({date}, {cert})",
                                                                     title=note.get("sujet", note["file"]),
                                                                     date=note.get("date", "?"),
                                                                     cert=note.get("certitude", "?")),
                                 {"tool": "note", "note": note}))
            except Exception:
                pass
        gdb = self.gamedb(required=False)
        if gdb:
            has_q = bool(gdb.q("SELECT 1 FROM sqlite_master WHERE type='table' AND name='q_quests'"))
            specs = [("item", "SELECT id, name, name_norm, req_level, quality, ilvl, stats_json FROM items WHERE name_norm LIKE ? "
                              "ORDER BY length(name) LIMIT 40"),
                     ("zone", "SELECT id, name, name_norm FROM zones WHERE name_norm LIKE ? LIMIT 10"),
                     ("item", "SELECT i.id, i.name, fold(q.name) AS name_norm, i.req_level, i.quality, i.ilvl, "
                              "i.stats_json FROM q_items q JOIN items i ON i.id = q.id WHERE fold(q.name) LIKE ? "
                              "LIMIT 20"),
                     ("dungeon", "SELECT map_id AS id, name, name_norm FROM dungeons WHERE name_norm LIKE ? LIMIT 10"),
                     ("recipe", "SELECT spell_id AS id, name, name_norm FROM recipes WHERE name_norm LIKE ? "
                                "LIMIT 10")]
            if self.has_table(gdb, "c_quests"):  # quêtes vues en jeu (dont celles propres à Forever)
                specs += [("quest", "SELECT id, title AS name, title_norm AS name_norm FROM c_quests "
                                    "WHERE title_norm LIKE ? LIMIT 10"),
                          ("npc", "SELECT id, name, name_norm FROM c_creatures WHERE name_norm LIKE ? LIMIT 10"),
                          ("object", "SELECT id, name, name_norm FROM c_objects WHERE name_norm LIKE ? LIMIT 6")]
            specs.append(("spell", "SELECT min(id) AS id, name, fold(name) AS name_norm, max(spell_level) AS level "
                                   "FROM spells WHERE fold(name) LIKE ? GROUP BY name LIMIT 10"))
            if has_q:
                specs += [("npc", "SELECT id, coalesce(name_loc, name) AS name, "
                                  "coalesce(name_norm, '') || ' | ' || fold(subname) AS name_norm, "
                                  "subname, friendly FROM q_npcs WHERE subname IS NOT NULL AND fold(subname) LIKE ? "
                                  "ORDER BY spawn_count DESC LIMIT 15")]
                specs += [("quest", "SELECT id, coalesce(name_loc, name) AS name, name_norm, level FROM q_quests "
                                    "WHERE name_norm LIKE ? LIMIT 20"),
                          ("npc", "SELECT id, coalesce(name_loc, name) AS name, name_norm, min_level AS level, "
                                  "friendly FROM q_npcs WHERE name_norm LIKE ? ORDER BY spawn_count DESC LIMIT 20"),
                          ("object", "SELECT id, coalesce(name_loc, name) AS name, name_norm FROM q_objects "
                                     "WHERE name_norm LIKE ? LIMIT 10")]
            else:
                specs.append(("quest", "SELECT id, title AS name, title_norm AS name_norm FROM quests "
                                       "WHERE title_norm LIKE ? LIMIT 20"))
            if want("item"):
                hits += self._search_english_items(gdb, text, score, has_q)
            plevel = F.g(db, "progression", "level") if db else None
            for kind, sql in specs:
                if not want(kind):
                    continue
                try:
                    rows = gdb.q(sql, (like,))
                except Exception:
                    continue
                seen = set(h[3].get("name") for h in hits if h[1] == kind)
                for r in rows:
                    if kind == "item" and not GDB.plausible_item(r):
                        continue
                    if (kind == "npc" and faction in ("A", "H") and "friendly" in r.keys() and r["friendly"]
                            and faction not in str(r["friendly"]).upper()):
                        continue  # PNJ de l'autre faction (formateurs, gardes)
                    if r["name"] in seen:
                        continue
                    seen.add(r["name"])
                    s = score(F.norm_key(r["name_norm"]) if kind in ("spell", "npc") else r["name_norm"])
                    if not s:
                        continue
                    lvl = r["level"] if "level" in r.keys() else (r["req_level"] if "req_level" in r.keys() else None)
                    if plevel and lvl:
                        s -= min(abs(lvl - plevel), 30) / 100  # plus proche du niveau du perso = plus pertinent
                    if kind == "zone":
                        s += 1.2  # « Menethil » = d'abord le port, pas « Garde de Menethil »
                    elif kind == "object" and kind_filter not in KIND_ALIASES["object"]:
                        s -= 0.8  # objets du monde (panneaux, coffres) : rarement ce qu'on cherche
                    hits.append((s, kind, self._search_line(kind, r), {"tool": kind, "id": r["id"],
                                                                       "name": r["name"]}))
        if not hits:
            return T("Rien trouvé pour « {q} » (base locale, mémoire de recherche, données du perso). Vérifie le nom "
                     "dans la langue du jeu ; sinon web, puis save_knowledge.", q=text)
        hits.sort(key=lambda h: -h[0])
        hits = hits[:limit]
        lines = [T("**{n} résultat(s) pour « {q} »**", n=len(hits), q=text)
                 + (f" {GDB.badge()}" if gdb else ""), ""]
        for s, kind, line, ref in hits:
            lines.append(f"- {line}")
        top = hits[0]
        clear = top[0] >= 2.9 and (len(hits) == 1 or hits[1][0] < top[0] - 0.4)
        if clear or len(hits) == 1:
            sheet = self._search_sheet(top[3], args)
            if sheet:
                lines += ["", "---", sheet]
        else:
            lines.append("\n_" + T("Plusieurs résultats : ouvre celui qui convient avec la commande indiquée après "
                                   "la flèche.") + "_")
        return "\n".join(lines)

    def _search_english_items(self, gdb: GDB.GameDB, text: str, score: Any,
                              has_q: bool) -> List[Tuple[float, str, str, Dict[str, Any]]]:
        """Objets introuvables par leur nom anglais dans QuestieDB (qui ne garde que les objets avec une source) :
        - butin des donjons Forever d'après les guides de donjons.json (nom anglais → itemId) ;
        - objets fabriqués : « Pattern: X » / « Patron : Y » (QuestieDB / client, même id) donne X = Y,
          puis Y retrouvé dans items par son nom dans la langue du jeu."""
        out: List[Tuple[float, str, str, Dict[str, Any]]] = []
        for g in DG.guide_items():
            s = score(F.norm_key(g["en"]))
            if not s:
                continue
            row = gdb.item(g["id"])
            name = row["name"] if row else g["en"]
            local = None
            if g["boss"].get("encounter"):
                rr = gdb.q("SELECT name FROM encounters WHERE id = ?", (g["boss"]["encounter"],))
                local = rr[0]["name"] if rr else None
            boss = g["boss"].get("en") if I.get_lang() == "en" or not local else local
            out.append((s + 0.1, "item", T("Objet de donjon : **{name}** ({en}, id {id}) — {dungeon}, {boss} → item "
                                            "itemId:{id}", name=name, en=g["en"], id=g["id"],
                                            dungeon=DG.loc(g["instance"], "name"), boss=boss),
                        {"tool": "item", "id": g["id"], "name": name}))
        n = F.norm_key(text)
        if not has_q or len(n) < 4:
            return out
        try:
            rows = gdb.q("SELECT q.name AS en, i.name AS loc FROM q_items q JOIN items i ON i.id = q.id "
                         "WHERE q.name LIKE '%: %' AND fold(q.name) LIKE ? LIMIT 20",
                         ("%" + "%".join(n.split()) + "%",))
        except Exception:
            return out
        for r in rows:
            en_rest = str(r["en"]).split(": ", 1)[1].strip()
            loc_rest = re.split(r"\s?: ", str(r["loc"] or ""), maxsplit=1)
            if len(loc_rest) < 2:
                continue
            s = score(F.norm_key(en_rest))
            if not s:
                continue
            made = gdb.q("SELECT id, name, name_norm, req_level, quality, ilvl, stats_json FROM items "
                         "WHERE name = ? ORDER BY quality DESC, id LIMIT 1", (loc_rest[1].strip(),))
            if made and GDB.plausible_item(made[0]):
                m = made[0]
                out.append((s + 0.05, "item", self._search_line("item", m), {"tool": "item", "id": m["id"],
                                                                             "name": m["name"]}))
        return out

    def _knowledge_sheet(self, sec: Dict[str, Any]) -> str:
        return (f"**{sec['title'].replace('**', '')}** — " + T("connaissances du plugin ({file}), à citer avec leur badge et leur date",
                                              file=sec["file"]) + "\n" + clip_section(sec["body"]))

    def _search_line(self, kind: str, r: Any) -> str:
        if kind == "item":
            return T("Objet : **{name}** (id {id}, niv. {req}, {quality}) → item itemId:{id}", name=r["name"],
                     id=r["id"], req=r["req_level"], quality=GDB.quality_name(r["quality"]))
        if kind == "quest":
            return T("Quête : **{name}** (id {id}) → quests questId:{id}", name=r["name"], id=r["id"])
        if kind == "npc":
            sub = r["subname"] if "subname" in r.keys() and r["subname"] else None
            name = f"{r['name']}** <{sub}>" if sub else f"{r['name']}**"
            return T("PNJ : **{name} (id {id}) → npc npcId:{id}", name=name, id=r["id"])
        if kind == "spell":
            return T("Sort : **{name}** (id {id}) → talents sorts:true", name=r["name"], id=r["id"])
        if kind == "object":
            return T("Objet du monde : **{name}** (id {id}) → npc nom:{name}", name=r["name"], id=r["id"])
        if kind == "zone":
            return T("Zone : **{name}** → quests disponibles:true zone:{name}", name=r["name"])
        if kind == "dungeon":
            return T("Donjon : **{name}** → dungeon donjon:{name}", name=r["name"])
        return T("Recette : **{name}** → professions", name=r["name"])

    def _search_sheet(self, ref: Dict[str, Any], args: Dict[str, Any]) -> Optional[str]:
        perso = {"perso": args["perso"]} if args.get("perso") else {}
        tool = ref.get("tool")
        try:
            if tool == "item" and ref.get("id"):
                return self.get_item({"itemId": ref["id"], **perso})
            if tool == "item" and ref.get("itemId"):
                return self.get_item({"itemId": ref["itemId"], **perso})
            if tool == "quest":
                return self.get_quest_info({"questId": ref["id"], **perso})
            if tool == "quests":
                return self.get_quest_info({"titre": ref["quete"], **perso})
            if tool == "npc":
                return self.find_npc({"npcId": ref["id"], **perso})
            if tool == "object":
                return self.find_npc({"nom": ref["name"], **perso})
            if tool == "dungeon":
                return self.tool_dungeon({"donjon": ref["name"], **perso})
            if tool == "knowledge":
                return self._knowledge_sheet(ref["section"])
            if tool == "zone":
                return self.find_quests({"zone": ref["name"], **perso})
            if tool == "note":
                note = ref["note"]
                return f"### {note.get('sujet', note['file'])}\n{note.get('body', '')[:1200]}"
        except Exception:
            return None
        return None


def short_title(title: str) -> str:
    """Titre de section sans gras ni précision après « — » (sert de commande d'ouverture)."""
    return title.replace("**", "").split(" — ")[0].strip()


def clip_section(body: str, limit: int = 3500, hard: int = 6000) -> str:
    """Section entière si elle tient ; sinon coupe à une limite de paragraphe, jamais au milieu d'un tableau."""
    if len(body) <= limit:
        return body
    out: List[str] = []
    size = 0
    lines = body.splitlines()
    for i, line in enumerate(lines):
        in_table = line.lstrip().startswith("|")
        if size + len(line) > limit and not in_table and (not line.strip() or not out or
                                                          not out[-1].lstrip().startswith("|")):
            break
        if size + len(line) > hard:
            break
        out.append(line)
        size += len(line) + 1
    rest = len(lines) - len(out)
    text = "\n".join(out).rstrip()
    if rest > 0:
        text += "\n" + T("… (section coupée : {n} ligne(s) de plus dans le fichier)", n=rest)
    return text


def _jids(v: Any) -> List[int]:
    try:
        x = json.loads(v) if isinstance(v, str) and v else (v or [])
    except ValueError:
        return []
    return [int(i) for i in x if isinstance(i, (int, float))]


def _int_ids(row: Any) -> List[int]:
    out: List[int] = []
    for k in ("pre_single", "pre_group"):
        try:
            v = json.loads(row[k]) if row[k] else []
        except (ValueError, KeyError, IndexError, TypeError):
            v = []
        out += [int(x) for x in v if isinstance(x, (int, float)) or str(x).isdigit()]
    return out


KIND_ALIASES = {
    "item": ("item", "objet", "objets", "items"), "quest": ("quest", "quete", "quetes", "quests"),
    "npc": ("npc", "pnj", "monstre", "mob"), "object": ("object", "objet du monde", "world object"),
    "zone": ("zone", "zones"), "dungeon": ("dungeon", "donjon", "raid"), "recipe": ("recipe", "recette"),
    "note": ("note", "notes", "memoire"), "perso": ("perso", "character", "moi"),
    "knowledge": ("knowledge", "connaissance", "connaissances", "regle", "regles", "mecanique"),
    "spell": ("spell", "sort", "sorts", "talent", "talents", "capacite"),
}
