# 상위권 리플레이 특징 추출 (`tools/top_features.js`)

`data/top/`에 모이는 상위권(레이팅 1900 이상 팀끼리) 대전 리플레이에서 경기마다 JSON 한 줄씩 특징을 뽑는다. 리플레이만 읽고 경기는 돌리지 않는다. 원격 접근도 없다.

## 사용법
```
node tools/top_features.js [--limit N] [--jobs K] [--force]
```
- **입력:** `data/top/index.jsonl`(수집기가 5분마다 덧붙인다)과 리플레이 `data/top/<battleId>/<gameId>.replay.gz`.
- **출력:** `data/top/features.jsonl`. 경기당 한 줄이고, 키는 `battleId:gameId`다. 줄은 처리가 끝난 순서로 붙으므로 index 순서가 아니다.
- **기본 동작(증분):** 출력에 없는 경기만 처리해서 덧붙인다. 몇 번을 다시 돌려도 된다.
- `--limit N`: 이번 실행에서 최대 N판만 처리한다. index 순서로 고른다. 검증용으로 쓴다(`--limit 20`).
- `--jobs K`: 워커 스레드 수. 기본은 6이다.
- `--force`: 고른 경기를 다시 계산한다. 다른 경기의 줄은 그대로 두고 `features.jsonl.tmp`에 새로 쓴 뒤, 끝에 한 번에 바꿔 끼운다. 스키마를 바꾼 뒤에 쓴다.
- **안전장치**
  - `features.jsonl.lock`(PID)으로 동시 실행을 막는다. 살아 있는 실행이 있으면 아무것도 하지 않고 끝나고, 죽은 실행의 잠금은 치운다.
  - 중단 때문에 마지막 줄이 잘렸으면, 다음 실행이 그 줄을 지우고 이어 쓴다.
  - 읽지 못한 경기는 쓰지 않는다. 다음 실행에서 다시 시도한다.
- **실행 요약:** 처리 수, 오류 수, 시간, `simMismatches` 분포, 나머지 점검의 합계를 찍는다. 오류가 있으면 종료 코드가 1이다.
- **비용(2026-09-29, 6 jobs):**
  - 464판 전체 재계산에 53~82초가 걸렸다. 시간은 대부분 capnp 해석이다.
  - 최대 메모리는 약 1.8GB다.
  - 한 줄은 중앙값 약 31KB, 최대 약 207KB다. 464판이면 21.5MB다.

읽기 예:
```js
const rows = require('fs').readFileSync('data/top/features.jsonl', 'utf8').trim().split('\n').map(JSON.parse);
```

## 스키마
한 줄은 `{ meta, A, B }`다. A와 B는 팀이고, 같은 모양이다.

### meta
| 필드 | 뜻 |
|---|---|
| `battleId`, `gameId`, `map` | index 행 그대로 |
| `width`, `height` | 지도 크기 |
| `teams.A`, `teams.B` | `{name, elo, rank}`. index 행의 teamA/eloA/rankA 등이다. |
| `winner` | `'A'` 또는 `'B'`. index의 소문자를 대문자로 바꿨다. |
| `ranked`, `at` | index 행 그대로(대전 단위) |
| `seed` | 경기 시드. 16자리 hex이고, 형식 2 리플레이의 루트에 있다. |
| `endReason` | `R.result.endReason`: `roundLimit` 또는 `teamEliminated` |
| `rounds` | 실제로 시작된 라운드 수(마지막 roundStart + 1). 끝까지 가면 500이다. |
| `final.A`, `final.B` | `R.result`의 `{dragonCount, longestDragon, totalLength}` |
| `simMismatches` | 재구성 일관성 점검. 이동 한 걸음마다 시뮬레이션한 머리·꼬리가 리플레이의 dragonUpdate와 다른 횟수다(analyze.js와 같은 정의). |
| `checks` | 추가 점검. 아래 "검증" 절에 있다. |

### 팀 객체 (`A`, `B`)
50라운드 창은 `w = floor(round / 50)`이다. 0은 라운드 0–49, 9는 450–499다.

