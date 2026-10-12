# contacts/cut_off: 637158:contact:12

[사실] 분류 N=8372; 해당 특징의 중심에 가까운 사례 2. 점수 0.462.
게임 637158, Trauma/a, r246–246; 결과 kill; id 224 / 166.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/top/637150/637158.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/top/637150/637158.replay.gz' 'Trauma' 'a' 'A' '243,244,245,246,247'

시작: {"166":{"r":246,"seq":22180,"id":166,"team":"A","len":4,"head":[25,22],"after":[25,23],"action":{"kind":"move","steps":["S"]},"tag":"","free":2,"wall":0,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1,"visibleAlly":1,"visibleEnemy":1,"eaten":0,"path":[1129]},"224":{"r":246,"seq":22216,"id":224,"team":"B","len":3,"head":[11,20],"after":[11,20],"action":{"kind":"move","steps":["W"]},"tag":"","free":1,"wall":1,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0,"visibleAlly":1,"visibleEnemy":0,"eaten":0,"path":[]}}
사망 상세: {"dead":224,"killer":166,"pattern":"cut_off"}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|244|166/A|3|26,21→25,21|1|1/1|W|0||
|244|224/B|4|11,19→11,19|2|2/0|split|0||
|245|166/A|3|25,21→25,22|2|1/1|S|1||
|245|224/B|2|11,19→11,20|2|2/0|S|1||
|246|166/A|4|25,22→25,23|2|1/1|S|0||
|246|224/B|3|11,20→11,20|1|1/0|W|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
