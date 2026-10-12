# Independent check: how our queen dies (card #38 follow-up)

## Verdict per claim

- **A: holds in part.** The counts are right (28 wall, 16 own body; 19 and 10 before round 50). "Two thirds forced" is wrong: all 44 were forced. The 15 "had a safe move" cases are a 2-long queen's own tail tile, which the engine blocks.
- **B: holds in part.** 20 of the 44 stepped onto a tile that then closed around her. The other 24 never walked anywhere: the map spawns her with her head in a dead end.
- **C: holds, but not as a bot fault on three of the four maps.** autarky_v0, prisoners_dilemma_v0 and slithery_fight_v0 kill both queens in the same round in every game by map design. portals_v0 is the one repeated case the bot causes.
- **D: holds in part.** The numbers are right. "Shorter at round 100" and "fewer pearls before round 300" hold. "The enemy queen grows more when ours loops" is not supported: 3 of 4 trauma pairs, with overlapping ranges.

## What is safe to tell the team

1. Measured, 136 hunter-run games: our queen died 115 times, 28 by wall and 16 by her own body. In all 44 she had no free first step at the fatal action, and she was 2 or 3 long (too short to split).
2. Measured: wall and own body are one kind of death. The same trap is logged as "wall" in one game and "own body" in the next (slithery_fight_v0: wall as side 0, own body as side 1). Inferred from the code: with four blocked sides a tie-break picks the side.
3. Measured: 24 of the 44 are autarky_v0 (round 9), prisoners_dilemma_v0 (round 6) and slithery_fight_v0 (round 4), 8 of 8 games each. These maps spawn the queen 14, 11 and 7 long with her head in a dead end of 3, 2 and 2 tiles. She lives exactly as long as the tiles and splits allow.
4. Measured: the enemy queen dies in the same round in all 24 of those games. The queen rule never decides a game on these three maps, and no bot change can keep her alive there.
5. Measured: the other 20 are portals_v0 8 (8 of 8 games), maze 5, devil_v0 3, weakhold 3, islands 1. In 18 of the 20 one of our own dragons stood next to her head during her last two actions. In 0 of the 20 an enemy dragon did.
6. Measured: on portals_v0 she steps through a portal into a sealed one-tile cell and dies on her next action, in 8 of 8 games (round 13 with seed 3000, rounds 113 and 121 with seed 3001). At that step the portal was the only side not blocked, and a team-mate was on the other open side.
7. Measured: the hunter is not the cause. The hunter's own queen died by wall or own body 44 times in the same 136 games, on the same maps apart from islands. On the four maps both runs share, the count is 3 in 32 games in each run, all on weakhold. The runs differ because of the map list.
8. Inferred from `main.cpp`: nothing walks her into a wall on purpose. It is the last line of her turn when no tile can be entered, she cannot split, and no portal is left.
9. Inferred, not tested: the fixable part is 20 deaths in 136 games (23 with the 3 "other body" deaths), nearly all "our own dragon closed her exit". The existing switches to try are listed at the end.
10. Measured, trauma, 4 games per arm: with the switch on our queen ate 0 pearls before round 300 in 4 of 4 games (4 to 7 with it off), was 2 long at round 300 in 4 of 4, and lost all 4 on the queen rule by 13 to 17 segments. With the switch off the result was 2 wins and 2 losses.
11. Not supported by 4 games: that the enemy queen grows more because ours loops. Her pearls from round 300 on were 17, 38, 26, 42 with the switch off and 47, 47, 35, 30 with it on. One of the four pairs goes the other way.
12. Separate finding, not explained: on tower_defense the queen with id 0 dies with "no valid action" at round 403 in 8 of 8 games, whichever bot plays that side. In the three games looked at, 16 to 19 dragons of that side die the same way from round 401 on.

## Counts next to the earlier ones

