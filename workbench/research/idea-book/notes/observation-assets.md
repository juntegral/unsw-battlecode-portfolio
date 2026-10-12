# 관측·탐색, 실행 중 지도 모형, 구조 위험과 공유 자산

[사실] 읽은 시각 확인: `date` 결과 2026-10-01 23:26:34 KST. 이 메모는 새 연구가 아니라 기존 문서·도구 머리말의 종합이다. 새 경기·네트워크·업로드·커밋 없음. 사용자 허용 쓰기 범위 안의 이 파일만 작성했다.

## 1. 작은 조각의 관측과 정보 공유를 무엇에 근거해 제안할 수 있는가

### Takeaway

[해석] 새 팀에 우선 제안할 것은 **여왕을 탐험시키기보다 작은 조각이 관측하고, 확인한 구조를 수명 있는 요약으로 공유하는 체계**다. 팀 전체의 시야를 개별 프로세스가 이미 안다고 가정하면 설계가 틀어진다. 정찰 정책은 아직 가설이고, 관측 가능성 연구는 구규칙에서 나온 고정 경로의 상한·조건부 공유 입력이다.

### Cited Findings

- [사실, 사용자 정의] 탐색은 “작은 조각들이 옵저빙하는거”, 적 접근·지형·샘을 보고 음파로 알리는 것이다. W12는 열림이며 구역 분담·대칭 우선·샘 찾기는 가설이다. — `docs/WORKQUEUE.md` §W12(17:05 정의).
- [사실, 구규칙 온라인+로컬 관측] `observability.md` 모집단은 2,460경기/2,823선택 팀·경기: W1 로컬 240/240, 우리 온라인 1,260/1,260, top 960/1,323. top 15지도·배치 층마다 SHA256 64경기, 기록 순위≤10인 편. 로컬 독립 지도·시드 조건 N=30. 상위권 번들 5지도 N=0이다. — `research/observations/observability.md` 방법과 N.
- [사실] r30 팀 누적 시야: 우리 W0–W12 **47.6%(N=1050 팀·경기)**, 상위권 **58.9%(N=1323)**. 같은 시각 개별 살아 있는 프로세스 직접 관측: **16.5%(N=5138)**, **13.7%(N=14677)**. r50 우리 프로세스 own **19.5%**, own+확정 미러 **25.3%(N=5841)**. 이득을 “각 봇이 지도 절반을 안다”로 바꾸면 틀린다. — `research/observations/observability.md` 머리/§2/최종 table.
- [사실] 새끼는 새 프로세스이며 부모 메모리가 자동 복사되지 않는다. 현재 음파는 위치·길이·목표 요약으로 완전한 칸·간선 표를 보내지 않는다. 연구의 부모 전체 상속은 반사실 상한이고 실제 상속 구현 N=0이다. — 같은 파일 §2.
- [사실] r50 우리 W0–W12 살아 있는 프로세스 N=5841에서 부모 전체 상속−own **+4.44pp**, 칸 패킷−own **+0.20pp**, 대칭 요약−own 미러 **+2.79pp**, 완전 창 패킷−own **0.00pp**. 상위권 N=19751은 각각 **8.83pp / 0.35pp / 3.39pp / 0.03pp**. 고정 실제 음파 접촉에 필드를 대신 싣는 조건부 재현이며 신규 탐색/공유 정책 실행 N=0이다. — 같은 파일 §2 패킷 표.
- [사실] 제안 패킷의 64비트는 PROTOCOL3 교환 뒤의 조건이다. 최초 루트 입력은 교환 전 32비트이고 자식은 프로토콜 버전을 잇는다. 표본은 W,H≤64를 가정했고 r200까지 최대 프로세스 ID **1125(경기 N=2,460)**다. 좁은 ID 비트폭은 별도 확인 대상이다. — 같은 파일 §2.
- [사실] 온라인 실제 countdown으로 빨라지는 대칭 시각과 리셋 분류 정확도 **N=0**. 기보가 countdown·spawn gap을 숨기므로 관측 칸 spawn support는 정답 지도를 시야에 투영한 값이다. 상위권 기존 알려진 지도 이동을 미지 지도 메모리 모델에 투영한 것으로, 상위권이 실제로 모르는 지도에서 정찰한 행동을 측정한 것이 아니다. — 같은 파일 방법과 N.
- [사실] 우리 W0–W12 팀 대칭 확정은 r10 **625/1050**, r25 **793/1050**, r50 **869/1050**. 같은 프로세스 자체 확정은 r25 **1506/4924**, r50 **2316/5841**다. 정답 대칭 제거/잘못 확정은 전체 N=2,460에서 **0**이나, x축 반사 지도 표본 **N=0**이다. — 같은 파일 §3.
- [사실] 샘은 정답 평균 gap μ≤12, 추정 시도율 λ=1/μ다. 몸이 있어 생성하지 못해도 countdown은 리셋된다. 따라서 생성 시도율은 실제 생성/섭취율과 다르다. 연속 리셋 gap gate4 로컬 r50 팀 N=240: **P=99.95%, 전체 R=38.8%, 상대 λ MAE=9.7%(rate 타일·편 N=2094)**. 프로세스 직접 분류 r50 N=1929: **P=100.00%, 전체 R=4.5%**. — 같은 파일 방법/§4.
- [사실] 우리 팀 r50 인증 주머니: **P=100.0%, R=59.2%, TP/FP/FN=22327/0/15368, 팀·경기 N=1050**. 단일 프로세스 가중 대표 표본 r50: **P=100.0%, R=17.1%, 표본 N=1050/대표 프로세스 N=5841**. “미지를 벽”으로 둔 팀 주머니 P는 r50 **60.3%**, 프로세스 표본 **41.0%**다. — 같은 파일 §5.
- [사실] 인증 주머니는 단순 optimistic pruning만이 아니라 **제거 성분에 접한 모든 간선 관측 + 모든 포털 짝 해결**을 요구한다. known subgraph의 남은 2-core는 순환의 양성 근거이고, 그 밖은 아직 unknown일 수 있다. 수확 가능한 입구/왕복/공급까지 검증 N=0이다. — 같은 파일 §5.
- [사실] 우리 팀 f-bin 미러 정확도 r10 **80.3%**, r25 **84.3%**, r50 **88.6%**, 각 팀·경기 N=1050; r50 알려진/미러 칸·편 N=721675. 최초 아군 머리 전체를 알고 있다는 가정이며 미관측 전체의 정확도가 아니다. — 같은 파일 §6/최종 table.
- [사실, 시야 기하] 한 칸 이동의 새 7×7 관측 창 추가는 최대 **7칸**, 겹치지 않는 포털 이동/새끼 첫 창은 최대 **49칸(N=1 정의)**이다. 포털 너머로 시야가 뻗지 않는다. — 같은 파일 §7.
- [사실, 운영진 힌트/구규칙 본선] 운영진은 Maze의 진짜·가짜 2×2 샘/음파 타이밍, Australia 먼 태즈메이니아 공급, 기지에 갇힌 팀의 탐색 실패를 지적했다. “탐색 로직을 고치고 좀 더 위험을 감수하라” [22:22][40:06], “그러라고 음파가 있다” [15:55]. 이는 권위 있는 설계 힌트이나 기보 행동 검증의 N은 문서에 없고 확인 목록으로 남아 있다. — `research/observations/sprint-commentary.md` §1–3/§6.

