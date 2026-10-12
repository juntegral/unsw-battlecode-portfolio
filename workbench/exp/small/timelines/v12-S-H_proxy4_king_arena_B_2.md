# v12-S-H:proxy4_king:arena:B:2 (Arena, 우리 B)

기보: ~/01. Project/개인 프로젝트/unsw-swarm/exp/gen/v12-S-H/games/proxy4_king_arena_B_2/game.replay
결과: teamEliminated, 43라운드. 전멸 true; 마지막 사망 r42.
수 열세: 첫 라운드 시작 r22, 10라운드 지속 시작 r22. 사건 첫 열세 {"r":21,"kind":"split","id":6,"A":4,"B":3,"from":0,"to":-1}.

## 분열 전수

|r|부모→새끼|규칙|전→부모+새끼|머리 x,y|새끼 빈출구|새끼 사망|
|---|---|---|---|---|---|---|
|12|1→2|split: split2 u1 L4 sx t6 v k E=S|4→2+2|9,1|2|r30 rammed|
|17|1→4|split: split2 u2 L4 sx t6 k E=S|4→2+2|8,0|2|r29 rammed|
|22|2→9|split: split2 u3 L8 sx t6 k E=S|8→6+2|9,5|3|r42 rammed|
|23|2→10|split: split2 u4 L6 sx t6 k E=S|6→4+2|9,7|3|r28 rammed|
|26|10→17|split: split2 u5 L5 sx t6 v k E=S|5→3+2|9,7|2|r28 trap|
|28|2→23|escsplit: escape-split2 L4 E=S|4→2+2|10,8|2|r38 rammed|
|33|23→34|split: split2 u2 L4 sx t7 v k E=S|4→2+2|9,9|2|r37 rammed|

## 사망 전수

|r|id|원인|길이|x,y|충돌 상대|최근 분열|자기 차례 빈출구|
|---|---|---|---|---|---|---|---|
|28|10|rammed|3|8,7|0|r26 parent split|1|
|28|17|trap|2|9,5|9|r26 child split|0|
|29|4|rammed|3|9,2|5|r17 child split|2|
|30|2|rammed|3|9,7|25|r28 parent escsplit|2|
|32|1|rammed|3|9,1|13|r17 parent split|2|
|37|34|rammed|2|6,10|21|r33 child split|1|
|38|23|rammed|2|10,8|36|r33 parent split|1|
|42|9|rammed|3|10,5|14|r22 child split|2|

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
|21|3/3|8,3,2|6,4,4|
|22|3/5|8,3,2|7,3,2,2,2|
|23|4/6|6,3,2,2|4,4,4,3,3,3|
|24|5/7|4,3,3,2,2|5,5,4,4,4,3,2|
|25|5/9|4,4,3,3,2|6,5,5,4,3,3,3,2,2|
|26|5/10|5,4,3,3,2|6,6,5,4,4,4,3,3,3,2|
|27|6/12|4,3,3,3,3,2|7,6,5,4,4,4,4,3,2,2,2,2|
|28|6/16|4,3,3,3,3,2|5,4,4,4,4,3,3,3,3,3,3,3,2,2,2,2|
|29|5/17|3,3,3,2,2|4,4,4,3,3,3,3,3,3,2,2,2,2,2,2,2,2|
|30|4/18|4,3,2,2|5,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2|
|31|3/16|4,3,2|6,4,4,3,3,3,3,3,3,3,3,3,2,2,2,2|
|32|3/19|4,3,2|4,4,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2|
|33|2/18|4,2|4,4,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2|
|34|3/19|3,2,2|4,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2|
|35|3/19|3,2,2|4,4,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2|
|36|3/19|3,2,2|5,4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,2,2,2|
|37|3/23|3,2,2|4,4,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2|
|38|2/23|3,2|4,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2|
|39|1/21|3|4,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2|
|40|1/22|3|4,4,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2|
|41|1/22|3|4,4,4,4,4,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2|
|42|1/23|3|4,4,4,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2|

## 전멸 직전 20라운드 (차례 이전 상태와 실제 행동)

