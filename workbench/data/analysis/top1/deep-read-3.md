# Why our economy falls behind: a read of our games next to top-team games on the same maps (sub-session A3)

Written 2026-10-05 for team meow (1119).

The question. On large maps we have 39 units and total length 116 at round 200; the teams we play have 61 and 254 against us
(`findings.md`). Why? This file reads 30 of our games and 25 games of the three top teams (Vibing++ 306, SSS 91, "forgot to
mention" 264) against the same two opponents we mostly play, test4 (19) and WeHaveQuizzes (87, "WHQ" below), on ten maps, and
backs every claim with a count over all games where that was possible: our 401 games against 2000+ teams and about 1,400 games
of the top three (Schooltime left out everywhere).

How it was read. Every game with `c_econ.py` (per 10 rounds and side: economy, deaths by kind, spread, what every dragon-turn
was, speed to a pearl, sprints, contact, fountain tiles) and `c_ledger.py` (where total length comes from and where it goes; it
balances to the segment); where a number needed explaining, `story.py events / view`, `c_tiles.py` (every fountain tile in one
game) and `c_mid.py` (the mid-game by length class and dragon by dragon). Counts over all games: `c_agg.py` (the `c_econ.py`
numbers of 1,795 games), `c_gap.py`, `c_rams.py`, `c_ramlocal.py`, `c_ramsteps.py`, `c_contest.py`, `c_adj.py`, `c_zone2.py`,
`c_avoid.py`, `c_midall.py`, `c_tilesall.py`, `c_deadcells.py`, `c_freedeaths.py`, `c_front.py`, `c_endstate.py`, and by bot build
`c_batches.py`, `c_bybatch.py`, `c_rambatch.py`, `c_pairs.py`. All outputs are in `c_out/`. A replay shows positions, actions,
deaths, pearls and sonar rays; it does not show intentions, memory or knowledge. Sentences that go beyond the replay are
marked "inference". Rules of our own bot are quoted from `battlecode/mybot2/main.cpp`.

Which bot played. Our 401 games are not one bot. They come from eleven runs (`c_batches.py`, `c_out/batches_1119.txt`): two
ladder downloads and pairs of smoke tests in which the live bot (run names ending in "-old") and a candidate ("-new") play
test4 and WHQ once per map. The run name is the only trace of the build in `games.csv`. One candidate matters for this file:
the run `tc30-test-new` (28 games against test4 and WHQ) and the run `tc30-dev1b-new` (14 against "dev test 1") were played by a
build with `TRADE_CONTACT`. Its source is kept in `data/online/smoke/tc30-bot/main.cpp` and differs from the current
`mybot2/main.cpp` in that one rule: on maps over 1,200 cells a small dragon may ram an enemy that shows at least its own
length, where the live bot asks for max(5, own length + 2) segments. On the twelve maps of 1,200 cells or fewer the two are
the same bot (`c_out/mapsizes.txt`). I picked the newest games to read before I knew this, so 8 of the 16 large-map games of
ours read are from that test build; three live-bot games were added afterwards, and every game below is marked "live" or
"test build". It turned out to be useful: the test build is a ladder trial of half of what finding 1 asks for. Over all games it
is 12 of our 111 large-map games; where a count differs between the builds, both are given. "Live" then means the 99 other
games: the live bot of the hour and three other candidates ("stride", "passage2", and queen hunt, whose kept source leaves the
rules quoted here alone). The run-by-run table is `c_out/bybatch_large.txt`; in rounds 0-149 the ram rate at meetings is
5-11% in every one of those nine runs and 29-32% in the two trade-on-contact runs.

Words used. **Queen**: each team's lowest-id dragon. **Ram**: a head moves into an enemy head; both dragons die, whatever their
lengths. **Charge**: a ram made with a move of two or more steps, by a dragon whose head was not next to the enemy head when its
turn began (a dragon of length 3 can move two steps in a turn, one of 4 three; the extra steps cost a segment each unless a
pearl is eaten on the way). **Boxed death**: a death that is not a ram, with no free cell next to the head at that moment.
**Shed**: a dragon of 5 or more splits and keeps only its front two segments; the rest becomes a new dragon with its head at the
old tail (the front part is usually stuck and dies). **Fountain**: a tile that gave 10 or more natural pearls per 500 rounds over
all games on that map (the replay hides the spawn gaps, so the supply was counted: `c_supply.py`). A fountain makes nothing
while a pearl lies on it or a body covers it. **Own half**: the cells nearer by path to the own queen's start than to the
enemy's. **In view**: inside the 7x7 square around a head. **Path steps**: kelp, wrap and portals respected, bodies ignored.
**Meeting**: a turn that begins with an enemy head on the cell next to the own head, both dragons 4 or shorter. **Dragon-turn**:
one turn of one dragon. `#44` is a dragon id, `L3` a length of 3, `r150` round 150. In a list of six numbers the order is
always meow, test4 against us, WHQ against us, forgot, SSS, Vibing++.

## The three findings that matter most

1. **The gap is made where the two teams touch, and it is made by our small dragons giving way.** Left alone, our dragons forage
   as well as anybody's: a pearl that appears near one of our heads with no enemy near is eaten after 2.6-3.8 rounds (our
   opponents 2.9-3.4), and in rounds 0-49 we eat 6-11% less than they do. The gap opens in rounds 50-99, when a quarter of our
   dragon-turns have an enemy head in view (25-27% fewer natural pearls; 40% fewer in rounds 100-149). The live bot rams in 10%
   of 6,994 meetings on large maps and steps away in 90%; our opponents ram in 37%, forgot in 37%, SSS in 42%, Vibing++ in
   36%. The dragon that steps away eats 0.33 pearls in the next ten rounds and the enemy it left 0.70. Beyond the meetings, our
   opponents make another 13.7 rams a game in rounds 0-149 by charging from two or three cells away (the top three 8.7-12.9);
   the live bot makes 1.0. So the border lies in our half (58% of all rams in our large-map games happen nearer to our spawn;
   top three 47-48%), and in rounds 50-149 our opponents eat 76 natural pearls on the fountains of our half while we eat 34 on
   theirs. That item alone is a third of the whole pearl gap of those rounds; with the corpse pearls it is two thirds.
   **It has been half tried.** The test build that rams on contact (12 large-map games) rams in 31% of meetings, like
   everybody. Its units at round 150 are 52 against 58 instead of 46 against 61, its total length 143 against 191 instead of
   121 against 212; on Australia and Islands it is close to level at round 150 (total 132 against 140 and 123 against 149 in
   three games each; live: 91 against 188 and 85 against 198). It won none of the 12 games (live: 12 of 99), the border did
   not move (57% of rams in our half, 57 natural pearls from the enemy's fountains in rounds 0-149 against the live bot's 49,
   the opponents' 96 from ours unchanged), and it charges 3.9 times a game. What it did not change is the rest of the giving
   way (the retreat at sight, the charge) and the two things finding 3 is about.
2. **A ram is not an even trade for us, because the other side eats the pearls.** In 111 large-map games we lose 296 segments in
   rams and the enemy 332, but of the 39,590 pearls those rams left we ate 28% and the enemy 67%; the top three eat 47-50% of
   theirs. It is not mainly numbers: with the same number of own and enemy heads within 8 steps of the ram we eat 26% and
   the top three 47-49%, and even of the rams we start ourselves, at equal numbers, we eat 34% against their 53-58%. The side
   that starts a ram eats 61-78% of its pearls, and we start 24% of the rams (live 22%, test build 37%; top three 48-57%).
   The test build eats 33% (live 27%): 52% of the pearls of the rams it starts and 21% of those it suffers, and it still
   suffers 63% of the rams, two thirds of them charges. The whole exchange moves about 110 segments a game to the enemy on
   large maps; test4 and WHQ gain 68 and 148 from it against us and nothing against the top three.
3. **Our clock at round 150 turns the team from eaters into prey.** On large maps a small dragon with a free pearl on the cell
   next to its head eats it in 81-82% of turns before round 150, like everybody (our opponents 81-85%, forgot 89-91%), and in
   59-61% after; within 9 cells of our longest dragon in 44%. On medium and small maps, where our switch is at round 300, the
   same drop comes at round 300. Ordinary splits fall from 32 to 15 per 50 rounds (top three 33-59), the 2-longs eat half as
   much per dragon-round as anybody else's (1.25 natural pearls per 100 dragon-rounds against 2.5-3.3), and the dragons of 5
   and more, which no longer split, shed two segments every 15 rounds and are rammed by 2-4-longs. The test build shows what
   that costs when the opening is not lost: against WHQ on Australia and on Islands it has 60 units against 33 and 39 at
   round 150 and total length 207 against 84 and 170 against 91; at round 300 it is behind in both (184 against 245, 101
   against 209) and loses both (`c_out/pairs_large.md`). The drop in eating at round 150 is the same in the two builds (83%
   to 62% in the test build, 82% to 59% in the live bot).

How much of our record this is (`c_endstate.py`, `c_out/endstate_*.txt`). At round 300 our total length is below the opponent's
in 108 of our 109 large-map games that get that far: in all 97 losses and in 11 of the 12 wins, every one of which is won on
the longest dragon. So on large maps the economy is behind in every game. It is not the whole record: the top three are behind
at round 300 in 82 of 158 (forgot), 48 of 139 (SSS) and 40 of 127 (Vibing++) of their large-map games and win 35%, 50% and 40%
of those; we win 10% of ours (11 of 108). That second gap is the end game, which sub-sessions A and A2 read; this file is
about the first.

Two more things that can be counted, each tied to a kind of map: on Slithery Fight our dragons eat on in closed corridors to
length 6-8 and then shed their front two segments (125 sheds a game in rounds 0-99 against 56 for our opponents, and 65
splits at length 4 against 120), where forgot and SSS split at 4 and 5; and 6.4 of our dragons a game on large maps (18.4 on
Islands) die in rounds 0-149 by stepping through a portal onto a body they cannot see.

What this read is not about: the fountain pocket behind a portal on Australia, the corridor on Islands and the start room on
Tower Defense are known and are met in the per-map notes; so are, new to me, the fountain pocket behind a portal on Stripes
(our queen is at its door ten rounds after forgot's and goes in in one game of two) and the narrow fountain corridors on Maze
(we have eaten from 10 of the 19 fountains of our half by round 140, WHQ from 18 of its own).

A correction to earlier tables of this sub-session, for anyone who saw a draft: the all-games snapshots of `c_agg.py` are taken
at the start of a 10-round block, so what a draft called "units at round 50 / 100 / 150" was measured at rounds 40 / 90 / 140.
The numbers below are at the rounds they name (`q/<id>.json`), and snapshot values say "round 90" or "round 140".

## Games read

55 games: 28 on large maps, 11 on medium, 16 on small; 30 of ours and 25 of the top three with the same opponents. "Tables" = the per-10-round tables of
`c_econ.py` for rounds 0-150 (both sides), kept as `c_out/ec_<id>.txt`; the large-map games also for rounds 150-350 (`c_out/ecm_<id>.txt`).
Every game was read for both sides, so the opponent in each of our games (test4, WeHaveQuizzes) is read as well.
The column "end": `wipe-out rN` = one team had no dragon left at round N. Otherwise the game runs 500 rounds and the team with
the longer queen wins, a dead queen counting as 0 (`queen rule`); if that is a tie (both dead, as a rule), the team with the
longest living dragon (`longest`).
The column "run and build" is for our own games: the run the game came from (`c_batches.py`) and what bot played it; see
"Which bot played" above. On large maps 8 of the 16 games of ours read are from the trade-on-contact test build.

| # | game id | map | size | team read | side | opponent (elo) | result | end | final units / total / longest, own vs opponent | run and build (our games) | read with |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1058144 | Australia | large | meow | A | test4 (2176) | loss | queen rule | 4 / 29 / 10 vs 63 / 571 / 61 | `passage2-test-old`: live bot | tables, board r40, pocket tiles |
| 2 | 1067904 | Australia | large | meow | A | test4 (2083) | loss | queen rule | 54 / 174 / 18 vs 49 / 303 / 42 | `tc30-test-new`: test build, trade on contact | tables |
| 3 | 1068050 | Australia | large | meow | A | WeHaveQuizzes (2180) | loss | queen rule | 19 / 136 / 29 vs 7 / 204 / 70 | `tc30-test-new`: test build, trade on contact | tables, ledger to r349 |
| 4 | 1021860 | Australia | large | meow | A | ComTamSuonNuong (2073) | win | longest | 52 / 217 / 30 vs 61 / 211 / 29 | ladder: live bot | tables |
| 5 | 1046985 | Australia | large | forgot | A | test4 (2171) | win | longest | 18 / 220 / 58 vs 11 / 96 / 23 | - | tables |
| 6 | 1046528 | Australia | large | SSS | B | test4 (2171) | win | queen rule | 30 / 241 / 54 vs 14 / 246 / 65 | - | tables |
| 7 | 1069883 | Australia | large | forgot | B | WeHaveQuizzes (2217) | loss | longest | 14 / 211 / 66 vs 6 / 148 / 76 | - | tables |
| 8 | 1054789 | Australia | large | Vibing++ | B | test4 (2189) | loss | longest | 5 / 89 / 32 vs 14 / 393 / 93 | - | tables |
| 9 | 1063012 | Islands | large | meow | A | test4 (2131) | loss | longest | 3 / 15 / 11 vs 17 / 336 / 57 | `qh31-test-old`: live bot | tables |
| 10 | 1067905 | Islands | large | meow | A | test4 (2083) | loss | longest | 12 / 84 / 34 vs 16 / 246 / 63 | `tc30-test-new`: test build, trade on contact | tables, ledger to r349 |
| 11 | 1068051 | Islands | large | meow | A | WeHaveQuizzes (2180) | loss | longest | 7 / 41 / 16 vs 8 / 235 / 82 | `tc30-test-new`: test build, trade on contact | tables, events r8-24 and r19-24, fountain tiles, length classes r100-349, dragon list r140-220 |
| 12 | 1063671 | Islands | large | meow | A | test4 (2131) | loss | wipe-out r313 | 0 / 0 / 0 vs 63 / 381 / 22 | `qh31-test-new`: test build, queen hunt | tables |
| 13 | 1062235 | Islands | large | forgot | A | WeHaveQuizzes (2143) | win | longest | 11 / 216 / 84 vs 2 / 72 / 63 | - | tables |
| 14 | 1051826 | Islands | large | SSS | A | test4 (2165) | win | longest | 11 / 61 / 20 vs 51 / 270 / 12 | - | tables |
| 15 | 1046989 | Islands | large | forgot | A | test4 (2171) | loss | queen rule | 12 / 110 / 56 vs 39 / 234 / 53 | - | tables |
| 16 | 1063016 | Around UNSW | large | meow | A | test4 (2131) | loss | longest | 20 / 258 / 73 vs 20 / 314 / 100 | `qh31-test-old`: live bot | tables |
| 17 | 1068055 | Around UNSW | large | meow | A | WeHaveQuizzes (2180) | loss | longest | 20 / 178 / 48 vs 11 / 282 / 68 | `tc30-test-new`: test build, trade on contact | tables |
| 18 | 1067909 | Around UNSW | large | meow | A | test4 (2093) | loss | queen rule | 33 / 222 / 47 vs 61 / 443 / 45 | `tc30-test-new`: test build, trade on contact | tables, fountain tiles, boards r22 and r28, events r22-30 |
| 19 | 1063675 | Around UNSW | large | meow | A | test4 (2131) | win | longest | 23 / 199 / 69 vs 40 / 397 / 49 | `qh31-test-new`: test build, queen hunt | tables |
| 20 | 1064304 | Around UNSW | large | SSS | A | test4 (2121) | win | longest | 60 / 372 / 83 vs 17 / 251 / 54 | - | tables |
| 21 | 1062237 | Around UNSW | large | forgot | A | WeHaveQuizzes (2143) | loss | longest | 18 / 316 / 72 vs 8 / 211 / 79 | - | tables |
| 22 | 1063252 | Slithery Fight | large | meow | A | WeHaveQuizzes (2135) | loss | longest | 20 / 177 / 64 vs 10 / 227 / 94 | `qh31-test-old`: live bot | tables |
| 23 | 1067917 | Slithery Fight | large | meow | A | test4 (2093) | loss | queen rule | 21 / 153 / 51 vs 36 / 244 / 62 | `tc30-test-new`: test build, trade on contact | tables, death cells, splits |
| 24 | 1068063 | Slithery Fight | large | meow | A | WeHaveQuizzes (2180) | loss | longest | 21 / 124 / 53 vs 5 / 258 / 92 | `tc30-test-new`: test build, trade on contact | tables, ledger |
| 25 | 1063024 | Slithery Fight | large | meow | A | test4 (2131) | win | longest | 27 / 163 / 79 vs 61 / 283 / 17 | `qh31-test-old`: live bot | tables |
| 26 | 1051824 | Slithery Fight | large | SSS | A | test4 (2165) | win | longest | 37 / 166 / 22 vs 49 / 283 / 18 | - | tables, death cells, fountain tiles |
| 27 | 1046988 | Slithery Fight | large | forgot | A | test4 (2171) | loss | queen rule | 33 / 161 / 39 vs 42 / 252 / 64 | - | tables, splits |
| 28 | 1054792 | Slithery Fight | large | Vibing++ | B | test4 (2189) | win | longest | 16 / 273 / 90 vs 40 / 140 / 18 | - | tables |
| 29 | 1067915 | Trauma | medium | meow | A | test4 (2093) | loss | queen rule | 4 / 30 / 14 vs 26 / 122 / 33 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 30 | 1068061 | Trauma | medium | meow | A | WeHaveQuizzes (2180) | loss | wipe-out r467 | 0 / 0 / 0 vs 6 / 130 / 38 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 31 | 1063774 | Trauma | medium | meow | A | WeHaveQuizzes (2135) | win | queen rule | 4 / 59 / 50 vs 4 / 113 / 49 | `qh31-test-new`: test build, queen hunt | tables |
| 32 | 1046991 | Trauma | medium | forgot | A | test4 (2171) | win | queen rule | 5 / 79 / 46 vs 10 / 64 / 25 | - | tables |
| 33 | 1054786 | Trauma | medium | SSS | B | test4 (2189) | win | queen rule | 10 / 74 / 32 vs 14 / 84 / 30 | - | tables |
| 34 | 1067906 | Maze | medium | meow | A | test4 (2093) | loss | queen rule | 19 / 100 / 47 vs 13 / 124 / 73 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 35 | 1068052 | Maze | medium | meow | A | WeHaveQuizzes (2180) | loss | longest | 12 / 131 / 66 vs 4 / 121 / 94 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables, fountain tiles |
| 36 | 1063672 | Maze | medium | meow | A | test4 (2131) | win | longest | 8 / 134 / 76 vs 3 / 81 / 64 | `qh31-test-new`: test build, queen hunt | tables |
| 37 | 1046984 | Maze | medium | forgot | A | test4 (2171) | loss | queen rule | 15 / 148 / 55 vs 17 / 121 / 67 | - | tables |
| 38 | 1046526 | Maze | medium | SSS | B | test4 (2171) | win | queen rule | 6 / 135 / 93 vs 5 / 123 / 66 | - | tables |
| 39 | 1069373 | Maze | medium | SSS | B | WeHaveQuizzes (2204) | win | queen rule | 16 / 167 / 48 vs 4 / 73 / 37 | - | tables |
| 40 | 1067908 | Tower Defense | small | meow | A | test4 (2093) | loss | wipe-out r322 | 0 / 0 / 0 vs 52 / 136 / 4 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 41 | 1068054 | Tower Defense | small | meow | A | WeHaveQuizzes (2180) | loss | queen rule | 3 / 73 / 28 vs 2 / 46 / 32 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 42 | 1046992 | Tower Defense | small | forgot | A | test4 (2171) | win | longest | 21 / 108 / 37 vs 1 / 14 / 14 | - | tables |
| 43 | 1051827 | Tower Defense | small | SSS | A | test4 (2165) | win | wipe-out r230 | 44 / 105 / 3 vs 0 / 0 / 0 | - | tables |
| 44 | 1070191 | Tower Defense | small | forgot | B | WeHaveQuizzes (2202) | win | wipe-out r124 | 27 / 70 / 3 vs 0 / 0 / 0 | - | tables |
| 45 | 1067907 | Stripes | small | meow | A | test4 (2093) | loss | wipe-out r140 | 0 / 0 / 0 vs 20 / 50 / 5 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables, events r0-34, board r18 |
| 46 | 1068053 | Stripes | small | meow | A | WeHaveQuizzes (2180) | loss | wipe-out r176 | 0 / 0 / 0 vs 28 / 64 / 4 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 47 | 1059076 | Stripes | small | meow | A | WeHaveQuizzes (2155) | win | wipe-out r274 | 18 / 42 / 3 vs 0 / 0 / 0 | `passage2-test-new`: test build | tables |
| 48 | 1046977 | Stripes | small | forgot | A | test4 (2171) | win | wipe-out r91 | 13 / 33 / 5 vs 0 / 0 / 0 | - | tables |
| 49 | 1062236 | Stripes | small | forgot | A | WeHaveQuizzes (2143) | win | wipe-out r141 | 16 / 36 / 4 vs 0 / 0 / 0 | - | tables |
| 50 | 1063682 | Portals | small | meow | A | test4 (2131) | loss | longest | 9 / 53 / 16 vs 2 / 46 / 33 | `qh31-test-new`: test build, queen hunt | tables, fountain tiles, board r60 |
| 51 | 1063251 | Portals | small | meow | A | WeHaveQuizzes (2135) | loss | longest | 13 / 58 / 9 vs 2 / 40 / 37 | `qh31-test-old`: live bot | tables |
| 52 | 1067916 | Portals | small | meow | A | test4 (2093) | win | longest | 3 / 57 / 49 vs 1 / 44 / 44 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 53 | 1046982 | Portals | small | forgot | A | test4 (2171) | loss | queen rule | 4 / 84 / 57 vs 4 / 49 / 40 | - | tables |
| 54 | 1062234 | Portals | small | forgot | A | WeHaveQuizzes (2143) | win | queen rule | 4 / 45 / 28 vs 1 / 44 / 44 | - | tables |
| 55 | 1064306 | Portals | small | SSS | A | test4 (2121) | win | queen rule | 5 / 51 / 32 vs 2 / 42 / 40 | - | tables |

## Per-map notes

How to read the tables. One row per 10 rounds unless the first column shows a wider block (50 rounds); every cell is "side A /
side B" (we are A in all 30 of our games read). Units and total length are at the start of the row. "Rammed" = own dragons that
an enemy rammed, "rammers" = own dragons that rammed an enemy, "head-on with a team-mate" = dragons lost when two heads of the
same team met (both die; these are not rams), "boxed" = non-ram deaths with no free cell, "other non-ram" = non-ram deaths
with a free cell. "Board squares" = how many of the 64 squares of an 8x8 grid over the board hold an own head. The last three
columns are about fountains: the share of own heads standing in the own half, natural pearls eaten on fountains of the enemy's
half, and the share of tile-rounds in which a pearl lay uneaten on a fountain of the own half (while it lies there the tile
produces nothing).
The "all games" lines are means per game from `c_agg.py` (`c_out/agg_map_<map>.txt`): meow = our games against 2000+ teams, all
builds; "test4 / WHQ against us" = those two opponents in our games; forgot, SSS, Vibing++ = their games against 2000+ teams.
Units and total length are at round 150; the other counts are sums over rounds 0-149.
Each of our games says which bot played it: "live" or "test build" (trade on contact; it differs from the live bot only on the
four large maps).

### Australia (large, 64x64; we won 1 of 28)

**Supply.** 1,420 natural pearls appear per 500 rounds, 56% of them on 36 fountain tiles: two pockets of 12 tiles each that are
closed by kelp and entered through a portal ((53-57,37-40), by path the one nearer to side A's spawn, and (6-10,23-26) for side
B), and 12 single tiles in the open. 43 pearls appear in rounds 0-9 and then only 5-7 per 10 rounds until somebody starts to
eat them: a fountain with a pearl lying on it is blocked.

**All games** (28 of ours): units at round 150: meow 38, test4 against us 62, WHQ against us 57, forgot 55, SSS 54, Vibing++ 40.
Natural pearls eaten in rounds 0-149: 117 / 259 / 227 / 218 / 219 / 181, of which on fountains of the enemy's half 22 / 81 / 64 /
38 / 38 / 38. Dragons rammed by the enemy: 15.3 / 2.4 / 3.6 / 17.0 / 12.6 / 10.0; dragons that rammed: 3.1 / 15.1 / 15.5 / 15.8 / 13.5 /
13.9. Boxed deaths: 10.5 / 58 / 31 / 30 / 40 / 43. We are the team with the fewest dead-end deaths and the fewest pearls. By build
(`c_out/bybatch_Australia.txt`): the 25 live games have 37 units against 59 at round 150 and total length 91 against 188; the
3 test-build games 47 against 52 and 132 against 140.

**The live bot's typical loss, 1058144 against test4** (queen rule; final 4 units and total 29 against 63 and 571):

Game 1058144, Australia: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 9 / 9 | 26 / 26 | 1 / 2 | 0 / 0 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 5 / 5 | 84 / 84 | 0 / 1 | 23 / 22 |
| 10-19 | 13 / 13 | 27 / 28 | 1 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 9 / 8 | 85 / 85 | 1 / 0 | 85 / 87 |
| 20-29 | 13 / 13 | 28 / 29 | 4 / 1 | 0 / 0 | 2 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 9 / 9 | 79 / 85 | 1 / 0 | 90 / 88 |
| 30-39 | 15 / 13 | 32 / 30 | 5 / 13 | 0 / 0 | 2 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 11 / 9 | 73 / 81 | 0 / 10 | 79 / 91 |
| 40-49 | 17 / 16 | 37 / 40 | 3 / 21 | 0 / 1 | 0 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 5 | 0 / 0 | 13 / 12 | 75 / 72 | 0 / 6 | 32 / 66 |
| 50-59 | 17 / 18 | 40 / 52 | 10 / 22 | 0 / 7 | 4 / 15 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 5 | 0 / 0 | 15 / 15 | 77 / 65 | 0 / 7 | 33 / 30 |
| 60-69 | 21 / 28 | 50 / 71 | 12 / 21 | 0 / 6 | 5 / 12 | 1 / 0 | 0 / 1 | 0 / 0 | 1 / 6 | 0 / 0 | 14 / 18 | 77 / 64 | 3 / 7 | 27 / 34 |
| 70-79 | 24 / 33 | 57 / 81 | 10 / 17 | 2 / 8 | 6 / 11 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 7 | 0 / 1 | 16 / 22 | 73 / 60 | 2 / 5 | 32 / 38 |
| 80-89 | 30 / 36 | 69 / 87 | 5 / 26 | 0 / 6 | 2 / 8 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 18 / 23 | 64 / 60 | 0 / 8 | 50 / 57 |
| 90-99 | 31 / 43 | 72 / 116 | 8 / 23 | 2 / 17 | 2 / 21 | 2 / 0 | 0 / 2 | 0 / 0 | 1 / 9 | 0 / 0 | 19 / 28 | 66 / 63 | 0 / 6 | 19 / 32 |
| 100-109 | 30 / 53 | 74 / 129 | 5 / 24 | 0 / 13 | 3 / 12 | 0 / 1 | 1 / 0 | 0 / 0 | 0 / 6 | 0 / 0 | 24 / 32 | 65 / 63 | 0 / 9 | 31 / 27 |
| 110-119 | 32 / 58 | 77 / 151 | 6 / 25 | 0 / 16 | 2 / 16 | 2 / 0 | 0 / 2 | 0 / 0 | 0 / 9 | 0 / 0 | 26 / 37 | 61 / 61 | 1 / 7 | 11 / 28 |
| 120-129 | 32 / 63 | 78 / 167 | 3 / 18 | 2 / 7 | 2 / 6 | 3 / 0 | 0 / 3 | 0 / 0 | 0 / 4 | 0 / 1 | 24 / 35 | 61 / 55 | 0 / 6 | 7 / 46 |
| 130-139 | 31 / 61 | 74 / 170 | 4 / 30 | 1 / 13 | 0 / 4 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 1 | 0 / 0 | 24 / 37 | 61 / 57 | 0 / 6 | 56 / 44 |
| 140-149 | 30 / 63 | 76 / 204 | 8 / 21 | 1 / 11 | 5 / 4 | 3 / 0 | 0 / 3 | 0 / 0 | 1 / 2 | 0 / 0 | 24 / 39 | 57 / 55 | 0 / 8 | 28 / 28 |

- Rounds 0-29: level (13 units each). 43 natural pearls lie on the board from round 10; at round 20 our heads are nearer to
  28 of them, at round 30 to 12 of 45 (test4: 33).
- Our dragons had 11 of the 12 tiles of the pocket of our half in view from round 10 (from outside the kelp) and never ate
  there in 150 rounds. test4's dragons eat inside OUR pocket from round 33 and inside the pocket of their own half from round
  39 (board at round 40: a test4 3-long stands at (7,23) on twelve lying pearls), 4-8 pearls on each of our 11 tiles by
  round 150 (`c_out/tiles_1058144.txt`: natural pearls eaten on the fountains of our half: we 31, test4 87; on those of
  test4's half: test4 99, we 8).
- test4 pays for it: 54 boxed deaths (122 segments) in 150 rounds, 13 of them on one cell, against our 3. It eats 87 of its
  own corpse pearls back and has 63 units at round 120 against our 32.
- From round 60 test4 rams: we lose 13 dragons to rams by round 150 and make 1. Of the 128 natural pearls that appeared within
  6 steps of one of our heads we ate 68 and test4 53; of the 53 with no enemy head within 6 steps we ate 47 after 3.4 rounds
  (test4: 173 of 190 after 3.3 rounds). Undisturbed, the two teams are equally fast.

**The same opponent against forgot, 1046985** (forgot is side A, as we are; forgot won on the longest dragon, 58 against 23):

Game 1046985, Australia: A = forgot, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 9 / 9 | 26 / 26 | 1 / 2 | 0 / 0 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 5 / 5 | 84 / 84 | 1 / 1 | 57 / 57 |
| 10-19 | 12 / 12 | 27 / 28 | 3 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 8 / 10 | 83 / 84 | 1 / 0 | 88 / 88 |
| 20-29 | 13 / 13 | 30 / 28 | 4 / 8 | 0 / 0 | 2 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 8 / 7 | 72 / 80 | 2 / 8 | 78 / 92 |
| 30-39 | 15 / 14 | 34 / 33 | 4 / 14 | 0 / 6 | 1 / 10 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 6 | 0 / 0 | 11 / 10 | 72 / 65 | 1 / 9 | 38 / 88 |
| 40-49 | 15 / 17 | 36 / 38 | 5 / 19 | 0 / 6 | 1 / 10 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 6 | 0 / 1 | 10 / 14 | 73 / 60 | 1 / 4 | 36 / 39 |
| 50-59 | 15 / 19 | 38 / 45 | 7 / 20 | 3 / 15 | 3 / 13 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 6 | 0 / 0 | 10 / 15 | 68 / 56 | 1 / 7 | 44 / 40 |
| 60-69 | 17 / 25 | 45 / 64 | 10 / 25 | 3 / 7 | 8 / 13 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 8 | 0 / 0 | 13 / 21 | 65 / 54 | 2 / 9 | 33 / 40 |
| 70-79 | 24 / 29 | 54 / 75 | 11 / 21 | 1 / 14 | 5 / 16 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 10 | 0 / 0 | 17 / 19 | 62 / 52 | 3 / 8 | 28 / 31 |
| 80-89 | 28 / 35 | 64 / 88 | 13 / 34 | 0 / 11 | 4 / 16 | 1 / 1 | 1 / 1 | 0 / 0 | 0 / 10 | 0 / 0 | 20 / 22 | 56 / 46 | 1 / 7 | 26 / 29 |
| 90-99 | 30 / 39 | 71 / 102 | 10 / 18 | 3 / 11 | 5 / 13 | 2 / 1 | 1 / 2 | 0 / 0 | 0 / 4 | 0 / 0 | 22 / 20 | 57 / 48 | 1 / 3 | 59 / 33 |
| 100-109 | 32 / 45 | 77 / 111 | 11 / 18 | 7 / 18 | 6 / 12 | 3 / 1 | 1 / 3 | 0 / 2 | 0 / 1 | 0 / 0 | 18 / 24 | 61 / 44 | 3 / 4 | 57 / 37 |
| 110-119 | 34 / 50 | 85 / 124 | 13 / 37 | 0 / 9 | 7 / 20 | 2 / 2 | 2 / 2 | 0 / 0 | 0 / 4 | 0 / 0 | 22 / 29 | 56 / 50 | 3 / 10 | 31 / 29 |
| 120-129 | 37 / 62 | 88 / 153 | 6 / 21 | 16 / 5 | 10 / 7 | 3 / 3 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 21 / 33 | 57 / 56 | 2 / 7 | 19 / 30 |
| 130-139 | 41 / 63 | 94 / 162 | 11 / 24 | 8 / 18 | 5 / 13 | 4 / 6 | 6 / 4 | 0 / 0 | 0 / 4 | 0 / 0 | 25 / 35 | 54 / 47 | 3 / 8 | 14 / 30 |
| 140-149 | 36 / 62 | 87 / 160 | 11 / 26 | 7 / 17 | 7 / 3 | 3 / 0 | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 25 / 32 | 47 / 51 | 2 / 12 | 48 / 62 |

- forgot is out-eaten by test4 almost as badly as we are (120 natural pearls against 287 in rounds 0-149; 40 units and total
  96 against 62 and 189 at round 150) and has 1 boxed death against test4's 59. What forgot does that we do not: it rams (14
  rams made and 22 suffered in rounds 0-149; we 1 and 13), and from round 150 it rams far more than test4: 29, 21, 33, 24
  rams per 50 rounds against 8, 2, 7, 1, with rammers of 2.5-3.0 segments on victims of 3.2-4.3, and it eats the corpses
  (104 corpse pearls against 57 in rounds 250-299). Its total goes 96, 94, 137, 168, 170 at rounds 150 to 350 while test4's
  goes 189, 228, 261, 230, 211 (`c_out/ledger_large.txt`), and it ends with a 58-long against a 23-long. An opening deficit
  against test4 on this map is not what separates us from forgot; what happens at the border afterwards is.
- SSS against test4 (1046528, SSS won): 237 natural pearls against 201, 47 boxed deaths against 41. Vibing++ against test4
  (1054789, Vibing++ lost): 92 against 275 and 18 units against 63 at round 150.

**The test build with a good opening, 1068050 against WHQ** (lost on the queen rule: our queen dead, WHQ's 70 long):

Game 1068050, Australia: A = meow, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 9 / 9 | 26 / 26 | 1 / 3 | 0 / 0 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 5 / 5 | 84 / 84 | 0 / 1 | 33 / 33 |
| 10-19 | 12 / 12 | 27 / 29 | 3 / 1 | 0 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 9 / 7 | 83 / 84 | 1 / 0 | 87 / 85 |
| 20-29 | 12 / 13 | 30 / 30 | 3 / 5 | 0 / 0 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 10 / 7 | 74 / 82 | 1 / 1 | 86 / 81 |
| 30-39 | 15 / 16 | 33 / 35 | 17 / 12 | 0 / 1 | 5 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 2 | 0 / 0 | 10 / 9 | 69 / 72 | 0 / 1 | 89 / 57 |
| 40-49 | 20 / 19 | 50 / 44 | 14 / 11 | 0 / 4 | 8 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 3 | 0 / 1 | 13 / 12 | 61 / 68 | 3 / 1 | 84 / 37 |
| 50-59 | 28 / 20 | 64 / 51 | 14 / 10 | 0 / 2 | 6 / 7 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 1 | 0 / 0 | 20 / 13 | 55 / 65 | 4 / 2 | 70 / 30 |
| 60-69 | 33 / 25 | 76 / 59 | 18 / 10 | 0 / 8 | 4 / 8 | 0 / 0 | 0 / 0 | 0 / 4 | 0 / 2 | 0 / 0 | 23 / 15 | 50 / 62 | 5 / 2 | 74 / 19 |
| 70-79 | 37 / 27 | 94 / 64 | 25 / 12 | 3 / 8 | 11 / 7 | 1 / 3 | 3 / 1 | 0 / 0 | 0 / 4 | 1 / 1 | 25 / 20 | 56 / 61 | 3 / 1 | 33 / 28 |
| 80-89 | 43 / 25 | 110 / 60 | 15 / 16 | 14 / 7 | 14 / 10 | 0 / 1 | 1 / 0 | 0 / 0 | 2 / 4 | 0 / 0 | 23 / 18 | 53 / 58 | 4 / 1 | 18 / 17 |
| 90-99 | 54 / 30 | 131 / 70 | 21 / 19 | 5 / 2 | 10 / 9 | 0 / 1 | 1 / 0 | 0 / 0 | 5 / 5 | 1 / 0 | 26 / 17 | 54 / 61 | 6 / 3 | 24 / 20 |
| 100-109 | 57 / 33 | 141 / 78 | 20 / 11 | 15 / 8 | 12 / 9 | 1 / 4 | 4 / 1 | 0 / 0 | 4 / 3 | 0 / 0 | 29 / 19 | 54 / 66 | 1 / 2 | 33 / 13 |
| 110-119 | 60 / 34 | 155 / 79 | 21 / 10 | 10 / 5 | 6 / 4 | 2 / 1 | 1 / 2 | 0 / 2 | 3 / 1 | 1 / 0 | 27 / 19 | 52 / 61 | 2 / 3 | 30 / 63 |
| 120-129 | 59 / 32 | 165 / 77 | 18 / 17 | 10 / 6 | 6 / 7 | 1 / 2 | 2 / 1 | 0 / 0 | 2 / 1 | 0 / 0 | 29 / 21 | 50 / 62 | 4 / 2 | 43 / 44 |
| 130-139 | 60 / 35 | 180 / 91 | 16 / 12 | 8 / 10 | 9 / 10 | 2 / 7 | 7 / 2 | 0 / 0 | 0 / 3 | 0 / 1 | 33 / 24 | 47 / 59 | 3 / 1 | 74 / 23 |
| 140-149 | 60 / 32 | 171 / 79 | 17 / 5 | 24 / 8 | 2 / 4 | 0 / 1 | 1 / 0 | 0 / 0 | 1 / 1 | 0 / 1 | 32 / 19 | 46 / 68 | 3 / 1 | 66 / 64 |

- This is what trading on contact does on this map. In rounds 0-149 the test build has 38 meetings and rams in 15 of them; it
  makes 20 rams and suffers 8 (the live bot against the same opponent an hour earlier, 1063239: 4 made, 16 suffered, 2 of 46
  meetings). It eats 64 pearls of ram corpses and WHQ 32. From round 50 only 46-56% of our heads stand in our own half, and we
  eat 40 natural pearls on the fountains of WHQ's half against WHQ's 22 on ours. At round 150 we have 60 units and total 207
  against 33 and 84; the live bot in 1063239 had 51 and 128 against 54 and 148.
- Then the clock. Per 50 rounds (`c_ledger.py`):

| rounds | our units | our total | our natural | our dragons rammed (segments) | WHQ units | WHQ total | WHQ natural | WHQ rams made |
|---|---|---|---|---|---|---|---|---|
| 100-149 | 57 > 60 | 141 > 207 | 92 | 6 (25) | 33 > 33 | 78 > 84 | 55 | 6 |
| 150-199 | 60 > 60 | 207 > 199 | 63 | 17 (65) | 33 > 58 | 84 > 187 | 124 | 17 |
| 200-249 | 60 > 49 | 199 > 172 | 49 | 11 (57) | 58 > 64 | 187 > 235 | 101 | 11 |
| 250-299 | 49 > 54 | 172 > 184 | 42 | 8 (22) | 64 > 45 | 235 > 245 | 107 | 8 |

Our natural intake per 100 dragon-turns falls from 3.05 to 2.08 at round 150 and to 1.7-1.8 later; WHQ's is 3.2-5.2 throughout.
This is the round-150 switch (answer f), in a game that the opening had won. The test build against test4 on this map
(1067904) is behind from the start of the contact (47 units against 61 at round 150, total 107 against 161) but far less than
the live bot in 1063011 (27 against 64, 63 against 232).

### Around UNSW (large, 64x64; we won 6 of 24)

**Supply.** 2,035 natural pearls per 500 rounds, 76% on 84 fountain tiles: a cluster of 17 tiles 21-27 steps from each spawn
((50-56,6-8) and (58-60,11) for side A), a central cluster of about 32 tiles around (28-35,29-34) that both teams reach in 28-37
steps, three tiles at (58-59,26-27) with their mirror at (4-5,36-37), and a few corridor tiles.

**All games** (24 of ours): units at round 150: meow 59, test4 63, WHQ 62, forgot 58, SSS 61, Vibing++ 60, so no unit gap. Total
length at round 150: 157 / 281 / 261 / 151 / 239 / 213. Natural pearls eaten in rounds 0-149: 220 / 383 / 379 / 281 / 387 / 361, of
which on fountains of the enemy's half: 27 / 122 / 109 / 74 / 127 / 110. Own heads in the own half: 78% / 63% / 69% / 77% / 71% / 69%.
Cells visited by round 140: 1,344 / 1,864 / 1,668 / 1,537 / 1,558 / 1,499. Boxed deaths: 45 / 53 / 62 / 86 / 91 / 85. The whole
natural-pearl gap to test4 and WHQ on this map is in the enemy's half: they take 109-122 pearls from our fountains, we take 27
from theirs.

**The live bot against test4, 1063016** (lost on the longest dragon, 73 against 100):

Game 1063016, Around UNSW: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 10 / 10 | 36 / 36 | 2 / 4 | 0 / 0 | 7 / 8 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 2 | 0 / 0 | 5 / 5 | 78 / 73 | 0 / 1 | 27 / 28 |
| 10-19 | 14 / 16 | 32 / 35 | 4 / 9 | 0 / 0 | 1 / 3 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 8 / 9 | 80 / 75 | 0 / 0 | 57 / 53 |
| 20-29 | 14 / 18 | 33 / 41 | 13 / 23 | 0 / 5 | 4 / 12 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 2 | 0 / 0 | 7 / 11 | 87 / 75 | 0 / 6 | 74 / 56 |
| 30-39 | 18 / 28 | 46 / 65 | 8 / 39 | 0 / 6 | 4 / 17 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 3 | 0 / 0 | 11 / 15 | 90 / 78 | 0 / 14 | 52 / 39 |
| 40-49 | 21 / 41 | 51 / 99 | 8 / 37 | 2 / 8 | 2 / 16 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 3 | 0 / 0 | 10 / 20 | 89 / 72 | 0 / 14 | 30 / 24 |
| 50-59 | 22 / 53 | 59 / 129 | 17 / 36 | 3 / 8 | 10 / 15 | 2 / 0 | 0 / 2 | 0 / 0 | 3 / 5 | 0 / 0 | 13 / 24 | 88 / 69 | 1 / 17 | 25 / 26 |
| 60-69 | 27 / 61 | 69 / 154 | 12 / 25 | 5 / 19 | 10 / 7 | 2 / 0 | 0 / 2 | 0 / 0 | 4 / 4 | 1 / 0 | 15 / 27 | 93 / 66 | 0 / 9 | 18 / 32 |
| 70-79 | 30 / 62 | 69 / 180 | 10 / 36 | 3 / 3 | 5 / 7 | 1 / 0 | 0 / 1 | 0 / 0 | 2 / 4 | 0 / 0 | 12 / 27 | 97 / 66 | 0 / 10 | 19 / 25 |
| 80-89 | 32 / 64 | 76 / 207 | 18 / 31 | 3 / 11 | 7 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 4 / 5 | 0 / 0 | 17 / 34 | 95 / 71 | 0 / 8 | 28 / 26 |
| 90-99 | 35 / 62 | 88 / 236 | 14 / 35 | 5 / 9 | 10 / 8 | 1 / 0 | 0 / 1 | 0 / 0 | 5 / 7 | 0 / 0 | 19 / 28 | 90 / 68 | 0 / 13 | 23 / 33 |
| 100-109 | 39 / 62 | 95 / 254 | 13 / 27 | 9 / 14 | 11 / 5 | 0 / 1 | 1 / 0 | 0 / 0 | 4 / 3 | 1 / 0 | 22 / 31 | 90 / 71 | 0 / 5 | 25 / 36 |
| 110-119 | 44 / 63 | 102 / 266 | 16 / 30 | 9 / 8 | 12 / 6 | 1 / 2 | 2 / 1 | 0 / 0 | 5 / 3 | 1 / 0 | 23 / 33 | 96 / 63 | 0 / 10 | 23 / 26 |
| 120-129 | 47 / 63 | 108 / 282 | 18 / 26 | 8 / 12 | 11 / 6 | 1 / 0 | 0 / 1 | 0 / 0 | 4 / 4 | 0 / 0 | 19 / 36 | 91 / 63 | 0 / 4 | 21 / 34 |
| 130-139 | 53 / 64 | 122 / 307 | 20 / 17 | 5 / 8 | 11 / 4 | 1 / 0 | 0 / 1 | 0 / 0 | 3 / 3 | 0 / 0 | 22 / 37 | 90 / 65 | 0 / 3 | 21 / 31 |
| 140-149 | 60 / 64 | 138 / 312 | 17 / 28 | 13 / 5 | 8 / 4 | 0 / 3 | 3 / 0 | 0 / 0 | 4 / 1 | 0 / 0 | 23 / 33 | 83 / 73 | 0 / 7 | 21 / 29 |

- No fight is needed to lose this map. test4 has 41 units at round 40 and 61 at round 60; we have 21 and 27. In 150 rounds
  we eat 190 natural pearls and test4 403; on the fountains of the other half we eat 1 and test4 121. From round 20 on 83-97%
  of our heads are in our own half (test4: 63-78%). Only 12 of our dragons are rammed in these 150 rounds and we ram 6 times;
  of 13 meetings we ram in 2.
- The units catch up by round 140 (60 against 64) because test4 is at the 64-unit cap; the total length does not (138
  against 312).

**The test build against test4, 1067909** (lost on the queen rule; final 33 units and total 222 against 61 and 443):

Game 1067909, Around UNSW: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 10 / 10 | 36 / 36 | 5 / 4 | 2 / 0 | 7 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 2 | 0 / 0 | 5 / 5 | 78 / 73 | 3 / 2 | 24 / 25 |
| 10-19 | 14 / 15 | 37 / 35 | 9 / 5 | 0 / 3 | 6 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 3 | 0 / 0 | 8 / 10 | 74 / 72 | 4 / 2 | 61 / 61 |
| 20-29 | 18 / 16 | 42 / 37 | 16 / 18 | 1 / 3 | 5 / 8 | 0 / 1 | 1 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 9 / 12 | 76 / 70 | 3 / 7 | 71 / 72 |
| 30-39 | 21 / 22 | 52 / 50 | 14 / 32 | 4 / 3 | 6 / 13 | 3 / 0 | 0 / 3 | 0 / 0 | 2 / 1 | 0 / 0 | 11 / 15 | 85 / 64 | 0 / 13 | 44 / 69 |
| 40-49 | 22 / 31 | 56 / 72 | 11 / 29 | 5 / 9 | 7 / 14 | 2 / 0 | 0 / 2 | 0 / 0 | 2 / 2 | 0 / 0 | 13 / 15 | 86 / 66 | 2 / 10 | 35 / 47 |
| 50-59 | 25 / 41 | 62 / 94 | 13 / 39 | 5 / 13 | 9 / 21 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 5 | 0 / 0 | 13 / 22 | 82 / 67 | 1 / 12 | 24 / 29 |
| 60-69 | 31 / 57 | 74 / 136 | 18 / 30 | 7 / 7 | 8 / 13 | 2 / 1 | 1 / 2 | 0 / 0 | 3 / 5 | 0 / 0 | 17 / 23 | 82 / 66 | 0 / 8 | 14 / 22 |
| 70-79 | 33 / 62 | 85 / 154 | 14 / 32 | 6 / 10 | 10 / 8 | 1 / 1 | 1 / 1 | 0 / 0 | 5 / 5 | 0 / 0 | 18 / 26 | 76 / 70 | 0 / 8 | 25 / 25 |
| 80-89 | 36 / 63 | 89 / 173 | 17 / 33 | 6 / 13 | 10 / 5 | 1 / 2 | 2 / 1 | 0 / 0 | 2 / 3 | 0 / 0 | 20 / 28 | 76 / 69 | 1 / 10 | 33 / 23 |
| 90-99 | 41 / 62 | 100 / 193 | 18 / 27 | 7 / 13 | 11 / 5 | 2 / 0 | 0 / 2 | 0 / 0 | 5 / 3 | 0 / 0 | 22 / 30 | 84 / 70 | 0 / 6 | 25 / 29 |
| 100-109 | 45 / 62 | 109 / 216 | 17 / 36 | 7 / 12 | 11 / 8 | 0 / 0 | 0 / 0 | 0 / 0 | 7 / 6 | 0 / 0 | 21 / 35 | 86 / 69 | 0 / 9 | 17 / 28 |
| 110-119 | 49 / 64 | 116 / 239 | 16 / 25 | 4 / 17 | 9 / 8 | 0 / 2 | 2 / 0 | 0 / 0 | 1 / 8 | 0 / 0 | 22 / 33 | 83 / 64 | 0 / 6 | 14 / 34 |
| 120-129 | 55 / 62 | 130 / 248 | 17 / 27 | 14 / 10 | 9 / 7 | 2 / 3 | 3 / 2 | 0 / 0 | 4 / 2 | 0 / 0 | 23 / 33 | 87 / 69 | 0 / 9 | 18 / 29 |
| 130-139 | 55 / 62 | 138 / 256 | 12 / 22 | 10 / 14 | 12 / 5 | 1 / 2 | 2 / 1 | 0 / 0 | 2 / 1 | 2 / 0 | 29 / 35 | 89 / 70 | 0 / 3 | 20 / 34 |
| 140-149 | 60 / 63 | 145 / 270 | 18 / 23 | 3 / 13 | 4 / 10 | 0 / 2 | 2 / 0 | 0 / 0 | 2 / 7 | 0 / 0 | 29 / 32 | 84 / 69 | 4 / 7 | 27 / 26 |

- Until round 30 we are level or ahead: 18 units against 16 at round 20, 21 against 22 at round 30 (total length 52 against
  50), and we have seen 33 of the 39 fountains of our half (test4: 22 of its own). From round 30 test4 eats 29-39 natural
  pearls per 10 rounds and we 11-18; test4 has 57 units at round 60, we 31.
- Where: `c_out/tiles_1067909.txt`. We eat on the 17 tiles of our near cluster (about 50 pearls in 100 rounds, at the pooled
  rate). The central cluster we reach first (round 10-23) and then lose: by round 100 test4 has eaten on 35 of the 39
  fountains of its half and on 21 of the 39 of ours; we have eaten on 21 of ours and 9 of theirs. The three tiles at (58-59,26-27),
  34-36 steps from our spawn and 43-45 from theirs, give test4 13 pearls from round 26 on and us 1 (at round 99).
- How the centre was lost (events of rounds 22-30 around (31,31)): at round 22 three of our dragons stand in a field of about 30
  lying pearls. `#17` (L4) splits inside a 2x2 nook; next round the parent has only its own tail and its child's tail next to
  its head and dies ("body"). The child `#44` walks away west (9 moves, no pearl). `#38` (L3) eats a pearl and at round 23,
  4 long, eats another and rams test4's 5-long `#20` in the same two-step move (the test build's rule allows a target of its
  own length; the live bot would ask for 6 segments here). `#41` (L2) circles for 8 rounds, eats one corpse pearl at round 29
  and is rammed at round 30 by test4's `#10`, which moved three steps (a charge; eating a pearl on the way pays for a step).
  `#5` (L2) arrives, eats one pearl at round 30 and is rammed in the same round by `#36`, which also moved three steps over
  two pearls. Four of ours and three of theirs are dead by round 30;
  test4's survivors split on the pearls and stay; ours do not come back (85% of our heads are in our own half from round 30,
  64-70% of theirs).
- Against the live game above the test build makes 14 rams instead of 6 and eats 215 natural pearls instead of 190, 18 on
  test4's fountains instead of 1; test4 still eats 382.

**SSS against test4 from our side of the board, 1064304** (SSS won on the longest dragon):

Game 1064304, Around UNSW: A = SSS, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 10 / 10 | 36 / 36 | 9 / 5 | 2 / 0 | 8 / 8 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 0 / 0 | 5 / 5 | 73 / 73 | 3 / 1 | 24 / 24 |
| 10-19 | 16 / 16 | 42 / 36 | 12 / 3 | 3 / 0 | 9 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 4 / 0 | 0 / 0 | 8 / 9 | 73 / 75 | 6 / 1 | 37 / 34 |
| 20-29 | 21 / 18 | 49 / 39 | 28 / 19 | 5 / 0 | 11 / 7 | 1 / 2 | 2 / 1 | 0 / 0 | 4 / 0 | 0 / 0 | 10 / 12 | 74 / 75 | 12 / 4 | 48 / 49 |
| 30-39 | 25 / 22 | 64 / 51 | 27 / 22 | 10 / 9 | 13 / 8 | 1 / 1 | 1 / 1 | 0 / 0 | 3 / 0 | 0 / 0 | 15 / 13 | 78 / 74 | 8 / 4 | 25 / 34 |
| 40-49 | 33 / 28 | 87 / 71 | 23 / 11 | 12 / 0 | 16 / 7 | 0 / 1 | 1 / 0 | 0 / 0 | 8 / 2 | 0 / 0 | 13 / 17 | 74 / 77 | 7 / 0 | 26 / 28 |
| 50-59 | 40 / 32 | 101 / 75 | 28 / 25 | 12 / 3 | 21 / 12 | 0 / 1 | 1 / 0 | 0 / 0 | 7 / 3 | 0 / 0 | 14 / 17 | 72 / 73 | 6 / 3 | 22 / 27 |
| 60-69 | 53 / 40 | 120 / 95 | 32 / 23 | 11 / 2 | 17 / 10 | 1 / 0 | 0 / 1 | 0 / 0 | 8 / 4 | 0 / 0 | 15 / 22 | 72 / 71 | 7 / 4 | 21 / 21 |
| 70-79 | 61 / 45 | 144 / 108 | 30 / 9 | 17 / 7 | 11 / 6 | 2 / 1 | 1 / 2 | 0 / 0 | 9 / 1 | 0 / 0 | 19 / 26 | 71 / 73 | 12 / 0 | 20 / 24 |
| 80-89 | 60 / 47 | 159 / 113 | 34 / 19 | 11 / 6 | 11 / 9 | 2 / 2 | 2 / 2 | 0 / 0 | 6 / 1 | 1 / 0 | 25 / 21 | 73 / 75 | 6 / 4 | 25 / 17 |
| 90-99 | 60 / 51 | 173 / 122 | 34 / 18 | 18 / 4 | 10 / 8 | 0 / 3 | 3 / 0 | 0 / 0 | 5 / 2 | 0 / 0 | 25 / 26 | 74 / 78 | 13 / 2 | 27 / 24 |
| 100-109 | 62 / 54 | 202 / 132 | 22 / 22 | 16 / 6 | 10 / 8 | 1 / 3 | 3 / 1 | 0 / 0 | 6 / 4 | 0 / 0 | 28 / 23 | 73 / 79 | 9 / 2 | 26 / 28 |
| 110-119 | 62 / 54 | 211 / 142 | 29 / 14 | 13 / 8 | 10 / 10 | 2 / 2 | 2 / 2 | 0 / 0 | 6 / 2 | 0 / 0 | 27 / 19 | 70 / 77 | 11 / 2 | 28 / 29 |
| 120-129 | 62 / 58 | 226 / 147 | 39 / 17 | 12 / 12 | 9 / 11 | 4 / 0 | 0 / 4 | 0 / 0 | 6 / 4 | 0 / 0 | 25 / 28 | 73 / 75 | 15 / 1 | 26 / 19 |
| 130-139 | 61 / 61 | 249 / 148 | 30 / 19 | 12 / 16 | 10 / 5 | 1 / 1 | 1 / 1 | 0 / 0 | 8 / 2 | 0 / 0 | 29 / 27 | 73 / 72 | 10 / 2 | 24 / 19 |
| 140-149 | 61 / 62 | 260 / 167 | 28 / 12 | 15 / 13 | 14 / 7 | 4 / 2 | 2 / 4 | 0 / 0 | 7 / 1 | 0 / 0 | 26 / 33 | 71 / 78 | 6 / 0 | 24 / 16 |

- SSS has 62 units at round 100 (we 39 and 45 in the two games above), eats 405 natural pearls in rounds 0-149 (we 190 and
  215), 131 of them on fountains of test4's half (we 1 and 18), and has 89 boxed deaths (we 41 and 44). Against SSS it is
  test4 that stays at home (30 pearls from SSS's half).

### Islands (large, 56x40; we won 0 of 30)

**Supply.** 1,546 natural pearls per 500 rounds, 85% on 26 fountain tiles. Each side has four big fountains 3-6 steps from its
queen's start ((41,6), (47,6), (41,9), (47,9) for side A; 54-79 pearls per 500 rounds each), three corridor tiles at (38-39,12-13),
one at (42,21), four at (42-43,36-38) and one at the bottom edge ((54,36) for A and (1,36) for B, three cells apart across the wrap).

**All games** (30 of ours): units at round 150: meow 36, test4 62, WHQ 57, forgot 57, SSS 57, Vibing++ 46. Natural pearls in
rounds 0-149: 202 / 281 / 241 / 281 / 266 / 227. Dragons rammed by the enemy: 33.8 / 8.3 / 9.6 / 32.3 / 25.1 / 20.6; dragons that rammed:
8.5 / 37.3 / 32.8 / 28.8 / 27.3 / 34.9. Boxed deaths: 24.7 / 27.8 / 31.3 / 37.0 / 50.2 / 33.2. Non-ram deaths with a free cell: 18.4 /
0.5 / 4.4 / 0.2 / 1.5 / 3.9. Meetings (a turn that begins with an enemy head on the next cell): 52.7 per game for us, and we step
away in 88% of them (test4 65%, WHQ 66%, forgot 63%, SSS 52%, Vibing++ 58%).
The 18.4 are steps through a portal onto a body on the far side, which the dragon cannot see: 12.7 onto a team-mate and 5.7
onto an enemy per game in rounds 0-149 (`c_freedeaths.py`; our opponents 3.0; on all large maps together we 6.4 and they
2.2). It is 43% of our non-ram deaths on this map and costs 44 segments a game.
By build (`c_out/bybatch_Islands.txt`): the 27 live games have 35 units against 60 at round 150 and total length 85 against 198;
the 3 test-build games 47 against 55 and 123 against 149; at round 300 both are lost (11 against 62 units, and 18 against 58).

**The live bot against test4, 1063012** (lost on the longest dragon, 11 against 57; 3 units left against 17):

Game 1063012, Islands: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 5 / 5 | 12 / 12 | 4 / 9 | 0 / 0 | 2 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 0 / 0 | 5 / 5 | 70 / 79 | 2 / 2 | 64 / 55 |
| 10-19 | 6 / 7 | 14 / 21 | 11 / 11 | 1 / 0 | 4 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 5 / 5 | 69 / 72 | 0 / 3 | 63 / 70 |
| 20-29 | 10 / 13 | 26 / 32 | 21 / 14 | 0 / 0 | 9 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 7 / 11 | 58 / 76 | 7 / 4 | 47 / 51 |
| 30-39 | 19 / 19 | 47 / 46 | 16 / 14 | 0 / 4 | 8 / 7 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 1 | 0 / 0 | 14 / 14 | 67 / 77 | 3 / 3 | 46 / 39 |
| 40-49 | 26 / 24 | 61 / 57 | 19 / 12 | 2 / 5 | 9 / 8 | 2 / 0 | 0 / 2 | 0 / 0 | 1 / 1 | 0 / 0 | 19 / 17 | 69 / 82 | 10 / 3 | 41 / 36 |
| 50-59 | 32 / 29 | 76 / 67 | 17 / 15 | 5 / 0 | 11 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 1 | 2 / 0 | 22 / 18 | 66 / 77 | 7 / 3 | 43 / 29 |
| 60-69 | 38 / 34 | 87 / 79 | 19 / 14 | 4 / 2 | 8 / 5 | 1 / 0 | 0 / 1 | 0 / 0 | 3 / 1 | 0 / 0 | 26 / 21 | 57 / 77 | 6 / 3 | 43 / 25 |
| 70-79 | 42 / 37 | 100 / 90 | 15 / 21 | 7 / 13 | 11 / 10 | 6 / 0 | 0 / 6 | 0 / 0 | 1 / 2 | 2 / 0 | 30 / 28 | 55 / 73 | 3 / 8 | 40 / 35 |
| 80-89 | 44 / 39 | 102 / 96 | 12 / 19 | 6 / 22 | 9 / 15 | 7 / 1 | 1 / 7 | 0 / 0 | 2 / 2 | 2 / 0 | 31 / 25 | 58 / 74 | 4 / 8 | 35 / 38 |
| 90-99 | 41 / 44 | 94 / 108 | 17 / 14 | 4 / 15 | 7 / 10 | 3 / 0 | 0 / 3 | 0 / 2 | 1 / 3 | 0 / 0 | 29 / 27 | 60 / 72 | 6 / 4 | 44 / 27 |
| 100-109 | 44 / 46 | 105 / 117 | 11 / 23 | 10 / 13 | 5 / 15 | 6 / 0 | 0 / 6 | 0 / 0 | 3 / 4 | 1 / 0 | 31 / 29 | 56 / 64 | 4 / 6 | 31 / 38 |
| 110-119 | 39 / 51 | 102 / 124 | 17 / 17 | 2 / 30 | 10 / 16 | 8 / 1 | 1 / 8 | 0 / 0 | 3 / 4 | 0 / 0 | 28 / 34 | 60 / 63 | 7 / 7 | 48 / 29 |
| 120-129 | 37 / 54 | 93 / 133 | 9 / 22 | 12 / 26 | 8 / 20 | 9 / 2 | 2 / 9 | 0 / 0 | 2 / 3 | 1 / 0 | 27 / 33 | 53 / 60 | 4 / 8 | 30 / 25 |
| 130-139 | 31 / 60 | 77 / 141 | 3 / 31 | 4 / 22 | 4 / 8 | 4 / 0 | 0 / 4 | 0 / 0 | 2 / 2 | 1 / 0 | 25 / 40 | 48 / 58 | 0 / 15 | 38 / 39 |
| 140-149 | 28 / 62 | 67 / 170 | 4 / 23 | 6 / 6 | 3 / 5 | 2 / 2 | 2 / 2 | 0 / 0 | 0 / 1 | 1 / 0 | 23 / 40 | 55 / 60 | 0 / 11 | 42 / 45 |

- For 90 rounds we are level or ahead: 44 units against 39 at round 80, total 102 against 96, and 134 natural pearls
  against 129 in rounds 0-89. Nothing is wrong with the opening.
- From round 70 test4 rams: 6, 7, 3, 6, 8, 9, 4, 2 of our dragons per 10 rounds, 49 in the 150 rounds; we ram 6 times, in 3 of
  56 meetings. test4 eats the dead: 13-30 corpse pearls per 10 rounds in rounds 70-139 against our 2-12. Ten more of ours die with
  a free cell beside them (the step through a portal onto a body).
- Units: 44 at round 100, 26 at round 150, 5 at round 300; test4 46, 62, 63. The test build against the same opponent
  (1067905) makes 21 rams and suffers 32 in rounds 0-149 and has 41 units against 63 at round 150; it is lost as well.

**The test build with a good opening, 1068051 against WHQ** (lost on the longest dragon, 16 against 82):

Game 1068051, Islands: A = meow, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 5 / 5 | 12 / 12 | 6 / 8 | 0 / 0 | 3 / 2 | 0 / 0 | 0 / 0 | 0 / 2 | 1 / 0 | 0 / 0 | 5 / 5 | 81 / 82 | 2 / 1 | 65 / 61 |
| 10-19 | 7 / 5 | 16 / 16 | 13 / 8 | 2 / 0 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 6 / 4 | 65 / 78 | 1 / 2 | 70 / 74 |
| 20-29 | 11 / 9 | 31 / 24 | 17 / 14 | 0 / 2 | 7 / 7 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 10 / 8 | 70 / 81 | 5 / 1 | 58 / 67 |
| 30-39 | 17 / 15 | 46 / 37 | 16 / 10 | 3 / 1 | 9 / 6 | 0 / 1 | 1 / 0 | 0 / 0 | 0 / 3 | 1 / 1 | 13 / 10 | 70 / 88 | 5 / 0 | 57 / 34 |
| 40-49 | 24 / 16 | 60 / 38 | 21 / 10 | 7 / 2 | 10 / 5 | 1 / 1 | 1 / 1 | 0 / 0 | 2 / 2 | 1 / 0 | 17 / 11 | 73 / 96 | 4 / 0 | 28 / 33 |
| 50-59 | 29 / 17 | 76 / 41 | 24 / 10 | 7 / 1 | 15 / 5 | 0 / 1 | 1 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 21 / 11 | 72 / 100 | 3 / 0 | 30 / 39 |
| 60-69 | 42 / 19 | 103 / 45 | 24 / 13 | 4 / 3 | 14 / 5 | 1 / 0 | 0 / 1 | 0 / 0 | 2 / 0 | 0 / 0 | 27 / 10 | 69 / 100 | 3 / 0 | 32 / 45 |
| 70-79 | 53 / 23 | 124 / 56 | 24 / 7 | 7 / 6 | 13 / 6 | 5 / 2 | 2 / 5 | 0 / 0 | 3 / 1 | 1 / 0 | 31 / 12 | 65 / 100 | 4 / 0 | 22 / 40 |
| 80-89 | 55 / 21 | 129 / 46 | 21 / 17 | 7 / 14 | 11 / 9 | 0 / 3 | 3 / 0 | 0 / 0 | 1 / 0 | 2 / 0 | 33 / 12 | 76 / 100 | 2 / 0 | 26 / 45 |
| 90-99 | 60 / 27 | 142 / 65 | 15 / 15 | 8 / 20 | 10 / 10 | 4 / 3 | 3 / 4 | 0 / 0 | 2 / 2 | 1 / 0 | 35 / 16 | 77 / 100 | 2 / 0 | 39 / 33 |
| 100-109 | 60 / 28 | 141 / 72 | 27 / 13 | 19 / 11 | 9 / 9 | 2 / 0 | 0 / 2 | 0 / 0 | 5 / 2 | 2 / 2 | 33 / 15 | 71 / 97 | 1 / 0 | 40 / 31 |
| 110-119 | 60 / 31 | 161 / 81 | 17 / 15 | 10 / 9 | 9 / 11 | 3 / 2 | 2 / 3 | 0 / 2 | 3 / 1 | 1 / 1 | 37 / 19 | 72 / 95 | 2 / 0 | 40 / 30 |
| 120-129 | 60 / 33 | 163 / 85 | 23 / 12 | 12 / 19 | 10 / 12 | 5 / 3 | 3 / 5 | 0 / 0 | 1 / 0 | 1 / 1 | 36 / 20 | 68 / 95 | 3 / 0 | 22 / 39 |
| 130-139 | 60 / 36 | 168 / 90 | 14 / 14 | 29 / 7 | 14 / 10 | 2 / 4 | 4 / 2 | 0 / 0 | 3 / 2 | 5 / 0 | 36 / 26 | 69 / 96 | 2 / 0 | 38 / 33 |
| 140-149 | 60 / 38 | 174 / 89 | 19 / 14 | 20 / 15 | 15 / 11 | 5 / 2 | 2 / 5 | 0 / 0 | 3 / 3 | 5 / 0 | 39 / 22 | 71 / 94 | 3 / 0 | 38 / 30 |

Game 1068051, Islands: A = meow, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 150-199 | 60 / 39 | 170 / 91 | 78 / 72 | 57 / 92 | 45 / 56 | 26 / 5 | 5 / 26 | 0 / 0 | 17 / 11 | 8 / 1 | 39 / 21 | 76 / 96 | 5 / 0 | 47 / 37 |
| 200-249 | 49 / 52 | 138 / 131 | 42 / 105 | 56 / 103 | 32 / 63 | 18 / 11 | 11 / 18 | 0 / 0 | 6 / 24 | 7 / 2 | 33 / 24 | 84 / 83 | 0 / 20 | 56 / 37 |
| 250-299 | 39 / 60 | 116 / 192 | 29 / 97 | 28 / 117 | 19 / 62 | 12 / 5 | 5 / 12 | 0 / 0 | 5 / 24 | 4 / 30 | 26 / 32 | 79 / 83 | 0 / 26 | 52 / 41 |
| 300-349 | 32 / 51 | 101 / 209 | 30 / 108 | 16 / 136 | 12 / 74 | 8 / 1 | 1 / 8 | 0 / 0 | 14 / 13 | 2 / 62 | 24 / 27 | 67 / 75 | 3 / 33 | 45 / 36 |

- We lead until round 150: 60 units against 39, total 170 against 91 (the live bot against WHQ on this map an hour earlier,
  1063240: 47 against 61 and 108 against 189; it rams in 6 of 84 meetings, the test build in 11 of 40). Then our units fall 60,
  49, 39, 32, 19 and WHQ's rise 39, 52, 60. The ledger per 50 rounds (`c_ledger.py`): natural pearls 100, 78, 42, 29, 30 for us
  from round 100 and 68, 72, 105, 97, 108 for WHQ; segments we lose to WHQ's rams 58, 99, 63, 41, 32; segments WHQ loses in the
  rams it makes 44, 74, 53, 36, 28. WHQ's rammers are shorter than their victims (2.8 against 3.8 segments on average in
  rounds 150-199) and WHQ eats 38 pearls of our dead in rounds 150-199 while we eat 15 of theirs.
- By length class (`c_out/mid_1068051.txt`): in rounds 150-199 our 2-longs eat 1.86 natural pearls per 100 dragon-rounds and
  WHQ's 3.08; 3-4-longs 3.11 and 3.78. In rounds 150-209, 23-29 of our 49-60 dragons have not eaten for 20 rounds (WHQ: 11-17
  of 39-53). A pearl lies uneaten on 42-69% of the fountain tile-rounds of our half after round 150 (before: 22-40% from round
  40 on; WHQ's half after round 150: 29-47%).
- Rounds 140-220 dragon by dragon (`c_out/midlist_1068051.txt`; the 28 of our dragons that were 5 or longer at some round):
  9 were rammed, by attackers of 2-4 (`#76` at L12 by an L2 at (26,3) after it left the fountains at (42-43,37-38) at round 180
  and walked 40 cells; `#133` L9 by an L3; `#241` L9 by an L4; `#360` L10 by an L2 five rounds after it was born; `#290` L7 by
  an L2; `#326` L6; `#207` L5; `#316` L5 in the round it was born; `#44` L4). 8 shed their front two segments in a place with
  no way out (12 -> 2+10 twice, 7 -> 2+5 three times, 6 -> 2+4 twice, 5 -> 2+3), the 2-long front part dying the next round.
  The others roam: `#84` (L5 -> 10) stands on 76 different cells in 81 rounds and eats 5 pearls; `#315` (L5) takes 93 steps in
  48 rounds and eats nothing. None of them splits in the ordinary way (our rule: no growth splits above length 4 after round 150
  on maps over 1,200 cells).
- A camper that does not eat: our `#3` (L3) circles six cells next to the fountain (1,36) from round 14 to 26; at round 20 a
  natural pearl lies on (1,36), next to its head at (1,37), with nobody near, and it steps west. It eats one pearl in 13
  rounds. (Why it declined I could not determine; the bot's score for that step is not in the replay.)

**forgot against the same opponent from our side, 1062235** (forgot won on the longest dragon, 84 against 63):

Game 1062235, Islands: A = forgot, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-49 | 5 / 5 | 12 / 12 | 76 / 53 | 6 / 12 | 36 / 28 | 3 / 1 | 1 / 3 | 0 / 4 | 2 / 3 | 0 / 2 | 5 / 5 | 75 / 84 | 17 / 7 | 56 / 63 |
| 50-99 | 35 / 20 | 80 / 47 | 129 / 64 | 78 / 33 | 74 / 38 | 10 / 17 | 17 / 10 | 0 / 2 | 20 / 6 | 0 / 1 | 20 / 13 | 65 / 86 | 28 / 4 | 30 / 32 |
| 100-149 | 62 / 22 | 172 / 58 | 112 / 57 | 77 / 57 | 48 / 44 | 12 / 12 | 12 / 12 | 0 / 0 | 24 / 11 | 0 / 0 | 35 / 15 | 66 / 97 | 20 / 0 | 37 / 38 |
| 150-199 | 62 / 31 | 188 / 72 | 99 / 66 | 116 / 68 | 64 / 47 | 13 / 19 | 19 / 13 | 0 / 0 | 33 / 10 | 0 / 1 | 41 / 16 | 62 / 93 | 10 / 2 | 41 / 35 |
| 200-249 | 61 / 35 | 184 / 92 | 105 / 68 | 113 / 63 | 60 / 54 | 10 / 20 | 20 / 10 | 0 / 0 | 28 / 22 | 1 / 0 | 37 / 19 | 69 / 96 | 16 / 3 | 35 / 36 |
| 250-299 | 62 / 37 | 188 / 91 | 105 / 66 | 115 / 74 | 58 / 51 | 8 / 21 | 21 / 8 | 0 / 4 | 28 / 17 | 1 / 5 | 39 / 19 | 76 / 97 | 16 / 0 | 36 / 38 |
| 300-349 | 62 / 33 | 204 / 79 | 100 / 62 | 109 / 79 | 73 / 37 | 11 / 9 | 9 / 11 | 4 / 0 | 26 / 11 | 24 / 12 | 37 / 16 | 71 / 100 | 10 / 0 | 33 / 41 |

- forgot has 61-62 units from round 100 to 350. It loses 8-13 dragons to rams per 50 rounds (we 8-26) and makes 9-21 rams
  (we 1-11), replaces its losses (48-74 splits per 50 rounds; we 45, 32, 19, 12 after round 150) and keeps eating 99-129
  natural pearls per 50 rounds. WHQ against forgot stays at 20-37 units.

### Slithery Fight (large, 63x27; we won 5 of 29)

**Supply.** 2,720 natural pearls per 500 rounds, the richest map; 86% on 115 fountain tiles, most of them in narrow corridors and
at their closed ends (rows 0-1 and 25-26, and single cells such as (39,19) and (46,19)).

**All games** (29 of ours): units at round 150: meow 57, test4 62, WHQ 63, forgot 61, SSS 62, Vibing++ 57. Total length at round
150: 160 / 204 / 229 / 160 / 208 / 170. Natural pearls in rounds 0-149: 421 / 409 / 497 / 549 / 388 / 502. Boxed deaths: 242 / 169 / 205 /
262 / 87 / 284. Splits: 322 / 250 / 290 / 356 / 179 / 367. Dragons rammed: 21.5 / 3.8 / 5.1 / 17.3 / 18.4 / 9.6; dragons that rammed: 4.5 /
21.9 / 20.7 / 18.9 / 18.0 / 18.4. We eat as much as test4 here; the length goes into deaths. The test build is no better on this
map (3 games: 53 units against 61 and total 145 against 226 at round 150; the 26 live games 58 against 62 and 162 against 207).

**The live bot against WHQ, 1063252** (lost on the longest dragon, 64 against 94):

Game 1063252, Slithery Fight: A = meow, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 7 / 7 | 47 / 47 | 27 / 25 | 6 / 4 | 24 / 26 | 0 / 0 | 0 / 0 | 0 / 0 | 11 / 8 | 0 / 1 | 7 / 7 | 90 / 86 | 0 / 5 | 40 / 47 |
| 10-19 | 20 / 24 | 58 / 55 | 28 / 30 | 6 / 5 | 14 / 15 | 0 / 0 | 0 / 0 | 0 / 0 | 6 / 8 | 0 / 0 | 12 / 14 | 92 / 83 | 6 / 11 | 53 / 60 |
| 20-29 | 28 / 31 | 80 / 74 | 35 / 29 | 11 / 10 | 20 / 20 | 0 / 0 | 0 / 0 | 0 / 0 | 14 / 12 | 0 / 0 | 19 / 18 | 89 / 76 | 9 / 11 | 25 / 56 |
| 30-39 | 34 / 39 | 96 / 87 | 33 / 30 | 12 / 11 | 20 / 18 | 0 / 0 | 0 / 0 | 0 / 0 | 17 / 12 | 0 / 0 | 21 / 23 | 85 / 80 | 10 / 13 | 31 / 50 |
| 40-49 | 37 / 45 | 107 / 101 | 24 / 34 | 21 / 19 | 23 / 22 | 1 / 0 | 0 / 1 | 0 / 0 | 20 / 12 | 0 / 0 | 22 / 23 | 85 / 81 | 3 / 10 | 40 / 52 |
| 50-59 | 39 / 54 | 108 / 127 | 32 / 27 | 24 / 23 | 25 / 21 | 3 / 0 | 0 / 3 | 0 / 0 | 19 / 18 | 0 / 0 | 22 / 21 | 84 / 81 | 11 / 8 | 34 / 48 |
| 60-69 | 42 / 54 | 113 / 128 | 31 / 32 | 31 / 24 | 24 / 25 | 1 / 0 | 0 / 1 | 0 / 0 | 26 / 18 | 0 / 0 | 19 / 26 | 85 / 78 | 11 / 10 | 26 / 48 |
| 70-79 | 39 / 60 | 114 / 141 | 33 / 33 | 28 / 22 | 29 / 22 | 3 / 0 | 0 / 3 | 0 / 0 | 20 / 18 | 0 / 0 | 20 / 27 | 89 / 78 | 8 / 14 | 32 / 39 |
| 80-89 | 45 / 61 | 126 / 151 | 33 / 26 | 33 / 34 | 28 / 23 | 3 / 0 | 0 / 3 | 2 / 0 | 23 / 21 | 0 / 0 | 24 / 27 | 89 / 83 | 6 / 9 | 34 / 38 |
| 90-99 | 45 / 60 | 128 / 148 | 23 / 35 | 25 / 23 | 24 / 18 | 1 / 0 | 0 / 1 | 2 / 0 | 20 / 14 | 0 / 0 | 25 / 29 | 88 / 85 | 8 / 12 | 36 / 42 |
| 100-109 | 46 / 63 | 129 / 163 | 33 / 32 | 18 / 28 | 25 / 19 | 2 / 0 | 0 / 2 | 0 / 0 | 15 / 17 | 0 / 0 | 24 / 29 | 90 / 84 | 8 / 12 | 32 / 49 |
| 110-119 | 54 / 63 | 144 / 172 | 35 / 24 | 25 / 23 | 25 / 14 | 1 / 0 | 0 / 1 | 0 / 0 | 23 / 17 | 0 / 0 | 27 / 32 | 89 / 86 | 11 / 6 | 29 / 43 |
| 120-129 | 55 / 59 | 155 / 174 | 29 / 18 | 25 / 7 | 28 / 12 | 0 / 0 | 0 / 0 | 0 / 0 | 25 / 7 | 0 / 0 | 26 / 33 | 88 / 88 | 6 / 8 | 35 / 54 |
| 130-139 | 58 / 64 | 156 / 180 | 29 / 24 | 27 / 17 | 22 / 12 | 0 / 2 | 2 / 0 | 0 / 0 | 19 / 9 | 0 / 1 | 28 / 30 | 87 / 88 | 8 / 8 | 43 / 55 |
| 140-149 | 59 / 64 | 159 / 184 | 31 / 48 | 25 / 23 | 18 / 15 | 2 / 0 | 0 / 2 | 0 / 0 | 14 / 14 | 0 / 0 | 29 / 29 | 85 / 89 | 11 / 18 | 42 / 43 |

- A level game for 150 rounds: 61 units against 63 and total 176 against 200 at round 150, 456 natural pearls against 447.
  We make 349 new dragons and lose 272 boxed; WHQ 282 and 205. WHQ rams 17 of ours and we ram 2 (1 of 26 meetings). It is lost
  in the second half: total 174 against 256 at round 300.

**The test build against test4, 1067917** (lost on the queen rule; final 21 units and total 153 against 36 and 244):

Game 1067917, Slithery Fight: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 7 / 7 | 47 / 47 | 26 / 23 | 5 / 6 | 23 / 25 | 0 / 0 | 0 / 0 | 0 / 0 | 10 / 10 | 0 / 0 | 7 / 7 | 91 / 92 | 0 / 0 | 45 / 45 |
| 10-19 | 20 / 22 | 58 / 54 | 30 / 36 | 6 / 7 | 15 / 17 | 0 / 0 | 0 / 0 | 0 / 0 | 7 / 7 | 0 / 0 | 15 / 16 | 91 / 87 | 5 / 8 | 59 / 61 |
| 20-29 | 28 / 32 | 80 / 82 | 34 / 20 | 11 / 5 | 21 / 12 | 0 / 0 | 0 / 0 | 0 / 0 | 14 / 7 | 0 / 0 | 18 / 18 | 85 / 79 | 13 / 11 | 38 / 49 |
| 30-39 | 35 / 37 | 97 / 91 | 34 / 37 | 23 / 12 | 22 / 19 | 2 / 0 | 0 / 2 | 0 / 0 | 22 / 6 | 0 / 0 | 20 / 26 | 86 / 78 | 11 / 14 | 34 / 49 |
| 40-49 | 33 / 48 | 103 / 122 | 28 / 33 | 21 / 18 | 27 / 25 | 2 / 0 | 0 / 2 | 0 / 0 | 20 / 13 | 0 / 0 | 24 / 23 | 86 / 78 | 9 / 14 | 40 / 30 |
| 50-59 | 38 / 58 | 106 / 141 | 24 / 24 | 25 / 20 | 23 / 21 | 1 / 0 | 0 / 1 | 0 / 0 | 22 / 18 | 0 / 0 | 24 / 27 | 84 / 77 | 7 / 8 | 41 / 35 |
| 60-69 | 38 / 60 | 104 / 145 | 31 / 35 | 22 / 23 | 22 / 20 | 1 / 0 | 0 / 1 | 0 / 0 | 20 / 16 | 0 / 0 | 25 / 30 | 82 / 73 | 9 / 15 | 42 / 35 |
| 70-79 | 39 / 63 | 113 / 163 | 22 / 28 | 22 / 30 | 20 / 19 | 4 / 0 | 0 / 4 | 0 / 0 | 18 / 16 | 0 / 0 | 24 / 34 | 83 / 72 | 8 / 7 | 36 / 36 |
| 80-89 | 37 / 62 | 107 / 164 | 23 / 29 | 24 / 33 | 22 / 18 | 2 / 1 | 1 / 2 | 0 / 0 | 21 / 15 | 0 / 0 | 22 / 31 | 85 / 73 | 8 / 17 | 39 / 33 |
| 90-99 | 35 / 62 | 103 / 169 | 23 / 27 | 22 / 20 | 24 / 11 | 0 / 0 | 0 / 0 | 0 / 0 | 19 / 9 | 0 / 0 | 20 / 29 | 86 / 74 | 8 / 11 | 35 / 43 |
| 100-109 | 40 / 64 | 110 / 189 | 26 / 22 | 25 / 31 | 23 / 12 | 1 / 1 | 1 / 1 | 0 / 0 | 20 / 11 | 0 / 0 | 22 / 32 | 89 / 71 | 10 / 8 | 33 / 46 |
| 110-119 | 41 / 63 | 113 / 178 | 24 / 33 | 29 / 22 | 25 / 10 | 2 / 2 | 2 / 2 | 0 / 0 | 21 / 6 | 0 / 0 | 23 / 35 | 89 / 69 | 8 / 14 | 42 / 47 |
| 120-129 | 41 / 63 | 112 / 198 | 25 / 39 | 25 / 24 | 21 / 12 | 3 / 0 | 0 / 3 | 0 / 0 | 20 / 9 | 0 / 0 | 25 / 33 | 89 / 68 | 6 / 17 | 36 / 44 |
| 130-139 | 39 / 63 | 113 / 221 | 22 / 25 | 24 / 17 | 20 / 11 | 1 / 1 | 1 / 1 | 0 / 0 | 20 / 9 | 0 / 0 | 24 / 33 | 90 / 68 | 8 / 11 | 38 / 53 |
| 140-149 | 37 / 63 | 111 / 223 | 21 / 30 | 22 / 18 | 25 / 8 | 0 / 1 | 1 / 0 | 0 / 0 | 19 / 7 | 0 / 0 | 25 / 35 | 91 / 73 | 9 / 14 | 43 / 45 |

- 38 units at round 50 against 58, 40 at round 100 against 64, 42 at round 150 against 63. Per 50 rounds we eat 152, 123, 118
  natural pearls and 66, 115, 125 corpse pearls and lose 73, 100, 100 dragons boxed (148, 209, 208 segments); test4 eats 149,
  143, 149 and 48, 126, 112 and loses 43, 74, 42 (92, 191, 155 segments).
- 274 non-ram deaths in 150 rounds on 34 cells; 37 on (46,19) and 37 on (39,19), one every four rounds on each.
- The form of it (`c_out/ec_1067917.txt`, splits): 57 splits 4 -> 2+2, and 236 splits in which a dragon of 6, 7 or 8 keeps
  only its front two segments (6 -> 2+4: 92, 7 -> 2+5: 63, 8 -> 2+6: 81). Natural pearls by the eater's length: 2: 49, 3: 70,
  4: 103, 5: 37, 6 and more: 136. Our dragons walk into a closed corridor, eat everything in it, grow to 6-8 and then shed the
  front two, which die; the rear part, now a dragon of 4-6 with its head at the old tail, goes back in for the dead front's
  pearl. That makes no new dragon. In our bot this is the "harvest" mode (`harvestable()`: enter a dead end that holds at least
  3 pearls, do not split while harvesting, leave by the escape split). The rule is the same in the live bot and the test build.
- forgot on the same side against test4 (1046988): 294 of its 375 splits are 4 -> 2+2 and its eaters are 2 long (247 pearls) or
  3 long (246); it has as many boxed deaths as we do (275) but 50 units at round 50 and 61 at round 100. Vibing++ (1054792):
  276 boxed deaths, 589 natural pearls, 58 units at round 100.
- All our games on this map, rounds 0-99 (`c_out/midall_1119_Slithery Fight.txt`): 65 splits at length 4 and 125 sheds per game;
  our opponents 120 and 56. On the other three large maps our sheds are 1-17 a game, the same as our opponents', and on
  medium and small maps 5 against 5-6: the shed form is this map's (closed corridors full of fountains), not a general habit.

**SSS against test4 from our side, 1051824** (SSS won on the longest dragon, 22 against 18):

Game 1051824, Slithery Fight: A = SSS, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 7 / 7 | 47 / 47 | 17 / 25 | 2 / 5 | 22 / 25 | 0 / 0 | 0 / 0 | 0 / 0 | 6 / 9 | 0 / 0 | 7 / 7 | 92 / 91 | 0 / 2 | 48 / 48 |
| 10-19 | 23 / 23 | 51 / 58 | 13 / 28 | 2 / 7 | 7 / 17 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 7 | 0 / 0 | 16 / 13 | 96 / 81 | 0 / 11 | 59 / 71 |
| 20-29 | 27 / 33 | 60 / 78 | 19 / 33 | 3 / 9 | 10 / 16 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 10 | 0 / 0 | 18 / 22 | 93 / 81 | 2 / 15 | 54 / 66 |
| 30-39 | 35 / 39 | 77 / 98 | 21 / 27 | 4 / 12 | 12 / 18 | 1 / 1 | 1 / 1 | 2 / 0 | 3 / 12 | 0 / 0 | 18 / 25 | 87 / 79 | 7 / 8 | 53 / 60 |
| 40-49 | 40 / 43 | 87 / 109 | 21 / 31 | 11 / 25 | 11 / 23 | 5 / 1 | 1 / 5 | 0 / 0 | 3 / 17 | 0 / 0 | 23 / 21 | 87 / 87 | 6 / 7 | 62 / 48 |
| 50-59 | 42 / 43 | 93 / 110 | 24 / 28 | 7 / 20 | 11 / 21 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 12 | 0 / 0 | 25 / 23 | 85 / 83 | 9 / 8 | 61 / 50 |
| 60-69 | 51 / 52 | 118 / 131 | 17 / 20 | 3 / 17 | 9 / 17 | 3 / 0 | 0 / 3 | 0 / 0 | 4 / 13 | 0 / 0 | 28 / 28 | 87 / 83 | 7 / 8 | 56 / 44 |
| 70-79 | 53 / 53 | 120 / 133 | 24 / 25 | 17 / 24 | 13 / 20 | 2 / 3 | 3 / 2 | 0 / 0 | 3 / 15 | 0 / 0 | 25 / 26 | 87 / 86 | 8 / 5 | 65 / 51 |
| 80-89 | 58 / 53 | 142 / 136 | 17 / 27 | 11 / 24 | 12 / 22 | 2 / 2 | 2 / 2 | 0 / 0 | 7 / 14 | 0 / 0 | 25 / 24 | 89 / 85 | 7 / 7 | 62 / 44 |
| 90-99 | 59 / 57 | 135 / 144 | 26 / 21 | 10 / 24 | 10 / 20 | 2 / 1 | 1 / 2 | 0 / 0 | 5 / 15 | 0 / 0 | 31 / 27 | 86 / 82 | 9 / 8 | 54 / 51 |
| 100-109 | 61 / 59 | 149 / 143 | 26 / 26 | 18 / 17 | 12 / 15 | 1 / 2 | 2 / 1 | 0 / 0 | 8 / 14 | 0 / 0 | 29 / 27 | 87 / 79 | 7 / 6 | 61 / 60 |
| 110-119 | 62 / 57 | 159 / 146 | 32 / 25 | 16 / 26 | 6 / 21 | 0 / 1 | 1 / 0 | 0 / 0 | 6 / 19 | 0 / 0 | 30 / 31 | 86 / 76 | 10 / 10 | 52 / 59 |
| 120-129 | 61 / 58 | 181 / 151 | 33 / 24 | 14 / 27 | 13 / 21 | 2 / 0 | 0 / 2 | 2 / 0 | 8 / 18 | 0 / 0 | 32 / 27 | 83 / 79 | 9 / 6 | 58 / 54 |
| 130-139 | 62 / 59 | 191 / 147 | 24 / 27 | 16 / 22 | 10 / 16 | 1 / 1 | 1 / 1 | 0 / 0 | 9 / 10 | 0 / 0 | 28 / 30 | 85 / 77 | 4 / 4 | 51 / 61 |
| 140-149 | 61 / 63 | 197 / 164 | 30 / 20 | 20 / 22 | 12 / 13 | 4 / 0 | 0 / 4 | 0 / 0 | 8 / 8 | 0 / 0 | 27 / 29 | 86 / 78 | 10 / 5 | 52 / 60 |

- SSS eats 344 natural pearls in 150 rounds, a quarter fewer than we do in the live game above (456) and fewer than test4
  (387), makes 170 new dragons and loses 77 boxed (we 349 and 272), and has 61 units and total length 200 at round 150
  against test4's 64 and 167 (we 61 and 176 against WHQ, 42 and 113 against test4). 99 of its 170 splits are at length 4, 37
  at length 5, and only 24 are by dragons of 6-8 that keep their front two segments. Fewer pearls, far fewer deaths, more
  length: on this map the deaths are what our pearls pay for.

### Trauma (medium, 48x24; we won 4 of 27)

**Supply.** 732 natural pearls per 500 rounds; 42% on 10 fountain tiles (a column of five at (13,10-14) and its mirror at
(34,9-13)); the rest on 130 slow tiles. The two start areas are separated by portals; nobody rams before round 150.

**All games** (27 of ours): units at round 150: meow 14, test4 40, WHQ 35, forgot 35, SSS 33, Vibing++ 32. Natural pearls in
rounds 0-149: 48 / 120 / 106 / 110 / 106 / 112, of which on the own fountain column 27 / 66 / 54 / 62 / 60 / 73. Natural pearls per 100
dragon-turns: 4.5 / 4.4 / 5.2 / 4.4 / 5.2 / 4.8, the same for everybody: the gap is the number of dragons, and it is made in the
first 50 rounds. A pearl lies on 76% of our fountain tile-rounds (test4 34%, WHQ 47%).

**Against test4, 1067915** (test build, the same as the live bot on this map; lost on the queen rule):

Game 1067915, Trauma: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 8 / 8 | 0 / 0 | 0 / 0 | 2 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 90 / 90 |
| 10-19 | 4 / 3 | 8 / 8 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 4 / 3 | 100 / 100 | 0 / 0 | 100 / 100 |
| 20-29 | 4 / 3 | 8 / 9 | 0 / 6 | 0 / 0 | 0 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 3 / 3 | 100 / 100 | 0 / 0 | 100 / 30 |
| 30-39 | 4 / 6 | 8 / 13 | 2 / 5 | 0 / 1 | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 3 / 5 | 100 / 100 | 0 / 0 | 100 / 24 |
| 40-49 | 4 / 8 | 10 / 17 | 0 / 7 | 0 / 1 | 0 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 4 / 8 | 100 / 100 | 0 / 0 | 100 / 24 |
| 50-59 | 4 / 11 | 10 / 23 | 0 / 5 | 0 / 1 | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 4 / 11 | 100 / 100 | 0 / 0 | 100 / 24 |
| 60-69 | 4 / 13 | 10 / 27 | 6 / 5 | 0 / 1 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 4 / 13 | 100 / 100 | 0 / 0 | 58 / 24 |
| 70-79 | 6 / 15 | 14 / 31 | 0 / 7 | 0 / 1 | 0 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 6 / 13 | 100 / 100 | 0 / 0 | 84 / 24 |
| 80-89 | 5 / 17 | 12 / 35 | 0 / 13 | 0 / 2 | 0 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 4 / 15 | 100 / 100 | 0 / 0 | 100 / 24 |
| 90-99 | 5 / 21 | 12 / 48 | 4 / 8 | 1 / 2 | 1 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 3 | 0 / 0 | 4 / 16 | 100 / 100 | 0 / 0 | 78 / 24 |
| 100-109 | 6 / 23 | 17 / 52 | 1 / 11 | 2 / 4 | 3 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 4 | 0 / 0 | 6 / 14 | 100 / 100 | 0 / 0 | 64 / 24 |
| 110-119 | 6 / 24 | 14 / 59 | 6 / 8 | 2 / 3 | 3 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 0 / 0 | 6 / 19 | 100 / 100 | 0 / 0 | 50 / 24 |
| 120-129 | 7 / 27 | 18 / 65 | 0 / 12 | 0 / 3 | 0 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 4 | 0 / 0 | 6 / 20 | 100 / 95 | 0 / 0 | 92 / 24 |
| 130-139 | 7 / 29 | 18 / 71 | 5 / 12 | 1 / 3 | 2 / 9 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 0 / 0 | 7 / 23 | 100 / 90 | 0 / 0 | 100 / 24 |
| 140-149 | 7 / 36 | 20 / 82 | 0 / 11 | 0 / 1 | 1 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 3 | 0 / 0 | 6 / 28 | 100 / 88 | 0 / 0 | 100 / 24 |

- test4 eats on its fountain column from round 20 (from then on a pearl lies on its five tiles in a quarter of the
  tile-rounds); we eat our first fountain pearls after round 60, and a pearl lies on ours in 50-100% of the tile-rounds all
  game. In 150 rounds we eat 24 natural pearls, 13 of them on our column; test4 111 and 66. 7 units against 36 at round 140.
  This is the known problem (the fountains are reached through a portal).

**Against WHQ, 1068061** (same bot; lost by wipe-out at round 467):

Game 1068061, Trauma: A = meow, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 8 / 8 | 0 / 0 | 0 / 0 | 2 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 90 / 90 |
| 10-19 | 4 / 4 | 8 / 8 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 4 / 3 | 100 / 100 | 0 / 0 | 100 / 100 |
| 20-29 | 4 / 4 | 8 / 9 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 4 | 100 / 100 | 0 / 0 | 100 / 100 |
| 30-39 | 4 / 4 | 8 / 9 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 2 / 4 | 100 / 100 | 0 / 0 | 100 / 100 |
| 40-49 | 4 / 3 | 8 / 7 | 1 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 3 | 100 / 100 | 0 / 0 | 100 / 100 |
| 50-59 | 4 / 3 | 9 / 7 | 0 / 3 | 0 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 4 / 3 | 100 / 100 | 0 / 0 | 100 / 100 |
| 60-69 | 4 / 3 | 9 / 8 | 5 / 7 | 0 / 1 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 0 / 0 | 4 / 3 | 100 / 100 | 0 / 0 | 98 / 100 |
| 70-79 | 6 / 6 | 12 / 16 | 10 / 0 | 0 / 0 | 4 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 0 / 0 | 5 / 4 | 100 / 100 | 0 / 0 | 44 / 100 |
| 80-89 | 8 / 5 | 18 / 12 | 0 / 4 | 0 / 1 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 7 / 5 | 100 / 100 | 0 / 0 | 100 / 100 |
| 90-99 | 8 / 6 | 18 / 17 | 1 / 4 | 0 / 0 | 0 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 6 / 6 | 100 / 100 | 0 / 0 | 100 / 100 |
| 100-109 | 8 / 8 | 19 / 21 | 1 / 4 | 0 / 0 | 0 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 2 | 0 / 0 | 6 / 7 | 100 / 100 | 0 / 0 | 100 / 100 |
| 110-119 | 8 / 8 | 20 / 21 | 5 / 7 | 2 / 2 | 2 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 0 / 0 | 7 / 8 | 100 / 100 | 0 / 0 | 60 / 100 |
| 120-129 | 9 / 11 | 25 / 30 | 7 / 0 | 1 / 2 | 1 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 8 / 9 | 100 / 98 | 0 / 0 | 72 / 100 |
| 130-139 | 9 / 11 | 31 / 27 | 8 / 18 | 2 / 1 | 8 / 8 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 1 | 0 / 0 | 9 / 10 | 100 / 90 | 0 / 0 | 56 / 58 |
| 140-149 | 14 / 18 | 35 / 44 | 4 / 27 | 2 / 3 | 2 / 12 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 4 | 0 / 0 | 11 / 13 | 100 / 80 | 0 / 0 | 44 / 8 |

- Here the opponent is as slow as we are. WHQ does not touch its column until round 130 (from round 10 a pearl lies on all
  five tiles in every round) and the game is level: 9 units against 11 at round 130, total 31 against 27. Then WHQ's dragons reach the
  column, eat 45 natural pearls in 20 rounds and are 18 at round 140; we eat 12. The gap of this game is 20 rounds old at
  round 150.

**forgot against test4 from our side, 1046991** (forgot won on the queen rule, 46 against 25):

Game 1046991, Trauma: A = forgot, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 8 / 8 | 0 / 0 | 0 / 0 | 2 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 90 / 90 |
| 10-19 | 4 / 3 | 8 / 8 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 4 / 3 | 100 / 100 | 0 / 0 | 100 / 100 |
| 20-29 | 4 / 3 | 8 / 9 | 0 / 6 | 0 / 0 | 0 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 4 / 3 | 100 / 100 | 0 / 0 | 100 / 30 |
| 30-39 | 4 / 6 | 8 / 13 | 0 / 5 | 0 / 1 | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 4 / 5 | 100 / 100 | 0 / 0 | 100 / 24 |
| 40-49 | 4 / 8 | 8 / 17 | 1 / 6 | 1 / 1 | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 3 / 8 | 100 / 100 | 0 / 0 | 100 / 24 |
| 50-59 | 3 / 10 | 8 / 22 | 0 / 5 | 0 / 1 | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 3 / 9 | 100 / 100 | 0 / 0 | 100 / 24 |
| 60-69 | 3 / 12 | 8 / 26 | 1 / 7 | 0 / 1 | 1 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 3 / 11 | 100 / 100 | 0 / 0 | 100 / 24 |
| 70-79 | 4 / 15 | 9 / 32 | 5 / 7 | 0 / 1 | 1 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 2 | 0 / 0 | 4 / 13 | 100 / 100 | 0 / 0 | 100 / 24 |
| 80-89 | 5 / 16 | 14 / 36 | 2 / 11 | 0 / 4 | 2 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 5 | 0 / 0 | 5 / 15 | 100 / 100 | 0 / 0 | 100 / 24 |
| 90-99 | 7 / 17 | 16 / 40 | 7 / 6 | 1 / 3 | 3 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 5 / 15 | 100 / 100 | 0 / 0 | 100 / 24 |
| 100-109 | 9 / 20 | 22 / 45 | 8 / 1 | 0 / 2 | 3 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 3 | 0 / 0 | 9 / 17 | 100 / 100 | 0 / 0 | 100 / 98 |
| 110-119 | 12 / 18 | 30 / 42 | 2 / 9 | 0 / 1 | 0 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 9 / 16 | 100 / 100 | 0 / 0 | 100 / 94 |
| 120-129 | 12 / 21 | 32 / 50 | 7 / 8 | 6 / 2 | 5 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 2 | 0 / 0 | 10 / 15 | 94 / 100 | 0 / 0 | 100 / 26 |
| 130-139 | 14 / 23 | 37 / 56 | 5 / 10 | 1 / 6 | 3 / 6 | 1 / 0 | 0 / 1 | 0 / 0 | 1 / 5 | 0 / 0 | 10 / 17 | 89 / 100 | 0 / 0 | 100 / 24 |
| 140-149 | 15 / 23 | 38 / 57 | 5 / 7 | 4 / 12 | 3 / 7 | 2 / 1 | 1 / 2 | 0 / 0 | 2 / 2 | 0 / 0 | 9 / 17 | 95 / 100 | 0 / 0 | 100 / 10 |

- forgot never eats on its fountain column in these 150 rounds (from round 10 a pearl lies on all five tiles in every round;
  test4 eats 57 on its own). It lives on the slow tiles: 43 natural pearls, 3 units at round 50, 9 at round 100, 13 at round 150 against
  test4's 10, 20 and 25. It was as slow as we were against the same opponent and still won: on this map the end game decides
  more than the opening. Over all games forgot does reach the column (62 pearls there against our 27).

### Maze (medium, 48x24; we won 8 of 27)

**Supply.** 1,381 natural pearls per 500 rounds; 49% on 38 fountain tiles, 34 of them narrow corridor cells (two open sides,
20 or fewer cells within four steps).

**All games** (27 of ours): units at round 150: meow 37, test4 48, WHQ 57, forgot 47, SSS 54, Vibing++ 52. Natural pearls in
rounds 0-149: 129 / 156 / 220 / 167 / 189 / 230, of which on fountains of the own half 49 / 44 / 85 / 57 / 86 / 87. Fountains of the
own half eaten from by round 140 (of 19): 9.7 / 12.2 / 18.1 / 12.3 / 15.4 / 15.2. Boxed deaths: 30 / 32 / 53 / 41 / 48 / 68.

**Against WHQ, 1068052** (test build, the same as the live bot on this map; lost on the longest dragon, 66 against 94):

Game 1068052, Maze: A = meow, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 8 / 8 | 0 / 2 | 0 / 0 | 2 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 47 / 47 |
| 10-19 | 4 / 4 | 8 / 10 | 2 / 2 | 0 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 3 | 100 / 100 | 0 / 0 | 63 / 63 |
| 20-29 | 4 / 5 | 10 / 12 | 9 / 10 | 0 / 0 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 4 / 4 | 100 / 100 | 0 / 0 | 77 / 77 |
| 30-39 | 7 / 8 | 17 / 20 | 9 / 11 | 1 / 1 | 4 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 4 / 8 | 100 / 100 | 0 / 0 | 95 / 95 |
| 40-49 | 10 / 13 | 25 / 30 | 7 / 12 | 2 / 1 | 4 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 3 | 0 / 0 | 8 / 9 | 100 / 98 | 0 / 0 | 94 / 91 |
| 50-59 | 13 / 17 | 32 / 37 | 10 / 12 | 1 / 2 | 6 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 1 | 0 / 0 | 9 / 12 | 100 / 95 | 0 / 0 | 92 / 84 |
| 60-69 | 17 / 22 | 39 / 49 | 2 / 13 | 1 / 2 | 2 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 1 | 0 / 0 | 13 / 14 | 98 / 99 | 0 / 0 | 94 / 75 |
| 70-79 | 17 / 27 | 38 / 62 | 7 / 25 | 1 / 3 | 2 / 10 | 0 / 1 | 1 / 0 | 0 / 0 | 1 / 5 | 0 / 0 | 13 / 18 | 95 / 97 | 0 / 0 | 96 / 45 |
| 80-89 | 17 / 31 | 41 / 78 | 6 / 20 | 1 / 6 | 4 / 12 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 5 | 0 / 0 | 13 / 20 | 100 / 96 | 0 / 0 | 96 / 45 |
| 90-99 | 20 / 38 | 46 / 94 | 7 / 7 | 1 / 2 | 5 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 13 / 22 | 100 / 94 | 0 / 0 | 96 / 44 |
| 100-109 | 24 / 42 | 52 / 99 | 11 / 22 | 1 / 7 | 3 / 12 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 9 | 0 / 0 | 14 / 26 | 98 / 91 | 0 / 0 | 94 / 44 |
| 110-119 | 26 / 45 | 62 / 108 | 13 / 25 | 2 / 7 | 5 / 12 | 0 / 2 | 2 / 0 | 0 / 0 | 2 / 6 | 0 / 0 | 18 / 26 | 97 / 95 | 0 / 0 | 78 / 37 |
| 120-129 | 27 / 49 | 68 / 121 | 9 / 10 | 5 / 11 | 8 / 9 | 1 / 0 | 0 / 1 | 0 / 0 | 2 / 7 | 0 / 0 | 17 / 29 | 99 / 98 | 0 / 0 | 81 / 65 |
| 130-139 | 32 / 50 | 75 / 122 | 13 / 23 | 6 / 8 | 11 / 9 | 0 / 0 | 0 / 0 | 0 / 0 | 5 / 7 | 0 / 0 | 20 / 28 | 99 / 97 | 0 / 0 | 81 / 46 |
| 140-149 | 38 / 52 | 84 / 136 | 11 / 26 | 5 / 10 | 4 / 11 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 8 | 0 / 0 | 22 / 29 | 94 / 95 | 0 / 0 | 87 / 45 |

- The gap opens in rounds 60-89: we eat 2, 7 and 6 natural pearls per 10 rounds and WHQ 13, 25 and 20. From round 70 a pearl
  lies on WHQ's fountains in 37-65% of the tile-rounds; on ours in 92-96% until round 110. In 150 rounds we eat 116 natural
  pearls, 42 on the fountains of our half; WHQ 220 and 99.
- `c_out/tiles_1068052.txt` (rounds 0-150): we eat on 8 of our 19 fountain tiles (43 pearls) and WHQ on all 19 of its own (101
  pearls). (15,5) and (16,5) are in view from round 45 and never eaten; (17,8) and (17,9) from round 61, never; six of the
  eight tiles at (29-31,0-3) are in view from round 62-100 and never eaten; (11,1) and (11,2) are seen at round 30 and first
  eaten at round 53. All of them are corridor cells with two open sides and 6-13 cells within four steps. Our dragons do not
  go into them; WHQ's do and lose 5 dragons on its fountain tiles (we none).

**Against test4, 1067906** (same bot; lost on the queen rule):

Game 1067906, Maze: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 8 / 8 | 3 / 2 | 0 / 0 | 2 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 47 / 47 |
| 10-19 | 4 / 5 | 11 / 10 | 9 / 7 | 0 / 0 | 4 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 0 / 0 | 4 / 4 | 100 / 100 | 0 / 0 | 64 / 68 |
| 20-29 | 7 / 7 | 18 / 17 | 7 / 9 | 1 / 0 | 4 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 5 / 4 | 100 / 100 | 0 / 0 | 89 / 89 |
| 30-39 | 10 / 9 | 24 / 24 | 9 / 11 | 1 / 1 | 5 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 8 / 9 | 100 / 100 | 0 / 0 | 96 / 95 |
| 40-49 | 14 / 13 | 32 / 34 | 7 / 12 | 1 / 1 | 3 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 10 / 10 | 100 / 100 | 0 / 0 | 96 / 95 |
| 50-59 | 16 / 18 | 38 / 45 | 7 / 7 | 1 / 1 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 11 / 11 | 100 / 100 | 0 / 0 | 95 / 95 |
| 60-69 | 18 / 20 | 44 / 51 | 6 / 4 | 2 / 1 | 5 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 12 / 13 | 100 / 100 | 0 / 0 | 94 / 96 |
| 70-79 | 22 / 23 | 50 / 54 | 7 / 8 | 1 / 2 | 3 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 3 | 0 / 0 | 15 / 13 | 100 / 100 | 0 / 0 | 94 / 92 |
| 80-89 | 23 / 25 | 54 / 58 | 7 / 8 | 1 / 2 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 14 / 14 | 95 / 97 | 0 / 0 | 96 / 96 |
| 90-99 | 25 / 26 | 60 / 64 | 13 / 11 | 2 / 4 | 7 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 4 | 0 / 0 | 16 / 14 | 91 / 97 | 2 / 0 | 95 / 84 |
| 100-109 | 30 / 28 | 71 / 71 | 13 / 9 | 1 / 4 | 5 / 10 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 5 | 0 / 0 | 19 / 16 | 89 / 95 | 4 / 0 | 92 / 76 |
| 110-119 | 33 / 33 | 81 / 74 | 15 / 10 | 3 / 2 | 8 / 2 | 1 / 0 | 0 / 1 | 0 / 0 | 4 / 1 | 0 / 0 | 22 / 19 | 80 / 91 | 6 / 2 | 84 / 48 |
| 120-129 | 36 / 33 | 88 / 81 | 23 / 13 | 10 / 9 | 14 / 6 | 1 / 2 | 2 / 1 | 0 / 0 | 7 / 2 | 0 / 0 | 21 / 19 | 84 / 91 | 9 / 0 | 84 / 46 |
| 130-139 | 40 / 34 | 97 / 89 | 14 / 16 | 8 / 5 | 13 / 10 | 0 / 1 | 1 / 0 | 0 / 0 | 8 / 5 | 0 / 0 | 25 / 20 | 84 / 97 | 2 / 0 | 89 / 34 |
| 140-149 | 44 / 38 | 100 / 98 | 14 / 13 | 9 / 5 | 5 / 10 | 1 / 0 | 0 / 1 | 0 / 0 | 5 / 5 | 0 / 0 | 29 / 22 | 79 / 97 | 5 / 0 | 85 / 46 |

- Level: 154 natural pearls against 140, 43 units against 42 at round 150. test4 leaves its fountains alone as well until
  round 90 (a pearl lies on them in 92-96% of the tile-rounds from round 30), and from round 90 we eat 28 pearls on test4's
  fountains. The game is lost after round 150.

**forgot against test4 from our side, 1046984** (forgot lost on the queen rule):

Game 1046984, Maze: A = forgot, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 8 / 8 | 3 / 2 | 0 / 0 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 47 / 47 |
| 10-19 | 5 / 5 | 11 / 10 | 5 / 5 | 0 / 0 | 1 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 5 / 5 | 100 / 100 | 0 / 0 | 63 / 63 |
| 20-29 | 6 / 6 | 16 / 15 | 6 / 8 | 0 / 0 | 3 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 4 / 4 | 100 / 100 | 0 / 0 | 89 / 89 |
| 30-39 | 8 / 9 | 20 / 21 | 12 / 13 | 1 / 1 | 5 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 4 / 7 | 100 / 100 | 0 / 0 | 95 / 92 |
| 40-49 | 12 / 12 | 31 / 31 | 7 / 7 | 1 / 1 | 3 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 9 / 11 | 100 / 100 | 0 / 0 | 96 / 95 |
| 50-59 | 14 / 15 | 37 / 37 | 5 / 6 | 1 / 2 | 5 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 9 / 13 | 94 / 100 | 0 / 0 | 95 / 91 |
| 60-69 | 18 / 18 | 41 / 41 | 11 / 8 | 1 / 3 | 4 / 2 | 0 / 1 | 1 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 11 / 14 | 99 / 100 | 0 / 0 | 96 / 100 |
| 70-79 | 20 / 18 | 49 / 48 | 5 / 5 | 1 / 1 | 2 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 11 / 13 | 95 / 100 | 0 / 0 | 96 / 96 |
| 80-89 | 21 / 22 | 53 / 52 | 8 / 6 | 1 / 1 | 5 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 15 / 15 | 96 / 98 | 0 / 0 | 93 / 96 |
| 90-99 | 25 / 24 | 59 / 57 | 14 / 9 | 2 / 3 | 6 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 1 | 0 / 0 | 16 / 13 | 98 / 98 | 0 / 0 | 81 / 93 |
| 100-109 | 28 / 25 | 69 / 67 | 9 / 5 | 1 / 1 | 5 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 3 | 0 / 0 | 17 / 18 | 94 / 96 | 0 / 0 | 80 / 95 |
| 110-119 | 31 / 28 | 75 / 67 | 9 / 10 | 10 / 1 | 9 / 5 | 1 / 1 | 1 / 1 | 0 / 0 | 5 / 1 | 0 / 0 | 22 / 19 | 94 / 98 | 0 / 1 | 84 / 96 |
| 120-129 | 33 / 30 | 76 / 71 | 19 / 15 | 6 / 3 | 10 / 7 | 1 / 2 | 2 / 1 | 0 / 0 | 3 / 3 | 0 / 0 | 18 / 22 | 92 / 99 | 0 / 0 | 74 / 87 |
| 130-139 | 37 / 31 | 87 / 76 | 21 / 17 | 6 / 5 | 12 / 8 | 0 / 0 | 0 / 0 | 0 / 0 | 8 / 3 | 1 / 0 | 20 / 17 | 99 / 96 | 0 / 0 | 52 / 79 |
| 140-149 | 40 / 36 | 95 / 92 | 21 / 17 | 14 / 3 | 11 / 6 | 1 / 0 | 0 / 1 | 0 / 0 | 5 / 3 | 0 / 0 | 17 / 23 | 99 / 97 | 0 / 0 | 43 / 85 |

- The same picture as our game against test4: 155 natural pearls against 133, 40 units against 36 at round 140, 58 pearls on
  the fountains of its half. On this map the difference in the opening is to WHQ, SSS and Vibing++, who go into the corridors
  (18.1, 15.4 and 15.2 of 19 fountains eaten from), not to test4 or forgot (12.2 and 12.3; we 9.7).

### Tower Defense (small, 32x16; we won 0 of 24)

Known (the start room). The map has one fountain tile by my definition (11 pearls per 500 rounds); 78% of its pearls come from
59 slow tiles (5-9 pearls each per 500 rounds), so the last column of the tables means little here.

**All games**: units at round 150: meow 3, test4 37, WHQ 29, forgot 22, SSS 20, Vibing++ 11; natural pearls in rounds 0-149:
5 / 103 / 88 / 84 / 61 / 42; cells visited by round 140: 64 / 331 / 302 / 291 / 244 / 211.

**Against test4, 1067908** (test build, the same as the live bot on this map; wiped out at round 322):

Game 1067908, Tower Defense: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 90 |
| 10-19 | 2 / 2 | 4 / 4 | 1 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 20-29 | 2 / 2 | 5 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 30-39 | 2 / 2 | 5 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 40-49 | 2 / 2 | 5 / 5 | 0 / 3 | 0 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 50-59 | 2 / 3 | 5 / 8 | 0 / 8 | 0 / 0 | 0 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 3 | 100 / 85 | 0 / 0 | 0 / 100 |
| 60-69 | 2 / 7 | 5 / 16 | 1 / 17 | 0 / 0 | 0 / 8 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 6 | 100 / 49 | 0 / 0 | 0 / 100 |
| 70-79 | 2 / 15 | 6 / 33 | 1 / 10 | 0 / 0 | 1 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 12 | 100 / 55 | 0 / 0 | 0 / 100 |
| 80-89 | 3 / 18 | 7 / 43 | 0 / 6 | 0 / 0 | 0 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 16 | 100 / 51 | 0 / 0 | 0 / 100 |
| 90-99 | 3 / 20 | 7 / 49 | 0 / 22 | 0 / 0 | 0 / 8 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 2 | 0 / 0 | 2 / 18 | 100 / 55 | 0 / 0 | 0 / 60 |
| 100-109 | 3 / 26 | 7 / 66 | 0 / 8 | 0 / 2 | 0 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 2 / 21 | 100 / 48 | 0 / 0 | 0 / 100 |
| 110-119 | 3 / 30 | 7 / 74 | 0 / 9 | 0 / 4 | 0 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 4 | 0 / 0 | 3 / 23 | 100 / 48 | 0 / 0 | 0 / 100 |
| 120-129 | 3 / 31 | 7 / 78 | 1 / 6 | 0 / 3 | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 3 / 26 | 100 / 48 | 0 / 0 | 0 / 100 |
| 130-139 | 3 / 33 | 8 / 85 | 1 / 6 | 0 / 4 | 1 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 3 | 0 / 0 | 3 / 23 | 100 / 50 | 0 / 0 | 0 / 100 |
| 140-149 | 4 / 35 | 9 / 88 | 1 / 15 | 0 / 5 | 0 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 5 | 0 / 0 | 4 / 27 | 100 / 50 | 0 / 0 | 0 / 100 |

- Our two dragons stay in the start room (all heads in the own half, two board squares) and eat 6 pearls in 150 rounds.
  test4's dragons leave at round 50-60 (the share of its heads in its own half falls from 100% to 49%), eat 17 pearls in
  rounds 60-69 and are 31 at round 120.

**Against WHQ, 1068054** (same bot; lost on the queen rule at round 500: our queen dead, WHQ's 32 long):

Game 1068054, Tower Defense: A = meow, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 90 |
| 10-19 | 2 / 2 | 4 / 4 | 0 / 0 | 1 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 20-29 | 1 / 2 | 3 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 30-39 | 1 / 2 | 3 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 40-49 | 1 / 2 | 3 / 4 | 0 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 1 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 50-59 | 1 / 1 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |
| 60-69 | 1 / 1 | 3 / 3 | 1 / 0 | 0 / 0 | 1 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |
| 70-79 | 2 / 1 | 4 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |
| 80-89 | 2 / 1 | 4 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |
| 90-99 | 2 / 1 | 4 / 3 | 2 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |
| 100-109 | 2 / 1 | 6 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |
| 110-119 | 2 / 1 | 6 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |
| 120-129 | 2 / 1 | 6 / 3 | 1 / 0 | 0 / 0 | 1 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |
| 130-139 | 3 / 1 | 7 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |
| 140-149 | 3 / 1 | 7 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 1 | 100 / 100 | 0 / 0 | 0 / 100 |

- In this game the opponent is stuck too: WHQ has one dragon from round 50 and eats no natural pearl in 150 rounds; we have
  1-3 dragons and eat 4. Neither side leaves its room before round 150. The start room is not only our problem; but the two
  opponents get out in most games (37 and 29 units at round 150 on average) and we have 3.

**forgot against test4 from our side, 1046992** (forgot won on the longest dragon):

Game 1046992, Tower Defense: A = forgot, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 90 |
| 10-19 | 2 / 2 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 20-29 | 2 / 2 | 4 / 4 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 30-39 | 2 / 2 | 4 / 5 | 0 / 1 | 0 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 40-49 | 2 / 3 | 4 / 6 | 2 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 0 / 100 |
| 50-59 | 2 / 3 | 6 / 7 | 5 / 5 | 0 / 1 | 2 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 2 / 3 | 100 / 100 | 0 / 0 | 0 / 100 |
| 60-69 | 4 / 4 | 11 / 11 | 19 / 0 | 0 / 0 | 5 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 4 / 3 | 61 / 100 | 0 / 0 | 0 / 100 |
| 70-79 | 9 / 4 | 30 / 11 | 19 / 5 | 4 / 2 | 13 / 2 | 1 / 1 | 1 / 1 | 0 / 0 | 5 / 0 | 0 / 0 | 8 / 4 | 51 / 100 | 0 / 0 | 0 / 100 |
| 80-89 | 15 / 4 | 38 / 12 | 12 / 2 | 10 / 2 | 7 / 2 | 1 / 1 | 1 / 1 | 0 / 0 | 3 / 0 | 0 / 0 | 13 / 4 | 47 / 95 | 0 / 0 | 0 / 100 |
| 90-99 | 17 / 4 | 45 / 9 | 10 / 2 | 2 / 3 | 7 / 2 | 0 / 2 | 2 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 13 / 4 | 58 / 89 | 0 / 0 | 0 / 100 |
| 100-109 | 22 / 4 | 52 / 9 | 8 / 1 | 10 / 0 | 5 / 1 | 0 / 1 | 1 / 0 | 0 / 0 | 2 / 0 | 0 / 0 | 17 / 4 | 57 / 100 | 0 / 0 | 0 / 100 |
| 110-119 | 24 / 4 | 63 / 8 | 12 / 1 | 5 / 0 | 7 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 0 | 0 / 0 | 19 / 4 | 51 / 100 | 0 / 0 | 0 / 100 |
| 120-129 | 28 / 4 | 70 / 9 | 5 / 0 | 2 / 0 | 3 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 0 | 0 / 0 | 23 / 4 | 47 / 100 | 0 / 0 | 0 / 100 |
| 130-139 | 29 / 4 | 70 / 9 | 8 / 0 | 3 / 0 | 4 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 4 / 0 | 0 / 0 | 22 / 4 | 47 / 100 | 1 / 0 | 0 / 70 |
| 140-149 | 29 / 4 | 73 / 9 | 9 / 2 | 0 / 0 | 6 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 0 | 0 / 0 | 24 / 4 | 46 / 100 | 0 / 0 | 0 / 90 |

- forgot's two dragons eat their first pearls at round 40-59 and leave at round 60 (heads in the own half: 61% in rounds
  60-69, about half from then on), eat 19, 19, 12 and 10 natural pearls per 10 rounds and are 28 at round 120. test4 is the
  one that stays at 4 units in this game.

### Stripes (small, 24x12; we won 5 of 29)

**Supply.** 459 natural pearls per 500 rounds; 78% on 12 fountain tiles. The two strongest of each half ((11,10) and (12,10) for
side A) lie in a four-cell pocket, (11-12,10-11), closed by kelp. The way in is a portal: a step south from (10,10) comes out
at (11,11) (boards at round 18 of 1067907 and 1068053).

**All games** (29 of ours): units at round 140, or at the last 10-round mark of a shorter game: meow 3, test4 12, WHQ 15, forgot
13, SSS 12, Vibing++ 17. Natural pearls in rounds 0-149: 17 / 54 / 71 / 57 / 68 / 84; per 100 dragon-turns 3.0 / 6.3 / 7.4 / 6.9 / 6.9 /
8.4. With a pearl in view and nobody else as near, our dragons fail to get nearer in 47% of turns (everyone else 26-35%). Of
the pearls that appear within six steps of one of our heads the enemy eats 38% (of theirs we eat 2-10%). Dragons rammed: 3.9 /
1.4 / 0.6 / 4.0 / 3.6 / 2.3; dragons that rammed: 0.8 / 3.8 / 4.3 / 4.4 / 5.2 / 6.3.

**Against test4, 1067907** (test build, the same as the live bot on this map; wiped out at round 140):

Game 1067907, Stripes: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 80 | 0 / 0 | 77 / 77 |
| 10-19 | 2 / 2 | 4 / 4 | 0 / 5 | 0 / 0 | 0 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 2 / 2 | 95 / 54 | 0 / 2 | 82 / 77 |
| 20-29 | 2 / 3 | 4 / 7 | 0 / 4 | 0 / 1 | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 2 / 3 | 10 / 55 | 0 / 2 | 80 / 78 |
| 30-39 | 2 / 5 | 4 / 10 | 2 / 9 | 0 / 0 | 1 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 5 | 0 / 25 | 2 / 7 | 62 / 92 |
| 40-49 | 3 / 7 | 6 / 19 | 1 / 5 | 0 / 2 | 0 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 5 | 0 / 0 | 2 / 7 | 7 / 12 | 0 / 5 | 40 / 93 |
| 50-59 | 3 / 7 | 7 / 16 | 1 / 8 | 3 / 1 | 1 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 3 / 7 | 45 / 36 | 0 / 2 | 77 / 77 |
| 60-69 | 3 / 9 | 8 / 21 | 2 / 5 | 1 / 5 | 2 / 4 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 3 | 0 / 0 | 3 / 9 | 59 / 38 | 0 / 2 | 58 / 63 |
| 70-79 | 4 / 9 | 9 / 22 | 4 / 12 | 0 / 2 | 2 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 4 | 0 / 0 | 4 / 9 | 50 / 35 | 0 / 6 | 65 / 65 |
| 80-89 | 6 / 12 | 13 / 28 | 0 / 7 | 1 / 4 | 0 / 4 | 1 / 0 | 0 / 1 | 0 / 0 | 1 / 3 | 0 / 0 | 6 / 12 | 49 / 21 | 0 / 5 | 50 / 75 |
| 90-99 | 4 / 12 | 9 / 31 | 0 / 5 | 1 / 4 | 0 / 5 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 2 | 0 / 0 | 4 / 12 | 48 / 17 | 0 / 5 | 55 / 100 |
| 100-109 | 3 / 14 | 7 / 34 | 0 / 7 | 1 / 5 | 0 / 5 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 2 | 0 / 0 | 3 / 14 | 31 / 34 | 0 / 1 | 70 / 70 |
| 110-119 | 2 / 16 | 6 / 39 | 0 / 9 | 0 / 4 | 1 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 3 | 0 / 0 | 2 / 15 | 21 / 35 | 0 / 3 | 87 / 60 |
| 120-129 | 3 / 18 | 6 / 46 | 0 / 6 | 2 / 5 | 0 / 3 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 2 | 0 / 0 | 3 / 15 | 0 / 41 | 0 / 3 | 83 / 82 |
| 130-139 | 2 / 18 | 6 / 48 | 0 / 10 | 1 / 7 | 1 / 8 | 2 / 0 | 0 / 2 | 0 / 0 | 1 / 4 | 0 / 0 | 1 / 16 | 0 / 43 | 0 / 4 | 65 / 65 |

- We eat nothing for 30 rounds. Our queen `#1` walks east along row 10 and is at (9,10) at round 7 with the two pocket pearls
  in view two cells away behind the kelp. She turns south, wanders over (9,11), (10,11), (10,0), (9,1) for ten rounds, and
  stands on the door cell (10,10) at round 18. A test4 2-long (`#5`) is at (13,0) then, two cells from the pocket across the
  wrap. She steps north and walks round the outside of the pocket for the next 15 rounds without going in. (Inference: the
  enemy head near the pocket. Not the queen's portal ban: on a map of 288 cells our bot's queen rules are off, `is_queen()`
  needs more than 600 cells or a closed home, and in the next game she goes through.) Our other dragon `#3` wanders in rows
  6-8, where there are no fountains. test4's two dragons eat their first pearls at rounds 11 and 12 (one of them is its queen,
  through the portal of its own pocket) and are five by round 30.
- From there it is a ram fight between 2-3 dragons of ours and 7-18 of theirs.

**Against WHQ, 1068053** (same bot; wiped out at round 176):

Game 1068053, Stripes: A = meow, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 100 | 0 / 0 | 90 / 90 |
| 10-19 | 2 / 2 | 4 / 4 | 0 / 4 | 0 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 95 / 77 | 0 / 0 | 100 / 85 |
| 20-29 | 2 / 3 | 4 / 8 | 2 / 7 | 1 / 1 | 1 / 4 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 2 | 0 / 0 | 2 / 3 | 50 / 73 | 0 / 0 | 93 / 57 |
| 30-39 | 2 / 4 | 5 / 9 | 0 / 4 | 0 / 1 | 0 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 2 / 4 | 50 / 67 | 0 / 0 | 100 / 63 |
| 40-49 | 2 / 5 | 5 / 12 | 0 / 4 | 0 / 1 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 2 / 4 | 50 / 51 | 0 / 1 | 100 / 63 |
| 50-59 | 2 / 5 | 5 / 15 | 0 / 10 | 0 / 4 | 0 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 2 | 0 / 0 | 2 / 5 | 50 / 40 | 0 / 4 | 63 / 68 |
| 60-69 | 2 / 9 | 5 / 25 | 1 / 13 | 0 / 4 | 0 / 11 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 6 | 0 / 0 | 2 / 9 | 5 / 44 | 1 / 5 | 62 / 47 |
| 70-79 | 2 / 14 | 6 / 29 | 1 / 10 | 0 / 7 | 1 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 5 | 0 / 2 | 2 / 12 | 0 / 32 | 1 / 4 | 55 / 47 |
| 80-89 | 3 / 13 | 7 / 31 | 1 / 9 | 0 / 5 | 1 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 7 | 0 / 0 | 3 / 11 | 0 / 34 | 0 / 6 | 60 / 75 |
| 90-99 | 4 / 10 | 8 / 28 | 2 / 8 | 0 / 7 | 1 / 9 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 5 | 0 / 0 | 4 / 10 | 10 / 46 | 2 / 4 | 52 / 72 |
| 100-109 | 5 / 14 | 10 / 33 | 1 / 7 | 1 / 6 | 0 / 4 | 3 / 0 | 0 / 3 | 0 / 0 | 0 / 2 | 0 / 0 | 4 / 13 | 27 / 49 | 0 / 4 | 62 / 73 |
| 110-119 | 2 / 13 | 6 / 33 | 1 / 9 | 1 / 10 | 2 / 8 | 2 / 0 | 0 / 2 | 0 / 0 | 0 / 3 | 0 / 0 | 2 / 13 | 74 / 57 | 0 / 2 | 58 / 67 |
| 120-129 | 2 / 16 | 4 / 40 | 1 / 11 | 2 / 9 | 1 / 8 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 7 | 0 / 1 | 2 / 16 | 36 / 58 | 0 / 6 | 82 / 58 |
| 130-139 | 2 / 15 | 5 / 40 | 4 / 8 | 2 / 8 | 2 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 4 | 0 / 0 | 2 / 14 | 45 / 41 | 0 / 4 | 33 / 67 |
| 140-149 | 2 / 18 | 7 / 47 | 0 / 10 | 0 / 2 | 1 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 6 | 0 / 0 | 2 / 17 | 31 / 46 | 0 / 0 | 67 / 60 |

- The same first 18 rounds, move for move. This time no enemy head is near at round 18: the queen steps south through the
  portal, eats (12,10) at round 20 and (11,10) at round 21, and splits at round 22. In that round WHQ's `#4` (L2) steps through
  the same portal from the other side, from (10,11), and rams her: our queen is dead at round 22. We eat 14 natural pearls in
  150 rounds, 8 of them on our fountains; WHQ 114, of which 54 on its own fountains and 40 on ours; 7 of ours are rammed and
  we ram nobody.

**forgot against test4 from our side, 1046977** (forgot wiped test4 out at round 91):

Game 1046977, Stripes: A = forgot, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 2 / 2 | 4 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 2 | 100 / 80 | 0 / 0 | 80 / 80 |
| 10-19 | 2 / 2 | 4 / 4 | 3 / 5 | 0 / 0 | 1 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 1 | 0 / 0 | 2 / 2 | 63 / 54 | 0 / 2 | 63 / 77 |
| 20-29 | 3 / 3 | 7 / 7 | 1 / 5 | 0 / 0 | 0 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 3 | 37 / 38 | 0 / 2 | 73 / 83 |
| 30-39 | 3 / 5 | 8 / 12 | 6 / 1 | 1 / 0 | 4 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 2 | 0 / 0 | 2 / 5 | 44 / 43 | 2 / 0 | 58 / 90 |
| 40-49 | 6 / 4 | 13 / 8 | 7 / 0 | 3 / 0 | 4 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 1 | 0 / 0 | 5 / 4 | 42 / 44 | 2 / 0 | 60 / 78 |
| 50-59 | 7 / 3 | 17 / 6 | 5 / 2 | 2 / 1 | 3 / 1 | 0 / 1 | 1 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 6 / 3 | 19 / 32 | 3 / 2 | 73 / 78 |
| 60-69 | 8 / 2 | 20 / 5 | 4 / 4 | 1 / 2 | 3 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 8 / 2 | 29 / 0 | 2 / 4 | 58 / 75 |
| 70-79 | 10 / 2 | 23 / 9 | 11 / 0 | 5 / 0 | 6 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 1 | 0 / 0 | 10 / 2 | 48 / 25 | 4 / 0 | 47 / 67 |
| 80-89 | 13 / 3 | 31 / 7 | 9 / 0 | 6 / 0 | 7 / 0 | 1 / 1 | 1 / 1 | 0 / 0 | 4 / 0 | 0 / 0 | 13 / 3 | 44 / 4 | 4 / 0 | 53 / 67 |
| 90-99 | 14 / 1 | 33 / 3 | 2 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 0 / 1 | 0 / 0 | 0 / 0 | 0 / 0 | 13 / 1 | 57 / 0 | 1 / 0 | 67 / 83 |

- forgot's queen starts on the same cell as ours, (2,10), and walks the same row. She is on the door cell (10,10) at round
  8, goes through, eats (12,10) at round 10 and (11,10) at round 11, splits at round 12, leaves through the portal at round 13
  and is back inside for the next pearl at round 19. Our queen is at the door ten rounds later (round 18) and eats at rounds
  20-21 or not at all. In 90 rounds forgot eats 29 natural pearls on the fountains of its half and 18 on test4's, makes 2 rams
  and has 13 units when test4 has none.

### Portals (small, 32x16; we won 6 of 27)

**Supply.** 1,262 natural pearls per 500 rounds; 96% on 56 fountain tiles: 2x2 blocks closed by kelp and entered through a
portal, and one corridor one cell wide with four of the richest tiles of the map ((15,1), (15,3), (15,5), (15,7) for side A,
32-52 pearls per 500 rounds each). The two teams never meet: there is no ram between the teams in rounds 0-149 in any of our
27 games (`c_agg.py`) and none in 500 rounds in the three games read; by my path map no fountain of one half can be reached
from the other spawn (`c_out/tiles_1063682.txt`). This map is the economy and the end game with nothing in between.

**All games** (27 of ours): units at round 150: meow 19, test4 33, WHQ 25, forgot 37, SSS 30, Vibing++ 23. Natural pearls in
rounds 0-149: 187 / 207 / 140 / 225 / 136 / 110. Natural pearls per 100 dragon-turns: 9.2 / 6.4 / 6.1 / 6.6 / 6.1 / 5.1, ours the highest.
Boxed deaths: 120 / 108 / 42 / 108 / 55 / 40; segments lost in them 307 / 264 / 99 / 255 / 134 / 94. Splits: 141 / 142 / 71 / 156 / 83 / 62.
So for every 100 new dragons we lose 85 boxed, test4 76, WHQ 59, forgot 69, SSS 66 and Vibing++ 65; and we lose a dragon for
every 1.6 natural pearls, test4 for every 1.9, forgot 2.1, SSS 2.5, Vibing++ 2.8, WHQ 3.3. Where the deaths are
(`c_out/deadcells.txt`, 12 games a team): ours on 32 different cells a game, 74% on a cell where a team-mate had died before;
forgot's 110 on 60 cells, 46% on such a cell; 39% of ours come within a round of eating on that cell (forgot 22%, our
opponents 23%).
How the games end (`c_endstate.py`): our 21 losses are 14 on the longest dragon and 7 on the queen rule. At round 300 our total
length is below the opponent's in 20 of the 21; at the end the totals are level (50 against 52) and theirs is in one dragon:
longest 30 against 42, units 5.3 against 2.6, our queen dead in every one.

