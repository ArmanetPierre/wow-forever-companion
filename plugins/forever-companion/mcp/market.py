"""Outil `market` : un métier d'artisanat face aux prix de l'hôtel des ventes (HV) relevés par l'addon.

Pour un métier (défaut : Travail du cuir) et un perso :
- monter au meilleur prix : le parcours de professions_plan, mais à chaque point la recette au plus faible
  coût net par point = (composants à acheter − revente du produit) × fabrications attendues pour un point ;
  chaque composant vaut le moins cher entre le prix HV relevé (le plus bas du dernier relevé), le prix
  marchand (`items.buy_price` + vendeur ami connu) et sa fabrication ; ce qui est déjà dans les sacs ou la
  banque ne coûte rien (consommé au fil du parcours). Revente = max(prix HV × (1 − 5 %), prix marchand),
  prix HV compté pour au plus la moitié de la quantité vue à l'HV (le reste au prix marchand).
- rentabilité : recettes connues ou apprenables au rang actuel, profit = revente HV nette − coût des
  composants, volume vu (quantité, enchères), marge ; « vendre brut ou fabriquer ? » pour le cuir récolté.
- équipement : objets fabricables par ce métier qui améliorent un perso (lui ou un autre du compte),
  notés par gear.evaluate, coût de fabrication face au prix HV de l'objet fini, ensembles signalés.
- sacs : matières et produits du métier en sacs/banque : garder pour le parcours, HV ou marchand.

Jamais de prix inventé : sans relevé HV, seuls les prix marchands de la base locale servent et l'outil
liste les objets à chercher à l'HV. Prix HV : badge [Forever · tes relevés HV du JJ/MM], signalés au-delà
de 3 jours. Prix marchands : [Forever · base locale].
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import formats as F
import gamedb as GDB
import gear as G
import i18n as I
import prices as PR
import professions_plan as PP
from gamedb_tools import PROFESSION_IDS, db_at_level
from i18n import T
from i18n_en import EN
from luasv import as_list

DEFAULT_PROF = 165          # Travail du cuir
LEATHER = (7, 6)            # artisanat / cuir : matières récoltées par le Dépeçage
STICKY = 0.35
CRAFT_TIME = 10.0   # « coût » d'une fabrication (cuivre) : départage les recettes qui se remboursent
# couleur capturée par l'addon (1.5, jeton non traduit) -> difficulty (0 orange … 3 grise)
SKILL_TYPES = {"optimal": 0, "medium": 1, "easy": 2, "trivial": 3}
VIEWS = ("tout", "monter", "profit", "equipement", "sacs")
VIEW_ALIASES = {"all": "tout", "level": "monter", "leveling": "monter", "levelling": "monter", "montee": "monter",
                "profits": "profit", "rentabilite": "profit", "gear": "equipement", "equipment": "equipement",
                "ensembles": "equipement", "sets": "equipement", "bags": "sacs", "inventaire": "sacs"}


def smoney(c: Any) -> str:
    """Somme signée en po/pa/pc (« −1 pa 20 pc »)."""
    try:
        v = int(round(float(c)))
    except (TypeError, ValueError):
        return "?"
    return ("−" if v < 0 else "") + F.money(abs(v))


def volume(e: Dict[str, Any]) -> str:
    """Volume vu à l'HV ; n = 0 : vue de navigation (prix plancher seulement, pas de médiane)."""
    if not e.get("n"):
        return T("{qty} en vente, prix plancher (vue de navigation)", qty=e.get("qty") or "?")
    return T("vu {qty} en {n} annonce(s)", qty=e.get("qty") or "?", n=e["n"])


def price_day(day: str) -> str:
    """« 2026-11-24 » -> « 24/11 » (fr) ou « 11/24 » (en)."""
    try:
        _y, m, d = day.split("-")
    except ValueError:
        return day
    return f"{m}/{d}" if I.get_lang() == "en" else f"{d}/{m}"


# ---------------------------------------------------------------------------
# catalogue valorisé aux prix du marché

class MarketCatalog(PP.Catalog):
    """Catalog de professions_plan dont le coût d'un composant tient compte des prix HV relevés."""

    def __init__(self, tools: Any, gdb: Any, pid: int, place: PP.Place, market: PR.Market):
        self.market = market
        self._src: Dict[int, str] = {}
        super().__init__(tools, gdb, pid, place)

    def unit_cost(self, iid: int, depth: int = 0) -> Tuple[float, bool]:
        """(coût unitaire, connu ?) : le moins cher entre HV, marchand et fabrication (même métier).
        Source dans self.source(iid) : hv, marchand, fabrication ou inconnu (valeur interne de classement)."""
        if iid in self._cost:
            return self._cost[iid]
        self._cost[iid] = (math.inf, False)  # garde contre les boucles de recettes
        opts: List[Tuple[float, str]] = []
        v = self.buyable(iid)
        if v:
            opts.append((float(v["price"]), "marchand"))
        p = self.market.buy(iid)
        if p:
            opts.append((float(p), "hv"))
        if depth < 2 and iid in self.by_product:
            for rec in self.by_product[iid]:
                if rec["rank"] > 300 or not rec["reagents"] or any(g["item_id"] == iid for g in rec["reagents"]):
                    continue
                parts = [self.unit_cost(g["item_id"], depth + 1) for g in rec["reagents"]]
                if all(k for _c, k in parts):
                    c = sum(g["count"] * pc for g, (pc, _k) in zip(rec["reagents"], parts)) / max(1, rec["item_count"])
                    opts.append((c, "fabrication"))
        if opts:
            cost, src = min(opts)
            self._cost[iid], self._src[iid] = (cost, True), src
            return self._cost[iid]
        it = self.items.get(iid)
        sell = (it["sell_price"] if it is not None else 0) or 0
        self._cost[iid], self._src[iid] = (max(20.0, 4.0 * sell), False), "inconnu"
        return self._cost[iid]

    def source(self, iid: int) -> str:
        self.unit_cost(iid)
        return self._src.get(iid, "inconnu")

    def resale(self, iid: int) -> Tuple[int, str]:
        """(revente unitaire, « hv » | « marchand » | « » ) : max(HV net de commission, prix marchand)."""
        it = self.items.get(iid)
        vendor = int((it["sell_price"] if it is not None else 0) or 0)
        ah = self.market.sell_net(iid) or 0
        if ah > vendor:
            return ah, "hv"
        return (vendor, "marchand") if vendor else (0, "")

    def craft_cost(self, rec: Dict[str, Any]) -> Tuple[float, bool]:
        """(coût des composants d'une fabrication, tous les prix connus ?)."""
        total, known = 0.0, True
        for g in rec["reagents"]:
            c, k = self.unit_cost(g["item_id"])
            total += g["count"] * c
            known = known and k
        return total, known


