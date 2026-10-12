# 스위치와 정책 값: 읽은 v1.3 코드

기본 경로는 `versions/v1.3/bot/`다. `v1.4/...`는 `versions/v1.4/bot/...`다. 선언된 boolean과 **실제 실행 코드의 읽기 지점**을 함께 적었다. 주석에서만 언급한 것은 read로 세지 않았다. `true`라도 engine/map/phase gate로 발동하지 않을 수 있다(`plan.cpp:1307`, `policy.hpp:160`).

## params.hpp의 constexpr bool 전체

정의 63개를 파일에서 추출했고, 각 이름의 `P::NAME` read를 v1.3의 모든 `.cpp/.hpp`에서 교차 조회했다.

| switch / definition | v1.3 value | gates | read sites(files와 lines) |
|---|---|---|---|
| `POCKET_EAT` / `params.hpp:108` | `true` | doom dead-end에서 마지막 진주를 먹고 escape split을 한 차례 늦춤 | `plan.cpp:1922` |
| `POCKET_EAT_MAP_DRAGONS` / `params.hpp:109` | `false` | map-given dragon에도 pocket-eat 허용; false여도 low-yield 예외는 별개 | `plan.cpp:1923` |
| `POCKET_MAP_LOW_YIELD` / `params.hpp:113` | `true` | birthRound=0이고 laneYield<2이면 pocket-eat 예외 허용 | `plan.cpp:1921` |
| `CONV_ON` / `params.hpp:137` | `true` | legacy local conv 조기 feed; SW sf는 이 토글을 읽지 않음 | `plan.cpp:1453` |
| `RAM_SMALL_ON` / `params.hpp:147` | `false` | 작은 조각의 adjacent ram override; 현재 꺼짐 | `plan.cpp:720` |
| `RAM_SMALL_NEED_COLLECTOR` / `params.hpp:152` | `true` | smallRam에 visible collector 요구; 상위 RAM_SMALL_ON=false라 현재 dormant | `plan.cpp:728` |
| `KS_ON` / `params.hpp:158` | `false` | late king threat/deadend 강화·blind 진입 억제; 현재 꺼짐 | `plan.cpp:1318` |
| `FRAG_ON` / `params.hpp:170` | `true` | legacy fragment split 및 youngPiece 20라운드 conv/sf-main 제외 판정 | `plan.cpp:819,1389` |
| `GRAB_ON` / `params.hpp:196` | `true` | death-drop 기록과 source boost; late king 해제는 별도 PT override | `plan.cpp:1321,1325`; `world.cpp:145` |
| `KS2_ON` / `params.hpp:209` | `false` | late king long sprint threat 및 escape trust 우회; 현재 꺼짐 | `plan.cpp:1319` |
| `TG_ON` / `params.hpp:229` | `true` | occupied/vacated-tail와 unseen-length/adjacent pearl을 반영한 enemy reach field; old field도 진단·child safety용 유지 | `plan.cpp:46,54,93,194,802,914,2111,2641` |
| `ESC_SPLIT_ON` / `params.hpp:237` | `false` | short-head cornered 조기 esc-split만 제어; 뒤의 doom escape-split은 별도이며 계속 켜짐 | `plan.cpp:1653` |
| `PX_ON` / `params.hpp:246` | `false` | unseen portal ally crowd / long unprobed penalty; 현재 꺼짐 | `plan.cpp:263,1588,1589,1712,1726,2118` |
| `GX_ON` / `params.hpp:253` | `true` | gather path distance+5가 남은 라운드 이상이면 goal pull 해제 | `plan.cpp:1192`; `ptmod.cpp:120` |
| `SPLIT_TAIL_ON` / `params.hpp:263` | `false` | wantSplit의 별도 tail distance gate와 tag; csplit/sx의 tail safety는 이 토글과 독립 | `plan.cpp:778,2011` |
| `CSPLIT_ON` / `params.hpp:282` | `true` | legacy coverage split; SW sx는 이 토글 대신 cfg.explode를 읽음 | `plan.cpp:868` |
| `FGUARD_ON` / `params.hpp:314` | `true` | legacy F/F2 target; SW sd는 cfg.disperse를 읽음 | `plan.cpp:1010` |
| `COV_ON` / `params.hpp:329` | `true` | 짧은 조각 own-side spawn source의 enemy contest floor .6 | `plan.cpp:356,2039` |
| `NOEXIT_SPARE_ON` / `params.hpp:337` | `true` | no-exit에서 ally head와 같이 죽는 방향 대신 다른 죽는 방향 선택 | `plan.cpp:1962` |
| `MAPID_TAG` / `params.hpp:342` | `true` | 인식 상태가 바뀌면 indicator map tag 출력; 인식 동작 자체는 끄지 않음 | `main.cpp:75` |
| `BSPLIT_ON` / `params.hpp:353` | `true` | Schooltime b legacy early split; 실제 인식 Schooltime은 SW라 현재 정책상 발동 경로 없음 | `plan.cpp:838` |
| `FLOOR_ON` / `params.hpp:382` | `true` | legacy low-unit split; map gate families가 SW라 현재 정책상 발동 경로 없음 | `plan.cpp:958` |
| `KCAP_ON` / `params.hpp:394` | `true` | legacy king-cap split; map gate families가 SW라 현재 정책상 발동 경로 없음 | `plan.cpp:942` |
| `F2_ON` / `params.hpp:415` | `true` | legacy F의 table lookup와 new/held distances; unknown은 observed/symmetry fallback | `plan.cpp:1016,1017,1031,2036` |
| `F2P_ON` / `params.hpp:426` | `false` | live pearl claim을 위해 F goal pull 일시 정지; 현재 꺼짐 | `plan.cpp:362,1075` |
| `CLAIM_ALLY_ON` / `params.hpp:438` | `true` | cl source 강화·긴 아군에게 양보하지 않고 가까운 sibling만 우선; W4 제외 | `plan.cpp:362,377,408,2105` |
| `CLAIM_ENEMY_ON` / `params.hpp:439` | `false` | ce claimed pearl의 enemy contest floor .9; 현재 꺼짐 | `plan.cpp:362,377,415,2106` |
| `PX2_ON` / `params.hpp:452` | `false` | ally에 막힌 dirty probe portal extra를 최소30으로; 현재 꺼짐 | `plan.cpp:1591,2124` |
| `LSPLIT_ON` / `params.hpp:479` | `true` | legacy late L4..6 split, W4 제외; S는 sr가 담당 | `plan.cpp:974` |
| `FRAG_CAP_CSPLIT_ON` / `params.hpp:491` | `true` | legacy frag cap 확대; W4는 fc argument=false로 제외 | `plan.cpp:823` |
| `LNT_ON` / `params.hpp:511` | `true` | trade value의 local veto / optional ram / veto diagnostic; sd vetoAt는 이 토글을 읽지 않음 | `plan.cpp:643,674,695,1577,1614,1740,2060` |
| `LNT_RAM_ON` / `params.hpp:514` | `false` | lnt adjacent offensive ram override; 현재 꺼짐 | `plan.cpp:674` |
| `LNT_KINT_NEED_LONGEST` / `params.hpp:521` | `false` | false면 enemy proven L≥8 모두 veto 예외; true면 teamLongest보다 길어야 함 | `plan.cpp:690` |
| `UTAB_ON` / `params.hpp:532` | `false` | legacy csplit unit target을 layout 표로 교체; 현재 꺼짐 | `plan.cpp:874` |
| `UTAB_PORTALS` / `params.hpp:535` | `false` | utab의 Portals 적용 여부; 현재 UTAB_ON도 false | `plan.cpp:893` |
| `GH_ON` / `params.hpp:568` | `true` | gather hold radius3, longer ally 근처 drop ceding; S는 ghOn=false | `plan.cpp:538,592,1200,2133` |
| `KX_ON` / `params.hpp:572` | `true` | map-gated king-away leaf; S는 kxOn=false | `plan.cpp:1246` |
| `LWK_ON` / `params.hpp:578` | `false` | legacy late feed를 kingLen-2 recipient로 제한; 현재 꺼짐 | `plan.cpp:1496` |
| `SEND_SONAR` / `params.hpp:592` | `true` | main의 SONAR 출력; false여도 Planner 내부 setSonar 계산은 유지 | `main.cpp:56` |
| `INDICATOR` / `params.hpp:593` | `true` | main의 INDICATOR 출력 | `main.cpp:82` |
| `PROFILE` / `params.hpp:594` | `false` | 정상 move에 단계별 CPU point diagnostic 추가; 현재 꺼짐 | `plan.cpp:2175` |
| `ENGINE_TAG` / `params.hpp:600` | `true` | main의 E=F/W/S 출력 | `main.cpp:81` |
| `BELIEF_FIX_ON` / `params.hpp:613` | `true` | 11-bit direct/relay messages, fresh ally 집계, exact/direct length replacement, unified longest reference | `main.cpp:59`; `plan.cpp:774,852,1161,1166,1225,1499,2658`; `ptmod.cpp:90,96`; `world.cpp:122,232,238,403,420,451,469,495,515`; `world.hpp:177,178` |
| `BELIEF_TAG` / `params.hpp:619` | `true` | 5라운드마다 정상 move/HV MOVE에 believed longest와 k0/1 표시 | `plan.cpp:2174,2561` |
| `SWARM_AS_FORTRESS` / `params.hpp:623` | `false` | identity option: SW row도 swarm=false default config; E=S 라벨은 유지 | `policy.hpp:143` |
| `FORT_W4_ON` / `params.hpp:626` | `true` | Autarky/PD a를 MODE1 W4 config로 선택 | `policy.hpp:135` |
| `SD_CONTEST_TIES` / `params.hpp:661` | `false` | front=false일 때만 enemy tie ownership 변경; 현재 false; front=true 경로는 이 값을 건너뜀 | `plan.cpp:2305` |
| `SF_PIECE_BIG_ONLY` / `params.hpp:680` | `true` | sf main의 L≤4도 recipient≥max(L+4,8); late sf branch는 이 조건 우회 가능 | `plan.cpp:1411` |
| `FRONTIER_ON` / `params.hpp:688` | `true` | makeConfig에서 FRONT_POLICY pointer 배정; sd front runtime은 sideChar도 요구 | `policy.hpp:152` |
| `KING_FLOOR_ON` / `params.hpp:694` | `true` | SW config kingFloor 활성; endpoint choice cost | `policy.hpp:153` |
| `KING_BEACON_ON` / `params.hpp:701` | `true` | fresh king metadata와 own beacon / one-shot relay; portal probe는 우선 | `plan.cpp:1131,2166`; `world.cpp:457,464` |
| `BELIEF_LEN_KEEP_ON` / `params.hpp:706` | `true` | C2 partial sighting/relay raise-only; 인식한 non-Portals에서만 active | `world.cpp:113` |
| `PT_ON` / `params.hpp:719` | `true` | Portals family의 MODE3 선택; PT_LEN_ON의 ingest hook와 별개 | `policy.hpp:139` |
| `PT_ENDGAME_ON` / `params.hpp:726` | `true` | computeGoalPt에서 r430 이후 unit/length floors 해제만 제어 | `ptmod.cpp:106` |
| `PT_KING_SAFE_ON` / `params.hpp:734` | `true` | PT king DEAD tile / unprobed unseen crossing prices; PT2 pocket와 독립 | `plan.cpp:607,624`; `ptmod.cpp:55` |
| `PT_PIECE_PORTAL_ON` / `params.hpp:739` | `true` | PT nonking의 unseen exit near fresh king penalty | `ptmod.cpp:62` |
| `PT_LEN_ON` / `params.hpp:745` | `true` | Portals 인식 뒤 ptLenActive를 latch; false가 PT mode 전체를 끄지 않음 | `world.cpp:120` |
| `PT_ENDFEED_ON` / `params.hpp:751` | `true` | PT r430 이후 visible king-class recipient feed의 late timing 우회 | `plan.cpp:1540` |
| `PT_KING_GRAB_ON` / `params.hpp:752` | `true` | PT late king grab source boost 재활성 | `plan.cpp:1325` |
| `PT2_POCKET_ON` / `params.hpp:758` | `true` | PT one-tile POCKET에 every-dragon penalty40; v1.4에는 없음 | `ptmod.cpp:78` |
| `HARVEST_ON` / `params.hpp:769` | `true` | SW Trauma/SF의 cfg.harvest; sd 뒤 pocket plan과 search 전 script RETURN | `policy.hpp:154` |
| `HV2_ON` / `params.hpp:779` | `false` | Trauma cfg.harvestQueue; mouth queue/lease 확대; 현재 꺼짐 | `policy.hpp:155` |
| `KR_ON` / `params.hpp:784` | `false` | nonking king-news relay chain; false는 기존 FORTRESS one-shot relay를 유지 | `plan.cpp:1136` |

