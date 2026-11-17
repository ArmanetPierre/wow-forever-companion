-- Test hors jeu de ForeverScribe.
-- Usage (depuis la racine du repo) : lua addon/tests/run_capture.lua
-- Charge l'addon dans un environnement WoW simulé (valeurs réelles de la sonde),
-- rejoue une session (connexion, événements, combat, métier, banque, /scribe, /reload),
-- vérifie la sortie contre addon/tests/schema_spec.lua et écrit des fichiers d'exemple
-- dans addon/tests/fixtures/ (format SavedVariables du jeu + JSON).
local here = (arg and arg[0] or ""):match("^(.*)[/\\]") or "."
package.path = here .. "/?.lua;" .. package.path
local root = here .. "/../ForeverScribe/"

local spec = require("schema_spec")
local failures, checks = {}, 0

-- Textes attendus selon la langue du client simulé
local EXPECT = {
  frFR = {
    profession = "Travail du cuir", bow = "Arc des marais", bowSubType = "Arcs", repName = "Forgefer",
    leaderboard = "Insigne de la Confrérie : 0/3", played = "Temps de jeu",
    combatRefused = "en combat : synchro impossible", combatOver = "combat terminé",
    helpKey = "touche : CTRL%-SHIFT%-S", ready = "prêt %(", prefix = "ForeverScribe|r : ",
    binding = "Synchroniser pour Claude", moneyText = "po",
    status = "statut", help = "aide", button = "bouton", key = "touche",
  },
  enUS = {
    profession = "Leatherworking", bow = "Marsh Bow", bowSubType = "Bows", repName = "Ironforge",
    leaderboard = "Brotherhood Insignia: 0/3", played = "Total time played",
    combatRefused = "in combat: sync not possible", combatOver = "combat over",
    helpKey = "key: CTRL%-SHIFT%-S", ready = "ready %(", prefix = "ForeverScribe|r: ",
    binding = "Sync for Claude", moneyText = "g ",
    status = "status", help = "help", button = "button", key = "key",
  },
}

local function session(locale)
local X = EXPECT[locale]
package.loaded.wow_mock = nil
local mock = require("wow_mock")
_G.ForeverScribeDB, _G.ForeverScribeCharDB, _G.QuestMapFrame, _G.ForeverScribeNS = nil, nil, nil, nil
mock.install(_G, locale)

