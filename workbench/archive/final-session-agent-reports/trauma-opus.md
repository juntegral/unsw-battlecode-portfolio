# Reports sent to the lead by trauma-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 04:50:44 — Trauma heads-up: unused pearl corridor

trauma-opus heads-up: on Trauma the opponent farms a dead-end corridor next to its start, we never enter our mirror of it [M, game 1523632].
Cache me: tiles (36,9)-(36,13)+(35,9) respawn at once; from r19 one dragon eats 2, splits, the stub dies on the wall, every 4 rounds a new L2 leaves (44 splits by r100, 78 pearls). Our mirror (11,10)-(11,14)+(12,14) holds 6 pearls untouched from before r32 to past r84 while our dragon walks past in column 10; we had 0 natural pearls until r83 and lost a L2 on a wall at r47. Suspect the pocket/dead-end target veto (TARGET_REACHABLE entry_dead_end main.cpp:4820/4925, POCKET_KEEP_OUT :943); testing one constant at a time now, not confirmed yet.

---

## 2026-10-09 04:56:36 — Trauma cause confirmed, PORTAL_FAR_DECAY test

trauma-opus heads-up 2: cause confirmed by one constant. The pull toward an unseen portal dies at 6.5 steps (target_bonus main.cpp:5601-5606, 260-40*dist; used at :7717), the portal to the pearl corridor is 8 steps from our start, so we drift round a barren home area and cross at r29-r85 (online) while Cache me / Preyas cross at r9 and eat at r19.
PORTAL_FAR_DECAY:13 (existing off switch, :349/:7714) on local Trauma vs m3base, both seats [M]: first portal jump r29 -> r9, first eat r39/r44 -> r19. But r100 pearls did NOT rise locally (17->15, 24->19; the local corridor has only 3 pearls at r19, supply is an estimate), so by your rule it is not "ready" yet. Other-map check (5 ladder + 2 gx, off vs on) is running now, table by 14:10.

---

## 2026-10-09 05:03:33 — PORTAL_FAR_DECAY:13 not ready, table

trauma-opus heads-up 3: not ready: PORTAL_FAR_DECAY:13 fails the other-map rule. Do not plan an upload around it.
Our natural pearls by r100, off -> on, one game each vs m3base seat 0 [M]: Australia 62->48, Default 95->73 (queen dead r136->r116), Queen of Spades 44->41 (units 17->12, queen alive->dead r87), Portals 114->115 (queen dead r115->r301), Stripes 46->64 (queen dead r83->alive). Trauma 17->15 and 24->19 (jump r29->r9 and first eat r39/44->r19 as intended, but the local Trauma file gives 3 of the 6 corridor tiles a 350-round respawn, online they refill within 4 rounds, so the local file cannot show the gain).
Last check running: the same switch capped to the opening (PORTAL_FAR_ROUNDS:30) on Trauma, Australia, Default, Queen of Spades; final report by 14:12 either way. Four games cannot make it "ready" by your rule.

---

## 2026-10-09 05:11:53 — trauma-opus final: cause found, not ready

trauma-opus final: cause of the Trauma starvation found and confirmed with one constant; nothing to upload.
not ready: PORTAL_FAR_DECAY:13 (alone, or with PORTAL_FAR_ROUNDS:30) fixes the timing on Trauma but lowers r100 pearls on Default by 23-29% and does not raise them on the local Trauma file.
How sure: cause high (4 online games + 2 local pairs agree); net value of the fix unmeasured, the local Trauma file cannot show it.

CAUSE
[M] Trauma's home area is nearly barren. The food is a 6-tile dead-end corridor reached only through one portal: ours (10,0)->(16,7), corridor (11,10)-(11,14)+(12,14); mirror (37,23)->(31,16), (36,9)-(36,13)+(35,9). Online its tiles refill within 4 rounds.
[M] Round of first crossing of that portal -> natural pearls by r100 (script tr.py / m.py, same both sides):
  1523632  us r83 -> 7     Cache me r9 -> 78
  1525842  us r29 -> 27    Preyas  r9 -> 69
  1527409  us r85 -> 9     SKKU    r63 -> 17
  1528866  us r61 -> 9     Cache me r9 -> 83
  Our two L2 scouts walk the home area, usually take the other portal (10,20)->(26,22) first (a poor room) at r25-r33; one L2 died on a wall there at r47/r49 in two games. The queen is not the difference: Cache me's queen also stays home at L4-6.
