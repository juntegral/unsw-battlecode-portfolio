from pathlib import Path
p=Path('data/analysis/top1/TEAM-BRIEF.md');s=p.read_text()
def block(a,b,t):
 global s
 i=s.index(a);j=s.index(b,i);s=s[:i]+t.strip()+'\n\n'+s[j:]
block('## 7. Small dragons','### Replays to open\n\nSources: `deep-read-3.md`', '''## 7. Small dragons circling instead of finding pearls

### What the data says

- No-food-for-20-rounds dragons at round 90 / 140: ours 19/41 and 25/46; test4 20/52 and 31/62; WHQ 20/50 and 25/59. These are mean counts, not a no-pearl-visible loop rate. Large-map samples: ours 111, test4 42 and WHQ 44 against us. Source: `deep-read-3.md`, question b, point 7.
- Undisturbed pearls within six steps were eaten after 2.6 rounds by us in rounds 50–99; test4 3.0, WHQ 3.1, forgot 2.6, SSS 2.6, Vibing++ 2.0. Source: `deep-read-3.md`, question b, large-map sample.
- Parent-child distance five rounds after splitting: ours 6.2, test4 6.1, WHQ 6.4, forgot 6.1, SSS 5.7, Vibing++ 5.9. Children's steps onto unvisited cells: 21 / 21 / 20 / 20 / 18 / 18%. Large maps, rounds 0–149. Source: `deep-read-3.md`, question c.
- Own-half fountains eaten from by 150: ours 62%, opponents 80%, each top team 69%. Enemy-half fountain pearls/game in rounds 50–149: ours 34, test4/WHQ 76 each, forgot 58, SSS/Vibing++ 65 each. Source: `deep-read-3.md`, comparison table, rows 3, 5.
- Live free-pearl take rates on big maps at rounds 140–149 / 150–159 / 200–299: **84 / 64 / 58%**, opponents 86 / 85 / 85%. Small maps at 290–299 / 300–309 / 310–319: 83 / 64 / 51%, opponents 81 / 82 / 80%. All eleven runs in the 401-game sample show the switch. Source: `REPORT.md` §3.2(a).
- In 82 readable earlier-bot games, post-switch small-map take rates at distance 0–3 / 4–6 / 7–9 / 10–12 from the believed leader were 35 / 16 / 19 / 81%. Under 40% named the true longest. Source: `REPORT.md` §3.2(b–c).
- Natural pearls per 50 rounds before→after switching: small-map live cohort 39.5→31.0 (99 games), big-map 81.1→54.0 (75); opponents 51.4→48.7 and 130.6→130.8. Leaders' intake stayed 3.2→3.2 and 4.1→3.8. Source: `REPORT.md` §3.2(d–e).

Large-map means, sources by row: later `deep-read-3.md`, comparison table rows 1–2; earlier `findings.md` §2. Ours has 111 games; the later read's top-team round-300 survivors are forgot 158, SSS 139, Vibing++ 127, but its intake sample is not restricted to survivors. The earlier fact sheet gives round-100 units ours 39, Vibing++ 38, SSS 49, forgot 47; the later read gives 43 / 42 / 54 / 52. Both are retained as different counters, not silently combined.

| Measure | Ours | Opponents | Forgot | SSS | Vibing++ |
|---|---|---|---|---|---|
| Units 100 / 150, later | 43 / 47 | test4 56/62; WHQ 53/59 | 52 / 58 | 54 / 58 | 42 / 50 |
| Natural pearls 0–49 / 50–99 / 100–149, later | 72 / 91 / 79 | test4 76/125/129; WHQ 81/122/133 | 84 / 121 / 117 | 75 / 118 / 122 | 71 / 113 / 121 |
| Units 200 / 300, earlier | 39 / 34 | all 61 / 61 | 57 / 57 | 58 / 59 | 53 / 55 |
| Total length 100 / 200 / 300, earlier | 98 / 116 / 113 | all 138 / 254 / 326 | 117 / 165 / 183 | 130 / 195 / 220 | 105 / 177 / 208 |

### What the top teams actually do

They continue eating near the leader. Small-map free pearls within nine cells of a length-10+ leader, rounds 300–399: live meow took 29%, opponents 87%, forgot 96%, SSS 80%, Vibing++ 88%, in the main study sample. Source: `REPORT.md` §3.2(f).

The study's own pick was to remove the pearl zone before feeding, then reserve a smaller area around a visible leader. Its estimate was +0.3 to +2 percentage points, most likely +1; the amended design was never tested. This reports the study's conclusion, not a ranking of cards. Source: `REPORT.md` §§3.1, 3.4, 3.7.''')
block('### Not known\n\nThe economy read','## 8. Late game', '''### Not known

No exact “nothing visible, choose a two-by-two loop” rate or step scores were measured. The Islands camper circles six cells. Early dispersal and undisturbed eating do not establish a general search failure. Source: `deep-read-3.md`, questions b–c and Islands notes.

The later red team rejected “the zone gives the leader nothing”: per small-map race, the final lineage ate 2.4 natural and 3.4 corpse pearls declined in it; 7/41 wins had smaller margins. Removing all reservation risks those pearls. More length also did not establish more wins: the trade build gained 21% big-map length at 300 but won 0/12. Sources: `redteam-2.md` §5; `REPORT.md` §3.7. Neither tests #33 alone.''')
block('## 8. Late game','### Replays to open\n\nSources: `deep-read-5.md`', '''## 8. Late game: feeding and the race to the longest dragon

Card #22 has feeders die in place and the leader sprint to their corpses. The sources do not test that exact behaviour.

### What the data says

- Races: ours **41/143 wins**, top three 266/447. At round 300, 106/143 of ours had under 0.8 of enemy potential; we won 20, top three 23/94 in that state. Potential = longest plus pearls all other dragons would drop. Source: `deep-read-5.md` opening, §1.
- Under two thirds of enemy total length at 300: ours 168/268 games reaching it, top three 171/1,056; wins within the band 7% versus 15%. At ratio 0.67–1: 26% of 61 versus 48% of 241. Denominators sum the source rows. Source: `REPORT.md` §2.
- Median feeding starts: live meow 401 (105/186 games with starts), forgot 359 (309/400), SSS 301 (291/334), Vibing++ 363 (236/322). Small-map medians: 403 / 372 / 307 / 401. Start = first of three feeder deaths within 15 rounds by a non-queen leader. Source: `deep-read-5.md` §2e.
- Apparent recipients ate 54% of live-meow feeder pearls; other allies 36%, enemy 3.4%, nobody 7%. Recipient shares: forgot 78%, SSS 77%, Vibing++ 77%, opponents 71%. Small-map races from 250; samples 53 / 65 / 42 / 67 / 78. Source: `deep-read-5.md` §2, Tables A1, B2.
- Following the final leader's ancestry instead: it ate 39% of our pearls from deaths by choice after 300 on small maps, opponents 39%, top three 45%; big maps 26 / 16 / 29%. The later report rounds ours to 25%. Different definition from apparent recipient above. Sources: `deep-read-5.md` §1; `REPORT.md` §3.6.
- Final longest / final potential, small-map medians: live meow 65%, candidates 71%, forgot 69%, SSS 79%, Vibing++ 59%, opponents 77%. Samples: 53 / 25 / 65 / 42 / 67 / 78 races. Source: `deep-read-5.md` §2, Table A1.
- At level potential before feeding, ours won 11/23 races, top three 99/169. The later red team attributed about 45% of the earlier gap to comparing total length after feeding. Its remaining estimate was about 8 wins across our 143 races at top-three conversion rates, range 0–16. Sources: `deep-read-5.md` §1; `redteam-2.md` §§1, 5.

### What the top teams actually do

Feeders die one to three steps from a larger head. In small-map races, one-step deaths were SSS 65%, forgot 14%, Vibing++ 12%, live meow 5%. The recipient and nearby allies eat the corpse. No remote summons was established. Source: `deep-read-5.md` §2, Table B2.

There was no pre-feeding gathering: heads within 15 cells of the longest at 50 / 25 / 0 rounds before start were forgot 15 / 14 / 13, SSS 18 / 19 / 18, Vibing++ 17 / 15.5 / 15. A clock tied to units or map size is inference; replays cannot distinguish them. Source: `deep-read-5.md` §2e.

Queen feeding differs. Forgot feeds from about 200–225 and reached length 8+ by 300 in 175/189 relevant games. SSS keeps her short and decides later. Vibing++ has both early and late queen-feeding examples; voluntary disposal of a fed queen was not observed. Sources: `findings.md` §6b; `deep-read.md` §f.''')
block('### Not known\n\nThe race read initially','## 9. Anything', '''### Not known

Earlier leader-cut delay: median 27 rounds, 388 cuts in 78 readable games. Later recount: median 28 among 370 resolved cases, 458 cuts in 82 games—but an older bot. Current live feeding recovered after about 15 rounds, candidates after 10. Growth after cuts was 11.4 versus 11.1 without; the deficit was in windows containing cuts. Source: `redteam-2.md` §5, correcting `deep-read-5.md` §§1, 7.

The race summary says test4 never feeds a leader while its queen lives; its §2e instead records living-queen starts in 38% of 61 starts against us and 12% of 26 against top three. This supports a tendency, not “never.” Earlier feeding, remote collection and faster leader identification were not causally settled. Source: `deep-read-5.md` §§1, 2e.''')
# Remove duplicated replay examples while preserving the most illustrative tables.
for line in s.splitlines(True):
 if line.startswith('| [1052766]') or line.startswith('| [1060356]') or line.startswith('| [1053032]') or line.startswith('| [1067641]') and 'Forgot loops onto' in line:
  s=s.replace(line,'',1)
p.write_text(s);print(len(s))
