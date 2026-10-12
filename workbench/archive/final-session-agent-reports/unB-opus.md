# Reports sent to the lead by unB-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:00:59 — Heads-up: start-room RED, QUEEN_EXIT_STRICT candidate

unB-opus heads-up, RED on enclosed start rooms (2 maps, 1 game each so far, seat A vs m3base): on ub_room3 (24x12, 3x3 room, 3-long exit) mD17's second starter dies on its own body at r1, the queen circles the room 57 rounds, 1 eat, eliminated r61 (m3base leaves r24, 17 eats by r50); the same game with only QUEEN_EXIT_STRICT off leaves at r18, 22 eats by r50 and wins by elimination r56, BUT the queen walks into a wall at r2 in that arm, so it is not a clean fix. POCKET_KEEP_OUT off and QUEEN_CORRIDOR_GUARD off change nothing there (same numbers as one17).
Second, not a one17 regression: on ub_room8o (46x22 = 1012 cells, 4x4 room, 8-long exit) neither mD17 nor m3base ever leaves the room in 500 rounds (0 eats, draw 4-4), while the same design at 968 cells (ub_room8u) both leave at r22-26, so the centre pull is what gets them out; arms on tworooms / other seat / CENTER_MAX_CELLS are running, report by 14:15.

---

## 2026-10-09 05:11:53 — CENTER_MAX_CELLS removes the never-leave RED

unB-opus: one constant removes the "never leaves the start room" RED above 1000 cells. ub_room8o (46x22 = 1012 cells, 4x4 start room, 8-long one-wide exit, no pearl in sight), seat A vs m3base, seed 7: one17 = 0 eats, 2 dragons, both starters in the room for all 500 rounds (same in the mirror and from seat B; m3base does it too); the same game with only CENTER_MAX_CELLS:100000 = starter out at r26, first eat r32, 107 eats and 44 dragons by r100, win by elimination r132 (bot ub_cmax, runs/ub_a_ub_cmax). Code: main.cpp:612 center_map = cells <= CENTER_MAX_CELLS && (long_map || cells <= CENTER_SMALL_CELLS), used at 7760-7763.
NOT checked yet: what it does to pearls on ladder/gx maps over 1000 cells (it changes the first 30-60 rounds wherever no pearl is known and length <= 4), and non-long maps of 700-1000 cells are still excluded by CENTER_SMALL_CELLS. QUEEN_EXIT_STRICT off is replay-number-identical on ladder Tower Defense and Stripes (seat A, seed 7) and fixes ub_room3 from both seats, but does nothing on room8o, room20 or tworooms. I am starting cmax vs one17 on ladder maps over 1000 cells now.

---

## 2026-10-09 05:14:22 — unB-opus final report: start-room RED

