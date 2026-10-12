# 온라인 서버 운영 (game.battlecode.au)

2026-09-29에 작성했다. 대상 서버는 `https://game.battlecode.au/api/v1`이고, 우리 팀은 id 583(JJYA)이다.

**표기**
- **[사실]**: 이번에 직접 조회했거나 원자료에 있는 내용이다. 근거 경로를 붙인다.
- **[검증 전]**: 추론이나 제안이다.

이번 조사에서는 GET만 썼다. 대전 신청, 업로드, 티켓 사용은 하지 않았다(`data/online/REMOTE-LOG.md`).

## 한눈에 보기
- **인증:** 팀원별 API 키(`bc_...`)를 `Authorization: Bearer` 헤더에 넣는다. 키 파일은 `~/Downloads/api.txt`이고, 내용을 화면, 파일, 로그, 커밋에 남기지 않는다.
- **티켓:** 서버 용어로는 "시간당 허용량(hourly allowance)"이다.
  - 우리가 직접 신청한 대전만 티켓을 쓴다.
  - 일반 팀 상대로 시간당 60게임을 쓸 수 있다. DEV(운영) 팀 상대로는 따로 60게임이 있다.
  - 비랭크는 지도 1개가 1게임이고, 랭크는 1회가 5게임이다.
  - 자동 대전(autoscrim)은 티켓을 쓰지 않는다.
- **잔량:** 공식 잔량은 API로 읽을 수 없다. 사이트에 로그인한 브라우저에서만 보인다.
  - `node tools/online.js tickets`가 최근 60분의 신청 기록으로 잔량을 추정한다.
  - 2026-09-29 11:41Z 추정치는 일반 60, DEV 60이다.
- **무료 관측:** 모든 대전은 공개된다. 그래서 다른 팀끼리 한 대전(상위권끼리 포함)의 리플레이도 우리 키로 받을 수 있고, 티켓이 들지 않는다.
- **도구:** `tools/online.js`로 조회, 다운로드, 신청을 한다. 신청은 `--confirm --expect-active <제출 id>`가 없으면 계획과 예상 비용만 출력한다.

## 1. `tools/online.js` 사용법
키는 `$UNSWBC_KEY`에서 먼저 찾고, 없으면 `~/Downloads/api.txt`의 첫 `bc_...` 값을 쓴다. 파일 경로는 `$UNSW_KEY_FILE`로 바꿀 수 있다.

키는 game.battlecode.au로 가는 헤더에만 넣는다. 출력, 파일, 자식 프로세스에는 넘기지 않고, 서버 응답 문자열은 가려서 출력한다. 리플레이는 서명된 임시 링크로 받는데, 이 요청에는 키를 붙이지 않는다.

| 명령 | 하는 일 | 티켓 |
|---|---|---|
| `leaderboard [--top 20] [--eligible] [--ranked] [--json]` | 순위표와 신청 가능 여부(비랭크/랭크)를 보여 준다. `--eligible`을 주면 신청 가능한 팀만 보인다. | 0 |
| `team [<id>] [--json]` | 팀 정보, 게임 전적, 랭크 스위치, 최근 대전 6건을 보여 준다. id를 빼면 우리 팀이다. | 0 |
| `tickets [--json]` | 시간당 허용량 추정치(일반, DEV)와 다음 반환까지 남은 분을 보여 준다. | 0 |
| `submissions [--all] [--json]` | 제출 목록과 활성 제출(`*`)을 보여 준다. | 0 |
| `battles [--limit 20] [--json]` | 최근 우리 대전을 시리즈 단위로 보여 준다(최대 200). | 0 |
| `battle <id> [--json]` | 게임별 상태, 승자, 대기열 위치, 신청 주체 추정, 시드, 서버 로그를 보여 준다. | 0 |
| `maps`, `queue` | 현재 지도 풀과 판정 서버 부하를 보여 준다. | 0 |
| `download <id>[,<id>…] [--out <폴더>] [--only] [--no-events] [--purpose "…"]` | 대전(시리즈)의 모든 게임을 `data/online/<폴더>/`에 받는다. 다른 팀끼리 한 대전도 받을 수 있다. | 0 |
| `request <팀id>[,…] \| --top N [--ranked] [--maps all\|4,7\|portals,trophy] [--purpose "…"] [--confirm --expect-active <제출id>]` | 대전을 신청한다. `--confirm`이 없으면 계획만 출력한다. | 비랭크는 지도당 1, 랭크는 5 |

