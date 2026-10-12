# The toolbox: every script worth keeping, what it does and how to run it

Written 2026-10-10 for the next bot-programming contest. Paths are relative to one of three roots:

- `S` = `unsw-swarm` (jun's private repo: `tools/`, `docs/`, `data/`, `archive/`)
- `R` = `~/meow-redteam` (the local game rig; not a git repository)
- `B` = the team repo `forrest-gan2005/battlecode` (here: the worktree `one13-into-main`)

Words used here. A **bot build** is one compiled program. We turned every new behaviour into a **switch**: a `constexpr`
constant at the top of the one C++ file that is off by default, so one source file gives many builds. An **arm** is a build
with a named set of switch values (we called them `mD16`, `mNps` and so on). A **seat** is the side a bot plays (0 or 1).
A **ticket** is one game of the server's hourly allowance. A **ranked battle** is a five-game series on maps the server
picks. A **replay** is the file the engine writes for each game.

## 0. What to take from this chapter

1. The tools that carried the work were small. Four of them did most of it: a local game launcher with a machine-wide slot
   limit (`R/play.sh` + `R/engine/run_game.py`), a build-variants script (`R/solo/tools/mkbots.py`), a shell template that
   plays "arm vs live bot, both seats, skip finished games" and prints a tally, and a replay reader that rebuilds the true
   game state (`S/tools/ladder_replay.py`). Counted from disk on 2026-10-10 over the 229 files in
   `S/archive/final-session-scripts/`: 50 call `play.sh`, 27 call `mkbots.py`, 26 hash binaries with `shasum`, 33 start
   something with `nohup`, 35 use `pgrep`. Those four patterns are what to rebuild first.
2. Everything that spends a scarce resource (tickets, uploads, the live bot) printed a plan and did nothing until it got
   `--confirm`, and refused when the live bot was not the one the caller expected (`--expect-active <id>`). That design cost
   a few lines per tool and prevented wasted tickets. Copy it.
3. "Is this build the same program as that one?" was asked about 30 times and was answered mechanically, by a hash of the
   all-switches-off binary (`92fb69564fbd` was the fixed value for the last two days) and, when hashes differed, by comparing
   replays byte for byte. Decide the identity test before writing the first switch.
4. We lost real time to plumbing, not to the game: the server refused our client version, a hard-coded freeze time blocked
   all online tests for a while, a `pkill` pattern killed a whole queue, the local slot limit silently capped us at two games
   for three days. Section 10 lists each with its date.
5. The replay analysis scripts (`dossier/work/`, 359 Python files) were mostly one-off. The reusable part was a handful of
   readers; the rest were cheap because those readers existed. Build the reader first, then let anyone (human or AI) write
   a 30-line script on top.

How the tool counts below were obtained: file counts and line counts by listing the folders on 2026-10-10. Usage lines are
copied from the scripts' own docstrings or from `S/docs/HANDOVER-2026-10-09.md` section 7; where I only read the code, I
say "read". I ran none of the server, Discord or GitHub tools.

---

## 1. Talking to the contest server

Lesson: put every server call behind two tools (read/request, and upload/activate), log every spending call in a ledger
file, and make the spending commands default to "print the plan". Everything else (collectors, test runners, watchers)
should call these two tools, never the HTTP API directly. We did that, so the key was handled in exactly two places.

| Tool | What it does | Command line as used |
|---|---|---|
| `S/tools/online.js` (499 lines) | Read: leaderboard, team, tickets, submissions, battles, one battle, maps, queue, tournaments, `mapsave` (saves every server map body to a folder). Download: all games of a battle. Spend: request battles. | see below |
| `S/tools/submit.js` (163 lines) | `upload`, `activate`, `active`, `check`. | see below |
| `S/tools/subs.js` | Lists our submissions with descriptions (read-only). | `node tools/subs.js list [--last N] [--json]` |
| `S/tools/smoke.py` (871 lines) | Online test of a build: plan, start, baseline, pair, status, report, rollback. Upload, play N games, restore the live build. | `python3 tools/smoke.py pair "$BOT" --name $LABEL --opp $OPP --maps $M --new-only --ref "$REF" --confirm` (from `S/data/online/smoke/run-pair.sh` line 215) |
| `S/data/online/smoke/run-pair.sh` | Wrapper around `smoke.py pair`: builds the notice text, posts it to the team channel, waits, rolls back. | `run-pair.sh <label> <botdir> <card ref text> [opponent ids]`; `LIVE_ONLY=1` plays only the live bot; `BASELINE=1` also replays the live bot first |
| `S/data/online/smoke/at-q.sh` | Queue runner: reads jobs from `at-q.txt` one line at a time, waits for ticket room, runs `run-pair.sh`, writes `<label>-report.log`. Exits if the active bot is not `LIVE_ID`. | `LIVE_ID=<submission id> SMOKE_ALLOW_PENDING=1 nohup data/online/smoke/at-q.sh > /dev/null 2>&1 &` |
| `S/tools/pair_report.py` (290 lines) | Summarises a finished pair test against the pooled baseline of earlier runs on the same opponent and map. | `python3 tools/pair_report.py <label> [--post [card name]]` |
| `S/data/online/live-one1/collect.sh` | Every 300 s, lists our finished battles and downloads new ones into `data/online/live-one1/b<id>/`. | no arguments; it stopped itself at the deadline (a time constant inside) |

`online.js` details (read from the script):

- Reads cost no tickets. `request` and anything that spends tickets only prints the plan and expected cost unless `--confirm`
  is given, and `--confirm` requires `--expect-active <submission id>`.
- Ranked request: `node tools/online.js request <teamId> --ranked --purpose "<why>" --expect-active <id> --confirm`
  (from `S/data/online/ranked-push-1005.sh`). Ranked takes no `--maps`: the server picks five maps. Unranked request:
  one game per map, `--maps all|4,7,9|portals,trauma` is required.
- Download: `node tools/online.js download <battleId>[,<id>...] --out live-one1/b<id> --purpose "<why>"`. It writes
  `game-<id>.json`, `M<id>.replay`, `events-<id>.jsonl.gz` and `index.json`, and can also download public battles between
  two other teams. The storage link is followed without the key.
- Tickets: `node tools/online.js tickets --json` returns `normal` and `dev` counters (`fromServer`, `fromLedger`, `used`).
  The comment in the script says 60 games an hour by hand plus a separate 60 against the organisers' "DEV" teams (docs of
  2026-09-29). Our shell scripts computed free games as `60 - max(fromServer, fromLedger, used)`.
- Ledger: every request is one line in `S/data/online/requests.jsonl` (179 lines at the end); every request, upload and
  download is also written to `S/data/online/REMOTE-LOG.md`.
- Key: read from `$UNSWBC_KEY` or from a key file, never printed, never written, replaced by `[REDACTED]` in every printed
  server text. `submit.js` and `smoke.py` do the same redaction.

