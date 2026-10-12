# Brief: team guide page + PDFs for the new loop workflow

Work dir: unsw-swarm/data/guide/.
- `old-workflow.html` is our previous team page (3 workflows, Oct 3). It is outdated; reuse its look: the CSS tokens, fonts, light/dark tokens, the language toggle pattern and the diagram style.
- The new content comes from ~/01. Project/개인 프로젝트/battlecode/docs/LOOP.md (authoritative) and docs/LOOP.zh.md.

## Write `guide.html`
One self-contained page. Languages: English + 中文, with a toggle. `?lang=zh` in the URL selects Chinese on load, so we can print each language.
Audience: the two teammates. Zhe focuses on strategy rather than code; QWQ is the bot author and reads Chinese.
Tone: casual, short, like a teammate explaining; no lab jargon; explain any term the first time.

Sections:
1. **Title + 4-line summary.** Drop an idea → the loop asks you questions → you check 2–3 replays → it gets tested → you decide → you + one other OK in Discord ships it.
2. **One diagram** (inline SVG, hand-drawn style like the old page): the card's journey through the states.
   - Show ready → needs-info → building → needs-look → testing → tested → candidate → (smoke) → kept / rejected / inconclusive.
   - Colour the boxes by who acts: you (the idea's author), the loop/AI, or the team (approvals).
   - Label the arrows with what moves the card ("you answer", "build passes, plays the same as v61 when off", "you say 'that's what I meant'", …).
   - Add a side rail showing new ladder games feeding AI ideas (by:ai).
3. **How to take part.** One small card per person.
   - Zhe: ideas + replay checks + ladder/strategy focus, coding optional.
   - QWQ: queen area + review + approvals.
   - 준싱: runs the loop on the Mac, tools.
   Then numbered steps with the exact commands/buttons:
   - `/hypo` in Discord (any language);
   - answer the "Questions before we build" comment on GitHub (or in Discord; it gets copied);
   - watch the attached replays when meowbot pings you and reply "looks right" or what's off;
   - read the result comment: 3-line summary on top, then the "why" table;
   - decide on the card: candidate / drop / inconclusive;
   - press OK on the meowbot candidate card (author + 1 other; AI ideas: 1 OK);
   - optional online check: v61 and the new bot vs the same top teams within about an hour, then swap back.
4. **Rules that keep us safe.** Short bullets:
   - new behaviour starts as a switch that is off;
   - plays exactly the same as v61 when off;
   - no per-map tricks (the qualifier maps are unseen);
   - one test at a time;
   - the loop never uploads or requests ranked games;
   - rollback is one command;
   - freeze after Oct 8 20:00 KST (= Oct 8 22:00 AEDT); qualifier closes Oct 9 15:00 KST (17:00 AEDT).
5. **How we judge a change.** Local tests only catch "is it broken / does it do what we meant". The real test is vs higher-elo teams: a good bot beats most top bots, and there is no single best bot (Zhe's point).
   The "why" table always shows our longest vs their longest at the end, total length, and results by map type.
6. **Glossary** (8–10 terms): card, label/state, toggle, v61/base, replay, A/B, unranked, candidate, rollback, freeze.
7. **Footer:** "Proposed by 준싱, Oct 4. Shout in Discord if anything's off." + a link to docs/LOOP.md in the repo:
   https://github.com/forrest-gan2005/battlecode/blob/juntegral/docs/LOOP.md

## Page contract (must keep)
- A `<title>` of 2–4 words: "meow Loop Guide".
- Colours as tokens on :root, with a dark mode under `@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme="light"])` and again under `:root[data-theme="dark"]`. The body has an explicit background.
- External: only Google Fonts stylesheets. No other external scripts or images.
- Works at phone width (16px side gutter, no horizontal page scroll; the SVG may scroll inside its box).
- Print CSS: A4, light colours forced, no toggle buttons, sections not split awkwardly (`break-inside: avoid` on cards), and the diagram fits the page width.

## PDFs
Render with headless Chrome:
`"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=<out> "file://<path>/guide.html?lang=…"`
Outputs: `meow-loop-guide-en.pdf` and `meow-loop-guide-zh.pdf` in data/guide/. Check the page count (aim for 3–5 pages each).
Render page 1 of each to PNG (sips or Chrome --screenshot) as `preview-en.png` / `preview-zh.png` so the result can be checked visually.
If Chrome fails in the sandbox, say so in the report and leave the HTML ready.

Do not publish anything. Do not commit. Write a ≤10-line note to data/codex/report-guide.md.

## ADDENDUM (team lead feedback): every stage needs real detail
Add a section "What happens at each step, in detail" with one block per state. Each block covers:
- who acts;
- what exactly happens;
- what you see (which GitHub comment / Discord ping, with a short mock example);
- how long it usually takes;
- what moves it on.
Get the facts from battlecode/work/loop/runner.py, work/loop/prompts/*.md, work/board.py and unsw-swarm/tools/smoke.py. Be concrete:
- **needs-info:** example questions; where to answer; that answers in any language work.
- **building:** the switch is added off, and "plays the same as v61 when off" is checked on the old 10 maps × 2 seeds, i.e. the same moves, not just the same winner.
- **needs-look:** a small run of about 16–32 games on maps where the behaviour should show. The 2–3 most telling replays arrive in Discord. How to open a .replay: https://game.battlecode.au/docs/quickstart.
- **testing (local A/B):** the base bot and the new bot each play v61 on the same maps, seeds and sides.
  - Sets: held-out maps (80 unseen generated maps × 2 sides), their transposed copies, and the old 10 maps × 8.
  - About 400 games per bot, a few hours on the Mac.
  - We compare game by game: + means only the new bot won, − means only the base won.
  - About ±8 per 160 games is just luck.
  - Local tests answer "is it broken / does it do what we meant", not "is it better vs top teams".
- **tested:** the result comment layout: the 3-line summary, then the "why" table (our longest vs their longest at the end, total length, results by map type), then the per-set numbers.
- **online comparison (smoke pair):**
  1. pick 2–3 higher-elo teams (or `--top N`, or the DEV team dev_test_1);
  2. v61 (still active) plays about 30 unranked games vs them;
  3. when those are done, the new bot is uploaded and plays the same teams and maps;
  4. then v61 is reactivated.
  It takes about an hour and uses one hour of unranked tickets (60 games). The report shows each opponent side by side, with replay ids for Zhe. It never runs while games are pending, and rollback is one command.
- **candidate / approve:** the meowbot card shows the needs (author + 1 other; AI ideas: 1). OK → confirm → merge → submit that exact commit.
- **kept / rejected / inconclusive.**
Also add a short "A day in the loop" timeline example: one card from idea to decision, with realistic durations.
PDFs can now be longer (5–8 pages).

## ADDENDUM 2 (team lead): task cards, wording, no PDFs
- **Skip the PDFs and PNG previews entirely.** The web page is enough. Keep the print CSS anyway.
- **Add "two card types" near the top**, as a simple comparison table:
  - **Idea card:** changes how we play (examples: feeding, queen zone). It passes when it does what we meant and wins vs top teams. Steps: questions > build > replays > test > decide > approve. Takes a few hours. Queue: after task cards.
  - **Task card:** must NOT change play (examples: sonar message encryption, cleanup, CPU). It passes when it plays exactly like the previous version and passes its own check. Steps: build > check > approve. Takes about 30–60 min. Queue: first.
  - Rule of thumb: if play changes at all, it is an idea card. Both go through the same loop and the same branch flow (card/N → candidate → main).
- **Queue order:** task cards > Zhe's cards > other people's cards > AI ideas from ladder games.
- **Wording:** identity checks are against "the previous version" (the latest main release), never a fixed "v61". The online pair test compares the previous version and the new bot.
- In the state diagram, show the task-card shortcut (building → tested, skipping needs-look/testing) as a dashed path.
- Facts on task cards: battlecode docs/LOOP.md once it has a "Task cards" section (being added now). If it isn't there yet, use this addendum.
