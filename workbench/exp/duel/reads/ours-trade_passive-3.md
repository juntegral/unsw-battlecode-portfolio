# ours/trade_passive: 650952:60:369:145

[사실] 분류 N=411; 해당 특징의 중심에 가까운 사례 3. 점수 0.905.
게임 650952, Slithery Fight/a, r145–147; 결과 trade; id 369 / 60.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-merge2-online-r3/M650952.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-merge2-online-r3/M650952.replay' 'Slithery Fight' 'a' 'B' '144,145,146,147,148'

시작: {"60":{"id":60,"team":"B","len":3,"budget":1,"head":[32,8],"free":1,"wall":0,"pearls":0,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":4,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":6,"firstInRound":true},"369":{"id":369,"team":"A","len":9,"budget":7,"head":[30,8],"free":1,"wall":0,"pearls":0,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":4,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":6,"firstInRound":false}}
사망 상세: {"dead":369,"partner":60,"mover":60,"steps":2,"flags":{"wall_pin":false,"coil":true,"pearl_bait":false,"head_bait":false},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":147,"seq":18073,"id":60,"team":"B","len":3,"head":[32,7],"after":[31,7],"action":{"kind":"move","steps":["W","W"]},"tag":"","free":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":4,"visibleEnemy":1,"eaten":0,"fate":{"reason":"H","step":1,"hit":369,"hitTeam":"A","hitLen":2},"path":[472],"exposed":false},"victimPre":{"id":369,"team":"A","len":9,"budget":7,"head":[30,7],"free":2,"wall":0,"pearls":0,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":3,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|144|369/A|9|30,9→30,8|1|0/5|N|0|N v-205.6 d7 L9|
|145|60/B|3|31,8→32,8|1|3/1|E|0||
|145|369/A|9|30,8→30,7|1|0/2|N|0|N v-923.2 d7 L9|
|146|60/B|3|32,8→32,7|1|3/1|N|0||
|146|369/A|9|30,7→30,7|2|0/3|split|0|escape-split7 L9|
|147|60/B|3|32,7→31,7|1|4/1|WW|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
