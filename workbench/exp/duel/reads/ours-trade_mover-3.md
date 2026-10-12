# ours/trade_mover: 740358:496:565:226

[사실] 분류 N=187; 해당 특징의 중심에 가까운 사례 3. 점수 1.158.
게임 740358, Slithery Fight/a, r226–228; 결과 trade; id 565 / 496.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/bench-s11-3/M740358.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/bench-s11-3/M740358.replay' 'Slithery Fight' 'a' 'A' '225,226,227,228,229'

시작: {"496":{"id":496,"team":"B","len":8,"budget":6,"head":[31,9],"free":1,"wall":0,"pearls":0,"visiblePearls":0,"ally8":0,"enemy8":1,"visibleAlly":2,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":4,"firstInRound":true},"565":{"id":565,"team":"A","len":8,"budget":6,"head":[31,7],"free":1,"wall":0,"pearls":0,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":4,"firstInRound":false}}
사망 상세: {"dead":496,"partner":565,"mover":565,"steps":1,"flags":{"wall_pin":false,"coil":false,"pearl_bait":false,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":228,"seq":39628,"id":565,"team":"A","len":2,"head":[32,7],"after":[32,7],"action":{"kind":"move","steps":["S"]},"tag":"last-trade","free":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":1,"visibleEnemy":4,"eaten":0,"fate":{"reason":"H","step":0,"hit":496,"hitTeam":"B","hitLen":8},"path":[],"exposed":false},"victimPre":{"id":496,"team":"B","len":8,"budget":6,"head":[31,8],"free":1,"wall":0,"pearls":0,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":4,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|226|496/B|8|31,10→31,9|1|2/1|N|0||
|226|565/A|8|31,7→32,7|1|0/3|E|0|E v-1000.0 d7 L8|
|227|496/B|8|31,9→31,8|1|3/1|N|0||
|227|565/A|8|32,7→32,7|1|0/4|split|0|escape-split6 L8|
|228|496/B|8|31,8→32,8|1|4/2|E|0||
|228|565/A|2|32,7→32,7|0|1/4|S|0|last-trade|

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
