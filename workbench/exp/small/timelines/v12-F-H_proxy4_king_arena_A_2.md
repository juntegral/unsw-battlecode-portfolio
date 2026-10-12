# v12-F-H:proxy4_king:arena:A:2 (Arena, 우리 A)

기보: ~/01. Project/개인 프로젝트/unsw-swarm/exp/gen/v12-F-H/games/proxy4_king_arena_A_2/game.replay
결과: teamEliminated, 32라운드. 전멸 true; 마지막 사망 r31.
수 열세: 첫 라운드 시작 r20, 10라운드 지속 시작 r20. 사건 첫 열세 {"r":19,"kind":"split","id":4,"A":2,"B":3,"from":0,"to":-1}.

## 분열 전수

|r|부모→새끼|규칙|전→부모+새끼|머리 x,y|새끼 빈출구|새끼 사망|
|---|---|---|---|---|---|---|
|13|0→2|csplit: csplit2 u1 L5 t8 v k E=F|5→3+2|0,7|2|r29 rammed|
|21|0→5|csplit: csplit2 u2 L6 t8 v k E=F|6→4+2|4,10|2|r27 rammed|
|30|0→23|escsplit: escape-split3 L5 E=F|5→2+3|2,10|2|r31 rammed|

## 사망 전수

|r|id|원인|길이|x,y|충돌 상대|최근 분열|자기 차례 빈출구|
|---|---|---|---|---|---|---|---|
|27|5|rammed|4|6,9|10|r21 child csplit|2|
|29|2|rammed|10|1,2|8|r13 child csplit|2|
|30|0|rammed|2|6,10|15|r30 parent escsplit|1|
|31|23|rammed|4|3,9|11|r30 child escsplit|2|

## 매 라운드 시작 머리 수

|r|우리/적|우리 길이|적 길이|
|---|---|---|---|
|0|1/1|3|3|
|1|1/1|3|3|
|2|1/1|3|3|
|3|1/1|3|3|
|4|1/1|3|3|
|5|1/1|3|3|
|6|1/1|3|3|
|7|1/1|3|3|
|8|1/1|3|3|
|9|1/1|3|3|
|10|1/1|3|3|
|11|1/1|4|3|
|12|1/1|4|3|
|13|1/1|5|3|
|14|2/1|3,2|3|
|15|2/1|3,3|3|
|16|2/1|4,3|4|
|17|2/2|5,3|3,2|
|18|2/2|6,4|4,3|
|19|2/2|7,4|5,4|
|20|2/3|8,5|5,3,3|
|21|2/3|9,6|6,4,3|
|22|3/5|10,4,2|4,4,3,3,2|
|23|3/6|11,4,3|5,4,4,3,3,2|
|24|3/8|10,4,3|5,4,4,3,3,3,3,2|
|25|3/8|10,5,3|6,5,5,4,4,4,4,3|
|26|3/11|10,5,3|6,6,5,4,4,3,3,3,2,2,2|
|27|3/12|10,5,3|6,6,5,4,4,4,3,3,3,3,3,2|
|28|2/15|10,5|5,4,4,4,3,3,3,3,3,3,3,3,3,2,2|
|29|2/16|10,5|5,5,5,4,4,3,3,3,3,3,3,3,3,3,2,2|
|30|1/17|5|6,5,4,4,4,4,3,3,3,3,3,3,3,2,2,2,2|
|31|1/20|4|5,4,4,4,4,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2|

## 전멸 직전 20라운드 (차례 이전 상태와 실제 행동)

