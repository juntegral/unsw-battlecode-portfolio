# UNSW Battlecode 2026: 엔지니어링 포트폴리오

English: [README.md](README.md)

UNSW Battlecode 2026에서 내가 한 작업 전체를 모은 저장소다. 이 대회는 팀마다 자율 에이전트("드래곤", 가장자리가 이어진
격자 위의 뱀 모양 유닛)를 만들어 공개 래더에서 겨루고, 마지막에는 처음 보는 지도에서 토너먼트를 치르는 2주짜리
대회다.

나는 봇의 중반 탐색·분열 엔진 작업에 참여했고, 그 주변의 엔지니어링을 만들었다. 테스트 환경, 온라인 테스트 도구,
리플레이 분석, 세 시간대에 흩어진 3인 팀을 위한 Discord·GitHub 협업 환경, 그리고 사람이 자는 동안 AI 코딩 에이전트가
아이디어를 만들고 시험하게 하는 루프를 설계하고 운영했다. 소스, 설계 문서, 매일의 운영 기록, 무엇이 통했고 무엇이
실패했는지를 정리한 일곱 장짜리 회고가 여기 다 들어 있다.

팀 저장소를 옮겨 놓은 것이 아니라 개인 포트폴리오다. 팀원과 함께 만든 것, 내 지시로 AI 에이전트가 만든 것은
그렇게 적어 두었다. 회고 일곱 장도 별개의 AI 작성자들이 프로젝트 기록을 바탕으로 썼고, 리드 AI 세션이 확인할 수 있는
부분을 확인했다([회고 00](writeup/00-README.md)).

## 여기서 시작 (3분)

**AI를 쓰는 법, 규칙 여섯 개**([docs/HOW-I-USE-AI.ko.md](docs/HOW-I-USE-AI.ko.md)). 규칙마다 원인 사고와 대회 끝까지
유지됐는지가 적혀 있다. 유지: 2번과 4번. 일부 유지: 1, 3, 5, 6번.

1. AI 보고는 그 안의 숫자 하나를 다시 센 뒤에만 쓴다.
2. 바뀌면 안 되는 빌드는 해시로 증명한다: 스위치를 전부 끄면 이전 바이너리가 나온다.
3. 카드 루프의 AI는 push, 병합, 업로드, 경기 신청을 할 수 없다(이 제한은 루프에 해당하고 리드 세션에는 해당하지 않는다).
4. 권한이 거부되면 멈추고 실행할 한 줄만 넘긴다.
5. 팀원 아이디어가 먼저다.
6. 병렬이나 반복 AI 작업은 시작하기 전에 상한을 정한다.

**통제를 어디서 풀었고 무엇을 치렀나.** 마지막 이틀에 리드 AI 세션에 넓은 권한을 주었다. 해로운 스위치 셋이 3.3, 4.6,
13.0시간 라이브였고, 마지막 세 버전은 온라인 경기 없이 올라갔다: [docs/LAST-TWO-DAYS.ko.md](docs/LAST-TWO-DAYS.ko.md).

**10분 코스**

