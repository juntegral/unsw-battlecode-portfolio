# /task 구현 보고

작성: 2026-10-05 21:41:34 KST. `data/codex/brief-task-cmd.md` 범위로 작업했다. 커밋, 봇 또는 기존 프로세스의 시작·중지·재시작, Discord 게시, 게임 서버 호출은 하지 않았다. `docs/api.txt`와 `docs/discord.txt`는 읽지 않았다. 기존 `docs/PROMISES.md` 수정은 건드리지 않았다.

## 변경한 곳

- `tools/tasks.py`: `collect(now, state=None)`가 세 사람별 `todo`, `yours`, `parked`와 공유 `anyone` 블록을 만든다. 대기 항목에는 카드/PR 참조, 행동, 답하는 방법, 기준 시각, 대기 시간, snooze 만료 시각이 들어간다. `render(data, who=None, now=None, caller=None)`가 담당자 필터, 호출자 우선 순서, CEST/AEDT 현지 시각, 정렬한 코드 블록을 적용한다. 가장 긴 목록의 뒤를 `… and N more`로 줄여 1,900자 미만을 유지한다.
- `tools/meowbot.py`: 모듈 설명의 명령 목록에 `/task` 한 줄을 추가했다. `board_state()`에 `updatedAt`을 읽는 필드만 추가했다. `reply_tasks()`와 `/task` 등록을 추가했다. `who` 선택지는 `me`, `준싱`, `Zhe`, `QWQ`, `all`이며 기본은 `all`이다. 기본 응답은 호출자에게만 보이고, `share=true`는 현재 채널에 보인다. 모든 응답에 `AllowedMentions.none()`을 적용한다. 팀원 확인 후 읽기 전용 수집을 별도 스레드에서 수행하며 모델은 호출하지 않는다. `--preview-tasks [--who NAME]`는 텍스트를 출력하고 봇 실행 전에 종료한다.
- `tools/test_tasks.py`: 28개 오프라인 테스트를 추가했다. 네 대기 상태, Zhe만 필요한 replay check, snooze, 후보 OK 조건과 커밋 변경, 수동 진행/대기열/parked/ETA, 오래된 일반 PR, 기록된 미제출 merge, 필터/호출자 순서/현지 시각/빈 사람/문자 제한, CLI 종료, 팀원 제한과 공유 시 mention 비활성화를 검증한다. 새 테스트의 GitHub 호출과 데이터 파일 읽기는 모두 stub이다.

## 후보 OK를 읽는 방법

실행 중에는 봇이 이미 가진 `st`를 전달한다. CLI에서는 기존 `load_state()`가 `data/meowbot/state.json`을 읽는다. `candidates`의 `manifest.issues`, `author_labels`, `oks`, `status`, `head_sha`를 열린 PR 목록의 `headRefOid`와 대조한다. 현재 head의 `pending`/`hold` 후보만 표시하고, 닫힌 PR, stale/완료 후보 및 옛 head의 표는 사용하지 않는다. `oks`는 Discord 회원 ID 문자열이며 `MEMBERS`로 사람 이름을 얻는다.

인간 아이디어는 작성자 집합 중 한 사람의 OK와 작성자가 아닌 한 사람의 OK가 필요하다. 아직 충족하지 않은 역할을 줄 수 있는 사람들에게 항목을 표시하며, 이미 OK한 사람에게 추가 OK를 요구하지 않는다. AI-only는 회원 한 명, 작성자 불명은 서로 다른 회원 두 명으로 기존 `approval_ready()`의 조건을 따른다. 필요한 OK가 모두 있으면 기존 투표자에게 OK → Confirm으로 merge를 확정하는 행동을 표시한다. 카드와 후보 PR이 같은 요구를 중복 표시하지 않도록 연결 카드 번호를 처리한다.

캐시된 작성자 정보가 없을 때는 OK 버튼과 같은 `candidate_authors()`를 사용한다. 아직 현재 head의 후보 기록이 없으면 기존 읽기 전용 `pr_candidates()`와 `candidate_authors()`로 manifest와 작성자를 읽고, 이전 head의 OK를 가져오지 않는다. 이 경우에는 PR 링크와 후보 게시물을 기다리라는 안내를 표시한다. 수집 중 상태, snooze, OK를 수정하지 않는다.

