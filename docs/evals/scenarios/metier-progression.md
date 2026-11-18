---
id: metier-progression
question: « Comment je monte mon travail du cuir ? »
contexte: Brannok, Travail du cuir dans les fixtures ; base synthétique (recettes)
outils-attendus: [professions]   # v0.5 : [get_professions, find_recipes]
outils-interdits: [sous-agent forever-guide]
budget: { appels: 2, appels-web: 0, tokens: 12000, duree: 30s }
mesure-v0.5: { appels: 3, appels-web: 1, sortie-outils: 439, redondance: 4% }
mesure-v0.8: { appels: 1, sortie-outils: 713, redondance: 0%, verdict: oui }
---

## Préparation

- Bac à sable de `mesure.py`, mémoire de recherche vide.

## Critères de réussite

- [ ] Première ligne : verdict en gras ; un badge de source ; aucune tournure de la liste noire
      (`python3 docs/evals/verifie_reponse.py <réponse.md>`).
- [ ] Rang et compétence actuels cités (`get_professions`, ou le résumé du perso).
- [ ] Les recettes proposées sont **celles qui donnent encore des points** à la compétence
      actuelle (couleur orange/jaune), triées par coût en composants.
- [ ] Les composants manquants sont croisés avec les sacs (au plus 1 appel de plus, ou
      directement dans la réponse de `find_recipes` dans la version cible).
- [ ] Le prochain palier de formateur est indiqué (compétence max du rang).
- [ ] Aucune recherche web pour les recettes présentes dans la base locale.

## Erreurs interdites

- Proposer des recettes grises (plus de points) ou non apprises sans dire où les apprendre.
- Recopier toute la liste des recettes connues.

## Notes

v0.5 : get_professions, find_recipes, get_inventory (+1 web pour les formateurs).
Cible : `find_recipes` filtre « qui rapporte des points » et croise les sacs.
