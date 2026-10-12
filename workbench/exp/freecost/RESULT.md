# Freecost ANALYSIS — 2026-10-02 06:08:24 KST

| 사전 기준 | 값(off → on) | N | 판정 |
|---|---|---|---|
| 1. L≥5 무료 다중 이동 수·차례당 비율 증가 | 1,630/119,526(1.364%) → 9,701/111,464(8.703%); 완주 1,613 → 9,681 | 68짝, 각 68판; 시드1 | PASS |
| 2a. 완전한 입력의 지급·길이·꼬리 predictor | oracleDrift 0; 합성 on 2,833/off 1,386 통과 | 기보 완주 MOVE 853,339(160판); 합성 4,219 | PASS |
| 2b. 실제 자기 몸 기억 drift=0 | knownBodyDrift 6,845, uncertainBodyDrift 204; 알려진 불일치의 free/paid/길이 차이 0, 몸 해시 차이 6,845 | predicted 350,600; unknownSlots=0 태그 347,615; 38/68키에서 known drift | FAIL |
| 2c. 재구성·관측 불확실성·태그 | sim/eatTC/splits/drops/ledger/final/lineage/natBal/dropBal/unknownDeath 모두 0; unknownBodies 2,985, blindUnverified 845, missingTags 0 | 160판; on 완주 MOVE 351,445 | PASS(불확실성은 성공에서 제외) |
| 3a. Hit Self 합계·키별 비증가 | 1,317 → 1,343(+26); 증가 23키 | 68짝 | FAIL |
| 3b. Hit Wall 합계·키별 비증가 | 3,490 → 3,289(−201); 증가 17키 | 68짝 | FAIL(합계 PASS, 키별 FAIL) |
| 3c. 여왕 사망·더 이른 사망 비증가 | 57 → 57; 새 사망 4키, 더 이른 사망 12키(새 사망 포함) | 68짝; 양쪽 사망 중 앞당김 8키 | FAIL(합계 PASS, 키별 FAIL) |
| 3d. oversprint·invalidAction·오류 0 | 각각 0 | 160판 | PASS |
| 4a. off 공식 WASM·사건/메시지 동일성 | 496,456 bytes/SHA-256 동일; 두 분석 모두 12/12 same | WASM 2개; 온라인·스프린트·생성 × 양편 × 양 상대 12키 | PASS |
| 4b. CPU <80M 경보/<100M 한도 | 최대 off 32.1M → on 32.4M; CPU 누락 0 | 160판 | PASS |
| 4c. 오류·실행 누락·실패 이력 없음 | missing/historyErrors 0, expectedGames 160, pairs 68, identity 12 | 160판 | PASS |

## 무료 이동 분모

시드1, 각 지도 4짝(A/B × king/hunter). 숫자는 무료 다중 이동/시작 L≥5 차례다. 키별 전체 분모·비율·차이는 `analysis.json.pairs`와 `summary.json.pairs`에 있으며, 평균 대신 전체 수를 합산했다.

| 지도 | off | on | N(짝) |
|---|---:|---:|---:|
| arena | 11/90 | 95/523 | 4 |
| big_empty | 604/47295 | 3937/44028 | 4 |
| Colosseum | 46/1317 | 257/1018 | 4 |
| default_small | 46/1466 | 150/1557 | 4 |
| stronghold | 19/4582 | 413/5085 | 4 |
| trophy | 62/3139 | 382/4127 | 4 |
| portals | 16/6705 | 385/6979 | 4 |
| slithery_fight | 150/10370 | 722/11268 | 4 |
| around_unsw | 76/11775 | 413/5769 | 4 |
| australia | 54/7110 | 479/7952 | 4 |
| stripes | 3/752 | 22/481 | 4 |
| gen_S_03 | 0/33 | 0/33 | 4 |
| gen_M_03 | 415/11532 | 1303/10312 | 4 |
| gen_M_07 | 4/1894 | 142/2160 | 4 |
| gen_L_02 | 0/0 | 0/0 | 4 |
| gen_R_01 | 0/0 | 0/0 | 4 |
| gen_X_07 | 124/11466 | 1001/10172 | 4 |

| 편/상대/시작 길이 | off 무료 이동/차례 | on 무료 이동/차례 |
|---|---:|---:|
| A | 792/55227 | 4799/55614 |
| B | 838/64299 | 4902/55850 |
| proxy4_king | 529/37358 | 2716/34671 |
| bot-hunter | 1101/82168 | 6985/76793 |
| L2-4 | 0/254445 | 0/252790 |
| L5-8 | 601/49891 | 2957/45996 |
| L9-12 | 408/24058 | 1814/21545 |
| L13+ | 621/45577 | 4930/43923 |

68키 중 수 증가 48, 동일 19, 감소 1; 차례당 비율 증가 48키. 양쪽 L≥5 차례가 없는 14키는 비율 미확인이다. gen_L_02/gen_R_01은 L≥5 N=0, gen_S_03은 발동 0/33으로 지도별 기제 미확인이다. 완주하지 못한 무료 시도는 off 17/on 20으로, 증가가 사망 시도에만 생긴 것은 아니다.

