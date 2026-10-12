# under_bracket/trade_mover: 806890:0:70:172

[사실] 분류 N=8; 해당 특징의 중심에 가까운 사례 1. 점수 1.203.
게임 806890, weakhold/?, r172–175; 결과 trade; id 0 / 70.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/sprint-bracket/M806890.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/sprint-bracket/M806890.replay' 'weakhold' '?' 'B' '172,173,174,175,176'

시작: {"0":{"id":0,"team":"A","len":3,"budget":1,"head":[9,0],"free":2,"wall":0,"pearls":2,"visiblePearls":2,"ally8":0,"enemy8":1,"visibleAlly":2,"visibleEnemy":0,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":14,"firstInRound":true},"70":{"id":70,"team":"B","len":3,"budget":1,"head":[5,0],"free":2,"wall":0,"pearls":0,"visiblePearls":0,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":26,"firstInRound":false}}
사망 상세: {"dead":0,"partner":70,"mover":70,"steps":2,"flags":{"wall_pin":false,"coil":false,"pearl_bait":false,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":175,"seq":4333,"id":70,"team":"B","len":3,"head":[7,1],"after":[8,1],"action":{"kind":"move","steps":["E","E"]},"tag":"","free":3,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":1,"visibleEnemy":3,"eaten":0,"fate":{"reason":"H","step":1,"hit":0,"hitTeam":"A","hitLen":3},"path":[48],"exposed":false},"victimPre":{"id":0,"team":"A","len":3,"budget":1,"head":[10,1],"free":1,"wall":0,"pearls":2,"visiblePearls":4,"ally8":0,"enemy8":1,"visibleAlly":2,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|173|0/A|3|9,0→10,0|2|2/2|E|0||
|173|70/B|3|6,0→6,1|2|0/1|S|0||
|174|0/A|3|10,0→10,1|2|2/1|S|0||
|174|70/B|3|6,1→7,1|3|0/0|E|0||
|175|0/A|3|10,1→9,1|1|2/2|W|0||
|175|70/B|3|7,1→8,1|3|1/3|EE|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
