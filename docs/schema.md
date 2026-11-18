# Schéma des données ForeverScribe — version 1.4

> **1.4 (addon 1.4.0)** : ajout rétrocompatible `ForeverScribeDB.questMemory`, la
> **mémoire des quêtes vues**, au niveau du compte et commune à tous les persos : donneurs
> et receveurs avec leur position, quêtes proposées par un PNJ, positions où les objectifs
> avancent, point de carte et point de rendu. `schemaMinor = 4`. Voir la section 7.

> **1.3 (addon 1.3.0)** : client anglais (enUS) et toute autre langue. Ajouts
> rétrocompatibles de clés **non traduites** à côté des libellés traduits : index
> `raceFile`, `locale` ; `quests.list[].tagId` ; `reputations.list[].standingToken`,
> `categoryId` ; `bags.ammo.byId` ; `recipes[].professionName` ; `spells.lines[].index`,
> `iconId`, `specId`, `isGuild` ; `pet.current.loyaltyLevel`. `money.text` suit la langue
> du client. `schemaMinor = 3`. Voir la section 6 « Langue du client ».

> **1.2 (addon 1.2.0)** : ajout rétrocompatible `quests.list[].rewards` (récompenses de
> quête : objets au choix, objets fixes, argent, XP, réputation, sorts). `schemaMinor = 2`.

> **1.1 (addon 1.1.0)** : ajouts rétrocompatibles pour la synchro en un geste —
> `schemaMinor`, `settings` (compte) et `meta.lastSyncRequestAt`, `meta.lastSyncReason`,
> `meta.writtenAt` (perso). `schemaVersion` reste 1 : un parseur v1 lit toujours tout.

