# contacts/sprint_cut: 595781:contact:25

[사실] 분류 N=1036; 해당 특징의 중심에 가까운 사례 1. 점수 0.457.
게임 595781, Slithery Fight/b, r159–159; 결과 kill; id 484 / 475.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/top/595778/595781.replay.gz
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/top/595778/595781.replay.gz' 'Slithery Fight' 'b' 'B' '156,157,158,159,160'

시작: {"475":{"r":159,"seq":25504,"id":475,"team":"B","len":6,"head":[25,20],"after":[25,22],"action":{"kind":"move","steps":["S","S"]},"tag":"","free":1,"wall":2,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0,"visibleAlly":0,"visibleEnemy":2,"eaten":1,"path":[1348,1411]},"484":{"r":159,"seq":25515,"id":484,"team":"A","len":2,"head":[24,21],"after":[24,21],"action":{"kind":"move","steps":["N"]},"tag":"","free":0,"wall":1,"self":1,"allyBody":0,"enemyBody":2,"allyHead":0,"enemyHead":0,"visibleAlly":1,"visibleEnemy":1,"eaten":0,"path":[]}}
사망 상세: {"dead":484,"killer":475,"pattern":"sprint_cut"}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|157|475/B|5|23,19→24,19|1|3/1|E|1||
|157|484/A|4|24,22→24,21|2|1/2|N|0||
|158|475/B|6|24,19→25,20|1|0/1|SE|1||
|158|484/A|4|24,21→24,21|1|1/2|split|0||
|159|475/B|6|25,20→25,22|1|0/2|SS|1||
|159|484/A|2|24,21→24,21|0|1/1|N|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
