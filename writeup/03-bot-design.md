# 03. The final bot (one21): how it works, every switch, and the history of versions

Written 2026-10-10, the day after the qualifier deadline. Folder names used below: `S` = jun's private repo `unsw-swarm`,
`B` = the team repo worktree `battlecode/.claude/worktrees/one13-into-main` (branch `one15-profile`, commit `44fae14`),
`R` = the local game rig `~/meow-redteam`. Times are KST. Marks: **[M]** = a number measured and written down at the
time, **[R]** = my reading of the code or of the record.

## The five things to take away

1. **The bot is one old program plus 49 switch values.** `B/mybot2/main.cpp` (8,657 lines) is the team's bot with every
   later idea behind a compile-time constant that is off by default. `B/work/server_profile.txt` lists the 49 values that
   make it "one21". This design is why 21 versions could ship in 16 hours with no crash or timeout on record; keep it.
2. **Most switches were never shown to help.** By my count of section 2.1, eight of the 49 values have a comparison on
   record that shows a gain of their own; for about twenty the intended behaviour was counted but wins did not move or
   were not separated; the remaining twenty or so are "no difference", "no harm seen" or not measured. Local
   head-to-head games on new maps said that nothing added between one5 and one11 was a clear gain [M].
3. **Seven of our own additions were taken out again** (section 3.3). Two of them (`PORTAL_SCOUT_MIN_LEN`,
   `TERRITORY_DECAY`) passed the local test as "neutral" and still broke whole maps online for three to four and a half
   hours. A test set that lacks a map feature cannot clear a switch that acts on that feature.
4. **The queen decides the game and the queen code is the weakest part.** By the last day's count our queen died in 28
   of one15's 30 losses [M]. Most late switches are queen patches layered on each other, and three of the last four
   uploads (one19, one20, one21) carried a repair for a hole opened by an earlier upload of the same day.
5. **The last three uploads (one19, one20, one21) had no online game on disk at the deadline** [M]. What is known about
   them is only "plays the same local games as the version before, except where intended".

## 0. The game in ten lines (only what this chapter needs)

A rectangular grid that wraps around at the edges. Walls between cells are called kelp; portals join two far cells.
Each team runs up to 64 dragons (snakes). Every dragon is a separate process running the same program and sees only
the 7x7 square around its head. Dragons talk only by sonar, a 64-bit message sent along a line. A dragon eats a pearl
to grow by one; pearls reappear on fixed cells after a countdown that is visible. A dragon may split (the rear part
leaves as a new dragon; minimum length 2), or move. The first ceil(L/4) steps of a turn are free, each extra step costs
one body cell (we call that a paid step or sprint). Moving the head into a wall or any body kills the mover; head into
head kills both. A dragon that gives no action dies. After 500 rounds the team with the **longer queen** wins; the queen
is the dragon with the lowest starting id (0 or 1), and a dead queen counts 0. Tiebreaks: longest living dragon, then
total length. Rules: `S/rules/` (movement.md, splitting.md, vision.md, sonar.md, death.md).

Because a dragon must act every turn, **the only way to stand still is to split**. That costs the rear 2 cells each
time and is behind several queen problems below.

---

## Part 1. Architecture

### 1.1 Files and build

| file | what it is |
|---|---|
| `B/mybot2/main.cpp` | the whole bot: constants 20-473, small structs 475-566, `class Bot` 568-8620 (member data 8349-8620), `main()` 8641 |
| `B/mybot2/helper.hpp`, `sonar_codec.hpp` | the organisers' C++ API wrapper and our sonar scrambler (keyed by map size and team) |
| `B/work/server_profile.txt` | `NAME value` lines, the 49 live values |
| `B/work/server_bot.py` | copies the bot folder and rewrites each `constexpr ... NAME = ...;` to the profile value. It refuses to run unless every name matches exactly one line |
| `R/solo/src/solo/main.cpp` | the working copy; byte-identical to `B/mybot2/main.cpp` (checked with `diff` today) |
| `R/solo/src/solo/main.cpp.pre-one*-1009`, `R/solo/src/w-*` | the source before each version, and one work folder per candidate |
| `S/data/online/smoke/one<N>-bot/` | the exact folder uploaded for each version (`one1-bot` to `one21-bot`; submission ids from one5 on in `versions.tsv`) |

Build the live bot: `python3 work/server_bot.py OUT` in `B`. Three checks were run before the uploads and are worth
keeping as a habit [M, `S/docs/SESSION-STATE.md` lines 444-858]: (1) all switches off gives the same binary hash as
before (`92fb69564fbd`), (2) the previous version's values give the previous version's binary, (3) the uploaded copy on
the server equals the local folder.

### 1.2 One turn, in the order the code runs

`main()` (8641) creates one `Bot` and calls `take_turn()` (630) each round inside a `try`; any exception falls back to
`fallback_direction()` (8621), a step into any free neighbour.

| step | function (line) | what happens | origin |
|---|---|---|---|
| 1 | `take_turn` 630 | clears per-turn state, calls `act()`, then runs the post-move guards (1.7), then `broadcast_leader()` | old; guards are switches |
| 2 | `observe` 2705 | reads round, length, head; rebuilds its own body from a remembered trail (`trail`, `enter_time`); reads sonar; scans the 49 visible tiles into the map memory; lists ally and enemy heads | old |
| 3 | inside `observe` 2874-2890 | `update_lifecycle`, feeding targets (`compute_drop_cells` 4127, `pick_feed_target` 4164), leader zone, `map_rivals` 4266, `map_threats` 4323, `map_hits` 6315 (queen only), `mark_trade_targets` 4580, `mark_hunt_targets` 4448 | old + switches inside |
| 4 | `act` 1666-1730 | queen bookkeeping: home cell, "queen game" flags, `herd_update` 5346 (`QUEEN_HERD`), `target_prepare` 4889 (`TARGET_REACHABLE`) | mixed |
| 5 | `act` 1732 `hunt_path` 4528 | if a hunt target is within sprint reach, ram it now and end the turn | old; `QUEEN_SURE_*`, `HUNT_SMALL_RATIO`, `LUNGE_PEARL` widen it |
| 6 | `act` 1743 `ready_to_die` 7635 | a feeder standing on a drop cell beside the leader returns without acting, which kills it and leaves its pearls for the leader | old |
| 7 | `act` 1752-1795 | picks a far "route target" if any: leave a barren region (`escape_update` 7489), chase the enemy queen, rally | old; `QUEEN_AVENGE` |
| 8 | `pick_direction` 8048 | scores the four neighbour steps with `score_step` 7667 (or `score_portal_step` 7917), adds lookahead `look_gain` 5630, applies the queen's ring veto and the long-dragon veto, returns the best step | old core; many switch terms |
| 9 | `act` 1802-1996 | the action ladder (1.6): ram, queen emergency branch, wait-split, emergency portal, escape split, long escape, ordinary split, multi-step stride, single step | old; switches listed in 1.6 |
| 10 | guards 661-699 | may replace the action already sent (the engine keeps only the last action of a turn) | all switches |
| 11 | `broadcast_leader` 3310 | sends one sonar message per direction | old; far-head and queen pings are switches |

