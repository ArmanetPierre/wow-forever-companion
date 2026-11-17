---
name: forever-quetes
description: Aide sur une ou plusieurs quêtes de WoW Forever : où la prendre ou la rendre, quoi faire, où trouver les objectifs (/way), prérequis, chaîne, récompenses, quêtes à rendre, journal plein. À utiliser quand le joueur cite une quête, un PNJ donneur de quête, un objectif bloquant (« je trouve pas… », « où est… ») ou demande quelles quêtes rendre ou faire dans une zone.
---

# Quêtes

## Méthode

1. **`get_quests`** (outil MCP `forever`) en premier : filtre `zone` ou un mot du titre. Tu
   obtiens niveau, couleur de difficulté, objectifs et progression, `/way`, quêtes à rendre
   et si le journal est plein. Données de plus de 30 min et question sur la progression :
   rappelle Ctrl+Maj+S (voir la charte).
2. Si la quête n'est pas dans le journal : `get_quest_info` (titre ou id) donne le titre et
   l'objectif des quêtes déjà vues par le client `[Forever · base locale]` ; les objets cités
   se lisent avec `get_item`. S'il manque une info (donneur, récompense, astuce) : cherche dans `${CLAUDE_PLUGIN_ROOT}/knowledge/forever-essentiels.md`, puis sur les sources de
   `${CLAUDE_PLUGIN_ROOT}/knowledge/sources.md` — requêtes `"<nom de la quête>" WoW Forever`,
   `site:wowhead.com/forever "<nom>"`, puis le nom anglais si tu le trouves.
3. Une quête de Classic peut avoir changé dans Forever (zones refaites) : badge et certitude.
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