### Inferences: 카탈로그에 쓸 아이디어

1. **작은 조각 정찰자 / theme=exploration and observation / status=가설.** [해석] 여왕 생존·암살을 위해 필요한 미지 통로·적 접근·샘·포털 반대 끝을 L2–3 일꾼이 보도록 역할을 나눈다. 당김은 겹치지 않는 창, 대칭 후보 간 불일치 칸, 주머니 목을 목표로 하고, 정보가 회수될 연락 경로를 동시에 둔다. **구현:** 관측 메모리 갱신 뒤 정찰 gate + 정보 이득을 후보 행동의 첫 action 항으로 넣고, 여왕의 안전/급식 gate가 먼저 작동하도록 한다. **첫걸음 주의:** 현재 시야의 미지 가치·정적 위험을 미래 DFS 매 단계에 같은 값으로 반복하면 가상 탐색 이득/회피가 과장된다. **위험:** 싸움·생산 일꾼 감소, 정찰자는 보지만 전달 못함, 적 머리 새끼/포털 기습, 여왕 단독 시작 지도에서 분열이 여왕을 줄임. **근거:** `observability.md` §1–2/§7; `WORKQUEUE.md` W12; `sprint-commentary.md` §1–3. 실제 새 정찰 정책 N=0.

2. **확정 대칭 + 작은 요약부터 공유 / theme=exploration and observation / status=가설(조건부 공유 재현만 확인).** [해석] 첫 머리/계보/대칭 후보를 먼저, 포털 두 끝/리셋 표본 수·합·출처를 다음에 보낸다. 출생 상속 프로토콜은 진짜 구현해야 한다. **구현:** 프로세스별 observed-edge/spawn/portal 메모리, 대칭 후보 교집합, source·timestamp·TTL, 조각 수신 완료 조건. 중복 리셋 요약은 합산하지 말고 더 많은 동일 origin 요약으로 교체한다. **첫걸음 주의:** 공유한 확정 정적 사실을 그래프로 반영하는 것은 전 경로에 유효하지만 현재 접촉/적 위치 위험 가격은 첫 action/다음 차례 기준으로 별도 처리한다. **위험:** 메시지 손실·몸/켈프 차단, PROTOCOL3 이전 32비트, ID truncation, 새끼 지연, 틀린 대칭의 오염. **근거:** `observability.md` §2–3/§7; `versions/v1.6.1/VERSION.md` §6.

3. **샘을 발견과 분류로 나누기 / theme=map-independent runtime rules / status=가설(고정 경로 추정 기제 재현).** [해석] 본 spawn support, 연속 리셋 표본, 추정 시도율과 신뢰도를 각각 저장해 여왕 식량/정찰 구역을 정한다. **구현:** 연속 관측 expiry 이동만 gap으로 세고 표본 수·합 유지; ≥4 reset은 기존 연구 출발 gate이며 배포 최적값이 아니다. 생산량은 점유로 막힌 시도와 실제 출현을 분리한다. **첫걸음 주의:** 현재 진주/카운트다운 반복 보상과 현재 샘 점유 벌점을 DFS 단계마다 그대로 쌓지 않는다. **위험:** μ≈12 경계, 느린 샘 뒤늦게 발견, 점유 검열, 관측 끊김 gap 합, 공유 중복, 이 표본에서의 높은 P를 새 지도로 보증. **근거:** `observability.md` §4.

