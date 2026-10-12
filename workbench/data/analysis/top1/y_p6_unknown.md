## 6. What I could not determine

1. **What any of the rules does in a real game.** I ran none. Every size in this file is arithmetic on games that
   were played.
2. **Whether more pearls become more wins for our bot.** The pearls of 3z are measured (a step at our own switch
   round). The wins are read off bands and curves that were earned with the bot as it is, and the one time our
   big-map economy was raised by a fifth it won 0 of 12. This is the open question of the candidate I would send.
3. **What small dragons would do with the pearls of feeders if the zone were gone.** Today they leave 3.8 to 4.8 of
   them a game in rounds 400-449 on small maps and the leader gets about 40% of those. Whether they would take a
   third of them or four fifths decides whether the plain version of 3z costs the small-map leader 2 segments or 5.
   Feeders themselves never get the eating bonus, so it depends on how many of the dragons near a leader are not
   feeders; I did not count that.
4. **What the exact amended form does** (a zone only in the feeding phase, only around a leader in view, radius
   about 4). It is read off the counts, not counted.
5. **Why today's builds recover faster after a leader cut than the earlier bot** (20 rounds, 15, and 5 to 10 in
   the test builds). The log says none of the builds changed the leader or feeding code; their pings are sealed and
   I left them sealed. The belief numbers of candidate 5 therefore describe a bot we no longer run, and I cannot say
   how stale the record is in the current one.
6. **Whether the heir of a cut really takes its own stub for the leader**, as the code says it should (a new
   dragon with an empty record hears the old report like everybody else). The heir's own pings would show it; I
   followed the feeders near a cut, not the heir.
7. **Whether fast naming of the heir makes it grow faster, inside the same game.** 25 usable cuts in the readable
   games, 5 of them "fast". No power.
8. **What the other teams know.** A replay shows that forgot, Vibing++ and WHQ feed through a cut and that SSS does
   not; it does not show a record. Vibing++'s and test4's small dragons take fewer corpse pearls near their leader
   late in the game; whether that is a rule or feeders on their way to die cannot be seen.
9. **How many spawns a blocked tile costs.** Spawn intervals are hidden. Declined pearls block their tiles for 45
   to 93 tile-rounds per game per 50 rounds; on a fountain that is several pearls, elsewhere none.
10. **Queen-feeding games.** When our queen is fed, the record names her and the zone lies around her. 3z would
    remove that too. Our queen is alive at round 300 in about a seventh of our games and both queens are alive at
    the end in 14; I did not separate those games, and the amended form (zone kept in the feeding phase) leaves them
    as they are.
11. **Why the zone was put in, and why 9 cells.** Not in `work/plan.md`, which starts on 29 September.
12. **Whether the race gap against the top three is real or 30 games.** Against test4 and WHQ the top three win 69%
    at level potential and we 44%; their side of that is 30 races.
13. **Why we never win from under half the enemy's potential** (0 of 48; the top three 5 of 43). Five of the eight
    wins of section 1 sit there. I did not read those five games.
14. **Why our leader cuts so often, and its heir again so soon.** It is the number that separates us most from
    every other team in the last hundred rounds, and no candidate works on it.
15. **Anything about maps nobody has seen.** 3z gains most on maps over 1,200 cells (5 of the 15 known maps) and
    wherever the fountains lie near where our long dragons grow.

## 7. Counts I made

All scripts are in this directory and are my own; they use `lib.py` (the replay walker) and `games.csv`, and none
plays a game. Outputs are in `y_out/`. Filter everywhere: opponents rated 2000 or more, map Schooltime left out. I
read `e_belief.py` for the layout of a readable ping and the other sub-sessions' scripts to learn what they counted.
No key or derived value was copied anywhere; sealed pings were counted as unreadable and left alone.

**Walks of the replays**

| Script | What it counts | Output |
|---|---|---|
| `y_lib.py`, `y_r.py` | Shared helpers: the game filter and runs, a small logistic fit, the loader for walk 1, lineage of the final longest | |
| `y_w1.py` | All 1,795 games with a study side, both sides. Every 5 rounds from round 100: units, total length, longest and second longest, potential, potential within 15 cells of the longest, queen. Every split; for splits of a dragon of 6+ the free cells at its head and the longest other own dragon. Every death from round 100 with the free cells at its head when it gave its order, the longest other own dragon, all own heads within 8 path steps, the nearest enemy head. Every corpse pearl eaten (eater, dead dragon). Natural pearls per dragon and 25 rounds, by the leader of the time and by length class | `y_out/w1/<game>.json` |
| `y_w2.py` | The same games. For our side in readable games, every round from 150: how many own dragons name a longest dragon, a dead id, a living dragon under half the longest, themselves; how many could feed the longest by geometry and name it. For every leader cut of either side from round 150: free cells, room in front of the stub, own heads near; the own dragons that could feed the heir near the cut, followed for 30 rounds (distance to heir and stub, how and where they died, and in readable games what they named each round); the heir's length each round; why the follow-up ended | `y_out/w2/<game>.json` |
| `y_w3.py` | The same games, both sides. Every pearl turn, by 25 rounds, own length, distance from the pearl to the true longest and its length class, distance to the zone head the dragon itself named (readable games), natural or corpse pearl; the same per 10 rounds. Every pearl declined inside a zone and its fate (who ate it, after how many rounds, how often it was declined). Dragon-rounds of small dragons and natural pearls they ate, inside and outside the true zone and the named zone. Natural pearls by eater class, inside and outside the zone. Every turn of a team's longest dragon of 8+: free cells, what blocks, small own heads near | `y_out/w3/<game>.json` |
| `y_w4.py` | Our 401 games: every feeder ("no order") death of ours from round 150 with the id, length and age it named one turn before (readable games), that dragon's true length, distance, path steps and whether it was in view; the true longest; the longest own head in view within 3 cells | `y_out/w4/<game>.json` |
| `y_w4b.py` | Our 401 games: for every feeder death, how many segments of the dragon it died next to were inside its own view | `y_out/w4b/<game>.json` |
| `y_dbg.py`, `y_dbg2.py`, `y_dbg3.py`, `y_peek.py`, `y_env.py` | Checks: event order around deaths and splits, my board-occupancy mirror against the walker's bodies, the direction code of recorded moves, the game filter (401 / 503 / 502 / 632 game-sides), the Python in use | |

