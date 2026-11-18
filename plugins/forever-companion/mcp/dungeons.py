"""Table de référence des donjons et raids (knowledge/donjons.json) : noms FR/EN, niveaux, ouverture.

Le client Forever liste des cartes de test et des raids pas encore ouverts, et ne connaît pas toutes les
fourchettes de niveau : cette table sert de référence aux outils `dungeon` et `search`.
Bibliothèque standard uniquement.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import formats as F
import i18n as I
from i18n import T

PATH = Path(__file__).resolve().parent.parent / "knowledge" / "donjons.json"
_CACHE: Dict[str, Any] = {}

# Cartes du client qui ne sont pas du contenu jouable de Forever (tests, Season of Discovery, scénarios).
TEST_MARKERS = ("test", "cashtest", "unused")


def _key(text: Any) -> str:
    """norm_key qui garde les ligatures (« Cœur » → « coeur » et non « cur »)."""
    s = str(text or "")
    for a, b in (("œ", "oe"), ("Œ", "Oe"), ("æ", "ae"), ("Æ", "Ae")):
        s = s.replace(a, b)
    return F.norm_key(s)


def instances() -> List[Dict[str, Any]]:
    try:
        mtime = PATH.stat().st_mtime
    except OSError:
        return []
    if _CACHE.get("mtime") != mtime:
        try:
            data = json.loads(PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        lst = []
        for d in data.get("instances") or []:
            d = dict(d)
            names = [d.get("fr"), d.get("en"), *(d.get("alias") or [])]
            d["_names"] = {f(x) for x in names if x for f in (F.norm_key, _key)}
            lst.append(d)
        guides = data.get("guides") if isinstance(data.get("guides"), dict) else {}
        _CACHE.update(mtime=mtime, list=lst, guides=guides)
    return _CACHE.get("list") or []


def guide(d: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Guide sourcé d'une instance (butin par boss, mécaniques, quêtes), clé = nom anglais ; None sinon."""
    if not d:
        return None
    instances()
    g = (_CACHE.get("guides") or {}).get(d.get("en"))
    return g if isinstance(g, dict) and g.get("boss") else None


def guide_items() -> List[Dict[str, Any]]:
    """Objets de butin des guides : {id, en, instance, boss} (sert à la recherche par nom anglais)."""
    out = []
    for d in instances():
        g = guide(d)
        for b in (g or {}).get("boss") or []:
            for it in b.get("butin") or []:
                if isinstance(it, dict) and it.get("id"):
                    out.append({"id": int(it["id"]), "en": it.get("en") or "", "instance": d, "boss": b})
    return out


def guide_source(g: Dict[str, Any]) -> str:
    """« guide Method du 14/11/2026, probable » pour l'en-tête du butin."""
    host = str(g.get("source") or "").split("//")[-1].split("/")[0].replace("www.", "")
    date = str(g.get("date") or "")
    if len(date) == 10:
        date = f"{date[8:10]}/{date[5:7]}/{date[:4]}"
    return T("guide {host} du {date}, {cert}", host=host or "?", date=date or "?",
             cert=g.get("certitude") or "probable")


def sources_label(sources: Any, cert: Any = None) -> str:
    """« warcrafttavern.com, method.gg · probable » pour le badge d'un bloc du guide (entrée, dangers)."""
    hosts: List[str] = []
    for u in sources if isinstance(sources, list) else [sources]:
        h = str(u or "").split("//")[-1].split("/")[0].replace("www.", "")
        if h and h not in hosts:
            hosts.append(h)
    return ", ".join(hosts or ["?"]) + " · " + str(cert or "probable")


def by_map(map_id: Any) -> Optional[Dict[str, Any]]:
    for d in instances():
        if d.get("map_id") is not None and d.get("map_id") == map_id:
            return d
    return None


def by_name(name: Any) -> Optional[Dict[str, Any]]:
    n = _key(name)
    if not n:
        return None
    for d in instances():
        if n in d["_names"]:
            return d
    hits = find(name, 1)
    return hits[0] if hits else None


def find(text: Any, limit: int = 3) -> List[Dict[str, Any]]:
    """Donjons dont un nom (FR, EN, alias) contient tous les mots de la recherche (débuts de mots)."""
    n = _key(text)
    toks = n.split()
    if not toks:
        return []
    out = []
    for d in instances():
        for name in d["_names"]:
            words = name.split()
            if name == n or all(any(w.startswith(t) for w in words) for t in toks):
                out.append(d)
                break
    out.sort(key=lambda d: 0 if n in d["_names"] else 1)
    return out[:limit]


def is_test_map(name: Any) -> bool:
    n = F.norm_key(name)
    return any(m in n.split() or n.startswith(m) for m in TEST_MARKERS)


def loc(d: Dict[str, Any], key: str) -> Any:
    """Champ dans la langue de réponse : zone/zone_en, note/note_en ; « name » = fr/en."""
    en = I.get_lang() == "en"
    if key == "name":
        return (d.get("en") if en else d.get("fr")) or d.get("fr") or d.get("en")
    return (d.get(f"{key}_en") if en else None) or d.get(key)


def badge(d: Dict[str, Any]) -> str:
    return "[Forever]" if d.get("badge") == "forever" else T("[Classic · à vérifier dans Forever]")


def levels_text(d: Dict[str, Any]) -> str:
    lv = f"{d['min']}-{d['max']}" if d.get("min") != d.get("max") else str(d.get("min"))
    txt = T("niveaux {lv}", lv=lv) if d.get("min") != d.get("max") else T("niveau {lv}", lv=lv)
    if d.get("kind") == "raid" and d.get("players"):
        txt = T("raid {n} joueurs", n=d["players"]) + ", " + txt
    st = status_text(d)
    return txt + (f", {st}" if st else "")


def status_text(d: Dict[str, Any]) -> str:
    st = d.get("status") or "open"
    if st.startswith("opens:"):
        y, m, dd = (st.split(":", 1)[1].split("-") + ["", "", ""])[:3]
        return T("ouvre le {date}", date=f"{dd}/{m}/{y}")
    if st == "not_open":
        return T("pas encore ouvert dans Forever")
    return ""


def is_open(d: Dict[str, Any]) -> bool:
    return (d.get("status") or "open") == "open"


def verdict(d: Dict[str, Any], lvl: Any, name: str) -> str:
    """Opportunité d'y aller à ce niveau, d'après la fourchette conseillée."""
    a, b = d.get("min"), d.get("max")
    if not is_open(d):
        return T("{name} : {status}", name=name, status=status_text(d))
    if not isinstance(lvl, int) or a is None:
        return T("{name} : {levels}", name=name, levels=levels_text(d))
    if lvl < a - 1:
        return T("{name} ({a}-{b}), toi {lvl} : encore tôt, reviens vers le niveau {a}", name=name, a=a, b=b, lvl=lvl)
    if lvl > b + 3:
        return T("{name} ({a}-{b}), toi {lvl} : trop bas pour toi, peu d'XP ; seulement pour les quêtes ou un objet",
                 name=name, a=a, b=b, lvl=lvl)
    if lvl > b:
        return T("{name} ({a}-{b}), toi {lvl} : fin de fourchette, facile, fais-le pour les quêtes",
                 name=name, a=a, b=b, lvl=lvl)
    return T("{name} ({a}-{b}), toi {lvl} : c'est le bon moment, en groupe de 5 avec les quêtes prises avant",
             name=name, a=a, b=b, lvl=lvl)
