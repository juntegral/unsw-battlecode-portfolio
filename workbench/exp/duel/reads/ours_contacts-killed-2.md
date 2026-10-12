# ours_contacts/killed: 748854:contact:20

[사실] 분류 N=1141; 해당 특징의 중심에 가까운 사례 2. 점수 0.657.
게임 748854, Schooltime/a, r222–222; 결과 kill; id 137 / 192.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/v1-w2/M748854.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/v1-w2/M748854.replay' 'Schooltime' 'a' 'B' '219,220,221,222,223'

시작: {"137":{"r":222,"seq":25656,"id":137,"team":"A","len":3,"head":[40,39],"after":[40,39],"action":{"kind":"move","steps":["E"]},"tag":"no-exit E=S","free":0,"wall":1,"self":1,"allyBody":1,"enemyBody":1,"allyHead":0,"enemyHead":0,"visibleAlly":1,"visibleEnemy":2,"eaten":0,"path":[]},"192":{"r":221,"seq":25563,"id":192,"team":"B","len":8,"head":[43,37],"after":[43,36],"action":{"kind":"move","steps":["N"]},"tag":"","free":3,"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0,"visibleAlly":1,"visibleEnemy":2,"eaten":0,"path":[2203]}}
사망 상세: {"dead":137,"killer":192,"pattern":"coil"}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|219|192/B|7|42,38→43,38|2|0/1|E|0||
|220|137/A|2|38,39→39,39|2|1/0|E|1|E v6.0 d7 L2 cl@39,39 sd17@43,10o bl4@35,25 k0 E=S|
|220|192/B|7|43,38→43,37|2|1/0|N|1||
|221|137/A|3|39,39→40,39|1|1/1|E|0|E v-1113.0 d7 L3 sd1@43,39o E=S|
|221|192/B|8|43,37→43,36|3|1/2|N|0||
|222|137/A|3|40,39→40,39|0|1/2|E|0|no-exit E=S|

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
