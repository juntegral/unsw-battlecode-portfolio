1. [E] 가장 위험한 정책 경계: 600칸 여왕 역할 차등 → `QUEEN_MIN_CELLS:0`. [C] L5682·1665–1686·3209–3212: 작은 개방 지도는 `queen_game`을 스스로 켜지 못해 여왕 우선 먹이기를 놓칠 수 있다. [E] 크기 차등을 없애지만 작은 포털 지도에도 일반 포털 금지가 확대되므로 검증 없는 적용은 권하지 않는다.
2. [E] 중앙이 유리하다는 크기·방향 가정 → `CENTER_PULL:0`. [C] L611–614·7760–7763: 700/1000칸·가로세로비 2·r30/60 경계의 고정 중앙 유도를 제거한다. [E] 비대칭 시작·막힌 중앙·복도 지도에 유리할 수 있으나 중앙 미탐색 대체 유도도 함께 꺼진다.
3. [E] 1200칸 초과 시 성장 전환이 150턴 빨라짐 → `LEADER_GROW_ROUND_BIG:300`. [C] L605–606·2304·5674–5678: 큰 지도도 기본 성장 전환 r301로 통일한다. [E] 거대하고 진주가 드문 지도에서 미개척 상태의 조기 분열 억제를 완화하지만 여왕 성장 시작도 늦출 수 있다.

[C] 대상은 `data/online/smoke/one17-bot/main.cpp`와 인접 `helper.hpp`다. 이하 `L`은 main.cpp 줄, `H`는 helper.hpp 줄이다. 실제 시각 2026-10-09 13:48:09 KST에 읽은 소스 SHA-256: `1143e97efa733a5110bb984bab93b62dbf679bef685d38b832c4982234025042`. 선언값과 사용 줄 전체는 `inventory.json`에 있다. 표의 동작은 [C], 실패할 지도 유형은 [E]이며 성능 순위와 변경안도 추론이다.

[C] `is_queen()`은 600칸/닫힌 집 조건을 사용하지만 `real_queen()`, `queen_wary()`, `dead_queen()`, `queen_aloof()`는 현재 모든 크기의 실제 여왕에 적용된다(L5681–5687·6105–6115). 따라서 “작은 지도에서 여왕 보호 전체가 꺼진다”는 해석은 틀리다. `QUEEN_NO_BLIND_PORTAL`도 크기 조건 없이 실제 여왕에 적용하며, 비상 탈출은 별도 경로다.

[C] 별도의 구조적 한계: 한 변이 129칸부터 **모든 음파 수신·송신이 중단**된다(L604·3234–3237·3279–3280). [E] 거대 지도에서는 우선 확인할 위험이다. `SONAR_COORD_MAX:255`만 바꾸면 7비트 좌표·14비트 셀 포맷이 부족하므로 안전한 한 상수 수정이 아니다(L3005–3008·3131–3132·3930·3988). 이 한계는 위 세 가지 정책 수정으로 해결되지 않는다.

[C] 경계는 조건식의 정확한 `>`/`>=` 기준이다. `observe()`의 먹이기·리더 계산이 `act()`의 `queen_game` 설정보다 먼저라 새 플래그의 일부 효과는 다음 관측까지 늦을 수 있다(L1642·1665–1686·2838–2854). `N`은 전체 아군 수, `A/E`는 시야 내 다른 아군/적 머리 수, `L`을 수식에서 사용하면 자기 길이다. 전역 포털 개수에 따른 정책은 없고, 아래는 포털 하나의 존재/출구 관측에 따른 분기다.

**전체 지도 크기·형상 및 국소 영역 크기**

