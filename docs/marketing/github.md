# Page GitHub — propositions

Statut : **suggestions**. Rien n'est appliqué sur GitHub ni publié sans l'accord du mainteneur.

## Description du dépôt (≤ 350 caractères)

Retenue (EN, 242 caractères) :
> AI companion for World of Warcraft: Forever. An addon captures your character, a local
> database reads your game client, and Claude answers your questions with your gear, your
> quest log and /way coordinates. EN/FR. Everything stays on your PC.

Alternative courte (EN, 128 caractères) :
> Your WoW: Forever character + the game's own data + Claude. Answers with exact numbers
> and /way coordinates. Local, EN/FR, MIT.

Champ « Website » : laisser vide ou pointer vers la release.

## Topics

`world-of-warcraft`, `wow-addon`, `wow-forever`, `wow-classic`, `claude-code`,
`claude-code-plugin`, `mcp`, `mcp-server`, `ai-companion`, `lua`, `python`, `questie`,
`gaming`, `game-assistant`

## Accroche (README)

Retenue :
> **Forever isn't Classic. Your companion knows the difference.**

Alternatives :
1. > **Your character, your client, your questions. Answered with `/way` coordinates, not guesses.**
2. > **The guildmate who read your bags before answering.**

## Social preview (1280 × 640)

- **Idée A, recommandée** : fond sombre façon parchemin ; à gauche la question « What should
  I do now? », à droite la réponse avec deux `/way` surlignés ; en bas le titre et
  « EN · FR · local · MIT ». Aucune image ni logo Blizzard (marque déposée).
- **Idée B** : capture de la fenêtre Claude Code à côté du jeu (minimap visible, interface du
  jeu floutée), une flèche de la touche Ctrl+Shift+S vers la réponse.
- **Idée C** : le tableau « A chatbot / The companion », en grand, trois lignes.

## Captures et GIF à produire (en jeu)

Avec un perso sans nom réel visible (masquer le nom, la guilde et le royaume, ou utiliser un
perso créé pour l'occasion). Interface du jeu en anglais pour la page EN si possible.

1. **GIF de tête (≈ 15 s)** : en jeu aux Paluns, appuyer sur Ctrl+Shift+S (court chargement)
   → bascule sur Claude Code → taper « What should I do now? » → la réponse s'affiche avec
   les `/way` → retour en jeu, coller `/way 38.8 52.4`, la flèche pointe vers Whelgar.
2. **Comparaison d'arme** : infobulle de l'arbalète en jeu (Maj survol) à gauche, réponse
   « Crossbow or rifle? » à droite. Image fixe.
3. **Quête bloquée** : la carte du monde ouverte sur l'Excavation, et la réponse des
   fragments avec les trois `/way`. Image fixe.
4. **Le bouton et la synchro** : le bouton parchemin près de la minimap, le message
   « ForeverScribe: … » dans le chat après `/scribe`. Petite image pour l'installation.
5. **Familier** (optionnel) : la fenêtre du familier ouverte (bonheur), la réponse à côté.

Format : PNG pour les images, GIF ou MP4 court (moins de 10 Mo) pour la démo, rangés dans
`docs/media/` (à créer au moment de la publication).

## Badges

En place dans les deux README (appliqués le 18/11) : tests GitHub Actions
(`.github/workflows/tests.yml`, macOS, Windows, Ubuntu), licence MIT, WoW Forever 1.60,
Python 3.9+ stdlib, macOS · Windows · Linux, client enUS · frFR. À ajouter : dernière release.

## Première release publique

Titre : **v0.8.0 — Forever companion, first public release** (ou la version en cours).

Structure des notes :
1. Une phrase d'accroche et le GIF.
2. **What it does** : 4 puces (ton perso, les données Forever, les quêtes avec `/way`, EN/FR).
3. **Install** : les 3 étapes.
4. **What's inside** : addon ForeverScribe x.y, plugin forever-companion x.y, nombre d'outils.
5. **Known limits** : quêtes propres à Forever, butin des donjons, tests Windows/Linux légers.
6. **Feedback wanted** : testeurs Windows, Linux et client anglais.
7. Mention légale (fan project, marques Blizzard, données Questie non redistribuées).

Pièce jointe possible : un zip de l'addon seul (`ForeverScribe-x.y.zip`) pour ceux qui ne
veulent pas cloner.

## Où annoncer (après accord)

| Canal | Angle | Remarque |
|---|---|---|
| r/classicwow, sous-reddit Forever s'il existe | « Forever isn't Classic » + GIF | vérifier les règles d'autopromo |
| r/ClaudeAI, r/ClaudeCode | plugin Claude Code + MCP + addon, cas d'usage concret | angle technique |
| Discord Forever FR / EN, Discord de guilde | démo et appel aux testeurs | demander aux modos |
| Discord Questie | remerciements, lien vers la doc QuestieDB | ne pas solliciter de données |
| CurseForge et Wago (addon seul) | ForeverScribe comme addon de capture | vérifier que l'addon a un sens seul ; licence et description claires |
| Annuaires MCP / plugins Claude Code | fiche du serveur `forever` | |

Rappels : pas d'image ni de logo Blizzard, mention « not affiliated », aucune donnée de
joueur réelle dans les captures.
