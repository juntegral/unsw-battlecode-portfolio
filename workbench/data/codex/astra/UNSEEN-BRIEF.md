# Unseen-map health check of the live bot (last hour; report by 14:15 KST)

The qualifier is played on maps nobody has seen. Three times today a rule of ours misfired on one kind of map and nobody had
looked there: short dragons refused every unseen portal (pearls halved on six maps), a territory term left us at 3 dragons for
100 rounds on one map, and on maps of 600 cells or fewer the queen scouted blind portals into closed rooms and died by round 10
in 30 of 30 games on one map. All three were found from online losses, hours late. Your job is to find the next one BEFORE the
deadline, on a family of maps the bot has not been looked at on.

Read first: `CLAUDE-COMMON.md` in this folder (ROOT, the live bot one17 = local bot `~/meow-redteam/solo/bots/mD17`, how to
play, the shell rule: scripts via the Write tool, run with `zsh <absolute path>` or `python3 <absolute path>`), and
`ASTRA-COMMON.md` (the game, replay readers). **At most 3 games running at a time.** You change no bot code. You never upload,
post or touch git. Your folder: `ROOT/data/codex/astra/<your name>/`; new maps go to `~/meow-redteam/maps/un2/<your tag>_*.map`.

Tools that exist:
- Map generator and its notes: `ROOT/data/codex/astra/mapgen/gen.py`, `ladder-params.md` (sizes, pearl supply, portal counts of
  the 17 ladder maps), `loader_check.py`; an earlier set of 33 threshold-probing maps with its generator:
  `ROOT/data/codex/astra/unseen/make_maps.py`, `maps/`, `inventory.md` (which constant each map probes). Generated set in use:
  `~/meow-redteam/maps/gx/` with `INDEX.tsv`. Ladder maps: `~/meow-redteam/maps/ladder/`. Read two map files to learn the format
  (size line, walls, portals with pairing, starts for A and B, pearl beds with respawn gaps). A map must load in the engine:
  play one short game on it before you rely on it.
- Health detectors over replays: `ROOT/data/codex/astra/stuck-opus/detect.py` (usage in its header: `detect.py local <run
  folder name>`; then `cls.py local`), `ROOT/data/analysis/ladder/dossier/work/o1_local.py` (`rows(arm)` for games under
  `~/meow-redteam/solo/runs/<arm>/`, `snap`), `ROOT/data/codex/astra/qexit-opus/qdeath.py` and `classify.py` (queen deaths),
  `ROOT/data/codex/astra/shed-sonnet/` (queen splits).
- Opponents: `solo/bots/m3base` (old main), `solo/bots/mD17` itself (mirror), and for a different style `solo/bots/m3hunt`.

For every map you test, both seats, against m3base and in the mirror, one line with these health numbers for OUR side (and
the opponent's, same script): crash, timeout or illegal-action markers in `engine.log`; first eat round; pearls and dragons at
r25/r50/r100; the share of our dragon-rounds in no-eat loops of 30+ rounds; our queen: death round, cause (rammed / wall / own
body / mate), free cells at her last turn start, portal steps in r0-99, her length at r100/r300/end; how the game was decided.
A map is RED when any of these holds: a crash or timeout; first eat after round 40 while pearls lie within 10 steps of a start;
3 or fewer dragons at r100 while the opponent has 3 times as many; our queen dead before round 50 by wall, own body or mate;
loops above 10 percent of our dragon-rounds; the mirror game decided by something one side did to itself.
For each RED map: the first round where it goes wrong, two 7 by 7 boards (`o1_look.py`), the code path and the constant that
governs it (cite lines of `ROOT/data/online/smoke/one17-bot/main.cpp`), and whether ONE live constant changed back to its
default or to another value removes it: build that arm from `~/meow-redteam/solo/src/solo/main.cpp` with
`MKSRC=src/solo/main.cpp python3 tools/mkbots.py "<name>=<one17 values with the change>"` (values in
`~/.claude/jobs/e2109d93/tmp/one17.switches`) and replay the same game (games are deterministic).

Final message, under 40 lines: first line "ALL GREEN on <n> maps" or "RED: <map family>, <what>, <constant candidate or
'no constant'>"; then the table; then for each RED the evidence. Send a two-line message at once when you see a RED that
repeats on two maps of a family: do not wait for the report. Stop at 14:12 KST and report by 14:15.
