-- ForeverScribe : prix de l'hôtel des ventes (schéma 1.5)
-- Lecture PASSIVE de ce que l'interface de l'HV a déjà reçu après une recherche faite par
-- le joueur. Aucune recherche n'est lancée par l'addon : jamais de QueryAuctionItems,
-- C_AuctionHouse.SendBrowseQuery, SendSearchQuery ni équivalent.
-- Deux API gérées, détectées à l'exécution :
--   * moderne : AUCTION_HOUSE_BROWSE_RESULTS_UPDATED, ITEM_SEARCH_RESULTS_UPDATED,
--     COMMODITY_SEARCH_RESULTS_UPDATED + C_AuctionHouse.Get*Results* ;
--   * classique : AUCTION_ITEM_LIST_UPDATE + GetNumAuctionItems / GetAuctionItemInfo("list").
-- Stockage au niveau du compte (ForeverScribeDB.auction), une entrée par royaume et
-- faction, dernière observation par objet seulement. Rien en combat, lecture par lots.
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS

local CHUNK = 25                  -- annonces lues par image (pas de gel sur une page de 50+)
local MAX_AGE = 30 * 86400        -- observations gardées 30 jours
local MAX_ITEMS = 5000            -- objets gardés par royaume et faction
local BROWSE_KEEP = 900           -- s : une recherche détaillée récente prime sur la navigation
local MIN_FOR_MEDIAN = 3          -- annonces nécessaires pour une médiane

-- ---------------------------------------------------------------- stockage

local function store()
  local db = _G.ForeverScribeDB
  if type(db) ~= "table" then return nil end
  if type(db.auction) ~= "table" then db.auction = {} end
  return db.auction
end

-- Clé "<royaume>|<faction>" : royaume = GetRealmName() brut, comme identity.realm et
-- l'index du compte ; faction = jeton non traduit de UnitFactionGroup ("Alliance"/"Horde").
-- Sur Forever, GetRealmName() renvoie parfois "" (constaté en jeu le 26/11). On se
-- rabat alors sur le nom normalisé, puis sur le royaume d'un autre perso du compte
-- dont le GUID porte le même numéro de serveur, puis sur "?" : un relevé n'est jamais
-- jeté faute de nom de royaume (le serveur MCP sait rattacher "?" par faction).
local function nonEmpty(s) return type(s) == "string" and s ~= "" and s or nil end

local function realmFromSiblings()
  local guid = nonEmpty(ns.get("UnitGUID", "player"))
  local server = guid and guid:match("^Player%-(%d+)%-")
  local db = _G.ForeverScribeDB
  if not server or type(db) ~= "table" or type(db.characters) ~= "table" then return nil end
  for otherGuid, c in pairs(db.characters) do
    if type(otherGuid) == "string" and otherGuid:match("^Player%-(%d+)%-") == server
       and type(c) == "table" and nonEmpty(c.realm) then
      return c.realm
    end
  end
  return nil
end

local function realmKey()
  local faction = nonEmpty(ns.get("UnitFactionGroup", "player"))
  if not faction then return nil end
  local realm = nonEmpty(ns.get("GetRealmName")) or nonEmpty(ns.get("GetNormalizedRealmName"))
  if not realm then
    local ok, r = pcall(realmFromSiblings)
    realm = (ok and r) or "?"
  end
  return realm .. "|" .. faction
end
ns.AuctionRealmKey = realmKey

local function bucket(create)
  local s = store()
  local key = realmKey()
  if not s or not key then return nil end
  local b = s[key]
  if type(b) ~= "table" then
    if not create then return nil end
    b = { items = {} }
    s[key] = b
  end
  b.items = b.items or {}
  return b
end
ns.AuctionBucket = bucket

-- Erreur gardée en mémoire seulement (/scribe statut) : la table auction ne contient
-- que des clés "<royaume>|<faction>".
local function noteError(where, err)
  ns.auctionLastError = { event = where, message = tostring(err):sub(1, 160), at = ns.now() }
end

-- ---------------------------------------------------------------- calcul

local function median(sorted)
  local n = #sorted
  if n == 0 then return nil end
  if n % 2 == 1 then return sorted[(n + 1) / 2] end
  return math.floor((sorted[n / 2] + sorted[n / 2 + 1]) / 2 + 0.5)
end

-- rows : itemId -> { prices = { prix unitaire par annonce }, qty = total }
local function writeRows(rows, browse)
  local b = bucket(true)
  if not b then return 0 end
  local t = ns.now()
  local written = 0
  for itemId, r in pairs(rows) do
    if #r.prices > 0 then
      local prev = b.items[itemId]
      -- la navigation (prix minimum seul) n'écrase pas une recherche détaillée récente
      if not (browse and prev and prev.n and prev.n > 0 and prev.t and t - prev.t < BROWSE_KEEP) then
        table.sort(r.prices)
        local n = browse and 0 or #r.prices
        b.items[itemId] = {
          min = r.prices[1],
          med = (n >= MIN_FOR_MEDIAN) and median(r.prices) or nil,
          n = n,
          qty = r.qty,
          t = t,
        }
        written = written + 1
      end
    end
  end
  if written > 0 then b.lastScan = t end
  return written
