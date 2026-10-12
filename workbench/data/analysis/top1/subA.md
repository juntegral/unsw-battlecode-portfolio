You are sub-session A of an overnight study for team meow (id 1119) in the Battlecode "deep-sea dragons" game (unswbc 1.2.7).
Your one job: READ 13–15 REPLAYS CLOSELY and write `deep-read.md`. Work only in this directory, which is your current directory:
`~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/top1/`

Time: you have about 55 minutes of wall-clock time (hard stop 65). Depth matters more than breadth, but an unfinished file is worth
nothing: create `deep-read.md` after the first two games and rewrite it after every two more, so that it is always complete for the
games read so far. If time runs short, read fewer games; do not drop the "Recurring patterns" section.

## Hard rules
- Read-only towards the outside world: no network, no uploads, no GitHub, no Discord. Do not run games. Never read key or token files.
- Write only inside this directory. Name your own scripts `a_*.py`. Do not edit or delete existing files (lib.py, story.py, digest.py,
  extract*.py, q/, q2/, q3/, dg/, run1/, *.csv, other *.md). The only existing file you replace is `deep-read.md`.
- A policy hook guards the shell. It allows only Bash, Read, Glob, Grep, Write, Edit. It blocks: `python3 -c`, `$(...)`, backticks,
  a single `&` anywhere in a command (so no `2>&1`, no background `&`), `curl`/`wget`, sub-agents and every other tool, and any shell
  command that mentions `settings.json`, `guard.py` or `work/loop`. Put code in a file and run `python3 a_something.py args`.
  Plain pipes (`| head`) and `;` are fine. Do not try to work around the hook. Do not start other AI sessions.
- Be honest: say what you saw in the replay (round, coordinates, dragon ids), what you infer, and what cannot be seen.
  A replay shows positions, actions, deaths, pearls and sonar rays. It does NOT show a bot's intentions, its memory or what it knew.

## The game in ten lines (so you read replays correctly)
- Snake-like dragons on a wrapping grid. Kelp (walls) and portals sit on the EDGES between tiles. A dragon sees the 7x7 square around its head.
- Each round every living dragon acts once, in ascending id order. A dragon must MOVE (1 or more steps) or SPLIT; there is no "stay".
  The two queens have ids 0 and 1, so both queens always move before every other dragon in the round.
- A dragon of length L gets ceil(L/4) free steps per turn; each extra step costs one segment. Most it can move in one turn ("reach")
  = ceil(L/4) + (L-2): length 2 reaches 1 cell, 3 reaches 2, 4 reaches 3, 5 reaches 5, 6 reaches 6. Eating a pearl on the way gives a segment back.
- Moving the head into another dragon's HEAD kills both ("head-on", a ram), whatever their lengths. Into a body, kelp or itself kills only the mover.
- A dead dragon of length L drops ceil(L/2) pearls on its body cells. Eating a pearl = +1 length. Teams feed a leader by letting small
  dragons die next to it. A death with reason `noaction` is a dragon killing itself (an order it cannot carry out, or the suicide action).
- Split: a dragon of length 4 or more splits off its rear as a new dragon (child at least 2, parent at least 2). The child's head is the old tail,
  facing the other way. A split is the only way to stand still for a turn. At most 64 dragons per team.
- THE QUEEN is each team's lowest id (0 or 1). The game ends at round 500, or earlier if one team has no dragons (wipe-out).
  At round 500: the longer living QUEEN wins (a dead queen counts as 0); if equal (for example both dead), the team with the LONGEST single
  dragon wins; then total length.
- Sonar: up to 4 rays per turn (N/E/S/W), each carries a 64-bit value to the first dragon it hits. It is the only communication.

