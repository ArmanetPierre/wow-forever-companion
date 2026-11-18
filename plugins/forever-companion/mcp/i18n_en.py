"""English catalog: French source template -> English template (see i18n.py).

Keys must match the French literal passed to T() exactly; tests/test_i18n.py checks that every
T() literal of the server has an entry here and that the {placeholders} are the same.
"""

EN = {
    "{d} j {h} h":
        "{d} d {h} h",
    " · foyer : {bind}":
        " · hearth: {bind}",
    "il y a moins de 2 min":
        "less than 2 min ago",
    "il y a {m} min":
        "{m} min ago",
    "il y a {n} jours":
        "{n} days ago",
    "il y a 1 jour":
        "1 day ago",
    "jamais capturé":
        "never captured",
    "zone inconnue":
        "unknown zone",
    " · capturé {age}":
        " · captured {age}",
    " · jamais capturé":
        " · never captured",
    " (Ctrl+Maj+S en jeu pour actualiser)":
        " (Ctrl+Shift+S in game to refresh)",
    " · en instance : {name} {diff}":
        " · in instance: {name} {diff}",
    "- Caractéristiques : For {str} · Agi {agi} · End {sta} · Int {int} · Esp {spi}":
        "- Attributes: Str {str} · Agi {agi} · Sta {sta} · Int {int} · Spi {spi}",
    "- PV {hp} · {power} {pmax} · armure {armor} · ilvl moyen {ilvl}":
        "- HP {hp} · {power} {pmax} · armor {armor} · average ilvl {ilvl}",
    "| Emplacement | Objet | ilvl | Stats | Durabilité |":
        "| Slot | Item | ilvl | Stats | Durability |",
    "- Spé : {spec} ({role}) · {spent} points dépensés, {free} libre(s) · {n} spé(s) disponible(s)":
        "- Spec: {spec} ({role}) · {spent} points spent, {free} free · {n} spec(s) available",
    "| Métier | Type | Niveau |":
        "| Profession | Type | Level |",
    "- Argent : {money}":
        "- Money: {money}",
    " ✔ à rendre":
        " ✔ ready to turn in",
    "- **{title}** (niv. {level}, {color})":
        "- **{title}** (lvl {level}, {color})",
    "| Faction | Groupe | Palier | Progression |":
        "| Faction | Group | Standing | Progress |",
    "> Généré automatiquement depuis l'addon ForeverScribe · capture du {time} (heure de l'ordinateur) · compte {account}.":
        "> Generated automatically from the ForeverScribe addon · capture of {time} (computer time) · account {account}.",
    "> Ne modifie pas cette section : elle est réécrite à chaque synchro. Tes notes vont en bas.":
        "> Do not edit this section: it is rewritten at every sync. Your notes go below.",
    "## Identité":
        "## Identity",
    "## Progression":
        "## Progression",
    "## Position":
        "## Position",
    "## Combat":
        "## Combat",
    "## Équipement":
        "## Equipment",
    "## Talents":
        "## Talents",
    # arbre de talents (talents_tree.py, outil talents arbre:true)
    "(après {list})":
        "(after {list})",
    "_Arbre de talents : la base locale du jeu n'est pas construite._":
        "_Talent tree: the local game database is not built yet._",
    "_Arbre de talents absent de la base locale (base trop ancienne) : reconstruis-la (`{cmd} --force`)._":
        "_No talent tree in the local game database (database too old): rebuild it (`{cmd} --force`)._",
    "_Arbre de talents introuvable pour cette classe dans la base locale._":
        "_No talent tree for this class in the local game database._",
    "Arbre de talents":
        "Talent tree",
    "{spent} points dépensés, {free} libre(s).":
        "{spent} points spent, {free} free.",
    "Rang actuel/max · * disponible maintenant · x bloqué (points de la rangée ou prérequis).":
        "Current rank/max · * available now · x locked (row points or prerequisite).",
    "Branche {n}":
        "Branch {n}",
    "0 pt · ouvert : {list}":
        "0 pts · open: {list}",
    "{n} pts":
        "{n} pts",
    "… {n} rangée(s) de plus":
        "… {n} more row(s)",
    "Retirés":
        "Removed",
    "Rangée {r} ({req} pts, il en manque {m})":
        "Row {r} ({req} pts, {m} missing)",
    "Rangée {r} ({req} pts)":
        "Row {r} ({req} pts)",
    "Rangée {r}":
        "Row {r}",
    "Branches sans point résumées ; arbre:complet pour tout l'arbre.":
        "Branches without points are summarized; arbre:complet for the whole tree.",
    "Arbre complet (talents disponibles, bloqués, rangées) : arbre:true.":
        "Full tree (available and locked talents, rows): arbre:true.",
    "## Métiers":
        "## Professions",
    "## Familier":
        "## Pet",
    "## Sacs et argent":
        "## Bags and money",
    "## Quêtes":
        "## Quests",
    "## Réputations":
        "## Reputations",
    "date inconnue":
        "unknown date",
    "il y a {h} h {m:02d}":
        "{h} h {m:02d} min ago",
    "il y a {h} h":
        "{h} h ago",
    "{dom} : erreur ({msg})":
        "{dom}: error ({msg})",
    "- **{label}** · {race} {cls} niveau {level} · {faction} · {region} · ruleset {ruleset}":
        "- **{label}** · {race} {cls} level {level} · {faction} · {region} · ruleset {ruleset}",
    "- Guilde : {name} ({rank})":
        "- Guild: {name} ({rank})",
    "- Guilde : aucune":
        "- Guild: none",
    "- Spé : {spec} ({role}) · {spent} points de talent dépensés, {free} libre(s)":
        "- Spec: {spec} ({role}) · {spent} talent points spent, {free} free",
    "- Progression : jamais capturée":
        "- Progression: never captured",
    "- Niveau maximum ({level})":
        "- Max level ({level})",
    "- Temps de jeu : {total} ({level} à ce niveau)":
        "- Played time: {total} ({level} at this level)",
    "- Position : jamais capturée":
        "- Position: never captured",
    "- Stats : jamais capturées":
        "- Stats: never captured",
    "- Distance : PA {ap} ({base} + {pos}) · {min}–{max} toutes les {speed} s ({dps} DPS hors crit) · crit {crit}{pc}":
        "- Ranged: AP {ap} ({base} + {pos}) · {min}–{max} every {speed} s ({dps} DPS without crits) · crit {crit}{pc}",
    "- Mêlée : PA {ap} · {min}–{max} toutes les {speed} s ({dps} DPS) · crit {crit}{pc} · esquive {dodge}{pc} · parade {parry}{pc}":
        "- Melee: AP {ap} · {min}–{max} every {speed} s ({dps} DPS) · crit {crit}{pc} · dodge {dodge}{pc} · parry {parry}{pc}",
    "- Résistances : {list}":
        "- Resistances: {list}",
    "- Équipement : jamais capturé":
        "- Equipment: never captured",
    "objet {id}":
        "item {id}",
    "\nRéparation complète : {cost}.":
        "\nFull repair: {cost}.",
    "Durabilité faible : {slots}.":
        "Low durability: {slots}.",
    "- Talents : jamais capturés":
        "- Talents: never captured",
    "- Talents pris : {list}":
        "- Talents taken: {list}",
    "- Métiers : aucun capturé":
        "- Professions: none captured",
    "- Familier : jamais capturé":
        "- Pet: never captured",
    "actif":
        "active",
    "renvoyé (vu {age})":
        "dismissed (seen {age})",
    "- Pas de familier actif":
        "- No active pet",
    "- À l'écurie : {list}":
        "- In the stable: {list}",
    " ✘ échouée":
        " ✘ failed",
    " · {n} quêtes terminées au total":
        " · {n} quests completed in total",
    "À rendre ({n}) : {list}":
        "To turn in ({n}): {list}",
    "Aucune quête du journal ne correspond à « {zone} ».":
        "No quest in the log matches \"{zone}\".",
    "- Réputations : jamais capturées":
        "- Reputations: never captured",
    "- {name} : rang {level} ({xp}/{max})":
        "- {name}: rank {level} ({xp}/{max})",
    "- Sorts : jamais capturés":
        "- Spells: never captured",
    "Sacs":
        "Bags",
    "Banque":
        "Bank",
    " (capturée {age})":
        " (captured {age})",
    "## Données non lues par l'addon":
        "## Data the addon could not read",
    "{dom} : fonctions absentes ({fns})":
        "{dom}: missing functions ({fns})",
    "{dom} : {n} appel(s) en erreur":
        "{dom}: {n} call(s) failed",
    "\nRecettes : jamais capturées (ouvre la fenêtre du métier en jeu, puis Ctrl+Maj+S (ou /sync)).":
        "\nRecipes: never captured (open the profession window in game, then Ctrl+Shift+S (or /sync)).",
    "\n**{prof}** : {n} recettes connues (capturé {age}).":
        "\n**{prof}**: {n} known recipes (captured {age}).",
    "\nRecettes capturées pour : {list}.":
        "\nRecipes captured for: {list}.",
    "- XP familier : {xp} / {max} · points de dressage {free} libres sur {total}":
        "- Pet XP: {xp} / {max} · training points {free} free out of {total}",
    "- Mange : {list}":
        "- Eats: {list}",
    "- Techniques : {list}":
        "- Abilities: {list}",
    "- Sacs : {free} place(s) libre(s) sur {total}":
        "- Bags: {free} free slot(s) out of {total}",
    "Journal : {n}/{max} quêtes":
        "Quest log: {n}/{max} quests",
    "vide":
        "empty",
    "- {name} ({free}/{slots} libres) : {content}":
        "- {name} ({free}/{slots} free): {content}",
    " · au repos":
        " · resting",
    "Recettes qui font encore monter le métier : {list}":
        "Recipes that still raise the skill: {list}",
    "- {name} ({family}) niveau {level}, {status}":
        "- {name} ({family}) level {level}, {status}",
    " — presque pleins":
        " — almost full",
    "- Munitions : {n}":
        "- Ammo: {n}",
    " — **journal plein**, impossible d'en prendre d'autres":
        " — **quest log full**, you cannot take any more",
    "\nBanque : jamais capturée (ouvre ta banque en jeu, puis Ctrl+Maj+S (ou /sync)).":
        "\nBank: never captured (open your bank in game, then Ctrl+Shift+S (or /sync)).",
    "- XP : {xp} / {max} ({pct}) · reste {left}":
        "- XP: {xp} / {max} ({pct}) · {left} to go",
    " · {mood} ({pct}{pc} dégâts)":
        " · {mood} ({pct}{pc} damage)",
    "Autres":
        "Other",
    " [passif]":
        " [passive]",
    " · repos {n}":
        " · rested {n}",
    "Conteneur {id}":
        "Container {id}",
    "ressource":
        "resource",
    ", {n} faisables":
        ", {n} craftable",
    "armure":
        "armor",
    "arme":
        "weapon",
    "niveau requis {n}":
        "required level {n}",
    "le jeu l'indique inutilisable pour ce perso":
        "the game marks it as unusable for this character",
    "utilisable (indiqué par le jeu)":
        "usable (according to the game)",
    "niv. {n}":
        "lvl {n}",
    "objet":
        "item",
    "classe inconnue":
        "unknown class",
    "{kind} non portable par la classe [Classic]":
        "{kind} cannot be worn by this class [Classic]",
    "{kind} portable seulement au niveau {n} [Classic]":
        "{kind} wearable only from level {n} [Classic]",
    "{kind} non maîtrisée par la classe [Classic]":
        "{kind} not usable by this class [Classic]",
    "ce n'est pas un équipement":
        "not a piece of equipment",
    "classe de lanceur de sorts : Int/Esprit/Endurance comptés":
        "caster class: Int/Spirit/Stamina counted",
    "aucune stat":
        "no stats",
    "**{name}** (id {id}) — {quality}, niv. d'objet {ilvl}, niveau requis {req}":
        "**{name}** (id {id}) — {quality}, item level {ilvl}, required level {req}",
    "{min}-{max} dégâts, vitesse {speed}, {dps} DPS":
        "{min}-{max} damage, speed {speed}, {dps} DPS",
    "{n} armure":
        "{n} armor",
    "{badge} build {build}, base construite le {date} (langue du jeu : {locale}).":
        "{badge} build {build}, database built on {date} (game language: {locale}).",
    "{n} objet(s) :":
        "{n} item(s):",
    "- Origine des données : {origin} {badge}":
        "- Data origin: {origin} {badge}",
    "Améliorations possibles pour **{name}** ({cls}, niveau {level}) — objets de niveau requis {lmin} à {lmax}, qualité {quality} ou mieux :":
        "Possible upgrades for **{name}** ({cls}, level {level}) — items with required level {lmin} to {lmax}, quality {quality} or better:",
    "donjon":
        "dungeon",
    "**{name}** ({kind}, carte {map}) {badge}":
        "**{name}** ({kind}, map {map}) {badge}",
    "Aucun objet ne correspond à ces critères dans la base locale.":
        "No item matches these criteria in the local database.",
    "Objet introuvable dans la base locale (vérifie l'orthographe, ou cherche avec find_items).":
        "Item not found in the local database (check the spelling — names are in the game's language — or search with find_items).",
    "- Prix de vente au marchand : {price}":
        "- Vendor sell price: {price}",
    "- Réservé à certaines classes (masque {mask})":
        "- Restricted to some classes (mask {mask})",
    "- Sources :":
        "- Sources:",
    "- Source : non répertoriée dans la base (butin, quête ou marchand). Cherche dans la mémoire de recherche puis sur le web.":
        "- Source: not listed in the database (loot, quest or vendor). Search the research memory, then the web.",
    "- Fabriqué par {prof} : {name} (rang ≈ {rank}{est})":
        "- Crafted by {prof}: {name} (rank ≈ {rank}{est})",
    "- Composant de : {list}":
        "- Reagent of: {list}",
    "\nAutres objets au nom proche : {list}":
        "\nOther items with a similar name: {list}",
    "Aucune amélioration trouvée dans la base locale avec ces critères (élargis avec marge_niveau ou qualite_min).":
        "No upgrade found in the local database with these criteria (widen with marge_niveau or qualite_min).",
    "**{slot}** (équipé : {name})":
        "**{slot}** (equipped: {name})",
    "Donjons et raids connus du client :":
        "Dungeons and raids known to the client:",
    "Donjon « {name} » introuvable dans la base. Appelle get_dungeon_loot sans paramètre pour la liste.":
        "Dungeon \"{name}\" not found in the database (names are in the game's language). Call get_dungeon_loot without parameter for the list.",
    "Boss : {list}":
        "Bosses: {list}",
    "\nButin : **pas dans les fichiers du client Forever** (le Journal des donjons n'y est pas rempli). Pour le butin par boss : mémoire de recherche (search_knowledge), puis web ; un export en jeu du Journal des donjons par l'addon est prévu.":
        "\nLoot: **not in the Forever client files** (the Dungeon Journal is empty there). For loot per boss: research memory (search_knowledge), then the web; an in-game export of the Dungeon Journal by the addon is planned.",
    "\nAutres correspondances : {list}":
        "\nOther matches: {list}",
    "Indique le métier (ex. « Travail du cuir »).":
        "Give the profession (e.g. \"Leatherworking\").",
    "Métier « {name} » introuvable ou sans recette dans la base.":
        "Profession \"{name}\" not found or without recipes in the database.",
    "Aucune recette dans cette tranche.":
        "No recipe in this range.",
    "Quête inconnue de la base locale (le client ne connaît que les titres des quêtes déjà vues) et absente du journal. Cherche dans la mémoire, puis sur le web.":
        "Quest unknown to the local database (the client only knows the titles of quests already seen) and not in the quest log. Search the memory, then the web.",
    "- Base du jeu absente : les pistes d'amélioration (find_upgrades) demandent de la construire une fois : `{cmd}`.":
        "- Game database missing: upgrade suggestions (find_upgrades) need it to be built once: `{cmd}`.",
    "\n**Pistes d'amélioration {badge}** (détail : find_upgrades) :":
        "\n**Upgrade leads {badge}** (details: find_upgrades):",
    "Emplacement « {slot} » inconnu. Exemples : tête, cou, distance, main droite, doigt (ou head, neck, ranged, main hand, finger).":
        "Unknown slot \"{slot}\". Examples: head, neck, ranged, main hand, finger (or tête, cou, distance, main droite, doigt).",
    "Détail et sources d'un objet : get_item. La base contient tous les objets définis par le client, y compris certains jamais obtenables : vérifie la source avant de conseiller.":
        "Item details and sources: get_item. The database holds every item defined by the client, including some that can never be obtained: check the source before recommending.",
    "Donne l'itemId ou le nom de l'objet.":
        "Give the itemId or the item name.",
    "source non répertoriée":
        "source not listed",
    "Stats calculées depuis les fichiers du jeu et les correctifs Forever (exactes sur les objets vérifiés). Un objet de la base n'est pas forcément obtenable : pour une « source non répertoriée », vérifie où il tombe (mémoire de recherche, puis web) avant de l'annoncer. Les objets à suffixe aléatoire (« … de l'aigle ») n'ont pas de stats de base et sont ignorés. Maîtrises d'armes/armures selon Classic.":
        "Stats computed from the game files and the Forever hotfixes (exact on the verified items). An item in the database is not necessarily obtainable: for a \"source not listed\", check where it drops (research memory, then the web) before announcing it. Random-suffix items (\"… of the Eagle\") have no base stats and are ignored. Weapon/armor proficiencies as in Classic.",
    "- {name} ({kind}, carte {map}, {n} boss)":
        "- {name} ({kind}, map {map}, {n} bosses)",
    "**{prof}** — recettes de rang ≈ {rmin} à {rmax}":
        "**{prof}** — recipes of rank ≈ {rmin} to {rmax}",
    "Rang requis : le client Forever ne le donne presque jamais ; il est repris du patron, schéma ou plan qui apprend la recette, ou de l'objet fabriqué quand il exige ce métier. Sinon « ≈ » = estimation (5 × niveau de l'objet fabriqué, ou rang de ses composants), à confirmer chez le formateur. Une recette rapporte des points tant qu'elle n'est pas grise ; ouvre la fenêtre du métier en jeu pour que l'addon capture les couleurs exactes. Les sources des recettes (formateur, marchand, butin) ne sont pas dans la base.":
        "Required rank: the Forever client almost never provides it; it is taken from the pattern, schematic or plan that teaches the recipe, or from the crafted item when it requires this profession. Otherwise \"≈\" = estimate (5 × item level of the crafted item, or rank of its reagents), to confirm at the trainer. A recipe gives points as long as it is not grey; open the profession window in game so the addon captures the exact colours. Recipe sources (trainer, vendor, loot) are not in the database.",
    "Donne le questId ou le titre de la quête.":
        "Give the questId or the quest title.",
    "- Objectif : {text}":
        "- Objective: {text}",
    "- Titre et texte inconnus localement : la quête n'a pas encore été vue en jeu.":
        "- Title and text unknown locally: the quest has not been seen in game yet.",
    "\nDans ton journal : **{title}** (niv. {level})":
        "\nIn your quest log: **{title}** (lvl {level})",
    "Les fichiers du client ne contiennent ni le niveau, ni le donneur, ni les récompenses des quêtes : get_quests/get_quest_rewards pour celles du journal, sinon mémoire puis web.":
        "The client files contain neither the level, nor the quest giver, nor the rewards of quests: get_quests/get_quest_rewards for those in the log, otherwise memory then the web.",
    "Type « {type} » inconnu. Exemples : cuir, maille, arc, fusil, arbalète, dague, épée, bâton, anneau, cape (ou en anglais : leather, mail, bow, gun, crossbow, dagger…).":
        "Unknown type \"{type}\". Examples: leather, mail, bow, gun, crossbow, dagger, sword, staff, ring, cloak (or in French: cuir, maille, arc, fusil, arbalète…).",
    "- {name} ({slot}, niv. {req}) — {stats}":
        "- {name} ({slot}, lvl {req}) — {stats}",
    " (ton rang : {rank})":
        " (your rank: {rank})",
    " — à rendre":
        " — ready to turn in",
    " estimé":
        " estimated",
    "- Pour {name} : {verdict}":
        "- For {name}: {verdict}",
    "rien":
        "nothing",
    "- {name} (id {id}, {quality}, niv. {req}) — {stats} → {verdict}":
        "- {name} (id {id}, {quality}, lvl {req}) — {stats} → {verdict}",
    "(titre inconnu)":
        "(unknown title)",
    "Butin commun":
        "Shared loot",
    "Compétence d'arme pour « {text} » introuvable dans la capture : vérifie en jeu que tu sais l'utiliser (maître d'armes).":
        "Weapon skill for \"{text}\" not found in the capture: check in game that you can use it (weapon master).",
    "Perso actif : {name}-{suffix} ({user}). Il le reste jusqu'à ce qu'un autre perso soit capturé plus récemment.":
        "Active character: {name}-{suffix} ({user}). It stays active until another character is captured more recently.",
    "Enregistré dans la mémoire de recherche : {path}":
        "Saved in the research memory: {path}",
    "Récompense : {list}":
        "Reward: {list}",
    "\nDossier des données : {path}":
        "\nData folder: {path}",
    "aucun":
        "none",
    "- Familier : aucun":
        "- Pet: none",
    "- Armes : {list}":
        "- Weapons: {list}",
    "- Métiers : {list}":
        "- Professions: {list}",
    "- Quêtes : {n}/{max} dans le journal, {done} à rendre · {total} terminées au total":
        "- Quests: {n}/{max} in the log, {done} to turn in · {total} completed in total",
    "- Régénération de mana : {n} (hors incantation)":
        "- Mana regeneration: {n} (out of casting)",
    "- Défense : {def} · crit des sorts {crit}{pc}":
        "- Defense: {def} · spell crit {crit}{pc}",
    "- Points : {spent}/{max} dépensés, {free} disponibles":
        "- Points: {spent}/{max} spent, {free} available",
    " Récompenses inconnues : elles apparaissent avec l'addon 1.2 après une synchro (Ctrl+Maj+S).":
        " Rewards unknown: they appear with addon 1.2 after a sync (Ctrl+Shift+S).",
    "\nDétail par quête :":
        "\nDetail per quest:",
    "\nPour le détail : get_equipment, get_inventory, get_quest_rewards, get_talents, get_professions, find_upgrades.":
        "\nFor details: get_equipment, get_inventory, get_quest_rewards, get_talents, get_professions, find_upgrades.",
    "Rien dans la mémoire de recherche pour « {q} » ({folder}). Cherche ailleurs (knowledge/ du plugin, puis le web), puis enregistre la trouvaille avec save_knowledge.":
        "Nothing in the research memory for \"{q}\" ({folder}). Look elsewhere (the plugin's knowledge/, then the web), then save the finding with save_knowledge.",
    "Mémoire de recherche ({folder}) — {n} note(s) :":
        "Research memory ({folder}) — {n} note(s):",
    "fin de journée du {date}":
        "end of day {date}",
    "objet proposé":
        "offered item",
    "| | Équipé : {name} | {cand} |":
        "| | Equipped: {name} | {cand} |",
    "**À prendre : environ {sign}{delta} DPS{pct}.**":
        "**Take it: about {sign}{delta} DPS{pct}.**",
    "1 Agi = 2 PA à distance et 1 PA en mêlée, 1 For = 1 PA en mêlée (cohérent avec la fiche du perso)":
        "1 Agi = 2 ranged AP and 1 melee AP, 1 Str = 1 melee AP (consistent with the character sheet)",
    "conversions For/Agi → PA reprises de Classic, à vérifier dans Forever":
        "Str/Agi → AP conversions taken from Classic, to check in Forever",
    "Hypothèses : 14 PA = 1 DPS (confirmé dans Forever) ; {conv}.":
        "Assumptions: 14 AP = 1 DPS (confirmed in Forever); {conv}.",
    "Non chiffré : le crit apporté par l'Agilité, les effets spéciaux (« Chance quand vous touchez… »).":
        "Not counted: crit from Agility, special effects (\"Chance on hit…\").",
    "| Perso | Joueur | Classe | Niveau | Zone | ilvl | Argent | Métiers | Capturé |":
        "| Character | Player | Class | Level | Zone | ilvl | Money | Professions | Captured |",
    ", remplace {name}":
        ", replaces {name}",
    ", emplacement vide":
        ", empty slot",
    " (fixe)":
        " (fixed)",
    " (au choix)":
        " (choice)",
    "à prendre : {pick}":
        "take: {pick}",
    "Aucune donnée synchronisée pour {name}. Synchronise en jeu (Ctrl+Maj+S ou /sync).":
        "No synced data for {name}. Sync in game (Ctrl+Shift+S or /sync).",
    "Aucun perso connu. En jeu : active l'addon ForeverScribe, connecte un perso, puis Ctrl+Maj+S (ou /sync).":
        "No known character. In game: enable the ForeverScribe addon, log in a character, then Ctrl+Shift+S (or /sync).",
    "\nPersos présents dans le jeu mais jamais capturés par l'addon : {list}. Connecte-les avec ForeverScribe actif, puis Ctrl+Maj+S (ou /sync).":
        "\nCharacters present in the game but never captured by the addon: {list}. Log them in with ForeverScribe enabled, then Ctrl+Shift+S (or /sync).",
    "\nComptes sans prénom : {list}. Demande au joueur à qui ils appartiennent, puis register_account.":
        "\nAccounts without a first name: {list}. Ask the player who they belong to, then register_account.",
    "Indique le perso : nom, Nom-Région ou Utilisateur/Nom.":
        "Give the character: name, Name-Region or User/Name.",
    "Paramètres requis : account (dossier WTF/Account) et user (prénom).":
        "Required parameters: account (WTF/Account folder) and user (first name).",
    "- Familier : {name} ({family}) niveau {level}":
        "- Pet: {name} ({family}) level {level}",
    "- Données non lues : {list}":
        "- Data not read: {list}",
    " · langue du jeu : {locale}":
        " · game language: {locale}",
    "- Valeur de la PA à distance : {dps} DPS (14 PA = 1 DPS, confirmé dans Forever)":
        "- Value of ranged AP: {dps} DPS (14 AP = 1 DPS, confirmed in Forever)",
    "- Munitions : {yes}":
        "- Ammo: {yes}",
    "Récompenses de quête inconnues : elles sont capturées par l'addon ForeverScribe 1.2 ou plus. Mets l'addon à jour, puis synchronise en jeu (Ctrl+Maj+S). En attendant, ne présente pas de récompense comme certaine.":
        "Quest rewards unknown: they are captured by the ForeverScribe addon 1.2 or later. Update the addon, then sync in game (Ctrl+Shift+S). Until then, do not present any reward as certain.",
    "**À rendre maintenant, avec une amélioration :**":
        "**Turn in now, with an upgrade:**",
    "\n**En cours, avec une amélioration à la clé :**":
        "\n**In progress, with an upgrade to earn:**",
    "**Aucune récompense de quête connue n'améliore ton équipement.**":
        "**No known quest reward improves your gear.**",
    "- Emplacements vides : {list} — vide ne veut pas dire faible : ne conseille pas de les remplir sans un objet précis disponible à ce niveau (récompense, donjon, artisanat, marchand).":
        "- Empty slots: {list} — empty does not mean weak: do not advise filling them without a specific item available at this level (reward, dungeon, crafting, vendor).",
    ", {n} à rendre":
        ", {n} to turn in",
    "\n**Quêtes à rendre :**":
        "\n**Quests to turn in:**",
    "Indique la question ou les mots-clés à chercher.":
        "Give the question or the keywords to search.",
    "\nCompétences d'armes : {list}":
        "\nWeapon skills: {list}",
    "\nMonnaies : {list}":
        "\nCurrencies: {list}",
    "Ce perso n'a pas de familier de chasseur.":
        "This character has no hunter pet.",
    "première capture ({date})":
        "first capture ({date})",
    "Pas encore d'historique : il se construit à chaque synchro (un instantané par jour).":
        "No history yet: it builds up at every sync (one snapshot per day).",
    "Depuis la {label} :":
        "Since the {label}:",
    "temps de jeu +{d}":
        "played time +{d}",
    "| DPS de l'arme | {a} | {b} |":
        "| Weapon DPS | {a} | {b} |",
    "| **DPS à distance (coups blancs)** | {now} | **≈ {new}** ({sign}{delta}) |":
        "| **Ranged DPS (white hits)** | {now} | **≈ {new}** ({sign}{delta}) |",
    "| DPS en mêlée (coups blancs) | {now} | ≈ {new} ({sign}{delta}) |":
        "| Melee DPS (white hits) | {now} | ≈ {new} ({sign}{delta}) |",
    "**À ne pas équiper : environ {delta} DPS{pct}.**":
        "**Do not equip: about {delta} DPS{pct}.**",
    "**Quasi équivalent en dégâts** : départage avec l'endurance ou l'armure.":
        "**Nearly equivalent in damage**: decide with stamina or armor.",
    "Endurance : {sign}{n} (≈ {hp} PV, hypothèse Classic).":
        "Stamina: {sign}{n} (≈ {hp} HP, Classic assumption).",
    "Niveau requis {n} : pas encore équipable.":
        "Required level {n}: not equippable yet.",
    "Aucun perso capturé.":
        "No captured character.",
    "\nQui fait quoi :":
        "\nWho does what:",
    "**Attention, compétence {name} : {rank}/{max}.** Avec une compétence basse, beaucoup de tirs ou de coups ratent au début : le gain réel n'arrive qu'après l'avoir montée en l'utilisant [Classic · probable dans Forever, la compétence existe en jeu].":
        "**Careful, {name} skill: {rank}/{max}.** With a low skill, many shots or swings miss at first: the real gain only comes after raising it by using the weapon [Classic · likely in Forever, the skill exists in game].",
    "objets : {names} (rien de mieux pour toi)":
        "items: {names} (nothing better for you)",
    " ← actif":
        " ← active",
    " — renvoyé":
        " — dismissed",
    "\nCompte {account} · capture du {time}":
        "\nAccount {account} · capture of {time}",
    "Stats capturées {age}.":
        "Stats captured {age}.",
    "Équipement capturé {age}.":
        "Equipment captured {age}.",
    "Talents capturés {age}.":
        "Talents captured {age}.",
    "Sorts capturés {age}.":
        "Spells captured {age}.",
    "fixe":
        "fixed",
    "au choix":
        "choice",
    "  - réputation : {name} +{n}":
        "  - reputation: {name} +{n}",
    "Gains estimés en coups blancs (14 PA = 1 DPS, confirmé) ; maîtrises d'armes et d'armures selon Classic, à vérifier dans Forever — le drapeau « utilisable » du jeu prime.":
        "Gains estimated on white hits (14 AP = 1 DPS, confirmed); weapon and armor proficiencies as in Classic, to check in Forever — the game's \"usable\" flag wins.",
    "Journal capturé {age}.":
        "Quest log captured {age}.",
    "- Quêtes : {n}/{max}":
        "- Quests: {n}/{max}",
    "\n**Améliorations à gagner en finissant des quêtes en cours :**":
        "\n**Upgrades to earn by finishing current quests:**",
    "Une note « probable » ou ancienne se recoupe avant d'être affirmée ; une note contredite par le jeu se corrige avec save_knowledge.":
        "A \"probable\" or old note is cross-checked before being stated; a note contradicted by the game is fixed with save_knowledge.",
    "Métiers capturés {age}.":
        "Professions captured {age}.",
    "Sacs capturés {age}.":
        "Bags captured {age}.",
    "Réputations capturées {age}.":
        "Reputations captured {age}.",
    "Familier capturé {age}.":
        "Pet captured {age}.",
    "- Argent : {a} → {b}":
        "- Money: {a} → {b}",
    "- Aucun changement notable.":
        "- No notable change.",
    "\nJournal sur la période :":
        "\nJournal over the period:",
    "Emplacement « {slot} » inconnu. Exemples : distance, main droite, tête, doigt 2 (ou ranged, main hand, head, finger 2).":
        "Unknown slot \"{slot}\". Examples: ranged, main hand, head, finger 2 (or distance, main droite, tête, doigt 2).",
    "Indique l'emplacement (ex. « distance », « mains », « doigt 1 »).":
        "Give the slot (e.g. \"ranged\", \"hands\", \"finger 1\").",
    "Note : {domains} repris de la capture précédente (valeurs vides à la déconnexion).":
        "Note: {domains} taken from the previous capture (empty values at logout).",
    " · origine : {reason}":
        " · origin: {reason}",
    "Journal capturé {age}. Couleurs : difficulté par rapport au niveau du perso. `/way` = coordonnées sur la carte de la quête.":
        "Quest log captured {age}. Colours: difficulty relative to the character's level. `/way` = quest map coordinates.",
    "{n} quête(s) sans récompenses capturées (journal ouvert pendant la capture, ou capture ancienne) : resynchronise.":
        "{n} quest(s) without captured rewards (log open during the capture, or old capture): sync again.",
    "aucune":
        "none",
    " (journal plein)":
        " (quest log full)",
    "Récompenses de quête inconnues (addon antérieur à 1.2) : synchronise avec l'addon à jour.":
        "Quest rewards unknown (addon older than 1.2): sync with the updated addon.",
    "{date} · certitude : {cert} · sources : {src} · fichier {file}":
        "{date} · certainty: {cert} · sources: {src} · file {file}",
    "- Niveau {a} → {b}":
        "- Level {a} → {b}",
    "connu de l'addon mais pas encore synchronisé (connecte-le puis Ctrl+Maj+S (ou /sync))":
        "known to the addon but not synced yet (log it in, then Ctrl+Shift+S (or /sync))",
    "oui":
        "yes",
    "non":
        "no",
    "un objet n'était pas encore chargé par le jeu : resynchronise pour le détail":
        "an item was not loaded by the game yet: sync again for the details",
    "Je connais « {name} » ({where}) mais pas ses stats : l'addon ne lit les stats que des objets équipés et la base locale du jeu n'est pas construite. Donne-moi ses stats (DPS, agilité, PA…) en paramètres, ou construis la base : {cmd}":
        "I know \"{name}\" ({where}) but not its stats: the addon only reads the stats of equipped items and the local game database is not built. Give me its stats (DPS, agility, AP…) as parameters, or build the database: {cmd}",
    "capturé {age}":
        "captured {age}",
    "{acc} (affiché « {name} »)":
        "{acc} (shown as \"{name}\")",
    "Format de date attendu : AAAA-MM-JJ, « hier », « aujourd'hui » ou « semaine ».":
        "Expected date format: YYYY-MM-DD, \"yesterday\", \"today\" or \"week\".",
    "non notées":
        "not recorded",
    "dans tes sacs":
        "in your bags",
    "objet inconnu":
        "unknown item",
    "Erreur interne de {tool} : {err}":
        "Internal error in {tool}: {err}",
    "Première capture par l'addon : {race} {cls} niveau {level} · {zone} · {n} quêtes en cours · {done} terminées":
        "First capture by the addon: {race} {cls} level {level} · {zone} · {n} quests in progress · {done} completed",
    "Familier {name} niveau {level}":
        "Pet {name} level {level}",
    "Le compte {acc} est déjà rattaché à {user}.":
        "Account {acc} is already linked to {user}.",
    "à rendre à {who}": "turn in to {who}",
    "**{n} quêtes disponibles** pour {name} (niv. {level}) dans **{zone}** : quêtes de niveau {a}-{b}, niveau requis {c} au plus":
        "**{n} quests available** for {name} (lvl {level}) in **{zone}**: quest levels {a}-{b}, required level {c} at most",
    "**Aucune quête disponible** pour {name} (niv. {level}) dans **{zone}**":
        "**No quest available** for {name} (lvl {level}) in **{zone}**",
    "rien à prendre pour ton niveau, d'autres quêtes plus tard": "nothing to pick up at your level, more quests later",
    "aucune quête connue ici dans QuestieDB (couverture partielle pour Forever)":
        "no known quest here in QuestieDB (partial coverage for Forever)",
    "**Pas encore : niveau {n} requis, ensuite environ {sign}{delta} DPS{pct}.**":
        "**Not yet: level {n} required, then about {sign}{delta} DPS{pct}.**",
    "**À prendre, mais compétence {name} à {rank}/{max} : environ +{delta} DPS{pct} une fois montée, beaucoup de coups ratés d'ici là.**":
        "**Take it, but {name} skill is {rank}/{max}: about +{delta} DPS{pct} once leveled, lots of misses until then.**",
    "Comparé à {slot}, le plus faible des deux emplacements.": "Compared with {slot}, the weaker of the two slots.",
    " (et compétence {name} à {rank}/{max})": " (and {name} skill at {rank}/{max})",
    "- **Objet probablement inobtenable** (objet de test, stats ou niveau d'objet hors du jeu) : ne le conseille pas.":
        "- **Probably unobtainable item** (test item, stats or item level outside the game): do not recommend it.",
    "{prof} ≈{rank} requis (métier non appris)": "{prof} ≈{rank} required (profession not learned)",
    "{prof} ≈{rank} requis, tu es à {have}": "{prof} ≈{rank} required, you are at {have}",
    "- Pour toi : {gap}": "- For you: {gap}",
    '**Donjons et raids de Forever**, par niveau conseillé :': '**Forever dungeons and raids**, by recommended level:',
    'Donjons (5 joueurs)': 'Dungeons (5 players)',
    'Raids': 'Raids',
    'Les cartes de test et de Season of Discovery présentes dans le client sont masquées. Fourchettes Classic : à vérifier dans Forever.': 'Test and Season of Discovery maps found in the client are hidden. Classic ranges: to check in Forever.',
    'Donjon « {name} » introuvable. Appelle dungeon sans paramètre pour la liste.': 'Dungeon "{name}" not found. Call dungeon without parameters for the list.',
    '**{name}** ({en}) — {levels} {badge}': '**{name}** ({en}) — {levels} {badge}',
    '- Zone : {zone}': '- Zone: {zone}',
    "- Boss et butin : pas dans les fichiers du client. Mémoire de recherche (search), puis web ; un export en jeu du Journal des donjons par l'addon est prévu.": '- Bosses and loot: not in the client files. Research notes (search), then the web; an in-game Dungeon Journal export by the addon is planned.',
    '- {levels} {badge}': '- {levels} {badge}',
    'Boss ({n}) : {list}': 'Bosses ({n}): {list}',
    '[Classic · à vérifier dans Forever]': '[Classic · check in Forever]',
    'niveaux {lv}': 'levels {lv}',
    'niveau {lv}': 'level {lv}',
    'raid {n} joueurs': '{n}-player raid',
    'ouvre le {date}': 'opens {date}',
    'pas encore ouvert dans Forever': 'not open yet in Forever',
    '{name} : {status}': '{name}: {status}',
    '{name} : {levels}': '{name}: {levels}',
    '{name} ({a}-{b}), toi {lvl} : encore tôt, reviens vers le niveau {a}': '{name} ({a}-{b}), you {lvl}: too early, come back around level {a}',
    "{name} ({a}-{b}), toi {lvl} : trop bas pour toi, peu d'XP ; seulement pour les quêtes ou un objet": '{name} ({a}-{b}), you {lvl}: too low for you, little XP; only for quests or a specific item',
    '{name} ({a}-{b}), toi {lvl} : fin de fourchette, facile, fais-le pour les quêtes': '{name} ({a}-{b}), you {lvl}: end of the range, easy, do it for the quests',
    "{name} ({a}-{b}), toi {lvl} : c'est le bon moment, en groupe de 5 avec les quêtes prises avant": '{name} ({a}-{b}), you {lvl}: right time, group of 5 with the quests picked up first',
    '\n**Dans ton journal pour ce donjon** (chaînes comprises) : {list}': '\n**In your log for this dungeon** (chains included): {list}',
    '- Problème connu (au {date}) : *{quest}* — {problem} ({status})': '- Known issue (as of {date}): *{quest}* — {problem} ({status})',
    '{name} : quêtes niv. {a}-{b}, toi {lvl} : niveau du donjon inconnu, vise le niveau des quêtes': '{name}: quests lvl {a}-{b}, you {lvl}: dungeon level unknown, aim for the quest level',
    '{name} : donjon de groupe, niveau conseillé inconnu de la base': '{name}: group dungeon, recommended level unknown to the database',
    'Donjon : **{name}** ({levels}) → dungeon donjon:{name}': 'Dungeon: **{name}** ({levels}) → dungeon donjon:{name}',
    'Connaissance Forever : **{title}** ({file})': 'Forever knowledge: **{title}** ({file})',
    'connaissances du plugin ({file}), à citer avec leur badge et leur date': 'plugin knowledge ({file}), quote with its badge and date',
    'Sort : **{name}** (id {id}) → talents sorts:true': 'Spell: **{name}** (id {id}) → talents sorts:true',
    "Compte {acc} rattaché à {user}":
        "Account {acc} linked to {user}",
    "**Niveau {n} atteint**":
        "**Level {n} reached**",
    "Quête rendue : {title}":
        "Quest turned in: {title}",
    "{n} autre(s) quête(s) terminée(s)":
        "{n} other quest(s) completed",
    "Nouvelle zone : {zone}":
        "New zone: {zone}",
    "Réputation {name} : {a} → {b}":
        "Reputation {name}: {a} → {b}",
    "Spé : {a} → {b}":
        "Spec: {a} → {b}",
    "<!-- Tes notes à la main : jamais modifiées par la synchro. -->":
        "<!-- Your own notes: never modified by the sync. -->",
    "Perso « {q} » inconnu. Utilise list_characters.":
        "Unknown character \"{q}\". Use list_characters.",
    "Plusieurs persos correspondent : {list}. Précise.":
        "Several characters match: {list}. Be more specific.",
    "{name} n'a pas encore été capturé : connecte-le en jeu avec ForeverScribe actif, puis Ctrl+Maj+S (ou /sync).":
        "{name} has not been captured yet: log it in with ForeverScribe enabled, then Ctrl+Shift+S (or /sync).",
    "Compte « {acc} » inconnu. Comptes : {list}.":
        "Unknown account \"{acc}\". Accounts: {list}.",
    " ; dossiers déplacés : {list}.":
        "; folders moved: {list}.",
    "Quête retirée du journal (abandonnée ?) : {title}":
        "Quest removed from the log (abandoned?): {title}",
    "Objectifs remplis, à rendre : {title}":
        "Objectives complete, ready to turn in: {title}",
    "Équipé ({slot}) : {name}":
        "Equipped ({slot}): {name}",
    " à la place de {name}":
        " instead of {name}",
    "Nouveau métier : {name} ({rank}/{max})":
        "New profession: {name} ({rank}/{max})",
    "Nouvelle réputation : {name} ({standing})":
        "New reputation: {name} ({standing})",
    "Talent retiré : {name}":
        "Talent removed: {name}",
    "Nouveau(x) sort(s) : {list}":
        "New spell(s): {list}",
    "### Ancien profil (avant l'addon)":
        "### Old profile (before the addon)",
    "Aucun perso capturé. En jeu : active ForeverScribe, puis Ctrl+Maj+S (ou /sync).":
        "No captured character. In game: enable ForeverScribe, then Ctrl+Shift+S (or /sync).",
    "Le dossier {path} existe déjà : déplace-le à la main puis recommence.":
        "Folder {path} already exists: move it by hand, then try again.",
    "{name} : plafond porté à {max}":
        "{name}: cap raised to {max}",
    "## Mes notes":
        "## My notes",
    "# Profil — {name}-{suffix} ({region})":
        "# Profile — {name}-{suffix} ({region})",
    "## Journal automatique":
        "## Automatic journal",
    "[Forever · base locale]":
        "[Forever · local DB]",
    "La base locale du jeu n'est pas encore construite. Elle se construit une fois, en quelques secondes, à partir des fichiers de ton client WoW Forever (lecture seule) :\n\n    {cmd}\n\n(depuis le dépôt : python3 tools/gamedata/build_db.py). Ensuite, ces outils répondent sans recherche web.":
        "The local game database is not built yet. It is built once, in a few seconds, from the files of your WoW Forever client (read only):\n\n    {cmd}\n\n(from the repository: python3 tools/gamedata/build_db.py). Then these tools answer without any web search.",
    "(compétence ":
        "(skill ",
    # -- questdb_tools.py (QuestieDB) --
    '**{title}** (id {id}) — niveau {level}, requis {req}':
        '**{title}** (id {id}) — level {level}, requires {req}',
    'niv. {level}':
        'lvl {level}',
    'zone {id}':
        'zone {id}',
    'quête {id}':
        'quest {id}',
    'faite':
        'done',
    'dans ton journal, à rendre':
        'in your log, ready to turn in',
    'dans ton journal':
        'in your log',
    'pas faite':
        'not done',
    '**{n} quêtes disponibles** pour {name} (niv. {level}) dans **{zone}**, niveaux {a}-{b}':
        '**{n} quests available** for {name} (lvl {level}) in **{zone}**, levels {a}-{b}',
    '**{n} quêtes** dans **{zone}**':
        '**{n} quests** in **{zone}**',
    'Filtre : race, classe, prérequis faits, quêtes déjà faites ou dans le journal exclues.':
        'Filter: race, class, completed prerequisites; quests already done or in the log removed.',
    'Couverture QuestieDB partielle pour les quêtes ajoutées par Forever.':
        'QuestieDB coverage is partial for quests added by Forever.',
    ', requis {n}':
        ', requires {n}',
    ' — donneur : {who}':
        ' — giver: {who}',
    ' · suite de *{title}*':
        ' · follows *{title}*',
    ' · répétable':
        ' · repeatable',
    '- Titre anglais : {name}':
        '- English title: {name}',
    'classe réservée':
        'class-restricted',
    '**pas pour ce perso**':
        '**not for this character**',
    'répétable':
        'repeatable',
    'événement saisonnier':
        'seasonal event',
    'métier requis (compétence {id}, rang {rank})':
        'profession required (skill {id}, rank {rank})',
    '- Conditions : {list}':
        '- Requirements: {list}',
    '- Donneur : {who}':
        '- Quest giver: {who}',
    '- À rendre à : {who}':
        '- Turn in to: {who}',
    '- Réputation : {list}':
        '- Reputation: {list}',
    ' et {n} autres':
        ' and {n} more',
    'vendu par {name}':
        'sold by {name}',
    '- Prérequis (toutes) : {list}':
        '- Prerequisites (all): {list}',
    "- Quête d'introduction (facultative) qui mène à : {list}":
        '- Optional breadcrumb leading to: {list}',
    '- Fait partie de : {list}':
        '- Part of: {list}',
    '- Suite : {list}':
        '- Next: {list}',
    '- Exclusive avec : {list}':
        '- Exclusive with: {list}',
    '_Autres quêtes du même nom : {list}._':
        '_Other quests with the same name: {list}._',
    'Précise la zone (aucun perso synchronisé pour la deviner).':
        'Give the zone (no synced character to guess it from).',
    'Zone « {zone} » inconnue de la base (nom dans la langue du jeu).':
        'Zone "{zone}" not found in the database (name in the game language).',
    '- … et {n} autres (limite={limit}).':
        '- … and {n} more (limite={limit}).',
    '\n_Plus tard ({n}) : {list}._':
        '\n_Later ({n}): {list}._',
    '\n_Classées dans cette zone par QuestieDB mais données ailleurs ({n}) : {list}._':
        '\n_Filed under this zone by QuestieDB but given elsewhere ({n}): {list}._',
    " · objectif : {text}": " · objective: {text}",
    " · **rendu** : {where}": " · **turn-in**: {where}",
    " · suite : {text}": " · follow-up: {text}",
    " · prérequis : *{name}*": " · prerequisite: *{name}*",
    "point du jeu (ton journal) : {where}": "in-game waypoint (your quest log): {where}",
    " ; pierre de rencontre au pied du chemin `/way {way}`": "; meeting stone at the foot of the path `/way {way}`",
    "**Entrée** [Forever · {src}] : {text}": "**Entrance** [Forever · {src}]: {text}",
    "**Dangers hors boss (trash)** [Forever · {src}] :": "**Non-boss dangers (trash)** [Forever · {src}]:",
    'Quêtes terminées non capturées : la liste peut contenir des quêtes déjà faites.':
        'Completed quests not captured: the list may contain quests already done.',
    "Donne le nom (ou npcId) du PNJ, du monstre ou de l'objet à trouver.":
        'Give the name (or npcId) of the NPC, mob or object to find.',
    'Aucun PNJ ni objet « {name} » dans QuestieDB (nom dans la langue du jeu ou en anglais).':
        'No NPC or object "{name}" in QuestieDB (name in the game language or in English).',
    'hostile':
        'hostile',
    '**{name}**{sub} (PNJ {id}{lvl}, {friendly})':
        '**{name}**{sub} (NPC {id}{lvl}, {friendly})',
    '- Où : {where}':
        '- Where: {where}',
    '**{name}** (objet {id})':
        '**{name}** (object {id})',
    'Donne':
        'Gives',
    'Reçoit':
        'Receives',
    'Les quêtes et PNJ de QuestieDB ne sont pas encore dans la base locale. Ajoute-les une fois (téléchargement depuis GitHub, quelques secondes) :\n\n    {cmd}':
        'QuestieDB quests and NPCs are not in the local database yet. Add them once (download from GitHub, a few seconds):\n\n    {cmd}',
    'PNJ {id}':
        'NPC {id}',
    'objet **{name}**':
        'object **{name}**',
    "objet de l'inventaire **{name}** (id {id}) : clic droit dessus pour lancer la quête":
        'bag item **{name}** (id {id}): right-click it to start the quest',
    ' (niv. {a}-{b})':
        ' (lvl {a}-{b})',
    ' (niv. {a})':
        ' (lvl {a})',
    '  - tuer **{name}**{lvl}':
        '  - kill **{name}**{lvl}',
    '  - utiliser **{name}**':
        '  - use **{name}**',
    '  - récupérer **{name}**':
        '  - collect **{name}**',
    '  - **{name}**':
        '  - **{name}**',
    '  - explorer : {text} — {zone} · `/way {x} {y}`':
        '  - explore: {text} — {zone} · `/way {x} {y}`',
    'sur {names}{more}':
        'from {names}{more}',
    'dans {name}':
        'in {name}',
    '- Prérequis (une seule suffit) : {list}':
        '- Prerequisites (any one): {list}',
    '- Prérequis : {list}':
        '- Prerequisite: {list}',
    'Dans ton journal : **{title}** (niv. {level})':
        'In your log: **{title}** (lvl {level})',
    'Source : QuestieDB (communauté Questie), révision {rev} ; positions en % de la carte de la zone. Une quête refaite par Forever peut différer : vérifie en jeu si un détail ne colle pas.':
        'Source: QuestieDB (Questie community), revision {rev}; positions in % of the zone map. A quest reworked by Forever may differ: check in game if a detail does not match.',
    'Ni donneur ni chaîne connus localement pour cette quête (absente de QuestieDB ou QuestieDB non importé) : get_quests pour celles du journal, sinon mémoire puis web.':
        'No quest giver or chain known locally for this quest (missing from QuestieDB, or QuestieDB not imported): get_quests for quests in the log, otherwise memory then web.',
    "\n**À rendre d'abord** : {list}.":
        '\n**Turn in first**: {list}.',
    ', niv. {a}':
        ', lvl {a}',
    ', niv. {a}-{b}':
        ', lvl {a}-{b}',
    'Positions en % de la carte de la zone (/way). Plusieurs points : le plus central est indiqué.':
        'Positions in % of the zone map (/way). Several spawn points: the most central one is shown.',
    ' ({n} points)':
        ' ({n} points)',
    'certaines races':
        'some races only',
    'Donneur, niveau, objectifs localisés et chaîne : ajoute QuestieDB à la base (`{cmd}`).':
        'Quest giver, level, objective locations and chain: add QuestieDB to the database (`{cmd}`).',
    'Alliance et Horde':
        'Alliance and Horde',
    'position inconnue':
        'unknown location',
    'faction {id}':
        'faction {id}',
    'requis {n}':
        'requires {n}',
    '[Forever · QuestieDB]':
        '[Forever · QuestieDB]',
    # v0.8 — outils d'intention, résumé, recherche
    'équipe **{item}**, déjà dans tes sacs ({slot}, {gain})':
        'equip **{item}**, already in your bags ({slot}, {gain})',
    "- Source inconnue (à vérifier avant d'en parler) :":
        '- Unknown source (check before mentioning it):',
    '  - … et {n} autres (detail:complet).':
        '  - … and {n} more (detail:complet).',
    ' : elle donne une amélioration':
        ': it gives an upgrade',
    'Sacs : {free} place(s) libre(s) sur {total}':
        'Bags: {free} free slot(s) out of {total}',
    'Recette : **{name}** → professions':
        'Recipe: **{name}** → professions',
    ' · voix : {voice}':
        ' · voice: {voice}',
    ' · munitions {n}':
        ' · ammo {n}',
    'rends ta quête terminée':
        'turn in your completed quest',
    ' ; journal plein':
        '; quest log full',
    '{prof} {rank}/{max} : va chez le formateur prendre le rang suivant':
        '{prof} {rank}/{max}: visit the trainer for the next rank',
    '{name} est heureux ({pct} % de dégâts)':
        '{name} is happy ({pct}% damage)',
    "nourris {name} : il n'est pas heureux, il perd des dégâts et de la loyauté":
        'feed {name}: it is not happy and loses damage and loyalty',
    ' ; {n} points de dressage à dépenser':
        '; {n} training points to spend',
    'Rien trouvé pour « {q} » (base locale, mémoire de recherche, données du perso). Vérifie le nom dans la langue du jeu ; sinon web, puis save_knowledge.':
        'Nothing found for "{q}" (local DB, research memory, character data). Check the name in the game language; otherwise web, then save_knowledge.',
    'Objet : **{name}** (id {id}, niv. {req}, {quality}) → item itemId:{id}':
        'Item: **{name}** (id {id}, lvl {req}, {quality}) → item itemId:{id}',
    'Quête : **{name}** (id {id}) → quests questId:{id}':
        'Quest: **{name}** (id {id}) → quests questId:{id}',
    'PNJ : **{name} (id {id}) → npc npcId:{id}':
        'NPC: **{name} (id {id}) → npc npcId:{id}',
    'Objet du monde : **{name}** (id {id}) → npc nom:{name}':
        'World object: **{name}** (id {id}) → npc nom:{name}',
    'Zone : **{name}** → quests disponibles:true zone:{name}':
        'Zone: **{name}** → quests disponibles:true zone:{name}',
    'Donjon : **{name}** → dungeon donjon:{name}':
        'Dungeon: **{name}** → dungeon donjon:{name}',
    'argent {money}':
        'money {money}',
    ' — palier bientôt atteint : rang suivant chez le formateur':
        ' — cap almost reached: next rank at the trainer',
    'Métiers : {list}':
        'Professions: {list}',
    "ton journal est plein : termine ou abandonne avant d'en prendre d'autres":
        'your quest log is full: finish or drop quests before taking new ones',
    'fais de la place dans tes sacs':
        'make room in your bags',
    'nourris ton familier':
        'feed your pet',
    'rachète des munitions':
        'buy more ammo',
    'prends les quêtes de {zone} ({n} pour ton niveau)':
        'pick up the quests in {zone} ({n} for your level)',
    'continue à monter : {next}':
        'keep levelling: {next}',
    "rien d'urgent : choisis ton prochain objectif":
        'nothing urgent: pick your next goal',
    '**Prochaine étape** : {list}.':
        '**Next step**: {list}.',
    '\n**Quêtes à rendre**':
        '\n**Quests to turn in**',
    '\n**Améliorations à portée**':
        '\n**Upgrades within reach**',
    '\n**Quêtes à prendre dans {zone}** [Forever · QuestieDB]':
        '\n**Quests to pick up in {zone}** [Forever · QuestieDB]',
    '\n**État**':
        '\n**Status**',
    '**{slot}** — équipé : {item}':
        '**{slot}** — equipped: {item}',
    "\n**Par les quêtes** (à rendre d'abord)":
        '\n**From quests** (turn-ins first)',
    '\n**Déjà dans tes sacs**':
        '\n**Already in your bags**',
    '\n**Dans la base locale** (niveau requis {lmin}-{lmax}) {badge}':
        '\n**In the local DB** (required level {lmin}-{lmax}) {badge}',
    "\n_Base du jeu absente : pistes d'amélioration limitées aux quêtes et aux sacs. Construis-la une fois : `{cmd}`._":
        '\n_No game database: upgrade leads limited to quests and bags. Build it once: `{cmd}`._',
    'rien de mieux en vue pour cet emplacement':
        'nothing better in sight for this slot',
    'ton équipement est à jour pour ton niveau':
        'your gear is up to date for your level',
    'rends tes {n} quêtes terminées':
        'turn in your {n} completed quests',
    'aucune quête à rendre : avance les quêtes en cours':
        'nothing to turn in: push the quests in progress',
    '\n**À rendre ({n})**':
        '\n**To turn in ({n})**',
    '\n**En cours**':
        '\n**In progress**',
    '\n**À équiper**':
        '\n**Worth equipping**',
    '\n**À vendre (gris)** : {list}':
        '\n**To sell (grey)**: {list}',
    '\n**{prof} : recettes connues qui rapportent encore des points** (couleurs du jeu, capturées {age})':
        '\n**{prof}: known recipes that still give points** (game colours, captured {age})',
    'tu peux monter {prof} tout de suite avec ce que tu as en sacs':
        'you can level {prof} right now with what you carry',
    '- Nourriture adaptée dans tes sacs : {list}':
        '- Matching food in your bags: {list}',
    '- Aucune nourriture adaptée dans tes sacs (régime : {diet}) : achète-en chez un aubergiste ou un vendeur de nourriture.':
        '- No matching food in your bags (diet: {diet}): buy some from an innkeeper or a food vendor.',
    '- Ton niveau : {n}. Équipement et améliorations : gear.':
        '- Your level: {n}. Gear and upgrades: gear.',
    'Indique le nom ou les mots à chercher.':
        'Give the name or words to search for.',
    '**{n} résultat(s) pour « {q} »**':
        '**{n} result(s) for "{q}"**',
    '{left} XP avant le niveau {n}':
        '{left} XP to level {n}',
    'au niveau {n}, passe chez ton maître de classe (nouveaux rangs) [Classic · probable]':
        'at level {n}, visit your class trainer (new ranks) [Classic · likely]',
    'niveau pair : nouveaux rangs de sorts chez ton maître de classe [Classic · probable]':
        'even level: new spell ranks at your class trainer [Classic · likely]',
    '- … {n} autres quêtes à rendre (quests a_rendre:true).':
        '- … {n} more quests to turn in (quests a_rendre:true).',
    '- … et {n} autres (quests disponibles:true).':
        '- … and {n} more (quests disponibles:true).',
    'Équipé : {list}':
        'Equipped: {list}',
    ' (en cours)':
        ' (in progress)',
    'rends *{quest}* pour **{item}**':
        'turn in *{quest}* for **{item}**',
    'termine *{quest}* pour **{item}**':
        'finish *{quest}* for **{item}**',
    '- Rien de mieux que ton équipement à ce niveau.':
        '- Nothing better than your gear at this level.',
    'vise **{item}** ({slot}, {gain})':
        'aim for **{item}** ({slot}, {gain})',
    'Objectifs et récompenses : quests detail:normal ; une quête : quests quete:<titre>.':
        'Objectives and rewards: quests detail:normal; one quest: quests quete:<title>.',
    '- Aucune : toutes tes recettes sont grises, il en faut de nouvelles.':
        '- None: all your recipes are grey, you need new ones.',
    '{prof} {rank} : récolte les composants des prochaines recettes':
        '{prof} {rank}: gather the reagents of the next recipes',
    'aucun métier capturé':
        'no profession captured',
    '\n**Dans ton journal pour ce donjon** : {list}':
        '\n**In your log for this dungeon**: {list}',
    'finir *{quest}* (niv. {n}) → {pick}':
        'finish *{quest}* (lvl {n}) → {pick}',
    'Familier : {name} niv. {level}, {mood}':
        'Pet: {name} lvl {level}, {mood}',
    ' (repos : {n})':
        ' (rested: {n})',
    'rends ta quête terminée ({where})':
        'turn in your completed quest ({where})',
    'rends tes {n} quêtes terminées ({where})':
        'turn in your {n} completed quests ({where})',
    ', dont {n} avec une amélioration':
        ', {n} of them with an upgrade',
    'Détail : gear, quests, professions, pet ; overview detail:complet pour tout.':
        'More: gear, quests, professions, pet; overview detail:complet for everything.',
    'Vides : {list} (vide ne veut pas dire faible : rien à conseiller sans objet précis).':
        'Empty: {list} (empty is not weak: nothing to advise without a named item).',
    ' — source à vérifier':
        ' — source to check',
    "Objets de la base pas forcément obtenables : « source non répertoriée » = vérifier où il tombe avant de l'annoncer. Maîtrises d'armes et d'armures selon Classic.":
        'DB items are not always obtainable: "source not listed" = check where it drops before naming it. Weapon and armor proficiencies as in Classic.',
    '(tu en as {n})':
        '(you have {n})',
    "Plusieurs résultats : ouvre la fiche avec l'outil indiqué (item, quests, npc, dungeon).":
        'Several results: open the sheet with the tool shown (item, quests, npc, dungeon).',
    ' · nourriture en sacs : {list}':
        ' · food in bags: {list}',
    ' · aucune nourriture adaptée en sacs ({diet})':
        ' · no matching food in bags ({diet})',
    'Verdict :':
        'Verdict:',
    ' ; et {n} autres':
        '; and {n} more',
    ' · faisable maintenant':
        ' · can craft now',
    '- Niveau des quêtes du donjon : {a}-{b} [Forever · QuestieDB]':
        '- Dungeon quest levels: {a}-{b} [Forever · QuestieDB]',
    'Dans tes sacs : **{name}** ×{n}':
        'In your bags: **{name}** ×{n}',
    'Note : **{title}** ({date}, {cert})':
        'Note: **{title}** ({date}, {cert})',
    '**{name}** déjà dans tes sacs → {verdict}':
        '**{name}** already in your bags → {verdict}',
    "- Quêtes à prendre avant d'y aller : {list}":
        '- Quests to pick up before going: {list}',
    'Quête de ton journal : **{title}** ({state})':
        'Quest in your log: **{title}** ({state})',
    'à rendre':
        'ready to turn in',
    'en cours':
        'in progress',
    '{badge} build {build}':
        '{badge} build {build}',
    # v0.8 — verdicts talents et donjon
    "1 point de talent à dépenser": "1 talent point to spend",
    "{n} points de talent à dépenser": "{n} talent points to spend",
    "aucun point de talent libre pour l'instant": "no free talent point for now",
    "{name} : quêtes niv. {a}-{b}, toi {lvl} : encore tôt, monte un peu avant":
        "{name}: quests level {a}-{b}, you {lvl}: a bit early, level up first",
    "{name} : quêtes niv. {a}-{b}, toi {lvl} : facile, surtout pour les quêtes":
        "{name}: quests level {a}-{b}, you {lvl}: easy, mostly for the quests",
    "{name} : quêtes niv. {a}-{b}, toi {lvl} : à ta portée, en groupe de 5":
        "{name}: quests level {a}-{b}, you {lvl}: within reach, with a group of 5",
    "{name} : donjon de groupe, vérifie le niveau conseillé avant d'y aller":
        "{name}: group dungeon, check the advised level before going",
    "aucune quête à prendre ici pour ton niveau": "no quest to pick up here for your level",
    "1 quête à prendre": "1 quest to pick up",
    "{n} quêtes à prendre": "{n} quests to pick up",
    'Aucun PNJ ni objet « {name} » dans QuestieDB, la mémoire des quêtes vues ou le cache du client (nom dans la langue du jeu ou en anglais).':
        'No NPC or object "{name}" in QuestieDB, the quest memory or the client cache (name in the game language or in English).',
    '\n**Vues en jeu, absentes de QuestieDB** :':
        '\n**Seen in game, missing from QuestieDB**:',
    '\n**Hors QuestieDB** (vus en jeu ou dans le cache du client) :':
        '\n**Outside QuestieDB** (seen in game or in the client cache):',
    '[Forever · observé en jeu]':
        '[Forever · seen in game]',
    '[Forever · cache du client]':
        '[Forever · client cache]',
    'Quête vue en jeu : **{name}** (id {id}) → quests questId:{id}':
        'Quest seen in game: **{name}** (id {id}) → quests questId:{id}',
    'carte {id}':
        'map {id}',
    'en instance':
        'in an instance',
    'Quête inconnue : ni dans ton journal, ni vue en jeu, ni dans QuestieDB, ni sur Wowhead. Vérifie le titre (langue du jeu) ou donne son questId ; sinon mémoire (search), puis web.':
        'Unknown quest: not in your log, not seen in game, not in QuestieDB, not on Wowhead. Check the title (game language) or give its questId; otherwise research notes (search), then the web.',
    'niveau {level}':
        'level {level}',
    '- Point sur la carte du jeu (à rendre)':
        '- Point on the game map (turn-in)',
    '- Point sur la carte du jeu (objectif)':
        '- Point on the game map (objective)',
    ', niv. {level}':
        ', lvl {level}',
    '**{name}** (PNJ {id})':
        '**{name}** (NPC {id})',
    '- Proposée par : {who}':
        '- Offered by: {who}',
    '- Cités dans le texte (probable) : {list}':
        '- Named in the text (likely): {list}',
    '- Lieux cités : {list}':
        '- Places named: {list}',
    '- Texte : « {text} »':
        '- Text: "{text}"',
    '(probable)':
        '(likely)',
    '- Point de rendu (jeu) : {where}':
        '- Turn-in point (game): {where}',
    '  - objectif {n} avancé en jeu ici : {where}':
        '  - objective {n} progressed here in game: {where}',
    '- Point sur la carte du jeu : {where}':
        '- Point on the game map: {where}',
    "Donneur et receveur pas encore vus en jeu : l'addon (1.4) les note au prochain dialogue. « Probable » = rapproché par le nom cité dans le texte.":
        'Quest giver and turn-in NPC not seen in game yet: the addon (1.4) records them at the next dialogue. "Likely" = matched by the name in the quest text.',
    'donneur : **{name}**':
        'giver: **{name}**',
    'à rendre à **{name}**':
        'turn in to **{name}**',
    '- Donne : {list}':
        '- Gives: {list}',
    '- Reçoit : {list}':
        '- Takes: {list}',
    " (niv. {n} : il n'en veut plus)":
        " (lvl {n}: your pet won't eat it any more)",
    " (niv. {n} : peu efficace)":
        " (lvl {n}: not very effective)",
    "- Points de dressage = niveau × (loyauté − 1) = {lvl} × {k} = {n}":
        "- Training points = level × (loyalty − 1) = {lvl} × {k} = {n}",
    " (loyauté au maximum)":
        " (loyalty maxed)",
    " ; +{n} par rang de loyauté gagné":
        "; +{n} per loyalty rank gained",
    "- Gardés pour une quête du journal (ne les donne pas) : {list}":
        "- Kept for a quest in your log (don't feed them): {list}",
    "\n**Pour tes quêtes en cours** : {list}":
        "\n**For your current quests**: {list}",
    "**Objets de quête qu'aucun objectif du journal ne cite** (à rendre, à utiliser ou début de quête : vérifie avant de jeter) : {list}":
        "**Quest items no objective in your log mentions** (to hand in, to use or quest starters: check before deleting): {list}",
    'Intelligence comptée en départage seulement : Visée minutieuse {r}/5 la convertit en PA distance, coefficient Forever non vérifié [Forever · probable]':
        'Intellect only used as a tie-breaker: Careful Aim {r}/5 turns it into ranged attack power, Forever coefficient not verified [Forever · probable]',
    'stats sans effet pour ta classe ({stats})':
        'stats with no effect for your class ({stats})',
    '**Butin des boss** [Forever · QuestieDB] — listes de Classic reprises par QuestieDB, à confirmer en jeu :':
        '**Boss loot** [Forever · QuestieDB] — Classic lists taken over by QuestieDB, to be confirmed in game:',
    # donjons Forever : guide sourcé (donjons.json), verdict au niveau requis
    "**Butin et mécaniques par boss** [Forever · {src}] — objets lus dans la base locale (stats exactes), à confirmer en jeu :":
        "**Loot and mechanics per boss** [Forever · {src}] — items read from the local database (exact stats), to be confirmed in game:",
    "  - {name} (id {id}) — absent de la base locale":
        "  - {name} (id {id}) — not in the local database",
    "  - {name} ({slot}, {quality}, niv. {req}, id {id}) — {stats}":
        "  - {name} ({slot}, {quality}, lvl {req}, id {id}) — {stats}",
    "Source : {url}":
        "Source: {url}",
    "au niveau {n} : ":
        "at level {n}: ",
    "guide {host} du {date}, {cert}":
        "{host} guide of {date}, {cert}",
    "- Quêtes du donjon [Forever · {src}] (nom anglais du guide quand le titre en jeu n'est pas connu) :":
        "- Dungeon quests [Forever · {src}] (English name from the guide when the in-game title is unknown):",
    " (dans ton journal)":
        " (in your log)",
    "Objet de donjon : **{name}** ({en}, id {id}) — {dungeon}, {boss} → item itemId:{id}":
        "Dungeon item: **{name}** ({en}, id {id}) — {dungeon}, {boss} → item itemId:{id}",
    '- Source [Forever · QuestieDB] : {src}':
        '- Source [Forever · QuestieDB]: {src}',
    '  - {name} ({slot}, niv. {req}) — {stats}':
        '  - {name} ({slot}, lvl {req}) — {stats}',
    ' (+{n} autres)':
        ' (+{n} more)',
    '- **Problème connu** (au {date}) : {problem} ({status})':
        '- **Known issue** (as of {date}): {problem} ({status})',
    '- Titre dans ton jeu : {name}':
        '- Title in your game: {name}',
    'butin courant ({n} PNJ)':
        'common drop ({n} NPCs)',
    'récompense de quête : {title}':
        'quest reward: {title}',
    ' (niv. {lvl})':
        ' (lvl {lvl})',
    '… (section coupée : {n} ligne(s) de plus dans le fichier)':
        '… (section cut: {n} more line(s) in the file)',
    "Récompenses : pas capturées pour ce perso (addon antérieur à 1.2), donc pas de notation possible : synchronise en jeu avec l'addon à jour. Objectifs : quests detail:normal ; une quête : quests quete:<titre>.":
        'Rewards: not captured for this character (addon older than 1.2), so no rating possible: sync in game with the current addon. Objectives: quests detail:normal; one quest: quests quete:<title>.',
    "- Quêtes à prendre avant d'y aller (début de chaîne compris) :":
        '- Quests to pick up before going (chain start included):',
    'Plusieurs résultats : ouvre celui qui convient avec la commande indiquée après la flèche.':
        'Several results: open the right one with the command after the arrow.',
    'Connaissance Forever : **{title}** → search texte:"{title}" type:connaissance':
        'Forever knowledge: **{title}** → search texte:"{title}" type:connaissance',
    '[Forever · base locale] table LevelExperience du client':
        '[Forever · local DB] client LevelExperience table',
    "[Classic · probable] table de Classic Era, base locale sans table d'XP (reconstruis-la)":
        '[Classic · probable] Classic Era table, local DB has no XP table (rebuild it)',
    "**XP jusqu'au niveau {t}** : {n} XP {badge}.":
        '**XP to level {t}**: {n} XP {badge}.',
    "**Rien pour toi en dégâts : {stats} sans effet pour ta classe ; garde l'objet équipé.**":
        '**Nothing for your damage: {stats} has no effect for your class; keep the equipped item.**',
    "**Équivalent : aucune différence chiffrable entre les deux ; garde l'objet équipé.**":
        '**Equivalent: no measurable difference between the two; keep the equipped item.**',
    ' (Visée minutieuse {r}/5, effet non chiffré [Forever · probable])':
        ' (Careful Aim {r}/5, effect not quantified [Forever · probable])',
    '**Équivalent en dégâts, léger avantage au nouvel objet : {what}.**':
        '**Equal damage, slight edge to the new item: {what}.**',
    "**Équivalent en dégâts, léger avantage à l'objet équipé : {what} pour le nouveau.**":
        '**Equal damage, slight edge to the equipped item: {what} for the new one.**',
    "**XP jusqu'au niveau {t}** : déjà atteint (niveau {l}).":
        '**XP to level {t}**: already reached (level {l}).',
    "**XP jusqu'au niveau {t}** : table connue seulement jusqu'au niveau {r} {badge}.":
        '**XP to level {t}**: table only known up to level {r} {badge}.',
    '- Détail : {left} pour finir le niveau {l}, puis {rest} pour les niveaux {a} à {b}.':
        '- Breakdown: {left} to finish level {l}, then {rest} for levels {a} to {b}.',
    '- Attention : ton jeu demande {a} XP pour ce niveau, la table {b} : écart à signaler.':
        '- Warning: your game asks {a} XP for this level, the table {b}: mismatch worth reporting.',
    "- XP reposée en réserve : {n} (double l'XP des monstres jusqu'à épuisement).":
        '- Rested XP banked: {n} (doubles mob XP until used up).',
    'niveau_cible attend un nombre (ex. 40).':
        'niveau_cible expects a number (e.g. 40).',
    'déjà porté ({worn}) ; un 2e exemplaire en {slot} : {verdict}':
        'already worn ({worn}); a 2nd copy in {slot}: {verdict}',
    'déjà porté ({slot})':
        'already worn ({slot})',
    '≈{n} (estimé)':
        '≈{n} (estimated)',
    ' — **portable au niveau {n}**':
        ' — **wearable at level {n}**',
    ' (niveau de ton journal ; {n} dans QuestieDB, sans doute ajusté par Forever)':
        ' (level from your quest log; {n} in QuestieDB, probably adjusted by Forever)',
    'Dans ton journal : **{title}**':
        'In your quest log: **{title}**',
    "- **Chaîne d'harmonisation** (par personnage) [Forever · QuestieDB] :":
        '- **Attunement chain** (per character) [Forever · QuestieDB]:',
    '  - {faction} : {n} étapes environ. Départ : {start}. Aboutit à *{end}* (id {id}){done}':
        '  - {faction}: about {n} steps. Start: {start}. Ends with *{end}* (id {id}){done}',
    '- Rien de mieux à ton niveau actuel.':
        '- Nothing better at your current level.',
    '\n**Plus tard** (niveau {a} à {b})':
        '\n**Later** (level {a} to {b})',
    "{name} n'a pas {prof} : recettes génériques ci-dessous ; pour un autre perso du compte, characters action:activer":
        "{name} doesn't have {prof}: generic recipes below; for another character on the account, characters action:activer",
    'vise **{item}** au niveau {n} ({slot}, {gain})':
        'aim for **{item}** at level {n} ({slot}, {gain})',
    '{prof} : récolte les composants des prochaines recettes':
        '{prof}: gather the materials for the next recipes',
    ' ✔ faite':
        ' ✔ done',
    'ce perso':
        'this character',
    # worldmap.py
    'Cartes indisponibles : {err}':
        'Maps unavailable: {err}',
    'Point illisible : {p}. Attendu : {{x, y, label}} ou « /way x y ».':
        'Unreadable point: {p}. Expected: {{x, y, label}} or "/way x y".',
    'Coordonnées hors carte : {x} {y} (0 à 100).':
        'Coordinates off the map: {x} {y} (0 to 100).',
    '{n} points : {max} au plus par carte.':
        '{n} points: {max} at most per map.',
    'Zone inconnue des cartes du client : {zone}.':
        'Zone not found in the client maps: {zone}.',
    "Précise la zone de ces /way (nom ou uiMapID) : sans elle, le repère serait posé sur la carte où se trouve le perso.":
        "Give the zone of these /way (name or uiMapID): without it, the marker would land on the map where the character is.",
    'Indique la zone (nom ou uiMapID).':
        'Give the zone (name or uiMapID).',
    'Carte de {zone} absente du client.':
        'No map for {zone} in the client.',
    'Carte : {zone} (uiMap {id}) · {w}×{h} · [Forever · client]':
        'Map: {zone} (uiMap {id}) · {w}×{h} · [Forever · client]',
    'Repère : ':
        'Marker: ',
    'Point bleu : ta position ({x:g} {y:g}).':
        'Blue dot: your position ({x:g} {y:g}).',
    'Fichier : {path}':
        'File: {path}',
    # XP des quêtes (questdb_tools.py)
    "ces {n} quêtes":
        "these {n} quests",
    " · ≈ {xp} XP":
        " · ≈ {xp} XP",
    " · {xp} XP":
        " · {xp} XP",
    "XP du jeu":
        "game XP",
    "XP du jeu pour {r}, estimée pour {e} [Classic · estimation]":
        "game XP for {r}, estimated for {e} [Classic · estimate]",
    "estimation [Classic], ±30 %":
        "[Classic] estimate, ±30%",
    "\n**XP** : {what} {op} **{xp} XP**, soit {pct} % d'un niveau {level} ; niveau atteint ≈ **{new}** (+{frac} %) — {src}.":
        "\n**XP**: {what} {op} **{xp} XP**, i.e. {pct}% of a level {level}; level reached ≈ **{new}** (+{frac}%) — {src}.",
    "ces {n} rendus":
        "these {n} turn-ins",
    "ce rendu":
        "this turn-in",
    "tout le journal ({n} quêtes, une fois finies)":
        "the whole log ({n} quests, once finished)",
    "\n**Grises, à abandonner** (peu d'XP, place dans le journal) : {list}.":
        "\n**Grey, abandon them** (little XP, log space): {list}.",
}
