# Reports sent to the lead by early-opus

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 02:08:13 — early-opus heads-up: measured differences, tests running

early-opus heads-up (11:10): measured r0-100 on one14-c1, one11-c1, one11-p1 (45 games, same script both sides); nothing ready yet, two existing-constant candidates are playing locally.
[M] (1) Next to a pearl everyone eats the same (81-83% of turns), but they get 1.5-2x as many such turns: short non-queen dragons with a pearl 1 step away, per game: us 88 / Cache 182, us 110 / Preyas 167. Our length 2-3 dragons are 9+ steps from any pearl in 40% of turns, Cache 26% (higher for us on 11 of 15 maps), Preyas 36%. (2) Non-queen dragons that reach 4+: Cache splits on the first turn 93%, Preyas 83%, we 48-62%; with a pearl adjacent at 4+ we eat 84% / split 13%, Cache splits 82%; we hold 59-66 such turns a game against Cache's 6, most often exactly 2 turns [E: the harvest gate, main.cpp 1921 + 2318; existing switch HARVEST_SPLIT lifts it, never tested]. (3) r0-11 without a pearl in reach: we keep heading 54-59%, they 68-74%, and they end nearer a pearl 61-72% against our 53-58% (HEADING_TIE is live only for r0-11; Preyas keeps 67-72% all game). Not a difference: paid steps (under 1 a game both sides), deaths (they die more: 37-50 against our 26-32 by r100, trapped length-2 dragons on both sides), share of turns that end no nearer a pearl (44% both).
Testing now against mNps, same maps and seed: HEADING_TIE_ROUNDS 0 (always), HEADING_TIE 4.0, then HARVEST_SPLIT true. All-off hash of my copy = 92fb69564fbd, one14 build of my copy = mNps byte for byte.

---

## 2026-10-09 02:31:40 — early-opus: gap is pearls on corridor cells

early-opus (11:31): the pearl gap is mostly pearls eaten on narrow cells (2 or fewer open sides: corridors, dead ends), where our short dragons go half as often as Cache. Not ready; candidates are existing constants, local test in progress.
[M] 60 games (one14-c1/p1, one11-c1/p1), non-queen length 2-3, r0-100. Narrow cells give everyone 16-24 pearls per 100 turns against 5.5-7.8 on open cells. Share of turns there: us 9.1% / Cache 16.1% (lower for us on 10 of 15 maps), 9.6% / 15.8% (9 of 15); against Preyas 10.8 / 11.1 and 9.8 / 12.4. Pearls per game eaten on narrow cells: us 16 / Cache 57, 19 / 57, us 26 / Preyas 38, 22 / 44. That is about 40 of the 48-pearl r100 gap against Cache and 13-22 of the ~40 against Preyas.
[C] src/solo/main.cpp 7664-7667: a step from which the flood does not reach our own tail costs PENALTY_NO_TAIL 600 whatever room is ahead, because NO_TAIL_ROOM is 0 (in a one-wide corridor the tail is always behind the neck); the only exemption is the stall release (5157-5160), which exists only where the centre rule is on (1000 cells or fewer). [M] local ladder_tower_defense_1: both our dragons circle the start room 22-40 rounds before entering the corridor, first pearl r64-73 (Cache online r39); TR_STALL_ROUNDS 4 brings it to r56; CENTER_PULL 0 makes it worse (they pace a 2x2 for 50 rounds, 4 pearls by r100): do not turn the centre pull off.
Ruled out as differences [M]: behaviour next to a pearl (81-85% eat at 1 step, both sides), approach at 2-8 steps (same), portal steps by r50 (8-12 both), paid steps (under 1 a game), deaths (they die more), pacing in place (2-4% both).
Playing now against mNps: NO_TAIL_ROOM 6, NO_TAIL_ROOM 6 + TR_STALL_ROUNDS 4, TR_STALL_ROUNDS 4, base. First table by about 11:45.

---

## 2026-10-09 02:33:38 — early-opus: correction + EXPLORE_GAIN first signal

