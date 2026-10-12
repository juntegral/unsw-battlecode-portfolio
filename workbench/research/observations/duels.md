# 온라인 국소 결투: 상위권의 행동과 우리 실패

작성 2026-10-02 00:11:56 KST. W10. 네트워크·대전·업로드·커밋 없이 기존 온라인 기보 전수를 읽었다.

[사실] 원문 규칙은 [ALL.md](../../rules/ALL.md)·[death.md](../../rules/death.md), 항의 크기는 [terms.md](../../docs/arch/terms.md), kill path/TRADE는 [bot/plan.cpp](../../bot/plan.cpp)를 확인했다.

[사실] 이 보고서는 온라인에서 관측한 행동의 기술 통계다. 로컬 흉내 상대의 승패를 채택 근거로 사용하지 않았다. 실제 변경은 구현하지 않았고 마지막 규칙의 적용 N은 모두 0이다.

## 먼저 읽을 관측

[사실] 상위 10팀 승자 정면접촉의 능동 이동은 309,628/534,426=57.9%, 우리 전체는 2,368/13,483=17.6%다. 그러나 우리 본선 7판은 93/108=86.1%로 방향이 뒤집힌다. 본선 사망594 중 켈프252·자기 몸79·아군 몸136이므로 이 집단을 따로 읽어야 한다.

[해석] 자료가 지지하는 다음 가설은 일괄 공격성 증가보다 다음 차례 도달 위험, 살아남는 몸 장벽, 분열 뒤 부모·새끼의 출구 보존이다. 감기·미끼는 아래 조작적 대리 지표이며 의도는 미확인이다. 마지막 규칙표의 수치는 구현할 시험 강도이고 예상 승률이 아니다.

## 1. 모집단과 세 단계 방법

[사실] 첫 목록 시각 2026-10-01 18:04:09 KST, 최종 목록 고정 2026-10-01 21:24:25 KST, 마지막 집계 2026-10-01 23:28:52 KST. 게임 id 중복 제거 후 목록 24,942판, 분석 24,942판, 엄격 상위 10팀끼리 목록 5,844판. 목록에서 기보가 없는 항목 44개는 제외하고 population.json에 남겼다. 에피소드 11,662,901개다. strict 조기 표는 2026-10-01 18:47:12 KST에 5,600판을 저장했다. 추출이 끝난 뒤 최종 목록을 한 번 더 고정해 그때까지 도착한 기보를 반영했다.

[사실] 우리 W0–W12 및 v1-w1..3는 1477판. UnderTheC는 203판. 맞춤 지도 목록 N=511이다. 맞춤 지도 여부는 기존 열 지도 이름 이외라는 조작적 구분으로, 본선이라는 서버 표식의 확인과는 구분한다.

[사실] stalled 추정으로 상위권 집계에서 제외한 게임 N=305. 기존 연구와 같은 ‘100라운드 이상, 한 팀의 sonar=0 및 분열≤3’ 규칙이다. 조용한 요새를 제외할 수 있는 휴리스틱이며, 원기보·에피소드는 삭제하지 않았다. 우리와 UnderTheC의 기준선에서는 이 제외를 적용하지 않았다.

[사실] ① 전체 기보를 스크립트로 재구성하고 표를 먼저 저장했다. ② 에피소드 결과·머릿수·판면 조건의 분류와 크기를 확정했다. ③ 유형마다 그 특징의 평균에 가까운 서로 다른 게임 최대 세 개를 선택해 직전 세 결정을 읽고 eval/board.js로 그렸다. 상위권 깊은읽기는 strict 대전의 각 유형 안에서 고르며, 우리 사례는 전체 우리 온라인 집단에서 고른다. 극적인 사례를 임의로 고르지 않았다. classes.json과 selection.json에 N·선택 점수가 있다.

[사실] 우리 시리즈별 경기 수: {'cand-merge2-online': 70, 'cand-merge2-online-r2': 70, 'cand-merge2-online-r3': 70, 'cand-stack1-online': 70, 'cand-stack2-online': 70, 'cand-stack3-online': 70, 'cand-stack4-online': 70, 'cand-stack5-online': 70, 'cand-stack6-online': 70, 'cand-stack6-online-r2': 70, 'cand-stack7-online': 70, 'cand-stack8-online': 70, 'cand-stack9-online': 70, 'cand-stack10-online': 70, 'cand-stack11-online': 70, 'bench-s11-1': 70, 'bench-s11-2': 70, 'bench-s11-3': 70, 'v1-w1': 70, 'v1-w2': 70, 'v1-w3': 70, 'sprint-bracket': 7}. 여러 제출 버전의 기록이므로 모든 실패를 현재 v1.7의 효과라고 해석하지 않는다.

[사실] 조기 strict 표의 노출-교환 플래그와 제삼 몸 접촉의 isolated 제외 조건을 최종 재집계에서 고쳤다. 에피소드 진입·끝·결과 id는 바꾸지 않았고 전수 독립 재구성으로 확인했다. 조기 파일은 tables-strict-first.json.gz에 보존하고 tables-strict.json은 최종 정의로 갱신했다.

[사실] strict는 수집 당시 rank A/B가 모두 1–10인 게임이다. elite는 해당 편의 수집 rank가 1–10인 게임이며, population은 요청한 data/top과 data/elite 전체 수집 기보의 편이며, 원 요청의 전체 상위권 자료에 해당한다. 실제 랭크 1–10 편만 보는 elite는 더 좁은 추가 집단이다. winner/loser는 결투 결과가 아니라 최종 경기 승패다. 반복 팀·시리즈·동일 게임의 두 편은 독립 표본이 아니므로 p값이나 인과 효과를 주장하지 않는다.

## 2. 정의와 관측 한계

[사실] 진입은 적대 두 머리의 지형 BFS 거리가 4 이하가 되는 라운드 시작 또는 action 종료/사망 직전 판면이다. 켈프·포털·경계 래핑을 반영하며 몸은 거리 계산에서 제외한다. 포털에서 방향성이 생길 수 있어 양방향 거리의 작은 값을 쓴다. 각 편의 id는 평생 고정이고 새끼는 더 높은 id를 받는다.

[사실] 제삼의 머리가 둘 중 하나와 BFS 5 이내면 third_party로 끝낸다. 진입 때부터 제삼자가 있는 경우도 즉시 종료하며, 같은 쌍은 라운드 시작에서 거리 4를 벗어나기 전 재진입하지 않는다. 거리 6 초과가 3라운드 지속하면 disengage, 경기 종료는 censored다. 원 정의의 사망 중 직접 죽임·맞교환에 해당하지 않는 경우는 other_death로 남겨 수치가 빠지지 않게 했다.

[사실] isolated는 검사한 모든 시작·action·분열 판면에서 제삼의 머리가 없고 제삼 몸 접촉도 없었던 사건이다. 질주 중간 통과만으로 스쳐 간 제삼자는 놓칠 수 있어 ‘전 시간 고립’보다 약한 관측 경계 정의다. local1v1은 진입 때 두 머리의 BFS8 이웃 합집합에서 팀 머릿수가 같다는 뜻이다. 지형 거리와 d8·공간은 전체 기보 연구 특징이다. 봇의 7×7 단일 창에서 그대로 알 수 있다고 가정하지 않는다.

[사실] kill은 파트너 몸으로 Hit Other Body, 또는 파트너와 거리 2 이내에서 Hit Wall/Self를 당하고 파트너가 그 fatal action을 살아남는 경우다. 벽/자기 사망은 파트너가 원인이라는 증명이 없으므로 reason별로 구분한다. trade는 파트너와 Head to Head 한 번이고 사망 둘을 한 사건으로 센다.

[사실] 여유 공간은 머리에서 지형 BFS5 이내의 빈칸 flood-fill이다. 현재의 모든 몸·자기 꼬리는 막힘으로 취급한다. 적 몸을 제거한 공간과 비교한 감기 후보는 정적 공간 감소이며, 꼬리 이동을 반영한 미래 탈출 증명이 아니다. 벽은 켈프이고 맵 바깥은 래핑한다. 길이 L의 진주 없는 브리프의 1무료걸음 가정에서 진주 없는 총 걸음 여력은 L−1, 추가 여력은 L−2다. 현행 규칙은 첫 ceil(L/4)걸음이 무료이며, 이때 총 여력은 L+ceil(L/4)−2, 추가 여력은 L+ceil(L/4)−3이다. 원기보와 맞는 재구성 모델을 적용했다. 0/1/2+ 여력 구간과 길이에 따른 대소관계는 두 공식에서 같다.

[사실] 현재 rules/ALL.md의 무료 질주 규칙이 브리프 및 기존 mass_ledger.js의 1무료걸음 가정과 달랐다. 압축 캐시 검사값을 전수 감사한 N=24,942판 중 411판을 ceil(L/4) 모델로 재구성해 이동·분열·진주·최종 상태 검사와 독립 episode id 대조를 모두 통과시켰다. 영향을 받은 우리 기보 N=0, 본선 맞춤 지도 N=0, UnderTheC 아는 지도 N=53이다. 이 수정은 연구 디코더의 오류 수정이며 우리 봇의 성능 향상 수치가 아니다.

[사실] 기존 도구 파일은 수정하지 않았다. exp/duel/ledger.js에 로컬 사본을 두고, 보정 경기의 eval/board.js 그림에만 ledger-preload.js를 적용했다. 다른 경기의 1무료걸음 모델이 기보와 맞는다는 사실만으로 실제 규칙이 1무료였다고 단정하지 않는다. 긴 조각의 복수 이동이 없으면 두 모델이 같은 기보를 만든다.

## 3. 빈도: 전수 표

각 N은 해당 집단의 편-에피소드 수다. 같은 엄격 게임의 두 편에 맞교환이 각각 한 번 나타나므로 winner/loser 열을 합해 사건 수로 읽지 않는다. 죽임/피살은 episode의 결과이고 최종 승패와 다르다.

|집단|N 경기|N 에피소드|평균/경기|죽임|피살|교환|이탈|제삼자|그밖 사망|검열|
|---|---|---|---|---|---|---|---|---|---|---|
|strict/winner|5722|2933548|512.68|171|167|5096|5082|2921632|943|457|
|strict/loser|5722|2933548|512.68|167|171|5096|5082|2921632|943|457|
|elite/winner|11847|5676438|479.15|542|366|10764|10456|5651542|1866|902|
|elite/loser|9321|4733145|507.79|358|287|8570|8495|4712989|1614|832|
|population/winner|23132|11132699|481.27|1088|900|22070|21847|11080707|4081|2006|
|population/loser|23132|11132699|481.27|900|1088|22070|21847|11080707|4081|2006|
|ours|1477|491479|332.75|27|53|598|1493|488343|800|165|
|ours/custom|7|5938|848.29|0|0|8|44|5879|1|6|
|under/known|189|75605|400.03|7|1|134|239|75150|57|17|
|under/known_autoscrim|30|14865|495.50|0|0|23|41|14798|1|2|
|under/custom|14|6837|488.36|1|0|17|52|6760|4|3|
|sprint_custom/winner|511|378029|739.78|99|60|1228|2153|374116|234|139|
|sprint_custom/loser|511|378029|739.78|60|99|1228|2153|374116|234|139|

### 진입 제삼자 없음 + 시작 d8 수 같음

|집단|N|죽임|피살|교환|이탈|제삼자|그밖 사망|검열|
|---|---|---|---|---|---|---|---|---|
|strict/winner|23473|81|80|2172|2844|17441|603|252|
|strict/loser|23473|80|81|2172|2844|17441|603|252|
|elite/winner|48593|286|176|4592|5820|36019|1197|503|
|elite/loser|39075|192|134|3719|4757|28814|1012|447|
|population/winner|99730|572|458|9610|12071|73283|2619|1117|
|population/loser|99730|458|572|9610|12071|73283|2619|1117|
|ours|5564|13|35|312|815|3907|393|89|
|ours/custom|99|0|0|3|18|74|1|3|
|under/known|810|5|1|51|148|555|36|14|
|under/known_autoscrim|148|0|0|6|21|118|1|2|
|under/custom|122|1|0|9|28|81|0|3|
|sprint_custom/winner|6634|43|25|509|1156|4715|112|74|
|sprint_custom/loser|6634|25|43|509|1156|4715|112|74|

### 끝까지 제삼자 없는 isolated

|집단|N|죽임|피살|교환|이탈|제삼자|그밖 사망|검열|
|---|---|---|---|---|---|---|---|---|
|strict/winner|11916|171|167|5096|5082|0|943|457|
|strict/loser|11916|167|171|5096|5082|0|943|457|
|elite/winner|24896|542|366|10764|10456|0|1866|902|
|elite/loser|20156|358|287|8570|8495|0|1614|832|
|population/winner|51992|1088|900|22070|21847|0|4081|2006|
|population/loser|51992|900|1088|22070|21847|0|4081|2006|
|ours|3136|27|53|598|1493|0|800|165|
|ours/custom|59|0|0|8|44|0|1|6|
|under/known|455|7|1|134|239|0|57|17|
|under/known_autoscrim|67|0|0|23|41|0|1|2|
|under/custom|77|1|0|17|52|0|4|3|
|sprint_custom/winner|3913|99|60|1228|2153|0|234|139|
|sprint_custom/loser|3913|60|99|1228|2153|0|234|139|

직접 몸 충돌(O)과 근접 벽(W)·자기 몸(S) 사망의 연관을 분리한다.

|집단|죽임 O/W/S (N)|피살 O/W/S (N)|
|---|---|---|
|strict/winner|{'W': 40, 'O': 119, 'S': 12}|{'O': 130, 'W': 27, 'S': 10}|
|strict/loser|{'O': 130, 'W': 27, 'S': 10}|{'W': 40, 'O': 119, 'S': 12}|
|elite/winner|{'W': 154, 'O': 327, 'S': 61}|{'O': 265, 'W': 75, 'S': 26}|
|elite/loser|{'O': 250, 'W': 65, 'S': 43}|{'W': 71, 'O': 192, 'S': 24}|
|population/winner|{'W': 324, 'O': 627, 'S': 137}|{'O': 592, 'W': 204, 'S': 104}|
|population/loser|{'O': 592, 'W': 204, 'S': 104}|{'W': 324, 'O': 627, 'S': 137}|
|ours|{'O': 22, 'W': 4, 'S': 1}|{'W': 18, 'O': 35}|
|ours/custom|{}|{}|
|under/known|{'O': 6, 'W': 1}|{'O': 1}|
|under/known_autoscrim|{}|{}|
|under/custom|{'W': 1}|{}|
|sprint_custom/winner|{'O': 35, 'S': 29, 'W': 35}|{'W': 21, 'O': 25, 'S': 14}|
|sprint_custom/loser|{'W': 21, 'O': 25, 'S': 14}|{'O': 35, 'S': 29, 'W': 35}|

[해석] 승패 집단의 차이는 최종 승리와 함께 나타나는 행동의 차이다. 머릿수·위치·시간·길이가 다르므로 개별 결투 항을 바꿨을 때의 효과로 읽을 수 없다.

[사실] population/winner: 제삼자 종료 11,080,707/11,132,699=99.5%, 고립 완료 51,992/11,132,699=0.5%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] population/loser: 제삼자 종료 11,080,707/11,132,699=99.5%, 고립 완료 51,992/11,132,699=0.5%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] elite/winner: 제삼자 종료 5,651,542/5,676,438=99.6%, 고립 완료 24,896/5,676,438=0.4%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] elite/loser: 제삼자 종료 4,712,989/4,733,145=99.6%, 고립 완료 20,156/4,733,145=0.4%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] ours: 제삼자 종료 488,343/491,479=99.4%, 고립 완료 3,136/491,479=0.6%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] ours/custom: 제삼자 종료 5,879/5,938=99.0%, 고립 완료 59/5,938=1.0%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] under/known: 제삼자 종료 75,150/75,605=99.4%, 고립 완료 455/75,605=0.6%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] under/known_autoscrim: 제삼자 종료 14,798/14,865=99.5%, 고립 완료 67/14,865=0.5%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] under/custom: 제삼자 종료 6,760/6,837=98.9%, 고립 완료 77/6,837=1.1%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] sprint_custom/winner: 제삼자 종료 374,116/378,029=99.0%, 고립 완료 3,913/378,029=1.0%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.
[사실] sprint_custom/loser: 제삼자 종료 374,116/378,029=99.0%, 고립 완료 3,913/378,029=1.0%. 따라서 고립 결투의 규칙만으로 군집 싸움 전체를 설명하지 않는다.

### 지도별·단계별

N 에피소드; 단계는 진입 라운드다. 게임이 끝나 해당 단계에 도달하지 않은 판은 N 경기에서 제외한다. 지도×단계의 교차표와 추가 조건표는 tables.json에 있다.

