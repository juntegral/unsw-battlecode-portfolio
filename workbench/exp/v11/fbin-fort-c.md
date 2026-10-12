# v1.1 spatial check: v1.1 vs v1

Paired games (same key in every set): 14. Sets: v1.1 = exp/v11/v11c-fort; v1 = exp/v11/v1-fort. Opponents: those of each set (local proxies: sanity only, not a filter).

## 1. Our head share by frontier bin (own-deep 0 .. enemy-deep 4), % of our heads at the round start; target = v1.1 FRONT_POLICY (elite winners)

| map / layout | r | target | v1.1 share (heads/game, N) | v1 share (heads/game, N) |
|---|---:|---|---|---|
| Autarky/a | 25 | – | 57·29·7·4·4 (7.0, 4) | 54·29·7·4·7 (7.0, 4) |
| Autarky/a | 50 | – | 41·38·14·7·0 (7.3, 4) | 38·45·10·7·0 (7.3, 4) |
| Autarky/a | 100 | – | 54·31·8·4·4 (6.5, 4) | 50·27·8·12·4 (6.5, 4) |
| Autarky/a | 250 | – | 48·52·0·0·0 (5.8, 4) | 41·50·5·5·0 (5.5, 4) |
| Portals/a | 25 | – | 100·0·0·0·0 (5.0, 4) | 100·0·0·0·0 (5.0, 4) |
| Portals/a | 50 | – | 100·0·0·0·0 (8.8, 4) | 100·0·0·0·0 (8.8, 4) |
| Portals/a | 100 | – | 100·0·0·0·0 (12.5, 4) | 100·0·0·0·0 (11.8, 4) |
| Portals/a | 250 | – | 100·0·0·0·0 (13.3, 4) | 100·0·0·0·0 (17.0, 4) |
| Prisoners Dilemma/10 | 25 | – | 25·50·25·0·0 (4.0, 2) | 25·50·25·0·0 (4.0, 2) |
| Prisoners Dilemma/10 | 50 | – | 30·40·30·0·0 (5.0, 2) | 30·40·30·0·0 (5.0, 2) |
| Prisoners Dilemma/10 | 100 | – | 0·63·38·0·0 (4.0, 2) | 0·63·38·0·0 (4.0, 2) |
| Prisoners Dilemma/10 | 250 | – | 0·44·44·11·0 (4.5, 2) | 0·71·29·0·0 (3.5, 2) |
| Prisoners Dilemma/a | 25 | – | 40·60·0·0·0 (5.0, 4) | 40·60·0·0·0 (5.0, 4) |
| Prisoners Dilemma/a | 50 | – | 50·38·13·0·0 (4.0, 4) | 50·38·13·0·0 (4.0, 4) |
| Prisoners Dilemma/a | 100 | – | 25·75·0·0·0 (4.0, 4) | 25·75·0·0·0 (4.0, 4) |
| Prisoners Dilemma/a | 250 | – | 42·58·0·0·0 (4.8, 4) | 44·50·6·0·0 (4.5, 4) |
| **all swarm** | 25 | – | 61·32·5·1·1 (5.4, 14) | 59·32·5·1·3 (5.4, 14) |
| **all swarm** | 50 | – | 64·23·10·2·0 (6.4, 14) | 63·26·9·2·0 (6.4, 14) |
| **all swarm** | 100 | – | 68·25·5·1·1 (7.1, 14) | 66·25·5·3·1 (6.9, 14) |
| **all swarm** | 250 | – | 69·26·4·1·0 (7.4, 14) | 74·22·3·1·0 (8.2, 14) |

## 2. Outcome, natural intake, deaths of ours (per game), king deaths (length >= 8, team longest at death), king exposure (r100-499)

| map / layout | set | games | wins | eliminated | final longest us / them | natural intake us / them | trap | rammed | ram | allyHead | enemyBody | sac | king deaths (cause) | king within 6 / 3 |
|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|
| Autarky/a | v1.1 | 4 | 4 | 0 | 64.0 / 27.8 | 344 / 282 (122%) | 250.5 | 2.8 | 0.0 | 0.0 | 0.0 | 7.3 | 0 | 15% / 0% (1600) |
| Autarky/a | v1 | 4 | 4 | 0 | 68.8 / 40.0 | 341 / 279 (122%) | 249.3 | 2.8 | 0.0 | 0.0 | 0.0 | 4.3 | 0 | 8% / 0% (1600) |
| Portals/a | v1.1 | 4 | 3 | 0 | 41.3 / 28.8 | 242 / 572 (42%) | 84.5 | 0.0 | 0.0 | 9.0 | 0.0 | 20.3 | trap 3, allyHead 2, sac 1 | 0% / 0% (1600) |
| Portals/a | v1 | 4 | 3 | 0 | 45.3 / 34.0 | 240 / 577 (42%) | 97.5 | 0.0 | 0.0 | 4.0 | 0.0 | 24.0 | trap 2, allyHead 1 | 0% / 0% (1600) |
| Prisoners Dilemma/10 | v1.1 | 2 | 0 | 0 | 13.0 / 23.5 | 171 / 219 (78%) | 166.5 | 4.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 86% / 9% (800) |
| Prisoners Dilemma/10 | v1 | 2 | 0 | 0 | 13.0 / 20.0 | 171 / 231 (74%) | 166.5 | 2.5 | 0.5 | 0.0 | 0.0 | 0.0 | 0 | 91% / 9% (800) |
| Prisoners Dilemma/a | v1.1 | 4 | 3 | 1 | 21.8 / 16.5 | 261 / 214 (122%) | 231.8 | 0.8 | 0.0 | 0.0 | 0.0 | 3.5 | 0 | 73% / 10% (1589) |
| Prisoners Dilemma/a | v1 | 4 | 2 | 2 | 15.0 / 15.0 | 260 / 211 (123%) | 229.5 | 0.8 | 0.0 | 0.0 | 0.0 | 3.3 | rammed 2 | 70% / 10% (1542) |
| **all swarm** | v1.1 | 14 | 10 | 1 | 38.1 / 24.2 | 266 / 336 (79%) | 185.7 | 1.6 | 0.0 | 2.6 | 0.0 | 8.9 | trap 3, allyHead 2, sac 1 | 37% / 4% (5589) |
| **all swarm** | v1 | 14 | 9 | 2 | 38.7 / 28.3 | 264 / 338 (78%) | 188.4 | 1.4 | 0.1 | 1.1 | 0.0 | 9.0 | trap 2, allyHead 1, rammed 2 | 35% / 4% (5542) |

## 3. v1.1 tags per game (sd turns; share of sd turns by target bin; contested; king floor turns / breaking the floor; beacon / relay)

| set | games | sd turns | target bin 0·1·2·3·4 (%) | contested (%) | sk turns | kf turns | kfx | kb | kbr |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| v1.1 | 14 | 0 | –·–·–·–·– | – | 0 | 0 | 0.0 | 56.2 | 131.1 |
| v1 | 14 | 0 | –·–·–·–·– | – | 0 | 0 | 0.0 | 0.0 | 0.0 |

## 4. Guard: sd turns whose top-deficit bin held no group we may take, so the head went to another bin (" fr<b><why>")

o = that bin has 2-core food in reach (owned by an ally, contested, vetoed or too poor); p = only pocket food in reach; n = no food of that bin in reach.

| map / layout | set | sd turns | redirected | o · p · n | top bins redirected from (0·1·2·3·4) |
|---|---|---:|---:|---|---|
