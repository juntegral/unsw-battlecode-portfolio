You are sub-session A3 of an overnight study for team meow (id 1119) in the Battlecode "deep-sea dragons" game (unswbc 1.2.7).
Your one job: explain, from replays, WHY OUR TEAM'S ECONOMY FALLS BEHIND the top teams', by reading our games next to top-team
games on the same maps. Output file: `deep-read-3.md`. Work only in this directory, which is your current directory:
`~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/top1/`

There is no time limit. Depth matters. But a file that is never written is worth nothing: create `deep-read-3.md` after the first
two maps and rewrite it after each further map, so that it is always complete for what has been read so far.

## Why this read exists
The study asks how the rank-1 team (Vibing++, id 306) and the two teams level with it (SSS, id 91; "forgot to mention", id 264) win,
to find ONE well-supported idea for our bot. Two close reads are done: `deep-read.md` (15 Vibing++ games) and `deep-read-2.md`
(SSS and forgot, with a three-team table); `findings.md` holds the numbers on all 2,343 games. Read `findings.md` and the "three
findings" and "answers 7 and 8" parts of both deep-read files first. They cover queens, hunting and feeding well. What nobody has
explained is the largest gap of all, the economy:

- Large maps, opponents rated 2000+ (means per game): at round 200 we have 39 units and total length 116; the top three have
  53–58 units and 165–195; the teams we actually play (mostly WeHaveQuizzes, id 87, and test4, id 19) have 61 units and 254 against us.
  Natural pearls we eat per 50 rounds: 83 (r50–100), 52 (r150–200), 44 (r250–300). Top three: 102–108, 107–124, 102–120.
- Our win rate on large maps is 13% (top three 56–67%). When both queens are dead at round 500 the longest dragon decides and we
  win 29% of those (top three 60%).
- In the top-team games themselves, 7 of Vibing++'s 9 losses read were behind 1.5 to 1 or worse in units by round 50–100.
- A2 found that the team that spreads wins the opening: on Australia forgot's heads stood in 20 of 64 board squares at round 60
  (SSS 9, Vibing++ 6) and it had visited about 1,300 cells by round 100 (788 and 454); parent and child were 6.4–7.3 steps apart five
  rounds after a split (Vibing++ 4.0–5.3). It also found that every team loses many small dragons in one-cell dead ends that hold
  a pearl (97–99% of early non-ram deaths happen with no free cell next to the head), the same cells again and again.

## Hard rules
- Read-only towards the outside world: no network, no uploads, no GitHub, no Discord. Do not run games. Never read key or token files.
- Write only inside this directory. Name your own scripts `c_*.py` and put their outputs in `c_out/`. Do not edit or delete existing
  files. At top level you create only `deep-read-3.md`, your scripts, and part files `c_*.md` if you assemble the report from parts.
- A policy hook guards the shell. It allows only Bash, Read, Glob, Grep, Write, Edit. It blocks: `python3 -c`, `$(...)`, backticks,
  a single `&` anywhere in a command (so no `2>&1`, no background `&`), `curl`/`wget`, sub-agents and every other tool, and any shell
  command that mentions `settings.json`, `guard.py` or `work/loop`. Put code in a file and run `python3 c_something.py args`.
  Plain pipes (`| head`) and `;` are fine. Do not try to work around the hook. Do not start other AI sessions.
- Be honest: say what you saw in the replay (round, coordinates, dragon ids), what you infer (mark it "inference"), and what cannot
  be seen. A replay shows positions, actions, deaths, pearls and sonar rays; not intentions, memory or knowledge.

## The game in ten lines
- Snake-like dragons on a wrapping grid. Kelp (walls) and portals sit on the EDGES between tiles. A dragon sees the 7x7 square around its head.
- Each round every living dragon acts once, in ascending id order. A dragon must MOVE (1 or more steps) or SPLIT; there is no "stay".
- A dragon of length L gets ceil(L/4) free steps per turn; each extra step costs one segment.
- Moving the head into another dragon's HEAD kills both (a ram). Into a body, kelp or itself kills only the mover.
- A dead dragon of length L drops ceil(L/2) pearls on its body cells (head, skip one, next...). Eating a pearl = +1 length.
- Split: a dragon of length 4 or more splits off its rear as a new dragon (child at least 2, parent at least 2). The child's head is the
  old tail, facing the other way. At most 64 dragons per team.
- Pearls: every tile has a hidden spawn interval; a tile with a short interval is a "fountain". A pearl appears only on an empty tile.
  On symmetric maps mirrored tiles spawn together, so both sides get the same supply.
- THE QUEEN is each team's lowest id (0 or 1). The game ends at round 500 or when one team has no dragons. At round 500 the longer
  living queen wins; if equal (both dead), the longest single dragon wins; then total length.

