# Builder notes (solo project, team 1119 "meow") — read fully before touching anything

## The game and the bot
- Game: two sides of "dragons" (snakes) on a torus grid with kelp walls and portals. Dragons eat pearls to grow, split into two,
  pay segments to sprint, and a head rammed into an enemy head kills both. Each dragon decides alone from a 7 by 7 view plus
  what the side shares over sonar. Rules and engine notes: `~/meow-redteam/README.md`, `~/meow-redteam/docs/`.
- Who wins ("Slay Queen"): the side whose QUEEN (lowest starting id) is longer at the end; a dead queen counts 0; then the longest
  dragon; then total length. In our 30 online games of the live build: queen alive at the end = 7 won of 8, dead = 7 of 22.
- Bot: one C++ file, `~/meow-redteam/solo/src/solo/main.cpp` (6,228 lines) + headers in `~/meow-redteam/solo/src/main3/`.
  Every behaviour change is a `constexpr` switch near the top, default OFF. The live bot is that file with this set on:
  `ZONE_NEARER:true,POCKET_LOOP:true,HARVEST_PORTAL:true,SPAWN_CLEAR:true,TRADE_EVEN:true,LEADER_FULL_UNITS:56,HUNT_SMALL_RATIO:2,QS_KEEP_LEN:3`

## Hard rules
1. Work ONLY on your own copy: `~/meow-redteam/solo/src/<your dir>/main.cpp` (copy of `src/solo/main.cpp`). Never edit
   `src/solo/main.cpp`, `src/main3/`, tools, the engine, other people's bots or runs, or anything under the team repo.
2. A new behaviour = one new `constexpr` switch (plus at most two tuning constants), default off, placed beside the related constants.
   With every switch off the bot must behave exactly as before.
3. No comments in the code. No map names, no per-map or per-size tables, nothing that depends on orientation or on which side we are.
4. Do not make dragons timid (no general "avoid enemies" terms for ordinary dragons). The queen is the exception: she may be careful.
5. Say whether your change touches the queen, the leader, or feeders, and how.
6. Judge by behaviour counted in replays, never by wins. Separate what you measured from what you infer.

## Build and test
- Bots: `cd ~/meow-redteam/solo && MKSRC=src/<your dir>/main.cpp python3 tools/mkbots.py "<name>=SWITCH:value,SWITCH:value"`
  writes and compiles `bots/<name>/`. Names: 6 characters for a plain bot, e.g. `m5ab01`; arms that play are named `<5-6 chars>_vh`.
- All-off identity check (mandatory, before any game): build `<name>=` (no switches) from your copy; `shasum bots/<name>/bot` must
  start with `e01afcc67c88` (the current all-off binary). If your change alters a runtime expression and the hash differs, play
  3 games and compare with the same games of an all-off bot built from `src/solo/main.cpp` (same map, seed, side, opponent):
  `game.replay` must have the same size and differ only in the bytes of the bot name.
- Games: `cd ~/meow-redteam && SOLO_MAPS="<map paths>" SOLO_OPP=solo/bots/m3hunt ./solo/tools/run_arms.sh <seed> <arm>...`
  plays each arm on each map on both sides against `m3hunt` (current team main + queen hunting: the only local opponent that chases
  a queen). Output `solo/runs/<arm>/<map>-seed<S>-side<K>/{game.replay,result.txt}`; an existing game is skipped.
  The baseline arm `m3b7qk_vh` (= the live build against m3hunt) already has seeds 1 and 2 on 32 maps (`ls solo/runs/m3b7qk_vh`),
  so compare your arm with it on the same map, seed and side and do not replay the baseline.
- The machine is shared and only two games run at a time (3 to 8 minutes each, your games queue behind others).
  Budget: at most 24 games for your arm(s) in total. Pick the maps with care (mix of sizes; games where the baseline queen was
  chased or rammed are the informative ones). Start the games in the background and keep working while they run.
- Replay reading: reuse the parsers in `~/…/unsw-swarm/data/analysis/ladder/dossier/local/count_local.py` (local runs; do NOT run its
  full recount, it is heavy) and `dossier/work/tq2_*.py` (queen company and chase measures used in `dossier/diag-topqueen.md`);
  full path prefix `~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/`. Put your own scripts in your src dir.
  Run anything heavy under `nice -n 10`.

## What to hand back (final message, under 500 words, plus files in your src dir)
- `<your dir>/<name>.diff` = `diff -u src/solo/main.cpp src/<your dir>/main.cpp`, the switch name(s) and the on-values.
- Identity proof (hash or the 3-game comparison).
- A small table, baseline against your arm on the same games: the behaviour counts your brief asks for, and the cost
  (own dragons and total length at r100 and r300, pearls eaten). Number of games behind each number.
- Two replay moments (game, round, tiles) that show the switch doing its job, and one where it did harm or nothing.
- Your honest verdict: fires as intended or not, the main risk, and what you would change with one more hour.
