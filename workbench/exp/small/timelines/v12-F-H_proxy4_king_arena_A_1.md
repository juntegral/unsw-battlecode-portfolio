# v12-F-H:proxy4_king:arena:A:1 (Arena, 우리 A)

기보: ~/01. Project/개인 프로젝트/unsw-swarm/exp/gen/v12-F-H/games/proxy4_king_arena_A_1/game.replay
결과: teamEliminated, 28라운드. 전멸 true; 마지막 사망 r27.
수 열세: 첫 라운드 시작 r14, 10라운드 지속 시작 r14. 사건 첫 열세 {"r":13,"kind":"split","id":4,"A":2,"B":3,"from":0,"to":-1}.

## 분열 전수

|r|부모→새끼|규칙|전→부모+새끼|머리 x,y|새끼 빈출구|새끼 사망|
|---|---|---|---|---|---|---|
|8|0→2|csplit: csplit2 u1 L4 t8 k E=F|4→2+2|2,7|3|r19 rammed|
|16|0→7|csplit: csplit2 u2 L5 t8 v k E=F|5→3+2|2,9|3|r27 rammed|
|19|7→12|csplit: csplit2 u3 L4 t8 v k E=F|4→2+2|2,9|2|r26 rammed|

## 사망 전수

|r|id|원인|길이|x,y|충돌 상대|최근 분열|자기 차례 빈출구|
|---|---|---|---|---|---|---|---|
|19|2|rammed|2|4,0|10|r8 child csplit|2|
|22|0|trap|2|5,10|7|r16 parent csplit|0|
|26|12|rammed|3|1,9|3|r19 child csplit|3|
|27|7|rammed|3|10,8|29|r19 parent csplit|1|

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
|8|1/1|4|3|
|9|2/1|2,2|4|
|10|2/2|2,2|3,2|
|11|2/2|3,2|3,2|
|12|2/2|3,3|3,2|
|13|2/2|4,3|4,3|
|14|2/3|5,2|4,3,2|
|15|2/4|5,2|4,3,3,2|
|16|2/5|5,2|4,3,3,3,2|
|17|3/5|3,2,2|4,4,4,4,3|
|18|3/9|3,3,2|4,3,3,3,2,2,2,2,2|
|19|3/9|4,2,2|5,4,4,3,3,3,3,3,3|
|20|3/8|2,2,2|6,5,4,4,4,4,4,3|
|21|3/13|3,2,2|7,5,4,3,3,3,3,2,2,2,2,2,2|
|22|3/15|3,2,2|5,4,4,4,4,4,3,3,3,3,3,3,2,2,2|
|23|2/15|3,2|5,4,4,4,4,4,4,3,3,3,2,2,2,2,2|
|24|2/18|3,2|5,5,4,4,3,3,3,3,3,3,3,2,2,2,2,2,2,2|
|25|2/20|3,2|6,4,4,4,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2|
|26|2/19|3,3|6,4,4,4,4,3,3,3,3,3,3,2,2,2,2,2,2,2,2|
|27|1/20|3|6,5,5,4,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2|

## 전멸 직전 20라운드 (차례 이전 상태와 실제 행동)

