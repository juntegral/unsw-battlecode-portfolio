# Reports sent to the lead by tiny-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 04:51:12 — tiny-opus heads-up: lead candidate, games stuck in queue

tiny-opus heads-up (13:51): lead candidate is TR_STALL_ROUNDS lower (4, maybe 1) on Tower Defense only; NOT verified on one17 yet, and Stripes is a different problem (first eat is already r3-r9 there, we lose dragons later), so the "both maps" bar will not be met by a start-room constant.
Blocker: engine/run_game.py lets only 2 games run machine-wide (flock slots in ~/meow-redteam/.locks) and about 16 games are queued; my 4 Tower Defense games (mD17, ST4, ST1, ST4+HEADING_TIE 12, seat 0 seed 7 vs m3base) have not started. I am not going around the lock. Hash checks done: all-off 92fb69564fbd, one17 build of my copy = d6d14e1f8f53 (binary identical to mD17, no source change).
[M] Tower Defense mechanism so far: start to centre tower is ~35 steps of corridor (opponents first eat r35-41 at (13,11)-(14,13)); our two starters orbit the room cell nearest the centre with a 12-round period until the stall release (TR_STALL_ROUNDS 12, lines 2826-2830, 5159-5161, 7763), leave at r21-24 locally (r14-41 online), first eat r64-73. With ST4 (early-opus game, one14 base) they leave at r9-12 and eat at r56.

---

## 2026-10-09 04:59:51 — tiny-opus: real cause on Tower Defense found, CRAMPED_EAT candidate

tiny-opus heads-up 2 (13:59): Tower Defense starvation is not mainly the start room; our dragons reach the tower door and refuse to step in. Candidate under test: CRAMPED_EAT:true (existing switch, line 74/7656), not ready yet.
[M] Online 1523625 r56: our queen L2 stands at (19,2), a pearl at (18,2) one free step away (born r19) and five more within 2-5 steps; she steps away to (19,1) and both starters pace x=19-20 beside the tower from r52 to r100 (one eat in 100 rounds). Same in 1528859 and 1525835. Local one17 game (TD seed 7 seat 0 vs m3base): queen at (12,13) r42, pearl at (13,13) one step, she walks off; first eat r62 elsewhere.
[C] All Tower Defense food sits in walled compartments of about 4-6 cells with one door. Queen: dead-end penalty 6000 when room < 3*length+8 or avail < length+8 (lines 4820-4821, 7674-7689), no constant relaxes it short of QUEEN_DEAD_END:false. Other dragons: PENALTY_TIGHT + PENALTY_NO_TAIL 600 (7658-7668) outweigh EAT_BONUS 300; CRAMPED_EAT skips those two for a non-queen step that eats and keeps avail >= length+2.
[M] single games, TD seed 7 seat 0 vs m3base: one17+ST1 first eat r62, 31 pearls / 9 dragons at r100; +CRAMPED_EAT r63, 39 / 14; +CRAMPED_EAT+TR_STALL_ROUNDS:1 r57, 40 / 10 (mate eats 4 in the compartment r57-60). ST1 = ST4 = ST4+HEADING_TIE 12 gave byte-same game (those leads look inert on one17 here; baseline game still queued).
Stripes [M]: first eat is r3-r9 already; in all 4 online games a starter enters the 3-cell pearl fountain at (16,9)-(16,10)-(17,10) through the portal, grows 2->5, splits, and the front L2 half dies there by 'wall' (r16; in 1528858 six times by r63). Net +1 length per visit, never a head. No start-room constant touches this.
Games take 7-60 s but only 2 run machine-wide; six-map check of CRAMPED_EAT is queued now.

---

## 2026-10-09 05:11:53 — tiny-opus final: not ready, causes found on both maps

tiny-opus FINAL (14:11): not ready: no existing constant gets first eat 15 rounds earlier or doubles r100 dragons on either small map; nothing should go live from this job.
Found instead what starves us: on Tower Defense our dragons reach the tower door and will not step into the pearl compartments, and the right-hand start starves locally too (3 dragons at r100); on Stripes a starter dies in a 3-cell pearl fountain at r16 every game.
How sure: mechanisms are measured in replays and read in code; every local number below is ONE game (seed 7, vs m3base), so treat sizes as leads.

Hash/identity: all-off 92fb69564fbd OK; my copy = base (cmp); one17 build = d6d14e1f8f53, same binary as mD17, so mD17 was used as the baseline. No source change, diff is empty.

Tower Defense, local, seat 0 (left room), r100 pearls / dragons r25,50,100 / first eat:
  mD17 (one17)                  44 / 2,2,12 / r68   won r231
  +TR_STALL_ROUNDS:1            31 / 2,2,9  / r62   won r184   (ST4 and ST4+HEADING_TIE 12: same eats, traces, counts, result as ST1)
  +CRAMPED_EAT                  39 / 2,2,14 / r63   lost at round limit 17-18
  +CRAMPED_EAT+ST1              40 / 2,2,10 / r57   won r147
Seat 1 (right room): mD17 19 / 2,2,3 / r69, queen dead r99, eliminated r192; +CRAMPED_EAT same numbers. m3base from the right: 35 pearls, 7 dragons.
Stripes: mD17 seat 0 32 / 2,4,7 / r9 (won r140); seat 1 43 / 2,4,5 / r9, queen dead r39 (lost); +CRAMPED_EAT same numbers both seats.
Check maps, mD17 vs +CRAMPED_EAT, pearls/dragons at r100: gx_open 116/26 both, gx_rooms 51/8 both, default 65/15 both, maze 81/29 both (maze result differs after r100: loss 59-72 vs win 65-46). Devil and Weakhold not played; no head to head vs mD17 (only 2 games run machine-wide, flock in engine/run_game.py; I stopped my 2 queued games by PID at 14:10).

