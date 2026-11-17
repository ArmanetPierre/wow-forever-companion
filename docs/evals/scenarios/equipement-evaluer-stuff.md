---
id: equipement-evaluer-stuff
question: « Est-ce que tu peux évaluer mon stuff par rapport à mon niveau ? »
contexte: Brannok, Nain Chasseur 25, Alliance, EU PvP, Les Paluns (fixtures de l'addon 1.2, récompenses capturées)
outils-attendus: [get_overview, get_inventory, get_quest_rewards]
outils-interdits: [sous-agent forever-guide]
budget: { appels: 6, appels-web: 2, tokens: 40000, duree: 60s }
---

## Préparation

- Données des fixtures (`addon/tests/fixtures/`) : tête, cou, épaules, bijoux vides ;
  quête « Purger la contrée » terminée, avec au choix *Arc des marais* (arc 14,8 DPS, +2 Agi),
  *Robe du marin* (tissu), *Gants de pisteur* (cuir, +3 Agi +2 End).
- Mémoire de recherche vide.

## Critères de réussite

- [ ] Les outils `forever` sont chargés en un seul `ToolSearch` (requête `+forever`).
- [ ] `get_overview` (ou `get_equipment`), `get_inventory` et `get_quest_rewards` sont
      appelés **avant** tout appel web.
- [ ] Le verdict cite la récompense de quête à rendre : **Arc des marais** de *Purger la
      contrée*, avec le gain estimé (≈ +1,4 DPS) et le `/way` de rendu.
- [ ] Les gants de pisteur sont mentionnés comme option pour les mains vides (un seul choix
      possible : la réponse explique l'arbitrage).
- [ ] Les emplacements vides (tête, cou, épaules, bijoux) sont présentés comme **normaux à
      ce niveau**, sans conseil de les remplir faute d'objet précis.
- [ ] Chaque objet conseillé est nommé avec sa source.
- [ ] Format de la charte : en-tête, verdict en gras, pied « Basé sur ».

## Erreurs interdites

- Conseiller de « prendre n'importe quel casque » ou classer les emplacements vides en
  priorité sans objet précis.
- Affirmer qu'une arme est faible « pour ce niveau » sans chiffre ni référence.
- Recommander la maille (interdite au chasseur avant 40 [Classic]) ou une arme non maîtrisée.
- Ne citer que des catégories génériques (« un bon arc », « des bijoux »).
- Lancer le sous-agent `forever-guide` pour cette question.

## Notes

Tiré d'un retour de session réel (anonymisé) : la première version avait répondu de
mémoire, conseillé un casque inexistant et ignoré les récompenses des quêtes à rendre.
