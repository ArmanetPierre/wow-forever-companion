# Changelog

## Plugin `forever-companion`

### 0.6.0 — 2026-11-17
- **English support.** The MCP server, the local game database, the agent and the skills
  now work with an English (enUS) or French (frFR) game client, and answer in English or
  French. Game language (item, quest, zone names) ≠ answer language (the language of the
  player's question).
- Every `forever` tool takes an optional `lang` (`en` / `fr`). Default: `answer_language` in
  `perso/config.json`, else the character's client language, else English.
- Server text localized through `mcp/i18n.py` + `mcp/i18n_en.py` (labels, verdicts, units,
  money g/s/c, number format, badges `[Forever · local DB]`). Tool descriptions in English.
- French-dependent logic replaced by IDs: canonical stat keys, verdict codes, weapon skills
  by SkillLine, item types parsed in both languages (class/subclass), professions by
  SkillLine (French or English names), pet abilities and passives recognized in both
  languages.
- `profil.md`, `journal.md`, `objectifs.md` generated in the character's language;
  `## My notes` and `## Mes notes` both recognized.
- Game database: client language detected (`Config.wtf` textLocale, `.build.info`, else
  enUS), `forever-<locale>.sqlite`, CASC read with the locale mask; the server picks the
  database matching the character's client.
- Agent and 8 skills: bilingual descriptions, answer in the question's language; answer
  charter English section; `perso.example/CLAUDE.example.en.md`; README in English
  (French: `README.fr.md`), CONTRIBUTING in English.
- Tests: `tests/test_i18n.py` (catalog coverage, formatting, enUS client), e2e
  `--lang en` and `--client enUS`.

### 0.5.0 — 2026-11-17
- **Base locale du jeu** (`gamedata/`) construite chez chaque joueur à partir de son client
  WoW Forever, en lecture seule : `python3 tools/gamedata/build_db.py` (ou
  `python3 -m gamedata.build` depuis le dossier du plugin). Lit les tables DB2 du stockage CASC
  (CascLib, compilée une fois) avec les définitions WoWDBDefs, applique les correctifs du
  serveur (`DBCache.bin`), lit les titres des quêtes déjà vues (`questcache.wdb`) et écrit
  `<données>/gamedata/forever-<langue>.sqlite` (schéma : `docs/schema-gamedb.md`). Aucune
  donnée du jeu n'est publiée dans le dépôt.
- Stats des objets calculées comme le client (répartition × budget RandPropPoints), armure
  (ItemArmorTotal × qualité × emplacement) et dégâts des armes (ItemDamage*) : identiques aux
  valeurs de l'addon sur tout l'équipement vérifié.
- Nouveaux outils MCP (26 au total), badge `[Forever · base locale]` : `find_upgrades`,
  `find_items`, `get_item`, `get_dungeon_loot`, `find_recipes`, `get_quest_info`.
- `compare_item` accepte un `itemId` quelconque (stats lues dans la base) ; `get_overview`
  ajoute des pistes d'amélioration ; `get_quest_rewards` complète les stats manquantes.
- Agent et skills (équipement, donjons, métiers, quêtes, leveling) : base locale avant la
  mémoire et le web.
- Limites connues : butin des donjons et sources des objets absents des fichiers du client ;
  rang requis des recettes estimé.

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

### 1.3.0 — 2026-11-17
- Client anglais (enUS) pris en charge : nouveau `Locales.lua` (messages de l'addon en
  français ou en anglais selon le client), détection sans dépendre du texte traduit.
- Schéma 1.3 (rétrocompatible) : clés non traduites à côté des libellés (`raceFile`,
  `locale`, `tagId`, `standingToken`, `categoryId`, `professionName`, `loyaltyLevel`…).
- Tests hors jeu sur des fixtures frFR et enUS.
- Nouveau fichier : un **redémarrage complet du jeu** est nécessaire après la mise à jour.

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