### 1.3 What a dragon knows

- **Map memory** (per dragon, never shared as a whole): `north_edge` / `west_edge` hold what lies between two cells
  (unknown, open, kelp, portal), `north_portal` / `west_portal` the portal ids, filled by `remember_edge` 2621 and
  `remember_portal` 2641. `seen_round`, `pearl_here`, `pearl_timer` (rounds until a cell next tries to spawn), `hot`
  (cells seen to respawn often, `note_hot` 2941).
- **Own body**: `trail` (deque of past head cells) and `enter_time[cell]` (0 = free now, otherwise how many rounds
  until our own body or a seen body clears it). A freshly split child does not know its tail (`tail_index < 0`) until
  it has moved its own length; several rules skip while that holds.
- **Enemy model**: only heads in view (`enemy_heads`), plus `ghosts` (heads seen in the last 3 rounds, `update_ghosts`
  4292). An enemy's size is the number of its body cells **in view** (`visible_parts` 2976). `map_threats` floods from
  each head for as many steps as that size allows and stores a depth per cell (`threat_depth`). For the queen,
  `map_hits` 6315 builds two rings for this turn only: cells an enemy can enter on free steps ("hit") and cells it can
  enter by paying ("pay", up to `QS_PAY_REACH`). `risk_at` 6491 returns 2, 1 or 0.
- **Sonar** (`hear_sonar` 3270, `broadcast_leader` 3310): the main message is "the longest dragon I know of: id,
  length, round, cell, facing" (`pack_leader` 3160), which is how the swarm agrees on a leader. Other kinds: a portal
  mouth is occupied (`pack_mouth` 4023), an enemy-queen sighting (`pack_queen_ping` 3962), and with `QUEEN_FAR_HEADS`
  an enemy head near our queen (`pack_far_head` 3019). `sonar_enabled` (610) is false when either side of the map is
  129 or more, because coordinates are packed in 7 bits.

### 1.4 Roles (all decided locally each turn)

| role | test (line) | behaviour |
|---|---|---|
| ordinary short dragon | default | eat, split at length 4 into 2+2, explore |
| leader | `is_leader` 5713 | after `grow_round` (300 on maps of 1,200 cells or fewer, 150 on larger) the longest known dragon stops splitting and grows |
| feeder | `is_feeder` 7604, `feeding_phase` 7630 | after round 400, or once we hold 56 dragons after `FEED_CAP_ROUND`, short dragons near the leader walk to a drop cell and die there |
| trader | `is_trader` 6091 | length 4 or less with a marked enemy head in view: is pulled to it and rams (`ram_path` 4644) |
| queen | `real_queen` 6141 = lowest id; `is_queen` 5717 = the same **only on maps above 600 cells or with a closed start region** | threat rings, no feeding role (`QUEEN_NO_FEED`), dead-end terms, portal rules, wait-split |

The `real_queen()` / `is_queen()` split is the single most error-prone thing in the file [R]. Old queen rules use
`is_queen()` and so do nothing on small maps; newer ones use `real_queen()`. `dead_queen()` 5722 chooses between them by
`QUEEN_DEAD_ALL`. Two of our reversals (section 3.3) came from flipping a rule across this 600-cell line.

### 1.5 How a step is scored (`score_step` 7667)

`survey_from` 5002 floods outward from the candidate cell through known-free cells and returns a `Survey` (struct at
528): reachable area seen and unseen, the share of it this dragon reaches before any seen ally or enemy head
("territory"), distances to the nearest pearl, soon-to-spawn cell, hot cell, unseen cell, portal, feed cell and trade
target, and whether the flood reaches our own tail. The score is then, in order: space and territory (7687), penalties
for too little room (`PENALTY_TIGHT`, `PENALTY_TRAPPED`, `PENALTY_NO_TAIL`, 7694-7705), the queen dead-end penalty
(7715-7726), the single best target bonus (7742), the pocket penalty (7771), the eat bonus (7779), `SPAWN_CLEAR`
(7784), the leader's pearl zone (7793), the centre pull in the opening (7796), enemy threat (7804-7827), `QUEEN_HERD`
(7857), feeder and trader pulls (7907-7912). There is no search over opponent replies; safety is one-turn reach maps
plus penalties. `look_gain` adds an 8-step pearl lookahead for the mover only.

### 1.6 The action ladder in `act()` (1802-1996)

First match wins: (a) `ram_path` 1803; (b) the **queen emergency branch** 1810-1875, entered when every clean step is
gone (`hit_blocked`): free sprint to a clean cell, else stand and split off 2 when her own cell is safe (1823), else a
paid sprint, else shed down to 2 (1834, limited by `QS_SHED_MAX`), else `QS_LONG_WAIT` (1838), else step onto a cell
the enemy must pay to reach (1844), else "trapped": act as a plain dragon for this turn (1855); (c) shed when no step
exists and she is in reach (1877); (d) `queen_wait` 1883: split off 2 and stay when cramped; (e) an emergency portal
when nothing else is enterable (1893); (f) escape splits and sprints (1926-1954); (g) the ordinary split
`split_child_size` 2314; (h) a free multi-step move `extend_stride` 2033; (i) the single best step (1994).

