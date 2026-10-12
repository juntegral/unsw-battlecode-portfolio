# Codex brief: why our pieces eat less than elite pieces (W11), especially pearls an enemy could reach

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`, especially §4 step 7: local games are mechanism checks only, and feedback comes from online behaviour.
- `docs/WORKQUEUE.md`, tasks W11 and W7.
- `docs/arch/terms.md`. Note T1 30 / T2 24 against a pearl's +1, and the remark that a static threat is re-added at every DFS step.
- The rules in `rules/ALL.md`: Pearls (spawn countdowns), Movement and Sprinting, Execution order (ascending id within a round), Death (drops ⌈L/2⌉).

Reuse:
- `exp/w7/pearlmiss.js` (corrected: adjacency is taken at turnStart from the pre-move pearl set; the post-move hook made eaten pearls invisible);
- `exp/w7/reach.js`, `exp/w7/reach-pop.txt`;
- `exp/small/`, `exp/spatial/`, `tools/mass_ledger.js`, `tools/top_features.js`.

## Why
Our pieces gain about 0.042 mass per dragon-turn on small boards. Elite Trophy winners gain 0.07–0.12. Splitting (W7b), head count and fights all depend on intake.

The opening agent's corrected pearl metric (Trophy: 174–300 top games; small maps: 40 local games):

| Group | Moves with a pearl one step away | Missed a safe adjacent pearl | Skipped when only in-reach pearls were adjacent | Ate on |
|---|---|---|---|---|
| Elite winners (Trophy) | 6.9% | 14.4% | **19.8%** | 5.9% of moves |
| Elite losers (Trophy) | 10.8% | 12.7% | 21.8% | 9.3% |
| Ours online (Trophy) | 6.6% | 18.7% | **73.6%** | 5.2% |
| Ours local small maps (v1.7) | 6.2% | 28.7% | 76.6% | 4.2% |

Elite pieces eat pearls an enemy can reach; we decline about three quarters of them. Elite pieces are rammed after 16.6% of their reach moves, ours after 33.6%. Elite and proxy pieces also ram shorter or equal targets far more often than we do.

## Data (the whole population, no sampling)
- **Elite:** every game in `data/top/index.jsonl` (excluding stalled games) and in `data/elite/`, all maps. Start with Trophy for comparability, then all maps.
- **Ours, online:** W0–W12 and `data/online/v1-w1..3`.
- **Ours, local:** the v1.7 small-board runs in `exp/w7/`, and the generated-map smoke games in `exp/mapgen/games/`. Qualifier maps will not look like Trophy, so report the generated small maps separately.

## Questions
1. **Decomposing the intake gap.** Per dragon-turn and per move, split it into:
   - pearls visible;
   - pearls reachable first (race);
   - pearls declined under threat;
   - pearls lost to the enemy;
   - travel efficiency (steps per pearl eaten);
   - time spent near spawn tiles and fountains;
   - more dragon-turns versus more per dragon-turn.

   Compare elite winners, elite losers, ours online and ours local.
2. **Eating under threat.**
   - P(rammed before our next turn | ate in reach), against local head balance (d3/d8), length difference and the enemy's sprint budget. Compare elite with ours.
   - When is eating in reach safe enough for the elite?
3. **Races.** When a pearl is reachable by both sides, who gets it? How do elite pieces win races (id order, sprints, approach angle)? How often do we abandon a race we could have won?
4. **Pre-positioning.** Do elite pieces wait near tiles whose countdown is about to fire, or near fountains, and how does that compare with our F-goal fountain pulls? How many pearls does each side eat within N rounds of a spawn?
5. **The share of visible pearls eaten within N turns**, by crowding and local balance.
6. **Recommendations.** Generic, map-independent rules, each with N and the expected mechanism effect, labelled as hypotheses. Each should name the planner term it changes (`docs/arch/terms.md`) and the size of the change. For example:
   - a food-versus-threat exchange rate conditioned on local balance;
   - a race rule;
   - first-step-only threat for food tiles.

## Deliverables
- `exp/intake/tables.json`, written first.
- `research/observations/intake.md`, in Korean:
  - keep [사실] and [해석] apart;
  - give N everywhere;
  - follow the three-stage method: full-population scripts, then classes with sizes, then deep reads with game ids, rounds and board pictures (`node eval/board.js`);
  - end with a rule table.
- `exp/intake/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** `exp/intake/**` and `research/observations/intake.md` only. Do not commit.
- No network, no uploads, no games.
- At most 3 worker processes, with `nice -n 10`.
- Pause if free memory drops below 10% or free disk below 21 GB.
- Keep caches compressed.
- Recount the key numbers independently.
- **Target:** about 5 hours after start.