## EngineConfig의 runtime switch

FORTRESS_CONFIG는 아래 기본값으로 만들어진다(`engcfg.hpp:53`). policy는 인식 state가 변할 때 config를 재생성한다. 같은 `Planner`의 기존 기억은 유지된다(`policy.hpp:172`, `engine.hpp:16`, `main.cpp:24`).

| field / definition | default F0/W/PT/S values | gate | read sites |
|---|---|---|---|
| `swarm`, `engcfg.hpp:12` | false / false / false / true | MODE2 선택; sonar KR gap; identity false | `plan.cpp:1302,1141,1145` |
| `econW4`, `engcfg.hpp:13` | false / true / false / false | MODE1 선택 | `plan.cpp:1302`; 설정 `policy.hpp:135` |
| `explode`, `engcfg.hpp:15` | false / false / false / true | wantExplode phaseA | `plan.cpp:2605`; 설정 `policy.hpp:146` |
| `resplit`, `engcfg.hpp:18` | false / false / false / true | wantResplit phaseB | `plan.cpp:2619`; 설정 `policy.hpp:147` |
| `resplitNeedDeficit`, `engcfg.hpp:20` | false / false / false / true | sr service deficit; units<8/survive는 예외 | `plan.cpp:2627` |
| `disperse`, `engcfg.hpp:25` | false / false / false / true | sd plan 호출 | `plan.cpp:1369` |
| `claimSonar`, `engcfg.hpp:26` | false / false / false / true | heard hotspot 해제·claim 수신; output target claim | `plan.cpp:1366,1121` |
| `spawnClear`, `engcfg.hpp:27` | false / false / false / true | body spawn clearance soft field | `plan.cpp:1363` |
| `portals`, `engcfg.hpp:29` | false / false / true / false | MODE3 선택 | `plan.cpp:1302`; 설정 `policy.hpp:139` |
| `d8Veto`, `engcfg.hpp:32` | F/W/PT false; S Slithery false, 나머지 true | trade/goal veto의 d3/d8 선택 | `plan.cpp:696,2282,2285`; 값 `policy.hpp:75` |
| `kingFloor`, `engcfg.hpp:35` | false / false / false / true | S king floor field | `plan.cpp:2401`; 설정 `policy.hpp:153` |
| `harvest`, `engcfg.hpp:36` | F/W/PT false; S Trauma/SF true | pocket plan/script | `plan.cpp:1371,1399`; 설정 `policy.hpp:154` |
| `harvestQueue`, `engcfg.hpp:37` | 전 행 false(HV2_ON=false) | occupied pocket 및 claim queue; +20 lease | `plan.cpp:2449,2454,2463,2501`; 설정 `policy.hpp:155` |
| `front` pointer, `engcfg.hpp:34` | F/W/PT nullptr; S FRONT_POLICY 해당 row | frontier deficit/ETA rules; sideChar known 필요 | `plan.cpp:2288,2298`; 설정 `policy.hpp:152` |
| `tag`, `engcfg.hpp:11` | F / W / F / S | 출력 label; 행동 스위치 아님 | `main.cpp:81`; 설정 `policy.hpp:136,142` |
| `convStart`, `engcfg.hpp:22` | F/W/PT default300; S row clock | sf main, sd pull 종료, kingClass, sr survive | `plan.cpp:1403,2250,2372,2394,2623`; 설정 `policy.hpp:150` |
| `broadcastRound`, `engcfg.hpp:23` | F/W/PT300; S1 | sonarAll, SW relay 준비 | `plan.cpp:1123,2568`; 설정 `policy.hpp:150` |
| `curve[5]`, `engcfg.hpp:31` | F/W/PT 모두0; S capped row curve | 실제 sx/sr headsAt 목표 | `engcfg.hpp:45`; `plan.cpp:2606,2625`; 설정 `policy.hpp:148` |
| `headTarget/headTargetB`, `engcfg.hpp:16,19` | F/W/PT0; S row100/250 capped | **값은 설정되나 현재 split에서 직접 읽지 않음** | 설정만 `policy.hpp:146,147`; actual read는 `curve/headsAt` |