Contrat entre l'addon **ForeverScribe** (en jeu) et le futur serveur **forever-mcp**
(sur l'ordinateur). Toute évolution incompatible change `schemaVersion`.

- Source de vérité des formes de retour : la sonde du 17/11/2026
  (résultats anonymisés dans [`api-inventaire.md`](api-inventaire.md)).
- Exemple complet généré par le test hors jeu :
  [`addon/tests/fixtures/character.json`](../addon/tests/fixtures/character.json) et
  sa version au format du jeu
  [`character_SavedVariables_ForeverScribe.lua`](../addon/tests/fixtures/character_SavedVariables_ForeverScribe.lua).
  Le même perso vu par un client anglais :
  [`character.enUS.json`](../addon/tests/fixtures/character.enUS.json) et
  [`character_SavedVariables_ForeverScribe.enUS.lua`](../addon/tests/fixtures/character_SavedVariables_ForeverScribe.enUS.lua).
  Les valeurs de Brannok y sont réelles sauf talents détaillés, banque, recettes,
  2ᵉ métier et contenu des sacs, inventés pour le test.
- Contrôle automatique : [`addon/tests/schema_spec.lua`](../addon/tests/schema_spec.lua).

## 1. Fichiers sur le disque

Le jeu écrit les fichiers au `/reload`, à la déconnexion ou en quittant. Jamais pendant
le jeu.

| Variable | Portée | Fichier |
|---|---|---|
| `ForeverScribeDB` | compte (index léger de tous les persos) | `WTF/Account/<COMPTE>/SavedVariables/ForeverScribe.lua` |
| `ForeverScribeCharDB` | personnage (état complet) | `WTF/Account/<COMPTE>/<DOSSIER_ROYAUME>/<Nom>-<Suffixe>/SavedVariables/ForeverScribe.lua` |

Exemple pour Brannok sur ce Mac :
```
/Applications/World of Warcraft/_forever_/WTF/Account/123456789#1/SavedVariables/ForeverScribe.lua
/Applications/World of Warcraft/_forever_/WTF/Account/123456789#1/93/Brannok-Durn/SavedVariables/ForeverScribe.lua
```
`93` est le dossier de royaume créé par le client ; il ne correspond pas au `realmId`
(1234). Le parseur doit parcourir `WTF/Account/*/*/*/SavedVariables/ForeverScribe.lua`
sans supposer son nom.

Format : fichier Lua `NomVariable = { ["clé"] = valeur, ... }`, encodage UTF-8. Le
client Windows écrit des fins de ligne CRLF. Les nombres décimaux sont écrits en pleine
précision. **Une table vide s'écrit `{}`** : quand une liste est attendue, traiter `{}`
comme une liste vide.

## 2. Identification (multi-joueurs, multi-persos)

| Niveau | Clé | Exemple |
|---|---|---|
| Joueur (humain) | dossier du compte `WTF/Account/<COMPTE>` → rattaché à un prénom côté ordinateur | `123456789#1` → « Alex » |
| Personnage | `meta.guid` = `UnitGUID("player")` | `Player-1234-0A1B2C3D` |
| Libellé affiché | `Nom-Suffixe · Région · Ruleset` | `Brannok-Durn · EU · PvP` |
| Repli si GUID absent | `region` + `name` + `suffix` | `EU/Brannok/Durn` |

Forever n'a pas de royaumes nommés : `GetRealmName()` renvoie un nom technique
(`CAMWOW EU4 Realm 6 PvP`) et `UnitName("player")` renvoie le nom et un **suffixe**
(`Durn`), le même que dans le nom du dossier WTF.

### Algorithme du ruleset (`identity.ruleset`)

1. `C_GameRules.IsHardcoreActive()` vrai → `"Hardcore"`.
2. Sinon, nom de royaume en minuscules sans espaces, tirets ni soulignés ; premier
   suffixe reconnu : `rppvp` → `"RP-PvP"`, `pvp` → `"PvP"`, `rp` → `"RP"`,
   `pve` / `normal` → `"Normal"`, `hardcore` / `hc` → `"Hardcore"`.
3. Sinon `"inconnu"`.

Les valeurs (`"PvP"`, `"Normal"`…, et `"inconnu"`) sont des **jetons fixes**, identiques
quelle que soit la langue du client : `GetRealmName()` renvoie le nom technique du
royaume, qui n'est pas traduit (`CAMWOW EU4 Realm 6 PvP` en frFR comme en enUS).
Le repli reste `"inconnu"` (pas `"unknown"`) pour ne pas casser les lecteurs existants.

`identity.rulesetSource` indique la règle appliquée. Seul `PvP` est confirmé par la
sonde ; les suffixes Normal, RP et Hardcore sont **à vérifier**.
`forever.allowedRolesets` (API `C_Roleset`) est capturé brut pour affiner cette règle
plus tard.

## 3. `ForeverScribeDB` (compte)

```lua
ForeverScribeDB = {
  schemaVersion = 1,              -- number
  schemaMinor = 4,                -- number (1.1 ; 2 depuis 1.2 ; 3 depuis 1.3 ; 4 depuis 1.4)
  addonVersion = "1.4.0",         -- string
  settings = {                    -- réglages de l'addon (1.1), facultatif
    showButton = true,            -- bouton de la minicarte affiché
    buttonAngle = 215,            -- position du bouton autour de la minicarte (degrés)
  },
  characters = {                  -- GUID -> entrée d'index
    ["Player-1234-0A1B2C3D"] = {
      name = "Brannok", suffix = "Durn",
      realm = "CAMWOW EU4 Realm 6 PvP", realmId = 1234, region = "EU", ruleset = "PvP",
      race = "Nain", raceFile = "Dwarf",      -- raceFile : 1.3, non traduit
      class = "Chasseur", classFile = "HUNTER", faction = "Alliance",
      level = 25, zone = "Les Paluns",
      locale = "frFR",                        -- 1.3 : langue du client à la dernière capture
      lastCapture = 1794909855,              -- epoch (secondes)
      lastCaptureISO = "2026-11-17T10:04:15Z" -- UTC
    },
  },
  questMemory = { … },            -- 1.4 : mémoire des quêtes vues (section 7), facultatif
}
```

## 4. `ForeverScribeCharDB` (personnage)

Une clé par **domaine**. Un domaine absent = jamais capturé. Les horodatages sont des
epochs en secondes (`time()`, UTC) ; `*ISO` en UTC.

### 4.1 `meta`

| Champ | Type | Description |
|---|---|---|
| `schemaVersion` | number | 1 |
| `addonVersion` | string | version de l'addon |
| `guid` | string | identifiant du perso |
| `locale` | string | langue du client : `frFR`, `enUS`, `deDE`… (dit dans quelle langue sont les libellés) |
| `build` | table | `{ version = "1.60.1", build = "70938", date = "Nov 12 2026", interface = 16001 }` |
| `wowProject` | number | 18 = Forever |
| `capturedAt` / `capturedAtISO` | number / string | dernière capture, tous domaines confondus |
| `domainsUpdatedAt` | table | domaine → epoch de sa dernière capture réussie (**fraîcheur par domaine**) |
| `errors` | table | domaine → `{ message, at }` si le collecteur a planté (données précédentes conservées) |
| `missing` | table | domaine → liste des fonctions de l'API absentes du client |
| `callErrors` | table | domaine → liste `"fonction : message"` des appels en erreur (domaine quand même capturé) |
| `schemaMinor` | number | 4 (1 depuis 1.1, 2 depuis 1.2, 3 depuis 1.3, 4 depuis 1.4) |
| `lastSyncRequestAt` | number? | epoch de la dernière synchro demandée (1.1) |
| `lastSyncReason` | string? | origine de cette synchro : `touche`, `commande` (`/sync`, `/scribe sync`), `bouton` (minicarte) ou `deconnexion` (déconnexion, sortie du jeu ou `/reload` tapé à la main) (1.1). Jetons fixes, jamais traduits |
| `writtenAt` | number? | epoch du dernier `PLAYER_LOGOUT`, c.-à-d. de la dernière écriture du fichier par le jeu (1.1) |

Côté serveur : `writtenAt` est la meilleure mesure de fraîcheur du fichier ; une raison
autre que `deconnexion` signifie que le joueur a synchronisé exprès (données à jour au
moment de la question).

### 4.2 Domaines

Colonnes : **Déclencheurs** = événements qui relancent la capture (regroupés, 2 s plus
tard, jamais en combat). **Connexion** = capturé ~4 s après la connexion.
**/reload** = recapturé à la déconnexion et au `/reload` (domaines légers).
**Conservé** = si la donnée n'est pas lisible (fenêtre fermée), la valeur précédente
est gardée.

| Domaine | Déclencheurs | Connexion | /reload | Conservé |
|---|---|---|---|---|
| `identity` | `PLAYER_GUILD_UPDATE`, `PLAYER_LEVEL_UP` | oui | oui | — |
| `forever` | — | oui | — | — |
| `progression` | `PLAYER_XP_UPDATE`, `PLAYER_LEVEL_UP`, `UPDATE_EXHAUSTION`, `PLAYER_UPDATE_RESTING`, `TIME_PLAYED_MSG` | oui | oui | `timePlayed` |
| `position` | `ZONE_CHANGED*`, `PLAYER_ENTERING_WORLD`, `HEARTHSTONE_BOUND` | oui | oui | — |
| `stats` | `UNIT_STATS`, `UNIT_ATTACK_POWER`, `UNIT_RANGED_ATTACK_POWER`, `UNIT_DAMAGE`, `UNIT_RANGEDDAMAGE`, `UNIT_ATTACK_SPEED`, `UNIT_RESISTANCES`, `UNIT_MAXHEALTH`, `UNIT_MAXPOWER`, `PLAYER_EQUIPMENT_CHANGED` | oui | oui | — |
| `equipment` | `PLAYER_EQUIPMENT_CHANGED`, `UPDATE_INVENTORY_DURABILITY`, `GET_ITEM_INFO_RECEIVED` | oui | — | — |
| `talents` | `TRAIT_CONFIG_UPDATED`, `PLAYER_TALENT_UPDATE`, `ACTIVE_TALENT_GROUP_CHANGED`, `ACTIVE_PLAYER_SPECIALIZATION_CHANGED`, `PLAYER_LEVEL_UP` | oui | — | — |
| `spells` | `LEARNED_SPELL_IN_SKILL_LINE`, `LEARNED_SPELL_IN_TAB`, `PLAYER_LEVEL_UP` | oui | — | — |
| `quests` | `QUEST_LOG_UPDATE`, `QUEST_ACCEPTED`, `QUEST_REMOVED`, `QUEST_TURNED_IN`, `UNIT_QUEST_LOG_CHANGED`, `ZONE_CHANGED_NEW_AREA`, `GET_ITEM_INFO_RECEIVED`/`ITEM_DATA_LOAD_RESULT` (objets de récompense en attente) | oui | — | — |
| `questsCompleted` | `QUEST_TURNED_IN` | oui | — | — |
| `professions` | `SKILL_LINES_CHANGED`, `CHAT_MSG_SKILL`, `TRADE_SKILL_SHOW` | oui | — | — |
| `recipes` | `TRADE_SKILL_SHOW`, `TRADE_SKILL_LIST_UPDATE`, `NEW_RECIPE_LEARNED` | non | — | **oui, par métier** |
| `bags` | `BAG_UPDATE` (seul le sac modifié est relu), `PLAYER_EQUIPMENT_CHANGED` | oui | oui | — |
| `bank` | ouverture de la banque, `PLAYERBANKSLOTS_CHANGED` | non | — | **oui** |
| `money` | `PLAYER_MONEY` | oui | oui | — |
| `pet` | `UNIT_PET`, `UNIT_HAPPINESS`, `UNIT_LEVEL`, `UNIT_PET_EXPERIENCE`, `PET_UI_UPDATE`, `PET_BAR_UPDATE`, `PET_STABLE_UPDATE` | oui | oui | `lastSeen` |
| `reputations` | `UPDATE_FACTION`, `QUEST_TURNED_IN` | oui | — | — |
| `currencies` | `CURRENCY_DISPLAY_UPDATE` | oui | — | — |
| `group` | `GROUP_ROSTER_UPDATE` | oui | oui | — |
| `buffs` | — | oui | oui | — |
| `collections` | `NEW_MOUNT_ADDED`, `ACHIEVEMENT_EARNED` | oui | — | — |

`/scribe` capture tous les domaines d'un coup (y compris `recipes` et `bank`, qui
gardent leur valeur si la fenêtre est fermée).

