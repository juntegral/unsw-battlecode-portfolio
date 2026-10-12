# Design study: a queen that cannot be killed ("sealed queen") for our bot

You are the analyst (team 1119 "meow"). Submissions close 2026-10-09 15:00 KST; the qualifier maps are unseen.
A black-box experiment found a formation our live bot cannot break. Decide how OUR bot could use it, and whether it
fits one or two build rounds. Design only: do not edit bot or loop code.

## Read
- `~/meow-redteam/report.md` (weakness W1) and `~/meow-redteam/verify/check.md` (an independent replay check).
- The red-team bot that does it: `~/meow-redteam/bot/main.cpp` (find the ring code: how it picks the block, how the
  queen grows to the length, how she enters the cycle, what she does while not yet sealed).
- The two replays named in the report, with `~/meow-redteam/tools/show.py` if you need to see the geometry.
- Our bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`: the queen rules (is_queen(),
  QUEEN_* switches, QUEEN_LOOP from card 38 if present on main, the split guard), the feeding phase and the leader,
  and how many free steps a dragon has (ceil(length / 4)).
- Ladder facts: `data/analysis/ladder/losses/summary.md` and `plan.md` (how our queen dies; 148 of 277 full games
  end with both queens dead; our queen is 2 or 3 long in most losses).

## Answer these, with reasons
1. Geometry: why is the 6 by 4 block with length 23 and 6 steps a turn sealed at every turn end? Which other
   (block, length) pairs are sealed in the same way? Give the general condition, and the smallest one. Check each
   claimed pair by simulating the cycle in a small script (head and free cell both enclosed at every stop).
2. Getting there in OUR bot: how can our queen reach the needed length early and safely? Compare (a) she simply
   stops splitting and eats, (b) our feeders feed her instead of, or before, the leader, (c) something else you
   find in the code. Use the ladder numbers on how fast she eats and when she dies.
3. Where: how does she find a block (open tiles, no walls or portals inside, no pearl-spawning tile inside if the
   bot knows them, away from the fighting)? What does the bot already know that helps (its map memory, home area)?
4. Entering and holding: the exact path to close the cycle from an arbitrary approach, what she does if a tile of
   the block is taken, if an enemy is in view while she is closing, if a pearl appears on her path (growing breaks
   the count), and how she re-forms if she had to break out.
5. Costs: what does the team lose (her early splits are how we grow on short starts: see `early-growth.md`)? What
   happens to the queen rule if their queen is alive and longer? Does the feeding phase conflict?
6. Smallest useful first build: one default-off switch, the fewest moving parts, with a mechanism check that a
   replay can show (sealed at turn end in N of M games by round R; alive at round 500; no enemy head ever adjacent).

## Output: `data/analysis/ladder/losses/queen-ring.md`, 110 lines or fewer
- Three lines on top: is it worth building now (yes / only the small version / no), the one-sentence design, the
  biggest risk.
- The answers to 1 to 6, each statement labelled measured (file), read from code (file:line), simulated (script) or
  estimate. Scripts under `data/analysis/ladder/losses/work/`.
- "The card", in sections `title:`, `slug:` (1 or 2 lowercase words, at most 16 characters), `What we tried:`,
  `Did it work:`, `### Area`, `### Claim`, `### Evidence`, `### Expected signal`, `### What would show it's wrong`.
- "Against it": the strongest reasons not to build it this week.
No map names in any rule. Write nothing outside `data/analysis/ladder/`.
