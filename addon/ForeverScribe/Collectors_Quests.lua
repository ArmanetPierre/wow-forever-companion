-- ForeverScribe : journal de quêtes et quêtes terminées
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS
local get, round = ns.get, ns.round

local function objectiveRecord(o, logIndex, objIndex)
  local text = o.text
  -- Le nom de l'objet peut manquer tant qu'il n'est pas en cache (« : 0/3 »)
  if (not text or text:match("^%s*:")) and logIndex then
    local alt = get("GetQuestLogLeaderBoard", objIndex, logIndex)
    if type(alt) == "string" and alt ~= "" then text = alt end
  end
  return {
    text = text, type = o.type, done = o.finished and true or false,
    have = o.numFulfilled, need = o.numRequired,
  }
end

local function mapPositions(mapIds)
  local out = {}
  for _, mapId in ipairs(mapIds) do
    local list = get("C_QuestLog.GetQuestsOnMap", mapId)
    if type(list) == "table" then
      for _, q in ipairs(list) do
        if q.questID and not out[q.questID] and q.x and q.y then
          out[q.questID] = { mapId = q.mapID or mapId, x = round(q.x * 100, 1), y = round(q.y * 100, 1) }
        end
      end
    end
  end
  return out
end


-- ---------------------------------------------------------------- récompenses
-- Les récompenses d'une quête ne changent pas : elles sont lues une fois puis
-- réutilisées (pas de sélection de quête à chaque capture).

local function questLogShown()
  for _, name in ipairs({ "QuestMapFrame", "QuestLogFrame", "QuestLogDetailFrame" }) do
    local f = _G[name]
    if type(f) == "table" and type(f.IsShown) == "function" then
      local ok, shown = pcall(f.IsShown, f)
      if ok and shown then return true end
    end
  end
  return false
end

local function rewardItem(kind, index, questId, name, numItems, quality, isUsable, itemId, ilvl)
  local link = get("GetQuestLogItemLink", kind, index, questId)
  if type(link) ~= "string" and type(itemId) == "number" and itemId > 0 then link = "item:" .. itemId end
  local rec
  if type(link) == "string" then
    rec = ns.ItemRecord and ns.ItemRecord(link) or { itemId = itemId }
    if rec.link and not rec.link:find("|H") then rec.link = nil end
  else
    rec = {}
  end
  rec.itemId = rec.itemId or itemId
  rec.name = rec.name or name
  rec.count = (type(numItems) == "number" and numItems > 1) and numItems or nil
  rec.quality = rec.quality or quality
  rec.itemLevel = rec.itemLevel or ilvl
  rec.usable = (isUsable == nil) and nil or (isUsable and true or false)
  if rec.pending then ns.waitingRewardItems = true end
  return rec
end

