# Plan — quêtes propres à Forever (absentes de QuestieDB)

Statut : **proposition, rien n'est développé.** Diagnostic du 18/11/2026, build 1.60.1.70938,
QuestieDB `e1652ce`.

## Constat chiffré

| Source (locale, lecture seule) | Ce qu'elle a pour les quêtes Forever |
|---|---|
| **QuestieDB** (import 0.7.0) | 4 244 quêtes, **aucune avec un id ≥ 80 000**. Ses données Forever sont celles de Classic Era, adaptées à la géométrie de Forever. L'issue Questie #8303 parle d'environ 1 600 quêtes nouvelles (ids surtout ≥ 90 000) sans source connue. Aucune date annoncée. |
| **Client `QuestV2`** (CASC + correctifs) | 6 614 ids, dont **2 595 ≥ 80 000** (80 056 à 99 670). Ces lignes ne contiennent que l'id et un drapeau : ni titre, ni PNJ. |
| **Correctifs `DBCache.bin`** | `QuestPOIBlob` (166), `QuestPOIPoint` (726), `QuestObjective` (43) et `QuestV2CliTask` (1 266) sont présents, mais **tous au statut invalide ou supprimé, avec 0 octet**. Le serveur ne les publie pas. `Creature` : 346 entrées invalides. **Rien d'exploitable.** |
| **Client `QuestPOIBlob` / `QuestObjective` / `QuestLineXQuest`** | 57, 0 et 22 lignes, aucune pour les 7 quêtes. |
| **`questcache.wdb`** | 90 quêtes vues par le joueur, **dont les 7**. On en tire le titre, l'objectif, la description et le texte de fin. Ces textes nomment souvent le PNJ de rendu et le lieu. Les champs binaires ne sont pas encore décodés : cibles des objectifs, quête suivante, zone, niveau minimum, races. |
| **`creaturecache.wdb` / `gameobjectcache.wdb`** | 857 créatures et 1 134 objets vus, avec **nom par id**, sans position. Exemples : Sylessa Murmesoir 270844, Plans d'attaque 671481/83/86. |
| **Capture de l'addon** | Titre, zone, niveau, objectifs avec progression pour 6 quêtes sur 7. **Point sur la carte pour 4 sur 7** (`GetQuestsOnMap`). Ni donneur, ni receveur, ni id de PNJ. |
| **Infobulle Wowhead Forever** (`dataEnv=16`, une requête par id) | **Quête** : nom en français et en anglais, niveau, objectif, objets requis. Pas de donneur ni de coordonnées. **PNJ et objet** : zone et **coordonnées**. Exemples : Sylessa en Paluns 8,0 55,8 ; Plan d'attaque, 4 points. |

## Constat par quête (journal d’un perso de test, niveau 25, Les Paluns)

| Id | Quête | QuestieDB | Texte du cache | Objectifs | Point carte | Donneur / receveur connus |
|---|---|---|---|---|---|---|
| 98815 | Cuir des hautes-terres (donjon) | non | oui, rendu à James Halloran, port de Menethil | 0/4 peaux | non (instance) | nommé dans le texte seulement |
| 95772 | À la recherche de Lame-chantante | non | oui, Daewyn, Excavations de Whelgar | terminée | oui, 48,2 56,5 | nommé dans le texte |
| 98221 | Tiré des cendres | non | oui, capitaine Rudepoing, donjon de Menethil | 4 plans | oui, 38,5 46,0 | Rudepoing seulement s'il existe dans QuestieDB ; 3 plans sur 4 ont un id dans le cache |
| 98209 | Fleur des cieux | non | oui, Thundris Tissevent, Auberdine | terminée | non | Sylessa dans le cache des créatures, mais pas reliée à la quête |
| 98246 | Période de disette | non | oui, Howin Genteplume ; crête des Raptors, vallon des Embruns | 0/12 œufs | oui, 37,0 20,4 | les tranchegueules sont des PNJ Classic (1018, 1023), donc **positionnés par QuestieDB** |
| 98245 | Travail d'aiguille tranchegueule | non | oui, Howin Genteplume | 0/10 incisives | oui, 35,8 16,8 | idem |
| 86614 | L'argent des vagues | non | oui, rendu à la propriétaire « K. E. » | terminée | non | inconnu (quête lancée par un objet) |

