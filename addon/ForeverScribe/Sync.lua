-- ForeverScribe : synchronisation « en un geste » pour Claude.
-- Une touche, /sync ou le bouton de la minicarte : capture complète puis rechargement
-- de l'interface, ce qui fait écrire les fichiers sur le disque par le jeu.
-- ReloadUI / C_UI.Reload exigent un geste du joueur (touche, clic, commande tapée) :
-- rien ici ne recharge tout seul.
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS

local DEFAULT_KEY = "CTRL-SHIFT-S"   -- libre dans les raccourcis par défaut du client
local BUTTON_RADIUS = 80              -- distance du bouton au centre de la minicarte
local REQUEST_WINDOW = 15             -- s : une demande récente explique la prochaine écriture
local atan2 = math.atan2 or function(y, x) return math.atan(y, x) end

-- Libellés du menu Options → Raccourcis → AddOns (traduits, voir Locales.lua)
_G.BINDING_HEADER_FOREVERSCRIBE = "ForeverScribe"
_G.BINDING_NAME_FOREVERSCRIBE_SYNC = ns.L.BINDING_SYNC

local function settings()
  local db = _G.ForeverScribeDB
  if type(db) ~= "table" then return {} end
  db.settings = db.settings or {}
  local s = db.settings
  if s.showButton == nil then s.showButton = true end
  s.buttonAngle = s.buttonAngle or 215
  return s
end
ns.settings = settings

-- âge de la dernière capture, pour l'infobulle et les messages
local function lastCaptureAge()
  local c = ns.charDB()
  local at = c and c.meta and c.meta.capturedAt
  if not at then return nil end
  return ns.now() - at
end

-- ---------------------------------------------------------------- action

-- reason : "touche" | "commande" | "bouton" (jetons de données lus par le MCP : jamais traduits)
function ns.Sync(reason)
  if ns.inCombat() then
    ns.syncAfterCombat = reason or "commande"
    ns.print(ns.L.SYNC_IN_COMBAT)
    return false
  end
  local c = ns.charDB()
  if not c or not c.meta then
    ns.print(ns.L.SYNC_NOT_READY)
    return false
  end
  local t = ns.now()
  c.meta.lastSyncRequestAt = t
  c.meta.lastSyncReason = reason or "commande"
  ns.CaptureAll(true)
  ns.print(ns.L.SYNC_RUNNING)
  local reload = ns.api("C_UI.Reload") or ns.api("ReloadUI")
  if not reload then
    ns.print(ns.L.SYNC_NO_RELOAD)
    return false
  end
  local ok, err = pcall(reload)
  if not ok then
    ns.print(string.format(ns.L.SYNC_RELOAD_REFUSED, tostring(err):sub(1, 60)))
    return false
  end
  return true
end

-- appelé par Bindings.xml
_G.ForeverScribe_Sync = function(reason) return ns.Sync(reason or "touche") end

-- ---------------------------------------------------------------- raccourci

-- Attribue la touche si elle est libre (hors combat). Ne remplace jamais une touche prise.
function ns.BindKey(key)
  key = (key and key ~= "") and key:upper() or DEFAULT_KEY
  if ns.inCombat() then
    ns.print(ns.L.KEY_IN_COMBAT)
    return false
  end
  local current = ns.get("GetBindingAction", key)
  if current == "FOREVERSCRIBE_SYNC" then
    ns.print(string.format(ns.L.KEY_ALREADY_SYNC, key))
    return true
  end
  if current and current ~= "" then
    ns.print(string.format(ns.L.KEY_TAKEN, key, current))
    return false
  end
  local ok = ns.get("SetBinding", key, "FOREVERSCRIBE_SYNC")
  if not ok then
    ns.print(string.format(ns.L.KEY_REFUSED, key))
    return false
  end
  local set = ns.get("GetCurrentBindingSet") or 2
  ns.call("SaveBindings", set)
  ns.print(string.format(ns.L.KEY_SET, key))
  return true
end

function ns.SyncKeyText()
  local key = ns.get("GetBindingKey", "FOREVERSCRIBE_SYNC")
  return key
end

-- ---------------------------------------------------------------- bouton minicarte

local button

local function placeButton()
  if not button then return end
  local a = math.rad(settings().buttonAngle)
  button:ClearAllPoints()
  button:SetPoint("CENTER", _G.Minimap, "CENTER", math.cos(a) * BUTTON_RADIUS, math.sin(a) * BUTTON_RADIUS)
end

