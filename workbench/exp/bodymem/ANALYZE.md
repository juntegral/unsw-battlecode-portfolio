# BODYMEM 외부 실행 뒤 분석

사전 기준은 `versions/v1.8/VERSION.md` §19다. `BODYMEM_ON=false`가 저장소 기본값이고 BODYX는 양 arm 모두 true다. FREECOST/다른 스위치/이동 가격은 보존했다. BUILD는 컴파일·합성 검사·기존 replay 읽기만 했다. 다음 결과로 사전 기준을 바꾸지 않는다.

## 1. 실행·완전성·동일성

조정자가 저장소 루트에서 실행한다. 게임 실행 전 기계 전체 동시6판 미만과 디스크21GiB 이상을 확인한다. `runq.js`는 runq14 형식을 받는 기존 BODYX runner 복제다. 상대 경로, 1.2.3 엔진, CPU 수집을 지원한다. 원래 runq14는 `exp/q2/bot-hunter`를 bots 아래로 해석하고 CPU 옵션을 읽지 않으므로 복제본을 사용한다.

```sh
node exp/bodymem/runq.js exp/bodymem/spec.json --jobs 3 --cap 6
UNSW_RULES=123 node exp/bodymem/analyze.js
UNSW_RULES=123 node exp/v16/identity.js exp/bodymem/id-off exp/bodymem/id-base > exp/bodymem/identity.txt
```

| 묶음 | 지도 | 판 수 |
|---|---|---:|
| 번들 | arena, big_empty, Colosseum, default_small, stronghold | 40 |
| 온라인 | default, schooltime, trophy, portals, slithery_fight, autarky, prisoners_dilemma | 56 |
| 스프린트 | around_unsw, australia, stripes | 24 |
| 생성 | gen_L_03, gen_X_07, gen_S_03, gen_M_07, gen_R_01, gen_L_02 | 48 |
| off/base 동일성 | trophy, around_unsw, gen_M_07 | 24 |

A/B × proxy4_king/hunter × seed1이며 총192판, on/off84짝, off/base12짝이다. 각 rows.jsonl에서 키별 마지막 깨끗한 row(G 존재, exit0, error/botProblem 없음)를 고르고 실패 이력을 함께 보고한다. analysis.json의 expectedGames192/missing0/historyErrors, pairs84/identity12를 확인한다. spec의 name은 설명이고 out+opponent basename+map+side+seed가 실행 키다. bot-base는 작업 시작 v1.8 동결본이며 identity-base lane이 사용한다.

동일성은 base/off 공식 WASM 바이트 동일과 12키 사건·음파 동일을 둘 다 요구한다. fingerprint는 지시 문자열/log/CPU instructions를 제외하지만 action/분열/이동/사망/진주/메시지는 포함한다. SHA-256은 compile-check.json, 소스/복제본/경로/키 검사는 validation.json에 있다. 판 실행 동안 동결 빌드를 수정하지 않는다.

## 2. 몸 기억 drift: 반드시 양 arm의 같은 표식

analyze.js는 `tools/mass_ledger.js`의 rules123 재구성으로 차례 직전 실제 몸을 얻고 모든 완주 다중 MOVE의 C++ 전이/독립123 oracle/dragonUpdate 머리·꼬리를 비교한다. 모든 ledger checks, oracleDrift/stepDrift/update 누락은0이어야 한다. 전이 호출용 transition-on은 실제 BODYX 함수를 쓰며 관측 기억 검사를 대신하지 않는다.

양 arm 모두 BODYX가 켜져 다음 **동일한 기존 표식**을 낸다.

```text
bodyx<free>,<paid>,<endLength>,<unknownStartSlots>,<startHash>,<endHash>,<unseenPathTiles>
```

시작/끝 해시는 head→tail 타일 t=y*W+x의32비트 FNV(h=2166136261, h=imul(h XOR t,16777619))다. `startBodyDrift`는 실제 차례 시작 해시와 다른 경우, `endBodyDrift`는 끝 길이/해시가 다른 경우, `memoryDrift`는 합집합이다. `multi`(사망 시도 포함)/`completed`/`predicted`/`missingTags` 분모를 ON/OFF 둘 다 낸다. ON 전용 bodymemr 태그는 거절 발동의 하한일 뿐 개선 게이트가 아니다. trade/조기 반환처럼 표식 대상이 아닌 다중 이동은 표식 없음으로 따로 남긴다. unknownStartSlots, 초기 긴 몸 직선 추정, 미관측 경로, 진주 오인, 실제 첫 입력부터의 오류를 숨기지 않는다.

OFF의 약121/3504는 이전 BODYX 표본의 참고값이다. 이번 짝에서는 **이번 OFF 분모/시작 drift**와 ON 값을 직접 비교한다. 완전하게 추적한 차례에서 ON 시작/다음 관측 전체 배열 drift0을 요구하고, 전체 표본에서는0을 향해 줄어드는지 본다. 미관측 성장 때문에 끝 예측만 다른 건은 입력 기억 drift와 분리한다. 실제 다음 LENGTH로 복원됐는지 확인하며 끝 오차를 성공으로 세지 않는다.

