# Reports sent to the lead by qaway-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 03:14:26 — qaway heads-up: D=7 fires, D=5 is a no-op

qaway-opus heads-up (12:15): QUEEN_KEEP_AWAY is built, all-off hash 92fb69564fbd OK, one15-values binary is byte-identical to mD15 (sha 1537f0dc). Value 5 is a no-op so far [M]: 2 of 2 games replay-identical to off (QS_PAY_REACH 4 already covers cells within 4 steps); value 7 does change her moves (first queen divergence r3 on ladder_default vs mD15), so only 7 is worth testing.
Not ready yet: only 2 paired games done, the game slot queue is ~6 min per spec; in the one diverging game (default, vs mD15) she lives in both arms but pearls by r100 were 109 on vs 137 off, so treat as unproven. Running off vs 7 on 16 more ladder/gx specs now; final report by 12:50.

---

## 2026-10-09 03:53:08 — qaway final: built, verified, NOT ready to go live

qaway-opus final (12:49): QUEEN_KEEP_AWAY built and hash-clean, but NOT ready to go live. It is safe (no pearl loss in total) and too weak: it does not lower the ram-death class.
Value 5 = no-op (replay-identical to off in 2 of 3 games); value 7 changes her moves in only 15 of 28 paired games and her mean gap to a head in view does not move (3.64 -> 3.67).
How sure: fairly sure it is not a fix (28 pairs, one instrumented game explains why); not sure it is harmless on every map (default_1 pearls -20% in one game).

WHAT I BUILT [C] ~/meow-redteam/solo/src/w-qaway/main.cpp, diff ROOT/data/codex/astra/qaway-opus/qaway-opus.diff (154 lines, 4 hunks)
- constexpr int QUEEN_KEEP_AWAY = 0 (steps), QUEEN_AWAY_PENALTY = 1e5 (above pearl/territory scores, below LONG_THREAT_VETO 1e6, ROUTE_OVERRIDE 1e7, QS penalties 2e8). QUEEN_AWAY_LOG is dead weight (bot LOG lines are not kept in replays), drop it.
- map_away(): one depth-limited BFS per pick_direction from every head she knows (ghosts <= 3 rounds old, which include heads in view, plus far_sight heads from mates), over cells with enter_time <= 1. State in a static accessor so the class layout is unchanged.
- In pick_direction, after the ring_wary block: each open step is charged PENALTY * (D - steps to nearest head). A step with fewer than two ways on, or closed/dead, is charged at least as much as the worst two-way step, so she never takes a one-exit cell for distance. No head within D = zero charge, so she eats as before; charges are relative, she never freezes.
- extend_stride: the real queen's free stride may not step nearer a head inside D.

1. IDENTITY [M] all-off bots/qa_off/bot = 92fb69564fbd7fbb... OK. One15 values: bots/qa_id/bot sha 1537f0dc = bots/mD15/bot, byte-identical binary, so I did not play the 4 cmp games.

2. DOES IT FIRE [M] 28 paired specs (off qa_L vs on qa_7, same map/seed/seat; 18 vs mD15, 10 vs m3base; 21 ladder + 7 gx)
- replay identical to off: 13 of 28 (10 of 18 vs mD15, 3 of 10 vs m3base), although she had a head in view on 8 to 156 turns in 12 of them.
- her turns with an enemy head in her 7x7 view, mean torus gap: mD15 off 897 turns 3.64, on 897 turns 3.67; m3base off 323 / 3.68, on 315 / 3.66. Turns at gap <= 3: 425 -> 402 and 146 -> 147.
- Why [M, one instrumented game, around_unsw side1 vs mD15, queen rammed r74 in both arms]: of her 75 turns, 9 had one open step, 24 two, 42 three. Only 17 turns had any charge, and on 12 of those she had one or two open steps. The argmax changed on 1 turn (r57) and the replay still came out identical. Her last 4 turns: one open step three times. Dump: qaway-opus/dbg-around_unsw-side1.txt.
- In all 15 diverging games the first different action is the queen's own, so non-queen behaviour before her divergence is identical.

3. WHAT IT BUYS AND COSTS [M] tables: qaway-opus/table-mD15.txt, table-m3base.txt
            n   queen dead   wins    q100  q200  qend   pearls r100  dragons r100
