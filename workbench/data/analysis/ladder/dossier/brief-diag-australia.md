# Why we never win on the layout "Australia": find the mechanism, then one general switch or none

You are the analyst (team 1119 "meow"). Submissions close 2026-10-09 15:00 KST. The qualifier is best of 7 on maps
nobody has seen, so a layout we always lose on is a class of maps we will lose on. The name "Australia" is only a handle
for the data: the answer must be a property a bot can measure during a game (sizes, open sides, portals, counts,
rounds, what it sees), never the name.

## Already counted (read first, do not recount)
- `data/analysis/ladder/dossier/summary.md` table C for this layout (every measure, ours against theirs, rounds
  0-100 and 101-300, sorted by gap, with the 15 normal layouts next to it), table A (all layouts) and table D.
  Per-game rows: `dossier/per-game.jsonl`.
- `data/analysis/ladder/findings.md` (the ledger; search it for this layout and for large layouts: F31, F11, F25,
  F26, F29, F30, F34, F40) and `data/analysis/ladder/losses/plan.md`, `early-growth.md`.

## Your job
1. From the dossier pick the three largest gaps on this layout that are NOT gaps on the normal layouts. For each,
   open 4 to 6 replays of this layout (ids in per-game.jsonl; replays under `data/online/`; parsers in
   `data/analysis/ladder/losses/work/` and `dossier/`) and find what our dragons do at the moment the gap opens and
   what theirs do in the same game. Then count that exact behaviour over every game on the layout.
2. Tie it to the bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`, file and line of the
   rule or constant that makes our dragons do it.
3. State the general property of the layout that triggers it, and check on which of the other 18 layouts the same
   property holds and what our record is there (it must explain wins as well as losses).
4. Decide with confidence: ONE default-off switch that fits a single build round and removes the behaviour, with a
   mechanism check a replay can show. If no general change survives, say "no card" and why. Do not hedge between
   several: pick the one you would build.

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/dossier/diag-australia.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/`. Label every statement measured (file or script), read from code (file:line)
or estimate.

## Output: `diag-australia.md`
1. Three lines: what loses the games here, the change in one sentence (or "no card"), how sure you are and why.
2. "What happens": one table, ours against theirs, every game on the layout.
3. "Why, in the code". 4. "Which other layouts share the property" (with our record on them).
5. "The card", in exactly these sections: `title:`, `slug:` (1 or 2 lowercase words, at most 16 characters),
   `What we tried:`, `Did it work:`, `### Area`, `### Claim` (with the proposal and the switch name),
   `### Evidence`, `### Expected signal`, `### What would show it's wrong`. Or "No card".
6. "Against it": the strongest counter-evidence, fairly.
