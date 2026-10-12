# Reports sent to the lead by watch17-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 04:56:36 — First verdict: one17 looks fine (20 games)

one17 looks fine (20 games) — watch17-opus, 13:55 KST: one17-c1 (15, Cache me outside) + ranked battle b1532562 (5, Team SKKU). All counts measured from replays, bot id 21693 checked in each.

Health
- c1: 5 wins of 15 (one15-c1 5, one16-c1 3). Ranked vs SKKU: 4 of 5 (queen alive at 78 on Autarky).
- Timeouts in our turns: 0 in all 20. No sudden collapse (3+ dragons to 0 in one round): 0. Wiped in c1 4 times (one15-c1 5, one16-c1 5), all gradual.
- Queen died in 11 of 15 c1 games (one15 13, one16 14), median death round 139 (137, 144), never at length 10+. Death causes head-on 9, body 1, wall 1 (same mix as before).
- "No action" deaths of our small dragons: 466 in c1 (one15-c1 506, one16-c1 637), same rate as before, not new.
- Only standstill: the queen's opening splits r0-r11 on Slithery Fight (present in one15/one16 too).

Mechanism (queen 10+ at round start, enemy head within 3, plain torus distance)
ver    games turns  moved  split(to 2)  dead<=3r  dead<=5r
one15   56    57     54     3 (2)        3         5
one16   35    25      6    19 (2)        3         4
one17   20    21     18     3 (0)        0         0
- No split from 10+ that leaves her 2 in one17. Base rate was 4 in 91 games, so 20 clean games is also what chance gives; I cannot see from a replay whether the changed line itself was reached.
- She is not dying faster in these spots: alive 5 rounds later on all 21 turns (games 1532059 Trauma r423-r485, alive 30 at the end; 1532061 Slithery Fight r342-r374; 1532562 Autarky).

One thing to know, not caused by one17: Slithery Fight 1532061 r370-r379 the queen stands at (41,1) and splits a 2-cell child off seven times (15 > 4), then walks into a wall at r380 at length 4. That is the older "blocked but not exposed" branch (one17-bot/main.cpp line 1797, split_off(keep)), which one16 and one15 also take (by-2 splits from 10+ after r50: one16-p1 25, one15-p1 6, one17-c1 4). Game was lost on longest dragon with both queens dead; one16 on the same map shed 19>2 at r363 and died r476. So on this map the result is the same either way.

Same-map table against Cache (one15 / one16 / one17) and the per-game lines: ROOT/data/codex/astra/watch17-opus/watch.md. Next: one17-s1 (~14:15), one17-p1 (~14:35), ranked battles as they land.

---

## 2026-10-09 05:04:44 — Second verdict: one17 looks fine (30 games)

one17 looks fine (30 games) — watch17-opus, 14:06 KST: added ranked b1533048 (Computers, 2 wins of 5) and b1533125 (Team SKKU, 3 of 5). Measured from replays, bot id 21693 in all.

- 30 games, 14 wins. Timeouts 0, sudden collapses 0, nothing standing still apart from the Slithery Fight opening splits.
- Sheds from 10+ to 2: 0. Queen 10+ with an enemy head within 3: 25 round starts in 4 games; she moved on 22, split 2 off on 3; dead within 3 rounds 0, within 5 rounds 0 (one15 3 and 5 of 57; one16 3 and 4 of 25).

One watch item, not a reason to roll back on its own:
- 1533128 Autarky r442: queen at length 62 walks three free steps north, (19,8) to (19,5), stops next to a 3-cell enemy head at (19,4) and is rammed. The game was still won (longest 20:3, enemy queen already dead). The head was 4 away at round start, so it is outside my "within 3" table.
- I cannot read from a replay whether that turn went through the changed line. If it did, the route is one17-bot/main.cpp 1824-1829: no shed, no escape, then "Trapped: for this turn she moves as a plain dragon" (qs_plain) and hunt_path, which would explain a queen walking up to an enemy head. That is inference, not measured.
- The same kind of death is in the older bots: one15 1523634 r391 (queen 44), one15 1526093 r445 (34), one16 1528866 r390 (33), each a step next to an enemy head and then rammed. Rate 3 in 91 games before, 1 in 30 now, so no worse so far.

