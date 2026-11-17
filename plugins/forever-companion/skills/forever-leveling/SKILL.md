---
name: forever-leveling
description: Conseille quoi faire ensuite pour progresser dans WoW Forever selon le niveau, l'XP restante, la zone, les quêtes en cours et les objectifs du joueur (quêtes à rendre, prochaine zone, donjons, entraînement de classe, montures). À utiliser pour « je fais quoi maintenant ? », « où aller au niveau X ? », « comment monter plus vite ? ».
---

# Leveling

## Méthode

1. **Outils MCP `forever`** : `get_overview` (niveau, XP restante, zone, quêtes à rendre et
   améliorations à gagner, en un appel), puis `get_quests` (quêtes jaunes/oranges, journal
   plein), `get_progress` (rythme récent). Puis `objectifs.md` du joueur (rush, exploration, amis, or…).
2. **Base locale du jeu** `[Forever · base locale]` : `get_overview` y ajoute des pistes
   d'amélioration ; `find_upgrades` pour le détail, `get_dungeon_loot` pour les boss d'un
   donjon envisagé, `find_recipes` pour un palier de métier à caser dans la session.
3. **Cherche** : `search_knowledge`, puis `${CLAUDE_PLUGIN_ROOT}/knowledge/forever-essentiels.md` (fourchettes de niveau des zones et donjons,
   capacités de classe par niveau), puis les guides de leveling Forever de
   `${CLAUDE_PLUGIN_ROOT}/knowledge/sources.md` — `WoW Forever leveling guide <faction> <niveau>`,
   `WoW Forever <classe> leveling`.
4. Forever a des zones nouvelles ou refaites : ne recopie pas un itinéraire Classic sans badge.
5. Ruleset Hardcore : signale les quêtes et zones dangereuses (quêtes rouges, élites).

## Réponse

Gabarit **« Je fais quoi maintenant ? »** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md` : verdict, *Maintenant* / *Ensuite* /
*À prévoir* (entraînement au prochain niveau, donjon adapté, palier de métier), un piège.
