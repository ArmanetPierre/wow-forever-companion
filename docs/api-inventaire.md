# Inventaire de l'API WoW Forever — étape 0 (résultats)

Client Forever : base **retail 12.1.5**, interface **16001**, `WOW_PROJECT_ID = 18`
(`WOW_PROJECT_CAMELOT`). Sonde lancée le **17/11/2026 17:50** sur Brannok
(build 1.60.1.70938 du 12/11/2026, frFR).

- Données brutes de la sonde : non publiées (elles contiennent des données de joueur) ; les valeurs utiles sont reprises ci-dessous, anonymisées.
- Liste des 7 137 fonctions trouvées : [`docs/sonde/fonctions.txt`](sonde/fonctions.txt)
- Bilan : 272 espaces `C_*` (4 951 fonctions) + 6 025 fonctions globales ;
  200 tests → **158 OK, 6 erreurs (mauvais arguments de la sonde), 36 absentes**.

Légende : ✅ OK · ⚠️ erreur d'appel (fonction présente) · ❌ absente.

## Verdict général

**Forever expose l'API retail moderne, pas l'API Classic.** Presque toutes les fonctions
globales Classic (`GetTalentInfo`, `GetNumQuestLogEntries`, `GetSkillLineInfo`,
`GetItemInfo`, `GetNumFactions`, `GetContainerNumSlots`, `GetSpellTabInfo`…) sont
**absentes**. Leurs équivalents `C_*` répondent, plus des ajouts propres à Forever
(`C_PetInfo`, `C_SkillInfo`, `UnitUsesAmmo`…). Aucun domaine prioritaire n'est bloqué.

## Les 5 incertitudes tranchées