### Gaps

- [사실] 신규 정찰·상속·전용 포털 패킷·최초 머리 census 정책의 실제 실행 검증은 위 연구에서 N=0. 새규칙에서 상위권 정찰 행동에 대한 완성 연구는 이 배정에서 찾지 못했다. — `observability.md` 방법/§2/§7; `WORKQUEUE.md` W12.
- [해석] 최소 정찰자 수나 정보 가중치를 수치로 확정할 근거가 없다. 최초 실험은 새 정보 발견/개별 프로세스 반영/여왕의 실제 경로 변경을 묶어 사전 등록해야 한다.

## 2. 미지 지도 엔진과 막다른 굴·미로·포털에서 무엇을 유지하고 무엇을 버렸는가

### Takeaway

[해석] FORTRESS 기본은 **현재 구현의 안전한 연결 경로**이지 흉내 상대 승패로 입증된 최적 엔진이 아니다. 새 지도에서는 지도명 인식을 끄고, 검증한 관측 구조를 기능 gate에 연결해야 한다. 좁은 입구와 막다른 나무를 구별하고, 사망 흔적을 곧바로 정책 실패로 해석하지 않는 것이 핵심이다.

### Cited Findings

- [사실, 구현 구조] v1.3 기반의 unknown 경로는 DEFAULT_POLICY FORTRESS MODE0. 관측·symmetry/mirror·sonar·belief/threat/areaSafety/DFS는 남지만, SW 흩어지기 sd/frontier allocation/2-core/harvest, PT DEAD/POCKET/ROOM/EXIT 가격, v1.4 opening은 자동 추론되어 켜지지 않는다. `mapNone`은 unknown edge를 blocked로 만들지 않는다. 일반 unknown edge는 torus 인접 취급/벌점 **−.3**, 미확정 portal endpoint는 **−2**와 probe/commit을 쓴다. — `docs/arch/unknown-maps.md` 인식 스케줄/table/fallback/관측 기반 기능.
- [사실] DEFAULT_POLICY를 SWARM으로 바꾸는 것만으로 `makeConfig`의 nullptr `fam` strcmp 충돌이 있었다. 지도 표 없는 SWARM에서 핵심 공간 기능이 돌지 않고 분열만 남는 것이 W1 엔진 유지의 기제 근거다. — `AGENTS.md` 핵심 사실; `docs/WORKQUEUE.md` W1/W2; `docs/arch/unknown-maps.md`.
- [사실, 구규칙 local] stronghold는 Trauma와 같은 **48×24**. v1.6 잘못 인식 **8/8판(46프로세스)** → v1.6.1 **0/8판**, 번들 전체 **0/40**. 하지만 시작/주변을 복사한 X13 함정 각 N=52에서는 잘못 결정한 프로세스 **119(시작50/새끼69) → 58(시작50/새끼8)**, 판 **31/52 → 26/52**, 잘못된 행 차례 **423 → 201**. 시작 증거까지 같으면 시작 관문도 잘못 믿는다. — `versions/v1.6.1/VERSION.md` §5.2/§6/§7.
- [사실, 구규칙 local] 확인 아군 음파를 기다리는 관문은 아는 지도 새끼 첫 차례 결정 **55%**였고 Trauma 보류 중앙값 **7턴**, p90 **51턴**, **406 중112**가 끝내 결정하지 못했다. 새끼 첫 10차례 Trauma S **100→52%**, hv **8.0→2.1%**, CONV2 **51→25%**. 이는 맵인식 지연 비용이지 정찰 기억 공유 정책의 효과를 입증한 결과가 아니다. — `versions/v1.6.1/VERSION.md` §5.3/§6; `WORKQUEUE.md` W2.
- [사실, 현재 결정] qualifier는 모든 지도에서 `QUAL_NO_MAPID`로 인식을 끄는 A안. v1.7은 r0부터 unknown 경로다. — `AGENTS.md` §1/§3, `DECISIONS.md` 15:15/16:52, `versions/v1.7/VERSION.md` 머리.
- [사실, 구규칙 known-map 연구] map-atlas는 원자료 top **17,331→17,057**, 우리 W0–W12 **1,050**, 이전 **630**, 로컬 참고 **372→204**. 행동 네 부류(F/F+C/SE/EL), 코드 두 엔진이라는 제안은 알려진 10지도/15판본의 **해석**이다. 실루엣 **0.32–0.46**으로 연속체에 가깝다. 선택 정독 표는 **17판**, §1.2는 “13판”으로 적혀 있어 숫자를 하나로 고치지 말아야 한다. — `research/observations/map-atlas.md` §0.2/§1.1–2/§2/§7.
- [사실, 원연구의 가설] area≤**1,100**, 시작 왕≥**8**, cycle≥**L+4**, 생산 pocket/guard를 r10–30 확인하면 요새 후보를 검토한다는 gate는 **[해석], 최적 엔진 분류 검증 N=0**이다. W9가 이를 “상위권은 ...일 때만 요새형” 사실처럼 요약했지만 원문을 우선한다. 완전 고립 증명 때 전진/적접촉 목표 0도 설계 후보다. — `research/observations/general-principles.md` §6(요새 후보 문단)/§11; 과장된 요약 `docs/WORKQUEUE.md` W9.
- [사실, 구규칙 도감] 알려진 Portals 두 진영은 큰 성분 **240/240**, 연결 없음. 상위권 N=1958, 멈춤48 제외; r300 뒤 왕 사망은 자기충돌, 승자 **0.27/판**, 패자 **0.54/판**. 우리 N=90 r300 뒤 왕 사망31은 갇힘20/아군머리11이다. 일반 포털 지도도 외딴형이라고 읽으면 틀린다. — `map-atlas.md` §5.4.
- [사실, 구규칙 개막 연구] `opening-book.md`는 동결06:38:04 원자료 **19,680판(상위13,714/온라인1,421/로컬고유4,545)**, 멈춤192 제외/판본미확정7 별도, 정독항목88. Devil/a r0–10 분열/판은 승자 **2.97(N=878)** vs W12 **3.00(N=6)**이나 최초 중앙 도착 **r14.22(N=878)** vs **29.67(N=3)**, r25 중앙몫 **54.1%(N=878)** vs **7.1%(N=6)**. 분열 수만 복사해도 진로 유지/수확 역할이 없으면 도착이 늦다. — `research/observations/opening-book.md` 머리/핵심 관측/§1.
- [사실, 실패에 대한 정정] 초기 W15 보고는 막다른 끝 사망 **58%(2,720/4,650)**였다. 18:57 진단은 v1.7 20지도×양편 사망 **4,069**, 가지 안 **2,838**의 원인을 시작고리 **1,995**, 미지 무순환 진입 **419**, 이미 갇힌 뒤 **250**, 자발분열 새끼 **125**, 자유 알려진 가지 진입 **4**로 나눴다. X_01 A는 먹음 **825/잃음824**, 온라인 Autarky A **749/744**, Dilemma A **738/749**. 분열 없으면 시작 드래곤은 r3 L16 사망이다. — `versions/v1.7/VERSION.md` §17; `DECISIONS.md` 18:57; `WORKQUEUE.md` W15 정정.
- [사실] “출구가 확인된 1칸 통로만” 규칙의 알려진 지도 비율은 실제 막다름 **48/806(6%)**, 통로 진입 **36/298**. 나쁜 이동 하나당 좋은 이동 약16개를 막으므로 구현하지 않았다. 1칸 입구가 막다른 곳이라는 등식도 사용자가 부정했다. — `v1.7/VERSION.md` §17 진단3; `DECISIONS.md` 18:57/19:02; `WORKQUEUE.md` W15/W16.
- [사실, 구규칙 local 기제] W15a-s는 알려진 유한 나무+새끼L/진주합<4+r500 전 경로종료 때만 자발분열을 막고 탈출분열을 제외한다. `ds`는 **2/40판**, S_03 A r135부터4번/X_07 B r152 1번. 나머지 **38판 사건 동일**. S_03 기준 새끼#24는 진주없는7칸 가지에 태어나 r139 죽지만 s는 분열을 안 한다. 가지 안 진주3–8개로 L4 탈출분열이 가능하면 허용했다. 끔은 **40/40 동일**. — `v1.7/VERSION.md` §17–18.
- [사실, 기제 실패] W15a-k는 **8/40판** 모두 이미 갇힌 L2–3이 죽을 장소만 바꿨다. 목적의 자유상태 수확불가 진입은 없었고 기존4건은 수확 가능했다. `dk 6130`은 모든 후보 같은 가격도 포함한다. k는 기제 이득 없음으로 끔. t/p는 금고 고리를 풀어 조각을 L2로 흩어 들이받히게 했고 껐다. — `v1.7/VERSION.md` §18(구규칙).
- [사실, 신규규칙 재점검 한계] v1.8 cand·cand2 **132판**에서 `ds` **0번**. 따라서 이 집단에서 무해·불발인 것으로만 읽고 s의 1.2.3 발동 효과를 검증했다고 주장하지 않는다. — `versions/v1.8/VERSION.md` §4.
- [사실, 1.2.3 구조적 함의] Autarky/PD/X_01/X_05의 시작 드래곤이 여왕 id0/1이고, 옛 탈출분열은 머리2칸(여왕)을 가지 끝에 남겨 r4 사망한다. 나갈 수 없다고 판정한 것은 이 시작 배치이며 모든 주머니 여왕에 대한 불가능 주장으로 확장하지 않는다. — `v1.7/VERSION.md` §18; `DECISIONS.md` 20:39.

