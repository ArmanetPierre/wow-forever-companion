---
name: forever-leveling
description: Quoi faire ensuite pour progresser dans WoW Forever : quêtes à rendre, quêtes à prendre, prochaine zone, donjon, entraînement de classe, selon le niveau, l'XP, la zone et les objectifs. À utiliser pour « je fais quoi maintenant ? », « où aller au niveau X ? ». EN: What to do next in WoW Forever: turn-ins, quests to pick up, next zone, dungeon, class training. Use for "what should I do now?", "where to go at level X?".
---

# Leveling

> Réponds dans la langue de la question et passe `lang` (`fr`/`en`) ; les noms du jeu restent ceux du client. Forme et voix : instructions du serveur `forever` (verdict en gras d'abord, badge de source).

## Appels (budget : 1 outil, 2 au plus)

1. `overview` : verdict et résumé calculé à la synchro (quêtes à rendre par zone avec la
   meilleure récompense, améliorations à portée, quêtes à prendre autour, XP restante, rappel
   du maître de classe, sacs, munitions, familier, métiers). Il répond seul la plupart du temps.
2. Si besoin d'un détail : `quests disponibles:true zone:<zone>` (autre zone) ou
   `dungeon donjon:<nom>` (donjon envisagé). `objectifs.md` du joueur s'il existe (rush, amis,
   or…).
3. Prochaine zone ou itinéraire : `search`, puis les guides de `sources.md` (`WoW Forever
   leveling guide <faction> <niveau>`). Zones nouvelles ou refaites : pas d'itinéraire Classic
   sans badge.

Carte : si le joueur demande où aller (« c'est où ? ») ou si l'étape suivante est un lieu à
trouver, `map zone:<zone>` avec les `/way` de cette étape (zone et rendu groupés sur une carte) ; pas
pour chaque réponse.

## Réponse

Verdict (la prochaine action) ; maintenant / ensuite / à prévoir ; un piège (journal plein,
mobs rouges). Hardcore : quêtes et zones dangereuses en premier.
