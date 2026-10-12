# KNOWLEDGE.md: 물려받은 모든 자료의 색인 (2026-10-01 01:45)

사용자 지시(01:35)는 "최대한 기존 기보, 그리고 우리가 사용했던 가설 검증 과정에서 나왔던 자세한 데이터를 다 활용해 줘. 전부 다."이다.
- 모든 경로는 이 저장소 기준이다. `legacy/` = `../unsw-heuristic`, `data/`와 `.cache/`는 그쪽으로 가는 링크다.
- 새 연구와 설계는 이 목록부터 본다. 모집단은 누적 전체다.

## 1. 기보(원자료)
- **상위권끼리:** `data/top/<대전>/<경기>.replay.gz`, 목록은 `data/top/index.jsonl`(2026-10-01 01:40에 16,681행).
  - 레이팅 1900 이상 팀끼리의 판이다. launchd 수집기(`legacy/tools/collect_top.js`)가 5분마다 덧붙인다.
  - 멈춘 팀이 있는 판은 뺀다. 규칙: 100라운드 이상에서 핑 0, 분열 ≤3. 공급망 연구는 이렇게 259판을 뺐다.
- **우리 대 상위 7팀 웨이브:** `data/online/<세트>/`(`index.json`, `game-<id>.json`, `M<id>.replay`)
  - 웨이브 세트:

| 웨이브 | 세트 | 봇 |
|---|---|---|
| W0 | `cand-merge2-online`, `-r2`, `-r3` | merge2 |
| W1–W4 | `cand-stack1..4-online` | stack1–4 |
| W5 | `cand-stack5-online` | stack5 |
| W6 | `cand-stack6-online` | stack6 |
| W7 | `cand-stack6-online-r2` | stack6 |
| W8 | `cand-stack7-online` | stack7 |
| W9 | `cand-stack8-online` | stack8 |
| W10 | `cand-stack9-online` | stack9 |
| W11 | `cand-stack10-online` | stack10 |
| W12 | `cand-stack11-online` | stack11 |

  - 이전 계열: `baseline-r1`, `-r1b`, `-r1c`(g4-r4), `cand-avoid6-online`, `cand-portal1-online`, `cand-swarm8-online`, `base-px8-online`, `base-px9d-online`, `px-king-v2-online`
  - 쓰지 않는 것: `r1-online`, `r1-autoscrim`, `g1`, `g2`(자동 대전·중위권, 사용자 규칙)
  - 원격 작업 기록: `data/online/REMOTE-LOG.md`, `requests.jsonl`, `submissions.jsonl`
- **로컬 판(흉내 상대 v4, a·b 판본):** `legacy/exp/<이름>-px4/`(`rows.jsonl` + `games/*/game.replay`)
  - 오늘 후보들: `stack5-a-px4`, `stack7-*`, `stack8-*`, `stack9*-*`, `stack10*-*`, `stack11-*`, `stack12*-*`
  - 09-29 흉내 상대 만들기와 swarm 로컬 기보는 지웠다(요약은 남음).

## 2. 가공 자료(캐시)
- **질량 장부**(`tools/mass_ledger.js`, 정의는 머리 주석): `.cache/mass-ledger/`
  - `top-sample.jsonl`: 상위권 전체, 23:55 기준 14,998판
  - `online-<세트>.jsonl`: 우리 세트 전부, W12까지
  - 필드: `st`(r0–500 10라운드마다 수·총길이·왕·두 번째), `fl`(10라운드 칸마다 흐름: 먹은 진주 출처별, 사망 원인별, 분열·질주), `dt`(사망 집계), `ct`(맞부딪힘), `lin`(최종 왕 계보)
- **결정 행**(`tools/decisions.js`): `data/decisions/<세트>/*.tsv.gz`
  - 드래곤 차례마다 한 줄이다: 볼 수 있던 상태, 한 행동, 짧은 결과.
  - `top-all` + 우리 세트 전부. 척도·가설 순위는 `data/decisions/scale.*`, `hypotheses*.md`.
- **연구 캐시:** `.cache/intake-gap/`(numbers.json, 347MB), `.cache/endgame-king/`, `.cache/supply-chain/`, `.cache/econ-principles/`, `.cache/conv-chain/`, `.cache/elite-counterplay/`, `.cache/outcome-review/`

## 3. 연구(전체 모집단, `legacy/research/observations/`)

