# Top-team study: what the best three teams do that we don't

Written 5 October 2026 for team meow (id 1119). Second, full run of the study; the first run's files are kept in `run1/`.
Nothing here was posted anywhere, no game was played and nothing was uploaded: it is all counting on ladder replays and reading
our bot's source.

## The 30-second version

**The pick: nobody leaves a pearl lying for the leader.**
From a fixed round on (150 on maps over 1,200 cells, 300 on the others) our small dragons stop taking pearls within 9 cells of
the dragon they believe is our longest. No other team we looked at does this, and it is the clearest single thing in 2,343
replays that we do and they don't.

- **What it costs us.** A small dragon of ours with a free pearl right next to its head takes it in about 84% of turns before
  that round and in 51–58% after. Our natural-pearl intake drops by a fifth on the smaller maps and by a third on the big ones,
  and our total length stops growing at exactly that round. The other side of the same games does not move.
- **What it buys.** Almost nothing before feeding starts: the longest dragon eats no more natural pearls than before, and two
  thirds of the pearls left for it are eaten by another small dragon of ours about ten rounds later. Late in the game it does help
  a little: it keeps small dragons off the pearls our feeders drop next to the leader.
- **The rule to test.** Until the team starts feeding one dragon, nobody passes up a pearl for anybody. Once feeding has started,
  a small dragon leaves only the pearls within a few cells of a leader it can actually see.
- **What it is worth.** Probably about +1 point of win rate (range +0.3 to +2) on our 27.9% against teams rated 2000+. That is an
  estimate from played games, not a test result.
- **How to check it.** Not by wins: one point is 0.3 wins in a 30-game test. Check the behaviour: "free pearl next to the head
  taken" must go from about 55% to over 80% after the switch round, and the leader's share of feeder pearls must not fall.

