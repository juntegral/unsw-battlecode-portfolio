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
