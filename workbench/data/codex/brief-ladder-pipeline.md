# Build the hourly ladder-analysis pipeline (collector, per-game rows, runner)

Work in this repo (`unsw-swarm`). Create new files only; do not change existing tools. Commit nothing (the caller
commits). Do not post anywhere. Never run `submit.js`, never run `online.js request`, never pass `--confirm` to
anything. The only server calls allowed are `node tools/online.js battles|battle|download|submissions|maps`
(all read-only, no tickets). Do not print `docs/api.txt` or `docs/discord.txt`.

Team: "meow", id 1119. Ranked ladder battles are 5 games each on random maps; about 10 battles arrive per hour.
The server lists only our last 200 battles, so anything not downloaded is lost after about a day.

## 1. `tools/ladder_collect.py` (no model)
- Reads `node tools/online.js battles --limit 200 --json` (rows: id, ranked, opponentId, opponent, opponentElo,
  eloChange, results, wins, losses, outcome, replayId, at). Keeps ranked battles only that are finished.
- For every ranked battle not yet on disk, downloads it with
  `node tools/online.js download <id> --out ladder/<id> --no-events --purpose "ladder analysis"` (read the tool's
  help and an existing folder such as `data/online/dl-20261004` for the exact layout; files are `game-<id>.json`
  and `M<id>.replay`). One battle per call, sequential, 1 second between calls, at most 150 battles per run.
  A battle counts as done only when every finished game's replay is on disk; retry incomplete ones next run.
- Appends/updates `data/analysis/ladder/battles.jsonl` (one row per battle, stable order by time): the fields above,
  `at_kst`, the game ids and map names, and `our_submission` (see below).
- Polls `node tools/online.js submissions --all --json` and appends one line to
  `data/online/ladder/active.jsonl`: time, the active submission's id / version / name / sourceHash / rating, and
  for every submission its wins and losses. From two consecutive polls the submission whose game count rose is the
  one that played in between. Use this to fill `our_submission` for battles between polls; leave it null (not a
  guess) for battles older than the first poll. Has a `--poll-only` mode for a 10-minute poll.
- Writes `data/analysis/ladder/new-this-hour.json`: battle ids added by this run.
- Idempotent, safe to interrupt, prints one summary line.

## 2. `tools/ladder_rows.py` (no model)
One row per game in `data/analysis/ladder/rows.jsonl`, rebuilt incrementally (skip games already present unless
`--rebuild`). Reuse existing replay parsing: look at `data/online/smoke/bbb-analysis-3/count.py`,
`data/online/smoke/drop-analysis/count.py`, `data/online/smoke/fountain-analysis-2/count.py` and
`data/local/hunter38/harness/work/card_38_check.py` (queen, death causes, reach, board wrap). Which side is ours
comes from the team names in `game-<id>.json` / the replay's DRAGON lines. Fields, all from our team's point of view
with the same figure for the opponent where it makes sense:
- ids: battle, game, map, time, opponent id / name / rating at the time, ranked, our_submission.
- result: win, how it ended (elimination / queen rule / longest dragon / other), last round, final queen lengths,
  final longest dragon each side, total length each side.
- curves at r50, r100, r150, r200, r300, r400 and the end: dragons alive each side, total length each side, longest
  each side, pearls eaten so far each side.
- queen: alive at each of those rounds, death round, death cause (wall / own body / other dragon's body / head-on
  with who rammed whom / none), her length at death, her length at r100/200/300/400/500, pearls she ate, times she
  split; the same for the enemy queen.
- deaths of our dragons and theirs by cause, in three windows (r0-100, r101-300, r301-500).
- head-on meetings: count, and pearls dropped by each side's dead dragons and who ate them within 15 rounds (the
  definition used in `drop-analysis/count.py`).
- pearls: share of all pearls eaten that we ate, in the same three windows.
- map properties into `data/analysis/ladder/maps.json`, keyed by map name: width, height, open tiles, wall share,
  number of portals, wrapped distance between the two queen spawns, number of pearl tiles, and an estimate of the
  share of pearl supply coming from fast-respawn tiles. Server replays hide the respawn gaps (they show 0 0); use
  the interval estimate from `fountain-analysis-2/count.py`, or the real gaps when a local copy of the map exists
  (see how that script finds them). Mark which one was used. Also a simple "corridor" measure (share of open tiles
  with exactly two open neighbours).