해시 충돌 가능성이 있으므로 불일치·미관측 성장·부분 관측·포털 사례의 실제 World 배열도 재생한다.

```sh
nice -n 10 python3 exp/bodymem/check-fixtures.py
nice -n 10 python3 exp/bodymem/check-replay.py
UNSW_RULES=123 nice -n 10 node exp/bodymem/replay.js exp/bodymem/on/games/bot-hunter_default_A_1/game.replay A exp/bodymem/audit/default-on 14
UNSW_RULES=123 nice -n 10 node exp/bodymem/replay.js exp/bodymem/off/games/bot-hunter_default_A_1/game.replay A exp/bodymem/audit/default-off 14
```

replay.js의 마지막 인자는 선택 id 목록이며 생략하면 그 팀 전체다. 각 source replay의 같은 7×7 창/부분 bodies/포털 edges/실제 받은64비트 메시지/echo/기록 행동 이력을 ON/OFF 양쪽 World에 입력한다. 이동/분열은 기록된 행동으로 강제하므로 다른 길을 고른 뒤 실제 게임의 같은 round/id를 같은 입력으로 오인하지 않는다. `.input`에 재생 입력, `.on/off.jsonl`에 실제 World 시작/예측 배열과 native 선택, `.json`에 실제 몸 대조/즉시 oracle/불확실성을 남긴다. countdown 누락·몸 facing 추론이 모호하면0으로 감추지 않고 미확인이다. 초기 긴 몸/프로세스 재시작은 따로 확인한다. native 선택은 judge point clock/깊이와 다를 수 있고 각 native Planner가 과거 진단 선택에 따라 내부 상태를 갱신하므로 **무해함 PASS의 근거로 쓰지 않는다**. 몸 배열의 실제 함수를 확인하는 진단 도구다.

합성 fixture는 시작L2–64/1–8걸음의 무료·유료·진주·미관측 진주/다음 실제 LENGTH/가격 보존, 지급 전L2/마지막 진주 선지급 불가/중복 섭취, 포털 아군 chain와 direct 보고/오래된 relay를 확인한다. on resyncDrift0이며 off도 같은 사례/분모로 기록한다. 실제 main의 split/SONAR는 replay의 dragonSplit와 sonarPing에서 부모 길이/머리/chain/보고 길이를 추가 대조한다. 포털 밖 진주를 먹은 이동의 보고는 보수적 추정일 수 있으므로 실제 길이보다 작게 보고한 경우도 별도로 센다. 관측하지 않은 아군 경로 전체를 head/length 메시지로 재구성할 수 있다고 주장하지 않는다.

## 3. 지급 사망·발동·판면

양 arm의 oversprint, causes.sprintDeath, 원시 A를 전수 확인한다. ON payment/sprint deaths0, malformed/no reply/timeout0이 필요하다. intentional trade도 마지막 걸음의 지급 검사 전에 죽으면 지급 사망이다. bodymemrN은 거절 후보 수의 하한이고 최종 MOVE 선택 단계에만 나타난다. 표식이 없는 조기 split/return을 발동 없음으로 단정하지 않는다.

기존 실패 입력을 먼저 재검증한다(새 게임 아님).

```sh
UNSW_RULES=123 nice -n 10 node exp/bodymem/replay.js exp/bodyx/on/games/bot-hunter_default_A_1/game.replay A exp/bodymem/audit/default-original 14
```

#14 r188 L2: OFF NW는 첫 미관측 포털 칸에 진주가 없는 실제 판에서 두 번째 유료 걸음 A로 죽어야 하고, 새 관문은 그 후보를 거절해야 한다. 알려진 첫 진주로L3가 되면 유료 두 번째는 허용한다. 마지막 걸음 진주로 그 걸음 비용을 선지급할 수 없고, 미관측 경로라도 진주 없이 이미 지급 가능하면 허용한다. 일반 무료 두/세 걸음도 유지한다.

판면은 L8 무료 두 걸음, L14 무료 세 걸음, 진주를 먹은 유료 걸음, 부분 관측/포털 후 다음 관측, split 부모와 아군 보고 사례를 각각 남긴다.

```sh
UNSW_RULES=123 node exp/w7/tunnelpic.js REPLAY MAPFILE A X,Y R0,R1,R2 --r 4
UNSW_RULES=123 node eval/board.js REPLAY MAP_NAME a A R0,R1,R2
```

tunnelpic은 라운드 시작 판면이므로 실제 차례의 id순서/걸음별 dragonUpdate/World 배열도 함께 읽는다. 무료 걸음에는 정상 꼬리 전진만, 진주에는 정상 꼬리 유지, 유료 걸음에는 추가 꼬리 제거가 보여야 한다. 잔존 drift/지급 사망/잘못된 아군 길이를 전수 조사한다.

## 4. 다른 곳 무해함: 변경 결정의 인과 검사

