# Reports sent to the lead by trophy-sonnet

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 03:05:18 — closing summary

**Verdict: not broken in the live code on Trophy, about 75% sure.** The one14 figure of 40 is mostly short games, plus one loss to Preyas. Eating at r25, r35 and r50 is back at the one8/one11 level. I have no one15 Trophy game yet: Trophy is map 11 of 15 in `one15-c1`, which started at 11:57 KST.

**Where the 40 comes from**
- Of the three one14 games in the 40: `c1` ended at r47 and `k1` at r39, both wins by elimination, so their r100 totals (36 and 38) stop at the end of the game. The third, `p1`, is a loss to Preyas (46).
- Over all 91 Trophy games, 88 had us in seat A. Table and logic are in `trophy-sonnet/`.

**Numbers that decide it** (all pearls we ate, mean per game [M])

| ver | games | r25 | r35 | r50 | dragons r50 | portal crossings r0-49 |
|---|---|---|---|---|---|---|
| one8 | 8 | 10.8 | 21.6 | 43.9 | 14.8 | 3.8 |
| one11 | 4 | 11.5 | 26.5 | 51.2 | 18.2 | 3.5 |
| one12 | 4 | 7.2 | 12.8 | 33.3 | 10.0 | 0.2 |
| one13 | 10 | 6.8 | 13.7 | 25.4 | 9.0 | 0.0 |
| one14 | 5 | 12.0 | 25.0 | 50.0 (n=3) | 16.3 | 4.0 |

- The real fall is one12 and one13, which matches the two switches already removed. One12 and one13 almost never use portals before r50. In one14 portal use is back to the one8/one11 level.
- Per-game r35 totals [M]:
  - one14: 17, 21, 23, 31, 33.
  - one11: 15, 26, 31, 34.
  - one13: 7 to 27, median about 13.
  - one8: 7 to 32.
- BIG_ESCAPE cannot fire early on Trophy. It needs a non-queen dragon of length 8 or more, and our longest dragon is 5 or less at r25, r50 and r75 in all 24 games of one8, one10, one11, one13 and one14 [M]. I did not check one12.
- Eating at r50 keeps pace with how many dragons we have: one13 has 9.0 dragons and 25 pearls, one14 has 16.3 and 50.

**Same opponent, one11 against one14**
- Cache: one11 `1496855` ate 56 natural pearls by r50. One14 `1517695` ate 35 by its end at r47 (win), after a first split at r15 against r7 and a dragon lost at r8. One game each, so I can't say whether that is behaviour or chance. The r15 first split is later than one11's, but one14's other four games split at r6 to r14.
- Preyas: one11 `1498747` ate 57 by r50. One14 `1518918` ate 25 and lost.
  - We were level at r25 (13 each), then stalled.
  - From r30 to r50 we ate 9 pearls over 159 dragon-rounds. One11 ate 43 over 315.
  - Preyas had 12 to 18 dragons against our 6 to 8.
  - Boards at r38 (dragon 14) and r44 (dragon 7): short dragons on empty cells, no pearls in view, enemy heads close. Our dragons moved every round and visited 15 to 20 distinct cells, so they were not circling.
- Preyas ate 14, 33 and 20 natural pearls by r50 against one8, one11 and one12, and 59, 48 and 46 against one13 and one14. That pattern fits a change in Preyas or a bad draw, but I can't separate the two from this data.
- Kraken: one14 beat kraken twice and one11 won once. The one11 kraken game ran 291 rounds, so its r100 figure is not a clean reference.

**Not checked**
- I couldn't tell which live switch is responsible for the one14 Preyas stall. I did not look into QUEEN_FAR_HEADS, QUEEN_CORRIDOR_GUARD or QS_KEEP_MIN_UNITS 2 (a one13 change).
- One15 Trophy behaviour is unmeasured online; one15 is one14 minus TERRITORY_DECAY.
- I did not re-run the local Trophy test. The brief gives 149 to 194 pearls for one11 and one14.
- Sample sizes per version and opponent are 1 to 3 games.

**What would show it is broken:** a one15 Trophy game against Cache or Preyas with fewer than 10 pearls at r25 and fewer than 12 dragons at r50, or no portal crossings before r50 with pearls under 30. Check the first one15 Trophy replay with `trophy-sonnet/final.py` and `tl.py`.

Files are in `~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet/`:
- `table.txt`: one row per Trophy game (91). Columns: version, opponent, seat, result, last round, pearls at r25/r50/r100 for both sides, natural pearls, dragons at r50/r100, first split, queen split, splits, deaths with causes, portal crossings, queen death. Dragons at r50/r10
[result truncated — ask the agent for the rest via SendMessage]
