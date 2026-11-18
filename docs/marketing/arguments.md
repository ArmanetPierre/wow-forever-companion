# Arguments — WoW Forever Companion

Statut : **proposition**. Les exemples suivent la voix `joueur` de
`plugins/forever-companion/knowledge/voix.md`. Perso fictif : **Brannok**, Nain Chasseur 25,
Alliance, Les Paluns. Les chiffres marqués « à mesurer » ne sont pas encore vérifiés.

## La proposition de valeur en une phrase

> Un compagnon qui connaît ton perso et les données de Forever, et qui te répond comme un
> pote de guilde : le verdict, les chiffres, le `/way`.

En trois temps :
1. **Il sait où tu en es** : il lit ton perso au lieu de te poser dix questions.
2. **Il sait ce qui existe dans Forever** : les données viennent de ton client et des
   correctifs du serveur, pas d'un souvenir de Classic.
3. **Il dit d'où il le tient** : base Forever, QuestieDB ou souvenir Classic, et à quel point
   c'est sûr.

## Les 3 arguments les plus forts

1. **« Forever n'est pas Classic, ton compagnon le sait. »** Une IA généraliste répond de
   mémoire Classic. Ici les objets et leurs stats viennent de ton client Forever et de ses
   correctifs serveur, et toute info Classic est signalée comme telle.
2. **« Zéro question de contexte. »** Niveau, stuff, talents, journal de quêtes, récompenses,
   familier, sacs, métiers : tout est déjà là. Tu demandes « je fais quoi ? », il répond.
3. **« Des `/way`, pas des “quelque part au nord” ».** 80 313 positions de PNJ et d'objets
   dans ta base locale : donneur, receveur, objectifs, tout se colle dans la barre de chat.

Arguments de réassurance :
- **Tout reste chez toi** : capture locale, base locale, aucun identifiant lu.
- **Il ne joue pas à ta place** : l'addon lit l'API, n'appuie sur aucune touche, rien en combat.
- **Gratuit et ouvert** : MIT, code lisible, Python sans dépendance.
- **Pour toute la bande** : chacun l'installe et garde ses données, plusieurs comptes et persos.

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
| Outils du serveur | 14 (28 en v0.7) | mesuré |
| Coût fixe en contexte | ≈ 4,6 k tokens (≈ 9,6 k en v0.7) | mesuré (`docs/evals/mesure.py`) |
| Première session sans base locale (question casque) | 21 appels, ≈ 107 k tokens, ≈ 2 min 30 | mesuré (17/11) |
| Appels d'outils par question courante | 1,0 en moyenne (3,8 en v0.5) | mesuré (`docs/evals/mesure.py`) |
| Questions de vrais joueurs rejouées | 72 | mesuré (`docs/evals/banque-questions.md`) |
| Temps de réponse ressenti par le joueur | — | à mesurer |
| Recherches web évitées sur les 72 questions | — | à mesurer (compté par lot, pas encore consolidé) |

Le bon récit chiffré : **« La première fois, une question sur un casque a demandé 21 appels
et 2 min 30 de recherche web. Avec la base locale, la même réponse tient en un appel. »**
Le « un appel » est mesuré en v0.8 par `docs/evals/mesure.py` (1,0 appel en moyenne sur les
questions types).

## Ce qu'on ne promet pas

- Pas de réponse dans le jeu (pour l'instant) : on pose la question dans une fenêtre à côté.
- Pas toutes les quêtes Forever d'un coup : celles ajoutées par Forever manquent dans
  QuestieDB ; l'addon les apprend pendant que tu joues, Wowhead complète au cas par cas.
- Pas un butin garanti : les sources de butin viennent de QuestieDB, donc de Classic.
- Pas de garantie Blizzard : projet de fan, non affilié.
