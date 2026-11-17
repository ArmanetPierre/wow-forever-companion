-- ForeverScribe : stats, équipement, talents, sorts
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS
local get, round, plain = ns.get, ns.round, ns.plain

-- ---------------------------------------------------------------- stats

local PRIMARY = { "strength", "agility", "stamina", "intellect", "spirit" }
local SCHOOLS = { [1] = "holy", [2] = "fire", [3] = "nature", [4] = "frost", [5] = "shadow", [6] = "arcane" }

ns.RegisterDomain("stats", {
  label = "Stats",
  logout = true,
  events = { PLAYER_EQUIPMENT_CHANGED = true, PLAYER_LEVEL_UP = true, PLAYER_DAMAGE_DONE_MODS = true },
  unitEvents = {
    UNIT_STATS = "player", UNIT_ATTACK_POWER = "player", UNIT_RANGED_ATTACK_POWER = "player",
    UNIT_RESISTANCES = "player", UNIT_DAMAGE = "player", UNIT_RANGEDDAMAGE = "player",
    UNIT_ATTACK_SPEED = "player", UNIT_MAXHEALTH = "player", UNIT_MAXPOWER = "player",
  },
  collect = function()
    local out = { primary = {} }
    for i, key in ipairs(PRIMARY) do
      local base, effective, posBuff, negBuff = get("UnitStat", "player", i)
      out.primary[key] = { base = base, effective = effective, posBuff = posBuff, negBuff = negBuff }
    end

    out.health = get("UnitHealthMax", "player")
    local powerType, powerToken = get("UnitPowerType", "player")
    out.power = { max = get("UnitPowerMax", "player"), type = powerType, token = powerToken }

    local apBase, apPos, apNeg = get("UnitAttackPower", "player")
    local minD, maxD, minOff, maxOff, physPos, physNeg, pct = get("UnitDamage", "player")
    local mhSpeed, ohSpeed = get("UnitAttackSpeed", "player")
    out.melee = {
      attackPower = apBase and ((apBase or 0) + (apPos or 0) + (apNeg or 0)) or nil,
      attackPowerBase = apBase, attackPowerPos = apPos, attackPowerNeg = apNeg,
      minDamage = round(minD, 1), maxDamage = round(maxD, 1),
      offhandMinDamage = round(minOff, 1), offhandMaxDamage = round(maxOff, 1),
      speed = round(mhSpeed, 2), offhandSpeed = round(ohSpeed, 2),
      damageModPct = pct,
      crit = round(get("GetCritChance"), 2),
      hit = get("GetHitModifier"),
      dodge = round(get("GetDodgeChance"), 2),
      parry = round(get("GetParryChance"), 2),
      block = round(get("GetBlockChance"), 2),
    }
    if out.melee.minDamage and out.melee.maxDamage and mhSpeed and mhSpeed > 0 then
      out.melee.dps = round((minD + maxD) / 2 / mhSpeed, 1)
    end

    local rapBase, rapPos, rapNeg = get("UnitRangedAttackPower", "player")
    local rSpeed, rMin, rMax, rPos, rNeg, rPct = get("UnitRangedDamage", "player")
    out.ranged = {
      attackPower = rapBase and ((rapBase or 0) + (rapPos or 0) + (rapNeg or 0)) or nil,
      attackPowerBase = rapBase, attackPowerPos = rapPos, attackPowerNeg = rapNeg,
      speed = round(rSpeed, 2), minDamage = round(rMin, 1), maxDamage = round(rMax, 1),
      damageModPct = rPct,
      crit = round(get("GetRangedCritChance"), 2),
      hit = get("GetRangedHitModifier"),
      usesAmmo = get("UnitUsesAmmo", "player") and true or false,
      ammoNeeded = get("C_PaperDollInfo.AmmoNeeded") and true or false,
    }
    if rSpeed and rSpeed > 0 and rMin and rMax then
      out.ranged.dps = round((rMin + rMax) / 2 / rSpeed, 1)
    end

    out.spell = { crit = round(get("GetSpellCritChance", 2), 2) }
    local manaBase, manaCasting = get("GetManaRegen")
    out.manaRegen = { base = round(manaBase, 2), casting = round(manaCasting, 2) }

    local armorBase, armorEff, armorTotal, armorPos = get("UnitArmor", "player")
    out.armor = { base = armorBase, effective = armorEff, total = armorTotal, bonus = armorPos }
    out.resistances = {}
    for i, school in pairs(SCHOOLS) do
      local _, total = get("UnitResistance", "player", i)
      out.resistances[school] = total
    end
    out.defense = get("UnitDefenseSkill", "player")

    local overall, equipped = get("GetAverageItemLevel")
    out.itemLevel = { overall = round(overall, 1), equipped = round(equipped, 1) }
    return out
  end,
})

-- ---------------------------------------------------------------- équipement

