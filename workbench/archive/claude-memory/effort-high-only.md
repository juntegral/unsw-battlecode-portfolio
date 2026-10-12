---
name: effort-high-only
description: user rule 10-08: never use xhigh effort anywhere; loop builds, analysts and subagents run at high at most
metadata:
  type: feedback
---

jun, 2026-10-08 17:44 KST: "앞으로 그냥 xhigh도 사용하지 말고 빌드할때도 high 고정해". No xhigh effort anywhere from now on: the card loop's build step (was xhigh in `battlecode/work/loop/jobs.py`), Opus analysts, subagents. High is the ceiling.

**Why:** token cost; said right after "아낄 수 있는 부분에서는 아껴야" on the same day (my reading: xhigh builds were the largest single spend he could cut without losing work).

**How to apply:** pass `--effort high` (or lower) on every `claude -p` launch; if a script or config still says xhigh, change it. The loop change is PR #56 (branch `loop/build-effort-high`); it only takes effect once merged and the main checkout on the loop machine is updated. Related: [[claude-usage-budget]].
