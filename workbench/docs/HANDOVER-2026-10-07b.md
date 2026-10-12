# 인계 문서 2026-10-07 저녁 (meow-main04 → meow-main05)

쓴 시각: 10-07 19:35 KST. 이 문서가 최신이다. 시간순 세부는 `docs/SESSION-STATE.md`(같은 세션이 하루 동안 갱신)에 있고,
둘이 다르면 이 문서를 따른다. 도구와 옛 규칙은 `HANDOVER-2026-10-06.md`, `HANDOVER-2026-10-07.md`가 아직 유효하다.
숫자와 상태는 쓴 시각 기준이니, 팀원에게 사실로 말하기 전에는 원본 파일을 다시 연다.

## 0. 새 세션이 할 일 (순서대로)
1. `cd unsw-swarm && python3 tools/team_watch.py`로 디코와 GitHub를 읽는다(마지막 글들을 실제로 읽는다).
2. 감시 둘을 백그라운드로 띄운다.
   - PR 감시: `python3 tools/team_watch.py --prs --wait 86400`
   - 조용한 세션 감시: `python3 tools/loop_watch.py 7200 300 quiet` (사람 차례·실패·멘션에만 깸. 깰 때마다 다시 띄운다)
3. 서버 봇과 루프를 확인한다: `tail -1 data/online/park/log.jsonl`, `~/meow-loop-out/status.json`, `runner.log`.
4. 이전 세션을 끈다: `claude stop 6b21c578` (meow-main04). 그 세션의 감시 두 개는 같이 죽는다.
5. jun에게 한국어로 짧게 보고한다. 루프 상황을 맨 위에 둔다.
6. 로컬 전용 사이드 프로젝트(4절)를 이어간다. Opus 진단 셋이 분리된 프로세스로 돌고 있다.

## 1. 사람
- 사용자는 jun(팀원에게 보이는 모든 글에서 "jun"). 팀 meow 1119. 예선 제출 마감 10-09 15:00 KST. 동결은 없다.
- Zhe(디코 900000000000000002, GitHub zhex0121, CEST = KST−7): 10-07 14:45 KST에 복귀. 15:06 이후 새 글 없음.
- QWQ(디코 900000000000000003, GitHub forrest-gan2005, AEDT = KST+2): 19:07 KST에 #38 수정을 답함.
- 태그는 각자의 활동 시간대에만(Zhe는 CEST, QWQ는 AEDT 기준). 정시 확인 스크립트가 이를 따른다.

## 2. 규칙 (오늘 바뀐 것 포함, 전부 jun의 말)
- 권한 분류기가 거부하면 그 자리에서 멈추고 jun에게 넘긴다. 줄이거나 쪼개 다시 보내는 것도 재시도다.
- `tools/park_watch.py`는 고치지 않는다. 라이브 봇의 직접 업로드와 활성화(`submit.js upload|activate`)는 jun의 손. 온라인 테스트 스크립트(`run-pair.sh`)가 하는 업로드와 복구는 해도 된다.
- 두 사본 전환(park_watch)은 자동. Zhe가 "switch the bot swap to manual"이라 하면 `--manual`로 재시작.
- 냥봇 답변은 지휘 세션에서 직접. Claude 서브에이전트는 쓰지 않는다(쓰려면 규모를 먼저 확인받는다).
- Zhe와 QWQ의 대화에 끼지 않는다. 봇이 멘션되거나 봇 글에 답글이 달렸을 때만 답한다. 분명한 요청은 되묻지 않고 하고 jun에게 사후 보고.
- 팀원에게 사실로 말하는 것은 파일을 열어 확인한 뒤에. 측정한 것과 읽어 낸 것을 나눠 적는다.
- 봇 글: 영어 소문자, 결론 먼저, 콜론 피하기, 비교는 작은 고정폭 표, 이모지로 시작(💬 답, 📢 공지), 답은 상대를 태그. 게시는 `python3 tools/meowbot.py --announce-file data/guide/px-<이름>.txt`(2000자 이하).
- 래더에서 나온 사실은 팀원 질문이나 카드와 관련 있으면 #meow에 공유. 단, 아래 로컬 전용 프로젝트의 전략과 분석은 올리지 않는다.
- 압축(/compact)은 하지 않는다. 컨텍스트가 커지면 jun이 "인계해"라고 할 때 새 세션으로 넘긴다.
- 보고는 한국어로 가볍고 짧게, 루프 상황을 맨 위에. 키와 토큰(`docs/api.txt`, `docs/discord.txt`)은 도구만 읽는다.
- battlecode 수정은 EnterWorktree 안에서, 커밋해서 브랜치로 push. main 병합과 push는 jun이 `!`로 한다.