|r|시작 우리/적|분열|사망(위치)|우리 행동|
|---|---|---|---|---|
|23|4/6|2→10 split||#1 L3 N N v7.7 d7 L3 tg E=S; #2 L6 {"kind":"split","childSegmentCount":2} split2 u4 L6 sx t6 k E=S; #4 L2 E E v10.7 d7 L2 tg scx E=S; #9 L2 N N v8.2 d7 L2 cl@8,4 tgx E=S; #10 L2 WW WW v1.5 d7 L2 cl@8,7 tg map=none E=S|
|24|5/7|||#1 L3 E E v9.4 d7 L3 cl@8,3 E=S; #2 L4 N N v10.7 d7 L4 cl@7,8 sxc E=S; #4 L2 N N v10.4 d7 L2 cl@9,1 E=S; #9 L2 N N v7.3 d7 L2 sc E=S; #10 L3 N N v5.2 d7 L3 cl@7,6 scx E=S|
|25|5/9|||#1 L3 S S v9.4 d7 L3 cl@8,3 bl4@10,3 k0 E=S; #2 L4 N N v10.2 d7 L4 cl@8,6 sxc bl4@7,6 k1 E=S; #4 L3 E E v7.8 d7 L3 bl4@10,3 k0 E=S; #9 L2 W W v-120.2 d7 L2 cl@8,6 tg bl4@8,1 k0 E=S; #10 L4 E E v-33.4 d7 L4 cl@8,6 tg sxx bl4@10,7 k1 E=S|
|26|5/10|10→17 split||#1 L3 W W v-5.9 d7 L3 cl@6,2 scx E=S; #2 L4 N N v-22.9 d7 L4 tgx sxc E=S; #4 L3 N N v8.9 d7 L3 tg E=S; #9 L2 S S v1.1 d7 L2 cl@9,4 E=S; #10 L5 {"kind":"split","childSegmentCount":2} split2 u5 L5 sx t6 v k E=S; #17 L2 N N v3.0 d7 L2 map=none E=S|
|27|6/12|||#1 L3 N N v-10.9 d7 L3 E=S; #2 L4 N N v-23.7 d7 L4 E=S; #4 L3 W W v-0.9 d7 L3 cl@6,2 tgx E=S; #9 L3 E E v-104.8 d7 L3 tgx E=S; #10 L3 S S v-157.0 d7 L3 grab@6,7 cl@9,8 E=S; #17 L2 N N v-1104.0 d7 L2 E=S|
|28|6/16|2→23 escsplit|#10 rammed L3 @8,7; #17 trap L2 @9,5|#1 L3 E E v-22.1 d7 L3 tgx E=S; #2 L4 {"kind":"split","childSegmentCount":2} escape-split2 L4 E=S; #4 L3 S S v-4.7 d7 L3 cl@6,2 E=S; #9 L3 N N v-11.7 d7 L3 E=S; #17 L2 N no-exit E=S; #23 L2 S S v3.9 d7 L2 map=none E=S|
|29|5/17||#4 rammed L3 @9,2|#1 L3 S S v-1127.0 d7 L3 cl@8,1 E=S; #2 L2 W W v-7.1 d7 L2 grab@9,5 cl@9,8 tgx E=S; #4 L3 S S v-7.9 d7 L3 cl@6,2 E=S; #9 L3 WS WS v-8.0 d7 L3 grab@8,4 tg E=S; #23 L2 W W v-8.8 d7 L2 cl@9,8 E=S|
|30|4/18||#2 rammed L3 @9,7|#1 L4 EN EN v-46.8 d7 L4 grab@9,0 tgx sxc bl4@10,8 k1 E=S; #2 L3 SS SS v-29.5 d7 L3 grab@8,7 cl@9,7 sc bl4@8,0 k0 E=S; #9 L2 E E v7.6 d7 L2 bl4@8,1 k0 E=S; #23 L2 N N v1.7 d7 L2 cl@9,8 bl4@9,0 k0 E=S|
|31|3/16|||#1 L4 ES ES v-38.0 d7 L4 tg sxc E=S; #9 L2 S S v5.0 d7 L2 grab@9,5 tgx E=S; #23 L3 N N v-4.6 d7 L3 grab@9,7 tg E=S|
|32|3/19||#1 rammed L3 @9,1|#1 L3 W W v-36.6 d7 L3 grab@9,2 E=S; #9 L2 S S v8.5 d7 L2 grab@7,6 tgx E=S; #23 L4 E E v-47.4 d7 L4 tg sxc E=S|
|33|2/18|23→34 split||#9 L2 WN WN v-6.9 d7 L2 grab@9,5 cl@9,6 E=S; #23 L4 {"kind":"split","childSegmentCount":2} split2 u2 L4 sx t7 v k E=S; #34 L2 S S v-1.4 d7 L2 tgx map=none E=S|
|34|3/19|||#9 L3 N N v9.4 d7 L3 grab@9,2 tg E=S; #23 L2 N N v2.6 d7 L2 tgx E=S; #34 L2 W W v2.4 d7 L2 E=S|
|35|3/19|||#9 L3 E E v-14.1 d7 L3 bl4@10,6 k0 E=S; #23 L2 W W v-14.5 d7 L2 bl4@9,0 k0 E=S; #34 L2 W W v-112.1 d7 L2 bl3@10,4 k0 E=S|
|36|3/19|||#9 L3 S S v-25.2 d7 L3 cl@8,5 tgx E=S; #23 L2 S S v-3.6 d7 L2 tg E=S; #34 L2 W W v-992.6 d7 L2 cl@4,8 E=S|
|37|3/23||#34 rammed L2 @6,10|#9 L3 S S v-4.0 d7 L3 sc E=S; #23 L2 E E v-0.9 d7 L2 tg sc E=S|
|38|2/23||#23 rammed L2 @10,8|#9 L3 W W v-114.7 d7 L3 grab@8,6 E=S; #23 L2 S S v-9.0 d7 L2 E=S|
|39|1/21|||#9 L3 S S v-46.3 d7 L3 grab@10,8 E=S|
|40|1/22|||#9 L3 E E v0.8 d7 L3 grab@10,8 tg bl4@8,6 k0 E=S|
|41|1/22|||#9 L3 N N v-47.2 d7 L3 cl@9,5 tgx E=S|
|42|1/23||#9 rammed L3 @10,5|#9 L3 N N v-48.6 d7 L3 cov sc E=S|

모든 head-on의 이동 주체, 길이, d3/d8, 시야 내 머리 수, 막힘 여부는 tables.json의 해당 ourGames.headons와 headons.jsonl에 있다.
