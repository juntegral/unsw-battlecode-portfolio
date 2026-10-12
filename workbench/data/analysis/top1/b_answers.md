## Answers to the eight questions

Where a count is "over all games" it covers every game of that team against opponents rated 2000+, Schooltime left out (SSS 503 games,
forgot 632, Vibing++ 502), and the script and output file are named. "In the games read" means the 15 games above (SSS 10, forgot 13);
those counts are in `b_out/tally15.txt` (`b_tally.py`).

### 1. Ram when in view

A "chance" is one turn of one dragon with a free path to the enemy queen's head no longer than its reach; "in view" means her head is
inside the dragon's 7x7 square on that turn (`q3v2`, the lead's `extract3.py`).

**forgot.** 457 in-view chances over all games, 254 taken. The rule that fits them (`b_chance.py`, `b_chance2.py`, `b_chance3.py`; outputs `b_out/chance*_264*.txt`):

| attacker | when | taken | what it does otherwise |
|---|---|---|---|
| 2-3 long | round 100 or later | 136 of 139 | |
| 2-3 long | rounds 0-99, at least as many other own heads within 4 steps of it as enemy heads there (the queen counted) | 47 of 51 | |
| 2-3 long | rounds 0-99, fewer other own heads within 4 steps than enemy heads there ("outnumbered") | 38 of 127 | moves away (77 of the 96 turns not taken by 2-3-longs) |
| 4 long | any round | 12 of 53 | splits 4 -> 2+2 (40 of the 41 turns not taken) |
| 5-9 long | any round | 21 of 65 | walks on; 11 of 27 taken when she is at least as long as the attacker, 10 of 38 when she is shorter |
| 10-12 long | any round | 0 of 22 | walks on |
| the team's longest dragon | any round | 4 of 47 | |

