## Counts I made for this file

All scripts are in this directory; outputs are in `h_out/`. Every script reads the lead's and the sub-sessions'
per-game files or walks the replays with `lib.py`; none plays a game. Filter everywhere: opponents rated 2000 or more,
map Schooltime left out.

| Script | What it counts | Output |
|---|---|---|
| `h_base.py` | One row per game and side for meow, the three top teams and meow's opponents: result, end type, run and build, units / total / longest / queen length at rounds 50-450 and at the end, both queens' deaths, every ram chance on either queen (from `q/`, `q3v2/`, `games.csv`) | `h_out/base.json` |
| `h_states.py` | How games end by queen state; the same inside economy bands; our wins if one factor at a time were at the top three's level | `h_out/states.txt` |
| `h_econ.py` | Win rate by own / enemy total length at round 300 in fine bands and by map class; expected wins if our total length at round 300 rose by 10-100%, by the band table and by a smooth fit | `h_out/econ.txt` |
| `h_c1.py` | In-view chances on the enemy queen taken, by team, attacker length, round, own queen alive, attacker = longest, paid steps; games by chance and kill; the what-if "her queen dies on our first untaken chance" under all readings, for any attacker length and for the qh31 limit; wins against losses per team | `h_out/c1.txt` |
| `h_c1walk.py` | Walks our 122 games with an untaken in-view chance: what the dragon did instead on each of the 347 turns, which of our trade rule's three tests failed, what became of the dragon that would have rammed, what the rule would have spent | `h_out/c1walk.json`, `h_out/c1walk.txt` |
| `h_c1flips.py` | The 25 round-500 losses with her queen alive and an untaken in-view chance, one line each: the first chance, what became of the dragon that would have rammed, and every reading of the flip (also with that dragon removed from our final lengths: still 13) | `h_out/c1flips.txt` |
| `h_c1enemy.py` | What our opponents build when their queen is dead: their longest dragon at the end, and its share of their total length at round 400, with the queen alive against dead before round 300; the 25 flippable losses re-scored with that share | `h_out/c1enemy.txt` |
| `h_c1long.py` | Walks our 401 games for the attackers the chance files skip: dragons of 13 or more with her queen in view and within 12 free steps (16 turns in 9 games), with the state of each game | `h_out/c1long.json`, `h_out/c1long.txt` |
| `h_c1recount.py`, `h_c1check.py` | Independent recount of the chance numbers for our 401 games, written without the lead's code and with a stricter path test (435 chances, 99 taken; the lead's 446 and 99); the 25 flippable losses and the flip counts under that stricter test (unchanged) | `h_out/c1recount.json`, `h_out/c1recount.txt`, `h_out/c1check.txt` |
| `h_joint.py` | Candidates 1 and 2 alone and together under the strict and the two realistic readings (A4's survival tables rebuilt) | `h_out/joint.txt` |
| `h_c2.py` | How the own queen ended in wins and in losses, per team; our games by queen rules on / off; each part of candidate 2 (and the parts left out) under the three readings | `h_out/c2.txt` |
| `h_c3.py` | Walks 791 games: a free pearl next to the head eaten or not, before and after our switch round, by whether a longer own dragon is within 9 cells of the pearl and by the dragon's own length; what became of declined pearls; how often dragons of 4 and of 5-9 split | `h_out/c3/`, `h_out/c3.txt` |
| `h_c3dist.py` | Walks our 401 games: after the switch round, the share of free pearls a 2-3-long takes by the distance from the pearl to the nearest longer own dragon (a test of the 9-cell zone), for us and our opponents | `h_out/c3dist.json`, `h_out/c3dist.txt` |
| `h_c3b.py` | Units, total length and longest dragon at rounds 100-450 by map class and team; our big-map wins against losses | `h_out/c3b.txt` |
| `h_c3wins.py` | Our 12 wins on maps over 1,200 cells one by one: the leader at rounds 150 / 300 / 400, the margin on the longest dragon; the close both-dead losses there | `h_out/c3wins.txt` |
| `h_c3game.py` | The count of `h_c3.py` for single games, per 50 rounds and side | `h_out/c3game.txt` |
| `h_c4.py` | Small intruders near the own queen rammed by her team, live bot against the trade-on-contact build and the other teams; the tc30 trial's wins against what our band win rates predict | `h_out/c4.txt` |
| `h_c4walk.py` | Walks the same 791 games: every turn on which a dragon of 4 or shorter could ram an enemy dragon of 4 or shorter (next cell, or 2-3 steps away), taken or not, by relative length and by whether it had as many own heads as enemy heads in view | `h_out/c4w/`, `h_out/c4walk.txt` |
| `h_c4pearls.py` | Walks the same 791 games: every ram between two dragons of 4 or shorter, by relative length and head count at its start, the lengths lost on each side and who ate the pearls of the two corpses: the swing per ram and per game for the side that starts it; wins against losses | `h_out/c4p/`, `h_out/c4pearls.txt` |
| `h_race.py` | Round-500 games with both queens dead: win rate by total-length and by longest-dragon ratio at round 400; which of the two predicts the result; growth of the longest dragon | `h_out/race.txt` |
| `h_peek.py`, `h_build.py`, `h_mdcheck.py` | Show the structure of the per-game files; assemble this file from `h_p*.md`; check its tables and file names | |

Checks against earlier numbers: `h_states.py` reproduces the lead's end-state table (1 of 1, 3 of 14, 41 of 143, 0 of
73) and band table (12 of 168, 16 of 61, 6 of 12, 17 of 27); `h_c1.py` reproduces the lead's chance table (99 of 446)
and the 13 flips of `an4b.py`; `h_joint.py` and `h_c2.py` reproduce A4's worth table within one win (26 strict, 8.6
against A4's 7.4 and 2.6 against 2.4 for the core rule; my realistic numbers also count losses in which both queens
would be alive, at our 3-of-14 rate). `h_c3.py` finds the fall in eating that A3 and the lead found with their own
scripts (83% to 58% here, 82% to 59% and 80% to 56% there). `h_c4walk.py`, summed over the head-count split, gives
the lead's `recount3.py` figures for the top three on big maps (same-length meetings rammed 37% against 34-40%,
shorter enemies 24% against 23-25%) and for our live bot (8% against 9%).