[C] The pull toward an unseen portal is target_bonus(dist, WEIGHT_PORTAL_SCOUT) = 0.40*(260-40*dist), zero from 6.5 steps (main.cpp:5601-5606, used :7717; constants :413 :414 :465). The portal is 8 steps from the start, so nothing pulls the scout to it. dist_portal is set only for scouts (:5076-5078, can_scout_portals :6062: length <= 6, not queen/leader/feeder).
[M] PORTAL_FAR_DECAY:13 (existing off switch, :349, :7714-7716; pull reaches 20 steps) on local Trauma vs m3base, both seats: first crossing r29 -> r9, first eat r39/r44 -> r19, total length at r25 8 -> 11. Same with PORTAL_FAR_ROUNDS:30 (seat 1).

HASH
all-off from my copy 92fb69564fbd OK. One17 values from my copy = d6d14e1f8f53, the same binary as mD17, so no replay comparison was needed. Source unchanged (diff empty, existing constants only). tr_pfd13 f67bb1b9b8b1, tr_pfd13r30 f9f17d57dcc9.

PER MAP, our natural pearls / units at r100, queen death round, vs m3base, one game each [M]
  map (seat)         off (mD17)        PFD:13            PFD:13 + ROUNDS:30
  Trauma (0)         17/8  q r415 L    15/8  alive L     -
  Trauma (1)         24/11 alive L     19/9  alive L     19/9  alive L
  Australia (0)      62/30 q r88 W     48/31 q r88 L     62/30 q r88 W (all columns equal to off)
  Default (0)        95/31 q r136 W    73/27 q r116 W    67/26 alive W (queen 93 at end)
  Queen of Spades(0) 44/17 alive W     41/12 q r87 W     44/17 alive W (all columns equal to off)
  Portals (0)        114/15 q r115 W   115/20 q r301 L   -
  Stripes (0)        46/9  q r83 W     64/15 alive W     -
  Trauma end totals us v them: off 14 v 112 and 25 v 109; PFD:13 67 v 76 and 46 v 39 (still lost on queen length).
[M] Why local Trauma shows no r100 gain: the file gives 3 of the 6 corridor tiles a 350-round respawn (TILE 36 10/36 11/35 9 and mirrors), the rest 6-16; the early scout finds 3 pearls, splits, and its L3 half dies on the corridor's end wall at r26.

NOT DONE
- No game against mD17 (my first batch failed: I wrote a log into the output folder; rerun went to m3base pairs only). No generated maps. So the head-to-head and gx columns are missing.
- TARGET_REACHABLE:false and POCKET_KEEP_OUT:false were built (tr_noTR, tr_noPK) but not played.
- Unexplained [M]: in 1528866 our L2 stood at (12,8), three steps from six corridor pearls, r67-r72, and walked away; another L2 circled (15-16,18-19) r45-r100. Rule not identified; my first heads-up's pocket-veto suspicion is unconfirmed.

WHAT WOULD SHOW IT WRONG
If a Trauma game where we cross at r9 still has under about 20 pearls by r100 online, the crossing time is not the cause. The Default drop is one deterministic game per arm; several seeds or seats could show it as noise, which I did not run.

Files: ROOT/data/codex/astra/trauma-opus/ (tr.py trace, m.py start table, t.py map table, g.zsh), runs ~/meow-redteam/solo/runs/tr_mD17_v3, tr_pfd13_v3, tr_pfd13r30_v3, bots tr_*. Nothing of mine is running.

---

## 2026-10-09 05:11:53 — closing summary

