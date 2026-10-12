# Reports sent to the lead by shed-sonnet

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 04:11:29 — Shed counts: headline numbers

Shed headline: sheds are common at 4-5 (mostly opening) but rare from 10+, and 10+ sheds are followed by queen death in 57% within 3 rounds, 76% within 20.
Counted over 474 games (one11-16, 150 ranked + 324 unranked; deduped): 465 sheds in 281 games. By queen length before: 4-5: 432 sheds (254 games), 6-9: 12 (11 games), 10+: 21 (21 games, all one per game; per version one11 1, one12 5, one13 9, one14 4, one15 2, none in one16 games on disk).
After a shed (queen is 2 long): dead within 3 rounds 82/465 (18%), within 20 rounds 118/465 (25%), alive at end 102/465 (22%). For 10+: 12/21 within 3, 16/21 within 20, 2/21 alive at end. For 4-5: 15% / 22% / 23%. Comparison (queen 4+, enemy head within 3, no queen split that round, 2565 turns in 293 games): dead within 3 = 4%, within 20 = 17%, alive at end 23%. For len 10+ no-split with enemy within 3 (412 turns): 4% / 21% / 34%. Same nearest distance, shed vs no-split dead within 3: nd=2 35% vs 4%, nd=3 37% vs 3% (selection effect: she sheds when the bot already sees no escape, so this is not a clean counterfactual).
Games with a shed: 113/281 won (40%), queen alive at end 22%; without shed: 95/193 won (49%), queen alive 26%. Shed from 10+: 3/21 won (14%), queen alive at end 2/21; 14 of the 21 happened at round 400+ (all at round 339+). In 15 of 21 her pre-shed length beat the enemy queen's; 18 of the 21 games were lost, the 3 wins came with the enemy queen already dead. Full table and the 21 listed rows: ~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/shed-sonnet/ana.out and ana2.out. Final message with caveats follows.

---

## 2026-10-09 04:12:23 — closing summary

Sheds from a queen of 10 or longer are rare (21 in 474 games). After one, she was dead within 3 rounds in 12 of 21 and within 20 rounds in 16 of 21. I'm fairly sure of that count, but only moderately sure it shows shedding costs us the game. Sheds at length 4-5 are common (432) and mostly early. Nothing in these numbers shows shedding saving anything. The comparison is confounded, because she sheds exactly when the bot already sees no escape.

**Data.** 474 games of versions one11 to one15: 150 ranked and 324 unranked, deduped by game id. The 300 unranked games turned out to also be in `live-one1`, so nothing was double-counted. **There are no one16 games on disk, so one16 is not covered.** I read the queen's state at the start of each round and counted a shed when she went from 4 or longer to exactly 2 in a split. Distances are torus Manhattan, ignoring walls. All numbers are [M].

**1. How common**
- There were 465 sheds in 281 of 474 games.
- Sheds per game: 0 in 193 games, 1 in 171, 2 in 65, 3 or more in 45.

| Queen length before | Sheds | Games |
|---|---|---|
| 4-5 | 432 | 254 |
| 6-9 | 12 | 11 |
| 10+ | 21 | 21 |

| Version | Games | Sheds | Games with a shed | Sheds from 10+ |
|---|---|---|---|---|
| one11 | 74 | 118 | 64 | 1 |
| one12 | 72 | 136 | 62 | 5 |
| one13 | 172 | 118 | 83 | 9 |
| one14 | 100 | 62 | 48 | 4 |
| one15 | 56 | 31 | 24 | 2 |

- The 4-5 sheds are mostly 4 to 2: 424 of 432. By round, 217 of all 465 sheds fall in rounds 0-49, and nearest-enemy distance is often 7 or more. That looks like an opening effect rather than the emergency rule [E].
- The 10+ sheds are all at round 339 or later, 14 of them at round 400 or later. Nine are from one13.

**2. What happens next**

| Set | N | Dead within 3 | Dead within 20 | Alive at end |
|---|---|---|---|---|
| All sheds | 465 | 18% | 25% | 22% |
| Sheds, length 4-5 | 432 | 15% | 22% | 23% |
| Sheds, length 6-9 | 12 | 58% | 67% | 8% |
| Sheds, length 10+ | 21 | 57% | 76% | 10% |
| Comparison: queen 4+, enemy head within 3, no queen split | 2565 turns, 293 games | 4% | 17% | 23% |
| Comparison, length 10+ | 412 turns | 4% | 21% | 34% |

- Comparing at the same nearest-enemy distance, dead within 3 rounds, shed against no split:
  - Distance 2: 35% against 4%.
  - Distance 3: 37% against 3%.
  - 10+ at distance 3: 57% against 6%.
- The comparison turns are strongly autocorrelated within a game, so the 2565 is not 2565 independent samples.
- After a shed the child is alive at the end in only 29 of 465. For 10+ sheds it is alive in 7 of 21, with a mean final length of 21.
- Cutting off the last 25 rounds of each game, to remove the game-end artefact, barely changes the 4-5 and 10+ rows.

**3. Games with a shed against games without**
- With a shed: 113 of 281 won (40%), queen alive at the end in 22%.
- Without a shed: 95 of 193 won (49%), queen alive in 26%.
- The gap is mostly in the unranked games (37% against 52%). In ranked games it points the other way (49% against 44%), on small samples (84 and 66 games).
- With a shed from 10+: 3 of 21 won (14%), queen alive at the end in 2 of 21.
- 42 games had a 10+ queen within 3 of an enemy head at some turn and no 10+ shed: 21 won, 20 with the queen alive at the end.
- The shed games are the ones where the queen was already in trouble, so none of this gives a cause.

**4. Every shed from 10+**
Format is game, version, round, lengths, nearest enemy as distance(length), enemy queen length, and the outcome. "Dead" is the round our queen died. "childfin" is the child's final length.

| Game | Ver | Rd | Queen to 2 (child) | Nearest enemy | Enemy queen | Outcome |
|---|---|---|---|---|---|---|
| 1498743 | one11 | 339 | 26 to 2 (24) | 3(10) | 15 | dead 343, loss |
| 1501671 | one12 | 403 | 17 to 2 (15) | 2(2) | 0 | alive at end with 17, win |
| 1503515 | one12 | 414 | 12 to 2 (10) | 2(3) | 37 | dead 416, loss |
| 1504019 | one12 | 429 | 58 to 2 (56) | 3(3) | 0 | dead 430, loss |
| 1504148 | one12 | 344 | 15 to 2 (13) | 3(3) | 
[result truncated — ask the agent for the rest via SendMessage]
