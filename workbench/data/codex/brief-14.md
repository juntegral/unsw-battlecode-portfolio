# Brief: finish the #14 check (EC_STATE_SPLIT) from finished runs

Worktree: ~/meow-bigmap (branch exp/bigmap-state, commit 1580105 adds the toggle EC_STATE_SPLIT and work/splitcheck.py).
Card: github.com/forrest-gan2005/battlecode/issues/14 "Replace the big-map split stop with game-state signals".
All game runs are already finished. Do NOT run new games.

Inputs in work/ec_results/:
- prereg.md: pre-registered criteria, written before any result. Judge only by these, add no new criteria.
- ident_EC0.txt: toggle-off identity check.
- mech_big.json/.log, mech_splitcheck.txt: mechanism run on 41 big maps (tags B61 = v61 baseline, ES = toggle on).
  If mech_splitcheck.txt is incomplete, rerun `python3 splitcheck.py B61 ES` from work/ if the replays exist.
- held.json, heldT.json (transposed maps), old.json (old 10 ladder maps, x8): paired outcome runs.
  Rows are ab3 format: tag, map, seed, side, win, us, them.
- results.md: a draft.
- See ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/../../../battlecode/work/ab3.py for the row format if needed.

Steps:
1. For each outcome set, compute paired flips of ES vs B61 by (map, seed, side): wins, +, -, net, and the per-map-family breakdown.
2. Check each prereg mechanism criterion with numbers, and the outcome bar written in prereg.md.
3. Write work/ec_results/test-comment.md: a GitHub comment in English, short, in the style below, under 35 lines. Start with
   "[test] EC_STATE_SPLIT vs v61". Include:
   - setup;
   - the mechanism table (criterion, expected, observed, pass/fail);
   - the outcome table (set, games, ES only, B61 only, net);
   - a one-line reading (supported / not supported / inside noise) by the prereg rules;
   - one suggested next step.
   Do not overclaim. Noise: paired SD is about 0.63 per game, so about ±8 for 160 games.
4. Write work/ec_results/codex-report.md (any language, under 20 lines): what you computed, and anything odd in the data.

Do not commit, push, post to GitHub or touch any process. Use python3 stdlib only.