`main` 관련 줄은 `active_submission.commit`과 기존 `pending_merges()` 기록으로 미제출 merge가 확인될 때만 표시한다. 최신 서버 상태를 알아보는 호출은 추가하지 않았다.

## 오늘 보드 fixture: all (721자)

GitHub 연결이 막혀 brief에 지정된 보드로 `collect()`와 `render()`를 실행했다. 준싱은 빈 상태, Zhe는 #39 needs-info / #31·#36 needs-look / #16 parked, QWQ는 #38·#33·#22 수동 진행이다. 출력 시각은 재현용 2026-10-05 21:27 KST이며, 대기 시간 30m/2h/1h30m는 테스트에 넣은 예시 `updatedAt`으로 계산한 값이다. 실제 보드의 대기 시간을 측정한 결과는 아니다. fixture에는 후보/일반 PR, ETA, 활성 제출 기록을 넣지 않았으므로 anyone 블록은 없다.

````text
📋 tasks · 21:27 KST
**준싱** · 0 waiting
nothing waiting
**Zhe** (14:27 there) · 3 waiting
```
#31 queen-hunt      check 2 to 3 replays · /answer card:31 text:…                          2h 0m
#36 queen-dead-end  check 2 to 3 replays · /answer card:36 text:…                          1h 30m
#39 queen-safety    answer the loop's questions before the build · /answer card:39 text:…  30m
```
parked: #16 safezone-v2 · queue it with status:ready or close it
**QWQ** (23:27 there) · 0 waiting
yours, nothing to do now: #22 late-feed (in progress by hand); #33 blind-circling (in progress by hand); #38 queen-loop (in progress by hand)
reply to a card with /answer card:N text:… · "/meow N still deciding" quiets the hourly check
````

## 오늘 보드 fixture: who=Zhe (510자)

````text
📋 tasks · 21:27 KST
**Zhe** (14:27 there) · 3 waiting
```
#31 queen-hunt      check 2 to 3 replays · /answer card:31 text:…                          2h 0m
#36 queen-dead-end  check 2 to 3 replays · /answer card:36 text:…                          1h 30m
#39 queen-safety    answer the loop's questions before the build · /answer card:39 text:…  30m
```
parked: #16 safezone-v2 · queue it with status:ready or close it
reply to a card with /answer card:N text:… · "/meow N still deciding" quiets the hourly check
````

## 검증

`tools/` 안에서 `python3 -m unittest discover -p 'test_*.py'` 실행 결과의 마지막 네 줄:

```text
----------------------------------------------------------------------
Ran 151 tests in 6.113s

OK
```

`git diff --check`도 통과했다.

다음 두 명령을 실제로 실행했지만 모두 exit 1로 끝났다:

```text
python3 tools/meowbot.py --preview-tasks
python3 tools/meowbot.py --preview-tasks --who Zhe

Task preview failed: error connecting to api.github.com
check your internet connection or https://githubstatus.com
```

## 확인하지 못한 것과 해석

- 네트워크 샌드박스 때문에 실제 GitHub 보드/후보 PR을 이용한 CLI 미리보기는 확인하지 못했다. 위 화면은 지정된 fixture를 같은 함수로 렌더한 결과다.
- 봇 재시작이 금지되어 Discord에서 slash command 동기화와 실제 비공개/공유 표시를 실행하지 않았다. 응답 함수의 권한, ephemeral 옵션, mention 비활성화는 Discord stub으로 확인했다. 실제 등록은 검토 후 수동 재시작 때 이루어진다.
- 카드의 대기 시작은 hourly check와 같은 `updatedAt`이다. 상태 전환만의 시각은 기록되지 않으므로 다른 GitHub 업데이트가 있으면 대기 시간이 다시 계산된다. 후보 PR도 `updatedAt` 기준이다.
- `main` 줄은 봇이 기록한 활성 제출과 merge에 근거한다. 수동 제출이나 기록 밖의 merge까지 실시간으로 확인하지 않으며, 판단할 기록이 없으면 줄을 생략한다.
