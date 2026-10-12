# Islands: why we never win there (team 1119, written 7 Oct 2026, 24 main games, 1 won)

**What loses the games.** From round 151, the bot's own switch round on layouts above 1200 cells, our dragons stop eating and splitting, and on this layout we lose as many dragons every 50 rounds as we have, so the team is not refilled: about 40 dragons at round 150, 16 at round 300, theirs 61. 9 games were level or ahead at round 150 and 8 of them were lost this way; the other 15 were behind before it.
**The change.** One switch, LEADER_FULL_UNITS (off = 0, test 56): the three leader rules that start at that round wait until we hold 56 dragons or the feeding phase begins.
**How sure.** High on the behaviour and its trigger (the step is in 22 of 23 games, the same step sits at round 301 on small layouts, and the lines are in the code). Low to medium on games won: the ladder has no game without the step, 15 of the 24 are lost earlier for another reason, and card 49 on the same phase was flat online.

Labels: [M] measured by my scripts in dossier/work/ on the 24 games in per-game.jsonl (isl_trace.py clusters and rams, isl_zone.py skips, eating and splits, isl_lead3.py leader status, isl_view.py single dragons), or summary.md where named. [C] read from battlecode/mybot2/main.cpp, line given. [E] my estimate. "Fast tile" = one of the 26 tiles maps.json marks fast (84 percent of all pearls here). "Skip" = a non-queen turn that starts beside a pearl and eats nothing.

## What happens

The three gaps from summary.md table C that the 15 normal layouts do not have, r101-300, ours / theirs [normal]: dragons alive at the end 16.2 / 61.5 [37.2 / 39.6]; pearls 234 / 787 [322 / 396]; splits 78.5 / 219 [123 / 132]. The marker beside them: adjacent pearl missed 45.0 / 29.3 percent [27.7 / 25.0]. All three open in the same round [M]:

| per game, 24 games | r101-150 ours | r151-200 ours | r101-150 theirs | r151-200 theirs |
|---|---:|---:|---:|---:|
| pearls eaten on fast tiles | 58.5 | 23.4 | 98.8 | 92.0 |
| pearls eaten elsewhere | 55.0 | 32.1 | 92.4 | 107.5 |
| splits | 42.3 | 16.3 | 59.1 | 54.7 |
| deaths | 41.2 | 29.5 | 53.9 | 50.4 |
| dragons alive (mean) | 40.5 | 35.6 | 51.7 | 55.3 |
| skip share, no enemy head within 2 tiles | 0.30 | 0.53 | 0.24 | 0.27 |

Every game [M]. "a>b" is r101-150 then r151-200; left of the colon ours, right theirs. Alive is ours:theirs.

