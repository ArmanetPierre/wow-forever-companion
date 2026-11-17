---
name: forever-quetes
description: Aide sur une ou plusieurs quêtes de WoW Forever : où la prendre ou la rendre, quoi faire, où trouver les objectifs (/way), prérequis, chaîne, récompenses, quêtes à rendre, journal plein. À utiliser quand le joueur cite une quête, un PNJ donneur de quête, un objectif bloquant (« je trouve pas… », « où est… ») ou demande quelles quêtes rendre ou faire dans une zone. EN: Help with one or more WoW Forever quests: where to pick up or turn in, what to do, where the objectives are (/way), prerequisites, chain, rewards, quests ready to turn in, full quest log. Use when the player names a quest, a quest giver, a blocking objective ("I can't find…", "where is…") or asks which quests to turn in or do in a zone.
---

# Quêtes

> **Langue / Language.** Réponds dans la langue de la question du joueur (français ou anglais) et passe `lang` (`fr`/`en`) aux outils `forever`. Les noms du jeu (objets, quêtes, zones, PNJ) restent tels que le client les affiche. *Answer in the language of the player's question and pass `lang` to the `forever` tools; game names stay as the client shows them.*

## Méthode

1. **`get_quests`** (outil MCP `forever`) en premier : filtre `zone` ou un mot du titre. Tu
   obtiens niveau, couleur de difficulté, objectifs et progression, `/way`, quêtes à rendre
   et si le journal est plein. Données de plus de 30 min et question sur la progression :
   rappelle Ctrl+Maj+S (voir la charte).
2. **Base locale avant le web** `[Forever · QuestieDB]` :
   - une quête précise (donneur, receveur, objectifs et où les trouver, `/way`, prérequis,
     suite, statut pour le perso) : **`get_quest_info`** (id ou titre, français ou anglais) ;
   - « quelles quêtes ici / à mon niveau ? » : **`find_quests`** (zone actuelle par défaut ;
     race, classe, prérequis vérifiés, quêtes faites ou dans le journal retirées) ;
   - « où est tel PNJ / monstre / objet ? » : **`find_npc`** ;
   - les objets cités se lisent avec `get_item`.
   Si la quête est absente de QuestieDB (couverture partielle des quêtes ajoutées par
   Forever) : `search_knowledge`, puis `${CLAUDE_PLUGIN_ROOT}/knowledge/forever-essentiels.md`,
   puis les sources de `${CLAUDE_PLUGIN_ROOT}/knowledge/sources.md` — requêtes
   `"<nom de la quête>" WoW Forever`, `site:wowhead.com/forever "<nom>"`, puis le nom anglais
   (donné par `get_quest_info` : « Titre anglais »). Si l'outil dit que QuestieDB n'est pas
   importé, donne au joueur la commande affichée (une fois, quelques secondes).
3. Une quête de Classic peut avoir changé dans Forever (zones refaites) : QuestieDB suit Forever
   mais reste communautaire ; si le joueur dit qu'un détail ne colle pas, crois le jeu.
4. Pour la récompense : `get_quests` affiche déjà la récompense conseillée sous chaque quête ;
   `get_quest_rewards` (filtre `zone`, `a_rendre`) classe tous les objets au choix pour ce
   perso (maîtrise d'armure/arme, gain estimé) et signale les quêtes à rendre qui donnent
   une amélioration. N'ajoute une recherche web que si les récompenses ne sont pas
   capturées (addon antérieur à 1.2).
5. Signale les risques : quête de groupe ou élite, mobs plus hauts que le perso, zone
   contestée sur un royaume PvP.

## Réponse

Gabarit **Quête** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md` : verdict, journal plein en premier si c'est le cas, étapes avec
`/way`, prérequis/suite, récompense conseillée pour la classe.
