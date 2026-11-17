-- Environnement WoW simulé pour tester ForeverScribe hors du jeu.
-- Les valeurs reprennent une sonde réelle du 17/11/2026, anonymisée (perso
-- fictif Brannok). Ce qui n'a pas pu être sondé
-- (détail des talents, banque, recettes…) est inventé mais plausible : marqué « inventé ».
local M = {}

M.events = {}       -- frames enregistrées
M.timers = {}       -- callbacks C_Timer en attente
M.chat = {}         -- messages affichés
M.clock = 1000
M.state = { bankOpen = false, tradeSkillOpen = false, inCombat = false, factionExpanded = false }
M.reloads = 0       -- appels à C_UI.Reload / ReloadUI
M.bindings = {}     -- touche -> action
M.savedBindings = nil
M.named = {}        -- frames nommées

-- Les méthodes non simulées (SetSize, SetPoint, CreateTexture…) ne font rien.
local noop = function() end
local frameMeta = {
  __index = function(t, k)
    local v = rawget(t, "_methods")[k]
    if v ~= nil then return v end
    return noop
  end,
}

local function frameObject(kind, name)
  local f = { events = {}, unitEvents = {}, scripts = {}, shown = true, kind = kind, name = name, _methods = {} }
  local m = f._methods
  function m.RegisterEvent(self, e) self.events[e] = true end
  function m.RegisterUnitEvent(self, e, unit) self.events[e] = true; self.unitEvents[e] = unit end
  function m.UnregisterEvent(self, e) self.events[e] = nil end
  function m.SetScript(self, kind2, fn)
    self.scripts[kind2] = fn
    if kind2 == "OnEvent" then self.onEvent = fn end
  end
  function m.GetScript(self, kind2) return self.scripts[kind2] end
  function m.Show(self) self.shown = true end
  function m.Hide(self) self.shown = false end
  function m.IsShown(self) return self.shown end
  function m.CreateTexture(self) return frameObject("Texture") end
  function m.GetCenter(self) return 500, 500 end
  function m.GetEffectiveScale(self) return 1 end
  function m.Click(self) local fn = self.scripts.OnClick; if fn then fn(self, "LeftButton") end end
  setmetatable(f, frameMeta)
  table.insert(M.events, f)
  if name then M.named[name] = f end
  return f
end

function M.fire(event, ...)
  for _, f in ipairs(M.events) do
    if f.events[event] and f.onEvent then f.onEvent(f, event, ...) end
  end
end

function M.runTimers(maxRounds)
  for _ = 1, (maxRounds or 20) do
    if #M.timers == 0 then return end
    local list = M.timers
    M.timers = {}
    table.sort(list, function(a, b) return a.delay < b.delay end)
    for _, t in ipairs(list) do
      M.clock = M.clock + t.delay
      t.fn()
    end
  end
end

local function vector(x, y)
  return { GetXY = function() return x, y end }
end

local RANGED_LINK = "|cnIQ3:|Hitem:2098::::::::25:1485:::::::::|h[Fusil à canon double]|h|r"
local MAIN_LINK = "|cnIQ3:|Hitem:1937::::::::25:1485::1::1:28:5240:::::|h[Coutelas trancheur]|h|r"
local CHEST_LINK = "|cnIQ2:|Hitem:6085::::::::25:1485:::::::::|h[Cuirasse de pillard]|h|r" -- inventé

