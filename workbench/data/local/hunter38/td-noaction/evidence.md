# tower_defense "no valid action" deaths from round 401: what they are

Checked 2026-10-07. Nothing in `tools/`, the bot source, git, Discord or the server was touched. Everything new is in
this folder; games were re-run on copies of the hunter38 bots (`rerun/base`, `rerun/hunter`).

## Answer

It is the bot's own feeding step, not CPU, not a crash and not a map rule.

From round 401 (`ENDGAME_ROUND = 400`) a small dragon that has reached its team's leader ends its turn **without
printing a MOVE or SPLIT** (it prints `LOG FEEDDIE ...` and returns). The engine's default action is suicide, and it
books that death as "no valid action". The dragon's body turns into pearls for the leader. The queen does it too on
maps of 600 tiles or fewer, because there the code treats her as a plain dragon.

"Always side A, whichever bot" is an effect of the two seeds in the test, not of the seat (see "Why one side").

## 1. The pattern in the raw replays (hunter38, 8 files)

`python3 data/local/hunter38/td-noaction/scripts/td_table.py data/local/hunter38/replays/*tower_defense*.replay`
and `scripts/td_line.py`, `scripts/td_state.py` on the same files.

`base_*` and `candidate_*` are event-for-event identical on this map (`td_state.py --same`), so the 8 files are 4
different games: 2 seeds x 2 seats.

| game (base = candidate) | A / B | result | units A:B, end of r400 | queen length A:B, end of r400 | no-action deaths A (rounds) | B (rounds) | queen A (id 0) | queen B (id 1) |
|---|---|---|---|---|---|---|---|---|
| 3000_0 | base / hunter | A, longest 27 to 2 | 29:1 | 3:9 | 19 (401 to 488) | 0 | r403 no action, 3 long | r479 head-on |
| 3000_1 | hunter / base | A, longest 59 to 6 | 30:2 | 3:9 | 23 (401 to 498) | 0 | r403 no action, 3 long | r432 head-on |
| 3001_0 | base / hunter | A, longest 36 to 11 | 18:2 | 2:3 | 14 (401 to 491) | 4 (436, 468, 491, 491) | r403 no action, 2 long | r436 no action, 2 long |
| 3001_1 | hunter / base | A, longest 29 to 22 | 11:3 | 2:0 | 15 (401 to 493) | 1 (470) | r403 no action, 2 long | r370 other body |

- First no-action death is round 401 in all four. None earlier.
- The dying dragons are 2 or 3 long in 73 of 76 cases (the others: 4, 7 and 11 long, all in 3001_1; `td_table.py`, "lens").
- Side B does it too when it has the units: 5 deaths in the two seed-3001 games, its queen among them.
- The report's "16 to 19 dragons" is 14 to 23 once all four games are counted.

## 2. The mechanism, with evidence

### Measured

1. **Every no-action death has a `FEEDDIE` log on that turn.** The hunter38 games ran with `--no-debug`
   (`harness/work/ab2.py` line 60), which drops bot logs from the replay. Re-run with logs kept, same bots, map and
   seeds (`rerun/logs_3000_0`, `_3000_1`, `_3001_0`, `_3001_1`): each re-run is event-identical to its original, and
   76 of 76 no-action deaths carry a `FEEDDIE` log from the same dragon in the same round. No other log kind appears.
   (`scripts/td_feeddie.py -v rerun/logs_*.replay`)
2. **The queen's last turn, raw output** (seed 3000, sandbox, `-v`; `rerun/sandbox/v.txt` line 49476):

   ```
   round 402: bot 0 (team A) stdout:   MOVE E / SONAR ... / PROTOCOL 3
   round 403: bot 0 (team A) stdout:   LOG FEEDDIE 3 50 9 / SONAR ... / PROTOCOL 3
   round 403: bot 0 (team A) points 4304545 memory 262144
   round 403: bot 0 (team A) died: no valid action
   ```

   `FEEDDIE 3 50 9` = her length 3, leader id 50, leader length 9. The process is alive, answers in full and ends
   the turn normally; it just sends no action. Of 7,006 turns in that game, 6,987 have a MOVE or SPLIT line and
   exactly 19 do not: the 19 no-action deaths.