local function readRewards(qid)
  local r = { choices = {}, items = {}, factions = {}, spells = {} }
  local money = get("GetQuestLogRewardMoney", qid)
  if type(money) == "number" and money > 0 then r.money = money end
  local xp = get("GetQuestLogRewardXP", qid)
  if type(xp) == "number" and xp > 0 then r.xp = xp end

  local nChoices = get("GetNumQuestLogChoices", qid, true) or 0
  local nItems = get("GetNumQuestLogRewards", qid) or 0
  local needSelect = (nChoices > 0 or nItems > 0)
  local previous
  if needSelect then
    if questLogShown() then return nil end -- le joueur lit son journal : on réessaiera
    previous = get("C_QuestLog.GetSelectedQuest")
    if previous ~= qid then ns.call("C_QuestLog.SetSelectedQuest", qid) end
  end
  local pending = false
  for i = 1, nChoices do
    local name, _, num, quality, usable, itemId, ilvl = get("GetQuestLogChoiceInfo", i, qid)
    if name or itemId then
      local rec = rewardItem("choice", i, qid, name, num, quality, usable, itemId, ilvl)
      pending = pending or rec.pending
      r.choices[#r.choices + 1] = rec
    end
  end
  for i = 1, nItems do
    local name, _, num, quality, usable, itemId, ilvl = get("GetQuestLogRewardInfo", i, qid)
    if name or itemId then
      local rec = rewardItem("reward", i, qid, name, num, quality, usable, itemId, ilvl)
      pending = pending or rec.pending
      r.items[#r.items + 1] = rec
    end
  end
  if needSelect and previous ~= qid then ns.call("C_QuestLog.SetSelectedQuest", previous or 0) end

  local nFactions = get("GetNumQuestLogRewardFactions", qid) or 0
  for i = 1, nFactions do
    local factionId, base, override = get("GetQuestLogRewardFactionInfo", i, qid)
    if type(factionId) == "number" then
      local data = get("C_Reputation.GetFactionDataByID", factionId)
      r.factions[#r.factions + 1] = {
        factionId = factionId, name = type(data) == "table" and data.name or nil,
        amount = (type(override) == "number" and override ~= 0) and override or base,
      }
    end
  end
  -- Fonction optionnelle selon le client : on ne la signale pas comme manquante
  local spells = (C_QuestInfoSystem and C_QuestInfoSystem.GetQuestRewardSpells)
    and get("C_QuestInfoSystem.GetQuestRewardSpells", qid) or nil
  if type(spells) == "table" then
    for _, spellId in ipairs(spells) do
      if type(spellId) == "number" then
        r.spells[#r.spells + 1] = { spellId = spellId, name = get("C_Spell.GetSpellName", spellId) }
      end
    end
  end
  if pending then r.pending = true end
  r.readAt = ns.now()
  return r
end
ns.ReadQuestRewards = readRewards

local function previousRewards(previous)
  local map = {}
  if type(previous) == "table" and type(previous.list) == "table" then
    for _, q in ipairs(previous.list) do
      if q.id and type(q.rewards) == "table" and not q.rewards.pending then map[q.id] = q.rewards end
    end
  end
  return map
end

ns.RegisterDomain("quests", {
  label = "Quêtes",
  events = {
    QUEST_LOG_UPDATE = true, QUEST_ACCEPTED = true, QUEST_REMOVED = true, QUEST_TURNED_IN = true,
    ZONE_CHANGED_NEW_AREA = true,
    GET_ITEM_INFO_RECEIVED = function() return ns.waitingRewardItems end,
    ITEM_DATA_LOAD_RESULT = function() return ns.waitingRewardItems end,
  },
  unitEvents = { UNIT_QUEST_LOG_CHANGED = "player" },
  collect = function(_, previous)
    ns.waitingRewardItems = false
    local known = previousRewards(previous)
    local entries, numQuests = get("C_QuestLog.GetNumQuestLogEntries")
    local maxQuests = get("C_QuestLog.GetMaxNumQuestsCanAccept") or get("C_QuestLog.GetMaxNumQuests")
    local out = { count = numQuests, max = maxQuests, list = {} }

    local mapIds = {}
    local mapId = get("C_Map.GetBestMapForUnit", "player")
    if mapId then
      mapIds[#mapIds + 1] = mapId
      local info = get("C_Map.GetMapInfo", mapId)
      if type(info) == "table" and info.parentMapID then mapIds[#mapIds + 1] = info.parentMapID end
    end
    local positions = mapPositions(mapIds)

    local header
    for i = 1, entries or 0 do
      local info = get("C_QuestLog.GetInfo", i)
      if type(info) == "table" then
        if info.isHeader then
          header = info.title
        elseif info.questID and info.questID > 0 and not info.isHidden then
          local qid = info.questID
          local q = {
            id = qid,
            title = info.title or get("C_QuestLog.GetTitleForQuestID", qid),
            category = header,
            level = info.level,
            difficultyLevel = info.difficultyLevel,
            suggestedGroup = (info.suggestedGroup and info.suggestedGroup > 0) and info.suggestedGroup or nil,
            frequency = info.frequency,
            isTask = info.isTask or nil,
            isOnMap = info.isOnMap or nil,
            complete = get("C_QuestLog.IsComplete", qid) and true or false,
            failed = get("C_QuestLog.IsFailed", qid) and true or nil,
            questType = get("C_QuestLog.GetQuestType", qid),
            position = positions[qid],
          }
          local tag = get("C_QuestLog.GetQuestTagInfo", qid)
          if type(tag) == "table" then q.tag = tag.tagName end
          local favor = get("C_QuestInfoSystem.GetQuestLogRewardFavor", qid)
          if type(favor) == "number" and favor > 0 then q.rewardFavor = favor end
          local objectives = get("C_QuestLog.GetQuestObjectives", qid)
          q.objectives = {}
          if type(objectives) == "table" then
            for idx, o in ipairs(objectives) do
              q.objectives[#q.objectives + 1] = objectiveRecord(o, i, idx)
            end
          end
          local okR, rewards = pcall(function() return known[qid] or readRewards(qid) end)
          if okR then q.rewards = rewards end
          out.list[#out.list + 1] = q
        end
      end
    end
    out.trivialRange = get("C_QuestLog.GetTrivialRange")
    out.dailyCompleted = get("GetDailyQuestsCompleted")
    return out
  end,
})

ns.RegisterDomain("questsCompleted", {
  label = "Quêtes terminées",
  events = { QUEST_TURNED_IN = true },
  collect = function()
    local ids = get("C_QuestLog.GetAllCompletedQuestIDs")
    if type(ids) ~= "table" then return nil end
    local list = {}
    for _, id in ipairs(ids) do list[#list + 1] = id end
    table.sort(list)
    return { count = #list, ids = list }
  end,
})
