# 상위권 흉내 상대 v3 (proxy3) — 2026-09-30

- **목적:** v2 흉내(`bots/proxy_*`)로 거른 늦은 변경 base-px8은 로컬에서 px1보다 G +3.37이었지만, 온라인 상위권 상대로는 이득이 없었다(`online-analysis-px8.md`). 원인은 흉내가 두 곳에서 약했기 때문이다. (1) 중반 질량과 붕괴, (2) 후반 왕이다. v3는 이 두 곳을 고친다. 그리고 상위권끼리의 통계가 아니라 **온라인에서 상위권이 우리 봇을 상대한 기록**에 맞춘다.
- **만든 것:** `bots/proxy3_swarm`, `bots/proxy3_elim`, `bots/proxy3_king`(새 폴더). 공통 코드 `pxcore.cpp`·`pxproto.*`·`spawndb.hpp`와 스타일별 `style.hpp`다. 원본은 `bots/proxy3_swarm`이다.
- **안 바꾼 것:** v2 `bots/proxy_*`는 그대로다(md5 앞 8자 pxcore f0787e95, style 3826887a·8809467d·7860cc1a). `tools/`의 기존 도구도 그대로다. 새 도구는 `exp/proxy3-tools/`에 뒀다.
- **원격 작업:** 없다. 네트워크 0건, 대전·업로드·다운로드 0건이다. `~/Downloads/api.txt`는 읽지 않았다.
- **표기:** 숫자는 모두 스크립트 출력이다(9절). 표의 칸 "a / b / c"는 **온라인 / v3 / v2** 순서다. **[사실]**은 수치, **[해석]**은 추론이다.

## 0. 요약
1. **[사실] 목표 1 — 우리 봇 g4-r4 대 흉내(지도 11개, 132판).** 지도별 오차 평균이 v2보다 작아졌다.

   | 지표 (지도별 평균 절대 오차) | v3 | v2 |
   |---|---:|---:|
   | 우리 승률 | 7.7%p | 13.6%p |
   | 우리 전멸 비율 | 19.5%p | 18.7%p |
   | 전멸 라운드 중앙값 | 51.8 | 78.5 |
   | 상대 몸 합 r300 | 33.0 | 39.5 |
   | 상대 최장 r500 | 11.8 | 13.9 |

2. **[사실] 목표 2 — px 계열(px8·px1)의 r340 도달.** 지도별 오차 11.4%p다(v2 18.6%p). 500라운드형 지도 도달은 88%다(온라인 71%, v2 96%). Autarky 58%(온라인 14%), Schooltime 79%(57%)다.
3. **[사실] px 계열 승률.** 로컬 31%, 온라인 6%, v2 56%다. 500라운드형 지도 42%(온라인 9%, v2 62%), 전멸형 23%(4%, 50%)다.
4. **[사실] 가까워진 곳.** 전멸형 지도의 초반 경제(빠른 진주 칸), 갇혀 죽는 비율, 작은 조각 박치기(R4), 상대의 r300 질량과 r500 왕.
5. **[사실] 남은 차이.** 500라운드형 지도에서 상대 왕 r500이 작다(px8 상대 29 대 38, g4-r4 상대 35 대 44). 상대 r300 질량도 작다(75 대 116, 117 대 148). Autarky·Schooltime에서 px 계열을 중반에 무너뜨리지 못한다. g4-r4를 Slithery Fight·Trauma에서 전멸시키지 못한다(0% 대 43%·33%).
6. **[해석]** v3는 v2보다 온라인에 훨씬 가깝다. 그래도 상위권보다 약하다. 특히 500라운드형 지도의 늦은 판에서 약하다. 늦은 변경의 로컬 효과는 v3로 재도 부풀려진다(8절).

## 1. v2에서 바뀐 것
공통 코드(`pxcore.cpp`)의 변경이다. 값은 `style.hpp`에 있다(swarm / elim / king).

| # | 바꾼 것 | 내용 | 근거 |
|---|---|---|---|
| 1 | 지도 인식 | `spawndb.hpp`에 지도 11개(온라인 10 + PD10)의 해초·포털 변과 칸별 진주 생성 간격을 넣었다. 보이는 변과 "진주가 생기는 칸인가"(카운트다운 −1 여부)로 후보를 지운다. 하나가 남으면 모든 칸의 간격 범위를 안다. 기하(해초·포털)는 지금처럼 시야로 배운다. | 상위권은 빠른 칸(간격 ≤50)에서 v2보다 몇 배 먹는다(6.1절). px3는 기하까지 바꿔서 부작용이 났다(`base-px.md` 6절 4). |
| 2 | 기대 진주 | 시야 밖 생성 칸의 가치 = 마지막 카운트다운으로 본 기대값. 시도 뒤 `max(0.75×0.98^경과, min(1, 경과/평균 간격)×0.5)`, 한 번도 못 본 칸은 `min(1, 라운드/최대 간격)×0.6`. | 같은 곳. |
| 3 | R4 박치기 | 길이 ≤4. 아군 머리가 보이면: 같거나 긴 적 0.70, 짧은 적 0.35(적 머리 1개)·0.15. 혼자면: 긴 적 0.50, 같은 0.06, 짧은 0.013. 스타일 배수 1.0 / 1.2 / 0.85. 두 걸음 질주 ×0.8 / 0.9 / 0.8, 세 걸음 elim만 ×0.4. 큰 적(6+·2배)은 v2대로 0.9. | `top-decisions.md` 2(b) b1 잎. v2는 아군과 무관하게 짧은 적도 0.28–0.45로 박았다. |
| 4 | 분열 | 적 머리가 보이면 확률 ×1.6. 팀 수 32 이상이면 2+2 확률 ×0.6, 56 이상이면 ×0.35. | 상위권 길이 4 분열: 적 보임 41.0% 대 24.3%, 팀 수 32 이상 23.3%(31 이하 38–43%). |
| 5 | 생존 탐색 | 모든 길이(v2는 5 이상)가 max(6, min(L, 8))걸음 살 길을 확인한다. 막다른 곳이라도 가는 길에 진주 2개 이상을 먹고 길이 4 이상이 되면 stub 분열로 빠져나오므로 산 것으로 본다. 알려진 샘(간격 ≤2)은 도착 때 진주로 친다. | v2 흉내의 갇힘 사망이 상위권보다 많았다(6.2절). stub 인정이 없으면 샘 통로에 안 들어가 Autarky·Trauma 먹이가 무너졌다(3절 d3). |
| 6 | 진주 경쟁 | 아군 머리가 더 가까우면 ×0.15(v2와 같음). 적 머리가 더 가까우면 ×0.35(v2 0.15), 비슷하면 ×0.80(v2 0.55). | 상위권은 위험한 진주도 간다(`top-decisions.md` 2(e): 75.7%). |
| 7 | R3 희생 | r250부터 길이 ≤4 조각이, 길이 8 이상 아군 머리가 체비쇼프 3 안이고 시야에 적 머리가 없고 그 머리 뒤쪽이 아니면 죽는다. 턴당 5.2%(r<350), 16.9%(r≥350). | `top-decisions.md` 2(d) d1. |
| 8 | px8에서 가져옴 | 꼬리가 안 보이는 아군은 3라운드 안의 보고 길이로 봄. 큰 받는 쪽·왕 머리 앞에서 희생(맨해튼 1: 0.90, 체비쇼프 2: 0.55). 큰 아군(8+) 머리 맨해튼 3 안 진주는 ×0.05로 남김. 갇힌 큰 드래곤은 박치기보다 stub 먼저. 길이 8+는 모르는 포털 금지, 안 보이는 출구 벌점 2.0. | `base-px.md` 3.2. |
| 9 | 먹이 주기 | r330부터 작은 조각이 보이는 큰 아군(8+, 자기+3)의 머리 앞 2칸 쪽으로 걸음당 0.10 / 0.10 / 0.15만큼 끌린다(적 머리가 안 보일 때). | 희생 진주가 왕에게 덜 간다(6.3절). |
| 10 | 흩어진 희생 줄임 | "3칸 안 아무 긴 아군" 희생 0.04 / 0.05 / 0.02 → 0.015 / 0.02 / 0.01. "2칸 안 큰 아군" 0.45 / 0.50 / 0.40 → 0.30 / 0.33 / 0.27. | R3·앞 먹이가 자리를 대신한다. d4에서 r300+ 희생 진주를 그때 최장이 20라운드 안에 먹은 몫이 9.4%였다(상위권 19%). d6 → d7에서 최장의 r400+ 희생 먹이가 판당 2.5 → 5.2개가 됐다(`exp/proxy3-final/kingdiet-dev.md`, 26판씩). |
| 11 | 전멸형 지도 사냥 | 지도 인식으로 전멸형(Default·Devil·Trophy·Queen Of Spades·PD)이면, 팀 수 6 이상일 때 작은 조각이 보거나 들은 적 머리 쪽으로 0.25 / 0.35 / 0.20만큼 간다. 음파 한 줄에 적 머리 목격을 싣는다. | 상위권은 우리 마지막 조각을 찾아 전멸시킨다. 효과는 작았다(3절 d8). |
| 12 | 큰 드래곤 안전 | 길이 10 이상은 적 도달 벌점 ×1.5. | 왕을 지킨다. |
| 13 | 음파 태그 | SALT를 바꿨다(0x3A51 / 0xE3C1 / 0x4B3D). v2·px8과 서로 해독하지 않는다. | px8(SALT 0x4B1D)과 같은 형식이면 서로 읽을 수 있다. |

