# BODYMEM2: 실행 뒤 분석 절차

기준은 `versions/v1.8/VERSION.md` §21이다. BODYMEM2_ON만 ON/OFF로 다르고 BODYMEM_ON=false, BODYX_ON=true와 다른 기본값은 같다. 이 BUILD에서는 게임·커밋·네트워크를 실행하지 않았다. 아래 게임 실행 명령은 조정자가 샌드박스 밖에서 실행한다.

```sh
node exp/bodymem2/runq.js exp/bodymem2/spec.json --jobs 3 --cap 6
```

runq14 형식 사본이며 `tools/unswbc123`, 상대 경로, CPU `-v`, machine cap6, disk21GiB, nice10을 지원한다. 원 runq14.js는 상대 경로/CPU/123을 모두 지원하지 않으므로 이 사본을 쓴다. 소스/지도/스펙 동결 해시는 validation.json에 있다. 실행 중 빌드를 바꾸지 않는다.

## 1. 자료·동일성·CPU: 기준4

```sh
python3 exp/bodymem2/validate.py
UNSW_RULES=123 nice -n 10 node exp/bodymem2/analyze.js
UNSW_RULES=123 nice -n 10 node tools/firstdiv.js exp/bodymem2/on exp/bodymem2/off --out exp/bodymem2/firstdiv.json
```

명세는 BODYMEM과 같은21지도 × A/B × king/hunter × seed1이다. bundled5(40판), online7(56), sprint3(24), generated6(48), identity24 =192판. on/off84짝, identity12키다. identity는 Trophy/Around UNSW/M_07 × A/B × 두 상대이며 bot-base는 작업 시작 v1.8 동결본이다. rows.jsonl의 키별 마지막 clean row(exit0/result 있음/error·botProblem 없음)만 선택하고 실패 이력도 별도로 남긴다. expectedGames192, missing0, pairs84, identity12, 모든 ledger checks0, oracleDrift0, stepDrift0을 확인한다. 같은 키라도 replay/row가 빠지면 미확인이다.

compile-check.json의 base/off WASM 바이트 동일과 analysis.json의 identity12/12 사건·소나 동일을 둘 다 요구한다. fingerprint는 지시 문자열/log/CPU instructions를 제외하고 action/이동/분열/사망/진주/메시지는 포함한다. BASE/off 크기·SHA와 모든 다른 스위치 보존도 validate.py로 확인한다.

모든192판의 우리 팀 points per turn이 존재하고 최대80M 미만(한도100M), timeout/no reply/오류0이어야 한다. null/미측정은 통과시키지 않는다. 탐색 완료 깊이 lower/same/higher도 보고하되 첫 행동 변경 뒤 깊이 차이는 순수 CPU 비용 비교가 아니다. 같은 입력 production 재생이 가능하면 old/new 완료 깊이·points도 남긴다. native 재생의 벽시계/깊이를 judge clock으로 주장하지 않는다.

## 2. 자기 몸 drift·범위 유지: 기준1

analyze.js는 양 arm 모두 같은 기존 BODYX 태그를 읽는다. 이 사본은 **사망한 다중 시도도 시작 태그를 검사**하며 완주에서 끝 몸·제거 수·매 걸음 head/tail을 독립123 oracle와 비교한다.

```text
bodyx<free>,<paid>,<endLength>,<unknownStartSlots>,<startHash>,<endHash>,<unseenPathTiles>
```

head→tail 타일 t=y*W+x의 hash는 32bit FNV(h=2166136261, h=imul(h XOR t,16777619))다. on/off 각각 multi(사망 포함), completed, predicted(시작 태그 있음), missingTags, startBodyDrift, endBodyDrift, unknownInput, unseenPearls 분모를 보고한다. 태그가 없는 trade/조기 반환을 성공으로 세지 않는다. 기준은 이번 OFF에서 이번 ON의 시작 drift가 줄어0을 향하는지와 완전히 추적 가능한 시작/다음 관측 전체 배열 drift0이다. ON 전용 bodymem2r는 지급 거절 발동의 하한일 뿐 효과 게이트가 아니다. 끝 예측만 다른 미관측 섭취, 시작부터 틀린 몸, 초기 긴 몸의 직선 추정, unknown 슬롯을 분리한다. 해시 비교만으로 배열 동일을 확정하지 않는다.