| 상수·현재값 | [C] 정확한 전환 / 사용 줄 | [E] 잘못 맞을 수 있는 미지 지도 |
|---|---|---|
| `QUEEN_MODE=true`, `QUEEN_MIN_CELLS=600` | 셀 수 >600 또는 `home_closed`일 때만 실제 여왕이 `is_queen()`; 일반 분열 중단·일반 포털 금지·조용한 경기 전환 등에 사용. L5681–5687, 2285, 6064–6069, 1665–1686 | ≤600 개방 지도에서는 실제 여왕이 경제·분열 역할상 일반 유닛 취급; >600 포털 의존 지도에서는 반대로 일반 포털 접근 억제 |
| `QUEEN_HOME_CLOSED=true`, `HOME_MIN_CELLS=40`, `HOME_MAX_FRAC=0.5` | 알려진 OPEN 간선 연결 성분이 40 이상, `floor(0.5*cells)` 이하이면 `home_closed`, `queen_game` 영구 설정. UNKNOWN 간선 하나라도 검사하면 실패; 포털은 경계로 취급. L1665–1670, 6556–6584 | 39칸의 풍부한 안전 섬은 제외; 40칸의 빈 복도·포털 침입 가능한 방은 안전한 집으로 오인; 비대칭 큰 시작 방은 반쪽 기준 탈락 |
| `AGGRESSIVE_MAX_CELLS=1200` | ≤1200 aggressive; 성장 시점·교환 최소 병력·램 최대 걸음·병력 부족 판정이 함께 바뀜. L605–606, 4547–4556, 4612, 5674 | 같은 면적의 긴 복도와 광장, 작은 고립 섬과 큰 중앙 전장에 같은 정책 적용. `TRADE_EVEN=true`라 worth 분기의 aggressive 효과는 현재 가려짐 |
| `CENTER_MAX_CELLS=1000`, `CENTER_SMALL_CELLS=700` | 중앙 유도는 ≤1000이며 `(가로가 긴 지도 또는 ≤700)`일 때만 활성. L611–614 | 700/701, 1000/1001 사이에서 중앙 지형과 무관하게 정책 변화; 빈 중앙·적 시작점 쪽 중앙 |
| 형상 리터럴 `width >= 2*height`, `TR_CENTER_ORIENT=false` | 가로로 긴 경우만 long_map. 세로로 돌리면 700 초과 지도에서 중앙 유도 사라지고, 이하에서도 시간·병력 조건이 달라짐. L611–614 | 회전만 다른 복도 지도; 비대칭 시작. 면적과 형상은 접근 가능한 중앙을 보장하지 않음 |
| `SONAR_COORD_MAX=127` | width,height 모두 ≤128일 때만 음파 활성. 한 변 >128이면 전체 송수신 중단. L604, 3234–3237, 3279–3280 | 129×작은 세로 폭의 복도도 통신 상실; 거대 지도에서 여왕 위치·사망·포털 입구·적 머리 정보 공유 상실 |
| `PORTAL_ID_GUARD=true`, 리터럴 `2*cells` | 포털 id≥2*cells이면 간선 id만 저장하고 쌍 표 확장/등록 생략. 출구는 UNKNOWN으로 남을 수 있음. L2605–2642 | id가 연속 번호라는 가정이 맞지 않는 희소·큰 id 포털 지도. 개수 제한이 아니라 id 값 제한 |
| `POCKET_CAP=48`, `POCKET_DIV=2`, `POCKET_LOOP=true` | 열린 성분 <48이며 성장 후 길이>floor(성분/2)이면 pocket_full. 48 도달·UNKNOWN 간선·인식된 외부 포털 루프는 cap 반환. 여왕 herd도 <48에서 중단. L4824–4826, 4908–4929, 5331, 5449–5500, 7734–7746 | 아주 작은 풍부한 고리에서 과도한 섭취 억제; 48칸 긴 막다른 복도에서는 작은 주머니 분류 해제; 미관측 포털 출구가 탈출 가능성을 과장 |
| `BOX_MAX_CELLS=40` | 전부 무진주·비생성 셀인 알려진 OPEN 성분 ≤40일 때 boxed_in; 41번째 셀 또는 UNKNOWN을 만나면 false. L6587–6615 | 41칸 이상 빈 방도 포털 탈출이 필요하지만 작은 빈방 보너스 없음; 40칸 방에서 출구 위험을 과소평가 |
| `STAFF_REGION_MAX=120`, `STAFF_CELLS=16` | OPEN 성분이 120 초과면 staffing 탈출 포기. 안에서는 `capacity=max(1,spawn/16)`, 같은 성분 내 더 낮은 id 아군 머리 수≥capacity일 때 포털로 보냄. L7381–7450 | 작은 고수익 샘 여러 개를 과소평가; 121칸 과밀 방은 제외; 복도·비대칭 시야에서는 보이는 낮은 id 수가 실제 밀집도를 대표하지 못함 |
| `BARREN_REGION_CAP=600`, `BARREN_MIN_SEEN=40`, `BARREN_MAX_SPAWN=0.06`, `BARREN_BY_RATE=false`, `BARREN_KNOWN=false` | 최대 600칸 탐색(UNKNOWN도 통과); 관측≥40, 생성 셀≤6%, 진주/hot 없음, 포털 발견 때 탈출 목표 설정. L7479–7526 | <40 빈 섬은 미발동; 거대 지도 일부만 보고 빈 곳이라 판단; 아주 느린/풍부한 드문 샘을 생성 셀 개수로 잘못 평가; 포털 없는 빈 지역에는 이 탈출책 없음 |
| `SURVEY_CAP=0`, `STRIDE_CAP=1500` | 일반 survey는 크기 cap 없음; stride 점수 survey는 dequeue 1500에서 중단. L1990–1993, 4986–4988 | 거대 개방 지도에서 같은 위치도 단일 이동/stride 평가 범위가 달라짐; 먼 공급을 잘못 비교 |
| `CELL_BUDGET=12000`, `STRIDE_BUDGET=12000` | 누적 탐색 셀 >12000이면 일부 탈출 후보 평가 중단; stride는 >24000에서 중단. 일반 전체 탐색의 보편적 cap은 아님. L2079, 4714, 4776, 4804, 6515 | 거대·가지 많은 미로에서 좋은 후보가 방향 순서상 뒤에 있으면 누락. CPU 안전 판정은 audit-time 범위 |
| 영역 리터럴 `3*L+8`, `L+2`; `QUEEN_ROOM=8`, `QUEEN_CORRIDOR_GUARD=6`, `TR_STALL_ROOM=6` | 꼬리에 못 닿는 방 <3L+8은 dead end; <L+2는 trapped; 여왕은 <L+8 추가 벌점. 복도 가드는 6단계 내 막힘 확인. stalled 상태에서 avail≥6L+8이면 no-tail 벌점 면제. L867, 4820–4821, 7666–7687 | 모든 길이의 복도·긴 순환로를 면적만으로 평가하면 실제 탈출 가능성과 다름; 7걸음 이후 막힘은 복도 가드 범위 밖 |

**절대 라운드·병력 수에 따른 정책**