### 상위권 팀과 대전하는 순서
1. `node tools/online.js submissions`: 활성 제출이 시험하려는 봇인지 확인한다.
2. `node tools/online.js tickets`: 남은 허용량을 확인한다.
3. `node tools/online.js leaderboard --top 20 --eligible`: 신청할 수 있는 최상위 팀을 확인한다. 랭크로 신청할 때는 `--ranked`를 붙인다.
4. `node tools/online.js request --top 6 --maps all --purpose "…"`: 대상 팀, 팀별 비용, 합계, 추정 잔량을 출력한다. 이 단계에서는 티켓을 쓰지 않는다.
5. 같은 명령에 `--expect-active <제출 id> --confirm`을 붙여 실제로 신청한다. 다음 경우에는 아무것도 신청하지 않는다.
   - 활성 제출이 `--expect-active`와 다를 때
   - 신청할 수 없는 대상이 하나라도 있을 때
   - 추정 잔량이 필요한 게임 수보다 적을 때
   여러 팀에 신청할 때는 한 건이라도 거절되면 거기서 멈춘다.
6. `battles`와 `battle <id>`로 진행을 확인한다. 대기열이 비어 있으면 신청하고 몇 초 뒤에 끝난다(2.4 참고).
7. `download <id> --out <폴더> --purpose "…"`로 기록을 받는다. 같은 명령을 다시 돌리면 이미 받은 게임은 건너뛰고, 끝나지 않은 게임만 다시 시도한다.

`request --top N`은 순위표 위에서부터 신청 가능한 팀 N개를 고른다. CLAUDE.md의 "리더보드 최상위권 팀 우선" 규칙을 따른 것이다. DEV 팀도 순위대로 포함하며, DEV 팀 상대 게임은 별도 허용량으로 계산한다.

### 남는 기록
- `data/online/REMOTE-LOG.md`: 도구가 신청(성공, 거절)과 다운로드를 한 줄씩 자동으로 적는다. 열은 날짜(UTC), 작업, 대상, 목적, 티켓이다.
- `data/online/requests.jsonl`: POST /battles를 할 때마다 한 줄씩 쌓는다. 내용은 시각, 팀, 종류, 지도, 비용, 응답 상태, 게임 id, 활성 제출, 목적이다. `tickets` 추정에도 쓴다.

### `download` 결과 형식
결과는 `data/online/<--out 폴더>/`에 저장된다. 폴더를 지정하지 않으면 `dl-YYYYMMDD`이다.

- `game-<id>.json`
  - 서버의 게임 정보가 들어 있다: 팀, 승자, 점수, 지도, 완료 시각, 서버 로그, 랭크 여부.
  - 추가 필드: `seed`, `requestedAt`, `startedAt`, 레이팅 변화, 팀 이름과 레이팅, 리플레이 결과 요약.
  - `submissionAId`와 `submissionBId`는 리플레이의 `teams.<A|B>.botId`에서 읽는다. 우리 쪽만 채워지고 상대 쪽은 null이다.
- `M<id>.replay`: 리플레이 원본이다. 전송 압축이 풀린 형태이며, 2026-09-27 기록과 형식이 같다.
- `events-<id>.jsonl.gz`: 1행은 `{"meta":…}`이고, 그다음부터 사건이 한 줄에 하나씩 `{round, type, …}` 형태로 들어 있다. `tools/export_replay.js`와 같은 형식에 `mapName`과 `seed`를 더했다.
- `index.json`: `games` 배열이다. 필드는 gameId, map, mapName, ranked, teamAId, teamBId, ourSide(A/B), opponentTeam, ourSubmission, winner, ourWin, requestedAt, completedAt, seed이다.
  - winner는 서버 값 그대로 소문자 a/b이고, ourSide는 대문자이다. 비교할 때는 `ourWin`을 쓴다.
  - 다른 팀끼리 한 대전이면 ourSide, opponentTeam, ourWin이 null이다.
- 읽기: `require('./tools/replay.js').load('data/online/r1-autoscrim/M587111.replay')`로 한 파일을 읽는다. `require('./tools/viewer.js').load(<폴더>)`는 폴더 안의 첫 리플레이만 읽는다.
- 예시(2026-09-29 시험):
  - `data/online/r1-autoscrim/`: 현재 활성 봇 g4-r4의 자동 대전 587111 5게임
  - `data/online/top-sample/`: Cutlery(1위)와 bread first search의 공개 대전 588757 중 1게임

## 2. 확인한 사실

