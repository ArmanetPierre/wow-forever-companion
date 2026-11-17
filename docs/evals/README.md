# Banc d'évaluation du compagnon

Des questions de joueur rejouables, avec ce qu'on attend de la réponse et ce qu'elle ne doit
jamais contenir. Le but : vérifier qu'un changement du plugin (agent, skills, outils MCP,
charte) rend le compagnon **plus juste, plus rapide et moins cher**, et pas l'inverse.

Tout est anonymisé : le perso d'exemple est **Brannok** (Nain Chasseur 25, Alliance, EU PvP,
Les Paluns), celui des fixtures de l'addon (`addon/tests/fixtures/`).

## Format d'un scénario

Un fichier Markdown par scénario dans `scenarios/`, avec un en-tête :

```yaml
---
id: equipement-evaluer-stuff          # identifiant stable
question: « Est-ce que tu peux évaluer mon stuff par rapport à mon niveau ? »
contexte: perso Brannok (fixtures), mémoire de recherche vide ou préparée (voir « Préparation »)
outils-attendus: [get_overview, get_inventory, get_quest_rewards]   # au moins ceux-là
outils-interdits: []                  # ex. un sous-agent pour une question simple
budget: { appels: 6, appels-web: 2, tokens: 40000, duree: 60s }
---
```

Puis quatre sections :

- **Préparation** : état à mettre en place (fixtures, note dans `connaissances/`, données
  plus ou moins fraîches).
- **Critères de réussite** : ce que la réponse doit contenir (verdict, objets nommés,
  sources, risques…), chacun vérifiable par oui/non.
- **Erreurs interdites** : ce qui fait échouer le scénario, même si le reste est bon.
- **Notes** : d'où vient le scénario (retour de session anonymisé), variantes.

## Rejouer un scénario

1. Construire un dossier de données de test à partir des fixtures (bac à sable du test e2e) :

   ```bash
   cd plugins/forever-companion/mcp && python3 tests/e2e_stdio.py --show
   ```

   ou préparer un dossier à la main : `perso/config.json` qui pointe vers un faux dossier
   WoW contenant les SavedVariables des fixtures (voir `build_sandbox()` dans
   `tests/e2e_stdio.py`).
2. Ouvrir une session Claude Code **neuve** dans un dossier qui contient le modèle
   `perso.example/CLAUDE.md` adapté à Brannok, avec `FOREVER_DATA_DIR` pointant vers le
   dossier de test (et `FOREVER_KNOWLEDGE_DIR` vers une mémoire de test si le scénario en
   prépare une).
3. Poser la question telle quelle, sans aide.
4. Relever : outils appelés (ordre et nombre), appels web, tokens et durée (`/cost` ou le
   détail de la session), texte de la réponse.
5. Cocher chaque critère et chaque erreur interdite dans un fichier de résultat
   `resultats/AAAA-MM-JJ-<id>.md` (ce dossier n'est pas versionné s'il contient des données
   réelles).

Un scénario **passe** si tous les critères sont cochés, aucune erreur interdite n'apparaît
et le budget est tenu. Rejouer tout le banc avant chaque version du plugin.

## Scénarios

| id | question | vérifie surtout |
|---|---|---|
| [equipement-evaluer-stuff](scenarios/equipement-evaluer-stuff.md) | « évalue mon stuff » | procédure fixe, récompenses de quête, pas de conseil sans objet |
| [equipement-casques-niveau](scenarios/equipement-casques-niveau.md) | « y a-t-il des casques à mon niveau ? » | mémoire de recherche, budget minimal |