### 4.3 Contenu des domaines

Exemples tirés de la fixture (valeurs réelles de Brannok sauf mention).

**`identity`**
```lua
{ guid = "Player-1234-0A1B2C3D", name = "Brannok", suffix = "Durn",
  realm = "CAMWOW EU4 Realm 6 PvP", realmNormalized = "CAMWOWEU4Realm6PvP", realmId = 1234,
  region = "EU", regionId = 3, ruleset = "PvP", rulesetSource = "GetRealmName",
  hardcore = false, gameMode = 1, warMode = false,
  race = "Nain", raceFile = "Dwarf", raceId = 3,
  class = "Chasseur", classFile = "HUNTER", classId = 3,
  sex = "male",                       -- "male" | "female" | "unknown"
  faction = "Alliance", factionLocalized = "Alliance", level = 25,
  guild = nil,                        -- ou { name, rank, rankIndex }
  expansionLevel = 0 }
```

**`forever`** : valeurs brutes des API propres à Forever, formes non encore connues
(`experiencePreset`, `selfFoundAllowed`, `gameModeDisplay`, `gameModeRecordId`,
`isStandard`, `allowedRolesets`, `blockedRolesets`).

**`progression`**
```lua
{ level = 25, maxLevel = 60, xp = 27088, xpMax = 34000, xpRested = 912,
  restState = { id = 1, name = "En forme", multiplier = 2 },
  isResting = false, xpDisabled = false,
  timePlayed = { total = 173365, level = 7481, at = 1794909897 } }  -- secondes
```