|집단|map|N 경기|N|죽임|피살|교환|이탈|제삼자|
|---|---|---|---|---|---|---|---|---|
|population/winner|Around UNSW|68|79797|12|3|278|878|78520|
|population/winner|Australia|63|97557|5|4|232|582|96680|
|population/winner|Autarky|2285|1871012|10|12|750|637|1869330|
|population/winner|Default|2445|1466351|111|140|2884|3041|1459933|
|population/winner|Devil|2077|563274|9|3|243|48|562951|
|population/winner|Islands|67|136864|9|7|120|247|136444|
|population/winner|Maze|68|18140|49|30|372|137|17445|
|population/winner|Portals|2541|0|0|0|0|0|0|
|population/winner|Prisoners Dilemma|2108|335159|13|17|105|311|334603|
|population/winner|Queen Of Spades|2132|551278|34|35|1379|2764|546904|
|population/winner|Schooltime|2481|3115991|284|204|5850|8472|3099929|
|population/winner|Slithery Fight|2307|1551696|210|240|6515|2550|1539398|
|population/winner|Stripes|62|6775|2|0|20|24|6719|
|population/winner|Tower Defense|61|4487|4|6|35|41|4394|
|population/winner|Trauma|2272|362926|321|190|2670|1818|357058|
|population/winner|Trophy|2030|964432|4|1|513|224|963661|
|population/winner|weakhold|65|6960|11|8|104|73|6738|
|population/loser|Around UNSW|68|79797|3|12|278|878|78520|
|population/loser|Australia|63|97557|4|5|232|582|96680|
|population/loser|Autarky|2285|1871012|12|10|750|637|1869330|
|population/loser|Default|2445|1466351|140|111|2884|3041|1459933|
|population/loser|Devil|2077|563274|3|9|243|48|562951|
|population/loser|Islands|67|136864|7|9|120|247|136444|
|population/loser|Maze|68|18140|30|49|372|137|17445|
|population/loser|Portals|2541|0|0|0|0|0|0|
|population/loser|Prisoners Dilemma|2108|335159|17|13|105|311|334603|
|population/loser|Queen Of Spades|2132|551278|35|34|1379|2764|546904|
|population/loser|Schooltime|2481|3115991|204|284|5850|8472|3099929|
|population/loser|Slithery Fight|2307|1551696|240|210|6515|2550|1539398|
|population/loser|Stripes|62|6775|0|2|20|24|6719|
|population/loser|Tower Defense|61|4487|6|4|35|41|4394|
|population/loser|Trauma|2272|362926|190|321|2670|1818|357058|
|population/loser|Trophy|2030|964432|1|4|513|224|963661|
|population/loser|weakhold|65|6960|8|11|104|73|6738|
|elite/winner|Australia|2|2368|0|0|8|26|2332|
|elite/winner|Autarky|1267|1031219|5|9|451|370|1030269|
|elite/winner|Default|1312|750749|47|51|1511|1478|747559|
|elite/winner|Devil|1075|256314|4|0|118|19|256169|
|elite/winner|Islands|2|4976|1|1|3|6|4965|
|elite/winner|Maze|1|123|0|0|7|3|113|
|elite/winner|Portals|1307|0|0|0|0|0|0|
|elite/winner|Prisoners Dilemma|1057|159268|5|13|62|158|158960|
|elite/winner|Queen Of Spades|1093|279601|17|15|684|1407|277408|
|elite/winner|Schooltime|1336|1723716|175|92|3222|4561|1715010|
|elite/winner|Slithery Fight|1159|797210|91|96|2948|1339|791474|
|elite/winner|Stripes|1|492|0|0|0|1|490|
|elite/winner|Tower Defense|1|34|0|0|0|0|34|
|elite/winner|Trauma|1177|201540|194|88|1517|974|198290|
|elite/winner|Trophy|1057|468828|3|1|233|114|468469|
|elite/loser|Around UNSW|4|4837|0|2|11|54|4760|
|elite/loser|Australia|2|3094|0|0|7|26|3059|
|elite/loser|Autarky|917|830457|6|2|356|315|829673|
|elite/loser|Default|987|595009|57|32|1169|1218|592426|
|elite/loser|Devil|869|228327|2|2|101|25|228184|
|elite/loser|Islands|2|3527|0|1|3|9|3514|
|elite/loser|Maze|3|610|0|4|16|10|569|
|elite/loser|Portals|1035|0|0|0|0|0|0|
|elite/loser|Prisoners Dilemma|927|146401|6|5|36|138|146201|
|elite/loser|Queen Of Spades|805|225674|22|7|546|1093|223946|
|elite/loser|Schooltime|1039|1453965|84|104|2540|3741|1446893|
|elite/loser|Slithery Fight|1051|718131|107|39|2540|1141|713143|
|elite/loser|Stripes|3|445|0|0|4|1|440|
|elite/loser|Tower Defense|3|142|1|0|1|2|138|
|elite/loser|Trauma|863|145375|71|87|1044|636|143187|
|elite/loser|Trophy|807|376828|1|2|194|84|376538|
|elite/loser|weakhold|4|323|1|0|2|2|318|
|ours|Around UNSW|1|1367|0|0|2|15|1349|
|ours|Australia|1|940|0|0|0|7|930|
|ours|Autarky|147|49287|0|0|2|12|48814|
|ours|Default|147|56069|5|1|34|155|55853|
|ours|Devil|147|34130|0|0|10|2|34117|
|ours|Islands|1|2269|0|0|1|14|2252|
|ours|Maze|1|644|0|0|0|1|643|
|ours|Portals|147|0|0|0|0|0|0|
|ours|Prisoners Dilemma|147|76122|0|0|19|63|75843|
|ours|Queen Of Spades|147|29394|1|0|8|184|29194|
|ours|Schooltime|147|88692|9|10|99|433|88066|
|ours|Slithery Fight|147|102089|3|13|229|336|101396|
|ours|Stripes|1|486|0|0|0|2|483|
|ours|Tower Defense|1|218|0|0|5|3|210|
|ours|Trauma|147|19873|9|29|184|240|19327|
|ours|Trophy|147|29885|0|0|5|24|29854|
|ours|weakhold|1|14|0|0|0|2|12|
|ours/custom|Around UNSW|1|1367|0|0|2|15|1349|
|ours/custom|Australia|1|940|0|0|0|7|930|
|ours/custom|Islands|1|2269|0|0|1|14|2252|
|ours/custom|Maze|1|644|0|0|0|1|643|
|ours/custom|Stripes|1|486|0|0|0|2|483|
|ours/custom|Tower Defense|1|218|0|0|5|3|210|
|ours/custom|weakhold|1|14|0|0|0|2|12|
|under/known|Autarky|18|6606|0|0|7|15|6579|
|under/known|Default|22|11424|2|1|31|61|11320|
|under/known|Devil|19|6267|0|0|2|2|6263|
|under/known|Portals|22|0|0|0|0|0|0|
|under/known|Prisoners Dilemma|22|3399|2|0|1|6|3375|
|under/known|Queen Of Spades|18|3575|0|0|4|33|3537|
|under/known|Schooltime|22|23099|1|0|52|86|22943|
|under/known|Slithery Fight|11|6827|0|0|20|12|6776|
|under/known|Trauma|13|1396|2|0|10|19|1359|
|under/known|Trophy|22|13012|0|0|7|5|12998|
|under/known_autoscrim|Autarky|2|662|0|0|1|2|659|
|under/known_autoscrim|Default|4|2292|0|0|4|2|2285|
|under/known_autoscrim|Devil|2|236|0|0|0|0|236|
|under/known_autoscrim|Portals|3|0|0|0|0|0|0|
|under/known_autoscrim|Prisoners Dilemma|5|491|0|0|0|1|490|
|under/known_autoscrim|Queen Of Spades|4|1047|0|0|2|4|1041|
|under/known_autoscrim|Schooltime|5|6692|0|0|13|30|6647|
|under/known_autoscrim|Slithery Fight|1|512|0|0|2|1|509|
|under/known_autoscrim|Trophy|4|2933|0|0|1|1|2931|
|under/custom|Around UNSW|2|1229|0|0|2|11|1213|
|under/custom|Australia|2|2110|0|0|3|23|2083|
|under/custom|Islands|2|2999|0|0|3|9|2986|
|under/custom|Maze|2|131|0|0|7|5|119|
|under/custom|Stripes|2|214|0|0|1|0|212|
|under/custom|Tower Defense|2|98|1|0|0|1|95|
|under/custom|weakhold|2|56|0|0|1|3|52|
|sprint_custom/winner|Around UNSW|73|85512|15|3|290|934|84155|
|sprint_custom/winner|Australia|73|104526|5|4|243|627|103589|
|sprint_custom/winner|Islands|73|148260|9|8|128|279|147793|
|sprint_custom/winner|Maze|73|19614|52|30|393|152|18877|
|sprint_custom/winner|Stripes|73|7803|2|0|23|34|7732|
|sprint_custom/winner|Tower Defense|73|5110|5|6|45|45|5001|
|sprint_custom/winner|weakhold|73|7204|11|9|106|82|6969|
|sprint_custom/loser|Around UNSW|73|85512|3|15|290|934|84155|
|sprint_custom/loser|Australia|73|104526|4|5|243|627|103589|
|sprint_custom/loser|Islands|73|148260|8|9|128|279|147793|
|sprint_custom/loser|Maze|73|19614|30|52|393|152|18877|
|sprint_custom/loser|Stripes|73|7803|0|2|23|34|7732|
|sprint_custom/loser|Tower Defense|73|5110|6|5|45|45|5001|
|sprint_custom/loser|weakhold|73|7204|9|11|106|82|6969|

|집단|phase|N 경기|N|죽임|피살|교환|이탈|제삼자|
|---|---|---|---|---|---|---|---|---|
|population/winner|0-49|23132|699409|48|40|1665|3996|692680|
|population/winner|150-349|19215|5845076|462|341|9917|4073|5829229|
|population/winner|350-500|13804|1462525|436|404|5943|9430|1442441|
|population/winner|50-149|22585|3125689|142|115|4545|4348|3116357|
|population/loser|0-49|23132|699409|40|48|1665|3996|692680|
|population/loser|150-349|19215|5845076|341|462|9917|4073|5829229|
|population/loser|350-500|13804|1462525|404|436|5943|9430|1442441|
|population/loser|50-149|22585|3125689|115|142|4545|4348|3116357|
|elite/winner|0-49|11847|362802|30|27|870|2042|359439|
|elite/winner|150-349|9718|2979244|226|130|4619|1703|2972028|
|elite/winner|350-500|6686|711047|215|155|2880|4494|701559|
|elite/winner|50-149|11574|1623345|71|54|2395|2217|1618516|
|elite/loser|0-49|9321|296822|14|14|643|1610|294186|
|elite/loser|150-349|7689|2516728|130|119|3774|1399|2510845|
|elite/loser|350-500|5534|619069|166|123|2260|3847|611117|
|elite/loser|50-149|9116|1300526|48|31|1893|1639|1296841|
|ours|0-49|1477|23453|1|0|23|227|23117|
|ours|150-349|1291|252699|12|28|305|346|251848|
|ours|350-500|947|75091|10|23|191|613|73678|
|ours|50-149|1477|140236|4|2|79|307|139700|
|ours/custom|0-49|7|22|0|0|0|5|16|
|ours/custom|150-349|7|3490|0|0|4|16|3470|
|ours/custom|350-500|7|1826|0|0|4|20|1796|
|ours/custom|50-149|7|600|0|0|0|3|597|
|under/known|0-49|189|5040|0|0|8|42|4978|
|under/known|150-349|161|42699|1|0|47|43|42597|
|under/known|350-500|108|7127|5|1|53|117|6901|
|under/known|50-149|183|20739|1|0|26|37|20674|
|under/known_autoscrim|0-49|30|958|0|0|1|8|949|
|under/known_autoscrim|150-349|24|8747|0|0|6|5|8735|
|under/known_autoscrim|350-500|16|1411|0|0|11|20|1378|
|under/known_autoscrim|50-149|28|3749|0|0|5|8|3736|
|under/custom|0-49|14|146|0|0|0|3|143|
|under/custom|150-349|14|4343|1|0|13|10|4318|
|under/custom|350-500|11|887|0|0|3|36|843|
|under/custom|50-149|14|1461|0|0|1|3|1456|
|sprint_custom/winner|0-49|511|7114|0|1|32|156|6920|
|sprint_custom/winner|150-349|437|217987|50|26|636|765|216419|
|sprint_custom/winner|350-500|355|72723|34|28|403|946|71056|
|sprint_custom/winner|50-149|503|80205|15|5|157|286|79721|
|sprint_custom/loser|0-49|511|7114|1|0|32|156|6920|
|sprint_custom/loser|150-349|437|217987|26|50|636|765|216419|
|sprint_custom/loser|350-500|355|72723|28|34|403|946|71056|
|sprint_custom/loser|50-149|503|80205|5|15|157|286|79721|

## 4. 어떤 조건에서 끝나는가

[사실] action 종료 직전의 진입에는 fatal action이 포함된다. 그 순간의 길이·공간은 이미 해당 행동의 영향을 받았으므로 원인 변수로 읽을 수 없다. tables.json의 각 조건에 roundStartN/roundStartOutcomes를 따로 남겼고, 아래에 라운드 시작 진입만의 핵심 조건도 분리했다.

[사실] 아래는 진입 제삼자가 없는 에피소드만의 시작 특징이다. N에 third_party·검열도 포함한다. 길이·공간·id는 서로 관련되므로 한 열의 차이를 해당 항의 인과 효과로 읽지 않는다. 길이×id, 공간×id 교차표도 tables.json에 있다.


### 상대와 길이 차

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|equal|114079|242|182|7374|7246|0.2%|
|population/winner|longer|121906|618|228|6947|7464|0.5%|
|population/winner|shorter|114394|228|490|7749|7137|0.2%|
|population/loser|equal|114079|182|242|7374|7246|0.2%|
|population/loser|longer|114394|490|228|7749|7137|0.4%|
|population/loser|shorter|121906|228|618|6947|7464|0.2%|
|elite/winner|equal|56514|130|83|3706|3604|0.2%|
|elite/winner|longer|60044|315|83|3242|3495|0.5%|
|elite/winner|shorter|55314|97|200|3816|3357|0.2%|
|elite/loser|equal|44266|74|58|2996|2797|0.2%|
|elite/loser|longer|46431|213|51|2822|2948|0.5%|
|elite/loser|shorter|47233|71|178|2752|2750|0.2%|
|ours|equal|5261|4|10|90|325|0.1%|
|ours|longer|7565|18|22|342|532|0.2%|
|ours|shorter|8524|5|21|166|636|0.1%|
|ours/custom|equal|67|0|0|3|5|0.0%|
|ours/custom|longer|74|0|0|2|12|0.0%|
|ours/custom|shorter|253|0|0|3|27|0.0%|
|under/known|equal|930|1|0|41|65|0.1%|
|under/known|longer|1001|6|1|53|110|0.6%|
|under/known|shorter|855|0|0|40|64|0.0%|
|under/known_autoscrim|equal|192|0|0|6|12|0.0%|
|under/known_autoscrim|longer|198|0|0|11|22|0.0%|
|under/known_autoscrim|shorter|131|0|0|6|7|0.0%|
|under/custom|equal|138|1|0|6|12|0.7%|
|under/custom|longer|105|0|0|2|20|0.0%|
|under/custom|shorter|174|0|0|9|20|0.0%|
|sprint_custom/winner|equal|7083|34|20|440|644|0.5%|
|sprint_custom/winner|longer|9303|54|15|381|891|0.6%|
|sprint_custom/winner|shorter|7192|11|25|407|618|0.2%|
|sprint_custom/loser|equal|7083|20|34|440|644|0.3%|
|sprint_custom/loser|longer|7192|25|11|407|618|0.3%|
|sprint_custom/loser|shorter|9303|15|54|381|891|0.2%|

### 추가 질주 여력

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|0|144203|276|439|7588|8764|0.2%|
|population/winner|1|106270|231|200|7983|5105|0.2%|
|population/winner|2+|99906|581|261|6499|7978|0.6%|
|population/loser|0|147511|210|556|7286|8653|0.1%|
|population/loser|1|109427|209|257|8084|5368|0.2%|
|population/loser|2+|93441|481|275|6700|7826|0.5%|
|elite/winner|0|70845|137|184|3896|4123|0.2%|
|elite/winner|1|51930|119|89|3851|2469|0.2%|
|elite/winner|2+|49097|286|93|3017|3864|0.6%|
|elite/loser|0|57251|84|152|3077|3142|0.1%|
|elite/loser|1|42014|79|67|3113|2077|0.2%|
|elite/loser|2+|38665|195|68|2380|3276|0.5%|
|ours|0|9220|2|18|105|518|0.0%|
|ours|1|4096|3|11|141|290|0.1%|
|ours|2+|8034|22|24|352|685|0.3%|
|ours/custom|0|233|0|0|4|20|0.0%|
|ours/custom|1|72|0|0|1|10|0.0%|
|ours/custom|2+|89|0|0|3|14|0.0%|
|under/known|0|1086|0|0|30|75|0.0%|
|under/known|1|952|2|0|50|58|0.2%|
|under/known|2+|748|5|1|54|106|0.7%|
|under/known_autoscrim|0|220|0|0|6|13|0.0%|
|under/known_autoscrim|1|174|0|0|7|13|0.0%|
|under/known_autoscrim|2+|127|0|0|10|15|0.0%|
|under/custom|0|198|1|0|10|17|0.5%|
|under/custom|1|144|0|0|5|18|0.0%|
|under/custom|2+|75|0|0|2|17|0.0%|
|sprint_custom/winner|0|9765|32|36|457|911|0.3%|
|sprint_custom/winner|1|5861|23|13|451|425|0.4%|
|sprint_custom/winner|2+|7952|44|11|320|817|0.6%|
|sprint_custom/loser|0|10757|27|65|462|1006|0.3%|
|sprint_custom/loser|1|6654|19|23|428|493|0.3%|
|sprint_custom/loser|2+|6167|14|11|338|654|0.2%|