| 문서 | 핵심 |
|---|---|
| `intake-gap.md` | **격차의 뿌리 = 머리 수.** 500형 섭취 격차 514 중 머리 511, 머리당 속도 3. 머리 r10 5.9 대 9.4, r50 8.0 대 20.1, r100 12.1 대 35.1, r250 16.2 대 51.3. 초반 분열 속도 0.08 대 0.64. 제안 pf, dsp, rd |
| `supply-chain.md` | 전환 결정·실행은 상위권과 같고 재료가 모자라다. r250 뒤 새 조각 156 대 8.7(120이 길이 4의 2+2). 새끼 선점을 긴 아군·상대에게 뺏긴다. 제안 lsplit, cl/ce, cov, fc |
| `endgame-king.md` | 최종 왕 격차 −21.5의 80%가 희생 진주다. 상위권 왕은 늦게 빨리 자란다(0.18/라운드). 모이기는 돕지만 목표가 바뀌고(33%) 가로채기가 있다(26–35%). 왕 노출 52 대 32%. 전체 모집단 재계산본 |
| `conversion-chain.md` | 상위권 희생 판당 59, 계보 몫 24%(양이 무기). 왕 = 끝까지 산 최장(r450 90%). 우리 전환은 대상 고르기에서 끊긴다 |
| `economy-principles.md` | E4 국지 수 교환 지지(열세 41% · 우세 77%). E1·E2·E8·E9 반박, E3·E5·E6 섞임, E7 부분 |
| `our-eliminations.md` | 전멸형 81% 전멸, 수 적은 채 1:1 교환. 상위권 패자는 낮은 수에서 2.0번 나눠 23–26% 회복 |
| `top-territory.md` | 진주는 가까운 쪽이 먹는다. 승자는 샘부터 지킨다. merge2 r100 4마리 대 승자 30 |
| `top-clock-vs-state.md` | 상위권 늦은 희생은 시계형이다(팀 고정 라운드, r250·r400 계단). 지도별 시작 r370–430 |
| `top-mass-spending.md`, `top-decisions-large.md`, `mech-merge2-failures.md` | 질량 쓰임, 결정 규칙 대규모, 실패 사례(위협 모형 빈틈 등) |
| `hypotheses-stack6-20260930.md` | 결정 학습 가설 순위(현재 봇 기준): R7 유지, B3·P1·R1·R3 더 자주 |
| `top-fragments.md`, `top-timing.md`, `top-maps-matchups.md`, `top-sonar.md`, `our-sonar.md`, `pearl-variants.md` | 조각, 시간, 지도 대진, 음파, 진주 판본 |
| `elite-counterplay.md` | Codex. 극상위권 상대별 대응(작성 중일 수 있음) |
| `bot-architecture-audit.md` | Codex(02:17 끝). stack11 구조 감사: 3,947줄, 상수 246, 불 토글 41(참 25). 탈출 분열이 모든 분열의 75%다. **음파 id가 8비트로 잘린다**(id >255가 W12 차례의 29%). 음파 내용은 행동 전 상태다. GH·KX는 소스에서 여전히 참이다(기준점도 같음). 기억이 만료되지 않고 죽은 코드가 있다 |
| (예정) `outcome-review.md` | Codex. 상위 7팀 성적 검토와 승리 해부 |

- **외부 딥 리서치:** `legacy/research/external/`에 Battlesnake, 방법론, 코드 기술, 경제가 있다. 반영 요약은 `INTEGRATION-2026-09-30.md`다.
  - **모이·덮기·전환 딥 리서치(2026-10-01 02:15, 사용자 Orca Codex):** `research/external/deep-research-foraging-coverage.md`, `.json`. 115개 주장을 3회 심사해 81개를 유지하고 34개를 반박했다. 이전 규칙은 9개 지렛대에 24개다.
  - v1 떼 엔진에 직접 쓸 규칙:
    1. 만료 임대(2/4/8턴)와 도착 시간 → 기회비용 → id 순서로 중복 목표를 막는다.
    2. 생성 시도 라운드 전에 몸 조각을 샘 칸에서 모두 비운다.
    3. 왕의 순성장은 자기 행동당 1 이하이므로 곁 먹이기를 순서대로 보낸다.
    4. 분열 짝홀: 4 → 2+2는 사망 진주를 늘리지 않고, 6 → 3+3은 1 늘린다.
    5. 머리 수는 닿을 수 있는 서비스 수요를 따른다.
- 독립 재계산: `legacy/research/experiments/verification-2026-09-30.md`(E4, 공급망, W8 수치 모두 재현).

## 4. 가설 검증 기록(`legacy/research/experiments/`)
- **웨이브별 판정:** `cand-stack1..12.md`, `cand-mapid.md`, `cand-conv2.md`, `cand-swarm1.md`. 사전 등록 기준, 로컬 결과, 온라인 판정, 핵심 수치가 들어 있다.
- **웨이브별 적용 확인 보고서:** `mech-cand-stack*.md`. 기능마다 발동, 상황, 의도대로, 상대별·지도별·국면별 값, 실패 사례의 기보 위치가 있다.
- **기보 선별:** `triage-cand-stack*.md`(가장 크게 진 판, 이긴 판, 부류별 최악)
- **한 줄 요약:** `VERSIONS.md`(올린 봇), `STACK-BACKLOG.md`(가설 대기열 1–50번과 판정), `WAVE-PLAN-2026-09-30.md`(계획, 점수 올리는 방법)
- **점검:** `research/CHECKPOINT-2026-10-01.md`(이 저장소에 사본)

## 5. 코드(부품)
- **기준점:** `benchmark/`(stack11). **처음 봇:** `bot/`(같음).
- **기능별 구현:** `legacy/exp/cand-stack<N>/bot/`, `bot.diff`, `apply.js`
  - stack1 conv·ram4·ks, stack2 frag·grab, stack3 ks2, stack4 tg·esc-split·px·gx
  - stack5 csplit·F·cov·no-exit s, cand-mapid mapid·bsp, stack7 floor·kcap
  - stack8 F2·F2p·cl·ce·px2, stack9 lsplit·fc·cov, stack10 lnt·utab
  - stack11 gh·kx·lwk, stack12 pf
- **추출기(진단 지표용):** `legacy/exp/intake-gap/`, `legacy/exp/endgame-king/`, `legacy/exp/supply-chain/`, `legacy/exp/econ-principles/`, `legacy/exp/conv-chain/`, `legacy/exp/eliminations/`, `legacy/exp/territory-analysis/`
