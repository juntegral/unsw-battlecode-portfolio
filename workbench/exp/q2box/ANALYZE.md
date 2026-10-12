# Q2box 실행 뒤 분석

BUILD 단계에서는 게임을 실행하지 않았다. 사전 기준은 `versions/v1.8/VERSION.md` §10이다. 모든 아래 명령은 저장소 루트에서 실행한다. 승패·총 길이는 채택 기준으로 쓰지 않는다.

## 1. 실행과 원자료 정리

```sh
node exp/q2box/runq.js exp/q2box/spec.json --jobs 3 --cap 6
```

이 runner는 runq14 형식을 유지한 Q1 runner 사본이다. `exp/q2/bot-hunter` 경로와 `cpu:true`를 지원한다. 원래 `exp/v14/runq14.js`는 상대 앞에 `bots/`를 붙여 hunter를 잘못 찾고 CPU 옵션을 읽지 않으므로 이 사본을 쓴다. 각 게임에 nice -n 10, 기계 전체 6판 제한, 디스크 21GiB 확인이 적용된다.

| lane | on/off 각각 판 수 | 지도·상대·시드 |
|---|---:|---|
| hunter22 | 44 | 온라인 10 + 번들 5 + 스프린트 7, hunter, 시드 1, 양편 |
| king15 | 30 | Around UNSW + 시작 주머니 3 + 번들 5 + 생성 6, king, 시드 1, 양편 |
| around-seed2 | 4 | Around UNSW, king·hunter, 시드 2, 양편 |
| identity-off/base | 각각 12 | Trophy·Around UNSW·gen_M_07, king·hunter, 시드 1, 양편 |

총 180판 = on/off 짝 78키(156판) + 동일성 12키(24판). 생성 6지도는 S_03, M_03, M_07, L_02, R_01, X_07이다. 각 lane의 명시적 `only`가 지도 수를 고정한다. 시드 2의 전 지도 회귀나 다른 시드는 이번 명세가 검증하지 않는다.

`rows.jsonl`을 지우지 않는다. 분석 도구는 `G` 있음·exit 0·error/botProblem 없음인 마지막 줄을 키별로 택한다. 깨끗한 줄과 기보가 없는 키는 missing이다. 실패 이력은 historyErrors로 따로 남는다. 아래 도구가 missing 0과 identity 12/12를 보고하기 전에는 분석 완료로 쓰지 않는다.

```sh
UNSW_RULES=123 node exp/q2box/analyze.js > exp/q2box/analysis.txt
```

결과는 `exp/q2box/analysis.json`이다. `sets.*.*.checks`의 sim/splits/drops/ledger/final 등 재구성 검사값은 모두 0이어야 한다. 이 도구는 queen id를 초기 팀 최저 id에서 찾으며 `side A = id 0`을 가정하지 않는다.

## 2. 비봉쇄 대안이 있으면 seal 금지

`sets.on.<key>.seals`와 off의 같은 키를 비교한다. 매 아군 차례 시작에 여왕 출구의 빈 칸 수를 기록하고, 실제 1.2.3 이동 뒤 생존한 조각의 몸이 모든 출구를 막았는지 잰다. 머리 끝점만 보지 않는다. seal 원자료에는 id, round, free/exits, 여왕 좌표, 선택 action, indicator, visible, nonsealSingles가 있다.

- 목표: 우리 조각 seal 약 0. 특히 보이는 여왕에게 `nonsealSingles`가 하나 이상인 seal은 0이다. 이 목록은 물리적으로 가능한 단일 걸음의 보수적 증거다. 값을 보지 않아 음수·죽음 예측 대안도 포함한다.
- `qbs<n>`는 후보 금지 수다. 표식 수만으로 seal 감소를 판정하지 않는다. 표시된 이동 뒤 실제 빈 출구와 몸을 확인한다.
- 도구는 기보 전체 시야를 사용한다. `visible:false` seal은 봇이 여왕을 못 본 경우로 나눈다. 포털·창 가장자리 출구는 그 차례 7×7 관측에서 알려져 있었는지 직접 확인한다. 전체 기보에서 보이는 대안을 봇도 알고 있었다고 단정하지 않는다.
- seal이 남으면 해당 차례에서 모든 생성 후보를 검토한다. 단일 걸음 대안 외에 질주·교환·미지 포털 대안도 확인한다. 단일 대안이 없다는 이유만으로 대안 부재를 확정하지 않는다. 대안 없는 seal은 수와 판면을 별도로 보고한다.

Around UNSW의 벽을 포함한 판면은 다음과 같이 뽑는다. X,Y는 analysis.json의 seal.qh 또는 queenHeads/death.head에서 가져온다.

```sh
UNSW_RULES=123 node exp/w7/tunnelpic.js exp/q2box/on/games/bot-hunter_around_unsw_B_1/game.replay exp/q2box/maps/around_unsw.map B X,Y 2,3,4,5,6,7 --r 4
UNSW_RULES=123 node exp/w7/tunnelpic.js exp/q2box/off/games/bot-hunter_around_unsw_B_1/game.replay exp/q2box/maps/around_unsw.map B X,Y 2,3,4,5,6,7 --r 4
```

이 도구는 라운드 시작의 판면을 그린다. 라운드 도중 #9와 새끼가 움직인 순서는 action과 대조한다. 필요하면 아래 전판 도구도 쓴다.

