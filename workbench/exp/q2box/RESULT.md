# Q2box ANALYSIS — 2026-10-02 05:48:24 KST

기존 180판만 `ANALYZE.md`대로 `UNSW_RULES=123`으로 분석했다. 새 게임·봇/params 수정·커밋·네트워크 0. 승패·총 길이는 판정에 사용하지 않았다.

| 사전 기준 | 값 | N | 판정 |
|---|---|---|---|
| 1a. 비봉쇄 대안이 있는 관측 seal 선택 0 | off 8 → on 0 | 78 on/off 키; on 잔여 seal 26건 전수 검토 | PASS |
| 1b. 우리 조각 seal 약 0 | off 41 → on 26; 시야 밖 0, 생성 대안 부재 26 | 각 78판 | FAIL: 약 0 목표 미달; 예외 전수 기록 |
| 2a. 이탈 대안 있는 qw 새끼 첫 행동 | on 18/18 이탈, off 21/21; qw의 qbe 0 | on qw 128마리 중 126 첫 행동 매칭, 조건 해당 18 | PASS: 조건 준수; qw 이탈의 추가 개선은 미확인 |
| 2b. Around UNSW B r6 사망 제거 | off/on 모두 r6 사망 4/4 | 상대 2 × 시드 1–2, B 4키 | FAIL |
| 2c. Around UNSW A 기반 유지 | 사건·여왕 머리 궤적 각각 4/4 동일 | A 4키 | PASS |
| 3. 다른 지도 키별 r500 여왕 생존 비회귀 | off/on 14/70; 회귀 0/70, 조기 사망 0/54 | 다른 지도 70키, 양쪽 사망 54키 | PASS |
| 4a. off 명령어·사건 동일성 | BUILD WASM 바이트 동일; 두 분석 모두 사건 12/12 동일 | WASM 2개, 온라인·스프린트·생성 × 양편 × 양 상대 12키 | PASS |
| 4b. CPU 경보 80M 미만·한도 100M | 우리 팀 최대 32.1M; CPU 누락 0 | 180판 모두 우리 팀 CPU 줄 있음 | PASS |
| 4c. 오류·재구성 깨짐 없음 | 오류·historyErrors·missing 0; sim/splits/drops/ledger/final 등 모두 0 | 180판 | PASS |

- **발동과 예외:** qbs 합계 118개 후보, qbe 합계 32개 후보. qbe는 모두 비qw L2 새끼 25마리에게 붙었고 첫 이동 사망 0/25; 이탈 조건 해당 비qw는 55/55 이탈했다. 잔여 seal 26건은 모두 직접 시야 안이다. 24건은 지급 가능한 1–4걸음 경로에 비봉쇄가 없고, 나머지 2건(Australia B r252 #132, stronghold A r191 #2)은 L4의 비거래 3걸음만 가능해 실제 후보로 생성되지 않는다(탈출 3걸음은 L≥6). 거래 경로·해당 지도의 포털 0. 전수 목록은 `exp/q2box/exceptions.md`, 몸·경로 원자료는 `exceptions.json`이다.
- **qw 누락 2/128:** islands B #163 r261, Around UNSW A #240 r189는 새끼 첫 행동 전에 여왕이 들이받혀 죽었다. 성공에서 제외했다. Around B 시드1의 #9 r4는 N만 가능해 봉쇄 금지가 발동하지 않는다. r5 qw 새끼는 여왕과 거리 3이라 ≤2 이탈 조건 밖이다. 시드2 새끼는 원래 이탈했으나 r6 사망은 그대로다. 벽 포함 r4–7은 `walls-on.txt`/`walls-off.txt`, 행동 순서는 `around-actions.json`이다.
- **안전성 대조:** 시작 주머니 3지도 사건·여왕 궤적 12/12 동일. 전체 78키 생존 회귀 0, 양쪽 사망 60키에서 더 이른 여왕 사망 0. Around A의 표식은 달라도 사건·여왕 궤적은 같다. 현재 v1.8 소스는 이후 freecost BUILD로 6파일 달라졌지만 저장 원본 `bot-base`는 baseline SHA와 전부 일치하고 실행된 id-base/off 사건도 12/12 같다. 명세나 기보는 바꾸지 않았다.
- **판면 2개:** big_empty A/hunter/시드1 r195. 직전 r194 #15는 off에서 W로 여왕 (20,6)의 마지막 출구 (21,6)를 막았고, on에서는 정지 분열해 출구가 남았다. 다음 r195의 다른 조각 #94 seal은 대안 부재 예외다. 두 판면은 `exp/v16/board.js`의 실제 1.2.3 재구성이다.

**off**

```text
round 195 around 20,6 (x 17..)
  3 .....ee
  4 aaaaf..
  5 aa.afF.
  6 aaBACc*
  7 aabb.cc
  8 ..bbddd
  9 ....d..
a=#0 L16  b=#12 L5  c=#15 L7  d=#63 L10  e=#72 L7  f=#92 L3
```

**on**

```text
round 195 around 20,6 (x 17..)
  3 .....ee
  4 aaaaf..
  5 aa.afF.
  6 aaBA.C*
  7 aabb.c.
  8 ..bbddd
  9 ....d..
a=#0 L16  b=#12 L5  c=#15 L2  d=#63 L10  e=#72 L7  f=#92 L3
```

**제안: switch ON.** 봉쇄 선택 8→0과 실제 출구 확보로 목적이 의도한 방향으로 움직였고 안전성 회귀·깨짐은 없다. 약 0 seal과 Around B r6 제거 실패는 결함으로 남긴다. 부분 적용 규칙에 따른 제안이며 스위치는 수정하지 않았다.