### 상대와 추가 질주 여력 차

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|equal|114079|242|182|7374|7246|0.2%|
|population/winner|less|114394|228|490|7749|7137|0.2%|
|population/winner|more|121906|618|228|6947|7464|0.5%|
|population/loser|equal|114079|182|242|7374|7246|0.2%|
|population/loser|less|121906|228|618|6947|7464|0.2%|
|population/loser|more|114394|490|228|7749|7137|0.4%|
|elite/winner|equal|56514|130|83|3706|3604|0.2%|
|elite/winner|less|55314|97|200|3816|3357|0.2%|
|elite/winner|more|60044|315|83|3242|3495|0.5%|
|elite/loser|equal|44266|74|58|2996|2797|0.2%|
|elite/loser|less|47233|71|178|2752|2750|0.2%|
|elite/loser|more|46431|213|51|2822|2948|0.5%|
|ours|equal|5261|4|10|90|325|0.1%|
|ours|less|8524|5|21|166|636|0.1%|
|ours|more|7565|18|22|342|532|0.2%|
|ours/custom|equal|67|0|0|3|5|0.0%|
|ours/custom|less|253|0|0|3|27|0.0%|
|ours/custom|more|74|0|0|2|12|0.0%|
|under/known|equal|930|1|0|41|65|0.1%|
|under/known|less|855|0|0|40|64|0.0%|
|under/known|more|1001|6|1|53|110|0.6%|
|under/known_autoscrim|equal|192|0|0|6|12|0.0%|
|under/known_autoscrim|less|131|0|0|6|7|0.0%|
|under/known_autoscrim|more|198|0|0|11|22|0.0%|
|under/custom|equal|138|1|0|6|12|0.7%|
|under/custom|less|174|0|0|9|20|0.0%|
|under/custom|more|105|0|0|2|20|0.0%|
|sprint_custom/winner|equal|7083|34|20|440|644|0.5%|
|sprint_custom/winner|less|7192|11|25|407|618|0.2%|
|sprint_custom/winner|more|9303|54|15|381|891|0.6%|
|sprint_custom/loser|equal|7083|20|34|440|644|0.3%|
|sprint_custom/loser|less|9303|15|54|381|891|0.2%|
|sprint_custom/loser|more|7192|25|11|407|618|0.3%|

### 자기 여유 공간 절대 크기

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|1-5|15881|130|198|5051|150|0.8%|
|population/winner|16+|303615|562|409|13409|20001|0.2%|
|population/winner|6-15|30883|396|293|3610|1696|1.3%|
|population/loser|1-5|16472|124|228|5063|149|0.8%|
|population/loser|16+|303226|467|420|13335|20044|0.2%|
|population/loser|6-15|30681|309|440|3672|1654|1.0%|
|elite/winner|1-5|7345|66|68|2341|64|0.9%|
|elite/winner|16+|149750|286|175|6746|9581|0.2%|
|elite/winner|6-15|14777|190|123|1677|811|1.3%|
|elite/loser|1-5|6628|40|60|1942|61|0.6%|
|elite/loser|16+|119748|205|124|5337|7791|0.2%|
|elite/loser|6-15|11554|113|103|1291|643|1.0%|
|ours|1-5|2560|3|14|215|12|0.1%|
|ours|16+|16970|13|6|227|1352|0.1%|
|ours|6-15|1820|11|33|156|129|0.6%|
|ours/custom|1-5|8|0|0|5|0|0.0%|
|ours/custom|16+|359|0|0|2|43|0.0%|
|ours/custom|6-15|27|0|0|1|1|0.0%|
|under/known|1-5|60|1|0|10|2|1.7%|
|under/known|16+|2522|3|0|103|215|0.1%|
|under/known|6-15|204|3|1|21|22|1.5%|
|under/known_autoscrim|1-5|4|0|0|0|0|0.0%|
|under/known_autoscrim|16+|486|0|0|19|38|0.0%|
|under/known_autoscrim|6-15|31|0|0|4|3|0.0%|
|under/custom|1-5|6|1|0|1|0|16.7%|
|under/custom|16+|373|0|0|12|51|0.0%|
|under/custom|6-15|38|0|0|4|1|0.0%|
|sprint_custom/winner|1-5|753|10|15|235|22|1.3%|
|sprint_custom/winner|16+|20050|39|13|677|1957|0.2%|
|sprint_custom/winner|6-15|2775|50|32|316|174|1.8%|
|sprint_custom/loser|1-5|737|10|22|239|12|1.4%|
|sprint_custom/loser|16+|20019|19|21|655|1968|0.1%|
|sprint_custom/loser|6-15|2822|31|56|334|173|1.1%|

### 같은 라운드 실행 순서

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|earlier|172209|604|404|10947|10410|0.4%|
|population/winner|later|178170|484|496|11123|11437|0.3%|
|population/loser|earlier|178170|496|484|11123|11437|0.3%|
|population/loser|later|172209|404|604|10947|10410|0.2%|
|elite/winner|earlier|85405|309|154|5326|5003|0.4%|
|elite/winner|later|86467|233|212|5438|5453|0.3%|
|elite/loser|earlier|69576|203|123|4336|4378|0.3%|
|elite/loser|later|68354|155|164|4234|4117|0.2%|
|ours|earlier|12340|16|24|352|969|0.1%|
|ours|later|9010|11|29|246|524|0.1%|
|ours/custom|earlier|210|0|0|3|21|0.0%|
|ours/custom|later|184|0|0|5|23|0.0%|
|under/known|earlier|1367|6|1|61|130|0.4%|
|under/known|later|1419|1|0|73|109|0.1%|
|under/known_autoscrim|earlier|255|0|0|13|23|0.0%|
|under/known_autoscrim|later|266|0|0|10|18|0.0%|
|under/custom|earlier|215|1|0|8|31|0.5%|
|under/custom|later|202|0|0|9|21|0.0%|
|sprint_custom/winner|earlier|11042|52|28|572|984|0.5%|
|sprint_custom/winner|later|12536|47|32|656|1169|0.4%|
|sprint_custom/loser|earlier|12536|32|47|656|1169|0.3%|
|sprint_custom/loser|later|11042|28|52|572|984|0.3%|

### 여유 공간 차: low <−4 / mid −4..4 / high >4

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|high|119387|455|216|5498|7611|0.4%|
|population/winner|low|115719|193|317|4954|7249|0.2%|
|population/winner|mid|115273|440|367|11618|6987|0.4%|
|population/loser|high|115719|317|193|4954|7249|0.3%|
|population/loser|low|119387|216|455|5498|7611|0.2%|
|population/loser|mid|115273|367|440|11618|6987|0.3%|
|elite/winner|high|59221|236|88|2795|3754|0.4%|
|elite/winner|low|56718|98|148|2401|3427|0.2%|
|elite/winner|mid|55933|208|130|5568|3275|0.4%|
|elite/loser|high|46050|131|56|1989|2844|0.3%|
|elite/loser|low|46966|96|114|2088|3052|0.2%|
|elite/loser|mid|44914|131|117|4493|2599|0.3%|
|ours|high|6196|5|2|101|481|0.1%|
|ours|low|8921|10|29|155|566|0.1%|
|ours|mid|6233|12|22|342|446|0.2%|
|ours/custom|high|151|0|0|0|17|0.0%|
|ours/custom|low|123|0|0|1|15|0.0%|
|ours/custom|mid|120|0|0|7|12|0.0%|
|under/known|high|992|2|0|39|81|0.2%|
|under/known|low|938|3|1|37|91|0.3%|
|under/known|mid|856|2|0|58|67|0.2%|
|under/known_autoscrim|high|186|0|0|9|14|0.0%|
|under/known_autoscrim|low|189|0|0|8|15|0.0%|
|under/known_autoscrim|mid|146|0|0|6|12|0.0%|
|under/custom|high|174|0|0|10|19|0.0%|
|under/custom|low|108|0|0|3|11|0.0%|
|under/custom|mid|135|1|0|4|22|0.7%|
|sprint_custom/winner|high|7917|41|5|314|702|0.5%|
|sprint_custom/winner|low|7582|15|19|304|680|0.2%|
|sprint_custom/winner|mid|8079|43|36|610|771|0.5%|
|sprint_custom/loser|high|7582|19|15|304|680|0.3%|
|sprint_custom/loser|low|7917|5|41|314|702|0.1%|
|sprint_custom/loser|mid|8079|36|43|610|771|0.4%|

### 켈프까지 거리

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|0-1|247109|1002|789|18191|14388|0.4%|
|population/winner|2-3|80655|83|106|3190|5880|0.1%|
|population/winner|4+|22615|3|5|689|1579|0.0%|
|population/loser|0-1|249967|814|1005|18323|14562|0.3%|
|population/loser|2-3|78310|84|80|3091|5754|0.1%|
|population/loser|4+|22102|2|3|656|1531|0.0%|
|elite/winner|0-1|121019|494|318|8794|6937|0.4%|
|elite/winner|2-3|40655|46|46|1628|2953|0.1%|
|elite/winner|4+|10198|2|2|342|566|0.0%|
|elite/loser|0-1|98440|314|257|7065|5757|0.3%|
|elite/loser|2-3|31391|43|28|1250|2305|0.1%|
|elite/loser|4+|8099|1|2|255|433|0.0%|
|ours|0-1|15522|26|52|516|985|0.2%|
|ours|2-3|4477|1|1|69|403|0.0%|
|ours|4+|1351|0|0|13|105|0.0%|
|ours/custom|0-1|298|0|0|8|27|0.0%|
|ours/custom|2-3|71|0|0|0|11|0.0%|
|ours/custom|4+|25|0|0|0|6|0.0%|
|under/known|0-1|1895|7|1|109|160|0.4%|
|under/known|2-3|662|0|0|20|62|0.0%|
|under/known|4+|229|0|0|5|17|0.0%|
|under/known_autoscrim|0-1|351|0|0|17|27|0.0%|
|under/known_autoscrim|2-3|130|0|0|5|14|0.0%|
|under/known_autoscrim|4+|40|0|0|1|0|0.0%|
|under/custom|0-1|251|1|0|16|22|0.4%|
|under/custom|2-3|97|0|0|0|17|0.0%|
|under/custom|4+|69|0|0|1|13|0.0%|
|sprint_custom/winner|0-1|14966|96|59|1006|1052|0.6%|
|sprint_custom/winner|2-3|4968|3|1|140|517|0.1%|
|sprint_custom/winner|4+|3644|0|0|82|584|0.0%|
|sprint_custom/loser|0-1|15148|58|92|998|1082|0.4%|
|sprint_custom/loser|2-3|4957|1|7|152|512|0.0%|
|sprint_custom/loser|4+|3473|1|0|78|559|0.0%|

### 7×7의 진주 수

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|0|143236|221|227|5492|10548|0.2%|
|population/winner|1-2|105272|356|283|7202|5967|0.3%|
|population/winner|3+|101871|511|390|9376|5332|0.5%|
|population/loser|0|143086|210|245|5488|10591|0.1%|
|population/loser|1-2|104945|294|347|7147|5989|0.3%|
|population/loser|3+|102348|396|496|9435|5267|0.4%|
|elite/winner|0|70008|110|94|2853|4949|0.2%|
|elite/winner|1-2|52612|183|110|3547|2894|0.3%|
|elite/winner|3+|49252|249|162|4364|2613|0.5%|
|elite/loser|0|55227|83|78|2274|3994|0.2%|
|elite/loser|1-2|42234|114|85|2844|2404|0.3%|
|elite/loser|3+|40469|161|124|3452|2097|0.4%|
|ours|0|8366|5|8|123|631|0.1%|
|ours|1-2|6023|10|10|176|397|0.2%|
|ours|3+|6961|12|35|299|465|0.2%|
|ours/custom|0|194|0|0|2|27|0.0%|
|ours/custom|1-2|109|0|0|2|13|0.0%|
|ours/custom|3+|91|0|0|4|4|0.0%|
|under/known|0|1251|4|0|38|117|0.3%|
|under/known|1-2|831|2|1|43|69|0.2%|
|under/known|3+|704|1|0|53|53|0.1%|
|under/known_autoscrim|0|244|0|0|8|22|0.0%|
|under/known_autoscrim|1-2|155|0|0|10|13|0.0%|
|under/known_autoscrim|3+|122|0|0|5|6|0.0%|
|under/custom|0|217|0|0|3|33|0.0%|
|under/custom|1-2|109|1|0|4|14|0.9%|
|under/custom|3+|91|0|0|10|5|0.0%|
|sprint_custom/winner|0|12233|23|11|361|1362|0.2%|
|sprint_custom/winner|1-2|5754|26|18|336|451|0.5%|
|sprint_custom/winner|3+|5591|50|31|531|340|0.9%|
|sprint_custom/loser|0|12177|11|19|336|1387|0.1%|
|sprint_custom/loser|1-2|5861|22|29|349|434|0.4%|
|sprint_custom/loser|3+|5540|27|51|543|332|0.5%|

### 에피소드 밖 아군 머리 BFS8

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|0|159970|812|612|13831|16616|0.5%|
|population/winner|1|101997|190|214|5532|4144|0.2%|
|population/winner|2+|88412|86|74|2707|1087|0.1%|
|population/loser|0|191575|709|796|15249|17686|0.4%|
|population/loser|1|95699|144|223|4826|3459|0.2%|
|population/loser|2+|63105|47|69|1995|702|0.1%|
|elite/winner|0|77626|400|246|6739|7956|0.5%|
|elite/winner|1|50229|93|82|2705|1983|0.2%|
|elite/winner|2+|44017|49|38|1320|517|0.1%|
|elite/loser|0|75169|287|195|5880|6898|0.4%|
|elite/loser|1|37292|50|70|1900|1316|0.1%|
|elite/loser|2+|25469|21|22|790|281|0.1%|
|ours|0|14680|25|49|495|1311|0.2%|
|ours|1|4820|2|3|86|160|0.0%|
|ours|2+|1850|0|1|17|22|0.0%|
|ours/custom|0|238|0|0|7|39|0.0%|
|ours/custom|1|108|0|0|1|5|0.0%|
|ours/custom|2+|48|0|0|0|0|0.0%|
|under/known|0|1379|7|1|91|199|0.5%|
|under/known|1|825|0|0|33|34|0.0%|
|under/known|2+|582|0|0|10|6|0.0%|
|under/known_autoscrim|0|234|0|0|19|33|0.0%|
|under/known_autoscrim|1|191|0|0|2|6|0.0%|
|under/known_autoscrim|2+|96|0|0|2|2|0.0%|
|under/custom|0|203|1|0|11|43|0.5%|
|under/custom|1|128|0|0|4|7|0.0%|
|under/custom|2+|86|0|0|2|2|0.0%|
|sprint_custom/winner|0|11898|66|41|769|1650|0.6%|
|sprint_custom/winner|1|6798|26|17|308|410|0.4%|
|sprint_custom/winner|2+|4882|7|2|151|93|0.1%|
|sprint_custom/loser|0|13131|38|68|828|1768|0.3%|
|sprint_custom/loser|1|6496|17|19|298|329|0.3%|
|sprint_custom/loser|2+|3951|5|12|102|56|0.1%|

### 7×7의 자기 포함 아군/적 머리 수