| 필드 | 형태 | 뜻 |
|---|---|---|
| `timeline` | `{r, units, total, longest}` 51개 | r = 0, 10, …, 500. 값은 라운드 r이 시작하기 직전, 곧 r라운드를 마친 뒤의 상태다: 살아 있는 드래곤 수, 몸길이 합, 최장 길이. r = 0은 초기 상태이고, r = 500은 최종 상태다. 경기가 일찍 끝나면 그 뒤의 점은 최종 상태를 그대로 이어 쓴다. |
| `splits` | `[round, parentLenBefore, childLen, unitsBefore]` 배열 | 분열 한 번에 한 개. `parentLenBefore`는 분열 직전 부모 길이(= 분열 뒤 부모 + 자식)다. `unitsBefore`는 분열 직전 그 팀의 생존 수이고, 부모를 포함한다. 불법 분열은 분열이 아니라 사망(`A`, `why: 'split'`)으로 남는다. |
| `deaths` | 객체 배열 | 아래 표 |
| `eaten` | 숫자 10개 | 창마다 먹은 진주 수. 머리가 진주 칸에 들어간 걸음 수다. |
| `sprints` | 숫자 10개 | 창마다 2걸음 이상인 이동 행동 수. 시도 기준이라 도중에 죽은 경우도 들어간다. 3걸음 이상도 포함한다. |
| `longSprints` | 숫자 10개 | `sprints` 중 3걸음 이상인 것 |
| `sonar` | 객체 | 아래 표 |

### `deaths` 원소
| 필드 | 뜻 |
|---|---|
| `r` | 사망 라운드 |
| `id` | 드래곤 id. 초기 드래곤이 가장 작은 id를 가진다. `id < timeline[0].units(A) + timeline[0].units(B)`이면 초기 드래곤이다. |
| `reason` | 리플레이에 적힌 사망 원인. `W`는 해초로 이동, `S`는 자기 몸, `O`는 다른 드래곤 몸, `H`는 머리끼리(둘 다 죽음), `A`는 유효 행동 없음이다. |
| `why` | `reason`이 `A`일 때만 있다. 값은 아래 목록이다. |
| `len` | 죽는 순간의 몸길이. 움직이다 죽었으면 치명 걸음 직전 길이이고, 질주의 앞선 걸음은 반영한다. 떨어지는 진주는 ceil(len/2)개다. |
| `born` | 태어난 라운드. 초기 드래곤은 0이다. 라운드 0에 분열로 태어난 자식도 0이므로, 둘은 `id`로 구별한다. |
| `mover` | 자기 차례에 죽었으면 true다. false는 H의 피해자(남이 머리로 들이받음)뿐이었다. |
| `hitTeam`, `hitLen` | `mover`이고 O/H일 때만 있다. 들이받은 상대의 팀(`'A'`/`'B'`)과 그때 길이다. |
| `byTeam`, `byLen` | `mover`가 아닐 때(H 피해자)만 있다. 들이받은 쪽의 팀과 길이(치명 걸음 직전)다. |

`why` 값:
- `split`: 불법 분열(SPLIT 1, 길이 부족 등)
- `suicide`: MOVE/SPLIT 없이 턴을 끝냄(엔진의 기본 행동이 남음)
- `sprint`: 비용을 치를 수 없는 질주
- `tle`: 시간 초과(행동이 전달되지 않음)
- `none`: 행동 없음, tle 표시도 없음
- `other`: 그 밖. 지금까지 관측되지 않았다.

팀 문자를 죽은 드래곤의 팀과 비교하면 아군인지 적인지 알 수 있다. 머리끼리 충돌 한 건은 두 줄로 남는다. 피해자가 먼저 죽고(`mover: false`), 들이받은 쪽이 다음에 죽는다(`mover: true`).

### `sonar`
| 필드 | 뜻 |
|---|---|
| `sent` | 창마다 보낸 음파 수. 리플레이의 sonarPing, 곧 실제로 쏜 광선이다. 발신자가 그 턴에 죽으면 음파가 나가지 않고 기록도 없다. |
| `self`, `ally`, `enemy`, `none` | 창마다 음파가 멈춘 곳이다. `self`는 발신자 자신의 몸(머리 포함), `ally`는 다른 아군, `enemy`는 적, `none`은 드래곤이 아닌 곳(해초 또는 아무것도 못 만남)이다. 넷의 합은 `sent`와 같다. |
| `enemyHead` | `enemy` 중 적의 머리에서 멈춘 수. 광선의 끝 칸이 재구성한 그 드래곤의 머리 칸과 같으면 센다. |
| `distinctValues` | 경기 전체에서 그 팀이 보낸 서로 다른 64비트 값의 수. 0도 하나로 센다. |
| `dragonRounds` | 그 팀 드래곤이 받은 턴 수(생존 드래곤 × 라운드). 분열로 태어난 자식이 같은 라운드에 받는 첫 턴도 포함한다. |
| `pingsPerDragonRound` | 보낸 음파 합 / `dragonRounds`. 소수 4자리까지 남긴다. |

