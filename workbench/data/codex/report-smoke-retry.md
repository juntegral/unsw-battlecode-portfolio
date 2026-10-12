# smoke swap 재시도 수정

- `swap()`은 `live or pending`인 RuntimeError만 15초 간격으로 재시도한다. monotonic 기준 900초가 지나면 마지막 오류를 다시 발생시키고, 다른 오류는 즉시 발생시킨다.
- `pair_execute`의 업로드·복귀 활성화와 `perform_rollback`의 활성화에 적용했다. 업로드 재시도 직전에 `check_freeze()`와 `pair_time_left(state)`를 다시 확인한다. 상태 필드와 실패 메시지는 유지했다.
- `pair_report.py` 첫 줄에는 새 게임과 상대·지도 키가 겹치는 실행만 표시하고, 각 실행의 공통 키 게임에 대한 승수/게임 수를 표시한다. 나머지 출력 형식은 유지했다.
- 재시도 성공, 기한 만료, 기타 오류 즉시 실패, 업로드 재시도 가드, 별도 rollback 재시도 테스트를 추가했다. 커밋·네트워크·실서버 smoke 실행은 하지 않았고, 금지된 파일과 기존의 관련 없는 변경은 건드리지 않았다.

`python3 -m unittest tools/test_smoke.py` 전체 출력의 마지막 5줄:

```text
..................................
----------------------------------------------------------------------
Ran 34 tests in 0.263s

OK
```

보고서 확인 결과:

- `tc30-dev1b`: `live baseline pooled over 15 games: 2/15` (기여 실행 `tc30-dev1`).
- `tc30-test`: `live baseline pooled over 120 games: 10/30, 11/30, 8/30, 8/30`.
- 두 보고서 모두 각 실행의 공통 키 승수/게임 수와 pooled 게임 수를 별도 assertion으로 확인했다. `git diff --check`도 통과했다.

불확실한 점 및 실행 방식: `pair_report.py`는 기본 실행에도 결과 파일을 저장하므로 브리프의 읽기 전용 조건과 충돌했다. 두 요청 명령과 같은 argv로 `runpy.run_path(..., run_name='__main__')`를 실행하되 결과 파일 쓰기는 메모리로 보내고 외부 프로세스 실행은 차단했다. 두 보고서 모두 기존 게임 파일만으로 완료했고 `--post`는 사용하지 않았다. 실제 서버에서의 재시도는 요청대로 확인하지 않았다.