- 상위권 규칙 R1(길이 4 → 2+2)과 R2(길이 5–9 초반 분열)는 v2에 이미 있다(성장 시작 전 길이 4는 턴당 0.50 / 0.45 / 0.50로 2+2, 6 이상은 반분). v3는 여기에 4번(적 보임·팀 크기)을 더했다. R3은 7번, R4는 3번이다.
- 스타일 차이는 v2와 같다(elim: 늦은 성장 300, 사냥, 음파 적 목격, 행동 없음으로 죽음; king: 340 → 왕 모으기, 왕 옆·몸 희생). 변경 목록 전체는 v2 `style.hpp`와 v3 `style.hpp`의 차이다.

## 2. 측정 방법
### 2.1 온라인 정답
| 묶음 | 경로 | 판 | 우리 봇 |
|---|---|---:|---|
| g4-r4 기준 | `data/online/baseline-r1`, `-r1b`, `-r1c` | 210 | 제출 10365 |
| px8 | `data/online/base-px8-online` | 70 | 제출 12096 |
| px1 | `data/online/px-king-v2-online` | 70 | 제출 11939 (= proxy_king v2) |

- `node tools/proxy_check.js online`으로 경기마다 두 편의 요약을 만들었다(`exp/proxy3-online/<묶음>/sides.jsonl`). 상대는 모두 고정 시험 팀 7개다.
- Prisoners Dilemma는 시작 드래곤 수로 PD6(팀당 3)·PD10(팀당 5)을 나눴다. 기준 210판에 PD6 14판, PD10 7판이 있다.

### 2.2 로컬
- **우리 봇:** g4-r4 = `exp/base-px1/opponents/r1`. git 첫 커밋(ef3ed35)의 `bot/`과 파일 md5가 같다. px8 = `exp/base-px8/bot`, px1 = `exp/base-px1/bot`.
- **지도:** 온라인 10개 + `maps/variants/prisoners_dilemma_10.map` = 11개(`exp/proxy3-maps/all11`).
- **판:** 흉내 3종 × 지도 11 × 양쪽 × 시드 1·2 = 132판(우리 봇마다).
- **실행:** `exp/proxy3-tools/run.js`. 공식 판정(`tools/unswbc --sandbox`). 동시 2판이고, 기계 전체 판정 프로세스가 6개 미만일 때만 새 판을 시작한다. 디스크 여유 20GB 미만이면 멈춘다.
- **v2 참고:** g4-r4는 `exp/r1-vs-proxies-v2`(10지도, 120판) + `exp/proxy3-v2ref-r1pd10`(PD10, 12판). px8·px1은 기존 평가(`exp/base-px8`, `-s3`, `-pd10`, `exp/base-px1`, `-s3`)의 흉내 판을 모아 쟀다(`exp/proxy3-v2ref-px8` 198판, `-px1` 180판, 시드 1–3).
- **결정론:** 최종판 시드 1의 132판(px8·g4-r4)은 개발 회차 d8과 모두 같은 경기였다(행 비교 66/66, 66/66).
- **주의:** `exp/proxy3-v2ref-px8`의 PD10 18판은 `exp/base-px8-pd10`의 경기를 가리키는 링크다. 그 폴더는 측정 뒤에 통째로 지워졌다(이 작업 밖의 정리). 행(`rows.jsonl`)과 측정값(`sides.jsonl`)은 `exp/proxy3-v2ref-px8`에 남아 있다. 이 묶음을 다시 `measure`하면 PD10 18판이 빠진다.

### 2.3 지표 (`exp/proxy3-tools/calib.js`)
| 지표 | 정의 |
|---|---|
| 승 | 우리 승 비율(무승부 0.5) |
| 우리 전멸 | 끝났을 때 우리 드래곤 0 |
| 전멸 라운드 중앙 | 우리가 전멸한 판의 끝 라운드 중앙값 |
| r340 도달 | r340에 우리 수 4 이상으로 살아 있음(`online-analysis-px8.md`와 같음) |
| 상대 몸 합 r300 | r300에 진행 중인 판의 상대 몸길이 합 중앙값 |
| 상대 왕 r500 | r500까지 간 판의 상대 최장 중앙값 |
| G | 우리 최장(전멸이면 0)의 평균 |

### 2.4 잡음
- 지도 하나에 로컬 12판(px 계열 합 24판), 온라인 7–21판이다. 비율 하나의 95% 구간 반폭은 12판에서 최대 ±28%p, 7판에서 ±37%p다. 지도별 차이는 대략의 방향으로만 읽는다.
- 묶음(500라운드형 60판, 전멸형 72판)이 더 믿을 만하다.

## 3. 보정 기록
개발 회차는 시드 1, 지도 11개, 양쪽이다(흉내 3종이면 66판). 판마다 `exp/proxy3-versions/<회차>/`에 얼린 사본을 두고 그 사본으로 돌렸다. 출처는 `exp/proxy3-final/dev-px8.md`, `dev-r1.md`(`exp/proxy3-tools/devsummary.js`).

| 회차 | 바꾼 것 (앞 회차 대비) |
|---|---|
| d1 | 1–3, 4의 앞부분(적 보임 ×1.6), 6, 7(머리 앞 조건 없이), 8, 12, 13 (swarm만) |
| d2 | + 5의 앞부분: 모든 길이 생존 탐색, 팀 수에 따른 분열 줄임 |
| d3 | elim·king 추가 |
| d4 | + 5의 뒷부분: 막다른 곳 stub 인정, 샘을 진주로 |
| d5 | 기대 진주 걸음 할인 0.8 → 0.9 (d6에서 되돌림) |
| d6 | + R3 머리 앞만, 9 먹이 주기 |
| d7 | + 10 흩어진 희생 줄임 |
| **d8** | + 11 전멸형 지도 사냥 — **최종판** |
| d9 | 중간 길이 방 확인 완화(길이 5–11: L+4, v2는 6 이상 2L+4), K형 왕 기준 6 (되돌림) |
| d10 | king만: 왕 모으기를 길이 5부터, 희생 시작 320 (되돌림) |

px8 상대(첫 줄이 온라인 정답):

| 회차 | 판 | px8 승: 500라운드형 / 전멸형 | px8 전멸: 500 / 전멸형 | r340 도달 Autarky / Schooltime | 상대 몸 합 r300 (500) | 상대 왕 r500 (500) | 지도 오차 승 / 전멸 / 도달 |
|---|---:|---|---|---|---:|---:|---|
| 온라인 px8 | 70 | 9% / 3% | 31% / 91% | 29% / 43% | 116 | 38 | – |
| v2 (시드 1–3) | 198 | 66% / 49% | 4% / 43% | 89% / 89% | 66 | 25 | 51.4%p / 39.8%p / 20.1%p |
| d1 swarm | 22 | 60% / 17% | 10% / 83% | 50% / 100% | 83 | 29 | 33.8%p / 20.6%p / 13.0%p |
| d2 swarm | 22 | 70% / 17% | 10% / 67% | 50% / 100% | 69 | 33 | 38.3%p / 27.1%p / 17.5%p |
| d3 | 66 | 67% / 28% | 7% / 67% | 83% / 100% | 77 | 31 | 42.9%p / 28.7%p / 14.9%p |
| d4 | 66 | 50% / 28% | 13% / 64% | 50% / 100% | 79 | 32 | 32.7%p / 24.1%p / 16.0%p |
| d5 | 66 | 67% / 44% | 13% / 56% | 33% / 83% | 71 | 27 | 49.4%p / 28.1%p / 14.5%p |
| d6 | 66 | 50% / 22% | 13% / 64% | 50% / 100% | 79 | 30 | 32.3%p / 24.1%p / 16.0%p |
| d7 | 66 | 47% / 25% | 13% / 72% | 50% / 100% | 79 | 29 | 29.7%p / 19.6%p / 16.0%p |
| **d8** | 66 | 47% / 28% | 13% / 69% | 50% / 100% | 79 | 29 | 31.2%p / 24.1%p / 14.5%p |
| d9 | 66 | 43% / 28% | 13% / 64% | 50% / 83% | 79 | 30 | 34.4%p / 27.1%p / 13.0%p |

