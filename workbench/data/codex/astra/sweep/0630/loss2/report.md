[M] 최다 직접 원인: 시야 안 길이3 공격자에게 짧은 여왕이 피격(2/3); 두 판의 예방책은 같지 않다.
[C/E] 카드: NEW ‘섭취·몸 이동을 반영한 여왕 탈출’(Stripes 1판), LIVE-BUT-FAILED ‘아군의 두 걸음 출구 보존’(Maze 1판).
[M/C/E] 사건·합법 경로는 높은 확신, 내부 분기·장기 구제는 미검증. one11/21269, 세 기보 botId 직접 확인.

[C] 코드 줄은 모두 `data/online/smoke/one11-bot/main.cpp`.

[M] 0기반 라운드·좌표. A=우리. 최종 값은 **여왕/최장/총길이/생존수**이며 기보 결과 필드와 대조했다. ‘전환’은 관측된 이후 경과이지 반격 불가능의 증명이 아니다.

| 경기 / 판정 | 최종 A : B [M] | 전환·단일 핵심 원인 [M, 인과 해석 E] | LIVE 조건의 미포괄 [C] |
|---|---|---|---|
|1496848 Maze / 여왕|0/64/125/19 : 63/63/180/32|여왕 길이 열세는 r15부터 끝까지. 결정 사건 r111–114: #0이 (12,13)에 들어간 뒤 #8이 (11,14)를 점유하고 r112·113 연속 섭취해 몸을 유지. #0 r112 분열→길이2, r113 (11,13) 진입, r114 서쪽 벽 사망. 공격자 없음.|`QUEEN_EXIT_KEEP:true`, `QUEEN_EXIT_STRICT:true`: 956–967·1021의 `exits(proposed)>0`가 첫 출구 (11,13) 하나로 통과시킴. r113의 #8은 길이4라 STRICT 889–891에서도 제외. `QS_KEEP_LEN:3`의 일반 분열 제한(2030–2034)은 `queen_wait`(5805–5830), 대기 분열(1582–1586)을 덮지 않음.|
|1496849 Stripes / 전멸 r224|0/0/0/0 : 0/4/79/34|상대 #0은 r13 자기몸 사망. 우리 #1의 여왕 우위가 r75 끝남: (14,11)→(13,11), 보이던 #38(L3)이 (13,9)→(13,10)→(13,11), 한 칸 비용을 내고 충돌. 섭취 동반 탈출을 놓친 것이 직접 원인 후보[E]. 총길이 열세는 r48부터, 최장 열세는 r194부터 끝까지. 마지막 #181은 r224 #163에게 피격.|`QUEEN_SAFETY:true`, `REACH_EATS:true`: 적 섭취는 6049–6060·6116–6130에서 반영하지만 자기 탈출 `limit=min(sprint_reach(),STRIDE_MAX)`(6201–6202)는 L3에서 2. 6231–6232는 이후 걸음의 현재 몸 점유도 차단. 관측된 NES 대안은 3걸음이므로 탐색 밖.|
|1496850 Tower Defense / 여왕|0/16/19/2 : 21/56/90/6|여왕 열세 r29부터, 총길이 열세 r43부터 끝까지. #0은 r34–258 네 칸 (3–4,9–10)을 225차례 무섭취 순환; 마지막 섭취 r7. r302 두 걸음 비용으로 L3→2. r351 (9,14)→(9,15), 보이던 #234(L3)가 (8,15)에서 동쪽 한 걸음 충돌. 성장 없는 순환으로 탈출 자원을 잃음[E].|`QUEEN_SAFETY:true`: r351 북쪽 벽·동쪽 자기몸, 서/남은 #234 도달권. 7915–7930의 `open[0]`가 없고 L2는 분열·유료 탈출 불가(5756–5760·6201–6202). 장기 무섭취 해소는 이 안전고리가 덮지 않음. `QUEEN_BOOT_LEN:6`은 먹이기 단계 분열 억제(5833–5834)이며 먹이를 찾아주지 않음.|

| 성장 격차 / 이후 행동 [M] | 근거 |
|---|---|
|Stripes|r100 누적 섭취 52:124, 자연 진주 포함 전체 섭취. r21–50 우리 139차례 중 무섭취 이동118·분열5, 섭취13(상대34). r201–224 섭취0:64, 우리 #98·151·156·149·181 순서로 피격해 전멸.|
|Tower Defense|r100 섭취11:94, r300 28:432. #6도 r50–300 251차례에 5개만 섭취. 여왕 225차례 순환은 위 표. `TERRITORY_DECAY:16`은 CARDS의 BEING BUILT이나 이 순환을 고친다는 증거는 없음.|