|r|시작 우리/적|분열|사망(위치)|우리 행동|
|---|---|---|---|---|
|8|1/1|0→2 csplit||#0 L4 {"kind":"split","childSegmentCount":2} csplit2 u1 L4 t8 k E=F; #2 L2 N N v10.8 d7 L2 cl@2,5 map=none E=F|
|9|2/1|||#0 L2 N N v12.2 d7 L2 cl@4,8 E=F; #2 L2 W W v8.9 d7 L2 kbr E=F|
|10|2/2|||#0 L2 W W v10.3 d7 L2 tg bl2@1,6 k1 E=F; #2 L2 N N v11.0 d7 L2 cl@1,5 tg bl2@2,8 k1 E=F|
|11|2/2|||#0 L2 S S v10.7 d7 L2 cl@2,9 kbr E=F; #2 L3 W W v10.6 d7 L3 tg E=F|
|12|2/2|||#0 L3 W W v7.3 d7 L3 cl@1,9 E=F; #2 L3 N N v11.2 d7 L3 cl@2,4 E=F|
|13|2/2|||#0 L4 N N v11.5 d7 L4 cl@1,8 E=F; #2 L3 NN NN v9.4 d7 L3 cl@1,1 tg E=F|
|14|2/3|||#0 L5 W W v10.7 d7 L5 E=F; #2 L2 N N v9.2 d7 L2 cl@1,1 tg E=F|
|15|2/4|||#0 L5 S S v3.5 d7 L5 tg bl4@1,5 k1 E=F; #2 L2 N N v8.6 d7 L2 tg bl4@0,9 k0 E=F|
|16|2/5|0→7 csplit||#0 L5 {"kind":"split","childSegmentCount":2} csplit2 u2 L5 t8 v k E=F; #2 L2 E E v2.9 d7 L2 cl@1,1 tgx E=F; #7 L2 E E v5.7 d7 L2 cl@4,9 kbr map=none E=F|
|17|3/5|||#0 L3 S S v5.7 d7 L3 tg E=F; #2 L2 E E v4.6 d7 L2 cl@2,1 kbr E=F; #7 L2 E E v9.4 d7 L2 cl@4,9 tg E=F|
|18|3/9|||#0 L3 EE EE v6.5 d7 L3 cl@4,9 tg E=F; #2 L2 E E v1.3 d7 L2 cl@3,1 E=F; #7 L3 E E v-4.7 d7 L3 cl@5,9 E=F|
|19|3/9|7→12 csplit|#2 rammed L2 @4,0|#0 L2 E E v7.7 d7 L2 kbr E=F; #2 L2 E E v-2.2 d7 L2 cl@4,1 E=F; #7 L4 {"kind":"split","childSegmentCount":2} csplit2 u3 L4 t8 v k E=F; #12 L2 W W v-4.6 d7 L2 map=none E=F|
|20|3/8|||#0 L2 E E v1.8 d7 L2 bl2@5,9 k1 E=F; #7 L2 E E v-3.0 d7 L2 cl@6,9 tgx bl4@- k0 E=F; #12 L2 S S v-2.9 d7 L2 kbr bl4@5,9 k0 E=F|
|21|3/13|||#0 L2 E E v5.2 d7 L2 E=F; #7 L3 S S v6.1 d7 L3 tg E=F; #12 L2 W W v-33.5 d7 L2 E=F|
|22|3/15||#0 trap L2 @5,10|#0 L2 N no-exit s E=F; #7 L3 E E v-5.5 d7 L3 cl@7,9 tg E=F; #12 L2 N N v7.1 d7 L2 cl@1,9 tgx E=F|
|23|2/15|||#7 L3 E E v-0.2 d7 L3 cl@8,9 tg E=F; #12 L2 N N v3.6 d7 L2 cl@3,6 tg E=F|
|24|2/18|||#7 L3 E E v-8.3 d7 L3 cl@9,9 E=F; #12 L2 E E v-2.0 d7 L2 cl@1,9 E=F|
|25|2/20|||#7 L3 E E v-126.4 d7 L3 bl2@1,8 k1 E=F; #12 L2 S S v-18.9 d7 L2 cl@1,9 bl4@10,10 k0 E=F|
|26|2/19||#12 rammed L3 @1,9|#7 L3 N N v-76.2 d7 L3 grab@9,7 cl@8,9 E=F|
|27|1/20||#7 rammed L3 @10,8|#7 L3 N N v-193.0 d7 L3 E=F|

모든 head-on의 이동 주체, 길이, d3/d8, 시야 내 머리 수, 막힘 여부는 tables.json의 해당 ourGames.headons와 headons.jsonl에 있다.
