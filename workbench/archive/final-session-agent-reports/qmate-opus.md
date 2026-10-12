# Reports sent to the lead by qmate-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 04:56:36 — qmate heads-up: cause is queen-side, switch built

qm heads-up: in the qexit rows the mate rarely MOVES into the box; the queen moves in beside a mate that is already there. [M] Of 24 boxed-on-own-move deaths with a mate as a wall (286 rows, qmate-opus/pick.py): 19 are class BQ (her own move left 0 free cells, f0a=0), 3 H, only 2 BM (a mate took the last cell); the mate wall is a body or tail in 17 and a head in 7. Maze 1527400 r151-152 [M]: queen 0 stepped W from (29,11) into (28,11), a cell whose only exit is a portal to (34,5); dragon 177 (L2) was in a 1-wide corridor (34,2)->(34,5), walls E and W, so (34,5) was its only move at r150 and r151, and it was 13 cells from her so keep_queen_exit never saw her (queen must be in ct.get_tiles(), main.cpp 1152-1165; strict also needs manhattan <=2, line 1281, which a portal neighbour fails).
Built QUEEN_ROOM_MATES (mate side only, any length, single-step alternative): all-off hash 92fb69564fbd OK, one17-values binary is byte-identical to mD17 (d6d14e1f8f53). Pairs are running now; the queen-side half (her free-cell count) is NOT built, and it is the half the counts point at. Expect "small effect" at best; final by 14:15.

---

## 2026-10-09 05:11:53 — qmate final: not ready, cause is queen-side

