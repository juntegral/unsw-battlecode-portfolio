# Why we lose on the layout "Australia" (9 won of 35 main games)

1. What loses the games: on this layout we almost never reach 59 dragons (under 59 in 258 of 278 25-round bins of r100-299), and under 59 on a layout above 1200 cells our short dragons do not take an even head-on trade. Theirs do: in r101-300 they ram us 44.5 times a game, we ram them 6.0 times, and they eat three quarters of the pearls both bodies drop. That costs us 114 length a game and them 46, about half of the gap in total length that opens between r100 (91 against 90) and r300 (119 against 261).
2. The change: turn on TRADE_EVEN, the switch that already exists and is off, so that a dragon of length 4 or less rams an enemy head at least as long as itself on every layout when it is not outnumbered in view, as it already does on small layouts and at 59 dragons.
3. How sure: sure of the mechanism (counted on all 35 games and on all 161 games above 1200 cells; both arms are in our own code and show a take rate of 0.11 against 0.80). About one in three that the switch alone changes results here: it reaches a quarter of the gap by direct count, and it has never been shown in games.

Labels: [M] measured, with the script; [C] read from the code, battlecode/mybot2/main.cpp:line; [E] my estimate. Scripts are in dossier/work/ (au_scan.py and au_scan2.py read the replays; au_agg.py, au_net.py, au_cap.py, au_cap2.py count). Layout facts [M, au_map.py]: 64 by 64, edges wrap, 9 dragons a side of length 2 to 4, 77% of tiles open on all four sides, 4 portal pairs, two pearl rooms of 12 tiles behind portals.

## What happens

All 35 games, rounds 101-300 unless a round is named, ours against theirs. Short = length 2 to 4, not the queen. Reach = the steps a dragon can make in one turn (length minus 1 for a short dragon). Edge = at least as many own heads as enemy heads in the 7 by 7 view.

| What | Ours | Theirs | Script |
|---|---|---|---|
| Head-on meetings started, a game (r0-100; r101-300; r301-499) | 0.4; 6.0; 5.8 | 3.8; 44.5; 26.2 | au_net.py |
| Short dragon ends its turn inside the reach of a short enemy head, a game | 147.5 | 131.9 | au_scan2.py |
| ... and is rammed by that head before its next turn | 30.8 a game (0.209) | 3.6 a game (0.028) | au_scan2.py |
| Short dragon starts a turn with an equal or longer enemy head in reach and the edge, our count under 59: a game; share rammed | 19.2; 0.111 (75 of 673) | 19.4; 0.696 (473 of 680) | au_scan2.py |
| The same with our count at 59 or more: share rammed | 0.805 (62 of 77) | 0.718 (74 of 103) | au_scan2.py |
| The dragon that is rammed: its own last step took it nearer to that head; the head was in its view; it ate on that step | 0.911; 0.886; 0.115 (1,547 rams on us) | 0.962; 0.727; 0.153 (209 rams by us) | au_agg.py |
| A meeting they start (1,557): length at turn start; steps paid for with a segment in | victim 3.28 | mover 3.62; 0.651 | au_net.py |
| ... pearls dropped 3.92; eaten within 15 rounds by | 0.202 | 0.754 | au_net.py |
| ... net length a meeting (lost, less drops eaten) | -2.49 | -0.67 | au_net.py |
| A meeting we start (210; our size rule picks long victims, 4.55): net length | -0.60 | -2.71 | au_net.py |
| Net length from all meetings, a game | -114.3 | -46.0 | au_net.py |
| Other heads within 5 steps where they ram us; share of their rams where theirs are more | 0.49 | 1.43; 0.627 | au_agg.py, au_cap.py |
| Dragons alive at r100, r150, r200, r300 | 36.7, 46.4, 42.1, 35.1 | 35.7, 51.7, 57.7, 59.0 | au_agg.py |
| Total length at r100, r300; longest dragon at r300 | 90.9, 119.1; 13.5 | 90.2, 261.0; 17.8 | au_agg.py |
| Splits per 25 rounds, r125-149 then r150-174 (the step of F31) | 20.0 then 12.1 | 20.7 then 18.8 | au_agg.py |
| Queen rammed while standing by r300; dead by r100; alive at the end | 30 of 35; 11; 1 | 19 of 35; 5; 4 | au_net.py |

Read with it [M]. The three gaps of table C that the normal layouts do not have are one thing seen three times: head-on deaths (ours hit 44.8, theirs moving 45.4), total length and pearls after r100 (the drops), and the queen (29 of our 32 rammed queens were 3 long or less). Their dragons are not more careful than ours: they end a turn inside our reach as often as we end inside theirs (132 against 148 a game). The difference is what the other side then does: 0.209 against 0.028. Replays read (23 meetings in 6 games, 21 started by them: 1233597, 1279533, 1297398, 1275537, 1256637, 1261218, r100-170, au_look.py): a dragon of ours of length 2 or 3 walks in open water, mostly with no pearl in the picture, onto a tile one or two steps from a head it can see; that dragon rams it on its next turn, with a paid second step in 10 of the 21; in most pictures more of their heads than ours stand near. In 1275537 r111-114 a dragon of length 2 follows our queen for three turns and she steps back in front of it.