| game | opp | end | alive r150 | r200 | r300 | fast-tile pearls | splits | skip % |
|---|---:|---|---|---|---|---|---|---|
| 1241403 | 1934 | lost, longest | 37:62 | 42:64 | 25:63 | 52>25 : 104>93 | 46>17 : 86>84 | 23>54 : 29>30 |
| 1244936 | 1974 | lost, longest | 33:62 | 17:63 | 8:63 | 37>20 : 121>106 | 26>7 : 66>64 | 23>52 : 31>31 |
| 1250698 | 1952 | wiped r455 | 45:64 | 32:63 | 20:64 | 66>28 : 99>91 | 44>21 : 42>47 | 25>50 : 21>17 |
| 1252500 | 1817 | lost, longest | 44:63 | 20:63 | 7:63 | 60>13 : 100>112 | 45>17 : 42>51 | 27>33 : 20>20 |
| 1255595 | 2020 | lost, longest | 61:34 | 56:37 | 49:52 | 84>70 : 77>79 | 55>45 : 56>73 | 22>43 : 23>18 |
| 1255622 | 1934 | lost, longest | 29:64 | 18:64 | 14:64 | 36>3 : 124>102 | 32>3 : 96>66 | 35>54 : 24>38 |
| 1256114 | 2107 | lost, queen | 57:58 | 31:59 | 4:58 | 72>20 : 100>96 | 62>11 : 43>39 | 30>50 : 25>31 |
| 1257760 | 2054 | lost, longest | 60:58 | 44:61 | 22:63 | 91>31 : 89>101 | 61>28 : 60>43 | 27>56 : 17>20 |
| 1263709 | 2022 | lost, longest | 39:63 | 17:62 | 5:62 | 70>20 : 108>101 | 54>13 : 70>57 | 26>64 : 30>34 |
| 1275535 | 1954 | lost, longest | 55:38 | 30:61 | 8:61 | 79>27 : 71>110 | 73>19 : 56>77 | 34>50 : 28>26 |
| 1280136 | 1978 | wiped r387 | 56:49 | 24:62 | 5:63 | 65>22 : 81>99 | 65>13 : 62>57 | 32>56 : 25>30 |
| 1280776 | 1873 | lost, longest | 60:19 | 61:36 | 42:62 | 121>59 : 30>56 | 48>35 : 23>34 | 30>51 : 34>34 |
| 1289228 | 2067 | lost, longest | 22:63 | 12:62 | 7:62 | 19>4 : 129>126 | 16>1 : 77>87 | 31>42 : 27>25 |
| 1291768 | 1876 | wiped r176 | 9:64 | - | - | 36>0 : 120>60 | 37>1 : 69>22 | 23>91 : 27>22 |
| 1293799 | 2061 | wiped r359 | 45:60 | 29:61 | 5:63 | 49>36 : 106>89 | 40>18 : 61>54 | 35>50 : 16>21 |
| 1302119 | 1881 | wiped r285 | 22:63 | 8:63 | - | 38>1 : 127>133 | 28>3 : 85>89 | 31>74 : 19>17 |
| 1303534 | 1927 | lost, longest | 60:31 | 53:52 | 31:64 | 55>43 : 60>79 | 41>34 : 39>70 | 36>51 : 18>20 |
| 1305216 | 2421 | wiped r145 | - | - | - | 0>0 : 145>0 | 0>0 : 50>0 | - |
| 1306465 | 1870 | wiped r260 | 15:63 | 7:63 | - | 24>2 : 136>112 | 16>0 : 65>44 | 40>81 : 23>25 |
| 1312177 | 1869 | lost, longest | 37:63 | 19:63 | 5:59 | 53>27 : 113>107 | 35>11 : 67>65 | 29>40 : 27>26 |
| 1312504 | 2309 | wiped r303 | 32:60 | 13:62 | 1:64 | 59>12 : 102>116 | 49>14 : 48>28 | 27>59 : 18>17 |
| 1322012 | 2180 | lost, longest | 37:63 | 21:63 | 7:63 | 52>1 : 125>119 | 40>4 : 74>52 | 35>76 : 34>45 |
| 1326444 | 1795 | lost, longest | 60:40 | 49:44 | 15:62 | 100>50 : 64>61 | 61>35 : 53>62 | 32>50 : 33>35 |
| 1330859 | 1889 | WON, they were wiped r461 | 60:18 | 58:34 | 46:63 | 87>48 : 41>60 | 42>41 : 29>48 | 30>57 : 42>41 |

- [M] Of the 23 games that reached round 175: our fast-tile eating fell by a quarter or more in 21 (theirs in 1), our splits in 20 (theirs in 6), our skip share rose by 10 points or more in 22 (theirs in 2).
- [M] What it looks like (5 replays opened: 1275535, 1280136, 1302119, 1280776, 1330859). 1280136 r149-151: our dragon 195 eats the fast tiles (17,13), (16,13), (16,12) in three turns. 1275535 r153-158, same cluster: our dragon 303 (length 2) walks the square (18,13) (18,12) (19,12) (19,13) beside three lying pearls on those tiles; a team mate of length 3 is 5 tiles away, no enemy within 6. 1302119 r151-160: our longest dragon 317 (length 5) circles a 2 by 2 block beside four lying pearls in a walled nook at (38-40, 12-13) until two enemy dragons arrive. Their dragons in the same games keep eating (skip 0.19 then 0.17 in 1302119).
- [M] Lying pearls block the tile: pearls born on fast tiles per game per 25 rounds are 77.0 and 73.8 in r100-149, then 61.2 and 54.7, while their eating there does not change. And the team cannot spare the splits: deaths in r101-150 equal our team size (41.2 on 40.5; turnover 1.02), because their dragons are the rammer in 83 percent of head-on meetings (ours rammed 15.7 times by round 100, ramming 3.9; 48.9 against 10.8 in r101-300, per-game.jsonl).
- [M] The 15 games behind at round 150 are a second, earlier fault: from round 50 they hold more of the 11 fast-tile clusters (only theirs 5.3, only ours 3.7 in r75-99) and eat twice the dropped pearls. The switch does not touch it.

