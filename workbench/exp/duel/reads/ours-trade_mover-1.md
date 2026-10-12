# ours/trade_mover: 702628:135:222:408

[사실] 분류 N=187; 해당 특징의 중심에 가까운 사례 1. 점수 0.697.
게임 702628, Trauma/a, r408–410; 결과 trade; id 222 / 135.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-stack7-online/M702628.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-stack7-online/M702628.replay' 'Trauma' 'a' 'A' '407,408,409,410,411'

시작: {"135":{"id":135,"team":"B","len":8,"budget":6,"head":[15,5],"free":2,"wall":0,"pearls":0,"visiblePearls":6,"ally8":0,"enemy8":1,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":5,"firstInRound":true},"222":{"id":222,"team":"A","len":5,"budget":3,"head":[12,0],"free":1,"wall":0,"pearls":0,"visiblePearls":2,"ally8":0,"enemy8":1,"visibleAlly":1,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":4,"firstInRound":false}}
사망 상세: {"dead":135,"partner":222,"mover":222,"steps":1,"flags":{"wall_pin":false,"coil":true,"pearl_bait":false,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":410,"seq":39093,"id":222,"team":"A","len":5,"head":[11,0],"after":[11,0],"action":{"kind":"move","steps":["W"]},"tag":"W v-6.6 d7 L5 g11","free":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":0,"visibleEnemy":1,"eaten":0,"fate":{"reason":"H","step":0,"hit":135,"hitTeam":"B","hitLen":8},"path":[],"exposed":false},"victimPre":{"id":135,"team":"B","len":8,"budget":6,"head":[15,6],"free":1,"wall":0,"pearls":0,"visiblePearls":5,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|408|135/B|8|14,5→15,5|1|1/1|E|0||
|408|222/A|4|13,0→12,0|1|1/2|W|1|W v2.1 d7 L4 g9|
|409|135/B|8|15,5→15,6|2|1/1|S|0||
|409|222/A|5|12,0→11,0|1|0/0|W|0|W v1.5 d7 L5 g10|
|410|135/B|8|15,6→15,7|1|0/1|S|0||
|410|222/A|5|11,0→11,0|0|0/1|W|0|W v-6.6 d7 L5 g11|

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
