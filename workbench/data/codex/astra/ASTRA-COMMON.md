# Analyst notes (read fully first)

You analyse replays of a game bot for a team with a deadline at 15:00 KST today. One live bot is improved version by version;
your report decides a change that goes live within the hour, so be exact and say what you did not check.

## Game
Two sides of "dragons" (snakes) on a torus grid with kelp walls and portals. Dragons eat pearls to grow, split in two, pay segments
to sprint, and a head rammed into an enemy head kills both. Each dragon sees a 7 by 7 view plus what the side shares.
Who wins: the side whose QUEEN (lowest starting id) is longer at the end; a dead queen counts 0; then the longest dragon; then total
length; a side with no dragons loses at once. Rules: `~/meow-redteam/README.md`, `~/meow-redteam/docs/`.

## Bot
Our team is 1119. Live source with its switch values set: `data/online/smoke/one5-bot/main.cpp` (one C++ file, about 6,400 lines).
Versions tonight: one1 (22:29), one2 (23:02), one3 (23:36), one4 (00:10), one5 (00:49 KST). Differences are listed in
`docs/SESSION-STATE.md` (grep "라이브 = one"). An earlier analyst's full report on these games: `data/analysis/ladder/dossier/diag-one1.md`
(14 sections; read the first lines of each section that touches your question, do not repeat its counts).

## Data (read-only)
- Online sets, 15 maps each, our bot against one opponent: `data/online/smoke/<label>-old/` with state `data/online/smoke/<label>.json`.
  Labels: one1-w1, one2-w1, one3-w1, one4-w1, one5-w1 (against WeHaveQuizzes, "WHQ", rank 12); one1-d1, one3-d1, one4-d1, one5-d1
  (against dev test 1, rank 9). one5 sets arrive during the next 30 minutes; use what is there.
- Ranked battles against whoever challenges us: `data/online/live-one1/b<battle id>/` (index `live-one1/index.txt`; which build played is
  the bot id in the replay or the time: one2 from 23:02, one3 23:36, one4 00:10, one5 00:49 KST).
- Local games (same replay format): `~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/game.replay` + `result.txt`; the arm is the
  side named in the folder. `m3hunt` is a copy of old main that hunts queens, `m3base` is old main.
- Readers and counters to import, not copy: `data/analysis/ladder/dossier/online/label_report.py` (per-label report, replay reader,
  per-game rows), `data/analysis/ladder/dossier/work/o1_*.py` (tonight's scripts: growth, stops, pearls, turn classes, local arms),
  `work/tq2_*.py` (queen: company, chases, depth), `work/tr_*.py` (rams), `dossier/local/replay_format.py`.

## Rules
- Write only under your own folder `data/codex/astra/<your name>/` (scripts, notes, `report.md`). No network, no posts, no games.
  You may compile a copy of the bot inside your folder to check that a proposed change builds (`c++ -std=c++20 -O2`), nothing else.
- Count from replays; mark every statement [M] measured, [C] read from the code with line numbers, or [E] inferred.
  Give game ids and rounds for two or three replay moments per finding. Never state a number you did not compute.
- The qualifier is played on maps nobody has seen: no rule keyed to a map name or a size table.
- A card = one concrete rule ("when X, dragon Y does Z"), the lines in `one5-bot/main.cpp` where it goes, whether an existing
  constant or switch already does it, the replay count that will show it works, and what would show it is wrong. At most two cards.
  "No card" is a valid answer and better than a weak one.

## Report: `data/codex/astra/<your name>/report.md`, under 450 words plus tables
First three lines: the finding, the card (or "no card"), how sure. Then the tables, the replay moments, what you did not check.

## Added 01:16 KST
- New set `one5-c1` (one5 against Cache me outside, team 952, rank 13; 6 wins of 15): `data/online/smoke/one5-c1-old/`. From now on
  the team judges versions on WHQ and Cache me outside; dev test 1 is no longer a yardstick (too strong to separate builds, and
  suspected of map knowledge). Use dev test 1 sets as a second sample only.
- Your folder may hold files from a run that was cut off by a usage limit. Reuse what is there; do not start over.
