# Codex brief: how teams handle the queen in the first new-rule games (unswbc 1.2.3)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`, especially the 1.2.3 notes;
- `rules/structure.md`, `movement.md`, `execution-order.md`, `splitting.md` and `death.md`.

What the new rules say:
- the longer queen (lowest-id dragon of a team: 0 or 1) wins at r500;
- a dead queen counts as 0;
- tiebreaks: the longest living dragon, then total length;
- the first ceil(L/4) steps per turn are free;
- the queens (ids 0 and 1) act first in every round.

## Important: simulation rules
Our replay simulators default to the OLD movement cost. For these games use the 1.2.3 rule:
- `tools/mass_ledger.js` takes `perGame(R, {rules:'123'})`;
- `tools/top_features.js` reads the env `UNSW_RULES=123`.

Without this, lengths drift down on every free sprint. Take deaths from the replay's `dragonDeath` events; they don't depend on the simulation.

## Data
- `data/elite/index.jsonl`: games with `at` ≥ `2026-10-01T11:08Z`, about 264 new-rule games among the followed elite teams. Replays are under `data/elite/<battleId>/`.
- **Side cohort, local 1.2.3 games:** `exp/q2/*/games/` (our v1.7/v1.8 candidates against proxy4_king and a queen-hunter bot) and `exp/v16/q1/` (the conversion agent's queen-feeding runs).

## Questions
1. **Queen fates.**
   - Alive at r500? Death round and cause (head-to-head, hit body, wall, self, no valid action).
   - Who killed her: an enemy head or our own body? A deliberate hunter or an accident?
   - Recount independently. A previous quick read gave "winners' queens alive 8, losers' 16", which can't hold under the rules, so explain the correct split. Cases: both alive, only the winner's alive, only the loser's alive (must be 0 by rule), both dead.
2. **Surviving queens.** Where do they live? Length curve, distance to the nearest enemy head, whether they loop or coil, room size, escorts.
3. **Assassination.** How often do enemy heads approach a queen within free-step reach? How many head-to-heads on queens look deliberate?
4. **Tiebreak games** (both queens dead): what decided them, and the longest dragon's length.
5. **Free-step use.** Steps per move by length. Do teams exploit the free steps, with long dragons moving 2–3 steps per turn? Are there early long dragons?
6. **Adaptation.** Which teams already protect their queen, and how? Compare with their old-rule behaviour if visible.
7. **Recommendations** for our queen safety, assassination and hedge, with N, as hypotheses.

## Deliverables
- `exp/queen-early/tables.json`, written first.
- `research/observations/queen-early.md`, in Korean:
  - keep [사실] and [해석] apart;
  - give N everywhere;
  - include game ids and rounds for the deep reads;
  - include board pictures (`node eval/board.js` or `exp/v16/board.js`, with `UNSW_RULES=123`).
- `exp/queen-early/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** `exp/queen-early/**` and `research/observations/queen-early.md`. Do not commit.
- No network, no uploads, no games.
- At most 2 worker processes, with `nice -n 10`.
- Pause if free disk drops below 21 GB.
- Recount the key numbers independently.
- **Target:** about 3 hours.