`submit.js` details (read, plus handover section 7.2):

```
B=data/online/smoke; mkdir $B/oneN-bot
cp ~/meow-redteam/solo/bots/<arm>/{main.cpp,helper.hpp,sonar_codec.hpp} $B/oneN-bot/; cp $B/agg8-bot/bot.toml $B/oneN-bot/
c++ -std=c++20 -O2 $B/oneN-bot/main.cpp -o <temporary>                 # compile check
node tools/submit.js upload "$PWD/$B/oneN-bot" --name oneN --desc "<one English line>" --confirm --allow-pending
node tools/submit.js check  "$PWD/$B/oneN-bot"                         # server copy == folder
node tools/submit.js active                                            # prints "<id> <name> (<uploadedAt>)"
```

`upload` smoke-tests the bot (two local games), refuses while live or pending battles exist unless `--allow-pending` or
`--force`, waits until the new submission is active, then downloads the server's zip and compares file hashes with the
folder. Running matches keep their version. Each upload is logged to `S/data/online/submissions.jsonl` (148 lines) and the
mapping from submission id to our version name is `S/data/online/smoke/versions.tsv` (17 rows, `20980 one5` to `21857 one21`).
`activate <id> --confirm` re-activates an older submission.

What the pair-test chain looked like at the end (measured from the files): `at-q.txt` lines have the form
`label|bot dir or -|description|opponent ids|mode` with mode `new` (upload, swap, 15 maps per opponent, swap back) or `live`
(live bot only, no swap). Opponent 545 drew on the DEV allowance, the others on the normal one. The same label cannot be used
twice (a state file `data/online/smoke/<label>.json` blocks it). 47 `at-*.sh` scripts and 60 `.sh` files in total sit in
`S/data/online/smoke/`; they are the per-test launchers written over the contest and are all variations of the above.

Traps:

- The server started refusing uploads from the unswbc 1.2.7 client ("1.2.9 is out", exit 1) from about 12:15 KST (the log line carries
  no date; its position in the "team log (meow-main05)" section of `S/docs/SESSION-STATE.md` suggests 10-07, and
  `S/docs/HANDOVER-2026-10-08.md` line 45 repeats "only 1.2.9 is accepted, from about 12:15"). 1.2.9 has the same engine; only the
  version string and the replay viewer differ. Fix: a second venv with 1.2.9 for uploads (`work/bc129`), `submit.js` uses it
  when present. Later the loop engine was upgraded too. Handover 10-09: the CLI keeps announcing "1.2.10 is out" but the upload
  goes up as 1.2.9. Lesson: keep the upload client separate from the engine used for local games and pin it.
- After one upload the immediate hash check failed once (handover 7.2). Always run `submit.js check` after `upload`.
- `smoke.py` had `FREEZE = 2026-10-08 20:00 KST` hard-coded on line 21. After that time every online test, including live-only
  runs, was refused. It was noticed at about 19:00 on 10-08 and fixed at 22:13 (new freeze 10-09 14:30 KST, plus the
  `SMOKE_ALLOW_PENDING` switch). The log records two automatic-classifier refusals of the edit at 19:00 and, at 20:00, that
  all online tests were refused pending jun's change; who made the 22:13 edit is not recorded in the files I read. Online
  tests were blocked for roughly two hours. The runner in the team repo had the same kind of constant
  (`FREEZE` on line 28 of `B/work/loop/runner.py`, fixed in commit 7c42d92). Next time: take the freeze time from one
  config value, and test the refusal path on day one.
- Do not upload while a live-only queue is running; the games would mix two builds (handover 7.2).
- A game result for a ranked battle you did not request is another team's request, not yours: count only your ledger
  (see `online.js tickets`, which uses both server and ledger counts).

Collectors for studying other teams (all read-only, no tickets):

| Tool | Use | Command line |
|---|---|---|
| `S/tools/top_collect.py` | Every `--every` s, read the leaderboard and the six most recent battles of the best `--watch` teams, download finished battles where both teams are above `--min-elo` into `data/top1/<battleId>/`. | `python3 tools/top_collect.py [--min-elo 2000] [--watch 12] [--every 180] [--cap-gb 6] [--until 2026-10-05T09:00]` |
| `S/tools/top3_collect.py` | Same for chosen team ids (battles against teams rated 2000 or more). | `python3 tools/top3_collect.py [--teams 454,157,306] [--every 240] [--until 2026-10-08T22:00]` |
| `S/tools/collect_top.js` | The first, JS version (writes `data/top/`). A team profile shows only its six latest battles, so it must poll every few minutes. | `node tools/collect_top.js [--min-elo 1900 | --top 20] [--dry]` |
| `S/tools/ladder_collect.py`, `ladder_hourly.py`, `ladder_rows.py` | The ladder pipeline: hourly battle ledger, per-game rows from replay true state, atomic file replacement. Schema and audit (625 games recounted by separate code on 10-07) in `S/data/analysis/ladder/SCHEMA.md`. | `python3 tools/ladder_collect.py --recheck` (refresh from disk without a server call); `ladder_hourly.py --once` |

Lesson that transfers: a team profile page lists only the latest few battles, so collecting other teams' games is a
polling job that must start early; what you did not collect before the contest ended is gone.

---

## 2. Running games locally and in bulk

Lesson: one launcher that every caller goes through, which holds a machine-wide slot lock, sets low priority, refuses to
overwrite a result folder, and writes a one-line result plus a JSON record. Batches are then just shell loops that skip
folders that already have a `result.txt`, so any batch can be killed and restarted.

| Tool | What it does | Command line as used |
|---|---|---|
| `R/play.sh` | `nice -n 15` wrapper around `R/engine/run_game.py`. | `./play.sh <botA> <botB> <map file> <seed> <out dir>` (A on seat 0, B on seat 1) |
| `R/engine/run_game.py` (161 lines) | Runs one native match with the engine's own `EngineModule`, `Pool` and `Bot` classes. Takes one of four `flock` slots in `R/.locks/game-{0..3}.lock`. Writes `game.replay`, `result.json`, `result.txt`, `engine.log`. Output folder must be empty. All inputs and outputs must be inside `R`. | called only through `play.sh` |
| `R/batch.sh` + `R/tools/batch.py` | Every map in a group, both seat orders, one game at a time. Summary per map and seat. | `batch.sh <botA> <botB> <dev|eval> <seeds> <out dir>` |
| `R/solo/tools/run_arms.sh` | Each arm plays an opponent on a list of maps, both seats; builds a jobs file and runs it. | `SOLO_OPP=solo/bots/m3base SOLO_MAPS="<map paths>" ./solo/tools/run_arms.sh <seed> <arm>...` |
| `R/solo/tools/sweep.sh` | Each arm vs `m3base` on the generated maps of 288 to 1536 cells, both seats, `xargs -P ${SWEEP_P:-6}`. | `./solo/tools/sweep.sh <arm>...` |
| `R/solo/tools/h2h_tally.py` | W/D/L of every head-to-head folder `runs/h2h_<arm>_v<opponent>/`. | `python3 solo/tools/h2h_tally.py` |
| `R/solo/tools/gx_tally.py` | W/D/L of each arm on the generated maps by size band; `-v` lists losses. | `python3 solo/tools/gx_tally.py <arm>... [-v]` |
| `S/archive/final-session-scripts/h2h17.zsh` | The head-to-head template (below). | `H2H_P=10 zsh h2h17.zsh <arm>...` |
| `R/tools/show.py` | Print a replay's board and live dragons at round N. | `python3 tools/show.py runs/one-game/game.replay --round 10` |
| `S/tools/eval.js`, `pair_ab.js`, `S/tools/unswbc*` | Older (09-27 to 10-01) benchmark through the official CLI under the previous rules; not used after the move to `R`. | not recommended; see Appendix A |