## 3. 모델 분배 (jun 10-07 12:2x: "사고가 필요한거는 무조건 opus.")
| 일 | 누가 | 모델 |
|---|---|---|
| 지휘와 결정, 분석, 설계, 판정, 결과 해석, 구현 | Claude | Opus 5.5 high (xhigh는 루프 빌드만) |
| 상태 요약, 분류 글, 번역 | Claude | Sonnet medium |
| 스크립트 수정, 지표가 정해진 집계, 단순 확인 | Codex | gpt-6.1-sol만 (astra 금지) |
| 감시, 알림, 전환, 온라인 테스트 | 스크립트 | 모델 없음 |
- Codex: 브리프를 `data/codex/brief-<이름>.md`에 쓰고
  `tools/cx.sh data/codex/<이름>.log -m gpt-6.1-sol -c model_reasoning_effort=<low|medium|high> -s workspace-write -C <unsw-swarm> "Follow the brief in … exactly."`
  (네트워크가 필요하면 `-c sandbox_workspace_write.network_access=true`). 백그라운드로 띄우고, 프로세스가 완전히 끝난 뒤 결과 파일만 읽는다.
  Plus 계정이 한도에 닿으면 3시간 동안 juntegral 계정으로 넘어간다(cx.sh가 알아서 함).
- 따로 띄우는 Opus 분석: `LADDER_ROLE=analyst claude -p --model claude-opus-5-5 --effort high --permission-mode bypassPermissions --settings tools/ladder_settings.json --output-format stream-json --verbose < 브리프 > 로그.jsonl` (cwd는 unsw-swarm, 쓰기는 `data/analysis/ladder/` 아래만 허용됨).
- 토큰: 지휘 세션은 호출 수 × 컨텍스트 크기다. 긴 출력을 올리지 말고(cut, head), 스크립트 → 파일 → 요약만 읽는다.
  래더 러너는 19:26에 `--no-ai`로 재시작했다(수집·집계만). 분석을 다시 켜려면 옵션 없이 띄운다.