- anything that cannot be measured for a game is null with a reason in `row["notes"]`, never a guess.
Also write `data/analysis/ladder/SCHEMA.md`: every field, how it is measured, what is estimated, what uses the
replay's true state, how to load a replay with the shared parser (a short code example), which side is ours.

## 3. `tools/ladder_hourly.py` (runner) with `tools/ladder_guard.py` and `tools/ladder_settings.json`
- Loop until 2026-10-08 20:00 KST: at the top of every hour run collect, rows, then the analyst, then the verifier
  if `data/analysis/ladder/verify-queue.json` is a non-empty list. Between hours, run the collector in
  `--poll-only` mode every 10 minutes. A lock file prevents two runners. Logs one line per step with times to
  `data/analysis/ladder/runner.log`. A failure in one step is logged and the loop goes on.
- Flags: `--once` (one cycle now, then exit), `--no-ai` (skip analyst and verifier), `--first` (see below).
- Analyst call, modelled on `ai()` in `~/01. Project/개인 프로젝트/battlecode/work/loop/jobs.py`:
  `claude -p --model claude-opus-5-5 --effort <e> --permission-mode bypassPermissions --settings
  tools/ladder_settings.json --output-format stream-json --verbose`, cwd = repo root, stdin = the text of
  `data/analysis/ladder/analyst-prompt.md` followed by a line `This run's hour file:
  data/analysis/ladder/hours/<YYYYMMDD-HHMM>.md` and a line with the current time in KST. Effort is `xhigh` on the
  first analyst run ever (no `findings.md` yet, or `--first`) and `high` otherwise. Timeout 50 minutes (90 on the
  first run). The stream goes to `data/analysis/ladder/logs/analyst-<stamp>.jsonl`.
- Verifier call: the same with `data/analysis/ladder/verifier-prompt.md`, effort `xhigh`, timeout 40 minutes, log
  `logs/verifier-<stamp>.jsonl`. After it finishes, the runner moves the queue to
  `data/analysis/ladder/verified/<stamp>-queue.json` and writes `[]` to `verify-queue.json`.
- `tools/ladder_settings.json` installs a PreToolUse hook running `tools/ladder_guard.py`. The guard follows
  `~/01. Project/개인 프로젝트/battlecode/work/loop/guard.py` (read it; do not import or modify it):
  block the credential files, `--confirm`, `submit.js`, `online.js` with anything but
  `battles|battle|download|submissions|maps`, any command mentioning `meowbot`, `meow_`, `discord`, `board.py`,
  `gh` writes, `git push|commit|config|remote`, `curl|wget`, detaching (`nohup`, `&`), and every write outside
  `data/analysis/ladder/` (for the verifier: outside `data/analysis/ladder/verify/` and
  `data/analysis/ladder/verify-results.json`; the runner passes which role via an environment variable).
  Unlike the loop guard, allow `python3 <file>` and also `python3 - <<'EOF'` heredocs; still block `python -c`.
- `tools/test_ladder.py` (unittest, no network, no claude): collector bookkeeping with a fake battles list and
  fake submissions polls (attribution of `our_submission`, incomplete battles retried, idempotence), the guard
  (each blocked class and a few allowed commands, both roles), the runner's effort choice and queue handling with
  the claude call stubbed.

## Run it and check it (this is part of the job)
1. Run the collector for real once. Report how many ranked battles and games were downloaded and the disk size.
2. Run `ladder_rows.py` on everything. Then prove the rows are right:
   - every game's `win` equals the battle's `results` entry for that game, and the per-battle win count equals
     `wins` (report mismatches; there should be none);
   - run your row code on one folder the team already counted, `data/online/smoke/ns39-bob1-new` (15 games vs Big
     Bobs Bots), and compare with the figures the earlier scripts give for the same folder (run
     `data/online/smoke/drop-analysis/count.py` or read its `summary.md` / `rows` to see how; head-on count and
     dropped-pearl shares must agree, or explain the difference);
   - for 5 random ladder games print the queen death round and cause from your rows next to what
     `card_38_check.py`'s death classifier gives on the same replay.
3. Run `python3 tools/ladder_hourly.py --once --no-ai` and show the log lines.
4. Run the tests: `cd tools && python3 -m unittest discover -p "test_*.py"` (the existing 249 must still pass).
Do NOT start the long-running runner and do NOT run the analyst; the caller starts it after checking your work.

## Report (in your last message, short)
Files created; download counts and size; the three checks with their actual numbers; anything estimated or null
and for how many games; test output; anything you are unsure of.
