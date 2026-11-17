-- Contrat minimal du schéma v1 (voir docs/schema.md).
-- Chaque entrée : chemin pointé -> type attendu. « ? » en fin de type = facultatif.
return {
  account = {
    ["schemaVersion"] = "number",
    ["addonVersion"] = "string",
    ["characters"] = "table",
    ["schemaMinor"] = "number",
    ["settings.showButton"] = "boolean?", ["settings.buttonAngle"] = "number?",
  },
  indexEntry = {
    ["name"] = "string", ["suffix"] = "string?", ["realm"] = "string", ["realmId"] = "number",
    ["region"] = "string", ["ruleset"] = "string", ["race"] = "string", ["class"] = "string",
    ["classFile"] = "string", ["faction"] = "string", ["level"] = "number", ["zone"] = "string?",
    ["lastCapture"] = "number", ["lastCaptureISO"] = "string",
    ["raceFile"] = "string?", ["locale"] = "string?", -- 1.3
  },
  character = {
    ["meta.schemaVersion"] = "number", ["meta.addonVersion"] = "string", ["meta.guid"] = "string",
    ["meta.locale"] = "string", ["meta.capturedAt"] = "number", ["meta.capturedAtISO"] = "string",
    ["meta.build.version"] = "string", ["meta.build.interface"] = "number",
    ["meta.domainsUpdatedAt"] = "table", ["meta.errors"] = "table", ["meta.missing"] = "table",
    ["meta.callErrors"] = "table",
    ["meta.schemaMinor"] = "number",
    ["meta.lastSyncRequestAt"] = "number?", ["meta.lastSyncReason"] = "string?", ["meta.writtenAt"] = "number?",

    ["identity.guid"] = "string", ["identity.name"] = "string", ["identity.realm"] = "string",
    ["identity.realmId"] = "number", ["identity.region"] = "string", ["identity.ruleset"] = "string",
    ["identity.race"] = "string", ["identity.raceFile"] = "string", ["identity.class"] = "string",
    ["identity.classFile"] = "string", ["identity.sex"] = "string", ["identity.faction"] = "string",
    ["identity.level"] = "number", ["identity.hardcore"] = "boolean", ["identity.guild"] = "table?",

    ["forever"] = "table",

    ["progression.level"] = "number", ["progression.maxLevel"] = "number", ["progression.xp"] = "number",
    ["progression.xpMax"] = "number", ["progression.xpRested"] = "number", ["progression.restState"] = "table",
    ["progression.timePlayed.total"] = "number", ["progression.timePlayed.level"] = "number",

    ["position.mapId"] = "number", ["position.zone"] = "string", ["position.subZone"] = "string",
    ["position.x"] = "number", ["position.y"] = "number", ["position.bind"] = "string",
    ["position.instance.inInstance"] = "boolean",

    ["stats.primary.agility.effective"] = "number", ["stats.health"] = "number",
    ["stats.melee.attackPower"] = "number", ["stats.melee.crit"] = "number",
    ["stats.ranged.attackPower"] = "number", ["stats.ranged.dps"] = "number", ["stats.ranged.crit"] = "number",
    ["stats.ranged.usesAmmo"] = "boolean", ["stats.armor.effective"] = "number",
    ["stats.resistances"] = "table", ["stats.itemLevel.equipped"] = "number",

    ["equipment.slots"] = "table", ["equipment.slots.RangedSlot.itemId"] = "number",
    ["equipment.slots.RangedSlot.name"] = "string", ["equipment.slots.RangedSlot.itemLevel"] = "number",
    ["equipment.slots.RangedSlot.dps"] = "number", ["equipment.slots.RangedSlot.stats"] = "table",
    ["equipment.slots.RangedSlot.durability.current"] = "number", ["equipment.slots.RangedSlot.tooltip"] = "table",
    ["equipment.repairCost"] = "number",

    ["talents.specId"] = "number", ["talents.specName"] = "string", ["talents.role"] = "string",
    ["talents.configId"] = "number", ["talents.treeId"] = "number", ["talents.nodes"] = "table",
    ["talents.nodeCount"] = "number", ["talents.unspent"] = "number?", ["talents.spent"] = "number?",

    ["spells.lines"] = "table",

    ["professions.professions"] = "table", ["professions.skills"] = "table",

    ["quests.count"] = "number", ["quests.list"] = "table",
    ["questsCompleted.count"] = "number", ["questsCompleted.ids"] = "table",

    ["pet.active"] = "boolean", ["pet.current.name"] = "string", ["pet.current.level"] = "number",
    ["pet.current.happiness.level"] = "number", ["pet.current.loyalty"] = "string",
    ["pet.current.trainingPoints.available"] = "number", ["pet.stable.active"] = "table",

    ["bags.containers"] = "table", ["bags.totalSlots"] = "number", ["bags.freeSlots"] = "number",
    ["bags.ammo.total"] = "number", ["bags.ammo.byId"] = "table", -- byId : 1.3

    ["money.copper"] = "number", ["money.text"] = "string",
    ["reputations.list"] = "table", ["currencies.list"] = "table",
    ["group.inGroup"] = "boolean", ["group.members"] = "table",
    ["buffs.list"] = "table",
    ["collections.mountsOwned"] = "number", ["collections.achievementsCompleted"] = "number",
  },
  -- domaines qui n'apparaissent qu'après ouverture d'une fenêtre
  onDemand = {
    ["recipes"] = "table",
    ["bank.containers"] = "table", ["bank.capturedAt"] = "number",
  },
}
