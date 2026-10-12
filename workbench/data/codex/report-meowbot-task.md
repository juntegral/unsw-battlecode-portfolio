[Task]를 [Idea]와 동일하게 상태 알림·/board·/loop·/answer에서 처리하도록 수정했다.
status:candidate 알림: `#N is a candidate, PR + OK buttons coming` (기존 상태 중복 방지 적용).
기존 오프라인 검사를 확장했으며 19개 검사, py_compile, git diff --check를 통과했다.
봇 실행·재시작·종료, 실제 전송, 커밋은 하지 않았다.
