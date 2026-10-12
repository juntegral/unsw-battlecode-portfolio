You are sub-session A2 of an overnight study for team meow (id 1119) in the Battlecode "deep-sea dragons" game (unswbc 1.2.7).
Your one job: a CLOSE READ OF THE TWO CROSS-CHECK TEAMS, SSS (team id 91) and "forgot to mention" (team id 264), and a
three-team comparison. Output file: `deep-read-2.md`. Work only in this directory, which is your current directory:
`~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/top1/`

There is no time limit. Depth matters. But a file that is never written is worth nothing: create `deep-read-2.md` after the first
two games and rewrite it after every two more, so that it is always complete for the games read so far.

## Why this read exists
The study asks how the rank-1 team (Vibing++, id 306) wins, to find ONE well-supported idea for our own bot. Sub-session A read 15
Vibing++ games (`deep-read.md`, read it first; it is good and you must not repeat it). The study's rule is: what all three top
teams do is probably a real winning factor; what only one does may be a quirk. So everything A found for Vibing++ has to be
checked on SSS and forgot, and the things those two do differently (they beat Vibing++ about as often as they lose) have to be
described. `findings.md` holds the numbers counted on all 2,343 games; read it too.

## Hard rules
- Read-only towards the outside world: no network, no uploads, no GitHub, no Discord. Do not run games. Never read key or token files.
- Write only inside this directory. Name your own scripts `b_*.py` and put their outputs in `b_out/`. Do not edit or delete existing
  files. The only file you create at top level besides your scripts is `deep-read-2.md` (and part files `b_*.md` if you assemble it).
- A policy hook guards the shell. It allows only Bash, Read, Glob, Grep, Write, Edit. It blocks: `python3 -c`, `$(...)`, backticks,
  a single `&` anywhere in a command (so no `2>&1`, no background `&`), `curl`/`wget`, sub-agents and every other tool, and any shell
  command that mentions `settings.json`, `guard.py` or `work/loop`. Put code in a file and run `python3 b_something.py args`.
  Plain pipes (`| head`) and `;` are fine. Do not try to work around the hook. Do not start other AI sessions.
- Be honest: say what you saw in the replay (round, coordinates, dragon ids), what you infer (mark it "inference"), and what cannot
  be seen. A replay shows positions, actions, deaths, pearls and sonar rays; not intentions, memory or knowledge.

## The game in ten lines
- Snake-like dragons on a wrapping grid. Kelp (walls) and portals sit on the EDGES between tiles. A dragon sees the 7x7 square around its head.
- Each round every living dragon acts once, in ascending id order. A dragon must MOVE (1 or more steps) or SPLIT; there is no "stay".
  The two queens have ids 0 and 1, so both queens always move before every other dragon in the round.
- A dragon of length L gets ceil(L/4) free steps per turn; each extra step costs one segment. "Reach" = ceil(L/4) + (L-2):
  length 2 reaches 1 cell, 3 reaches 2, 4 reaches 3, 5 reaches 5, 6 reaches 6. Eating a pearl on the way gives a segment back.
- Moving the head into another dragon's HEAD kills both (a ram), whatever their lengths. Into a body, kelp or itself kills only the mover.
- A dead dragon of length L drops ceil(L/2) pearls on its body cells. Eating a pearl = +1 length. Teams feed a leader or the queen by
  letting small dragons die next to it. A death with reason `noaction` is a dragon killing itself.
- Split: a dragon of length 4 or more splits off its rear as a new dragon (child at least 2, parent at least 2). The child's head is the
  old tail, facing the other way. A split is the only way to stand still for a turn. At most 64 dragons per team.
- THE QUEEN is each team's lowest id (0 or 1). The game ends at round 500, or earlier if one team has no dragons (wipe-out).
  At round 500: the longer living QUEEN wins (a dead queen counts as 0); if equal (for example both dead), the LONGEST single dragon wins; then total length.
- Sonar: up to 4 rays per turn (N/E/S/W), each carries a 64-bit value to the first dragon it hits. It is the only communication.

## Tools already here
- `python3 digest.py <game_id> <team_id>`: one page from that team's side (phase table, opening, the queen's line every 25 rounds,
  enemy heads that came within 6 steps of her and what happened to them, every queen death with the killer's distance and length
  over the previous rounds, rams by attacker length and sprint length, the leader every 25 rounds, self-kills per 50 rounds, who ate
  what, reverse splits, deaths of dragons 15 or longer, sonar pings). Pass 91 or 264 as the team id.
- `python3 story.py summary|queen|track|view|events ...` (run `python3 story.py` for the usage text): `events <id> <r1> <r2> [x y radius]`
  prints every action with its step directions, every death, split and pearl eaten, in turn order; `view <id> <round> <x> <y> [radius]`
  draws the board (`@` queen of A, `&` queen of B, `A`/`B` heads, `a`/`b` bodies, `*` pearl, `|` `-` kelp, `O` portal).
