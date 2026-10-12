# agg7 온라인 재집계

생성: 2026-10-08T18:36:07+09:00. 팀 1119. 발견: agg7-m1, agg7-m2, agg7-m3, agg7-b1, agg7-b2, agg8-q1, sr51-bob1.
미도착: agg8-q2, agg9-a1. 현재 자료에서 누락 판 없음.
검증: 195판 각각 1회; 로그 대조 agg7-m1:passed; agg7-m2:passed; agg7-m3:passed; agg7-b1:passed; agg7-b2:passed; agg8-q1:passed; sr51-bob1:passed. 원자료/봇 코드 변경 없음. sr51-bob1은 모든 MAIN/B7/B7Q/B10 비교에서 제외.

## 1. 결과

| arm / 상대 | 판/승 | 우리/상대 최종 총길이 평균 | 결정 Q/L/T/E | 여왕 생존/평균 길이 |
|---|---:|---:|---|---:|
| MAIN / Big Bobs Bots | 45/16 | 66.8/120.7 | 20/7/0/18 | 10/1.29 |
| MAIN / WeHaveQuizzes | 45/5 | 63.8/155.8 | 14/13/0/18 | 6/2.42 |
| B7 / Big Bobs Bots | 30/16 | 105.5/89.6 | 10/10/0/10 | 6/2.87 |
| B7 / WeHaveQuizzes | 30/7 | 104.7/129.1 | 9/9/0/12 | 5/0.50 |
| B7Q / Big Bobs Bots | 15/8 | 110.4/82.5 | 8/2/0/5 | 5/4.93 |
| B7Q / WeHaveQuizzes | 15/6 | 115.1/105.9 | 4/4/1/6 | 3/3.47 |
| B10 / 자료 없음 | 0/0 | NA | 0/0/0/0 | NA |
| OLD / Big Bobs Bots | 15/6 | 90.3/117.5 | 7/4/0/4 | 2/1.67 |
Q=여왕 길이, L=최장, T=총길이, E=전멸. 여왕 평균은 죽은 여왕 0 포함.
| 짝 (회차+상대+지도) / 크기 | n | 둘 승/둘 패/B7만/MAIN만/무승부 포함 | 양측 sign p |
|---|---:|---|---:|
| 전체 | 60 | 11/34/12/3/0 | 0.035 |
| 회차 1 | 30 | 4/18/5/3/0 | 0.727 |
| 회차 2 | 30 | 7/16/7/0/0 | 0.016 |
| Big Bobs Bots | 30 | 8/12/8/2/0 | 0.109 |
| WeHaveQuizzes | 30 | 3/22/4/1/0 | 0.375 |
| <=700 | 24 | 8/11/4/1/0 | 0.375 |
| 701-1200 | 16 | 3/8/4/1/0 | 0.375 |
| >1200 | 20 | 0/15/4/1/0 | 0.375 |
B7Q–MAIN 짝: q1↔m2, q2↔m3 (각각 바로 뒤 실행).
| B7Q–MAIN / 크기 | n | 둘 승/둘 패/B7Q만/MAIN만/무승부 포함 | 양측 sign p |
|---|---:|---|---:|
| 전체<br>q1↔m2<br>q2↔m3<br>Big Bobs Bots<br>WeHaveQuizzes<br><=700<br>701-1200<br>>1200 | 30<br>30<br>0<br>15<br>15<br>12<br>8<br>10 | 4/13/10/3/0<br>4/13/10/3/0<br>0/0/0/0/0<br>2/4/6/3/0<br>2/9/4/0/0<br>4/6/1/1/0<br>0/1/5/2/0<br>0/6/4/0/0 | 0.092<br>0.092<br>NA<br>0.508<br>0.125<br>1.000<br>0.453<br>0.125 |
B7Q–B7: 시간대가 다름. 모든 회차를 (상대, 지도)별 합산; 지도별 승률 비교(동률은 승률 0/1/혼합으로 구분), sign은 공유 지도 단위.
| B7Q–B7 합산 / 크기 | 공유 지도 | B7Q 판/승 | B7 판/승 | Q만 우세/B만 우세/동률(0/1/혼합) | 양측 sign p |
|---|---:|---:|---:|---|---:|
| 전체<br>Big Bobs Bots<br>WeHaveQuizzes<br><=700<br>701-1200<br>>1200 | 30<br>15<br>15<br>12<br>8<br>10 | 30/14<br>15/8<br>15/6<br>12/5<br>8/5<br>10/4 | 60/23<br>30/16<br>30/7<br>24/12<br>16/7<br>20/4 | 8/5/11/6/0<br>4/4/3/4/0<br>4/1/8/2/0<br>1/2/5/4/0<br>3/2/1/2/0<br>4/1/5/0/0 | 0.581<br>1.000<br>0.375<br>1.000<br>1.000<br>0.375 |
B10–B7Q 짝 (시간대가 다름): (상대, 지도). agg8-q1과 비교.
| B10–B7Q / 크기 | n | 둘 승/둘 패/B10만/B7Q만/무승부 포함 | 양측 sign p |
|---|---:|---|---:|
| 전체 (합산)<br>agg8-q1<br>Big Bobs Bots<br>WeHaveQuizzes<br><=700<br>701-1200<br>>1200 | 0<br>0<br>0<br>0<br>0<br>0<br>0 | 0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0 | NA<br>NA<br>NA<br>NA<br>NA<br>NA<br>NA |
B10–MAIN 짝 (시간대가 다름): (상대, 지도). MAIN 합산은 회차별 짝을 합침(같은 B10 판은 회차마다 재사용).
| B10–MAIN / 크기 | n | 둘 승/둘 패/B10만/MAIN만/무승부 포함 | 양측 sign p |
|---|---:|---|---:|
| 전체 (합산)<br>agg7-m1<br>agg7-m2<br>agg7-m3<br>Big Bobs Bots<br>WeHaveQuizzes<br><=700<br>701-1200<br>>1200 | 0<br>0<br>0<br>0<br>0<br>0<br>0<br>0<br>0 | 0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0<br>0/0/0/0/0 | NA<br>NA<br>NA<br>NA<br>NA<br>NA<br>NA<br>NA<br>NA |

