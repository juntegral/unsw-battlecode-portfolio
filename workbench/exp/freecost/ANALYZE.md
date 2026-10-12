# freecost 실행 뒤 분석

BUILD에서는 새 게임을 실행하지 않았다. 사전 등록은 `versions/v1.8/VERSION.md` §11이다. 아래 명령은 저장소 루트에서 조정자가 실행한다. 승패와 최종 길이로 채택을 판단하지 않는다.

## 실행과 원자료

```sh
node exp/freecost/runq.js exp/freecost/spec.json --jobs 3 --cap 6
UNSW_RULES=123 node exp/freecost/analyze.js > exp/freecost/analysis.txt
```

`runq.js`는 `exp/v16/q1/runq.js`의 사본이다. runq14의 lane 형식과 rows/games 배치를 유지하고 hunter 경로, `cpu:true`, 공식 `tools/unswbc123`을 사용한다. 원래 runq14는 `bots/` 접두사를 붙여 hunter 경로를 찾지 못하고 CPU 옵션도 읽지 않으므로 이 사본을 쓴다. 모든 판은 nice -n 10, 전체 6판 제한, 21GiB 디스크 여유 검사를 따른다.

| 지도 묶음 | 지도 | on/off 각각 |
|---|---|---:|
| 처음 보는 번들 | arena, big_empty, Colosseum, default_small, stronghold | 20 |
| 온라인 | trophy, portals, slithery_fight | 12 |
| 스프린트 | around_unsw, australia, stripes | 12 |
| 생성 | gen_S_03, gen_M_03, gen_M_07, gen_L_02, gen_R_01, gen_X_07 | 24 |
| off/base 동일성 | trophy, around_unsw, gen_M_07 | 각각 12 |

모든 묶음은 A/B × proxy4_king/hunter × seed 1이다. 총 160판 = on/off 68키(136판) + 동일성 12키(24판). `bot-base`는 작업 시작 v1.8을 동결한 복제본이고 `bot-off`는 수정 후 기본값 복제본이다. 다른 작업이 v1.8을 수정해도 비교 기반은 바뀌지 않는다. 이번 명세는 다른 시드·모든 생성 지도를 검증하지 않는다.

`analyze.js`는 키별 마지막 깨끗한 줄(G 있음, exit 0, error/botProblem 없음)을 선택하고 실패 이력을 별도로 남긴다. `analysis.json`의 expectedGames=160, missing=0, pairs=68, identity=12가 필요하다. rows/replay를 삭제하지 않는다. 재실행으로 회복된 오류도 historyErrors에서 확인한다. queen id는 초기 드래곤의 팀별 최저 id에서 찾는다.

## 1. 무료 다중 이동이 실제 늘었는가

`sets.on/off.<key>.turnsL5`는 시작 L≥5인 우리 차례 수이고 `freeMulti`는 1<steps≤ceil(L/4)인 선택 MOVE 수다. 사망한 시도도 포함하며 `completedFreeMulti`가 완주 수다. `bands`는 L2–4/L5–8/L9–12/L13+의 차례·무료 다중 이동 수다.

- 키별 `pairs[].freeMultiDelta`, `rateOn`, `rateOff`를 먼저 읽고 전체 합계/차례당 비율도 계산한다. 지도·편·상대·길이별 분모를 함께 보고한다. 키별 비율 단순 평균으로 전체 비율을 대신하지 않는다.
- on의 무료 다중 이동 수와 비율이 증가해야 기제 확인이다. 발동할 길이/상황이 없거나 증가하지 않으면 미확인으로 남긴다. 무료 MOVE 자체가 늘어도 사망 시도만 늘었는지 완주 수로 구분한다.
- `moves`에서 off와 action이 처음 달라진 차례, L5–8의 2걸음 진주/탈출, L9+의 3걸음 탈출을 골라 전후 판면을 읽는다. 시작 L과 실제 steps로 가격 변화 +1.6/+3.2를 계산한다. 모든 2걸음 후보 허용, late 완화, strike 길이 확장은 하지 않았다. 무료여도 기존 관문이 후보를 만들지 않으면 선택될 수 없다.
- Q2b 적 도달의 진주 경계 수정으로 달라진 이동은 가격 변경 사례와 따로 기록한다.

