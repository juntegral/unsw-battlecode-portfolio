# Reports sent to the lead by slithery-sonnet

Taken from the session transcript on 2026-10-10. Times are UTC (KST = UTC+9).

---

## 2026-10-09 03:07:58 — closing summary

Verdict: several habits, but one thing decides both maps: our queen dies in 24 of 29 Slithery Fight games and 30 of 30 Portals games. No existing constant is supported by the counts. Sure about the counts (high), less sure about the causes (medium).

- **Slithery Fight:** our queen is fed from round 300 and becomes our longest dragon, then a short sprinting dragon kills her. Fed queens that survive win 5 of 5; fed queens that die win 1 of 13.
- **Portals:** our queen dies in a dead end (wall, mate body or own body) within 3 rounds of her own split, in 22 of 30 games.
- **Constant:** `QS_KEEP_LEN:4` would block the L5 queen splits that precede 14 of the 30 Portals deaths. I give it low confidence because its local head-to-head against the live bot was worse (19-2-27, 48 games, `SESSION-STATE.md` 08:31), and it would not touch the L4 splits (8 deaths) or Slithery.

**What I scanned.** Ranked and unranked games completed since 21:00Z on 10-08 (one11 to one14), scanned with `o1_scan.scan` for 59 games (Slithery Fight 29, Portals 30). My counts do not match your 2/16 and 5/16.
- **Slithery Fight:** 11 wins in 29, but only 3 in 12 among ranked games.
- **Portals:** 9 in 30, and 3 in 8 among ranked games.
- **Unranked sets:** 34 of the 59 are the unranked test sets (`ranked:false`) against Cache me outside, kraken, Preyas and similar, which the folder `live-one1` also holds. Both the all-games and ranked-only numbers are in the files.
- **By version:** Slithery one12 is 0 for 6, one13 6 for 13, one14 4 for 6. Portals one12 is 1 for 5, one13 3 for 11, one14 3 for 6.
- **No smoke games for one15** existed yet.

**Loss classes (a = our queen dead, theirs alive; b = both dead, their longest longer; c and d = none):**

| Map | Games | Losses | a | b | c / d |
|---|---|---|---|---|---|
| Slithery, all | 29 | 18 | 9 | 9 | 0 / 0 |
| Slithery, ranked only | 12 | 9 | 3 | 6 | 0 / 0 |
| Portals, all | 30 | 21 | 17 | 4 | 0 / 0 |
| Portals, ranked only | 8 | 5 | 2 | 3 | 0 / 0 |

Our queen is dead at the end in every one of these losses. Our queen alive at the end occurs only in Slithery wins (5 of 11). The round we fell behind for good has a median of 412 on Slithery and 125 on Portals, at 25-round resolution (`beh.py`; `beh=` column in `rows.txt`). It is within 25 rounds of our first queen death in 8 of 18 Slithery losses and 14 of 21 Portals losses.

**Slithery Fight, all 18 losses, the same script on both sides:**

| | r100 | r200 | r300 | r350 | r400 |
|---|---|---|---|---|---|
| Our queen length (dead counts 0) | 3.3 | 3.5 | 4.1 | 16.0 | 20.9 |
| Their queen length | 4.4 | 5.7 | 6.3 | 7.4 | 5.7 |
| Our queen alive | all | 0.89 | 0.78 | 0.61 | 0.50 |
| Their queen alive | 0.89 | 0.89 | 0.67 | 0.67 | 0.61 |
| Our total length | 140 | 199 | 219 | 192 | 169 |
| Their total length | 143 | 193 | 214 | 211 | 222 |
| Our dragon count | 52 | 61 | 61 | 51 | 45 |
| Their dragon count | 52 | 60 | 57 | 54 | 55 |

- **How she grows:** our queen eats almost no natural pearls (about 1 per 100 rounds). She grows by eating the corpses of her feeders: 24.8 per game in rounds 300–400, against 1.8, 0.2 and 1.3 in the three windows before that. Their queen eats 3.6 corpses in the same window and 10.4 in rounds 400–500.
- **Rule that starts the feeding [C]:** from round 300 the queen is always in "queen game" mode (`QUEEN_SAFE_ROUND 300`, `QUEEN_SAFE_SPAN 0`, `main.cpp:194-195`, `1680`). That sets `feed_round` to `QUEEN_GAME_FEED_ROUND 300` (`193`, `1683-1684`), and `feeding_phase()` (`7592`) switches on queen feeding for every mate. `QUEEN_LEAD_LATE` (`190`, `3207`) makes her the leader, and `feed_len_ok` (`7581`) with `QUEEN_BOOT_LEN 6` lets mates of length 2–3 feed a queen under 6.
- **Why she is short before round 300 [C]:** `QS_KEEP_LEN 3` (`2296-2299`) stops a queen shorter than 5 from splitting.
- **Cost of feeding [M]:** our total length falls from 219 to 169 between rounds 300 and 400 while theirs rises from 214 to 222. A feeder's corpse returns only part 
[result truncated — ask the agent for the rest via SendMessage]
