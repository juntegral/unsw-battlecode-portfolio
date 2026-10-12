# Ladder pipeline schema

Team **meow, 1119**. All `us` / `them` pairs are symmetric. `our_side` is A if
`game-<id>.json.teamAId == 1119`, B if `teamBId == 1119`; the initial replay
DRAGON rows attach dragon IDs (their line order) to those sides (team 0 = A,
team 1 = B). Each side's lowest initial ID is its queen (always 0 or 1 here).
Opponent names are labels, not a classification rule.

Last audited 2026-10-07 (see "Audit" at the end): every field below marked
*recounted* was recomputed for all 625 games by separate code on the official
viewer's decoder and matched in every game.

## Files and loading

`battles.jsonl` and `rows.jsonl` contain one JSON object per line. They are
atomically replaced in chronological order, with ID breaking ties. The row
builder skips existing game IDs, except `--rebuild`; submission attribution is
refreshed even for skipped rows. `map-observations.json` is an incremental cache
of replay headers, natural birth counts and respawn intervals, keyed by game ID.
`maps.json` combines those observations by **`map_key`** (not by map name, see
below). `new-this-hour.json` is a list of newly completed battle IDs from this
collector invocation. Incomplete battles remain in the battle ledger with
`complete: false` and are retried. `python3 tools/ladder_collect.py --recheck`
refreshes `games` / `complete` from the files on disk without a server call.

```python
import sys, json
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, scan
from ladder_rows import make_row
folder = Path('data/online/ladder/12345')
meta = json.loads((folder / 'game-12345.json').read_text())
root = replay.load(folder / 'M12345.replay').root()
# root.text(0): initial map; root.text(1) / root.text(2): bot id of side A / B
# (ours is filled, the opponent's is blank); root.pointer(3): true-state events;
# root.pointer(4): result. Event kind: replay.EVENT_NAMES[event.u16(0)].
row, state = make_row(folder / 'M12345.replay', meta)
```

The shared parser uses the team's existing `battlecode/replay.py`, via the
existing `data/online/smoke/fountain-analysis-2/count.py` loader. Its path is
relative to the shared project parent, as in that script. It does not run that
script's CLI or write its outputs. True-state reconstruction in
`tools/ladder_replay.py` is adapted from `drop-analysis/count.py:scan`.
Initial body deques, dragonUpdate head/tail, dragonSplit bodies, and deaths
rebuild the board exactly; final alive / longest / total / queen length are
asserted against the replay result. Portals follow paired EDGE IDs; ordinary
steps wrap. Edge ids: north edge of (x,y) = `2y(W+1)+x`, west edge =
`(2y+1)(W+1)+x`; the east edge of the last column is the west edge of column 0
and the south edge of the last row is the north edge of row 0 (the server lists
each shared edge once; `ladder_replay.edge_id` does the wrap).
Parse inconsistencies fail the step rather than manufacture game values.

## Battles (`battles.jsonl`)

- `id`, `ranked`, `opponentId`, `opponent`, `opponentElo`, `eloChange`, `results`,
  `wins`, `losses`, `outcome`, `replayId`, `at`: unchanged server battle-list
  values. `at` is the server completion timestamp. Finished means ranked,
  final outcome win/loss/draw, and all result entries win/loss/draw.
  `opponentElo` is the opponent's rating when the battle was played (it differs
  between battles against the same team); `eloChange` is ours for the battle.
- `at_kst`: ISO timestamp converted to Asia/Seoul, or null if no timestamp.
- `games`: ordered `{id, map}` records from downloaded game metadata / index,
  sorted by game ID, the series order used by the server's result list
  (checked: all 625 game winners agree with `results` in this order).
- `complete`: true only if finished metadata and a whole replay file exist for
  every expected result entry. Whole = the file has the byte size the download
  recorded and, if it is gzip, reads to the end (server replays are not gzip).
  Partial downloads do not count as done; a file that fails is kept with an
  incomplete timestamp suffix before retry.
