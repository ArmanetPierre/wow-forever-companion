-- ForeverScribe : mémoire des quêtes vues (schéma 1.4)
-- Note pendant le jeu qui donne et qui reçoit chaque quête, les quêtes proposées par
-- un PNJ, les endroits où les objectifs avancent et les points de carte des quêtes.
-- Stockage au niveau du compte (ForeverScribeDB.questMemory), commun à tous les persos,
-- taille bornée. Rien en combat : les événements sont mis en attente jusqu'à la fin du
-- combat. Les ids (quête, PNJ, objet, carte) ne sont jamais traduits ; les titres et
-- noms sont rangés par langue du client.
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS
local get, round = ns.get, ns.round

local MAX_QUESTS = 3000      -- quêtes gardées (les moins récemment vues partent d'abord)
local MAX_NPCS = 3000        -- PNJ gardés
local MAX_OBJECTS = 1000     -- objets du monde gardés
local MAX_PLACES = 3         -- donneurs / receveurs différents gardés par quête
local MAX_OFFERED = 5        -- PNJ qui proposent une même quête
local MAX_NPC_POINTS = 5     -- positions gardées par PNJ ou objet
local MAX_OBJ_POINTS = 8     -- positions gardées par objectif
local NEAR = 1.5             -- deux points plus proches que ça (en % de carte) = même point
local DETAIL_TTL = 600       -- un QUEST_DETAIL sert à l'acceptation pendant 10 min
local MAX_QUEUE = 50         -- événements gardés pendant un combat
local MEMORY_VERSION = 1

-- ---------------------------------------------------------------- stockage

local function memory()
  local db = _G.ForeverScribeDB
  if type(db) ~= "table" then return nil end
  local m = db.questMemory
  if type(m) ~= "table" then
    m = {}
    db.questMemory = m
  end
  m.version = MEMORY_VERSION
  m.quests = m.quests or {}
  m.npcs = m.npcs or {}
  m.objects = m.objects or {}
  return m
end
ns.QuestMemory = memory

local function locale()
  return ns.get("GetLocale") or "enUS"
end

-- Valeur masquée par l'API 12.x (combat, instance) : on n'écrit rien.
local function secret(v)
  local f = _G.issecretvalue
  if type(f) == "function" then
    local ok, res = pcall(f, v)
    if ok and res then return true end
  end
  return false
end

local function plainNumber(v)
  if type(v) ~= "number" or secret(v) then return nil end
  return v
end

local function plainString(v)
  if type(v) ~= "string" or v == "" or secret(v) then return nil end
  return v
end

local function setLocalized(rec, field, text)
  text = plainString(text)
  if not text then return end
  rec[field] = rec[field] or {}
  rec[field][locale()] = text
end

local function inInstance()
  local f = ns.api("IsInInstance")
  if f then
    local ok, inside, kind = pcall(f)
    if ok and inside then return true, kind end
    return false
  end
  local _, kind = get("GetInstanceInfo")
  if type(kind) == "string" and kind ~= "none" then return true, kind end
  return false
end

-- Position du joueur : { mapId, x, y } en % (x et y absents si l'API les masque).
local function playerPlace()
  local mapId = plainNumber(get("C_Map.GetBestMapForUnit", "player"))
  if not mapId then return nil end
  local place = { mapId = mapId }
  local pos = get("C_Map.GetPlayerMapPosition", mapId, "player")
  if type(pos) == "table" and type(pos.GetXY) == "function" then
    local ok, x, y = pcall(pos.GetXY, pos)
    x, y = ok and plainNumber(x), ok and plainNumber(y)
    if x and y and (x > 0 or y > 0) then
      place.x, place.y = round(x * 100, 1), round(y * 100, 1)
    end
  end
  local inside = inInstance()
  if inside then place.instance = true end
  return place
end

local function near(a, b)
  if a.mapId ~= b.mapId then return false end
  return math.abs(a.x - b.x) < NEAR and math.abs(a.y - b.y) < NEAR
end

-- Ajoute un point à une liste bornée, sans doublon proche. Un lieu sans coordonnées
-- (instance, position masquée) n'est pas un point.
local function addPoint(list, place, max)
  if not (place and place.x and place.y) then return list end
  list = list or {}
  for _, p in ipairs(list) do
    if near(p, place) then return list end
  end
  if #list >= max then return list end
  list[#list + 1] = { mapId = place.mapId, x = place.x, y = place.y }
  return list
end

-- ---------------------------------------------------------------- PNJ / objet

-- "Creature-0-1234-0-12-1234-0000ABCDEF" -> "npc", 1234 ; "GameObject-…" -> "object", id
local GUID_KINDS = { Creature = "npc", Vehicle = "npc", Pet = "npc", GameObject = "object" }
local function parseGuid(guid)
  guid = plainString(guid)
  if not guid then return nil end
  local kind = guid:match("^(%a+)%-")
  kind = kind and GUID_KINDS[kind]
  if not kind then return nil end
  local id = tonumber(guid:match("^[^-]*%-[^-]*%-[^-]*%-[^-]*%-[^-]*%-([^-]*)"))
  if not id or id <= 0 then return nil end
  return kind, id
end
ns.ParseQuestGuid = parseGuid

-- Le PNJ (ou l'objet) avec qui le joueur parle. Renvoie { kind, id, name } ou nil.
local function currentNpc()
  local kind, id = parseGuid(get("UnitGUID", "npc"))
  if not kind then return nil end
  return { kind = kind, id = id, name = plainString(get("UnitName", "npc")) }
end

local function rememberNpc(npc, place)
  if not npc or not npc.id then return end
  local m = memory()
  if not m then return end
  local bucket = npc.kind == "object" and m.objects or m.npcs
  local rec = bucket[npc.id] or {}
  bucket[npc.id] = rec
  setLocalized(rec, "names", npc.name)
  rec.points = addPoint(rec.points, place, MAX_NPC_POINTS)
  rec.lastSeen = ns.now()
end

-- ---------------------------------------------------------------- quêtes

local function quest(qid)
  qid = plainNumber(qid)
  if not qid or qid <= 0 then return nil end
  local m = memory()
  if not m then return nil end
  local q = m.quests[qid]
  if not q then
    q = { firstSeen = ns.now() }
    m.quests[qid] = q
  end
  q.lastSeen = ns.now()
  return q, qid
end

-- Ajoute un donneur ou un receveur (dédupliqué par type + id ; position mise à jour).
local function addPlace(q, field, npc, place, via)
  if not npc then return end
  q[field] = q[field] or {}
  local list = q[field]
  for _, e in ipairs(list) do
    if e.kind == npc.kind and e.id == npc.id then
      if place and place.x then e.mapId, e.x, e.y = place.mapId, place.x, place.y end
      if place and place.instance then e.instance = true end
      e.at = ns.now()
      if via == "turnin" then e.via = "turnin" end
      return
    end
  end
  if #list >= MAX_PLACES then return end
  local e = { kind = npc.kind, id = npc.id, at = ns.now(), via = via }
  if place then e.mapId, e.x, e.y, e.instance = place.mapId, place.x, place.y, place.instance end
  list[#list + 1] = e
end

local function addOffered(q, npc)
  if not npc or not npc.id then return end
  q.offeredBy = q.offeredBy or {}
  for _, e in ipairs(q.offeredBy) do
    if e.kind == npc.kind and e.id == npc.id then return end
  end
  if #q.offeredBy < MAX_OFFERED then q.offeredBy[#q.offeredBy + 1] = { kind = npc.kind, id = npc.id } end
end

local function setTitle(q, qid, title)
  title = plainString(title) or plainString(get("C_QuestLog.GetTitleForQuestID", qid))
  setLocalized(q, "titles", title)
end

-- Quêtes proposées (et en cours) chez un PNJ : GOSSIP_SHOW et QUEST_GREETING.
local function noteOffers(npc, place, available, active)
  for _, a in ipairs(available) do
    local q, qid = quest(a.id)
    if q then
      setTitle(q, qid, a.title)
      if plainNumber(a.level) and a.level > 0 then q.level = a.level end
      if a.repeatable then q.repeatable = true end
      if a.frequency and a.frequency > 0 then q.frequency = a.frequency end
      addOffered(q, npc)
    end
  end
  for _, a in ipairs(active) do
    local q, qid = quest(a.id)
    if q then
      setTitle(q, qid, a.title)
      -- un PNJ liste une quête en cours seulement s'il la reçoit (ou la donne)
      addPlace(q, "ends", npc, place, "listed")
    end
  end
end

local function onGossip()
  local npc = currentNpc()
  local place = playerPlace()
  rememberNpc(npc, place)
  local available, active = {}, {}
  local list = get("C_GossipInfo.GetAvailableQuests")
  if type(list) == "table" then
    for _, q in ipairs(list) do
      available[#available + 1] = { id = q.questID, title = q.title, level = q.questLevel,
        repeatable = q.repeatable, frequency = q.frequency }
    end
  end
  list = get("C_GossipInfo.GetActiveQuests")
  if type(list) == "table" then
    for _, q in ipairs(list) do active[#active + 1] = { id = q.questID, title = q.title } end
  end
  noteOffers(npc, place, available, active)
end

-- Ancien dialogue (QUEST_GREETING) : GetAvailableTitle et GetActiveTitle ne sont pas
-- dans la sonde ; ils sont utilisés seulement s'ils existent.
local function onGreeting()
  local npc = currentNpc()
  local place = playerPlace()
  rememberNpc(npc, place)
  local available, active = {}, {}
  for i = 1, get("GetNumAvailableQuests") or 0 do
    local _, frequency, repeatable, _, qid = get("GetAvailableQuestInfo", i)
    local title = ns.api("GetAvailableTitle") and get("GetAvailableTitle", i) or nil
    available[#available + 1] = { id = qid, title = title, frequency = frequency, repeatable = repeatable }
  end
  for i = 1, get("GetNumActiveQuests") or 0 do
    local qid = get("GetActiveQuestID", i)
    local title = ns.api("GetActiveTitle") and get("GetActiveTitle", i) or nil
    active[#active + 1] = { id = qid, title = title }
  end
  noteOffers(npc, place, available, active)
end

local function dialogTitle()
  return ns.api("GetTitleText") and get("GetTitleText") or nil
end

-- QUEST_DETAIL : quête affichée avant acceptation (PNJ, objet du monde ou objet du sac).
local function onDetail(startItemId)
  local qid = plainNumber(get("GetQuestID"))
  if not qid or qid <= 0 then return end
  local npc = currentNpc()
  startItemId = plainNumber(startItemId)
  if not npc and startItemId and startItemId > 0 then npc = { kind = "item", id = startItemId } end
  local place = playerPlace()
  ns.lastQuestDetail = { qid = qid, npc = npc, place = place, title = dialogTitle(), at = ns.now() }
  local q = quest(qid)
  if not q then return end
  setTitle(q, qid, ns.lastQuestDetail.title)
  if npc and npc.kind ~= "item" then
    rememberNpc(npc, place)
    addOffered(q, npc)
  end
end

local function snapshotPoi(qid)
  local q = memory() and memory().quests[qid]
  if not q then return end
  local mapId = plainNumber(get("C_Map.GetBestMapForUnit", "player"))
  if not mapId then return end
  local list = get("C_QuestLog.GetQuestsOnMap", mapId)
  if type(list) ~= "table" then return end
  for _, p in ipairs(list) do
    if p.questID == qid and plainNumber(p.x) and plainNumber(p.y) then
      q.poi = { mapId = p.mapID or mapId, x = round(p.x * 100, 1), y = round(p.y * 100, 1), at = ns.now() }
      return
    end
  end
end

-- QUEST_ACCEPTED : le donneur est celui du dernier QUEST_DETAIL de la même quête.
local function onAccepted(qid)
  qid = plainNumber(qid)
  local q
  q, qid = quest(qid)
  if not q then return end
  local d = ns.lastQuestDetail
  local npc, place
  if d and d.qid == qid and ns.now() - d.at <= DETAIL_TTL then
    npc, place = d.npc, d.place
    setTitle(q, qid, d.title)
  else
    npc, place = currentNpc(), playerPlace()
    setTitle(q, qid, nil)
  end
  ns.lastQuestDetail = nil
  if npc then
    addPlace(q, "starts", npc, place, "accept")
    if npc.kind ~= "item" then rememberNpc(npc, place) end
  end
  local logIndex = get("C_QuestLog.GetLogIndexForQuestID", qid)
  if logIndex then
    local info = get("C_QuestLog.GetInfo", logIndex)
    if type(info) == "table" and plainNumber(info.level) and info.level > 0 then q.level = info.level end
  end
  snapshotPoi(qid)
end

-- QUEST_PROGRESS / QUEST_COMPLETE : la fenêtre de rendu s'ouvre seulement chez le receveur.
local function onTurnInDialog()
  local qid = plainNumber(get("GetQuestID"))
  local q
  q, qid = quest(qid)
  if not q then return end
  local npc = currentNpc()
  local place = playerPlace()
  setTitle(q, qid, dialogTitle())
  if npc then
    rememberNpc(npc, place)
    addPlace(q, "ends", npc, place, "turnin")
  end
end

local function onTurnedIn(qid)
  local q = quest(qid)
  if q then q.turnedIn = true end
end

-- ---------------------------------------------------------------- objectifs

-- Dernier compteur vu par quête et objectif (ns.objectiveSnapshot, en mémoire seulement).
-- Le premier scan sert de référence : rien n'est noté avant une vraie progression.

local function scanObjectives()
  local entries = get("C_QuestLog.GetNumQuestLogEntries") or 0
  local now = {}
  local place
  local first = ns.objectiveSnapshot == nil
  local prev = ns.objectiveSnapshot or {}
  for i = 1, entries do
    local info = get("C_QuestLog.GetInfo", i)
    local qid = type(info) == "table" and not info.isHeader and plainNumber(info.questID)
    if qid and qid > 0 then
      local objectives = get("C_QuestLog.GetQuestObjectives", qid)
      now[qid] = {}
      if type(objectives) == "table" then
        for idx, o in ipairs(objectives) do
          local have = plainNumber(o.numFulfilled) or 0
          now[qid][idx] = have
          local before = prev[qid] and prev[qid][idx]
          if not first and before and have > before then
            place = place or playerPlace()
            local q = quest(qid)
            if q and place then
              q.objectives = q.objectives or {}
              local rec = q.objectives[idx] or {}
              q.objectives[idx] = rec
              rec.type = plainString(o.type) or rec.type
              rec.need = plainNumber(o.numRequired) or rec.need
              rec.points = addPoint(rec.points, place, MAX_OBJ_POINTS)
            end
          end
        end
      end
      -- quête prête à rendre : l'API donne le point de rendu suivant
      if not first and get("C_QuestLog.IsComplete", qid) then
        local known = memory() and memory().quests[qid]
        if not (known and known.waypoint) then
          local mapId, x, y = get("C_QuestLog.GetNextWaypoint", qid)
          if plainNumber(mapId) and plainNumber(x) and plainNumber(y) then
            local q = quest(qid)
            if q then q.waypoint = { mapId = mapId, x = round(x * 100, 1), y = round(y * 100, 1), at = ns.now() } end
          end
        end
      end
    end
  end
  ns.objectiveSnapshot = now
end

-- Points de carte des quêtes du journal pour la zone actuelle.
local function scanPoi()
  local mapId = plainNumber(get("C_Map.GetBestMapForUnit", "player"))
  if not mapId then return end
  local list = get("C_QuestLog.GetQuestsOnMap", mapId)
  if type(list) ~= "table" then return end
  local m = memory()
  if not m then return end
  for _, p in ipairs(list) do
    local q = m.quests[p.questID]
    if q and plainNumber(p.x) and plainNumber(p.y) then
      q.poi = { mapId = p.mapID or mapId, x = round(p.x * 100, 1), y = round(p.y * 100, 1), at = ns.now() }
    end
  end
end

-- ---------------------------------------------------------------- taille bornée

local function prune(bucket, max)
  local keys = {}
  for k in pairs(bucket) do keys[#keys + 1] = k end
  if #keys <= max then return end
  table.sort(keys, function(a, b) return (bucket[a].lastSeen or 0) < (bucket[b].lastSeen or 0) end)
  for i = 1, #keys - max do bucket[keys[i]] = nil end
end

function ns.PruneQuestMemory()
  local m = memory()
  if not m then return end
  prune(m.quests, MAX_QUESTS)
  prune(m.npcs, MAX_NPCS)
  prune(m.objects, MAX_OBJECTS)
end

-- ---------------------------------------------------------------- événements

-- QUEST_LOG_UPDATE arrive en rafale : un seul scan, une seconde après la dernière.
local scanScheduled = false
local function scheduleScan()
  if scanScheduled then return end
  local after = _G.C_Timer and _G.C_Timer.After
  if not after then return scanObjectives() end
  scanScheduled = true
  after(1, function()
    scanScheduled = false
    if ns.inCombat and ns.inCombat() then
      ns.questMemoryWaitingScan = true
      return
    end
    local ok, err = pcall(scanObjectives)
    local m = memory()
    if m and not ok then m.lastError = { event = "QUEST_LOG_UPDATE", message = tostring(err):sub(1, 160), at = ns.now() } end
  end)
end

local HANDLERS = {
  QUEST_DETAIL = onDetail,
  QUEST_ACCEPTED = function(a, b) onAccepted(b or a) end, -- (questID) ou (logIndex, questID)
  GOSSIP_SHOW = onGossip,
  QUEST_GREETING = onGreeting,
  QUEST_PROGRESS = onTurnInDialog,
  QUEST_COMPLETE = onTurnInDialog,
  QUEST_TURNED_IN = onTurnedIn,
  QUEST_LOG_UPDATE = scheduleScan,
  UNIT_QUEST_LOG_CHANGED = scheduleScan,
  ZONE_CHANGED_NEW_AREA = scanPoi,
}

local function run(event, ...)
  local fn = HANDLERS[event]
  if not fn or not memory() then return end
  local ok, err = pcall(fn, ...)
  local m = memory()
  if not ok and m then m.lastError = { event = event, message = tostring(err):sub(1, 160), at = ns.now() } end
  if m then m.updatedAt = ns.now() end
end

ns.questMemoryQueue = {}

local function flushQueue()
  local queue = ns.questMemoryQueue
  ns.questMemoryQueue = {}
  local unpackFn = _G.unpack or table.unpack
  for _, e in ipairs(queue) do run(e.event, unpackFn(e.args, 1, e.n)) end
end
ns.FlushQuestMemory = flushQueue

local frame = CreateFrame("Frame")
ns.questMemoryFrame = frame
for event in pairs(HANDLERS) do
  if event == "UNIT_QUEST_LOG_CHANGED" and frame.RegisterUnitEvent then
    pcall(frame.RegisterUnitEvent, frame, event, "player")
  else
    pcall(frame.RegisterEvent, frame, event)
  end
end
pcall(frame.RegisterEvent, frame, "PLAYER_LOGIN")
pcall(frame.RegisterEvent, frame, "PLAYER_REGEN_ENABLED")
pcall(frame.RegisterEvent, frame, "PLAYER_LOGOUT")

frame:SetScript("OnEvent", function(_, event, ...)
  if event == "PLAYER_LOGIN" then
    memory()
    ns.PruneQuestMemory()
    return
  elseif event == "PLAYER_REGEN_ENABLED" then
    if #ns.questMemoryQueue > 0 then flushQueue() end
    if ns.questMemoryWaitingScan then
      ns.questMemoryWaitingScan = false
      run("QUEST_LOG_UPDATE")
    end
    return
  elseif event == "PLAYER_LOGOUT" then
    pcall(ns.PruneQuestMemory)
    return
  end
  if event == "UNIT_QUEST_LOG_CHANGED" and (...) ~= "player" then return end
  if ns.inCombat and ns.inCombat() then
    local queue = ns.questMemoryQueue
    -- un seul scan des objectifs en attente suffit
    if event == "QUEST_LOG_UPDATE" or event == "UNIT_QUEST_LOG_CHANGED" then
      for _, e in ipairs(queue) do if e.event == "QUEST_LOG_UPDATE" then return end end
      event = "QUEST_LOG_UPDATE"
    end
    if #queue < MAX_QUEUE then
      queue[#queue + 1] = { event = event, args = { ... }, n = select("#", ...) }
    end
    return
  end
  run(event, ...)
end)
