| 주장 | 계획의 수치·참조 | 독립 확인 수치·참조 | 일치 yes/no | 비고 |
|---|---|---|---|---|
| A1 main 판·패배·버킷 | 400판, 180패; L1 50, E2 43, Q2 30, Q1 21, E1 16, Other 14, Q3 6 | 400판, 180패; L1 50, E2 43, Q2 30, Q1 21, E1 16, Other 14, Q3 6 | yes | 현재 main이 정확히 400판이므로 첫 400판과 동일; summary.md 정의로 직접 분류. |
| A2 r100 ≤6마리 또는 그 전에 전멸 | 77판, 56패 | 77판, 56패 | yes | r100 체크포인트 또는 last_round<100 및 최종 생존 0. |
| A3 A2 중 팀당 2마리 시작 | 66/77 | 66/77 | yes | maps.json의 dragons_at_spawn=2. |
| A4 big/나머지 패배 | 77/127; 103/273 | 77/127; 103/273 | yes | width×height>1200 / ≤1200. |
| A5 big에서 r150 동률 범위 또는 우세 | 패배 40/77; 승리 42/82 | 패배 40/77; 승리 42/82 | yes | r150 존재, 우리 총 길이 ≥ 상대 총 길이×0.8; 결측 제외. |
| A6 패배의 최종 여왕 사망·사인 | 160/180; rammed 120, wall 23, own body 12, another body 5 | 160/180; head-on 120, wall 23, own body 12, other dragon body 5 | yes | rammed는 head-on 사인으로 해석; 공격자·피격자 구분 주장은 아님. |
| A7 Q1 및 우리 최장 엄격 우세 | 21패; 21판 모두 엄격 우세 | 21패; 엄격 우세 21/21 | yes | Q1 분류는 ≥, 실제 21판은 모두 >. |
| A8 big 최장 ≥10 | r150 33/126; r200 91/125 | r150 33/126; r200 91/125 | yes | 해당 체크포인트 존재 판만 분모에 포함. |
| A9 여왕 no action 사망 | 전체 1/295; 패배 0/180 | 전체 1/295; 패배 0/180 | yes | queen.us.death_other=no action; 최종 사망 여왕 295. |
| B1 grow_round | >1200이면 150, 나머지 300; L468 | >1200이면 150, 나머지 300; L468 | yes | L468 `grow_round = aggressive ? LEADER_GROW_ROUND : LEADER_GROW_ROUND_BIG;`; L467 `aggressive = cells <= AGGRESSIVE_MAX_CELLS;`; L91 `constexpr int AGGRESSIVE_MAX_CELLS = 1200;`; L45 `constexpr int LEADER_GROW_ROUND = 300;`; L46 `constexpr int LEADER_GROW_ROUND_BIG = 150;`; L242 `constexpr int LC_LEAD_ROUND = 0;`으로 초기 override 꺼짐. |
| B2 여왕 양보·아군 차단 | GIVE_WAY 0 L195; ALLY_BLOCK false L163 | 0 L195; false L163 | yes | L195 `constexpr int QUEEN_GIVE_WAY = 0;`; L163 `constexpr bool QUEEN_ALLY_BLOCK = false;`. |
| B3 사냥 길이·정보 수명·복수 시작 | MAX_LEN 4; FRESH 20; L1993–2007; 여왕 사망 시 r100부터 | 4 L367; 20 L370; 사용 L1993–2007; r100 L368/L1999 | yes | L367 `constexpr int QH_MAX_LEN = 4;`; L370 `constexpr int QH_FRESH = 20;`; L1993 `bool const small = ct.get_id() > 1 && !is_leader() && length <= QH_MAX_LEN;`; L1994 `bool const fresh = qh_round >= 0 && round - qh_round <= QH_FRESH;`; L368 `constexpr int QH_REVENGE_ROUND = 100;`; L1999 `bool const revenge = qh_queen_dead() && round >= QH_REVENGE_ROUND;`; L2007 `qh_on = target && (qh_hunter || revenge) && qh_reach(qh_pos);` — fresh, 목표 생존, 경로 도달 등의 추가 조건 필요. |
| B4 진주 보너스·리더 구역 벌점 | 300, 600; L5055–5060; 9칸 이내 | 300 L99, 600 L65; 적용 L5055–5059; 반경 9 L57/L2361–2362 | yes | L99 `constexpr double EAT_BONUS = 300.0;`; L65 `constexpr double ZONE_PEARL_PENALTY = 600.0;`; L5056 `score += EAT_BONUS;`; L5059 `score -= ZONE_PEARL_PENALTY;`; L57 `constexpr int LEADER_PEARL_RADIUS = 9;`; L2361–2362 `return torus_gap(cell.x, zone_head.x, width) + torus_gap(cell.y, zone_head.y, height) <= LEADER_PEARL_RADIUS;` — 토러스 Manhattan 거리, 활성 구역; 벌점은 비리더에게 적용. |
| B5 is_leader() | L3328 | L3328–3329 | yes | L3328 `bool is_leader() const {`; L3329 `return round > grow_round && known_leader_id == ct.get_id();`. |
불일치: 없음.