`EngineSwarm`은 새 planner를 만들지 않고 같은 planner에 config pointer를 건넨다(`engine.hpp:15`). dispatch 우선순위는 swarm → econW4 → portals → F0이므로 여러 switch가 동시에 true인 외부 config라면 앞 switch가 이긴다. 현재 makeConfig는 이런 중첩을 만들지 않는다(`plan.cpp:1302`, `policy.hpp:130`).

## 정책 행의 머리 곡선과 conversion clock

head curve 순서는 r10 / r25 / r50 / r100 / r250다. 중간은 정수 선형 보간, r10 전 첫 값, r250 뒤 마지막 값이다. S의 각 값은 min(56,unitLimit−8)으로 cap한다(`engcfg.hpp:45`, `policy.hpp:145`). 선언의 splitRateR0_49/.R50_99/childRoomMin/headsR250/kingNewsFresh는 현재 실행에서 읽지 않는다. `headCap=56`만 makeConfig가 소비한다(`policy.hpp:31`, `policy.hpp:145`).

| family/layout | engine/MODE | curve | conv clock | d8Veto | source |
|---|---|---|---|---|---|
| `Autarky/*` | FORTRESS/1 | 0/0/0/0/0 | default300 | false | `policy.hpp:66` |
| `Prisoners_Dilemma/*` | FORTRESS/0 | 0/0/0/0/0 | default300 | false | `policy.hpp:67` |
| `Prisoners_Dilemma/a` | FORTRESS/1 | 0/0/0/0/0 | default300 | false | `policy.hpp:68` |
| `Prisoners_Dilemma/b` | FORTRESS/0 | 0/0/0/0/0 | default300 | false | `policy.hpp:69` |
| `Portals/*` | FORTRESS/3 | 0/0/0/0/0 | default300 | false | `policy.hpp:70` |
| `Trauma/*` | SWARM/2 | 4/4/7/17/38 | 250 | true | `policy.hpp:75` |
| `Slithery_Fight/*` | SWARM/2 | 20/30/45/56/56 | 250 | false | `policy.hpp:76` |
| `Slithery_Fight/a` | SWARM/2 | 20/31/47/56/56 | 250 | false | `policy.hpp:77` |
| `Slithery_Fight/b` | SWARM/2 | 20/30/43/56/56 | 250 | false | `policy.hpp:78` |
| `Schooltime/*` | SWARM/2 | 6/6/10/30/52 | 300 | true | `policy.hpp:79` |
| `Schooltime/a` | SWARM/2 | 6/6/13/45/56 | 250 | true | `policy.hpp:80` |
| `Schooltime/b` | SWARM/2 | 6/6/8/16/49 | 340 | true | `policy.hpp:81` |
| `Default/*` | SWARM/2 | 7/8/11/19/38 | 340 | true | `policy.hpp:82` |
| `Devil/*` | SWARM/2 | 6/8/15/28/37 | 335 | true | `policy.hpp:83` |
| `Devil/a` | SWARM/2 | 6/8/17/31/39 | 340 | true | `policy.hpp:84` |
| `Devil/b` | SWARM/2 | 6/7/12/24/35 | 330 | true | `policy.hpp:85` |
| `Queen_Of_Spades/*` | SWARM/2 | 2/4/7/13/22 | 400 | true | `policy.hpp:86` |
| `Queen_Of_Spades/a` | SWARM/2 | 2/4/7/13/23 | 400 | true | `policy.hpp:87` |
| `Queen_Of_Spades/b` | SWARM/2 | 2/4/7/12/21 | 400 | true | `policy.hpp:88` |
| `Trophy/*` | SWARM/2 | 2/5/15/30/44 | 360 | true | `policy.hpp:89` |
| unknown / no family / map=none | FORTRESS/0 | 0/0/0/0/0 | default300 | false | `policy.hpp:91` |

