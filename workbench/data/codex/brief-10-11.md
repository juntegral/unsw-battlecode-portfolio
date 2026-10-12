# Brief: finish the #10 / #11 checks (QG_SAFEZONE, QG_CORNER) from finished runs

Worktree: ~/meow-queen (branch exp/zhe-queen).
- Commit f8dd8d8 adds the toggles and work/zonerun.py, work/zonecheck.py, work/ab3q.py. Read its message: `git log -1 f8dd8d8`.
- Cards: work/card10.md (#10 queen safe zone behind a portal) and work/card11.md (#11 queen fallback in a kelp corner).
  They hold the claim, expected signal and "what would show it's wrong". These are the criteria. Add no new ones after looking at results.
- These are Zhe's ideas. The reading should help Zhe judge; Zhe makes the decision.

Data (all runs finished; do NOT run new games):
- work/zm1/: kept replays with logs. Tags: B61 = v61 baseline, Z10/Z10b/Z10c = safe-zone versions (Z10c is the latest, v3), Z11 = corner.
  Logs zm1.log..zm4.log tell which run made which. Use `python3 zonecheck.py zm1 B61 Z10c` and `python3 zonecheck.py zm1 B61 Z11`, with --maps if needed.
  Note in your report which maps each tag covers.
- work/nh1.json (+ nh1.log): ab3q outcome run on held-out big maps, tags B61, Z10, Z11 (check which build "Z10" is there from the process args in nh1.log, if shown).
  Rows: tag, map, seed, side, win, us, them (+ queen fate fields from ab3q).

Steps:
1. Mechanism per toggle:
   - how often it fires: zone found / entered, corner anchored;
   - queen survival and death round vs B61, paired;
   - whether the falsifier on the card is hit.
2. Outcome: paired flips vs B61 in nh1.json (wins, +, -, net), per map family. Noise: paired SD about 0.63/game.
3. Write work/test-comment-10.md and work/test-comment-11.md: GitHub comments in English, each under 35 lines, starting "[test] QG_SAFEZONE vs v61" / "[test] QG_CORNER vs v61". Include:
   - setup;
   - a mechanism table;
   - an outcome table;
   - a one-line reading (supported / not supported / inside noise);
   - one suggested next step.
   No overclaiming.
4. Write work/codex-report-queen.md (any language, under 20 lines): what you computed, and anything odd in the data.

Do not commit, push, post to GitHub or touch any process. python3 stdlib only.