RED: enclosed start rooms with a one-wide exit, the starters (above all the queen) do not leave the room; CENTER_MAX_CELLS (1000 -> no cap) removes it above 1000 cells, QUEEN_EXIT_STRICT off removes the 3x3-room case, no constant found for room20 / tworooms.
9 new maps in ~/meow-redteam/maps/un2/ub_*.map, seed 7, ONE game per cell (seat A, seat B vs m3base; mirror). us/them. Markers crash|timeout|illegal in engine.log: 0 in every game. [M] unless marked.
map (cells)        | first eat | eats r25/50/100      | dragons r25/50/100 | loop | result
ub_room3 (288) A   | 3 / 5     | 1/1/1 vs 1/17/19     | 1/1/0 vs 1/8/8     | 44%  | eliminated r61  RED
ub_room3 B         | 3 / 5     | 1/1/1 vs 2/19/22     | 1/1/0 vs 2/9/10    | 36%  | eliminated r53  RED
ub_room3 mirror    | 3 / 3     | 1/1/1 both           | 1/1/1 both         | 93%  | draw 3-3 at r500, nobody ever left
ub_room8u (968) A/B| 32/28, 28/38 | 0/14/92 vs 0/13/85; 0/15/115 vs 0/6/25 | 2/8/13 vs 2/8/10; 2/8/42 vs 2/5/2 | 3-4% | won both (elim)  GREEN
ub_room8o (1012)   | none      | 0/0/0 both, A, B and mirror | 2/2/2        | 93%  | draw 4-4 at r500  RED (m3base does the same)
ub_room20 (640) A  | 61 / 45   | 0/0/1 vs 0/2/22      | 2/2/1 vs 2/3/10    | 40%  | eliminated r102  RED
ub_room20 B        | 45 / 37   | 0/2/3 vs 0/5/24      | 2/3/0 vs 2/4/8     | 40%  | eliminated r98   RED
ub_tworooms (396) A,B | 25 / 23 | 0/3/4 vs 1/16/41    | 2/2/0 vs 2/5/4     | 2-10%| eliminated r74 both seats  RED (mirror normal)
ub_comb (600) A,B,mirror | none | 0 both              | 0 by r25           | 0%   | both queens dead r7 on own body, all dead r16, draw  RED (m3base same)
ub_spiral (578) A  | 18 / 18   | 2/19/96 vs 2/21/82   | 2/6/12 vs 2/4/10   | 0%   | won on longest 34-16; our queen dead r26 own body, theirs r19  RED by rule (both bots)
ub_maze (693) A    | 17 / 17   | 2/14/96 vs 2/15/51   | 1/5/17 vs 1/5/2    | 0%   | won by elimination r110  GREEN (queen death r0 = my start placement, ignore)
ub_deadend (480)   | none      | 0 both, 500 rounds   | 2/2/2              | 92% A, 1% B | draw 4-4, degenerate map
Your questions. Dead-end pearls: one-cell pockets are refused forever by both bots (0 eats in 500 rounds, correct, entering is death); deep teeth are NOT refused: both queens enter the first 6-deep tooth at r1 and die at r7 on their own body (comb, 3 of 3 games), and in the maze we lose 15 dragons to walls + 5 to own body before r100 (m3base 13 + 4). Queen in one-wide dead ends: yes, comb r7 and spiral r26; old main does the same, so no one17 constant. Centre pull: helps, it is the only thing that gets a starter out when no pearl is in sight: the same room design leaves at r22-26 at 968 cells and never at 1012.
Evidence 1, ub_room3 [M+C]: r1 our second starter head (3,5) tail (2,5), queen head (3,7) tail (2,7); its only non-wall step is (3,6), the queen's only free neighbour, so keep_queen_exit(strict) finds no move that keeps a queen exit and steps onto its own tail (main.cpp 1356-1376, "QSTRICT die"). r20: queen length 3 on (3,5),(3,6),(2,6) circling the 2x2 block, exit (4,6) free, never taken in 60 rounds (500 in the mirror). With only QUEEN_EXIT_STRICT off (bot ub_nostrict): a starter is out at r18, eats by r50 = 22 (A) / 16 (B), wins by elimination r56 / r59, BUT the queen dies at r2 (wall / own body) in both, so the win is by elimination only. Same numbers as one17 on ladder Tower Defense and Stripes (seat A). No effect on room8o, room20, tworooms. No change on room3 either from POCKET_KEEP_OUT, QUEEN_CORRIDOR_GUARD, QW_END_ROOM, QUEEN_HERD, QUEEN_FAR_HEADS, QUEEN_BOOT_LEN, POCKET_LOOP off.
Evidence 2, ub_room8o [M+C]: both starters circle the 4x4 room for 500 rounds; main.cpp:612 center_map needs cells <= CENTER_MAX_CELLS, pull applied at 7760-7763. Only CENTER_MAX_CELLS:100000 (bot ub_cmax): out r26, first eat r32, 107 eats and 44 dragons by r100, win by elimination r132. It touches only maps with width >= 2*height over 1000 cells [C]; on the three such ladder maps, seat A vs m3base, one game each, cmax vs one17: maze_1 eats by r100 90 vs 80, dragons 37 vs 29, queen alive 39 vs dead r80 on a wall; trauma_1 15 vs 3 eats, 6 vs 4 dragons, both lost on queen length; slithery_fight cmax 415 eats and a win, one17 game not finished when I stopped.
Evidence 3, ub_room20 / ub_tworooms: the non-queen enters the corridor at about r46 (room20) and r24 (tworooms), the queen stays in the room; m3base sends both. Seven arms (strict, pocket, corridor guard, end room, herd, far heads, boot len off) give the same numbers on room20: no constant.
Not done: queen free cells and portal steps (no portals on these maps), gx_corridors / gx_rooms baselines, seat B and mirror on maze and spiral, any second seed. My "left the room" counter is wrong for the 5x5 room; the round above is from the head trace. Folder: data/codex/astra/unB-opus/ (mk.py, health.py, arm.zsh); runs: solo/runs/ub_17, ub_mir, ub_a_*.

