# v1.5: v1.3 + 개막 모듈(OPENING_ON)

- **날짜:** 2026-10-01
- **상태:** 사전 등록(1–4절)은 09:45 KST에 적었다. 이 시각까지 v1.5 빌드로 둔 판은 0판이다(구문 검사만 했다).
- **조정자 지시:** 사용자가 다음 후보로 승인했다. v1.5 = v1.3 + 개막 모듈이다.
  - v1.3: `HARVEST_ON`·`PT2_POCKET_ON` 켬, KR·HV2 끔
  - 동일성:
    - 개막 끔 = v1.3과 사건이 같다.
    - 개막 켬 = 개막 없는 지도에서 v1.3과 같다.
  - CPU, 연기 시험, 로컬 세트 전 사전 등록
- **고정 사본:** `versions/v1.5/bot`
  - `versions/v1.3/bot`(9ec834d)에 `exp/v14/opening-v1.2.diff`(v1.2 → v1.4 모듈, `opdb.hpp`·`opmod.cpp` + 걸이)를 `patch -p2`로 얹었다.
  - 어긋난 덩어리 둘은 손으로 붙였다(`params.hpp` v1.4 절, `plan.hpp` 멤버). 둘 다 파일 끝에 덧붙는 것이다.
  - v1.3과의 차이 전체: `exp/v15/v1.5-vs-v1.3.diff`
- **스위치:**
  - v1.3의 것: `HARVEST_ON` 켬, `PT2_POCKET_ON` 켬, `HV2_ON` 끔, `KR_ON` 끔
  - v1.4의 것: `OPENING_ON` 켬, `OP_HOLD_ON` 끔, `OP_HOLD_ALL` 끔. 지키기는 v1.4 7절의 측정 뒤 조정자가 정한다.

## 1. 가설 (사전 등록, 09:45 KST)
- **한 줄:** HV 포켓 수확(Trauma, Slithery a/b)과 개막(Devil a/b, Trophy, Schooltime a/b, Slithery a/b, Default)은 서로 다른 국면과 자리를 고친다. 그래서 둘을 합친 v1.5는 각 지도에서 그 지도의 단독 버전처럼 움직인다.
  - 개막만 있는 지도에서는 v1.4와 같다.
  - HV·Portals 지도에서는 v1.3과 같다.
  - 둘이 겹치는 Slithery에서만 새 상호작용이 있다.
- **근거:**
  - v1.3 7절: v1.3은 Trauma·Slithery(HV)와 Portals(PT2) 밖에서 v1.2와 같다.
  - v1.4 6절: 개막은 스크립트가 있는 가족 밖에서 아무것도 하지 않는다(`opUpdate`의 가족 검사).
- **Slithery 상호작용(설계로 정함):**
  - HV가 앞선다. `harvestTurn`이 차례를 가져가면(대본 진입·수확) 그 차례의 예정 분열은 없다. 예정 분열은 `OP_SPLIT_LATE`(2라운드) 안에 다시 시도하고, 그 뒤에는 버린다.
  - `harvestPlan`은 개막·지키기 걸이 뒤에 돈다. 포켓 접근 목표가 sd·지키기 목표를 덮는다.
  - Slithery 스크립트는 경유점이 없으므로 끌림 충돌은 없다(r0–10 분열 일정뿐).
- **로컬 결과 이월:** 개막만 있는 지도에서 v1.5 = v1.4라는 것을 3절 (c)로 확인한다. 같으면 v1.4 6절의 128키 결과가 v1.5의 그 지도 결과다.
  - Devil a/b, Trophy, Schooltime a/b, Default가 그런 지도다.

## 2. 바꾼 것
| 부분 | 내용 |
|---|---|
| v1.3 전부 | HV(`harvestPlan`/`harvestTurn`, `World::ensurePockets`), Portals v2 W1(`PT2_POCKET_ON`), KR·HV2 코드(끔) |
| v1.4 개막 모듈 | `opdb.hpp`, `opmod.cpp`, `params.hpp` v1.4 절(`OPENING_ON`, `OP_*`, `OP_HOLD_*`), `plan.hpp` 멤버, `plan.cpp` 걸이 |
| `plan.cpp` 걸이 | `opUpdate()`(updateSide 뒤), 잎 끌림(dfs<2>), 고르기 진전 값(`OP_STEP`), 분열 사슬(예정 분열이 먼저, 끄는 동안 sx/sr 쉼), 표식 |
| 지키기 걸이(꺼짐) | `computeDisperseGoal` 뒤 `opMidHold`, 파멸 판정 뒤 `opMidDoom`, 표식 |
| 걸이 순서 | computeDisperseGoal → opMidHold(꺼짐) → computeKingFloor → harvestPlan(v1.3) |

## 3. 로컬 점검 (사전 등록, 거르지 않음)
- **(a) 개막 끔 = v1.3:** `exp/v15/bot-opoff` 대 `versions/v1.3/bot`
  - Autarky, PD, Portals, Devil, Schooltime, Slithery, Trauma(a판) × 시드 1·2
  - `tools/fingerprint.js --same`(우리 A, proxy4_king). 모두 같아야 한다.
