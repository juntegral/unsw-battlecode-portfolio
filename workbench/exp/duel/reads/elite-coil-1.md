# elite/coil: 800834:20:615:241

[사실] 분류 N=1427; 해당 특징의 중심에 가까운 사례 1. 점수 0.637.
게임 800834, Slithery Fight/b, r241–243; 결과 trade; id 20 / 615.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/800831/800834.replay.gz
실행: 'node' '--require' './exp/duel/ledger-preload.js' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/800831/800834.replay.gz' 'Slithery Fight' 'b' 'B' '240,241,242,243,244'

시작: {"20":{"id":20,"team":"A","len":7,"budget":6,"head":[34,13],"free":1,"wall":0,"pearls":1,"visiblePearls":2,"ally8":3,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":4,"firstInRound":true},"615":{"id":615,"team":"B","len":5,"budget":4,"head":[32,15],"free":1,"wall":0,"pearls":1,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":4,"firstInRound":false}}
사망 상세: {"dead":20,"partner":615,"mover":615,"steps":1,"flags":{"wall_pin":false,"coil":true,"pearl_bait":true,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":243,"seq":54428,"id":615,"team":"B","len":5,"head":[33,15],"after":[33,15],"action":{"kind":"move","steps":["N"]},"tag":"","free":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":1,"visibleEnemy":2,"eaten":0,"fate":{"reason":"H","step":0,"hit":20,"hitTeam":"A","hitLen":8},"path":[],"exposed":false},"victimPre":{"id":20,"team":"A","len":7,"budget":6,"head":[34,14],"free":1,"wall":0,"pearls":1,"visiblePearls":1,"ally8":1,"enemy8":1,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|241|20/A|6|35,13→34,13|1|1/2|W|1||
|241|615/B|5|32,16→32,15|1|1/1|N|0||
|242|20/A|7|34,13→34,14|1|0/1|S|0||
|242|615/B|5|32,15→33,15|1|1/2|E|0||
|243|20/A|7|34,14→33,14|1|1/1|W|1||
|243|615/B|5|33,15→33,15|0|1/2|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
