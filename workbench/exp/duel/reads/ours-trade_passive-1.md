# ours/trade_passive: 650988:6:10:58

[사실] 분류 N=411; 해당 특징의 중심에 가까운 사례 1. 점수 0.806.
게임 650988, Default/a, r58–60; 결과 trade; id 6 / 10.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-merge2-online-r3/M650988.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/cand-merge2-online-r3/M650988.replay' 'Default' 'a' 'B' '57,58,59,60,61'

시작: {"6":{"id":6,"team":"A","len":7,"budget":5,"head":[0,3],"free":2,"wall":1,"pearls":0,"visiblePearls":3,"ally8":0,"enemy8":2,"visibleAlly":0,"visibleEnemy":0,"blocked":{"wall":0,"self":2,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":21,"firstInRound":true},"10":{"id":10,"team":"B","len":3,"budget":1,"head":[28,3],"free":2,"wall":0,"pearls":0,"visiblePearls":0,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":0,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":11,"firstInRound":false}}
사망 상세: {"dead":6,"partner":10,"mover":10,"steps":3,"flags":{"wall_pin":false,"coil":false,"pearl_bait":false,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":60,"seq":1700,"id":10,"team":"B","len":4,"head":[29,3],"after":[30,4],"action":{"kind":"move","steps":["E","S","E"]},"tag":"","free":2,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":0,"visibleEnemy":1,"eaten":0,"fate":{"reason":"H","step":2,"hit":6,"hitTeam":"A","hitLen":7},"path":[126,158],"exposed":false},"victimPre":{"id":6,"team":"A","len":7,"budget":5,"head":[31,3],"free":2,"wall":2,"pearls":0,"visiblePearls":1,"ally8":0,"enemy8":2,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":0,"self":2,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|58|6/A|7|1,3→0,3|2|0/0|W|0|W v7.0 d7 L7|
|58|10/B|3|28,2→28,3|2|0/0|S|0||
|59|6/A|7|0,3→31,3|2|0/0|W|0|W v7.5 d7 L7|
|59|10/B|3|28,3→29,3|2|0/1|E|1||
|60|6/A|7|31,3→31,4|2|0/1|S|0|S v4.8 d7 L7|
|60|10/B|4|29,3→30,4|2|0/1|ESE|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
