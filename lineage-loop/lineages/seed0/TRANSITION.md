# 공통 거푸집 전환 — 2026-09-28

상태: continuous-running; 갱신: 2026-09-28T05:39:18.398Z

## 기존 계통

- g1: 종료·보존. 마지막 w000005 / incomplete, commit 60cb401c65c6ec428a0614d0dae613bc7797ae09. STOP 유지.
- g2: 종료·보존. 마지막 w000018 / incomplete, commit 7bac8c45cc5a71262c4e7b40a304c2d95323bd05. STOP 유지.

- 독립 아카이브 g1: ~/01. Project/개인 프로젝트/unsw-arena-archive/legacy-20260928/g1
- 독립 아카이브 g2: ~/01. Project/개인 프로젝트/unsw-arena-archive/legacy-20260928/g2

## 공통 기준선

- seed0 r1: f8549ac8f85ba00c492c7a4ac5131a3113fcde17bfe7a0673b3632dd968228c3; 근거 ~/01. Project/개인 프로젝트/unsw-arena-seed/lineages/seed0/checks/w000001-b87f9a4e/report.json.

## 새 계통

- g3: ~/orca/workspaces/unsw-arena/g3; 초기 해시 f8549ac8f85ba00c492c7a4ac5131a3113fcde17bfe7a0673b3632dd968228c3.
- g4: ~/orca/workspaces/unsw-arena/g4; 초기 해시 f8549ac8f85ba00c492c7a4ac5131a3113fcde17bfe7a0673b3632dd968228c3.

- g3 최초 독립 저장소 격리 검사: 통과 (9개).
- g4 최초 독립 저장소 격리 검사: 통과 (9개).

- g3 Orca 하위 워크트리: ~/orca/workspaces/unsw-arena/g3, lineage-g3-clean, 이관 커밋 9a45afba2d770d6ddf6358fae7fd7a84c61613f8; 중단 시점 봇 9a52dd40a7573aa312a5602a3dfe5e2096fb2dcb11ea7cce5bd77cb8878db486, 평가 원자료 18개 해시 검증. 이전 독립 저장소 삭제.
- g4 Orca 하위 워크트리: ~/orca/workspaces/unsw-arena/g4, lineage-g4-clean, 이관 커밋 f22de254d2818d0a481a38745b1557583dfec2ec; 중단 시점 봇 fedc52d9476f59c1ccd430745d11c9306abe9d36eaa05a696416494acff5e7e0, 평가 원자료 22개 해시 검증. 이전 독립 저장소 삭제.

## 첫 웨이브

- g3: w000001, adopt, exit 0, commit 6cfd1e2dc7abb2d4a858a6abd5a58b71623202bc. 확인 근거: ~/01. Project/개인 프로젝트/unsw-arena-g3/lineages/g3/checks/w000001-fb489383/report.json.
- g4: w000001, adopt, exit 0, commit a4359d9da193cc94823c225903318dd08b3e1983. 확인 근거: ~/01. Project/개인 프로젝트/unsw-arena-g4/lineages/g4/checks/w000001-3c2d9a28/report.json.

## 연속 실행

- g4: PID 32644, 로그 ~/orca/workspaces/unsw-arena/g4/lineages/g4/waves/runner.log.
- g3: PID 32643, 로그 ~/orca/workspaces/unsw-arena/g3/lineages/g3/waves/runner.log.

- g3 지난 중단 기록: ~/orca/workspaces/unsw-arena/g3/lineages/g3/RESUME.md; r2, w000002 미완료, 당시 commit 939cb3ef6d33606464a8bb39406adf3d6318f192.
- g4 지난 중단 기록: ~/orca/workspaces/unsw-arena/g4/lineages/g4/RESUME.md; r2, w000003 미완료, 당시 commit e07d8ece6fde820852a7bd3802f499a687209f10.
- g3 재개 웨이브: w000003.
- g4 재개 웨이브: w000004.

각 계통은 자기 첫 웨이브의 검증이 끝나면 독립적으로 연속 실행을 시작한다. 결과·캐시·배포 사본은 각 저장소에만 저장하며, 기존 서버 제출 데몬과 연결하지 않았다.

중지는 해당 저장소에서 touch lineages/<이름>/STOP. 현재 웨이브와 등록된 평가가 끝난 뒤 종료한다.

격리·아카이브·초기 기준선의 검증 근거: CLEAN_START_VALIDATION.md.

운영 상태 파일: ~/01. Project/개인 프로젝트/unsw-arena-data/control/seed-transition-20260928/state.json

## 워크트리 정리 (2026-09-28)

g1·g2·seed0 최종 상태를 각각 `g1-lineage-wave-improve`(22b1b83), `g2-lineage-wave-improve`(d7012f3), `seed-foundation`(f8a184d)으로 커밋·푸시했다. 세 브랜치의 원격 해시를 대조했다. Git에서 제외한 원자료는 `unsw-arena-archive/legacy-20260928/{g1,g2,seed0}`에 별도로 보관하고 원본과 파일별 SHA256을 대조했다. 세 작업 폴더는 Orca와 Git의 워크트리 목록에서 제거했다. 위 과거 경로는 당시 작업 기록이며 현재 활성 경로가 아니다.

현재 활성 작업은 `unsw-arena → main` 아래 g3·g4뿐이다. 진행률 확인: `node scripts/loop-watch.js`.
