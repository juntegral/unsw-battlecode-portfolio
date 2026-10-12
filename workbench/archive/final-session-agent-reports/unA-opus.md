# Reports sent to the lead by unA-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:11:53 — RED heads-up: start box with portal-only exit into small rooms

unA-opus heads-up, RED on ONE map so far (ua_chain_448, 28x16): start box whose only exit is a portal into a closed 3x3 pearl room (room -> portal -> room -> portal -> field). mD17 never leaves the box: mirror = 0 pearls both seats in 500 rounds (draw 5,5); v m3base both seats 0 pearls by r100 (first eat r87 / r111) while m3base has 283 / 287 pearls and 60 dragons, we are eliminated r113 / lose 61 to 7.
Not fixed by any single switch back to default that I replayed (same 5,5 draw): QUEEN_NO_BLIND_PORTAL, POCKET_KEEP_OUT, TARGET_REACHABLE, HARVEST_PORTAL, POCKET_LOOP. All-off base and QUEEN_HERD / QUEEN_PORTAL_LAST / QUEEN_EXIT_KEEP arms still playing (machine slow). Start boxes whose portals open onto the field (ua_box_288/704) DO get left (first eat r20 / r6), so it is the "exit lands in a small closed room" case only. Map: ~/meow-redteam/maps/un2/ua_chain_448.map. Full report by 14:15.

---

## 2026-10-09 05:11:53 — unA-opus final: RED chain start box, box_288 by criterion

RED: small portal maps, start box whose only exit is a portal into a small closed room -> side never leaves and starves (ua_chain_448); constant = one of the one17 switches but NOT any single one of the 9 I replayed.
Scope: 8 new maps made (9 files), 7 played (22 games); ua_many_512 NOT played (my first file had an illegal horizontal/vertical pair, fixed, no time); the 6 baseline maps (ladder_portals_1, ladder_stripes_1, un_*) NOT run, machine got slow (one 87-round game took 309 s). Not measured: loop share, queen portal steps. No crash/timeout markers in any engine.log [M].

[M] per game, OUR side (opp): first eat | pearls r100 | dragons r100 | our queen | result
ua_r1_200   v3b s0  8 | 43 (9)    | 21 (0)  | alive            | win elim r58
ua_r1_200   v3b s1  14 | 41 (10)  | 14 (0)  | r22 mutual ram   | win elim r51
ua_r4_384   v3b s0  11 | 199 (47) | 46 (0)  | r30 rammed       | win elim r79
ua_r4_384   v3b s1  5 | 238 (64)  | 51 (0)  | r46 rammed       | win elim r86
ua_r9_600   v3b s0  7 | 481 (170) | 61 (0)  | r94 mate body f2 | win elim r98
ua_r9_600   v3b s1  5 | 479 (106) | 61 (2)  | alive            | win elim r119
ua_mix_900  v3b s0  7 | 463 (228) | 60 (19) | alive L9         | win elim
ua_mix_900  v3b s1  7 | 468 (146) | 61 (3)  | r61 rammed       | win elim
ua_single_750 v3b s0/s1  4 | 448/498 (340/323) | 64/60 (60/61) | alive, end L133/140 | win queen
ua_box_704  v3b s0  6 | 249 (388) | 9 (61)  | r82 rams         | LOSS elim r121
ua_box_704  v3b s1  6 | 483 (183) | 60 (6)  | alive            | win elim
ua_box_288  v3b s0  20 | 31 (124) | 0 (38)  | r44 rammed f2    | LOSS elim r68   <- RED by the dragon rule
ua_box_288  v3b s1  20 | 118 (196)| 1 (34)  | r44 rammed f2    | LOSS elim r101  <- RED by the dragon rule
ua_chain_448 v3b s0  87 | 1 (283) | 1 (60)  | r113 rammed      | LOSS elim       <- RED
ua_chain_448 v3b s1 111 | 0 (287) | 2 (60)  | r107 rammed f0   | LOSS 61 to 7    <- RED
ua_chain_448 mirror  never | 0 (0) | 2 (2)  | alive L3         | draw 5,5 at r500 <- RED both seats
Mirrors on r1/r4/r9/mix/box: decided by rams and elimination, no self-inflicted queen death before r50 (r4_384 mirror: queens ram each other r11).

