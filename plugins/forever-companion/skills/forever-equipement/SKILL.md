---
name: forever-equipement
description: Aide sur l'équipement dans WoW Forever : comparer un objet à celui porté (« je prends ? »), trouver les emplacements faibles à améliorer, choisir une récompense de quête, quoi garder, vendre ou mettre en banque, sacs pleins, réparations, munitions. À utiliser dès que le joueur cite un objet, ses stats, un loot, une récompense, ses sacs ou demande comment s'améliorer.
---

# Équipement

## Méthode (dans cet ordre, sans sauter d'étape)

1. **État du perso — toujours d'abord, avant le web** :
   - `get_overview` (ou `get_equipment` si la question porte sur un objet porté) : armes,
     ilvl, emplacements vides, quêtes à rendre.
   - `get_inventory` : un objet meilleur dort peut-être déjà dans les sacs ou à la banque.
   - `get_quest_rewards` : récompenses des quêtes du journal, classées pour ce perso, avec
     les quêtes à rendre qui donnent une amélioration. Ce sont les objets les plus sûrs.
2. **Base locale du jeu** `[Forever · base locale]` : `find_upgrades` (emplacement facultatif)
   liste les objets portables par le perso qui l'améliorent, avec stats exactes, armure, DPS
   et source quand elle est connue ; `get_item` pour la fiche d'un objet cité (stats, recette,
   verdict pour le perso) ; `find_items` pour une recherche libre. Un objet dont la source est
   « non répertoriée » n'est pas forcément obtenable : vérifie où il tombe (étape 3) avant de
   le conseiller. Si la base n'est pas construite, donne au joueur la commande renvoyée.
3. **Mémoire** : `search_knowledge` (ex. « casque cuir niveau 25 ») avant toute recherche web.
4. **Objet proposé** : `compare_item` (stats données par le joueur, ou `itemId` : la base locale
   fournit alors les stats) : DPS
   effectif et alertes (compétence d'arme, stats perdues). Calculs :
   `${CLAUDE_PLUGIN_ROOT}/knowledge/formules.md` (14 PA = 1 DPS confirmé ; conversions Agi/For
   par classe). Crit et effets « Chance quand vous touchez » ne sont pas chiffrés : mentionne-les.
5. **Améliorations ailleurs** (seulement si 1 à 3 ne suffisent pas, 2 ou 3 appels web) :
   donjons de son niveau, artisanat, hôtel des ventes —
   `site:wowhead.com/forever <emplacement> <niveau>`. Vérifie la maîtrise de la classe
   (chasseur : maille au niveau 40 [Classic · à vérifier en jeu]). Enregistre ce que tu
   trouves avec `save_knowledge`.
6. **Sacs pleins** : propose quoi vendre (gris, objets inférieurs à l'équipé), quoi garder
   (composants de ses métiers via `get_professions`), et rappelle les munitions.

## Règles

- **Vide ≠ faible.** À bas niveau, tête, cou, épaules, bijoux sont souvent vides : ne
  conseille pas de les remplir sans un objet précis disponible à ce niveau. Sinon :
  « rien de notable avant le niveau X ».
- **Chaque objet conseillé est nommé**, avec sa source (quête, boss, marchand, recette) et
  un `/way` ou un lieu.
- **Risques** : mobs plus hauts que le perso, zone PvP, quête ou donjon de groupe.

## Réponse

Gabarit **Comparaison d'objets**, **« Évalue mon stuff »** ou **Économie / sacs** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md`.
