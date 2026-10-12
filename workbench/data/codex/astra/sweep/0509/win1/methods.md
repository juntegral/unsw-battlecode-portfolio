이 작업은 brief의 12개 replay와 각 game JSON만 집계했다. bot ID는 replay A 필드 21200, 상대는 B/989로 확인했다. 모든 쓰기는 이 폴더에 한정했다. 네트워크·대전·봇 변경·커밋은 수행하지 않았다.

재현 순서(저장소 루트):

```sh
nice -n 10 python3 -B data/codex/astra/sweep/0509/win1/analyze.py
nice -n 10 python3 -B data/codex/astra/sweep/0509/win1/mechanisms.py
nice -n 10 python3 -B data/codex/astra/sweep/0509/win1/counts.py
```

이 환경은 `nice`의 setpriority를 허용하지 않아 경고를 냈으나 분석 프로세스는 완료됐다. 대전은 시작하지 않았다. Python bytecode 쓰기를 비활성화했다.

기존 reader/counter는 복사하지 않고 import했다. analyze.py는 sweep/0410/win1/analyze.py의 scan과 o1_scan의 질량 장부를 사용하며 OUT을 이 폴더로 바꾼다. mechanisms.py는 audit-threat/audit.py의 scan과 audit-hunt/analyze.py의 trace를 사용한다. counts.py는 o1_qdef의 방어 경로 검사 및 audit-move의 census도 사용한다. audit-move의 이름이 단순한 analyze 의존성은 evade의 Geo 모듈로 연결한 후 복원한다. 기존 코드나 원자료는 수정하지 않았다.

사망 이유는 replay enum 0=벽, 1=자기 몸, 2=다른 몸, 3=머리 충돌, 4=무행동이다. 충돌에서는 turn actor와 victim을 구분했다. 무료 걸음은 차례 시작 길이의 ceil(L/4)이며, 충돌 직전 실제 유료 차감은 질량 장부로 계산했다. 이로써 Maze #297의 5번째 충돌 걸음 전 유료 소모2를 확인했다. 충돌 걸음 자체와 실제 차감은 동일하지 않다.

라운드 말 상태를 재구성한 후 (여왕 길이, 최장, 총 길이)로 사전식 비교한다. 전멸은 우선 판정한다. 뒤에서부터 열세/동률이 처음 나올 때까지 거슬러 간 첫 우세 라운드가 영구우세다. 이는 해당 판의 실제 후속 행동을 알고 정의한 지표이지, 그 라운드에서 이미 확정된 승리가 아니다. 각 replay의 공식 final에 두 진영의 용 수·최장·총 길이·여왕 길이가 일치했고, 시작 질량+섭취−사망 질량−유료 소모=끝 질량 잔차도 각 진영 0이다. hunt의 토큰 장부도 별도로 같은 종료값과 잔차를 확인했다.

행동 일치 수는 개입 수가 아니다. EAT_FIRST는 처음 인접한 빈 진주를 실제 먹은 턴, HEADING_TIE는 r0–11 비여왕의 이전 방향 일치, HERD는 차례 시작의 가장 가까운 아군 머리로 거리가 줄어든 여왕 턴을 센다. 모든 내부 조건을 만족했다고 주장하지 않는다. 출구 비움은 visible 아군의 유일한 빈 이웃 칸이 이동 후보에 있었지만 실제 경로가 그 칸을 점유하지 않은 턴이다. weakhold r217 #45, Devil r41 #26은 이 검사의 반대인 실제 차단이다. 보호 규칙은 살아남는 대안을 찾는 최종검사이므로, 대안이 없을 때의 실패와 구분해야 한다.

QS_KEEP_MIN_UNITS는 차례 시작 L4 여왕·아군 수<6의 실제 분열이다. SPLIT_PORTAL_OK는 r≤100 비여왕 L4의 포털 인접 꼬리 분열로, 일반 분열과 탈출 분열을 분리하지 못했다. 23건의 자식 id를 사망에 결합해 3라운드 내 사망4와 관측 중단0을 확인했다. 이 수치가 해당 스위치가 만든 분열 수는 아니다. QUEEN_DEFEND_STEPS는 기존 정적 도달 대리검사(여왕→적≤3, 아군 L≤4, 아군의 빈 칸 경로 도달 가능)에 실제 박치기를 결합했다. is_leader 및 메시지 기억은 완전히 재구성하지 않았다.

