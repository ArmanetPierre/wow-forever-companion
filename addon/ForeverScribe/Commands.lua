-- ForeverScribe : commandes /scribe et message de connexion
-- Textes dans Locales.lua (ns.L). Sous-commandes acceptées en anglais et en français.
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS

local function L() return ns.L end

local function summaryLine()
  local c = ns.charDB()
  if not c then return L().NO_DATA end
  local id, p, pos = c.identity or {}, c.progression or {}, c.position or {}
  local q = c.quests and c.quests.count
  return string.format("%s · %s %s %s · %s%s",
    id.name or "?", id.race or "?", id.class or "?", tostring(p.level or id.level or "?"),
    pos.zone or "?", q and (" · " .. string.format(L().QUESTS_N, q)) or "")
end

ns.onLoginCaptured = function(ok, err)
  local key = ns.SyncKeyText and ns.SyncKeyText()
  ns.print(string.format(L().READY,
    ok, err > 0 and string.format(L().N_ERRORS, err) or "",
    key and string.format(L().SYNC_KEY_OR_CMD, key) or L().SYNC_NO_KEY))
end

local function status()
  local c = ns.charDB()
  if not c then ns.print(L().NOT_INITIALIZED) return end
  local m = c.meta
  local now = ns.now()
  ns.print(L().STATUS_HEADER)
  for _, name in ipairs(ns.order) do
    local def = ns.domains[name]
    local at = m.domainsUpdatedAt[name]
    local err = m.errors[name]
    local state
    if err then
      state = "|cffff5555" .. L().STATUS_ERROR .. "|r " .. tostring(err.message):sub(1, 80)
    elseif at then
      state = "|cff55ff55" .. string.format(L().STATUS_OK_AGO, ns.ageText(now - at)) .. "|r"
    else
      state = "|cffaaaaaa" .. L().STATUS_NEVER .. "|r"
      if name == "recipes" then state = state .. L().STATUS_OPEN_PROFESSION end
      if name == "bank" then state = state .. L().STATUS_OPEN_BANK end
    end
    local failed = m.callErrors[name]
    if failed and #failed > 0 then
      state = state .. " |cffffaa00(" .. string.format(L().STATUS_FAILED_CALLS, #failed) .. ")|r"
    end
    local missing = m.missing[name]
    if missing and #missing > 0 then
      state = state .. " |cffffaa00(" .. string.format(L().STATUS_MISSING_FUNCS, #missing) .. ")|r"
    end
    local label = L()["domain." .. name]
    if label == "domain." .. name then label = def.label or name end
    ns.print(string.format("  %-16s %s", label, state))
  end
  if m.lastSyncRequestAt then
    ns.print(string.format(L().LAST_SYNC, ns.ageText(now - m.lastSyncRequestAt), tostring(m.lastSyncReason)))
  end
  ns.print(L().STATUS_FOOTER)
end

local function help()
  ns.print(L().HELP_HEADER)
  ns.print(L().HELP_SCRIBE)
  ns.print(L().HELP_STATUS)
  ns.print(L().HELP_HELP)
  ns.print(L().HELP_SYNC_HEADER)
  local key = ns.SyncKeyText and ns.SyncKeyText()
  ns.print(L().HELP_SYNC)
  ns.print(string.format(L().HELP_KEY, key or L().HELP_NONE))
  ns.print(L().HELP_BUTTON)
  ns.print(L().HELP_AUTO)
end

-- sous-commandes : anglais et français, quelle que soit la langue du client
local KEY_WORDS = { key = true, touche = true }

SLASH_FOREVERSCRIBE1 = "/scribe"
SlashCmdList.FOREVERSCRIBE = function(msg)
  msg = (msg or ""):lower():gsub("^%s+", ""):gsub("%s+$", "")
  local cmd, arg = msg:match("^(%S+)%s+(%S+)")
  cmd = cmd or msg
  if cmd == "status" or cmd == "statut" then
    status()
  elseif cmd == "help" or cmd == "aide" or cmd == "?" then
    help()
  elseif cmd == "sync" then
    ns.Sync("commande")
  elseif cmd == "bouton" or cmd == "button" then
    ns.ToggleButton()
  elseif KEY_WORDS[cmd] then
    ns.BindKey(arg)
  else
    if ns.inCombat() then
      ns.print(L().IN_COMBAT_CAPTURE)
      for _, name in ipairs(ns.order) do ns.pending[name] = true end
      ns.waitingCombat = true
      return
    end
    local ok, err = ns.CaptureAll(true)
    ns.print(summaryLine())
    ns.print(string.format(L().CAPTURED_SUMMARY,
      ok, err > 0 and string.format(L().CAPTURED_ERRORS, err) or ""))
  end
end