- **(b) 개막 켬 = v1.3, 개막 없는 지도:** `versions/v1.5/bot` 대 `versions/v1.3/bot`
  - Autarky, PD, Portals, Trauma, QoS a × 시드 1·2(`fingerprint.js`)
  - QoS b, PD10 × 두 쪽 × 시드 1·2(`exp/v15/fp.js`)
  - 모두 같아야 한다.
- **(c) 개막만 있는 지도 = v1.4(이월 조건):** `versions/v1.5/bot` 대 `versions/v1.4/bot`
  - Devil, Trophy, Schooltime, Default(a판) × 시드 1·2(`fingerprint.js`)
  - Devil b, Schooltime b × 두 쪽 × 시드 1·2(`exp/v15/fp.js`)
  - 같으면 v1.4 6절 결과를 그 지도에 쓴다. 다르면 그 지도도 (d)처럼 돈다.
- **(d) 로컬 세트(겹치는 지도):** Slithery a/b × 두 쪽 × proxy4_king·proxy4_swarm × 시드 1–4 = 32키
  - v1.5 대 v1.3(같은 키)
  - 지표:
    - 개막: r0–10 분열, 첫 가운데, r10·r25·r50 가운데 몫, r25 머리
    - 사슬: r50·r100 머리, 섭취 r0–49·r0–99, r0–99 박힘·박음·갇힘
    - 결과: 승, 끝 최장(짝), 샘 포켓 순질량/판(`exp/v13/pocketnet.js`가 읽을 수 있으면), HV 표식(` hv`)·개막 표식(` op`)
  - 이어 돌리기: `exp/v14/runq14.js`(깨끗한 줄만 끝난 키)
- **(e) CPU:** 한 턴 최대 < 80M(Default a, Schooltime a, Slithery a·b, Trauma, Devil a), proxy4_swarm
- **(f) 올리기 연기 시험:** `exp/v1/smoke_upload.js versions/v1.5/bot` 2/2, 파일 21개(v1.3의 19개 + `opdb.hpp`, `opmod.cpp`)
- 흉내 상대 결과로 거르지 않는다. 로컬 결과를 본 뒤 1–4절을 바꾸지 않는다. 구현 결함을 고치면 5절에 적는다.

## 4. 온라인 판정 기준 (사전 등록; 올릴 수 있게 되면, 3웨이브 합산, 상위 6팀)
- **v1.3의 기준(v1.3 6절):**
  - 떼 500형 끝 최장 ≥ v1.2 합산
  - Trauma·Slithery 샘 포켓 순질량/판 > 0
  - Portals 중앙 ≥ v1.2 온라인 중앙
  - 요새 퇴보 없음
- **v1.4의 기준(v1.4 4절):**
  - Devil r25 가운데 몫 ≥ 30%
  - 전멸형 지도 전멸 < v1.2(v1.3) 합산
  - 요새·떼 500형 퇴보 없음
- **Slithery(겹치는 지도):** 끝 최장 중앙 ≥ v1.3 합산 − 3, 그리고 샘 포켓 순질량/판 > 0
- v1.3도 v1.4도 아직 온라인 결과가 없다(제출 동결, 조정자 공지). 기준점은 v1.2 온라인 3웨이브와 그때 가능한 v1.3 결과다.

## 5. 확인 결과 (09:50–11:50 KST; 흉내 상대, 거르지 않음; 1–4절은 바꾸지 않았다)
### 5.1 (a)–(c) 동일성 (`exp/v15/id-*.txt`)
| 점검 | 비교 | 결과 |
|---|---|---|
| (a) 개막 끔 = v1.3 | `exp/v15/bot-opoff` 대 v1.3: Autarky, PD, Portals, Devil, Schooltime, Slithery, Trauma × 시드 1·2 | **14/14 같다** |
| (b) 개막 켬 = v1.3, 스크립트 없는 지도 | v1.5 대 v1.3: Autarky, PD, Portals, Trauma, QoS a × 시드 1·2(10), QoS b·PD10 × 두 쪽 × 시드 1·2(8) | **18/18 같다** |
| (c) 개막만 있는 지도 = v1.4 | v1.5 대 v1.4: Devil, Trophy, Schooltime, Default × 시드 1·2(8), Devil b·Schooltime b × 두 쪽 × 시드 1·2(8) | **16/16 같다** |

- (c)에 따라 Devil a/b, Trophy, Schooltime a/b, Default에서 v1.5의 로컬 결과는 v1.4 6절(128키 중 112키)의 결과다.
- 지키기(`OP_HOLD_*`)는 v1.5에서도 끔이다. 7절 결과는 v1.4 VERSION.md 7.5에 있다.

