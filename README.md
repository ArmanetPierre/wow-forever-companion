# WoW Forever Companion

An AI companion for **World of Warcraft: Forever**, inside
[Claude Code](https://claude.com/claude-code). Ask your questions in a window next to the
game; it answers **in your language** (English or French) by combining **your character's
real state** (captured in game by an addon) with reliable sources about Forever.

> *[Version française](README.fr.md).* Works with an English or French game client: item,
> quest and zone names stay as your client shows them; answers follow the language of your
> question.

```
Brannok · Dwarf Hunter 25 · Loch Modan · data from 4 min ago

Yes, but not right away: about +2.4 DPS (+5.5%) once your Crossbows skill is up.

|                           | Double-barreled Rifle | Crossbow             |
|---------------------------|-----------------------|----------------------|
| Weapon DPS                | 13.3                  | 15.2                 |
| Bonus                     | +3 Agi, +3 Str        | +12 ranged AP        |
| Ranged DPS (white hits)   | 43.1                  | ≈ 45.5               |

- Your Crossbows skill is 1/125: many shots will miss at first.

Based on: gear and stats (addon), compare_item · Certainty: likely
```

## What's in the project

| Part | Role |
|---|---|
| **ForeverScribe** addon | captures your character's state in game: identity, XP, position, stats, gear, talents, spells, quests, professions and recipes, pet, bags, bank, gold, reputations… |
| **forever-companion** Claude Code plugin | the `forever-guide` agent, 8 skills, a Forever knowledge base and the MCP server |
| **forever** MCP server | reads the addon captures and serves them to the agent (26 tools); keeps your profile and journal up to date; keeps the research memory |
| **Local game database** (optional) | items, stats, armor, DPS, recipes, dungeons and quests read from *your* Forever client, to answer without searching the web |

Skills: `forever-quetes` (quests), `forever-leveling`, `forever-metiers` (professions),
`forever-talents`, `forever-donjons` (dungeons), `forever-equipement` (gear),
`forever-familier` (hunter pet), `forever-profil` (characters and notes).

## Requirements

- World of Warcraft: Forever (English or French client)
- [Claude Code](https://claude.com/claude-code)
- Python 3.9 or later (already on macOS and Linux; install it on Windows)

## Installation

**1. The addon**

```bash
git clone https://github.com/ArmanetPierre/wow-forever-companion.git
cd wow-forever-companion
addon/install.sh                 # macOS / Linux (finds the game folder)
```

Windows (PowerShell): `powershell -ExecutionPolicy Bypass -File addon\install.ps1`.
Game folder not found: add `--wow-path "/path/to/World of Warcraft/_forever_"`
(`-WowPath` on Windows). Without the script: copy `addon/ForeverScribe` into
`World of Warcraft/_forever_/Interface/AddOns/`.

Then **fully quit and restart the game**, and tick ForeverScribe in the AddOns list (plus
"Load out of date AddOns" if needed).

**2. The plugin**, in Claude Code:

```
/plugin marketplace add ArmanetPierre/wow-forever-companion
/plugin install forever-companion@wow-forever-companion
```

**3. Your player folder**: your data lives here, outside the project.

```bash
mkdir -p ~/WowForever && cd ~/WowForever && claude
```

Always start Claude Code from this folder to talk to your companion. Copy the template
[`perso.example/CLAUDE.example.en.md`](perso.example/CLAUDE.example.en.md) there as
`CLAUDE.md` and fill in your first name and character (French template:
[`perso.example/CLAUDE.md`](perso.example/CLAUDE.md)). It tells Claude to load all the
`forever` tools in one call at session start (`ToolSearch` with the query `+forever`), to
check the research memory before the web and to follow the answer charter.

## Usage

1. In game, sync: **Ctrl+Shift+S**, `/sync` or the scroll button near the minimap (short
   loading screen; refused in combat). Logging out also syncs. If the key binding does
   nothing: `/scribe touche`.
2. In Claude Code, ask your question:
   - "What should I do now?"
   - "Which quests can I turn in here?"
   - "Should I take this crossbow: 24-37, 15.2 DPS, +12 ranged AP?"
   - "My pet is unhappy, what do I do?"
   - "How do I level Leatherworking from 106 to 150?"
   - "Rate my gear" (quest rewards included)

Each answer starts with your character and the data age, gives the verdict first, then the
details, the provenance ([Forever], [Classic], [Retail]) and the certainty. If your
question depends on your current state and the data is old, the agent suggests syncing.

Main agent tools: `get_overview` (everything in one call), `get_quest_rewards` (rewards of
your logged quests ranked for your character: armor and weapon proficiency, estimated gain,
quests to turn in that give an upgrade), `compare_item`, `get_equipment`, `get_inventory`,
`get_quests`, `get_talents`, `get_professions`, `get_pet`, `get_progress`… Every tool takes
an optional `lang` (`en` / `fr`) for its labels.

**Research memory.** When the agent had to search for a while ("are there helmets at my
level?"), it saves the answer with `save_knowledge` in `~/WowForever/connaissances/`: one
dated Markdown file per topic, with sources and certainty. Next time, `search_knowledge`
answers in one call. These are plain text files: read, fix or delete them freely.

Other in-game commands: `/scribe` (capture + summary), `/scribe status` (state of each
area), `/scribe bouton` (show/hide the button), `/scribe help`.

## Language

- **Answer language**: the language of your question. To force it everywhere (including
  the `profil.md` and `journal.md` files generated by the sync), add
  `"answer_language": "en"` (or `"fr"`) to `perso/config.json`. Without it, generated files
  follow the character's client language.
- **Game language**: your client's (enUS, frFR…). Item, quest, zone and NPC names stay as
  you see them in game, even when you ask in the other language.
- The plugin's knowledge base (`knowledge/`) is written in French; the agent translates it
  on the fly.

## Your data

- **Everything stays on your computer.** The addon writes a game file; the MCP server reads
  it locally. The information only goes to your own Claude session when you ask a question.
- No login credentials are read or stored.
- Data folder, in this order: `FOREVER_DATA_DIR` variable, else `perso/` in the folder where
  you start Claude Code, else `~/WowForever/perso`.

```
~/WowForever/
├── CLAUDE.md                    companion instructions (template: perso.example/)
├── connaissances/               research memory (FOREVER_KNOWLEDGE_DIR to move it)
└── perso/
    ├── config.json              game folder, accounts, active character, answer_language
    └── <FirstName>/<Character>-<Region>/
        ├── profil.md            automatic section + your notes
        ├── objectifs.md         your goals (yours to write)
        ├── journal.md           your notes + automatic journal
        ├── etat.json            latest capture
        └── historique/          one snapshot per day
```

## Several characters, several players

- All your characters are tracked: the agent answers for the last one played, or say "I'm
  playing my mage". Log in each character once with the addon enabled.
- Several WoW accounts on the same computer: each account is linked to a first name (the
  agent asks you).
- Your friends install the project on their machine: their data stays with them.

## Building the game database

Optional but recommended: the agent then finds gear upgrades (`find_upgrades`), item
sheets, a profession's recipes and dungeon bosses on its own, without web searches. The
database is built **on your machine, from your client**; nothing is downloaded from a game
website and the game folder is never modified.

```bash
python3 tools/gamedata/build_db.py
```

- Options: `--wow "<World of Warcraft folder>"` if the game is not found,
  `--data-dir <folder>` (default `~/WowForever`), `--locale enUS`, `--force`.
- Language: your client's, detected automatically (`Config.wtf`, else `.build.info`);
  `--locale` forces another installed language.
- Start the game at least once before: Forever's hotfixes (new or reworked items) are in its
  `DBCache.bin` cache. Run the command again after a game update; it does nothing if nothing
  changed.
- The first time, it downloads from GitHub and compiles
  [CascLib](https://github.com/ladislav-zezula/CascLib) (reads the game storage, MIT) and
  the [WoWDBDefs](https://github.com/wowdev/WoWDBDefs) definitions (table layouts). You need
  `git`, `cmake` and a C compiler (macOS: `xcode-select --install` then `brew install cmake`;
  Linux: `apt install git cmake build-essential`). On Windows, the command prints the steps
  to build CascLib with CMake and Visual Studio Build Tools.
- **Quests and NPCs** (giver, turn-in, objectives and where, `/way`, chain, quests available
  in a zone, where an NPC is): the build then downloads the Forever data of
  [QuestieDB](https://github.com/Questie/QuestieDB) (community database of the Questie addon)
  at a pinned revision and merges it into your database (tools `get_quest_info`,
  `find_quests`, `find_npc`). These files are **not** part of this repository (no declared
  licence; Questie is GPLv3) and are only read as data. `--no-questie` skips it; to add it
  to an existing database: `cd plugins/forever-companion && python3 -m gamedata.questie`.
- Result: `~/WowForever/gamedata/forever-<locale>.sqlite`, e.g. `forever-enUS.sqlite`
  (≈ 17 MB with QuestieDB, a few seconds); dependencies in `~/WowForever/gamedata/.cache/`.
  Schema: [docs/schema-gamedb.md](docs/schema-gamedb.md).
- Limits: dungeon loot and item origin (drop, quest, vendor) are not in the client files;
  the required rank of recipes is estimated.

## Windows and Linux

- **Windows**: install Python (Microsoft Store, which provides `python3`). With the
  python.org installer (`python`/`py`), declare the server by hand:
  `claude mcp add forever -- py "<plugin path>\mcp\server.py"`.
- **Linux**: the game runs through Wine/Lutris; the addon works normally. If the game
  folder is not found:
  `python3 plugins/forever-companion/mcp/sync.py --wow "/path/to/World of Warcraft"`.

## Troubleshooting

| Problem | Fix |
|---|---|
| The addon does not show up | quit and restart the game (`/reload` does not load a new addon); otherwise reinstall with `--copy` |
| "No known character" | log in your character, sync (Ctrl+Shift+S), check that you start Claude Code from `~/WowForever` |
| Ctrl+Shift+S does nothing | `/scribe touche`, or Options → Key Bindings → AddOns → ForeverScribe |
| Empty recipes or bank | open the profession window or the bank once, then sync |
| Game folder not found | `sync.py --wow "<game folder>"` (it is remembered afterwards) |
| "Quest rewards unknown" | update the addon (1.2 or later), restart the game once, then sync |

## Roadmap

- Questions asked directly in game (experimental)
- Local cache of reference sources
- Combat analysis (Forever's built-in damage meter)

Companion evaluation bench (replayable scenarios, criteria, budgets):
[docs/evals/](docs/evals/). Design notes: [docs/conception/](docs/conception/), data format:
[docs/schema.md](docs/schema.md), verified API: [docs/api-inventaire.md](docs/api-inventaire.md)
(design documents are in French). To contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) © 2026 Pierre Armanet. Fan project, not affiliated with Blizzard
Entertainment. World of Warcraft is a trademark of Blizzard Entertainment.