frontier row별 목표 %는 `policy.hpp:103`의 표와 `EngineConfig.frontShare` 보간으로 정해진다. bool로 켜고 끄는 수치는 아니지만 sd 목표 순위를 직접 바꾸므로 아래 원값을 남긴다. 각 cell은 bin0..4의 %다(`engcfg.hpp:39`, `plan.cpp:2298`).

| family/layout | r25 | r50 | r100 | r250 | source |
|---|---|---|---|---|---|
| `Trauma/*` | 95,5,0,0,0 | 75,25,1,0,0 | 54,22,24,0,0 | 41,22,32,4,1 | `policy.hpp:104` |
| `Slithery_Fight/a` | 55,26,18,1,1 | 49,29,20,2,1 | 51,26,20,2,1 | 51,23,21,3,1 | `policy.hpp:105` |
| `Slithery_Fight/b` | 55,26,18,1,1 | 48,28,21,2,1 | 52,26,19,2,1 | 56,23,17,3,1 | `policy.hpp:106` |
| `Schooltime/a` | 12,28,46,9,5 | 6,16,63,11,4 | 4,11,70,10,4 | 4,10,72,10,4 | `policy.hpp:107` |
| `Schooltime/b` | 10,31,40,13,6 | 8,24,46,16,7 | 6,18,55,15,6 | 5,14,62,14,5 | `policy.hpp:108` |
| `Default/*` | 6,24,54,9,7 | 3,16,65,12,3 | 3,15,65,14,3 | 3,15,63,15,4 | `policy.hpp:109` |
| `Devil/a` | 16,30,54,0,0 | 10,25,58,7,0 | 16,28,42,12,2 | 21,30,32,13,4 | `policy.hpp:110` |
| `Devil/b` | 14,29,56,1,0 | 8,24,60,7,0 | 14,26,44,14,3 | 20,28,33,14,4 | `policy.hpp:111` |
| `Queen_Of_Spades/a` | 5,52,33,7,3 | 7,43,28,17,5 | 8,32,33,21,6 | 8,26,37,21,8 | `policy.hpp:112` |
| `Queen_Of_Spades/b` | 10,49,30,9,2 | 9,43,24,19,6 | 10,33,29,21,8 | 10,25,33,22,9 | `policy.hpp:113` |
| `Trophy/*` | 3,30,55,10,2 | 3,27,51,17,2 | 4,28,40,23,4 | 5,28,36,25,6 | `policy.hpp:114` |
| `Slithery_Fight/*` | 55,26,18,1,1 | 49,29,20,2,1 | 52,26,20,2,1 | 54,23,19,3,1 | `policy.hpp:115` |
| `Schooltime/*` | 11,30,43,11,6 | 7,20,54,13,5 | 5,15,63,13,5 | 4,12,67,12,5 | `policy.hpp:116` |
| `Devil/*` | 15,29,55,1,0 | 9,25,59,7,0 | 15,27,43,13,3 | 20,29,33,14,4 | `policy.hpp:117` |
| `Queen_Of_Spades/*` | 8,51,31,8,2 | 8,43,26,18,5 | 9,32,31,21,7 | 9,26,35,21,8 | `policy.hpp:118` |

