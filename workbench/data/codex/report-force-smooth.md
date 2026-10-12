# Force 예약 변경 보고서

작성: 2026-10-05 22:55:20 KST

## 완료 범위와 차단 사항

**봇 변경과 루프 패치 검증은 완료했지만, 지정 worktree 생성 및 커밋은 미완료다.**

요청한 `git worktree add -b loop/force-after-build ~/.claude/jobs/e3d433df/tmp/force-smooth-wt origin/main`이 다음 오류로 거부됐다.

```text
fatal: cannot lock ref 'refs/heads/loop/force-after-build': Unable to create '.../battlecode/.git/refs/heads/loop/force-after-build.lock': Operation not permitted
```

현재 환경에서 `.git`은 읽기만 허용되며 권한 승격도 사용할 수 없다. 사용자에게 worktree 생성 명령 실행을 요청했으나 아직 생성되지 않았다. 따라서 브리프의 worktree 내 테스트와 커밋 조건을 충족했다고 보고하지 않는다.

- 요청 브랜치: `loop/force-after-build` — 생성되지 않음.
- worktree 커밋 ID: 없음.
- 기준 `origin/main`: `fa618613c2dba9292ec1311a7897b46635965dac` (네트워크 갱신 없음).
- battlecode 원본 checkout: 수정 없음.
- unsw-swarm: 커밋 없음.
- 네트워크 접근, 봇·러너 시작/정지/재시작, push 없음. 금지된 두 자격증명 파일을 읽지 않았다.

## 저장소별 변경

### unsw-swarm

- `tools/meow_chat.py`: building 상태의 강행 candidate 요청을 미리보기 시점의 attempt에 고정한다. 내부 필드로 보관하고 spool 시 `after_build: true`, `attempt: n`을 넣는다. 모델이 이 필드를 직접 지정하지 못하게 기존 입력 스키마를 유지했다.
- 같은 attempt의 정상 진행은 확인 중에도 허용한다. 새 attempt, 실패, 카드 본문 변경은 차단한다. 기존 일반 Force와 권한·두 번의 확인·한 줄 사유·금지 작업 규칙은 유지한다.
- 미리보기와 최종 확인 뒤 메시지를 자동 대기 안내로 바꿨다. 현재 단계의 미래 ETA가 있을 때만 표시한다. 단계 ETA를 전체 재빌드 완료 시간으로 표현하지 않는다.
- standing prompt에 직접 예약 가능한 일을 “나중에 다시 요청하라”고 돌려보내지 말고, 시간 경고는 무엇이 언제 실행되는지 설명하도록 추가했다.
- `tools/test_meow_force_smooth.py`: 9개 테스트 추가. 문구, spool 필드, 확인 절차, 진행 중 상태 변경, 기존 동작, prompt, 결과를 요청 스레드에 한 번만 게시하는 경로를 검증했다.
- `tools/meow_ui.py`: 변경할 필요가 없었다. 기존 `poll()`이 예약 결과 파일을 읽어 원래 요청 스레드로 보내는 것을 테스트했다.
- `DECISIONS.md`: 실제 시계 시각으로 결과와 제한을 기록했다.

### battlecode용 패치

적용 파일은 `data/codex/force-smooth-loop.patch`다. 테스트용 로컬 사본은 `~/.claude/jobs/e3d433df/tmp/force-smooth-review`에 있다. 이 사본은 **git worktree가 아니다**. `origin/main`의 `work/`만 로컬 archive로 꺼냈다.

- `work/loop/meow_control.py`: deferred forced candidate 요청은 building 동안 receipt를 실행 중으로 만들지 않고 대기한다. mechanism/look도 building 상태에 속하므로 계속 대기한다.
- 같은 attempt가 needs-look 또는 이후 상태에 도달하고 commit/base가 있으면, 기존 `base_moved()`로 현재 기준임을 확인한 뒤 `_state` 진행을 허용하여 적용한다.
- attempt 변경, `meta.failed` 또는 build/adopt/task 작업 실패, 6시간 경과는 사람이 읽을 수 있는 사유로 거부한다. main의 봇 코드가 다시 바뀐 경우에도 오래된 코드를 후보로 열지 않고 취소한다.
- 기존 AI/game lock, pause, audit comment, 결과 파일, 일반 forced set_state 동작은 유지한다. `runner.py` 변경 없음.
- `work/loop/tests/test_force_after_build.py`: 14개 테스트 추가. 브리프의 6개 조건에 더해 단계별 대기, 늦은 상태, 실패 파일, audit/중복 적용 방지, 현재 기준·commit 필수 조건, lock 및 deferred 범위를 검증했다.
- 원본 checkout에서 `git apply --check` 통과. 실제 적용은 하지 않았다.

