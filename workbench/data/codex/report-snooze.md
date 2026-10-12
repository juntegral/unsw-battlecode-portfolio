# Snooze 구현 보고

작성 시각: 2026-10-05 11:08:06 KST (`date` 확인).

`tools/meowbot.py`, `tools/decision_nudge.py`를 수정하고 공유 모듈 `tools/snooze.py`, 테스트 `tools/test_snooze.py`를 추가했다. 커밋, 네트워크 호출, 봇 또는 알림 서비스 기동은 하지 않았다. `docs/api.txt`, `docs/discord.txt`는 읽지 않았고 기존 `docs/PROMISES.md` 변경은 건드리지 않았다. 이 보고서를 마지막으로 작성했다.

`data/meowbot/snooze.json`은 첫 설정 때 생성되며 카드 번호별로 `until`, `by`, `note`, `set`을 저장한다. 시각은 시간대가 있는 ISO 문자열이다. 프로세스·스레드 잠금 아래 읽기와 갱신을 수행하고, 같은 디렉터리의 임시 파일을 flush/fsync한 뒤 원자적으로 교체한다. 이번 검증의 저장소는 모두 임시 디렉터리를 사용했다.

`/meow`는 카드 번호 또는 `#번호`로 시작하는 명확한 연기·재개 요청을 먼저 판별한다. 영어·한국어·중국어 연기는 기본 6시간이며 명시한 시간은 최대 24시간, tomorrow/내일/明天은 24시간이다. `back`, `done`, `cancel`, `resume`, `끝`, `취소`는 해제한다. 명확하지 않은 요청, 질문, 감지한 부정 표현은 메시지를 바꾸지 않고 기존 `MeowUI.slash`로 전달한다.

빠른 경로에서는 팀원 여부와 열린 [Idea]/[Task] 카드인지 확인하고, 모델 호출이나 확인 버튼 없이 공개 한 줄로 응답한다. GitHub에는 카드 조회만 하며 댓글을 쓰지 않는다. 누락·닫힌 카드·PR·일반 이슈는 찾을 수 없다는 응답을 한다. 모델 경로는 `SnoozeMeowUI` 초기화 때 기존 스키마에 `snooze {card, text}`와 `unsnooze {card}`를 등록하므로 기존 프롬프트의 허용 행동 목록에도 포함된다. 이 두 행동은 즉시 처리하며, 같은 계획에 포함된 다른 행동은 기존 확인 절차로 넘긴다. 기존 대화 모듈 파일은 수정하지 않았다.

시간별 알림은 유효한 snooze를 멘션 대상에서 빼고 메시지 끝의 `still deciding:` 한 줄에 이름과 KST 종료 시각을 표시한다. 알림 대상 전부가 연기 중이면 게시하지 않는다. 만료되거나 대기 상태를 벗어난 카드의 기록은 다음 조회 때 정리한다. 대기 상태는 유지하되 최근 갱신으로 아직 1시간이 안 된 카드는 연기 기록을 유지한다. dry-run은 파일을 쓰거나 기록을 정리하지 않는다.

`tools/` 안에서 `python3 -m unittest discover -p 'test_*.py'`를 실행해 90개 테스트가 통과했다. 다국어 의도·시간 파싱, 기존 흐름 전달, 권한·카드 상태, 공개 응답, 모델 행동의 확인 생략, 저장·만료·삭제·동시 갱신·교체 실패, 알림 제외·끝줄·전부 연기, 모의 dry-run을 검증했다. `git diff --check`도 통과했다. 테스트 실행의 마지막 4줄:

```text
----------------------------------------------------------------------
Ran 90 tests in 0.255s

OK
```

응답 예시 3개는 QWQ가 11:00 KST에 #25 queen-unbox를 요청한 경우이며, 테스트에서 문자열을 그대로 비교했다.

```text
⏸ #25 queen-unbox: QWQ is taking more time on the decision. decision checks stay quiet for this card until ~17:00 KST. "/meow 25 back" ends it early
⏸ #25 queen-unbox: QWQ is taking more time on the decision. decision checks stay quiet for this card until ~14:00 KST. "/meow 25 back" ends it early
▶ #25 queen-unbox: QWQ resumed decision checks for this card.
```

미확인 사항: 실제 Discord 표시와 실제 모델의 행동 선택은 네트워크 없이 검증할 수 없었다. `python3 tools/decision_nudge.py --once --dry-run`도 내부에서 `gh issue list`로 네트워크를 사용하므로 직접 실행하지 않았다. 대신 단위 테스트에서 GitHub 조회를 모의 처리하고 동일한 `--once --dry-run` main 경로를 실행했다. 자유로운 자연어의 모든 표현을 빠른 경로에서 인식한다고 보장하지 않으며, 감지하지 못한 요청은 기존 모델 흐름이 처리한다.