|집단|조건|N|죽임|피살|교환|이탈|죽임/N|
|---|---|---|---|---|---|---|---|
|population/winner|equal|174858|361|261|9830|11612|0.2%|
|population/winner|higher|145173|520|485|8641|9364|0.4%|
|population/winner|lower|30348|207|154|3599|871|0.7%|
|population/loser|equal|178802|300|344|10079|11820|0.2%|
|population/loser|higher|129053|431|538|7462|8766|0.3%|
|population/loser|lower|42524|169|206|4529|1261|0.4%|
|elite/winner|equal|85474|179|92|4833|5549|0.2%|
|elite/winner|higher|71737|263|215|4290|4479|0.4%|
|elite/winner|lower|14661|100|59|1641|428|0.7%|
|elite/loser|equal|70194|128|90|3848|4550|0.2%|
|elite/loser|higher|51204|170|149|3035|3452|0.3%|
|elite/loser|lower|16532|60|48|1687|493|0.4%|
|ours|equal|10616|8|15|226|800|0.1%|
|ours|higher|7414|15|26|161|592|0.2%|
|ours|lower|3320|4|12|211|101|0.1%|
|ours/custom|equal|189|0|0|1|20|0.0%|
|ours/custom|higher|142|0|0|4|21|0.0%|
|ours/custom|lower|63|0|0|3|3|0.0%|
|under/known|equal|1476|4|0|76|117|0.3%|
|under/known|higher|1075|2|1|44|114|0.2%|
|under/known|lower|235|1|0|14|8|0.4%|
|under/known_autoscrim|equal|271|0|0|15|19|0.0%|
|under/known_autoscrim|higher|208|0|0|7|20|0.0%|
|under/known_autoscrim|lower|42|0|0|1|2|0.0%|
|under/custom|equal|215|0|0|8|31|0.0%|
|under/custom|higher|164|0|0|4|18|0.0%|
|under/custom|lower|38|1|0|5|3|2.6%|
|sprint_custom/winner|equal|12937|39|25|613|1181|0.3%|
|sprint_custom/winner|higher|8723|41|29|466|885|0.5%|
|sprint_custom/winner|lower|1918|19|6|149|87|1.0%|
|sprint_custom/loser|equal|12933|26|35|640|1210|0.2%|
|sprint_custom/loser|higher|8108|17|40|364|834|0.2%|
|sprint_custom/loser|lower|2537|17|24|224|109|0.7%|

### 라운드 시작에 이미 근접한 경우만의 조건

|집단|특징|조건|N|죽임|피살|교환|이탈|
|---|---|---|---|---|---|---|---|
|population/winner|lengthDifference|equal|0|0|0|0|0|
|population/winner|lengthDifference|longer|2307|0|0|0|0|
|population/winner|lengthDifference|shorter|2307|0|0|0|0|
|population/loser|lengthDifference|equal|0|0|0|0|0|
|population/loser|lengthDifference|longer|2307|0|0|0|0|
|population/loser|lengthDifference|shorter|2307|0|0|0|0|
|elite/winner|lengthDifference|equal|0|0|0|0|0|
|elite/winner|lengthDifference|longer|1159|0|0|0|0|
|elite/winner|lengthDifference|shorter|1159|0|0|0|0|
|elite/loser|lengthDifference|equal|0|0|0|0|0|
|elite/loser|lengthDifference|longer|1051|0|0|0|0|
|elite/loser|lengthDifference|shorter|1051|0|0|0|0|
|ours|lengthDifference|equal|0|0|0|0|0|
|ours|lengthDifference|longer|147|0|0|0|0|
|ours|lengthDifference|shorter|147|0|0|0|0|
|under/custom|lengthDifference|equal|0|0|0|0|0|
|under/custom|lengthDifference|longer|0|0|0|0|0|
|under/custom|lengthDifference|shorter|0|0|0|0|0|

|집단|특징|조건|N|죽임|피살|교환|이탈|
|---|---|---|---|---|---|---|---|
|population/winner|order|earlier|2307|0|0|0|0|
|population/winner|order|later|2307|0|0|0|0|
|population/loser|order|earlier|2307|0|0|0|0|
|population/loser|order|later|2307|0|0|0|0|
|elite/winner|order|earlier|1159|0|0|0|0|
|elite/winner|order|later|1159|0|0|0|0|
|elite/loser|order|earlier|1051|0|0|0|0|
|elite/loser|order|later|1051|0|0|0|0|
|ours|order|earlier|147|0|0|0|0|
|ours|order|later|147|0|0|0|0|
|under/custom|order|earlier|0|0|0|0|0|
|under/custom|order|later|0|0|0|0|0|

|집단|특징|조건|N|죽임|피살|교환|이탈|
|---|---|---|---|---|---|---|---|
|population/winner|spaceDifference|high|2307|0|0|0|0|
|population/winner|spaceDifference|low|2307|0|0|0|0|
|population/winner|spaceDifference|mid|0|0|0|0|0|
|population/loser|spaceDifference|high|2307|0|0|0|0|
|population/loser|spaceDifference|low|2307|0|0|0|0|
|population/loser|spaceDifference|mid|0|0|0|0|0|
|elite/winner|spaceDifference|high|1159|0|0|0|0|
|elite/winner|spaceDifference|low|1159|0|0|0|0|
|elite/winner|spaceDifference|mid|0|0|0|0|0|
|elite/loser|spaceDifference|high|1051|0|0|0|0|
|elite/loser|spaceDifference|low|1051|0|0|0|0|
|elite/loser|spaceDifference|mid|0|0|0|0|0|
|ours|spaceDifference|high|147|0|0|0|0|
|ours|spaceDifference|low|147|0|0|0|0|
|ours|spaceDifference|mid|0|0|0|0|0|
|under/custom|spaceDifference|high|0|0|0|0|0|
|under/custom|spaceDifference|low|0|0|0|0|0|
|under/custom|spaceDifference|mid|0|0|0|0|0|


## 5. 죽이는 유형과 시도 뒤 결과

[사실] 한 드래곤의 질주 여러 걸음 사이에 다른 드래곤의 차례가 끼어들지 않는다. 나중 id는 이미 놓인 몸을 보고 판단한다. 따라서 단순히 직전 진행 칸을 가로막았다는 사실은 피할 수 없는 죽임을 뜻하지 않는다.

[사실] 끊기 후보는 상대의 최근 진행 방향 다음 칸에 이번 이동으로 새 몸을 남긴 경우다. 사망 끊기는 실제 충돌한 몸 칸이 최근 2라운드 안에 만들어진 경우다. 그 몸을 만든 이동이 두 걸음 이상이면 질주 끊기다. kelp pin은 빈출구≤1, 켈프와 적 몸이 함께 막고 파트너가 거리≤2다. coil은 적 몸을 지우면 공간이 4칸 이상 늘고 현재 공간≤L+2이며 가까운 적 몸이≥3이다.

[사실] head_bait는 적이 유효한 최대 4걸음 경로로 닿을 수 있는 칸에 머리를 남긴 뒤의 교환 흔적이다. pearl_bait는 진주를 실제 먹은 이동에서 그런 노출이 있었던 흔적이다. 둘 모두 의도를 뜻하지 않는다. 도달 노출 대리 지표는 최대 4걸음만 보므로 더 긴 실제 질주에 대한 노출을 놓칠 수 있다. 직접 충돌 전수는 요청한 이동 길이 전체를 재구성한다. 시도 성공률은 그 조건을 보인 에피소드가 이후 kill/trade로 끝난 비율이지, 다른 수 대비 성공률이 아니다. 사망 유형은 겹치며 exclusive kill은 질주 끊기→끊기→벽 몰기→감기→진주 추격→기타 순서다.

|집단|유형|N 시도 ep|시도 사건|뒤 죽임|죽임/시도|뒤 교환|교환/시도|뒤 사망|종결 대리조건|kill·피살·교환 중 몫|배타 죽임|죽임 중 몫|
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|population/winner|cut_off|2921|3029|233|8.0%|239|8.2%|118|818|3.4% (818/24058)|363|33.4% (363/1088)|
|population/winner|sprint_cut|628|632|62|9.9%|65|10.4%|46|113|0.5% (113/24058)|64|5.9% (64/1088)|
|population/winner|wall_pin|8348|10641|749|9.0%|387|4.6%|853|1010|4.2% (1010/24058)|304|27.9% (304/1088)|
|population/winner|coil|4608|6062|263|5.7%|1483|32.2%|446|7128|29.6% (7128/24058)|166|15.3% (166/1088)|
|population/winner|head_bait|76376|118597|405|0.5%|14333|18.8%|1700|18837|78.3% (18837/24058)|0|0.0% (0/1088)|
|population/winner|pearl_bait|13776|14900|131|1.0%|3243|23.5%|240|4594|19.1% (4594/24058)|1|0.1% (1/1088)|
|population/loser|cut_off|3165|3275|188|5.9%|280|8.8%|114|818|3.4% (818/24058)|342|38.0% (342/900)|
|population/loser|sprint_cut|514|527|43|8.4%|64|12.5%|35|113|0.5% (113/24058)|49|5.4% (49/900)|
|population/loser|wall_pin|8248|10451|583|7.1%|382|4.6%|854|1010|4.2% (1010/24058)|201|22.3% (201/900)|
|population/loser|coil|4610|6011|227|4.9%|1532|33.2%|432|7128|29.6% (7128/24058)|176|19.6% (176/900)|
|population/loser|head_bait|80254|122913|338|0.4%|15018|18.7%|1880|18837|78.3% (18837/24058)|0|0.0% (0/900)|
|population/loser|pearl_bait|13822|14939|102|0.7%|3151|22.8%|277|4594|19.1% (4594/24058)|2|0.2% (2/900)|
|elite/winner|cut_off|1546|1584|126|8.2%|138|8.9%|73|414|3.5% (414/11672)|191|35.2% (191/542)|
|elite/winner|sprint_cut|440|443|37|8.4%|44|10.0%|30|59|0.5% (59/11672)|39|7.2% (39/542)|
|elite/winner|wall_pin|4178|5346|382|9.1%|217|5.2%|420|479|4.1% (479/11672)|147|27.1% (147/542)|
|elite/winner|coil|2087|2739|134|6.4%|631|30.2%|215|3217|27.6% (3217/11672)|79|14.6% (79/542)|
|elite/winner|head_bait|36207|55088|190|0.5%|6800|18.8%|786|9159|78.5% (9159/11672)|0|0.0% (0/542)|
|elite/winner|pearl_bait|6628|7139|69|1.0%|1511|22.8%|96|2189|18.8% (2189/11672)|1|0.2% (1/542)|
|elite/loser|cut_off|1353|1392|83|6.1%|114|8.4%|52|306|3.3% (306/9215)|141|39.4% (141/358)|
|elite/loser|sprint_cut|318|325|26|8.2%|33|10.4%|25|54|0.6% (54/9215)|29|8.1% (29/358)|
|elite/loser|wall_pin|3355|4277|244|7.3%|143|4.3%|330|323|3.5% (323/9215)|73|20.4% (73/358)|
|elite/loser|coil|1734|2281|91|5.2%|503|29.0%|162|2533|27.5% (2533/9215)|67|18.7% (67/358)|
|elite/loser|head_bait|30809|46423|118|0.4%|5700|18.5%|679|7334|79.6% (7334/9215)|0|0.0% (0/358)|
|elite/loser|pearl_bait|5358|5771|40|0.7%|1117|20.8%|94|1754|19.0% (1754/9215)|1|0.3% (1/358)|
|ours|cut_off|147|151|3|2.0%|9|6.1%|5|38|5.6% (38/678)|9|33.3% (9/27)|
|ours|sprint_cut|40|40|1|2.5%|3|7.5%|2|4|0.6% (4/678)|1|3.7% (1/27)|
|ours|wall_pin|411|552|19|4.6%|15|3.6%|89|39|5.8% (39/678)|4|14.8% (4/27)|
|ours|coil|279|347|9|3.2%|59|21.1%|57|286|42.2% (286/678)|9|33.3% (9/27)|
|ours|head_bait|3336|4699|8|0.2%|421|12.6%|87|482|71.1% (482/678)|0|0.0% (0/27)|
|ours|pearl_bait|572|627|5|0.9%|72|12.6%|23|77|11.4% (77/678)|0|0.0% (0/27)|
|ours/custom|cut_off|3|3|0|0.0%|0|0.0%|1|0|0.0% (0/8)|0|— (0/0)|
|ours/custom|sprint_cut|1|1|0|0.0%|0|0.0%|0|0|0.0% (0/8)|0|— (0/0)|
|ours/custom|wall_pin|1|1|0|0.0%|0|0.0%|1|1|12.5% (1/8)|0|— (0/0)|
|ours/custom|coil|2|4|0|0.0%|1|50.0%|0|4|50.0% (4/8)|0|— (0/0)|
|ours/custom|head_bait|101|161|0|0.0%|5|5.0%|1|8|100.0% (8/8)|0|— (0/0)|
|ours/custom|pearl_bait|6|9|0|0.0%|2|33.3%|0|2|25.0% (2/8)|0|— (0/0)|
|under/known|cut_off|22|22|1|4.5%|1|4.5%|2|5|3.5% (5/142)|5|71.4% (5/7)|
|under/known|sprint_cut|0|0|0|—|0|—|0|0|0.0% (0/142)|0|0.0% (0/7)|
|under/known|wall_pin|63|88|3|4.8%|3|4.8%|5|3|2.1% (3/142)|1|14.3% (1/7)|
|under/known|coil|35|46|1|2.9%|12|34.3%|3|35|24.6% (35/142)|0|0.0% (0/7)|
|under/known|head_bait|609|986|2|0.3%|105|17.2%|8|121|85.2% (121/142)|0|0.0% (0/7)|
|under/known|pearl_bait|116|129|0|0.0%|19|16.4%|2|33|23.2% (33/142)|0|0.0% (0/7)|
|under/known_autoscrim|cut_off|3|3|0|0.0%|0|0.0%|0|0|0.0% (0/23)|0|— (0/0)|
|under/known_autoscrim|sprint_cut|0|0|0|—|0|—|0|0|0.0% (0/23)|0|— (0/0)|
|under/known_autoscrim|wall_pin|11|22|0|0.0%|0|0.0%|0|0|0.0% (0/23)|0|— (0/0)|
|under/known_autoscrim|coil|2|2|0|0.0%|1|50.0%|0|3|13.0% (3/23)|0|— (0/0)|
|under/known_autoscrim|head_bait|85|135|0|0.0%|20|23.5%|0|21|91.3% (21/23)|0|— (0/0)|
|under/known_autoscrim|pearl_bait|12|12|0|0.0%|1|8.3%|0|3|13.0% (3/23)|0|— (0/0)|
|under/custom|cut_off|2|2|1|50.0%|0|0.0%|0|0|0.0% (0/18)|0|0.0% (0/1)|
|under/custom|sprint_cut|0|0|0|—|0|—|0|0|0.0% (0/18)|0|0.0% (0/1)|
|under/custom|wall_pin|8|10|1|12.5%|0|0.0%|0|1|5.6% (1/18)|1|100.0% (1/1)|
|under/custom|coil|3|5|0|0.0%|0|0.0%|1|2|11.1% (2/18)|0|0.0% (0/1)|
|under/custom|head_bait|90|152|0|0.0%|14|15.6%|3|17|94.4% (17/18)|0|0.0% (0/1)|
|under/custom|pearl_bait|9|11|0|0.0%|2|22.2%|0|3|16.7% (3/18)|0|0.0% (0/1)|
|sprint_custom/winner|cut_off|167|201|20|12.0%|6|3.6%|7|47|3.4% (47/1387)|22|22.2% (22/99)|
|sprint_custom/winner|sprint_cut|30|30|4|13.3%|2|6.7%|1|9|0.6% (9/1387)|5|5.1% (5/99)|
|sprint_custom/winner|wall_pin|566|658|73|12.9%|15|2.7%|64|99|7.1% (99/1387)|40|40.4% (40/99)|
|sprint_custom/winner|coil|169|203|15|8.9%|42|24.9%|25|385|27.8% (385/1387)|9|9.1% (9/99)|
|sprint_custom/winner|head_bait|4886|7947|31|0.6%|791|16.2%|132|1070|77.1% (1070/1387)|0|0.0% (0/99)|
|sprint_custom/winner|pearl_bait|696|761|3|0.4%|107|15.4%|15|148|10.7% (148/1387)|0|0.0% (0/99)|
|sprint_custom/loser|cut_off|176|182|15|8.5%|11|6.2%|7|47|3.4% (47/1387)|16|26.7% (16/60)|
|sprint_custom/loser|sprint_cut|36|36|3|8.3%|2|5.6%|1|9|0.6% (9/1387)|4|6.7% (4/60)|
|sprint_custom/loser|wall_pin|475|554|47|9.9%|13|2.7%|74|99|7.1% (99/1387)|25|41.7% (25/60)|
|sprint_custom/loser|coil|160|198|4|2.5%|29|18.1%|26|385|27.8% (385/1387)|7|11.7% (7/60)|
|sprint_custom/loser|head_bait|6167|10518|22|0.4%|826|13.4%|153|1070|77.1% (1070/1387)|0|0.0% (0/60)|
|sprint_custom/loser|pearl_bait|631|685|2|0.3%|132|20.9%|9|148|10.7% (148/1387)|0|0.0% (0/60)|

### 전수 분류 뒤 깊게 읽은 사례


#### cut_off: 분류 N=178, 선택 N=3

