# Early growth when our dragons start short

Scope: the 43 main games that never grew on the two layouts whose dragons start 2 long (Tower Defense 27, Stripes 16; 33 lost), rounds 0 to 60, both sides in the same game. All 174 main games on 2-dragon-start layouts were scanned to round 120 for the comparisons. Scripts and rows: losses/work/eg_*.py, eg_rows-*.jsonl. Bot code: battlecode/mybot2/main.cpp as it is on disk today ("main.cpp:line" below). Every line is marked measured, read from the code, or estimate.

1. What the opponents do that we do not (measured): on Tower Defense they walk out of the 49-tile start room (first head outside at round 15, median) and sweep the board; ours are inside it in every turn of rounds 0 to 59 in 27 of 27 games, pressed against the wall nearest the board centre. On Stripes both sides leave the start alike; they step through portals into the 1-to-4-tile pearl rooms 6.5 times a game and we do 2.3 times.
2. The change: one default-off switch, STALL_RELEASE: a dragon of length 4 or less that has not come nearer the centre for 12 rounds is no longer pulled to the centre and is not charged the no-tail penalty for a step that has room ahead. It answers Tower Defense only; no change survives for Stripes.
3. Who decides: the team at card triage (the bot owner builds). It needs their call, not mine: global forms of both terms were already tried and rejected on the local sets (battlecode/work/plan.md:639-641).

## What happens in rounds 0 to 60

All 43 games unless a layout is named (TD = Tower Defense 27 games, St = Stripes 16). Measured; script in the last column.

| What | Ours | Theirs | Script |
|---|---|---|---|
| Pearls eaten by r60, per game | 3.47 (TD 2.78, St 4.62) | 10.70 (TD 7.04, St 16.88) | eg_agg.py |
| Dragons alive at the end of r60; splits in r0-60 | 2.49; 45 | 4.37; 161 | eg_agg.py |
| Pearls by r60 per game: queen / other starting dragon / children | 2.23 / 0.51 / 0.72 | 2.49 / 2.35 / 5.86 | eg_agg.py |
| Share of the board seen by the side by r60 (7 by 7 view at turn starts) | 0.52 (TD 0.29, St 0.92) | 0.67 (TD 0.54, St 0.89) | eg_agg.py |
| No pearl in view: keeps its direction; steps onto one of its own last 12 tiles | 33.8%; 44.7% | 55.4%; 12.4% | eg_agg.py |
| TD: turns that start inside the 49-tile start room, r0-59 | 100% (3,408 of 3,408) | 60.9% (2,476 of 4,068) | eg_home.py, eg_recount.py |
| TD: games with no head outside the room by r60; by r120; first exit round | 27 of 27; 18 of 27; the other 9 at r69 to r120 (median 93) | 2 of 27; 1 of 27; median 15 | eg_home.py, eg_recount.py |
| TD: in-room turns on the 9 room tiles nearest the board centre, r0-59 (18.4% if even) | 48.9%; then r60-64 27.5%, r65-69 6.7% | 13.8% | eg_home.py, eg_fine.py |
| TD: in-room turns at the 2 by 2 exit corner, r30-59 and r75-89 (8.2% if even) | 0.9% and 23.2% (260 of 263 with no known pearl within 7 steps) | 11.8% and 12.1% | eg_exit.py |
| TD: pearls born r0-60 that are 16+ path steps from the side's nearest head; eaten by that side | 1,212 of 1,286; 0 | 1,027 of 1,286; 64 | eg_agg.py |
| TD: pearls eaten per turn once outside the room | 0.124 (290 turns, r90-120) | 0.118 (r60-89) | eg_home.py |
| TD: starting dragons dead by r60 | 8 of 54 (own body 5, other body 2, wall 1; four at r10) | 2 of 54 | eg_fine.py |
| St: steps into a pearl room behind a portal; pearls born in such rooms eaten by r60 | 37; 5.8% (37 of 636) | 104; 30.0% (191 of 636) | eg_fine.py |
| St: turns with a pearl one portal step away, not taken | 97.2% (242 of 249) | 49.7% (78 of 157) | eg_agg.py |
| St: deaths inside the rooms, r0-60 | 4 | 43 (wall 33) | eg_fine.py |
| Pearl on an open neighbouring tile, not eaten | 3.4% (5 of 147) | 21.6% (103 of 477) | eg_agg.py |
| Enemy head in view at turn start | 14.4% (TD 0 of 3,472; St 36.6%) | 12.3% (TD 0; St 28.5%) | eg_agg.py |
| Turns with no step; portal steps; turns of 2+ steps | 63; 80; 3 | 214; 168; 18 | eg_agg.py |
| No known pearl within 7 steps: the step lowers the distance to the centre | 54.2% | 48.9% | eg_agg.py |

