-- ForeverScribe : textes affichés (chat, aide, infobulle, raccourcis).
-- Anglais par défaut, français pour frFR. Toute autre langue retombe sur l'anglais.
-- Seuls les messages sont traduits : les données écrites pour le MCP gardent des
-- clés et jetons non traduits (voir docs/schema.md, « Langue du client »).
local ADDON, ns = ...
ns = ns or {}
_G.ForeverScribeNS = ns

local enUS = {
  -- chat : connexion, /scribe
  NO_DATA = "no data",
  QUESTS_N = "%d quests",
  READY = "ready (%d domains captured%s). Sync: %s. /scribe help",
  N_ERRORS = ", %d with errors",
  SYNC_KEY_OR_CMD = "%s or /sync",
  SYNC_NO_KEY = "/sync (or /scribe key to set a key)",
  NOT_INITIALIZED = "not initialized yet.",
  STATUS_HEADER = "status per domain:",
  STATUS_ERROR = "ERROR",
  STATUS_OK_AGO = "OK %s ago",
  STATUS_NEVER = "never captured",
  STATUS_OPEN_PROFESSION = " (open the profession window)",
  STATUS_OPEN_BANK = " (open your bank)",
  STATUS_FAILED_CALLS = "%d failed call(s)",
  STATUS_MISSING_FUNCS = "%d missing function(s)",
  LAST_SYNC = "Last sync: %s ago (%s).",
  QUEST_MEMORY = "Quest memory (account): %d quests, %d NPCs, %d objects.",
  STATUS_FOOTER = "Sync for Claude: /sync, your key or the minimap button.",
  HELP_HEADER = "commands:",
  HELP_SCRIBE = "  /scribe         full capture + summary",
  HELP_STATUS = "  /scribe status  state of each domain (OK, error, age)",
  HELP_HELP = "  /scribe help    this help",
  HELP_SYNC_HEADER = "Sync for Claude (capture + write to disk):",
  HELP_SYNC = "  /sync or /scribe sync   sync now",
  HELP_KEY = "  key: %s   (/scribe key [CTRL-SHIFT-S] to assign it)",
  HELP_NONE = "none",
  HELP_BUTTON = "  /scribe button  show / hide the minimap button",
  HELP_AUTO = "Data is also written automatically when you log out or quit the game.",
  IN_COMBAT_CAPTURE = "in combat: capture will run when combat ends.",
  CAPTURED_SUMMARY = "%d domains captured%s. /sync to send it to Claude.",
  CAPTURED_ERRORS = ", %d with errors (/scribe status)",

  -- synchro
  BINDING_SYNC = "Sync for Claude",
  SYNC_IN_COMBAT = "in combat: sync not possible. I'll remind you when combat ends.",
  SYNC_NOT_READY = "not ready yet, try again in a few seconds.",
  SYNC_RUNNING = "syncing for Claude…",
  SYNC_NO_RELOAD = "reload unavailable: type /reload.",
  SYNC_RELOAD_REFUSED = "reload refused by the game (%s): type /reload.",
  KEY_IN_COMBAT = "not possible in combat.",
  KEY_ALREADY_SYNC = "%s already syncs for Claude.",
  KEY_TAKEN = "%s is already used (%s). Pick another one (e.g. /scribe key ALT-F12) or use Options → Keybindings → AddOns → ForeverScribe.",
  KEY_REFUSED = "the game refused key %s. Use Options → Keybindings → AddOns → ForeverScribe.",
  KEY_SET = "key %s = Sync for Claude.",
  TIP_TITLE = "Sync for Claude",
  TIP_LAST_DATA = "Latest data: %s",
  TIP_AGO = "%s ago",
  TIP_NONE = "none",
  TIP_KEY = "Shortcut: %s",
  TIP_NO_KEY = "Shortcut: none (/scribe key)",
  TIP_HINT = "Click: sync · Drag: move",
  BUTTON_SHOWN = "minimap button shown.",
  BUTTON_HIDDEN = "minimap button hidden (/scribe button to show it again).",
  COMBAT_OVER = "combat over: %stype /sync or click the button to sync.",
  COMBAT_OVER_KEY = "press %s, ",

  -- durées et argent
  AGE_NEVER = "never",
  AGE_S = "%d s", AGE_MIN = "%d min", AGE_H = "%d h", AGE_D = "%d d",
  MONEY = "%dg %ds %dc",

  -- libellés des domaines (/scribe status)
  ["domain.identity"] = "Identity",
  ["domain.forever"] = "Forever settings",
  ["domain.progression"] = "Progression",
  ["domain.position"] = "Position",
  ["domain.stats"] = "Stats",
  ["domain.equipment"] = "Equipment",
  ["domain.talents"] = "Talents",
  ["domain.spells"] = "Spells",
  ["domain.quests"] = "Quests",
  ["domain.questsCompleted"] = "Completed quests",
  ["domain.professions"] = "Professions",
  ["domain.recipes"] = "Recipes",
  ["domain.bags"] = "Bags",
  ["domain.bank"] = "Bank",
  ["domain.money"] = "Money",
  ["domain.pet"] = "Pet",
  ["domain.reputations"] = "Reputations",
  ["domain.currencies"] = "Currencies",
  ["domain.group"] = "Group",
  ["domain.buffs"] = "Active effects",
  ["domain.collections"] = "Collections",
}

