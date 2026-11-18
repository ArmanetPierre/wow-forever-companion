# Audit de portabilité (macOS, Windows, Linux + Wine/Lutris)

Audit en lecture seule du 18 novembre 2026 : `plugins/forever-companion/mcp/`,
`plugins/forever-companion/gamedata/`, `tools/gamedata/`, `addon/install.sh`,
`addon/install.ps1` et `plugins/forever-companion/.mcp.json`. Aucun fichier n'a été modifié ;
les correctifs ci-dessous sont des propositions. Les numéros de ligne correspondent à l'état
du dépôt au moment de l'audit (un autre chantier modifie `mcp/` et `gamedata/` en parallèle).

> **Mise à jour du 18 novembre 2026 (plugin 0.9.0) :** les correctifs ont été appliqués. Le
> tableau « État des correctifs » ci-dessous donne le statut de chaque point ; le détail des
> problèmes plus bas reste celui de l'audit initial (numéros de ligne d'origine).

## État des correctifs

| # | Statut | Ce qui a été fait | Reste à vérifier sur une vraie machine |
|---|---|---|---|
| 1 | corrigé | `.mcp.json` lance `${FOREVER_PYTHON:-python3}` (expansion vérifiée avec `claude mcp list` : défaut et variable surchargée) ; section Windows et Linux des deux README : `setx FOREVER_PYTHON py` | Windows : installeur python.org sans `python3` dans le PATH |
| 2 | corrigé | `.gitattributes` : `eol=lf` partout, CRLF pour `*.ps1`/`*.bat`, binaires marqués | premier clone Windows avec `core.autocrlf=true` |
| 3 | corrigé | plus de `✓` ; toutes les CLI (`build.py`, `clientcache.py`, `questie.py`, `sync.py`, `luasv.py`, outils d'évaluation) forcent UTF-8 sur stdout/stderr (`reconfigure`, `errors="replace"`) | — |
| 4 | corrigé | `Path(...).resolve().as_uri() + "?mode=ro"` dans `gamedb.py`, `build.py`, `questie.py` ; test avec un dossier `Jeux #1 100%` | — |
| 5 | corrigé | module unique `mcp/wowpaths.py` partagé par `sync.py`, `build.py` et `install.sh` : registre (4 clés), `Battle.net.config`, lecteurs C–J, `/Applications`, `/Volumes/*`, préfixes Wine, Lutris (y compris `prefix:` des fiches de jeu et Flatpak), Proton, Bottles ; `install.ps1` suit le même ordre ; 10 tests sur arborescences simulées | clés de registre et `Battle.net.config` réels ; préfixes Lutris/Proton réels |
| 6 | corrigé | `casc.encode_path` : `mbcs` sous Windows, `os.fsencode` ailleurs ; CascLib compilé avec `-DCASC_UNICODE=OFF` ; erreur claire (OS, architecture, 32/64 bits) si la DLL ne se charge pas | chemin avec accents sous Windows |
| 7 | corrigé en partie | compilation automatique sous Windows quand `git` et `cmake` sont présents, sinon instructions affichées | build MSVC réel |
| 8 | corrigé | harnais e2e en UTF-8 ; la CI n'utilise plus `PYTHONIOENCODING` et ajoute la variante `--client enUS --lang fr` | premier passage de la CI Windows |
| 9 | corrigé | `install.ps1` en UTF-8 avec BOM | syntaxe sous PowerShell 5.1 (pas de `pwsh` ici) |
| 10 | corrigé | écritures atomiques en `\n` (`open(..., newline="\n")`) dans `sync.py`, `knowledge.py`, `wowhead.py` ; `os.replace` réessayé 5 fois sur `PermissionError` (antivirus, éditeur ouvert) ; testé | — |
| 11 | corrigé | stdout du serveur reconfiguré en UTF-8 avec `newline="\n"` | — |
| 12 | corrigé | voir 3 | — |
| 13 | corrigé | `REVISION` lu et écrit en UTF-8 | — |
| 14 | corrigé en partie | le dossier `perso/` créé par la synchro est en `0700` sous macOS et Linux (un dossier existant n'est pas modifié) ; la casse des noms reste celle du jeu | — |
| + | corrigé | `gear` : les objets vendus uniquement par des marchands de l'autre faction (QuestieDB `friendly`) ne sont plus proposés ; testé | — |

Gravité : **haute** (cas courant cassé sur un OS cible), **moyenne** (cas plausible cassé ou
fonction dégradée), **basse** (cosmétique, cas rare, dette).

## Synthèse

| # | Gravité | Sujet | Fichier |
|---|---|---|---|
| 1 | haute | `python3` dans `.mcp.json` introuvable sous Windows | `.mcp.json:4` |
| 2 | haute | pas de `.gitattributes` : checkout CRLF sous Windows casse `install.sh` | racine du dépôt |
| 3 | moyenne | `✓` dans un `log()` : `build.py` plante en fin de construction sous Windows (sortie redirigée) | `gamedata/build.py:518` |
| 4 | moyenne | URI SQLite construite à la main : chemin avec `#`, `?` ou `%` ouvre une autre base | `mcp/gamedb.py:138`, `gamedata/build.py:282`, `gamedata/questie.py:383` |
| 5 | moyenne | recherche du jeu sous Windows sans registre ni Battle.net ; trois listes de candidats divergentes | `mcp/sync.py:73-102`, `gamedata/build.py:131-141`, `install.sh:30-37`, `install.ps1:21-28` |
| 6 | moyenne | chemin passé à CascLib encodé en UTF-8 alors que la DLL Windows attend l'ANSI | `gamedata/casc.py:43` |
| 7 | moyenne | CascLib : compilation native par OS, manuelle sous Windows | `gamedata/build.py:189-239` |
| 8 | basse | harnais e2e : `✔`/`✘` plantent sous cp1252 (bloque la CI Windows) | `mcp/tests/e2e_stdio.py:268` |
| 9 | basse | `install.ps1` en UTF-8 sans BOM : accents illisibles sous Windows PowerShell 5.1 | `addon/install.ps1` |
| 10 | basse | écritures texte : CRLF sous Windows et `os.replace` qui échoue sur fichier verrouillé | `mcp/sync.py:120-131`, `mcp/knowledge.py:134` |
| 11 | basse | stdout du serveur MCP en mode texte : `\r\n` sous Windows | `mcp/server.py:989` |
| 12 | basse | sorties CLI `ensure_ascii=False` vers une console cp1252 | `mcp/sync.py:892`, `mcp/luasv.py:339` |
| 13 | basse | `write_text`/`read_text` sans `encoding` (contenu ASCII aujourd'hui) | `gamedata/build.py:255`, `gamedata/build.py:276` |
| 14 | basse | casse des noms et permissions sous Linux | `mcp/sync.py:68,176`, `gamedata/build.py:139` |

Ce qui est déjà correct : tous les autres `read_text`/`write_text` passent `encoding="utf-8"` ;
les SavedVariables sont lues en octets puis décodées en UTF-8 avec BOM et CRLF tolérés
(`luasv.py:328-331`) ; tous les chemins passent par `pathlib` (aucun séparateur codé en dur
hors chaînes d'exemple) ; `safe_name` (`sync.py:104-106`) retire les caractères interdits par
Windows ; le serveur lit stdin en octets et force UTF-8 sur stdout ; `install.ps1` utilise une
jonction (pas de droits administrateur ni du mode développeur, contrairement à un lien
symbolique) avec repli en copie ; `install.sh` crée un lien symbolique que Wine suit sans
problème.

## Tests locaux en simulant Windows

Machine de l'audit : macOS, Python 3.11, Lua 5.5 (pas de Lua 5.1 ni de Python 3.9 disponibles).

| Commande | Résultat |
|---|---|
| `mcp` : `python3 -m unittest discover -s tests` | 90/91 OK, 1 échec `test_i18n.test_every_literal_has_english` (textes de `intent_tools.py` sans traduction : chantier en cours de l'autre agent, sans lien avec la portabilité) |
| idem avec `PYTHONIOENCODING=cp1252 PYTHONUTF8=0` | même résultat |
| `gamedata` : `python3 -m unittest discover -s tests` (lancé depuis `gamedata/`, le dossier `tests/` n'est pas un paquet) | 21/21 OK, idem en cp1252 |
| `e2e_stdio.py` (défaut, `--lang en`, `--client enUS`) | OK |
| idem avec `PYTHONIOENCODING=cp1252 PYTHONUTF8=0` | **échec** des trois variantes : `UnicodeEncodeError: '\u2714'` dans le harnais (problème 8) ; le serveur répond correctement |
| copie du dépôt convertie en CRLF (simule `core.autocrlf=true`) : tests Python, e2e, `run_capture.lua` | OK |
| idem : `bash addon/install.sh --help` | **échec** : `set: pipefail: invalid option name` (problème 2) |
| URI `file:{chemin}?mode=ro` sur un dossier `dir #1 50%` | **échec** : la base n'est pas trouvée et un fichier parasite `dir ` est créé (problème 4) ; `Path.as_uri()` fonctionne |
| `ast.parse(..., feature_version=(3, 9))` sur tout le Python | OK (pas de syntaxe postérieure à 3.9) |

Limite : sur macOS, `open()` sans `encoding` reste en UTF-8 même avec `PYTHONUTF8=0` ; seule la
CI Windows (`.github/workflows/tests.yml`, sans `PYTHONUTF8`) exerce vraiment cp1252. La revue
du code n'a trouvé que les deux appels du problème 13.

## Détail des problèmes

### 1. `python3` dans `.mcp.json` sous Windows — haute

`plugins/forever-companion/.mcp.json:4` : `"command": "python3"`. Avec l'installateur de
python.org, Windows fournit `python.exe` et le lanceur `py.exe`, pas `python3.exe`. Le seul
`python3` présent est souvent l'alias d'exécution du Microsoft Store
(`%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe`), qui ouvre le Store ou sort sans rien
faire : le serveur `forever` ne démarre pas, sans message clair.

Correctif proposé : un interpréteur surchargeable par variable d'environnement, avec
`python3` par défaut (Claude Code développe `${VAR:-défaut}` dans `command` et `args` des
fichiers `.mcp.json` ; à vérifier sur un `.mcp.json` de plugin avant publication).

```diff
-      "command": "python3",
+      "command": "${FOREVER_PYTHON:-python3}",
```

Documentation Windows (README, section installation) :

```powershell
setx FOREVER_PYTHON py     # ou : setx FOREVER_PYTHON python
# puis rouvrir le terminal et Claude Code
```

Alternatives écartées : `"command": "python"` casse macOS (pas de `python` par défaut) ; un
script lanceur `.cmd`/`.sh` exigerait de choisir l'extension selon l'OS, ce que `.mcp.json` ne
sait pas faire.

### 2. Fins de ligne : pas de `.gitattributes` — haute

Git pour Windows est installé avec `core.autocrlf=true` par défaut : le checkout convertit tout
en CRLF. Conséquences mesurées : `install.sh` ne s'exécute plus sous Git Bash, WSL ou un Linux
qui partage le checkout (`set: pipefail: invalid option name`, ligne 13). Les tests Python et
Lua passent en CRLF. Inversement, `install.ps1` doit rester lisible par PowerShell, qui accepte
LF comme CRLF.

Correctif proposé : créer `.gitattributes` à la racine.

```diff
+# Texte normalisé en LF dans le dépôt et dans les copies de travail
+* text=auto eol=lf
+*.ps1 text eol=crlf
+*.sh text eol=lf
+*.lua text eol=lf
+*.toc text eol=lf
+# Binaires
+*.png binary
+*.tga binary
+*.blp binary
+*.sqlite binary
```

Puis `git add --renormalize .` dans un commit séparé.

### 3. `✓` dans la sortie de `build.py` — moyenne

`gamedata/build.py:518` : `log(f"✓ Base écrite en …")`. Sous Windows, quand la sortie est
redirigée (cas de Claude Code qui lance `tools/gamedata/build_db.py` par son outil Bash, ou
`> journal.txt`), `sys.stdout` est en cp1252 et `✓` (U+2713) n'y existe pas :
`UnicodeEncodeError` juste après l'écriture de la base, donc l'étape QuestieDB
(`_questie_step`) n'est jamais lancée. Les autres caractères des messages (`•`, `…`, `«`, `»`,
`·`, accents) existent en cp1252. C'est le seul `print`/`log` concerné dans `mcp/` et
`gamedata/`.

Correctif proposé (deux volets ; le second protège les futurs messages) :

```diff
-    log(f"✓ Base écrite en {time.time() - t0:.0f} s ({size:.1f} Mo)")
+    log(f"• Base écrite en {time.time() - t0:.0f} s ({size:.1f} Mo)")
```

```diff
 def main(argv=None):
+    for stream in (sys.stdout, sys.stderr):
+        try:
+            stream.reconfigure(errors="replace")
+        except AttributeError:
+            pass
```

### 4. URI SQLite construite à la main — moyenne

`mcp/gamedb.py:138`, `gamedata/build.py:282`, `gamedata/questie.py:383` :
`sqlite3.connect(f"file:{path}?mode=ro", uri=True)`. Dans une URI, `#` commence un fragment,
`?` une requête et `%` un échappement. Un dossier utilisateur comme `C:\Users\Jean#2\` ou
`~/Jeux 100%/` fait ouvrir un autre fichier, **sans** `mode=ro` : SQLite crée alors une base
vide parasite (vérifié : fichier `dir ` créé à côté de `dir #1 50%`). Le serveur répond
ensuite « base absente » ou des tables manquantes.

Correctif proposé (même chose aux trois endroits) :

```diff
-        self.con = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True, check_same_thread=False)
+        self.con = sqlite3.connect(Path(self.path).resolve().as_uri() + "?mode=ro", uri=True,
+                                   check_same_thread=False)
```

`Path.as_uri()` produit `file:///C:/Users/...` sous Windows et échappe les caractères spéciaux.

### 5. Recherche du dossier du jeu — moyenne

Trois listes différentes cherchent le jeu :

- `mcp/sync.py:73-102` (`detect_wow_paths`) : la plus complète. macOS
  `/Applications` et `~/Applications` ; Windows lecteurs C à G × `Program Files (x86)`,
  `Program Files`, `Games`, racine ; Linux : `~/Games/*` (préfixe par défaut de Lutris),
  `~/.wine`, `~/.local/share/wineprefixes/*`, `~/.local/share/lutris/prefixes/*`, Proton (deux
  emplacements Steam), Bottles en Flatpak.
- `gamedata/build.py:131-141` (`detect_wow`, aussi utilisé par `clientcache.py:129`) : six
  chemins seulement, lecteur C uniquement sous Windows, un seul préfixe Lutris
  (`~/Games/world-of-warcraft`), aucun préfixe Bottles, Proton ni `wineprefixes`.
- `addon/install.sh:30-37` et `addon/install.ps1:21-28` : listes encore différentes (C et D
  seulement sous Windows).

Manques communs :

- **Windows, registre** : contrairement à ce qu'on lit souvent, `winreg` **fait partie de la
  bibliothèque standard** (disponible seulement sous Windows). Le Battle.net écrit
  `HKLM\SOFTWARE\WOW6432Node\Blizzard Entertainment\World of Warcraft\InstallPath` et
  `HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\World of Warcraft\InstallLocation`
  (valeurs à confirmer sur une installation de WoW Forever, le produit `wowf` partageant le
  dossier `World of Warcraft`).
- **Windows, Battle.net** : `%APPDATA%\Battle.net\Battle.net.config` (JSON) contient
  `Client.Install.DefaultInstallPath`, le dossier proposé pour les nouvelles installations.
- **Linux, Lutris** : un préfixe choisi à la main n'est connu que du fichier du jeu dans
  `~/.config/lutris/games/*.yml` ou `~/.local/share/lutris/games/*.yml` (clé `prefix:`), ainsi
  que Lutris en Flatpak (`~/.var/app/net.lutris.Lutris/`).
- **macOS** : un jeu installé sur un disque externe (`/Volumes/*/World of Warcraft`).

Correctif proposé : une seule fonction (celle de `sync.py`) enrichie, réutilisée par
`build.py` et `clientcache.py`, et des scripts d'installation qui affichent au moins le
chemin à passer.

```diff
 def detect_wow_paths() -> List[Path]:
     home = Path.home()
     cands: List[Path] = [
         Path("/Applications/World of Warcraft"),
         home / "Applications" / "World of Warcraft",
     ]
+    cands.extend(Path("/Volumes").glob("*/World of Warcraft"))
     if os.name == "nt":
+        cands.extend(_windows_registry_paths())
+        cfg = Path(os.environ.get("APPDATA", "")) / "Battle.net" / "Battle.net.config"
+        try:
+            d = json.loads(cfg.read_text(encoding="utf-8"))
+            base = d.get("Client", {}).get("Install", {}).get("DefaultInstallPath")
+            if base:
+                cands.append(Path(base) / "World of Warcraft")
+        except (OSError, ValueError, AttributeError):
+            pass
         for drive in "CDEFG":
@@
+        ".var/app/net.lutris.Lutris/data/lutris/prefixes/*/drive_c/Program Files*/World of Warcraft",
     ]
     if os.name != "nt":
         for pattern in globs:
             cands.extend(home.glob(pattern))
+        for yml in [*home.glob(".config/lutris/games/*.yml"), *home.glob(".local/share/lutris/games/*.yml")]:
+            m = re.search(r"^\s*prefix:\s*(.+)$", yml.read_text(encoding="utf-8", errors="replace"), re.M)
+            if m:
+                cands.extend(Path(m.group(1).strip().strip("'\"")).expanduser()
+                             .glob("drive_c/Program Files*/World of Warcraft"))
```

```python
def _windows_registry_paths() -> List[Path]:
    try:
        import winreg
    except ImportError:
        return []
    keys = [r"SOFTWARE\WOW6432Node\Blizzard Entertainment\World of Warcraft",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\World of Warcraft"]
    out = []
    for key in keys:
        for value in ("InstallPath", "InstallLocation"):
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as k:
                    out.append(Path(winreg.QueryValueEx(k, value)[0]))
            except OSError:
                pass
    return out
```

```diff
 # gamedata/build.py
 def detect_wow():
-    home = Path.home()
-    cands = [Path("/Applications/World of Warcraft"), ...]
-    for c in cands:
+    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp"))
+    from sync import detect_wow_paths
+    for f in detect_wow_paths():           # renvoie le dossier _forever_
+        c = f.parent if f.name == "_forever_" else f
         if (c / ".build.info").is_file() and (c / "Data").is_dir():
             return c
     return None
```

`install.ps1` : lire la même clé de registre avant la liste fixe.

```diff
 if (-not $WowPath) {
+  foreach ($k in "HKLM:\SOFTWARE\WOW6432Node\Blizzard Entertainment\World of Warcraft") {
+    $p = (Get-ItemProperty -Path $k -ErrorAction SilentlyContinue).InstallPath
+    if ($p -and (Test-Path (Join-Path $p "_forever_"))) { $WowPath = Join-Path $p "_forever_"; break }
+  }
+}
+if (-not $WowPath) {
   $candidates = @(
```

`install.sh` : ajouter les motifs de `sync.py` (Lutris `prefixes/*`, `wineprefixes/*`, Proton,
Bottles) ; une boucle `for c in "$HOME"/.local/share/lutris/prefixes/*/drive_c/Program\ Files*/World\ of\ Warcraft/_forever_`
suffit.

### 6. Chemin passé à CascLib sous Windows — moyenne

`gamedata/casc.py:43` : `params = f"{wow_root}*{product}".encode()` encode en UTF-8.
`CascOpenStorage` prend un `LPCTSTR`. Compilée sans `UNICODE` (option CMake `CASC_UNICODE`,
désactivée par défaut, à vérifier sur la version clonée), la DLL interprète les octets dans la
page de code ANSI (cp1252) : un chemin avec accents (`C:\Jeux\Éditions\World of Warcraft`, ou
un dossier utilisateur accentué) échoue. Compilée avec `UNICODE`, elle attend du `wchar_t*` et
tout chemin échoue. Sous macOS et Linux, UTF-8 est correct.

Correctif proposé : encoder selon l'OS et fixer l'option à la compilation.

```diff
-        params = f"{wow_root}*{product}".encode()
+        text = f"{wow_root}*{product}"
+        params = text.encode("mbcs") if os.name == "nt" else os.fsencode(text)
```

et dans le message de compilation Windows (`build.py:205-211`), ajouter
`-DCASC_UNICODE=OFF` à la commande `cmake -S …`. Pour accepter tous les chemins Unicode, la
variante robuste est `-DCASC_UNICODE=ON` plus `argtypes = [ctypes.c_wchar_p, …]` sous Windows.

### 7. CascLib : bibliothèque native par OS — moyenne

`gamedata/build.py:189-239` : la construction de la base exige une CascLib compilée pour
l'OS : `libcasc.dylib`/`casc.framework` (macOS : Xcode CLT + CMake), `libcasc.so` (Linux :
git, cmake, build-essential), `casc.dll` (Windows : construction **manuelle** avec CMake et
Visual Studio Build Tools, l. 205-211). C'est la seule dépendance non stdlib du projet, et le
seul point où l'architecture compte (arm64 contre x86_64 sur macOS ; Python 64 bits contre DLL
32 bits sous Windows). Sous Linux avec le jeu sous Wine, il faut bien la `.so` native : le
Python qui la charge est natif, seul le jeu tourne sous Wine.

Correctifs proposés, du plus simple au plus complet :

1. Vérifier l'architecture avant `ctypes.CDLL` et donner un message clair :

```diff
 def load_lib(path):
-    lib = ctypes.CDLL(str(path))
+    try:
+        lib = ctypes.CDLL(str(path))
+    except OSError as exc:
+        raise SystemExit(f"CascLib ({path}) ne se charge pas : {exc}. Bibliothèque compilée pour un "
+                         f"autre OS ou une autre architecture ({platform.machine()}, Python "
+                         f"{struct.calcsize('P') * 8} bits) ? Supprime le dossier casclib et relance.") from exc
     return lib
```

2. Sous Windows, automatiser comme sous Unix quand `cmake` et un compilateur sont présents
   (`shutil.which("cmake")`) au lieu de lever `SystemExit` d'office.
3. À terme : publier les binaires CascLib (trois OS × deux architectures) en artefacts d'une
   release, téléchargés avec une somme SHA-256 vérifiée, sans compilation chez le joueur.

### 8. Harnais e2e et cp1252 — basse (mais bloque la CI Windows)

`plugins/forever-companion/mcp/tests/e2e_stdio.py:268` (et 256) : `print(f"{'✔' if ok else '✘'} …")`.
Sur un runner Windows, stdout est un tube en cp1252 : `UnicodeEncodeError` à la première
ligne, alors que le serveur testé fonctionne. Le workflow contourne avec
`PYTHONIOENCODING=utf-8` sur ces étapes, à retirer une fois le correctif appliqué.

```diff
 def main():
+    try:
+        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
+    except AttributeError:
+        pass
```

### 9. `install.ps1` sans BOM — basse

Le fichier est en UTF-8 sans BOM. Windows PowerShell 5.1 (celui livré avec Windows) lit alors
le script en ANSI : « créée » s'affiche « crÃ©Ã©e ». Les accents présents (é, à, è) ne
produisent pas de guillemets parasites, donc le script reste exécutable ; PowerShell 7 n'est
pas concerné.

Correctif proposé : enregistrer `install.ps1` en UTF-8 **avec** BOM (octets `EF BB BF` en
tête), ou n'utiliser que de l'ASCII dans les messages. Jonction : rien à changer
(`New-Item -ItemType Junction` ne demande ni droits administrateur ni mode développeur ;
le repli en copie couvre un dépôt sur un partage réseau ou `\\wsl$`).

### 10. Écritures de fichiers texte — basse

`mcp/sync.py:120-131` (`write_json`, `write_text`) et `mcp/knowledge.py:134` :
`Path.write_text(..., encoding="utf-8")` traduit `\n` en `\r\n` sous Windows (Python 3.9 n'a pas
le paramètre `newline` de `write_text`, ajouté en 3.10). Sans conséquence fonctionnelle (les
relectures passent en mode texte), mais un dossier `perso/` synchronisé entre deux OS
(OneDrive, Dropbox, Git) mélange les fins de ligne. Par ailleurs `os.replace` lève
`PermissionError` sous Windows si `profil.md` est ouvert dans un éditeur qui le verrouille ou
analysé par l'antivirus.

```diff
 def write_text(path: Path, text: str) -> None:
     path.parent.mkdir(parents=True, exist_ok=True)
     tmp = path.with_suffix(path.suffix + ".tmp")
-    tmp.write_text(text, encoding="utf-8")
-    os.replace(tmp, path)
+    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
+        f.write(text)
+    for attempt in range(5):
+        try:
+            os.replace(tmp, path)
+            return
+        except PermissionError:
+            if attempt == 4:
+                raise
+            time.sleep(0.1 * (attempt + 1))
```

Même chose pour `write_json` et `knowledge.py:134`.

### 11. stdout du serveur MCP — basse

`mcp/server.py:987-991` force `encoding="utf-8"`, ce qui règle cp1252. Reste que stdout est en
mode texte : sous Windows chaque réponse se termine par `\r\n`. Le transport MCP stdio
découpe sur `\n` et `JSON.parse` ignore le `\r`, donc rien ne casse aujourd'hui, mais autant
émettre exactement ce que la spécification décrit.

```diff
-        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
+        sys.stdout.reconfigure(encoding="utf-8", newline="\n")  # type: ignore[attr-defined]
```

`sys.stderr` n'a pas besoin de correctif : son gestionnaire d'erreurs par défaut est
`backslashreplace`, un journal ne peut donc pas planter.

### 12. Sorties des outils en ligne de commande — basse

`mcp/sync.py:892` et `mcp/luasv.py:339` : `print(json.dumps(..., ensure_ascii=False))`. Un nom
de perso ou de royaume hors cp1252 fait planter `python sync.py > rapport.json` sous Windows.
Même correctif qu'au problème 8 (reconfigurer stdout en UTF-8 dans le `main`), ou
`ensure_ascii=True` pour ces sorties destinées à des outils.

### 13. `read_text`/`write_text` sans encodage — basse

`gamedata/build.py:255` (`REVISION` en écriture) et `gamedata/build.py:276` (lecture) : sans
`encoding`, donc cp1252 sous Windows. Le contenu est ASCII (`master 2026-11-18`), aucun bogue
aujourd'hui ; c'est le seul écart à la règle « UTF-8 explicite » dans le code audité.

```diff
-        (defs / "REVISION").write_text("master " + time.strftime("%Y-%m-%d") + "\n")
+        (defs / "REVISION").write_text("master " + time.strftime("%Y-%m-%d") + "\n", encoding="utf-8")
@@
-        parts.append("defs=" + rev.read_text().strip())
+        parts.append("defs=" + rev.read_text(encoding="utf-8").strip())
```

### 14. Casse et permissions sous Linux — basse

- **Casse** : le code cherche `WTF/Account` (`sync.py:68,176`), `Data` et `.build.info`
  (`build.py:139`), `Cache/WDB/<locale>` et `Cache/ADB/<locale>` (`build.py:477-478`,
  `sync.py:734`), `SavedVariables/ForeverScribe.lua`. Le client crée ces noms avec cette casse,
  y compris sous Wine, donc rien ne casse sur une installation normale. Risque résiduel : un
  dossier copié depuis une sauvegarde Windows ou créé à la main avec une autre casse (`Wtf`,
  `interface/addons`) est invisible sous Linux alors qu'il marche sous Windows et macOS (systèmes
  de fichiers insensibles à la casse). Correctif possible si des retours le montrent : une
  fonction `child_ci(parent, name)` qui retombe sur une comparaison `name.lower()` quand le
  nom exact n'existe pas. `install.sh` installe le dossier avec le nom exact du `.toc`, ce qui
  est indispensable sous Linux.
- **Permissions** : `perso/` et `connaissances/` sont créés avec l'umask courant (souvent
  `0755`/`0644`), lisibles par les autres comptes de la machine alors qu'ils contiennent le
  numéro de compte WoW et les noms de persos. Correctif proposé dans `resolve_data_dir` ou au
  premier `mkdir` :

```diff
+    if os.name != "nt":
+        data_dir.mkdir(parents=True, exist_ok=True)
+        data_dir.chmod(0o700)
```

  Le préfixe Wine appartient à l'utilisateur : `install.sh` n'a pas besoin de `sudo`.
  `install.sh` est bien exécutable (`-rwxr-xr-x`) ; un checkout Windows perd ce bit, d'où
  la recommandation `bash addon/install.sh` dans la documentation.

## Intégration continue

`.github/workflows/tests.yml` lance, sur `ubuntu-latest`, `windows-latest` et `macos-latest`
avec Python 3.9 et 3.12 : les tests unitaires de `mcp/` et de `gamedata/`, puis
`e2e_stdio.py` (défaut, `--lang en`, `--client enUS`). Les tests de l'addon tournent avec
Lua 5.1 sur Ubuntu seulement ; une étape non bloquante signale si `run_capture.lua` a modifié
les fixtures du dépôt. `PYTHONUTF8` n'est pas activé, pour que le runner Windows exerce
réellement cp1252 ; `FOREVER_WEB_LOOKUP=0` garantit qu'aucun test n'utilise le réseau.
`claude plugin validate .` n'y figure pas (il demanderait d'installer Claude Code dans la CI).
