# Plan — Optimiser l'accès de l'agent à la base de connaissance

Statut : **lots O1 à O5 livrés en v0.8.0** (2026-11-18), résultats en section 8. Hors
chantier : levier 7 (talents, butin, formateurs). O5 sans FTS5 (voir section 8).

Objectif : que l'agent trouve **vite** l'info utile au joueur, en **1 à 2 appels** pour les
questions courantes, avec moins de tokens, moins de web et la même justesse.

## 1. Comment on mesure

- `docs/evals/mesure.py` (bibliothèque standard) rejoue **sans modèle** la séquence d'outils
  qu'un agent appelle pour chaque question type, et sort : appels, taille des réponses,
  tokens estimés (caractères / 3,5), lignes redondantes, durée des outils, coût fixe
  (instructions serveur, schémas des outils, agent, skills, fichiers `knowledge/`).
- `docs/evals/sequences-v0.5.json` : 8 questions types avec la séquence que les skills v0.5
  prescrivent. Une `sequences-cible.json` sera écrite avec chaque lot pour comparer avant/après.
- `docs/evals/scenarios/` : scénarios jugés à la main (critères, erreurs interdites, budget),
  avec la mesure v0.5 dans l'en-tête.

```bash
python3 docs/evals/mesure.py
```

Sans option : bac à sable (fixtures + base synthétique), chiffres publiables. Avec
`--data-dir` et `--gamedb` : données réelles du joueur. `--textes` garde le texte des
réponses dans `--json` : **à ne jamais committer** (données du perso).

## 2. Mesures actuelles (v0.5.0)

### Coût fixe

| Élément | ≈ tokens | Quand il est payé |
|---|---:|---|
| Instructions du serveur MCP | 273 | toujours |
| Descriptions des 8 skills | 941 | toujours |
| Schémas des 26 outils | **4 440** | après `ToolSearch +forever` (une fois par session si l'agent suit la règle) |
| Corps d'un skill | ≈ 560 (4 491 pour les 8) | à chaque skill chargé |
| `knowledge/format-reponse.md` (charte) | **2 948** | si l'agent la lit |
| `knowledge/forever-essentiels.md` | 4 107 | si lu |
| `knowledge/sources.md` | 3 571 | si lu (avant web) |
| `knowledge/formules.md` | 1 253 | si lu |
| Corps de l'agent `forever-guide` | 1 939 | si sous-agent lancé (+ tout le reste rechargé, cache froid) |

Contexte typique d'une question courante : **≈ 9 000 tokens** de fixe (instructions,
descriptions, schémas, un skill, la charte), **≈ 15 000 à 20 000** si l'agent lit aussi
`forever-essentiels` / `sources` ou passe par le sous-agent.

Les plus gros schémas : `compare_item` 1 517 car., `find_upgrades` 1 180, `save_knowledge`
1 039, `find_items` 801. Démarrage serveur + `tools/list` : ≈ 45 ms.

### Par question (séquences v0.5)

| Question | Appels MCP | Web probable | Sortie bac à sable (≈ tok) | Sortie données réelles (≈ tok) | Redondance (réel) |
|---|---:|---:|---:|---:|---:|
| Je fais quoi maintenant ? | 5 | 1 | 1 150 | **4 788** | 8 % |
| Évalue mon stuff | 6 | 0 | 1 438 | **4 153** | 11 % |
| Quêtes à rendre | 2 | 0 | 496 | 1 579 | 4 % |
| Monter le travail du cuir | 3 | 1 | 439 | 3 037 | 2 % |
| Prochain point de talent | 3 | 2 | 490 | 1 042 | 12 % |
| Familier | 2 | 0 | 253 | 671 | 9 % |
| Un casque à mon niveau ? | 4 | 1 | 551 | 1 742 | 5 % |
| Préparer un donjon | 5 | 2 | 845 | 1 813 | 7 % |
| **Moyenne** | **3,8** | **0,9** | **707** | **≈ 2 350** | |

Données réelles : un perso niveau 25, journal de 40 quêtes plein, 52 places de sacs
(chiffres agrégés, aucun contenu recopié ici).

### Ce que disent les chiffres

1. **Les outils sont instantanés** (1 à 33 ms par question). Le coût réel est ailleurs.
2. **Chaque appel = un tour du modèle** (il relit le contexte, décide, appelle). 3,8 appels
   séquentiels plus ≈ 1 `ToolSearch` et ≈ 1 web par question, c'est la latence ressentie.
3. **Le web coûte un ordre de grandeur de plus** que tout le reste : la session réelle du
   17/11 (casque) a fait 21 appels, ≈ 107 k tokens, ≈ 2 min 30, surtout en web. Les web
   restants viennent de **trous de données** (arbres de talents, butin des donjons,
   formateurs, quêtes), pas d'un mauvais routage.
