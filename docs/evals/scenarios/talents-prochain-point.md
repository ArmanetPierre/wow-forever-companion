---
id: talents-prochain-point
question: « J'ai un point de talent, je le mets où ? »
contexte: Brannok, Chasseur 25, talents des fixtures
outils-attendus: [get_talents]
outils-interdits: [sous-agent forever-guide]
budget: { appels: 2, appels-web: 1, tokens: 15000, duree: 40s }
mesure-v0.5: { appels: 3, appels-web: 2, sortie-outils: 490, redondance: 7% }
---

## Préparation

- Bac à sable de `mesure.py`. La base locale n'a pas encore les arbres de talents
  (dépend de l'extraction des tables de talents) : 1 appel web reste toléré.

## Critères de réussite

- [ ] Les talents actuels sont lus (`get_talents`) avant tout conseil.
- [ ] Un seul choix recommandé, avec la raison (leveling solo, chasseur) et l'alternative.
- [ ] `search_knowledge` est consulté avant le web ; la trouvaille web est enregistrée
      (`save_knowledge`) pour que la même question coûte 0 web la fois suivante.
- [ ] Badge de source : [Forever] si confirmé dans le jeu, sinon [Classic, à confirmer].

## Erreurs interdites

- Proposer un talent déjà au maximum ou un talent dont le prérequis manque.
- Appeler `get_character` et `get_spells` sans besoin (la classe et le niveau sont dans l'en-tête).

## Notes

Une fois les arbres de talents dans la base locale : budget cible 1 appel, 0 web.
