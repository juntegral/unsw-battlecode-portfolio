# Brief: add "task cards" to the loop (changes that must NOT change play)

Repo: battlecode, branch juntegral. Read docs/LOOP.md, docs/LOOP.zh.md, work/loop/runner.py, work/loop/prompts/*.md, work/board.py and .github/ISSUE_TEMPLATE/idea.yml.

The team decided on a second card type.
- An **idea card** is a hypothesis that changes play. It is the current path.
- A **task card** (`[Task]` title, label `type:task`, label already exists) is a change that must NOT change play: security (e.g. sonar message encryption), refactors, CPU savings, tooling.
- Rule: if play changes at all, it is an idea card. Behaviour-changing bug fixes are idea cards.

Do:
1. `.github/ISSUE_TEMPLATE/task.yml`: a short form with these fields:
   - what to change;
   - why;
   - how we check it is done (task-specific check, e.g. "fake messages are rejected", "decode(encode(m)) == m");
   - proposed by.
   It adds the labels type:task and status:untested.
2. Runner route for type:task:
   - ready → building (no clarify unless unclear; no needs-look; no A/B testing).
   - building: the AI implements it (prompts/task.md, new). It must keep play replay-identical vs the current base on the old 10 maps × 2 seeds, which is the same identity check as now, and the task-specific check from the card must pass (unit test, script or assertion run).
   - Then it posts a [check] comment (3-line plain summary first) and sets status:tested; the author decides as usual → candidate → approvals.
   - If the identity check fails, go back to ready with the note "this changes play; make it an idea card or fix it".
3. board.py `next`: task cards are picked in the same priority order (by:zhe > others > by:ai).
4. docs/LOOP.md and docs/LOOP.zh.md: add a short "Task cards" section (≤12 lines each) and mention them in the top summary.
5. Tests: extend work/loop/tests for the task route. `python3 -m unittest discover -s work/loop/tests` must pass.

Do not commit, push or call GitHub. Write a ≤8-line note to ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/report-taskcards.md.

## CORRECTIONS (team lead, override anything above)
- Task cards are part of the SAME loop and the same single branch flow (card/N → candidate → main), not a side path. Only the steps differ.
- "Plays the same" always means the same as the current base, i.e. the latest main release (the previous version), never a fixed "v61". Use that wording in docs and comments.
- Priority: task cards (type:task) come FIRST, above by:zhe. Order: type:task > by:zhe > other humans > by:ai, oldest first within each group.
