---
name: forever-metiers
description: Aide sur les métiers de WoW Forever : où en est le joueur, comment monter la compétence, quel formateur et quel rang suivant, quelles recettes rapportent des points, composants à récolter, rentabilité, choix de métiers pour une classe. À utiliser dès que le joueur parle de récolte, d'artisanat, de recettes, de cuisine, de pêche, de secourisme, de campement ou d'or gagné avec un métier. EN: WoW Forever professions help: current skill, how to level it, which trainer and next rank, recipes that give points, materials to gather, profitability, profession choice for a class. Use whenever the player talks about gathering, crafting, recipes, cooking, fishing, first aid, camping or gold from a profession.
---

# Métiers

> **Langue / Language.** Réponds dans la langue de la question du joueur (français ou anglais) et passe `lang` (`fr`/`en`) aux outils `forever`. Les noms du jeu (objets, quêtes, zones, PNJ) restent tels que le client les affiche. *Answer in the language of the player's question and pass `lang` to the `forever` tools; game names stay as the client shows them.*

## Méthode

1. **`get_professions`** (outil MCP `forever`) : métiers, compétence actuelle et plafond,
   recettes connues si elles ont été capturées. Recettes « jamais capturées » : demande au
   joueur d'ouvrir la fenêtre du métier puis Ctrl+Maj+S. `get_inventory` pour les composants
   déjà en sacs ou en banque.
2. **Base locale du jeu** `[Forever · base locale]` : `find_recipes` (par défaut le métier
   principal du perso, autour de son rang) donne les recettes, l'objet fabriqué avec ses stats
   et les composants ; `get_item` dit aussi quelle recette fabrique un objet et dans quelles
   recettes un composant sert. Le rang requis est **estimé** (« ≈ », 5 × niveau de l'objet) et
   la source des recettes (formateur, marchand, butin) n'y est pas : dis-le, et confirme le
   palier avec la fenêtre du métier ou une source.
3. **Cherche** : `${CLAUDE_PLUGIN_ROOT}/knowledge/forever-essentiels.md` (métiers, campements), puis
   `${CLAUDE_PLUGIN_ROOT}/knowledge/sources.md` — `WoW Forever <métier> leveling guide`, `WoW Forever <métier> trainer`.
   Vérifie que paliers et plafonds sont ceux de Forever.
4. Donne des paliers concrets (fabriquer X jusqu'à N) en partant de la compétence réelle et
   des recettes connues.

## Réponse

Gabarit **Métier** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md` : verdict, compétence actuelle, palier suivant (quoi, composants,
où), formateur et prérequis.
