# Stripes: why we never win there (4 of 24 main games), 7 Oct 2026

1. **What loses the games.** 86% of the pearls are born in rooms of 1, 3 and 4 tiles behind portals. Both sides stand at a room door at round 9; they step in at round 12 and we at round 38 (medians). Our queen then spends half of rounds 0-100 beside the door of a 4-tile room she could walk straight through, and our other starting dragon three quarters of them beside the door of a dead-end room.
2. **The change.** One default-off switch, POCKET_LOOP: a small room that has a portal edge inside it leading out is not a pocket, so the pocket penalty stops keeping a short dragon off a pearl in it.
3. **How sure.** Sure of the behaviour (every turn of all 24 games counted) and of the rule (code, and a pattern only that rule predicts: at length 2 we go in 79% of the time when the entry tile is empty and 9% when the pearl lies on it). Not sure it wins games: it reaches about half of the gap, nothing was built, and it is one layout.

Labels: [M script] = measured by me, script in dossier/work/ (rows from st_scan.py over the 24 main games; "theirs" is the opponent in the same games). [D] = dossier summary.md. [C] = read from battlecode/mybot2/main.cpp, line given. [E] = estimate.
Words: "door" = an open-area tile with a portal step into a room under 48 tiles. "Loop room" = a kelp-closed room with a portal edge inside it, so a dragon walks in at one tile and out at the other. "Dead-end room" = a room whose only portal edge is on its border.

Earlier diagnoses, one line each: diag-islands (leader rules from round 151 above 1200 cells) does not apply: 288 cells, 23 of 24 games end by elimination, 16 before round 170 [M st_games.py]. diag-australia (short dragons pass up head-on trades above 1200 cells) does not apply: head-on net is -0.25 a game [D]. sweep (keep moving) does not apply [D: dither 12% against 14%]. early-growth (centre pull, walled start) does not apply: both sides are at a door by round 9 [M st_open.py].

## What happens

The layout [M st_map.py, st_rooms.py; respawn from maps.json]: 24 by 12, one open area of 248 tiles in four bands, 8 portal pairs, 2 dragons of length 2 a side. Four 4-tile loop rooms (two hold the fast tiles, respawn 4 and 7 rounds median; the walk through is 4 steps). Four 3-tile and four 1-tile dead-end rooms: nobody ever left one alive; a 3-tile visit eats 3, splits off a child whose head is outside, and the 2-long rest dies. Two sealed 4-tile rooms with no portal. Natural births in 24 games: loop rooms 958 (37%), 3-tile dead ends 979 (38%), 1-tile 96, sealed 192, open area 360 (14%).
The three gaps of table C that the 15 normal layouts do not show [D]: pearls behind portals eaten 14% against 71% of those born (elsewhere 63 and 55); a pearl on a neighbouring tile not taken in 74% against 27% of such turns (elsewhere 19 and 23); splits by r100 3.7 against 16.2 (elsewhere 56 and 53). They are one behaviour seen three ways. Read round by round (st_trace.py): 1322016, 1321456, 1254072, 1280772, 1256411. In 5 of 5 our queen reached a loop-room door at round 8 to 11, did not step onto the pearl, and in 4 got in 9 to 25 rounds later by the room's other door; our other starter circled a 2 by 2 block beside a dead-end door from round 11 to 25 on. Their starters in the same games: loop room at round 9 by the front door (1321456, again at 18 and 27; 1254072), dead-end dive at round 8 to 12 (1322016, 1321456, 1254072, 1280772), neither in 1256411, which we won.