전체 배열 확인에는 같은 source history의 관측·소나·echo·기록 행동을 양 World로 강제 재생한다.

```sh
nice -n 10 python3 exp/bodymem2/check-fixtures.py
nice -n 10 python3 exp/bodymem2/check-replay.py
UNSW_RULES=123 nice -n 10 node exp/bodymem2/replay.js exp/bodymem2/on/games/bot-hunter_default_A_1/game.replay A exp/bodymem2/audit/default-on 14
UNSW_RULES=123 nice -n 10 node exp/bodymem2/replay.js exp/bodymem2/off/games/bot-hunter_default_A_1/game.replay A exp/bodymem2/audit/default-off 14
```

replay.js 마지막 인자를 생략하면 해당 팀의 모든 id다. 실제 source의 모든 관측/기록 action을 양 World에 넣는다. `.input`, `.on/off.jsonl`, `.json`에 같은 과거 행동 아래 실제 시작/예측 배열·실제 몸·native 선택·즉시 oracle가 남는다. 모든 drift 키, 부분 시야 성장/포털 키 및 bundled·online·sprint·generated의 대표 완주 키에 실행하고 양 원본 arm에서 각각 재생한다. countdown/facing 누락·모호함이 있으면 미확인으로 남긴다. native 내부 Planner 상태/clock이 production과 다를 수 있으므로 즉시 oracle는 재현한 선택에만 해당한다.

합성 fixture는 시작 L2–64/2–8걸음의 직접/미관측 진주, 무료/유료, 다음 LENGTH, 지급 순서/중복, 단일 no-op, 원격 포털 경로 이후 몸 복원 및 아군 관측/direct·relay/occupancy/fresh cache를 점검한다. fixture-check.json의 allySnapshot이 on/off 동일해야 한다. 단일 이동·분열은 v1.8 그대로이며 기능 효과에 섞지 않는다. main의 소나 계산/ingestDragons/ingestSonar/computeFreshAllies는 BASE와 소스 동일임도 validation.json에 기록한다. 다른 행동 뒤 달라진 실제 아군 캐시를 코드 회귀로 단정하지 않는다.

## 3. 지급 사망·의도한 판면: 기준1·3

ON의 causes.sprintDeath/oversprint는0이어야 한다. raw A는 원시 이벤트·action과 대조하여 지급 실패/invalid split/무출력/timeout을 모두 설명한다. 지급 직전 길이2면 마지막 진주도 선지급에 쓸 수 없다. trade의 마지막 걸음 지급도 검사한다. 오류/no reply/timeout0을 요구한다.

기존 실패 입력(새 게임이 아님)을 보조 대조한다.

```sh
UNSW_RULES=123 nice -n 10 node exp/bodymem2/replay.js exp/bodyx/on/games/bot-hunter_default_A_1/game.replay A exp/bodymem2/audit/default-original 14
```

#14 r188 L2 NW는 첫 미관측 진주 없으면 두 번째 유료 걸음 A다. guard는 거절하고 지급 가능한 대안을 골라야 한다. 이번 직접 본 첫 진주면 허용, 마지막 진주뿐이면 거절, L5의 무료2/진주 없이 지급 가능한 다중 이동은 허용임을 fixture와 같은 입력으로 확인한다.

L8 무료2(길이8/정상 꼬리 전진2), L14 무료3(길이14/전진3), 진주를 먹은 유료 걸음, 미관측 성장 후 LENGTH prefix 복원의 실제 차례 전/매 걸음 후/다음 관측 판면과 배열을 남긴다. 처음 보는 bundled/generated 및 인식 끈 online/sprint 대표를 포함한다.

```sh
UNSW_RULES=123 node exp/w7/tunnelpic.js REPLAY MAPFILE A X,Y R0,R1,R2 --r 4
UNSW_RULES=123 node eval/board.js REPLAY MAP_NAME a A R0,R1,R2
```