local function check(cond, msg)
  checks = checks + 1
  if not cond then failures[#failures + 1] = "[" .. locale .. "] " .. msg end
end

-- Charge les fichiers dans l'ordre du .toc
local ns = {}
local toc = assert(io.open(root .. "ForeverScribe.toc")):read("a")
for line in toc:gmatch("[^\r\n]+") do
  if line:match("%.lua%s*$") and not line:match("^##") then
    local chunk = assert(loadfile(root .. line:gsub("%s+$", "")))
    chunk("ForeverScribe", ns)
  end
end

-- Session simulée -------------------------------------------------------
mock.fire("ADDON_LOADED", "ForeverScribe")
mock.fire("PLAYER_LOGIN")
mock.runTimers()

local char = _G.ForeverScribeCharDB
check(char and char.identity, "capture de connexion absente")
check(#mock.timers == 0 and not ns.pending.reputations,
  "boucle : la lecture des réputations se redéclenche elle-même")
check(char.recipes == nil, "recettes capturées alors que la fenêtre de métier est fermée")
check(char.bank == nil, "banque capturée alors qu'elle est fermée")

-- temps de jeu reçu et message masqué dans le chat
for _, msg in ipairs(mock.chat) do
  check(not msg:find(X.played), "le message /played n'a pas été masqué")
end

-- sac modifié : relecture du seul sac 1
local before = char.bags.containers["0"]
mock.fire("BAG_UPDATE", 1)
mock.runTimers()
check(char.bags.containers["0"] == before, "BAG_UPDATE(1) a relu le sac 0 (devrait être incrémental)")

-- combat : la capture attend la fin du combat
mock.state.inCombat = true
local moneyAt = char.meta.domainsUpdatedAt.money
mock.clock = mock.clock + 5
_G.GetMoney = function() return 30000 end
mock.fire("PLAYER_MONEY")
mock.runTimers()
check(char.money.copper == 24016, "capture faite en combat")
mock.state.inCombat = false
mock.fire("PLAYER_REGEN_ENABLED")
mock.runTimers()
check(char.money.copper == 30000, "capture non faite après le combat")

-- fenêtre de métier
mock.state.tradeSkillOpen = true
-- client passé du français à l'anglais : l'ancienne entrée du même métier est remplacée
if locale == "enUS" then char.recipes = { ["Travail du cuir"] = { professionId = 165, recipes = {} } } end
mock.clock = mock.clock + 5
mock.fire("TRADE_SKILL_SHOW")
mock.runTimers()
check(char.recipes and char.recipes[X.profession] and char.recipes[X.profession].professionId == 165,
  "recettes non capturées à l'ouverture du métier")
mock.state.tradeSkillOpen = false
if locale == "enUS" then
  check(char.recipes["Travail du cuir"] == nil, "recettes : entrée de l'ancienne langue non retirée")
end

-- banque
mock.state.bankOpen = true
mock.fire("BANKFRAME_OPENED")
mock.runTimers()
mock.fire("BANKFRAME_CLOSED")
mock.state.bankOpen = false
check(char.bank and char.bank.containers["-1"], "banque non capturée à l'ouverture")

-- fonction absente et fonction en erreur : notées sans casser le domaine
_G.C_Roleset = nil
_G.C_GameRules.IsSelfFoundAllowed = function() error("argument invalide (simulé)") end

-- /scribe et /scribe status
mock.clock = mock.clock + 5
_G.SlashCmdList.FOREVERSCRIBE("")
_G.SlashCmdList.FOREVERSCRIBE(X.status)
check(char.bank ~= nil, "la banque a été effacée par /scribe (doit être conservée)")
check(char.recipes ~= nil, "les recettes ont été effacées par /scribe (doivent être conservées)")

check(char.meta.missing.forever and char.meta.missing.forever[1] == "C_Roleset.GetActiveAllowedRolesets",
  "fonction absente non notée dans meta.missing")
check(char.meta.callErrors.forever and char.meta.callErrors.forever[1]:find("IsSelfFoundAllowed"),
  "appel en erreur non noté dans meta.callErrors")
check(char.meta.errors.forever == nil, "une fonction absente ne doit pas mettre le domaine en erreur")
_G.C_Roleset = { GetActiveAllowedRolesets = function() return { 2 } end, GetActiveBlockedRolesets = function() return {} end }
_G.C_GameRules.IsSelfFoundAllowed = function() return false end
_G.SlashCmdList.FOREVERSCRIBE("")

-- Synchro pour Claude ----------------------------------------------------
local function chatHas(pattern)
  for _, msg in ipairs(mock.chat) do if msg:find(pattern) then return true end end
  return false
end
local btn = mock.named.ForeverScribeMinimapButton
check(btn ~= nil, "bouton de la minicarte non créé à la connexion")
check(btn and btn.shown, "bouton de la minicarte masqué par défaut")
_G.SlashCmdList.FOREVERSCRIBE(X.button)
check(btn and not btn.shown and _G.ForeverScribeDB.settings.showButton == false, "/scribe bouton n'a pas masqué le bouton")
_G.SlashCmdList.FOREVERSCRIBE(X.button)
check(btn and btn.shown and _G.ForeverScribeDB.settings.showButton == true, "/scribe bouton n'a pas réaffiché le bouton")
if btn then
  btn.scripts.OnEnter(btn)
  btn.scripts.OnDragStart(btn)
  check(btn.scripts.OnUpdate ~= nil, "glisser le bouton ne suit pas la souris")
  btn.scripts.OnUpdate(btn)
  btn.scripts.OnDragStop(btn)
  check(_G.ForeverScribeDB.settings.buttonAngle == 0, "angle du bouton non mis à jour après glissement")
end

-- en combat : refus, aucun rechargement, rappel à la sortie du combat
mock.state.inCombat = true
_G.SlashCmdList.FOREVERSCRIBESYNC("")
check(mock.reloads == 0, "/sync a rechargé l'interface en combat")
check(chatHas(X.combatRefused), "pas de message de refus en combat")
mock.state.inCombat = false
mock.fire("PLAYER_REGEN_ENABLED")
mock.runTimers()
check(chatHas(X.combatOver), "pas de rappel à la sortie du combat")
check(mock.reloads == 0, "rechargement automatique à la sortie du combat (interdit)")

-- hors combat : capture puis rechargement, raison enregistrée
_G.GetMoney = function() return 40000 end
_G.SlashCmdList.FOREVERSCRIBESYNC("")
check(mock.reloads == 1, "/sync n'a pas rechargé l'interface")
check(char.money.copper == 40000, "/sync n'a pas capturé avant de recharger")
check(char.meta.lastSyncReason == "commande", "raison /sync attendue « commande »")
_G.SlashCmdList.FOREVERSCRIBE("sync")
check(mock.reloads == 2, "/scribe sync n'a pas rechargé l'interface")
_G.ForeverScribe_Sync()
check(mock.reloads == 3 and char.meta.lastSyncReason == "touche", "raccourci : rechargement ou raison « touche » manquant")
if btn then btn:Click() end
check(mock.reloads == 4 and char.meta.lastSyncReason == "bouton", "bouton : rechargement ou raison « bouton » manquant")

-- attribution de la touche : uniquement si elle est libre
_G.SlashCmdList.FOREVERSCRIBE(X.key)
check(mock.bindings["CTRL-SHIFT-S"] == "FOREVERSCRIBE_SYNC" and mock.savedBindings == 2, "/scribe touche n'a pas attribué CTRL-SHIFT-S")
mock.bindings["CTRL-ALT-S"] = "TOGGLEBAG1"
_G.SlashCmdList.FOREVERSCRIBE(X.key .. " ctrl-alt-s")
check(mock.bindings["CTRL-ALT-S"] == "TOGGLEBAG1", "/scribe touche a écrasé une touche déjà utilisée")
_G.SlashCmdList.FOREVERSCRIBE(X.help)
check(chatHas(X.helpKey), "l'aide n'affiche pas la touche attribuée")

-- /reload = PLAYER_LOGOUT (juste après la demande du bouton : la raison est conservée)
mock.fire("PLAYER_LOGOUT")
check(char.meta.lastSyncReason == "bouton", "la déconnexion a écrasé une demande récente")
check(type(char.meta.writtenAt) == "number", "meta.writtenAt absent après l'écriture")
-- écriture sans demande récente = déconnexion, sortie ou /reload tapé
char.meta.lastSyncRequestAt = char.meta.lastSyncRequestAt - 100
mock.fire("PLAYER_LOGOUT")
check(char.meta.lastSyncReason == "deconnexion", "raison « deconnexion » attendue sans demande récente")

-- réputation repliée restaurée
for _, f in ipairs(mock.FACTIONS) do
  if f.factionID == 1169 then check(f.isCollapsed == true, "catégorie de réputation non repliée après lecture") end
end
local foundHidden = false
for _, r in ipairs(char.reputations.list) do if r.id == 21 then foundHidden = true end end
check(foundHidden, "réputation d'une catégorie repliée non lue")

-- Validation du schéma ----------------------------------------------------
local function at(t, path)
  for part in path:gmatch("[^%.]+") do
    if type(t) ~= "table" then return nil end
    t = t[part]
  end
  return t
end
local function validate(tbl, rules, label)
  for path, ty in pairs(rules) do
    local optional = ty:sub(-1) == "?"
    local want = optional and ty:sub(1, -2) or ty
    local v = at(tbl, path)
    if v == nil then
      check(optional, label .. "." .. path .. " manquant")
    else
      check(type(v) == want, label .. "." .. path .. " : " .. want .. " attendu, " .. type(v) .. " obtenu")
    end
  end
end
validate(_G.ForeverScribeDB, spec.account, "ForeverScribeDB")
local entry = _G.ForeverScribeDB.characters["Player-1234-0A1B2C3D"]
check(entry ~= nil, "index du compte sans entrée pour le perso")
if entry then validate(entry, spec.indexEntry, "index") end
validate(char, spec.character, "ForeverScribeCharDB")
validate(char, spec.onDemand, "ForeverScribeCharDB")
for name, e in pairs(char.meta.errors) do check(false, "erreur de domaine " .. name .. " : " .. tostring(e.message)) end

-- valeurs clés
check(char.identity.ruleset == "PvP", "ruleset attendu PvP, obtenu " .. tostring(char.identity.ruleset))
check(char.stats.ranged.attackPower == 233, "PA distance attendue 233")
check(char.bags.ammo.total == 550, "munitions attendues 550, obtenu " .. tostring(char.bags.ammo.total))
check(#char.talents.nodes == 3, "3 talents pris attendus, obtenu " .. #char.talents.nodes)
check(char.pet.current.trainingPoints.available == 44, "points de dressage disponibles attendus 44")
check(char.quests.list[2].objectives[1].text == X.leaderboard, "repli GetQuestLogLeaderBoard non appliqué")
check(char.quests.list[2].position and char.quests.list[2].position.x == 23, "coordonnées de quête absentes")

-- récompenses de quête (1.2)
do
  local q = char.quests.list[1]
  local r = q and q.rewards
  check(type(r) == "table", "récompenses de la quête 289 absentes")
  if type(r) == "table" then
    check(#r.choices == 3, "3 objets au choix attendus, obtenu " .. #r.choices)
    check(r.choices[1].name == X.bow and r.choices[1].dps == 14.8, "arc au choix mal lu")
    check(r.choices[1].equipLoc == "INVTYPE_RANGED" and r.choices[1].subType == X.bowSubType
      and r.choices[1].classId == 2 and r.choices[1].subclassId == 2, "emplacement/type de l'arc absent")
    check(r.choices[3].stats and r.choices[3].stats.ITEM_MOD_AGILITY_SHORT == 3, "stats des gants absentes")
    check(#r.items == 1 and r.items[1].count == 2, "récompense fixe (2 potions) mal lue")
    check(r.money == 1500 and r.xp == 2150, "argent/XP de récompense mal lus")
    check(r.factions[1] and r.factions[1].name == X.repName and r.factions[1].amount == 250, "réputation de récompense mal lue")
    check(r.choices[1].link and r.choices[1].link:find("|Hitem:9001", 1, true), "lien de l'objet au choix absent")
  end
  local r2 = char.quests.list[2].rewards
  check(type(r2) == "table" and #r2.choices == 0 and r2.money == 900, "quête sans objet : argent seul attendu")
  check(mock.selectedQuest == 0, "sélection du journal non restaurée (" .. tostring(mock.selectedQuest) .. ")")
  local calls = mock.selectCalls
  ns.RunDomain("quests")
  check(mock.selectCalls == calls, "les récompenses déjà connues ne doivent pas être relues")
  check(type(char.quests.list[1].rewards) == "table" and #char.quests.list[1].rewards.choices == 3, "récompenses perdues à la recapture")
  -- journal ouvert par le joueur : on ne touche pas à sa sélection, on réessaie plus tard
  char.quests = nil
  _G.QuestMapFrame = { IsShown = function() return true end }
  calls = mock.selectCalls
  ns.RunDomain("quests")
  check(mock.selectCalls == calls, "sélection modifiée alors que le journal est ouvert")
  check(char.quests.list[1].rewards == nil, "récompenses lues alors que le journal est ouvert")
  _G.QuestMapFrame = nil
  ns.RunDomain("quests")
  check(type(char.quests.list[1].rewards) == "table", "récompenses non relues après fermeture du journal")
end

-- Langue (1.3) ---------------------------------------------------------------
check(char.meta.locale == locale, "meta.locale attendu " .. locale .. ", obtenu " .. tostring(char.meta.locale))
check(entry and entry.locale == locale and entry.raceFile == "Dwarf", "index : locale ou raceFile absents")
check(char.identity.raceFile == "Dwarf" and char.identity.classFile == "HUNTER", "jetons race/classe non traduits attendus")
check(_G.BINDING_NAME_FOREVERSCRIBE_SYNC == X.binding, "libellé du raccourci dans la mauvaise langue")
check(char.money.text and char.money.text:find(X.moneyText, 1, true), "money.text dans la mauvaise langue : " .. tostring(char.money.text))
check(char.bags.ammo.byId["2519"] == 200 and char.bags.ammo.byId["2516"] == 350, "bags.ammo.byId absent ou faux")
check(char.quests.list[3] and char.quests.list[3].tagId == 41, "quests.list[].tagId absent")
do
  local rep
  for _, r in ipairs(char.reputations.list) do if r.id == 47 then rep = r end end
  check(rep and rep.standingToken == "FRIENDLY" and rep.categoryId == 469, "réputation : standingToken/categoryId absents")
end
check(char.pet.current.loyaltyLevel == 6, "pet.current.loyaltyLevel attendu 6")
check(char.spells.lines[1] and char.spells.lines[1].index == 1, "spells.lines[].index absent")
local lines = 0
for _, msg in ipairs(mock.chat) do
  if msg:find("ForeverScribe|r", 1, true) then
    lines = lines + 1
    check(msg:find(X.prefix, 1, true) == 5 or msg:find(X.prefix, 1, true) ~= nil, "préfixe du chat inattendu : " .. msg)
    if locale == "enUS" then
      check(not msg:find("[\195][\160-\191]"), "texte accentué (français ?) dans le chat anglais : " .. msg)
    end
  end
end
check(lines > 20, "trop peu de messages de l'addon dans le chat")
check(chatHas(X.ready), "message de connexion absent ou dans la mauvaise langue")

return char, _G.ForeverScribeDB, mock.chat
end -- session

-- Sérialisation -------------------------------------------------------------
local function sortedKeys(t)
  local keys = {}
  for k in pairs(t) do keys[#keys + 1] = k end
  table.sort(keys, function(a, b)
    if type(a) == type(b) then return a < b end
    return type(a) == "number"
  end)
  return keys
end

local function luaValue(v)
  if type(v) == "string" then
    return '"' .. v:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub("\n", "\\n") .. '"'
  elseif type(v) == "number" then
    if math.type and math.type(v) == "integer" then return tostring(v) end
    if v == math.floor(v) and math.abs(v) < 2^53 then return string.format("%d", v) end
    return string.format("%.17g", v)
  end
  return tostring(v)
end

-- Format proche de celui écrit par le client WoW
local function writeSV(name, value)
  local out = {}
  local function emit(v, indent)
    if type(v) ~= "table" then out[#out + 1] = luaValue(v); return end
    out[#out + 1] = "{\n"
    for _, k in ipairs(sortedKeys(v)) do
      out[#out + 1] = string.rep("\t", indent + 1)
      out[#out + 1] = "[" .. luaValue(k) .. "] = "
      emit(v[k], indent + 1)
      out[#out + 1] = ",\n"
    end
    out[#out + 1] = string.rep("\t", indent) .. "}"
  end
  out[#out + 1] = "\n" .. name .. " = "
  emit(value, 0)
  out[#out + 1] = "\n"
  return table.concat(out)
end

local function isArray(t)
  local n = 0
  for k in pairs(t) do
    if type(k) ~= "number" then return false end
    n = n + 1
  end
  for i = 1, n do if t[i] == nil then return false end end
  return true
end

local function json(v, indent)
  indent = indent or ""
  local ty = type(v)
  if ty == "table" then
    local inner = indent .. "  "
    local parts = {}
    if next(v) == nil then return "{}" end
    if isArray(v) then
      for _, x in ipairs(v) do parts[#parts + 1] = inner .. json(x, inner) end
      return "[\n" .. table.concat(parts, ",\n") .. "\n" .. indent .. "]"
    end
    for _, k in ipairs(sortedKeys(v)) do
      parts[#parts + 1] = inner .. json(tostring(k)) .. ": " .. json(v[k], inner)
    end
    return "{\n" .. table.concat(parts, ",\n") .. "\n" .. indent .. "}"
  elseif ty == "string" then
    return '"' .. v:gsub('[%c"\\]', function(c)
      local map = { ['"'] = '\\"', ['\\'] = '\\\\', ['\n'] = '\\n', ['\t'] = '\\t', ['\r'] = '\\r' }
      return map[c] or string.format("\\u%04x", c:byte())
    end) .. '"'
  elseif ty == "number" then
    return luaValue(v)
  end
  return tostring(v)
end

-- Exécution dans les deux langues ------------------------------------------
local charFR, accountFR, chatFR = session("frFR")
local charEN, accountEN, chatEN = session("enUS")

-- Les clés non traduites doivent être identiques en frFR et en enUS.
-- On retire les libellés traduits (et les horodatages), puis on compare tout le reste.
local LOCALIZED = {
  name = true, title = true, text = true, zone = true, subZone = true, race = true, class = true,
  family = true, category = true, standing = true, type = true, subType = true, link = true,
  tooltip = true, loyalty = true, loyaltyName = true, food = true, specName = true, configName = true,
  bind = true, parentMapName = true, tag = true, skillLineName = true, factionLocalized = true,
  professionName = true, subName = true, specialization = true, locale = true,
  mapName = true, realZone = true,
}
local VOLATILE = {
  capturedAt = true, capturedAtISO = true, at = true, writtenAt = true, lastSyncRequestAt = true,
  domainsUpdatedAt = true, lastCapture = true, lastCaptureISO = true,
}
local function norm(v, key, parentKey)
  if type(v) ~= "table" then return v end
  local out = {}
  for k, x in pairs(v) do
    local drop = type(k) == "string" and (LOCALIZED[k] or VOLATILE[k])
    if k == "items" and key == "ammo" then drop = true end
    if not drop then out[k] = norm(x, k, key) end
  end
  return out
end
local function byProfessionId(recipes)
  local out = {}
  for _, r in pairs(recipes or {}) do out[tostring(r.professionId)] = r end
  return out
end
local function diff(a, b, path, acc)
  if type(a) ~= type(b) then acc[#acc + 1] = path .. " : " .. tostring(a) .. " ≠ " .. tostring(b); return end
  if type(a) ~= "table" then
    if a ~= b then acc[#acc + 1] = path .. " : " .. tostring(a) .. " ≠ " .. tostring(b) end
    return
  end
  local keys = {}
  for k in pairs(a) do keys[k] = true end
  for k in pairs(b) do keys[k] = true end
  for k in pairs(keys) do diff(a[k], b[k], path .. "." .. tostring(k), acc) end
end
do
  local a, b = norm(charFR), norm(charEN)
  a.recipes, b.recipes = norm(byProfessionId(charFR.recipes)), norm(byProfessionId(charEN.recipes))
  local acc = {}
  diff(a, b, "char", acc)
  checks = checks + 1
  if #acc > 0 then
    table.sort(acc)
    failures[#failures + 1] = "clés non traduites différentes entre frFR et enUS (" .. #acc .. ") : " .. table.concat(acc, " | ", 1, math.min(#acc, 8))
  end
  -- et les libellés, eux, ont bien changé de langue
  checks = checks + 1
  if charFR.position.zone == charEN.position.zone then failures[#failures + 1] = "zone identique dans les deux langues (mock enUS inactif ?)" end
end

local fixtures = here .. "/fixtures/"
os.execute('mkdir -p "' .. fixtures .. '"')
local function write(path, content)
  local f = assert(io.open(path, "w"))
  f:write(content)
  f:close()
end
write(fixtures .. "account_SavedVariables_ForeverScribe.lua", writeSV("ForeverScribeDB", accountFR))
write(fixtures .. "character_SavedVariables_ForeverScribe.lua", writeSV("ForeverScribeCharDB", charFR))
write(fixtures .. "character.json", json(charFR) .. "\n")
write(fixtures .. "character_SavedVariables_ForeverScribe.enUS.lua", writeSV("ForeverScribeCharDB", charEN))
write(fixtures .. "character.enUS.json", json(charEN) .. "\n")

-- Rapport -------------------------------------------------------------------
print(string.format("Vérifications : %d, échecs : %d", checks, #failures))
for _, f in ipairs(failures) do print("  ÉCHEC : " .. f) end
local function dump(label, chat)
  print("Messages du chat simulé (" .. label .. ") :")
  for _, msg in ipairs(chat) do print("  " .. msg:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", "")) end
end
dump("frFR", chatFR)
dump("enUS", chatEN)
print("Fixtures écrites dans " .. fixtures)
os.exit(#failures == 0 and 0 or 1)