Mechanisms
1 [M] Start room, one17 TD seat 0: queen goes (5,4)->(7,7) r5 (centre pull), west to (2,5) r12, back east to (7,5) r17, west again, leaves by (2,1) r26; mate leaves r35. With ST1 queen leaves r16, mate r29. Door reached r42-52. So the room costs ~10-20 rounds, not the 45 that matter.
2 [M] At the door: online 1523625 r56 queen L2 at (19,2), pearl at (18,2) one step (born r19), five more within 5 steps; she steps to (19,1); both starters pace x=19-20 from r52 to r100, 1 eat. Same pattern 1528859, 1525835 (all three started in the right room; 1527402 started left and had 24 dragons at r100). Local: queen at (12,13) r42, pearl (13,13) one step, walks off, first eat r62-68 in the open middle band.
  [C] queen: -6000 when room < 3*length+8 or avail < length+8 (4820-4821, 7674-7689), hard-coded, only QUEEN_DEAD_END:false removes it (not tested, not advised today). Others: PENALTY_TIGHT + PENALTY_NO_TAIL 600 (7658-7668) against EAT_BONUS 300; CRAMPED_EAT (74, 7656) lifts those for a non-queen eating step with avail >= length+2.
3 [M] Stripes: in all 4 online games a starter takes the portal into (16,9)-(16,10)-(17,10), eats 3 (2->5), splits, front L2 dies there by 'wall' (r16, r28, r32; in 1528858 six deaths at (17,10) by r63). Local mD17 does the same at r16. [C] POCKET_LOOP treats a pocket with a portal door as open (5471-5489), so the dead-end cells behind the door are not a pocket.

What would show this wrong: TD seat 1 on other seeds not starving; a debug print of the score terms at (19,2)/(12,13) showing a term other than the dead-end/no-tail ones rejects the pearl step.
Files: ROOT/data/codex/astra/tiny-opus/ (table-all.txt, table-check.txt, early.py, late.py, deaths.py, table.py), runs ~/meow-redteam/solo/runs/ty_*.
Correction to heads-up 2: ST1/ST4 replays are not byte-same (bot name in the header); eats, traces, counts and result are the same.

---

## 2026-10-09 05:11:53 — closing summary

**not ready: no existing constant meets the bar on either small map.** Nothing from this job should go live. The final report went to the lead at 14:11, before the 14:12 cut.

What I found instead is the more likely cause of the starvation; every local number below is a single game (seed 7, against `m3base`).

- **Tower Defense, at the tower door:** our dragons reach the door and will not step into the pearl compartments. Online (game 1523625, round 56) the queen stood one step from a pearl, with five more within five steps, and walked away. Both starters then paced beside the tower from round 52 to 100 with one eat. Locally the queen does the same at round 42.
- **Why, from the code:** the queen takes a 6000 dead-end penalty when the room is under 3×length+8 (lines 4820-4821, 7674-7689), and only `QUEEN_DEAD_END:false` removes it. Other dragons are held out by the tight and no-tail penalties (7658-7668).
- **Tower Defense, right-hand start:** it starves locally too. `mD17` from the right room had 19 pearls and 3 dragons at round 100, with the queen dead at round 99. The three online starvation games all started on the right; the one left-start game had 24 dragons at round 100.
- **Start room:** it costs only about 10 to 20 rounds. On one17 the queen leaves at round 26 and the mate at round 35.
- **Stripes:** first eat is already round 9 locally (3 to 9 online), so no start-room constant applies. In all four online games a starter enters the 3-cell pearl fountain at (16,9)-(16,10)-(17,10) through the portal, grows from 2 to 5, splits, and the front half dies there. Local `mD17` does the same at round 16.

Tower Defense candidates, seat 0, single games:

| Build | First eat | Pearls r100 | Dragons r100 | Result |
|---|---|---|---|---|
| `mD17` (one17) | r68 | 44 | 12 | won r231 |
| + `TR_STALL_ROUNDS:1` | r62 | 31 | 9 | won r184 |
| + `CRAMPED_EAT` | r63 | 39 | 14 | lost at round limit 17-18 |
| + `CRAMPED_EAT` + `TR_STALL_ROUNDS:1` | r57 | 40 | 10 | won r147 |

- **`TR_STALL_ROUNDS` 4 and 4 with `HEADING_TIE` 12:** same eats, traces and result as the value 1.
- **`CRAMPED_EAT` elsewhere:** it changed nothing through round 100 on Tower Defense seat 1, Stripes (both seats), `gx_open`, `gx_rooms`, `ladder_default_1` and `ladder_maze_1`.

Not done: `ladder_devil_1` and `ladder_weakhold_1` were not played, and there was no head to head against `mD17`. Only two games run machine-wide (a lock in `engine/run_game.py`), so the queue ate most of the window; I stopped my two queued games by PID at 14:10.

Hash checks pass: all-off is `92fb69564fbd`, and the one17 build of my copy is the same binary as `mD17` (`d6d14e1f8f53`). There is no source change, so the diff is empty and nothing needed committing.

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/tiny-opus/`:
- table-all.txt
- table-check.txt
- early.py
- late.py
- deaths.py
- table.py

Runs are under `~/meow-redteam/solo/runs/ty_*`.
