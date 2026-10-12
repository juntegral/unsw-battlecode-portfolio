# under_bracket/trade_mover: 806957:13:15:53

[사실] 분류 N=8; 해당 특징의 중심에 가까운 사례 2. 점수 1.240.
게임 806957, Stripes/?, r53–55; 결과 trade; id 13 / 15.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806954/806957.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806954/806957.replay.gz' 'Stripes' '?' 'B' '52,53,54,55,56'

시작: {"13":{"id":13,"team":"A","len":3,"budget":1,"head":[11,0],"free":1,"wall":0,"pearls":1,"visiblePearls":1,"ally8":0,"enemy8":1,"visibleAlly":3,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":14,"firstInRound":true},"15":{"id":15,"team":"B","len":2,"budget":0,"head":[13,11],"free":2,"wall":0,"pearls":1,"visiblePearls":3,"ally8":0,"enemy8":3,"visibleAlly":1,"visibleEnemy":2,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":27,"firstInRound":false}}
사망 상세: {"dead":13,"partner":15,"mover":15,"steps":1,"flags":{"wall_pin":false,"coil":false,"pearl_bait":true,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":55,"seq":996,"id":15,"team":"B","len":2,"head":[13,0],"after":[13,0],"action":{"kind":"move","steps":["S"]},"tag":"","free":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1},"visibleAlly":0,"visibleEnemy":3,"eaten":0,"fate":{"reason":"H","step":0,"hit":13,"hitTeam":"A","hitLen":5},"path":[],"exposed":false},"victimPre":{"id":13,"team":"A","len":4,"budget":2,"head":[11,1],"free":1,"wall":0,"pearls":1,"visiblePearls":3,"ally8":1,"enemy8":1,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|53|13/A|3|12,0→11,0|1|3/1|W|0||
|53|15/B|2|13,10→13,11|2|1/2|S|0||
|54|13/A|3|11,0→11,1|1|3/1|S|1||
|54|15/B|2|13,11→13,0|2|1/3|S|0||
|55|13/A|4|11,1→12,1|1|1/1|E|1||
|55|15/B|2|13,0→13,0|1|0/3|S|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
