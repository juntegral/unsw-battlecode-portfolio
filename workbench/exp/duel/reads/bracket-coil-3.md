# bracket/coil: 806872:524:681:429

[사실] 분류 N=385; 해당 특징의 중심에 가까운 사례 3. 점수 0.697.
게임 806872, Maze/?, r429–431; 결과 trade; id 681 / 524.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806870/806872.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806870/806872.replay.gz' 'Maze' '?' 'A' '428,429,430,431,432'

시작: {"524":{"id":524,"team":"B","len":6,"budget":4,"head":[15,0],"free":2,"wall":0,"pearls":1,"visiblePearls":9,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":5,"firstInRound":true},"681":{"id":681,"team":"A","len":3,"budget":1,"head":[13,0],"free":1,"wall":0,"pearls":0,"visiblePearls":7,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":5,"firstInRound":false}}
사망 상세: {"dead":524,"partner":681,"mover":681,"steps":1,"flags":{"wall_pin":false,"coil":true,"pearl_bait":false,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":431,"seq":53042,"id":681,"team":"A","len":3,"head":[13,1],"after":[13,1],"action":{"kind":"move","steps":["E"]},"tag":"","free":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":1,"visibleEnemy":1,"eaten":0,"fate":{"reason":"H","step":0,"hit":524,"hitTeam":"B","hitLen":6},"path":[],"exposed":false},"victimPre":{"id":524,"team":"B","len":6,"budget":4,"head":[14,0],"free":1,"wall":0,"pearls":1,"visiblePearls":10,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|429|524/B|7|16,1→15,0|1|1/2|NW|0||
|429|681/A|3|12,0→13,0|1|0/1|E|0||
|430|524/B|6|15,0→14,0|2|0/1|W|0||
|430|681/A|3|13,0→13,1|1|0/1|S|0||
|431|524/B|6|14,0→14,1|1|0/1|S|0||
|431|681/A|3|13,1→13,1|0|1/1|E|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
