# eval/: 판정 도구

`EVAL.md`의 판정 규약을 계산하는 도구다. 주 보고서는 `system_report.js`다. 옛 `tools/mech_check.js`는 기능 표식 진단용으로만 남는다.

## system_report.js

온라인 세트 하나 또는 여러 세트의 합산을 받아 보고서를 만든다. 내용은 결과, 진단 지표 다섯, 엔진 표식이다. 기보와 캐시만 읽는다. 판을 돌리지 않고 네트워크도 쓰지 않는다.

```
node eval/system_report.js <세트>[+<세트>...] [<세트> ...] [--vs <세트>[+<세트>...]]
    [--name <이름>] [--vs-name <이름>] [--out <보고서.md>] [--json <보고서.json>] [--no-extract] [--online <폴더>]
```

- 세트는 `data/online/<세트>`다(`index.json`, `game-<id>.json`, `M<id>.replay`). `+`나 여러 인자로 합산한다.
- `--vs`: 비교 풀. 차이, 단측 검정, 검정력 표를 그 풀에 대해 낸다. 없으면 검정력 표는 `EVAL.md` 기준점(81/900)에 대해 낸다.
- `--out`이 없으면 Markdown을 표준 출력에 쓴다. `--json`은 모든 수치를 구조로 쓴다.
- `--online <폴더>`: `data/online`처럼 놓인 다른 폴더(로컬 세트 시험용). `--no-extract`와 함께 쓴다.

예:

```
node eval/system_report.js cand-stack11-online --out exp/system-report/w12.md --json exp/system-report/w12.json
node eval/system_report.js <v1 세트 셋을 +로> --vs cand-merge2-online+...+cand-stack11-online --vs-name "stack11 계열 15웨이브"
```

### 모집단
- 상위 6팀(306, 70, 20, 801, 264, 46)과 DEV 545의 판만 센다. 다른 상대의 판은 건너뛰고 "Sources" 표에 수를 적는다.
- 결과(1절)는 상위 6팀과 DEV 545를 따로 적는다.
- 진단 지표(2절)는 상위 6팀 + DEV 545 전체다. 옛 판정 문서의 "앞선 지표"가 이 모집단이었다(W12 70판).

### 자료 출처(판마다)

| 부분 | 출처 | 캐시 |
|---|---|---|
| 결과 | `index.json`(ourSide, winner, ourWin), `game-<id>.json`의 `replay.result`(endReason, dragonCount, longestDragon) | 없음 |
| 질량 장부 | `tools/mass_ledger.js` | `.cache/mass-ledger/online-<세트>.jsonl`(링크로 공유). 기보는 있는데 줄이 없는 판이 있으면 `node tools/mass_ledger.js extract online <세트> --jobs 2`를 nice로 돌린다(`--no-extract`면 안 돌림) |
| 끝판 | `legacy/exp/endgame-king/extract.js`의 `analyse()`(끝판 연구 추출기, 그대로) | 먼저 `.cache/endgame-king/online-<세트>.jsonl`(옛 캐시, 읽기만)을 본다. 없는 판은 여기서 계산해 `exp/system-report/cache/endgame-online-<세트>.jsonl`에 같은 형식으로 쓴다 |
| 엔진 표식 | 기보의 우리 `dragonIndicator` 글 | `exp/system-report/cache/labels-online-<세트>.jsonl`. 세트마다 첫 기보로 먼저 본다. 그 판에 ` E=` 표식이 없으면 표식 없는 세트로 보고 나머지는 읽지 않는다 |

### 정의

**결과(1절)**
- W: `ourWin`이 참. D: `winner`가 없음(무승부). L: 나머지.
- E(우리 전멸): endReason `teamEliminated`이고 우리 dragonCount 0. 상대 전멸은 따로 센다. 15웨이브 1,050판의 전멸 466은 모두 우리 전멸이었다.
- 모든 비율에 Wilson 95% 구간(z = 1.96)을 붙인다.
- 끝 최장: `replay.result`의 longestDragon(전멸하면 0), 판 평균, 우리 / 상대.
- 지도 가족: 요새 지도 = Autarky, Prisoners Dilemma, Portals. 떼 지도 = 나머지 일곱(`ENGINE.md`, `bot/policy.hpp`와 같다).
- 표: 전체, 가족별, 지도별, 상대별(상위 6팀), DEV 545(전체, 가족별, 지도별).

**비교(`--vs`)**
- 상위 6팀 승률의 차이와 Newcombe(Wilson 기반) 95% 구간을 낸다.
- 단측 Fisher 정확 검정 p를 두 방향으로 낸다. "이 풀 > 비교 풀"은 떼 지도의 목표이고, "이 풀 < 비교 풀"은 요새 지도의 퇴보 감시다. 전체, 요새, 떼, DEV에 대해 낸다.
- 우리 전멸(상위 7팀 판)은 "이 풀 < 비교 풀" p를 낸다.

