# bracket/sprint_cut: 806876:123:179:272

[사실] 분류 N=9; 해당 특징의 중심에 가까운 사례 1. 점수 1.138.
게임 806876, weakhold/?, r272–274; 결과 kill; id 179 / 123.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806870/806876.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806870/806876.replay.gz' 'weakhold' '?' 'B' '271,272,273,274,275'

시작: {"123":{"id":123,"team":"B","len":6,"budget":4,"head":[15,3],"free":1,"wall":0,"pearls":1,"visiblePearls":3,"ally8":1,"enemy8":1,"visibleAlly":1,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":7,"firstInRound":true},"179":{"id":179,"team":"A","len":2,"budget":0,"head":[12,4],"free":1,"wall":0,"pearls":1,"visiblePearls":2,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":13,"firstInRound":false}}
사망 상세: {"dead":179,"killer":123,"reason":"O","pattern":"sprint_cut","flags":{"cut_off":true,"sprint_cut":true,"wall_pin":true,"coil":true,"pearl_bait":false},"hitTile":133,"blockerAge":0,"lastKillerAction":{"r":274,"seq":12562,"id":123,"team":"B","len":7,"head":[14,3],"after":[13,2],"action":{"kind":"move","steps":["W","N"]},"tag":"","free":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":1,"visibleEnemy":2,"eaten":0,"fate":null,"path":[133,93],"exposed":false},"victimPre":{"id":179,"team":"A","len":2,"budget":0,"head":[13,4],"free":0,"wall":0,"pearls":0,"visiblePearls":1,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":2,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|272|123/B|5|16,3→15,3|1|3/0|W|1||
|272|179/A|2|11,4→12,4|1|0/0|E|0||
|273|123/B|6|15,3→14,3|1|2/1|W|1||
|273|179/A|2|12,4→13,4|1|0/1|E|0||
|274|123/B|7|14,3→13,2|1|1/2|WN|0||
|274|179/A|2|13,4→13,4|0|0/2|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
