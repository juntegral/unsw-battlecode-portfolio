## Games read

55 games: 28 on large maps, 11 on medium, 16 on small; 30 of ours and 25 of the top three with the same opponents. "Tables" = the per-10-round tables of
`c_econ.py` for rounds 0-150 (both sides), kept as `c_out/ec_<id>.txt`; the large-map games also for rounds 150-350 (`c_out/ecm_<id>.txt`).
Every game was read for both sides, so the opponent in each of our games (test4, WeHaveQuizzes) is read as well.
The column "end": `wipe-out rN` = one team had no dragon left at round N. Otherwise the game runs 500 rounds and the team with
the longer queen wins, a dead queen counting as 0 (`queen rule`); if that is a tie (both dead, as a rule), the team with the
longest living dragon (`longest`).
The column "run and build" is for our own games: the run the game came from (`c_batches.py`) and what bot played it; see
"Which bot played" above. On large maps 8 of the 16 games of ours read are from the trade-on-contact test build.

| # | game id | map | size | team read | side | opponent (elo) | result | end | final units / total / longest, own vs opponent | run and build (our games) | read with |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1058144 | Australia | large | meow | A | test4 (2176) | loss | queen rule | 4 / 29 / 10 vs 63 / 571 / 61 | `passage2-test-old`: live bot | tables, board r40, pocket tiles |
| 2 | 1067904 | Australia | large | meow | A | test4 (2083) | loss | queen rule | 54 / 174 / 18 vs 49 / 303 / 42 | `tc30-test-new`: test build, trade on contact | tables |
| 3 | 1068050 | Australia | large | meow | A | WeHaveQuizzes (2180) | loss | queen rule | 19 / 136 / 29 vs 7 / 204 / 70 | `tc30-test-new`: test build, trade on contact | tables, ledger to r349 |
| 4 | 1021860 | Australia | large | meow | A | ComTamSuonNuong (2073) | win | longest | 52 / 217 / 30 vs 61 / 211 / 29 | ladder: live bot | tables |
| 5 | 1046985 | Australia | large | forgot | A | test4 (2171) | win | longest | 18 / 220 / 58 vs 11 / 96 / 23 | - | tables |
| 6 | 1046528 | Australia | large | SSS | B | test4 (2171) | win | queen rule | 30 / 241 / 54 vs 14 / 246 / 65 | - | tables |
| 7 | 1069883 | Australia | large | forgot | B | WeHaveQuizzes (2217) | loss | longest | 14 / 211 / 66 vs 6 / 148 / 76 | - | tables |
| 8 | 1054789 | Australia | large | Vibing++ | B | test4 (2189) | loss | longest | 5 / 89 / 32 vs 14 / 393 / 93 | - | tables |
| 9 | 1063012 | Islands | large | meow | A | test4 (2131) | loss | longest | 3 / 15 / 11 vs 17 / 336 / 57 | `qh31-test-old`: live bot | tables |
| 10 | 1067905 | Islands | large | meow | A | test4 (2083) | loss | longest | 12 / 84 / 34 vs 16 / 246 / 63 | `tc30-test-new`: test build, trade on contact | tables, ledger to r349 |
| 11 | 1068051 | Islands | large | meow | A | WeHaveQuizzes (2180) | loss | longest | 7 / 41 / 16 vs 8 / 235 / 82 | `tc30-test-new`: test build, trade on contact | tables, events r8-24 and r19-24, fountain tiles, length classes r100-349, dragon list r140-220 |
| 12 | 1063671 | Islands | large | meow | A | test4 (2131) | loss | wipe-out r313 | 0 / 0 / 0 vs 63 / 381 / 22 | `qh31-test-new`: test build, queen hunt | tables |
| 13 | 1062235 | Islands | large | forgot | A | WeHaveQuizzes (2143) | win | longest | 11 / 216 / 84 vs 2 / 72 / 63 | - | tables |
| 14 | 1051826 | Islands | large | SSS | A | test4 (2165) | win | longest | 11 / 61 / 20 vs 51 / 270 / 12 | - | tables |
| 15 | 1046989 | Islands | large | forgot | A | test4 (2171) | loss | queen rule | 12 / 110 / 56 vs 39 / 234 / 53 | - | tables |
| 16 | 1063016 | Around UNSW | large | meow | A | test4 (2131) | loss | longest | 20 / 258 / 73 vs 20 / 314 / 100 | `qh31-test-old`: live bot | tables |
| 17 | 1068055 | Around UNSW | large | meow | A | WeHaveQuizzes (2180) | loss | longest | 20 / 178 / 48 vs 11 / 282 / 68 | `tc30-test-new`: test build, trade on contact | tables |
| 18 | 1067909 | Around UNSW | large | meow | A | test4 (2093) | loss | queen rule | 33 / 222 / 47 vs 61 / 443 / 45 | `tc30-test-new`: test build, trade on contact | tables, fountain tiles, boards r22 and r28, events r22-30 |
| 19 | 1063675 | Around UNSW | large | meow | A | test4 (2131) | win | longest | 23 / 199 / 69 vs 40 / 397 / 49 | `qh31-test-new`: test build, queen hunt | tables |
| 20 | 1064304 | Around UNSW | large | SSS | A | test4 (2121) | win | longest | 60 / 372 / 83 vs 17 / 251 / 54 | - | tables |
| 21 | 1062237 | Around UNSW | large | forgot | A | WeHaveQuizzes (2143) | loss | longest | 18 / 316 / 72 vs 8 / 211 / 79 | - | tables |
| 22 | 1063252 | Slithery Fight | large | meow | A | WeHaveQuizzes (2135) | loss | longest | 20 / 177 / 64 vs 10 / 227 / 94 | `qh31-test-old`: live bot | tables |
| 23 | 1067917 | Slithery Fight | large | meow | A | test4 (2093) | loss | queen rule | 21 / 153 / 51 vs 36 / 244 / 62 | `tc30-test-new`: test build, trade on contact | tables, death cells, splits |
| 24 | 1068063 | Slithery Fight | large | meow | A | WeHaveQuizzes (2180) | loss | longest | 21 / 124 / 53 vs 5 / 258 / 92 | `tc30-test-new`: test build, trade on contact | tables, ledger |
| 25 | 1063024 | Slithery Fight | large | meow | A | test4 (2131) | win | longest | 27 / 163 / 79 vs 61 / 283 / 17 | `qh31-test-old`: live bot | tables |
| 26 | 1051824 | Slithery Fight | large | SSS | A | test4 (2165) | win | longest | 37 / 166 / 22 vs 49 / 283 / 18 | - | tables, death cells, fountain tiles |
| 27 | 1046988 | Slithery Fight | large | forgot | A | test4 (2171) | loss | queen rule | 33 / 161 / 39 vs 42 / 252 / 64 | - | tables, splits |
| 28 | 1054792 | Slithery Fight | large | Vibing++ | B | test4 (2189) | win | longest | 16 / 273 / 90 vs 40 / 140 / 18 | - | tables |
| 29 | 1067915 | Trauma | medium | meow | A | test4 (2093) | loss | queen rule | 4 / 30 / 14 vs 26 / 122 / 33 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 30 | 1068061 | Trauma | medium | meow | A | WeHaveQuizzes (2180) | loss | wipe-out r467 | 0 / 0 / 0 vs 6 / 130 / 38 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 31 | 1063774 | Trauma | medium | meow | A | WeHaveQuizzes (2135) | win | queen rule | 4 / 59 / 50 vs 4 / 113 / 49 | `qh31-test-new`: test build, queen hunt | tables |
| 32 | 1046991 | Trauma | medium | forgot | A | test4 (2171) | win | queen rule | 5 / 79 / 46 vs 10 / 64 / 25 | - | tables |
| 33 | 1054786 | Trauma | medium | SSS | B | test4 (2189) | win | queen rule | 10 / 74 / 32 vs 14 / 84 / 30 | - | tables |
| 34 | 1067906 | Maze | medium | meow | A | test4 (2093) | loss | queen rule | 19 / 100 / 47 vs 13 / 124 / 73 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 35 | 1068052 | Maze | medium | meow | A | WeHaveQuizzes (2180) | loss | longest | 12 / 131 / 66 vs 4 / 121 / 94 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables, fountain tiles |
| 36 | 1063672 | Maze | medium | meow | A | test4 (2131) | win | longest | 8 / 134 / 76 vs 3 / 81 / 64 | `qh31-test-new`: test build, queen hunt | tables |
| 37 | 1046984 | Maze | medium | forgot | A | test4 (2171) | loss | queen rule | 15 / 148 / 55 vs 17 / 121 / 67 | - | tables |
| 38 | 1046526 | Maze | medium | SSS | B | test4 (2171) | win | queen rule | 6 / 135 / 93 vs 5 / 123 / 66 | - | tables |
| 39 | 1069373 | Maze | medium | SSS | B | WeHaveQuizzes (2204) | win | queen rule | 16 / 167 / 48 vs 4 / 73 / 37 | - | tables |
| 40 | 1067908 | Tower Defense | small | meow | A | test4 (2093) | loss | wipe-out r322 | 0 / 0 / 0 vs 52 / 136 / 4 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 41 | 1068054 | Tower Defense | small | meow | A | WeHaveQuizzes (2180) | loss | queen rule | 3 / 73 / 28 vs 2 / 46 / 32 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 42 | 1046992 | Tower Defense | small | forgot | A | test4 (2171) | win | longest | 21 / 108 / 37 vs 1 / 14 / 14 | - | tables |
| 43 | 1051827 | Tower Defense | small | SSS | A | test4 (2165) | win | wipe-out r230 | 44 / 105 / 3 vs 0 / 0 / 0 | - | tables |
| 44 | 1070191 | Tower Defense | small | forgot | B | WeHaveQuizzes (2202) | win | wipe-out r124 | 27 / 70 / 3 vs 0 / 0 / 0 | - | tables |
| 45 | 1067907 | Stripes | small | meow | A | test4 (2093) | loss | wipe-out r140 | 0 / 0 / 0 vs 20 / 50 / 5 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables, events r0-34, board r18 |
| 46 | 1068053 | Stripes | small | meow | A | WeHaveQuizzes (2180) | loss | wipe-out r176 | 0 / 0 / 0 vs 28 / 64 / 4 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 47 | 1059076 | Stripes | small | meow | A | WeHaveQuizzes (2155) | win | wipe-out r274 | 18 / 42 / 3 vs 0 / 0 / 0 | `passage2-test-new`: test build | tables |
| 48 | 1046977 | Stripes | small | forgot | A | test4 (2171) | win | wipe-out r91 | 13 / 33 / 5 vs 0 / 0 / 0 | - | tables |
| 49 | 1062236 | Stripes | small | forgot | A | WeHaveQuizzes (2143) | win | wipe-out r141 | 16 / 36 / 4 vs 0 / 0 / 0 | - | tables |
| 50 | 1063682 | Portals | small | meow | A | test4 (2131) | loss | longest | 9 / 53 / 16 vs 2 / 46 / 33 | `qh31-test-new`: test build, queen hunt | tables, fountain tiles, board r60 |
| 51 | 1063251 | Portals | small | meow | A | WeHaveQuizzes (2135) | loss | longest | 13 / 58 / 9 vs 2 / 40 / 37 | `qh31-test-old`: live bot | tables |
| 52 | 1067916 | Portals | small | meow | A | test4 (2093) | win | longest | 3 / 57 / 49 vs 1 / 44 / 44 | `tc30-test-new`: test build, trade on contact (same as live on this map) | tables |
| 53 | 1046982 | Portals | small | forgot | A | test4 (2171) | loss | queen rule | 4 / 84 / 57 vs 4 / 49 / 40 | - | tables |
| 54 | 1062234 | Portals | small | forgot | A | WeHaveQuizzes (2143) | win | queen rule | 4 / 45 / 28 vs 1 / 44 / 44 | - | tables |
| 55 | 1064306 | Portals | small | SSS | A | test4 (2121) | win | queen rule | 5 / 51 / 32 vs 2 / 42 / 40 | - | tables |