- `our_submission`: one submission ID whose wins+losses+draws count increased
  in the enclosing consecutive poll interval `(previous.time, current.time]`.
  Must be present in both polls. Multiple increases, no increase, a battle
  before the first poll, or after the last poll all yield null. This is
  poll-based attribution and is null for everything before 2026-10-07 00:59 KST.
  **Use the row's `our_bot` instead**; it is read from the replay.

`data/online/ladder/active.jsonl`: one object per successful poll. `time` is
KST after the server response; `active` is null or `{id, version, name,
sourceHash, rating}` copied from the active submission (missing server fields
remain null). `submissions` contains `{id, wins, losses, draws}` for every
submission. Draws are retained so a completed draw can increase game count.
`data/online/ladder/submissions.json`: `{id: {version, name, description,
sourceHash, uploadedAt}}` for every submission of ours, refreshed at each poll.
The collector has a separate nonblocking lock; downloads are sequential,
one second apart, capped at 150 battle calls per invocation.

## Game rows (`rows.jsonl`)

Missing measurements are null. `notes` maps dotted field paths to reasons.
A zero is a measured zero, not a missing value. Counts and states use the
replay's **true state**, including information unavailable to bots.

- Identity: `battle`, `game`, `map` (server map name), `time` (game
  completedAt, UTC), `opponent_id`, `opponent`, `opponent_rating` (the battle
  list's `opponentElo`: their rating at that battle), `ranked`, `our_side`.
- `map_version`, `map_key`: one map name can cover more than one layout
  (Schooltime and Prisoners Dilemma each have two in this data, both in use
  through the whole period). A layout is the size, the edges and the starting
  dragons, ignoring which team is which colour. `map_version` numbers a name's
  layouts by first game; `map_key` is `"<name> #<version>"` and is the key of
  `maps.json`. Join rows to map properties on `map_key`.
- `our_bot`: which of our submissions played, read from the replay itself
  (the replay stores our submission id for our side and nothing for the
  opponent): `{id, version, name, source` (first 10 hex of the source hash)`,
  test` (its description starts with "TEST")`, same_code_as` (all our versions
  with the same source hash)`}`. Null only if the replay has no id.
  `our_code`: the team's name for that source code: `main` (the current main,
  v39 = v40 = v44 = v47, ids 18066 / 18068 / 18504 / 18570), `v31` (the old
  live bot, id 17790, same source as v25 / v26), otherwise
  `"v<version> <submission name>"` (test builds and v36), or `unknown` (with a
  note) when the id is missing or not in `submissions.json`. The name follows
  the source hash, so a build uploaded as a TEST that has main's source is
  `main` with `our_bot.test` true. Confidence: exact per game. Checked: one id
  per battle in 125 of 125 battles; the opponent's id blank in 625 of 625; the
  ids follow the upload log through every test window; where the log and the
  replay differ (135 games) it is hand or tool switches between the two copies
  of main, which the log does not record.
  `our_submission`: the battle's poll-based value (null so far), kept for
  comparison only.
- `win`: boolean, whether the replay winner equals our side; draws are false.
  `result`: win/loss/draw, retaining the draw distinction for server checks.
  *Recounted*, and equal to the battle list's `results` in all 625 games.
- **`ended_by`: the one field for how the game ended.** `elimination` (the
  replay's end reason: a team had no dragons left at the end of a round; the
  game stops before round 500), otherwise the first rule that separates the
  teams at round 500: `queen rule` (queen lengths differ, a dead queen is 0),
  `longest dragon` (queens equal, longest living dragons differ),
  `total length` (those equal too), `draw`. *Recounted.*
  **`queens_at_end`**: `both alive`, `only ours`, `only theirs`, `both dead`,
  from the final state. Read the two together: `longest dragon` is mostly
  `both dead` (205 of 239 games; 0 = 0 ties the queen rule), `queen rule` is
  mostly one queen dead (99 of 129), and an `elimination` can leave the
  winner's queen alive or dead. If the stored winner ever disagrees with these
  rules the row carries `notes.result` (no such game so far).
  `last_round`: last raw roundStart index (499 for a full game).
- `final.us` / `final.them`: `queen_length` (0 if dead), `longest`, `total`,
  `alive` (number of living dragons). All reconstructed and asserted against
  the replay's own result block. *Recounted.*