| All 24 games, rounds 0-100 unless said | Ours | Theirs | Source |
|---|---|---|---|
| Pearls eaten a game by r50; by r100 | 3.7; 9.6 | 14.8; 39.5 | [D] |
| Of those by r100: open area / loop rooms / dead-end rooms | 3.5 / 5.0 / 1.1 | 6.0 / 12.8 / 20.6 | [M st_pergame.py] |
| First round a dragon stands at a door with a pearl behind it (median) | 9 | 9 | [M st_open.py] |
| First round one takes such a step (median); games with none by r60 | 38.5; 10 | 12; 5 | [M st_open.py] |
| Queen: turns that start within 2 steps of a door of a loop room with pearls | 49% (962 of 1,954) | 24% (456 of 1,924) | [M st_where.py] |
| Other starter: turns within 2 steps of a dead-end door; pearls it ate there | 74% (1,372 of 1,863); 2 | 25% (270 of 1,090); 14 | [M st_where.py] |
| Loop-room door, pearl on the entry tile, far side already seen: took the step (whole game) | 15% (49 of 328) | 63% (228 of 360) | [M st_known.py] |
| Same door, length 2, side has 4 dragons or fewer: pearl on the entry tile / pearl only deeper in | 9% (12 of 129) / 79% (26 of 33) | 57% (27 of 47) / 50% (10 of 20) | [M st_crowd.py; recounted from the replays with the doors typed in by hand, the two pearl rooms only: 12 of 123 and 26 of 32, theirs the same, st_recount.py] |
| Same door, length 3: pearl on the entry tile / only deeper in | 9% (11 of 129) / 19% (11 of 58) | 58% (64 of 111) / 61% (50 of 82) | [M st_known.py] |
| Dead-end 3-tile door, pearl on the entry tile: took the step (whole game) | 4% (33 of 783) | 59% (355 of 605) | [M st_known.py] |
| Loop-room visits, whole game: a game; left alive; pearls a visit | 9.9; 85%; 1.03 | 24.9; 85%; 1.34 | [M st_rooms.py] |
| Dead-end 3-tile visits, whole game: a game; pearls a visit; splits with the child outside | 1.5; 2.94; 33 in 35 | 15.4; 2.90; 397 in 370 | [M st_rooms.py] |
| Net length, 24 games summed (pearls eaten there minus length that died there): loop / dead 3 / dead 1 / open | +99 / +6 / -10 / +39 | +256 / +162 / -11 / +56 | [M st_pergame.py] |
| Dragons; total length at r100, or at the end if earlier | 2.8; 6.7 | 8.5; 20.7 | [M st_pergame.py] |
| Our record when they made 10 or more room visits by r100 (16 games) / fewer (8 games) | 1 won / 3 won | | [M st_pergame.py] |
| Our loop-room visits by r100 in our 4 wins / our 20 losses | 8.5 / 2.9 a game | | [M st_pergame.py] |

## Why, in the code