| 크기 | MAIN 판/승 | B7 판/승 | B7Q 판/승 | B10 판/승 |
|---|---:|---:|---:|---:|
| <=700 | 36/14 | 24/12 | 12/5 | 0/0 |
| 701-1200 | 24/5 | 16/7 | 8/5 | 0/0 |
| >1200 | 30/2 | 20/4 | 10/4 | 0/0 |
여왕 (MAIN/B7/B7Q/B10): r100/150/300/종료는 라운드 끝(조기 종료는 최종 유지); 길이 평균은 생존 판만. 턴 비율은 0≤r≤300 차례 시작 길이, 합산 분모. 일상/탈출 분기는 기보에 없어 일상 분열은 NA; 자식 L2 분열은 일상 후보이며 탈출·대기도 포함. 개별 분열 직후 길이는 JSON queen_splits에 전부 보존.
| 여왕 지표 | MAIN | B7 | B7Q | B10 |
|---|---|---|---|---|
| 생존 판/전체; 생존 평균 L (r100;150;300;종료) | 100: 51/90; L2.569<br>150: 38/90; L2.658<br>300: 22/90; L3.227<br>end: 16/90; L10.438 | 100: 34/60; L2.559<br>150: 22/60; L2.545<br>300: 14/60; L3.429<br>end: 11/60; L9.182 | 100: 19/30; L3.211<br>150: 11/30; L3.455<br>300: 9/30; L7.333<br>end: 8/30; L15.750 | 100: NA (0판)<br>150: NA (0판)<br>300: NA (0판)<br>end: NA (0판) |
| 턴 L2/L3/L4+ (%) / 전체 여왕 턴 0-300 | 40.252/53.677/6.072 / 13423 | 41.063/53.080/5.857 / 8263 | 9.286/47.447/43.266 / 4329 | NA/NA/NA / 0 |
| 일상 분열/판; 직후 여왕 L:횟수 (전체 게임 창) | 일상 NA; L2자식 후보 3.378/판 (L2:225,L3:16,L4:2,L5:6,L7:6,L9:6,L11:6,L13:6,L15:6,L17:6,L19:6,L21:6,L22:1,L23:6); 전체 3.378/판 (L2:225,L3:16,L4:2,L5:6,L7:6,L9:6,L11:6,L13:6,L15:6,L17:6,L19:6,L21:6,L22:1,L23:6) | 일상 NA; L2자식 후보 3.983/판 (L2:185,L3:10,L5:4,L7:4,L9:4,L11:4,L13:4,L15:4,L17:4,L19:4,L21:4,L22:2,L23:4,L24:1,L41:1); 전체 4.000/판 (L2:186,L3:10,L5:4,L7:4,L9:4,L11:4,L13:4,L15:4,L17:4,L19:4,L21:4,L22:2,L23:4,L24:1,L41:1) | 일상 NA; L2자식 후보 4.767/판 (L2:26,L3:62,L4:5,L5:2,L7:2,L9:2,L11:2,L13:2,L15:2,L17:2,L19:2,L21:2,L23:2,L27:1,L29:1,L31:1,L33:1,L35:1,L37:1,L39:1,L41:1,L43:1,L45:1,L47:1,L49:2,L51:2,L53:1,L55:1,L57:1,L59:1,L61:2,L63:1,L65:1,L67:1,L69:1,L71:1,L73:1,L75:1,L77:1,L78:1); 전체 4.767/판 (L2:26,L3:62,L4:5,L5:2,L7:2,L9:2,L11:2,L13:2,L15:2,L17:2,L19:2,L21:2,L23:2,L27:1,L29:1,L31:1,L33:1,L35:1,L37:1,L39:1,L41:1,L43:1,L45:1,L47:1,L49:2,L51:2,L53:1,L55:1,L57:1,L59:1,L61:2,L63:1,L65:1,L67:1,L69:1,L71:1,L73:1,L75:1,L77:1,L78:1) | NA (0판) |
| 사망 원인별 건수 (사망 L:횟수) | another body 1건 (L2:1); head-on hit 49건 (L2:33,L3:10,L4:1,L5:1,L6:1,L37:1,L38:1,L40:1); head-on mover 4건 (L2:4); own body 5건 (L2:2,L3:3); wall 15건 (L2:9,L3:6) | another body 3건 (L3:3); head-on hit 25건 (L2:18,L3:4,L4:2,L11:1); head-on mover 2건 (L2:2); own body 8건 (L2:5,L3:3); wall 11건 (L2:5,L3:6) | head-on hit 13건 (L2:8,L3:3,L4:2); head-on mover 3건 (L2:2,L3:1); own body 1건 (L2:1); wall 5건 (L2:1,L3:4) | NA (0판) |
| 여왕 길이 결정 판/승/패; 직접 분열 자식 수/판 (전체 게임 창) | 34판 / 1승 / 33패; 자식 304명 / 3.378명/판 | 19판 / 2승 / 17패; 자식 240명 / 4.000명/판 | 12판 / 3승 / 9패; 자식 143명 / 4.767명/판 | NA (0판); 자식 NA (0판) |

