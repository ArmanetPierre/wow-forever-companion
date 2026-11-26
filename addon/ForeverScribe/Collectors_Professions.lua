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
-- API moderne C_TradeSkillUI si présente, sinon API classique GetNumTradeSkills /
-- GetTradeSkillInfo. Couleur (1.5) : jeton non traduit skillType.

-- Enum.TradeskillRelativeDifficulty : 0 orange, 1 jaune, 2 vert, 3 gris
local DIFFICULTY_TOKENS = { [0] = "optimal", [1] = "medium", [2] = "easy", [3] = "trivial" }
local TOKEN_DIFFICULTY = { optimal = 0, medium = 1, easy = 2, trivial = 3 }

-- Liste des composants : { { itemId, count, name }, … }
local function reagentList(list)
  return (#list > 0) and list or nil
end

-- Objet fabriqué et composants d'une recette (API moderne). Statique : repris de la
-- capture précédente quand il est déjà connu, pour ne pas tout relire à chaque mise à jour.
local function modernStatic(id, known)
  if known and known.itemId and known.reagents then
    return known.itemId, known.reagents, known.made
  end
  local itemId, made
  local reagents = {}
  local sch = get("C_TradeSkillUI.GetRecipeSchematic", id, false)
  if type(sch) == "table" then
    itemId = sch.outputItemID
    if type(sch.quantityMin) == "number" then
      made = { min = sch.quantityMin, max = sch.quantityMax or sch.quantityMin }
    end
    for _, slot in ipairs(type(sch.reagentSlotSchematics) == "table" and sch.reagentSlotSchematics or {}) do
      local first = type(slot.reagents) == "table" and slot.reagents[1]
      -- reagentType 1 = composant de base (les autres sont facultatifs)
      if type(first) == "table" and first.itemID and (slot.reagentType == nil or slot.reagentType == 1) then
        reagents[#reagents + 1] = { itemId = first.itemID, count = slot.quantityRequired }
      end
    end
  end
  if not itemId then
    local out = get("C_TradeSkillUI.GetRecipeOutputItemData", id)
    if type(out) == "table" then itemId = out.itemID or ns.itemIdFromLink(out.hyperlink) end
  end
  if not itemId then itemId = ns.itemIdFromLink(get("C_TradeSkillUI.GetRecipeItemLink", id)) end
  if #reagents == 0 then
    local n = get("C_TradeSkillUI.GetRecipeNumReagents", id) or 0
    for i = 1, n do
      local name, _, count = get("C_TradeSkillUI.GetRecipeReagentInfo", id, i)
      local rid = ns.itemIdFromLink(get("C_TradeSkillUI.GetRecipeReagentItemLink", id, i))
      if rid or name then reagents[#reagents + 1] = { itemId = rid, count = count, name = name } end
    end
  end
  return itemId, reagentList(reagents), made
end

local function collectModern(previous)
  local ready = ns.api("C_TradeSkillUI.IsTradeSkillReady")
  if ready and not get("C_TradeSkillUI.IsTradeSkillReady") then return nil end
  if get("C_TradeSkillUI.IsTradeSkillLinked") or get("C_TradeSkillUI.IsNPCCrafting") then return nil end
  local base = get("C_TradeSkillUI.GetBaseProfessionInfo")
  if type(base) ~= "table" or not base.professionName or base.professionName == "" then return nil end
  local ids = get("C_TradeSkillUI.GetAllRecipeIDs")
  if type(ids) ~= "table" or #ids == 0 then return nil end

  local known = {}
  local prev = previous and previous[base.professionName]
  for _, r in ipairs(type(prev) == "table" and type(prev.recipes) == "table" and prev.recipes or {}) do
    if r.id then known[r.id] = r end
  end
  local recipes = {}
  for _, id in ipairs(ids) do
    local r = get("C_TradeSkillUI.GetRecipeInfo", id)
    if type(r) == "table" then
      local difficulty = r.relativeDifficulty
      if type(difficulty) ~= "number" and type(r.difficulty) == "number" then difficulty = r.difficulty end
      local itemId, reagents, made = modernStatic(id, known[id])
      recipes[#recipes + 1] = {
        id = id, spellId = id, name = r.name, learned = r.learned and true or false,
        difficulty = difficulty, skillType = DIFFICULTY_TOKENS[difficulty],
        skillUps = r.numSkillUps,
        craftable = r.craftable, available = r.numAvailable, categoryId = r.categoryID,
        itemId = itemId, made = made, reagents = reagents,
      }
    end
  end
  return {
    professionId = base.professionID,
    professionName = base.professionName,
    skillLevel = base.skillLevel, maxSkillLevel = base.maxSkillLevel,
    capturedAt = ns.now(),
    api = "C_TradeSkillUI",
    recipes = recipes,
  }
end

-- skillLineId d'un métier à partir de son nom (domaines professions déjà capturés)
local function skillLineIdByName(name)
  local c = ns.charDB and ns.charDB()
  local p = c and c.professions
  if type(p) ~= "table" then return nil end
  for _, x in ipairs(p.professions or {}) do if x.name == name then return x.skillLineId end end
  for _, x in ipairs(p.skills or {}) do if x.name == name then return x.skillId end end
  return nil
end

-- API classique (1.12 à 3.x). Les catégories repliées par le joueur ne sont pas lues :
-- on ne touche pas à l'état de sa fenêtre.
local function collectClassic()
  if not ns.api("GetNumTradeSkills") then return nil end
  if get("IsTradeSkillLinked") then return nil end
  local name, rank, maxRank = get("GetTradeSkillLine")
  if type(name) ~= "string" or name == "" or name == "UNKNOWN" then return nil end
  local n = get("GetNumTradeSkills") or 0
  if n <= 0 then return nil end
  local recipes = {}
  local category
  for i = 1, n do
    local rname, skillType, numAvailable = get("GetTradeSkillInfo", i)
    if skillType == "header" or skillType == "subheader" then
      category = rname
    elseif rname then
      local spellId
      local rlink = get("GetTradeSkillRecipeLink", i)
      if type(rlink) == "string" then spellId = tonumber(rlink:match("enchant:(%d+)") or rlink:match("spell:(%d+)")) end
      local reagents = {}
      for r = 1, (get("GetTradeSkillNumReagents", i) or 0) do
        local reagentName, _, count = get("GetTradeSkillReagentInfo", i, r)
        local rid = ns.itemIdFromLink(get("GetTradeSkillReagentItemLink", i, r))
        if rid or reagentName then reagents[#reagents + 1] = { itemId = rid, count = count, name = reagentName } end
      end
      local minMade, maxMade = get("GetTradeSkillNumMade", i)
      recipes[#recipes + 1] = {
        id = spellId, spellId = spellId, name = rname, learned = true,
        difficulty = TOKEN_DIFFICULTY[skillType], skillType = TOKEN_DIFFICULTY[skillType] and skillType or nil,
        available = numAvailable, craftable = (type(numAvailable) == "number" and numAvailable > 0) or nil,
        category = category,
        itemId = ns.itemIdFromLink(get("GetTradeSkillItemLink", i)),
        made = type(minMade) == "number" and { min = minMade, max = maxMade or minMade } or nil,
        reagents = reagentList(reagents),
      }
    end
  end
  if #recipes == 0 then return nil end
  return {
    professionId = skillLineIdByName(name),
    professionName = name,
    skillLevel = rank, maxSkillLevel = maxRank,
    capturedAt = ns.now(),
    api = "classic",
    recipes = recipes,
  }
end
ns.CollectClassicRecipes = collectClassic

ns.RegisterDomain("recipes", {
  label = "Recettes",
  login = false,
  events = { TRADE_SKILL_SHOW = true, TRADE_SKILL_LIST_UPDATE = true, TRADE_SKILL_UPDATE = true,
             NEW_RECIPE_LEARNED = true },
  collect = function(_, previous)
    local entry
    if ns.api("C_TradeSkillUI.GetAllRecipeIDs") then entry = collectModern(previous) end
    if not entry then entry = collectClassic() end
    if not entry then return nil end
    local out = previous or {}
    -- Clé = nom du métier (traduit, conservé pour compatibilité). Si la langue du client
    -- a changé, on retire l'ancienne entrée du même métier (même professionId).
    for k, v in pairs(out) do
      if k ~= entry.professionName and type(v) == "table" and entry.professionId
         and v.professionId == entry.professionId then
        out[k] = nil
      end
    end
    out[entry.professionName] = entry
    return out
  end,
})