Recounted from the raw replays on 2026-10-07: 136 hunter-run games and 32 check-run games. The earlier results (`deaths/`) were opened only after this count was finished. No games were run and no bot code was changed.

| | earlier (`deaths/summary.md`) | this recount |
|---|---|---|
| hunter run, queen deaths | 115 (59 + 56) | 115 (59 + 56) |
| wall / own body / other body / head-on / no action | 28 / 16 / 3 / 64 / 4 | 28 / 16 / 3 / 64 / 4 |
| wall deaths forced | 19 of 28 | **28 of 28** |
| own-body deaths forced | 10 of 16 | **16 of 16** |
| wall deaths before round 50 | 19 of 28 | 19 of 28 |
| own-body deaths before round 50 | 10 of 16 | 10 of 16 |
| check run: wall / own body | 2 / 1 | 2 / 1 |
| check run: wall forced | 0 of 2 | **2 of 2** |
| claim D lengths, pearls, splits | as in the summary | same values |

All 146 death rows match on file, round and cause (`compare.py`).

**The one difference, explained.** The earlier script takes her tail tile out of the blocked set ("Her tail is excluded as in the check", `count.py` lines 47 to 51). The engine does block it: "Hit Self: moved into its own body, including its tail", checked before the tail advances (`rules/ALL.md` lines 396 and 860). All 17 rows it called "had a safe move" (15 hunter, 2 check run) are a 2-long queen whose only "safe" step is her own tail. In 6 of them she took exactly that step and the engine recorded "hit self" (autarky_v0 four times, islands round 113, maze round 101). No row with a real safe move remains.

**By map, hunter run, wall and own-body deaths of the queen (8 games per map).**

| map | cells | ours | rounds | enemy queen | rounds |
|---|---|---|---|---|---|
| slithery_fight_v0 | 1701 | 8 | 4 ×8 | 8 | 4 ×8 |
| prisoners_dilemma_v0 | 512 | 8 | 6 ×8 | 8 | 6 ×8 |
| autarky_v0 | 972 | 8 | 9 ×8 | 8 | 9 ×8 |
| portals_v0 | 512 | 8 | 13 ×4, 113 ×2, 121 ×2 | 8 | 16 ×4, 37 ×2, 67 ×2 |
| maze | 1152 | 5 | 84, 92, 101, 112, 174 | 5 | 84, 92, 92, 112, 174 |
| devil_v0 | 512 | 3 | 35, 70, 243 | 4 | 35, 70, 79, 104 |
| weakhold | 600 | 3 | 93, 276, 295 | 3 | 93, 117, 134 |
| islands | 2240 | 1 | 113 | 0 | |
| around_unsw, australia, default, queen_of_spades, schooltime, stripes, trauma, trophy, tower_defense | | 0 | | 0 | |

Check run (australia, default, queen_of_spades, weakhold, 8 games each): ours 3, all weakhold (rounds 97, 129, 203); enemy queen 5, all weakhold. Same four maps in the hunter run: ours 3, all weakhold.

**When she became trapped** (first of her actions from which no 16-step way out existed on a frozen board):

| | wall | own body |
|---|---|---|
| trapped at spawn (never had a way out) | 16 | 8 |
| the step she took had a way out when taken; other dragons moved before her next action | 8 | 8 |
| her own step: another direction had a way out, hers did not | 4 | 0 |

The four "her own step" cases are devil_v0 rounds 35 and 243 and maze rounds 92 and 112. In the 20 non-spawn cases she was trapped for a median of 2 of her own actions, the fatal one included (range 1 to 12).

## Why she dies early: the three explanations

**1. Boxed in at spawn by the map: yes, 24 of 44.** She did not choose anything.

The drawings below are cut from the `--board` output. Q is her head, q her body, `|` and `-` kelp. Most show tile rows only, so kelp between two rows is drawn only where an edge row is included.

`base_slithery_fight_v0_3000_0`, round 0:

