You are sub-session A5 of a study for team meow (id 1119) in the Battlecode "deep-sea dragons" game (unswbc 1.2.7).
Your one job: explain, from replays, HOW THE LONGEST-DRAGON RACE IS WON AND WHY WE LOSE IT at equal total length, by reading the
last 250 rounds of our games next to top-team games in the same state, and then write the best general rule you can support as
a candidate hypothesis. Output file: `deep-read-5.md`. Work only in this directory, which is your current directory:
`~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/top1/`

There is no time limit. Depth matters. But a file that is never written is worth nothing: create `deep-read-5.md` once the
all-games tables of questions (a) and (b) are done and rewrite it after each further question, so that it is always complete
for what has been done so far.

## Why this read exists
The study asks how the rank-1 team (Vibing++, id 306) and the two teams level with it (SSS, id 91; "forgot to mention", id 264) win
against teams rated 2000+, to find ONE well-supported idea for our bot. Done so far: four close reads (`deep-read.md` Vibing++,
`deep-read-2.md` SSS and forgot, `deep-read-3.md` our economy, `deep-read-4.md` our own queen), a fact sheet (`findings.md`), four
candidate hypotheses (`hypotheses.md`) and a red team that recounted and attacked them (`redteam.md`). Read `findings.md` (all of
it; sections 1, 6b, 6c, 6d matter most here), then in `redteam.md` section 1 and "All candidates, attack I: the footing", then in
`hypotheses.md` candidate 3 and "Not proposed, and why", then what `deep-read-2.md` says about feeding (its finding on feeding
clocks and the per-game "late game" notes).

The red team's conclusion: the surviving candidate ("any dragon with the enemy queen in view and reach rams her") is real, safe
and small (about +1 point of win rate), and **the largest countable gap that no candidate works on is the longest-dragon race**:

- 143 of our 401 games against 2000+ teams end at round 500 with both queens dead, so the longest single dragon decides. We win
  41 (29%); the top three win 266 of 447 (60%).
- At equal economy the gap stays on maps of 1,200 cells or fewer: with own / enemy total length at round 400 between 0.8 and
  1.25 we win 9 of 30 such games (the top three 22 of 40); our longest dragon is 5 at round 300, 12 at round 400 and 28 at the
  end, against the enemy's 7, 16 and 39; a top team's is 7, 21 and 46 against 7, 18 and 42. Over all maps, 14 of our losses came
  with at least as much total length as the enemy at round 400 (listed in `x_out/race.txt`: five on Maze, five on Portals, three on
  weakhold, one on Slithery Fight; for instance 1027819: total 136 against 131, longest 13 against 58 at round 400).
- On maps over 1,200 cells the picture is the reverse: there our leader rules start at round 150 instead of 300, our leader is as
  long as a top team's at the same economy (27 at round 300 in level games against 16) and we convert as well as they do (4 of 6
  level, 6 of 23 behind against 17 of 49); all 12 of our wins there are longest-dragon wins, 10 of them from behind in total
  length. But the same early switch costs the economy: after it our small dragons take a free pearl on the next cell in 56% of
  turns instead of 80% (everyone else stays at 75–88%), and total length stands still from round 150 to 300 (`findings.md` 6c).
- How the others build the leader (`deep-read-2.md`): small dragons walk to within a few cells of one dragon and die there by
  choice, about 2.6 segments spent per segment it gains; forgot starts at about round 200–225 (it feeds its queen while she
  lives), SSS at about 200–300. Our bot: from `grow_round` (150 on maps over 1,200 cells, 300 otherwise) small dragons leave
  pearls within 9 cells of the leader for it and dragons longer than 4 stop splitting; deliberate feeding deaths start at
  `feed_round` (400; 300 in queen-feeding mode; 200 when the team has 56 units).
- It was tried in a simple form and came out neutral: feeding from round 330 instead of 400 won 24 of 60 online against a test
  opponent where the base won 23 (an older bot, the old map pool); feeding from 330 and from 300 won 70 and 69 of 152 locally
  where the base won 76 (`work/plan.md`). The team also notes "our late feeding often feeds the opponent".
So there is a measured gap and no rule yet. Your job is to find out what the winners of this race actually do differently from
us, round by round, and whether a general rule follows.

## Hard rules
- Read-only towards the outside world: no network, no uploads, no GitHub, no Discord. Do not run games. Never read key or token files.
- Write only inside this directory. Name your own scripts `e_*.py` and put their outputs in `e_out/`. Do not edit or delete existing
  files. At top level you create only `deep-read-5.md`, your scripts, and part files `e_*.md` if you assemble the report from parts.
