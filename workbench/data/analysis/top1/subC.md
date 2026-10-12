You are sub-session C ("Red team") of a study for team meow (id 1119) in the Battlecode "deep-sea dragons" game (unswbc 1.2.7).
Your one job: try to BREAK the candidate hypotheses in `hypotheses.md`, by recounting from the replays yourself and by looking for
everything that could make them wrong, weaker than claimed, or harmful. Output file: `redteam.md`.
Work only in this directory, which is your current directory:
`~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/top1/`

There is no time limit. Depth matters. But a file that is never written is worth nothing: create `redteam.md` as soon as the first
candidate has been attacked and rewrite it after each further one, so that it is always complete for what has been done so far.
(A file of that name from an earlier run exists; replace it. Do NOT read or rely on `run1/redteam.md` or on the old top-level
`redteam.md`: they attack an older set of hypotheses with older data, and your result must stand on your own recount.)

## Where the study stands
The study asks how the rank-1 team (Vibing++, id 306) and the two teams level with it (SSS, id 91; "forgot to mention", id 264) play
against teams rated 2000+, to find ONE excellent, well-supported hypothesis for our bot, which the team will then build and test
as one "card". Four close reads (`deep-read.md`, `deep-read-2.md`, `deep-read-3.md`, `deep-read-4.md`), the lead's fact sheet
(`findings.md`) and sub-session B's `hypotheses.md` exist. B proposes four candidates and picks the first:
1. **Take the queen**: any dragon of ours with the enemy queen's head in view and in reach rams her, at any length (claimed +1.5 to
   +3.2 points of win rate; switch `QUEEN_HUNT` plus one condition).
2. **Our queen is never spent**: she never ends a move inside a visible enemy's reach when another move exists, never rams, sheds 2
   instead of cutting herself to 2 when boxed in (+0.9 to +2.8).
3. **No leader before its time**: the leader rules (pearls left for the leader, split stop) start at the same round on every map
   (+0.4 to +1.5).
4. **Do not give way at contact**: a small dragon that is not outnumbered rams any small enemy head it can reach (0 to +2.4).
B also says 1 and 2 are two sides of one idea (+3.1 to +5.3 together) and lists what it did not propose (feeding earlier, among others).
After you, the lead decides: one hypothesis, or "none survives". An honest "this does not hold" is worth more than a polite pass.

Read `hypotheses.md` completely first, then `findings.md`, then the parts of the four deep reads each candidate leans on.

## Hard rules
- Read-only towards the outside world: no network, no uploads, no GitHub, no Discord. Do not run games. Never read key or token files.
- Write only inside this directory. Name your own scripts `x_*.py` and put their outputs in `x_out/`. Do not edit or delete existing
  files except `redteam.md`, which you replace. At top level you create only `redteam.md`, your scripts, and part files `x_*.md` if
  you assemble the file from parts.
- A policy hook guards the shell. It allows only Bash, Read, Glob, Grep, Write, Edit. It blocks: `python3 -c`, `$(...)`, backticks
  (also inside a heredoc), a single `&` anywhere in a command (so no `2>&1`, no background `&`), `curl`/`wget`, sub-agents and every
  other tool, and any shell command that mentions `settings.json`, `guard.py` or `work/loop`. Put code in a file and run
  `python3 x_something.py args`. Plain pipes (`| head`) and `;` are fine. Do not try to work around the hook. Do not start other AI
  sessions.
- **Recount, do not re-read.** For every number a candidate's case rests on, write your OWN script that walks the replays (or, where
  the claim is about a derived file, rebuild the derived quantity from the replay for a sample and compare). Do not import or copy
  the counting logic of `extract3.py`, `an4*.py`, `recount3.py`, `d_*.py`, `h_*.py`; you may use `lib.py` (the replay walker, checked
  against the engine on 81,853 steps) and `games.csv`, and you may READ the other scripts to find out exactly what they counted, so
  that a difference between your number and theirs can be explained. Say for every recounted number: theirs, yours, and why they
  differ if they do.
- Be honest about uncertainty: measured (script, file), inferred, or not visible in replays. A replay shows positions, actions,
  deaths, pearls and sonar rays; not intentions, memory or scores.

## The game in ten lines
- Snake-like dragons on a wrapping grid. Kelp (walls) and portals sit on the EDGES between tiles. A dragon sees the 7x7 square around its head.
- Each round every living dragon acts once, in ascending id order, so both queens (the lowest id of each team) move before every
  other dragon. A dragon must MOVE (1 or more steps) or SPLIT; there is no "stay".
