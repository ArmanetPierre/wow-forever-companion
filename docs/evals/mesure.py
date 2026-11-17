"""Mesure le coût des séquences d'outils MCP du compagnon (appels, taille, durée, redondance).

Rejoue, sans modèle, la séquence d'outils qu'un agent appelle pour chaque question type
(fichier JSON de séquences), et sort un tableau Markdown comparable avant/après une
optimisation. Bibliothèque standard uniquement.

Usage :
    python3 docs/evals/mesure.py                         # bac à sable (fixtures, données inventées)
    python3 docs/evals/mesure.py --data-dir ~/WowForever/perso --gamedb ~/WowForever/gamedata/forever-frFR.sqlite
    python3 docs/evals/mesure.py --server <autre server.py> --sequences docs/evals/sequences-v0.5.json --json out.json

Tokens estimés = caractères / 3,5 (texte français avec accents et tableaux Markdown ;
c'est une estimation pour comparer, pas un décompte exact).
Redondance = caractères des lignes déjà vues dans une réponse précédente de la même question
(en-têtes répétés, mêmes quêtes listées deux fois…).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_SERVER = REPO / "plugins" / "forever-companion" / "mcp" / "server.py"
CHARS_PER_TOKEN = 3.5


def tok(chars: int) -> int:
    return round(chars / CHARS_PER_TOKEN)


def sandbox(server: Path):
    """Bac à sable des tests e2e (fixtures + base synthétique) ; renvoie (tmp, env)."""
    tests = server.parent / "tests"
    sys.path.insert(0, str(tests))
    import e2e_stdio  # noqa: E402  (build_sandbox)
    tmp = e2e_stdio.build_sandbox()
    sys.path.insert(0, str(server.parents[1] / "gamedata" / "tests"))
    import synthetic  # noqa: E402
    db = tmp / "gamedata" / "forever-frFR.sqlite"
    db.parent.mkdir(parents=True, exist_ok=True)
    synthetic.make_db(db)
    return tmp, {"FOREVER_DATA_DIR": str(tmp / "perso"), "FOREVER_GAMEDB": str(db)}


class Client:
    def __init__(self, server: Path, env: dict):
        full = dict(os.environ)
        full.update(env)
        self.p = subprocess.Popen([sys.executable, str(server)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=full, text=True, encoding="utf-8")
        self.n = 0

    def rpc(self, method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            self.n += 1
            msg["id"] = self.n
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()
        return None if notify else json.loads(self.p.stdout.readline())

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default=str(DEFAULT_SERVER))
    ap.add_argument("--sequences", default=str(HERE / "sequences-v0.5.json"))
    ap.add_argument("--data-dir", help="dossier perso/ réel (sinon bac à sable des fixtures)")
    ap.add_argument("--gamedb", help="base locale du jeu (.sqlite)")
    ap.add_argument("--plugin-dir", help="dossier du plugin pour le coût fixe (agent, skills, knowledge)")
    ap.add_argument("--json", help="écrit aussi les mesures brutes dans ce fichier")
    ap.add_argument("--textes", action="store_true",
                    help="garde le texte des réponses dans --json (attention : données du perso)")
    ap.add_argument("--repeat", type=int, default=3, help="répétitions pour la durée (médiane)")
    a = ap.parse_args()

    server = Path(a.server).resolve()
    seqs = json.loads(Path(a.sequences).read_text(encoding="utf-8"))
    tmp = None
    if a.data_dir:
        env = {"FOREVER_DATA_DIR": str(Path(a.data_dir).expanduser())}
        if a.gamedb:
            env["FOREVER_GAMEDB"] = str(Path(a.gamedb).expanduser())
    else:
        tmp, env = sandbox(server)

    c = Client(server, env)
    t0 = time.perf_counter()
    init = c.rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                "clientInfo": {"name": "mesure", "version": "1"}})
    c.rpc("notifications/initialized", notify=True)
    tools = c.rpc("tools/list")["result"]["tools"]
    start_ms = (time.perf_counter() - t0) * 1000
    instr = init["result"].get("instructions", "")
    tools_chars = len(json.dumps(tools, ensure_ascii=False))

    # Coût fixe côté plugin (descriptions toujours présentes + corps chargés à la demande).
    plugin = Path(a.plugin_dir) if a.plugin_dir else server.parents[1]
    fixed = {"instructions serveur": len(instr), f"schémas des {len(tools)} outils": tools_chars}
    agent = plugin / "agents" / "forever-guide.md"
    if agent.exists():
        fixed["agent forever-guide (corps)"] = len(agent.read_text(encoding="utf-8"))
    skill_desc = skill_body = 0
    for s in sorted((plugin / "skills").glob("*/SKILL.md")):
        txt = s.read_text(encoding="utf-8")
        head = txt.split("---", 2)[1] if txt.startswith("---") else ""
        skill_desc += len(head)
        skill_body += len(txt)
    fixed["descriptions des skills (toujours chargées)"] = skill_desc
    fixed["corps des skills (si tous chargés)"] = skill_body
    for k in ("format-reponse.md", "formules.md", "forever-essentiels.md", "sources.md"):
        f = plugin / "knowledge" / k
        if f.exists():
            fixed[f"knowledge/{k}"] = len(f.read_text(encoding="utf-8"))

    rows, raw = [], []
    for q in seqs["questions"]:
        seen_lines, dup, total, durations, per = set(), 0, 0, [], []
        errors = 0
        for step in q["appels"]:
            args = step.get("args_bac_a_sable", step["args"]) if tmp else step["args"]
            times, text, is_err = [], "", False
            for _ in range(max(1, a.repeat)):
                t = time.perf_counter()
                res = c.rpc("tools/call", {"name": step["outil"], "arguments": args})
                times.append((time.perf_counter() - t) * 1000)
                r = res.get("result") or {}
                text = (r.get("content") or [{"text": json.dumps(res.get("error"))}])[0]["text"]
                is_err = bool(r.get("isError")) or "error" in res
            times.sort()
            ms = times[len(times) // 2]
            errors += is_err
            for line in text.splitlines():
                key = line.strip()
                if len(key) < 12:
                    continue
                if key in seen_lines:
                    dup += len(line)
                seen_lines.add(key)
            total += len(text)
            durations.append(ms)
            per.append({"outil": step["outil"], "car": len(text), "ms": round(ms, 1), "erreur": is_err,
                        **({"texte": text} if a.textes else {})})
        rows.append((q["id"], len(q["appels"]), q.get("web_probable", 0), total, dup, sum(durations), errors))
        raw.append({"id": q["id"], "question": q["question"], "appels": per, "car": total, "redondant": dup,
                    "ms": round(sum(durations), 1), "web_probable": q.get("web_probable", 0)})
    c.close()
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)

    mode = "données réelles" if a.data_dir else "bac à sable (fixtures)"
    print(f"## Mesure — séquences {seqs.get('version', '?')} — {mode}\n")
    print("### Coût fixe\n")
    print("| Élément | Caractères | ≈ tokens |\n|---|---:|---:|")
    for k, v in fixed.items():
        print(f"| {k} | {v:,} | {tok(v):,} |".replace(",", " "))
    print(f"\nDémarrage du serveur + tools/list : {start_ms:.0f} ms\n")
    print("### Par question\n")
    print("| Question | Appels MCP | Web probable | Sortie (car.) | ≈ tokens | Redondant | Durée outils | Erreurs |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for qid, n, web, total, dup, ms, err in rows:
        pct = f"{100 * dup / total:.0f} %" if total else "–"
        print(f"| {qid} | {n} | {web} | {total:,} | {tok(total):,} | {pct} | {ms:.0f} ms | {err} |".replace(",", " "))
    tot_calls = sum(r[1] for r in rows)
    tot_chars = sum(r[3] for r in rows)
    print(f"\nMoyenne : {tot_calls / len(rows):.1f} appels, ≈ {tok(tot_chars) // len(rows):,} tokens de sortie "
          f"par question.".replace(",", " "))
    if a.json:
        Path(a.json).write_text(json.dumps({"fixe": fixed, "questions": raw, "demarrage_ms": round(start_ms)},
                                           ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