---

## 2026-10-09 05:14:22 — Slithery baseline for CENTER_MAX_CELLS check

unB-opus addendum, the missing baseline: ladder_slithery_fight_1 seat A vs m3base seed 7, CENTER_MAX_CELLS:100000 vs one17: eats r25/50/100 58/154/415 vs 76/167/398, dragons 24/37/60 vs 29/48/61, both win on queen length (38-0 vs 65-0). So on the three long ladder maps over 1000 cells the centre-pull arm is slower in the first 50 rounds on slithery (58 vs 76 eats by r25), ahead by r100 on all three; one game each, not enough to call it safe. All my games are finished, nothing of mine is running.

---

## 2026-10-09 05:14:22 — closing summary

RED: on maps with an enclosed start room and a one-wide exit, our starters (above all the queen) do not leave the room. The full report and an addendum went to team-lead by 14:13 KST.

All of this is one game per cell, seed 7, on 9 new maps; no crash, timeout or illegal-action markers in any engine log.

| Map (cells) | What happened to mD17 | Verdict |
|---|---|---|
| `ub_room3` (288) | Second starter kills itself at r1, queen circles the 3x3 room; eliminated r61 / r53; mirror is a 3-3 draw with nobody leaving in 500 rounds | RED |
| `ub_room8u` (968) | Leaves at r22-26, wins both seats | GREEN |
| `ub_room8o` (1012) | Never leaves in 500 rounds, 0 eats, draw; m3base does the same | RED |
| `ub_room20` (640) | Non-queen enters the corridor about r46, queen stays; 1 and 3 eats by r100 against 22 and 24; eliminated r102 / r98 | RED |
| `ub_tworooms` (396) | Queen stays in the room; 4 eats by r100 against 41; eliminated r74 from both seats | RED |
| `ub_comb` (600) | Both queens enter the first 6-deep tooth and die on their own body at r7; m3base does the same | RED |
| `ub_spiral` (578) | Our queen dies on her own body at r26 (m3base's at r19); we still win on longest dragon | RED by rule |
| `ub_maze` (693) | Wins by elimination r110 | GREEN |
| `ub_deadend` (480) | Nobody eats in 500 rounds; one-cell pockets are refused by both bots | degenerate map |

Constant candidates:

- **`CENTER_MAX_CELLS` (1000 → no cap):** this alone fixes `ub_room8o`: starter out at r26, 107 eats and 44 dragons by r100, win at r132. It only touches maps over 1000 cells with width at least twice the height. On the three such ladder maps (maze, trauma, slithery fight) it was ahead on eats by r100 in all three, but slower on slithery early (58 against 76 eats by r25). One game each is not enough to call it safe.
- **`QUEEN_EXIT_STRICT` off:** this fixes `ub_room3` from both seats (out at r18, wins by elimination), but the queen dies at r2 in that arm, so it is not a clean fix. The self-kill is at `main.cpp` 1356-1376: the mate's only step is the queen's only free neighbour, so it moves onto its own tail. Turning it off gives the same numbers as one17 on ladder Tower Defense and Stripes, and does nothing on `ub_room8o`, `ub_room20` or `ub_tworooms`.
- **No constant found** for `ub_room20`, `ub_tworooms`, or the queen dying in dead ends. Seven one-constant-off arms gave unchanged numbers on `ub_room20`, and three on `ub_tworooms`.

Not done: queen free cells and portal steps, the `gx_corridors` / `gx_rooms` baselines, seat B and mirror on maze and spiral, and any second seed. The "left the room" counter is wrong for the 5x5 room, so the r46 figure comes from the head trace.

Maps are in `~/meow-redteam/maps/un2/ub_*.map`, scripts in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unB-opus/`, and runs in `~/meow-redteam/solo/runs/ub_17`, `ub_mir` and `ub_a_*`. Nothing of mine is still running.