What would change my verdict: a second long queen (10+) lost this way in the s1 or p1 set, or any 10+ queen dead within 3 rounds of an enemy head at 3 or closer. Per-game lines: ROOT/data/codex/astra/watch17-opus/watch.md. Waiting for one17-s1.

---

## 2026-10-09 05:11:53 — Third verdict: one17 looks fine (40 games), caveat

one17 looks fine (40 games), with one caveat about the changed branch — watch17-opus, 14:13 KST. Added ranked b1531921 (Check Raise, 3 of 5) and b1532570 (Sponge, 0 of 5).

Not broken: 40 games, 17 wins, timeouts 0, sudden collapses 0, no dragon standing still, sheds from 10+ to 2: 0.
Mechanism table (queen 10+, enemy head within 3): 26 round starts, dead within 3 rounds 1 (one15 3 of 57, one16 3 of 25). Not dying faster by that measure.

Caveat: two long queens were rammed, and both fit the route the change opens (inferred from the code, a replay cannot show the branch):
- 1532574 Around UNSW r319 (LOSS, queen 0 against their 4): queen 11 at (29,35) takes one step west; enemy 534, 3 cells, 4 away, sprints five steps eating a pearl and hits her head. Fits main.cpp 1813 "a tile an enemy must pay for": the enemy paid.
- 1533128 Autarky r442 (WIN anyway on longest): queen 62 walks three steps to stand next to a 3-cell enemy head and is rammed. Fits 1824 "Trapped: for this turn she moves as a plain dragon" then hunt_path. Before one17 only a queen too short to split reached that line; now any exposed queen of 10+ with no escape does.

Against that, what one16 did in the same spots (measured): 4 sheds from 10+ to 2 in 91 games (1525842, 1527409, 1528868, 1530575); the queen was dead one round later in 2 of the 4, dead before the end in all 4, and all 4 games were lost. One17: 2 such spots in 40 games, queen dead at once in both, 1 lost 1 won. Long queens (10+) killed overall: 3 in 91 games before, 2 in 40 now.

My read: nothing here says put one16 back. The change has not shown a gain either: the queen is lost in these spots under both builds, one16 keeps a 2-cell queen for a while, one17 loses her at full length. Numbers are far too small to rank them. I would roll back only if s1 or p1 shows a third long queen walking into a head, or any crash sign.

Lines and traces: ROOT/data/codex/astra/watch17-opus/watch.md. Waiting for one17-s1 (about 14:15).

---

## 2026-10-09 05:30:44 — one17 watch ended at 40 games; now watching one18

one17 looks fine (40 games, final for one17) — watch17-opus, 14:27 KST. No one17-s1 or one17-p1 set exists on disk, and versions.tsv shows one18 (submission 21761, one18-bot written 14:06) on top, so one17 will get no more games. Last one17 games: battles finished 14:07.

I have added bot id 21761 to the same checks (timeouts, collapses, standstill, queen death, sheds from 10+, the queen 10+ / enemy within 3 table) and will report on one18's games as they land. As of 14:26: no one18 game on disk yet (no new ranked battle since 14:07, no one18-* set folder). One18 still has QS_SHED_MAX 9 (one18-bot/main.cpp line 159), so the caveat from my 14:13 message carries over unchanged: 2 long queens rammed in 40 games on the route that switch opens, against 4 sheds to 2 (all 4 games lost) in 91 games before; too few to rank.

If nothing arrives I will send a last line at 14:45.

---

## 2026-10-09 05:30:44 — one18 first 10 games look fine

