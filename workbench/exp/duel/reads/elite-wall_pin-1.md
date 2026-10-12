# elite/wall_pin: 659225:231:363:211

[사실] 분류 N=175; 해당 특징의 중심에 가까운 사례 1. 점수 1.007.
게임 659225, Schooltime/a, r211–214; 결과 kill; id 363 / 231.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/top/659225/659225.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/top/659225/659225.replay.gz' 'Schooltime' 'a' 'A' '211,212,213,214,215'

시작: {"231":{"id":231,"team":"B","len":4,"budget":2,"head":[15,10],"free":2,"wall":1,"pearls":1,"visiblePearls":1,"ally8":0,"enemy8":2,"visibleAlly":1,"visibleEnemy":2,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0},"space":10,"firstInRound":true},"363":{"id":363,"team":"A","len":8,"budget":6,"head":[18,9],"free":1,"wall":0,"pearls":0,"visiblePearls":1,"ally8":0,"enemy8":1,"visibleAlly":2,"visibleEnemy":1,"blocked":{"wall":1,"self":2,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":7,"firstInRound":false}}
사망 상세: {"dead":231,"killer":363,"reason":"W","pattern":"wall_pin","flags":{"wall_pin":true,"coil":true,"pearl_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":213,"seq":35133,"id":363,"team":"A","len":8,"head":[18,8],"after":[16,9],"action":{"kind":"move","steps":["W","W","S"]},"tag":"","free":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":2,"visibleEnemy":1,"eaten":1,"fate":null,"path":[497,496,556],"exposed":false},"victimPre":{"id":231,"team":"B","len":6,"budget":4,"head":[15,8],"free":0,"wall":0,"pearls":0,"visiblePearls":0,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":3,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|211|363/A|8|19,9→18,9|1|3/0|W|0||
|212|231/B|4|15,10→15,9|2|1/3|N|1||
|212|363/A|8|18,9→18,8|1|2/1|N|0||
|213|231/B|5|15,9→15,8|3|1/2|N|1||
|213|363/A|8|18,8→16,9|1|2/1|WWS|1||
|214|231/B|6|15,8→15,8|0|0/3|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
