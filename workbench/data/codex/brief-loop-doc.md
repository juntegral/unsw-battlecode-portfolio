# Brief: write docs/LOOP.md, the team's loop spec (team meow, battlecode repo, branch juntegral)

Repo: ~/01. Project/개인 프로젝트/battlecode (branch juntegral).
Read first: docs/WORKFLOW.md, work/board.py, .github/ISSUE_TEMPLATE/idea.yml, README.md.
Also read ~/01. Project/개인 프로젝트/unsw-swarm/tools/meowbot.py docstring and tools/smoke.py usage, for the approve/smoke parts.

Write docs/LOOP.md in English for three teammates (one focuses on strategy rather than code).
Format rules:
- open with a plain-words summary of at most 6 lines;
- then sections with short paragraphs and tables;
- casual and clear, no lab jargon; explain any term the first time it appears;
- under about 180 lines.
Update docs/WORKFLOW.md only where it contradicts LOOP.md, and link to LOOP.md from it.

## Decisions to write down (all agreed by the team lead on 10-04)

1. **No timed waves.** A runner script polls GitHub every few minutes and costs no AI tokens. It calls the AI only when a card's state needs AI work.
   The AI tiers:
   - Opus 5.5 high: thinking steps, i.e. clarify questions, implementation plan and code, verdict draft, ladder hypotheses.
   - Light model: plain steps such as formatting, wiring and summaries.
   There is no call cap.
2. **Card state = one GitHub label**, the single source of truth, so the loop can crash and resume from labels alone.
   States, who acts, and the exit condition:
   - status:ready (loop picks by priority);
   - status:needs-info: the AI posts "what if…" edge-case questions on the card and @mentions the author via meowbot. It waits with no timeout and works on other cards meanwhile. The author answers on the card or in Discord;
   - status:building: implement as a toggle, default off. The build must pass, and with the toggle off play must be replay-identical to the current base on the old 10 maps. If not, the card goes back with a note;
   - status:needs-look: a small mechanism run keeps a few replays, picked by tools/smoke_pick.py. The author watches 2–3 and says "that's what I meant". This is required for Zhe's cards and auto-passes for the others;
   - status:testing: outcome A/B (paired games vs the current base on held-out maps, transposed copies and the old 10 maps), one batch at a time;
   - status:tested: results are posted; the author decides;
   - status:candidate: a candidate PR opens, and meowbot posts approve buttons;
   - status:smoke: optional online check;
   - final states: kept / rejected / inconclusive.
   Map these onto the existing labels where possible, and list the new labels needed.
3. **Priority:**
   1. Zhe's cards (by:zhe, ideas Zhe is confident are real improvements); these also get the extra clarify + look steps;
   2. other board cards;
   3. AI hypotheses from our latest ladder games (by:ai). The loop writes these itself after each new batch of ladder games.
4. **Every result comment** starts with a 3-line plain summary: what we tried, did it work, who decides now. It always includes a "why" table, not just wins:
   - our longest vs their longest at the end;
   - total length;
   - results by map family.
   (Context: games are decided by the longest dragon; on 10-03 a change made our longest longer but the opponent's longer still.)
5. **Approval:**
   - human idea: the author + one other member press OK on the meowbot card;
   - AI idea: one OK from anyone. Promotion by the AI counts as the author's OK.
   - Approval merges the candidate PR to main and submits that exact merge commit.
6. **Coin-flip results:** when local A/B is inside noise, the author can ask for a smoke test:
   - upload;
   - about 60 unranked games vs the DEV team dev_test_1 (id 545, its own 60 games/hour allowance);
   - compare with a v61 baseline recorded once;
   - judge by behaviour in the replays, not the win count;
   - keep or roll back: the area owner decides plus one OK; rollback is one command.
7. **Base version rule:** tests always compare against the current main release. When something new ships, results still running are marked "old base", and queued tests switch to the new base.
8. **Toggle combos:** before a candidate with two or more new toggles ships, run one short combined check (identity on old maps plus a short A/B).
9. **Freeze:** qualifier submissions close 2026-10-09 15:00 KST. After 2026-10-08 20:00 KST there are no new submissions, only rollback.
10. **Hard rules:**
    - no per-map hardcoding or fixed-map tuning; the qualifier is on unseen maps;
    - refactors keep the old 10 maps replay-identical, and real fixes may change them but must not lose much there;
    - no orientation dependence;
    - the loop never requests ranked battles and never uploads on its own; only the approve button or a human does.
11. **Discord pings** only when a human must act (questions, look, approve, results).
    The /loop and /board commands in meowbot show card states.

Do not commit or push. Do not post anything.
Write a short note of what you changed to ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/report-loop-doc.md (under 10 lines).