raw counts/queen lifetimes는 `analysis.json`과 `keywise.tsv`에서 모든84키의 원시 S/W/O/H/A 및 기제별 사망을 양 arm 그대로 보고한다. 여왕은 초기 팀별 최저id이며 queenLifetime(사망은 그 round, 생존은 마지막 round+1)/관측 종료(censoring)를 함께 보고한다. 연장/단축/동일 키 수와 각각의 크기를 모두 낸다. 새·조기 여왕 사망도 문맥으로 남기되, ON/OFF 첫 변경 뒤 키별 사망 증가율≈50%를 무해함 게이트로 쓰지 않는다. 승패도 게이트가 아니다.

**판정용 변경 결정 테이블은 다음 절차로 별도로 만든다.** replay.js가 찾은 native 변경은 후보 목록일 뿐이다. 각 source ON/OFF 이력에서 judge clock으로 production 선택을 재현하고, 실제 선택과 탐색 깊이를 재현한 자료만 테이블에 넣는다. 재현하지 못한 행은 누락으로 보고하며 통과로 세지 않는다.

1. 변경 직전 관측/메시지/echo와 과거 실행 행동을 고정한다. 기억 효과는 같은 관측·강제 행동 이력을 각 World 스위치로 갱신한 결과를 비교한다. guard의 순수 효과는 **동일 World/Planner snapshot**에 관문만 개입해 검사한다. 같은 r/id라는 이유로 갈라진 두 게임의 상태를 합치지 않는다. 과거 Planner 내부 상태까지 맞춘 judge replay harness가 필요하다.
2. 같은 실제 차례 직전 전체 bodies/pearls/edges/id순서를 독립123 oracle에 넣고 old/new 선택을 각각 수행한다. 지급은 시작L의free를 고정하고 지불 가능성 → 충돌 → 성장 → 추가 꼬리 제거 순서다. new가 자기 이동을 완주해야 한다. old가 죽었는지와 이유/걸음/몸도 남긴다. split도 min2/unitLimit과 부모 생존을 검사한다. 의도적 죽음으로 바뀐 결정 역시 행을 빼지 않는다.
3. 같은 snapshot에서 두 fork를 다음3라운드(해당 용의 다음3차례)까지 진행한다. 외생 아군/상대 행동·spawn 시도를 동일하게 고정하고, 초점 용의 다음 관측은 **각 fork의 실제 상태**에서 생성해 production 정책으로 선택한다. recorded tileChange를 그냥 덮어쓰지 않는다(다른 body 때문에 spawn이 막힐 수 있고 죽음 드롭도 달라진다). 상대의 기록 행동이 실행 불가능해지거나 spawn RNG/프로세스 상태를 복원할 수 없으면 해당 행은 미확인이다. 새 선택만 죽고 옛 선택은 살아 있는 행이0이어야 한다. 새 선택 때문에 여왕이 죽는 경로도 따로 표시한다.
4. `causal-decisions.jsonl`에 source key/arm/r/id/input hash/관측·기억·Planner 상태/old/new action/동일 입력 judge 깊이·CPU/immediate survival/old oracle death/future3-round fate/completeness를 남긴다. `causal-boards/`에 실제/old/new 차례 직전·이동 뒤·첫 사망 판면을 남긴다. 모든 변경 결정이 살아 있고 후속 회귀0인지 분모와 함께 판정한다.

현재 제공한 replay.js는 전체 입력·몸 배열·native 선택·**즉시 oracle**까지의 진단을 자동화한다. judge-clock 선택 재현과3라운드 fork 실행기는 제공하지 않는다. 따라서 spec 게임과 이 진단만 끝나도 §19의 무해함 기준은 **미확인**이며 채택 PASS를 낼 수 없다. 분석 단계에서 이 실행기를 만들거나 조정자의 상태 fork 도구를 써서 위 절차를 완료해야 한다. 전체 게임 재실행이나 diverged raw counts로 대체하지 않는다.

## 5. CPU·오류·인계

모든192row에 우리 팀 points per turn 측정이 있어야 한다. 우리 팀 최대80M 미만,100M 한도/timeout/no reply/오류0을 요구한다. 누락/null은 미검증이다. analyzer의 공통 round/id 완료 깊이 lower/same/higher는 문맥이며, 첫 선택 변경 이후의 깊이 차이는 순수 비용 비교가 아니다. 비용은 위 동일 입력 judge 재현에서도 따로 재야 한다. 새 World history의deque 복제/portal chain 검사 비용과 새로운 관문이 탐색 완료 깊이를 낮추는지 확인한다.

`exp/bodymem/RESULT.md`에 발동/지급 → 양 arm 시작 몸 drift와 실제 배열·판면 → 변경 결정의 인과 안전(완료/미확인 포함) → 원시 counts/여왕 수명 양방향 문맥 → 동일성 → CPU/오류 순서로 쓴다. 한 번의 시드1/21지도 표본이고 추가 시드/지도는 이192판 명세 밖이다. 사전 기준을 결과 뒤 수정하지 않는다. 기본값 변경/채택/커밋/업로드는 조정자가 한다.