early-opus (11:35): correction to my 11:31 note, and one existing constant showing a first signal: EXPLORE_GAIN 10 (off in one14). One map so far, not ready.
Corrections [M]: (1) NO_TAIL_ROOM 6 is inert: on two maps the game is move-for-move the base game through r48 and the r100 numbers are identical, so the no-tail penalty is not what keeps us out of corridors; drop that line. (2) "40 of the 48-pearl gap" mixed two populations. Among short non-queen dragons the r100 gap against Cache is 78 pearls a game (73 against 150), 41 of it on narrow cells (16 against 57) and 37 on open cells; against Preyas 13-22 of about 45 is on narrow cells. So narrow ground is about half against Cache and a third to a half against Preyas.
[M] local, seed 7, side A against mNps, gx_corridors_24x12: base 91 pearls by r100, 25 dragons, total length 61, 14 deaths; CRAMPED_EAT 92 / 26 / 62 / 13; NO_TAIL_ROOM 6 identical to base; EXPLORE_GAIN 10: 144 pearls, 32 dragons, length 77, but 29 deaths (double), pearls on narrow cells 27 against 14, turns with a pearl one step away 148 against 88.
[C] main.cpp 7717-7719: until r200 each step nearer the closest unseen tile is worth EXPLORE_GAIN; today the only pull beyond 6 steps is FAR_GAIN 2 a step (7720-7730), and every pearl / unseen bonus is zero from 6.5 steps (5599-5605, TARGET_REWARD 260 / TARGET_DECAY 40).
Now playing EXPLORE_GAIN 10 against base on ten maps, then the other side. I will not have 16 maps both sides by 12:00.

---

## 2026-10-09 02:46:54 — early-opus final: nothing ready, measured differences

early-opus FINAL (11:46): no switch is ready; the gap is measured and located, its cause in our code is not.
Ready to go live: NO. Six existing constants tried locally, none passes; one makes things worse (CENTER_PULL 0), one is inert (NO_TAIL_ROOM 6).
How sure: the measurements high (60 games one14-c1/p1 + one11-c1/p1, same script both sides, plus one5/one8/one10 against Cache for one row); the local tests low (1 game per map per arm, seed 7, side A against mNps: only gross effects show). Two code guesses of mine (no-tail penalty, corridor refusal) were refuted by test.

Hash: all-off of src/w-early/main.cpp = 92fb69564fbd; its one14 build = mNps byte for byte (84497be4d00e). The diff holds one new switch, PEARL_TAIL_GAIN (off, never played): do not use.

[M] r0-100 per game, us / them           one14-c1   one14-p1   one11-c1   one11-p1
pearls eaten                              114/162    118/155    112/162    113/156
natural pearls                             80/104     80/114     83/105     82/112
dragons at r100                            21/26      21/32      24/27      25/30
total length at r100                       56/63      52/88      65/66      62/81
short non-queen turns, pearl 1 step away   88/182    101/150    100/185    110/167
 ... of which eaten (same both sides)      82/83%     85/85%     84/82%     81/83%
share of short turns on narrow cells %    9.1/16.1  10.8/11.1   9.6/15.8   9.8/12.4
pearls eaten on narrow cells               16/57      26/38      19/57      22/44
short turns 9+ steps from any pearl %      42/26      41/41      40/27      39/36
repeat eats on the same tile               50/67      52/71      48/68      45/70
turns within 3 cells of a mate's head %    37/56      39/47      40/55      43/46
4+ non-queen: split on the first turn %    48/93      54/76      62/94      62/83
r0-11, no pearl near: keeps heading %      54/68      54/73      59/72      59/74
queen's distance from start at r50        12.7/7.7   11.2/6.1    9.5/5.5    9.8/4.9
deaths before r100                         32/50      34/35      26/48      28/37
Narrow cell = 2 or fewer open sides. They yield 16-24 pearls per 100 turns against 5.5-7.8 on open cells. Our share there is 8.6-9.6% in every version one5 to one14 against Cache's 15.3-16.3% (75 games), so it is the base scoring, not a recent switch.
The three largest, most consistent differences: (1) they have 1.5-2x the turns with a pearl one step away, about half of that surplus on narrow cells (lower for us on 9-10 of 15 maps against Cache; against Preyas the surplus is more on open ground); (2) they re-eat the same producing tiles (67-71 repeat eats against 45-52) with more dragons around (within 3 of a mate 46-56% against 37-43%, 10-13 of 15 maps); (3) from 4+ they split at once (76-94% against 48-62%); we eat first (84% eat / 13% split with a pearl adjacent, Cache 18% / 82%) and hold exactly 2 turns most often.
Not differences: what a dragon does 1, 2-3 or 4-8 steps from a pearl (same percentages), share of turns ending no nearer a pearl (44-45% both), paid steps (under 1 a game both), portal steps by r50 (8-12 both), pacing in place (2-4% both), deaths (they die as much or more; ours are trapped length-2 dragons too).

