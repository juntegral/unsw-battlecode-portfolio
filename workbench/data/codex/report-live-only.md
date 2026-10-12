# live-only 작업 보고

2026-10-05 21:04 KST. 커밋 없음. 실제 온라인 대전·업로드·활성화·Discord 전송·네트워크 호출 없음. `tools/submit.js`와 비밀 파일은 수정하거나 실행/열람하지 않았다. 작업 도중 다른 작업의 `tools/submit.js`, `tools/test_submit_verify.py` 변경이 나타났으며 그대로 두었다.

변경한 파일:

- `tools/smoke.py`: pair와 단일 start/plan 업로드에 `--desc`, `--ref` 추가. 기본 설명은 활성 제출 id의 version을 `subs.js list --json` 한 번으로 조회해 만든다. 조회 실패·해당 제출 없음·version 없음이면 `live <id>`로 계속한다. 명시 설명과 기본 설명 모두 190자로 자른다. plan에 보이는 설명과 실제 업로드 설명은 같다.
- `tools/smoke.py`: `pair --old-only` 추가, `--new-only`와 상호 배타적. botdir 검사·버전 조회·업로드·swap·롤백·swap을 위한 pending 검사를 생략한다. 한쪽 경기만 예산에 계산한다. 정상 pair 형태로 old에 경기와 원래 live id를 기록하고 new는 submission=None, battle_ids=[], requests=[], phase=skipped로 남긴다. old 완료 후 최종 phase는 기존 완료 판정과 호환되는 `rolled-back`, rollback_required=False로 기록한다. 이 phase는 live-only에서 실제 롤백을 의미하지 않는다. 실패 시에도 rollback_required=False이며 수동 rollback 명령 역시 활성화를 실행하지 않는다.
- `tools/pair_report.py`: old-only에서는 live 승수·평균 양측 점수·상대별 결과와 누적 baseline 경기 수를 출력한다. 이번에 완료한 old half도 기존 baseline 수집 규칙으로 포함된다. Discord에는 상대별 이번 승수, 누적 승률을 15판으로 환산한 승수, 누적 경기 수를 한 개의 정렬된 fenced table로 보낸다. 일반 비교 보고는 그대로 유지했다.
- `data/online/smoke/run-pair.sh` (git-ignored): 변경 전에 `data/online/smoke/run-pair.before-liveonly.sh`로 복사했다. 모든 pair에 카드 문구를 `--ref`로 전달한다. LIVE_ONLY=1은 --old-only로 실행하며 BASELINE보다 우선한다. 시작 공지는 업로드가 가능하다고 명시하고, 완료 시 pair_report --post로 결과 한 메시지를 전송한다. 이 분기는 활성 봇 재확인·롤백 루프에 들어가지 않는다. 일반 new-only 기본값, BASELINE=1, retry_state와 재시도 로직, 일반 롤백 루프는 유지했다.
- 테스트: `tools/test_smoke.py`, `tools/test_pair_report.py`, 새 `tools/test_run_pair_live_only.py`. Node/API 호출을 스텁으로 막았다. 셸 래퍼 테스트는 임시 디렉터리에서 node/python3/sleep을 가짜 명령으로 대체해 일반·BASELINE·live-only 성공/실패를 확인한다.

저장소 루트에서 실행할 정확한 명령 예시(이 작업에서는 실행하지 않았다). label은 기존 state와 겹치지 않아야 한다.

(a) 일반 카드 테스트:

```zsh
data/online/smoke/run-pair.sh card-liveonly-check versions/v1.7/bot "CARD-123: queen spacing" 19,87,545
python3 tools/pair_report.py card-liveonly-check --post "CARD-123: queen spacing"
```

일반 래퍼는 기존처럼 완료 공지만 보내므로 결과를 게시하는 기존 pair_report 명령도 함께 적었다.

(b) live-only 실행(결과 게시까지 래퍼가 처리):

```zsh
LIVE_ONLY=1 data/online/smoke/run-pair.sh live-baseline-extra - "more live bot games" 19,87,545
```

설명 예시(버전 42와 id 17594는 예시이며 실제 활성 제출을 조회하지 않았다):

```text
TEST. v42 main + CARD-123: queen spacing. vs test4, WeHaveQuizzes, dev1
TEST. live 17594 main + card-liveonly-check. vs test4, WeHaveQuizzes, dev1
```

두 번째 예시는 버전 조회 실패 및 --ref 생략 시 label로 대체하는 경우다. --desc를 주면 그 문구를 190자로 잘라 그대로 사용한다.

live-only 시작 Discord 공지:

```text
🧪 more live bot games for the baseline: 15 maps vs each of test4 + WeHaveQuizzes + dev1. no bot swap, uploads are fine meanwhile
```

live-only 완료 Discord 메시지 예시(아래 수치는 가상):

````text
📊 more live bot games: live bot baseline result. no bot swap or upload
```
opponent       wins this run  pooled wins /15  pooled games
test4          8/15           7.5/15           60
WeHaveQuizzes  6/15           6.8/15           60
dev1           10/15          9.0/15           60
```
````

검증:

- `zsh -n data/online/smoke/run-pair.sh`: 성공.
- tools/ 안에서 `python3 -m unittest discover -p 'test_*.py'`: 성공. 최종 실행 마지막 네 줄:

```text
----------------------------------------------------------------------
Ran 117 tests in 3.820s

OK
```

- `git diff --check`: 성공.
- `python3 tools/smoke.py pair --help`: 실행해 --new-only | --old-only, --desc DESC, --ref REF 표시를 확인했다.

서버 없이 확인하지 못한 점과 선택:

- 실제 제출 목록 응답, 실제 업로드 설명 보존, 온라인 allowance/대전 응답, 다운로드, Discord 전달은 실행하지 않고 스텁으로만 확인했다.
- 진행 중 다른 업로드가 활성 제출을 바꾸면 다음 요청의 기존 --expect-active/identity 검증이 중단시킨다. live-only는 그 업로드를 되돌리지 않는다. 이미 요청된 경기는 기록된 원래 live 제출에 속한다.
- pooled games는 이번 run에 나타난 상대+지도 키의 완료 live 경기 수이며, pooled wins /15는 그 경기들의 승률 ×15다. 기존 일반 비교의 지도별 평균 계산은 바꾸지 않았다.
- pair_report의 기존 로더는 상대+지도당 한 row와 한 번의 지도 순회를 전제로 한다. 이번 래퍼의 상대별 서로 다른 15지도 일정에 맞으며, 같은 run에서 동일 지도를 여러 번 돌리는 로더 확장은 하지 않았다.