3. **CPU.** The same game in the judge's sandbox (`--sandbox`, priced in CPU points, limit 100 million per turn) is
   event-identical to the native game.

   | | points per turn |
   |---|---|
   | the 19 no-action turns | 4.3M to 4.9M |
   | whole game, median / p99 / max | 7.2M / 18.5M / 26.6M |
   | limit | 100M |

   No "exceeded CPU limit" or "ran out of time" notice in any run here; 0 timeouts flagged in the 8 hunter38 replays.
4. **The code's gates hold on every logged case.** Over 120 logged FEEDDIE turns (5 logged games + 2 main-vs-main
   games): own length x 2 <= logged leader length in 120 of 120; the team had more than 3 units in 120 of 120
   (smallest team at a FEEDDIE: 4). (`scripts/td_gate.py`)
5. **It is not special to tower_defense.** All 136 hunter38 replays hold 15,076 no-action deaths on 14 of the 17
   maps (`scripts/td_allmaps.py ../replays`, about 6 minutes). What is special: only on tower_defense is a queen
   among them (10 of 10 queen cases: A's queen in 8 files, B's in 2).
6. **Removing the queen from the feed target removes her death.** On a copy (`rerun/variant/*_q/main.cpp`, one word
   changed at line 2303: `is_queen()` -> `real_queen()`), 8 games (seeds 3000, 3001, 3004, 3007, both seats): 0
   queen no-action deaths, 167 other FEEDDIE deaths still there. (`td_line.py rerun/variant/*.replay`)

### Read from the code (`mybot2/main.cpp`, same file as `bots/off/main.cpp`)

- Lines 551 to 554: `if (ready_to_die()) { ct.output_log("FEEDDIE", length, known_leader_id, known_leader_len); return; }`
  The turn ends with no `make_move` and no split.
- Rules, `unsw-swarm/rules/ALL.md` line 817: "Defaults are set: action = suicide"; line 529: No Valid Action covers
  "outputted no action"; line 533: "The engine treats a turn with no valid action as suicide".
- Lines 4924 to 4935 `ready_to_die`: she is a feeder, no enemy head within 4 (`FEEDER_ENEMY_CLEAR`, line 64), and
  she stands on a drop cell in front of the leader or within 3 of the visible leader (`FEEDER_DIE_DIST`, line 62).
- Lines 2296 to 2324 `pick_feed_target` decides who is a feeder: feeding phase, a known leader that is not herself
  and within 15 tiles (`FEEDER_APPROACH`, line 48), `length * 2 <= leader length` (`FEED_LEN_RATIO`, line 292;
  `feed_len_ok`, 4912 to 4917), team of more than 3 units (`FEEDER_KEEP_UNITS`, line 47).
- Lines 4919 to 4922 `feeding_phase`: `round > feed_round`, and `feed_round` starts at `ENDGAME_ROUND = 400`
  (lines 44, 472). Hence round 401. (Also earlier: 56 or more units after round 200, line 4921; round 300 in a
  "queen game", lines 149, 525 to 527. That is where the r201 and r301 starts on other maps come from.)
- **The queen.** Line 2303 leaves her out only through `is_queen()`. Lines 3332 to 3334: `is_queen()` is true only
  when `cells > QUEEN_MIN_CELLS` (600, line 159) or `home_closed`. tower_defense has 512 tiles. `real_queen()`
  (lines 3724 to 3726) has no size gate. That she logged FEEDDIE shows `is_queen()` was false for her at r403.

## 3. Why one side, and why whichever bot

- **Whichever bot:** the hunter is main with two constants changed (`bots/hunter.diff`), and on this map they play
  alike. main against main (`rerun/self/`) is event-identical to main against the hunter for both seeds. With the
  seats swapped the games are identical up to round 380 (seed 3000) and round 339 (seed 3001).
- **One side:** feeding needs more than 3 units and a leader twice the feeder's length. In these two seeds side A
  has 11 to 30 units at round 400 and side B has 1 to 3. Side B's 5 feed deaths come exactly when it has 4 or more.