```sh
UNSW_RULES=123 node eval/board.js exp/q2box/on/games/bot-hunter_around_unsw_B_1/game.replay 'Around UNSW' a B 2,3,4,5,6,7
```

## 3. qw 새끼의 첫 행동과 Around UNSW B r6

`qwChildren`는 실제 여왕의 `qw` 분열로 태어난 id·round다. `newborns`는 부모, 첫 길이, qw 여부, 이탈 가능한 단일 걸음, 선택 action, 전후 거리, 죽음을 기록한다. `qwChildren`의 각 id를 `newborns`와 매칭한다. 매칭이 없으면 그 사이 여왕 사망/새끼 사망/차례 누락을 확인하고 성공으로 세지 않는다.

- qw 새끼가 첫 차례에 보이는 여왕 2칸 안에 있고 비봉쇄 이탈 대안이 있으면, 선택한 이동의 afterDistance가 distance보다 커야 한다. `qbe<n>`와 실제 첫 action을 함께 확인한다.
- `qw:false`인 L2 새끼의 qbe도 따로 보고한다. 부모 정보가 없는 구현이 다른 새끼나 재시작된 L2 프로세스에 적용된 부작용이며, 회귀 키의 첫 원인 후보다.
- `pairs`의 Around UNSW B 네 키(상대 2 × 시드 1–2)에서 off의 r6 사망을 확인하고 on의 death.round가 6이 아님을 확인한다. 단지 r7로 늦어진 경우는 출구 확보·새끼 이탈 기제가 선 것인지 판면으로 구분한다.
- Around UNSW A 네 키는 `sameEvents`, `sameQueenHeads`가 모두 true인지 확인한다. 하나라도 다르면 첫 차이부터 판면·표식·깊이 d를 비교하고 “A unchanged”를 통과로 쓰지 않는다.

## 4. 다른 지도의 여왕 생존과 깨짐

`pairs[].survivalRegression`은 off에서 r500에 살던 여왕이 on에서 죽은 키다. 하나라도 있으면 회귀로 기록하고 사망 전 2라운드·사망 라운드를 벽 포함 판면으로 읽는다. 지도/편/상대/시드를 합산해 회귀를 숨기지 않는다. 초기 주머니 Autarky·PD·Slithery의 사건 차이도 별도로 대조한다. 둘 다 조기 사망한 키는 death.round/cause와 queenHeads로 더 이른 사망·아군 함정을 확인한다.

보조 사망 전조 출력(이번 명세는 로컬 A=id0/B=id1 지도이므로 아래 기존 도구의 id 가정이 맞는다):

```sh
UNSW_RULES=123 node exp/q2/queendeath.js exp/q2box/on exp/q2box/off --games > exp/q2box/queendeath.txt
```

`sets.*.*.cpu`의 우리 team 줄에서 max를 확인한다. 80M 이상이면 경보, 100M 한도/timeout/no reply는 깨짐이다. CPU 줄이 없으면 CPU 미검증으로 표시한다. historyErrors는 재실행으로 회복된 오류와 아직 clean 결과가 없는 오류를 구분한다. 실행 중 오류가 났던 사실도 결과에 남긴다.

## 5. off 동일성

```sh
UNSW_RULES=123 node exp/v16/identity.js exp/q2box/id-off exp/q2box/id-base > exp/q2box/identity.txt
```

12/12 키와 `analysis.json.identity` 전부 true가 필요하다. 온라인 Trophy·스프린트 Around UNSW·생성 gen_M_07, 양편·양 상대가 포함된다. `id-base`는 명세 실행 시의 `versions/v1.8/bot`이고 `id-off`는 plain copy다. 실행 전 이후 다른 작업이 v1.8을 수정하지 않았는지 확인한다. 수정됐으면 명세의 identity-base bot만 수정 전 복제본 `exp/q2box/bot-base`로 바꾸고 그 사실을 기록한다.

BUILD 시점에는 공식 judge clang으로 base/off/on을 컴파일했다. `compile-check.json`의 off_equals_original_v18_wasm=true이며 base와 off는 496456 bytes, SHA-256 `698253da7cb5f7886463210bdcd738719cfa86fc07757ae467640708ca306c35`로 동일했다. 이로써 off의 명령어와 자료 배치가 보존됨을 확인했다. 게임 사건 동일성과 CPU는 조정자 실행 뒤 확인한다.

`gate-fixtures.cpp`는 plan.cpp의 새 if constexpr 블록을 그대로 뽑은 `gate.inc`를 사용한 14개 합성 root 후보 검사다. 대안 없음·미지 포털/교환 대안·공짜 질주 중간 몸·두 출구 봉쇄·옛 꼬리 해제/진주 성장·여왕/시야 예외·첫 차례 새끼 이탈을 확인한다. DFS나 게임은 실행하지 않는다. 결과는 `gate-fixtures.txt`다.

## 6. 인계 결과 작성

발동 상황 → 실제 출구/첫 이동 판면 → r6 및 A 동일성 → 다른 지도 키별 생존 → off 동일성/CPU/오류 순서로 `exp/q2box/RESULT.md`에 쓴다. 이 BUILD의 범위 밖인 제출·네트워크·커밋은 하지 않는다. 분석 결과와 남은 예외를 조정자에게 넘긴다.
