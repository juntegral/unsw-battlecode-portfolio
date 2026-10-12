# Reports sent to the lead by qtrap-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 04:50:44 — qtrap cause heads-up

qtrap heads-up (cause, Maze 1523623, queen = dragon 1): [C] guard_queen_corridor let it through twice. r94 entry (24,20)->S: the room rule at main.cpp:870-878 counts free cells across branches already proven dead (3 pocket cells + 2 corridor cells = 5 >= len 3 + 2) so it returned "room". r96 (23,21)->S into the 3-pearl pocket WAS judged dead, but the only alternative W was also "dead" because a mate's body stood in that corridor (mates are static obstacles, :815-822), and with no clean alternative the guard keeps the original move (:923).
Second half: [C] escape_child_size :2413-2425 returns length-2 for the queen when no cell is enterable (the r100 split 4->2), then at length 2 she steps onto her own tail. Building one switch now: real queen with no enterable cell neither splits nor moves (stays), plus guard fallback prefers a mate-blocked alternative over a proven pocket. Report by 14:15.

---

## 2026-10-09 04:56:36 — qtrap usable switch heads-up

qtrap heads-up 2: usable switch QUEEN_CORRIDOR_MATE:true built (source ~/meow-redteam/solo/src/w-qtrap/main.cpp, diff in ROOT/data/codex/astra/qtrap-opus/qtrap-opus.diff). [M] all-off hash 92fb69564fbd OK; one17-values build is byte-identical to mD17 (d6d14e1f8f53).
Cause confirmed in 2 online cases (Maze 1523623 r96, Maze 1528857 r139) and reproduced locally: the guard DID judge the pocket dead, but the only other step led to a cell whose onward way was a mate's body, so that was "dead" too and the guard kept the fatal move. Local ladder_maze_1 vs m3base seed 1: off (= mD17) queen enters the 3-cell pocket at r151 and dies on a wall r155; MATE on takes the other step at r151 and lives to r192. Pairs table (pearls, 6 maps x 2 opponents) still running, final by 14:12. Ignore my earlier "stay" idea: a dragon with no action dies ("no valid action"), so it was dropped.

---

## 2026-10-09 04:57:28 — closing summary

Waiting on the pairs to finish; the diff is saved and both hash checks pass for the two-switch source.

---

## 2026-10-09 04:57:47 — qtrap candidate string for parallel check

qtrap candidate for your parallel check: QUEEN_CORRIDOR_MATE:true (source ~/meow-redteam/solo/src/w-qtrap/main.cpp; built bot solo/bots/qtm = one17 values + this). [M] all-off 92fb69564fbd; one17-values build byte-identical to mD17 (d6d14e1f8f53).
What it does: only when the corridor guard has already judged the queen's move a proven dead end AND found no clean other step, it re-checks the other steps with mates' bodies treated as passable and takes the best one that is then not a dead end. It cannot fire unless the guard already rejected the move. A second, wider switch QUEEN_CORRIDOR_TREE:true (drops the "length+2 free cells = room" shortcut that let the weakhold 1528854 r121 entry into a branching dead-end tree pass; bot qtt = both) is in the same source, same hashes; it is NOT a candidate until its pearls table is in. Now at 2 games at a time; table by 14:38.

---

## 2026-10-09 05:20:18 — qtrap final: ready QUEEN_CORRIDOR_MATE:true

qtrap-opus FINAL (14:19 KST): ready: QUEEN_CORRIDOR_MATE:true
Built: one switch in guard_queen_corridor. When the guard has judged the queen's move a proven dead end and found no clean other step, it re-checks the other steps with mates treated as passable and takes the best one that is then not a dead end. It cannot fire unless the guard already rejected the move.
How sure: high that it is harmless where it does not fire (byte-identical games), medium on how often it saves her (2 fires in 17 local pairs, both correct). The two online Maze cases are a board hand-walk, not a bot re-run.

HASH [M]: all-off 92fb69564fbd OK. one17 values = d6d14e1f8f53, byte-identical binary to mD17. one17 + MATE = 08f6a40bb8ff (same hash rebuilt from the final source).
Source ~/meow-redteam/solo/src/w-qtrap/main.cpp, diff ROOT/data/codex/astra/qtrap-opus/qtrap-opus.diff, table ROOT/data/codex/astra/qtrap-opus/table.txt, bots solo/bots/qtm (MATE) and qtt (MATE + TREE).

CAUSE (queen = lowest id)
- Maze 1523623 r96 (queen at (23,21), pocket (23,22)-(25,22)) and Maze 1528857 r139 (queen at (36,20), column (36,21)-(36,23)): [C] the guard does call the pocket dead (walk ends at depth 2, main.cpp:864). The only other step (W in both) leads to a cell whose way on is a mate's body; occupied() :815-822 treats every other dragon as a fixed wall, so that step is "dead" too, best stays -1 and :923 keeps the fatal move. [E] with mates passable the W walk reaches depth 6 in both, so W is taken.
- weakhold 1528854 r121 ((10,8) -> W into a branching dead-end tree of 8 cells, 5 pearls): [C] the room rule :870-878 returns "room" once a fork was seen and 5 free cells (length 3 + 2) were counted, mid-branch, though every branch is one-wide and closed. [E] assumes those edges were known. MATE does not cover this.
- Not the cause: EAT_FIRST (the guard runs after it), and growth (step() :835-842 counts it).
- Once inside nothing helps: a dragon with no action dies ("no valid action"), so she splits (:2413-2425, 4 -> 2) and then dies. Stripes 1525834 r79 has enemies around, a different class.