- A policy hook guards the shell. It allows only Bash, Read, Glob, Grep, Write, Edit. It blocks: `python3 -c`, `$(...)`, backticks
  (also inside a heredoc), a single `&` anywhere in a command (so no `2>&1`, no background `&`), `curl`/`wget`, sub-agents and every
  other tool, and any shell command that mentions `settings.json`, `guard.py` or `work/loop`. Put code in a file and run
  `python3 e_something.py args`. Plain pipes (`| head`) and `;` are fine. Do not try to work around the hook. Do not start other AI
  sessions. Read the bot source and the team's log with the Read or Grep tool, not the shell.
- Be honest: say what you saw in the replay (round, coordinates, dragon ids), what you infer (mark it "inference"), and what cannot
  be seen. A replay shows positions, actions, deaths, pearls and sonar rays; not intentions, memory or scores.

## The game in ten lines
- Snake-like dragons on a wrapping grid. Kelp (walls) and portals sit on the EDGES between tiles. A dragon sees the 7x7 square around its head.
- Each round every living dragon acts once, in ascending id order. A dragon must MOVE (1 or more steps) or SPLIT; there is no "stay".
- A dragon of length L gets ceil(L/4) free steps per turn; each extra step costs one segment.
- Moving the head into another dragon's HEAD kills both (a ram), whatever their lengths. Into a body, kelp or itself kills only the mover.
- A dead dragon of length L drops ceil(L/2) pearls on its body cells (head, skip one, next...). Eating a pearl = +1 length. So a
  dragon that dies next to a team-mate hands over at most half of its length.
- Split: a dragon of length 4 or more splits off its rear as a new dragon (child at least 2, parent at least 2). The child's head is the
  old tail, facing the other way. At most 64 dragons per team.
- Pearls: every tile has a hidden spawn interval; a pearl appears only on an empty tile.
- THE QUEEN is each team's lowest id (0 or 1). The game ends at round 500 or when one team has no dragons. At round 500 the longer
  living queen wins (a living queen beats a dead one); if both are dead or equal, the longest single dragon wins; then total length.

## Which bot played our games
Our 401 games against 2000+ teams (map Schooltime left out) are eleven runs; the run is the column `battle_id` in `games.csv`.
Ladder downloads `dl-20261003`, `dl-20261004` and the "-old" halves of the smoke pairs are the live bot (275 games); the "-new"
halves are test builds (stride, passage2, qh31, tc30; 126 games); none of them changed the leader or feeding rules. 313 of the
401 games are against test4 (id 19) and WeHaveQuizzes (id 87). Mark every game you read with its run.