- `curves`: keys `50`, `100`, `150`, `200`, `300`, `400`, `end`. Each is null
  if that raw round never happened, otherwise contains `us` and `them` with
  `alive`, `total`, `longest`, cumulative `pearls`, `queen_alive`,
  `queen_length`. Snapshots are **after** all events in that raw round, before
  the next round starts; end is the final state. No extrapolation after an
  early elimination. Raw rounds are zero-based: a full 500-turn game ends
  after raw r499, so key `100` is the state after 101 rounds. The queen's
  `length.500` uses the true final state; other curve/length marks name the
  raw round index explicitly. *Recounted.*
- `queen.us` / `queen.them`: *recounted*
  - `id`, `alive` (boolean/null at each of the six curve rounds), `alive_end`.
  - `death_round`, `death_cause`, `death_length`: raw round and body length
    immediately before dragonDeath. Survivors have null round/length and
    cause `none`. The cause is the engine's own reason: 0 = wall, 1 = own
    body (this includes stepping onto her own tail tile, which the engine
    checks before the tail moves), 2 = other dragon body, 3 = head-on,
    4 = other (no valid action). Reason 2 remains other dragon body even when
    that dragon belongs to the same team; this differs from the older drop
    script's allied-body grouping. For all 278,194 deaths the engine's reason
    also equals what the mover's next step runs into on the rebuilt board.
  - `death_other`: null unless the cause is `other`, then one of the
    `deaths_other` kinds below.
  - `death_hit_id`: body owner for reason 2 when resolved, otherwise null.
  - `head_on`: null unless head-on, then `{attacker, victim, attacker_side}`.
    The action's actor rammed the stationary victim; the paired victim
    death occurs first, actor death second. Both IDs and side are true-state.
  - `length`: keys `100`, `200`, `300`, `400`, `500`; 0 if already dead at
    a reached marker, null if the game ended before the marker. `500` is
    the completed 500-turn boundary (end of raw r499), not an extrapolation.
  - `pearls_eaten`: tile removals attributed to queen followed by her move
    update; `splits`: dragonSplit events with queen as parent. Whole-game
    counts; children do not inherit the queen identity.
- `deaths`: keys `r0-100`, `r101-300`, `r301-500`, each contains `us` / `them`
  counts for wall, own body, other dragon body, head-on, other. Windows use
  the death's raw round index, include raw r0, and contain both head-on deaths.
  The windows are not equally long: 101, 200 and 199 rounds. *Recounted.*
- `deaths_other`: the same windows and sides, splitting the `other` count by
  what the dying dragon had asked for: `no action` (it sent no move or split:
  a deliberate suicide, a crash or an empty reply; the replay cannot tell these
  apart), `illegal split`, `unpaid sprint` (a move with more steps than its
  length could pay for), `timeout` (the turn ran out of CPU points). The four
  sum to `deaths.*.other`. In this data every one of our 15,964 `other` deaths
  is `no action` and none is a timeout. *Recounted.*
- `head_on.count`: number of cross-team paired head-on meetings, once per
  meeting, not per death. `same_team_count` is retained separately.
  `drops.us` / `drops.them` contain: *recounted*
  - `total`: pearls actually spawned after those cross-team head-on deaths
    on body segments 0,2,4,..., asserted equal to ceil(death_length/2).
    `drops.us` are the pearls dropped by our dragons.
  - `eaten_within_15.us/them`: dropped pearls removed and eaten within raw
    round difference <=15, including same-round (0) meals. Event identity
    keeps repeat births on the same tile distinct.
  - `not_eaten_within_15`: later meals plus unconsumed pearls observed for
    at least 15 rounds. `censored`: still unconsumed when the game ends less
    than 15 rounds after the drop; their 15-round fate is unknown.
  - `eaten_by_end.us/them/nobody`: legacy whole-game definition retained for
    exact comparison with drop-analysis/count.py. The earlier report uses
    end-of-game consumption, whereas within-15 is the additional time limit
    requested here. Every share uses `total` as denominator; counts are
    retained to avoid ambiguous denominators.
