---
id: donjon-preparation
question: « Je veux faire le donjon de la zone, je dois préparer quoi ? »
contexte: Brannok, Chasseur 25 ; base synthétique (« Donjon d'essai », quêtes et butin)
outils-attendus: [get_dungeon_loot]
outils-interdits: [sous-agent forever-guide]
budget: { appels: 2, appels-web: 1, tokens: 15000, duree: 40s }
mesure-v0.5: { appels: 5, appels-web: 2, sortie-outils: 845, redondance: 4% }
---

## Préparation

- Bac à sable de `mesure.py` (`args_bac_a_sable` : « Donjon d'essai »).

## Critères de réussite

- [ ] Niveau conseillé du donjon comparé au niveau du perso, avec le risque.
- [ ] Quêtes **déjà dans le journal** pour ce donjon citées, et quêtes à prendre avant.
- [ ] Butin **utile pour ce perso** (comparé à l'équipé), pas toute la table de butin.
- [ ] Préparation concrète : munitions, nourriture du familier, place dans les sacs.
- [ ] Une seule recherche web au plus (mécaniques des boss), après `search_knowledge`.

## Erreurs interdites

- Appeler séparément get_overview, get_equipment et get_quests quand un appel d'intention
  (`get_dungeon_loot` enrichi ou futur `prepare_dungeon`) suffit.
- Affirmer une mécanique de boss Forever sans source.

## Notes

v0.5 : 5 appels + 2 web. Dépend du loot des donjons (export du Journal des donjons,
lot B restant) et des quêtes de donjon dans la base locale.
