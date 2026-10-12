# Reports sent to the lead by review19-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 05:30:44 — Heads-up: slithery slower early for B19

review19 heads-up (verdict follows by 14:36): on a big long map the candidate is slower early, and I cannot tell change 2 from change 4 without one more game.
[M] ladder_slithery_fight_1 (63x27 = 1701 cells, long, so centre pull is newly ON with CENTER_MAX_CELLS 100000), seed1 side0 vs m3base: mD18 u50=45 T100=163 T200=244 deaths len<=2 by r100 = 126; mB19 u50=36 T100=149 T200=213 len<=2 deaths = 145. Result went the other way (mD18 lost "longer queen 22 to 0", mB19 won "longest 82 to 43"), one game each.
[M] Your battery: A19 and B19 are identical to r200 everywhere except ladder_portals_1 (B: wall deaths by r100 41 -> 26, u100 15 -> 20, T100 40 -> 49, but B lost 44-39 where A won on queen 5-0). ladder_maze_1 (1152 cells, long, pull newly on) D18 -> A19 is level (T100 82 -> 86, T200 174 -> 168).
My 6-game budget is used (ub_deadend, ub_spiral, slithery, each mB19 + mD18; runs in solo/runs/rv19_mB19, rv19_mD18). The one game that separates it: mA19 on ladder_slithery_fight_1 seed1 side0 vs m3base (about 10 s). If mA19 shows u50 near 45, the drop is SPLIT_KNOWN_TAIL; if near 36, it is the centre pull on big long maps. Say the word and I run it, or run it yourself.

---

## 2026-10-09 05:33:12 — Verdict: SHIP A, without SPLIT_KNOWN_TAIL

SHIP A (without SPLIT_KNOWN_TAIL) - nothing in 1, 2, 3 breaks; 4 has a small proven gain and an unseparated early-growth drop on a big map, so it is the one to leave out unless one more game clears it.
Lines are in src/w-one19/main.cpp. [M] measured, [C] code, [E] inferred.

4 SPLIT_KNOWN_TAIL
[C] No new no-action path: 2353 returns 0 like a dozen other reasons; 1957 falls on to late_escape and the normal move, 6023 (queen_act) carries on.
[C] Tail is unknown only while trail.size() != length (2851); the trail gains at least one cell a turn and is rebuilt from vision (2900), so it cannot stay unknown for good unless the dragon eats every turn while its body is not traceable.
[M] In your battery A19 and B19 are identical to r200 on every map but ladder_portals_1: wall deaths by r100 41 -> 26, u50 12 -> 10, u100 15 -> 20, T100 40 -> 49; B then lost 44-39 on longest dragon where A won on queen 5-0 (one game).
[M] ladder_slithery_fight_1 (1701 cells), seed1 side0 vs m3base, mD18 -> mB19: u50 45 -> 36, T100 163 -> 149, T200 244 -> 213, deaths of length <= 2 by r100 126 -> 145. Result went B's way (mD18 lost on queen 22-0, mB19 won on longest 82-43).
[E] The u50 dip has the same shape as on portals (12 -> 10), so I read it as change 4, not the centre pull; not separated. The gain it buys is about 2 stubs a game (123 in 60). Clearing game: mA19 on that map, same seed, about 10 s (my 6 are used); u50 near 45 = it is change 4, near 36 = it is change 2 and B is as good as A.

1 QUEEN_DEAD_ALL removed
[M] Recounted your 20 pairs from result.txt: wins 8 -> 12, no pair worse (ua_chain_448 and ub_tworooms flip L -> W on both seats; ub_room3 lost on both seats in both arms).
[M] ub_spiral (578 cells) and ub_deadend, mB19 vs mD18: same result and same counts to r200. On ub_deadend both arms eat 0 pearls in 500 rounds (draw 4-4): the stuck-in-box case is still there on that map, in the live bot too.
[C] What the queen loses on maps of 600 cells or fewer with an open home: the 6000 penalty for room under length + 8 (7707) and for known room under length + 2 (7711), dead-end detection with unknown tail (4849, 7703), and she may now harvest pockets (2469). [E] POCKET_KEEP_OUT and the corridor guard cover entry; no game showed her dying in a pocket.

