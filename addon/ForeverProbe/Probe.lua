-- ForeverProbe : sonde de l'API WoW Forever (étape 0 du compagnon).
-- Inventorie les fonctions disponibles et teste les candidates de docs/api-inventaire.md.
-- Ne modifie rien dans le jeu : uniquement des fonctions de lecture.
-- Résultat dans ForeverProbeDB (SavedVariables du compte), écrit au /reload.

local ADDON = ...
local VERSION = "0.2.0"
local MAX_ENTRIES = 20
local MAX_STR = 120

-- Messages du chat : anglais par défaut, français pour un client frFR.
-- (Les données de ForeverProbeDB restent en clés françaises : format interne de la sonde.)
local MSG = {
  enUS = {
    done = "Probe finished: %d functions found (%d C_* namespaces), %d tests OK, %d errors, %d missing. Type /reload to write the file.",
    internal = "Internal probe error: ",
  },
  frFR = {
    done = "Sonde terminée : %d fonctions trouvées (%d espaces C_*), %d tests OK, %d erreurs, %d absentes. Tape /reload pour écrire le fichier.",
    internal = "Erreur interne de la sonde : ",
  },
}
local function msg(key)
  local loc = (type(GetLocale) == "function") and GetLocale() or "enUS"
  return (MSG[loc] or MSG.enUS)[key] or MSG.enUS[key]
end

-- ---------------------------------------------------------------------------
-- Utilitaires sûrs
-- ---------------------------------------------------------------------------

local function safeToString(v)
  local ok, s = pcall(tostring, v)
  if not ok then return "<illisible>" end
  if #s > MAX_STR then s = s:sub(1, MAX_STR) .. "…" end
  return s
end

