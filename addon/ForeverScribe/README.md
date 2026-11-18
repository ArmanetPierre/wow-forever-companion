# ForeverScribe

Addon that records your character's state (identity, level, zone, stats, gear,
talents, quests, professions, pet, bags, reputations…) for the WoW Forever AI companion.
It **only reads**: no in-game actions, nothing sent over the Internet.

The data format is described in [`docs/schema.md`](../../docs/schema.md) (French).
Version française : [`LISEZMOI.md`](LISEZMOI.md).

**Client language**: works with a game client in English, French or any other language.
Messages are in French for a French client and in English otherwise. Commands accept
both languages (`key` or `touche`, `button` or `bouton`, `status` or `statut`, `help` or
`aide`). The saved data always carries language-independent keys (class tokens, item,
map, quest-tag and profession IDs…) next to the translated labels.

**Updating to 1.3.0**: this version adds the `Locales.lua` file. **Quit and restart the
game completely** (a `/reload` does not load new files).

## Installation

From the repository folder:

| System | Command |
|---|---|
| macOS / Linux | `addon/install.sh` (or `addon/install.sh --wow-path "/path/to/_forever_"`) |
| Windows | `powershell -ExecutionPolicy Bypass -File addon\install.ps1` |

If the game does not see the addon, run it again with `--copy` (macOS/Linux) or `-Copy`
(Windows).

## In-game check, step by step (5 minutes)

1. **Quit the game completely and restart it.** A `/reload` is not enough for a new
   addon to register its saved files.
2. Character selection screen → **AddOns** button: tick **ForeverScribe**.
   If it is marked "out of date", tick **Load out of date AddOns**.
3. Log in. After ~5 s the chat shows:
   `ForeverScribe: ready (19 domains captured). … /scribe help`
4. **Summon your pet** if you have one.
5. **Open each profession window** (e.g. Leatherworking) for a few seconds, then close it.
6. If you are near a bank: **open your bank** for a few seconds.
7. Type **`/scribe`**: full capture and a one-line summary.
8. Type **`/scribe status`**: every domain should be **OK**. Note the ones in
   **ERROR**, or flagged "missing function(s)" or "failed call(s)".
9. Type **`/sync`** (or press your sync key): this writes the files to disk.

## Sync for Claude

The game only writes data to disk when the interface reloads, when you log out or when
you quit. To let Claude see your current state, sync in one gesture (full capture then
reload, ~3 s loading screen):

| Gesture | How |
|---|---|
| **Key** | `/scribe key` binds **Ctrl+Shift+S** (if free). Another key: `/scribe key ALT-F12`, or **Options → Keybindings → AddOns → ForeverScribe → Sync for Claude**. |
| **Command** | `/sync` (or `/scribe sync`) |
| **Button** | the scroll icon on the minimap edge: click = sync, drag = move. `/scribe button` shows or hides it. The tooltip shows the age of the data. |
| **Automatic** | logging out and quitting the game: nothing to do. |

- **Never in combat**: the game forbids it. The addon refuses and reminds you when combat
  ends; it never reloads on its own (the game requires a gesture from you).
- The default Ctrl+Shift+S binding is declared in `Bindings.xml`, but the game only
  applies it after "Reset keybindings": use `/scribe key` once.

## Commands

| Command | Effect |
|---|---|
| `/scribe` | full capture + summary |
| `/scribe status` (or `statut`) | state of each domain (OK / error / never captured, age) |
| `/scribe help` (or `aide`) | help |
| `/sync` or `/scribe sync` | sync for Claude (capture + reload) |
| `/scribe key [KEY]` (or `touche`) | bind the sync key (default Ctrl+Shift+S, only if free) |
| `/scribe button` (or `bouton`) | show / hide the minimap button |

Captures also run on their own when something changes (2 s later, never during combat).
They stay in memory until the next `/reload`, logout or game exit: that is when the game
writes the files.

## Files written

```
WTF/Account/<ACCOUNT>/SavedVariables/ForeverScribe.lua                        (character index + quest memory)
WTF/Account/<ACCOUNT>/<REALM>/<Character>/SavedVariables/ForeverScribe.lua    (full character state)
```

**Quest memory (1.4).** While you play, the addon also notes, for the whole account, who
gives and who receives each quest, the quests an NPC offers, where objectives progress and
the quest map points (with coordinates, outside instances). It fills the gaps for quests
that exist in no downloadable database. Nothing is read in combat. `/scribe status` shows
how many quests and NPCs it knows.

## Offline test (developers)

```bash
lua addon/tests/run_capture.lua
```
Replays a full session in a simulated WoW (probe values), with a French client then an
English client. It checks the schema, checks that language-independent keys are
identical in both languages, and regenerates the examples in `addon/tests/fixtures/`
(`*.enUS.*` for the English client).