- [사실] 게임 **625779**, Trauma, **r373–376**, id [317, 338], 결과 kill. [직전 결정](../../exp/duel/reads/elite-cut_off-1.md), [전체 판면](../../exp/duel/boards/elite-cut_off-1.png), [7×7 판단 시야](../../exp/duel/boards/elite-cut_off-1-micro.png), [board.js 원문](../../exp/duel/boards/elite-cut_off-1.txt).
![cut_off: 게임 625779 판단 시야](../../exp/duel/boards/elite-cut_off-1-micro.png)
  - [사실] r374 #338 L3: W @[13, 0]→[12, 0], 빈출구 1, 시야 아군/적 1/0, 섭취 0 → r375 #338 L3: W @[12, 0]→[11, 0], 빈출구 1, 시야 아군/적 1/0, 섭취 0 → r376 #338 L3: W @[11, 0]→[11, 0], 빈출구 0, 시야 아군/적 1/0, 섭취 0
- [사실] 게임 **613705**, Trauma, **r473–476**, id [408, 399], 결과 kill. [직전 결정](../../exp/duel/reads/elite-cut_off-2.md), [전체 판면](../../exp/duel/boards/elite-cut_off-2.png), [7×7 판단 시야](../../exp/duel/boards/elite-cut_off-2-micro.png), [board.js 원문](../../exp/duel/boards/elite-cut_off-2.txt).
  - [사실] r474 #399 L4: W @[13, 0]→[12, 0], 빈출구 1, 시야 아군/적 2/0, 섭취 1 → r475 #399 L5: W @[12, 0]→[11, 0], 빈출구 1, 시야 아군/적 1/0, 섭취 0 → r476 #399 L5: W @[11, 0]→[11, 0], 빈출구 0, 시야 아군/적 2/0, 섭취 0
- [사실] 게임 **707261**, Trauma, **r428–431**, id [408, 123], 결과 kill. [직전 결정](../../exp/duel/reads/elite-cut_off-3.md), [전체 판면](../../exp/duel/boards/elite-cut_off-3.png), [7×7 판단 시야](../../exp/duel/boards/elite-cut_off-3-micro.png), [board.js 원문](../../exp/duel/boards/elite-cut_off-3.txt).
  - [사실] r429 #408 L4: E @[34, 23]→[35, 23], 빈출구 1, 시야 아군/적 0/0, 섭취 0 → r430 #408 L4: E @[35, 23]→[36, 23], 빈출구 1, 시야 아군/적 0/0, 섭취 0 → r431 #408 L4: E @[36, 23]→[36, 23], 빈출구 0, 시야 아군/적 0/0, 섭취 0

#### sprint_cut: 분류 N=35, 선택 N=3

- [사실] 게임 **649396**, Schooltime, **r401–405**, id [566, 580], 결과 kill. [직전 결정](../../exp/duel/reads/elite-sprint_cut-1.md), [전체 판면](../../exp/duel/boards/elite-sprint_cut-1.png), [7×7 판단 시야](../../exp/duel/boards/elite-sprint_cut-1-micro.png), [board.js 원문](../../exp/duel/boards/elite-sprint_cut-1.txt).
![sprint_cut: 게임 649396 판단 시야](../../exp/duel/boards/elite-sprint_cut-1-micro.png)
  - [사실] r403 #566 L3: E @[52, 6]→[53, 6], 빈출구 2, 시야 아군/적 0/1, 섭취 0 → r404 #566 L3: S @[53, 6]→[53, 7], 빈출구 1, 시야 아군/적 0/1, 섭취 0 → r405 #566 L3: E @[53, 7]→[53, 7], 빈출구 0, 시야 아군/적 0/1, 섭취 0
- [사실] 게임 **691380**, Schooltime, **r442–445**, id [314, 271], 결과 kill. [직전 결정](../../exp/duel/reads/elite-sprint_cut-2.md), [전체 판면](../../exp/duel/boards/elite-sprint_cut-2.png), [7×7 판단 시야](../../exp/duel/boards/elite-sprint_cut-2-micro.png), [board.js 원문](../../exp/duel/boards/elite-sprint_cut-2.txt).
  - [사실] r443 #271 L2: W @[43, 11]→[42, 11], 빈출구 1, 시야 아군/적 0/2, 섭취 0 → r444 #271 L2: W @[42, 11]→[41, 11], 빈출구 1, 시야 아군/적 0/1, 섭취 1 → r445 #271 L3: N @[41, 11]→[41, 11], 빈출구 0, 시야 아군/적 0/1, 섭취 0
- [사실] 게임 **623954**, Trauma, **r361–364**, id [161, 215], 결과 kill. [직전 결정](../../exp/duel/reads/elite-sprint_cut-3.md), [전체 판면](../../exp/duel/boards/elite-sprint_cut-3.png), [7×7 판단 시야](../../exp/duel/boards/elite-sprint_cut-3-micro.png), [board.js 원문](../../exp/duel/boards/elite-sprint_cut-3.txt).
  - [사실] r362 #161 L2: E @[11, 15]→[12, 15], 빈출구 1, 시야 아군/적 3/1, 섭취 1 → r363 #161 L3: E @[12, 15]→[13, 15], 빈출구 2, 시야 아군/적 1/1, 섭취 0 → r364 #161 L3: E @[13, 15]→[13, 15], 빈출구 0, 시야 아군/적 1/1, 섭취 0

#### wall_pin: 분류 N=175, 선택 N=3

- [사실] 게임 **659225**, Schooltime, **r211–214**, id [363, 231], 결과 kill. [직전 결정](../../exp/duel/reads/elite-wall_pin-1.md), [전체 판면](../../exp/duel/boards/elite-wall_pin-1.png), [7×7 판단 시야](../../exp/duel/boards/elite-wall_pin-1-micro.png), [board.js 원문](../../exp/duel/boards/elite-wall_pin-1.txt).
![wall_pin: 게임 659225 판단 시야](../../exp/duel/boards/elite-wall_pin-1-micro.png)
  - [사실] r212 #231 L4: N @[15, 10]→[15, 9], 빈출구 2, 시야 아군/적 1/3, 섭취 1 → r213 #231 L5: N @[15, 9]→[15, 8], 빈출구 3, 시야 아군/적 1/2, 섭취 1 → r214 #231 L6: N @[15, 8]→[15, 8], 빈출구 0, 시야 아군/적 0/3, 섭취 0
- [사실] 게임 **613705**, Trauma, **r473–476**, id [408, 399], 결과 kill. [직전 결정](../../exp/duel/reads/elite-wall_pin-2.md), [전체 판면](../../exp/duel/boards/elite-wall_pin-2.png), [7×7 판단 시야](../../exp/duel/boards/elite-wall_pin-2-micro.png), [board.js 원문](../../exp/duel/boards/elite-wall_pin-2.txt).
  - [사실] r474 #399 L4: W @[13, 0]→[12, 0], 빈출구 1, 시야 아군/적 2/0, 섭취 1 → r475 #399 L5: W @[12, 0]→[11, 0], 빈출구 1, 시야 아군/적 1/0, 섭취 0 → r476 #399 L5: W @[11, 0]→[11, 0], 빈출구 0, 시야 아군/적 2/0, 섭취 0
- [사실] 게임 **701782**, Default, **r417–420**, id [236, 71], 결과 trade. [직전 결정](../../exp/duel/reads/elite-wall_pin-3.md), [전체 판면](../../exp/duel/boards/elite-wall_pin-3.png), [7×7 판단 시야](../../exp/duel/boards/elite-wall_pin-3-micro.png), [board.js 원문](../../exp/duel/boards/elite-wall_pin-3.txt).
  - [사실] r417 #236 L5: E @[22, 1]→[23, 1], 빈출구 1, 시야 아군/적 0/1, 섭취 0 → r418 #236 L5: E @[23, 1]→[24, 1], 빈출구 1, 시야 아군/적 0/2, 섭취 0 → r419 #236 L5: E @[24, 1]→[25, 1], 빈출구 1, 시야 아군/적 0/1, 섭취 0

#### coil: 분류 N=1427, 선택 N=3

- [사실] 게임 **800834**, Slithery Fight, **r241–243**, id [20, 615], 결과 trade. [직전 결정](../../exp/duel/reads/elite-coil-1.md), [전체 판면](../../exp/duel/boards/elite-coil-1.png), [7×7 판단 시야](../../exp/duel/boards/elite-coil-1-micro.png), [board.js 원문](../../exp/duel/boards/elite-coil-1.txt).
![coil: 게임 800834 판단 시야](../../exp/duel/boards/elite-coil-1-micro.png)
  - [사실] r241 #20 L6: W @[35, 13]→[34, 13], 빈출구 1, 시야 아군/적 1/2, 섭취 1 → r242 #20 L7: S @[34, 13]→[34, 14], 빈출구 1, 시야 아군/적 0/1, 섭취 0 → r243 #20 L7: W @[34, 14]→[33, 14], 빈출구 1, 시야 아군/적 1/1, 섭취 1
- [사실] 게임 **669078**, Schooltime, **r254–256**, id [418, 260], 결과 trade. [직전 결정](../../exp/duel/reads/elite-coil-2.md), [전체 판면](../../exp/duel/boards/elite-coil-2.png), [7×7 판단 시야](../../exp/duel/boards/elite-coil-2-micro.png), [board.js 원문](../../exp/duel/boards/elite-coil-2.txt).
  - [사실] r253 #418 L7: S @[39, 14]→[39, 15], 빈출구 1, 시야 아군/적 0/2, 섭취 1 → r254 #418 L8: S @[39, 15]→[39, 16], 빈출구 2, 시야 아군/적 0/1, 섭취 0 → r255 #418 L8: E @[39, 16]→[40, 16], 빈출구 1, 시야 아군/적 0/2, 섭취 0
- [사실] 게임 **625497**, Default, **r350–352**, id [170, 197], 결과 kill. [직전 결정](../../exp/duel/reads/elite-coil-3.md), [전체 판면](../../exp/duel/boards/elite-coil-3.png), [7×7 판단 시야](../../exp/duel/boards/elite-coil-3-micro.png), [board.js 원문](../../exp/duel/boards/elite-coil-3.txt).
  - [사실] r350 #170 L8: S @[14, 11]→[14, 12], 빈출구 1, 시야 아군/적 0/1, 섭취 0 → r351 #170 L8: S @[14, 12]→[14, 13], 빈출구 1, 시야 아군/적 0/1, 섭취 0 → r352 #170 L8: S @[14, 13]→[14, 13], 빈출구 0, 시야 아군/적 0/1, 섭취 0

#### head_bait: 분류 N=4315, 선택 N=3

- [사실] 게임 **624225**, Default, **r382–384**, id [206, 204], 결과 trade. [직전 결정](../../exp/duel/reads/elite-head_bait-1.md), [전체 판면](../../exp/duel/boards/elite-head_bait-1.png), [7×7 판단 시야](../../exp/duel/boards/elite-head_bait-1-micro.png), [board.js 원문](../../exp/duel/boards/elite-head_bait-1.txt).
![head_bait: 게임 624225 판단 시야](../../exp/duel/boards/elite-head_bait-1-micro.png)
  - [사실] r381 #206 L5: W @[24, 17]→[23, 17], 빈출구 3, 시야 아군/적 0/1, 섭취 0 → r382 #206 L5: N @[23, 17]→[23, 16], 빈출구 3, 시야 아군/적 1/1, 섭취 0 → r383 #206 L5: N @[23, 16]→[23, 15], 빈출구 2, 시야 아군/적 0/1, 섭취 0
- [사실] 게임 **687878**, Slithery Fight, **r187–189**, id [315, 392], 결과 trade. [직전 결정](../../exp/duel/reads/elite-head_bait-2.md), [전체 판면](../../exp/duel/boards/elite-head_bait-2.png), [7×7 판단 시야](../../exp/duel/boards/elite-head_bait-2-micro.png), [board.js 원문](../../exp/duel/boards/elite-head_bait-2.txt).
  - [사실] r186 #392 L3: W @[43, 1]→[42, 1], 빈출구 3, 시야 아군/적 1/0, 섭취 1 → r187 #392 L4: S @[42, 1]→[42, 2], 빈출구 3, 시야 아군/적 0/1, 섭취 0 → r188 #392 L4: S @[42, 2]→[42, 3], 빈출구 1, 시야 아군/적 0/1, 섭취 0
- [사실] 게임 **739890**, Schooltime, **r130–132**, id [60, 154], 결과 trade. [직전 결정](../../exp/duel/reads/elite-head_bait-3.md), [전체 판면](../../exp/duel/boards/elite-head_bait-3.png), [7×7 판단 시야](../../exp/duel/boards/elite-head_bait-3-micro.png), [board.js 원문](../../exp/duel/boards/elite-head_bait-3.txt).
  - [사실] r129 #154 L3: S @[18, 0]→[18, 1], 빈출구 2, 시야 아군/적 1/0, 섭취 0 → r130 #154 L3: W @[18, 1]→[17, 1], 빈출구 3, 시야 아군/적 1/0, 섭취 1 → r131 #154 L4: W @[17, 1]→[16, 1], 빈출구 2, 시야 아군/적 0/1, 섭취 0

#### pearl_bait: 분류 N=963, 선택 N=3

- [사실] 게임 **628358**, Slithery Fight, **r417–419**, id [1701, 919], 결과 trade. [직전 결정](../../exp/duel/reads/elite-pearl_bait-1.md), [전체 판면](../../exp/duel/boards/elite-pearl_bait-1.png), [7×7 판단 시야](../../exp/duel/boards/elite-pearl_bait-1-micro.png), [board.js 원문](../../exp/duel/boards/elite-pearl_bait-1.txt).
![pearl_bait: 게임 628358 판단 시야](../../exp/duel/boards/elite-pearl_bait-1-micro.png)
  - [사실] r416 #1701 L3: E @[31, 4]→[32, 4], 빈출구 2, 시야 아군/적 1/0, 섭취 1 → r417 #1701 L4: E @[32, 4]→[33, 4], 빈출구 2, 시야 아군/적 1/1, 섭취 0 → r418 #1701 L4: E @[33, 4]→[34, 4], 빈출구 3, 시야 아군/적 1/1, 섭취 1
- [사실] 게임 **686415**, Schooltime, **r219–221**, id [504, 280], 결과 trade. [직전 결정](../../exp/duel/reads/elite-pearl_bait-2.md), [전체 판면](../../exp/duel/boards/elite-pearl_bait-2.png), [7×7 판단 시야](../../exp/duel/boards/elite-pearl_bait-2-micro.png), [board.js 원문](../../exp/duel/boards/elite-pearl_bait-2.txt).
  - [사실] r218 #504 L3: N @[6, 8]→[6, 7], 빈출구 3, 시야 아군/적 1/0, 섭취 0 → r219 #504 L3: E @[6, 7]→[7, 7], 빈출구 3, 시야 아군/적 1/1, 섭취 1 → r220 #504 L4: E @[7, 7]→[8, 7], 빈출구 3, 시야 아군/적 0/1, 섭취 1
- [사실] 게임 **706255**, Slithery Fight, **r94–96**, id [131, 294], 결과 trade. [직전 결정](../../exp/duel/reads/elite-pearl_bait-3.md), [전체 판면](../../exp/duel/boards/elite-pearl_bait-3.png), [7×7 판단 시야](../../exp/duel/boards/elite-pearl_bait-3-micro.png), [board.js 원문](../../exp/duel/boards/elite-pearl_bait-3.txt).
  - [사실] r93 #294 L2: N @[31, 14]→[31, 13], 빈출구 3, 시야 아군/적 1/1, 섭취 1 → r94 #294 L3: N @[31, 13]→[31, 12], 빈출구 3, 시야 아군/적 0/2, 섭취 1 → r95 #294 L4: E @[31, 12]→[32, 12], 빈출구 3, 시야 아군/적 0/2, 섭취 1

### 판면과 세 결정을 직접 읽은 해석

[사실] 자동으로 직전 결정을 정리하고 그림을 만든 사례 N=132, 분류 N=45. 이 중 strict 유형별 대표 세 결정 N=18사례를 직접 비교하고, 전체/7×7 PNG N=12장을 육안 확인했다. 나머지 그림의 생성·연결은 파일 검사로 확인했다.

[사실] strict 대표 끊기 3/3은 Trauma 포털 협로였다(625779 r374–376, 613705 r474–476, 707261 r429–431). 피해자는 출구 1→1→0에서 같은 방향을 계속 선택했다. 625779의 실제 충돌 몸은 포털 반대편에 있어 머리 중심 7×7 그림만으로 보이지 않는다. 몸의 생성 시각을 기준으로 붙인 cut_off를 평지에서 머리가 눈앞을 가로지른 사건으로 읽으면 안 된다.

[사실] 질주 끊기 대표 3/3에서는 피해자의 마지막 차례 출구가 0이었다. 649396 r403의 L15 적은 NNE로 장벽을 놓고, L3 피해자는 r403 E(출구2)→r404 S(1)→r405 E(0)로 몸에 부딪혔다. 691380은 r443 EE 이후 피해자가 W→W(진주1)→N(출구0)으로 들어갔다. 623954는 긴 조각이 split한 뒤 L2 부모가 진주를 먹으며 SE를 실행한 사례다. 질주 절단을 언제나 큰 길이 우세의 기술로 해석할 수 없다.

