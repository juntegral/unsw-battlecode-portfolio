[M] 감사 시각: 2026-10-09 01:41:47 KST. 분석자 unseen. 원본 라이브 봇/다른 작업 파일은 수정하지 않았다.

[C/M] 자료 출처와 읽는 법

- [C] 모든 main.cpp/helper.hpp/sonar_codec.hpp 행 번호는 `data/online/smoke/one5-bot/` 원본이다. 소스 SHA256은 `source_hashes.json`이다.
- [M] 엔진은 `~/meow-redteam/engine/venv`의 installed unswbc1.2.7이며, wrapper는 `~/meow-redteam/docs/engine-engine.py:124–135` 그대로다. 바이너리 SHA256은 `checks.json`이다. map parser C++ 소스는 지정된 workspace에 없었다. 따라서 지도 허용 범위는 엔진 WASM 로더에 직접 넣어 확인한 [M] 결과이며 C++ 행 번호를 꾸며내지 않았다.
- [C] resource/timeout 규칙은 `~/meow-redteam/docs/ENGINE-METADATA.txt:118–136`, torus wrapping은 shipped helper.hpp:156–161, round cap은 :23, 실제 sprint/free-step 규칙은 :342–345, victory comparison은 `engine-run.py:23–34`에서 확인했다. 라이브 helper의 sprint 설명 주석만 구 규칙이고 구현은 shipped helper와 동일하다. Bot 자체 `sprint_free`, `sprint_reach`(main:4111–4120)는 ceil(L/4)와 MIN_SIZE2를 쓴다.
- [M] `maps.json`은 19 historical name/version 항목이다. `one5-w1.json`의 15개 목록으로 필터하고 Schooltime은 최근 #2를 선택했다. 실제 map initializer는 로컬 ladder 사본8개와 installed template7개(Maze 포함)다. `map_inventory.json`에 source 절대경로, index key, 원본 source 수치와 replay-derived index 수치를 함께 남겼다. index의 dragons_at_spawn은 한 팀 수이므로 총 시작 수와 그대로 비교하지 않는다. 일부 bed 수가 local template와 다르므로 이를 qualifier 서버 원본의 완전 동일한 snapshot이라고 주장하지 않는다. 가로/세로/여왕 길이는 모두 서로 일치했다.

[M] 로더 범위 증거

`probe_loader.py` / `probe_more.py`, `loader_probes.json` / `loader_more.json`을 참조한다. 해당 스크립트는 compiled engine을 읽고 map 초기화를 호출하지만 spawn callback에서 예외로 중단한다. bot reply callback은 실행되면 즉시 assert한다. 봇 실행/이동/분열/진주 시뮬레이션은 하지 않았다. 0-starter probe는 callback 없이 즉시 반환했으므로 그 항목의 `loaded:false`/`Returned without a spawn`은 map parser 거절을 뜻하지 않는다; playable two-sided test fixture에는 쓰지 않았다.

