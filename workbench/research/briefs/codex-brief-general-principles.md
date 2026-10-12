# Codex brief: map-independent elite principles (for a bot that will play UNSEEN maps)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`, the new lineage of our UNSW Battlecode 2026 bot (deep-sea dragon game; team 583; score = longest single dragon alive at round 500).

Read first:
- `CLAUDE.md`, `research/KNOWLEDGE.md`
- the rules in `rules/ALL.md`, especially **Vision**: each dragon sees only the 7×7 square around its head, and not through portals. Maps are symmetric: vertical mirror, horizontal mirror or 180° rotation. Spawn countdowns are visible in vision; min/max gaps are not.
- our per-map studies in `research/observations/`: `map-atlas.md`, `spatial-occupancy.md`, `pocket-harvest.md`, `opening-book.md`, `conversion-protocol.md`. Reuse their tables and code (`exp/map-atlas/`, `exp/spatial*/`, `exp/pocket/`, `exp/opening/`, `exp/conversion/`).

`legacy/` = `../unsw-heuristic`. `data/` and `.cache/` link to its data.

## Why
The qualifier (submissions close 2026-10-09 15:00 KST) is best-of-7 single elimination **on unseen maps**.
- Our bot plays per-map tables only on maps it recognises. On an unknown map it falls back to one engine.
- Everything we learned per map must be turned into rules the bot can apply on a map it has never seen. Such a rule must work from what it can observe at runtime, plus symmetry. An example: "with these geometry features, aim for this many heads by r100 and put this share of them in the middle".

## Population
- **Top-vs-top games:** `data/top/index.jsonl` (about 21,600 games on the 10 known maps; exclude stalled games as before).
- **Elite collection:** `data/elite/`. It holds every battle of the current top-10 teams against any opponent. It started 2026-10-01 11:25 KST and grows every 5 minutes. Opponents' strength varies there, so use it mainly as a check on the elite's own behaviour.
- **Ours:** W0–W12 and the v1 waves (`data/online/v1-w1..3`).

## Questions
1. **Map features computable at runtime.** For each known map/layout, compute the features a bot could estimate early from its own vision, its allies' sonar and symmetry:
   - size, wrap, the share of passable tiles, kelp density;
   - the number and positions of spawn tiles seen and their observed respawn rate;
   - fountain share, pocket count (non-2-core tiles), corridor width;
   - start-to-start distance, isolation (Portals-like), centre-vs-edge spawn share.
   Say for each feature how early (round) and how reliably it can be estimated from partial vision.
2. **Elite behaviour as a function of features, across the 10 maps** (winners vs losers):
   - head-count curve (r25/50/100/250);
   - split speed in r0–50;
   - frontier allocation (middle share at r25/r50/r100);
   - per-head intake;
   - sacrifice clock (onset round, step at r250);
   - pocket harvesting (yes/no, intensity);
   - conversion (line share, king growth r300–500);
   - king safety distance.
   Fit simple, robust relations: per-feature monotone fits or small trees, with leave-one-map-out validation. Report which behaviours are **invariant** (same on all maps) and which **scale** with which feature.
3. **Generalisation test.** With leave-one-map-out (and leave-one-family-out), how well do the fitted rules predict the elite's behaviour on the held-out map? Which rules transfer and which are map-specific?
4. **Recommendations for an unknown-map engine:**
   - concrete rules with numbers, e.g. a head target = f(observed spawn rate, area), and a middle-share target = f(centre spawn share);
   - when to choose a fortress-like vs a swarm-like plan, from features observable by about r10–30;
   - what to do in the first 10–20 rounds to measure the features (exploration).
5. **If the sprint bracket's unseen-map games** (17:30 AEST today, 16:30 KST, best of 7 on unseen maps) appear in `data/elite` before you finish, analyse elite behaviour on those maps separately as a true out-of-sample check. Their map names will not be among the known 10. Otherwise, write a short appendix plan for that check.

## Deliverables
- `exp/general/tables.json`: per map features; per map, class and behaviour; fitted rules with validation. Write it first.
- `research/observations/general-principles.md` (Korean):
  - [사실] / [해석], with N everywhere;
  - the three-stage method (full-population scripts → classes with sizes → deep reads with game ids and rounds);
  - a final table: "feature → rule → numbers → validation score".
- `exp/general/SUMMARY.txt`, written last (15 lines).

## Rules
- **Write scope:** only `exp/general/**` and `research/observations/general-principles.md`. Do not write in `bot/`, `versions/`, `eval/`, other `exp/*`, `legacy/`, `data/` or `.cache/`. Do not commit; the coordinator commits.
- **No network and no uploads.** Do not read `unsw-arena-clean-control/operator-only/` or opponent bot sources.
- **Resources:** at most 2 worker processes. Two agents run local games. Pause if free memory drops below 10% or free disk below 21 GB. Keep caches compressed.
- **Verification:** independently recount the key per-map behaviours and the fit validation, and report both counts.
- **Target:** tables by 15:00 KST, everything by 17:00 KST. If you must stop early, leave the tables and a partial report that says what is missing.
