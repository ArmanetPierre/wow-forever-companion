---
name: forever-equipement
description: Aide sur l'équipement dans WoW Forever : comparer un objet à celui porté (« je prends ? »), trouver les emplacements faibles à améliorer, choisir une récompense de quête, quoi garder, vendre ou mettre en banque, sacs pleins, réparations, munitions. À utiliser dès que le joueur cite un objet, ses stats, un loot, une récompense, ses sacs ou demande comment s'améliorer.
---

# Équipement

## Méthode

1. **Outils MCP `forever`** :
   - `compare_item` pour tout objet proposé (stats données par le joueur ou `itemId`) : il
     renvoie le DPS effectif et les alertes (compétence d'arme, stats perdues).
   - `get_equipment` : objets portés, ilvl, stats, durabilité, coût de réparation.
   - `get_inventory` : sacs, places libres, munitions, banque si capturée.
   - `get_stats` pour expliquer un calcul.
2. **Calculs** : `${CLAUDE_PLUGIN_ROOT}/knowledge/formules.md` (14 PA = 1 DPS confirmé ; conversions Agi/For par
   classe ; compétence d'arme). Le crit et les effets « Chance quand vous touchez » ne sont
   pas chiffrés : mentionne-les.
3. **Améliorations** : repère les emplacements à ilvl le plus bas ou sans stat utile pour la
   classe, puis cherche des objets accessibles au niveau du perso (récompenses de quêtes en
   cours, donjons de son niveau) — `site:wowhead.com/forever <emplacement> <niveau>`.
4. **Sacs pleins** : propose quoi vendre (gris, objets inférieurs à l'équipé), quoi garder
   (composants de ses métiers via `get_professions`), et rappelle les munitions.

## Réponse

Gabarit **Comparaison d'objets** ou **Économie / sacs** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md`.
