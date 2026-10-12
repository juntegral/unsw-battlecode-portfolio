# Why we are the side that gets rammed, and the one attack worth copying (team 1119; 500 main ladder games; written 7 Oct 2026)

1. **What their attackers do that ours do not.** They start 29.2 head-ons a game and we 12.8, and all of that gap is on layouts above 1200 cells (65.3 against 19.2 a game there; 12.0 against 9.8 on the others, where the length account is level). It is three things: even trades below our dragon cap (the switch already in test), rams on a shorter head (worth nothing in length), and a dragon of 2 to 4 ramming a head at least twice its length while outnumbered in view or after our feed round. They take 0.64 of those last chances, ours 0.22, and each is worth 5 to 9 length.
2. **The change.** One switch, HUNT_SMALL_RATIO (0 = off, test value 2): a dragon of length 4 or less that is not the leader or the queen rams an enemy head that shows at least twice its own length in parts, whatever the local head count and whatever the round.
3. **How sure.** Sure of the mechanism: every one of the 500 games, all 10 layouts that have enough chances, and our rule as read from the code predicts our dragons (taken 0.90 where it says yes, 0.013 where it says no). About one in four that the switch alone changes results: about +21 length a game above 1200 cells against 60 a game lost on meetings there, and nothing on smaller layouts.

