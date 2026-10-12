# ours_contacts/killed: 730074:contact:43

[사실] 분류 N=1141; 해당 특징의 중심에 가까운 사례 3. 점수 0.661.
게임 730074, Slithery Fight/b, r425–425; 결과 kill; id 1097 / 1135.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/bench-s11-1/M730074.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/bench-s11-1/M730074.replay' 'Slithery Fight' 'b' 'B' '422,423,424,425,426'

시작: {"1097":{"r":425,"seq":71216,"id":1097,"team":"A","len":2,"head":[28,4],"after":[28,4],"action":{"kind":"move","steps":["W"]},"tag":"no-exit","free":0,"wall":1,"self":1,"allyBody":0,"enemyBody":1,"allyHead":1,"enemyHead":0,"visibleAlly":2,"visibleEnemy":1,"eaten":0,"path":[]},"1135":{"r":424,"seq":71086,"id":1135,"team":"B","len":6,"head":[25,3],"after":[25,2],"action":{"kind":"move","steps":["N"]},"tag":"","free":2,"wall":0,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0,"visibleAlly":0,"visibleEnemy":3,"eaten":0,"path":[151]}}
사망 상세: {"dead":1097,"killer":1135,"pattern":"coil"}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|422|1135/B|6|26,4→26,3|2|0/2|N|0||
|423|1097/A|6|29,4→28,4|1|1/1|W|0|W v-3.2 d7 L6 g7|
|423|1135/B|6|26,3→25,3|1|0/3|W|0||
|424|1097/A|6|28,4→28,4|0|1/1|split|0|escape-split4 L6|
|424|1135/B|6|25,3→25,2|2|0/3|N|0||
|425|1097/A|2|28,4→28,4|0|2/1|W|0|no-exit|

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
