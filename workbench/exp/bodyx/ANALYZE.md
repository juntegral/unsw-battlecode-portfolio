# BODYX 외부 실행 뒤 기제 점검

BUILD는 새 게임·커밋·네트워크를 사용하지 않았다. `BODYX_ON=false`가 기본값이다. `FREECOST_ON=false`, 기존 이동 가격·후보 생성 관문을 유지한다. 사전 기준은 `versions/v1.8/VERSION.md` §17이며 결과를 보고 바꾸지 않는다.

## 0. 실행과 자료 완전성

저장소 루트에서 조정자가 실행한다.

```sh
node exp/bodyx/runq.js exp/bodyx/spec.json --jobs 3 --cap 6
UNSW_RULES=123 node exp/bodyx/analyze.js
```

`runq.js`는 runq14 형식의 spec을 받는 기존 QSIGHT runner 복제다. `exp/q2/bot-hunter` 상대 경로, 1.2.3 엔진, CPU 수집을 지원한다. 원래 `exp/v14/runq14.js`는 상대를 `bots/` 아래로만 해석하고 cpu 옵션을 읽지 않으므로 이 spec에는 복제본을 사용한다. 동시 게임 기계 전체6/내3, 디스크21GiB, nice10, 깨끗한 키 재개 정책을 유지한다.

| 묶음 | 지도 | on/off 합계 |
|---|---|---:|
| 번들 | arena, big_empty, Colosseum, default_small, stronghold | 40 |
| 온라인 | default, schooltime, trophy, portals, slithery_fight, autarky, prisoners_dilemma | 56 |
| 스프린트 | around_unsw, australia, stripes | 24 |
| 생성 | gen_L_03, gen_X_07, gen_S_03, gen_M_07, gen_R_01, gen_L_02 | 48 |
| off/base 동일성 | trophy, around_unsw, gen_M_07 | 24 |

전부 A/B × proxy4_king/hunter × seed1이다. 총192판, on/off84짝, off/base12짝이다. census10건의 지도6개가 모두 포함된다. `bot-base`는 작업 시작 v1.8을 동결했고, 수정 후 v1.8(default off)와 공식 WASM이 동일하다. 비교 동안 기반/복제본을 수정하지 않는다. seed2·전체 지도 검증은 이 명세에 포함하지 않았다.

`analysis.json`: expectedGames192, missing0, pairs84, identity12를 확인한다. 키별 마지막 깨끗한 row(G 있음, exit0, error/botProblem 없음)를 선택하고 historyErrors를 모두 읽는다. 실패 후 재실행됐어도 이력을 숨기지 않는다. queen id는 초기 드래곤의 팀별 최저 id다. 모든 checks(sim/splits/drops/eatTC/ledger/final/lineage/natBal/dropBal/unknownDeath)는0이어야 한다. 구 규칙 전용 timing_study/fragment_study/decisions/baseline_study는 사용하지 않는다.

## 1. 발동과 census10 입력 반례

```sh
nice -n 10 python3 exp/bodyx/check-fixtures.py
```

`tables.json.mainDeaths`의 cause=sac/reason=S인10건을 실제 raw 마지막 여왕 차례의 전체 몸·진주·다른 몸·실제 지형에서 추출한다. `census-fixtures.json`은 이 입력과 비충돌 한 걸음 대안이다. 실제 C++ `Planner::bodyXCandidate`를 호출한 on은10/10 거절, 기존 `tileEnterable`/구 전이의 off는10/10 완주해야 한다. on의 사망 위치는 failed=2(세 번째 걸음), reason=S이고, 성공한 두 걸음 뒤 몸은 census의 실제 endBody와 일치해야 한다. 최소 하나의 안전한 한 걸음 대안도 각각 있어야 한다. 이는 후보의 거절 검사이며 실제 Planner의 대안 선택까지 증명하지 않는다.

