-- ForeverScribe : familier, réputations, monnaies, groupe, buffs, collections
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS
local get, plain = ns.get, ns.plain

-- ---------------------------------------------------------------- familier

local SPELLBANK_PET = (_G.Enum and _G.Enum.SpellBookSpellBank and _G.Enum.SpellBookSpellBank.Pet) or 1

local function currentPet()
  if not get("UnitExists", "pet") then return nil end
  local family, familyId = get("UnitCreatureFamily", "pet")
  local happiness, damagePct, loyaltyRate = get("C_PetInfo.GetPetHappiness")
  local tpTotal, tpSpent = get("C_PetInfo.GetPetTrainingPoints")
  local xp, xpMax = get("GetPetExperience")
  local pet = {
    name = get("UnitName", "pet"),
    level = get("UnitLevel", "pet"),
    family = family, familyId = familyId,
    xp = xp, xpMax = xpMax,
    happiness = happiness and { level = happiness, damagePct = damagePct, loyaltyRate = loyaltyRate } or nil,
    loyalty = get("C_PetInfo.GetPetLoyalty"),
    trainingPoints = tpTotal and { total = tpTotal, spent = tpSpent,
      available = (tpTotal and tpSpent) and (tpTotal - tpSpent) or nil } or nil,
    food = ns.list(get("C_PetInfo.GetPetFoodTypes")),
    abilities = {},
  }
  local n = get("C_SpellBook.HasPetSpells")
  if type(n) == "number" and ns.readSpellItem then
    for i = 1, n do
      local s = ns.readSpellItem(i, SPELLBANK_PET)
      if s and s.name then pet.abilities[#pet.abilities + 1] = s end
    end
  end
  pet.talentTree = plain(get("C_PetInfo.GetPetTalentTree"), 3)
  return pet
end

local function stableInfo()
  local out = { active = {}, stabled = {} }
  local n = get("C_StableInfo.GetNumActivePets") or 0
  for i = 1, n do
    local p = get("C_StableInfo.GetStablePetInfo", i)
    if type(p) == "table" then
      out.active[#out.active + 1] = {
        slot = p.slotID or i, name = p.name, family = p.familyName, level = p.level,
        loyaltyLevel = p.loyaltyLevel, loyaltyName = p.loyaltyName, happiness = p.happinessLevel,
        exotic = p.isExotic or nil, specialization = p.specialization, petNumber = p.petNumber,
      }
    end
  end
  local stabled = get("C_StableInfo.GetStabledPetList")
  if type(stabled) == "table" then
    for _, p in ipairs(stabled) do
      if type(p) == "table" then
        out.stabled[#out.stabled + 1] = {
          slot = p.slotID, name = p.name, family = p.familyName, level = p.level,
          loyaltyLevel = p.loyaltyLevel, happiness = p.happinessLevel,
        }
      end
    end
  end
  return out
end

ns.RegisterDomain("pet", {
  label = "Familier",
  logout = true,
  events = { PET_UI_UPDATE = true, PET_BAR_UPDATE = true, PET_STABLE_UPDATE = true, PET_STABLE_CLOSED = true },
  unitEvents = { UNIT_PET = "player", UNIT_HAPPINESS = "pet", UNIT_LEVEL = "pet", UNIT_PET_EXPERIENCE = "pet" },
  collect = function(_, previous)
    local hasUI = get("HasPetUI")
    local cur = currentPet()
    local out = {
      hasPetUI = hasUI and true or false,
      active = cur ~= nil,
      current = cur,
      lastSeen = cur or (previous and (previous.current or previous.lastSeen)) or nil,
      stable = stableInfo(),
    }
    if cur then
      out.lastSeenAt = ns.now()
    elseif previous then
      out.lastSeenAt = previous.lastSeenAt
    end
    return out
  end,
})

-- ---------------------------------------------------------------- réputations

local function standingLabel(reaction)
  if not reaction then return nil end
  return _G["FACTION_STANDING_LABEL" .. reaction]
end

ns.RegisterDomain("reputations", {
  label = "Réputations",
  events = { UPDATE_FACTION = true, QUEST_TURNED_IN = true },
  collect = function()
    local expanded = {}
    local canExpand = ns.api("C_Reputation.ExpandFactionHeader") and ns.api("C_Reputation.CollapseFactionHeader")
    -- Déplie temporairement les catégories repliées pour tout lire, puis restaure
    if canExpand then
      local i = 1
      while i <= (get("C_Reputation.GetNumFactions") or 0) and i < 500 do
        local f = get("C_Reputation.GetFactionDataByIndex", i)
        if type(f) == "table" and f.isHeader and f.isCollapsed then
          expanded[f.factionID or f.name] = true
          ns.call("C_Reputation.ExpandFactionHeader", i)
        end
        i = i + 1
      end
    end

    local list, header = {}, nil
    local n = get("C_Reputation.GetNumFactions") or 0
    for i = 1, n do
      local f = get("C_Reputation.GetFactionDataByIndex", i)
      if type(f) == "table" then
        if f.isHeader and not f.isHeaderWithRep then
          header = f.name
        else
          local min, max = f.currentReactionThreshold, f.nextReactionThreshold
          list[#list + 1] = {
            id = f.factionID, name = f.name, category = header,
            reaction = f.reaction, standing = standingLabel(f.reaction),
            value = f.currentStanding, min = min, max = max,
            progress = (min and max and f.currentStanding and max > min)
              and (f.currentStanding - min) .. "/" .. (max - min) or nil,
            atWar = f.atWarWith or nil, watched = f.isWatched or nil,
          }
        end
      end
    end

    if canExpand and next(expanded) then
      for i = (get("C_Reputation.GetNumFactions") or 0), 1, -1 do
        local f = get("C_Reputation.GetFactionDataByIndex", i)
        if type(f) == "table" and f.isHeader and expanded[f.factionID or f.name] then
          ns.call("C_Reputation.CollapseFactionHeader", i)
        end
      end
    end

    local major = {}
    local ids = get("C_MajorFactions.GetMajorFactionIDs")
    if type(ids) == "table" then
      for _, id in ipairs(ids) do
        local d = get("C_MajorFactions.GetMajorFactionData", id)
        if type(d) == "table" then
          major[#major + 1] = {
            id = id, name = d.name, renownLevel = d.renownLevel,
            renownXp = d.renownReputationEarned, renownXpMax = d.renownLevelThreshold,
            unlocked = d.isUnlocked,
          }
        end
      end
    end
    return { list = list, major = major }
  end,
})

-- ---------------------------------------------------------------- monnaies

ns.RegisterDomain("currencies", {
  label = "Monnaies",
  events = { CURRENCY_DISPLAY_UPDATE = true },
  collect = function()
    local list, header = {}, nil
    local n = get("C_CurrencyInfo.GetCurrencyListSize") or 0
    for i = 1, n do
      local c = get("C_CurrencyInfo.GetCurrencyListInfo", i)
      if type(c) == "table" then
        if c.isHeader then
          header = c.name
        elseif c.discovered ~= false then
          local link = get("C_CurrencyInfo.GetCurrencyListLink", i)
          local id = c.currencyID
          if (not id or id == 0) and type(link) == "string" then
            id = tonumber(link:match("currency:(%d+)"))
          end
          list[#list + 1] = {
            id = id, name = c.name, category = header, quantity = c.quantity,
            max = (c.maxQuantity and c.maxQuantity > 0) and c.maxQuantity or nil,
            weekly = (c.canEarnPerWeek and c.maxWeeklyQuantity) or nil,
          }
        end
      end
    end
    return { list = list }
  end,
})

-- ---------------------------------------------------------------- groupe

ns.RegisterDomain("group", {
  label = "Groupe",
  logout = true,
  events = { GROUP_ROSTER_UPDATE = true },
  collect = function()
    local inGroup = get("IsInGroup") and true or false
    local inRaid = get("IsInRaid") and true or false
    local out = { inGroup = inGroup, inRaid = inRaid, size = get("GetNumGroupMembers") or 0, members = {} }
    if inGroup then
      local prefix, count = "party", (out.size - 1)
      if inRaid then prefix, count = "raid", out.size end
      for i = 1, count do
        local unit = prefix .. i
        if get("UnitExists", unit) then
          local _, classFile = get("UnitClass", unit)
          out.members[#out.members + 1] = {
            name = get("UnitName", unit), class = classFile, level = get("UnitLevel", unit),
            role = get("UnitGroupRolesAssigned", unit),
          }
        end
      end
    end
    return out
  end,
})

-- ---------------------------------------------------------------- buffs

ns.RegisterDomain("buffs", {
  label = "Effets actifs",
  logout = true,
  collect = function()
    local list = {}
    local now = get("GetTime") or 0
    for i = 1, 40 do
      local a = get("C_UnitAuras.GetAuraDataByIndex", "player", i, "HELPFUL")
      if type(a) ~= "table" then break end
      local remaining
      if a.expirationTime and a.expirationTime > 0 then
        remaining = math.floor(a.expirationTime - now)
      end
      list[#list + 1] = {
        name = a.name, spellId = a.spellId, stacks = (a.applications and a.applications > 1) and a.applications or nil,
        remaining = remaining, fromPlayer = a.isFromPlayerOrPlayerPet or nil,
      }
    end
    return { list = list }
  end,
})

-- ---------------------------------------------------------------- collections

ns.RegisterDomain("collections", {
  label = "Collections",
  events = { NEW_MOUNT_ADDED = true, ACHIEVEMENT_EARNED = true },
  collect = function()
    local owned = 0
    local ids = get("C_MountJournal.GetMountIDs")
    if type(ids) == "table" then
      for _, id in ipairs(ids) do
        local isCollected = select(11, get("C_MountJournal.GetMountInfoByID", id))
        if isCollected then owned = owned + 1 end
      end
    end
    local done = get("GetNumCompletedAchievements")
    return {
      mountsOwned = owned,
      mountsInJournal = get("C_MountJournal.GetNumMounts"),
      achievementsCompleted = done,
      achievementPoints = get("GetTotalAchievementPoints"),
      petsOwned = select(2, get("C_PetJournal.GetNumPets")),
    }
  end,
})
