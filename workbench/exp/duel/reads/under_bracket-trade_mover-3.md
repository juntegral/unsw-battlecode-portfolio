# under_bracket/trade_mover: 806885:500:555:282

[사실] 분류 N=8; 해당 특징의 중심에 가까운 사례 3. 점수 1.320.
게임 806885, Islands/?, r282–284; 결과 trade; id 500 / 555.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/sprint-bracket/M806885.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/sprint-bracket/M806885.replay' 'Islands' '?' 'B' '281,282,283,284,285'

시작: {"500":{"id":500,"team":"A","len":2,"budget":0,"head":[50,5],"free":2,"wall":0,"pearls":4,"visiblePearls":6,"ally8":0,"enemy8":1,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":28,"firstInRound":true},"555":{"id":555,"team":"B","len":2,"budget":0,"head":[50,3],"free":3,"wall":1,"pearls":2,"visiblePearls":5,"ally8":1,"enemy8":2,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":45,"firstInRound":false}}
사망 상세: {"dead":500,"partner":555,"mover":555,"steps":2,"flags":{"wall_pin":false,"coil":false,"pearl_bait":true,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":284,"seq":43506,"id":555,"team":"B","len":3,"head":[52,3],"after":[52,4],"action":{"kind":"move","steps":["S","S"]},"tag":"","free":3,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":0,"visibleEnemy":1,"eaten":0,"fate":{"reason":"H","step":1,"hit":500,"hitTeam":"A","hitLen":4},"path":[276],"exposed":false},"victimPre":{"id":500,"team":"A","len":3,"budget":1,"head":[51,5],"free":3,"wall":1,"pearls":2,"visiblePearls":3,"ally8":0,"enemy8":1,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|282|500/A|2|50,6→50,5|2|1/1|N|0||
|282|555/B|2|50,3→51,3|3|0/2|E|1||
|283|500/A|2|50,5→51,5|2|1/1|E|1||
|283|555/B|3|51,3→52,3|3|0/1|E|0||
|284|500/A|3|51,5→52,5|3|1/1|E|1||
|284|555/B|3|52,3→52,4|3|0/1|SS|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
