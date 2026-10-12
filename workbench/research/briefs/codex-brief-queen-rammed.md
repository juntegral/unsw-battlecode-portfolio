# Codex brief: why our queen still dies (v1.8 default), as input for the bunker design (analysis only)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read:
- `AGENTS.md` §4;
- `docs/WORKQUEUE.md` Q (the Q2 items: "bunker" and "rammed while L≥4");
- `versions/v1.8/VERSION.md` §§1–16;
- `research/observations/queen-mechanics.md`: the reach M = ceil(L/4)+L−2, the safe cycles and the vault condition;
- `research/observations/queen-early.md`.

Replay tools need `UNSW_RULES=123`.

## Data
All existing v1.8-default and candidate games against `exp/q2/bot-hunter` and `proxy4_king`:
- `exp/q2/cand4-*`;
- `exp/q-analysis`'s sets;
- the off/on arms of `exp/q2box`, `exp/qsight`, `exp/q1c` and `exp/freecost`.

Use only the arms whose build equals the current v1.8 default for the main census. Others are side cohorts. List which is which.

## Questions
1. **Every queen death in the main census.** Record:
   - round, cause, her length;
   - the killer: id, length, free steps, path length, and whether it was in her view the turn before;
   - her room/cycle state: inside a cycle she could circulate, open area, corridor, or pocket;
   - our pieces within 3 of her;
   - whether a "safe" first step existed by the queen-mechanics reach formula.
2. **Classes with sizes.** For example: hunter from outside her view; trapped by our own bodies; walked into reach; doomed by geometry; no safe step existed.
3. **For the largest classes, what would have saved her?** Examples: a vault (a cycle she controls with a single body-blocked entry), a screen of pieces between her and the hunter, keeping her length ≥ X for free-step escape, staying in a room with N tiles.
   - Use the vault condition and the safe-cycle catalogue, and check them against the actual positions.
4. **Elite comparison** where possible (`research/observations/queen-early.md`): how did the 24 surviving elite queens live?

## Deliverables
- `exp/queen-rammed/tables.json`.
- `research/observations/queen-rammed.md`, in Korean, with:
  - classes and sizes;
  - 3 board pictures;
  - a ranked list of design options, each with the mechanism it targets and its expected effect.
- `exp/queen-rammed/SUMMARY.txt`, written last (10 lines).

## Rules
- Write scope: `exp/queen-rammed/**` and `research/observations/queen-rammed.md`.
- Do not change the bot. No games, no commit, no network.
- Keep code comments short.
- Target: about 1.5 hours.
