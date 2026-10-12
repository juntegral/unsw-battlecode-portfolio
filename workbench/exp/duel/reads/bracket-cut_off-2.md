# bracket/cut_off: 803612:55:133:252

[사실] 분류 N=47; 해당 특징의 중심에 가까운 사례 2. 점수 0.887.
게임 803612, Tower Defense/?, r252–255; 결과 kill; id 55 / 133.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/803608/803612.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/803608/803612.replay.gz' 'Tower Defense' '?' 'A' '252,253,254,255,256'

시작: {"55":{"id":55,"team":"A","len":3,"budget":1,"head":[30,6],"free":3,"wall":1,"pearls":0,"visiblePearls":0,"ally8":1,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":24,"firstInRound":true},"133":{"id":133,"team":"B","len":3,"budget":1,"head":[30,10],"free":1,"wall":0,"pearls":0,"visiblePearls":0,"ally8":0,"enemy8":1,"visibleAlly":2,"visibleEnemy":0,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"space":7,"firstInRound":false}}
사망 상세: {"dead":133,"killer":55,"reason":"O","pattern":"cut_off","flags":{"cut_off":true,"sprint_cut":false,"wall_pin":false,"coil":true,"pearl_bait":false},"hitTile":254,"blockerAge":1,"lastKillerAction":{"r":255,"seq":15145,"id":55,"team":"A","len":3,"head":[31,7],"after":[31,8],"action":{"kind":"move","steps":["S"]},"tag":"","free":2,"blocked":{"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0},"visibleAlly":0,"visibleEnemy":1,"eaten":0,"fate":null,"path":[287],"exposed":false},"victimPre":{"id":133,"team":"B","len":3,"budget":1,"head":[30,8],"free":0,"wall":0,"pearls":0,"visiblePearls":2,"ally8":0,"enemy8":1,"visibleAlly":0,"visibleEnemy":1,"blocked":{"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0}}}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|253|55/A|3|30,6→30,7|3|0/0|S|0||
|253|133/B|3|30,10→30,9|1|0/1|N|0||
|254|55/A|3|30,7→31,7|2|0/1|E|0||
|254|133/B|3|30,9→30,8|1|0/1|N|0||
|255|55/A|3|31,7→31,8|2|0/1|S|0||
|255|133/B|3|30,8→30,8|0|0/1|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
