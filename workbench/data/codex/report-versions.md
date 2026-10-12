# 온라인 테스트 버전 표기 작업 보고

2026-10-05 21:12:55 KST. `brief-versions.md` 범위로 작업했으며 커밋하지 않았다. 네트워크, 실제 pair 실행·업로드·활성화·Discord 전송은 하지 않았다. `submit.js`, `subs.js`, `--confirm` 동작은 테스트에서 스텁으로 대체했다. `tools/submit.js`는 수정하지 않았고 `docs/api.txt`, `docs/discord.txt`는 읽지 않았다. 작업 시작 때 존재하던 다른 변경은 유지했다.

변경 내용:

- `tools/smoke.py`: pair 업로드와 제출 identity 검증 후 `subs.js list --json --last 40` 한 번으로 새 제출과 live 제출 버전을 조회한다. `halves.new.submission.version`, `halves.old.submission.version`, `rollback.version`에 저장한다. 조회 실패·제출 누락·version 누락은 실행을 중단하지 않는다. 기존 업로드 설명 조회에서 확인한 live 버전도 pair 상태에 보존한다. live-only는 업로드 없이 실행 시작 시 동일 조회로 live 버전을 저장한다. `--ref`는 상태에 저장해 게시 없이 출력할 때도 사용한다.
- `data/online/smoke/run-pair.sh`: 수정 전에 `run-pair.before-versions.sh`로 복사했다. **단순한 선택으로 시작 공지는 `new bot`을 쓰고, 완료 공지에서 새 버전을 표시한다.** 시작 공지 시점의 새 버전 존재 여부에 따라 전송을 더 기다리지 않는다. live-only 시작 공지는 상태의 live 버전을 읽도록 기존 25초 대기 뒤에 보낸다. 버전이 없으면 live bot으로 표시하며 완료 공지는 기존 문구로 대체한다. 일정·업로드·재시도·롤백 로직은 유지했다.
- `tools/pair_report.py`: 버전이 모두 있으면 Discord 첫 줄·승수 열·baseline 마지막 줄에 버전을 표시한다. 출력과 `<label>-result.txt`에는 버전 관계 한 줄만 맨 앞에 추가하며 나머지 결과는 유지한다. 옛 상태 또는 일부 버전 누락은 기존 비교 문구를 유지한다. live-only Discord 결과에는 `v<live> main`을 표시한다.
- 테스트: `tools/test_smoke.py`, `tools/test_pair_report.py`, `tools/test_run_pair_live_only.py`. 버전 저장, 업로드 후 한 번 조회, 조회 실패·버전 누락, 세 공지, 버전 유무에 따른 결과, 출력 파일 일치, live-only 버전 표기를 확인했다. 셸 테스트는 임시 폴더에서 모든 온라인 명령을 가짜 명령으로 바꾸고 상태·공지 파일로 동기화한다.

아래 버전·카드·결과 수치는 테스트 예시다. 공지와 결과는 실제 생성되는 문자열 그대로다.

일반 시작 공지(new-only와 BASELINE 공통):

```text
🧪 testing online now: new bot = v42 main + card reference, 15 maps vs each of test4 + WeHaveQuizzes + dev1. the active bot swaps for ~20 min, please don't upload or swap until "done, swapped back"
```

일반 완료 공지:

```text
✅ done, swapped back: v42 main is active again. v43 (card reference) finished, result coming
```

live-only 시작 공지:

```text
🧪 more v42 main games for the baseline: 15 maps vs each of test4 + WeHaveQuizzes + dev1. no bot swap, uploads are fine meanwhile
```

버전이 있는 비교 결과 메시지:

````text
📊 v43 = v42 main + card, online result, same teams + maps
```
opponent       wins v43  wins v42  our score    their score
all            1/2       1.0/2     17.0 → 15.0  25.0 → 17.5
test4          1/1       0.0/1     4.0 → 20.0   40.0 → 5.0
WeHaveQuizzes  0/1       1.0/1     30.0 → 10.0  10.0 → 30.0
```
v42 baseline 60 games. about ±4 wins in 30 games is luck
````

같은 예시의 출력·결과 파일에 추가되는 첫 줄:

```text
v43 = v42 main + card
```

버전이 없는 비교 결과 메시지:

````text
📊 card online result, same teams + maps
```
opponent       wins new  wins live  our score    their score
all            1/2       1.0/2      17.0 → 15.0  25.0 → 17.5
test4          1/1       0.0/1      4.0 → 20.0   40.0 → 5.0
WeHaveQuizzes  0/1       1.0/1      30.0 → 10.0  10.0 → 30.0
```
live baseline 60 games. about ±4 wins in 30 games is luck
````

live-only 결과 메시지:

````text
📊 v42 main (card): baseline result. no bot swap or upload
```
opponent  wins this run  pooled wins /15  pooled games
test4     1/1            15.0/15          1
```
````

검증:

- `zsh -n data/online/smoke/run-pair.sh`: 성공.
- `git diff --check`: 성공.
- tools/ 안에서 `python3 -m unittest discover -p 'test_*.py'`: 성공. 최종 실행 마지막 네 줄:

```text
----------------------------------------------------------------------
Ran 123 tests in 6.115s

OK
```

실행하지 않은 부분: 실제 서버 제출 목록의 버전 응답, 업로드·활성화·대전·다운로드, 실제 25초 공지 시점과 장시간 재시도, Discord 전달. 이 작업의 검증은 오프라인 스텁이며 온라인 pair를 실행하지 않았다. 이 보고서는 모든 코드 수정과 검증 뒤 마지막으로 작성했다.
