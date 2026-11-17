# Faisabilité — base de données locale du jeu

Statut : **étude terminée ; réalisé en 0.5.0 dans `plugins/forever-companion/gamedata/` (commande `tools/gamedata/build_db.py`).** Date : 17/11/2026.
Client testé : WoW Forever `wowf`, build **1.60.1.70938** (macOS), locale frFR.

## Verdict

**Faisable, mais en deux couches.** Les fichiers du jeu (`Data/`, format CASC) se lisent
sans problème et vite : les tables se décodent avec les définitions communautaires
WoWDBDefs, **qui couvrent déjà les builds Forever 1.60.1 jusqu'au 70938**. Mais ces tables ne
contiennent que **la base Classic**. Ce que Forever a ajouté ou modifié (objets refaits,
nouveaux objets, Journal des donjons) n'y est pas : ça arrive par les **correctifs (hotfixes)**
que le serveur envoie et que le client garde dans `_forever_/Cache/ADB/frFR/DBCache.bin`
(7,6 Mo). Lire ce fichier sort de l'autorisation actuelle : c'est le prochain point à valider.

## Preuves

Extraction des 17 tables visées depuis le stockage local : **1,3 s**, 8,4 Mo de DB2.
Décodage d'ItemSparse (19 333 objets, 16 sections) : **0,5 s** en Python pur.

| Objet attendu (ID vu en jeu) | Dans les fichiers du jeu | En jeu |
|---|---|---|
| Balle dure (3033) | **trouvé** : niv. requis 25, ilvl 30, munition (type 24), pile de 200 | identique |
| Cuirasse de pillard (6085) | présent mais **ancienne version** : « Tunique de fantassin », ilvl 13, stats Agi/Endu 2/3–1/3 | « Cuirasse de pillard », ilvl 22 → modifié par correctif |
| Fusil à canon double (2098) | **absent d'ItemSparse** (présent dans Item : arme, fusil) | ilvl 27, +3 Agi +3 For → données dans les correctifs |
| Coutelas trancheur (1937) | absent d'ItemSparse (présent dans Item : arme, épée) | idem |
| Arbalète de points dissimulés, Heaume d'Humbert | introuvables par le nom | idem |

Autres tables :

| Table | Verdict | Extrait |
|---|---|---|
| ItemSparse / Item | **Partiel** : base Classic seulement, 89 enregistrements chiffrés (clés absentes, ignorés) | 19 333 / 9 148 lignes, noms FR |
| SkillLine / SkillLineAbility + SpellName | **OK** | Travail du cuir = 165 ; 616 recettes (« Bottes en cuir cousu main », « Gilet en cuir estampé »…) ; les rangs « trivial » valent 0, à confirmer |
| AreaTable | **OK** | 1 375 zones, dont « Les Paluns », « Excavations : les Paluns » |
| QuestV2 / QuestLineXQuest | **Pauvre** : seulement les ID (6 614) et 22 liens de chaînes | pas de titres ni de récompenses |
| JournalInstance / JournalEncounter / JournalEncounterItem | **Vide dans les fichiers** (0 enregistrement) | le loot des donjons vient des correctifs ou du serveur |
| ItemEffect, Map, ChrClasses, ItemClass/SubClass | **OK** | 12 672 effets, 73 cartes |
| Cache WDB (`questcache.wdb`, `creaturecache.wdb`) | **OK, mais limité à ce que le joueur a vu** | 45 quêtes avec titre et texte FR (« Bannières de guerre »…), 679 créatures (« Meri Ironweave — Armures & boucliers ») |

Stats des objets : le client moderne ne stocke pas de valeurs fixes mais une **répartition**
(`StatPercentEditor`, ex. 6667/3333) à combiner avec le niveau d'objet et les tables de budget
(RandPropPoints, ItemDamage*). Le calcul est connu mais **reste à valider** sur des objets dont
on connaît les vraies stats en jeu.

## Chaîne d'outils retenue