**Against test4, 1063682** (queen-hunt test build, which changes nothing on a map where the teams never meet; lost on the longest dragon, 16 against 33):

Game 1063682, Portals: A = meow, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 3 / 3 | 9 / 9 | 5 / 5 | 1 / 0 | 2 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 0 | 0 / 0 | 3 / 3 | 100 / 100 | 0 / 0 | 40 / 42 |
| 10-19 | 3 / 5 | 9 / 14 | 8 / 6 | 3 / 1 | 6 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 2 | 0 / 0 | 3 / 5 | 100 / 100 | 0 / 0 | 84 / 83 |
| 20-29 | 6 / 6 | 13 / 16 | 8 / 9 | 4 / 2 | 3 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 2 | 0 / 0 | 5 / 5 | 100 / 100 | 0 / 0 | 68 / 81 |
| 30-39 | 6 / 9 | 19 / 23 | 8 / 11 | 3 / 2 | 5 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 2 | 0 / 0 | 6 / 7 | 100 / 100 | 0 / 0 | 76 / 76 |
| 40-49 | 8 / 14 | 24 / 32 | 10 / 8 | 3 / 3 | 6 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 5 / 3 | 0 / 0 | 7 / 12 | 100 / 100 | 0 / 0 | 72 / 68 |
| 50-59 | 9 / 15 | 26 / 36 | 13 / 15 | 6 / 4 | 9 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 6 / 6 | 0 / 0 | 8 / 14 | 100 / 100 | 0 / 0 | 66 / 71 |
| 60-69 | 12 / 16 | 31 / 41 | 15 / 21 | 3 / 4 | 7 / 9 | 0 / 0 | 0 / 0 | 0 / 0 | 4 / 2 | 0 / 0 | 11 / 14 | 100 / 100 | 0 / 0 | 64 / 48 |
| 70-79 | 15 / 23 | 38 / 59 | 20 / 14 | 17 / 7 | 13 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 8 / 7 | 0 / 0 | 14 / 22 | 100 / 100 | 0 / 0 | 56 / 60 |
| 80-89 | 20 / 23 | 54 / 61 | 15 / 16 | 16 / 15 | 12 / 16 | 0 / 0 | 0 / 0 | 2 / 0 | 12 / 9 | 0 / 0 | 18 / 20 | 100 / 100 | 0 / 0 | 41 / 49 |
| 90-99 | 18 / 30 | 51 / 68 | 21 / 22 | 23 / 22 | 17 / 16 | 0 / 0 | 0 / 0 | 0 / 0 | 16 / 16 | 0 / 0 | 17 / 26 | 100 / 100 | 0 / 0 | 24 / 41 |
| 100-109 | 19 / 30 | 52 / 72 | 16 / 15 | 20 / 22 | 15 / 12 | 0 / 0 | 0 / 0 | 0 / 4 | 11 / 13 | 0 / 0 | 15 / 25 | 100 / 100 | 0 / 0 | 45 / 34 |
| 110-119 | 23 / 25 | 58 / 67 | 14 / 19 | 27 / 14 | 15 / 15 | 0 / 0 | 0 / 0 | 0 / 0 | 17 / 11 | 0 / 0 | 19 / 24 | 100 / 100 | 0 / 0 | 37 / 41 |
| 120-129 | 21 / 29 | 48 / 74 | 11 / 16 | 22 / 20 | 10 / 13 | 0 / 0 | 0 / 0 | 0 / 0 | 14 / 10 | 0 / 0 | 17 / 20 | 100 / 100 | 0 / 0 | 42 / 42 |
| 130-139 | 17 / 32 | 43 / 85 | 14 / 20 | 18 / 20 | 10 / 20 | 0 / 0 | 0 / 0 | 2 / 2 | 11 / 15 | 0 / 3 | 15 / 28 | 100 / 100 | 0 / 0 | 56 / 38 |
| 140-149 | 14 / 32 | 40 / 81 | 14 / 18 | 18 / 20 | 13 / 17 | 0 / 0 | 0 / 0 | 0 / 0 | 8 / 12 | 0 / 0 | 13 / 29 | 100 / 100 | 0 / 0 | 55 / 34 |