- **It is a time switch plus a local head count, not a price.** Before round 100 a small forgot dragon rams her only when it is not outnumbered where it stands; from round 100 it always does, even alone among enemies (22 of 24 when the enemy heads within 4 steps outnumbered the other own heads there by two or more). Cost does not explain it: a 3-long takes 13 of 28 free chances and 24 of 47 one-paid-step chances on a 2-long queen. Whether its own queen is alive does not explain it either (65% taken with her dead, 52% alive, over all lengths).
- **The head count holds however the heads are counted.** A second script (`b_chance4.py`) recounted the 178 early turns: with heads inside the attacker's 7x7 view instead of within 4 steps, 66 of 82 taken when not outnumbered and 19 of 96 when outnumbered; within 5 steps, 57 of 71 and 28 of 107; within 3 steps, 33 of 39 and 52 of 139. Which radius forgot really uses I cannot tell; 4 steps and the 7x7 view fit best.
- **Longer dragons are not fighters.** A 4-long splits, as every forgot 4-long does. Dragons of 5 and more mostly walk past. In the game read with the most such turns, 1067620, a 12-long (#193) walked beside Vibing++'s 3-long queen for five turns (r169-173; 4-8 steps, 1-5 paid) and an 8-long and a 7-long passed one turn each (r118, r137); a 9-long took the eighth turn (r178).
- **Being fed, yes; on its way to feed, no.** Of the 31 forgot dragons of 5-12 that passed up an in-view chance (first such turn each, `b_chance5.py`), 19 had eaten pearls of dead team-mates in the 20 rounds before and 7 were the team's longest dragon at that moment: they are dragons the team is growing. None of the 31 died by choice next to its queen or its leader in the 40 rounds after; 8 were rammed, 5 rammed another dragon, 5 split, 6 died elsewhere and 7 were still alive.
- **Other things checked and found not to matter:** a pearl within reach (taken 13 of 48 with a pearl next to it, but those are mostly the early outnumbered turns), an ally about to do it (she was rammed by another forgot dragon in the same round on 3 of the 203 turns not taken), the attacker's age.
- **What it costs.** forgot had an in-view chance in 308 games. In 104 it missed at least one; in 37 of those it never rammed her at all, and won 12 of the 37 (32%). In the 204 games in which it took every chance it won 154 (75%).
- In the games read: 5 of 12 in-view chances taken; the 7 not taken are the ones in 1067620 above (`b_out/mychances15.txt`).

**SSS.** 250 of 254 in-view chances taken over all games, at every length (2-3 long 155 of 155, 4 long 26 of 26, 5-9 long 59 of 61, 10-12 long 10 of 12) and every price (4 paid steps 9 of 9). In the games read: 5 of 5.
- **The 4 not taken are not exceptions to the rule.** Two are turns of a 5-long whose only path ran over cells of its own body that the counting script treats as vacated in time (1049256 r313, 1056815 r452; drawn with `b_turn.py`). Two are 10-step paths costing 7 segments (1055271 r236, a 10-long; 1059358 r421, a 12-long); SSS takes 12 of 12 six-step paths and 3 of the 5 longer ones, the two it left being these 10-step paths, so its search seems to stop at about 7-9 steps (inference).
- **Out of view: never.** 0 of 273 over all games. In 1067636 this cost the game: SSS #851 (12 long) had a free path of 6 and 5 steps (3 and 2 paid) at rounds 485-486 to forgot's 92-94-long queen, who had not moved for three and four rounds; the path ran through a portal, her head was 9 columns away, and it walked on. SSS's own queen was dead.

### 2. How hunters find her

**The kills read** (`b_out/tally15.txt`, section D; tracks in the per-game notes).

| team | game, round | killer | where it was before | in its own view before the fatal round | last move | why she could be caught |
|---|---|---|---|---|---|---|
| SSS | 1059834 r72 | #42, 5 long (3 long until r69) | 4 steps from her for 20 rounds | 13 of the 40 rounds before | 4 steps, 2 paid | it grew from 3 to 5 on two corpse pearls of a ram beside her |
| SSS | 1059840 r208 | #255, 2 long, born r200 | 6-8 steps away at r202-204 | 3 | next cell | she kept walking her 2x2 loop and stepped next to it |
| SSS | 1060356 r143 | #123, 8 long, a split child of 7 born r106 | 9-25 steps away for 30 rounds | 0 | 6 steps, 4 paid | a 2-long of the same team followed her for 24 rounds; the 8-long struck on its first turn in view |
| SSS | 1067641 r166 | #227, 3 long | walked 20 steps in 25 rounds, then 2-6 steps away for 15 rounds | 7 | next cell | she kept her loop and stepped next to it |
| SSS | 1067644 r304 | #76, 3 long | followed her for 15 rounds | 7 | 2 steps, 1 paid | she was forgot's last dragon |
| forgot | 1059840 r157 | #16, 3 long, a starting dragon that never ate | walked 20 steps in 20 rounds, then 2-4 steps away for 21 rounds | 19 | next cell | she ran into the closed end of a corridor |
| forgot | 1067641 r166 | #195, 5 long | 21 steps away 40 rounds before, 8-10 steps for 8 rounds | 3 | 5 steps, 3 paid | first turn in view and in reach |
| forgot | 1067636 r181 | #39, 3 long | walking east, 5 steps from a portal mouth | 2 | 2 steps, 1 paid | she stepped out of the portal next to it |
| forgot | 1067654 r111 | #146, 2 long, born r103 | followed her for 8 rounds | 7 | next cell | she split, and so stood still, with it next to her head |
| forgot | 1067629 r103 | #54, 2-3 long | walked 20 steps in 12 rounds | 0 | 3 steps, a pearl eaten on the way | she was walking towards it |
| forgot | 1067620 r178 | #159, 9 long | fed 13-17 steps away for 14 rounds | 1 | 6 steps, 3 paid (a path of 4 existed) | first turn in view and in reach |

- **Killer length.** SSS: 5 or longer in 2 of 5 (the lead's count over all large-map kills is 64%). forgot: 5 or longer in 2 of 6.
- **A small dragon alone does not catch a queen that keeps stepping away.** Of the 11 kills, 4 needed the queen's own step (she stepped next to or towards the killer in 1059840 r208, 1067641 r166 for forgot's queen and 1067629 r103, and stood still in 1067654 r111); 2 were forced by the map (1059840 r157, a dead end; 1067636 r181, a portal); 4 were sprints of a dragon of 5 or more (1059834 r72, 1060356 r143, 1067641 r166 for SSS's queen, 1067620 r178); and 1 was the last dragon of a beaten team (1067644 r304).
- **Followers exist in both teams and look the same.** A follower here is a non-queen dragon that keeps the enemy queen's head in its view for 6 or more rounds in a row while able to walk to her (path of 6 steps or less). SSS: 14 such streaks in 10 games; forgot: 14 in 13. All 28 are 2 or 3 long. They sit 3-4 steps from her (median distance 3 or 4 in 21 of 28). They eat nothing during the streak in 20 of 28. The longest: SSS #21 in 1059840, 30 rounds at exactly 4 steps; SSS #33 and #115 in 1060356, 29 and 24 rounds; SSS #100 in 1059834, 21 rounds; forgot #16 in 1059840, 20 rounds.
- **Is the follower a role?** What is seen: a 2-3-long that has her in view goes where she goes and stops eating. She moves one step a round and so does it, so the distance stays at 3-4 and it never gets a turn within reach. That needs no special role, only "walk towards a queen you can see" (inference). It ends with the follower ramming her in 4 of 28 streaks, with another dragon ramming her in 4, with the follower rammed in 2 and with her getting away in 18. One dragon does look like a dedicated hunter: forgot #16 in 1059840 was a starting 3-long that ate nothing in 157 rounds and crossed the board.
- **A call for help: yes for SSS, found in the sonar value itself.** A field of SSS's 64-bit sonar value decodes to a board cell, and in the rounds when SSS knows where the enemy queen is that cell is on or within 2 cells of her head in 26% of all SSS pings in 1060356 (r120-143, 1,492 of 5,832) and 39% in 1067641 (r120-166, 1,531 of 3,926); a random cell would be there 0.6% and 1.1% of the time (`b_sonar4.py`). Pings from dragons that cannot see her carry it, so it is relayed. In 1063806 the cell stayed within 2 cells of forgot's queen in 29-52% of pings through rounds 140-179 although no SSS head had her head in view for 20 rounds at a time: she was pacing where she had last been seen, so the team repeats an old sighting. In 1060356 the later killer received rays carrying her cell at rounds 123-127 and 132-133, when it was 14-20 steps from her, and closed in from round 133. SSS sends 1-7 pings a round until round 119 and four per dragon per round from round 120 (130-250 a round) in all three games.
- **forgot: weak.** The same search finds her cell in 5% (1059840, r100-157) and 9% (1067641) of forgot's pings, against 0.6-1.1% by chance: some dragons send it, the team as a whole does not repeat it. Most of forgot's value is positions of its own dragons (the sender's own head in 67% of pings, another own head in 25%; `b_sonar2.py`). Direct rays from a dragon that sees her to the later killer are rare for both teams: of the rays that ended on the killer in the 40 rounds before the 11 kills, 10 of 158 (SSS) and 2 of 131 (forgot) came from a dragon that had had her in view in the last 3 rounds (`b_rays.py`). Whatever reaches the killer comes through relays.
- **Vibing++: not found.** The same search on 1069168 and 1063780 gives nothing above chance.

### 3. A boxed-in queen

"Boxed in" = no free cell next to her head at the start of her turn.

- **A queen of 4 or more: SSS and forgot shed 2 from the tail and stay; they never cut.** Over all games (`b_qsplit.py`, `b_out/qsplit_all.txt`): Vibing++ made 67 cuts that left a queen of 8+ with 2-3 segments, in 61 of 502 games (mean length before 19; 86 -> 3 and 85 -> 3 at the top). SSS made 0 in 503 games and forgot 0 in 632. Instead they split 2 off the tail in round after round: SSS has 29 runs of three or more such rounds in 22 games (526 segments, longest 28 rounds), forgot 116 runs in 88 games (2,488 segments, longest 43 rounds, 11 still running at round 499).
- **In the games read:** both teams' 25-long queens on Slithery Fight shed 2 for nine rounds with no free cell and lose nothing (1063806, 1060000). forgot's fed queen: 82 -> 62 (1063806 r490-499, boxed by her own segment 4 after a tight loop for two pearls), 102 -> 66 (1067636 r482-499, her only exit a portal mouth she did not take), 77 -> 75 (1067446 r343, she had caught her own tail and the two shed segments were the ones in her way), 28 -> 26 and 43 -> 41 (1067634 r382, r450). All 18 SSS queen splits and 22 of forgot's 23 queen splits made with no free cell were of this kind (the other was a 4 -> 2+2).
- **Which rule is better depends on what blocks her.** Blocked by her own tail end or by another dragon that will move: shedding costs 2 and Vibing++'s cut costs everything behind the blocker (1067446: 2 against 70). Blocked by her own segment 4 for good: both end at 3, forgot's rule more slowly, which saved a 62-long queen at round 499 in 1063806. Over all games the shedding turned 5 forgot games and 3 SSS games that were lost on the queen rule with both queens alive into losses they would not have been without it (same games, nothing else changed).
- **A queen of 2-3: she dies, in all three teams.** Over all games (`b_qdeath.py`): SSS's queen died other than by an enemy ram in 50 games (10%); in 48 of the 50 she had no free cell; she was 2-3 long in 44. forgot: 71 games (11%), 66 with no free cell, 70 of them 2-3 long. The reason in the replay differs (SSS's queen moves into a body: `self` 23, `body` 18, into a head 9; forgot's gives the suicide order: `noaction` 51), the situation is the same as Vibing++'s `noaction` deaths.
- **How she gets there.** One-cell dead ends (kelp on three sides): 15 of SSS's 48, 29 of forgot's 66. A team-mate's body on at least one side: 23 of 48 and 20 of 66. An enemy head within 3 steps in only 12 of 50 and 27 of 71. She had split in the 20 rounds before in 32 of 50 and 48 of 71, so the "mother" split that leaves her 2 long is what removes her way out. Maps: Portals 16 of SSS's 50; Maze 12 and Portals 11 of forgot's 71.
- **SSS also splits to wait.** With one free cell and a feeder about to die next to her, SSS's queen splits off 2 and stays (1063806 r448, r449, r454, r457; 1067634 r471). Not seen for forgot or Vibing++.

### 4. How does SSS keep its queen alive?

- **The numbers over all games** (`b_out/cand_tab.txt`): SSS's queen is dead by round 100 in 11 of 139 large-map games and 11 of 147 medium ones (8% and 7%). forgot: 49 of 161 and 38 of 191 (30% and 20%). Vibing++: 13 of 127 and 35 of 147 (10% and 24%). On small maps all three lose her early: 66 of 217, 104 of 280, 124 of 228.
- **She does not forage like the others.** In the 10 games read she eats 2.1 natural pearls per 100 rounds against 4.7 for the average SSS dragon, and less than the average in all 10 (`b_qhome.py`, `b_out/qhome15.txt`). forgot's queen: 3.5 against 4.6.
- **She stays near her spawn.** While she is 5 or shorter she is 10.8 cells from her spawn on average and the other SSS heads 16.7; nearer than they are in 8 of 10 games. She comes back to the same corner cells to split: (46,38) four times in 1060356 and twice in 1059840, (29,7) twice in 1067644. On Tower Defense she is 0-7 cells from her spawn at all 16 checkpoints.
- **So she is inside her own team, not ahead of it.** Own heads within 8 cells: 6.3 for her, 6.5 for the average SSS dragon. Enemy heads within 8 cells: 1.1 for her, 1.7 for the average SSS dragon. forgot's queen: 1.6 against 1.4, more enemies than its average dragon.
- **She stays 2-3 long**, so a mother split never costs much and a ram on her costs the team two segments; but a 3-long queen cannot split to stand still (1059840 r157) and cannot outrun anything.
- **When an enemy head is within 3 steps** (39 rounds in 6 of the 10 games): she moves one step, 39 times of 39; 36 times the step leaves the nearest enemy head further away. The three steps towards an enemy were 1059840 r120, and the two fatal forced ones (1059840 r157, the corridor end; 1067636 r181, the portal pocket). She never splits and never pays for a second step.
- **Allies do not turn towards the intruder.** In those rounds she had no own head within 6 steps in 10, one in 12, two in 4, three or more in 13. Own dragons within 6 steps of her ended their move nearer to the intruder 40 times and further from it 44 times. Six intruders were rammed while within 6 steps of her (1059834 r276, a 24-long by a 4-long; 1059840 r125; 1067641 r148, r158, r162; 1067629 r57), each by a dragon that had the intruder within its own reach. That is the ordinary "ram a head you can reach" behaviour happening near the queen because she lives among her own dragons (inference); no dragon was seen moving between her and an intruder.
- **How she still dies** (5 deaths read): a 5-long sprinting 5 steps while she had four own heads within 6 steps (1067641 r166); an 18-long that she walked towards without ever having it in her view, striking with 5 free steps (1060000 r479); a 3-long follower and a corridor end, with 19-21 SSS units on the board and none near her (1059840 r157); a blind step through a portal (1067636 r181); a 2-3-long that came 20 steps while she walked towards it on a small map (1067629 r103).
- **Answer.** She is steered in two ways that can be seen: kept near home and kept from eating her way outward. She is not steered away from enemies beyond the one-step retreat, and nobody guards her.

### 5. Feeding and the end game

- **When, over all games** (`b_feed.py`, `b_out/feed_all.txt`; round-500 games with the own queen alive at round 300):

  | | Vibing++ (142 games) | SSS (193) | forgot (189) |
  |---|---|---|---|
  | queen first 8 or longer by round 250 | 77 | 0 | 139 |
  | ... by round 300 | 102 | 3 | 175 |
  | ... never | 10 | 79 | 1 |
  | mean queen length at r300 / r400 / r450 / end, enemy queen alive at r300 | 11 / 20 / 29 / 37 | 3 / 16 / 21 / 35 | 23 / 33 / 44 / 50 |
  | same, enemy queen dead by r300 | 12 / 23 / 31 / 38 | 3 / 4 / 9 / 23 | 22 / 34 / 42 / 46 |
  | at r400 the queen is the team's longest dragon | 69 of 110 | 31 of 163 | 110 of 162 |

- **forgot feeds its queen from about round 200-225, whatever the enemy queen is doing.** In the games read she is 6 long at round 206 (1067446), 213 (1063806), 220 (1067667) and 225 (1067636). Two games are later: 297 on Portals (1067634), and 1067620, where she grows on natural pearls to 10 by round 357 and gets her 23 corpse pearls only in rounds 400-449. Before it starts, the small dragons gather: own heads within 8 cells of the queen go from 5 to 21 between rounds 120 and 200 in 1067446.
- **SSS keeps its queen 2-3 long and decides late.** With the enemy queen alive at round 300 (102 games) its queen is 8 or longer by round 350 in 27, only after round 425 in 39 and never in 28. With the enemy queen dead by round 300 (91 games): by round 350 in 3, only after round 425 in 37, never in 51. In the games read: round 305 (1063806, the round after an SSS dragon saw forgot's 33-long queen), 302 (1067634), 438 (1060000, although SSS dragons had seen Kaizen's 17-22-long queen at rounds 364-394), 441 (1059834, enemy queen dead since round 72), never (1060356, enemy queen dead; she ends 3 long and wins).
- **How.** The same in both teams: small dragons walk to within a few cells of the queen and die there with a free cell available. forgot uses the suicide order. SSS's feeders die by a move they cannot pay for (a 2-long moving two steps, reason `noaction`) or by a move into their own body (`self`), ending 1-2 cells from her head. Near the end dragons of 20-36 do it too (forgot 30-long, 1063806 r411; SSS 29-long, r468; Kaizen 36-long twice, 1060000).
- **What it costs.** Each dead feeder leaves half its length as pearls, and the queen gets about two thirds of those: 2.6 to 2.7 segments of feeder per segment she gains, on both sides (1063806: SSS 216 for 81, forgot 183 for 70).
- **Who is the leader.** forgot: the queen while she lives (in 1067667 a second dragon of 62 as well, from round 380); if she is dead, one other dragon from about round 300 (1059834: 34 at r325, 88 at the end; 1067654: 8 at r325; 1067641: 22 at r325, 63 at the end), built the same way, with dragons of 32-57 killing themselves next to a longer one (1059834 r424, r451; 1067620 r432). SSS: a separate dragon from round 200-350 (1059834 #458/#579: 29 at r200, 83 at r375; 1060356 #105: 25 at r225, 95 at r475; 1060000: 29 at r375, 58 at the end), and the queen as well only at the end or when the enemy queen is seen to be long.
- **Share of the team's length in its longest dragon at the end** (final lengths in `games.csv`). forgot: 25% (1059840, 1067620), 29% (1067654), 31% (1063806), 32% (1067636), 33% (1067667), 38% (1063814), 51% (1059834), 52% (1067641), 71% (1067446), 73% (1067634). SSS: 9% (1060356, after its 95-long was rammed), 16% (1067641), 23% (1059834), 29% (1059840), 39% (1063806, 1060000), 60% (1067636), 100% (1067634). forgot is not always the more concentrated team; it is when its queen is dead and one dragon is all it has left to build (1059834, 1067641) or when the game is a pure queen race on a small or medium map (1067446, 1067634).
- **What each does with a queen alive at round 300-400.** forgot: has been feeding her for 100 rounds and keeps on; she is the team. SSS: leaves her 2-3 long near home and, if the enemy queen is dead, may never feed her. Neither hides her; both keep her moving every round.
- **Results with both queens alive at round 500** (`b_out/cand_tab.txt`): forgot wins 52 of 71 (its queen 50.6 long on average against 38.5), Vibing++ 24 of 40 (34.0 against 33.1), SSS 27 of 48 (36.8 against 38.0).

### 6. Leaders: kept alive or lost

- **Lost to small dragons, as with Vibing++.** Own dragons of 15+ rammed in the games read: SSS 12 (attacker 3 long 2, 4 long 3, 5-9 long 7); forgot 21 (2 long 3, 3 long 10, 4 long 6, 5-9 long 2). The attackers walk a long way to them: 38 steps in 20 rounds to SSS's 95-long (1060356 r493, then three rounds 3-5 steps away, then a 5-step sprint); 30 steps in 20 rounds to forgot's 42-long (1067654 r394); 28 steps in 20 rounds by an SSS 3-long to a forgot 22-long (1059840 r275); 34 steps in 20 rounds by a forgot 3-long to a Sponge 21-long (1067654 r216).
- **Kills of enemy dragons of 15+.** SSS: 13 (attacker 2 long 2, 3 long 8, 4 long 3; from the next cell 3, with a 2-3-step move 9, 4+ steps 1). Typical SSS attacker: a 2-long that eats one pearl and rams with a 2-step move (four of five in 1059840). forgot: 7 (3 long 2, 4 long 2, 5-9 long 3).
- **SSS may broadcast the enemy leader's cell as it does the queen's** (weaker evidence). With the enemy queen dead, a field of SSS's sonar value was within 2 cells of the head of the enemy's longest dragon in 20-38% of SSS pings in some 10-round blocks and 0% in the others: rounds 220-229 and 240-249 in 1059834 (SSS rammed forgot's longest at rounds 238 and 276), rounds 220-229 and 250-259 in 1059840 (rams at 236, 248, 275). Chance is 0.6%. The field sits at a different place in the value than the queen's and I found it by the same blind search, so it needs a second look before anyone builds on it (`b_out/sonar4_*_leader.txt`).
- **The split trick** (a long dragon splits and rams with the cheap part). SSS: 1 clear case of 13. 1059834 r482-484: a 15-long splits 15 -> 2+13 four steps from forgot's 17-long and the 2-long front part rams it two rounds later. One more attacker had split in the five rounds before (1067641 r202-207), but that was an ordinary 4 -> 2+2 followed by one pearl. forgot: 0 of 7.
- **Protection: none seen.** No escort, no retreat. SSS's 95-long in 1060356 had an enemy 7-long 3-5 steps from its head for three rounds and did not use its 24 free steps to leave.
- **Reverse splits are something else** (a long dragon keeps 2-3 segments at the front and the rest becomes a child with its head at the old tail). forgot does it when the head has no free cell: 225 of 272 in 13 games; the 2-long front part then dies. SSS does it with a free cell: 63 of 74. For neither team does it look like protection of the leader (inference): forgot's is a rescue of a trapped dragon, SSS's a way to turn round or to drop a 2-long.
- **Merging.** Both teams kill their own long dragons next to a longer one or next to the queen: forgot 18 deaths of 15+ by the suicide order with a free cell, SSS 8 (6 by a move into itself, 2 `noaction`).

### 7. Openings

The table for every game is in the per-game notes. All games in one view (`b_opentab.py`, `b_out/opentab15.txt`):

| game | map | team | units r30 / r50 / r100 | natural pearls eaten r0-39 / r40-89 | non-ram deaths r0-99 | cells visited by r100 |
|---|---|---|---|---|---|---|
| 1059834 | Around UNSW | SSS | 29 / 52 / 62 | 85 / 189 | 70 | 1,162 |
| | | forgot | 21 / 26 / 37 | 47 / 72 | 36 | 1,043 |
| 1063806 | Slithery Fight | SSS | 31 / 41 / 59 | 62 / 111 | 41 | 771 |
| | | forgot | 42 / 55 / 56 | 135 / 179 | 189 | 764 |
| 1060000 | Slithery Fight | SSS | 40 / 50 / 61 | 96 / 128 | 62 | 819 |
| | | Kaizen | 37 / 46 / 60 | 127 / 159 | 160 | 765 |
| 1059840 | Australia | SSS | 16 / 20 / 21 | 22 / 23 | 11 | 788 |
| | | forgot | 14 / 23 / 60 | 22 / 117 | 28 | 1,278 |
| 1060356 | Australia | SSS | 18 / 32 / 61 | 36 / 100 | 19 | 1,299 |
| | | bread first search | 14 / 14 / 21 | 4 / 24 | 1 | 813 |
| 1067641 | Islands | SSS | 18 / 25 / 35 | 47 / 77 | 27 | 580 |
| | | forgot | 20 / 35 / 62 | 56 / 117 | 16 | 1,113 |
| 1067636 | Maze | SSS | 10 / 16 / 35 | 29 / 65 | 24 | 387 |
| | | forgot | 12 / 17 / 26 | 27 / 40 | 15 | 396 |
| 1067654 | Australia | forgot | 12 / 21 / 35 | 14 / 68 | 11 | 1,055 |
| | | Sponge | 12 / 17 / 48 | 10 / 99 | 11 | 940 |
| 1063814 | Around UNSW | forgot | 18 / 27 / 62 | 32 / 122 | 39 | 1,091 |
| | | Sponge | 25 / 40 / 62 | 65 / 123 | 30 | 1,063 |
| 1067667 | Around UNSW | forgot | 25 / 31 / 46 | 58 / 99 | 59 | 1,125 |
| | | bread first search | 22 / 31 / 58 | 55 / 109 | 49 | 976 |
| 1067446 | Maze | forgot | 8 / 14 / 31 | 23 / 48 | 12 | 390 |
| | | bread first search | 7 / 11 / 23 | 14 / 34 | 7 | 291 |
| 1067620 | Australia | forgot | 14 / 21 / 62 | 18 / 127 | 23 | 1,315 |
| | | Vibing++ | 11 / 9 / 9 | 15 / 31 | 27 | 454 |
| 1067629 | Stripes | forgot | 3 / 8 / 12 | 14 / 27 | 4 | 226 |
| | | SSS | 4 / 6 / 5 | 14 / 30 | 19 | 162 |
| 1067644 | Tower Defense | SSS | 2 / 2 / 11 | 2 / 28 | 4 | 174 |
| | | forgot | 2 / 2 / 10 | 0 / 23 | 3 | 144 |
| 1067634 | Portals | SSS | 8 / 13 / 33 | 27 / 65 | 34 | 229 |
| | | forgot | 10 / 13 / 34 | 40 / 86 | 48 | 237 |

- **forgot does not out-eat everybody.** Its natural pearls in rounds 40-89 against the opponent's: 5.1 to 1 and 4.1 to 1 on Australia against SSS and Vibing++, 1.6 and 1.5 to 1 against SSS on Slithery Fight and Islands, 1.4 and 1.3 to 1 on Maze and Portals; but 0.4 to 1 against SSS on Around UNSW, 0.6 on Maze, and 0.7-1.0 against Sponge and bread first search in three games. Ahead by 1.3 or more in 6 of 13 games, behind by 0.9 or less in 5.
- **What it does when it is ahead: it spreads.** On Australia its heads stand in 20 of 64 squares of the board at round 60 (SSS 9, Vibing++ 6) and it has visited 1,278-1,315 cells by round 100 (SSS 788, Vibing++ 454). On Islands 1,113 against 580. Parent and child part faster after a split (6.4-7.3 steps apart after five rounds against Vibing++'s 4.0-5.3 in 1067620). Its eaters are almost all 2-3 long. It does not sprint to pearls (0-4 paid steps per 10 rounds for the whole team; SSS 0-7).
- **SSS when it is ahead** (1059834, 1060356, 1067636): the same, plus longer eaters. It splits at 5 into 2+3 as well as at 4 (15 of 92 early splits in 1059834) and 73 of its 308 natural pearls there were eaten by dragons of 4 or more (forgot: 1 of 128).
- **Split timing.** Both split as soon as a dragon is 4: 4 -> 2+2 is by far the commonest split in rounds 0-60 (1059834: forgot 40 of 45, SSS 69 of 92; 1063806: forgot 122 of 156, SSS 40 of 68). Neither has a "stop splitting" round before the 64-unit limit is reached (forgot at round 70 on Slithery Fight, 90-100 on Australia and Islands; SSS at round 70 on Around UNSW, 100 on Australia).
- **Dead ends and small rooms: both walk in and die.** Non-ram deaths in rounds 0-100 over the games read: forgot 488, of which 484 with no free cell (477 by the suicide order); SSS 317, of which 314 with no free cell (225 by a move into its own body, 89 into another body). The same cells take dragon after dragon: (30,41) 14 times and (33,22) 14 times on Around UNSW, (10,26) 11 times on Australia, (54,18) 14 times on Slithery Fight, (36,23) 10 times on Maze. A dragon walks into a pocket for a pearl, cannot turn, dies, and its pearl draws the next one. On Slithery Fight this cost forgot 429 segments in 100 rounds (204 pearls eaten back) and left it level with SSS at round 100 (137 each) after eating 350 natural pearls to SSS's 200.
- **Self-kills by choice in the opening: none.** 4 of forgot's 488 and 3 of SSS's 317 early non-ram deaths had a free cell.
- **First contact.** From round 40 on the bigger maps the teams ram each other about one for one (1067641: 30 head-on deaths each in rounds 40-99), which holds the smaller team down (SSS 25-31 units from round 50 to 90 while forgot goes from 35 to 58).

### 8. What do they do that Vibing++ does not, and the other way round?

- **The three "self-kill" styles are one behaviour.** Vibing++ orders a split that cannot be made, forgot gives the suicide order, SSS moves into its own body. In all three the dragon had no free cell (Vibing++ 347 of 359 in rounds 0-100 of six of A's games, forgot 484 of 488 and SSS 314 of 317 in the games read). It is not a choice and not a difference between the teams. It does matter for results as a cost that all three pay: see question 7.
- **Reverse splits.** Vibing++ and SSS do them with a free cell as well (38 of 70 in 1063780; 63 of 74 for SSS); forgot only when boxed in (225 of 272). No effect on results was seen.
- **Vibing++ and SSS ram the queen with long dragons; forgot does not** (question 1). It matters: forgot never rammed her in 37 of the 104 games in which it passed up an in-view chance, and won 12 of those 37.
- **Vibing++'s queen grows on her own to 5-13 by round 100-200; SSS's and forgot's stay 2-3.** A 12-13-long queen has 3-4 free steps and walks away from followers (A's finding), and when rammed she is a large loss. The 2-3-long queens of SSS and forgot cost nothing when lost in length terms, but SSS's lives longer because of where she is, and forgot's dies early because of where she goes.
- **Vibing++ cuts a boxed-in queen to 3; SSS and forgot shed 2 a round** (question 3). It decided 1063789 against Vibing++ (85 -> 3 at round 484); forgot's rule left its queen 62 long instead of 3 in 1063806 (a game lost anyway) and cost her 2 instead of 70 in 1067446.
- **forgot feeds from round 200; Vibing++ and SSS late** (question 5). It wins forgot the games in which both queens live (52 of 71) and loses it games in which it runs out of feeders (1063806: 10-14 units from round 425, its queen stuck at 77-82 while SSS's went from 64 to 85).
- **SSS decides whom to feed by what it knows of the enemy queen; forgot does not** (inference from the table in question 5: SSS's queen is 16 long at round 400 when the enemy queen is alive and 4 when she is dead). When SSS gets it wrong it loses outright (1060000: a 58-long leader and an 18-long queen against a 47-long queen).
- **SSS broadcasts the enemy queen's cell to the whole team from round 120; forgot barely; Vibing++ not found** (question 2).
- **SSS's queen waits for feeders by splitting** (5 times in 2 games, 2 segments each). Small cost, no result changed.
- **forgot's queen keeps a 2x2 loop even with an enemy head next to it** (1059840 r208, 1067641 r166) and sometimes steps next to an enemy head (1067654 r86): 11 of her 88 close-round moves ended nearer to the enemy, 3 of them fatal. SSS's and Vibing++'s queens step away (36 of 39, the 3 others forced or harmless; 151 of 151).
