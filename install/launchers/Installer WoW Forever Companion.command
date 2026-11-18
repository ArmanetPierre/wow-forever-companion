#!/bin/bash
# Double-clic : installe ou met à jour WoW Forever Companion (macOS).
# Double-click: installs or updates WoW Forever Companion (macOS).
cd "$(dirname "$0")" || exit 1
clear 2>/dev/null || true
# L'archive téléchargée porte la « quarantaine » de macOS : on la retire de NOS fichiers
# seulement, pour que les scripts lancés ensuite ne soient pas bloqués un par un.
/usr/bin/xattr -dr com.apple.quarantine "files" >/dev/null 2>&1 || true
bash "files/install/install.sh" "$@"
code=$?
echo
case "${LC_ALL:-${LANG:-$(defaults read -g AppleLocale 2>/dev/null)}}" in
  fr*|FR*) printf 'Appuie sur Entrée pour fermer cette fenêtre. ' ;;
  *) printf 'Press Enter to close this window. ' ;;
esac
read -r _ || true
echo
exit $code