The head-to-head template, which is the single most used shape of script (read from `h2h17.zsh`):

```
P=${H2H_P:-10}
for m in <ladder maps> <generated maps by size>; do
  for a in "$@"; do for s in 0 1; do
    O=solo/runs/h2h_${a}_v16/$N-seed1-side$s
    [ -e $O/result.txt ] && continue                 # restartable
    if [ $s = 0 ]; then ./play.sh solo/bots/$a solo/bots/mD16 $m 1 $O > /dev/null 2>&1 &
    else               ./play.sh solo/bots/mD16 solo/bots/$a $m 1 $O > /dev/null 2>&1 &; fi
    n=$((n+1)); [ $((n % P)) -eq 0 ] && wait
  done; done
done
wait; echo "h2h17-done $* $(date '+%T')" >> solo/runs/run.log
python3 solo/tools/h2h_tally.py | grep "_v16"
```

Why it works: result folders are the state (no database), a `...-done` line in `R/solo/runs/run.log` is the only signal,
and the tally script reads the folders. Scale reached (counted on 2026-10-10): 488 arm folders and 9,077 finished local
games under `R/solo/runs/`, 615 bot builds under `R/solo/bots/`, 45 source variants under `R/solo/src/`.

Traps:

- The slot limit in `run_game.py` was two games machine-wide from 10-07. The log (10-09 13:52, from `tiny-opus`) found that
  this had capped every local batch at two games all day, including a batch started with 8 at a time. A trial of 7 slots gave
  load 44 to 51 because each game uses four to five cores (one process per dragon), so throughput is set by CPU, not slots;
  it was set to 4. The local engine has no time limit, so load does not change a game's result, it only slows it (replays are
  deterministic). Lesson: print the slot count and the number of running games at the start of every batch, and measure one
  game's core use before choosing the limit.
- Native mode has the engine's wall timeout but does not measure the judge's CPU-point budget (`R/engine/README.md`). A build
  that passes locally can still be too slow on the server; `S/archive/final-session-scripts/stress17.zsh` plays the live
  build on every generated and ladder map and then greps `engine.log` for errors and timeouts. The team repo's convention
  was to run a 64x64 map under `unswbc run --sandbox` and keep the worst turn under about 60M points (`B/README.md`).
- Codex workers could not play games on this machine (their sandbox refuses `nice`), and `R` is not a git repository, so
  Codex jobs were started from `S` and told to write under `S/data/codex/` (handover 7.1).
- A local win or loss does not predict the server result (handover section 8). Local games answer "did the mechanism fire,
  and what did it cost", not "is it better".

---

## 3. Building variants and proving two builds are the same program

Lesson: keep one source file where every behaviour is a named constant, generate variants by textual substitution, and
treat "same program" as a checked property (hash, then replay bytes), not a belief.

| Tool | What it does | Command line as used |
|---|---|---|
| `R/solo/tools/mkbots.py` (16 lines) | For each `name=SWITCH:value,...` argument: copy the source, replace each `constexpr <type> SWITCH = ...;` (assert exactly one match), write `solo/bots/<name>/main.cpp`, compile with `c++ -std=c++20 -O2`. | `cd ~/meow-redteam/solo && [MKSRC=src/w-x/main.cpp] python3 tools/mkbots.py "mD21=$(cat one21.switches)"` |
| `B/work/server_bot.py` (75 lines) | The team repo's version: reads `work/server_profile.txt` (52 `NAME value` lines, the live switch values), allows `--on NAME:value`, requires each constant to match exactly once, copies `main.cpp helper.hpp sonar_codec.hpp bot.toml`, compiles. | `python3 work/server_bot.py OUT [--src mybot2] [--profile work/server_profile.txt] [--on NAME:value ...] [--no-compile]` |
| `S/archive/final-session-scripts/up21.zsh` | The upload script with its checks; `up14` to `up21` are the same script edited per version. | `zsh up21.zsh` |
| `S/archive/final-session-scripts/chk18.zsh` | The lead's own check of a builder's source: size of its diff against the team source; builds all-off, live values, live plus the new switches; prints hashes. | `chk18.zsh <source file> <tag> <extra switches>` |
| `S/archive/final-session-scripts/idx.zsh` | "Is source X with the live values the same player as the live bot although the binary differs?" Plays 4 maps, both seats; compares replays with `cmp -l`. | `zsh idx.zsh` |
| `S/tools/fingerprint.js` | Hashes a game's event stream (actions, moves, splits, deaths, pearls; not timing or indicator text); two builds that should behave identically must give equal fingerprints on the same map, opponent and seed. | usage text in the script header (read, not used in the final week) |
| `B/work/ident.py` | The earlier identity check in the team repo: `sha1` over dragon update, death, split and round events of 10 fixed maps against a reference version `REF` (default `v53`). | `REF=v53 python3 work/ident.py` (read) |

The identity protocol, as written in `S/docs/HANDOVER-2026-10-09.md` section 7.1 and used in `up15` to `up21`:

1. Work on a copy: `src/w-<name>/main.cpp`; diff with `diff -u src/solo/main.cpp src/w-<name>/main.cpp`.
2. Build with every switch off; its binary hash must equal the fixed value (`92fb69564fbd`): the new code is inert when off.
3. Build with the live build's switch values; its hash must equal the live build's binary.
4. Only then copy over the team source and upload. `up21.zsh` encodes this: it exits with "CHECK FAILED, not uploading" if
   either hash differs, and again if four short games do not finish.
5. If the hashes differ although the code should play the same (a new switch in a `||` expression changes code generation),
   play the same 6 to 8 games with both and compare `game.replay` with `cmp -l`. A difference of only 2 bytes where the
   bot-name strings differ means the same game; keep arm names the same length. Example (10-09 11:56): `mXl5` vs `mD15`, four
   maps both seats, all identical but 2 bytes of the bot name.

Traps:

- The official CLI's compile cache omitted header files in version 1.1.0, so editing `helper.hpp` did not rebuild. The
  workaround `S/tools/unswbc-clean.py` copies the bot project into a folder named by a hash of all inputs (headers too).
  `R` avoids this by compiling directly with `c++`. If the next game has a CLI with a cache, test header edits first.
- `mkbots.py` asserts one match per switch; a typo fails loudly (good) but a rename of a constant in the source breaks every
  saved switch list. Keep the switch lists (`one13.switches` ... `one21.switches` in `S/archive/final-session-scripts/`) with the source.
- A builder's rewrite of a helper function (`can_split` wrapper, a ternary changed to `||`) broke the all-off identity once
  (log 07:31, `qhold-builder`). That is why step 2 is mandatory for every worker's output.

---

## 4. Reading replays and measuring behaviour

Lesson: one shared reader that reconstructs the **true** state of the game from the replay (the replay lists events, not
states; the sides' bot also does not see everything the replay shows) is worth more than any single analysis. Scripts on top
of it were 30 to 300 lines and were written by AI workers in minutes. Write it in the first week, test it against a recount
by independent code, and keep its import path stable.

The reader stack (read from the code):

- `B/replay.py` (344 lines, from QWQ's repository): parses the `.replay` file (gzip + packed Cap'n Proto) into an event
  stream. `python3 replay.py file.replay [--json]`.
- `S/tools/ladder_replay.py` (156 lines): the shared true-state module the analysts import (`from ladder_replay import replay, edge_id, canonical_edges, scan`).
  Its docstring says it is "adapted from drop-analysis/count.py's scan", and it loads
  `S/data/online/smoke/fountain-analysis-2/count.py` by file path. A shared library that imports a one-off analysis folder is
  fragile: do not delete that folder. `S/data/analysis/ladder/SCHEMA.md` shows the use:
  `root = replay.load(folder/'M12345.replay').root()`; `root.text(0)` is the map; `root.pointer(3)` the events;
  `replay.EVENT_NAMES[event.u16(0)]` the event kind.
- `S/tools/ladder_rows.py` (247 lines): one symmetric row per game (us and them) from the true state; skips game ids it
  already has; `--rebuild` to redo.
- `S/data/analysis/ladder/dossier/online/label_report.py`: per-label report with its own replay reader and per-game rows;
  `python3 label_report.py <label> [--ref ...] [--dir NAME=FOLDER[,FOLDER...]]` (read).
- `R/tools/replay_format.py` and `R/mytools/trace.py`: independent readers for the local rig (per-round dragon table with
  deaths and splits; `trace.py replay [--from R] [--to R] [--every N]`).
- `S/tools/viewer.js` and `S/tools/replay.js`: the official viewer parser extracted from the pip package in a Node VM.
  `viewer.js` points into `개인 프로젝트/UNSW/.venv-ppo/...`; that folder no longer exists, so `viewer.js`, `replay.js` and
  everything built on it (`replay2map.js`, `top_features.js`, `mass_ledger.js` ...) are broken today. The log says the same
  about `replay2map.js` (10-09 11:06).

The scripts that were reused across analyses (all take the repo root as the working directory):

| Script | Job | Command line |
|---|---|---|
| `S/data/analysis/ladder/dossier/work/o1_scan.py` (287 lines) | Full length ledger of both sides: every death with who ate its pearls, every paid turn, every split, a snapshot every 25 rounds; one JSON row per game. Defines the named sets (`w1`, `d1`, `live`, ...). The base for most other `o1_*`. | `python3 -B data/analysis/ladder/dossier/work/o1_scan.py <set> [limit]` |
| `.../o1_look.py` | Draws the 7x7 view around one dragon, round by round, with free-path step counts to pearls. The "look at the actual moment" tool. | `o1_look.py <set> <game id> <dragon id> <r0> <r1>` |
| `.../o1_local.py`, `o1_sweeptab.py`, `o1_ledger.py`, `o1_net.py` | Scan local arm folders (`~/meow-redteam/solo/runs/<arm>/<map>-seed<S>-side<K>/game.replay`), table of early economy per arm vs a baseline arm, length ledger by round window. | `o1_sweeptab.py <baseline arm> <arm>...` |
| `S/data/codex/astra/qexit-opus/qdeath.py` (339 lines) + `classify.py` | Every death of our queen: her free cells at her last turn starts, who closed them, killer. Then a class table. Shared by later watchers. | `python3 -B data/codex/astra/qexit-opus/qdeath.py online | local <arm> ...`; `classify.py <jsonl> [rows]` |
| `.../stuck-opus/detect.py` (357 lines) | Wasted-turn detector (loops in small areas, pearl in reach but not nearer, crowding by mates, death soon after a split); cached rows per set. Plus `agg.py`, `paired.py`, `board.py`. | `detect.py online one14-c1 ...` / `detect.py local h2h_mNps_v13 ...`; `agg.py online|local [pattern ...]` |
| `.../watch17-opus/w.py` + `rep.py` (and `watch19-opus/w19.py`) | Per-game health lines plus one mechanism table, cached per game; written to judge a new live version's own games within minutes. Verdicts were typed into `verdicts.md` by the analyst. | `python3 -B data/codex/astra/watch17-opus/w.py`, then `rep.py` |
| `.../opp-*/tab.py` | Every game vs one named opponent, same script for both sides. | `python3 data/codex/astra/opp-ballers/tab.py` |
| `S/tools/sweep_games.py` | Finds games of ours not yet analysed and starts Codex analysts on the lost ones (5 per job), one on the wins, then a synthesis job. | `--round`, `--synth`, `--pending` |
| `S/tools/weak_watch.py` | Lists ranked games lost to a team rated at least 100 below us (rule from jun, 10-09 02:52 KST), starts one analyst per battle. | `--list`, `--new` |
| `S/tools/smoke_pick.py` | Picks online replays with visible queen, split or feed behaviour for a human to watch. | read |
| `S/tools/pair_report.py` | See section 1. | |

Older, bigger studies in `S/tools/` (09-29 to 10-05; each reads `data/top/` replays and writes tables in Markdown): `decisions*.js`
(a per-dragon-turn decision dataset and rule learning), `mass_ledger.js`, `fragment_study.js`, `sonar_study.js`,
`timing_study.js`, `matchup_study.js`, `mech_check.js` (2,424 lines, "did each mechanism fire against these opponents"),
`wave_triage.js` (rank losses by margin, then read only the worst), `pearl_layout.js`. These were the instruments of the
first week, when we had no bot yet to measure. They were not used in the last three days and depend on the broken viewer
stack above.

Traps and notes:

- Server replays hide the pearl respawn timers: `pearlRespawn` is all 0 and the tile gaps are redacted. Any number that
  depends on respawn timing is an estimate (`S/tools/pearl_layout.js` header). The same holds for maps rebuilt from replays
  (section 6).
- Counting on the whole population mattered: several early AI claims were wrong when recounted (`portalcheck*.py`,
  `lcheck.py` in the archive are exactly such rechecks of a subagent's claim, written by the lead from the label caches).
  The corrected reading is the one in the log; the scripts remain as the pattern "re-derive a worker's headline number with
  independent code".
- A re-count script that re-aggregates everything when a field is added took over ten minutes and blocked the session twice
  (`count_local.py`, log line 176): run such jobs in the background and cache per game.
- Mark every sentence in analysts' reports as measured `[M]`, read from code `[C]` or inferred `[E]` (the rule in
  `S/data/codex/astra/ASTRA-COMMON.md`). It made the lead's verification quick.

---

## 5. Watching live results and the health of a new version

Lesson: after every upload there was a window of minutes where a broken build costs rating. The cheap defence was a status
script that prints one screen, and a "health lines per game" analyst (`w.py`, `w19.py`) that checks crashes, zero-point games
and the new mechanism's firing. Do not decide from win rate; decide from "did it break" and "did the mechanism fire".

| Tool | What it prints | Command line |
|---|---|---|
| `S/archive/final-session-scripts/poll.zsh` | One look at everything: load, number of game and Codex processes, last lines of `team_watch.py`, active submission, rank and rating, last 7 battles with result string (`WWLL.`), last line of the queue log, finished audit reports. | `zsh poll.zsh` |
| `status.zsh`, `elig.zsh`, `games.zsh`, `load.zsh`, `prog.zsh` (archive) | Smaller one-screen views: status; which ranked requests are allowed and tickets left; which local games are running; what loads the machine; local batch tallies. | `zsh <name>.zsh` |
| `S/tools/park_watch.py` (121 lines) | Two copies of the same code are kept as submissions; the higher-rated one stays parked, the lower plays; when the playing copy climbs above the parked one it swaps them (activates the parked copy) and says so in the team channel. Every 300 s, stops at the deadline. | `python3 tools/park_watch.py [--once] [--dry-run] [--manual]` |
| `S/tools/loop_watch.py`, `mention_watch.py`, `jun_dm.py --watch`, `team_watch.py --prs --wait` | "Wake me when X" watchers without a model (section 7 and 9). | |
| `S/tools/scrim.py`, `seat.py` (archive) | Which opponents pay in ranked battles (win share vs the rating-gap expectation); whether we win less as seat B across all games on disk. | `python3 scrim.py` |

`park_watch.py` ("elo defence") came from a user rule on 10-06 and became a ratchet on 10-07: since each submission keeps its
own rating, keep two copies of the intended bot and always play the lower one. It was used for the last days (6 mentions in the log).

Traps:

- A background process started with `&` inside a Bash call does not wake the session. Waits that must wake the session have
  to be run with the harness's "run in background" option (handover section 8).
- Builders and analysts sometimes finished without reporting (2.5 hours missed once). `wait_any.sh` (section 9) waits on
  result files instead of on the worker's message.

---

## 6. Maps: generating, converting, rebuilding from replays

Lesson: the qualifier ran on maps nobody had seen, so the value of the map tools was breadth (many shapes and sizes), not
fidelity. The generated set exposed failures the 16 known ladder maps never showed (7x7 maps, 64x16 corridors, up to 65,536
cells); a portal bug, on the other hand, was invisible locally because the generated set had few portal maps and we had no
local copy of seven ladder maps (log 10-09 11:05 to 11:06). A map reconstructed from a replay is an estimate.

| Tool | What it does | Command line |
|---|---|---|
| `S/data/codex/astra/mapgen/gen.py` (358 lines) | Deterministic generator for the unseen-map suite; 8 families (`open rooms corridors islands ring rotation poor rich`), mirrored by symmetry (`x`, `y`, `xy`), checks connectivity and legality, no bot. Output: 64 maps, copied to `R/maps/gx/` with `INDEX.tsv` (name, family, w, h, cells, symmetry, portals, bearing tiles, start layout, ladder range). | `python3 gen.py` in that folder (read; arguments not recorded here) |
| `S/tools/mapgen/*.js` (census, mapgen, validate, check, smoke, report) | Earlier generator and static validator (format, symmetry, portal endpoints, connectivity) with a 48-game smoke runner. | `node tools/mapgen/census.js; node tools/mapgen/validate.js --existing; node tools/mapgen/mapgen.js --seed 20261001; node tools/mapgen/validate.js` (from its README) |
| `B/work/mkgen.py` | QWQ's generator for the earlier held-out sets (`sqheld_*` in `R/maps/dev` and `R/maps/eval`, 90000-series ids). Palette of kelp and portal densities. | read |
| `S/data/codex/astra/maps-sonnet/convert.py` | Replay to `.map`: geometry (walls, portals, dragons) copied from the map text inside the replay; pearl gaps are redacted there, so they are estimated from natural spawn gaps. Replaced the broken `replay2map.js`. | `python3 -I convert.py <game id> <out.map>`; `cmp.py <a.map> <b.map>` compares |
| `S/archive/final-session-scripts/mkmaps.py` | Calls `replay2map.js` for every ladder map we did not have; superseded by `convert.py`. | |
| `S/data/codex/astra/mapgen/ladder-params.md` | Table of the 15 ladder maps (size, kelp share, portal pairs, pearl timers, starts, start distance). The map-shape reference. | |
| `S/tools/online.js mapsave <dir>` | Saves every map body the server serves. | `node tools/online.js mapsave <dir>` |
| `B/work/validmap.py`, `R/mytools` | Format check of a map file. | |

How the maps reached `R/maps/`: `ladder/` has 16 maps (those the server used, rebuilt from replays plus engine templates),
`gx/` 64 generated ones, `dev/` and `eval/` the 90000-series sets (they share no maps or transposed pairs, `R/maps/README.md`),
`community/portal_boomerang.map` was fetched from an attachment in the team channel (`zhemap.py`; map by Zhe).

Traps:

- Reconstructed maps carry estimated pearl timers. The ladder-params table says so explicitly: "Ladder reconstructions may
  have estimated pearl timers".
- The first `replay2map.js` depended on a deleted file and broke on 10-09 (log 11:06); `convert.py` was written by a
  Sonnet worker in that hour and validated by converting two maps we already had (`cmp_portals.map`, `cmp_stripes.map`) and
  diffing against the existing files. That validation step is the pattern to copy.
- The generated suite had no portal-heavy family beyond islands; the `portal` bug (`PORTAL_SCOUT_MIN_LEN`) was found online,
  not locally (log 10-09 10:24).

---

## 7. Team channel and GitHub plumbing

Lesson: three people in three time zones needed a shared read of the channel and the pull requests at the start of every
working turn. We made that a script (`team_watch.py`) and made it the first action of each session. The bot (`meowbot`)
grew to 2,082 lines, which is more than anything else in the toolbox (slash commands, a threaded read-only AI teammate, candidate approval
buttons). Whether a team of three needed that much, rather than just the mirror and the watchers, was not measured.
Decide up front whether you need an interactive bot.

| Tool | What it does | Command line |
|---|---|---|
| `S/tools/team_watch.py` (140 lines) | New channel messages (via `discord_sync.py`) plus new GitHub repository events; skips events from our own account; `--prs --wait N` is a background mode that polls PR list snapshots every 30 s and exits on the first PR change. | `python3 tools/team_watch.py` ; `python3 tools/team_watch.py --prs --wait 86400` |
| `S/tools/discord_sync.py` (169 lines) | Mirrors one channel to `data/discord/<channel>.jsonl` (raw) and `.md` (KST log), saves text attachments (the mirror itself is not published); `--show N`, `--wait`. Bot token in a git-excluded file, never printed. | `python3 tools/discord_sync.py [--channel <id>] [--show N] [--wait SECONDS]` |
| `S/tools/meowbot.py` (2,082 lines) | Bridge between the team repo and the channel: posts PR and idea updates, candidate approval buttons, `/hypo`, `/board`, `/answer`, `/meow <message>` (member-only AI session, read-only), and one-off announcements. | `python3 tools/meowbot.py`; `python3 tools/meowbot.py --announce-file FILE [--dry-run]`; `--preview-pr N` |
| `S/tools/meow_offer.py`, `meow_think.py`, `decision_nudge.py`, `snooze.py`, `tasks.py` | Helpers: a ready-made plan with a Confirm button for one person; "(thinking)" placeholder message; hourly "this card waited for you" nudge; snooze; per-person task text. | `meow_offer.py --to Zhe --text-file FILE --plan JSON`; `meow_think.py start|done` |
| `S/tools/mention_watch.py` (31 lines), `jun_dm.py` (87 lines) | No-model wake-up watchers: exit when a teammate mentions or replies to the bot; DM jun the message. | `python3 tools/mention_watch.py [seconds] [poll seconds]`; `jun_dm.py --send-file <path>` / `--watch [seconds]` |
| `S/docs/DISCORD-DESK.md` | The brief for a cheap model session that owns the channel and hands work over through a file, `data/guide/desk-inbox.txt`. | |
| `S/tools/check-meow*.py`, `test_*.py` (25 files) | Offline regression tests for the bot with fake Discord, GitHub and model calls. | `python3 tools/check-meow.py` |
| `S/archive/final-session-scripts/announce14.zsh` ... `announce17.zsh` | One-shot posts of a version notice through `meowbot.py --announce-file data/guide/px-*.txt`. | |
| `S/archive/final-session-scripts/prwatch.zsh` | Wake when the team repo's PRs change. | `zsh prwatch.zsh` |

The notice files (`S/data/guide/px-*.txt`) were the interface: a script or a person writes a short English text, and
`meowbot.py --announce-file` posts it. The rules for those texts (English, short, no colons, a monospace table for numbers that compare things) are in
the memory files under `S/archive/claude-memory/`.

Traps:

- Do not run two instances of the PR watcher (`team_watch.py --prs`); a handover note says to kill the older one by PID.
- The channel mirror needs the bot's View Channel and Read Message History permissions and the Message Content Intent
  (docstring of `discord_sync.py`).
- The desk session was added on 10-09 to keep channel chatter out of the main session's context; work passes to the main
  session through `data/guide/desk-inbox.txt`. How much it saved was not recorded.
- Secrets (bot token, API key) live in git-excluded files read only by the tools; none of the scripts here print them.

The card loop (team repo `B/work/loop/`):

| Piece | What it does |
|---|---|
| `runner.py` (1,051 lines) | A poll loop over GitHub issues ("cards") with state labels (`ready needs-info building needs-look testing tested candidate smoke kept rejected inconclusive untested`). It starts a Claude or local job only when a card's state needs work. It never uploads and never requests ranked games. Arguments: `--once`, `--dry-run`, `--repo`, `--out ~/meow-loop-out`, `--cards ~/meow-cards`, `--game-env KEY=VALUE`. |
| `jobs.py` (496 lines) | Detached job supervisor with lease files and `done.json`; jobs outlive the runner. |
| `board.py` | The card commands: `next`, `state N S`, `claim N`, `report N --kind test|check --file F --state S`, `ask N --file F`, `heartbeat --loop NAME`. |
| `guard.py`, `meow_control.py`, `late.py`, `prompts/*.md`, `tests/` (13 test files) | The hook that restricts a card session, confirmed-request consumer, late-estimate explainer, prompts per step, tests. |

Traps: `pkill -f runner.py` also kills the running jobs; restart by killing only the daemon PID and starting it again with
the same arguments (log, "runner restart"). The runner's own freeze constant is mentioned in section 1.
The rules of the loop are in `B/docs/LOOP.md` and `WORKFLOW.md`.

---

## 8. Driving AI workers (Codex wrapper, subagents)

Lesson: the wrapper that mattered was tiny (19 lines): run a worker in the background, write its whole output to a log,
and fall back to a second account when the first reports a limit. Everything else (briefs, folders, report format) was
convention. A worker is only as good as the brief; the brief files are in `S/data/codex/brief-*.md` and the shared
instructions in `S/data/codex/astra/ASTRA-COMMON.md`, `CLAUDE-COMMON.md`, `UNSEEN-BRIEF.md`, `OPPONENT-BRIEF.md`.

| Tool | What it does | Command line as used |
|---|---|---|
| `S/tools/cx.sh` (19 lines) | `codex exec` with account fallback: tries the Plus account first; on "usage limit / rate limit / 429" in the log tail it writes a 3-hour skip marker and reruns on the default account; appends one line to `data/codex/accounts.log`. Stdin closed, output to the log file. | `nohup tools/cx.sh data/codex/<log> -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write -C "$PWD" "Follow the brief in data/codex/brief-<name>.md exactly." > /dev/null 2>&1 &` (counting jobs: `-m gpt-6.1-sol ... medium`) |
| `S/tools/codex/codex-build.sh`, `codex-analyze.sh`, `S/tools/codex-continue.sh` | The first (10-01) wrappers: build phase only, analysis phase, "continue the work with Codex when Claude is unavailable". | `codex-build.sh <task-slug> "<task line>"` |
| `S/tools/mk_top_briefs.py` | Generates the per-question briefs for the top-team study from a header template. | read |
| `S/archive/final-session-scripts/cx*.zsh` | The launchers (`cxlaunch`, `cxorbit`, `cxskku`, `cxhidden`, `cxfinal`, `cxcheck` which shows limit markers, running jobs and newest briefs). | `zsh cxcheck.zsh` |
| `S/tools/sweep_games.py` + `sweep_loop.sh` | Automatic analysis rounds: every 5 minutes start syntheses of finished rounds; start a new round when an online queue finished or a ranked game was lost. Stopped at 14:30 KST on 10-09. | `nohup tools/sweep_loop.sh &` (read) |
| `S/data/codex/astra/<name>/` | One folder per worker (80 on disk): its scripts, notes and `report.md`. | |
| `B/work/loop/runner.py` | See section 7. | |

Brief template (what every successful brief contained, from `ASTRA-COMMON.md`): the game in a paragraph and who wins; the
bot and where its source is; where the data is, read-only, with exact folder names; the rules (write only under your own
folder, no network, no games, count from replays, mark `[M]/[C]/[E]`, no map-specific rules because the qualifier maps are
unseen); what a deliverable is (a "card": one concrete rule, where in the source it goes, the replay count that would show
it works, what would show it wrong; "no card" is a valid answer); and a word limit for the report.

Traps:

- Codex numbers were wrong at least once on 10-07; the standing rule was to verify one key number from the worker's own
  report on local games or replays before acting (handover 10-09 section 1).
- Workers that finished without a report: wait on files (section 9).
- Capacity: both Codex accounts hit limits (`cx-fallback-test.log`, `cx-second.log` in the archive record the tests of the
  fallback); the 3-hour skip marker avoided retrying the limited account on every call.
- Models for roles: the log's model table (10-07 12:2x) records jun's correction that anything needing thinking goes to Opus,
  and later (10-08 22:35, 10-09 00:49) that thinking jobs may go to Codex "astra" in parallel when Claude capacity is short.
  The tools did not care which model; the briefs did.

---

## 9. Process hygiene: slot limits, killing a process tree, waiting without polling

Lesson: long jobs on one laptop survive only if (a) each is detached and restartable, (b) you can stop exactly your own
processes, and (c) you wait on files, not on a person's report. The scripts for these are 10 to 25 lines each.

| Tool | What it does | Command line |
|---|---|---|
| `R/engine/run_game.py` `game_slot()` | Machine-wide limit of concurrent games through four `flock` lock files; lock files must never be deleted. | automatic |
| `S/archive/final-session-scripts/killtree.py` | Stop every process whose command line starts with a prefix, and all its descendants, by PID (SIGTERM, then SIGKILL after 2 s); never itself. | `python3 killtree.py "<command prefix>"` |
| `stopround.py` (archive) | Stops one analysis loop and every job of one round by PID, and nothing else (used 10-09 when round 1055 fanned out over the whole backlog and overloaded the machine). | |
| `h2hrestart.py`, `relaunch.zsh`, `start*.zsh` (archive) | Restart a batch with another width or order; start each batch detached only if it is not already running (`pgrep -f "tmp/<script>"` guard). Finished games are skipped on restart. | `nohup zsh <script> > <out> 2>&1 &` |
| `until.zsh` (archive) | Return after N seconds or earlier when a new `...-done` line appears in `solo/runs/run.log`. | `zsh until.zsh <seconds>` |
| `wait_any.sh` (archive) | Return when any watched thing changes: online result files, Codex reports, build `done.txt`, synthesis reports, new `...-done` lines, the size of the desk inbox. Snapshots with `cmp` every 30 s and prints what is new. | `zsh wait_any.sh` (run in the harness background mode so it wakes the session) |
| `S/tools/wait_diag.sh` | Wait until the first of named diagnostic runs has a result line; print its cost and result text. | `wait_diag.sh <name>...` |
| `S/tools/loop_watch.py` | Exit with a short reason when the card loop needs a look. | `python3 tools/loop_watch.py` |
| `S/archive/final-session-scripts/stoplocal.zsh` | Stop the remaining local batches, print final tallies, then the team feeds and rank. | |

Rules that came out of incidents (each is in the handover or log):

- Stop processes by PID only. A builder ran `pkill -f "xargs -P 2"` on 10-08 19:06 and cut the whole local queue; on 10-09 05:03
  an overload (load average 76, 24 games at once) was cleared by killing four batches by PID. Handover 7.1: "pkill pattern forbidden".
- The assistant session's command time limit (10 minutes) can kill batches started from it. Start detached with `nohup`
  and let `relaunch.zsh` restart the ones that are not running.
- Write the "done" marker the waiter looks for in the batch script itself (`echo "<name>-done $(date +%T)" >> solo/runs/run.log`).
- Finished subagents (Claude's, which die with the session) must be stopped after their report is processed; Codex jobs,
  queue runners and collectors started with `nohup` survive the session.
- This worktree session refuses complex shell lines; the working method was to write the script with the file tool and run
  `zsh <absolute path>` (log, line 682). Spaces in the Korean project path need quotes everywhere.

---

## 10. Consolidated trap list (dates from the log)

| Date (KST) | What happened | Cost | Rule |
|---|---|---|---|
| 10-07 (date inferred), about 12:15 | Server refused unswbc 1.2.7 uploads ("1.2.9 is out") | One failed upload attempt, a separate venv | Pin and separate the upload client; test an upload early each day |
| 10-07 | Local game slot set to two machine-wide | All local batches ran two games at a time until 10-09 13:52, including batches started "8 at a time" | Print slots and running games at batch start |
| 10-08 19:00 to 22:13 | `smoke.py` freeze constant already passed | All online tests refused for roughly two hours; two classifier refusals of the edit | One config value for deadlines; check on day 1 |
| 10-08 19:06 | `pkill -f "xargs -P 2"` by a worker | Local queue lost (arms stopped between 24 and 57 of 64 games) | PID-only kills |
| 10-09 05:03 | 24 games at once, load 76 | Four batches killed | Cap by CPU, not by slot count |
| 10-09 10:24 | Portal-scouting bug only visible online | One version live with a team-wide stall on portal maps | Keep local copies of every server map; generated suite needs portal maps |
| 10-09 11:06 | `replay2map.js` broken (deleted dependency) | Seven ladder maps missing locally until `convert.py` | Keep tools independent of folders that get deleted |
| 10-09 13:52 | Slot limit discovery (above) | | Set to 4 |
| any | `viewer.js` points into a deleted folder | The JS study stack is dead | Vendor the parser; do not import from sibling projects |

---

## 11. What we would build first next time

Ordered by how much of the last three days depended on it (measured by the counts in section 0 and in the archive scripts).

1. **The local rig** (first day): `play.sh` + a slot-limited launcher with `flock`, low priority, result folder per game,
   one-line `result.txt`. Plus the two tally scripts and the `...-done` line convention. Ours was about 160 lines plus 30.
2. **Build-by-switch**: a 20-line `mkbots.py` and the rule that every behaviour is a default-off constant. Add the identity
   check (all-off hash recorded in the docs) on the same day, and a `chk`/`up` script that refuses to upload when it fails.
3. **The server tool pair** with plan-by-default, `--expect-active`, a ledger and key redaction (`online.js`, `submit.js`),
   plus `submit.js check`. Write the collector (`collect.sh` shape: list, download new, sleep) the same day and start it
   before the first ranked game: other teams' games are only available while they are still listed.
4. **The true-state replay reader** with an independent recount of a sample, in a stable path, plus `look` (draw one dragon's
   view) and a death classifier. Everything else was thin scripts on top.
5. **A queue runner for online tests** (`at-q.sh` shape: a text file of jobs, wait for ticket room, abort if the live bot
   changed) and a **status script** (`poll.zsh` shape). Read the deadline from one config file.
6. **A map generator with a legality validator and a replay-to-map converter**, validated by round trip on known maps.
   Include portal-heavy and tiny and huge families from the start; keep a local copy of every map the server uses.
7. **Process hygiene scripts**: `killtree.py`, `wait_any.sh`, a `relaunch` that starts detached jobs only when not running.
8. **The worker wrapper** (`cx.sh`) and a standard brief header. Do this only after 1 to 5 exist, because workers are only
   as useful as the tools and data they can read.
9. Last: the channel mirror and PR watcher. A bot with commands and buttons (our `meowbot.py`) is optional for a team of
   three; I (the writer of this chapter) did not find a measurement of how much it saved, so treat that as unproven.

What never got proven about the toolbox: how much each of the many one-off analysis scripts changed a decision (the log
records conclusions per analyst, not per script); whether the 4-slot limit is right for another machine; whether
`fingerprint.js` would have replaced the byte-compare procedure (it was written on 09-30 and not used afterwards).

---

## Appendix A. One-off and retired scripts, by folder (counts from disk on 2026-10-10)

| Folder | Files | What is in it |
|---|---|---|
| `S/tools/` | 108 entries: 61 `.py`, 34 `.js`, 4 `.sh`, 25 of them tests/checks | Kept ones are in sections 1 to 9. Retired: `baseline_study.js`, `decisions*.js` (5), `mass_ledger.js`, `fragment_study.js`, `sonar_study.js`, `timing_study.js`, `matchup_study.js`, `mech_check.js`, `proxy_check.js`, `pearl_layout.js`, `observe_*.js`, `online_compare.js`, `online_wave.js`, `eval.js`, `pair_ab.js`, `fetch_rules.js` (saves the public rules pages as Markdown), `export_replay.js`, `firstdiv.js`, `top_features.js`, `top_metrics.py`, `wave_triage.js`; all from 09-27 to 10-05 and dependent on the broken viewer or on folders no longer present |
| `S/data/analysis/ladder/dossier/work/` | 359 `.py`, 603 `.jsonl`, 28 `.json` | Analysis scripts named by two-letter job prefix: `o1` (35, the growth/economy/queen set from the "diag-one1" study), `ec` 17, `wo` 16, `fd` 15, `to` 14, `as` 14, `op` 13, `tq2` 13, `tr` 13, `st` 12, `wq` 11, `ta` 11, `sc` 11, `bm` 11, `hg` 10, `au` 10, `dr` 10, `tq` 10, `lg` 10, `at` 9, others fewer. The `.jsonl` files are per-game caches. Only `o1_scan`, `o1_look`, `o1_local`, `o1_sweeptab` and `o1_ledger` were imported by later scripts |
| `S/data/analysis/ladder/dossier/{online,local}/` | 4 + 12 `.py` | `label_report.py`, `replay_format.py` and small helpers |
| `S/data/codex/astra/<analyst>/` | 80 folders; 739 `.py`, 67 `.zsh`, 40 `.sh`, 4,682 `.json` | One folder per worker. Shared ones: `qexit-opus` (`qdeath.py`, `classify.py`, `cmp.py`), `stuck-opus` (`detect.py`, `agg.py`, `geom.py`), `watch17-opus` and `watch19-opus`, `qdead-opus` (`census.py`, `look.py`, `run.py`), `opp-*` (`tab.py`, `poll.py`), `maps-sonnet` (`convert.py`), `mapgen` (`gen.py`), `sweep` (the automatic rounds) |
| `S/archive/final-session-scripts/` | 229 files: 85 `.zsh`, 21 `.py`, 29 `.jobs`, 14 `.switches`, 28 `.txt`, 18 `.out`, 9 `.bin` | The last session's scripts: `up14` to `up21` (upload), `h2h15` to `h2h17`, `lcheck*`, `pcheck*`, `portalcheck*`, `final19`/`final20`, `stress17`, `scrim*`, `announce14` to `announce17`, `cx*`, `inv*` (wrap-up inventories), `rec14*` (record a version in the memo and promise ledger), `*.jobs` (job lists for `xargs`), `*.switches` (switch lists per version), `one*.bin` (binaries kept for byte comparison), `pr-one*` (PR texts) |
| `S/data/online/smoke/*.sh` | 60 (47 named `at-*.sh`) | Per-test launchers (`at-agg9.sh`, `at-qh31.sh`, ...); same shape as `at-q.sh` |
| `R/solo/tools/` | 8 files | `mkbots.py`, `run_arms.sh`, `sweep.sh`, `h2h_tally.py`, `gx_tally.py`, three `chain_m3*.sh` night chains |
| `R/mytools/` | 14 files | The first week's rig scripts (`pair.sh`, `multi.sh`, `six.sh`, `trace.py`, `qdeath.py`, `evalsum.py` ...) |
| `R/tools/` | 5 files | `batch.py`, `build.py`, `check_setup.py`, `replay_format.py`, `show.py` |
| `R/guard.py`, `R/settings.json` | 2 | A Claude Code PreToolUse hook: blocks strings naming the other projects, network commands and binary inspection of the opponent; exit 2 with a reason. A hook, not an OS sandbox. |
| `B/work/` | 85 `.py`, 37 `.sh`, 49 `.txt` | QWQ's analysis and A/B scripts: `ab.py`/`ab2.py`/`ab3.py` (parallel A/B per map, seed, seat with `--set L:NAME=VALUE`), `paired.py`, `bc.py` (event-by-event body reconstruction), `qa1.sh`... (night batches), `crawl.py`/`ladfetch.py`/`tops.py` (download games from the public API into TSV indices), `worker.py` (a distributed game worker that fetches bots and maps from a server), `nr_*.txt` (game lists), `card_*_check.py` (one check per loop card), `plan.md` (the hourly-loop state, 646 lines). Paths inside many of them point to absolute paths on QWQ's machine |
| `B/` root | `ab.py`, `tune.py`, `sim.py`, `fitness.py`, `replay.py`, `quick.sh` | A/B, an evolution-strategy tuner over `constexpr` constants (`tune.py`), a minimal protocol driver that reproduces a decision (`sim.py`, no portals), length curves from `-v` output (`fitness.py`) |

I did not read the bodies of the 359 + 739 analysis scripts; their purposes above come from folder names, docstrings and
the log. Anything not described in a row is "not recorded".