| 상수·현재값 | [C] 정확한 전환 / 사용 줄 | [E] 잘못 맞을 수 있는 미지 지도 |
|---|---|---|
| `LEADER_GROW_ROUND=300`, `LEADER_GROW_ROUND_BIG=150` | ≤1200칸은 r301, >1200칸은 r151부터 리더 역할/진주 양보 구역/길이>4 일반 분열 억제; board_short 예외. L605–606, 2304, 4173, 5677–5678 | 거대하고 가난한 지도는 아직 퍼지는 중일 수 있음; 작고 풍부한 지도는 반대로 성장 집중이 늦음 |
| `LEADER_FULL_UNITS=56`, `LEADER_FULL_KEEP=10` | >1200칸, feeding 전, N<56이면 board_short. 길이<10 리더 지정·분열 억제 예외; 진주 양보 구역도 꺼짐. N=56에서 해제. L2304, 4173, 5673–5678 | 거대 저자원 지도에서 56 도달 불가; 풍부한 좁은 구역에서는 56이 이미 과밀. 지도 전체 크기와 점유 가능한 면적 불일치 |
| `ENDGAME_ROUND=400` | 기본 feed_round=400, r401부터 feeding_phase. 일반 교환 normal_ok는 r400까지. L610, 4547, 7594–7596 | 큰 장거리 지도에선 모이기 늦음; 작은 풍부한 지도에서는 이른 합류가 유리할 수 있음 |
| `QUEEN_QUIET_ROUND=100` | is_queen이 지금까지 적 머리를 한 번도 못 봤으면 r100부터 queen_game latch. 단 한 번 본 뒤에는 이 경로 불가. L1672–1678 | 비대칭·고립·큰 지도에서 못 봤다는 사실이 안전/공급 충분을 의미하지 않음; 작은 개방 지도에는 is_queen 관문 때문에 발동 안 됨 |
| `QUEEN_SAFE_ROUND=300`, `QUEEN_SAFE_SPAN=0` | is_queen이면 r300부터 queen_game latch; span=0이라 **지금 적이 보여도** 시간 조건 충족. L1679–1683 | r300에도 여왕이 교전 중인 작은 전장·침입 포털 주변; 이름과 달리 안전 확인 조건이 없음 |
| `QUEEN_GAME_FEED_ROUND=300` | queen_game이면 feed_round≤300으로 내림; r301부터 먹이기. 일반 교환 종료도 앞당김. L1685–1686, 4547, 7594–7596 | 거대 장거리 지도에서는 300이 늦거나, 앞선 false-safe latch로 교전 병력을 너무 일찍 먹이기에 돌릴 수 있음 |
| `QUEEN_LEAD_LATE=true`, `QUEEN_LEAD_ROUND=0`, `QUEEN_LEAD_BONUS=1000` | feeding_phase && queen_game && round≥0일 때만 여왕 리더 우선도 +1000. L3208–3212 | ≤600 개방 지도에서 queen_game이 끝까지 false면 여왕 우선도 없음; 매우 풍부한 지도에서는 길이 차>1000이면 여왕이 우선되지 않을 수 있음 |
| `HOME_CHECK_ROUND=200`, 주기 리터럴 `round%2==0` | r0..200 짝수턴에만 닫힌 집 검사; 성공은 영구. L1665–1670 | 미로의 마지막 경계를 r201 이후에 확인하면 영영 집 판정 누락; 포털 있는 집은 안전 상태가 변해도 latch 유지 |
| `FEED_CAP_UNITS=56`, `FEED_CAP_ROUND=350` | N≥56 && r>350이면 기본 endgame 전에도 feeding_phase. N이 55로 내려가면 r≤feed_round에서 다시 꺼질 수 있음. L7594–7596 | 풍부한 큰 지도에서 r351의 일괄 전환이 이르거나, 소모전 중 N55/56 왕복으로 역할 흔들림; 가난한 지도에서는 도달 불가 |
| `FEEDER_KEEP_UNITS=3` | N≤3이면 새 feeder 대상 선택 안 함; N=4부터 허용. L4135–4138 (rally/local도 같은 조건이나 현재 꺼짐) | 거대 지도 마지막 수집원 보존에는 너무 적음; 좁은 막판 지도에서 3마리 중 하나의 먹이기가 꼭 필요한 경우 차단 |
| `SPLIT_LAST_ROUND=495` | 일반 split_child_size는 r496부터 금지. 긴급 split/queen_wait는 별도여서 전역 분열 금지는 아님. L2281–2308, 1797–1846, 1850–1855 | 자원 풍부한 막판 또는 포털 탈출 필요 상황에서는 일반 증식 중단 시점이 다를 수 있음 |
| `QUEEN_SPLIT_ROUND=200` | is_queen의 일반 분열은 r201부터 금지. L2285–2287 | 거대·가난한 지도에서 확장 부족; ≤600 개방 지도 여왕에는 이 금지 자체가 안 걸림 |
| `SPLIT_SOFT_LIMIT=60` | N≥60에서 일반 분열 금지. 교환 at_cap은 N≥min(unit_limit,60)-1이지만 worth는 TRADE_EVEN=true로 이미 같은 쪽. L2307, 4546–4556 | 수백 마리가 유효한 거대 지도에서 60이 부족; 작은 풍부한 방에서는 60 이전부터 과밀 |
| `QS_KEEP_LEN=3`, `QS_KEEP_MIN_UNITS=2`, `QS_KEEP_ROUND=0`, `QS_KEEP_CLEAR=0` | 모든 라운드에서 실제 여왕 일반 분열 후 길이<3이고 N≥2면 금지. N=1에는 이 관문 예외. L2298–2302 | 작은 저자원 지도에서 단독 여왕과 여왕+1마리 사이 생존/증식 타협이 급변 |
| `ESCAPE_RESERVE=2`, `LONG_SAFE_MIN_LENGTH=8` | N≥unit_limit-2이면 길이<8 escape split 거부, harvestable도 거부. 긴급 다른 분열 경로는 별개. L2420, 2452 | 좁은 포털 방에서 꽉 찬 병력을 탈출시켜야 하는 순간 차단; 상한이 낮은 지도에서는 일찍 발동 |
| 게임 동적 `unit_limit` | 모든 ct.can_split은 N<unit_limit 필요. H352–353. 상수 60과 달리 엔진 입력값 | 지도별 병력 상한이 다르면 고정 56/60 관문이 불가능하거나 너무 낮음; 규칙 자체를 잘못된 봇 정책으로 보지는 않음 |
| `AGGRESSIVE_TRADE_MIN_UNITS=1`, `TRADE_MIN_UNITS=8`, `TRADE_LOCAL_EDGE=1` | feed_round 이하에서 N≥(≤1200:1, >1200:8), A+1-E≥1이면 일반 교환 목표 허용. L4547–4558 | 작은 저자원·비대칭 시작에서 귀한 소수 병력 교환; 거대 복도 국지 전투는 N8과 전체 면적이 실제 우위를 못 나타냄 |
| `ATTACK_MIN_UNITS=56`, `LUNGE_PEARL=true`, `TRADE_SHORT_BY=1` | N≥56인 비여왕은 진주를 밟는 hunt/ram 걸음을 거리 비용0으로 계산, 1칸 짧은 적도 교환 가치 인정. N55에서는 해제. L4535, 4556, 4650, 5669–5670 | 풍부한 진주 복도에서 공격 범위 급증; 병력은 많지만 핵심 지역 방어가 빈 지도 |
| `QUEEN_HERD=true`, `HERD_MIN_UNITS=12`, 시야 아군 리터럴 `2` | 실제 여왕, 비리더, N≥12, 작은 pocket 아님, 기억 아군 있음, A<2일 때 herd 거리 유도. A=2부터 거리 유도 중단. L5310–5378 | 포털로 분산된 거대 지도에서 글로벌 N12는 근처 호위를 뜻하지 않음; 좁은 복도 두 머리는 충분한 경호가 아닐 수 있음 |
| `CENTER_ROUNDS=60`, `CENTER_SMALL_ROUNDS=30`, `CENTER_MAX_LENGTH=4`, `CENTER_PULL=40` | long_map은 r<60, 나머지는 r<30; 길이≤4, 가까운 pearl/hot 보너스 없을 때 중앙 유도. L611–614, 7760–7763 | 시작이 비대칭·외곽 공급이 풍부한 지도; 느린 복도 탐색이 끝나기 전 갑자기 방향 편향 소멸 |
| `CENTER_OUTNUMBER_MARGIN=0`, long_map이면 margin=`cells` | 중앙 유도 조건 E-A≤0; 자기 머리는 A에 포함 안 됨. 가로 긴 지도에서는 E-A≤cells라 사실상 병력 열세 해제 조건 없음. L614, 7761 | 가로로 긴 적 우세 복도에서 중앙 돌진 지속; 지도 회전만으로 다른 전투 판단 |
| `TR_STALL_RELEASE=true`, `TR_STALL_ROUNDS=12`, `TR_STALL_SEEK=30` | 중앙 최단거리 기록을 12턴 개선하지 못하면 중앙 대신 가장 가까운 미탐색(거리 상한30) 유도. L2825–2830, 5158–5166, 7763 | 긴 우회 복도에서 정상 우회를 정체로 오인; 거대한 미탐색 영역도 거리30 이후 차이를 무시 |
| `HEADING_TIE_ROUNDS=12`, `HEADING_TIE=1.5` | r<12, 길이≤4인 비여왕/비리더/비feeder의 정면 합법 이동에 보너스. r12부터 없음. L8252–8255 | 시작 방향이 막힌 비대칭 지도·초반 미로; 작지만 저자원 지도에서 r12가 탐색 단계와 무관 |
| `TIE_SEED=0`, 리터럴 `round*17`, `%5`, `0.25` | 모든 턴에서 id·방향·라운드의 5주기 잔여값에 따른 작은 타이 보너스. 시간 단계 전환은 아님. L8251 | 대칭 좁은 복도에서 동률 행동의 주기성이 반복 궤도를 만들 가능성 |
| `BARREN_ESCAPE=true`, `BARREN_ROUNDS=100` | barren portal routing은 r100까지, r101부터 꺼짐. L7453–7458 | 빈 시작 방을 늦게 발견하거나 r101 이후 포털로 빈 방에 도착한 지도 |
| `SPLIT_ROUND0=true` | harvest_round 초기값 -2. r0에 가짜 “직전 턴 수확” 상태가 생기지 않아 일반 분열 억제가 풀림. L1923, 2320, 8458 | 작은 막힌 시작 구역은 초기 증식이 불리할 수 있으나 꼬리 공간·출구 검사는 별도로 적용 |
| `QW_END_ROOM=1`, `MAX_ROUNDS=500` | queen_wait에서 chosen_room≥500-round면 cramped만으로는 대기 분열 안 함; !any_enterable은 별개. L6076–6078, H23 | 회전할 수 없는 복도는 남은 턴 수만큼 면적이 있어도 안전하지 않음; 진주 성장으로 공간 요구량이 바뀌는 풍부한 지도 |
| `FEEDER_APPROACH=15`, `FD_APPROACH_SCALE=false` | feeding_phase에서도 리더 Manhattan 거리>15이면 feeder 대상 지정 안 함. 큰 지도 크기 비례 보정 없음. L615, 4140–4142 | 거대·복도·포털 지도에서 실제 접근 경로와 토러스 거리가 다름; r301/401 전환이 원거리 합류를 보장하지 않음 |

