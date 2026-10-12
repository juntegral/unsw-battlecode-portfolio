You are sub-session B ("Hypotheses") of a study for team meow (id 1119) in the Battlecode "deep-sea dragons" game (unswbc 1.2.7).
Your one job: turn the evidence collected so far into 3 to 5 candidate hypotheses for how our bot can win more, each stated as a
GENERAL rule and each put on the same footing so that they can be compared. Output file: `hypotheses.md`.
Work only in this directory, which is your current directory:
`~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/top1/`

There is no time limit. Depth matters: where a candidate lacks a number, count it yourself on the replays instead of guessing.
But a file that is never written is worth nothing: create `hypotheses.md` as soon as the first candidate is written up and rewrite
it after each further one, so that it is always complete for what has been done so far. (A file of that name from an earlier run
exists; replace it. The earlier version is kept in `run1/` and you may read it as one more set of notes, not as a result.)

## Where the study stands
The study asks how the rank-1 team (Vibing++, id 306) and the two teams level with it (SSS, id 91; "forgot to mention", id 264) play
against teams rated 2000+, to find ONE excellent, well-supported hypothesis for our bot. The lead will pick the one after a red
team has tried to break your candidates; your job is the candidates. What all three top teams do is probably a real winning
factor; what only one does may be a quirk.

Read, in this order, completely:
1. `findings.md`: the lead's fact sheet on all 2,343 games (1,637 top-team games, 401 of ours against 2000+ teams), with the
   corrections from the four close reads and the two online trials that already exist.
2. `deep-read.md` (15 Vibing++ games), `deep-read-2.md` (SSS and forgot; the three-team table), `deep-read-3.md` (why our economy
   falls behind), `deep-read-4.md` (how and why our own queen dies). At least the "three findings", the comparison tables, the
   "what I would change" and the "wrong or thin" sections of each; the per-game parts where you need a case.
3. The team's own records (Read tool only, not the shell): the author's experiment log
   `~/01. Project/개인 프로젝트/battlecode/work/plan.md` and `~/01. Project/개인 프로젝트/battlecode/docs/LOOP.md`
   (how the team's card loop tests an idea); the online smoke-test records in `../../online/smoke/` (`tc30-test-result.txt`,
   `qh31-test-result.txt`, `qh31-analysis/summary.txt`, `qn23-analysis/summary.md`, and whatever else is there);
   `../newmaps-2026-10-04.md`; `../../codex/report-top-metrics.md`.
4. Our bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (4,873 lines; the toggles are the `constexpr` lines
   near the top). Every candidate must name the functions and constants it changes, so read the parts it touches.

## What the evidence looks like so far (the lead's reading; check it, do not take it on trust)
Two gaps, both large (`findings.md` 6d). Economy: we are under two thirds of the enemy's total length at round 300 in 63% of our
games that get there (the top three in 16% of theirs). Conversion: inside the same economy band we win about half as often as
they do (15% against 7%, 48% against 26%, 61% against 50%, 88% against 63%), about half of every top team's wins are queen-rule
wins and ours are 4 of 51, our queen is dead before round 300 in 84% of games (43–62%), and our longest dragon is 12 at round 400
(25–34). The mechanisms the reads found, each with counts in the files:
- **Enemy queen, attack.** Their queens end a turn inside the reach of one of our heads as often as ours does in theirs; they take
  the ram 71–86% of the time, we 16–22%. All three top teams ram a queen that a 2–3-long has in view and in reach (99–100%);
  Vibing++ and SSS at every length and price. The queen-hunt candidate qh31 (hunters of 4 or shorter) was tried online: 10 wins of
  30 against 8 on the same pairs; it takes 8 of 9 chances with 2–3-longs and 2 of 11 with longer dragons.
