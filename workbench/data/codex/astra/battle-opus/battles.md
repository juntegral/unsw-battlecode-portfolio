# one17 (bot 21693) ranked battles after 04:31Z, one block per battle (battle-opus)

Marks: [M] measured from replay, [C] code, [E] inferred. f0 / f1 = free neighbour cells of the queen's head at her second-last / last turn start.

## b1532562 Team SKKU (2171), WON 4-1, seat A, +71 in the file, one17 all 5 games [M]
- LOSS 1532565 Tower Defense (512 cells): eliminated r355. Behind for good from r75 (total 13 v 19; r100 5 / 15 v 13 / 32; natural pearls before r100 16 v 42). Queen 1, L3, rammed r74 by dragon 8 (L4, 3 steps = 1 free + 2 paid, started 3 away), in her view; f0 / f1 = 3 / 2; 2 mates within 4; their queen alive (died r100-125). She walked r72-r74 toward dragon 8 as it closed 6 > 4 > 2. Class: rammed in the open + out-eaten from r75.
- Fixes: (c) applies (512 cells under QUEEN_MIN_CELLS, no queen role, main.cpp:5682 [C]). Nothing new.

## b1533048 Computers (2148), LOST 2-3, seat B, -28, one17 all 5 (wins weakhold 55-22, Prisoners Dilemma 47-0) [M]
- 1533048 Maze (1152): THROWN, lost on queen while ahead (r200 total 153 v 131, r499 157 v 144; their queen L5-6 until r350). Queen 1 walked into a 3-cell walled dead end lined with 3 pearls: r204 at (36,9) L4 split 2+2, r205 N to (36,8), r206 (36,7), r207 split 4 to 2+2, r208 (35,7), r209 no move, died on the wall as L3. No attacker. f0 / f1 = 1 / 0. At r205 her other exits: W (35,9)>(35,8) then mate body (34,8), mate head (33,8); S (36,10) mate head. Class: self-trap after a split (pocket). Behind for good r209.
- 1533050 Queen Of Spades (875): out-eaten from r50 (14 v 25; r100 6 / 14 v 12 / 32; natural pearls before r100 15 v 65; r25 2 / 6). Queen 1 alone, r109 paid a segment (3 to 2) up a walled staircase (free 1, 1, 2), rammed r111 by dragon 44 (L4, 3 steps = 1 free + 2 paid, from 3 away), unseen by her or mates. Class: rammed from a one-way place + out-eaten from r50.
- 1533051 Slithery Fight (1701): ahead until r325 (r275 275 v 247), behind from r350. Queen 0 L4 rammed r280 by dragon 955 (L13, 4 free steps, from 4 away), unseen by her, seen by a mate; f 2 / 2; 2 mates within 4; their queen L5 (33 at r499). Class: rammed in the open by a long dragon on free steps. 17 of our L8+ dragons rammed (L44 r412, L40 r460).
- Fixes: (a) fits Maze [M board, E guard reasoning]. Maze queen also split 4 to 2+2 three times in 30 rounds (r180, r204, r207), no foe within 6. (d) unverified for Queen Of Spades (pearls born r9 / r12 at (7,9),(8,9) uneaten at r111 beside her, behind walls). (b)(c)(e)(f) no.

## b1533125 Team SKKU (2180), WON 3-2, seat A, rating change not in the file (0), one17 all 5 [M]
- 1533127 Portals (512): THROWN WIN. Their queen dead since r222, ours L4-6; lost on longest 42 v 61 after she died r398. r395 queen 1 (L5) at (19,6) stepped W through a known portal into (12,3) for a pearl: walls N, S, W, the portal the only door, her own body across it. Free 0 at r396-r398; split 6>4, 4>2 to stall, then as L2 moved onto her own tail (reason own body). No attacker. A pearl was 1 step E at (20,6). Class: self-trap in a one-cell box (NEW shape: through a portal, splits after not before).
- 1533125 Devil (512): eliminated r181; out-eaten from r50 (14 v 21, r75 7 v 38; natural 30 v 67). Queen 1 split 4>3 r27, L2 by r40, circled a 2x2 block r40-r58, walked S r59-r61 toward dragon 14 (gap 6 > 4 > 2, in view); at r61 both free cells touched its head; rammed by dragon 14 (L3, 1 free step). f 2 / 2, no mate within 4, their queen alive. Class: rammed in the open.
- NEW: Portals + Maze = a dragon enters a width-1 dead end for a pearl and cannot turn round. Fix (d) must exclude single-door compartments without a 2x2. (c) applies to both games (512 cells, no queen role). (a) not Portals (walls only).