- `pearls`: the same three windows, each `{eaten: {us, them}, our_share}`.
  Counts include naturally spawned and dropped pearls, use the meal's raw
  round, and share is us/(us+them), null if neither side ate a pearl.
  A pearl is credited to the dragon whose turn removed it. *Recounted.*

## Map properties (`maps.json`, keyed by `map_key`)

These are geometry / supply descriptions, not name-based bot policy tables.
There are 19 entries for 17 map names.

- `name`, `version`, `versions_of_name`, `first_game`, `last_game`,
  `games_observed`: which layout this is and the games it was seen in.
- `width`, `height`: MAP header.
- `open_tiles`: tiles with at least one non-kelp edge; kelp blocks edges,
  not tile occupancy, so isolated tiles are excluded under this definition.
- `wall_share`: blocked incident directions / (4*width*height); equivalent
  to blocked-edge share on the toroidal board. It is an **edge**
  share, not a fraction of wall-valued cells (this format has no such cells).
- `portals`: number of distinct paired portal IDs, not directed entrances.
- `queen_spawn_distance`: wrapped Manhattan distance between initial queen
  heads, ignores walls and portal shortcuts; not a path distance.
- `corridor_share`: open tiles with exactly two non-kelp neighbour directions
  divided by open_tiles; turns and straight corridors both count.
- `dragons_at_spawn` (per team), `queen_spawn_length`.
- Queen spawn (the smaller value of the two queens; the maps are symmetric):
  - `queen_spawn_room`: tiles she can reach from her head at spawn when every
    starting dragon segment, her own included, stays where it is (kelp blocks,
    portals pass), capped at 60. 0 means every first step is fatal.
  - `queen_spawn_region`: tiles in the kelp-bounded area her head is in,
    dragons ignored, her own tile counted, capped at 400. A small number is a
    sealed vault she can never leave and nobody can enter.
  - `queen_spawn_dead_end`: true if a queen has no run of 16 single steps that
    keeps her alive on that frozen spawn board (her tail tile blocks for the
    step, as in the engine). This is the "trapped at spawn" test of
    `data/local/hunter38/verify/recount.py`.
  True on three entries: **Schooltime #1 and #2** (a sealed 2x2 vault,
  region 4: the queen can only split once and circle; ours never died there in
  42 games, theirs died in 7) and **Slithery Fight #1** (a 25-long queen coiled
  around her own head, room 0, region open). Queen statistics on these maps
  describe the vault or the coil, not play: exclude or separate them
  (`maps[row["map_key"]]["queen_spawn_dead_end"]`).
- Pearl supply. Server replays hide every tile's respawn gap (`TILE x y 0 0`).
  - `fast_supply_share`: **natural pearl births on fast tiles / all natural
    pearl births, over the observed games of this layout. The same definition
    on every map.** It is what was actually born in our games, so it depends on
    play as well as on the map (a fast tile only gives a new pearl after the
    old one is eaten). `natural_births` is the denominator. Births exclude
    pearls dropped by deaths.
  - `fast_tiles`, `supply_method`: how the fast tiles were identified.
    - `local gaps` (Around UNSW, Australia, Portals, Trauma): a local map file
      has the same size, edges, starting dragons (allowing a team swap) and
      tile set, and no observed natural birth falls on a tile it says never
      spawns. Fast = real `max_gap` between 1 and 12. `source` names the file.
    - `observed intervals` (the other 15 entries): a tile is fast when it has
      >=5 removal-to-next-natural-spawn gaps with median <=12 (the fountain
      analysis threshold). This is an estimate of which tiles are fast, not of
      the hidden gaps. `observed_intervals` gives `{n, median, mean, fast}`
      per tile `x,y`.
  - `fast_rate_share` (`local gaps` maps only, else null): share of the map's
    *potential* supply on fast tiles: expected rate per tile 2/(lo+hi), fast
    rates / all rates. This is the number the previous table called
    `fast_supply_share` on local-gap maps; it is far above the born share on
    the same map (Around UNSW 0.84 vs 0.31, Trauma 0.90 vs 0.35) and must not
    be compared with `fast_supply_share`.
  - `pearl_tiles`: `local gaps`: tiles with max_gap > 0. `observed intervals`:
    tiles seen to spawn at least once, a **lower bound**.
  - How far to trust the estimate. On the four maps with real gaps the
    estimate was run as well: 122 tiles called fast, all 122 truly fast; it
    missed 62 of 184 truly fast tiles, the ones rarely eaten; the estimated
    `fast_supply_share` was within 0.004 of the real-tile value on three maps
    and 0.04 low on Portals. Those maps' slow tiles all have max_gap >= 30; a
    server map with gaps between 13 and 29 could be misjudged either way. Use
    the share in broad bands (none / some / most), not to two decimals.
  - Local files that were rejected: `battlecode/maps/devil.map` and
    `queen_of_spades.map` have the server's layout but not its pearls (748 of
    13,647 and 487 of 11,133 natural births on tiles they say never spawn);
    the rejection reason is in `notes.source`.
  - Not separated: layouts whose pearls differ but whose header is identical.
    Slithery Fight splits into two groups of games by which tiles ever spawn
    (about 195 vs about 300 tiles per game), and on Devil and Queen Of Spades
    about half the games show the extra spawn tiles. These are probably two
    pearl layouts per name; their supply numbers here are pooled.