**`position`** : coordonnées en pourcentage de la carte (0-100, 1 décimale), prêtes
pour `/way`.
```lua
{ mapId = 1437, mapName = "Les Paluns", mapType = 3, parentMapId = 1415,
  parentMapName = "Royaumes de l'est", zone = "Les Paluns", realZone = "Les Paluns",
  subZone = "Port de Menethil", x = 9.5, y = 58.3, bind = "Forgefer",
  instance = { name = "Royaumes de l'est", type = "none", difficultyId = 0,
               difficultyName = "", inInstance = false } }
```

**`stats`**
```lua
{ primary = { strength = { base = 48, effective = 48, posBuff = 15, negBuff = 0 },
              agility = {…}, stamina = {…}, intellect = {…}, spirit = {…} },
  health = 922, power = { max = 991, type = 0, token = "MANA" },
  melee = { attackPower = 233, attackPowerBase = 168, attackPowerPos = 65, attackPowerNeg = 0,
            minDamage = 62.3, maxDamage = 84.3, speed = 2.3, dps = 31.9,
            offhandMinDamage = 0, offhandMaxDamage = 0, offhandSpeed = nil, damageModPct = 1,
            crit = 7.4, hit = 1, dodge = 7.17, parry = 4.64, block = 0 },
  ranged = { attackPower = 233, attackPowerBase = 193, attackPowerPos = 40, attackPowerNeg = 0,
             speed = 2.09, minDamage = 76.3, maxDamage = 96.3, dps = 41.3, damageModPct = 1,
             crit = 7.72, hit = 1, usesAmmo = true, ammoNeeded = true },
  spell = { crit = 9.14 }, manaRegen = { base = 14, casting = 0 },
  armor = { base = 190, effective = 780, total = 780, bonus = 590 },
  resistances = { holy = 5, fire = 5, nature = 5, frost = 5, shadow = 5, arcane = 5 },
  defense = 116, itemLevel = { overall = 18.4, equipped = 18.1 } }
```
- `attackPower` = base + bonus + malus, comme la fiche de personnage du jeu.
  **À vérifier en jeu** : comparer à la fiche (touche C).
- `dps` = moyenne des dégâts ÷ vitesse : coups blancs uniquement, sans crit ni
  capacités.
- `crit`, `dodge`, `parry`, `block` en % ; `hit` = bonus de toucher en %.

**`equipment`**
```lua
{ slots = {                           -- clé = nom d'emplacement du jeu
    RangedSlot = { slotId = 18, itemId = 2098, name = "Fusil à canon double",
      link = "|cnIQ3:|Hitem:2098::::::::25:1485:::::::::|h[Fusil à canon double]|h|r",
      quality = 3, itemLevel = 27, requiredLevel = 22, type = "Arme", subType = "Fusils",
      equipLoc = "INVTYPE_RANGEDRIGHT", classId = 2, subclassId = 3, sellPrice = 3020,
      dps = 13.26,                    -- DPS de l'arme (armes seulement)
      stats = { ITEM_MOD_AGILITY_SHORT = 3, ITEM_MOD_STRENGTH_SHORT = 3 },
      durability = { current = 69, max = 70 },
      tooltip = { "Fusil à canon double", "Lié quand équipé", "Distance | Fusil", … },
      pending = nil },               -- true si les infos de l'objet n'étaient pas encore en cache
    MainHandSlot = {…}, … },
  repairCost = 9,                     -- en pièces de cuivre, tous emplacements
  tempEnchants = { mainHand = nil, offHand = nil } }  -- { expiresInMs, charges, enchantId }
```
Emplacements : `HeadSlot`, `NeckSlot`, `ShoulderSlot`, `ShirtSlot`, `ChestSlot`,
`WaistSlot`, `LegsSlot`, `FeetSlot`, `WristSlot`, `HandsSlot`, `Finger0Slot`,
`Finger1Slot`, `Trinket0Slot`, `Trinket1Slot`, `BackSlot`, `MainHandSlot`,
`SecondaryHandSlot`, `RangedSlot`, `TabardSlot`. Un emplacement vide est absent.
Les clés de `stats` sont les constantes du jeu (`ITEM_MOD_*_SHORT`, `RESISTANCE0_NAME`
= armure…). `tooltip` contient le texte complet de la bulle d'aide ; deux colonnes y sont
jointes par `" | "`.

