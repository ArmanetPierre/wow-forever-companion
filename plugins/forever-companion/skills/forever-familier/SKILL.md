---
name: forever-familier
description: Aide sur le familier du chasseur dans WoW Forever : bonheur, loyauté, nourriture, niveau et XP du familier, points de dressage, capacités et talents à apprendre, apprivoiser une nouvelle bête, écurie. À utiliser dès que le joueur parle de son familier, de son pet, de le nourrir, de l'apprivoisement ou des compétences de bête.
---

# Familier

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