g4-r4 상대:

| 회차 | 판 | 승: 500 / 전멸형 | 전멸: 500 / 전멸형 | 상대 몸 합 r300 (500) | 상대 왕 r500 (500) | 지도 오차 승 / 전멸 / 도달 |
|---|---:|---|---|---:|---:|---|
| 온라인 g4-r4 | 210 | 12% / 8% | 30% / 80% | 148 | 44 | – |
| v2 | 120 | 37% / 17% | 13% / 60% | 97 | 27 | 15.0%p / 17.1%p / 9.8%p |
| d2 swarm | 22 | 40% / 8% | 20% / 67% | 77 | 30 | 13.0%p / 16.2%p / 12.3%p |
| d3 | 66 | 33% / 8% | 17% / 58% | 91 | 34 | 10.0%p / 19.3%p / 9.3%p |
| **d8** | 66 | 23% / 14% | 13% / 69% | 106 | 36 | 8.4%p / 20.3%p / 9.3%p |
| d9 | 66 | 33% / 17% | 17% / 67% | 102 | 34 | 14.5%p / 16.0%p / 7.8%p |

- **[사실]** 첫 회차 d1에서 px8의 전멸형 지도 전멸이 43%(v2) → 83%가 됐다(swarm 22판). 전멸형 지도의 초반 먹이가 상위권에 가까워졌다(6.1절).
- **[사실]** 모든 길이 생존 탐색(d2)은 갇힘 사망을 줄였지만(Slithery Fight r0–99 해초·자기 몸 갇힘 117 → 43/판, swarm 2판, `exp/proxy3-final/dev-deaths-slithery.md`), 샘 통로를 피해서 먹이가 무너졌다. swarm의 판당 먹이(50라운드)는 d1 → d3에서 Autarky r50–99 55.0 → 24.5, Trauma r100–149 60.5 → 13.5다. stub 인정(d4, 세 종 합)으로 55.7, 42.0이 됐다(`exp/proxy3-final/dev-econ.md`).
- **[사실]** 기대 진주 할인을 느슨하게 하면(d5) 조각이 먼 곳을 헤매서 px8 승이 500라운드형 50% → 67%로 올랐다. 되돌렸다.
- **[사실]** d9·d10은 d8보다 낫지 않았다(g4-r4 승 오차 8.4 → 14.5%p, king만 6.1 → 13.0%p). 되돌렸다. 회차 비교는 지도당 2–6판이라 잡음이 크다.

## 4. 목표 1: g4-r4 대 흉내 (132판, 시드 1·2)
출처: `exp/proxy3-final/calib-r1.md`(흉내별 열 포함), 요약 `summary-r1.md`. 칸 = 온라인 / v3 / v2.

| 지도 | 판 | 승 | 우리 전멸 | 전멸 라운드 중앙 |
|---|---|---|---|---|
| Autarky | 21 / 12 / 12 | 62% / 83% / 100% | 0% / 0% / 0% | – / – / – |
| Portals | 21 / 12 / 12 | 0% / 0% / 0% | 0% / 0% / 0% | – / – / – |
| Schooltime | 21 / 12 / 12 | 0% / 0% / 0% | 76% / 58% / 67% | 262 / 239 / 287 |
| Slithery Fight | 21 / 12 / 12 | 0% / 8% / 17% | 43% / 0% / 0% | 389 / – / – |
| Trauma | 21 / 12 / 12 | 0% / 25% / 67% | 33% / 0% / 0% | 452 / – / – |
| Default | 21 / 12 / 12 | 0% / 0% / 0% | 95% / 50% / 58% | 207 / 238 / 247 |
| Devil | 21 / 12 / 12 | 0% / 0% / 0% | 95% / 75% / 92% | 184 / 154 / 239 |
| PD6 | 14 / 12 / 12 | 50% / 75% / 58% | 7% / 17% / 8% | 380 / 430 / 493 |
| PD10 | 7 / 12 / 12 | 0% / 0% / 0% | 57% / 75% / 92% | 132 / 278 / 317 |
| Queen Of Spades | 21 / 12 / 12 | 5% / 0% / 25% | 86% / 58% / 42% | 217 / 265 / 278 |
| Trophy | 21 / 12 / 12 | 0% / 0% / 0% | 100% / 100% / 100% | 109 / 144 / 180 |
| **500라운드형** | 105 / 60 / 60 | 12% / 23% / 37% | 30% / 12% / 13% | 340 / 239 / 287 |
| **전멸형** | 105 / 72 / 72 | 8% / 13% / 14% | 80% / 63% / 65% | 170 / 209 / 241 |
| **전체** | 210 / 132 / 132 | 10% / 17% / 24% | 55% / 39% / 42% | 199 / 212 / 248 |

| 지도 | 상대 몸 합 r300 | 상대 왕 r500 | 우리 몸 합 r300 | 우리 G |
|---|---|---|---|---|
| Autarky | 148 / 117 / 91 | 50 / 39 / 23 | 68 / 70 / 71 | 58.7 / 56.8 / 62.9 |
| Portals | 87 / 74 / 72 | 40 / 29 / 28 | 12 / 14 / 12 | 8.7 / 12.1 / 7.3 |
| Schooltime | 280 / 317 / 270 | 61 / 51 / 70 | 5 / 4 / 4 | 5.0 / 8.7 / 7.4 |
| Slithery Fight | 338 / 221 / 194 | 63 / 38 / 38 | 30 / 34 / 85 | 16.0 / 25.6 / 32.4 |
| Trauma | 138 / 97 / 99 | 33 / 21 / 16 | 27 / 29 / 27 | 9.4 / 19.0 / 17.6 |
| Default | 162 / 117 / 102 | 46 / 40 / 22 | 6 / 2 / 4 | 0.3 / 4.3 / 2.8 |
| Devil | 153 / 136 / 153 | 21 / 42 / 39 | 4 / 5 / 2 | 0.1 / 2.3 / 0.4 |
| PD6 | 58 / 43 / 38 | 28 / 20 / 22 | 34 / 34 / 35 | 24.5 / 23.7 / 20.7 |
| PD10 | 60 / 64 / 73 | 25 / 28 / 25 | 4 / 2 / 2 | 2.7 / 1.3 / 0.5 |
| Queen Of Spades | 72 / 63 / 36 | 22 / 32 / 23 | 6 / 4 / 15 | 1.1 / 4.3 / 12.0 |
| Trophy | – / – / – | – / – / – | – / – / – | 0.0 / 0.0 / 0.0 |
| **500라운드형** | 148 / 117 / 97 | 44 / 35 / 27 | 24 / 28 / 28 | 19.5 / 24.4 / 25.5 |
| **전멸형** | 69 / 64 / 47 | 25 / 28 / 23 | 8 / 5 / 10 | 3.8 / 6.0 / 6.1 |
| **전체** | 139 / 97 / 84 | 41 / 33 / 25 | 22 / 23 / 24 | 11.6 / 14.4 / 14.9 |

- **[사실]** 승은 11개 지도 중 8개가 온라인과 15%p 안이다(v2 7개). v2와 크게 갈리던 Trauma가 67% → 25%(온라인 0%), Queen Of Spades가 25% → 0%(5%)다.
- **[사실]** 우리 쪽 흐름은 거의 같다. 우리 몸 합 r300 지도 오차 1.9(v2 7.5), 우리 G 오차 3.6(v2 4.8)이다. v2는 Slithery Fight에서 우리 몸 합이 85(온라인 30)였고 v3는 34다.
- **[사실]** 상대 쪽은 아직 작다. 500라운드형 상대 몸 합 r300 117(온라인 148), 왕 r500 35(44)다. 가장 큰 차이는 Slithery Fight(221 대 338, 38 대 63)와 Trauma(97 대 138, 21 대 33)다.
- **[사실]** 전멸 비율은 v2와 비슷하게 낮다(전멸형 63% 대 80%). Slithery Fight·Trauma에서 우리를 전멸시킨 판이 없다(온라인 43%·33%). 전멸 라운드는 v2보다 온라인에 가깝다(전멸형 중앙 209, 온라인 170, v2 241).
- 흉내별(승 오차 / 전멸 오차): swarm 10.7 / 18.5%p, elim 6.2 / 15.8%p, king 6.2 / 26.3%p(`summary-r1.md`).

## 5. 목표 2: px 계열 대 흉내
### 5.1 r340 도달 (px8 132판 + px1 132판)
출처: `exp/proxy3-final/calib-pxline.md`. 온라인은 px8 70판 + px1 70판이다. v2의 PD10은 px8 쪽 18판뿐이다.