## 2. 몸·길이·꼬리 예측과 resync drift

`analyze.js`는 `tools/mass_ledger.js perGame(..., rules:'123')`로 매 걸음 head/tail을 replay dragonUpdate와 대조한다. 모든 sets의 checks(sim/eatTC/splits/drops/ledger/final 등)는 0이어야 한다. 특히 chk.sim은 재동기화 횟수이며 0이 필요하다.

다음 두 검사가 실제 구현을 검증한다.

1. on MOVE의 `fc<free>,<paid>,<predictedLength>,<unknownSlots>,<bodyHash>`는 main에서 `World::predictOwnMove`로 갱신한 자기 몸 기억이다. 무료 걸음 수는 시작 길이에 고정된다. 분석 도구가 그 값과 기보 이동 직후 길이/몸의 FNV 해시를 비교한다. `knownBodyDrift`는 완전한 몸 기억이고 이동 진주가 전부 시작 7×7 안에서 보인 상황의 불일치다. **0이어야 한다.** `predicted` 분모, unknownBodies, uncertainBodyDrift, blindUnverified, missingTags를 함께 보고한다. 알려진 완주 MOVE에서 표식 누락이 있으면 분석 누락을 먼저 고친다.
2. 기보 시작의 전체 몸/확정 진주를 실제 C++ predictor에 넣는다(`fixtures-on --predict`). `oracleDrift`는 기보와 몸 타일 순서·길이·지급이 다름을 나타내며 **0이어야 한다.** 이는 부분 관측으로 만들어진 기억이 정확하다는 증거와 구분한다. 실제 기억은 1의 해시로 검증한다.

몸 해시는 head→tail 타일 번호 t=y*W+x에 대해 h=2166136261, h=((h XOR t)*16777619) mod 2^32다. 불일치가 나오면 해당 차례의 fc, 시작/완료 몸, 진주, 벽/포털을 전수 확인한다. unknownSlots>0인 기억과 창 밖 진주는 불확실성으로 기록하고 알려진 예측의 성공으로 세지 않는다. 해시 일치에는 충돌의 한계가 있으므로 원자료 predictor 대조도 함께 쓴다. 사망한 MOVE는 완주 예측 대조에서 제외하되 사망 분석에 포함한다.

BUILD 합성 검사는 아래와 같다. 게임을 만들지 않는다.

```sh
python3 exp/freecost/check-fixtures.py
```

실제 `Planner::paidSteps`, `World::predictOwnMove`, Q2b computeEnemyDistance/ks2Threat를 연결한다. 시작 길이 2–64, 걸음1–20, 진주 없음/첫걸음/번갈아 먹기, L4→5 무료 구간 고정, 도달 끝의 최소 길이2, L5/6의 5–7칸 적 도달, L16+진주가 무료 5번째로 변하지 않음, L17의 무료 5번째를 점검한다. 현재 on 2833/off 1386개 통과다.

## 3. 자기·벽·여왕 사망 회귀

`sets.*.<key>.self/wall`은 기보 사유 S/W를 그대로 센다. ledger의 sac/trap은 두 원인을 묶으므로 그것으로 대신하지 않는다. `death`는 실제 우리 여왕 사망(id/round/reason/L/head/indicator)이고 `deaths`는 우리 모든 드래곤 사망이다. `oversprint`는 1.2.3 step simulator의 지급 실패, `invalidAction`은 기보 A 사유다.

