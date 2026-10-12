# bracket/wall_pin: 803862:221:244:285

[사실] 분류 N=99; 해당 특징의 중심에 가까운 사례 1. 점수 0.641.
게임 803862, Maze/?, r285–288; 결과 kill; id 244 / 221.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/803860/803862.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/803860/803862.replay.gz' 'Maze' '?' 'A' '285,286,287,288,289'

시작: {"221":{"id":221,"team":"B","len":4,"budget":2,"head":[24,11],"free":2,"wall":0,"pearls":0,"visiblePearls":1,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":12,"firstInRound":true},"244":{"id":244,"team":"A","len":4,"budget":2,"head":[21,12],"free":2,"wall":0,"pearls":2,"visiblePearls":1,"ally8":0,"enemy8":1,"visibleAlly":2,"visibleEnemy":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":18,"firstInRound":false}}
사망 상세: {"dead":221,"killer":244,"reason":"S","pattern":"wall_pin","flags":{"wall_pin":true,"coil":true,"pearl_bait":false},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":287,"seq":25349,"id":244,"team":"A","len":4,"head":[21,11],"after":[20,11],"action":{"kind":"move","steps":["W"]},"tag":"","free":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":0,"visibleEnemy":1,"eaten":0,"fate":null,"path":[548],"exposed":false},"victimPre":{"id":221,"team":"B","len":4,"budget":2,"head":[22,11],"free":0,"wall":0,"pearls":0,"visiblePearls":1,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|285|244/A|3|21,13→21,12|2|2/1|N|1||
|286|221/B|4|24,11→23,11|2|0/2|W|0||
|286|244/A|4|21,12→21,11|2|2/1|N|0||
|287|221/B|4|23,11→22,11|1|0/2|W|0||
|287|244/A|4|21,11→20,11|1|0/1|W|0||
|288|221/B|4|22,11→22,11|0|0/2|E|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
