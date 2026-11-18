#!/usr/bin/env bash
# WoW Forever Companion : installateur macOS / Linux (installation et mise à jour).
#
#   Double-clic : « Installer WoW Forever Companion.command » (archive macOS)
#   En une ligne :
#     curl -fsSL https://raw.githubusercontent.com/ArmanetPierre/wow-forever-companion/main/install/install.sh | bash
#   Depuis le dépôt :
#     install/install.sh [options]
#
# Options :
#   --wow-path DOSSIER   dossier du jeu (« World of Warcraft » ou son « _forever_ »)
#   --data-dir DOSSIER   dossier du joueur (défaut : ~/WowForever)
#   --lang fr|en         langue des messages (défaut : celle du système)
#   --yes                répond oui aux questions sur NOS étapes (base du jeu) ;
#                        n'installe jamais un logiciel tiers sans un « oui » tapé
#   --no-db              ne propose pas de construire la base du jeu
#   --uninstall          retire l'addon et le plugin ; ne touche jamais à tes données
#   -h, --help           cette aide
#
# Variables utiles : FOREVER_PYTHON (Python à utiliser), WOW_FOREVER_PATH, FOREVER_HOME
# (dossier du joueur), FOREVER_SOURCE_URL (archive du dépôt à télécharger),
# FOREVER_MARKETPLACE (source de la marketplace Claude Code), FOREVER_NO_TTY=1 (aucune question).
#
# Le script entier est dans une fonction appelée à la dernière ligne : avec « curl | bash »,
# rien ne s'exécute tant que le fichier n'est pas arrivé en entier.