[result truncated — this drain's results exceeded 16000 characters; ask the agent for it via SendMessage]

---

## 2026-10-09 05:11:53 — Candidate SPLIT_KNOWN_TAIL:true, hash OK, testing

trauma-opus candidate (hash and identity OK, behaviour test running): SPLIT_KNOWN_TAIL:true, new off-by-default switch in ~/meow-redteam/solo/src/w-trauma/main.cpp (2 guarded lines in split_child_size + the constant). all-off 92fb69564fbd OK; one17 values from this source = d6d14e1f8f53 = the same binary as mD17; candidate bot tr_skt 224f9dd44f74.
What it stops [M+C]: every corridor harvest ends with an escape split (stub 2 + tail part 6); the newborn 6 does not know its tail yet, so split_child_size returns at `if (tail_index < 0) return child;` before the child-exit and room checks, and cuts off a 2 that faces the dead end and dies the same round. Online 1525842: such a death at (11,13) at r45, r58, r71, r84, r97 = 10 length thrown away by r100 with our total at 22. The switch makes a dragon that does not know its tail skip the regular split after round 0. On your veto question: none of POCKET_KEEP_OUT / TARGET_REACHABLE stops the harvest; the gate is harvestable() main.cpp:2439-2460 (outside: length <= 6, pearls >= 3, length + pearls > room), and our loop already runs, it is just 13 rounds per cycle and loses 4 per 6 eaten. Pairs by 14:30.

---

## 2026-10-09 05:14:22 — SPLIT_KNOWN_TAIL first pairs: fires as built

trauma-opus: SPLIT_KNOWN_TAIL:true does what it was built for; other maps running, verdict by 14:30. Clean 2-hunk diff against the CURRENT base (yours moved at 14:06, QUEEN_CORRIDOR_MATE/TREE): ROOT/data/codex/astra/trauma-opus/trauma-opus.diff.
[M] Trauma copy with the corridor refilling as online (my file solo/runs/tr_maps/ladder_traumafast_1.map = ladder_trauma_1 with the 12 corridor tiles set to "3 4"), seat 1 vs m3base, off -> on: wasted L2 deaths at the corridor's inner cell by r100 5 -> 0; r100 pearls 34 -> 40, units 11 -> 16, total length 29 -> 41; end 42 v 94 loss -> 75 v 84 win (queen 46 to 40).
[M] Standard ladder_trauma_1 seat 1: replay identical to mD17 until r182 (first blind split there: off loses the L2 the same round, on keeps the dragon at L5), so r100 numbers are equal (24/11). Caution: after the divergence our queen died at r396 in the on game (alive at 20 in the off game); one game, late, cause not traced.

---

## 2026-10-09 05:18:45 — SPLIT_KNOWN_TAIL passes other maps and head to head

trauma-opus: SPLIT_KNOWN_TAIL:true passes the other-map check and wins the head to head on the corridor map; start your own check now if you want it. Still running: head to head vs mD17 on Portals, Trauma, Australia, Default (both seats), result by 14:28.
[M] How often the waste happens online (60 of our games in one15-c1/p1/s1 + one16-c1, waste.py): 123 times for us (246 length), 35 for opponents; per game Trauma 10-16, Portals 3-11 (from r27, every 12 rounds), Australia 4-6.
[M] off -> on vs m3base seat 0, our pearls / units / total length at r100, queen death, result:
  Default, Queen of Spades, Stripes, gx_islands_24x12, gx_open_24x12: traces identical for the whole game (switch never fires).
  Australia  62/30/80 -> 64/32/85, queen r88 = r88, win = win (first difference r94, exactly the wasted split)
  Portals    114/15/40 -> 116/20/49, queen r115 -> r122, win -> LOSS (both queens dead, longest dragon 28-22 -> ?; end totals 51 v 53 -> 61 v 55)
  Trauma-fast seat 0  33/12/32 -> 39/14/37, loss -> win; seat 1  34/11/29 -> 40/16/41, loss -> win
  Trauma standard seat 1: equal to r182, then our queen dies r396 (alive at 20 in off), loss = loss
[M] Head to head tr_skt vs mD17 on Trauma-fast: seat 0 win 47 to 28 (81 v 64), seat 1 win 38 to 2 (91 v 43).
By your written rule it is "not ready" on one line only: Trauma r100 pearls rise 18%, not x2 (it removes waste, it does not make us arrive earlier). Flags: the Portals result flip and the late queen death on standard Trauma, one game each, not traced yet.

---

## 2026-10-09 05:26:18 — Caution on SPLIT_KNOWN_TAIL: Portals head to head negative

trauma-opus caution before you spend time on SPLIT_KNOWN_TAIL:true: the Portals head to head vs mD17 is against it at r100 in both seats, so I am leaning "not ready".
[M] Portals, same game, total length at r100 / r150: seat 0 skt 36 / 51 vs mD17 50 / 70; seat 1 skt 41 / 48 vs mD17 51 / 56; skt's queen died r138 and r145, mD17's was alive at r150 in both. Games went 1-1 by seat (seat A won both), as on Australia, Default and standard Trauma (all 1-1 by seat); only Trauma-fast went 2-0 for skt.
The other readings on Portals point the other way (vs m3base 114/15/40 -> 116/20/49 at r100; skt mirror 54 and 66 total at r100 vs mD17 mirror 44 and 38), so this is variance or a real cost I have not traced. Running a second seed of the Portals head to head now; final verdict by 14:32.

---

## 2026-10-09 05:26:18 — trauma-opus final 2: SPLIT_KNOWN_TAIL not ready

trauma-opus final (replaces my 14:07 report's verdict; its cause section stands): two findings, no upload.
not ready: SPLIT_KNOWN_TAIL:true. It removes a real waste and wins on the Trauma corridor, but in the head to head against mD17 on Portals it is behind (1 win 3 losses, r100 total length 45 v 51.5 on average), and Trauma r100 pearls rise 18%, not x2. Also not ready: PORTAL_FAR_DECAY:13 (14:07 report).
How sure: the waste and its removal are measured and solid; the Portals cost is four games, cause not traced.

YOUR QUESTION (which veto stops a 4+ from harvesting the corridor)
[C] None of POCKET_KEEP_OUT / TARGET_REACHABLE / entry_dead_end. The gate is harvestable(), main.cpp:2439-2460: from outside length <= 6 (HARVEST_MAX_LENGTH), pocket pearls >= 3, and length + pearls > room (:2449); inside length <= 8. Our loop does run online (1525842: full 6-pearl trips at r39, r52, r65, r77...).
[M] Why it is slower than Cache me: they go in with 2, eat 2, split, 4 rounds a trip, one L2 lost per 4 eaten. We eat all 6, escape-split 2+6 (escape_child_size :2402), and then the newborn 6 splits again the same turn: split_child_size returns at `if (tail_index < 0) return child;` (:2328 in the base I copied) before the child-exit and room checks (:2333), cutting off a 2 that faces the dead end and dies that round. So 4 lost per 6 eaten, 13 rounds a trip.
[M] That wasted death, online, 60 of our games (one15-c1/p1/s1, one16-c1; waste.py): 123 for us, 35 for opponents. Per game: Trauma 10-16, Portals 3-11 (from r27, every 12 rounds), Australia 4-6.

CANDIDATE SPLIT_KNOWN_TAIL:true (a dragon that does not know its tail skips the regular split after round 0)
Hash: all-off 92fb69564fbd OK; one17 values from my source = d6d14e1f8f53 = the mD17 binary; tr_skt 224f9dd44f74. Diff against your current base (2 hunks, 4 lines): ROOT/data/codex/astra/trauma-opus/trauma-opus.diff. My w-trauma copy predates your 14:06 base change.
Mechanism count, wasted deaths per game off -> on vs m3base: Trauma-fast 18 -> 0 and 11 -> 0, Portals 14 -> 1, standard Trauma 1 -> 0, Australia 1 -> 1.
vs m3base, our pearls / units / total length at r100, queen death, result (one game each):
  Default, Queen of Spades, Stripes, gx_islands_24x12, gx_open_24x12: whole-game traces identical
  Australia (0)     62/30/80 -> 64/32/85    q r88 = r88     win = win
  Portals (0)       114/15/40 -> 116/20/49  q r115 -> r122  win -> loss (both queens dead, longest dragon)
  Trauma-fast (0)   33/12/32 -> 39/14/37    alive = alive   loss -> win
  Trauma-fast (1)   34/11/29 -> 40/16/41    alive = alive   loss -> win
  Trauma std (1)    24/11/27 = 24/11/27     alive -> q r396 loss = loss (identical to r182)
Head to head tr_skt vs mD17 (the candidate's total length at r100 v mD17's in the same game):
  Trauma-fast: 2-0 (36 v 21, 21 v 30; ends 81 v 64 and 91 v 43)
  Portals seed 1: 1-1 by seat (36 v 50, 41 v 51; skt queen dead r138, r145). Seed 2: 0-2 (56 v 52, 47 v 53; skt queen dead r275, r476). All four decided by longest dragon.
  Australia 1-1, Default 1-1, standard Trauma 1-1: seat decided each pair.
"Trauma-fast" is my own file (solo/runs/tr_maps/ladder_traumafast_1.map: ladder_trauma_1 with the 12 corridor tiles set to refill "3 4" as online); it is a fixture, not a ladder map.

WHAT WOULD SHOW IT WRONG / WHAT IS MISSING
- Portals: if more seeds bring the head to head back to level, the cost was variance. I did not find why the longer newborn does worse there (guess [E]: at length 5-6 it fails harvestable()'s length and fill conditions more often).
- Not run: skt on generated maps with portals bigger than 24x12, Queen of Spades / Stripes head to head.
- A narrower form worth trying after the deadline: skip the blind split only when the dragon was born in a dead end.

Files: ROOT/data/codex/astra/trauma-opus/ (tr.py, m.py, t.py, waste.py, wastel.py, div.zsh, g.zsh, trauma-opus.diff); runs tr_mD17_v3, tr_skt_v3, tr_skt_vD, tr_skt_vS, tr_mD17_vD, tr_pfd13*; bots tr_*. Nothing of mine is running.

---

## 2026-10-09 05:26:18 — closing summary

Final report sent to the lead at 14:25 KST, ahead of the 14:35 cut: two causes found, two candidates tested, neither ready, so nothing to upload from me.

**Not ready: `SPLIT_KNOWN_TAIL:true`** (new off-by-default switch, 4 lines). It removes a real waste and wins on the Trauma corridor, but against the live bot on Portals it is behind, and Trauma r100 pearls rise 18%, not x2. `PORTAL_FAR_DECAY:13` from the earlier report is also still not ready.

**The lead's question: which veto stops a dragon of 4 or longer harvesting the corridor**
- None of `POCKET_KEEP_OUT`, `TARGET_REACHABLE` or `entry_dead_end`. The gate is `harvestable()` at `main.cpp:2439-2460`, and our harvest loop does run online.
- It is slower than Cache me's because after eating all six pearls we escape-split 2+6, and the newborn 6 immediately splits again. `split_child_size` returns at `if (tail_index < 0) return child;` before the child-exit and room checks, so it cuts off a 2 that faces the dead end and dies that round.
- That costs us 4 length per 6 eaten at 13 rounds a trip, against their 2 lost per 4 eaten at 4 rounds a trip.
- The wasted death happened 123 times for us and 35 for opponents across 60 online games: Trauma 10-16 per game, Portals 3-11, Australia 4-6.

**What the candidate did**
- **Hash and identity:** all-off is `92fb69564fbd`; the one17 values from my source give `d6d14e1f8f53`, the same binary as mD17.
- **Waste removed:** wasted deaths per game against m3base fell from 18 and 11 to 0 on the fast-corridor Trauma copy, and from 14 to 1 on Portals.
- **Other maps against m3base:** Default, Queen of Spades, Stripes and two generated maps were trace-identical for the whole game. Australia and Portals were slightly up at r100, though the Portals result flipped from win to loss on the longest-dragon tie-break.
- **Fast-corridor Trauma against m3base:** total length at r100 went 32 to 37 and 29 to 41, and both seats went from loss to win.
- **Standard Trauma against m3base:** identical until r182, then our queen died at r396 where she had survived with the switch off. One game, not traced.

**Head to head against mD17**

| Map | Result for candidate | Total length at r100, candidate v mD17 |
|---|---|---|
| Fast-corridor Trauma | 2-0 | 36 v 21, 21 v 30 |
| Portals, seed 1 | 1-1 by seat | 36 v 50, 41 v 51 |
| Portals, seed 2 | 0-2 | 56 v 52, 47 v 53 |
| Australia, Default, standard Trauma | 1-1 each, seat decided | not compared |

The fast-corridor Trauma map is my own fixture (`ladder_trauma_1` with the 12 corridor tiles set to refill as they do online), not a ladder file.

**Not done:** I did not find why the longer newborn does worse on Portals. I also did not run the candidate on larger generated maps with portals, or head to head on Queen of Spades and Stripes.

The diff is against the lead's current base, which changed at 14:06; my `w-trauma` copy predates that. Nothing of mine is still running, and I made no git changes.

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trauma-opus/`:
- trauma-opus.diff
- tr.py
- m.py
- t.py
- waste.py
- wastel.py
- div.zsh
- g.zsh

Source is `~/meow-redteam/solo/src/w-trauma/main.cpp`, runs are under `~/meow-redteam/solo/runs/tr_*`, and the fixture map is `~/meow-redteam/solo/runs/tr_maps/ladder_traumafast_1.map`.