# ---------------------------------------------------------------------------
# monter au meilleur prix

def _real_colors(rec: Dict[str, Any], start: int, captured: Optional[Dict[str, int]]) -> Dict[str, Any]:
    """Recale les couleurs estimées d'une recette sur sa couleur réelle capturée en jeu à `start`
    (skillType / difficulty) quand le jeu la dit plus facile : jaune → la jaune commence à `start`,
    verte → `start` est au milieu jaune-grise (seuil de la verte). Largeur jaune-grise conservée."""
    real = (captured or {}).get(F.norm_key(rec["name"]))
    if real not in (1, 2) or start < rec["rank"] or PP.color_at(start, rec) >= real:
        return rec
    w = max(2, rec["grey"] - rec["yellow"])
    out = dict(rec)
    if real == 1:
        out["yellow"], out["grey"] = start, min(rec["grey"], start + w)
        out["green"] = (out["yellow"] + out["grey"]) // 2
    else:
        out["grey"] = min(rec["grey"], start + w // 2)
        out["yellow"], out["green"] = out["grey"] - w, start
    out["colors_src"] = "jeu"
    return out


def pattern_price(cat: MarketCatalog, rec: Dict[str, Any]) -> int:
    """Prix marchand du patron qui apprend la recette (0 si apprise au formateur ou inconnu)."""
    if rec.get("acq") != "patron-marchand":
        return 0
    for p in rec["patterns"]:
        v = cat.buyable(p["id"])
        if v:
            return int(v["price"])
    return 0


def plan_cheapest(cat: MarketCatalog, start: int, target: int, stock: Dict[int, int],
                  captured: Optional[Dict[str, int]] = None, learned: Optional[set] = None
                  ) -> List[Dict[str, Any]]:
    """Segments [{from, to, rec, crafts, buy, resale}] : à chaque point, la recette au plus faible coût net
    par point. Stock des sacs/banque gratuit, consommé au fil du parcours. Pénalités de professions_plan
    (patron, verte, rang estimé) ajoutées au coût brut, jamais de recette grise."""
    recs = [r for r in cat.recipes if cat.usable(r)]
    for r in recs:
        r["acq"], r["penalty"] = cat.acquisition(r)
    recs = [_real_colors(r, start, captured) for r in recs if r["penalty"] != math.inf]
    left = dict(stock)
    segs: List[Dict[str, Any]] = []
    skill = max(1, start)

    sold: Dict[int, float] = {}
    used: set = set()

    def resale_of(r: Dict[str, Any], units: float) -> float:
        """Revente HV comptée pour au plus la moitié du volume vu à l'HV (le reste au prix marchand)."""
        iid = r["item_id"]
        val, src = cat.resale(iid)
        if src != "hv":
            return val * units
        e = cat.market.latest(iid) or {}
        cap = max(1, (e.get("qty") or 0) // 2)
        ah_units = min(units, max(0.0, cap - sold.get(iid, 0.0)))
        vendor = (cat.items[iid]["sell_price"] if iid in cat.items else 0) or 0
        return ah_units * val + (units - ah_units) * vendor

    def point(r: Dict[str, Any]) -> Optional[Tuple[float, float, float, float]]:
        """(score, achats, revente, fabrications) pour gagner un point avec r."""
        cpp = PP.crafts_per_point(skill, r)
        if cpp == math.inf:
            return None
        if captured and captured.get(F.norm_key(r["name"])) == 3 and skill == start:
            return None
        buy = gross = 0.0
        for g in r["reagents"]:
            unit = cat.unit_cost(g["item_id"])[0]
            need = g["count"] * cpp
            gross += need * unit
            buy += max(0.0, need - left.get(g["item_id"], 0)) * unit
        resale = resale_of(r, max(1, r["item_count"]) * cpp)
        if learned is not None and r["name"] not in used and F.norm_key(r["name"]) not in learned \
                and r["spell_id"] not in learned:
            buy += pattern_price(cat, r)  # patron à acheter une fois
        mult = r["penalty"] * (PP.GREEN_PENALTY if PP.color_at(skill, r) == 2 else 1.0) \
            * (1.1 if r["source"] == "estimation" else 1.0)
        # une recette qui se rembourse par la revente ne coûte rien : on préfère alors la moins longue
        # (moins de fabrications) plutôt que d'enchaîner des fabrications vertes pour leur bénéfice
        score = max(0.0, buy - resale) + CRAFT_TIME * cpp + (mult - 1.0) * (gross + 5.0 * cpp)
        return score, buy, resale, cpp

    while skill < target:
        best, best_v = None, None
        for r in recs:
            v = point(r)
            if v is not None and (best_v is None or v[0] < best_v[0]):
                best, best_v = r, v
        prev = segs[-1]["rec"] if segs else None
        if best is not None and prev is not None and prev is not best:
            pv = point(prev)
            if pv is not None and pv[0] <= best_v[0] + STICKY * abs(best_v[0]) + 1:
                best, best_v = prev, pv
        if best is None:
            segs.append({"from": skill, "to": target, "rec": None, "crafts": 0, "buy": 0, "resale": 0})
            break
        _s, buy, resale, cpp = best_v
        sold[best["item_id"]] = sold.get(best["item_id"], 0.0) + max(1, best["item_count"]) * cpp
        used.add(best["name"])
        for g in best["reagents"]:
            if left.get(g["item_id"]):
                left[g["item_id"]] = max(0, left[g["item_id"]] - g["count"] * cpp)
        if segs and segs[-1]["rec"] is best:
            s = segs[-1]
            s["to"], s["crafts"], s["buy"], s["resale"] = skill + 1, s["crafts"] + cpp, s["buy"] + buy, \
                s["resale"] + resale
        else:
            segs.append({"from": skill, "to": skill + 1, "rec": best, "crafts": cpp, "buy": buy, "resale": resale})
        skill += 1
    return segs


# ---------------------------------------------------------------------------
# outil

class MarketToolsMixin:
    """Mélangé à Tools (server.py) : utilise self.store, self._char, self.gamedb, self._bag_items."""

    def tool_market(self, args: Dict[str, Any]) -> str:
        char, db = self._char(args)
        gdb = self.gamedb()
        view = F.norm_key(args.get("vue") or "tout")
        view = VIEW_ALIASES.get(view, view)
        if view not in VIEWS:
            raise self.ToolError(T("vue inconnue : {v} (tout, monter, profit, equipement, sacs)", v=args.get("vue")))
        # métier
        wanted = args.get("metier")
        profs = as_list(F.g(db, "professions", "professions"))
        pid = PROFESSION_IDS.get(F.norm_key(wanted)) if wanted else DEFAULT_PROF
        if wanted and not pid:
            pid = PP.profession_id(gdb, wanted)
        if not pid:
            raise self.ToolError(T("Métier « {m} » inconnu de la base locale.", m=wanted))
        cid = PP.classic_id(gdb, pid)
        prof = next((p for p in profs if p.get("skillLineId") in (pid, cid)
                     or (wanted and F.norm_key(p.get("name")) == F.norm_key(wanted))), None)
        if prof is None and not wanted:
            prof = next((p for p in profs if PP.classic_id(gdb, p.get("skillLineId") or 0) == cid), None)
        pname = (prof or {}).get("name") or (gdb.q("SELECT name FROM professions WHERE id = ?", (pid,)) or
                                             [{"name": wanted or "?"}])[0]["name"]
        if cid in PP.GATHERING:
            raise self.ToolError(T("{prof} est un métier de récolte : demande `market` sur le métier d'artisanat "
                                   "qui utilise ses matières (ex. Travail du cuir pour le Dépeçage).", prof=pname))
        rank = int((prof or {}).get("rank") or 0)
        max_rank = int((prof or {}).get("max") or 0) or None
        level = int(F.g(db, "progression", "level") or F.g(db, "identity", "level") or 1)
        # prix du royaume et de la faction du perso
        ident = F.g(db, "identity", default={}) or {}
        hist = PR.load(self.store.data_dir, ident.get("realm"), ident.get("faction"), ident.get("realmNormalized"))
        market = PR.Market(hist)
        place = PP.Place(self, gdb, db)
        cat = MarketCatalog(self, gdb, pid, place, market)
        stock: Dict[int, int] = {}
        for it in self._bag_items(db, bank=True):
            if it.get("itemId"):
                stock[it["itemId"]] = stock.get(it["itemId"], 0) + (it.get("count") or 1)
        captured = self._market_captured(db, pid, cid, pname)
        learned = {F.norm_key(r.get("name")) for r in as_list((captured or {}).get("recipes")) if r.get("learned")}
        learned |= {r.get("spellId") or r.get("id") for r in as_list((captured or {}).get("recipes"))
                    if r.get("learned") and (r.get("spellId") or r.get("id"))}
        ctx = {"cat": cat, "market": market, "stock": stock, "rank": rank, "max": max_rank, "level": level,
               "learned": learned, "captured": captured, "pname": pname, "scan": [], "verdict": []}

        if prof is None:
            ctx["verdict"].append(T("{name} n'a pas {prof} : parcours depuis 1", name=ident.get("name") or "?",
                                    prof=pname))
        lines: List[str] = [self._market_header(market, ident)]
        if view in ("tout", "monter"):
            lines += self._market_levelup(ctx, args, prof is not None)
        if view in ("tout", "profit"):
            lines += self._market_profit(ctx, args)
        if view in ("tout", "equipement"):
            lines += self._market_gear(ctx, args, db)
        if view in ("tout", "sacs"):
            lines += self._market_bags(ctx)
        if not market:
            lines += self._market_scan_list(ctx)
        lines.append("")
        lines.append("_" + T("Prix HV = le plus bas du dernier relevé de l'addon (revente nette de 5 % de commission "
                             "[Classic]) ; un prix HV bouge vite et n'est jamais garanti : vérifie avant d'acheter "
                             "en gros. Prix marchands et recettes : [Forever · base locale]. Parcours : couleurs et "
                             "fabrications comme l'outil professions (règles [Classic] à vérifier dans Forever).") + "_")
        verdict = " ; ".join(ctx["verdict"]) or T("rien à conseiller sans prix ni recette exploitable")
        return "**" + T("Verdict :") + "** " + verdict[:1].upper() + verdict[1:] + ".\n" + self._head(db, *lines)

    # -- en-tête et recettes capturées ------------------------------------------------------
    def _market_header(self, market: PR.Market, ident: Dict[str, Any]) -> str:
        if not market:
            return T("**Aucun prix HV relevé** pour {realm} ({faction}) : seuls les prix marchands servent "
                     "[Forever · base locale]. Ouvre l'hôtel des ventes avec ForeverScribe actif et cherche les "
                     "objets listés en bas.", realm=ident.get("realm") or T("ton royaume"),
                     faction=ident.get("faction") or "?")
        last = market.last_scan
        age = (market.now - last) / 86400 if last else None
        stamp = price_day(PR.day_of(last)) if last else "?"
        txt = T("Prix HV : {n} objets relevés, dernier relevé le {day} ({age}) [Forever · tes relevés HV du {day}].",
                n=market.count, day=stamp, age=F.age(last))
        if age is not None and age > PR.OLD_DAYS:
            txt += " " + T("⚠ relevé de plus de {d} jours : repasse à l'HV.", d=PR.OLD_DAYS)
        if market.hist.get("realmGuessed"):
            txt += " " + T("Royaume absent de la capture : relevés de {realm} ({faction}) utilisés.",
                           realm=market.hist.get("realm") or "?", faction=market.hist.get("faction") or "?")
        return txt

    @staticmethod
    def _market_captured(db: Dict[str, Any], pid: int, cid: int, pname: str) -> Optional[Dict[str, Any]]:
        best = None
        for key, entry in (F.g(db, "recipes", default={}) or {}).items():
            if not isinstance(entry, dict):
                continue
            if entry.get("professionId") in (pid, cid) or F.norm_key(key) == F.norm_key(pname):
                if best is None or (entry.get("capturedAt") or 0) > (best.get("capturedAt") or 0):
                    best = entry
        if best is None:
            return None
        # 1.5 : skillType (jeton non traduit) = vraie couleur actuelle, prioritaire sur difficulty
        recs = []
        for r in as_list(best.get("recipes")):
            if isinstance(r, dict) and r.get("skillType") in SKILL_TYPES:
                r = {**r, "difficulty": SKILL_TYPES[r["skillType"]]}
            recs.append(r)
        return {**best, "recipes": recs}

    def _price_note(self, ctx: Dict[str, Any], iid: int) -> str:
        """« 1 pa 20 pc HV 24/11 » / « 50 pc marchand » / « prix inconnu » pour un composant."""
        cat, market = ctx["cat"], ctx["market"]
        src = cat.source(iid)
        cost = cat.unit_cost(iid)[0]
        if src == "hv":
            e = market.latest(iid)
            age = market.age_days(iid) or 0
            return T("{price} HV {day}", price=F.money(cost), day=price_day(e["day"])) + (
                " ⚠" + T("{d} j", d=int(age)) if age > PR.OLD_DAYS else "")
        if src == "marchand":
            return T("{price} marchand", price=F.money(cost))
        if src == "fabrication":
            return T("{price} en le fabriquant", price=F.money(cost))
        return T("prix inconnu")

    def _want_scan(self, ctx: Dict[str, Any], iid: int) -> None:
        if iid not in ctx["scan"] and not ctx["market"].latest(iid):
            ctx["scan"].append(iid)

    # -- a. monter au meilleur prix -----------------------------------------------------------
    def _market_levelup(self, ctx: Dict[str, Any], args: Dict[str, Any], learned_prof: bool) -> List[str]:
        cat, market, stock = ctx["cat"], ctx["market"], ctx["stock"]
        start = ctx["rank"] if learned_prof and ctx["rank"] else 1
        try:
            target = int(args["cible"]) if args.get("cible") is not None else \
                PP.target_for(start, ctx["max"], ctx["level"], learned_prof)
        except (TypeError, ValueError):
            target = PP.target_for(start, ctx["max"], ctx["level"], learned_prof)
        target = max(start + 1, min(300, target))
        ctx["colors"] = PP.captured_colors(ctx["captured"])
        segs = plan_cheapest(cat, start, target, stock, ctx["colors"], ctx["learned"])
        out = ["", T("**Monter {prof} de {a} à {b} au meilleur prix** (coût net par point = composants à acheter "
                     "− revente du produit, revente HV limitée à la moitié du volume vu) :", prof=ctx["pname"], a=start, b=target)]
        steps: List[Tuple[Dict[str, Any], int]] = []
        for i, s in enumerate(segs[:PP.MAX_SEGMENTS], 1):
            rec = s["rec"]
            if rec is None:
                out.append(T("- {a} → {b} : aucune recette connue de la base ne donne de points ici.", a=s["from"],
                             b=s["to"]))
                continue
            crafts = max(1, math.ceil(s["crafts"] - 1e-9))
            pts = max(1, s["to"] - s["from"])
            net = s["buy"] - s["resale"]
            known = T("connue") if (F.norm_key(rec["name"]) in ctx["learned"] or rec["spell_id"] in ctx["learned"]) else {
                "formateur": T("formateur"), "patron-marchand": T("patron marchand"),
                "patron": T("patron (butin/réputation)"), "inconnue": T("source inconnue")}.get(rec["acq"], "?")
            real = ctx["colors"].get(F.norm_key(rec["name"])) if s["from"] == start else None
            col = I.L("recipe_color", real, "?") + T(" (en jeu)") if real is not None else \
                I.L("recipe_color", PP.color_at(s["from"], rec), "?")
            unknown = [cat.item_name(g["item_id"], g.get("name")) for g in rec["reagents"]
                       if not cat.unit_cost(g["item_id"])[1]]
            if unknown:  # la valeur interne de classement n'est jamais affichée comme un prix
                out.append(T("{n}. **{a} → {b}** · {name} ({known}, {col}) · ~{crafts} fabrications · net : "
                             "prix incomplet ({list} sans prix)", n=i, a=s["from"], b=s["to"], name=rec["name"],
                             known=known, col=col, crafts=crafts, list=", ".join(unknown)))
            else:
                out.append(T("{n}. **{a} → {b}** · {name} ({known}, {col}) · ~{crafts} fabrications · net {net} "
                             "({per} par point)", n=i, a=s["from"], b=s["to"], name=rec["name"], known=known,
                             col=col, crafts=crafts, net=smoney(net), per=smoney(net / pts)))
            parts = []
            for g in rec["reagents"]:
                parts.append(f"{g['count']}× {cat.item_name(g['item_id'], g.get('name'))} "
                             f"({self._price_note(ctx, g['item_id'])})")
                if cat.source(g["item_id"]) != "marchand":
                    self._want_scan(ctx, g["item_id"])
            rv, rsrc = cat.resale(rec["item_id"])
            if rsrc == "hv":
                e = market.latest(rec["item_id"])
                age = market.age_days(rec["item_id"]) or 0
                sale = T("revente HV {price} pièce net ({day}{old}, {vol} : {k} à écouler)",
                         price=F.money(rv), day=price_day(e["day"]),
                         old=" ⚠" + T("{d} j", d=int(age)) if age > PR.OLD_DAYS else "", vol=volume(e),
                         k=crafts * max(1, rec["item_count"]))
            else:
                sale = T("revente {price} pièce ({src})", price=F.money(rv), src=T("marchand")) if rv \
                    else T("pas de revente connue")
            self._want_scan(ctx, rec["item_id"])
            out.append("   " + T("Composants : {list} · {sale}", list="; ".join(parts), sale=sale))
            pp = pattern_price(cat, rec) if known == T("patron marchand") else 0
            if pp:
                out.append("   " + T("Patron à acheter chez un marchand : {price} (compté dans le coût).",
                                      price=F.money(pp)))
            steps.append((rec, crafts))
        if not steps:
            return out
        craft, raw, via = PP.expand_steps(cat, steps)
        total_buy, unknown, shop = 0.0, [], []
        for iid, qty in sorted(raw.items(), key=lambda x: -x[1]):
            have = min(stock.get(iid, 0), qty)
            need = qty - have
            have_t = T(" (tu en as {n})", n=stock[iid]) if stock.get(iid) else ""
            if need <= 0:
                shop.append(T("{qty} {name}{have} — déjà en sacs", qty=qty, name=cat.item_name(iid), have=have_t))
                continue
            src = cat.source(iid)
            if src in ("hv", "marchand"):
                cost = cat.unit_cost(iid)[0] * need
                total_buy += cost
                shop.append(T("{need} {name}{have} — {note} → {total}", need=need, name=cat.item_name(iid),
                              have=have_t, note=self._price_note(ctx, iid), total=F.money(cost)))
            else:
                unknown.append(iid)
                self._want_scan(ctx, iid)
                shop.append(T("{need} {name}{have} — prix inconnu : à récolter ou à relever à l'HV", need=need,
                              name=cat.item_name(iid), have=have_t))
        if craft:
            out.append(T("À fabriquer en route : {list}.", list=", ".join(
                f"{q} {cat.item_name(i)}" for i, q in sorted(craft.items(), key=lambda x: -x[1]))))
        out.append(T("**À acheter ou récolter** (total du parcours, stock des sacs et de la banque déduit) :"))
        out += ["- " + p for p in shop]
        seen_rec = set()
        for rec, _c in steps:
            if rec["name"] in seen_rec or F.norm_key(rec["name"]) in ctx["learned"] or rec["spell_id"] in ctx["learned"]:
                continue
            seen_rec.add(rec["name"])
            pp = pattern_price(cat, rec)
            if pp:
                total_buy += pp
                out.append("- " + T("Patron de {name} — marchand → {total}", name=rec["name"], total=F.money(pp)))
        resale = sum(s["resale"] for s in segs if s["rec"])
        net = total_buy - resale
        basis = T(" (prix HV + marchand)") if market else T(" (prix marchands seulement)")
        if unknown:
            out.append(T("**Coût estimé** : achats connus {buy} + {n} composant(s) sans prix (à récolter ou relever) ; "
                         "revente possible des produits {resale}. Pas de total net tant que ces prix manquent.",
                         buy=F.money(total_buy), n=len(unknown), resale=F.money(resale)))
            ctx["verdict"].append(T("monter {prof} de {a} à {b} : {buy} d'achats connus{basis} + {list} à récolter "
                                    "ou à relever à l'HV", prof=ctx["pname"], a=start, b=target,
                                    buy=F.money(total_buy), basis=basis,
                                    list=", ".join(cat.item_name(i) for i in unknown[:3])))
        else:
            out.append(T("**Coût estimé** : achats {buy} − revente des produits {resale} = **{net} net**.",
                         buy=F.money(total_buy), resale=F.money(resale), net=smoney(net)))
            if net < 0:
                ctx["verdict"].append(T("monter {prof} de {a} à {b} : {buy} d'achats{basis}, et ≈ {gain} de gain net "
                                        "si tu revends les produits", prof=ctx["pname"], a=start, b=target,
                                        buy=F.money(total_buy), basis=basis, gain=F.money(-net)))
            else:
                ctx["verdict"].append(T("monter {prof} de {a} à {b} coûte ≈ {net} net{basis}", prof=ctx["pname"],
                                        a=start, b=target, net=smoney(net), basis=basis))
        ctx["plan_raw"] = raw
        return out

    # -- b. rentabilité -----------------------------------------------------------------------
    def _profit_rows(self, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        cat, market, rank = ctx["cat"], ctx["market"], ctx["rank"]
        rows = []
        for rec in cat.recipes:
            if not cat.usable(rec):
                continue
            known = (F.norm_key(rec["name"]) in ctx["learned"] or rec["spell_id"] in ctx["learned"])
            if not known and (rec["rank"] > max(rank, 1) or cat.acquisition(rec)[1] == math.inf):
                continue
            cost, all_known = cat.craft_cost(rec)
            e = market.latest(rec["item_id"])
            per = max(1, rec["item_count"])
            sale = (market.sell_net(rec["item_id"]) or 0) * per if e else None
            vendor = (rec["item_sell"] or 0) * per
            rows.append({"rec": rec, "known": known, "cost": cost, "cost_known": all_known, "sale": sale,
                         "vendor": vendor, "entry": e,
                         "profit": (sale - cost) if sale is not None and all_known else None})
        return rows

    def _market_profit(self, ctx: Dict[str, Any], args: Dict[str, Any]) -> List[str]:
        cat, market = ctx["cat"], ctx["market"]
        rows = ctx.setdefault("profit_rows", self._profit_rows(ctx))
        out = ["", T("**Rentabilité** (recettes connues ou apprenables à {rank} ; profit = revente HV − 5 % − "
                     "composants au moins cher) :", rank=ctx["rank"])]
        priced = sorted((r for r in rows if r["profit"] is not None), key=lambda r: -r["profit"])
        if not priced:
            out.append(T("- Aucun produit de ces recettes n'a de prix HV relevé : profit impossible à calculer."))
            for r in sorted(rows, key=lambda r: (not r["known"], -r["rec"]["rank"]))[:6]:
                self._want_scan(ctx, r["rec"]["item_id"])
        for r in priced[:8]:
            rec, e = r["rec"], r["entry"]
            margin = (r["profit"] / r["cost"] * 100) if r["cost"] else None
            age = market.age_days(rec["item_id"]) or 0
            out.append(T("- {name} ({known}) : vend {sale}, coûte {cost} → **{profit}**{margin} · {vol}, "
                         "HV {day}{old}", name=rec["item_name"], vol=volume(e),
                         known=T("connue") if r["known"] else T("à apprendre"), sale=F.money(r["sale"]),
                         cost=F.money(r["cost"]), profit=smoney(r["profit"]),
                         margin=f" ({F.num(margin)} %)" if margin is not None else "", day=price_day(e["day"]),
                         old=" ⚠" + T("{d} j", d=int(age)) if age > PR.OLD_DAYS else ""))
        if priced and priced[0]["profit"] > 0:
            best = priced[0]
            ctx["verdict"].append(T("meilleure vente : {name} (+{p} par fabrication, prix HV du {day})",
                                    name=best["rec"]["item_name"], p=F.money(best["profit"]),
                                    day=price_day(best["entry"]["day"])))
        elif priced:
            ctx["verdict"].append(T("aucune recette rentable aux prix HV relevés"))
        unpriced = [r for r in rows if r["sale"] is not None and not r["cost_known"]]
        if unpriced:
            out.append(T("- Coût incomplet (composant sans prix) : {list}.", list=", ".join(
                r["rec"]["item_name"] for r in unpriced[:5])))
        out += self._raw_or_craft(ctx, rows)
        return out

    def _craft_value(self, ctx: Dict[str, Any], iid: int) -> Optional[Tuple[float, Dict[str, Any]]]:
        """(valeur d'une unité de la matière transformée, ligne de rentabilité) : meilleure recette connue ou
        apprenable dont le produit a un prix HV et dont les autres composants ont tous un prix ; None sinon."""
        cat = ctx["cat"]
        if "profit_rows" not in ctx:
            ctx["profit_rows"] = self._profit_rows(ctx)
        best = None
        for r in ctx["profit_rows"]:
            if r["sale"] is None:
                continue
            uses = sum(g["count"] for g in r["rec"]["reagents"] if g["item_id"] == iid)
            if not uses:
                continue
            others = [cat.unit_cost(g["item_id"]) for g in r["rec"]["reagents"] if g["item_id"] != iid]
            if not all(k for _c, k in others):
                continue
            cnt = [g["count"] for g in r["rec"]["reagents"] if g["item_id"] != iid]
            per_unit = (r["sale"] - sum(c * n for (c, _k), n in zip(others, cnt))) / uses
            if best is None or per_unit > best[0]:
                best = (per_unit, r)
        return best

    def _raw_or_craft(self, ctx: Dict[str, Any], rows: List[Dict[str, Any]]) -> List[str]:
        """Cuir récolté (Dépeçage) en sacs : le vendre brut ou le transformer ?"""
        cat, market, stock = ctx["cat"], ctx["market"], ctx["stock"]
        raws = []
        for iid, n in stock.items():
            it = cat.items.get(iid)
            if it is None:
                cat._load_items([iid])
                it = cat.items.get(iid)
            if it is not None and (it["class_id"], it["subclass_id"]) == LEATHER and n:
                raws.append(iid)
        if not raws:
            return []
        out = [T("**Vendre brut ou fabriquer ?** (matières récoltées en sacs/banque) :")]
        for iid in sorted(raws, key=lambda i: -stock[i]):
            raw_v, raw_src = cat.resale(iid)
            best = self._craft_value(ctx, iid)
            name = f"{cat.item_name(iid)} ×{stock[iid]}"
            if not market.latest(iid):
                self._want_scan(ctx, iid)
            if best is None:
                out.append(T("- {name} : brut {raw} ({src}) ; aucune recette au produit relevé à l'HV pour comparer",
                             name=name, raw=F.money(raw_v), src=T("HV") if raw_src == "hv" else T("marchand")))
            elif best[0] > raw_v:
                out.append(T("- {name} : **fabriquer {prod}** ({v} par unité de matière contre {raw} brut)",
                             name=name, prod=best[1]["rec"]["item_name"], v=smoney(best[0]), raw=F.money(raw_v)))
            else:
                out.append(T("- {name} : **vendre brut** ({raw} pièce ; meilleure recette {prod} : {v} par unité)",
                             name=name, raw=F.money(raw_v), prod=best[1]["rec"]["item_name"], v=smoney(best[0])))
        return out

    # -- c. équipement fabricable pour un perso ------------------------------------------------
    def _market_gear(self, ctx: Dict[str, Any], args: Dict[str, Any], crafter_db: Dict[str, Any]) -> List[str]:
        cat, market = ctx["cat"], ctx["market"]
        gdb = cat.gdb
        if args.get("pour"):
            _c, db = self._char({"perso": args["pour"]})
        else:
            db = crafter_db
        who = F.g(db, "identity", "name") or "?"
        cls = F.g(db, "identity", "classFile") or ""
        level = int(F.g(db, "progression", "level") or F.g(db, "identity", "level") or 1)
        class_bit = 1 << (GDB.CLASS_IDS.get(cls, 0) - 1) if cls in GDB.CLASS_IDS else 0
        seen, cands = set(), []
        for rec in cat.recipes:
            iid = rec["item_id"]
            if iid in seen or rec["rank"] > 300 or not cat.usable(rec) or cat.acquisition(rec)[1] == math.inf:
                continue
            seen.add(iid)
            row = gdb.item(iid)
            if row is None or row["class_id"] not in (2, 4) or not GDB.plausible_item(row):
                continue
            ac = row["allowable_class"]
            if class_bit and ac not in (None, -1, 0) and not (ac & class_bit):
                continue
            req, _est = GDB.effective_req(row)
            if req > level + 5:
                continue
            ev = G.evaluate(db_at_level(db, req) if req > level else db, GDB.to_addon_item(row))
            if ev.get("code") not in G.USEFUL:
                continue
            cands.append((req > level, -ev.get("score", 0), rec, row, ev, req))
        cands.sort(key=lambda c: (c[0], c[1]))
        out = ["", T("**Équipement fabricable pour {who}** ({cls} {lvl}, objets portables jusqu'au niveau {max}) :",
                     who=who, cls=F.g(db, "identity", "class") or cls, lvl=level, max=level + 5)]
        if not cands:
            out.append(T("- Aucun objet de ce métier n'améliore {who} à ce niveau.", who=who))
            return out
        for later, _s, rec, row, ev, req in cands[:8]:
            cost, known = cat.craft_cost(rec)
            missing = [cat.item_name(g["item_id"]) for g in rec["reagents"] if not cat.unit_cost(g["item_id"])[1]]
            if missing:  # la valeur interne de classement n'est jamais affichée comme un prix
                cost = sum(g["count"] * cat.unit_cost(g["item_id"])[0] for g in rec["reagents"]
                           if cat.unit_cost(g["item_id"])[1])
            gain = G.gain_text(ev)
            if rec["rank"] <= ctx["rank"]:
                reach = T("faisable") if (F.norm_key(rec["name"]) in ctx["learned"] or rec["spell_id"] in ctx["learned"]) else T("recette à apprendre")
            else:
                reach = T("{prof} {r} requis, tu es à {cur}", prof=ctx["pname"], r=rec["rank"], cur=ctx["rank"])
            e = market.latest(rec["item_id"])
            if e:
                buy = e["min"]
                choice = T("acheter à l'HV ({p}, {day})", p=F.money(buy), day=price_day(e["day"])) \
                    if known and buy < cost else T("fabriquer (HV : {p}, {day})", p=F.money(buy), day=price_day(e["day"]))
            else:
                choice = T("pas vu à l'HV")
                self._want_scan(ctx, rec["item_id"])
            line = T("- {name} (niv. {req}{later}) → {verdict}{gain} · {reach} · composants {cost}{unk} · {choice}",
                     name=row["name"], req=req, later=T(", plus tard") if later else "", verdict=ev["verdict"],
                     gain=f" ({gain})" if gain else "", reach=reach, cost=F.money(cost),
                     unk=T(" + {list} sans prix", list=", ".join(missing)) if missing else "", choice=choice)
            if row["item_set"]:
                mates = gdb.q("SELECT name FROM items WHERE item_set = ? AND id != ?", (row["item_set"], row["id"]))
                made = [m["name"] for m in mates if any(r["item_name"] == m["name"] for r in cat.recipes)]
                line += " · " + T("**pièce d'ensemble** (autres pièces : {list})",
                                  list=", ".join(made or [m["name"] for m in mates][:4]) or "?")
            out.append(line)
        top = cands[0]
        ctx["verdict"].append(T("pour {who} : {name} ({verdict})", who=who, name=top[3]["name"],
                                verdict=top[4]["verdict"]))
        return out

    # -- d. valeur des sacs ----------------------------------------------------------------------
    def _market_bags(self, ctx: Dict[str, Any]) -> List[str]:
        cat, market, stock = ctx["cat"], ctx["market"], ctx["stock"]
        reagents = {g["item_id"] for r in cat.recipes if cat.usable(r) for g in r["reagents"]}
        products = {r["item_id"] for r in cat.recipes}
        rows = []
        for iid, n in stock.items():
            it = cat.items.get(iid)
            if iid not in reagents and iid not in products:
                if it is None:
                    cat._load_items([iid])
                    it = cat.items.get(iid)
                if it is None or (it["class_id"], it["subclass_id"]) != LEATHER:
                    continue
            rows.append((iid, n))
        out = ["", T("**Sacs et banque : matières et produits du métier**")]
        if not rows:
            out.append(T("- Rien qui concerne ce métier."))
            return out
        known = [r for r in cat.recipes if cat.usable(r) and (F.norm_key(r["name"]) in ctx["learned"] or r["spell_id"] in ctx["learned"])
                 and PP.color_at(max(ctx["rank"], 1), r) in (0, 1, 2)]
        plan_raw = ctx.get("plan_raw") or {}
        for iid, n in sorted(rows, key=lambda x: -(cat.resale(x[0])[0] * x[1])):
            vendor = (cat.items[iid]["sell_price"] if iid in cat.items else 0) or 0
            ah = market.sell_net(iid)
            e = market.latest(iid)
            uses = [r["name"] for r in known if any(g["item_id"] == iid for g in r["reagents"])]
            craft = self._craft_value(ctx, iid)
            if plan_raw.get(iid):
                verdict = T("garder : le parcours de montée en utilise {n}", n=plan_raw[iid])
            elif craft and craft[0] > max(ah or 0, vendor):
                verdict = T("fabriquer {prod} ({v} par unité, contre {raw} en la vendant)",
                            prod=craft[1]["rec"]["item_name"], v=smoney(craft[0]), raw=F.money(max(ah or 0, vendor)))
            elif uses:
                verdict = T("garder : sert à {list} (recette connue qui donne encore des points)",
                            list=", ".join(uses[:2]))
            elif ah and ah > vendor:
                verdict = T("HV ({p} pièce net, relevé du {day})", p=F.money(ah), day=price_day(e["day"]))
            elif ah is not None:
                verdict = T("marchand ({p} pièce, plus que l'HV net)", p=F.money(vendor))
            else:
                verdict = T("marchand {p} pièce ; prix HV inconnu", p=F.money(vendor)) if vendor else \
                    T("prix HV inconnu, invendable au marchand")
                self._want_scan(ctx, iid)
            out.append(f"- {cat.item_name(iid)} ×{n}{F.sep()}{verdict}")
        return out

    # -- objets à relever -----------------------------------------------------------------------
    def _market_scan_list(self, ctx: Dict[str, Any]) -> List[str]:
        cat = ctx["cat"]
        ids = ctx["scan"][:10]
        if not ids:
            return []
        ctx["verdict"].insert(0, T("aucun prix HV relevé : ouvre l'HV et cherche {list}", list=", ".join(
            cat.item_name(i) for i in ids[:3])))
        return ["", T("**À chercher à l'HV en priorité** (l'addon note les prix affichés) : {list}.",
                      list=", ".join(f"{cat.item_name(i)} (id {i})" for i in ids))]


# ---------------------------------------------------------------------------
# traductions anglaises de ce module

MARKET_EN = {
    "vue inconnue : {v} (tout, monter, profit, equipement, sacs)":
        "unknown view: {v} (tout, monter, profit, equipement, sacs)",
    "Métier « {m} » inconnu de la base locale.": "Profession \"{m}\" is unknown to the local database.",
    "{prof} est un métier de récolte : demande `market` sur le métier d'artisanat "
    "qui utilise ses matières (ex. Travail du cuir pour le Dépeçage).":
        "{prof} is a gathering profession: call `market` on the crafting profession that uses its materials "
        "(e.g. Leatherworking for Skinning).",
    "Prix HV = le plus bas du dernier relevé de l'addon (revente nette de 5 % de commission "
    "[Classic]) ; un prix HV bouge vite et n'est jamais garanti : vérifie avant d'acheter "
    "en gros. Prix marchands et recettes : [Forever · base locale]. Parcours : couleurs et "
    "fabrications comme l'outil professions (règles [Classic] à vérifier dans Forever).":
        "AH price = lowest of the addon's latest scan (resale net of the 5% cut [Classic]); AH prices move fast "
        "and are never guaranteed: check before buying in bulk. Vendor prices and recipes: [Forever · local DB]. "
        "Path: colors and crafts as in the professions tool ([Classic] rules, to check in Forever).",
    "rien à conseiller sans prix ni recette exploitable": "nothing to advise without prices or a usable recipe",
    "**Aucun prix HV relevé** pour {realm} ({faction}) : seuls les prix marchands servent "
    "[Forever · base locale]. Ouvre l'hôtel des ventes avec ForeverScribe actif et cherche les "
    "objets listés en bas.":
        "**No AH price recorded** for {realm} ({faction}): only vendor prices are used [Forever · local DB]. "
        "Open the auction house with ForeverScribe enabled and search for the items listed at the bottom.",
    "Prix HV : {n} objets relevés, dernier relevé le {day} ({age}) [Forever · tes relevés HV du {day}].":
        "AH prices: {n} items recorded, latest scan on {day} ({age}) [Forever · your AH scans of {day}].",
    "⚠ relevé de plus de {d} jours : repasse à l'HV.": "⚠ scan older than {d} days: visit the AH again.",
    "{price} HV {day}": "{price} AH {day}",
    "{d} j": "{d} d",
    "{price} marchand": "{price} vendor",
    "{price} en le fabriquant": "{price} if you craft it",
    "prix inconnu": "unknown price",
    "**Monter {prof} de {a} à {b} au meilleur prix** (coût net par point = composants à acheter "
    "− revente du produit, revente HV limitée à la moitié du volume vu) :":
        "**Level {prof} from {a} to {b} at the best price** (net cost per point = reagents to buy − product "
        "resale, AH resale capped at half the volume seen):",
    "- {a} → {b} : aucune recette connue de la base ne donne de points ici.":
        "- {a} → {b}: no recipe known to the database gives points here.",
    "connue": "known", "formateur": "trainer", "patron marchand": "vendor pattern",
    "patron (butin/réputation)": "pattern (drop/reputation)", "source inconnue": "unknown source",
    "{n}. **{a} → {b}** · {name} ({known}, {col}) · ~{crafts} fabrications · net : "
    "prix incomplet ({list} sans prix)":
        "{n}. **{a} → {b}** · {name} ({known}, {col}) · ~{crafts} crafts · net: incomplete price ({list} unpriced)",
    "{n}. **{a} → {b}** · {name} ({known}, {col}) · ~{crafts} fabrications · net {net} "
    "({per} par point)":
        "{n}. **{a} → {b}** · {name} ({known}, {col}) · ~{crafts} crafts · net {net} ({per} per point)",
    "revente {price} pièce ({src})": "resale {price} each ({src})",
    "revente HV {price} pièce net ({day}{old}, {vol} : {k} à écouler)":
        "AH resale {price} each net ({day}{old}, {vol}: {k} to sell)",
    "{qty} en vente, prix plancher (vue de navigation)": "{qty} for sale, floor price (browse view)",
    "vu {qty} en {n} annonce(s)": "seen {qty} in {n} listing(s)",
    " (en jeu)": " (in game)",
    "monter {prof} de {a} à {b} : {buy} d'achats{basis}, et ≈ {gain} de gain net "
    "si tu revends les produits":
        "levelling {prof} from {a} to {b}: {buy} of purchases{basis}, and ≈ {gain} net gain if you sell the "
        "products",
    "fabriquer {prod} ({v} par unité, contre {raw} en la vendant)":
        "craft {prod} ({v} per unit, vs {raw} if you sell it)",
    "HV": "AH", "marchand": "vendor",
    "pas de revente connue": "no known resale",
    "Composants : {list} · {sale}": "Reagents: {list} · {sale}",
    "Patron de {name} — marchand → {total}": "Pattern for {name} — vendor → {total}",
    "Patron à acheter chez un marchand : {price} (compté dans le coût).":
        "Pattern to buy from a vendor: {price} (included in the cost).",
    " (tu en as {n})": " (you have {n})",
    "{qty} {name}{have} — déjà en sacs": "{qty} {name}{have} — already in bags",
    "{need} {name}{have} — {note} → {total}": "{need} {name}{have} — {note} → {total}",
    "{need} {name}{have} — prix inconnu : à récolter ou à relever à l'HV":
        "{need} {name}{have} — unknown price: gather it or check it at the AH",
    "À fabriquer en route : {list}.": "To craft along the way: {list}.",
    "**À acheter ou récolter** (total du parcours, stock des sacs et de la banque déduit) :":
        "**To buy or gather** (whole path, bags and bank stock deducted):",
    "**Coût estimé** : achats {buy} − revente des produits {resale} = **{net} net**.":
        "**Estimated cost**: purchases {buy} − product resale {resale} = **{net} net**.",
    "monter {prof} de {a} à {b} coûte ≈ {net} net{basis}": "levelling {prof} from {a} to {b} costs ≈ {net} net{basis}",
    " (prix HV + marchand)": " (AH + vendor prices)",
    " (prix marchands seulement)": " (vendor prices only)",
    "**Rentabilité** (recettes connues ou apprenables à {rank} ; profit = revente HV − 5 % − "
    "composants au moins cher) :":
        "**Profitability** (recipes known or learnable at {rank}; profit = AH resale − 5% − cheapest reagents):",
    "- Aucun produit de ces recettes n'a de prix HV relevé : profit impossible à calculer.":
        "- None of these products has a recorded AH price: profit cannot be computed.",
    "- {name} ({known}) : vend {sale}, coûte {cost} → **{profit}**{margin} · {vol}, "
    "HV {day}{old}":
        "- {name} ({known}): sells {sale}, costs {cost} → **{profit}**{margin} · {vol}, AH {day}{old}",
    "à apprendre": "to learn",
    "meilleure vente : {name} (+{p} par fabrication, prix HV du {day})":
        "best seller: {name} (+{p} per craft, AH price of {day})",
    "aucune recette rentable aux prix HV relevés": "no profitable recipe at the recorded AH prices",
    "- Coût incomplet (composant sans prix) : {list}.": "- Incomplete cost (reagent without a price): {list}.",
    "**Vendre brut ou fabriquer ?** (matières récoltées en sacs/banque) :":
        "**Sell raw or craft?** (gathered materials in bags/bank):",
    "- {name} : brut {raw} ({src}) ; aucune recette au produit relevé à l'HV pour comparer":
        "- {name}: raw {raw} ({src}); no recipe whose product has an AH price to compare",
    "- {name} : **fabriquer {prod}** ({v} par unité de matière contre {raw} brut)":
        "- {name}: **craft {prod}** ({v} per unit of material vs {raw} raw)",
    "- {name} : **vendre brut** ({raw} pièce ; meilleure recette {prod} : {v} par unité)":
        "- {name}: **sell raw** ({raw} each; best recipe {prod}: {v} per unit)",
    "**Équipement fabricable pour {who}** ({cls} {lvl}, objets portables jusqu'au niveau {max}) :":
        "**Craftable gear for {who}** ({cls} {lvl}, items wearable up to level {max}):",
    "- Aucun objet de ce métier n'améliore {who} à ce niveau.":
        "- No item of this profession is an upgrade for {who} at this level.",
    "faisable": "craftable", "recette à apprendre": "recipe to learn",
    "{prof} {r} requis, tu es à {cur}": "{prof} {r} required, you are at {cur}",
    "acheter à l'HV ({p}, {day})": "buy it at the AH ({p}, {day})",
    "fabriquer (HV : {p}, {day})": "craft it (AH: {p}, {day})",
    "pas vu à l'HV": "not seen at the AH",
    "- {name} (niv. {req}{later}) → {verdict}{gain} · {reach} · composants {cost}{unk} · {choice}":
        "- {name} (lvl {req}{later}) → {verdict}{gain} · {reach} · reagents {cost}{unk} · {choice}",
    ", plus tard": ", later",
    " + {list} sans prix": " + {list} without a price",
    "**pièce d'ensemble** (autres pièces : {list})": "**set piece** (other pieces: {list})",
    "pour {who} : {name} ({verdict})": "for {who}: {name} ({verdict})",
    "**Sacs et banque : matières et produits du métier**": "**Bags and bank: materials and products of the profession**",
    "- Rien qui concerne ce métier.": "- Nothing related to this profession.",
    "garder : le parcours de montée en utilise {n}": "keep: the levelling path uses {n}",
    "garder : sert à {list} (recette connue qui donne encore des points)":
        "keep: used by {list} (known recipe that still gives points)",
    "ton royaume": "your realm",
    "Royaume absent de la capture : relevés de {realm} ({faction}) utilisés.":
        "Realm missing from the capture: scans of {realm} ({faction}) used.",
    "**Coût estimé** : achats connus {buy} + {n} composant(s) sans prix (à récolter ou relever) ; "
    "revente possible des produits {resale}. Pas de total net tant que ces prix manquent.":
        "**Estimated cost**: known purchases {buy} + {n} reagent(s) without a price (gather or scan them); "
        "possible product resale {resale}. No net total while these prices are missing.",
    "monter {prof} de {a} à {b} : {buy} d'achats connus{basis} + {list} à récolter "
    "ou à relever à l'HV":
        "levelling {prof} from {a} to {b}: {buy} of known purchases{basis} + {list} to gather or check at the AH",
    "HV ({p} pièce net, relevé du {day})": "AH ({p} each net, scan of {day})",
    "marchand ({p} pièce, plus que l'HV net)": "vendor ({p} each, more than the AH net)",
    "marchand {p} pièce ; prix HV inconnu": "vendor {p} each; AH price unknown",
    "prix HV inconnu, invendable au marchand": "AH price unknown, cannot be sold to a vendor",
    "aucun prix HV relevé : ouvre l'HV et cherche {list}": "no AH price recorded: open the AH and search for {list}",
    "**À chercher à l'HV en priorité** (l'addon note les prix affichés) : {list}.":
        "**Search the AH for these first** (the addon records the prices shown): {list}.",
    "Verdict :": "Verdict:",
    "{name} n'a pas {prof} : parcours depuis 1": "{name} does not have {prof}: path from 1",
}
for _k, _v in MARKET_EN.items():
    EN.setdefault(_k, _v)