| 질문 | 직접 확인한 사항 [M] | 해석/미확인 [E] |
|---|---|---|
| 크기 | 7×16,8²,64²,65×64,128²,129×32,32×129,256² accept; 6짜리 변은 `at least 7x7`,257+는 `at most 256x256` 거절 | 이진 loader 허용 범위가 대회 운영자의 지도 제작 제한과 같다는 보장은 없음 |
| 대칭 | x,y,xy accept; 생략한 비대칭 pearl bed accept; none/rot90/diagonal 문자열 거절; 선언한 대칭을 깨는 bed는 거절 | 다른 대칭/비대칭 지도는 SYMMETRY를 생략해서 만들 수 있음. 정적 bed 대칭은 현재 countdown 동일성을 보장하지 않음 |
| gaps | 0,0과 양수1,501,1,000,000,INT_MAX accept; 0,1/음수/hi<lo 거절 | INT_MAX는 loader 입력 상한 확인이며 한 판의 실제 countdown 동작/분포는 재지 않음 |
| portals | 같은 방향 두 끝 accept, mixed orientation/1끝/3끝 거절; ID8,000,000과 INT_MAX accept, 음수 거절 | 따라서 main의 other_horizontal!=horizontal 경로는 정상 legal pair에서 문제 아님; sparse numeric ID는 합법임 |
| kelp/seam | seam EDGE와 wrap alias 로드 accept; 모든 생성 파일 notice0 | 실제 seam 이동 판은 하지 않음. helper add_dir는 wrap하고 bot edge_at은 canonical seam 칸을 조회함 |
| 시작 | 팀0/1 또는1/0 순서 accept, 같은 팀 연속 거절; odd3 /65 /128 total starters accept; L1 거절, L2/4/25/128 accept; fixture L1116 accept | 최소2는 engine helper와 일치. 일반 playable two-sided 최소 총2, 각 팀≥1. 같은 queen L4/동일 시작 위치/총2는 요구 없음. 위치·방향은 DRAGON 몸으로 정해지며 새끼는 tail reverse. parser가 시작 수가 limit를 넘는지 spawn 전에 검사하는지는 확인되지 않음 |
| unit cap/rounds | UNIT_LIMIT0 거절,1/2/64/128/4096/INT_MAX accept, 생략은64; ROUND_LIMIT/MAX_ROUNDS/TORUS 지시어 거절 | 양수 cap에 대한 loader 최대 고정값은 발견되지 않음. 지형당 총 body 수는 칸 비중복 때문에 area로 제한. 같은 limit라도 첫-turn 실제 unit count와 helper의 상한 검사는 대전 없이는 미검증 |

[C] 코드 감사의 구분

