You are sub-session A4 of a study for team meow (id 1119) in the Battlecode "deep-sea dragons" game (unswbc 1.2.7).
Your one job: explain, from replays, HOW AND WHY OUR OWN QUEEN DIES so early and so often, by reading our games next to top-team
games on the same maps, and say which general rule would keep her alive and what that would be worth. Output file: `deep-read-4.md`.
Work only in this directory, which is your current directory:
`~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/top1/`

There is no time limit. Depth matters. But a file that is never written is worth nothing: create `deep-read-4.md` once the
classification of question (a) is done and rewrite it after each further question, so that it is always complete for what has
been done so far.

## Why this read exists
The study asks how the rank-1 team (Vibing++, id 306) and the two teams level with it (SSS, id 91; "forgot to mention", id 264) win,
to find ONE well-supported idea for our bot. Three close reads are done: `deep-read.md` (15 Vibing++ games), `deep-read-2.md` (SSS
and forgot: how THEIR queens live and how they hunt), `deep-read-3.md` (why our economy falls behind). `findings.md` holds the
numbers on all 2,343 games; read it first, all of it (sections 1, 4, 6b and 6d matter most here), then the "three findings" and
the queen answers of `deep-read-2.md`. What nobody has read closely is our own queen in our own games:

- Our queen is dead before round 100 in 45% of our 401 games against 2000+ teams and before round 300 in 84% (Vibing++ 62%, SSS 43%,
  forgot 52%). On maps over 1,500 cells: 95% before round 300 (top three 49–57%). On maps of 600 cells or fewer: 95% (42–74%).
- 63% of our queens are rammed by an enemy, 28% die boxed in or by their own crash (SSS 11%, forgot 12%, Vibing++ 27%), 10% live.
- About half of every top team's wins are queen-rule wins (their queen alive, the other dead). Ours: 4 of 51 wins in games that
  reach round 300. At the same economy (own / enemy total length at round 300) our queen is alive at round 300 half to a quarter as
  often as a top-three queen (`findings.md` section 4). 102 of our round-500 losses ended with BOTH queens dead: each would have
  been a queen-rule win had ours lived.
- A2 found that a top queen survives by where she lives, not by guards: SSS's queen eats 2.1 natural pearls per 100 rounds (an
  average SSS dragon 4.7) and stays 10.8 cells from her spawn (team 16.7); nobody escorts; a queen always steps away from a close
  enemy (Vibing++ 151 of 151 rounds) and pays segments for it; a boxed-in 2–3-long queen dies in every team.

## Hard rules
- Read-only towards the outside world: no network, no uploads, no GitHub, no Discord. Do not run games. Never read key or token files.
- Write only inside this directory. Name your own scripts `d_*.py` and put their outputs in `d_out/`. Do not edit or delete existing
  files. At top level you create only `deep-read-4.md`, your scripts, and part files `d_*.md` if you assemble the report from parts.
- A policy hook guards the shell. It allows only Bash, Read, Glob, Grep, Write, Edit. It blocks: `python3 -c`, `$(...)`, backticks
  (also inside a heredoc), a single `&` anywhere in a command (so no `2>&1`, no background `&`), `curl`/`wget`, sub-agents and every
  other tool, and any shell command that mentions `settings.json`, `guard.py` or `work/loop`. Put code in a file and run
  `python3 d_something.py args`. Plain pipes (`| head`) and `;` are fine. Do not try to work around the hook. Do not start other AI
  sessions.
- Be honest: say what you saw in the replay (round, coordinates, dragon ids), what you infer (mark it "inference"), and what cannot
  be seen. A replay shows positions, actions, deaths, pearls and sonar rays; not intentions, memory or knowledge.

## The game in ten lines
- Snake-like dragons on a wrapping grid. Kelp (walls) and portals sit on the EDGES between tiles. A dragon sees the 7x7 square around its head.
- Each round every living dragon acts once, in ascending id order, so both queens (ids 0 and 1) move before every other dragon.
  A dragon must MOVE (1 or more steps) or SPLIT; there is no "stay".
