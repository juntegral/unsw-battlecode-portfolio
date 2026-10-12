# contacts/sprint_cut: 613690:contact:227

[사실] 분류 N=1036; 해당 특징의 중심에 가까운 사례 2. 점수 0.457.
게임 613690, Schooltime/a, r399–399; 결과 kill; id 808 / 882.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/top/613689/613690.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/top/613689/613690.replay.gz' 'Schooltime' 'a' 'A' '396,397,398,399,400'

시작: {"808":{"r":399,"seq":75720,"id":808,"team":"B","len":2,"head":[51,13],"after":[51,13],"action":{"kind":"move","steps":["N"]},"tag":"","free":0,"wall":1,"self":1,"allyBody":0,"enemyBody":2,"allyHead":0,"enemyHead":0,"visibleAlly":0,"visibleEnemy":1,"eaten":0,"path":[]},"882":{"r":398,"seq":75579,"id":882,"team":"A","len":6,"head":[51,12],"after":[50,14],"action":{"kind":"move","steps":["W","S","S"]},"tag":"","free":1,"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1,"visibleAlly":0,"visibleEnemy":1,"eaten":1,"path":[770,830,890]}}
사망 상세: {"dead":808,"killer":882,"pattern":"sprint_cut"}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|396|882/A|4|50,11→51,11|3|0/1|E|1||
|397|808/B|7|51,14→51,13|2|0/1|N|1||
|397|882/A|5|51,11→51,12|3|0/1|S|1||
|398|808/B|8|51,13→51,13|1|0/1|split|0||
|398|882/A|6|51,12→50,14|1|0/1|WSS|1||
|399|808/B|2|51,13→51,13|0|0/1|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