## 2. 행동 (R=1위, O=우리 래더; * R에 가까워짐, ! 멀어짐)

온라인은 합산 분자/분모; 체크포인트는 판 평균(조기 종료는 최종 상태 유지). 래더 R/O는 기존 동일 지도 가중 평균; 상대·시간대가 달라 인과 비교가 아니다.
NA=자료/분모 없음. 기존 래더에 없는 작은 용 섭취·정확 타이머·순길이 지표의 R/O는 NA; 방향 표식도 생략. 체크포인트 R/O는 판 평균. 두 창 행의 세미콜론은 0-100;101-300 순서다.
생성 타이머 없는 온라인 기보 195/195판: kind-2 사건이 없어 c1·c2 기회와 성공률 복원 불가(0건이 아님).
| 지표 / 창 | R | O | MAIN | B7 | B7Q | B10 |
|---|---:|---:|---:|---:|---:|---:|
| L2-3 섭취 /1k turns / game | NA | NA | 46.361 | 51.453 | 52.405 | NA |
| c1 생성칸 밟음 % / 0-300 | NA | NA | NA | NA | NA | NA |
| c2 두 칸 밖에서 생성 % / 0-300 | NA | NA | NA | NA | NA | NA |
| 전체 섭취 /1k turns / game | 84.060 | 58.816 | 59.956 | 65.203* | 65.849* | NA |
| 자연 진주 섭취/생성 / game | NA | NA | 0.359 | 0.445 | 0.452 | NA |
| 생성→섭취 대기 / game | NA | NA | 9.402 | 8.608 | 8.480 | NA |
| Split frequency / game | 30.580 | 22.661 | 22.480 | 24.553* | 25.107* | NA |
| Head-on meetings started / game | NA | NA | 1.293 | 1.902 | 1.766 | NA |
| alive / 100 | 23.987 | 23.576 | 24.900 | 27.817! | 26.100! | NA |
| alive / 300 | 34.983 | 30.248 | 26.867 | 35.367* | 36.233* | NA |
| longest / 300 | 9.678 | 9.334 | 7.156 | 10.367* | 11.267* | NA |
| longest / end | 29.985 | 24.148 | 17.911 | 28.567* | 26.100* | NA |
| 순길이 (섭취−사망 길이) /1k turns / game | NA | NA | 5.571 | 7.725 | 8.082 | NA |
| Natural birth-cohort harvest / 0-100;101-300 | 53.448;57.070 | 46.764;43.548 | 45.900;38.176 | 48.767*;45.292* | 46.338*;47.185* | NA;NA |
| Birth-cohort wait until eaten / 0-100;101-300 | 17.058;5.505 | 26.550;8.660 | 14.583;7.043 | 15.754*;6.917* | 16.887*;6.718* | NA;NA |
| Split frequency / 0-100;101-300 | 39.570;28.904 | 30.702;21.072 | 34.481;21.172 | 35.774*;23.577* | 36.704*;24.653* | NA;NA |
| Head-on meetings started / 0-100;101-300 | 4.272;4.189 | 2.186;1.991 | 1.172;1.458 | 1.854*;2.350* | 1.827*;2.139* | NA;NA |
| Death: head-on mover / 0-100;101-300 | 4.272;4.189 | 2.186;1.991 | 1.172;1.458 | 1.854*;2.350* | 1.827*;2.139* | NA;NA |
| Death: head-on hit / 0-100;101-300 | 2.763;2.965 | 2.711;3.306 | 3.465;4.578 | 3.342*;4.233* | 3.722!;4.068* | NA;NA |
| Death: wall / 0-100;101-300 | 0.000;0.000 | 8.315;7.273 | 9.082;7.657 | 8.579*;6.853* | 9.204!;7.506* | NA;NA |
| Death: own body / 0-100;101-300 | 0.005;0.008 | 3.153;3.436 | 3.806;3.565 | 4.085!;3.386* | 3.767*;3.466* | NA;NA |
| Death: another body / 0-100;101-300 | 0.298;0.479 | 1.889;2.465 | 2.909;2.937 | 2.860*;3.046! | 3.136!;2.979! | NA;NA |
| Death: no action / 0-100;101-300 | 0.000;0.000 | 0.000;0.639 | 0.000;0.591 | 0.000=;2.404! | 0.000=;2.814! | NA;NA |
| Death: unpaid sprint / 0-100;101-300 | 0.000;0.000 | 0.000;0.000 | 0.000;0.000 | 0.000=;0.000= | 0.000=;0.000= | NA;NA |
| Death: illegal split / 0-100;101-300 | 18.111;18.792 | 0.000;0.000 | 0.000;0.000 | 0.000=;0.000= | 0.000=;0.000= | NA;NA |
| Death: timeout / 0-100;101-300 | 0.000;0.000 | 0.000;0.000 | 0.000;0.000 | 0.000=;0.000= | 0.000=;0.000= | NA;NA |

