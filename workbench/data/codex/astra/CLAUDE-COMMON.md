# Common brief for Claude builders and analysts (10-09, last four hours before the 15:00 KST deadline)

Read `ASTRA-COMMON.md` (same folder: the game, the bot, the data, how to mark statements [M] measured / [C] code with lines /
[E] inferred; never state a number you did not compute) and `CARDS.md` (what is live, what was dropped, open causes).
The repo root is `~/01. Project/개인 프로젝트/unsw-swarm` (called ROOT below).

## State
- Live bot since 13:31 KST: **one17** (submission 21693) = `~/meow-redteam/solo/src/solo/main.cpp` with the switches in
  `~/.claude/jobs/e2109d93/tmp/one17.switches` (one line, `NAME:value,...`). Local bot of the same build:
  `~/meow-redteam/solo/bots/mD17` (binary sha starts d6d14e1f8f53). Live source as uploaded: `ROOT/data/online/smoke/one17-bot/main.cpp`.
  Today's changes on the way here: one14 dropped PORTAL_SCOUT_MIN_LEN, one15 dropped TERRITORY_DECAY, one16 added
  QUEEN_NO_BLIND_PORTAL (queen takes no unseen portal on maps of 600 cells or fewer), one17 added QS_SHED_MAX 9 (a queen of 10
  or longer no longer splits down to 2 when exposed). The deadline is 15:00 KST; the last upload can be at about 14:30.
- The lead (main session) integrates and uploads. You never upload, post to Discord, touch git, or edit `src/solo/main.cpp`,
  `src/w-one*/`, another agent's folder, or any tool. No switch goes live unless it is ready and verified by the time your brief names: stop
  building then and report what you have, even if it is "not ready".

## Building and playing (Claude agents can play local games; Codex cannot)
- Work on your own copy: `~/meow-redteam/solo/src/w-<you>/main.cpp` (copy the base your brief names). The bot is one C++ file
  with `constexpr` switches, all off by default. New behaviour = a new switch, off by default, every new line guarded so that
  OFF is the same program. No comments beyond one short line, no map names, no size tables, nothing tuned to a known map.
- Build: `cd ~/meow-redteam/solo && MKSRC=src/w-<you>/main.cpp python3 tools/mkbots.py "<botname>=CONST:value,CONST:value"`
  (an empty list after `=` builds all-off). Binary: `bots/<botname>/bot`. Prefix every bot name with your agent's short tag.
- Identity check, required: `shasum bots/<allOffName>/bot` must start with `92fb69564fbd` (the all-off hash of the base); also build your source with only the one17 values and play 4 games beside `mD17` on the same maps and seeds against `m3base`: the replays must be identical (`cmp`), the binary hash may differ. If a
  wrapper function changes inlining and the hash moves, inline the term at the call sites until it matches.
- Play: `cd ~/meow-redteam && ./play.sh <botA dir> <botB dir> <map file> <seed> <out dir>`; out dir gets `result.txt`,
  `game.replay`, `engine.log`. Put runs under `solo/runs/<tag>_<arm>/<map>-seed<S>-side<K>/`. Maps: `maps/gx/` (64 generated
  maps, `INDEX.tsv` has the cell counts; use 288 to 1536 cells for speed) and `maps/ladder/ladder_*.map` (16 ladder maps; seven of them rebuilt from replays with
  estimated pearl supply: compare arms on the same file, never against online numbers). Opponents: `solo/bots/mD17` (the live bot; a head to head against it is the test
  that counts) and `solo/bots/m3base` (old main, weaker).
- **At most 4 games running at a time per agent** (sixteen jobs share the machine in the last hour) (the machine has room; several jobs share it). Stop only processes you
  started, by PID. Never `pkill` by pattern.
- This session's shell refuses long compound commands (pipes into `sh -c`, `xargs`, `cd` chains). Write a script file with the
  Write tool under your folder and run it as `zsh <absolute path>`; keep each direct command simple.
- Replay readers (run python from ROOT): `tools/ladder_replay.py`, `data/analysis/ladder/dossier/work/o1_scan.py`,
  `o1_look.py` (7 by 7 boards), `o1_local.py` (`rows(arm)` for local runs under `~/meow-redteam/solo/runs/<arm>`, `snap`).

## What counts as evidence here
- A switch is judged by behaviour first: does it fire where it should (count it in replays), and does the thing it was built to
  stop happen less. Win counts over fewer than about 40 games mean nothing; on symmetric maps the seat often decides a head to
  head, so information comes from games where the two bots' behaviour diverges.
- The mistake of this morning: a switch that looked level in local head to head had halved our pearls on six ladder maps. So
  always also report our pearls by r100 and dragons at r100 per map, switch on against switch off, same opponent and seeds.

## Deliver
Your folder: `ROOT/data/codex/astra/<you>/` (scripts, tables). Source and diff: `~/meow-redteam/solo/src/w-<you>/main.cpp` and
`ROOT/data/codex/astra/<you>/<you>.diff` (`diff -u <base> <yours>`). Final message to the lead, plain text, under 50 lines:
first three lines = what you built or found, whether it is ready to go live (yes / no / with which values), how sure;
then the hash check, the mechanism counts, the per-map pearls table, the head to head, and what would show it is wrong.
Send a two-line heads-up to the lead as soon as you have something usable; do not wait for the final report.