### 2.1 인증과 요청 한도
- **[사실] 키:** 팀원 한 명당 하나이고, 업로드와 신청은 그 팀원 이름으로 기록된다. 새 키를 만들면 이전 키는 폐기된다(`rules/api.md`).
- **[사실] 한도:**
  - 키 하나당 분당 120회이고, `/leaderboard`와 `/ratings`는 분당 30회이다. 넘으면 429와 `Retry-After`가 온다(`rules/api.md`).
  - 없는 경로는 JSON 404를 준다: `{"error":"No such endpoint: /api/v1/…"}`. 2026-09-29에 확인했다.
- **[사실] 같은 키를 쓰는 다른 프로세스:** 지금 두 개가 돌고 있고, 분당 한도를 이들과 나눠 쓴다.
  - `tools/collect_top.js`: launchd `com.jun.unsw-heuristic.collect-top`로 5분마다 돈다. 요청 간격은 0.6초이다.
  - UNSW 배관 데몬(`UNSW/lineages/_daemon/plumber.js`): 3분마다 `online_cli.js active`를 부른다(GET /submissions).

### 2.2 엔드포인트
2026-09-29에 GET으로 응답 모양을 확인했다. 원자료는 `data/online/snapshots/20260929T1141Z/`에 있다.

| 요청 | 응답 내용 | 확인 |
|---|---|---|
| GET /me | user{id, username}, team{id, name, elo, dev, settings{ranked, joinsClosed}, …}, key{prefix, createdAt, lastUsedAt} | 200 |
| GET /team | 우리 팀 정보. team{…, hasBot, code(가입 코드)}, record{wins, draws, losses}(게임 수), history[{date, elo}], peak, rank, recent[6], requests[] | 200. 도구는 code를 지운다 |
| GET /teams/:id | 공개 프로필. /team과 같지만 code와 requests가 없다. recent는 최근 대전 6건이다 | 200 |
| GET /leaderboard | 917팀의 배열. rank(순위 없는 팀은 null), ranked, id, name, elo, wins, hasBot, language, history[32], settings{ranked, unranked(일부 팀), joinsClosed, rankedChangedAt}, dev, 상 자격 필드, members | 200, 1.5 MB |
| GET /ratings | {ladder[{rank, id, name, elo, wins, dev}], histories{팀id: [{date, elo}]}} | 200, 5.9 MB |
| GET /submissions | 배열. id, name, description, language, status(active/idle), uploadedAt, sourceHash, kStart, kFreshAt, wins/draws/losses(게임 수), byMap{지도: {wins, draws, losses}}, version | 200 |
| GET /battles?limit=N | 우리 팀 대전을 시리즈 단위로, 새것부터, 최대 200건. id(첫 게임 id), ranked, opponentId, opponent, opponentElo, eloChange, results[win/loss/pending], wins, losses, outcome(win/loss/draw/live), replayId, at(시리즈의 마지막 게임 완료 시각). 진행 중이면 wait{ahead, ms}가 붙는다 | 200 |
| GET /battles/:id | 게임 1개. match{id, teamAId, teamBId, mapId, ranked, status, winner(a/b), scoresA/B, seriesId, eloChangeA/B, requestedAt, startedAt, completedAt, log, seed, skinA/B, views}, mapName, teamAName/teamBName, teamAElo/teamBElo, games[{id, status, winner, hasReplay, mapName}](같은 시리즈 전체), wait(대기열 위치) | 200. 다른 팀끼리 한 대전도 200 |
| GET /battles/:id/replay | 302로 서명된 임시 링크(Cloudflare R2)를 준다. 이 링크는 키 없이 받는다 | 우리 대전과 다른 팀끼리 대전 모두 받았다 |
| GET /maps | 지도 10개. id, name, sizeLabel, mapText, active, private | 200 |
| GET /queue | judges[{slots, busy}], pending, running | 200 |
| GET /teams | "Find a team" 목록(87팀) | 200 |
| GET /tournaments | 빈 배열(지금은 대회가 없다) | 200 |
| POST /battles | 요청 본문 {teamId, ranked, mapIds?}. 성공하면 201과 {ids: [게임 id…]} | 이번에는 쓰지 않았다. 이전 프로젝트에서 902회 201을 받았다 |
| POST /submissions, POST /submissions/:id/activate, GET /submissions/:id/download | 업로드, 활성화, 업로드한 zip 받기 | 이번에는 쓰지 않았다 |

- **[사실] 제출 id:** GET /battles/:id는 더 이상 `submissionAId`/`submissionBId`를 주지 않는다. 2026-09-27 기록(`data/online/g2/20260927-g2-r6-b1/game-399525.json`)에는 있었다.
  - 대신 우리 대전 리플레이의 `teams.<우리 쪽>.botId`에 우리 제출 id가 들어 있다. 예: 587111의 A쪽 값은 "10365"이다.
  - 상대 쪽 botId는 빈 문자열이다. 다른 팀끼리 한 대전은 양쪽 모두 빈 문자열이다.