Answers to your three questions:
1. Queen into a closed room and boxed: NOT seen. No queen death by wall / own body / mate before r50 on any map, 600 cells or less or above [M].
2. Refusing the only way to food: YES, but it is the whole side, not QUEEN_NO_BLIND_PORTAL. ua_chain_448 = 5x3 start box, no pearls inside, east edge is a portal into a closed 3x3 pearl room, that room's portal into a second one, then the field. Boards r60 (mirror game): queen at (4,2), short dragon at (2,3), both circling in the box for 500 rounds; pearls in view all at "99 steps". m3base and the all-off base (ua_off v mD17: 181 to 7) leave at once (first eat r5).
   Single switch set back to default, same game replayed, still the 5,5 draw [M]: QUEEN_NO_BLIND_PORTAL, POCKET_KEEP_OUT, TARGET_REACHABLE, HARVEST_PORTAL, POCKET_LOOP, QUEEN_HERD, QUEEN_PORTAL_LAST, QUEEN_EXIT_KEEP, EAT_FIRST. So it needs two switches together or one I did not try (untested: QUEEN_EXIT_STRICT, QUEEN_CORRIDOR_GUARD, REACH_EATS, ZONE_NEARER, SPAWN_CLEAR, QS_*). [C] the portal step is scored in score_portal_step, one17 main.cpp 7881-7912; POCKET_PORTAL_BAN is false (line 221) so 5398 is not it. Cause not located [E].
   Start boxes whose portals open on the field (ua_box_288/704) are left normally (first eat r20 / r6).
3. Short dragons dying in pockets: not a RED, but watch: on ua_r9_600 our deaths before r100 are wall 26, mate body 27, own body 18 (opp 6/4/6) while we still out-eat 481 to 170. I did not split feeder deaths from room deaths.
ua_box_288 RED is a fight loss, not a rule misfire [E]: our queen L5 is rammed at r44 in the open field with 3 enemy heads in her 7x7 (board r43, head (23,0)); QUEEN_NO_BLIND_PORTAL and POCKET_KEEP_OUT back to default give the identical game (elim r69). No constant.
What would show the chain RED is wrong: it is one hand-made map, one seed; a start with no pearl in view and a room-only exit may be rare. Files: ROOT/data/codex/astra/unA-opus/ (gen_ua.py, health.py, arm_test.py), maps ~/meow-redteam/maps/un2/ua_*.map, runs solo/runs/ua_m3base, ua_mirror, ua_arm_*.

---

## 2026-10-09 05:11:53 — closing summary

RED: on small portal maps, a start box whose only exit is a portal into a small closed room is never left, and the side starves (`ua_chain_448`). The all-off base leaves that box at once, so a one17 switch causes it, but none of the nine single switches I set back to default removes it.

**Coverage (stopped at 14:11 KST)**
- I made 9 maps (one more than asked) and played 7 of them: both seats against m3base on all 7, the mirror on 6 (the `ua_single_750` mirror was stopped), plus the single-switch replays.
- `ua_many_512` (the 8-pair map) was not played: my first file paired a horizontal edge with a vertical one, the engine refused it, and the fixed file had no time left.
- The six baseline maps (`ladder_portals_1`, `ladder_stripes_1`, the four `un_*`) were not run; the machine slowed badly (one 87-round game took 309 s).
- Not measured: loop share and queen portal steps.
- No crash, timeout or illegal-action markers in any `engine.log`.

**Per game, our side (opponent in brackets)**

