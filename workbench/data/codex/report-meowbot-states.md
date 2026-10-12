# meowbot 상태 연동 완료
- `needs-info`·`needs-look`에 짧은 알림, `tested` 기존 판정 문구에 작성자 멘션을 추가했다.
- `by:*`를 MEMBERS ID로 연결하며 `by:ai`·알 수 없는 작성자는 멘션하지 않는다.
- 상태와 이벤트 커서를 저장해 중복을 막고, 상태 재진입은 새 전환으로 알린다.
- `/board`·`/loop`에서 열린 카드의 `status:*`를 표시하고 `/loop`는 최종 상태를 숨긴다.
- 카드 형식을 유지하며 다수 카드는 Discord 임베드 개수·문자 한도 안에서 나눠 보낸다.
- `check-meowbot-states.py` 오프라인 10개, 기존 `check-approver.py` 25개, `py_compile`·`git diff --check` 통과.
- 봇 실행·재시작·종료, 실제 Discord/GitHub 작업, 커밋은 하지 않았다.
