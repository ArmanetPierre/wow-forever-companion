-- ForeverScribe : identité, réglages Forever, progression, position
local ADDON, ns = ...
ns = ns or _G.ForeverScribeNS
local get, round = ns.get, ns.round

-- Ruleset : 1) Hardcore actif ? 2) suffixe du nom de royaume 3) inconnu
local SUFFIXES = {
  { pattern = "rppvp$", value = "RP-PvP" },
  { pattern = "pvp$", value = "PvP" },
  { pattern = "rp$", value = "RP" },
  { pattern = "pve$", value = "Normal" },
  { pattern = "normal$", value = "Normal" },
  { pattern = "hardcore$", value = "Hardcore" },
  { pattern = "hc$", value = "Hardcore" },
}

function ns.DetectRuleset(realmName, hardcore)
  if hardcore then return "Hardcore", "C_GameRules.IsHardcoreActive" end
  if type(realmName) == "string" then
    local compact = realmName:lower():gsub("[%s%-_]", "")
    for _, s in ipairs(SUFFIXES) do
      if compact:find(s.pattern) then return s.value, "GetRealmName" end
    end
  end
  return "inconnu", nil
end

ns.RegisterDomain("identity", {
  label = "Identité",
  logout = true,
  events = { PLAYER_GUILD_UPDATE = true, PLAYER_LEVEL_UP = true, NEUTRAL_FACTION_SELECT_RESULT = true },
  collect = function()
    local name, suffix = get("UnitName", "player")
    local race, raceFile, raceId = get("UnitRace", "player")
    local class, classFile, classId = get("UnitClass", "player")
    local faction, factionLocalized = get("UnitFactionGroup", "player")
    local realm = get("GetRealmName")
    local hardcore = get("C_GameRules.IsHardcoreActive")
    local ruleset, rulesetSource = ns.DetectRuleset(realm, hardcore)
    local guildName, guildRank, guildRankIndex = get("GetGuildInfo", "player")
    local sex = get("UnitSex", "player")
    return {
      guid = get("UnitGUID", "player"),
      name = name,
      suffix = suffix,
      realm = realm,
      realmNormalized = get("GetNormalizedRealmName"),
      realmId = get("GetRealmID"),
      region = get("GetCurrentRegionName"),
      regionId = get("GetCurrentRegion"),
      ruleset = ruleset,
      rulesetSource = rulesetSource,
      hardcore = hardcore and true or false,
      gameMode = get("C_GameRules.GetActiveGameMode"),
      warMode = get("C_PvP.IsWarModeActive") and true or false,
      race = race, raceFile = raceFile, raceId = raceId,
      class = class, classFile = classFile, classId = classId,
      sex = (sex == 2 and "male") or (sex == 3 and "female") or "unknown",
      faction = faction, factionLocalized = factionLocalized,
      level = get("UnitLevel", "player"),
      guild = guildName and { name = guildName, rank = guildRank, rankIndex = guildRankIndex } or nil,
      expansionLevel = get("GetAccountExpansionLevel"),
    }
  end,
})