## 인스턴스 상수와 v1.4 전용 switches

| selector / definition | values | excluded / gated |
|---|---|---|
| `SW/W4/PT`, `plan.cpp:1307` | MODE0=F/F/F; MODE1=F/T/F; MODE2=T/F/F; MODE3=F/F/T | if constexpr SW는 goals/HV/sf/KF/tags, PT는 module goals/penalties/DFS/tags, W4는 F 제거; compile details `plan.cpp:1358,1375,1377,1398,1774,1819,1848,2145,2167` |
| `SW/W4`, `plan.cpp:328` | computeAttractT의 동일 MODE flags | core2 grab/cl C, W4 cov/claims K exclusion (`plan.cpp:350,356,362,368`) |
| `OPENING_ON`, `v1.4/params.hpp:761` | v1.3 **정의 없음**, v1.4 true | SW opUpdate/leaf/progress/split/tags (`v1.4/plan.cpp:538,1354,1841,1983,2006,2160`) |
| `OP_HOLD_ON`, `v1.4/params.hpp:774` | v1.3 **정의 없음**, v1.4 false | opMidHold/opMidDoom/opMidTag가 if constexpr로 제외 (`v1.4/plan.cpp:1362,1883,2161`; 함수 runtime guard `v1.4/opmod.cpp:147`) |
| `OP_HOLD_ALL`, `v1.4/params.hpp:775` | v1.3 **정의 없음**, v1.4 false | 각본 종료 외 heads도 bin2 hold 허용 (`v1.4/opmod.cpp:155`) |
| `opdb.Script.pull/lossStops`, `v1.4/opdb.hpp:11` | Devil/Trophy/Schooltime T/T; Slithery F/F; Default F/T | waypoint pull 및 unit 감소 stop (`v1.4/opmod.cpp:48,83`; rows `v1.4/opdb.hpp:159`) |

