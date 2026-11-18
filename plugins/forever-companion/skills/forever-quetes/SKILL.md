---
name: forever-quetes
description: Quêtes de WoW Forever : où la prendre ou la rendre, objectifs avec /way, prérequis, chaîne, récompenses, quêtes à rendre, quêtes du coin, journal plein. À utiliser quand le joueur cite une quête, un PNJ, un objectif introuvable (« je trouve pas… », « où est… ») ou demande quelles quêtes faire. EN: WoW Forever quests: pick-up and turn-in, objectives with /way, prerequisites, chain, rewards, quests nearby. Use when the player names a quest or NPC, or can't find an objective.
---

# Quêtes

> Réponds dans la langue de la question et passe `lang` (`fr`/`en`) ; les noms du jeu restent ceux du client. Forme et voix : instructions du serveur `forever` (verdict en gras d'abord, badge de source).

## Appels (budget : 1 outil, 2 au plus)

| Question | Appel |
|---|---|
| mes quêtes, quoi rendre | `quests` (verdict, à rendre, en cours) ; `a_rendre:true` pour les récompenses classées |
| une quête précise, « je trouve pas » | `quests quete:<titre>` (ou `questId`) : donneur, receveur, objectifs avec `/way`, prérequis, suite, statut |
| quêtes à prendre ici ou ailleurs | `quests disponibles:true` (`zone` facultatif) |
| où est un PNJ, un monstre, un objet | `npc nom:<nom>` |
| un nom flou | `search texte:<nom>` |
| « je trouve pas », « où c'est ? » (2e appel) | `map zone:<zone> points:["/way x y <nom>", …]` : carte de la zone, repères numérotés, le perso en bleu |

Sources de la fiche, de la plus sûre à la moins sûre : `[Forever · observé en jeu]` (l'addon a
vu le dialogue) > `[Forever · QuestieDB]` > `[Wowhead Forever]` > `[Forever · cache du client]`
(PNJ et lieux cités dans le texte : « probable », le dire). Sans donneur ni receveur connus :
`search`, puis le web (`"<nom>" WoW Forever`), puis `save_knowledge`. Si le joueur dit qu'un
détail ne colle pas, croire le jeu.

## Réponse

Verdict ; journal plein en premier s'il l'est ; problème connu (affiché par l'outil) avant les étapes ; étapes avec `/way` ; prérequis ou suite ;
récompense conseillée. Carte : seulement quand le joueur cherche un lieu (« je trouve pas », « où est »),
une par réponse et par zone, avec les `/way` de la réponse (9 au plus ; `zone` obligatoire avec des points, sinon l'outil refuse) ; donne le chemin du fichier. Pas de carte
pour un simple rendu de quête en ville ni si aucun `/way` n'est connu. Risques : groupe, élite, mobs plus hauts, zone contestée en JcJ.
