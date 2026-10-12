#!/usr/bin/env python3
"""One-off: bring findings.md up to date after sub-sessions A2 and A3 (corrections + new sections)."""
s = open("findings.md").read()

s = s.replace("# Fact sheet: the numbers so far (lead session, refreshed 05:10 KST on 5 Oct)",
              "# Fact sheet: the numbers so far (lead session, refreshed 10:00 KST on 5 Oct, after sub-sessions A, A2, A3)")

old = "**view** = the 7x7 square around a head. **self-kill** = death with reason `noaction`.\n"
new = old + """
**Which bot played our games (found by A3, recounted by the lead: `bybuild.py`, `recount3.py`).** Our 401 games against 2000+ teams
are eleven runs, and "meow" below pools them unless a line says otherwise: two ladder downloads (24 + 153 games, the live bot of
that hour) and smoke-test pairs in which the live bot ("-old") and a candidate ("-new") each play test4 and WeHaveQuizzes once per
map: stride-old/new, passage2-test-old/new, qh31-test-old/new (28 games each), tc30-test-new (28), tc30-dev1-old and tc30-dev1b-new
(14 each, against "dev test 1"). Two candidates are online trials of ideas in this study:
- **qh31 = queen-hunt build (card #31, hunters 4 or shorter).** Team record (`../../online/smoke/qh31-test-result.txt`,
  `qh31-analysis/summary.txt`): new 10 wins of 30, live 8 of 30 on the same pairs (live average 9.2 of 30); head-on kills of her queen
  10 -> 11; 338 hunters in 23 games, 8 rammed her queen, 36 died in head-ons with other enemies. My count on its 28 games: in-view
  chances taken by 2-3-longs 8 of 9 (live bot in the paired run 8 of 20), by 4+ longs 2 of 11 (0 of 9); only 1 game with a
  chance and no kill.
- **tc30 = trade-on-contact build** (on maps over 1,200 cells a small dragon may ram an enemy showing at least its own length; the
  live bot asks for max(5, length + 2) there). Team record: new 6 of 30, live 9.2 of 30. On large maps it rams in 28% of meetings
  (live 8%), has 52 units against 58 at round 150 (live 46 against 61), and won 0 of 12 large-map games (live 12 of 99).

In-view ram chances on her queen taken, by run: ladder 3 Oct 3 of 8; ladder 4 Oct 16 of 72 and 24 of 125 (smoke copy); stride-old 7
of 36, stride-new 9 of 37; passage2-old 8 of 27, -new 5 of 25; qh31-old 8 of 29, qh31-new 10 of 20; tc30-new 7 of 34; tc30-dev1-old
1 of 21, tc30-dev1b-new 1 of 12. The low take-up holds for every build.
"""
assert old in s
s = s.replace(old, new)

old = """| | alive | rammed | by her own move (kelp / own body / another body / she rams) | self-kill (`noaction`) |
|---|---|---|---|---|
| Vibing++ | 27% | 46% | 5% | 22% |
| SSS | 41% | 48% | 11% | 0% |
| forgot | 36% | 52% | 4% | 8% |
| meow | 10% | 63% | 28% | 0% |
"""
new = """| | alive | rammed by an enemy | boxed in or own crash (kelp / own body / another body / she rams / `noaction`) |
|---|---|---|---|
| Vibing++ | 27% | 46% | 27% (of which `noaction` 22%) |
| SSS | 41% | 48% | 11% |
| forgot | 36% | 52% | 12% (of which `noaction` 8%) |
| meow | 10% | 63% | 28% |

Correction (A2): the last column is ONE kind of event. A queen with no free cell next to her head dies whatever she does; Vibing++
and forgot send no action (`noaction`), SSS and we step into something. A2's comparable figure for "a 2-3-long queen boxed in":
Vibing++ 23%, forgot 11%, SSS 10%, ours 28% of games.

When she dies (`qearly.py`, `out2/qearly.txt`; share of games, in brackets how many of those deaths were enemy rams):

| Own queen dead before | meow | Vibing++ | SSS | forgot |
|---|---|---|---|---|
| round 50 | 20% (49 of 80) | 17% (47 of 87) | 9% (45 of 47) | 13% (68 of 80) |
| round 100 | 45% (118 of 180) | 34% (96 of 171) | 17% (82 of 88) | 30% (160 of 191) |
| round 300 | 84% (231 of 336) | 62% (187 of 312) | 43% (184 of 215) | 52% (273 of 330) |
| the end | 90% (251 of 362) | 73% (230 of 368) | 59% (240 of 296) | 64% (327 of 406) |
| before round 300, maps of 600 cells or fewer | 95% (69 of 138) | 74% | 42% | 51% |
| before round 300, maps of 601-1,500 cells | 63% (77 of 92) | 58% | 38% | 50% |
| before round 300, maps over 1,500 cells | 95% (85 of 106) | 50% | 49% | 57% |

Per map the file shows where it is worst: on Portals (the teams never touch there) our queen is dead before round 300 in 26 of 27
games, never by a ram (SSS 28%, forgot 10% of games); Maze 26 of 27 (14 rams); Tower Defense 22 of 24; weakhold 27 of 27;
Slithery Fight 24 of 29 (9 rams); Stripes 29 of 29; Australia 28 of 28 and Islands 30 of 30 (all but three by rams).
Our own queen alive at round 300, by how the economy stands then (own / enemy total length; `behind.py`, `out2/behind.txt`):
under 0.67: 26 of 168 (top three 58 of 171); 0.67-1: 8 of 61 (115 of 241); 1-1.5: 0 of 12 (194 of 312); over 1.5: 7 of 27
(218 of 332). So at the same economy our queen is alive half to a quarter as often.
"""
assert old in s
s = s.replace(old, new)
s = s.replace("How she ends (share of games, `out2/selfdeath.txt`, `out2/qmap.txt`):",
              "How she ends (share of games, `out2/selfdeath.txt`, `out2/qmap.txt`; table corrected after A2):")

