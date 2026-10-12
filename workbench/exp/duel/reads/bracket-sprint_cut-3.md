# bracket/sprint_cut: 806774:156:160:177

[사실] 분류 N=9; 해당 특징의 중심에 가까운 사례 3. 점수 1.372.
게임 806774, Maze/?, r177–179; 결과 kill; id 156 / 160.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806772/806774.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806772/806774.replay.gz' 'Maze' '?' 'A' '176,177,178,179,180'

시작: {"156":{"id":156,"team":"A","len":3,"budget":1,"head":[33,13],"free":1,"wall":0,"pearls":0,"visiblePearls":4,"ally8":1,"enemy8":1,"visibleAlly":0,"visibleEnemy":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":11,"firstInRound":true},"160":{"id":160,"team":"B","len":3,"budget":1,"head":[14,17],"free":1,"wall":0,"pearls":0,"visiblePearls":5,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":9,"firstInRound":false}}
사망 상세: {"dead":160,"killer":156,"reason":"O","pattern":"sprint_cut","flags":{"cut_off":true,"sprint_cut":true,"wall_pin":true,"coil":false,"pearl_bait":false},"hitTile":704,"blockerAge":0,"lastKillerAction":{"r":179,"seq":19069,"id":156,"team":"A","len":3,"head":[32,13],"after":[33,14],"action":{"kind":"move","steps":["S","E"]},"tag":"","free":2,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":0,"visibleEnemy":1,"eaten":0,"fate":null,"path":[704,705],"exposed":false},"victimPre":{"id":160,"team":"B","len":3,"budget":1,"head":[31,14],"free":0,"wall":0,"pearls":0,"visiblePearls":4,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|177|156/A|3|33,12→33,13|1|0/1|S|0||
|177|160/B|3|15,17→14,17|1|0/0|W|0||
|178|156/A|3|33,13→32,13|1|0/0|W|0||
|178|160/B|3|14,17→31,14|1|0/2|S|0||
|179|156/A|3|32,13→33,14|2|0/1|SE|0||
|179|160/B|3|31,14→31,14|0|0/1|E|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
