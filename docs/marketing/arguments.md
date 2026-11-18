# Arguments — WoW Forever Companion

Statut : **proposition**. Les exemples suivent la voix `joueur` de
`plugins/forever-companion/knowledge/voix.md`. Perso fictif : **Brannok**, Nain Chasseur 25,
Alliance, Les Paluns. Les chiffres marqués « à mesurer » ne sont pas encore vérifiés.

## La proposition de valeur en une phrase

> Le compagnon connaît ton perso et le détail de Forever : il te dit quoi rendre, où cliquer,
> avec le `/way` et la carte, et il n'invente pas.

Cible : les joueurs de WoW un peu geeks qui ont déjà un assistant de code sous la main
(Claude Code aujourd'hui). Ils connaissent ChatGPT ; il faut leur montrer ce qu'il ne sait pas
faire, pas le dénigrer.

En trois temps :
1. **Il sait où tu en es** : il lit ton perso (journal, sacs, familier, équipement) au lieu
   de te poser dix questions ou de te demander une fiche.
2. **Il sait ce qui existe dans Forever** : les données viennent de ton client et des
   correctifs du serveur, pas d'un souvenir de Classic.
3. **Il dit ce qu'il ne sait pas** : « entrée encore inconnue » plutôt que des coordonnées
   inventées, avec la source et la certitude.

## Les 3 arguments les plus forts

1. **« Il lit ton perso. »** Sur les 4 questions liées au perso du comparatif, le compagnon a
   12/12 à chaque fois. ChatGPT et Gemini ont 3 à 8 en moyenne, et au mieux 7,8 même quand on
   leur colle une fiche du perso. Lui seul voit les 13 quêtes à rendre dans un journal plein.
2. **« Des `/way` exacts, et maintenant la carte. »** Les positions viennent de la base locale
   (80 313 positions). L'outil `map` dessine la carte de la zone, tirée de ton client, avec
   les repères numérotés. Les généralistes inventent des coordonnées quand ils ne savent pas
   (comparatif : C03, C06).
3. **« Forever n'est pas Classic, et il ne bluffe pas. »** 0 piège Classic et 0 invention
   grave sur les 12 questions du comparatif. Gemini sans fiche : 3 pièges Classic et 3
   inventions graves. ChatGPT : 2 inventions graves, avec ou sans fiche.

Arguments de réassurance :
- **Tout reste chez toi** : capture locale, base locale, cartes extraites en local, aucun
  identifiant lu.
- **Il ne joue pas à ta place** : l'addon lit l'API, n'appuie sur aucune touche, rien en combat.
- **Gratuit et ouvert** : MIT, code lisible, Python sans dépendance.
- **Pour toute la bande** : chacun l'installe et garde ses données, plusieurs comptes et persos.

## Face à ChatGPT et Gemini

Comparatif à l'aveugle du 18/11/2026 : 12 questions, 5 réponses par question, notées sur 12.
Détails et limites : `docs/comparaison/bilan.md`.

| | Compagnon | ChatGPT (sans / avec fiche) | Gemini (sans / avec fiche) |
|---|---|---|---|
| Moyenne sur 12 | **11,8** | 7,8 / 8,6 | 6,1 / 8,2 |
| Questions liées au perso (C01-C04) | **12** | 5,2 / 7,8 | 3,0 / 7,8 |
| Actualité de Forever (C07-C12) | **11,7** | meilleure réponse : 10 à 11 selon la question | meilleure réponse : 8 à 11 selon la question |
| Pièges Classic tombés | **0** | 1 / 0 | 3 / 1 |
| Inventions graves | **0** | 2 / 2 | 3 / 1 |
| Temps de réponse | 10 à 12 s (Sonnet), 12 à 24 s (Opus), mesuré | 10 à 20 s, observé | même ordre, observé |

Ce qu'il faut retenir, honnêtement :
- **L'écart est sur le perso et le détail du jeu**, pas sur l'actualité. Sur les annonces
  (GDKP, Éolides, raids), ChatGPT fait presque aussi bien.
- **Le temps brut est comparable.** ChatGPT paraît plus rapide parce qu'il écrit dès la
  première seconde ; le compagnon lit d'abord le perso.
- **ChatGPT est gratuit, sur téléphone, avec images et voix.** On ne gagne pas là-dessus.

### Avant / après (voix `joueur`)

**C01 — « Je fais quoi maintenant ? »**
- ChatGPT, sans fiche, 4/12 : un circuit en 7 étapes, dont 5 quêtes introuvables dans les
  données du jeu, sans un seul `/way`.
- Compagnon, 12/12 :
  > **Rends d'abord tes 13 quêtes terminées** : ton journal est plein. Les PNJ et les `/way`
  > sont juste en dessous.

**C03 — « Je trouve pas les fragments de tablette, ils sont où ? »**
- Gemini, sans fiche, 2/12 : présente Forever comme un « serveur privé WotLK 3.3.5 » et
  conseille de vider le dossier Cache.
- Compagnon, 12/12 :
  > Les 4 sont dans l'Excavation. Trois dans des **Reliques anciennes**, le premier vers
  > `/way 34.1 49.9`, le dernier dans une **Terre meuble** vers `/way 33.1 46.4`. Retour chez
  > Whelgar `/way 38.8 52.4`. _QuestieDB · sûr_

**C04 — « Mon félin : je lui donne quoi et je mets où mes points de dressage ? »**
- Gemini, sans fiche, 1/12 : confond points de dressage et points de talent, et donne un arbre
  Maîtrise des bêtes avec des talents mal nommés.
- Compagnon, 12/12 :
  > **Tu as 120 points de dressage, dont 44 libres.** Ne lui donne pas les 3 ingrédients de
  > la *Goulash des Carmines* : ils sont pour ta quête. _Addon · sûr_

**Le cas où ChatGPT fait aussi bien — C10, « Les Éolides, c'est quelles classes ? »**
- ChatGPT, 11/12 : classes par faction, île de Zéphras, niveaux 1 à 12, pack requis. Juste
  et sourcé.
- Compagnon, 12/12 : même contenu, plus court.
- À montrer tel quel : ça rend le reste crédible.

## Schémas

Rendus en PNG dans `schemas/`, en clair et en sombre (`-sombre`). Détail et régénération :
`schemas/README.md`.

| Schéma | Ce qu'il fait comprendre | Où l'utiliser |
|---|---|---|
| `1-comment-il-repond` (+ `1b` web, `1c` règle) | L'ordre de recherche : ton perso, puis la base du jeu, puis les règles Forever. Le web vient en dernier et la trouvaille est gardée. | README « Comment ça marche », post de lancement |
| `2-ce-quil-sait` | Ce qu'il sait sans Internet, ce qu'il va chercher, ce qu'il signale au lieu d'inventer. | README, réponse aux sceptiques (« il invente comme ChatGPT ? ») |
| `3-avec-ou-sans-mcp` | Même question : un généraliste sans accès au jeu, contre le compagnon avec ses outils. Notes du comparatif. | Sous le bloc « Pourquoi pas juste ChatGPT ? » |
| `4-ce-qui-reste-chez-toi` | Ce qui tourne sur ton PC, et ce qui part vers l'IA : ta question et les résultats des outils. | Section confidentialité, FAQ |

## Personas

| Persona | Ce qui le bloque aujourd'hui | Ce que le compagnon lui apporte | Question type |
|---|---|---|---|
| **Le joueur en leveling** | Alt-tab sur Wowhead, guides Classic faux pour Forever | Les quêtes dispo autour de lui, à rendre d'abord, avec `/way` | « Je fais quoi maintenant ? » |
| **Le joueur Hardcore** | Une mauvaise info coûte le perso | Mise en garde en premier (niveau des mobs, élites, PvP), certitude affichée | « Je peux faire cette quête seul ? » |
| **Le crafteur** | Quel rang, quelle recette donne encore des points, quels compos | Recettes connues et leur couleur, compos dans les sacs et la banque | « Comment passer de 106 à 150 en Travail du cuir ? » |
| **Le chasseur** | Bonheur, nourriture, points de dressage du familier | État réel du familier croisé avec la nourriture en sac | « Mon familier fait la tête, je fais quoi ? » |
| **La petite bande d'amis** | Chacun cherche dans son coin | Même outil pour tous, données séparées, notes et objectifs par perso | « Compare mon stuff avec celui de mon mage » |
| **Le joueur anglophone** | Outils et guides FR ou Classic | Client enUS, réponses en anglais, noms du jeu tels quels | “Which quests can I turn in here?” |

## Exemples parlants (voix `joueur`)

**1. Leveling, « Je fais quoi maintenant ? »**
> **Rends d'abord tes 13 quêtes terminées**, dont 4 ici aux Paluns : c'est de l'XP gratuite,
> et ton journal est plein de toute façon. Ensuite deux nouvelles près de l'Excavation :
> *La vengeance d'Ormer* chez Ormer Ironbraid `/way 38.2 50.9` et *Découverte du passé* chez
> le Prospecteur Whelgar `/way 38.8 52.4`. _QuestieDB · sûr_

**2. Arme, « L'arbalète ou le fusil ? »**
> **Pas encore : il faut le niveau 26.** Ensuite, environ +2,4 DPS (+5,6 %) sur ton fusil,
> mais ta compétence Arbalètes est à 1/125 : au début tu vas rater pas mal de tirs. Monte-la
> sur des mobs gris ou verts avant de la sortir sur un élite. _Base locale Forever · probable_

**3. Quête bloquée, « Je trouve pas les fragments de Découverte du passé »**
> Les 4 sont dans l'Excavation à l'ouest du campement. Trois dans des **Reliques anciennes**,
> le premier vers `/way 34.1 49.9`, le dernier dans une **Terre meuble** vers `/way 33.1 46.4`.
> Les troggs respawn vite : pull un par un. Retour chez Whelgar `/way 38.8 52.4`.
> _QuestieDB · sûr_

**4. Stuff, « Évalue mon stuff »**
> **Ton point faible, c'est les jambes** : les *Jambières pétrolifères* (rares, niveau 25)
> te font environ +2 DPS, butin courant sur 13 PNJ. Tête, cou et bijoux vides, c'est normal
> à 25. Le *Casque de bagarreur en cuir* demande Travail du cuir ≈ 150 : tu es à 106, pas
> encore. _Base locale Forever · sûr_

**5. Chaîne de quêtes, “The Cursed Crew?”** (question en anglais, client français)
> Mobs are 26 to 28 around `/way 14.0 30.2`, a bit high for you, bring a friend. Snellig's
> Snuffbox drops from First Mate Snellig. You already did the prerequisite, *La IIIe flotte*;
> next up is *Levée de la malédiction*. _QuestieDB · confirmed_

**6. PNJ, « Il est où le Montagnard Rockgar ? »**
> Au Loch Modan, `/way 25.4 10.4`. Ses quêtes, tu les as déjà toutes faites, pas la peine
> d'y retourner pour ça. _QuestieDB · sûr_

**7. Progression, « Il me faut combien pour le 40 ? »**
> **823 312 XP** du niveau 25 au 40 : 6 912 pour finir le 25, puis 816 400 du 26 au 39.
> Tu as 912 d'XP reposée en réserve. _Base locale Forever · sûr (table d'XP du client)_

