# Black-box bot workspace

Start with `docs/README.md`, the unchanged engine helper in
`docs/engine-starters/cpp/helper.hpp`, and `starter/main.cpp`. Map inventories
and starting counts are in `maps/README.md`. `SETUP-REPORT.md` records the actual
setup checks and any limitations.

Commands from this directory:

```sh
./starter/build.sh starter
./play.sh starter opponent/bot maps/dev/sqheld_open_small_90018.map 1 runs/one-game
python3 tools/show.py runs/one-game/game.replay
python3 tools/show.py runs/one-game/game.replay --round 10
```

`play.sh <botA> <botB> <map file> <seed> <out dir>` places A on side 0 and B on
side 1, prints one result line, and preserves a replay. Bots can be native
executables or directories containing a built `bot`. Inputs and outputs must
be inside this workspace. Use a fresh output directory each time.

`batch.sh <botA> <botB> <dev|eval> <seeds> <out dir>` runs every map, every listed
seed, and both starting orders through `play.sh`, sequentially. Seeds are a
comma-separated list, such as `1,2`, or a quoted space-separated list. Results
are recorded after each game in `rows.jsonl`; final `summary.txt` and
`summary.json` report the first supplied bot's wins by map and starting side
and the way each game ended. Both scripts share the same two game lock slots.
An actual batch is intentionally not part of setup verification.

`tools/show.py` defaults to the final state. `--round 0` shows the initial
state; `--round N` shows the end of played round N, numbered from 1. It prints
the board's pearls, kelp and portal edges, both teams' bodies, and all living
dragon IDs, teams, lengths, heads, and full body coordinates.

`guard.py` reads Claude Code PreToolUse JSON on stdin; allowed inputs exit 0,
denied inputs exit 2 with a short reason on stderr. `settings.json` registers
it for all tools by absolute path. To load this profile in a later Claude Code
session, run `claude --settings settings.json` here. This file does not change
the current session's tool policy. The guard implements the brief's string
rules; it is a hook, not an OS sandbox.