- A dragon of length L gets ceil(L/4) free steps per turn; each extra step costs one segment. Most steps in a turn ("reach"):
  1, 2, 3, 5, 6 for lengths 2, 3, 4, 5, 6.
- Moving the head into another dragon's HEAD kills both (a ram). Into a body, kelp or itself kills only the mover.
- A dead dragon of length L drops ceil(L/2) pearls on its body cells. Eating a pearl = +1 length.
- Split: a dragon of length 4 or more splits off its rear as a new dragon (child at least 2, parent at least 2). The child's head is the
  old tail, facing the other way. At most 64 dragons per team.
- The game ends at round 500 or when one team has no dragons. At round 500 the longer living queen wins (a living queen of any
  length beats a dead one): the "queen rule". If equal (both dead, or the same length), the longest single dragon wins: the
  "longest rule". Then total length.

## Data and tools
- `games.csv`: one row per game (map, cells, teams, elo, winner, end type, replay path, `battle_id`). 2,343 games: 1,637 of the top
  three and 706 of ours, of which 401 are against teams rated 2000+ with the map Schooltime left out (both queens are sealed in a
  room there). Our 401 games are eleven runs (`battle_id`): ladder downloads `dl-20261003`, `dl-20261004` and the "-old" halves of
  smoke pairs = the live bot (275 games); the "-new" halves = test builds stride, passage2, qh31, tc30 (126 games). 313 of the 401
  are against two teams, test4 (id 19) and WeHaveQuizzes (id 87).
- `lib.py`: `lib.Walk(path).run(hooks)` streams a replay with the full board state: every body, every pearl and where it came from,
  kelp and portal edges, `Board.bfs/step/nb/cheb/manhattan`, hooks `round_start, action, moved, split, death, eat, sonar, end`
  (read its source: 260 lines). About 1.3 s per game; use `multiprocessing.Pool` with at most 5 workers and `os.nice(10)`.
- `python3 story.py` (usage when run without arguments: `summary`, `queen`, `track`, `view`, `events`) and
  `python3 digest.py <game_id> <team_id>` show single games; use them to look at cases with your own eyes.
- Our bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (Read or Grep tool, not the shell). The test builds'
  sources: `../../online/smoke/qh31-bot/main.cpp`, `tc30-bot`, `qn23-bot`.
- The team's records (Read tool): the author's experiment log `~/01. Project/개인 프로젝트/battlecode/work/plan.md`
  (every toggle tried locally and what came of it; version notes such as "QUEEN_HUNT off since v55"),
  `~/01. Project/개인 프로젝트/battlecode/docs/LOOP.md` (how a card is tested), and the online smoke-test records in
  `../../online/smoke/` (`*-result.txt`, `qh31-analysis/`, `qn23-analysis/`, the `*.log` files).

## What to attack, for EVERY candidate (and hardest for candidate 1 and for the pair 1 + 2)
A. **The counts.** Recount the behaviour gap itself (for candidate 1: turns on which a non-queen dragon has the enemy queen's head in
   its 7x7 view and a legal path to it within its reach at the start of its own turn, and whether it rammed; for 2: queen turns
   that end inside a visible enemy's reach although a safe step existed, and her deaths on such turns; for 3: free pearls beside a
   small dragon taken or not, before and after round 150 and 300 by map class, and the split and length curves around the switch;
   for 4: meetings and rams by local head count). Do the definitions hide anything? Are "chances" really executable by a bot that
   knows only what it sees (does it know that head is the queen; would its own path search call the path free; does the model's
   treatment of bodies that move between turns matter)? Check a sample of at least 15 cases per candidate by eye with `story.py`.
B. **Cause or consequence.** The side that is winning is near the enemy queen more often, has more dragons near its own queen, eats
   more. For each candidate find a comparison that removes this: the same team at the same economy (own / enemy total length at
   the round of the event), the same opponents, the protagonist's wins against its own losses, and above all natural
   experiments. For candidate 1, forgot is one: it takes only 56% of its in-view chances. Compare forgot's games in which the first
   chance was taken with those in which it was not, at the same round band and economy band: does taking it change how the game
   ends? Do the same inside our own games (first chance taken or not) and for every other team with enough chances. Does a team's
   take-up rate go with its rating across ALL teams in the data, or do weak teams take the ram just as often?
