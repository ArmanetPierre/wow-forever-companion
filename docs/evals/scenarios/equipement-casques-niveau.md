---
id: equipement-casques-niveau
question: « Mais est-ce qu'il y a des armures de tête pour mon niveau ? »
contexte: Brannok, Nain Chasseur 25, Alliance, EU PvP ; mémoire de recherche préparée avec la note « Casques en cuir niveau 20-30 (Alliance) »
outils-attendus: [gear]   # v0.5 : [search_knowledge, get_quest_rewards]
outils-interdits: [sous-agent forever-guide, WebFetch, WebSearch]
budget: { appels: 4, appels-web: 0, tokens: 15000, duree: 30s }
mesure-v0.8: { appels: 1, sortie-outils: 557, redondance: 0%, verdict: oui }
---

## Préparation

Créer la note dans la mémoire de test (`FOREVER_KNOWLEDGE_DIR`) avec `save_knowledge` :

- sujet : « Casques en cuir niveau 20-30 (Alliance) »
- certitude : « probable [Classic, à confirmer dans Forever] »
- contenu : quasiment rien avant 30-35 ; **Heaume d'Humbert** (cuir, niv. 25, +7 Agi +8 End,
  rare, butin des Fusiliers de Dun Garok, Contreforts de Hautebrande, mobs ~30-34 en
  Classic) ; maille impossible avant 40 pour un chasseur ; pas de casque en cuir craftable
  avant ~220 ; aucun casque dans Excavations : les Paluns.

## Critères de réussite

- [ ] Première ligne : verdict en gras ; un badge de source ; aucune tournure de la liste noire
      (`python3 docs/evals/verifie_reponse.py <réponse.md>`).
- [ ] `search_knowledge` est appelé avant tout appel web, et la réponse s'appuie sur la note.
- [ ] `get_quest_rewards` (ou `get_quests`) vérifie qu'aucune quête du journal ne donne de
      casque.
- [ ] Verdict : **pas de casque utile avant ~30-35, sauf le Heaume d'Humbert**, nommé avec
      sa source et son lieu.
- [ ] Risques signalés : mobs ~30-34 (perso 25), zone contestée sur un royaume PvP.
- [ ] La certitude « probable [Classic, à confirmer dans Forever] » est reprise.
- [ ] Au plus 4 appels d'outils au total, aucun appel web.

## Erreurs interdites

- Relancer une recherche web ou un sous-agent alors que la note répond.
- Présenter la note comme sûre pour Forever.
- Proposer un casque en maille.

## Notes

Même question que le retour de session d'origine, qui avait coûté 21 appels d'outils,
~107 k tokens et ~2 min 25 via le sous-agent. Variante : mémoire vide → la réponse peut
utiliser ≤ 8 appels web via le sous-agent, avec budget annoncé, puis doit appeler
`save_knowledge`.
