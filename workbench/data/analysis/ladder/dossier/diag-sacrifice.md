# Their "no action" deaths: what they are and whether we copy them (team 1119, written 7 Oct 2026; 500 main games)

**What their deliberate deaths are for.** Most are not deliberate. Of their 14,091 deaths by no valid action in rounds 0-300, 75% (88% of the "no action" ones in rounds 0-100) are dragons with no free cell beside the head: the deaths ours take by stepping into a wall. Boxed-in deaths of every label run at 16.1 per 1,000 turns for them and 16.2 for us in rounds 0-100. Of the real remainder (3,496), 83% comes from four teams whose shortest dragons die while the team stands at 60 or more dragons, and the team goes on splitting; only one of the four is rated 2100 or above (chad gdp).
**The change.** No card.
**How sure.** High that the round 0-100 gap is a label and not a behaviour: every event is counted, the recount equals fingerprint.md to three decimals, five replays were drawn by a second script, and a second implementation of the free-tile test gave the same count for 16,007 of 16,007 deaths in 50 games (sc_check.py; 2,491 deaths beside a portal side were not compared). Medium to high that dying at the dragon limit buys nothing the game is decided on by round 300: it rests on 12 games against 45 inside three layouts, and on who wins (below).

Labels: [M] measured by my scripts in dossier/work/ (sc_scan.py replays the 500 games of input-snapshot.json into sc_ev-0..3.jsonl; sc_tab.py is the recount against fingerprint.md; sc_table.py, sc_kind.py, sc_final.py, sc_st.py, sc_team.py, sc_free.py and sc_buy.py print the figures; sc_view.py draws one death from the replay; sc_check.py is the independent recount). [C] read from battlecode/mybot2/main.cpp, line given. [E] my estimate.
Terms: "boxed in" = at the moment of death no tile beside the head is free of kelp and of bodies. "By choice" = a death by no valid action with such a tile free. "No valid action" = the engine's reason 4: no order, an illegal split or an unpaid sprint. Rounds are given as 0-100 / 101-200 / 201-300.

## 1. The kinds (job 1)

[M] Their side, rounds 0-300, 15,408 events: 14,091 deaths by no valid action and 1,317 same-team head-ons. In brackets: against teams rated 2100 and above.

| kind | events by window | the dragon | where; nearest team mate | who eats what it drops | our head within 4 |
|---|---|---|---|---|---:|
| K1 boxed in: the front left by a split the round before | 1,902 / 2,330 / 2,309 (431 / 601 / 581) | 2 long 94% | no free tile; dead-end cell 54%; mate head within 3 in 67%, median 3 long, the queen 1%, their longest 9% | own 2-4 long 46%, own 5+ 35%, their longest 16%, their queen 0.2%, ours 2%; 47% within 3 rounds | 29% |
| K2 boxed in, other (new child, dead-end cell, crowd) | 651 / 1,665 / 1,738 (193 / 458 / 511) | 2 long 48%, 3 long 40% | no free tile; dead-end cell 19%; mate head within 3 in 85% | own 2-4 74%, own 5+ 13%, longest 8%, queen 1%, ours 3%; 61% within 3 | 32% |
| K3 by choice, team at 60 or more dragons | 149 / 1,125 / 1,616 (98 / 497 / 917) | 2 long 76%, 3 long 17% | open ground (11% have 3 tiles or fewer to go to); 63 of the team alive (median); mate head within 3 in 87%, median 3 long, the queen 4%, their longest 5% | own 2-4 61%, own 5+ 29%, longest 5%, queen 4%, ours 1%; 76% within 3 | 8% |
| K4 by choice beside a longer queen, under 60 dragons | 21 / 31 / 56 (3 / 9 / 5) | 2 long 68% | nearest mate is the queen in 81%, median 9 long | queen 58%, own 2-4 32%, ours 3% | 22% |
| K5 by choice beside a mate twice its length, under 60 | 16 / 23 / 103 (6 / 4 / 19) | 2 long 54%, 3 long 38% | mate median 7 long, their longest in 15% | own 5+ 55%, own 2-4 29%, longest 12% | 21% |
| K6 by choice, none of these, under 60 | 72 / 129 / 155 (27 / 48 / 54) | 2 long 51%, 3 long 41% | 35% have 3 tiles or fewer to go to; 174 of the 356 are one team's dragons, mostly on their first turns | own 2-4 58%, own 5+ 27%, queen 8% | 26% |
| K7 same-team head-on, mover had no other free tile | 102 / 259 / 268 (21 / 39 / 43) | both: 2 long 54%, 3 long 33% | boxed in, in a fight | own 2-4 81%, longest 10%, queen 0.2%, ours 3% | 61% |
| K8 same-team head-on, mover had another free tile | 153 / 258 / 277 (20 / 35 / 39) | both: 2 long 52%, 4+ 17% | open; a third mate twice the mover within 4 tiles in 14% | own 2-4 72%, longest 10%, queen 0.4%, ours 8% | 27% |

