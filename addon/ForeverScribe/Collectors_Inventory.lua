-- ForeverScribe : sacs, munitions, banque, argent
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS
local get = ns.get

local PROJECTILE_CLASS = 6 -- Enum.ItemClass.Projectile

local function bagIds()
  local ids = { 0 }
  local n = _G.NUM_BAG_SLOTS or 4
  for i = 1, n do ids[#ids + 1] = i end
  local reagent = _G.Enum and _G.Enum.BagIndex and _G.Enum.BagIndex.ReagentBag
  if reagent and reagent > n then ids[#ids + 1] = reagent end
  return ids
end
ns.bagIds = bagIds

local function bankIds()
  local seen, ids = {}, {}
  local function add(id)
    if type(id) == "number" and not seen[id] then seen[id] = true; ids[#ids + 1] = id end
  end
  add(_G.BANK_CONTAINER or -1)
  local first = (_G.NUM_BAG_SLOTS or 4) + 1
  local nbank = _G.NUM_BANKBAGSLOTS or 7
  for i = first, first + nbank - 1 do add(i) end
  local bi = _G.Enum and _G.Enum.BagIndex
  if type(bi) == "table" then
    add(bi.Bank)
    for i = 1, 7 do add(bi["BankBag_" .. i]) end
    for i = 1, 6 do add(bi["CharacterBankTab_" .. i]) end
  end
  return ids
end

local isBag = {}
for _, id in ipairs(bagIds()) do isBag[id] = true end

-- Lecture d'un conteneur (sac ou banque)
local function readContainer(bagId)
  local slots = get("C_Container.GetContainerNumSlots", bagId) or 0
  if slots == 0 then return nil end
  local free, family = get("C_Container.GetContainerNumFreeSlots", bagId)
  local bag = {
    id = bagId, name = get("C_Container.GetBagName", bagId),
    slots = slots, free = free, family = family, items = {},
  }
  for slot = 1, slots do
    local info = get("C_Container.GetContainerItemInfo", bagId, slot)
    if type(info) == "table" and info.itemID then
      local _, _, _, _, _, classId, subclassId = get("C_Item.GetItemInfoInstant", info.itemID)
      bag.items[#bag.items + 1] = {
        slot = slot, itemId = info.itemID, name = info.itemName or ns.nameFromLink(info.hyperlink),
        link = info.hyperlink, count = info.stackCount, quality = info.quality,
        bound = info.isBound or nil, noValue = info.hasNoValue or nil,
        classId = classId, subclassId = subclassId,
      }
    end
  end
  return bag
end

local function summarize(containers)
  local total, free = 0, 0
  local ammo = { total = 0, items = {} }
  for _, bag in pairs(containers) do
    total = total + (bag.slots or 0)
    free = free + (bag.free or 0)
    for _, it in ipairs(bag.items or {}) do
      if it.classId == PROJECTILE_CLASS then
        ammo.total = ammo.total + (it.count or 0)
        ammo.items[it.name or tostring(it.itemId)] = (ammo.items[it.name or tostring(it.itemId)] or 0) + (it.count or 0)
      end
    end
  end
  return total, free, ammo
end

ns.RegisterDomain("bags", {
  label = "Sacs",
  logout = true,
  events = {
    BAG_UPDATE = function(bagId)
      if not isBag[bagId] then return false end
      ns.ctx.bags = ns.ctx.bags or {}
      ns.ctx.bags[bagId] = true
      return true
    end,
    PLAYER_EQUIPMENT_CHANGED = true,
  },
  collect = function(dirty, previous)
    local containers = {}
    if dirty and previous and type(previous.containers) == "table" then
      for k, v in pairs(previous.containers) do containers[k] = v end
      for bagId in pairs(dirty) do containers[tostring(bagId)] = readContainer(bagId) end
    else
      for _, bagId in ipairs(bagIds()) do containers[tostring(bagId)] = readContainer(bagId) end
    end
    local total, free, ammo = summarize(containers)
    return { containers = containers, totalSlots = total, freeSlots = free, ammo = ammo }
  end,
})

-- Banque : lisible seulement quand elle est ouverte ; conservée ensuite.
ns.RegisterDomain("bank", {
  label = "Banque",
  login = false,
  events = {
    PLAYERBANKSLOTS_CHANGED = function() return ns.bankOpen end,
    BAG_UPDATE = function(bagId) return ns.bankOpen and not isBag[bagId] end,
  },
  collect = function()
    if not ns.bankOpen then return nil end
    local containers = {}
    for _, bagId in ipairs(bankIds()) do containers[tostring(bagId)] = readContainer(bagId) end
    if not next(containers) then return nil end
    local total, free = summarize(containers)
    return { containers = containers, totalSlots = total, freeSlots = free, capturedAt = ns.now() }
  end,
})

local bankFrame = CreateFrame("Frame")
bankFrame:RegisterEvent("BANKFRAME_OPENED")
bankFrame:RegisterEvent("BANKFRAME_CLOSED")
bankFrame:SetScript("OnEvent", function(_, event)
  if event == "BANKFRAME_OPENED" then
    ns.bankOpen = true
    local after = _G.C_Timer and _G.C_Timer.After
    local function run() if ns.bankOpen and ns.charDB() then ns.RunDomain("bank") end end
    if after then after(0.5, run) else run() end
  else
    ns.bankOpen = false
  end
end)

ns.RegisterDomain("money", {
  label = "Argent",
  logout = true,
  events = { PLAYER_MONEY = true },
  collect = function()
    local copper = get("GetMoney")
    return { copper = copper, text = ns.moneyText(copper) }
  end,
})
