# Reports sent to the lead by unC-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 04:56:36 — Game queue is the bottleneck, 2 global slots

unC-opus heads-up, not a RED: local games are limited to 2 at a time for the whole machine (flock slots in ~/meow-redteam/engine/run_game.py game_slot), about 35 games are waiting at 13:55 and the oldest have waited 7+ minutes; the 256x256 crash-pass game has held one slot for 7 minutes.
So each agent gets only a handful of games before 14:12; I am running mD17 seat 0 v m3base on my 11 maps first (tiny and adjacent-start first), mirror second. Also measured from the earlier audit: the engine refuses any side under 7 or over 256, so 5x5 and 4x200 cannot exist; I use 7x7, 7x200 and 200x7 instead.

---

## 2026-10-09 04:59:15 — Tiny maps: 3 of 3 elimination losses to m3base

unC-opus heads-up: on the three smallest maps (49 to 63 cells) one17 at seat 0 loses to m3base by elimination by round 25, 3 of 3: uc_tiny7x7 (our queen L4, never split, rammed r25 by their queen L2 just after she split, leaving them a spare), uc_tiny7x9 (queen L3 rammed r14 by an L2), and your gx_corridors_7x7 (round-0 split in a 7-cell ring corridor: the child comes round and meets the queen head-on, she turns into a 4-cell dead end and dies on her own body r6; m3base loses nobody).
9x9 and larger are fine so far (9x9 with 2 and 6 dragons, 12 a side, adjacent starts, rich: all wins, no crash, no "no valid action" outside feeders). Seat 1, mirror and a no-SPLIT_ROUND0 arm on the corridor map are queued; no constant candidate yet. Second amber: on 3000 cells with 6 pearl beds we lose on queen length 10 to 21 with more total length (47 to 37): 8 feeder stops against m3base's 15; arms minus one feeding switch each are queued.

---

## 2026-10-09 05:11:53 — unC-opus final: extremes of size, shape, supply

RED: 7-wide tiny maps (49 cells), one map by the listed criteria (gx_corridors_7x7: queen dead r6 on her own body), SPLIT_ROUND0 off removes it there; nothing else RED on 11 new maps; no crash, timeout or bot error in 30+ games. I recommend no live change from this family.
Engine refuses sides under 7 or over 256 [earlier audit], so 5x5 and 4x200 cannot exist: I used 7x7, 7x200, 200x7. Maps: ~/meow-redteam/maps/un2/uc_*.map; runs solo/runs/uc_mD17 (side0, side1), uc_mir, uc_n*, uc_t7_*; scripts ROOT/data/codex/astra/unC-opus/.
[M] one17 seat 0 v m3base, seed 1 (first eat; our pearls r25/50/100; our dragons r25/50/100; our queen; result):
 tiny7x7 49      r8;   4/4/4;        0;        rammed r25 L4 free2;  LOSS elim r25. Seat 1 LOSS elim r22. Mirror A wins r45
 tiny7x9 63      r8;   7/7/7;        0;        rammed r14 L3 free2;  LOSS elim r20. Seat 1 win r38. Mirror A loses r32 (pearls 6 v 33)
 tiny9x9 2/side  r7;   17/22/22;     7/5/5;    alive L4;             win elim r29
 tiny9x9 6/side  r4;   20/27/27;     8/8/8;    alive L4;             win elim r30. Mirror A wins r16, both queens rammed r9-11
 many12 16x16    r6;   34/91/121;    11/20/28; alive L3;             win elim r61
 adj0 (heads touching) r8; 38/229/229; 16/59/59; alive L4;           win elim r50. Mirror: A queen rams B queen at r1, both dead
 adj1 (1 gap)    r7;   32/166/293;   13/40/60; alive L5;             win elim r66
 rich16 (all beds) r1; 281/616/1291; 26/26/58; rammed r15 L11 free2; win elim r86 (mD16 same game: queen rammed r17 L4, win r38)
 thin7x200       r8;   35/144/471;   14/57/60; alive 4/11/45;        win queen 45-0
 thin200x7       r10;  28/115/416;   12/45/62; rammed r107 L2 (shed from 6 at r105); LOSS longest 58-83 with more total (535-451)
 sparse3000 (6 beds) r32; 0/1/5;     5/5/7;    alive 3/4/10;         LOSS queen 10-21. Seat 1 LOSS 15-20. Mirror 8-18