| 지도 | 판 | r340 도달 | px 승 | px 전멸 |
|---|---|---|---|---|
| Autarky | 14 / 24 / 36 | 14% / 58% / 89% | 0% / 33% / 75% | 86% / 54% / 11% |
| Portals | 14 / 24 / 36 | 100% / 100% / 100% | 29% / 33% / 53% | 0% / 0% / 0% |
| Schooltime | 14 / 24 / 36 | 57% / 79% / 89% | 0% / 46% / 61% | 43% / 13% / 11% |
| Slithery Fight | 14 / 24 / 36 | 100% / 100% / 100% | 7% / 42% / 67% | 0% / 0% / 0% |
| Trauma | 14 / 24 / 36 | 86% / 100% / 100% | 7% / 54% / 53% | 14% / 0% / 0% |
| Default | 14 / 24 / 36 | 14% / 50% / 56% | 7% / 29% / 58% | 79% / 46% / 22% |
| Devil | 14 / 24 / 36 | 7% / 8% / 28% | 14% / 21% / 69% | 86% / 75% / 14% |
| PD6 | 8 / 24 / 36 | 0% / 0% / 0% | 0% / 0% / 17% | 88% / 100% / 83% |
| PD10 | 6 / 24 / 18 | 0% / 0% / 0% | 0% / 17% / 39% | 100% / 83% / 61% |
| Queen Of Spades | 14 / 24 / 36 | 0% / 8% / 17% | 0% / 13% / 39% | 100% / 79% / 53% |
| Trophy | 14 / 24 / 36 | 0% / 0% / 6% | 0% / 58% / 72% | 100% / 42% / 22% |
| **500라운드형** | 70 / 120 / 180 | 71% / 88% / 96% | 9% / 42% / 62% | 29% / 13% / 4% |
| **전멸형** | 70 / 144 / 198 | 4% / 11% / 19% | 4% / 23% / 50% | 91% / 71% / 41% |
| **전체** | 140 / 264 / 378 | 38% / 46% / 56% | 6% / 31% / 56% | 60% / 45% / 24% |

- **[사실]** 도달 지도 오차 11.4%p(v2 18.6%p), 15%p 안 지도 8/11(v2 6/11)이다. 봇별로 온라인 자기 기록과 비교하면 px8 13.7%p(v2 20.1%p), px1 10.2%p(v2 18.9%p)다.
- **[사실]** px8과 px1의 도달은 거의 같다(Autarky 58% / 58%, Schooltime 83% / 75%). 두 봇의 차이는 늦은 판에만 있기 때문이다.
- **[사실]** 여전히 도달이 온라인보다 많은 곳: Autarky(58% 대 14%), Schooltime(79% 대 57%), Default(50% 대 14%), Trauma(100% 대 86%).

### 5.2 상대 질량과 왕 (px 계열)
| 지도 | 상대 몸 합 r300 | 상대 왕 r500 |
|---|---|---|
| Autarky | 155 / 36 / 42 | 48 / 22 / 17 |
| Portals | 88 / 75 / 67 | 36 / 30 / 32 |
| Schooltime | 193 / 179 / 95 | 43 / 37 / 35 |
| Slithery Fight | 202 / 172 / 161 | 53 / 34 / 32 |
| Trauma | 88 / 52 / 58 | 36 / 18 / 14 |
| Default | 90 / 37 / 29 | 23 / 19 / 26 |
| **500라운드형** | 130 / 75 / 66 | 39 / 30 / 27 |
| **전멸형** | 75 / 46 / 29 | 23 / 20 / 27 |

- **[사실]** Schooltime 질량은 온라인에 가까워졌다(179 대 193, v2 95). Autarky(36 대 155)와 Trauma(52 대 88)는 v2와 비슷하게 작다.
- **[사실]** 왕 r500은 500라운드형 30(온라인 39, v2 27)이다. Portals·Schooltime은 가깝고 Autarky·Slithery Fight·Trauma가 작다.
- px8만의 표(전멸 라운드 포함)는 `exp/proxy3-final/doc-px8.md`, 흉내별 열은 `calib-px8.md`에 있다. px8 승 지도 오차는 28.9%p(v2 51.4%p)이고 흉내별로 swarm 25.0, elim 40.9, king 22.1%p다(`summary-px8.md`).

## 6. 기전 지표
### 6.1 어디서 먹나 (px8 상대, r0–99, 판당)
`exp/proxy3-tools/eatsrc.js`: 먹은 진주를 칸의 생성 간격으로 나눴다(샘 ≤10, 빠름 ≤50, 중간 ≤300, 느림 >300). 출처 `exp/proxy3-final/eatsrc-px8.md`.

| 지도 | 칸 종류 | 온라인 상위권 | v3 | v2 |
|---|---|---:|---:|---:|
| Trophy | 빠름 / 중간 / 느림 | 33.6 / 24.9 / 38.3 | 11.0 / 18.6 / 21.5 | 5.7 / 12.8 / 15.1 |
| Devil | 샘 / 빠름 / 중간 | 62.2 / 16.9 / 17.1 | 48.7 / 24.2 / 17.8 | 29.7 / 11.9 / 12.3 |
| Default | 중간 / 느림 | 16.8 / 25.2 | 6.6 / 17.8 | 2.3 / 11.5 |
| Autarky | 샘 / 느림 | 51.8 / 17.1 | 37.8 / 13.6 | 32.1 / 9.1 |
| Schooltime | 빠름 / 중간 | 40.1 / 48.3 | 20.0 / 86.2 | 20.4 / 58.7 |
| Trauma | 샘 / 중간 | 29.4 / 9.4 | 18.8 / 5.3 | 20.1 / 10.3 |

- **[사실]** 지도 인식으로 빠른 칸·샘 먹이가 v2보다 늘었다(Devil 샘 29.7 → 48.7, Trophy 빠름 5.7 → 11.0). 상위권에는 아직 못 미친다(Trophy 빠름 33.6, Schooltime 빠름 40.1).
- **[사실]** 중반(r100–199) Autarky 샘은 v3 39.0, 상위권 70.4다. Trauma 샘은 16.3 대 43.4다.
- **[해석]** 상위권은 먼 곳의 빠른 칸(예: Schooltime 아래 가운데 1–20 칸 묶음)을 전략적으로 차지한다. v3는 가까운 진주를 좇는다(걸음 할인 0.8). 할인을 느슨하게 한 d5는 오히려 나빠졌다.

### 6.2 얼마나 죽나 (상대 편, 드래곤 턴 1000당)
출처 `exp/proxy3-final/eff.md`(`exp/proxy3-tools/eff.js`, `proxy_check` 편 요약의 사망 방식).

| 묶음 | 편 | 먹음 | 사망 | 갇힘(행동 없음·분열 + 해초·자기 몸) | 아군 몸 | 분열 |
|---|---:|---:|---:|---:|---:|---:|
| 상위권 대 g4-r4 | 210 | 73.4 | 20.9 | 14.5 | 1.8 | 23.4 |
| v2 대 g4-r4 | 120 | 87.1 | 28.0 | 19.2 | 3.3 | 29.8 |
| v3 대 g4-r4 | 132 | 77.3 | 23.9 | 16.2 | 3.0 | 25.6 |
| 상위권 대 px 계열 | 140 | 80.1 | 24.2 | 14.9 | 1.7 | 26.7 |
| v2 대 px8 | 198 | 95.6 | 33.7 | 20.8 | 3.1 | 34.7 |
| v3 대 px8 | 132 | 92.5 | 31.9 | 19.8 | 3.2 | 33.8 |

- **[사실]** g4-r4 상대에서 v3의 사망률(23.9)과 갇힘(16.2)은 상위권(20.9, 14.5)에 가까워졌다. px8 상대에서는 여전히 높다(31.9 대 24.2).

### 6.3 후반 왕의 먹이 (500라운드형, r500까지 간 판)
출처 `exp/proxy3-final/kingdiet.md`(`exp/proxy3-tools/kingdiet.js`).

| 묶음 | 판 | 최장이 r400–499에 먹음 | 그중 자기 희생 진주 | 몫 | r300+ 희생 | 떨군 진주 | 20라운드 안 아군 | 20라운드 안 그때 최장 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 상위권 대 g4-r4 | 73 | 22.9 | 14.9 | 64.9% | 61.0 | 120.0 | 86% | 19.1% |
| v2 대 g4-r4 | 52 | 17.3 | 5.3 | 30.4% | 63.3 | 89.5 | 88% | 8.7% |
| v3 대 g4-r4 | 53 | 17.9 | 6.6 | 37.0% | 67.2 | 104.1 | 86% | 11.5% |
| 상위권 대 px 계열 | 50 | 20.8 | 12.0 | 57.7% | 57.2 | 108.9 | 87% | 19.2% |
| v2 대 px8 | 82 | 18.9 | 3.4 | 17.8% | 41.0 | 57.7 | 88% | 10.3% |
| v3 대 px8 | 51 | 19.3 | 4.4 | 22.9% | 46.5 | 73.0 | 84% | 9.9% |