- **[사실] 공식 잔량 경로:** 사이트는 `GET /teams/:id/availability`로 잔량을 읽는다. 이 경로에 API 키를 붙이면 401(`"Join a team to request a battle."`)이고, `/api/v1/teams/:id/availability`는 404이다.

### 2.3 티켓 (시간당 허용량)
- **[사실] 허용량:** 현행 문서(2026-09-29) 기준이다(`snapshots/20260929T1141Z/site/docs-game-format.txt`, `docs-api.txt`).
  - 팀이 직접 시작하는 대전은 시간당 60게임까지이고, 랭크로는 12회에 해당한다.
  - DEV 팀 상대 대전에는 별도로 시간당 60게임이 있다.
  - 자동 대전은 허용량을 쓰지 않는다.
- **[사실] 비용:** 랭크 1회는 5게임이고 지도는 무작위이다. 비랭크는 고른 지도 수만큼 게임을 쓴다.
  - 사이트 신청 창 코드에 "This selection uses N games", "Enough for ⌊remaining/5⌋ ranked battles at 5 games each"라는 문구가 있다(`site/bundle-request-dialog.rlfXList.js`).
- **[사실] 사이트의 잔량 표시:** 사이트는 `{remaining, freeIn, dev}`를 받아 아래 문구를 보여 준다.
  - "N games remaining in your team's hourly allowance, shared across every opponent except organising teams"
  - "More games free up in N min"

  허용량은 팀 전체가 함께 쓴다. 우리 팀원은 2명이다.
- **[사실] 이전 프로젝트 기록:** 2026-09-24부터 27일까지 48번에 걸쳐 모두 비랭크로 신청했다.
  - 한 번에 최대 57게임(19팀 × 지도 3개)을 대략 1시간 간격으로 보냈다(`UNSW/experiments/scrim-cycles/*/requests.json`).
  - 신청 910건 가운데 허용량 초과로 거절된 것은 없었다.
- **[사실, 2026-09-30 사용자 브라우저 관측] 허용량 창은 움직이는 60분 창이다.** 07:31 KST에 일반 60판과 DEV 10판을 신청했다. 07:59–08:20에 일반은 0판(freeIn 33 → 13분), DEV는 50판(freeIn 32 → 13분)이었고, 정각에 초기화되지 않았다. 게임마다 따로 돌아오는지, 한꺼번에 돌아오는지는 아직 모른다.
  - 공식 잔량은 로그인 세션 전용 `GET /teams/<상대 id>/availability`로 읽는다. 응답은 `{"dev":true,"remaining":50,"freeIn":32}` 꼴이고 freeIn의 단위는 분이다.
  - `tickets`는 움직이는 60분 창으로 센다. 실제로는 매시 정각에 초기화되는 방식이라면 실제 잔량은 추정치보다 크거나 같다.
- **[사실] `tickets` 추정 방법:**
  1. GET /battles 목록에서 최근 65분 안에 끝났거나 아직 안 끝난 대전의 상세를 읽는다.
  2. 우리가 A측이고, 정각에 요청된 랭크(자동 대전)가 아니고, 요청 시각이 60분 안인 대전의 게임 수를 더한다.
  3. 로컬 원장(`requests.jsonl`)의 합계와 비교해 큰 값을 쓴다.
- **[사실] 과거 시각으로 되돌린 시험:**
  - 2026-09-27T14:40Z 기준 57게임이 나왔다. 그 시각 requests.json의 57게임과 같다.
  - 2026-09-28T14:42–14:44Z에 우리 쪽이 신청한 대전은 랭크 2회와 비랭크 1회(지도 10개)로 20게임이었다. 2026-09-28T15:30Z 기준 추정치도 20게임이다.
- **[사실] 현재 추정치:** 2026-09-29T11:41Z에 일반은 0게임 사용으로 60 남음, DEV도 0게임 사용으로 60 남음이다(`snapshots/20260929T1141Z/tickets.json`).
- **[사실] 신청 주체:** 우리 요청 기록(`UNSW/experiments/scrim-cycles/*/requests.json`)과 대조한 7건에서, 대전 상세의 teamAId가 신청한 팀이었다.
  - 기록에 있는 우리 신청 399525: A=583이다.
  - 기록에 없는 6건(470737, 499734, 500182, 499605, 506980, 546756): A가 상대 팀이다.
  - 자동 대전은 requestedAt이 정각(`…:00:00.000Z`)이다. 표본 8건 모두 우리가 A였다.

