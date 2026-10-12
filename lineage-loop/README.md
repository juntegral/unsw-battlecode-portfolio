# unsw-arena — 무한 개선 루프 작업장

UNSW Battlecode 봇을 계통(lineage)별로 끝없이 개선하는 저장소. Orca(또는 그냥 터미널)에서 계통마다 Claude Code 웨이브 루프를 돌린다.

## 구성
- **연구(이 저장소):** `loop/run-lineage.sh <이름>`이 새 문맥을 반복 실행한다. 현재 상태는 `CURRENT.md`, 과거 근거는 `NOTES.md`와 원자료에 분리한다. 탐색과 채택 전 확인을 나누며 채택·기각·미완료를 구분한다. 채택 버전과 남은 실험 이력은 각각 커밋한다. worktree의 기록을 `main`에 반영하려면 별도 병합이 필요하다.
- **배관(저장소 밖, AI 없음):** `UNSW/lineages/_daemon/plumber.js`가 3분마다 새 배포 스냅숏을 스모크·표준 벤치마크하고 서버에 제출한다. 새 온라인 대전은 요청하지 않으며, 기존 요청분의 기록만 수집한다. 활성 제출본에 대한 서버의 자동 매칭은 별도로 발생할 수 있다.
- **공유 데이터:** `~/01. Project/개인 프로젝트/unsw-arena-data` (`releases/`, `logs/<계통>/online/`, `eval/`). 저장소의 `lineages/_releases`, `lineages/_eval`, `lineages/<계통>/logs`는 여기로 가는 링크라 모든 worktree가 같은 데이터를 본다.
- **근거:** `lineages/<계통>/checks/*/`에 코드·조건·확인 원자료·보고서가 남는다. `waves/last.json`은 실행 결과, `lineages/_eval/PROGRESS.md`는 외부 데몬이 완료한 표준 벤치마크만 보여준다. 웨이브 횟수나 `ready` 번호 자체는 성장의 증거가 아니다.

## 처음 한 번
1. Claude Code 설치·로그인: `npm install -g @anthropic-ai/claude-code` → `claude` 실행 → Max 계정 로그인 → 종료.
2. (선택) 공식 도구 설치: `uv tool install unswbc==1.1.0`. 없으면 `lineages/_tools/unswbc`가 UNSW 프로젝트의 설치본을 쓴다.
3. Aside에서 돌던 계통을 가져오기: `scripts/sync-from-unsw.sh` → 그다음 **Aside에 "g1, g2 감시 루틴 멈춰줘"**라고 한다(같은 계통을 두 곳에서 동시에 고치지 않도록).
4. 배관 데몬이 안 돌고 있으면 터미널에서: `"~/01. Project/개인 프로젝트/UNSW/lineages/claude-code/start-plumber.command"` (중복 실행은 스스로 거부).

## Orca에서
1. 이 폴더를 저장소로 추가한다.
2. 계통마다 worktree를 하나씩 만든다(예: `lineage-g1`, `lineage-g2`, 새 설계면 `lineage-g3`).
3. 각 worktree 터미널에서 `caffeinate -i loop/run-lineage.sh g1` 처럼 실행한다. 기존 `bot/`이 있으면 그 코드가 시작점이다. 봇이 없는 새 계통만 규칙서에서 기반 설계를 시작한다. 여기의 g1·g2는 UNSW/Aside에서 가져온 기존 봇으로 시작했다.
4. 멈추기: 그 worktree의 새 터미널에서 `touch lineages/g1/STOP`. 현재 웨이브와 등록된 평가가 끝나면 멈춘다. 다시 시작할 때는 종료를 확인하고 `rm lineages/g1/STOP` 후 실행한다.

## 그냥 터미널에서
```bash
cd "~/01. Project/개인 프로젝트/unsw-arena"
caffeinate -i loop/run-lineage.sh g1     # 창 1
caffeinate -i loop/run-lineage.sh g2     # 창 2
```

## 주의
- 실행 중인 구형 Bash 루프는 파일 수정만으로 전환되지 않는다. STOP으로 웨이브 종료를 기다리고 남은 로컬 경기가 없는지 확인한 뒤, 공통 문서·도구를 함께 업데이트하고 재시작한다. 봇·NOTES·Git 기록은 지우지 않는다. CURRENT.md가 없으면 첫 새 웨이브에서 한 번 복원한다.
- 운영자용 자동 전환: `node loop/activate-after-wave.js schedule <worktree 절대경로> <계통> <기존 루프 PID> <공통 변경 commit>`. 기존 웨이브·잔여 로컬 작업을 기다려 공통 파일만 반영·커밋하고 재시작한다. 예약 후 공통 파일이나 STOP이 바뀌면 덮어쓰거나 임의 재시작하지 않는다. 상태는 공유 데이터의 `control/handoffs/*/plan.json`, 새 터미널 출력은 해당 계통의 `waves/runner.log`.
- 모델: 기본 `claude-opus-5-5`, 오류·거절 시 아직 판단을 완료하지 않았고 기존 봇이 유지된 경우 같은 웨이브를 `claude-fable-5`로 재시도한다. `loop/run-lineage.sh g1 <모델> <대체모델>` 또는 `UNSW_MODEL`, `UNSW_FALLBACK_MODEL`로 변경한다.
- 같은 공유 데이터 폴더를 쓰는 새 실행기는 계통 중복 실행을 막고, 등록된 로컬 평가를 한 배치씩 처리한다(배치 내부 동시 2판 이하). 기존 Aside 작업·외부 데몬·도구를 우회한 직접 실행은 이 큐 밖이므로 별도 조율이 필요하다.
- 확인 도구는 현재 10개 지도·4개 상대·양 진영에서 새 시드 2개를 사용한다(후보와 기존 최선 각각 160판). 코드·조건을 고정하며 수치에 의한 자동 승격 기준은 두지 않는다. 같은 지도·상대 풀의 한계와 반복 선택 편향까지 없어진 것은 아니다.
- `--dangerously-skip-permissions`로 확인 없이 도구를 실행한다. 규칙(서버·API 키·다른 폴더 금지)은 `CLAUDE.md`와 프롬프트로 지켜진다.
- 맥북 잠자기 중에는 루프·데몬이 멈춘다(전원 연결 + `caffeinate`).
- 웨이브 기록: `lineages/<계통>/waves/`(git 제외).
- 로컬 구조 테스트: `node --test loop/test/runtime.test.js`(가짜 실행기·평가 사용; 실제 경기·Claude·서버 호출 없음).