## Our bot's leader and feeding rules (start here, then read the functions)
`~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp`: `grow_round = aggressive ? LEADER_GROW_ROUND (300) :
LEADER_GROW_ROUND_BIG (150)` with `aggressive = cells <= AGGRESSIVE_MAX_CELLS (1200)`; `feed_round = ENDGAME_ROUND (400)`, lowered to
`QUEEN_GAME_FEED_ROUND (300)` in queen-feeding mode; `feeding_phase()` is also true from `FEED_CAP_ROUND (200)` on when the team has
`FEED_CAP_UNITS (56)`. `is_leader()`, `known_leader_id`, `refresh_leader_zone()`, `in_leader_pearl_zone()` (`LEADER_PEARL_RADIUS 9`,
`ZONE_PEARL_PENALTY 600`), `split_child_size()` (no splits above length 4 after `grow_round`, none by the leader), `pick_feed_target()`,
`is_feeder()`, `feed_len_ok()` (`FEED_LEN_RATIO 2`), `ready_to_die()`, `local_die()` (`FEED_LOCAL 0` = off), `FEEDER_APPROACH 15`,
`FEEDER_KEEP_UNITS 3`, `FEEDER_ENEMY_CLEAR 4`, `FEEDER_DIE_DIST 3`, `LEADER_ENDGAME_PEARL_MULT 4`, the toggles `LC_LEAD_ROUND`,
`LC_FEED_ROUND`, `LC_ENEMY_LEAD`, `LC_ENEMY_FEED`, `FEED_EARLY_ROUND`, `FEED_BOOT_LEN` (all 0 = off), `END_HUNT_MIN_PARTS`, and how the
leader's identity and position travel between dragons (sonar). The author's experiment log is
`~/01. Project/개인 프로젝트/battlecode/work/plan.md`: find every trial of the leader round, the feed round, feeding
by local deaths, the leader zone, "late feeding" (card #22), the state-based split stop (card #14), and what each gave.

## Tools already here
- `q/<game_id>.json` (all 2,343 games; `extract.py`): per round and side units / total / longest / second longest, a length
  histogram every 25 rounds, every ram (with lengths), every suicide, deaths of big dragons, queen deaths. `x_out/race.txt`,
  `x_out/race2.txt` and the red team's `x_race.py`, `x_race2.py`, `x_race3.py`, `x_c3wins.py`; the lead's `leaderrace.py`, `behind.py`,
  `cf.py` (leader kills after round 400) with outputs in `out2/`; `h_race.py`, `h_c3.py` (sub-session B); A2's `b_feed.py` and
  `b_out/feed_all.txt` (when each top team's queen is fed). Read the docstrings; copy and adapt under your own `e_` names.
- `lib.py`: `lib.Walk(path).run(hooks)` streams a replay with the full board state: every body, every pearl and where it came from
  (`('natural',)` or `('corpse', team, id, reason)`), hooks `round_start, action, moved, split, death, eat, sonar, end` (read its
  source, 260 lines). About 1.3 s per game; `recount3.py` is a short example with a multiprocessing run (use at most 5 workers
  and `os.nice(10)`).
- `python3 digest.py <game_id> <team_id>`, `python3 story.py summary|queen|track|view|events ...` (run `python3 story.py` for usage):
  `track <id> <dragon>` follows one dragon; `view <id> <round> <x> <y> [radius]` draws the board; `events <id> <r1> <r2> [x y radius]`
  lists every action in turn order.
- `games.csv` (one row per game), `cand1119.txt`, `cand91.txt`, `cand264.txt`, `cand306.txt` (one line per game of that team against
  2000+ teams, with final lengths and queen fates).

## Which games
All-games counts first (questions a to e), on: our 143 round-500 games with both queens dead, the top three's 447, and the other
side of our games (our opponents are the winners of most of our races, in the same game on the same map). Then read closely:
- at least 14 of OUR games from rounds 250 to 500: the 14 losses with at least level total length at round 400, or as many of
  them as it takes to cover each map, plus 4 level games we won and 4 games on maps over 1,200 cells that we won from behind on
  the longest dragon; in every one read the opponent's side of the same game as well;
- at least 8 top-team games in the same state (both queens dead by round 300–400, total length level at round 400), same map
  class, won on the longest dragon; prefer games against test4 and WeHaveQuizzes, and include each of the three teams.

## The questions (answer each with game ids, rounds, dragon ids and counts; say "not seen" where that is the case)
a. **The leader's curve.** For each group (meow live bot / test builds; our opponents; forgot; SSS; Vibing++), by map class (over
   1,200 cells / 1,200 or fewer, because our own switch differs there; say also whether the picture depends on anything else
   about the terrain) and by own / enemy total length at round 400: the longest dragon's length every 25 rounds from 150 to 500;
   the round at which the dragon that ends as the longest first passes 8, 15 and 25; its share of the team's total; the team's
   units and total length alongside. When does each team start, and how fast does it grow once started?
b. **Where the leader's length comes from.** Per 50 rounds, for the dragon that is the team's longest at the end and for whichever
   dragon is the longest at the time: segments gained from natural pearls, from pearls of own dragons that died by choice near it
   (define "by choice": a death that is not a ram, with a free cell next to the head, or a move the dragon could not pay for), from
   pearls of other own corpses, from enemy corpses; segments it spent (paid steps, splits, sheds); and for the team: feeders spent
   and their length, the share of feeder pearls the leader ate / other own dragons ate / the enemy ate / nobody ate, and the
   leader's gain per segment of feeder spent. How far from the leader's head does a feeder die, and how far away is the nearest
   enemy head at that moment?
c. **Who the leader is and whether it lasts.** Is the dragon that is longest at round 300 / 350 / 400 still the longest at the end?
   How often is a leader of 15+ / 25+ lost (rammed by an enemy and of what length, boxed in, cut or shed down, starved by paid
   steps) and what did the team do next? Where does the leader live (distance to the nearest enemy head, to its own start, open or
   closed terrain, behind a portal), how much does it move, does it eat on its own? Does a team run one leader or several?
d. **Our two switches as natural experiments.** (1) The leader zone: from `grow_round` on, follow every free pearl that one of our
   small dragons left lying within 9 cells of our leader: who ate it in the end (the leader, another of ours, the enemy, nobody
   within 30 rounds) and when; how much the leader gains from the zone per 50 rounds against what the team did not eat. Do this on
   both map classes (the zone starts at round 150 on one and 300 on the other). (2) Feeding: find in each of our games the round
   at which deliberate feeding deaths actually begin (it can be 200, 300 or 400 by the rules above, depending on units and on the
   queen), and compare games with an early and a late start in the same band of total length: the leader's curve and the result.
   Which of the two mechanisms builds our leader, round for round?
e. **The trigger of the others.** For forgot, SSS, Vibing++, test4 and WeHaveQuizzes: the round at which feeding of a non-queen
   leader begins, against candidate states: the round itself, the own queen's death, the enemy queen's death, the unit count
   (near the cap of 64?), the first round with no enemy head near the leader, the enemy's longest dragon passing some length. Is
   it a clock or a state? What do they do in the rounds between their queen's death and the start of feeding?
f. **The close read.** In each game read: both teams' leaders from round 250 on (id, length every 25 rounds, where it is), every
   feeder death near them, every leader loss, and the moment the race was decided. What exactly did the winner do between rounds
   300 and 500 that we did not: start earlier, feed faster (more feeders per round, feeders nearer, feeders longer), lose less to
   the enemy, keep its leader alive, pick a better dragon, keep eating natural pearls meanwhile?
g. **The earlier trials.** For each trial in `work/plan.md` and online that moved the leader or feed round or changed how feeders
   die: exactly what was changed, on which bot version and map pool, against whom, the result, and whether what you now see in
   replays explains a neutral result (for instance: an earlier feed round that only halves the team while the leader gains
   little because feeders die too far away or the enemy eats the pearls).
h. **The risks, counted.** How often is an early, long leader rammed (by round started and by leader length), ours and theirs?
   What does early feeding cost in units and in natural pearls eaten, and does the team that starts first lose the game more
   often on a wipe-out or on the queen rule? How much of our feeding goes to the enemy, and under what local conditions?
i. **The rule, written as a candidate hypothesis.** If the evidence supports one: a general rule for when and how our team builds
   its longest dragon. It may depend on the game state (rounds, lengths, counts, which queens live, what a dragon sees) and on
   terrain; it must NEVER name a map and NEVER use a map-size condition (removing the map-size switch our code has today counts
   as making it general). Write it in the format of the candidates in `hypotheses.md`: (1) the claim; (2) evidence: us against each
   of the three top teams and against our opponents in the same games, the winners against the losers of level races, at least two
   game ids with rounds showing the behaviour and its absence, each number marked measured or inferred, and the earlier trials;
   (3) mechanism under the longest rule; (4) expected effect: games of our 401 (and of the live bot's 275) that would have ended
   differently under a strict reading and a realistic one, as points of win rate with an honest range, in which kinds of game it
   acts, and how it combines with the four existing candidates (candidate 3 above all, which moves the same switch the other way
   on maps over 1,200 cells); (5) what changes in `mybot2/main.cpp` by function and constant, and whether a toggle exists; (6) what
   would show it wrong: behaviour numbers countable on 20–60 new replays with your scripts, and how many games a win test would
   need; (7) known risks. Heed the red team's cautions when sizing it: a win rate "for a band" was earned with the bot as it is and
   is not a property of the band; counts on fewer than about 30 games need their range said; 313 of our games are against two
   opponents; say what holds against each of them separately. If the evidence supports no rule, say so plainly and say what is
   missing; "the gap is real and I found no rule" is an acceptable result.

## Output: `deep-read-5.md` (plain, casual, clear English; a teammate must be able to follow it without this brief; explain a term on first use)
1. The three findings that matter most, at the top.
2. The all-games tables for (a) to (e), each with its script and output file.
3. A table of the games read (id, map, cells, run, side, opponent, result, total and longest at rounds 300 / 400 / end for both sides).
4. Per game read: the story of the two leaders from round 250, with rounds, dragon ids, coordinates and small board views where
   they explain something.
5. "Answers to the nine questions" with counts.
6. "The race, us against the others": one row per behaviour, columns meow / our opponents / forgot / SSS / Vibing++.
7. "Candidate 5" in the seven-item format of question (i), or "No rule supported" with reasons.
8. "Where `findings.md`, `hypotheses.md`, `redteam.md` or the earlier deep reads look wrong or thin", if you find anything.
9. "Things I could not determine from replays".
Every count quoted in sections 2 and 5–7 must come from a script or from a list of game ids and rounds you can show. Finish by
printing the line `SUBSESSION A5 DONE` as your final message.
