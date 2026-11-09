# Known issues in this repository

Problems found while revising this portfolio, each checked against the files on 2026-11-09. The archived source
(`card-loop`, `workbench`, `local-rig`, `final-bot`, `first-bot`, `lineage-loop`) is kept as it ran, so none of the
code issues below were fixed here. Changes to the record are listed in [CHANGELOG.md](CHANGELOG.md).

## Code

| File and line | What | Effect | Why not fixed |
|---|---|---|---|
| [`workbench/tools/meow_guard.py`](../workbench/tools/meow_guard.py) line 12 | `MEMORY = Path('~/.claude/projects/...')` is never passed through `expanduser`. `roots()` (line 16) returns it as is, and `safe_path()` (line 33) resolves it to a literal `~` folder under the current directory | The memory folder never matches the allowed roots, so a read-only session is refused paths in it that the list meant to allow. The check fails closed | Archived source is kept as it ran |
| [`card-loop/work/loop/guard.py`](../card-loop/work/loop/guard.py) lines 27, 46 and 56 | The credential block matches only `docs/api.txt` and `docs/discord.txt` | A key kept under another file name would not be stopped by this check. The file's own docstring calls it "defence in depth, not an OS sandbox" | Archived source is kept as it ran |
| [`final-bot/server_bot.py`](../final-bot/server_bot.py) line 55 | It copies `main.cpp`, `helper.hpp`, `sonar_codec.hpp` and `bot.toml` from `--src`. `final-bot/` holds only `main.cpp`. `sonar_codec.hpp` is at [`card-loop/mybot2/sonar_codec.hpp`](../card-loop/mybot2/sonar_codec.hpp), a `bot.toml` is at [`workbench/data/online/smoke/one21-bot/bot.toml`](../workbench/data/online/smoke/one21-bot/bot.toml), and `helper.hpp` is the organisers' file and is not published | The uploaded source cannot be regenerated from this repository alone, even with `--no-compile`: it stops at the copy step. The defaults (`--src mybot2`, `--profile work/server_profile.txt`) name the team repository's layout, not this one | The files are not added: `helper.hpp` belongs to the organisers, and `final-bot/` is a team artifact |

## Missing project files

| What | Fact | Effect | Why not added |
|---|---|---|---|
| License | No `LICENSE` file is tracked | No reuse rights are granted by this repository | `final-bot/` is a team artifact, so the grant is not mine alone |
| Dependency list | No `requirements*.txt`, `pyproject.toml` or `package.json` is tracked. 1,967 `.py` and 642 `.js` files are; 3 import `discord` and 1 imports `numpy` | A reader must find the dependencies from the imports | Archived source is kept as it ran |
| CI | No workflow under `.github/`. Only `card-loop/.github/ISSUE_TEMPLATE/` exists | The 35 `test_*.py` files are not run automatically | Their fakes for Discord, GitHub and model calls assume the original machine's layout |

Provenance: compiled by an AI session under my direction from the records linked on this page; quotes are verbatim.