그림은 라운드 시작이므로 id순서·dragonUpdate·실제 차례 snapshot도 함께 읽는다.

## 4. 첫 변경 결정 인과 게이트: 기준2

firstdiv.json을 사용한다. `summary.tables.changed[3]`의 harm <= help, `summary.tables.queen[50]`의 harm <= help, **모든 harm의 원인 설명**을 요구한다. firstdiv의 changed 집계는 라운드/차례 순서상 첫 변경 용 하나/키이며 같은 R의 추가 changed[]도 전수 별도 공개한다. k=3은 R+3 시작(사망 R..R+2), k=50은 R+50 시작(사망 R..R+49)이다. 의도적 먹이기 harm도 원 합계에 유지하고 목적만 표시한다. censored는 생존으로 세지 않는다. no_divergence는 분모와 별도 보고하며 측정 기회0을 효과 통과로 쓰지 않는다.

오류/누락/start state mismatch/turnBoardIdentical=false를 전수 점검한다. boardIdentical은 R 시작 전체 몸·진주·geometry·facing, firstTurnBoardIdentical은 변경 용 실제 차례 판면이다. earlier prefixDifference(소나/입력 이력)는 같은 입력이라는 주장과 별도로 공개한다. 이전 소나가 다르면 해당 양 실제 이력 각각을 같은 강제 과거 행동으로 replay.js 양 스위치에 넣어 기억/선택 원인을 진단하고, 재현하지 못한 원인은 미확인으로 남긴다. 이후 정책/다른 용 선택도 변하므로 queen k50을 첫 행동 하나의 고정 개입 효과로 주장하지 않는다. 이 게이트의 인과 범위는 최초 동일 물리 상태에서 시작한 두 정책의 후속 결과다.

각 changed 행에서 old/new action과 indicator, 새 선택의 자기 이동 완주, 옛 선택의 즉시123 oracle 사망 여부·이유/걸음/잔존 몸, k1/3 fate를 표로 작성한다. firstdiv의 turn.on/off.action·fate·after와 fates는 실제 선택/결과이고, 반대 선택 oracle는 replay.js 또는 독립123 시뮬레이션으로 같은 완전한 차례 snapshot에서 평가한다. input 불완전/native 선택 불일치를 숨기지 않는다. 새 선택이 즉시 죽은 사례도 누락 없이 설명한다.

changed k3 또는 queen k50 harm인 모든 키는 R/id, on/off choice/표식·원인, 물리 차례 상태/몸/진주/소나, 이동 직후와 첫 사망 실제 판면, 상대 행동·아군 몸·자기 기억·지급 관문 중 선택을 바꾼 경로를 남긴다. `exp/firstdiv/RESULT.md` BODYMEM harm8 및 memory-cache-ablation.json의16개 과거 복원 결과는 이번 기능 분리 근거이며 이번 게이트 성공으로 세지 않는다. 아직 설명하지 못한 harm이1개라도 있으면 이 항은 미확인이다.

## 5. 문맥 보고·판정

analysis.json과 keywise.tsv의84키를 빠짐없이 보고한다. raw S/W/O/H/A 및 기제별 사망 counts on/off, queenLifetime on/off, longer/shorter/same 키 수와 변화량, censoring을 모두 낸다. 여왕은 실제 팀 최저 초기id이며 생존은 마지막 round+1로 표시한 관측 종료다. 이 원시 수치·새/조기 사망·승패·총길이는 게이트가 아니다.

`exp/bodymem2/RESULT.md`는 발동/지급·실제 판면 → 양 arm 공통 태그 시작 drift/전체 배열 → firstdiv 두 threshold와 harm 전수 설명/즉시 oracle → 원시 counts·여왕 수명 양방향 문맥 → identity → CPU/오류 순서로 쓴다. PASS/FAIL/미확인과 분모를 각각 남긴다. 새 게임은 이192판 범위뿐이며 추가 시드/설정은 별도 사전 등록이 필요하다. 스위치 변경/채택/커밋/업로드는 조정자가 한다.
