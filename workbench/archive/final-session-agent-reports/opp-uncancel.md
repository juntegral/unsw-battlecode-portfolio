# Reports sent to the lead by opp-uncancel

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:39:58 — uncancelables first report: no rematch, queen survival decides

opp-uncancel 1/2 (the uncancelables, 899): NO rematch. Per-game win chance about 40% [M: 4 of 10 as seat A with one15/one18; one18 alone 2 of 5], so 3+ of 5 is about 32% [E].
Decides our games: whether OUR queen lives. Queen alive at end 6 games = 6 wins; queen dead 7 games = 1 win 6 losses [M]. Their queen dies in 9 of 13 anyway.
Constant for the last upload: none (nothing I can stand behind untested; see last line).

13 games [M], same scan both sides. endQ us/them; r100 = dragons/total length/pearls eaten, us | them
1485483 10-08 one8  B Trophy   WIN elim r62   3/0  ended r62
1485484 10-08 one8  B PrisDil  WIN elim r41   3/0  ended r41
1485485 10-08 one8  B Autarky  WIN elim r224  5/0  22/60/71 | 11/26/36
1524544 03:21 one15 A Trophy   LOSS elim r194 0/0  11/27/72 | 24/61/66
1524545 03:21 one15 A Portals  LOSS queen     0/80 16/42/104 | 4/11/5
1524546 03:21 one15 A PrisDil  WIN elim r99   3/0  ended r99
1524547 03:21 one15 A Default  WIN elim r250  0/0  18/51/48 | 14/35/29
1524548 03:21 one15 A TowerDef LOSS elim r183 0/0  4/9/11 | 21/51/59
1535563 14:28 one18 A Trauma   WIN queen      46/18 10/26/29 | 8/19/48
1535564 14:28 one18 A Devil    LOSS elim r260 0/0  2/4/43 | 28/68/85
1535565 14:28 one18 A PrisDil  WIN elim r323  2/0  7/16/16 | 4/9/10
1535566 14:28 one18 A Default  LOSS queen     0/24 17/42/33 | 14/37/21
1535567 14:28 one18 A TowerDef LOSS elim r84  0/3  ended r84 (r75: 1/3 | 9/23)
Overall 7-6. Seat A 4-6, seat B 3-0 (all one8, unranked). Maps: PrisDil 3-0, TowerDef 0-2, Trophy 1-1, Default 1-1.

Losses by class: Trophy = queen rammed from a one-way place (r78, L2, stepped into a 1-exit cell with an L3 at gap 2; their queen was dead since r20). Portals = queen self-trap (r31, portal exit with 0 free cells; one15, before QUEEN_NO_BLIND_PORTAL). TowerDef x2 = out-eaten from r25 (pearls r0-100: 11 v 59, 1 v 32) then L2 queen rammed in the open (r53 by L3 paying 1 from gap 2; r69 by L2). Devil = out-eaten from r50 (8 dragons at r50, 2 at r100; they rammed 12, we 2), lone L2 queen rammed in the open r260 with their queen dead since r79. Default = queen rammed in the open r259 (L3, two L2 heads on her diagonals).
Common to all 5 ram deaths [M]: on her last turn every free step ended next to a short head; the lost move was one earlier, letting an L2/L3 head stand at gap 2 at her turn start, with no mate within 4 in 4 of 5.
How they win: everything split to L2-3 all game (their longest is 3-4), head-on rams they start: Default r100+ 83 v 9, Trophy r50-200 35 v 3. Our wins: our L2-4 hunters rammed their queen from gap 1-3 at r16/r24/r41/r52/r96, she self-trapped at r66/r79/r119.
Untested lead only [C/E]: with REACH_EATS the queen marks every cell within QS_PAY_REACH:4 of any head, so inside a swarm all steps look equally bad. More in 2/2 by 14:46.

---

## 2026-10-09 05:39:58 — uncancelables final: no rematch, no constant

opp-uncancel 2/2 FINAL (the uncancelables, 899): NO rematch. About 40% per game [M: 4 of 10 as seat A on one15/one18; one18 alone 2 of 5], about 32% to take 3 of 5 [E].
Decides it: our queen alive at the end = 6 of 6 won; our queen dead = 1 of 7 won [M, 13 games]. They do not out-play us, they outlast our queen.
Constant for the last upload: NONE. I withdraw the QS_PAY_REACH lead from 1/2: that constant is the split/exposed check (main.cpp:6346); the queen's move reach under REACH_EATS is QUEEN_REACH_MAX (4354). Not tested, do not act on it.

Table in 1/2 stands (13 games, 7-6; seat A 4-6, seat B 3-0 all one8 unranked; PrisDil 3-0, TowerDef 0-2, Trophy 1-1, Default 1-1). No newer battle on disk as of 14:38.