**`talents`** (système `C_Traits` ; nœuds pris seulement)
```lua
{ specIndex = 1, specId = 1485, specName = "Chasseur", role = "DAMAGER", numSpecs = 1,
  activeSpecGroup = 1, hasEarnedPoint = true,
  configId = 3758979, configName = "Chasseur", treeId = 1091, nodeCount = 52,
  currencies = { { id = 3001, available = 10, max = 16, spent = 6 } },   -- inventé
  unspent = 10, spent = 6,
  nodes = { { nodeId = 104960, rank = 3, maxRank = 5, entryId = 500, spellId = 19151,
              name = "Tir amélioré", posX = 100, posY = 200 }, … } }        -- inventé
```
**À vérifier en jeu** : `C_Traits.GetNodeInfo` et `GetTreeCurrencyInfo` n'ont pas été
sondés.

**`spells`** : livre de sorts par ligne. `subName` contient le rang (`"Rang 2"`) quand
il existe. 1.3 : `index` (position dans le livre, 1 = Général), `iconId`, `specId` et
`isGuild` ne sont pas traduits ; `name` l'est.
```lua
{ lines = { { name = "Maîtrise des bêtes", index = 2, iconId = nil, specId = nil,
              spells = { { spellId = 13165, name = "Aspect du faucon", subName = "Rang 2",
                           passive = nil, offSpec = nil, itemType = 1 }, … } }, … } }
```

**`quests`**
```lua
{ count = 40, max = 20, trivialRange = 6, dailyCompleted = 0,
  list = { { id = 275, title = "Ennemis du port", category = "Les Paluns",  -- en-tête du journal
             level = 25, difficultyLevel = 25, suggestedGroup = nil, frequency = 0,
             complete = false, failed = nil, questType = 0, tag = nil,      -- ex. "JcJ" (traduit)
             tagId = nil,                                                   -- 1.3 : ex. 41 (JcJ), non traduit
             isTask = nil, isOnMap = true, rewardFavor = nil,
             position = { mapId = 1437, x = 23, y = 28.5 },                 -- si sur la carte actuelle
             objectives = { { text = "Insigne de la Confrérie : 0/3", type = "item",
                              done = false, have = 0, need = 3 } },
             rewards = {                                                     -- 1.2, voir ci-dessous
               money = 900, xp = 1800,
               choices = { { itemId = 9001, name = "Arc des marais", link = "|cnIQ2:|Hitem:9001…|h[Arc des marais]|h|r",
                             quality = 2, itemLevel = 26, requiredLevel = 21, equipLoc = "INVTYPE_RANGED",
                             type = "Arme", subType = "Arcs", classId = 2, subclassId = 2,
                             dps = 14.8, stats = { ITEM_MOD_AGILITY_SHORT = 2 }, usable = true,
                             count = nil, sellPrice = 1500, pending = nil }, … },
               items = { … },                                                -- objets reçus d'office (même forme)
               factions = { { factionId = 47, name = "Forgefer", amount = 250 } },
               spells = { { spellId = 1234, name = "…" } },
               pending = nil,                                                -- true : un objet n'était pas en cache
               readAt = 1794910326 } }, … } }
```
**`rewards`** (1.2) : lu une seule fois par quête puis réutilisé (les récompenses ne changent
pas). Les objets au choix et leurs liens dépendent de la quête **sélectionnée** dans le
journal : l'addon la sélectionne (`C_QuestLog.SetSelectedQuest`) puis restaure la sélection
du joueur. Si le journal de quêtes est ouvert à l'écran, il ne touche à rien et `rewards`
reste absent jusqu'à la capture suivante. Un objet pas encore en cache donne
`pending = true` : la quête est relue à l'arrivée des données (`GET_ITEM_INFO_RECEIVED`,
`ITEM_DATA_LOAD_RESULT`). Un perso capturé par une version antérieure n'a pas `rewards`.
`position` n'est connue que pour les quêtes visibles sur la carte actuelle ou sa carte
parente. Le texte d'un objectif peut arriver sans le nom de l'objet (` : 0/3`) quand
l'objet n'est pas en cache ; l'addon tente alors `GetQuestLogLeaderBoard`.

**`questsCompleted`** : `{ count = 195, ids = { 19, 20, 34, … } }` (IDs triés).

**`professions`**
```lua
{ professions = { { slot = "primary1", name = "Travail du cuir", skillLineId = 165,
                    rank = 106, max = 150, modifier = 0, specializationIndex = -1,
                    skillLineName = "Travail du cuir", numAbilities = 1 }, … },
  -- slot : primary1 | primary2 | archaeology | fishing | cooking | firstAid
  skills = { { name = "Maîtrise des bêtes", skillId = 50, category = "Compétences de classe",
               rank = 1, max = 1, modifier = 0, temp = 0, abandonable = nil }, … } }
```