### 2.4 대전 신청 규칙과 진행
- **[사실] 공통:** 상대는 `teamId`로 지정한다. 양쪽 모두 활성 봇이 있어야 한다(`hasBot`).
- **[사실] 비랭크:**
  - 봇이 있는 팀이면 누구든 신청할 수 있다. 레이팅은 변하지 않는다.
  - 지도를 고를 수 있다(`mapIds`, 현재 풀의 id). 지도 하나에 1게임이다.
  - 한 번에 지도 풀 전체(10개)까지 넣을 수 있다. 다른 팀이 우리에게 보낸 10게임짜리 500182로 확인했다.
- **[사실] 랭크:**
  - 5게임이고, 지도는 서버가 무작위로 고른다.
  - 양쪽 팀 모두 설정에서 랭크 스위치를 켜 두어야 한다.
  - 상대가 우리보다 50점 넘게 낮으면 신청할 수 없다. 우리보다 높은 팀에는 제한이 없다.
  - 랭크 스위치는 한 번 바꾸면 8시간(480분) 동안 다시 바꿀 수 없다(문서와 `site/bundle-eligibility.DEnjH1Ua2.js`). 우리 스위치는 켜져 있다.
- **[사실] 과거 거절 응답(910회 중):**
  - 404 "No such team." 4회
  - 409 "You already have a pending match against this team." 3회
  - 502 1회

  지도 풀이 바뀐 직후에는 "One of those maps is no longer available"로 거절된 적이 있다(`UNSW/tools/online_plan_ext.js` 주석, 2026-09-27).
- **[사실] 상대당 대기 대전 1개 규칙은 폐지됐다.** `#changelog` 9/27 21:45에 "You can have multiple pending matches against the same team at the same time now"라고 나와 있다. 도구는 대기 중인 대전이 있는 상대에게 경고만 한다.
- **[사실] 스프린트 마감:** `#announcements` 9/28 07:23 "Sprint Deadlines"에 따르면 **2026-10-01 08:00 KST에 활성 제출이 고정되고, 그 뒤로는 제출과 수동 대전 신청이 막힌다.** 이것은 스프린트 마감이다. 우리 목표는 메인 대회인 qualifier(1/10까지)라서 이 마감은 크게 상관없다(사용자, 2026-09-30).
- **[사실] 공개:** 모든 대전은 공개된다(`rules/game-format.md`).
- **[사실] 진행 속도:**
  - 우리가 신청한 399525는 14:32:08에 요청되어 1초 안에 시작했고, 시작 17초 뒤 끝났다.
  - 자동 대전은 정각에 요청되고, 시리즈 첫 id 게임 기준 6–56분 뒤에 시작했다(표본 8건).
  - 2026-09-29 11:36Z에 판정 서버는 3대였고, 슬롯 78개 중 39개를 쓰고 있었다. 대기는 0이었다.
  - 한 시리즈의 게임은 순서 없이 동시에 돈다. 예를 들어 587113이 587111보다 먼저 끝났다.
- **[사실] 진행 중인 대전의 모양:** 2026-09-29 11:50Z에 팀 70의 대전 590335 등에서 관측했다.
  - 목록과 팀 프로필에서는 `outcome`이 `"live"`이고, 끝나지 않은 게임은 `results`에 `"pending"`으로 나온다.
  - 랭크 대전은 `eloChange`가 null이고, `wait: {ahead: 0, ms: 58107}` 같은 필드가 붙는다.
  - 상세의 `games[].status`는 `completed` 또는 `running`이다. 실행 중인 게임은 winner가 null이고 hasReplay가 false이다.
  - 실행 중인 게임 하나를 상세로 조회하면 `wait: {ahead: 0, ms: 3097}`처럼 나온다(590373, 2026-09-29 11:52Z). `download`는 이런 게임을 "아직 안 끝남"으로 건너뛴다.
  - 도구는 outcome이 win/loss/draw가 아니면 끝나지 않은 대전으로 본다.
- **[사실] 승패 판정:** winner 값은 a 또는 b이다. 전멸이 없으면 가장 긴 생존 드래곤을 가진 쪽이 이긴다.
  - 예: 587112는 점수가 30 대 106이었지만, 최장 드래곤이 12 대 10이라 A가 이겼다.
  - scoresA/B는 총길이로 보인다.