-- Échantillon d'une valeur : scalaires tronqués, tables aplaties sur 2 niveaux.
local function sample(v, depth)
  depth = depth or 0
  local t = type(v)
  if t == "string" then
    return (#v > MAX_STR) and (v:sub(1, MAX_STR) .. "…") or v
  elseif t == "number" or t == "boolean" or t == "nil" then
    return v
  elseif t == "table" then
    if depth >= 2 then return "<table>" end
    local out, n = {}, 0
    local ok = pcall(function()
      for k, val in pairs(v) do
        n = n + 1
        if n > MAX_ENTRIES then out["…"] = "tronqué"; break end
        out[safeToString(k)] = sample(val, depth + 1)
      end
    end)
    if not ok then return "<table illisible>" end
    return out
  else
    return "<" .. t .. ">"
  end
end

-- Seulement les types (pour les données personnelles : BattleTag, etc.)
local function typesOnly(...)
  local out = {}
  for i = 1, select("#", ...) do
    out[i] = type((select(i, ...)))
  end
  return out
end

-- Résout "C_Item.GetItemStats" -> fonction ou nil
local function resolve(path)
  local cur = _G
  for part in string.gmatch(path, "[^%.]+") do
    if type(cur) ~= "table" then return nil end
    local ok, nxt = pcall(function() return cur[part] end)
    if not ok then return nil end
    cur = nxt
  end
  return cur
end

local function chat(msg)
  if DEFAULT_CHAT_FRAME then
    DEFAULT_CHAT_FRAME:AddMessage("|cff66ccff[ForeverProbe]|r " .. msg)
  else
    print("[ForeverProbe] " .. msg)
  end
end

-- ---------------------------------------------------------------------------
-- Énumération de l'API réelle
-- ---------------------------------------------------------------------------

local KEYWORDS = {
  "Talent", "Spec", "Quest", "Skill", "Profession", "Trade", "Pet", "Item",
  "Inventory", "Container", "Bag", "Faction", "Reputation", "Currency", "Spell",
  "Stat", "Attack", "Ranged", "Crit", "Hit", "Damage", "Armor", "Resist", "XP",
  "Rest", "Bind", "Zone", "Map", "Money", "Guild", "Ammo", "Mount", "Achievement",
  "Played", "Realm", "Region", "Expansion", "BN", "Unit", "Weapon", "Durability",
  "Loyalty", "Happiness", "Legacy", "Camp", "Ruleset", "Hardcore", "Warmode", "GameRule",
}

local function enumerate()
  local namespaces, globals = {}, {}
  local nsCount, fnCount, globalFnTotal = 0, 0, 0
  pcall(function()
    for name, val in pairs(_G) do
      if type(name) == "string" then
        local tv = type(val)
        if tv == "table" and name:sub(1, 2) == "C_" then
          local fns = {}
          pcall(function()
            for k, f in pairs(val) do
              if type(f) == "function" and type(k) == "string" then fns[#fns + 1] = k end
            end
          end)
          table.sort(fns)
          namespaces[name] = fns
          nsCount = nsCount + 1
          fnCount = fnCount + #fns
        elseif tv == "function" then
          globalFnTotal = globalFnTotal + 1
          for _, kw in ipairs(KEYWORDS) do
            if name:find(kw, 1, true) then globals[#globals + 1] = name; break end
          end
        end
      end
    end
  end)
  table.sort(globals)
  return {
    namespaces = namespaces,
    namespaceCount = nsCount,
    namespaceFunctionCount = fnCount,
    globalFunctionsMatching = globals,
    globalFunctionTotal = globalFnTotal,
  }
end

-- ---------------------------------------------------------------------------
-- Candidates à tester (lecture seule). Champs :
--   d = domaine, f = chemin de la fonction, a = arguments (table)
--   af = fonction qui renvoie les arguments (calculés au moment du test)
--   r = true : ne garder que les types (donnée personnelle)
-- ---------------------------------------------------------------------------

local function firstEquippedLink()
  for slot = 1, 19 do
    local l = GetInventoryItemLink and GetInventoryItemLink("player", slot)
    if l then return l end
  end
end

local function rangedLink()
  return (GetInventoryItemLink and GetInventoryItemLink("player", 18)) or firstEquippedLink()
end

local TESTS = {
  -- Identification compte / perso
  { d = "ident", f = "UnitGUID", a = { "player" } },
  { d = "ident", f = "UnitName", a = { "player" } },
  { d = "ident", f = "UnitFullName", a = { "player" } },
  { d = "ident", f = "GetRealmName" },
  { d = "ident", f = "GetNormalizedRealmName" },
  { d = "ident", f = "GetRealmID" },
  { d = "ident", f = "GetCurrentRegion" },
  { d = "ident", f = "GetCurrentRegionName" },
  { d = "ident", f = "BNGetInfo", r = true },
  { d = "ident", f = "C_BattleNet.GetAccountInfoByGUID", af = function() return { UnitGUID("player") } end, r = true },
  { d = "ident", f = "GetAccountExpansionLevel" },
  { d = "ident", f = "GetExpansionLevel" },
  { d = "ident", f = "GetServerExpansionLevel" },
  { d = "ident", f = "C_GameRules.IsHardcoreActive" },
  { d = "ident", f = "C_GameRules.GetActiveGameMode" },
  { d = "ident", f = "C_PvP.IsWarModeDesired" },
  { d = "ident", f = "C_PvP.IsWarModeActive" },
  { d = "ident", f = "IsWarModeDesired" },
  { d = "ident", f = "C_RealmList.GetRealmInfo" },
  { d = "ident", f = "GetLocale" },

  -- Identité
  { d = "identite", f = "UnitRace", a = { "player" } },
  { d = "identite", f = "UnitClass", a = { "player" } },
  { d = "identite", f = "UnitSex", a = { "player" } },
  { d = "identite", f = "UnitFactionGroup", a = { "player" } },
  { d = "identite", f = "UnitLevel", a = { "player" } },
  { d = "identite", f = "GetGuildInfo", a = { "player" } },
  { d = "identite", f = "C_PlayerInfo.GetRace" },
  { d = "identite", f = "C_CreatureInfo.GetRaceInfo", af = function() return { select(3, UnitRace("player")) } end },

  -- Progression
  { d = "progression", f = "UnitXP", a = { "player" } },
  { d = "progression", f = "UnitXPMax", a = { "player" } },
  { d = "progression", f = "GetXPExhaustion" },
  { d = "progression", f = "GetRestState" },
  { d = "progression", f = "IsResting" },
  { d = "progression", f = "GetMaxPlayerLevel" },
  { d = "progression", f = "IsXPUserDisabled" },
  { d = "progression", f = "RequestTimePlayed" },

  -- Position
  { d = "position", f = "GetZoneText" },
  { d = "position", f = "GetRealZoneText" },
  { d = "position", f = "GetSubZoneText" },
  { d = "position", f = "GetMinimapZoneText" },
  { d = "position", f = "C_Map.GetBestMapForUnit", a = { "player" } },
  { d = "position", f = "C_Map.GetPlayerMapPosition", af = function() return { C_Map.GetBestMapForUnit("player"), "player" } end },
  { d = "position", f = "C_Map.GetMapInfo", af = function() return { C_Map.GetBestMapForUnit("player") } end },
  { d = "position", f = "GetBindLocation" },
  { d = "position", f = "GetInstanceInfo" },

  -- Équipement et objets
  { d = "equipement", f = "GetInventorySlotInfo", a = { "RangedSlot" } },
  { d = "equipement", f = "GetInventorySlotInfo", a = { "AmmoSlot" } },
  { d = "equipement", f = "GetInventorySlotInfo", a = { "MainHandSlot" } },
  { d = "equipement", f = "GetInventoryItemLink", a = { "player", 18 } },
  { d = "equipement", f = "GetInventoryItemLink", a = { "player", 16 } },
  { d = "equipement", f = "GetInventoryItemID", a = { "player", 18 } },
  { d = "equipement", f = "GetInventoryItemDurability", a = { 18 } },
  { d = "equipement", f = "GetInventoryItemQuality", a = { "player", 18 } },
  { d = "equipement", f = "C_Item.GetItemInfo", af = function() return { rangedLink() } end },
  { d = "equipement", f = "GetItemInfo", af = function() return { rangedLink() } end },
  { d = "equipement", f = "C_Item.GetItemStats", af = function() return { rangedLink() } end },
  { d = "equipement", f = "GetItemStats", af = function() return { rangedLink() } end },
  { d = "equipement", f = "C_Item.GetDetailedItemLevelInfo", af = function() return { rangedLink() } end },
  { d = "equipement", f = "C_Item.GetItemInfoInstant", af = function() return { rangedLink() } end },
  { d = "equipement", f = "C_TooltipInfo.GetInventoryItem", a = { "player", 18 } },
  { d = "equipement", f = "C_Item.GetWeaponEnchantInfo" },
  { d = "equipement", f = "GetWeaponEnchantInfo" },
  { d = "equipement", f = "GetAverageItemLevel" },

  -- Stats du personnage
  { d = "stats", f = "UnitStat", a = { "player", 1 } },
  { d = "stats", f = "UnitStat", a = { "player", 2 } },
  { d = "stats", f = "UnitStat", a = { "player", 3 } },
  { d = "stats", f = "UnitStat", a = { "player", 4 } },
  { d = "stats", f = "UnitStat", a = { "player", 5 } },
  { d = "stats", f = "UnitAttackPower", a = { "player" } },
  { d = "stats", f = "UnitRangedAttackPower", a = { "player" } },
  { d = "stats", f = "UnitDamage", a = { "player" } },
  { d = "stats", f = "UnitRangedDamage", a = { "player" } },
  { d = "stats", f = "UnitAttackSpeed", a = { "player" } },
  { d = "stats", f = "UnitArmor", a = { "player" } },
  { d = "stats", f = "UnitResistance", a = { "player", 2 } },
  { d = "stats", f = "UnitDefense", a = { "player" } },
  { d = "stats", f = "UnitDefenseSkill", a = { "player" } },
  { d = "stats", f = "UnitHealthMax", a = { "player" } },
  { d = "stats", f = "UnitPowerMax", a = { "player" } },
  { d = "stats", f = "UnitPowerType", a = { "player" } },
  { d = "stats", f = "GetCritChance" },
  { d = "stats", f = "GetRangedCritChance" },
  { d = "stats", f = "GetSpellCritChance", a = { 2 } },
  { d = "stats", f = "GetHitModifier" },
  { d = "stats", f = "GetRangedHitModifier" },
  { d = "stats", f = "GetCombatRating", a = { 7 } },
  { d = "stats", f = "GetDodgeChance" },
  { d = "stats", f = "GetParryChance" },
  { d = "stats", f = "GetBlockChance" },
  { d = "stats", f = "GetArmorPenetration" },
  { d = "stats", f = "GetCritChanceFromStat" , a = { 2 } },
  { d = "stats", f = "GetRangedAttackPowerForStat", a = { 2, 10 } },
  { d = "stats", f = "GetManaRegen" },
  { d = "stats", f = "UnitUsesAmmo", a = { "player" } },
  { d = "stats", f = "C_PaperDollInfo.AmmoNeeded" },
  { d = "stats", f = "C_PaperDollInfo.GetMinItemLevel" },
  { d = "stats", f = "C_SwingTimer.GetSwingInfo" },

  -- Talents et spécialisation
  { d = "talents", f = "GetNumTalentTabs" },
  { d = "talents", f = "GetTalentTabInfo", a = { 1 } },
  { d = "talents", f = "GetNumTalents", a = { 1 } },
  { d = "talents", f = "GetTalentInfo", a = { 1, 1 } },
  { d = "talents", f = "GetActiveTalentGroup" },
  { d = "talents", f = "GetNumTalentGroups" },
  { d = "talents", f = "UnitCharacterPoints", a = { "player" } },
  { d = "talents", f = "GetUnspentTalentPoints" },
  { d = "talents", f = "GetSpecialization" },
  { d = "talents", f = "GetSpecializationInfo", af = function() return { GetSpecialization and GetSpecialization() or 1 } end },
  { d = "talents", f = "GetNumSpecializations" },
  { d = "talents", f = "C_SpecializationInfo.GetSpecialization" },
  { d = "talents", f = "C_SpecializationInfo.GetSpecializationInfo", a = { 1 } },
  { d = "talents", f = "C_SpecializationInfo.GetActiveSpecGroup" },
  { d = "talents", f = "C_SpecializationInfo.GetNumSpecGroups" },
  { d = "talents", f = "C_SpecializationInfo.IsSpecSelectionEnabled" },
  { d = "talents", f = "C_SpecializationInfo.HasPlayerEarnedATalentPoint" },
  { d = "talents", f = "C_ClassTalents.GetActiveConfigID" },
  { d = "talents", f = "C_ClassTalents.GetConfigIDsBySpecID" },
  { d = "talents", f = "C_Traits.GetConfigInfo", af = function() return { C_ClassTalents and C_ClassTalents.GetActiveConfigID and C_ClassTalents.GetActiveConfigID() } end },
  { d = "talents", f = "C_Traits.GetTreeNodes", af = function()
      local cid = C_ClassTalents and C_ClassTalents.GetActiveConfigID and C_ClassTalents.GetActiveConfigID()
      local info = cid and C_Traits.GetConfigInfo(cid)
      return { info and info.treeIDs and info.treeIDs[1] }
    end },
  { d = "talents", f = "C_Traits.GetMaxAvailableTraitCurrency" },

  -- Quêtes
  { d = "quetes", f = "GetNumQuestLogEntries" },
  { d = "quetes", f = "GetQuestLogTitle", a = { 1 } },
  { d = "quetes", f = "GetQuestLogLeaderBoard", a = { 1, 1 } },
  { d = "quetes", f = "C_QuestLog.GetNumQuestLogEntries" },
  { d = "quetes", f = "C_QuestLog.GetInfo", a = { 1 } },
  { d = "quetes", f = "C_QuestLog.GetInfo", a = { 2 } },
  { d = "quetes", f = "C_QuestLog.GetQuestObjectives", af = function()
      for i = 1, 30 do
        local info = C_QuestLog.GetInfo(i)
        if info and not info.isHeader and info.questID then return { info.questID } end
      end
    end },
  { d = "quetes", f = "C_QuestLog.GetTitleForQuestID", af = function()
      local info = C_QuestLog.GetInfo(2) or C_QuestLog.GetInfo(1)
      return { info and info.questID }
    end },
  { d = "quetes", f = "C_QuestLog.IsComplete", af = function()
      local info = C_QuestLog.GetInfo(2) or C_QuestLog.GetInfo(1)
      return { info and info.questID }
    end },
  { d = "quetes", f = "C_QuestLog.GetQuestTagInfo", af = function()
      local info = C_QuestLog.GetInfo(2) or C_QuestLog.GetInfo(1)
      return { info and info.questID }
    end },
  { d = "quetes", f = "C_QuestLog.IsQuestFlaggedCompleted", a = { 783 } },
  { d = "quetes", f = "C_QuestLog.GetAllCompletedQuestIDs" },
  { d = "quetes", f = "GetQuestsCompleted" },
  { d = "quetes", f = "C_QuestLog.GetQuestsOnMap", af = function() return { C_Map.GetBestMapForUnit("player") } end },
  { d = "quetes", f = "C_QuestLog.GetTrivialRange" },
  { d = "quetes", f = "GetQuestGreenRange" },
  { d = "quetes", f = "GetDailyQuestsCompleted" },

  -- Métiers et compétences
  { d = "metiers", f = "GetProfessions" },
  { d = "metiers", f = "GetProfessionInfo", af = function() local p1 = GetProfessions and GetProfessions(); return { p1 } end },
  { d = "metiers", f = "GetNumSkillLines" },
  { d = "metiers", f = "GetSkillLineInfo", a = { 1 } },
  { d = "metiers", f = "C_SkillInfo.GetNumSkillLines" },
  { d = "metiers", f = "C_SkillInfo.GetSkillLineInfo", a = { 1 } },
  { d = "metiers", f = "C_SkillInfo.GetSkillLineInfo", a = { 2 } },
  { d = "metiers", f = "C_SpellBook.GetClassSkillLineInfo" },
  { d = "metiers", f = "C_TradeSkillUI.GetAllProfessionTradeSkillLines" },
  { d = "metiers", f = "C_TradeSkillUI.GetBaseProfessionInfo" },
  { d = "metiers", f = "C_TradeSkillUI.GetAllRecipeIDs" },
  { d = "metiers", f = "GetNumTradeSkills" },

  -- Familier
  { d = "familier", f = "HasPetUI" },
  { d = "familier", f = "UnitExists", a = { "pet" } },
  { d = "familier", f = "UnitName", a = { "pet" } },
  { d = "familier", f = "UnitLevel", a = { "pet" } },
  { d = "familier", f = "UnitCreatureFamily", a = { "pet" } },
  { d = "familier", f = "GetPetHappiness" },
  { d = "familier", f = "C_PetInfo.GetPetHappiness" },
  { d = "familier", f = "C_PetInfo.GetPetLoyalty" },
  { d = "familier", f = "C_PetInfo.GetPetTrainingPoints" },
  { d = "familier", f = "C_PetInfo.GetPetFoodTypes" },
  { d = "familier", f = "GetPetExperience" },
  { d = "familier", f = "GetPetLoyalty" },
  { d = "familier", f = "GetPetTrainingPoints" },
  { d = "familier", f = "GetNumStableSlots" },
  { d = "familier", f = "C_StableInfo.GetNumActivePets" },
  { d = "familier", f = "C_StableInfo.GetStablePetInfo", a = { 1 } },
  { d = "familier", f = "C_SpellBook.HasPetSpells" },

  -- Sacs, argent, réputations, monnaies
  { d = "sacs", f = "C_Container.GetContainerNumSlots", a = { 0 } },
  { d = "sacs", f = "C_Container.GetContainerNumFreeSlots", a = { 0 } },
  { d = "sacs", f = "C_Container.GetContainerItemInfo", a = { 0, 1 } },
  { d = "sacs", f = "GetContainerNumSlots", a = { 0 } },
  { d = "sacs", f = "C_Container.GetBagName", a = { 1 } },
  { d = "sacs", f = "GetMoney" },
  { d = "reputation", f = "GetNumFactions" },
  { d = "reputation", f = "GetFactionInfo", a = { 1 } },
  { d = "reputation", f = "C_Reputation.GetNumFactions" },
  { d = "reputation", f = "C_Reputation.GetFactionDataByIndex", a = { 1 } },
  { d = "reputation", f = "C_Reputation.GetFactionDataByIndex", a = { 2 } },
  { d = "reputation", f = "C_Reputation.GetWatchedFactionData" },
  { d = "reputation", f = "C_MajorFactions.GetMajorFactionIDs" },
  { d = "monnaies", f = "C_CurrencyInfo.GetCurrencyListSize" },
  { d = "monnaies", f = "C_CurrencyInfo.GetCurrencyListInfo", a = { 1 } },

  -- Sorts connus
  { d = "sorts", f = "C_SpellBook.GetNumSpellBookSkillLines" },
  { d = "sorts", f = "C_SpellBook.GetSpellBookSkillLineInfo", a = { 2 } },
  { d = "sorts", f = "C_SpellBook.GetSpellBookItemInfo", a = { 1, 0 } },
  { d = "sorts", f = "C_SpellBook.GetSpellBookItemName", a = { 1, 0 } },
  { d = "sorts", f = "GetNumSpellTabs" },
  { d = "sorts", f = "GetSpellTabInfo", a = { 2 } },
  { d = "sorts", f = "GetSpellBookItemName", a = { 1, "spell" } },
  { d = "sorts", f = "C_Spell.GetSpellInfo", a = { 75 } },
  { d = "sorts", f = "IsPlayerSpell", a = { 75 } },
  { d = "sorts", f = "GetNumTrainerServices" },

  -- Banque
  { d = "banque", f = "C_Bank.CanViewBank" },
  { d = "banque", f = "GetNumBankSlots" },
  { d = "banque", f = "C_Container.GetContainerNumSlots", a = { -1 } },

  -- Collections
  { d = "collections", f = "C_MountJournal.GetNumMounts" },
  { d = "collections", f = "C_MountJournal.GetMountIDs" },
  { d = "collections", f = "C_PetJournal.GetNumPets" },
  { d = "collections", f = "GetNumCompanions", a = { "MOUNT" } },
  { d = "collections", f = "GetTotalAchievementPoints" },
  { d = "collections", f = "GetNumCompletedAchievements" },
  { d = "collections", f = "C_TransmogCollection.GetNumMaxOutfits" },
}

-- ---------------------------------------------------------------------------
-- Exécution des tests
-- ---------------------------------------------------------------------------

local function runTests()
  local results, okCount, errCount, missCount = {}, 0, 0, 0
  for i, t in ipairs(TESTS) do
    local entry = { domaine = t.d, fonction = t.f }
    local fn = resolve(t.f)
    if type(fn) ~= "function" then
      entry.existe = false
      missCount = missCount + 1
    else
      entry.existe = true
      local args = t.a or {}
      if t.af then
        local okA, computed = pcall(t.af)
        if okA and type(computed) == "table" then args = computed
        else entry.argsErreur = safeToString(computed) end
      end
      entry.args = sample(args)
      local packed = { pcall(fn, unpack(args)) }
      local ok = table.remove(packed, 1)
      if ok then
        entry.ok = true
        okCount = okCount + 1
        if t.r then
          entry.typesRetour = typesOnly(unpack(packed))
          entry.note = "valeurs masquées (donnée personnelle)"
        else
          local vals = {}
          local okS = pcall(function()
            for k = 1, math.min(#packed, MAX_ENTRIES) do
              vals[k] = sample(packed[k])
              if type(packed[k]) == "table" then
                local n = 0
                for _ in pairs(packed[k]) do n = n + 1 end
                entry.tailles = entry.tailles or {}
                entry.tailles[k] = n
              end
            end
          end)
          entry.retour = okS and vals or "<échantillon illisible>"
          entry.nbRetours = #packed
        end
      else
        entry.ok = false
        entry.erreur = safeToString(packed[1])
        errCount = errCount + 1
      end
    end
    results[i] = entry
  end
  return results, okCount, errCount, missCount
end

-- ---------------------------------------------------------------------------
-- Point d'entrée
-- ---------------------------------------------------------------------------

local timePlayed

local function charKey()
  local ok, guid = pcall(UnitGUID, "player")
  if ok and guid then return guid end
  local okN, name = pcall(UnitName, "player")
  return (okN and name) or "inconnu"
end

local function runProbe()
  local ok, err = pcall(function()
    ForeverProbeDB = ForeverProbeDB or {}
    ForeverProbeDB.runs = ForeverProbeDB.runs or {}

    local build = { pcall(GetBuildInfo) }
    local run = {
      version = VERSION,
      capturedAt = time and time() or 0,
      capturedAtText = date and date("%Y-%m-%d %H:%M:%S") or "",
      build = { version = build[2], build = build[3], date = build[4], interface = build[5] },
      locale = GetLocale and GetLocale() or nil,
      wowProject = WOW_PROJECT_ID,
      wowProjectCamelot = WOW_PROJECT_CAMELOT,
      inCombat = InCombatLockdown and InCombatLockdown() or nil,
      personnage = (pcall(UnitName, "player")) and UnitName("player") or nil,
      timePlayed = timePlayed,
    }

    run.api = enumerate()
    local results, okC, errC, missC = runTests()
    run.tests = results
    run.resume = {
      fonctionsTrouvees = run.api.namespaceFunctionCount + #run.api.globalFunctionsMatching,
      espacesC = run.api.namespaceCount,
      testsTotal = #TESTS, testsOk = okC, testsErreur = errC, testsAbsents = missC,
    }

    ForeverProbeDB.runs[charKey()] = run
    ForeverProbeDB.lastRun = charKey()

    chat(string.format(msg("done"),
      run.resume.fonctionsTrouvees, run.resume.espacesC, okC, errC, missC))
  end)
  if not ok then chat(msg("internal") .. safeToString(err)) end
end

-- Événements
local frame = CreateFrame("Frame")
frame:RegisterEvent("PLAYER_ENTERING_WORLD")
frame:RegisterEvent("TIME_PLAYED_MSG")
frame:SetScript("OnEvent", function(_, event, a1, a2)
  if event == "TIME_PLAYED_MSG" then
    timePlayed = { total = a1, niveau = a2 }
    if ForeverProbeDB and ForeverProbeDB.runs and ForeverProbeDB.lastRun then
      local r = ForeverProbeDB.runs[ForeverProbeDB.lastRun]
      if r then r.timePlayed = timePlayed end
    end
  elseif event == "PLAYER_ENTERING_WORLD" then
    frame:UnregisterEvent("PLAYER_ENTERING_WORLD")
    if C_Timer and C_Timer.After then
      C_Timer.After(5, runProbe)
    else
      runProbe()
    end
  end
end)

SLASH_FOREVERPROBE1 = "/probe"
SlashCmdList["FOREVERPROBE"] = function() runProbe() end
