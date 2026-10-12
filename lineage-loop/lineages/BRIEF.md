# UNSW Battlecode

**니가 생각하기에 최적의 로직을 작성해와.**

## 규칙 (전부 읽어라)
- `rules/ALL.md`: 공식 문서 22쪽 전체 저장본(2026-09-27, 와이어 프로토콜 3.0.0: 음파 반향 ECHOES, 64비트 음파, `PROTOCOL 3` 옵트인). 페이지별 파일도 `rules/`에 있다. 의심스러우면 https://game.battlecode.au/docs/ 최신판을 직접 읽어 확인한다(읽기만).
- `rules/judge-limits.md`: 심판 한도(unswbc 1.1.0). 드래곤당 턴당 100,000,000 CPU points, 메모리 48MB, 턴당 CPU 1초·벽시계 10초. 넘으면 그 턴 응답이 없고 그 드래곤은 죽는다.

## 환경
- 공식 도구 1.1.0(현재 심판과 같은 판): `lineages/_tools/unswbc` (`init`, `run <map> <botA> <botB> --sandbox [--seed N]`, `help`). `unswbc init cpp <dir>`가 최신 헬퍼를 준다. 언어는 자유(C/C++/Python).
- 지도: `maps/online-20260927/`(현재 온라인 지도 풀 10개), `maps/bundled/`(도구에 들어 있는 지도 13개).
- 로컬 상대(블랙박스로 실행만, 소스는 읽지 말 것): `bots/replay_rules_v8`(이전 서버 봇), `bots/archetype_swarm`, `bots/archetype_hunter`, `bots/h2`.
- 표준 평가기: `lineages/_tools/eval.js`. G는 공식 리플레이의 최종 상태에서 살아남은 우리 최장 드래곤 길이(전멸 0). 기본 시드 1,2의 반복 벤치마크는 탐색 자료이지 새 확인 자료가 아니다.

## 작업 방식
- 네 폴더: `lineages/<네 이름>/`. 봇은 `lineages/<이름>/bot/`(항상 네 최선 버전). 그 밖은 수정하지 않는다.
- 다른 `lineages/` 폴더와 `bots/`의 소스는 읽지 않는다. 처음부터 네 생각으로 설계하기 위해서다.
- 탐색 경기는 `node loop/run-job.js <이름> -- <평가 명령과 인자>`로 실행한다. 명령 안에서 동시 2개 이하, 자식 작업을 분리하지 않고 완료까지 기다린다. 공통 큐는 등록된 평가 배치를 한 번에 하나만 실행한다. 디스크 여유 20GB 미만이면 새 경기를 시작하지 않는다.
- 채택·기록·버전 커밋은 `LOOP.md`의 종료 절차를 따른다. `ready` 한 줄만으로는 export하지 않는다.
- 온라인 대전 기록은 `lineages/<이름>/logs/online/<배치>/`에 들어온다(game json, 공식 replay, `events-<id>.jsonl.gz` 전체 이벤트). 참고 정보이며 목표가 아니다.
- `CURRENT.md`에는 현재 최선과 근거 경로, 진행 중인 가설·실험 경로·다음 확인만 짧게 덮어쓴다. `NOTES.md`에는 결과와 판단을 누적한다. 과거의 Next·추측은 현재 명령이나 확정 사실이 아니다.
