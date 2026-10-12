---
name: top-team-study-1004
description: overnight background study (10-04 → 10-05 09:00) of how the rank-1 team wins vs 2000+ teams; one hypothesis + card draft by morning
metadata:
  type: project
---
Started 2026-10-04 22:25 KST, user-approved. Separate from the card loop.
- Collector: unsw-swarm/tools/top_collect.py (top-3 teams' battles vs 2000+ opponents, every 3 min, 6 GB cap, stops 10-05 09:00). Replays in unsw-swarm/data/online/top1/, index data/top1/index.jsonl, log data/top1/collect.log.
- Driver: data/analysis/top1/run_study.sh: (1) Codex astra writes tools/top_metrics.py; (2) waits for replays until 01:30 or the cap; (3) one headless Claude session (Opus, effort high) follows STUDY-PROMPT.md, with at most 3 sequential sub-sessions at max effort (deep read, hypotheses, red team). Log: data/analysis/top1/study.log, study.jsonl.
- Deliverables in data/analysis/top1/: REPORT.md, card-draft.md, SUMMARY-ko.md, DONE. Protagonist = rank-1 team (SSS id 91 at start; Vibing++ 306 and forgot to mention 264 as cross-checks).
- Budget: about 20% of weekly Max-20 usage; no subagent swarms.
- In the morning: read SUMMARY-ko.md + REPORT.md, show the user, and only then (if they like it) put the card on the board.

Related: [[claude-usage-budget]], [[loop-spec-1004]], [[zhe-intuition]].