v1.4는 HV/HV2/KR/PT2 토글과 로직을 포함하지 않는 분기다. v1.3 config에 opening을 켤 수 있는 switch가 있다고 가정하지 않는다(`v1.4/params.hpp:755`, `v1.4/policy.hpp:154`, `v1.4/plan.hpp:201`; v1.3 HV는 `params.hpp:769`). 결정 기록의 “개막 계열 중단”과 파일의 `OPENING_ON=true`는 서로 다른 사실이다. 코드는 true로 읽되 qualifier의 v1.3 실행에는 opening이 없다(`DECISIONS.md:86`, `v1.4/params.hpp:761`).

## 남은 tunable / state와 switch의 구별

`SD_MAX_DIST`, `SD_ALLY_STALE`, `SD_FALLBACK_K`, `W_HUNT`는 params에 있으나 v1.3 실행 코드 read가 없다. 값16/3/4/.6과 과거 설명을 현재 알고리즘 gate로 옮기면 안 된다(`params.hpp:651`, `params.hpp:655`, `params.hpp:656`, `params.hpp:89`). 분열의 현재 간격/phase, 목표 거리, feed 문턱 등 숫자 gate는 [flow-swarm.md](flow-swarm.md), [flow-fortress.md](flow-fortress.md), 점수 계수는 [terms.md](terms.md)에 식과 함께 적었다.