### 1.7 Post-move guards (all switches, 661-699)

Each simulates the chosen move and, if it fails a test, sends a different action: `keep_queen_exit` 1169
(`QUEEN_EXIT_KEEP`, and with `strict` for `QUEEN_EXIT_STRICT`: a mate must not take the queen's last free
neighbour), `keep_mate_exit` 1424 (`MATE_UNPIN`), `keep_out_of_pocket` 968 (`POCKET_KEEP_OUT`), `guard_queen_corridor`
788 (`QUEEN_CORRIDOR_GUARD`). They share copied code for rebuilding the body and stepping it; a fix in one usually
needs the same fix in the others [R].

### 1.8 Old team bot against switches

Everything above except what is marked a switch is the team's bot as merged through the card loop (queen mode, threat
maps, feeding, stride, wait-split, `QUEEN_SAFETY` rings are on by default in the source: lines 116, 138, 142, 147, 207,
439, 455). The switch layer came from jun's solo project (started 10-07 evening, `S/docs/SESSION-STATE.md` line 16)
and the last night's work. PR text: `S/archive/final-session-scripts/pr-one13.md` (+2,523 / -93 lines against main).

### 1.9 Before you change anything

- Add behaviour as a new `constexpr` that is off by default, and prove the all-off binary did not change. Removing a
  line from the profile is then a safe rollback of one idea.
- Know the size cliffs: 600 cells (`QUEEN_MIN_CELLS`), 700 (`CENTER_SMALL_CELLS`), 1,200 (`AGGRESSIVE_MAX_CELLS`: ram
  limits, leader round), 128 per side (sonar), 56 / 60 / 64 dragons (`ATTACK_MIN_UNITS`, `SPLIT_SOFT_LIMIT`, engine cap).
- Enemy size is what is in view. Any rule that says "safe because the enemy is short" is wrong when the body runs out
  of the 7x7 view; only the queen has a floor (`CUT_BODY_LEN`).
- One process per dragon: a 60-dragon game uses 4 to 5 cores locally [M, line 790], so local throughput is CPU-bound.

---

## Part 2. The switches

Evidence classes: **gain** = a comparison on record shows the intended effect and no loss; **behaviour** = the intended
behaviour was counted, the result (wins) was not shown to improve; **no harm** = only "same games elsewhere";
**none** = not measured. "Local" means games on jun's machine, usually against the old team bot ("old main").

### 2.1 On in the final profile (49 values)

