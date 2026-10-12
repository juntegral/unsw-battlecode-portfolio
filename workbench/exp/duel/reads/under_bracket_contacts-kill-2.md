# under_bracket_contacts/kill: 806959:contact:16

[사실] 분류 N=27; 해당 특징의 중심에 가까운 사례 2. 점수 0.537.
게임 806959, Around UNSW/?, r132–132; 결과 kill; id 277 / 36.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806954/806959.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/elite/806954/806959.replay.gz' 'Around UNSW' '?' 'B' '129,130,131,132,133'

시작: {"36":{"r":132,"seq":20877,"id":36,"team":"B","len":3,"head":[30,31],"after":[31,31],"action":{"kind":"move","steps":["E"]},"tag":"","free":1,"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":1,"visibleAlly":1,"visibleEnemy":5,"eaten":0,"path":[2015]},"277":{"r":132,"seq":21046,"id":277,"team":"A","len":2,"head":[30,30],"after":[30,30],"action":{"kind":"move","steps":["W"]},"tag":"","free":0,"wall":2,"self":1,"allyBody":0,"enemyBody":1,"allyHead":0,"enemyHead":0,"visibleAlly":4,"visibleEnemy":2,"eaten":0,"path":[]}}
사망 상세: {"dead":277,"killer":36,"pattern":"wall_pin"}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|130|36/B|2|29,32→30,32|2|1/2|E|1||
|130|277/A|5|30,29→30,30|3|4/1|S|1||
|131|36/B|3|30,32→30,31|2|1/3|N|0||
|131|277/A|6|30,30→30,30|0|3/1|split|0||
|132|36/B|3|30,31→31,31|1|1/5|E|0||
|132|277/A|2|30,30→30,30|0|4/2|W|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