- **[사실] 시드:** 게임마다 16자리 16진 `seed`가 있다. 로컬 `unswbc run --seed`는 "리플레이가 보여 주는 형태의" 시드를 받는다(`tools/unswbc help run`).

### 2.5 제출
- **[사실] 규칙:**
  - 활성 제출은 1개이다. 새 버전은 빌드되자마자 활성이 된다.
  - 업로드는 시간당 12개까지이고, zip은 4 MB 이하, `bot.toml`은 zip 최상위에 있어야 한다.
  - 같은 코드를 다시 올려도 K를 새로 받지 않는다. 서버에 sourceHash로 드러나는데, g1-r1인 8497, 8633, 8684가 모두 a661dea238eb이다.
  - 12시간 안의 두 번째 새 봇은 빠른 K를 받지 못한다(`rules/elo.md`).
- **[사실] 활성 제출(2026-09-29T11:41Z):** 10365 g4-r4이다.
  - 2026-09-28T14:37Z에 업로드했다. kStart는 0, kFreshAt은 14:43Z이다.
  - 게임 전적은 75승 0무 94패이다.
  - 지도별 전적: Autarky 16-0, Trauma 11-2, Portals 9-9, Slithery Fight 8-7, Queen Of Spades 8-12, Default 6-9, Prisoners Dilemma 5-8, Schooltime 7-17, Devil 3-14, Trophy 2-16 (`snapshots/…/submissions.json`).
- **업로드 절차:** 이 도구에는 업로드 명령이 없다. 이전 배관 데몬(`UNSW/lineages/_daemon/plumber.js`)은 아래 순서로 올렸다. `tools/unswbc` 래퍼도 `submit` 인자를 공식 CLI에 그대로 넘긴다.
  1. 키를 자식 프로세스의 환경변수 `UNSWBC_KEY`로만 넘겨 `unswbc submit <dir> -n <이름> -d <설명>`을 실행한다.
  2. GET /submissions로 활성이 되었는지 확인한다.
  3. GET /submissions/:id/download로 받은 zip의 파일 해시를 로컬 스냅숏과 비교한다.

### 2.6 2026-09-29 조회 결과
원자료: `data/online/snapshots/20260929T1141Z/leaderboard-top30.json`, `team-583.json`

**리더보드 상위 20팀 (11:41Z).** 순위가 있는 팀은 571팀, 전체는 917팀이다. 랭크 스위치 열의 off는 랭크 신청을 받지 않는다는 뜻이다.

| 순위 | 팀 id | 이름 | 레이팅 | 랭크 스위치 | 비고 |
|---:|---:|---|---:|:-:|---|
| 1 | 306 | Cutlery | 2109 | off | |
| 2 | 70 | cheji bt | 2091 | on | |
| 3 | 20 | calc | 2071 | on | |
| 4 | 801 | 中国必须人能飞😡 | 2067 | off | |
| 5 | 91 | SSS | 2042 | off | |
| 6 | 46 | Sabotage-d | 2035 | on | |
| 7 | 264 | forgot to mention | 2029 | on | |
| 8 | 249 | Team SKKU | 2004 | on | |
| 9 | 213 | Sponge(Albert and Bob) | 1984 | on | |
| 10 | 952 | Cache me outside | 1978 | on | |
| 11 | 104 | Peanut Butter | 1976 | on | |
| 12 | 545 | dev test 1 :P | 1973 | on | DEV 팀(별도 허용량) |
| 13 | 27 | PPP | 1965 | on | |
| 14 | 507 | bread first search | 1958 | off | |
| 15 | 157 | zitian | 1954 | on | |
| 16 | 206 | Stockfish | 1951 | on | |
| 17 | 470 | 龙虎豹 | 1946 | off | |
| 18 | 566 | tungtung67 | 1942 | off | |
| 19 | 314 | 3.14159265 | 1937 | on | |
| 20 | 63 | Kamikaze | 1936 | on | |

- 상위 20팀은 모두 활성 봇이 있어서(모두 C++) 비랭크로 신청할 수 있다.
- 순위와 레이팅은 몇 분 사이에도 바뀐다. 같은 날 11:35Z에는 5위가 Sabotage-d(2044), 6위가 SSS(2042)였다.

**우리 팀 583 JJYA (11:41Z)**
- 순위 301 / 571, 레이팅 1460, 최고 1540이다.
- 게임 전적은 1533승 6무 2315패이다.
- 랭크 스위치는 켜져 있다. 우리 레이팅이 그대로여도 순위는 11:23Z 303위에서 11:41Z 301위로 움직였다.

