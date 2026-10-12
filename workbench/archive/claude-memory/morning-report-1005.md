---
name: morning-report-1005
description: trigger "아침 보고 진행해줘": give the morning report on everything that ran overnight from 2026-10-05 ~04:25 KST
metadata:
  type: project
---

The user signed off on 2026-10-05 ~04:25 KST and said: tomorrow morning, when I say "아침 보고 진행해줘", give the report. Work proactively overnight within [[proactive-handling-ok]] and [[ai-cards-delegated]]; keep hands-on work with delegates ([[main-session-master-workbench]]).

What was running at that moment (verify each, these are 04:25 facts):
- Card loop: #23 queen-no-trap build finishing; #30 big-map-trades at look; #29 safer-stride and #31 queen-hunt waiting for their local outcome runs (about 2 h each); #27 passage answered "inconclusive" by 준싱, loop closing it.
- Online tests: #23 launcher `unsw-swarm/data/online/smoke/at-qn23.sh` (new bot vs test4, WeHaveQuizzes, dev1). #30 done (6/30 vs live 9.2/30; dev1 3/15 vs 2/15). #31 done (10/30 vs 9.2/30).
- Codex: behaviour count for #30 → `unsw-swarm/data/online/smoke/tc30-analysis/summary.md`.
- Top-team study, continued properly with Opus max sub-sessions (A close read started 04:18, then B hypotheses, C red team, lead decides): `unsw-swarm/data/analysis/top1/` (`study.log`, final `SUMMARY-ko.md`, `REPORT.md`, `card-draft.md`, `DONE`; first shallow run kept in `run1/`). Deadline 08:30 KST.
- Open with people: Zhe's answer on the portal pathing question for #31; QWQ's answer on what killed the queen locally; card #34 keep-guards parked.

The report follows [[loop-status-first]] and [[report-in-korean]]: loop first, then what was decided on AI cards and why, online results, the study's outcome compared with `run1/`, anything that broke, and what waits for the user.

Updates after 04:25:
- Study: the 08:30 deadline and time budgets were lifted on the user's word (04:27); new driver `run_study_free.sh` lets the lead request any sub-sessions (runaway stop at 12). It may still be running in the morning.
- #31: Zhe agreed to the portal rule (hunters take a portal only when her last seen spot is clearly closer to the far tile) and said "just go with the original order" (04:33). Plan: after the current #31 local test posts its result, put the saved text `unsw-swarm/data/guide/drafts-1005/a31-zhe-portal.md` on the card as Zhe's revision (remove its last sentence about going back to building now). I once applied it too early at 04:29 and undid it at 04:30; do not relabel the card before the result is in.
- #30 behaviour count is in `unsw-swarm/data/online/smoke/tc30-analysis/summary.md`: big-map ram rate 7.6% -> 29.2% vs normal teams, units at r200 37 -> 47, enemy heads near our queen 1.33 -> 1.60, wins unchanged. Decide only after its local test, by reasoning, not thresholds.