| switch = value | plain meaning | first live | evidence on record |
|---|---|---|---|
| `ZONE_NEARER` true | a pearl nearer to me than to the leader is mine, not the leader's | v62 | gain, local: 64 pairs, wins 48 to 54 (+6 -0); no gain on large maps [M, lines 68, 81] |
| `POCKET_LOOP` true | a small room with a portal in it is a way through, not a dead end | v62 | gain on one map family: rebuilt Stripes, pearls by r100 19 to 49, wins 10 to 12 of 12; 48 other pairs identical [M, lines 23, 33] |
| `HARVEST_PORTAL` true | a dead-end room behind a portal may be entered to eat and split out | v62 | behaviour: with POCKET_LOOP pearls +37%; alone 8 wins against 10 [M, line 33] |
| `SPAWN_CLEAR` true | do not stand on a cell about to spawn a pearl | v62 | gain, local 64 pairs: natural pearls eaten +12.3%, wins 48 to 50; cost seen: own-body deaths 3.49 to 4.49 per 1,000 turns [M, line 60] |
| `TRADE_EVEN` true | a short dragon may ram a head of equal size | v62 | behaviour: even trades 2/23 to 19/44; wins 13 to 14 of 72 [M, line 19] |
| `LEADER_FULL_UNITS` 56 | on maps above 1,200 cells a would-be leader shorter than 10 keeps splitting until we hold 56 dragons | v62 | behaviour: alive at r300 51.7 to 57.2; wins 17 to 18 of 18 [M, line 30] |
| `HUNT_SMALL_RATIO` 2 | a dragon of 4 or less rams a head at least twice its length | v62 | behaviour: chance taken 0.28 to 0.92; wins 6 to 5 of 12 [M, line 58] |
| `QS_KEEP_LEN` 3 | the queen does not split below 5; paid escape before a standing split | v62 | gain, online 30 games: queen turns at length 2 41% to 9%; value 4 tested later and lost 19-2-27 [M, lines 102, 675] |
| the eight above as one bundle | | v62 | gain, online: 23/60 against main 21/90 on the same maps and hours, paired 12 to 3 (sign test p 0.035); with QS_KEEP_LEN 14/30 [M, `S/data/guide/px-p61-final.txt`] |
| `QUEEN_HERD` true | the queen's score pulls her toward mates | one1 | behaviour: turns with no mate within 5 cells 33% to 18% local, 31-42% to 20% online; threat turns rose 6.3 to 11.6 per 100 [M, lines 417, 452] |
| `QUEEN_DEFEND_STEPS` 3 | a short mate rams a head within 3 steps of our queen | one1 | no harm: fired 3 times in 8 local games, online events did not rise [M, lines 430, 452] |
| `SPLIT_ROUND0` true | starting dragons split in round 0 | one1 | behaviour: dragons at r20 7.0 against 6.0, level from r100; online r0 splits 18/27 against 3/27 [M, line 435]. Cost on a 7x7 corridor map, see part 4 |
| `FEEDER_EAT` true | a feeder still eats a pearl beside it | one1 | behaviour: events 129 against 97 and 87 online [M, line 452] |
| `QW_END_ROOM` 1 | no wait-split when the room ahead lasts to round 500 | one1 | none after shipping; reason: one game lost 28 to 44 after 28 needless wait-splits [M, line 115] |
| `LUNGE_PEARL` true | a pearl on the way to a ram costs no reach | one2 | with the next two, local: 15 wins of 16 against old main on 1,536-cell maps; without the 56 condition it lost a small open map on both sides [M, lines 443, 595] |
| `TRADE_SHORT_BY` 1 | a head one shorter than ours is worth a ram | one2 | as above |
| `ATTACK_MIN_UNITS` 56 | the two above only while we hold 56 dragons | one2 | as above |
| `FEED_CAP_ROUND` 350 (was 200) | feeding at the dragon cap starts after r350 | one3 | gain, local 8 big-map pairs: total length at r300 418 to 484, at the end 409 to 447 [M, `px-live-one3.txt`] |
| `HEADING_TIE` 1.5, `HEADING_TIE_ROUNDS` 12 | in the first 12 rounds a short dragon breaks a tie for straight ahead | one4 | behaviour on one start layout: first pearl r30/r48 to r11/r13; weakest bundle arm locally (8 of 16) [M, `px-live-one4.txt`, line 595] |
| `EAT_FIRST` true | a pearl one step away is eaten even if a mate is nearer the ground beyond | one5 | behaviour: corner pearl eaten at r9 instead of r19-34; first time level with a mid-table team at r100 [M, `px-live-one5.txt`, `px-live-one6.txt`] |
| `QUEEN_EXIT_KEEP` true | a mate does not take the queen's last free neighbour | one7 | none of its own; closed exits were still 10 of 21 queen deaths two versions later [M, line 621] |
| `PORTAL_ID_GUARD` true | ignore portal ids far above the cell count | one7 | none; never fires on known maps (a guard for unseen maps) |
| `QUEEN_AVENGE` 8 | when our queen is dead and theirs alive, dragons of 4 or less hunt her within 8 | one7 | measured as **not working**: never armed in five lost games [M, `px-live-one10.txt`]. It also switches off the old queen-hunt scout (`qh_watch` 3826-3835) [R, unmeasured] |
| `QS_KEEP_MIN_UNITS` 2 | the keep-3 rule applies only while we have 2 or more dragons | one8 (6 in one9-12) | gain: 2 against 6 won 29-2-17 locally; without any floor, new 7x7 maps went from 6-4-6 to 2-1-13 [M, `px-live-one13.txt`, `px-live-one8.txt`] |
| `MATE_UNPIN` true | do not pin a mate against a wall | one8 | none of its own ("effect not confirmed", line 621) |
| `POCKET_KEEP_OUT` true | queen and dragons under 4 do not step into a cell whose only way on is their own neck | one8 | none of its own (same audit) |
| `TARGET_REACHABLE` true | a pearl behind an entry the bot refuses is not a target | one8 | none of its own (same audit); built for a dragon circling a portal for 145 turns |
| `SMALL_SPRINT_THREAT` true | short dragons price an enemy's sprint reach, not only its next step | one8 | none of its own. The four one8 switches together: rams on us 4.3 to 3.2 per 1,000 turns against one opponent, once; the same bot scored 8 then 4 of 15 [M, `px-live-one9.txt`, `px-live-one11.txt`] |
| `QUEEN_SURE_LEN` 64, `QUEEN_SURE_STEPS` 5 | any dragon but queen and leader rams their queen's head when it can reach it in 5 steps | one8 (4 / 3), one10 | behaviour: 8 of the enemy queen's 10 deaths in one10 games were our rams [M, line 621] |
| `REACH_EATS` true | an enemy's reach counts pearls it eats on the way | one9 | behaviour: our queen rammed 9 to 5 times in 15 games against one opponent [M, `px-live-one10.txt`] |
| `SPLIT_PORTAL_OK` true | a dragon with its tail by a portal may split if an ordinary exit is open | one9 | "effect confirmed" by an audit, number not recorded (line 621) |
| `CUT_BODY_LEN` 4, `QS_PAY_REACH` 4 | for the queen, an enemy cut by the edge of view counts at least 4 long; pay ring out to 4 | one10 | behaviour with REACH_EATS: queen rammed 9 to 4 against the same opponent [M, `px-live-one8-back.txt`] |
| `QUEEN_BOOT_LEN` 6 | late, mates of 2 or 3 may feed a queen shorter than 6 | one10 | none |
| `QUEEN_PORTAL_LAST` true | the queen enters an unseen portal only when she has no other move | one11 | none of its own |
| `CUT_BODY_STRIDE` true | the cut-body length also applies at the end of her multi-step moves | one11 | none of its own |
| `QUEEN_EXIT_STRICT` true | a mate of 2 or 3 never takes the queen's last cell and kills itself if that is its only move (Zhe's rule) | one11 | no difference: removing it scored 24-2-22 [M, line 675]. Known cost in a small start room, part 4 |
| `BIG_ESCAPE_STEPS` 6, `BIG_ESCAPE_MIN_LENGTH` 8 | a dragon of 8 or more steps out of reach of short enemies | one12 | no difference: removal 22-2-22 [M, line 678] |
| `QUEEN_FAR_HEADS` 2 | the queen's rings include enemy heads her mates saw in the last 2 rounds | one12 | no difference: removal 21-1-22 [M, line 678] |
| `QUEEN_CORRIDOR_GUARD` 6 | the queen refuses a step into a visible dead-end corridor when she has another | one12 | no difference: removal 22-2-21 [M, line 678] |
| `QUEEN_NO_BLIND_PORTAL` true | the queen never takes a portal whose far side nobody has seen | one16 | gain on one map: local Portals, queen dead by r100 6/7 to 1/8, wins 2/7 to 5/8, pearls -15%; 13 of 13 other maps identical [M, `pr-one16.md`] |
| `QS_SHED_MAX` 9 | a queen of 10 or more does not shed down to 2 | one17 | no difference online: 7 of 91 games lost that way before, 3 of 50 after [M, line 848]; opened a hole, see `QS_LONG_WAIT` |
| `QUEEN_CORRIDOR_MATE` true | the corridor guard looks past a mate's body when judging her other way | one18 | behaviour: fired in 2 of 17 local pairs, queen lived r155 to r192 and r258 to r331 [M, `pr-one19.md`] |
| `CENTER_MAX_CELLS` 100000 (was 1000) | the opening pull to the centre applies to long maps of any size | one19 | gain on one test map (never left the start room, now out at r26); slower opening on one long ladder map (dragons at r50 45 to 36), same results [M, lines 832, 848] |
| `QUEEN_NO_RAM` true | a trapped queen does not take the plain dragon's ram paths | one19, completed one20 | no harm: 9 of 9 pairs identical; reason: 22 of 286 queen deaths were her own ram [M, lines 828, 839] |
| `QUEEN_BLIND_STALL` 20 | lifts the blind-portal ban between r20 and r100 while we have 2 dragons or fewer | one19 | weak: 0 pearls to 10-14 on the test map, still lost [M, line 845] |
| `QS_LONG_WAIT` true | an exposed queen of 10 or more with no escape stays and splits off 2 | one21 | **none**: 4 short local games identical; "the effect itself is NOT measured" [M, `pr-one21.md`] |

