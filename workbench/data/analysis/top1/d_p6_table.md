## 6. Our queen against the others

One row per behaviour. "meow" is all 401 games unless a cell says live bot or rules on / off. Rates are per 1,000 queen-rounds unless a cell says otherwise. The source of each row is the table of section 5 named in the last column.

| Behaviour | meow | our opponents | forgot | SSS | Vibing++ | source |
|---|---|---|---|---|---|---|
| Queen deaths per 1,000 queen-rounds | 6.5 | 2.2 | 2.8 | 2.1 | 3.4 | 2 |
| Alive at round 300 (of games that reach it) / at the end | 15% / 10% | 61% / 40% | 52% / 36% | 65% / 41% | 49% / 27% | `haz.txt` |
| Rounds with an enemy head in her view | 20% | 17% | 21% | 18% | 21% | 5b |
| ... on large maps, rounds 50-149 | 22-26% (live) | 10-12% | 17-12% | 11-10% | 14-22% | 5c |
| Ends a turn in reach although a safe step exists | 2.7 | 1.5 | 0.8 | 0.6 | 1.1 | 5b |
| From outside reach, steps into it (share of such turns) | 0.76% | 0.42% | 0.18% | 0.15% | 0.23% | 5b |
| In reach with a safe step, stays in reach (share of such turns) | 19% | 13% | 10% | 8% | 10% | 5b |
| Takes a pearl that lies inside a visible enemy's reach | yes: she ate on 19 of her 68 stay-in turns (games 8-11) | 26 of 88 | 8 of 67 | 8 of 43 | 12 of 63 | `expo.txt` |
| Steps nearer to a small enemy head 3 / 4 steps away | 10% / 30% (rules on), 48% / 67% (rules off) | 12% / 12% | 5% / 5% | 7% / 8% | 16% / 32% | 5b |
| Cornered turns (no safe step) | 2.8 | 3.9 | 3.1 | 2.2 | 3.5 | 5b |
| A turn that ends in reach is punished by a ram | 71% | 16% (by us) | 44% | 47% | 32% | 5b |
| Rammed by an enemy she could not see | 0.55 | 0.06 | 0.48 | 0.41 | 0.62 | 2 |
| Boxed in with 6 or more segments: what she does | cuts to 2 (40 cuts in 37 games; never sheds with no free cell) | cuts (85 in 63 games) and sheds (109) | sheds 2 from the tail (1,448 times); 0 cuts | sheds (394); 0 cuts | cuts to 3 (105 in 86 games), sheds 78 | `cut.txt` |
| Dies boxed in by bodies (her own team's in 58 of our 61) | 1.1 (cut and stuck 14, own child 11, nose to nose 20, a team-mate's body 14) | 0.7 | 0.16 | 0.17 | 0.87 | 2 |
| Dies in a terrain dead end | 0.54; ate inside in 26 of 30 | 0.33 | 0.20 | 0.11 | 0.20 | 2, 4.6 |
| Takes portal steps (queens that ever did, maps with portals) | 4% with rules on; 61% with rules off, 24 of 27 before round 20 | 13% | 4%, none before round 20 | 7%, none before round 20 | 27% | 5e |
| Rams an enemy head herself with a free safe cell | 10 games, all rules off | 1 | 4 | 0 | 5 | `misc.txt` |
| Walks a loop of 4 cells | 0.3% of rounds with rules on, 11% with rules off | 12% (test4 25%; WHQ 1.5%) | 2.4% | 5.2% (weakhold 46%) | 2.4% | 5f |
| Path distance from her start, rounds 50-99, queen / other heads | 14.7 / 19.8 (live) | 12.7 / 22.6 | 15.0 / 21.4 | 12.3 / 23.1 | 16.9 / 23.2 | 5c |
| Rams of a short queen by distance from her start (0-5 / 11-15 / 16-25 cells) | 1.8 / 5.5 / 8.1 | 0.6 / 1.4 / 1.6 | 1.1 / 4.8 / 4.5 | 0.8 / 1.7 / 2.9 | 1.0 / 3.4 / 3.9 | 5c |
| Own heads within 4 cells, rounds 100-149 / 150-199 | 1.2 / 1.3 (live) | 1.5 / 1.8 | 1.7 / 1.9 | 1.7 / 2.2 | 1.4 / 1.5 | 5c |
| Rams of a short queen with 0 / 3 or more own heads within 6 steps, rounds 50-149 | 9.7 / 2.2 | 2.4 / 0.1 | 5.3 / 1.4 | 3.1 / 1.0 | 4.9 / 0.7 | 5c |
| A small intruder within 4 steps of her is rammed by one of her team | 3.7% | 13.6% | 13.5% | 16.6% | 12.1% | 5f |
| Natural pearls per 100 rounds, rounds 0-49 / 100-149 | 4.7 / 2.2 (live) | 4.9 / 2.4 | 4.6 / 1.3 | 4.1 / 1.6 | 4.7 / 2.3 | 5c |
| Her splits per 100 rounds, rounds 0-49 / 100-149 | 3.6 / 1.6 (live) | 3.6 / 1.2 | 4.4 / 1.0 | 4.9 / 1.0 | 3.2 / 1.1 | 5c |
| Her mean length, rounds 100-199 | 2.5 | 3.2 | 2.7 | 2.6 | 5.3 | `e.txt` |
| Queens of 6 or more lost: rammed / cut to 2-3 and dead boxed in | 16 / 17 (10 at round 3, 3 in dead ends, 4 fed queens late) | 21 / 24 | 63 / 0 | 24 / 0 | 67 / 12 | `misc.txt` |
| Splits with an enemy head in view within 3 turns of being rammed | 16 of 251 rams | 11 of 102 | 23 of 327 | 14 of 240 | 19 of 230 | `misc.txt` |

Reading the table down: in what she eats, how often she splits, how far she goes on average and how often she is seen, our queen is an ordinary 2-3-long queen like SSS's or forgot's. She differs in five rows: she ends turns in reach by choice, she takes pearls in reach, she cuts herself when boxed in, she has less company, and nobody near her rams the intruder. With the rules off she is a different animal: she walks toward small enemy heads, trades herself for a 2-long, and takes portals at once.
