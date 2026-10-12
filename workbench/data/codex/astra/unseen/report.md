[C/M] 라이브 one5는 256×256까지 허용하는 엔진보다 음파 좌표·탐색 예산·포털 ID 처리 범위가 좁다.
[C] 카드 1개: `remember_portal` 1445행 다음에 큰 ID 배열 확장을 막는 한 줄; 별도 [패치](portal_guard.patch)와 컴파일된 복사본만 제공한다.
[M/E] 로더 확인은 확실, 전략 피해·시간 초과의 발생 확률은 미측정. 감사 시각: 2026-10-09 01:41:47 KST.

[M] `maps.json`은 과거 버전까지 19항목이다. 실제 15지도는 one5-w1의 목록으로 골랐다. 상세 수치는 [inventory.md](inventory.md), 전체 근거·한계는 [audit.md](audit.md)에 있다. 아래 main/helper 행은 `data/online/smoke/one5-bot/` 원본이다.

| 범위 | 엔진의 실제 허용/규칙 | 현재 15지도에서 확인한 범위 |
|---|---|---|
| 크기 [M] | 각 변 7–256, 면적 49–65,536; 6/257은 로더 거절 | 가로 24–64, 세로 12–64, 면적 288–4,096 |
| 지형 [M/C] | 토러스; seam에도 켈프 가능; 선언 x/y/xy, 선언 생략 시 비대칭도 허용; 포털은 같은 방향의 변 두 개를 연결 | 선언 y/xy, seam 켈프 존재; 포털 0–20쌍, ID 0–19 |
| 진주 [M/C] | (0,0)=생성 없음, 양수 min≤max; 1과 INT_MAX gap도 로드됨; 타이머는 생성 시도까지 남은 라운드(helper:244) | beds 70–1,024; gap 1–3,849; 재생 타이머는 대칭 추론의 고정 지형 정보가 아님 |
| 시작 [M/C] | 길이 ≥2, 좌표 범위 내 비중복 몸; 시작 수/길이/위치 고정 없음. 팀 교대 강제, 따라서 여왕은 #0/#1. UNIT_LIMIT 기본64, 양수 사용자 지정 허용 | 양편 각각 2–10마리; 여왕 L2–25, 모든 시작 몸 L2–25; 여왕 간 토러스 거리 2–44; limit64 |
| 종료/자원 [C] | 500라운드(helper:23), 턴당 100M points, 드래곤당 48MB, CPU1초/벽시계10초(ENGINE-METADATA:118–124) | 이번 감사에서 턴 자원 측정 없음 |

[E] 확률은 지도 분포를 모르므로 수치화하지 않았다. **한 줄이며 기존 지도에서 분기가 발동하지 않는 수정은 먼저 제시**하고, 나머지는 조건부 발생 가능성×피해의 정성 순서다.