| Map, seat | First eat | Pearls r100 | Dragons r100 | Our queen | Result |
|---|---|---|---|---|---|
| `ua_r1_200` s0 | 8 | 43 (9) | 21 (0) | alive | win, elim r58 |
| `ua_r1_200` s1 | 14 | 41 (10) | 14 (0) | r22 mutual ram | win, elim r51 |
| `ua_r4_384` s0 | 11 | 199 (47) | 46 (0) | r30 rammed | win, elim r79 |
| `ua_r4_384` s1 | 5 | 238 (64) | 51 (0) | r46 rammed | win, elim r86 |
| `ua_r9_600` s0 | 7 | 481 (170) | 61 (0) | r94 mate body | win, elim r98 |
| `ua_r9_600` s1 | 5 | 479 (106) | 61 (2) | alive | win, elim r119 |
| `ua_mix_900` s0 | 7 | 463 (228) | 60 (19) | alive, L9 | win, elim |
| `ua_mix_900` s1 | 7 | 468 (146) | 61 (3) | r61 rammed | win, elim |
| `ua_single_750` s0 / s1 | 4 / 4 | 448 / 498 (340 / 323) | 64 / 60 (60 / 61) | alive, end L133 / L140 | win on queen |
| `ua_box_704` s0 | 6 | 249 (388) | 9 (61) | r82, died ramming | loss, elim r121 |
| `ua_box_704` s1 | 6 | 483 (183) | 60 (6) | alive | win, elim |
| `ua_box_288` s0 | 20 | 31 (124) | 0 (38) | r44 rammed | **loss, elim r68 (RED)** |
| `ua_box_288` s1 | 20 | 118 (196) | 1 (34) | r44 rammed | **loss, elim r101 (RED)** |
| `ua_chain_448` s0 | 87 | 1 (283) | 1 (60) | r113 rammed | **loss, elim (RED)** |
| `ua_chain_448` s1 | 111 | 0 (287) | 2 (60) | r107 rammed | **loss, 61 to 7 (RED)** |
| `ua_chain_448` mirror | never | 0 (0) | 2 (2) | alive, L3 | **draw 5,5 at r500 (RED)** |

The other mirrors (r1, r4, r9, mix, both box maps) were decided by rams and elimination, with no self-inflicted queen death before r50.

**Your three questions**
1. **Queen walking into a closed room and dying boxed:** not seen. No queen death by wall, own body or mate before r50 on any map, on either side of 600 cells.
2. **Refusing the only portal to food:** yes, but it is the whole side, and `QUEEN_NO_BLIND_PORTAL` is not the cause.
   - **Map:** `ua_chain_448` has a 5x3 start box with no pearls, whose east edge is a portal into a closed 3x3 pearl room, then a second room, then the field.
   - **Behaviour:** in the mirror game at r60 the queen is at (4,2) and the short dragon at (2,3); neither side eats a pearl in 500 rounds, and the pearls in view show no free path. Seat s0 against m3base is equally bad from round 0 (0 pearls by r50).
   - **Contrast:** m3base leaves at once (first eat r5), and the all-off base beats mD17 on this map 181 to 7.
   - **Switches ruled out:** the same game replayed with one switch back to default still ends 5,5 for each of `QUEEN_NO_BLIND_PORTAL`, `POCKET_KEEP_OUT`, `TARGET_REACHABLE`, `HARVEST_PORTAL`, `POCKET_LOOP`, `QUEEN_HERD`, `QUEEN_PORTAL_LAST`, `QUEEN_EXIT_KEEP`, `EAT_FIRST`.
   - **Still open:** it needs two switches together or one I did not try (`QUEEN_EXIT_STRICT`, `QUEEN_CORRIDOR_GUARD`, `REACH_EATS`, `ZONE_NEARER`, `SPAWN_CLEAR`, the `QS_*` group). The portal step is scored in `score_portal_step` (one17 `main.cpp` 7881-7912); `POCKET_PORTAL_BAN` is false (line 221), so that branch is not it. I did not locate the cause.
   - **Not affected:** start boxe
[result truncated — ask the agent for the rest via SendMessage]

---

## 2026-10-09 05:17:28 — Chain RED: QUEEN_DEAD_ALL off removes it (one map so far)

