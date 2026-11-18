---
id: leveling-quoi-faire
question: « Je fais quoi maintenant ? »
contexte: Brannok, Nain Chasseur 25, Alliance, EU PvP, Les Paluns (fixtures de l'addon 1.2) ; base synthétique
outils-attendus: [overview]   # v0.5 : [get_overview]
outils-interdits: [sous-agent forever-guide, get_character, get_equipment, get_stats]
budget: { appels: 2, appels-web: 0, tokens: 12000, duree: 30s }
mesure-v0.5: { appels: 5, appels-web: 1, sortie-outils: 1150, redondance: 13% }
mesure-v0.8: { appels: 1, sortie-outils: 1204, redondance: 0%, verdict: oui }
---

## Préparation

- Bac à sable de `mesure.py` (fixtures + base synthétique), mémoire de recherche vide.
- Le perso a des quêtes à rendre et un journal partiellement rempli.

## Critères de réussite

- [ ] Première ligne : verdict en gras ; un badge de source ; aucune tournure de la liste noire
      (`python3 docs/evals/verifie_reponse.py <réponse.md>`).
- [ ] Un seul `ToolSearch` (requête `+forever`) en début de session, pas un par question.
- [ ] La réponse tient en **1 appel** (`get_overview`, ou le futur `what_next`) ; 2 au plus
      si le joueur précise une zone.
- [ ] Les 3 premières actions proposées sont concrètes et ordonnées : quêtes à rendre (avec
      `/way`), quêtes du niveau dans la zone actuelle, prochaine étape (zone, donjon, formateur).
- [ ] Le reste d'XP avant le niveau suivant est cité, avec le repos.
- [ ] Aucune recherche web si la réponse est couverte par les données locales.

## Erreurs interdites

- Appeler `get_quests` **et** `get_overview` pour relire les mêmes quêtes à rendre.
- Lister toutes les quêtes du journal au lieu de prioriser.
- Proposer une zone ou un donjon hors de portée (rouge) sans prévenir du risque.

## Notes

Séquence v0.5 mesurée : get_overview, get_quests, get_progress, find_upgrades,
search_knowledge (5 appels, 13 % de lignes redondantes). Cible : un résumé « quoi faire »
précalculé à la synchro, servi par `get_overview` ou un outil d'intention.