1. [확신에 찬 AI 보고가 틀렸던 사례 12건과 그 뒤에 추가한 확인](writeup/05-ai-workforce.md#3-verification-confident-reports-that-were-wrong) (회고 05, 3절)
2. [AI 세션을 인력처럼 운영하기](docs/case-studies/05-ai-workforce.md) (사례, 영어)
3. [1인 계열을 끝낸 점검 문서](first-bot/research/CHECKPOINT-2026-10-01.md)
4. [가장 큰 비용](writeup/01-playbook.md#what-cost-us-most) (회고 01, "What cost us most")
5. [마지막 이틀](docs/LAST-TWO-DAYS.ko.md)

## 한눈에 보기

| | |
|---|---|
| 대회 | UNSW Battlecode 2026, 2026-09-25 ~ 2026-10-10 |
| 팀 | 10-02까지 1인 팀(583), 이후 Zhe, QWQ와 함께 팀 1119 "meow" |
| 내 담당 | 중반 탐색·분열 엔진 작업에 참여. 그 주변의 인프라, 도구, 테스트·분석 파이프라인, AI 세션 운영, 최종 봇 프로필의 대부분을 만든 스위치 프로젝트 |
| 최종 봇 | `one21`: C++ 파일 하나(8,657줄)와 스위치 값 49개로 된 프로필 |
| 래더 | 팀 결성 때 1800(32위), 최고 2202(23위), 마지막 날 14:59에 2092(41위), 최종 38위와 시드 36번은 [팀 README](https://github.com/forrest-gan2005/battlecode/blob/main/README.md) |
| 결과 | 토너먼트 진출, 10-10 64강에서 탈락([팀 README](https://github.com/forrest-gan2005/battlecode/blob/main/README.md)) |
| 규모 | 업로드 84회(시험용 사본 포함), 마지막 16시간에 라이브 버전 21개(비용도 있었다: [회고 05 8.3절](writeup/05-ai-workforce.md#83-things-to-avoid)), 로컬 경기 약 9,000판, 최종 계열 온라인 경기 약 1,080판 수집 |

수치는 회고의 타임라인 장에서 가져왔고, 그 장에 수치마다 출처가 있다.

## 만든 것

### 1. 세 시간대 팀을 위한 협업 환경

최대 9시간 차이 나는 세 사람이 봇 하나를 같이 고쳤다. 담당자가 자리에 없어도 일이 진행되도록 팀 Discord 채널과 GitHub
저장소를 연결했다.

- **meowbot** ([`workbench/tools/meowbot.py`](workbench/tools/meowbot.py), 2,082줄, 그리고
  [`meow_chat.py`](workbench/tools/meow_chat.py), [`meow_ui.py`](workbench/tools/meow_ui.py),
  [`meow_guard.py`](workbench/tools/meow_guard.py)): PR과 아이디어 카드를 채널에 올리고, 슬래시 명령을 구조화된 GitHub
  이슈로 바꾸고, 보드와 루프 상태를 보여 주고, 팀원만 누를 수 있는 승인·보류 버튼으로 배포 후보를 제시하고, 스레드에서
  읽기 전용 AI 세션으로 질문에 답하는 Discord 봇.
- **모델 없이 도는 감시 스크립트** ([`team_watch.py`](workbench/tools/team_watch.py),
  [`discord_sync.py`](workbench/tools/discord_sync.py), [`mention_watch.py`](workbench/tools/mention_watch.py),
  [`loop_watch.py`](workbench/tools/loop_watch.py)): 채널을 미러링하고 GitHub를 폴링하다가, 생각이 필요한 일이 생겼을
  때만 세션을 깨운다.
- **오프라인 테스트**: 가짜 Discord·GitHub·모델 호출로 도는 테스트 파일 38개, 테스트 함수 431개.

사례: [docs/case-studies/01-collaboration-environment.md](docs/case-studies/01-collaboration-environment.md)

### 2. 카드 루프: GitHub 라벨 상태 기계로 아이디어를 만들고 시험하기

아이디어 하나가 GitHub 이슈 하나다. `status:*` 라벨 하나가 상태의 전부다. 실행기가 라벨을 폴링하다가 카드 상태가 AI
작업을 요구할 때만 AI를 부른다. 작성자에게 질문하고, 기본값이 꺼진 스위치 뒤에 구현하고, 스위치를 끄면 기존 프로그램과
같다는 것을 증명하고, 작성자가 고른 리플레이를 보고, 결과 테스트를 돌리고, 판정을 쓰고, 후보 PR을 연다. 승인은 카드 작성자가
하고, 루프의 AI는 업로드할 수 없다(`guard.py`가 막는다). 이 제한은 루프에만 해당한다: 마지막 밤의 21개 버전은 리드
Claude 세션이 위임을 받아 올렸다([docs/LAST-TWO-DAYS.ko.md](docs/LAST-TWO-DAYS.ko.md)).

- 명세: [`card-loop/docs/LOOP.md`](card-loop/docs/LOOP.md)(팀원을 위한 중국어판 포함),
  [`WORKFLOW.md`](card-loop/docs/WORKFLOW.md)
- 실행기와 작업 관리자: [`card-loop/work/loop/runner.py`](card-loop/work/loop/runner.py)(1,051줄),
  [`jobs.py`](card-loop/work/loop/jobs.py), [`guard.py`](card-loop/work/loop/guard.py),
  단계별 프롬프트 [`prompts/`](card-loop/work/loop/prompts), 테스트 파일 13개
- 작성자 간 공정 대기열: [`card-loop/work/fair_queue.py`](card-loop/work/fair_queue.py)

사례: [docs/case-studies/02-card-loop.md](docs/case-studies/02-card-loop.md)

### 3. 배포 규율: 기본값이 꺼진 스위치, 동일함을 해시로 증명

새 동작은 전부 기본값이 꺼진 컴파일 상수 뒤에 두었고, 전부 끈 빌드는 이전 프로그램과 바이트 단위로 같아야 했다. 이
규율 덕분에 16시간 동안 라이브 버전 21개를 올리면서 크래시도, 시간 초과도, 지금 무엇이 라이브인지에 대한 혼란도
없었다. 해시가 증명하는 것은 동일함이지 개선이 아니다. 15판짜리 온라인 세트로는 두 버전을 구분하지 못했고, 해로운
스위치 셋이 3.3, 4.6, 13.0시간 라이브였다([회고 05 3절](writeup/05-ai-workforce.md#3-verification-confident-reports-that-were-wrong),
[회고 06 3절](writeup/06-timeline.md)).

- 변형 빌더: [`local-rig/solo/tools/mkbots.py`](local-rig/solo/tools/mkbots.py)
- 계획 출력, `--confirm`, `--expect-active`가 있는 업로드: [`workbench/tools/submit.js`](workbench/tools/submit.js),
  [`smoke.py`](workbench/tools/smoke.py)
- 최종 봇과 프로필: [`final-bot/`](final-bot)

사례: [docs/case-studies/03-switches-proven-by-hash.md](docs/case-studies/03-switches-proven-by-hash.md)

### 4. 측정: 로컬 환경, 온라인 도구, 리플레이 분석

- **로컬 환경** ([`local-rig/`](local-rig)): 기기 전체 동시 실행 제한이 있는 결정적 경기 실행기, 배치 실행기, 처음
  보는 지도 대비용 생성 지도 묶음.
- **온라인 도구** ([`workbench/tools/smoke.py`](workbench/tools/smoke.py),
  [`pair_report.py`](workbench/tools/pair_report.py), [`park_watch.py`](workbench/tools/park_watch.py),
  [`weak_watch.py`](workbench/tools/weak_watch.py), [`fair_queue.py`](workbench/tools/fair_queue.py)): 지정한 상대와의
  짝 테스트, 라이브 봇 사본 두 개 사이의 레이팅 래칫, 레이팅이 훨씬 낮은 팀에게 졌을 때 분석가를 붙이는 경보.
- **래더 연구** ([`workbench/tools/ladder_*.py`](workbench/tools),
  [`workbench/data/analysis/ladder/`](workbench/data/analysis/ladder)): 매시간 수집기, 리플레이에서 실제 게임 상태를
  복원하는 판독기, 전체 경기를 대상으로 한 패배 원인 분류.
- **지도 생성기** ([`workbench/tools/mapgen/`](workbench/tools/mapgen)): 보류 세트 테스트용 지도 묶음.

사례: [docs/case-studies/04-measurement-and-noise.md](docs/case-studies/04-measurement-and-noise.md)

### 5. AI 세션을 인력처럼 운영하기

이 저장소의 코드와 분석 대부분은 내가 지시한 AI 코딩 에이전트(Claude Code 세션, Codex 작업자)가 썼다. 그 운영을
설계하는 것이 작업의 큰 부분이었다. 누가 결정하고, 누가 생각하고, 누가 세는지, 지시문에는 무엇이 들어가야 하는지,
보고는 어떻게 검증하는지, 문맥이 너무 커진 세션은 다음 세션에 어떻게 넘기는지를 정했다.

- 여섯 번 이어진 리드 세션 사이의 인계: [`workbench/docs/`](workbench/docs) (`HANDOVER-*.md`, `SESSION-STATE.md`,
  `PROMISES.md`, 대부분 한국어)
- 규칙 하나당 파일 하나, 규칙마다 그 원인이 된 사건을 적은 상시 규칙:
  [`workbench/archive/claude-memory/`](workbench/archive/claude-memory), 정리한
  [색인](workbench/archive/claude-memory/INDEX.md)
- 분석가 지시문과 보고서: [`workbench/data/codex/astra/`](workbench/data/codex/astra),
  [`workbench/archive/final-session-agent-reports/`](workbench/archive/final-session-agent-reports)
- 확신에 찬 보고가 틀렸던 사례 12건과 그 뒤에 추가한 확인 절차: [회고 05장](writeup/05-ai-workforce.md)

사례: [docs/case-studies/05-ai-workforce.md](docs/case-studies/05-ai-workforce.md)

### 6. 봇

- **첫 봇** ([`first-bot/`](first-bot)): 1인 팀 시기의 휴리스틱 C++ 봇과 연구 노트, 그 계열을 끝낸 점검 문서
  ([`CHECKPOINT-2026-10-01.md`](first-bot/research/CHECKPOINT-2026-10-01.md)).
- **계통 루프** ([`lineage-loop/`](lineage-loop)): 봇 계통별로 웨이브마다 AI 세션 하나를 돌리던 초기의 "끝없이 개선"
  루프와 그 런타임 테스트.
- **swarm 계열** ([`workbench/versions/`](workbench/versions), v0 ~ v1.8): 시스템 단위로 다시 설계한 봇. 버전마다
  가설, 바꾼 것, 사전 등록 기준, 판정을 기록했다. 설계 다이어그램은 [`workbench/docs/arch/`](workbench/docs/arch).
- **최종 봇** ([`final-bot/`](final-bot)): 팀이 제출한 봇. 기반 봇은 QWQ가 썼고, 그것을 `one21`로 만든 스위치와
  프로필은 대부분 내 스위치 프로젝트에서 나왔다.

## 회고

[`writeup/`](writeup)에 대회가 끝난 날 쓴 일곱 장이 있다(영어). 측정한 것과 해석을 구분하고, 장마다 확인하지 못한
것으로 끝난다.

| 장 | 다루는 질문 |
|---|---|
| [00 개요](writeup/00-README.md) | 대회 요약, 교훈 아홉 가지, 기록의 빈 곳 |
| [01 플레이북](writeup/01-playbook.md) | 무엇을 만들지 정하는 법, 변경을 시험하는 법, 배포, 처음 보는 지도 대비 |
| [02 게임 지식](writeup/02-game-knowledge.md) | 승부를 가른 것, 퀸이 죽는 방식, 상위 팀이 한 것 |
| [03 봇 설계](writeup/03-bot-design.md) | 최종 봇이 한 턴을 결정하는 방식, 스위치마다의 근거 |
| [04 도구](writeup/04-tools.md) | 남길 만한 스크립트 전부, 명령과 함정 |
| [05 AI 인력 운영](writeup/05-ai-workforce.md) | AI 세션 지휘: 통한 것, 실패한 것, 비용 |
| [06 타임라인](writeup/06-timeline.md) | 날짜별, 마지막 밤은 시간별, 레이팅 추이 |

## 잘못된 것

회고는 성공담으로 쓰지 않았다. 플레이북과 마지막 이틀 문서에서 뽑은 짧은 목록이다.

1. 처음 보는 유형의 지도에서 체계적으로 시험한 것이 마감 13시간 전이었다. 그 시험에서 당시 라이브 버전은 익숙한
   지도에서는 이기면서 새 지도에서는 우리 옛 봇에게 졌다.
2. 마지막 밤 8시간 동안 버전을 15판짜리 온라인 세트로 판정했다. 같은 봇이 같은 상대에게 15판 중 8승을 했다가 두 시간
   뒤에는 4승을 했다.
3. 해로운 스위치 두 개가 3시간에서 4시간 반 동안 라이브였다. 버전을 지도별로가 아니라 승수로 비교했기 때문이다.
4. 가장 큰 패배 유형인 초반 150라운드의 유닛 수 열세는 끝내 고치지 못했다.
5. 시드를 올리려고 마지막 한 시간에 신청한 랭크 경기로 레이팅이 오히려 내려갔다.
6. 마지막 이틀에 리드 AI 세션에 넓은 권한을 주었다. 해로운 스위치 셋이 3.3, 4.6, 13.0시간 라이브였고, 마지막 세 버전은
   온라인 경기 없이 올라갔다([docs/LAST-TWO-DAYS.ko.md](docs/LAST-TWO-DAYS.ko.md)).

항목마다 수치가 있는 절이 [01장](writeup/01-playbook.md)에 있다.

## 저장소 지도

| 폴더 | 출처 | 내용 |
|---|---|---|
| [`docs/`](docs) | 이 포트폴리오를 위해 작성 | 구조 개요, 사례 다섯 편, [AI를 쓰는 법](docs/HOW-I-USE-AI.ko.md), [마지막 이틀](docs/LAST-TWO-DAYS.ko.md), [공개 뒤 정정 기록](docs/CHANGELOG.md) |
| [`writeup/`](writeup) | `unsw-swarm/docs/retro` | 일곱 장짜리 회고 |
| [`workbench/`](workbench) | 비공개 저장소 `unsw-swarm` (커밋 383개) | 주 작업장: 도구(meowbot, 온라인 도구, 래더 연구, 지도 생성기), swarm 봇 계열, 실험, 분석가 작업, 운영 기록 |
| [`card-loop/`](card-loop) | 팀 저장소([공개](https://github.com/forrest-gan2005/battlecode)) 중 내 파일 | 카드 루프 실행기, 프롬프트, 테스트, 루프 명세, 확인 스크립트 |
| [`local-rig/`](local-rig) | 비공개 저장소 `meow-redteam` | 로컬 경기 환경, 생성 지도, 변형 빌더 |
| [`final-bot/`](final-bot) | 팀 저장소 최종 브랜치 | `one21` 소스, 프로필, 업로드 소스를 만드는 스크립트 |
| [`lineage-loop/`](lineage-loop) | 비공개 저장소 `unsw-battlecode-2026` | 초기 계통 루프와 봇 |
| [`first-bot/`](first-bot) | 비공개 저장소 `unsw-heuristic` (커밋 133개) | 첫 봇, 연구 노트, 실험 스크립트 |

코드의 알려진 문제와 없는 프로젝트 파일(라이선스, 의존성 목록, CI): [docs/KNOWN-ISSUES.md](docs/KNOWN-ISSUES.md)(영어).

처음 읽을 때 필요 없는 것: `workbench/data/`(4,777개 파일)와 `workbench/exp/`(2,568개 파일)의 분석가 스크립트, 지시문,
시간별 보고서, 그리고 중복 파일(추적 파일 9,888개 중 1,090개는 다른 파일과 내용이 완전히 같은 사본이다. 내용 해시로 센
값).

폴더마다 원래 저장소의 구조를 그대로 두었다. 그래서 회고에 인용된 경로가 그대로 통한다. 회고의 `S/...`는 여기의
`workbench/...`, `R/...`는 `local-rig/...`, `B/...`는 팀 저장소다(내 몫은 `card-loop/`, 최종 봇은 `final-bot/`).

## 여기 없는 것

- 키와 토큰. 어느 저장소에도 넣은 적이 없고, 도구가 버전 관리 밖의 파일에서 읽었다.
- 팀의 비공개 대화와 팀원 개인에 관한 내용. 인용한 대목은 지우거나 풀어 썼고, Discord ID는 자리표시 값으로 바꿨다.
- 팀원의 코드. 최종 봇만 팀 산출물로 싣고 [`final-bot/README.md`](final-bot/README.md)에 저작 관계를 적었다.
- 주최 측의 엔진, 스타터 코드, 규칙 원문, 공식 지도.
- 리플레이, 로그, 대량 실험 출력(수십 GB). 스크립트, 보고서, 작은 표는 남겼다.
- 실험 폴더 안의 봇 소스 중간 사본. 버전으로 관리한 계열은 남겼다.

## 저작 관계

- 팀은 나(jun), Zhe([zhex0121](https://github.com/zhex0121)), QWQ([forrest-gan2005](https://github.com/forrest-gan2005))
  였다. QWQ가 기반 봇을 쓰고 팀 저장소를 관리했다. Zhe는 전략 판단과 아이디어 카드의 대부분을 냈고, 그의 포트폴리오는
  [zhex0121/unsw-battlecode-portfolio](https://github.com/zhex0121/unsw-battlecode-portfolio)에 있다.
- `card-loop/`의 파일은 팀 저장소에서 모든 커밋이 내 계정으로 올라간 파일이다. 여기서 "내 것"에는 그 계정으로 일한 AI
  도구가 포함된다. 팀 저장소 이력에서 이 파일들을 건드린 커밋 67개 중 61개에 `Co-Authored-By: Claude` 표기가 있고, 나머지
  6개는 러너가 스스로 만드는 "Prepare candidate" 커밋이다([`runner.py`](card-loop/work/loop/runner.py) 843행. 85행의
  주석은 도구가 "jun의 로그인으로 게시한다"고 적었다).
- 항목별로 누가 무엇을 만들었는지와 커밋·세션 근거: [docs/AUTHORSHIP.md](docs/AUTHORSHIP.md)(영어).
- 이 저장소의 코드, 분석, 글의 상당 부분은 내 지시문에 따라 AI 에이전트가 만들었다. 무엇을 무엇으로 확인했는지는
  [회고 05 3절](writeup/05-ai-workforce.md#3-verification-confident-reports-that-were-wrong)에 있다: 스크립트(바이너리 해시
  동일성, 서버 사본과 업로드 폴더 비교, 리플레이에서 읽은 봇 id), 핵심 숫자 하나를 다시 세는 리드 AI 세션, 마지막 후보를
  깨뜨려 보라고 지시받은 두 번째 AI 세션, 팀원의 지적. 시스템 설계, 방향, 그 확인 절차의 구성, 결정은 내 작업이고,
  회고에 적힌 실수도 내 것이다.
- 이 저장소의 이력은 공개 시점부터 시작한다. 전체 이력이 있는 내 원래 저장소들은 비공개로 남아 있다. 팀 저장소는 공개다
  ([forrest-gan2005/battlecode](https://github.com/forrest-gan2005/battlecode)).