CUT_BODY_LEN은 여왕의 현재 시야에서 머리가 보이는 적(상대 여왕 제외)의 몸이 시야 경계에 닿고 visible parts<4인 여왕 턴이다. 해당 조건271턴 중 실제 길이도4 미만인 턴267, 그중 인접 진주를 먹지 않고 이동 후 생존한 턴2다. 완전히 보이는 짧은 몸도 경계에 닿으면 하한이 커진다. 실제 ring 변경으로 그 진주를 포기했는지는 알 수 없다. floor-cost-candidates.json은 최초 별도 재집계, counts.json의 queen_floor_above_true/queen_floor_missed_pearl이 재현 가능한 같은 수치다.

QUEEN_PORTAL_ALL의 미지는 해당 여왕 프로세스의 직접 7×7 관측 이력 기준이다. 공유·지도 대칭·사적 메모리는 포함하지 않으므로 실제 코드의 미지 출구와 동일하지 않다. 기회2턴에서 모두 다른 방향을 골랐고, 직접 관측 이력에 없는 출구로 이동한 여왕 턴은0이다. 관문이 선택을 바꿨다는 반사실은 없다.

SHORT_EVADE 대용 조건은 비여왕·id>1·L≤4·이동 지시·분열 없음·보이는 아군 머리 수(자기 포함)≤적 머리 수다. 지도 위협·내부 leader·공격 플래그·안전 대안까지는 복원하지 못했다. SMALL_SPRINT_THREAT의 가시 조건은 짧은 비여왕이 visible parts3 또는4인 적 머리를 본 턴이다. REACH_EATS의 정책 영향은 독립 계수하지 않았다. Islands의 4걸음 피격은 실제 진주2를 먹었지만, 공격자 머리가 여왕 판단 때 보이지 않았으므로 이것만으로 REACH_EATS 계산 오류라 할 수 없다.

QUEEN_BOOT의 강한 일치 사건은 정지사망 donor L2/3의 사체 진주를 r300 뒤 여왕 L<6이 먹었으며, donor L×2>섭취 전 여왕 길이인 경우다. Trauma donor #205는 r307 L3으로 정지사망, 여왕은 r309 L5에서 한 진주를 먹고L6이 됐다. 먹이기 의도는 로그가 없어 확정할 수 없다. Maze의 donor L2→여왕L4/5는 기존 길이비 조건도 허용하므로 새 조건 일치 수에서 제외했다. r400 뒤 여왕L<6 무분열109턴도 `can_split` 자체가 참인지 확인한 발동 수는 아니다.

RALLY는 audit-hunt의 송신된 leader 보고·나이≤5·길이비·거리>15 등의 관측 대용 후보다. 225마리/7판의 후보 시작 질량768 중 최종 최장에 간 토큰33, 소실176이며, 이동 뒤 손실도 포함한다. 코드의 is_feeder/is_trader·위협·내부 목표를 다 복원하지 않았으므로 집결이 만든 희생이나 성공을 뜻하지 않는다. FEED_CAP 조건의 무행동 사망125턴 역시 의도한 먹이기와 중복될 수 있다.

사망 주장 신호는 audit-hunt의 wire_decoder로 replay의 sonar wire를 복호화했다. 상태1/3 메시지 이벤트는121,780건/3판이며 전달 대상별 중복과 실패 송신 이벤트를 포함한다. signal-witnesses.json은 각 판의 최초 상태1을 기록했다. receiver=None인 첫 두 예는 송신 생성의 증거이고, Devil r42 #2→#15는 실제 수신자까지 있는 예다. 이는 CARDS의 “신호가 생성되지 않음”을 반박하지만, avenge_hunt가 참이거나 그 경로가 최종 행동으로 채택됐다는 증거는 아니다. 이 witness 파일은 raw 이벤트를 wire_decoder로 순회해 최초 상태1/3을 찾아 별도 생성했다.

모든 findings는 보고서에서 [M] 재계산, [C] one10 소스, [E] 추론으로 표시했다. 내부 DEBUG_LOG가 꺼져 있고 dragonLog 이벤트0이어서 독립 발동 수와 제안 전/후 비교를 복원하지 못했다. CPU, on/off, 강한 상대, 미지지도 일반화, 사냥 실패의 의도, 지나친 진주의 안전성은 검사하지 않았다. 새 카드 제안은 하지 않았다.