## Why, in the code

- [C] 467-468: aggressive = cells <= 1200; grow_round is 300 when aggressive, else LEADER_GROW_ROUND_BIG = 150 (line 46). Three rules hang on "round > grow_round", and nothing else does (1037, 2341, 3329; 3320 only moves it).
- [C] 1037: a dragon longer than 4 never splits again. 1028 with 3328-3329: a dragon that knows nobody longer is "leader" and never splits at any length. Leader = the longest dragon seen or heard of in 25 rounds, itself included (1422, 1746-1771, 1782-1795).
- [C] 2339-2362: every other dragon gets a zone of 9 tiles round that leader's last known position; a pearl there loses EAT_BONUS 300 and costs 600 (5055-5060) and is not a target at all (2954-2973).
- [C] 5049-5054, not tied to the round: a pearl in a pocket under 48 tiles is refused once length + 1 is above half the pocket. It starts to bite when dragons stop splitting and grow; several fast-tile clusters here sit in walled nooks.
- [C] 2666-2676: above 1200 cells we ram only an enemy showing at least max(5, our length + 2) parts, so their dragons of length 2 to 4 ram ours and are never rammed.
- [M] Not separated: which of the three rules does it. The skip share rises alike for dragons with a longer mate seen in 25 rounds and the pearl in its zone (0.33 then 0.56), for dragons with no longer mate seen (0.29 then 0.53), and for the longest dragon of the team (0.19 then 0.54, 135 turns). So it is not the zone alone. The switch replaces the one test all three share.

## Which other layouts share the property

Property a bot can measure: **the leader rules start while we hold fewer than 56 dragons.** [M] isl_zone.py, all main games; ratios are r151-200 over r101-150; "full" = our mean count in r101-150 is 56 or more.

| layout (cells; fast tiles) | won | our count r101-150 | eaten, ours / theirs | splits, ours / theirs | our skip | turnover | won, full | won, not full |
|---|---|---:|---|---|---|---:|---|---|
| Islands (2240; 26) | 1 of 24 | 40.5 | 0.52 / 1.11 | 0.41 / 0.98 | 0.30 then 0.53 | 1.02 | 1 of 7 | 0 of 17 |
| Australia (4096; 36) | 9 of 35 | 42.6 | 0.82 / 1.28 | 0.60 / 0.88 | 0.20 then 0.30 | 0.75 | 3 of 4 | 6 of 31 |
| Schooltime 1 (2400; 0) | 8 of 20 | 14.3 | 1.41 / 1.88 | 0.45 / 1.88 | 0.30 then 0.41 | 0.30 | none | 8 of 20 |
| Schooltime 2 (2400; 0) | 10 of 13 | 45.4 | 0.96 / 1.10 | 0.75 / 0.90 | 0.23 then 0.42 | 0.69 | 4 of 4 | 6 of 9 |
| Around UNSW (4096; 32) | 15 of 32 | 59.0 | 0.82 / 1.09 | 0.73 / 1.04 | 0.27 then 0.38 | 0.54 | 15 of 30 | 0 of 2 |
| Slithery Fight (1701; 122) | 18 of 37 | 58.1 | 0.66 / 1.05 | 0.64 / 0.98 | 0.17 then 0.44 | 1.43 | 17 of 32 | 1 of 5 |