[사실] 벽 몰기 대표 659225 r212–214에서는 피해자가 N으로 진주를 두 번 먹어 L4→5→6이 되었지만, 적의 r213 WWS 뒤 출구가 3→0이 되어 켈프에 충돌했다. 613705은 포털 몸 충돌과 겹치고, 701782는 벽 몰기 조건 뒤 정면교환으로 끝났다(대표 N=3). 유형 조건과 종결 원인은 구분해야 한다.

[사실] 감기 대표 N=3 중 800834 r243과 669078 r256은 정면교환, 625497 r352는 켈프 사망이었다. 800834의 피해 편은 협로에서 W→S→W로 진주를 먹고, 상대는 N→E→N(출구0)으로 교환했다. 완전히 닫힌 원형 포위를 세 사례에서 입증한 것은 아니다. coil 대리 조건은 켈프와 몸이 함께 줄인 공간도 포착한다.

[사실] head_bait 대표 N=3 모두 낮은 id가 2걸음으로 들어가 다음 차례가 아직 없는 높은 id를 죽였다(624225 r384 SE, 687878 r189 SE, 739890 r132 ES). 수동 편의 직전 빈출구는 2/1/2였다. pearl_bait 대표 N=3에서도 수동 편은 직전 두 차례 중 진주를 먹었고, 낮은 id가 SW/SS/WW 두 걸음으로 교환했다(628358 r419, 686415 r221, 706255 r96). 의도적 유인인지 정상 진주 추격 뒤 노출인지 기보만으로 구분되지 않는다.

[해석] 직접 확인한 행동은 출구 감소, 몸 장벽의 유지, id 순서에 따른 다음 행동 기회의 차이다. ‘미끼를 설계했다’·‘코일을 계획했다’는 별도 의도 증거가 없다. 지도 독립 후보는 이 관측 가능한 상태를 조건으로 해야 한다. 포털 반대편의 미관측 몸을 구현이 안다고 가정하는 규칙은 제외한다.

[사실] 맞춤 지도의 질주 끊기도 보인다: 806693 r254 WWW 뒤 피해자는 r255 N(출구0), 806976 r302 NN 뒤 r303 W(0), 806777 r440 ENEE 뒤 높은 id 피해자가 E(0)를 선택했다(대표 N=3). [세 결정과 그림 목록](../../exp/duel/selection.json)의 bracket_contacts/sprint_cut에 연결된다. 이 세 사례는 군집 포함 직접 충돌이며 고립 1:1로 바꿔 부르지 않는다.

### 군집을 포함한 직접 충돌 전수 (다른 분모)

[사실] 직접 충돌/근접 사망 사건 N=1,146,139. 고립 에피소드가 제삼자로 끝난 뒤의 싸움을 별도로 남겼다. O는 실제 상대 몸 id로 귀속한다. W/S는 적 머리 근처라는 연관만 뜻한다. head_bait는 직전 적 관측, pearl_bait는 최근 진주 섭취 흔적이라 에피소드 reach 기준보다 넓다. 두 대리 지표의 N을 합하지 않는다.

|집단|N 사건|머리 교환|몸으로 죽임|적 몸에 피살|근접 벽/자기 사망|제삼 머리 근접|
|---|---|---|---|---|---|---|
|population/winner|1127966|1049390|23736|21375|15767|1057663|
|population/loser|1127966|1049390|21375|23736|17698|1057663|
|elite/winner|571952|534426|12757|9782|5950|537589|
|elite/loser|477820|447181|9865|8319|6014|450245|
|ours|15455|13483|599|668|473|13956|
|ours/custom|123|108|1|11|3|106|
|under/known|6285|5963|161|54|7|5840|
|under/known_autoscrim|1343|1281|29|23|2|1245|
|under/custom|624|595|4|1|1|562|
|sprint_custom/winner|31541|28469|839|583|731|27813|
|sprint_custom/loser|31541|28469|583|839|919|27813|

[사실] 우리 직접 피살의 유형 수: {'coil': 217, 'other_body_or_near_wall': 92, 'wall_pin': 383, 'sprint_cut': 66, 'cut_off': 365, 'pearl_bait': 18}. 우리 실제 몸으로 죽임의 유형 수: {'cut_off': 227, 'near_head': 342, 'other_body_or_near_wall': 48, 'coil': 292, 'far_head': 257, 'sprint_cut': 25, 'pearl_bait': 3, 'wall_pin': 4}. near_head/far_head는 상대 머리 거리≤4/초과의 중복 진단 열이다.

[사실] 군집 포함 cut_off, 분류 N=8372, 선택 N=3: 게임 617076 r15 ([세 결정](../../exp/duel/reads/contacts-cut_off-1.md), [판면](../../exp/duel/boards/contacts-cut_off-1.png), [판단 시야](../../exp/duel/boards/contacts-cut_off-1-micro.png)); 게임 637158 r246 ([세 결정](../../exp/duel/reads/contacts-cut_off-2.md), [판면](../../exp/duel/boards/contacts-cut_off-2.png), [판단 시야](../../exp/duel/boards/contacts-cut_off-2-micro.png)); 게임 668957 r86 ([세 결정](../../exp/duel/reads/contacts-cut_off-3.md), [판면](../../exp/duel/boards/contacts-cut_off-3.png), [판단 시야](../../exp/duel/boards/contacts-cut_off-3-micro.png)).
[사실] 군집 포함 sprint_cut, 분류 N=1036, 선택 N=3: 게임 595781 r159 ([세 결정](../../exp/duel/reads/contacts-sprint_cut-1.md), [판면](../../exp/duel/boards/contacts-sprint_cut-1.png), [판단 시야](../../exp/duel/boards/contacts-sprint_cut-1-micro.png)); 게임 613690 r399 ([세 결정](../../exp/duel/reads/contacts-sprint_cut-2.md), [판면](../../exp/duel/boards/contacts-sprint_cut-2.png), [판단 시야](../../exp/duel/boards/contacts-sprint_cut-2-micro.png)); 게임 615604 r157 ([세 결정](../../exp/duel/reads/contacts-sprint_cut-3.md), [판면](../../exp/duel/boards/contacts-sprint_cut-3.png), [판단 시야](../../exp/duel/boards/contacts-sprint_cut-3-micro.png)).
[사실] 군집 포함 wall_pin, 분류 N=10894, 선택 N=3: 게임 588078 r270 ([세 결정](../../exp/duel/reads/contacts-wall_pin-1.md), [판면](../../exp/duel/boards/contacts-wall_pin-1.png), [판단 시야](../../exp/duel/boards/contacts-wall_pin-1-micro.png)); 게임 588116 r325 ([세 결정](../../exp/duel/reads/contacts-wall_pin-2.md), [판면](../../exp/duel/boards/contacts-wall_pin-2.png), [판단 시야](../../exp/duel/boards/contacts-wall_pin-2-micro.png)); 게임 597488 r198 ([세 결정](../../exp/duel/reads/contacts-wall_pin-3.md), [판면](../../exp/duel/boards/contacts-wall_pin-3.png), [판단 시야](../../exp/duel/boards/contacts-wall_pin-3-micro.png)).
[사실] 군집 포함 coil, 분류 N=7332, 선택 N=3: 게임 623945 r166 ([세 결정](../../exp/duel/reads/contacts-coil-1.md), [판면](../../exp/duel/boards/contacts-coil-1.png), [판단 시야](../../exp/duel/boards/contacts-coil-1-micro.png)); 게임 638415 r210 ([세 결정](../../exp/duel/reads/contacts-coil-2.md), [판면](../../exp/duel/boards/contacts-coil-2.png), [판단 시야](../../exp/duel/boards/contacts-coil-2-micro.png)); 게임 632923 r161 ([세 결정](../../exp/duel/reads/contacts-coil-3.md), [판면](../../exp/duel/boards/contacts-coil-3.png), [판단 시야](../../exp/duel/boards/contacts-coil-3-micro.png)).
[사실] 군집 포함 head_bait, 분류 N=263348, 선택 N=3: 게임 586222 r43 ([세 결정](../../exp/duel/reads/contacts-head_bait-1.md), [판면](../../exp/duel/boards/contacts-head_bait-1.png), [판단 시야](../../exp/duel/boards/contacts-head_bait-1-micro.png)); 게임 586225 r117 ([세 결정](../../exp/duel/reads/contacts-head_bait-2.md), [판면](../../exp/duel/boards/contacts-head_bait-2.png), [판단 시야](../../exp/duel/boards/contacts-head_bait-2-micro.png)); 게임 586226 r258 ([세 결정](../../exp/duel/reads/contacts-head_bait-3.md), [판면](../../exp/duel/boards/contacts-head_bait-3.png), [판단 시야](../../exp/duel/boards/contacts-head_bait-3-micro.png)).
[사실] 군집 포함 pearl_bait, 분류 N=74159, 선택 N=3: 게임 586227 r364 ([세 결정](../../exp/duel/reads/contacts-pearl_bait-1.md), [판면](../../exp/duel/boards/contacts-pearl_bait-1.png), [판단 시야](../../exp/duel/boards/contacts-pearl_bait-1-micro.png)); 게임 586372 r152 ([세 결정](../../exp/duel/reads/contacts-pearl_bait-2.md), [판면](../../exp/duel/boards/contacts-pearl_bait-2.png), [판단 시야](../../exp/duel/boards/contacts-pearl_bait-2-micro.png)); 게임 586387 r279 ([세 결정](../../exp/duel/reads/contacts-pearl_bait-3.md), [판면](../../exp/duel/boards/contacts-pearl_bait-3.png), [판단 시야](../../exp/duel/boards/contacts-pearl_bait-3-micro.png)).

## 6. 우리 온라인 결투와 kill path

|집단|N 정면접촉|들어감|들이받힘|들어감/N|질주 주체|수동 직전 출구≥2|N 직전 결정|
|---|---|---|---|---|---|---|---|
|population/winner|1049390|590915|458475|56.3%|296061|364196|452843|
|population/loser|1049390|458475|590915|43.7%|217804|473421|584052|
|elite/winner|534426|309628|224798|57.9%|157465|178172|221869|
|elite/loser|447181|202270|244911|45.2%|97701|195970|241628|
|ours|13483|2368|11115|17.6%|619|7432|10993|
|ours/custom|108|93|15|86.1%|49|3|15|
|under/known|5963|3014|2949|50.5%|1393|2366|2922|
|under/known_autoscrim|1281|576|705|45.0%|302|596|700|
|under/custom|595|325|270|54.6%|187|202|269|
|sprint_custom/winner|28469|15648|12821|55.0%|8097|9375|12676|
|sprint_custom/loser|28469|12821|15648|45.0%|5954|11601|15514|

[사실] Trophy만의 같은 분모 비교: elite/winner 정면접촉 N=49888, 들어감 31276, 수동 18612; elite/loser 정면접촉 N=40092, 들어감 16504, 수동 23588; ours 정면접촉 N=1176, 들어감 82, 수동 1094.

[사실] 우리 자기 차례 N=4,426,468; 3–4걸음 TRADE 선택 N=224, 전체 차례 중 0.0%. 후보 생성/적격 차례의 분모는 알 수 없다.
[사실] 우리 에피소드 N=491479, 죽임 N=27, 피살 N=53, 교환 N=598. 정면접촉 전체와 isolated 결투의 분모는 다르다. cuts와 killer-body의 상대가 누구인지 직접 대조했다.

|선택 지시 태그|N 발동|적 머리 교환|그밖/불일치|
|---|---|---|---|
|kill_path_selected|224|224|0|
|trade_1_2_selected|961|961|0|
|trade_veto_logged|221|0|221|

[사실] plan.cpp의 kill paths 분기는 3–4걸음으로 적 머리에 닿아 tradeValue를 받는 후보를 만든다. 몸으로 자르는 후보라는 뜻이 아니다. 선택되면 TRADE를 기록하고, 기보 이동 길이≥3으로 해당 분기를 식별했다. 1–2걸음 TRADE는 별도다. lntv는 지역 열세로 후보가 거부되었다는 흔적이며, 모든 생성 후보의 N은 기록되지 않는다. 성공은 적 머리 교환의 실행 여부이고 최종 경기 승리나 몸으로 죽임과 구별한다.

[사실] ours/killed, 분류 N=53, 선택 N=3: 게임 718407 r444 ([직전 세 결정](../../exp/duel/reads/ours-killed-1.md)); 게임 687755 r282 ([직전 세 결정](../../exp/duel/reads/ours-killed-2.md)); 게임 666166 r460 ([직전 세 결정](../../exp/duel/reads/ours-killed-3.md)).
[사실] ours/kill, 분류 N=27, 선택 N=3: 게임 687773 r459 ([직전 세 결정](../../exp/duel/reads/ours-kill-1.md)); 게임 702618 r295 ([직전 세 결정](../../exp/duel/reads/ours-kill-2.md)); 게임 748887 r397 ([직전 세 결정](../../exp/duel/reads/ours-kill-3.md)).
[사실] ours/trade_passive, 분류 N=411, 선택 N=3: 게임 650988 r60 ([직전 세 결정](../../exp/duel/reads/ours-trade_passive-1.md)); 게임 650932 r433 ([직전 세 결정](../../exp/duel/reads/ours-trade_passive-2.md)); 게임 650952 r147 ([직전 세 결정](../../exp/duel/reads/ours-trade_passive-3.md)).
[사실] ours/trade_mover, 분류 N=187, 선택 N=3: 게임 702628 r410 ([직전 세 결정](../../exp/duel/reads/ours-trade_mover-1.md)); 게임 666235 r168 ([직전 세 결정](../../exp/duel/reads/ours-trade_mover-2.md)); 게임 740358 r228 ([직전 세 결정](../../exp/duel/reads/ours-trade_mover-3.md)).
[사실] ours_contacts/killed, 분류 N=1141, 선택 N=3: 게임 677119 r225 ([직전 세 결정](../../exp/duel/reads/ours_contacts-killed-1.md)); 게임 748854 r222 ([직전 세 결정](../../exp/duel/reads/ours_contacts-killed-2.md)); 게임 730074 r425 ([직전 세 결정](../../exp/duel/reads/ours_contacts-killed-3.md)).
[사실] ours_contacts/kill, 분류 N=831, 선택 N=3: 게임 646183 r129 ([직전 세 결정](../../exp/duel/reads/ours_contacts-kill-1.md)); 게임 632326 r278 ([직전 세 결정](../../exp/duel/reads/ours_contacts-kill-2.md)); 게임 646192 r344 ([직전 세 결정](../../exp/duel/reads/ours_contacts-kill-3.md)).
[사실] ours_contacts/trade_passive, 분류 N=11115, 선택 N=3: 게임 632365 r91 ([직전 세 결정](../../exp/duel/reads/ours_contacts-trade_passive-1.md)); 게임 646163 r118 ([직전 세 결정](../../exp/duel/reads/ours_contacts-trade_passive-2.md)); 게임 646183 r161 ([직전 세 결정](../../exp/duel/reads/ours_contacts-trade_passive-3.md)).
[사실] ours_contacts/trade_mover, 분류 N=2368, 선택 N=3: 게임 687755 r289 ([직전 세 결정](../../exp/duel/reads/ours_contacts-trade_mover-1.md)); 게임 707850 r204 ([직전 세 결정](../../exp/duel/reads/ours_contacts-trade_mover-2.md)); 게임 712904 r268 ([직전 세 결정](../../exp/duel/reads/ours_contacts-trade_mover-3.md)).

### 우리에게 보인 실패와 본선의 차이

[사실] 우리 피살 대표에서 748854 r220 E로 진주1을 먹은 L2는 r221 E(출구1, 점수 −1113.0) 뒤 r222 no-exit(0)로 적 몸에 닿았다. 730074는 r423 W(출구1)→r424 escape-split4(0)→r425 L2 no-exit(0)였다. 687755는 r280 N→r281 escape-split5→r282 L2 no-exit로 켈프 사망했다. 분열로 길이를 줄인 사실이 빈출구를 만든다는 뜻은 아니다(서로 다른 게임 사례 N=3).

[사실] 우리 실제 몸으로 죽임 대표 632326 r275–278에서는 W→S→E로 남긴 몸에 상대가 S로 충돌했다. 646192 r342–344에서도 S→S→W의 몸 장벽에 상대가 escape split 뒤 W로 부딪혔다. 선택 태그는 통상 이동 평가 문자열이었고 TRADE가 아니었다(사례 N=2). 따라서 실제 몸 죽임과 kill-path 지시를 같은 기제로 합하지 않는다.