### 5.2 (e) CPU, (f) 연기 시험
- **CPU**(우리 A 대 proxy4_swarm, 시드 1, 한 턴 최대 / p99):
  - Slithery a 31.7M / 23.3M
  - Default a 31.6M / 27.8M
  - Slithery b 30.5M / 25.5M
  - Schooltime a 29.4M / 24.4M
  - Trauma 23.6M / 21.3M
  - Devil a 20.0M / 16.5M
  - 한도 100M, 경보 80M이다. 오류·시간 초과 0(64 + 6판).
- **연기 시험:** `exp/v15/smoke-upload-v15.txt` **2/2 깨끗하다.** 올라갈 파일은 21개다(v1.3의 19개 + `opdb.hpp`, `opmod.cpp`).

### 5.3 (d) 겹치는 지도 Slithery a/b (32키: 두 판본 × 두 쪽 × proxy4_king·proxy4_swarm × 시드 1–4)
- **세트:** `exp/v15/v15-sfa`·`v15-sfb` 대 `exp/v15/v13-sfa`·`v13-sfb`
  - 같은 키의 v1.4·v1.2는 v1.4 6절의 세트다.
  - 64판 깨끗하다.
  - 표: `exp/v15/report-local.txt`, `exp/v15/pocketnet-local.txt`

| 칸 (a / b) | v1.5 | v1.3 | v1.4 | v1.2 | 상위 승자 |
|---|---|---|---|---|---|
| r0–10 분열/판 | **19.6 / 21.8** | 11.1 / 11.0 | 18.1 / 19.9 | 8.9 / 8.9 | 23.8 / 23.7 |
| r25 머리 | 25.8 / 26.4 | 21.8 / 23.4 | 23.1 / 21.3 | 19.5 / 17.8 | 31.1 / 30.1 |
| r50 머리 | 35.6 / 33.4 | 34.9 / 35.0 | 29.7 / 25.8 | 28.9 / 26.3 | 47.1 / 43.5 |
| r100 머리 | 45.1 / 31.7 | 43.9 / 35.9 | 40.7 / 26.2 | 39.2 / 27.8 | 59.3 / 53.8 |
| 섭취 r0–99 | 180.2 / 140.7 | 167.6 / 139.1 | 101.6 / 49.6 | 87.2 / 47.7 | – |
| 승 | **4 / 3** | 2 / 1 | 2 / 0 | 3 / 0 | – |
| 끝 최장 평균 / 중앙 | 29.9 / 29.5, 21.7 / 22.0 | 30.1 / 33.5, 23.6 / 24.5 | 26.3 / 24.5, 18.6 / 19.0 | 26.3 / 26.5, 18.5 / 17.5 | – |
| 샘 포켓 순질량/판 | 28.4 / 19.7 | 29.9 / 26.5 | – | – | – |
| 수확 분열/판 | 89.3 / 62.8 | 85.0 / 69.0 | – | – | – |

- **짝 끝 최장(v1.5 − v1.3):** 높음 14 / 낮음 16 / 같음 2, 중앙 −0.5(부호 p = 0.86). a는 6 / 8 / 2, b는 8 / 8이다.
- **상호작용:** HV는 개막과 함께 돈다.
  - 수확 분열 76 대 77/판
  - 포켓 순질량은 둘 다 양수다(24.0 대 28.2/판).
  - 개막의 Slithery 분열 일정(23 새끼의 연속 2 떼기)도 HV와 함께 돈다(예정 분열 판당 8.1–9.2).
- **읽기:**
  - v1.5는 Slithery에서 초기 머리(r25 +4)와 승(7 대 3)이 v1.3보다 많다. 끝 최장은 같다.
  - 다른 지도는 동일성에 따라 v1.4(개막 지도) 또는 v1.3(나머지)과 같다.
  - 온라인 판정은 4절 기준대로다(제출이 다시 열리면).

## 6. 멈춤 (조정자 결정, 2026-10-01 11:2x–11:5x)
- **결정:** v1.4는 연구 빌드로 남는다. v1.5 합치기와 개막 계통(v1.5 포함)은 멈춘다. 다음 qualifier 후보는 v1.3이다.
  - qualifier는 처음 보는 지도에서 열린다. 개막 모듈은 지도 표가 있어야 켜진다.
- **5.3의 Slithery 세트:** 멈춤 지시가 닿기 전에 64판을 다 두었다(11:12–11:49). 결과는 5.3에 그대로 둔다.
  - 조정자의 앞 메시지("v1.4b 팔을 재기 전에는 v1.5 로컬 세트를 돌리지 말 것")와 엇갈렸다. 이 세트는 1–4절의 사전 등록대로 돌린 것이다.
- **구성 결정은 하지 않았다:** 개막을 어느 팔로 넣을지, 반박음을 따로 넣을지 등이다. 그 결정에 필요한 v1.4b(지키기 + 교환·보강) 팔은 두지 않았다.
- **빌드:** `versions/v1.5/bot`은 준비된 산출물로 남는다(동일성·CPU·연기 시험 통과).
