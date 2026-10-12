# CONV2 mechanism check (2026-10-01T06:49Z): 32 games from exp/v16/h-d, exp/v16/h-dsb; our turns and feeds from r250

| map | games | our turns | tags per 100 turns (ck / cp / cy / sq) | feeds by kind | declared K = our longest | median share of our declarations naming K | K shorter than the donor believed (and too short for the gate) | drops: to K / other own / enemy / none | median drop distance to K head | merges: n, median slack, drops to K | just-in-time merges: n, slack min-max, K longest, drops to K, median K eating delay | far pulls (d > 24): n, median change of d over 10 rounds | spread gate: dragons, median distance to our longest at the first gated turn, share >= 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Default/a | 8 | 26906 | 63.7 / 1.6 / 7.0 / 0.0 | cv2 31 | 61% | 20% | 0 (0) of 31 | 75% / 15% / 5% / 5% (55) | 3 | 1, 17, 75% | 0 | 0 | 0 |
| Devil/a | 8 | 8154 | 60.7 / 5.8 / 12.1 / 0.0 | cv2 19 | 74% | 50% | 3 (3) of 19 | 59% / 38% / 0% / 3% (29) | 3 | 1, 26, 0% | 0 | 0 | 0 |
| Queen Of Spades/a | 8 | 23046 | 41.1 / 1.4 / 5.5 / 0.0 | cv2 16 | 81% | 33% | 1 (0) of 16 | 82% / 9% / 9% / 0% (22) | 3 | 0, –, – | 0 | 0 | 0 |
| Schooltime/b | 8 | 27448 | 62.4 / 2.0 / 4.2 / 0.0 | cv2 20 | 70% | 17% | 2 (2) of 20 | 83% / 14% / 3% / 0% (36) | 3 | 1, 8, 89% | 1, 8-8, 100%, 89%, 15 | 33, 0 | 0 |
| all | 32 | 85554 | 56.9 / 2.1 / 6.2 / 0.0 | cv2 86 | 70% | 25% | 6 (5) of 86 | 75% / 18% / 4% / 3% (142) | 3 | 3, 17, 65% | 1, 8-8, 100%, 89%, 15 | 33, 0 | 0 |

## Feeds