mD15  off  18      12         11      51    42   176      2920          598
mD15  on   18      11         12      51    44   167      2917          607
m3b   off  10       8          7      24    15    70      1739          337
m3b   on   10       6          7      31    25    89      1855          373
- The 15 diverging games: dead -> alive 3 (gx_open s1, tower_defense s0, queen_of_spades s1), dies later 5 (australia both seats, tower s1, weakhold, gx_rotation), dies earlier 4 (gx_corridors r446->r268, trauma r440->r409, stripes r67->r51, islands r238->r235), both alive 2 (default qend 33->20, queen_of_spades s0), same round 1.
- Pearls r100 per map: down more than 10% on one, ladder_default_1 s0 137 -> 109 (her own length is 4 in both, so this is knock-on, single game). Every other map equal or up (stripes 45->59, weakhold 46->54, tower s1 48->53).

4. HEAD TO HEAD vs mD15 [M] 11 -> 12 wins of 18, with 5 flips: tower s1, weakhold, queen_of_spades s1 loss->win; islands, slithery s1 win->loss. Noise level at this n.

AGAINST THE READY BAR: hash OK; dies in fewer games 20 -> 17 of 28 and later in 5, earlier in 4 (not "most"); pearls fail on one map; head to head not worse. Missing in one line: the death class did not move, because by the time a head is within 7 steps she usually has one or two open steps, so a step-choice term has nothing to choose between.

WHAT THIS POINTS TO [E] the lever is where she lives, not which step she picks near a head: her candidate count is already 1-2 on a third of all turns with no enemy near. That fits your peer note (their queen stays ~2 cells from her start tile). A "stay in a cell region with 3 open steps" or home-radius rule is the untested thing; I did not build it.
WOULD SHOW ME WRONG: an instrumented count over more games where charged turns mostly have 3 open steps (then the weight or the two-ways rule is what blocks it, not geometry); I have one game only.
All my runners have exited; no games of mine are running.

---

## 2026-10-09 03:53:08 — qaway correction to one line of the final report

qaway-opus correction to one line of my final report: in the instrumented game her last turns were r71 three open steps (all at pay risk), r72 two (one already under the pay penalty), r73 one, r74 one. So "one open step" holds for her last two turns, not three of the last four. The other counts stand (9 / 24 / 42 turns with one / two / three open steps; 17 charged turns, 12 of them with one or two open steps).

---

## 2026-10-09 03:53:08 — closing summary

`QUEEN_KEEP_AWAY` is built and hash-clean, but it is not ready to go live: it does not lower the queen ram-death class. The full report and one correction have gone to the lead.

- **Identity:** the all-off binary hash is `92fb69564fbd…`, as required. The one15-values build is byte-identical to `mD15` (sha `1537f0dc`), so I did not play the four `cmp` games.
- **Value 5:** effectively a no-op — two of the three games played were replay-identical to off, the third diverged at r130.
- **Value 7:** changes her moves in only 15 of 28 paired games. Her mean gap to an enemy head in view does not move (3.64 to 3.67 against `mD15`).

| Opponent | Arm | Games | Queen dead | Wins | Pearls r100 | Dragons r100 |
|---|---|---|---|---|---|---|
| `mD15` | off | 18 | 12 | 11 | 2920 | 598 |
| `mD15` | on 7 | 18 | 11 | 12 | 2917 | 607 |
| `m3base` | off | 10 | 8 | 7 | 1739 | 337 |
| `m3base` | on 7 | 10 | 6 | 7 | 1855 | 373 |

- **Diverging games (15):** she goes from dead to alive in 3, dies later in 5, dies earlier in 4, is alive in both arms in 2, and dies the same round in 1.
- **Pearls:** down more than 10 percent on one map only, `ladder_default_1` seat 0 (137 to 109, a single game); every other map is equal or up.
- **Non-queen behaviour:** in all 15 diverging games the first different action is the queen's own.
- **Why it is weak:** in the one instrumented game (`around_unsw`, seat 1, rammed r74 in both arms), only 17 of her 75 turns carried any charge. On 12 of those she had one or two open steps, so there was nothing to choose between. This is one game, not a count across the set.