## Tools already here (use them; write more if you need)
- `python3 digest.py <game_id> [team_id]` (default team 306): one page from that team's side: phase table every 50 rounds (units, total
  length, top-3 lengths, queen length), opening (first contact, first splits, queen splits), the queen's line every 25 rounds (position,
  length, openness "ball" = cells within 4 steps, 41 = open field; distance from spawn "home"; enemy heads within 8 steps; allied heads
  within 6; different cells used in the last 25 rounds), enemy heads that came within 6 steps of her and what happened to them, every queen
  death with the killer's distance and length over the previous rounds, rams by attacker length and sprint length, the leader every 25
  rounds from round 200, self-kills per 50 rounds and how many were next to the leader or the queen, who ate what, "reverse" splits, deaths
  of dragons 15 or longer, sonar pings per 100 rounds. Ready-made digests of the 15 games of the first pass are in `dg/<game_id>.txt`.
- `python3 story.py summary <game_id>`: table every 25 rounds for both teams, queen logs, splits / self-kills / rams per 50 rounds, biggest dragons.
- `python3 story.py queen <game_id> <A|B> [every]` and `python3 story.py track <game_id> <id,id,...> [every]`: a dragon's line every N rounds:
  head, length, openness, enemy heads within 8 steps (distance, length, id), allied heads within 8. With every <= 2 it also prints corpse pearls eaten.
- `python3 story.py view <game_id> <round> <x> <y> [radius]`: ASCII board around a cell at the START of that round (`@` queen of A, `&` queen
  of B, `A`/`B` other heads, `a`/`b` bodies, `*` pearl, `|` `-` kelp, `O` portal; rows are y, columns x, the board wraps).
- `python3 story.py events <game_id> <r1> <r2> [x y radius]`: every action (with its step directions), death, split and pearl eaten in a
  round range, in turn order, optionally only near a cell. This is the tool for "what exactly happened in rounds 440–448".
- `python3 sonarpeek.py <game_id> [A|B] [max]`: raw sonar pings (sender, start and end point of each ray, 64-bit value). Values are packed;
  you can see who pings, how often and which rays end on a dragon, not what they say.
- `lib.py`: `lib.Walk(path).run(hooks)` streams a replay and keeps the full board (every body, every pearl with its origin). See the `Hooks`
  class and how `story.py` / `digest.py` use it. `Board.step/bfs/ball/degree` respect kelp, wrap and portals. Checked: it predicts
  81,853 of 81,853 real move steps in four test games and reproduces the metrics CSV with 0 differences in 1,064 values.
- Per-game extracts for all 2,343 games: `q/<id>.json` (per-round queen record, queen death with killer, "approach" episodes = enemy heads
  that came within 6 steps of a live queen and how each ended, every ram, every suicide; fields in the docstrings of `extract.py` and
  `qan.py`), `q2/<id>.json` (killer tracks for queen and leader kills, leader exposure, queen vs team surroundings; `extract2.py`),
  `q3/<id>.json` (turn-level "chances": turns on which a dragon had a free path to the enemy queen's head within its reach, and whether it
  rammed; `extract3.py`).
- `games.csv` (one row per game: map, size, teams, elo, winner, end_type = wipe-out / queen rule / longest / total), `timeline.csv`.
- `cand306.txt`: every game of the protagonist against opponents rated 2000+, one line each:
  size | map | game_id | protagonist's side | W/L | end type | opponent | opp elo | final own units/total/longest/queen | same for opp |
  own queen fate | opp queen fate | rounds. (537 games, refreshed at 04:16.)

## Who to follow
Protagonist = **Vibing++ (team id 306)**, rank 1 by the latest elo in the collected games (2309). The two cross-check teams are
**"forgot to mention" (264, elo 2306)** and **SSS (91, elo 2297)**. Head to head: 306 beat 91 in 41 of 79 games and 264 in 63 of 112.
In each game, find which side (A or B) is 306 from the header line the tools print. Vibing++ vs 2000+ teams: 341 wins in 537 games
(large maps 102/162, medium 110/147, small 129/228).

## Which games
Read at least 13. The mandatory block comes first. End with at least 7 large-map games, at least 3 medium, at least 3 small, and at
least 6 protagonist losses. You may swap a listed game for another from `cand306.txt` if it turns out uninformative; say so.