one18 looks fine (10 games); one17 looks fine (40 games, final) — watch17-opus, 14:32 KST. One18's first games: b1535044, unranked against Preyas, 10 on disk, bot id 21761 in all.

- one18: 4 wins of 10 (one15-p1 6 of 15, one16-p1 6 of 15). Timeouts 0, sudden collapses 0, no standstill apart from the Slithery Fight opening, wiped 2 times, sheds from 10+ to 2: 0.
- Queen 10+ with an enemy head within 3: 2 round starts (1535047 r369, r437), alive 20 rounds later on both.
- Third long queen rammed since QS_SHED_MAX went live: 1535047 Around UNSW r461 (LOSS on longest 40:46, both queens dead). Queen 15 steps one cell north; enemy 798 five cells away splits that round and the child sprints into her head. Head was 5 away at round start.

Running count for the switch, both builds that carry it against both that do not:
                      games  queen 10+ killed  shed 10+ to 2  lost either way
one15 + one16           91         3                4          7 (7.7%)
one17 + one18           50         3                0          3 (6.0%)
So the sheds are gone and long queens are killed somewhat more often instead; the sum is level. Nothing measured says roll back, nothing says the switch gained. No crash or timeout sign in any of the 50 games.

Not checked: which code branch each death took (not in the replay); one18's QUEEN_CORRIDOR_MATE itself (outside my brief, I only ran the health checks on it). Still polling until 14:45.

---

## 2026-10-09 05:39:58 — one18 looks fine (20 games)

one18 looks fine (20 games) — watch17-opus, 14:36 KST. Added ranked b1535543 (test4, 3 wins of 5) and b1535558 (Cybers, 3 of 5), bot id 21761 in all.

- one18: 10 wins of 20. Timeouts 0, sudden collapses 0, wiped 3 times. Standstill only in the three Slithery Fight openings (queen splits r0-r7, same in every build).
- Sheds from 10+ to 2: 0. No new long queen killed in these 10 (still the one from 14:32, game 1535047). Queen 10+ / enemy within 3: 2 round starts, both survived.
- Switch count unchanged in rate: one17 + one18, 60 games, 3 long queens killed, 0 shed to 2 (5.0%); one15 + one16, 91 games, 3 killed + 4 shed to 2 (7.7%).

No sign of a broken build in either one17 or one18. Last line at 14:45.

---

## 2026-10-09 05:39:58 — one17 45 games, one18 30 games: both fine

one18 looks fine (30 games); one17 looks fine (45 games) — watch17-opus, 14:36 KST. Added b1535563 (one18, the uncancelables, 2 wins of 5) and a late one17 battle b1533646 (BambooCode, 4 of 5).

- Both builds: timeouts 0, sudden collapses 0, no standstill outside the Slithery Fight opening, sheds from 10+ to 2: 0. one18 15 wins of 30; one17 21 of 45.
- One more long queen killed, in the late one17 battle: 1533650 Slithery Fight r279-r281 (LOSS, 0 against their 67). A 3-cell enemy sits 2 away for three rounds, queen 15 steps one cell each round, at r281 she steps to (27,21) right above its head at (27,22) and is rammed.
- "Queen 10+, enemy head within 3" table, dead within 3 rounds: one15 3 of 57 turns, one16 3 of 25, one17 4 of 44 (3 of the 4 are this one death), one18 0 of 7. Per episode: one15 2 of 23, one16 2 of 7, one17 2 of 22, one18 0 of 4. Not clearly more often.

Switch count, builds with QS_SHED_MAX 9 against builds without:
                 games  queen 10+ killed  shed 10+ to 2  lost either way  those games won
one15 + one16      91         3                4           7 (7.7%)          0 of 7
one17 + one18      75         4                0           4 (5.3%)          1 of 4
Sheds are gone; kills of long queens went from 3.3% to 5.3% of games; the sum is level. All four kills look the same: a 3-cell enemy within sprint reach, she takes a single step (or walks up to it) and is rammed (1532574 r319, 1533128 r442, 1533650 r281, 1535047 r461). Which branch each took is not readable from replays.