- We eat nearly as much as test4 and have half its units. In 150 rounds we eat 192 natural and 184 corpse pearls and test4
  215 and 156; we make 143 new dragons and lose 123 boxed and 4 in head-ons between team-mates; test4 makes 153 and loses 110
  and 6. 14 units against 32 at round 140. Our dragons die 2-3 long on a few cells ((16,7) 14 times, (22,10) 12, (27,5) 10,
  (19,12) 10 in 150 rounds); (16,7) is the one-cell nook at the bottom of the rich corridor at x=15 (board at round 60: our
  `#57`, L2, has its head in the nook and its tail on (15,7), and no way out). 101 of our 144 splits are 4 -> 2+2. test4 here
  is the one that sheds (77 of its 155 splits are by dragons of 5-7 that keep their front two segments), the reverse of
  Slithery Fight.
- Why the same pearls cost us more dragons than they cost test4 or forgot on this map I did not find out. It is not that we
  take pearls in dead-end cells more readily: a free pearl on a next cell that has no other exit is eaten in 61% of turns by
  us and in 60% by our opponents on small maps (`c_out/adj_1119_small.txt`).

**Against WHQ, 1063251** (live bot; lost on the longest dragon, 9 against 37):

Game 1063251, Portals: A = meow, B = WeHaveQuizzes. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 3 / 3 | 9 / 9 | 7 / 6 | 0 / 0 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 0 / 0 | 3 / 3 | 100 / 100 | 0 / 0 | 50 / 50 |
| 10-19 | 5 / 6 | 14 / 15 | 12 / 7 | 2 / 3 | 7 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 4 | 0 / 0 | 5 / 5 | 100 / 100 | 0 / 0 | 68 / 80 |
| 20-29 | 9 / 6 | 21 / 16 | 14 / 9 | 5 / 1 | 6 / 3 | 0 / 0 | 0 / 0 | 0 / 2 | 6 / 0 | 0 / 0 | 7 / 6 | 100 / 100 | 0 / 0 | 66 / 85 |
| 30-39 | 9 / 7 | 25 / 20 | 9 / 5 | 11 / 1 | 10 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 7 / 2 | 0 / 0 | 9 / 6 | 100 / 100 | 0 / 0 | 68 / 91 |
| 40-49 | 12 / 8 | 29 / 22 | 13 / 9 | 6 / 2 | 5 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 5 / 1 | 0 / 0 | 11 / 7 | 100 / 100 | 0 / 0 | 69 / 85 |
| 50-59 | 12 / 12 | 35 / 31 | 13 / 11 | 14 / 4 | 11 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 12 / 2 | 0 / 0 | 12 / 11 | 100 / 100 | 0 / 0 | 59 / 82 |
| 60-69 | 11 / 15 | 32 / 38 | 17 / 11 | 16 / 5 | 14 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 8 / 4 | 0 / 0 | 9 / 13 | 100 / 100 | 0 / 0 | 52 / 69 |
| 70-79 | 17 / 16 | 45 / 40 | 14 / 8 | 11 / 2 | 10 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 11 / 1 | 1 / 0 | 17 / 14 | 100 / 100 | 0 / 0 | 40 / 85 |
| 80-89 | 15 / 19 | 41 / 46 | 14 / 7 | 17 / 4 | 13 / 5 | 0 / 0 | 0 / 0 | 2 / 0 | 12 / 3 | 0 / 0 | 15 / 16 | 100 / 100 | 0 / 0 | 51 / 85 |
| 90-99 | 14 / 21 | 39 / 49 | 16 / 13 | 16 / 5 | 11 / 5 | 0 / 0 | 0 / 0 | 0 / 2 | 9 / 5 | 0 / 0 | 13 / 20 | 100 / 100 | 0 / 0 | 46 / 79 |
| 100-109 | 16 / 19 | 43 / 48 | 13 / 12 | 18 / 7 | 14 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 12 / 6 | 0 / 0 | 13 / 16 | 100 / 100 | 0 / 0 | 35 / 73 |
| 110-119 | 18 / 20 | 45 / 49 | 17 / 5 | 16 / 3 | 12 / 3 | 0 / 0 | 0 / 0 | 4 / 0 | 12 / 2 | 0 / 0 | 16 / 17 | 100 / 100 | 0 / 0 | 34 / 88 |
| 120-129 | 14 / 21 | 41 / 53 | 18 / 11 | 21 / 3 | 15 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 11 / 1 | 1 / 1 | 11 / 18 | 100 / 100 | 0 / 0 | 42 / 77 |
| 130-139 | 17 / 23 | 49 / 58 | 10 / 10 | 18 / 9 | 11 / 7 | 0 / 0 | 0 / 0 | 0 / 2 | 11 / 4 | 0 / 0 | 16 / 21 | 100 / 100 | 0 / 0 | 45 / 82 |
| 140-149 | 17 / 24 | 47 / 59 | 16 / 11 | 18 / 8 | 14 / 7 | 0 / 0 | 0 / 0 | 0 / 0 | 12 / 9 | 0 / 0 | 16 / 18 | 100 / 100 | 0 / 0 | 39 / 83 |

