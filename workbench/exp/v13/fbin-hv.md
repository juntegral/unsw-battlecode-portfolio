# v1.1 spatial check: v1.3-HV vs v1.2

Paired games (same key in every set): 24. Sets: v1.3-HV = exp/v13/hv-a, exp/v13/hv-b; v1.2 = exp/v11/v11bc-a-px4, exp/v11/v11bc-b-px4, exp/v13/base-a, exp/v13/base-b. Opponents: those of each set (local proxies: sanity only, not a filter).

## 1. Our head share by frontier bin (own-deep 0 .. enemy-deep 4), % of our heads at the round start; target = v1.1 FRONT_POLICY (elite winners)

| map / layout | r | target | v1.3-HV share (heads/game, N) | v1.2 share (heads/game, N) |
|---|---:|---|---|---|
| Slithery Fight/a | 25 | 55·26·18·1·1 | 75·15·9·1·0 (23.5, 8) | 66·21·12·1·1 (20.0, 8) |
| Slithery Fight/a | 50 | 49·29·20·2·1 | 68·23·9·0·0 (36.9, 8) | 67·27·6·0·0 (29.9, 8) |
| Slithery Fight/a | 100 | 51·26·20·2·1 | 73·21·6·0·0 (47.6, 8) | 65·20·15·0·0 (40.3, 8) |
| Slithery Fight/a | 250 | 51·23·21·3·1 | 81·15·4·0·0 (36.5, 8) | 77·17·6·0·0 (27.3, 8) |
| Slithery Fight/b | 25 | 55·26·18·1·1 | 72·19·8·1·0 (25.5, 8) | 59·24·17·0·0 (17.9, 8) |
| Slithery Fight/b | 50 | 48·28·21·2·1 | 66·22·12·0·0 (35.8, 8) | 60·26·14·0·0 (26.3, 8) |
| Slithery Fight/b | 100 | 52·26·19·2·1 | 87·11·2·0·0 (36.4, 8) | 69·21·10·0·0 (26.6, 8) |
| Slithery Fight/b | 250 | 56·23·17·3·1 | 75·23·2·0·0 (34.4, 8) | 58·33·9·0·0 (30.0, 8) |
| Trauma/a | 25 | 95·5·0·0·0 | 100·0·0·0·0 (4.0, 8) | 100·0·0·0·0 (4.0, 8) |
| Trauma/a | 50 | 75·25·1·0·0 | 100·0·0·0·0 (4.4, 8) | 100·0·0·0·0 (4.8, 8) |
| Trauma/a | 100 | 54·22·24·0·0 | 98·2·0·0·0 (7.5, 8) | 94·6·0·0·0 (6.3, 8) |
| Trauma/a | 250 | 41·22·32·4·1 | 64·28·8·0·0 (12.0, 8) | 60·35·5·0·0 (9.4, 8) |
| **all swarm** | 25 | – | 75·16·8·1·0 (17.7, 24) | 66·20·13·0·0 (14.0, 24) |
| **all swarm** | 50 | – | 69·21·10·0·0 (25.7, 24) | 67·24·9·0·0 (20.3, 24) |
| **all swarm** | 100 | – | 81·15·4·0·0 (30.5, 24) | 69·19·12·0·0 (24.4, 24) |
| **all swarm** | 250 | – | 76·20·4·0·0 (27.6, 24) | 66·27·7·0·0 (22.2, 24) |

## 2. Outcome, natural intake, deaths of ours (per game), king deaths (length >= 8, team longest at death), king exposure (r100-499)