**The honest headline is less exciting than one would like.** We did not find one big thing the top teams do that would lift us
a lot. The main gap is that we arrive at the late game with much less length than the other side (we are under two thirds of the
enemy's length at round 300 in 63% of our games that get there; the top three in 16% of theirs). Every rule that survived the
red team is worth roughly one point. This one is picked because it is the best-measured, it works on that main gap, it is tiny to
build, and it shows up in 20 games.

**Runner-up, and safe to run alongside as its own card:** any dragon of ours that has the enemy queen's head in view and in reach
rams her, at any length. The top three do it nearly every time (Vibing++ 265 of 266 such turns), our opponents do it to our queen
86% of the time, we do it 23% of the time. Also about +1 point, and it can hardly hurt. A narrower version (hunters of 4 or
shorter) has been online twice: the behaviour moved, the results did not.

## Words used

- **Queen**: each team's lowest-numbered dragon. **Ram**: a head moves into another head; both dragons die.
- **How a game ends**: by wipe-out, or at round 500. At round 500 a living queen beats a dead one and the longer living queen
  wins (**queen rule**). If both are dead, the longest single dragon wins (**longest rule**). A round-500 game with both queens
  dead is called a **race** here.
- **Leader**: a team's longest dragon. **Feeding**: small dragons die on purpose next to the leader, which eats the pearls they
  drop (a dead dragon drops half its length as pearls). Every team does this late in the game.
- **Switch round**: in our bot, round 150 on maps over 1,200 cells and round 300 on smaller ones (`grow_round`). From then on
  dragons longer than 4 stop splitting and the pearl zone applies.
- **Pearl zone**: after the switch round a small dragon of ours may not take, or even walk to, pearls within 9 cells of the place
  where it believes our leader is (`LEADER_PEARL_RADIUS 9`).
- **Free pearl turn**: a dragon of length 2–4 that is not the queen, no enemy head in its 7x7 view, and a pearl on a free cell
  right next to its head with a way out behind it. "Taken" = it eats that pearl this turn.
- **Natural pearl**: one a tile produced. **Corpse pearl**: one a dead dragon left.
- **Top three**: Vibing++ (id 306, rank 1 in the snapshot and the team this study follows), SSS (91) and "forgot to mention" (264).
  **test4** and **WeHaveQuizzes (WHQ)**: the two teams rated just over 2000 that we meet in 313 of our 401 games.
- **Small maps / big maps**: 1,200 cells or fewer / more. Used only because our own code switches there. Nothing proposed here
  uses a map size.
- **Live bot / test builds**: our 401 games are 275 by the released bot of that hour and 126 by test builds (stride, passage2,
  queen hunt, trade-on-contact).
- **Point**: one percentage point of win rate. One game of our 401 is 0.25 points.

## 1. How the study was done

- **Data.** 2,343 ladder replays: 1,637 games of the top three against teams rated 2000 or more, and 706 of ours, of which 401
  are against teams rated 2000+ (the map Schooltime is left out everywhere: both queens are sealed in a room there). A replay
  walker (`lib.py`) rebuilds the whole board turn by turn; it was checked against the game engine on 81,853 steps.
- **Eight sub-sessions**, each a separate max-effort session started by the driver, each with its own scripts:
  five close reads (`deep-read.md` Vibing++; `deep-read-2.md` SSS and forgot; `deep-read-3.md` our economy; `deep-read-4.md` our own
  queen; `deep-read-5.md` the longest-dragon race), one hypotheses session (`hypotheses.md`, four candidates), and two red-team
  rounds (`redteam.md`, `redteam-2.md`) that recounted every key number with scripts of their own and tried to break the candidates.
- **The lead's own checks.** After each sub-session I recounted its main numbers with separately written scripts
  (`check_a2.py`, `recount3.py`, `check_a4.py`, `behind.py`, `leaderrace.py`, `qearly.py`, `bybuild.py`; outputs in `out2/`) and read
  the code paths the candidates rely on. The fact sheet with all numbers is `findings.md`.
- **One thing found on the way that matters for every "meow" number:** our 401 games are not one bot. They are eleven runs: two
  ladder downloads and smoke-test pairs in which the live bot and a candidate each played test4 and WHQ. Where the builds differ,
  the tables say so.

## 2. Where we stand

**How our games end** (401 games against 2000+ teams; top three: 1,637):

| How the game ended | meow | won | top three | won |
|---|---|---|---|---|
| wipe-out, we wiped them out | 67 (17%) | 67 | 455 (28%) | 455 |
| wipe-out, we were wiped out | 103 (26%) | 0 | 267 (16%) | 0 |
| round 500, our queen alive, hers dead | 1 | 1 | 177 (11%) | 177 |
| round 500, both queens alive | 14 | 3 | 159 (10%) | 103 |
| round 500, both queens dead (a race) | 143 (36%) | 41 | 447 (27%) | 266 |
| round 500, our queen dead, hers alive | 73 (18%) | 0 | 132 (8%) | 0 |
| all | 401 | 112 = 27.9% | 1,637 | 1,001 = 61.1% |

**Two gaps, and the first is the bigger one.** Games that reach round 300, by our total length divided by the enemy's at round 300:

| Length ratio at round 300 | top three: games, won | meow: games, won |
|---|---|---|
| under 0.67 | 171, 15% | 168, 7% |
| 0.67 to 1 | 241, 48% | 61, 26% |
| 1 to 1.5 | 312, 61% | 12, 50% |
| over 1.5 | 332, 88% | 27, 63% |

- **Economy.** We are far behind in 63% of these games; the top three in 16%. On big maps we are behind in total length at round
  300 in 108 of 109 games.
- **Conversion.** In the same row we win about half as often as they do. Most of that is the queen rule: about half of every top
  team's wins are queen-rule wins; ours are 4 of 51. Our queen is dead before round 300 in 84% of games (SSS 43%, forgot 52%,
  Vibing++ 62%).