- **Own queen, defence.** 104 of our 362 queen deaths came on a turn on which she ended in a visible enemy's reach although a safe
  step existed (6 times the top three's rate against the same opponents); a boxed-in queen cuts herself to 2 where SSS and forgot
  shed and wait; the queen rules are off on maps of 600 cells or fewer and she dies at twice the rate there; team-mates step onto
  her last exit; nobody near her rams an intruder (3.7% against 12–17%).
- **Contact.** On maps over 1,200 cells our small dragons ram at 8% of meetings (everyone else 33–41%; on smaller maps we do 33–35%
  ourselves): a map-size switch in our code. We make 1 charge a game where others make 9–14, start 22% of the rams and eat 29% of
  the ram pearls (top three 49–52%). The trade-on-contact candidate tc30 was tried online: rams at 28% of meetings, units at round
  150 up from 46 to 52 (against 58–61), and 6 wins of 30 against 9.2 (0 of 12 on large maps).
- **The round clock.** After `grow_round` (150 on maps over 1,200 cells, 300 otherwise) a small dragon of ours eats a free pearl on
  the next cell in 49–56% of turns instead of 80–85% (everyone else stays at 75–88%), dragons longer than 4 stop splitting, and
  units fall. The leader zone (`LEADER_PEARL_RADIUS 9`, `ZONE_PEARL_PENALTY 600`) is the visible rule; card #14 replaced only the
  split stop and saw no local gain.
- **The longest-dragon race.** forgot feeds from about round 200–225 and SSS from about 200–300; our feeding starts at round 400
  (300 in queen-feeding mode, or 200 with 56 units). With both queens dead and total length level at round 400 we win 13 of 36
  (top three about 60%).
- No gap was found in ramming the enemy's longest dragon late (we do it at their rate), and "stride" raised the economy 14%
  locally without more wins.
You are free to form candidates that are not on this list and to drop any that are; but every item above must be either a
candidate, a part of one, or named under "Not proposed, and why".

## Hard rules
- Read-only towards the outside world: no network, no uploads, no GitHub, no Discord. Do not run games. Never read key or token files.
- Write only inside this directory. Name your own scripts `h_*.py` and put their outputs in `h_out/`. Do not edit or delete existing
  files except `hypotheses.md`, which you replace. At top level you create only `hypotheses.md`, your scripts, and part files
  `h_*.md` if you assemble the file from parts.
- A policy hook guards the shell. It allows only Bash, Read, Glob, Grep, Write, Edit. It blocks: `python3 -c`, `$(...)`, backticks
  (also inside a heredoc), a single `&` anywhere in a command (so no `2>&1`, no background `&`), `curl`/`wget`, sub-agents and every
  other tool, and any shell command that mentions `settings.json`, `guard.py` or `work/loop`. Put code in a file and run
  `python3 h_something.py args`. Plain pipes (`| head`) and `;` are fine. Do not try to work around the hook. Do not start other AI
  sessions.
- Be honest about uncertainty: for every statement say whether it is measured (which script, which file), inferred, or could not
  be seen in replays. A replay shows positions, actions, deaths, pearls and sonar rays; not intentions, memory or scores.

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
- THE QUEEN is each team's lowest id (0 or 1). The game ends at round 500 or when one team has no dragons. At round 500 the longer
  living queen wins (a living queen of any length beats a dead one): the "queen rule". If equal (both dead, or the same length),
  the longest single dragon wins: the "longest rule". Then total length.

## Data and tools already here
- `games.csv` (one row per game: map, cells, teams, elo, winner, end type, `battle_id` = which run and therefore which build of
  ours, replay path). Our 401 games are eleven runs: ladder downloads (live bot) and smoke pairs "-old" (live bot) / "-new"
  (candidates stride, passage2, qh31, tc30); see `findings.md`. Use opponents rated 2000+ and leave the map Schooltime out.
- `q/<game_id>.json` (per round: units, total, longest per side; a per-round queen record; queen death with its killer; every ram),
  `q3v2/<game_id>.json` (every turn on which a non-queen dragon had a legal ram on the enemy queen, with length, steps, taken or
  not, in view or not), `r3/<game_id>.json` (meetings, charges, ram pearls, free-pearl turns), `d_out/cls/`, `d_out/life/` (A4: the
  board around every queen), `c_out/` (A3: economy per 10 rounds). The scripts that wrote them have docstrings: `extract.py`,
  `extract3.py`, `recount3.py`, `d_class.py`, `c_econ.py`.
- The lead's what-if and tally scripts: `an4.py`, `an4b.py` (games that flip if the enemy queen had been rammed on a missed in-view
  chance), `behind.py`, `leaderrace.py`, `qearly.py`, `bybuild.py`, `check_a4.py`, `whatif.py`, `whatif2.py`, `cf.py`; outputs in `out2/`.
  A4's worth table: `d_out/worth.txt` and section 5g of `deep-read-4.md`.