## 봇 메시지 원문

ETA 없는 미리보기:

```text
Force for #31 queen-hunt: skip the remaining tests and open the candidate. The loop is still rebuilding it on the new main; confirm now and it happens by itself when this rebuild and its replay check finish. You don't need to come back.
Force: confirm → responsibility reason → final confirm.
```

유효한 현재 단계 ETA가 19:11 KST인 경우의 미리보기:

```text
Force for #31 queen-hunt: skip the remaining tests and open the candidate. The loop is still rebuilding it on the new main (current step done about 19:11 KST); confirm now and it happens by itself when this rebuild and its replay check finish. You don't need to come back.
Force: confirm → responsibility reason → final confirm.
```

두 번 확인한 뒤, ETA 없는 경우:

```text
Force queued for #31 queen-hunt: skip the remaining tests and open the candidate automatically when this rebuild and its replay check finish. You don't need to come back. I'll post the result here.
```

같은 유효 ETA가 있는 경우:

```text
Force queued for #31 queen-hunt: skip the remaining tests and open the candidate automatically when this rebuild and its replay check finish (current step done about 19:11 KST). You don't need to come back. I'll post the result here.
```

runner 적용 뒤 원래 요청 스레드에 오는 기존 형식 (요청자 jun, 사유 예시):

```text
✅ Applied set_state to #31.

via /meow by jun
⚠️ forced by jun: local tests were already enough
```

## 테스트 실행 마지막 4줄

unsw-swarm `tools/`에서 `python3 -m unittest discover -p 'test_*.py'`:

```text
----------------------------------------------------------------------
Ran 177 tests in 6.123s

OK
```

**worktree가 아닌 로컬 검증 사본**의 `work/loop/`에서 `python3 -m unittest discover -s tests`:

```text
----------------------------------------------------------------------
Ran 135 tests in 2.713s

OK
```

## 해석과 미확인 사항

- `status.json`의 ETA는 현재 작업 단계의 ETA이므로 전체 rebuild + mechanism/look의 완료 시간은 확정할 수 없다. 안내에 이를 명시했다.
- “현재 base”는 기존 runner의 `base_moved()` 의미를 따른다. main의 문서·도구 변경만으로는 봇 코드의 기준이 바뀐 것으로 취급하지 않는다.
- 기존 controls의 pause/lock 순서를 유지하므로 만료·실패 거부 알림도 controls가 해당 요청을 처리할 수 있는 시점에 게시된다. 6시간을 지난 요청이 이후 적용되지는 않는다.
- 실제 Discord/GitHub 및 실행 중인 runner와의 통합 실행은 하지 않았다. 모든 테스트는 오프라인 fixture/mock을 사용한다.
- 브리프를 완전히 마치려면 지정 worktree를 만들고 패치를 적용한 뒤 그 안에서 전체 테스트를 실행하고 커밋해야 한다. 현재 봇 변경만으로 기능 전체가 배포된 것은 아니다.

## 권한이 있는 터미널에서 남은 작업

아래 명령은 여기서 실행되지 않았다. 네트워크나 push는 포함하지 않는다.

```sh
force_wt='~/.claude/jobs/e3d433df/tmp/force-smooth-wt'
git -C '~/01. Project/개인 프로젝트/battlecode' worktree add -b loop/force-after-build "$force_wt" origin/main
git -C "$force_wt" apply '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/force-smooth-loop.patch'
(cd "$force_wt/work/loop" && python3 -m unittest discover -s tests)
git -C "$force_wt" diff --check
git -C "$force_wt" add work/loop/meow_control.py work/loop/tests/test_force_after_build.py
git -C "$force_wt" -c user.name='juntegral' -c user.email='<email>' commit -m 'Queue forced candidates until their build attempt finishes' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
git -C "$force_wt" rev-parse HEAD
```

테스트가 OK인 것을 확인한 뒤 커밋 명령을 실행한다. 실제 커밋 ID와 worktree 테스트 결과는 그때 이 보고서에 보완해야 한다.