- The two rough what-ifs (our rates with their mix of rows, their rates with our mix) give 42% and 32% against our 19% in these
  games. The red team is right that the ranges overlap (the two top rows of ours hold only 39 games), and that 133 of our games,
  with 61 of our 112 wins, are over before round 300 and are in neither number.

**What rank 1 does, in one line.** Vibing++ keeps its whole team eating until late (its small dragons take 88–91% of the pearls
near their own leader), starts feeding its leader as late as we do (about round 360–400), ends with the smallest share of its
length in one dragon of all the teams looked at, and still wins races, because it arrives with more. It rams a queen it can see
every time. Its own losses are mostly games in which it was already behind 1.5 to 1 in units by round 50–100.

## 3. The chosen hypothesis: nobody leaves a pearl lying for the leader

### 3.1 The claim, as a general rule

> Until the team starts to feed one dragon, no dragon of ours passes up a pearl for the sake of another dragon. Once feeding has
> started, a small dragon leaves the pearls within a few cells of a leader it can see, and no others.

It names no map and uses no map size. The switch round itself, the split stop, who counts as leader and when feeding starts all
stay as they are.

### 3.2 Evidence

**(a) The rate drops at exactly our own switch round, on both kinds of map, and nobody else's moves.** Share of free pearl turns
taken (`redteam-2.md` section 3, script `y_c3a.py`; the lead's separate count `recount3.py` gives 80% to 56% on big maps and 85% to
49% on the others with a slightly looser definition; sub-sessions A3 and B found the same):

| Big maps, rounds | 130–139 | 140–149 | 150–159 | 160–169 | 170–199 | 200–299 |
|---|---|---|---|---|---|---|
| meow, live bot | 84% | 84% | **64%** | 60% | 60% | 58% |
| meow, test builds | 82% | 79% | 62% | 54% | 60% | 56% |
| our opponents in the same games | 86% | 86% | 85% | 85% | 84% | 85% |
| forgot / SSS / Vibing++ | 93 / 84 / 90% | 93 / 84 / 90% | 93 / 82 / 89% | 93 / 83 / 89% | 93 / 83 / 90% | 93 / 83 / 89% |

| Small maps, rounds | 280–289 | 290–299 | 300–309 | 310–319 | 320–349 | 350–399 |
|---|---|---|---|---|---|---|
| meow, live bot | 85% | 83% | **64%** | 51% | 51% | 53% |
| meow, test builds | 86% | 85% | 60% | 50% | 55% | 55% |
| our opponents in the same games | 81% | 81% | 82% | 80% | 79% | 76% |
| forgot / SSS / Vibing++ | 91 / 82 / 89% | 91 / 82 / 89% | 92 / 81 / 90% | 92 / 81 / 89% | 91 / 79 / 89% | 91 / 80 / 87% |

Each of our eleven runs shows the step. The same behaviour appearing at round 150 on one kind of map and round 300 on the other,
on the round our own code switches, is what makes this more than a correlation.

**(b) It is the zone, measured from what each dragon itself believes.** In 82 games of an earlier live bot the sonar pings can be
read, and each dragon's ping says which dragon it takes for the leader and where. Free pearl turns taken, by distance from the
pearl to that believed leader (`y_c3a.py`; sub-session A5 found the same with `e_d.py`):

| | 0–3 cells | 4–6 | 7–9 | 10–12 | 13–16 | 17+ |
|---|---|---|---|---|---|---|
| small maps, 50 rounds before the switch | 90% | 85% | 86% | 84% | 91% | 93% |
| small maps, 50 rounds after | 35% | 16% | 19% | **81%** | 92% | 96% |
| big maps, 50 rounds before | 90% | 85% | 79% | 84% | 83% | 72% |
| big maps, 50 rounds after | 24% | 21% | 31% | **70%** | 76% | 79% |

A step between 9 and 10 cells, after the switch and not before. If every turn inside a zone were played like a turn outside it,
92–94% of the fall would come back on small maps and 72–79% on big maps.

