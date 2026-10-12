# run-pair 재시도 수정 보고

작성 시각: 2026-10-05 18:50:10 KST (`date` 확인).

## 변경 범위

- 수정 전에 `data/online/smoke/run-pair.before-retry2.sh`로 원본을 복사했다.
- 수정 파일은 `data/online/smoke/run-pair.sh`뿐이다. `tools/smoke.py`와 기존 테스트는 수정하지 않았다. 이 보고서를 마지막으로 작성했다.
- 16–59행: 실패 상태의 재시도 안전성 검사와 `<label>.failed-<n>.json` 보존 함수. 기존 파일명을 덮어쓰지 않도록 하드 링크를 먼저 만든 뒤 원래 이름을 해제한다.
- 60–117행: 종료 후 분류하는 재시도 루프, 네트워크 재시도 최대 5회, 시작 거절 재시도 30분 제한. 기존의 무조건적인 상태 파일 삭제를 제거했다.
- 118–132행, 150행: 최종 실패 이유를 상태의 오류 또는 로그에서 가져오고 빈 phase 대신 원인을 알린다.
- 83–85행: 최초 실행의 기존 시작 알림은 유지하되 재시도 실행에서는 시작 알림도 다시 보내지 않는다. 재시도 도중에는 종료 알림이 없다.
- 1–14행의 상대·지도·`BASELINE=1` 설정과 137–146행의 자동 롤백 루프는 원본과 바이트 단위로 동일함을 검사했다. 완료 알림, 복구 실패 알림, finished 표시도 유지했다.

## 사례 1: 업로드 네트워크 실패

1. `smoke.py pair` 종료를 기다린다. 기존과 달리 25초 이후 종료해도 오류를 검사한다.
2. 상태가 `kind=pair`, 해당 label, `phase=failed`이고 `active_verified=true`, `rollback_required=false`인지 확인한다. 관측된 활성 제출과 롤백 대상, old 제출의 id가 시작 시 `BASEID`와 같아야 한다.
3. old/new 양쪽의 `battle_ids`와 `requests`가 명시적으로 빈 배열이어야 한다. 완료/진행 중 half는 제외하고, new 제출은 없어야 한다. 그러므로 경기·요청 이력, 미확인 활성 상태, 업로드된 new 제출, 보류 중 롤백이 있는 상태는 보존 대상으로 옮기지 않는다.
4. 상태의 오류가 `submit.js upload failed`이면서 `fetch failed`, `ECONNRESET`, `ETIMEDOUT`, `EAI_AGAIN`, `socket hang up` 중 하나일 때만 재시도한다.
5. 60초 기다리고 같은 안전성 검사를 다시 한다. 실패 상태를 사용 가능한 첫 `<label>.failed-<n>.json` 이름으로 보존한 뒤 동일 bot·label·상대·지도·MODE로 새 pair를 시작한다.
6. 최초 시도 이후 최대 5회 재시도한다. 여섯 번째 실패는 현재 `<label>.json`에 남기고 마지막에 네트워크 오류가 다섯 번의 재시도 후에도 계속됐다는 알림을 한 번 보낸다.
7. 실행 전 같은 label의 안전한 실패 상태가 이미 있어도 같은 60초 대기와 보존을 적용하며, 이를 첫 재시도로 센다. 안전하지 않은 기존 상태는 삭제하거나 이동하지 않는다.

`tools/smoke.py:330–331`은 상태 파일이 이미 있으면 `State already exists; refusing duplicate pair`를 발생시킨다. 실패 상태를 이어서 실행하는 resume 경로는 없다. 그래서 안전한 상태만 보존 후 새로 시작하는 방식을 선택했다. 실제 `qw37-test.json`은 이 검사 조건에 맞는다.

## 사례 2: live/pending 시작 거절

기존 스크립트는 25초 뒤 `kill -0`이 성공하면 `started=1`로 설정하고 시작 검사 루프에서 바로 빠져나왔다. 그 뒤 `wait`에서 받은 오류는 재시도 검사로 돌아가지 않았다. 따라서 25초 이후 발생한 `qh31c-dev1.log`의 거절은 문자열이 기존 grep 목록에 있어도 재시도되지 않는다. 해당 로그에 타임스탬프가 없어 정확한 종료 초는 확인할 수 없지만, 이 제어 흐름과 보고된 90초 이내 종료가 현상을 설명한다. grep도 명시적인 `-E`와 `|`로 바꿨다.

