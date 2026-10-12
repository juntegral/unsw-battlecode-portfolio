# meow-redteam: local game rig and the solo bot's source lineage (archived 2026-10-10)

This folder was the local workbench for team meow (1119) in the UNSW Battlecode-style contest of 2026. It started as
a black-box test of the engine (see `README.md`, `SETUP-REPORT.md`) and became the place where the final bot was
built and tested. The contest ended on 2026-10-10. The write-up of what was learnt is in the private repo
`juntegral/unsw-swarm`, folder `docs/retro/`; the final bot as shipped is in the team repo
`forrest-gan2005/battlecode` (`mybot2/main.cpp` plus `work/server_profile.txt`).

## What is here

| Path | What it is |
|---|---|
| `play.sh`, `batch.sh`, `engine/run_game.py` | Run one local game or a batch. `run_game.py` holds the machine-wide limit on simultaneous games. |
| `maps/` | Test maps: `gx/` generated families with `INDEX.tsv`, `ladder/` the 16 ladder maps (7 rebuilt from replays, pearl supply estimated), `un2/` unseen-style families, `community/`, `dev/`, `eval/`. |
| `solo/src/solo/main.cpp` | The final source (one21). `main.cpp.pre-one*-1009` are the stages before each upload of the last day. |
| `solo/src/w-*/` | Work folders, one per candidate change, each with its own copy of the source. |
| `solo/tools/mkbots.py` | Builds a bot from a source and a list of switch values: `MKSRC=src/<dir>/main.cpp python3 tools/mkbots.py "name=CONST:value,..."`. |
| `solo/bots/<name>/main.cpp` | The exact source of every test build (source plus that build's switch values). Compiled files are not kept. |
| `solo/runs-results.tar.xz` | The result line and json of every local game (about 9,000 games), without replays. |
| `runs/`, `proof/`, `variants/`, `opponent/` | The early black-box phase: results, the compiled bots of versions v2 to v24 and the reference opponent. |

## What is not here

- Replays and engine logs of local games (about 55 GB). Local games are deterministic: the same two bots, map and seed
  give the same game, so any of them can be played again with `play.sh`.
- Compiled test bots under `solo/bots/*/bot`. Rebuild with `mkbots.py`. With every switch off the build's sha1 starts
  `92fb69564fbd`; that identity check is how each new source was shown to still contain the old program.
- Online replays (our games, ladder, top teams): attached to the release `data-2026-10-10` of `juntegral/unsw-swarm`.
