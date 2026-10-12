# bracket/sprint_cut: 806844:466:535:377

[사실] 분류 N=9; 해당 특징의 중심에 가까운 사례 2. 점수 1.220.
게임 806844, Maze/?, r377–379; 결과 kill; id 535 / 466.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806842/806844.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806842/806844.replay.gz' 'Maze' '?' 'A' '376,377,378,379,380'

시작: {"466":{"id":466,"team":"B","len":2,"budget":0,"head":[19,21],"free":2,"wall":0,"pearls":0,"visiblePearls":8,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":12,"firstInRound":true},"535":{"id":535,"team":"A","len":5,"budget":3,"head":[18,19],"free":2,"wall":0,"pearls":0,"visiblePearls":9,"ally8":0,"enemy8":1,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":15,"firstInRound":false}}
사망 상세: {"dead":466,"killer":535,"reason":"O","pattern":"sprint_cut","flags":{"cut_off":true,"sprint_cut":true,"wall_pin":true,"coil":true,"pearl_bait":true},"hitTile":978,"blockerAge":1,"lastKillerAction":{"r":378,"seq":64185,"id":535,"team":"A","len":5,"head":[18,19],"after":[19,20],"action":{"kind":"move","steps":["S","E"]},"tag":"","free":2,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":1,"visibleEnemy":1,"eaten":0,"fate":null,"path":[978,979],"exposed":false},"victimPre":{"id":466,"team":"B","len":3,"budget":1,"head":[18,21],"free":0,"wall":0,"pearls":0,"visiblePearls":10,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|376|535/A|6|15,19→16,19|1|1/0|E|0||
|377|466/B|2|20,21→19,21|2|0/1|W|0||
|377|535/A|6|16,19→18,19|1|1/1|EE|0||
|378|466/B|2|19,21→18,21|2|0/2|W|1||
|378|535/A|5|18,19→19,20|2|1/1|SE|0||
|379|466/B|3|18,21→18,21|0|0/2|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
