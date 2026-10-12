# Reports sent to the lead by battle-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:02:36 — Battle 1532562 SKKU won 4-1, one loss

b1532562 Team SKKU (2171), WON 4-1, seat A, +71 in the file (bot 21693 = one17, all 5 games) [M]
- LOSS 1532565 Tower Defense (512 cells): eliminated r355. Behind for good from r75 (total 13 v 19; r100 5 dragons / 15 v 13 / 32; natural pearls before r100 16 v 42). Decisive: queen 1, L3, rammed r74 by dragon 8 (L4, 3 steps = 1 free + 2 paid, started 3 away), in her view; her free cells 3 then 2 at her last two turn starts; 2 mates within 4; their queen alive (theirs died r100-125, so a queen alive past r125 was a win). She walked r72-r74 (19,1)>(19,2)>(19,3) toward dragon 8 as it closed 6 > 4 > 2. Class: rammed in the open + out-eaten from r75.
- NEW / fixes: nothing new. (c) applies: 512 cells is under QUEEN_MIN_CELLS, so she has no queen role here (main.cpp:5682) and stepped toward a visible equal-length head. Same Tower Defense starve as one16 1528859 but milder (r100 total 15, was 3). (a)(b)(d)(e)(f) do not apply.
- Not one17: b1529403 SSS 0-5 was played by bot 21651 (one16), done 04:32-04:39Z; I am not analysing it. 1533125 / 1533048 / 1532570 / 1531921 are not on disk yet (collector last wrote 13:52 KST); polling.

---

## 2026-10-09 05:05:53 — Battle 1533048 Computers lost 2-3, three queen deaths

