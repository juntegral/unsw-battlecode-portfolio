# Codex brief: what makes Cutlery strong on any map (W16), with our intake gap as a core part (W11)

You work in `~/01. Project/개인 프로젝트/unsw-swarm`. Read first:
- `AGENTS.md`, especially §4 step 7: local games are mechanism checks only, and feedback comes from online behaviour.
- `docs/WORKQUEUE.md`, tasks W16, W11, W10, W7.
- `docs/arch/terms.md`.
- `research/briefs/codex-brief-intake.md`. Its questions are part of this study (§B below).
- The rules in `rules/ALL.md`.

Reuse:
- `exp/w7/` (`reach.js`, `pearlmiss.js` corrected to turnStart adjacency, `ramprop.js`, `boxing.js`, `forced.js`, `drift.js`);
- `exp/small/`, `exp/spatial/`, `exp/general/`, `exp/duel/` if it already exists;
- `tools/top_features.js`, `tools/mass_ledger.js`.

## Why
The user, watching the sprint bracket on custom unseen maps, concluded: "now we must build not a map-optimised bot but simply a very strong one, and Cutlery is the GOAT at that." Teams with per-map logic dropped out early. Cutlery is ladder rank 1 (team 306).

We want Cutlery's map-independent principles, and the biggest behavioural gaps between Cutlery and us, ranked. They must come from online behaviour.

## Data (the whole population, no sampling)
- **Cutlery:** 2,054 games in `data/top/index.jsonl` (all 10 maps, about 200 each, 1,127 wins) and 40 in `data/elite/`.
- **Comparison cohorts:**
  - the other top-10 teams' winners and losers (`data/top`, `data/elite`);
  - ours online: W0–W12 and `data/online/v1-w1..3`;
  - UnderTheC (`data/online/undertheC/`, `data/elite/`) as a side cohort.
- **Sprint bracket games:** if any appear in `data/elite/` or `data/online/`, analyse them as a separate cohort. They are on unseen custom maps.

## A. Cutlery's profile, per map and pooled
Measure:
- head-count curve (r25/50/100/250/500);
- split schedule;
- piece-length distribution;
- intake per dragon-turn and per move;
- cohesion: nearest ally head;
- ram propensity by length difference × local balance;
- avoidable and forced exposures;
- sealing allies;
- deaths by cause;
- conversion: the share of team mass in the longest dragon over time, when the concentration starts and what triggers it;
- king safety: the enemy heads within 3/5/8 of the king;
- pocket and fountain use;
- scouting: where its L2–3 pieces sit relative to its king, the enemy and fountains.

## B. Intake (W11), with Cutlery as the main reference
Answer the questions in `codex-brief-intake.md` (§Questions 1–6) with Cutlery as an extra cohort next to elite winners, elite losers and ours. The core fact: elite winners skip 19.8% of adjacent pearls that only an enemy could also reach, and we skip 73.6%.

## C. What is map-independent
- For each metric in A, compare its spread across the 10 maps for Cutlery with the same spread for the other elite teams.
- Metrics that stay steady across maps are candidate general principles.
- For metrics that vary, test whether the variation is predicted by geometry a bot can observe at runtime: area, pocket share, fountain share, corridor widths, start distance. If it is, the result is a runtime rule. If it isn't, Cutlery probably uses per-map knowledge and we should not copy it.

## D. Cutlery against others
- Which behaviours separate Cutlery from the other top-10 winners?
- How does Cutlery lose: against which opponents, on which maps, and what went wrong? Give game ids, rounds and boards.

## E. Ours against Cutlery
Rank the behavioural gaps by size. For the top 5 gaps, give:
- board pictures (`node eval/board.js`, or `exp/v16/board.js` for any map);
- the planner terms (`docs/arch/terms.md`) that a fix would touch, and roughly by how much.

## Deliverables
- `exp/cutlery/tables.json`, written first.
- `research/observations/cutlery.md`, in Korean:
  - keep [사실] and [해석] apart;
  - give N everywhere;
  - use the three-stage method;
  - end with a rule table: principle → evidence → map-independent or geometry-conditioned → planner term → expected mechanism effect, labelled as hypotheses.
- `exp/cutlery/SUMMARY.txt`, written last (12 lines).

## Rules
- **Write scope:** `exp/cutlery/**` and `research/observations/cutlery.md` only. Do not commit.
- No network, no uploads, no games.
- At most 3 worker processes, with `nice -n 10`.
- Pause if free memory drops below 10% or free disk below 21 GB.
- Keep caches compressed.
- Recount the key numbers independently.
- **Target:** tables for A and B about 3 hours after start; everything about 7 hours after start.
