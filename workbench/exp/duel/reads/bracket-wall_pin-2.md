# bracket/wall_pin: 806991:606:626:396

[사실] 분류 N=99; 해당 특징의 중심에 가까운 사례 2. 점수 0.907.
게임 806991, Maze/?, r396–398; 결과 kill; id 626 / 606.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806989/806991.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806989/806991.replay.gz' 'Maze' '?' 'B' '395,396,397,398,399'

시작: {"606":{"id":606,"team":"B","len":4,"budget":2,"head":[18,13],"free":1,"wall":0,"pearls":0,"visiblePearls":0,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":13,"firstInRound":true},"626":{"id":626,"team":"A","len":3,"budget":1,"head":[13,19],"free":1,"wall":0,"pearls":0,"visiblePearls":6,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":3,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":7,"firstInRound":false}}
사망 상세: {"dead":626,"killer":606,"reason":"W","pattern":"wall_pin","flags":{"wall_pin":true,"coil":true,"pearl_bait":false},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":398,"seq":50483,"id":606,"team":"B","len":4,"head":[18,12],"after":[17,12],"action":{"kind":"move","steps":["W"]},"tag":"","free":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":2,"visibleEnemy":1,"eaten":0,"fate":null,"path":[593],"exposed":false},"victimPre":{"id":626,"team":"A","len":3,"budget":1,"head":[19,12],"free":0,"wall":0,"pearls":0,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":3,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|396|606/B|3|19,13→18,13|1|0/0|W|1||
|396|626/A|3|13,19→13,18|1|0/3|N|0||
|397|606/B|4|18,13→18,12|1|0/0|N|0||
|397|626/A|3|13,18→19,12|1|0/2|W|0||
|398|606/B|4|18,12→17,12|1|2/1|W|0||
|398|626/A|3|19,12→19,12|0|0/3|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