- A dragon of length L gets ceil(L/4) free steps per turn; each extra step costs one segment. Most steps in a turn ("reach"):
  1, 2, 3, 5, 6 for lengths 2, 3, 4, 5, 6.
- Moving the head into another dragon's HEAD kills both (a ram). Into a body, kelp or itself kills only the mover.
- A dead dragon of length L drops ceil(L/2) pearls on its body cells. Eating a pearl = +1 length.
- Split: a dragon of length 4 or more splits off its rear as a new dragon (child at least 2, parent at least 2). The child's head is the
  old tail, facing the other way. At most 64 dragons per team.
- THE QUEEN is each team's lowest id (0 or 1). She is an ordinary dragon in every other way; at the start she is the team's first
  (often only) dragon and has to begin the economy herself.
- The game ends at round 500 or when one team has no dragons. At round 500 the longer living queen wins (a living queen of any
  length beats a dead one); if equal (both dead, or the same length), the longest single dragon wins; then total length.

## Which bot played our games (important)
Our 401 games are eleven runs; the run is the column `battle_id` in `games.csv`. Ladder downloads `dl-20261003` (24 games) and
`dl-20261004` (153): the live bot of that hour. Smoke-test pairs against test4 (id 19) and WeHaveQuizzes (id 87, "WHQ"), one game per
map each: `stride-old/new`, `passage2-test-old/new`, `qh31-test-old/new`, `tc30-test-new` (28 games each), and against "dev test 1"
`tc30-dev1-old`, `tc30-dev1b-new` (14 each). "-old" = the live bot, "-new" = a candidate: stride (free sprint steps), passage2 (lets
short dragons through narrow passages; the team's note says this change got our queen killed online), qh31 (queen hunters of 4 or
shorter), tc30 (small dragons ram on contact on maps over 1,200 cells). Kept sources: `../../online/smoke/tc30-bot/main.cpp`,
`qh31-bot`, `qn23-bot` (a queen "no trap" candidate). Mark every game you read with its run, give every all-games count for the live
bot (ladder + "-old" runs) and for the candidates separately where they differ, and use the old/new pairs as natural experiments
where a candidate touched the queen (passage2 above all: same opponents, same maps, same hour).