## 재구성 방법
g5의 `lineages/g5/tools/analyze.js`에서 몸 재구성 핵심을 옮겼다. 그 도구는 로컬 160판에서 불일치 0이었다.
- **이동:** 초기 드래곤에서 출발한다. 이동 행동(dragonAction move)마다 `rules/execution-order.md` 순서대로 걸음을 시뮬레이션한다.
  - 두 번째 걸음부터 비용을 치른다. 길이가 2면 치를 수 없어 A로 죽는다.
  - 해초, 포털, 가장자리 감싸기를 적용한다.
  - 자기 몸(꼬리 포함), 다른 드래곤(머리면 H) 순서로 충돌을 검사한다.
  - 머리를 옮기고, 진주를 먹으면 꼬리를 그대로 둔다.
- **분열·사망·진주:** 분열은 리플레이에 적힌 부모·자식 몸을 그대로 쓴다. 사망하면 제거한다. 진주는 tileChange로 추적한다.
- **analyze.js와 다른 점**
  1. 질주 도중 죽으면 이미 간 걸음은 반영한다. 그래서 `len`이 규칙의 "죽을 때 몸"과 맞는다(`checks.drops`로 확인).
  2. 불일치가 나면 뷰어처럼 dragonUpdate로 몸을 다시 맞춘다. 오류 하나가 경기 끝까지 번지지 않는다.
  3. 분열은 분열 전 부모 길이를 기록한다. analyze.js의 `pLen`은 분열 뒤 길이였다.
  4. 한 진영만이 아니라 두 팀을 모두 기록하고, A 사망의 세부 원인(`why`)을 남긴다.

## 서버 리플레이(형식 2)와 로더
**형식 차이:** 서버 리플레이는 모두 형식 2다. `tools/viewer.js`와 `tools/replay.js`가 쓰는 뷰어(`.venv-ppo`의 unswbc)는 형식 1 스키마를 쓰고, 형식 검사만 풀어서 읽는다. 대부분의 사건은 그대로 맞지만 음파 값은 틀린다.
- `sonarPing.value`는 형식 1 자리(UInt32 @8)를 읽는데, 형식 2에서는 늘 0이다.
- 실제 64비트 값은 UInt64 @16(`value64`)에 있다. 형식 2 음파의 95%가 2^32보다 크다.
- 멈춘 곳의 종류는 UInt16 @24(`hitKind`)에 있다. 0 unknown, 1 empty(아무것도 못 만남), 2 kelp, 3 ally, 4 allyHead, 5 enemy, 6 enemyHead다. 발신자 기준이고, 자신에게 돌아온 광선은 ally/allyHead다.
- 리플레이 루트에는 시드가 붙었다. UInt16 @4가 1이면 UInt64 @8이 시드다.
- 이 배치는 unswbc 1.1.0 뷰어(`../UNSW/.unswbc-110/unswbc/replay-viewer.vsix`)의 스키마와 같다.

**이 도구의 로더:** `tools/replay.js`와 같은 뷰어 소스를 vm에서 돌리되, 내부 함수(`Df`, `bf`, `Of`, capnp 유틸 `$`)를 꺼내 위 필드를 함께 읽는다. 나머지 필드는 `tools/replay.js`의 결과와 사건 단위로 같다. 사건 11만 개와 22만 개인 두 판에서 차이가 0이었고, 지도·결과·팀 정보도 같았다.

**다른 도구에 주는 영향:** `tools/viewer.js`의 `load()`로 읽으면 음파 값이 모두 0이다. 로컬 리플레이도 형식 2라서 마찬가지다. 2026-09-29부터 `tools/replay.js`는 이 도구의 로더를 쓰므로 값이 제대로 나온다. `tools/observe_local.js`와 `tools/observe_online.js`도 같은 우회를 쓴다.
```js
const { load } = require('./tools/replay.js');
const R = load(file); // sonarPing마다 e.value64(BigInt)와 e.hitKind가 붙는다. R.seed, R.formatVersion도 있다.
```
`value64`는 BigInt라서, 사건을 그대로 `JSON.stringify`하려면 변환 함수가 필요하다.