1. pair 종료 이후, 상태 파일이 아직 없고 로그에 `refusing to swap or start`, `live or pending` 또는 기존의 `Insufficient`가 있는지 확인한다.
2. 최초 거절을 감지한 때부터 1,800초의 기한을 설정한다.
3. 종료 후 60초 기다리고 같은 실행을 다시 시작한다. 마지막 대기는 남은 기한이 60초 미만이면 그만큼으로 줄인다.
4. 기한이 끝난 뒤에는 새 실행을 시작하지 않는다. 실행 중 기한을 넘겨 종료하는 경우에도 이후 재시도는 하지 않는다. 진행 중인 pair를 강제로 죽이지는 않는다.
5. 최종 알림은 다른 우리 경기 때문에 서버가 30분 동안 교체를 거절했다고 설명한다. allowance 부족은 별도의 문구로 설명한다. 빈 phase는 출력하지 않는다.

## 검증

- `zsh -n data/online/smoke/run-pair.sh`: 성공.
- `tools/`에서 `python3 -m unittest discover -p 'test_*.py'`: 90개, `OK`.
- 임시 오프라인 점검: `/private/tmp/check-runpair-retry.py`. 최종 출력: `/private/tmp/check-runpair-retry-output.txt`.
- 실제 스크립트 본문을 임시 디렉터리에 복사하고 작업 경로를 바꿨다. `python3 tools/smoke.py`, Node 활성 조회, Discord 전송을 가짜 함수로 대체했다. 실행 복사본에는 `--confirm` 문자열을 남기지 않았으며, 모든 확인 플래그를 무효한 stub 플래그로 바꿨다. sleep은 짧은 대기와 zsh `SECONDS` 증가로 대체했다. 운영 스크립트에는 테스트용 환경변수나 실행 경로를 추가하지 않았다.
- 네트워크 오류 5종, 네트워크 실패 반복 한도, 25초 관찰 이후의 네트워크 실패와 live/pending 거절, 빠른 거절, 30분 반복 거절, allowance 부족, 보존 함수 실패, 경기/요청/롤백/미확인 상태/new 제출/완료 이력/깨진 JSON 보호, 다른 업로드 오류, 기존 안전/위험 상태, 보존 이름 충돌, `BASELINE=1` 등 총 23개 시나리오가 통과했다.
- 테스트마다 상대 `19,87`이 그대로 전달되는지 확인했다. 기본 MODE는 `--new-only --games 30`, BASELINE 모드는 `--games 60`이었다. 보류 롤백 사례에서는 기존 자동 롤백 경로가 가짜 rollback을 한 번 호출해 복구하는 것도 확인했다.

### 실제 오프라인 출력