```
+ + + +-+-+-+-
 . . .|.|. . .
+ + + + + + + 
 . . .|.|. . .
+ + + + + + + 
 . . .|Q|. . .
+ + + + + + + 
 . . . q . . .
```

She is 7 long with two tiles ahead and kelp on three sides of the last one. Two splits (7 to 5 to 3) and two steps use rounds 0 to 3. Round 4 has no legal action. prisoners_dilemma_v0 is the same shape with 11 segments and two tiles (4 splits, 2 steps, dead in round 6). autarky_v0 has 14 segments and three tiles (6 splits, 3 steps, dead in round 9):

```
 . . . . . q . . .|. .      base_autarky_v0_3000_1, round 0
 . M . . .|Q|. . . . .
 . m . . .|.|. . . . .
 . m o .|. .|. . . . .
+-+-+-+-+-+-+-+-+-+-+-
```

**2. Boxed in by our own dragons: yes, 18 of the other 20** (plus the 3 "other body" deaths, all against a team-mate).

`base_portals_v0_3000_0`, round 12 (M and m are our own dragons, `:` a portal edge):

```
 . . . q|.:.|. m .
|. .|. q Q:o . M|.        north kelp, west her own body, south a team-mate's head
|o .|. m M . . .|o        east: a portal
```

She steps east through the portal and lands here in round 13:

```
 .|x X o:o X .|. .
:. . .|.:Q|. . . .        kelp north, east and south; west leads back onto her own body
 . . .|. .|. . . o
```

The same tile (8,6), or its mirror (27,6), is where she is caught in all 8 portals_v0 games. In round 11 she had stepped onto it to eat a pearl, and the team-mate moved under her afterwards.

`base_devil_v0_3001_1`, rounds 33 to 35: she walks south into a one-tile-wide corridor for a pearl, a team-mate enters from the other end, she splits once to wait (4 to 2), then has nothing.

```
|.|M . q m m .       round 33: she is in the corridor mouth, a pearl below her
|.|. . q . . .
|.|. .|Q|. .|.
 M . .|o|M .|.
 m . .|.|m .|.

|m|M .|q|m .|.       round 35: north herself, east and west kelp, south our own head
 . . .|Q|. .|.
 . . .|M|. .|.
|.|. .|m|. .|.
```

`base_weakhold_3000_1`, rounds 91 to 93: she walks east along a wall into a corner while a team-mate runs parallel on the open side.

```
 . M m m|. .|.       round 93: north our own body, east and south kelp, west herself
 . . q Q|. .|o
+-+-+-+-+ +-+
```

Boards drawn and read: slithery_fight_v0 3000/0, prisoners_dilemma_v0 3000/1, autarky_v0 3000/1, portals_v0 3000/0, 3001/0 and 3001/1, devil_v0 3001/1, maze 3001/0, weakhold 3000/1. Any of them prints with
`python3 data/local/hunter38/verify/recount.py --board base_portals_v0_3000_0 --back 5`.
The last three actions before all 23 non-spawn deaths are in `python3 data/local/hunter38/verify/tables.py last3`.

**3. The bot chooses a fatal step although a legal one exists: no, 0 of 44.** Ruled out at the fatal action. One step earlier it is true in 4 cases (the "her own step" row above).

**Ruled out:**
- the hunter closing her exits: no enemy dragon on a neighbouring tile in her last two actions in any of the 23;
- a paid or multi-step move: all 44 fatal actions were a single step;
- a timeout: no action of our side is flagged as timed out in any of the 168 games;
- a split that left her head without an exit: in each of the 6 hunter-run deaths with a split in her last three actions (and the 2 in the check run), she already had no way out at the split.

## What the code does (`~/meow-release/mybot2/main.cpp`)