**뷰어 빌드 의존:** 로더는 뷰어 빌드의 축소된 이름과 자르는 지점(`var Af=B(`)에 기댄다. 뷰어가 바뀌면 "unexpected replay-viewer build" 오류로 멈춘다. 조용히 틀린 값을 내지는 않는다.

## 검증
2026-09-29 기준이다. 464판 전부, 음파 약 1,910만 개를 점검했다. 모든 점검은 0이 정상이다.

| 점검 | 뜻 | 결과 |
|---|---|---|
| `simMismatches` | 걸음마다 시뮬레이션한 머리·꼬리 vs dragonUpdate | 464판 모두 0 |
| `checks.deaths` | 움직인 쪽의 사망 원인(W/S/O/H, 질주 비용 A) vs 시뮬레이션. H 피해자는 들이받은 쪽의 시뮬레이션과 짝이 맞는지 본다. | 0 |
| `checks.splits` | 분열 전 길이 = 분열 뒤 부모 + 자식 | 0 |
| `checks.eaten` | 시뮬레이션으로 먹은 진주 수 vs 진주가 사라진 tileChange 수(팀별) | 0 |
| `checks.drops` | 사망 직후 생긴 진주 수 = ceil(`len`/2). `len`을 확인한다. | 0 |
| `checks.hitKind` | 리플레이의 hitKind vs 재구성한 판(자신·아군·적, 머리 여부) | 0 |
| `checks.pings` | 발신자나 맞은 드래곤을 찾지 못한 음파 | 0 |
| `checks.finalMatch` | 최종 timeline = `R.result`(수, 최장, 합) | 모두 true |
| `checks.winnerMatch` | index 승자 = `R.result` 승자 | 모두 true |
| `checks.format` | 리플레이 형식 | 모두 2 |

hitKind 분포는 418판 기준으로 2(kelp) 987만, 3 430만, 4 251만, 5 33만, 6 21만이다. 0과 1은 없었다. 지도마다 한 판씩 보니 2는 모두 해초 칸에서 멈췄다.

## 알려진 한계
- **elo·rank:** 수집 시점의 리더보드 값이다(`tools/collect_top.js`). 경기 당시 값이 아니다. 리더보드에 없는 팀은 rank가 null이다(464판 중 23판).
- **timeline 종료 뒤:** 경기가 끝난 뒤의 점은 최종 상태를 이어 쓴 값이다. 조기 종료(teamEliminated)가 464판 중 219판이다. 라운드별 평균을 낼 때는 `meta.rounds`로 거르거나 그 처리를 명시한다. 50라운드 창 배열도 경기가 끝난 뒤의 창은 0이다.
- **none:** 해초와 empty(아무것도 못 만남)가 함께 들어 있다. 다만 지금까지 empty는 없었다.
- **sonar 값의 뜻:** 값은 개수만 센다. 메시지 형식은 해석하지 않는다. 한 번도 음파를 쓰지 않은 팀은 `distinctValues`와 `pingsPerDragonRound`가 0이다(팀·경기 928개 중 48개).
- **sprints:** 행동(시도) 기준이다. 실제로 간 걸음 수나 치른 몸길이는 따로 남기지 않는다. 418판 기준 걸음 수 분포는 2걸음 18,528, 3걸음 3,444, 4걸음 412, 5걸음 이상 87이다.
- **eaten:** 먹은 수만 센다. 먹을 수 있었던 진주나 진주 생성량은 세지 않는다.
- **why=suicide:** 봇이 일부러 행동을 내지 않았는지, 출력이 잘못돼 기본값이 남았는지는 리플레이로 구별할 수 없다. 로그와 지시자는 이 도구가 읽지 않는다.
- **표본:** 팀 이름으로는 봇 버전을 구별할 수 없다. 같은 팀이 제출을 바꿔도 이름은 같다. 한 팀이 여러 경기에 나오므로 경기들은 독립 표본이 아니다.
- **메모리:** 워커 하나가 리플레이 하나를 통째로 해석한다. 6 jobs에서 최대 약 1.8GB다. 메모리가 빠듯하면 `--jobs`를 줄인다.