### 2.2 In the code, off: live once and removed

| switch | live in | removed in | recorded reason |
|---|---|---|---|
| `QS_KEEP_ROUND` 20, `QS_KEEP_CLEAR` 6 | one4 | one5 | see 3.3 |
| `RALLY_END_FRESH` 25, then 5 | one6, one7-10 | one11 | see 3.3 |
| `SHORT_EVADE` (+ `SHORT_EVADE_PAID` 1) | one7, one9-10 | one8, one11 | see 3.3 |
| `QUEEN_PORTAL_ALL` | one10 | one11 | see 3.3 |
| `PORTAL_SCOUT_MIN_LEN` 4 | one12-13 | one14 | see 3.3 |
| `TERRITORY_DECAY` 16 | one12-14 | one15 | see 3.3 |
| `QUEEN_DEAD_ALL` | one6-18 | one19 | see 3.3 |

### 2.3 In the code, off: built and tested, never live in a "one" build

| switch | what it would do | recorded result |
|---|---|---|
| `QUEEN_WAR`, `WAR_FEED_FIRST` | all short dragons go for their queen once ours is dead | held back; its skipped splits were a confirmed small-map regression [M, line 621] |
| `QUEEN_EDGE_REACH` | assume a 3-long attacker just outside the queen's view | built, not live; the constant test was stopped for CPU (line 790) |
| `QUEEN_CORRIDOR_TREE` | corridor guard follows branches | dropped: 12 games unchanged, one flipped win to loss [M, line 837] |
| `SPLIT_KNOWN_TAIL` | a new child does not split before it knows its tail | dropped: Portals head-to-head 1-3, queen died early [M, line 843] |
| `HARVEST_SPLIT` | split at 4 even while harvesting a room | no difference 25-0-22; wins against old main 19 to 16 [M, lines 753, 759] |
| `CRAMPED_EAT` | eat in a tight room without the tight-room penalties | dropped 10-08: 128 pairs, alone 97 to 97, inside the bundle 105 to 98 [M, line 80] |
| `LEADER_GUARD_ROUNDS` 200 | the leader keeps off enemy heads late | good on big maps alone (54 pairs), worse on all maps (35 to 33 of 48); "keep" verdict withdrawn [M, lines 45, 53] |
| `QUEEN_FALLBACK` (card 55), `LONG_SAFETY` (card 54) | teammate cards: queen falls back when outnumbered; long dragons use the rings | card 55 online 3/15 against 4 and 6 for v62; both listed "worse online" [M, line 442, `S/data/codex/astra/CARDS.md`] |
| `EXPLORE_GAIN` 10 | a pull toward unseen ground | dropped: pearls on 8 maps 125 to 108, collapse on four [M, line 731] |
| `PORTAL_FAR_DECAY` 13 | portals attract from farther away | dropped: -23% pearls on one map, queen death on another [M, line 813] |
| `QUEEN_HOME_LEASH` 3 / 6 | the queen stays near her start cell | 11-0-8 and 5-0-11, not shipped [M, line 778] |
| `QUEEN_HUNT`, `HERD_BEHIND`, wide `QUEEN_DEFEND_RADIUS`, `EAT_BONUS` changes, `SPLIT_MIN_LENGTH` 5 | | listed as tried and dropped in `CARDS.md`; defence radius 5: wins 37 to 32 of 58; split at 5: 4 wins to 10 [M, lines 430, 137] |
| `QUEEN_BRAIN`, `QG_SAFEZONE`, `QG_CORNER`, `SYM_INFER`, `SHARE_SIGHT`, `INC_PERIOD`, `ASSASSIN_MOD`, `IDLE_ESCAPE` and others | older team and solo experiments | reasons not looked up for this chapter; treat as untested |

### 2.4 Candidates tested in work folders that are not in the final source

Local head-to-head against the live version of the hour, wins-draws-losses [M, lines 524, 657, 670, 726-781, 824, and
`S/data/codex/astra/CARDS.md`]: enemy cut by view counts
8 long for everyone (`THREAT_HIDDEN_PARTS`) 8-0-14, long dragons turn timid; queen does not split near a head
(`QS_HEAD_CLEAR`) 20-0-17; queen refuses one-exit cells (`QUEEN_ONE_EXIT`) 23-0-23; skip unreachable pocket pearls
(`POCKET_PEARL_SKIP`) 15-0-14; queen holds length once their queen is dead (`QUEEN_HOLD_LEN`) 46-4-46, because our
dragons rarely learn that she is dead; queen keeps away from heads (`QUEEN_KEEP_AWAY`) "safe but weak"; mates leave
room for the queen (`QUEEN_ROOM_MATES`) queen died earlier in 4 of 6 pairs; queen cuts at the blocking segment
(`QUEEN_CUT_BLOCK`, Zhe) does not fire where it was meant to; two-step pearl rule (`EAT_FIRST_TWO`) dropped. Feeding
and leader growth from round 200 (Zhe) 5-13 and 5-11.

---

## Part 3. Version history

### 3.1 Before the "one" builds

