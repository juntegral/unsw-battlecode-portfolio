# CONV2 mechanism check (2026-10-01T08:56Z): 32 games from exp/v16/h0-d, exp/v16/h0-dsb; our turns and feeds from r250

| map | games | our turns | tags per 100 turns (ck / cp / cy / sq) | feeds by kind | declared K = our longest | median share of our declarations naming K | K shorter than the donor believed (and too short for the gate) | drops: to K / other own / enemy / none | median drop distance to K head | merges: n, median slack, drops to K | just-in-time merges: n, slack min-max, K longest, drops to K, median K eating delay | far pulls (d > 24): n, median change of d over 10 rounds | spread gate: dragons, median distance to our longest at the first gated turn, share >= 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Default/a | 8 | 27336 | 64.3 / 2.1 / 6.5 / 0.0 | cv2 31 | 58% | 29% | 1 (0) of 31 | 71% / 7% / 11% / 11% (55) | 3 | 0, –, – | 0 | 8, -4 | 0 |
| Devil/a | 8 | 7985 | 59.6 / 5.5 / 12.1 / 0.0 | cv2 22 | 77% | 57% | 0 (0) of 22 | 47% / 47% / 6% / 0% (34) | 3 | 1, 26, 0% | 0 | 0 | 0 |
| Queen Of Spades/a | 8 | 23106 | 41.2 / 1.9 / 5.0 / 0.0 | cv2 16 | 81% | 33% | 1 (0) of 16 | 76% / 10% / 10% / 5% (21) | 3 | 0, –, – | 0 | 0 | 0 |
| Schooltime/b | 8 | 27960 | 63.1 / 2.2 / 3.5 / 0.0 | cv2 20 | 65% | 24% | 0 (0) of 20 | 86% / 10% / 3% / 0% (29) | 3 | 0, –, – | 0 | 10, -5 | 0 |
| all | 32 | 86387 | 57.3 / 2.4 / 5.7 / 0.0 | cv2 89 | 69% | 33% | 2 (0) of 89 | 69% / 18% / 8% / 5% (139) | 3 | 1, 26, 0% | 0 | 18, -5 | 0 |

## Feeds

