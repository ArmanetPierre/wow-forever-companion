# Base locale du jeu — schéma (`forever-<langue>.sqlite`, schéma 2)

Construite chez chaque joueur par `python3 tools/gamedata/build_db.py` (code :
`plugins/forever-companion/gamedata/`), à partir de **son** client WoW Forever, en lecture
seule. Jamais publiée : le dépôt ne contient que les scripts.

## Sources

| Donnée | Source dans le client | Remarque |
|---|---|---|
| Tables DB2 | stockage CASC (`Data/`, produit `wowf`) lu avec CascLib | décodées avec les définitions WoWDBDefs (`gamedata/wdc5.py`) |
| Correctifs Forever | `_forever_/Cache/ADB/<langue>/DBCache.bin` (« XFTH », v9) | ajoutent ou remplacent des enregistrements : objets nouveaux ou refaits, quêtes, sorts… (`gamedata/dbcache.py`) |
| Titres de quêtes | `_forever_/Cache/WDB/<langue>/questcache.wdb` | seulement les quêtes déjà vues en jeu (`gamedata/wdb.py`) |
| Version | `.build.info` (colonne Version du produit `wowf`) | |

Statut d'un correctif : 1 valide (appliqué), 2 supprimé (retire l'enregistrement),
3 invalide et 4 non public (ignorés). Pour un même (table, id), le plus récent l'emporte.

## Langue du client / Client language

- **Détection** (`gamedata/build.py`, `detect_locale`) : `--locale xxXX` si donné ; sinon
  `SET textLocale` de `_forever_/WTF/Config.wtf` ; sinon l'étiquette `xxXX text?` de
  `.build.info` ; sinon `enUS`. La langue choisie est écrite dans `meta.locale` et dans le
  nom du fichier : `forever-frFR.sqlite`, `forever-enUS.sqlite`…
- Les tables DB2 sont lues dans le stockage CASC avec le masque de cette langue (repli sur
  toutes les langues), les correctifs et le cache des quêtes dans `Cache/ADB/<langue>/` et
  `Cache/WDB/<langue>/`. Les noms (`items.name`, `quests.title`, `zones.name`…) sont donc
  ceux que le joueur voit en jeu.
- **Choix de la base par le serveur** : celle dont la langue correspond au client du perso
  (`meta.locale` de la capture), sinon la plus récente.
