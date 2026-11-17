# Changelog

## Plugin `forever-companion`

### 0.4.0 — 2026-11-17
- Nouveaux outils MCP (20 au total) :
  - `get_overview` : vue d'ensemble en un appel (perso, armes, emplacements vides, sacs,
    quêtes à rendre, améliorations à gagner en quête) ;
  - `get_quest_rewards` : récompenses des quêtes du journal classées pour le perso
    (maîtrise d'armure et d'arme par classe et niveau, gain estimé comme `compare_item`),
    quêtes à rendre qui donnent une amélioration en tête ;
  - `search_knowledge` / `save_knowledge` : mémoire de recherche, un fichier Markdown daté
    par trouvaille (sujet, sources, certitude) dans `<dossier de données>/connaissances/`.
- `get_quests` affiche la récompense conseillée sous chaque quête.
- Comportement : jamais de conseil « remplis cet emplacement » sans objet précis (vide ≠
  faible), objets nommés avec source et `/way`, risques signalés (mobs plus hauts, royaume
  PvP, groupe) ; procédure fixe du skill `forever-equipement` (état du perso, sacs,
  récompenses, mémoire, puis web) ; chargement des outils `forever` en un seul
  `ToolSearch` (`+forever`) ; sous-agent réservé aux recherches profondes (≤ 8 appels web).
- Modèle `perso.example/CLAUDE.md` pour le dossier du joueur.
- Banc d'évaluation `docs/evals/` (format de scénario, deux premiers scénarios).

### 0.3.0 — 2026-11-17
- Charte de réponse (`knowledge/format-reponse.md`) : en-tête du perso, verdict d'abord,
  gabarit par type de question, badges et certitude, règle de fraîcheur.
- Formules de calcul sourcées (`knowledge/formules.md`), dont 14 PA = 1 DPS (confirmé en jeu).
- Nouveaux skills `forever-equipement` et `forever-familier` ; les 6 autres appellent
  d'abord les outils MCP.
- Correction : les compétences d'armes existent dans Forever (seul le bonus racial a disparu).

### 0.2.1 — 2026-11-17
- Messages du serveur : « Ctrl+Maj+S ou /sync » au lieu de « /reload ».

### 0.2.0 — 2026-11-17
- Serveur MCP `forever` (Python, bibliothèque standard) : 16 outils (fiche, stats,
  équipement, talents, sorts, quêtes, métiers, sacs, réputations, familier, progression,
  comparaison d'objets et de persos, gestion des persos et des comptes).
- Synchro : `etat.json`, section auto de `profil.md`, journal automatique, un instantané
  par jour, multi-comptes et multi-persos.

### 0.1.0 — 2026-11-12
- Agent `forever-guide`, 6 skills, base de connaissances et sources.

## Addon ForeverScribe

### 1.2.0 — 2026-11-17
- Récompenses de quête capturées (schéma 1.2) : objets au choix et fixes avec leurs
  infos complètes (type, emplacement, stats, DPS, niveau requis, utilisable), argent, XP,
  réputations, sorts. Lecture mise en cache par quête, différée quand le journal de quêtes
  est ouvert, sélection du joueur restaurée ; objets pas encore en cache relus à leur
  chargement.

### 1.1.1 — 2026-11-17
- Correctif : à la sortie du jeu, le client renvoie parfois des valeurs vides (PV, XP,
  sacs, argent). L'addon garde alors la capture précédente au lieu de l'écraser.

### 1.1.0 — 2026-11-17
- Synchro en un geste : raccourci (Ctrl+Maj+S par défaut), `/sync`, bouton de minicarte.
  Refusée en combat. Origine de chaque écriture enregistrée.

### 1.0.0 — 2026-11-17
- Capture de 21 domaines (identité, progression, position, stats, équipement, talents,
  sorts, quêtes, métiers, recettes, familier, sacs, banque, argent, réputations,
  monnaies, groupe, effets, collections, réglages Forever).

## Addon ForeverProbe

### 0.1.0 — 2026-11-17
- Sonde de diagnostic : inventaire de l'API et appels de test.