old = "## 7. Known already by the team (do not rediscover)"
new = """## 6b. What sub-session A2 found in 15 SSS and forgot games (`deep-read-2.md`; the lead recounted the marked points, `check_a2.py`)

- The one hunting rule all three share: a 2-3-long with the enemy queen in view and in reach rams her (Vibing++ 186 of 186, SSS 155
  of 155, forgot 136 of 139 from round 100 on; before round 100 forgot rams only when not outnumbered locally, 47 of 51 against
  38 of 127; recounted). forgot's longer dragons mostly do not (4-long 12 of 53, 5-9 21 of 65, 10-12 0 of 22). Nobody rams a queen
  that is outside the attacker's own view.
- Queen survival is about where she lives, not about guards: SSS's queen eats 2.1 natural pearls per 100 rounds (an average SSS
  dragon 4.7) and stays 10.8 cells from her spawn (team 16.7). Nobody escorts (allies moved nearer to an intruder 40 times, away
  44). Dead before round 100 on large / medium maps: SSS 8% / 7%, forgot 30% / 20%, Vibing++ 10% / 24% (recounted).
- A boxed-in long queen: SSS and forgot shed 2 segments from the tail each round and never cut themselves short (0 cuts in 503
  and 632 games); Vibing++ cuts to 3. A boxed-in 2-3-long queen dies in all three teams.
- Feeding the queen: forgot feeds her from round 200-225 whatever the game looks like (8+ long by round 300 in 175 of 189 games)
  and wins 52 of 71 games in which both queens live; SSS keeps her 2-3 long and decides late (27 of 48); Vibing++ 24 of 40.
- The early "self-kills" of small dragons are not a choice: 97-99% happen with no free cell (one-cell dead ends holding a pearl).
- Followers (a 2-3-long keeping the enemy queen in view for 6+ rounds) exist in SSS and forgot; in 18 of 28 streaks she got away.

## 6c. Economy and contact: what sub-session A3 found (`deep-read-3.md`), with the lead's own recount (`recount3.py`, `out2/recount3.txt`)

A3's three findings were recounted by the lead with a separately written script; the recount agrees within 1-3 points.

| Large maps (over 1,500 cells) | meow live bot (99 games) | meow tc30 build (12) | opponents in our games | forgot | SSS | Vibing++ |
|---|---|---|---|---|---|---|
| Meetings (enemy head on the next cell, both 4 or shorter) that end in this side's ram | 8% of 9,789 | 28% of 1,031 | 35% | 35% | 41% | 33% |
| The same when this side is shorter / same length / longer | 13 / 9 / 5% | 43 / 33 / 7% | 62 / 32 / 20% | 64 / 34 / 25% | 83 / 40 / 24% | 53 / 34 / 23% |
| Charges per game (rams with a 2+ step move from a non-adjacent cell), rounds 0-149 | 1.0 | 3.9 | 13.5 | 8.8 | 10.2 | 12.9 |
| Share of the game's rams started by this side | 22% | 37% | 76% | 48% | 48% | 57% |
| Pearls of ram corpses eaten by this side | 29% | 35% | 68% | 49% | 50% | 52% |
| ... of the rams this side started / of the rams the enemy started | 50% / 21% | 53% / 23% | 78% / 46% | 67% / 33% | 68% / 36% | 66% / 34% |
| Free pearl on the next cell is eaten (dragon 2-4, no enemy head in view, a way out): rounds 0-149 / 150-299 / 300+ | 80 / 56 / 54% | 81 / 59 / 58% | 80 / 83 / 77% | 87 / 88 / 88% | 75 / 80 / 77% | 84 / 87 / 75% |
| ... rounds 150-299: within 9 cells of the own longest dragon (5+) / farther / no own 5+ | 41 / 58 / 66% | 40 / 61 / 60% | 81 / 83 / 84% | 87 / 89 / 87% | 80 / 80 / 86% | 86 / 87 / 87% |
| Games in which own total length is below the enemy's at round 300 | 96 of 97 | 12 of 12 | 1 of 109 | 82 of 158 | 48 of 139 | 40 of 127 |

- **On medium and small maps the live bot already rams at meetings like everyone else** (33-35% of meetings; opponents 30-31%).
  The 8% is a large-map behaviour, and the code says why: `AGGRESSIVE_MAX_CELLS = 1200` switches the trade rule
  (`worth = aggressive ? parts >= length : parts >= max(5, length + 2)`, minimum units 1 instead of 8). The tc30 build removed
  that size gate for contact and got 28%. Even so, on medium and small maps we start only 39-41% of the rams (charges 0.6-0.8 a
  game in rounds 0-149 against 2.1-2.5) and eat 41-44% of the ram pearls (opponents 51-56%).
- **The round clock.** The free-pearl row drops at exactly our `grow_round`: on large maps at round 150 (80% -> 56%), on medium and
  small maps at round 300 (85% in rounds 0-149, 82-84% in rounds 150-299, then 49-50%; near the own longest 30-45%). Every run
  and both builds show it. Code after `grow_round`: a pearl within 9 cells (Manhattan) of the known leader position costs
  `ZONE_PEARL_PENALTY 600` for everyone but the leader and loses `EAT_BONUS 300` (`score_step`, `in_leader_pearl_zone`), and dragons
  longer than 4 stop splitting (`split_child_size`). The drop is also there far from the own longest dragon (58%) and with no
  own dragon of 5+ at all (62-66%), so a remembered leader position or another rule is involved too (not visible in a replay).
- A3's reading: at contact our small dragons give way (finding 1), the enemy eats the ram pearls (2), and the round-150 clock
  turns eaters into prey (3); about 110 segments a game move to the enemy through rams on large maps.
- A3: large maps are two pairs. Australia and Islands: units and length both collapse (1 win in 58). Around UNSW and Slithery
  Fight: units level until round 300, total length 60-80% (11 wins in 53).
- A3: fewer of our dragons die in dead ends than our opponents' on 8 of 10 maps; the exceptions are Slithery Fight (sheds) and
  Portals; 6.4 of our dragons a game die by stepping through a portal onto a body they cannot see (18.4 on Islands).

## 6d. From behind, and the longest-dragon race (lead: `behind.py`, `leaderrace.py`; `out2/behind.txt`, `out2/leaderrace.txt`)

Games reaching round 300, all sizes, by own / enemy total length at round 300:

| Total-length ratio at round 300 | top three: games, won | meow: games, won | top three's wins by queen rule / longest | our wins by queen rule / longest |
|---|---|---|---|---|
| under 0.67 | 171, 15% | 168, 7% | 15 / 10 | 2 / 10 |
| 0.67-1 | 241, 48% | 61, 26% | 58 / 56 | 1 / 14 |
| 1-1.5 | 312, 61% | 12, 50% | 97 / 88 | 0 / 5 |
| over 1.5 | 332, 88% | 27, 63% | 110 / 111 (+70 wipe-outs) | 1 / 10 (+6) |

- We are far behind (under 0.67) in 63% of our games that reach round 300; the top three in 16% of theirs. A3's "they win 35-50%
  of the games in which they are behind, we 10%" is mostly this mix: inside the same band the gap is 15% against 7% and 48%
  against 26%.
- Two rough what-ifs with these four bands: our band win rates with the top three's mix of bands would give 42% (we have 19% of
  these games); the top three's band win rates with our mix would give 32%. Reading: economy is the larger lever, the conversion at
  equal economy the smaller one, and both are large. (Our two "ahead" bands hold only 39 games.)
- About half of every top team's wins in every band are queen-rule wins. Ours: 4 of 51.
- Longest dragon, medians in round-500 games (longest / total length): round 300 meow 5 / 72, Vibing++ 12 / 141, SSS 8 / 167,
  forgot 15 / 127; round 400 meow 12 / 74, Vibing++ 25 / 145, SSS 31 / 151, forgot 34 / 121; end 26 / 57, 45 / 131, 44 / 136, 50 / 106.
- Round-500 games in which both queens are dead, own / enemy total length at round 400 between 0.8 and 1.25: we win 13 of 36
  (own longest 13 at round 400 -> 32 at the end; the enemy's 21 -> 39); Vibing++ 28 of 44 (32 -> 56), SSS 37 of 61 (37 -> 54),
  forgot 30 of 51 (40 -> 61). Our code starts feeding the leader at `ENDGAME_ROUND 400` (300 in queen-feeding mode, or round 200
  with 56 units).

## 7. Known already by the team (do not rediscover)"""
assert old in s
s = s.replace(old, new)
open("findings.md", "w").write(s)
print(len(s.splitlines()), "lines")