| game | r | donor | L | kind | K (L; believed) | K longest | declared same K | drop distances to K | to K / own / enemy of drops | slack |
|---|---|---|---|---|---|---|---|---|---|---|
| proxy4_king:default:A:1 | 469 | #110 | 5 | cv2 | #126 (12; 12) | yes | 33% of 3 | 2,4,4 | 3 / 0 / 0 of 3 | 24 |
| proxy4_king:default:A:2 | 369 | #188 | 3 | cv2 | #149 (9; 5) | yes | 40% of 10 | 2,13 | 2 / 0 / 0 of 2 | 126 |
| proxy4_king:default:A:2 | 376 | #183 | 3 | cv2 | #149 (11; 5) | yes | 33% of 9 | 3,3 | 2 / 0 / 0 of 2 | 118 |
| proxy4_king:default:A:2 | 415 | #225 | 2 | cv2 | #149 (13; 8) | yes | 37% of 19 | 3 | 1 / 0 / 0 of 1 | 80 |
| proxy4_king:default:B:1 | 474 | #125 | 3 | cv2 | #176 (8; 8) | no | 22% of 9 | 2,4 | 0 / 0 / 2 of 2 | 21 |
| proxy4_king:default:B:2 | 394 | #7 | 3 | cv2 | #11 (5; 5) | yes | 56% of 9 | 2,4 | 2 / 0 / 0 of 2 | 101 |
| proxy4_king:default:B:2 | 409 | #184 | 2 | cv2 | #11 (8; 8) | yes | 46% of 13 | 3 | 1 / 0 / 0 of 1 | 86 |
| proxy4_king:default:B:2 | 420 | #85 | 2 | cv2 | #11 (9; 9) | yes | 54% of 13 | 2 | 1 / 0 / 0 of 1 | 76 |
| proxy4_king:default:B:2 | 437 | #198 | 3 | cv2 | #11 (11; 11) | yes | 58% of 12 | 3,5 | 2 / 0 / 0 of 2 | 57 |
| proxy4_king:default:B:2 | 459 | #200 | 4 | cv2 | #11 (16; 16) | yes | 45% of 11 | 3,5 | 2 / 0 / 0 of 2 | 34 |
| proxy4_king:default:B:2 | 461 | #215 | 3 | cv2 | #187 (5; 5) | no | 0% of 10 | 3,1 | 1 / 1 / 0 of 2 | 33 |
| proxy4_king:default:B:2 | 470 | #11 | 2 | cv2 | #222 (16; 16) | yes | 11% of 9 | 2 | 0 / 0 / 1 of 1 | 26 |
| proxy4_king:default:B:2 | 491 | #178 | 2 | cv2 | #222 (13; 13) | no | 11% of 9 | 3 | 1 / 0 / 0 of 1 | 4 |
| proxy4_king:default:B:2 | 492 | #187 | 3 | cv2 | #62 (6; 6) | no | 13% of 8 | 2,4 | 2 / 0 / 0 of 2 | 3 |
| proxy4_king:devil:A:1 | 447 | #548 | 2 | cv2 | #81 (4; 4) | yes | 100% of 2 | 3 | 0 / 1 / 0 of 1 | 48 |
| proxy4_king:devil:A:2 | 360 | #48 | 2 | cv2 | #0 (4; 4) | yes | 100% of 2 | 3 | 1 / 0 / 0 of 1 | 135 |
| proxy4_king:devil:A:2 | 430 | #536 | 2 | cv2 | #470 (4; 4) | yes | 50% of 4 | 3 | 1 / 0 / 0 of 1 | 65 |
| proxy4_king:devil:A:2 | 431 | #521 | 2 | cv2 | #470 (4; 4) | yes | 33% of 3 | 2 | 1 / 0 / 0 of 1 | 65 |
| proxy4_king:devil:B:1 | 389 | #239 | 2 | cv2 | #118 (4; 4) | yes | 0% of 4 | 1 | 0 / 0 / 1 of 1 | 108 |
| proxy4_king:devil:B:1 | 391 | #140 | 2 | cv2 | #118 (4; 4) | yes | 0% of 3 | 2 | 0 / 0 / 1 of 1 | 105 |
| proxy4_king:devil:B:1 | 466 | #523 | 2 | cv2 | #38 (5; 5) | yes | 60% of 5 | 3 | 0 / 1 / 0 of 1 | 29 |
| proxy4_king:devil:B:1 | 484 | #537 | 5 | cv2 | #530 (8; 8) | yes | 33% of 3 | 1,3,5 | 3 / 0 / 0 of 3 | 10 |
| proxy4_king:devil:B:2 | 451 | #492 | 2 | cv2 | #3 (4; 4) | no | 75% of 4 | 2 | 1 / 0 / 0 of 1 | 45 |
| proxy4_king:devil:B:2 | 458 | #506 | 4 | cv2 | #58 (6; 6) | yes | 0% of 3 | 3,1 | 0 / 2 / 0 of 2 | 35 |
| proxy4_king:queen_of_spades:A:1 | 494 | #151 | 2 | cv2 | #63 (11; 11) | yes | 25% of 4 | 2 | 1 / 0 / 0 of 1 | 2 |
| proxy4_king:queen_of_spades:A:2 | 407 | #155 | 2 | cv2 | #124 (16; 16) | yes | 33% of 6 | 3 | 1 / 0 / 0 of 1 | 88 |
| proxy4_king:queen_of_spades:A:2 | 439 | #149 | 2 | cv2 | #124 (20; 20) | yes | 40% of 5 | 1 | 1 / 0 / 0 of 1 | 58 |
| proxy4_king:queen_of_spades:A:2 | 439 | #164 | 2 | cv2 | #124 (20; 20) | yes | 40% of 5 | 3 | 1 / 0 / 0 of 1 | 56 |
| proxy4_king:queen_of_spades:A:2 | 450 | #148 | 2 | cv2 | #162 (4; 4) | no | 0% of 4 | 2 | 0 / 1 / 0 of 1 | 46 |
| proxy4_king:queen_of_spades:A:2 | 480 | #172 | 3 | cv2 | #124 (22; 22) | yes | 33% of 3 | 3,5 | 2 / 0 / 0 of 2 | 14 |
| proxy4_king:queen_of_spades:B:1 | 439 | #162 | 2 | cv2 | #139 (4; 4) | yes | 14% of 7 | 3 | 1 / 0 / 0 of 1 | 56 |
| proxy4_king:queen_of_spades:B:2 | 495 | #192 | 2 | cv2 | #177 (13; 13) | yes | 20% of 15 | 2 | 1 / 0 / 0 of 1 | 1 |
| proxy4_swarm:default:A:1 | 354 | #144 | 2 | cv2 | #127 (9; 9) | yes | 62% of 13 | 2 | 0 / 0 / 1 of 1 | 142 |
| proxy4_swarm:default:A:2 | 453 | #59 | 4 | cv2 | #199 (9; 9) | yes | 61% of 31 | 3,3 | 0 / 0 / 1 of 2 | 40 |
| proxy4_swarm:default:A:2 | 464 | #183 | 2 | cv2 | #199 (7; 9) | yes | 74% of 31 | 2 | 1 / 0 / 0 of 1 | 32 |
| proxy4_swarm:default:A:2 | 485 | #217 | 5 | cv2 | #216 (8; 8) | no | 4% of 28 | 1,3,3 | 3 / 0 / 0 of 3 | 7 |
| proxy4_swarm:default:A:2 | 487 | #221 | 2 | cv2 | #199 (8; 8) | yes | 67% of 27 | 3 | 0 / 0 / 0 of 1 | 8 |
| proxy4_swarm:default:B:1 | 362 | #150 | 3 | cv2 | #160 (8; 8) | yes | 8% of 13 | 1,10 | 1 / 0 / 1 of 2 | 134 |
| proxy4_swarm:default:B:1 | 451 | #180 | 2 | cv2 | #140 (6; 5) | yes | 25% of 12 | 1 | 1 / 0 / 0 of 1 | 46 |
| proxy4_swarm:default:B:1 | 455 | #179 | 2 | cv2 | #119 (4; 4) | no | 33% of 9 | 2 | 1 / 0 / 0 of 1 | 41 |
| proxy4_swarm:default:B:1 | 486 | #199 | 3 | cv2 | #140 (8; 8) | no | 43% of 7 | 2,4 | 2 / 0 / 0 of 2 | 9 |
| proxy4_swarm:default:B:1 | 491 | #185 | 4 | cv2 | #140 (10; 6) | no | 29% of 7 | 2,4 | 0 / 0 / 0 of 2 | 3 |
| proxy4_swarm:default:B:2 | 447 | #225 | 3 | cv2 | #216 (5; 5) | no | 18% of 11 | 2,4 | 2 / 0 / 0 of 2 | 48 |
| proxy4_swarm:default:B:2 | 449 | #240 | 3 | cv2 | #216 (6; 6) | no | 10% of 10 | 3,5 | 2 / 0 / 0 of 2 | 45 |
| proxy4_swarm:default:B:2 | 451 | #200 | 2 | cv2 | #238 (4; 4) | no | 22% of 9 | 3 | 1 / 0 / 0 of 1 | 45 |
| proxy4_swarm:default:B:2 | 455 | #226 | 3 | cv2 | #238 (5; 5) | no | 13% of 8 | 4,6 | 0 / 2 / 0 of 2 | 39 |
| proxy4_swarm:default:B:2 | 460 | #238 | 5 | cv2 | #187 (8; 8) | no | 14% of 7 | 2,4,4 | 2 / 1 / 0 of 3 | 33 |
| proxy4_swarm:default:B:2 | 478 | #187 | 4 | cv2 | #255 (9; 9) | yes | 14% of 7 | 3,5 | 2 / 0 / 0 of 2 | 16 |
| proxy4_swarm:default:B:2 | 492 | #242 | 5 | cv2 | #255 (11; 11) | yes | 17% of 6 | 3,5,5 | 1 / 0 / 0 of 3 | 0 |
| proxy4_swarm:devil:A:1 | 426 | #496 | 2 | cv2 | #2 (4; 4) | yes | 100% of 3 | 2 | 1 / 0 / 0 of 1 | 70 |
| proxy4_swarm:devil:A:1 | 427 | #492 | 2 | cv2 | #2 (4; 4) | yes | 100% of 2 | 2 | 1 / 0 / 0 of 1 | 69 |
| proxy4_swarm:devil:A:2 | 439 | #503 | 2 | cv2 | #495 (4; 4) | yes | 50% of 2 | 3 | 1 / 0 / 0 of 1 | 56 |
| proxy4_swarm:devil:B:1 | 433 | #357 | 2 | cv2 | #537 (4; 4) | no | 0% of 7 | 3 | 0 / 1 / 0 of 1 | 62 |
| proxy4_swarm:devil:B:1 | 440 | #5 | 2 | cv2 | #265 (4; 4) | no | 29% of 7 | 3 | 1 / 0 / 0 of 1 | 55 |
| proxy4_swarm:devil:B:1 | 472 | #546 | 3 | cv2 | #265 (5; 5) | yes | 57% of 7 | 1,3 | 0 / 2 / 0 of 2 | 24 |
| proxy4_swarm:devil:B:1 | 484 | #565 | 2 | cv2 | #579 (4; 4) | no | 0% of 6 | 3 | 0 / 1 / 0 of 1 | 11 |
| proxy4_swarm:devil:B:1 | 489 | #562 | 6 | cv2 | #265 (8; 8) | yes | 100% of 5 | 2,4,6 | 0 / 3 / 0 of 3 | 3 |
| proxy4_swarm:devil:B:2 | 402 | #451 | 2 | cv2 | #161 (4; 4) | no | 75% of 4 | 2 | 1 / 0 / 0 of 1 | 94 |
| proxy4_swarm:devil:B:2 | 452 | #455 | 4 | cv2 | #493 (12; 8) | yes | 17% of 6 | 2,4 | 1 / 1 / 0 of 2 | 42 |
| proxy4_swarm:devil:B:2 | 463 | #489 | 8 | cv2 m | #493 (14; 14) | yes | 100% of 6 | 3,5,7,5 | 0 / 4 / 0 of 4 | 26 |
| proxy4_swarm:devil:B:2 | 473 | #494 | 6 | cv2 | #493 (15; 15) | yes | 100% of 5 | 2,4,4 | 3 / 0 / 0 of 3 | 19 |
| proxy4_swarm:queen_of_spades:A:1 | 413 | #137 | 2 | cv2 | #142 (15; 18) | yes | 95% of 19 | 2 | 1 / 0 / 0 of 1 | 83 |
| proxy4_swarm:queen_of_spades:B:1 | 446 | #4 | 2 | cv2 | #88 (16; 16) | yes | 33% of 12 | 3 | 1 / 0 / 0 of 1 | 49 |
| proxy4_swarm:queen_of_spades:B:2 | 437 | #146 | 3 | cv2 | #169 (16; 16) | yes | 67% of 12 | 2,2 | 0 / 0 / 2 of 2 | 58 |
| proxy4_swarm:queen_of_spades:B:2 | 443 | #168 | 3 | cv2 | #169 (17; 17) | yes | 60% of 10 | 2,4 | 2 / 0 / 0 of 2 | 52 |
| proxy4_swarm:queen_of_spades:B:2 | 459 | #16 | 3 | cv2 | #169 (20; 20) | yes | 70% of 10 | 3,3 | 1 / 1 / 0 of 2 | 35 |
| proxy4_swarm:queen_of_spades:B:2 | 477 | #143 | 2 | cv2 | #149 (5; 5) | no | 11% of 9 | 3 | 1 / 0 / 0 of 1 | 18 |
| proxy4_swarm:queen_of_spades:B:2 | 483 | #188 | 2 | cv2 | #1 (8; 8) | no | 14% of 7 | 2 | 1 / 0 / 0 of 1 | 13 |
| proxy4_swarm:queen_of_spades:B:2 | 492 | #192 | 3 | cv2 | #169 (23; 23) | yes | 67% of 6 | 3,5 | 1 / 0 / 0 of 2 | 2 |
| proxy4_king:schooltime_b:A:1 | 364 | #95 | 3 | cv2 | #144 (14; 14) | yes | 16% of 25 | 2,4 | 2 / 0 / 0 of 2 | 131 |
| proxy4_king:schooltime_b:A:1 | 387 | #151 | 2 | cv2 | #144 (16; 16) | yes | 21% of 29 | 3 | 1 / 0 / 0 of 1 | 108 |
| proxy4_king:schooltime_b:A:1 | 396 | #153 | 3 | cv2 | #64 (12; 12) | no | 17% of 29 | 3,5 | 2 / 0 / 0 of 2 | 98 |
| proxy4_king:schooltime_b:A:1 | 414 | #138 | 2 | cv2 | #144 (18; 18) | yes | 6% of 33 | 3 | 1 / 0 / 0 of 1 | 81 |
| proxy4_king:schooltime_b:B:1 | 438 | #177 | 2 | cv2 | #34 (4; 4) | no | 10% of 10 | 3 | 1 / 0 / 0 of 1 | 57 |
| proxy4_king:schooltime_b:B:1 | 490 | #34 | 5 | cv2 | #186 (11; 11) | no | 13% of 8 | 2,4,4 | 3 / 0 / 0 of 3 | 3 |
| proxy4_king:schooltime_b:B:2 | 452 | #185 | 2 | cv2 | #3 (5; 5) | no | 20% of 10 | 3 | 1 / 0 / 0 of 1 | 43 |
| proxy4_king:schooltime_b:B:2 | 473 | #57 | 3 | cv2 | #3 (8; 5) | no | 33% of 9 | 2,4 | 2 / 0 / 0 of 2 | 22 |
| proxy4_king:schooltime_b:B:2 | 488 | #33 | 3 | cv2 | #3 (10; 10) | no | 25% of 8 | 3,5 | 1 / 1 / 0 of 2 | 6 |
| proxy4_king:schooltime_b:B:2 | 493 | #115 | 2 | cv2 | #189 (37; 11) | yes | 71% of 7 | 2 | 1 / 0 / 0 of 1 | 3 |
| proxy4_swarm:schooltime_b:B:1 | 424 | #83 | 2 | cv2 | #148 (4; 4) | yes | 22% of 9 | 2 | 1 / 0 / 0 of 1 | 72 |
| proxy4_swarm:schooltime_b:B:1 | 444 | #80 | 2 | cv2 | #148 (5; 5) | no | 38% of 8 | 2 | 1 / 0 / 0 of 1 | 52 |
| proxy4_swarm:schooltime_b:B:1 | 458 | #134 | 2 | cv2 | #148 (8; 8) | yes | 57% of 7 | 3 | 1 / 0 / 0 of 1 | 37 |
| proxy4_swarm:schooltime_b:B:1 | 468 | #188 | 2 | cv2 | #148 (8; 8) | yes | 50% of 6 | 3 | 0 / 0 / 1 of 1 | 27 |
| proxy4_swarm:schooltime_b:B:1 | 471 | #187 | 4 | cv2 | #148 (7; 7) | yes | 40% of 5 | 2,4 | 2 / 0 / 0 of 2 | 23 |
| proxy4_swarm:schooltime_b:B:2 | 375 | #19 | 3 | cv2 | #135 (25; 23) | yes | 28% of 18 | 3,5 | 0 / 2 / 0 of 2 | 119 |
| proxy4_swarm:schooltime_b:B:2 | 376 | #154 | 4 | cv2 | #135 (25; 25) | yes | 24% of 17 | 3,5 | 2 / 0 / 0 of 2 | 117 |
| proxy4_swarm:schooltime_b:B:2 | 391 | #164 | 2 | cv2 | #135 (26; 26) | yes | 25% of 16 | 2 | 1 / 0 / 0 of 1 | 105 |
| proxy4_swarm:schooltime_b:B:2 | 428 | #169 | 2 | cv2 | #135 (31; 31) | yes | 17% of 18 | 2 | 1 / 0 / 0 of 1 | 68 |
| proxy4_swarm:schooltime_b:B:2 | 433 | #177 | 2 | cv2 | #135 (32; 31) | yes | 6% of 17 | 2 | 1 / 0 / 0 of 1 | 63 |
