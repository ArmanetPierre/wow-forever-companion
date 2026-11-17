---
name: forever-familier
description: Aide sur le familier du chasseur dans WoW Forever : bonheur, loyauté, nourriture, niveau et XP du familier, points de dressage, capacités et talents à apprendre, apprivoiser une nouvelle bête, écurie. À utiliser dès que le joueur parle de son familier, de son pet, de le nourrir, de l'apprivoisement ou des compétences de bête. EN: Hunter pet help in WoW Forever: happiness, loyalty, food, pet level and XP, training points, abilities to learn, taming a new beast, stable. Use whenever the player talks about their pet, feeding it, taming or beast abilities.
---

# Familier

> **Langue / Language.** Réponds dans la langue de la question du joueur (français ou anglais) et passe `lang` (`fr`/`en`) aux outils `forever`. Les noms du jeu (objets, quêtes, zones, PNJ) restent tels que le client les affiche. *Answer in the language of the player's question and pass `lang` to the `forever` tools; game names stay as the client shows them.*

## Méthode

1. **`get_pet`** (outil MCP `forever`) : famille, niveau vs niveau du perso, XP, bonheur et
   bonus de dégâts, loyauté, nourriture acceptée, points de dressage libres, capacités.
   `get_inventory` pour vérifier qu'il y a de quoi le nourrir dans les sacs.
2. **Cherche** : `${CLAUDE_PLUGIN_ROOT}/knowledge/forever-essentiels.md` (section Chasseur), puis `${CLAUDE_PLUGIN_ROOT}/knowledge/sources.md` —
   `WoW Forever hunter pet <famille> abilities`, `WoW Forever pet training points`,
   `WoW Forever tame <bête>`. Le système de familier de Forever a une API dédiée (bonheur,
   loyauté, points de dressage, arbre de talents de familier) : ne suppose pas qu'il est
   identique à Classic.
3. Familier en retard de niveau : conseille de le garder actif sur des monstres de son niveau.

## Réponse

Gabarit **Familier** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md` : verdict, état, action (nourrir avec quoi, quoi apprendre et où).