**포털 존재·출구 상태에 따른 전환**

| 상수·현재값 | [C] 정확한 전환 / 사용 줄 | [E] 잘못 맞을 수 있는 미지 지도 |
|---|---|---|
| `QUEEN_NO_PORTAL=true`, `QUEEN_PORTAL_ROUND=0`, `QUEEN_PORTAL_ALL=false` | r0부터 is_queen은 일반 portal scoring과 survey 통과 금지. ≤600 비폐쇄 여왕은 이 일반 금지 제외. 비상 경로는 허용 가능. L6062–6069, 7634, 5062, 7889, 1860–1890 | 포털만으로 공급/안전 지역에 도달하는 큰 지도에서 잔류; 작은 지도에서는 반대로 일반 포털을 평가 |
| `QUEEN_NO_BLIND_PORTAL=true` | pick_direction에서 실제 여왕의 blind[k]를 false로 만들어 미지 포털 정찰 보너스 제거. 크기 조건 없음. L8078–8084, 8244–8245 | 유일한 유망 출구가 미지 포털이고 현재 작은 방에서 움직일 공간은 있는 경우 계속 잔류; 비상 이동까지 금지하는 규칙은 아님 |
| `QUEEN_PORTAL_LAST=true` | any_enterable=false의 비상 포털이 미지 출구면 실제 여왕은 먼저 합법 2분열/알려진 빈 한 걸음 시도. 대안 없으면 미지 포털 통과. L1860–1890, 1965–1987 | 작은 빈 방에서 대기 분열만 반복하고 탈출 늦춤; 포털이 유일 생존 경로인 곳 |
| `PORTAL_SCOUT_MAX_LENGTH=6`, `WEIGHT_PORTAL_SCOUT=0.40` | 길이≤6, 비feeder/비리더, 정책상 여왕 아님, 꼬리 확인 시 scout. 미지 출구 발견은 target bonus, 바로 앞 blind이면 best_base+bonus. L6062–6065, 5075–5078, 8080, 8244–8245 | 포털 많은 빈 지도에서 작은 유닛만 탐색; 길이7부터 공급망 개척 중단. 꼬리가 보이지 않는 작은 지도/복도도 제외 |
| `PORTAL_SCOUT_MIN_LEN=0` | 짧은 비여왕의 미지 포털 이동을 대체하는 사후 가드 꺼짐. L627, 691, 729–771, 8257 | 포털 도배 지도에서 2–3길이도 맹목 정찰 가능; 반대로 하한을 올리면 가난한 포털 방 탈출을 막을 수 있음 |
| `PORTAL_GUARD_LENGTH=10`, `PORTAL_GUARD_LEADER_MIN=6`, `PORTAL_GUARD_ENEMY_CLEAR=4` | is_queen 또는 길이≥10 또는 리더 길이>6은 이번 턴 출구 관측·노출0·적 머리 거리>4 필요. survey에서도 unsafe portal 뒤는 공간/자원 계산 제외(꼬리 도달은 유지). L6535–6553, 7902, 4985–5002, 5082 | 출구가 7×7 시야 바깥인 필수 포털은 긴 개체가 평상시 이용 어려움; 포털로 인접한 적은 단순 Manhattan 여유와 불일치 |
| `PORTAL_SAFETY_MARGIN=6`, `PORTAL_LEAP_PENALTY=150`, `PORTAL_LEAP_SMALL=0` | 알려진 포털 기본 -150; 길이≤6 && boxed_in이면 0. 길이>6이면 관측 공간<길이+6일 때 거부. L7905–7908 | 진주가 풍부하지만 좁은 순환 출구는 과도하게 거부; 40칸/길이6 경계가 출구 실제 위험과 다름 |
| `SPLIT_PORTAL_OK=true`, 리터럴 `round<=100`, `SPLIT_MIN_LENGTH=4` | 꼬리 옆 포털 하나라도 있으면 일반 분열 거부. r≤100, 비여왕, 길이=4이며 안전 OPEN 출구 공간이 충분한 경우만 예외. L2337–2358 | 포털 도배 지도에서 r101부터 같은 안전한 분열이 금지; 아주 작은 방의 증식에 장애 |
| `child_spans_portal` 리터럴 Manhattan `!=1` | 자식 몸 내부 연속 좌표 간격이 1이 아니면 일반 분열 거부. L2337, 2393–2399 | 비국소 포털을 가로지른 몸의 분열 차단; 지리적으로 붙은 포털에는 이 근사 탐지가 다르게 작동 |
| `HARVEST_PORTAL=true`, `TARGET_REACHABLE=true` | 비여왕만 portal dead-end harvest 재평가. 미지 출구 하나로 pocket confined=false/target_reachable=true가 될 수 있음. L4829–4830, 4915–4929, 4953–4961, 8068, 8157–8169 | 미지 포털 출구가 실제로 막혀 있는 작은 진주방; 포털 도배로 막다른 목표가 낙관 평가 |
| `SN_TAIL_MOUTH=true`, 입구 존재 `>=1`, fresh 리터럴 `1`턴 | 머리 옆 포털 또는 행동 후 꼬리 입구가 있으면 포털 경고가 리더·사냥·원거리 적 보고보다 우선. 수신 경고 age≤1이면 해당 출구 금지; unknown 출구는 아무 fresh mouth 보고로 금지. L3296–3333, 3340–3375, 3994–4013, 7899, 8080 | 포털 도배 지도에서는 경제 통신이 밀리고 관계없는 미지 출구까지 억제; 큰 지도에서는 sonar 자체가 꺼져 이 보호 없음 |
| `STRIDE=true`, 포털 간선 1개 | 첫 걸음 포털이면 stride 연장 안 함; 연장·long_escape·hit_escape는 PORTAL 간선 배제. sprint_escape도 시험 경로의 포털 배제. L1950–1953, 2059, 4690, 4751–4792, 6492 | 모든 통로에 포털이 있는 지도에서는 여러 걸음 탈출 선택지가 크게 줄어듦 |
| `QUEEN_SURE_LEN=64`, `QUEEN_SURE_STEPS=5` | 비여왕·비리더 길이≤64, 적 여왕 거리≤5의 sure hunt는 포털을 통과하지 않음. L4432–4441, 4496, 4514 | 공간상 가까워도 포털로만 닿는 적 여왕; 포털로 짧아진 경로를 버림 |
| `LOOK_DEPTH=8`, 포털 간선 1개 | lookahead는 PORTAL과 KELP를 넘어 확장하지 않음. L5567–5574; 역할별 herd·중앙 거리·home 검사도 포털을 보행 공간과 구분(L5366–5368, 5126–5155, 6570) | 포털 위주의 지도에서 공급·동료 접근성이 실제와 다르게 평가; 포털 없는 지도에서는 이 차이 없음 |
| `POCKET_KEEP_OUT=true`, `QUEEN_CORRIDOR_GUARD=6`, `MATE_UNPIN=true` | 미지 간선/미지 포털이면 죽은 길임을 증명하지 않고 가드가 개입하지 않거나 현재 안을 보존. L824–827, 855–857, 1007, 1514–1523 | 미지 포털이 많은 작은 복도에서 유일한 미래 출구를 낙관; 안전 가드가 미지 출구 안전성을 증명한 것은 아님 |

