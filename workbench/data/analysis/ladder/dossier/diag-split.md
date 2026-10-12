# Splitting: rank-1 does not split sooner than we do, it eats more (team 1119, written 8 Oct 2026; 500 of ours, 597 of rank-1)

**What rank-1 does that we do not.** Nothing in the splitting. Per pearl eaten we split as often as it does (0.38 against 0.36), a dragon of ours that reaches 4 is split sooner and more surely (within 5 turns 83% against 76%, ever 94% against 91%), and rank-1 holds more unsplit length than we do at every checkpoint. Its higher split rate is its higher pearl rate: 84.1 pearls per 1,000 dragon turns against our 58.8, and the whole of that gap sits in dragons 2 and 3 long. Its higher death rate is the same boxed-in deaths after splits, plus ramming.
**The change.** No card.
**How sure.** High that no split rule holds us back: every turn of all 1,097 games is counted, the scan gives the scoreboard figures to three decimals (22.661 / 30.580, 20.065 / 27.789, 21.072 / 28.904, 0.382 / 0.362), and a second script on the stock parser agrees game by game on 220 of 220 games. Medium on what a looser late rule would be worth (section 6): that is 22 splits a game at most and the diag-islands card already tests it.

Labels: [M] measured by my scripts in dossier/work/ (sl_scan.py replays both sets into sl_scan-0..3.jsonl and sl_agg.py prints the tables; sl_fate.py and sl_fateagg.py follow every split for 20 rounds; sl_recount.py and sl_cmp.py are the independent recount). [C] read from battlecode/mybot2/main.cpp, line given; the file at that path is dated 6 Oct and holds neither QUEEN_NO_FEED nor TR_STALL_RELEASE. [E] my estimate. The three lines above are [M]. The scans ran without nice: the session guard does not allow that command.
Terms: figures are ours / rank-1. "lay" = mean of the 19 layouts weighted equally, as in scoreboard.md; "pooled" = all games together (the two sets have nearly the same layout mix, 32% and 30% of games above 1,200 cells). "Spare splits" of a dragon = half its length rounded down, minus 1. "Spell" = the turns a dragon spends at 4 or longer until it splits, dies or the game ends. "Late" = after our own switch round (150 above 1,200 cells, else 300).

## 1. Lengths, splits, lifetimes, dragons alive (job 1)

[M] Share of dragon turns by length, lay, ours / rank-1. Every living dragon takes one turn a round, so this is also the length of living dragons.

| rounds | 2 long | 3 | 4 | 5 to 7 | 8+ | mean length |
|---|---|---|---|---|---|---|
| 0-100 | 61.9 / 61.8 | 32.5 / 31.2 | 3.9 / 4.7 | 1.5 / 1.9 | 0.2 / 0.4 | 2.47 / 2.50 |
| 101-200 | 59.2 / 58.8 | 33.1 / 31.9 | 3.9 / 4.7 | 2.9 / 3.1 | 1.0 / 1.5 | 2.60 / 2.66 |
| 201-300 | 56.4 / 55.5 | 33.5 / 31.3 | 3.1 / 5.3 | 3.7 / 4.7 | 3.3 / 3.2 | 2.86 / 2.90 |
| 301-400 | 54.8 / 51.2 | 30.2 / 32.6 | 3.0 / 5.9 | 6.1 / 5.0 | 5.8 / 5.3 | 3.17 / 3.18 |
| 401-500 | 48.6 / 38.6 | 26.6 / 29.2 | 3.5 / 7.5 | 6.0 / 8.6 | 15.2 / 16.1 | 4.26 / 4.66 |

