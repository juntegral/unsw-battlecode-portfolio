AI 제목의 기존 [Idea]/[Task] 접두사를 제거한 뒤 [Idea]를 한 번만 붙이도록 수정했습니다.
ladder 프롬프트와 생성 카드에 지정 승인 문구를 적용했습니다(빌드 전 승인 없이 진행, 출하 전 팀원 1명 OK).
일상 진행 댓글과 재시작 시 남은 진행 댓글 예약을 제거하고 status.json·Loop heartbeat에 기록합니다.
질문·look 요청·결과/판정·task check·실패·후보 PR 링크 댓글은 유지하며 회귀 테스트 7개를 추가했습니다.
python3 -m unittest discover -s work/loop/tests: 50개 통과; 라이브 러너 조작·커밋·푸시 없이 파일만 수정했습니다.
라이브 카드 #15/#17/#18 열람은 gh 네트워크 차단, 웹 조회 실패 및 Aside 미실행으로 확인하지 못했습니다.
