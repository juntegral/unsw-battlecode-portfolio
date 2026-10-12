# Replay padding 작업 보고

작성 시각: 2026-10-05 23:31:53 KST

## 완료한 변경

unsw-swarm에는 `tools/replay_fix.py`와 `tools/test_replay_fix.py`를 추가했다. 진단 스크립트의 packed Cap’n Proto unpack/pack과 Text 포인터 보정 로직을 자체 구현했다. 빈 수평 패딩 EDGE를 제거하고 EDGE_COUNT와 Text byte-list 길이를 고친다. 세그먼트 크기·위치는 유지하며 남은 공간은 0으로 채운다. 수정할 것이 없거나 파싱에 실패하거나 패딩이 비어 있지 않으면 원본 bytes를 반환한다. 예외를 호출자에게 전달하지 않는다.

`tools/meowbot.py`의 look 첨부 파일 읽기에서만 `strip_padding`을 호출한다. 보정 후 기존 크기 확인과 gzip 처리, 첨부 전송을 그대로 수행한다. 첨부 테스트로 보정 순서, gzip 여부, 원본 파일 불변을 확인했다.

지정 실제 생성 지도 기보는 scratch의 fixed_all 보정본과 바이트 단위로 일치했다. 지정 공식 지도 기보는 바이트 단위로 불변이었다. 두 fixture가 모두 존재하여 skip하지 않았다. 합성 테스트는 Text 길이와 tail zeroing, 양·음 near pointer, 여러 세그먼트, 잘린 packed 입력, 비어 있지 않은 패딩, 재적용 불변을 확인한다.

## battlecode: 변경 준비 및 검증 완료, worktree/커밋 미완료

원본 checkout의 작업 파일은 수정하지 않았다. 네트워크 없이 로컬 `origin/main` (`1ca2d295a2eceb4235346ea9c209edb075d232af`)에서 테스트용 사본을 추출했다.

준비한 변경은 다음과 같다.

- `work/mkgen.py`: 수평 패딩 슬롯을 출력하지 않고 EDGE_COUNT에서 H+1을 뺀다.
- `work/loop/jobs.py`의 `transpose()`: 구 padded count와 새 real-edge count를 모두 읽고 실제 EDGE 개수도 확인한다. 출력 패딩을 생략하고 count를 수정한다.
- `work/loop/tests/test_padding_edges.py`: 변경 전 생성 지도 fixture와 셀별 사방 벽·포털, 타일, 드래곤이 같음을 확인한다. 모든 생성 스타일의 패딩 부재, 구·새 형식 전치, 비대칭 포털의 좌표 변환, 전치 왕복, 잘못된 포털·count 거부를 확인한다.
- `work/loop/tests/legacy_generated_padding.txt`: 변경 전 origin/main 생성기를 메모리에서 실행해 얻은 `gen_rooms_small_1001`의 새 테스트 fixture다. 기존 지도 파일을 재생성하거나 덮어쓰지 않았다.
- `work/loop/tests/test_runner.py`: 기존 전치 왕복 테스트의 기대 출력을 새 clean 형식으로 수정했다.

검증 사본: `~/.claude/jobs/e3d433df/tmp/padding-prep`

적용용 패치: `~/.claude/jobs/e3d433df/tmp/replay-padding-battlecode.patch`

원본 checkout에서 `git apply --check`는 통과했다. 실제 적용은 하지 않았다.

요청 branch: `tools/no-padding-edges` — **생성되지 않음**.

요청 worktree: `~/.claude/jobs/e3d433df/tmp/padding-wt` — **생성되지 않음**.

Commit ID: **없음**. unsw-swarm에도 커밋하지 않았다. push하지 않았다.

worktree 생성 명령은 다음 오류로 실패했다.

```text
fatal: cannot lock ref 'refs/heads/tools/no-padding-edges': unable to create directory for .git/refs/heads/tools/no-padding-edges
```

현재 파일시스템 권한에서 battlecode `.git`은 읽기 전용이고 권한 상승은 허용되지 않는다. 사용자에게 아래 명령을 터미널에서 실행하도록 요청했다. 생성 후에는 준비된 패치를 지정 worktree에 적용하고 그곳에서 전체 테스트를 다시 실행해야 한다. 커밋도 동일한 `.git` 쓰기 권한이 필요하다. 커밋 메시지는 영어이며 마지막 줄에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`을 포함해야 한다.

```sh
git -C '~/01. Project/개인 프로젝트/battlecode' worktree add -b tools/no-padding-edges ~/.claude/jobs/e3d433df/tmp/padding-wt origin/main
```

## 테스트의 마지막 4줄

unsw-swarm `tools/`에서 `python3 -m unittest discover -p 'test_*.py'`:

```text
----------------------------------------------------------------------
Ran 184 tests in 9.839s

OK
```

임시 검증 사본 `padding-prep/work/loop/`에서 `python3 -m unittest discover -s tests`:

```text
----------------------------------------------------------------------
Ran 126 tests in 2.276s

OK
```

두 번째 실행은 지정 worktree의 실행이 아니다. 그 체크와 branch 커밋이 남아 있으므로 브리프 전체 완료로 판정하지 않는다.

## 확인 범위와 불확실성

실제 사이트 viewer는 네트워크 금지 때문에 열지 않았다. 사이트 호환성은 진단 보정본과의 바이트 동일성과 패딩 제거 테스트로 확인했다. 진단 로직처럼 Text가 같은 세그먼트의 near byte-list pointer로 연결된 replay를 보정하며, 지원하지 않는 형태는 원본 그대로 반환한다. gzip 입력 처리는 브리프대로 제공하지 않는다.

기존 지도·기보 파일, 원본 battlecode checkout, 기존 다른 작업 변경은 건드리지 않았다. 비밀 파일은 읽지 않았고 네트워크 호출, 봇·운영 loop runner 시작/중지/재시작을 하지 않았다. DECISIONS.md에는 실제 시각의 결과만 추가했다. 이 보고서를 마지막으로 작성했다.