| 우선/위험 | 정확한 코드와 고장 | 발생 가능성·피해 [E] | 시험 지도(`maps/`의 파일명) | 최소 수정/판정 |
|---|---|---|---|---|
| 먼저: sparse 포털 ID [C/M] | main:1445–1447 ID+1개의 8byte 원소. ID8,000,000 로드 가능, payload64,000,008byte. take_turn 예외만 catch(6470–6474): 메모리 실패가 trap/사망 또는 반복 fallback으로 나타날 수 있음 | 보통 생성기에서는 낮음, sparse ID면 확정된 과대 요청·치명적 | `un_portalid_1.map`, 같은 지형의 ID0 대조 `un_portalid_2.map` | 1445 다음 `if (id >= 2 * cells) return;`. 높은 ID는 연결을 모르는 포털로 남음. 완전 지원은 sparse keyed 저장. 카드 성공: 고ID 관측 턴의 할당 실패0, memory<48MB; 실패: 여전히 실패/대조판 행동 변경. [M] 15지도+24 held-out에서 분기 불발, native compile 통과; 기보 동일성 미실행 |
| 1. 큰 지도 CPU [C] | main:2511–2546 rival floods, 3093–3231 무제한 survey, 3448–3499 herd, 2164–2187/2198–2248 QH floods. CELL_BUDGET은 survey 종료 뒤 증가하며 기본 survey를 멈추지 않음; LOOK_DEPTH8도 별도 | 큰 열린 지도라면 중간 이상, timeout이면 해당 드래곤 사망; **실제 초과 미확인** | `un_cpu_1.map`(256², 양편64마리), `un_sonar128_3.map` | cells>4096일 때만 survey와 다른 full floods에 작업 상한. survey 한 곳만 제한하면 불충분. lead의 WASM 측정 전 채택 카드 없음 |
| 2. 음파 전체 소실 [C] | main:356,556,1935–1937,1984–1986: 어느 변이129+면 송수신 모두 중단. leader/먹이기·QH 여왕 목격/사망·mouth 공유 소실 | 129+면 확정, 협동 전략 피해 큼 | `un_sonar128_1.map`, `_2.map`; 128 대조 `_3.map` | 큰 지도용 별도 wire format. COORD_MAX만255로 올리면 7bit x/y가 alias하므로 금지 |
| 3. 긴 적의 도달 범위 과소평가 [C] | main:26–30,123,2598–2627,4350–4363: 일반 threat 최대6/queen8, 부분 목격 길이로 free reach 계산; LONG_SAFETY=false이므로 foe_size 보정은 라이브 ring에 적용 안 됨 | 매우 긴 시작 몸/큰 free stride에서 중간, 여왕이 안전하다고 고른 칸에 피격 가능 | `un_threatreach_1.map`(적 비여왕 L61, 실제 free16), `un_startlength_2.map` | 부분 몸이면 긴 적 길이의 보수적 상한+공유 목격을 사용하고 탐색 비용 제한. reach 상수만 늘리면 시간 초과 위험도 증가; 기존 지도에도 영향 |
| 4. 작은 여왕의 일부 보호 소실 [C] | main:185,3789–3795 is_queen은 cells>600 또는 home_closed. 작은 열린 지도에서는 dead-end 점검(5674–5687), r200 뒤 분열 제한(1138), 포털 금지(4156) 등이 빠짐. **real_queen 기반 ring safety/QS_KEEP은 유지** | ≤600 열린 지도면 높음; 함정 진입/여왕 손실 가능 | `un_queen600_1.map`, `_2.map`, `un_startlength_1.map` | 필요한 보호만 real_queen으로 바꿔 기제 검증. 전역 is_queen 교체는 기존 작은 지도 행동도 변경 |
| 5. 포털 의존·먼 먹이 [C] | main:1462–1482 양 끝을 직접 봐야 연결 앎; 4151–4156 큰 지도 여왕은 포털 ban. 분열 새 프로세스에 portal_edges 기억 없음. 397–409 CENTER/FAR, 3709–3715 target_bonus 거리 이득 범위 제한 | 봉쇄 방/드문 샘이면 중간, 접근 불능·탐색 정체 | `un_portalonly_1.map`, `un_timers_1.map`, `un_edgewrap_1.map` | 목격 연결 공유 또는 조건부 여왕 출구 허용; 현재 동작을 바꾸므로 지도/판면 검증 필요 |
| 6. 크기/축 정책 절벽 [C] | main:557–566 cells1200에서 aggression/성장 r300↔150; CENTER_MAX1000/SMALL700, width≥2height인 축만 long. home 판정 ≤0.5*cells(4565–4596). 지형·생산량과 무관한 정책 | 경계/세로 긴 지도면 중간; 조기 정체·잘못된 끌림 | `un_aggressive1200_1.map`, `_2.map`; `un_center700_1.map`, `_2.map`; `un_center1000_1.map`, `_2.map`; `un_aspect_1.map`, `_2.map` | 실행 중 연결 공간/샘 관측 사용. 기존 스위치 TR_CENTER_ORIENT=true는 축 차이를 줄이지만 기존 지도도 변경 |
| 7. 유닛 상한64 가정 [C] | main:44,77–78,294–295,1159,3781,5592–5594: 60 split, 56 feed/full, 12 herd. can_split은 실제 limit를 확인하므로 cap 자체로 illegal split은 안 함 | custom limit이면 높음; 작은 cap에 영구 미달/큰 cap에서 과소 증식·조기 먹이기 | `un_unitcap_1.map`, `_2.map`, `un_id32768_1.map` | limit64는 기존 상수 유지, 다른 limit만 비율·실제 밀도로 분기; 56/60만 고치는 것으로 종료 전략 전체가 해결되지 않음 |
| 8. 음파 ID/길이 범위 [C] | main:1838–1860,1960–1962: id16bit 중 bit15는 queen_game; ID32768+는 다른 ID로 해석. QH_SCOUT=true에서 길이는 min(len,1023), QH hunter ID16bit(2267). 새 몸이 많이 생기는 지도에서 제한보다 좁음 | 높은 churn/큰 시작 길이면 낮음~중간; 잘못된 leader/먹이기 크기, 사망 상태 혼선 | `un_id32768_1.map`(churn 보장 아님), `un_startlength_2.map`(L1116) | wire format 확장/고ID 직접 목격 fallback. 현재 지도에서도 누적 ID 위험을 배제할 수 없으므로 기존 행동 불변 수정으로 분류하지 않음 |
| 현재 비활성: 12/14bit 셀 [C] | SHARE_SIGHT=false(:161); pack_sight :1777은 >4096에서 false, 따라서 4097 truncation crash는 아님. learn_sight:1820–1829는 4096에서 second sentinel4095를 진짜 ghost로 처리할 수 있음. QH/mouth14bit는 sonar≤128² gate로 현 상태 안전; zone도 off | 라이브12bit 경로 피해 없음; 재활성화/좌표 gate 제거 시 위험 | `un_cells4096_1.map`, `un_cells4097_1.map`, `un_width64_1.map` | 활성화 전에 sentinel 제외 및 더 넓은 format. width65만으로 셀 인덱스가 깨지는 코드는 없음 |
| 현재 비활성: 대칭 고정 [C] | SYM_INFER=false(:186). :1336–1418은 좌우/상하/180도만, 마지막 후보를 영구 고정하고 추정 변을 관측 변과 구분하지 않음; 이후 반증 불검사. 순간 pearl timer 차이로 후보도 제거 | 라이브 피해 없음; 비대칭/다른 대칭에서 켜면 위험 | `un_symmetry_1.map`–`_4.map` | false 유지. 켜려면 직접 관측만으로 지속 반증하고 추정 변 제거; 선언 없음도 엔진에서 허용 |
| 점검상 안전 [C/M] | main:522–553 지도 배열은 동적, 큐2*cells; 고정 배열4/3은 방향/대칭 후보용. constructor payload 최대7,864,320byte(부가 메모리 제외). helper:503–505 실제 길이 읽음; main:1540–1543,1591–1606 queen ID는 팀으로 판별. round9bit는 500 범위 충분. codec key(:58–63)는 256 차원 수용 | 단순 큰 width/queen L≠4/시작 두 마리≠고정으로 확인된 crash 없음; 몸 기억/시간은 별도 | `un_startlayout_1.map`, `un_startlength_1.map`, `_2.map`, `un_edgewrap_1.map` | 고정 배열 확대, A=id0/queen L4 강제 같은 수정 불필요 |

[M] **33/33 지도 로더 통과, notice0**([검증](maps_validation.json)). `EngineModule.run`의 spawn callback에서 중단했다. 봇 차례·대전·네트워크 요청은 0이다. 한 줄 후보는 C++20/O2 native 컴파일만 통과했다.

[E] 미검증: qualifier 서버가 로컬1.2.7과 같은 지도 제한인지, 최대 지도 WASM points/RSS, 카드의 기보 동일성, 유닛 cap 위반 시작의 실제 첫-turn 처리, 높은 누적 ID 재현. 기보 순간/승패 집계는 이번 코드 감사에서 수집하지 않았다. 후속 실행자는 [지도 목록과 목적](maps_manifest.json)을 사용한다.
