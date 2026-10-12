# v12-S-H:proxy4_swarm:arena:B:2 (Arena, 우리 B)

기보: ~/01. Project/개인 프로젝트/unsw-swarm/exp/gen/v12-S-H/games/proxy4_swarm_arena_B_2/game.replay
결과: teamEliminated, 35라운드. 전멸 true; 마지막 사망 r34.
수 열세: 첫 라운드 시작 r22, 10라운드 지속 시작 r22. 사건 첫 열세 {"r":21,"kind":"split","id":6,"A":4,"B":3,"from":0,"to":-1}.

## 분열 전수

|r|부모→새끼|규칙|전→부모+새끼|머리 x,y|새끼 빈출구|새끼 사망|
|---|---|---|---|---|---|---|
|12|1→2|split: split2 u1 L4 sx t6 v k E=S|4→2+2|9,1|2|r24 rammed|
|17|1→4|split: split2 u2 L4 sx t6 k E=S|4→2+2|8,0|2|r34 rammed|
|21|2→7|split: split2 u3 L6 sx t6 v k E=S|6→4+2|9,5|3|r32 rammed|
|28|1→21|escsplit: escape-split3 L5 E=S|5→2+3|4,0|1|r28 rammed|

## 사망 전수

|r|id|원인|길이|x,y|충돌 상대|최근 분열|자기 차례 빈출구|
|---|---|---|---|---|---|---|---|
|24|2|rammed|4|9,5|5|r21 parent split|3|
|28|21|rammed|3|4,0|20|r28 child escsplit|첫 차례 전|
|32|1|rammed|4|2,0|12|r28 parent escsplit|2|
|32|7|rammed|4|10,1|14|r21 child split|2|
|34|4|rammed|2|4,1|29|r17 child split|2|

## 매 라운드 시작 머리 수

|r|우리/적|우리 길이|적 길이|
|---|---|---|---|
|0|1/1|3|3|
|1|1/1|2|3|
|2|1/1|2|3|
|3|1/1|2|3|
|4|1/1|2|3|
|5|1/1|2|3|
|6|1/1|2|3|
|7|1/1|2|3|
|8|1/1|2|3|
|9|1/1|2|3|
|10|1/1|3|3|
|11|1/1|3|3|
|12|1/1|4|3|
|13|2/1|2,2|3|
|14|2/1|2,2|3|
|15|2/1|2,2|3|
|16|2/1|3,3|4|
|17|2/2|4,4|3,2|
|18|3/2|5,2,2|4,3|
|19|3/3|6,2,2|4,2,2|
|20|3/3|7,3,2|5,3,3|
|21|3/3|6,3,2|6,4,4|
|22|4/6|4,3,2,2|4,3,3,2,2,2|
|23|4/7|4,3,2,2|4,4,3,3,3,3,2|
|24|4/8|4,4,2,2|4,4,4,4,4,3,3,2|
|25|3/10|4,2,2|4,4,4,3,3,2,2,2,2,2|
|26|3/11|4,3,2|5,4,4,4,3,3,3,3,2,2,2|
|27|3/13|4,2,2|6,5,4,4,4,3,3,3,3,3,2,2,2|
|28|3/15|5,2,2|5,4,4,4,4,4,4,3,3,3,3,3,2,2,2|
|29|3/18|2,2,2|5,4,4,4,3,3,3,3,3,2,2,2,2,2,2,2,2,2|
|30|3/20|3,2,2|5,4,4,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2|
|31|3/20|4,3,2|4,4,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2|
|32|3/21|4,4,2|4,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2|
|33|1/19|2|4,4,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2|
|34|1/20|2|4,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2|

## 전멸 직전 20라운드 (차례 이전 상태와 실제 행동)