- `lib.py`: `lib.Walk(path).run(hooks)` streams a replay with the full board state (about 1.3 s per game; `recount3.py` is a short
  example with a multiprocessing run). `python3 story.py` (usage when run without arguments) and `python3 digest.py <game_id> <team_id>`
  show single games.

## What a candidate must contain
For each of the 3 to 5 candidates, in this order:
1. **The claim, as a general rule.** One or two sentences a teammate can repeat. It may depend on the game state (what a dragon
   sees, lengths, counts, the round, who is ahead) and on terrain (open sides, dead ends, portals, distances). It must NEVER name a
   map and NEVER use a map-size condition. Removing a map-size switch that our code has today counts as making a rule general;
   say so where that is the change.
2. **Evidence.** The counts, with the file or script each comes from: us against the three top teams one by one (does each of the
   three do it?), us against our actual opponents in the same games, the protagonist's wins against its own losses where that
   says something about cause and consequence, and at least two game ids with rounds that show the behaviour and its absence.
   Mark each number "measured" or "inferred". If an online or local trial of the idea or of part of it exists, give its result
   and say exactly what it did and did not test.
3. **Mechanism.** Why following the rule wins games under the end-of-game rules: through the queen rule, the longest rule, a
   wipe-out, or through the economy that feeds them. Say which game states it turns into which.
4. **Expected effect, on the common footing.** (a) Games of our 401 (and of the live bot's 275) that would have ended differently
   under at least two readings: strict (nothing else changes) and realistic (state the assumption, for instance "afterwards she
   survives as a top-three queen does at that economy" or "we then win such games at our own rate for that state"). (b) The same
   as points of win rate, with an honest range. (c) In which kinds of game it acts (state of the economy, queens alive or dead,
   open or closed terrain, early or late) and in which it does nothing. (d) How the effect combines with the other candidates:
   does it need one of them first, does it overlap, does it add? Count the overlap in games where you can.
5. **What changes in `mybot2/main.cpp`.** Functions, constants and conditions by name; whether a toggle for it already exists and
   what its current value is; what else must obey the same test for the rule not to leak; a rough size of the change (a constant,
   a condition, a new function).
6. **What would show it is wrong.** Behaviour signals that can be counted on new replays with the scripts here (name the script and
   the number it must reach), separate from win counts. Say how many games a win-rate test would need to see the expected effect:
   the team's online comparison is 30 games against 30, and a difference of one or two wins in 30 is noise.
7. **Known risks, as far as you see them** (the red team comes after you; do not write its report, but do not hide what you already
   know): earlier experiments in `work/plan.md` or online that point the other way, a way the change could backfire (the passage
   change that got our queen killed is the team's example), a confounder you could not remove.

## Also required
- **A ranking with reasons.** One table: candidate, strongest evidence in one line, expected points (range), how sure, how hard to
  build, how testable, what it depends on. Then say which ONE you would pick and which you would pick second, and what would
  change your mind. If two rules are really one idea seen from two sides (for instance a rule about queens that applies to hers
  and to ours), say whether they should be one candidate or two and why; the final pick has to be one hypothesis that one card can
  test.
- **"Not proposed, and why"**: every mechanism on the list above that did not become a candidate, and every idea from `run1/hypotheses.md`
  you dropped, each with the number that decided it.
- **"Counts I made for this file"**: every new script, what it counts, its output file.
- **"What I could not determine"**.
Write in plain, casual, clear English; explain every term on first use; no lab jargon. A teammate who has not read the deep reads
must be able to follow `hypotheses.md` on its own. Finish by printing the line `SUBSESSION B DONE` as your final message.
