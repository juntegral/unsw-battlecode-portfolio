meowbot·team_watch의 PR 알림을 `gh pr list --state all --limit 30` 스냅샷 비교로 전환했다.
opened/reopened/merged/closed/ready-for-review를 감지하고, team_watch는 head SHA 변경도 출력한다.
첫 실행은 조용히 초기화하며, 기록 없는 열린 #26만 한 번 알린다. 이벤트 피드의 PR 중복은 제외한다.
기존 PR 카드·멘션 없음·후보 승인 초기화 경로를 유지했고, 일반 점검과 --prs에 모두 적용했다.
오프라인 가짜 테스트 7개와 py_compile 통과. 테스트 상태는 임시 폴더만 사용했다.
봇 실행·재시작·종료, 실제 게시, 원격 호출, 커밋은 하지 않았다.