- **Not the seat.** Six more seeds, both seats (`rerun/seeds/`, `td_line.py`):

  | seed | who has the no-action deaths (A / B, seat 0 game) | queen that died of it |
  |---|---|---|
  | 3002 | 2 / 53 | none (both queens dead by r267) |
  | 3003 | 2 / 4 | none |
  | 3004 | 27 / 0 (other seat 36 / 0) | A at r452 (other seat) |
  | 3005 | 0 / 38 | none |
  | 3006 | 0 / 8 | none |
  | 3007 | 4 / 3 | **B at r403** |

  And with the two teams' start rooms swapped on the map (`rerun/tower_defense_swapped.map`, seed 3000, hunter in
  seat A): B has 46, A has 0, B's queen at r401. (`td_line.py rerun/swap/*.replay`)
- **The map is fair in shape.** Tiles, kelp and start positions are exactly symmetric under a half turn
  (`scripts/td_map.py rerun/tower_defense.map`: 0 tile and 0 edge mismatches; the board wraps).

## 4. Ruled out

| guess | verdict | how |
|---|---|---|
| CPU or time budget | no | sandbox points 4.3M to 4.9M on those turns against 100M; 0 timeouts; the local test ran without any CPU limit at all (`NOSANDBOX=1`; rules line 889: only a 10 s wall clock), and a 500-round game takes 2 to 5 s in total |
| crash, exit, array bound | no | the dying turn prints its log, sonar lines and `PROTOCOL 3` and ends normally; engine exit code 0; no bot-error notice in any `.out` |
| malformed or empty output | half | the output is well formed; it has no action line, on purpose |
| engine or map rule at r400 | no | the engine has no such rule in the rules text. The map does change near r400: 38 tiles have a pearl gap of 400 to 500, so their first pearls appear then. A coincidence with `ENDGAME_ROUND`: the same deaths happen from r401 on portals_v0 and weakhold, and the FEEDDIE logs account for every one |
| map asymmetry | no | exact half-turn symmetry; other seeds put side B ahead |

## 5. Does it matter

**The other 2- and 3-long dragons:** this is the feeding plan working as written. Not judged here.

**The queen:** under the queen rule (longer queen wins, a dead queen counts 0) she gives up whatever she had.

- Hunter38, 4 games: no result changes. In 3000_0 and 3000_1 she was behind anyway (3 against 9) and the game was
  decided on longest dragon only because B's queen died later (r479, r432). In 3001_0 both queens fed themselves.
  In 3001_1 the enemy queen had been dead since r370, so A was 2 to 0 ahead on the queen rule, threw that away at
  r403 and still won on longest dragon, 29 to 22.
- The variant runs (queen never feeds) are single games that drift after r403, so they are not a strength test.
  One of them shows the limit of the fix: seed 3000, her queen lives at 2 long and the side with 29 units against 1
  loses "longer queen, 11 to 2".
- **Online (real server), `data/analysis/ladder/rows.jsonl`, 660 games, read only:** our no-action deaths are 0 in
  rounds 0 to 100, 3,580 in 101 to 300 and 13,549 in 301 to 500, so feeding runs online as it does locally. Our
  queen died of no action in 2 of 660 games, both on maps of 512 tiles, both lost:
  - game 1163279, Tower Defense, against Proof by Intimidation, bot v31: their queen was dead from r58, ours was
    alive (2 to 3 long), so we led on the queen rule. She died with no action at r418 (4.86M points, no timeout)
    and we lost on longest dragon, 24 to 37. **Inferred:** had she lived to r500 this was a win; whether she would
    have lived 82 more rounds with 3 units against 40 is not known.
  - game 1160662, Prisoners Dilemma, against SHINK AI 6500: she died at r401, 3 long; their queen ended 35 long.
    Lost either way.
- Online Tower Defense, 38 games, 69,049 of our turns: max 36.6M points, 0 timeouts. 107 no-action deaths of ours,
  4.3M to 5.5M points each, first one per game at r401 or later in all 17 games that have any. Our queen was still
  alive at r400 in 8 of the 38.
- Exposure is narrow: maps of 600 tiles or fewer where our queen is still alive after r400.

## 6. The three replays

`replays/` (logs kept, so the viewer shows the FEEDDIE line; `tools/replay_fix.strip_padding` leaves them unchanged)

