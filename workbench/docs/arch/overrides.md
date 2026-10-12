# 선점·취소·대체 지점

기본 `file:line`은 `versions/v1.3/bot/`다. `v1.4/...`만 `versions/v1.4/bot/...`다. “정적 위험”은 코드에서 확인한 우선순위이며, 실제 실패 기록을 찾았다는 뜻이 아니다. 태그 발동과 행동 변경을 구별해야 한다. `F/sd/hva`는 상태이고, 행동은 여러 점수 항 또는 앞선 RETURN으로 결정된다(`plan.cpp:2035`, `plan.cpp:2145`, `plan.cpp:1398`).

## 엔진·세계·길이 기억

| 선점·대체 | 정확한 조건과 영향 | 근거 | 기록된 실패 / 한계 |
|---|---|---|---|
| 정책의 layout → family → DEFAULT | 인식 전 기본 F0; 같은 차례 ingest가 family를 확정하면 바로 해당 엔진. 여러 SW row라도 `SWARM_AS_FORTRESS`면 cfg.swarm=false | `policy.hpp:160`, `policy.hpp:143`, `main.cpp:31`, `main.cpp:42` | unseen maps가 실제 qualifier 대상이라는 결정: `DECISIONS.md:67`. 인식 실패를 SW가 자동 보완하지 않음 |
| SW → W4 → PT → F0 dispatch | enum은 FORTRESS/SWARM 두 개. Portals는 FORTRESS config의 MODE3; engine label은 F | `policy.hpp:24`, `policy.hpp:139`, `plan.cpp:1302`, `main.cpp:81` | label E=F만으로 F0와 PT 구분 불가라는 정적 해석 위험 |
| mapNone latch | 후보 0이면 family/layout를 지우고 이후 update는 즉시 return. 새 관측으로 재인식하지 않음 | `mapid.cpp:57`, `mapid.cpp:69` | 인식 후 모순 때 같은 Planner 기억을 초기화하지 않는 정적 위험; policy만 재생성 `policy.hpp:172` |
| 직접 길이 / 전신이 relay max를 대체 | 전신은 정확 길이로 교체; 직접 보고는 timestamp가 충분히 새로우면 교체. C2 부분 목격·relay는 max 유지 | `world.cpp:232`, `world.cpp:238`, `world.cpp:400`, `world.cpp:420` | C2가 인정된 non-Portals에만 켜지는 범위: `versions/v1.2/VERSION.md:57`. KR 실패에서 실제 왕92를95로 믿은 C2 소식 전파가 원인 후보: `versions/v1.3/VERSION.md:131` |
| fresh 집계가 오래된 아군 제외 | 20라운드 초과 아군은 fresh longest에서 제외; dragon record와 C2 길이를 지우지는 않음 | `world.cpp:455`, `world.hpp:60` | 오래된 높은 길이가 부분 재목격으로 신선해질 수 있다는 정적 위험; 확정된 실측 원인이라고 쓰지 않음 |
| PT length latch | Portals를 한번 인식하면 ptLenActive 유지. 최장 집계의 PT 기억 사용에는 별도 age20 조건 | `world.cpp:120`, `world.cpp:461`, `world.hpp:133` | ptUpdateLens는 저장된 모든 아군을 순회하고 동등 길이도 round를 갱신할 수 있음 `ptmod.cpp:14`, `ptmod.cpp:21`; 실제 head freshness 조건과 함께 읽어야 함 |
| 동률 king | `myLen>=freshAllyLen`이면 여러 드래곤이 동시에 king. SW kingClass는 여기에 L≥8 또는 conv clock 조건 | `world.hpp:178`, `plan.cpp:2394` | 긴 조각이 여러 개일 때 sd/harvest/kingFloor gate가 동시에 달라지는 정적 위험 |

## 목표의 우선순위와 소유권

| 선점·취소 | 실행 의미 | 근거 | 기록된 실패 / 한계 |
|---|---|---|---|
| SW는 중앙 gathering/F/KX/GH를 제외 | relay용 computeGoalSwarm 뒤 sd가 goalDist를 만들고 harvestPlan이 접근 목표를 마지막으로 덮음 | `plan.cpp:1364`, `plan.cpp:1368`, `plan.cpp:1369`, `plan.cpp:1371`, `plan.cpp:2486` | “gh/kx off”라는 과거 설명과 실제 baseline을 구분한 결정: `DECISIONS.md:25`. 현재 F branch에는 그대로 있음 |
| gathering goal이 F 선택 선점 | computeGoal이 goalOn을 켜면 다음 computeFountainGoal이 즉시 return. 두 목표를 함께 합산하지 않으며 leaf는 fGoal에 따라 한 식을 사용. W4는 F를 명시적으로 clear | `plan.cpp:1376`, `plan.cpp:1377`, `plan.cpp:1008`, `plan.cpp:537` | F는 r<340만 활성화되어 정상 gather r340 이후와 주로 시간 분리됨 `plan.cpp:1010`, `plan.cpp:1176` |
| F2 table 결과가 관측·대칭보다 우선 | table 값이 -1이면 observed/mirror fountain 및 strict own-side 대칭 fallback. F2P는 false여서 현재 claim으로 F pull을 pause하지 않음 | `plan.cpp:1016`, `plan.cpp:1017`, `plan.cpp:1075`, `params.hpp:426` | unseen에서는 table F2의 정확한 사전 지식이 없어짐; F 전체가 꺼지는 것은 아님 |
| SW sd king/clock gate | units<3, mapFam/home 미확정, king L≥8, r≥max(convClock,430)이면 target 없음. r≥convClock이면 sdFree는 계산해도 goal pull은 생성하지 않음 | `plan.cpp:2248`, `plan.cpp:2250`, `plan.cpp:2372` | source attraction은 남으므로 conversion clock에 행동이 갑자기 고정되는 것은 아님 |
| sd enemy tie 소유권 | front=false일 때 SD_CONTEST_TIES=false이면 enemy ETA≤mine을 제외. front=true 경로는 별도 ETA+1 규칙으로 그 flag를 건너뜀 | `plan.cpp:2302`, `plan.cpp:2305`, `params.hpp:661` | v1의 symmetric centre 회피와 tie 정책 기록: `DECISIONS.md:49`, `DECISIONS.md:50`, `DECISIONS.md:51` |
| sd ally tie와 claim | fresh ally path/Manhattan tie에서 lower id 우선. older head와 sonar claim도 ETA로 제외; frontier target은 vetoAt면 제외 | `plan.cpp:2307`, `plan.cpp:2309`, `plan.cpp:2314`, `plan.cpp:2316`, `plan.cpp:2321` | 여러 소유권 기준이 함께 작용하므로 한 flag만 바꿔 centre 귀속을 예측하면 안 됨 |
| sd 기존 lease가 새 최적 target을 덮음 | front anchor distance>2이고 취득 후<30이면 hysteresis2로 유지, held best가 있으면 새 best 대신 선택. lease는 4라운드마다 갱신 가능 | `plan.cpp:2335`, `plan.cpp:2336`, `plan.cpp:2366`, `plan.cpp:2368` | weak FG .12로 target은 잡아도 머리 이동이 약했던 기록, .4/commit30 변경: `DECISIONS.md:53`, `DECISIONS.md:55` |
| harvest 접근 목표가 sd를 덮음 | 유효 pocket을 고르면 goalDist=mouth, sdAnchor=entrance, kind=3, bin=-1. 이미 같은 pocket 내부이면 일찍 return하여 그 차례 sd가 만든 goal fields를 재설정하지 않음 | `plan.cpp:2438`, `plan.cpp:2477`, `plan.cpp:2486`, `plan.cpp:2487` | 내부 이동은 harvestTurn이 먼저 선점할 수 있으므로 endpoint score로만 설명 불가 |
| harvest pocket 유지 | 내부 held pocket은 새 food/deadline/claim 검사보다 먼저 유지; 밖의 lease는 ETA+10 동안 유지. HV2 queue 예외는 현재 false | `plan.cpp:2438`, `plan.cpp:2463`, `policy.hpp:155`, `params.hpp:779` | HV2 gate 통과 못함/성능 악화로 최종 false: `versions/v1.3/VERSION.md:196`, `versions/v1.3/VERSION.md:206`, `versions/v1.3/VERSION.md:211` |
| gather recipient의 길이·신선도 우선 | la가 현재 goalLen보다 2 초과 길거나, 길이가 goalLen±2 이상 범위에서 더 신선하면 교체. 엄밀한 전역 최대 길이 argmax가 아님 | `plan.cpp:1173`, `ptmod.cpp:102` | longest라는 이름만으로 누가 goal을 갖는지 예측하면 틀림 |
| GX time gate | gathering distance+5≥남은 round이면 goalOn=false. goalId/goalT 소식은 남을 수 있음 | `plan.cpp:1192`, `ptmod.cpp:120`, `params.hpp:253` | 목표 진단 소식과 이동 pull이 다를 수 있음 |
| source top20이 뒤의 cl 강화 선점 | grab/fountain 적용 후 현재 head 할인값으로 trimming; cl boost/contest는 그 다음이므로 탈락 source를 부활시키지 않음 | `plan.cpp:343`, `plan.cpp:353`, `plan.cpp:387`, `plan.cpp:409` | candidate 이동 점수에 source가 실제 들어가는지 확인 필요 |
| gh와 claims가 pearl attraction 수정 | gh drop은 grab 취소·즉시 p×.15; cl은 long ally 양보 대신 sibling 거리 사용; SW takeClaims는 hotspot source를 지움 | `plan.cpp:351`, `plan.cpp:413`, `plan.cpp:1219`, `plan.cpp:2228` | 새 goal pull과 실제 food attraction이 서로 다른 층이라는 정적 위험 |