local ITEMS = {
  [2098] = { "Fusil à canon double", RANGED_LINK, 3, 27, 22, "Arme", "Fusils", 1, "INVTYPE_RANGEDRIGHT", 135617, 3020, 2, 3 },
  [1937] = { "Coutelas trancheur", MAIN_LINK, 3, 24, 19, "Arme", "Épées à une main", 1, "INVTYPE_WEAPON", 135321, 2400, 2, 7 },
  [6085] = { "Cuirasse de pillard", CHEST_LINK, 2, 22, 17, "Armure", "Cuir", 1, "INVTYPE_CHEST", 132719, 900, 4, 2 },
  [5441] = { "Petite sacoche de poudre", nil, 1, 10, 0, "Divers", "Divers", 20, "", 133581, 5, 15, 0 },
  [2516] = { "Balles légères", nil, 1, 5, 1, "Projectile", "Balle", 200, "INVTYPE_AMMO", 132384, 0, 6, 3 },
  [2519] = { "Balles lourdes", nil, 1, 15, 10, "Projectile", "Balle", 200, "INVTYPE_AMMO", 132384, 0, 6, 3 },
  [4306] = { "Étoffe de soie", nil, 1, 25, 0, "Artisanat", "Tissu", 20, "", 132905, 150, 7, 5 },
  -- récompenses de quête (inventées pour les tests)
  [9001] = { "Arc des marais", "|cnIQ2:|Hitem:9001::::::::25:1485:::::::::|h[Arc des marais]|h|r", 2, 26, 21, "Arme", "Arcs", 1, "INVTYPE_RANGED", 135490, 1500, 2, 2 },
  [9002] = { "Robe du marin", "|cnIQ2:|Hitem:9002::::::::25:1485:::::::::|h[Robe du marin]|h|r", 2, 25, 20, "Armure", "Tissu", 1, "INVTYPE_ROBE", 132644, 800, 4, 1 },
  [9003] = { "Gants de pisteur", "|cnIQ2:|Hitem:9003::::::::25:1485:::::::::|h[Gants de pisteur]|h|r", 2, 25, 20, "Armure", "Cuir", 1, "INVTYPE_HAND", 132952, 700, 4, 2 },
  [9004] = { "Potion de soins", nil, 1, 25, 15, "Consommable", "Potion", 5, "", 134830, 100, 0, 1 },
}

local REWARDS = {
  [289] = { money = 1500, xp = 2150, choices = { 9001, 9002, 9003 }, items = { { 9004, 2 } },
            factions = { { 47, 250 } } },
  [275] = { money = 900, xp = 1800, choices = {}, items = {}, factions = {} },
}
M.selectedQuest = 0
M.selectCalls = 0

local function itemIdOf(arg)
  if type(arg) == "number" then return arg end
  if type(arg) == "string" then return tonumber(arg:match("item:(%d+)")) end
end

local BAGS = {
  [0] = { name = "Sac à dos", slots = 20, items = {
    [1] = { id = 5441, count = 1 }, [2] = { id = 4306, count = 12 }, [3] = { id = 2519, count = 200 },
  } },
  [1] = { name = "Petite giberne", slots = 10, family = 2, items = {
    [1] = { id = 2516, count = 200 }, [2] = { id = 2516, count = 150 },
  } },
  [2] = { name = "Sac en lin", slots = 6, items = {} },
  [-1] = { name = nil, slots = 32, items = { [1] = { id = 4306, count = 20 } } }, -- banque (inventé)
  [5] = { name = "Sac de banque", slots = 8, items = { [4] = { id = 2519, count = 200 } } }, -- inventé
}

local QUESTS = {
  { isHeader = true, title = "Les Paluns" },
  { questID = 289, title = "Purger la contrée", level = 24, difficultyLevel = 24, frequency = 0,
    objectives = { { text = "Raptor des Paluns tué : 4/10", type = "monster", finished = false, numFulfilled = 4, numRequired = 10 } } },
  { questID = 275, title = "Ennemis du port", level = 25, difficultyLevel = 25, frequency = 0,
    objectives = { { text = "  : 0/3", type = "item", finished = false, numFulfilled = 0, numRequired = 3 } } },
  { isHeader = true, title = "JcJ" },
  { questID = 8374, title = "La revendication du bassin d'Arathi", level = 29, difficultyLevel = 29, frequency = 0,
    objectives = { { text = "  : 0/3", type = "item", finished = false, numFulfilled = 0, numRequired = 3 } } },
}

local FACTIONS = {
  { factionID = 469, name = "Alliance", isHeader = true, isCollapsed = false, reaction = 5, currentStanding = 4936,
    currentReactionThreshold = 3000, nextReactionThreshold = 9000 },
  { factionID = 69, name = "Darnassus", isChild = true, reaction = 5, currentStanding = 4886,
    currentReactionThreshold = 3000, nextReactionThreshold = 9000 },
  { factionID = 47, name = "Forgefer", isChild = true, reaction = 5, currentStanding = 5600,
    currentReactionThreshold = 3000, nextReactionThreshold = 9000 },
  { factionID = 1169, name = "Autres", isHeader = true, isCollapsed = true, reaction = 0 }, -- replié (test)
  { factionID = 21, name = "Baie-du-Butin", isChild = true, reaction = 4, currentStanding = 200,
    currentReactionThreshold = 0, nextReactionThreshold = 3000, hiddenWhenCollapsed = true },
}