## b1532570 Sponge(Albert and Bob) (2543), LOST 0-5, seat A, -49, one17 all 5; our queen died in all 5, theirs alive each time [M]
- 1532570 Islands (2240): lost on longest 19 v 57, both queens dead at the end. Behind on total from r25 (28 v 37; r100 108 v 116). r163 queen 0 (L4) split 2+2 with heads 186 (L3), 289 (L2) at 3-4; r164 stepped W toward 289; r165 on her own turn rammed 289's head (L2 v L2) with 2 free cells open. Class: other = queen rams a head herself (NEW). [C] main.cpp:1820-1838 qs_plain then hunt_path / ram_path; [E] that path.
- 1532571 Stripes (288): eliminated r120; out-eaten from r75 (13 v 26). Queen 1 L2 rammed r108 by dragon 47 (L3, 1 free step), in view; f 2 / 2; dragon 39 (L3) 3 away for 5 turns. Class: rammed in the open. (c) applies.
- 1532572 Queen Of Spades (875): eliminated r178; out-eaten from r50 (12 v 18), collapse r75-r100 (6 / 14 to 2 / 5). Queen 0 L3 alone rammed r166 by dragon 37 (L3, 1 free + 1 paid), in view; f 3 / 2. Class: out-eaten from r50, rammed in the open.
- 1532573 Autarky (972): eliminated r330; behind from r25 (33 v 37; r50 24 v 42; natural 44 v 97). Queen 1 L2 alone, 4 heads within 4, rammed r82 by dragon 16 (L3, 1 free step) from a 1-free cell (f 3 / 1), in view. Class: rammed from a one-way place + out-eaten from r25.
- 1532574 Around UNSW (4096): lost on queen while ahead on total (r300 358 v 238). Queen 0 grew 7 > 11 r313-r319 alone, rammed r319 as L11 by dragon 534 (L3 at her turn start, 4 away; scan says 5 steps, unverified), in view; f 2 / 3. Their queen 19-24 then, 4 at r499: a living L11 queen wins. Class: rammed in the open (long queen, no escort).

## b1531921 Check Raise (2010), WON 3-2, seat A, -25 in the file, one17 all 5 [M]
- 1531923 Trophy (625): eliminated r240; out-eaten from r50 (12 v 30; r100 8 / 21 v 38 / 90; natural 35 v 100). Queen 1 split 5 > 3 four times (r77, r85, r96, r115), L2 by r136; dragon 72 (L2) 2 away for 5 turns, rammed her r145 (1 free step), in view; f 2 / 2; 3 mates within 4. Class: out-eaten from r50 + rammed in the open.
- 1531925 Default (1024): lost on longest 5 v 41, both queens dead. Behind from r25 (20 v 27; r100 5 / 13 v 26 / 62). Queen 1 L3 alone walked N up column 24 r59-r64 at head 24 (L3) 3 ahead in view; rammed r64 (1 free + 1 paid); f 3 / 3. Class: rammed in the open.
- None of (a)-(f) applies.

## Unranked one17 set b1532047 (Cache me outside 2270, seat A, 5 W / 10 L), own-turn queen deaths only [M]
- 1532061 Slithery Fight: THROWN WIN (their queen dead since r38). Queen 1 L15 stood at (42,1) and split off 2 a turn r370-r376 (15 > 4), then ate into a 2-cell nook (41,0),(42,0), free 1 / 0, split 6 > 4, died on the wall r380. Fix (b): [C] main.cpp:1797 is the standing split; QS_SHED_MAX is only on :1808.
- 1532050 Maze: queen 0 L3 in a width-1 corridor (1 free cell from r210), exit (19,8) plugged by mate 324's body, died r216 on it. Total 155 v 53 at the end, lost on queen. Class: boxed with a mate.
- Other 8 queen deaths are rams (weakhold r99, Australia r158, Islands r139, Stripes r42, Tower Defense r73, Default r147, Trophy r172; their queen already dead in Stripes, Default, Trophy); Trauma no queen death (30 v 33).

## b1529403 SSS (2528), lost 0-5: bot 21651 (one16), not one17, not analysed.