b1533048 Computers (2148), LOST 2-3, seat B, -28 (one17 all 5; wins weakhold 55-22, Prisoners Dilemma 47-0). All 3 losses = our queen dead, their queen alive [M]
- 1533048 Maze (1152): THROWN, lost on queen while ahead (r200 total 153 v 131, r499 157 v 144; their queen L5-6 until r350). Queen 1 walked into a 3-cell walled dead end lined with 3 pearls: r204 at (36,9) L4 split to 2+2, r205 stepped N to (36,8), r206 (36,7), r207 split 4 to 2+2 again, r208 (35,7), r209 no move, died on the wall as L3. No attacker (nearest foe 73 L3 at 5 then 3). Free cells at her last two turn starts 1 / 0 (1 since r206). At r205 her other exits were W (35,9)>(35,8) then mate body at (34,8) with mate head at (33,8), and S (36,10) = mate head. Class: self-trap after a split (pocket). Behind for good: r209.
- 1533050 Queen Of Spades (875): out-eaten from r50 (14 v 25; r100 6 dragons / 14 v 12 / 32; natural pearls before r100 15 v 65; r25 still 2 dragons / 6). Queen 1 alone (0 mates within 4 from r98 on), r109 paid a segment (L3 to L2) to sprint up a walled staircase (free cells 1 at r109 and r110, 2 at r111), rammed r111 by dragon 44 (L4, 3 steps = 1 free + 2 paid, from 3 away), not in her view or any mate's. Class: rammed from a one-way place + out-eaten from r50.
- 1533051 Slithery Fight (1701): ahead until r325 (r275 total 275 v 247), behind for good from r350. Queen 0, L4 (she sat at 3-4 from r25 on; theirs L5, grown to 33 by r499), rammed r280 by dragon 955 (L13, 4 steps all free, from 4 away), not in her view, seen by a mate; free cells 2 / 2 (wall on one side), 2 mates within 4. Class: rammed in the open by a long dragon on free steps. Also 17 of our dragons of L8+ rammed (L44 r412, L40 r460, both by 3-step attackers) = long dragon rammed.
- NEW / never: Maze is the "working bot never does this" one: a queen eating her way into a dead end and standing in it. Fix (a) fits Maze exactly [M board, E for the guard's reasoning]: the only non-fatal exit at r205 ran into a mate's body 3 cells on, so both exits looked like pockets and the pearl step was kept. Also in Maze she split 4 to 2+2 three times in 30 rounds (r180, r204, r207) with 1-2 free cells and no foe within 6; not (b) (she is not 10+), but a queen that splits back to 2 while their queen is 5-6 cannot win the queen count anyway. (c)(e)(f) do not apply (875+ cells). (d) unverified for Queen Of Spades: pearls born r9 / r12 at (7,9),(8,9) were still uneaten at r111 right beside her, behind walls. (b) would not have saved Slithery (queen L4, never long).

---

## 2026-10-09 05:11:53 — Battle 1533125 SKKU won 3-2; Portals thrown, warning on fix (d)

b1533125 Team SKKU (2180), WON 3-2, seat A, rating change not in the file yet (shows 0, us 2100) (one17 all 5; wins Prisoners 17-0, Autarky 107-3, Stripes 36-0) [M]
- 1533127 Portals (512): THROWN WIN. Their queen dead since r222, ours alive at L4-6; lost on longest 42 v 61 after she died r398. r395 queen 1 (L5) at (19,6) stepped W through a portal into (12,3) for a pearl (grew to 6): that cell has walls N, S, W and the portal as its only door, and her own body lay across the door. Free cells 0 at r396, r397, r398; she split 6>4, 4>2 to stall (r396, r397), then as L2 moved back onto her own tail and died (reason own body). No attacker (foe 829 L42 beside the box, irrelevant). The portal was a known one, not a blind one (main.cpp:8082 only clears blind) [C]. At r395 a pearl was 1 step E at (20,6) in the open. Class: self-trap in a one-cell box (splits came after, not before). Behind for good: r398.
- 1533125 Devil (512): eliminated r181; out-eaten from r50 (total 14 v 21, r75 7 v 38; natural pearls before r100 30 v 67). Queen 1 split 4>3 at r27, was L2 by r40, circled a 2x2 block (18-19, 0-1) from r40 to r58 with 1-2 free cells and 2-4 enemy heads within 6, then walked S down a walled column r59-r61 toward dragon 14 (gap 6 > 4 > 2, in her view). At r61 both her free cells touched its head; rammed by dragon 14 (L3, 1 free step). Free cells 2 / 2, no mate within 4, their queen alive. Class: rammed in the open (walked into a visible longer head).
- NEW, and a warning for fix (d): the Portals death and the Maze death (1533048, 3-cell dead end) are the same thing: a dragon steps into a width-1 dead end for a pearl and can never turn round. A compartment whose only door is the one she enters by is fatal at any depth unless it holds a 2x2 open block. If (d) makes dragons enter small walled compartments for a pearl one step away, it must exclude compartments with a single door and no 2x2, or it produces exactly these two deaths. A one-line guard for the queen (never enter a cell whose only other exits are walls, at depth 1-3, walls only, mates not counted) would have kept both games: Portals was a sure win, Maze a likely one.
- Fixes: (c) applies to both (512 cells: no queen role, so on Devil she walked into a head and on Portals took a pearl through a portal like any worker). (a) does not apply to Portals (no mate involved, pure walls). (b)(e)(f) no.

---

## 2026-10-09 05:11:53 — Unranked one17 set: fix (b) case and 4 own-turn queen deaths

Extra, from the unranked one17 set b1532047 (Cache me outside 2270, seat A, 5 W / 10 L), only the two own-turn queen deaths looked at [M]
- 1532061 Slithery Fight: THROWN WIN and a clean case for fix (b) IN ONE17. Their queen dead since r38. Our queen 1 was L15 at r370 at (42,1), enemy heads L2-L4 at 1-5; she stood still and split off 2 a turn r370, r372, r373, r374, r375, r376: 15 > 13 > (ate) 14 > 12 > 10 > 8 > 6 > 4. QS_SHED_MAX 9 did not stop it (she was 15, 14, 12, 10 at four of those splits). Then r377 N to (41,0), r378 E to (42,0), eating both: a 2-cell walled nook whose way out (42,1) was her own 4th segment; free cells 1 / 0; r379 split 6 > 4, r380 died on the wall. Lost on longest 34 v 71.
- 1532050 Maze: queen 0 L3, in a width-1 corridor with 1 free cell every turn from r210 (after a portal), r216 at (18,8) the corridor's only exit (19,8) was the body of mate 324 (L4); free 1 / 0; died on the mate's body. We had total 155 v 53 at the end; lost on queen (theirs 25). Class: boxed with a mate.
- So of 15 one17 losses on disk (5 ranked + 10 unranked), 4 are the queen killing herself with no attacker: Maze 1533048 (dead end), Portals 1533127 (portal box), Slithery 1532061 (shed then nook), Maze 1532050 (mate plug). In 2 of them their queen was already dead (sure wins), in the other 2 we led on total. The other 8 unranked queen deaths are rams (weakhold r99, Australia r158, Islands r139, Stripes r42, Tower Defense r73, Default r147, Trophy r172; their queen already dead in Stripes, Default, Trophy); Trauma had no queen death (30 v 33).
- Not checked: why QS_SHED_MAX let the 15 > 4 chain through (code path), the 7 ram deaths in detail.

---

## 2026-10-09 05:11:53 — Code line for fix (b): standing 2-cell split is main.cpp:1797

Code pointer for fix (b), one17-bot/main.cpp [C]: the standing 2-cell split in 1532061 (15 > 4 in 7 rounds) is line 1797, `if (!exposed && ct.can_split(keep) && ...) split_off(keep);` (keep = MIN_SIZE = 2: she sheds 2 whenever her chosen step is hit_blocked but her own tile is not exposed, then stands; next turn the same). QS_SHED_MAX is tested only on line 1808 (the exposed branch that keeps 2 and sends the rest away), so it never touches this path. [E] The same length test on line 1797 would have ended the chain at the first split (she was 15). Not built or played by me.

---

## 2026-10-09 05:14:22 — Battle 1532570 Sponge lost 0-5; queen rammed a head herself

b1532570 Sponge(Albert and Bob) (2543), LOST 0-5, seat A, -49 (one17 all 5). Our queen died in all 5, theirs alive each time [M]
- 1532570 Islands (2240): lost on longest 19 v 57, both queens dead at the end (theirs L17 died r200-300). Behind on total from r25 (28 v 37) but close (r100 108 v 116). r163 queen 0 (L4) split to 2+2 with heads 186 (L3) and 289 (L2) at 3-4; r164 stepped W toward 289; r165 ON HER OWN TURN she rammed 289's head (L2 v L2, both die) with 2 free cells open (N (19,18), S (19,20)). 2 mates within 4. Class: other = QUEEN RAMS A HEAD HERSELF (new).
- 1532571 Stripes (288): eliminated r120; out-eaten from r75 (13 v 26). Queen 1 L2 walked W along row 9 r104-r108 with dragon 39 (L3) holding 3 away, rammed r108 by dragon 47 (L3, 1 free step, adjacent), in view; free 2 / 2; 1 mate within 4. Class: rammed in the open.
- 1532572 Queen Of Spades (875): eliminated r178; out-eaten from r50 (12 v 18), collapse r75-r100 (6 dragons / 14 to 2 / 5 v 10 / 26). Queen 0 L3 alone, rammed r166 by dragon 37 (L3, 2 steps = 1 free + 1 paid), in view; free 3 / 2. Class: out-eaten from r50, then rammed in the open.
- 1532573 Autarky (972): eliminated r330; behind from r25 (33 v 37; r50 24 v 42; r75 14 v 46; natural pearls before r100 44 v 97). Queen 1 L2 alone with 4 heads within 4, rammed r82 by dragon 16 (L3, 1 free step) from a cell with 1 free neighbour (free 3 / 1; 1 at r80 too), in view. Class: rammed from a one-way place + out-eaten from r25.
- 1532574 Around UNSW (4096): lost on queen while far ahead on total (r300 358 v 238, r499 306 v 265). Queen 0 grew 7 > 11 r313-r319 eating alone (0 mates within 4 from r316), rammed r319 as L11 by dragon 534 (L3 at her turn start, 4 away; the scan says 5 steps, I did not verify how an L3 pays that), in view of her and a mate; free 2 / 3, open ground. Their queen was 19-24 then but ended at 4: a living L11 queen wins this game. Class: rammed in the open (long queen, no escort).
- NEW / never: Islands, the queen trading herself into an enemy head on her own turn. [C] one17 main.cpp:1820-1838 "Trapped: for this turn she moves as a plain dragon" sets qs_plain and then calls hunt_path / ram_path; [E] that is the path (not confirmed by a run). A queen should never take ram_path. Fixes: (c) Stripes only (288 cells). (a)(b)(d)(e)(f) none. Around UNSW is the opposite of (b): she was 11 with heads at 3-4 and neither split nor ran.

---

## 2026-10-09 05:14:22 — Battle 1531921 Check Raise won 3-2 but -25

b1531921 Check Raise (2010), WON 3-2, seat A, -25 in the file (one17 all 5; wins Stripes 57-0, Queen Of Spades 92-0, Autarky 104-0). A team rated 100+ below us took two games, both by starving us and then ramming a short queen [M]
- 1531923 Trophy (625): eliminated r240; out-eaten from r50 (12 v 30; r100 8 dragons / 21 v 38 / 90; natural pearls before r100 35 v 100). Queen 1 split 5 > 3 four times (r77, r85, r96, r115), was L2 by r136; dragon 72 (L2) sat 2 away from her for 5 turns r141-r145 while she walked E, then rammed her r145 (1 free step), in view of her and a mate; free cells 2 / 2; 3 mates within 4 did nothing; their queen alive. Class: out-eaten from r50 + rammed in the open.
- 1531925 Default (1024): lost on longest 5 v 41, both queens dead (theirs after ours). Behind from r25 (20 v 27; r100 5 / 13 v 26 / 62; natural 20 v 52). Queen 1 L3, alone (0 mates within 4 from r56), walked straight N up column 24 r59-r64 at head 24 (L3) that stood 3 ahead in her view at r63, with dragon 17 (L2) tailing 3 behind for 9 turns; rammed r64 by dragon 24 (2 steps = 1 free + 1 paid); free 3 / 3, open ground. Class: rammed in the open (walked at a visible equal head).
- NEW / fixes: nothing new; none of (a)-(f) applies (625 and 1024 cells, no pocket, no long queen). Common to both and to Sponge's Queen Of Spades / Autarky and SKKU's Tower Defense / Devil: we have 2-8 dragons at r100 against 10-38, and a queen of L2-L3 with an enemy head held 2-3 away for several turns keeps walking instead of leaving or being covered. The economy collapse comes first in all six (behind by r25-r50).

---

## 2026-10-09 05:14:22 — closing summary

Six battles processed and reported to the lead; the poller is running in the background and will wake me when the next ranked battle finishes downloading (or at 14:44 KST for the final tally).

Status so far (one17, bot 21693, ranked after 04:31Z):
- b1532562 Team SKKU won 4-1, b1533125 Team SKKU won 3-2, b1531921 Check Raise won 3-2 (-25), b1533048 Computers lost 2-3 (-28), b1532570 Sponge lost 0-5 (-49); b1529403 SSS was one16, skipped.
- Running file: `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/battle-opus/battles.md`

---

## 2026-10-09 05:14:22 — closing summary

No new battles on disk yet (last download 14:07 KST). The poller is still running and will wake me for the next one; I'll report each battle with its bot id (one17 = 21693, one18 = 21761) and, for one18 games, the pocket check on own-move queen deaths, until 14:55.
