---
id: quetes-a-rendre
question: « Quelles quêtes je peux rendre, et lesquelles donnent un truc utile ? »
contexte: Brannok, Nain Chasseur 25 (fixtures de l'addon 1.2, récompenses capturées)
outils-attendus: [quests a_rendre]   # v0.5 : [get_quest_rewards]
outils-interdits: [sous-agent forever-guide, recherche web]
budget: { appels: 1, appels-web: 0, tokens: 8000, duree: 20s }
mesure-v0.5: { appels: 2, appels-web: 0, sortie-outils: 496, redondance: 4% }
mesure-v0.8: { appels: 1, sortie-outils: 527, redondance: 0%, verdict: oui }
---

## Préparation

- Fixtures : « Purger la contrée » terminée, récompense au choix *Arc des marais*,
  *Robe du marin*, *Gants de pisteur*.

## Critères de réussite

- [ ] Première ligne : verdict en gras ; un badge de source ; aucune tournure de la liste noire
      (`python3 docs/evals/verifie_reponse.py <réponse.md>`).
- [ ] **1 appel** : `get_quest_rewards` (filtre « à rendre ») suffit ; il porte déjà le `/way`.
- [ ] Les quêtes sont groupées par lieu de rendu, du plus proche au plus loin.
- [ ] Pour chaque quête à choix, la meilleure récompense **pour ce perso** est désignée,
      avec le gain chiffré (ex. Arc des marais ≈ +1,4 DPS).
- [ ] Les récompenses inutilisables (tissu pour un chasseur) sont signalées « à vendre ».

## Erreurs interdites

- Appeler `get_quests` puis `get_quest_rewards` (doublon de la liste).
- Recommander une récompense sans la comparer à l'équipé.

## Notes

Cas le plus simple : sert de témoin. S'il dépasse 1 appel, le routage de l'agent est en cause.
