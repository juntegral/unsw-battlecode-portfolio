# Plan from our lost ladder games (team 1119), written 7 Oct 2026 13:30 KST

**What the losses are made of.** 180 lost main games of 400. Three faults cover almost all of them and they overlap: we never grow on some 2-dragon starts (56 losses), we stop eating when our own leader phase starts (77 losses on layouts above 1200 cells, 40 of them from a level or leading position), and our queen is dead at the end in 160, which gives 51 games to their living queen, 21 of them games we had won on the next rule.
**The plan in one sentence.** Make the leader rules wait for a real leader, let the revenge hunt keep a sighting long enough to arrive, keep our own dragons off the queen's last tile, and stop spending rounds on cards 38, 47 and 48 as they stand.
**Who decides.** jun decides the order and anything that is uploaded; Zhe and QWQ decide their own cards (38, 43, 47, 48). Nothing here is accepted, and an online pair test is started by a person, not by the loop.

Labels: [M] measured, with the file. [C] read from the code, main.cpp line. [E] my estimate. Unless a file is named, [M] is my own recount of rows.jsonl at 13:10 KST (script: losses/work/recount.py). rows.jsonl has 5 more main games than summary.md (400 and 180 losses against 395 and 178; E2 43 and Q3 6 instead of 42 and 5).

## Where the losses are

| Bucket | main | v31 | What it is |
|---|---:|---:|---|
| L1 | 50 (28%) | 72 | both queens dead, lost on longest dragon or total length |
| E2 | 43 (24%) | 58 | wiped out after round 125 |
| Q2 | 30 (17%) | 25 | only their queen alive, their longest dragon also longer |
| Q1 | 21 (12%) | 21 | only their queen alive, OUR longest dragon the longer one (all 21 strictly) |
| E1 | 16 (9%) | 16 | wiped out by round 125 |
| Other | 14 (8%) | 11 | both queens alive and equal in length, lost on longest dragon (13 of 14 above 1200 cells) |
| Q3 | 6 (3%) | 4 | both queens alive, ours shorter |

My reading: four faults, seen from different sides. The counts overlap and must not be added.
- **A. We never grow (parts of E2, E1, Q2).** [M] In 77 main games we have 6 or fewer dragons at r100 or are gone before it; 56 are lost (E2 25, E1 16, Q2 9, others 6): 31% of all losses. 66 of the 77 are on layouts that start with 2 dragons a side (38% of the 174 such games; we lose 47 of those 66 and 32 of the 108 in which we grew). Pearls by r50 in them: 4.1 against 13.7. The queen is not the reason: she is alive at r50 in 58 of 66 and eats and splits as theirs does. v31: 76 games, 68 lost.
- **B. We stop eating when the leader phase starts (L1, Other, the big-layout part of Q2 and E2).** [M] Above 1200 cells we lose 77 of 127 games (103 of 273 below). 40 of the 77 were level or ahead in total length at r150; from that position we win only 42 of 82. In the 77, pearls in r151-200 are 0.69 of r101-150, theirs 1.18. Of the 47 L1 and Other losses there, our longest dragon is the shorter one at r300 in 29. Smaller layouts, same thing at r301: 19 losses level or ahead at r300.
- **C. Their queen outlives ours (Q1, Q2, Q3).** 51 losses on the queen rule with only theirs alive. Q1 is the clean part: 21 games that are wins the moment she dies.
- **D. Our queen dies (cause of C, and inside L1 and the E buckets).** [M] She is dead at the end in 160 of 180 losses: rammed 120, wall 23, own body 12, another body 5; 2 or 3 long in 145. Where the queen can leave spawn she dies first in 106 of 153 losses (82 of them by r200); we win 70 of 176 games when ours dies first and 103 of 141 when theirs does. In 38 losses their queen died first and we then lost ours (34 rammed, after a median of 82 rounds alone).

## The plan (ranked by losses reached per hour of build and test)