- **[사실]** g4-r4 상대에서 r300+ 희생 수(67.2 대 61.0)와 떨군 진주(104.1 대 120.0)는 상위권에 가깝다. px8 상대에서는 적다(46.5 대 57.2, 73.0 대 108.9). 떨군 진주를 그때 최장이 먹는 몫은 상위권의 절반쯤이다(10–12% 대 19%). 그래서 왕의 늦은 먹이 중 희생 몫이 23–37%(상위권 58–65%)에 머문다.
- **[사실]** 상위권 왕의 모양(g4-r4 기준 세트의 Trauma 두 판 599331, 599321; 최장을 20라운드마다 추적, `exp/proxy3-tools/kingpos.js`): forgot to mention은 r320까지 최장 5에 수 46을 유지하다가 r340 10 → r380 29 → r480 45로 자랐다. 中国必须人能飞😡는 r280 13 → r340 28 → r480 41이었다. v3 king은 px8 상대 Trauma(A, 시드 1)에서 r430까지 최장 5–7에 머물렀다(최종판과 같은 경기인 개발 회차 d7에서 추적, `kingtr.js`).
- **[해석]** 상위권은 큰 떼를 늦게까지 지키다가 왕 하나에게 짧은 시간에 몰아준다. v3는 떼가 작고(px8 상대 500라운드형 r300 수 28 대 44, `calib-px8.md`), 먹이가 여러 중간 드래곤에 흩어진다.

## 7. 흉내끼리 스타일 (상위권 목표와 비교)
- 판: swarm 거울전 시드 1–3 × 지도 11(33판) + elim·king 대 swarm 양쪽 시드 1·2(88판) = 121판(`exp/proxy3-style`). `tools/proxy_check.js report`·`summary`로 쟀다. 목표는 v2 때와 같은 상위권 스냅숏이다(swarm: 상위권 전체, elim: cheji bt, king: K팀).
- 출처: `exp/proxy3-final/summary-style.md`, `report-swarm.md`, `report-elim.md`, `report-king.md`. 값(비 = 흉내 ÷ 목표).

| 판 | 유닛 r100 | 유닛 r300 | 최장 r400 | 최장 r500 | 500라운드 승자 최장 r500 | 2+2 | 출구 희생/편 | 최장 먹이 중 희생(400+) | 박치기/편 | 질주 비율 | 갇힘 사망/편 | r0–99 먹이 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v2 swarm | 15.0 (0.88) | 21.0 (0.66) | 17.0 (0.94) | 26.0 (0.74) | 29.5 (0.69) | 68.5% (1.00) | 32.9 (1.06) | 18.5% (0.37) | 16.3 (0.79) | 43.7% (0.92) | 157 (1.22) | 76.0 (0.88) |
| v3 swarm | 13.0 (0.76) | 23.0 (0.72) | 17.5 (0.97) | 27.0 (0.77) | 30.0 (0.70) | 63.2% (0.92) | 20.1 (0.65) | 21.9% (0.43) | 20.3 (0.98) | 34.9% (0.73) | 116 (0.89) | 93.5 (1.09) |
| v2 elim | 16.0 (0.89) | 24.0 (0.57) | 12.0 (0.55) | 21.0 (0.55) | 21.5 (0.49) | 62.0% (0.93) | 22.1 (0.70) | 20.9% (0.46) | 18.3 (0.81) | 48.5% (1.15) | 131 (2.83) | 65.5 (0.94) |
| v3 elim | 12.0 (0.67) | 30.0 (0.71) | 15.0 (0.68) | 28.0 (0.74) | 36.0 (0.83) | 61.2% (0.92) | 20.0 (0.63) | 24.9% (0.55) | 23.9 (1.05) | 41.6% (0.99) | 117 (2.54) | 63.5 (0.91) |
| v2 king | 18.5 (1.09) | 21.5 (0.65) | 15.0 (0.60) | 29.0 (0.66) | 30.0 (0.65) | 65.7% (1.13) | 16.8 (0.60) | 20.6% (0.34) | 15.9 (1.13) | 46.3% (0.88) | 158 (1.41) | 78.5 (0.96) |
| v3 king | 12.5 (0.74) | 26.0 (0.79) | 17.0 (0.68) | 28.0 (0.64) | 34.0 (0.74) | 63.0% (1.08) | 13.3 (0.48) | 16.7% (0.27) | 19.5 (1.39) | 34.7% (0.66) | 113 (1.01) | 54.5 (0.66) |

- **[사실]** 가까워진 것: 갇힘 사망(swarm 1.22 → 0.89, king 1.41 → 1.01), 박치기 수(swarm 0.79 → 0.98), 유닛 r300(0.57–0.66 → 0.71–0.79), 500라운드 승자 최장(0.49–0.69 → 0.70–0.83).
- **[사실]** 멀어진 것: 출구 있는 희생(swarm 1.06 → 0.65, king 0.60 → 0.48), 유닛 r100(0.88–1.09 → 0.67–0.76), 질주 비율(swarm 0.92 → 0.73), king의 r0–99 먹이(0.96 → 0.66).
- **[사실]** elim의 갇힘 사망은 여전히 cheji의 2.54배다(v2 2.83배).
- **[사실]** swarm 거울전의 지도별 전멸 비율(11판씩): Trophy 100%(상위권 91.3%), Devil 100%(97.0%), Prisoners Dilemma 100%(85.1%), Queen Of Spades 90.9%(82.4%), Default 81.8%(62.5%), Autarky 72.7%(42.6%), Schooltime 27.3%(24.1%), Trauma 0%(8.2%), Portals·Slithery Fight 0%(0%). Autarky가 상위권보다 자주 전멸로 끝난다.
- **[해석]** 흩어진 희생을 줄인 것(1절 10)이 출구 희생 수를 낮췄다. 우리 봇 상대 지표를 우선했기 때문에 받아들였다.

## 8. 남은 차이와 쓰는 법
### 8.1 남은 차이
1. **500라운드형 지도의 늦은 판.** px 계열이 v3에게 42% 이긴다(온라인 9%). 원인은 상대 왕이 작은 것(r500 30 대 39)과, 왕이 희생 진주를 덜 먹는 것(6.3절)이다.
2. **Autarky·Trauma 중반 질량.** 상대 몸 합 r300: Autarky 36(px 계열 상대 온라인 155), Trauma 52(88). r100–199 샘 먹이가 상위권의 38–55%다(6.1절).
3. **Autarky·Schooltime 중반 붕괴.** px 계열 r340 도달 Autarky 58%(14%), Schooltime 79%(57%). Schooltime에서 상위권은 px8의 먹이를 크게 줄인다. px8이 r50–99에 먹은 진주는 온라인 37.0개, v3 상대 80.2개다(`econ.js --side us`). v3는 먹이를 뺏지 못한다.
4. **g4-r4를 전멸시키기.** Slithery Fight·Trauma 전멸 0%(온라인 43%·33%), Default 50%(95%), Queen Of Spades 58%(86%).
5. **전멸형 지도의 px 계열 승.** 23%(온라인 4%). Trophy는 58%(0%)다.
6. **스타일.** 출구 희생 0.48–0.65, 최장 먹이 중 희생 몫 0.27–0.55다. PD6에서 g4-r4가 75% 이긴다(온라인 50%).
7. **규칙 발동은 따로 재지 않았다.** R1–R4의 턴당 발동 비율을 `tools/decisions.js`로 재지 않았다. `proxy_check` 보고서의 "적 머리가 옆일 때 박는 비율(길이 ≤4)"만 봤다: swarm 43.5%(목표 36.2%), elim 49.0%(cheji 43.9%), king 38.6%(K 30.9%).

### 8.2 쓰는 법
- **권장:** 로컬 주 지표는 v3 세 종 합(132판)이다. 흉내 하나만 쓰면 swarm(목표 2 도달 오차 11.4%p)과 king(목표 1 승 오차 6.2%p)이 가깝다. elim은 500라운드형 지도에서 가장 약하다(px8에게 60% 짐).
- **v3로도 늦은 변경은 부풀려진다.** 500라운드형 지도의 도달(88% 대 71%)과 상대 왕(30 대 39)이 온라인보다 우리에게 유리하다. 늦은 변경의 로컬 효과는 `online-analysis-px8.md` 5.1절처럼 "도달 판 효과 × 온라인 도달 비율"로 옮기고, 승률 이득은 더 깎아서 본다.
- **v2와 짝:** 기존 실험은 v2와 짝지어져 있다. v3와 v2를 섞어 비교하지 않는다.
- **지도 11개:** PD10을 넣으려면 `--maps exp/proxy3-maps/all11`(eval.js도 같은 폴더를 받는다).