This suggests the lever is where she lives rather than which step she picks near a head; a home-radius or "stay where three steps are open" rule is untested and I did not build it.

`QUEEN_AWAY_LOG` should be dropped if anyone reuses the diff, because bot log lines are not kept in replays. All my runners have exited and no games of mine are running.

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qaway-opus/`:
- `qaway-opus.diff`
- `table-mD15.txt`
- `table-m3base.txt`
- `dbg-around_unsw-side1.txt`
- `qa_cmp.py`

Source is `~/meow-redteam/solo/src/w-qaway/main.cpp`; `dbg.cpp` beside it is the instrumented copy and is not a deliverable.

---

## 2026-10-09 03:53:08 — qaway: your two messages arrived after my final report; building the full-reach rule now

qaway-opus (12:52): your two messages (long fed queen; six Cache cases) reached me only after my 12:49 final report. My existing pairs already include your test case and the switch FAILS it [M]: ladder_slithery_fight seat 1 vs mD15, queen 17 long rammed at r350 off, 16 long rammed at r350 on (first divergence is r350 itself). The single-step term does not use her free steps, as you suspected.
Unless you say stop, I am now building the one rule you asked for as a second switch QUEEN_OUT_OF_REACH (off by default): if her chosen step ends within an enemy's full reach (free + payable, existing stride_reach_map) plus a margin, and a seen cell outside all reaches is within her own free steps, she goes there in one multi-step move. I will stop at 13:30 and report by 13:35 with slithery pairs first (death round, length r350/r400/end); tell me if you want an earlier or later cut.

---

## 2026-10-09 04:33:57 — qaway second report: full-reach rule built, fails your Slithery case, not ready

qaway-opus second report (13:32): QUEEN_OUT_OF_REACH built (the rule you asked for), hash-clean, and NOT ready. It fails your own test case: the fed queen on Slithery seat 1 is rammed at r349 with the switch on (r350 off), in all three forms I tried.
Reason, measured: she first SEES the attacker at gap 5 and its reach is 5 (5 long = 2 free + 3 paid). One turn earlier it was at gap 8, outside her 7x7 view. Sight is the limit, not the step rule.
How sure: sure about this one game (turn-by-turn below); the wider table is 11 pairs only, the game queue slowed to ~5 min a spec.

WHAT IT IS [C] ~/meow-redteam/solo/src/w-qaway/main.cpp; diff on my 12:00 base: qaway-opus/qaway-opus.diff; same change applied on your current base (with QUEEN_NO_BLIND_PORTAL): w-qaway/main-on-current-base.cpp + qaway-opus/qaway-opus-on-current-base.diff
- constexpr int QUEEN_OUT_OF_REACH = 0 (margin in steps; tested 1 and 3), QUEEN_REACH_PAY = 3 (paid steps counted per enemy).
- leave_reach_map(): per known enemy head (in view, ghosts with age, mates' far heads; enemy queen skipped) reach = free steps + min(length - 2, 3), spread with the existing spread_kill.
- reach_leave(), called in act() after the hit_blocked block, real queen with 2+ free steps only: if her chosen step ends within reach + margin, BFS over her FREE steps through cells seen this turn, take the cell farthest out of every reach (ties by score_step), needing risk 0, not a dead end, room >= length + 2. extend_stride may not step deeper into a reach.
- Hash [M]: all-off 92fb69564fbd on both bases; one15 values = mD15 byte for byte (1537f0dc).

YOUR TEST CASE [M] ladder_slithery_fight seed 1 seat 1 vs mD15 (script qaway-opus/qa_last.py)
- off: r344-346 she takes 0 steps and goes 19 -> 17 -> 15 -> 13 long (sheds 2 a turn, standing still; existing behaviour, not mine). r350 start: enemy 847 (6 long) at gap 5 in view, she moves 3 steps and ends at gap 4, rammed on 847's turn.
- on (margin 3): r348 the rule fires, 4 steps; she ends at gap 6 from 847 and gap 7 from 871 (14 long), both outside her view. r349 start: 847 (5 long) gap 5 and 871 gap 6 now in view, she has 4 free steps, moves 2, ends at gap 5 / gap 4, rammed by 847.
- first form (uncapped reach, any queen length): rammed r352 at 19 long. Uncapped reach was worse: the 14-long enemy's reach of 16 covered every cell, so the nearer 5-long stopped counting.

PAIRS, third form margin 3, same map/seed/seat, off = one15 behaviour [M] tables qaway-opus/table-reach-mD15.txt, table-reach-m3base.txt
            n   queen dead   wins   pearls r100
mD15  off   7       6          3       2554
mD15  on    7       5          4       2554
m3b   off   4       3          3        840
m3b   on    4       3          3        840
- 6 of 11 replay-identical. The 5 that differ: Slithery s2 seat 1 died r248 -> lives, 51 long, loss -> win. Slithery s1 seat 1 r350 -> r349, win -> loss. Slithery s4 seat 1 lives both, end length 67 -> 53. Queen of Spades seat 1 r367 (17 long) -> r200 (3 long). gx_corridors r446 -> r323 (12 long; off she was 14 at r350, 33 at r400).
- Fed queen class (10+ long after r300, rammed): one case in my games, not saved. Her length r350/r400/end is in the tables.
- Pearls r100 identical on all 11 (the rule needs 5+ length, so nothing moves before r100). Margin 1: 3 pairs, 2 identical, Slithery s1 same death.
- First form (any length, full reach), 8 pairs vs mD15: wins 4 -> 1 (margin 1) and 4 -> 3 (margin 3). Do not use that form.

AGAINST THE READY BAR: hash OK; queen dies in 8 of 11 instead of 9, but earlier in 3; the named test case fails; head to head 3 -> 4 of 7 (noise). Missing in one line: she cannot leave a reach she cannot see, and attackers with reach 5+ arrive from outside a 3-cell view.

WHAT WOULD ACTUALLY ADDRESS IT [E, not built]: (1) heads from mates at longer range and age than QUEEN_FAR_HEADS 2, so a 5-reach attacker is known at gap 8+; (2) stop the fed queen shedding 2 a turn while standing still (r344-346 above) — check which branch that is before touching it; (3) escorts between her and open lanes. I have no evidence for any of these beyond the one game.
WOULD SHOW ME WRONG: more fed-queen deaths where the attacker was in her view two turns before the ram and she still had free steps to a clear cell; then the rule's cell filters (risk 0, room >= length + 2) are what block it.
QUEEN_KEEP_AWAY (first report) is unchanged in the same file, still off, still not recommended. All my runners are stopped; a few queued games of mine may still finish on their own.

---

## 2026-10-09 04:33:57 — closing summary

Both switches are built and hash-clean, and neither is ready to go live; the second report has gone to the lead.

**`QUEEN_OUT_OF_REACH` (the rule from the lead's follow-up messages)** fails the lead's own test case. On Slithery Fight seed 1, seat 1 against `mD15`, the fed queen is rammed at r349 with the switch on and r350 with it off, in all three forms I tried.

The reason is sight, not the step rule. She first sees the attacker at gap 5 when its reach is already 5 (5 long, 2 free plus 3 paid); one turn earlier it was at gap 8, outside her 7 by 7 view.

Paired results for the final form (margin 3, paid reach capped at 3, queens with 2+ free steps only):

| Opponent | Arm | Games | Queen dead | Wins | Pearls r100 |
|---|---|---|---|---|---|
| `mD15` | off | 7 | 6 | 3 | 2554 |
| `mD15` | on | 7 | 5 | 4 | 2554 |
| `m3base` | off | 4 | 3 | 3 | 840 |
| `m3base` | on | 4 | 3 | 3 | 840 |

- Six of the 11 pairs are replay-identical to off.
- Of the five that differ, she is saved in one (Slithery seed 2, loss to win), dies earlier in three, and lives in both arms of the fifth with a shorter end length (67 to 53).
- The first form (uncapped reach, any queen length) was worse: wins against `mD15` went 4 to 1 at margin 1 and 4 to 3 at margin 3 over 8 pairs. It should not be used.
- Only 11 pairs were possible because the game queue slowed to about five minutes a spec.

**`QUEEN_KEEP_AWAY` (the original task)** is unchanged from my first report: safe in total but too weak, still off and not recommended.

One thing seen in the Slithery replay that is not mine: on r344–346 the fed queen stands still and drops from 19 to 13 long. I flagged it to the lead as worth checking; I have not traced which branch does it.

Hash checks hold throughout: the all-off binary is `92fb69564fbd…` on both my 12:00 base and the lead's current base, and the one15-values build is byte-identical to `mD15`. All my runners are stopped; a few queued games may still finish on their own.

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qaway-opus/`:
- `qaway-opus.diff`
- `qaway-opus-on-current-base.diff`
- `table-reach-mD15.txt`
- `table-reach-m3base.txt`
- `table-mD15.txt`
- `table-m3base.txt`
- `qa_last.py`
- `qa_cmp.py`

