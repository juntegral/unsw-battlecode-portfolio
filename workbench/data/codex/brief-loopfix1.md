# Brief: first-morning fixes for the card loop (battlecode, branch juntegral)

The runner is LIVE from this checkout (work/loop/runner.py, pid in ~/.meow-card-loop-locks/). Edit the files only; do not start, stop or signal any process. The team lead restarts the runner after review.
Read work/loop/runner.py, work/loop/prompts/*.md and the live cards #15, #17 and #18 (examples are pasted below).

Fix:
1. **AI card titles get a doubled prefix:** "[Idea] [Idea] Once our queen is dead…". Strip any existing [Idea]/[Task] prefix from the AI-written title before adding ours.
2. **AI card "Who decides now" text is wrong.**
   - It says "Any teammate. One OK lets the loop build it". By the spec (docs/LOOP.md), by:ai cards go straight into the loop. The one human OK happens at approval (candidate), not before building.
   - Make the ladder prompt / template say: "The loop builds and tests it now; one teammate's OK is needed only before it ships."
3. **Routine progress comments are noise.** Every step posts "What we tried: Move this card's next step forward. Did it work: Started mechanism…".
   - Stop posting comments for routine progress (job started, waiting, step done). Put that in status.json and the Loop status heartbeat only.
   - Keep comments for things people read: questions, the look request, results/verdicts, task checks, failures that need a human, and candidate PR links.
4. Add unit tests for 1–3. `python3 -m unittest discover -s work/loop/tests` must pass.

Do not commit or push. Write a ≤6-line note to ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/report-loopfix1.md.