unA-opus: the start-box RED on ua_chain_448 has a one-constant remedy, replayed: QUEEN_DEAD_ALL back to false -> the arm leaves the box and eliminates mD17 at r161 (228 to 0); one17 itself = 0 pearls in 500 rounds. Still ONE map (448 cells); repeat maps (320, 660, 720 cells) are playing now, verdict in ~5 min.
How I got there [M]: all-off base leaves; first 22 switches alone = stuck, switches 11-21 alone = stuck; minus-one over those: only QUEEN_DEAD_ALL frees it (FEEDER_EAT, QW_END_ROOM, LUNGE_PEARL, TRADE_SHORT_BY, ATTACK_MIN_UNITS, FEED_CAP_ROUND, HEADING_TIE pair, EAT_FIRST, QUEEN_EXIT_KEEP do not). [C] one17 main.cpp 5686-5687: dead_queen() = real_queen() on every size with the switch, else is_queen() which is false at 600 cells or fewer (5682); it feeds the dead-end terms at 4821, 7675-7683 (room < 3*length+8 without reaching the tail = dead end). Caveat [E]: above 600 cells is_queen() is true anyway, so the switch cannot be the remedy there; I am testing 660 and 720 to see whether the same stall exists above the threshold with the switch irrelevant. Bot: ~/meow-redteam/solo/bots/ua_m20.

---

## 2026-10-09 05:17:28 — RED repeats on 2 maps; QUEEN_DEAD_ALL false removes the stall

unA-opus: RED now repeats on two maps of 600 cells or fewer, remedy replayed on both: QUEEN_DEAD_ALL false. Start box whose only exit is a portal into a small closed room, v m3base seat A, same seed [M]:
map            | one17 first eat, pearls r25/50/100 | QUEEN_DEAD_ALL off (bots/ua_m20)
ua_chain_448   | r87, 0/0/1 (mirror: never, 500 rounds) | leaves, beats mD17 228 to 0 (v m3base still playing)
ua_chain1_320  | r86, 0/0/8                             | r13, 4/8/24
Limits: (1) on ua_chain1_320 the arm leaves the box but still loses to m3base by elimination at r95 (one17 loses at r183), so the switch removes the stall, not the loss. (2) Above 600 cells the switch changes nothing (ua_chain1_660: identical game, one17 first eats at r54 and still wins 321 to 3 because m3base sits until r134). (3) Not yet checked: what QUEEN_DEAD_ALL off costs on ordinary small maps; I am playing ua_m20 v m3base on my room maps and ladder_stripes_1 / ladder_portals_1 next, result by 14:30.

---

## 2026-10-09 05:26:18 — Second stall: QUEEN_NO_BLIND_PORTAL starves the side in a blind-exit start box

unA-opus: second stall, and this one IS today's switch: on ua_boxnp_320 (20x16, start box with no pearl inside, single exit = a portal whose far end is out of view) one17 sits with both dragons, 0 pearls to r50, first eat r52, eliminated r55 by m3base; QUEEN_NO_BLIND_PORTAL off (bots/ua_nbp), same game: first eat r7, 262 pearls and 44 dragons at r100, wins by elimination r100. QUEEN_DEAD_ALL off does nothing there (identical game). So with 2 starters the queen is the only one that scouts a blind portal; the short starter does not go either [M], reason not located.
Summary of the two start-box stalls at 600 cells or fewer [M]: exit lands in a small closed room in view (ua_chain_448, ua_chain1_320, ua_chain1p_320) -> QUEEN_DEAD_ALL false frees it (not QUEEN_NO_BLIND_PORTAL); exit lands out of view (ua_boxnp_320) -> QUEEN_NO_BLIND_PORTAL false frees it (not QUEEN_DEAD_ALL). Cost seen for QUEEN_DEAD_ALL off: on ua_chain_448 the queen dies boxed by two mates inside the 3x3 room at r36 (0 free cells), game still won 246 to 0 v m3base. On ladder_stripes_1 and ladder_portals_1 v m3base seat A, QUEEN_DEAD_ALL off was better (queen alive at the end on both; one17 queen rammed r83 / dead on a wall with 0 free cells r115); on ua_r1/r4/r9/box_288/many_512 identical games. Checking the other small ladder maps now.

---

## 2026-10-09 05:30:44 — unA-opus final report: two start-box stalls, remedies replayed both seats

RED: small portal maps (600 cells or fewer), start box whose only exit is a portal -> the side sits and starves; two causes, each with ONE constant replayed in both seats: QUEEN_DEAD_ALL false (exit into a small closed room) and QUEEN_NO_BLIND_PORTAL false (exit out of view).
Played: 13 ua maps + 2 ladder + 4 copied un maps, about 110 games, seed 1. No crash/timeout markers anywhere [M]. Not measured: loop share, queen portal steps. All numbers below [M], our side v m3base, seat A / seat B.