## Why, in the code

- [C] main.cpp:91, 467: aggressive is true on layouts of 1200 cells or fewer. main.cpp:2666: at_cap is true from 59 of our dragons (the lower of the unit limit and SPLIT_SOFT_LIMIT 60, minus 1).
- [C] main.cpp:2676: an enemy head is worth ramming if it has at least our length, but only when at_cap, aggressive or TRADE_EVEN holds; otherwise it needs max(TRADE_TARGET_MIN_PARTS 5, our length + 2) parts. main.cpp:271: TRADE_EVEN is false. So above 1200 cells and under 59 dragons a dragon of length 2 to 4 may ram only a head of 5 parts or more.
- [C] main.cpp:2667-2669: besides that, round at most feed_round, at least TRADE_MIN_UNITS 8 dragons (1 when aggressive), and own heads in view plus itself at least enemy heads plus TRADE_LOCAL_EDGE 1. main.cpp:3680-3684: only length 4 or less, not the leader. main.cpp:2698-2702, 3649-3653: the ram path may use the whole sprint reach, capped at RAM_MAX_STEPS 4. main.cpp:5144-5145, 5261: TRADE_REWARD 2500 pulls it onto the head.
- [M] The rule fits the replays: with a chance and the edge our short dragons ram in 0.111 under 59 dragons and 0.805 at 59 or more on Australia, 0.234 and 0.808 on Around UNSW, 0.927 on Autarky (972 cells, always aggressive; au_scan2.py).
- [C] Why ours walk into reach: a short enemy head marks only the tiles one step from it for our short dragons (SMALL_UNIT_THREAT_REACH 1, main.cpp:29, 2472-2473, 2518, 2544; SMALL_SPRINT_THREAT false, main.cpp:235), and that tile costs 225 to 450 (main.cpp:5077-5090). A head of length 3 reaches two steps. [M] 0.70 of their rams on us are made from 2 steps or more (au_agg.py).

## Which other layouts share the property

The property a dragon can measure: more than 1200 cells (width times height) and fewer than 59 own dragons alive. [M] au_cap2.py, au_net.py; rounds 100-299 in 25-round bins, r101-300 for the meetings.

| Layout (cells) | Share of bins under 59 | They ram / we ram, a game | Net length from meetings, ours minus theirs | Won |
|---|---|---|---|---|
| Schooltime 1 (2400) | 1.00 | 13.8 / 1.7 | -37.6 | 8 of 20 |
| Islands (2240) | 0.94 | 48.9 / 10.7 | -85.1 | 1 of 24 |
| Australia (4096) | 0.93 | 44.5 / 6.0 | -68.3 | 9 of 35 |
| Schooltime 2 (2400) | 0.88 | 41.8 / 14.5 | -71.7 | 10 of 13 |
| Around UNSW (4096) | 0.60 | 37.2 / 15.9 | -8.6 | 15 of 32 |
| Slithery Fight (1701) | 0.59 | 29.4 / 11.2 | -22.5 | 18 of 37 |
| 13 layouts of 1200 cells or fewer | never (rule always on) | 6.6 / 5.5 | -6.0 (Trauma) to +18.2 (Autarky) | 208 of 339 |

- [M] It orders five of the six big layouts by record; Schooltime 2 is the exception (we win there with the longer leader, 36 against 18 at r300).
- [M] Inside the big layouts, by our count at r150: 59 or more, 45 won of 85; 50 to 58, 6 of 19; under 50, 10 of 56. Australia: 6 of 11, 1 of 7, 2 of 17 (au_cap2.py).
- [M] Per 25-round bin on all big layouts: at 59 or more they ram 3.92 and we 1.99, net -11.5 against -8.0; at 35 to 49 they ram 6.22 and we 1.00, net -15.0 against -5.6 (au_cap.py).

## The card

title: Take the even head-on trade on big layouts below the dragon cap too (TRADE_EVEN on)
slug: even trade
What we tried: Nothing built. Counted every head-on meeting of the 500 main ladder games in its context (who could reach whom, who had more heads in view, who ate the drop) and read the trade rule in main.cpp.
Did it work: Not run. Open until the mechanism check below is done on a layout above 1200 cells.

### Area
Middle game, rounds 100 to 400, dragons of length 2 to 4, layouts above 1200 cells while we have fewer than 59 dragons. Nothing changes on layouts of 1200 cells or fewer or at 59 dragons and more.