**`recipes`** (conservé ; une entrée par métier ouvert au moins une fois)
```lua
{ ["Travail du cuir"] = { professionId = 165, professionName = "Travail du cuir",  -- 1.3
    skillLevel = 106, maxSkillLevel = 150,
    capturedAt = 1794909897,
    recipes = { { id = 2149, name = "…", learned = true,
                  difficulty = 3,     -- 0 optimale (orange) · 1 moyenne (jaune) · 2 facile (vert) · 3 grise
                  skillUps = 1, craftable = true, available = 0, categoryId = 10 }, … } } }
```
La clé est le nom du métier **dans la langue du client** (conservée pour compatibilité).
Identifier un métier par `professionId` (= `skillLineId` de `professions`). Si le joueur
change la langue du client, l'addon remplace l'ancienne entrée du même `professionId` à
la prochaine ouverture du métier ; d'ici là, deux clés peuvent coexister : garder celle
dont `capturedAt` est le plus récent.

**`bags`** / **`bank`**
```lua
{ containers = {                      -- clé = ID du conteneur en texte ("0".."4", banque "-1", "5".."11")
    ["1"] = { id = 1, name = "Petite giberne", slots = 10, free = 8,
              family = 2,             -- type de sac (carquois / giberne), 0 = sac normal
              items = { { slot = 1, itemId = 2516, name = "Balles légères", link = "…",
                          count = 200, quality = 1, bound = nil, noValue = nil,
                          classId = 6, subclassId = 3 }, … } }, … },
  totalSlots = 36, freeSlots = 31,
  ammo = { total = 550,
          items = { ["Balles légères"] = 350, ["Balles lourdes"] = 200 },  -- par nom (traduit)
          byId = { ["2516"] = 350, ["2519"] = 200 } },                    -- 1.3 : par ID d'objet
  capturedAt = 1794909897 }           -- bank seulement
```
Munitions = objets de classe 6 (Projectile) dans les sacs ; l'emplacement de munitions
n'existe pas dans Forever.

**`money`** : `{ copper = 24016, text = "2 po 40 pa 16 pc" }` — `text` suit la langue du
client depuis 1.3 (`"2g 40s 16c"` en anglais) : calculer avec `copper`.

**`pet`**
```lua
{ hasPetUI = true, active = true,
  current = { name = "Félin", level = 24, family = "Félin", familyId = 2,
              xp = 2475, xpMax = 7925,
              happiness = { level = 3, damagePct = 125, loyaltyRate = 20 },  -- 1 mécontent · 2 content · 3 heureux
              loyalty = "(Niveau de loyauté 6) Meilleur ami",
              loyaltyLevel = 6,                                                -- 1.3 : premier nombre de loyalty
              trainingPoints = { total = 120, spent = 76, available = 44 },
              food = { "Viande", "Poisson" },
              abilities = { { spellId = 17253, name = "Morsure", subName = "Rang 3", itemType = 3 }, … },
              talentTree = nil },
  lastSeen = { … même forme que current … }, lastSeenAt = 1794909897,  -- quand le familier est renvoyé
  stable = { active = { { slot = 1, name = "Félin", family = "Félin", level = 24, loyaltyLevel = 6,
                          loyaltyName = "…", happiness = 3, exotic = nil,
                          specialization = "Par défaut", petNumber = 1412027 } },
             stabled = { … } } }
```

**`reputations`**
```lua
{ list = { { id = 69, name = "Darnassus", category = "Alliance", categoryId = 469,  -- categoryId : 1.3
             reaction = 5, standing = "Amical",
             standingToken = "FRIENDLY",   -- 1.3 : HATED HOSTILE UNFRIENDLY NEUTRAL FRIENDLY HONORED REVERED EXALTED
             value = 4886, min = 3000, max = 9000,
             progress = "1886/6000", atWar = nil, watched = nil }, … },
  major = { { id = 2800, name = "…", renownLevel = 1, renownXp = 120, renownXpMax = 2500,
              unlocked = true } } }
```
L'addon déplie un instant les catégories repliées pour tout lire, puis les replie.

**`currencies`** : `{ list = { { id = 1901, name = "…", category = "Divers", quantity = 3,
max = nil, weekly = nil } } }`

**`group`** : `{ inGroup = true, inRaid = false, size = 2, members = { { name, class
(classFile), level, role } } }` (sans le joueur lui-même).

**`buffs`** : `{ list = { { name = "Aspect du faucon", spellId = 13165, stacks = nil,
remaining = nil (permanent) | secondes, fromPlayer = true } } }`

**`collections`** : `{ mountsOwned, mountsInJournal, achievementsCompleted,
achievementPoints, petsOwned }` (compteurs seulement).

## 5. Règles pour le parseur (étape 3)

- Lire `ForeverScribeDB` pour l'index, puis chaque `ForeverScribeCharDB` trouvé sous le
  compte ; rattacher le fichier au perso par `meta.guid`.
- Un champ `nil` n'est pas écrit dans le fichier : tout champ peut manquer.
- Fraîcheur : `meta.domainsUpdatedAt[domaine]`, à comparer à l'heure de l'ordinateur
  (epoch UTC des deux côtés).
- `meta.errors`, `meta.missing` et `meta.callErrors` sont à remonter tels quels : ils
  disent ce qui n'a pas pu être lu.
- Ne jamais écrire dans ces fichiers : le jeu les réécrit à chaque déconnexion.
- Ne jamais baser une logique sur un libellé traduit : utiliser les clés de la section 6.