### Inferences: 카탈로그에 쓸 아이디어

4. **인식 끈 실행 중 지도 모형 / theme=map-independent runtime rules / status=가설(인식 끄기·기존 fallback은 기제 확인).** [해석] 칸/간선/spawn/포털/대칭/certified core를 프로세스별 누적해 기능에 직접 공급한다. 표준 unknown row와 nullptr 방어, 모든 함수의 unknown 상태를 명시한다. **구현:** ingest 뒤 구조 갱신 → 기능별 증거 gate → 목표; “r30이면 완성” 플래그 대신 확인된 간선·리셋 수를 쓴다. **첫걸음 주의:** 정적 구조의 경로 제약은 DFS에 반영하되 현재 적 위협·탐색 당김 가격은 action 단위와 미래 단계 모델을 분리한다. **위험:** unknown=벽 FP, stale core/pt state, 잘못 대칭, 비가역 mapNone, 포털 누락, CPU, 전선 공급 오차. **근거:** `unknown-maps.md`; `observability.md` §4–6; `v1.6.1/VERSION.md` §6–7.

5. **증거 있는 요새와 지역 생산의 선택 / theme=engine choice / status=가설.** [해석] 새규칙의 요새는 고정 여왕을 지킬 순환/성장 여유/급식 도착 경로를 증명했을 때 후보로 두고, 나머지 지역 생산은 별도 일꾼이 맡는다. 1100/8/L+4는 출발 gate이고 확정법이 아니다. **구현:** W3 structural input가 마련되면 먼저 shadow decision 기록, 여왕/백업 분리, map label 없이 runtime policy gate. **첫걸음 주의:** 엔진 교체로 새 목표 당김을 DFS 전 단계에 과잉 누적하지 않고 초기 후보값·early return·기존 gather 덮어쓰기를 함께 확인한다. **위험:** 구규칙 longest를 queen으로 이름만 치환, 고립을 짧은 관측만으로 확정, SW 공간 부품 없이 엔진만 바꿈, 여러 기능 동시 변경. **근거:** `general-principles.md` §6/§11(검증N=0); `map-atlas.md` §0.2/§2; `WORKQUEUE.md` W1/W9.