A. Exit lands in a closed 2x2 or 3x3 pearl room that is in view (first eat; pearls r100; result)
map             | one17                                   | QUEEN_DEAD_ALL false (bots/ua_m20)
ua_chain_448    | r87 / r111; 1 / 0; loss / loss (mirror: 0 pearls in 500 rounds) | r5 / r5; 324 / 319; WIN elim / WIN elim
ua_chain1_320   | r86 / never; 8 / 0; loss / loss         | r13 / r13; 24 / 244; loss r95 / WIN elim
ua_chain1p_320  | r69 / r90; 3 / 6; loss / loss           | r17 / r17; 55 / 20; loss / loss
one17 0 wins of 6 and stalled in 6 of 6; arm leaves in 6 of 6, wins 3. QUEEN_NO_BLIND_PORTAL off does NOT free these (chain_448, chain1_320 replayed).
Found by bisection: all-off leaves; switches 11-21 alone stall; minus-one over them, only QUEEN_DEAD_ALL frees. [C] one17 main.cpp 5686-5687 dead_queen() = real_queen() on every size (else is_queen(), false at <=600, line 5682), used by the dead-end terms 4821 and 7675-7683.
Cost of the remedy: on ua_chain_448 the arm's queen dies inside the 3x3 room boxed by mates (r36 mate body, 0 free cells; seat B r33 mate head) - games still won.
Elsewhere with QUEEN_DEAD_ALL false: identical games on every portal-less small map tried (devil, tower_defense, weakhold, gx_rooms_24x12, queen600_1/2) and on ua_r1/r4/r9/box_288/many_512, and above 600 cells (chain1_660, chain_720: no-op, as the code says). It changes only ladder_stripes_1 and ladder_portals_1: v m3base seat A better on both (queen alive at the end; one17 queen rammed r83 / dead on a wall r115); head to head v mD17: stripes arm wins both seats, portals arm LOSES both seats (its queen dies r291 on a mate head, r396 on a wall with 0 free). So mixed on the one ladder map where it matters; I do not know which loss QUEEN_DEAD_ALL was added for.

B. Exit lands out of view, no pearl bed in the box (ua_boxnp_320)
one17: first eat r52 / r47, 1 / 1 pearls r100, eliminated r55 / r56. QUEEN_NO_BLIND_PORTAL false (bots/ua_nbp): first eat r7 / r7, 262 / 210 pearls, wins by elimination both seats. QUEEN_DEAD_ALL false: identical to one17. So today's switch does starve the side when the blind portal is the only way out: with two starters the short one does not scout it either (cause not located). ua_box_288/704 (two exits, one slow pearl bed in the box) do get out (first eat r20 / r6); I cannot say which difference matters.
Above 600 cells the same boxes only delay us: first eat r54 (chain1_660), r44 (chain_720), still won because m3base sits until r134 / r113.

Your three questions: (1) queen walking into a closed room and dying boxed: not seen with one17 on any map (no queen death by wall/own/mate before r50); it comes back on ua_chain_448 if QUEEN_DEAD_ALL is turned off. (2) refusing the only portal to food: yes, sections A and B. (3) short dragons dying in pockets: no RED; ua_r9_600 has wall 26 / mate 27 / own 18 deaths before r100 against 6/4/6 but out-eats 481 to 170, feeder deaths not separated.
Other: ua_box_288 lost both seats to m3base (0 and 1 dragons at r100 v 38 and 34), a fight loss in the open, identical with either switch off. ua_cp_queen600_1 (plain 24x25) lost by elimination in both seats to m3base while 24x26 is won in both; NOT QUEEN_MIN_CELLS (599 and 624 arms identical) and not QS_SHED_MAX; single games, open-field fights, I would not act on it. ua_cp_portalonly_1 lost 105 to 73 on longest dragon, both queens dead (ours r56 on a foe body). ua_cp_portalid_1: m3base dies at round 0, we survive.
What would show this wrong: hand-made maps, one seed; a start with no other way out than a portal may never appear in the qualifier. My read: B is a real hole in today's switch but turning it off brings back the 30-of-30 deaths, so no constant there; A's constant is cheap on the maps I could test but loses the portals head to head, so only take it if the reason QUEEN_DEAD_ALL went in is weaker than a 0-pearl stall.
Files: ROOT/data/codex/astra/unA-opus/ (gen_ua.py, gen_ua2.py, health.py, h2.py, pair_test.py, sub.py); maps ~/meow-redteam/maps/un2/ua_*.map; runs ~/meow-redteam/solo/runs/ua_m3base, ua_mirror, ua_arm_*; arms solo/bots/ua_m20, ua_nbp.

