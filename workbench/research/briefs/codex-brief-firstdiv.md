# Codex brief: first-divergence causal check, a reusable tool (analysis only)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read:
- `AGENTS.md` §4;
- `research/briefs/codex-build-template.md`, especially "Measure 'no harm elsewhere' causally";
- `exp/bodymem/RESULT.md` and `exp/bodyx/RESULT.md`.

Replay tools need `UNSW_RULES=123`.

## Why
An on/off pair (same map, side, opponent, seed) is identical until the first round in which any of our dragons acts differently. That round is a natural fork: same state, two different actions, and both continuations were actually played. So we can test harm causally without a forking engine.

## Build
Write `tools/firstdiv.js`. Input: an on set dir and an off set dir (runq layout: rows and replays). Per key it should:
1. Find the first round R where our action log differs: dragon id and action, on vs off. Confirm the boards at the start of R are identical (all dragons and pearls). Report any key where they are not.
2. For the changed dragon, and separately for our queen, record the fate in each arm:
   - alive or dead at R+1, R+3 and R+10;
   - death cause if dead.
3. Classify each key:
   - **harm:** on died within k, off survived;
   - **help:** off died within k, on survived;
   - **both** or **neither**.
   - Do this for k = 1, 3 and 10, and for the queen with k = 10 and 50.
4. Keep the full per-key rows: key, R, id, both actions, the indicator tags if present, and fates.

## Apply it to
- `exp/bodymem` on/off: the current question.
- `exp/bodyx` on/off: this checks the earlier coordinator call that set BODYX on.
- `exp/freecost` and `exp/qsight` on/off: retrospective.

For the harm cases, draw boards of the fork round, on vs off (`exp/v16/board.js`), and say in one line each whether the switch's own logic made the different choice. For BODYMEM, also say whether the choice came from a memory difference.

## Deliverables
- `tools/firstdiv.js`
- `exp/firstdiv/<set>.json` (per-key rows)
- `exp/firstdiv/RESULT.md`, in Korean: per set, a harm/help/both/neither table for each k, with the harm-case pictures and one-line explanations.
- `exp/firstdiv/SUMMARY.txt`, written last (8 lines). Include one line per set: "harm vs help at k = 3 and queen k = 50".

## Rules
- Write scope: `tools/firstdiv.js` and `exp/firstdiv/**`.
- No games, no bot changes, no commit, no network.
- Keep code comments short.
- Target: about 1 hour.