forever_install() {
  set -u
  local REPO="ArmanetPierre/wow-forever-companion"
  local MARKET_NAME="wow-forever-companion"
  local PLUGIN_ID="forever-companion@wow-forever-companion"
  local MARKET_SOURCE="${FOREVER_MARKETPLACE:-$REPO}"
  local SOURCE_URL="${FOREVER_SOURCE_URL:-https://github.com/$REPO/archive/refs/heads/main.tar.gz}"

  local WOW_ARG="${WOW_FOREVER_PATH:-}" DATA_DIR="${FOREVER_HOME:-$HOME/WowForever}"
  local LANG_OPT="" ASSUME_YES=0 NO_DB=0 UNINSTALL=0
  while [ $# -gt 0 ]; do
    case "$1" in
      --wow-path) WOW_ARG="${2:-}"; shift 2 ;;
      --data-dir) DATA_DIR="${2:-}"; shift 2 ;;
      --lang) LANG_OPT="${2:-}"; shift 2 ;;
      --yes|-y) ASSUME_YES=1; shift ;;
      --no-db) NO_DB=1; shift ;;
      --uninstall) UNINSTALL=1; shift ;;
      -h|--help) sed -n '2,/FOREVER_NO_TTY/p' "${BASH_SOURCE[0]:-/dev/null}" 2>/dev/null || true; return 0 ;;
      *) printf 'Option inconnue / unknown option: %s\n' "$1" >&2; return 64 ;;
    esac
  done

  # ---------- langue ----------
  local L="$LANG_OPT"
  if [ -z "$L" ]; then
    local sys="${LC_ALL:-${LC_MESSAGES:-${LANG:-}}}"
    if [ -z "$sys" ] && [ "$(uname -s)" = "Darwin" ]; then
      sys="$(defaults read -g AppleLocale 2>/dev/null || true)"
    fi
    case "$sys" in fr*|FR*) L="fr" ;; *) L="en" ;; esac
  fi
  t() { if [ "$L" = "fr" ]; then printf '%s' "$1"; else printf '%s' "$2"; fi; }

  # ---------- affichage ----------
  local B="" D="" G="" Y="" R="" C="" N=""
  if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    B=$'\033[1m'; D=$'\033[2m'; G=$'\033[32m'; Y=$'\033[33m'; R=$'\033[31m'; C=$'\033[36m'; N=$'\033[0m'
  fi
  local STEP=0 TOTAL=6
  step() { STEP=$((STEP + 1)); printf '\n%s[%d/%d] %s%s\n' "$B$C" "$STEP" "$TOTAL" "$1" "$N"; }
  ok()   { printf '  %s✔%s %s\n' "$G" "$N" "$1"; }
  info() { printf '  %s·%s %s\n' "$D" "$N" "$1"; }
  warn() { printf '  %s!%s %s\n' "$Y" "$N" "$1"; }
  fail() { printf '  %s✘%s %s\n' "$R" "$N" "$1"; }

  # Questions : lues sur le terminal même avec « curl | bash ». Sans terminal, réponse par défaut.
  local TTY=""
  if [ -z "${FOREVER_NO_TTY:-}" ] && [ -r /dev/tty ] && [ -w /dev/tty ] && { : < /dev/tty; } 2>/dev/null; then TTY="/dev/tty"; fi
  ask_yes() {  # $1 = question, $2 = défaut (y/n), $3 = 1 si --yes peut répondre à notre place
    local q="$1" def="$2" allow="${3:-0}" hint ans
    if [ "$allow" = "1" ] && [ "$ASSUME_YES" = "1" ]; then return 0; fi
    if [ "$def" = "y" ]; then hint="$(t '[O/n]' '[Y/n]')"; else hint="$(t '[o/N]' '[y/N]')"; fi
    if [ -z "$TTY" ]; then
      info "$q $hint → $(t 'pas de terminal, réponse par défaut' 'no terminal, default answer')"
      [ "$def" = "y" ]; return
    fi
    printf '  %s?%s %s %s ' "$C" "$N" "$q" "$hint" > /dev/tty
    IFS= read -r ans < /dev/tty || ans=""
    case "$ans" in
      "") [ "$def" = "y" ] ;;
      o|O|y|Y|oui|Oui|OUI|yes|Yes|YES) return 0 ;;
      *) return 1 ;;
    esac
  }
  ask_text() {  # $1 = question ; affiche la réponse (vide sans terminal)
    local ans=""
    if [ -n "$TTY" ]; then
      printf '  %s?%s %s ' "$C" "$N" "$1" > /dev/tty
      IFS= read -r ans < /dev/tty || ans=""
    fi
    printf '%s' "$ans"
  }
  open_url() {
    if command -v open >/dev/null 2>&1; then open "$1" >/dev/null 2>&1 || true
    elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1 || true; fi
  }
  pause_for() {  # attend que l'utilisateur ait fini une installation tierce
    if [ -n "$TTY" ]; then
      printf '  %s %s' "$(t "Appuie sur Entrée quand c'est fait…" 'Press Enter when done…')" "" > /dev/tty
      IFS= read -r _ < /dev/tty || true
    fi
  }

  printf '\n%s⚔  WoW Forever Companion%s %s\n' "$B" "$N" \
    "$(if [ "$UNINSTALL" = 1 ]; then t '— désinstallation' '— uninstall'; else t '— installation et mise à jour' '— install and update'; fi)"
  printf '%s%s%s\n' "$D" "$(t "Ce programme n'installe rien sans te le dire. Tes données de joueur ne sont jamais modifiées." "This installer tells you everything it does. Your player data is never modified.")" "$N"

  # ---------- sources : dossier local (dépôt, archive) ou téléchargement ----------
  local SRC="" TMP=""
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]:-.}")" 2>/dev/null && pwd || true)"
  if [ -n "$here" ] && [ -f "$here/../addon/ForeverScribe/ForeverScribe.toc" ]; then
    SRC="$(cd "$here/.." && pwd)"
  fi
  if [ -z "$SRC" ] && [ "$UNINSTALL" = 0 ]; then
    TMP="$(mktemp -d 2>/dev/null || mktemp -d -t forever)"
    trap 'rm -rf "$TMP"' EXIT
    info "$(t 'Téléchargement du compagnon…' 'Downloading the companion…')"
    if ! curl -fsSL "$SOURCE_URL" -o "$TMP/src.tar.gz" || ! tar -xzf "$TMP/src.tar.gz" -C "$TMP"; then
      fail "$(t "Téléchargement impossible : $SOURCE_URL" "Download failed: $SOURCE_URL")"
      return 1
    fi
    local toc
    toc="$(find "$TMP" -path '*/addon/ForeverScribe/ForeverScribe.toc' -print 2>/dev/null | head -n 1)"
    if [ -z "$toc" ]; then fail "$(t 'Archive inattendue (addon absent).' 'Unexpected archive (addon missing).')"; return 1; fi
    SRC="$(cd "$(dirname "$toc")/../.." && pwd)"
  fi

  # Dossier où l'installateur garde les outils (construction de la base, mises à jour).
  local APP
  if [ "$(uname -s)" = "Darwin" ]; then APP="$HOME/Library/Application Support/WoW Forever Companion"
  else APP="${XDG_DATA_HOME:-$HOME/.local/share}/wow-forever-companion"; fi

  # ---------- 1. prérequis ----------
  local PY="" CLAUDE="" HAVE_CLAUDE=0 RESULT_PLUGIN="" RESULT_ADDON="" RESULT_DB="" RESULT_DATA=""
  find_claude() {
    CLAUDE=""
    if command -v claude >/dev/null 2>&1; then CLAUDE="$(command -v claude)"; return 0; fi
    local c
    for c in "$HOME/.local/bin/claude" "$HOME/.claude/local/claude" "/usr/local/bin/claude" "/opt/homebrew/bin/claude"; do
      if [ -x "$c" ]; then CLAUDE="$c"; return 0; fi
    done
    return 1
  }
  py_ok() {  # $1 = commande python ; vrai si >= 3.9
    local v
    v="$("$1" -c 'import sys; print("%d %d" % sys.version_info[:2])' 2>/dev/null)" || return 1
    set -- $v
    [ "${1:-0}" -gt 3 ] || { [ "${1:-0}" -eq 3 ] && [ "${2:-0}" -ge 9 ]; }
  }
  find_python() {
    PY=""
    if [ -n "${FOREVER_PYTHON:-}" ]; then
      if py_ok "$FOREVER_PYTHON"; then PY="$FOREVER_PYTHON"; return 0; fi
      return 1
    fi
    local c
    for c in python3 python; do
      if command -v "$c" >/dev/null 2>&1 && py_ok "$c"; then PY="$c"; return 0; fi
    done
    return 1
  }

  if [ "$UNINSTALL" = 1 ]; then
    TOTAL=3
    step "$(t "Retrait de l'addon" 'Removing the addon')"
  else
    step "$(t 'Vérification des prérequis' 'Checking prerequisites')"
    while ! find_python; do
      if [ -n "${FOREVER_PYTHON:-}" ]; then
        fail "$(t "FOREVER_PYTHON=$FOREVER_PYTHON ne répond pas ou date d'avant 3.9." "FOREVER_PYTHON=$FOREVER_PYTHON does not run or is older than 3.9.")"
      else
        fail "$(t 'Python 3.9 ou plus récent est introuvable. Le compagnon en a besoin (aucune bibliothèque en plus).' 'Python 3.9 or newer was not found. The companion needs it (no extra packages).')"
      fi
      if [ "$(uname -s)" = "Darwin" ]; then
        info "$(t 'Le plus simple : le programme officiel de python.org (ou « xcode-select --install »).' 'Easiest: the official installer from python.org (or "xcode-select --install").')"
      else
        info "$(t 'Installe le paquet python3 de ta distribution.' "Install your distribution's python3 package.")"
      fi
      if ask_yes "$(t 'Ouvrir la page de téléchargement de Python ?' 'Open the Python download page?')" n; then
        open_url "https://www.python.org/downloads/"
        pause_for
      else
        fail "$(t 'Installation arrêtée : rien n’a été modifié.' 'Install stopped: nothing was changed.')"
        return 1
      fi
    done
    ok "Python : $("$PY" -c 'import sys; print(sys.version.split()[0])') ($PY)"

    if find_claude; then
      HAVE_CLAUDE=1
      ok "Claude Code : $("$CLAUDE" --version 2>/dev/null | head -n 1)"
    else
      warn "$(t "Claude Code est introuvable. C'est l'assistant dans lequel le compagnon répond (abonnement Claude requis)." 'Claude Code was not found. It is the assistant the companion answers in (Claude subscription required).')"
      info "$(t "Installateur officiel d'Anthropic : curl -fsSL https://claude.ai/install.sh | bash" "Anthropic's official installer: curl -fsSL https://claude.ai/install.sh | bash")"
      if ask_yes "$(t "Lancer l'installateur officiel de Claude Code maintenant ?" "Run the official Claude Code installer now?")" n; then
        if curl -fsSL https://claude.ai/install.sh | bash; then
          find_claude && HAVE_CLAUDE=1
        fi
      else
        info "$(t 'Page officielle : https://claude.com/product/claude-code' 'Official page: https://claude.com/product/claude-code')"
      fi
      if [ "$HAVE_CLAUDE" = 1 ]; then ok "Claude Code : $CLAUDE"
      else warn "$(t "Je continue sans : relance cet installateur une fois Claude Code installé." "Continuing without it: run this installer again once Claude Code is installed.")"; fi
    fi
  fi

  # ---------- 2. le jeu ----------
  local WOW="" detected=""
  normalize_wow() {  # affiche le dossier _forever_ correspondant, ou rien
    local p="${1%/}"
    [ -n "$p" ] || return 0
    case "$p" in "~"*) p="$HOME${p#\~}" ;; esac
    if [ "$(basename "$p")" = "_forever_" ] && [ -d "$p" ]; then printf '%s' "$p"
    elif [ -d "$p/_forever_" ]; then printf '%s' "$p/_forever_"
    elif [ -d "$p/World of Warcraft/_forever_" ]; then printf '%s' "$p/World of Warcraft/_forever_"; fi
  }
  if [ "$UNINSTALL" = 0 ]; then step "$(t 'Recherche de WoW Forever' 'Finding WoW Forever')"; fi
  if [ -n "$WOW_ARG" ]; then
    WOW="$(normalize_wow "$WOW_ARG")"
    [ -n "$WOW" ] || warn "$(t "Pas de dossier _forever_ dans : $WOW_ARG" "No _forever_ folder in: $WOW_ARG")"
  fi
  if [ -z "$WOW" ] && [ -z "$WOW_ARG" ]; then
    local pyc="${PY:-}"
    if [ -z "$pyc" ]; then find_python >/dev/null 2>&1 && pyc="$PY"; fi
    local wp="${SRC:-$APP}/plugins/forever-companion/mcp"
    if [ -n "$pyc" ] && [ -f "$wp/wowpaths.py" ]; then
      detected="$(cd "$wp" && "$pyc" -c 'import wowpaths; p = wowpaths.detect_wow_paths(); print(p[0] if p else "")' 2>/dev/null || true)"
      WOW="$(normalize_wow "$detected")"
    fi
    if [ -z "$WOW" ]; then
      local c
      for c in "/Applications/World of Warcraft/_forever_" "$HOME/Applications/World of Warcraft/_forever_"; do
        if [ -d "$c" ]; then WOW="$c"; break; fi
      done
    fi
  fi
  if [ -z "$WOW" ]; then
    local typed
    typed="$(ask_text "$(t 'Dossier du jeu introuvable. Glisse ici le dossier « World of Warcraft » (ou Entrée pour passer) :' 'Game folder not found. Drag the "World of Warcraft" folder here (or Enter to skip):')")"
    typed="$(printf '%s' "$typed" | sed -e "s/^[\"']//" -e "s/[\"'] *\$//" -e 's/\\ / /g' -e 's/ *$//')"
    [ -n "$typed" ] && WOW="$(normalize_wow "$typed")"
  fi
  if [ -n "$WOW" ]; then ok "$(t 'Jeu' 'Game') : $WOW"
  else warn "$(t "Jeu introuvable : l'addon ne sera pas installé. Relance avec --wow-path \"/chemin/World of Warcraft\"." 'Game not found: the addon will not be installed. Run again with --wow-path "/path/World of Warcraft".')"; fi

  # ---------- 3. l'addon ----------
  local ADDONS_DIR="" DEST=""
  if [ -n "$WOW" ]; then ADDONS_DIR="$WOW/Interface/AddOns"; DEST="$ADDONS_DIR/ForeverScribe"; fi
  toc_version() { sed -n 's/^## Version: *//p' "$1" 2>/dev/null | tr -d '\r' | head -n 1; }

  if [ "$UNINSTALL" = 1 ]; then
    if [ -z "$DEST" ]; then warn "$(t 'Jeu introuvable : addon non retiré.' 'Game not found: addon not removed.')"
    elif [ -L "$DEST" ]; then rm -f "$DEST"; ok "$(t 'Lien de développement ForeverScribe retiré (sa cible est intacte).' 'ForeverScribe development link removed (its target is untouched).')"
    elif [ -d "$DEST" ]; then rm -rf "$DEST"; ok "$(t 'Addon ForeverScribe retiré.' 'ForeverScribe addon removed.')"
    else info "$(t 'Addon déjà absent.' 'Addon already absent.')"; fi
    info "$(t 'Les captures du jeu (WTF/…/SavedVariables) et ton dossier de joueur restent en place.' 'Game captures (WTF/…/SavedVariables) and your player folder stay in place.')"

    step "$(t 'Retrait du plugin Claude Code' 'Removing the Claude Code plugin')"
    if find_claude; then
      if "$CLAUDE" plugin uninstall "$PLUGIN_ID" >/dev/null 2>&1; then ok "$(t 'Plugin retiré.' 'Plugin removed.')"
      else info "$(t 'Plugin déjà absent.' 'Plugin already absent.')"; fi
      if "$CLAUDE" plugin marketplace remove "$MARKET_NAME" >/dev/null 2>&1; then ok "$(t 'Marketplace retirée.' 'Marketplace removed.')"; fi
    else info "$(t 'Claude Code absent : rien à retirer.' 'Claude Code absent: nothing to remove.')"; fi

    step "$(t 'Nettoyage' 'Cleanup')"
    if [ -d "$APP" ]; then rm -rf "$APP"; ok "$(t "Outils de l'installateur retirés" 'Installer tools removed') ($APP)"; fi
    ok "$(t 'Ton dossier de joueur est intact' 'Your player folder is untouched') : $DATA_DIR"
    printf '\n%s%s%s\n\n' "$B$G" "$(t 'Désinstallation terminée.' 'Uninstall complete.')" "$N"
    return 0
  fi

  step "$(t "Installation de l'addon ForeverScribe" 'Installing the ForeverScribe addon')"
  if [ -z "$DEST" ]; then
    RESULT_ADDON="skip"; warn "$(t 'Étape passée (jeu introuvable).' 'Step skipped (game not found).')"
  elif [ -L "$DEST" ]; then
    RESULT_ADDON="dev"; info "$(t "Lien de développement détecté : je n'y touche pas." 'Development link detected: left as is.')"
  else
    local newv oldv=""
    newv="$(toc_version "$SRC/addon/ForeverScribe/ForeverScribe.toc")"
    [ -d "$DEST" ] && oldv="$(toc_version "$DEST/ForeverScribe.toc")"
    if mkdir -p "$ADDONS_DIR" && rm -rf "$DEST.tmp-install" && cp -R "$SRC/addon/ForeverScribe" "$DEST.tmp-install" \
       && rm -rf "$DEST" && mv "$DEST.tmp-install" "$DEST"; then
      RESULT_ADDON="ok"
      if [ -n "$oldv" ] && [ "$oldv" != "$newv" ]; then ok "$(t 'Addon mis à jour' 'Addon updated') : $oldv → $newv"
      elif [ -n "$oldv" ]; then ok "$(t 'Addon réinstallé' 'Addon reinstalled') ($newv)"
      else ok "$(t 'Addon installé' 'Addon installed') ($newv)"; fi
      info "$DEST"
    else
      rm -rf "$DEST.tmp-install" 2>/dev/null || true
      RESULT_ADDON="fail"; fail "$(t "Copie impossible dans $ADDONS_DIR (droits ?)." "Could not copy into $ADDONS_DIR (permissions?).")"
    fi
  fi

  # ---------- 4. le plugin Claude Code ----------
  step "$(t 'Installation du plugin dans Claude Code' 'Installing the plugin in Claude Code')"
  if [ "$HAVE_CLAUDE" = 0 ]; then
    RESULT_PLUGIN="skip"; warn "$(t 'Étape passée (Claude Code absent).' 'Step skipped (Claude Code missing).')"
  else
    local out
    if "$CLAUDE" plugin marketplace list 2>/dev/null | grep -Eq "(^|[[:space:]])$MARKET_NAME[[:space:]]*\$"; then
      "$CLAUDE" plugin marketplace update "$MARKET_NAME" >/dev/null 2>&1 \
        && ok "$(t 'Marketplace mise à jour.' 'Marketplace updated.')" \
        || warn "$(t 'Mise à jour de la marketplace impossible (réseau ?).' 'Could not update the marketplace (network?).')"
    else
      if out="$("$CLAUDE" plugin marketplace add "$MARKET_SOURCE" 2>&1)"; then ok "$(t 'Marketplace ajoutée' 'Marketplace added') ($MARKET_SOURCE)"
      else fail "$(t 'Ajout de la marketplace impossible' 'Could not add the marketplace') : $(printf '%s' "$out" | tail -n 1)"; fi
    fi
    if "$CLAUDE" plugin list 2>/dev/null | grep -q "$PLUGIN_ID"; then
      if out="$("$CLAUDE" plugin update "$PLUGIN_ID" 2>&1)"; then RESULT_PLUGIN="ok"; ok "$(t 'Plugin mis à jour (redémarre Claude Code pour en profiter).' 'Plugin updated (restart Claude Code to use it).')"
      else RESULT_PLUGIN="fail"; fail "$(t 'Mise à jour du plugin impossible' 'Could not update the plugin') : $(printf '%s' "$out" | tail -n 1)"; fi
    else
      if out="$("$CLAUDE" plugin install "$PLUGIN_ID" 2>&1)"; then RESULT_PLUGIN="ok"; ok "$(t 'Plugin installé' 'Plugin installed') ($PLUGIN_ID)"; info "$(t "Si Claude Code était ouvert, redémarre-le." 'If Claude Code was open, restart it.')"
      else RESULT_PLUGIN="fail"; fail "$(t 'Installation du plugin impossible' 'Could not install the plugin') : $(printf '%s' "$out" | tail -n 1)"; fi
    fi
  fi

  # ---------- 5. dossier du joueur et outils ----------
  step "$(t 'Ton dossier de joueur' 'Your player folder')"
  case "$DATA_DIR" in "~"*) DATA_DIR="$HOME${DATA_DIR#\~}" ;; esac
  if mkdir -p "$DATA_DIR/perso"; then
    chmod 700 "$DATA_DIR/perso" 2>/dev/null || true
    if [ -f "$DATA_DIR/CLAUDE.md" ]; then
      ok "$(t 'Dossier existant gardé tel quel' 'Existing folder kept as is') : $DATA_DIR"
    else
      local tpl="$SRC/perso.example/CLAUDE.md"
      [ "$L" = "en" ] && [ -f "$SRC/perso.example/CLAUDE.example.en.md" ] && tpl="$SRC/perso.example/CLAUDE.example.en.md"
      cp "$tpl" "$DATA_DIR/CLAUDE.md" && ok "$(t 'Dossier créé' 'Folder created') : $DATA_DIR"
    fi
    RESULT_DATA="ok"
  else
    RESULT_DATA="fail"; fail "$(t "Impossible de créer $DATA_DIR" "Could not create $DATA_DIR")"
  fi
  # Copie des outils (construction de la base, désinstallation) hors du dossier temporaire.
  if [ "$SRC" != "$APP" ]; then
    rm -rf "$APP.tmp-install" && mkdir -p "$APP.tmp-install" \
      && cp -R "$SRC/plugins" "$SRC/tools" "$SRC/install" "$APP.tmp-install/" 2>/dev/null \
      && { [ ! -f "$SRC/LICENSE" ] || cp "$SRC/LICENSE" "$APP.tmp-install/"; } \
      && rm -rf "$APP" && mv "$APP.tmp-install" "$APP" \
      && info "$(t 'Outils gardés dans' 'Tools kept in') : $APP" \
      || warn "$(t "Copie des outils impossible dans $APP" "Could not copy the tools into $APP")"
  fi

  # ---------- 6. base locale du jeu ----------
  step "$(t 'Base locale du jeu' 'Local game database')"
  local BUILD="$APP/tools/gamedata/build_db.py"
  [ -f "$BUILD" ] || BUILD="$SRC/tools/gamedata/build_db.py"
  local ROOT=""
  [ -n "$WOW" ] && ROOT="$(dirname "$WOW")"
  if [ -z "$ROOT" ]; then
    RESULT_DB="skip"; warn "$(t 'Étape passée (jeu introuvable).' 'Step skipped (game not found).')"
  elif [ "$NO_DB" = 1 ]; then
    RESULT_DB="skip"; info "$(t 'Étape passée (--no-db).' 'Step skipped (--no-db).')"
  else
    info "$(t "Elle donne au compagnon les objets, quêtes, PNJ, /way et cartes de TON client. Lecture seule du jeu ; télécharge une fois CascLib et QuestieDB ; quelques minutes." "It gives the companion the items, quests, NPCs, /way and maps of YOUR client. Reads the game only; downloads CascLib and QuestieDB once; a few minutes.")"
    if ask_yes "$(t 'Construire (ou mettre à jour) la base maintenant ?' 'Build (or update) the database now?')" y 1; then
      if "$PY" "$BUILD" --wow "$ROOT" --data-dir "$DATA_DIR"; then RESULT_DB="ok"; ok "$(t 'Base prête.' 'Database ready.')"
      else RESULT_DB="fail"; warn "$(t 'La construction a échoué ; le compagnon marche quand même, en moins précis.' 'The build failed; the companion still works, with less detail.')"; fi
    else
      RESULT_DB="later"; info "$(t 'Plus tard' 'Later') : \"$PY\" \"$BUILD\" --wow \"$ROOT\""
    fi
  fi

  # ---------- récapitulatif ----------
  mark() { case "$1" in ok) printf '%s✔%s' "$G" "$N" ;; dev) printf '%s✔%s' "$G" "$N" ;; fail) printf '%s✘%s' "$R" "$N" ;; *) printf '%s–%s' "$Y" "$N" ;; esac; }
  printf '\n%s%s%s\n' "$B" "$(t 'Récapitulatif' 'Summary')" "$N"
  printf '  %s %s\n' "$(mark "$RESULT_ADDON")" "$(t 'Addon ForeverScribe' 'ForeverScribe addon')"
  printf '  %s %s\n' "$(mark "$RESULT_PLUGIN")" "$(t 'Plugin Claude Code' 'Claude Code plugin')"
  printf '  %s %s\n' "$(mark "$RESULT_DATA")" "$(t 'Dossier du joueur' 'Player folder') ($DATA_DIR)"
  printf '  %s %s\n' "$(mark "$RESULT_DB")" "$(t 'Base locale du jeu' 'Local game database')"

  printf '\n%s%s%s\n' "$B" "$(t 'Et maintenant :' 'Next:')" "$N"
  printf '  1. %s\n' "$(t 'Redémarre complètement le jeu (pas seulement /reload).' 'Fully restart the game (not just /reload).')"
  printf '  2. %s\n' "$(t 'En jeu, appuie sur Ctrl+Maj+S (ou tape /sync).' 'In game, press Ctrl+Shift+S (or type /sync).')"
  printf '  3. %s\n' "$(t "Ouvre Claude Code dans ton dossier : cd \"$DATA_DIR\" && claude" "Open Claude Code in your folder: cd \"$DATA_DIR\" && claude")"
  printf '     %s\n\n' "$(t 'et demande : « Je fais quoi maintenant ? »' 'and ask: "What should I do now?"')"

  if [ "$RESULT_ADDON" = "fail" ] || [ "$RESULT_PLUGIN" = "fail" ] || [ "$RESULT_DATA" = "fail" ]; then return 1; fi
  if [ "$RESULT_ADDON" = "skip" ] || [ "$RESULT_PLUGIN" = "skip" ]; then
    printf '%s%s%s\n\n' "$Y" "$(t 'Installation incomplète : voir les étapes marquées « – ».' 'Install incomplete: see the steps marked "–".')" "$N"
    return 2
  fi
  printf '%s%s%s\n\n' "$B$G" "$(t 'Installation terminée. Bon jeu !' 'All set. Have fun!')" "$N"
  return 0
}

forever_install "$@"