## Our bot's queen rules (read the source with the Read or Grep tool, not the shell)
`~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (toggles are the `constexpr` lines near the top). Points to
start from: `is_queen()` is true only when `cells > QUEEN_MIN_CELLS (600)` or `home_closed`; on the six maps of 600 cells or fewer
our queen is therefore an ordinary dragon unless her start area is closed. With `is_queen()` true: no splits after
`QUEEN_SPLIT_ROUND 200`, no portal steps (`QUEEN_NO_PORTAL`), she is not a trader, a threat penalty with `QUEEN_THREAT_MULT 1.0`
and reach up to `QUEEN_REACH_MAX 8`; `QUEEN_GUARD_RADIUS 0`, `QUEEN_DEAD_PENALTY 0`, `QUEEN_ROOM 0`, `QUEEN_PESSIMIST false`,
`QUEEN_GIVE_WAY 0`, `QUEEN_BRAIN false` (all off). The general step score (`score_step`) has room / dead-end penalties
(`PENALTY_TIGHT`, `PENALTY_TRAPPED`, `PENALTY_NO_TAIL`, the pocket rule `POCKET_CAP 48`) and a head-race penalty for cells an enemy
head can reach (`threat_at`, `PENALTY_HEAD_RACE 450`). The author's experiment log is
`~/01. Project/개인 프로젝트/battlecode/work/plan.md` (Read tool only): it lists the queen toggles tried in LOCAL
games, all without a gain in survival: never step into reach, escorts, give-way, longer queen, no early splits, never split, known
cells, safe zone, portal bans, wait. Local games are against our own older bots, which do not hunt queens; the local queen-alive
rate is 11–20%. Team cards: #23 `QUEEN_NO_TRAP`, #25 `QUEEN_WAIT` (never fired because she is 2–3 long when boxed in), #16 safe zone,
#18 "queen should end longer than 3". A teammate's untested idea: "stay at length 2 and circle on 4 tiles".

## Tools already here
- `q/<game_id>.json` (all 2,343 games; written by `extract.py`, read its docstring): per side `qdeath` (round, reason, length,
  position, the killer with its start cell, length, steps used, whether born that round), `qsplits`, `qsteps`, `qeats`,
  `episodes` (enemy approaches to the queen), `per.q[round]` = `[x, y, len, e8m, e8p, e4p, a6p, a3p, seen, margin, near_small, free,
  ball4, degree, portal_dist, start_manh, is_longest]` (enemy heads within 8 Manhattan / 8 path / 4 path steps, allied heads
  within 6 / 3 path steps, whether an enemy has her in view, free neighbour cells, openness, distance from her start cell), and
  `per.units / total / longest` per round. `q2/`, `q3v2/` hold kill tracks and turn-level ram chances on the enemy queen.
- `selfdeath.py`, `defend.py`, `qmap.py`, `qan.py`, `approach.py`, `approach2.py`, `approach3.py`, `qearly.py`, `behind.py` (lead) and
  their outputs in `out2/`; `b_*.py` (A2's queen scripts: where a queen lives, what she eats, followers, boxed-in queens) with
  outputs in `b_out/`. Read the docstrings; copy and adapt under your own `d_` names.
- `python3 digest.py <game_id> <team_id>`, `python3 story.py summary|queen|track|view|events ...` (run `python3 story.py` for usage):
  `queen <id> <team>` follows a queen round by round; `view <id> <round> <x> <y> [radius]` draws the board around a cell;
  `events <id> <r1> <r2> [x y radius]` lists every action in turn order.
- `lib.py`: `lib.Walk(path).run(hooks)` streams a replay with the full board state (every body, every pearl and where it came from,
  kelp and portal edges; `Board.bfs/ball/degree/step`). Checked against the engine on 81,853 steps. `recount3.py` is a short
  example of a hooks class with a multiprocessing run over many games (about 1.3 s per game).
- `games.csv` (one row per game: map, cells, teams, elo, winner, end type, `battle_id`, replay path), `cand1119.txt`, `cand91.txt`,
  `cand264.txt`, `cand306.txt` (one line per game of that team against 2000+ teams, with queen fates).

## Which games
Use opponents rated 2000+ and leave the map Schooltime out (both queens are sealed in there). First classify ALL our queen deaths
by script (question a). Then read closely at least 24 of our games, chosen from the classification so that every kind of death
with 15 or more cases has at least three games, across different maps and mostly the live bot; plus 3 of the 39 games in which our
queen lived. For every kind, read next to it:
- the OPPONENT's queen in the same game (same map, same round, mirrored start: the cleanest comparison there is), and
- one or two top-team games on the same map in which the top team has our side letter (same start) and, if possible, the same
  opponent (SSS, forgot and Vibing++ all play test4 and WHQ), with the top queen alive at round 300.

## The questions (answer each with game ids, rounds, coordinates and counts; say "not seen" where that is the case)
a. **Every death, classified.** For all our queen deaths (about 362), from the board state in her last 10 rounds, a kind such as:
   boxed in a terrain dead end she walked into (for a pearl? after a split? fleeing?); boxed in by her own body or by allied
   bodies (which ally, how long, was it her own split child?); stepped through a portal onto a body; rammed in a meeting she could
   have left (an enemy head was in her view at the start of her turn and a step out of its reach existed); rammed after she herself
   stepped next to or into the reach of a visible enemy head; rammed by a charge from outside her view (nothing she could see);
   rammed with no safe step left (cornered: say by what); she rammed an enemy herself. Give counts by kind, by round band (0–49,
   50–99, 100–299, 300+), by run (live / each candidate), by whether `is_queen()` was on (cells over 600), her length, the killer's
   length and how many steps it moved, and what each game became. Do the same classification for the queens of Vibing++, SSS,
   forgot and of our opponents in our games, so that every row has a comparison.
b. **Avoidable or not.** For the rammed deaths: at the start of her last turn and of each of the five turns before it, which enemy
   heads were in her view, how many of her legal steps ended outside the reach of every visible enemy head, and which did she
   take? How often does she step nearer to a visible small enemy head, and how often does a top-three queen (and our opponent's
   queen) do that in the same situation? Give the share of our rammed deaths in which she had a step out of reach on the last
   turn / at any of the last three turns, and the same for the top three.
c. **How she lives.** Per 50 rounds, for our queen, our opponent's queen in the same games and the three top teams' queens:
   natural pearls eaten against her team's average dragon, distance from her start cell against her team's, share of rounds in the
   enemy's half, enemy heads within 4 and 8 steps, rounds with an enemy head in her view, splits she makes and her length, cells
   used per 25 rounds. Is our queen a forager like any other dragon of ours? At which round, or at which state of the game (units,
   first enemy seen), does a top queen stop foraging forward, if she does? A top queen is the team's only dragon at the start
   too: describe the hand-over from "she builds the economy" to "she keeps out of the way" in SSS and forgot games, and whether
   ours has one.
d. **The opening deaths.** 80 of our queens die before round 50. Some are one pattern on one map (Portals: boxed by a body at
   rounds 9–10 at length 4–5 in 11 games; Devil rounds 18–32; Slithery Fight round 3). Describe each repeating pattern exactly
   (cells, what blocked her, the split or step before it) and say what general state it is an instance of.
e. **Queen rules on and off.** On maps of 600 cells or fewer our queen rules are off. Does she behave differently there in ways a
   replay shows (portal steps, splits after round 200, rams she starts, steps next to enemy heads)? Do the rules that are on
   elsewhere change her fate (compare kinds of death and rounds)? What did the passage2 candidate change for her (old against new
   pairs), and the qn23 no-trap candidate if any of its games are in the data?
f. **Found and survived.** How often is each team's queen seen by an enemy head (in its 7x7 view), for how many rounds, and how
   often does she survive being seen? What happens to enemy small dragons that come within 4 steps of her: rammed by a defender,
   leave, ram her? Is there any queen that circles on a few cells (a loop of 4–8 cells), where and for how long, and what happens
   when an enemy 2–3-long finds a circling queen (she moves first each round)? Is a 2-long queen on a 4-cell loop catchable by one
   small dragon, by two? Work it out from the rules and check it against cases.
g. **What it is worth.** For each kind of death in (a): the games it cost under assumptions you state. Two readings at least: (1)
   strict, nothing else changes: round-500 losses with both queens dead turn into wins, the rest stays; (2) she then survives the
   rest of the game as often as a top-three queen does from that round on, on that map size and at that economy (own / enemy
   total length at that round, bands as in `behind.py`). Give the result for the live bot's games alone as well.
h. **The rule.** If you could change one general rule for our queen (game state or terrain only: no map names, no map-size
   conditions), which would it be, stated precisely enough to code against `score_step` and the functions around it; which kinds
   of death and how many cases would it have prevented, which would it not touch, what would it cost (she is one of our first
   foragers), and what would show it is wrong? Which of the toggles the team already tried is it closest to, and why would the
   ladder result differ from the local result (or not)? Give a second-best rule too.

## Output: `deep-read-4.md` (plain English; a teammate must be able to follow it without this brief; explain a term on first use)
1. The three findings that matter most, at the top.
2. The classification table of (a) for meow (live bot / candidates), our opponents, forgot, SSS, Vibing++.
3. A table of the games read (id, map, cells, run, side, opponent, result, kind of queen death, round).
4. Per kind of death: the games read, with rounds, coordinates and small board views where they explain something; the same
   situation in the opponent's and the top team's game.
5. "Answers to the eight questions" with counts (name the script and the output file for each count).
6. "Our queen against the others": one row per behaviour, columns meow / our opponents / forgot / SSS / Vibing++, each cell a number
   or "yes / no / partly" with an example.
7. "What I would change, and what would show it is wrong" (question h), and "what it is worth" (question g).
8. "Where `findings.md` or the earlier deep reads look wrong or thin", if you find anything.
9. "Things I could not determine from replays".
Every count quoted in sections 2 and 5–7 must come from a script or from a list of game ids and rounds you can show. Finish by
printing the line `SUBSESSION A4 DONE` as your final message.
