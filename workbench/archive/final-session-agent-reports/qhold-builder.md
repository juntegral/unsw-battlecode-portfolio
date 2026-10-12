# Reports sent to the lead by qhold-builder

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-08 22:30:44 — qhold build finished, OFF equals base

qhold is finished: OFF equals base, all ON builds compile, nothing was played or run.
1. OFF = base: both b2c4e46138e027449f58dcd9c5b6719aeb0ee230 (same output path, cmp equal). Extra check: main.cpp with all one12 live constants and HOLD 0 builds to 48e3d8ad..., identical to one12-bot/main.cpp itself.
2. What broke it: the previous builder's member wrapper `bool can_split(int)` (changes inlining). Now an inline term `&& !(QUEEN_HOLD_LEN > 0 && hold_split(child))` at each of the 11 ct.can_split sites. Second trap: `(old cond) || (HOLD...) ? BONUS : 0` in leader_priority also changes the binary; the nested ternary form folds back.
3. ON builds, -O2 -Wall -Wextra, 0 warnings: main.on.cpp (HOLD 4 only) 369aea14...; your 7 live settings 7fe0556c...; all 45 one12 constants + HOLD 4 98b5459e.... Rebuild a profile copy with scratch/profile.py.
4. Lines changed: +117 / -18, 21 hunks, one comment line. qhold.diff regenerated (patching base reproduces main.cpp); done.txt written.
5. Signal: qh_foe_dead() (qh_foe_dead_round, queen-ping bit 23), detection unchanged. Relay = one extra term in the existing queen-ping branch (2 of 4 directions per round). With QUEEN_AVENGE 8 as live, that branch already sends it, so live sonar traffic is unchanged.
6. Delay: 0-1 round if our queen is the witness; 1-3 rounds if a witness's sonar ray reaches her; otherwise hop by hop with no upper bound. Sonar ordering is taken from ../war/done.txt, I could not find the rule file.
7. Biggest caveat [E]: with the live corpse mask a witness only catches a queen who dies on the cell where it last saw her head (killed before her next move). How often the switch arms at all is unmeasured; count that first in replays.
8. Design changes vs preregister (reasons in done.txt): (a) relay no longer overrides mouth/tail/zone/sight pings of every dragon for the rest of the game; (b) the leader bonus is seen only by the queen and mates of 2 or 3, so mates of 4+ keep their leader; (c) the paid-move search is now a copy of the queen's hit_escape (visited cells, room test, score above reject, no portals, eval cap) with one-step moves included; the old one was an unbounded DFS that accepted rejected tiles; (d) dropped the corpse-mask narrowing, enemy_queen_dead resets and the hear_exact re-run.
9. Splits: all 11 can_split sites covered, every split_off goes through one. At hold 4 every "keeps 2" escape split is refused while she holds; no replacement split that keeps 4 was added (this is the "boxed" falsifier).
10. Paid moves: one gate on the final act_dirs after all overrides; logs "QHOLD" when it replaces a move. Deviations from the brief: it does nothing on a qs_plain (trapped) turn; "rejected by rings" includes hit_escape's room test, so she still pays if her only free safe tiles are closed pockets; a pearl on the paid step itself does not excuse the payment.
11. Feeding: for the queen and mates of 2 or 3, feeding_phase is true at once and the ratio is waived until she is 8; all other conditions unchanged. Side effects: she becomes is_leader after grow_round, the qboot split guard arms below 6, and mates of 2 or 3 rally to her.
12. Could not do: verify behaviour, CPU, or arming rate (no games, no replays read). Zone flag enemy_queen_dead is not merged into the signal (QG_SAFEZONE is off in base and live).
Files: ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/qhold/{main.cpp, main.on.cpp, qhold.diff, done.txt, scratch/}

---

## 2026-10-08 22:30:44 — closing summary

The `QUEEN_HOLD_LEN` build is finished and reported to the team lead: the OFF build is byte-identical to base, and all ON builds compile. No games were played, so behaviour, CPU and how often the switch arms are unmeasured.

- **OFF = base:** both hash to `b2c4e46138e027449f58dcd9c5b6719aeb0ee230`. With all one12 live constants and the switch at 0, the build also matches the one12 live bot's binary.
- **What broke it:** the previous builder's `can_split` wrapper function. It is now an inline term at each of the 11 split sites.
- **ON builds:** `main.on.cpp` (hold 4 only), the seven live settings you listed, and the full one12 profile plus hold 4 all compile with no warnings.
- **Size:** +117 / -18 lines, 21 hunks, one comment line.
- **Signal:** `qh_foe_dead()`, with detection unchanged. The relay is one extra term in the existing queen-ping branch; with `QUEEN_AVENGE = 8` as live, that branch already sends it, so live sonar traffic does not change.
- **Delay:** 0–1 round if our queen is the witness, 1–3 rounds if a witness's sonar ray reaches her, otherwise no upper bound. The sonar ordering is taken from `../war/done.txt`; I could not find the rule file.
- **Biggest caveat:** with the live corpse mask, a witness only catches a queen who dies on the cell where it last saw her head. If the signal rarely fires, the switch does nothing, so count arming first in replays.

Design changes from the previous builder's plan:
- **Relay:** it no longer overrides every other sonar message of every dragon for the rest of the game.
- **Leader bonus:** only the queen and mates of length 2 or 3 see her as leader, so mates of 4+ keep theirs.
- **Paid-move search:** it now mirrors the queen's own `hit_escape` search instead of an unbounded depth-first walk that accepted rejected tiles.

Deviations from the brief:
- **Escape splits:** every "keeps 2" escape split is refused at hold 4, and no replacement split that keeps 4 was added.
- **Paid moves:** she still pays if her only free ring-safe tiles are closed pockets, and nothing changes on a turn she is already trapped.
- **Zone flag:** `enemy_queen_dead` is not merged into the signal (`QG_SAFEZONE` is off in base and live).

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/build/qhold/`:
- main.cpp
- main.on.cpp
- qhold.diff
- done.txt
- scratch/profile.py