2 CENTER_MAX_CELLS 100000
[C] 616: the pull is now on for every map with width >= 2 x height at any size (TR_CENTER_ORIENT is off, so tall maps get nothing): 40 per cell, dragons of 4 or shorter, first 60 rounds, only with no pearl or hot target (7787).
[M] ladder_maze_1 (1152 cells, newly on) D18 -> A19: T100 82 -> 86, T200 174 -> 168, level. Slithery as above, confounded with 4. ladder_trauma_1 not played.

3 QUEEN_NO_RAM
[C] No new no-action path: the fall-through after 1860 already existed when hunt_path and ram_path both failed.
[C] Not complete: on the trapped turn queen_wary() is false, so mark_trade_targets spares nobody (4580), and for a queen of 4 or shorter pick_direction scores the single step into a trade-target enemy head at TRADE_REWARD 2500 (8145) and pulls toward it (7902). It only narrows one18, so it cannot be worse than live on this point.
[E] Cost: a queen that really is lost no longer takes an enemy head with her.

Runs: ~/meow-redteam/solo/runs/rv19_mB19, rv19_mD18. Scripts: unsw-swarm/data/codex/astra/review19-opus/ (snap.py, qda.py).
Slip: the readers wrote o1_local-*.jsonl caches into the dossier OUT folder, and two failed launches left empty logs in my folder.

---

## 2026-10-09 05:33:12 — closing summary

Verdict sent to the lead at about 14:32 KST: **SHIP A (without SPLIT_KNOWN_TAIL)**. Changes 1, 2 and 3 showed nothing that breaks; change 4 has a small proven gain and an early-growth drop on one big map that I could not attribute.

- **Change 4 (SPLIT_KNOWN_TAIL):** it creates no path without an action, and the tail cannot stay unknown for long.
  - In the lead's battery A19 and B19 match to r200 on every map except `ladder_portals_1`. There wall deaths by r100 fell 41 → 26 and total length at r100 rose 40 → 49, but B lost 44–39 where A won on queen 5–0 (one game).
  - On `ladder_slithery_fight_1` (1701 cells), mD18 → mB19 gave dragons at r50 45 → 36, total length at r100 163 → 149 and at r200 244 → 213. mB19 still won that game where mD18 lost.
  - Whether that dip comes from change 4 or the centre pull is not separated; I read it as change 4 because portals shows the same shape. One mA19 game on that map and seed would settle it.
- **Change 1 (QUEEN_DEAD_ALL removed):** I recounted the 20 pairs: wins 8 → 12, no pair worse. `ub_spiral` and `ub_deadend` gave the same result in both arms. On `ub_deadend` both arms eat 0 pearls in 500 rounds, so that stuck-in-box case exists in the live bot too.
- **Change 2 (CENTER_MAX_CELLS 100000):** the centre pull is now on for every map at least twice as wide as tall, at any size (line 616); tall maps get nothing. `ladder_maze_1` is level between D18 and A19; `ladder_trauma_1` was not played.
- **Change 3 (QUEEN_NO_RAM):** it creates no path without an action, but it is incomplete. A trapped queen of 4 or shorter still gets `TRADE_REWARD` for a single step into an enemy head in `pick_direction` (line 8145). It only narrows one18, so it cannot be worse than live on this point.

I used all six games and did not run the seventh that would separate changes 2 and 4; I asked the lead and had no reply before sending.