**(c) Half of what the zone forbids is forbidden around nobody.** Turns inside a believed zone are 51–56% of all free pearl turns
on small maps and 33–38% on big maps. The zone of our true longest dragon covers far fewer (32% and 14%): most zones sit around
the last known place of a dragon that is dead or short, because under 40% of our dragons name the true longest at any time.

**(d) The team pays for it.** Natural pearls eaten per 50 rounds, same games throughout (`y_c3b.py`):

| | before the switch | first 50 rounds after | next 50 | the other side, same rounds |
|---|---|---|---|---|
| small maps, live bot (99 games) | 39.5 | 31.0 (−22%) | 29.4 | 51.4, 48.7, 44.4 |
| big maps, live bot (75 games) | 81.1 | 54.0 (−33%) | 47.1 | 130.6, 130.8, 127.8 |

Per small dragon (so that a falling unit count cannot be the reason) the intake falls 20% and 38% within the first 25 rounds;
the other side's stays flat. Our total length on the same games: small maps 60, 61, 61, 62 at rounds 250 to 400 (the other side
95, 99, 99, 95); big maps 109, 126, 125, 122, 122 at rounds 100 to 300 (the other side 152, 207, 260, 300, 327). We stop growing
at the switch. Inside the zone a small dragon does not just skip the pearl next to it: the code also stops it from walking to
pearls, fountains and tiles about to produce a pearl there, which is why the ground that was our richest before the switch
(3.8–4.0 natural pearls per 100 dragon-rounds near the believed leader) becomes our poorest (1.3–1.5).

**(e) The leader gets almost nothing from it before feeding.** Of the natural pearls left lying in a zone, 62–75% are eaten by
another small dragon of ours a median 8–11 rounds later, 11–26% by a leader, 4–5% by the enemy on small maps and 12–17% on big
maps. The leader's own natural intake does not rise at the switch (3.2 then 3.2 per 50 rounds on small maps; 4.1 then 3.8 on big).
Leaders of teams that have no zone eat as many (3.0 and 4.6 for our opponents' leaders in the same games). The leader of our
big-map wins is built by feeding from about round 200 (when we have 56 units), not by the zone: in all 12 big-map wins its feeder
pearls go 2.9, 4.7, 5.0, 6.0, 20.8 per 50 rounds while its natural pearls stay at 1–4.

**(f) Nobody else does it.** Natural pearls taken when the pearl is within 9 cells of the team's own longest dragon (10 or
longer) / farther away (`y_c3a.py`):

| | small maps, rounds 300–399 | big maps, rounds 150–299 |
|---|---|---|
| meow, live bot | 29% / 59% | 48% / 64% |
| our opponents | 87% / 87% | 83% / 84% |
| forgot | 96% / 94% | 95% / 95% |
| SSS | 80% / 78% | 82% / 82% |
| Vibing++ | 88% / 83% | 88% / 87% |

For every other team the ground near its long dragon is the best ground on the board. One mild exception, late: from round 400
Vibing++'s and test4's small dragons hold back a little on corpse pearls near their leader (64–70% against 72–81% elsewhere).
That is the feeding phase, and it is why the rule above keeps a small zone there.

**(g) Where the first version of this idea was wrong.** "The leader gets nothing from the zone" does not hold late in the game.
The zone also covers the pearls of dead feeders. Per small-map race, the dragon that ends as our longest eats 3.4 corpse pearls
and 2.4 natural pearls that a small dragon next to them had left alone (2.2 and 0.9 on big maps), and 7 of our 41 race wins were
closer than that. So switching the zone off in every phase would make the team 12–16% longer on small maps but probably leave
the final longest dragon a little shorter there. That is why the rule keeps feeder pearls next to a visible leader reserved once
feeding has started.