- `kind` et `slot_fr` sont des **colonnes d'aide en français**, quelle que soit la langue :
  l'affichage et les filtres passent par les identifiants (`class_id`, `subclass_id`,
  `inventory_type`) et sont traduits dans la langue de réponse (`lang` de l'outil).
  `source_type` (`artisanat`, `donjon`) est un code, pas un libellé.
- *EN: the build detects the client language (`--locale`, then `Config.wtf` textLocale, then
  `.build.info`, then `enUS`), names the file `forever-<locale>.sqlite` and stores it in
  `meta.locale`; names come in the client language. `kind`/`slot_fr` are French helper
  columns; display and filters use IDs and are localized per the tool's `lang`.*

## Calculs (`gamedata/stats.py`)

- **Stats** : `round(StatPercentEditor × budget / 10 000)`, budget =
  `RandPropPoints[niveau d'objet].{Good|Superior|Epic}[colonne]` selon la qualité
  (inhabituel ou moins | rare | épique) et la colonne de l'emplacement : 0 tête, torse, jambes,
  deux mains, arc ; 1 épaules, taille, pieds, mains, bijou ; 2 cou, poignets, doigt, dos,
  bouclier, main gauche tenue ; 3 armes à une main ; 4 fusil, arbalète, baguette, armes de jet.
- **Armure** : `round(ItemArmorTotal[ilvl].<matière> × ItemArmorQuality[ilvl].Qualitymod[qualité]
  × ArmorLocation[emplacement].<matière>modifier)` (les capes comptent en tissu ; boucliers :
  `ItemArmorShield[ilvl].Quality[qualité]`).
- **Armes** : DPS de base `ItemDamage<Ranged|OneHand|TwoHand|Thrown|Wand>[ilvl].Quality[qualité]`,
  dégâts moyens = DPS × vitesse ; min = arrondi inférieur de moyen × (1 − variance/2),
  max = arrondi de moyen × (1 + variance/2) ; DPS affiché = (min + max) / 2 / vitesse.
- Vérifié sur tout l'équipement capturé d'un perso de test (13 objets) : stats principales,
  PA, puissance des sorts, résistance, armure et DPS identiques à l'infobulle. Non couverts :
  objets à suffixe aléatoire (« … du sanglier ») dont les stats viennent du suffixe ; stats
  secondaires rares (crit, parade…) non vérifiées.

## Tables

| Table | Colonnes principales |
|---|---|
| `meta` | `key`, `value` : `schema_version`, `fingerprint` (version + correctifs + définitions, sert à l'idempotence), `build`, `locale`, `built_at`, `dbcache_build`, `dbcache_entries`, `counts` (JSON), `hotfixes` (JSON par table : client, ajoutés, modifiés, supprimés, indécodables), `note_loot` |
| `items` | `id`, `name`, `name_norm` (minuscules sans accents), `quality` (0 médiocre … 4 épique), `ilvl`, `req_level`, `class_id`/`subclass_id` (2 arme, 4 armure…), `kind` (Cuir, Fusil…), `inventory_type`, `slot`, `slot_fr`, `armor`, `dmg_min`, `dmg_max`, `speed`, `dps`, `str`, `agi`, `sta`, `int`, `spi`, `ap`, `rap`, `spell_power`, `stats_json` (toutes les stats calculées), `allowable_class` (masque, −1 = toutes), `bonding`, `sell_price`, `buy_price` (cuivre), `item_set`, `start_quest`, `required_skill`, `required_skill_rank`, `max_stack`, `origin` |
| `item_sources` | `item_id`, `source_type` (`artisanat`, `donjon`), `source_id`, `source_name`, `detail` |
| `spells` | `id`, `name`, `spell_level`, `origin` |
| `professions` | `id` (SkillLine), `name`, `name_norm`, `category` (11 métier, 9 secondaire) |
| `recipes` | `spell_id`, `profession_id`, `name`, `min_rank`, `yellow`, `green`, `grey` (vides dans Forever), `skill_ups`, `acquire_method`, `item_id`, `item_count`, `reagents_json` (`[{item_id, count, name}]`), `origin`, `rank_est`, `rank_source` (`client` ou `estimation` = 5 × niveau de l'objet fabriqué) |
| `zones` | `id` (AreaTable), `name`, `name_norm`, `parent_id`, `continent_id` |
| `dungeons` | `map_id`, `name`, `name_norm`, `instance_type` (1 donjon, 2 raid), `max_players`, `origin` |
| `encounters` | `id` (DungeonEncounter), `map_id`, `name`, `order_index`, `origin` |
| `dungeon_loot` | `map_id`, `encounter_id`, `item_id`, `source` (`journal`) — vide dans Forever 1.60 : le Journal des donjons n'est pas rempli dans les fichiers du client |
| `quests` | `id` (QuestV2), `title`, `title_norm`, `objectives`, `origin` (`cache` si connue seulement du cache) |

`origin` : `client` (fichiers du jeu), `modifie` (correctif du serveur qui remplace
l'enregistrement du client), `ajoute` (enregistrement absent des fichiers du client, fourni
par le serveur — pas forcément un objet nouveau dans le jeu).

Index : `items(name_norm)`, `items(inventory_type, req_level)`, `items(class_id, subclass_id)`,
`item_sources(item_id)`, `recipes(profession_id, rank_est)`, `recipes(item_id)`,
`encounters(map_id)`, `dungeon_loot(map_id)`, `dungeon_loot(item_id)`, `quests(title_norm)` ;
QuestieDB : `q_quests(name_norm)`, `q_quests(zone_id, level)`, `q_npcs(name_norm)`,
`q_objects(name_norm)`, `q_spawns(kind, id)`.

## Ce que la base ne contient pas

- **Butin des donjons** et **source des objets** (butin de monstre, récompense de quête,
  marchand) : côté serveur. Pistes : export en jeu du Journal des donjons par l'addon
  (`C_EncounterJournal`), objets vus par l'addon (récompenses, marchands).
- **Rang requis des recettes** et couleurs de difficulté : à 1 dans les fichiers ; estimés.
- **Niveau, donneur et récompenses des quêtes** : pas dans les fichiers du client (seulement
  le titre et l'objectif des quêtes déjà vues) → fournis par QuestieDB (section suivante),
  sauf les récompenses (capturées par l'addon pour les quêtes du journal).

## Quêtes et PNJ : QuestieDB (tables `q_*`)

Ajoutées par `gamedata/questie.py`, appelé à la fin de `build.py` (ou seul :
`python3 -m gamedata.questie`, depuis `plugins/forever-companion/`).

- **Source** : [QuestieDB](https://github.com/Questie/QuestieDB), base communautaire des
  quêtes de Forever (dossiers `data/Forever/` et `l10n/Forever/`). Licence non déclarée sur
  GitHub (projet Questie sous GPLv3) : **jamais copiée dans ce dépôt**. Les fichiers sont
  téléchargés chez le joueur, à une révision fixée (`QUESTIE_COMMIT`), dans
  `<données>/gamedata/.cache/questie/<commit>/`, puis lus comme des **données** avec le
  parseur Lua de `mcp/luasv.py` (jamais exécutés).
- **Fichiers** : `foreverQuestDB.lua`, `foreverNpcDB.lua`, `foreverObjectDB.lua`,
  `foreverItemDB.lua` ; traductions `lookupQuests|lookupNpcs|lookupObjects/<langue>.lua`
  (deDE, esES, esMX, frFR, koKR, ptBR, ruRU, zhCN, zhTW ; rien pour enUS, les données sont
  déjà en anglais).
- **Options** : `build.py --no-questie` pour s'en passer ; `questie.py --offline` n'utilise
  que les fichiers déjà téléchargés ; `--force` réimporte. Sans `--force`, l'import est sauté
  si `meta.questie_commit` vaut déjà la révision fixée.
- **Mise à jour** : changer `QUESTIE_COMMIT` (et la date en commentaire) après avoir relu le
  diff de QuestieDB, puis `python3 -m gamedata.questie`.

| Table | Colonnes |
|---|---|
| `q_quests` | `id`, `name` (anglais), `name_loc` (langue de la base, si traduit), `name_norm` (`anglais\|traduit`, normalisés), `req_level`, `level`, `max_level`, `races` (masque Questie : bits 0-7 races Classic, 32 Éolides Alliance, 33 Éolides Horde), `classes` (masque `1 << (classe-1)`), `objectives_text` (JSON, traduit si possible), `zone_id` (AreaTable, si > 0), `sort_id` (QuestSort, si < 0 dans Questie : métiers, fêtes…), `start_npcs`, `start_objects`, `start_items`, `end_npcs`, `end_objects` (JSON d'ids), `objectives_json` (`{creatures, objects, items: [[id, texte]], reputation, killcredit, spells}`), `trigger_json` (exploration : `{text, spawns: {zone: [[x, y]]}}`), `source_item`, `pre_group` (toutes), `pre_single` (une seule), `next_in_chain`, `exclusive_to`, `parent`, `children`, `breadcrumb_for`, `breadcrumbs`, `required_skill` (`[compétence, rang]`), `rep_reward` (`[[faction, valeur]]`), `special_flags` (1 répétable, 2 objectif d'exploration ou d'événement scripté), `quest_flags` |
| `q_npcs` | `id`, `name`, `name_loc`, `name_norm`, `subname` (titre, traduit si possible), `min_level`, `max_level`, `rank`, `zone_id`, `friendly` (`A`, `H`, `AH` ou vide = hostile), `npc_flags`, `starts`, `ends` (JSON d'ids de quêtes), `spawn_count` |
| `q_objects` | `id`, `name`, `name_loc`, `name_norm`, `zone_id`, `starts`, `ends`, `spawn_count` |
| `q_spawns` | `kind` (`npc`/`object`), `id`, `zone_id` (AreaTable), `x`, `y` (% de la carte de la zone, prêts pour `/way`) ; au plus 40 points par zone et par PNJ (répartis) |
| `q_items` | `id`, `name` (anglais), `npc_drops`, `object_drops`, `item_drops`, `vendors`, `start_quest`, `quest_rewards`, `related_quests` — seulement les objets qui ont une source |

`meta` reçoit `questie_commit`, `questie_schema`, `questie_source`, `questie_license`,
`questie_imported_at`, `questie_counts`. Les noms de zones viennent de la table `zones`
(langue du client) ; les noms d'objets de `items` (langue du client), sinon `q_items.name`.

*EN: QuestieDB (quests, NPCs, objects, item sources) is downloaded on the player's machine at a
pinned commit, parsed as data (never executed), and merged into the `q_*` tables; it is never
redistributed by this repository. Localized names come from Questie's l10n files.*

## Emplacements

- Base : `<données>/gamedata/forever-<langue>.sqlite` (défaut `~/WowForever/gamedata/`).
  Le serveur MCP la cherche dans `FOREVER_GAMEDB` (si défini, seul ce chemin compte), puis à
  côté du dossier `perso/` utilisé, puis dans `~/WowForever/gamedata/`.
- Dépendances : `<données>/gamedata/.cache/` (`casclib/` source et bibliothèque compilée,
  `wowdbdefs/` manifeste et définitions, `raw/<version>/` copies des DB2 lues).