local function visibleFactions()
  local out, hide = {}, false
  for _, f in ipairs(FACTIONS) do
    if f.isHeader then
      hide = f.isCollapsed
      out[#out + 1] = f
    elseif not hide then
      out[#out + 1] = f
    end
  end
  return out
end

local TRAIT_NODES = { 104960, 104961, 104962, 104963, 104964 }
local NODE_INFO = { -- inventé : rangs pris pour tester GetNodeInfo
  [104960] = { activeRank = 3, maxRanks = 5, entry = 500, spell = 19151, name = "Tir amélioré" },
  [104961] = { activeRank = 2, maxRanks = 2, entry = 501, spell = 19552, name = "Aspect du faucon amélioré" },
  [104962] = { activeRank = 0, maxRanks = 3, entry = 502, spell = 19420, name = "Endurance" },
  [104963] = { activeRank = 1, maxRanks = 1, entry = 503, spell = 19434, name = "Visée" },
  [104964] = { activeRank = 0, maxRanks = 5, entry = 504, spell = 19168, name = "Pistage" },
}

function M.install(G)
  G.date, G.time = os.date, os.time
  G.WOW_PROJECT_ID = 18
  G.NUM_BAG_SLOTS = 4
  G.NUM_BANKBAGSLOTS = 7
  G.BANK_CONTAINER = -1
  G.FACTION_STANDING_LABEL4 = "Neutre"
  G.FACTION_STANDING_LABEL5 = "Amical"
  G.Enum = { SpellBookSpellBank = { Player = 0, Pet = 1 }, BagIndex = { Bank = -1 } }
  G.SlashCmdList = {}
  G.DEFAULT_CHAT_FRAME = { AddMessage = function(_, msg) table.insert(M.chat, msg) end }
  G.CreateFrame = function(kind, name) return frameObject(kind, name) end
  G.Minimap = frameObject("Frame", "Minimap")
  G.GameTooltip = frameObject("GameTooltip", "GameTooltip")
  G.GetCursorPosition = function() return 600, 500 end
  G.C_UI = { Reload = function() M.reloads = M.reloads + 1 end }
  G.ReloadUI = function() M.reloads = M.reloads + 1 end
  G.GetBindingAction = function(key) return M.bindings[key] or "" end
  G.GetBindingKey = function(action)
    for k, a in pairs(M.bindings) do if a == action then return k end end
  end
  G.SetBinding = function(key, action) M.bindings[key] = action; return true end
  G.GetCurrentBindingSet = function() return 2 end
  G.SaveBindings = function(set) M.savedBindings = set end
  G.C_Timer = { After = function(delay, fn) table.insert(M.timers, { delay = delay, fn = fn }) end }
  G.GetTime = function() return M.clock end
  G.InCombatLockdown = function() return M.state.inCombat end
  G.UnitAffectingCombat = function() return M.state.inCombat end

  -- identité
  G.UnitGUID = function(u) if u == "player" then return "Player-1234-0A1B2C3D" end end
  G.UnitName = function(u)
    if u == "player" then return "Brannok", "Durn" end
    if u == "pet" then return "Félin" end
    if u == "party1" then return "Brunhilde" end
  end
  G.UnitFullName = G.UnitName
  G.GetRealmName = function() return "CAMWOW EU4 Realm 6 PvP" end
  G.GetNormalizedRealmName = function() return "CAMWOWEU4Realm6PvP" end
  G.GetRealmID = function() return 1234 end
  G.GetCurrentRegion = function() return 3 end
  G.GetCurrentRegionName = function() return "EU" end
  G.GetAccountExpansionLevel = function() return 0 end
  G.C_GameRules = {
    IsHardcoreActive = function() return false end,
    GetActiveGameMode = function() return 1 end,
    GetForeverExperiencePreset = function() return 1 end, -- inventé
    IsSelfFoundAllowed = function() return false end, -- inventé
    GetCurrentGameModeDisplayInfo = function() return { name = "Forever", recordID = 7 } end, -- inventé
    GetCurrentGameModeRecordID = function() return 7 end,
    IsStandard = function() return true end,
  }
  G.C_Roleset = { GetActiveAllowedRolesets = function() return { 2 } end, GetActiveBlockedRolesets = function() return {} end }
  G.C_PvP = { IsWarModeActive = function() return false end }
  G.GetLocale = function() return "frFR" end
  G.GetBuildInfo = function() return "1.60.1", "70938", "Nov 12 2026", 16001 end
  G.UnitRace = function() return "Nain", "Dwarf", 3 end
  G.UnitClass = function(u)
    if u == "party1" then return "Guerrier", "WARRIOR", 1 end
    return "Chasseur", "HUNTER", 3
  end
  G.UnitSex = function() return 2 end
  G.UnitFactionGroup = function() return "Alliance", "Alliance" end
  G.UnitLevel = function(u) if u == "pet" then return 24 end return 25 end
  G.GetGuildInfo = function() return nil end
  G.UnitExists = function(u) return u == "player" or u == "pet" or u == "party1" end

  -- progression
  G.UnitXP = function() return 27088 end
  G.UnitXPMax = function() return 34000 end
  G.GetXPExhaustion = function() return 912 end
  G.GetRestState = function() return 1, "En forme", 2 end
  G.IsResting = function() return false end
  G.GetMaxPlayerLevel = function() return 60 end
  G.IsXPUserDisabled = function() return false end
  G.RequestTimePlayed = function()
    table.insert(M.timers, { delay = 0.2, fn = function() M.fire("TIME_PLAYED_MSG", 173365, 7481) end })
  end
  G.ChatFrame_DisplayTimePlayed = function() table.insert(M.chat, "Temps de jeu total : 2 jours") end

  -- position
  G.GetZoneText = function() return "Les Paluns" end
  G.GetRealZoneText = function() return "Les Paluns" end
  G.GetSubZoneText = function() return "Port de Menethil" end
  G.GetBindLocation = function() return "Forgefer" end
  G.GetInstanceInfo = function() return "Royaumes de l'est", "none", 0, "", 0, 0, false, 0, 0 end
  G.C_Map = {
    GetBestMapForUnit = function() return 1437 end,
    GetPlayerMapPosition = function() return vector(0.0951, 0.5833) end,
    GetMapInfo = function(id)
      if id == 1437 then return { mapID = 1437, name = "Les Paluns", mapType = 3, parentMapID = 1415 } end
      if id == 1415 then return { mapID = 1415, name = "Royaumes de l'est", mapType = 2, parentMapID = 947 } end
    end,
  }

  -- stats
  local STATS = { { 48, 48, 15, 0 }, { 73, 73, 23, 0 }, { 81, 81, 34, 0 }, { 44, 44, 12, 0 }, { 62, 62, 26, 0 } }
  G.UnitStat = function(_, i) return table.unpack(STATS[i]) end
  G.UnitAttackPower = function() return 168, 65, 0 end
  G.UnitRangedAttackPower = function() return 193, 40, 0 end
  G.UnitDamage = function() return 62.2785758972168, 84.27857971191406, 0, 0, 0, 0, 1 end
  G.UnitRangedDamage = function() return 2.091000080108643, 76.27857971191406, 96.27857971191406, 0, 0, 1 end
  G.UnitAttackSpeed = function() return 2.299999952316284 end
  G.UnitArmor = function() return 190, 780, 780, 590 end
  G.UnitResistance = function() return 5, 5, 5, 0 end
  G.UnitDefenseSkill = function() return 116, 0 end
  G.UnitHealthMax = function() return 922 end
  G.UnitPowerMax = function() return 991 end
  G.UnitPowerType = function() return 0, "MANA" end
  G.GetCritChance = function() return 7.399499416351318 end
  G.GetRangedCritChance = function() return 7.719500541687012 end
  G.GetSpellCritChance = function() return 9.139999389648438 end
  G.GetHitModifier = function() return 1 end
  G.GetRangedHitModifier = function() return 1 end
  G.GetDodgeChance = function() return 7.166299819946289 end
  G.GetParryChance = function() return 4.639999866485596 end
  G.GetBlockChance = function() return 0 end
  G.GetManaRegen = function() return 14.00100040435791, 0.001000000047497451 end
  G.UnitUsesAmmo = function() return true end
  G.C_PaperDollInfo = { AmmoNeeded = function() return true end }
  G.GetAverageItemLevel = function() return 18.375, 18.125, 18.375 end

  -- équipement
  local EQUIPPED = { [5] = CHEST_LINK, [16] = MAIN_LINK, [18] = RANGED_LINK }
  local SLOT_IDS = {
    HeadSlot = 1, NeckSlot = 2, ShoulderSlot = 3, ShirtSlot = 4, ChestSlot = 5, WaistSlot = 6, LegsSlot = 7,
    FeetSlot = 8, WristSlot = 9, HandsSlot = 10, Finger0Slot = 11, Finger1Slot = 12, Trinket0Slot = 13,
    Trinket1Slot = 14, BackSlot = 15, MainHandSlot = 16, SecondaryHandSlot = 17, RangedSlot = 18, TabardSlot = 19,
    AmmoSlot = 0,
  }
  G.GetInventorySlotInfo = function(name) return SLOT_IDS[name], 136520, name == "RangedSlot" end
  G.GetInventoryItemLink = function(_, slot) return EQUIPPED[slot] end
  G.GetInventoryItemQuality = function(_, slot) local id = itemIdOf(EQUIPPED[slot]); return id and ITEMS[id][3] end
  G.GetInventoryItemDurability = function(slot) if EQUIPPED[slot] then return 69, 70 end end
  G.GetWeaponEnchantInfo = function() return false end
  G.C_Item = {
    GetItemInfo = function(arg)
      local id = itemIdOf(arg)
      local it = id and ITEMS[id]
      if not it then return nil end
      return table.unpack(it)
    end,
    GetItemStats = function(link)
      local id = itemIdOf(link)
      if id == 2098 then return { ITEM_MOD_AGILITY_SHORT = 3, ITEM_MOD_DAMAGE_PER_SECOND_SHORT = 13.2608699798584, ITEM_MOD_STRENGTH_SHORT = 3 } end
      if id == 1937 then return { ITEM_MOD_DAMAGE_PER_SECOND_SHORT = 10.5, ITEM_MOD_STAMINA_SHORT = 2 } end
      if id == 6085 then return { RESISTANCE0_NAME = 120, ITEM_MOD_AGILITY_SHORT = 4 } end
      if id == 9001 then return { ITEM_MOD_DAMAGE_PER_SECOND_SHORT = 14.8, ITEM_MOD_AGILITY_SHORT = 2 } end
      if id == 9002 then return { RESISTANCE0_NAME = 30, ITEM_MOD_INTELLECT_SHORT = 5 } end
      if id == 9003 then return { RESISTANCE0_NAME = 60, ITEM_MOD_AGILITY_SHORT = 3, ITEM_MOD_STAMINA_SHORT = 2 } end
      return {}
    end,
    GetDetailedItemLevelInfo = function(link) local id = itemIdOf(link); return id and ITEMS[id] and ITEMS[id][4] end,
    GetItemInfoInstant = function(arg)
      local id = itemIdOf(arg); local it = id and ITEMS[id]
      if not it then return nil end
      return id, it[6], it[7], it[9], it[10], it[12], it[13]
    end,
    RequestLoadItemDataByID = function() end,
  }
  G.C_TooltipInfo = {
    GetInventoryItem = function(_, slot)
      if not EQUIPPED[slot] then return nil end
      return { id = itemIdOf(EQUIPPED[slot]), repairCost = 9, lines = {
        { leftText = ITEMS[itemIdOf(EQUIPPED[slot])][1] },
        { leftText = "Lié quand équipé" },
        { leftText = "Distance", rightText = "Fusil" },
        { leftText = "Durabilité 69 / 70" },
      } }
    end,
  }

  -- talents
  G.GetNumSpecializations = function() return 1 end
  G.C_SpecializationInfo = {
    GetSpecialization = function() return 1 end,
    GetSpecializationInfo = function() return 1485, "Chasseur", "", 626000, "DAMAGER", 4, 0 end,
    GetActiveSpecGroup = function() return 1 end,
    HasPlayerEarnedATalentPoint = function() return true end,
  }
  G.C_ClassTalents = { GetActiveConfigID = function() return 3758979 end }
  G.C_Traits = {
    GetConfigInfo = function() return { ID = 3758979, name = "Chasseur", treeIDs = { 1091 }, type = 4 } end,
    GetTreeNodes = function() return TRAIT_NODES end,
    GetTreeCurrencyInfo = function() return { { traitCurrencyID = 3001, quantity = 10, maxQuantity = 16, spent = 6 } } end,
    GetNodeInfo = function(_, nodeId)
      local n = NODE_INFO[nodeId]
      return { ID = nodeId, activeRank = n.activeRank, ranksPurchased = n.activeRank, maxRanks = n.maxRanks,
               activeEntry = { entryID = n.entry, rank = n.activeRank }, entryIDs = { n.entry }, posX = 100, posY = 200 }
    end,
    GetEntryInfo = function(_, entryId) return { definitionID = entryId + 1000 } end,
    GetDefinitionInfo = function(defId)
      for _, n in pairs(NODE_INFO) do if n.entry + 1000 == defId then return { spellID = n.spell } end end
    end,
  }

  -- sorts
  G.C_SpellBook = {
    GetNumSpellBookSkillLines = function() return 2 end,
    GetSpellBookSkillLineInfo = function(i)
      if i == 1 then return { name = "Général", itemIndexOffset = 0, numSpellBookItems = 2 } end
      return { name = "Maîtrise des bêtes", itemIndexOffset = 2, numSpellBookItems = 2 }
    end,
    GetSpellBookItemInfo = function(idx, bank)
      if bank == 1 then
        local pet = { { spellID = 17253, name = "Morsure", subName = "Rang 3" }, { spellID = 24450, name = "Rôder", subName = "Rang 1" } }
        local s = pet[idx]; if s then s.itemType = 3 end
        return s
      end
      local list = {
        { spellID = 6603, name = "Attaque", subName = "", itemType = 1 },
        { spellID = 75, name = "Tir automatique", subName = "", itemType = 1 },
        { spellID = 1515, name = "Dressage des bêtes", subName = "", itemType = 1 },
        { spellID = 13165, name = "Aspect du faucon", subName = "Rang 2", itemType = 1 },
      }
      return list[idx]
    end,
    HasPetSpells = function() return 2, "PET" end,
  }
  G.C_Spell = { GetSpellName = function(id)
    for _, n in pairs(NODE_INFO) do if n.spell == id then return n.name end end
  end }

  -- quêtes
  G.C_QuestLog = {
    GetNumQuestLogEntries = function() return #QUESTS, 3 end,
    GetMaxNumQuestsCanAccept = function() return 20 end,
    GetInfo = function(i)
      local q = QUESTS[i]; if not q then return nil end
      return { isHeader = q.isHeader or false, title = q.title, questID = q.questID or 0, level = q.level or 0,
               difficultyLevel = q.difficultyLevel or 0, frequency = q.frequency, isHidden = false,
               suggestedGroup = 0, isOnMap = true }
    end,
    GetTitleForQuestID = function(id) for _, q in ipairs(QUESTS) do if q.questID == id then return q.title end end end,
    IsComplete = function(id) return id == 289 end,
    IsFailed = function() return false end,
    GetQuestType = function() return 0 end,
    GetQuestTagInfo = function(id) if id == 8374 then return { tagID = 41, tagName = "JcJ" } end end,
    GetQuestObjectives = function(id) for _, q in ipairs(QUESTS) do if q.questID == id then return q.objectives end end end,
    GetQuestsOnMap = function(mapId)
      if mapId ~= 1437 then return {} end
      return { { questID = 275, mapID = 1437, x = 0.2295818328857422, y = 0.284837543964386 },
               { questID = 289, mapID = 1437, x = 0.140836238861084, y = 0.3000756502151489 } }
    end,
    GetTrivialRange = function() return 6 end,
    GetSelectedQuest = function() return M.selectedQuest end,
    SetSelectedQuest = function(id) M.selectCalls = M.selectCalls + 1; M.selectedQuest = id end,
    GetAllCompletedQuestIDs = function() return { 19, 20, 34, 65, 89, 91, 115 } end,
  }
  G.GetQuestLogLeaderBoard = function(obj, logIndex)
    if logIndex == 3 then return "Insigne de la Confrérie : 0/3" end
    return nil
  end
  G.GetDailyQuestsCompleted = function() return 0 end
  -- récompenses (comme le client retail : le choix et les liens dépendent de la quête sélectionnée)
  local function rw(id) return REWARDS[id] end
  local function info(id)
    local it = ITEMS[id]
    return it[1], it[10], 1, it[3], true, id, it[4]
  end
  G.GetQuestLogRewardMoney = function(id) return rw(id) and rw(id).money or 0 end
  G.GetQuestLogRewardXP = function(id) return rw(id) and rw(id).xp or 0 end
  G.GetNumQuestLogChoices = function(id) return rw(id) and #rw(id).choices or 0 end
  G.GetNumQuestLogRewards = function(id) return rw(id) and #rw(id).items or 0 end
  G.GetQuestLogChoiceInfo = function(i)
    local r = rw(M.selectedQuest); local id = r and r.choices[i]
    if id then return info(id) end
  end
  G.GetQuestLogRewardInfo = function(i, qid)
    local r = rw(qid or M.selectedQuest); local e = r and r.items[i]
    if e then local a, b, _, d, ee, f, g = info(e[1]); return a, b, e[2], d, ee, f, g end
  end
  G.GetQuestLogItemLink = function(kind, i)
    local r = rw(M.selectedQuest); if not r then return nil end
    local id = (kind == "choice") and r.choices[i] or (r.items[i] and r.items[i][1])
    return id and ITEMS[id] and ITEMS[id][2]
  end
  G.GetNumQuestLogRewardFactions = function(id) return rw(id) and #rw(id).factions or 0 end
  G.GetQuestLogRewardFactionInfo = function(i, id)
    local f = rw(id) and rw(id).factions[i]
    if f then return f[1], f[2], 0 end
  end
  G.C_QuestInfoSystem = { GetQuestLogRewardFavor = function() return 0 end }

  -- métiers
  G.GetProfessions = function() return 5, 7, nil, nil, 9 end
  G.GetProfessionInfo = function(idx)
    if idx == 5 then return "Travail du cuir", 136247, 106, 150, 1, 58, 165, 0, -1, 0, "Travail du cuir" end
    if idx == 7 then return "Dépeçage", 134366, 112, 150, 1, 60, 393, 0, -1, 0, "Dépeçage" end -- inventé
    if idx == 9 then return "Cuisine", 133971, 40, 75, 1, 70, 185, 0, -1, 0, "Cuisine" end -- inventé
  end
  local SKILLS = {
    { isHeader = true, name = "Compétences de classe" },
    { name = "Maîtrise des bêtes", skillID = 50, rank = 1, maxRank = 1, modifier = 0 },
    { isHeader = true, name = "Langues" },
    { name = "Langue : nain", skillID = 111, rank = 300, maxRank = 300, modifier = 0 },
  }
  G.C_SkillInfo = {
    GetNumSkillLines = function() return #SKILLS end,
    GetSkillLineInfo = function(i) local s = SKILLS[i]; return s and { isHeader = s.isHeader or false, name = s.name,
      skillID = s.skillID or 0, rank = s.rank or 0, maxRank = s.maxRank or 0, modifier = s.modifier or 0, tempPoints = 0 } end,
  }
  G.C_TradeSkillUI = {
    IsTradeSkillReady = function() return M.state.tradeSkillOpen end,
    IsTradeSkillLinked = function() return false end,
    IsNPCCrafting = function() return false end,
    GetBaseProfessionInfo = function()
      if not M.state.tradeSkillOpen then return { professionName = "", professionID = 0 } end
      return { professionID = 165, professionName = "Travail du cuir", skillLevel = 106, maxSkillLevel = 150 }
    end,
    GetAllRecipeIDs = function()
      if not M.state.tradeSkillOpen then return {} end
      return { 2149, 2152, 3753 }
    end,
    GetRecipeInfo = function(id)
      local r = { [2149] = { "Bottes en cuir pour poignets", true, 3 }, [2152] = { "Armure en cuir léger", true, 2 },
                  [3753] = { "Ceinture en cuir épais", false, 1 } } -- inventé
      local x = r[id]
      return { recipeID = id, name = x[1], learned = x[2], relativeDifficulty = x[3], numSkillUps = 1,
               craftable = true, numAvailable = 0, categoryID = 10 }
    end,
  }

  -- familier
  G.HasPetUI = function() return true, true end
  G.UnitCreatureFamily = function() return "Félin", 2 end
  G.GetPetExperience = function() return 2475, 7925 end
  G.C_PetInfo = {
    GetPetHappiness = function() return 3, 125, 20 end,
    GetPetLoyalty = function() return "(Niveau de loyauté 6) Meilleur ami" end,
    GetPetTrainingPoints = function() return 120, 76 end,
    GetPetFoodTypes = function() return { "Viande", "Poisson" } end,
    GetPetTalentTree = function() return nil end,
  }
  G.C_StableInfo = {
    GetNumActivePets = function() return 1 end,
    GetStablePetInfo = function() return { slotID = 1, name = "Félin", familyName = "Félin", level = 24,
      loyaltyLevel = 6, loyaltyName = "(Niveau de loyauté 6) Meilleur ami", happinessLevel = 3, isExotic = false,
      specialization = "Par défaut", petNumber = 1412027 } end,
    GetStabledPetList = function() return {} end,
  }

  -- sacs, banque, argent
  G.C_Container = {
    GetContainerNumSlots = function(bag)
      local b = BAGS[bag]
      if not b then return 0 end
      if bag == 5 and not M.state.bankOpen then return 0 end
      return b.slots
    end,
    GetContainerNumFreeSlots = function(bag)
      local b = BAGS[bag]; if not b then return 0, 0 end
      local used = 0; for _ in pairs(b.items) do used = used + 1 end
      return b.slots - used, b.family or 0
    end,
    GetContainerItemInfo = function(bag, slot)
      local b = BAGS[bag]; local it = b and b.items[slot]
      if not it then return nil end
      local def = ITEMS[it.id]
      return { itemID = it.id, itemName = def[1], hyperlink = "|cnIQ1:|Hitem:" .. it.id .. "|h[" .. def[1] .. "]|h|r",
               stackCount = it.count, quality = def[3], isBound = false, hasNoValue = false }
    end,
    GetBagName = function(bag) return BAGS[bag] and BAGS[bag].name end,
  }
  G.GetMoney = function() return 24016 end

  -- réputations (avec une catégorie repliée pour tester dépliage/restauration)
  G.C_Reputation = {
    GetFactionDataByID = function(id)
      for _, f in ipairs(FACTIONS) do if f.factionID == id then return { factionID = id, name = f.name } end end
    end,
    GetNumFactions = function() return #visibleFactions() end,
    GetFactionDataByIndex = function(i)
      local f = visibleFactions()[i]; if not f then return nil end
      local copy = {}; for k, v in pairs(f) do copy[k] = v end
      return copy
    end,
    ExpandFactionHeader = function(i)
      local f = visibleFactions()[i]; if f then f.isCollapsed = false end
      M.fire("UPDATE_FACTION") -- comme le jeu : l'action déclenche un événement
    end,
    CollapseFactionHeader = function(i)
      local f = visibleFactions()[i]; if f then f.isCollapsed = true end
      M.fire("UPDATE_FACTION")
    end,
  }
  M.FACTIONS = FACTIONS
  G.C_MajorFactions = { GetMajorFactionIDs = function() return { 2800 } end,
    GetMajorFactionData = function() return { name = "Faveur des marchands", renownLevel = 1,
      renownReputationEarned = 120, renownLevelThreshold = 2500, isUnlocked = true } end } -- inventé

  -- monnaies
  G.C_CurrencyInfo = {
    GetCurrencyListSize = function() return 2 end,
    GetCurrencyListInfo = function(i)
      if i == 1 then return { isHeader = true, name = "Divers" } end
      return { isHeader = false, name = "Marque d'honneur", currencyID = 0, quantity = 3, maxQuantity = 0, discovered = true }
    end,
    GetCurrencyListLink = function(i) if i == 2 then return "|cffffffff|Hcurrency:1901:0|h[Marque d'honneur]|h|r" end end,
  }

  -- groupe, buffs, collections
  G.IsInGroup = function() return true end
  G.IsInRaid = function() return false end
  G.GetNumGroupMembers = function() return 2 end
  G.UnitGroupRolesAssigned = function() return "TANK" end
  G.C_UnitAuras = { GetAuraDataByIndex = function(_, i)
    if i == 1 then return { name = "Aspect du faucon", spellId = 13165, expirationTime = 0, applications = 0, isFromPlayerOrPlayerPet = true } end
    if i == 2 then return { name = "Bien nourri", spellId = 19705, expirationTime = M.clock + 600, applications = 1 } end
  end }
  G.C_MountJournal = {
    GetNumMounts = function() return 136 end,
    GetMountIDs = function() return { 6, 8, 11 } end,
    GetMountInfoByID = function(id) return "Monture " .. id, 0, 0, false, true, 0, false, false, 0, false, id == 6 end,
  }
  G.GetNumCompletedAchievements = function() return 111, 4 end
  G.GetTotalAchievementPoints = function() return 0 end
  G.C_PetJournal = { GetNumPets = function() return 0, 0 end }
end

return M