## Tools already here
- `python3 a_open.py <game_id> <team_id> [upto]`: opening economy per 10 rounds for both teams (units, total length, natural and
  corpse pearls eaten, splits, self-kills, other deaths, mean distance of heads from the spawn, natural pearls lying near the spawn).
  `b_open.py`, `b_opentab.py`, `b_pack.py` (sub-session A2) add: non-ram deaths with / without a free cell, cells visited, squares of
  the board with a head in them, parent-child distance after a split. Read their docstrings and outputs in `a_out/`, `b_out/`; copy
  and adapt them under your own `c_` names.
- `python3 digest.py <game_id> <team_id>`, `python3 story.py summary|queen|track|view|events ...` (run `python3 story.py` for usage):
  `view <id> <round> <x> <y> [radius]` draws the board around a cell; `events <id> <r1> <r2> [x y radius]` lists every action in turn order.
- `lib.py`: `lib.Walk(path).run(hooks)` streams a replay with the full board state (every body, every pearl and where it came from,
  kelp and portal edges; `Board.bfs/ball/degree/step`). Checked against the engine on 81,853 steps.
- `games.csv` (one row per game), `timeline.csv` (per game, side and phase bucket: units, total length, cells visited, natural and
  corpse pearls eaten, splits and deaths by length class and cause, rams started, sprints), `q/<id>.json` (per-round units / total /
  longest per side, length histogram every 25 rounds, every ram, every suicide; see `extract.py`).
- Candidate lists, one line per game (size | map | game_id | that team's side | W/L | end type | opponent | opp elo | finals | queen
  fates | rounds): `cand1119.txt` (ours, 427 games vs 2000+ teams), `cand91.txt` (SSS), `cand264.txt` (forgot), `cand306.txt` (Vibing++).
- `out2/gap2_large.txt`, `out2/gap2_medium.txt`, `out2/gap2_small.txt`: the phase tables by team; `out2/lenhist.txt`,
  `out2/splitcls.txt`: units by length class and splits by parent length over time.
