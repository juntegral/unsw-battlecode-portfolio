#!/usr/bin/env python3
"""One-off: add sub-session A4's results and the lead's cross-check to findings.md."""
s = open("findings.md").read()
s = s.replace("after sub-sessions A, A2, A3)", "after sub-sessions A, A2, A3, A4)")
old = "## 7. Known already by the team (do not rediscover)"
new = """## 6e. Our own queen's deaths: what sub-session A4 found (`deep-read-4.md`), with the lead's cross-check (`check_a4.py`)

Words: **in reach** = on a cell that an enemy head in her view can move into this round; **safe step** = a one-step move that
ends outside the reach of every enemy head in her view; **queen-round** = one round in which a queen is alive; **boxed in** = no
free cell next to her head; **cut** = a split that keeps 2-3 segments for her; **shed** = a split that gives away 2 from the tail.

| Queen deaths per 1,000 queen-rounds | all | rammed after she stepped or stayed in reach with a safe step on the board | rammed, cornered | rammed by an unseen enemy | boxed in by bodies | boxed in a terrain dead end | she rams |
|---|---|---|---|---|---|---|---|
| meow, all 401 games | 6.5 | 1.86 (104 deaths) | 2.07 | 0.55 | 1.09 | 0.54 | 0.34 |
| meow live bot, queen rules on (maps over 600 cells, 175 games) | 5.0 | 1.53 | 1.73 | 0.66 | 0.73 | 0.27 | 0.07 |
| meow live bot, queen rules off (600 cells or fewer, 100 games) | 10.7 | 2.40 | 2.40 | 0.33 | 2.62 | 1.42 | 1.53 |
| our opponents in our games | 2.2 | 0.24 | 0.61 | 0.06 | 0.66 | 0.33 | 0.16 |
| top three together | 2.7 | 0.29 | 1.25 | 0.49 | 0.36 | 0.17 | 0.12 |
| top three against test4 and WHQ only (108 games) | 3.0 | 0.28 | 1.46 | 0.61 | 0.28 | 0.28 | 0.00 |

- **She ends turns in reach by choice.** Against test4 and WHQ: turns with no safe step 2.5 per 1,000 queen-rounds (top three 2.2);
  turns that ended in reach although a safe step existed 2.6 (top three 0.4). 104 of our 362 queen deaths; in 90 a safe step with
  room behind it and no portal was on the board. When she did take the safe step in the same situation she was rammed within 10
  rounds in 19-24% of cases (65-87% when she did not). Code: for the queen the danger of a cell is one term of a sum
  (`PENALTY_HEAD_RACE 450 x max(0.5, length / 4) x ...`, smallest for a 2-long) that a pearl (`EAT_BONUS 300` plus target bonus) can
  outweigh; dragons of 8 or more have a strict "least exposed cell first" order (`LONG_SAFE_MIN_LENGTH` block in
  `pick_direction()`), the 2-3-long queen never enters it.
- **The mirror.** Their queens end a turn in the reach of one of our heads as often as ours does in theirs (5.4 per 1,000
  queen-rounds, both); they ram on 71% of those turns, we on 16%. The lead's own attacker-side data agree (`check_a4.py`): in-view
  ram chances on OUR queen taken by our opponents 197 of 230 = 86% (4.1 rounds with a chance per 1,000 queen-rounds); on THEIR
  queen taken by us 99 of 446 = 22% (3.9 per 1,000). Live bot alone: 88% against 21%.
- **Boxed-in deaths are five things** (91 of 401 games): cut and stuck 14 (a boxed-in queen of 4+ keeps 2 and gives the rest to
  a child: 40 cuts of a queen of 6+ in 37 games, 10 of them at round 3 on one map, also fed queens of 57, 32 and 15; SSS and
  forgot shed 2 and wait: 0 cuts in 1,135 games, and forgot's boxed-in queens of 6+ are alive after 184 of 207 such episodes); her
  own split child on her exit 11; a team-mate's head on her exit 20; a team-mate's body 14; terrain dead end 30 (she ate inside
  in 26). Card #25 (wait) could not fire because the cut had already made her 2 long.
- **Queen rules off** (`is_queen()` false on maps of 600 cells or fewer): she dies at twice the rate; takes a portal step in 27
  of 44 small-map games with portals (7 of 175 with rules on); rams an enemy head herself with a free safe cell in 10 games; 21 of
  the 30 terrain dead-end deaths are there. On Portals the two homes are not connected at all, so all 27 of our queen deaths
  there are self-made.
- **Where she lives matters less than A2 suggested, for us**: her average distance from her start, her eating and how often she is
  seen are like SSS's and forgot's; but a short queen of ours is rammed 1.8 times per 1,000 rounds within 5 cells of her start
  and 5.5-8 beyond 10, and with no own head within 6 steps 9.7 against 2.2 with three or more. A small intruder within 4 steps of
  her is rammed by one of her team in 3.7% of cases (top three 12-17%, our opponents 13.6%). test4's queen walks a 4-cell loop in
  a quarter of her rounds and is almost never rammed on it.
- **What it is worth (A4's arithmetic on played games, three readings: strict / she then survives like a top-three queen / every
  other kind of death stays at our rate):** the "never end in reach" rule alone 26 / 7.4 / 2.4 games of 401 (plus 0.6 to 1.9
  points of win rate); all four families she controls herself (that rule, shed-not-cut, the bans on every map, team-mates off her
  exit) 59 / 18.3 / 8.7 games (plus 2 to 5 points); all 362 deaths 102 / 30.4 / 8.2.
- qn23 ("no trap" candidate, 45 games outside `games.csv`): boxed-in deaths 15 of 45 against 52 of 215 for the live bot (no gain).
  passage2 pairs: the new queen died earlier in 16 pairs, later in 11; the qh31 pairs show the same shift (16 and 10), so the
  "passage change got the queen killed" note is not carried by these data.

## 7. Known already by the team (do not rediscover)"""
assert old in s
s = s.replace(old, new)
open("findings.md", "w").write(s)
print(len(s.splitlines()), "lines")