Loops of 30+ rounds: 0.0 percent of our dragon-rounds on every map (stuck-opus detect/cls). "No valid action": only feeder stops after r300 with free cells, plus a few boxed-in at the unit cap; none on tiny maps.
Time: 0.8 to 2.3 ms wall per dragon-turn for both bots together (1024 to 4096 cells, 60 dragons a side), no growth worth noting; server WASM points not measured. gx_corridors_256x256: no result file, engine.log stops at round 372 (written 13:52), process gone at 13:58, no error line in it: yours to confirm whether you stopped it.
RED gx_corridors_7x7 (your st_mD17 run): [M] r0 queen L4 splits 2+2 inside a 7-cell 1-wide ring; the child comes round, at r2 queen head (6,0) has the child's head on (5,0), her only other move is south into a 4-cell pocket (6,1)-(3,1); r6 head (3,1) walls N,S,W, dies r7 on her body; child died r3 on her body. m3base splits at r4 and loses nobody. Boards: o1_look.py <that replay> 0 0 0 6. [C] one17 main.cpp:72 SPLIT_ROUND0, :8458 harvest_round. [M] arm uc_ns0 (one17 minus SPLIT_ROUND0), same game: no early loss, draw 6-6 at r500 (our queen still dies on her body r258). One degenerate map; I did not test what the switch off costs elsewhere.
Open 7x7, not a listed RED (queen is rammed, not self-killed) but 2 of 2 seats lost to m3base: we eat 3-4 pearls and never split, m3base eats 6, splits twice at L4 and trades evenly, its queen included (r18 queen L3 into ours). [M] same game by build: one5 win, one7 loss, one8 win, one9/10/11/13/16/17 loss (one11 onward the identical game); minus QUEEN_HERD identical. Not from today's changes, not monotone, one seed: no constant.
Adjacent starts: v m3base our queen lives both maps. In the mirror she rams their queen at r1 (L4 v L4): [C] :4552-4556, a wary queen spares everything except the enemy queen and trades at equal length. By design, but it turns a touching-start game into a no-queen game at round 1.
Sparse: queens sit at 3-5 until r300, then the game is who feeds: ours stop at r302-345 then pause until about r440-468 (8 and 5 stops), m3base feeds r363-496 (15 and 11). Queen length ranged 6 to 24 over 6 games on this one map. Arms on the seat-0 game: minus FEED_CAP_ROUND, QUEEN_HERD, QUEEN_BOOT_LEN, FEEDER_EAT each replay identically (those never fire here); minus LEADER_FULL_UNITS wins 8-7; minus ATTACK_MIN_UNITS wins 24-6 with 13+ feeder stops. [E] the last is one game and the switch only gates LUNGE_PEARL and TRADE_SHORT_BY (:4535, :4556), so I read it as a diverged game, not a fix; worth 4 more seeds only if time remains.
Not checked: seat 1 and mirror on 9x9, many12, rich16, thin (queue: two game slots for the whole machine); gx 64x64 and 256x256 non-corridor, un_cells4096_1, un_cpu_1, un_unitcap_1, un_startlength_1 (no replays existed, no slot to play them); 64x64 corridors: our queen L20 died on a wall with 0 free cells at r202 (boxed), not looked at further.

---

## 2026-10-09 05:11:53 — closing summary

The report went to the lead at 14:10, and all my game queues are stopped. I changed no bot code, uploaded nothing and did not touch git.

**Verdict: one RED, no live change recommended.** The only map that is RED by the brief's criteria is `gx_corridors_7x7` from the lead's own run, where our queen dies on her own body at round 6. Removing `SPLIT_ROUND0` removes that early loss on that map: the same game becomes a 6–6 draw at round 500. It is one degenerate map of 1-wide corridors, and I did not test what switching it off costs elsewhere.

- **Crashes and timing:** no crash, timeout or bot error in any game. Wall time is about 0.8–2.3 ms per dragon-turn for both bots together, with no growth worth noting. Server-side cost was not measured.
- **Tiny maps:** on the open 7x7, one17 loses to m3base by elimination from both seats by round 25. Our queen is rammed, so this is not a listed RED. Older builds give mixed results on the same game (one5 and one8 win; one7, one9 and later lose), so it is not from today's changes and there is no constant.
- **7x9 and 9x9:** 7x9 splits by seat (seat 0 loss, seat 1 win). Both 9x9 maps are wins.
- **Adjacent starts:** against m3base our queen survives on both maps. In the mirror she rams their queen at round 1 and both die; this is by design (`main.cpp:4552-4556`).
- **Nothing to eat (3000 cells, 6 beds):** we lose on queen length from both seats (10–21 and 15–20). Our feeders stop feeding for about 100 rounds after round 345 while m3base keeps feeding. No loops of 30+ rounds on any map. Queen length ranged 6 to 24 over six games on this map, so I read it as variance. The arm without `ATTACK_MIN_UNITS` won 24–6, but that is one game and that switch does not gate feeding.
- **Other new maps:** 12 dragons a side, the all-pearl map and 7x200 are wins. 200x7 is a loss on longest dragon (58–83) after both queens were rammed.

Not checked:
- **Seat 1 and mirror** on 9x9, 12-a-side, rich and thin maps: only two games run at once across the whole machine, so few of mine got through.
- **Largest existing maps** (`un_cells4096_1`, `un_cpu_1`, `un_unitcap_1`, `un_startlength_1`, non-corridor 64x64 and 256x256): no replays existed and there was no slot to play them.
- **`gx_corridors_256x256`:** no result file. Its log stops at round 372 with no error line, and the process was gone by 13:58; the lead needs to confirm whether they stopped it.

Also, the engine refuses any side under 7, so 5x5 and 4x200 cannot exist; I used 7x7, 7x200 and 200x7 instead.

Files are in:
- `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/unC-opus/` (scripts: `gen.py`, `health.py`, `detail.py`)
- `~/meow-redteam/maps/un2/uc_*.map` (the 11 new maps)
- `~/meow-redteam/solo/runs/` under `uc_mD17`, `uc_mir`, `uc_n*`, `uc_t7_*` (replays)
- `~/meow-redteam/solo/bots/uc_*` (test arms only)