1. [C] hard bounds: main constructor의 모든 지도 크기 vector와 Position 인덱스는 65,536칸에서도 int 범위 안이다. static arrays4는 방향용, sym_alive3은 후보용이다. `bfs_queue`/`bfs_beyond`는 2*cells; 일반 flood는 칸당 한 번 방문, survey는 beyond→plain 개선 때 한 번 추가 방문하므로 이 배열이 4096으로 고정됐다는 주장은 틀리다. pocket_queue는 POCKET_CAP+4이며 enqueue 직전에 POCKET_CAP를 검사한다(3569–3616). known/escape/QH queues도 cells 크기로 할당한다. 이 사실은 메모리 전체·timeout 검증을 대신하지 않는다.
2. [C] coordinate/value encoding: leader position127, signed ID flag32768, QH leader length1023 saturation, QH/mouth cell16383, sight cell4095, round511가 실제 format 경계다. sonar_codec.hpp는 좌표를 encode하지 않고 keyed check/seal/open만 한다. make_key(width,height,tag) :58–63은 256에 문제 없다. 현재 `sonar_enabled` gate는 최대128²를 보장하므로 active QH/mouth14bit가 overflow하지 않는다. SHARE_SIGHT=false여서12bit 경로는 미사용이다. >4096 pack_sight는 return false다. width65 자체는 flat index/128 coord 한계와 무관하다. 단독 second sentinel4095는 count=4096에서 cell>=cells 검사를 통과하는 latent bug다.
3. [C] layout assumptions: queen identity는 ID≤1을 팀과 함께 관측하고, 첫 self ID≤1이면 자기 팀 queen으로 정한다. engine가 시작 팀 교대를 강제하므로 이 ID 가정은 맞다. real_queen의 QS ring은 작은 지도에도 남는다. is_queen의600 gate는 별도 정책 가정이다. INITIAL_LENGTH3은 첫 update LENGTH로 대체된다. 처음부터 긴 몸은7×7 밖 tail을 모를 수 있고 split_child_size는 tail_index<0이면 child2를 바로 허용(1178–1180)한다. 안전한 출산 검사를 못 하는 상태지만 새로운 L4/2마리 고정 배열 오류는 아니다. L1116 fixture는 1023 saturation과 알려지지 않은 시작 꼬리를 함께 검증하도록 만들었다.
4. [C] map-scale policy: AGGRESSIVE1200, QUEEN_MIN600, CENTER_MAX1000/SMALL700, width≥2height, QUEEN_HOME_LEASH min((width+height)/8) 경로(5811, 현재 leash0), HOME_MAX_FRAC0.5와 minimum40, BARREN_REGION_CAP600/MIN_SEEN40/MAX_SPAWN0.06, STAFF_REGION_MAX120/STAFF_CELLS16, POCKET_CAP48/div2, BOX_MAX40, INC_RADIUS30(현재 INC_PERIOD0) 같은 숫자는 배열 capacity가 아니라 공간/정책 한계다. 각각 지역 구조·샘 밀도가 ladder와 다른 지도에서 길찾기/정체로 이어질 수 있다. BARREN_BY_RATE=false(:271)라 반복 관측한 수입이 아니라 생산 가능 tile 비율로 barren을 판단한다(escape_update:5459–5525). 새 지도에서 풍부한 샘 하나와 많은 빈칸인 방도 barren으로 오판할 수 있다. timers fixture가 드문 샘/긴 gap을 포함한다. 공격/먹이기 시간은 fixed round이며 qualifier round cap500과는 일치한다.
5. [C] portal handling: 같은 방향2끝 제약은 엔진과 일치한다. 다른 endpoint를 스스로 관측하기 전에는 unknown으로 처리한다. portal IDs의 조밀함은 엔진이 요구하지 않는다. portal_edges를 ID로 resize하는 것이 hard fault다. 연결 그래프는 fresh enemy/body를 차단하고 unknown terrain을 open으로 취급한다; 이는 합법 이동 보장보다 전망이 낙관적인 전략 가정이다. helper 업데이트에서 현재7×7 실제 edges가 다시 들어오기 때문에 한 칸 앞 켈프를 항상 보지 못한다고 주장하지 않는다.
6. [C] Threat reach: THREAT_REACH_MAX6/QUEEN_REACH_MAX8는 엔진의 최대 sprint가 아니다. main:2624–2627은 이 깊이에서 threat flood를 자른다. main:4350–4363의 hit ring도 몸이 시야를 벗어나면 확인한 parts로 free를 구하고, 실제 length 대신 seen+1 또는3을 full 범위에 사용한다. LONG_SAFETY=false(:151)라 foe_size 보정은 현 라이브 경로에서 빠진다. 이는 큰 unseen 지도에 허용된 긴 시작 몸이나 무료 긴 이동을 과소평가할 수 있다. `un_threatreach_1`은 enemy nonqueen #3의 실제 몸61, free16이지만 queen #0의 시야에는 작은 stub만 보이도록 했다. ID0의 첫 head(3,3)와 enemy head(6,3) 거리는3이다. damage는 실제 한 판으로 측정하지 않았으며 enemy action이 queen을 때릴지는 상대 전략에 달렸다. 이 코드 보정은 알려진 지도에서도 움직임/CPU를 바꿀 수 있어 한 줄 불변 카드가 아니다.
7. [C] CPU: default SURVEY_CAP0, basic survey는 CELL_BUDGET을 while 중 검사하지 않는다. 검사와 turn_cells 증가는 일부 escape/stride만 제한한다. rivals는 ally/enemy 전체 reachable component 두 번, QH는 target에서 unknown-open와 seen-open flood 후 상황에 따라 세 번째 flood, HERD는 remembered allies multi-source flood, 경로별 survey도 component flood이다. queens에서 capped known_room/room probing이 추가된다. LOOK_DEPTH8 DFS는 width-height와 독립적인 국소 지수 work이고 cell counter에 포함되지 않는다. 최대256² open/cap64 fixture에서는 첫 여왕 (4,4)에서 아군 머리 (4,6)가 보이므로 rival flood와4개의 basic step surveys가 각각 최대65,536칸 범위에 이를 수 있다. 이는 작업량 분석이며 CPU points로 환산하거나 실제 timeout 횟수로 주장하지 않았다. cap64는 **드래곤별100M**을64개가 공유한다는 뜻이 아니다.
8. [C] memory: `checks.json`의 vector 원소 크기 기반 정적 합은 constructor120byte/cell=7,864,320byte at65536이다. lazy arrays, capacities, allocator/header, std deque, log strings, stack은 제외한다. ordinary largest-map constructor가 자동48MB 초과라고 결론내릴 근거는 없다. 반면 sparse-ID fixture의 portal vector payload만64,000,008byte는 decimal48MB와48MiB 모두 넘는다. main catch는 Bot 생성/init/update 바깥 오류를 잡지 않으며, take_turn 안의 std bad_alloc은 fallback으로 갈 수 있다; sandbox allocation이 trap인지 bad_alloc인지는 실행 미검증이다.