- We eat half as much again as WHQ (203 natural pearls against 135, 189 corpse pearls against 57) and end the 150 rounds with
  fewer dragons (17 against 24 at round 140): 156 new dragons and 132 boxed deaths for us, 70 and 44 for WHQ. WHQ grows by
  not dying.

**forgot against test4 from our side, 1046982** (forgot lost on the queen rule):

Game 1046982, Portals: A = forgot, B = test4. Every cell is A / B.

| rounds | units | total length | natural eaten | corpse eaten | splits | rammed | rammers | head-on with a team-mate | boxed | other non-ram | board squares | heads in own half % | eaten on enemy-half fountains | own-half fountains with a pearl lying % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-9 | 3 / 3 | 9 / 9 | 3 / 6 | 0 / 0 | 1 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 0 | 0 / 0 | 3 / 3 | 100 / 100 | 0 / 0 | 45 / 42 |
| 10-19 | 3 / 5 | 9 / 15 | 4 / 6 | 0 / 0 | 3 / 3 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 3 / 4 | 100 / 100 | 0 / 0 | 90 / 79 |
| 20-29 | 5 / 7 | 11 / 19 | 13 / 6 | 0 / 3 | 6 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 3 | 0 / 0 | 4 / 7 | 100 / 100 | 0 / 0 | 78 / 84 |
| 30-39 | 10 / 8 | 22 / 21 | 14 / 9 | 2 / 2 | 5 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 2 | 0 / 0 | 9 / 7 | 100 / 100 | 0 / 0 | 71 / 84 |
| 40-49 | 12 / 12 | 30 / 27 | 15 / 11 | 6 / 3 | 7 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 5 / 3 | 0 / 0 | 10 / 11 | 100 / 100 | 0 / 0 | 56 / 76 |
| 50-59 | 14 / 15 | 39 / 35 | 22 / 7 | 11 / 7 | 17 / 5 | 0 / 0 | 0 / 0 | 2 / 0 | 7 / 5 | 0 / 0 | 11 / 14 | 100 / 100 | 0 / 0 | 53 / 76 |
| 60-69 | 22 / 15 | 51 / 37 | 19 / 22 | 8 / 3 | 11 / 11 | 0 / 0 | 0 / 0 | 0 / 0 | 6 / 2 | 0 / 0 | 16 / 14 | 100 / 100 | 0 / 0 | 50 / 55 |
| 70-79 | 27 / 24 | 65 / 57 | 19 / 12 | 13 / 5 | 14 / 6 | 0 / 0 | 0 / 0 | 0 / 0 | 11 / 4 | 0 / 0 | 21 / 20 | 100 / 100 | 0 / 0 | 40 / 53 |
| 80-89 | 30 / 26 | 73 / 65 | 20 / 22 | 11 / 9 | 12 / 12 | 0 / 0 | 0 / 0 | 2 / 0 | 7 / 7 | 1 / 0 | 21 / 23 | 100 / 100 | 0 / 0 | 59 / 54 |
| 90-99 | 32 / 31 | 78 / 79 | 17 / 19 | 13 / 13 | 11 / 12 | 0 / 0 | 0 / 0 | 2 / 0 | 8 / 10 | 0 / 0 | 24 / 24 | 100 / 100 | 0 / 0 | 53 / 37 |
| 100-109 | 33 / 33 | 80 / 85 | 23 / 22 | 18 / 17 | 16 / 17 | 0 / 0 | 0 / 0 | 0 / 0 | 12 / 13 | 0 / 0 | 24 / 26 | 100 / 100 | 0 / 0 | 50 / 31 |
| 110-119 | 37 / 37 | 90 / 88 | 9 / 17 | 16 / 20 | 10 / 10 | 0 / 0 | 0 / 0 | 2 / 0 | 10 / 15 | 0 / 0 | 26 / 28 | 100 / 100 | 0 / 0 | 43 / 44 |
| 120-129 | 35 / 32 | 88 / 92 | 19 / 14 | 16 / 20 | 14 / 16 | 0 / 0 | 0 / 0 | 0 / 0 | 10 / 13 | 0 / 1 | 24 / 25 | 100 / 100 | 0 / 0 | 56 / 26 |
| 130-139 | 39 / 34 | 99 / 93 | 19 / 17 | 23 / 20 | 17 / 14 | 0 / 0 | 0 / 0 | 6 / 0 | 15 / 16 | 0 / 0 | 28 / 27 | 100 / 100 | 0 / 0 | 39 / 40 |
| 140-149 | 35 / 32 | 90 / 89 | 10 / 17 | 22 / 21 | 13 / 19 | 0 / 0 | 0 / 0 | 2 / 0 | 10 / 14 | 0 / 0 | 24 / 26 | 100 / 100 | 0 / 0 | 52 / 34 |

