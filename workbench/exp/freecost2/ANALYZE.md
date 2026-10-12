# FREECOST2 실행·분석 인계

사전 등록: `versions/v1.8/VERSION.md` §23, 2026-10-02 13:42:25 KST. BUILD에서는 게임·네트워크·커밋을 사용하지 않았다. 이번 ON/OFF는 **BODYX_ON=true, BODYMEM2_ON=true, FREECOST_ON=false**이며 FREECOST2 가격만 다르다. 기존 FREECOST 결과를 이번 결과로 대신하지 않는다.

## 0. 실행과 자료 완전성

저장소 루트에서 조정자가 실행한다.

```sh
python3 exp/freecost2/validate.py
node exp/freecost2/runq.js exp/freecost2/spec.json --jobs 3 --cap 6
UNSW_RULES=123 node exp/freecost2/analyze.js > exp/freecost2/analysis.log
UNSW_RULES=123 node tools/firstdiv.js exp/freecost2/on exp/freecost2/off --out exp/freecost2/firstdiv.json > exp/freecost2/firstdiv-summary.json 2> exp/freecost2/firstdiv.log
UNSW_RULES=123 node exp/v16/identity.js exp/freecost2/id-off exp/freecost2/id-base > exp/freecost2/identity.txt
```

`runq.js`는 runq14 lane 형식이며 `exp/freecost/runq.js`의 사본이다. 원 runq14는 경로 상대와 cpu를 처리하지 못하므로 이 사본을 쓴다. 공식123 sandbox·cpu:true·nice10·기계 전체6판·21GiB 여유·clean row 재개를 지원한다. BUILD의 nice10은 환경의 setpriority 거부 때문에 적용되지 않았으나 컴파일/fixture는 정상 완료했다. 실행 전 validator는 source-manifest의 소스/지도/spec와 현재 v1.8/off 일치를 검사한다. 다른 작업이 현재v1.8을 바꾸면 기준을 조용히 새로 만들지 않는다.

| 지도 묶음 | 지도 | 각 arm 판 수 |
|---|---|---:|
| 번들 | arena, big_empty, Colosseum, default_small, stronghold | 20 |
| 온라인 | trophy, portals, slithery_fight | 12 |
| sprint | around_unsw, australia, stripes | 12 |
| 생성 | gen_S_03, gen_M_03, gen_M_07, gen_L_02, gen_R_01, gen_X_07 | 24 |
| identity OFF/현재v1.8 | trophy, around_unsw, gen_M_07 | 12 |

각 지도는 A/B × proxy4_king/hunter × seed1이다. 68짝136판 + identity12키24판 =160판. identity-base는 `versions/v1.8/bot`를 직접 사용한다. `bot-base`는 수정 전 소스/명령어 비교용이며 게임 lane에는 사용하지 않는다. 17지도와 68키는 기존 exp/freecost와 정확히 같다. 시드2/모든 생성 지도는 범위 밖이다.

`analysis.json`의 expectedGames=160, pairs=68, identity=12, missing/errors/unexpected=0을 확인한다. rows는 마지막 깨끗한 줄을 쓰며 historyErrors·duplicates를 숨기지 않는다. 회복된 오류도 오류0 요구에 포함한다. firstdiv.inventory의 양 arm keys=68 및 summary.errors=0을 별도 대조한다. replay/rows/log를 보존한다.

## 1. 가격 발동·무료 다중 이동 몫·의도한 판면

`analyze.js`는 `mass_ledger.perGame(...,rules:'123')`의 차례 시작 길이와 출력 MOVE를 양쪽에서 똑같이 센다.

- `turnsL5`: L>=5인 우리 차례 수(모든 action 종류 포함).
- `freeMulti`: `1<steps<=ceil(시작L/4)`인 MOVE 시도 수; 사망 시도도 포함한다.
- `completedFreeMulti`: 위 시도의 실제 완주 수. `multi/completedMulti`는 전체 다중 이동 분모다.
- `rate=freeMulti/turnsL5`, 기회0이면 null이다. `bands`는 L2–4/L5–8/L9–12/L13+의 차례·무료 다중 시도·완주 수다.

**게이트:** 합계의 무료 다중 이동 몫 ON>OFF. 각 arm의 sum(freeMulti)/sum(turnsL5)로 계산하며 키별 rate의 단순 평균으로 대신하지 않는다. 시도 증가가 사망 시도뿐인지 완주 수로 구분한다. 모든68키·지도/편/상대·L구간의 분모와 값도 보고한다. 기회가 없거나 몫이 오르지 않으면 미확인이다. 승패·최종 길이로 보완하지 않는다.

`firstdiv.rows`에서 같은 최초 입력의 L5+ 무료2/무료3 선택을 찾는다. 옛/new dirs·시작 몸·진주·매 걸음 머리/꼬리·실제 사망/완주를 함께 확인한다. 가격 차이는 `1.6*((steps-1)-max(0,steps-ceil(L/4)))`로 계산한다. L5/2는+1.6, L9/3은+3.2, L13/4는+4.8; L4/2는 변화0이다. L4가 첫 진주로 L5가 되어도 무료 수는1이다. 새 비용을 더 저렴한 다른 경로와 비교할 때 각 선택의 길이/걸음 수를 따로 계산한다.

