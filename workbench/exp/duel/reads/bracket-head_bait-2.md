# bracket/head_bait: 806927:793:868:381

[사실] 분류 N=1070; 해당 특징의 중심에 가까운 사례 2. 점수 0.532.
게임 806927, Islands/?, r381–384; 결과 trade; id 793 / 868.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806926/806927.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806926/806927.replay.gz' 'Islands' '?' 'A' '381,382,383,384,385'

시작: {"793":{"id":793,"team":"A","len":3,"budget":1,"head":[43,9],"free":1,"wall":1,"pearls":0,"visiblePearls":1,"ally8":2,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":0,"self":1,"allyBody":2,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":20,"firstInRound":true},"868":{"id":868,"team":"B","len":5,"budget":3,"head":[46,10],"free":2,"wall":1,"pearls":0,"visiblePearls":1,"ally8":2,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0},"space":28,"firstInRound":false}}
사망 상세: {"dead":868,"partner":793,"mover":793,"steps":2,"flags":{"wall_pin":false,"coil":false,"pearl_bait":false,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":384,"seq":77852,"id":793,"team":"A","len":3,"head":[44,10],"after":[44,11],"action":{"kind":"move","steps":["S","E"]},"tag":"","free":2,"blocked":{"wall":0,"self":1,"allyBody":1,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":0,"visibleEnemy":1,"eaten":0,"fate":{"reason":"H","step":1,"hit":868,"hitTeam":"B","hitLen":5},"path":[660],"exposed":false},"victimPre":{"id":868,"team":"B","len":5,"budget":3,"head":[46,11],"free":1,"wall":0,"pearls":0,"visiblePearls":0,"ally8":1,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|381|868/B|5|47,10→46,10|1|0/1|W|0||
|382|793/A|3|43,9→43,10|1|0/1|S|0||
|382|868/B|5|46,10→46,11|2|0/1|S|0||
|383|793/A|3|43,10→44,10|2|0/1|E|0||
|383|868/B|5|46,11→45,11|1|0/1|W|0||
|384|793/A|3|44,10→44,11|2|0/1|SE|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
