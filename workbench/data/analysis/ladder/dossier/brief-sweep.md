# Do our dragons waste the opening by not sweeping the board? Decide, and design one switch

You are the analyst (team 1119 "meow"). Submissions close 2026-10-09 15:00 KST; the qualifier maps are unseen.

## The claim to test, strictly
Being behind at round 100 carries more than half of our ladder losses (loss rate 72 percent against 31). In the
43 games where we never grew, a first count showed this when no pearl is in view: our dragons keep their direction
on 34 percent of turns and step back onto one of their own last 12 tiles on 45 percent; the opponents 55 and 12.
Claim: that is general (all layouts, not only those two), it costs pearls, and a rule that keeps a dragon moving
on when it has nothing to go for would close part of the economy gap.

## Already counted (read first, do not recount)
`data/analysis/ladder/dossier/summary.md`: table A (per layout, ours against theirs: dither, keeps-direction, board
seen, hot-tile share, pearls), table B (by opponent rating), table D (inside each layout: dither, board seen and
pearls in won against lost games, and the within-layout correlation of dither with pearls by round 100).
Per-game rows in `dossier/per-game.jsonl`. Also `data/analysis/ladder/losses/early-growth.md` and the ledger
`data/analysis/ladder/findings.md` (F4, F10, F11, F16, F20, F26, F41).

## Your job
1. Verdict on the claim from the dossier: is our dither higher than theirs on most layouts and against every
   rating band? Inside a layout, do our low-dither games eat more? If the numbers say no, say no and stop at a
   "no card".
2. If yes: read the code that moves a dragon with nothing in range
   (`~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`: FAR_GAIN, EXPLORE_GAIN, the unseen
   bonus, CENTER_PULL, PENALTY_NO_TAIL, the survey that picks a step, anything that remembers recent tiles) and say
   which lines produce the back-and-forth. Open 5 replays from different layouts to see it.
3. Also weigh the second candidate the dossier can support or kill: standing on or next to tiles that keep spawning
   pearls ("hot tiles"). Is their hot-tile share higher than ours, and does it track pearls inside a layout?
4. Pick ONE of the two (or neither) and design it as a default-off switch that fits a single build round, with a
   mechanism check a replay can show. Be decisive: the one you would build first.

## Hard limits
Read-only on everything existing. No server calls, no posts, no edits to bot or loop code. Write only
`data/analysis/ladder/dossier/sweep.md` (110 lines or fewer) and scratch scripts under
`data/analysis/ladder/dossier/work/`. Label every statement measured, read from code (file:line) or estimate.
No map names in any rule.

## Output: `sweep.md`
Three lines on top (verdict on the claim, the change in one sentence or "no card", how sure and why), then the
evidence table, the code lines, "The card" in the sections `title:`, `slug:` (1 or 2 lowercase words, at most 16
characters), `What we tried:`, `Did it work:`, `### Area`, `### Claim`, `### Evidence`, `### Expected signal`,
`### What would show it's wrong`, and "Against it".
