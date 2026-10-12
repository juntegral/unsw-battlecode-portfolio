# Turn six ladder layouts into local map files

The local engine plays `.map` files like those in `~/meow-redteam/maps/dev/` and `maps/eval/`
(format: read those files, `~/meow-redteam/docs/`, and `~/meow-redteam/engine/run_game.py`).
Our ladder replays (under `data/online/`; index and per-game rows in `data/analysis/ladder/dossier/per-game.jsonl`,
parsers in `data/analysis/ladder/dossier/count_dossier.py` and `dossier/work/isl_map.py`, `au_map.py`) hold the full
starting board of each game.

## Job
For each of the six ladder layouts above 1200 cells (Islands #1, Australia #1, Around UNSW #1, Slithery Fight #1,
Schooltime #1, Schooltime #2) write one map file `data/analysis/ladder/dossier/local/maps/ladder_<slug>.map` that
reproduces the layout exactly: size, walls, wrap, portals, kelp, pearl spawn tiles with their periods and phases,
every starting dragon of both sides with its body, and anything else the format carries (unit limit, round limit).
If the original `.map` files of these layouts already exist anywhere under `~/01. Project/개인 프로젝트/`
or `~/meow-redteam/`, prefer copying them and say where they came from.

## Check (required)
For each map: parse your `.map` with the engine's own loader (the python in
`~/meow-redteam/engine/venv/bin/python3` can import what `run_game.py` imports; read-only use, do not
run games) and compare the loaded starting state with round 0 of two different ladder replays of that layout:
size, wall set, portal pairs, starting dragons, pearl tiles. Report equal / differs per item.

## Output
`data/analysis/ladder/dossier/local/maps/README.md` (30 lines or fewer): per map the size, cells, dragons a side,
source, and the check result; then anything the `.map` format cannot express. Write
`data/analysis/ladder/dossier/local/maps/done.txt` (one line) as the very last step.
Write only under `data/analysis/ladder/dossier/local/maps/`. No network, no posts, no games.