[C] src/solo/main.cpp. Pearl, soon, hot and unseen pulls are zero from 6.5 steps (5599-5605, TARGET_REWARD 260 / TARGET_DECAY 40; used 7704-7716); beyond that only FAR_GAIN 2 a step (7720-7730); EXPLORE_GAIN 0 (7717). Centre pull and its stall release only on maps of 1000 cells or fewer (610, 5157-5160, 7758-7762). Split gate while harvesting: 1921 + 2318 (HARVEST_SPLIT lifts it; built as ea_hs, not played). Tight-room penalty counts mates in the room against it (7651-7658, ally_load 5115). [E] Which of these keeps us off narrow ground is open.

Local tests, pearls by r100 / dragons at r100, base (mNps mirror) -> arm:
EXPLORE_GAIN 10 (8 maps): corridors24x12 91/25 -> 144/32; ring24x12 77/2 -> 93/7; tower_defense 29/8 -> 34/12; corridors64x16 247/48 -> 244/47; rooms64x16 350/60 -> 266/29; open24x12 115/27 -> 69/1; rooms24x12 53/6 -> 14/1; stripes 40/5 -> 2/1. Mean 125 -> 108; deaths 27.5 -> 27.5; as side A 3 wins of 8 against base 5 of 8. FAILS (down more than 10% on 4 maps; on two it starves with few deaths [E: anchored to unseen tiles it cannot reach]).
TR_STALL_ROUNDS 4 (3 maps): open24x12 115/27 -> 165/29; stripes 40/5 -> 33/4; tower_defense 29/8 -> 23/9 (first pearl r73 -> r56). Unclear.
HEADING_TIE always, 1.5 (3 maps): 115 -> 121, 350 -> 287, 258 -> 262; heading kept when far 34% -> 40%. With 12.0 (2 maps): tower 29 -> 40, stripes 40 -> 44; 25.0: tower 29 -> 17. No clear effect.
CENTER_PULL 0: tower_defense 29/8 -> 4/3, both dragons pace a 2x2 for 50 rounds. Harmful; keep the centre pull.
NO_TAIL_ROOM 6: the same game as base on both maps played. CRAMPED_EAT: 91/25 -> 92/26 on one map.
Head to head on 16 maps both sides: not done for any arm (nothing earned it).

What would show this is wrong: if a version with our narrow-cell share raised to about 15% does not close the pearl gap against Cache, the narrow-ground reading is only a correlate of having more dragons. The split-latency row is carried by four maps (Slithery Fight, Around UNSW, Islands, Portals), so it is not a most-maps habit.
Files: ROOT/data/codex/astra/early-opus/ (scan.py, summ.py, narrow.py, hold2.py, sight.py, blind.py, tiles.py, portal.py, centre.py, table-*.txt, early-opus.diff); runs under ~/meow-redteam/solo/runs/ea_*. All my games and queues are stopped.

---

## 2026-10-09 02:46:54 — closing summary

Final report (also sent to the lead by message at 11:46 KST).

**No switch is ready to go live.** I measured the first-100-round gap and located where it sits, but did not find the code that causes it. Six existing constants were tried locally: none passes, one is harmful, one is inert.

**How sure:** the measurements are solid (60 games across `one14-c1`, `one14-p1`, `one11-c1`, `one11-p1`, same script for both sides). The local tests are weak: one game per map per arm, seed 7, side A against `mNps`, so only gross effects show. Two of my own code guesses (the no-tail penalty, corridor refusal) were refuted by test.