`fixture-check.json`에는10건의 on/off 몸 배열과 대안을 남긴다. 3,998개 입력은 L2–64, 1–20걸음, 무진주/첫걸음/교대 진주, 반복 경로의 진주 재섭취 금지, 고정 무료 구간, 지급 직전 길이2, 꼬리 충돌이 꼬리 전진보다 먼저인 경우, 다른 몸과의 충돌, 마지막 적 머리 교환을 포함한다. 실제 가격 함수가 항상 (steps−1)×1.6인지도 검사한다. 합성 상태는 게임이 아니다.

새 기보의 `bodyxrN`은 BODYX가 제거한 후보 수다. 일반 MOVE로 선택 단계까지 도달한 차례에 표시되므로 split/조기 반환에서 생긴 탈락까지 세는 전수 카운터가 아니다. `sets.on.*.rejected`는 발동 하한이다. census처럼 몸이 굽은 L6/8/10/14 상황을 기보에서 찾아 실제 출력이 금지한 경로를 피하는지 판면으로 확인한다.

## 2. 다중 이동 몸·꼬리 drift0

`analyze.js`는 1.2.3 mass_ledger로 현재 차례의 실제 몸·진주를 재구성한다. **모든 완주 다중 MOVE**(여왕 및 모든 우리 드래곤, trade 사망은 제외)의 입력을 실제 C++ 전이/후보 검증 함수(`fixtures-on`)에 넣는다. 각 걸음의 전체 몸 배열을 독립123 oracle과 비교하고 최종 몸 배열을 replay 재구성 결과와 비교한다. `oracleDrift=0`이어야 한다. 매 걸음의 머리/꼬리는 원본 dragonUpdate와 직접 비교해 `stepDrift=0`, update 누락0이어야 한다. `checks.sim=0`도 별도 필요하다. 원본 replay는 중간 몸 전체가 아니라 머리/꼬리 update를 기록하므로 전체 배열은 규칙 재구성과 C++ 배열을 교차 확인한다.

실제 Planner 입력 기억에서 낸 표식도 따로 비교한다.

```text
bodyx<free>,<paid>,<endLength>,<unknownStartSlots>,<startHash>,<endHash>,<unseenPathTiles>
```

해시는 head→tail 타일 번호 t=y×W+x, h=2166136261, h=((h XOR t)×16777619) mod2^32다. 시작 몸 해시까지 비교해 기존 기억 오류와 전이 오류를 구분한다. 끝의 길이/해시가 replay와 다르거나 시작 해시가 다르면 `memoryDrift`에 시작/완료 몸·경로·진주·표식을 전수 기록한다. **memoryDrift0도 필요하다.** 완전 입력 oracle0으로 실제 입력 기억 불일치를 통과시키지 않는다. `unknownInput`, `unseenPearls`, `missingTags`와 predicted/completed 분모도 보고한다. 관측 불확실성과 unknown 슬롯은 성공으로 세지 않는다. 해시는 충돌 가능성이 있으므로 실제 C++의 배열 대조를 함께 사용한다.

이번 수정은 World의 몸 기억 재구성이나 창 밖 진주 추정을 바꾸지 않았다. 따라서 drift가 남으면 실패/미확인으로 기록하고 다음 작업을 제안한다. DFS는 다중 후보 끝의 정확한 제거 수·길이에서 시작한다. 이후 차례의 기존 보수적 visited-path 가정은 유지한다. 단일 후보의 flood fill/DFS에는 새 항을 넣지 않았다.

## 3. 자기 몸 사망과 다른 사망 원인

`sets.on/off.*`의 multi(사망한 시도 포함)/completed 분모와 selfMulti/queenSelfMulti를 합계 및 키별로 낸다. on의 여왕·모든 드래곤의 다중 MOVE 자기 몸 사망이 약0으로 내려야 한다. 모든 원시 S와 다중 S를 모두 보고하고, `deaths`의 intentionalFeed/noExit는 보조 분류로만 쓴다. 의도적 먹이·진주 오인·몸 기억 오류·충돌로 갈 수밖에 없는 판을 판면으로 전수 확인해 남은 사망을 설명하되 원시 집계에서 제외하지 않는다. 표식 정규식의 먹이 분류는 실제 action/판면으로 재확인한다.

