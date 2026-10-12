새 replay 첨부 동작을 검증하도록 look 테스트 14개를 갱신: 텍스트 우선, 개별 전송(최대 3개), 원본/gzip/초과 건너뛰기, 실패 후 계속, manifest 없음.
실제 버그 수정: 파일 실패 시 NameError를 내던 log를 모듈 범위로 이동하고, 읽기 파일 핸들을 with로 닫도록 tools/meowbot.py를 최소 수정.
지정 검사 11개 파일 모두 통과, git diff --check 통과; 봇 실행·재시작 및 커밋 없음.