local function onDragUpdate()
  local mm = _G.Minimap
  local getCursor = ns.api("GetCursorPosition")
  if not mm or not getCursor then return end
  local mx, my = mm:GetCenter()
  local scale = mm:GetEffectiveScale()
  local cx, cy = getCursor()
  if not (mx and my and cx and cy and scale and scale > 0) then return end
  cx, cy = cx / scale, cy / scale
  settings().buttonAngle = math.deg(atan2(cy - my, cx - mx))
  placeButton()
end

local function showTooltip(self)
  local tip = _G.GameTooltip
  if not tip then return end
  tip:SetOwner(self, "ANCHOR_LEFT")
  local L = ns.L
  tip:SetText(L.TIP_TITLE)
  local age = lastCaptureAge()
  tip:AddLine(string.format(L.TIP_LAST_DATA, age and string.format(L.TIP_AGO, ns.ageText(age)) or L.TIP_NONE), 1, 1, 1)
  local key = ns.SyncKeyText()
  tip:AddLine(key and string.format(L.TIP_KEY, key) or L.TIP_NO_KEY, 0.7, 0.7, 0.7)
  tip:AddLine(L.TIP_HINT, 0.7, 0.7, 0.7)
  tip:Show()
end

local function createButton()
  if button or not _G.Minimap or not _G.CreateFrame then return button end
  local ok, b = pcall(_G.CreateFrame, "Button", "ForeverScribeMinimapButton", _G.Minimap)
  if not ok or not b then return nil end
  button = b
  b:SetSize(28, 28)
  b:SetFrameStrata("MEDIUM")
  b:SetFrameLevel(8)
  b:RegisterForClicks("LeftButtonUp")
  b:RegisterForDrag("LeftButton")
  b:SetMovable(true)

  local icon = b:CreateTexture(nil, "ARTWORK")
  icon:SetTexture("Interface\\Icons\\INV_Scroll_03")
  icon:SetSize(18, 18)
  icon:SetPoint("CENTER", b, "CENTER", 0, 0)
  local border = b:CreateTexture(nil, "OVERLAY")
  border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
  border:SetSize(52, 52)
  border:SetPoint("TOPLEFT", b, "TOPLEFT", 0, 0)
  b:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight")

  b:SetScript("OnClick", function() ns.Sync("bouton") end)
  b:SetScript("OnEnter", showTooltip)
  b:SetScript("OnLeave", function() if _G.GameTooltip then _G.GameTooltip:Hide() end end)
  b:SetScript("OnDragStart", function(self) self:SetScript("OnUpdate", onDragUpdate) end)
  b:SetScript("OnDragStop", function(self) self:SetScript("OnUpdate", nil) end)
  placeButton()
  return b
end

function ns.RefreshButton()
  if settings().showButton then
    local b = createButton()
    if b then b:Show() end
  elseif button then
    button:Hide()
  end
end

function ns.ToggleButton()
  local s = settings()
  s.showButton = not s.showButton
  ns.RefreshButton()
  ns.print(s.showButton and ns.L.BUTTON_SHOWN or ns.L.BUTTON_HIDDEN)
end

-- ---------------------------------------------------------------- événements

local frame = CreateFrame("Frame")
frame:RegisterEvent("PLAYER_LOGIN")
frame:RegisterEvent("PLAYER_REGEN_ENABLED")
frame:RegisterEvent("PLAYER_LOGOUT")
frame:SetScript("OnEvent", function(_, event)
  if event == "PLAYER_LOGIN" then
    pcall(ns.RefreshButton)
  elseif event == "PLAYER_REGEN_ENABLED" then
    if ns.syncAfterCombat then
      ns.syncAfterCombat = nil
      local key = ns.SyncKeyText()
      ns.print(string.format(ns.L.COMBAT_OVER, key and string.format(ns.L.COMBAT_OVER_KEY, key) or ""))
    end
  elseif event == "PLAYER_LOGOUT" then
    -- Le jeu écrit les fichiers juste après. Sans demande récente (touche, bouton,
    -- /sync), l'écriture vient d'une déconnexion, d'une sortie ou d'un /reload tapé.
    local c = ns.charDB()
    if not c or not c.meta then return end
    local t = ns.now()
    c.meta.writtenAt = t
    if not (c.meta.lastSyncRequestAt and t - c.meta.lastSyncRequestAt <= REQUEST_WINDOW) then
      c.meta.lastSyncRequestAt = t
      c.meta.lastSyncReason = "deconnexion"
    end
  end
end)

-- /sync
_G.SLASH_FOREVERSCRIBESYNC1 = "/sync"
_G.SlashCmdList.FOREVERSCRIBESYNC = function() ns.Sync("commande") end
