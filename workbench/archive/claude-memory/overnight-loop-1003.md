---
name: overnight-loop-1003
description: overnight local improvement loop started 10-03 03:42 KST in ~/meow-loop (branch loop/overnight-1003); report results when the user says "일어났어"
metadata:
  type: project
---

On 10-03 ~03:40 KST the user asked for an overnight loop in QWQ's environment, Opus 5.5 effort high, local only, no uploads, and a Korean dashboard. **Trigger:** when the user says "일어났어", read the loop state and give a Korean results report.

- Worktree `~/meow-loop` (no spaces), branch `loop/overnight-1003` from main d35c1d2; local commits only, never pushed. Hardcoded `/Users/UNSW/battlecode` paths in 79 QWQ scripts were repointed there (local commit ca29e18).
- Data: all 36 meow battles / 228 games, list `work/nr_meow.txt`, replays `work/nr/` (794MB, fetched with ladfetch.py from the public endpoint).
- Runner `loop/runner.py` (detached, caffeinate): each wave = `claude -p` Opus high, bypassPermissions, PreToolUse guard `loop/guard.py` blocks uploads/battle requests/git push/gh/main-repo writes; MIN_GAP 40 min, timeout 75 min, no new waves after 10-03 15:00 KST or if `loop/STOP` exists.
- Wave prompt `loop/PROMPT.md`: Phase A analysis → B baseline B61 + placebo noise → C hypothesis cycle (prereg, held-out sets weighted over official maps, no fixed-map logic, skip queen/feeding areas owned by QWQ/Zhe).
- Files: STATE.md / LEDGER.md / ANALYSIS.md in English; `status.json` local-only with Korean fields; Korean dashboard `loop/dashboard.html` (auto-refresh).
- **How to report:** read status.json (runner.waves, hypotheses, baseline, noise, findings), STATE.md, LEDGER.md tail, `git log` on the loop branch; check whether runs are still going (`pgrep -f "claude -p # meow overnight loop"`). Stop with `touch ~/meow-loop/loop/STOP`.

Related: [[no-fixed-map-optimization]], [[github-english]], [[meow-team-repo]].
