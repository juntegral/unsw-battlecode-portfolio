# contacts/wall_pin: 588116:contact:203

[사실] 분류 N=10894; 해당 특징의 중심에 가까운 사례 2. 점수 0.661.
게임 588116, Schooltime/a, r325–325; 결과 kill; id 612 / 580.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/top/588110/588116.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/top/588110/588116.replay.gz' 'Schooltime' 'a' 'A' '322,323,324,325,326'

시작: {"580":{"r":325,"seq":63071,"id":580,"team":"A","len":3,"head":[45,21],"after":[45,20],"action":{"kind":"move","steps":["N"]},"tag":"","free":2,"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1,"visibleAlly":0,"visibleEnemy":1,"eaten":1,"path":[1245]},"612":{"r":325,"seq":63095,"id":612,"team":"B","len":3,"head":[17,12],"after":[17,12],"action":{"kind":"move","steps":["E"]},"tag":"","free":1,"wall":1,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0,"visibleAlly":2,"visibleEnemy":0,"eaten":0,"path":[]}}
사망 상세: {"dead":612,"killer":580,"pattern":"cut_off"}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|323|580/A|3|46,22→46,21|3|0/0|N|0||
|323|612/B|3|16,13→16,12|1|3/0|N|0||
|324|580/A|3|46,21→45,21|3|0/1|W|0||
|324|612/B|3|16,12→17,12|1|3/0|E|0||
|325|580/A|3|45,21→45,20|2|0/1|N|1||
|325|612/B|3|17,12→17,12|1|2/0|E|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