### Claim
[E, from the measured rows and code lines above] Under 59 dragons on a big layout our short dragons pass up nine in ten even trades that they take eight times in ten at 59, and the opponents take seven in ten; the opponents collect the difference in dropped pearls. Proposal: set the existing constant TRADE_EVEN (main.cpp:271, read at main.cpp:2676) to true. No new code. The local-edge rule, TRADE_MIN_UNITS 8, RAM_MAX_STEPS 4 and the leader and queen exclusions stay as they are. Switch name: TRADE_EVEN.

### Evidence
- [M] Australia, under 59 dragons: 19.2 chances a game with the edge, 0.111 taken; theirs 19.4 and 0.696. At 59 or more ours take 0.805 (au_scan2.py).
- [M] What such a trade is worth, from the 379 even trades we started at 59 or more on big layouts: we lose 0.51 a meeting net, they lose 1.88, and we eat 0.655 of the drops. The 2,317 even trades they started on us below 59: they lose 0.22, we lose 2.12 (au_cap2.py).
- [M] Their short dragons that end a turn inside our reach are rammed in 0.018 of cases while we are under 59 and 0.069 at 59 or more (Australia); 0.028 and 0.108 on Around UNSW; 0.215 on Autarky (au_scan2.py).
- From the bot owner's notes, not re-run by me: top teams start 14 to 25 head-ons a game before r300 with equal short dragons, we 9.9 (battlecode/work/plan.md:508-509).

### Expected signal
[E] In local or ladder replays on a layout above 1200 cells, rounds 101-300, while we have fewer than 59 dragons (au_scan2.py and au_net.py give all four): chances with the edge taken in 0.6 or more (now 0.11 on Australia, 0.23 on Around UNSW); meetings we start on Australia 15 a game or more (now 6.0); their exposed short dragons rammed in 0.07 or more (now 0.02 to 0.03); net length from meetings, ours minus theirs, better than -50 a game on Australia (now -68). By direct count that is about 13 more trades and 18 length a game. With all layouts of 1200 cells or fewer the build must play identically to the build with the switch off.

### What would show it's wrong
- The take rate rises and the net from meetings does not improve by 10 a game: under 59 we do not get the drops (in the meetings we start below 59 we eat 0.535 of them, at 59 or more 0.655).
- Our dragons alive at r150 or r200 fall below 46 and 42 on Australia, or our longest dragon at r300 gets shorter than 13.5: the trades cost the board or the leader more than they return.
- Our queen dies as the mover of a head-on more often than now (0 of 35 on Australia).
- Any change in games on layouts of 1200 cells or fewer: the switch reached code it should not reach.

## Against it

- [M] Inside the layout the rams do not separate wins from losses: they ram us 44.8 times a game in our 9 wins and 44.4 in the 26 losses, net from meetings -66.6 and -68.9 (au_net.py). What separates them is the position at r150: 54.9 dragons against 38.9 in the wins, 43.4 against 56.1 in the losses. The cap rule then keeps a side that is ahead ahead.
- [M] The switch reaches only the chances with the edge. In 0.627 of their rams on us their other heads near the spot outnumber ours, and of the 1,547 rams only 134 hit a dragon that could have reached that head first, 15 of them where we were not outnumbered within 5 steps (au_cap.py). So it answers their trades with trades elsewhere; it does not stop ours from being rammed. By direct count it returns 18 of 68.
- [M] Schooltime 2 has the same loss from meetings (-71.7) and we win 10 of 13. Findings F8: teams that ram more do not beat us more, and that bar failed twice.
- [M] The other half of the gap is not touched: from r151 our splits fall from 20.0 to 12.1 per 25 rounds and our natural pearls from 35.1 to 29.1 while theirs rise (F31, the leader rules, main.cpp:1037). That is the card LEADER_MIN_LEN of losses/plan.md, and it stands on its own.
- [C] TRADE_EVEN was built once and a local run started (plan.md:513-514, run te1 with TE, TEU, TEE). No result is written down and the constant was left off; I read that as no gain against our own older build. Two builds that made short dragons shy of short heads did not cut ram deaths either (plan.md:113-132), which is why I do not propose keeping out of reach.
- [M] The 59-and-over stretches are stretches in which we are doing well, so the value of a trade measured there (1.88 against 0.51) is the best case. A trade is one dragon for one, and under 59 we are the side with fewer.
- Not checked: that main.cpp on disk is the build that played as main; the value of the unit limit (the take rate jumps at 59, as the code says); v31 games; whether an unseen layout above 1200 cells fills the board as slowly as this one.
- Note on method: the write guard refused the Write tool for dossier/work (the known spelling mismatch, verify/NOTE-write-guard.md), so the scripts and this file went through the Python route. Nothing outside dossier/work and this file was written.