[사실] 본선 맞춤 지도 우리 N=7판에서는 적 정면접촉 108 중 능동 93(86.1%), 수동 15였다. 능동 93 중 최종 TRADE 태그 77(82.8%)이고, 자신이 짧은 경우 82/93이었다. 직전 자기 포함 가시 머릿수는 우세54/동수28/열세11이었다. 비교 집단 맞춤 지도 승자의 열세 진입은 1,633/15,648=10.4%, 우리는 11/93=11.8%다. 보이는 수 열세만으로 우리 교환을 설명할 차이는 크지 않다.

[사실] 우리 본선 사망 N=594: 켈프252, 자기 몸79, 몸147, 정면116. 몸147은 적11/아군136이며, 정면116은 적 접촉108에 대응하는 우리 사망108과 아군 접촉 사망8이다. 직접 적 몸 죽임과 아군 몸 충돌을 분리했다. 고립 episode 죽임/피살은 각각 0으로, 실제 적 몸 피살11을 고립 결투 결과0과 혼동하지 않는다.

[해석] 전체 온라인의 낮은 능동 비율을 본선에 그대로 옮겨 ‘더 자주 들이받자’고 권고할 근거가 없다. 본선 N=7은 작고 교환 뒤 승리의 인과 효과도 알 수 없다. 먼저 켈프·자기/아군 몸과 후속 출구를 진단하고, TRADE를 허용한 목적이 왕 성장·생존으로 이어지는지 기제로 확인하는 쪽이 이 자료에 맞는다.

## 7. UnderTheC: 자동 대전 기준선과 본선 맞춤 지도

[사실] 사용자 관찰은 본선의 처음 보는 지도 대응에 한정된다. under/known_autoscrim은 별도 전달된 30판의 아는 지도 기준선이다. under/known에는 수집기가 받은 아는 지도 대전도 합쳤다. under/custom은 본선의 맞춤 지도 대전이며 서로 합해 처음 보는 지도 능력을 주장하지 않는다.


### under/known_autoscrim

|r|N 도달 경기|평균 머리|평균 최장|평균 총길이|
|---|---|---|---|---|
|0|30|3.40|6.17|14.17|
|10|30|5.90|2.87|14.30|
|25|30|6.90|3.27|17.40|
|50|28|10.93|3.71|27.64|
|100|27|16.56|3.89|41.85|
|150|24|21.21|3.83|52.04|
|250|20|32.80|3.90|81.00|
|350|16|24.50|11.44|80.25|
|450|13|10.00|28.15|104.15|
|499|13|8.08|33.00|112.15|

[사실] 길이 차례 분포 N=213,226: {'2': 115389, '3-4': 83525, '5-7': 6534, '8+': 7778}. 분열 N=6,275, 시점 {'0-49': 519, '50-149': 1509, '150-349': 3449, '350-500': 798}. 부모+새끼 형태 상위 6개 [('2+2', 5150), ('2+3', 377), ('2+4', 216), ('3+2', 163), ('3+3', 88), ('2+5', 47)].
[사실] L≤4 조각의 5라운드마다 자기 turnStart 위치 N=39,835: 왕 거리>5 36018, 적 머리가 7×7에 있음 12079, 샘 거리≤3 6299. 거리 평균은 8 초과를 9로 자른 값: 왕 8.22, 적 7.86, 샘 7.46. 샘은 지도를 구분할 수 있는 판만 기존 지도 타일로 읽은 연구 정보다. custom 집단의 기존 표 기반 샘 값 0/거리9는 미관측 대체값이므로 실제 샘에서 멀다는 증거가 아니다. 위 경험적 재생 칸 통계와 구분한다.
[사실] 사망 원인 N=5,978: {'A': 4122, 'H': 1697, 'O': 154, 'S': 3, 'W': 2}. 최종 최장 N=30, 평균 15.90, 중앙값 4.5, 최종 생존 경기 N=23.

### under/known

|r|N 도달 경기|평균 머리|평균 최장|평균 총길이|
|---|---|---|---|---|
|0|189|3.46|6.66|15.02|
|10|189|6.30|2.95|15.40|
|25|186|7.84|3.30|19.45|
|50|183|11.86|3.64|29.78|
|100|175|19.02|3.83|47.62|
|150|161|23.56|3.81|58.88|
|250|137|30.20|3.98|75.46|
|350|108|21.64|11.69|77.04|
|450|96|9.40|27.96|84.77|
|499|93|8.45|33.86|92.59|

[사실] 길이 차례 분포 N=1,406,482: {'2': 746429, '3-4': 560294, '5-7': 53807, '8+': 45952}. 분열 N=46,108, 시점 {'0-49': 3769, '50-149': 12726, '150-349': 24432, '350-500': 5181}. 부모+새끼 형태 상위 6개 [('2+2', 34820), ('2+3', 3886), ('2+4', 2427), ('3+2', 1803), ('3+3', 656), ('2+5', 486)].
[사실] L≤4 조각의 5라운드마다 자기 turnStart 위치 N=261,558: 왕 거리>5 237551, 적 머리가 7×7에 있음 67950, 샘 거리≤3 53995. 거리 평균은 8 초과를 9로 자른 값: 왕 8.25, 적 8.12, 샘 6.85. 샘은 지도를 구분할 수 있는 판만 기존 지도 타일로 읽은 연구 정보다. custom 집단의 기존 표 기반 샘 값 0/거리9는 미관측 대체값이므로 실제 샘에서 멀다는 증거가 아니다. 위 경험적 재생 칸 통계와 구분한다.
[사실] 사망 원인 N=44,007: {'H': 8789, 'A': 34296, 'O': 892, 'S': 23, 'W': 7}. 최종 최장 N=189, 평균 18.81, 중앙값 9, 최종 생존 경기 N=151.

### under/custom

|r|N 도달 경기|평균 머리|평균 최장|평균 총길이|
|---|---|---|---|---|
|0|14|4.57|4.14|14.00|
|10|14|6.57|3.00|15.43|
|25|14|9.00|3.86|22.36|
|50|14|15.00|3.36|36.64|
|100|14|25.79|3.36|61.71|
|150|14|31.36|4.00|79.07|
|250|12|42.08|4.17|104.42|
|350|11|39.36|7.45|104.82|
|450|10|12.90|31.50|124.40|
|499|10|10.60|43.80|151.80|

[사실] 본선에서 관측한 빠른 자연 재생 칸의 부분집합: 자연 진주 섭취 뒤 재생 간격≤12를 두 번 이상 보고, 간격 중앙값≤12인 칸만 사용했다. 판 전체를 읽은 사후 정보이며 모든 샘의 정답 표가 아니다. 해당 칸이 식별된 경기 N=14, 작은 조각 위치 N=34306, 거리≤3 N=6728, 8 초과를 9로 자른 평균 거리 6.69. death drop은 자연 진주 origin과 구분해 제외했다.

[사실] 길이 차례 분포 N=181,414: {'2': 97767, '3-4': 73582, '5-7': 4733, '8+': 5332}. 분열 N=5,524, 시점 {'0-49': 266, '50-149': 1144, '150-349': 3187, '350-500': 927}. 부모+새끼 형태 상위 6개 [('2+2', 4386), ('2+3', 472), ('2+4', 271), ('3+2', 146), ('3+3', 60), ('2+5', 44)].
[사실] L≤4 조각의 5라운드마다 자기 turnStart 위치 N=34,306: 왕 거리>5 32035, 적 머리가 7×7에 있음 3948, 샘 거리≤3 0. 거리 평균은 8 초과를 9로 자른 값: 왕 8.46, 적 8.27, 샘 9.00. 샘은 지도를 구분할 수 있는 판만 기존 지도 타일로 읽은 연구 정보다. custom 집단의 기존 표 기반 샘 값 0/거리9는 미관측 대체값이므로 실제 샘에서 멀다는 증거가 아니다. 위 경험적 재생 칸 통계와 구분한다.
[사실] 사망 원인 N=5,465: {'A': 4637, 'H': 809, 'O': 18, 'W': 1}. 최종 최장 N=14, 평균 31.71, 중앙값 37.5, 최종 생존 경기 N=11.

### elite/winner

|r|N 도달 경기|평균 머리|평균 최장|평균 총길이|
|---|---|---|---|---|
|0|11847|3.63|7.46|16.49|
|10|11847|7.05|4.01|17.95|
|25|11816|9.59|3.98|23.94|
|50|11574|15.43|4.17|38.32|
|100|10732|27.28|4.50|68.42|
|150|9718|35.26|5.24|93.13|
|250|7816|43.35|7.69|124.93|
|350|6686|36.74|17.99|131.38|
|450|6091|19.35|37.77|129.12|
|499|5859|12.89|46.91|128.72|

[사실] 본선에서 관측한 빠른 자연 재생 칸의 부분집합: 자연 진주 섭취 뒤 재생 간격≤12를 두 번 이상 보고, 간격 중앙값≤12인 칸만 사용했다. 판 전체를 읽은 사후 정보이며 모든 샘의 정답 표가 아니다. 해당 칸이 식별된 경기 N=7, 작은 조각 위치 N=20380, 거리≤3 N=4753, 8 초과를 9로 자른 평균 거리 6.28. death drop은 자연 진주 origin과 구분해 제외했다.

[사실] 길이 차례 분포 N=123,711,039: {'2': 66376192, '3-4': 45479766, '5-7': 6655086, '8+': 5199995}. 분열 N=3,307,568, 시점 {'0-49': 296253, '50-149': 899552, '150-349': 1594652, '350-500': 517111}. 부모+새끼 형태 상위 6개 [('2+2', 2372060), ('2+3', 301117), ('2+4', 166802), ('3+2', 126932), ('4+2', 57871), ('2+5', 54376)].
[사실] L≤4 조각의 5라운드마다 자기 turnStart 위치 N=22,379,852: 왕 거리>5 20756502, 적 머리가 7×7에 있음 5260654, 샘 거리≤3 4577436. 거리 평균은 8 초과를 9로 자른 값: 왕 8.41, 적 8.25, 샘 6.84. 샘은 지도를 구분할 수 있는 판만 기존 지도 타일로 읽은 연구 정보다. custom 집단의 기존 표 기반 샘 값 0/거리9는 미관측 대체값이므로 실제 샘에서 멀다는 증거가 아니다. 위 경험적 재생 칸 통계와 구분한다.
[사실] 사망 원인 N=3,046,939: {'A': 717850, 'H': 636548, 'O': 311888, 'S': 656354, 'W': 724299}. 최종 최장 N=11847, 평균 27.14, 중앙값 22, 최종 생존 경기 N=11847.

### elite/loser

|r|N 도달 경기|평균 머리|평균 최장|평균 총길이|
|---|---|---|---|---|
|0|9321|3.68|7.76|16.99|
|10|9321|7.18|3.92|18.09|
|25|9297|9.16|3.81|22.67|
|50|9116|12.97|3.99|32.24|
|100|8434|19.90|4.15|49.84|
|150|7689|24.25|4.56|63.37|
|250|6367|29.78|5.74|82.12|
|350|5534|25.60|11.71|87.88|
|450|5047|13.78|23.77|86.60|
|499|4873|9.62|29.16|87.55|

[사실] 본선에서 관측한 빠른 자연 재생 칸의 부분집합: 자연 진주 섭취 뒤 재생 간격≤12를 두 번 이상 보고, 간격 중앙값≤12인 칸만 사용했다. 판 전체를 읽은 사후 정보이며 모든 샘의 정답 표가 아니다. 해당 칸이 식별된 경기 N=20, 작은 조각 위치 N=38153, 거리≤3 N=5469, 8 초과를 9로 자른 평균 거리 7.19. death drop은 자연 진주 origin과 구분해 제외했다.

[사실] 길이 차례 분포 N=71,446,629: {'2': 38918565, '3-4': 25844994, '5-7': 3795885, '8+': 2887185}. 분열 N=2,181,060, 시점 {'0-49': 207054, '50-149': 556501, '150-349': 1046971, '350-500': 370534}. 부모+새끼 형태 상위 6개 [('2+2', 1537981), ('2+3', 180334), ('2+4', 115805), ('3+2', 86170), ('4+2', 41754), ('2+5', 40415)].
[사실] L≤4 조각의 5라운드마다 자기 turnStart 위치 N=12,962,028: 왕 거리>5 11742362, 적 머리가 7×7에 있음 4100560, 샘 거리≤3 3541714. 거리 평균은 8 초과를 9로 자른 값: 왕 8.24, 적 8.05, 샘 6.23. 샘은 지도를 구분할 수 있는 판만 기존 지도 타일로 읽은 연구 정보다. custom 집단의 기존 표 기반 샘 값 0/거리9는 미관측 대체값이므로 실제 샘에서 멀다는 증거가 아니다. 위 경험적 재생 칸 통계와 구분한다.
[사실] 사망 원인 N=2,168,915: {'W': 512755, 'H': 514529, 'O': 202426, 'S': 441386, 'A': 497819}. 최종 최장 N=9321, 평균 15.29, 중앙값 7, 최종 생존 경기 N=4871.

### sprint_custom/winner

|r|N 도달 경기|평균 머리|평균 최장|평균 총길이|
|---|---|---|---|---|
|0|511|4.57|4.14|14.00|
|10|511|6.57|2.97|15.37|
|25|509|9.40|3.38|22.71|
|50|503|16.91|3.61|41.23|
|100|481|32.58|4.89|86.14|
|150|437|42.28|6.67|126.05|
|250|387|49.37|10.24|172.09|
|350|355|43.78|20.39|180.79|
|450|338|24.97|40.77|176.90|
|499|323|17.87|51.14|182.05|

[사실] 본선에서 관측한 빠른 자연 재생 칸의 부분집합: 자연 진주 섭취 뒤 재생 간격≤12를 두 번 이상 보고, 간격 중앙값≤12인 칸만 사용했다. 판 전체를 읽은 사후 정보이며 모든 샘의 정답 표가 아니다. 해당 칸이 식별된 경기 N=490, 작은 조각 위치 N=1179071, 거리≤3 N=186750, 8 초과를 9로 자른 평균 거리 7.04. death drop은 자연 진주 origin과 구분해 제외했다.

[사실] 길이 차례 분포 N=7,073,868: {'2': 3359573, '3-4': 2561004, '5-7': 610132, '8+': 543159}. 분열 N=155,813, 시점 {'0-49': 9809, '50-149': 37344, '150-349': 77852, '350-500': 30808}. 부모+새끼 형태 상위 6개 [('2+2', 100358), ('2+3', 16606), ('2+4', 8016), ('3+2', 7373), ('2+5', 3719), ('4+2', 2752)].
[사실] L≤4 조각의 5라운드마다 자기 turnStart 위치 N=1,183,784: 왕 거리>5 1120642, 적 머리가 7×7에 있음 199863, 샘 거리≤3 0. 거리 평균은 8 초과를 9로 자른 값: 왕 8.57, 적 8.07, 샘 9.00. 샘은 지도를 구분할 수 있는 판만 기존 지도 타일로 읽은 연구 정보다. custom 집단의 기존 표 기반 샘 값 0/거리9는 미관측 대체값이므로 실제 샘에서 멀다는 증거가 아니다. 위 경험적 재생 칸 통계와 구분한다.
[사실] 사망 원인 N=146,727: {'A': 35731, 'H': 31599, 'W': 27541, 'O': 10660, 'S': 41196}. 최종 최장 N=511, 평균 36.71, 중앙값 37, 최종 생존 경기 N=511.

### sprint_custom/loser

|r|N 도달 경기|평균 머리|평균 최장|평균 총길이|
|---|---|---|---|---|
|0|511|4.57|4.14|14.00|
|10|511|6.24|3.05|14.85|
|25|509|8.04|3.41|19.66|
|50|503|12.32|3.58|30.56|
|100|481|20.40|4.23|52.06|
|150|437|26.13|4.80|69.36|
|250|387|31.83|6.03|91.09|
|350|355|29.21|10.38|97.59|
|450|338|15.34|19.99|89.56|
|499|323|12.88|23.89|94.96|

[사실] 본선에서 관측한 빠른 자연 재생 칸의 부분집합: 자연 진주 섭취 뒤 재생 간격≤12를 두 번 이상 보고, 간격 중앙값≤12인 칸만 사용했다. 판 전체를 읽은 사후 정보이며 모든 샘의 정답 표가 아니다. 해당 칸이 식별된 경기 N=490, 작은 조각 위치 N=824386, 거리≤3 N=123489, 8 초과를 9로 자른 평균 거리 7.13. death drop은 자연 진주 origin과 구분해 제외했다.