## 6. Langue du client (1.3)

L'addon fonctionne avec un client dans n'importe quelle langue. Les **messages** (chat,
`/scribe help`, infobulle, libellé du raccourci) sont en anglais par défaut et en
français pour un client `frFR` (`Locales.lua`). Les **données** ne dépendent jamais de la
langue pour leur structure : les libellés sont recopiés tels que le jeu les donne, et
chaque libellé utile a une clé non traduite à côté.

`meta.locale` (et `characters[guid].locale` dans l'index) dit dans quelle langue sont les
libellés. Les jetons propres à l'addon (`ruleset`, `lastSyncReason`, `sex`, `slot` des
métiers, `role`, noms d'emplacements `*Slot`, clés `ITEM_MOD_*` des stats) sont fixes.

| Domaine | Libellé traduit (affichage seulement) | Clé à utiliser pour la logique |
|---|---|---|
| identity | `race`, `class`, `factionLocalized` | `raceFile` / `raceId`, `classFile` / `classId`, `faction` |
| identity | `ruleset` | jeton fixe (voir § 2) |
| progression | `restState.name` | `restState.id` |
| position | `zone`, `realZone`, `subZone`, `mapName`, `parentMapName`, `bind`, `instance.name` | `mapId`, `parentMapId`, `instance.type` |
| equipment, rewards, sacs | `name`, `type`, `subType`, `tooltip`, `link` (texte entre crochets) | `itemId`, `classId`, `subclassId`, `equipLoc`, clés de `stats` |
| talents | `specName`, `configName`, `nodes[].name` | `specId`, `role`, `nodeId`, `spellId` |
| spells | `lines[].name`, `name`, `subName` | `lines[].index`, `iconId`, `specId`, `spellId` |
| quests | `title`, `category`, `tag`, `objectives[].text` | `id`, `tagId`, `objectives[].type/have/need` |
| professions | `name`, `skillLineName`, `skills[].name`, `skills[].category` | `skillLineId`, `skills[].skillId`, `slot` |
| recipes | clé de la table, `professionName`, `recipes[].name` | `professionId`, `recipes[].id` |
| bags | `containers[].name`, `ammo.items` (clés) | `containers[].family`, `ammo.byId` |
| money | `text` | `copper` |
| pet | `family`, `loyalty`, `food`, `abilities[].name`, `stable[].specialization` | `familyId`, `loyaltyLevel`, `happiness.level`, `spellId` |
| reputations | `name`, `category`, `standing` | `id`, `categoryId`, `reaction`, `standingToken` |
| currencies | `name`, `category` | `id` |
| buffs | `name` | `spellId` |
| group | `name` | `class` (= `classFile`), `role` |
| questMemory (compte) | `titles[locale]`, `names[locale]` | ids de quête, de PNJ, d'objet, `kind`, `via`, `mapId`, `x`, `y` |

Exemple de valeurs pour le même perso :

| Champ | frFR | enUS |
|---|---|---|
| `identity.race` / `raceFile` | `Nain` / `Dwarf` | `Dwarf` / `Dwarf` |
| `identity.class` / `classFile` | `Chasseur` / `HUNTER` | `Hunter` / `HUNTER` |
| `identity.realm` / `ruleset` | `CAMWOW EU4 Realm 6 PvP` / `PvP` | idem / `PvP` |
| `position.zone` / `mapId` | `Les Paluns` / 1437 | `Wetlands` / 1437 |
| `professions[1].name` / `skillLineId` | `Travail du cuir` / 165 | `Leatherworking` / 165 |
| `bags.ammo.items` / `byId` | `{ ["Balles lourdes"] = 200 }` / `{ ["2519"] = 200 }` | `{ ["Heavy Shot"] = 200 }` / idem |
| `reputations[].standing` / `standingToken` | `Amical` / `FRIENDLY` | `Friendly` / `FRIENDLY` |
| `money.text` | `2 po 40 pa 16 pc` | `2g 40s 16c` |

Le test hors jeu (`lua addon/tests/run_capture.lua`) joue la même session avec un client
frFR puis enUS, retire les libellés traduits ci-dessus et vérifie que tout le reste est
identique. Les noms anglais des objets et quêtes inventés du test sont eux aussi inventés.

## 7. Mémoire des quêtes vues (1.4)

`ForeverScribeDB.questMemory` est au **niveau du compte** : tous les persos du compte
l'enrichissent. L'addon l'alimente pendant le jeu ; il ne la vide jamais, sauf pour
respecter les plafonds. Elle sert surtout aux quêtes propres à Forever, absentes de
QuestieDB et des tables du client (voir `docs/conception/plan-quetes-forever.md`).

```lua
questMemory = {
  version = 1,                          -- format de la mémoire (pas la version du schéma)
  updatedAt = 1794937235,               -- dernier événement traité (epoch)
  lastError = { event = "QUEST_DETAIL", message = "…", at = 0 },  -- dernière erreur, facultatif
  quests = {                            -- questId (number) -> quête
    [90001] = {
      titles = { frFR = "Peaux de raptor", enUS = "Raptor Hides" },  -- par langue du client
      level = 24,                       -- niveau de la quête, si connu
      repeatable = true,                -- facultatif
      frequency = 1,                    -- facultatif, > 0 seulement (1 quotidienne, 2 hebdo)
      firstSeen = 1794937235, lastSeen = 1794937235,
      starts = {                        -- donneurs (3 au plus), confirmés à l'acceptation
        { kind = "npc", id = 90100, mapId = 1437, x = 37, y = 20, at = 1794937235, via = "accept" },
      },
      ends = {                          -- receveurs (3 au plus)
        { kind = "npc", id = 90101, mapId = 1437, x = 10, y = 60, at = 0, via = "listed" },
        { kind = "npc", id = 90101, mapId = 1437, instance = true, at = 0, via = "turnin" },
      },
      offeredBy = { { kind = "npc", id = 90100 } },   -- PNJ qui la proposent (5 au plus)
      objectives = {                    -- index de l'objectif (comme quests.list[].objectives)
        [1] = { type = "monster", need = 10,
                points = { { mapId = 1437, x = 14, y = 30 }, … } },  -- 8 points au plus
      },
      poi = { mapId = 1437, x = 23, y = 28.5, at = 0 },        -- point de carte de la quête
      waypoint = { mapId = 1437, x = 38.1, y = 50.2, at = 0 }, -- point de rendu (quête finie)
      turnedIn = true,                  -- rendue au moins une fois sur ce compte
    },
  },
  npcs = {                              -- id de PNJ (number) -> PNJ vu
    [90100] = { names = { frFR = "Garde Brumebarbe" }, lastSeen = 0,
                points = { { mapId = 1437, x = 37, y = 20 } } },   -- 5 points au plus
  },
  objects = {                           -- id d'objet du monde (number) -> même forme que npcs
    [90200] = { names = { frFR = "Coffre englouti" }, lastSeen = 0, points = { … } },
  },
}
```

**Valeurs.**
- `kind` : `npc` (GUID `Creature`, `Vehicle` ou `Pet`), `object` (GUID `GameObject`),
  `item` (quête lancée par un objet du sac : `id` est l'id de l'objet, sans position).
- `via` : `accept` (donneur vu au `QUEST_DETAIL` puis acceptation), `turnin` (fenêtre de
  rendu `QUEST_PROGRESS` ou `QUEST_COMPLETE` ouverte chez ce PNJ : **receveur certain**),
  `listed` (le PNJ liste la quête en cours dans son dialogue : **receveur probable**, il
  peut aussi s'agir du donneur d'une quête en plusieurs étapes).
- `x`, `y` : pourcentage de la carte `mapId` (0 à 100, une décimale), comme `/way`.
  Ils manquent quand l'API ne donne pas la position (instance, valeur masquée) ; dans ce
  cas `instance = true` peut être présent. Un point sans coordonnées n'est jamais ajouté
  à `points`.
- Les positions de `starts` et `ends` sont celles **du joueur** au moment du dialogue,
  donc à un ou deux mètres du PNJ. Celles de `objectives[].points` sont celles du joueur
  quand le compteur a augmenté, ou à la fin du combat si l'objectif a avancé en combat.
- `titles` et `names` sont rangés par code de langue du client (`GetLocale()`), car un
  même compte peut jouer en frFR puis en enUS. Toute la logique passe par les ids.

**Événements utilisés.** `GOSSIP_SHOW` et `QUEST_GREETING` (quêtes proposées et en cours
chez un PNJ), `QUEST_DETAIL` (quête affichée avant acceptation, argument
`questStartItemID`), `QUEST_ACCEPTED`, `QUEST_PROGRESS` et `QUEST_COMPLETE` (rendu),
`QUEST_TURNED_IN`, `QUEST_LOG_UPDATE` et `UNIT_QUEST_LOG_CHANGED` (progression, un seul
scan une seconde après la rafale), `ZONE_CHANGED_NEW_AREA` (points de carte).

**Règles.**
- Rien n'est lu en combat : les événements attendent `PLAYER_REGEN_ENABLED` (50 au plus,
  les scans d'objectifs fusionnés).
- Le premier scan des objectifs après une connexion ou un `/reload` sert de référence :
  seule une hausse de compteur ajoute un point.
- Une valeur masquée par l'API (`issecretvalue`) n'est jamais écrite.
- Plafonds : 3 000 quêtes, 3 000 PNJ, 1 000 objets ; au-delà, les entrées vues le moins
  récemment (`lastSeen`) sont retirées à la connexion et à la déconnexion. Deux points à
  moins de 1,5 % l'un de l'autre sur la même carte comptent pour un.

**Pour le serveur.** Lire `questMemory` dans chaque fichier `ForeverScribe.lua` de compte,
fusionner les comptes (union des listes, dédoublonnage par `kind` + `id`, le `at` le plus
récent l'emporte pour la position), puis l'exposer avec le badge « observé en jeu ». Un
`via = "turnin"` prime sur un `via = "listed"`. Les ids de PNJ et d'objets se recoupent avec
QuestieDB et le cache des créatures du client pour les noms dans l'autre langue.

