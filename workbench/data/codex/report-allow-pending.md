# 변경 결과

- `tools/submit.js upload`에 `--allow-pending`을 추가했다. pending/live 경기가 있으면 지정된 안내 한 줄을 출력하고 계속한다. 옵션이 없을 때의 거부 메시지와 종료 코드, `--force`의 허용 동작을 유지했다. `activate`는 변경하지 않았다. 사용법도 갱신했다.
- `tools/meowbot.py`의 릴리스 `upload()`는 항상 `--allow-pending`을 전달한다.
- `tools/smoke.py`는 변경하지 않았다. 기존 시험에 paired 및 single 시험 업로드가 해당 옵션을 전달하지 않는 검증을 추가했다.
- 새 오프라인 테스트는 릴리스 명령의 옵션과 pending 정책 함수의 거부·허용·force·빈 목록 분기를 검증한다.

`node --check tools/submit.js`와 `git diff --check`가 통과했다. `tools/`에서 실행한 전체 unittest 결과의 마지막 4줄:

```text
----------------------------------------------------------------------
Ran 186 tests in 11.108s

OK
```

실제 네트워크 호출, 서버 pending 조회, 실제 업로드·활성화 및 로컬 경기 실행은 수행하지 않았다. pending 정책은 분리한 함수를 통해 오프라인으로 검증했고 릴리스와 시험 업로드 명령은 subprocess 모의 처리로 검증했다. 금지된 CLI 명령 실행, 비밀 파일 읽기, 서비스 프로세스 제어 및 커밋은 하지 않았다.
