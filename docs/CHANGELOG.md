# Changelog of corrections

Changes made after publication that alter a stated fact. One line each: date / file / before → after / evidence.
Additions that do not change a stated fact (new pages, links, the start-here block) are not listed.

| Date | File | Before → after | Evidence |
|---|---|---|---|
| 2026-11-09 | `README.md`, `README.ko.md` | "84 uploads" → "84 uploads (including test copies)" | `writeup/06-timeline.md` section 1, uploads line |
| 2026-11-09 | `README.md`, `README.ko.md` | "21 live versions in the last 16 hours" stated as a plain benefit → same number with a link to its cost | `writeup/05-ai-workforce.md` section 8.3; `writeup/01-playbook.md`, "What cost us most" |
| 2026-11-09 | `README.md`, `README.ko.md` | Heading "proven by hash" → "identity proven by hash", with a sentence that the hash proves identity, not improvement | `docs/case-studies/03-switches-proven-by-hash.md` ("What it did not buy"); `writeup/05-ai-workforce.md` section 3, cases 1 to 3 |
| 2026-11-09 | `README.md`, `README.ko.md` | "People approve; the loop never uploads." → the loop's AI cannot upload, and that limit covers the loop only; the lead Claude session uploaded the 21 versions by delegation | `card-loop/work/loop/guard.py`; `workbench/docs/HANDOVER-2026-10-08.md` line 28; `workbench/docs/HANDOVER-2026-10-09.md` section 7.2 |
| 2026-11-09 | `README.md`, `README.ko.md` | Authorship: "every commit is mine" → every commit is under my account, and 61 of the 67 commits touching these files carry a `Co-Authored-By: Claude` trailer; the other 6 are "Prepare candidate" commits made by the runner | Team repository history (public); `card-loop/work/loop/runner.py` lines 85 and 843 |
| 2026-11-09 | `README.md`, `README.ko.md` | Authorship: "checked by me or by a second agent" → the checks recorded in the write-up (scripts, lead recount, second-AI adversarial review, teammates' notes) | `writeup/05-ai-workforce.md` section 3 |
| 2026-11-09 | `README.md`, `README.ko.md` | First role sentence and "My part" row: "the engineering around the bot more than the bot itself" → "took part in the mid-game exploration and split logic" plus the engineering around it. "In charge of" was lowered to "took part in" because the public team README states that the base bot, including its splits and exploration scoring, is QWQ's | Team repository `README.md`, 2026-10-15 (public); `final-bot/README.md` |
| 2026-11-09 | `README.md`, `README.ko.md` | "What went wrong" had 5 items → 6, the sixth on the last two days | `writeup/05-ai-workforce.md` sections 3 and 4; `docs/LAST-TWO-DAYS.md` |
| 2026-11-09 | `README.md`, `README.ko.md` | Ladder row "seeded 39th" → final rank 38 and seed 36; Result row "eliminated there on 10-10" → lost in the round of 64 on 10-10 | Team repository `README.md`, 2026-10-15 (public). The earlier seed 39 is jun's own message of 10-09 19:19 (channel mirror, not published) |
| 2026-11-09 | `writeup/00-README.md`, `writeup/01-playbook.md`, `writeup/03-bot-design.md`, `writeup/06-timeline.md` | "jun reports a quarterfinal exit", "seed 39", "the round is not recorded" → each left in place with a bracketed correction: round of 64, seed 36, final rank 38 | Same record |
| 2026-11-09 | `README.md`, `README.ko.md`, `writeup/00-README.md`, `card-loop/README.md` | The team repository described as private → public | `https://github.com/forrest-gan2005/battlecode` opens without login (checked 2026-11-09) |
| 2026-11-09 | `writeup/05-ai-workforce.md` section 4 | "who applied the change at 22:13 is not recorded" → jun confirmed with "ㄱㄱ" at 22:13 and the lead session edited `tools/smoke.py` | `workbench/docs/SESSION-STATE.md` line 431 |