[C/M] 카드: 큰 numeric portal ID는 dense array로 확장하지 않는다

- 삽입: main.cpp1445 바로 다음 `if (id >= 2 * cells) return;`.
- 기존 switch/constant: 해당 numeric-ID guard는 없다. 2*cells는 canonical edge 수에 따른 메모리 안전 ceiling이고, engine portal ID 범위라고 오해하면 안 된다.
- [C] ID는 north_portal/west_portal에 먼저 남기므로 portal_exit(:1465)의 vector-size 검사에서 PORTAL_UNKNOWN으로 처리한다. 높은 ID의 포털이 알려지지 않은 출구로 남는 한계는 의도적으로 보고한다. 일단 allocator failure를 막고, full support는 dense array 대신 ID→endpoint pair keyed 저장으로 바꿔야 한다.
- [M] inventoried15 ladder +24 held-out의 max portal ID는2*cells 미만이어서 새 guard는 그 파일의 정책/메시지를 바꾸지 않는다. 코드 분기만으로 판단했으며 새 WASM CPU overhead와 on/off replay fingerprint는 측정하지 않았다.
- [M] `build-check/main.cpp` 복사본에 한 줄만 적용하고 `c++ -std=c++20 -O2`로 compile exit0을 확인했다. 원본 diff 없음. raw diff는 `portal_guard.patch`.
- [E] lead 검사: sparse fixture의 처음 portal mouth 관측 이후 allocator/trap/fallback 오류0, peak memory48MB 아래; ID0 대조 fixture 정책 사건이 원본과 같음. 고ID 연결을 찾는 전략 문제는 이 guard로 해결됐다고 판단하지 않는다. 나머지 큰 지도/codec 수정은 meter 검증 전 카드로 제시하지 않는다.

[M] 생성 지도/재현

`make_maps.py`가 기존 지도와 같은 MAP/SYMMETRY/MAP_NAME/UNIT_LIMIT/TILE_COUNT/TILE/EDGE_COUNT/EDGE/DRAGON_COUNT/DRAGON/END 형식으로 만든다. width+1 stride의 horizontal/vertical 교대 edge row를 그대로 쓴다. flags x/y는 축 이름이다. 기존 표에 keyed policy를 추가하지 않았다. symmetry 없음 fixture는 SYMMETRY 줄을 생략한다. 생성33개를 로더로 하나씩 읽고 spawn callback에서 중단하여33/33 accept, notice0을 얻었다. `maps_validation.json`의 initialized metadata와 `maps_manifest.json`의 목적을 보고 lead가 판을 실행하면 된다. paired portal fixtures는 name와numericID 외에 정확히 같다(`checks.json`). 경계 비교 지도는 area가 다른 정책 스트레스이고 동작 불변 A/B 실험을 뜻하지 않는다. churn fixture는 id32768 이상 도달을 보장하지 않으므로 lead는 cumulative birth ID를 따로 확인해야 한다.

[M/E] 검증하지 않은 일

네트워크, 메시지 게시, 게임, native bot 실행, WASM bot 실행, replays 읽기/계수, server rule 변경 확인은 하지 않았다. 따라서 구체적 game IDs/rounds를 발견 근거로 꾸며내지 않았다. 원본 dossier의 성장 정체·포털 출발·여왕 관련 절을 읽되 기존 승패/기보 계수를 새 측정처럼 반복하지 않았다. 잠재 위험의 chance는 미지 지도 분포를 모르는 정성 추정이다. `nice -n10`을 요청했지만 sandbox가 setpriority를 거부했다; 출력에 경고가 남았고 게임을 추가로 시작하지 않았다. 문서 수정은 own folder로 제한했으므로 공용 WORKQUEUE/DECISIONS 변경이나 커밋을 하지 않았다.
