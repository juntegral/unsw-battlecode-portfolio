# Prepare a black-box workspace in this directory (~/meow-redteam)

An analyst will later be asked to write a bot that beats a fixed opponent bot of which it only has the binary.
Prepare everything it needs here, self-contained, and prove it works. You may READ anywhere on this Mac to find the
pieces, but WRITE only inside this directory. Do not post anywhere, no server calls, do not start long batches of
games (a handful of single games to prove the scripts work is fine; never more than 2 games at once).

## Where things are
- The opponent: the compiled live bot `~/meow-loop-out/card-48/attempt-3/bot-off` (built from the current main).
  Copy it to `opponent/bot`. Copy nothing else of ours.
- How games are run locally: `~/meow-loop-out/card-48/attempt-3/harness/` (the loop's harness: see how it starts a
  game between two bots, where maps live, `replay.py`), the loop code in
  `~/01. Project/개인 프로젝트/battlecode/work/loop/` (jobs.py and friends), and the engine
  `~/01. Project/개인 프로젝트/battlecode/work/bc127` (a Python venv, unswbc 1.2.7).
- Map lists: `~/01. Project/개인 프로젝트/battlecode/work/heldset.txt`, `heldset_sq.txt`,
  `freshset.txt`, and the map files the harness uses.

## Build in this directory
1. `engine/`: whatever is needed to run games without naming any path outside this directory in a command
   (a symlink to the venv is fine).
2. `maps/dev/` (8 maps) and `maps/eval/` (16 maps, none of them in dev): pick from the generated held-out maps so
   both sets mix sizes (some of 600 cells or fewer, some above 1200) and shapes. Copy the files. Write `maps/README.md`
   with size and starting-dragon count of each.
3. `docs/`: the game rules and the bot programming interface as shipped with the ENGINE (its own documentation,
   headers, starter or example bot). Do NOT copy anything from our bot's source directory (`mybot2`) or from our
   notes and analyses. If the engine ships no starter bot and no interface documentation, say so clearly in
   `SETUP-REPORT.md` and stop; do not substitute our own files.
4. `starter/`: a minimal bot that compiles and plays legal moves, built only from the engine's own material, with a
   `build.sh` that compiles a bot directory into a binary.
5. `play.sh <botA> <botB> <map file> <seed> <out dir>`: plays one game with A on side 0 and B on side 1, saves the
   replay and prints one line: winner, how it ended, rounds, final lengths. It must run the game at low priority
   (`nice -n 15`) and take a lock so that at most 2 games run at once however it is called (for example two lock
   files tried with `flock`-style locking in Python).
6. `batch.sh <botA> <botB> <dev|eval> <seeds> <out dir>`: every map in the set, both side orders, through `play.sh`,
   then a summary table (wins by map and side, how games ended). Still at most 2 games at once.
7. `tools/`: a small replay reader (`tools/show.py <replay> [--round N]`) that prints the board state and each
   dragon's id, team, length and position, built from the engine's replay format (you may adapt the harness's
   `replay.py`).
8. `guard.py` and `settings.json`: a Claude Code PreToolUse hook (see
   `~/01. Project/개인 프로젝트/unsw-swarm/tools/ladder_guard.py` and `ladder_settings.json` for the
   form) that DENIES a tool call when any string in its input contains one of: `battlecode`, `unsw-swarm`,
   `meow-cards`, `meow-release`, `meow-loop`, `meow-dev`, `meow-queen`, `meow-bigmap`, `meow-deploy`, `meow-tx`,
   `mybot`, `.claude/projects`, `api.txt`, `discord`; or when it would inspect the opponent binary other than by
   running it in a game (`strings`, `objdump`, `otool`, `nm`, `lldb`, `gdb`, `hexdump`, `xxd`, `dtruss`, `dtrace`
   together with `opponent`); or when it uses the network (`curl`, `wget`, `gh `, `git push`, `ssh`, `nc `).
   Everything else is allowed. The hook must exit 0 on allowed calls and block with a short reason otherwise.
   `settings.json` registers it for all tools, using the absolute path of `guard.py` in this directory.
9. Proof: build the starter, play `starter` against `opponent/bot` on one dev map on both sides and
   `opponent/bot` against itself once, with `play.sh`. Put the three result lines in `SETUP-REPORT.md` together with
   a list of what is in each folder, the exact commands, how long one game takes, and anything that does not work.
   Test the guard with three sample inputs (one allowed, two denied) and report the outcome.
Write `SETUP-REPORT.md` last (40 lines or fewer).