**8. Hardcore, « Je peux faire L'équipage maudit seul ? »**
> **Non, pas à 25 en HC.** Mobs 26 à 28, un à trois niveaux au-dessus de toi. Ça, c'est le
> genre de pull qui te coûte le perso. Reviens à 27 ou en groupe. _QuestieDB · sûr_
> (le mode Hardcore de Forever n'ouvre pas avant l'hiver 2026/27)

**9. Honnêteté, une info qui n'est pas dans Forever**
> Le butin de ce boss vient de QuestieDB, donc de Classic : Forever a revu des loots,
> _à vérifier en jeu_.

**10. Familier, « Mon familier est content ? »**
> **Oui : ton félin est heureux (125 % de dégâts), mais tu as 44 points de dressage qui
> dorment.** Passe voir un dresseur de familiers. Il mange viande et poisson, et tu as
> 10 Poisson-lune sauté dans les sacs pour la suite. _Addon · sûr_

## Bénéfices chiffrés

| Chiffre | Valeur | Statut |
|---|---|---|
| Quêtes dans la base locale (QuestieDB) | 4 244 | mesuré |
| PNJ / objets du monde | 10 119 / 6 645 | mesuré |
| Positions prêtes pour `/way` | 80 313 | mesuré |
| Objets dont on connaît la provenance | 10 144 | mesuré |
| Taille de la base (avec QuestieDB) | ≈ 17 Mo, construite en quelques secondes | mesuré |
| Objets dans la base locale | ≈ 24 700 | mesuré |
| Tests automatiques de l'addon | 695 contrôles, client frFR et enUS | mesuré |
| Outils du serveur | 15 (28 en v0.7), dont `map` | mesuré |
| Cartes de zone disponibles | 60 cartes du client, dont celles propres à Forever (Île de Zéphras, Mont Hyjal…) | mesuré |
| Temps de rendu d'une carte | moins d'1 s la première fois, puis 0,1 à 0,3 s | mesuré |
| Coût fixe en contexte | ≈ 4,6 k tokens (≈ 9,6 k en v0.7) | mesuré (`docs/evals/mesure.py`), avant l'outil `map` |
| Première session sans base locale (question casque) | 21 appels, ≈ 107 k tokens, ≈ 2 min 30 | mesuré (17/11) |
| Appels d'outils par question courante | 1,0 en moyenne (3,8 en v0.5) | mesuré (`docs/evals/mesure.py`) |
| Questions de vrais joueurs rejouées | 72 | mesuré (`docs/evals/banque-questions.md`) |
| Temps de réponse complet (de la question à la réponse) | 10 à 12 s avec Sonnet, 12 à 24 s avec Opus | mesuré le 18/11, 2 questions, un essai chacune |
| Note moyenne au comparatif à l'aveugle | 11,8 / 12 (ChatGPT 8,6, Gemini 8,2 avec fiche) | mesuré, juge de la famille Claude (`docs/comparaison/`) |
| Recherches web évitées sur les 72 questions | — | à mesurer (compté par lot, pas encore consolidé) |

