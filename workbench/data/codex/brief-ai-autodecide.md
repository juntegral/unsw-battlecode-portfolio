# Brief: the loop decides AI cards by itself (battlecode main)

Repo: ~/01. Project/개인 프로젝트/battlecode, branch main. The runner is LIVE from this checkout: edit the files only, start/stop nothing.
Read work/loop/runner.py, work/loop/prompts/verdict.md and docs/LOOP.md (+ LOOP.zh.md).

New rule, for `by:ai` cards only, applied right after the verdict is posted (state tested). Human cards are unchanged; their author decides.
1. **Barely fired:**
   - ≥95% of A/B pairs identical, OR the verdict says the target behaviour never appeared.
   - On the first attempt: start ONE automatic revision. A new attempt in building, with a note "didn't fire: <reason>; revising once". The build prompt gets the verdict's evidence and must make the behaviour actually trigger.
   - On a second barely-fired result: set status:inconclusive and close the issue with a one-line reason.
2. **Clearly worse:** net ≤ −9 on the held-out set (or the combined unseen sets) → status:rejected, closed, with a one-line reason.
3. **Clearly better:** net ≥ +9 on held-out AND the mechanism shown AND old maps not worse than −9 → status:candidate (the usual candidate PR; one human OK is still needed to merge).
4. **Otherwise** (works but coin-flip): leave it at tested and add a line: "coin flip locally; a 30:30 online pair test would settle it (tools/smoke.py pair)". meowbot pings as usual.

The verdict step must emit machine-readable fields so the runner doesn't parse prose: identical_pairs, total_pairs, net per set, mechanism_shown (bool), and target_seen (bool). Put them in the hidden card-loop JSON marker or in a results JSON in the out dir.
- Each auto-decision posts one short comment: plain words, why, and what happens next.
- Thresholds are constants at the top of runner.py.
- Docs: add a short "AI cards decide themselves" section to LOOP.md and LOOP.zh.md (≤10 lines each).
- Tests: cover each branch, the revise-once limit and human cards untouched. `python3 -m unittest discover -s work/loop/tests` must pass.
- Make it apply to existing tested AI cards on the next poll too. Card #18 has 396/400 identical pairs and "no surviving queen longer than 3", so it should get the one automatic revision.
Do not commit, push or call GitHub. Write a ≤8-line note to ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/report-ai-autodecide.md.