## 3. 스위치 관련 사건

아래는 브리프의 관측 조건에 맞는 사건이며 독점 발동 증명은 아니다: MAIN도 만들 수 있고 로그에 스위치 실행 표식이 없다. 두 포털 스위치는 같은 사건으로 분리 불가.
| 스위치 | MAIN | B7 | B7Q | B10 |
|---|---|---|---|---|
| SPAWN_CLEAR c1 on/case; c2 born/case | NA (타이머 없음) | NA (타이머 없음) | NA (타이머 없음) | NA (0판) |
| ZONE_NEARER | 2439 | 2628 | 1572 | NA (0판) |
| TRADE_EVEN | 492 | 704 | 341 | NA (0판) |
| HUNT_SMALL_RATIO | 170 | 242 | 101 | NA (0판) |
| POCKET_LOOP | 1730 | 1089 | 594 | NA (0판) |
| HARVEST_PORTAL | 1730 | 1089 | 594 | NA (0판) |
| TRADE_SHORT_BY (L3/L4/L5+; 동길이/2+ 짧음) | 89/10/4 (10건 미만: 읽기 작음)/488/17 | 57/13/1 (10건 미만: 읽기 작음)/703/13 | 26/9 (10건 미만: 읽기 작음)/1 (10건 미만: 읽기 작음)/339/6 (10건 미만: 읽기 작음) | NA (0판)/NA (0판)/NA (0판)/NA (0판)/NA (0판) |
| LUNGE_PEARL / 전체 paid-sprint hits | 3 (10건 미만: 읽기 작음)/220 | 6 (10건 미만: 읽기 작음)/348 | 3 (10건 미만: 읽기 작음)/159 | NA (0판)/NA (0판) |
| FEEDER_EAT | 440 | 342 | 174 | NA (0판) |
| QS_KEEP_LEN 3 (자식 L2·직후 Q<3; 일상/탈출 미분리) | 225 | 185 | 26 | NA (0판) |
| LEADER_FULL_UNITS (>1200, L>10 & 수<56 첫 r) | 1397917:r254; 1397918:r236; 1397922:r215; 1397925:r84; 1397930:r0; 1398177:r202; 1398178:r187; 1398182:r186; 1398185:r179; 1398190:r0; 1415577:r248; 1415578:r176; 1415582:r176; 1415585:r169; 1415590:r0; 1415983:r185; 1415984:r170; 1415988:r204; 1415991:r162; 1415996:r0; 1426392:r214; 1426393:r229; 1426397:r245; 1426400:r160; 1426405:r0; 1426889:r215; 1426890:r172; 1426894:r215; 1426897:r330; 1426902:r0 | 1403107:r260; 1403108:r176; 1403112:r209; 1403115:r452; 1403120:r0; 1403639:r447; 1403640:r204; 1403644:r208; 1403647:r176; 1403652:r0; 1408112:r235; 1408113:r190; 1408117:r190; 1408120:r211; 1408125:r0; 1408543:r365; 1408544:r163; 1408548:r217; 1408551:r90; 1408556:r0 | 1421767:r236; 1421768:r206; 1421772:r226; 1421775:r204; 1421780:r0; 1422309:r318; 1422310:r419; 1422314:r209; 1422317:r91; 1422322:r0 | NA (0판) |
TRADE_SHORT_BY: 비여왕 아군이 시작한 적 머리 충돌; 충돌 시 우리 길이 3/4/5+에서 적이 정확히 1 짧음, 같은 모집단의 동길이/2 이상 짧음도 집계.
LUNGE_PEARL: 적 머리 충돌 걸음이 시작 길이 ceil(L/4)를 넘고, 그 차례의 유료 이동 걸음에서 진주를 먹은 충돌/전체 유료 충돌(여왕 포함).
FEEDER_EAT: 섭취 차례 시작에 비여왕·최장보다 짧은 아군이 사망 전 0–3라운드에 먹은 진주 중, 그 사망 낙하 진주가 사망 후 0–3라운드에 차례 시작 최장 아군에게 먹힌 경우를 1회씩 집계; 내부 feed_index·흡수 의도는 복원 불가.
ZONE 거리=시작 머리와 진주의 토러스 맨해튼; 최장 동률은 최소 id. 리더 r=작은 지도 300, 큰 지도 150. TRADE 길이는 충돌 시점, 수는 차례 시작·실제 UNIT_LIMIT 기준.

## 4. 패배 해부 (MAIN/B7/B7Q/B10 분리; OLD는 상세 JSON에 보존)