- **Last line of the turn**, lines 776 to 777: `ct.make_move(best)`. `best` comes from `pick_direction`, which starts at NORTH with a score of twice `SCORE_REJECT` (lines 5185 to 5186). A kelp edge or an occupied tile keeps `SCORE_REJECT` (lines 5221, 5236 to 5240). Line 5361 adds a small tie-break that depends on dragon id, round and direction, and line 5369 takes the highest. With four blocked sides the tie-break alone picks the side.
- **What is tried before that**, in order: the waiting split when she is 4 or longer (lines 671 to 677, `queen_wait` at 3697 to 3722, `QW_MIN_LENGTH = 4` at 124); a portal as the last way out when nothing can be entered (lines 681 to 706); the escape split of `length - 2`, again only from length 4 (lines 708 to 714, `escape_child_size` at 1111 to 1135). A queen of 2 or 3 has none of these.
- **Portals.** `score_portal_step` (lines 5151 to 5182) returns `SCORE_PORTAL = -1e9` (line 377) for a banned portal, which still beats `SCORE_REJECT = -1e15` (line 383). So a portal is taken whenever everything else is blocked, ban or no ban. The check that a portal leads into a small pocket exists (`portal_into_pocket`, lines 3083 to 3089) and is switched off (`POCKET_PORTAL_BAN = false`, line 171).
- **Queen-only protection is gated by map size.** `is_queen()` (lines 3332 to 3334) is true only when the map has more than `QUEEN_MIN_CELLS = 600` cells (line 159) or `home_closed` is set (lines 505 to 511). The dead-end penalty and known-room requirement (lines 4994 to 5005), the queen portal ban (lines 3693 to 3695) and `QUEEN_ALLY_BLOCK` (line 4960) all use it. portals_v0, devil_v0 and tower_defense have 512 cells and weakhold exactly 600, so there she is steered as a plain dragon unless `home_closed` was set.
- **Our own dragons as blockers.** `QUEEN_ALLY_BLOCK = false` (line 163, used at 4960 and 2997) and `QUEEN_GIVE_WAY = 0` (line 195, used at 5006 to 5013): both ways of keeping team-mates from closing her exits exist and are off.
- `fallback_direction` (lines 5636 to 5652) runs only after an exception (lines 5661 to 5665) and plays no part here.

## Check run against plain main

The earlier count is right: 2 wall and 1 own body in 32 games. All three are on weakhold and all three were forced. The hunter run has the same 3 in 32 on the same four maps. The hunter run looks different only because 13 of its 17 maps are not in the check run, and 41 of its 44 deaths are on seven of those.

## Claim D

Numbers recounted and equal to the earlier ones. Per game, trauma (off / on, pairs in the order 3000/0, 3000/1, 3001/0, 3001/1):

| | switch off | switch on |
|---|---|---|
| our queen's pearls before round 300 | 7, 4, 5, 5 | 0, 0, 0, 0 |
| our queen's length at round 300 | 5, 2, 3, 3 | 2, 2, 2, 2 |
| enemy queen's length at round 300 | 5, 5, 3, 3 | 4, 4, 5, 4 |
| our queen's pearls from round 300 | 32, 0 (she died), 29, 36 | 22, 34, 21, 18 |
| enemy queen's pearls from round 300 | 17, 38, 26, 42 | 47, 47, 35, 30 |
| final length, ours against theirs | 37:22, 0:43, 32:29, 39:43 | 24:37, 36:51, 23:40, 20:34 |
| result | win, loss, win, loss | 4 losses |

What can be said:
- **Supported as a description of these 8 games:** with the switch on she eats nothing before round 300 on trauma and enters the growth phase 2 long against an enemy queen of 4 to 5. This is the same in all 4 games and follows from her looping on 95.8% of her decisions there.
- **Not supported:** that the enemy queen eats more because ours loops. The pairs differ by +30, +9, +9 and −12. The enemy queen's pearls before round 300 are the same in both arms (26 and 27).
- **Wins:** 2 of 4 against 0 of 4 on trauma, and 3 of 5 against 0 of 6 over the queen-rule games. Neither is beyond what such small numbers give by chance (about 1 in 5 and 1 in 16 if the switch did nothing).
- **The two lines of claim D are mostly the same games.** 4 of the 5 switch-off and 4 of the 6 switch-on queen-rule games are the trauma games. The other two switch-on games are ones where our queen died (maze 3001/0 and weakhold 3001/0). The 276 enemy pearls after round 300 in that line include 116 from the single maze game.

