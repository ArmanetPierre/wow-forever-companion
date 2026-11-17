-- ForeverScribe : métiers, lignes de compétence, recettes
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS
local get = ns.get

local PROF_SLOTS = { "primary1", "primary2", "archaeology", "fishing", "cooking", "firstAid" }

ns.RegisterDomain("professions", {
  label = "Métiers",
  events = { SKILL_LINES_CHANGED = true, CHAT_MSG_SKILL = true, TRADE_SKILL_SHOW = true, PLAYER_LEVEL_UP = true },
  collect = function()
    local out = { professions = {}, skills = {} }
    local indexes = { get("GetProfessions") }
    for i, slot in ipairs(PROF_SLOTS) do
      local idx = indexes[i]
      if idx then
        local name, icon, rank, maxRank, numAbilities, spellOffset, skillLineId, modifier,
              specIndex, specOffset, skillLineName = get("GetProfessionInfo", idx)
        if name then
          out.professions[#out.professions + 1] = {
            slot = slot, name = name, skillLineId = skillLineId, rank = rank, max = maxRank,
            modifier = modifier, specializationIndex = specIndex,
            skillLineName = skillLineName, numAbilities = numAbilities,
          }
        end
      end
    end

    local n = get("C_SkillInfo.GetNumSkillLines") or 0
    local header
    for i = 1, n do
      local s = get("C_SkillInfo.GetSkillLineInfo", i)
      if type(s) == "table" then
        if s.isHeader then
          header = s.name
        else
          out.skills[#out.skills + 1] = {
            name = s.name, skillId = s.skillID, category = header,
            rank = s.rank, max = s.maxRank, modifier = s.modifier, temp = s.tempPoints,
            abandonable = s.isAbandonable or nil,
          }
        end
      end
    end
    return out
  end,
})

-- Recettes : lisibles seulement quand la fenêtre du métier est ouverte.
-- Conservées d'une session à l'autre, une entrée par métier.
ns.RegisterDomain("recipes", {
  label = "Recettes",
  login = false,
  events = { TRADE_SKILL_SHOW = true, TRADE_SKILL_LIST_UPDATE = true, NEW_RECIPE_LEARNED = true },
  collect = function(_, previous)
    local ready = ns.api("C_TradeSkillUI.IsTradeSkillReady")
    if ready and not get("C_TradeSkillUI.IsTradeSkillReady") then return nil end
    if get("C_TradeSkillUI.IsTradeSkillLinked") or get("C_TradeSkillUI.IsNPCCrafting") then return nil end
    local base = get("C_TradeSkillUI.GetBaseProfessionInfo")
    if type(base) ~= "table" or not base.professionName or base.professionName == "" then return nil end
    local ids = get("C_TradeSkillUI.GetAllRecipeIDs")
    if type(ids) ~= "table" or #ids == 0 then return nil end

    local recipes = {}
    for _, id in ipairs(ids) do
      local r = get("C_TradeSkillUI.GetRecipeInfo", id)
      if type(r) == "table" then
        recipes[#recipes + 1] = {
          id = id, name = r.name, learned = r.learned and true or false,
          difficulty = r.relativeDifficulty, skillUps = r.numSkillUps,
          craftable = r.craftable, available = r.numAvailable, categoryId = r.categoryID,
        }
      end
    end
    local out = previous or {}
    out[base.professionName] = {
      professionId = base.professionID,
      skillLevel = base.skillLevel, maxSkillLevel = base.maxSkillLevel,
      capturedAt = ns.now(),
      recipes = recipes,
    }
    return out
  end,
})