- forgot eats 226 natural and 159 corpse pearls, makes 157 new dragons and loses 107 boxed: 22 units at round 60 against
  test4's 15 and 35 against 32 at round 140. With the same number of new dragons as we make in 1063251 it loses 25 fewer.

### weakhold (small, 40x15; we won 10 of 27)

Not a problem in the opening: units at round 150: meow 21, test4 9, WHQ 21, forgot 16, SSS 18, Vibing++ 22; natural pearls in
rounds 0-149: 94 / 36 / 98 / 59 / 71 / 131. We lose this map to WHQ later (3 wins in 11); it is also the one map where a loss often
comes with the larger total length at round 300 (8 of 17 losses, `c_endstate.py`).

## Answers to the eight questions

All-games counts are over our games against 2000+ teams with Schooltime left out (large maps: 111 games; medium: 117; small: 173)
and over the games of the three top teams against 2000+ teams (all of them for the `c_agg.py` tables, a spread sample of 50-80
per team for the scripts that walk whole replays; each output file names its sample). "Our opponents" in a table means test4 and
WHQ in their games against us, unless it says "all opponents in our games".

### a. Where does the first gap open?

**It depends on the map; on the large maps it opens at the first contact, not before.** All large-map games, means per game
(`c_agg.py`, `c_out/agg_large_*.txt`):