Verdict for the 14:40 decision: no sign of a broken build, nothing that calls for putting one16 back. Last line at 14:45.

---

## 2026-10-09 05:47:33 — Last verdict: one17 and one18 fine; one19/one20 unseen

one17 looks fine (45 games); one18 looks fine (35 games); one19 and one20 cannot be judged (0 games on disk) — watch17-opus, last verdict, 14:45 KST.

- one18 final: 16 wins of 35 (added b1535538 Team SKKU, b1535553 Ballers 1 of 5). Timeouts 0, sudden collapses 0, sheds from 10+ to 2: 0, no further long queen killed.
- one17 final: 21 wins of 45, same clean health checks.
- QS_SHED_MAX 9 over both builds, 80 games: 4 long queens (10+) killed, 0 shed to 2 = 5.0% of games. one15 + one16, 91 games: 3 killed + 4 shed to 2 = 7.7%. Level; the switch neither broke anything nor showed a gain. Dead within 3 rounds of a "queen 10+, enemy within 3" turn: one15 3 of 57, one16 3 of 25, one17 4 of 44, one18 0 of 11.
- The four kills (1532574 r319, 1533128 r442, 1533650 r281, 1535047 r461) share one picture: a 3-cell enemy inside sprint reach, the queen takes one step or walks up beside its head, and is rammed. Three of the four games lost.

Not covered: versions.tsv shows one19 (21827, with QUEEN_NO_RAM, QUEEN_BLIND_STALL 20, QUEEN_DEAD_ALL off) and one20 (21843) uploaded after one18. No game of either was on disk by 14:44, so whatever is live now has had no health check from me. The scripts take a new build with one line: add its id to VER in w.py, then run w.py and rep.py from ROOT.

Not checked at any point: which code branch each queen death took (replays do not show it); distances are plain torus distance, walls and portals ignored.

Files: ROOT/data/codex/astra/watch17-opus/watch.md (verdicts, per-game lines, tables), w.py, rep.py, cmp.py, trace.py, longq.py. Stopping now.

---

## 2026-10-09 05:47:33 — closing summary

The watch is finished: one17 looks fine (45 games) and one18 looks fine (35 games), but one19 and one20 had no games on disk by 14:44, so whatever is live now has had no health check.

- **Health:** timeouts 0, sudden collapses 0, and no dragon standing still apart from the queen's opening splits on Slithery Fight, which every build does. one17 won 21 of 45, one18 16 of 35.
- **Sheds:** no queen split from 10+ down to 2 in any of the 80 games.
- **Mechanism check:** she is not dying clearly faster when she is 10+ with an enemy head within 3.

| Build | Turns (queen 10+, enemy within 3) | Dead within 3 rounds |
|---|---|---|
| one15 | 57 | 3 |
| one16 | 25 | 3 |
| one17 | 44 | 4 |
| one18 | 11 | 0 |

- **Net effect of `QS_SHED_MAX 9`:** level — the sheds are gone and long queens are killed slightly more often instead.

| Builds | Games | Queen 10+ killed | Shed 10+ to 2 | Lost either way |
|---|---|---|---|---|
| one15 + one16 | 91 | 3 | 4 | 7 (7.7%) |
| one17 + one18 | 80 | 4 | 0 | 4 (5.0%) |

- **The four kills:** games 1532574 r319, 1533128 r442, 1533650 r281 and 1535047 r461. Each time a small enemy within sprint reach rams her after she takes one step or walks up beside its head; three of the four games were lost.
- **Not confirmed:** a replay does not show which code branch ran, so I cannot say these deaths went through the changed line. From the code, an exposed queen of 10+ with no escape now falls through to the lines after `main.cpp` 1808, including "Trapped: for this turn she moves as a plain dragon" and `hunt_path`.
- **Scope changes:**
  - The planned `one17-s1` and `one17-p1` sets never ran.
  - one18 went live at about 14:06, so I ran the same checks on it.
  - Distances are plain torus distance, ignoring walls and portals.

