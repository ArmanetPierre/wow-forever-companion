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
    "Rang requis : le client Forever ne le fournit pas ; « ≈ » = estimation 5 × niveau de l'objet fabriqué (juste sur les recettes Classic vérifiées, à confirmer chez le formateur). Une recette rapporte des points tant qu'elle n'est pas grise ; ouvre la fenêtre du métier en jeu pour que l'addon capture les couleurs exactes. Les sources des recettes (formateur, marchand, butin) ne sont pas dans la base.":
        "Required rank: the Forever client does not provide it; \"≈\" = estimate 5 × item level of the crafted item (right on the verified Classic recipes, to confirm at the trainer). A recipe gives points as long as it is not grey; open the profession window in game so the addon captures the exact colours. Recipe sources (trainer, vendor, loot) are not in the database.",
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
    "\nCompte {account} ({user}) · capture du {time}":
        "\nAccount {account} ({user}) · capture of {time}",
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
}