Mandatory, new since the lead's first pass (nobody has read these):
- 1063780 Around UNSW, W vs forgot, queen rule: own queen alive at 28 on an open big map, forgot's queen rammed at round 34.
- 1069168 Islands, W vs tungtung67, queen rule: own queen alive at 29; enemy queen rammed at round 223 by an 11-long.
- 1067620 Australia, L vs forgot, queen rule: own queen rammed at round 178 by a 9-long that sprinted 6 steps; forgot's queen ends 39 long.
- 1063789 Slithery Fight, L vs forgot, queen rule with BOTH queens alive (4 vs 50).
- 1067623 Slithery Fight, L vs forgot, longest 75 vs 83 although Vibing++ ends with 59 units and total length 364.
- 1064500 Around UNSW, W vs horse, longest 88 vs 82; own queen rammed at round 333 by a 22-long.
Mandatory, read by the lead in the first pass with the digest tool only; read them yourself with `events` and `view` and say where the
lead's note in `run1/deep-read.md` is wrong or thin (do not copy it):
- 1052703 Islands, L vs SSS: the lead says Vibing++ split and killed its own living 16-long queen at rounds 262–263, and lost a 69-long leader at round 426.
- 1056036 Australia, W vs SSS: the lead says a queen kill at round 472 and a leader kill at round 479 decided it.
Pick from (medium): 1067619 Maze L vs forgot (longest 68 vs 73); 1063792 Trauma L vs forgot (both queens alive, 35 vs 48);
  1064508 Trauma W vs horse (both alive, 32 vs 23); 1063791 Autarky L vs forgot (wiped at round 330); 1067625 Autarky W vs forgot;
  1047092 Maze L vs horse (queen rule).
Pick from (small): 1063783 and 1067617 Portals L vs forgot (queen rule; own queen dies by `noaction` at round 131–132);
  1063793 Tower Defense L vs forgot (wiped); 1067622 Prisoners Dilemma L vs forgot; 1064507 Devil L vs horse; 1063784 Devil W vs forgot;
  1067612 Stripes W vs forgot.
Contrast, optional and last (two of OUR games, team 1119 = meow; use `python3 digest.py <id> 1119`): 1029030 Autarky, loss to WeHaveQuizzes on
  the queen rule against a lone 2-long queen; 1053784 Trauma, loss to WeHaveQuizzes with both queens alive (31 vs 39).
Do not spend a game on Schooltime: both queens are sealed in a tiny room there and always end 3 long.

## What to extract from each game (follow the protagonist's queen and its 2–3 most important dragons)
1. Opening (rounds 0–50): how it expands, when and at what length dragons split (the queen too), how it leaves the start area, first contact.
2. Mid-game (50–300): unit growth, how it treats contact. For enemy heads that come close: does a protagonist dragon ram them, avoid
   them, box them in? Who rams (length, how far it sprinted, was it already next to the enemy or did it travel)?
3. Queen routine: where she stays (distance from spawn, open field / corridor / dead end / near a portal), how long she is, how much she
   moves, whether allies stay near her, when she grows, how she dies or survives. When an enemy comes within about 6 steps of her,
   describe the next 10 rounds move by move (`events`), including what she did and what the nearest allies did.
4. Late game (300–500): who feeds whom and where, how the feeders die, how far the leader moves to collect, whether the leader
   "reverses" by splitting (a long parent keeps 2 segments, the child gets the rest), how the leader is protected, how sprint is used,
   who goes for the enemy leader and the enemy queen.
5. The decisive moment: the event or stretch that decided the game, with round and coordinates. Say what the result would have been without it if the numbers allow.
6. Roles: do dragons behave differently by length or position (for example 2–3-long ones ram heads, 5–9-long ones sprint at queens and
   leaders, the longest plays safe)? Evidence with counts, not guesses.
7. Sonar: who pings, how often, do rays end on allies; anything that looks like a relayed target (several dragons turning towards the
   enemy queen within a few rounds of a sighting).

