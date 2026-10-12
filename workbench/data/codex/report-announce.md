`--announce-file FILE [--dry-run]` 추가: urllib REST POST 후 종료하며 기존 SSL fallback과 토큰 읽기를 공유한다.
본문은 UTF-8 그대로 전송하고 빈 본문·2000자 초과는 거부한다. dry-run은 채널 id와 본문만 출력한다.
py_compile 통과, 가짜 요청·dry-run·길이 제한·비밀 오류 출력 테스트 4개와 기존 look 테스트 7개 통과.
실제 전송, 봇 재시작, 커밋은 하지 않았다.