## 조기 RETURN과 split 우선순위

다음 순서는 실제 함수 실행 순서다. PT는 이 사슬의 별도 RETURN이 아니라 goal/feed/candidate/DFS hook이다(`plan.cpp:1375`, `plan.cpp:1540`, `plan.cpp:1774`, `plan.cpp:1819`).

| 순서 / 선점 규칙 | 무엇을 건너뛰는가 / gate | 근거 |
|---|---|---|
| 1 degraded MOVE | input/head/map storage가 유효하지 않으면 field/goal/search/split 전부 생략 | `plan.cpp:1328`, `plan.cpp:1335` |
| 2 SW harvestTurn | script MOVE 또는 hvs SPLIT 성공이면 sf/search/doom/sx/sr 생략. 내부 BFS는 food 먼저, threat/areaSafety 점수 비교 없이 실행 | `plan.cpp:1398`, `plan.cpp:2511`, `plan.cpp:2530`, `plan.cpp:2556` |
| 3 SW sf feed | recipient과 timing gate 통과 후 pickup queue<2이면 neck MOVE. queue≥2면 hold하며 이후 search 진행; 별도 hold RETURN 없음 | `plan.cpp:1402`, `plan.cpp:1441`, `plan.cpp:1443` |
| 4 non-SW local conv | youngPiece가 아니고 L≤4/r≥300 등 gate와 visible recipient 있으면 neck MOVE | `plan.cpp:1453`, `plan.cpp:1478` |
| 5 non-SW gathering / late feed | gather floor 또는 lateWindow 또는 PT endfeed이면 neck MOVE. PT r430 endfeed는 일반 lateWindow를 우회 | `plan.cpp:1490`, `plan.cpp:1536`, `plan.cpp:1540`, `plan.cpp:1541`, `plan.cpp:1547` |
| 6 short-head esc-split | 후보 생성 도중 cornered-tail gate지만 ESC_SPLIT_ON=false라 현재 비활성 | `plan.cpp:1653`, `plan.cpp:1687`, `params.hpp:237` |
| 7 doom pocket-eat | 탐색 후 raw doom 판정; 마지막 pearl MOVE가 doom escape split을 한 차례 유예 | `plan.cpp:1873`, `plan.cpp:1922`, `plan.cpp:1938` |
| 8 doom escape-split | splittable/childCanMove면 SPLIT L−2; ESC_SPLIT_ON=false와 독립 | `plan.cpp:1890`, `plan.cpp:1945`, `plan.cpp:1951` |
| 9 last-trade / no-exit | best<0이면 인접 enemy head 첫 방향으로 MOVE: **tradeValue/lntVeto를 다시 검사하지 않음**. 없으면 no-exit action | `plan.cpp:1954`, `plan.cpp:1956`, `plan.cpp:1962`, `plan.cpp:1972` |
| 10 일반 split 사슬 | 선택 후보 trade/blind면 검사 생략. SW sx→sr; F0/PT wantSplit→frag→bsp→csplit→kcap→floor→lsplit; W4는 wantSplit/frag/bsp까지만 | `plan.cpp:1987`, `plan.cpp:1988`, `plan.cpp:1990` |
| 11 일반 split urgency | p≥.5, 선택 경로 threat>0, safety≤−1, head enemy distance≤2 중 하나면 split 취소. 앞 true rule 다음 rule 재시도 없음 | `plan.cpp:1991`, `plan.cpp:1993`, `plan.cpp:2014` |
| 12 정상 MOVE | 선택 raw score와 진단 tag; 공통 output으로 이동 | `plan.cpp:2024`, `plan.cpp:2031`, `plan.cpp:2181` |

harvest script가 area penalty를 건너뛰는 것은 pocket 수확을 위한 의도된 구조다(`versions/v1.3/VERSION.md:43`). sf youngPiece 예외·bigger recipient·pickup queue는 feed 수를 줄인 변경으로 기록돼 있다(`versions/v1.2/VERSION.md:147`). 이 기록은 v1.3의 모든 map에서 개선을 보장하지 않는다.

## 값·선택·출력에서의 대체

| 선점·취소 | 정확한 영향 | 근거 | 해석 위험 |
|---|---|---|---|
| trade veto가 terminal 값을 제거 | positive trade라도 lnt veto면0 → legal=false. kint enemy≥8 예외와 r495 해제가 있음 | `plan.cpp:637`, `plan.cpp:647`, `plan.cpp:690`, `plan.cpp:695`, `plan.cpp:1574` | sd/hold의 vetoAt는 별도 함수이며 kint/r495/LNT_ON 예외가 없음 `plan.cpp:2279` |
| TG가 구 enemy field 대체 | threatAt는 TG reach 사용; old field는 child-safe/room용 유지 | `plan.cpp:43`, `plan.cpp:194`, `plan.cpp:802`, `plan.cpp:2641` | TG 때문에 T1=0이라는 과거 해석이 틀렸음을 수정한 기록: `versions/v1.4/VERSION.md:252`, `versions/v1.4/VERSION.md:262` |
| sprint가 single 비용식 대체 | regular2/escape2/escape3는 별도 base 식. 첫 칸의 모든 single penalties를 누적하지 않음 | `plan.cpp:1625`, `plan.cpp:1711`, `plan.cpp:1725` | 단계별 비용을 그냥 합산하면 candidate 순위 틀림 |
| PT pocket/DEAD가 move 가격을 크게 변경 | 현재 step당 pocket−40, king DEAD−40. PT dfs에는 pocket/DEAD가 있으나 crossing−12 전체를 재호출하지 않음 | `ptmod.cpp:55`, `ptmod.cpp:78`, `plan.cpp:621`, `plan.cpp:624` | PT tag는 losing candidate의 pricing으로도 켜짐 |
| blind safety가 ordinary max로 대체 | 실제 exit를 flood하지 않고 ordinary safety 최대 사용. clean voluntary blind value는 bestOrd+blindBase−.5 이상으로 올림 | `plan.cpp:1793`, `plan.cpp:1837` | “portal 위험이 커서 안 갈 것”이라는 단순 가산 비교로 설명 불가 |
| timeout depth 폐기 | soft/hard budget에 걸린 iteration의 부분 값 전체 버리고 마지막 완료 depth 사용 | `plan.cpp:1810`, `plan.cpp:1822`, `plan.cpp:1824` | 어떤 candidate가 깊게 계산됐는지만으로 final value 설명 불가 |
| kingFloor가 raw winner 대체 | SW best와 bestSingle은 value−endpoint cost로 선택. doom은 raw, indicator v도 raw | `plan.cpp:1848`, `plan.cpp:1850`, `plan.cpp:1873`, `plan.cpp:2031` | d3→d4 cost 차18이 goal 한 칸 .4를 압도 `plan.cpp:2423` |
| deterministic tie-break | jitter≤.002를 더한 뒤 strict >; 완전 동률이면 먼저 생성한 candidate. dirs loop N/E/S/W 각 방향 single 직후 그 방향의 2-step들을 추가; escape/kill은 이 루프 뒤에 추가 | `plan.cpp:1559`, `plan.cpp:1696`, `plan.cpp:1736`, `plan.cpp:1841`, `plan.cpp:1853` | map symmetry가 동일 순위를 보장하지 않음; id-dependent jitter |
| main fallback와 split legality | 먼저 safeDir fallback MOVE 출력 후 intended MOVE/유효 SPLIT 출력. SPLIT legality 실패는 fallback 또는 forward MOVE로 남음 | `main.cpp:47`, `main.cpp:49`, `main.cpp:51` | indicator가 SPLIT을 계획한 흔적이어도 실제 출력 legality 확인 필요 |
| sonar probe가 broadcast/king beacon 선점 | single portal probe면 setSonar beacon 분기에서 즉시 return. 일반 sonarAll는 cfg.broadcastRound 이후, king beacon는 r%8=0; 아군 goal relay도 별도 | `plan.cpp:1092`, `plan.cpp:1123`, `plan.cpp:1125`, `plan.cpp:1133`, `plan.cpp:1135` | portal probe 차례에는 왕 소식의 네 방향 beacon을 보내지 않음 |
| escaped stub / youngPiece가 feed 지연 | escSplitRound 후 3라운드 이내는 conv 및 sf main 제외; born child≤2의 첫20라운드도 제외. sf lateWin은 이를 우회 가능 | `plan.cpp:1389`, `plan.cpp:1403`, `plan.cpp:1404`, `plan.cpp:1454` | split 직후 feed가 바로 작동한다고 볼 수 없음 |
| post-action sonar 길이 | SPLIT/MOVE/추정 food에 맞춰 보낼 길이·head 좌표를 계산. relay 우선; map/engine tag는 모든 early RETURN 뒤에도 붙음 | `main.cpp:58`, `main.cpp:62`, `main.cpp:66`, `main.cpp:75`, `main.cpp:81` | feed early RETURN은 setSonar 없음. 정상 tag 조립을 건너뛴 action에는 일부 태그도 없음 `plan.cpp:1448` |