## Questions the numbers could not answer (the reason for a close read; answer each with game ids and rounds, or say "not seen")
The lead's first pass measured these on 1,754 games; treat them as leads to test against what you see, not as verdicts.
a. **How does a hunter get to the enemy queen?** In the numbers, top-team dragons ram the enemy queen in 58–80% of large-map games; the
   killer is 5 or more long in 46% of large-map kills and starts the fatal round 4 or more steps from her in 86% of those. In each queen
   kill you read: where was the killer 20, 10, 5 rounds before; did it head for her from far away or was it feeding nearby; had it (or an
   ally whose sonar ray could reach it) seen her before; did it grow first? Is there a designated hunter or does any dragon take the chance?
b. **Do they always ram when they can?** Turn-level count: with a 2–3-long dragon that has a free path to the enemy queen's head within its
   reach, Vibing++ and SSS ram in 98% of such turns, forgot in 67%, we in 36%. Find 3–4 turns where a protagonist dragon had such a chance
   and did NOT take it (`q3/<id>.json`, list `chances`, each entry = [round, side, dragon id, its length, steps needed, taken 0/1,
   her length, attacker is its team's longest 0/1, attacker's own queen alive 0/1]) and say what it did instead and what was different about the situation
   (cost in segments, our own queen alive or not, an ally in the way, the attacker being the longest dragon).
c. **Why do some queens live on open big maps?** In the first snapshot nearly every queen died on Around UNSW, Australia and Islands. In
   1063780, 1069168 (and 1062216, 1065203 if you have time) the Vibing++ queen lives to the end. What is different in those games: where
   she is, how long she is, who is near her, what happened to enemies that came close, or simply that the opponent never looked for her?
d. **What does the queen do in the round an enemy gets close?** Step away, sprint, split, nothing? Does any ally react (ram the intruder,
   move between)? The numbers say allies near a top-team queen ram 24–27% of small intruders (ours 13%), and that once a small enemy is 2–3
   steps away a top-team queen dies about as often as ours.
e. **How do queens avoid killing themselves?** Our queen dies by her own move (kelp, a body, her own body) in 28% of our games, almost
   always with no free neighbour cell and no enemy near; top-team queens in 4–12%. When the protagonist's queen is in a tight spot (few
   free cells, allies around), what does she do: split to stand still, loop on a 2x2 block, keep to open water? Also note how the
   protagonist handles a queen that starts long (Slithery Fight: 25 long at round 0).
f. **When is the queen fed, and when is she thrown away?** The lead saw Vibing++ feed its queen only in games where no enemy ever came near
   her, and saw it kill its own queen by a reverse split (1052703) or by `noaction` (Portals games above, small maps). What decides it?
g. **The leader in the last 100 rounds:** how is it kept alive, and how does it die (a 2–4-long from the next cell, a long sprinter)?
   The numbers: the side that alone rammed the other's 20+ long leader after round 400 won 51 of 55 round-500 "longest" games.
h. **Openings lost:** 5 of the 9 protagonist losses the lead read were lost by round 100 (far fewer units). What goes wrong in the first
   60 rounds of the losses you read, compared with the wins on the same map?

## Output: `deep-read.md` (plain English; a teammate must be able to follow it without this brief)
1. A table at the top: games read (id, map, size, opponent, result, end type).
2. Per-game notes, one section per game, with the seven headings above. Short and concrete: rounds, coordinates, ids, lengths.
   End each with one line: "Decisive moment: ...".
3. "Answers to the eight questions" (a to h), each with the games and rounds that support it and a count ("seen in 5 of 7 queen kills").
4. "Recurring patterns": each as one sentence, then the count ("seen in 9 of 13 games; not seen in: ids"), the best two examples
   (game id, round), and whether it is something the protagonist DOES or something that HAPPENS to it. Keep patterns in wins and in losses apart.
5. "What the protagonist's losses have in common" (its weaknesses), with counts.
6. "Where the lead's first notes were wrong or thin" (the two re-read games).
7. "Things I could not determine from replays".
Explain any term on first use; no lab jargon. Finish by printing the line `SUBSESSION A DONE` as your final message.