---

## 2026-10-09 05:30:44 — closing summary

RED: on portal maps of 600 cells or fewer, a start box whose only exit is a portal makes the whole side sit and starve. There are two causes, and for each I replayed a one-constant remedy in both seats; the full report went to the lead at about 14:28 KST.

All games are seed 1 against m3base unless stated. No crash or timeout markers appeared in any `engine.log`. Loop share and queen portal steps were not measured.

**A. Exit lands in a small closed pearl room that is in view**

| Map | one17 (seat A / seat B) | `QUEEN_DEAD_ALL` false (seat A / seat B) |
|---|---|---|
| `ua_chain_448` | first eat r87 / r111, loss / loss; mirror: 0 pearls in 500 rounds | first eat r5 / r5, win / win by elimination |
| `ua_chain1_320` | first eat r86 / never, loss / loss | first eat r13 / r13, loss r95 / win by elimination |
| `ua_chain1p_320` | first eat r69 / r90, loss / loss | first eat r17 / r17, loss / loss |

- **Result:** one17 stalls in 6 of 6 and wins none; the arm leaves in 6 of 6 and wins 3.
- **How it was found:** the all-off base leaves the box; switches 11-21 alone stall; removing them one at a time, only `QUEEN_DEAD_ALL` frees it. `QUEEN_NO_BLIND_PORTAL` off does not.
- **Code:** `dead_queen()` at one17 `main.cpp` 5686-5687 applies the dead-end terms (4821, 7675-7683) to the queen on every board size.
- **Cost:** on `ua_chain_448` the arm's queen dies inside the 3x3 room, boxed by mates (r36 with 0 free cells; r33 in seat B). Both games were still won.
- **Effect elsewhere:**
  - Results are identical on every portal-less small map tried and on the 660- and 720-cell chain maps.
  - On `ladder_stripes_1` it is better against m3base and wins both seats head to head against mD17.
  - On `ladder_portals_1` it is better against m3base in seat A but loses both seats head to head against mD17.

**B. Exit lands out of view, no pearl bed in the box (`ua_boxnp_320`)**

- **one17:** first eat r52 / r47, eliminated r55 / r56.
- **`QUEEN_NO_BLIND_PORTAL` false:** first eat r7 in both seats, wins both by elimination. `QUEEN_DEAD_ALL` false changes nothing here.
- **Meaning:** today's switch starves the side when the blind portal is the only way out. With two starters the short one does not scout it either; I did not find why.
- **Not affected:** `ua_box_288` and `ua_box_704` (two exits, one slow pearl bed in the box) do get out. I cannot say which difference matters.

Above 600 cells the same boxes only delay us (first eat r54 and r44), and those games were still won.

**The lead's three questions**
1. **Queen walking into a closed room and dying boxed:** not seen with one17 on any map. It comes back on `ua_chain_448` if `QUEEN_DEAD_ALL` is turned off.
2. **Refusing the only portal to food:** yes, both A and B.
3. **Short dragons dying in pockets:** no RED. `ua_r9_600` has many wall, mate-body and own-body deaths before r100, but we still out-eat m3base 481 to 170; I did not separate feeder deaths.