Le bon récit chiffré : **« Sur les questions liées à ton perso, 12/12 contre 3 à 8 pour ChatGPT
et Gemini. »** Autre récit possible : **« La première fois, une question sur un casque a demandé 21 appels
et 2 min 30 de recherche web. Avec la base locale, la même réponse tient en un appel. »**
Le « un appel » est mesuré en v0.8 par `docs/evals/mesure.py` (1,0 appel en moyenne sur les
questions types).

## Ce qu'on ne dit pas

- **Pas « plus rapide que ChatGPT »** : c'est faux. Le temps brut est comparable, et ChatGPT
  écrit plus tôt.
- **Pas « ChatGPT se trompe sur tout »** : c'est faux sur l'actualité (10 à 11 sur 12 sur les
  GDKP, les Éolides, les raids).
- **Pas de note publique sans ses limites.** Toujours écrire, à côté du 11,8 :
  - le juge est un modèle Claude, de la même famille que le compagnon ;
  - les références ont été écrites avec les mêmes sources que le compagnon ;
  - les temps de ChatGPT et Gemini sont observés, pas chronométrés ;
  - il y a eu un seul tirage par question.
- **Pas de lien vers des conversations ChatGPT** d'un compte réel ; on cite les transcriptions
  de `docs/comparaison/reponses/`.

