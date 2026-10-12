# jun 표시 이름 변경 보고

작성 시각: 2026-10-05 22:34:00 KST

- `tools/member_names.py`: 표시 이름을 `jun`으로 정규화한다. `jun`, `Jun`, `junsing`, `juntegral`, 이전 한글 이름을 같은 사람으로 받는다. 상태에서는 `by`, `idea_by`, `author`, `proposer` 이름 필드를 정규화하고 파일명·라벨·기타 값은 보존한다.
- `tools/meowbot.py`: MEMBERS, AUTHOR_LABELS, board/queue 이름, 카드 작성자, --who를 갱신했다. GitHub 라벨 `by:junsing`과 Discord id는 그대로다. `/task who`, `/hypo idea_by`, `/hypo-max idea_by`, `/board-edit idea_by`는 정규 이름을 자동완성으로 추천하면서 이전 별칭도 직접 입력할 수 있다.
- `tools/tasks.py`, `tools/decision_nudge.py`: 개인별 작업과 승인 대기 이름을 `jun`으로 표시한다. `/task` 호출자·대상 별칭과 이전 decision/snooze fixture 이름도 정규화한다.
- `tools/snooze.py`, `tools/meowbot.py`, `tools/smoke.py`, `tools/pair_report.py`: 기존 snooze·봇·pair 상태의 이름을 읽을 수 있고 새로 저장하는 이름 필드는 `jun`이다. pair 보고 출력에서도 이전 한글 이름을 정규화한다. 실제 운영 상태 파일은 이번 작업에서 직접 수정하지 않았다.
- `tools/meow_chat.py`: brain으로 읽은 문맥의 표시 이름과 ACTION PLAN의 idea_by를 정규화하고 프롬프트에 `jun` 표시 지침을 추가했다. 먼저 반영된 서버 버전 조회·LIVE/control·pair 연결·실패 시 보존 동작은 유지했다. 원본 memory·docs 파일은 수정하지 않았다.
- `tools/team_watch.py`: PR 작성자의 GitHub 계정 `juntegral`을 화면에는 `jun`으로 표시한다. 계정으로 하는 조회·필터는 그대로다.
- `tools/check-meow.py`, `tools/test_tasks.py`, `tools/test_snooze.py`: 출력 기대값을 갱신했다. 별도 check-meow의 brain 테스트에도 앞서 추가된 버전 조회 fixture를 넣어 외부 호출을 차단했다. `tools/test_jun_name.py`의 새 테스트 8개와 `tools/test_pr_poll.py`의 새 테스트 1개가 별칭, 라벨 연결, CLI, 상태 읽기·쓰기, 출력, 원본 보존을 확인한다.
- 커밋, 네트워크 요청, 운영 프로세스 시작·중지·재시작, 비밀 파일 읽기는 하지 않았다. 기존 작업자의 변경은 보존했다. 테스트는 외부 호출을 mock 또는 fixture 실행으로 대체했다.

## 남은 검색 결과

`grep -rn "준싱" tools/*.py`의 모든 남은 일치와 이유:

- `tools/member_names.py:2` — 이전 이름을 받는 입력 별칭 정의. 코드: `JUN_ALIASES = ('jun', 'junsing', 'juntegral', '준싱')`
- `tools/test_jun_name.py:17` — 이전·현재 이름을 받는 입력 별칭 테스트 목록. 코드: `ALIASES = ('jun', 'Jun', 'junsing', 'juntegral', '준싱')`
- `tools/test_jun_name.py:60` — CLI --who가 이전 이름을 받는지 확인하는 입력. 코드: `with patch('sys.argv', ['meowbot.py', '--preview-tasks', '--who', '준싱']), \`
- `tools/test_jun_name.py:67` — 기존 state.json의 by 필드 호환성 fixture. 코드: `old = {'candidates': {'fixture': {'by': '준싱', 'author_labels': ['by:junsing']}},`
- `tools/test_jun_name.py:68` — 파일명은 변경하지 않는지 확인하는 fixture. 코드: `'meow': {'plan': {'fields': {'idea_by': 'juntegral'}}}, 'file': '준싱.md'}`
- `tools/test_jun_name.py:78` — 기존 파일명이 보존되는지 확인하는 단언. 코드: `self.assertEqual(saved['file'], '준싱.md')`
- `tools/test_jun_name.py:82` — 기존 snooze.json의 by 필드 호환성 fixture. 코드: `path.write_text(json.dumps({'25': {'by': '준싱', 'until': (NOW + dt.timedelta(hours=2)).isoformat()}}))`
- `tools/test_jun_name.py:91` — 이전 이름이 들어 있는 decision-check 행 fixture. 코드: `row = (90, 25, 'queen-unbox', ('준싱', UID, 9), 'decision on the results')`
- `tools/test_jun_name.py:92` — 이전 이름이 들어 있는 snooze 표시 fixture. 코드: `quiet = ((row, {'by': '준싱', 'until': (NOW + dt.timedelta(hours=2)).isoformat()}),)`
- `tools/test_jun_name.py:96` — decision-check 출력에 이전 이름이 없음을 확인하는 단언. 코드: `self.assertNotIn('준싱', text)`
- `tools/test_jun_name.py:99` — pair 상태의 이전 by 값과 보존할 파일명 fixture. 코드: `state = {'label': 'fixture', 'kind': 'pair', 'by': '준싱', 'file': '준싱.md'}`
- `tools/test_jun_name.py:114` — 이전 이름이 들어 있는 brain 원본 문서 fixture. 코드: `source.write_text('준싱 will review the fixture.')`
- `tools/test_jun_name.py:120` — brain 출력에 이전 이름이 없음을 확인하는 단언. 코드: `self.assertNotIn('준싱', brain)`
- `tools/test_jun_name.py:121` — brain 원본 문서는 수정하지 않았음을 확인하는 단언. 코드: `self.assertEqual(source.read_text(), '준싱 will review the fixture.')`

## /task fixture 출력

테스트용 카드·시각으로 실제 생성했다. 온라인 현황을 뜻하지 않는다.

````text
📋 tasks · 21:27 KST
**jun** · 1 waiting
```
#25 queen-unbox  decide: ship it, drop it or revise · /answer card:25 text:…  1h 30m
```
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

## decision-check fixture 출력

테스트용 행·snooze·시각으로 실제 생성했다. 게시하지 않았다.

```text
⏰ 21:27 KST decision check
#25 queen-unbox has waited 1h 30m for jun's decision on the results (ship it, drop it, or revise). <@900000000000000005>
reply with /answer card:N text:…
still deciding: #39 queen-safety (jun, quiet until ~23:27 KST)
```

## 검증

`tools/`에서 `python3 -m unittest discover -p 'test_*.py'` 실행. 마지막 4줄:

```text
----------------------------------------------------------------------
Ran 168 tests in 6.366s

OK
```

별도 `python3 check-meow.py` 마지막 4줄:

```text
----------------------------------------------------------------------
Ran 28 tests in 0.136s

OK
```

`git diff --check` 통과.