**검정력 표**
- 단측 Fisher 정확 검정, α = 0.05다. 비교 풀은 관측 승률과 판 수로, 새 버전은 참 승률 12/14/17/20%(`EVAL.md` 표의 행)로 둔다. 두 풀 모두 이항이라고 보고 정확히 합한다.
- 열은 1, 2, 3, 4, 6웨이브(상위 6팀 60판 단위)와 이 풀의 크기다. 마지막 줄은 p < 0.05에 필요한 최소 승수다.
- `EVAL.md` 1절의 표는 고정 9.0%에 대한 값이고 계산법이 적혀 있지 않다. 81/900에 대한 이 계산은 그 표와 ±0.06 안에서 맞는다. 예를 들어 3웨이브(180판)에서 12% 0.30(표 0.31), 14% 0.58(0.57), 17% 0.88(0.86), 20% 0.98(0.97)이다.
- 같은 시기 기준점 1웨이브(60판)를 비교 풀로 쓰면 검정력이 크게 준다. 예를 들어 W12 대 W11에서 3웨이브, 17%일 때 0.44다. 주 판정은 합산 기준점(900판)에 대고, 같은 시기 웨이브는 상대 변화 감시로 쓴다.

**진단 지표(2절, `EVAL.md` 2절)**
- 칸: 지도 가족(요새·떼) × 지도 종류로 나눈다.
  - 500형(r500) = Autarky, Portals, Schooltime, Slithery Fight, Trauma
  - 전멸형(elim) = Default, Devil, Prisoners Dilemma, Queen Of Spades, Trophy
  - 종류 구분은 `tools/mass_ledger.js`의 R500/ELIM, 곧 연구 문서의 "500형·전멸형"이다. 판이 실제로 500라운드까지 갔는지가 아니다.
- r100 머리: 장부 `st.units[10]`. r100 시작에 살아 있는 드래곤 수이고, 전멸하면 0이다. 판 평균, 우리 / 상대.
- 자연 진주 섭취: 판 전체의 `fl` nat_own + nat_enemy + nat_neutral 합이다. 판 평균이다. 비율은 우리 합 ÷ 상대 합이다.
- 계보 희생 진주 r300–499: 끝판 추출기의 `dec[b][1]`을 b = 1..4(r300–349 … r450–499)로 더한다. 최종 왕 계보가 먹은 우리 희생 사망 진주다.
  - 그 팀의 "끝까지 간 판"(500라운드, 최종 왕 있음)의 평균이다. mech_check의 gh·kx 행("500형 끝까지")과 같다.
  - 괄호 안은 판 수(우리 / 상대)다.
- 끝 최장: 장부 `st.king[50]`. 판 평균이다.
- 전멸: 우리 전멸 ÷ 판(Wilson). v1 목표는 전멸형 지도에서 본다.

**엔진 표식(3절)**
- 우리 드래곤의 표식 글 끝의 ` E=F` / ` E=S`(`bot/main.cpp`, v0부터)를 지도별로 센다. 차례 수와 E=S 몫을 낸다.
- 표식이 없는 차례는 "unlabelled"다.
- v0에서 E=S는 "떼 엔진으로 배정됨"이다. 행동은 요새 엔진 그대로다(`bot/engine.hpp`).

### 검증(2026-10-01, 보고서는 `exp/system-report/`)
아래 값은 모두 점검 문서와 옛 판정 문서의 값과 같다.

| 풀 | 값 | 기대(출처) | 보고서 |
|---|---|---|---|
| 15웨이브(W0 merge2 ×3 + W1–W12) | 상위 6팀 81/900 = 9.0%(7.3–11.0%), DEV 28/150, 전멸 466/1050 | `research/CHECKPOINT-2026-10-01.md` 1절, `EVAL.md` 1절 | `w0-w12.md` |
| 같은 풀, 지도별 | Autarky 37/90, PD 22/90, Portals 16/90, Trauma 3/90, Slithery 3/90, 나머지 0/90. 요새 75/270, 떼 6/630 | `ENGINE.md` 표 | `w0-w12.md` |
| W12(`cand-stack11-online`) | 상위 6팀 6/60, DEV 3/10, 전멸 26/70 | 점검 1절 | `w12.md` |
| W12 500형 | 섭취 227.4 대 710.5(32%), r100 머리 12.3 대 32.6, 끝 최장 23.3 대 42.8. 전멸형 섭취 73.9 대 264.1 | `legacy/research/experiments/cand-stack11.md` W12 판정 | `w12.md` |
| W12 계보 희생 진주 r300–499 | 10.3(500형 끝까지 32판) | `legacy/research/experiments/mech-cand-stack11.md` gh 행 | `w12.md` |
| W6–W12 합산(7세트) | 상위 6팀 38/420, DEV 16/70, 전멸 179/490 | 점검 1절 표의 합 | `w6-w12-vs-w0-w5.md` |

- 통계 함수(Fisher 단측 p, Wilson)는 파이썬 정수 연산(`math.comb`, `Fraction`)으로 따로 계산해 소수 여섯째 자리까지 같았다.
- W12 끝판 수치는 옛 캐시에 W12가 없어서 여기서 계산했다(70판, 약 30초). 추출기 자체 점검(chk, chk2)은 모두 0이다.
- 3절(엔진 표식)은 v0 로컬 기보 5판으로 만든 모의 세트(`--online`)에서 확인했다. Autarky·Portals는 E=F 100%, Default·Schooltime·Slithery Fight는 E=S 100%였다.

### 한계
- 판본(a/b)별 칸은 아직 없다. 지도별 표는 가족 단위다.
- 진단 지표의 모집단은 상위 7팀 전체다. 상위 6팀만 따로 보려면 JSON의 판별 값을 다시 묶어야 한다.
- 새 온라인 세트의 첫 실행은 질량 장부 추출과 끝판 계산 때문에 몇 분 걸릴 수 있다. 다음부터는 캐시를 읽는다.
