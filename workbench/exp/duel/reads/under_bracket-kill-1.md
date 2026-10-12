# under_bracket/kill: 806958:89:104:327

[사실] 분류 N=1; 해당 특징의 중심에 가까운 사례 1. 점수 0.000.
게임 806958, Tower Defense/?, r327–329; 결과 kill; id 104 / 89.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806954/806958.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806954/806958.replay.gz' 'Tower Defense' '?' 'B' '326,327,328,329,330'

시작: {"89":{"id":89,"team":"B","len":2,"budget":0,"head":[28,14],"free":1,"wall":0,"pearls":0,"visiblePearls":1,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":5,"firstInRound":true},"104":{"id":104,"team":"A","len":2,"budget":0,"head":[31,15],"free":1,"wall":0,"pearls":0,"visiblePearls":1,"ally8":0,"enemy8":1,"visibleAlly":2,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":5,"firstInRound":false}}
사망 상세: {"dead":104,"killer":89,"reason":"W","pattern":"wall_pin","flags":{"wall_pin":true,"coil":false,"pearl_bait":false},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":329,"seq":15862,"id":89,"team":"B","len":2,"head":[28,15],"after":[27,15],"action":{"kind":"move","steps":["W"]},"tag":"","free":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":0,"visibleEnemy":3,"eaten":0,"fate":null,"path":[507],"exposed":false},"victimPre":{"id":104,"team":"A","len":2,"budget":0,"head":[29,15],"free":0,"wall":0,"pearls":0,"visiblePearls":0,"ally8":0,"enemy8":1,"visibleAlly":2,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|327|89/B|2|27,14→28,14|1|0/1|E|0||
|327|104/A|2|31,15→30,15|1|3/1|W|0||
|328|89/B|2|28,14→28,15|1|0/3|S|0||
|328|104/A|2|30,15→29,15|1|2/1|W|0||
|329|89/B|2|28,15→27,15|1|0/3|W|0||
|329|104/A|2|29,15→29,15|0|2/1|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