[사실] 길이 차례 분포 N=4,613,467: {'2': 2459648, '3-4': 1666375, '5-7': 268131, '8+': 219313}. 분열 N=94,575, 시점 {'50-149': 22342, '150-349': 48216, '0-49': 6525, '350-500': 17492}. 부모+새끼 형태 상위 6개 [('2+2', 68136), ('2+3', 7835), ('3+2', 3948), ('2+4', 3730), ('2+5', 1627), ('4+2', 1241)].
[사실] L≤4 조각의 5라운드마다 자기 turnStart 위치 N=825,539: 왕 거리>5 753003, 적 머리가 7×7에 있음 205677, 샘 거리≤3 0. 거리 평균은 8 초과를 9로 자른 값: 왕 8.30, 적 7.62, 샘 9.00. 샘은 지도를 구분할 수 있는 판만 기존 지도 타일로 읽은 연구 정보다. custom 집단의 기존 표 기반 샘 값 0/거리9는 미관측 대체값이므로 실제 샘에서 멀다는 증거가 아니다. 위 경험적 재생 칸 통계와 구분한다.
[사실] 사망 원인 N=92,779: {'W': 20890, 'O': 6664, 'H': 31207, 'S': 20609, 'A': 13409}. 최종 최장 N=511, 평균 15.16, 중앙값 9, 최종 생존 경기 N=323.

### 기준선에서 다른 점 (지도 구성 통제 전)

[사실] r25 머릿수 UnderTheC 7.84 (N=186) / 상위 승자 9.59 (N=11816); 최장 3.30/3.98.
[사실] r50 머릿수 UnderTheC 11.86 (N=183) / 상위 승자 15.43 (N=11574); 최장 3.64/4.17.
[사실] r100 머릿수 UnderTheC 19.02 (N=175) / 상위 승자 27.28 (N=10732); 최장 3.83/4.50.
[사실] r250 머릿수 UnderTheC 30.20 (N=137) / 상위 승자 43.35 (N=7816); 최장 3.98/7.69.
[사실] r350 머릿수 UnderTheC 21.64 (N=108) / 상위 승자 36.74 (N=6686); 최장 11.69/17.99.
[사실] 작은 조각 farKing: UnderTheC 237551/261558=90.8% / 상위 승자 20756502/22379852=92.7%.
[사실] 작은 조각 visibleEnemy: UnderTheC 67950/261558=26.0% / 상위 승자 5260654/22379852=23.5%.
[사실] 작은 조각 nearFountain: UnderTheC 53995/261558=20.6% / 상위 승자 4577436/22379852=20.5%.

[해석] 이 차이는 아는 지도 분포·상대 강도·승패 구성이 함께 다른 기준선이다. 처음 보는 지도를 분석하는 능력의 차이라고 해석하지 않는다.

### 본선에서 상위권과 다른 점: 승패를 나눠 비교

|집단|N 경기|r50 머리|최종 최장 평균|분열/경기|N 정면|능동|적 몸 피살|아군 몸 피살|
|---|---|---|---|---|---|---|---|---|
|custom/winner|511|16.91 (N=503)|36.71|304.92|28469|15648|583|10077|
|custom/loser|511|12.32 (N=503)|15.16|185.08|28469|12821|839|5825|
|ours/custom/winner|3|6.00 (N=3)|34.00|128.00|72|64|5|49|
|ours/custom/loser|4|7.75 (N=4)|7.00|51.50|36|29|6|87|
|under/custom/winner|8|19.12 (N=8)|41.50|507.50|480|264|0|16|
|under/custom/loser|6|9.50 (N=6)|18.67|244.00|115|61|1|1|

[사실] UnderTheC 본선 N=14판의 L≤4 위치 N=34,306: 왕 거리>5는 32,035(93.4%), 적 머리가 시야에 있음 3,948(11.5%), 경험적 빠른 자연 재생 칸 거리≤3은 6,728(19.6%). 맞춤 지도 승자 기준은 각각 1,120,642/1,183,784(94.7%), 199,863/1,183,784(16.9%), 186,750/1,179,071(15.8%). 왕에서 떨어져 있는 것만은 특이하지 않고, 적을 덜 보며 재생 칸에 더 자주 가까운 차이가 보인다. 같은 조각의 반복 관측이고 지도·승패 분포를 통제하지 않은 위치 통계다.

[사실] UnderTheC 본선 사망 N=5,465: No Valid Action(A) 4,637(84.8%), 정면809, 몸18(적1/아군17), 켈프1, 자기 몸0. A의 로컬 ledger 조작적 세부는 trap 2,353/sac 2,284, fault 0/sprintDeath 0이다. trap은 유효 이웃 없음, sac은 유효 이웃은 있지만 행동이 없었음을 뜻한다. 의도적 정리·시간 초과·프로그램 오류 중 무엇인지는 이 태그만으로 확정하지 않는다. 질주 길이 부족 사망으로 세면 틀린다.

[사실] UnderTheC 맞춤 지도 실제 적 몸 죽임 N=4, 고립 죽임 N=1(806958 r329 켈프 연관)이다. 806885 r349–351의 L2 id873은 E→E→E로 몸을 남겼고 적 id885는 S→W→N(출구0)으로 충돌했다. 다른 대표 806887 r160과 806959 r132는 상대가 출구0에서 split한 뒤 부모가 죽은 근접 사건이다. 실제 몸 죽임4와 근접 켈프/자기 사망 연관은 별도 분모다.

[해석] UnderTheC는 이 본선에서 평지의 단독 절단을 많이 기록한 팀이라고 말하기 어렵다(N=4). 짧은 조각을 많이 만들고, 켈프·몸 충돌은 드물게 남기며, 왕과 떨어진 재생 칸 주변에 조각을 두고, 작은 조각의 교체가 많은 형태가 더 두드러진다. 정찰보다는 분산 수확·교환의 후보 해석도 맞지만, 통신/목표 의도가 보이지 않아 역할과 승리 기여는 미확인이다. 최종 승자만으로 비교하지 않도록 위 표를 승패별로 나눴으며 동일 상황의 대조 실험은 아니다.
[사실] under_bracket/kill, 분류 N=1, 선택 N=1: 게임 806958 r329 ([세 결정](../../exp/duel/reads/under_bracket-kill-1.md), [시야 그림](../../exp/duel/boards/under_bracket-kill-1-micro.png)).
[사실] under_bracket/trade_mover, 분류 N=8, 선택 N=3: 게임 806890 r175 ([세 결정](../../exp/duel/reads/under_bracket-trade_mover-1.md), [시야 그림](../../exp/duel/boards/under_bracket-trade_mover-1-micro.png)); 게임 806957 r55 ([세 결정](../../exp/duel/reads/under_bracket-trade_mover-2.md), [시야 그림](../../exp/duel/boards/under_bracket-trade_mover-2-micro.png)); 게임 806885 r284 ([세 결정](../../exp/duel/reads/under_bracket-trade_mover-3.md), [시야 그림](../../exp/duel/boards/under_bracket-trade_mover-3-micro.png)).
[사실] under_bracket/trade_passive, 분류 N=9, 선택 N=3: 게임 806955 r169 ([세 결정](../../exp/duel/reads/under_bracket-trade_passive-1.md), [시야 그림](../../exp/duel/boards/under_bracket-trade_passive-1-micro.png)); 게임 806959 r355 ([세 결정](../../exp/duel/reads/under_bracket-trade_passive-2.md), [시야 그림](../../exp/duel/boards/under_bracket-trade_passive-2-micro.png)); 게임 806954 r281 ([세 결정](../../exp/duel/reads/under_bracket-trade_passive-3.md), [시야 그림](../../exp/duel/boards/under_bracket-trade_passive-3-micro.png)).
[사실] under_bracket_contacts/kill, 분류 N=27, 선택 N=3: 게임 806887 r160 ([세 결정](../../exp/duel/reads/under_bracket_contacts-kill-1.md), [시야 그림](../../exp/duel/boards/under_bracket_contacts-kill-1-micro.png)); 게임 806959 r132 ([세 결정](../../exp/duel/reads/under_bracket_contacts-kill-2.md), [시야 그림](../../exp/duel/boards/under_bracket_contacts-kill-2-micro.png)); 게임 806885 r351 ([세 결정](../../exp/duel/reads/under_bracket_contacts-kill-3.md), [시야 그림](../../exp/duel/boards/under_bracket_contacts-kill-3-micro.png)).
[사실] under_bracket_contacts/killed, 분류 N=2, 선택 N=2: 게임 806955 r275 ([세 결정](../../exp/duel/reads/under_bracket_contacts-killed-1.md), [시야 그림](../../exp/duel/boards/under_bracket_contacts-killed-1-micro.png)); 게임 806959 r256 ([세 결정](../../exp/duel/reads/under_bracket_contacts-killed-2.md), [시야 그림](../../exp/duel/boards/under_bracket_contacts-killed-2-micro.png)).

[해석] 왕에서 멀고 적을 자주 보는 조각은 정찰 역할의 후보 조건이다. 몸 위치만으로는 적 관측의 보고, 분열 목표, sonar 내용, 의도된 역할을 알 수 없다. 샘 접근과 먹이 경쟁도 같은 위치를 만들 수 있으므로 ‘관측자’라고 확정하지 않는다. 본선 맞춤 지도에서 같은 위치 조건이 나타나는지도 별도 N으로 비교한다. 움직임과 사망 흔적만으로 정찰의 효과를 확정하지 않는다.

## 8. 독립 재집계와 재현

[사실] 본선 능동접촉의 사전 시야 수 균형과 TRADE 태그도 별도 Python 스트림으로 재집계했다: 우리 정면접촉 주/독립 108/108, 능동 93/93; UnderTheC 정면 595/595, 능동 325/325. 8개 집단의 조건 셀 불일치 0이며 verification-custom.json에 두 수를 함께 남겼다.

[사실] 에피소드 전수 재구성: 주 코드 11,662,901, 별도 dragonUpdate 코드 11,662,901, 대조 게임 N=24,942, 불일치 게임 0. 집계 코드 독립 재계산: 주 표 11,662,901, Python gzip 스트림 11,662,901, 불일치 0.

|항목|주 코드|원사건 독립 코드|
|---|---|---|
|deaths|11777908|11777908|
|headDeaths|2558014|2558014|
|enemyContacts|1065327|1065327|
|splits|12311779|12311779|
|indSelected|224|224|
|indSelectedTrade|224|224|

[사실] 직접 사망 상대 id의 원자료 독립 대조: 머리 교환 주/독립 1,065,327/1,065,327, 적 몸 피살 주/독립 46,524/46,524. 수뿐 아니라 각 게임의 (round, victim, killer)도 전부 대조했다.

[사실] 직접 충돌/근접 사망 집계도 독립 재계산했다: 주 코드 1,146,139 / Python 1,146,139. 집단별 실제 몸으로 죽임·몸 피살·머리 교환·근접 벽/자기 사망은 verification.json에 두 수를 함께 남겼다.

[사실] 엔진 시뮬레이션·최종 상태·질량 검증 합: {'sim': 0, 'splits': 0, 'drops': 0, 'eatTC': 0, 'ledger': 0, 'final': 0, 'lineage': 0, 'natBal': 0, 'dropBal': 0, 'unknownDeath': 0, 'ind_deaths': 0, 'ind_headDeaths': 0, 'ind_enemyContacts': 0, 'ind_splits': 0, 'ind_indSelected': 0, 'ind_indSelectedTrade': 0}. 직접 적 몸 충돌·머리 교환의 상대 id도 별도 dragonUpdate 코드로 매 경기 대조했다. 둘 다 같은 조작적 정의를 쓰므로 정의의 적절성을 검증한 것은 아니다. 재구성/집계 오류를 서로 다른 경로로 검사했다.

[사실] 전체 목록 population.json, 표 tables.json, strict 조기 표 tables-strict.json, 에피소드 episodes.jsonl.gz, 원기보 대조 verification-raw.json, 독립 표 verification.json, 유형 classes.json, 판면 boards/에 있다. CPU 정책 효과·7×7 구현 가능성의 실제 적용 결과 N=0.

## 9. 일반 규칙 후보 — 모두 가설

[해석] 아래 N은 행동 근거의 기술 통계 분모이며, 규칙을 적용한 게임 N은 전부 0이다. 근접할 때만 현재 7×7과 자기 길이·id·이동 이력으로 발동한다. d8 전체 상태나 고정 지도 표를 구현 입력으로 요구하지 않는다. 적 길이는 현재 보이는 몸만으로 하한만 알 수 있으므로 길이 비교가 불확실하면 교환 보너스를 억제한다. id 순서는 한 라운드 동안 더 높은 id가 아직 움직이지 않았음을 이용하고, 다음 자기 차례까지는 낮은 id도 다음 라운드에서 한 번 움직인다는 것을 포함한다.

|규칙|근거 N|7×7+자기 상태 발동|예상 기제 효과 (미검증)|기존 항/크기 가설|
|---|---|---|---|---|
|가설: 현행 무료 질주와 후속 몸을 맞추기|재구성 보정 N=411판; 영향받은 우리 온라인 N=0|자기 시작 길이로 free=ceil(L/4)를 고정하고, 비용과 후속 꼬리 제거량을 max(0,steps−free)로 계산한다. 현재 제출 환경의 규칙을 확인한 뒤 후보를 생성한다.|무료 이동의 과도한 비용 평가와 잘못된 후속 몸 예측을 줄임. 실제 봇 적용 N=0.|SPRINT_COST=1.6 유지, 유료 걸음 수에만 곱함. L5의 2걸음은 기존보다 +1.6, L9의 3걸음 +3.2, L13의 4걸음 +4.8.|
|가설: 첫걸음의 다음 차례 도달 위험|우리 정면접촉 N=13483, 수동 N=11115; 상위 승자 접촉 N=534426|보이는 적 머리의 합법적인 관측창 안의 경로와 질주 소모를 현재 몸으로 계산한다. 더 높은 id의 이번 라운드 행동과 낮은 id의 다음 라운드 행동을 구별한다. 안전한 다른 끝칸이 있으면 위험 칸을 낮춘다.|능동 머리 절단/질주 들이받힘을 줄임. 대안이 없는 경우는 별도 기록.|T1/T2 첫걸음만: 할인된 −4.8을 위험 조건에서 −24 정도로 복원(차 −19.2), 인접 −30 유지. DFS 전체에 반복하지 않음.|
|가설: 끊기는 새 몸이 유지될 때만|상위 승자 끊기 시도 ep N=1546|현재 보이는 상대의 마지막 출구/좁은 진로를 줄이고, 적 차례까지 그 몸이 꼬리로 사라지지 않으며 자기 후속 출구가 있는 경로만 컷 후보로 기록. 진행 방향 하나만 막는 보너스는 채택하지 않음.|한 턴의 몸 장벽이 실제 적 경로를 막는지 확인.|새 첫걸음 cut 후보 +3..+6 가설. 진주 +1, sprint −1.6/추가 걸음과 비교; T1·공간 사망 벌점은 유지.|
|가설: 질주 끊기 비용과 탈출 관문|상위 승자 질주 끊기 시도 ep N=440|질주 후 최소 길이 2와 자기 몸 뒤 빈출구를 확인한다. 진주를 먹을 것이라는 가정 없이 먼저 비용을 지불할 수 있어야 한다.|적 몸 충돌 유도 뒤 자기 oversprint/갇힘을 억제.|SPRINT_COST=1.6 기본 유지; 안전 컷의 작은 보너스 +3..+6만, 공간 부족 AREA_TRAP≈−60 우회 금지.|
|가설: 켈프·자기/아군 몸에서 출구 보존|우리 본선 사망594: 켈프252/자기79/아군 몸136; escape-split 깊은읽기 N=3|7×7 첫걸음 뒤 공간과 다음 출구를 계산하며 자기·아군 몸도 막힘으로 넣는다. split 후보는 부모와 새끼의 차례 순서별 출구를 확인한다. 관측 밖을 출구로 확정하지 않는다.|벽 몰기·감기 후보가 완성되기 전에 빠져나옴.|first-step 공간 1→2 회복에 +6..+12 가설. AREA_TRAP60/FILL3/DEADEND8의 적용 관계를 분리해 진단.|
|가설: 보이는 수 균형으로 교환을 허용|상위 승자 trade ep N=10764, 우리 trade N=598|긴 자기 왕을 보존하고, 보이는 수가 열세이면 같은 길이 교환을 억제한다. 짧은 조각·아군 지역 우세·명확한 적 길이의 경우에만 능동 교환을 시험한다.|왕의 손실을 억제하고 교환 허용 이유를 명확히 기록. 우리 본선은 이미 능동93/108이므로 일괄 공격성 증가 근거는 없음.|tradeValue W_KILL=4 기본; 같은 길이 우세 창에 +6..+12 terminal 가설. LNT veto와 왕 관문을 명시적으로 유지·시험.|
|가설: 위험한 진주 추격을 사건으로 기억|상위 승자 pearl_bait 시도 ep N=6628|먹은 뒤 적 도달 칸에 머리를 남기는 후보, 사망 진주 줄을 쫓으며 켈프 출구가 줄어드는 후보를 따로 표시한다. 머리 교환 가치·다음 출구를 같이 비교.|진주 추격 노출과 몸에 막힌 길의 반복 진입을 줄임.|확실한 진주 +1은 유지; 위험도는 첫걸음 T2/space로 −6..−24 조건부 가설. 진주 전체에 일괄 벌점 부여할 근거 없음.|
