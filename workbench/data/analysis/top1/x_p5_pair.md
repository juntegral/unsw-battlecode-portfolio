## 3. The pair 1 + 2, and the pair 3 + 4

### Candidates 1 and 2 together

B says they are "two sides of one idea" and worth +3.1 to +5.3 points together, more than the two alone. I recounted
each sentence of that case (`x_c2c.py` part 3, `x_c1e.py`, `x_pair.py`; outputs `x_out/c2c.txt`, `x_out/pair.txt`).

| B's sentence | B | mine | holds? |
|---|---|---|---|
| Both queens end a turn inside a visible enemy reach equally often (per 1,000 queen-rounds) | 5.4 and 5.4 | ours 5.2, theirs 4.5 | roughly. By opponent it is two different things: test4's queen 3.0 against our 4.5; WeHaveQuizzes's 7.1 against our 5.2 |
| They ram on such a turn, we do not | 71% and 16% | 76% and 19% | yes |
| "Our queen alive, hers dead at round 500": games | 1 of 401; 177 of 1,637 for the top three | 1; 178 | yes |
| Round-500 losses in which both rules have something to change | 10 | 11 (25 with a candidate-1 event, 63 with a candidate-2 event) | yes |
| Strict flips: 1 alone, 2 alone, together | 6 to 13, 34, 49 to 54 | 6 to 13, 36, 51 to 56 | yes, as arithmetic |
| Realistic wins together | 12.3 to 21.4 | 17 to 31 with my cruder survival curves; **about 6 to 10 with what was measured** | the arithmetic yes, the inputs no |

The joint number is sound as a sum and unsound in what goes into it. Three inputs carry it:

1. **How long a saved queen lives.** B's two readings bracket "at our own other death rates" and "like a top-three
   queen". The replays answer it directly: our queen, after taking the safe step in the same situation, is alive at
   the end of the game in 6 to 9% of cases (candidate 2, items B and C). That puts candidate 2 at about 2 to 3
   games, below B's bracket.
2. **What a dead enemy queen is worth.** About 6 games by reading the 25 games one by one (candidate 1, item C).
3. **The extra from doing both.** It comes from the 11 losses in which our queen would be saved and hers killed. It
   needs our queen alive at round 500, so it is 11 times that same 6 to 9%, about one game; B's +1.8 and my +1.7 to
   +4.3 use the survival curves again.

So together: **about 6 + 2 or 3 + 1 = 9 or 10 games if everything holds, 5 to 8 more likely, which is +1.2 to +2.5
points; not +3.1 to +5.3.** The upper half of B's range is the assumption that our queen will live like a top-three
queen once she stops stepping into reach, and nothing measured supports that.

"Two sides of one idea" is a fair description of the state both aim at. As work for the team they are two cards
(B says so too): a switch on the attackers that cannot hurt much, and new scoring for the queen that has an open
question on small maps. One real link between them, which B does not state: **against test4 candidate 2 is worth
almost nothing without candidate 1.** test4's queen is alive at the end of 45% of our games, so 13 of the 45
avoidable deaths of our queen against test4 are in round-500 losses with her queen alive, and a living 2-long queen
of ours still loses those on queen length; 7 are in losses with both dead. Against WeHaveQuizzes it is the other way
round (2 and 17).

### Candidates 3 and 4 together

B says candidate 4 "needs" candidate 3, because the trade-on-contact build led at round 150 in two big-map games and
was behind by rounds 213 and 249 "under the leader switch". The two-game story is true, and it is two games. Over
its 12 big-map games that build had more length than the live bot at round 300 (147 against 122) and a longer
leader (19 against 14), and it lost six of them with her queen alive and ours dead and six on the longest dragon at
half the enemy's length. Nothing in those games says that a later leader would have turned them. And the same
switch builds the leader that every one of our big-map wins was won with (candidate 3, item C). I would not treat
the two as one package.
