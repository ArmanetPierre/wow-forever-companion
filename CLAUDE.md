# WoW Forever Companion — développement

Ce dépôt contient l'**outil** : l'addon ForeverScribe, le plugin Claude Code
`forever-companion` (agent, skills, connaissances, serveur MCP) et leur documentation.
Il ne contient **aucune donnée de joueur**. Les données d'un joueur vivent dans son propre
dossier (par défaut `~/WowForever/perso`), jamais ici.

## Structure

| Chemin | Rôle |
|---|---|
| `.claude-plugin/marketplace.json` | le dépôt est une marketplace Claude Code |
| `plugins/forever-companion/agents/` | agent `forever-guide` |
| `plugins/forever-companion/skills/` | 8 skills `forever-*` |
| `plugins/forever-companion/knowledge/` | faits Forever, sources, charte de réponse, formules |
| `plugins/forever-companion/mcp/` | serveur MCP Python (stdlib) : `luasv.py`, `sync.py`, `formats.py`, `server.py` |
| `plugins/forever-companion/.mcp.json` | déclaration du serveur `forever` |
| `addon/ForeverScribe/` | addon de capture (Lua, interface 16001) |
| `addon/ForeverProbe/` | sonde de diagnostic de l'API (pour contributeurs) |
| `addon/install.sh`, `addon/install.ps1` | installation de l'addon |
| `addon/tests/` | tests hors jeu de l'addon + fixtures partagées avec le serveur |
| `docs/schema.md` | contrat de données addon → serveur (à tenir à jour) |
| `docs/api-inventaire.md` | API Forever vérifiée en jeu |
| `docs/conception/` | plans et décisions de conception |
| `perso.example/` | modèles de fichiers d'un perso |

## Tests (à lancer avant chaque commit)

```bash
lua addon/tests/run_capture.lua                       # addon (luac/lua 5.1+)
cd plugins/forever-companion/mcp
python3 -m unittest discover -s tests                 # parseur + synchro
python3 tests/e2e_stdio.py                            # serveur MCP de bout en bout (fixtures)
cd - && claude plugin validate .                      # manifeste du plugin
```

## Règles

- **Ne jamais committer de données de joueur** : pas de `perso/`, pas de fichiers
  SavedVariables réels, pas de numéro de compte, GUID, nom de perso réel ni chemin
  personnel. Les exemples utilisent le perso fictif **Brannok** (Nain Chasseur 25),
  le compte `123456789#1` et le GUID `Player-1234-0A1B2C3D`.
- Toute modification du format de capture passe par `docs/schema.md` (version mineure
  rétrocompatible, sinon `schemaVersion` + migration côté `sync.py`).
- Serveur MCP : Python 3.9+, **bibliothèque standard uniquement**, chemins via `pathlib`,
  compatible macOS, Windows et Linux (Wine).
- Addon : chaque collecteur dans `pcall`, rien en combat, aucune automatisation de
  touches (`ReloadUI` exige un geste du joueur).
- Contenu destiné au joueur en français ; badges [Forever] / [Classic] / [Retail] et
  niveau de certitude ; ne jamais présenter une info Classic comme vérifiée dans Forever.
- Changement visible : mettre à jour `CHANGELOG.md` et la version (`plugin.json`,
  `ForeverScribe.toc` + `ns.VERSION` dans `Util.lua`).