6. **수확 가능한 가지와 막다른 새끼 분열을 구별 / theme=dead ends, mazes and portals / status=구규칙 기제 확인(s), 새규칙 발동 가설; 전면 미지굴 금지/k/t/p는 시도·실패.** [해석] s의 좁은 gate를 유지하되 L4 생산·탈출 가능성이 있는 가지 수확은 남긴다. 여왕의 가지 진입은 희생 일꾼과 별도 gate로 다룬다. **구현:** `regionAhead` 알려진고리0/미지1/유한나무2, cap160; voluntary child 앞→L+진주<4→남은 경기시간 조건. 긴 여왕의 몸/성장 여유와 동점 모드는 별도. **첫걸음 주의:** k=60을 모든 DFS 단계에 반복하지 않는다; 바로 이번 action 진입/질주 실제 중간 칸에 필요한 판정만 하고 후보 순위 변화와 대안 가능성을 기록한다. **위험:** 생존 금고를 병적인 고리로 오진, 폭1 입구를 나무로 오진, 예상 진주가 사라짐, unknown 포털이 cycle로 열림, 새규칙 s0 발동을 통과로 과장. **근거:** `v1.7/VERSION.md` §17–18; `v1.8/VERSION.md` §4; `WORKQUEUE.md` W15 정정.

7. **미확정 포털은 정찰·연결학습과 여왕 위험으로 나누기 / theme=dead ends, mazes and portals / status=가설(기존 generic 관측/probe 구현은 존재).** [해석] 작은 조각은 정보 이득이 큰 반대 끝을 찾고 여왕은 알려진 안전 짝/충분한 통로에서만 자발 통과한다. 포털 ID·양끝·방향을 저장/공유하고, 미해결 출구는 적 ingress 가능성으로 남긴다. **구현:** generic `World.across` 포털 짝 학습을 확장하고 DEAD/POCKET/ROOM/EXIT를 runtime 인증으로 대체; 머리 위치와 같은 깨끗한 음파 probe freshness, 확인된 포털을 BFS/2-core/도달에 넣는다. **첫걸음 주의:** 현재 출구 적 도달 위험·blind 진입은 첫 action 끝 칸에 주되 장거리 DFS에는 시간에 따른 불확실성/도달을 따로 둔다. **위험:** 시야는 포털 너머로 연장되지 않음, ID 숫자의 대칭복사 오류, 짝 미해결인데 일반 edge로 근사, 한정32×16 ptmap 강제 활성으로 static array 위험, 새규칙 긴 적 ingress. **근거:** `unknown-maps.md` table/관측 기반; `observability.md` §3/§5/§7; `WORKQUEUE.md` W3 포털; `v1.8/VERSION.md` §3 Portals A1 L3 여왕 r10 blind crossing/r12 죽음.

### Gaps / 기존 요약을 정정할 때 주의

- [해석] `WORKQUEUE.md` W9의 요새 gate를 [사실]로 인용하지 말 것. 원연구가 검증 N=0라고 명시했다.
- [해석] `map-atlas.md`의 “Portals 로컬 검증이 곧 온라인 값”, 끝 최장 문턱·예측 승률로 채택하는 권고는 현재 사용자 원칙(14:37)에 의해 방법론으로 재사용하면 안 된다. 알려진 Portals 구조와 구규칙 관측은 남지만 미지 지도 정책 판정 근거는 아니다.
- [해석] `sprint-commentary.md` §0의 “최장 관찰을 여왕으로 바꿔 읽는다”는 목적 재정의이지, 구규칙 winner-longest 연구를 queen 정책 효과로 재증명하지 않는다.
- [사실] `DECISIONS.md` 21:35의 **91%(240/264)**는 당시 잠정 요약이며 바로 같은 항목에 **승자 여왕생존8/패자16이 규칙과 모순이라 재집계 요청**이라고 적혔다. 정확 검증된 새규칙 모집단 사실로 쓰지 말고 잠정값/재검증 중이라고 표시한다.

## 3. 무엇을 새 팀에 공유할 수 있고, 어떤 한계를 함께 전달해야 하는가

### Takeaway

[해석] 공유 가치가 큰 것은 테스트 지도·기보 해독/장부·판면·기제 진단·독립 검증 파이프라인이다. 숫자의 기준 시각과 규칙 flag를 함께 가져가야 하며, 지도복원을 원본 완전 복원이라고 부르지 않는다.

