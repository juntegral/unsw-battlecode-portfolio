# CONV2 mechanism check (2026-10-01T10:15Z): 36 games from exp/v16/h2F-gen; our turns and feeds from r400

| map | games | our turns | tags per 100 turns (ck / cp / cy / sq / sg) | feeds by kind | declared K = our longest | median share of our declarations naming K | K shorter than the donor believed (and too short for the gate) | drops: to K / other own / enemy / none | median drop distance to K head | merges: n, median slack, drops to K | just-in-time merges: n, slack min-max, K longest, drops to K, median K eating delay | far pulls (d > 24): n, median change of d over 10 rounds | spread gate: dragons, median distance to our longest at the first gated turn, share >= 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gen_L_01/? | 4 | 5053 | 11.8 / 0.3 / 0.5 / 0.0 / 11.8 | feed 27 | 33% | 0% | 0 (0) of 27 | 28% / 26% / 28% / 19% (47) | 5 | 0, –, – | 0 | 0 | 10, 23, 40% |
| gen_L_02/? | 4 | 0 | 0.0 / 0.0 / 0.0 / 0.0 / 0.0 | – | – | –% | 0 (0) of 0 | – / – / – / – (0) | – | 0, –, – | 0 | 0 | 0 |
| gen_L_03/? | 4 | 7003 | 28.5 / 5.0 / 1.4 / 0.0 / 28.5 | feed 26, conv 3, cv2 3 | 44% | 0% | 0 (0) of 32 | 65% / 26% / 6% / 3% (62) | 4 | 0, –, – | 0 | 15, -7 | 28, 30, 71% |
| gen_L_04/? | 4 | 9048 | 50.8 / 19.1 / 3.5 / 0.0 / 50.8 | feed 71, conv 9, cv2 12 | 41% | 0% | 0 (0) of 92 | 35% / 43% / 15% / 7% (331) | 5 | 5, 19, 23% | 3, 14-19, 100%, 28%, 6 | 344, -4 | 80, 29, 79% |
| gen_L_05/? | 4 | 11504 | 61.1 / 9.5 / 3.0 / 0.0 / 61.1 | conv 17, feed 53, cv2 20 | 27% | 0% | 0 (0) of 90 | 35% / 31% / 27% / 7% (320) | 5 | 11, 20, 27% | 2, 7-20, 0%, 7%, 2 | 79, -7 | 125, 29, 76% |
| gen_L_06/? | 4 | 12703 | 46.6 / 6.0 / 2.8 / 0.0 / 46.6 | feed 87, conv 27, cv2 22 | 14% | 0% | 0 (0) of 136 | 43% / 33% / 12% / 12% (602) | 5 | 10, 38, 52% | 1, 10-10, 0%, 10%, 5 | 18, -9 | 148, 26, 61% |
| gen_M_06/? | 4 | 482 | 0.0 / 0.0 / 0.0 / 0.0 / 0.0 | – | – | –% | 0 (0) of 0 | – / – / – / – (0) | – | 0, –, – | 0 | 0 | 0 |
| gen_R_01/? | 4 | 0 | 0.0 / 0.0 / 0.0 / 0.0 / 0.0 | – | – | –% | 0 (0) of 0 | – / – / – / – (0) | – | 0, –, – | 0 | 0 | 0 |
| gen_R_02/? | 4 | 143 | 0.0 / 0.0 / 0.0 / 0.0 / 0.0 | – | – | –% | 0 (0) of 0 | – / – / – / – (0) | – | 0, –, – | 0 | 0 | 0 |
| all | 36 | 45936 | 43.9 / 8.6 / 2.5 / 0.0 / 43.9 | feed 264, conv 56, cv2 57 | 28% | 0% | 0 (0) of 377 | 40% / 34% / 16% / 9% (1362) | 5 | 26, 20, 35% | 6, 7-20, 50%, 19%, 5 | 456, -5 | 391, 28, 70% |

## Feeds