ns.SLOTS = {
  "HeadSlot", "NeckSlot", "ShoulderSlot", "ShirtSlot", "ChestSlot", "WaistSlot", "LegsSlot",
  "FeetSlot", "WristSlot", "HandsSlot", "Finger0Slot", "Finger1Slot", "Trinket0Slot",
  "Trinket1Slot", "BackSlot", "MainHandSlot", "SecondaryHandSlot", "RangedSlot", "TabardSlot",
}

-- Texte complet de la bulle d'aide d'un objet (effets « Équipé : », bonus d'ensemble…)
function ns.TooltipLines(data)
  if type(data) ~= "table" or type(data.lines) ~= "table" then return nil end
  local lines = {}
  for _, line in ipairs(data.lines) do
    if type(line) == "table" then
      local left, right = line.leftText, line.rightText
      if left and left ~= "" then
        lines[#lines + 1] = (right and right ~= "") and (left .. " | " .. right) or left
      end
    end
  end
  return lines
end

-- Fiche d'un objet à partir de son lien (marche pour équipement, sacs, banque)
function ns.ItemRecord(link, extra)
  local rec = extra or {}
  rec.link = link
  rec.itemId = ns.itemIdFromLink(link)
  local name, _, quality, ilvl, reqLevel, itemType, subType, stackMax, equipLoc,
        _, sellPrice, classId, subclassId = get("C_Item.GetItemInfo", link)
  rec.name = name or ns.nameFromLink(link)
  rec.quality = rec.quality or quality
  rec.itemLevel = get("C_Item.GetDetailedItemLevelInfo", link) or ilvl
  rec.requiredLevel = reqLevel
  rec.type = itemType
  rec.subType = subType
  rec.equipLoc = equipLoc
  rec.classId = classId
  rec.subclassId = subclassId
  rec.sellPrice = sellPrice
  if not name then
    rec.pending = true
    ns.waitingItems = true
    if rec.itemId then ns.call("C_Item.RequestLoadItemDataByID", rec.itemId) end
  end
  local stats = get("C_Item.GetItemStats", link)
  if type(stats) == "table" then
    rec.stats = {}
    for k, v in pairs(stats) do
      if k == "ITEM_MOD_DAMAGE_PER_SECOND_SHORT" then
        rec.dps = round(v, 2)
      else
        rec.stats[k] = v
      end
    end
  end
  return rec
end

ns.RegisterDomain("equipment", {
  label = "Équipement",
  events = {
    PLAYER_EQUIPMENT_CHANGED = true, UPDATE_INVENTORY_DURABILITY = true,
    GET_ITEM_INFO_RECEIVED = function() return ns.waitingItems end,
    ITEM_DATA_LOAD_RESULT = function() return ns.waitingItems end,
  },
  collect = function()
    ns.waitingItems = false
    local out = { slots = {}, repairCost = 0 }
    for _, slotName in ipairs(ns.SLOTS) do
      local slotId = get("GetInventorySlotInfo", slotName)
      if slotId and slotId > 0 then
        local link = get("GetInventoryItemLink", "player", slotId)
        if link then
          local rec = ns.ItemRecord(link, { slotId = slotId })
          rec.quality = get("GetInventoryItemQuality", "player", slotId) or rec.quality
          local cur, max = get("GetInventoryItemDurability", slotId)
          if cur and max then rec.durability = { current = cur, max = max } end
          local tip = get("C_TooltipInfo.GetInventoryItem", "player", slotId)
          rec.tooltip = ns.TooltipLines(tip)
          if type(tip) == "table" and type(tip.repairCost) == "number" then
            out.repairCost = out.repairCost + tip.repairCost
          end
          out.slots[slotName] = rec
        end
      end
    end
    -- Enchantements temporaires d'arme (huiles, pierres à aiguiser…)
    local hasMain, mainExp, mainCharges, mainEnchant, hasOff, offExp, offCharges, offEnchant =
      get("GetWeaponEnchantInfo")
    out.tempEnchants = {
      mainHand = hasMain and { expiresInMs = mainExp, charges = mainCharges, enchantId = mainEnchant } or nil,
      offHand = hasOff and { expiresInMs = offExp, charges = offCharges, enchantId = offEnchant } or nil,
    }
    return out
  end,
})

-- ---------------------------------------------------------------- talents

local function spellNameForEntry(configId, entryId)
  local entry = get("C_Traits.GetEntryInfo", configId, entryId)
  if type(entry) ~= "table" or not entry.definitionID then return nil, nil end
  local def = get("C_Traits.GetDefinitionInfo", entry.definitionID)
  if type(def) ~= "table" then return nil, nil end
  local spellId = def.spellID or def.overriddenSpellID
  local name = def.overrideName
  if (not name or name == "") and spellId then
    name = get("C_Spell.GetSpellName", spellId)
  end
  return name, spellId
end

ns.RegisterDomain("talents", {
  label = "Talents",
  events = {
    TRAIT_CONFIG_UPDATED = true, PLAYER_TALENT_UPDATE = true, ACTIVE_TALENT_GROUP_CHANGED = true,
    ACTIVE_PLAYER_SPECIALIZATION_CHANGED = true, PLAYER_LEVEL_UP = true, TRAIT_TREE_CURRENCY_INFO_UPDATED = true,
  },
  collect = function()
    local out = {}
    local specIndex = get("C_SpecializationInfo.GetSpecialization")
    out.specIndex = specIndex
    if specIndex then
      local specId, specName, _, _, role = get("C_SpecializationInfo.GetSpecializationInfo", specIndex)
      out.specId, out.specName, out.role = specId, specName, role
    end
    out.numSpecs = get("GetNumSpecializations")
    out.activeSpecGroup = get("C_SpecializationInfo.GetActiveSpecGroup")
    out.hasEarnedPoint = get("C_SpecializationInfo.HasPlayerEarnedATalentPoint")

    local configId = get("C_ClassTalents.GetActiveConfigID")
    out.configId = configId
    if not configId then return out end
    local config = get("C_Traits.GetConfigInfo", configId)
    local treeId = type(config) == "table" and type(config.treeIDs) == "table" and config.treeIDs[1] or nil
    out.configName = type(config) == "table" and config.name or nil
    out.treeId = treeId
    if not treeId then return out end

    local currencies = get("C_Traits.GetTreeCurrencyInfo", configId, treeId, false)
    out.currencies = {}
    if type(currencies) == "table" then
      for _, c in ipairs(currencies) do
        out.currencies[#out.currencies + 1] = {
          id = c.traitCurrencyID, available = c.quantity, max = c.maxQuantity, spent = c.spent,
        }
      end
      if out.currencies[1] then
        out.unspent = out.currencies[1].available
        out.spent = out.currencies[1].spent
      end
    end

    local nodes = get("C_Traits.GetTreeNodes", treeId)
    out.nodeCount = type(nodes) == "table" and #nodes or 0
    out.nodes = {}
    if type(nodes) == "table" then
      for _, nodeId in ipairs(nodes) do
        local node = get("C_Traits.GetNodeInfo", configId, nodeId)
        if type(node) == "table" then
          local rank = node.activeRank or node.currentRank or node.ranksPurchased or 0
          if rank > 0 then
            local entryId = node.activeEntry and node.activeEntry.entryID
              or (type(node.entryIDs) == "table" and node.entryIDs[1]) or nil
            local name, spellId
            if entryId then name, spellId = spellNameForEntry(configId, entryId) end
            out.nodes[#out.nodes + 1] = {
              nodeId = nodeId, rank = rank, maxRank = node.maxRanks,
              entryId = entryId, spellId = spellId, name = name,
              posX = node.posX, posY = node.posY,
            }
          end
        end
      end
    end
    return out
  end,
})

-- ---------------------------------------------------------------- sorts

local SPELLBANK_PLAYER = (_G.Enum and _G.Enum.SpellBookSpellBank and _G.Enum.SpellBookSpellBank.Player) or 0
local SPELLBANK_PET = (_G.Enum and _G.Enum.SpellBookSpellBank and _G.Enum.SpellBookSpellBank.Pet) or 1

local function readSpellItem(index, bank)
  local info = get("C_SpellBook.GetSpellBookItemInfo", index, bank)
  if type(info) ~= "table" then return nil end
  return {
    spellId = info.spellID or info.actionID,
    name = info.name,
    subName = (info.subName and info.subName ~= "") and info.subName or nil,
    passive = info.isPassive and true or nil,
    offSpec = info.isOffSpec and true or nil,
    itemType = info.itemType,
  }
end
ns.readSpellItem = readSpellItem

ns.RegisterDomain("spells", {
  label = "Sorts",
  events = {
    LEARNED_SPELL_IN_SKILL_LINE = true, LEARNED_SPELL_IN_TAB = true, PLAYER_LEVEL_UP = true,
  },
  collect = function()
    local out = { lines = {} }
    local n = get("C_SpellBook.GetNumSpellBookSkillLines") or 0
    for i = 1, n do
      local line = get("C_SpellBook.GetSpellBookSkillLineInfo", i)
      if type(line) == "table" and not line.shouldHide then
        local entry = { name = line.name, spells = {} }
        local offset = line.itemIndexOffset or 0
        for idx = offset + 1, offset + (line.numSpellBookItems or 0) do
          local s = readSpellItem(idx, SPELLBANK_PLAYER)
          if s then entry.spells[#entry.spells + 1] = s end
        end
        out.lines[#out.lines + 1] = entry
      end
    end
    return out
  end,
})