**Tables**

| Script | What it counts | Output |
|---|---|---|
| `y_a.py` | Claim A: races and wins by group; won of games by own / enemy total length at round 400 and by potential at rounds 300, 350, 400, by map class and against test4 and WHQ; total length at rounds 250 and 300; the first red team's band looked at again; a logistic fit per group and footing (the edge at ratio 1, the slope); a fitted footing (final longest from longest and rest); our races on the top three's curve with a resampling range; the level band on nine footings; share of potential in the longest | `y_out/a.txt` |
| `y_a2.py` | Claim A: fine bands of the potential ratio with our races at the top three's rates; a pooled fit with a term for our side; medians of final longest over potential; who has converted by round 400; our level races by map and opponent | `y_out/a2.txt` |
| `y_c5a.py` | Candidate 5 from positions: leader cuts per race and phase, with a free cell; cuts of the final lineage and lost races they would turn; growth of the longest per 25-round window with a cut inside / only before / none, by build, run, opponent, map class, team, leader length, and inside the same game; deaths by choice by what stood within 3 and 8 steps and who ate the pearls; the clock after a cut; the longest around a cut | `y_out/c5a.txt` |
| `y_c5b.py` | Candidate 5 from the pings and the cut follow-ups: readable games per run; what our dragons name per 25 rounds; rounds until half name the longest after a cut; growth by the share naming it, with cuts taken out and by rounds since the cut; what the feeders near a cut do within 25 rounds, per team; the heir's growth; how soon the heir cuts again | `y_out/c5b.txt` |
| `y_c5c.py` | What our feeders die next to: the true longest (within 3 steps, or across a wall), another big dragon, a fresh stub, a short dragon; who ate the pearls; by map class, build, opponent and map | `y_out/c5c.txt` |
| `y_c5d.py` | Candidate 5's size and backfire: unfed length near and far from the longest at the end; the gap between our two longest dragons during feeding; lost races that turn under three readings of the misdirected pearls; A5's what-ifs recounted; margins of our races; the "see it is long" test on today's deaths | `y_out/c5d.txt` |
| `y_c5e.py` | The naming curve after a cut on every leader cut of the readable games from round 300; when half of the feeders first name the heir; fast against slow naming | `y_out/c5e.txt` |
| `y_c5f.py` | The earlier bot against today's builds: the clock after a cut and the three kinds of window for readable games, sealed live-bot games and test builds | `y_out/c5f.txt` |
| `y_c5g.py` | The heir's growth 3 to 25 rounds after a leader cut, per team and map class, and by whether the cut was made with a free cell | `y_out/c5g.txt` |
| `y_c3a.py` | Candidate 3z: the free-pearl rate around the switch per team, build and run; inside against outside the zone by belief and by the true longest, natural and corpse pearls, by distance; how much of the fall comes back with the zone off; by map; other teams near their own longest | `y_out/c3a.txt` |
| `y_c3b.py` | Candidate 3z: the fate of pearls declined in a zone; natural pearls per 50 rounds by team, leader and length class on the same games, next to the other side; pearls per 100 dragon-rounds inside and outside the zone before and after the switch; by map | `y_out/c3b.txt` |
| `y_c3c.py` | Candidate 3z: natural pearls per 25 rounds and per small dragon around the switch; where the final lineage's segments come from in our races and race wins; declined pearls the lineage ate, against the margins of our wins; the leader boxed in, per team and phase; extra pearls at the before-switch rate per dragon-round; our win curve on total length and the wins on it | `y_out/c3c.txt` |
| `y_c3d.py` | Small dragons near their own longest, every team: natural pearls per 100 dragon-rounds inside and outside 9 cells; our 401 games by map class, ending and whether they reach the switch | `y_out/c3d.txt` |
| `y_misc.py` | Rounds until half name the longest with and without the cuts after which it never happens; margins by map class; growth of the longest after round 400 by build and run | `y_out/misc.txt` |
| `y_build.py`, `y_mdcheck.py` | Assembles this file from `y_p0_head.md` to `y_p6_unknown.md`; checks its tables and the file names in it | `redteam-2.md` |

Checks against earlier numbers. `y_w1.py` reproduces game 1 of A5's reading list to the unit (1027819: total length
140 : 157, 136 : 131, 156 : 154; longest 4 : 8, 13 : 58, 32 : 77; potential 84 : 92, 85 : 99, 99 : 117). `y_a.py`
reproduces every count of A5's footing tables and the first red team's race table. `y_c5a.py` reproduces A5's
window, cut and death tables within a few windows or one point; `y_c5b.py` the belief table within two points.
`y_c3a.py` reproduces the first red team's 10-round blocks around both switch rounds exactly (84, 84, 64, 60 and 85,
83, 64, 51).