**Hash:** all-off build of `w-early/main.cpp` = `92fb69564fbd`; its one14 build is byte-identical to `mNps` (`84497be4d00e`). The diff holds one new switch, `PEARL_TAIL_GAIN`, off and never played — do not use it.

## Measured differences (r0-100, per game, us / them)

| | one14-c1 | one14-p1 | one11-c1 | one11-p1 |
|---|---|---|---|---|
| Pearls eaten | 114/162 | 118/155 | 112/162 | 113/156 |
| Natural pearls | 80/104 | 80/114 | 83/105 | 82/112 |
| Dragons at r100 | 21/26 | 21/32 | 24/27 | 25/30 |
| Total length at r100 | 56/63 | 52/88 | 65/66 | 62/81 |
| Short non-queen turns with a pearl 1 step away | 88/182 | 101/150 | 100/185 | 110/167 |
| …share of those eaten | 82/83% | 85/85% | 84/82% | 81/83% |
| Share of short turns on narrow cells | 9.1/16.1% | 10.8/11.1% | 9.6/15.8% | 9.8/12.4% |
| Pearls eaten on narrow cells | 16/57 | 26/38 | 19/57 | 22/44 |
| Short turns 9+ steps from any pearl | 42/26% | 41/41% | 40/27% | 39/36% |
| Repeat eats on the same tile | 50/67 | 52/71 | 48/68 | 45/70 |
| Turns within 3 cells of a mate's head | 37/56% | 39/47% | 40/55% | 43/46% |
| Non-queen at 4+: splits on the first turn | 48/93% | 54/76% | 62/94% | 62/83% |
| r0-11, no pearl near: keeps heading | 54/68% | 54/73% | 59/72% | 59/74% |
| Queen's distance from start at r50 | 12.7/7.7 | 11.2/6.1 | 9.5/5.5 | 9.8/4.9 |
| Deaths before r100 | 32/50 | 34/35 | 26/48 | 28/37 |

A narrow cell has two or fewer open sides (corridor or dead end). These yield 16-24 pearls per 100 turns against 5.5-7.8 on open cells. Our share there is 8.6-9.6% in every version from one5 to one14 against Cache's 15.3-16.3% (75 games), so it comes from the base scoring, not a recent switch.

The three largest, most consistent differences:
1. **Turns next to a pearl.** They get 1.5-2x as many, and about half of that surplus is on narrow cells against Cache (we are lower on 9-10 of 15 maps). Against Preyas the surplus is more on open ground.
2. **Re-eating producing tiles in company.** They eat the same tile again far more often and keep more dragons close together (we are lower on 10-13 of 15 maps).
3. **Splitting at once.** With a pearl adjacent at 4+ we eat 84% and split 13%; Cache eats 18% and splits 82%. This one is carried by six maps (Slithery Fight, Around UNSW, Islands, Portals, Trauma, weakhold), not most maps.

Not differences:
- what a dragon does 1, 2-3 or 4-8 steps from a pearl (same percentages);
- share of turns ending no nearer a pearl (44-45% both);
- paid steps (under 1 a game both);
- portal steps by r50 (8-12 both);
- pacing in place (1-5% both);
- deaths (they die as much or more).

## Code that bears on it (`src/solo/main.cpp`)

- **Pulls vanish at range:** pearl, soon, hot and unseen bonuses are zero from 6.5 steps (5599-5605, used at 7704-7716). Beyond that only `FAR_GAIN` 2 per step applies (7720-7730); `EXPLORE_GAIN` is 0 (7717).
- **Centre pull and its stall release** exist only on maps of 1000 cells or fewer (610, 5157-5160, 7758-7762).
- **Split gate while harvesting:** 1921 + 2318. `HARVEST_SPLIT` lifts it; I built `ea_hs` but did not play it.
- **Tight-room penalty** counts mates in the room against the dragon (7651-7658, 5115).

Which of these keeps us off narrow ground is still open.

## Local tests (pearls by r100 / dragons at r100, base → arm)

| Arm | Maps | Result |
|---|---|---|
| `EXPLORE_GAIN` 10 | 8 | Fails. Mean pea
[result truncated — ask the agent for the rest via SendMessage]