```text
PASS network-once fetch failed : attempts=2, archives=1, 60s waits=1, notices=1, baseline=False
PASS network-once ECONNRESET : attempts=2, archives=1, 60s waits=1, notices=1, baseline=False
PASS network-once ETIMEDOUT : attempts=2, archives=1, 60s waits=1, notices=1, baseline=False
PASS network-once EAI_AGAIN : attempts=2, archives=1, 60s waits=1, notices=1, baseline=False
PASS network-once socket hang up : attempts=2, archives=1, 60s waits=1, notices=1, baseline=False
PASS network-forever  : attempts=6, archives=5, 60s waits=5, notices=1, baseline=False
  ⚠️ offline card online test stopped early: the upload request kept failing on the network after five retries. the live bot is active, nothing is broken. checking what happened
PASS network-late  : attempts=2, archives=1, 60s waits=1, notices=2, baseline=False
PASS archive-failure  : attempts=1, archives=0, 60s waits=1, notices=1, baseline=False
PASS refusal-fast  : attempts=2, archives=0, 60s waits=1, notices=1, baseline=False
PASS refusal-late  : attempts=2, archives=0, 60s waits=1, notices=2, baseline=False
PASS refusal-forever  : attempts=22, archives=0, 60s waits=21, notices=1, baseline=False
  ⚠️ offline card online test stopped early: the server kept refusing the swap for 30 minutes because other battles of ours were running. the live bot is active, nothing is broken. checking what happened
PASS allowance  : attempts=22, archives=0, 60s waits=21, notices=1, baseline=False
  ⚠️ offline card online test stopped early: the server kept refusing the run for 30 minutes because the game allowance was insufficient. the live bot is active, nothing is broken. checking what happened
PASS protected-battle  : attempts=1, archives=0, 60s waits=0, notices=1, baseline=False
PASS protected-request  : attempts=1, archives=0, 60s waits=0, notices=1, baseline=False
PASS protected-rollback  : attempts=1, archives=0, 60s waits=0, notices=1, baseline=False
PASS protected-unverified  : attempts=1, archives=0, 60s waits=0, notices=1, baseline=False
PASS protected-new-submission  : attempts=1, archives=0, 60s waits=0, notices=1, baseline=False
PASS protected-finished  : attempts=1, archives=0, 60s waits=0, notices=1, baseline=False
PASS protected-malformed  : attempts=1, archives=0, 60s waits=0, notices=1, baseline=False
PASS other-error  : attempts=1, archives=0, 60s waits=0, notices=1, baseline=False
PASS success  safe: attempts=1, archives=2, 60s waits=1, notices=1, baseline=False
PASS success  unsafe: attempts=1, archives=1, 60s waits=0, notices=1, baseline=False
PASS success  : attempts=1, archives=0, 60s waits=0, notices=1, baseline=True
All 23 offline scenarios passed; no real pair, upload, confirmation command, Discord, or network call executed.
```

## 실행하지 않은 부분과 남은 불확실성

- 운영 스크립트 자체의 외부 호출인 13행·80행·136행·140행·143행과 14행의 Discord 호출은 실제 서비스로 실행하지 않았다. 모든 pair/업로드/활성화/알림 효과는 stub으로만 검사했다. 네트워크, 실제 pair test, 업로드, 확인 플래그가 있는 실제 명령, 커밋은 실행하지 않았다. `docs/api.txt`, `docs/discord.txt`는 읽지 않았다.
- 새 분기 중 69–71행의 **실행 전 기존 상태 보존 실패**는 직접 유발하지 않았다. 같은 실패 처리인 96–98행은 보존 함수가 실패하도록 만들어 검사했다.
- 111–113행의 **실행 도중 기한을 넘긴 뒤 종료** 분기는 직접 유발하지 않았다. 75–77행의 재시도 시작 전 기한 검사는 반복 거절/allowance 시나리오에서 실행했다.
- 50행/54행의 실제 디스크·권한 오류는 유발하지 않았다. 정상 보존 및 52–53행 이름 충돌은 검사했다. 56–57행의 깨진 JSON 처리도 검사했다.
- 129행의 완전히 빈 로그에 대한 기본 문구와 150행의 reason 없는 기본 문구는 직접 유발하지 않았다. 상태 오류, 상태 없는 로그 오류, 최종 재시도 실패 이유는 확인했다.
- 기존 롤백의 40회 실패, 141행의 30초 반복 대기, 145행의 완료 판정, 152행의 끝내 복구하지 못한 알림은 이번 추가 점검에서 직접 실행하지 않았다. 해당 루프는 바꾸지 않았다.
- 30분은 최초 거절 감지부터의 재시도 시작 허용 시간이다. 이미 시작한 pair와 기존 롤백은 안전상 강제 종료하지 않으므로 전체 프로세스의 종료 시각까지 30분으로 제한하지 않는다.
- 업로드 요청 오류만으로 서버에서 업로드가 전혀 일어나지 않았는지는 증명할 수 없다. 재시도 허용은 smoke.py가 오류 직후 활성 제출을 다시 확인하여 기존 live id를 검증했고, 요청 이력도 없으며, 롤백이 필요 없다고 저장한 경우로 한정했다. 이것은 브리프가 지정한 확인 근거이며 실제 서버 동작은 이번 오프라인 작업에서 추가 확인하지 않았다.
- 같은 label을 여러 launcher가 동시에 실행하는 경우의 조정은 이번 범위에서 추가하지 않았다. 정상적인 단일 launcher 흐름에서 상태를 보존하며, 기존 보존 파일은 덮어쓰지 않는다.
