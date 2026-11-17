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

ns.RegisterDomain("quests", {
  label = "Quêtes",
  events = {
    QUEST_LOG_UPDATE = true, QUEST_ACCEPTED = true, QUEST_REMOVED = true, QUEST_TURNED_IN = true,
    ZONE_CHANGED_NEW_AREA = true,
  },
  unitEvents = { UNIT_QUEST_LOG_CHANGED = "player" },
  collect = function()
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