| map / layout | set | games | wins | eliminated | final longest us / them | natural intake us / them | trap | rammed | ram | allyHead | enemyBody | sac | king deaths (cause) | king within 6 / 3 |
|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|
| Slithery Fight/a | v1.3-HV | 8 | 2 | 0 | 32.3 / 38.3 | 420 / 1696 (25%) | 196.3 | 24.4 | 7.8 | 2.3 | 0.0 | 34.6 | trap 3, rammed 4, allyHead 2 | 21% / 4% (3200) |
| Slithery Fight/a | v1.2 | 8 | 1 | 0 | 26.8 / 38.0 | 216 / 1671 (13%) | 47.1 | 18.4 | 5.4 | 1.5 | 0.0 | 26.0 | trap 6, rammed 2, ram 1 | 22% / 3% (3200) |
| Slithery Fight/b | v1.3-HV | 8 | 1 | 0 | 27.4 / 34.6 | 360 / 1482 (24%) | 155.3 | 21.6 | 5.5 | 3.5 | 0.0 | 32.1 | trap 4, rammed 4 | 34% / 3% (3200) |
| Slithery Fight/b | v1.2 | 8 | 0 | 0 | 18.0 / 40.4 | 189 / 1446 (13%) | 31.6 | 20.1 | 5.4 | 1.8 | 0.0 | 19.4 | rammed 6, allyHead 3, trap 3 | 38% / 6% (3200) |
| Trauma/a | v1.3-HV | 8 | 0 | 0 | 17.4 / 24.0 | 100 / 369 (27%) | 29.5 | 5.3 | 3.4 | 4.5 | 0.0 | 6.9 | allyHead 1 | 2% / 1% (3200) |
| Trauma/a | v1.2 | 8 | 0 | 0 | 13.1 / 22.0 | 77 / 353 (22%) | 18.8 | 5.9 | 3.3 | 0.5 | 0.0 | 5.5 | trap 1 | 5% / 1% (3200) |
| **all swarm** | v1.3-HV | 24 | 3 | 0 | 25.7 / 32.3 | 293 / 1182 (25%) | 127.0 | 17.1 | 5.5 | 3.4 | 0.0 | 24.5 | trap 7, rammed 8, allyHead 3 | 19% / 3% (9600) |
| **all swarm** | v1.2 | 24 | 1 | 0 | 19.3 / 33.5 | 161 / 1157 (14%) | 32.5 | 14.8 | 4.7 | 1.3 | 0.0 | 17.0 | trap 10, rammed 8, allyHead 3, ram 1 | 22% / 3% (9600) |

## 3. v1.1 tags per game (sd turns; share of sd turns by target bin; contested; king floor turns / breaking the floor; beacon / relay)

| set | games | sd turns | target bin 0·1·2·3·4 (%) | contested (%) | sk turns | kf turns | kfx | kb | kbr |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| v1.3-HV | 24 | 2545 | 43·33·18·3·3 | 9 | 505 | 59 | 17.1 | 0.7 | 0.0 |
| v1.2 | 24 | 3238 | 41·34·20·3·3 | 9 | 574 | 89 | 27.6 | 0.7 | 0.0 |

## 4. Guard: sd turns whose top-deficit bin held no group we may take, so the head went to another bin (" fr<b><why>")

o = that bin has 2-core food in reach (owned by an ally, contested, vetoed or too poor); p = only pocket food in reach; n = no food of that bin in reach.

Redirected = the turn has an sd target in another bin; no group = the dragon could take no group at all (it follows the pearl field).

| map / layout | set | sd turns | redirected (% of sd turns) | o · p · n | top bins redirected from (0·1·2·3·4) | no group at all: o · p · n |
|---|---|---:|---:|---|---|---|
| Slithery Fight/a | v1.3-HV | 25115 | 16693 (66%) | 14254 · 206 · 2233 | 2041 · 4071 · 10574 · 7 · 0 | 33408 · 301 · 2566 |
| Slithery Fight/a | v1.2 | 28617 | 20495 (72%) | 15721 · 967 · 3807 | 3948 · 3416 · 13129 · 2 · 0 | 35019 · 508 · 4475 |
| Slithery Fight/b | v1.3-HV | 28466 | 19695 (69%) | 17643 · 265 · 1787 | 2317 · 7855 · 9519 · 4 · 0 | 29803 · 137 · 1575 |
| Slithery Fight/b | v1.2 | 39913 | 28789 (72%) | 23068 · 867 · 4854 | 7547 · 5614 · 15620 · 8 · 0 | 27765 · 928 · 4714 |
| Trauma/a | v1.3-HV | 7501 | 5754 (77%) | 1872 · 174 · 3708 | 1089 · 1646 · 3019 · 0 · 0 | 7969 · 987 · 8693 |
| Trauma/a | v1.2 | 9179 | 6563 (72%) | 2214 · 519 · 3830 | 1805 · 1553 · 3205 · 0 · 0 | 6247 · 1071 · 9017 |