| when | live bot | what it was | what was learnt |
|---|---|---|---|
| 10-05 08:22 | submission 17184 | team main + card 29 (safer multi-step moves) | `S/data/guide/px-live17184.txt` |
| 10-05 18:39 | 17594 | + card 25 (queen wait-split) | `px-live-17594.txt` |
| to 10-08 14:59 | "v47" 18570, parked copy "v44" 18504 | older main; later main (cards 48 and 51) was uploaded as v56 but not made live | line 203 |
| 10-07 20:04 on | (local only) | **solo project**: jun's private line in `R/solo`, two parallel lines of diagnosis and build, switches all off by default | switch bundles b6 (10-08 03:31) and b7 (05:08): 128 local pairs, wins 97 to 105 [M, line 74] |
| 10-08 08:45-15:19 | test bots "agg7", "agg8" | b7, and b7 + `QS_KEEP_LEN` 3, against main on the same 15 maps and hours | main 21/90, b7 23/60, + queen rule 14/30 [M, `px-p61-final.txt`] |
| 10-08 14:59 | **v62**, 20366 | main + the seven switches + `QS_KEEP_LEN` 3 | against three top teams still 3, 3 and 1 of 15 [M] |
| 10-08 18:56 | "agg9" | v62 + three attack switches | never played: the upload was refused while another team's ranked match was pending (line 408) |

At 22:19 on 10-08 jun decided: one combined bot is live, a bad result is answered by fixing the switch that failed,
never by going back to an old bot. The builds from then on are "one1", "one2", ...

### 3.2 one1 to one21

| version | live from | submission | change | why | learnt afterwards |
|---|---|---|---|---|---|
| one1 | 10-08 22:29 | 20850 | v62 + `QUEEN_HERD`, `QUEEN_DEFEND_STEPS` 3, `SPLIT_ROUND0`, `FEEDER_EAT`, `QW_END_ROOM` 1 | stop testing piece by piece | opening and queen company moved as meant; 4/15 against the mid-table test team (v62: 6 and 4) |
| one2 | 23:02 | 20880 | + `LUNGE_PEARL`, `TRADE_SHORT_BY` 1 under `ATTACK_MIN_UNITS` 56 | the pair had lost a small map unconditioned | not separated online |
| one3 | 23:36 | 20910 | `FEED_CAP_ROUND` 200 to 350 | feeders died from r201 in 11 of 11 games at the cap | total length grew r200-300 in 4 of 5 such games; 2/15 and 1/15 |
| one4 | 10-09 00:10 | 20941 | + queen early split (`QS_KEEP_ROUND` 20), `HEADING_TIE` | top teams split the queen in round 0 | the queen split was a loss (3.3) |
| one5 | 00:49 | 20980 | - queen early split, + `EAT_FIRST` | corner pearl lay 19-34 rounds | level with the test team at r100 for the first time; in later local head-to-heads nothing up to one11 beat one5 |
| one6 | 01:35 | 21033 | + `RALLY_END_FRESH` 25, `QUEEN_DEAD_ALL` | 49 of 69 longest-dragon decisions lost | 1/15 and 3/15; rally cost length (3.3) |
| one7 | 02:31 | 21086 | rally 25 to 5, + `SHORT_EVADE`, `QUEEN_AVENGE` 8, `QUEEN_EXIT_KEEP`, `PORTAL_ID_GUARD` | 559 rams on non-queens by r200; all 10 losses to weaker teams had our queen dead | level with one5; evade did nothing |
| one8 | 03:09 | 21126 | - `SHORT_EVADE`, + `SMALL_SPRINT_THREAT`, `QS_KEEP_MIN_UNITS` 2, `MATE_UNPIN`, `POCKET_KEEP_OUT`, `TARGET_REACHABLE`, `QUEEN_SURE_LEN` 4 | per-game analysis of losses to teams 100+ points below | "first version that moved": 8/15 and 9/15; two hours later the same bot scored 4/15 |
| one9 | 04:00 | 21165 | + `REACH_EATS`, `SPLIT_PORTAL_OK`, `QS_KEEP_MIN_UNITS` 6, `SHORT_EVADE` with a paid step | queen rammed by dragons eating on the way | queen rams 9 to 5 against one team; the 6 was a loss (3.3) |
| one10 | 04:35 | 21200 | + `QUEEN_SURE_LEN` 64 / steps 5, `CUT_BODY_LEN` 4, `QS_PAY_REACH` 4, `QUEEN_PORTAL_ALL`, `QUEEN_BOOT_LEN` 6 | the avenge rule never fired; queen hit from one step further than allowed for | 12/15 against that team, 3/15 against another |
| (one8 again) | 05:23 | 21126 | rollback of one9 and one10 | one10 scored 3/15 where one8 had 8/15 | **a mistake**: one8 replayed scored 4/15 against the same unchanged opponent. A 15-game set cannot separate two versions |
| one11 | 06:01 | 21269 | one10 - `SHORT_EVADE`, - rally, - `QUEEN_PORTAL_ALL`, + `QUEEN_PORTAL_LAST`, `CUT_BODY_STRIDE`, `QUEEN_EXIT_STRICT` | 10 of 21 queen deaths were a closed exit | local head-to-head against one8: 17-2-29, against one5: 21-2-24 |
| one12 | 07:08 | 21330 | + `BIG_ESCAPE` 6/8, `TERRITORY_DECAY` 16, `QUEEN_FAR_HEADS` 2, `QUEEN_CORRIDOR_GUARD` 6, `PORTAL_SCOUT_MIN_LEN` 4 | first version tested before upload: 40-3-29 against one11 on 24 new maps | two of the five switches were broken on ladder maps (3.3) |
| one13 | 08:07 | 21377 | `QS_KEEP_MIN_UNITS` 6 to 2 | 29-2-17 against one12 | declared final at 09:01; 45 online games: 18 (one11 17, one12 14) |
| one14 | 10:24 | 21497 | - `PORTAL_SCOUT_MIN_LEN` | found from a 1-4 loss to a team 90 points below | portal maps came back; 21 of 45 |
| one15 | 11:44 | 21583 | - `TERRITORY_DECAY` | one map still starved; found by removing each one12 switch in turn | that map 17 to 57 pearls by r100; local ladder wins 15 to 22 of 32 |
| one16 | 12:51 | 21651 | + `QUEEN_NO_BLIND_PORTAL` | queen died in 30 of 30 games on one portal map | no queen portal step in r0-99 online; later found to starve a blind start box |
| one17 | 13:31 | 21693 | + `QS_SHED_MAX` 9 | 21 sheds from 10+ in 474 games, 18 lost | sheds gone, long queens die about as often; opened the hole one21 patches |
| one18 | 14:10 | 21761 | + `QUEEN_CORRIDOR_MATE` | three games thrown from a lead on one maze map | fired 2 of 17 local pairs, both correct |
| one19 | 14:36 | 21827 | - `QUEEN_DEAD_ALL`, `CENTER_MAX_CELLS` 100000, + `QUEEN_NO_RAM`, `QUEEN_BLIND_STALL` 20 | all four found in the last hour by running on never-seen maps | 20 pairs: pearls by r100 522 to 1,036, wins 8 to 12; lost both seats on one portal map head-to-head |
| one20 | 14:43 | 21843 | code only: `QUEEN_NO_RAM` also skips target marking; blind-portal lift limited to r20-100 | holes named by a reviewer | 17 local games identical to one19 |
| one21 | 14:49 | 21857 | + `QS_LONG_WAIT` | Zhe's match 1532574: a queen of 11 stepped into a cell an enemy could sprint to | not measured. Final bot. No online game of one19-21 was on disk at 15:00 |

