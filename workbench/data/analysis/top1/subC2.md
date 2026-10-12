You are sub-session C2 (second red-team round) of a study for team meow (id 1119) in the Battlecode "deep-sea dragons" game
(unswbc 1.2.7). Your one job: try to BREAK two new candidate hypotheses that came out of the last close read, by recounting from
the replays yourself, and then say which of three finalists you would send to the team, or none. Output file: `redteam-2.md`.
Work only in this directory, which is your current directory:
`~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/top1/`

There is no time limit. Depth matters. But a file that is never written is worth nothing: create `redteam-2.md` as soon as the
first candidate has been attacked and rewrite it after each further step, so that it is always complete for what has been done.

## Where the study stands
The study asks how the rank-1 team (Vibing++, id 306) and the two teams level with it (SSS, id 91; "forgot to mention", id 264) play
against teams rated 2000+, to find ONE excellent, well-supported hypothesis for our bot, which the team will then build and test
as one "card". Read, in this order: `findings.md` (the lead's fact sheet on all 2,343 games); `hypotheses.md` (four candidates);
`redteam.md` (the first red-team round: verdict table, candidate 1, candidate 3, "attack I: the footing", "If I had to pick");
`deep-read-5.md` sections 1, 2 (tables), 5 (answers d, e, g, h), 7 (candidate 5), 8 and 9; and from `deep-read-3.md` the finding on
the round clock. Do not read `run1/` (an older run).

After the first red-team round the picture was: candidate 1 ("any dragon of ours with the enemy queen's head in view and in reach
rams her") holds as a small, safe card of about +1 point of win rate (+0.5 to +2); candidate 2 (our queen never ends a move in a
visible enemy's reach) +0.3 to +1.5; candidates 3 (leader rules start at round 300 on every map instead of 150 on big ones) and 4
(small dragons do not give way at contact) "cannot be told"; and the red team named the longest-dragon race as the largest gap
no candidate works on. The lead then ordered a close read of that race (`deep-read-5.md`). It says three things you must test:

**Claim A (a correction of the first red team).** The race gap at "level total length at round 400" (we win 9 of 30 on maps of
1,200 cells or fewer, the top three 22 of 40) is mostly the economy seen late: a team that has fed its leader has already spent
length, so level total at round 400 hides that the enemy was richer. On "potential" (the longest dragon plus the pearls all other
own dragons would drop if they died now) we win 11 of 23 level races at round 300 and 12 of 24 at round 350, and we enter 106 of
our 143 races below 0.8 of the enemy's potential.

**Candidate 5, "one leader, known to all"** (`deep-read-5.md` section 7): when our leader cuts itself (keeps 2 segments, hands the
rest to a new dragon with a new id), every team-mate's record still names the old id for a median of 27 rounds, because a longer,
older report outranks a fresher, slightly shorter one; feeding stalls (the longest grows 5.0 per 25-round window with a cut
against 10.8 without) and a quarter of our deaths by choice happen next to no bigger dragon (our opponents 15%, top three 10%).
Rule: fresher news of a nearly-as-long dragon replaces older news of a longer one, and a dragon dies only next to a leader it can
see is long. Claimed +0.7 to +2.2 points, "most likely a little over +1", inferred from contrasts inside our own games; the
belief numbers come from 78 games of an earlier live bot whose sonar pings are readable.

**Candidate 3z, "nobody leaves a pearl lying for the leader"** (the lead's reformulation of candidate 3 after `deep-read-5.md`
answer d and section 8 item 7; it is not written up anywhere else, so this paragraph is its definition). From `grow_round` on (round
150 on maps over 1,200 cells, 300 otherwise) our small dragons must not take pearls within 9 cells of the believed leader
(`LEADER_PEARL_RADIUS 9`, `ZONE_PEARL_PENALTY 600`, no `EAT_BONUS` there; `in_leader_pearl_zone()`, `refresh_leader_zone()`,
`score_step()`). The rule: remove that pearl zone on every map (radius 0), and change nothing else: the leader's identity, the
split stop for dragons longer than 4, the leader's own no-split rule and the start of feeding stay as they are. The case for it:
(i) after the switch a small dragon of ours takes a free pearl on the next cell in 49–56% of turns instead of 80–85%, at exactly
our switch round on both map classes, in every run and build, and no other team's rate moves (`findings.md` 6c, lead's
`recount3.py`); (ii) by the dragon's own belief (readable pings) it takes such a pearl in 18–26% of turns inside its believed
leader's zone and in 75–87% outside; (iii) the leader gets nothing from it: it eats 7–17% of the pearls left for it, its own natural
intake does not rise at the switch (1.7 to 1.6 per 50 rounds on small maps, 4.0 to 3.4 on big), an own dragon under 8 eats 58–73%
of the left pearls a median 7–10 rounds later, the enemy 2–13%; (iv) the team's natural intake falls from 20.8 to 15.6 per 50
rounds on small maps and from 79.5 to 52.7 on big maps, and on a board where the zone's 181 cells are a third of all cells the
team starves (40 natural pearls in rounds 250–299, then 16, 9, 3); (v) the first red team's objection to candidate 3, "all 12 of our
big-map wins are longest-dragon wins won with the leader the round-150 switch builds", is answered by `deep-read-5.md`: that leader
is built by feeding from round 201–204 when we have 56 units and by not splitting, not by the zone. It differs from candidate 3
in leaving the switch round and the split stop alone and in acting on every map. The team's log has trials of moving the switch
(`GB300`, `LC_LEAD_ROUND` 200) but, as far as the lead found, none of the zone alone. No size has been put on it yet: that is part
of your job.

## Hard rules
- Read-only towards the outside world: no network, no uploads, no GitHub, no Discord. Do not run games. Never read key or token files.
  Our bot's sonar pings are sealed in later builds with a key that sits in the bot source: do NOT copy that key or any derived
  value into this directory or into any output; work with the 78 games whose pings are readable as they are, as sub-session A5 did
  (`e_bel.py`, `e_belief.py`), and say so.
- Write only inside this directory. Name your own scripts `y_*.py` and put their outputs in `y_out/`. Do not edit or delete existing
  files. At top level you create only `redteam-2.md`, your scripts, and part files `y_*.md` if you assemble the file from parts.
- A policy hook guards the shell. It allows only Bash, Read, Glob, Grep, Write, Edit. It blocks: `python3 -c`, `$(...)`, backticks
  (also inside a heredoc), a single `&` anywhere in a command (so no `2>&1`, no background `&`), `curl`/`wget`, sub-agents and every
  other tool, and any shell command that mentions `settings.json`, `guard.py` or `work/loop`. Put code in a file and run
  `python3 y_something.py args`. Plain pipes (`| head`) and `;` are fine. Do not try to work around the hook. Do not start other AI
  sessions.
- **Recount, do not re-read.** For every number a claim rests on, write your OWN script that walks the replays. Do not import or copy
  the counting logic of `e_*.py`, `h_*.py`, `x_*.py`, `recount3.py`, `c_*.py`; you may use `lib.py` (the replay walker) and `games.csv`,
  and you may READ the other scripts to learn exactly what they counted, so that a difference can be explained. For every recounted
  number give theirs, yours, and why they differ if they do. (How A5 reads a readable ping you may take from `e_belief.py`: that is
  a file format, not a count.)
- Be honest about uncertainty: measured (script, file), inferred, or not visible in replays. A replay shows positions, actions,
  deaths, pearls and sonar pings; not intentions or scores.

## The game in ten lines
- Snake-like dragons on a wrapping grid. Kelp (walls) and portals sit on the EDGES between tiles. A dragon sees the 7x7 square around its head.
- Each round every living dragon acts once, in ascending id order. A dragon must MOVE (1 or more steps) or SPLIT; there is no "stay".
- A dragon of length L gets ceil(L/4) free steps per turn; each extra step costs one segment.
- Moving the head into another dragon's HEAD kills both (a ram). Into a body, kelp or itself kills only the mover.
- A dead dragon of length L drops ceil(L/2) pearls on its body cells. Eating a pearl = +1 length. So a dragon that dies next to a
  team-mate hands over at most half of its length; that is how every bot "feeds" one long dragon late in the game.
- Split: a dragon of length 4 or more splits off its rear as a new dragon (child at least 2, parent at least 2). The child's head is the
  old tail, facing the other way. At most 64 dragons per team.
- Pearls: every tile has a hidden spawn interval; a pearl appears only on an empty tile (a pearl left lying blocks the next one).
- THE QUEEN is each team's lowest id (0 or 1). The game ends at round 500 or when one team has no dragons. At round 500 the longer
  living queen wins (a living queen beats a dead one); if both are dead or equal, the longest single dragon wins; then total length.

## Data and tools
- `games.csv`: one row per game (map, cells, teams, elo, winner, end type, replay path, `battle_id`). 2,343 games: 1,637 of the top
  three, 706 of ours, of which 401 are against teams rated 2000+ with the map Schooltime left out. Our 401 games are eleven runs
  (`battle_id`): ladder downloads `dl-20261003`, `dl-20261004` and the "-old" halves of smoke pairs = the live bot (275 games); the
  "-new" halves = test builds stride, passage2, qh31, tc30 (126). 313 of the 401 are against test4 (id 19) and WeHaveQuizzes (id 87).
- `lib.py`: `lib.Walk(path).run(hooks)` streams a replay with the full board state: every body, every pearl and where it came from,
  kelp and portal edges, hooks `round_start, action, moved, split, death, eat, sonar, end` (260 lines; read it). About 1.3 s per
  game; use `multiprocessing.Pool` with at most 5 workers and `os.nice(10)`.
- `python3 story.py` (usage when run without arguments) and `python3 digest.py <game_id> <team_id>` show single games.
- Our bot: `~/01. Project/개인 프로젝트/battlecode/mybot2/main.cpp` (Read or Grep tool, not the shell). The team's
  experiment log: `~/01. Project/개인 프로젝트/battlecode/work/plan.md` (Read tool). Online smoke-test records:
  `../../online/smoke/` (`*-result.txt`, `*-analysis/`).

## What to do
1. **Claim A, the footing of the race.** Recount the round-500 games with both queens dead (ours 143, the top three 447, our
   opponents' side of ours): wins by own / enemy TOTAL length at round 400 and by own / enemy POTENTIAL at rounds 300, 350 and 400,
   by map class (1,200 cells or fewer / more) and against test4 and WeHaveQuizzes separately. Is A5 right that the first red team's
   "30% against 55% at level length" is mostly the economy? What is left of a race gap of its own, with its range? Is "potential"
   itself a fair footing (it counts a far-away 2-long as half a segment for the leader; big maps end with 39–49% of potential in
   the longest for everybody), and does a different fair footing change the answer?
2. **Candidate 5.** Attack it as the first round attacked candidates 1 to 4:
   - *The counts*: leader cuts per race, the growth of the longest in 25-round windows with and without a cut (ours 5.0 against
     10.8; by run, by opponent, by map class), deaths by choice next to no bigger own dragon (26% / 20% against 8–20% for the
     others), the share of feeder pearls that reaches the final longest. From the readable pings: rounds until half the team
     names the new longest after a cut (27), the share of samples in rounds 400–494 in which under a quarter name the true
     longest (187 of 347), growth by that share.
   - *Cause or consequence*: a leader cuts when it is crowded or in a pocket, and a window with a cut starts with the longest
     dragon having just lost 2 segments and its id. Is the 5.0 against 10.8 the stale record, or the pocket, the crowd, the cut
     itself, or simply that windows without a cut are the games in which things go well? Compare the same window types for teams
     that have no such record problem; compare windows right after a cut in which the team DID name the heir quickly with those in
     which it did not (inside the same game where possible); look at what the feeders near the heir actually do in the 25 rounds
     after a cut (wait, walk to the stub, die next to the stub, die next to the heir).
   - *What happens next*, *sample size* (78 readable games of an earlier bot; 12 level races won and 12 lost; two opponents),
     *cross-team* (do forgot, Vibing++ and WHQ really keep feeding through a cut, and is SSS, which shows the same halving, worse
     for it?), *earlier experiments* (`FEED_LOCAL`, "refuse to feed a leader much shorter than the max ever heard", regional
     leaders: what the log says and on what numbers), *backfire* (regional leaders on big maps when age counts; feeders that no
     longer die and are alive and useless at round 500; a leader that is not followed at all for a while), *the code claim*
     (`hear_exact()`, `hear_sighting()`, `leader_priority()`, `expire_leader()`, `broadcast_leader()`, `pick_feed_target()`,
     `ready_to_die()`, `beside_visible_leader()`, `escape_child_size()`: does the record behave as A5 says after a cut; would the
     three proposed changes do what is claimed and only that; is any map-size condition hidden in it).
   - *The size*: A5's strict 6–12 and realistic 3–9 games of 401. Re-derive it your own way and give the range you would defend.
3. **Candidate 3z.** It has no write-up but the paragraph above, so first establish the facts, then attack them:
   - *The counts*: the free-pearl rate of our small dragons before and after the switch round on both map classes, for the live
     bot and the test builds, and for the other teams; inside and outside the zone, both by the dragon's own believed leader
     position (readable pings) and by the true longest dragon's position (all games); what happens to every pearl left lying in
     the zone (who eats it, after how many rounds, how long the tile is blocked); the leader's own natural intake before and after
     the switch; the team's natural intake and total length before and after, against the same rounds for the other side of the
     same games.
   - *Cause or consequence*: how much of the fall in intake at the switch is the zone and how much is everything else that
     changes at that round (the split stop for dragons longer than 4, fewer units, the enemy arriving, in queen-feeding mode the
     feeders walking to the queen)? Use the within-game contrast: dragons inside against outside the zone in the same rounds,
     boards on which the zone covers a large or a small share of the cells, games in which the believed leader is far from most
     of the team. Give the share of the fall that would come back if every zone turn behaved like an out-of-zone turn.
   - *Does the leader need it?* The first red team's objection, and A5's answer. Recount on ALL our races and on all our wins that
     were decided by the longest dragon (not four games): the leader's segments by source (natural pearls inside what would be its
     zone, feeder pearls, other own corpses, enemy corpses) per 50 rounds, on both map classes; how many of our wins had a margin
     smaller than the natural pearls the leader ate that small dragons would probably have taken instead; whether pearls eaten by
     small dragons come back to the leader later through feeding (half of a feeder's length drops as pearls; the final longest
     gets 36–47% of those on small maps and 15–31% on big ones) and what the net for the leader's final length then is.
   - *What it is worth*: put a size on it your own way, with its range, for all 401 games and for the live bot's 275: more natural
     pearls -> more total length and potential from the switch round on -> which games change (wipe-outs, races, queen games), under
     a strict and a cautious reading; remember the first round's warning that a win rate "for a band" was earned with the bot as it
     is. Say in which kinds of game it acts and in which it does nothing.
   - *Earlier experiments*: everything in `work/plan.md` and online that moved the leader round, the zone, the leader's pearl
     weight (`LC_LEAD_MULT`), or the split stop (`GB300`, `LC_LEAD_ROUND`, `LC200`, card #14 if you can find it), with numbers; does
     any of it contradict 3z, or did all of it test something else?
   - *Backfire*: small dragons crowding the leader and boxing it in or stepping onto its exits once nothing keeps them away (count
     how often a leader of ours is boxed in by own bodies today, inside and outside feeding); the leader's growth before feeding
     starts; more dragons near the leader when an enemy rams it; the enemy eating what our small dragons used to leave.
   - *The code claim*: with radius 0, does `in_leader_pearl_zone()` switch the zone off entirely, what else reads `zone_active` or
     `zone_head`, and does anything else change with it? Is there a toggle? Is any map-size condition left in the rule as stated?
   - *Cross-team*: does any top team, or test4 or WeHaveQuizzes, leave pearls for its leader in any phase (the eating rate of
     small dragons near their own longest dragon, before and during feeding)?
4. **The three finalists side by side.** Candidate 1 (take the queen; first round: +0.5 to +2, most likely about +1), candidate 5
   and candidate 3z. One table: what is measured and how solid, what is inferred, the range you would defend, the chance it does
   harm and how much, the size of the change in the code, what behaviour number would show it working on 20–60 new replays,
   whether all three top teams do it. Then say plainly which ONE you would send to the team as the study's hypothesis, or none,
   and the most likely way it disappoints. Say whether two of them are safe to test together and what would be lost by that.
5. **Corrections** to `deep-read-5.md`, `redteam.md`, `hypotheses.md`, `findings.md`: every number you could not reproduce, both values.
6. **What I could not determine**, and **Counts I made** (every script, what it counts, its output file).

## Output: `redteam-2.md`
Plain, casual, clear English; explain every term on first use; a teammate who has read none of the other files must be able to
follow it. Start with a verdict table (Claim A, candidate 5, candidate 3z: "holds" / "holds, weaker than claimed" / "does not hold"
/ "cannot be told"; the claimed range; the range you would defend; the strongest objection; what would settle it), then the
sections 1 to 6 above. Begin each candidate with the strongest argument AGAINST it, stated as its opponent would. An honest
"this does not hold" is worth more than a polite pass. Finish by printing the line `SUBSESSION C2 DONE` as your final message.