**1. LEADER_MIN_LEN: before feeding starts, the leader rules wait for a real leader. New card.**
- Bucket [M]: fault B. 77 big-layout losses (L1 34, Other 13, Q2 11, E2 10, Q1 9), 40 from level or ahead at r150, plus 19 small-layout losses level or ahead at r300. findings.md F31: the step sits in one round (r151 above 1200 cells, r301 below), ours lower in 99 of 107 games; splits fall to 0.68 while theirs hold at 0.98.
- Code today [C]: 468 sets grow_round to 150 above 1200 cells, else 300. From then: 1037 nothing longer than 4 splits; 2339-2354 a pearl zone is on for any known leader, at its last known position; 5055-5060 a pearl within 9 tiles of it loses EAT_BONUS 300 and costs ZONE_PEARL_PENALTY 600; 3328 is_leader() turns true, which stops splits (1028), trades (3682-3684) and harvest (1150) and doubles the head threat (5083). And the leader is not the team's leader: by 1422, 1763-1771 and 1782-1796 each dragon takes the longest dragon it has seen or heard of in the last 25 rounds, itself included. A dragon sees 3 tiles, so any longer team mate in view puts every pearl next to it inside the zone, and a dragon that knows of nobody longer is leader itself, at any length. The zone is the one rule here that changes the score of a pearl with no enemy near.
- Change: constexpr int LEADER_MIN_LEN = 0 (0 = as now). When above 0 and feeding_phase() is false: is_leader() also needs length at least LEADER_MIN_LEN, and refresh_leader_zone() leaves the zone off unless known_leader_len is at least LEADER_MIN_LEN. Once feeding starts everything is as now, so dropped feed pearls stay protected. The rounds and line 1037 stay. Test value 10. [M] Our longest dragon is 10 or more at r150 in 33 of 126 big-layout games and at r200 in 91 of 125; below 1200 cells in 2 of 156 at r300.
- Upper bound [E]: 59 games (40 + 19), every loss that entered the phase level or ahead; an upper bound because it takes the pearl step to be the reason for each. My guess at the real gain is 5 to 12.
- Against: F31_cost failed (inside a layout the games with the deeper drop are not lost more often: 37 of 84 against 35 of 88). F32 was refuted the other way: the longer leader at r300 wins the both-queens-dead ending in 49 of 57 main games, and these rules exist to make that leader. F31 bar c failed: nine tenths of the gap is outside 9 tiles of the true longest dragon; my code reading explains that but it is a reading. There is no build without the step.
- Mechanism check (replays, layouts above 1200 cells, on against off): share of non-queen turns that start beside a free pearl and end without eating, r151-199, at most 0.30 (ladder 0.40 to 0.43; 0.28 before r151; work/h13_pass.py); pearls in r151-200 at least equal to r101-150 (0.74); splits in r150-174 at least 0.9 of r125-149 (0.68; work/h14_pass.py); dragons alive at r200 not below r150 (52 then 48); our longest dragon at r300 and at the end not shorter than in the off arm. The same at r301 on smaller layouts. A shorter leader stops the card.
- Size: small (one constant, two conditions).

**2. QH_REVENGE_FRESH: with our queen dead, a sighting of theirs stays usable for 60 rounds. New card.**
- Bucket [M]: Q1, 21 losses. On the 15 played where a queen can leave spawn she was the only queen for 240 rounds or more in 13; she is 13 or longer in 8, 5 to 12 in 5, 4 or less in 2.
- Code today [C]: 1993-2007. A hunter is 4 long or less and not the leader (QH_MAX_LEN 4), holds a report no older than QH_FRESH 20 rounds, and with our queen dead every such dragon hunts from round 100. A short dragon makes one free step a turn, so one that hears the report from more than 20 steps away drops it before it arrives.
- Change: constexpr int QH_REVENGE_FRESH = 0 (0 = as now); when above 0 and revenge is true, line 1994 uses it instead of QH_FRESH. Test value 60. I leave QH_MAX_LEN alone: F39_supply failed, we have 26 short dragons alive at her turns.
- Upper bound [E]: 21, wins by rule if she dies and nothing else moves. My guess 3 to 6.
- Against: F42 is to-verify and F42_hunt (do our hunters get near her in these games at all) is not counted. F39, verifier: with the layout mix held we are at 0.6 to 0.9 of their numbers near a lone queen, not a third, and on main lone queens die equally fast. A queen of 13 makes 4 free steps a turn.
- Mechanism check: turns of their lone queen after r100 with a sighting under 20 rounds old: our heads within 12 path steps at least 2 a turn (1.15 now, F39); head-on deaths with her as the victim; their lone queen alive at the end of full games under 0.30 (41 of 102 now); our pearls after r300 not down by more than a tenth.
- Size: small.

