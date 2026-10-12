# v1.6 conversion report (2026-10-01T06:00Z)

Sets: v16g = exp/v16/g-sh (8 games); v13 = exp/gen/id-v13-F-H?stronghold (8 games)

Paired keys: 8 (first set 8, second 8)

## Outcome and conversion (per game; paired keys only)

| map | set | N | wins | elim | final longest | king r300/350/400/450/500 | r300-499 king sac pearls | king natural r300+ | feeds/game | declared target = final line | r300+ sac drops: line/ally/enemy/none | king deaths non-sac / sac | heads r250/350/450 | mass r250/350/450 | other L>=8 mass r450 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| stronghold/? | v16g | 8 | 7 | 0 | 67.9 | 10.3 / 19.1 / 38.4 / 55.4 / 67.9 | 31.9 | 29.6 | 37.6 | 233/301 (77%) | 39% / 57% / 2% / 2% (646) | 1 / 0 | 26 / 18 / 3 | 89 / 72 / 63 | 4.3 |
| stronghold/? | v13 | 8 | 7 | 0 | 72.5 | 10.3 / 19.3 / 38.6 / 55.1 / 72.5 | 33.8 | 32.1 | 37.8 | 236/302 (78%) | 41% / 55% / 2% / 2% (651) | 1 / 0 | 26 / 17 / 3 | 89 / 71 / 65 | 3.9 |
| all | v16g | 8 | 7 | 0 | 67.9 | 10.3 / 19.1 / 38.4 / 55.4 / 67.9 | 31.9 | 29.6 | 37.6 | 233/301 (77%) | 39% / 57% / 2% / 2% (646) | 1 / 0 | 26 / 18 / 3 | 89 / 72 / 63 | 4.3 |
| all | v13 | 8 | 7 | 0 | 72.5 | 10.3 / 19.3 / 38.6 / 55.1 / 72.5 | 33.8 | 32.1 | 37.8 | 236/302 (78%) | 41% / 55% / 2% / 2% (651) | 1 / 0 | 26 / 17 / 3 | 89 / 71 / 65 | 3.9 |

## Paired differences (v16g − v13): mean, then + / 0 / − pairs and the two-sided sign test p

| map | pairs | r300-499 king sac pearls | final longest | king r400 | king r500 | wins | eliminations |
|---|---|---|---|---|---|---|---|
| stronghold/? | 8 | -1.9 (1/5/2, p 1.000) | -4.6 (0/5/3, p 0.250) | -0.3 (1/5/2, p 1.000) | -4.6 (0/5/3, p 0.250) | 7 vs 7 | 0 vs 0 |
| all | 8 | -1.9 (1/5/2, p 1.000) | -4.6 (0/5/3, p 0.250) | -0.3 (1/5/2, p 1.000) | -4.6 (0/5/3, p 0.250) | 7 vs 7 | 0 vs 0 |

## CONV2 mechanism (the tags of each set; r >= 250, our moves)

| map | set | feeds by kind | cv2 feeds: piece / mid / big (merge) | cv2 feeds r250-349 / 350-399 / 400-499 | cv2 on final line | feed drops eaten by the declared target / another of ours / all | sf labels on the row after r250 | ck turns: = longest / = final line / self | K switches after r400 (dragons) | cp turns | cy turns | sq turns | moves |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| stronghold/? | v16g | conv 179, feed 122 | 0 / 0 / 0 | 0 / 0 / 0 | 0/0 | 300 / 322 / 646 | 0 | 59% / 57% / 69 (245) | 0 (0) | 17 | 16 | 0 | 28397 |
| stronghold/? | v13 | conv 181, feed 121 | 0 / 0 / 0 | 0 / 0 / 0 | 0/0 | 317 / 309 / 651 | 0 | – / – / 0 (0) | 0 (0) | 0 | 0 | 0 | 28538 |
| all | v16g | conv 179, feed 122 | 0 / 0 / 0 | 0 / 0 / 0 | 0/0 | 300 / 322 / 646 | 0 | 59% / 57% / 69 (245) | 0 (0) | 17 | 16 | 0 | 28397 |
| all | v13 | conv 181, feed 121 | 0 / 0 / 0 | 0 / 0 / 0 | 0/0 | 317 / 309 / 651 | 0 | – / – / 0 (0) | 0 (0) | 0 | 0 | 0 | 28538 |

## Feeds by the recipient length the donor saw (r >= 250; all labelled feeds): N, on the final line, drops eaten by the declared target / all drops

| map | set | recipient < 8 | 8-15 | >= 16 |
|---|---|---|---|---|
| stronghold/? | v16g | 0: – line, 0/0 | 0: – line, 0/0 | 0: – line, 0/0 |
| stronghold/? | v13 | 0: – line, 0/0 | 0: – line, 0/0 | 0: – line, 0/0 |
| all | v16g | 0: – line, 0/0 | 0: – line, 0/0 | 0: – line, 0/0 |
| all | v13 | 0: – line, 0/0 | 0: – line, 0/0 | 0: – line, 0/0 |

Definitions: versions/v1.6/VERSION.md §3.2. "declared target = final line": labelled feeds (`feed #<id>`) from r250 whose id is the active final line at the death. "king deaths": deaths from r250 of our longest at that moment when it is >= 8 (the extractor's kingDeaths), non-sacrifice causes vs sacrifice. Replay checks (sim, splits, drops, lineage) summed over the games: [{"sim":0,"splits":0,"drops":0,"eatTC":0,"ledger":0,"final":0,"lineage":0,"natBal":0,"dropBal":0,"unknownDeath":0,"curve":0},{"sim":0,"splits":0,"drops":0,"eatTC":0,"ledger":0,"final":0,"lineage":0,"natBal":0,"dropBal":0,"unknownDeath":0,"curve":0}]