| rounds | units at round 50 / 100 / 150, meow / test4 / WHQ | natural pearls eaten | dragon-turns | natural pearls per 100 dragon-turns | turns with an enemy head in view, meow |
|---|---|---|---|---|---|
| 0-49 | 29.2 / 33.1 / 33.3 | 71.7 / 76.3 / 80.7 | 995 / 1,060 / 1,070 | 6.6 / 7.0 / 7.2 | 12% |
| 50-99 | 42.7 / 55.9 / 52.7 | 90.9 / 124.7 / 121.8 | 1,902 / 2,345 / 2,255 | 4.7 / 5.4 / 5.3 | 26% |
| 100-149 | 47.0 / 62.3 / 59.4 | 79.0 / 129.4 / 132.9 | 2,315 / 3,079 / 2,880 | 3.3 / 4.2 / 4.6 | 34% |

In rounds 0-49 we eat 6-11% less; in rounds 50-99, when a quarter of our turns have an enemy head in view, 25-27% less; in rounds
100-149 about 40% less. In the games read the first ram between the two teams is at round 52-90 on Australia, 18-27 on Around
UNSW, 20-32 on Islands and 33-42 on Slithery Fight. The table pools the builds; the 99 live games have 42.4 units at round
100 and 46.4 at round 150, the 12 games of the trade-on-contact test build 45.2 and 51.6 (`c_out/bybatch_large.txt`).

**When the unit ratio falls below 0.8 for good** (own units / enemy units below 0.8 from that round to the end of the game;
`c_gap.py`, `c_out/gap_1119.txt`, all 401 games):

| map size | games | rounds 0-49 | 50-99 | 100-149 | 150-199 | 200-299 | 300+ | never |
|---|---|---|---|---|---|---|---|---|
| large | 111 | 5 | 22 | 7 | 7 | 3 | 18 | 49 |
| medium | 117 | 30 | 9 | 4 | 4 | 3 | 11 | 56 |
| small | 173 | 53 | 15 | 2 | 0 | 1 | 9 | 93 |

By map, large: Australia 13 of 28 in rounds 50-99; Islands 4 before round 50, 9 in 50-99, 7 in 100-149, 5 in 150-199; Around UNSW
and Slithery Fight never before round 150 (0 of 53 games), although we win only 11 of those 53: there the units are level (median
ratio 0.94-0.97 at round 150 and 200) and the total length is not (median ratio 0.61 and 0.78 at round 150). By opponent on large
maps: against test4 16 of 42 games are lost in units in rounds 50-99; against WHQ 29 of 44 never, and we win 2 of the 44: the
median total-length ratio against WHQ goes 0.95, 0.78, 0.64, 0.52, 0.45 at rounds 50, 100, 150, 200, 300. Medium and small:
Trauma against test4 (10 of 11 before round 50), Stripes (20 of 29), Tower Defense (14 of 24) and Queen Of Spades (14 of 28,
a map I did not read) are behind before round 50, which is before any ram; on the three I read the fountains are behind a
portal or outside the start room.

**The games read** (`c_qa.py`, `c_out/qa_table.md`; "first ram" = the first ram between the two teams; "the 20 rounds before" are
the two 10-round blocks before the round in which the units, or if they never do, the total length, fall behind for good; a
round after 350 has no block data. "Never" means the ratio was 0.8 or more at the end of the game, which also happens when
the opponent feeds one dragon in the end game and its total shrinks: 1063016 has total length 150 against 333 at round 150
and is "never" behind for good. The run and build of each game are in the table of games read):

| game | map | opponent | result | heads first in view | first ram | units behind for good from | total length behind for good from | the 20 rounds before: units, own / enemy | natural eaten | corpse eaten | splits | own dragons rammed, ramming, boxed, other | enemy dragons rammed, ramming, boxed, other |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1058144 | Australia | test4 | loss | r22 | r68 | r85 | r78 | r60-79: 21 / 28 | 22 / 38 | 2 / 14 | 11 / 23 | 1, 0, 1, 0 | 0, 1, 13, 1 |
| 1067904 | Australia | test4 | loss | r22 | r73 | never | r125 | r100-119: 37 / 47 | 18 / 37 | 12 / 28 | 13 / 25 | 7, 1, 0, 1 | 1, 7, 12, 0 |
| 1068050 | Australia | WHQ | loss | r27 | r52 | never | r249 | r220-239: 51 / 62 | 19 / 43 | 28 / 22 | 16 / 11 | 2, 4, 8, 2 | 4, 2, 1, 0 |
| 1021860 | Australia | ComTamSuonNuon | win | r11 | r90 | never | never | - | - | - | - | - | - |
| 1063012 | Islands | test4 | loss | r3 | r32 | r115 | r112 | r90-109: 41 / 44 | 28 / 37 | 14 / 28 | 12 / 25 | 9, 0, 4, 1 | 0, 9, 7, 0 |
| 1067905 | Islands | test4 | loss | r3 | r20 | r102 | r98 | r80-99: 35 / 36 | 20 / 35 | 24 / 22 | 18 / 22 | 5, 4, 5, 3 | 4, 5, 4, 0 |
| 1068051 | Islands | WHQ | loss | r3 | r26 | never | r213 | r190-209: 53 / 44 | 19 / 37 | 24 / 54 | 17 / 32 | 12, 3, 10, 1 | 3, 12, 7, 0 |
| 1063671 | Islands | test4 | loss | r3 | r20 | r73 | r69 | r50-69: 25 / 28 | 35 / 33 | 14 / 29 | 24 / 19 | 7, 3, 5, 5 | 3, 7, 3, 0 |
| 1063016 | Around UNSW | test4 | loss | r15 | r18 | never | never | - | - | - | - | - | - |
| 1068055 | Around UNSW | WHQ | loss | r21 | r24 | never | r170 | r150-169: 60 / 63 | 17 / 49 | 10 / 45 | 16 / 21 | 7, 2, 8, 0 | 2, 7, 13, 1 |
| 1067909 | Around UNSW | test4 | loss | r17 | r23 | r406 | r392 | - | - | - | - | - | - |
| 1063675 | Around UNSW | test4 | win | r18 | r27 | r486 | r83 | - | - | - | - | - | - |
| 1063252 | Slithery Fight | WHQ | loss | r0 | r42 | never | r497 | - | - | - | - | - | - |
| 1067917 | Slithery Fight | test4 | loss | r0 | r35 | r407 | r400 | - | - | - | - | - | - |
| 1068063 | Slithery Fight | WHQ | loss | r0 | r33 | never | r432 | - | - | - | - | - | - |
| 1063024 | Slithery Fight | test4 | win | r0 | r33 | r406 | r58 | - | - | - | - | - | - |
| 1067915 | Trauma | test4 | loss | r60 | r159 | r30 | r22 | r10-29: 4 / 3 | 0 / 7 | 0 / 0 | 0 / 4 | 0, 0, 0, 0 | 0, 0, 1, 0 |
| 1068061 | Trauma | WHQ | loss | r24 | r154 | r140 | r143 | r120-139: 9 / 11 | 15 / 18 | 3 / 3 | 9 / 10 | 0, 0, 4, 0 | 0, 0, 3, 0 |
| 1063774 | Trauma | WHQ | win | r4 | r200 | never | r382 | - | - | - | - | - | - |
| 1067906 | Maze | test4 | loss | r32 | r112 | never | never | - | - | - | - | - | - |
| 1068052 | Maze | WHQ | loss | r3 | r78 | never | never | - | - | - | - | - | - |
| 1063672 | Maze | test4 | win | r19 | r106 | never | never | - | - | - | - | - | - |
| 1067908 | Tower Defense | test4 | loss | r93 | r176 | r45 | r44 | r20-39: 2 / 2 | 0 / 0 | 0 / 0 | 0 / 0 | 0, 0, 0, 0 | 0, 0, 0, 0 |
| 1068054 | Tower Defense | WHQ | loss | after r150 | r324 | never | never | - | - | - | - | - | - |
| 1067907 | Stripes | test4 | loss | r4 | r60 | r16 | r13 | r0-19: 2 / 2 | 0 / 5 | 0 / 0 | 0 / 2 | 0, 0, 0, 0 | 0, 0, 1, 0 |
| 1068053 | Stripes | WHQ | loss | r10 | r22 | r26 | r13 | r0-19: 2 / 2 | 0 / 4 | 0 / 0 | 0 / 1 | 0, 0, 0, 0 | 0, 0, 0, 0 |
| 1059076 | Stripes | WHQ | win | r3 | r76 | never | never | - | - | - | - | - | - |
| 1063682 | Portals | test4 | loss | r0 | none | never | never | - | - | - | - | - | - |
| 1063251 | Portals | WHQ | loss | r0 | none | never | never | - | - | - | - | - | - |
| 1067916 | Portals | test4 | win | r0 | none | never | never | - | - | - | - | - | - |

Reading. In the five Australia and Islands games against test4 the fall is at round 73-125. In the 20 rounds before it test4
eats 1.7-2.1 times our natural pearls in three of the five (22 against 38, 18 against 37, 20 against 35) and more corpse pearls
in four; in the three Islands games 9-10 of our dragons die in rams in those 20 rounds (rammed or ramming). In the three large-map games
of the test build against WHQ the units never fall behind for good and the total length does at round 170-249, in 20 rounds in
which WHQ eats 2-3 times our natural pearls (17 against 49, 19 against 37, 19 against 43) and in two of the three rams 7 and 12
of our dragons. On Trauma against test4, Tower Defense and Stripes it comes before any ram, in rounds in which we eat nothing.
A unit ratio "for good" that falls after round 390 (Around UNSW, Slithery Fight) is the end game, not the economy: on those
maps look at the total length.

**Does the gap decide the game?** Large maps, games that reached round 300 (`c_endstate.py`, `c_out/endstate_<team>.txt`):

| | meow | forgot | SSS | Vibing++ |
|---|---|---|---|---|
| games that reached round 300 | 109 | 158 | 139 | 127 |
| own total length below the opponent's at round 300 | 108 | 82 | 48 | 40 |
| wins among those | 11 = 10% | 29 = 35% | 24 = 50% | 16 = 40% |
| level or ahead at round 300 | 1 | 76 | 91 | 87 |
| wins among those | 1 | 52 = 68% | 68 = 75% | 61 = 70% |

We are behind in all 97 losses and in 11 of our 12 wins; all 12 wins are on the longest dragon. On medium maps we are behind at
round 300 in 66 of 84 games and win 11 of them (17%), and win 14 of the 18 others; on small maps 55 of 75, 6 wins (11%), and
8 of the 20 others (most small-map games end by wipe-out before round 300). The gap of this file is there in nearly every
game; what it costs depends on the end game, where the top three recover a third to a half of the games in which they are
behind and we a tenth.

### b. With the same pearls on offer, why do we eat fewer?

First what it is not. **Our dragons are not slower when left alone.** A natural pearl that appears within 6 steps of one of our
heads with no enemy head within 6 steps is eaten after 3.8 rounds in rounds 0-49, 2.6 in 50-99 and 2.7 in 100-149; test4's
dragons need 3.4, 3.0, 3.2 and WHQ's 3.4, 3.1, 2.9; forgot 2.9, 2.6, 2.6; SSS 3.0, 2.6, 2.7; Vibing++ 2.4, 2.0, 1.9
(`c_agg.py`). With a pearl in view and nobody else as near, our dragons eat or end nearer in 64-67% of turns, test4's in 66-69%,
WHQ's in 66-69%. **And we do not lose more dragons in dead ends**: boxed deaths in rounds 0-149 on large maps are 82 for us, 78
for test4, 85 for WHQ, 95 for forgot, 67 for SSS and 103 for Vibing++.

**Where the pearls are lost** (large maps, rounds 50-149, pearls per game; `c_out/agg_large_50_99.txt` and `_100_149.txt`):

| income | meow | test4 against us | WHQ against us | gap to the two | share of the gap |
|---|---|---|---|---|---|
| natural, on fountains of the enemy's half | 34 | 76 | 76 | -42 | 33% |
| corpse pearls of own dragons | 89 | 117 | 118 | -29 | 22% |
| natural, on fountains of the own half | 106 | 128 | 128 | -22 | 17% |
| natural, on other tiles | 30 | 51 | 51 | -21 | 16% |
| corpse pearls of enemy dragons | 15 | 31 | 29 | -15 | 12% |
| all pearls | 274 | 402 | 402 | -128 | |
| segments lost (all deaths and paid steps) | 222 | 259 | 263 | we lose 39 fewer | |

Close to half of the gap (the fountains of the enemy's half and the enemy's corpses, 45%) is made in the other half or at the
border. The corpse pearls of own dragons (22%) follow partly from the opponents having more to recycle (they lose 259-263
segments, we 222) and partly from who gets to a corpse first (point 2 below). The causes the brief lists, ranked, with their
counts:

1. **Dragons standing off from enemy heads (the largest).** Large maps, rounds 0-300 (`c_avoid.py`, `c_out/avoid_*_large*.txt`): a
   meeting (a turn of a dragon of 4 or shorter that begins with an enemy head of 4 or shorter on the next cell) happens 69.7
   times a game to us. Over all our games we ram in 12% (18% when shorter than the enemy, 13% at the same length, 5% when
   longer) and step away in 88%. By build: the live bot (99 games, 6,994 meetings) rams in 10% (14 / 11 / 5); the
   trade-on-contact test build (12 games, 739 meetings) in 31% (49 / 36 / 7). Our opponents in the same games ram in 36%
   (62 / 33 / 22), forgot in 37% (63 / 36 / 26), SSS in 42% (86 / 41 / 24), Vibing++ in 36% (56 / 37 / 25). In the ten rounds after
   one of ours steps away it eats 0.33 pearls and the enemy it left eats 0.70; 20% of them are rammed in those ten rounds all
   the same (an opponent that steps away from the live bot: 8%; from the test build: 18%). With an enemy head in view (not next
   to it) our dragons end the turn farther from it in 34-37% of turns and nearer in 12-13%; everyone else 22-29% and 15-22%
   (`c_agg.py`).
   *Charges.* A meeting is not where most rams come from. Of the 22.9 rams a game that our opponents make in rounds 0-149, 41%
   are made from the next cell and 59% with a move of two or more steps; forgot 58% and 42% (of 20.8), SSS 45% and 55% (of
   18.6), Vibing++ 43% and 57% (of 22.6) (`c_ramsteps.py`, `c_out/ramsteps_large.txt`, from the head-on records of every game).
   The live bot makes 5.1 rams a game in those rounds, 81% from the next cell: 1.0 charge a game against 13.7 for our
   opponents and 8.7-12.9 for the top three. The test build makes 13.8 rams, 3.9 of them charges. Our bot can charge
   (`ram_path()` searches up to four steps for a marked target); what it lacks is targets: an enemy head is marked only when
   the dragon sees at least as many other own heads as enemy heads, the team has 8 units and the target is long enough
   (`mark_trade_targets()`).
   *Consequences that can be counted:* 76% of our heads are in our own half in rounds 50-99 (the others 68-72%); 58% of all rams in our games happen in
   our half (top three 47-48%, `c_front.py`); natural pearls that appear with only an enemy head within 8 steps outnumber those
   with only one of ours 17,097 to 13,282 in rounds 0-99, 20,464 to 9,621 in rounds 100-199 and 51,326 to 18,982 after round
   200 (`c_contest.py`, 111 games; for forgot the two numbers are 47,666 and 52,173 over the whole game, for SSS 47,635 and
   44,619).