## v1.4 opening / hold의 우선순위

**v1.3에는 opening이 없고, v1.4에는 v1.3 HV/PT2가 없다.** 따라서 검토 대상인 v1.3/v1.4 각각의 실행 경로에는 “harvest → opening split 선점”이 없다. 두 분기 hook 위치를 그대로 합치는 경우에만 HV RETURN이 opWantSplit보다 먼저인 구조가 된다(`plan.cpp:1398`, `v1.4/plan.cpp:1983`, `v1.4/policy.hpp:154`).

| 선점·취소 | v1.4 실제 코드 | 기록된 실패 / 상태 |
|---|---|---|
| layout 미확정·birth role 우선 | layout ?에서 a script를 조회; role은 birthRound/birthLen/home 좌표로만 매치하며 Script의 side/team 필드를 매치 조건에 읽지 않음. scripted family에서 role 없으면 n으로 영구 hand-off | `v1.4/opmod.cpp:28`, `v1.4/opmod.cpp:36`, `v1.4/opmod.cpp:41` |
| opDone latch | stop 이유 n/e/c/u/b/l/a가 생기면 이후 opUpdate는 재시작하지 않음. 아직 family 미확정이면 return만 하고 retry 가능 | `v1.4/opmod.cpp:20`, `v1.4/opmod.cpp:27`, `v1.4/opmod.cpp:46`, `v1.4/opmod.cpp:81` |
| opPull이 기존 sd pull 대체 | DFS leaf if opPull이면 opLeaf=true, 다음 goal if 제외. OP_W=1, hold0 | `v1.4/plan.cpp:538`, `v1.4/params.hpp:762`; 근접 waypoint에 모든 첫 수가 도달해 차이 없어졌던 실패 `versions/v1.4/VERSION.md:95` |
| OP_STEP이 winner 변경 | cv에 진행 방향 +2/정지0/후퇴−2; raw value는 바꾸지 않음 | `v1.4/plan.cpp:1841`, `v1.4/plan.cpp:1843`; 앞 waypoint/step 수정 `versions/v1.4/VERSION.md:97` |
| opWantSplit 먼저 | scheduled split이 먼저; active pull이면 opHoldSplits가 sx/sr를 막음. urgency gate는 여전히 최종 적용 | `v1.4/plan.cpp:1983`, `v1.4/opmod.cpp:90`, `v1.4/opmod.cpp:112` |
| hand-off 뒤 sd 복귀 | opening 완료 후 opPull 해제, 기존 sd 선택이 centre에서 철수 가능 | `v1.4/opmod.cpp:18`, `v1.4/opmod.cpp:76`, `v1.4/plan.cpp:1361`; Devil r50 centre7.2% 기록 `versions/v1.4/VERSION.md:265` |
| optional opMidHold가 sd goal 대체 | sd 뒤 held bin2 goal/anchor overwrite; ally ownership/enemy ETA 검사 대신 yield·veto 사용. hold flags 모두 false여서 현재 compiled out | `v1.4/plan.cpp:1362`, `v1.4/opmod.cpp:198`, `v1.4/opmod.cpp:213`, `v1.4/params.hpp:774` |
| trade veto가 hold 종료 | head veto는 v로 hold 종료. target veto는 기존 target을 무효화하고 다른 target을 찾으며, 모두 배제되면 x로 종료. king/r>100/doom도 종료. opMidDoom은 이미 계산된 그 차례 goal fields를 지우지는 않음 | `v1.4/opmod.cpp:173`, `v1.4/opmod.cpp:209`, `v1.4/opmod.cpp:235`; Devil r34 veto/r29 doom과 낮은 heads 원인 기록 `versions/v1.4/VERSION.md:348`, `versions/v1.4/VERSION.md:380` |
| 문서의 실험 중단 ≠ code switch off | 결정문은 opening line 중단, 코드 OPENING_ON=true/OP_HOLD_ON=false. 코드 결과와 채택 결정을 별개로 봄 | `DECISIONS.md:81`, `DECISIONS.md:86`, `v1.4/params.hpp:761`, `v1.4/params.hpp:774` |

## 호출 교차 확인 부록

아래 목록은 관련 source에서 함수 이름을 `rg`로 다시 조회한 위치다. 동명이름인 `std::fill` 등 비관련 조회도 포함되며, 실제 caller는 코드 문맥으로 구분했다. 정의·선언도 포함하여 호출 누락을 찾는 용도로 사용한다. 제시한 엔진별 실제 호출 해석은 위 표와 flow 문서에 있다.

정의 181개(오버로드 포함)를 확인했다. source 밖 runtime이 호출하는 main, 테스트 helper, 선언만 있는 함수는 실행 경로와 구분한다.