**Other observations**
- `ua_box_288` is lost in both seats to m3base (0 and 1 dragons at r100 against 38 and 34). It looks like a fight loss in the open; the game is identical with `QUEEN_NO_BLIND_PORTAL` or `QUEEN_DEAD_ALL` off.
- The plain 24x25 map (`un_queen600_1`) is lost by elimination in both seats while 24x26 is won in both. It is not `QUEEN_MIN_CELLS` and not `QS_SHED_MAX`; these are single open-field games and I would not act on them.
- `un_portalonly_1` is lost on longest dragon, 105 to 73 (seat A).
- The four `un_*` baseline maps had to be copied into `~/meow-redteam/maps/un2/` as `ua_cp_*` because the engine refuses maps outside its workspace.

My read: B is a real hole in today's switch, but turning it off brings back the queen deaths it was added for, so there is no constant to take. A's constant is cheap on everything I could test except the `ladder_portals_1` head to head. It is worth taking only if the reason `QUEEN_DEAD_ALL` went in matters less than a 0-pearl stall. These are hand-made maps on one seed, and a start with no way o
[result truncated — ask the agent for the rest via SendMessage]

---

## 2026-10-09 05:30:44 — Bisect landed on one18 too: QUEEN_DEAD_ALL, cost table on 3 ladder maps

unA-opus: bisect is done and holds on one18: the smallest set whose removal frees the side is ONE constant, QUEEN_DEAD_ALL (true -> false). mD18 shows the same lock-in as mD17. Arm = one18 minus QUEEN_DEAD_ALL: ~/meow-redteam/solo/bots/ua_18m. All [M], v m3base, seed 1.

Lock-in maps (first eat | pearls r25/50/100 | dragons r25/50/100 | our queen | result)
ua_chain_448  seat 0  mD18   r87  | 0/0/1      | 2/2/1   | r113 rammed   | loss elim r113
ua_chain_448  seat 0  ua_18m r5   | 27/62/341  | 4/8/60  | r116 wall f0  | WIN 127 to 7 (longest)
ua_chain_448  seat 1  mD18   r111 | 0/0/0      | 2/2/2   | r107 rammed   | loss 61 to 7
ua_chain_448  seat 1  ua_18m r5   | 25/73/319  | 5/11/37 | r33 mate head | WIN elim r223
ua_chain1_320 seat 0  mD18   r86  | 0/0/8      | 2/2/3   | r86 rams      | loss elim r183
ua_chain1_320 seat 0  ua_18m r13  | 4/8/24     | 4/3/0   | r95 rammed    | loss elim r95
ua_chain1_320 seat 1  mD18   never| 0/0/0      | 2/2/0   | r100 rams     | loss elim r100
ua_chain1_320 seat 1  ua_18m r13  | 4/31/244   | 3/11/60 | alive L3      | WIN elim r111

What removing it costs, seat 0 v m3base (pearls r100 | dragons r100 | queen | result)
ladder_portals_1          mD18   190 | 15 | dead r115 on a wall, 0 free | win, longest dragon 28 to 22
ladder_portals_1          ua_18m 190 | 15 | alive, L5 at the end        | win, longer queen 5 to 0
ladder_stripes_1          mD18   63  | 9  | rammed r83                  | win elim r253
ladder_stripes_1          ua_18m 90  | 19 | alive                       | win elim r102
ladder_queen_of_spades_1  mD18   52  | 17 | alive L3                    | win elim r243
ladder_queen_of_spades_1  ua_18m 52  | 17 | alive L3                    | win elim r243 (identical: 875 cells, switch is a no-op above 600)
So on these three it costs nothing and is better on two. The one thing against it that I measured (one17 build, head to head v mD17 on ladder_portals_1): the arm lost both seats, its queen dying r291 on a mate head and r396 on a wall with 0 free cells; on ladder_stripes_1 it won both seats. And the remedy's own risk: on ua_chain_448 the freed queen dies in or near the small room (r33 mate head, r116 wall with 0 free) though both games are won on dragons.