Sources: `S/data/guide/px-live-one*.txt` (one per version), `S/docs/SESSION-STATE.md` lines 444-858,
`S/data/online/smoke/versions.tsv`, `git -C B log`. Ladder standing during the night: 51st / 2,018 at 05:23, 27th /
2,158 at 09:01, 41st / 2,092 at the deadline [M, lines 681, 861]. By jun's account the team went out in the
quarterfinal on 10-10; the bracket games were not available to me.

### 3.3 Reversals of our own switches, and what each cost

| switch | on | off | time live | measured cost | why the test missed it |
|---|---|---|---|---|---|
| `QS_KEEP_ROUND` 20 (queen splits early) | one4 00:10 | one5 00:49 | 39 min | queen split 4 to 2 before r20 in 21 of 30 games, stayed 2 for a median 40 rounds, never regrew in 4; gained nothing (8.9 against 8.8 dragons at r25) | an earlier local run of the same idea from round 40 had already shown 7 to 16% less total length from r100 and it was set aside (lines 420, 435); it then shipped at round 20 on the argument that top teams split their queen early |
| `RALLY_END_FRESH` 25, then 5 | one6 01:35 | one11 06:01 | 4 h 26 min (one8 carried it too) | at 25: gave up 14 dragons and 26 length after r400 to add 6 to the longest; walkers followed stale leader reports | built from a count of lost decisions, no paired test first |
| `SHORT_EVADE` | one7, one9 | one8, one11 | about 2 h in two spells | none proven; rams on us unchanged (4.16 against 4.13 per 1,000 turns); suspected of costing early pearls | a rule judged only by the count it was built to move |
| `QS_KEEP_MIN_UNITS` 6 | one9 04:00 | one13 08:07 | about 3.5 h | queen 2 long in 31% of her first 100 rounds against 13%; a queen of 2 dies 1.27 times per 100 rounds, of 4 0.35; the build with 6 lost 17-2-29 locally to the build with 2 | raised for more early dragons on two-dragon starts, checked only on those 17 games |
| `QUEEN_PORTAL_ALL` | one10 04:35 | one11 06:01 | 48 min of play | "trapped her on portal maps"; a confirmed small-map regression (line 621); win cost not measured | blanket ban; replaced by "only when no other move" |
| rollback to one8 | 05:23 | 06:01 | 38 min | not measured; one10 was level or ahead | compared 15 games against 15 games from two hours earlier |
| `PORTAL_SCOUT_MIN_LEN` 4 | one12 07:08 | one14 10:24 | 3 h 16 min | pearls by r100 on one portal map 238 to 71, others 41 to 4, 92 to 36; short dragons' portal steps 32 to 4 a game, zero in 48 of 108 games; a 1-4 ranked loss worth -33 points | local removal test 21-2-21: the new test maps had few long portals |
| `TERRITORY_DECAY` 16 | one12 07:08 | one15 11:44 | 4 h 36 min | one map: 2-3 dragons at r100, pearls 59 to 17; no-eat loops 2.1% to 5.3% of dragon rounds (suspected) | local removal test 22-3-21, and an economy sweep had shown +9% length on new maps |
| `QUEEN_DEAD_ALL` | one6 01:35 | one19 14:36 | 13 h | on maps of 600 cells or fewer the queen took every small room for a dead end; one test map 0 pearls in 500 rounds; 20 pairs without it: pearls 522 to 1,036, wins 8 to 12. Online cost not measured | cleared by a count of changed turns (37 of 30,004, `px-live-one6.txt`), not by games on small maps with rooms; found only on purpose-built maps in the last hour |

Two more chains are the same pattern in small: `QUEEN_NO_BLIND_PORTAL` (one16) starved a side whose only exit is a blind
portal, patched by `QUEEN_BLIND_STALL` (one19); `QS_SHED_MAX` (one17) sent a long queen down the next branch into a
paid attack, patched by `QS_LONG_WAIT` (one21).

### 3.4 What this history says about judging a version

- **Lesson: decide the yardstick before the night, and make it able to see what the change touches.** Three yardsticks
  were used. Online sets of 15 games per opponent: the same bot scored 8 and then 4 of 15, so they separate nothing
  [M]. Local head-to-head on 24 generated maps, 48 games: separated one12 and one13 from one5, and passed two broken
  switches because those maps lacked the feature. Per-map behaviour tables (pearls and dragons at r100 by map and
  version): this is what found both broken switches and it was only built after the damage (`regress`, line 695).
- **Next time**: keep the per-map behaviour table running from the first version, and add a removal test on the real
  ladder maps for every switch before it ships. This transfers to any game with distinct map families.
- **A switch that changes behaviour "almost nowhere" still needs one game where it fires.** `QUEEN_AVENGE`,
  `QUEEN_DEFEND_STEPS` and the hold rule were all safe and all did nothing because their trigger almost never occurred.
- **Bundles hide losers.** one7 to one12 shipped 3 to 7 changes each, and most of the switches that were later
  removed entered inside such a bundle and stayed for hours.

---

## Part 4. If you continue this bot: known weak points, checked against the source

