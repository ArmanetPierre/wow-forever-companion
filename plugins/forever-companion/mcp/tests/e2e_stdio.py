"""Test de bout en bout : lance server.py en sous-processus et lui parle en JSON-RPC (stdio).

Usage : python3 tests/e2e_stdio.py [--data-dir DIR] [--show] [--lang en|fr] [--client frFR|enUS]
Sans --data-dir, construit un faux dossier WoW + perso/ temporaires à partir des fixtures
(addon/tests/fixtures) : le test ne dépend ni du jeu ni de tes données.
Avec --data-dir, teste sur un vrai dossier de données (ex. ~/WowForever/perso).
--lang en : chaque appel demande une réponse en anglais (fragments attendus en anglais).
--client enUS : bac à sable avec la capture d'un client anglais et une base du jeu anglaise.
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE.parent / "server.py"
FIXTURES = HERE.parents[3] / "addon" / "tests" / "fixtures"
ACC = "123456789#1"


def build_sandbox(client: str = "frFR") -> Path:
    """Faux dossier WoW + perso/ à partir des fixtures ; renvoie le dossier temporaire."""
    tmp = Path(tempfile.mkdtemp(prefix="forever-e2e-"))
    wow = tmp / "World of Warcraft" / "_forever_"
    acc = wow / "WTF" / "Account" / ACC
    (acc / "SavedVariables").mkdir(parents=True)
    shutil.copy(FIXTURES / "account_SavedVariables_ForeverScribe.lua", acc / "SavedVariables" / "ForeverScribe.lua")
    char = acc / "93" / "Brannok-Durn" / "SavedVariables"
    char.mkdir(parents=True)
    suffix = "" if client == "frFR" else f".{client}"
    shutil.copy(FIXTURES / f"character_SavedVariables_ForeverScribe{suffix}.lua", char / "ForeverScribe.lua")
    data = tmp / "perso"
    data.mkdir()
    (data / "config.json").write_text(json.dumps({"wowPaths": [str(wow.parent)], "accounts": {ACC: "Alex"}}),
                                      encoding="utf-8")
    return tmp

CALLS = [
    ("list_characters", {}),
    ("get_character", {}),
    ("get_stats", {}),
    ("get_equipment", {}),
    ("get_talents", {}),
    ("get_spells", {"ligne": "Précision"}),
    ("get_quests", {"zone": "Paluns"}),
    ("get_quests", {}),
    ("get_professions", {}),
    ("get_inventory", {}),
    ("get_reputations", {}),
    ("get_pet", {}),
    ("get_progress", {"depuis": "semaine"}),
    ("compare_item", {"nom": "Arbalète de points dissimulés", "emplacement": "distance", "dps": 15.2,
                      "pa_distance": 12}),
    ("compare_item", {"nom": "Gants test", "emplacement": "mains", "agilite": 7, "endurance": 2}),
    ("get_overview", {}),
    ("get_quest_rewards", {}),
    ("get_quest_rewards", {"a_rendre": True}),
    ("save_knowledge", {"sujet": "Test e2e : casques en cuir", "contenu": "Note de test du bac à sable.",
                        "sources": ["test"], "certitude": "probable [Classic, à confirmer dans Forever]"}),
    ("search_knowledge", {"question": "casque cuir"}),
    ("compare_characters", {}),
    ("find_items", {"nom": "essai"}),
    ("get_item", {"itemId": 1001}),
    ("find_upgrades", {}),
    ("get_dungeon_loot", {"donjon": "Donjon d'essai"}),
    ("find_recipes", {"metier": "Travail du cuir"}),
    ("get_quest_info", {"questId": 1}),
    ("compare_item", {"itemId": 1002}),
    ("set_active_character", {"perso": "Brannok"}),
    ("get_character", {"perso": "inconnu"}),  # erreur attendue
]


# Sur les fixtures, chaque réponse doit contenir ces fragments (vérifiés seulement dans le bac à sable).
EXPECT = {
    ("get_quests", 1): ["Récompense : à prendre : **Arc des marais**"],
    ("get_overview", 0): ["Quêtes à rendre", "Arc des marais", "Emplacements vides", "Pistes d'amélioration"],
    ("get_quest_rewards", 0): ["À rendre maintenant", "Arc des marais", "Robe du marin", "Forgefer +250",
                              "fixe : Potion de soins"],
    ("search_knowledge", 0): ["Test e2e : casques en cuir", "probable"],
    ("find_upgrades", 0): ["[Forever · base locale]", "Casque d'essai"],
    ("get_item", 0): ["+10 Agi", "Donjon d'essai"],
    ("get_dungeon_loot", 0): ["Boss d'essai", "Casque d'essai"],
    ("find_recipes", 0): ["Ceinture fabriquée", "Cuir d'essai"],
    ("get_quest_info", 0): ["Quête d'essai"],
    ("compare_item", 2): ["Fusil d'essai"],
}
# Mêmes appels, réponse demandée en anglais (capture d'un client français : les noms restent en français).
EXPECT_EN = {
    ("get_quests", 1): ["Reward: take: **Arc des marais**"],
    ("get_overview", 0): ["Quests to turn in", "Arc des marais", "Empty slots", "Upgrade leads"],
    ("get_quest_rewards", 0): ["Turn in now", "Arc des marais", "Robe du marin", "Forgefer +250",
                              "fixed: Potion de soins"],
    ("find_upgrades", 0): ["[Forever · local DB]", "Casque d'essai"],
    ("get_item", 0): ["+10 Agi", "Donjon d'essai"],
    ("get_dungeon_loot", 0): ["Boss d'essai", "Casque d'essai"],
    ("find_recipes", 0): ["Ceinture fabriquée", "Cuir d'essai"],
    ("compare_item", 2): ["Fusil d'essai"],
}
# Client anglais : paramètres et fragments propres à la base anglaise synthétique.
CALLS_ENUS = {"get_dungeon_loot": {"donjon": "Trial Dungeon"}, "find_items": {"nom": "trial"},
              "find_recipes": {"metier": "Leatherworking"}, "get_quests": None}
EXPECT_ENUS = {
    ("get_overview", 0): ["Quests to turn in", "Cleansing the Land", "Empty slots"],
    ("find_upgrades", 0): ["[Forever · local DB]", "Trial Helm"],
    ("get_dungeon_loot", 0): ["Trial Boss", "Trial Helm"],
    ("find_recipes", 0): ["Crafted Belt", "Trial Leather"],
    ("get_quest_info", 0): ["Trial Quest"],
    ("compare_item", 2): ["Trial Rifle"],
}
# Outils de la base locale : en vrai dossier de données, appelés avec des ids réels au besoin.
GAMEDB_SANDBOX_ONLY = {"get_item", "get_dungeon_loot", "get_quest_info"}
SANDBOX_ONLY = {"set_active_character", "save_knowledge"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir")
    ap.add_argument("--show", action="store_true", help="affiche les réponses complètes")
    ap.add_argument("--lang", choices=["fr", "en"], help="langue de réponse demandée à chaque appel")
    ap.add_argument("--client", choices=["frFR", "enUS"], default="frFR", help="langue du client simulé")
    args = ap.parse_args()
    expect = EXPECT
    if args.client == "enUS":
        expect = EXPECT_ENUS if args.lang != "fr" else {}
    elif args.lang == "en":
        expect = EXPECT_EN
    env = dict(os.environ)
    sandbox = None
    if args.data_dir:
        env["FOREVER_DATA_DIR"] = args.data_dir
    else:
        sandbox = build_sandbox(args.client)
        env["FOREVER_DATA_DIR"] = str(sandbox / "perso")
        sys.path.insert(0, str(HERE.parents[1] / "gamedata" / "tests"))
        import synthetic  # données inventées, pas de données du jeu
        dbp = sandbox / "gamedata" / f"forever-{args.client}.sqlite"
        synthetic.make_db(dbp, args.client)
        env["FOREVER_GAMEDB"] = str(dbp)
    proc = subprocess.Popen([sys.executable, str(SERVER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, text=True, encoding="utf-8")
    n = 0

    def rpc(method, params=None, notify=False):
        nonlocal n
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            n += 1
            msg["id"] = n
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        if notify:
            return None
        return json.loads(proc.stdout.readline())

    failures = 0
    init = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                              "clientInfo": {"name": "e2e", "version": "1"}})
    assert init["result"]["protocolVersion"] == "2025-06-18", init
    rpc("notifications/initialized", notify=True)
    tools = rpc("tools/list")["result"]["tools"]
    names = {t["name"] for t in tools}
    print(f"initialize OK · {len(tools)} outils : {', '.join(sorted(names))}")
    seen = {}
    for name, params in CALLS:
        if args.client == "enUS" and name in CALLS_ENUS and not (name == "get_quests" and params):
            params = CALLS_ENUS[name] if CALLS_ENUS[name] is not None else params
        if args.lang:
            params = {**params, "lang": args.lang}
        if (name in SANDBOX_ONLY or (name in GAMEDB_SANDBOX_ONLY) or params.get("itemId") in (1001, 1002)) \
                and not sandbox:
            continue  # perso d'exemple et écriture : seulement dans le bac à sable
        idx = seen.get(name, 0)
        seen[name] = idx + 1
        res = rpc("tools/call", {"name": name, "arguments": params})
        if "error" in res:
            print(f"✘ {name} : erreur JSON-RPC {res['error']}")
            failures += 1
            continue
        r = res["result"]
        text = r["content"][0]["text"]
        expected_error = params.get("perso") == "inconnu"
        ok = r["isError"] == expected_error
        missing = [w for w in expect.get((name, idx), []) if w not in text] if sandbox else []
        if missing:
            print(f"   fragments absents : {missing}")
            ok = False
        failures += 0 if ok else 1
        print(f"{'✔' if ok else '✘'} {name} {json.dumps(params, ensure_ascii=False)} → {len(text)} car."
              + (" (erreur attendue)" if expected_error else ""))
        if args.show or not ok:
            print(text, "\n")
    unknown = rpc("tools/call", {"name": "nexiste_pas", "arguments": {}})
    failures += 0 if "error" in unknown else 1
    proc.stdin.close()
    proc.wait(timeout=10)
    err = proc.stderr.read()
    if "Traceback" in err:
        print(err)
        failures += 1
    if sandbox:
        shutil.rmtree(sandbox, ignore_errors=True)
    print("RÉSULTAT :", "OK" if not failures else f"{failures} échec(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
