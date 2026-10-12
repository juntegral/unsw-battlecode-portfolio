# meowbot 승인 → 병합 + 제출 변경 보고

- 작성: 2026-10-03 21:33:26 KST.
- `new_candidates()`는 열린 PR과 변경 파일을 페이지 끝까지 조회한다. main 디렉터리 감지는 교체했다.
- `candidate_pr()` / `pr_candidates()`는 PR head SHA에 고정된 manifest를 읽는다. 삭제 파일·잘못된 JSON·필수값 누락은 제외한다.
- `candidate_embed()`에 실제 PR 링크·head SHA를 넣고 모듈 설명·footer·버튼 문구를 새 흐름으로 바꿨다.
- `CandidateView.approve()`는 MEMBERS에게만 비공개 Confirm/Cancel을 표시한다. Hold의 보류자 기록·후속 승인 허용은 유지했다.
- `CandidateConfirm.confirm()`은 전역 승인 잠금과 일회성 확인으로 중복 클릭을 막는다.
- 열린 상태·main 대상·비초안·mergeable·head SHA를 검사한다. SHA 변경은 거절하고 새 카드를 게시한다.
- `merge_candidate()`는 `gh pr merge N --repo ... --merge --match-head-commit SHA`를 사용하며 실제 병합 완료·커밋을 확인한다.
- 확인 후 `sync_release()` → `upload()` 순서로 실행한다. release 잠금은 분석 작업의 동기화와 겹치지 않게 한다.
- `UPLOAD_ENABLED = False`와 기존 mock 분기는 유지했다. 병합은 실제이며 제출만 mock이라는 점을 확인창·카드·결과에 표시한다.
- `edit_candidate()`는 승인자·병합 커밋·업로드 결과를 카드에 기록하고 버튼을 비활성화한다.

상태 파일 변경:
- 기존 `candidates`와 기타 키를 보존한다. 새 키는 `pr:<번호>:<head SHA>:<파일 경로 해시>`다.
- 새 기록에는 manifest, pr, url, head_sha, path, message_id를 저장한다.
- pending/hold → approving → approved/error; 교체된 카드와 같은 PR의 다른 카드는 stale로 남긴다.
- by, at, merge_commit, result를 저장한다. 진행 중/오류 기록은 재시작 때 자동 재실행하지 않는다.
- 예전 main 카드 기록은 남기되 승인 시 새 PR 카드를 안내한다. 실제 state.json은 건드리지 않았다.

오프라인 검증:
- `python3 -m py_compile tools/meowbot.py`, `git diff --check` 통과.
- `--preview-candidate`와 `--help` 실행 통과; `--preview-candidate-pr 12`는 가짜 gh 응답으로 출력 검증.
- `/tmp/preview_meowbot_approval.py`: 15개 검사 통과. 페이지 처리·중복 감지·권한·취소·보류·병렬 클릭·SHA 변경·병합 불가·오류·mock/실제 업로드 분기를 검증했다.
- GitHub/Discord/병합/제출은 전부 대역 처리했다. 봇 시작·재시작·종료, 실제 병합·제출·push·커밋, 비밀 파일 접근은 없었다.

남은 위험:
- 실제 GitHub 권한·보호 규칙·Discord 상호작용은 검증하지 않았다. merge queue에 들어간 경우 업로드하지 않고 수동 확인 대상으로 남긴다.
- 승인 잠금은 단일 봇 프로세스 기준이다. 중단·응답 유실·카드 수정 실패는 저장된 상태와 원격 상태를 수동 대조해야 한다.
- main이 외부에서 추가로 갱신되면 기존 동기화 방식대로 최신 origin/main을 제출한다.
- 변경은 미커밋 상태이며, 실행 중인 봇에는 적용하지 않았다.
