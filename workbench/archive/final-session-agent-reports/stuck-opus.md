# Reports sent to the lead by stuck-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 02:07:04 — Heads-up: dead-end pearl orbit in one14

stuck-opus heads-up: live one14 has a second orbit state, not portals. Short dragons (L2-3) circle a 2x2 block beside a pearl that sits in a dead-end cell (3 kelp sides) for 100-300 rounds: one14-c1 Around UNSW M1517691 dragon 31 r4-130 (pearls (33,21),(33,22) born r1-2, never eaten), Islands M1517687 dragons 230+484 r235-471 (pearl (39,18) age 155), Schooltime M1517694 dragon 91 r188-499. [M] 14 one14 games: 30-round no-eat loops = 9.8% of our dragon-rounds vs 5.6% of theirs; loops of 50+ rounds 6.3% vs 2.1%.
[C/E] Cause: the target BFS and EAT_FIRST still pick the pearl (target_reachable, main.cpp:4939, only knows closed rooms, not cul-de-sacs) while POCKET_KEEP_OUT (keep_out_of_pocket, :940-1045, live since one11) swaps the entering move for the next best one every turn. Turning POCKET_KEEP_OUT off is NOT the remedy (they would walk in and die); it needs a few lines in target_reachable, no single constant. Counts by version/map and the size of this cause follow.

---

## 2026-10-09 02:15:51 — stuck-opus final: no portal-size bug, big-map loops doubled

stuck-opus final: one14 has no second state of the portal rule's size, but it is not clean. On maps of 2,000+ cells our dragons spend 5.3% of their rounds in long no-eat loops against 2.1% for one11 and 1.4-1.6% for the opponents, and that came in with one12 and stayed after the portal rule left.
Ready to go live: nothing. No one-constant remedy is supported by this data. One check is worth a builder: TERRITORY_DECAY:0 on big maps (below).
How sure: counts high (193 online games, 122 local); the cause of the big-map rise is inference, not isolated. This corrects my heads-up, which called dead-end pearls "the" cause: they are one of three classes and the smaller part of the gap.

Detector [M]. Looping = a dragon's 30th and later round without an eat on 12 or fewer head cells, classed by its nearest pearl on a free path of 12 steps. Share of that side's dragon-rounds, us | them:
  version (games)   all maps    no Portals   2000+ cells   under 2000
  one11 (45)        2.1 | 1.2   2.2 | 1.2    2.1 | 1.4     2.2 | 1.0
  one12 (45)        4.3 | 1.6   3.5 | 1.4    4.4 | 1.6     2.5 | 1.3
  one13 (74)        4.4 | 1.3   3.4 | 1.2    4.7 | 1.4     2.0 | 1.1
  one14 (30)        3.5 | 1.6   3.7 | 1.4    5.3 | 1.6     2.0 | 1.3
Validation: it lights up on the Portals map (one11 0.5/0.2/1.0, one12 11.3/17.9/21.0, one13 23.4/12.3/15.9/24.6, one14 0.8/1.9) and locally (ladder_portals_1: one13 18.2%, one14 0.6%, 4 games each). It does NOT light up on Queen Of Spades (about 0 in every version, we have few dragon-rounds there) and Trauma is high in every version including one11 (wider measure 14-20%), so the portal rule's damage on those two was not loops.
Other patterns, one14, us | them: (b) no move or back-and-forth 0.0 | 0.0; (c) pearl within 10 and not approached for 15 rounds 0.4 | 0.4; (d) three of ours within 3 for 20 rounds 2.0 | 2.2; (e) death within 3 rounds of a split 39 | 24 per 100 splits (one11 35 | 30), the blocked-parent split already covered by splitdie and walls. None is an excess except (a).

The three classes of (a) in one14, us | them, on 2000+ cells in brackets:
1. Idle, no pearl in reach: 1.6 | 0.6 (2.6 | 0.8; one11 1.0). [C] survey_from main.cpp:5001-5029 gives no target when a mate is nearer (share 0), so the score is space and territory only (:7649) and FAR_GAIN (:7720) has nothing to pull to. Old base behaviour: old main does the same locally on Schooltime (7.7 | 11.8). [E] The rise since one12 points at TERRITORY_DECAY 16 (reach_discount :5501), the only one12 switch still live that touches every short dragon's score. Examples: Around UNSW M1517691 dragon 198 (L6) r141-321 round a 2x4 block; Schooltime M1517694 dragon 91 r188-499 and dragon 267 r341-499.
2. Orbit beside a pearl the dragon may not enter: 0.9 | 0.5 (1.3 | 0.5; one11 0.6). [C] entry_dead_end (:4818, used :7672) forbids the step and EAT_FIRST skips dead ends (:8106), but the target search still names that pearl: target_reachable (:4939) only knows closed rooms (pocket_size :5447), not cul-de-sacs. Old base behaviour, not a live switch; POCKET_KEEP_OUT is not the cause and must stay on. Examples: Around UNSW M1517691 dragon 31 r4-130 beside (33,21),(33,22), born r1-2; Islands M1517687 dragon 230 r235-471 beside (39,18), 155 rounds old; Trauma M1517697 dragons 5 (r75-187) and 40 (r156-268) beside eight pearls in two 2x2 rooms at (33-34,4-7), up to 191 rounds old. 71% of sampled cases are single cells with three kelp sides.
3. Yielding: enemy head within 6 0.4 | 0.2, mate nearer 0.3 | 0.2, neither 0.2 | 0.1. The last holds one portal form that survives in one14: Islands M1517687 dragon 122 r252-336 circles between pearls on (26,38) and (29,38), each a nook whose only way on is a portal. [E] an unknown portal exit adds no room (:5073-5079), so the nook counts as a dead end.

Local, live build: generated maps of 288-1536 cells in all 8 families loop 0.0-0.2% on both sides, so the local head-to-heads cannot see any of this. The "poor" family shows 27% idle only because no pearl is born (24x12: 0 births in 500 rounds, 4-4 draw). Ladder maps against old main: Islands 5.5 | 4.4, Schooltime 13.5 | 15.0, Slithery 2.2 | 0.8, Australia 1.1 | 0.3.

Verdict. Class 2 is a bug in the sense "no version should do this", but it is old, costs about 1% of dragon-rounds and needs about ten lines in target_reachable, no constant. Class 1 is inefficiency. The one constant worth a test is TERRITORY_DECAY:0: paired by map and opponent, one14 loops more than one11 in 8 of 8 big-map pairs (Around UNSW 0.8 to 5.4, Islands 3.5 to 8.4, Schooltime 6.5 to 11.5, Australia 0.2 to 1.9 against Cache). I have no evidence that it costs games (one14 won 7 of 15 against Cache, one11 4), so I am not asking for it live untested.
What would show this wrong: mNps against a TERRITORY_DECAY:0 build on ladder_schooltime_1, ladder_islands_1 and ladder_australia_1 with equal idle share on both sides.
Not checked: local games of the live build on 7x7, 64x64, 7x256 or 256x256 (none exist); one14-k1/c2/q1 had not arrived; the idle cause was not isolated; dragon 122's portal knowledge is inferred.

Files in ROOT/data/codex/astra/stuck-opus/: t-online.txt (pattern by map by version), t-local.txt and t-cls-local.txt (family, size), t-cls-map.txt, boards.txt (7x7 boards of five examples). Rerun on a new set: python3 -B data/codex/astra/stuck-opus/detect.py online <label>, then cls.py online ver.