| game | r | donor | L | kind | K (L; believed) | K longest | declared same K | drop distances to K | to K / own / enemy of drops | slack |
|---|---|---|---|---|---|---|---|---|---|---|
| proxy4_king:default:A:1 | 464 | #110 | 2 | cv2 | #126 (4; 4) | yes | 33% of 6 | 1 | 1 / 0 / 0 of 1 | 31 |
| proxy4_king:default:A:1 | 470 | #205 | 3 | cv2 | #126 (5; 5) | yes | 20% of 5 | 2,2 | 2 / 0 / 0 of 2 | 25 |
| proxy4_king:default:A:2 | 366 | #183 | 3 | cv2 | #149 (8; 8) | yes | 36% of 11 | 1,3 | 1 / 1 / 0 of 2 | 128 |
| proxy4_king:default:A:2 | 372 | #188 | 3 | cv2 | #149 (8; 8) | yes | 40% of 10 | 3,3 | 2 / 0 / 0 of 2 | 122 |
| proxy4_king:default:A:2 | 381 | #175 | 2 | cv2 | #149 (9; 5) | yes | 22% of 9 | 3 | 1 / 0 / 0 of 1 | 114 |
| proxy4_king:default:A:2 | 489 | #238 | 3 | cv2 | #244 (23; 16) | yes | 7% of 14 | 4,4 | 2 / 0 / 0 of 2 | 5 |
| proxy4_king:default:B:1 | 425 | #130 | 2 | cv2 | #167 (4; 4) | yes | 33% of 9 | 2 | 1 / 0 / 0 of 1 | 71 |
| proxy4_king:default:B:1 | 445 | #180 | 2 | cv2 | #167 (6; 6) | yes | 38% of 8 | 3 | 1 / 0 / 0 of 1 | 50 |
| proxy4_king:default:B:1 | 447 | #125 | 2 | cv2 | #170 (5; 5) | no | 0% of 7 | 5 | 1 / 0 / 0 of 1 | 49 |
| proxy4_king:default:B:1 | 474 | #170 | 8 | cv2 m | #167 (9; 9) | no | 29% of 7 | 1,3,3,12 | 3 / 0 / 0 of 4 | 17 |
| proxy4_king:default:B:1 | 484 | #148 | 3 | cv2 | #146 (9; 9) | no | 17% of 6 | 2,4 | 1 / 1 / 0 of 2 | 11 |
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
| proxy4_king:devil:B:1 | 355 | #140 | 2 | cv2 | #38 (2; 4) | yes | 67% of 3 | 3 | 1 / 0 / 0 of 1 | 140 |
| proxy4_king:devil:B:1 | 467 | #540 | 2 | cv2 | #529 (5; 5) | no | 38% of 8 | 2 | 0 / 1 / 0 of 1 | 29 |
| proxy4_king:devil:B:1 | 476 | #531 | 5 | cv2 | #530 (7; 7) | yes | 0% of 7 | 3,3,1 | 2 / 1 / 0 of 3 | 16 |
| proxy4_king:devil:B:2 | 451 | #492 | 2 | cv2 | #3 (4; 4) | no | 75% of 4 | 2 | 1 / 0 / 0 of 1 | 45 |
| proxy4_king:devil:B:2 | 456 | #506 | 4 | cv2 | #58 (6; 6) | yes | 0% of 3 | 3,5 | 0 / 1 / 0 of 2 | 37 |
| proxy4_king:queen_of_spades:A:1 | 494 | #151 | 2 | cv2 | #63 (11; 11) | yes | 25% of 4 | 2 | 1 / 0 / 0 of 1 | 2 |
| proxy4_king:queen_of_spades:A:2 | 407 | #155 | 2 | cv2 | #124 (16; 16) | yes | 33% of 6 | 3 | 1 / 0 / 0 of 1 | 88 |
| proxy4_king:queen_of_spades:A:2 | 439 | #149 | 2 | cv2 | #124 (20; 20) | yes | 40% of 5 | 1 | 1 / 0 / 0 of 1 | 58 |
| proxy4_king:queen_of_spades:A:2 | 439 | #164 | 2 | cv2 | #124 (20; 20) | yes | 40% of 5 | 3 | 1 / 0 / 0 of 1 | 56 |
| proxy4_king:queen_of_spades:A:2 | 450 | #148 | 2 | cv2 | #162 (4; 4) | no | 0% of 4 | 2 | 0 / 1 / 0 of 1 | 46 |
| proxy4_king:queen_of_spades:A:2 | 480 | #172 | 3 | cv2 | #124 (22; 22) | yes | 33% of 3 | 3,5 | 2 / 0 / 0 of 2 | 14 |
| proxy4_king:queen_of_spades:B:1 | 439 | #162 | 2 | cv2 | #139 (4; 4) | yes | 14% of 7 | 3 | 1 / 0 / 0 of 1 | 56 |
| proxy4_king:queen_of_spades:B:2 | 494 | #107 | 2 | cv2 | #177 (13; 12) | yes | 20% of 15 | 3 | 1 / 0 / 0 of 1 | 1 |
| proxy4_swarm:default:A:1 | 354 | #144 | 2 | cv2 | #127 (9; 9) | yes | 62% of 13 | 2 | 0 / 0 / 1 of 1 | 142 |
| proxy4_swarm:default:B:1 | 362 | #150 | 3 | cv2 | #160 (8; 8) | yes | 8% of 13 | 1,10 | 1 / 0 / 1 of 2 | 134 |
| proxy4_swarm:default:B:1 | 482 | #185 | 3 | cv2 | #119 (5; 5) | no | 50% of 8 | 2,2 | 0 / 2 / 0 of 2 | 13 |
| proxy4_swarm:default:A:2 | 474 | #239 | 4 | cv2 | #191 (8; 8) | yes | 4% of 28 | 3,1 | 2 / 0 / 0 of 2 | 19 |
| proxy4_swarm:devil:A:1 | 426 | #496 | 2 | cv2 | #2 (4; 4) | yes | 100% of 3 | 2 | 1 / 0 / 0 of 1 | 70 |
| proxy4_swarm:devil:A:1 | 427 | #492 | 2 | cv2 | #2 (4; 4) | yes | 100% of 2 | 2 | 1 / 0 / 0 of 1 | 69 |
| proxy4_swarm:default:B:2 | 447 | #225 | 3 | cv2 | #216 (5; 5) | no | 18% of 11 | 2,4 | 2 / 0 / 0 of 2 | 48 |
| proxy4_swarm:default:B:2 | 449 | #240 | 3 | cv2 | #216 (6; 6) | no | 10% of 10 | 3,5 | 2 / 0 / 0 of 2 | 45 |
| proxy4_swarm:default:B:2 | 451 | #200 | 2 | cv2 | #238 (4; 4) | no | 22% of 9 | 3 | 1 / 0 / 0 of 1 | 45 |
| proxy4_swarm:default:B:2 | 455 | #226 | 3 | cv2 | #238 (5; 5) | no | 13% of 8 | 4,6 | 0 / 2 / 0 of 2 | 39 |
| proxy4_swarm:default:B:2 | 460 | #238 | 5 | cv2 | #187 (8; 8) | no | 0% of 7 | 2,4,4 | 2 / 1 / 0 of 3 | 33 |
| proxy4_swarm:default:B:2 | 478 | #187 | 4 | cv2 | #255 (9; 9) | yes | 14% of 7 | 3,5 | 2 / 0 / 0 of 2 | 16 |
| proxy4_swarm:default:B:2 | 492 | #242 | 5 | cv2 | #255 (11; 11) | yes | 17% of 6 | 3,5,5 | 1 / 0 / 0 of 3 | 0 |
| proxy4_swarm:devil:A:2 | 439 | #503 | 2 | cv2 | #495 (4; 4) | yes | 50% of 2 | 3 | 1 / 0 / 0 of 1 | 56 |
| proxy4_swarm:devil:B:1 | 344 | #315 | 2 | cv2 | #103 (2; 4) | no | 0% of 8 | 3 | 0 / 1 / 0 of 1 | 151 |
| proxy4_swarm:devil:B:1 | 432 | #39 | 2 | cv2 | #5 (4; 4) | yes | 0% of 6 | 2 | 0 / 1 / 0 of 1 | 64 |
| proxy4_swarm:devil:B:2 | 402 | #451 | 2 | cv2 | #161 (4; 4) | no | 75% of 4 | 2 | 1 / 0 / 0 of 1 | 94 |
| proxy4_swarm:devil:B:2 | 452 | #455 | 4 | cv2 | #493 (12; 8) | yes | 17% of 6 | 2,4 | 1 / 1 / 0 of 2 | 42 |
| proxy4_swarm:devil:B:2 | 457 | #492 | 4 | cv2 | #37 (2; 7) | no | 0% of 6 | 3,5 | 2 / 0 / 0 of 2 | 36 |
| proxy4_swarm:devil:B:2 | 463 | #489 | 8 | cv2 m | #493 (14; 14) | yes | 100% of 5 | 3,5,7,5 | 0 / 4 / 0 of 4 | 26 |
| proxy4_swarm:devil:B:2 | 473 | #494 | 6 | cv2 | #493 (15; 15) | yes | 100% of 4 | 2,4,4 | 3 / 0 / 0 of 3 | 19 |
| proxy4_swarm:queen_of_spades:A:1 | 413 | #137 | 2 | cv2 | #142 (15; 18) | yes | 95% of 19 | 2 | 1 / 0 / 0 of 1 | 83 |
| proxy4_swarm:queen_of_spades:A:1 | 489 | #161 | 2 | cv2 | #75 (11; 11) | yes | 25% of 16 | 3 | 1 / 0 / 0 of 1 | 6 |
| proxy4_swarm:queen_of_spades:B:1 | 446 | #4 | 2 | cv2 | #88 (16; 16) | yes | 33% of 12 | 3 | 1 / 0 / 0 of 1 | 49 |
| proxy4_swarm:queen_of_spades:B:1 | 485 | #146 | 5 | cv2 | #88 (25; 25) | yes | 85% of 13 | 3,5,5 | 3 / 0 / 0 of 3 | 7 |
| proxy4_swarm:queen_of_spades:B:1 | 486 | #187 | 3 | cv2 | #88 (25; 25) | yes | 83% of 12 | 3,5 | 2 / 0 / 0 of 2 | 8 |
| proxy4_swarm:queen_of_spades:B:1 | 491 | #182 | 2 | cv2 | #195 (14; 6) | no | 27% of 11 | 2 | 0 / 1 / 0 of 1 | 5 |
| proxy4_swarm:queen_of_spades:B:2 | 459 | #12 | 4 | cv2 | #175 (6; 6) | no | 20% of 10 | 3,1 | 2 / 0 / 0 of 2 | 34 |
| proxy4_swarm:queen_of_spades:B:2 | 478 | #188 | 3 | cv2 | #175 (9; 6) | yes | 14% of 7 | 2,4 | 0 / 0 / 2 of 2 | 17 |
| proxy4_king:schooltime_b:A:1 | 364 | #95 | 3 | cv2 | #144 (14; 14) | yes | 16% of 25 | 2,4 | 2 / 0 / 0 of 2 | 131 |
| proxy4_king:schooltime_b:A:1 | 387 | #151 | 2 | cv2 | #144 (16; 16) | yes | 21% of 29 | 3 | 1 / 0 / 0 of 1 | 108 |
| proxy4_king:schooltime_b:A:1 | 396 | #153 | 3 | cv2 | #64 (12; 12) | no | 17% of 29 | 3,5 | 2 / 0 / 0 of 2 | 98 |
| proxy4_king:schooltime_b:A:1 | 414 | #138 | 2 | cv2 | #144 (18; 18) | yes | 6% of 31 | 3 | 1 / 0 / 0 of 1 | 81 |
| proxy4_king:schooltime_b:A:1 | 472 | #214 | 17 | cv2 m jit | #144 (21; 21) | yes | 10% of 29 | 3,5,7,9,11,11,11,11,9 | 8 / 1 / 0 of 9 | 8 |
| proxy4_king:schooltime_b:A:1 | 480 | #178 | 5 | cv2 | #144 (24; 24) | yes | 7% of 28 | 2,2,2 | 3 / 0 / 0 of 3 | 13 |
| proxy4_king:schooltime_b:B:1 | 436 | #186 | 2 | cv2 | #177 (2; 4) | no | 0% of 11 | 3 | 0 / 1 / 0 of 1 | 59 |
| proxy4_king:schooltime_b:B:1 | 452 | #173 | 2 | cv2 | #16 (4; 4) | no | 10% of 10 | 2 | 0 / 1 / 0 of 1 | 44 |
| proxy4_king:schooltime_b:B:2 | 452 | #160 | 3 | cv2 | #3 (5; 5) | no | 11% of 9 | 3,5 | 2 / 0 / 0 of 2 | 42 |
| proxy4_swarm:schooltime_b:A:2 | 358 | #12 | 2 | cv2 | #9 (2; 4) | no | 11% of 9 | 2 | 1 / 0 / 0 of 1 | 138 |
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
