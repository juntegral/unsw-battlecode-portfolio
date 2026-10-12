## 7. Counts I made

All scripts are in this directory and are my own; they use `lib.py` (the replay walker), `games.csv` and the smoke
folders, and none plays a game. Outputs are in `x_out/`. Filter unless said: opponents rated 2000 or more, map
Schooltime left out. I read the other sub-sessions' scripts only to find out what they counted.

**Walks of the replays**

| Script | What it counts | Output |
|---|---|---|
| `x_games.py` | My game list: the 2,343 games of `games.csv` plus 135 smoke-test games that are not in it (qh31b old and new against test4, WeHaveQuizzes and dev test 1; qn23) | `x_out/games.json` |
| `x_c1.py` | All 2,478 replays, both sides. Every turn of a non-queen dragon with the enemy queen's head in its view or in Manhattan reach: three path tests (strict, strict inside the own view, walls only), head counts in view, both teams' units and lengths at that moment, what the dragon did, whether it rammed her, what became of it. Every queen death with its killer. A timeline every 10 rounds. The final board | `x_out/c1/<game>.json` |
| `x_c2.py` | All 2,478 replays, both queens. Every queen turn with an enemy head in her view or near: the four one-step moves and whether each is in an enemy's reach (plain reach and pearl-paid reach; enemies in view and all), the room behind each, where she really ended and whether that was in reach on the real board, her death and its killer; every queen split; queen-rounds; whether she could reach the enemy queen | `x_out/c2/<game>.json` |
| `x_c34.py` | All 2,478 replays, both sides. Candidate 3: a free pearl on the next cell taken or not (dragon of 2-4, no enemy head in view, a way on), by 10-round block, own length, distance to the nearest longer own dragon and its length; splits and dragon-turns by length class; pearls eaten by class. Candidate 4: every turn on which a dragon of 4 or shorter can reach a small enemy head, by head count, relative length and distance, rammed or not; every ram between two small dragons with who ate the pearls of both corpses | `x_out/c34/<game>.json` |
| `x_c2vis.py`, `x_c2vis2.py` | Our 401 games: for every turn of our queen with an enemy head in view, which one-step moves are "in reach" under four models (the bot's existing pieces: visible parts, no pearls; the same plus one segment; true length; true length with pearl-paid steps) | `x_out/c2vis.json`, `x_out/c2vis.txt` |
| `x_c1p.py` | Our 401 games, both sides: in-view chances on a queen that exist only through a pearl-paid step, taken or not | `x_out/c1p.txt` |
| `x_eye.py`, `x_c1pick.py`, `x_c2pick.py`, `x_pick34.py` | Draws the board at the start of one dragon's own turn; picks the turns looked at by eye for each candidate | `x_out/c1_eye.txt`, `x_out/c2_eye.txt`, `x_out/c3_eye.txt`, `x_out/c4_eye.txt` |

**Tables**

| Script | What it counts | Output |
|---|---|---|
| `x_c1a.py` | The chance table against B's: by team, attacker length, round, own queen, paid steps, head count, queen length; games with a chance and no ram; queen ids | `x_out/c1a.txt` |
| `x_c1far.py` | Rams on a queen that no plain-reach chance explains: 284 of 2,128 are moves longer than the plain reach | `x_out/c1far.txt` |
| `x_c1b.py`, `x_c1b2.py`, `x_logit.py` | Take-up per team against rating over all teams; the first chance of each game taken or not, inside the same team, economy band and own-queen state; logistic fits holding economy, round, own queen, team and the local head count fixed | `x_out/c1b.txt`, `x_out/c1b2.txt` |
| `x_c1c.py` | Win rate by state (round, economy band, own queen, her queen) for us, the top three and all 2000+ teams; how games ended after real rams against the same state with her alive; what a team builds after its queen dies; rams by a team's own longest dragon | `x_out/c1c.txt` |
| `x_c1d.py` | Our 401 games by what happened at the first chance; B's 25 candidate games one by one with the lenient and hard readings recomputed; where they sit by opponent, map and run; our take-up by opponent; how often each team's queen offers a chance and to whom | `x_out/c1d.txt` |
| `x_c1e.py` | Round-500 end states by queen state per team (check of B's footing table) | `x_out/c1e.txt` |
| `x_c1f.py`, `x_c1pairs.py` | Every run of ours recounted from its replays (qh31, qh31b, stride, passage2, tc30, qn23, ladder): wins, chances taken, rams on her queen, end states, our queen; old/new pairs by opponent and map; our queen's death round in each pair | `x_out/c1f.txt`, `x_out/c1pairs.txt` |
| `x_c1g.py` | Backfire of candidate 1: our wins in which the rule would have fired and whether they stand without the attacker; untaken chances by attacker (our longest, 10+, 13+, outnumbered); what the rule would spend; both-dead games by when her queen died | `x_out/c1g.txt` |
| `x_c2a.py` | The queen table against A4's and B's, under the pearl-paid and the plain reach model: turns in reach by choice, how each queen ended, cuts and sheds | `x_out/c2a.txt` |
| `x_c2b.py` | The same situation by what she did (fate that round, within 10 and 50 rounds, at the end); our queen's survival from each round; the deaths each part of candidate 2 touches and what they are worth; the turns the rule would change; her own rams | `x_out/c2b.txt` |
| `x_c2c.py`, `x_c2cut.py` | What follows a cut and a shed, per team; ram risk by own heads near the queen; the mirror (turns in reach, punished or not) per opponent; our cuts one by one and the coiled start on Slithery Fight | `x_out/c2c.txt`, `x_out/c2cut.txt` |
| `x_pair.py` | Candidates 1 and 2 alone and together on our round-500 losses, strict and realistic | `x_out/pair.txt` |
| `x_c3a.py`, `x_c3stall.py`, `x_c3wins.py` | The pearl-taking rate by map class, team and round, around both switch rounds, by distance to a longer own dragon; the same in wins, losses and economy bands; splits; units, total length and longest dragon on the same games through the switch; our 12 big-map wins one by one | `x_out/c3a.txt`, `x_out/c3stall.txt`, `x_out/c3wins.txt` |
| `x_race.py`, `x_race2.py`, `x_race3.py` | Round-500 games with both queens dead: win rate by total length at round 400 and map class, the longest dragon of both sides at rounds 150 to the end; logistic fits of win on total length and longest dragon at rounds 300 and 400; candidate 3's trade priced with those fits | `x_out/race.txt`, `x_out/race2.txt`, `x_out/race3.txt` |
| `x_c4a.py` | Ram chances on small enemy heads taken, by head count, relative length and distance; rams started per game and the swing per ram; wins against losses; the trade-on-contact build against the live bot on big maps | `x_out/c4a.txt` |
| `x_foot.py`, `x_small.py` | B's band table with 80% ranges; the two what-ifs with ranges; how our games end, by map size | `x_out/foot.txt`, `x_out/small.txt` |
| `x_load.py`, `x_show.py`, `x_build.py`, `x_mdcheck.py`, `x_peek.py` | Shared loader; prints one per-game file; assembles this file from `x_p*.md`; checks its tables and file names; a first look at `games.csv` | |