**경과 라운드·관측 수의 보조 경계**

| 상수·현재값 | [C] 정확한 전환 / 사용 줄 | [E] 잘못 맞을 수 있는 미지 지도 |
|---|---|---|
| `SONAR_STALE=25` | 리더 보고/기억 age>25면 무효·망각; far-head 송신의 여왕 위치도 age≤25 필요. L2988–2990, 3156–3170 | 거대 장거리 지도는 전달/재접촉 간격이 길고, 작은 고속 전장에서는 25턴 기억이 너무 오래됨 |
| `FEEDER_FRESH_ROUNDS=5` | 리더 시야에 있거나 리더 보고 age≤5면 fresh. 실제 ready_to_die의 on_drop 분기는 추가 leader_in_vision을 요구하므로 현재 이 5는 최종 허용 범위를 넓히지 못함. L4026–4027, 7608–7609 | 수치만 보고 5턴 지난 원거리 보고로 희생한다고 해석하면 오류; 실질 오판은 보이는 리더의 경로 예측 문제 |
| `GHOST_ROUNDS=3` | 마지막으로 본 적 머리 age>3 폐기; 현재 보이는/부재 확인 정보로 더 빨리 제거 가능. L4255–4283, 7921 | 긴 몸·고속 스프린트·포털 주변에서 3턴 위치 확장 근사가 실제 위협을 과소/과대평가 |
| `QUEEN_FAR_HEADS=2`, 보고 cap 리터럴 `8` | 원거리 적 보고 age≤2, 8개 저장 후 가장 오래된 것 교체; 여왕 가까운 적 머리(거리<9)만 송신. L2982–3059 | 수백 드래곤이 밀집한 지도는 9번째 위협 누락 가능; 포털로 다가오는 적은 지리적 거리 필터에 빠짐 |
| `INC_ALLY_MEMORY=10`, `HERD_BEHIND=0` | herd의 아군 위치는 age>10에서 삭제. HERD_BEHIND 분기의 GHOST_ROUNDS 조건은 현재 미사용. L5328–5351 | 거대 지도·포털 이후 동료는 이미 다른 곳인데 옛 위치를 향함; 좁은 안전 지역에서 장기 호위 기억은 짧을 수 있음 |
| `QUEEN_CHASE_FRESH=8`, `QUEEN_AVENGE=8` | 적 여왕 보고 age≤8, 우리 여왕 사망·길이≤4 등 avenge 조건에서 적 여왕 거리≤8이고 >1이면 추격 목표. L1744–1752, 3747–3749 | 포털 전장에서는 오래된 위치와 지리적 반경이 실제 공격 가능성과 다름 |
| 사망 추론 리터럴 `1`턴 | 이전 턴 여왕 머리 위치/주변의 빈·비생성 셀이 이번 턴 진주가 되고 여왕이 안 보이면 사망 상태 추론. L3381–3401, 3767, 3781–3783 | 좁은 포털·여러 몸의 동시 사망 지도에서 사체 원인 혼동 가능; [E] 이 감사에서는 기보 검증 안 함 |
| `HOT_TIMER=4`, `HOT_MIN_GAP=6`, `HOT_MAX_GAP=25`, `HOT_FALSE_TIMER=8` | 생성 타이머≤4 관측 간격6..25면 hot, 타이머>8이면 hot 해제. L2916–2925 | 매우 빠른/느린 샘·드문 재방문·진주 극빈 지도에서 자원 지대 분류가 실제 생산률과 불일치 |
| `SOON_SLACK=6`, `SPAWN_CLEAR_MAX=4`, `SPAWN_CLEAR=true`, `SPAWN_CLEAR_ALL=false` | 생성까지≤도달걸음+6이면 soon 목표. 일반 비리더/비feeder가 0..min(길이,4)턴 뒤 생성될 빈 셀에 들어가면 -300. L5036–5042, 7748–7753 | 아주 풍부한 좁은 샘 복도는 이동 가능한 모든 셀을 감점; 극빈 지도에서는 유일한 공급 근처를 피할 수 있음 |
| 현재/과거 관측 리터럴 `0`, `1`턴 | `seen_round==round`는 현재 진주·출구·안전 stride/escape 검증, `seen_round<0`는 미탐색. 일반 포털 길찾기는 과거에 안 출구도 사용하지만 긴 개체 가드는 현재 시야 요구. L1974–1978, 2063, 2348, 6375, 6496, 6544 | 거대·미로·포털 밀집 지도에서는 전역으로 알고 있는 것과 현재 안전을 확인한 것을 구별해야 함; 이것은 통상 필요한 신선도 관문 |
| 송신 주기 리터럴 `%2`, `%4` | avenge 보고는 (round+방향)%2==0, 리더가 있을 때 far-head는 %4==2 슬롯; 앞선 mouth 경고가 우선. L3318–3333 | 긴 복도에서 음파가 필요한 방향/시각과 슬롯이 맞지 않거나 포털 경고로 계속 밀림 |
| `TERRITORY_DECAY=0`, `TERRITORY_TIME_SCALE=80` | 거리 할인은 항상1; 생성 대기는 80/(80+대기)로 연속 할인. 80턴에서 정책이 뒤집히는 임계값은 아님. L5503–5531 | 거대한 빈 공간이 멀리 있는 공급보다 과대평가될 수 있음. 명확한 면적 cutoff는 없지만 큰 지도 위험을 키움 |