**그 밖의 조회 결과**
- **티켓 잔량(추정):** 일반 60, DEV 60 (`tickets.json`).
- **현재 활성 제출:** 10365 g4-r4 (2.5 참고).
- **지도 풀(`maps.json`):** 4 Default, 7 Queen Of Spades, 9 Schooltime, 11 Trophy, 13 Devil, 15 Trauma, 17 Prisoners Dilemma, 19 Autarky, 20 Portals, 21 Slithery Fight.
  - 10개 모두 `maps/online-20260927/`의 같은 이름 파일과 내용이 같다(sha256 비교).

### 2.7 문서 변경
`rules/`의 2026-09-27 저장본과 2026-09-29 현행 문서가 다른 점이다.

| 항목 | 2026-09-27 저장본 | 2026-09-29 현행 |
|---|---|---|
| 자동 대전 | 2시간마다, 상대 최대 2팀 | 1시간마다(UTC 정각), 상대 1팀. 위아래 8계단 안에서 뽑는다 |
| DEV 팀 상대 신청 | 허용량에 세지 않는다 | 별도 허용량 60게임/시간 |
| 상대당 대기 대전 1개 규칙 | 있음 | 문장이 빠졌다 |
| ELO 문서 | 내용 차이 없음 | 내용 차이 없음 |

- 이 부분에서 `rules/api.md`와 `rules/game-format.md`는 옛 내용이다.
- 현행 원문은 `data/online/snapshots/20260929T1141Z/site/`에 있다.

## 3. 운영 제안 (검증 전)
1. **공개 대전 수집부터 한다.** 상위권에게 배우는 가장 싼 방법은 공개 대전을 모으는 것이다. 티켓이 들지 않는다.
   - `tools/collect_top.js`가 이미 5분마다 레이팅 1900 이상 팀끼리의 대전을 `data/top/`에 모은다.
   - 특정 대전이 필요하면 `team <id>`로 최근 대전 id를 찾아 `download <id>`로 받는다.
2. **우리 봇을 상위권과 붙일 때는 비랭크로 지도를 지정한다.** 지도를 고를 수 있어서 티켓 하나로 얻는 정보가 가장 많다.
   - 약한 지도를 골라 시험할 수 있다. 온라인 전적으로는 Trophy 2-16, Devil 3-14, Schooltime 7-17이 약하다.
   - 로컬 평가 G로는 portals 8.6, trauma 20.0, trophy 25.6이 낮다(`research/2026-09-29-heuristic-agenda.md`). 두 기준이 가리키는 약한 지도는 서로 다르다.
   - 60게임이면 한 시간에 예를 들어 `request --top 6 --maps all`(6팀 × 10지도)이나 `request --top 20 --maps trophy,devil,schooltime`(20팀 × 3지도)를 할 수 있다.
3. **DEV 팀 545를 활용한다.** "dev test 1 :P"(12위, 1973)는 별도 허용량을 쓴다. 일반 티켓을 쓰지 않고 상위권 수준의 상대와 붙을 수 있다. 다만 운영진의 시험 봇이다.
4. **랭크는 레이팅 손해가 작지만 제약이 있다.** Elo 식(`rules/elo.md`)에 따른 예상치이다.
   - 1460 대 2109이면 우리의 기대 게임 수는 0.12이다.
   - K=24(자리 잡은 봇)에서 0-5로 지면 약 −1점이고, 한 게임 이길 때마다 +4.8점이다.
   - 10365는 활성화 뒤 랭크 대전을 31번 치러(`battles-200.json`), K=24로 보인다.
   - 다만 지도가 무작위이고, 1·4·5·14·17·18위는 랭크 스위치가 꺼져 있다.
   - 레이팅이 목표가 아니면 비랭크가 낫다.
5. **신청할 때마다 활성 제출을 고정한다.** 신청은 항상 `--expect-active`로 한다. 배관 데몬이 새 릴리스를 자동으로 업로드하고 활성화할 수 있기 때문이다(5장 참고).

## 4. 불확실한 점
- 공식 잔량을 API로 읽는 방법이 없다. 사이트 로그인 세션 전용이라 추정만 할 수 있다.
- 허용량 창은 움직이는 60분 창으로 관측됐다(2.3). 게임마다 따로 돌아오는지는 모른다. 거절된 신청(409 등)이 허용량을 쓰는지도 문서에 없다. 사이트 신청 창은 남은 수를 넘기면 버튼이 꺼져서, 거절은 API에서만 생긴다.
- 팀원이 사이트에서 직접 신청한 대전도 같은 허용량을 쓴다(문서상 팀 공유).
  - 2026-09-28T14:42–14:44Z의 신청 3건(랭크: 457, 201 / 비랭크 10지도: 835)은 A=583인데, 이 저장소와 UNSW의 요청 기록에는 없다.
  - 사람이 사이트에서 신청한 것으로 보인다.