항목: game 지도; 결정; Q 사망 r/원인/L/아군5; 충돌 상대 id:L(시작 L), 차례 시작 머리→충돌 칸 최단 열린 변·포털 거리 d/실제 걸음 k; 영구 역전 r(라운드 끝); r300 이후 최장 피격 r:L.
| arm / 상대 | 각 패배 (상대별, 판마다 줄바꿈) |
|---|---|
| MAIN / Big Bobs Bots | 1397916 weakhold; queen_length; Q r98/head-on hit/L2/a0 ←#17:L3(시작4),d3/k3; queen_length↑98; late [[451, 10]]<br>1397917 Australia; queen_length; Q r57/head-on hit/L2/a0 ←#34:L3(시작3),d2/k2; queen_length↑57; late 없음<br>1397918 Islands; queen_length; Q r130/head-on mover/L2/a1 ←#5:L2(시작2),d1/k1; queen_length↑130; late [[351, 4]]<br>1397919 Maze; queen_length; Q r142/head-on hit/L2/a2 ←#49:L2(시작2),d1/k1; queen_length↑141; late [[321, 3], [450, 5]]<br>1397921 Tower Defense; elimination; Q r277/head-on hit/L2/a2 ←#46:L2(시작2),d1/k1; longest↑324; late [[327, 3], [360, 2]]<br>1397922 Around UNSW; queen_length; Q r185/head-on hit/L2/a2 ←#296:L5(시작5),d3/k3; queen_length↑185; late [[441, 25], [473, 10], [482, 15], [486, 11]]<br>1397923 Default; longest; Q r25/head-on hit/L2/a2 ←#2:L3(시작3),d2/k2; longest↑492; late [[317, 15]]<br>1397928 Trauma; queen_length; Q r474/head-on hit/L40/a1 ←#320:L3(시작5),d3/k5; queen_length↑474; late [[310, 4], [474, 40]]<br>1397929 Portals; queen_length; Q r62/wall/L2/a2; queen_length↑61; late 없음<br>1397930 Slithery Fight; queen_length; Q r92/head-on hit/L3/a1 ←#285:L3(시작4),d3/k3; queen_length↑92; late [[387, 12], [391, 8]]<br>1415576 weakhold; queen_length; Q r111/head-on hit/L2/a0 ←#20:L2(시작2),d1/k1; queen_length↑111; late [[333, 8], [389, 3]]<br>1415577 Australia; elimination; Q r318/head-on hit/L2/a1 ←#357:L4(시작5),d4/k4; longest↑380; late [[359, 14], [368, 18], [427, 12], [444, 5]]<br>1415578 Islands; elimination; Q r90/head-on hit/L2/a2 ←#19:L2(시작2),d1/k1; longest↑386; late [[316, 10], [357, 8], [386, 7]]<br>1415580 Stripes; elimination; Q r97/wall/L2/a2; longest↑141; late 없음<br>1415582 Around UNSW; queen_length; Q r107/head-on hit/L2/a1 ←#128:L4(시작5),d5/k5; queen_length↑61; late [[390, 11], [420, 13]]<br>1415584 Queen Of Spades; queen_length; Q r56/head-on mover/L2/a0 ←#8:L2(시작2),d1/k1; queen_length↑56; late [[326, 7]]<br>1415585 Schooltime; longest; Q 생존; longest↑480; late [[480, 59]]<br>1415588 Trauma; queen_length; Q r427/head-on hit/L37/a0 ←#109:L4(시작5),d4/k4; queen_length↑427; late [[427, 37]]<br>1415589 Portals; queen_length; Q r60/wall/L3/a1; queen_length↑60; late 없음<br>1415590 Slithery Fight; queen_length; Q r361/head-on hit/L38/a0 ←#696:L4(시작5),d4/k4; queen_length↑361; late [[307, 9], [361, 38]]<br>1426391 weakhold; queen_length; Q r114/head-on hit/L2/a0 ←#63:L4(시작4),d4/k4; queen_length↑114; late 없음<br>1426392 Australia; queen_length; Q r240/head-on hit/L6/a0 ←#286:L3(시작4),d4/k4; queen_length↑240; late 없음<br>1426393 Islands; elimination; Q r90/head-on hit/L3/a0 ←#79:L4(시작6),d3/k5; longest↑328; late [[328, 9], [381, 6], [394, 2]]<br>1426394 Maze; queen_length; Q r65/head-on mover/L2/a0 ←#38:L2(시작2),d1/k1; queen_length↑52; late 없음<br>1426397 Around UNSW; queen_length; Q r83/head-on hit/L2/a2 ←#16:L4(시작5),d4/k4; queen_length↑76; late [[428, 24]]<br>1426398 Default; longest; Q r62/head-on hit/L2/a0 ←#8:L3(시작3),d2/k2; longest↑495; late 없음<br>1426399 Queen Of Spades; elimination; Q r309/head-on hit/L2/a1 ←#56:L5(시작6),d4/k4; longest↑300; late [[306, 4], [309, 2], [311, 2], [316, 2], [325, 3]]<br>1426401 Trophy; elimination; Q r26/head-on hit/L2/a0 ←#2:L3(시작3),d3/k3; longest↑180; late 없음<br>1426405 Slithery Fight; queen_length; Q r256/own body/L3/a6; queen_length↑256; late [[432, 42]] |
| MAIN / WeHaveQuizzes | 1398176 weakhold; longest; Q r280/head-on hit/L2/a0 ←#228:L3(시작3),d2/k2; longest↑405; late [[404, 12], [419, 3]]<br>1398177 Australia; queen_length; Q r227/head-on hit/L2/a0 ←#19:L3(시작3),d2/k2; queen_length↑99; late 없음<br>1398178 Islands; longest; Q r90/head-on hit/L2/a1 ←#84:L3(시작3),d2/k2; longest↑243; late [[358, 10], [387, 9], [405, 6]]<br>1398179 Maze; longest; Q r53/wall/L2/a2; longest↑338; late [[346, 7]]<br>1398180 Stripes; elimination; Q r62/head-on hit/L2/a1 ←#6:L3(시작3),d2/k2; longest↑74; late 없음<br>1398181 Tower Defense; elimination; Q r108/head-on hit/L3/a0 ←#4:L3(시작3),d2/k2; longest↑109; late 없음<br>1398182 Around UNSW; longest; Q r79/head-on hit/L5/a0 ←#5:L3(시작3),d4/k4; longest↑362; late [[362, 26]]<br>1398184 Queen Of Spades; elimination; Q r75/head-on hit/L3/a0 ←#12:L3(시작3),d2/k2; longest↑148; late 없음<br>1398185 Schooltime; longest; Q 생존; longest↑112; late [[342, 14], [447, 16], [453, 3]]<br>1398186 Trophy; elimination; Q r23/head-on hit/L3/a2 ←#6:L3(시작3),d3/k5; longest↑95; late 없음<br>1398188 Trauma; queen_length; Q 생존; queen_length↑243; late [[307, 5]]<br>1398189 Portals; queen_length; Q r101/own body/L3/a1; queen_length↑101; late 없음<br>1398190 Slithery Fight; queen_length; Q r186/wall/L2/a5; queen_length↑183; late [[340, 32]]<br>1415983 Australia; queen_length; Q r137/head-on hit/L2/a0 ←#18:L3(시작4),d3/k3; queen_length↑93; late [[306, 8], [343, 15], [426, 12]]<br>1415984 Islands; longest; Q r198/head-on hit/L3/a0 ←#297:L3(시작4),d4/k4; longest↑199; late [[319, 11], [325, 6]]<br>1415985 Maze; queen_length; Q r145/head-on hit/L2/a0 ←#164:L3(시작3),d2/k2; queen_length↑131; late 없음<br>1415986 Stripes; elimination; Q r74/wall/L3/a0; longest↑72; late 없음<br>1415987 Tower Defense; elimination; Q r112/head-on hit/L2/a0 ←#29:L2(시작2),d1/k1; longest↑67; late 없음<br>1415988 Around UNSW; queen_length; Q r33/head-on hit/L4/a3 ←#65:L3(시작2),d2/k2; queen_length↑33; late 없음<br>1415989 Default; elimination; Q r174/head-on hit/L2/a0 ←#77:L3(시작3),d3/k3; longest↑381; late [[303, 3], [338, 8], [430, 6]]<br>1415990 Queen Of Spades; elimination; Q r128/head-on hit/L2/a0 ←#21:L2(시작2),d1/k1; longest↑87; late 없음<br>1415991 Schooltime; longest; Q 생존; longest↑328; late 없음<br>1415993 Devil; elimination; Q r51/head-on hit/L2/a0 ←#19:L3(시작2),d2/k2; longest↑146; late 없음<br>1415994 Trauma; queen_length; Q 생존; queen_length↑272; late 없음<br>1415995 Portals; queen_length; Q r77/wall/L2/a1; queen_length↑77; late 없음<br>1415996 Slithery Fight; queen_length; Q r265/own body/L2/a2; queen_length↑213; late [[349, 22]]<br>1426888 weakhold; longest; Q r118/head-on hit/L2/a1 ←#63:L3(시작3),d3/k3; longest↑379; late [[314, 3], [343, 3], [379, 7], [474, 9]]<br>1426889 Australia; longest; Q r152/head-on mover/L2/a0 ←#177:L2(시작2),d1/k1; longest↑139; late [[356, 11]]<br>1426890 Islands; longest; Q r49/head-on hit/L3/a0 ←#3:L4(시작4),d2/k2; longest↑327; late [[327, 18]]<br>1426891 Maze; queen_length; Q r99/another body/L2/a2; queen_length↑99; late [[330, 10]]<br>1426892 Stripes; elimination; Q r57/wall/L3/a0; longest↑57; late 없음<br>1426893 Tower Defense; elimination; Q r109/wall/L2/a1; longest↑108; late 없음<br>1426894 Around UNSW; longest; Q r37/head-on hit/L3/a1 ←#25:L5(시작4),d3/k3; longest↑264; late [[376, 17]]<br>1426895 Default; elimination; Q r92/head-on hit/L2/a1 ←#46:L2(시작2),d1/k1; longest↑151; late 없음<br>1426896 Queen Of Spades; elimination; Q r154/head-on hit/L2/a0 ←#16:L3(시작3),d2/k2; longest↑142; late 없음<br>1426897 Schooltime; longest; Q 생존; longest↑222; late 없음<br>1426898 Trophy; elimination; Q r32/head-on hit/L3/a1 ←#15:L3(시작4),d3/k3; longest↑93; late 없음<br>1426900 Trauma; queen_length; Q 생존; queen_length↑277; late 없음<br>1426901 Portals; queen_length; Q r39/wall/L2/a2; queen_length↑38; late 없음<br>1426902 Slithery Fight; queen_length; Q r312/wall/L3/a4; queen_length↑171; late [[302, 10]] |
| B7 / Big Bobs Bots | 1403106 weakhold; queen_length; Q r104/own body/L2/a1; queen_length↑104; late 없음<br>1403107 Australia; longest; Q r67/head-on hit/L2/a0 ←#2:L3(시작3),d3/k3; longest↑378; late [[440, 13]]<br>1403108 Islands; longest; Q r125/head-on hit/L2/a4 ←#205:L2(시작2),d1/k1; longest↑490; late [[331, 4], [373, 4], [386, 7], [402, 4], [404, 4], [406, 4], [410, 3], [417, 6], [494, 34]]<br>1403109 Maze; queen_length; Q r184/head-on mover/L2/a0 ←#225:L3(시작3),d1/k1; queen_length↑184; late 없음<br>1403112 Around UNSW; queen_length; Q r238/head-on hit/L11/a0 ←#410:L6(시작6),d3/k3; queen_length↑238; late 없음<br>1403114 Queen Of Spades; elimination; Q r121/head-on hit/L2/a0 ←#3:L2(시작2),d1/k1; longest↑157; late 없음<br>1403115 Schooltime; longest; Q 생존; longest↑164; late [[377, 4], [387, 4], [393, 4], [400, 4], [402, 3], [405, 4]]<br>1403119 Portals; queen_length; Q r109/wall/L3/a0; queen_length↑109; late 없음<br>1403120 Slithery Fight; queen_length; Q r89/wall/L3/a4; queen_length↑89; late 없음<br>1408112 Australia; queen_length; Q r85/own body/L2/a1; queen_length↑85; late 없음<br>1408113 Islands; longest; Q r142/wall/L3/a1; longest↑442; late [[442, 20]]<br>1408119 Queen Of Spades; elimination; Q r156/head-on hit/L3/a0 ←#35:L3(시작3),d2/k2; longest↑332; late [[334, 2], [352, 4]]<br>1408124 Portals; queen_length; Q r73/own body/L2/a2; queen_length↑73; late 없음<br>1408125 Slithery Fight; queen_length; Q r192/wall/L3/a2; queen_length↑192; late 없음 |
| B7 / WeHaveQuizzes | 1403638 weakhold; longest; Q r97/head-on hit/L2/a3 ←#50:L3(시작3),d1/k1; longest↑379; late [[348, 2]]<br>1403639 Australia; longest; Q r126/head-on hit/L2/a1 ←#128:L3(시작2),d3/k3; longest↑109; late [[304, 5], [306, 3], [311, 3], [319, 3], [335, 3]]<br>1403640 Islands; longest; Q r95/wall/L2/a2; longest↑491; late [[304, 4], [372, 4], [375, 4]]<br>1403641 Maze; queen_length; Q r185/head-on hit/L2/a1 ←#240:L4(시작4),d2/k2; queen_length↑165; late 없음<br>1403642 Stripes; elimination; Q r14/own body/L3/a1; longest↑46; late 없음<br>1403643 Tower Defense; queen_length; Q r104/head-on hit/L3/a0 ←#26:L4(시작4),d2/k2; queen_length↑104; late [[427, 5]]<br>1403644 Around UNSW; queen_length; Q r52/head-on hit/L3/a1 ←#82:L3(시작4),d5/k5; queen_length↑52; late 없음<br>1403646 Queen Of Spades; elimination; Q r74/head-on hit/L2/a0 ←#14:L2(시작2),d1/k1; longest↑67; late 없음<br>1403649 Devil; elimination; Q r19/head-on hit/L2/a2 ←#4:L3(시작3),d2/k2; longest↑68; late 없음<br>1403650 Trauma; elimination; Q r230/head-on hit/L2/a0 ←#153:L5(시작6),d4/k4; longest↑177; late [[341, 3]]<br>1403651 Portals; queen_length; Q r83/another body/L3/a1; queen_length↑83; late 없음<br>1403652 Slithery Fight; queen_length; Q r318/another body/L3/a7; queen_length↑285; late 없음<br>1408543 Australia; longest; Q r53/head-on hit/L2/a0 ←#6:L3(시작4),d3/k3; longest↑135; late [[312, 3]]<br>1408545 Maze; queen_length; Q r124/wall/L3/a1; queen_length↑124; late [[439, 13], [446, 9]]<br>1408546 Stripes; elimination; Q r14/own body/L2/a1; longest↑143; late 없음<br>1408547 Tower Defense; elimination; Q r133/head-on hit/L3/a1 ←#34:L3(시작4),d3/k3; longest↑370; late [[351, 2], [356, 3], [362, 2], [370, 3]]<br>1408548 Around UNSW; longest; Q r51/head-on hit/L2/a2 ←#106:L3(시작3),d4/k4; longest↑396; late 없음<br>1408550 Queen Of Spades; elimination; Q r85/head-on hit/L2/a0 ←#27:L2(시작2),d1/k1; longest↑109; late 없음<br>1408551 Schooltime; longest; Q 생존; longest↑487; late [[387, 29]]<br>1408553 Devil; elimination; Q r24/head-on hit/L2/a0 ←#4:L3(시작3),d4/k4; longest↑161; late 없음<br>1408554 Trauma; queen_length; Q 생존; queen_length↑276; late 없음<br>1408555 Portals; queen_length; Q r10/own body/L3/a0; queen_length↑10; late 없음<br>1408556 Slithery Fight; queen_length; Q r384/head-on hit/L2/a0 ←#1548:L2(시작2),d1/k1; queen_length↑271; late [[361, 48]] |
| B7Q / Big Bobs Bots | 1421766 weakhold; queen_length; Q r77/head-on mover/L2/a0 ←#33:L2(시작2),d1/k1; queen_length↑77; late 없음<br>1421767 Australia; queen_length; Q r85/head-on hit/L2/a0 ←#51:L2(시작2),d1/k1; queen_length↑85; late 없음<br>1421769 Maze; queen_length; Q r83/wall/L3/a0; queen_length↑83; late [[439, 39]]<br>1421771 Tower Defense; elimination; Q r104/head-on hit/L3/a0 ←#7:L2(시작2),d1/k1; longest↑215; late 없음<br>1421773 Default; queen_length; Q r118/head-on hit/L2/a0 ←#30:L2(시작2),d1/k1; queen_length↑118; late 없음<br>1421779 Portals; queen_length; Q r139/wall/L3/a3; queen_length↑139; late 없음<br>1421780 Slithery Fight; queen_length; Q 생존; queen_length↑489; late 없음 |
| B7Q / WeHaveQuizzes | 1422309 Australia; longest; Q r110/head-on hit/L4/a0 ←#30:L4(시작5),d4/k4; longest↑104; late 없음<br>1422310 Islands; longest; Q r109/wall/L2/a3; longest↑208; late [[301, 4], [313, 4], [316, 4], [317, 3], [337, 3], [340, 3], [342, 4], [346, 4], [351, 4], [358, 4], [363, 4], [394, 4], [402, 5]]<br>1422311 Maze; queen_length; Q r113/wall/L3/a4; queen_length↑113; late [[351, 6]]<br>1422312 Stripes; elimination; Q r58/head-on mover/L3/a1 ←#1:L3(시작3),d2/k2; longest↑212; late 없음<br>1422313 Tower Defense; elimination; Q r74/head-on hit/L3/a0 ←#11:L4(시작4),d3/k3; longest↑73; late 없음<br>1422314 Around UNSW; longest; Q r81/head-on hit/L2/a2 ←#104:L3(시작3),d4/k4; longest↑235; late [[357, 22], [369, 14], [374, 3]]<br>1422319 Devil; elimination; Q r59/head-on hit/L4/a3 ←#27:L3(시작3),d4/k4; longest↑69; late 없음<br>1422321 Portals; queen_length; Q r10/own body/L2/a0; queen_length↑9; late 없음<br>1422322 Slithery Fight; queen_length; Q r284/head-on hit/L2/a2 ←#1116:L3(시작5),d5/k5; queen_length↑261; late 없음 |

