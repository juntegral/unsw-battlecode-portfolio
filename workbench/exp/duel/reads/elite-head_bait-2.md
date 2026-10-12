# elite/head_bait: 687878:315:392:187

[사실] 분류 N=4315; 해당 특징의 중심에 가까운 사례 2. 점수 0.550.
게임 687878, Slithery Fight/b, r187–189; 결과 trade; id 315 / 392.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/top/687878/687878.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/top/687878/687878.replay.gz' 'Slithery Fight' 'b' 'A' '186,187,188,189,190'

시작: {"315":{"id":315,"team":"A","len":3,"budget":1,"head":[39,1],"free":3,"wall":1,"pearls":4,"visiblePearls":23,"ally8":1,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":27,"firstInRound":true},"392":{"id":392,"team":"B","len":4,"budget":2,"head":[42,2],"free":2,"wall":1,"pearls":10,"visiblePearls":21,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":0,"self":2,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":38,"firstInRound":false}}
사망 상세: {"dead":392,"partner":315,"mover":315,"steps":2,"flags":{"wall_pin":false,"coil":false,"pearl_bait":false,"head_bait":true},"hitTile":null,"blockerAge":null,"lastKillerAction":{"r":189,"seq":37437,"id":315,"team":"A","len":3,"head":[41,2],"after":[41,3],"action":{"kind":"move","steps":["S","E"]},"tag":"","free":1,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0},"visibleAlly":0,"visibleEnemy":1,"eaten":1,"fate":{"reason":"H","step":1,"hit":392,"hitTeam":"B","hitLen":4},"path":[230],"exposed":false},"victimPre":{"id":392,"team":"B","len":4,"budget":2,"head":[42,2],"free":1,"wall":1,"pearls":8,"visiblePearls":20,"ally8":0,"enemy8":2,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":0,"self":2,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|186|392/B|3|43,1→42,1|3|1/0|W|1||
|187|315/A|3|38,1→39,1|3|0/0|E|0||
|187|392/B|4|42,1→42,2|3|0/1|S|0||
|188|315/A|3|39,1→41,2|3|0/1|ESE|2||
|188|392/B|4|42,2→42,3|1|0/1|S|0||
|189|315/A|3|41,2→41,3|1|0/1|SE|1||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