- "상대당 대기 대전 1개" 규칙이 서버에서 아직 유효한지 모른다.
- 랭크 신청에 `mapIds`를 넣으면 무시되는지 거절되는지 모른다. 도구는 이 조합을 막는다.
- `settings.unranked`의 뜻을 모른다.
  - true인 팀이 268개, false인 팀이 4개이고, false인 4팀은 모두 봇이 없다.
  - 사이트 코드의 신청 조건에는 쓰이지 않는다. 도구는 false인 팀을 "비랭크 거부로 보임"으로 표시하고 신청하지 않는다.
- "teamA가 신청 팀"이라는 규칙은 요청 기록과 대조한 7건에서만 확인했다. 자동 대전 8건에서는 모두 우리가 A였다.
- 아직 시작하지 않은(판정 서버 대기열에 있는) 대전의 모양은 관측하지 못했다. 관측한 것은 실행 중인 `live`뿐이다.
  - `wait.ms`가 예상 대기 시간인지, 경과 시간인지도 모른다.
  - 이전 도구는 `outcome == null`을 대기 중으로 보았다. 지금 서버는 진행 중인 대전에 `live`를 준다.
- 서버의 판정 엔진 버전을 모른다.
  - PyPI에는 unswbc 1.2.2가 나와 있고, 로컬 판정은 1.1.0이다.
  - 서버 `seed`로 로컬에서 같은 진주 배치를 재현할 수 있는지는 시험하지 않았다.
- 리플레이 저장소는 압축 전송을 쓰고, 받을 때 자동으로 풀려 저장된다.
  - 예: 587111은 전송 456,728바이트, 저장 1,564,717바이트이다.
  - 2026-09-27 파일과 같은 형식이고 해석기로 읽힌다.

## 5. 운영 위험
- **배관 데몬과 g5 러너:** 둘 다 이 저장소 밖이라 건드리지 않았다.
  - `UNSW/lineages/_daemon/plumber.js`(PID 5938, 2026-09-28T09:00Z 시작)가 아직 돈다. 이 데몬은 `unsw-arena-data/releases/`에 새 릴리스가 생기면 자동으로 업로드하고 활성화하도록 되어 있다.
  - unsw-arena g5 러너(`loop/runner.js run g5`, PID 81153)도 2026-09-29 11:42Z에 살아 있었다.
    - 이후 12:09Z에 w000008을 마치고 멈췄다. 자동 재시작(launchd) 작업도 지웠고 STOP 파일이 남아 있다. 루프가 멈춰 있는 동안에는 새 릴리스가 생기지 않는다.
  - 새 릴리스가 생기면 활성 제출이 예고 없이 바뀐다.
- **요청 한도 공유:** `collect_top`, 배관 데몬, `online.js`가 분당 120회를 나눠 쓴다. 다운로드를 크게 돌리면 429가 날 수 있다. 도구는 `Retry-After`만큼 기다렸다가 다시 시도한다.
- **키 재발급:** 새 키를 만들면 이전 키가 폐기되어, 이 키를 쓰는 다른 프로세스가 모두 멈춘다.
- **공개:** 우리 대전도 공개되어 누구나 리플레이를 볼 수 있다.

## 원자료
- `data/online/snapshots/20260929T1141Z/`: leaderboard-top30.json, team-583.json(가입 코드 제거), submissions.json, battles-200.json, maps.json, queue.json, tickets.json
- `data/online/snapshots/20260929T1141Z/site/`: 현행 문서 3쪽의 본문과 사이트 번들 두 조각(신청 창, 신청 조건). 키 없이 받았다.
- `data/online/r1-autoscrim/`, `data/online/top-sample/`: `download` 시험 결과
- `data/online/REMOTE-LOG.md`: 원격 작업 기록
- `rules/api.md`, `rules/game-format.md`, `rules/elo.md`, `rules/submitting.md`: 2026-09-27 저장본
- 이전 프로젝트(읽기 전용):
  - `UNSW/tools/online_cli.js`, `online_plan_ext.js`, `online_resend.js`, `scrim_report.js`, `v6_online_collect.repl.js`
  - `UNSW/lineages/_daemon/plumber.js`와 `log.md`, `state.json`
  - `UNSW/experiments/scrim-cycles/*/requests.json`: 48개, 신청 910건, 수락 902건, 2,706게임