qm FINAL: not ready: QUEEN_ROOM_MATES. Do not put it live.
Built the mate-side half only (any-length mate will not end its move beside the queen's head when she is left under 2 free cells, if it has another free single step). In 9 complete on/off pairs the thing it targets (boxed with a mate as a wall) happened 0 times off and 0 times on, and the queen died earlier with it on in 4 of the 6 pairs that diverged. Fairly sure of "not ready"; one seed per map, so the harm itself is not proven.

Hash and identity: qm_off = 92fb69564fbd OK. qm_17 (one17 values) binary = d6d14e1f8f53, byte-identical to mD17, so I did not play the 4 cmp games.

Cause (task 1), [M] unless marked:
- 286 qexit rows, 24 boxed-on-own-move deaths with a mate as a wall: 19 BQ (her own move or split left 0 free cells; the mate was already there), 3 H, 2 BM (mate took the last cell). Mate wall is a body or tail in 17, a head in 7. So mostly she walks in beside a standing mate; the live rules only check the mate's move.
- Maze 1527400: r151 queen 0 stepped W from (29,11) to (28,11) with (30,11) free; (28,11) has walls N and S and one exit, a portal to (34,5). Dragon 177 (L2) was in a 1-wide corridor (34,2)->(34,5), walls E and W, so S was its only move at r150 and r151 (its last choice was r149: pearl W or corridor S). It was 13 cells from her. [C] keep_queen_exit needs her head in its own 7x7 (solo main.cpp 1152-1165, returns if not seen); strict's near test is manhattan (1275-1283), which a portal neighbour fails; with no alternative the plain rule returns (about 1325).
- Devil 1518919 r40: 1-wide corridor x=17. Mate 14 (L4-5, too long for strict) entered from the south at r38 for a pearl when she was 3 cells away; she walked on to (17,6) at r39, head to head, 0 free cells by her own move.
- Portals 1513846 r215 (one13): she took the portal at (3,14) into (27,1) (walls E, S); mate 8 (L2) at (26,0) had walls N, W, so (26,1) was its only move and it closed her last cell.
- Common to all three: the mate had no other move or was there first. A rule that needs "the mate has another legal move" fires in none of them. The queen-side half (her own free-cell count, through portals, two steps ahead) is what the counts ask for; I did not build it, there was no time to verify it.

Pairs, seed 7, side 0, off = qm_17, on = qm_on (pearls eaten r1-100 / dragons at r100 / queen):
vs mD17        off              on
gx_corridors   133/24 alive     133/24 alive     same game
gx_rooms       38/3  r34 rammed 38/3  r34 rammed same game
islands        180/39 r195 rammed   167/34 r81 boxed, own body (pearls -7%)
maze           69/30 r209 rammed    69/30 r395 boxed, own body
portals        251/22 alive L12, won   251/22 r161 boxed by own split, lost
slithery       433/52 r311 rammed   436/60 r356 rammed
vs m3base
maze           81/29 r80 boxed own  81/29 r80 same game
portals        271/28 alive L37     271/28 r206 boxed by own split
slithery       399/61 alive L65     399/61 r447 rammed
Not finished by the cut: default (both opponents), islands on vs m3base, both gx maps vs m3base. Firing count: the bot's log lines are not kept in local replays or engine.log, so I only have the first differing 25-round snapshot (r50 islands and slithery, r150 portals, r175 maze vs mD17; r200 portals and slithery vs m3base).

What would show this wrong: more seeds where the on arm's Portals queen survives as often as off (2 of 2 died here against 0 of 2), or online games where a mate with a free alternative closes her in.
Files: ROOT/data/codex/astra/qmate-opus/ (pairs.txt, summ.py, pick.py, look3.sh, qmate-opus.diff), source ~/meow-redteam/solo/src/w-qmate/main.cpp, bots qm_off, qm_17, qm_on. All my processes are stopped.

---

## 2026-10-09 05:11:53 — closing summary

**not ready: QUEEN_ROOM_MATES** — do not put it live. The final report went to team-lead at 14:11 KST, before the cut.

**What I built:** only the mate-side half. A mate of any length will not end its move beside the queen's head when that leaves her fewer than two free cells, provided it has another free single step. The queen-side half (her own free-cell count) is not built.

**Hash and identity:** all-off is `92fb69564fbd`, as required. The one17-values build is byte-identical to `mD17` (`d6d14e1f8f53`), so I did not play the four comparison games.

**Cause:** mostly the queen walks in beside a mate that is already there; the mate rarely moves in.
- **Counts:** of 24 boxed-on-own-move deaths with a mate as a wall (286 rows), 19 are her own move or split leaving 0 free cells, 3 are her ramming a head, and only 2 are a mate taking her last cell.
- **Maze 1527400:** at r151 the queen stepped from (29,11) into (28,11), whose only exit is a portal to (34,5), while (30,11) was free. Dragon 177 was in a one-wide corridor, so (34,5) was its only move, and it was 13 cells from her. `keep_queen_exit` needs her head in the mate's own 7x7 view (`main.cpp` 1152-1165), and the strict test uses manhattan distance (1275-1283), which a portal neighbour fails.
- **Devil 1518919 r40:** a mate of length 4-5 entered a one-wide corridor from the far end for a pearl; she walked up to its head on her own move.
- **Portals 1513846 r215:** she took a portal into a two-cell pocket; the 2-long mate beside it had only one legal move and closed her last cell.

In all three the mate had no other move or was there first, so a rule that needs "the mate has another legal move" would not fire.

**Pairs** (seed 7, side 0, one game each; pearls eaten r1-100 / dragons at r100 / queen):

| Opponent | Map | Off | On |
|---|---|---|---|
| mD17 | gx_corridors | 133 / 24, alive | same game |
| mD17 | gx_rooms | 38 / 3, r34 rammed | same game |
| mD17 | islands | 180 / 39, r195 rammed | 167 / 34, r81 boxed by own body |
| mD17 | maze | 69 / 30, r209 rammed | 69 / 30, r395 boxed by own body |
| mD17 | portals | 251 / 22, alive, won | 251 / 22, r161 boxed by own split, lost |
| mD17 | slithery | 433 / 52, r311 rammed | 436 / 60, r356 rammed |
| m3base | maze | 81 / 29, r80 boxed by own tail | same game |
| m3base | portals | 271 / 28, alive | 271 / 28, r206 boxed by own split |
| m3base | slithery | 399 / 61, alive | 399 / 61, r447 rammed |

- **Target event:** boxed-with-a-mate deaths were 0 with the switch off and 0 with it on, so there was nothing to reduce.
- **Queen deaths:** she died earlier with the switch on in 4 of the 6 pairs that diverged, including Portals against both opponents (alive off, boxed on).
- **Pearls:** the largest drop by r100 is 7 percent, on Islands.
- **Not finished by the cut:** default against both opponents, the Islands on-arm against m3base, and both generated maps against m3base.
- **Firing count:** not measured, because the bot's log lines are not kept in local replays; I only have the first 25-round snapshot where the two games differ.

One seed per map means the harm is not proven, but the "ready" bar is not met either way.

Everything is in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qmate-opus/` (`pairs.txt` is the table, `qmate-opus.diff` the change). The source is `~/meow-redteam/solo/src/w-qmate/main.cpp`, and the bots are `qm_off`, `qm_17` and `qm_on`. All my processes are stopped.