-- Réglages propres à Forever (préréglage d'expérience, self-found, rulesets autorisés)
ns.RegisterDomain("forever", {
  label = "Réglages Forever",
  collect = function()
    local out = {
      experiencePreset = ns.plain(get("C_GameRules.GetForeverExperiencePreset"), 3),
      selfFoundAllowed = get("C_GameRules.IsSelfFoundAllowed"),
      gameModeDisplay = ns.plain(get("C_GameRules.GetCurrentGameModeDisplayInfo"), 3),
      gameModeRecordId = get("C_GameRules.GetCurrentGameModeRecordID"),
      isStandard = get("C_GameRules.IsStandard"),
      allowedRolesets = ns.plain(get("C_Roleset.GetActiveAllowedRolesets"), 3),
      blockedRolesets = ns.plain(get("C_Roleset.GetActiveBlockedRolesets"), 3),
    }
    return out
  end,
})

-- Temps de jeu : demandé une fois à la connexion, sans afficher le message dans le chat
local function hookTimePlayed()
  local function wrap(tbl, key)
    if type(tbl) ~= "table" or type(tbl[key]) ~= "function" then return end
    local orig = tbl[key]
    tbl[key] = function(...)
      if ns.silencePlayed then
        ns.silencePlayed = false
        return
      end
      return orig(...)
    end
  end
  wrap(_G, "ChatFrame_DisplayTimePlayed")
  wrap(_G.ChatFrameUtil, "DisplayTimePlayed")
end

local playedFrame = CreateFrame("Frame")
playedFrame:RegisterEvent("PLAYER_LOGIN")
playedFrame:RegisterEvent("TIME_PLAYED_MSG")
playedFrame:SetScript("OnEvent", function(_, event, total, atLevel)
  if event == "PLAYER_LOGIN" then
    hookTimePlayed()
    local after = _G.C_Timer and _G.C_Timer.After
    local function ask()
      ns.silencePlayed = true
      if not ns.call("RequestTimePlayed") then ns.silencePlayed = false end
      -- sécurité : ne jamais masquer un /played tapé plus tard par le joueur
      if after then after(10, function() ns.silencePlayed = false end) end
    end
    if after then after(6, ask) else ask() end
  elseif event == "TIME_PLAYED_MSG" then
    ns.timePlayed = { total = total, level = atLevel, at = ns.now() }
    ns.Mark("progression")
  end
end)

ns.RegisterDomain("progression", {
  label = "Progression",
  logout = true,
  events = {
    PLAYER_XP_UPDATE = true, PLAYER_LEVEL_UP = true, UPDATE_EXHAUSTION = true,
    PLAYER_UPDATE_RESTING = true,
  },
  collect = function(_, previous)
    local restId, restName, restMult = get("GetRestState")
    local tp = ns.timePlayed or (previous and previous.timePlayed) or nil
    return {
      level = get("UnitLevel", "player"),
      maxLevel = get("GetMaxPlayerLevel"),
      xp = get("UnitXP", "player"),
      xpMax = get("UnitXPMax", "player"),
      xpRested = get("GetXPExhaustion") or 0,
      restState = { id = restId, name = restName, multiplier = restMult },
      isResting = get("IsResting") and true or false,
      xpDisabled = get("IsXPUserDisabled") and true or false,
      timePlayed = tp,
    }
  end,
})

ns.RegisterDomain("position", {
  label = "Position",
  logout = true,
  events = {
    ZONE_CHANGED = true, ZONE_CHANGED_NEW_AREA = true, ZONE_CHANGED_INDOORS = true,
    PLAYER_ENTERING_WORLD = true, HEARTHSTONE_BOUND = true,
  },
  collect = function()
    local mapId = get("C_Map.GetBestMapForUnit", "player")
    local out = {
      mapId = mapId,
      zone = get("GetZoneText"),
      realZone = get("GetRealZoneText"),
      subZone = get("GetSubZoneText"),
      bind = get("GetBindLocation"),
    }
    if mapId then
      local info = get("C_Map.GetMapInfo", mapId)
      if type(info) == "table" then
        out.mapName = info.name
        out.mapType = info.mapType
        out.parentMapId = info.parentMapID
        if info.parentMapID then
          local parent = get("C_Map.GetMapInfo", info.parentMapID)
          out.parentMapName = type(parent) == "table" and parent.name or nil
        end
      end
      local pos = get("C_Map.GetPlayerMapPosition", mapId, "player")
      if pos and pos.GetXY then
        local ok, x, y = pcall(pos.GetXY, pos)
        if ok and x and y then
          out.x = round(x * 100, 1)
          out.y = round(y * 100, 1)
        end
      end
    end
    local iName, iType, difficultyId, difficultyName = get("GetInstanceInfo")
    out.instance = {
      name = iName, type = iType, difficultyId = difficultyId, difficultyName = difficultyName,
      inInstance = (iType ~= nil and iType ~= "none"),
    }
    return out
  end,
})