**3. QUEEN_GIVE_WAY 2 with QUEEN_ALLY_BLOCK true. Fits card 48 as its next build.**
- Bucket [M]: 40 losses with our queen dead on a wall, herself or another body; 36 where she can leave spawn (L1 11, Q1 10, Q2 8, E2 6, E1 1). findings.md F38, verifier: one of our own dragons is on her last free tile in 80 of our 496 queen deaths, theirs 28 of 486. The rank-5 queen never died on a wall in 49 deaths, ours 47 in 271 (data/local/queen454/sol/summary.md).
- Code today [C]: 195 QUEEN_GIVE_WAY 0, used at 5006-5015 (a non-queen pays 3000 per tile for ending within that distance of the queen it sees); 163 QUEEN_ALLY_BLOCK false, used at 4960 (her room count would close tiles next to friendly heads).
- Change: no new code. One switch that sets the two constants; off = 0 and false as now.
- Upper bound [E]: about 10. Half of the 36 have a team mate in the way, and only L1 and Q1 flip by rule if she lives. 58 main wins contain the same queen death.
- Against: F37_base_rate failed (their queens have own dragons beside them more often than ours, 0.069 against 0.043 of turns, and live). No cost in games was ever shown (we won 10 of 21). In a passage one tile wide the dragon in front cannot turn round whatever it is charged.
- Mechanism check: queen deaths on wall or own body per game where she can leave spawn (0.23 now: 70 in 307) at most 0.15; deaths with a team mate on her last free tile halved; team pearls by r100 not down by more than 5 percent.
- Size: small. card-48 attempt-3 look.md asks for this rule itself: the queen died at r452 boxed in by our leader's body.

**4. QUEEN_REACH_PAD: the queen keeps one more step from a short enemy head. New card, or the next attempt of 38.**
- Bucket [M]: fault D. Where she can leave spawn she dies head-on in 110 of 153 losses, the standing victim in 105; 35 of the 110 are L1, wins by rule if she lives and their queen still dies.
- Code today [C]: 2470-2476. She marks every cell within ceil(parts/4) + parts - 1 steps of a seen head (3 steps for a head of 3), parts being the parts she can see; the cost is charged at 5069-5076.
- Change: constexpr int QUEEN_REACH_PAD = 0; when above 0, for heads of 6 parts or fewer add it to queen_reach and count parts as at least 3. Test value 1.
- Upper bound [E]: 35. My guess 2 to 6.
- Against: on main F28 is between its lines (1.22 pooled; ours higher in 23 games, lower in 18). She sees 3 tiles, so a head 4 straight steps away is out of view and the pad only reaches diagonal approaches. F13: at her last turn no safe step existed in 23 of 28 rams on a lone queen. Card 38: the looping queen stepped off late in 13 of 35 and died as often (12 and 12). More caution may mean more deaths on narrow tiles (F38).
- Mechanism check (needs the hunting spar QWQ asked for on card 38; the release bot does not hunt): from 4 path steps she steps closer in under 0.20 of turns (0.31 now, theirs 0.17; work/h12_pass.py); rams on her per game down; her wall and own-body deaths not up; her pearls by r100 not down by more than a tenth.
- Size: small, plus setting up the spar.

**5. Early growth: count first, a switch only if the count names one. Fits card 43 if it comes to a build.**
- Bucket [M]: fault A, 56 losses, the largest. No change survives the numbers yet, so it is last in spite of its size.
- Code today [C]: 346-347 the pearl pull is zero from 7 steps; 234 PEARL_FAR_DECAY 0; 264 EXPLORE_GAIN 0; 257 IDLE_ESCAPE 0; 261 FAR_GAIN 2 a step; 358 and 5061-5065 CENTER_PULL 40 a tile toward the centre for the first 30 to 60 rounds on small or long layouts when no pearl is in range, twenty times FAR_GAIN.
- Change: none yet. One replay pass by the hourly analyst (no loop round) over the 77 games, rounds 0-100: at each turn of ours that eats nothing, was a pearl known (seen in the last 25 rounds), how many path steps away, and was the dragon moving toward the centre. If a known pearl was more than 6 steps away in at least 60 percent of those turns, build FEW_UNITS_FAR (default 0): while we have that many dragons or fewer and the round is under 100, a known pearl pulls from 50 steps (the PEARL_FAR_DECAY path at 5021) and the centre pull is skipped. If no pearl was known, drop the bucket for this deadline.
- Upper bound [E]: 56. No guess; the mechanism is not known.
- Against: card 43 (idle exit) aimed here, its behaviour was real, and online it was flat: 4 of 15 against 4, 4 against 4.5, 1 against 3 (data/online/smoke/ie43-bob1, ie43-bob2, ie43-dev1 reports). F41 refuted, F7b failed. Early wipe-outs cut both ways: by r125 we win 21 and lose 16.
- Mechanism check: on layouts that start with 2 dragons, our pearls by r50 at least half of theirs (4.1 against 13.7 in the never-grew games) and never-grew games under 25 percent (38 now), with wipe-outs done by us not down (97 main wins are eliminations).