Loss classes for your tally (6): queen rammed in the open 4 (TowerDef 1524548 r53, TowerDef 1535567 r69, Devil 1535564 r260, Default 1535566 r259), queen rammed from a one-way place 1 (Trophy 1524544 r78), queen self-trap 1 (Portals 1524545 r31, one15, portal exit with 0 free cells). Underneath three of the four open rams: out-eaten first (TowerDef from r25 both times: 0 and 1 pearls in r0-50 while they took 4 and 6 then 22-34 in r50-75; Devil from r50: 8 dragons to 2 by r100).

What they do [M]:
- Queen is split to L2 at round 0 or as soon as she reaches 4 (Devil: r0, r23, r39, r56, r76) and stays 2-3; everything else is L2-3 too. No guard: their queen died in 9 of 13 (our ram 6, self-trap 3).
- They start the head-on rams: Default r100+ 83 v 9, Trophy r50-200 35 v 3, Devil r50-100 12 v 2. One for one, paid with 2-part dragons.
- Our queen is killed by L2 (free step, gap 1) 3 times or L3 (pays 1, gap 2) 2 times. On her last turn every free step ended next to a head in 5 of 5; no mate within 4 in 4 of 5. In 2 of 5 she had stepped toward the heads when a step keeping gap 5+ was free (Default r257-258: took gap 3/3 over gap 5/5; TowerDef 1524548 r52: gap 4 over gap 6).
- Once our queen is dead they feed theirs: Portals 3 to 80, Default 3 to 24. We then had a head within 5 of her on 118 of 240 turns (Default, one18) and 300 of 468 (Portals, one15), within 2 on 9 and 78, and never killed her.

What of ours beats them: the early queen hunt (ram at r16, r20, r24, r41, r52, r96 by L2-4 from gap 1-3), then elimination; and a queen that just stays alive (Trauma 46 v 18).

Looked at and rejected: QUEEN_AVENGE:8 to a larger value (only dragons within 8 of her hunt after our queen dies, main.cpp:1771). Right direction by the rules against anyone, but the counts above say range is not what fails, the kill is; so no.
Not checked: where their queen sits on the map, whether those 9 / 78 close turns were rammable, why we find no pearls on TowerDef, Elo points at stake.
Scripts: data/codex/astra/opp-uncancel/ (tab.py, qlast.py, qco2.py, deaths.py).

---

## 2026-10-09 05:47:33 — closing summary

The uncancelables (team 899): don't request a rematch, and nothing from this analysis is worth the last upload. Both messages went to team-lead (first at about 14:36, final at about 14:38 KST), and no new battle against 899 had landed by 14:44:54.

- **Rematch: no.** We win about 40% of games against them (4 of 10 as seat A on one15/one18; one18 alone 2 of 5). That gives roughly a 32% chance of taking 3 of 5.
- **What decides it: whether our queen survives.** When our queen was alive at the end we won 6 of 6; when she was dead we won 1 of 7 (13 games, 7-6 overall).
- **Constant: none.** I looked at raising `QUEEN_AVENGE` above 8 and rejected it: in the Default loss on one18 we had a head within 5 of their queen on 118 of 240 turns after ours died and still never killed her, so range is not what fails. I also withdrew a `QS_PAY_REACH` lead from my first message, because I had attributed it to the wrong part of the code.

Loss classes for the tally (6 losses):

| Class | Count | Games |
|---|---|---|
| Queen rammed in the open | 4 | Tower Defense 1524548 (r53), Tower Defense 1535567 (r69), Devil 1535564 (r260), Default 1535566 (r259) |
| Queen rammed from a one-way place | 1 | Trophy 1524544 (r78) |
| Queen self-trap | 1 | Portals 1524545 (r31, one15, portal exit with no free cells) |

Three of the four open rams came after we were already out-eaten: Tower Defense from r25 both times, Devil from r50.

How they beat us:
- **Swarm of short dragons.** Their queen is split to length 2 at round 0 or as soon as she reaches 4, and everything else stays at 2–3. Their own queen is unguarded and died in 9 of 13 games.
- **They start the head-on rams.** Default from r100: 83 to our 9; Trophy r50–200: 35 to 3; Devil r50–100: 12 to 2.
- **Our queen dies alone.** In all 5 ram deaths every free step on her last turn ended next to an enemy head, and in 4 of 5 she had no mate within 4. In 2 of 5 she had stepped toward the heads when a step keeping a gap of 5 or more was free.
- **After our queen dies they feed theirs.** She grew from 3 to 80 on Portals and 3 to 24 on Default.

What of ours beats them is the early queen hunt (rams at r16–r96 by our length 2–4 dragons, then elimination) and simply keeping our queen alive (Trauma, 46 to 18).

Not checked: where their queen sits on the map, whether the close turns near their queen were actually rammable, why we find no pearls on Tower Defense, and the Elo points at stake.

Scripts are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/opp-uncancel/` (`tab.py` for the table, `qlast.py` for the queen's last turns, `qco2.py` for queen exposure, `deaths.py` for ram counts). No code was changed and nothing was committed.
