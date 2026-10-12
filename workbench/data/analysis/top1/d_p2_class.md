## 2. Every queen death, classified (question a)

**How a death gets its kind.** `d_class.py` walks each replay and stores the board at the start of the queen's own turn for her last 13 turns. `d_tab.py` then gives each queen one kind from the board at the start of her **last own turn**:

- **Rammed** (an enemy moved its head into hers). Four kinds, decided by two facts: was the killer's head in her view when her last turn began, and did she have a one-step move that ended outside the reach of every enemy head in her view.
  - *stepped in*: the killer was in view, she began the turn outside every visible reach, a safe step existed, and she ended in reach.
  - *stayed in*: the killer was in view, she began the turn in reach, a safe step existed, and she ended in reach again.
  - *cornered*: the killer was in view and none of her one-step moves ended outside reach.
  - *unseen*: the killer's head was outside her 7x7 view when her last turn began (or it was born by a split after her turn).
- **Boxed in** (she died by her own order with no free cell next to her head). The sub-kind names what stood on the sides that were not kelp and not her own body: a team-mate, an enemy, or nothing (then it is a *terrain dead end* if her head stood on a tree cell, else *own body*).
- **Own ram**: she moved her head into a head herself. A few rare kinds are joined as "other".

The reach model: an enemy of length L can move its head into a cell this round if a path of body-free cells of k steps leads there with k no larger than ceil(L/4) + (L - 2), plus one for each pearl it eats on the way. Bodies are taken where they stand when her turn starts, and her own last segment is taken as gone. Dragons that move between her turn and the enemy's turn are not modelled. Where it can be checked it holds: with the killer in view, the model called the cell she died on safe in 2 of our 220 rams and in 15 of the top three's 603 (the "model miss" row).

The four ram kinds of our 251 rammed queens were counted a second time by a script that shares no code with the first and enumerates every enemy move step by step (`d_recount.py`, `d_out/recount_summary.txt`): killer in view 220, a safe step existed 106, cornered 114, unseen 31, the same as below. The kind differs in 3 games: in two the queen made a two-step move that the recount does not follow, in one a pearl on the enemy's path is counted differently.

None of our 362 queen deaths is a time-out or an illegal order: the kind "no action with a free cell" is empty for us.

Counts are games; the percentage is the share of that group's games. Source: `d_md.py`, output `d_out/md_class.md` (the same numbers in another layout: `d_tab.py`, `d_out/tab.txt`).

@@include d_out/md_class.md@@

**The same deaths as rates** (`d_haz.py`, `d_out/haz.txt`). Shares of games flatter a short-lived queen: one that lives 280 rounds has twice the time to meet each kind of death as one that lives 140. "Stepped or stayed in" joins the two avoidable kinds; "cornered" includes the model misses; "boxed by bodies" joins team-mate, enemy and own body.

| Deaths per 1,000 queen-rounds | all | rammed: stepped or stayed in | rammed: cornered | rammed: unseen | boxed by bodies | boxed: terrain | own ram | mean rounds alive |
|---|---|---|---|---|---|---|---|---|
| meow, all 401 games | 6.47 | 1.86 | 2.07 | 0.55 | 1.09 | 0.54 | 0.34 | 139 |
| meow live bot (275) | 6.31 | 1.73 | 1.88 | 0.59 | 1.17 | 0.53 | 0.41 | 143 |
| ... rules on (175) | 4.98 | 1.53 | 1.73 | 0.66 | 0.73 | 0.27 | 0.07 | 172 |
| ... rules off (100) | 10.68 | 2.40 | 2.40 | 0.33 | 2.62 | 1.42 | 1.53 | 92 |
| meow against test4 and WHQ only (313) | 6.46 | 1.93 | 2.04 | 0.60 | 1.10 | 0.48 | 0.28 | 139 |
| our opponents (401) | 2.15 | 0.24 | 0.61 | 0.06 | 0.66 | 0.33 | 0.16 | 278 |
| forgot (632) | 2.79 | 0.27 | 1.50 | 0.48 | 0.16 | 0.20 | 0.13 | 230 |
| SSS (503) | 2.12 | 0.27 | 1.04 | 0.41 | 0.17 | 0.11 | 0.06 | 277 |
| Vibing++ (502) | 3.42 | 0.33 | 1.19 | 0.62 | 0.87 | 0.20 | 0.19 | 214 |
| top three together (1,637) | 2.73 | 0.29 | 1.25 | 0.49 | 0.36 | 0.17 | 0.12 | 240 |
| top three against test4 and WHQ only (108) | 2.96 | 0.28 | 1.46 | 0.61 | 0.28 | 0.28 | 0.00 | 229 |

Our queen dies 6.5 times per 1,000 rounds she is alive, a top-three queen 2.7 times. The gap of 3.7 splits like this: stepped or stayed in 1.57 (42% of the gap; our rate is 6.4 times theirs), cornered 0.82 (22%; 1.7 times), boxed by bodies 0.73 (20%; 3 times, though Vibing++ is as bad as we are), terrain dead ends 0.37 (10%; 3 times), own rams 0.22 (6%; 3 times), unseen rams 0.06 (none: the same rate). Against the same two opponents the picture is the same (6.46 against 2.96; stepped or stayed in 1.93 against 0.28).

**The boxed-in deaths by what blocked her** (`d_box.py`, `d_out/box.txt`):

| Boxed in by | meow, all | live bot | live, rules on | live, rules off | our opponents | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|---|---|
| cut and stuck: she cut herself from 6 or more to 2-3 and died boxed in | 14 | 11 | 11 | 0 | 10 | 0 | 0 | 4 |
| her own recent split child on her last exit (not a cut) | 11 | 7 | 1 | 6 | 8 | 1 | 0 | 16 |
| nose to nose: a team-mate's HEAD on her last exit | 20 | 17 | 8 | 9 | 23 | 8 | 8 | 34 |
| another team-mate's body segment on her last exit | 14 | 9 | 2 | 7 | 20 | 9 | 14 | 31 |
| an enemy body on her last exit | 2 | 2 | 0 | 2 | 5 | 5 | 2 | 9 |
| her own body only, not a dead end | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 |
| terrain dead end (tree cell) | 30 | 21 | 8 | 13 | 37 | 29 | 15 | 21 |
| all | 91 | 67 | 30 | 37 | 110 | 52 | 39 | 115 |
| ... one of her sides was a portal edge (the cell behind it is outside her view) | 29 | 19 | 0 | 19 | 14 | 3 | 19 | 18 |

For the terrain dead ends, the turn on which the free space around her fell under 12 cells: she stepped onto a pearl in 16 of our 30, a roomier free side existed in 21, she ate inside in 26 and split inside in 18. For "nose to nose", the space was open until the very last turn in 12 of 20: the team-mate stepped in front of her after her move.

**How good was the safe step she did not take** (`d_ramdet.py`, `d_out/ramdet.txt`). "Roomy" = not a tree cell and at least her length + 2 body-free cells behind it.

| Stepped or stayed in | deaths | a roomy safe step existed | ... and it did not cross a portal | the only safe step led into a pocket | the only roomy safe step crossed a portal |
|---|---|---|---|---|---|
| meow, all | 104 | 92 | 90 | 12 | 2 |
| meow live bot | 68 | 61 | 59 | 7 | 2 |
| top three | 112 | 75 | 71 | 37 | 4 |