- [M] No crash kind: in no round do 4 or more dragons that are half of a team die by no valid action.
- [M] "No action" is a family mark. Seven teams end a boxed-in dragon that way (chad gdp 98% of its boxed-in deaths, UnderTheC 97%, "1" 93%, Heartbreaker, Goated, Bot and doofenshmirtz 100%) and two by an illegal split (Maccas 99%, Proof by Intimidation 98%: the under-1900 gap in fingerprint.md; 94% of all illegal splits are boxed in). Everyone else, like us, moves into kelp, itself or a body. Ours: kelp 59%, own body 26%, another body 15%.
- [M] The same deaths on both sides, per 1,000 turns. All boxed-in deaths that are not head-ons: theirs 16.13 / 14.51 / 14.69, ours 16.16 / 12.60 / 12.68. The front left by a split: theirs 8.95 / 6.11 / 5.89, ours 10.89 / 6.65 / 5.99.
- [M] So the fingerprint figures split like this. Theirs 2.98 in rounds 0-100 = 2.63 boxed in + 0.35 by choice. Against 2100+: 5.48 = 4.51 + 0.97, and 7.98 in rounds 101-300 = 4.63 + 3.35.
- [M] Same-team head-ons: theirs 1,317 (0.370 per 1,000 turns), ours 348 (0.105). K7: 0.177 against our 0.088. K8: 0.193 against our 0.017; 143 of the 688 are one team rated 1878, and the rate is 0.276 under 1900, 0.128 at 1900-2099, 0.156 at 2100+. Each costs two dragons and nothing is routed to the queen. K7 is a lower bound: the count is exact only when the dragon hit is 2 long.
- [M] Replays drawn (sc_view.py game round dragon). Boxed in: 1311384 r36 #125, 1305215 r66 #176, 1305217 r80 #8: each a 4-long that split 2 + 2 the round before inside a pocket of two tiles, kelp or body on all four sides, no order given. At the limit: 1241400 r99 #18 (64 alive, three free sides; a 4-long one tile away splits 2 + 2 in the same round; 64 alive again at r101); 1311384 r166 #593 (64 alive, two free sides; a 2-long eats the pearl next round).

## 2. Who uses which kind, how early, and what it buys (job 2)

- [M] Who. Deaths by choice (K3-K6): chad gdp 1,475, ":3" 844, f2p 321, Heartbreaker 251; together 83%. In the 2100+ band chad gdp is 1,475 of 1,687 (87%). Five 2100+ teams have none before round 300 (40 games, they win 30); the other three have a few, from rounds 100, 153 and 250 on. All eight together: 0.06 / 0.23 / 0.87 per 1,000 turns, against chad gdp 3.75 / 10.80 / 18.72.
- [M] How early. K3 begins when the team reaches 60 dragons: 1 event before round 60, 41 in rounds 60-79, 102 in rounds 80-99. Median first death by choice in a game: chad gdp round 67, ":3" 93.5, f2p 193.5. Before round 60 all 500 games hold 64 deaths by choice.
- [M] K4 is small and not a 2100+ habit: 108 events, 49 of them one team rated 1943 (queen 6 long at r100, 12.5 at r300; it wins 3 of 10 against us); 17 events in the 70 games against 2100+.

[M] Medians as queen / longest / dragons / total length. "Full board" = that side has 56 or more dragons at round 100.