**En résumé :**
- **Ce qu'on sait déjà** : le texte et les objectifs, souvent un point sur la carte, et les lieux nommés.
- **Ce qui manque** : l'**id et la position du donneur et du receveur**, la **chaîne**, et la **position des objectifs** quand ce sont des PNJ ou objets nouveaux.
- **Ce qu'aucune source locale ni QuestieDB ne fournit** : ces données se trouvent uniquement côté serveur. La seule façon fiable de les obtenir est de **les observer en jouant**.

## Approche recommandée

**Pour les quêtes nouvelles, la vraie source est ce que le joueur voit en jeu, complétée par Wowhead au cas par cas.** On n'attend pas QuestieDB : si elle ajoute ces quêtes, l'import 0.7.0 les prendra automatiquement en changeant `QUESTIE_COMMIT`.

| Lot | Contenu | Effort | Gain |
|---|---|---|---|
| **1. Exploiter l'existant** (MCP seul) | Pour une quête absente de QuestieDB, `get_quest_info` fusionne trois sources. **Le texte complet du cache** (description, objectif, fin). **Le point de carte capturé** en `/way` (à rendre si la quête est terminée). **Les PNJ et lieux nommés dans le texte**, rapprochés par nom de `q_npcs` et du cache des créatures. Exemple : les tranchegueules ont leurs positions QuestieDB. Certitude « probable » pour ces rapprochements par nom. | faible | immédiat, sur les 7 |
| **2. Mémoire des quêtes vues** (addon + MCP) | Hors combat, chaque collecteur en `pcall`, aucune automatisation : voir le détail des événements sous ce tableau. Stockage au niveau du compte, partagé par les persos. | moyen | **donneur, receveur et zones d'objectifs exacts**, de plus en plus complets à mesure qu'on joue |
| **3. Décoder `questcache.wdb`** | Lire les champs binaires : objectifs (type, id cible, quantité), quête suivante (**chaîne**), zone, niveau minimum, races et classes. Le format est vérifié par le numéro de build ; s'il ne correspond pas, on garde les textes. Les noms viennent des caches de créatures et d'objets. | moyen | chaîne et cibles d'objectifs pour toute quête vue |
| **4. Wowhead à la demande** | Une requête d'infobulle par id manquant (PNJ et objets des lots 2 et 3, quête non vue pour son nom français et anglais), seulement pour une question posée. Résultat gardé en cache dans `gamedata/.cache/wowhead/`, débit limité, User-Agent générique, rien de personnel dans l'URL. Badge `[Wowhead Forever]`. | faible | coordonnées des PNJ et objets nouveaux |
| **5. Expérimental : `/scribe quetes`** | Commande du joueur, hors combat, par petits lots : `C_QuestLog.RequestLoadQuestByID` sur la plage 80 000 à 99 999. Le jeu remplit alors son propre cache de quêtes, ce qui donne **le titre et le texte de toutes les quêtes Forever**, sans donneur. À tester d'abord sur 100 ids pour voir si le serveur ralentit les réponses. | faible à moyen | catalogue des titres pour `find_quests` |

**Détail du lot 2 : ce que l'addon observe**
- `QUEST_DETAIL` : `GetQuestID`, `UnitGUID("npc")`, d'où l'id du PNJ ou de l'objet, son nom, et la position du joueur (`C_Map.GetBestMapForUnit`, `GetPlayerMapPosition`).
- `QUEST_PROGRESS` et `QUEST_COMPLETE` : le receveur, avec sa position.
- `GOSSIP_SHOW` et `QUEST_GREETING` : les quêtes **proposées** par un PNJ, avec id, titre et niveau, avant même de les accepter (`C_GossipInfo.GetAvailableQuests`).
- Progression d'un objectif (`QUEST_LOG_UPDATE`, compteur qui augmente) : la position du joueur, au plus N points par objectif.
- Quête terminée : `C_QuestLog.GetNextWaypoint`.