- on/off 68키의 전체 self/wall/여왕 사망이 늘지 않아야 한다. `pairs`의 selfDelta/wallDelta/queenDeathDelta>0 및 queenEarlier 키를 빠짐없이 읽는다. 합계가 같아도 키별 회귀를 숨기지 않는다.
- 사망 원인이 공짜 걸음의 덜 빠진 꼬리인지, 열린 길이 사실 자기 몸인지, 진주 오인인지, 기존 함정인지 구분한다. oversprint/invalidAction/오류는 0이 필요하다.
- 여왕 사망이 둘 다 있는 판에서도 더 이른 사망을 별도로 읽고 길이 보존으로 정당화하지 않는다. 시작 주머니 Slithery와 Around UNSW B를 포함한다.

대표 벽 포함 판면(지도 이름·좌표·라운드는 analysis의 해당 사건으로 바꾼다):

```sh
UNSW_RULES=123 node exp/w7/tunnelpic.js exp/freecost/on/games/bot-hunter_around_unsw_B_1/game.replay maps/sprint/around_unsw.map B X,Y 4,5,6,7 --r 4
UNSW_RULES=123 node exp/w7/tunnelpic.js exp/freecost/off/games/bot-hunter_around_unsw_B_1/game.replay maps/sprint/around_unsw.map B X,Y 4,5,6,7 --r 4
UNSW_RULES=123 node exp/q2/queendeath.js exp/freecost/on exp/freecost/off --games > exp/freecost/queendeath.txt
```

tunnelpic은 라운드 시작의 판면이다. 같은 라운드 내 id 순서·다중 걸음 중간 몸은 replay action/dragonUpdate와 맞춘다. 기존 queendeath는 A=id0/B=id1을 가정하므로 이번 지도 파일의 초기 id를 확인한 뒤 보조로만 쓴다. 기본 분석은 팀별 queen id를 직접 찾는다. 구 규칙 전용 timing_study/fragment_study/decisions/baseline_study는 사용하지 않는다.

## 4. off 동일성과 CPU

```sh
UNSW_RULES=123 node exp/v16/identity.js exp/freecost/id-off exp/freecost/id-base > exp/freecost/identity.txt
```

12/12 사건 동일성이 필요하다. `analysis.json.identity`도 모두 same=true여야 한다. fingerprint에는 이동/사망/진주/분열과 메시지 사건이 들어가며 indicator/log/CPU points는 빠진다. 기록된 지시문과 메시지도 차이가 없는지 첫 차이가 있을 때 직접 읽는다.

`compile-check.json`은 base/off/on을 공식 judge clang으로 컴파일한 결과다. base와 off WASM은 496456 bytes, SHA-256 `698253da7cb5f7886463210bdcd738719cfa86fc07757ae467640708ca306c35`로 동일했다. 이 검사는 off 명령어와 자료 배치를 보존함을 보여주며 실제 사건 동일성/CPU를 대신하지 않는다.

`sets.*.*.cpuMaxM`은 우리 팀 points per turn의 max다. null이면 미검증, 80M 이상이면 경보, 100M/timeout/no reply는 깨짐이다. 모든 lane에 cpu:true가 있다. `d`(완료 탐색 깊이)를 같은 키·차례에서 비교해 새 태그/예측 비용이 탐색 깊이를 줄이는지도 확인한다. on은 몸 해시를 계산하므로 CPU 비용이 추가된다. BUILD의 컴파일/합성 실행은 실제 judge 턴 CPU 측정이 아니다.

## 결과 인계

`exp/freecost/RESULT.md`에 분모·무료 다중 이동 변화·첫 선택 차이 판면 → 몸 예측/재동기화 → 키별 사망 → off 동일성 → CPU/오류 순서로 쓴다. pending과 미확인을 성공으로 쓰지 않는다. 온라인 행동의 근거는 duels §9 가설1이며, 로컬 승패로 채택하지 않는다. 제출·네트워크·커밋은 별도 조정자 작업이다.

분석 도구 구문과 replay hook/predictor 연동은 기존 Q2box Colosseum A 기보 한 개를 읽어서 확인했다(`analysis-smoke.json`, checks 전부0, oracleDrift0). 새 게임이나 freecost 후보 결과는 아니다.