**선언은 있으나 현재 정책 경계가 아닌 항목(꺼짐·가려짐)**

| 현재값 | [C] 도달성 / 사용 줄 | [E] 미지 지도 해석 |
|---|---|---|
| `QH_SCOUT=true`, `QH_REVENGE_ROUND=100`, `QH_QUIET=20`, `QH_FRESH=20`, `QH_MAX_LEN=4` | `QUEEN_AVENGE=8`로 qh_watch가 qh_on/hunter/notice=false 후 L3800 return. L3802–3821의 r100·20턴·포털 경로 활성 조건은 실행 안 됨. L3790–3800 | 현재 위험을 이 정찰 상수에 돌리면 오류. 사망/여왕 위치 메시지와 avenge의 8턴 경로는 살아 있음 |
| `QUEEN_WAR=0`, war 추격 신선도 리터럴 `30`, 사망 count `A+1==N`, war 방송 `%4/%2` | war_act/war_hunt 및 그 count-dead 분기 꺼짐. L654, 1653, 3310–3312, 3459, 3607, 3770 | 현재 전역 병력 수로 여왕 사망 판정하지 않음 |
| `QUEEN_GUARD_CELLS=0`; `QG_*` 보호 강화 상수 | queen_guard 항상 false. 추가 크기 경계 및 해당 위협·집 반경·분열 유지 강화 없음. L5690–5691 | 현재 작은/큰 지도 보호 차이를 이 비활성 묶음 탓으로 설명하면 오류 |
| `LC_LEAD_ROUND=0`, `LC_FEED_ROUND=0`, `LC_ENEMY_LEAD=0`, `LC_ENEMY_FEED=0` | 라운드 override/보이는 큰 적에 따른 조기 전환 없음. L607–610, 5653–5665 | 현재 전환은 지도 면적·고정 라운드·병력 수에 의존 |
| `FD_APPROACH_SCALE=false`, `FD_APPROACH_BASE_SPAN=100`, `FD_APPROACH_DIV=4`, `FD_RALLY_BIG=false`, `FD_RALLY_FRESH=25`, `RALLY_FRESH=0`, `RALLY_END_FRESH=0` | width+height>100 접근거리/신선도 보정 없음. rally 전체 호출 꺼짐. L615–616, 1757, 7572–7579 | 거대 지도에서 원거리 자동 집결이 켜져 있다고 가정하면 안 됨 |
| `FEED_EARLY_ROUND=0`, `FEED_EARLY_MAX=2`, `FEED_LOCAL=0`, `FEED_LOCAL_MIN=4` | 조기 feeder 예외 및 local_die 호출 꺼짐. L1721, 4134, 7612–7624 | 작은 가난한 지도에서 이 상수들이 조기 여왕 회복을 해주지 않음 |
| `EXPLORE_GAIN=0`, `EXPLORE_ROUNDS=200`, `EXPLORE_RANGE=60`, `FAR_IDLE=0` | r200까지 추가 탐색항 없음. FAR_GAIN=2는 idle 조건 없이 항상 적용. L7719–7730 | 큰 지도에서도 추가 탐색항이 살아 있다고 해석하면 안 됨 |
| `IDLE_ESCAPE=0`, `IDLE_REGION_MAX=40`, `IDLE_STRICT=false`, `IDLE_LOG=0`, `INC_PERIOD=0` | 시간 정체 기반 portal escape·로그·주기 income 갱신 호출 없음. L1730–1734, 1771, 7267, 7314–7378 | barren r101 종료 뒤 별도의 정체 탈출책으로 보완되지 않음; staff는 별개로 살아 있음 |
| `ASSASSIN_MOD=0`, `ASSASSIN_FRESH=30` | assassin 역할 및 그 30턴 신선도 관문 없음. L6049–6052 | 큰 지도 오래된 적 추격 위험을 이 상수 탓으로 설명하면 오류 |
| `CORPSE_SLACK=0`, `CORPSE_FRESH=15`, `HOT_FAST=false` (fast gap 리터럴2..4) | 사체 15턴 경합 예외와 빠른 샘 2..4턴 분류 꺼짐. L2731, 2907–2914, 5026–5028 | 현재 hot 판정은 6..25턴 창; 사체 단기 이익 예외 없음 |
| `PORTAL_FAR_DECAY=0`, `PORTAL_FAR_ROUNDS=0` | 라운드 제한 장거리 portal bonus 없음; 기본 target_bonus 사용. L7714–7717 | 0이 “r0까지만 포털 탐색”이라는 뜻이 아님 |
| `LEADER_GUARD_ROUNDS=0`, `LEADER_GUARD_RADIUS=6`, `BIG_ESCAPE_LATE=false`, `QUEEN_DEFEND_LATE=false` | 종료 직전 leader 추가 가드 없음; big escape/queen defense에 feeding-phase 제한 없음. L4664, 4596–4597, 7854 | 막판에 별도 보호가 켜진다고 가정하면 안 됨; QUEEN_DEFEND_RADIUS=0 경로는 통상 다른 머리와 거리0 불가 |
| `QUEEN_FALLBACK=false`, `QF_MEMORY=40`, `QF_HOLD=2`, `QF_SPOTS=4`, `QF_CROWD=3`, `QF_TIE_SPAN=2` | 현재/최근 3턴 직접 본 적 머리 수≥A+1의 fallback 및 기억/crowd 임계 전부 비활성. L1659, 5170, 5214–5298 | 적 우세에서 안전한 과거 위치로 후퇴하는 기능은 현재 없음 |
| `QG_SAFEZONE=false`, `QG_SAFEZONE_CHECKS=2`, `QG_SAFEZONE_GAP=4`, `QG_SAFEZONE_ROOM=3`, `QG_SAFEZONE_FRAC=0.1`, `QG_SAFEZONE_PROBE=12` | 포털 구역 확인 횟수·대기·크기 10% 판정 비활성. L1689, 6647–6976 | 포털 많은 미지 지도에서 이런 안전지대 검증이 켜져 있다고 가정하면 안 됨 |
| `QG_CORNER=false`, `QG_CORNER_EVERY=10`, `QG_CORNER_REACH=40`, `QG_CORNER_DANGER=4`, `QG_CORNER_RADIUS=2` | 구석 앵커의 10턴 재검사·40칸 범위·3면 차단 리터럴 등 비활성. L1696, 6998–7206 | 미로/포털 구석에서 이 방어가 개입하지 않음 |
| `QUEEN_BRAIN=false`, `QB_GHOST_AGE=3`, `QB_DANGER_ROUNDS=20`, `QB_W_DANGER=0`, `QB_W_ESCORT=0` | brain 기억 나이·20턴 위험 이력·호위 수 점수 모두 비활성. L1702, 5754, 5791, 5924–5945 | 보호 기능의 실제 범위를 과장하지 않도록 제외 |
| `SHORT_EVADE=false`, `SHORT_EVADE_ANY=false`, `SMALL_THREAT_OUTNUMBERED=false`, `SMALL_THREAT_MULT=1`, `CROWD_MARGIN=0` | A+1>E의 short evade gate, E>A의 small threat gate, survey 아군 몸 crowd 가산이 현재 비활성. L1064, 5112, 7785–7787 | 포털 출구 과밀·지역 열세를 이 항들이 보정하지 않음 |
| `SHARE_SIGHT=false`, 면적 리터럴 `4096`, 적 수 리터럴 `1` | 일반 sight packet은 cells>4096 또는 적 머리0이면 생성 안 하며, 적 머리>1이면 두 번째 머리도 넣지만 송수신 호출 자체가 꺼짐. L3063–3088, 3264, 3308 | 4096은 현재 통신 cutoff가 아님. 현재 활성 cutoff는 한 변128이며 QUEEN_FAR_HEADS 보고는 별도 |
| `POCKET_PORTAL_BAN=false`, `CENTER_PATH=false`, `TR_CENTER_ORIENT=false`, `UNSEEN_CLAIM=false`, `QUEEN_PORTAL_ALL=false` | 작은 pocket 포털 직접 금지·경로 중앙 거리·세로 긴 지도 대칭 처리·feeding 시 미탐색 점유 예외·모든 실제 여왕 일반 portal ban 없음. L5398–5403, 5126–5129, 611, 5050, 6065–6069 | 이름만 보고 현재 기능을 있다고 읽지 말 것; 활성 경계는 위 표에 기재 |

[E] 세 변경은 각각 독립적인 완화 후보이며 동시 적용안이나 승인된 배포안이 아니다. [C] 소스·다른 폴더·git·원격 상태는 수정하지 않았다. [M] 새 경기/업로드/컴파일은 0회다. 기보를 측정하지 않았으므로 승률, 발동 빈도, 실제 실패 game id/round는 제시하지 않는다. 정적 코드의 조건·도달성은 확인했으며, 미지 지도에서 어떤 후보가 실제로 더 낫다는 결론은 확인하지 않았다. audit-diff의 충돌 안전성과 audit-time의 실행시간 판정을 대체하지 않는다.