4. **Les réponses longues sont celles des questions larges** : `find_upgrades` seul fait
   ≈ 7 500 caractères en réel (3 objets par emplacement, 8 emplacements),
   `get_quests` ≈ 5 100 (journal plein). `quoi-faire` relit les quêtes à rendre deux fois
   (`get_overview` puis `get_quests`).
5. **En-tête répété** : chaque réponse recommence par l'identité, la fraîcheur et la note
   « repris de la capture précédente » (≈ 250 caractères × 5 appels = la moitié de la
   redondance mesurée).
6. **Les schémas** (4 440 tokens) pèsent autant que la réponse d'une grosse question, pour
   26 outils dont certains se recouvrent (`get_character` / `get_stats` / `get_overview` ;
   `get_quests` / `get_quest_rewards` / `get_quest_info` ; `find_items` / `find_upgrades` /
   `get_item` / `compare_item`).

## 3. Leviers, classés gain / effort

| # | Levier | Gain estimé | Effort | Risque |
|---|---|---|---|---|
| 1 | **Résumé précalculé à la synchro** servi par `get_overview` | quoi-faire 5 → 1 appel, évaluer-stuff 6 → 1-2 ; ≈ −4 tours sur les 2 questions les plus fréquentes | moyen | faible |
| 2 | **Routage direct + charte courte + budget par question** | −1 tour (pas de lecture de charte), −2 500 tokens fixes, plus de sous-agent | faible | faible |
| 3 | **`detail` court/normal/complet + en-tête une seule fois** | sortie réelle −40 à −50 % (quoi-faire ≈ 4 800 → ≈ 2 000 tok) | faible | faible |
| 4 | **Outils d'intention qui croisent côté serveur** (familier × sacs, recettes × compétence × sacs, donjon × quêtes × équipé) | −1 appel sur familier, métier, donjon | moyen | faible |
| 5 | **Fusion des outils 26 → ≈ 12** | schémas 4 440 → ≈ 2 000 tok, moins d'erreurs de choix | moyen-fort | moyen (skills, docs, tests) |
| 6 | **Recherche globale `search(query)`** (index FTS5 FR/EN : objets, quêtes, sorts, zones, PNJ, notes) | évite 1-2 essais ratés sur un nom (accents, apostrophes, langue) | moyen | faible |
| 7 | **Combler les trous de données** (talents, butin, formateurs, quêtes) | −0,9 web/question en moyenne, le plus gros gain en temps | fort | dépend des sources |
| 8 | **Score de pertinence joueur** (niveau, classe, zone, quête au journal) | réponses plus courtes et mieux ordonnées ; sert 1, 3, 4, 6 | moyen | faible |
| 9 | **Stabilité du cache** (liste d'outils et instructions fixes, rien de daté hors résultats) | cache de prompt réutilisé d'une question à l'autre | faible | nul |
| 10 | **Fraîcheur** : une ligne d'âge, alerte seulement si > 1 h ou domaine vide | −150 car. par appel, moins de bruit | faible | nul |

### Détail des cinq premiers

**1. Résumé précalculé.** `sync.py` calcule, à chaque synchro, un `resume.json` par perso :
quêtes à rendre groupées par lieu avec la meilleure récompense, 3 meilleures améliorations
(tous emplacements, avec source), quêtes du niveau dans la zone, prochaine étape (niveau du
formateur de classe, zone suivante, donjon à portée), métiers (points restants avant le
palier), familier (bonheur, nourriture dans les sacs), munitions et place. `get_overview`
le sert tel quel, en ≈ 1 500 tokens. Pas de calcul au moment de la question, pas d'oubli.

**2. Routage direct.** Chaque skill commence par sa séquence exacte et son budget
(« 1 appel : `get_quest_rewards a_rendre:true`. Web : jamais. »). La charte passe de
≈ 2 950 à ≈ 600 tokens, recopiée dans l'agent (plus de lecture de fichier). Règles :
un seul `ToolSearch +forever` par session, pas de sous-agent pour une question courante,
`search_knowledge` seulement avant un web, pas en réflexe.

**3. Niveaux de détail.** Paramètre `detail` sur les outils de liste : `court` par défaut
dans les séquences (1 meilleur objet par emplacement, quêtes à rendre seulement), `complet`
sur demande. En-tête complet uniquement dans `get_overview` ; les autres outils gardent une
ligne (`Brannok 25 · capturé il y a 12 min`).

**4. Outils d'intention.** Le serveur fait les croisements que l'agent fait aujourd'hui en
2-3 appels : `get_pet` liste la nourriture compatible déjà en sacs ; `find_recipes` filtre
« rapporte encore des points » et marque les composants possédés ; `get_dungeon_loot`
ajoute niveau conseillé, quêtes du journal pour ce donjon et butin comparé à l'équipé.

**5. Fusion des outils.** Cible indicative (noms à fixer avec le chantier anglais) :

| Outil cible | Remplace |
|---|---|
| `overview(detail)` | get_overview, get_character, get_stats, get_progress |
| `gear(emplacement?, detail)` | get_equipment, find_upgrades, compare_item |
| `bags()` | get_inventory |
| `quests(zone?, a_rendre?, quete?)` | get_quests, get_quest_rewards, get_quest_info |
| `items(query/filtres)` | find_items, get_item |
| `professions(metier?)` | get_professions, find_recipes |
| `talents()` / `spells()` | get_talents, get_spells |
| `pet()` | get_pet |
| `dungeon(nom)` | get_dungeon_loot |
| `reputations()` | get_reputations |
| `search(query)` / `knowledge(save?)` | search_knowledge, save_knowledge |
| `characters(...)` | list_characters, set_active_character, register_account, compare_characters |

Les anciens noms restent un temps comme alias non listés (compatibilité des skills).

## 4. Architecture cible par type de question

| Type de question | Aujourd'hui | Cible | Appels cible | Web cible |
|---|---|---|---:|---:|
| Quoi faire maintenant | overview, quests, progress, upgrades, knowledge | `overview` (résumé précalculé) | **1** | 0 |
| Évaluer le stuff | overview, equipment, inventory, quest_rewards, upgrades, knowledge | `overview` puis `gear detail:complet` si besoin | **1-2** | 0 |
| Quêtes à rendre | quests, quest_rewards | `quests a_rendre:true` | **1** | 0 |
| Objet précis (« casque à mon niveau ? ») | knowledge, equipment, upgrades, find_items | `gear emplacement:tête` | **1** | 0 |
| Métier | professions, find_recipes, inventory | `professions metier:…` | **1** | 0 (1 tant que formateurs absents) |
| Familier | pet, inventory | `pet` | **1** | 0 |
| Talents | character, talents, spells | `talents` | **1** | 1 → 0 avec les arbres en base |
| Donjon | overview, equipment, dungeon_loot, quests, knowledge | `dungeon nom:…` | **1-2** | 1 (mécaniques) |
| Nom inconnu (« c'est quoi X ? ») | essais successifs | `search X` | **1** | 0 si en base |

Moyenne cible : **≤ 1,3 appel MCP** et **≤ 0,3 web** par question, contre 3,8 et 0,9.

## 5. Lots (après le chantier anglais)

| Lot | Contenu | Fichiers touchés | Fin du lot |
|---|---|---|---|
| **O1** — routage | leviers 2, 9, 10 : séquences et budgets dans les skills, charte courte dans l'agent, en-tête d'une ligne | `agents/forever-guide.md`, `skills/*/SKILL.md`, `knowledge/format-reponse.md`, `mcp/server.py` (`_head`), `mcp/formats.py` | scénarios verts, coût fixe ≤ 6 500 tok |
| **O2** — résumé + détail | leviers 1, 3, 8 : `resume.json` à la synchro, `get_overview` le sert, `detail` sur les outils de liste | `mcp/sync.py`, `mcp/server.py`, `mcp/gear.py`, `mcp/gamedb_tools.py`, tests | quoi-faire et évaluer-stuff en 1-2 appels |
| **O3** — intentions | levier 4 : familier × sacs, recettes × points × sacs, donjon enrichi | `mcp/server.py`, `mcp/formats.py`, `mcp/gamedb_tools.py`, tests | familier, métier en 1 appel |
| **O4** — fusion | levier 5 : 26 → ≈ 12 outils, alias de compatibilité une version | `mcp/server.py` (TOOLS), skills, `docs/schema*.md`, `tests/e2e_stdio.py` | schémas ≤ 2 200 tok, e2e verts |
| **O5** — recherche | levier 6 : index FTS5 FR + EN construit avec la base, outil `search` | `gamedata/` (construction de la base), `mcp/gamedb.py`, `mcp/gamedb_tools.py` | nom avec ou sans accent, FR ou EN, trouvé en 1 appel |
| (hors chantier) | levier 7 : talents, butin, formateurs, quêtes | lot B restant, recherche de données de quêtes | web moyen ≤ 0,3 |

Ordre conseillé : O1 → O2 → O3 (gains rapides, pas de rupture), puis O4 et O5.
Chaque lot ajoute ou met à jour `sequences-cible.json` et rejoue `mesure.py` + scénarios.

## 6. Critères de réussite

- [x] Moyenne **≤ 1,5 appel MCP** par question sur les 8 séquences (3,8 aujourd'hui).
- [ ] **≤ 0,3 web** par question en moyenne (0,9 aujourd'hui), tous les scénarios avec
      `appels-web: 0` à zéro.
- [x] Sortie moyenne en données réelles **≤ 1 500 tokens** (≈ 2 350 aujourd'hui),
      redondance ≤ 3 %.
- [x] Coût fixe d'une question courante **≤ 6 000 tokens** (≈ 9 000 aujourd'hui),
      schémas ≤ 2 200 tokens.
- [ ] Zéro sous-agent pour les 8 questions types ; un seul `ToolSearch` par session.
- [ ] Justesse inchangée : tous les scénarios de `docs/evals/scenarios/` passent, dont les
      deux scénarios d'équipement existants.
- [ ] Mêmes résultats en client anglais (scénarios rejoués avec la base enUS).

## 7. Dépendances avec le chantier anglais

- **Noms et arguments des outils** (`emplacement`, `niveau_max`, `a_rendre`…) : le chantier
  anglais décide s'ils restent français, deviennent anglais ou ont des alias. La fusion (O4)
  se fait après, sur les noms définitifs, sinon on renomme deux fois.
- **Textes des réponses** (`formats.py`, `server.py`) localisés par le chantier anglais :
  O1 (en-tête court) et O2 (résumé) modifient les mêmes fonctions.
- **Skills et agent** réécrits ou traduits par le chantier anglais : O1 touche les mêmes
  fichiers.
- **Base du jeu FR + EN** : l'index de recherche (O5) a besoin des deux langues pour
  retrouver un nom quel que soit le client.
- **Indépendant** : `mesure.py`, les séquences et les scénarios (déjà livrés) ; la conception
  du `resume.json` peut être affinée dès maintenant.

## 8. Résultats v0.8.0 (2026-11-18)

Mesures `mesure.py` (tokens ≈ caractères / 3,5). Avant = serveur v0.7 + `sequences-v0.5.json` ;
après = serveur v0.8 + `sequences-v0.8.json`. Données réelles : un perso chasseur 25 (chiffres
seuls, aucune donnée versionnée).

| | Avant | Après |
|---|---:|---:|
| Outils listés | 28 | 14 (+ 27 anciens noms appelables) |
| Schémas des outils | 7 548 tok | 2 180 tok |
| Instructions serveur (règles Forever incluses) | 449 tok | 1 113 tok |
| Descriptions des skills | 1 646 tok | 1 111 tok |
| **Coût fixe toujours chargé** | **9 643 tok** | **4 404 tok** |
| Corps de l'agent | 2 500 tok | 1 122 tok |
| Corps des 8 skills | 6 201 tok | 3 716 tok |
| `format-reponse.md` | 3 922 tok | 1 263 tok |
| Appels MCP par question | 3,8 | 1,0 |
| Sortie par question, bac à sable | ≈ 743 tok | ≈ 211 tok |
| Sortie par question, données réelles | ≈ 2 359 tok | ≈ 388 tok |
| Redondance | 2-12 % | 0 % |
| Verdict en première ligne | 0/8 | 8/8 |
| Web probable par question | 0,9 | 0,75 |

Ce qui a été fait :
- **O1** : règles toujours chargées (`knowledge/regles-forever.md` dans les instructions du
  serveur : faits Forever, routage, forme, voix) ; agent, skills et charte raccourcis avec
  séquence et budget ; en-tête d'une ligne.
- **O2** : `resume.json` dans le dossier du perso, calculé à la synchro (et à la demande),
  servi par `overview` avec `detail` court/normal/complet.
- **O3** : familier × nourriture des sacs, métiers × recettes qui rapportent × composants
  possédés, donjon × quêtes du journal et à prendre, sacs × objets à équiper.
- **O4** : 28 → 14 outils d'intention, anciens noms toujours appelables (non listés).
- **O5** : outil `search` (objets, quêtes, PNJ, objets du monde, zones, donjons, recettes,
  notes de recherche, journal et sacs du perso ; FR/EN, accents facultatifs) sur les colonnes
  normalisées de la base, **sans index FTS5** : assez rapide sur la base actuelle (≈ 10 ms).
- Charte de voix (`voix.md`) branchée : réglage `voix` lu par le serveur, liste noire,
  badges en forme naturelle ; `docs/evals/verifie_reponse.py` vérifie la forme d'une réponse.

Reste : levier 7 (web), scénarios à rejouer avec un modèle et en client anglais.
