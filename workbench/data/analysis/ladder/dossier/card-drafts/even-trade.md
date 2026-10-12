What we tried: Counted every head-on meeting of the 500 ladder games in its context (who could reach whom, who had more heads in view, who ate the dropped pearls) and read the trade rule. On layouts above 1200 cells, while we have fewer than 59 dragons, our short dragons take about 1 even trade in 9 that they could; the opponents take 7 in 10.
Did it work: Not tested yet, this is a new idea. The switch already exists (TRADE_EVEN, off); a local run was started once and no result was written down.
Who decides now: The loop builds and tests it now; one teammate's OK is needed only before it ships.

### Idea by
AI

### Area
economy

### Claim
Words: a head-on meeting is one dragon moving its head onto an enemy head; the mover and the dragon it hits both lose length and drop pearls. An even trade is ramming a head that shows at least as many parts as we are long. "Short" = length 2 to 4, not the queen. "The edge" = at least as many of our heads as enemy heads in the 7 by 7 view.

Today a short dragon takes an even trade only on layouts of 1200 cells or fewer, or once we hold 59 dragons. Above 1200 cells and under 59 dragons it may ram only a head of 5 parts or more. The opponents ram our short dragons in exactly that stretch and eat most of what both bodies drop.

Proposal: turn on the existing switch TRADE_EVEN (mybot2/main.cpp line 271, read at line 2676). No new code. The edge rule, the minimum of 8 dragons, the 4-step limit and the leader and queen exclusions stay as they are. Nothing changes on layouts of 1200 cells or fewer, or at 59 dragons and more. No map names and no per-map values.

### Evidence
Measured (ladder, live bot; scripts and rows in unsw-swarm/data/analysis/ladder/dossier on jun's Mac; the starred rows were recounted a second time by a separate script):
- one layout above 1200 cells, 35 games (9 won), rounds 101-300: they start 44.5 head-on meetings a game on us, we start 6.0*
- same games: a short dragon of ours with an equal or longer enemy head in reach and the edge rams it in 0.111 of cases (75 of 673) while we are under 59 dragons, and in 0.805 (62 of 77) at 59 or more; theirs in 0.696 (473 of 680)*
- in a meeting they start, 3.9 pearls drop and they eat 0.75 of them; net length a meeting, drops counted: ours -2.49, theirs -0.67. Over a game: -114 against -46
- dragons alive there at rounds 100, 150, 200, 300: ours 36.7, 46.4, 42.1, 35.1; theirs 35.7, 51.7, 57.7, 59.0*
- all six layouts above 1200 cells, by our dragon count at round 150: 59 or more 45 won of 85; 50 to 58 6 of 19; under 50 10 of 56*
- what such a trade is worth when we do take it (379 even trades we started at 59 or more on those layouts): we lose 0.51 a meeting net, they lose 1.88, and we eat 0.66 of the drops

Read from the code (mybot2/main.cpp): TRADE_EVEN at 271; the cap test at 2666; the worth test at 2676; the edge and minimum-count tests at 2667-2669; who may trade at 3680-3684.

Against it: inside that layout the rams do not separate wins from losses (they ram us 44.8 times a game in our wins and 44.4 in our losses); what separates them is who is ahead at round 150. The switch answers their trades with trades elsewhere, it does not stop ours being rammed: only 134 of 1,547 rams hit a dragon that could have reached that head first. The value of a trade above was measured in stretches where we were doing well, so it is the best case; under 59 we are the side with fewer dragons and a trade is one for one. An earlier ladder count found that teams that ram more do not beat us more.

### Expected signal
Local games on layouts above 1200 cells, switch on against off, rounds 101-300, while we have fewer than 59 dragons: chances with the edge taken in 0.6 or more (ladder 0.11 to 0.23); head-on meetings we start per game at least double the off arm; net length from meetings, ours minus theirs, better than in the off arm. Every game on a layout of 1200 cells or fewer plays move for move as with the switch off.

### What would show it's wrong
The take rate rises and the net length from meetings does not improve (under 59 we do not get the drops). Or our dragons alive at round 150 or 200 fall below the off arm by more than a tenth, or our longest dragon at round 300 gets shorter (the trades cost the board or the leader more than they return). Or our queen dies as the mover of a head-on more often than with the switch off. Or any game on a layout of 1200 cells or fewer differs from the off arm (the switch reached code it should not reach).
