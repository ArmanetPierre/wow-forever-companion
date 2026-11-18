# Page GitHub — propositions

Statut : **suggestions**. Rien n'est appliqué sur GitHub ni publié sans l'accord du mainteneur.

## Description du dépôt (≤ 350 caractères)

Retenue (EN, mise à jour le 18/11 après le comparatif) :
> AI companion for World of Warcraft: Forever. It reads your character and your game client,
> then answers with your quest log, your gear, exact /way coordinates and a zone map.
> No Classic guesses. EN/FR, local, MIT.

Ancienne version (242 caractères) :
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
> **A guide built around your character: personalised advice to get the most out of WoW Forever.**

Sous-titre proposé (après le comparatif) :
> **ChatGPT knows the news. The companion knows your character, your quests and the game's
> own data, and it doesn't make things up.**

Alternatives :
1. > **Your character, your client, your questions. Answered with `/way` coordinates, not guesses.**
2. > **The guildmate who read your bags before answering.**

## Bloc README proposé : « Pourquoi pas juste ChatGPT ? »

À placer après « What it does ». Le texte est proposé ici seulement : les README ne sont pas
modifiés.

**EN**

> ### Why not just ask ChatGPT?
>
> ChatGPT is good at news: GDKP ban, new raids, Éolides. On those questions it almost
> matches the companion. It doesn't know **your** character, and when it doesn't know a quest
> detail, it guesses.
>
> Blind test, 18/11/2026, 12 questions, each answer scored out of 12:
>
> | | Companion | ChatGPT | Gemini |
> |---|---|---|---|
> | Average | **11.8** | 8.6 | 8.2 |
> | Questions about your character | **12** | 5–8 | 3–8 |
> | Classic traps / made-up facts | **0 / 0** | 1 / 2 | 3 / 3 |
>
> ChatGPT and Gemini were given a hand-written character sheet for the averages, which is
> their best case. Ranges cover both runs, with and without the sheet; trap and made-up counts are for the run without the sheet.
> Response time is similar (about 10–25 s). Limits: the judge is a Claude model and the
> reference answers share the companion's sources. Full report and transcripts:
> [docs/comparaison/bilan.md](docs/comparaison/bilan.md) (in French).

**FR**

> ### Pourquoi pas juste ChatGPT ?
>
> ChatGPT est bon sur l'actualité : GDKP interdits, nouveaux raids, Éolides. Sur ces questions,
> il fait presque jeu égal. Mais il ne connaît pas **ton** perso, et quand il ne connaît pas
> un détail de quête, il devine.
>
> Test à l'aveugle du 18/11/2026, 12 questions, chaque réponse notée sur 12 :
>
> | | Compagnon | ChatGPT | Gemini |
> |---|---|---|---|
> | Moyenne | **11,8** | 8,6 | 8,2 |
> | Questions sur ton perso | **12** | 5 à 8 | 3 à 8 |
> | Pièges Classic / inventions graves | **0 / 0** | 1 / 2 | 3 / 3 |
>
> Pour les moyennes, ChatGPT et Gemini avaient une fiche du perso écrite à la main : c'est leur
> meilleur cas. Les fourchettes couvrent les deux essais, avec et sans fiche ; les pièges et inventions comptent l'essai sans fiche.
> Temps de réponse comparable (environ 10 à 25 s). Limites : le juge est un modèle Claude, et
> les références partagent les sources du compagnon. Rapport complet et transcriptions :
> [docs/comparaison/bilan.md](docs/comparaison/bilan.md).

Vérification des chiffres : moyennes avec fiche (GPT-B 8,6 ; GEM-B 8,2). « Questions sur ton
perso » : de la plus basse à la plus haute moyenne C01-C04 (ChatGPT 5,2 à 7,8 ; Gemini 3,0 à
7,8). Pièges et inventions : le maximum des deux conditions (ChatGPT : 1 piège sans fiche,
2 inventions dans chaque condition ; Gemini : 3 et 3 sans fiche). Source : `resultats.md`.

## Social preview (1280 × 640)

- **Idée A, recommandée** : fond sombre façon parchemin ; à gauche la question « What should
  I do now? », à droite la réponse avec deux `/way` surlignés ; en bas le titre et
  « EN · FR · local · MIT ». Aucune image ni logo Blizzard (marque déposée).
- **Idée B** : capture de la fenêtre Claude Code à côté du jeu (minimap visible, interface du
  jeu floutée), une flèche de la touche Ctrl+Shift+S vers la réponse.
- **Idée C** : le tableau « A chatbot / The companion », en grand, trois lignes.
- **Idée D** : la carte des Paluns avec deux repères numérotés, et au-dessus la question « Where are the tablet fragments? ». C'est visuel, et c'est ce que ChatGPT ne fait pas avec des coordonnées justes.

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
6. **Carte avec repères** : l'image rendue par l'outil `map` sur les Paluns (Menethil,
   Whelgar, perso en bleu), à côté de la réponse qui la cite. L'image d'essai existe déjà,
   mais elle vient d'un vrai perso : la refaire avec Brannok avant de la publier. La carte
   vient du client Blizzard : la montrer comme capture d'écran du rendu, sans distribuer les
   fichiers extraits.
7. **Avant / après C03** : à gauche, la réponse de Gemini (« serveur privé WotLK 3.3.5 », vider
   le cache), tirée de `docs/comparaison/reponses/gem-A.md` ; à droite, la réponse du compagnon
   avec les 4 `/way` et la carte. Mettre la note du juge sous chaque réponse (2/12 et 12/12).
   Mettre aussi une ligne sur le cas où ChatGPT fait aussi bien (C10), pour rester crédible.

8. **Schémas d'explication (faits)** : `docs/marketing/schemas/`, en clair et en sombre.
   - `1-comment-il-repond.png` pour la section « How it works » du README ;
   - `3-avec-ou-sans-mcp.png` sous le bloc « Pourquoi pas juste ChatGPT ? » ;
   - `4-ce-qui-reste-chez-toi.png` pour la section confidentialité.
   Dans le README, utiliser `<picture>` pour servir la version sombre en mode sombre.

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
| r/classicwow, sous-reddit Forever s'il existe | « A guide built around your character » + GIF | vérifier les règles d'autopromo |
| r/ClaudeAI, r/ClaudeCode | plugin Claude Code + MCP + addon, cas d'usage concret | angle technique |
| Discord Forever FR / EN, Discord de guilde | démo et appel aux testeurs | demander aux modos |
| Discord Questie | remerciements, lien vers la doc QuestieDB | ne pas solliciter de données |
| CurseForge et Wago (addon seul) | ForeverScribe comme addon de capture | vérifier que l'addon a un sens seul ; licence et description claires |
| Annuaires MCP / plugins Claude Code | fiche du serveur `forever` | |

Rappels : pas d'image ni de logo Blizzard, mention « not affiliated », aucune donnée de
joueur réelle dans les captures.
