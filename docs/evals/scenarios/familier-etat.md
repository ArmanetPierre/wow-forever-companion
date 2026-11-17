---
id: familier-etat
question: « Mon familier va bien ? Je le nourris avec quoi ? »
contexte: Brannok, familier des fixtures
outils-attendus: [get_pet]
outils-interdits: [sous-agent forever-guide, recherche web]
budget: { appels: 1, appels-web: 0, tokens: 8000, duree: 20s }
mesure-v0.5: { appels: 2, appels-web: 0, sortie-outils: 253, redondance: 7% }
---

## Préparation

- Bac à sable de `mesure.py`.

## Critères de réussite

- [ ] Bonheur et régime lus avec `get_pet`. v0.5 : il faut `get_inventory` en plus pour la
      nourriture ; cible : **1 appel**, `get_pet` croise le régime avec les sacs.
- [ ] Conseil concret : quel objet des sacs donner, combien il en reste.
- [ ] Si aucune nourriture compatible : où en acheter (marchand le plus proche connu).

## Erreurs interdites

- Appeler `get_inventory` pour retrouver la nourriture si `get_pet` la croise déjà.
- Proposer une nourriture hors régime du familier.

## Notes

v0.5 : get_pet + get_inventory. Cible : croisement régime × sacs fait côté serveur.