| their side | games, won by them | round 100 | round 200 | round 300 | us in the same games, round 300 |
|---|---|---|---|---|---|
| chad gdp (K3) | 15, 11 | 2 / 4 / 39.5 / 94.5 | 2 / 8 / 61.5 / 179.5 | 2 / 9 / 62 / 188 | 0 / 5 / 37 / 93 |
| the other 2100+ teams | 55, 42 | 2.5 / 4 / 26 / 65 | 2 / 7 / 57.5 / 153.5 | 2 / 13.5 / 57 / 200 | 0 / 7 / 29 / 77 |
| ":3" (K3) | 20, 6 | 2 / 4 / 21.5 / 47 | 3 / 5 / 38 / 92 | 1 / 8 / 41.5 / 108 | 1 / 5.5 / 31.5 / 85 |
| Heartbreaker (K5, K6) | 15, 5 | 2 / 6 / 15 / 50 | 1 / 10.5 / 18.5 / 81 | 0 / 16 / 23 / 101.5 | 1.5 / 18.5 / 52 / 157.5 |
| full board, 1 or more deaths by choice per 1,000 turns by r200 | 12, 7 | 2 / 6.5 / 62 / 162 | 3 / 12 / 62 / 217 | 3 / 18 / 62 / 269 | 2 / 16 / 54 / 196 |
| full board, fewer | 47, 33 | 3 / 7 / 62 / 164 | 3 / 14 / 63 / 236.5 | 3 / 19.5 / 62 / 282.5 | 0 / 23.5 / 54 / 206.5 |
| OURS on a full board (won by us) | 55, 27 | 3 / 7 / 60 / 160 | 2 / 13 / 60 / 210 | 0 / 25 / 55 / 213 | theirs: 3 / 16 / 62 / 226 |

- [M] Inside the same layouts (three have both kinds of game on a full board, 12 against 45), much minus little at rounds 100 / 200 / 300: queen -1.6 / -0.5 / -0.9, longest -0.5 / -1.0 / +0.4, dragons +0.4 / -0.2 / +0.5, total length +1.9 / -10.0 / -10.3.
- [M] The price. K3 gives up 7,046 length for 3,800 pearls, 99% eaten by its own side: 0.46 of the length is gone. chad gdp gives up 22 / 82 / 135 length a game and eats back 12 / 45 / 75.
- [M] What goes with it. Splits per 1,000 turns: chad gdp 33.6 / 28.8 / 36.9, the other 2100+ teams 34.5 / 22.8 / 21.8, ours on a full board 38.1 / 15.7 / 19.6. Natural pearls per 1,000 turns: chad gdp 78 / 68 / 79, the others 61 / 43 / 38, ours on a full board 60 / 31 / 29. [E] K3 keeps a full team splitting and its dragons 2 to 4 long; I cannot separate its pearl rate from the board it holds (62 dragons against our 31 to 37).
- [M] Who wins. The five teams other than chad gdp that die by choice before round 200 win 19 of 55 against us; the five 2100+ teams that never do win 30 of 40.
- [M] The teams that beat us do not feed their queens early. 2100+ queens are alive at rounds 100 / 200 / 300 in 70 / 60 / 60% of games, 3 long at the median, 5 or longer in 9 / 13 / 17%, and eat 0.19 / 0.21 / 0.43 pearls a game from deaths by choice. Ours against them: alive 70 / 40 / 34%. "Their queen is longer" at round 200 is a living 3 against a dead 0.
- [M] Ours. No death by choice before round 201; 2,840 in rounds 201-300 (2.25 per 1,000 turns), 550 of them with 60 or more alive. Our longest eats 1.95 of those pearls a game in rounds 201-300; a 2100+ longest eats 1.51 of theirs.

## 3. Why, in the code (job 3)

- [C] Boxed in. 681-706 try a portal. 708-714 with 1111-1135: a dragon of 4 or more (ESCAPE_MIN_LENGTH, 294) splits off length minus 2 and the 2-long front stays; 1129: within 2 of the dragon limit a dragon under 8 does not. Then 776 moves in the best-scored direction: kelp and bodies keep SCORE_REJECT (5221, 5236), an enemy head is half of it (5260-5262), a mate's head 1.5 times (5263-5265). So ours takes the wall, never gives "no order" and seldom takes a mate's head: K1, K2 and K7 under other engine reasons, with the same pearls dropped.
- [C] By choice. The one place a dragon of ours returns without an order is 551-554. It needs ready_to_die() (4924-4935), which needs is_feeder() (4899-4901), set in pick_feed_target() (2296-2324): feeding_phase() or the early flag (2302-2303), not the queen, a known leader at least twice its length (4912-4917, FEED_LEN_RATIO 292) within 15 tiles (48, 2308), more than 3 of ours alive (47).
- [C] feeding_phase() (4919-4922) is round > feed_round (400: 44, 472; 300 in a queen game: 149, 525-526) or round > 200 with 56 or more dragons (69-70). Hence no feeder before round 201.
- [C] The two switches that are off. FEED_EARLY_ROUND 0 with FEED_EARLY_MAX 2 (269-270, read at 2302): a 2-long could feed a known leader twice its length earlier. That is K5, which the 2100+ teams hardly use (29 events in 70 games), and not K3. FEED_LOCAL 0 (267; 555-557, 4937-4954): die beside any mate in view that shows 4 parts and twice its length. That is the nearest thing to K3, but 4938 still asks for feeding_phase().
- [C] At the limit before round 201 ours neither split nor die: 1040 stops splits at 60 dragons (SPLIT_SOFT_LIMIT, 42), 1161 stops pocket harvests and 1129 escape splits within 2 of the limit. They grow where they are. K3 is the opposite choice.