**(h) Games that show it.** weakhold games 1029033 and 1045374 (both against WHQ, `deep-read-5.md` games 11 and 12): at round 300
we have 65 total length against 34 and 94 against 43. From the switch on our natural pearls per 50 rounds go 40, 16, 9, 3 and
47, 26, 4 (WHQ in the first game: 34, 27, 24, 24), and our total length falls to 44 and to 59 by round 400 with nobody feeding
yet. We lose both on the longest dragon (4 to 26 and 25 to 31). On that board the zone's 181 cells are a third of all cells. The trade
build's two best big-map openings (1068050, 1068051: ahead of WHQ at round 150 with 60 units against 33 and 39) were lost between
rounds 150 and 250, under this zone.

### 3.3 Why it should win games

More pearls from the switch round on means more total length, and length is what feeding turns into the longest dragon. The
estimate is 8 to 10 more natural pearls by round 400 on small maps and 30 to 45 more by round 300 on big maps (a quarter to a
third more total length there). It acts in every game that reaches the switch round: all 111 big-map games from round 150 and
159 of our 290 small-map games from round 300. It does nothing in the 131 small-map games that are over before round 300 and
cannot turn the games we lose with our queen dead and hers alive.

### 3.4 What it is worth

No game was played, so this is arithmetic on played games (`redteam-2.md` section 3, part H):

| Reading | all 401 games | live bot, 275 games |
|---|---|---|
| strict (every extra pearl arrives; win rates per length band as they are today) | +5 to +13 wins | +3 to +9 |
| cautious (half the pearls; races only; the small-map leader pays what (g) says) | +1 to +4 wins | +1 to +3 |
| what the red team and I would defend | **+1 to +8 wins: +0.3 to +2 points, most likely about +1** | +0.4 to +2 points |

Why the low half: a win rate "for a length band" was earned with the bot as it is. The one time our big-map economy was raised
by a fifth (the trade-on-contact build) it won 0 of 12 big-map games, where 1.7 would be expected. And a third more length still
leaves most big-map games under two thirds of the enemy's.

### 3.5 What changes in the code

`mybot2/main.cpp`. There is no toggle today; `LEADER_PEARL_RADIUS` (9) and `ZONE_PEARL_PENALTY` (600) are plain constants.

- The zone is set in `refresh_leader_zone()` and tested in `in_leader_pearl_zone()`, which is read in seven places: four in
  `survey_from()` (zone pearls, tiles about to produce a pearl and fountain tiles are not targets), one in `look_cell_value()`, and
  two in `score_step()` (no `EAT_BONUS` on a zone pearl; `ZONE_PEARL_PENALTY` for anyone but the leader).
- **The build to test:** in `refresh_leader_zone()` the zone exists only when `feeding_phase()` is true and the leader's head is in
  the dragon's own view, with a radius of about 4 (our feeders die within 3 cells of the leader's head). About three lines and one
  constant, behind a new toggle that is off by default.
- **The plain version** (zone off in every phase) is one constant. Note that radius 0 does not switch it off: the one cell of the
  remembered position stays. Radius −1 or an early return does. It gains the same on big maps and puts some close small-map races
  at risk, see (g).
- Nothing else changes with it: `grow_round` still decides who counts as leader and the split stop; feeding is untouched.

### 3.6 What would show it is wrong

Countable on 20 big-map and 20 small-map games of a build with it, with `y_w3.py` / `y_c3a.py` / `y_c3b.py` (or the lead's `recount3.py`
for the first number):

1. Free pearl next to the head taken after the switch round: 51–58% today, must be over 80%. If not, the code is not doing what
   the rule says.
2. Natural pearls per 50 rounds after the switch: 54 must become 70 or more on big maps, 31 must become 37 or more on small
   maps. Total length at round 300 on big maps: 122 must become 150 or more.
3. Must not fall: the share of feeder pearls our final longest dragon eats (39% on small maps, 25% on big), and our longest
   dragon at round 400 and at the end. If these fall, the trade is the wrong way round and the zone should come back in the
   feeding phase with a larger radius.
