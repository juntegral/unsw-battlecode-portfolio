# A modification plan from our lost ladder games (strict analysis, team 1119 "meow")

You are the analyst. jun asked for a rigorous analysis of our LOST ladder games and, from it, an active plan of bot
changes. Submissions close 2026-10-09 15:00 KST; the qualifier is played on maps nobody has seen.

## Read first
- `data/analysis/ladder/losses/summary.md` and `losses.json`: an exclusive breakdown of every lost game (counted
  by a script just now, live code "main" and old bot "v31").
- `data/analysis/ladder/findings.md` (the whole ledger, 42 findings) and `data/analysis/ladder/state.json`.
- `data/analysis/ladder/rows.jsonl` (one row per game) when you need to recount something.
- The bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (switches and constants such as
  LEADER_GROW_ROUND, LEADER_GROW_ROUND_BIG, QUEEN_GIVE_WAY, QH_MAX_LEN, QH_FRESH, QUEEN_NO_FEED, QUEEN_LOOP).
- What teammates are already testing: `~/meow-loop-out/card-38/`, `card-47/`, `card-48/` (verdict.md, look.md),
  `data/local/queen454/sol/summary.md` (the rank-5 team's queen next to ours), and the online result of card 47 in
  `data/online/smoke/um47-bob1-report.log`.

## Hard limits
- Read-only. Do not edit bot code, loop code or existing files. No server calls, no uploads, no Discord or GitHub posts.
  Write only `data/analysis/ladder/losses/plan.md` and scratch scripts under `data/analysis/ladder/losses/work/`.
- General logic only. No per-map tables or map names in a proposed rule (the qualifier maps are unseen). A rule may
  depend on things the bot can measure in a game (size, open sides of a tile, counts, rounds).
- Every new behaviour sits behind a switch that is off by default.
- Local win rates do not decide anything here. For each change say what would be counted in replays to show the
  mechanism fired and did what was meant.
- Keep three kinds of statement apart and label them: measured (with the file it comes from), read from the code
  (file and line), and your estimate.

## What to produce: `plan.md`, 150 lines or fewer, plain English
1. Three lines on top: what the losses are made of, the plan in one sentence, who decides.
2. "Where the losses are": the breakdown in one small table, largest first, with your reading of which buckets are
   one underlying fault seen from different sides.
3. "The plan": 5 to 8 changes, ranked by losses they can reach per hour of build and test. For each:
   - the loss bucket it goes after and how many lost games that bucket holds (measured);
   - the mechanism in the code today (file, line, switch or constant);
   - the exact change, as a default-off switch, small enough for one build round;
   - an upper bound on what it can win back, in games, and why it is an upper bound (your estimate);
   - the strongest evidence against it in the ledger or in the card results, stated fairly;
   - the mechanism check (what to count in replays);
   - size (small, medium, large) and whether it fits an existing card of Zhe or QWQ (38 queen loop, 43 idle exit,
     47 map updates, 48 queen never feeds) or needs a new one.
4. "Order for the hours left": a concrete sequence for a loop that takes about 2.5 hours per build-and-test round
   and runs one card at a time, including what to stop or drop.
5. "What I could not establish": at most 8 lines.
Be active: prefer a change that attacks a large bucket and can be falsified in one round over a safe small one.
Be strict: if a popular idea does not survive the numbers, say so and leave it out.
