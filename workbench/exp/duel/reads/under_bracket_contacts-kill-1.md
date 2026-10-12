# under_bracket_contacts/kill: 806887:contact:11

[사실] 분류 N=27; 해당 특징의 중심에 가까운 사례 1. 점수 0.537.
게임 806887, Stripes/?, r160–160; 결과 kill; id 49 / 87.
기보: ~/01. Project/개인 프로젝트/unsw-swarm/data/online/sprint-bracket/M806887.replay
실행: 'node' 'eval/board.js' '~/01. Project/개인 프로젝트/unsw-swarm/data/online/sprint-bracket/M806887.replay' 'Stripes' '?' 'B' '157,158,159,160,161'

시작: {"49":{"r":160,"seq":4201,"id":49,"team":"A","len":2,"head":[11,10],"after":[11,10],"action":{"kind":"move","steps":["E"]},"tag":"","free":0,"wall":2,"self":1,"allyBody":1,"enemyBody":0,"allyHead":0,"enemyHead":0,"visibleAlly":2,"visibleEnemy":3,"eaten":0,"path":[]},"87":{"r":159,"seq":4189,"id":87,"team":"B","len":3,"head":[10,1],"after":[10,0],"action":{"kind":"move","steps":["N"]},"tag":"","free":2,"wall":1,"self":1,"allyBody":0,"enemyBody":0,"allyHead":0,"enemyHead":0,"visibleAlly":1,"visibleEnemy":3,"eaten":0,"path":[10]}}
사망 상세: {"dead":49,"killer":87,"pattern":"other_body_or_near_wall"}

|차례 r|id/팀|길이|머리→끝|빈출구|시야 아군/적|행동|진주 섭취|지시 문자열|
|---|---|---|---|---|---|---|---|---|
|157|87/B|3|8,1→9,1|2|1/1|E|0||
|158|49/A|4|12,10→11,10|1|1/4|W|0||
|158|87/B|3|9,1→10,1|3|1/2|E|0||
|159|49/A|4|11,10→11,10|0|1/3|split|0||
|159|87/B|3|10,1→10,0|2|1/3|N|0||
|160|49/A|2|11,10→11,10|0|2/3|E|0||

[해석] 위 행동과 판면 조건은 관측이다. 끊기·감기·미끼의 의도 및 같은 상황에서 다른 수를 택했을 결과는 입증하지 않는다.