- **선택 변화:** arena B/proxy4_king/시드1의 첫 차이 r15 #1은 같은 시작 몸 L5에서 off `N`, on `NE`다. on은 (7,8)→(7,7)→(8,7)의 진주를 먹고 L6으로 끝나며 free=2/paid=0, 비용 개선 +1.6이다. 아래 r16 판면 2개에서 머리 이동과 남은 몸을 확인했다. 기존 후보 관문은 유지된다.
- **3걸음 탈출:** big_empty A/proxy4_king/시드1 r91 #12는 L9에서 `NWW esc`, free=3/paid=0, 진주 없이 L9 유지(+3.2)다. 시작 (20,55)→(20,54)→(19,54)→(18,54), 꼬리 3칸만 정상 전진했다. off의 같은 id는 이미 다른 위치/L5여서 이 비교를 같은 상태의 가격 인과 증거로 쓰지 않는다. r91/92 양쪽 판면은 `exp/freecost/boards/`, 전체 몸은 `selected-states.json`에 있다.
- **비가격 사례:** Trophy B/hunter r12 #1은 양쪽 모두 같은 L3 몸·한 걸음인데 off `S`, on `W`로 달랐다. 무료 비용 개선 사례에서 제외했다. Q2b의 진주 경계 변경과 음파 길이 보고 변경을 이 기보만으로 분리할 수 없어, Q2b만의 기보 인과 효과는 미확인이다. 지급 경계와 threat 소거 방지는 실제 C++ 합성 검사에서 확인했다.
- **몸 전수 확인:** 불일치 7,049건의 시작/완료 몸·fc·실제 진주·포털/벽 경로는 `audit.json`에 있다. 알려진 6,845건은 길이·지급이 맞고 몸 순서/타일 해시가 다르다. 이 중 시작 몸 전체와 이동 경로가 관측창 안인 사례도 16건(Portals)이다. 예: proxy4_king/Portals B r169 #174, L6→7에서 예상 해시 3193563132 ≠ 실제 2175577662. unknownSlots=0이 기억의 모든 타일이 관측으로 확정됐다는 뜻은 아니며, big_empty r350의 갓 태어난 L17 #201처럼 창 밖 몸을 직선으로 추정한 사례도 포함한다. 이러한 표식/기억의 한계를 기준 통과로 바꾸지 않았다. 불확실 경로 204건 중 길이 차이 194건, 지급 차이 0이다. 독립 simulator 0과 완전한 입력 oracle 0으로 실제 기억의 FAIL을 덮지 않는다.
- **사망 판면 전수:** 회귀 34키의 양쪽 S/W 및 여왕 사망 7,154건을 실제 차례 순서의 직전/직후 몸·경로·판면으로 대조했다(`audit.json`, `audit-review.json`). 직후 다음 차례 판면 7,151건, 게임 끝 3건은 최종 전체 상태로 보완했다. 분류는 표식 기반이며 의도적 먹이 on/off 1,104/951, no-exit 2,557/2,501, 일반 자기 경로 0/13, 일반 벽 경로 1/0, 여왕 머리 접촉 14/13이다. 먹이/막힘 변화로 원시 S/W 합계를 면제하지 않았다. 구 유료 꼬리 예측으로는 비었다고 할 자기 칸에서 실제 충돌한 사례는 off 12건/on 0건이다(선택이 달라지므로 개별 동일 상태 개선 인과는 미확인). on Portals A/hunter r307 #175의 `EE`는 첫 E 포털 도착 (19,12) 뒤 둘째 E가 켈프라 사망했다. 공짜여도 알려진 경로 밖 벽 안전성은 미해결이다.
- **여왕 회귀:** 새 사망은 stronghold A/king r236 W, stronghold A/hunter r200 O, Portals B/hunter r172 W, Around UNSW A/hunter r449 W다. 양쪽 사망에서 앞당김은 arena B/king 30→26 H, default_small B/king 136→105 H, Colosseum B/hunter 60→32 H, Portals B/king 178→164 W, Trophy B/hunter 88→50 H, gen_X_07 A/king 125→110(H), B/king 196→171(W), A/hunter 127→97 W다. Slithery 양편·양 상대의 r3 W 4/4, Around UNSW B의 r6 W 2/2는 그대로다. 모든 초기 여왕 id는 팀별 최저 id로 확인했다.
- **탐색 깊이:** 같은 키·라운드·id의 d 표식 117,173쌍에서 on 낮음 1,631, 같음 113,494, 높음 2,048; 평균 off 6.9732/on 6.9763이다. 달라진 관측·선택이 포함돼 예측/태그 비용의 인과 검사는 아니며, CPU 경보는 없다.

**off, arena B/proxy4_king/시드1 r16**

