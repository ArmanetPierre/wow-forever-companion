---
name: forever-familier
description: Familier du chasseur dans WoW Forever : bonheur, loyauté, nourriture, niveau, points de dressage, capacités à apprendre, apprivoisement, écurie. À utiliser dès que le joueur parle de son familier ou de le nourrir. EN: WoW Forever hunter pet: happiness, loyalty, food, level, training points, abilities, taming, stable. Use whenever the player talks about their pet.
---

# Familier

> Réponds dans la langue de la question et passe `lang` (`fr`/`en`) ; les noms du jeu restent ceux du client. Forme et voix : instructions du serveur `forever` (verdict en gras d'abord, badge de source).

## Appels (budget : 1 outil, 0 à 2 web)

1. `pet` : famille, niveau vs perso, XP, bonheur et bonus de dégâts, loyauté, régime,
   **nourriture trouvée dans les sacs**, points de dressage, capacités.
2. Capacité ou bête à apprivoiser : `search`, puis le web (`WoW Forever hunter pet <famille>
   abilities`), puis `save_knowledge`. Le système de familier de Forever a sa propre API : ne
   pas supposer qu'il est identique à Classic.

## Réponse

Verdict (il va bien ou pas, l'action) ; état ; quoi lui donner (nourriture des sacs nommée,
jamais un objet gardé pour une quête) ;
quoi apprendre et où. Familier en retard de niveau : le garder actif sur des mobs de son niveau.