4. If 1 and 2 hold and results still do not move over many games, the extra length is being lost at contact (we ram at 8% of
   meetings on big maps where everyone else rams at 33–41%, and eat 29% of ram pearls against 49–52%), and the next card is
   about contact, not pearls.

A win test is out of reach: one point is 0.3 wins in 30 games, and seeing +2 points with four chances in five takes about 8,000
games a side.

### 3.7 Earlier trials, and risks

- **Never tried alone.** The team's log has trials that moved the whole switch: `GB300` (round 300 instead of 150 on big maps;
  local mirror matches 46 of 96 against 48 and 73 of 152 against 76) and `LC_LEAD_ROUND 200` (online 19 of 60 against 23; it moved
  the zone 100 rounds earlier on small maps and lost four games, which points the same way as this rule, inside the noise).
  `LC_LEAD_MULT` 2 and 3 (a keener leader) changed nothing. A local mirror match is a weak judge here: neither side eats what the
  other leaves.
- **The standing warning.** More length has not turned into wins for us yet: "stride" (+14% economy locally, no more wins) and
  the trade-on-contact build (+21% length at round 300 on big maps, 0 of 12).
- **Boxing the leader in.** Checked: with the zone on there are already as many small own dragons next to our leader's head as
  next to anybody's (0.70 within 3 cells; teams with no zone 0.47–0.91), and only 8% of its blocked neighbour cells are small own
  dragons. No reason to expect more.
- **The amended form was designed from the counts, not counted itself.** Point 3 above is its guard.
- **Belief numbers** come from 82 games of an earlier live bot (later builds seal their pings; nobody unsealed them). The rate
  step itself is in every run of every build.

## 4. Runners-up

| Candidate | What the red team would defend | Why it is not the pick |
|---|---|---|
| **Take the queen**: any dragon with the enemy queen in view and reach rams her | +0.5 to +2 points, most likely about +1 | Surer in sign than the pick and tiny to build, but its tested half has been online twice with no change in how games end, and it does nothing when we are far behind |
| **Our queen is never spent**: she never ends a move in a visible enemy's reach when another move exists; never rams; sheds 2 instead of cutting herself to 2 | +0.3 to +1.5 | A queen of ours that does take the safe step is still alive at the end only 6–9% of the time |
| **One leader, known to all**: after the leader cuts itself, the team follows the new dragon at once | −0.3 to +0.8 | The 27-round blindness is from an earlier bot; today's builds recover in 10–15 rounds |
| **Do not give way at contact**: a small dragon that is not outnumbered rams any small enemy head in reach | −0.5 to +1.5 | The one online trial of a third of it won 6 of 30 against 9.2 (0 of 12 on big maps) |
| **Leader rules start at round 300 on every map** (the first form of the pick) | −1.2 to +1.3 | Moves the whole switch; replaced by the narrower pick |

**Take the queen, in more detail**, because it is close and safe to run as a second card (`hypotheses.md` candidate 1,
`redteam.md` candidate 1):

- A "chance" is a turn that starts with the enemy queen's head in a dragon's view and a free path to it within its reach. Queens
  move first each round, so such a ram cannot be dodged. Chances taken: Vibing++ 265 of 266, SSS 250 of 252, forgot 253 of 451 (its
  2–3-longs 136 of 139 from round 100 on), our opponents on our queen 197 of 228, meow 99 of 435 (2–3-longs 87 of 231, 4-longs 5
  of 39, longer 7 of 165). The lead's own data agree (86% against 22%), and both queens are exposed about equally often.
- In 75 of our games we had such a chance and never rammed her. 25 were round-500 losses with her alive. Read one by one, about
  6 flip (4 of them live-bot games); a comparison inside our own record gives 3 to 11, with zero not excluded.