- `notes`: definitions / uncertainty and null reasons for that map.

## Audit (2026-10-07)

- Results and side: 625 of 625 games agree with the battle list's `results`
  (game-ID order), wins per battle agree in 125 of 125, `our_side` agrees with
  the team ids, the team names and the side the replay stores our bot id on.
  `tools/ladder_check.py` repeats the result and side check on every run.
- Definitions: all 625 games (not a sample) were recounted by separate code
  (the official 1.2.7 viewer's decoder in Node, own state rebuild) for
  `result`, `ended_by`, `queens_at_end`, `last_round`, `final`, `curves`,
  `queen.*`, `deaths`, `deaths_other`, `head_on.*`, `pearls`. No disagreement.
  The recount also matched the replay's own result block (dragons, longest,
  total, queen length) in 625 games and the winner the written rules give.
- Fixed in this audit: battles were all `complete: false` (the completeness
  check expected gzip replays) so the result check never ran; `ended_by` said
  `other` for total-length endings; map `wall_share` / `corridor_share` missed
  the kelp on the east and south border (15 of 17 maps, up to 0.02 / 0.04);
  two map names hold two layouts each; `fast_supply_share` meant two different
  things on different maps; two local gap files did not match the server.
- Added: `queens_at_end`, `our_bot`, `our_code`, `deaths_other`,
  `queen.*.death_other`, `map_version`, `map_key`, the queen spawn properties.
- Not checked or estimated: the hidden respawn gaps of 13 map names (see
  above); pearl layouts that share a header; `opponent_rating` is the server's
  number, taken as given; our own rating at each battle is not in the data.

## Runner and policy

`runner.log` records timestamp, step, start/ok/failed/skipped and a short
summary. `--once --no-ai` runs collect and rows only. The foreground loop
waits for the next hour, polls at intervening ten-minute boundaries, and
stops at 2026-10-08 20:00 KST, including in-flight subprocesses at the deadline. A flock prevents overlapping runners and is
inherited by children, so killing the supervisor does not free its lease
while a child is alive. AI stdout/stderr stream logs remain under logs/.
Verifier queues are archived and cleared only after successful verification;
failed verifier calls leave the queue intact. No AI has been run as part of
pipeline validation.

The PreToolUse guard is defence in depth, **not an OS sandbox**. Shell commands
are allowlisted; Python scripts / quoted heredocs get conservative AST checks
on literal or statically resolvable write targets and imports. Dynamic output
paths may be rejected; use Write/Edit or explicit paths. AI replay downloads
are blocked because online.js writes outside the permitted analysis directory;
the collector is responsible for those downloads. Verifier writes are limited
to verify/ and verify-results.json. Credentials, submission, confirmation,
posting, git mutations, raw networking and detached shell children are blocked.