**Left out because the numbers do not carry them.**
- Card 38 (queen loop): unseen maps +41 -35, old ten +7 -12, one map 0 of 8; deaths unchanged; Zhe said drop (card-38 attempt-2 verdict.md).
- Card 47 (map updates): locally +73 -67; online 3 of 15 against 7, new only +2, live only -6 (um47-bob1-report.log); the mechanism (dragons acting on the message) was not shown.
- Card 48 as it stands (queen never feeds): the death it removes, a queen dying with no action, is 1 of our 295 queen deaths on main and in none of the 180 losses [M]. Its open question is what change 3 answers.
- A guard radius round the queen: she has fewer than 2 friends within 5 tiles in 27 of 30 rams on a lone queen (F13), and the keep-guards builds lost online (5 and 6 of 30 against 8: kg34b, kg34c reports).
- A passage-mouth rule (F38_mouth failed: a wider way existed in 0.37) and a grown queen (F36 refuted).
- Moving LEADER_GROW_ROUND_BIG as the first test: it gives up the leader that wins the both-dead ending. Kept only as the fallback arm of change 1.

## Order for the hours left (2.5 hours a round, one card at a time; now 7 Oct 13:30 KST)

- Now, no round needed: close 38; stop 47; ask Zhe whether 48's next build may be change 3. Start the two counts on the analyst side: change 5's pass and F42_hunt.
- Round 1 (7 Oct 13:30-16:00): change 1, LEADER_MIN_LEN 10. Keep replays of the behaviour games on layouts above 1200 cells.
- Round 2 (16:00-18:30): change 2, QH_REVENGE_FRESH 60. If F42_hunt has come back and says our hunters are near her and do not ram, drop it and take round 3 early.
- Round 3 (18:30-21:00): change 3 as card 48 attempt 4.
- Round 4 (21:00-23:30): if change 1 restored eating but shortened the leader, its one fallback arm (the zone gate without the is_leader() gate, or LEADER_GROW_ROUND_BIG 200). Otherwise change 4 with the hunting spar.
- Round 5 (8 Oct 00:00-02:30): one build with every switch that passed its mechanism check turned on; identity with all off, then the checks of 1 and 2 again (both steer short dragons after grow_round).
- 8 Oct morning, by a person: online pair test of change 1 alone as soon as it has passed, then of the round-5 build, 15 pairs against each of two opponents as in the um47 test.
- Rounds 6 to 8 (8 Oct 09:00-16:30): change 5 only if its count named a switch; else change 4 if not yet run; else nothing. Do not fill rounds.
- Last build starts no later than 8 Oct 17:30. From 8 Oct 20:00 only online confirmation and the final upload; submissions close 9 Oct 15:00 KST.
- Stop rules: a change that fails its mechanism check is dropped, not tuned (change 1 gets its one fallback arm). Local win counts decide nothing in either direction.

## What I could not establish

- Why we never grow on some 2-dragon starts. It is the largest fault (56 losses) and has no shared mechanism: far first pearls on one layout, pearl rooms behind portals on another, nothing named on the rest.
- Whether the leader phase costs games at all. The ladder has no control group; change 1 is the first test that can say.
- Which leader rule makes a dragon leave a pearl. I read it as the zone; it is not counted.
- Whether our hunters ever get near their lone queen in the 21 Q1 games (F42_hunt), and F42 itself is not yet recounted by the verifier.
- How to stop a queen of length 2 being rammed. The rank-5 queen has a team mate nearer to the enemy in 70 percent of samples against our 50, but that is one team in one hour and no proof of a rule.
- Anything about main against v31: different hours and opponents; every main game is from 30 hours (5 to 7 Oct).
- How the switches behave together, and their CPU cost.
- Anything about layouts nobody has seen: every count is from 19 known layouts, and the line at 1200 cells is where the code splits, not where the data put it.
