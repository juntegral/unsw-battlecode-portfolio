# bracket/cut_off: 806844:297:388:298

[사실] 분류 N=47; 해당 특징의 중심에 가까운 사례 3. 점수 0.887.
게임 806844, Maze/?, r298–301; 결과 kill; id 297 / 388.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806842/806844.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806842/806844.replay.gz' 'Maze' '?' 'A' '298,299,300,301,302'

시작: {"297":{"id":297,"team":"A","len":3,"budget":1,"head":[26,9],"free":1,"wall":0,"pearls":0,"visiblePearls":0,"ally8":1,"enemy8":1,"visibleAlly":3,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":10,"firstInRound":true},"388":{"id":388,"team":"B","len":3,"budget":1,"head":[29,10],"free":1,"wall":0,"pearls":0,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":6,"firstInRound":false}}
사망 상세: {"dead":388,"killer":297,"reason":"O","pattern":"cut_off","flags":{"cut_off":true,"sprint_cut":false,"wall_pin":false,"coil":true,"pearl_bait":false},"hitTile":459,"blockerAge":1,"lastKillerAction":{"r":301,"seq":48807,"id":297,"team":"A","len":3,"head":[28,9],"after":[28,8],"action":{"kind":"move","steps":["N"]},"tag":"","free":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":0,"visibleEnemy":1,"eaten":0,"fate":null,"path":[412],"exposed":false},"victimPre":{"id":388,"team":"B","len":3,"budget":1,"head":[27,10],"free":0,"wall":0,"pearls":0,"visiblePearls":1,"ally8":0,"enemy8":2,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|299|297/A|3|26,9→27,9|1|3/1|E|0||
|299|388/B|3|29,10→28,10|1|0/1|W|0||
|300|297/A|3|27,9→28,9|2|2/1|E|0||
|300|388/B|3|28,10→27,10|1|0/1|W|0||
|301|297/A|3|28,9→28,8|1|0/1|N|0||
|301|388/B|3|27,10→27,10|0|1/1|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