| game | r | donor | L | kind | K (L; believed) | K longest | declared same K | drop distances to K | to K / own / enemy of drops | slack | K eats within L + 5 rounds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| proxy4_king:gen_L_01:A:1 | 451 | #48 | 4 | feed | #22 (5; –) | no | 0% of 1 | 4,6 | 1 / 1 / 0 of 2 | 41 | 1 of 2 |
| proxy4_king:gen_L_01:A:1 | 464 | #22 | 6 | feed | #2 (7; –) | no | 0% of 4 | 5,7,9 | 0 / 3 / 0 of 3 | 25 | 0 of 3 |
| proxy4_king:gen_L_01:A:1 | 471 | #12 | 4 | feed | #9 (5; –) | no | 0% of 5 | 3,3 | 2 / 0 / 0 of 2 | 22 | 2 of 2 |
| proxy4_king:gen_L_01:A:1 | 485 | #43 | 3 | feed | #2 (7; –) | no | 17% of 6 | 5,7 | 0 / 0 / 1 of 2 | 7 | 0 of 2 |
| proxy4_king:gen_L_01:A:1 | 486 | #9 | 7 | feed | #0 (8; –) | yes | 83% of 6 | 5,3,5,7 | 1 / 0 / 0 of 4 | 2 | 1 of 4 |
| proxy4_king:gen_L_01:A:1 | 488 | #38 | 2 | feed | #37 (3; –) | no | 0% of 6 | 4 | 0 / 0 / 1 of 1 | 6 | 0 of 1 |
| proxy4_king:gen_L_01:A:1 | 491 | #23 | 5 | feed | #0 (10; –) | yes | 83% of 6 | 4,6,8 | 0 / 0 / 0 of 3 | 0 | 0 of 3 |
| proxy4_king:gen_L_01:B:1 | 444 | #38 | 4 | feed | #11 (6; –) | yes | – | 3,5 | 2 / 0 / 0 of 2 | 49 | 1 of 2 |
| proxy4_king:gen_L_01:B:1 | 464 | #28 | 7 | feed | #11 (8; –) | yes | – | 5,7,7,9 | 0 / 4 / 0 of 4 | 24 | 0 of 4 |
| proxy4_king:gen_L_01:B:1 | 471 | #21 | 4 | feed | #11 (9; –) | yes | – | 5,7 | 2 / 0 / 0 of 2 | 20 | 2 of 2 |
| proxy4_king:gen_L_01:B:1 | 489 | #5 | 9 | feed | #11 (11; –) | yes | – | 4,6,8,8,10 | 3 / 0 / 0 of 5 | -2 | 3 of 5 |
| proxy4_king:gen_L_03:A:1 | 419 | #15 | 4 | feed | #22 (6; –) | no | – | 5,7 | 1 / 1 / 0 of 2 | 72 | 1 of 2 |
| proxy4_king:gen_L_03:A:1 | 431 | #0 | 4 | feed | #22 (7; –) | no | – | 3,3 | 1 / 1 / 0 of 2 | 62 | 1 of 2 |
| proxy4_king:gen_L_03:A:1 | 433 | #7 | 4 | feed | #2 (5; –) | no | – | 2,2 | 2 / 0 / 0 of 2 | 61 | 2 of 2 |
| proxy4_king:gen_L_03:A:1 | 436 | #9 | 3 | conv | #22 (8; –) | yes | – | 3,5 | 2 / 0 / 0 of 2 | 58 | 1 of 2 |
| proxy4_king:gen_L_03:A:1 | 437 | #5 | 3 | conv | #22 (8; –) | yes | – | 3,5 | 0 / 2 / 0 of 2 | 57 | 0 of 2 |
| proxy4_king:gen_L_03:A:1 | 441 | #2 | 8 | feed | #22 (9; –) | yes | – | 3,3,5,5 | 1 / 3 / 0 of 4 | 48 | 0 of 4 |
| proxy4_king:gen_L_03:A:1 | 442 | #30 | 4 | feed | #22 (9; –) | yes | – | 3,1 | 2 / 0 / 0 of 2 | 51 | 2 of 2 |
| proxy4_king:gen_L_03:A:1 | 446 | #32 | 4 | feed | #40 (5; –) | no | – | 3,3 | 2 / 0 / 0 of 2 | 47 | 2 of 2 |
| proxy4_king:gen_L_03:A:1 | 458 | #40 | 8 | feed | #22 (13; –) | yes | – | 4,6,4,4 | 4 / 0 / 0 of 4 | 30 | 4 of 4 |
| proxy4_king:gen_L_03:B:1 | 424 | #18 | 6 | feed | #12 (7; –) | yes | 9% of 11 | 3,1,3 | 2 / 1 / 0 of 3 | 67 | 2 of 3 |
| proxy4_king:gen_L_03:B:1 | 444 | #9 | 6 | feed | #46 (7; –) | no | 0% of 15 | 3,5,3 | 2 / 1 / 0 of 3 | 47 | 2 of 3 |
| proxy4_king:gen_L_03:B:1 | 452 | #39 | 6 | feed | #12 (9; –) | yes | 80% of 15 | 3,5,7 | 1 / 2 / 0 of 3 | 39 | 1 of 3 |
| proxy4_king:gen_L_03:B:1 | 454 | #43 | 3 | cv2 | #12 (9; 9) | yes | 50% of 14 | 2,4 | 2 / 0 / 0 of 2 | 41 | 2 of 2 |
| proxy4_king:gen_L_03:B:1 | 456 | #61 | 2 | conv | #12 (11; –) | yes | 50% of 14 | 3 | 1 / 0 / 0 of 1 | 39 | 0 of 1 |
| proxy4_king:gen_L_03:B:1 | 459 | #11 | 5 | cv2 | #12 (12; 12) | yes | 64% of 14 | 3,1,3 | 3 / 0 / 0 of 3 | 33 | 3 of 3 |
| proxy4_king:gen_L_03:B:1 | 464 | #41 | 4 | feed | #12 (15; –) | yes | 71% of 14 | 4,6 | 2 / 0 / 0 of 2 | 28 | 2 of 2 |
| proxy4_king:gen_L_03:B:1 | 473 | #27 | 2 | cv2 | #12 (18; 18) | yes | 93% of 14 | 2 | 1 / 0 / 0 of 1 | 23 | 1 of 1 |
| proxy4_king:gen_L_03:B:1 | 478 | #1 | 6 | feed | #23 (8; –) | no | 0% of 14 | 5,7,5 | 0 / 3 / 0 of 3 | 11 | 0 of 3 |
| proxy4_king:gen_L_03:B:1 | 478 | #23 | 8 | feed | #12 (19; –) | yes | 93% of 14 | 4,4,6,6 | 3 / 1 / 0 of 4 | 10 | 3 of 4 |
| proxy4_king:gen_L_04:A:1 | 401 | #234 | 6 | feed | #91 (29; –) | yes | – | 5,7,5 | 0 / 3 / 0 of 3 | 88 | 0 of 3 |
| proxy4_king:gen_L_04:A:1 | 404 | #321 | 4 | feed | #91 (29; –) | yes | 100% of 1 | 3,3 | 1 / 1 / 0 of 2 | 89 | 1 of 2 |
| proxy4_king:gen_L_04:A:1 | 407 | #274 | 5 | feed | #91 (31; –) | yes | 100% of 1 | 3,5,5 | 2 / 1 / 0 of 3 | 85 | 2 of 3 |
| proxy4_king:gen_L_04:A:1 | 408 | #159 | 5 | feed | #91 (31; –) | yes | 100% of 1 | 4,4,4 | 1 / 2 / 0 of 3 | 83 | 0 of 3 |
| proxy4_king:gen_L_04:A:1 | 409 | #194 | 6 | feed | #91 (31; –) | yes | 100% of 1 | 4,6,8 | 1 / 1 / 1 of 3 | 81 | 1 of 3 |
| proxy4_king:gen_L_04:A:1 | 410 | #301 | 3 | conv | #323 (8; –) | no | 0% of 1 | 2,2 | 0 / 2 / 0 of 2 | 85 | 0 of 2 |
| proxy4_king:gen_L_04:A:1 | 410 | #354 | 4 | feed | #91 (32; –) | yes | 100% of 1 | 3,3 | 0 / 2 / 0 of 2 | 81 | 0 of 2 |
| proxy4_king:gen_L_04:A:1 | 414 | #150 | 7 | feed | #91 (32; –) | yes | 100% of 1 | 2,2,4,6 | 2 / 2 / 0 of 4 | 77 | 2 of 4 |
| proxy4_king:gen_L_04:A:1 | 417 | #323 | 9 | feed | #91 (34; –) | yes | 100% of 2 | 4,6,6,6,8 | 0 / 5 / 0 of 5 | 70 | 0 of 5 |
| proxy4_king:gen_L_04:A:1 | 417 | #349 | 4 | feed | #91 (34; –) | yes | 100% of 2 | 5,7 | 0 / 2 / 0 of 2 | 74 | 0 of 2 |
| proxy4_king:gen_L_04:A:1 | 419 | #363 | 4 | feed | #91 (35; –) | yes | 100% of 2 | 2,4 | 1 / 1 / 0 of 2 | 75 | 1 of 2 |
| proxy4_king:gen_L_04:A:1 | 422 | #227 | 7 | feed | #91 (36; –) | yes | 100% of 5 | 3,5,7,9 | 2 / 2 / 0 of 4 | 68 | 1 of 4 |
| proxy4_king:gen_L_04:A:1 | 423 | #231 | 7 | feed | #91 (37; –) | yes | 100% of 7 | 3,5,5,7 | 0 / 4 / 0 of 4 | 67 | 0 of 4 |
| proxy4_king:gen_L_04:A:1 | 423 | #372 | 4 | feed | #91 (37; –) | yes | 100% of 7 | 4,6 | 2 / 0 / 0 of 2 | 69 | 2 of 2 |
| proxy4_king:gen_L_04:A:1 | 424 | #286 | 4 | feed | #91 (37; –) | yes | 100% of 8 | 4,6 | 0 / 2 / 0 of 2 | 68 | 0 of 2 |
| proxy4_king:gen_L_04:A:1 | 425 | #326 | 6 | feed | #91 (38; –) | yes | 100% of 10 | 5,7,9 | 2 / 1 / 0 of 3 | 64 | 2 of 3 |
| proxy4_king:gen_L_04:A:1 | 428 | #310 | 6 | feed | #91 (39; –) | yes | 100% of 12 | 5,5,7 | 0 / 3 / 0 of 3 | 61 | 0 of 3 |
| proxy4_king:gen_L_04:A:1 | 429 | #374 | 4 | feed | #91 (40; –) | yes | 100% of 13 | 4,4 | 2 / 0 / 0 of 2 | 63 | 2 of 2 |
| proxy4_king:gen_L_04:A:1 | 431 | #357 | 7 | feed | #282 (13; –) | no | 0% of 13 | 3,5,7,7 | 0 / 4 / 0 of 4 | 59 | 0 of 4 |
| proxy4_king:gen_L_04:A:1 | 431 | #379 | 5 | feed | #241 (9; –) | no | 0% of 13 | 4,4,4 | 0 / 3 / 0 of 3 | 60 | 0 of 3 |
| proxy4_king:gen_L_04:A:1 | 432 | #165 | 7 | feed | #306 (9; –) | no | 0% of 13 | 5,7,9,11 | 1 / 3 / 0 of 4 | 56 | 1 of 4 |
| proxy4_king:gen_L_04:A:1 | 432 | #290 | 14 | feed | #156 (20; –) | no | 0% of 13 | 3,5,7,5,5,3,3 | 2 / 3 / 1 of 7 | 51 | 2 of 7 |
| proxy4_king:gen_L_04:A:1 | 434 | #300 | 5 | feed | #364 (6; –) | no | 0% of 16 | 3,3,5 | 3 / 0 / 0 of 3 | 58 | 2 of 3 |
| proxy4_king:gen_L_04:A:1 | 437 | #315 | 2 | conv | #306 (11; –) | no | 0% of 19 | 3 | 1 / 0 / 0 of 1 | 58 | 1 of 1 |
| proxy4_king:gen_L_04:A:1 | 439 | #241 | 9 | feed | #320 (12; –) | no | 0% of 19 | 3,5,7,5,5 | 3 / 2 / 0 of 5 | 49 | 1 of 5 |
| proxy4_king:gen_L_04:A:1 | 442 | #373 | 5 | feed | #156 (23; –) | no | 0% of 19 | 5,5,5 | 2 / 1 / 0 of 3 | 48 | 2 of 3 |
| proxy4_king:gen_L_04:A:1 | 446 | #401 | 5 | feed | #320 (16; –) | no | 0% of 18 | 3,3,1 | 0 / 3 / 0 of 3 | 46 | 0 of 3 |
| proxy4_king:gen_L_04:A:1 | 451 | #380 | 7 | cv2 | #91 (48; 48) | yes | 93% of 15 | 3,5,5,7 | 4 / 0 / 0 of 4 | 39 | 4 of 4 |
| proxy4_king:gen_L_04:A:1 | 453 | #404 | 4 | feed | #228 (9; –) | no | 0% of 13 | 3,5 | 0 / 2 / 0 of 2 | 40 | 0 of 2 |
| proxy4_king:gen_L_04:A:1 | 453 | #408 | 5 | feed | #250 (7; –) | no | 0% of 13 | 1,3,3 | 2 / 1 / 0 of 3 | 41 | 2 of 3 |
| proxy4_king:gen_L_04:A:1 | 461 | #403 | 14 | feed | #359 (21; –) | no | 0% of 15 | 3,5,5,7,7,9,7 | 3 / 1 / 2 of 7 | 22 | 3 of 7 |
| proxy4_king:gen_L_04:A:1 | 464 | #353 | 14 | cv2 m jit | #91 (53; 53) | yes | 100% of 16 | 3,3,5,7,5,7,7 | 2 / 0 / 4 of 7 | 19 | 2 of 7 |
| proxy4_king:gen_L_04:A:1 | 474 | #418 | 4 | feed | #415 (10; –) | no | 0% of 14 | 4,6 | 0 / 2 / 0 of 2 | 18 | 0 of 2 |
| proxy4_king:gen_L_04:A:1 | 477 | #156 | 4 | cv2 | #91 (54; 54) | yes | 100% of 13 | 2,4 | 1 / 0 / 1 of 2 | 17 | 1 of 2 |
| proxy4_king:gen_L_04:A:1 | 485 | #422 | 15 | feed | #425 (31; –) | no | 0% of 11 | 2,2,2,4,4,6,4,6 | 1 / 3 / 3 of 8 | -2 | 1 of 8 |
| proxy4_king:gen_L_04:A:1 | 487 | #427 | 2 | feed | #91 (56; –) | yes | 83% of 12 | 4 | 0 / 1 / 0 of 1 | 7 | 0 of 1 |
| proxy4_king:gen_L_04:A:1 | 491 | #428 | 2 | feed | #423 (18; –) | no | 0% of 12 | 2 | 1 / 0 / 0 of 1 | 5 | 1 of 1 |
| proxy4_king:gen_L_04:A:1 | 492 | #434 | 15 | feed | #423 (18; –) | no | 0% of 13 | 3,3,3,5,5,5,7,9 | 1 / 3 / 1 of 8 | -10 | 1 of 8 |
| proxy4_king:gen_L_04:A:1 | 493 | #359 | 4 | cv2 | #430 (40; 40) | no | 0% of 11 | 3,3 | 1 / 0 / 0 of 2 | 0 | 1 of 2 |
| proxy4_king:gen_L_04:A:1 | 494 | #431 | 3 | feed | #423 (18; –) | no | 0% of 11 | 4,6 | 0 / 0 / 0 of 2 | -1 | 0 of 2 |
| proxy4_king:gen_L_04:A:1 | 497 | #423 | 19 | feed | #430 (42; –) | no | 0% of 11 | 5,7,7,9,9,9,11,13,11,9 | 0 / 0 / 0 of 10 | -21 | 0 of 10 |
| proxy4_king:gen_L_04:B:1 | 418 | #340 | 4 | feed | #210 (14; –) | no | 0% of 29 | 3,3 | 1 / 1 / 0 of 2 | 75 | 1 of 2 |
| proxy4_king:gen_L_04:B:1 | 423 | #122 | 7 | feed | #110 (19; –) | yes | 100% of 31 | 3,5,7,9 | 0 / 0 / 4 of 4 | 67 | 0 of 4 |
| proxy4_king:gen_L_04:B:1 | 423 | #261 | 12 | feed | #110 (19; –) | yes | 100% of 31 | 3,5,5,7,7,5 | 3 / 2 / 1 of 6 | 62 | 3 of 6 |
| proxy4_king:gen_L_04:B:1 | 425 | #322 | 10 | feed | #110 (21; –) | yes | 100% of 31 | 2,4,6,8,8 | 3 / 2 / 0 of 5 | 63 | 2 of 5 |
| proxy4_king:gen_L_04:B:1 | 428 | #323 | 8 | feed | #110 (21; –) | yes | 100% of 32 | 5,5,7,9 | 0 / 4 / 0 of 4 | 59 | 0 of 4 |
| proxy4_king:gen_L_04:B:1 | 429 | #362 | 3 | conv | #336 (8; –) | no | 0% of 30 | 2,4 | 2 / 0 / 0 of 2 | 66 | 2 of 2 |
| proxy4_king:gen_L_04:B:1 | 440 | #331 | 5 | feed | #165 (15; –) | no | 0% of 30 | 4,4,4 | 1 / 2 / 0 of 3 | 51 | 1 of 3 |
| proxy4_king:gen_L_04:B:1 | 442 | #377 | 11 | feed | #237 (16; –) | no | 0% of 30 | 2,2,4,6,8,8 | 3 / 3 / 0 of 6 | 45 | 3 of 6 |
| proxy4_king:gen_L_04:B:1 | 444 | #282 | 10 | cv2 m | #110 (27; 27) | yes | 100% of 29 | 2,4,6,8,8 | 0 / 5 / 0 of 5 | 44 | 0 of 5 |
| proxy4_king:gen_L_04:B:1 | 448 | #375 | 9 | feed | #295 (12; –) | no | 0% of 28 | 3,5,7,9,11 | 1 / 4 / 0 of 5 | 40 | 1 of 5 |
| proxy4_king:gen_L_04:B:1 | 457 | #106 | 26 | cv2 m jit | #110 (28; 28) | yes | 100% of 25 | 3,5,7,9,9,7,5,5,5,5,7,9,11 | 3 / 4 / 6 of 13 | 14 | 3 of 13 |
| proxy4_king:gen_L_04:B:1 | 459 | #403 | 14 | feed | #75 (15; –) | no | 0% of 26 | 5,3,1,3,3,5,7 | 3 / 4 / 0 of 7 | 22 | 3 of 7 |
| proxy4_king:gen_L_04:B:1 | 461 | #64 | 18 | cv2 m jit | #110 (30; 30) | yes | 96% of 25 | 2,4,6,6,8,10,12,14,16 | 3 / 3 / 2 of 9 | 19 | 3 of 9 |
| proxy4_king:gen_L_04:B:1 | 462 | #407 | 9 | feed | #354 (10; –) | no | 0% of 23 | 3,1,3,5,7 | 2 / 3 / 0 of 5 | 26 | 2 of 5 |
| proxy4_king:gen_L_04:B:1 | 468 | #286 | 10 | cv2 m | #110 (32; 32) | yes | 90% of 21 | 3,5,7,5,3 | 1 / 2 / 2 of 5 | 19 | 1 of 5 |
| proxy4_king:gen_L_04:B:1 | 471 | #412 | 11 | feed | #411 (15; –) | no | 0% of 20 | 2,4,2,4,6,8 | 3 / 3 / 0 of 6 | 16 | 3 of 6 |
| proxy4_king:gen_L_04:B:1 | 475 | #406 | 18 | feed | #237 (24; –) | no | 0% of 20 | 4,6,6,4,4,6,8,8,6 | 4 / 5 / 0 of 9 | 3 | 4 of 9 |
| proxy4_king:gen_L_04:B:1 | 477 | #415 | 10 | feed | #295 (23; –) | no | 0% of 20 | 4,4,4,6,8 | 2 / 3 / 0 of 5 | 9 | 2 of 5 |
| proxy4_king:gen_L_04:B:1 | 479 | #411 | 18 | feed | #29 (19; –) | no | 0% of 20 | 2,4,6,4,6,8,8,8,10 | 5 / 3 / 0 of 9 | 1 | 5 of 9 |
| proxy4_king:gen_L_04:B:1 | 480 | #418 | 7 | feed | #29 (20; –) | no | 0% of 19 | 3,3,5,5 | 0 / 4 / 0 of 4 | 10 | 0 of 4 |
| proxy4_king:gen_L_04:B:1 | 482 | #410 | 7 | feed | #295 (24; –) | no | 0% of 19 | 4,6,6,4 | 1 / 2 / 1 of 4 | 7 | 1 of 4 |
| proxy4_king:gen_L_05:A:1 | 400 | #274 | 4 | conv | #220 (9; –) | no | 0% of 27 | 2,4 | 2 / 0 / 0 of 2 | 94 | 2 of 2 |
| proxy4_king:gen_L_05:A:1 | 405 | #374 | 7 | feed | #53 (44; –) | yes | 100% of 30 | 5,7,7,5 | 0 / 4 / 0 of 4 | 83 | 0 of 4 |
| proxy4_king:gen_L_05:A:1 | 411 | #225 | 11 | cv2 m | #53 (44; 44) | yes | 90% of 30 | 2,4,4,6,4,4 | 0 / 6 / 0 of 6 | 76 | 0 of 6 |
| proxy4_king:gen_L_05:A:1 | 419 | #313 | 2 | conv | #436 (10; –) | no | 0% of 29 | 3 | 1 / 0 / 0 of 1 | 76 | 1 of 1 |
| proxy4_king:gen_L_05:A:1 | 424 | #328 | 17 | feed | #53 (50; –) | yes | 97% of 30 | 4,4,6,8,10,10,12,14,12 | 3 / 1 / 5 of 9 | 55 | 3 of 9 |
| proxy4_king:gen_L_05:A:1 | 427 | #418 | 3 | conv | #271 (9; –) | no | 0% of 29 | 1,3 | 2 / 0 / 0 of 2 | 69 | 2 of 2 |
| proxy4_king:gen_L_05:A:1 | 430 | #441 | 9 | feed | #267 (12; –) | no | 0% of 32 | 2,4,2,4,2 | 3 / 2 / 0 of 5 | 59 | 3 of 5 |
| proxy4_king:gen_L_05:A:1 | 431 | #462 | 8 | feed | #355 (9; –) | no | 0% of 31 | 3,3,5,5 | 0 / 4 / 0 of 4 | 58 | 0 of 4 |
| proxy4_king:gen_L_05:A:1 | 434 | #438 | 10 | feed | #463 (11; –) | no | 0% of 33 | 3,5,7,5,7 | 0 / 5 / 0 of 5 | 53 | 0 of 5 |
| proxy4_king:gen_L_05:A:1 | 435 | #457 | 7 | feed | #317 (9; –) | no | 0% of 35 | 4,2,2,2 | 2 / 2 / 0 of 4 | 54 | 2 of 4 |
| proxy4_king:gen_L_05:A:1 | 436 | #466 | 5 | feed | #311 (7; –) | no | 0% of 34 | 3,3,3 | 1 / 2 / 0 of 3 | 56 | 1 of 3 |
| proxy4_king:gen_L_05:A:1 | 440 | #473 | 4 | conv | #267 (14; –) | no | 0% of 33 | 2,2 | 2 / 0 / 0 of 2 | 54 | 2 of 2 |
| proxy4_king:gen_L_05:A:1 | 445 | #314 | 2 | cv2 | #267 (16; 16) | no | 0% of 32 | 2 | 1 / 0 / 0 of 1 | 51 | 1 of 1 |
| proxy4_king:gen_L_05:A:1 | 445 | #480 | 4 | feed | #355 (11; –) | no | 0% of 32 | 3,3 | 0 / 2 / 0 of 2 | 48 | 0 of 2 |
| proxy4_king:gen_L_05:A:1 | 450 | #422 | 8 | cv2 m | #317 (12; 12) | no | 7% of 30 | 3,3,5,7 | 3 / 0 / 1 of 4 | 39 | 2 of 4 |
| proxy4_king:gen_L_05:A:1 | 457 | #408 | 6 | cv2 | #317 (14; 13) | no | 3% of 32 | 3,5,7 | 2 / 0 / 1 of 3 | 34 | 2 of 3 |
| proxy4_king:gen_L_05:A:1 | 470 | #507 | 7 | feed | #292 (9; –) | no | 0% of 36 | 2,2,2,4 | 0 / 2 / 1 of 4 | 21 | 0 of 4 |
| proxy4_king:gen_L_05:A:1 | 476 | #526 | 4 | feed | #191 (11; –) | no | 0% of 35 | 2,2 | 1 / 1 / 0 of 2 | 18 | 1 of 2 |
| proxy4_king:gen_L_05:A:1 | 478 | #400 | 13 | cv2 m jit | #317 (19; 19) | no | 3% of 35 | 2,4,6,6,8,8,6 | 1 / 1 / 5 of 7 | 7 | 1 of 7 |
| proxy4_king:gen_L_05:A:1 | 482 | #534 | 10 | feed | #481 (11; –) | no | 0% of 32 | 3,3,1,3,3 | 2 / 2 / 0 of 5 | 5 | 2 of 5 |
| proxy4_king:gen_L_05:A:1 | 483 | #311 | 7 | cv2 | #508 (20; 20) | no | 0% of 30 | 3,5,5,5 | 3 / 0 / 1 of 4 | 7 | 3 of 4 |
| proxy4_king:gen_L_05:A:1 | 483 | #537 | 4 | feed | #481 (12; –) | no | 0% of 30 | 3,5 | 0 / 1 / 1 of 2 | 10 | 0 of 2 |
| proxy4_king:gen_L_05:A:1 | 487 | #533 | 3 | feed | #519 (4; –) | no | 0% of 30 | 5,7 | 0 / 0 / 0 of 2 | 5 | 0 of 2 |
| proxy4_king:gen_L_05:A:1 | 491 | #540 | 10 | feed | #482 (12; –) | no | 0% of 29 | 3,5,5,7,9 | 1 / 1 / 1 of 5 | -4 | 1 of 5 |
| proxy4_king:gen_L_05:B:1 | 404 | #333 | 6 | cv2 | #316 (8; 8) | no | 11% of 19 | 2,2,4 | 2 / 1 / 0 of 3 | 88 | 2 of 3 |
| proxy4_king:gen_L_05:B:1 | 406 | #285 | 4 | feed | #197 (4; –) | no | 0% of 22 | 3,5 | 0 / 1 / 1 of 2 | 87 | 0 of 2 |
| proxy4_king:gen_L_05:B:1 | 408 | #247 | 10 | feed | #51 (46; –) | yes | 76% of 21 | 4,6,6,8,6 | 4 / 1 / 0 of 5 | 78 | 4 of 5 |
| proxy4_king:gen_L_05:B:1 | 416 | #158 | 31 | feed | #51 (49; –) | yes | 87% of 23 | 3,5,5,7,9,11,11,11,13,15,15,13,13,15,17,19 | 1 / 4 / 9 of 16 | 50 | 1 of 16 |
| proxy4_king:gen_L_05:B:1 | 417 | #351 | 7 | cv2 | #51 (49; 47) | yes | 79% of 24 | 3,3,5,7 | 4 / 0 / 0 of 4 | 73 | 3 of 4 |
| proxy4_king:gen_L_05:B:1 | 420 | #375 | 3 | conv | #308 (9; –) | no | 0% of 24 | 3,5 | 2 / 0 / 0 of 2 | 74 | 0 of 2 |
| proxy4_king:gen_L_05:B:1 | 426 | #324 | 2 | conv | #353 (14; –) | no | 3% of 29 | 3 | 1 / 0 / 0 of 1 | 69 | 1 of 1 |
| proxy4_king:gen_L_05:B:1 | 428 | #315 | 15 | feed | #51 (54; –) | yes | 100% of 30 | 3,5,7,9,11,13,15,15 | 1 / 5 / 2 of 8 | 54 | 1 of 8 |
| proxy4_king:gen_L_05:B:1 | 430 | #189 | 4 | conv | #345 (8; –) | no | 0% of 30 | 3,5 | 1 / 1 / 0 of 2 | 63 | 1 of 2 |
| proxy4_king:gen_L_05:B:1 | 430 | #388 | 4 | feed | #349 (7; –) | no | 0% of 30 | 4,4 | 0 / 2 / 0 of 2 | 62 | 0 of 2 |
| proxy4_king:gen_L_05:B:1 | 430 | #411 | 5 | feed | #223 (11; –) | no | 0% of 30 | 3,5,7 | 0 / 0 / 2 of 3 | 62 | 0 of 3 |
| proxy4_king:gen_L_05:B:1 | 431 | #181 | 3 | conv | #51 (55; –) | yes | 100% of 30 | 2,4 | 1 / 1 / 0 of 2 | 64 | 1 of 2 |
| proxy4_king:gen_L_05:B:1 | 434 | #223 | 11 | cv2 m | #51 (56; 56) | yes | 97% of 29 | 1,3,5,7,9,7 | 2 / 3 / 1 of 6 | 54 | 2 of 6 |
| proxy4_king:gen_L_05:B:1 | 434 | #404 | 4 | feed | #254 (6; –) | no | 0% of 29 | 2,4 | 2 / 0 / 0 of 2 | 60 | 2 of 2 |
| proxy4_king:gen_L_05:B:1 | 436 | #420 | 6 | feed | #263 (33; –) | no | 0% of 28 | 4,4,6 | 0 / 2 / 1 of 3 | 54 | 0 of 3 |
| proxy4_king:gen_L_05:B:1 | 438 | #398 | 7 | feed | #192 (8; –) | no | 0% of 28 | 4,6,8,6 | 2 / 2 / 0 of 4 | 51 | 2 of 4 |
| proxy4_king:gen_L_05:B:1 | 454 | #431 | 7 | feed | #228 (9; –) | no | 0% of 28 | 5,5,5,7 | 0 / 4 / 0 of 4 | 34 | 0 of 4 |
| proxy4_king:gen_L_05:B:1 | 465 | #397 | 13 | cv2 m jit | #316 (19; 15) | no | 8% of 25 | 2,4,6,6,4,4,2 | 0 / 0 / 4 of 7 | 20 | 0 of 7 |
| proxy4_king:gen_L_05:B:1 | 469 | #299 | 12 | cv2 m | #242 (33; 33) | no | 29% of 24 | 2,2,4,6,6,4 | 1 / 1 / 4 of 6 | 17 | 1 of 6 |
| proxy4_king:gen_L_05:B:1 | 497 | #457 | 2 | feed | #464 (8; –) | no | 0% of 26 | 2 | 0 / 0 / 0 of 1 | -1 | 0 of 1 |
| proxy4_king:gen_L_06:A:1 | 400 | #446 | 6 | feed | #450 (98; –) | yes | 100% of 7 | 4,6,8 | 0 / 1 / 2 of 3 | 90 | 0 of 3 |
| proxy4_king:gen_L_06:A:1 | 400 | #467 | 3 | conv | #488 (67; –) | no | 0% of 7 | 3,5 | 0 / 2 / 0 of 2 | 94 | 0 of 2 |
| proxy4_king:gen_L_06:A:1 | 400 | #570 | 4 | feed | #549 (5; –) | no | 0% of 7 | 3,3 | 2 / 0 / 0 of 2 | 93 | 2 of 2 |
| proxy4_king:gen_L_06:A:1 | 412 | #481 | 5 | feed | #581 (27; –) | no | 0% of 15 | 4,6,6 | 2 / 1 / 0 of 3 | 79 | 2 of 3 |
| proxy4_king:gen_L_06:A:1 | 417 | #491 | 12 | feed | #325 (19; –) | no | 0% of 17 | 4,6,8,8,8,10 | 3 / 3 / 0 of 6 | 67 | 3 of 6 |
| proxy4_king:gen_L_06:A:1 | 417 | #547 | 5 | feed | #304 (23; –) | no | 0% of 17 | 5,7,7 | 0 / 3 / 0 of 3 | 73 | 0 of 3 |
| proxy4_king:gen_L_06:A:1 | 417 | #582 | 4 | feed | #581 (29; –) | no | 0% of 17 | 2,4 | 2 / 0 / 0 of 2 | 77 | 1 of 2 |
| proxy4_king:gen_L_06:A:1 | 423 | #529 | 3 | cv2 | #450 (99; 99) | yes | 61% of 23 | 3,5 | 1 / 1 / 0 of 2 | 71 | 1 of 2 |
| proxy4_king:gen_L_06:A:1 | 425 | #615 | 5 | feed | #325 (22; –) | no | 0% of 23 | 2,4,6 | 3 / 0 / 0 of 3 | 68 | 3 of 3 |
| proxy4_king:gen_L_06:A:1 | 426 | #470 | 10 | feed | #450 (100; –) | yes | 67% of 24 | 2,4,4,6,8 | 3 / 0 / 0 of 5 | 62 | 3 of 5 |
| proxy4_king:gen_L_06:A:1 | 429 | #593 | 3 | conv | #450 (101; –) | yes | 92% of 24 | 3,5 | 0 / 2 / 0 of 2 | 65 | 0 of 2 |
| proxy4_king:gen_L_06:A:1 | 430 | #583 | 5 | feed | #542 (6; –) | no | 0% of 25 | 5,3,3 | 0 / 1 / 2 of 3 | 60 | 0 of 3 |
| proxy4_king:gen_L_06:A:1 | 430 | #607 | 6 | feed | #523 (7; –) | no | 0% of 25 | 3,5,5 | 2 / 1 / 0 of 3 | 61 | 2 of 3 |
| proxy4_king:gen_L_06:A:1 | 431 | #645 | 6 | feed | #463 (9; –) | no | 0% of 24 | 4,4,2 | 3 / 0 / 0 of 3 | 59 | 3 of 3 |
| proxy4_king:gen_L_06:A:1 | 432 | #650 | 4 | conv | #533 (8; –) | no | 0% of 23 | 2,4 | 0 / 2 / 0 of 2 | 62 | 0 of 2 |
| proxy4_king:gen_L_06:A:1 | 439 | #594 | 7 | cv2 | #450 (104; 104) | yes | 77% of 22 | 2,4,4,6 | 3 / 1 / 0 of 4 | 52 | 3 of 4 |
| proxy4_king:gen_L_06:A:1 | 444 | #523 | 10 | cv2 m | #450 (106; 104) | yes | 68% of 19 | 3,5,5,3,5 | 4 / 1 / 0 of 5 | 43 | 4 of 5 |
| proxy4_king:gen_L_06:A:1 | 445 | #673 | 6 | feed | #652 (24; –) | no | 0% of 18 | 5,7,9 | 0 / 3 / 0 of 3 | 44 | 0 of 3 |
| proxy4_king:gen_L_06:A:1 | 447 | #675 | 12 | feed | #633 (46; –) | no | 0% of 17 | 3,3,5,5,7,5 | 4 / 1 / 0 of 6 | 36 | 4 of 6 |
| proxy4_king:gen_L_06:A:1 | 449 | #548 | 11 | cv2 m | #591 (13; 13) | no | 0% of 16 | 2,2,4,6,6,4 | 2 / 2 / 2 of 6 | 38 | 1 of 6 |
| proxy4_king:gen_L_06:A:1 | 451 | #676 | 5 | feed | #668 (6; –) | no | 0% of 16 | 3,5,3 | 1 / 2 / 0 of 3 | 41 | 1 of 3 |
| proxy4_king:gen_L_06:A:1 | 453 | #555 | 5 | cv2 | #450 (111; 111) | yes | 73% of 15 | 1,3,3 | 1 / 2 / 0 of 3 | 41 | 1 of 3 |
| proxy4_king:gen_L_06:A:1 | 455 | #652 | 26 | feed | #666 (68; –) | no | 0% of 15 | 4,6,8,10,10,8,6,4,4,2,4,6,8 | 4 / 9 / 0 of 13 | 15 | 4 of 13 |
| proxy4_king:gen_L_06:A:1 | 456 | #668 | 7 | feed | #533 (10; –) | no | 0% of 15 | 5,5,3,3 | 0 / 4 / 0 of 4 | 32 | 0 of 4 |
| proxy4_king:gen_L_06:A:1 | 466 | #709 | 80 | feed | #700 (114; –) | yes | 25% of 16 | 4,6,8,6,8,8,10,10,12,12,12,14,16,18,20,20,22,22,24,24,24,24,22,24,24,22,20,20,18,16,18,20,22,22,24,26,28,30,28,28 | 4 / 17 / 2 of 40 | -50 | 4 of 40 |
| proxy4_king:gen_L_06:A:1 | 470 | #545 | 5 | cv2 | #700 (115; 115) | yes | 27% of 15 | 3,5,3 | 2 / 0 / 0 of 3 | 22 | 2 of 3 |
| proxy4_king:gen_L_06:A:1 | 473 | #595 | 10 | cv2 m | #524 (24; 24) | no | 0% of 16 | 1,3,3,5,7 | 1 / 0 / 2 of 5 | 16 | 1 of 5 |
| proxy4_king:gen_L_06:A:1 | 487 | #730 | 14 | feed | #735 (72; –) | no | 0% of 14 | 2,2,4,6,4,4,2 | 5 / 0 / 0 of 7 | -3 | 5 of 7 |
| proxy4_king:gen_L_06:A:1 | 488 | #667 | 8 | feed | #699 (34; –) | no | 0% of 12 | 2,4,6,6 | 4 / 0 / 0 of 4 | 2 | 4 of 4 |
| proxy4_king:gen_L_06:A:1 | 496 | #749 | 2 | feed | #772 (49; –) | no | 0% of 10 | 3 | 0 / 0 / 0 of 1 | -3 | 0 of 1 |
| proxy4_king:gen_L_06:A:1 | 498 | #764 | 18 | feed | #699 (39; –) | no | 0% of 10 | 4,4,4,6,8,10,10,8,10 | 0 / 0 / 0 of 9 | -20 | 0 of 9 |
| proxy4_king:gen_L_06:B:1 | 406 | #488 | 5 | feed | #395 (9; –) | no | 0% of 9 | 5,3,1 | 3 / 0 / 0 of 3 | 84 | 3 of 3 |
| proxy4_king:gen_L_06:B:1 | 411 | #485 | 2 | conv | #500 (39; –) | no | 0% of 12 | 3 | 1 / 0 / 0 of 1 | 84 | 1 of 1 |
| proxy4_king:gen_L_06:B:1 | 412 | #436 | 12 | feed | #395 (13; –) | no | 8% of 13 | 2,2,4,4,4,4 | 1 / 5 / 0 of 6 | 74 | 1 of 6 |
| proxy4_king:gen_L_06:B:1 | 413 | #308 | 11 | feed | #378 (17; –) | no | 0% of 12 | 4,4,4,6,6,4 | 6 / 0 / 0 of 6 | 72 | 6 of 6 |
| proxy4_king:gen_L_06:B:1 | 414 | #444 | 3 | conv | #497 (20; –) | no | 0% of 11 | 3,5 | 0 / 2 / 0 of 2 | 80 | 0 of 2 |
| proxy4_king:gen_L_06:B:1 | 414 | #476 | 3 | conv | #477 (9; –) | no | 0% of 11 | 3,5 | 2 / 0 / 0 of 2 | 80 | 2 of 2 |
| proxy4_king:gen_L_06:B:1 | 417 | #464 | 5 | feed | #497 (21; –) | no | 0% of 11 | 5,7,5 | 0 / 3 / 0 of 3 | 73 | 0 of 3 |
| proxy4_king:gen_L_06:B:1 | 417 | #470 | 5 | feed | #497 (21; –) | no | 0% of 11 | 4,6,8 | 0 / 3 / 0 of 3 | 74 | 0 of 3 |
| proxy4_king:gen_L_06:B:1 | 417 | #516 | 4 | feed | #498 (5; –) | no | 0% of 11 | 3,3 | 1 / 1 / 0 of 2 | 76 | 1 of 2 |
| proxy4_king:gen_L_06:B:1 | 419 | #489 | 4 | feed | #498 (6; –) | no | 0% of 12 | 3,3 | 0 / 2 / 0 of 2 | 74 | 0 of 2 |
| proxy4_king:gen_L_06:B:1 | 424 | #498 | 7 | feed | #527 (39; –) | no | 0% of 19 | 3,5,3,1 | 3 / 1 / 0 of 4 | 66 | 3 of 4 |
| proxy4_king:gen_L_06:B:1 | 430 | #448 | 7 | feed | #531 (13; –) | no | 0% of 21 | 3,5,7,9 | 2 / 2 / 0 of 4 | 60 | 2 of 4 |
| proxy4_king:gen_L_06:B:1 | 430 | #535 | 7 | feed | #522 (21; –) | no | 0% of 21 | 3,1,3,3 | 2 / 2 / 0 of 4 | 60 | 2 of 4 |
| proxy4_king:gen_L_06:B:1 | 431 | #508 | 4 | feed | #412 (9; –) | no | 0% of 22 | 3,5 | 1 / 1 / 0 of 2 | 62 | 1 of 2 |
| proxy4_king:gen_L_06:B:1 | 431 | #519 | 4 | feed | #167 (26; –) | no | 0% of 22 | 1,3 | 2 / 0 / 0 of 2 | 64 | 2 of 2 |
| proxy4_king:gen_L_06:B:1 | 439 | #531 | 15 | feed | #545 (44; –) | no | 0% of 22 | 3,5,7,5,7,7,5,5 | 1 / 7 / 0 of 8 | 43 | 1 of 8 |
| proxy4_king:gen_L_06:B:1 | 445 | #412 | 10 | cv2 m | #251 (31; 31) | no | 8% of 25 | 3,5,7,9,11 | 0 / 5 / 0 of 5 | 42 | 0 of 5 |
| proxy4_king:gen_L_06:B:1 | 448 | #377 | 2 | conv | #564 (99; –) | yes | 0% of 24 | 3 | 1 / 0 / 0 of 1 | 47 | 1 of 1 |
| proxy4_king:gen_L_06:B:1 | 450 | #544 | 13 | feed | #388 (23; –) | no | 0% of 24 | 3,3,5,5,7,7,5 | 7 / 0 / 0 of 7 | 34 | 7 of 7 |
| proxy4_king:gen_L_06:B:1 | 453 | #559 | 3 | conv | #570 (98; –) | yes | 0% of 24 | 2,4 | 2 / 0 / 0 of 2 | 42 | 2 of 2 |
| proxy4_king:gen_L_06:B:1 | 455 | #569 | 18 | feed | #453 (26; –) | no | 5% of 22 | 4,4,6,6,4,6,8,10,10 | 1 / 5 / 3 of 9 | 23 | 1 of 9 |
| proxy4_king:gen_L_06:B:1 | 455 | #571 | 6 | feed | #111 (14; –) | no | 0% of 22 | 4,2,2 | 3 / 0 / 0 of 3 | 35 | 3 of 3 |
| proxy4_king:gen_L_06:B:1 | 457 | #524 | 3 | conv | #561 (10; –) | no | 0% of 23 | 2,4 | 2 / 0 / 0 of 2 | 38 | 2 of 2 |
| proxy4_king:gen_L_06:B:1 | 462 | #433 | 10 | feed | #579 (67; –) | no | 0% of 22 | 2,4,6,6,6 | 2 / 3 / 0 of 5 | 26 | 2 of 5 |
| proxy4_king:gen_L_06:B:1 | 463 | #545 | 3 | conv | #585 (46; –) | no | 0% of 22 | 2,2 | 1 / 0 / 0 of 2 | 32 | 0 of 2 |
| proxy4_king:gen_L_06:B:1 | 463 | #564 | 3 | conv | #580 (28; –) | no | 0% of 22 | 3,3 | 2 / 0 / 0 of 2 | 31 | 2 of 2 |
| proxy4_king:gen_L_06:B:1 | 464 | #428 | 4 | cv2 | #575 (49; 49) | no | 5% of 21 | 3,3 | 2 / 0 / 0 of 2 | 29 | 2 of 2 |
| proxy4_king:gen_L_06:B:1 | 472 | #561 | 12 | feed | #578 (100; –) | yes | 41% of 22 | 4,4,6,6,4,4 | 4 / 0 / 0 of 6 | 12 | 4 of 6 |
| proxy4_king:gen_L_06:B:1 | 486 | #608 | 2 | feed | #538 (3; –) | no | 0% of 22 | 5 | 0 / 0 / 1 of 1 | 7 | 0 of 1 |
| proxy4_king:gen_L_06:B:1 | 488 | #624 | 11 | feed | #616 (18; –) | no | 0% of 20 | 2,4,6,8,8,6 | 5 / 0 / 0 of 6 | -1 | 5 of 6 |
| proxy4_king:gen_L_06:B:1 | 492 | #629 | 29 | feed | #612 (69; –) | no | 5% of 21 | 1,3,3,3,5,7,5,7,7,9,9,11,13,15,13 | 3 / 4 / 0 of 15 | -22 | 3 of 15 |
| proxy4_swarm:gen_L_01:A:1 | 485 | #11 | 2 | feed | #13 (2; –) | no | 0% of 4 | 5 | 0 / 1 / 0 of 1 | 8 | 0 of 1 |
| proxy4_swarm:gen_L_01:A:1 | 485 | #13 | 2 | feed | #19 (2; –) | no | 25% of 4 | 5 | 0 / 1 / 0 of 1 | 8 | 0 of 1 |
| proxy4_swarm:gen_L_01:A:1 | 485 | #18 | 2 | feed | #25 (2; –) | no | 0% of 4 | 5 | 0 / 0 / 1 of 1 | 8 | 0 of 1 |
| proxy4_swarm:gen_L_01:A:1 | 486 | #12 | 2 | feed | #14 (2; –) | no | 25% of 4 | 4 | 0 / 0 / 1 of 1 | 8 | 0 of 1 |
| proxy4_swarm:gen_L_01:A:1 | 486 | #23 | 2 | feed | #2 (2; –) | yes | 0% of 4 | 4 | 0 / 0 / 1 of 1 | 8 | 0 of 1 |
| proxy4_swarm:gen_L_01:A:1 | 488 | #14 | 2 | feed | #2 (2; –) | no | 0% of 4 | 5 | 0 / 0 / 1 of 1 | 5 | 0 of 1 |
| proxy4_swarm:gen_L_01:A:1 | 490 | #19 | 2 | feed | #9 (3; –) | yes | 25% of 4 | 4 | 1 / 0 / 0 of 1 | 4 | 1 of 1 |
| proxy4_swarm:gen_L_01:B:1 | 486 | #10 | 2 | feed | #16 (2; –) | no | – | 5 | 0 / 0 / 1 of 1 | 7 | 0 of 1 |
| proxy4_swarm:gen_L_01:B:1 | 486 | #29 | 2 | feed | #12 (2; –) | no | – | 4 | 0 / 1 / 0 of 1 | 8 | 0 of 1 |
| proxy4_swarm:gen_L_01:B:1 | 486 | #60 | 2 | feed | #19 (2; –) | no | – | 4 | 0 / 0 / 1 of 1 | 8 | 0 of 1 |
| proxy4_swarm:gen_L_01:B:1 | 487 | #34 | 2 | feed | #3 (2; –) | no | – | 4 | 0 / 1 / 0 of 1 | 7 | 0 of 1 |
| proxy4_swarm:gen_L_01:B:1 | 489 | #3 | 2 | feed | #1 (3; –) | yes | – | 3 | 0 / 0 / 1 of 1 | 6 | 0 of 1 |
| proxy4_swarm:gen_L_01:B:1 | 489 | #12 | 2 | feed | #11 (2; –) | no | – | 5 | 0 / 0 / 1 of 1 | 4 | 0 of 1 |
| proxy4_swarm:gen_L_01:B:1 | 491 | #16 | 2 | feed | #30 (2; –) | no | – | 4 | 0 / 0 / 1 of 1 | 3 | 0 of 1 |
| proxy4_swarm:gen_L_01:B:1 | 493 | #19 | 3 | feed | #24 (2; –) | no | – | 5,7 | 0 / 0 / 2 of 2 | -1 | 0 of 2 |
| proxy4_swarm:gen_L_01:B:1 | 496 | #24 | 2 | feed | #30 (2; –) | no | – | 4 | 1 / 0 / 0 of 1 | -2 | 1 of 1 |
| proxy4_swarm:gen_L_03:A:1 | 485 | #61 | 2 | feed | #33 (2; –) | no | 0% of 9 | 5 | 1 / 0 / 0 of 1 | 8 | 1 of 1 |
| proxy4_swarm:gen_L_03:A:1 | 485 | #63 | 2 | feed | #13 (2; –) | no | 33% of 9 | 5 | 0 / 0 / 0 of 1 | 8 | 0 of 1 |
| proxy4_swarm:gen_L_03:A:1 | 486 | #22 | 2 | feed | #33 (2; –) | no | 0% of 9 | 4 | 1 / 0 / 0 of 1 | 8 | 1 of 1 |
| proxy4_swarm:gen_L_03:A:1 | 488 | #11 | 2 | feed | #25 (2; –) | no | 0% of 9 | 3 | 1 / 0 / 0 of 1 | 7 | 1 of 1 |
| proxy4_swarm:gen_L_03:A:1 | 489 | #32 | 2 | feed | #72 (5; –) | yes | 11% of 9 | 4 | 1 / 0 / 0 of 1 | 5 | 1 of 1 |
| proxy4_swarm:gen_L_03:A:1 | 489 | #81 | 3 | feed | #21 (2; –) | no | 0% of 9 | 5,5 | 2 / 0 / 0 of 2 | 3 | 2 of 2 |
| proxy4_swarm:gen_L_03:B:1 | 485 | #27 | 2 | feed | #1 (2; –) | no | 0% of 1 | 5 | 1 / 0 / 0 of 1 | 8 | 1 of 1 |
| proxy4_swarm:gen_L_03:B:1 | 486 | #17 | 2 | feed | #32 (2; –) | no | 100% of 1 | 4 | 0 / 0 / 1 of 1 | 8 | 0 of 1 |
| proxy4_swarm:gen_L_03:B:1 | 487 | #8 | 2 | feed | #6 (2; –) | no | 0% of 1 | 3 | 1 / 0 / 0 of 1 | 8 | 1 of 1 |
| proxy4_swarm:gen_L_03:B:1 | 487 | #62 | 2 | feed | #74 (2; –) | no | 0% of 1 | 5 | 0 / 1 / 0 of 1 | 6 | 0 of 1 |
| proxy4_swarm:gen_L_03:B:1 | 488 | #74 | 2 | feed | #83 (2; –) | no | 0% of 1 | 5 | 0 / 0 / 1 of 1 | 5 | 0 of 1 |
| proxy4_swarm:gen_L_03:B:1 | 493 | #22 | 3 | feed | #80 (2; –) | no | 0% of 1 | 4,4 | 0 / 0 / 2 of 2 | 0 | 0 of 2 |
| proxy4_swarm:gen_L_03:B:1 | 496 | #7 | 2 | feed | #6 (3; –) | no | 0% of 1 | 5 | 0 / 0 / 0 of 1 | -3 | 0 of 1 |
| proxy4_swarm:gen_L_04:A:1 | 406 | #288 | 6 | feed | #133 (21; –) | yes | 100% of 3 | 4,6,6 | 0 / 2 / 1 of 3 | 84 | 0 of 3 |
| proxy4_swarm:gen_L_04:A:1 | 408 | #82 | 2 | conv | #133 (21; –) | yes | 80% of 5 | 1 | 1 / 0 / 0 of 1 | 89 | 1 of 1 |
| proxy4_swarm:gen_L_04:A:1 | 408 | #140 | 6 | feed | #133 (22; –) | yes | 80% of 5 | 4,4,6 | 0 / 2 / 1 of 3 | 82 | 0 of 3 |
| proxy4_swarm:gen_L_04:A:1 | 430 | #301 | 6 | feed | #237 (8; –) | no | 0% of 11 | 2,4,6 | 2 / 0 / 1 of 3 | 62 | 2 of 3 |
| proxy4_swarm:gen_L_04:A:1 | 430 | #302 | 4 | feed | #177 (6; –) | no | 0% of 11 | 3,5 | 2 / 0 / 0 of 2 | 63 | 1 of 2 |
| proxy4_swarm:gen_L_04:A:1 | 430 | #346 | 5 | feed | #286 (7; –) | no | 0% of 11 | 3,5,7 | 0 / 3 / 0 of 3 | 62 | 0 of 3 |
| proxy4_swarm:gen_L_04:A:1 | 431 | #327 | 2 | conv | #259 (8; –) | no | 0% of 11 | 3 | 1 / 0 / 0 of 1 | 64 | 1 of 1 |
| proxy4_swarm:gen_L_04:A:1 | 432 | #286 | 7 | feed | #133 (26; –) | yes | 100% of 11 | 5,5,3,3 | 2 / 1 / 1 of 4 | 56 | 2 of 4 |
| proxy4_swarm:gen_L_04:A:1 | 433 | #285 | 4 | feed | #353 (5; –) | no | 0% of 11 | 5,3 | 1 / 1 / 0 of 2 | 58 | 1 of 2 |
| proxy4_swarm:gen_L_04:A:1 | 436 | #258 | 8 | feed | #259 (9; –) | no | 0% of 11 | 4,4,4,2 | 1 / 3 / 0 of 4 | 52 | 1 of 4 |
| proxy4_swarm:gen_L_04:A:1 | 440 | #256 | 4 | feed | #177 (6; –) | no | 0% of 10 | 4,4 | 0 / 1 / 1 of 2 | 52 | 0 of 2 |
| proxy4_swarm:gen_L_04:A:1 | 443 | #253 | 5 | feed | #353 (5; –) | no | 0% of 10 | 5,5,3 | 3 / 0 / 0 of 3 | 47 | 3 of 3 |
| proxy4_swarm:gen_L_04:A:1 | 443 | #268 | 7 | feed | #259 (10; –) | no | 0% of 10 | 2,4,6,8 | 2 / 2 / 0 of 4 | 48 | 2 of 4 |
| proxy4_swarm:gen_L_04:A:1 | 443 | #335 | 2 | conv | #237 (10; –) | no | 0% of 10 | 3 | 0 / 1 / 0 of 1 | 52 | 0 of 1 |
| proxy4_swarm:gen_L_04:A:1 | 449 | #325 | 3 | conv | #313 (10; –) | no | 0% of 10 | 2,4 | 2 / 0 / 0 of 2 | 46 | 2 of 2 |
| proxy4_swarm:gen_L_04:A:1 | 451 | #331 | 4 | feed | #310 (3; –) | no | 0% of 10 | 3,5 | 2 / 0 / 0 of 2 | 42 | 2 of 2 |
| proxy4_swarm:gen_L_04:A:1 | 455 | #211 | 5 | cv2 | #133 (35; 35) | yes | 89% of 9 | 2,4,4 | 1 / 0 / 2 of 3 | 38 | 1 of 3 |
| proxy4_swarm:gen_L_04:A:1 | 456 | #58 | 5 | cv2 | #133 (35; 32) | yes | 88% of 8 | 3,5,7 | 0 / 0 / 2 of 3 | 36 | 0 of 3 |
| proxy4_swarm:gen_L_04:A:1 | 457 | #294 | 4 | feed | #353 (8; –) | no | 0% of 8 | 3,5 | 1 / 1 / 0 of 2 | 36 | 1 of 2 |
| proxy4_swarm:gen_L_04:A:1 | 459 | #303 | 3 | conv | #353 (8; –) | no | 0% of 7 | 3,5 | 1 / 0 / 1 of 2 | 35 | 1 of 2 |
| proxy4_swarm:gen_L_04:A:1 | 476 | #317 | 5 | feed | #177 (12; –) | no | 0% of 6 | 4,4,6 | 0 / 0 / 2 of 3 | 15 | 0 of 3 |
| proxy4_swarm:gen_L_04:A:1 | 486 | #212 | 2 | feed | #323 (5; –) | no | 20% of 5 | 5 | 1 / 0 / 0 of 1 | 7 | 1 of 1 |
| proxy4_swarm:gen_L_04:B:1 | 453 | #143 | 4 | feed | #96 (5; –) | no | 0% of 3 | 3,5 | 0 / 0 / 2 of 2 | 40 | 0 of 2 |
| proxy4_swarm:gen_L_04:B:1 | 456 | #326 | 6 | feed | #184 (7; –) | yes | 0% of 3 | 1,3,5 | 3 / 0 / 0 of 3 | 37 | 3 of 3 |
| proxy4_swarm:gen_L_04:B:1 | 457 | #71 | 4 | feed | #349 (5; –) | no | 0% of 3 | 3,3 | 0 / 0 / 2 of 2 | 36 | 0 of 2 |
| proxy4_swarm:gen_L_04:B:1 | 464 | #197 | 4 | cv2 | #184 (9; 9) | yes | 50% of 2 | 3,5 | 0 / 1 / 1 of 2 | 29 | 0 of 2 |
| proxy4_swarm:gen_L_04:B:1 | 466 | #304 | 2 | conv | #184 (9; –) | yes | 50% of 2 | 2 | 1 / 0 / 0 of 1 | 30 | 1 of 1 |
| proxy4_swarm:gen_L_04:B:1 | 475 | #158 | 2 | cv2 | #96 (5; 5) | no | 0% of 1 | 2 | 0 / 0 / 1 of 1 | 21 | 0 of 1 |
| proxy4_swarm:gen_L_04:B:1 | 480 | #96 | 5 | feed | #11 (6; –) | no | 0% of 1 | 3,5,7 | 3 / 0 / 0 of 3 | 12 | 2 of 3 |
| proxy4_swarm:gen_L_04:B:1 | 486 | #1 | 3 | feed | #184 (5; –) | no | 100% of 1 | 5,5 | 1 / 0 / 1 of 2 | 6 | 1 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 402 | #439 | 3 | conv | #102 (9; –) | no | 0% of 4 | 2,2 | 2 / 0 / 0 of 2 | 93 | 2 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 405 | #403 | 3 | conv | #102 (10; –) | no | 0% of 6 | 2,4 | 1 / 1 / 0 of 2 | 90 | 1 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 408 | #400 | 4 | feed | #338 (44; –) | yes | 100% of 6 | 4,2 | 1 / 1 / 0 of 2 | 84 | 1 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 414 | #452 | 4 | feed | #338 (46; –) | yes | 43% of 7 | 2,2 | 1 / 1 / 0 of 2 | 80 | 1 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 422 | #191 | 4 | conv | #102 (9; –) | no | 0% of 11 | 3,3 | 0 / 2 / 0 of 2 | 71 | 0 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 426 | #440 | 4 | conv | #102 (9; –) | no | 9% of 11 | 1,3 | 2 / 0 / 0 of 2 | 69 | 2 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 427 | #370 | 3 | conv | #355 (8; –) | no | 0% of 11 | 3,5 | 1 / 1 / 0 of 2 | 67 | 1 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 427 | #383 | 3 | cv2 | #97 (16; 16) | no | 9% of 11 | 2,2 | 1 / 0 / 1 of 2 | 68 | 1 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 430 | #396 | 7 | feed | #102 (11; –) | no | 10% of 10 | 4,2,4,4 | 0 / 1 / 3 of 4 | 59 | 0 of 4 |
| proxy4_swarm:gen_L_05:A:1 | 430 | #406 | 5 | feed | #355 (9; –) | no | 0% of 10 | 2,2,4 | 2 / 1 / 0 of 3 | 63 | 2 of 3 |
| proxy4_swarm:gen_L_05:A:1 | 430 | #432 | 5 | feed | #102 (11; –) | no | 10% of 10 | 3,1,3 | 2 / 1 / 0 of 3 | 62 | 2 of 3 |
| proxy4_swarm:gen_L_05:A:1 | 431 | #421 | 6 | feed | #393 (7; –) | no | 0% of 9 | 4,6,8 | 1 / 2 / 0 of 3 | 59 | 1 of 3 |
| proxy4_swarm:gen_L_05:A:1 | 433 | #479 | 4 | feed | #102 (13; –) | no | 11% of 9 | 5,7 | 0 / 2 / 0 of 2 | 58 | 0 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 434 | #445 | 5 | feed | #135 (24; –) | no | 0% of 9 | 4,4,2 | 3 / 0 / 0 of 3 | 57 | 3 of 3 |
| proxy4_swarm:gen_L_05:A:1 | 435 | #459 | 3 | conv | #420 (8; –) | no | 0% of 9 | 3,5 | 2 / 0 / 0 of 2 | 59 | 1 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 436 | #441 | 5 | cv2 | #102 (13; 11) | no | 0% of 8 | 2,4,6 | 1 / 1 / 1 of 3 | 57 | 1 of 3 |
| proxy4_swarm:gen_L_05:A:1 | 438 | #358 | 4 | feed | #102 (14; –) | no | 0% of 8 | 4,6 | 0 / 0 / 2 of 2 | 54 | 0 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 447 | #438 | 10 | cv2 m | #135 (29; 29) | no | 0% of 11 | 3,5,5,5,7 | 1 / 0 / 4 of 5 | 40 | 1 of 5 |
| proxy4_swarm:gen_L_05:A:1 | 454 | #455 | 4 | feed | #102 (13; –) | no | 36% of 11 | 4,6 | 1 / 1 / 0 of 2 | 38 | 0 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 457 | #477 | 4 | conv | #468 (47; –) | yes | 27% of 11 | 3,3 | 1 / 0 / 1 of 2 | 36 | 1 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 459 | #463 | 3 | cv2 | #102 (13; 13) | no | 20% of 10 | 1,3 | 1 / 0 / 1 of 2 | 37 | 1 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 459 | #465 | 4 | feed | #102 (13; –) | no | 20% of 10 | 4,6 | 1 / 0 / 1 of 2 | 33 | 0 of 2 |
| proxy4_swarm:gen_L_05:A:1 | 468 | #350 | 10 | cv2 m | #521 (33; 33) | no | 13% of 8 | 2,4,6,8,10 | 0 / 0 / 2 of 5 | 20 | 0 of 5 |
| proxy4_swarm:gen_L_05:A:1 | 474 | #453 | 8 | cv2 m | #532 (48; 48) | yes | 0% of 7 | 3,5,7,7 | 2 / 2 / 0 of 4 | 15 | 2 of 4 |
| proxy4_swarm:gen_L_05:A:1 | 478 | #529 | 10 | feed | #532 (49; –) | yes | 20% of 5 | 3,5,5,7,9 | 1 / 0 / 4 of 5 | 9 | 1 of 5 |
| proxy4_swarm:gen_L_05:A:1 | 498 | #546 | 2 | feed | #466 (10; –) | no | 0% of 5 | 4 | 0 / 0 / 0 of 1 | -4 | 0 of 1 |
| proxy4_swarm:gen_L_05:B:1 | 400 | #400 | 4 | feed | #273 (50; –) | yes | 100% of 2 | 3,5 | 1 / 0 / 1 of 2 | 93 | 1 of 2 |
| proxy4_swarm:gen_L_05:B:1 | 410 | #373 | 7 | feed | #414 (23; –) | no | 0% of 2 | 3,5,7,5 | 4 / 0 / 0 of 4 | 80 | 4 of 4 |
| proxy4_swarm:gen_L_05:B:1 | 410 | #386 | 4 | feed | #347 (6; –) | no | 0% of 2 | 4,6 | 0 / 2 / 0 of 2 | 82 | 0 of 2 |
| proxy4_swarm:gen_L_05:B:1 | 412 | #384 | 4 | conv | #274 (32; –) | no | 50% of 2 | 3,3 | 0 / 2 / 0 of 2 | 81 | 0 of 2 |
| proxy4_swarm:gen_L_05:B:1 | 416 | #410 | 7 | feed | #273 (56; –) | yes | 67% of 3 | 3,5,7,5 | 1 / 0 / 3 of 4 | 74 | 1 of 4 |
| proxy4_swarm:gen_L_05:B:1 | 417 | #412 | 4 | feed | #414 (23; –) | no | 0% of 3 | 5,5 | 0 / 2 / 0 of 2 | 74 | 0 of 2 |
| proxy4_swarm:gen_L_05:B:1 | 419 | #406 | 3 | conv | #414 (24; –) | no | 0% of 3 | 2,2 | 2 / 0 / 0 of 2 | 76 | 2 of 2 |
| proxy4_swarm:gen_L_05:B:1 | 425 | #416 | 5 | feed | #273 (55; –) | yes | 100% of 4 | 5,5,7 | 3 / 0 / 0 of 3 | 65 | 3 of 3 |
| proxy4_swarm:gen_L_05:B:1 | 426 | #308 | 5 | feed | #351 (6; –) | no | 0% of 4 | 3,5,3 | 1 / 0 / 2 of 3 | 66 | 1 of 3 |
| proxy4_swarm:gen_L_05:B:1 | 432 | #447 | 4 | feed | #273 (57; –) | yes | 80% of 5 | 4,6 | 0 / 2 / 0 of 2 | 60 | 0 of 2 |
| proxy4_swarm:gen_L_05:B:1 | 434 | #329 | 8 | feed | #273 (58; –) | yes | 100% of 7 | 5,7,5,3 | 3 / 1 / 0 of 4 | 53 | 3 of 4 |
| proxy4_swarm:gen_L_05:B:1 | 439 | #448 | 6 | cv2 | #273 (60; 60) | yes | 50% of 6 | 1,3,3 | 3 / 0 / 0 of 3 | 54 | 3 of 3 |
| proxy4_swarm:gen_L_05:B:1 | 446 | #430 | 8 | cv2 m | #273 (64; 64) | yes | 100% of 5 | 3,5,5,5 | 3 / 1 / 0 of 4 | 43 | 2 of 4 |
| proxy4_swarm:gen_L_05:B:1 | 448 | #349 | 4 | feed | #467 (6; –) | no | 0% of 5 | 5,3 | 1 / 0 / 1 of 2 | 43 | 0 of 2 |
| proxy4_swarm:gen_L_05:B:1 | 448 | #414 | 31 | feed | #273 (64; –) | yes | 100% of 5 | 4,6,6,8,10,10,10,12,14,14,16,18,20,18,16,16 | 6 / 3 / 6 of 16 | 17 | 6 of 16 |
| proxy4_swarm:gen_L_05:B:1 | 454 | #442 | 7 | feed | #375 (10; –) | no | 0% of 5 | 5,5,5,5 | 0 / 0 / 2 of 4 | 34 | 0 of 4 |
| proxy4_swarm:gen_L_05:B:1 | 457 | #375 | 11 | feed | #273 (69; –) | yes | 100% of 5 | 3,5,5,7,7,5 | 0 / 3 / 3 of 6 | 29 | 0 of 6 |
| proxy4_swarm:gen_L_05:B:1 | 467 | #312 | 12 | cv2 m | #273 (72; 72) | yes | 83% of 6 | 2,4,2,4,6,8 | 3 / 1 / 0 of 6 | 19 | 3 of 6 |
| proxy4_swarm:gen_L_05:B:1 | 475 | #434 | 12 | feed | #355 (16; –) | no | 20% of 5 | 2,2,4,6,4,2 | 0 / 0 / 5 of 6 | 11 | 0 of 6 |
| proxy4_swarm:gen_L_05:B:1 | 477 | #424 | 6 | feed | #467 (9; –) | no | 0% of 5 | 3,5,7 | 0 / 0 / 3 of 3 | 14 | 0 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 400 | #464 | 7 | feed | #462 (55; –) | yes | 100% of 3 | 3,5,5,7 | 1 / 2 / 0 of 4 | 90 | 1 of 4 |
| proxy4_swarm:gen_L_06:A:1 | 400 | #569 | 4 | conv | #559 (20; –) | no | 0% of 3 | 1,3 | 2 / 0 / 0 of 2 | 95 | 2 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 402 | #216 | 2 | conv | #559 (20; –) | no | 0% of 3 | 3 | 1 / 0 / 0 of 1 | 93 | 1 of 1 |
| proxy4_swarm:gen_L_06:A:1 | 403 | #511 | 2 | conv | #542 (33; –) | no | 0% of 4 | 2 | 1 / 0 / 0 of 1 | 93 | 0 of 1 |
| proxy4_swarm:gen_L_06:A:1 | 404 | #565 | 6 | feed | #472 (13; –) | no | 0% of 5 | 4,2,4 | 0 / 3 / 0 of 3 | 86 | 0 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 406 | #545 | 5 | feed | #547 (19; –) | no | 0% of 4 | 5,3,5 | 2 / 1 / 0 of 3 | 84 | 2 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 407 | #465 | 4 | conv | #542 (35; –) | no | 0% of 5 | 2,4 | 1 / 1 / 0 of 2 | 87 | 1 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 407 | #532 | 2 | conv | #472 (13; –) | no | 0% of 5 | 3 | 1 / 0 / 0 of 1 | 88 | 1 of 1 |
| proxy4_swarm:gen_L_06:A:1 | 411 | #497 | 5 | feed | #572 (37; –) | no | 20% of 5 | 4,4,6 | 2 / 1 / 0 of 3 | 80 | 1 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 414 | #472 | 12 | feed | #462 (61; –) | yes | 67% of 6 | 3,1,1,3,5,5 | 1 / 2 / 1 of 6 | 71 | 1 of 6 |
| proxy4_swarm:gen_L_06:A:1 | 414 | #559 | 25 | feed | #542 (38; –) | no | 0% of 6 | 3,3,3,1,3,5,7,5,5,3,5,5,7 | 6 / 2 / 5 of 13 | 56 | 6 of 13 |
| proxy4_swarm:gen_L_06:A:1 | 414 | #588 | 4 | feed | #440 (21; –) | no | 0% of 6 | 1,3 | 2 / 0 / 0 of 2 | 81 | 1 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 415 | #526 | 6 | feed | #572 (37; –) | no | 33% of 6 | 3,5,3 | 1 / 1 / 1 of 3 | 76 | 1 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 415 | #551 | 4 | feed | #594 (16; –) | no | 0% of 6 | 4,4 | 0 / 1 / 1 of 2 | 77 | 0 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 417 | #531 | 6 | feed | #302 (25; –) | no | 0% of 6 | 4,4,6 | 2 / 0 / 1 of 3 | 73 | 1 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 419 | #544 | 4 | conv | #440 (22; –) | no | 0% of 7 | 3,5 | 2 / 0 / 0 of 2 | 74 | 2 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 420 | #523 | 4 | conv | #440 (23; –) | no | 0% of 7 | 3,5 | 2 / 0 / 0 of 2 | 73 | 2 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 420 | #604 | 4 | feed | #462 (63; –) | yes | 57% of 7 | 3,5 | 0 / 0 / 0 of 2 | 73 | 0 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 422 | #594 | 18 | feed | #627 (26; –) | no | 0% of 9 | 2,4,4,6,8,8,10,8,6 | 4 / 4 / 1 of 9 | 58 | 4 of 9 |
| proxy4_swarm:gen_L_06:A:1 | 430 | #627 | 29 | feed | #462 (64; –) | yes | 69% of 13 | 3,3,5,7,5,5,5,7,7,7,7,9,9,11,13 | 4 / 0 / 11 of 15 | 38 | 4 of 15 |
| proxy4_swarm:gen_L_06:A:1 | 439 | #608 | 10 | feed | #499 (17; –) | no | 0% of 14 | 3,1,3,5,7 | 4 / 0 / 0 of 5 | 46 | 4 of 5 |
| proxy4_swarm:gen_L_06:A:1 | 439 | #625 | 4 | feed | #599 (6; –) | no | 0% of 14 | 4,2 | 2 / 0 / 0 of 2 | 53 | 2 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 441 | #623 | 4 | feed | #512 (5; –) | no | 0% of 13 | 5,7 | 0 / 1 / 1 of 2 | 50 | 0 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 447 | #541 | 6 | cv2 | #642 (15; 15) | no | 0% of 12 | 2,2,4 | 2 / 1 / 0 of 3 | 45 | 2 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 457 | #492 | 4 | feed | #593 (5; –) | no | 0% of 12 | 3,5 | 2 / 0 / 0 of 2 | 36 | 2 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 458 | #584 | 4 | feed | #609 (5; –) | no | 0% of 12 | 5,3 | 1 / 0 / 1 of 2 | 33 | 1 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 459 | #580 | 5 | cv2 | #549 (57; 56) | no | 9% of 11 | 3,3,5 | 3 / 0 / 0 of 3 | 33 | 3 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 459 | #617 | 5 | feed | #593 (6; –) | no | 0% of 11 | 4,6,8 | 3 / 0 / 0 of 3 | 32 | 3 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 464 | #302 | 5 | feed | #645 (25; –) | no | 0% of 11 | 4,6,4 | 1 / 0 / 2 of 3 | 27 | 1 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 464 | #681 | 4 | feed | #652 (50; –) | no | 18% of 11 | 2,2 | 0 / 0 / 2 of 2 | 30 | 0 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 467 | #574 | 20 | cv2 m jit | #549 (61; 61) | no | 10% of 10 | 3,5,7,7,5,5,3,5,7,5 | 1 / 9 / 0 of 10 | 10 | 1 of 10 |
| proxy4_swarm:gen_L_06:A:1 | 469 | #609 | 5 | cv2 | #593 (10; 10) | no | 0% of 9 | 3,5,7 | 3 / 0 / 0 of 3 | 23 | 3 of 3 |
| proxy4_swarm:gen_L_06:A:1 | 477 | #653 | 3 | conv | #704 (25; –) | no | 0% of 10 | 3,3 | 1 / 0 / 1 of 2 | 17 | 1 of 2 |
| proxy4_swarm:gen_L_06:A:1 | 481 | #723 | 17 | feed | #440 (36; –) | no | 22% of 9 | 4,6,6,6,4,6,8,10,10 | 5 / 0 / 2 of 9 | -2 | 5 of 9 |
| proxy4_swarm:gen_L_06:A:1 | 485 | #731 | 27 | feed | #499 (30; –) | no | 0% of 8 | 1,1,3,3,5,7,9,11,11,13,15,13,11,9 | 2 / 2 / 6 of 14 | -13 | 2 of 14 |
| proxy4_swarm:gen_L_06:A:1 | 487 | #713 | 26 | feed | #728 (62; –) | no | 13% of 8 | 5,7,7,7,9,11,9,7,9,7,5,3,3 | 5 / 0 / 3 of 13 | -18 | 5 of 13 |
| proxy4_swarm:gen_L_06:A:1 | 491 | #745 | 2 | feed | #708 (2; –) | no | 0% of 8 | 3 | 1 / 0 / 0 of 1 | 4 | 1 of 1 |
| proxy4_swarm:gen_L_06:A:1 | 499 | #759 | 2 | feed | #499 (3; –) | no | 9% of 11 | 2 | 0 / 0 / 0 of 1 | -3 | 0 of 1 |
| proxy4_swarm:gen_L_06:B:1 | 402 | #457 | 3 | conv | #540 (24; –) | no | 0% of 10 | 2,2 | 2 / 0 / 0 of 2 | 93 | 1 of 2 |
| proxy4_swarm:gen_L_06:B:1 | 403 | #494 | 5 | feed | #330 (15; –) | no | 0% of 10 | 4,4,6 | 1 / 2 / 0 of 3 | 88 | 1 of 3 |
| proxy4_swarm:gen_L_06:B:1 | 404 | #394 | 5 | feed | #362 (47; –) | no | 80% of 10 | 3,5,7 | 2 / 0 / 0 of 3 | 88 | 0 of 3 |
| proxy4_swarm:gen_L_06:B:1 | 407 | #439 | 10 | feed | #362 (49; –) | no | 80% of 15 | 4,2,4,6,8 | 3 / 2 / 0 of 5 | 79 | 3 of 5 |
| proxy4_swarm:gen_L_06:B:1 | 411 | #527 | 8 | feed | #362 (51; –) | no | 11% of 18 | 5,7,7,9 | 0 / 4 / 0 of 4 | 76 | 0 of 4 |
| proxy4_swarm:gen_L_06:B:1 | 413 | #512 | 33 | feed | #362 (52; –) | no | 6% of 17 | 3,5,7,9,11,11,9,9,11,11,13,13,13,13,15,15,17 | 0 / 17 / 0 of 17 | 51 | 0 of 17 |
| proxy4_swarm:gen_L_06:B:1 | 416 | #509 | 8 | cv2 m | #379 (17; 17) | no | 19% of 16 | 2,4,4,6 | 3 / 1 / 0 of 4 | 74 | 2 of 4 |
| proxy4_swarm:gen_L_06:B:1 | 420 | #516 | 3 | conv | #379 (19; –) | no | 11% of 18 | 2,4 | 2 / 0 / 0 of 2 | 75 | 2 of 2 |
| proxy4_swarm:gen_L_06:B:1 | 422 | #580 | 3 | cv2 | #330 (17; 17) | no | 24% of 17 | 2,4 | 1 / 0 / 1 of 2 | 73 | 1 of 2 |
| proxy4_swarm:gen_L_06:B:1 | 423 | #562 | 4 | feed | #461 (6; –) | no | 6% of 17 | 5,3 | 2 / 0 / 0 of 2 | 68 | 2 of 2 |
| proxy4_swarm:gen_L_06:B:1 | 423 | #585 | 5 | feed | #556 (10; –) | no | 0% of 17 | 4,6,4 | 2 / 1 / 0 of 3 | 68 | 2 of 3 |
| proxy4_swarm:gen_L_06:B:1 | 425 | #470 | 2 | conv | #594 (29; –) | no | 0% of 17 | 3 | 1 / 0 / 0 of 1 | 70 | 1 of 1 |
| proxy4_swarm:gen_L_06:B:1 | 430 | #584 | 5 | feed | #598 (16; –) | no | 0% of 18 | 2,4,4 | 0 / 3 / 0 of 3 | 63 | 0 of 3 |
| proxy4_swarm:gen_L_06:B:1 | 432 | #480 | 6 | feed | #604 (42; –) | no | 0% of 17 | 4,6,6 | 3 / 0 / 0 of 3 | 58 | 3 of 3 |
| proxy4_swarm:gen_L_06:B:1 | 434 | #535 | 3 | conv | #461 (8; –) | no | 0% of 17 | 2,2 | 0 / 2 / 0 of 2 | 61 | 0 of 2 |
| proxy4_swarm:gen_L_06:B:1 | 435 | #608 | 6 | feed | #554 (8; –) | no | 0% of 17 | 4,4,4 | 1 / 2 / 0 of 3 | 55 | 1 of 3 |
| proxy4_swarm:gen_L_06:B:1 | 437 | #616 | 13 | feed | #362 (65; –) | yes | 39% of 18 | 4,4,6,8,8,10,10 | 5 / 2 / 0 of 7 | 46 | 5 of 7 |
| proxy4_swarm:gen_L_06:B:1 | 442 | #461 | 9 | cv2 m | #330 (20; 20) | no | 13% of 16 | 3,5,3,1,3 | 5 / 0 / 0 of 5 | 46 | 3 of 5 |
| proxy4_swarm:gen_L_06:B:1 | 442 | #540 | 2 | conv | #631 (29; –) | no | 0% of 16 | 1 | 1 / 0 / 0 of 1 | 55 | 1 of 1 |
| proxy4_swarm:gen_L_06:B:1 | 442 | #594 | 2 | conv | #628 (28; –) | no | 0% of 16 | 2 | 0 / 1 / 0 of 1 | 54 | 0 of 1 |
| proxy4_swarm:gen_L_06:B:1 | 445 | #545 | 10 | feed | #627 (21; –) | no | 0% of 16 | 4,6,8,8,8 | 0 / 4 / 1 of 5 | 41 | 0 of 5 |
| proxy4_swarm:gen_L_06:B:1 | 445 | #560 | 6 | cv2 | #362 (69; 69) | yes | 56% of 16 | 3,5,7 | 1 / 2 / 0 of 3 | 46 | 1 of 3 |
| proxy4_swarm:gen_L_06:B:1 | 448 | #573 | 8 | feed | #586 (31; –) | no | 0% of 17 | 5,7,5,3 | 4 / 0 / 0 of 4 | 39 | 4 of 4 |
| proxy4_swarm:gen_L_06:B:1 | 448 | #604 | 47 | feed | #620 (70; –) | no | 0% of 17 | 4,6,6,6,8,8,10,12,14,16,14,12,10,12,12,10,10,8,10,10,8,10,8,6 | 4 / 9 / 11 of 24 | 1 | 4 of 24 |
| proxy4_swarm:gen_L_06:B:1 | 453 | #449 | 8 | cv2 m | #634 (11; 10) | no | 7% of 15 | 3,5,7,9 | 3 / 1 / 0 of 4 | 36 | 3 of 4 |
| proxy4_swarm:gen_L_06:B:1 | 455 | #525 | 2 | cv2 | #634 (12; 11) | no | 0% of 14 | 3 | 1 / 0 / 0 of 1 | 40 | 1 of 1 |
| proxy4_swarm:gen_L_06:B:1 | 457 | #602 | 5 | feed | #620 (73; –) | no | 0% of 14 | 5,7,9 | 1 / 2 / 0 of 3 | 33 | 1 of 3 |
| proxy4_swarm:gen_L_06:B:1 | 458 | #628 | 29 | feed | #362 (74; –) | no | 0% of 14 | 2,4,4,6,8,6,8,10,10,12,14,12,14,16,16 | 9 / 4 / 2 of 15 | 11 | 9 of 15 |
| proxy4_swarm:gen_L_06:B:1 | 468 | #473 | 11 | cv2 m | #637 (20; 20) | no | 0% of 13 | 3,5,7,7,5,5 | 5 / 0 / 0 of 6 | 18 | 5 of 6 |
| proxy4_swarm:gen_L_06:B:1 | 469 | #379 | 3 | cv2 | #635 (25; 25) | no | 0% of 12 | 2,4 | 1 / 0 / 1 of 2 | 26 | 0 of 2 |
| proxy4_swarm:gen_L_06:B:1 | 471 | #601 | 9 | feed | #362 (81; –) | yes | 9% of 11 | 4,6,8,6,4 | 0 / 0 / 4 of 5 | 16 | 0 of 5 |
| proxy4_swarm:gen_L_06:B:1 | 474 | #148 | 8 | cv2 m | #634 (16; 16) | no | 9% of 11 | 2,4,4,6 | 4 / 0 / 0 of 4 | 16 | 4 of 4 |
| proxy4_swarm:gen_L_06:B:1 | 474 | #649 | 2 | conv | #636 (12; –) | no | 9% of 11 | 3 | 1 / 0 / 0 of 1 | 21 | 0 of 1 |
| proxy4_swarm:gen_L_06:B:1 | 492 | #701 | 8 | feed | #636 (15; –) | no | 11% of 9 | 5,7,5,5 | 2 / 1 / 0 of 4 | -5 | 2 of 4 |
| proxy4_swarm:gen_L_06:B:1 | 493 | #717 | 10 | feed | #634 (21; –) | no | 18% of 11 | 3,3,3,1,3 | 2 / 1 / 0 of 5 | -6 | 2 of 5 |
| proxy4_swarm:gen_L_06:B:1 | 497 | #671 | 3 | conv | #725 (24; –) | no | 0% of 12 | 1,3 | 2 / 0 / 0 of 2 | -1 | 2 of 2 |