- Code: `QUEEN_HUNT` exists and is off. Switching it on makes every non-queen dragon that sees her head and has a free path within
  its reach ram (`mark_hunt_targets()`, `hunt_path()`, called first in `act()`). One condition must change with it: the guard uses
  `is_queen()`, which is false on maps of 600 cells or fewer, so our own queen would hunt there; it must test `real_queen()`.
- The queen-hunt builds qh31 and qh31b (hunters of 4 or shorter that also walk towards her) were online: over 56 games a side,
  chances taken by 2–3-longs went from 15 of 49 to 19 of 20 and games with a ram on her queen from 16 to 24; her queen alive at
  the end 19 to 16, certain losses 16 to 15, wins 16 to 17.
- Where a dead enemy queen helps: not when we are far behind (0 wins in 49 races in which she died before round 300 and we were
  under two thirds of their length), a lot when we are level or ahead. Do not limit it to short dragons: three of the six flips
  need an attacker of 6 or 8 segments, late, on a fed queen.
- It is safe together with the pick: different code, different number to read (chances taken 22% to over 90%).

**Looked at and not proposed:** feeding the leader earlier (the start does not separate winners: Vibing++ starts as late as we
do; three earlier trials were neutral); guards near the queen (nobody escorts; the team's newest online trial of guards won 5 of
30 against 8); hunters that walk to her (36 hunters lost for 8 rams in the first online trial); ramming the enemy's longest
dragon late (no gap: we already do it at their rate).

## 5. The queen questions from QWQ and Zhe

From `deep-read-2.md` and `deep-read-4.md` (per 1,000 "queen-rounds" = rounds in which a queen is alive):

| | meow | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|
| Queen deaths per 1,000 queen-rounds | 6.5 | 2.2 | 2.8 | 2.1 | 3.4 |
| Alive at round 300 / at the end | 15% / 10% | 61% / 40% | 52% / 36% | 65% / 41% | 49% / 27% |
| Rounds with an enemy head in her view | 20% | 17% | 21% | 18% | 21% |
| Ends a turn inside a visible enemy's reach although a safe step exists (per 1,000) | 2.7 | 1.5 | 0.8 | 0.6 | 1.1 |
| Such a turn is punished by a ram | 71% | 16% (by us) | 44% | 47% | 32% |
| A small intruder within 4 steps of her is rammed by one of her team | 3.7% | 13.6% | 13.5% | 16.6% | 12.1% |
| Path distance from her start, rounds 50–99 | 14.7 | 12.7 | 15.0 | 12.3 | 16.9 |
| Walks a loop of 4 cells (share of rounds) | 0.3% (11% on maps of 600 cells or fewer) | 12% (test4 25%) | 2.4% | 5.2% | 2.4% |

- **Is she found?** Every team's queen is seen in 88–98% of its games, about as often per round as ours. Ours is not found more;
  she dies more once found (an episode with an enemy in view ends in a ram 11.5% of the time for ours, 4.7–6.3% for the top three).
- **Why she dies.** 104 of our 362 queen deaths came on a turn on which she ended in a visible enemy's reach although a safe step
  was on the board; she is cornered about as often as a top-three queen. Three in ten deaths are not rams: a boxed-in queen cuts
  herself down to 2 segments (SSS and forgot give away 2 from the tail and wait: 0 cuts in 1,135 games), team-mates step onto her
  last exit, and on maps of 600 cells or fewer our queen rules are off and she dies at twice the rate.
- **Enemy heads near her, and where she sits.** On average she lives where SSS's and forgot's queens live and is seen as often.
  What differs is the price of being far out: rammed 1.8 times per 1,000 rounds within 5 cells of her start and 5.5–8 beyond 10.
- **Cells moved.** 17–21 different cells per 25 rounds for every team; queens are not parked, with two exceptions below.
- **Zhe's "stay at 2 and circle on 4 tiles".** test4 does exactly this in every game (a quarter of its queen's rounds), and SSS on
  two maps. test4's queen is almost never rammed on the loop (1 of 38 rams by the top three) and dies at half our queen's rate.
  From the rules: one 2-long can never catch a 2-long queen in open water if she steps away; on a strict loop her next cell is
  known, so she must leave the loop when a head comes within 2–3 steps. In the one case read, test4's queen left the loop, was
  safe, stepped back onto it and was rammed.