Two side effects outside my folder: the replay reader wrote `o1_local-*.jsonl` cache files into the dossier output folder, and the engine required game outputs under `~/meow-redteam/solo/runs/`.

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/review19-opus/`:
- `snap.py`
- `qda.py`
- `play5.sh`
- `play6.sh`

Game runs are in `~/meow-redteam/solo/runs/rv19_mB19/` and `~/meow-redteam/solo/runs/rv19_mD18/`.

---

## 2026-10-09 05:33:12 — Verdict: SHIP C

SHIP C
1. Portals question, no: [M] in your st_ games mC19 and mA19 on ladder_portals_1 have identical first 30 rounds on both seats (same eats by r30, 35 and 33; same death list, first deaths r12 and r11, none at r9; same dragons at r25, 9 and 7) and identical final results. The lift needs 2 or fewer dragons at round 20 or later, and we have 9 and 7 at r25, so it never fires there. ladder_stripes_1 is also identical C = A on both seats.
2. [M] ua_boxnp_320: the lift fires (eats by r30 0 -> 5 and 0 -> 3, dragons at r50 1 -> 2 and 1 -> 3) but mC19 is still eliminated on both seats (r58 and r91; mA19 and mD18 at r56 and r57). Not the win the ban-off arm gave: harmless, incomplete.
3. [C] Line 8111 has no upper round: any time from round 20 on that our side is down to 2 dragons, the queen may take blind portals again, also late with a queen lead. [E] Rare, since small maps are mostly seen by then; not seen in a game.
4. Keep CENTER_MAX_CELLS: your slithery numbers (behind at r25 and r50, ahead by r100, seats split 1-1) against a start room never left in 500 rounds is a clear trade. [C] It reaches only maps at least twice as wide as tall (616); tall maps get nothing.
5. QUEEN_DEAD_ALL removal and QUEEN_NO_RAM stand as in my first message: 20 pairs recounted 8 -> 12 wins with no pair worse, no new no-action path. NO_RAM still leaves the single step into a trade-target head for a queen of 4 or shorter (8145), which is no worse than live.
Not checked: mC19 binary against one19C.switches, and any game of mC19 on a map over 1000 cells.

---

## 2026-10-09 05:33:12 — closing summary

Final verdict sent to the lead at about 14:32 KST: **SHIP C** (one18 minus `QUEEN_DEAD_ALL`, plus `CENTER_MAX_CELLS:100000`, `QUEEN_NO_RAM:true`, `QUEEN_BLIND_STALL:20`). `SPLIT_KNOWN_TAIL` was dropped by the lead before this verdict.

- **Portals question (the lead's main ask):** no, mC19's queen shows no sign of taking a blind portal in the first 30 rounds on `ladder_portals_1`, and no round-9 deaths. In the lead's games mC19 and mA19 have the same eats, the same death list (first deaths at r12 and r11) and the same final results on both seats. The lift needs 2 or fewer dragons at round 20 or later, and we have 9 and 7 at r25.
- **`QUEEN_BLIND_STALL` on `ua_boxnp_320`:** the lift fires (eats by r30 go 0 → 5 and 0 → 3), but mC19 is still eliminated on both seats (r58 and r91, against r56 and r57 for mA19 and mD18). It is harmless but does not give the win the ban-off arm gave.
- **Open risk in `QUEEN_BLIND_STALL`:** line 8111 has no upper round, so any time from round 20 on that our side is down to 2 dragons the queen may take blind portals again, including late with a queen lead. I did not see this in a game.
- **`CENTER_MAX_CELLS`:** keep it. The lead's numbers show the early slowdown on the big long map is recovered by r100, against a start room the live bot never leaves in 500 rounds. It only reaches maps at least twice as wide as tall (line 616).
- **`QUEEN_DEAD_ALL` removal and `QUEEN_NO_RAM`:** unchanged from my first message. `QUEEN_NO_RAM` still leaves the single step into an enemy head for a queen of 4 or shorter (line 8145), which is no worse than live.

Not checked: whether the mC19 binary matches `one19C.switches`, and any game of mC19 on a map over 1000 cells.

Scripts are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/review19-opus/` (`snap.py`, `qda.py`, `stall.py`); my six games are in `~/meow-redteam/solo/runs/rv19_mB19/` and `~/meow-redteam/solo/runs/rv19_mD18/`.