| 우리 여왕 사후 상대 여왕 접근 [M] | 결과 |
|---|---|
|Maze|있음. 지형 최단거리≤5인 우리 차례 시작37회; 첫 r370 #545 (37,9)→상대여왕 (39,6), 거리5. 모든 상태변경도 검사: 최소2, r451 #281 (38,17), 상대 (39,18). 거리만으로 즉시 충돌 가능을 뜻하지 않음.|
|Stripes|해당 없음: 상대 여왕은 우리보다 먼저 r13 사망.|
|Tower Defense|없음. 모든 상태변경에서 최소35: r425 #238 (15,15), 상대여왕 (28,11). 상대여왕 마지막 차례 (26,12). 거리 계산은 켈프·포털 반영, 몸 장애물 제외이므로 ‘5걸음 불가’의 하한임.|

[M/C/E] 원인 순위와 카드. 첫 묶음은 피격 기제의 공통점이며 하나의 변경으로 2판을 구제한다는 주장이 아니다. CARDS의 BEING BUILT `QUEEN_FAR_HEADS`·`QUEEN_EDGE_REACH`는 여기서 공격자가 이미 보였다는 결손을 해결하지 않는다.

| 순위 / 설명 수 | 카드·규칙·코드 위치 [C/E] | 기존 스위치 / 확인·반증 수치 [M/E] |
|---|---|---|
|1. 보이는 적 앞 짧은 여왕의 탈출 실패, 2/3|**NEW**, Stripes만: 여왕의 안전한 한 걸음이 없으면 현재 진주와 매 걸음 몸 이동·비용을 반영해 탈출 탐색. 5756–5760·6195–6260. Tower Defense r351은 이 카드로 구제 불가.|그대로 구현하는 상수 없음. `REACH_EATS:true`는 적만 처리. r75 NES=(14,10)→진주(15,10)→자기몸이 비운(15,11), 길이3→3→2: 합법 경로1개 확인. 보이는 적3마리·현재 시야 진주·다른 몸 고정·8걸음 한도 검사에서 종점 도달 적0. 성공: 이 누락 후보1개가 탐색에 들어오고 선택 후10라운드 생존. 불법 비용·몸 충돌 또는 조기 사망이면 반증.|
|2. 아군이 여왕의 다음다음 칸을 차단, 1/3|**LIVE-BUT-FAILED**: 아군 이동 뒤 여왕의 유일한 첫 출구에서 다음 이동도 막히면, 그 연속 출구를 남기는 합법 대안을 선택. 956–967·1021–1035의 출구 평가 확장.|`QUEEN_EXIT_KEEP:true`, `QUEEN_EXIT_STRICT:true`는 한 걸음만 보호. Maze r111 #8의 E는 여왕 후속 출구0; 합법 N/W는 각각1(고정 판면). 성공: 봉쇄 선택1→0 및 여왕 r124 생존. 다른 용 이동 때문에 대안도 막히거나 불필요 희생이면 반증. 여왕 자신의 이동만 검사하는 구축 중 CORRIDOR는 이 아군 차례를 직접 덮지 않음.|

[M] 마지막 세 자기 차례 **시작**의 7×7 판면. 중앙 Q=우리 여왕, K=상대 여왕, A/B=각 팀 머리, a/b=몸, *=진주, .=빈칸. 각 칸에 붙은 대문자 N/E/S/W는 벽, 소문자는 포털. 위치는 원판의 토러스 좌표이며 칸을 가르는 공백은 통로 표시가 아니다.