| 함수 / 정의 | 이름 조회 위치(정의·선언·호출) |
|---|---|
| `World::ptUpdateLens` / `ptmod.cpp:14` | `world.cpp:121`, `ptmod.cpp:14`, `world.hpp:132` |
| `Planner::ptExit` / `ptmod.cpp:35` | `ptmod.cpp:35`, `ptmod.cpp:51`, `plan.hpp:202`, `plan.cpp:607`, `plan.cpp:608` |
| `Planner::ptKingTilePen` / `ptmod.cpp:40` | `plan.hpp:203`, `plan.cpp:607`, `plan.cpp:624`, `ptmod.cpp:40` |
| `Planner::ptStepPenalty` / `ptmod.cpp:48` | `plan.hpp:204`, `plan.cpp:1777`, `plan.cpp:1779`, `ptmod.cpp:48` |
| `Planner::ptTilePen2` / `ptmod.cpp:77` | `plan.hpp:208`, `ptmod.cpp:54`, `ptmod.cpp:77`, `plan.cpp:608`, `plan.cpp:625` |
| `Planner::computeGoalPt` / `ptmod.cpp:85` | `plan.hpp:206`, `ptmod.cpp:85`, `plan.cpp:1375` |
| `nowPoints` / `plan.cpp:18` | `plan.hpp:211`, `plan.cpp:18`, `plan.cpp:530`, `plan.cpp:583`, `plan.cpp:1313`, `plan.cpp:1353`, `plan.cpp:1355`, `plan.cpp:1381`, `plan.cpp:1803`, `plan.cpp:1810`, `plan.cpp:1822`, `plan.cpp:1827`, `plan.cpp:2176` |
| `initGpow` / `plan.cpp:27` | `plan.cpp:27`, `plan.cpp:1308` |
| `mix32` / `plan.cpp:33` | `plan.cpp:33`, `plan.cpp:1842` |
| `Planner::computeEnemyDistance` / `plan.cpp:43` | `plan.hpp:92`, `plan.cpp:43`, `plan.cpp:1354` |
| `Planner::computeSoftPenalty` / `plan.cpp:161` | `plan.hpp:94`, `plan.cpp:161`, `plan.cpp:1357` |
| `Planner::threatAt` / `plan.cpp:190` | `plan.hpp:99`, `plan.cpp:190`, `plan.cpp:565`, `plan.cpp:621`, `plan.cpp:1598`, `plan.cpp:1618`, `plan.cpp:1640`, `plan.cpp:1641`, `plan.cpp:1709`, `plan.cpp:1719`, `plan.cpp:1932`, `plan.cpp:1992`, `plan.cpp:2020`, `plan.cpp:2112`, `plan.cpp:2556` |
| `Planner::ks2Threat` / `plan.cpp:198` | `plan.hpp:101`, `plan.cpp:192`, `plan.cpp:198`, `plan.cpp:210` |
| `Planner::threatAtOld` / `plan.cpp:208` | `plan.hpp:100`, `plan.cpp:208`, `plan.cpp:2112` |
| `Planner::threatCore` / `plan.cpp:216` | `plan.hpp:102`, `plan.cpp:194`, `plan.cpp:212`, `plan.cpp:216` |
| `Planner::exploreValue` / `plan.cpp:234` | `plan.hpp:103`, `plan.cpp:234`, `plan.cpp:532`, `plan.cpp:586` |
| `Planner::portalPenalty` / `plan.cpp:251` | `plan.hpp:104`, `plan.cpp:251`, `plan.cpp:279`, `plan.cpp:565`, `plan.cpp:621`, `plan.cpp:1599`, `plan.cpp:1625`, `plan.cpp:1627`, `plan.cpp:1711`, `plan.cpp:1725` |
| `Planner::pxPenalty` / `plan.cpp:272` | `plan.hpp:105`, `plan.cpp:263`, `plan.cpp:272`, `plan.cpp:1589`, `plan.cpp:1712`, `plan.cpp:1726` |
| `Planner::computeFrontier` / `plan.cpp:288` | `plan.hpp:96`, `plan.cpp:288`, `plan.cpp:1356` |
| `Planner::frontierValue` / `plan.cpp:314` | `plan.hpp:97`, `plan.cpp:314`, `plan.cpp:445`, `plan.cpp:549`, `plan.cpp:603`, `plan.cpp:1100`, `plan.cpp:1566` |
| `Planner::blindRisk` / `plan.cpp:322` | `plan.hpp:98`, `plan.cpp:322`, `plan.cpp:552`, `plan.cpp:606`, `plan.cpp:1568` |
| `Planner::computeAttractT` / `plan.cpp:327` | `plan.hpp:93`, `plan.cpp:327`, `plan.cpp:1367`, `plan.cpp:1374` |
| `Planner::tileEnterable` / `plan.cpp:472` | `plan.hpp:108`, `plan.cpp:472`, `plan.cpp:535`, `plan.cpp:558`, `plan.cpp:589`, `plan.cpp:614`, `plan.cpp:1594`, `plan.cpp:1621`, `plan.cpp:1706`, `plan.cpp:1721`, `plan.cpp:1883`, `plan.cpp:2547`, `plan.cpp:2555` |
| `Planner::areaSafety` / `plan.cpp:481` | `plan.hpp:106`, `plan.cpp:481`, `plan.cpp:1789` |
| `Planner::dfs` / `plan.cpp:526` | `plan.hpp:107`, `plan.cpp:526`, `plan.cpp:570`, `plan.cpp:1820` |
| `Planner::dfsPt` / `plan.cpp:579` | `plan.hpp:205`, `plan.cpp:579`, `plan.cpp:628`, `plan.cpp:1819` |
| `Planner::tradeValue` / `plan.cpp:637` | `plan.hpp:109`, `plan.cpp:382`, `plan.cpp:637`, `plan.cpp:1575`, `plan.cpp:1612`, `plan.cpp:1739` |
| `Planner::tradeValuePreVeto` / `plan.cpp:653` | `plan.hpp:139`, `plan.cpp:653`, `plan.cpp:1577`, `plan.cpp:1614`, `plan.cpp:1740`, `plan.cpp:2064` |
| `Planner::lntD3` / `plan.cpp:664` | `plan.hpp:134`, `plan.cpp:664`, `plan.cpp:682`, `plan.cpp:697`, `plan.cpp:715`, `plan.cpp:2064`, `plan.cpp:2065` |
| `Planner::lntRam` / `plan.cpp:673` | `plan.hpp:135`, `plan.cpp:644`, `plan.cpp:673`, `plan.cpp:2063` |
| `Planner::lntKint` / `plan.cpp:686` | `plan.hpp:136`, `plan.cpp:686`, `plan.cpp:696`, `plan.cpp:697`, `plan.cpp:2065` |
| `Planner::lntVeto` / `plan.cpp:694` | `plan.hpp:137`, `plan.cpp:647`, `plan.cpp:694` |
| `Planner::lntD8` / `plan.cpp:702` | `plan.hpp:138`, `plan.cpp:696`, `plan.cpp:702` |
| `Planner::lntVetoNote` / `plan.cpp:713` | `plan.hpp:140`, `plan.cpp:713`, `plan.cpp:1577`, `plan.cpp:1614`, `plan.cpp:1765` |
| `Planner::smallRam` / `plan.cpp:719` | `plan.hpp:111`, `plan.cpp:639`, `plan.cpp:655`, `plan.cpp:719`, `plan.cpp:2051` |
| `Planner::tradeValueBase` / `plan.cpp:736` | `plan.hpp:110`, `plan.cpp:638`, `plan.cpp:654`, `plan.cpp:736`, `plan.cpp:2052` |
| `Planner::wantSplit` / `plan.cpp:759` | `plan.hpp:112`, `plan.cpp:759`, `plan.cpp:1989` |
| `Planner::childSafe` / `plan.cpp:790` | `plan.hpp:113`, `plan.hpp:116`, `params.hpp:296`, `plan.cpp:778`, `plan.cpp:779`, `plan.cpp:783`, `plan.cpp:790`, `plan.cpp:831`, `plan.cpp:843`, `plan.cpp:914` |
| `Planner::wantFrag` / `plan.cpp:817` | `plan.hpp:114`, `plan.cpp:817`, `plan.cpp:1989` |
| `Planner::wantBSplit` / `plan.cpp:837` | `plan.hpp:118`, `plan.cpp:837`, `plan.cpp:1989` |
| `Planner::longerAllyKnown` / `plan.cpp:851` | `plan.hpp:125`, `plan.cpp:828`, `plan.cpp:851`, `plan.cpp:877`, `plan.cpp:961`, `plan.cpp:979` |
| `Planner::wantCsplit` / `plan.cpp:867` | `plan.hpp:115`, `plan.cpp:867`, `plan.cpp:1989` |
| `Planner::utabTarget` / `plan.cpp:892` | `plan.hpp:141`, `plan.cpp:874`, `plan.cpp:892` |
| `Planner::csplitChildSafe` / `plan.cpp:903` | `plan.hpp:116`, `plan.cpp:880`, `plan.cpp:903`, `plan.cpp:948`, `plan.cpp:965`, `plan.cpp:982`, `plan.cpp:2612`, `plan.cpp:2630` |
| `Planner::floorMapOn` / `plan.cpp:930` | `plan.hpp:121`, `plan.cpp:930`, `plan.cpp:935`, `plan.cpp:962` |
| `Planner::kcapMapOn` / `plan.cpp:935` | `plan.hpp:122`, `plan.cpp:935`, `plan.cpp:945` |
| `Planner::wantKcap` / `plan.cpp:941` | `plan.hpp:119`, `plan.cpp:941`, `plan.cpp:1990` |
| `Planner::wantFloor` / `plan.cpp:957` | `plan.hpp:120`, `plan.cpp:957`, `plan.cpp:1990` |
| `Planner::wantLsplit` / `plan.cpp:973` | `plan.hpp:123`, `plan.cpp:973`, `plan.cpp:1990` |
| `Planner::ourSide` / `plan.cpp:988` | `plan.hpp:81`, `plan.hpp:124`, `plan.cpp:988`, `plan.cpp:1000`, `plan.cpp:1017` |
| `Planner::covSide` / `plan.cpp:997` | `plan.hpp:124`, `plan.cpp:356`, `plan.cpp:997`, `plan.cpp:2039` |
| `Planner::computeFountainGoal` / `plan.cpp:1008` | `plan.hpp:117`, `plan.cpp:1008`, `plan.cpp:1378` |
| `Planner::freshDrop` / `plan.cpp:1084` | `plan.hpp:126`, `plan.cpp:349`, `plan.cpp:367`, `plan.cpp:1084`, `plan.cpp:1212` |
| `Planner::pickSonarDir` / `plan.cpp:1092` | `plan.hpp:127`, `plan.cpp:1092`, `plan.cpp:1119` |
| `Planner::setSonar` / `plan.cpp:1112` | `plan.hpp:128`, `plan.cpp:1112`, `plan.cpp:1689`, `plan.cpp:1939`, `plan.cpp:1948`, `plan.cpp:2000`, `plan.cpp:2029`, `plan.cpp:2531`, `plan.cpp:2558` |
| `Planner::computeGoal` / `plan.cpp:1155` | `plan.hpp:95`, `plan.cpp:1155`, `plan.cpp:1376` |
| `Planner::computeGhDrops` / `plan.cpp:1197` | `plan.hpp:150`, `plan.cpp:1197`, `plan.cpp:1373` |
| `Planner::pearlValue` / `plan.cpp:1219` | `plan.hpp:154`, `plan.cpp:565`, `plan.cpp:621`, `plan.cpp:1219`, `plan.cpp:1599`, `plan.cpp:1625`, `plan.cpp:1711`, `plan.cpp:1725` |
| `Planner::kingFresh` / `plan.cpp:1224` | `plan.hpp:152`, `plan.cpp:1224`, `plan.cpp:1246` |
| `Planner::kxMapOn` / `plan.cpp:1235` | `plan.hpp:153`, `plan.cpp:1235`, `plan.cpp:1246` |
| `Planner::computeKingAway` / `plan.cpp:1244` | `plan.hpp:151`, `plan.cpp:1244`, `plan.cpp:1379` |
| `Planner::pickHotspot` / `plan.cpp:1266` | `plan.hpp:129`, `plan.cpp:1121`, `plan.cpp:1266` |
| `Planner::exactlyExposed` / `plan.cpp:1275` | `plan.hpp:52`, `plan.cpp:1275`, `plan.cpp:2025` |
| `Planner::decide` / `plan.cpp:1302` | `plan.hpp:30`, `main.cpp:44`, `main.cpp:45`, `engcfg.hpp:12`, `plan.cpp:1302`, `engine.hpp:16` |
| `Planner::decideImpl` / `plan.cpp:1306` | `plan.hpp:39`, `plan.cpp:1302`, `plan.cpp:1306` |
| `Planner::updateSide` / `plan.cpp:2189` | `plan.hpp:177`, `plan.cpp:1362`, `plan.cpp:2189`, `plan.cpp:2586` |
| `Planner::sideOf` / `plan.cpp:2202` | `plan.hpp:178`, `plan.cpp:356`, `plan.cpp:2202`, `plan.cpp:2596` |
| `Planner::takeClaims` / `plan.cpp:2211` | `plan.hpp:175`, `plan.cpp:1366`, `plan.cpp:2211` |
| `Planner::computeDisperseGoal` / `plan.cpp:2248` | `plan.hpp:173`, `plan.cpp:1369`, `plan.cpp:2248` |
| `Planner::kingClass` / `plan.cpp:2394` | `plan.hpp:189`, `plan.cpp:2164`, `plan.cpp:2394`, `plan.cpp:2401`, `plan.cpp:2436` |
| `Planner::computeKingFloor` / `plan.cpp:2399` | `plan.hpp:190`, `plan.cpp:1370`, `plan.cpp:2399` |
| `Planner::kingFloorCost` / `plan.cpp:2423` | `plan.hpp:191`, `plan.cpp:1848`, `plan.cpp:1850`, `plan.cpp:2423` |
| `Planner::harvestPlan` / `plan.cpp:2434` | `plan.hpp:196`, `plan.cpp:1371`, `plan.cpp:2434` |
| `Planner::harvestTurn` / `plan.cpp:2495` | `plan.hpp:197`, `plan.cpp:1399`, `plan.cpp:2495` |
| `Planner::computeGoalSwarm` / `plan.cpp:2566` | `plan.hpp:174`, `plan.cpp:1368`, `plan.cpp:2566` |
| `Planner::addSpawnClear` / `plan.cpp:2581` | `plan.hpp:176`, `plan.cpp:1363`, `plan.cpp:2581` |
| `Planner::wantExplode` / `plan.cpp:2604` | `plan.hpp:170`, `plan.cpp:1988`, `plan.cpp:2604` |
| `Planner::wantResplit` / `plan.cpp:2618` | `plan.hpp:171`, `plan.cpp:1988`, `plan.cpp:2618` |
| `Planner::roomOk` / `plan.cpp:2636` | `plan.cpp:2612`, `plan.cpp:2630`, `plan.cpp:2636`, `plan.hpp:172` |
| `Planner::beliefTag` / `plan.cpp:2656` | `plan.hpp:179`, `plan.cpp:2174`, `plan.cpp:2561`, `plan.cpp:2656` |
| `Reader::fill` / `proto.cpp:19` | `world.cpp:280`, `world.cpp:281`, `world.cpp:282`, `proto.hpp:65`, `proto.cpp:19`, `proto.cpp:42`, `plan.cpp:69`, `plan.cpp:120`, `plan.cpp:399`, `plan.cpp:450`, `plan.cpp:485`, `plan.cpp:1415`, `plan.cpp:1461`, `plan.cpp:1519`, `plan.cpp:1743`, `plan.cpp:2074`, `plan.cpp:2093`, `plan.cpp:2507` |
| `Reader::nextLine` / `proto.cpp:35` | `proto.hpp:67`, `proto.cpp:35`, `proto.cpp:65`, `proto.cpp:96`, `proto.cpp:114`, `proto.cpp:120`, `proto.cpp:123`, `proto.cpp:131`, `proto.cpp:135`, `proto.cpp:141`, `proto.cpp:144`, `proto.cpp:155`, `proto.cpp:165`, `proto.cpp:169` |
| `Reader::peekLine` / `proto.cpp:64` | `proto.hpp:68`, `proto.cpp:64`, `proto.cpp:93` |
| `toInt` / `proto.cpp:69` | `proto.cpp:69`, `proto.cpp:85`, `proto.cpp:97`, `proto.cpp:99`, `proto.cpp:100`, `proto.cpp:118`, `proto.cpp:121`, `proto.cpp:139`, `proto.cpp:148`, `proto.cpp:159` |
| `toU64` / `proto.cpp:75` | `proto.cpp:75`, `proto.cpp:132` |
| `edgeTok` / `proto.cpp:82` | `proto.cpp:82`, `proto.cpp:166`, `proto.cpp:170` |
| `Reader::readInit` / `proto.cpp:89` | `main.cpp:21`, `proto.hpp:58`, `proto.cpp:89` |
| `Reader::readRound` / `proto.cpp:109` | `main.cpp:30`, `proto.hpp:60`, `proto.cpp:109` |
| `Writer::endTurn` / `proto.cpp:176` | `main.cpp:83`, `proto.hpp:82`, `proto.cpp:176` |
| `World::init` / `world.cpp:23` | `main.cpp:23`, `world.cpp:23`, `world.hpp:159` |
| `World::mirrorTile` / `world.cpp:39` | `world.cpp:39`, `world.cpp:314`, `world.cpp:353`, `world.cpp:369`, `world.cpp:430`, `plan.cpp:990`, `plan.cpp:1014`, `world.hpp:169` |
| `World::mirrorDir` / `world.cpp:47` | `world.cpp:47`, `world.cpp:319`, `world.cpp:353`, `world.cpp:373`, `world.hpp:170` |
| `World::canonicalPortalEnd` / `world.cpp:55` | `world.cpp:55`, `world.cpp:69`, `world.cpp:85`, `world.cpp:354`, `world.hpp:202` |
| `World::setEdge` / `world.cpp:62` | `world.cpp:62`, `world.cpp:179`, `world.cpp:180`, `world.cpp:181`, `world.cpp:182`, `world.hpp:182`, `world.hpp:192` |
| `World::across` / `world.cpp:76` | `world.hpp:164`, `world.cpp:76`, `world.cpp:269`, `world.cpp:297`, `plan.cpp:78`, `plan.cpp:104`, `plan.cpp:117`, `plan.cpp:128`, `plan.cpp:150`, `plan.cpp:169`, `plan.cpp:182`, `plan.cpp:297`, `plan.cpp:307`, `plan.cpp:317`, `plan.cpp:431`, `plan.cpp:459`, `plan.cpp:495`, `plan.cpp:535`, `plan.cpp:547`, `plan.cpp:589`, `plan.cpp:601`, `plan.cpp:681`, `plan.cpp:726`, `plan.cpp:806`, `plan.cpp:912`, `plan.cpp:917`, `plan.cpp:1068`, `plan.cpp:1098`, `plan.cpp:1184`, `plan.cpp:1258`, `plan.cpp:1288`, `plan.cpp:1332`, `plan.cpp:1422`, `plan.cpp:1468`, `plan.cpp:1526`, `plan.cpp:1561`, `plan.cpp:1606`, `plan.cpp:1666`, `plan.cpp:1685`, `plan.cpp:1703`, `plan.cpp:1718`, `plan.cpp:1753`, `plan.cpp:1882`, `plan.cpp:1895`, `plan.cpp:1957`, `plan.cpp:1963`, `plan.cpp:1966`, `plan.cpp:2079`, `plan.cpp:2098`, `plan.cpp:2384`, `plan.cpp:2413`, `plan.cpp:2481`, `plan.cpp:2516`, `plan.cpp:2528`, `plan.cpp:2544`, `plan.cpp:2553`, `plan.cpp:2645`, `ptmod.cpp:36`, `ptmod.cpp:114` |
| `World::ingest` / `world.cpp:97` | `main.cpp:31`, `world.cpp:97`, `world.hpp:160` |
| `World::ingestTiles` / `world.cpp:136` | `world.hpp:193`, `world.cpp:108`, `world.cpp:136` |
| `kindOf` / `world.cpp:173` | `world.cpp:173`, `world.cpp:179`, `world.cpp:180`, `world.cpp:181`, `world.cpp:182` |
| `World::ingestEdges` / `world.cpp:175` | `world.cpp:109`, `world.cpp:175`, `world.hpp:194` |
| `World::ingestDragons` / `world.cpp:186` | `world.cpp:114`, `world.cpp:186`, `world.hpp:195` |
| `World::updateOwnBody` / `world.cpp:249` | `world.cpp:115`, `world.cpp:249`, `world.hpp:196` |
| `World::buildOccupancy` / `world.cpp:279` | `world.cpp:118`, `world.cpp:279`, `world.hpp:197` |
| `World::updateSymmetry` / `world.cpp:308` | `world.cpp:116`, `world.cpp:308`, `world.hpp:198` |
| `World::applyMirror` / `world.cpp:344` | `world.cpp:117`, `world.cpp:344`, `world.hpp:199` |
| `World::ingestSonar` / `world.cpp:386` | `world.cpp:119`, `world.cpp:386`, `world.hpp:200` |
| `World::pearlProb` / `world.cpp:425` | `world.cpp:425`, `plan.cpp:104`, `plan.cpp:117`, `plan.cpp:337`, `plan.cpp:1212`, `plan.cpp:2459`, `plan.cpp:2512`, `world.hpp:167` |
| `World::teamLongestKnown` / `world.cpp:451` | `plan.cpp:690`, `plan.cpp:746`, `plan.cpp:1317`, `world.cpp:451`, `world.hpp:171` |
| `World::computeFreshAllies` / `world.cpp:455` | `world.cpp:122`, `world.cpp:455`, `world.hpp:201` |
| `World::msgIdMask` / `world.cpp:469` | `world.cpp:391`, `world.cpp:469`, `world.hpp:189` |
| `World::encodeMsg` / `world.cpp:472` | `main.cpp:68`, `main.cpp:69`, `world.cpp:472`, `world.cpp:483`, `world.hpp:185`, `world.hpp:186` |
| `World::encodeMsg` / `world.cpp:483` | `main.cpp:68`, `main.cpp:69`, `world.cpp:472`, `world.cpp:483`, `world.hpp:185`, `world.hpp:186` |
| `World::encodeKingMsg` / `world.cpp:494` | `main.cpp:58`, `world.cpp:494`, `world.hpp:187` |
| `World::decodeMsg` / `world.cpp:513` | `world.cpp:390`, `world.cpp:513`, `world.hpp:188` |
| `main` / `main.cpp:17` | `main.cpp:17` |
| `hexBit` / `mapid.cpp:25` | `mapid.cpp:25`, `mapid.cpp:28`, `mapid.cpp:29` |
| `tableEdge` / `mapid.cpp:26` | `mapid.cpp:26`, `mapid.cpp:62`, `mapid.cpp:140`, `mapid.cpp:141`, `mapid.cpp:172` |
| `tableRange` / `mapid.cpp:31` | `mapid.cpp:31`, `mapid.cpp:37`, `mapid.cpp:96`, `mapid.cpp:206` |
| `tableFits` / `mapid.cpp:36` | `mapid.cpp:36`, `mapid.cpp:65` |
| `World::initMapId` / `mapid.cpp:46` | `world.cpp:36`, `mapid.cpp:46`, `world.hpp:203` |
| `World::updateMapId` / `mapid.cpp:56` | `mapid.cpp:56`, `world.cpp:110`, `world.hpp:204` |
| `World::mapIs` / `mapid.cpp:81` | `mapid.cpp:81`, `plan.cpp:838`, `plan.cpp:894`, `world.hpp:124`, `policy.hpp:161` |
| `World::mapFamIs` / `mapid.cpp:86` | `mapid.cpp:86`, `world.cpp:113`, `world.cpp:120`, `world.hpp:125`, `plan.cpp:893`, `plan.cpp:932`, `plan.cpp:935`, `plan.cpp:1237`, `policy.hpp:162` |
| `World::mapFountAt` / `mapid.cpp:92` | `mapid.cpp:92`, `plan.cpp:1016`, `plan.cpp:1051`, `world.hpp:139` |
| `World::mapTerrAt` / `mapid.cpp:103` | `mapid.cpp:103`, `world.hpp:140`, `plan.cpp:998`, `plan.cpp:1017`, `plan.cpp:1051` |
| `World::mapTerrChar` / `mapid.cpp:117` | `mapid.cpp:117`, `plan.cpp:2190`, `plan.cpp:2195`, `plan.cpp:2203`, `world.hpp:141` |
| `World::mapFrontBin` / `mapid.cpp:125` | `mapid.cpp:125`, `world.hpp:157`, `plan.cpp:2295`, `plan.cpp:2346`, `plan.cpp:2356`, `plan.cpp:2359`, `plan.cpp:2370` |
| `World::ensureCore2` / `mapid.cpp:134` | `mapid.cpp:134`, `mapid.cpp:164`, `plan.cpp:1361`, `world.hpp:147` |
| `World::ensurePockets` / `mapid.cpp:163` | `mapid.cpp:163`, `plan.cpp:2435`, `world.hpp:154` |
| `World::mapSpawnGap` / `mapid.cpp:203` | `mapid.cpp:197`, `mapid.cpp:203`, `plan.cpp:2263`, `plan.cpp:2360`, `world.hpp:142` |
| `World::mapTag` / `mapid.cpp:210` | `mapid.cpp:210`, `main.cpp:77`, `world.hpp:135` |
| `EngineSwarm` / `engine.hpp:15` | `engine.hpp:15` |
| `decide` / `engine.hpp:16` | `plan.hpp:30`, `engine.hpp:16`, `plan.cpp:1302`, `engcfg.hpp:12`, `main.cpp:44`, `main.cpp:45` |
| `opp` / `geom.hpp:12` | `world.cpp:49`, `world.cpp:50`, `world.cpp:51`, `world.cpp:67`, `world.cpp:89`, `world.cpp:128`, `world.cpp:223`, `world.cpp:364`, `world.cpp:377`, `world.cpp:380`, `plan.cpp:535`, `plan.cpp:546`, `plan.cpp:589`, `plan.cpp:600`, `plan.cpp:1097`, `plan.cpp:1107`, `plan.cpp:1329`, `plan.cpp:1443`, `plan.cpp:1478`, `plan.cpp:1547`, `plan.cpp:1560`, `plan.cpp:1605`, `plan.cpp:1702`, `plan.cpp:1717`, `plan.cpp:1752`, `plan.cpp:1881`, `plan.cpp:1966`, `plan.cpp:1969`, `plan.cpp:2515`, `plan.cpp:2543`, `plan.cpp:2553`, `geom.hpp:12` |
| `leftOf` / `geom.hpp:13` | `geom.hpp:13`, `plan.cpp:1329`, `plan.cpp:1913`, `plan.cpp:1967` |
| `rightOf` / `geom.hpp:14` | `plan.cpp:1329`, `plan.cpp:1913`, `plan.cpp:1967`, `geom.hpp:14` |
| `dirFromChar` / `geom.hpp:15` | `plan.cpp:1117`, `geom.hpp:15` |
| `wrapX` / `geom.hpp:24` | `world.cpp:104`, `world.cpp:106`, `world.cpp:139`, `world.cpp:169`, `world.cpp:196`, `world.cpp:201`, `world.cpp:211`, `world.cpp:215`, `world.cpp:225`, `world.cpp:231`, `world.cpp:245`, `plan.cpp:239`, `plan.cpp:1211`, `plan.cpp:1439`, `plan.cpp:2326`, `plan.cpp:2378`, `plan.cpp:2592`, `geom.hpp:24`, `geom.hpp:30` |
| `wrapY` / `geom.hpp:25` | `geom.hpp:25`, `geom.hpp:30`, `world.cpp:104`, `world.cpp:106`, `world.cpp:139`, `world.cpp:169`, `world.cpp:196`, `world.cpp:201`, `world.cpp:211`, `world.cpp:215`, `world.cpp:225`, `world.cpp:231`, `world.cpp:245`, `plan.cpp:239`, `plan.cpp:1211`, `plan.cpp:1439`, `plan.cpp:2326`, `plan.cpp:2378`, `plan.cpp:2592` |
| `idx` / `geom.hpp:26` | `world.cpp:42`, `world.cpp:43`, `world.cpp:44`, `world.cpp:104`, `world.cpp:106`, `world.cpp:139`, `world.cpp:169`, `world.cpp:196`, `world.cpp:201`, `world.cpp:211`, `world.cpp:215`, `world.cpp:225`, `world.cpp:231`, `world.cpp:245`, `world.cpp:527`, `world.cpp:528`, `world.cpp:542`, `world.cpp:543`, `geom.hpp:26`, `geom.hpp:30`, `plan.cpp:239`, `plan.cpp:1211`, `plan.cpp:1439`, `plan.cpp:2326`, `plan.cpp:2378`, `plan.cpp:2592` |
| `tiles` / `geom.hpp:27` | `plan.hpp:144`, `mapid.cpp:138`, `mapid.cpp:170`, `world.cpp:26`, `world.cpp:305`, `ptmod.cpp:88`, `plan.cpp:44`, `plan.cpp:162`, `plan.cpp:292`, `plan.cpp:300`, `plan.cpp:329`, `plan.cpp:763`, `plan.cpp:821`, `plan.cpp:825`, `plan.cpp:872`, `plan.cpp:977`, `plan.cpp:1013`, `plan.cpp:1158`, `plan.cpp:1201`, `plan.cpp:1247`, `plan.cpp:1268`, `plan.cpp:1315`, `plan.cpp:2252`, `plan.cpp:2402`, `plan.cpp:2476`, `plan.cpp:2504`, `plan.cpp:2584`, `geom.hpp:27` |
| `stepIdx` / `geom.hpp:28` | `mapid.cpp:141`, `mapid.cpp:153`, `mapid.cpp:172`, `mapid.cpp:173`, `world.cpp:58`, `world.cpp:59`, `world.cpp:65`, `world.cpp:90`, `world.cpp:92`, `world.cpp:212`, `world.cpp:223`, `world.cpp:265`, `world.cpp:364`, `world.cpp:377`, `world.cpp:380`, `plan.cpp:1910`, `geom.hpp:28` |
| `dx` / `geom.hpp:33` | `plan.cpp:345`, `geom.hpp:33`, `geom.hpp:36`, `geom.hpp:39` |
| `dy` / `geom.hpp:34` | `plan.cpp:345`, `geom.hpp:34`, `geom.hpp:36`, `geom.hpp:39` |
| `cheb` / `geom.hpp:35` | `world.cpp:231`, `plan.cpp:2282`, `geom.hpp:35` |
| `manhattan` / `geom.hpp:39` | `plan.cpp:261`, `plan.cpp:278`, `plan.cpp:389`, `plan.cpp:412`, `plan.cpp:706`, `plan.cpp:731`, `plan.cpp:752`, `plan.cpp:991`, `plan.cpp:1022`, `plan.cpp:1024`, `plan.cpp:1036`, `plan.cpp:1038`, `plan.cpp:1064`, `plan.cpp:1282`, `plan.cpp:1515`, `plan.cpp:1661`, `plan.cpp:2042`, `plan.cpp:2054`, `plan.cpp:2282`, `plan.cpp:2308`, `plan.cpp:2311`, `plan.cpp:2315`, `plan.cpp:2317`, `plan.cpp:2318`, `plan.cpp:2328`, `plan.cpp:2329`, `plan.cpp:2371`, `plan.cpp:2455`, `ptmod.cpp:70`, `geom.hpp:39` |
| `abs` / `geom.hpp:40` | `geom.hpp:36`, `geom.hpp:39`, `geom.hpp:40`, `plan.cpp:345`, `plan.cpp:1210`, `plan.cpp:1438`, `plan.cpp:2326`, `plan.cpp:2377`, `plan.cpp:2591` |
| `lenRoundOf` / `world.hpp:64` | `world.cpp:238`, `world.cpp:403`, `world.cpp:420`, `world.hpp:64` |
| `ptLenOf` / `world.hpp:133` | `world.cpp:461`, `plan.cpp:1509`, `world.hpp:133`, `ptmod.cpp:95` |
| `mapStateCode` / `world.hpp:134` | `mapid.cpp:165`, `main.cpp:76`, `plan.cpp:2254`, `world.hpp:123`, `world.hpp:134`, `policy.hpp:171`, `policy.hpp:177` |
| `inCore2` / `world.hpp:148` | `world.hpp:148`, `plan.cpp:350`, `plan.cpp:356`, `plan.cpp:368`, `plan.cpp:1404`, `plan.cpp:2259`, `plan.cpp:2361` |
| `edgeUnknown` / `world.hpp:165` | `plan.cpp:566`, `plan.cpp:622`, `plan.cpp:1599`, `plan.cpp:1626`, `plan.cpp:1711`, `plan.cpp:1725`, `world.hpp:165` |
| `isFountain` / `world.hpp:168` | `world.cpp:169`, `world.hpp:168`, `plan.cpp:343`, `plan.cpp:1014`, `plan.cpp:2268`, `plan.cpp:2361` |
| `allyLongest` / `world.hpp:177` | `world.hpp:177` |
| `iAmLongest` / `world.hpp:178` | `world.hpp:178`, `plan.cpp:203`, `plan.cpp:220`, `plan.cpp:227`, `plan.cpp:228`, `plan.cpp:675`, `plan.cpp:742`, `plan.cpp:774`, `plan.cpp:852`, `plan.cpp:944`, `plan.cpp:1011`, `plan.cpp:1134`, `plan.cpp:1161`, `plan.cpp:1225`, `plan.cpp:1318`, `plan.cpp:1319`, `plan.cpp:1321`, `plan.cpp:1324`, `plan.cpp:1404`, `plan.cpp:2004`, `plan.cpp:2007`, `plan.cpp:2251`, `plan.cpp:2394`, `plan.cpp:2567`, `plan.cpp:2623`, `plan.cpp:2669`, `plan.cpp:2670`, `ptmod.cpp:90` |
| `allyFresh` / `world.hpp:179` | `world.cpp:459`, `plan.cpp:1166`, `plan.cpp:2194`, `plan.cpp:2571`, `ptmod.cpp:96`, `world.hpp:179` |
| `testSetEdge` / `world.hpp:182` | `world.hpp:182` |
| `engineTag` / `policy.hpp:25` | `policy.hpp:25` |
| `lookupFront` / `policy.hpp:120` | `policy.hpp:120`, `policy.hpp:152` |
| `makeConfig` / `policy.hpp:130` | `policy.hpp:130`, `policy.hpp:172` |
| `lookupPolicy` / `policy.hpp:160` | `policy.hpp:160`, `policy.hpp:172` |
| `get` / `policy.hpp:170` | `main.cpp:42`, `policy.hpp:170` |
| `config` / `policy.hpp:175` | `main.cpp:44`, `main.cpp:45`, `main.cpp:81`, `policy.hpp:175` |
| `frontShare` / `engcfg.hpp:39` | `engcfg.hpp:39`, `plan.cpp:2298` |
| `headsAt` / `engcfg.hpp:45` | `engcfg.hpp:45`, `plan.cpp:2606`, `plan.cpp:2625` |
| `dirFromCharSafe` / `proto.hpp:9` | `proto.hpp:9`, `proto.cpp:124`, `proto.cpp:160` |
| `move` / `proto.hpp:76` | `plan.hpp:113`, `main.cpp:47`, `main.cpp:51`, `main.cpp:53`, `proto.hpp:76` |
| `split` / `proto.hpp:77` | `plan.hpp:59`, `main.cpp:50`, `proto.hpp:77` |
| `sonar` / `proto.hpp:78` | `main.cpp:70`, `main.cpp:71`, `proto.hpp:78` |
| `indicator` / `proto.hpp:79` | `main.cpp:82`, `proto.hpp:79`, `params.hpp:594`, `world.hpp:123` |
| `log` / `proto.hpp:80` | `proto.hpp:80` |
| `size` / `proto.hpp:83` | `mapid.cpp:149`, `mapid.cpp:178`, `mapid.cpp:180`, `mapid.cpp:190`, `main.cpp:66`, `world.cpp:72`, `world.cpp:84`, `world.cpp:193`, `world.cpp:204`, `world.cpp:208`, `world.cpp:220`, `world.cpp:260`, `world.cpp:262`, `world.cpp:263`, `world.cpp:267`, `world.cpp:274`, `world.cpp:283`, `world.cpp:294`, `world.cpp:347`, `proto.cpp:25`, `proto.cpp:27`, `proto.cpp:53`, `proto.cpp:97`, `proto.cpp:98`, `proto.cpp:99`, `proto.cpp:100`, `proto.cpp:116`, `proto.cpp:120`, `proto.cpp:123`, `proto.cpp:137`, `proto.cpp:145`, `proto.cpp:155`, `proto.cpp:165`, `proto.cpp:169`, `proto.cpp:179`, `proto.hpp:83`, `plan.cpp:71`, `plan.cpp:122`, `plan.cpp:146`, `plan.cpp:303`, `plan.cpp:387`, `plan.cpp:417`, `plan.cpp:448`, `plan.cpp:453`, `plan.cpp:475`, `plan.cpp:486`, `plan.cpp:490`, `plan.cpp:502`, `plan.cpp:528`, `plan.cpp:581`, `plan.cpp:665`, `plan.cpp:667`, `plan.cpp:794`, `plan.cpp:905`, `plan.cpp:1065`, `plan.cpp:1181`, `plan.cpp:1202`, `plan.cpp:1254`, `plan.cpp:1351`, `plan.cpp:1352`, `plan.cpp:1404`, `plan.cpp:1418`, `plan.cpp:1454`, `plan.cpp:1464`, `plan.cpp:1491`, `plan.cpp:1522`, `plan.cpp:1640`, `plan.cpp:1653`, `plan.cpp:1679`, `plan.cpp:1698`, `plan.cpp:1748`, `plan.cpp:1765`, `plan.cpp:1767`, `plan.cpp:1779`, `plan.cpp:1784`, `plan.cpp:1785`, `plan.cpp:1795`, `plan.cpp:1801`, `plan.cpp:1806`, `plan.cpp:1807`, `plan.cpp:1811`, `plan.cpp:1813`, `plan.cpp:1819`, `plan.cpp:1820`, `plan.cpp:1834`, `plan.cpp:1835`, `plan.cpp:1841`, `plan.cpp:1850`, `plan.cpp:1851`, `plan.cpp:1855`, `plan.cpp:1858`, `plan.cpp:1861`, `plan.cpp:1875`, `plan.cpp:1879`, `plan.cpp:1890`, `plan.cpp:1907`, `plan.cpp:1928`, `plan.cpp:1930`, `plan.cpp:2049`, `plan.cpp:2063`, `plan.cpp:2076`, `plan.cpp:2095`, `plan.cpp:2218`, `plan.cpp:2309`, `plan.cpp:2315`, `plan.cpp:2381`, `plan.cpp:2409`, `plan.cpp:2467`, `plan.cpp:2478`, `plan.cpp:2510`, `plan.cpp:2520`, `plan.cpp:2525`, `plan.cpp:2585`, `plan.cpp:2638`, `ptmod.cpp:111` |
| `Planner` / `plan.hpp:29` | `plan.hpp:29` |
| `setConfig` / `plan.hpp:34` | `plan.hpp:34`, `main.cpp:45`, `engine.hpp:16` |
| `Planner::opUpdate` / `v1.4/opmod.cpp:16` | `v1.4/plan.hpp:216`, `v1.4/plan.cpp:1354`, `v1.4/opmod.cpp:16` |
| `Planner::opWantSplit` / `v1.4/opmod.cpp:90` | `v1.4/plan.hpp:217`, `v1.4/plan.cpp:1983`, `v1.4/opmod.cpp:90` |
| `Planner::opHoldSplits` / `v1.4/opmod.cpp:112` | `v1.4/plan.hpp:218`, `v1.4/plan.cpp:1983`, `v1.4/opmod.cpp:112` |
| `Planner::opTag` / `v1.4/opmod.cpp:115` | `v1.4/plan.hpp:219`, `v1.4/plan.cpp:2160`, `v1.4/opmod.cpp:115` |
| `Planner::opSplitTag` / `v1.4/opmod.cpp:127` | `v1.4/plan.hpp:220`, `v1.4/plan.cpp:2006`, `v1.4/opmod.cpp:127` |
| `Planner::opMidHold` / `v1.4/opmod.cpp:145` | `v1.4/plan.hpp:228`, `v1.4/plan.cpp:1362`, `v1.4/opmod.cpp:145` |
| `Planner::opMidDoom` / `v1.4/opmod.cpp:235` | `v1.4/plan.hpp:229`, `v1.4/plan.cpp:1883`, `v1.4/opmod.cpp:235` |
| `Planner::opMidTag` / `v1.4/opmod.cpp:237` | `v1.4/plan.hpp:230`, `v1.4/plan.cpp:2161`, `v1.4/opmod.cpp:237` |