### Cited Findings: 자산 목록

| 자산 | [사실] 문서화된 수/범위/명령 | 원출처와 중요한 제한 |
|---|---|---|
| 생성 시험장 | **35개 S6/M8/L6/R2/X13**, seed20261001. 기존 전수 **38파일/20고유**, 기존 형식대칭 **38/38**, 생성 엄격 **34/35**. 범위안12/스트레스23. 구규칙 smoke **48/48 시작·로딩·완료**, 오류0/timeout0/CPU max32.2M | `maps/generated/MANIFEST.md` 머리/한계; `research/observations/mapgen.md`; `exp/mapgen/SUMMARY.txt`; `WORKQUEUE.md` W8. organizer 분포의 표본 아님. **gen_X_04**는 보존한 Portals 주변의 작은 성분4개×각2칸으로 연결성 예외, 모든 시작 큰 성분/양팀 도달. smoke는 새 runtime 기제 효과를 입증하지 않음 |
| 인식 함정 | X13 중 X01–10은 시작/반경6 근처를 보존한 원본 함정; 외부 변/support 40% 이상 변경 기준은 가변 영역이며 전체40% 아님 | 같은 원출처 인식함정/한계. 같은 크기뿐 아니라 시작 증거까지 동일하게 만들어 인식 gate의 한계를 재현 |
| 본선 복원 | **7지도 Australia/Islands/Maze/Stripes/Tower Defense/Around UNSW/weakhold**, **224기보/32시리즈×7**, 지도당32기보. 알려진 **10종/15배치/60가림 기보** 구조 일치, 비가림 **10종/20기보** TILE까지 정확 일치. 본선 형식대칭7/7, 엄격연결5/7 | `maps/sprint/README.md`; `exp/sprint-maps/SUMMARY.txt`; `DECISIONS.md`20:00/20:45. **구조만 복원, gap은 검열균등 추정**. initial pearls/RNG seed/bots 복제 안 함. 미관측묶음0..0은 비생성의 증명 아님. Islands23성분/Stripes3성분은 원본 고립구역 보존 |
| 복원 포털 | 기보 embedded text와 match.map 배열로 변 종류/포털id·짝을 대조해 복원. pair-list만 있으면 순서 번호로 ID를 부여하며 embedded text가 원래 ID의 빈 번호를 보존 | `tools/replay2map.js` `fromMap()`; `maps/sprint/README.md` 머리/검증. **포털 짝을 통계로 추정했다고 쓰면 원문과 충돌**한다. 추정된 것은 gap/생성·샘·공급; 배열만 있는 입력의 원래 포털 ID 복구와 pairing 보존은 구별 |
| 번들 미지 테스트 | **arena/big_empty/Colosseum/default_small/stronghold 5개**. bundled dilemma는 PD 중복 | `AGENTS.md` 핵심 사실; `mapgen.md` 전수조사. 알려진 지도 표를 끈 추가10지도와 구별. 이5개는 이미 로컬 점검에 사용됐으므로 “미사용 최종 holdout”으로 과장 금지 |
| proxies | `bots/proxy4_king`, `bots/proxy4_swarm`을 기제를 발동시킬 시험 도구로 사용, `proxy4_elim`도 파일 존재. king style은 후반 최장에게 모여 희생, swarm style은2+2/작은조각교환/지역큰아군희생 | `AGENTS.md` §4.6–7; `bots/proxy4_king/style.hpp`, `bots/proxy4_swarm/style.hpp` 머리말/상수. 머리말은 proxy3를 적는 오래된 설명이며 실력 인증 아님. SPAWN_KNOW=true의 아는 지도 의존/구규칙 최장 기준 목적이 있어 queen 적응 proxy로 자동 간주 금지 |
| 여왕 사냥 test bot | `exp/q2/bot-hunter`: v1.8+Q2c. 새규칙 queen 안전의 구체적 가혹상황을 만든다 | `DECISIONS.md`21:27/21:39; `v1.8/VERSION.md`. 일반 elite 대리 성능으로 주장 금지 |
| 질량 장부 | `tools/mass_ledger.js`: pearl origin, death cause, splits/sprint 비용, longest/lineage, reconciliation. `perGame(R,{rules:'123'},hooks)` 또는 **`UNSW_RULES=123`** | 도구§perGame 주석/`AGENTS.md`§1/`DECISIONS.md`22:14. 우선순위 **info.rules > env UNSW_RULES > '110'**. flag만으로 `king`/lin이 queen으로 바뀌지 않음(정의는 순간최장/최종최장 계보). 캐시는 이미 있는 판 건너뛰므로 구규칙 캐시를 새flag 실행만으로 올바른 캐시라고 가정 금지 |
| 기보 해독·features | `tools/top_features.js` 123 free steps 지원 | step simulation은 **env UNSW_RULES > '110'**, default old. 분석 전에 원자료/규칙 epoch/캐시를 맞춘다 |
| reach | `exp/w7/reach.js`: 행동 끝 칸 적 한 행동 도달, safe alternative, avoidable/forced 노출, latent higher-id split-child, 다음차례 전 ram outcome, `--sets`, `--population`, `--show`11×11 그림 | 스크립트 머리말+코드. **별도 BFS 반경 max(1,min(L−1,6))**, 대안1-step/L≥3 2-step은 old-rule 모델. `UNSW_RULES=123`으로 장부만 고쳐도 reach 자체가 새규칙에 맞지 않음 |
| boxing | `exp/w7/boxing.js`: 행동으로 아군 출구≤1(box)/0(seal), 다음2턴 사망, crowd≥5heads in7×7, `--sets/--population` | 스크립트 머리말. 이동 직후 정적 몸으로 계산하며 미래 행동 스케줄 전체 모델 아님; ledger 규칙flag 필요 |
| forced | `exp/w7/forced.js`: 합법대안 모두 적 도달이면 forced, 3자기턴 전 상태/비forced 대조; nearest enemy/ally, balance8, forage, length | 스크립트 머리말/코드. **reach와 같은 old L−1 cap6/2-step 대안**을 따로 갱신해야 새규칙 안전 판정에 쓸 수 있음 |
| drift | `exp/w7/drift.js`: 가장 가까운 아군 거리≥3인데 더 멀어지는 이동, 그 끝 balance8<0; 거리분포 | 스크립트 머리말. Manhattan 비교로 벽/포털 실제 거리와 다름; ledger flag 필요 |
| 실제 판면 | `eval/board.js <replay> <mapName> <variant a|b> <ourTeam A|B> [rounds comma list]` ASCII; 경제/전환 timeline, sf/sd tags | 스크립트머리말/`docs/arch/README.md`. `perGame` 사용하므로 **`UNSW_RULES=123 node eval/board.js ...`**로 새규칙. `exp/w7/driftpic.js`, opening heatmaps/boards, atlas SVG는 저장된 보조 자산 |
| replay2map | `node tools/replay2map.js <기보> <출력.map> [추가기보...]`; `--audit` | `tools/replay2map.js` 머리말/`maps/sprint/README.md`. **이번 작업에서 실행 안 함**. --audit는 exp/sprint-maps에 쓰므로 사용자 쓰기 범위 밖 실행하지 않음 |
| 지문 | `tools/fingerprint.js` 기존 `.replay` hash, `--same`은 **새 게임을 실행** | 머리말. instruction/timing/indicator text 제외하고 actions/moves/splits/deaths/pearls event 해시. 이번 작업에서는 명령 실행 안 함 |
| top 데이터 | **21,568판**, 2026-10-01 11:10 결정에서 수집중지 | `DECISIONS.md`11:10, `observability.md`방법. `research/KNOWLEDGE.md`01:40 **16,681행**, atlas02:50 **17,331원자료**는 서로 다른 동결시각; 지금 exact21k를 새로 세지 않았다 |
| elite 데이터 | 처음 상위10팀 모든 상대/5분수집; 19:29 사다리초기화 뒤16강16+3.14159265/Sponge/WeHaveQuizzes의 **19팀 고정목록** | `DECISIONS.md`11:10/19:29; `WORKQUEUE.md`Q. 현재 파일전체 exactN은 이 메모에서 추정/재계산하지 않음. 구규칙/새규칙 era와 상대강도가 섞임 |
| 본선 대진 데이터 | `data/online/sprint-bracket/` **224판(32시리즈×7)** | `DECISIONS.md`20:00; `sprint-commentary.md`머리. old-rule unseen board 행동자료; queen 정책 성능 자료 아님 |

