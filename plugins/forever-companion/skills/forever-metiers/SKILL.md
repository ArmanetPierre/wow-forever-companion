---
name: forever-metiers
description: Métiers de WoW Forever : où en est le joueur, comment monter, formateur et rang suivant, recettes qui rapportent des points, composants, rentabilité, prix de l'hôtel des ventes, or gagné avec un métier, objets à fabriquer pour son perso. À utiliser dès que le joueur parle de récolte, d'artisanat, de recettes, de cuisine, de pêche, de secourisme, de campement, de vendre ou d'acheter à l'HV. EN: WoW Forever professions: skill, how to level, trainer and next rank, recipes that give points, reagents, profit, auction house prices, craftable gear. Use whenever the player talks about gathering, crafting, recipes or selling/buying at the AH.
---

# Métiers

> Réponds dans la langue de la question et passe `lang` (`fr`/`en`) ; les noms du jeu restent ceux du client. Forme et voix : instructions du serveur `forever` (verdict en gras d'abord, badge de source).

## Appels (budget : 1 à 2 outils, 0 à 2 web)

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
2. **Argent et hôtel des ventes** : `market` (`metier`, défaut Travail du cuir ; `vue` = `tout` |
   `monter` | `profit` | `equipement` | `sacs` ; `cible` ; `pour` = autre perso du compte à équiper).
   À utiliser pour « monter au moins cher », « qu'est-ce qui rapporte ? », « je vends ou je
   fabrique ? », « quoi me fabriquer ? », « que faire de mes peaux ? ». Il croise les prix HV relevés
   par l'addon (le joueur ouvre l'HV et cherche les objets ; l'addon note ce qui s'affiche), les prix
   marchands de la base locale et le stock des sacs/banque :
   - **monter au meilleur prix** : à chaque point la recette au plus faible coût net par point
     (composants au moins cher entre HV, marchand, fabrication ; gratuits s'ils sont en sacs ; moins
     la revente du produit = max(HV − 5 %, marchand)), liste d'achats avec prix et date du relevé,
     coût total net (pas de total net si un composant n'a aucun prix) ;
   - **rentabilité** : recettes connues ou apprenables, profit net de commission, marge, volume vu
     (« vu 40 en 6 annonces » ; « en vente, prix plancher » = vue de navigation, moins fiable) ;
     « vendre brut ou fabriquer ? » pour le cuir et les peaux en sacs ;
   - **équipement** : objets du métier qui améliorent le perso (ou `pour`), niveau, recette faisable
     ou à apprendre, coût des composants, prix HV de l'objet fini (« fabriquer ou acheter »),
     pièces d'ensemble ;
   - **sacs** : garder pour le parcours, fabriquer, vendre à l'HV ou au marchand.
   Sans relevé HV, il marche avec les prix marchands et termine par « À chercher à l'HV en
   priorité » : transmets cette courte liste au joueur.
3. Objet fabriqué ou composant : `item`. Ce que les outils ne savent pas (spécialisations, quêtes de
   métier) : `search`, puis le web (`WoW Forever <métier> leveling guide`), puis `save_knowledge`.

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
- Prix : `professions` ne donne que des prix **marchands** ; les prix d'hôtel des ventes viennent
  seulement de `market`, d'après les relevés du joueur. Ne jamais inventer un prix HV ni en
  présenter un comme sûr : toujours citer sa date (« [Forever · tes relevés HV du 24/11] ») et dire
  qu'il a pu bouger ; un prix marqué ⚠ (plus de 3 jours) est à revérifier à l'HV avant d'acheter ou
  de fabriquer en série. « Prix inconnu » = ni marchand ni relevé : à récolter ou à relever.
- Un profit élevé sur un petit volume (1 ou 2 annonces, prix plancher) ne se répète pas : signaler le
  nombre d'objets à écouler face au volume vu. Commission HV 5 % [Classic], dépôt non compté.
- Source d'une recette : « formateur [Classic] » est une supposition (pas de patron connu) ;
  « patron vendu par un marchand » et « patron (butin…) » viennent des fichiers du client et de QuestieDB.

## Réponse

Verdict (la prochaine étape, avec la condition de palier) ; compétence actuelle et palier ; parcours
résumé (2 à 4 tranches : recette, de N à M, nombre de fabrications, composants et où les acheter) ;
formateur le plus proche avec `/way` ; ce qui reste incertain.
Avec `market` : verdict chiffré (coût net de la montée, meilleure vente), date des prix, 3 à 5 lignes
utiles (achats, recettes rentables, quoi vendre), puis les objets à relever s'il en manque.
