# Codex brief: how much of an unseen map can the bot know, and when? (input for W3, the runtime map model)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`
- `docs/WORKQUEUE.md`, task W3
- `docs/arch/unknown-maps.md` and `docs/arch/flow-turn.md` (the world-update part)
- the rules in `rules/ALL.md`:
  - **Vision:** each dragon sees the 7×7 square around its head, not through portals.
  - **Map symmetry:** vertical mirror, horizontal mirror or 180° rotation.
  - **Spawn countdowns:** visible in vision; `min_gap`/`max_gap` are hidden.
  - **Sonar:** see the sonar section.

Also read `research/observations/general-principles.md` §observability, which says "r30: the union of allies' vision is the sharing upper bound".

## Why
The qualifier is played on unseen maps. Our swarm features need per-map tables (spawn/fountain groups, territory, frontier bins, the 2-core and pockets). W3 will build these tables at runtime from what our dragons have seen. To design W3 we need to know, from real games:
- what our team can have seen by round r;
- when the symmetry type can be determined, and with it the enemy start;
- how accurately fountains, spawn rates, pockets and frontier bins can be estimated from partial observation.

## Data
- Our local replays from W1: `exp/gen/v12-F-H`, `v12-F-K`, `v12-S-H`, `v12-S-K`. These are bundled maps plus known maps with recognition off, so our bot did not have map tables.
- Our online sets (W0–W12, `v1-w1..3`).
- Elite games in `data/top`, used to see how fast a strong team's union of vision grows.
- The maps themselves: `maps/online-20260927`, `maps/server-b`, `maps/bundled`. They give the ground truth for kelp, portals and spawn gaps.

## Questions (per map and layout, ours vs elite)
1. **Vision coverage.** The union of all our dragons' 7×7 windows up to round r (r = 5, 10, 20, 30, 50, 100, 200), as a share of all tiles. Separately, the share of spawn tiles seen at least once, and the share of fountain tiles.
2. **Shared knowledge.** Sharing is limited: sonar carries little information per message. Estimate what a single process can realistically know if it only knows its own windows, its parent's knowledge inherited at birth, and fields carried by sonar. Report the coverage per process as a distribution.
3. **Symmetry.** The first round at which the observed tiles rule out all but one symmetry type, consistent with the true one: for the team union, and for a single process. After that, mirroring doubles the known map. Report the coverage with mirroring.
4. **Estimating fountains and spawn rates.** From countdown observations in vision, how many rounds does it take before the observed reset samples classify a tile as a fountain (gap mean ≤ 12) correctly (precision/recall vs the map file)? How well does the spawn-rate estimate track the true rate?
5. **Pockets and 2-core.** Build the 2-core from the edges seen so far, treating unknown edges as open (optimistic) or as walls (pessimistic). How do precision and recall of the pocket tiles evolve with r?
6. **Frontier bins.** Take the enemy start as the mirror of ours, using the decided symmetry; while the symmetry is undecided, use the most likely type. Compute f-bins on the known region, unknown tiles open. Compare with the true f-bins: accuracy by round.
7. **Recommendations for W3.**
   - Which tables are reliable by r10, r25 or r50?
   - Which inheritance or sonar fields would raise single-process knowledge most, and by how much?
   - What should be explored early to learn the map fastest?

## Deliverables
- `exp/observe/tables.json`, written first.
- `research/observations/observability.md`, in Korean:
  - keep [사실] and [해석] apart; give N everywhere;
  - state the method;
  - end with a table: "table → reliable from round … with accuracy … under assumption …".
- `exp/observe/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** `exp/observe/**` and `research/observations/observability.md` only. Do not commit.
- No network, no uploads, no new games.
- At most 2 worker processes. Pause below 10% free memory or 21 GB free disk.
- Keep caches compressed.
- Recount the key numbers independently.
- **Target:** tables by 16:30 KST, everything by 18:00 KST.