### Cited Findings: 방법·Codex 파이프라인

- [사실] 기존 연구 표준은 **전체 모집단 스크립트 → 크기 있는 부류 → 사전 선택 규칙의 대표 기보 정독**이다. `opening-book.md`는 표본선별 JSON/원래set/물리좌석/자식계보를 보존하고 `tables.json`을 먼저 쓴 뒤 정독·보고서를 썼다. `observability.md`도 population/tables/verification을 남겼다. — `opening-book.md` §1–2; `observability.md`방법/독립재계산; `map-atlas.md` §1.2–4.
- [사실] observability 독립검증: 머리/창/상속/음파 경기 **2460**, 그래프 대표경기 **40**/그래프 **4320**, 리셋 로컬경기 **240**, 전체집계 경기 **2460**, 표의 모든 불일치 **0**. 대칭 축 라벨을 뒤집어 읽은 오류는 `axis-label-correction.json`으로 정정하고 재계산했다. — `observability.md` §3/독립재계산.
- [사실] opening 독립경로는 primary 훅 없이 dragonUpdate/split을 따라 원자료 **19,680** 재집계/멈춤제외 **19,488**에서 분열tuple/r25bin 불일치 **0**. decoder·판본 배정은 공유한 한계를 기록했다. — `opening-book.md` §2.
- [사실] atlas는 원 산출물 검산 뒤 경로거리·희생률의 시간축·재계산·캐시비교를 더했다. Manhattan으로 Portals 왕 노출 **50%가 적6칸 안**처럼 나오는 문제를 발견해 `kingpath.js`를 만들었다. 이는 도구의 지표 정의가 전략을 잘못 유도할 수 있다는 구체 사례다. — `map-atlas.md` §1.4.
- [사실] `tools/codex-continue.sh [task-id] [extra instruction]`는 AGENTS/WORKQUEUE→작업, diagram/pre-register/identity/unseen check를 지시하고 `exp/codex-runs/` 로그/last.txt에 남긴다. wrapper 자체는 큐/결정 수정·커밋 지시를 포함하므로 **현재 IDEA BOOK 제한 scope에서는 실행하면 안 된다**. — 스크립트 머리말/PROMPT.
- [사실] 방법원칙은 로컬proxy 수치로 채택/기각하지 않기, (a) 상황발동 (b) 실제판면변화 (c) 오류/CPU/오인식/끔 동일성, 흐름도 꽂을 자리·덮어쓰기·terms 세기 비교·예상판면·VERSION 사전등록이다. — `AGENTS.md` §4; `docs/arch/README.md`.
- [사실] 정적위협을 모든 DFS 단계에 다시 매기면 미래경로 벌점이 이어져 첫칸 순위가 안 바뀔 수 있었다. W7a′는 첫 action 끝칸만 무할인3배로 매겨 관측노출 **1.4%→1.1%**. 이는 특정 구규칙 local 기제의 교훈이며 모든 목적항이 “첫걸음만”이어야 한다는 일반 정리가 아니다. — `docs/arch/terms.md` §W7교훈(124–131행); `v1.7/VERSION.md` §7–8.