**Ordre conseillé : 1, puis 2, puis 4, puis 3, puis 5.**
- **Le lot 1** sert tout de suite.
- **Le lot 2** est la seule source fiable pour le donneur et le receveur.
- **Le lot 4** donne les coordonnées des ids trouvés par le lot 2.
- **Le lot 3** ajoute la chaîne.
- **Le lot 5** reste un test.

## Impact sur le schéma (`docs/schema.md`, version mineure 1.4, rétrocompatible)

`ForeverScribeDB.questMemory`, au niveau du compte, partagé par tous les persos :

```lua
questMemory = {
  quests = { [98246] = { title = "…", level = 29,
      starts = { { kind = "npc", id = 1234, name = "…", mapId = 1437, x = 37.1, y = 20.2, at = 0 } },
      ends   = { … },
      offeredBy = { 1234 },
      objectivePoints = { [1] = { { mapId = 1437, x = 36.0, y = 18.4 } } } } },  -- 20 points au plus
  npcs = { [1234] = { name = "…", kind = "npc", points = { … } } },
}
```

Les tailles sont plafonnées et les ids ne sont jamais traduits. `sync.py` écrit le tout dans
`perso/<Utilisateur>/memoire-quetes.json`, en fusionnant les comptes.

## Outils MCP touchés (aucun outil nouveau)

- **`get_quest_info`** : ordre des sources QuestieDB, puis mémoire observée, puis cache du client, puis Wowhead. Chaque information porte son badge (`[Forever · QuestieDB]`, `[Forever · observé en jeu]`, `[Forever · cache client]`, `[Wowhead Forever]`) et sa certitude.
- **`find_quests`** : ajoute les quêtes proposées que la mémoire a relevées (`offeredBy`) dans la zone, et le catalogue du lot 5.
- **`find_npc`** : cherche aussi dans les PNJ observés et dans le cache des créatures, avec en complément les coordonnées Wowhead mises en cache.

## Tests

- **Addon** : `wow_mock.lua` simule `QUEST_DETAIL`, `GOSSIP_SHOW`, `QUEST_COMPLETE`, la progression des objectifs, un combat (aucune capture) et une valeur secrète. Les fixtures restent fictives (Brannok), en frFR et en enUS.
- **Python** :
  - fusion des sources et priorité entre badges ;
  - décodage d'un enregistrement `questcache.wdb` **synthétique** ;
  - lecture d'une infobulle JSON **écrite à la main** ;
  - aucun accès réseau dans les tests.
- **Banc d'essai** : nouveau scénario « où rendre *Cuir des hautes-terres* ? », qui ne doit pas déclencher de recherche web.

## Risques

- **Valeurs secrètes de l'API 12.x.** En combat ou en instance, certains GUID et positions sont masqués. Il faut tester `issecretvalue` et ne rien écrire si la valeur est masquée.
- **Pas de position en donjon.** Les quêtes de donjon, comme 98815, n'auront pas de point. On garde alors le nom du donjon.
- **Format du cache selon le build.** Le décodage du lot 3 doit être protégé par le numéro de build. S'il ne correspond pas, on retombe sur les textes.
- **Wowhead.** Faible volume, à la demande seulement, résultats en cache, aucune aspiration. Si l'accès est refusé, on abandonne sans réessayer en boucle.
- **Lot 5.** Le serveur peut ralentir ou couper les requêtes : petits lots, arrêt dès qu'une réponse manque.
- **Redistribution.** La mémoire observée reste dans le dossier du joueur. Un partage entre amis, hors du dépôt, sera à décider plus tard. Rien de Blizzard, de Questie ni de Wowhead n'entre dans le dépôt.
- **Fonctions non listées par la sonde.** `GetLootSourceInfo`, `GetTitleText` et `GetObjectiveText` n'y apparaissent pas : à vérifier avec ForeverProbe avant le lot 2.