MECHANISM [M], ladder_maze_1 vs m3base, same seed, off = mD17 binary
  seed 1: off enters the 3-cell pocket r151, dies on a wall r155 | MATE steps E at r151, lives to r192
  seed 2: off enters a 3-cell pocket r253, dies on a wall r258   | MATE steps E at r253, lives to r331 (rammed)
Fires: 2 of 17 pairs, both on Maze. Queen death round: later in those 2, identical in the other 15, earlier in none.

PEARLS BY R100 / DRAGONS AT R100, off = MATE on in every row (seed 1; both fires came after r100)
  map       vs m3base   vs mD17
  maze      76 / 35     80 / 35
  weakhold  60 / 18     52 / 11
  stripes   63 / 9      56 / 9
  default   119 / 31    137 / 39
  cor24     67 / 21     65 / 4     (gx_corridors_24x12; the m3base game ended r68)
  cor64     315 / 58    290 / 48   (gx_corridors_64x16)
Extra seeds (maze 2 and 3, weakhold 2): identical too. Byte check: 5 games replayed with the off binary under a 3-letter name differ from the MATE replays in 1 byte (the name).
Head to head vs mD17, 8 games: no divergence, so results equal by construction (maze W, weakhold W, stripes W, default W, cor64 W, cor24 L, maze s2 W, weakhold s2 L).

NOT READY: QUEEN_CORRIDOR_TREE:true (drops the room shortcut, aimed at the weakhold case). It changed nothing in the 12 base games. In the one game where it differed from MATE-only (maze vs m3base seed 2) the queen died on her own body at r333 and the game went from win to loss. Unexplained, and its worst-case CPU is unmeasured. Do not ship it.

STILL OPEN
- r192 in the seed 1 MATE game: she is in a one-wide corridor, a mate's body sits on the only through exit, the other exit is a dead end, and at length 3 she cannot split. No legal alternative exists.
- maze vs mD17 seed 2, r185, both arms: a mate's head comes head-on in a one-wide corridor. Mates do not yield to the queen.

WHAT WOULD SHOW IT WRONG
- A queen death by ram or head-to-head within about 3 rounds of a fire: the fallback ignores the score floor, so it can step next to an enemy rather than into the pocket.
- A fire where the "passable" mate is itself stuck, so she queues behind it and dies anyway.
- Any game without a fire that differs from mD17 (should be impossible; 5 of 5 byte-identical).

---

## 2026-10-09 05:20:18 — closing summary

**ready: `QUEEN_CORRIDOR_MATE:true`** — final report sent to the lead at 14:19 KST, ahead of the 14:35 cut.

**What it does:** when the corridor guard has already judged the queen's move a proven dead end and found no clean other step, it re-checks the other steps with mates treated as passable and takes the best one that is then not a dead end. It cannot fire unless the guard already rejected the move.

**Cause found**
- **Maze 1523623 r96 and Maze 1528857 r139:** the guard did call the pocket dead. The only other step led to a cell whose way on was a mate's body, which the guard treats as a fixed wall, so that step was "dead" too and the guard kept the fatal move (`main.cpp:815-822`, `:923`).
- **weakhold 1528854 r121:** the room rule (`:870-878`) counted free cells in a branching dead-end tree as room. The new switch does not cover this case.
- **Not the cause:** `EAT_FIRST` (the guard runs after it) and growth from eating (it is counted).
- **Stripes 1525834 r79:** enemies were around her; a different class.

**Verification**
- **Hashes:** all-off is `92fb69564fbd`; the one17-values build is byte-identical to `mD17` (`d6d14e1f8f53`); one17 plus the switch is `08f6a40bb8ff`.
- **It fires where it should:** on `ladder_maze_1` against `m3base`, the off queen enters a 3-cell pocket and dies on a wall (r155 on seed 1, r258 on seed 2). With the switch on she steps the other way and lives to r192 and r331.
- **No cost elsewhere:** it fired in 2 of 17 pairs. In the other 15, pearls by r100, dragons at r100 and the queen's death round are identical on all six maps against both opponents. Five games replayed under a same-length bot name are byte-identical apart from the name.
- **Online cases:** the two Maze cases are a hand-walk of the boards, not a re-run of the bot on that turn.

**Not ready: `QUEEN_CORRIDOR_TREE:true`** (same source, aimed at the weakhold case). It changed nothing in the 12 base games, and in the one game where it differed the queen died on her own body and the result flipped from win to loss. I could not explain that in the time left.

**Still open:** two self-trap deaths the switch does not reach — a mate's body sitting on the only through exit of a corridor she is already in (r192), and a mate's head coming head-on in a one-wide corridor (r185).

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/qtrap-opus/`:
- qtrap-opus.diff
- table.txt

Source: `~/meow-redteam/solo/src/w-qtrap/main.cpp`. Built bots: `~/meow-redteam/solo/bots/qtm` (the candidate) and `qtt` (both switches).
