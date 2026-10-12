# Codex brief: one document for our philosophy and method, in Korean and English (writing only)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. The user wants a single document of how we work: philosophy, hypothesis testing and judgement. It may be shared with a new team. The method is currently spread over several files. Consolidate it, do not invent it.

## Sources (read only)
- `../unsw-arena/lineages/GROWTH.md`, `LOOP.md`, `BRIEF.md`: growth judgement and the improvement cycle.
- `AGENTS.md` §1, §4 and §5: development procedure, mechanism checks, final-submission criteria.
- `DECISIONS.md`: dated decisions. Extract the method lessons, not every decision.
- `research/briefs/codex-build-template.md`: pre-registration, switch discipline, the causal harm gate.
- `exp/firstdiv/RESULT.md` and `tools/firstdiv.js` (header): first-divergence causal check.
- `research/observations/queen-rammed.md`: the death census as a bug-finding method.
- `../unsw-heuristic/exp/outcome-review/METHOD.md`: census, not samples; a frozen method before deep reading.

## The user's own principles
These come from the coordinator's notes and are authoritative. Mark them as the user's.
1. The goal is to keep finding better logic and keep growing. Site scores and results against specific opponents are signals, not the goal.
2. Feedback is the core. After every test, analyse replays deeply against the baseline. Feedback matters more than results.
3. Real feedback is online behaviour: did each mechanism fire and work against strong teams? Local proxy games are mechanism checks only. "Numbers are poison." Never take comfort from local wins.
4. Carry facts, not verdicts, between waves. Criteria come from the hypothesis alone and are enforced mechanically.
5. Every large analysis uses the whole population (all accumulated games), not samples.
6. Build a generally strong bot, not a map-tuned one. The qualifier uses unseen custom maps, so map recognition is off.
7. Rules first: derive mechanics from the rule text and check them with small simulations.
8. Uploads: upload only, never auto-revert. The first upload is late and only with a complete build. Rollback is the user's call.
9. Keep code comments short. Rationale goes in VERSION.md and DECISIONS.md.
10. Curious, data-driven discovery. Check mechanisms in actual replays, with board pictures.

## Method lessons to cover
Each one needs the principle, why it exists, a concrete example from our history, and a source path.
- **Pre-registration before games:** where the change plugs in, the expected board, and the criteria.
- **Mechanism criteria:** it fires in the intended situations; the intended state change is visible on boards; nothing breaks (identity with the switch off, CPU, errors). No win-count gates.
- **Switch discipline:** every change sits behind a `constexpr` switch that defaults to off, with `if constexpr` so the off build is byte-identical. Identity keys check this.
- **Partial-application rule:** if the purpose moved and nothing broke, the switch goes on and is refined. Otherwise it goes off.
- **Divergence:** on/off games diverge after the first changed decision, so raw counts after it are noise (about 50% per key).
  - Measure harm at the first divergence, which is a natural fork (`tools/firstdiv.js`).
  - Never gate on a measure that only one arm produces.
  - Cases: FREECOST was rejected on raw counts but was favourable causally. BODYX was confirmed. BODYMEM's ally part was caught and attributed by ablation.
- **Noise and power:** what local win counts cannot detect. See the g5 lessons in DECISIONS/NOTES if present; otherwise state it generally.
- **Timing:** the same change acts differently depending on when it first acts. Prefer state triggers to clock triggers.
- **Read boards before believing a count:** the W15 "58% dead-end deaths" was actually a designed vault.
- **Verify assumptions on flipped maps:** the queen id does not depend on the side.
- **A death census finds correctness bugs:** our 10/10 queen self-deaths came from the old-rule body model.
- **Only first-step terms change rankings** (`docs/arch/terms.md`, if present).
- **Division of labour:** Codex builds and analyses, the coordinator runs games and decides, the human sets direction.

## Deliverables
- `docs/PHILOSOPHY.md`: Korean, the master.
  - Order: purpose; the user's principles; the cycle (observe → hypothesis → pre-register → build behind a switch → mechanism check → causal harm check → decide → record); the method lessons; anti-patterns; a short glossary.
  - About 200–300 lines. Plain sentences. Give source paths in brackets.
- `docs/PHILOSOPHY.en.md`: a faithful English translation of the master, with the same structure and terms.
  - Glossary terms: mechanism check, pre-registration, partial-application rule, first-divergence causal check, switch discipline, census not samples.

## Rules
- Write scope: those two files only. No commit, no network, no games.
- Make it shareable:
  - no secrets, key paths or account details;
  - no team-internal operational details beyond method;
  - no claims about reading opponent sources (we never do).
- Do not invent numbers. Every number must come from a source file, cited.
- Target: about 40 minutes.