## 9. 판, CPU, 재현
### 9.1 판 (md5 앞 8자)
| 폴더 | pxcore.cpp | style.hpp | spawndb.hpp | pxproto.cpp / .hpp | bot.toml |
|---|---|---|---|---|---|
| `bots/proxy3_swarm` | b7833c9d | 0fba4c82 | 3dd2d1be | 89e9534f / 0575f9dd | 09a60132 |
| `bots/proxy3_elim` | b7833c9d | 140df28d | 3dd2d1be | 89e9534f / 0575f9dd | a198230a |
| `bots/proxy3_king` | b7833c9d | 2247f582 | 3dd2d1be | 89e9534f / 0575f9dd | 74614af6 |

- 개발 회차 사본은 `exp/proxy3-versions/d3`–`d10`에 있다. 최종판 = `d8`(파일 md5 같음).
- 공통 코드를 고치면 `bots/proxy3_swarm`의 `pxcore.cpp`, `pxproto.*`, `spawndb.hpp`를 다른 두 폴더에 복사한다(`tools/proxy_check.js sync`는 `proxy_` 폴더만 다루므로 쓰지 않는다).
- `spawndb.hpp`는 `node exp/proxy3-tools/genspawndb.js bots/proxy3_swarm/spawndb.hpp`로 만든다.

### 9.2 CPU (`tools/unswbc run --sandbox`, 시드 7, `exp/proxy3-final/cpu/`)
| 판 | 턴당 p50 / p99 / 최대 |
|---|---|
| Slithery Fight, swarm 대 king | 6.1M / 7.5M / 7.8M (양쪽) |
| Schooltime, swarm 대 king | 7.2M / 8.9–9.0M / 9.2–9.3M |
| Trauma, elim 대 g4-r4 | elim 4.7M / 6.1M / 6.3M (g4-r4 최대 26.3M) |

- 한도는 턴당 100M 점이다. 최종 264판(g4-r4·px8)과 px1 132판, 스타일 121판에서 시간 초과·충돌·비정상 종료가 0건이었다(`rows.jsonl`의 `botProblem`·`exit`).

### 9.3 재현 (저장소 루트)
```
# 온라인 정답 (경기 없음)
for s in baseline-r1 baseline-r1b baseline-r1c px-king-v2-online base-px8-online; do
  node tools/proxy_check.js online --dir data/online/$s --out exp/proxy3-online/$s; done
# 로컬 (동시 2판, 기계 전체 6판 미만일 때만 시작)
node exp/proxy3-tools/run.js --label proxy3-r1  --bot exp/base-px1/opponents/r1 --opps proxy3_swarm,proxy3_elim,proxy3_king --seeds 1,2
node exp/proxy3-tools/run.js --label proxy3-px8 --bot exp/base-px8/bot --opps proxy3_swarm,proxy3_elim,proxy3_king --seeds 1,2
node exp/proxy3-tools/run.js --label proxy3-px1 --bot exp/base-px1/bot --opps proxy3_swarm,proxy3_elim,proxy3_king --seeds 1,2
node exp/proxy3-tools/run.js --label proxy3-v2ref-r1pd10 --bot exp/base-px1/opponents/r1 --opps proxy_swarm,proxy_elim,proxy_king --maps exp/proxy3-maps/pd10 --seeds 1,2
node exp/proxy3-tools/run.js --label proxy3-style --pairs proxy3_swarm:proxy3_swarm --seeds 1,2,3
node exp/proxy3-tools/run.js --label proxy3-style --pairs proxy3_elim:proxy3_swarm,proxy3_king:proxy3_swarm --both-sides --seeds 1,2
for L in proxy3-r1 proxy3-px8 proxy3-px1 proxy3-v2ref-r1pd10 proxy3-style; do node tools/proxy_check.js measure --label $L; done
# v2 참고 묶음(proxy3-v2ref-px8, -px1)은 base-px8·-s3·-pd10, base-px1·-s3의 흉내 판을 rows.jsonl로 모으고 games/를 링크한 뒤 measure로 쟀다.
# 표
node exp/proxy3-tools/calib.js --g "온라인 g4-r4 (210)=online:baseline-r1+online:baseline-r1b+online:baseline-r1c" --g "proxy3 (132)=local:proxy3-r1" \
  --g "v2 (132)=local:r1-vs-proxies-v2+local:proxy3-v2ref-r1pd10" --metrics n,win,elim,elimR,reach,G,oU100,oM300,oU300,oK400,oK500,uM300
node exp/proxy3-tools/calib.js --g "온라인 px 계열 (140)=online:base-px8-online+online:px-king-v2-online" \
  --g "proxy3: px8+px1 (264)=local:proxy3-px8+local:proxy3-px1" --g "v2: px8+px1 (378)=local:proxy3-v2ref-px8+local:proxy3-v2ref-px1" --metrics n,reach,win,elim,oM300,oK500
node exp/proxy3-tools/devsummary.js --runs "온라인 px8 (70)=online:base-px8-online" --runs "proxy3 (132)=local:proxy3-px8"
node tools/proxy_check.js summary --runs proxy-v2:proxy_swarm:all,proxy3-style:proxy3_swarm:all,proxy-v2:proxy_elim:cheji,proxy3-style:proxy3_elim:cheji,proxy-v2:proxy_king:K,proxy3-style:proxy3_king:K
node tools/proxy_check.js report --label proxy3-style --bot proxy3_swarm --target all
# 기전 지표
node exp/proxy3-tools/eatsrc.js --g "top vs px=online:base-px8-online+online:px-king-v2-online" --g "proxy3 vs px8=local:proxy3-px8" --maps trophy,devil,default,autarky,schooltime,trauma
node exp/proxy3-tools/econ.js --g "top vs px=online:base-px8-online+online:px-king-v2-online" --g "proxy3 vs px8=local:proxy3-px8"
node exp/proxy3-tools/deaths.js --g "top vs px=online:base-px8-online+online:px-king-v2-online" --g "proxy3 vs px8=local:proxy3-px8" --maps schooltime
node exp/proxy3-tools/kingdiet.js "proxy3 vs px8=exp/proxy3-px8/sides.jsonl" "top vs px line=exp/proxy3-online/base-px8-online/sides.jsonl+exp/proxy3-online/px-king-v2-online/sides.jsonl"
node exp/proxy3-tools/eff.js "proxy3 vs g4-r4=exp/proxy3-r1/sides.jsonl" "proxy3 vs px8=exp/proxy3-px8/sides.jsonl"
node exp/proxy3-tools/kingpos.js data/online/baseline-r1/M599331.replay B 200
```
- 이 기계에서 132판 한 묶음이 약 6–9분 걸렸다(동시 2판).
- 결과 파일: `exp/proxy3-final/`(표·요약·CPU), `exp/proxy3-r1`, `-px8`, `-px1`, `-style`, `-v2ref-*`(경기와 `sides.jsonl`), `exp/proxy3-d*`(개발 회차).

## v4: 진주 판본 인식 (2026-09-30)
- **왜:** 서버는 Devil, Queen Of Spades, Schooltime, Slithery Fight를 진주 배치 a·b로, Prisoners Dilemma를 6마리·10마리로 반씩 낸다(`research/observations/pearl-variants.md`). 이제 로컬 평가도 시드 1은 a판(`maps/online-20260927`), 시드 2는 b판(`maps/server-b`)으로 돌린다. v3의 지도 표에는 b 배치가 없다.
  - [사실] v3에 LOG만 더한 사본(`exp/proxy4-tools/px3log.js`, `exp/proxy4-check-p3`, b 파일당 1판)에서 b 지도를 맞게 인식한 드래곤 프로세스는 0이다.
  - 대부분은 맞는 지도가 표에 없어 진주 지식 없이 움직였다(Devil b 207/213, Queen Of Spades b 125/179, Schooltime b 203/213, Slithery Fight b 1,409/1,745). 나머지는 a로 잘못 확정했다(6, 54, 10, 336).
- **만든 것:** `bots/proxy4_swarm`, `proxy4_elim`, `proxy4_king`. v3 사본에서 지도 인식(`pxcore.cpp`의 `checkSdb`)과 지도 표(`spawndb.hpp`)만 바꿨다.
  - 표는 `node exp/proxy4-tools/genspawndb.js bots/proxy4_swarm/spawndb.hpp`로 만든다. 공통 코드 원본은 `bots/proxy4_swarm`이다.
  - `style.hpp`, `pxproto.*`, 난수·음파 SALT는 v3와 같다(md5 같음). md5 앞 8자는 `pxcore.cpp` e62a8ad9, `spawndb.hpp` cd4f4ed5다.