| file | bytes | gz | what it shows |
|---|---|---|---|
| `td1_seed3000_mainA_queenA_feeds_r403.replay` | 1,585,900 | 361,464 | the reported case: main in seat A, 19 feed deaths r401 to 488, queen 0 at r403 while B's queen is alive and 9 long. Event-identical to `base_tower_defense_3000_0` |
| `td2_seed3001_mainB_queenA_feeds_r403.replay` | 815,461 | 188,687 | the hunter in seat A does the same; its queen gives up a 2 to 0 queen lead (B's queen dead since r370). main in seat B has one feed death at r470. Identical to `base_tower_defense_3001_1` |
| `td3_seed3007_mainA_queenB_feeds_r403.replay` | 790,171 | 186,608 | the other side: B's queen feeds herself at r403, both sides feed (A 4, B 3), A wins "longer queen, 20 to 0" although B has the longer dragon (24 to 20). Not in hunter38; made here |

**Ways to share**
- Attach by hand in Discord: all three are under 2 MB, far below the 10 MB limit, so the `.gz` copies are not needed.
  Viewer: https://game.battlecode.au/visualiser, choose the file, go to rounds 401 to 403.
- `tools/meowbot.py --announce-file` posts text only (JSON `content`, at most 2,000 characters; lines 1177 to 1196).
  The bot's only attachment path is the card "needs-look" message (`send_state_message`, lines 564 to 612: up to 3
  replays from `~/meow-loop-out/card-N/look.json`, gzip above 8 MB). It is tied to a card state, not a one-off post.
- Regenerate from the team repo at main `0e03867`, unswbc 1.2.7 (measured here: same game as td1; the sandbox makes
  it repeatable, another unswbc version was not tried):

      unswbc run tune_runs/official127/tower_defense.map mybot2 mybot2 --sandbox --seed 3000 -o td3000.replay

  Add `-v` to see `LOG FEEDDIE` in each dying dragon's output.

## 7. Commands

All from `unsw-swarm/`, with `S=data/local/hunter38/td-noaction/scripts` and `U=../battlecode/work/bc127/bin/unswbc`.

    python3 $S/td_table.py data/local/hunter38/replays/*tower_defense*.replay      # per-game table
    python3 $S/td_state.py data/local/hunter38/replays/base_tower_defense_*.replay # units, longest, queens by round
    python3 $S/td_feeddie.py -v data/local/hunter38/td-noaction/rerun/logs_*.replay # death <-> FEEDDIE log
    python3 $S/td_gate.py data/local/hunter38/td-noaction/rerun/logs_*.replay      # length and unit gates
    python3 $S/td_line.py data/local/hunter38/td-noaction/rerun/seeds/*.replay     # other seeds
    python3 $S/td_map.py data/local/hunter38/td-noaction/rerun/tower_defense.map   # drawing + symmetry
    cd data/local/hunter38/td-noaction/rerun
    $U run tower_defense.map base hunter -o x.replay --seed 3000                   # with logs (native)
    $U run tower_defense.map base hunter --no-replay --sandbox -v --seed 3000      # points and raw output per turn

## 8. Limits and things not settled

- Two seeds in the original test; 8 seeds in all here, one game per seed and seat. Counts, not rates.
- The online replays carry no bot logs, so online the FEEDDIE path is inferred from the same signature (death
  reason, round 401 or later, 4 to 5M points, recorded action = the default, suicide). Both online queen cases are bot v31, not
  current main; that v31 has the same lines was not checked.
- Why `home_closed` stays false on tower_defense (the queen starts in a walled room) was not looked at; only that
  `is_queen()` was false at r403.
- Why side A is so far ahead by round 300 in seed 3000 (26 units to 4; 9 to 4 in seed 3001) was not looked at. A
  hint only: in seed 3000 the side that starts in the left-hand room is ahead in both layouts (A normally, B on the
  swapped map). One seed, not established.
- One no-action death before r401 on devil_v0 (r379) and the r201/r301 starts on bigger maps were counted, not
  traced. They fit the unit-cap and queen-game starts in the code; not verified per death.
- Whether the queen should feed at all on small maps is a design call for the bot's authors. The variant is a
  mechanism check on a copy, not a proposal that was tested for strength.
- The engine is a compiled wasm (`unswbc_engine.wasm`); "no valid action" conditions are taken from the rules text
  and from the observed output, not from engine source.
