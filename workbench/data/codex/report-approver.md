# meowbot 작성자 라벨·공동 승인 변경 보고

- 작성: 2026-10-03 23:15:35 KST.
- /hypo·/hypo-max 생성 시 제안자의 by:junsing/by:zhe/by:qwq/by:ai 라벨을 붙인다.
- 선택 옵션 idea_by 또는 입력 본문의 Idea by: 줄로 다른 제안자를 지정한다. 모달 입력칸은 기존 5개를 유지한다.
- /board-edit는 기존 작성자를 보존하며, 지정 시 본문·라벨을 변경한다. 실제 편집자 기록은 유지한다.
- author_label()과 모듈 docstring에 AI 카드 라벨링 명령을 문서화했다.
- 후보 게시 때 연결 이슈의 작성자 라벨을 한 번 조회해 author_labels와 oks를 상태에 저장한다.
- 라벨 없음 → 본문 작성자 → 알 수 없는 인간 순으로 판정한다. 기존 미결 카드도 첫 OK 때 안전하게 초기화한다.
- 인간·혼합 후보는 작성자 1명 + 비작성자 1명, AI 전용은 멤버 1명, 작성자 불명은 서로 다른 멤버 2명이 필요하다.
- 카드에 작성자·필요 승인·현재 OK를 표시한다. 중복 OK는 추가되지 않으며 열린 확인창도 중복 생성하지 않는다.
- Cancel·확인창 만료 후 OK는 유지하고 같은 멤버도 확인창을 다시 열 수 있다.
- 새 head SHA는 OK를 초기화하고 새 카드에 초기화 안내를 표시한다.
- UPLOAD_ENABLED=False, 기존 잠금·SHA 검증·병합·sync_release(merge commit)·업로드 경로를 유지했다.
- data/codex/check-approver.py: 가짜 gh/Discord/subprocess 기반 오프라인 검사 25개 통과.
- py_compile 및 git diff --check 통과. 필수 승인·중복·SHA·fallback과 기존 병합 안전장치를 검증했다.
- 봇 실행·재시작·종료, 실제 gh 쓰기·병합·push·commit·제출, 키·실제 상태 파일 접근은 하지 않았다.
- 실제 Discord/GitHub 통합은 검증하지 않았다. 변경은 미커밋이며 실행 중인 봇에는 적용하지 않았다.
