# bracket/cut_off: 806983:733:834:376

[사실] 분류 N=47; 해당 특징의 중심에 가까운 사례 1. 점수 0.761.
게임 806983, Islands/?, r376–379; 결과 kill; id 733 / 834.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806982/806983.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806982/806983.replay.gz' 'Islands' '?' 'A' '376,377,378,379,380'

시작: {"733":{"id":733,"team":"A","len":4,"budget":2,"head":[23,13],"free":3,"wall":2,"pearls":2,"visiblePearls":1,"ally8":1,"enemy8":4,"visibleAlly":0,"visibleEnemy":0,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":57,"firstInRound":true},"834":{"id":834,"team":"B","len":4,"budget":2,"head":[14,21],"free":1,"wall":0,"pearls":2,"visiblePearls":1,"ally8":1,"enemy8":1,"visibleAlly":0,"visibleEnemy":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":37,"firstInRound":false}}
사망 상세: {"dead":834,"killer":733,"reason":"O","pattern":"cut_off","flags":{"cut_off":true,"sprint_cut":false,"wall_pin":false,"coil":false,"pearl_bait":false},"hitTile":750,"blockerAge":1,"lastKillerAction":{"r":379,"seq":57252,"id":733,"team":"A","len":5,"head":[22,14],"after":[21,14],"action":{"kind":"move","steps":["W"]},"tag":"","free":2,"blocked":{"wall":0,"self":2,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":0,"visibleEnemy":0,"eaten":0,"fate":null,"path":[805],"exposed":false},"victimPre":{"id":834,"team":"B","len":5,"budget":3,"head":[15,22],"free":2,"wall":1,"pearls":0,"visiblePearls":0,"ally8":2,"enemy8":1,"visibleAlly":0,"visibleEnemy":0,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|377|733/A|4|23,13→22,13|3|0/0|W|1||
|377|834/B|4|14,21→14,22|1|0/0|S|0||
|378|733/A|5|22,13→22,14|3|0/0|S|0||
|378|834/B|4|14,22→15,22|2|0/0|E|1||
|379|733/A|5|22,14→21,14|2|0/0|W|0||
|379|834/B|5|15,22→15,22|2|0/0|S|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
