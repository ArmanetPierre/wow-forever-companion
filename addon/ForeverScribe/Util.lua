-- ForeverScribe : utilitaires partagés (aucune dépendance au reste de l'addon)
local ADDON, ns = ...
ns = ns or {}
_G.ForeverScribeNS = ns -- accès pour le débogage (/dump ForeverScribeNS)

ns.ADDON = ADDON or "ForeverScribe"
ns.VERSION = "1.5.0"
ns.SCHEMA_VERSION = 1   -- change seulement si le format devient incompatible
ns.SCHEMA_MINOR = 5     -- ajouts rétrocompatibles (1.1 : synchro ; 1.2 : récompenses de quête ;
                        -- 1.3 : client anglais, clés non traduites en plus des libellés ;
                        -- 1.4 : mémoire des quêtes vues, au niveau du compte ;
                        -- 1.5 : prix de l'hôtel des ventes, couleur et composants des recettes)

-- Résout "C_Item.GetItemInfo" ou "UnitLevel" dans _G. Renvoie la fonction ou nil.
function ns.api(path)
  local cur = _G
  for part in string.gmatch(path, "[^%.]+") do
    if type(cur) ~= "table" then return nil end
    cur = cur[part]
  end
  if type(cur) == "function" then return cur end
  return nil
end

-- Appel protégé. Renvoie ok, ...retours. Si la fonction manque : false, "absent".
-- Les fonctions absentes sont notées dans ns.currentMissing (domaine en cours).
function ns.call(path, ...)
  local fn = ns.api(path)
  if not fn then
    if ns.currentMissing then ns.currentMissing[path] = true end
    return false, "absent"
  end
  return ns.recordFailure(path, pcall(fn, ...))
end

-- Note les fonctions présentes mais en erreur (domaine en cours), sans casser l'appel.
function ns.recordFailure(path, ok, ...)
  if not ok and ns.currentFailed and not ns.currentFailed[path] then
    ns.currentFailed[path] = tostring((...)):sub(1, 160)
  end
  return ok, ...
end

-- Comme ns.call mais ne renvoie que les valeurs (nil si échec).
local function dropStatus(ok, ...)
  if not ok then return nil end
  return ...
end
function ns.get(path, ...)
  return dropStatus(ns.call(path, ...))
end

function ns.round(v, decimals)
  if type(v) ~= "number" then return v end
  local m = 10 ^ (decimals or 0)
  return math.floor(v * m + 0.5) / m
end

-- Copie d'une table de l'API en ne gardant que les valeurs simples
-- (évite d'écrire des fonctions/userdata dans les SavedVariables).
function ns.plain(t, depth)
  depth = depth or 2
  if type(t) ~= "table" then
    local ty = type(t)
    if ty == "string" or ty == "number" or ty == "boolean" then return t end
    return nil
  end
  if depth <= 0 then return nil end
  local out = {}
  for k, v in pairs(t) do
    local kt = type(k)
    if kt == "string" or kt == "number" then
      local pv = ns.plain(v, depth - 1)
      if pv ~= nil then out[k] = pv end
    end
  end
  return out
end

-- Liste à partir d'une table indexée de l'API (gère les trous).
function ns.list(t)
  local out = {}
  if type(t) ~= "table" then return out end
  for _, v in ipairs(t) do out[#out + 1] = v end
  return out
end

function ns.now()
  return time()
end

function ns.iso(t)
  return date("!%Y-%m-%dT%H:%M:%SZ", t or time())
end

function ns.itemIdFromLink(link)
  if type(link) ~= "string" then return nil end
  local id = link:match("item:(%d+)")
  return id and tonumber(id) or nil
end

function ns.nameFromLink(link)
  if type(link) ~= "string" then return nil end
  return link:match("%[(.-)%]")
end

function ns.moneyText(copper)
  if type(copper) ~= "number" then return nil end
  local g = math.floor(copper / 10000)
  local s = math.floor((copper % 10000) / 100)
  local c = copper % 100
  return string.format(ns.L and ns.L.MONEY or "%dg %ds %dc", g, s, c)
end

function ns.ageText(seconds)
  local L = ns.L or {}
  if type(seconds) ~= "number" then return L.AGE_NEVER or "never" end
  if seconds < 60 then return string.format(L.AGE_S or "%d s", seconds) end
  if seconds < 3600 then return string.format(L.AGE_MIN or "%d min", math.floor(seconds / 60)) end
  if seconds < 86400 then return string.format(L.AGE_H or "%d h", math.floor(seconds / 3600)) end
  return string.format(L.AGE_D or "%d d", math.floor(seconds / 86400))
end

function ns.print(msg)
  -- typographie : « : » espacé en français, « : » collé en anglais
  local PREFIX = "|cff7fbfffForeverScribe|r" .. (ns.uiLocale == "frFR" and " : " or ": ")
  local frame = _G.DEFAULT_CHAT_FRAME
  if frame and frame.AddMessage then
    frame:AddMessage(PREFIX .. tostring(msg))
  else
    print(PREFIX .. tostring(msg))
  end
end