- [M] Rank-1's dragons are not shorter than ours. It spends more turns at exactly 4 (game 5.6% against 3.5%, 18 of 19 layouts), and 14.0% of its turns at 4 or longer against our 10.6% (15 of 19).
- [M] Both bots cut the same way. Share of splits, lay: a 4-long into 2 + 2, 71.0 / 69.6; a 5-long sending off 3, 8.0 / 11.8, or 2, 2.3 / 2.4; 6 or longer sending off 4 or more, 15.1 / 12.9, or 2, 3.6 / 3.3. The parent is 2 long after the split in 95.3% / 94.1% (recount, pooled). Mean parent 4.97 / 4.96, mean child 2.76 / 2.75. About a third of all splits on both sides are made with no free tile beside the head (34.6% / 32.2%, pooled): the escape of a boxed-in dragon.
- [M] Rank-1 asks for 57.7 splits per 1,000 turns in rounds 0-100 and gets 39.6. The rest are its "illegal split" deaths (18.1 per 1,000): 98% of them have no free tile beside the head, and under 0.005 per 1,000 turns happen with 64 alive. It is how rank-1 ends a boxed-in dragon, where ours takes the wall.
- [M] Rounds lived, for dragons born in rounds 101-200: dead within 5 rounds 27% / 26%, within 20 rounds 52% / 53%, within 80 rounds 78% / 85%. Born in 0-100: 26 / 24, 47 / 51, 71 / 81. The median is about 20 rounds for both. Of the two halves of a split, 53% / 55% of children and 60% / 64% of parents are dead 20 rounds later.
- [M] Dragons alive. No game goes above 64. Rank-1 has its own ceiling at 62: of its 222 games that reach 60, the most it ever has is 62 in 169, 63 in 20, 64 in 2. Ours with a ceiling of 60 for ordinary splits goes higher through escape splits: of 123 games, 62 in 48, 63 in 28, 64 in 23.
- [M] Games with 56 or more alive, lay, by round: r100 8.9% / 7.8%, r150 17.4 / 19.1, r200 19.8 / 27.2, r250 10.7 / 29.5, r300 8.4 / 31.5, r350 6.9 / 30.0, r400 8.1 / 8.4. We fill the board as fast as rank-1 and lose it after round 200; rank-1 keeps it to round 350. Mean alive: r200 30.2 / 33.8, r300 28.6 / 33.8, r400 24.4 / 27.3.

## 2. The moments we could split and do not (job 2)