- Sub-session A's scripts, which take a team id as second argument and work for any team: `a_pack.py <id> <team>` (opening table,
  queen splits, close approaches to the own queen round by round, every queen kill with the killer's track, who could see her, sonar
  rays that ended on the killer, deaths of dragons 15+, long self-kills and who ate them, ram chances not taken),
  `a_open.py <id> <team> [upto]` (opening economy per 10 rounds for both teams), `a_box.py <id> <team>` (what lay on the four cells
  around the queen's head at each of her splits and at her death), `a_check.py`. Read their docstrings; copy and adapt them under
  your own `b_` names if you need changes. Their outputs for A's games are in `a_out/`.
- `sonarpeek.py <id> [A|B] [max]`: raw sonar pings.
- `lib.py`: `lib.Walk(path).run(hooks)` streams a replay with the full board state. Checked against the engine on 81,853 steps.
- Per-game extracts for all 2,343 games: `q/<id>.json`, `q2/<id>.json`, `q3v2/<id>.json` (turn-level chances on the enemy queen:
  list `chances`, each = [round, side, dragon id, its length, steps needed, taken 0/1, her length, attacker is its team's longest 0/1,
  attacker's own queen alive 0/1, her head in the attacker's view 0/1]); field descriptions are in the docstrings of `extract.py`,
  `extract2.py`, `extract3.py`.
- `games.csv` (one row per game), `timeline.csv`, and the candidate lists `cand91.txt` (SSS, 534 games vs 2000+ teams) and `cand264.txt`
  (forgot, 670 games), one line per game: size | map | game_id | that team's side | W/L | end type | opponent | opp elo |
  final own units/total/longest/queen | same for opp | own queen fate | opp queen fate | rounds.
- `out2/*.txt`: raw outputs of the lead's counting scripts on the current snapshot.

## Which games
Read at least 7 SSS games and at least 7 forgot games closely (more is welcome). Per team: at least 4 large-map games, at least 1
medium, at least 1 small, at least 3 losses. Prefer games that do NOT involve Vibing++ (A read those from the Vibing++ side); games
between SSS and forgot count for both teams if you read both sides. Not Schooltime (queens are sealed there).

Mandatory, SSS:
- 1059834 Around UNSW, W vs forgot, queen rule: SSS queen alive at 36, forgot's queen rammed at round 72.
- 1063806 Slithery Fight, W vs forgot, both queens alive 86 vs 62.
- 1060000 Slithery Fight, L vs Kaizen, queen rule: SSS queen rammed at round 479 by an 18-long.
- 1059840 Australia, L vs forgot, longest 27 vs 79 (SSS queen rammed at round 157).
- 1060356 Australia, W vs bread first search, queen rule with a 3-long queen.
- 1067641 Islands, L vs forgot, longest 37 vs 63 while SSS ends with 41 units and total 237.
Mandatory, forgot (some overlap with the SSS list on purpose; read forgot's side there):
- 1067654 Australia, L vs Sponge, longest 41 vs 105.
- 1063814 Around UNSW, L vs Sponge, queen rule: forgot's queen rammed at round 34.
- 1067667 Around UNSW, W vs bread first search, both queens alive 53 vs 36.
- 1067636 Maze, W vs SSS, queen rule with a 66-long queen; 1067446 Maze, W vs bread first search, both queens alive 108 vs 91.
- 1067620 Australia (forgot beat Vibing++; forgot had 62 units at round 100 against 9): read forgot's opening, rounds 0–120.
Pick the rest from the candidate lists (small maps: Portals, Tower Defense, Devil, Stripes, Prisoners Dilemma, Trophy; medium:
Autarky, Default, Queen Of Spades, Trauma, Maze, weakhold).

## What to extract from each game (follow that team's queen and its 2–3 most important dragons)
1. Opening (rounds 0–60): units and natural pearls eaten per 10 rounds (`a_open.py`), when and at what length dragons split, what
   the queen does, self-kills, first contact.
2. Mid-game: who rams whom (length, steps), what happens to enemy heads near the queen.
3. Queen routine: where she is, how long, how much she moves, allies near her, every round in which an enemy head is within 3
   steps (what she does, what allies do), every split and what surrounded her head (`a_box.py`), how she dies or survives.
4. Late game: who is fed (queen or another dragon), from which round, how; how the leader is protected or lost.
5. Kills of the enemy queen and of enemy leaders: the killer's track (where it was 20, 10, 5 rounds before, what it ate, whether
   she was in its view, whether it was a fresh split child).
6. The decisive moment, with round and coordinates.

## The questions (answer each for SSS and for forgot, with game ids, rounds and counts; say "not seen" where that is the case)
1. **Ram when in view.** On all games (`findings.md`, section 3): when a dragon has a free path to the enemy queen's head within its
   reach AND she is inside its 7x7 view, Vibing++ rams in 266 of 267 turns and SSS in 250 of 254, at any length and any cost.
   forgot rams in only 254 of 457 (70% with a 2–3-long attacker, 23% at length 4, 32% at 5–9, 0 of 22 at 10–12; 70% when it costs
   nothing, 25% when it costs 2 segments). Find, with `q3v2`, the in-view chances forgot did NOT take in the games you read (and more
   games if needed, at least 20 such turns) and work out its rule: cost, attacker length, own queen alive or dead, an ally about to
   do it, the attacker being fed or feeding, something else? Also confirm SSS on a few turns, including the 4 it did not take.
2. **How hunters find her.** A saw Vibing++ hunters walk 14–29 steps to a queen nobody had in view, three of seven being fresh
   split children. For SSS (64% of its large-map queen kills are by a dragon 5 or longer, 61% with a 4–5-step sprint) and forgot
   (mostly 2–3-long killers; A saw forgot's small dragons follow a queen for 30–110 rounds until a second one arrives): describe
   each queen kill you read the same way. Is forgot's "follower" a role (one dragon that stops eating and stays 2–5 steps behind
   her)? Does anything suggest a call for help (sonar rays from the follower ending on the later killer)?
3. **A boxed-in queen.** Vibing++: a queen of 4+ with no free neighbour cell splits just in front of the own segment touching her
   head (usually leaving her 3 long, 85 -> 3 in one game); a 2–3-long one dies. A saw forgot's queen shed 2 from her tail every
   round for 16 rounds instead (42 -> 10). Check every queen split and queen death of SSS and forgot in your games with
   `a_box.py`: what do they do with no free neighbour, and how do their queens get into that state (or avoid it)? SSS queens die
   by their own body or another body in 8% of games and never by `noaction`; forgot's die by `noaction` in 8%.
4. **How does SSS keep its queen alive?** SSS has the best queen survival of the three (41% alive at the end; Vibing++ 27%, forgot
   36%). The numbers: SSS's queen is 2–3 long, has as many allies near her as the average SSS dragon and about half as many enemy
   heads within 8 cells; with three or more allies near, intruders are rammed by an SSS dragon in 27% of approaches; on small maps
   she uses 10 cells or fewer in 29% of 25-round windows. In the games you read: is she steered (towards allies, away from enemy
   sightings, back to a home area), or does she simply forage like the others? What happens round by round when an enemy comes
   within 3 steps? Do allies react to the intruder or to her?
5. **Feeding and the end game.** When does each team start feeding, whom (queen or another dragon), and what decides it? forgot
   ended one game as a single 73-long dragon; in A's games forgot put 44–100% of its length into one dragon and Vibing++ 21–39%.
   Which dragon becomes the leader, how do feeders reach it, how many segments are lost on the way (a corpse gives back half)?
   What does each team do with a queen that is alive at round 300–400: feed her, hide her, both?
6. **Leaders: kept alive or lost.** How are leaders of 15+ lost and how are enemy leaders killed (A: a 2–4-long from the next
   cell, often out of a portal or as a split child; "split first, then ram with the cheap part")? Do SSS and forgot use the split trick?
7. **Openings.** For every game read, the per-10-round table for rounds 0–100 (units, natural pearls eaten, self-kills, splits) for
   both sides. forgot out-ate Vibing++ 2–4 to 1 in rounds 40–90 in five of A's games. What does forgot do in those rounds that
   Vibing++ (and SSS) does not: split timing and length, where the children go, how far they spread, sprinting to pearls,
   self-kills, how they treat dead ends and small rooms? A separate sub-session will go deep on the economy; here record what you see.
8. **What do they do that Vibing++ does not, and the other way round?** For example: Vibing++ makes small dragons kill themselves
   from round 0 and reverse-splits long dragons all the time; SSS has no `noaction` deaths at all in its openings; forgot uses the
   suicide action. Do these differences matter for results anywhere you can see?

## Output: `deep-read-2.md` (plain English; a teammate must be able to follow it without this brief; explain a term on first use)
1. The three findings that matter most, at the top.
2. A table of games read (id, map, size, team read, opponent, result, end type, both queens' fates).
3. Per-game notes with the six headings above, short and concrete (rounds, coordinates, ids, lengths), each ending with
   "Decisive moment: ...".
4. "Answers to the eight questions", for SSS and for forgot separately, with counts ("seen in 5 of 7 queen kills").
5. **The three-team table**: one row per behaviour (use A's list in `deep-read.md` for Vibing++ and add what you find), columns
   Vibing++ / SSS / forgot, each cell "yes / no / partly" with a count and one example (game id, round). Then two short lists:
   "what all three do" and "what only one or two do".
6. "What the losses of SSS and of forgot have in common" (their weaknesses), with counts.
7. "Where `deep-read.md` or `findings.md` looks wrong or thin", if you find anything.
8. "Things I could not determine from replays".
Every count quoted in sections 4–6 must come from a script or from a list of game ids and rounds you can show. Finish by printing
the line `SUBSESSION A2 DONE` as your final message.