Source is `~/meow-redteam/solo/src/w-qaway/main.cpp`, with the same change applied on the current base in `main-on-current-base.cpp` beside it.

---

## 2026-10-09 04:33:57 — qaway: your 13:25 terms arrived at 13:33; verdict is one16 stays final

qaway-opus (13:34): your go-ahead with the 13:25 cut reached me at 13:33, after my second report. By your own rule the answer is: one16 is final. Slithery does not show her surviving in clearly more pairs.
Slithery pairs I have, final form margin 3 [M], off = one15 behaviour, opponent mD15 not mD16 (one16 arrived mid-run): seed1 seat1 dies both (r350 off, r349 on); seed2 seat1 died r248 -> lives 51 long; seed3 seat1 identical (dies r317, 4 long); seed1 seat0 identical (dies r157, 2 long); seed4 seat1 lives both (end 67 -> 53). Against m3base seed1 seat0: identical, lives 67. So one more survival in 6 pairs, and the one fed-queen ram in the set is not prevented.
Gaps against your terms, so you do not assume them: my file still contains QUEEN_KEEP_AWAY and the log switch; the destination test is "risk 0, not a dead end, room >= length + 2", not "two ways on"; it triggers on her chosen step, not her own cell; it applies from 2 free steps = length 5 (your note says 8); I did not build against one16 values or compare with mD16 (e05a74e6e982). Identity that I did measure: 6 of 11 pairs replay-identical to off, and pearls by r100 identical in all 11.
I am past the cut and am not starting new games. If you still want a clean one16-based file with only this switch and its hash check (a build, no games, about 5 minutes), say so and I will do just that.