## 4. 로컬 전용 사이드 프로젝트 (jun 10-07 19:1x. 10-07 23:38에 팀에 공개)
jun의 말: "니 의견에 확실한 자신감을 가지고 혼자 멀리까지 나가봐. 가설을 한두개 내고 마는게 아니라, 이게 맞아. 이런식으로. …
두가지만 명심해. 적극적인 전략 수립과, 엄격한 고민." 래더 운용도 맡김. 온라인 테스트는 루프 큐의 카드는 버전당 한 번만, 나머지 여력은 이 작업에. 온라인 테스트를 못 했다고 멈추지 않는다.
- 공개 범위: 전략과 분석을 #meow에 올리지 않는다. "testing online now" 같은 운영 알림은 그대로 둔다. 팀원이 냥봇에게 직접 물으면 거짓말하지 않고 jun에게 넘긴다. AI 카드는 루프에 보이는 대로 둔다.
- **끝나는 조건**(jun 확인): 10-08 12:00 KST, 또는 그 전에 (1) 한 바퀴 완료(진단 셋 → 카드 → 빌드·행동 확인 → 통과한 것들의 묶음 온라인 90판 이상 한 번) (2) 통과한 카드가 하나도 없음 (3) ~~Opus 실행 10회 소진~~ 없앰(jun 10-07 19:4x: "횟수제한은 없애고 진행해") (4) 사고(라이브 봇 미복구, 주차 사본 점수 하락, 권한 거부) (5) 팀과 부딪힘(AI 카드가 팀원 카드를 밀어냄, 팀원이 멈추라 함, 팀원이 직접 물어 옴). 끝나면 jun에게만 보고 하나. 최종 제출은 팀이 정한다.
- **정한 전략**: (a) 무너지는 지도 유형 고치기 (b) 초반에 판을 넓게 쓸기 (c) 퀸 생존(QWQ의 #38). 스위치 하나씩 30판 테스트는 그만두고, 통과한 변경을 묶어서 90판 이상 돌린다. 새 사본으로 점수를 부풀리는 건 하지 않는다.
- 근거(main 485~500판, 내가 센 것. 두 번째 검산 없음): 지도 4개(Islands 0/23, Stripes 4/24, Australia 7/33, Tower Defense 8/31)가 패배의 41%. 끝까지 간 판은 우리 퀸만 생존 18/18, 상대만 0/58. 상대 2100+ 승률 28%, 2300+ 20%. 54위 1953, 35위 2050.
- **지금 도는 것**(Opus 실행 1~3회째, 횟수 제한 없음. 19:29 시작, 분리된 프로세스라 세션이 바뀌어도 돈다):
  | 브리프 (`data/analysis/ladder/dossier/`) | 결과 파일 | 로그 |
  |---|---|---|
  | `brief-diag-islands.md` | `diag-islands.md` | `run-diag-islands.jsonl` |
  | `brief-diag-australia.md` | `diag-australia.md` | `run-diag-australia.jsonl` |
  | `brief-sweep.md` (진주가 안 보일 때 되돌아가는 걸음, 진주 재생성 칸) | `sweep.md` | `run-sweep.jsonl` |
  끝났는지는 `pgrep -fl "claude -p --model claude-opus-5-5"`와 결과 파일로 본다. 입력은 Codex 집계 `dossier/summary.md`(87줄, 500판 검산 통과).
- **다음 단계**: 결과 셋을 읽는다 → 카드가 나오면 핵심 숫자와 코드 줄을 Codex(sol low)로 검산 → AI 카드로 올린다(아래 5절) → 첫 빌드의 살펴보기에서 스위치가 실제 판을 바꾸는지 본다(안 바꾸면 접는다) → 통과한 것들과 #49(LEADER_WAIT), #51을 한 봇으로 묶어 온라인 90판 이상(6절) → jun에게 보고.
- 오늘 이미 나온 것: `data/analysis/ladder/losses/`에 `summary.md`(패배 분류), `plan.md`(수정 계획), `counts/`, `split/`, `early-growth.md`(→ #51), `queen-ring.md`(봉인 퀸: 지금 닿는 건 3판쯤이라 접음). 블랙박스 실험은 `~/meow-redteam/report.md`.
- 래더: 19:1x에 팀 82(2138)에게 랭크전 1회 신청(게임 1335872~1335876). 결과는 `node tools/online.js battles --limit 8`로 확인.

- **20:04 갱신(jun)**: 이 프로젝트는 로컬 전용이다. 카드·GitHub·디코에 올리지 않고, 누가 물으면 jun에게 넘긴다. 행동 확인(스위치가 판을 바꾸는가)과 철학에 맞는지만 보고 계속 쌓는다. 멈추지 않는다. 자세한 건 SESSION-STATE와 메모리 `solo-project`. 위 "다음 단계"의 AI 카드 게시는 하지 않는다.

- **23:38 갱신(jun)**: jun이 #meow에 "공격적인 플레이 로직을 백그라운드에서 만들고 있다"고 직접 알림. 이제 팀에 공개됨(물으면 사실대로 답함). 작업 방식은 로컬 그대로. SESSION-STATE와 메모리 `solo-project` 참조.

## 5. 루프 (19:30 KST)
| 카드 | 상태 | 다음 |
|---|---|---|
| #50 revenge-hunt (AI) | 빌드 중, 19:30쯤 끝 | 살펴보기는 자동 통과 → 결과 테스트 |
| #38 queen-loop (QWQ) | QWQ의 19:07 수정으로 3차 빌드 대기 | 살펴보기는 QWQ가 답함 |
| #51 stall-release (AI) | 빌드 대기 | 자동 진행 |
| #47 update-map (Zhe) | 2차 빌드의 살펴보기 요청이 17:02에 올라감 | Zhe가 답함. 대신 답하지 않는다 |
| #49 leader-wait (AI) | 결과 나옴: 뒤집힌 짝 71 대 49, 행동 확인 불통과, 온라인 9/30 대 9.4/30 | 결정 글을 달지 않았다. 묶음 후보로 둔다 |
| #48 queen-sacrifice (Zhe) | 결과: 400쌍 중 391쌍이 같은 판 | Zhe 결정 |
| #43 idle-exit (Zhe) | 결과 나와 있음 | Zhe 결정 |
- 큐는 사람 카드가 AI 카드보다 먼저다(fair_queue). 짧은 단계가 긴 결과 테스트보다 먼저 돈다.
- AI 카드 만들기: 제목 `[Idea] …`, 라벨 `by:ai`, `status:ready`, `wf:3`, `name:<슬러그>`(없으면 `gh label create`). 본문은 요약 세 줄(What we tried / Did it work / Who decides now) + `### Idea by`(AI) + `### Area`, `### Claim`, `### Evidence`, `### Expected signal`, `### What would show it's wrong`. 본보기는 이슈 #49, #50, #51.
- by:zhe 카드에서 루프가 답으로 읽는 것: Zhe·QWQ 본인 GitHub 댓글, 또는 `Answer from Zhe|QWQ|jun: …`로 시작하는 댓글. by:qwq 카드는 jun 로그인의 일반 댓글도 답으로 읽으니 #38에는 댓글을 달지 않는다.
- 팀원이 온라인이면 그의 카드에 대신 답하지 않는다. 오프라인인 동안에는 jun과 QWQ, 또는 jun의 허락 아래 냥봇이 살펴보기에 대신 답해 1차 테스트까지 돌린다(Zhe에게 14:4x에 알림). 규칙이 깨진 빌드는 "통과"가 아니라 "수정".
- 러너: pid 75232(10-07 11:01 재시작, main 5480a65 코드). 재시작은 데몬 pid만 kill하고 같은 인자로 다시 띄운다(`pkill -f runner.py` 금지, 방법은 SESSION-STATE "러너 재시작").
- 루프 강도: 빌드만 xhigh, 나머지 high(main 5480a65). 동결 시각 상수는 10-09 15:00으로 바꿈.

## 6. 온라인 테스트
- `data/online/smoke/run-pair.sh <label> <botdir> "<ref>" <상대>`: 라이브 봇 15판(`BASELINE=1`), 테스트 봇 15판, 끝나면 복구. 실행기 본보기는 `at-lw49.sh`(상대 둘을 차례로, `SMOKE_RESTORE_BEST=0`으로 원래 켜져 있던 18570을 그대로 복구).
- 같은 테스트 봇을 두 번 올리면 park_watch가 둘을 같은 코드의 두 사본으로 잡는다. 두 번째는 주석 한 줄이라도 다르게 올린다.
- 일반 팀 허용량은 시간당 60판(랭크 판 포함). 한 번에 테스트 하나. 상대는 Big Bobs Bots(946), test4(19), WeHaveQuizzes(87). dev1(545)은 쓰지 않는다.
- 테스트 봇 만들기: 카드 커밋의 `mybot2/`를 `data/online/smoke/<label>-bot/`에 뽑고 토글을 켠 뒤 `c++ -std=c++20 -O2`로 컴파일 확인. 묶음은 카드들의 변경을 한 main.cpp에 합쳐야 한다(카드 워크트리 `~/meow-cards/card-N`).
- 오늘 결과(30판씩): #47 1차 4 대 10(나쁨), 퀸 양보 스위치 8 대 9.5, #49 9 대 9.4. 30판으로는 6승 차이 이상만 잡힌다.
- 서버(19:2x): v47(18570) 활성 1953, v44(18504) 주차 1964.

## 7. 데몬 (하나씩만)
meowbot, runner, decision_nudge, park_watch(자동), ladder_hourly(`--no-ai`). 재시작 명령은 `HANDOVER-2026-10-07.md` 7절과 SESSION-STATE.
새 세션이 끄는 것은 이전 세션(6b21c578)뿐이다. 데몬은 건드리지 않는다.

## 8. jun의 손이 필요한 것
- unsw-swarm push: `! cd "../unsw-swarm" && git push` (로컬 커밋이 여럿 쌓여 있다).
- battlecode main push와 병합, 라이브 업로드와 활성화.
- 팀에 무엇을 언제 가져갈지(로컬 전용 프로젝트의 결과 포함).

## 9. 알아 둘 함정
- Codex가 `last.txt`를 쓴 뒤에도 요약을 고칠 수 있다. 프로세스가 끝난 걸 확인하고 읽는다(오늘 한 번 당함, 숫자는 안 바뀌었음).
- 묶은 비교는 구성 차이를 먼저 본다(오늘 "같은 지도 안에서 갈린다"고 잘못 말했다가 정정함: 시작 길이가 다른 지도들을 합친 비교였다).
- 로컬 판은 상대가 우리 기준 봇이라 래더의 상황(초반에 눌리는 판)을 못 만든다. #49가 그랬다.
- 시각은 `date`로 확인하고 쓴다.
