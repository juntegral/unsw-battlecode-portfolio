Continuation of your study session. What has changed:
- The user now allows the sub-sessions. A driver script (run_study_cont.sh, outside your session) starts them for you, one at a time, with the exact command from the "How to call a sub-session" section of your prompt. Do not try to start any process yourself.
- Your earlier single-session results (REPORT.md, SUMMARY-ko.md, card-draft.md, hypotheses.md, redteam.md, deep-read.md, DONE, study.jsonl) are saved in run1/. They count as your own first notes, not as sub-session output. The same files are still in this directory (DONE was removed); each sub-session's output file replaces the one of the same name, and the driver checks that it was written during that sub-session.
- The metrics were just refreshed (python3 ../../../tools/top_metrics.py): ../../online/top1/ holds 263 battle folders (175 when you started).
- The protagonist stays the rank-1 team of the snapshot, as your prompt defines it.
- It is 04:05 KST. Deadline unchanged: before 08:30 KST on 2026-10-05.

Your step now: update subA.md if the refreshed data changes which games to read (keep it self-contained; output file deep-read.md). Then stop. The driver starts sub-session A next and resumes you when it has finished.