end

local function addRow(rows, itemId, unitPrice, qty)
  if type(itemId) ~= "number" or itemId <= 0 then return end
  if type(unitPrice) ~= "number" or unitPrice <= 0 then return end
  local r = rows[itemId]
  if not r then r = { prices = {}, qty = 0 }; rows[itemId] = r end
  r.prices[#r.prices + 1] = unitPrice
  r.qty = r.qty + ((type(qty) == "number" and qty > 0) and qty or 0)
end

-- ---------------------------------------------------------------- lecteurs (lecture seule)

-- Chaque lecteur renvoie total, lire(i) -> itemId, prixUnitaire, quantité
local READERS = {}

-- API classique : page de résultats "list" affichée par l'onglet Parcourir
READERS.classic = function()
  local n = ns.get("GetNumAuctionItems", "list")
  if type(n) ~= "number" or n <= 0 then return 0 end
  return n, function(i)
    local ok, name, _, count, _, _, _, _, _, _, buyout, _, _, _, _, _, _, itemId =
      pcall(_G.GetAuctionItemInfo, "list", i)
    if not ok then return nil end
    if type(itemId) ~= "number" then itemId = ns.itemIdFromLink(ns.get("GetAuctionItemLink", "list", i)) end
    count = (type(count) == "number" and count > 0) and count or 1
    if type(buyout) ~= "number" or buyout <= 0 then return nil end   -- pas d'achat immédiat
    return itemId, math.floor(buyout / count + 0.5), count
  end
end

-- API moderne : toutes les annonces d'un objet non empilable (clic sur une ligne)
READERS.item = function(itemKey)
  if type(itemKey) ~= "table" then return 0 end
  local n = ns.get("C_AuctionHouse.GetNumItemSearchResults", itemKey)
  if type(n) ~= "number" or n <= 0 then return 0 end
  return n, function(i)
    local r = ns.get("C_AuctionHouse.GetItemSearchResultInfo", itemKey, i)
    if type(r) ~= "table" then return nil end
    local qty = (type(r.quantity) == "number" and r.quantity > 0) and r.quantity or 1
    local buyout = r.buyoutAmount
    if type(buyout) ~= "number" or buyout <= 0 then return nil end
    local id = (type(r.itemKey) == "table" and r.itemKey.itemID) or itemKey.itemID
    return id, math.floor(buyout / qty + 0.5), qty
  end
end

-- API moderne : paliers de prix d'une marchandise (cuir, tissu… : prix déjà unitaire)
READERS.commodity = function(itemId)
  if type(itemId) ~= "number" then return 0 end
  local n = ns.get("C_AuctionHouse.GetNumCommoditySearchResults", itemId)
  if type(n) ~= "number" or n <= 0 then return 0 end
  return n, function(i)
    local r = ns.get("C_AuctionHouse.GetCommoditySearchResultInfo", itemId, i)
    if type(r) ~= "table" then return nil end
    return r.itemID or itemId, r.unitPrice, r.quantity
  end
end

-- API moderne : liste de navigation (un prix minimum et une quantité totale par objet)
READERS.browse = function()
  local list = ns.get("C_AuctionHouse.GetBrowseResults")
  if type(list) ~= "table" or #list == 0 then return 0 end
  return #list, function(i)
    local r = list[i]
    if type(r) ~= "table" then return nil end
    local id = type(r.itemKey) == "table" and r.itemKey.itemID or nil
    return id, r.minPrice, r.totalQuantity
  end
end

-- ---------------------------------------------------------------- lecture par lots

local job                       -- lecture en cours
local generation = 0
local pending                   -- { kind, arg } en attente de la fin du combat
local session = {}              -- classique : itemId -> { pages = {}, prices = {}, qty } (visite en cours)
ns.auctionOpen = nil            -- nil = inconnu (événement absent), true / false sinon

local function classicPage()
  local f = _G.AuctionFrameBrowse
  if type(f) ~= "table" then return nil end
  local ok, page = pcall(function() return f.page end)
  return (ok and type(page) == "number") and page or nil
end

-- Classique : une recherche peut tenir sur plusieurs pages de 50. On cumule les pages
-- d'une même visite ; relire une page déjà vue (nouvelle recherche, rafraîchissement)
-- repart de zéro pour cet objet. Page inconnue : la page remplace l'observation.
local function mergeClassic(rows, page)
  if page == nil then return rows end
  local merged = {}
  for itemId, r in pairs(rows) do
    local s = session[itemId]
    if not s or s.pages[page] then
      s = { pages = {}, prices = {}, qty = 0 }
      session[itemId] = s
    end
    s.pages[page] = true
    for _, p in ipairs(r.prices) do s.prices[#s.prices + 1] = p end
    s.qty = s.qty + r.qty
    local copy = {}
    for i, p in ipairs(s.prices) do copy[i] = p end
    merged[itemId] = { prices = copy, qty = s.qty }
  end
  return merged
end

local function finish(j)
  local rows = j.rows
  if j.kind == "classic" then rows = mergeClassic(rows, j.page) end
  local written = writeRows(rows, j.kind == "browse")
  ns.auctionLastScan = { kind = j.kind, rows = j.total, ticks = j.ticks, written = written }
end

local function step(gen)
  local j = job
  if not j or j.gen ~= gen or gen ~= generation then return end
  if ns.inCombat and ns.inCombat() then
    -- combat pendant la lecture : on relira tout à la fin du combat
    pending = { kind = j.kind, arg = j.arg }
    job = nil
    return
  end
  j.ticks = j.ticks + 1
  local last = math.min(j.total, j.i + CHUNK - 1)
  for i = j.i, last do
    local ok, itemId, unit, qty = pcall(j.read, i)
    if ok then addRow(j.rows, itemId, unit, qty) end
  end
  j.i = last + 1
  if j.i > j.total then
    job = nil
    local ok, err = pcall(finish, j)
    if not ok then noteError(j.kind, err) end
    return
  end
  local after = _G.C_Timer and _G.C_Timer.After
  if after then after(0, function() step(j.gen) end) else step(j.gen) end
end

local function scan(kind, arg)
  if ns.inCombat and ns.inCombat() then
    pending = { kind = kind, arg = arg }
    return
  end
  local reader = READERS[kind]
  local okR, total, read = pcall(reader, arg)
  if not okR then noteError(kind, total) return end
  if type(total) ~= "number" or total <= 0 or not read then return end
  generation = generation + 1     -- une nouvelle page remplace la lecture en cours
  job = { gen = generation, kind = kind, arg = arg, total = total, read = read, i = 1,
          rows = {}, ticks = 0, page = (kind == "classic") and classicPage() or nil }
  local gen = generation
  local after = _G.C_Timer and _G.C_Timer.After
  if after then after(0, function() step(gen) end) else step(gen) end
end
ns.AuctionScan = scan

-- ---------------------------------------------------------------- taille bornée

function ns.PruneAuction()
  local s = store()
  if not s then return end
  local limit = ns.now() - MAX_AGE
  for key, b in pairs(s) do
    if type(b) ~= "table" or type(b.items) ~= "table" then
      s[key] = nil
    else
      local keys = {}
      for id, e in pairs(b.items) do
        if type(e) ~= "table" or type(e.t) ~= "number" or e.t < limit then
          b.items[id] = nil
        else
          keys[#keys + 1] = id
        end
      end
      if #keys > MAX_ITEMS then
        table.sort(keys, function(a, c) return b.items[a].t < b.items[c].t end)
        for i = 1, #keys - MAX_ITEMS do b.items[keys[i]] = nil end
      end
      if next(b.items) == nil then s[key] = nil end
    end
  end
end

-- Nombre de prix relevés et date du dernier passage (royaume et faction du perso)
function ns.AuctionSummary()
  local b = bucket(false)
  if not b then return 0, nil end
  local n = 0
  for _ in pairs(b.items) do n = n + 1 end
  return n, b.lastScan
end

-- ---------------------------------------------------------------- événements

local HANDLERS = {
  AUCTION_ITEM_LIST_UPDATE = function() scan("classic") end,
  AUCTION_HOUSE_BROWSE_RESULTS_UPDATED = function() scan("browse") end,
  AUCTION_HOUSE_BROWSE_RESULTS_ADDED = function() scan("browse") end,
  ITEM_SEARCH_RESULTS_UPDATED = function(itemKey) scan("item", itemKey) end,
  COMMODITY_SEARCH_RESULTS_UPDATED = function(itemId) scan("commodity", itemId) end,
}

local frame = CreateFrame("Frame")
ns.auctionFrame = frame
for event in pairs(HANDLERS) do pcall(frame.RegisterEvent, frame, event) end
for _, event in ipairs({ "AUCTION_HOUSE_SHOW", "AUCTION_HOUSE_CLOSED", "PLAYER_LOGIN",
                         "PLAYER_REGEN_ENABLED", "PLAYER_LOGOUT" }) do
  pcall(frame.RegisterEvent, frame, event)
end

frame:SetScript("OnEvent", function(_, event, ...)
  if event == "PLAYER_LOGIN" or event == "PLAYER_LOGOUT" then
    pcall(ns.PruneAuction)
    return
  elseif event == "AUCTION_HOUSE_SHOW" then
    ns.auctionOpen = true
    session = {}
    return
  elseif event == "AUCTION_HOUSE_CLOSED" then
    ns.auctionOpen = false
    session = {}
    pending = nil
    generation = generation + 1   -- abandonne une lecture en cours
    job = nil
    return
  elseif event == "PLAYER_REGEN_ENABLED" then
    if pending and ns.auctionOpen ~= false then
      local p = pending
      pending = nil
      scan(p.kind, p.arg)
    end
    return
  end
  local fn = HANDLERS[event]
  if not fn then return end
  local ok, err = pcall(fn, ...)
  if not ok then noteError(event, err) end
end)