### Inferences: 다음 실험 우선순위와 피치 문장

- [해석] **피치 문장:** “우리는 21,568판 top 기록과 224판 새 본선 지도 기보, 35개 합성 스트레스 지도, 7개 구조 복원 지도를 가져옵니다. 관측가능성과 실제 행동을 분리하고, 작은 조각 정찰·프로세스별 기억·확정 구조 공유를 여왕 생존에 연결하는 기제를 제안합니다.” 위 N은 표의 원출처와 시각을 붙인다.
- [해석] **1순위:** 여왕이 모르는 포털/무순환 가지로 들어가기 전 필요한 정보를 작은 조각이 얻고 여왕이 수신하는 한 장면부터 설계. 새 정보→수신→첫 action 변화→여왕 위험 감소를 기록한다. 실제 신규 정찰 검증 N=0를 해소한다.
- [해석] **2순위:** 미지 간선을 벽으로 취급하는 FP를 줄이는 인증 구조 모델. closed-edge/portal provenance/대칭확정 조건을 직접 검증하고 여왕 성장여유·출구봉함과 연결한다.
- [해석] **3순위:** s의1.2.3 발동 장면을 별도 구성해 정확한 실패새끼만 막는지 확인. 현재132판0발동은 이 질문을 답하지 못한다. k/전면굴금지를 과거 판정만 보고 되살리지 않는다.
- [해석] **4순위:** runtime engine shadow gate로 입력·판정만 기록. 요새 후보면 queen 생존/급식 경로/backup 유지 조건을 실제판면으로 비교한 뒤 배포한다. gate의 N=0를 사실화하지 않는다.
- [해석] **5순위:** Maze/포털/원격샘 특성은 운영진 힌트로 시험장에 반영하되 복원gap 추정을 정답으로 채점하지 않는다. 정찰 방향의 행동근거는 구규칙 unseen 본선 원자료에서 얻고 새규칙 상대 도달은 새 도구로 계산한다.

### Gaps / 읽은 범위·출처 충돌

- [사실] 전부 읽음: `research/observations/observability.md`, `mapgen.md`, `research/KNOWLEDGE.md`, `docs/arch/unknown-maps.md`, `maps/sprint/README.md`, `AGENTS.md`, `tools/mapgen/README.md`, `tools/codex-continue.sh`, `eval/README.md`, `research/observations/sprint-commentary.md`. `DECISIONS.md`/`WORKQUEUE.md`는 배정 주제 및 현재Q·W1/W2/W3/W8/W9/W12/W15/W16/수집변경·규칙변경·정정 항목을 읽었다.
- [사실] 긴 반복문서 압축 읽음: `map-atlas.md` §0–4/§6–8과 지도별 모든 서술 요약/기하/해석/권장/모집단을 읽고 반복 numeric 상세표는 대표치/검증 요약 중심으로 확인했다. `opening-book.md` §0–2/모든 절 서술·선택정독/구현한계와 핵심 수치, 반복 지도별 표는 요약 중심. `maps/generated/MANIFEST.md` 머리·한계·가족별 모든 항목을 훑고 반복 너비/gap 분포는 제안기제에 필요한 값만 노트로 옮겼다. 파일별 숫자 새 재집계 없음.
- [사실] 인접 구현/자료는 설명·정의 확인용으로 읽음: `versions/v1.6.1/VERSION.md` 결과§5–7, `versions/v1.7/VERSION.md` W15§17–18/첫걸음 관련 항목, `versions/v1.8/VERSION.md` 결과§3–4, `general-principles.md` 요새gate/최종표, `docs/arch/README.md`, `terms.md` 관련줄, reach/boxing/forced/drift/board/replay2map/mass_ledger/top_features/fingerprint 도구 머리말·해당 코드, proxies style 머리말. `mapgen/SUMMARY.txt`, `sprint-maps/SUMMARY.txt`로 문서 inventory를 대조했다.
- [사실] 이 배정에서는 문서화된 현재 elite 전체 N을 찾지 못했고 새로 세지 않았다. 91%는 재집계 요청 중이다. 새 여왕 초기 연구/역학 연구는 별도 동시 작업이므로 본 IDEA BOOK에서 완료로 주장하지 않는다. — `DECISIONS.md`21:35/23:22.
- [해석] 모든 구규칙숫자는 queen 목적에서 “행동근거/기제기록”으로 옮길 수 있지만 새규칙 효과로 옮길 수 없다. 신뢰할 수 있는 원연구가 기존 요약보다 좁게 주장하면 원연구를 따른다.