---

## 2026-10-09 04:33:57 — closing summary

The lead's go-ahead for `QUEEN_OUT_OF_REACH` (with a 13:25 hard cut) reached me at 13:33, after I had already built and reported on it. By the lead's own rule the answer is that one16 stays final, and I have told them so.

- **Slithery result:** she survives in one more of 6 pairs, not clearly more. The one fed-queen ram in the set (seed 1, seat 1) is not prevented: r350 with the switch off, r349 with it on.
- **Gaps against the lead's terms:**
  - My file still contains `QUEEN_KEEP_AWAY` and the log switch.
  - The destination test is "risk 0, not a dead end, room at least length + 2" rather than "two ways on".
  - It triggers on her chosen step, not her own cell.
  - It applies from length 5, not 8.
  - My pairs were against `mD15`, and I did not build with one16 values or compare against `mD16`.
- **Identity I did measure:** 6 of 11 pairs are replay-identical to off, and pearls by r100 are identical in all 11.

I am past the cut and have started no new games. I offered the lead a clean one16-based file with only this switch and its hash check (a build, no games, about five minutes) if they still want it; I am waiting on their answer.

Everything is in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qaway-opus/`, with source in `~/meow-redteam/solo/src/w-qaway/`.

---

## 2026-10-09 04:33:57 — qaway: diff paths and Slithery numbers, with one merge warning

qaway-opus (13:37): diff paths and Slithery numbers. My recommendation stays "do not ship": 1 more survival in 6 Slithery pairs, and the one fed-queen ram is not prevented.

DIFF
- On the 12:49 source (one16, before QS_SHED_MAX): ROOT/data/codex/astra/qaway-opus/qaway-opus-on-current-base.diff ; whole file ~/meow-redteam/solo/src/w-qaway/main-on-current-base.cpp (all-off hash 92fb69564fbd [M]).
- It also carries QUEEN_KEEP_AWAY / QUEEN_AWAY_LOG / QUEEN_AWAY_PENALTY (struct Away, map_away, away_steps, one block in pick_direction, one condition in extend_stride). Leave those out.
- QUEEN_OUT_OF_REACH is exactly: constants QUEEN_OUT_OF_REACH and QUEEN_REACH_PAY (3); functions leave_reach_map() and reach_leave() placed before portal_guarded(); the 7-line call in act() placed just before "if (QUEEN_SAFETY && queen_wary() && !any_enterable && (hit_head || pay_head) ..."; in extend_stride the leave_reach_map() call before "Position const origin = head;" and the queen_margin condition after the SHARE_SIGHT one.
- MERGE WARNING [C]: my call in act() is guarded by !qs_plain. The trapped fall-through of the hit_blocked block sets qs_plain = true, so in exactly the case you describe (long exposed queen, no escape, no shed) my jump will NOT fire as written. If your QS_SHED_MAX path ends in that qs_plain branch you would have to drop that guard, and that combination is untested by me.
- Not what your terms asked: destination test is risk 0 + not a dead end + room >= length + 2 (not "two ways on"); trigger is her chosen step (not her own cell); active from 2 free steps = length 5.

SLITHERY, margin 3, on against off, same seed and seat [M]. Off = one15 behaviour, opponent mD15 (not mD16/mD17). Her length r350 / r400 / end:
  seed1 seat1  off  0/0/0   rammed r350 at 17      on  0/0/0    rammed r349 at 18   (the fed-queen case; not saved; win -> loss)
  seed2 seat1  off  0/0/0   died r248 at 2         on  6/14/51  lives               (loss -> win)
  seed3 seat1  off  0/0/0   rammed r317 at 4       on  identical game
  seed1 seat0  off  0/0/0   rammed r157 at 2       on  identical game
  seed4 seat1  off  18/28/67 lives                 on  18/28/53 lives (first difference r484)
  vs m3base seed1 seat0   off 10/25/67 lives       on  identical game
  6 pairs: she survives in 3 on against 2 off; dies in the same round or a round earlier in 3; end length lower in 1.
Other maps, same form: 5 pairs (islands, queen_of_spades, gx_open, gx_corridors, tower_defense): 3 identical; queen_of_spades rammed r367 at 17 -> r200 at 3; gx_corridors rammed r446 -> r323 at 12.

IDENTITY
- [C] With fewer than 2 free steps (length 4 or less) both entry points return before doing anything, so such turns are the same program.
- [M] 6 of 11 pairs replay-identical to off; in the 5 others the first different action is the queen's own, at r187, r188, r192, r348, r484; pearls by r100 identical in all 11.
- NOT shown: identity against one16 or one17 values, and I did not check her length in the 6 identical games one by one.

---

## 2026-10-09 04:33:57 — closing summary

I've sent the lead the diff paths and the Slithery numbers they asked for, with my recommendation unchanged: do not ship `QUEEN_OUT_OF_REACH`.

- **Slithery, margin 3, six pairs:** she survives in 3 with the switch on against 2 with it off. The fed-queen case (seed 1, seat 1) is not saved: rammed r350 at 17 long off, r349 at 18 long on.
- **Other maps, five pairs:** three are replay-identical; on Queen of Spades and `gx_corridors` she dies earlier with the switch on.
- **Merge warning:** my call in `act()` is guarded by `!qs_plain`, and the trapped fall-through sets `qs_plain = true`. If the new `QS_SHED_MAX` path ends there, my jump will not fire in exactly the case the lead described. Dropping the guard is untested.
- **Not shown:** identity against one16 or one17 values. My pairs were against `mD15` with one15 behaviour as the off arm.
- **Diff contents:** it still carries the `QUEEN_KEEP_AWAY` hunks; I listed which parts belong to `QUEEN_OUT_OF_REACH` so the lead can leave the rest out.

The lead said not to rebase myself and will decide by 13:45, so I have stopped: no games or builds of mine are running.

The diff is `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qaway-opus/qaway-opus-on-current-base.diff`, and the whole file is `~/meow-redteam/solo/src/w-qaway/main-on-current-base.cpp`.