| arm / 상대 | Q<100 / Q100-300 / Q>300 / 늦은 최장 피격 / 두 Q 사망·out-eaten / 전멸 / 기타 |
|---|---|
| MAIN / Big Bobs Bots | 14/9/5/20/2/7/0 |
| MAIN / WeHaveQuizzes | 17/16/1/17/9/14/4 |
| B7 / Big Bobs Bots | 4/9/0/5/3/2/0 |
| B7 / WeHaveQuizzes | 13/6/2/10/5/8/1 |
| B7Q / Big Bobs Bots | 3/3/0/1/0/1/1 |
| B7Q / WeHaveQuizzes | 5/4/0/3/3/3/0 |
| B10 / Big Bobs Bots | 0/0/0/0/0/0/0 |
| B10 / WeHaveQuizzes | 0/0/0/0/0/0/0 |
클래스는 겹칠 수 있다(예: Q 사망과 전멸). out-eaten은 두 Q 사망·양팀 생존 상태의 패배이며 섭취 인과 증명은 아니다. 기타는 앞 조건 모두 없음.

## 5. 관측 요약 (조언 없음)

MAIN 90판 21승; B7 60판 23승; 짝 60판.
B7Q 30판 14승; MAIN 짝 30판; B7 공유 지도 30개.
B10 0판 0승.
별도 시간대 sr51-bob1 15판 6승.
MAIN 최대 패배 클래스: leader rammed late 37건, queen <100 31건, queen 100-300 25건.
B7 관련 사건: even 704건, small hunt 242건.
재실행: `nice -n 10 python3 -B data/analysis/ladder/dossier/online/agg7_report.py`. 상세 분자/분모·모든 판: `agg7-games.json`; 검증: `agg7-validation.json`.
