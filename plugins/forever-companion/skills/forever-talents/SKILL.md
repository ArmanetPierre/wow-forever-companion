---
name: forever-talents
description: Conseille une spécialisation, un arbre de talents ou un build pour la classe du joueur dans WoW Forever (leveling, donjons, PvP, solo, Hardcore) à partir de ses talents actuels : prochains points, ordre, rotation de base. À utiliser pour « quels talents ? », « quelle spé ? », « build <classe> », « ma rotation », « j'ai un point de talent ». EN: Recommends a spec, talent tree or build for the player's class in WoW Forever (leveling, dungeons, PvP, solo, Hardcore) from their current talents: next points, order, basic rotation. Use for "which talents?", "which spec?", "<class> build", "my rotation", "I have a talent point".
---

# Talents et spécialisation

> **Langue / Language.** Réponds dans la langue de la question du joueur (français ou anglais) et passe `lang` (`fr`/`en`) aux outils `forever`. Les noms du jeu (objets, quêtes, zones, PNJ) restent tels que le client les affiche. *Answer in the language of the player's question and pass `lang` to the `forever` tools; game names stay as the client shows them.*

## Méthode

1. **Outils MCP `forever`** : `get_talents` (spé, talents pris et rangs, points libres),
   `get_spells` (sorts et rangs connus, pour la rotation), `get_character` (niveau, rôle).
   Puis `objectifs.md` (leveling, donjons, PvP).
2. **Cherche** : `${CLAUDE_PLUGIN_ROOT}/knowledge/forever-essentiels.md` (talents refaits dans Forever, jalons à
   11/16/21/31 points, section de la classe), puis les guides de classe Forever de
   `${CLAUDE_PLUGIN_ROOT}/knowledge/sources.md` — `WoW Forever <classe> <spé> talents leveling`.
3. Recoupe deux sources ; si elles divergent, présente les deux options et leur logique.
   Les arbres de Forever diffèrent de Classic : pas de build Classic sans badge.

## Réponse

Gabarit **Build / talents** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md` : verdict (prochain point ou spé), talents actuels vs
conseillés, ordre des prochains points, rotation en 3 étapes max.