The code line [C] (one17 main.cpp; one18 not re-read): 5686-5687 dead_queen() = QUEEN_DEAD_ALL ? real_queen() : is_queen(), and is_queen() (5682) is false at 600 cells or fewer unless home_closed. With the switch on, score_step 7679-7682 subtracts QUEEN_DEAD_PENALTY from every step of the queen that is a dead end or short of room (dead end = 4821: room < 3*length + 8 without reaching the tail), and 7683-7690 subtracts more when known_room < length + 2. [E] In a 15-cell box with a 4- or 9-cell room behind the portal every destination is "dead end" for a length-3 queen (needs 17), so the portal step never outscores circling. Why the short starter stays with her I did not locate.
Not done: ua_18m on seeds other than 1, online opponents, and the reason QUEEN_DEAD_ALL was switched on in the first place. The blind-exit box (ua_boxnp_320) is a separate lock-in that this arm does not fix; only QUEEN_NO_BLIND_PORTAL false does.

---

## 2026-10-09 05:30:44 — closing summary

The bisect lands on one constant: turning `QUEEN_DEAD_ALL` off frees the side, and this holds on one18 as well as one17. The lead has the full tables (sent about 14:30 KST).

mD18 shows the same lock-in as mD17. The arm is one18 minus `QUEEN_DEAD_ALL`, built as `~/meow-redteam/solo/bots/ua_18m`. All games are against m3base, seed 1.

**Lock-in maps**

| Map, seat | Bot | First eat | Pearls r100 | Dragons r100 | Our queen | Result |
|---|---|---|---|---|---|---|
| `ua_chain_448`, 0 | mD18 | r87 | 1 | 1 | r113 rammed | loss, elim r113 |
| `ua_chain_448`, 0 | `ua_18m` | r5 | 341 | 60 | r116 wall, 0 free | win, 127 to 7 |
| `ua_chain_448`, 1 | mD18 | r111 | 0 | 2 | r107 rammed | loss, 61 to 7 |
| `ua_chain_448`, 1 | `ua_18m` | r5 | 319 | 37 | r33 mate head | win, elim r223 |
| `ua_chain1_320`, 0 | mD18 | r86 | 8 | 3 | r86, died ramming | loss, elim r183 |
| `ua_chain1_320`, 0 | `ua_18m` | r13 | 24 | 0 | r95 rammed | loss, elim r95 |
| `ua_chain1_320`, 1 | mD18 | never | 0 | 0 | r100, died ramming | loss, elim r100 |
| `ua_chain1_320`, 1 | `ua_18m` | r13 | 244 | 60 | alive | win, elim r111 |

**What removing it costs (seat 0)**

| Map | Bot | Pearls r100 | Dragons r100 | Queen | Result |
|---|---|---|---|---|---|
| `ladder_portals_1` | mD18 | 190 | 15 | dead r115 on a wall | win, longest dragon 28 to 22 |
| `ladder_portals_1` | `ua_18m` | 190 | 15 | alive, L5 | win, longer queen 5 to 0 |
| `ladder_stripes_1` | mD18 | 63 | 9 | rammed r83 | win, elim r253 |
| `ladder_stripes_1` | `ua_18m` | 90 | 19 | alive | win, elim r102 |
| `ladder_queen_of_spades_1` | mD18 | 52 | 17 | alive | win, elim r243 |
| `ladder_queen_of_spades_1` | `ua_18m` | 52 | 17 | alive | identical game |

On these three it costs nothing and is better on two. Two things count against it:
- **Head to head on `ladder_portals_1`:** the one17-based arm lost both seats against mD17, with its queen dying late (r291 on a mate head, r396 on a wall). On `ladder_stripes_1` it won both seats.
- **The freed queen still dies:** on `ua_chain_448` she dies on a mate head at r33 (seat 1) or on a wall with no free cells at r116 (seat 0), though both games are won on dragons.

**Code:** in one17 `main.cpp`, `dead_queen()` (5686-5687) becomes true for the queen on every board size when the switch is on. `score_step` (7679-7690) then penalises every queen step that is a dead end or short of room. My inference is that in a 15-cell box with a 4- or 9-cell room behind the portal, every destination counts as a dead end for a length-3 queen, so the portal never outscores circling. I did not find why the short starter stays with her.

Not done: seeds other than 1, online opponents, and the reason `QUEEN_DEAD_ALL` was switched on originally. The blind-exit box (`ua_boxnp_320`) is a separate lock-in that this arm does not fix; only `QUEEN_NO_BLIND_PORTAL` off does.

Scripts and logs are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unA-opus/`.
