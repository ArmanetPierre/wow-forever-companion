"""Test de bout en bout : lance server.py en sous-processus et lui parle en JSON-RPC (stdio).

Usage : python3 tests/e2e_stdio.py [--data-dir DIR] [--show]
Sans --data-dir, construit un faux dossier WoW + perso/ temporaires à partir des fixtures
(addon/tests/fixtures) : le test ne dépend ni du jeu ni de tes données.
Avec --data-dir, teste sur un vrai dossier de données (ex. ~/WowForever/perso).
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


def build_sandbox() -> Path:
    """Faux dossier WoW + perso/ à partir des fixtures ; renvoie le dossier temporaire."""
    tmp = Path(tempfile.mkdtemp(prefix="forever-e2e-"))
    wow = tmp / "World of Warcraft" / "_forever_"
    acc = wow / "WTF" / "Account" / ACC
    (acc / "SavedVariables").mkdir(parents=True)
    shutil.copy(FIXTURES / "account_SavedVariables_ForeverScribe.lua", acc / "SavedVariables" / "ForeverScribe.lua")
    char = acc / "93" / "Brannok-Durn" / "SavedVariables"
    char.mkdir(parents=True)
    shutil.copy(FIXTURES / "character_SavedVariables_ForeverScribe.lua", char / "ForeverScribe.lua")
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
    ("get_professions", {}),
    ("get_inventory", {}),
    ("get_reputations", {}),
    ("get_pet", {}),
    ("get_progress", {"depuis": "semaine"}),
    ("compare_item", {"nom": "Arbalète de points dissimulés", "emplacement": "distance", "dps": 15.2,
                      "pa_distance": 12}),
    ("compare_item", {"nom": "Gants test", "emplacement": "mains", "agilite": 7, "endurance": 2}),
    ("compare_characters", {}),
    ("set_active_character", {"perso": "Brannok"}),
    ("get_character", {"perso": "inconnu"}),  # erreur attendue
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir")
    ap.add_argument("--show", action="store_true", help="affiche les réponses complètes")
    args = ap.parse_args()
    env = dict(os.environ)
    sandbox = None
    if args.data_dir:
        env["FOREVER_DATA_DIR"] = args.data_dir
    else:
        sandbox = build_sandbox()
        env["FOREVER_DATA_DIR"] = str(sandbox / "perso")
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
    for name, params in CALLS:
        if name == "set_active_character" and not sandbox:
            continue  # le perso d'exemple n'existe que dans le bac à sable
        res = rpc("tools/call", {"name": name, "arguments": params})
        if "error" in res:
            print(f"✘ {name} : erreur JSON-RPC {res['error']}")
            failures += 1
            continue
        r = res["result"]
        text = r["content"][0]["text"]
        expected_error = params.get("perso") == "inconnu"
        ok = r["isError"] == expected_error
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
