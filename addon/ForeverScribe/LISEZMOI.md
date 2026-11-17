# ForeverScribe

Addon qui enregistre l'état de ton personnage (identité, niveau, zone, stats,
équipement, talents, quêtes, métiers, familier, sacs, réputations…) pour le compagnon
IA. Il ne fait **que lire** : aucune action en jeu, aucun envoi sur Internet.

Le format des données est décrit dans [`docs/schema.md`](../../docs/schema.md).
English version: [`README.md`](README.md).

**Langue du client** : l'addon marche avec un jeu en français, en anglais ou dans une
autre langue. Les messages sont en français pour un client français, en anglais sinon ;
les commandes acceptent les deux (`touche` ou `key`, `bouton` ou `button`, `statut` ou
`status`, `aide` ou `help`).

**Mise à jour vers 1.3.0** : elle ajoute le fichier `Locales.lua`. **Quitte et relance
complètement le jeu** (un `/reload` ne charge pas un nouveau fichier).

## Installation

Déjà faite sur le Mac de Pierre : `Interface/AddOns/ForeverScribe` est un lien vers ce
dossier du repo.

Pour un autre ordinateur, depuis le dossier du repo :

| Système | Commande |
|---|---|
| macOS / Linux | `addon/install.sh` (ou `addon/install.sh --wow-path "/chemin/_forever_"`) |
| Windows | `powershell -ExecutionPolicy Bypass -File addon\install.ps1` |

Si le jeu ne voit pas l'addon, relance avec `--copy` (macOS/Linux) ou `-Copy` (Windows).

## Test en jeu, pas à pas (5 minutes)

1. **Quitte complètement le jeu puis relance-le.** Un `/reload` ne suffit pas pour
   qu'un nouvel addon déclare ses fichiers de sauvegarde.
2. Écran de sélection des personnages → bouton **AddOns** : coche **ForeverScribe**.
   S'il est marqué « obsolète », coche **Charger les addons obsolètes**.
3. Connecte **Brannok**. Après ~5 s, le chat affiche :
   `ForeverScribe : prêt (19 domaines capturés). … /scribe aide`
4. **Appelle ton familier** s'il n'est pas déjà là.
5. **Ouvre ta fenêtre de métier** (Travail du cuir) quelques secondes, puis ferme-la.
   Fais pareil avec ton 2ᵉ métier, ta cuisine et ton secourisme si tu en as.
6. Si tu passes près d'une banque : **ouvre ta banque** quelques secondes.
7. Tape **`/scribe`** : capture complète et une ligne de résumé.
8. Tape **`/scribe status`** : chaque domaine doit être **OK**. Note ceux en
   **ERREUR**, ceux marqués « fonction(s) absente(s) » ou « appel(s) en erreur ».
9. Ouvre ta fiche de personnage (**C**) et note la **puissance d'attaque à distance**
   affichée. Elle sert à vérifier un calcul de l'addon.
10. Tape **`/reload`** : c'est ce qui écrit les fichiers sur le disque.
11. Préviens Claude.

Bonus pour le multi-perso : connecte aussi **Elwyna**, attends le message « prêt », puis
`/reload`.

## Synchroniser pour Claude

Le jeu n'écrit les données sur le disque qu'au rechargement de l'interface, à la
déconnexion ou en quittant le jeu. Pour que Claude voie ton état actuel, synchronise
en un geste (capture complète puis rechargement, ~3 s d'écran de chargement) :

| Geste | Comment |
|---|---|
| **Touche** | `/scribe touche` attribue **Ctrl+Maj+S** (si elle est libre). Autre touche : `/scribe touche ALT-F12`, ou **Options → Raccourcis → AddOns → ForeverScribe → Synchroniser pour Claude**. |
| **Commande** | `/sync` (ou `/scribe sync`) |
| **Bouton** | l'icône de parchemin au bord de la minicarte : clic = synchro, glisser = déplacer. `/scribe bouton` l'affiche ou la masque. L'infobulle donne l'âge des données. |
| **Automatique** | déconnexion et sortie du jeu : rien à faire. |

- **Jamais en combat** : le jeu l'interdit. L'addon refuse et te prévient à la sortie du
  combat ; il ne recharge jamais tout seul (le jeu exige un geste de ta part).
- Le raccourci par défaut Ctrl+Maj+S est déclaré dans `Bindings.xml`, mais le jeu ne
  l'applique qu'après « Réinitialiser les raccourcis » : utilise `/scribe touche` une fois.
- Après une mise à jour qui ajoute `Bindings.xml`, **quitte et relance complètement le
  jeu** (un `/reload` ne charge pas un nouveau fichier).

## Commandes

| Commande | Effet |
|---|---|
| `/scribe` | capture complète + résumé |
| `/scribe statut` (ou `status`) | état de chaque domaine (OK / erreur / jamais capturé, âge) |
| `/scribe aide` (ou `help`) | aide |
| `/sync` ou `/scribe sync` | synchroniser pour Claude (capture + rechargement) |
| `/scribe touche [TOUCHE]` (ou `key`) | attribuer la touche de synchro (défaut Ctrl+Maj+S, seulement si libre) |
| `/scribe bouton` (ou `button`) | afficher / masquer le bouton de la minicarte |

Les captures se font aussi toutes seules quand quelque chose change (2 s après,
jamais pendant un combat). Elles restent en mémoire jusqu'au prochain `/reload`, à la
déconnexion ou à la fermeture du jeu : c'est là que le jeu écrit les fichiers.

## Fichiers produits

```
WTF/Account/<COMPTE>/SavedVariables/ForeverScribe.lua                     (index des persos)
WTF/Account/<COMPTE>/<ROYAUME>/<Perso>/SavedVariables/ForeverScribe.lua   (état complet du perso)
```
Pour Brannok : `WTF/Account/123456789#1/93/Brannok-Durn/SavedVariables/ForeverScribe.lua`.

## Désactiver la sonde ForeverProbe

ForeverProbe n'est plus utile une fois ForeverScribe validé. Pour l'arrêter :
- en jeu : écran de sélection des personnages → **AddOns** → décoche **ForeverProbe** ;
- ou supprime le lien : `rm "/Applications/World of Warcraft/_forever_/Interface/AddOns/ForeverProbe"`
  (le dossier du repo n'est pas touché).

## Test hors jeu (développeurs)

```bash
lua addon/tests/run_capture.lua
```
Rejoue une session complète dans un WoW simulé (valeurs de la sonde), avec un client
français puis anglais, vérifie le schéma, vérifie que les clés non traduites sont
identiques dans les deux langues et régénère les exemples dans `addon/tests/fixtures/`
(`*.enUS.*` pour le client anglais).
