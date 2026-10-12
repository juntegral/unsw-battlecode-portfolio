# ours/trade_mover: 666235:55:170:166

[사실] 분류 N=187; 해당 특징의 중심에 가까운 사례 2. 점수 1.094.
게임 666235, Devil/a, r166–168; 결과 trade; id 170 / 55.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-stack3-online/M666235.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-stack3-online/M666235.replay' 'Devil' 'a' 'A' '165,166,167,168,169'

시작: {"55":{"id":55,"team":"B","len":8,"budget":6,"head":[26,0],"free":1,"wall":0,"pearls":1,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":4,"firstInRound":true},"170":{"id":170,"team":"A","len":3,"budget":1,"head":[26,12],"free":1,"wall":0,"pearls":1,"visiblePearls":2,"ally8":0,"enemy8":2,"visibleAlly":0,"visibleEnemy":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":4,"firstInRound":false}}
사망 상세: {"dead":55,"partner":170,"mover":170,"steps":1,"flags":{"wall_pin":false,"coil":true,"pearl_bait":true,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":168,"seq":10158,"id":170,"team":"A","len":3,"head":[26,14],"after":[26,14],"action":{"kind":"move","steps":["S"]},"tag":"last-trade","free":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":0,"visibleEnemy":1,"eaten":0,"fate":{"reason":"H","step":0,"hit":55,"hitTeam":"B","hitLen":3},"path":[],"exposed":false},"victimPre":{"id":55,"team":"B","len":2,"budget":0,"head":[26,0],"free":1,"wall":0,"pearls":1,"visiblePearls":3,"ally8":1,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|166|55/B|7|26,1→26,0|1|0/0|N|1||
|166|170/A|3|26,12→26,13|1|0/0|S|0|S v4.4 d7 L3|
|167|55/B|8|26,0→26,0|1|0/1|split|0||
|167|170/A|3|26,13→26,14|1|0/1|S|0|S v-1044.7 d7 L3|
|168|55/B|2|26,0→26,15|1|0/1|N|1||
|168|170/A|3|26,14→26,14|0|0/1|S|0|last-trade|

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
