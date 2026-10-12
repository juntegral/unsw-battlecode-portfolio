# ours/killed: 687755:347:377:280

[사실] 분류 N=53; 해당 특징의 중심에 가까운 사례 2. 점수 0.899.
게임 687755, Schooltime/a, r280–282; 결과 kill; id 377 / 347.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-stack6-online-r2/M687755.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-stack6-online-r2/M687755.replay' 'Schooltime' 'a' 'B' '279,280,281,282,283'

시작: {"347":{"id":347,"team":"B","len":8,"budget":6,"head":[39,14],"free":1,"wall":0,"pearls":1,"visiblePearls":1,"ally8":0,"enemy8":1,"visibleAlly":1,"visibleEnemy":3,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":6,"firstInRound":true},"377":{"id":377,"team":"A","len":7,"budget":5,"head":[43,14],"free":1,"wall":0,"pearls":0,"visiblePearls":4,"ally8":1,"enemy8":2,"visibleAlly":2,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":6,"firstInRound":false}}
사망 상세: {"dead":377,"killer":347,"reason":"W","pattern":"wall_pin","flags":{"wall_pin":true,"coil":true,"pearl_bait":false},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":282,"seq":41245,"id":347,"team":"B","len":8,"head":[40,14],"after":[42,15],"action":{"kind":"move","steps":["E","E","S"]},"tag":"","free":2,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":2,"visibleEnemy":2,"eaten":1,"fate":null,"path":[881,882,942],"exposed":false},"victimPre":{"id":377,"team":"A","len":2,"budget":0,"head":[43,14],"free":0,"wall":0,"pearls":0,"visiblePearls":5,"ally8":1,"enemy8":1,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|280|347/B|8|39,15→39,14|2|1/3|N|0||
|280|377/A|7|43,15→43,14|2|2/2|N|0|N v7.0 d7 L7|
|281|347/B|8|39,14→40,14|1|1/1|E|0||
|281|377/A|7|43,14→43,14|1|0/2|split|0|escape-split5 L7|
|282|347/B|8|40,14→42,15|2|2/2|EES|1||
|282|377/A|2|43,14→43,14|0|0/2|N|0|no-exit|

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