후보 생성은 기존 p2 진주/탈출/late/strike gate와 순서가 그대로다. `paidSteps()`는 가격과 분리하여 그대로 두었고, 모든 SPRINT_COST 승수만 `pricedPaidSteps()`를 쓴다. 자기 kill reach는 free+L-2이나 STRIKE_MAX_STEPS=4, 시작L>=4이므로 기존 cap과 모든 유효 길이에서 동일하다. 적 reach/Q2b 변경 사례가 나오면 이번 코드 외 원인을 조사한다.

실제 판면 명령은 해당 key/map/side/좌표/round를 대입한다(라운드 시작 판면이며 차례 순서는 firstdiv.turn으로 확인).

```sh
UNSW_RULES=123 node eval/board.js exp/freecost2/on/games/KEY_WITH_UNDERSCORES/game.replay MAP_NAME a SIDE R,R_PLUS_1
UNSW_RULES=123 node exp/w7/tunnelpic.js exp/freecost2/on/games/KEY_WITH_UNDERSCORES/game.replay MAP_FILE SIDE X,Y R_MINUS_1,R,R_PLUS_1 --r 6
UNSW_RULES=123 node exp/w7/tunnelpic.js exp/freecost2/off/games/KEY_WITH_UNDERSCORES/game.replay MAP_FILE SIDE X,Y R_MINUS_1,R,R_PLUS_1 --r 6
```

`bodyx` 공통 태그의 free/paid/endLength/startHash/endHash 및 unknown/unseen 분모를 양쪽 모두 보고한다. `startHashDrift/endHashDrift`는 기존 부분 관측/초기 꼬리/portal chain 한계와 분리한다. 실제 몸은 BODYX/BODYMEM2가 만들며 가격 스위치에 몸 갱신 코드가 없다. ON 전용 태그·거절 횟수를 목적 개선 게이트로 쓰지 않는다. 태그 없는 trade 사망은 시도 분모와 인과 검사를 통해 남긴다.

## 2. 같은 입력 변경 결정의 인과 게이트

**고정 게이트:** `firstdiv.summary.tables.changed[3].harm <= help`, `tables.queen[50].harm <= help`, **모든 harm의 원인 설명**. 변경 용은 각 키의 가장 먼저 바뀐 action 한 개다. 같은 R의 추가 용은 `rows[].changed`로 별도 공개하고 분모에 중복 합산하지 않는다.

R+k는 라운드 R+k의 시작이며 사망 라운드 R..R+k-1을 포함한다. harm=new만 사망, help=old만 사망, both/neither/censored도 그대로 보고한다. k1/3/10과 queen10/50 전체 표를 남기되 게이트는 changed3/queen50이다. 여왕은 초기 팀별 최저 id이며 양쪽에서 R 전에 이미 죽은 여왕은 별도 분모로 공개한다. 여왕50은 변경 이후 전체 정책의 효과로 해석한다.

각 첫 변경 키에서 다음을 확인한다.

1. `status=matched`, geometryIdentical/boardIdentical/facingIdentical/firstTurnBoardIdentical=true, ledger checks0. `firstActionDifferenceAll`도 그 R/id여야 한다. `prefixDifference`의 첫 다른 의미 있는 사건이 그 action인지 읽는다. 같은 R의 더 이른 소나/다른 용 행동 차이도 제외/미확인 사유다. firstdiv.summary의 이전 라운드 차이 검사만으로 같은 R의 차이를 놓치지 않는다.
2. 첫 `changed[0].turn.on/off`의 body/neighbors/action/fate/after를 읽는다. **new 이동 즉시 생존 여부와 old 선택의 독립123 oracle 즉시 사망 여부**를 전수 표로 남긴다. 같은 차례 판면에서는 ledger의 각 action simulation이 old/new oracle다. 둘 다 즉시 죽는 기존 no-exit/trade/feed를 새 사망으로 세지 않고 원인/의도를 그대로 설명한다. new만 즉시 죽으면 반드시 harm 설명 대상으로 추가한다.
3. changed k3 또는 queen k50에서 harm인 모든 키에 old/new 선택 이유(가격과 기존 threat/SA/DFS), 최초 차례와 이동 직후 판면, 실제 사망 직전/직후 판면, 선택한 경로/충돌 상대/진주/지급·회피 가능한 대안·의도적 먹이 여부를 기록한다. k3 이후에도 후속 결정이 다른지 명시한다. 판면이나 동일 입력을 검증하지 못하면 PASS로 바꾸지 않는다.
4. 첫 갈림 이후 실제 ON/OFF의 같은 round:id가 같은 입력이라는 가정을 하지 않는다. 원시 사망 증가와 여왕 수명 감소를 별도 harm로 세거나 게이트로 쓰지 않는다.

같은 관측·강제 과거 행동의 C++ 진단을 위해 다음 도구도 준비했다. BUILD에서 native 두 arm은 컴파일만 한다. 게임을 만들지 않는다.