Read with it (measured): what stops ours is not an enemy head (none in view on Tower Defense), not standing still, and not pearls left on an open neighbour (we take 97%). On Tower Defense it is the room: 94% of pearls are born 16+ steps from our heads and we eat none of them; once outside we eat at their rate. On Stripes it is the portal rooms, where 90.1% of the pearls are born (636 of 706). The last table row shows why the centre did not show up in the earlier pooled count: a dragon held against a wall shuffles to and fro, so half its steps raise the distance.

## Why, in the code

- Read from the code: the pearl pull is 2 x (260 - 40 x steps), zero from 7 steps (main.cpp:346-348, 3260-3266, 5021-5033). PEARL_FAR_DECAY is 0.0 (234) and EXPLORE_GAIN is 0.0 (264, 5034-5036). Past 7 steps the only pull is FAR_GAIN, 2 a step toward the nearest pearl or unseen tile (261, 5037-5047), and at most 8 a step from the unseen bonus (374).
- Read from the code: CENTER_PULL takes 40 per tile of wrap-around straight-line (Manhattan) distance to the tile (width/2, height/2) from a dragon of length 4 or less that has no pearl bonus (358, 360, 5061-5065, 3051-3055, 2198-2200). Walls are ignored (CENTER_PATH false, 169). It lasts 60 rounds on layouts of 1000 cells or fewer with width at least twice height, 30 rounds on other layouts of 700 cells or fewer (359-363, 473-476). 40 a tile against 2 to 8: the centre wins.
- Measured against that rule: on Tower Defense (32 by 16) the room has one exit tile, at the corner farthest from the centre (eg_fine.py: 1 exit tile in 27 of 27). Our dragons leave the centre-side tiles in the very bin where the rule ends: 51.9% in r55-59, 27.5% in r60-64, 6.7% in r65-69. 9 of the 19 ladder layouts fall under the rule (eg_fine.py, part 3).
- Read from the code: PENALTY_NO_TAIL, 600, is charged on any step whose survey does not lead back to the dragon's tail, whatever room lies ahead (375, 168, 4987-4989). Estimate: this is what holds them at the exit after round 60, since the way out is a corridor one tile wide. The bot owner's per-term logs at this exit say the same (plan.md:637); the replays only show the standing there (exit-corner row).
- Read from the code: IDLE_ESCAPE is 0 (257) and would not help: it only routes to a portal out of a known region of 40 tiles or fewer (4645-4710), and Tower Defense has no portals.
- Read from the code: the threat rule costs a dragon of length 2 between 225 and 563 a step near an enemy of length 2 to 4 (2471-2479, 5077-5092) against 740 for a pearl one step away (5021-5033, 5055-5057). Measured: we leave 5 of 147 pearls on an open neighbour, so it is not what costs us here.
- Read from the code, Stripes: a non-queen dragon's survey counts pearls behind portals (2954-2957; portals are skipped only for the queen, 2987-2989), so the pearl pull brings it to the portal mouth. The step in is scored at the exit tile (5175-5176), where a 4-tile room costs 400 x (3 x length + 8 - room), about 4,000 at length 2 (4978-4983), and the pocket rule takes 1,000 more and the eat bonus (165-167, 5049-5057). The queen takes a portal only as a last resort (QUEEN_NO_PORTAL, 144, 5159-5161; she went into a room 12 times in the 16 games). Estimate: stepping in scores about 4,500 below staying outside, so the dragon waits at the mouth: 36.2% of our Stripes turns start within 2 path steps of a known pearl and eat nothing (theirs 17.5%, eg_fine.py).

## The card

title: Let a short dragon go when the centre pull has stopped moving it (default-off STALL_RELEASE)
slug: stall release
What we tried: Nothing built. Counted rounds 0 to 120 of the 174 main ladder games on 2-dragon-start layouts and read main.cpp; the proposal is below.
Did it work: Not run yet. Open until the mechanism check on Tower Defense is done.

### Area
Opening, rounds 0 to 60, dragons of length 4 or less, on layouts where the centre rule is on (1000 cells or fewer and wide, or 700 or fewer).

### Claim
Estimate, from the measured rows and the code lines above: on Tower Defense our two starting dragons never leave the start room in the first 60 rounds because CENTER_PULL pins them to the wall nearest the centre, and after round 60 the no-tail penalty keeps them at the exit. Proposal, one switch STALL_RELEASE (rounds; 0 = off, first value 12): each dragon remembers the round it last set a new lowest centre distance; while the centre rule is on and that is STALL_RELEASE or more rounds ago, (a) skip CENTER_PULL at main.cpp:5061 and (b) skip PENALTY_NO_TAIL at main.cpp:4987 when the room ahead is at least 6 x length + 8. One int of state, one test, two conditions; no map name.

