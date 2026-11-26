# Changelog

## Plugin `forever-companion`

### 0.11.0 — 2026-11-25
- **New `market` tool: optimise a crafting profession with auction house prices.** For a
  profession (Leatherworking by default) and a character:
  - **Level at the best price**: at each step, the recipe with the lowest net cost per point
    (reagents valued at the cheapest of your AH scans, vendor price, or free when already in your
    bags or bank; minus the product's resale, AH net of the 5 % cut or vendor). A step whose
    reagents have no price says so instead of showing a cost.
  - **Profit**: known or learnable recipes ranked by profit, margin, volume seen and price date;
    "sell raw or craft?" for leather and hides you gather.
  - **Gear**: craftable items that upgrade this character or another one (`pour`), with
    "craft or buy?" when the finished item was seen at the AH, and item sets flagged.
  - **Bags**: keep, craft, list at the AH or sell to a vendor.
  - Without any AH price it still works on vendor prices and lists the items to look up first.
    Prices are never invented; prices older than 3 days are flagged.
- **Price history**: each sync keeps one point per item and per day for 60 days, shared by all
  characters of the same realm and faction (`perso/prix/<realm>-<faction>.json`, never in the
  repo).
- Uses the recipe colours captured in game (addon 1.5) when present.
- Server and agent now list 16 tools; `forever-metiers` explains how to read prices.

### 0.10.0 — 2026-11-18
- **Fixes from the strategy-question tests** (`docs/comparaison/serie2/resultats.md`):
  - **`professions`**: current and next tier with the skill required ("not yet: 106/125"),
    trainers for the character's faction with `/way`, and a levelling route from the current
    skill (or from 1 for an unlearned profession; `cible` sets the goal): recipe per step,
    estimated colours and number of crafts, reagents, vendor price and nearest vendor, vendor
    resale. Tier thresholds and colours are Classic values marked "to verify"; no auction
    house price exists anywhere and none is invented.
  - **Recipe ranks fixed** (`gamedata/recipe_rank.py`): the client stores rank 1 for most
    recipes, and the old estimate (5 × item level) gave ≈5 for high-level recipes. The rank now
    comes from the recipe, the pattern or the crafted item first (≈80 % of recipes), then an
    estimate marked "≈". Recomputed when read, so `find_recipes` and older databases benefit.
  - **`dungeon`**: loot per boss with stats and a verdict for the character's class, plus
    mechanics, in one call (26 of 37 dungeons): QuestieDB lists for Classic dungeons, sourced
    guides (marked "probable") for Hall of Thanes, Ruins of Lordaeron, Excavation Site:
    Wetlands and Dalaran, with their quests, givers and `/way`.
  - **`quests`**: a French zone name could resolve to an empty duplicate zone ("Bois de la
    Pénombre" gave 0 quests, "Duskwood" 14); zones now resolve the same in French, English or
    without accents. XP per quest (real value from the addon when captured, otherwise a
    Classic estimate ±30 %), totals with the level reached, and grey quests to abandon.
  - **`talents` with `arbre`**: the full tree of the character's class, read from the
    client's Trait tables with Forever's hotfixes (470 talents, 9 classes): rank/max, taken,
    available now or blocked (row points or prerequisite).
  - **`search`** finds items by their English name, including Forever items and items with
    no source (QuestieDB names are all kept).
  - **Knowledge**: `metiers-forever.md` (Forever profession changes: camp objects such as the
    Reagent Bot and Repair Bot, Merchant's Favor and its vendors, First Aid healing potions,
    cooking, fishing, Legacy perks), with sources and certainty; quest XP formula in
    `formules.md`.
  - Game database schema 4 (talents table, all QuestieDB item names): rebuilt automatically.
- **Fixes from the second test pass:**
  - **Levelling route never uses grey recipes.** Classic yellow/grey thresholds come from the
    Classic Era `SkillLineAbility` table, downloaded on the player's machine when the database
    is built (wago.tools CSV, cached; table `recipe_colors`, nothing shipped in the repo);
    without it, a cautious "≈" estimate is used and only orange/yellow steps are kept. Crafts
    use the expected skill-up chance.
  - Recipes learned with the profession start at rank 1 (Tailoring and Alchemy routes now start
    at 1).
  - Gathering professions (Herbalism, Mining, Skinning, Fishing) show nodes or beast levels by
    skill and nearby zones instead of a recipe route.
  - The verdict says first when the character already has two primary professions.
  - Reagent totals are expanded to raw materials, with intermediates listed apart.
  - **Excavation Site: Wetlands guide**: *Highland Hides* asks for Thicket Raptor Hides (with its
    prerequisite), *Songblade Search* separates giver and turn-in, entrance and trash dangers
    added (sourced, "probable").
  - `quests`: quests filed under a zone by QuestieDB but given elsewhere are set apart with a
    note (an Arathi quest no longer shows in the Wetlands).
- **One-click install and update, macOS and Windows.** Each GitHub Release carries
  `WoW-Forever-Companion-macOS.zip` (double-click *Installer WoW Forever Companion.command*)
  and `WoW-Forever-Companion-Windows.zip` (*Installer WoW Forever Companion.cmd*); the same
  installer runs in one line (`curl … install/install.sh | bash`, `irm … install/install.ps1 | iex`).
  Six numbered steps, in French or English: prerequisites (Python 3.9+, Claude Code; nothing
  third-party installed without a typed "yes": Python is never installed, python.org is shown; Anthropic's Claude Code installer is offered only after confirmation), game detection, ForeverScribe addon copied
  into `Interface/AddOns` (a development symlink is left alone), marketplace and plugin
  added or updated, player folder created from `perso.example` (never overwritten), optional
  local game database. Run it again to update; `--uninstall` / `-Uninstall` removes the
  addon and the plugin and keeps the player data. On Windows it records `FOREVER_PYTHON`
  when `python3` is missing. `tools/release/build_release.py` builds the archives (no
  player data, executable bits kept) and `.github/workflows/release.yml` attaches them to
  the release on a `v*` tag. The archives are not signed yet: since macOS 15, the first
  launch must be allowed in System Settings › Privacy & Security › "Open Anyway" (or
  `xattr -dr com.apple.quarantine` on the unzipped folder); the one-line command avoids it. Sandbox tests in `install/tests/` (fake home, game and
  `claude`), run by the CI on macOS, Ubuntu and Windows.
- **Zone map with markers (`map` tool).** When an answer gives a `/way` the player has to
  find, the agent can show the zone map with a numbered red marker per point and the
  character in blue (when they are on that map). `points` takes `"/way 38.1 50.2 Whelgar"`
  strings or `{x, y, label}`; `zone` takes a client name, an English name or a uiMapID and
  is required as soon as there are points (without it, a `/way` would land on the map the
  character stands on); with no points it shows the current zone; `cadre: auto` zooms on close markers, `zone` shows the whole
  map. The answer carries the PNG (MCP image content) and its path.
- **Maps come from your own client, read-only.** UiMap → UiMapXMapArt → UiMapArtTile give
  the background tiles; the discovered-area overlays (WorldMapOverlay) are laid on top as if
  the whole zone were explored. BLP2 textures (DXT1/3/5, palette, BGRA) are decoded and the
  PNG is written in pure Python (`gamedata/blp.py`, `gamedata/maps.py`, `mcp/worldmap.py`).
  Forever's own maps (Île de Zéphras, Rives Claires, Mont Hyjal…) are included.
- **Cache on the player's machine only:** `<data>/gamedata/maps/<build>/` (index + one
  compressed image per zone, about 1 MB, extracted on first request, under a second) and
  rendered maps in `<data>/gamedata/cartes/` (the 40 latest are kept). Nothing extracted from
  the client goes into the repository; the tests use synthetic textures.
- The database build now also indexes the maps (`python3 -m gamedata.maps` extracts them
  all ahead of time). The `forever-quetes` and `forever-leveling` skills and the
  `forever-guide` agent show a map only when the player looks for a place, one per answer.

### 0.9.0 — 2026-11-18
- **Quests added by Forever get a real sheet.** About half of the quests met so far are not
  in QuestieDB. `quests`, `npc`, `search` and `overview` now merge three local sources, in
  this order of trust:
  - **seen in game** (`[Forever · observé en jeu]`): the quest memory of addon 1.4. It holds
    who gives and who takes each quest, where, the quests an NPC offers and where objectives
    progressed;
  - **QuestieDB** (`[Forever · QuestieDB]`), as before;
  - **client cache** (`[Forever · cache du client]`): the full quest text from
    `questcache.wdb`, plus creature and world-object names from `creaturecache.wdb` and
    `gameobjectcache.wdb`. NPCs and places named in the text are matched and shown as
    « probable », with a `/way` when one is known.
- **Quest memory at sync:** the sync reads `ForeverScribeDB.questMemory` from each account
  file and merges the accounts of one user into `perso/<User>/memoire-quetes.json` (never in
  the repository). Rules: union deduplicated by kind and id, the latest position wins, a
  confirmed turn-in beats a « listed » NPC, points closer than 1.5 % count once. The file is
  rewritten only when its content changes.
- **Client caches in the local database:** new tables `c_quests`, `c_creatures` and
  `c_objects`, refreshed at sync and at build (skipped while the cache files are unchanged;
  `python3 -m gamedata.clientcache` runs it alone). Nothing is written to the game folder.
- **Wowhead on demand** (`[Wowhead Forever]`): when no local source places an NPC or names a
  quest, the server asks the public Wowhead tooltip for that one id (`dataEnv=16`). At most 3
  requests per tool call, 1 second apart, 4-second timeout, generic User-Agent, nothing about
  the player in the URL, 10-minute pause after a network error. Answers (and « not found »,
  rechecked after 7 days) are cached in `<data>/gamedata/.cache/wowhead/`. Turn it off with
  `"web_lookup": false` in `perso/config.json` or `FOREVER_WEB_LOOKUP=0`.
- Quest text cleanup: the client placeholders `$1oa` and `$gmale:female;` no longer leak into
  objectives.
- `knowledge/regles-forever.md`: condensed Forever facts (level cap, rulesets, new dungeons,
  raid date, XP notes). Fixed cost stays within 5 % of 0.8.0.
- Tests: quest memory merge and sync, client caches on synthetic WDB files, quest sheets
  without QuestieDB, Wowhead with a simulated fetch (no network in any test).
- **Fixes from the first evaluation pass** (forum-style questions run against real data):
  - Privacy: the account number is masked (`••••#1`) in the character sheet.
  - Quests: turn-ins show the real NPC, its zone and `/way` (observed, then QuestieDB end
    NPC, then captured point); `a_rendre` and `detail: complet` no longer come back empty;
    the `disponibles` header gives the real level span of the listed quests and a clear verdict
    when QuestieDB has nothing for the zone.
  - Gear: the verdict accounts for the required level and the weapon skill (« not yet: level 26
    required, then about +2.4 DPS »); rings, trinkets and one-hand twins are compared with the
    weaker one; a crafted item out of reach says the skill gap (« Leatherworking ≈150
    required, you are at 106 »); the misleading « skill 1 » is gone; test, retail-stat and
    absurd-level items are filtered out of searches and upgrades.
  - Dungeons: new reference table `knowledge/donjons.json` (levels for every dungeon incl. the
    9 Forever ones, raid status: opens 9 Dec 2026 or not open yet). The list hides test and
    Season of Discovery maps; bosses are deduplicated; the verdict follows the level range;
    quests of the log for the dungeon include their chains (category match fixed) and known
    bugs from the knowledge files are shown. « Coeur » now finds « Cœur du Magma ».
  - Search: whole-word and prefix scoring; plugin knowledge sections, spells and NPC
    subtitles (« maître des chasseurs ») are searched, accents optional.
  - Pet: food in bags is read from the item class (cooked food and raw meat), drinks and oils
    excluded, items a quest of the log asks for are kept aside, low-level food is flagged;
    training points shown as level × (loyalty − 1).
  - Bags: items a log quest asks for are listed with their quest; other quest items are
    flagged « check before deleting ».
  - The overview header shows the ruleset (PvP, Hardcore…).
  - Tests: `tests/test_eval_fixes.py` (synthetic Brannok data).
- **Fixes from the second evaluation pass:**
  - Search: knowledge sections open directly by their title (`search texte:"<title>"
    type:connaissance`, the command is printed after each hit); long sections are cut cleanly,
    never inside a table, with the number of lines left. Softer matching: French and English
    stop words, simple stems, FR/EN synonyms (battleground → BG, auction house → HdV…),
    œ/æ, apostrophes and hyphens. « Menethil » now gives the zone first. English item names
    from QuestieDB are searchable; NPCs of the other faction are skipped.
  - Item sources: `item`, `gear` and `dungeon` fall back to QuestieDB drops, vendors, objects
    and quest rewards (vendor first for common items, NPC levels, local spawns first).
    `dungeon` lists boss loot from QuestieDB (`[Forever · QuestieDB]`, to confirm in game).
  - Quests: homonyms open the quest in the log first and list the others with their id; a
    known bug from the knowledge files is shown on the sheet; with `lang: en`, quest and NPC
    names come from QuestieDB in English (the in-game title is shown too); without captured
    rewards, `a_rendre` says so in one line.
  - `dungeon`: quests to pick up whose objectives target the instance (start of the chain
    included); zone names and notes in English with `lang: en`.
  - `overview` uses the same food logic as `pet`.
  - Gear: `niveau_max` can be above the character's level; items whose stats do nothing for
    the class (healer or caster stats for a hunter, rogue or warrior; Agility/Strength for a
    mage, priest or warlock) are « not for you »; resistance-only items no longer fill an empty
    slot. A comparison with no DPS difference always gets a bold verdict and only breaks the
    tie on a stat one of the items has. Intellect counts for a hunter only as a tie-breaker,
    and only when the Forever talent « Visée minutieuse » is captured (coefficient unknown,
    `[Forever · probable]`).
  - XP to a target level: `overview` with `niveau_cible` (progress view). The table comes from
    the client (`LevelExperience`, new `xp_levels` table in the local database, schema 3, so
    the next build rebuilds it); without it, the Classic Era table with `[Classic · probable]`.
  - Routing: ruleset, Heritage, social and rules questions go to `search type:connaissance`;
    `forever-donjons` calls `characters` for loot of another class.
  - Tests: `tests/test_eval_fixes2.py` (synthetic data).
- **Fixes from the third evaluation pass:**
  - Gear: items added by Forever whose client data says « level 1 » get an estimated
    required level (item level − 5, shown « ≈N (estimated) ») instead of being offered at
    level 1; estimated items with no known source are skipped. With `niveau_max` above the
    character's level, a **Later** section lists items wearable at that level, and the verdict
    says « aim for X at level N ». An item already worn is « already worn », or « a 2nd copy
    in <other slot> » for rings, trinkets and one-hand twins.
  - Quests: a known bug listed for one step of a chain (by id) no longer spreads to the other
    quests of the same title; when the quest log and QuestieDB disagree on a quest level, the
    log wins and the sheet says so; the `disponibles` verdict counts every matching quest,
    not just the ones shown.
  - `npc`: technical client NPCs (`World …`, `[PH]`, `[DND]`, all caps) are hidden and NPCs
    with a known position come first; « paladin trainer » finds the trainers through their
    subtitle, for the character's faction.
  - `dungeon` for a raid: the attunement chain for the character's faction (start NPC with
    `/way`, final quest, number of steps, done mark; Onyxia filled in
    `knowledge/donjons.json`); stray item-started quests are gone.
  - `professions` for a profession the character doesn't have says so and points to
    `characters`; no more « ? » rank. Weapon types are no longer doubled (« one-hand mace »,
    not « one-hand mace one hand »), in recipes and item sheets.
  - `item` finds an item by its English name (QuestieDB) on a French client.
  - Knowledge: PvP vendor outage dated and marked « to recheck »; the Hall of Thanes access
    chain (Earthseer Farsen, Alliance), marked « probable », with its sources.
  - Tests: `tests/test_eval_fixes3.py` (synthetic data).

- **Windows and Linux portability** (see `docs/portabilite.md`): the server starts with
  `${FOREVER_PYTHON:-python3}`; one shared game finder (`mcp/wowpaths.py`) for sync, the
  local database and `install.sh` checks the Windows registry, Battle.net settings, drives,
  macOS volumes and Wine, Lutris, Proton and Bottles prefixes; command-line tools and the
  server write UTF-8 with LF on every OS; SQLite paths with `#` or `%` open the right file;
  CascLib gets ANSI paths on Windows and a clear error on architecture mismatch; file
  replacement retries when Windows locks the file; `install.ps1` is saved with a BOM; a new
  `perso/` folder is private (`0700`) on macOS and Linux.
- **`gear` no longer suggests other-faction vendor items** (for example a Horde-only
  quartermaster's necklace for an Alliance character).

### 0.8.0 — 2026-11-18
- **Faster, cheaper agent.** Most questions now take one tool call instead of 3.8. On real
  data, the tool output per question falls from about 2,360 tokens to about 390. The fixed
  cost (tool schemas, server instructions and skill descriptions) falls from about 9,600
  tokens to about 4,400. Measured with `docs/evals/mesure.py`; the reference sequences are
  `sequences-v0.5.json` and the new ones `sequences-v0.8.json`.
- **14 intent tools replace the 28 listed tools:**
  - `overview` (`vue: fiche|stats|progres`)
  - `gear` (also compares an item with `objet` or `stats`)
  - `quests` (`quete`, `disponibles`, `a_rendre`)
  - `npc`, `item`, `professions`, `pet`, `talents`, `dungeon`, `bags`, `reputations`
  - `search`, `save_knowledge`, `characters` (`action: activer|comparer|rattacher`)
  - Every tool takes `detail` (`court` by default, `normal`, `complet`) where it applies,
    and `lang`.
- **Migration:** the 27 old tool names (`get_overview`, `find_upgrades`, `get_quest_info`,
  `find_quests`, `find_npc`, `compare_item`, `search_knowledge`…) are still callable, with
  the same arguments and output, but no longer listed. Saved prompts and `CLAUDE.md` files
  that name them keep working. Switch to the new names; the old ones may be removed in a
  later version.
- **Digest computed at sync:** `resume.json` is written in the character's folder (never in
  the repository). It holds the quests to turn in, grouped by zone with the best reward;
  upgrades within reach with a known source (quest rewards, bags, local database); quests
  to pick up nearby; the next step (XP, class trainer); and the state of bags, ammo, pet
  food and professions. `overview` serves it in a few milliseconds.
- **Verdict first:** every intent tool starts with a one-line `**Verdict:**`. A one-line
  header follows, and the capture age shows only after one hour.
- **Cross-checks on the server:**
  - pet diet with the food in bags;
  - recipes that still give points with the reagents owned (full names only);
  - dungeon with the quests in the log and the quests to pick up;
  - gear in bags worth equipping;
  - items from the database with an unknown source, listed apart.
- **Global search** `search`: items, quests, NPCs, world objects, zones, dungeons, recipes,
  research notes, the quest log and the bags. It works in French or English, accents
  optional. A clear hit returns its sheet.
- **Forever rules always loaded:** `knowledge/regles-forever.md` is included in the
  server instructions. It covers Forever facts, routing, answer form and voice.
- **Shorter agent, skills and answer charter:** each skill now gives the exact calls and a
  budget. There is no subagent for routine questions.
- **Voice** (`knowledge/voix.md`): a new `voix` setting in `perso/config.json`. It takes
  `joueur` (the default), `pnj` or `neutre`; `voice` with `player`, `npc` or `neutral` is
  also accepted. The server reads it and shows it in the `overview` header. The answer
  charter now lists phrases to avoid and accepts natural badges
  (_Base locale Forever · sûr_).
- **Answer check:** new `docs/evals/verifie_reponse.py` checks that an answer starts with a
  bold verdict, cites a badge, uses no listed phrase and no emoji, and stays short.
  `mesure.py` also checks for a verdict on the first line and takes a `--perso` option.
  The scenarios now name the new tools.
- `knowledge/sources.md`: added [Gethe/wow-ui-source](https://github.com/Gethe/wow-ui-source)
  (branch `forever`) for addon API signatures.
- Tests: `intent_tools.py` added to the i18n catalogue check. The e2e test calls the intent
  tools in fr, en, enUS and enUS + fr.

### 0.7.0 — 2026-11-18
- **Quests and NPCs from QuestieDB.** The local database build now downloads the Forever
  data of [QuestieDB](https://github.com/Questie/QuestieDB) on the player's machine, at a
  pinned commit, and merges it into `forever-<locale>.sqlite` (tables `q_quests`, `q_npcs`,
  `q_objects`, `q_spawns`, `q_items`; localized names from Questie's l10n files). Never
  redistributed by this repository; files are parsed as data with `luasv.py`, never run.
  `build.py --no-questie` skips it; `python3 -m gamedata.questie` adds it to an existing
  database (`--offline`, `--force`).
- `get_quest_info` rewritten: level, required level, zone, faction/class restrictions, quest
  giver and turn-in with `/way`, objectives with where to find mobs, objects and items
  (drops, vendors), exploration points, prerequisites, next quest, breadcrumbs, and the
  character's status (done, in log, ready to turn in). Title search in the game language or
  in English. Falls back to the client quest cache without QuestieDB.
- New `find_quests`: quests the character can pick up in a zone (default: current zone)
  around its level — race, class, prerequisites, exclusive and seasonal quests checked,
  quests done or in the log removed — each with its giver and `/way`.
- New `find_npc`: where an NPC, mob or world object is (zone, `/way`, current zone first),
  level, title, and the quests it gives or receives.
- Badge `[Forever · QuestieDB]`; agent, `forever-quetes` skill, answer charter and
  `sources.md` updated. Quest log matching in `get_quest_info` fixed (`id` key).
- Tests: synthetic QuestieDB fixtures (`gamedata/tests/synthetic.py`, invented content),
  `gamedata/tests/test_questie.py`, `mcp/tests/test_questdb_tools.py`, e2e calls.

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

### 1.5.0 — 2026-11-25
- **Auction house prices captured passively.** When you search the auction house yourself,
  ForeverScribe records, per item, the lowest unit buyout, the median (3 listings or more), the
  number of listings, the quantity on sale and the time, in `ForeverScribeDB.auction`, per realm
  and faction. Classic (`AUCTION_ITEM_LIST_UPDATE`) and modern (`C_AuctionHouse`) APIs are both
  read; nothing is read in combat, large pages are read in small batches, observations older than
  30 days are purged. **It never starts a search**: it only reads what the auction house UI
  already received. `/scribe aide` and `/scribe statut` show the number of prices recorded.
- **Recipes**: each known recipe now carries its spell, its current colour (`skillType`), the
  item made, the amount made and its reagents; classic trade skill API supported as a fallback.
- Checked in game: Forever uses the modern `C_AuctionHouse` API (browse results carry
  `minPrice` and `totalQuantity`). Fixed before release: prices were silently dropped when
  `GetRealmName()` returned an empty string; the realm now falls back to the normalized name,
  then to another character of the same server, then to `?`.
- To check further in game: run `/probe hv` (ForeverProbe 0.3.0) at an auctioneer to see which
  auction house API Forever uses.

### 1.4.0 — 2026-11-18
- Mémoire des quêtes vues (schéma 1.4, rétrocompatible) : pendant le jeu, l'addon note
  pour tout le compte qui donne et qui reçoit chaque quête (PNJ, objet du monde ou objet
  du sac) avec sa position, les quêtes qu'un PNJ propose, où les objectifs avancent, le
  point de carte et le point de rendu. Comble les quêtes propres à Forever absentes de
  QuestieDB. Rien n'est lu en combat (mise en attente), pas de position en instance,
  valeurs masquées ignorées, taille bornée.
- `/scribe statut` affiche le nombre de quêtes, PNJ et objets mémorisés.
- Nouveau fichier : un **redémarrage complet du jeu** est nécessaire après la mise à jour.

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

### 0.3.0 — 2026-11-25
- `/probe hv`: lists the auction house functions and events this client has, then logs what
  arrives when you search (read-only, sellers hidden); `/probe hv stop` ends it.

### 0.1.0 — 2026-11-17
- Sonde de diagnostic : inventaire de l'API et appels de test.
