# /meow 서버 버전 문맥 변경 보고

작성 시각: 2026-10-05 22:26:44 KST

- `tools/meow_chat.py`: brain 갱신마다 `node tools/subs.js list --json --last 15`를 10초 제한으로 실행한다. 최신 버전부터 표시하고 활성 제출에 LIVE를 붙인다. 이름과 새 제출 id가 맞는 pair 상태에서 카드 참조(없으면 label), 상대, 결과 파일 첫 줄을 연결한다. 활성 제출을 control로 명시한다.
- 같은 파일: 실패하면 이전 섹션을 보존하고 `(could not refresh at HH:MM)`을 갱신한다. 섹션은 오래된 버전부터 제거해 2,499자 이하로 제한한다. 버전 조회와 버전 우선·카드 다음 명명 지침을 모델 프롬프트에 추가했다.
- `tools/meow_ui.py`는 기존 `session_call()` 경로로 변경 사항을 사용하므로 수정할 필요가 없었다.
- `tools/test_meow_versions.py`: 새 테스트 8개로 label 연결, 미연결 버전, LIVE/control, 결과 첫 줄, ref 대체, id 검증, 조회 실패·타임아웃, 길이 제한, brain 갱신을 검증한다. `tools/test_meow_eta.py`, `tools/test_meow_late.py`도 새 조회를 스텁 처리한다. 테스트에서 서버에 접속하지 않았다.
- `DECISIONS.md`에 결과를 기록했다. 커밋, 봇 시작·중지·재시작, 비밀 파일 읽기는 하지 않았다.

아래는 테스트 fixture에서 실제 생성한 섹션이다. 설명과 결과 문구는 예시이며 실제 온라인 결과를 뜻하지 않는다.

```text
## Bot versions on the server
v26 · 17648 · qh31d-test · idle · Queen hunt test · tested: #31 queen-hunt (on new main) · vs test4 + WeHaveQuizzes · Fixture result: mechanism observed
v22 · 17594 · card-25-ff0327008d · active · LIVE · Current main
Control: v22 (active submission 17594); card tests are v22 main + <card>.
```

`tools/`에서 실행: `python3 -m unittest discover -p 'test_*.py'`

테스트 출력의 마지막 4줄:

```text
----------------------------------------------------------------------
Ran 159 tests in 6.168s

OK
```