### Evidence
- Measured: 27 of 27 main games on Tower Defense never grew (8 won). Inside the start room in 3,408 of 3,408 of our turns in r0-59; no head of ours is outside before round 69 in any game and none by r120 in 18; theirs is out at round 15 (median). Recounted another way (coordinates, heads at round end): 3,399 of 3,399, first exit at round 68, 18 with none, theirs 14 (eg_recount.py).
- Measured: 48.9% of those turns are on the 9 tiles nearest the centre, and this ends in the bin where the rule ends (round 60). Outside the room our dragons eat 0.124 pearls a turn against 0.012 to 0.041 inside.
- Measured: the test is selective. With 12 rounds it is true in 56.6% of our short-dragon turns on Tower Defense, 10.7% on weakhold, 5.1% to 9.2% on Trophy, 5.6% on Stripes (eg_stall.py nogrowth; with growth also resetting the clock: 43.4%, 10.1%, 1.8% to 4.7%, 2.5%).
- From the bot owner's notes, not re-run by me (plan.md:637-641): on local Tower Defense CENTER_PULL=0 gave 100 cells by r100 against 52 and 7 of 8 won; with NO_TAIL_ROOM=6 as well 152 cells. Both were rejected as global settings: CENTER_PULL=0 lost Autarky, Prisoners Dilemma and Stripes 0 of 8 each. EXPLORE_GAIN 5 to 40 did not get the dragons out (plan.md:636), so the test proposed under F7 is already answered.

### Expected signal
Estimate of what the check should show. Local games on Tower Defense with the switch at 12: first round one of our heads is outside the start room at 30 or earlier (median; now never before 69, opponents 15); at least 30% of our turns in r30-59 outside the room (now 0%, opponents 52%); pearls by r100 at 15 or more (now 1 to 7 in every main game, F7). On the ladder afterwards: more than 6 dragons at r100 in at least 5 of the next 10 Tower Defense games (now 0 of 27).

### What would show it's wrong
- With the switch on, the median first exit on Tower Defense is still after round 45: another term holds them, and the two named here are not the cause.
- They leave but pearls by r100 stay at 7 or fewer: leaving is not the bottleneck.
- On the local sets where CENTER_PULL=0 lost (Autarky, Prisoners Dilemma, Stripes), the switch costs 3 or more games of 8 against the same build with it off: holding at the centre is the value there and a stall test does not keep it.
- Wall or own-body deaths of our dragons in r0-100 rise on corridor layouts (weakhold, Maze): the no-tail waiver is sending short dragons into dead ends.

## Against it

- Measured: it is one layout. The 16 Stripes games are untouched: there both sides are 8+ steps from the start by round 8 (median, eg_home.py) and the gap is the portal rooms. The opponents pay for those rooms with 43 deaths in 16 games; F18 already found that going in kills two dragons in three, and no single rule I can name gets the pearls without the deaths.
- From the notes: both terms were tried as global settings and thrown out (plan.md:639-641), and CENTER_PATH with NO_TAIL_ROOM=6, the nearest earlier form, won Tower Defense 8 of 8 but lost 8 on the held-out set (44 against 52). The gated form is untested. Those sets are games against our own older build with many flips either way.
- Measured: the test is not rare elsewhere. It is true at some point in 22 of 22 weakhold games, a layout we win 13 of 22 on. A short dragon that has not grown for 16+ rounds is ordinary: 26% to 64% of short-dragon turns on Maze, Queen Of Spades and Trauma (eg_home.py). That is why the waiver is tied to the centre stall and not to hunger.
- Estimate: the second hold is not proven from replays. If it is something other than the no-tail penalty, part (b) does nothing and part (a) alone may free few: after the rule ended at round 60, only 9 of 27 games had a head of ours outside by round 120. The queen, one of our two starting dragons, also carries room rules the switch does not touch (QUEEN_DEAD_END, main.cpp:111-113, 4996-5005); she may stay when the other leaves.
- Measured: the upside is bounded. Tower Defense is 27 of 400 main games; we won 8 of them anyway, 6 of the 25 in which the opponent left its room by round 60. The 0.124 pearls a turn outside comes from 290 turns in 9 games.
- Measured: the opponents do not find pearls by heading for them. With the nearest pearl 16+ steps away they step toward it in 60.5% of turns and we in 46.9%; their first meal is no earlier (F41). What they do is leave and keep going straight.
- Not checked: that main.cpp on disk is the build that played as main on the ladder; whether the qualifier has a layout with a walled start whose way out leads away from the centre. The property is that, not the name.
