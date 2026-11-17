# Contributing

Thanks for your help! A few simple rules:

1. **No player data** in a contribution: no real SavedVariables file, account number, GUID,
   real character name or personal path. Use the fictional character Brannok and the
   fixtures in `addon/tests/fixtures/`.
2. **Run the tests** (see `CLAUDE.md`): addon, parser/sync, end-to-end server (default, then
   `--lang en` and `--client enUS`), `claude plugin validate .`.
3. **Data format**: any new captured data is described in `docs/schema.md`.
4. **Game API**: if you find out what a function returns in Forever, add it to
   `docs/api-inventaire.md`. The `ForeverProbe` addon helps check it in game (see its
   `LISEZMOI.md`).
5. **Knowledge**: a fact added to `knowledge/` has a source (link) and a certainty level.
   No source, no fact.
6. **Languages**: the companion supports English and French game clients and answers.
   - Logic never depends on a displayed name: use IDs (item class/subclass, inventory type,
     SkillLine, quality) and canonical stat keys.
   - Server text goes through `i18n.T("French source")` with its English translation in
     `mcp/i18n_en.py`; fixed labels through `i18n.L(table, key)`. `tests/test_i18n.py`
     fails if a translation or placeholder is missing.
   - In-game names (items, quests, zones, NPCs) are never translated: they stay in the
     client's language.
7. Python: standard library only. Lua: 5.1 compatible (WoW client).

Open an issue to discuss a significant change before coding it.

*Version française : les mêmes règles s'appliquent ; le contenu destiné au joueur existe en
français et en anglais, les documents de conception restent en français.*