| Étape | Outil | Remarque |
|---|---|---|
| Lire le stockage CASC | **CascLib** (C, licence MIT, github.com/ladislav-zezula/CascLib), compilé en bibliothèque partagée avec CMake | appelé depuis Python par `ctypes` ; ouverture `"<dossier WoW>*wowf"` ; fichiers ouverts par FileDataID |
| Trouver les FileDataID et les formats | **WoWDBDefs** (github.com/wowdev/WoWDBDefs) : `manifest.json` + `definitions/*.dbd` | couvre Forever 1.60.1 ; mis à jour par la communauté à chaque build |
| Décoder les DB2 (WDC5) | **`plugins/forever-companion/gamedata/wdc5.py`**, lecteur Python maison (bibliothèque standard) | évite .NET ; gère sections, compression bitpacked/common/pallet, tables creuses, chaînes, tableaux, relations |
| Lire les caches WDB | **`plugins/forever-companion/gamedata/wdb.py`** (maison) | en-tête de 24 octets puis (id, taille, données) |
| DBCD (C#) | non utilisé | l'installation du SDK .NET a été refusée par le système de permissions ; le lecteur Python suffit |

Prérequis par système :

| | macOS | Windows | Linux |
|---|---|---|---|
| CascLib | `cmake` + compilateur (Xcode CLT) → `casc.framework/casc` | binaire `CascLib.dll` publié par l'auteur, ou MSVC | `cmake` + gcc → `libcasc.so` |
| Python 3.9+ | oui | oui | oui |
| Dossier du jeu | `/Applications/World of Warcraft` | `C:\Program Files (x86)\World of Warcraft` | préfixe Wine |

Option à étudier pour simplifier la vie des joueurs : fournir CascLib précompilé (licence MIT,
redistribution autorisée) ou un petit lecteur CASC en Python (index locaux + BLTE), pour que
`build-db` n'exige aucune compilation.

## Ce qui manque, même avec les correctifs

- **Sources de loot hors donjon** (quel monstre lâche quoi, taux) : connues du serveur seulement.
- **Emplacement des PNJ et des monstres**, donneurs de quêtes, récompenses des quêtes
  non rencontrées : serveur seulement (ou observations de l'addon).
- **Texte des quêtes** : uniquement pour les quêtes déjà vues (cache WDB).
→ Ces trous se comblent par l'addon (récompenses, marchands, butin, Journal des donjons
via l'API en jeu) et par la mémoire de recherche.

## Risques

- **Mises à jour du client** : chaque patch change les builds et parfois les formats ; il
  faut des définitions WoWDBDefs à jour (la communauté les publie vite : le build 70938 est
  déjà couvert) et relancer `build-db`.
- **Correctifs** : `DBCache.bin` ne contient que ce que le serveur a envoyé à ce client ;
  à vérifier qu'il couvre bien tous les objets Forever (et pas seulement ceux déjà vus).
- **Sections chiffrées** : quelques dizaines d'enregistrements (contenu à venir) restent
  illisibles sans clé ; c'est voulu par Blizzard, on les ignore.
- **Conditions d'utilisation** : lecture locale, en lecture seule, de fichiers déjà présents
  sur le disque du joueur, sans interaction avec le jeu ni le serveur. La base est construite
  chez chaque joueur et **n'est jamais publiée** ; le repo ne publie que les scripts.
  `.gitignore` exclut `*.db2`, `*.wdb`, `*.sqlite*` et les dossiers de sortie.

## Plan du lot B

1. **Autorisation à obtenir** : lecture seule de `_forever_/Cache/ADB/<locale>/DBCache.bin`.
   Puis un lecteur de correctifs (format `XFTH` : en-têtes par enregistrement avec hash de
   table, ID, statut ; données au même format que la ligne DB2 creuse) qui **superpose** les
   correctifs à la base. Critère de réussite : retrouver le Fusil à canon double avec
   ilvl 27, +3 Agi +3 For.
2. **Calcul des stats** à partir de la répartition et du niveau d'objet (RandPropPoints,
   ItemDamage*), validé sur 5 objets connus.
3. **Script `build-db`** (`python3 -m gamedata build`) : détecte le jeu, extrait les tables,
   applique les correctifs, lit les caches WDB, écrit `~/WowForever/gamedata/forever-<build>.sqlite`.
   À relancer après chaque patch (le serveur MCP signale si le build du client a changé).
4. **Schéma SQLite** :
   - `items(id, name, quality, ilvl, req_level, inventory_type, class_id, subclass_id, stats_json, dps, speed, armor, source_hint)`
   - `skills(id, name)`, `recipes(spell_id, skill_id, name, min_rank, trivial_low, trivial_high, item_id)`
   - `areas(id, name, parent_id, map_id)`
   - `quests(id, title, text, level, zone, source)` (cache WDB + addon)
   - `dungeon_loot(instance, encounter, item_id)` (correctifs si présents, sinon export du
     Journal des donjons par l'addon)
   - `meta(build, built_at, sources)`
5. **Outils MCP** : `find_items(filtres)`, `get_item(id|nom)`, `find_upgrades(emplacement?, niveau_max?)`
   (filtre armure/arme portable, compare à l'équipé), `get_dungeon_loot(donjon)`,
   `get_quest_info(id|nom)`.

Effort estimé du lot B : **3 à 4 sessions de travail**, dont la plus incertaine est le
point 1 (format des correctifs) puis le point 2 (formules de stats).

## Reproduire le prototype

```bash
# Tout en une commande (CascLib, WoWDBDefs, extraction, correctifs, SQLite) :
python3 tools/gamedata/build_db.py
```