| # | Question | Verdict |
|---|---|---|
| 1 | Talents : Classic ou Traits ? | **Système retail `C_Traits` / `C_ClassTalents`.** Toute l'API Classic est absente. Une seule « spé » (ID 1485 « Chasseur », rôle DAMAGER) avec un arbre de classe unique (`treeID 1091`, 52 nœuds). Le détail des talents pris se lira par `C_Traits.GetNodeInfo(configID, nodeID)`, pas encore testé. |
| 2 | Ruleset / royaume | `GetRealmName()` = **« CAMWOW EU4 Realm 6 PvP »** : le ruleset est dans le nom (suffixe `PvP`). `GetRealmID()` = 1234 (= le serveur du GUID). `UnitName("player")` renvoie un 2ᵉ élément **« Durn »** : c'est le suffixe affiché du perso (même nom que le dossier WTF `Brannok-Durn`). `C_GameRules.IsHardcoreActive()` = false, `GetActiveGameMode()` = 1. `C_RealmList` absent ; `C_Roleset.GetActiveAllowedRolesets` existe (non testé). |
| 3 | Métiers | **`GetProfessions` + `GetProfessionInfo`** pour les métiers (Travail du cuir 106/150). **`C_SkillInfo`** (ajout Forever) pour toutes les lignes de compétence (26 lignes : classe, armes, langues…). `GetSkillLineInfo` Classic absent. Recettes : `C_TradeSkillUI.GetAllRecipeIDs` renvoie une liste vide fenêtre fermée → à capturer **à l'ouverture de la fenêtre de métier**. Spécialisations de métier : `C_ProfSpecs` existe. |
| 4 | Familier | **`C_PetInfo` répond en entier** : bonheur (3 = content), loyauté (« Niveau 6, Meilleur ami »), points de dressage (120 / 76), nourriture (Viande, Poisson). `C_StableInfo.GetStablePetInfo` donne la fiche complète (famille, niveau, XP, loyauté, spé). **Munitions : oui**, `UnitUsesAmmo` et `C_PaperDollInfo.AmmoNeeded` = true ; mais `GetInventorySlotInfo("AmmoSlot")` renvoie l'emplacement 0 non valide → le stock de munitions se comptera dans les sacs/carquois. |
| 5 | Stats et quêtes | **`C_Item.GetItemStats` ✅** (stats + DPS de l'arme : Fusil 13,26 DPS, +3 Agi, +3 For). **`UnitRangedDamage` ✅** (vitesse 2,09 s, 76-96 dégâts). Quêtes : **`C_QuestLog` ✅** (52 lignes dont 40 quêtes, titres, objectifs, niveau, tags), `GetQuestsOnMap` donne même les **coordonnées** des objectifs. **Quêtes terminées ✅** : `GetAllCompletedQuestIDs` (195 IDs). |

## Identification compte / perso (multi-joueurs, multi-persos)

| Donnée | Fonction | Résultat sonde |
|---|---|---|
| ID unique du perso | `UnitGUID("player")` | ✅ `Player-1234-0A1B2C3D` |
| Nom + suffixe | `UnitName`, `UnitFullName` | ✅ `Brannok`, `Durn` |
| « Royaume » technique | `GetRealmName` / `GetNormalizedRealmName` / `GetRealmID` | ✅ `CAMWOW EU4 Realm 6 PvP` / `CAMWOWEU4Realm6PvP` / `1234` |
| Région | `GetCurrentRegion`, `GetCurrentRegionName` | ✅ `3`, `EU` |
| Compte Battle.net | `BNGetInfo`, `C_BattleNet.GetAccountInfoByGUID` | ✅ (valeurs masquées par la sonde) |
| Ruleset | suffixe de `GetRealmName`, `C_GameRules.IsHardcoreActive`, `GetActiveGameMode`, `C_PvP.IsWarModeActive` | ✅ `PvP`, false, 1, false |
| Mode Forever | `C_GameRules.GetForeverExperiencePreset` | non testé (découvert) |
| Extension | `GetAccountExpansionLevel` etc. | ✅ 0 |
| `C_RealmList.GetRealmInfo`, `IsWarModeDesired` global | — | ❌ |

**Clé retenue**
- **Joueur** = dossier `WTF/Account/<compte>/` (ici `123456789#1`), rattaché à un prénom
  au premier lancement.
- **Perso** = `UnitGUID("player")`. Libellé affiché : `Nom-Suffixe · Région · Ruleset`,
  ex. **Brannok-Durn · EU · PvP**. Le ruleset est extrait du suffixe de `GetRealmName`
  (`PvP`, et à vérifier pour Normal / RP / Hardcore).
- Repli si le GUID manque : `région + nom + suffixe`.
- Dossiers : `perso/<joueur>/<Nom>-<Suffixe>/` (le WTF utilise déjà `Brannok-Durn`,
  `Elwyna-Lor`).
- Le compte contient un 2ᵉ perso, **Elwyna-Lor** (dossier WTF `93/Elwyna-Lor`) :
  premier cas réel de multi-perso.

## Domaines — résultats et décisions

| Domaine | Résultat sonde | **Décision ForeverScribe** | Alternative |
|---|---|---|---|
| Identité | ✅ `UnitRace` (Nain, Dwarf, 3), `UnitClass` (Chasseur, HUNTER, 3), `UnitSex` (2), `UnitFactionGroup` (Alliance), `UnitLevel` (25), `GetGuildInfo` (vide = sans guilde), `C_CreatureInfo.GetRaceInfo` ✅ · ⚠️ `C_PlayerInfo.GetRace` (attend un `PlayerLocation`) | `Unit*` + `GetGuildInfo` | `C_PlayerInfo.GetRace(PlayerLocation:CreateFromUnit("player"))` |
| Progression | ✅ `UnitXP` 27 088 / `UnitXPMax` 34 000, `GetXPExhaustion` 912 (repos), `GetRestState` (1, « En forme »), `IsResting`, `GetMaxPlayerLevel` 60, temps de jeu via `TIME_PLAYED_MSG` (48 h 09 au total, 2 h 05 au niveau) | ces fonctions + `RequestTimePlayed` à la connexion | — |
| Position | ✅ `GetZoneText` (Les Paluns), `GetSubZoneText` (Port de Menethil), `C_Map.GetBestMapForUnit` (1437), `C_Map.GetPlayerMapPosition` (vecteur → `:GetXY()`), `C_Map.GetMapInfo`, `GetBindLocation` (Forgefer), `GetInstanceInfo` | `C_Map.*` + textes de zone ; coordonnées ×100 pour `/way` | — |
| Équipement | ✅ `GetInventoryItemLink/ID/Quality/Durability`, `C_Item.GetItemInfo`, `C_Item.GetItemStats`, `C_Item.GetDetailedItemLevelInfo`, `C_Item.GetItemInfoInstant`, `C_TooltipInfo.GetInventoryItem` (lignes de bulle + coût de réparation), `GetAverageItemLevel` (18,4) · ⚠️ `C_Item.GetWeaponEnchantInfo` (attend un emplacement) · ❌ `GetItemInfo`, `GetItemStats` globaux | `C_Item.*` par emplacement 1-19 + `C_TooltipInfo` pour le texte complet | `GetWeaponEnchantInfo` global ✅ pour les enchantements temporaires |
| Munitions | ✅ `UnitUsesAmmo` = true, `C_PaperDollInfo.AmmoNeeded` = true · `AmmoSlot` = emplacement 0 non valide | compter les munitions dans les sacs (type d'objet Projectile) + noter le carquois/giberne | `GetInventoryItemCount` sur l'arme à distance (à tester) |
| Stats | ✅ `UnitStat` 1-5 (For 48, Agi 73, End 81, Int 44, Esp 62), `UnitAttackPower` 168, `UnitRangedAttackPower` 193, `UnitDamage`, `UnitRangedDamage`, `UnitAttackSpeed`, `UnitArmor` 780, `UnitResistance`, `UnitDefenseSkill` 116, `GetCritChance` 7,4 %, `GetRangedCritChance` 7,7 %, `GetHitModifier`, `GetRangedHitModifier`, `GetDodgeChance`, `GetParryChance`, `GetManaRegen`, `GetRangedAttackPowerForStat` (Agi 10 → 20 PA) · ⚠️ `GetCritChanceFromStat` (2 arguments) · ❌ `UnitDefense`, `C_SwingTimer.GetSwingInfo` | toutes ces fonctions | `GetCritChanceFromStat(stat, valeur)` pour les comparaisons |
| Talents / spé | ❌ toute l'API Classic (`GetTalentInfo`, `GetNumTalentTabs`, `UnitCharacterPoints`…) et `GetSpecialization` global · ✅ `C_SpecializationInfo.GetSpecialization` (1), `GetSpecializationInfo` (1485 Chasseur DAMAGER), `GetActiveSpecGroup` (1), `HasPlayerEarnedATalentPoint`, `C_ClassTalents.GetActiveConfigID` (3758979), `C_Traits.GetConfigInfo`, `C_Traits.GetTreeNodes` (52 nœuds) · ❌ `GetNumSpecGroups` | `C_ClassTalents.GetActiveConfigID` → `C_Traits.GetConfigInfo` → `GetTreeNodes` → `GetNodeInfo` (rangs pris, max) + `GetTreeCurrencyInfo` (points dépensés / restants) | double spé : surveiller `C_SpecializationInfo.GetActiveSpecGroup` et l'événement `ACTIVE_TALENT_GROUP_CHANGED` |
| Quêtes | ✅ `C_QuestLog.GetNumQuestLogEntries` (52 / 40), `GetInfo` (titre, niveau, en-têtes de zone), `GetQuestObjectives`, `GetTitleForQuestID`, `IsComplete`, `GetQuestTagInfo` (ex. « JcJ »), `GetQuestsOnMap` (coordonnées), `GetTrivialRange` (6), `GetDailyQuestsCompleted` · ❌ `GetNumQuestLogEntries`, `GetQuestLogTitle`, `GetQuestGreenRange` globaux | `C_QuestLog.*` | `GetQuestLogLeaderBoard` global ✅ (texte des objectifs) |
| Quêtes terminées | ✅ `GetAllCompletedQuestIDs` (195), `IsQuestFlaggedCompleted` · ❌ `GetQuestsCompleted` | `GetAllCompletedQuestIDs` à la connexion | `IsQuestFlaggedCompleted` ciblé |
| Métiers, compétences | ✅ `GetProfessions` (2 métiers principaux, index 5 et 7), `GetProfessionInfo` (Travail du cuir 106/150), `C_SkillInfo.GetNumSkillLines` (26), `GetSkillLineInfo`, `C_SpellBook.GetClassSkillLineInfo`, `C_TradeSkillUI.GetAllProfessionTradeSkillLines` · ❌ `GetNumSkillLines`, `GetSkillLineInfo` globaux | `GetProfessions`/`GetProfessionInfo` + `C_SkillInfo` (armes, langues…) | `C_SkillInfo.GetSkillLineInfoByID` |
| Recettes | `C_TradeSkillUI.GetAllRecipeIDs` ✅ mais vide fenêtre fermée · ❌ `GetNumTradeSkills` | capture sur `TRADE_SKILL_SHOW` / `TRADE_SKILL_LIST_UPDATE` | `C_TradeSkillUI.GetRecipeInfo` |
| Familier | ✅ `HasPetUI`, `UnitName/Level/CreatureFamily("pet")` (Félin 24), `C_PetInfo.GetPetHappiness` (3, 125, 20), `GetPetLoyalty`, `GetPetTrainingPoints` (120, 76), `GetPetFoodTypes`, `GetPetExperience` (2 475 / 7 925), `C_StableInfo.GetNumActivePets` (1), `GetStablePetInfo` (fiche complète), `C_SpellBook.HasPetSpells` (18) · ❌ `GetPetHappiness`, `GetPetLoyalty`, `GetPetTrainingPoints`, `GetNumStableSlots` globaux | `C_PetInfo` + `C_StableInfo` + sorts du familier | `C_PetInfo.GetPetTalentTree` (découvert, non testé) |
| Sacs, argent | ✅ `C_Container.GetContainerNumSlots` (sac 0 : 20), `GetContainerNumFreeSlots` (sac 0 : 0 libre), `GetContainerItemInfo` (lien, ID, nom, quantité, qualité, lié), `GetBagName` (« Petite giberne »), `GetMoney` (24 016 pc = 2 po 40 pa 16 pc) · ❌ `GetContainerNumSlots` global | `C_Container.*` sacs 0-4 (+ sac de composants si présent) | — |
| Réputations | ✅ `C_Reputation.GetNumFactions` (11), `GetFactionDataByIndex` (Alliance, Darnassus…, palier, seuils), `GetWatchedFactionData` (aucune suivie), `C_MajorFactions.GetMajorFactionIDs` (2800, 2802) · ❌ `GetNumFactions`, `GetFactionInfo` globaux | `C_Reputation.*` | `C_MajorFactions.GetMajorFactionData` pour 2800/2802 (à identifier) |
| Monnaies | ✅ `C_CurrencyInfo.GetCurrencyListSize` (3), `GetCurrencyListInfo` | `C_CurrencyInfo.*` | — |
| Sorts connus | ✅ `C_SpellBook.GetNumSpellBookSkillLines` (4), `GetSpellBookSkillLineInfo` (« Maîtrise des bêtes » 17 sorts), `GetSpellBookItemInfo/Name`, `C_Spell.GetSpellInfo` (Tir automatique, portée 8-41), `IsPlayerSpell` · ❌ `GetNumSpellTabs`, `GetSpellTabInfo`, `GetSpellBookItemName` globaux | `C_SpellBook.*` + `C_Spell.GetSpellInfo` | — |
| Banque | ✅ `C_Container.GetContainerNumSlots(-1)` = 32 (taille connue sans être à la banque) · ⚠️ `C_Bank.CanViewBank` (attend un type de banque) · ❌ `GetNumBankSlots` | contenu capturé sur `BANKFRAME_OPENED` | `C_Bank.CanViewBank(Enum.BankType.Character)` |
| Collections | ✅ `C_MountJournal.GetNumMounts` (136, compte), `GetMountIDs`, `C_PetJournal.GetNumPets` (0), `GetNumCompanions("MOUNT")` (0), `GetTotalAchievementPoints` (0), `GetNumCompletedAchievements` (111) · ❌ `C_TransmogCollection.GetNumMaxOutfits` | priorité 3 : nombre de montures **possédées** (filtrer `isCollected`) et succès | — |

## Découvertes (non prévues dans le plan)

| Espace / fonction | Intérêt |
|---|---|
| `C_GameRules.GetForeverExperiencePreset`, `IsSelfFoundAllowed`, `IsGameRuleActive`, `GetCurrentGameModeDisplayInfo` | Réglages propres à Forever (préréglage d'expérience, self-found…) : à capturer dans l'identité |
| `C_Roleset.GetActiveAllowedRolesets` / `GetActiveBlockedRolesets` | API des rulesets (Normal / PvP / RP / HC) : source plus fiable que le suffixe du royaume |
| `ToggleLegacySystemUI`, `LegacySystemFrame_LoadUI`, `ShowLegacyChallenge`, `ToggleLegacyChallenges` | **Système Héritage** (Legacy) : interface présente ; ses données passent probablement par `C_Traits` ou `C_PerksActivities` → à explorer |
| `C_QuestInfoSystem.GetQuestLogRewardFavor` | Récompense de **faveur** des quêtes : probablement Merchant's Favor |
| `C_Housing` (dont `GetCurrentHouseLevelFavor`), `C_NeighborhoodInitiative` | Logis / quartier (hérités du retail) ; peut-être les **campements** : à vérifier |
| `C_ProfSpecs` | Spécialisations de métier (points, voies, avantages) |
| `C_PetInfo.GetPetTalentTree`, `C_StableInfo.GetStabledPetList` | Talents du familier et familiers à l'écurie |
| `C_DamageMeter` | **Compteur de dégâts intégré** : sessions de combat → analyse de DPS sans journal de combat |
| `C_MapExplorationInfo` | Zones explorées : utile pour le leveling et les succès d'exploration |
| `C_PerksActivities` | Activités suivies (le WTF contient `trackedPerksActivities`) : à identifier dans Forever |
| `C_Reincarnation`, `C_LevelSquish` | Présents, rôle dans Forever inconnu |
| `C_EquipmentSet` | Ensembles d'équipement enregistrés |
| `C_Trophy` | Monuments/trophées, à identifier |
| `PaperDollFrame_SetWeaponSkill` | Fonction d'interface héritée ; les compétences d'armes semblent pourtant absentes du gameplay |

## Pas encore testé par la sonde

- **Détail des talents** : `C_Traits.GetNodeInfo`, `GetTreeCurrencyInfo` (rangs pris, points restants).
- **Banque** (contenu) et **recettes** : nécessitent la fenêtre ouverte.
- **2ᵉ métier** (index 7) et métiers secondaires (pêche, cuisine, secourisme) : non détaillés.
- Nombre de **munitions**, contenu complet des 5 sacs, liste des familiers à l'écurie.
- `C_Roleset`, `GetForeverExperiencePreset`, `GetCurrentGameModeDisplayInfo`, `C_MajorFactions.GetMajorFactionData`, `C_DamageMeter`, `C_ProfSpecs`.
- Valeur du suffixe de royaume pour les rulesets Normal, RP et Hardcore.
- Un 2ᵉ perso (Elwyna-Lor) : non sondé.
