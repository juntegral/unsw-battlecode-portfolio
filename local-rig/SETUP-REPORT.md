# Setup report
Status: workspace prepared; real-game proof INCOMPLETE because this session's sandbox denies setpriority.

- `opponent/`: only the requested compiled executable, copied as `bot`; no opponent source was read or copied.
- `engine/`: allowed `venv` symlink to installed unswbc 1.2.7, native-match driver, usage/limitations README.
- `maps/dev/`: 8 held-out maps (224–3477 cells); `maps/eval/`: 16 disjoint held-out maps (170–2976 cells).
- Both sets mix sizes and shape families; `maps/README.md` lists dimensions, cells, and starting dragons by side.
- `docs/`: engine-shipped C/C++/Python examples/helpers, package README/metadata, license, runner/turn/API source and viewer README.
- `starter/`: unchanged engine C++ starter/helper, native `bot`, `build.sh`, README; build succeeded.
- `tools/`: replay decoder/show.py, directory compiler, batch planner/summary, and offline verification script.
- `proof/`: three failed-command logs/JSON, guard outcomes, protocol output, and clearly labelled synthetic replay/summary fixtures.
- `.locks/`: two shared flock slots; `.tmp/`: local temporary directory. Root: play.sh, batch.sh, guard.py, settings.json, README.md.

Exact commands run from this directory:
```sh
./starter/build.sh starter
./play.sh starter opponent/bot maps/dev/sqheld_open_small_90018.map 1 proof/starter-side-0
./play.sh opponent/bot starter maps/dev/sqheld_open_small_90018.map 1 proof/starter-side-1
./play.sh opponent/bot opponent/bot maps/dev/sqheld_open_small_90018.map 1 proof/opponent-self
PYTHONDONTWRITEBYTECODE=1 ./engine/venv/bin/python3 -B tools/check_setup.py
python3 -B tools/show.py proof/synthetic.replay --round 1
```
Proof outcomes (no winner/result lines exist because no games launched):
1. Starter side 0: BLOCKED, exit 1, before game launch.
2. Starter side 1: BLOCKED, exit 1, before game launch.
3. Opponent self-play: BLOCKED, exit 1, before game launch.
All three printed `nice: setpriority: Operation not permitted` and `game failed: [Errno 1] Operation not permitted` to stderr.
One-game duration: unavailable; zero actual games ran. The scripts retain nice -n 15 and stop if priority cannot be set.

Guard samples: allowed play.sh command => exit 0; Read of `~/meow-dev/notes.txt` => exit 2; `xxd opponent/bot` => exit 2.
Exact hook inputs/reasons are in `proof/guard-tests.json`; all forbidden strings, inspection commands and network patterns also passed checks.
settings.json registers guard.py for all tools by absolute path; a later Claude Code session must load that settings file.
Offline checks passed: starter chose the only open legal direction; map counts/disjointness; synthetic replay growth/split/death/rounds/edges; batch side/seed planning and summaries.
Five lock-only processes exercised the actual shared slots; peak holders was 2. No batch or extra games ran.
Syntax, engine version, unchanged starter provenance, executable permissions, and hook registration checks passed.
Limitations: the installed engine ships documented helpers and engine code but no separate prose rulebook; only its shipped materials were included, with no private/older notes substituted.
Native games do not meter the judge's WebAssembly CPU points; the permitted engine symlink depends on the existing installation on this Mac.
To finish the required proof, run the three unchanged play.sh commands in a local session that permits nice -n 15; then record results and timing.
All workspace writes stayed here; no network/server calls or posting occurred. This report was written last.