```text
round 16 around 7,8 (x 4..)
  5 x**.**.
  6 *xX***.
  7 *x.A**.
  8 Xx*a...
  9 *.aa.*.
 10 ..a....
  0 .......
a=#1 L5
```

**on, arena B/proxy4_king/시드1 r16**

```text
round 16 around 7,8 (x 4..)
  5 x**.**.
  6 *xX***.
  7 *x.aA*.
  8 Xx*a...
  9 *.aa.*.
 10 ..a....
  0 .......
a=#1 L6
```

## 키별 회귀(34키)

Δ는 on−off이며, 왕 앞당김은 on 새 사망도 포함한다. 모든 기준은 합계와 키별로 따로 판정했다.

| 키(모두 seed1) | ΔSelf | ΔWall | Δ여왕 사망 | 여왕 off→on 라운드 |
|---|---:|---:|---:|---|
| proxy4_king:arena:B:1 | +0 | +0 | +0 | r30 H → r26 H |
| proxy4_king:big_empty:B:1 | +31 | +0 | +0 | 생존 → 생존 |
| proxy4_king:default_small:A:1 | -1 | +3 | +0 | r52 S → r105 O |
| proxy4_king:default_small:B:1 | +0 | -2 | +0 | r136 H → r105 H |
| proxy4_king:stronghold:A:1 | +3 | -1 | +1 | 생존 → r236 W |
| bot-hunter:arena:B:1 | +1 | +16 | +0 | r40 H → r118 H |
| bot-hunter:big_empty:A:1 | +10 | +0 | -1 | r256 H → 생존 |
| bot-hunter:big_empty:B:1 | +19 | +0 | +0 | r142 H → r252 H |
| bot-hunter:Colosseum:A:1 | +5 | -9 | +0 | r35 H → r37 H |
| bot-hunter:Colosseum:B:1 | +7 | -2 | +0 | r60 H → r32 H |
| bot-hunter:default_small:A:1 | +5 | -3 | +0 | r35 H → r35 H |
| bot-hunter:stronghold:A:1 | -7 | -9 | +1 | 생존 → r200 O |
| proxy4_king:portals:A:1 | +4 | +52 | +0 | r119 W → r214 H |
| proxy4_king:portals:B:1 | -7 | -2 | +0 | r178 W → r164 W |
| proxy4_king:slithery_fight:A:1 | +5 | -2 | +0 | r3 W → r3 W |
| proxy4_king:slithery_fight:B:1 | -3 | +23 | +0 | r3 W → r3 W |
| bot-hunter:trophy:A:1 | +10 | +3 | +0 | r287 H → r370 H |
| bot-hunter:trophy:B:1 | +1 | +0 | +0 | r88 H → r50 H |
| bot-hunter:portals:A:1 | +15 | +21 | +0 | r177 O → r180 H |
| bot-hunter:portals:B:1 | -8 | +28 | +1 | 생존 → r172 W |
| bot-hunter:slithery_fight:A:1 | +1 | +7 | +0 | r3 W → r3 W |
| bot-hunter:slithery_fight:B:1 | +3 | +14 | +0 | r3 W → r3 W |
| proxy4_king:around_unsw:B:1 | +8 | +13 | +0 | r6 W → r6 W |
| proxy4_king:australia:A:1 | +1 | -7 | -1 | r214 H → 생존 |
| bot-hunter:around_unsw:A:1 | -3 | -60 | +1 | 생존 → r449 W |
| bot-hunter:australia:A:1 | +16 | +33 | +0 | 생존 → 생존 |
| bot-hunter:australia:B:1 | +5 | +8 | -1 | r256 O → 생존 |
| bot-hunter:stripes:A:1 | +0 | +14 | +0 | r120 H → r122 W |
| proxy4_king:gen_X_07:A:1 | +4 | +76 | +0 | r125 W → r110 H |
| proxy4_king:gen_X_07:B:1 | +5 | -124 | +0 | r196 S → r171 W |
| bot-hunter:gen_M_03:A:1 | +0 | +8 | +0 | r122 H → r135 H |
| bot-hunter:gen_M_03:B:1 | +6 | +11 | +0 | r124 S → r127 H |
| bot-hunter:gen_M_07:A:1 | +4 | +32 | +0 | r32 W → r32 W |
| bot-hunter:gen_X_07:A:1 | -5 | -79 | +0 | r127 W → r97 W |

**제안: switch OFF.** 무료 다중 이동 목적은 의도한 방향으로 움직였지만 실제 몸 기억 drift와 키별 안전성 회귀가 남아 “목적 개선 + 깨짐 없음”의 부분 적용 규칙을 충족하지 않는다. 봇·params·스위치는 수정하지 않았다.

원자료: `analysis.json`, `summary.json`, `audit.json`, `audit-review.json`, `actions.json`, `selected-states.json`; 보조 검증: `identity.txt`, `queendeath.txt`, `fixture-analysis.txt`, `compile-check.json`. 분석기와 보조 분석기만 실행했고 runq는 실행하지 않았다.
