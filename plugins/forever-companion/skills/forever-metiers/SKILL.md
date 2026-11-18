---
name: forever-metiers
description: Métiers de WoW Forever : où en est le joueur, comment monter, formateur et rang suivant, recettes qui rapportent des points, composants, rentabilité. À utiliser dès que le joueur parle de récolte, d'artisanat, de recettes, de cuisine, de pêche, de secourisme ou de campement. EN: WoW Forever professions: skill, how to level, trainer and next rank, recipes that give points, reagents, profit. Use whenever the player talks about gathering, crafting or recipes.
---

# Métiers

> Réponds dans la langue de la question et passe `lang` (`fr`/`en`) ; les noms du jeu restent ceux du client. Forme et voix : instructions du serveur `forever` (verdict en gras d'abord, badge de source).

## Appels (budget : 1 outil, 0 à 2 web)

1. `professions` (`metier`, facultatif `cible` = compétence visée) — marche aussi pour un métier
   que le perso n'a pas (parcours depuis 1). Il donne :
   - le **palier actuel et le palier suivant** avec la compétence et le niveau requis, et s'ils
     sont atteints (« pas encore : 106/125 ») — seuils de Classic, marqués « [Classic] à vérifier » ;
   - les **formateurs** de ce palier pour la faction du perso, du plus proche au plus loin, avec `/way` ;
   - le **parcours de montée** : par tranche de compétence, la recette la moins chère qui donne encore
     des points, ses couleurs (orange/jaune/verte/grise), le nombre de fabrications estimé, les
     composants (en sacs, marchand avec prix et `/way`, à fabriquer, à récolter), le patron à acheter,
     la revente marchand du produit, puis deux listes : **à fabriquer en route** (intermédiaires du
     même métier) et **à acheter ou récolter** (matières brutes, quantités totales) ;
   - pour un **métier de récolte** (Herboristerie, Minage, Dépeçage, Pêche) : pas de parcours de
     recettes mais les règles de montée [Classic] (rang requis par nœud, niveau max des bêtes
     dépeçables, zones proches), le palier suivant et les formateurs ;
   - les recettes capturées en jeu qui donnent encore des points (couleurs exactes du jeu).
   `rang_min`/`rang_max` : liste brute des recettes d'une tranche.
2. Objet fabriqué ou composant : `item`. Ce que l'outil ne sait pas (spécialisations, quêtes de
   métier, rentabilité à l'hôtel des ventes) : `search`, puis le web
   (`WoW Forever <métier> leveling guide`), puis `save_knowledge`.

## Règles

- **Avant de conseiller une formation** (« va prendre Expert / Artisan »), vérifie dans la sortie
  la compétence requise du palier suivant et le niveau : si elle n'est pas atteinte, dis-le avec les
  chiffres (« pas encore : 106/125, encore 19 points ») et donne d'abord le parcours jusqu'au seuil.
  Ne jamais dire « tout de suite » sans que la compétence et le niveau soient OK.
- Le palier en cours plafonne la compétence (75, 150, 225) : signale chaque passage chez le
  formateur indiqué dans le parcours (« à 150 : formateur, palier Expert »).
- Rang requis : sans « ≈ » = lu dans les fichiers du client (recette, patron, objet fabriqué) ;
  « ≈ » = estimation. Couleurs sans « ≈ » = valeurs [Classic] de la recette ; « ≈ » = estimation
  prudente. Le parcours ne propose jamais de recette grise et privilégie orange/jaune ; le nombre de
  fabrications est l'espérance de points (formule Classic). Le dire, et proposer d'ouvrir la fenêtre
  du métier en jeu puis Ctrl+Maj+S pour les couleurs exactes.
- Si le verdict dit « tu as déjà 2 métiers principaux », le dire **en premier** (il faut en oublier
  un) ; Cuisine, Secourisme et Pêche sont secondaires, le Dépeçage est principal.
- Prix : seuls les prix **marchands** existent (achat chez un PNJ, revente au marchand). Aucun prix
  d'hôtel des ventes n'est connu : ne jamais en inventer ; dire « à récolter ou acheter à l'HV ».
- Source d'une recette : « formateur [Classic] » est une supposition (pas de patron connu) ;
  « patron vendu par un marchand » et « patron (butin…) » viennent des fichiers du client et de QuestieDB.

## Réponse

Verdict (la prochaine étape, avec la condition de palier) ; compétence actuelle et palier ; parcours
résumé (2 à 4 tranches : recette, de N à M, nombre de fabrications, composants et où les acheter) ;
formateur le plus proche avec `/way` ; ce qui reste incertain.