- **안 바꾼 것:** `bots/proxy3_*`와 v2 `bots/proxy_*`는 md5가 9.1절, 머리말과 같다. 원격 작업은 0건이다.

### 인식 규칙
1. 지도 표는 15개다. v3의 11개(순서·값 같음)에 `Devil b`, `Queen Of Spades b`, `Schooltime b`, `Slithery Fight b`를 더했다. b 배치는 a 지도와 한 가족이다(크기·해초·포털이 같고 진주만 다르다).
2. a와 b는 한쪽에서만 생성하지 않는 칸(`pearlIn` −1)으로 가린다. v3가 지도를 가리는 방법과 같다.
3. 두 판본 지도에는 카운트다운 확인을 더한다. `pearlIn ≤ max`여야 한다. 라운드 < min − 1이면 첫 시도 전이므로 `pearlIn + 라운드 + 1`이 [min, max] 안이어야 한다(여유 5% + 1).
   - [사실] 로컬 리플레이로 확인했다. 0라운드에 읽은 42칸 모두 `pearlIn` = 초기 카운트다운 − 1이었다. 4판(Devil·Schooltime·Slithery Fight·Queen Of Spades)의 초기 카운트다운 1,281개와 재추첨 35,404개는 모두 [min, max] 안이었다.
4. a와 b가 둘 다 남으면 가족 상태가 된다. 두 판본이 같은 칸은 그 범위를 쓰고, 다른 칸의 기대 진주는 두 판본 값의 평균(같은 사전확률)이다. 하나가 남으면 v3처럼 확정한다.
5. 전멸형 지도 판단(1절 11번)은 a 지도 이름으로 한다. 그래서 Devil b와 Queen Of Spades b도 전멸형이다.
6. 인식이 바뀔 때 프로세스마다 LOG 한 줄을 쓴다(`px4 map Devil_b r0`, `px4 fam Schooltime n2 r39`). `tools/eval.js`는 `--no-logs`라서 이 줄이 리플레이에 남지 않는다.
7. Prisoners Dilemma 6·10은 v3 인식 그대로 둔다(따로 된 지도로 보고, 생성 여부만 본다).
   - [사실] 개발 회차 d1은 PD 6·10도 한 가족으로 묶고, 카운트다운 확인을 모든 지도에 켰다. 그러자 흉내끼리 PD 경기 14판이 21–71라운드에 끝났다. v3는 22판 중 21판이 138–206라운드였고, 상위권 중앙은 119–126이다.
   - merge2 상대 결과가 달라진 것은 120판 중 PD 12판뿐이다(`node tools/pair_ab.js --cand proxy4-d1-merge2 --base merge2 --sets px4`). PD6에서 merge2는 d1 상대로 6/6승(G 30.3), 최종판 상대로 3/6승(G 19.3)이다. d1 기록은 `exp/proxy4-d1-*`에 있다.

### 검증
- [사실] 0라운드 창(`node exp/proxy4-tools/window0.js`, 지도 파일만 봄): 네 지도는 a·b 모두 시작 드래곤 전부의 7×7 창에 한 판본에서만 생성하지 않는 칸이 있다(Devil 6, Queen Of Spades 4, Schooltime 6, Slithery Fight 14마리).
  - 머리 위치 전체로 보면 그런 칸이 없는 창이 Devil 20%, Queen Of Spades 29%, Schooltime 5%, Slithery Fight 7%다. 분열로 생긴 드래곤이 여기서 태어나면 가족 상태로 시작한다.
- [사실] 로컬 경기의 LOG(`node exp/proxy4-tools/recog.js report --label proxy4-check,proxy4-check-s2`): v4 swarm 대 king 시드 1, merge2 대 v4 elim 시드 2, 지도 파일 15개 × 2판.

| 지도 파일 | 프로세스 | 맞음 | 틀림 / 지도 없음 | 시작 드래곤 0라운드 맞음 | 인식 지연 p90 / 최대 | 가족 상태 거침 (기간 중앙 / 최대) |
|---|---:|---:|---|---|---|---|
| devil / devil_b | 239 / 253 | 239 / 252 | 0 / 0 | 9/9, 9/9 | 0 / 16, 0 / 17 | 8 (2 / 16), 8 (3 / 14) |
| queen_of_spades / _b | 242 / 223 | 238 / 217 | 0 / 0 | 6/6, 6/6 | 6 / 24, 4 / 37 | 61 (5 / 24), 57 (4 / 37) |
| schooltime / _b | 813 / 336 | 812 / 336 | 0 / 0 | 9/9, 9/9 | 0 / 10, 0 / 7 | 17 (2 / 10), 24 (3 / 7) |
| slithery_fight / _b | 3,006 / 2,561 | 2,986 / 2,541 | 0 / 0 | 21/21, 21/21 | 1 / 20, 1 / 20 | 530 (2 / 20), 446 (2 / 20) |
| prisoners_dilemma / _10 (v3 그대로) | 232 / 262 | 232 / 262 | 0 / 0 | 3/7, 6/11 | 0 / 227, 4 / 176 | – |
| 한 판본 지도 5개 | 2,588 | 2,588 | 0 / 0 | 51/51 | 0 / 0 | 0 |

- "맞음"이 프로세스 수보다 적은 것은 가족 상태에서 확정하기 전에 죽은 프로세스다. 지연은 태어난 라운드부터 센다.
- [사실] 같은 시드의 v3 대 v3 경기(swarm 대 king, 시드 1)와 사건 단위로 같다: Autarky, Default, Devil, Portals, PD6, PD10, Trauma, Trophy. Schooltime a는 88라운드에 가족 상태로 태어난 분열 드래곤(id 88)에서 처음 갈라진다.
- [사실] CPU는 턴당 최대 9.8M 점이다(Schooltime b, 한도 100M). 최종판 280판에서 시간 초과·충돌이 0건이었다.

### b에서 스타일
흉내끼리 경기(`exp/proxy4-style-ab`: swarm 거울 시드 1–3, king·elim 대 swarm 양쪽 시드 1, 지도 파일당 7판)를 상위권끼리 경기와 판본별로 비교했다. 상위권 자료는 `exp/proxy-check/top-sides.jsonl`이고, 판본은 `data/pearl_layout/variants.json`에서 붙였다. v3는 같은 설계로 b 파일에서만 돌렸다(`exp/proxy3-style-b`). 명령은 `node exp/proxy4-tools/style_ab.js --g "proxy4=proxy4-style-ab" --g "proxy3=proxy3-style-b"`이고, 값은 편 중앙값이다.

| 지도 | 지표 | 상위권 a / b | v4 a / b | v3 b |
|---|---|---|---|---|
| Schooltime | 전멸 / r0–99 먹이 | 7% / 48%, 156 / 30 | 29% / 57%, 114 / 21 | 0%, 14 |
| | 몸 합 r100 / 최장 r500 | 87 / 30, 48 / 28 | 62.5 / 23.5, 39 / 21.5 | 18, 20.5 |
| Devil | 라운드 중앙 / r0–99 먹이 | 99.5 / 118, 109 / 71 | 97 / 109, 54 / 80 | 192, 92 |
| Queen Of Spades | 라운드 중앙 / r0–99 먹이 | 265 / 225, 50 / 41.5 | 318 / 302, 47.5 / 37.5 | 433, 38.5 |
| Slithery Fight | 몸 합 r100 / 최장 r500 | 155 / 138, 43 / 52.5 | 120 / 92.5, 37 / 29 | 110, 33 |
| PD 6 / 10 | 라운드 중앙 / r0–99 먹이 | 126 / 119, 57.5 / 58.5 | 161 / 193, 40.5 / 55 | 193, 55 |

- [사실] Schooltime b에서 v4는 상위권과 같은 방향, 비슷한 크기로 바뀐다. r0–99 먹이는 둘 다 ×0.19이고, 몸 합 r100은 ×0.38 대 ×0.34, 전멸은 +28%p 대 +41%p다. v3는 b에서 전멸로 끝난 판이 없었다(상위권 48%).
- [사실] Devil b·Queen Of Spades b의 경기 길이는 v4가 상위권에 가깝다(109 대 118, 302 대 225; v3는 192, 433). v3는 b를 알아보지 못해 전멸형 사냥을 하지 않는다.
- [사실] 남은 차이: Slithery Fight b에서 상위권 최장 r500은 a보다 커지지만(43 → 52.5) v4는 작아진다(37 → 29). Devil의 r0–99 먹이는 판이 100라운드 안팎에 끝나서 흔들린다.
- [해석] b 지도에서 흉내가 먹이를 대하는 방식은 상위권과 같은 방향으로 바뀐다. 지도·판본마다 14편이라 크기는 대략으로만 읽는다.

