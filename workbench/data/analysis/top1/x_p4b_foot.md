## All candidates, attack I: the footing, and what B did not propose

### The footing itself

B puts every candidate on "points of win rate" from two kinds of what-if (strict, realistic) and from win rates per
economy band at round 300. I recounted the tables (`x_foot.py`, `x_out/foot.txt`; `x_c1e.py`): the end-state table
and the band table reproduce exactly (12 of 168, 16 of 61, 6 of 12, 17 of 27; +33.9 and +60.8 wins). Four things are
wrong with leaning on it.

1. **It leaves out a third of our games and more than half of our wins.** 133 of our 401 games are over before round
   300, all but two on maps of 1,200 cells or fewer, and we win 61 of them (46%). In the 268 games that reach round
   300 we win 51 (19%). So against teams rated 2000+ we are close to level in the short fights on the smaller maps
   and far behind in every game that goes long. None of B's numbers sees the first kind of game, and two candidates
   act in it (candidate 2 changes what our queen does on small maps; candidate 4 adds trades).
2. **"The economy is the larger gap" is not safe to say.** The economy what-if (our win rate per band with the top
   three's mix of bands, +60.8 wins) takes 93 of its 112 wins from our two upper bands, which hold 12 and 27 games.
   With the 80% ranges of those two rates it is +32 to +90 wins. The conversion what-if (their rates, our mix) is
   +25 to +44. The two ranges overlap, and the two effects multiply rather than add.
3. **The band rates are not a property of the band.** The "realistic" readings re-score a changed game with "our own
   win rate for the band it lands in". But those rates were earned with the bot as it is. Two examples from this
   file: in the lowest band our record with both queens dead depends on when her queen died (0 of 49 before round
   300, 4 of 23 after; candidate 1); and on maps over 1,200 cells our rate inside a band was earned with a leader
   that starts at round 150, which is the thing candidate 3 removes.
4. **The ranking is by confidence and cost, not by points.** All four ranges lie between 0 and +3 points and overlap.
   That is a fair way to rank, but it should be said that way: the table does not show that candidate 1 is worth more
   than candidate 3 or 4, only that it is surer and cheaper.

A different footing that I find more useful, how our 401 games end (`x_foot.py`):

| How it ended | games | won | on maps over 1,200 cells | on smaller maps |
|---|---|---|---|---|
| wipe-out before round 300 | 133 | 61 | 0 of 2 | 61 of 131 |
| wipe-out from round 300 on | 37 | 6 | 0 of 11 | 6 of 26 |
| round 500, both queens dead (longest dragon decides) | 143 | 41 | 12 of 65 | 29 of 78 |
| round 500, our queen dead, hers alive | 73 | 0 | 0 of 33 | 0 of 40 |
| round 500, both alive | 14 | 3 | none | 3 of 14 |
| round 500, ours alive, hers dead | 1 | 1 | none | 1 of 1 |

On it, candidate 1 works on the fourth row (73 certain losses, which become longest-dragon games), candidate 2 on
the third and fourth (a living queen wins the third outright), candidates 3 and 4 on which row a big-map game lands
in. Nothing proposed works on the third row as it is, and that is where the next item sits.

### Dismissed too quickly: the longest-dragon race

B drops "start feeding earlier" because it was tried (three trials, neutral) and because "the ceiling is small once
the economy is held fixed" (+6.9 wins). I recounted the race by total length at round 400 and by map class
(`x_race.py`, `x_race2.py`; outputs `x_out/race.txt`, `x_out/race2.txt`). Round-500 games with both queens dead:

| Maps of 1,200 cells or fewer; own / enemy total length at round 400 | meow: won | our longest at round 300 / 400 / end against the enemy's | top three: won | their longest at 300 / 400 / end against the enemy's |
|---|---|---|---|---|
| 0.8 to 1.25 (level) | 9 of 30 = 30% | 5 / 12 / 28 against 7 / 16 / 39 | 22 of 40 = 55% | 7 / 21 / 46 against 7 / 18 / 42 |
| over 1.25 (ahead) | 15 of 18 = 83% | 4 / 13 / 36 against 4 / 12 / 18 | 77 of 83 = 93% | 6 / 15 / 39 against 4 / 5 / 13 |

| Maps over 1,200 cells | meow: won | our longest at 300 / 400 / end against the enemy's | top three: won | theirs |
|---|---|---|---|---|
| 0.5 to 0.8 (behind) | 6 of 23 = 26% | 19 / 25 / 51 against 20 / 38 / 52 | 17 of 49 = 35% | 12 / 35 / 41 against 15 / 35 / 59 |
| 0.8 to 1.25 (level) | 4 of 6 | 27 / 46 / 58 against 20 / 33 / 53 | 73 of 116 = 63% | 16 / 41 / 60 against 14 / 30 / 50 |

Two things follow.

- **On the smaller maps we lose level games on the longest dragon that the top three win.** With total length level
  at round 400 we win 30% and they win 55%; our leader is 12 long then and theirs 21, from the same 5 to 7 at round
  300. Over all maps, **14 of our losses came with at least as much total length as the enemy at round 400**
  (`x_out/race.txt` lists them: five on Maze, five on Portals, three on weakhold, one on Slithery Fight; for instance
  1027819, total 136 against 131, longest 13 against 58). At the top three's rates for games at 0.8 or better we
  would win about 40 of those 55 games instead of 29: **+10 wins, 2.7 points**. That ceiling is larger than what I
  would defend for any of the four candidates, B's pick included. It is a ceiling and not a rule: the direct trials
  (feeding from round 330 or 300) were neutral, the online one on an older bot and the old map pool. But "the
  ceiling is small" is not a reason to drop it; +6.9 wins, B's own figure, is as much as B claims for candidate 1.
- **On the big maps the picture is the reverse, and it bears on candidate 3**: there our leader is as long as a top
  team's at the same economy and we convert as well as they do (see candidate 3).

### The other dismissed items

- **Team-mates off the queen's last exit, the queen rules on every map, dead ends:** I have nothing to add to B;
  each was tried in some form and lost or did nothing.
- **"Keep the queen near her team" / defenders near the queen.** B says where she lives is not what differs. That
  holds in my count as far as it can be tested (candidate 2, items B and C): once an enemy head is within 3 steps
  of a 2-3-long queen, the number of own heads near her does not lower her risk for any team, and for ours it goes
  with a higher one.
- **Hunters that walk to her (the dropped half of the first run's H1).** B's reason stands and the second online
  trial confirms it: qh31b's hunters raised rams on her queen from 8 to 13 games of 28 and the end state did not
  move.
