# bracket/wall_pin: 805850:765:780:427

[사실] 분류 N=99; 해당 특징의 중심에 가까운 사례 3. 점수 0.917.
게임 805850, Maze/?, r427–430; 결과 kill; id 780 / 765.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/805848/805850.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/805848/805850.replay.gz' 'Maze' '?' 'A' '427,428,429,430,431'

시작: {"765":{"id":765,"team":"B","len":4,"budget":2,"head":[32,10],"free":1,"wall":0,"pearls":1,"visiblePearls":6,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":7,"firstInRound":true},"780":{"id":780,"team":"A","len":6,"budget":4,"head":[29,11],"free":2,"wall":0,"pearls":0,"visiblePearls":6,"ally8":1,"enemy8":1,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":16,"firstInRound":false}}
사망 상세: {"dead":765,"killer":780,"reason":"S","pattern":"wall_pin","flags":{"wall_pin":true,"coil":true,"pearl_bait":false},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":429,"seq":61046,"id":780,"team":"A","len":6,"head":[30,11],"after":[30,12],"action":{"kind":"move","steps":["S"]},"tag":"","free":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":1,"visibleEnemy":1,"eaten":0,"fate":null,"path":[606],"exposed":false},"victimPre":{"id":765,"team":"B","len":4,"budget":2,"head":[30,10],"free":0,"wall":0,"pearls":0,"visiblePearls":6,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|427|780/A|6|29,10→29,11|1|1/1|S|0||
|428|765/B|4|32,10→31,10|1|0/1|W|0||
|428|780/A|6|29,11→30,11|2|1/1|E|0||
|429|765/B|4|31,10→30,10|1|0/1|W|0||
|429|780/A|6|30,11→30,12|1|1/1|S|0||
|430|765/B|4|30,10→30,10|0|0/1|E|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