- Our bot's source, to link what you see to a rule (use the Read or Grep tool, not the shell):
  `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (toggles are the `constexpr` lines near the top), and the
  author's experiment log `~/01. Project/개인 프로젝트/battlecode/work/plan.md`.

## What the team already knows (do not rediscover; build on it)
- Weak maps: Australia (1 win in 28), Islands (0 in 30), Tower Defense (0 in 24), Around UNSW, Stripes, Slithery Fight, Portals, Trauma.
- Tower Defense: we leave the start room at round ~180 (opponents ~19) because of a "no path back to my tail" penalty and a pull
  towards the map centre that ignores walls. Australia: a 12-cell pocket behind a portal that kills 50–90 of our dragons a game.
  Islands: a 4-cell dead-end corridor where a split child walks in every 6 rounds. These three are known and are being worked on;
  mention them where you meet them but do not make them your result.
- Per dragon we eat about 10% less than strong opponents in rounds 20–60; the unit gap compounds from there.
- Our code stops growth splits of dragons longer than 4 after round 150 on maps over 1,200 cells (`LEADER_GROW_ROUND_BIG`) and after
  round 300 on smaller maps; on large maps our units fall from round 150. A state-based replacement (card #14) changed nothing in
  local games, where our bot reaches 60 units either way.
- We ram much less (large maps, rounds 150–200: 3 rams started per game against 9–12); an "always trade evenly" toggle and a
  far-pearl attraction (`FAR_GAIN 2`, in the live bot) were tried locally. "Stride" (free sprint steps) raised our economy 14% locally
  without more wins. Local games are against our own older bots and do not show what the ladder shows.

## Which games
Work map by map. Mandatory maps: Australia, Islands, Around UNSW, Slithery Fight (large); Trauma and Maze or weakhold (medium);
Tower Defense, Stripes and Portals (small). For each map read:
- two of OUR games (team 1119; we are almost always side A), one typical loss and, if there is one, a win or a close game;
- one or two top-team games on the same map in which the top team has the SAME side letter as we do (same spawn), preferring forgot
  and SSS wins, and if possible a game against the same opponent we lost to (SSS and Vibing++ also play test4, id 19, and
  WeHaveQuizzes, id 87; see `cand91.txt`, `cand306.txt`, `cand264.txt`);
- inside every game of ours, the OPPONENT's side as well: the maps are symmetric, both sides get the same pearls, so our opponent
  in the same game is the cleanest comparison there is.
That is at least 9 maps and about 30 games; most of the work is by script, with board views and event lists where a number needs
explaining. Add all-games counts wherever a claim can be counted on every game (as A2 did with its `b_*.py` scripts).

## What to measure and explain (rounds 0–150 first, then 150–350 on the large maps)
For both sides of every game, per 10 rounds:
1. Units, total length, natural pearls eaten, corpse pearls eaten (own corpses, enemy corpses), natural pearls lying on the board
   and how many of them are nearer to one of our heads than to an enemy head.
2. Deaths by kind: rammed by an enemy, rammed an enemy, non-ram death with no free cell (dead end, crowding: which cell, which
   blocker), non-ram death WITH a free cell (a choice), and the segments lost in each kind.
3. Splits: at what length, how many rounds after reaching 4, how far apart parent and child are 5 and 10 rounds later, where the
   child goes (towards unvisited cells? back along the parent's trail?).
4. Spread: squares of the board (8x8 grid) with one of our heads in them, cells visited so far, mean and maximum distance of heads
   from the spawn, the share of heads within 6 cells of another own head (crowding).
5. Idle and wasted turns: dragons that have not eaten for 20 rounds; dragons that walk a loop of 8 cells or fewer; dragons that
   walk towards a pearl another own dragon reaches first (two heads chasing one pearl); turns spent inside a pocket or dead end.
6. Speed to a pearl: when a natural pearl appears within 6 steps of one of our heads, how many rounds until it is eaten and by whom
   (us, the enemy, nobody for 20 rounds). The same for the opponent.
7. Sprint use: paid steps per 10 rounds, free multi-step moves, and what they were for (a pearl, an escape, a ram).
8. Contact: from the first meeting on, rams made and suffered per 10 rounds, who eats the corpse pearls of each ram, how many of our
   dragons move away from an enemy head they could ram and what that costs (pearls not taken, ground given up).
Then, for the large maps, rounds 150–350: what our dragons of each length class are doing after our round-150 switch (the leader,
the 5–9-longs that no longer split, the 2–4-longs), where our units go (deaths by kind per 50 rounds against new dragons made), where
the enemy's units are relative to our spawn area, and why our natural-pearl intake halves while theirs stays level.

## The questions (answer each with game ids, rounds, counts; say "not seen" where that is the case)
a. Round by round, where does the first gap open: before any contact (pure foraging), at first contact, or later? Give the round
   at which the unit ratio first falls below 0.8 for good in each game, and what happened in the 20 rounds before it.
b. With the same pearls on offer, why do we eat fewer? Rank the causes you can count: fewer dragons, each dragon slower to the
   pearl, dragons in each other's way, dragons lost to dead ends, dragons lost to rams, dragons standing off from enemy heads,
   dragons idle, the queen and other dragons kept back by a rule.
c. Spread. Do our children leave the parent's area? How do forgot, SSS and our opponents send a child away, and how far? Is there a
   visible rule (child goes away from the parent, towards cells no own dragon has visited, along a different axis)?
d. Dead ends and pockets. Count our early non-ram deaths with no free cell against the opponent's in the same game, per map. Do the
   top teams lose as many as we do, more, fewer? Is there any team that avoids the same cell after a team-mate died there?
e. Contact. When enemy small dragons arrive in our area, what do ours do, and what do the top teams' small dragons do in the same
   situation? Count pearls and ground lost per avoided ram if you can.
f. The round-150 switch on large maps. Describe one of our games from round 140 to 220 dragon by dragon (the ones that are 5 or
   longer): what do they do instead of splitting, do they eat, do they die, what happens to the cells they used to cover?
   Compare with what a top team's 5–9-long dragons do in rounds 150–300 (A2: SSS splits at 5 into 2+3 as well; top teams hold 55–60
   units until round 300).
g. Is there anything our opponents WeHaveQuizzes and test4 do in the opening that the top three do not, or the other way round?
   (They are the teams we must beat; they are rated about 2150–2200.)
h. If you could change one general rule in our bot's opening and one in its mid-game (no map names, no map-size conditions), which
   would they be, what in the replays supports them, and what would show they are wrong? Say also which of the ideas already
   tried by the team (list above) your evidence contradicts or supports.

## Output: `deep-read-3.md` (plain English; a teammate must be able to follow it without this brief; explain a term on first use)
1. The three findings that matter most, at the top.
2. A table of games read (id, map, size, which team read, side, opponent, result).
3. Per-map sections: the per-10-round table for our game(s), our opponent in the same game, and the top-team game(s); then what
   the boards and event lists show, with rounds and coordinates.
4. "Answers to the eight questions" with counts, and all-games counts where you made them (name the script and output file).
5. "Us against the top three and against our opponents": one row per behaviour, columns meow / our opponents (WeHaveQuizzes, test4) /
   forgot / SSS / Vibing++, each cell a number or "yes / no / partly" with an example.
6. "What I would change, and what would show it is wrong" (question h).
7. "Where `findings.md`, `deep-read.md` or `deep-read-2.md` look wrong or thin", if you find anything.
8. "Things I could not determine from replays".
Every count quoted in sections 4–6 must come from a script or from a list of game ids and rounds you can show. Finish by printing
the line `SUBSESSION A3 DONE` as your final message.
