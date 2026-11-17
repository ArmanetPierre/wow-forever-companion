---
name: forever-donjons
description: Prépare le joueur à un donjon ou raid de WoW Forever, y compris les 9 nouveaux donjons propres à Forever (Hall of Thanes, Excavations : les Paluns, Drowned City, Blackmaw Hold…) et les raids qui ouvrent le 9 décembre 2026 : niveau conseillé, accès, quêtes à prendre avant, boss et mécaniques, rôle du joueur, loot intéressant pour sa classe. À utiliser quand le joueur cite un donjon, un boss, ou demande quel donjon faire.
---

# Donjons et raids

## Méthode

1. **Outils MCP `forever`** : `get_character` (niveau, rôle, ruleset), `get_equipment`
   (emplacements à améliorer), `get_quests` filtré sur le nom du donjon (quêtes `[Donjon]`
   déjà dans le journal).
2. **Cherche** : `${CLAUDE_PLUGIN_ROOT}/knowledge/forever-essentiels.md` (liste des donjons et niveaux), puis
   `${CLAUDE_PLUGIN_ROOT}/knowledge/sources.md` — `WoW Forever <donjon> guide`, `site:wowhead.com/forever <donjon>`,
   `WoW Forever <donjon> loot <classe>`.
3. Les nouveaux donjons sont propres à Forever : aucune info Classic pour eux. Pour un donjon
   d'origine, vérifie s'il a été modifié.

## Réponse

Gabarit **Donjon** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md` : verdict (y aller ou pas), niveau conseillé vs niveau du perso,
quêtes à prendre avant, 2-3 boss avec ce que le joueur doit faire, loot qui améliore son
équipement actuel.