local frFR = {
  NO_DATA = "aucune donnée",
  QUESTS_N = "%d quêtes",
  READY = "prêt (%d domaines capturés%s). Synchro : %s. /scribe aide",
  N_ERRORS = ", %d en erreur",
  SYNC_KEY_OR_CMD = "%s ou /sync",
  SYNC_NO_KEY = "/sync (ou /scribe touche pour une touche)",
  NOT_INITIALIZED = "pas encore initialisé.",
  STATUS_HEADER = "état par domaine :",
  STATUS_ERROR = "ERREUR",
  STATUS_OK_AGO = "OK il y a %s",
  STATUS_NEVER = "jamais capturé",
  STATUS_OPEN_PROFESSION = " (ouvre la fenêtre du métier)",
  STATUS_OPEN_BANK = " (ouvre ta banque)",
  STATUS_FAILED_CALLS = "%d appel(s) en erreur",
  STATUS_MISSING_FUNCS = "%d fonction(s) absente(s)",
  LAST_SYNC = "Dernière synchro : il y a %s (%s).",
  QUEST_MEMORY = "Mémoire des quêtes (compte) : %d quêtes, %d PNJ, %d objets.",
  STATUS_FOOTER = "Synchronise pour Claude : /sync, ta touche ou le bouton de la minicarte.",
  HELP_HEADER = "commandes :",
  HELP_SCRIBE = "  /scribe         capture complète + résumé",
  HELP_STATUS = "  /scribe statut  état de chaque domaine (OK, erreur, âge)",
  HELP_HELP = "  /scribe aide    cette aide",
  HELP_SYNC_HEADER = "Synchroniser pour Claude (capture + écriture sur le disque) :",
  HELP_SYNC = "  /sync ou /scribe sync   synchroniser maintenant",
  HELP_KEY = "  touche : %s   (/scribe touche [CTRL-SHIFT-S] pour l'attribuer)",
  HELP_NONE = "aucune",
  HELP_BUTTON = "  /scribe bouton  afficher / masquer le bouton de la minicarte",
  HELP_AUTO = "Les données s'écrivent aussi toutes seules à la déconnexion et en quittant le jeu.",
  IN_COMBAT_CAPTURE = "en combat : la capture se fera à la sortie du combat.",
  CAPTURED_SUMMARY = "%d domaines capturés%s. /sync pour l'envoyer à Claude.",
  CAPTURED_ERRORS = ", %d en erreur (/scribe statut)",

  BINDING_SYNC = "Synchroniser pour Claude",
  SYNC_IN_COMBAT = "en combat : synchro impossible. Je te préviens à la sortie du combat.",
  SYNC_NOT_READY = "pas encore prêt, réessaie dans quelques secondes.",
  SYNC_RUNNING = "synchro pour Claude…",
  SYNC_NO_RELOAD = "rechargement indisponible : tape /reload.",
  SYNC_RELOAD_REFUSED = "rechargement refusé par le jeu (%s) : tape /reload.",
  KEY_IN_COMBAT = "impossible en combat.",
  KEY_ALREADY_SYNC = "%s synchronise déjà pour Claude.",
  KEY_TAKEN = "%s est déjà utilisée (%s). Choisis-en une autre (ex. /scribe touche ALT-F12) ou passe par Options → Raccourcis → AddOns → ForeverScribe.",
  KEY_REFUSED = "le jeu a refusé la touche %s. Passe par Options → Raccourcis → AddOns → ForeverScribe.",
  KEY_SET = "touche %s = Synchroniser pour Claude.",
  TIP_TITLE = "Synchroniser pour Claude",
  TIP_LAST_DATA = "Dernières données : %s",
  TIP_AGO = "il y a %s",
  TIP_NONE = "aucune",
  TIP_KEY = "Raccourci : %s",
  TIP_NO_KEY = "Raccourci : aucun (/scribe touche)",
  TIP_HINT = "Clic : synchroniser · Glisser : déplacer",
  BUTTON_SHOWN = "bouton de la minicarte affiché.",
  BUTTON_HIDDEN = "bouton de la minicarte masqué (/scribe bouton pour le réafficher).",
  COMBAT_OVER = "combat terminé : %stape /sync ou clique sur le bouton pour synchroniser.",
  COMBAT_OVER_KEY = "appuie sur %s, ",

  AGE_NEVER = "jamais",
  AGE_S = "%d s", AGE_MIN = "%d min", AGE_H = "%d h", AGE_D = "%d j",
  MONEY = "%d po %d pa %d pc",

  ["domain.identity"] = "Identité",
  ["domain.forever"] = "Réglages Forever",
  ["domain.progression"] = "Progression",
  ["domain.position"] = "Position",
  ["domain.stats"] = "Stats",
  ["domain.equipment"] = "Équipement",
  ["domain.talents"] = "Talents",
  ["domain.spells"] = "Sorts",
  ["domain.quests"] = "Quêtes",
  ["domain.questsCompleted"] = "Quêtes terminées",
  ["domain.professions"] = "Métiers",
  ["domain.recipes"] = "Recettes",
  ["domain.bags"] = "Sacs",
  ["domain.bank"] = "Banque",
  ["domain.money"] = "Argent",
  ["domain.pet"] = "Familier",
  ["domain.reputations"] = "Réputations",
  ["domain.currencies"] = "Monnaies",
  ["domain.group"] = "Groupe",
  ["domain.buffs"] = "Effets actifs",
  ["domain.collections"] = "Collections",
}

local LOCALES = { frFR = frFR }

-- Choisit la table de la langue du client (relu par les tests pour changer de langue).
function ns.SetLocale(locale)
  local chosen = LOCALES[locale] or {}
  ns.L = setmetatable({}, {
    __index = function(_, k)
      local v = chosen[k]
      if v == nil then v = enUS[k] end
      if v == nil then v = k end
      return v
    end,
  })
  ns.uiLocale = LOCALES[locale] and locale or "enUS"
  return ns.L
end

local getLocale = _G.GetLocale
ns.SetLocale(type(getLocale) == "function" and getLocale() or "enUS")