C. **What happens next.** B's "strict" reading changes one event and keeps the rest of the game. Measure what really follows the
   event in games where it did happen: after an enemy queen is rammed at round R with economy E, how do such games end, compared
   with games at the same R and E in which she lived? What does the team that lost its queen do (longer leader, hunts our queen,
   nothing)? What happens to the side that spent a dragon of 5 or more on the ram? For candidate 2: how long does a queen live
   after a safe step, and what kills her then? For 3 and 4: where the economy did rise (the tc30 build, "stride"), why did wins
   not follow, and does the candidate avoid that?
D. **Sample size.** Give a plain range for every key share (for instance an 80% interval), and say for every "N games flip" how
   many of those games rest on a single run, a single map or a single opponent. 313 of our 401 games are against two teams: does
   each claim hold against test4 and WeHaveQuizzes separately, and is there any sign it holds against the stronger teams we
   must beat at the qualifier (our few games against the top three; the top three's games against each other)? How often does a
   TOP team's queen offer an in-view chance at all, compared with test4's and WeHaveQuizzes's?
E. **Cross-team.** Does each of the three top teams really do it? Where one does not (forgot does not ram queens with long dragons;
   Vibing++ cuts its boxed-in queen as we do; SSS and forgot differ on feeding), is that team worse for it in the games where it
   matters, or just as good? Is there a team rated 2000+ that does the opposite and does well?
F. **Contradiction with earlier experiments.** Read `work/plan.md` and the smoke records for every trial that touches the candidate:
   why was `QUEEN_HUNT` switched off after v54, and on what numbers; what did the local queen-hunt variants ("H4", "QS0PH" and
   others), the queen-protection toggles, the leader-round and feed-round variants, the "trade evenly" and trade-on-contact
   variants give; what did the online trials qh31, tc30, qn23, stride and passage2 give, pair by pair? For each: does it
   contradict the candidate, is it too small to say, or did it test something else? Recount the online trials' mechanism numbers
   from their replays (they are in `games.csv` under their `battle_id`) rather than quoting the team's summaries.
G. **Backfire.** The team's cautionary tale is a change that let short dragons through narrow passages and got our queen killed
   online. For each candidate: construct the ways it could lose games (long dragons or the leader spent on a queen kill that does
   not decide the game; hunters abandoning a fight; a queen that refuses a pearl starving the opening; a queen fleeing into a dead
   end or away from her team; more rams made while outnumbered; a later leader losing the longest-dragon race), then COUNT how often
   the losing situation occurs in played games, ours and the top three's. For candidate 1 in particular: in how many of our wins
   would the rule have fired and spent a dragon we needed; in how many games would our own queen (on maps where the bot does not
   treat her as queen) or our longest dragon have been the attacker; what does Vibing++ or SSS lose when its leader rams a queen?
H. **The code claim.** Read the functions each candidate says it changes. Does the switch do what B says and only that (for
   candidate 1: `mark_hunt_targets()`, `hunt_path()`, the call in `act()`, how `enemy_queen_id` is found and whether it can be wrong,
   what `enter_time` counts as blocked)? Is anything else switched on with it? Is there a hidden map-size or map-name condition
   left in any candidate (the final hypothesis must be a general rule: game state or terrain only)?
I. **The footing.** B puts all candidates on "points of win rate" from strict and realistic readings and band win rates. Attack the
   footing itself: band rates on few games, overlaps counted twice, the claim that economy is the larger gap but has no ready
   rule, the ranking. Would a different, defensible footing reorder the candidates? Is anything under "Not proposed, and why"
   dismissed too quickly (earlier feeding of the longest dragon, keeping the queen near her team, defenders near the queen)?

## Output: `redteam.md` (plain, casual, clear English; explain every term on first use; a teammate must be able to follow it alone)
1. **Verdicts in one table**, at the top: candidate, verdict ("holds", "holds, weaker than claimed", "does not hold", "cannot be told"),
   B's claimed range, the range you would defend, the single strongest objection, and what would settle it.
2. **Per candidate**: each attack A to I that applies, with what you counted (script and output file), theirs against yours, the
   cases you looked at (game id, round, what the board showed), and what is left of the claim afterwards. Start each with the
   strongest argument AGAINST it, stated as its opponent would.
3. **The pair 1 + 2** and any other combination B proposes: does the "two sides of one idea" claim hold, and is the joint number
   sound?
4. **If you had to pick**: which one hypothesis would you send to the team, or none, and what is the most likely way it
   disappoints. Say plainly if you think the lead should pick differently from B.
5. **Corrections**: every number in `hypotheses.md`, `findings.md` or the deep reads that your recount could not reproduce, with
   both values.
6. **What I could not determine**.
7. **Counts I made**: every script, what it counts, its output file.
Finish by printing the line `SUBSESSION C DONE` as your final message.