### merge2 기준점 (`bot/`, 제출 12142)
- 표준 묶음은 `merge2-a-px4`, `merge2-b-px4`(흉내 3종 × 지도 10 × 양쪽, 각 60판)와 `merge2-a-old4`, `merge2-b-old4`(옛 상대 4종, 각 80판)다. 명령은 작업 지시 그대로다.
- 네 묶음 모두 문제 0건, 오류 0건이다. `merge2-a-old4`는 `exp/cand-merge2`의 시드 1 80판과 사건 단위로 같다.

| 묶음 (표준: a 시드 1, b 시드 2) | 흉내 G / 승 / 생존 | 옛 상대 G / 승 / 생존 |
|---|---|---|
| 전체 | 15.9 / 17% / 57% (120판) | 41.1 / 83% / 95% (160판) |
| 두 판본 지도 a | 13.4 / 13% / 67% | 48.8 / 85% / 98% |
| 두 판본 지도 b | 8.3 / 3% / 50% | 37.0 / 83% / 100% |
| 한 판본 지도 (시드 1·2) | 20.9 / 25% / 57% | 39.3 / 81% / 91% |

- [사실] 표준 방식의 a → b 차이에는 시드 차이가 섞인다. 흉내 상대 두 판본 지도의 G는 a에서 시드 1이 13.4, 시드 2가 9.9이다. b에서는 시드 1이 10.2, 시드 2가 8.3이다.
- 그래서 판본의 효과는 교차 칸을 더해 같은 시드로 짝지어 쟀다. 교차 칸은 `merge2-a5s2-px4`, `merge2-b5s1-px4`, `merge2-b5s1-old4`이고, 옛 상대 a 시드 2는 `exp/cand-merge2`에서 가져왔다(`node exp/proxy4-tools/ab_matched.js`).
- 한 짝은 상대·지도·진영·시드가 같고 TILE 줄만 다른 두 판이다. 표의 b − a 구간은 95% 짝 t 구간이다.

| 지도 (짝: 흉내 12 + 옛 16) | 흉내 G a / b (b − a) | 흉내 승 a / b | 옛 상대 G a / b (b − a) | 옛 승 a / b | 합 G b − a |
|---|---|---|---|---|---|
| Devil | 4.8 / 2.3 (−2.5 [−7.7, +2.7]) | 0 / 0% | 37.0 / 24.2 (−12.8 [−22.8, −2.8]) | 81 / 56% | −8.4 [−14.5, −2.3] |
| Queen Of Spades | 3.3 / 6.4 (+3.2 [−4.6, +11.0]) | 8 / 0% | 37.9 / 30.6 (−7.3 [−15.1, +0.6]) | 75 / 75% | −2.8 [−8.4, +2.9] |
| Schooltime | 8.6 / 3.8 (−4.8 [−11.9, +2.4]) | 0 / 0% | 73.4 / 32.8 (−40.6 [−61.8, −19.4]) | 75 / 88% | −25.3 [−39.0, −11.5] |
| Slithery Fight | 25.0 / 20.5 (−4.5 [−12.6, +3.6]) | 0 / 8% | 68.1 / 62.8 (−5.3 [−21.8, +11.1]) | 100 / 100% | −5.0 [−14.4, +4.5] |
| PD 6 / 10 | 16.4 / 13.3 (−3.2 [−13.4, +7.1]) | 42 / 8% | 29.7 / 35.3 (+5.6 [−5.8, +17.0]) | 100 / 100% | +1.9 [−5.7, +9.4] |
| **다섯 지도** | 11.6 / 9.3 (−2.4 [−5.5, +0.8]) | 10 / 3% | 49.2 / 37.1 (−12.1 [−18.8, −5.3]) | 86 / 84% | −7.9 [−12.0, −3.8] |

- [사실] b에서 merge2의 G는 다섯 지도 합으로 −7.9다. 대부분 Schooltime(−25.3)과 Devil(−8.4)에서 온다. 옛 상대 기준으로 승과 생존은 거의 그대로다(승 86 → 84%, 생존 99 → 100%).
- [사실] 흉내 상대 승은 10% → 3%다(−7%p [−15, +1]). 가장 큰 곳은 PD10으로 42% → 8%다(−33%p [−65, −2]). 생존은 57%로 같다.
- [해석] Schooltime b와 Devil b는 먹이가 적어서 모두 덜 자란다(첫 100라운드 자연 진주 −67%, −23%). 그래서 이기는 상대에게도 G가 준다. 흉내 상대로는 이 지도들을 원래 거의 이기지 못해서 G 차이가 작다. b에서 승을 가장 많이 잃는 곳은 PD10이다.

### 한 명령 선별
```
node tools/pair_ab.js --cand <이름> --base merge2 --bot <후보 폴더>              # 없는 묶음 4개(280판)를 돌리고 짝 비교
node tools/pair_ab.js --cand <이름> --base merge2 --bot <후보 폴더> --sets px4   # 흉내 상대만(120판)
node tools/pair_ab.js --base merge2                                              # 한 봇의 지도·판본별 표
```
- `--bot`을 주면 없는 묶음(`<이름>-a-px4`, `-b-px4`, `-a-old4`, `-b-old4`)만 `tools/eval.js --jobs 2`로 돌린다. 판정 프로세스가 4개 이하일 때만 평가 하나를 시작하고(합 6 이하), 평가는 한 번에 둘까지 돈다.
- 짝은 같은 키(상대·지도·진영·시드)로 a 묶음끼리, b 묶음끼리 맺는다.
- 출력은 전체(95% 짝 t 구간, G는 지도 묶음 부트스트랩도), 상대 묶음별, 두 판본 지도의 a와 b, 한 판본 지도, 지도별, 두 판본 지도는 a·b 따로다. 판별 한계는 `research/MEASUREMENT.md`를 따른다.

### 재현
```
node exp/proxy4-tools/genspawndb.js bots/proxy4_swarm/spawndb.hpp   # 그다음 pxcore.cpp·spawndb.hpp를 proxy4_elim·king에 복사
node exp/proxy4-tools/window0.js
node exp/proxy4-tools/recog.js run --label proxy4-check --pairs proxy4_swarm:proxy4_king --seeds 1
node exp/proxy4-tools/recog.js run --label proxy4-check-s2 --pairs bot:proxy4_elim --seeds 2
node exp/proxy4-tools/recog.js report --label proxy4-check,proxy4-check-s2
node exp/proxy4-tools/px3log.js <임시 폴더>   # v3 LOG 사본; recog.js run --label proxy4-check-p3 --maps maps/variants
node exp/proxy3-tools/run.js --label proxy4-style-ab --pairs proxy4_swarm:proxy4_swarm --maps exp/proxy4-maps/ab10 --seeds 1,2,3
node exp/proxy3-tools/run.js --label proxy4-style-ab --pairs proxy4_king:proxy4_swarm,proxy4_elim:proxy4_swarm --both-sides --maps exp/proxy4-maps/ab10 --seeds 1
#   proxy3-style-b: 위 두 줄을 proxy3_*와 exp/proxy4-maps/b5로
node tools/proxy_check.js measure --label proxy4-style-ab            # proxy3-style-b도
node exp/proxy4-tools/style_ab.js --g "proxy4=proxy4-style-ab" --g "proxy3=proxy3-style-b"
node tools/eval.js --bot bot --label merge2-a5s2-px4 --maps exp/proxy4-maps/a5 --seeds 2 --opps proxy4_swarm,proxy4_elim,proxy4_king --jobs 2
node tools/eval.js --bot bot --label merge2-b5s1-px4 --maps exp/proxy4-maps/b5 --seeds 1 --opps proxy4_swarm,proxy4_elim,proxy4_king --jobs 2
node tools/eval.js --bot bot --label merge2-b5s1-old4 --maps exp/proxy4-maps/b5 --seeds 1 --opps replay_rules_v8,archetype_swarm,archetype_hunter,h2 --jobs 2
node tools/pair_ab.js --base merge2
node exp/proxy4-tools/ab_matched.js --a merge2-a-px4+merge2-a5s2-px4 --b merge2-b-px4+merge2-b5s1-px4
node exp/proxy4-tools/ab_matched.js --a merge2-a-old4+cand-merge2@2 --b merge2-b-old4+merge2-b5s1-old4
```
- `exp/proxy4-maps/`의 `a5`, `b5`, `ab10`은 두 판본 지도 파일로 가는 심볼릭 링크다.