- [M] All six layouts above 1200 cells: with a full board 40 won of 77; without, 21 of 84. The step is on all six; it is paid where the board is not full. Slithery Fight has higher turnover but 122 fast tiles, and our count stays at 57.9 after round 150; Islands has 26 for both sides and ours falls. Islands with a full board is still 1 of 7: the count is under 56 in 4 of the 7 by round 200 and in all 7 by round 300, and the rules stay on. That is why the switch tests the count every turn, not once.
- [M] At or under 1200 cells the same step comes at round 301 (r301-400 over r201-300): Maze skip 0.20 then 0.49, eaten 0.83 / 1.06, 23 won of 35; Autarky skip 0.05 then 0.25, 24 of 26. The other 11 small layouts I did not run (findings.md F31 has them pooled: 0.81 against 1.05).

## The card

title: Leader rules wait for a full board
slug: full board
What we tried: Card 49 (LEADER_MIN_LEN 10) made two of the three rules wait for a long leader and left line 1037. Locally its situation never came up (our longest was 18 to 49 at round 150); online 9 of 30 against 9.4 of 30 (docs/SESSION-STATE.md lines 86 and 90). Nothing has tied the phase to our dragon count.
Did it work: not built yet.

### Area
main.cpp: split_child_size() line 1037, refresh_leader_zone() line 2341, is_leader() line 3329. One constant, one helper, three tests.

### Claim
Add "constexpr int LEADER_FULL_UNITS = 0;" (0 = as now; test 56, the value of FEED_CAP_UNITS) and "bool leader_phase() const { return round > grow_round && (LEADER_FULL_UNITS <= 0 || feeding_phase() || ct.get_unit_count() >= LEADER_FULL_UNITS); }". Use it in place of "round > grow_round" on the three lines. Rounds, zone, pocket rule and feeding stay. Claim: a team under 56 dragons keeps eating and splitting after the switch round as it did before it; a team at 56 or more plays as now.

### Evidence
- The step, in 22 of 23 Islands games and on all six big layouts (tables above); the same step at round 301 on Maze and Autarky.
- Before round 151 the same team under the same ramming holds its count (40.1 then 40.8 in r100-149; 55 to 61 in the nine games it leads). Big layouts: 40 of 77 won with a full board at the switch round, 21 of 84 without.

### Expected signal
Replays on layouts above 1200 cells, switch on against off, counted as isl_zone.py does, in games where our count at round 150 is under 56: skip share in r151-200 at most 0.35 (ladder 0.53; 0.30 before); pearls eaten in r151-200 at least 0.9 of r101-150 (0.52); splits at least 0.8 (0.41); dragons alive at round 200 not below round 150. A game that never drops under 56 between the switch round and round 400 plays move for move as with the switch off.

### What would show it's wrong
- The three counts above are not met: the behaviour has another cause; drop the card, do not tune it.
- The counts are met and our dragons at round 300 are still under half of theirs on an Islands-like map: the loss is the earlier fault (ramming and fast-tile clusters), not this phase.
- At or under 1200 cells our longest dragon at the end is shorter and both-queens-dead endings are lost more often than with the switch off: the wait costs the ending the leader phase exists for.

## Against it

- [M] 15 of the 24 games are behind at round 150 and the switch cannot win those; even before the step they out-eat us on fast tiles 98.8 to 58.5. [E] Reach: the 8 lost games that were level or ahead, of which I would expect 2 to 4 to turn.
- [M] The one win has the step too (87 then 48), and the full and not-full split is partly "already behind" (findings.md F40: the count falls after round 150 either way; F31_cost: within a layout the deeper drop is not lost more often).
- [M] Card 49 was flat online, and the leader phase has a purpose: the longer leader at round 300 wins the both-queens-dead ending in 49 of 57 main games (plan.md, F32). On small layouts, where we win six in ten, this switch delays the phase from round 301 to 400 in nearly every game, because no small layout averages 56 dragons. [E] And local opponents may not ram or contest fast tiles as ladder teams do, so the local check can pass or fail for the wrong reason, as it did for card 49.
