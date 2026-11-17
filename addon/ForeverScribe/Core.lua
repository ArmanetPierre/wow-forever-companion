-- ForeverScribe : cœur (registre des domaines, base de données, planification, événements)
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS

local THROTTLE = 2          -- secondes entre un événement et la capture
local LOGIN_DELAY = 4       -- capture complète après la connexion
local SUPPRESS = 1          -- ignore les événements provoqués par notre propre lecture

ns.domains = {}             -- nom -> définition
ns.order = {}               -- ordre d'affichage
ns.pending = {}             -- nom -> true
ns.ctx = {}                 -- nom -> données de contexte (ex. sacs modifiés)
ns.suppressUntil = {}       -- nom -> GetTime()
ns.handlers = {}            -- événement -> { {domain, filter} }
ns.unitHandlers = {}        -- événement -> { unit = { {domain, filter} } }

--[[ Définition d'un domaine :
  key      : clé dans ForeverScribeCharDB (par défaut = nom)
  label    : libellé pour /scribe status
  events   : { EVENT = true | function(...) -> bool (marquer ?) }
  unitEvents : { EVENT = "player" | "pet" }
  collect  : function(ctx, previous) -> table | nil (nil = garder la valeur précédente)
  logout   : true = recapturé à la déconnexion / au /reload (domaine léger)
  login    : false = pas de capture automatique à la connexion
]]
function ns.RegisterDomain(name, def)
  def.name = name
  def.key = def.key or name
  ns.domains[name] = def
  ns.order[#ns.order + 1] = name
end

-- ---------------------------------------------------------------- données

local function charDB()
  return _G.ForeverScribeCharDB
end
ns.charDB = charDB

local function initDB()
  if type(_G.ForeverScribeDB) ~= "table" then _G.ForeverScribeDB = {} end
  local db = _G.ForeverScribeDB
  db.schemaVersion = ns.SCHEMA_VERSION
  db.schemaMinor = ns.SCHEMA_MINOR
  db.addonVersion = ns.VERSION
  db.characters = db.characters or {}

  if type(_G.ForeverScribeCharDB) ~= "table"
     or (_G.ForeverScribeCharDB.meta and _G.ForeverScribeCharDB.meta.schemaVersion ~= ns.SCHEMA_VERSION) then
    _G.ForeverScribeCharDB = {}
  end
  local c = _G.ForeverScribeCharDB
  c.meta = c.meta or {}
  local m = c.meta
  m.schemaVersion = ns.SCHEMA_VERSION
  m.schemaMinor = ns.SCHEMA_MINOR
  m.addonVersion = ns.VERSION
  m.domainsUpdatedAt = m.domainsUpdatedAt or {}
  m.errors = m.errors or {}
  m.missing = m.missing or {}
  m.callErrors = m.callErrors or {}
end

local function refreshMeta()
  local m = charDB().meta
  local version, build, bdate, interface = ns.get("GetBuildInfo")
  m.build = { version = version, build = build, date = bdate, interface = interface }
  m.locale = ns.get("GetLocale")
  m.guid = ns.get("UnitGUID", "player")
  m.wowProject = _G.WOW_PROJECT_ID
end

function ns.UpdateIndex()
  local c = charDB()
  if not c or not c.meta or not c.meta.guid then return end
  local id = c.identity or {}
  local p = c.progression or {}
  _G.ForeverScribeDB.characters[c.meta.guid] = {
    name = id.name,
    suffix = id.suffix,
    realm = id.realm,
    realmId = id.realmId,
    region = id.region,
    ruleset = id.ruleset,
    race = id.race,
    class = id.class,
    classFile = id.classFile,
    faction = id.faction,
    level = p.level or id.level,
    zone = c.position and c.position.zone or nil,
    lastCapture = c.meta.capturedAt,
    lastCaptureISO = c.meta.capturedAtISO,
  }
end

-- ---------------------------------------------------------------- exécution

function ns.RunDomain(name)
  local def = ns.domains[name]
  local c = charDB()
  if not def or not c then return false end
  local m = c.meta
  local ctx = ns.ctx[name]
  ns.ctx[name] = nil
  local gt = ns.api("GetTime")
  -- bloque les événements que notre propre lecture déclenche (ex. dépliage des réputations)
  if gt then ns.suppressUntil[name] = gt() + 600 end
  ns.currentMissing, ns.currentFailed = {}, {}
  local ok, res = pcall(def.collect, ctx, c[def.key])
  local missing, failed = {}, {}
  for path in pairs(ns.currentMissing) do missing[#missing + 1] = path end
  for path, msg in pairs(ns.currentFailed) do failed[#failed + 1] = path .. " : " .. msg end
  table.sort(missing)
  table.sort(failed)
  ns.currentMissing, ns.currentFailed = nil, nil
  m.missing[name] = (#missing > 0) and missing or nil
  m.callErrors[name] = (#failed > 0) and failed or nil

  local t = ns.now()
  if ok then
    if res ~= nil then
      c[def.key] = res
      m.domainsUpdatedAt[name] = t
    end
    m.errors[name] = nil
  else
    m.errors[name] = { message = tostring(res), at = t }
  end
  m.capturedAt = t
  m.capturedAtISO = ns.iso(t)
  if gt then ns.suppressUntil[name] = gt() + SUPPRESS end
  return ok
end

local function inCombat()
  local f = ns.api("InCombatLockdown")
  if f and f() then return true end
  local u = ns.api("UnitAffectingCombat")
  return (u and u("player")) and true or false
end
ns.inCombat = inCombat

function ns.Flush()
  ns.timerScheduled = false
  if not charDB() then return end
  if inCombat() then
    ns.waitingCombat = true
    return
  end
  local ran = false
  for _, name in ipairs(ns.order) do
    if ns.pending[name] then
      ns.pending[name] = nil
      ns.RunDomain(name)
      ran = true
    end
  end
  if ran then ns.UpdateIndex() end
end

local function schedule(delay)
  if ns.timerScheduled then return end
  ns.timerScheduled = true
  local after = _G.C_Timer and _G.C_Timer.After
  if after then
    after(delay or THROTTLE, ns.Flush)
  else
    ns.Flush()
  end
end

function ns.Mark(name, ctxFn)
  local def = ns.domains[name]
  if not def then return end
  local gt = ns.api("GetTime")
  if gt and ns.suppressUntil[name] and gt() < ns.suppressUntil[name] then return end
  if ctxFn then ns.ctx[name] = ctxFn(ns.ctx[name]) end
  ns.pending[name] = true
  if ns.ready then schedule() end
end

-- Capture immédiate de tous les domaines (hors combat). Renvoie ok, erreurs.
function ns.CaptureAll(includeOnDemand)
  if not charDB() then return 0, 0 end
  local ok, err = 0, 0
  for _, name in ipairs(ns.order) do
    local def = ns.domains[name]
    if includeOnDemand or def.login ~= false then
      ns.pending[name] = nil
      if ns.RunDomain(name) then ok = ok + 1 else err = err + 1 end
    end
  end
  ns.UpdateIndex()
  return ok, err
end

-- ---------------------------------------------------------------- événements

local frame = CreateFrame("Frame")
ns.frame = frame

local function safeRegister(event)
  pcall(frame.RegisterEvent, frame, event)
end

local function safeRegisterUnit(event, unit)
  if frame.RegisterUnitEvent then
    local ok = pcall(frame.RegisterUnitEvent, frame, event, unit)
    if ok then return end
  end
  safeRegister(event)
end

local function wireDomains()
  for _, name in ipairs(ns.order) do
    local def = ns.domains[name]
    for event, filter in pairs(def.events or {}) do
      ns.handlers[event] = ns.handlers[event] or {}
      table.insert(ns.handlers[event], { domain = name, filter = filter })
      safeRegister(event)
    end
    for event, unit in pairs(def.unitEvents or {}) do
      ns.unitHandlers[event] = ns.unitHandlers[event] or {}
      ns.unitHandlers[event][unit] = ns.unitHandlers[event][unit] or {}
      table.insert(ns.unitHandlers[event][unit], { domain = name })
      safeRegisterUnit(event, unit)
    end
  end
end

local function dispatch(event, ...)
  local list = ns.handlers[event]
  if list then
    for _, h in ipairs(list) do
      local f = h.filter
      if f == true or (type(f) == "function" and f(...)) then
        ns.Mark(h.domain)
      end
    end
  end
  local ulist = ns.unitHandlers[event]
  if ulist then
    local unit = ...
    local hs = ulist[unit]
    if hs then
      for _, h in ipairs(hs) do ns.Mark(h.domain) end
    end
  end
end

frame:SetScript("OnEvent", function(self, event, ...)
  if event == "ADDON_LOADED" then
    local name = ...
    if name == ns.ADDON then initDB() end
    return
  elseif event == "PLAYER_LOGIN" then
    initDB()
    refreshMeta()
    wireDomains()
    ns.ready = true
    local after = _G.C_Timer and _G.C_Timer.After
    local function loginCapture()
      if inCombat() then
        for _, name in ipairs(ns.order) do
          if ns.domains[name].login ~= false then ns.pending[name] = true end
        end
        ns.waitingCombat = true
        return
      end
      local ok, err = ns.CaptureAll(false)
      if ns.onLoginCaptured then ns.onLoginCaptured(ok, err) end
    end
    if after then after(LOGIN_DELAY, loginCapture) else loginCapture() end
    return
  elseif event == "PLAYER_REGEN_ENABLED" then
    if ns.waitingCombat or next(ns.pending) then
      ns.waitingCombat = false
      schedule(1)
    end
    -- pas de return : d'autres domaines peuvent écouter cet événement
  elseif event == "PLAYER_LOGOUT" then
    if not charDB() then return end
    refreshMeta()
    -- À la sortie du jeu, le client renvoie parfois des zéros (PV, XP, sacs, argent).
    -- Dans ce cas on garde la capture précédente au lieu de l'écraser.
    local hpMax = _G.UnitHealthMax and _G.UnitHealthMax("player") or 0
    local level = _G.UnitLevel and _G.UnitLevel("player") or 0
    local xpMax = _G.UnitXPMax and _G.UnitXPMax("player") or 0
    if hpMax == 0 or (level > 0 and level < 60 and xpMax == 0) then
      local db = charDB()
      if db and db.meta then db.meta.logoutRecaptureSkipped = true end
      ns.UpdateIndex()
      return
    end
    for _, name in ipairs(ns.order) do
      if ns.domains[name].logout or ns.pending[name] then
        ns.pending[name] = nil
        ns.RunDomain(name)
      end
    end
    ns.UpdateIndex()
    return
  end
  if ns.ready then dispatch(event, ...) end
end)

frame:RegisterEvent("ADDON_LOADED")
frame:RegisterEvent("PLAYER_LOGIN")
frame:RegisterEvent("PLAYER_LOGOUT")
frame:RegisterEvent("PLAYER_REGEN_ENABLED")
