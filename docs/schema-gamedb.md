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
`encounters(map_id)`, `dungeon_loot(map_id)`, `dungeon_loot(item_id)`, `quests(title_norm)`.

## Ce que la base ne contient pas

- **Butin des donjons** et **source des objets** (butin de monstre, récompense de quête,
  marchand) : côté serveur. Pistes : export en jeu du Journal des donjons par l'addon
  (`C_EncounterJournal`), objets vus par l'addon (récompenses, marchands).
- **Rang requis des recettes** et couleurs de difficulté : à 1 dans les fichiers ; estimés.
- **Niveau, donneur et récompenses des quêtes** : seulement le titre et l'objectif des
  quêtes déjà vues.

## Emplacements

- Base : `<données>/gamedata/forever-<langue>.sqlite` (défaut `~/WowForever/gamedata/`).
  Le serveur MCP la cherche dans `FOREVER_GAMEDB` (si défini, seul ce chemin compte), puis à
  côté du dossier `perso/` utilisé, puis dans `~/WowForever/gamedata/`.
- Dépendances : `<données>/gamedata/.cache/` (`casclib/` source et bibliothèque compilée,
  `wowdbdefs/` manifeste et définitions, `raw/<version>/` copies des DB2 lues).