Five verdicts went to the lead between 13:55 and 14:36, and the last at 14:45. To check a newer build, add its bot id to `VER` in `w.py`, add its name to the version tuples in `rep.py`, then run `w.py` and `rep.py` from ROOT.

Everything is in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/watch17-opus/`; open `watch.md` first (verdicts, per-game lines, tables).

---

## 2026-10-09 05:47:33 — one18 looks fine (40 games); dead-end deaths listed

one18 looks fine (40 games), with three queen dead-end deaths for you to look at — watch17-opus, 14:47 KST. Added b1536232 (Team SKKU). No one17 game has arrived since 14:33 (45 total); no game of one19 or one20 on disk yet.

Timeouts 0, sudden collapses 0, sheds from 10+ to 2: 0, in all 40. 17 wins.

Queen dies on her own move (wall or own body), my own game population (yours differs, so compare within this table only):
build  games  on wall/own  0 free sides at death  the step into the last cell had another free side
one15    56       7              7                      2
one16    35       8              8                      2
one17    45       3              3                      1
one18    40       6              6                      3
In losses only: one15 4 of 30, one16 5 of 26, one17 3 of 24, one18 2 of 23. So one18's rate (15% of games) sits between one15 (12.5%) and one16 (23%), double one17's (6.7%); not out of line, too few to call.

The three one18 deaths where she chose the dead end while another side was free, the turns the guard change could have touched (I cannot see whether it did):
- 1535545 weakhold (WIN) r319: head (9,4), two free sides, steps south into (9,5), a cell with three walls, dies on the wall r320.
- 1535048 Portals (WIN) r374: head (23,9), two free sides, takes the west step through a portal to (8,5), three walls, splits r375, dies on the wall r376.
- 1535052 Australia (LOSS) r68: head (24,35) with an enemy body alongside for five rounds, two free sides, steps west into (23,35) (two walls, enemy on the third side), splits to 2 at r69, dies on her own body r70.
The other three (1535049 Islands r185, 1535553 Maze r251, 1535544 Slithery Fight r312) were forced: one free side on the entering step, corridor or 2 by 2 pocket entered earlier.

Free side = open neighbour with no body on it at round start; it does not know enemy reach, so "another free side" may have been a tile an enemy could hit. Earlier builds have the same kind of death (for example one15 1524545 r31, 1525843 r288; one16 1528867 r193, 1529404 r156).

Still watching until 14:55; send me the new id when it is up and I will add it.

---

## 2026-10-09 05:55:15 — Final: one17, one18 fine; one19 to one21 unseen

one18 looks fine (40 games); one17 looks fine (45 games); one19, one20 and one21 cannot be judged (0 games on disk) — watch17-opus, final, 14:55 KST.

- Nothing new since my 14:47 message: no ranked battle has landed after b1536232 (14:44), and no new id reached me.
- versions.tsv now lists one19 (21827), one20 (21843) and one21 (21857) after one18. None has a game on disk, so the bot that is live at the deadline has had no health check from me. w.py already knows the three ids; running w.py then rep.py and self.py from ROOT will pick their games up as soon as a battle is downloaded.
- Standing numbers: timeouts 0 and sudden collapses 0 in all 85 games of one17 and one18; sheds from 10+ to 2: 0; long queens killed 4 in 85 games (before 3 killed + 4 shed in 91); queen dead-end deaths one18 6 of 40 games (one15 7 of 56, one16 8 of 35, one17 3 of 45), three of them with another free side on the entering step (1535545 r319, 1535048 r374, 1535052 r68).

Everything is in ROOT/data/codex/astra/watch17-opus/watch.md. Stopping.
