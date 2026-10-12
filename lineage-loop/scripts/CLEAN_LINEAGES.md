# g3·g4 Orca 하위 워크트리 운영

2026-09-28 사용자 요청에 따라 g1·g2를 종료·아카이빙하고, 검증한 공통 거푸집에서 g3·g4를 시작했다. 최초에는 독립 Git 저장소였으나 Orca의 `unsw-arena` 프로젝트 안에서 `main`의 하위 워크트리로 보이도록 같은 Git 저장소로 이관했다. 기존 독립 저장소 폴더와 Orca 등록은 검증 후 삭제했다.

## 현재 위치

- g3: `~/orca/workspaces/unsw-arena/g3`, 브랜치 `lineage-g3-clean`.
- g4: `~/orca/workspaces/unsw-arena/g4`, 브랜치 `lineage-g4-clean`.
- 두 브랜치의 시작 커밋에는 부모가 없으므로 이전 코드가 체크아웃되지 않는다. Git object 저장소 자체는 `unsw-arena/.git`으로 공유된다.
- g1·g2·seed0 아카이브: 프로젝트 상위의 `unsw-arena-archive/legacy-20260928/{g1,g2,seed0}`. 연구 프로세스는 접근할 수 없다. 원자료와 최종 Git 번들을 파일별 해시로 검증했다.
- 기존 세 워크트리는 2026-09-28 Orca와 로컬 Git에서 제거했다. Git 브랜치 `g1-lineage-wave-improve`(22b1b83), `g2-lineage-wave-improve`(d7012f3), `seed-foundation`(f8a184d)는 GitHub `origin`에 푸시했고 로컬 브랜치도 남겨 두었다. Git에서 제외된 원자료는 위 격리 아카이브에 보존한다.
- 평가 원자료·캐시·로그: 각 워크트리의 `.arena-data/`와 `lineages/<이름>/`에 보존. 두 계통은 `unsw-arena-clean-control/`의 잠금·작업 상태만 공유한다.

## 격리와 실행

각 워크트리의 `.isolation/launch.sh`는 Git 커밋·검증을 담당하는 신뢰 실행기를 시작한다. 그 실행기가 연구용 Claude와 Bash·평가 자식 프로세스를 macOS Seatbelt 안에서 시작한다. 연구 프로세스에서는 공용 `.git`, 다른 워크트리, 과거 아카이브·독립 저장소, 기존 대화·메모리 자료의 읽기를 차단한다. 자기 연구 파일은 수정할 수 있고 공통 규칙·도구·상대 실행 바이너리는 읽기 전용이다. 이 규칙은 과거 UNSW 자료와 알려진 세션 경로를 대상으로 한 격리이며 사용자 홈 전체의 파일 접근을 차단하는 정책은 아니다. 프롬프트에서도 다른 계통과 공용 Git 이력을 읽지 말라고 지시하지만, 검증한 핵심 경계는 실제 파일 접근 차단이다.

Claude는 safe mode, 세션 저장 비활성화, 빈 MCP 구성, 자동 메모리 비활성화로 시작한다. 두 워크트리에서 실제 초기화 응답의 외부 스킬·MCP 서버가 비어 있음을 확인했다. 사용 가능한 상대는 컴파일된 WASM뿐이다. 서버 업로드와 API 키 사용은 금지되며 이 루프는 제출 데몬과 연결되지 않는다.

연구 프로세스의 `node loop/runner.js finish`는 종료 요청만 기록한다. 샌드박스 밖의 신뢰 실행기가 원자료·고정 조건·봇 해시를 다시 검증하고 버전 커밋·배포 스냅숏을 만든다. 이 분리 덕분에 연구 프로세스에 공용 Git 이력을 열어주지 않는다.

## 재개와 중지

- 운영 상태: `node scripts/seed-transition.js status`; 짧은 상태: `node scripts/seed-transition.js brief`.
- 진행 중인 g3·g4 웨이브와 확인 평가 진행률: `node scripts/loop-watch.js` (`--json` 지원). 이 명령은 읽기만 한다.
- g3의 중단 지점은 `w000002`, 현재 재개 웨이브는 `w000003`. g4의 중단 지점은 `w000003`, 현재 재개 웨이브는 `w000004`.
- 각각의 `lineages/<이름>/RESUME.md`와 `PAUSED.json`에 중단 작업·봇·원자료 해시가 있다. 이관 시 원본의 파일 체크섬, 봇 해시, 평가 행, 유효한 확인 보고서의 원자료 집계를 검증했다. 미완료 확인은 같은 후보·시드·조건으로 남은 행만 이어간다.
- 중지: 해당 워크트리에서 `touch lineages/<이름>/STOP`. 현재 평가를 마친 뒤 실행기가 종료한다.
- 재개: STOP을 제거하고 해당 워크트리의 `.isolation/launch.sh`를 시작한다. 연구 에이전트를 Orca의 일반 세션에서 직접 실행하면 이 격리 검사를 거치지 않는다.

공식 1.1.0 C++ 빌드 캐시는 헤더 변경을 키에 포함하지 않는다. `scripts/clean-unswbc.py`는 전체 입력 해시로 독립 소스 디렉터리를 만든 뒤 공식 컴파일러를 호출한다. 최초 seed0 확인은 중단 전 66판 이후 동일한 코드·지도·상대·시드로 나머지 경기만 이어서 160판으로 완료했다. 근거는 `lineages/seed0/CLEAN_START_VALIDATION.md`와 `TRANSITION.md`에 있다.

## 웨이브 모델·워크플로우 (2026-09-28)

- 웨이브 모델은 각 워크트리 `.isolation/launch.sh`의 `UNSW_MODEL`(현재 `claude-fable-5-1`)과 `UNSW_FALLBACK_MODEL`(`claude-opus-5-5`)이 정한다. `loop/runner.js`의 기본값은 `claude-opus-5-5`이므로 이 두 줄을 지우면 Opus로 돌아간다. 효과는 웨이브 로그 첫 줄의 `model`로 확인한다.
- 연구용 Claude의 도구 목록에 `Workflow`가 있다(`loop/runner.js`의 `--tools`). 웨이브 프롬프트가 `loop/WORKFLOW.md`의 세 지점(가설 패널, 구현 검토, 채택 전 반박)에서 워크플로우를 실행하라고 지시한다. 헤드리스 `-p` 세션은 워크플로우 완료 알림을 기다린 뒤 이어간다(2026-09-28 샌드박스 안에서 확인).
- `--tools`·프롬프트·launch.sh 변경은 실행기 재시작 후 다음 웨이브부터 적용된다. `wave-prompt.md`와 `lineages/LOOP.md`는 웨이브마다 새로 읽는다.
- 사용량 한도: 웨이브 로그의 `rate_limit_event`에 5시간·7일 창의 사용률이 있다. 초과 사용(overage)이 조직 수준에서 꺼져 있으면 창이 차는 순간 웨이브가 실패·재시도만 반복한다.