[M] Every turn a dragon of the side starts at 4 or longer (ours 1,447 a game, rank-1 2,097), put in the first class that applies, in the order of our own code. Pooled. "Room" = free tiles reachable from the tail tile on the true board, counted to 8. Turns x difference = our turns in the class x (rank-1's rate - ours).

| class | our turns a game | splits per 100 such turns | rank-1 higher in | turns x difference | our spells a game | spells that end in a split |
|---|---:|---|---|---:|---:|---|
| late, longest of the team | 169.5 | 5.0 / 14.2 | 14 of 15 | +15.7 | 6.6 | 85% / 95% |
| late, longer than 4 | 752.8 | 4.5 / 7.2 | 14 of 15 | +20.1 | 23.8 | 83% / 81% |
| 60 to 63 alive | 132.3 | 4.9 / 8.8 | 6 of 7 | +5.1 | 20.8 | 83% / 79% |
| no free tile behind the tail | 34.1 | 18.4 / 29.8 | 10 of 14 | +3.9 | 30.0 | 97% / 95% |
| 1 to 3 free tiles behind the tail | 47.8 | 25.7 / 44.0 | 16 of 17 | +8.8 | 12.2 | 96% / 97% |
| portal at the tail | 20.8 | 12.0 / 40.2 | 14 of 14 | +5.9 | 11.1 | 89% / 96% |
| head boxed in | 32.1 | 99.8 / 99.3 | 5 of 16 | -0.2 | 10.9 | 100% / 100% |
| queen after round 200 | 28.5 | 2.3 / 0.5 | 0 of 8 | -0.5 | 0.8 | 83% / 54% |
| enemy head within 3 | 59.3 | 52.9 / 29.9 | 6 of 19 | -13.6 | 31.2 | 96% / 94% |
| open, length 4 | 149.5 | 57.4 / 28.8 | 1 of 19 | -42.7 | 91.8 | 97% / 94% |
| open, length 5 or more | 19.8 | 27.0 / 7.9 | 1 of 15 | -3.8 | 0.8 | 100% / 95% |
| all | 1,446.8 | 15.6 / 15.4 | 11 of 19 | -1.4 | 240.1 | 94% / 91% |

- [M] The classes cancel: over all turns at 4 or longer the two bots split at the same rate (15.6 / 15.4 per 100; lay 31.5 / 32.7). Rank-1 splits 323 times a game against our 225 because it has 650 more such turns a game, and it has those because it eats more.
- [M] The same by other cuts, splits per 100 turns at 4+: length 4, 36.7 / 26.8; 5, 10.5 / 16.3; 6-7, 11.2 / 9.7; 8+, 5.4 / 5.7. Fewer than 32 alive 21.1 / 22.4; 32-55, 17.1 / 20.5; 56-59, 15.2 / 17.2. Enemy head within 3 of head or tail 19.2 / 19.5; none 14.4 / 14.5. Room behind the tail 0, 13.6 / 21.2; 1-3, 21.4 / 28.9; 4-7, 22.1 / 20.0; 8+, 14.7 / 13.2. Rounds 0-100, 47.1 / 48.2; 101-150, 24.3 / 30.2; 151-200, 14.0 / 20.3; 201-300, 15.3 / 14.4; 301-400, 10.9 / 11.7.
- [M] The tail classes are a delay, not a loss. A spell that begins with 0 to 3 free tiles behind the tail splits on its first turn in 16-27% of ours against 32-55% of theirs, but within 5 turns in 89-94% against 84-91%. Only the portal class loses splits: 11.1 spells a game x 7 points = 0.8 splits a game.
- [M] What the late rules forbid, seen from rank-1's side (sl_fateagg.py): late, a dragon of 5 or more or the team's longest sheds a 2-long child 23.9 times a game; ours does it 1.5 times. That is 7% of rank-1's splits and the largest thing it does that our code refuses. For the rest it holds length late as we do: 7.2 splits per 100 turns for its late dragons above 4.
- [M] Unsplit length held, spare splits a game, lay: r100 1.9 / 3.1, r200 8.9 / 11.0, r300 11.3 / 16.2, r400 17.6 / 26.1, end 28.5 / 49.1 (rank-1 higher in 14 to 16 of 17 to 19 layouts). At round 300, 13.8 of our 14.7 (pooled) sit in the two late classes; of rank-1's 21.7, 16.9 do.

## 3. Why, in the code (job 3)

- [C] The ordinary split is 748-751 calling split_child_size() (1020-1071). The child is always 2 (1048), so a 4-long becomes 2 + 2. It comes after hunting (543-549), ramming (602-607), the queen's blocks (609-677), the boxed-in escape (708-714) and the cornered split (730-736).
- [C] Open, length 4 and enemy near: nothing in 1020-1071 stands in the way, and ours splits at 57 and 53 per 100 turns, about twice rank-1. SPLIT_MIN_LENGTH 4 (41, 1028) is the engine's own minimum; rank-1 has the same.
- [C] The two late classes: 1028 with is_leader() (3328-3329) and 1037, both on round > grow_round (467-468). They account for the only 2-long children rank-1 makes and we do not.
- [C] 60 to 63 alive: 1040, SPLIT_SOFT_LIMIT 60 (42); escape splits stop at 62 for dragons under 8 (1129, ESCAPE_RESERVE 318), which reads the limit from the game (gm.get_unit_limit(), also 1161 and 2666). Rank-1 stops at 62. The difference is 2 dragons, in the 3% of rounds 201-400 we spend at 60 or more.
- [C] Room behind the tail: 1058, child_has_exit() (1091-1100) and tail_room() under CHILD_MIN_ROOM 4 (317, 1188-1192). Portal: 1062-1069. Both wait a turn or two (section 2).
- [C] Harvesting (1045, HARVEST_SPLIT false at 232) cannot be seen in a replay. It lies inside the open and room classes, where ours splits as fast or faster.
- [C] Queen: 1024-1026 stop her after round 200 (QUEEN_SPLIT_ROUND 102). Rank-1's queen splits less than ours there (0.5 against 2.3 per 100).
- [C] Boxed in: escape_child_size() (1111-1145) sends off length minus 2 and, with no move at all, does so whatever room the child has (1132-1135). [M] 19.3 splits a game are of this kind with 1 to 3 free tiles behind the tail, fewer than 60 alive and a parent of 5 or more: the child is dead within 5 rounds in 91% and the front in 98%. Rank-1 has 11.6 a game (64% and 94%). They are dragons already lost; they add to splits and to deaths alike.

## 4. What the extra splitting buys, and what keeping length buys (job 4)

- [M] Splits per 1,000 turns = pearls per 1,000 turns x splits per pearl. Lay: ours 58.8 x 0.382, rank-1 84.1 x 0.362. Rank-1 is higher on pearls in 18 of 19 layouts and on splits per pearl in 4 of 19. fingerprint.md has ours at 0.382 against the 2100+ teams too. [E] At rank-1's pearl rate and our own splits per pearl we would split 32 times per 1,000 turns, above its 30.6.
- [M] Pearls eaten per 1,000 turns by the length of the eater, lay: 2 long 41.7 / 58.9 and 3 long 62.1 / 95.9 (each 18 of 19 layouts); 4 long 138.9 / 139.9 (7 of 19); 5 to 7, 164.9 / 142.2; 8+, 181.0 / 210.9. 89% of our turns are at 2 or 3. The gap is in how a short dragon finds its next pearl, not in how often we make short dragons.
- [M] After an open 2 + 2 split the two halves eat 2.68 / 3.03 pearls in 20 rounds: child 1.26 / 1.33, parent 1.42 / 1.70. Our children die within 5 rounds in 17% against 12%.
- [M] Board. Share of natural pearls eaten, lay: 47.1% / 54.6% in rounds 0-100, 47.6 / 58.9 in 101-200, 46.5 / 58.2 in 201-300, 37.7 / 58.2 in 301-400. Tiles nearer to one of our heads than to any of theirs: r100 53.4% / 53.0%, r200 52.1 / 54.8, r300 47.7 / 54.4, r400 46.6 / 55.6.
- [M] Deaths per 1,000 turns, lay, 20.1 / 27.8. Boxed in, by wall, body or no legal action: 11.7 / 18.5. Ramming an enemy head: 2.1 / 3.9. Being rammed: 3.3 / 2.7. Wall, body or no legal action with a tile free: 2.9 / 2.3. Counted another way, deaths by wall, body or no legal action within a round of the dragon being in a split: 6.8 / 11.2, which is 0.30 / 0.37 per split. So rank-1's turnover is its eating, its splits, and the fronts those splits leave behind; nothing in it is a thing to copy by itself.
- [M] Rank-1's one habit that looks like buying: with its head free and 1 to 3 free tiles behind the tail it splits 31.9 times a game (ours 3.2). That child eats 2.31 pearls in 20 rounds (80% eat at least one) and is dead within 5 rounds in 55%, boxed in. [E] About +0.5 length a split after the pearls it drops; not a card.
- [M] Keeping length. Our games end by elimination 191 (117 won), on the queen 105 (39), on the longest dragon 201 (111). Ahead on longest at round 300 we win 108 of 158, behind 36 of 147; with more dragons 78 of 106, with fewer 87 of 234. Rank-1 keeps more: longest at r300 10.5 / 10.8, at r400 17.8 / 19.8, at the end 31.1 / 42.2; total length at r300 90.5 / 112.6; queen alive at r300 35.9% / 52.7%. It wins 135 of 208 on the longest dragon. It does not trade length for splits; it has more of both.

## 5. The card: no card

No title and no slug on purpose: there is nothing to draft.

### Claim
No split switch. SPLIT_MIN_LENGTH, the child of 2, SPLIT_SOFT_LIMIT 60, child_has_exit, CHILD_MIN_ROOM and the queen's rule stay as they are. The splitting gap in scoreboard.md is the eating gap under another name, and the death gap follows from both. The one class our code refuses and rank-1 plays, a 2-long child shed late, is the subject of the diag-islands card (LEADER_FULL_UNITS); a second switch on the same lines would test the same thing twice.

### Evidence
Sections 1, 2 and 4. In short: splits per pearl 0.382 / 0.362; splits per 100 turns at 4 or longer 15.6 / 15.4; spells ending in a split 94% / 91%; spare splits held at round 300 11.3 / 16.2; pearls per 1,000 turns at length 2, 41.7 / 58.9.

### Expected signal
In any later batch, counted by sl_scan.py and sl_agg.py: our splits per pearl at or above rank-1's 0.36; our spells of 4+ ending in a split at or above its 91%. And when a card from the eating side lifts pearls per 1,000 turns at length 2 from 41.7 toward rank-1's 58.9, splits per 1,000 turns rise by about 0.38 for every pearl with no split line touched.

### What would show it's wrong
- A batch where our splits per pearl fall under 0.33, or spells ending in a split under 85%.
- A build that eats 55 or more per 1,000 turns at length 2 and still splits under 26 per 1,000: then a rule binds once the pearls come.
- The diag-islands switch, in its own check, lifting pearls per dragon turn after the switch round: then the late class is worth more than I give it.
- Other teams rated 2300 and above holding fewer spare splits than we do at round 300: then rank-1 is the odd one out and not the mark.

## 6. Against it

- [M] Counted by turns, the late classes are +35.8 splits a game and the tail and portal classes +18.6; I set them against the classes where ours is faster. If the faster classes are wasted hurry (rank-1 waits at 4: 5.6% of its turns against our 3.5%) the sum is not the right measure, and the late rules cost up to 22 splits a game, a tenth of ours.
- [M] We lose the full board after round 200 and rank-1 does not (section 1). I did not separate feeding from round 201 (diag-feeding), the queen's stop and the late rules as its cause; a looser late rule could matter there more than the class table shows.
- [M] Rank-1 plays 448 of its 597 games against teams rated 2100 or more, we play 70 of 500. Its opponents and ours eat alike (natural pearls 39.0 / 39.2 per 1,000 of their turns, lay), but nothing here holds the opponent level.
- [E] A dragon is 4 long only just after eating, so the eating rate by length is partly who stands in a pearl patch. It shows where the gap is, not that length makes a dragon eat.
- [M] The classes are ours, applied to a bot that has other rules; "longest" is the true longest, not what a dragon of ours knows; room is counted on the true board, not from the dragon's view. Rank-1's turns at 60 to 63 alive rest on 7 layouts.
- [M] 19 ladder layouts, about 30 hours of play. Nothing here is from an unseen map.