|r|시작 우리/적|분열|사망(위치)|우리 행동|
|---|---|---|---|---|
|12|1/1|||#0 L4 E E v13.6 d7 L4 cov cl@2,9 E=F|
|13|1/1|0→2 csplit||#0 L5 {"kind":"split","childSegmentCount":2} csplit2 u1 L5 t8 v k E=F; #2 L2 N N v16.1 d7 L2 cl@1,6 kbr map=none E=F|
|14|2/1|||#0 L3 S S v12.2 d7 L3 E=F; #2 L2 E E v17.4 d7 L2 cl@1,6 E=F|
|15|2/1|||#0 L3 E E v12.3 d7 L3 cov cl@4,9 kbr bl4@0,6 k0 E=F; #2 L3 N N v18.7 d7 L3 cl@1,5 bl4@2,9 k0 E=F|
|16|2/1|||#0 L3 E E v14.1 d7 L3 cov cl@4,9 E=F; #2 L4 N N v19.5 d7 L4 cl@1,4 E=F|
|17|2/2|||#0 L3 NW NW v7.6 d7 L3 cl@4,9 tgx E=F; #2 L5 N N v19.5 d7 L5 E=F|
|18|2/2|||#0 L4 W W v14.5 d7 L4 cov cl@2,8 tg E=F; #2 L6 N N v18.9 d7 L6 E=F|
|19|2/2|||#0 L4 N N v16.4 d7 L4 cov cl@2,8 E=F; #2 L7 N N v19.1 d7 L7 E=F|
|20|2/3|||#0 L5 W W v11.8 d7 L5 bl4@0,6 k1 E=F; #2 L8 E E v18.7 d7 L8 bl4@2,9 k1 E=F|
|21|2/3|0→5 csplit||#0 L6 {"kind":"split","childSegmentCount":2} csplit2 u2 L6 t8 v k E=F; #2 L9 E E v17.8 d7 L9 E=F; #5 L2 E E v15.3 d7 L2 cl@5,9 kbr map=none E=F|
|22|3/5|||#0 L4 W W v8.1 d7 L4 F5@3,5 cov tg E=F; #2 L10 E E v17.6 d7 L10 E=F; #5 L2 N N v17.9 d7 L2 cl@5,9 tg E=F|
|23|3/6|||#0 L4 S S v-2.5 d7 L4 F4@3,5 cov E=F; #2 L11 NW NW v4.8 d7 L11 tg E=F; #5 L3 W W v6.5 d7 L3 cl@4,8 tgx E=F|
|24|3/8|||#0 L4 E E v3.4 d7 L4 F5@3,5 cl@1,9 kbr E=F; #2 L10 W W v6.5 d7 L10 kb E=F; #5 L3 S S v4.1 d7 L3 tgx E=F|
|25|3/8|||#0 L5 S S v-18.0 d7 L5 F4@3,5 bl10@2,0 k0 E=F; #2 L10 W W v7.6 d7 L10 bl5@1,10 k1 E=F; #5 L3 E E v-0.2 d7 L3 tgx bl9@1,0 k0 E=F|
|26|3/11|||#0 L5 E E v-61.1 d7 L5 F5@3,5 tgx E=F; #2 L10 W W v9.0 d7 L10 E=F; #5 L3 E E v6.1 d7 L3 E=F|
|27|3/12||#5 rammed L4 @6,9|#0 L5 E E v-50.2 d7 L5 F4@3,5 tgx E=F; #2 L10 S S v10.0 d7 L10 E=F; #5 L3 N N v-52.2 d7 L3 cl@6,9 E=F|
|28|2/15|||#0 L5 EE EE v-24.1 d7 L5 grab@5,10 tgx E=F; #2 L10 S S v-63.9 d7 L10 tgx E=F|
|29|2/16||#2 rammed L10 @1,2|#0 L5 E E v-62.0 d7 L5 E=F; #2 L10 E E v-145.3 d7 L10 E=F|
|30|1/17|0→23 escsplit|#0 rammed L2 @6,10|#0 L5 {"kind":"split","childSegmentCount":3} escape-split3 L5 E=F; #23 L3 NE NE v-65.5 d7 L3 cl@2,9 tg bl0@- k1 map=none E=F|
|31|1/20||#23 rammed L4 @3,9||

모든 head-on의 이동 주체, 길이, d3/d8, 시야 내 머리 수, 막힘 여부는 tables.json의 해당 ourGames.headons와 headons.jsonl에 있다.