- [C] The queen rules are off here: is_queen() needs more than 600 cells or a closed home (159, 3332-3333). Both starters are ordinary dragons. [M] She made 28 loop-room visits.
- [C] The pull to the door: the survey walks through a portal whose far side is known (1358-1366, 2993), so a pearl in the room pulls 2 x (260 - 40 x steps) (346-348, 5021-5023), 360 from the door tile.
- [C] The step in is scored at the exit tile, minus 150 (5162, 5175-5176, 379). In a loop room the survey leaves by the portal inside the room, so the room is the whole open area and the tight, trapped and no-tail terms (4978-4989) are zero.
- [C] What is left is the pocket rule. pocket_size() (3134-3166) floods open edges only; a portal edge is a wall to it (3151), so a loop room is a "pocket" of 4. Lines 5049-5057: grown = length + 1 if the destination holds a pearl; if grown is more than pocket / 2, minus 1,000 per excess and EAT_BONUS 300 (99) is withheld. Length 2 onto a pearl: -1,300. Length 2 onto an empty entry tile: nothing. Length 3: -1,000, or -2,300 onto a pearl. [M] That is the 9% / 79% / 9% / 19% pattern in the table; the opponents show no such pattern (57 / 50 / 58 / 61).
- [E] After the refusal the next tiles lose the pull (the dragon's own body closes the way back for a step), it drifts, the pull returns: it circles. Read from the scores above and seen in the five traces, not logged.
- [C] Dead-end 3-tile room: the room from the exit tile is 3, so tight 400 x (14 - 3), trapped 5,000 and no-tail 600 (344-345, 375, 4978-4989), and pocket 1,000 x (grown - 1). The harvest rule that would allow "eat, split, lose the rest" (1148-1170, 5276-5284) reads dead[k] and pearls[k], which are filled only for ordinary steps (5244-5255), never in the portal branch (5226-5235): through a portal it cannot fire. This half is not in the card.
- [C] Why another portal layout differs: when the far side of a portal is not known the step is not scored at all; a dragon of length 6 or less takes it blind at the best ordinary score + 88 (5172-5173, 5233-5235, 5354-5356, 382). [M st_known.py] On Stripes the two edges of a pair are one tile apart, so the far side is in view on arrival: 85% of loop-door chances (524 of 616). On Portals they are 24 columns apart: 38% (3,483 of 9,087).

## Which other layouts share the property

Property a bot can measure: a kelp-closed room under 48 tiles that contains both tiles of a portal edge whose exit lies outside it. The rule bites a length-2 dragon only when the room has 5 tiles or fewer (pocket / 2 under 3), and only when the dragon knows the far side. [M st_layouts.py; birth shares from the last 6 games of each layout, Stripes from all 24]

| Layout | Loop rooms | Births in them | Start | Our record | What the rule does there |
|---|---|---|---|---|---|
| Stripes | 4 of 4 tiles | 37% | 2 of length 2 | 4 of 24 | fires from round 9: door and room in one view, 2 dragons |
| Portals | 12 of 4 tiles | 71% | 3 of length 3 | 11 of 23 | mostly silent: 62% of door chances are blind, 72% of those taken [M st_known.py] |
| Slithery Fight | 2 of 4 tiles | 7% | 7 of length 25 | 18 of 37 | would fire for every dragon that knows the far side [C]; small supply |
| Default; Queen Of Spades | 9 of 16 and 2 of 25; 2 of 16 | 52%; 54% | 4 of 4; 2 of 3 | 21 of 30; 25 of 34 | only for dragons longer than half the room |
| Autarky; Prisoners Dilemma 1, 2; Trauma | 8 of 9; 4 of 9; 2 of 21 and 2 of 23 | 0% | | 24 of 26; 8 of 12, 9 of 13; 23 of 35 | nothing to eat inside |
| The other 10 layouts | none | | | 126 of 266 | the switch changes nothing [C] |

Portals is the check on the win side [M st_rooms.py, st_crowd.py on the 23 Portals games]: the same 4-tile loop rooms, and there we take the loop-room step in 63% of chances against their 49% (5,676 of 9,024; 4,206 of 8,668). With the far side seen, 4 dragons or fewer and length 2 or 3 we took 2 of 13, as on Stripes; but that case is rare there, the first entries are blind and the later ones come with 17 or more dragons (44% taken). Inside Stripes the same holds game by game (last two table rows). Dead-end rooms behind a portal, which the card does not touch: Stripes (8 rooms, 42% of births), Australia (2 of 12 tiles, 23%, 9 of 35 won), Maze (12 rooms, 5%), Portals (16 of 1 tile, 1%).

## The card

title: A room with a portal inside it is not a pocket (default-off POCKET_LOOP)
slug: pocket loop
What we tried: Nothing built. Counted every turn of the 24 main Stripes games and the 23 Portals games, read five games round by round, read main.cpp.
Did it work: Not run yet. Open until the mechanism check below is done.

### Area
The pocket rule (POCKET_CAP 48, POCKET_DIV 2, POCKET_PENALTY 1000) on rooms that have a portal edge inside them. Opening, dragons of length 2 and 3, any layout with such a room of 5 tiles or fewer whose door is within 3 tiles of the room.

### Claim
[E, from the rows and lines above] On Stripes our short dragons stand at the door of a walk-through room and do not step onto the pearl because pocket_size() counts the portal inside the room as a wall. Proposal, one switch POCKET_LOOP (bool, default false): in pocket_size() (main.cpp:3134-3166) remember each portal edge the flood meets (3151 skips them today); after the flood, if one of them has the tile on its other side inside the same flood and portal_exit() of it is a known tile outside the flood, return POCKET_CAP. Nothing else changes: the room, tight, trapped and no-tail terms still judge the step, and dead-end rooms stay pockets. One bool, about 12 lines, one function.

### Evidence
- [M] At a loop-room door with the far side seen we step onto a pearl on the entry tile in 15% of chances (49 of 328), the opponents in 63% (228 of 360).
- [M] With 4 dragons or fewer and length 2: 9% (12 of 129) when the pearl is on the entry tile, 79% (26 of 33) when it is only deeper in; theirs 57% and 50%. [C] The rule is silent in exactly the second case (5049-5052).
- [M] First step into a pearl room: round 38.5 against 12 (medians); our queen spends 49% of rounds 0-100 within 2 steps of the door.
- [M] Loop rooms are safe and pay: 85% of visits leave alive on both sides; net length by r100, 24 games: ours +99, theirs +256. Fast tiles there respawn in 4 and 7 rounds.
- [M] On Portals, where the far side is mostly unknown and the rule cannot fire, we enter more often than the opponents and win 11 of 23.

### Expected signal
[E] With the switch on, on a copy of the layout (tools/replay2map.js makes one from a ladder replay; its pearl gaps are estimates) or in the next ladder games: share of loop-room door chances with a pearl on the entry tile that are taken, length 2 and 3, at least 0.5 (now 0.15; theirs 0.63; count with st_known.py). First step into a pearl room at round 15 or earlier (median; now 38.5). Pearls eaten in loop rooms by r100 at least 10 a game (now 5.0; theirs 12.8) and pearls by r50 at least 8 (now 3.7). Loop-room visits that leave alive stay at 0.8 or more (now 0.85). On the 10 layouts with no loop room the fingerprint is identical with the switch on.

### What would show it's wrong
- The taken share stays under 0.3: another term holds them (the 150 portal cost, a threat term), and the pocket rule is not the cause.
- They go in and pearls by r50 on Stripes stay under 6: the rooms are emptied by the opponent first, or the walk is too slow to matter.
- Visits that end inside a loop room rise above 0.25 on Stripes, or deaths inside loop rooms on Portals rise by more than a tenth (140 a game now), or Portals, Default or Queen Of Spades lose 3 or more of 8 local games against the same build with the switch off.

## Against it

- [M] It reaches half of the gap at most. Net length by r100 is +134 for us and +463 for them; loop rooms are 157 of the 329 difference, the dead-end dive is 156, and the card does nothing for the dive. Our second starter stays beside its dead-end door (74% of its turns).
- [M] The door is delayed, not shut: in 4 of 5 traced games the queen got in by the other door 9 to 25 rounds later, and we already make 3.8 loop-room visits a game by r100 against their 7.8. The card removes a delay of about one cycle each time.
- [M] In 8 of the 24 games the opponent hardly used the rooms and we still lost 5 of them, at rounds 156 to 499. Those losses have another cause.
- [M] Loop rooms cost too: 11% of our visits end inside (27 of 238: wall 11, own body 10, other body 4, head-on 2), and on Portals 42% (3,223 of 7,595) once the half is crowded. More informed entries on Portals, Default and Queen Of Spades, layouts we win, is a cost I did not measure.
- [M] I cannot explain the 15% we do take; our queen takes 2 of 164 and our other dragons 50 of 169 (st_rooms.py), and both are ordinary dragons by the code.
- The rule reading is a reading. No build and no per-term log; I did not check that main.cpp on disk is the code that played. F18 is "weakened" in the ledger because taking the pearl looked fatal two times in three; split by room, the visit ends inside in 100% of dead-end visits and in 11 to 12% of loop-room visits [M st_rooms.py], which is what this card rests on.
- One layout. The property was found after looking, and the line "5 tiles or fewer, door in sight" comes from two layouts. Against opponents who also dive we may lose the race with the loop rooms alone.