## Definitions that would mislead a reader

- **"Forced"** in the earlier tables leaves her tail tile free. For a 2-long queen that turns every dead end into "had a safe move".
- **Head-on deaths.** 52 of the 64 in the hunter run happened during an enemy dragon's action, 12 during her own. For the 52, "forced" or "had a safe move" describes the board when the enemy started moving and says nothing about her choice.
- **Wall and own body** are reported as two causes. They are one situation with an arbitrary last step.
- **Dead queens count as 0 in the mean lengths.** The switch-on "17.17 at the end" over 6 queen-rule games is 25.75 over the 4 queens still alive.
- **Rounds are labelled 0 to 499.** "Round 9" is the tenth round and "before round 50" is the first 50 rounds.
- **"Ended on the queen rule"** picks different games in each arm, so the two columns are not the same games.
- **Mean death round** in `result.md` (98.7 against 130.7) includes 12 map-forced deaths per arm at rounds 4 to 9.
- **This recount's own limits.** "Way out" freezes every other dragon, looks 16 single steps ahead and ignores pearls and splits. "Next to her head" means the four neighbouring tiles at the start of her last two actions.

## Could not determine

- What the bot saw or scored: the replays carry no bot logs. In particular whether `home_closed` was set on the maps of 600 cells or fewer, which decides if the queen-only rules were active there.
- Whether an enemy further away steered her toward these tiles. Only adjacent tiles were checked.
- Whether a different earlier step would have saved her in the 16 "board changed" cases.
- Why dragons on tower_defense produce no action from round 401. The bot has no suicide command, so it is a turn with no output. `none_check.py` shows the counts.
- Why both queens eat more after round 300 in the switch-on trauma games (254 pearls together against 220).

## Smallest changes that would test a fix (ideas only, nothing edited)

1. **Nothing for autarky_v0, prisoners_dilemma_v0, slithery_fight_v0.** The queen cannot survive there. The 24 deaths should be left out of any "queen survival" number.
2. **Our own dragons closing her exit (18 of 20, plus 3):** turn on `QUEEN_GIVE_WAY` (line 195) so team-mates are penalised for stepping next to her, or `QUEEN_ALLY_BLOCK` (line 163) so her room count treats their tiles as closed. Read out: wall, own-body and other-body queen deaths on portals_v0, devil_v0, maze, weakhold, islands and tower_defense with the same seeds and sides, now 23 in the 48 games on those maps (both arms together).
3. **Maps of 600 cells or fewer:** set `QUEEN_MIN_CELLS` (line 159) to 0 for one run so `is_queen()` holds on portals_v0, devil_v0, weakhold and tower_defense. Without it change 2's `QUEEN_ALLY_BLOCK` has no effect there. 14 of the 20 deaths are on those maps.
4. **portals_v0:** turn on `POCKET_PORTAL_BAN` (line 171) and let it also apply in the last-resort branch (lines 681 to 706), so a portal into a sealed cell does not count as room or as a way out. In these 8 games the portal step only delayed death by one action; the step to prevent is the one before, onto the tile beside the portal with a team-mate adjacent.

## Files

- `recount.py`: the count; writes `deaths.json` (both queens, every death) and `games.json`. `--board` draws boards.
- `tables.py`: `deaths`, `maps`, `foe`, `last3`, `head`, `claimD`.
- `compare.py`: row by row against `deaths/rows.json`.
- `none_check.py`: the no-action deaths on tower_defense.

All run from the repo root with `python3 data/local/hunter38/verify/<name>.py`.
