# 래더 지도 6개

정확히 일치하는 기존 .map을 우선 탐색했다. 없으면 기보의 전체 시작 지도 헤더를 그대로 추출했다. 셀 수는 전체 격자 기준이다.
각 지도는 엔진 1.2.7 WASM 로더로 초기화하고 첫 행동 요청에서 중단했다(행동 0).
검증은 서로 다른 두 래더 기보의 r0와 대조했다. 아래 S/W/P/D/T는 크기/벽/포털 쌍/양팀 전체 몸/진주 생성 타일이다.
전체 변(켈프·랩 경계 포함), SYMMETRY도 모두 equal. A/B와 id 순서까지 같은 기보 두 개를 선택했다.
상세 기보 경로·항목별 결과·해시는 `checks.json`, 재검증은 지정 venv로 `python3 -B verify_maps.py`.

| 지도 파일 | 크기 | 셀 | A/B 마리 | 원본 | 두 기보 S/W/P/D/T |
|---|---:|---:|---:|---|---|
| ladder_islands_1.map | 56×40 | 2240 | 5/5 | ~/01. Project/개인 프로젝트/unsw-swarm/data/online/ladder/1241400/M1241403.replay | equal/equal/equal/equal/equal ×2 |
| ladder_australia_1.map | 64×64 | 4096 | 9/9 | ~/01. Project/개인 프로젝트/unsw-swarm/data/online/ladder/1233593/M1233597.replay | equal/equal/equal/equal/equal ×2 |
| ladder_around_unsw_1.map | 64×64 | 4096 | 10/10 | ~/01. Project/개인 프로젝트/unsw-swarm/data/online/ladder/1182278/M1182281.replay | equal/equal/equal/equal/equal ×2 |
| ladder_slithery_fight_1.map | 63×27 | 1701 | 7/7 | ~/01. Project/개인 프로젝트/unsw-swarm/data/online/ladder/1240735/M1240739.replay | equal/equal/equal/equal/equal ×2 |
| ladder_schooltime_1.map | 60×40 | 2400 | 3/3 | ~/01. Project/개인 프로젝트/unsw-swarm/data/online/ladder/1240151/M1240152.replay | equal/equal/equal/equal/equal ×2 |
| ladder_schooltime_2.map | 60×40 | 2400 | 3/3 | ~/01. Project/개인 프로젝트/unsw-swarm/data/online/ladder/1243018/M1243021.replay | equal/equal/equal/equal/equal ×2 |

형식과 재현 한계:
- TILE의 두 값은 생성 간격 min/max다. 고정 주기·위상이나 기보의 RNG 상태/실제 첫 생성 카운트다운은 저장하지 않는다.
- 켈프는 EDGE kind 1, 포털은 kind 2와 연결 id, 랩은 격자 경계 변으로 보존된다.
- UNIT_LIMIT는 형식에서 지원한다. 원본과 기보에는 명시가 없으며 엔진 초기화에서 확인한 기본값은 [64]이다.
- 라운드 상한은 지도 항목이 아닌 엔진 상수 MAX_ROUNDS=500이다(문서 helper.hpp).
- MAP_NAME과 SYMMETRY는 원본 그대로다. 서버 map_version, 팀 이름/봇, 시드는 지도 형식의 항목이 아니다.