2. **The pearls of the dead go to the other side.** Large maps, whole game (`c_rams.py`, `c_ramlocal.py`): 20.8 rams made and 65.1
   suffered per game; segments lost in them 296 for us and 332 for the enemy; pearls of those corpses eaten: we 109, the enemy
   255. Counted pearl by pearl (39,590 pearls of 9,540 rams): we eat 28%, the enemy 67%, 5% lie for 20 rounds. By the number
   of other heads within 8 steps of the ram: three or more enemy heads more than ours (28% of the rams): we eat 7%; one or two
   more (25%): 15%; the same number (14%): 26%; one or two more of ours (18%): 45%; three or more (15%): 67%. forgot, SSS and
   Vibing++ in the same five classes: 16-19%, 30-32%, 47-49%, 67-69%, 81-83%, and 47-50% overall. With the top three's
   shares in each class and our own mix of classes we would eat 44-45%: being outnumbered more often explains 3-5 points of
   our 20-point shortfall, and what our dragons do with the same numbers around them explains the rest. By build
   (`c_rambatch.py`, `c_out/rambatch_1119_large.txt`): the live bot eats 27% (82 rams a game, 22% of them started by us; 47%
   of the pearls of the rams we start and 19% of the others), the test build 33% (116 rams a game, 37% started by us; 52%
   and 21%). Starting more rams raises the share because the starter eats more; it does not change what happens to the
   pearls of the rams the enemy starts, and those are still two rams in three. With a ram-corpse
   pearl at the same distance from one of our heads and an enemy head we get it in 35% of cases, forgot in 47%, SSS in 52%
   (`c_contest.py`). Rule in our bot (inference from the source): a pearl is a target only if we reach it strictly before any
   enemy head, or, for dragons of 4 or shorter, within one step of the enemy's distance; and cells next to a small enemy head
   carry a penalty of 225-450 against 520-820 for a pearl. The team's own log (`plan.md`) found the same against one opponent
   (34% of ram pearls against calc) and a relaxed corpse rule changed nothing in local games.
3. **Fewer dragons.** 19% fewer dragon-turns than test4 in rounds 50-99 and 25% fewer in 100-149. It is a result of 1 and 2
   and of the next point, and then a cause: per 100 dragon-turns we eat 86-88% of what they eat in rounds 50-99 and 73-79% in
   100-149, so in rounds 50-99 about two thirds of the natural-pearl gap is the number of dragons and one third the rate; in
   100-149 half and half.
4. **Fewer new dragons per pearl, on one map by a form of our own.** Large maps, rounds 0-99, per game (`c_midall.py`): splits by
   a dragon of exactly 4 (the split that makes a new 2-long forager and keeps the parent): meow 56, all opponents in our games
   85, forgot 107, SSS 75, Vibing++ 81. Splits in which a dragon of 5 or more keeps only its front two segments and leaves the
   rest ("shed"; the front part is in a dead end and dies): meow 39, opponents 22, forgot 9, SSS 16, Vibing++ 27. We eat 4.1
   pearls for every split at 4, our opponents about 3.3, forgot 2.8. By map the shed excess is Slithery Fight alone (125 sheds
   a game against 56 for our opponents; 65 splits at 4 against 120); on Australia, Islands and Around UNSW our sheds are 1, 7
   and 17 a game against 8, 3 and 17, and the fewer splits at 4 there (32, 67, 58 against 60, 78, 81) follow the fewer
   pearls. On medium and small maps there is no difference in sheds (5 against 5-6 a game). Rule in our bot behind the
   Slithery Fight form: no split while "harvesting" a dead end.
5. **Dragons kept back by a rule.** (i) After round 150 on large maps (300 on the others) a pearl within 9 cells of the leader
   is not to be eaten by other dragons: answer f. (ii) Pearls behind a portal: on Stripes the two best fountains of each half
   are in a pocket whose door is a portal. forgot's queen, from the same start cell as ours, is through the door at round 8
   and eats at rounds 10 and 11; ours is next to the door at round 7, goes through at round 18 in one of the two games read
   and not at all in the other (per-map notes). I first read this as the queen's portal ban; that is wrong, the ban is off on
   maps of 600 cells or fewer. Which rule holds her back I could not determine. (iii) Narrow places: on Maze we have eaten from 9.7 of
   the 19 fountains of our half by round 140 and WHQ from 18.1 of its 19; over all large maps we have eaten from 62% of the
   fountain tiles of our half by round 150, our opponents from 80% of theirs, the top three from 69% (`c_tilesall.py`).
6. **Dragons lost by a step they could have not taken.** Non-ram deaths with a free cell next to the head, rounds 0-149, large
   maps: 6.4 per game for us (15 segments), 2.2 for our opponents; 6.3 of ours are steps through a portal onto a body on the
   far side (4.3 onto a team-mate, 2.0 onto an enemy). On Islands it is 18.4 per game (`c_freedeaths.py`).
7. **Idle dragons.** Dragons that have not eaten for 20 rounds: 19 of 41 at round 90 (47%) and 25 of 46 at round 140 (54%); test4
   20 of 52 (39%) and 31 of 62 (49%); WHQ 20 of 50 and 25 of 59 (39%, 42%). A smaller difference than I expected; the per-map
   notes have two examples (the camper on Islands, the queen on Stripes).
8. **Dragons in each other's way: no.** We crowd less than anyone: an own second head within 2 steps of an eaten pearl 14 times
   per game in rounds 50-99 against 27-35 for everybody else, and 81% of our heads have an own head within 6 steps against
   80-89%.
9. **Each dragon slower to the pearl: no** (see the top of this answer), until round 150; after it, yes (answer f).

### c. Spread

**Our children leave the parent as far as anybody's; what we do not do is enter the other half.** Large maps, rounds 0-149, all
games (`c_agg.py`): path distance between parent and child five rounds after a split: meow 6.2, test4 6.1, WHQ 6.4, forgot 6.1,
SSS 5.7, Vibing++ 5.9; after ten rounds 8.0, 8.7, 8.5, 8.8, 7.9, 8.1. Share of the child's steps in its first ten rounds that
go onto cells no own head had visited: 21%, 21%, 20%, 20%, 18%, 18%; of the parent's: 21%, 22%, 20%, 20%, 19%, 18%. I see no
rule in any team that sends the child "away" or towards unvisited cells: the child's head is the old tail, so its first steps go
back along the parent's trail in every team, and four of five steps of both parent and child are on cells the team has
visited. (A2's 6.4-7.3 against 4.0-5.3 on Australia was forgot against Vibing++ in one game; over all games forgot and Vibing++
are 6.1 and 5.9.)

The difference is at team level. Cells visited by round 90 and 140: meow 752 and 1,123; test4 895 and 1,400; WHQ 787 and 1,242;
forgot 908 and 1,369; SSS 821 and 1,223; Vibing++ 677 and 1,072. Squares of the 8x8 grid with an own head at round 90:
22.9 / 28.6 / 26.4 / 26.3 / 24.7 / 20.5. Own heads in the own half in rounds 50-99: 76% / 68% / 71% / 71% / 72% / 69%. Natural
pearls eaten on fountains of the enemy's half in rounds 0-149: 50 / 99 / 99 / 81 / 85 / 86 (`c_out/agg_large_0_149.txt`). On
Around UNSW the difference is the whole gap (27 against 109-122 pearls from the other half). Vibing++
spreads least of the top three and has the fewest units at round 100 (42), as A found.

How the others get there: by not turning back when an enemy head is near (answer b, point 1), not by a different split. The
trade-on-contact test build did not get there: 76% of its heads are in the own half in rounds 0-149 against the live bot's
78%, and it eats 57 natural pearls on the enemy's fountains against 49 (`c_out/bybatch_large.txt`). Ramming at a meeting is
one thing; walking towards an enemy head is another, and the test build changed only the first.

### d. Dead ends and pockets

**The top teams lose as many small dragons this way as we do or more; nobody avoids the cell where a team-mate died.**
Boxed deaths in rounds 0-150, about 12 games per team and map (`c_deadcells.py`, `c_out/deadcells.txt`):

| map | meow | our opponents | forgot | SSS | Vibing++ | share of boxed deaths on a cell where a team-mate had died before, same order |
|---|---|---|---|---|---|---|
| Australia | 14 | 40 | 32 | 40 | 42 | 53% / 61% / 57% / 73% / 68% |
| Islands | 20 | 28 | 41 | 50 | 32 | 52% / 43% / 41% / 58% / 46% |
| Around UNSW | 45 | 54 | 88 | 92 | 87 | 57% / 40% / 60% / 66% / 51% |
| Slithery Fight | 243 | 207 | 262 | 88 | 288 | 81% / 68% / 72% / 45% / 74% |
| Trauma | 16 | 31 | 29 | 29 | 35 | 67% / 59% / 60% / 73% / 67% |
| Maze | 32 | 53 | 41 | 45 | 67 | 58% / 55% / 51% / 67% / 60% |
| weakhold | 37 | 41 | 20 | 26 | 74 | 77% / 71% / 35% / 71% / 74% |
| Tower Defense | 0.5 | 13 | 17 | 6 | 11 | 0% / 9% / 14% / 17% / 25% |
| Stripes | 3 | 24 | 16 | 18 | 31 | 26% / 70% / 50% / 69% / 71% |
| Portals | 123 | 43 | 110 | 54 | 42 | 74% / 50% / 46% / 58% / 56% |

We have fewer than our opponents on eight of the ten maps (not on Slithery Fight and Portals), mostly because we have fewer
dragons or do not go in. The one team with a visibly lower number where it matters is SSS on Slithery Fight: 88 against
207-288, 45% on repeat cells against 68-81%, 9.6 deaths on its most used cell against 17-28. In the game read (1051824) 99
of SSS's 170 splits are at length 4 and 37 at length 5, and only 24 are by dragons of 6-8 that keep their front two segments
(ours in 1067917: 236). Whether SSS also remembers the cell I cannot tell.
What is particular to us is the form on Slithery Fight: 125 sheds a game in rounds 0-99 there against 56 for our opponents,
so most of our 243 boxed deaths on that map are the 2-long front parts of sheds (answer b, point 4). On Portals, where we
have the most boxed deaths of the five (123), the form is the ordinary one: 2-3-longs dying on fountain cells.

### e. Contact

**When an enemy small dragon arrives, ours give way and theirs do not.** The counts are in answer b, points 1 and 2. In one place
(Around UNSW, 1067909, the test build, the centre at rounds 22-30): four of ours and three of test4's die; one of ours rams a
5-long with a two-step move, two are rammed within a round of eating a pearl, by test4 dragons that charge three steps over
pearls to reach them, and one dies boxed by its own child, whose own steps then lead west, away from the pearls. test4's
survivors split on the 25 or so pearls still lying there. From round 30 on 85% of our heads are in our half.

Price of a ram not made (large maps, rounds 0-300, `c_avoid.py`): after stepping away our dragon eats 0.33 pearls in ten rounds
and the enemy it left 0.70, a swing of 0.37 pearls, and it is rammed anyway in 20% of cases (a top-three dragon that steps away:
22-26%; an opponent of ours that steps away from us: 9%). Price of a ram made: one dragon each; the pearls of both corpses go
61% to us when we start it at a meeting (2,423 pearls; live bot 59%, test build 65%) and 74% to the enemy when they do (5,107
pearls); for forgot, SSS and Vibing++ the rammer's team gets 68-70%. At equal lengths a ram is therefore worth about one pearl
to the side that starts it, and with the shorter dragon more; our dragons take it 13% of the time at equal length and 18% when
shorter (live bot 11% and 14%, test build 36% and 49%), the top three 36-41% and 56-86%.
Ground: in rounds 50-149 our opponents eat 76 natural pearls on the fountains of our half and we 34 on theirs.

Our rule (source): a dragon of 4 or shorter may ram only when there are at least as many own other heads in its view as enemy
heads (`TRADE_LOCAL_EDGE`), the team has 8 units, and, on maps over 1,200 cells and below the unit cap, the target shows at least
max(5, own length + 2) segments. A lone 2-long facing a lone 2-long therefore never rams on any map, and on a large map the
live bot rams no 2-4-long. The test build drops the third condition (a target of the own length is enough) and keeps the
other two.

**The test build on the ladder, game by game** (`c_pairs.py`, `c_out/pairs_large.md`). The run of the test build and a run of
the live bot 80 minutes earlier each played test4 and WHQ once on every large map, from the same side:

| map | opponent | game | bot | units r100 / r150 / r300, own:opp | total length r150 / r300, own:opp | natural pearls r0-149, own:opp | rams made:suffered r0-149 | meetings rammed r0-149 | result |
|---|---|---|---|---|---|---|---|---|---|
| Around UNSW | WHQ | 1063244 | live | 50:63 / 60:60 / 54:54 | 155:246 / 195:315 | 236:371 | 11:19 | 10 of 48 | loss, longest |
| Around UNSW | WHQ | 1068055 | test build | 51:61 / 60:63 / 54:59 | 204:218 / 214:320 | 295:329 | 20:28 | 14 of 38 | loss, longest |
| Around UNSW | test4 | 1063016 | live | 39:62 / 61:64 / 56:64 | 150:333 / 242:460 | 190:403 | 6:12 | 2 of 13 | loss, longest |
| Around UNSW | test4 | 1067909 | test build | 45:62 / 60:64 / 60:64 | 156:273 / 253:312 | 215:382 | 14:14 | 10 of 26 | loss, queen rule |
| Australia | WHQ | 1063239 | live | 36:44 / 51:54 / 23:60 | 128:148 / 60:336 | 133:226 | 4:16 | 2 of 46 | loss, longest |
| Australia | WHQ | 1068050 | test build | 57:33 / 60:33 / 54:45 | 207:84 / 184:245 | 223:154 | 20:8 | 15 of 38 | loss, queen rule |
| Australia | test4 | 1063011 | live | 31:50 / 27:64 / 9:64 | 63:232 / 33:495 | 77:293 | 3:17 | 1 of 13 | loss, queen rule |
| Australia | test4 | 1067904 | test build | 37:47 / 47:61 / 47:62 | 107:161 / 120:313 | 131:235 | 8:15 | 5 of 15 | loss, queen rule |
| Islands | WHQ | 1063240 | live | 43:60 / 47:61 / 11:62 | 108:189 / 28:315 | 223:252 | 6:32 | 6 of 84 | loss, wipe-out r449 |
| Islands | WHQ | 1068051 | test build | 60:28 / 60:39 / 32:51 | 170:91 / 101:209 | 281:180 | 22:29 | 11 of 40 | loss, longest |
| Islands | test4 | 1063012 | live | 44:46 / 26:62 / 5:63 | 66:188 / 11:409 | 195:259 | 6:49 | 3 of 56 | loss, longest |
| Islands | test4 | 1067905 | test build | 36:45 / 41:63 / 9:62 | 102:171 / 35:336 | 227:252 | 21:32 | 6 of 26 | loss, longest |
| Slithery Fight | WHQ | 1063252 | live | 46:63 / 61:63 / 54:55 | 176:200 / 174:256 | 456:447 | 2:17 | 1 of 26 | loss, longest |
| Slithery Fight | WHQ | 1068063 | test build | 50:63 / 56:61 / 55:58 | 143:260 / 167:273 | 347:569 | 16:16 | 15 of 46 | loss, longest |
| Slithery Fight | test4 | 1063024 | live | 34:63 / 48:63 / 44:62 | 134:203 / 144:279 | 381:428 | 2:23 | 1 of 32 | win, longest |
| Slithery Fight | test4 | 1067917 | test build | 40:64 / 42:63 / 52:64 | 113:228 / 163:294 | 393:441 | 6:19 | 4 of 22 | loss, queen rule |

Over all its 12 large-map games against the live bot's 99 (`c_bybatch.py`, `c_out/bybatch_large.txt`; four of the 12 are
against "dev test 1"):

| means per game | live bot (99) | test build (12) | their opponents (live / test build games) |
|---|---|---|---|
| meetings in rounds 0-149, share rammed | 35.3, 9% | 27.4, 31% | 26.6, 34% / 27.4, 33% |
| rams made : suffered, rounds 0-149 | 5.1 : 22.9 | 13.8 : 22.5 | |
| pearls of ram corpses eaten, rounds 0-149 | 28 | 47 | 65 / 71 |
| natural pearls eaten, rounds 0-149 | 239 | 262 | 336 / 335 |
| of them on fountains of the other half | 49 | 57 | 99 / 96 |
| own heads in the own half, rounds 0-149 | 78% | 76% | |
| units at round 100 / 150 / 200 / 300 | 42 / 46 / 41 / 35 | 45 / 52 / 48 / 42 | 54 / 61 / 62 / 62 and 51 / 58 / 61 / 59 |
| total length at round 150 / 300 | 121 / 118 | 143 / 147 | 212 / 331 and 191 / 291 |
| games won | 12 | 0 | |

Reading. The rule did what it says (31% of meetings end in a ram, the opponents' rate) and nothing else changed in the
code. It is worth about 5 units and 20 segments at round 150 and 7 units and 30 segments at round 300 on average, nearly all
of it on Australia and Islands (the eight pairs above: total length at round 150 goes from 128, 63, 108, 66 to 207, 107, 170,
102 there; on Around UNSW from 155 and 150 to 204 and 156; on Slithery Fight from 176 and 134 down to 143 and 113). It does
not move the border, it does not make the opponents eat less, and it wins nothing. That last count is weak evidence either
way: 0 of 12 against 12 of 99 is what chance gives one time in five when the true rate is the same, and all 12 wins of the
live bot are longest-dragon wins (11 of them from behind in total length at round 300), 6 on Around UNSW, 5 on Slithery Fight
and 1 on Australia, which is to say they are end-game wins and mostly on the two maps where trading on contact gains least.

### f. The round-150 switch on large maps

**Three things change at round 150, and each can be counted.**

1. *Small dragons stop eating pearls next to them.* A dragon of 2-4 that is not its team's longest, with a pearl on a free cell
   next to its head, a way out behind the pearl, no enemy head within two steps of the pearl and no team-mate next to it
   (`c_adj.py`, `c_zone2.py`; 111 games):

| eats it, % of such turns | rounds 0-99 | 100-149 | 150-199 | 200-299 | 300-399 | 400+ |
|---|---|---|---|---|---|---|
| meow | 81 | 82 | 61 | 59 | 59 | 56 |
| meow, pearl within 9 cells of our longest dragon (5+) | 83 | 81 | 44 | 41 | 42 | 39 |
| meow, pearl within 9 cells of another own dragon of 5+ | 85 | 80 | 56 | 56 | 58 | 56 |
| meow, no own dragon of 5+ within 9 cells | 80 | 82 | 67 | 66 | 65 | 62 |
| all opponents in our games | 81 | 85 | 85 | 84 | 81 | 78 |
| all opponents, pearl within 9 cells of their longest dragon | 80 | 85 | 84 | 83 | 75 | 73 |

   forgot is at 89-91% in every phase, SSS at 70-80%, Vibing++ at 83-89% until round 300. On medium and small maps, where our
   switch is at round 300, our rate is 84-85% in rounds 150-299 and 53% and 63% after round 300 (opponents 74% and 77%). That
   is 235 such turns a game in rounds 150-299 on large maps and about 94 pearls not taken at once; half of them we eat later,
   a tenth the enemy eats, four tenths still lie there ten rounds later. Rule (source):
   after `grow_round` a pearl within 9 cells of the leader the dragon knows of carries a penalty of 600 and no eating bonus
   for anyone but the leader. The table fits it: the drop is at round 150 exactly and is deepest near the longest dragon; that
   it is also there with no long dragon near may be a leader position the dragon remembers (inference).
2. *Splitting stops.* Ordinary splits per game in rounds 150-199 (`c_midall.py`): meow 15, all opponents in our games 24, forgot 59,
   SSS 33, Vibing++ 53; in rounds 100-149 ours were 32. Our dragons of 5 and more make 0.1 ordinary splits per game in rounds
   150-199 (forgot 14.5, Vibing++ 3.1, our opponents 6.5).
3. *The dragons of 5 and more become prey.* Per game, rounds 150-299: 3.4-3.6 dragons of 5-9 and 0.3-1.4 of 10+ alive at a
   time; they move two or more steps in 61-71% of their turns, eat 5.8-8.8 natural pearls per 100 dragon-rounds, shed their
   front two segments 42 times (once per 15 rounds per dragon), and are rammed 4.3 times (34 segments). Per dragon-round our
   5-9-longs are rammed about 5 times as often as those of our opponents in rounds 150-199 (1.3 a game of 3.4 alive against
   0.9 of 12.3; theirs are safe because we do not ram), 1.5-1.8 times as often as forgot's and Vibing++'s, and as often as
   SSS's.

**The switch is the same in both builds.** It is the same code, and the counts agree: the eating rate of the first table falls
from 82% in rounds 50-149 to 59% in rounds 150-299 in the live bot's 99 games and from 83% to 62% in the test build's 12
(`c_out/adj_1119_large_notc.txt`, `c_out/adj_1119_large_tc.txt`). The live bot's units go 46, 41, 35 at rounds 150, 200, 300
and the test build's 52, 48, 42, while their opponents stay at 58-62 (`c_out/bybatch_large.txt`). In the two games the test
build had won by round 150 (1068050 and 1068051, 60 units against 33 and 39) the total length is behind by round 249 and 213.

**What the 2-longs do after the switch.** Natural pearls per 100 dragon-rounds, large maps (`c_midall.py`):

| | r50-99 | r100-149 | r150-199 | r200-249 | r250-299 |
|---|---|---|---|---|---|
| meow, 2-long | 3.0 | 2.0 | 1.25 | 1.3 | 1.4 |
| all opponents in our games, 2-long | 4.0 | 2.9 | 2.5 | 2.3 | 2.3 |
| forgot / SSS / Vibing++, 2-long (r50-99, r150-199, r250-299) | 4.7 / 3.4 / 5.1 | | 2.8 / 2.8 / 3.3 | | 2.5 / 2.5 / 2.9 |
| meow, 3-4-long | 6.7 | 4.2 | 2.5 | 2.8 | 3.1 |
| all opponents, 3-4-long | 7.3 | 4.9 | 4.2 | 4.0 | 4.1 |
| meow, dragons alive: 2 / 3-4 / 5-9 / 10+ | 23 / 13 / 1 / 0 | 27 / 17 / 2 / 0 | 24 / 16 / 3 / 0.3 | 21 / 13 / 4 / 1 | 20 / 12 / 4 / 1 |
| all opponents, dragons alive | 26 / 17 / 2 / 0 | 27 / 24 / 6 / 1 | 22 / 24 / 12 / 3 | 20 / 22 / 16 / 5 | 19 / 19 / 16 / 8 |

**One game, 1068051 (Islands against WHQ), rounds 140-220, dragon by dragon:** in the per-map notes. In short: of 28 dragons of 5 or
more, 9 are rammed by 2-4-longs, 8 shed in a dead end, and the rest roam the whole board at two steps a turn eating 0-9
pearls each in 80 rounds; the fountains they left are eaten from less (a pearl lies on 42-69% of our fountain tile-rounds
after round 150 against 22-40% before).

**The top teams' 5-9-longs in rounds 150-300.** forgot has 3.5-4.2 of them at a time and they split in the ordinary way 11-14
times per 50 rounds (ours 0); SSS has 6.2-6.9, which shed 21-22 times per 50 rounds and are rammed 2.3-2.6 times; Vibing++
4.3-6.4, 23 sheds. All three keep 25-31 dragons of length 2 and 20-24 of length 3-4 through round 300 (we 20-24 and 12-16). The
opponents in our games hold 12-16 dragons of 5-9 and 3-8 of 10+ from round 150; against the top three test4 and WHQ have
6-11 and 0.5-3.5 (`c_out/midall_*_vs19_87.txt`).

**Why the natural intake halves:** fewer dragons (units 47 at round 150, 42 at 200, 36 at 300 over all 111 games), each small one eating
half as much (1.25-1.4 against 2.3-2.5 for 2-longs), of which the declined pearls are the countable part, and the border moving
further into our half (natural pearls appearing with only an enemy head within 8 steps: 2.1 times those with only ours in rounds
100-199, 2.7 times after round 200).

### g. test4 and WeHaveQuizzes against the top three

Against the top three the two are ordinary (large maps, 21 games of test4 and 4 of WHQ, `c_agg.py` and `c_rams.py`): test4 has
52 units at round 100 and 60 at round 150 (forgot 52 and 58, SSS 54 and 58), eats 285 natural pearls in rounds 0-149 (forgot 322,
SSS 315, Vibing++ 305) and gains nothing from rams (swing -3 segments per game; against us +68; WHQ -9 and +148). What they do
that the top three do not, or less:

- **test4 has few boxed deaths in the first 50 rounds** (13-14 per game; forgot 21, Vibing++ 20, SSS 12, we 18).
- **WHQ sprints.** Moves of two or more steps in rounds 50-99: WHQ 40 against us and 87 against the top three, test4 25 and 9,
  forgot 10, SSS 43, Vibing++ 38, we 3. WHQ pays 6 segments per 50 rounds for it, we none before round 150.
- **Both eat on the other half's fountains from the start** (23 pearls in rounds 0-49 against us; forgot 23, SSS 20, Vibing++ 22;
  we 16), and against us they take 1.4-1.6 times as much there as against the top three in rounds 50-149 (76 against 47-56).
- **Both charge, as the top three do.** Rams made with a move of two or more steps in rounds 0-149: 13.7 a game against us and
  12.4 against the top three (forgot 8.7, SSS 10.2, Vibing++ 12.9; `c_ramsteps.py`). The difference between their games
  against us and against the top three is not what they do but what comes back: the top three make 19-23 rams a game in
  those rounds (over all their opponents), the live bot 5.
- **WHQ consolidates early and by suicide orders**, like forgot: 30-62 non-ram deaths with a free cell per 50 rounds from round 250
  in the two games read to round 350, and one dragon of 70-138 at the end of our large-map losses. test4 mostly keeps 50-64
  units to the end.
- What the top three do that the two do not: forgot splits its 5-9-longs (answer f); SSS and Vibing++ ram the queen at any
  length (A's and A2's finding). I found nothing in the opening that only the top three do.

### h. One rule for the opening, one for the mid-game

In the section "What I would change".

## Us against the top three and against our opponents

Large maps and means per game unless a row says otherwise. meow = our 111 large-map games against 2000+ teams (Schooltime left
out), all builds; where the live bot (99 games) and the trade-on-contact test build (12 games) differ, both are in the cell.
"Our opponents" = test4 / WHQ in their games against us (42 and 44 large-map games); "(all)" = every opponent in those 111
games, for the scripts that pool the other side of our games. forgot, SSS, Vibing++ = their own games against 2000+ teams.
Sources: `c_agg.py` (rows 1-4, 6, 12, 21-26, 30-32), `c_tilesall.py` (5), `c_adj.py` (7, 8), `c_contest.py` (9), `c_avoid.py` (10, 11),
`c_ramsteps.py` (13), `c_rams.py` (14, 18), `c_ramlocal.py` and `c_rambatch.py` (15, 16), `c_front.py` (17), `c_midall.py` (19, 20,
27-29), `c_endstate.py` (33, 34), `c_bybatch.py` (the build split of rows 1, 14, 17).