```sh
nice -n 10 python3 exp/freecost2/build-audit.py
UNSW_RULES=123 nice -n 10 python3 exp/freecost2/run-audit.py > exp/freecost2/audit.log
```

`run-audit.py`는 firstdiv의 matched 키마다 최초 R의 모든 변경 id를 양 arm 원본 이력으로 읽는다. `replay-audit.js`는 관측·소나를 재구성하고 기록된 과거 action을 강제하여 두 실제 World/Planner에 넣는다. `audit/*.on/off.jsonl`의 R/id와 `*.snapshots.json`/`*.json`을 읽어 양쪽 start body·선택·독립 즉시 oracle를 확인한다. 첫 선택까지 BODYMEM2 기억이 같아야 한다. 이전 소나 전달·LENGTH·countdown/facing 입력도 확인한다. 미관측 countdown -1은 지도 maxGap0과 실제 누락을 구분한다.

이 진단의 `future3Rounds:'UNMEASURED'`는 native 강제 이력의 한계다. 후속 k3/k50은 **실제 게임 firstdiv**에서 측정한다. native clock/깊이는 production judge clock이 아니며 불재현 선택을 인과 증거로 세지 않는다. 진단에서 추가로 발견한 첫 갈림 뒤 변경은 새로운 matched 실험 표본이 아니다. 함수가 가격만 바꾸므로 frozen history의 World 몸/아군/소나 소스는 양쪽 동일하다. 실제 judge 첫 action과 맞지 않으면 그 native 선택은 보조 진단으로만 보고한다.

## 3. 지급 사망·오류·원자료 문맥

**게이트:** ON `oversprint=0`, `causes.sprintDeath=0`, 오류/timeout/no reply0. `raw.A`의 모든 death는 `deaths[].fate/action/indicator`와 실제 replay로 분류한다. 지급 실패와 malformed/no-action/illegal split을 뭉뚱그리지 않는다. OFF에도 같은 검사를 적용해 공개한다. `checks`의 모든 항은0이어야 한다. `turnActionGap/tle/missingAction` 및 historyErrors도 확인한다.

`keywise.tsv`와 `analysis.json.pairs`에 모든68키의 S/W/O/H/A 양 arm, 여왕 lifetime/longer/shorter/same/delta/censoring을 기록한다. 기제 사망 sac/trap/rammed/ram/enemyBody/allyHead/fault/sprintDeath도 양방향으로 report한다. 합계가 유리해도 단축/증가 키를 생략하지 않고, 키별 증가가 있어도 그 자체로 채택을 거부하지 않는다. 이것은 문맥만이다. 여왕 사망=그 round, 게임 종료 생존=마지막round+1이며 조기 종료 생존을 r500 생존으로 바꾸지 않는다.

## 4. OFF 동일성·CPU·탐색

`compile-check.json`: 수정 전 bot-base와 bot-off **536250 bytes**, SHA256 `1363a4b2c686cca0f66f696e367fea3812757521df001329820a0fe729b831fe`로 바이트 동일. ON537285 bytes. 공식 judge clang 결과이며 게임 사건/CPU 검사를 대신하지 않는다.

`identity.txt`의 12/12 IDENTICAL 및 `analysis.json.identity`의12 same=true가 필요하다. fingerprint는 이동/사망/진주/분열/소나·메시지 사건을 포함하고 indicator/log/draw/명령어 수를 제외한다. 행 누락이 양쪽에 있으면 intersection만 보는 identity.js가 놓칠 수 있으므로 analysis의 expected/missing 검사를 먼저 확인한다. OFF/현재v1.8의 소스 일치도 validator로 확인한다.

모든160판의 `cpuMaxM`은 우리 팀 points per turn의 최대다. null은 미측정이며0으로 채우지 않는다. 80M 이상은 경보·원인 조사, 100M 초과/timeout/no reply는 깨짐이다. 완료 DFS `depth[round:id]`와 누락 수를 보고한다. firstdiv 이전의 동일 차례와 native 동일 관측 진단 깊이를 우선 대조한다. 갈림 이후 공통 round:id의 lower/same/higher는 입력이 달라진 문맥으로만 쓴다.

## BUILD 검증과 결과 작성

```sh
nice -n 10 ../UNSW/.venv-ppo/bin/python3 exp/freecost2/build.py
nice -n 10 python3 exp/freecost2/check-fixtures.py
python3 exp/freecost2/validate.py
```

양 arm 각각 가격5080·capped reach125·몸/지급762 합성 검사 통과. 기존 BODYMEM2 Colosseum 기보1개의 분석 연결 점검은 `analysis-smoke.json`(ledger checks 전부0)이며 이번 FREECOST2 성과가 아니다. source-manifest/validation은 게임0·CPU 미측정을 명시한다.

`RESULT.md`에는 각 사전 기준의 값/N/판정/한계와 실제 판면 최소2장, 무료 몫 → 첫 변경 인과 표와 모든 harm 설명 → 지급/오류 → identity/CPU → 모든 키 양방향 문맥 순서로 작성한다. 미측정·불재현·censored를0/성공으로 채우지 않는다. 결과와 제안은 조정자에게 넘기며 기본값을 자동으로 켜지 않는다.