| 경기·차례 / 중심·행동 [M] | 7×7 [M] |
|---|---|
|1496848 Maze r112 / [12, 13] / 분열 #97|<code>A aE .EW .NW .NE .NW .S</code><br><code>. aE .SW .S aE .SW .NS</code><br><code>. . .NS aN aES .NW .N</code><br><code>. .E .NW QES .NW .ES .SW</code><br><code>. a A .NE .W .NE .NW</code><br><code>. aE *EW .SW .S .ES .EW</code><br><code>. .E *SW *NES .NW .NS .ES</code>|
|1496848 Maze r113 / [12, 13] / W|<code>a aE .EW .NW .NE .NW .S</code><br><code>. .E .SW AS aE .SW .NS</code><br><code>. . .NS aN .ES .NW .N</code><br><code>. .E .NW QES .NW .ES .SW</code><br><code>. a a .NE .W .NE .NW</code><br><code>. aE AEW .SW .S .ES .EW</code><br><code>. .E *SW *NES .NW .NS .ES</code>|
|1496848 Maze r114 / [11, 13] / W|<code>. a .E .EW .NW .NE .NW</code><br><code>. . .E ASW aS .E .SW</code><br><code>. . . .NS .N .ES .NW</code><br><code>a . .E QNW aES .NW .ES</code><br><code>. . a a .NE .W .NE</code><br><code>. . aE aEW .SW .S .ES</code><br><code>. . .E ASW *NES .NW .NS</code>|
|1496849 Stripes r73 / [16, 11] / W|<code>.S .S bS .eS .Sw BS bS</code><br><code>.N .N aNE .NeW *NESw .NW .N</code><br><code>aW A AE *SW *NES .W .Es</code><br><code>.W .S .S QNS aNS aS .nES</code><br><code>.sW AN .N .N .N .N .N</code><br><code>.nW a . . . . .</code><br><code>aS .S aS AS .S .S .S</code>|
|1496849 Stripes r74 / [15, 11] / W|<code>.S .S .S .S BeS BSw bS</code><br><code>BNS .N AN .NE *NeW *NESw .NW</code><br><code>*NE .W a *E *SW *NES .W</code><br><code>.ES .W .S QS aNS aNS .S</code><br><code>.NEs AsW aN .N .N .N .N</code><br><code>*nES .nW . . A . .</code><br><code>aNS .S .S .S aS .S .S</code>|
|1496849 Stripes r75 / [14, 11] / W|<code>.S .S .S .S BS beS bSw</code><br><code>bNS bNS BN aN ANE *NeW *NESw</code><br><code>bNsW BNE .W . *E *SW *NES</code><br><code>.nSW .ES .W QS aS aNS .NS</code><br><code>.NW .NEs asW aN .N .N .N</code><br><code>*SW AnES .nW . A a .</code><br><code>aNS aNS .S .S .S .S .S</code>|
|1496850 Tower Defense r349 / [10, 15] / N|<code>.NEW .SW .NE .EW bW bE .SW</code><br><code>.SW .NS .S .ES bW b *N</code><br><code>BN .N .N .N b .E .SW</code><br><code>.S .S aS QS b b bN</code><br><code>.NE .NW .NE .NEW bW b .S</code><br><code>.SW .ES .W .ES .W .E *NW</code><br><code>.N .NE .SW .NE .W .E .SW</code>|
|1496850 Tower Defense r350 / [10, 14] / W|<code>.NS .NE *NSW *NE bW bE .NW</code><br><code>.NEW .SW .NE .EW bW bE .SW</code><br><code>.SW .NS .S .ES bW b *N</code><br><code>bN .N .N QN b .E .SW</code><br><code>BS .S .S aS b b bN</code><br><code>.NE .NW .NE .NEW bW b .S</code><br><code>.SW .ES .W .ES .W .E *NW</code>|
|1496850 Tower Defense r351 / [9, 14] / S|<code>.N .NS .NE *NSW *NE bW bE</code><br><code>.EW .NEW .SW .NE .EW bW bE</code><br><code>.ES .SW .NS .S .ES bW b</code><br><code>.N bN .N QN aN b .E</code><br><code>.S bS BS .S .S b b</code><br><code>.N .NE .NW .NE .NEW bW b</code><br><code>.ES .SW .ES .W .ES .W .E</code>|

[M] 재현: `python3 -B analyze.py`, 이어서 `python3 -B check_paths.py`(저장소 루트에서 이 폴더 경로를 붙여 실행). 공유 리플레이 리더·지형 해석기를 import했다. 원자료는 `*-base.json`, `*-detail.json`, 대안 검증은 `path-checks.json`.

[E] 새 정책 실행·내부 점수/분기 추적·후속 턴 반사실·CPU는 검사하지 않았다. 고정 판면의 대안이 실제 승리로 이어진다는 주장은 없다. 네트워크·대전·원본 코드 변경 없음.

[M] 작성 시각: 2026-10-09T06:39:44+09:00.
