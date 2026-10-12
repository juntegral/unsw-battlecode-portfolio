# Early growth when our dragons start short: find the mechanism, then one switchable change or none

You are the analyst (team 1119 "meow"). Submissions close 2026-10-09 15:00 KST; the qualifier maps are unseen.

## What is already counted (read these first, do not recount them)
- `data/analysis/ladder/losses/counts/summary.md` (second table) and `data/analysis/ladder/losses/split/summary.md`,
  with `split/per-game.json` and `counts/growth.json`.
- In short: on layouts where each side starts with 2 dragons, 66 main games "never grew" (6 or fewer dragons at round
  100) and 52 grew. 43 of the 66 are on the two layouts whose starting dragons are 2 long (27 of 27 games on one,
  16 of 18 on the other); a split needs length 4, so a dragon of 2 must eat twice first. Where dragons start 3 or 4
  long we mostly grow. In the never-grew games our first meal comes as early as in the others (median round 19) but
  by round 50 we have eaten 4.1 pearls a game against the opponents' 13.7 in the same games.
- The ledger `data/analysis/ladder/findings.md` already holds F7, F10, F18, F23, F41, F4, F16, F20 on this; read
  those blocks, including what was refuted.

## Your job
1. Find what the opponents do in rounds 0 to 60 of those games that we do not. Use the replays of the never-grew
   games on starts of length 2 (ids in `split/per-game.json`; replays under `data/online/`; parsers in
   `data/analysis/ladder/losses/counts/` and `split/`). Look at both sides in the same game: where each dragon goes,
   which pearls it reaches and when, what stops ours (walls, portals, an enemy head, a pearl that is seen and not
   taken, moving toward the centre, standing still). Count it over all those games, not a sample.
2. Read the early-game code in `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (pearl pull and
   its range, CENTER_PULL, EXPLORE_GAIN, IDLE_ESCAPE, FAR_GAIN, PEARL_FAR_DECAY, portal handling, the threat rule
   that makes a dragon leave a pearl) and tie each counted behaviour to a line.
3. Decide: is there ONE change that is general (it may depend on things the bot can measure in a game such as its
   own length, the number of dragons it has, the round, open sides of a tile, portals; never on a map name), sits
   behind a default-off switch, fits one build round, and has a mechanism check? If yes, write it as a card. If no,
   say so and why. Do not force one.

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/losses/early-growth.md` (120 lines or fewer) and scratch scripts under
`data/analysis/ladder/losses/work/`. Label every statement: measured (with the file or script), read from the code
(file and line), or your estimate.

## Output: `early-growth.md`
1. Three lines: what the opponents do that we do not, the change in one sentence (or "no change survives"), who decides.
2. "What happens in rounds 0 to 60": one table, ours against theirs, all games.
3. "Why, in the code": the lines.
4. Either "The card", written in exactly these sections so it can be filed as is:
   `title:` (one line), `slug:` (1 or 2 lowercase words, at most 16 characters),
   `What we tried:` / `Did it work:` (one line each), `### Area`, `### Claim` (with the proposal and the switch name),
   `### Evidence`, `### Expected signal`, `### What would show it's wrong`;
   or "No card", with the two most promising things to count next.
5. "Against it": the strongest counter-evidence, fairly.