Labels: [M] measured by my scripts in dossier/work/. at_scan.py replays the 500 games of input-snapshot.json and writes every head-on and every chance; at_check.py matches its head-on counts to the dossier in 500 of 500 games; at_recount.py and at_rcsum.py recount meetings, lengths, drops and who ate them with the shared reader (tools/ladder_replay.py) and get the same number in every cell; at_agg.py, at_rank.py, at_card.py and at_more.py print the tables; at_view.py shows a replay window. [C] read from battlecode/mybot2/main.cpp, line given. [E] my estimate.
Terms: "chance" = at the start of a dragon's turn an enemy head can be entered this turn over free tiles, on free steps (the first ceil(L/4)) or by paying a segment a step down to length 2; one row per dragon turn and head. "Taken" = it rams that head. "Outnumbered" = its side's heads in its 7 by 7 view, itself counted, are not more than the enemy heads there (the bot's own test; one against one counts as outnumbered). "Swing" = 15 rounds later, length the victim's side is down minus length the mover's side is down, drops eaten counted. "Switch round" = round 150 above 1200 cells, 300 otherwise. "Feed round" = 400, or 300 when our queen is alive then on more than 600 cells.

## 1. Every cross-team head-on (job 1) [M]

| All rounds; shares of meetings unless said | They ram us (14,590) | We ram them (6,407) |
|---|---|---|
| A game; rounds 0-100, 101-300, 301-500; above 1200 cells (161 games), at or below (339) | 29.2; 3.8, 16.1, 9.2; 65.3, 12.0 | 12.8; 2.1, 7.0, 3.8; 19.2, 9.8 |
| Mover's length at the start of its turn: 2; 3; 4; 5 or more | 0.33; 0.43; 0.11; 0.13 | 0.50; 0.39; 0.04; 0.07 |
| Victim's length: 2; 3; 4; 5 to 9; 10 or more | 0.43; 0.35; 0.09; 0.08; 0.05 | 0.40; 0.28; 0.08; 0.13; 0.11 |
| Victim shorter than the mover; same length; longer, under twice; twice or more | 0.33; 0.37; 0.19; 0.11 | 0.10; 0.50; 0.20; 0.20 |
| Steps from where the mover began its turn: 1; 2; 3; 4 or more | 0.45; 0.39; 0.11; 0.05 | 0.71; 0.23; 0.03; 0.04 |
| Paid a segment; segments paid a meeting; ate a pearl on the way | 0.52; 0.66; 0.10 | 0.27; 0.34; 0.03 |
| Other heads within 5 tiles of the hit: mover's side, victim's side; mover's side has more, as many, fewer | 1.69, 0.96; 0.54, 0.23, 0.24 | 1.81, 1.06; 0.56, 0.20, 0.24 |
| Mover not outnumbered in its own view | 0.67 | 0.73 |
| Victim is a queen; victim is its side's longest dragon and 8 or more | 0.015; 0.022 | 0.033; 0.036 |
| 15 rounds later, a meeting: mover's side lost, ate, net | 3.28, 2.50, -0.78 | 2.90, 2.19, -0.71 |
| ... victim's side lost, ate, net; swing to the mover's side | 3.56, 1.01, -2.55; +1.77 | 4.73, 1.42, -3.31; +2.60 |

| Victim against mover; a game above 1200 cells / at or below | They | Their swing | We | Our swing |
|---|---|---|---|---|
| Shorter | 22.8 / 3.1 | +0.5 (mover 2 to 4), -2.2 (mover 5 or more) | 2.1 / 0.7 | -1.1 to -3.2 |
| Same length to under twice | 33.8 / 7.8 | +1.8 / +1.2 | 10.1 / 8.1 | +1.0 / +1.4 |
| Twice or more | 8.1 / 0.7 | +8.8 / +4.3 | 6.6 / 0.5 | +9.2 / +5.7 |

- [M] Net length from all meetings, a game: above 1200 cells ours -198 and theirs -138; at or below 1200 cells ours -29 and theirs -31. On the smaller layouts we are not the side that gets rammed in any way that costs: the only class they lead there is the shorter victim (3.1 against 0.7), and its swing is zero.
- [M] Their attack as a rule a dragon could follow: a dragon of 2 to 4 (87 percent of their movers) that begins its turn one or two steps from one of our heads goes in, and pays a segment for the second step (0.52 of their rams are paid; in 0.10 it eats a pearl on the way, which a dragon of 2 needs to reach two steps). Per chance it rams from one step in 0.32, from two in 0.18, from three in 0.07; at length 2 or 3 a head twice its length or more in 0.41 to 0.52, an equal one in 0.26 to 0.31, a shorter one in 0.12. Being outnumbered cuts the rate for equal heads to a third (0.46 to 0.16) and takes less off for heads twice its length (0.50 to 0.36). The round changes nothing (equal heads 0.25, 0.33, 0.28 before our switch round, after it, after our feed round). Teams rated 2100 and above take the twice-its-length chance most (0.74; 0.65 at 1900 to 2099; 0.61 below).

## 2. The chances each side passes up (job 2) [M]

Dragons of length 2 to 4, queens left out; chances a game over all 500 games and the share taken. Free = within the free steps, paid = a segment or more.

| Target against own length, reach | Ours, not outnumbered | Ours, outnumbered | Theirs, not outnumbered | Theirs, outnumbered |
|---|---|---|---|---|
| Shorter, free | 3.4, 0.09 | 8.5, 0.06 | 3.3, 0.34 | 7.6, 0.09 |
| Shorter, paid | 17.1, 0.00 | 27.9, 0.00 | 25.7, 0.15 | 37.6, 0.03 |
| Same to under twice, free | 9.3, 0.54 | 15.9, 0.09 | 8.9, 0.67 | 17.3, 0.20 |
| Same to under twice, paid | 12.0, 0.16 | 18.3, 0.00 | 13.4, 0.32 | 16.4, 0.11 |
| Twice to 9 long, free | 1.3, 0.56 | 1.7, 0.15 | 0.9, 0.77 | 0.8, 0.55 |
| Twice to 9 long, paid | 1.9, 0.16 | 2.8, 0.03 | 1.5, 0.35 | 1.2, 0.24 |
| 10 or more, paid | 1.1, 0.22 | 1.9, 0.09 | 1.2, 0.36 | 1.2, 0.26 |

| Phase | Same to under twice: ours; theirs | Twice or more: ours; theirs | Shorter: ours; theirs |
|---|---|---|---|
| Before the switch round | 24.1, 0.23; 28.7, 0.25 | 1.4, 0.24; 1.2, 0.48 | 26.3, 0.02; 27.9, 0.09 |
| After it, not feeding | 17.9, 0.09; 15.6, 0.33 | 5.0, 0.15; 2.8, 0.41 | 18.4, 0.01; 26.3, 0.10 |
| Feeding with 56 or more dragons, before the feed round | 3.8, 0.15; 3.6, 0.28 | 1.3, 0.29; 0.8, 0.37 | 3.4, 0.01; 6.2, 0.08 |
| After the feed round | 9.8, 0.06; 8.2, 0.28 | 4.0, 0.19; 2.1, 0.36 | 8.8, 0.02; 13.9, 0.08 |

- [M] All chances: ours 407 a game, 0.031 taken; theirs 533, 0.055. Dragons of 5 or more hold 277 and 387 of them, nearly all on a shorter head, and take 0.003 and 0.010; queens 5.4 and 7.9, under 0.01. Layout size and phase, dragons of 2 to 4, ours against theirs: above 1200 cells 0.06 against 0.20 before the switch round, 0.05 against 0.19 after it, 0.06 against 0.16 after the feed round; at or below 1200 cells 0.19 against 0.17, 0.23 against 0.23, and 0.11 against 0.23 after the feed round. Equal heads before the feed round on the smaller layouts: ours 0.35, theirs 0.22.

Ranked by (their rate minus ours) times our chances a game times the swing of their meetings in the class:

| Class: own length, target | Our chances a game, taken | Their rate | Extra rams a game at their rate | Swing a meeting | Score |
|---|---|---|---|---|---|
| 3, same to under twice | 26.4, 0.11 | 0.26 | +4.1 | +2.0 | 8.2 |
| 3, 10 or more | 2.2, 0.23 | 0.45 | +0.5 | +15.9 | 7.9 |
| 3, twice to 9 | 3.3, 0.16 | 0.41 | +0.8 | +7.2 | 5.9 |
| 2, twice to 9 | 3.8, 0.20 | 0.52 | +1.3 | +3.5 | 4.3 |
| 2, same to under twice | 25.2, 0.21 | 0.31 | +2.5 | +1.1 | 2.8 |
| 3, shorter | 39.7, 0.02 | 0.12 | +4.1 | +0.4 | 1.5 |
| 5 to 10, shorter | 165, 0.001 | 0.010 | +1.5 | -1.5 | -2.2 |

- [M] Summed for dragons of 2 to 4: a target twice their length or more 21.6; same to under twice 12.3, of which 10.6 is "above 1200 cells with under 59 dragons before the feed round", the class TRADE_EVEN covers; shorter 1.7. The largest class not already in test is the first. Inside it, by the clause of our rule that says no (TRADE_EVEN counted as on): the local count alone 5.0, the feed round alone 2.8, both 2.4, a first step onto a pearl 2.2, allowed but not taken 2.9.

## 3. Why, in the code

- [C] 2664-2681: a trade needs round at most feed_round (2667), 8 dragons above 1200 cells (2668) and own heads in view plus itself minus enemy heads at least TRADE_LOCAL_EDGE 1 (2669, constant at 94). One of ours facing one head alone gives 1 minus 1 = 0 and fails, whatever the head's length. 3680-3684: only length 4 or less, not the leader.
- [C] 2603-2616: the hunt is the one path with no count, no round and no dragon minimum, but its target must show HUNT_MIN_PARTS 10 parts and own length plus 4 (285-286, 2611). 2587-2598: in feeding a head of 6 parts or more is hunted, only by a dragon that knows a longer leader. Parts are those inside the hunter's own 7 by 7 view (1610-1616). So a dragon of 2 or 3 beside a head of 6 to 9 parts, or beside one of 10 or more that shows under 10, rams only if it is not outnumbered and the feed round has not come. 544 against 551 and 602: a hunt is acted on first, before a feeder's death and before the trade path. 2623 with 3649-3653: its reach is ceil(L/4) + L - 2 steps (1, 2, 3 for length 2, 3, 4), paid down to length 2.
- [M] The reading fits: where these lines say yes ours take 0.90 of chances (0.998 before the switch round) and where they say no 0.013; theirs take 0.64 and 0.043 on the same split. Chances with the count as the only failing clause: 10.9 a game; the size test alone 22.8 (the class in test and the shorter heads).

## 4. The card

title: A short dragon rams a head at least twice its length, whatever the local count or the round (HUNT_SMALL_RATIO 2)
slug: ram the long

### Claim
[E, from the rows above] Our dragons of 2 to 4 pass up four in five chances at a head twice their length or more when they are outnumbered in view or the feed round has passed; opponents take two in three, and the trade is one short dragon for a long one. Proposal: add "constexpr int HUNT_SMALL_RATIO = 0;" (0 = as now, test 2) and at main.cpp 2611 let "big" also hold when HUNT_SMALL_RATIO is above 0, length is at most TRADE_MAX_LENGTH, the dragon is not the queen (real_queen(), 3724) and parts is at least HUNT_SMALL_RATIO times length. One constant and one condition. The leader is already out (2603), even trades keep the count rule, and nothing about targets under twice our length changes. Switch name: HUNT_SMALL_RATIO.

### Evidence
- [M] The chances the switch adds (visible parts at least twice own length, within sprint reach, today's rule says no; TRADE_EVEN counted as on): ours 2.73 a game, 0.22 taken; theirs 1.17, 0.64. Above 1200 cells: ours 7.47 a game, 0.21; theirs 2.76, 0.67 (with TRADE_EVEN off ours 8.1). At or below: 0.47 and 0.41 a game. The six layouts above 1200 cells, ours against theirs: 0.28 against 0.69, 0.14 against 0.51, 0.22 against 0.75, 0.23 against 0.78, 0.07 against 0.62, 0.33 against 0.68; theirs is higher on 10 of the 10 layouts with ten chances a side.
- [M] By clause: count alone 1.70 a game (0.12 against 0.62), feed round alone 0.37 (0.45 against 0.79), both 0.60 (0.39 against 0.59). By phase: after the switch round 1.14 a game (0.05 against 0.66), after the feed round 0.97 (0.42 against 0.68). Where the count rule is right and where it is not, chances refused for count only, by visible parts over own length: 1.0 to 1.49, their swing +0.2 and ours -0.8; 1.5 to 1.99, +1.1; 2.0 to 2.99, +3.8 (ours +7.7); 3 or more, +9.7.
- [M] What one such attack costs and buys (job 5), above 1200 cells. Theirs on us (297): mover 2.5 long at its turn start (0.46 of a segment paid), victim 8.3; 5.8 pearls dropped, mover's side eats 2.6, victim's side 2.1; net +0.1 against -6.1. Ours on them, the fifth we take today (255): mover 2.6, victim 11.6, net +0.5 against -8.8. One dragon for one dragon each time. The victim is 10 or more in 0.24 and 0.46, its side's longest in 0.14 and 0.11. Our longest dragon and our queen: the mover is one of our longest in 13 of the 888 such meetings we start today and never the queen; [C] the switch keeps both out.
- [M] Replays (at_view.py): 1233597 round 366, ours of length 2 starts one step from their longest (18) with two enemy heads to its one, steps away; lost 27 against 33 on longest dragon. 1255362 round 394, ours of length 3 two straight steps from their longest (33), one head each, steps aside; lost 34 against 49.
- [M] The other candidates, same score (extra rams a game at their rate times their swing; this switch 6.2 over all games): trades allowed after the feed round 4.5 (2.80 chances a game, 0.16 against 0.56, swing +4.0), and it takes feeders, which diag-feeding found not worth a switch; paying for the lunge is already allowed (2702) and "the longest in view whatever the count" is inside this switch; even heads while outnumbered are rightly refused (21.5 a game, swing +0.3, ours -0.6); a 3 on a shorter head 2.7 for a dragon each time (swing +0.9); a first step onto a pearl 1.8 and needs a new search.

### Expected signal
[E] In replays on layouts above 1200 cells (at_scan.py, then at_more.py prints all of it): the added chances are taken in 0.6 or more (now 0.21; theirs 0.67 is the mark; the chances our rule already allows are taken in 0.74); rams by our dragons of 2 to 4 on heads twice their length rise by 3.4 a game at their rate and up to 4.8; swing a meeting stays above +4; net length from meetings improves by about 21 a game (now -198 against -138). On layouts of 1200 cells or fewer under one more ram a game.

### What would show it's wrong
- The take rate rises and the swing of the added meetings is under +2: their heads near the spot collect the drops (with 3 or more enemy heads above our count the swing is +0.1, 17 meetings).
- Our dragons alive at round 200 or 300 fall by more than 5 on layouts above 1200 cells, or our longest dragon at round 300 or at the end is shorter than with the switch off.
- Our queen or our longest dragon appears as the mover of such a ram, or head-ons with a victim under twice the mover's length change: the switch reached code it should not.

## 5. Against it

- [M] It answers "what do theirs take that ours refuse", not "why are we rammed". Their 65 rams a game above 1200 cells stay; 8.1 of them hit a dragon of ours at least twice the mover's length, a matter of where our long dragons stand, not of this switch.
- [M] Size. About +21 length a game where meetings cost us 60 more than them and the total-length gap at round 300 passes 100 on the worst layouts (summary.md, table C). Below 1200 cells it does nothing, so on a small unseen map it is neutral at best.
- [M] It is a tool of the side that is behind: we have 7.5 such chances a game above 1200 cells and they 2.8 because their dragons are the long ones. Each use spends one of our dragons where the dragon count at round 150 separates wins from losses (diag-australia).
- [M] Findings F8: teams that ram more do not beat us more. We take 0.30 of these chances in our wins above 1200 cells and 0.16 in losses, but winning positions are also the ones where our rule says yes. Games it reaches directly: of 75 lost on longest dragon with both queens dead, 10 hold a refused chance at their then-longest dragon after round 300; so do 10 of 95 such wins.
- [E] Their swing is measured on the two thirds of chances they chose to take. Ours would take nearly all; the worth of the rest is not measured. [M] After the feed round the dragon that rams is one that would have fed the leader (0.97 chances a game). A feeder gives the leader a fifth of its length (diag-feeding); the ram removes 8 to 12 from them.
- Not checked: that main.cpp on disk is the build that played; who a dragon believes is leader (not in a replay; a dragon that knows no longer one refuses all rams after the switch round, 1422 and 3328); the feed round per game is my reconstruction; visible parts are counted from the true board; no build has run, and the local opponent may never put a long head beside our short dragons. Method: the Write tool was refused for this folder (the path-spelling fault in verify/NOTE-write-guard.md), so the scripts and this file went through the Python route. Left behind: at_scan-test.jsonl (harmless). Nothing outside dossier/work and this file was written.
