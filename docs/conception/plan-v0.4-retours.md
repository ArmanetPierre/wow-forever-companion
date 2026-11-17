# Plan v0.4 — Améliorations après le premier retour de session

Statut : **proposition, rien n'est développé.**
Source : retour de session « équipement et casque niveau 25 » (17/11/2026).

## Diagnostic en une phrase

L'agent avait les données du perso mais **pas les données du jeu** : il ne savait pas quels
objets existent à ce niveau, ni ce que rapportent les quêtes en cours. Il a donc répondu de
mémoire Classic (faux sur le casque), puis a compensé par une recherche web coûteuse
(21 appels, ~107 k tokens, ~2 min 30) bloquée par Wowhead.

La bonne nouvelle : **le jeu lui-même expose presque tout ce qui manquait.** La sonde a confirmé
que ces fonctions existent dans Forever :

| Besoin | API présente dans Forever |
|---|---|
| Récompenses des quêtes | `GetNumQuestLogChoices`, `GetQuestLogChoiceInfo`, `GetQuestLogItemLink`, `GetNumQuestLogRewards`, `GetQuestLogRewardInfo`, `GetQuestLogRewardMoney`, `GetQuestLogRewardXP` |
| Loot des donjons (Journal des donjons) | `C_EncounterJournal.GetLootInfo`, `GetLootInfoByIndex`, `SetSlotFilter`, `InstanceHasLoot` (+ fonctions `EJ_*` à confirmer) |
| Fiche d'un objet | `C_Item.GetItemInfo`, `GetItemInfoInstant`, `RequestLoadItemDataByID`, `C_Item.GetItemStats` |

## Les améliorations, par ordre de priorité

### 1. Récompenses des quêtes (addon + MCP) — impact fort, effort faible
- L'addon capture pour chaque quête du journal : objets au choix et objets fixes (lien, ID,
  emplacement, type d'armure ou d'arme, stats, ilvl, niveau requis), argent, XP, réputation.
- `get_quests` les affiche ; nouvel outil `get_quest_rewards` qui classe les récompenses
  **utiles pour ce perso** (comparées à l'équipé avec la logique de `compare_item`).
- Effet : « rends ces 3 quêtes, la 2e donne un torse +4 DPS » au lieu de catégories vagues.

### 2. Comportement de l'agent — effort faible
- **Règle** : ne jamais conseiller de remplir un emplacement sans preuve qu'un objet existe à ce
  niveau ; distinguer « emplacement faible » et « emplacement vide normal ».
- **Objets nommés** avec source et `/way`, jamais des catégories génériques.
- **Prévenir des risques** quand on envoie le joueur chercher un loot : niveau des monstres,
  serveur PvP, donjon en groupe.
- **Procédure fixe** pour « évalue mon stuff » : `get_equipment` + `get_inventory` +
  `get_quest_rewards` + `find_upgrades` (point 4), **avant** toute recherche web.
- **Moins d'allers-retours** :
  - charger tous les outils `forever` en une fois en début de session (une seule recherche
    d'outils au lieu d'une par question) ;
  - nouvel outil `get_overview` : perso + équipement + quêtes à rendre + récompenses en un appel.
- **Sous-agent seulement pour la recherche approfondie**, avec un budget annoncé ; les questions
  courantes sont traitées directement avec les skills.

### 3. Mémoire de recherche — effort faible, gain cumulatif
- Quand l'agent trouve une info sur le web (ex. « pas de casque cuir avant ~30, sauf Heaume
  d'Humbert »), il l'enregistre dans le dossier de données du joueur
  (`~/WowForever/connaissances/`), avec source, date et certitude.
- Il consulte cette mémoire avant le web : la même question ne coûte plus 100 k tokens deux fois.
- Les trouvailles solides peuvent être proposées au repo public (`knowledge/`) via une PR.

### 4. Base d'objets locale + `find_upgrades` — impact fort, effort moyen
L'addon construit, chez chaque joueur, une base des objets Forever **réels**, sans site externe :
- **Journal des donjons** : commande `/scribe journal` qui exporte le loot des donjons
  (dont les 9 nouveaux), par boss, emplacement et stats ;
- **Tout objet vu** : récompenses de quête, sacs, banque, butin, **marchands** (à l'ouverture
  d'un vendeur), hôtel des ventes (pages consultées) ;
- Outil `find_upgrades(emplacement?, niveau_max?, source?)` : filtre par armure et arme
  portables par la classe, niveau requis, compare à l'équipé et classe par gain de DPS,
  avec la source de chaque objet.

### 5. Connaissances de règles et de repères — effort moyen
- `knowledge/regles-equipement.md` : types d'armure et d'armes par classe et par niveau
  (ex. chasseur : maille à 40), double arme / arme à deux mains, priorités de stats.
  À vérifier dans Forever et sourcer.
- `knowledge/reperes-par-niveau.md` : à quel niveau apparaissent les premiers objets de tête,
  cou et bijoux ; DPS d'arme attendu par tranche de niveau. Alimenté ensuite par la base locale.
- `get_equipment` indique pour chaque emplacement vide si c'est **normal à ce niveau**.

### 6. Sources de secours — effort faible
- `knowledge/sources.md` : documenter que les listes Wowhead /forever ne sont pas lisibles
  automatiquement, et l'ordre de secours : base locale → mémoire de recherche →
  pages d'objet Wowhead individuelles / infobulles → warcraft.wiki.gg → guides.

### 7. Banc d'essai — effort faible
- `docs/evals/` : chaque retour de session devient des scénarios (question, outils attendus,
  erreurs à ne pas refaire, budget d'appels). On les rejoue après chaque changement pour
  mesurer : justesse, nombre d'appels, tokens, temps.
- Premier scénario : cette session (« évalue mon stuff » ne doit plus conseiller de casque à 25).

## Ordre de réalisation proposé

| Lot | Contenu | Pourquoi d'abord |
|---|---|---|
| **A** | 1 (récompenses) + 2 (comportement) + 3 (mémoire) + 7 (banc d'essai) | gains immédiats, peu de code |
| **B** | 4 (base d'objets + `find_upgrades`) | la vraie réponse aux questions d'équipement |
| **C** | 5 (règles et repères) + 6 (sources) | s'appuie sur les données de B pour les repères |

Chaque lot se termine par : tests verts, scénarios du banc d'essai rejoués, test en jeu.
