#!/usr/bin/env bash
# Installe les addons du compagnon WoW Forever (macOS / Linux).
#
# Usage :
#   addon/install.sh                      # installe ForeverScribe (lien symbolique)
#   addon/install.sh ForeverProbe         # installe un autre addon du dossier addon/
#   addon/install.sh --copy               # copie au lieu du lien symbolique
#   addon/install.sh --wow-path "/chemin/vers/_forever_"
#   WOW_FOREVER_PATH="/chemin/vers/_forever_" addon/install.sh
#
# Le lien symbolique garde l'addon à jour quand le repo change. Si le jeu ne voit pas
# l'addon (lien ignoré), relance avec --copy.
set -euo pipefail

ADDON_DIR="$(cd "$(dirname "$0")" && pwd)"
MODE="link"
WOW_PATH="${WOW_FOREVER_PATH:-}"
ADDONS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --copy) MODE="copy"; shift ;;
    --wow-path) WOW_PATH="$2"; shift 2 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) ADDONS+=("$1"); shift ;;
  esac
done
[ ${#ADDONS[@]} -eq 0 ] && ADDONS=("ForeverScribe")

if [ -z "$WOW_PATH" ]; then
  CANDIDATES=(
    "/Applications/World of Warcraft/_forever_"
    "$HOME/Applications/World of Warcraft/_forever_"
    "$HOME/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_forever_"
    "$HOME/Games/world-of-warcraft/drive_c/Program Files (x86)/World of Warcraft/_forever_"
    "$HOME/.wine/drive_c/Program Files (x86)/World of Warcraft/_forever_"
  )
  for c in "${CANDIDATES[@]}"; do
    if [ -d "$c" ]; then WOW_PATH="$c"; break; fi
  done
fi

if [ -z "$WOW_PATH" ] || [ ! -d "$WOW_PATH" ]; then
  echo "Dossier du jeu introuvable. Indique-le avec --wow-path \"/chemin/vers/World of Warcraft/_forever_\"" >&2
  exit 1
fi

TARGET_DIR="$WOW_PATH/Interface/AddOns"
mkdir -p "$TARGET_DIR"
echo "Dossier du jeu : $WOW_PATH"

for name in "${ADDONS[@]}"; do
  SRC="$ADDON_DIR/$name"
  DEST="$TARGET_DIR/$name"
  if [ ! -f "$SRC/$name.toc" ]; then
    echo "  $name : introuvable dans $ADDON_DIR (pas de $name.toc)" >&2
    exit 1
  fi
  if [ -L "$DEST" ]; then
    rm "$DEST"
  elif [ -d "$DEST" ]; then
    if [ "$MODE" = "copy" ]; then
      rm -rf "$DEST"
    else
      echo "  $name : un dossier existe déjà dans AddOns (ancienne copie ?)." >&2
      echo "  Supprime-le ou relance avec --copy pour le remplacer." >&2
      exit 1
    fi
  fi
  if [ "$MODE" = "link" ]; then
    ln -s "$SRC" "$DEST"
    echo "  $name : lien symbolique créé -> $SRC"
  else
    cp -R "$SRC" "$DEST"
    echo "  $name : copié dans $DEST (relance la commande après chaque mise à jour du repo)"
  fi
done

echo "Terminé. En jeu : écran de sélection des personnages > AddOns > vérifie que l'addon est coché."