Line numbers are for the final file. The lead's log (line 863) lists these; I checked each.

| weak point | what the record says | what I found in the code | where to look |
|---|---|---|---|
| The queen steps toward a visible head and is rammed | against one team 19 of 21 rams came right after her own step one cell toward the attacker, typically gap 3 to 2 against a 3-long (one free + one paid step) [M, line 855] | [R] No rule pulls her toward a non-queen head. Two things let it happen. (1) In the emergency branch, when no clean step exists and she is too short to split, line 1844 deliberately steps onto a "pay" cell; the enemy pays one cell and hits. (2) The rings are for this turn only, so a clean cell one step nearer is as good as any other; only the soft depth penalty (7804-7811) counts distance. A queen of 4 or less is also a "trader" toward the **enemy queen's** head (6091-6094, 8152) | `act` 1814-1875, `map_hits` 6315, `score_step` 7804. The distance-only fix was tried and was weak (`QUEEN_KEEP_AWAY`); the analyst's reading was that the lever is where she lives, not which step she takes near a head |
| A long queen shrinks standing still | a queen of 15 went to 4 in rounds 370-376 while their queen was dead; the log names "line 1797", an older numbering [M, line 826] | Confirmed. It is now line **1823**: hit-blocked, own cell safe, so she splits off 2 and stays, every turn. `QS_SHED_MAX` guards only the shed at 1834. The wait-split at 1883 (`queen_wait` 6108) does the same when cramped: 72 events in 38 of 509 games, 332 cells, one result flipped [M, line 810]. Also unguarded: the shed at 1877 when she has no step at all [R] | 1823, 1877, 1883, 6108 |
| 7x7 maps | open 7x7 maps lose to old main since one7-one9, no constant found; on a 7x7 corridor map `SPLIT_ROUND0` causes an early suicide [M, line 822] | Not verifiable from the source alone. Relevant code: `SPLIT_ROUND0` only presets `harvest_round` (8495) so the split gate at 2353 opens in round 0; the keep-3 rule (2331) was the earlier 7x7 culprit | `split_child_size` 2314; test map `R/maps/un2/uc_tiny7x7.map` |
| Closed start rooms | on two test maps the other dragons leave and the queen stays and is wiped out; in a 288-cell room a mate kills itself in round 1 (`QUEEN_EXIT_STRICT`) and with that off the queen dies in round 2 [M, line 832] | Cause not established. Switching off eight switches one at a time changed nothing (`S/data/codex/astra/unB-opus/a-room20.txt`). Whether old main does the same is not recorded. The strict suicide is lines 1382-1402. These rooms open through a corridor, so they are not the "closed start region" that `QUEEN_HOME_CLOSED` (1691, 6592) detects [R] | `keep_queen_exit` 1169, dead-end terms 7710-7726; maps `R/maps/un2/ub_room20.map`, `ub_tworooms`, `ub_room3` |
| Tower Defense compartments | dragons stop at the door of small pearl rooms; our right-hand start starves; `CRAMPED_EAT` opens the rooms but lost pearls in a single game (44 to 39) [M, line 823] | Consistent with the code: a room smaller than 3 x length + 8 without a way to our tail is a dead end (`entry_dead_end` 4856) and draws `PENALTY_TIGHT` (7694); harvesting is allowed only under `harvestable` 2475 | 7689-7705, 4856, 2475, `CRAMPED_EAT` 7692 |
| Sonar off on wide maps | all sonar stops when a side is 129 or more [M, line 799] | Confirmed: line 610, used at 3271 and 3315. Ladder maps were 24 to 64 per side, so this never occurred in play; the engine accepts up to 256 (line 541) | 393, 610; the packing in `pack_leader` 3160 |
| Queen-exit search has no node cap | noted by an audit, never timed [M, line 799] | Confirmed: the breadth-first search at 1354-1380 has no limit on nodes or depth. In strict mode the mover is 2 or 3 long so it is tiny; in `QUEEN_EXIT_KEEP` mode a long mate has ceil(L/4) free steps plus paid steps and the state includes the whole body [R]. An analyst's 30+ games on unusual maps showed no crash or timeout (0.8-2.3 ms a turn, line 822); the search itself was never timed | 1354-1380 |

Found while checking, not in the lead's list [R, none measured]:

- `QUEEN_AVENGE` > 0 makes `qh_watch` return early with the old hunter flags cleared (3826-3835), so the team's
  earlier queen-hunt scout is off in the final bot while the rule that replaced it was measured as never arming.
- `long_escape` 4696 leaves when `threat_at` is 0, and threat is sized by visible body cells, so a long dragon reads a
  half-seen attacker as harmless. Of 33 rams on our dragons of 8 or more in two battles the attacker was fully in view
  in 3 [M, line 692].
- The four guards in 1.7 each carry their own copy of the body simulation.

If there is one thing to build first, the record points at the queen's position rather than her reflexes: her death
is in almost every loss, the patches on her last-moment choices listed in 2.4 came out level in head-to-head, and the
one observation about opponents is that their queen stays near her start (within 2 cells by one analyst's note, line
765; at r50 ours was a mean 12.7 cells from her start against 7.7 for the opponents in those games, line 731). That is
a reading, not a tested plan, and the one direct test of it, `QUEEN_HOME_LEASH`, came out 11-0-8 and 5-0-11.

## Looked for and not established

- The result and games of the 10-10 bracket; nothing in the folders I was given records them.
- Any online evidence for one19, one20 or one21.
- A per-switch result for `MATE_UNPIN`, `POCKET_KEEP_OUT`, `TARGET_REACHABLE`, `SMALL_SPRINT_THREAT`,
  `QUEEN_PORTAL_LAST`, `CUT_BODY_STRIDE`, `QUEEN_BOOT_LEN`, `QUEEN_EXIT_KEEP`, `PORTAL_ID_GUARD`: they shipped in bundles.
- The number behind "`SPLIT_PORTAL_OK` effect confirmed".
- Why the older off switches in the last row of 2.3 were abandoned.
- The cause of the queen staying in a closed start room, and of the open 7x7 losses.
- Whether switching off the old queen-hunt scout through `QUEEN_AVENGE` was intended.