## Compatibilité

<!-- COMPAT -->
Vérifié dans les documentations officielles le 18/11/2026, **pas encore testé** hors de Claude Code.

| Assistant | Modèles | Le serveur `forever` | Ce qu'il faut adapter |
|---|---|---|---|
| **Claude Code** | Claude | Oui, installation en un clic (marketplace) | Rien : c'est la cible actuelle. |
| **GitHub Copilot, VS Code (agent)** | GPT, Claude, Gemini… | Oui (MCP local) | Un `.vscode/mcp.json` (clé `servers`). Les skills `SKILL.md` se réutilisent ; l'agent devient un `.agent.md`. |
| **GitHub Copilot CLI** | GPT et autres | Oui (MCP local) | `~/.copilot/mcp-config.json`. Lit `AGENTS.md` et les skills. |
| **OpenAI Codex CLI** | GPT | Oui (MCP local) | `[mcp_servers.forever]` dans `~/.codex/config.toml`, un `AGENTS.md`, skills dans `.agents/skills/`. Offre ChatGPT Plus ou clé API. |
| **Cursor** | GPT, Claude… | Oui (MCP local), images affichées | `.cursor/mcp.json`. |
| **Gemini CLI** | Gemini | Oui (MCP local) | `~/.gemini/settings.json`, un `GEMINI.md`. |
| **App ChatGPT** | GPT | **Non en direct** : seulement un serveur distant ou un tunnel | Inadapté : le serveur lit des fichiers sur le disque du joueur. |

Message possible, **après un test réel** : « Marche avec Claude Code, et avec Copilot ou Codex si
tu préfères GPT. » D'ici là : « Conçu pour Claude Code. Le serveur suit le standard MCP. »
Point à vérifier : l'affichage de l'image de la carte, documenté seulement dans Cursor et Gemini
CLI ; le chemin du PNG est toujours donné en texte.

## Ce qu'on ne promet pas

- Pas de réponse dans le jeu (pour l'instant) : on pose la question dans une fenêtre à côté.
- Pas sur téléphone, pas de voix : le compagnon se sert à l'ordinateur.
- Pas toujours le premier sur une annonce de la veille : sa base de connaissances doit être
  mise à jour, alors que ChatGPT cherche sur le web.
- Pas toutes les quêtes Forever d'un coup : celles ajoutées par Forever manquent dans
  QuestieDB ; l'addon les apprend pendant que tu joues, Wowhead complète au cas par cas.
- Pas un butin garanti : les sources de butin viennent de QuestieDB, donc de Classic.
- Pas de garantie Blizzard : projet de fan, non affilié.
