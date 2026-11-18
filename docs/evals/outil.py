"""Appelle un outil du serveur MCP du compagnon en ligne de commande (banc d'essai).

Sert aux évaluations avec un modèle : l'agent de test appelle les outils du serveur en
développement exactement comme le ferait Claude Code, mais via le shell.

Usage :
    python3 docs/evals/outil.py --list
    python3 docs/evals/outil.py overview '{"detail": "court"}'
    python3 docs/evals/outil.py quests '{"titre": "Découverte du passé"}' --data-dir ~/WowForever/perso

Par défaut, le dossier de données suit la même règle que le serveur
(FOREVER_DATA_DIR, puis ./perso, puis ~/WowForever/perso). Bibliothèque standard uniquement.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SERVER = REPO / "plugins" / "forever-companion" / "mcp" / "server.py"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tool", nargs="?")
    ap.add_argument("args", nargs="?", default="{}")
    ap.add_argument("--list", action="store_true", help="liste les outils et leurs paramètres")
    ap.add_argument("--data-dir")
    ap.add_argument("--server", default=str(SERVER))
    a = ap.parse_args()
    for _stream in (sys.stdout, sys.stderr):  # sortie redirigée sous Windows = cp1252
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    env = dict(os.environ)
    if a.data_dir:
        env["FOREVER_DATA_DIR"] = str(Path(a.data_dir).expanduser())

    msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                        "clientInfo": {"name": "outil.py", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"}]
    if a.list or not a.tool:
        msgs.append({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    else:
        try:
            args = json.loads(a.args)
        except json.JSONDecodeError as e:
            print(f"Arguments JSON invalides : {e}", file=sys.stderr)
            return 2
        msgs.append({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                     "params": {"name": a.tool, "arguments": args}})

    proc = subprocess.run([sys.executable, a.server],
                          input="\n".join(json.dumps(m) for m in msgs) + "\n",
                          capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)
    resp = None
    for line in proc.stdout.splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("id") == 2:
            resp = obj
    if resp is None:
        print(proc.stderr or "Pas de réponse du serveur.", file=sys.stderr)
        return 1
    if "error" in resp:
        print(json.dumps(resp["error"], ensure_ascii=False), file=sys.stderr)
        return 1
    res = resp["result"]
    if "tools" in res:
        for t in res["tools"]:
            props = ", ".join(t.get("inputSchema", {}).get("properties", {}))
            print(f"- {t['name']}({props}) : {t.get('description', '').splitlines()[0]}")
        return 0
    for c in res.get("content", []):
        if c.get("type") == "text":
            print(c["text"])
    return 1 if res.get("isError") else 0


if __name__ == "__main__":
    sys.exit(main())