`lenKeepActive/ptLenActive`, `mapNone`, `goalOn/fGoal`, `kingSafe`, `hvPhase`, `probeClear`, `opDone/opPull/opMidState` 등은 관측과 실행이 만든 상태이며 설정 토글이 아니다(`world.hpp:121,129,130`, `plan.hpp:48,55,193`, `v1.4/plan.hpp:205,209,223`). `Action.sonarAll`도 결정 결과다(`plan.hpp:19`). 이 표가 모든 `bool` 멤버를 config로 잘못 분류하지 않도록 구분한다.

## v1.6 CONV2 스위치 (`versions/v1.6/bot/params.hpp`, v1.6g)

줄 번호는 `versions/v1.6/bot/`이다. read는 실행 코드만 셌다(주석 제외). 결정 근거는 `versions/v1.6/VERSION.md` §1–9다.

| switch / definition | v1.6g value | gates | read sites(files와 lines) |
|---|---|---|---|
| `CONV2_ON` / `params.hpp:809` | `true` | CONV2 전체: conv2 설정, `decideImpl<4>`·`<5>` 배정, `cvOn()` | `plan.cpp:1304,1306`; `plan.hpp:220`; `policy.hpp:144,162` |
| `CV2_CAND` / `params.hpp:810` | `350` | 선출 이력 단계, 중간(L5–7) 당김 시작, 당김 반경 단계 | `conv2.cpp:74,151,153` |
| `CV2_FREEZE` / `params.hpp:811` | `400` | 큰 것(8–12) 합치기·당김 시작, 이력 단계, r400부터 HV 접근 양보 | `conv2.cpp:74,147,151,153,190` |
| `CV2_H1`, `CV2_H2`/`_DIV`, `CV2_H3`/`_DIV` / `params.hpp:812–814` | `2`, `3`/`5`, `6`/`3` | 현 K를 바꾸는 길이 차이(단계별) | `conv2.cpp:74` |
| `CV2_MARGIN` / `params.hpp:815` | `2` | 조각·중간은 K ≥ L+2에게만 | `conv2.cpp:151,190` |
| `CV2_BIG` / `params.hpp:816` | `8` | 큰 것(합치기)의 길이 | `conv2.cpp:150,189` |
| `CV2_MERGE_SLACK` / `params.hpp:817` | `6` | 큰 것: r + 거리 + L + 6 ≤ 499 | `conv2.cpp:168,207` |
| `CV2_R1/R2/R3` / `params.hpp:818` | `10/16/24` | 당김 반경(r350 전 / r400 전 / 그 뒤) + 소식 나이 | `conv2.cpp:153` |
| `CV2_PULL_FRESH` / `params.hpp:819` | `6` | K 머리 소식이 이보다 오래되면 당기지 않음 | `conv2.cpp:149` |
| `CV2_PULL_W` / `params.hpp:820` | `.3` | 조각·중간의 잎 당김 | `conv2.cpp:171` |
| `CV2_HOLD` / `params.hpp:821` | `3` | 당김 없는 K 곁 거리 | `plan.cpp:541` |
| `CV2_YIELD_R` / `params.hpp:822` | `4` | K 머리 곁 남기기 반경 | `conv2.cpp:100,101` |
| `CV2_FRONT_PEN` / `params.hpp:823` | `2.0` | K 다음 칸 벌점 | `conv2.cpp:111` |
| `CV2_RELAY_K` / `params.hpp:825` | `false` | true면 전달이 이 프로세스의 K를 실음(v1.6). false는 v1.3의 전달 | `conv2.cpp:138,144` |
| `CV2_YIELD_ALL` / `params.hpp:827` | `true` | K 곁의 모든 진주 남기기, 새 드롭 임대 | `conv2.cpp:87,89,103` |
| `CV2_LEASE` / `params.hpp:829` | `12` | 임대 라운드 | `conv2.cpp:104` |
| `CV2_YIELD_PEN` / `params.hpp:830` | `.5` | 남긴 칸 밟기 벌점 | `conv2.cpp:87` |
| `CV2_KING_GRAB` / `params.hpp:831` | `true` | 늦은 왕 grab 유지 | `plan.cpp:1329,1330` |
| `CV2_HV_YIELD` / `params.hpp:832` | `true` | r400부터 주머니 접근이 당김에 양보 | `conv2.cpp:147` |
| `CV2_KMIN` / `params.hpp:833` | `8` | 조각·중간의 받는 쪽 바닥(시동이 아닐 때) | `conv2.cpp:31` |
| `CV2_MERGE_MAX` / `params.hpp:835` | `12` | 합치는 큰 것의 최대 길이 | `conv2.cpp:151,190` |
| `CV2_PORTAL_SAFE` / `params.hpp:836` | `true` | 포털 조심 벌점, 당김 BFS의 포털 제외 | `conv2.cpp:115,161` |
| `CV2_PORTAL_NEAR` / `params.hpp:838` | `2` | 포털 출구와 K 머리의 거리 | `conv2.cpp:116` |
| `CV2_PORTAL_PEN` / `params.hpp:839` | `12.0` | 포털 출구 벌점 | `conv2.cpp:123` |
| `CV2_ALL_SWARM` / `params.hpp:842` | `true` | 모든 떼 행이 conv2. false면 v1.6b의 SE 넷 행 | `policy.hpp:162` |
| `CV2_BOOT_UNITS` / `params.hpp:843` | `12` | 우리 수 ≤ 12면 바닥 0(시동) | `conv2.cpp:31` |
| `CV2_LEN_MEM` / `params.hpp:845` | `true` | C2가 꺼진 프로세스(모르는 지도)의 CONV2 자체 길이 기억 | `conv2.cpp:23,45` |
| `CV2_LEN_MEMORY` / `params.hpp:846` | `20` | 그 기억의 유효 라운드 | `conv2.cpp:25,56` |
| `CV2_PULL_W_BIG` / `params.hpp:848` | `.6` | 큰 것의 잎 당김 | `conv2.cpp:171` |
| `CV2_FORT_ON` / `params.hpp:849` | `false` | 요새 후반 CONV2(`decideImpl<5>`); 꺼짐이면 그 코드가 컴파일에서 빠짐 | `plan.cpp:1306`; `policy.hpp:144` |
| `CV2_FORT_START` / `params.hpp:850` | `400` | 요새 후반 시작 라운드 | `policy.hpp:144` |
| `CV2_EVAL_UNKNOWN_SWARM` / `params.hpp:853` | `false` | 평가 전용: mapNone이면 Unknown 떼 행 | `policy.hpp:172` |
| `CV2_EVAL_MAPID_OFF` / `params.hpp:854` | `false` | 평가 전용: 인식 강제 끔 | `mapid.cpp:48` |
| `CV2_EVIDENCE_LEN` / `params.hpp:856` (v1.6g+H0) | `true` | CONV2의 아군 길이를 minLen(증거)으로 읽음; estLen의 질주 추정(≥ 4) 안 씀 | `conv2.cpp:23,66` |
| `CV2_LEN_CONFIRM` / `params.hpp:858` (v1.6g+H0) | `8` | 8보다 짧게 읽은 길이의 정확한 증거가 8라운드보다 오래됐고 머리가 시야에 있으면 보이는 칸 수로 줄임; 0이면 끔 | `conv2.cpp:24,31` |

`cfg.conv2`, `cfg.cv2Start`, `cfg.fortConv2`(`v1.6/engcfg.hpp:38–40`)는 행에서 만든 설정이다. `cvK_`, `cvPull_`, `cvPullW_`, `cvLen_`(`v1.6/plan.hpp:212–224`)는 차례마다 만드는 상태이며 토글이 아니다.
