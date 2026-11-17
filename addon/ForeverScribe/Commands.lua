-- ForeverScribe : commandes /scribe et message de connexion
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS

local function summaryLine()
  local c = ns.charDB()
  if not c then return "aucune donnée" end
  local id, p, pos = c.identity or {}, c.progression or {}, c.position or {}
  local q = c.quests and c.quests.count
  return string.format("%s · %s %s %s · %s%s",
    id.name or "?", id.race or "?", id.class or "?", tostring(p.level or id.level or "?"),
    pos.zone or "?", q and (" · " .. q .. " quêtes") or "")
end

ns.onLoginCaptured = function(ok, err)
  local key = ns.SyncKeyText and ns.SyncKeyText()
  ns.print(string.format("prêt (%d domaines capturés%s). Synchro : %s. /scribe help",
    ok, err > 0 and (", " .. err .. " en erreur") or "",
    key and (key .. " ou /sync") or "/sync (ou /scribe touche pour une touche)"))
end

local function status()
  local c = ns.charDB()
  if not c then ns.print("pas encore initialisé.") return end
  local m = c.meta
  local now = ns.now()
  ns.print("état par domaine :")
  for _, name in ipairs(ns.order) do
    local def = ns.domains[name]
    local at = m.domainsUpdatedAt[name]
    local err = m.errors[name]
    local state
    if err then
      state = "|cffff5555ERREUR|r " .. tostring(err.message):sub(1, 80)
    elseif at then
      state = "|cff55ff55OK|r il y a " .. ns.ageText(now - at)
    else
      state = "|cffaaaaaajamais capturé|r"
      if name == "recipes" then state = state .. " (ouvre la fenêtre du métier)" end
      if name == "bank" then state = state .. " (ouvre ta banque)" end
    end
    local failed = m.callErrors[name]
    if failed and #failed > 0 then
      state = state .. " |cffffaa00(" .. #failed .. " appel(s) en erreur)|r"
    end
    local missing = m.missing[name]
    if missing and #missing > 0 then
      state = state .. " |cffffaa00(" .. #missing .. " fonction(s) absente(s))|r"
    end
    ns.print(string.format("  %-16s %s", def.label or name, state))
  end
  local m2 = c.meta
  if m2.lastSyncRequestAt then
    ns.print(string.format("Dernière synchro : il y a %s (%s).", ns.ageText(now - m2.lastSyncRequestAt), tostring(m2.lastSyncReason)))
  end
  ns.print("Synchronise pour Claude : /sync, ta touche ou le bouton de la minicarte.")
end

local function help()
  ns.print("commandes :")
  ns.print("  /scribe         capture complète + résumé")
  ns.print("  /scribe status  état de chaque domaine (OK, erreur, âge)")
  ns.print("  /scribe help    cette aide")
  ns.print("Synchroniser pour Claude (capture + écriture sur le disque) :")
  local key = ns.SyncKeyText and ns.SyncKeyText()
  ns.print("  /sync ou /scribe sync   synchroniser maintenant")
  ns.print("  touche : " .. (key or "aucune") .. "   (/scribe touche [CTRL-SHIFT-S] pour l'attribuer)")
  ns.print("  /scribe bouton  afficher / masquer le bouton de la minicarte")
  ns.print("Les données s'écrivent aussi toutes seules à la déconnexion et en quittant le jeu.")
end

SLASH_FOREVERSCRIBE1 = "/scribe"
SlashCmdList.FOREVERSCRIBE = function(msg)
  msg = (msg or ""):lower():gsub("^%s+", ""):gsub("%s+$", "")
  if msg == "status" or msg == "statut" then
    status()
  elseif msg == "help" or msg == "aide" or msg == "?" then
    help()
  elseif msg == "sync" then
    ns.Sync("commande")
  elseif msg == "bouton" or msg == "button" then
    ns.ToggleButton()
  elseif msg == "touche" or msg:match("^touche%s") or msg == "key" or msg:match("^key%s") then
    ns.BindKey(msg:match("^%S+%s+(%S+)"))
  else
    if ns.inCombat() then
      ns.print("en combat : la capture se fera à la sortie du combat.")
      for _, name in ipairs(ns.order) do ns.pending[name] = true end
      ns.waitingCombat = true
      return
    end
    local ok, err = ns.CaptureAll(true)
    ns.print(summaryLine())
    ns.print(string.format("%d domaines capturés%s. /sync pour l'envoyer à Claude.",
      ok, err > 0 and (", " .. err .. " en erreur (/scribe status)") or ""))
  end
end