| # | behaviour | meow | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| 1 | Units at round 100 / 150 | 43 / 47 (live 42 / 46, test build 45 / 52) | 56 / 62 and 53 / 59 | 52 / 58 | 54 / 58 | 42 / 50 |
| 2 | Natural pearls eaten, rounds 0-49 / 50-99 / 100-149 | 72 / 91 / 79 | 76 / 125 / 129 and 81 / 122 / 133 | 84 / 121 / 117 | 75 / 118 / 122 | 71 / 113 / 121 |
| 3 | Of those, on fountains of the enemy's half, rounds 50-149 | 34 | 76 and 76 | 58 | 65 | 65 |
| 4 | Own heads standing in the own half, rounds 50-99 | 76% | 68% and 71% | 71% | 72% | 69% |
| 5 | Fountain tiles of the own half eaten from by round 150 | 62% | 80% (all) | 69% | 69% | 69% |
| 6 | Undisturbed pearl within 6 steps: rounds until eaten, rounds 50-99 | 2.6 | 3.0 and 3.1 | 2.6 | 2.6 | 2.0 |
| 7 | Free pearl on the next cell is eaten (dragon of 2-4, a way out behind it, nobody near), rounds 0-149 | 80-82% | 78-84% (all) | 89-91% | 70-78% | 83-87% |
| 8 | The same in rounds 150-299 | 60% (live 59%, test build 62%) | 85% (all) | 91% | 80% | 89% |
| 9 | Natural pearl at the same distance from an own and an enemy head: own team eats it | 35% | 57% (all) | 46% | 48% | 50% |
| 10 | Meeting (enemy head on the next cell, both 4 or shorter): rams it | no: 12% (live 10%, test build 31%) | yes: 36% (all) | yes: 37% | yes: 42% | yes: 36% |
| 11 | The same when shorter than the enemy / of the same length | 18% / 13% (live 14% / 11%, test build 49% / 36%) | 62% / 33% (all) | 63% / 36% | 86% / 41% | 56% / 37% |
| 12 | Enemy head in view: ends the turn farther from it, rounds 50-99 | 34% | 25% and 25% | 22% | 28% | 27% |
| 13 | Rams made by charging (a move of two or more steps that ends in the enemy head), rounds 0-149 | no: 1.0 (test build 3.9) | yes: 13.7 (all) | yes: 8.7 | yes: 10.2 | yes: 12.9 |
| 14 | Share of the game's rams it starts | 24% (live 22%, test build 37%) | 71% and 80% | 48% | 48% | 57% |
| 15 | Pearls of ram corpses (both dragons) eaten by own team | 28% (live 27%, test build 33%) | 67% (all) | 47% | 49% | 50% |
| 16 | The same with equal numbers of other heads within 8 steps | 26% | 62% (all) | 47% | 49% | 48% |
| 17 | Share of the rams that happen in the own half | 58% (live 58%, test build 57%) | 40% (all) | 47% | 48% | 47% |
| 18 | Change in (own - enemy) total length from rams and their pearls, whole game | -110 | +68 and +148 | -16 | -36 | +12 |
| 19 | Splits by a dragon of exactly 4, rounds 0-99 | 56 | 85 (all) | 107 | 75 | 81 |
| 20 | Sheds (a dragon of 5+ keeps its front two segments), rounds 0-99 | 39 | 22 (all) | 9 | 16 | 27 |
| 21 | Boxed deaths, rounds 0-149 | 82 | 78 and 85 | 95 | 67 | 103 |
| 22 | Non-ram deaths with a free cell, rounds 0-149 | 6.4, of which 6.3 steps through a portal onto a body | 0.5 and 3.4 | 0.3 | 1.2 | 4.1 |
| 23 | Moves of two or more steps, rounds 50-99 (segments paid) | 3 (0) | 25 (6) and 40 (6) | 10 (3) | 43 (7) | 38 (5) |
| 24 | A second own head within 2 steps of an eaten pearl, rounds 50-99 | 14 | 30 and 27 | 30 | 35 | 34 |
| 25 | Cells visited by round 90 | 752 | 895 and 787 | 908 | 821 | 677 |
| 26 | Parent-child path distance 5 / 10 rounds after a split, rounds 0-149 | 6.2 / 8.0 | 6.1 / 8.7 and 6.4 / 8.5 | 6.1 / 8.8 | 5.7 / 7.9 | 5.9 / 8.1 |
| 27 | Ordinary splits, rounds 150-199 | 15 | 24 (all) | 59 | 33 | 53 |
| 28 | Natural pearls per 100 dragon-rounds of a 2-long, rounds 150-199 | 1.25 | 2.5 (all) | 2.8 | 2.8 | 3.3 |
| 29 | Dragons alive in rounds 150-199, of length 2 / 3-4 / 5-9 / 10+ | 24 / 16 / 3 / 0.3 | 22 / 24 / 12 / 3 (all) | 30 / 24 / 4 / 0.5 | 26 / 24 / 6 / 1 | 26 / 20 / 4 / 1 |
| 30 | Goes into narrow fountain corridors: Maze, fountains of the own half eaten from by round 140 (of 19) | partly: 9.7 | 12.2 and 18.1 | 12.3 | 15.4 | 15.2 |
| 31 | Eats in a fountain pocket whose door is a portal: Stripes, pearls eaten on own-half fountains in rounds 0-149 | late or not: 7 | 19 and 39 | 28 | 26 | 29 |
| 32 | Dragons that have not eaten for 20 rounds, share at round 90 | 47% | 39% and 39% | 31% | 44% | 28% |
| 33 | Games in which the own total length is below the opponent's at round 300 | 108 of 109 | (ahead of us in 108 of 109) | 82 of 158 | 48 of 139 | 40 of 127 |
| 34 | Wins among those games | 11 = 10% | | 29 = 35% | 24 = 50% | 16 = 40% |

Where we stand apart from all five columns, in the losing direction: rows 3-5, 8-18, 27, 28, 33 and 34. Where we are like the
others: rows 6, 7, 21 and 26. Row 24: we crowd a pearl less than anyone, which is not a loss in itself. Rows 19 and 20: the
shed excess is Slithery Fight alone (125 a game against 56); on the other large maps the fewer splits at 4 follow the fewer
pearls. Rows 10, 11 and 14: the test build is at the others' level at a meeting and still starts only 37% of the rams, because
it charges 3.9 times a game where they charge 9-14 times (row 13).

## What I would change, and what would show it is wrong (question h)

Neither rule names a map or a map size. Both are about behaviour that all three top teams and both of our usual opponents share
and that we alone do not have. One part of the opening rule has already been on the ladder (the trade-on-contact test build);
its numbers are in answer e and are used below as evidence for and against.

### Opening: a small dragon does not give way to an enemy small dragon that is not shorter than itself

In words, three parts:

1. A dragon of 4 or shorter whose turn begins with an enemy head on the next cell rams it when the enemy is at least as long.
   Today (live bot, maps over 1,200 cells) the target must show max(5, own length + 2) segments.
2. It does the same from two or three cells away when it can reach that head in this turn (a charge), and it does it alone.
   Today a target is marked only if the dragon sees at least as many other own heads as enemy heads and the team has 8 units.
3. Cells next to the head of an enemy that is not shorter are not treated as dangerous when choosing where to step or which
   pearl to go for. Today every cell next to a small enemy head carries a penalty, and a pearl is a target only if we reach it
   before any enemy head (within one step for dragons of 4 or shorter).

Part 1 is the test build. What its 12 large-map games say (answer e):
- It works as a rule: 31% of meetings end in a ram (live bot 10%, opponents 30-37%, top three 36-42%).
- It pays in units and length: 52 units against 58 at round 150 where the live bot has 46 against 61; total length 143 against
  191 where the live bot has 121 against 212; at round 300, 42 units and total 147 where the live bot has 35 and 118. On
  Australia and Islands the opening is no longer lost (total length at round 150: 132 against 140 and 123 against 149).
- It does not do what the rule is for. The border stays where it was (57% of rams in our half; 76% of our heads at home; 57
  natural pearls from the enemy's fountains in rounds 0-149 against the opponents' 96 from ours), the opponents eat as much as
  before (335 natural pearls against 336), and it won 0 of 12.
- Why not more: it still suffers 63% of the rams, and two thirds of the rams it suffers are charges. It charges 3.9 times a
  game in rounds 0-149; test4 and WHQ 13.7 times, forgot 8.7, SSS 10.2, Vibing++ 12.9. A dragon that only fights when the
  enemy has walked up to it fights on the enemy's terms and at home.
- The test's own verdict was counted in wins over 30 games (6 against a pooled 9.2, `data/online/smoke/tc30-test-result.txt`).
  Twenty of those 30 games are on maps of 1,200 cells or fewer, where the test build is the live bot, and on the large maps
  our base rate is 12 wins in 99: no count of wins in 8 or 10 games can see this rule. The counts that can, moved.

What supports parts 2 and 3, which have not been on the ladder:
- 69.7 meetings a game on large maps, and beyond them 8.7-13.7 charges a game by everybody but us (`c_ramsteps.py`).
- The side that starts a ram eats 61-78% of the pearls of both corpses (the test build: 65% at meetings, 52% over all rams it
  starts). Stepping away costs 0.37 pearls in the next ten rounds against the enemy that stays, and one in five of the dragons
  that step away is rammed in those ten rounds anyway.
- With an enemy head in view our dragons end the turn farther from it in 34-37% of turns and nearer in 12-13%; everyone else
  22-29% and 15-22%. 76% of our heads are at home in rounds 50-99 against 68-72%, and the fountains of our half feed the
  enemy: 76 pearls in rounds 50-149 against 34 the other way, a third of the whole pearl gap of those rounds. The test build
  left this as it was, which says it is not the ram at a meeting that keeps our dragons at home.
- The exchange as it is now moves about 110 segments a game to the enemy on large maps and 21 on medium ones; test4 and WHQ gain
  68 and 148 from it against us and lose 3 and 9 against the top three, who ram back (`c_rams.py`).

What would show it is wrong (on the ladder against test4 and WHQ, large maps, against the test build's numbers as the base;
local games against our own bots cannot show it, because two teams that both step away never meet like this):
- Charges stay under 6 a game in rounds 0-149 or the share of rams we start stays under 40% (test build: 3.9 and 37%). Then
  the head count and the unit minimum were not what held the dragons back, and part 2 is not built yet.
- We start 45% or more of the rams and still eat under 35% of the ram pearls (test build 33%, top three 47-50%). Then the
  pearls are lost for another reason (who stands behind the rammer) and the trades only cost us dragons.
- Natural pearls from the enemy's fountains in rounds 0-149 stay under 65 (live 49, test build 57, top three 81-86), or the
  share of rams in our half stays at 57-58%. Then part 3 does not move the border and the rule fails at what it is for.
- Units at round 100 fall below the live bot's 42 (test build 45). We make fewer new dragons per pearl than they do (4.1
  pearls eaten per split at 4 against 3.3 in rounds 0-99; answer b, point 4), so an even trade may cost us more than it costs
  them.
- More games lost by wipe-out (today 103 of our 427 games against 2000+ teams, Schooltime included; `findings.md`).
Limits. The queen is excluded. Local numbers matter for everybody: a top-three rammer's team eats 31-34% of the pearls when
the enemy has three or more heads more within 8 steps and 87-89% when it has three or more itself (we 16% and 75%), so "charge
only when not outnumbered by three" is a refinement to try second; A2 found that forgot holds back in that way before round
100 against the queen.

Not a general rule, but countable on one map type: **split as soon as a dragon is 4, also inside a dead end and while
"harvesting"** (the child is born at the tail, on the way the parent came in). Support: on Slithery Fight we shed 125 times a
game in rounds 0-99 and split at 4 only 65 times (our opponents 56 and 120); in the live game read we eat as many natural
pearls as WHQ there (456 against 447) and lose 272 dragons boxed against 205; SSS eats a quarter fewer pearls than we do,
loses 77 dragons boxed and has more total length at round 150 than we have (200 against 176). forgot and SSS split at 4 and
5 in the same corridors. On the other maps our sheds are no more than our opponents'. It would be wrong if the boxed deaths
on that map rose above today's 243 a game in rounds 0-150 without the units rising, or if the 2-long children were lost at
the corridor mouth (count deaths within 5 rounds of birth).

### Mid-game: no switch by the clock: until the team starts to feed one dragon, every dragon eats the pearl next to it and splits at 4

In words: drop the two things that change at `grow_round` (round 150 on large maps, 300 on the others): the reservation of pearls
within 9 cells of the leader for the leader, and the ban on growth splits of dragons longer than 4. If a switch is wanted, tie
it to the state the feeding phase already uses (the unit count, or the start of feeding), not to the round or the map.

This is the rule I would test first now, on top of the trade-on-contact build. That build shows the opening can be held on
the two maps where the live bot collapses, and that the games are then lost between round 150 and round 300.

What supports it:
- A small dragon with a free pearl next to its head eats it in 81-82% of turns before round 150 and 59-61% after; within 9
  cells of our longest dragon 44%. The opponents in our games: 81-85% all game; forgot 89-91%, SSS 70-80%, Vibing++ 83-89%.
  On medium and small maps the same drop comes at round 300. It is the same in both builds (82% to 59%, 83% to 62%).
- Ordinary splits fall from 32 to 15 per 50 rounds at round 150; the top three make 33-59 and keep 25-31 two-longs and 20-24
  three-to-four-longs until round 300; our 2-longs eat half as much as theirs per dragon-round after the switch (1.25 against
  2.5-3.3).
- The dragons the rule is meant to grow do not grow: our longest dragon at round 300 is 15 on large maps against 16-21 for the
  top three and 24 for our opponents (`findings.md`); the 5-9-longs shed two segments every 15 rounds and are rammed.
- In the test build's games with a won opening (1068050, 1068051: 60 units at round 150 against 33 and 39, total length 207
  against 84 and 170 against 91) the collapse begins in the 50 rounds after the switch and the total length is behind by
  round 249 and 213. Over the test build's three games each on Australia and Islands the units go from 47 at round 150 to 41
  and to 18 at round 300 while the opponents' go from 52 to 56 and from 55 to 58.

What would show it is wrong:
- The rate at which a small dragon eats a free pearl next to it stays under 75% in rounds 150-299 on large maps. Then the
  reservation was not the cause.
- Units at round 200 and 300 on large maps stay at 41 and 35 (48 and 42 on top of the test build), and natural pearls in
  rounds 150-200 at about 52 (`findings.md` section 2).
- The longest dragon at round 300 falls below 15, or our share of wins in games decided by the longest dragon falls below
  today's 29% (41 of 143, `findings.md` section 1). All 12 of our large-map wins are of that kind, so this is the number that
  could get worse.

### What this read says about the ideas already tried

| idea | tried | what the replays say |
|---|---|---|
| Trade on contact (`TRADE_CONTACT`, the tc30 test) | on the ladder, 30 games; counted as 6 wins against 9.2 | Supported as far as it goes, and it does not go far enough. On the large maps, the only ones it changes, it rams like everybody at a meeting and is 5 units and 20 segments better at round 150; it does not charge, does not move the border and won none of 12. The win count that judged it cannot see a rule that acts on 5 of 15 maps, on which we win one game in eight. |
| "Always trade evenly" (`TRADE_EVEN`) and the variants without the local head count | locally: no gain; without the local head count worse against a rushing copy of our bot | Not tested on the ladder. What the ladder shows is what keeping the head count leaves undone: the test build charges 3.9 times a game against 9-14 for everybody else and suffers two rams in three. A local opponent that steps away nine times in ten does not punish stepping away, so the local result says little about test4 and WHQ. |
| A stronger fear of small enemies (`SMALL_THREAT_MULT`) | locally neutral | Contradicted: we already give way far more than anyone (90% of meetings against 58-64%; farther from an enemy head in view in 34% of turns against 22-28%). |
| A relaxed contest for corpse pearls (`CORPSE_SLACK`) | locally no change (share 49-50%) | The ladder deficit is real and large (28% of ram pearls against 47-50% for the top three), and mostly not explained by being outnumbered. A mirror match is 50% by symmetry and cannot show it. |
| State-based split stop (card #14) | locally no change: our bot reaches 60 units either way | Supported: on the ladder we have 47 units at round 150 on large maps and 36-38 on Australia and Islands, so the round-150 stop bites there; the same switch also stops small dragons from eating, which the card did not touch. |
| Splitting while harvesting (`HARVEST_SPLIT`) | locally neutral | Supported for Slithery Fight only (125 sheds a game against 56); on the other maps our sheds are not more than our opponents'. |
| Far-pearl attraction (`FAR_GAIN 2`) | in the live bot | No evidence either way: with no pearl in view our dragons step onto new cells as often as our opponents' (19% against 17-18% of turns in rounds 50-99). |
| Stride (free sprint steps) | locally +14% economy, no more wins | Sprinting does not separate the teams: forgot makes 10 moves of two or more steps per 50 rounds in rounds 50-99 and eats the most of the three top teams in rounds 0-99; SSS and Vibing++ make 38-43, WHQ 40-87. |
| Queen never uses portals (`QUEEN_NO_PORTAL`) | in the live bot | No evidence in the games read. On Stripes, where I first blamed it, the queen rules are off (288 cells; they need more than 600 or a closed home) and the queen does go through the portal in 1068053; she is simply ten rounds later than forgot's. |
| Queen hunt (`QH_SCOUT`, the qh31 test) and "passage2" | on the ladder, 28 games each | Not economy rules; their large-map games look like the live bot's in every count of `c_out/bybatch_large.txt` (ram rate at meetings 10-11%, units at round 150 42-45 against 62-63). |

## Where `findings.md`, `deep-read.md` or `deep-read-2.md` look wrong or thin

1. **All of them, and the brief, treat our games as one bot.** The 401 games are eleven runs (`c_batches.py`), and 42 of them, 12
   on large maps, were played by a candidate that rams on contact. On the measures that matter here the two bots are not the
   same team: 10% and 31% of meetings end in a ram, 46 and 52 units at round 150, total length 121 and 143. Every pooled
   "meow" number for contact (for instance "rams started in rounds 150-200: 3.3" in `findings.md` section 2) is a mix of the
   two, and a reader who picks "our newest games" to read, as I did, reads the candidate. Nothing in `findings.md`, the two
   deep reads or `plan.md` mentions that test or its result.
2. **`findings.md`, section 2, the column "our opponents".** It reads as if test4 and WHQ had a stronger economy than the top three
   (total length 254 at round 200 against 165-195). They do not: it is the economy of a team that plays us. Against the top
   three test4 has 52 units at round 100 and eats 285 natural pearls in rounds 0-149 (forgot 322, SSS 315, Vibing++ 305), holds
   6-11 dragons of 5-9 from round 150 instead of 12-16, and gains nothing from rams (-3 segments a game; against us +68).
3. **"On large maps our units fall from round 150 because growth splits stop"** (`findings.md` section 2 and the brief). True and
   half the story. The same switch stops small dragons from eating pearls next to them (82% before, 60% after; 44% near the
   longest dragon), which no earlier note mentions and card #14 did not touch; and in the two games read with a won opening
   (both of the test build) the units fall because of rams (17 and 26 of our dragons rammed in rounds 150-199 against 4 and 5
   rams made), not because of missing splits alone.
4. **"Per dragon we eat about 10% less in rounds 20-60; the unit gap compounds from there"** (the brief's list of known facts). The 6-8% in
   rounds 0-49 is there (6.6 natural pearls per 100 dragon-turns against 7.0-7.2), but the gap that decides is made in rounds
   50-149 and close to half of it at the border and in the enemy's half. On Around UNSW and Slithery Fight there is no unit gap
   at all until round 300 (median unit ratio 0.94-0.97 at round 150 and 200) and we win 11 of 53: there the measure that shows the
   gap is total length (ratio 0.61 and 0.78 at round 150). In the live game read on Islands (1063012) we are ahead until round
   90.
5. **`deep-read-2.md`, answer 7 and table row 34: "the team that spreads wins the opening ... parent and child part faster
   (6.4-7.3 steps against 4.0-5.3)".** That was one game. Over all games the parent-child distance five rounds after a split is
   the same for everybody (meow 6.2, test4 6.1, WHQ 6.4, forgot 6.1, SSS 5.7, Vibing++ 5.9) and so is the share of the child's
   steps onto unvisited cells (18-21%). Spread differs at team level: cells visited, and above all how much of the team
   stands and eats in the other half.
6. **`deep-read-2.md`: "no top team avoids" the dead-end deaths.** True as far as cells go (40-80% of every team's boxed deaths are
   on a cell where a team-mate had died), but SSS has a third of the others' boxed deaths on Slithery Fight (88 against
   207-288 in rounds 0-150); in the game read it splits at 4 and 5 where we shed at 6-8, eats a quarter fewer pearls than we
   do and has more total length at round 150.
7. **The brief: "we ram much less (3 rams started against 9-12)".** The count is right; two things about it are not where one
   would look. First the cost: in dragons a ram is one for one whoever starts it, and in segments we even lose a little less
   than the enemy (296 against 332 per large-map game); the cost is the pearls (28% against 67%) and the ground. Second the
   kind: more than half of everybody else's rams are charges from two or three cells away (8.7-13.7 a game in rounds 0-149
   against our 1.0), so a rule that only answers at a meeting, like the test build's, closes about half of the gap in rams
   made (13.8 a game in rounds 0-149 against the live bot's 5.1 and the opponents' 22.9).
8. **The brief: Islands, "a 4-cell dead-end corridor where a split child walks in every 6 rounds".** It is there ((40,12): 14
   deaths in 150 rounds of 1068051). The larger countable loss on that map is another: 18.4 dragons a game in rounds 0-149
   step through a portal onto a body they cannot see, 43% of our non-ram deaths there.
9. **`findings.md` section 2 reads the large maps as one.** They are two pairs. Australia and Islands: units and length both
   collapse (1 win in 58). Around UNSW and Slithery Fight: units level, length 60-80% (11 wins in 53). A change that only
   raises the unit count will not show on the second pair; the test build shows it: against the live bot's game with the
   same opponent it has 36-79 segments more total length at round 150 in all four pairs on Australia and Islands, 6 and 49
   more on Around UNSW, and 21 and 33 fewer on Slithery Fight (`c_out/pairs_large.md`).
10. **"Win rate by size: large 13%" as the thing to explain** (`findings.md` section 1). Two different gaps are in that number, and
    the earlier notes study one each without saying how they add up. Counted (`c_endstate.py`): at round 300 we are behind in
    total length in 108 of our 109 large-map games that reach it; forgot in 82 of 158, SSS in 48 of 139, Vibing++ in 40 of
    127. Of the games in which they are behind, they still win 35%, 50% and 40%; we win 10%, and all 12 of our wins are
    longest-dragon wins, 11 of them from behind. So the economy is why we are always behind, and the end game (A, A2) is why
    a game in which we are behind is won three to five times less often than one of theirs. With their conversion and our
    economy we would win 35-50% of the large-map games; with our conversion and their economy I cannot say, because we have
    one game to judge it by.
11. **Thin everywhere, this file included: what a team does in rounds 300-500 with an economy that is level.** forgot was out-eaten
    by test4 on Australia (120 natural pearls against 287 in rounds 0-149) and on Trauma (9 units against 20 at round 100) in
    the games read and won both; the test build is ahead of WHQ at round 150 in 1068050 and 1068051 and loses both; on Portals,
    where the teams never touch, we end 21 losses with as much total length as the winner (50 against 52) and a longest dragon
    of 30 against 42.

## Things I could not determine from replays

1. **Why a dragon declines a free pearl next to its head.** The count is solid (who, when, where); the reason is the bot's score for
   that step, which a replay does not hold. Before round 150 our rate is the same as our opponents' (80-82%); what the missing
   18-20% are I did not find. The one case I followed (1068051, `#3` at (1,37), round 20) had no enemy in view, an open cell,
   and a team-mate three cells away.
2. **Whether the leader zone is the whole reason for the drop at round 150.** The drop is deepest within 9 cells of our longest
   dragon (44%) but is also there with no own dragon of 5+ within 9 cells (67% against 82% before). A remembered leader
   position would explain it; the replay does not show what a dragon remembers. A run with the rule's log line switched on
   would settle it.
3. **Which build played each game, beyond the run name.** The smoke runs name their candidate, and three candidates have their
   source kept (`tc30-bot`, `qh31-bot`, `qn23-bot` under `data/online/smoke/`); the candidates "stride" and "passage2" do not, and
   the two ladder downloads (177 games) carry no mark at all. Whether the live bot itself changed between the four "-old" runs
   of 4 October I did not check; its moves of two or more steps in rounds 0-149 are 7, 13, 18 and 38 a game in those runs,
   which may be the build or the game. The pocket rule in particular: by my own reconstruction of kelp-closed regions our
   dragons still eat 68% of the adjacent pearls in pockets that the rule would forbid (small maps), so either it was not in
   those builds, or it rarely fires because a dragon has not seen every edge of the pocket.
4. **Why our queen waits at the portal door on Stripes.** She has the two pocket pearls in view at round 7, is on the door cell at
   round 18 and goes in or not; forgot's queen goes in at round 8 from the same start. The pocket has four cells, which our
   pocket rule would call too small for a dragon of 2, and in the game in which she stays out an enemy head is two cells from
   the pocket. Either may be the reason; the replay holds neither.
5. **Whether test4 and WeHaveQuizzes know the maps.** Their first dragons are on the fountains at rounds 11-12 on Stripes (through
   a portal) and at round 20 on Trauma, and inside our pocket on Australia at round 33. Knowledge, a strong pull towards
   portals, or symmetry reasoning: a replay cannot tell. They are not always fast: WHQ is stuck in its start room in the
   Tower Defense game read and does not find its fountain column on Trauma until round 130, and test4 is stuck on Tower
   Defense against forgot.
6. **How the opponents' dragons come to stand in our half**: by a rule that sends them there or simply by not turning back at an
   enemy head. The counts fit the second (they end the turn nearer to an enemy head in view in 18-21% of turns, we in 12-13%)
   but do not exclude the first. The same goes for our side: the test build shows that ramming at a meeting does not bring our
   dragons forward, and which of our rules holds them back (the penalty next to small enemy heads, the pearl-target rule, or
   something else) is in the scores, not in the replay.
7. **The true pearl supply.** The replay hides each tile's spawn gap; my "fountain" tiles are counted from appearances, and a
   tile that is eaten promptly appears more often, so the pooled rates are lower bounds and the supply is not strictly "the
   same for both sides" once one side leaves pearls lying.
8. **Whether SSS remembers the cells where its dragons died** on Slithery Fight, or only splits earlier.
9. **Why the same pearls cost us more dragons on Portals** (a dragon lost boxed for every 1.6 natural pearls; test4 1.9, forgot 2.1,
   WHQ 3.3). Our deaths repeat on fewer cells and come more often right after eating there, but we do not take pearls in
   dead-end cells more readily than our opponents. I did not follow single dragons on that map.
10. **Whether opponents call team-mates to a fight or a corpse by sonar.** I did not read the sonar values. That the enemy has
    more heads within 8 steps of a ram in 53% of the rams in our games (top three: 44%) may be numbers, position or a call.
11. **What our win rate would be with a level economy.** We are level or ahead in total length at round 300 in one large-map
    game of 109 (and won it). The top three win 68-75% of such games.
12. **What a ram is worth exactly at each length pair.** I counted who eats the pearls and what the two dragons eat in the next
    ten rounds; I did not follow the units that each side makes from those pearls.
13. **Whether the trade-on-contact test would have won more with more games.** 0 wins in 12 large-map games against a base rate
    of 12 in 99 is no evidence either way.

