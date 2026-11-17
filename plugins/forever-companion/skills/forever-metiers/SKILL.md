---
name: forever-metiers
description: Aide sur les métiers de WoW Forever : où en est le joueur, comment monter la compétence, quel formateur et quel rang suivant, quelles recettes rapportent des points, composants à récolter, rentabilité, choix de métiers pour une classe. À utiliser dès que le joueur parle de récolte, d'artisanat, de recettes, de cuisine, de pêche, de secourisme, de campement ou d'or gagné avec un métier.
---

# Métiers

## Méthode

1. **`get_professions`** (outil MCP `forever`) : métiers, compétence actuelle et plafond,
   recettes connues si elles ont été capturées. Recettes « jamais capturées » : demande au
   joueur d'ouvrir la fenêtre du métier puis Ctrl+Maj+S. `get_inventory` pour les composants
   déjà en sacs ou en banque.
2. **Cherche** : `${CLAUDE_PLUGIN_ROOT}/knowledge/forever-essentiels.md` (métiers, campements), puis
   `${CLAUDE_PLUGIN_ROOT}/knowledge/sources.md` — `WoW Forever <métier> leveling guide`, `WoW Forever <métier> trainer`.
   Vérifie que paliers et plafonds sont ceux de Forever.
3. Donne des paliers concrets (fabriquer X jusqu'à N) en partant de la compétence réelle et
   des recettes connues.

## Réponse

Gabarit **Métier** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md` : verdict, compétence actuelle, palier suivant (quoi, composants,
où), formateur et prérequis.