- **Guards.** No top team escorts. Intruders near their queens die because ordinary small dragons nearby ram them, which ours do
  not do on big maps.

None of the queen rules alone is worth much (+0.3 to +1.5 points for the best of them), because a queen who avoids one death
meets the next. The numbers are in `deep-read-4.md` section 7 for anyone who works on cards #23 and #25.

## 6. Limits

- **Nothing was played.** Every size in this report is arithmetic on games that already happened, or a comparison inside them.
  What a rule does to wins can only be estimated.
- **Two opponents.** 313 of our 401 games are against test4 and WHQ as they were this week; we have 21 games against the top
  three. The qualifier is against stronger teams on maps nobody has seen.
- **The size of every candidate is about one point, and no test before the freeze can see one point.** The choice between them
  rests on the recounts in these files.
- **Beliefs** (which dragon a dragon takes for the leader) are readable in 82 games of an earlier live bot only.
- **The amended form of the pick** (a small zone around a visible leader in the feeding phase) is a design read off the counts;
  only the plain form's effects were counted.
- **More length has not turned into wins for us before** (stride, the trade build). The pick may do what it says and still not
  move results, because the extra dragons then meet an enemy that rams at four times our rate on big maps.
- **Win rates per length band** were earned with the bot as it is and are not a property of the band; they are used here only
  for rough sizes.
- The first red team's "largest uncovered gap" (the longest-dragon race at level total length) turned out to be about half an
  artefact: a team that has already fed its leader has spent length, so "level at round 400" hides that it was richer. What is
  left is about 8 wins in our 143 races against the top three's conversion, with a range from 0 to 16.

## 7. What changed since the first run, and why

- **The pick changed.** The first run (one session, no independent checks, 1,754 games) picked "ram the enemy queen whenever in
  reach" at +2 to +3 points. That idea survived every recount as a behaviour gap, but its size came down to about +1, and its
  tested half turned out to have been online twice with no change in results. It is now the runner-up.
- **Why.** The sub-sessions the first run could not start did the work this time. The economy read found the drop in pearl-taking
  at our own switch round; the race read showed with the dragons' own pings that it is the pearl zone and that the leader does not
  need it before feeding; two red-team rounds recounted it and cut the first version down to the amended rule.
- **Corrections to the first run's notes:** our 401 games are eleven runs with several builds, not one bot; the queen's "deaths by
  her own move" and "no action" deaths are one kind of event (boxed in); the low ram rate at meetings is a big-map behaviour that
  comes from a map-size switch in our code (on smaller maps we already ram like everyone else); "economy alone" claims need
  care, because two attempts to raise it did not win more.

## 8. Files

- `REPORT.md` (this file), `card-draft.md` (the idea card, not posted), `SUMMARY-ko.md` (short Korean summary).
- `findings.md`: the fact sheet. `hypotheses.md`: four candidates. `redteam.md`, `redteam-2.md`: the two red-team rounds.
- `deep-read.md` (Vibing++), `deep-read-2.md` (SSS, forgot), `deep-read-3.md` (economy), `deep-read-4.md` (our queen),
  `deep-read-5.md` (the race).
- Scripts: the lead's (`lib.py`, `extract*.py`, `recount3.py`, `check_a2.py`, `check_a4.py`, `behind.py`, `leaderrace.py`, `qearly.py`,
  `bybuild.py`; outputs in `out2/`) and each sub-session's (`a_`, `b_`, `c_`, `d_`, `h_`, `x_`, `e_`, `y_` prefixes, outputs in the
  matching `*_out/` directories). Sub-session briefs: `subA.md` to `subC2.md`.
- `run1/`: the first run's report, card draft, summary and notes.
