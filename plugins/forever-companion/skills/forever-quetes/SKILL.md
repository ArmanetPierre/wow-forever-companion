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
2. Si la quête n'est pas dans le journal ou s'il manque une info (donneur, récompense,
   astuce) : cherche dans `${CLAUDE_PLUGIN_ROOT}/knowledge/forever-essentiels.md`, puis sur les sources de
   `${CLAUDE_PLUGIN_ROOT}/knowledge/sources.md` — requêtes `"<nom de la quête>" WoW Forever`,
   `site:wowhead.com/forever "<nom>"`, puis le nom anglais si tu le trouves.
3. Une quête de Classic peut avoir changé dans Forever (zones refaites) : badge et certitude.
4. Pour la récompense, croise avec `get_equipment` (est-ce une amélioration ?).

## Réponse

Gabarit **Quête** de `${CLAUDE_PLUGIN_ROOT}/knowledge/format-reponse.md` : verdict, journal plein en premier si c'est le cas, étapes avec
`/way`, prérequis/suite, récompense conseillée pour la classe.