`pairs[].reasons`는 S/W/O/H/A의 키별 변화, `causes`는 sac/trap/rammed/ram/enemyBody/allyHead/fault/sprintDeath의 변화다. **S 이외의 원인 증가가 없는지** 합계와 키별 모두 확인한다. 증가한 원인·새 여왕 사망·더 이른 여왕 사망(queenEarlier)은 빠짐없이 판면을 읽는다. oversprint/invalid A/timeout/no reply/errors는0이어야 한다. 다른 사망의 합계 감소로 특정 지도 회귀를 숨기지 않는다. 승패·최종 길이는 채택 기준으로 사용하지 않는다.

## 4. 실제 판면과 사례 선택

각 키의 `samples`에서 첫 선택 변화, L8의 유료 세 번째 이동, L14의 무료 세 걸음, 진주를 먹는 sprint/escape를 고른다. census fixture g0018/default_small B r128 `WSW`, g0081/around_unsw A r221 `SSW`도 비교 기준으로 사용한다. 선택이 바뀐 판은 이후 관측도 바뀌므로 같은 키·라운드를 같은 입력의 인과 증거로 취급하지 않는다.

```sh
UNSW_RULES=123 node exp/w7/tunnelpic.js exp/bodyx/on/games/bot-hunter_default_small_B_1/game.replay maps/bundled/default_small.map B X,Y 126,127,128,129 --r 4
UNSW_RULES=123 node exp/w7/tunnelpic.js exp/bodyx/off/games/bot-hunter_default_small_B_1/game.replay maps/bundled/default_small.map B X,Y 126,127,128,129 --r 4
```

X,Y와 라운드는 실제 선택 사건 좌표로 바꾼다. tunnelpic은 라운드 시작 판면이므로 그 라운드의 id 순서와 다중 이동 중간 상태는 samples/drift 기록 및 dragonAction/dragonUpdate 원문과 함께 읽는다. 기대 그림은 정상 꼬리만 빠지는 무료 걸음, 추가 꼬리가 빠지는 유료 걸음, 진주 걸음의 정상 꼬리 유지, 자기 몸의 남은 칸 회피다. 모든 회귀/불일치도 같은 방식으로 전후 그림을 남긴다.

## 5. off 동일성·CPU·오류

```sh
nice -n 10 python3 exp/bodyx/build.py
UNSW_RULES=123 node exp/v16/identity.js exp/bodyx/id-off exp/bodyx/id-base > exp/bodyx/identity.txt
```

`compile-check.json`의 off_equals_original_v18_wasm=true, 공식 base/off 전체 바이트 동일이 필요하다. 게임 사건·음파는 `identity[].same`12/12와 identity.txt로 확인한다. fingerprint는 indicator/log/CPU instructions를 제외하고 action/분열/이동/사망/진주/메시지는 포함한다. 차이가 있다면 첫 사건에서 중단 원인을 조사한다. 컴파일 동일성이 게임 동일성을 대신하지 않는다.

모든 row에 cpu가 있고 cpuMaxM이 null이면 미검증이다. 우리 팀 max80M 미만,100M/시간 초과/오류 없음이 필요하다. pairs의 depthPairs/depthLower/depthSame/depthHigher로 같은 키·round·id의 완료 탐색 깊이를 비교한다. BODYX는 다중 후보 몸 복제와 예측 해시를 추가하므로 단순 wall time으로 judge point CPU를 대신하지 않는다. 선택 변화 이후 차례 비교는 순수 비용의 인과 증거가 아님을 적는다.

## 결과 인계

`exp/bodyx/RESULT.md`에 발동·census → 실제 몸 drift/사망 판면 → 다른 원인·키별 회귀 → off 동일성 → CPU·오류 순서로 쓴다. 표본·분모·불확실성·미완료를 명시하고 기준을 결과 뒤에 바꾸지 않는다. 채택/기본값 변경/커밋/업로드는 조정자가 결정한다.

BUILD에서 기존 census g0018 기보만 읽어 분석 연결을 점검했다(`analysis-smoke.json`): 완주 다중 MOVE82건, replay head/tail 및 C++ 전이 drift0, ledger checks전부0. 이것은 on 후보의 실제 사망·기억·CPU 결과가 아니다.