## 4. The card: no card

No title and no slug on purpose: there is nothing to draft.

### Claim
We adopt none of the three things the fingerprint rows could mean. (a) "No order when boxed in" is our wall death under another name. (b) Dying at the dragon limit before round 201 (K3) is one top team's habit and three lower teams'; by round 300 it shows no longer queen, no longer longest dragon and 10 less total length inside the same layouts. (c) Feeding the queen early (K4) is not what the 2100+ teams do. Our rule holds as it is: the swarm first, eat what is safe, no timid dragons.

### Evidence
Sections 1 and 2. In short: 16.13 against 16.16 boxed-in deaths per 1,000 turns in rounds 0-100; 88% of their "no action" deaths there have no free tile; 64 deaths by choice before round 60 in 500 games; 87% of the 2100+ deaths by choice are one team; -10 total length and -1.0 / +0.4 longest at rounds 200 / 300 for the teams that do it; 19 of 55 against 30 of 40 on who wins.

### Expected signal
If this reading is right, any later batch shows: their "no action" deaths in rounds 0-100 with no free tile beside the head in 85% or more (sc_table.py: 88.3%); deaths by choice per 1,000 turns among 2100+ teams other than chad gdp under 0.3 before round 200 (sc_buy.py: 0.06 and 0.23); with fewer than 60 of the team alive, under 0.2 per 1,000 turns (now 0.17: 606 events over all their turns).

### What would show it's wrong
- A second 2100+ team with 1 or more deaths by choice per 1,000 turns before round 200.
- With 30 or more full-board games on each side inside the same layouts, the teams that do it ahead in total length or longest dragon at round 300 (now -10.3 and +0.4 on 12 against 45).
- A stricter boxed-in test (tiles the dragon can still be alive on two turns later) moving more than a tenth of K1 and K2 to "had a way out".
- For the queen: 2100+ queens 5 or longer at round 200 in more than a third of games (now 13%).

## 5. Against it

- [M] The one team that does K3 at scale is the highest rated we meet (2425) and wins 11 of 15. It keeps 62 dragons, splits at 29 to 37 per 1,000 turns after round 100 and eats 68 to 79 natural pearls per 1,000 turns, where everyone else falls to about 40 and we fall to 31 on a full board. If the churn is what keeps a full team eating, the gain is in pearls and I measured standings.
- [M] Without holding the rating, games with 3 or more deaths by choice by round 200 look better inside 7 layouts: longest +1.7 at r200 and +4.8 at r300, queen +3.1 at r300, won 23 of 34 against 108 of 182. chad gdp carries that; the full-board comparison, which holds the size of the team level, has 12 games on one side and chad gdp is in them.
- [M] Our own full boards go no better than the rest (27 of 55 won; 269 of 500 overall) and look worse inside: natural pearls 31 per 1,000 turns in rounds 101-200 against their 44, total length 213 against 226 at round 300, queen dead at the median. Standing still at 60 dragons (section 3, last line) may be part of that. I have not shown that dying there would not help; plan.md change 1 aims at the same rounds from the eating side.
- [M] A gap this pass did not chase, and it runs the other way: against 2100+ our fronts left by a split die at 15.1 per 1,000 turns in rounds 0-100, theirs at 7.9 in the same games (all boxed-in deaths 21.3 against 14.6). Each is 2 length for 1 pearl. A lead for the analyst, not a card.
- [M] "Free tile" is a test of one moment: 11% of K3 and 35% of K6 had 3 tiles or fewer to go to, so some deaths by choice are dragons that were lost anyway. This makes the by-choice count too high, not too low.
- [E] K3's purpose (to free a place so that a longer dragon can split) is read from two replays and the split rates, not from their code.
- [M] 15 games of chad gdp, 19 layouts, about 30 hours of ladder play. Nothing here is from an unseen map.