|r|시작 우리/적|분열|사망(위치)|우리 행동|
|---|---|---|---|---|
|15|2/1|||#1 L2 S S v13.4 d7 L2 cl@9,1 bl2@10,3 k1 E=S; #2 L2 WS WS v16.7 d7 L2 cl@9,3 bl3@9,1 k0 E=S|
|16|2/1|||#1 L3 S S v13.3 d7 L3 cl@9,2 E=S; #2 L3 S S v18.7 d7 L3 cl@9,5 sc E=S|
|17|2/2|1→4 split||#1 L4 {"kind":"split","childSegmentCount":2} split2 u2 L4 sx t6 k E=S; #2 L4 S S v19.0 d7 L4 cl@9,6 sxx E=S; #4 L2 S S v5.5 d7 L2 cl@7,1 tgx map=none E=S|
|18|3/2|||#1 L2 W W v12.5 d7 L2 cl@7,2 E=S; #2 L5 S S v18.2 d7 L5 sxx E=S; #4 L2 E E v12.4 d7 L2 tg E=S|
|19|3/3|||#1 L2 WN WN v6.7 d7 L2 cl@7,2 tg E=S; #2 L6 S S v9.7 d7 L6 tg sxx scx E=S; #4 L2 N N v14.1 d7 L2 E=S|
|20|3/3|||#1 L3 N N v7.3 d7 L3 tg bl4@9,5 k0 E=S; #2 L7 EN EN v6.3 d7 L7 tg sxc sc bl4@9,0 k1 E=S; #4 L2 W W v15.0 d7 L2 cl@8,3 bl6@10,7 k0 E=S|
|21|3/3|2→7 split||#1 L3 W W v8.8 d7 L3 cl@6,1 tg E=S; #2 L6 {"kind":"split","childSegmentCount":2} split2 u3 L6 sx t6 v k E=S; #4 L2 S S v13.5 d7 L2 cl@8,3 E=S; #7 L2 E E v5.9 d7 L2 tgx map=none E=S|
|22|4/6|||#1 L3 W W v9.1 d7 L3 cl@5,1 tg E=S; #2 L4 N N v-62.2 d7 L4 cl@8,6 tgx sxc E=S; #4 L2 E E v11.0 d7 L2 tg scx E=S; #7 L2 N N v14.7 d7 L2 E=S|
|23|4/7|||#1 L3 SW SW v-9.9 d7 L3 cl@5,1 tg E=S; #2 L4 W W v-43.9 d7 L4 cl@8,6 sxc E=S; #4 L2 N N v6.0 d7 L2 sc E=S; #7 L2 N N v10.2 d7 L2 E=S|
|24|4/8||#2 rammed L4 @9,5|#1 L4 N N v-38.0 d7 L4 sxx E=S; #2 L4 N N v-63.8 d7 L4 sxc E=S; #4 L2 W W v-0.4 d7 L2 cl@8,3 E=S; #7 L2 N N v-3.0 d7 L2 E=S|
|25|3/10|||#1 L4 W W v-62.5 d7 L4 cl@3,1 sxc bl6@10,7 k0 E=S; #4 L2 W W v-12.5 d7 L2 cl@6,1 tgx bl4@10,2 k0 E=S; #7 L2 W W v0.1 d7 L2 grab@9,5 cl@9,2 tg bl4@9,6 k0 E=S|
|26|3/11|||#1 L4 WS WS v-77.2 d7 L4 cl@2,1 sxx E=S; #4 L2 S S v12.1 d7 L2 cl@6,1 E=S; #7 L3 NN NN v8.1 d7 L3 tg E=S|
|27|3/13|||#1 L4 E E v-32.3 d7 L4 cl@3,1 sxc scx E=S; #4 L2 WW WW v10.3 d7 L2 cl@6,1 sc E=S; #7 L2 W W v5.7 d7 L2 grab@7,4 cl@8,2 E=S|
|28|3/15|1→21 escsplit|#21 rammed L3 @4,0|#1 L5 {"kind":"split","childSegmentCount":3} escape-split3 L5 E=S; #4 L2 N N v-18.2 d7 L2 E=S; #7 L2 W W v8.4 d7 L2 grab@7,4 tg E=S|
|29|3/18|||#1 L2 N N v-14.6 d7 L2 grab@2,0 E=S; #4 L2 E E v-19.7 d7 L2 tgx E=S; #7 L2 S S v-2.1 d7 L2 grab@7,4 cl@7,1 E=S|
|30|3/20|||#1 L2 ES ES v-12.8 d7 L2 grab@4,0 tg bl6@10,7 k0 E=S; #4 L2 S S v-719.6 d7 L2 bl4@4,1 k0 E=S; #7 L3 E E v-27.2 d7 L3 grab@8,5 cl@8,1 bl4@9,6 k0 E=S|
|31|3/20|||#1 L3 W W v-28.9 d7 L3 grab@2,0 cl@3,1 E=S; #4 L2 W W v-24.4 d7 L2 grab@2,0 E=S; #7 L4 E E v-53.6 d7 L4 sxc E=S|
|32|3/21||#1 rammed L4 @2,0; #7 rammed L4 @10,1|#1 L4 WN WN v-47.8 d7 L4 grab@2,0 sxc scx E=S; #4 L2 N N v-10.1 d7 L2 E=S; #7 L4 E E v-76.1 d7 L4 sxx E=S|
|33|1/19|||#4 L2 W W v-53.4 d7 L2 grab@2,0 E=S|
|34|1/20||#4 rammed L2 @4,1|#4 L2 S S v-83.9 d7 L2 grab@8,1 E=S|

모든 head-on의 이동 주체, 길이, d3/d8, 시야 내 머리 수, 막힘 여부는 tables.json의 해당 ourGames.headons와 headons.jsonl에 있다.
