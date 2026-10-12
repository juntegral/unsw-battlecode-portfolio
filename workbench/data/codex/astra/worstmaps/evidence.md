[M] 작성 시각: 2026-10-09T03:01:34+09:00.
[M] 입력은 inventory.json에 고정했다. 결과 작성 범위는 이 폴더뿐이다.

| [M] 구조 | 대표 경기·우리 진영 | 우리 시작 머리 (x,y) | 상대 시작 머리 (x,y) |
|---|---|---|---|
| Australia f739cd5560776b94 | 1472753 A | (39,44)L4 (39,12)L4 (42,48)L2 (39,49)L2 (33,54)L2 (34,44)L2 (33,47)L3 (34,50)L4 (40,38)L3 | (24,19)L4 (24,51)L4 (21,15)L2 (24,14)L2 (30,9)L2 (29,19)L2 (30,16)L3 (29,13)L4 (23,25)L3 |
| Stripes 4b7365f190887d37 | 1472756 A | (21,1)L2 (21,4)L2 | (2,10)L2 (2,7)L2 |
| Tower Defense ee5de00562c8f1ad | 1472757 A | (26,11)L2 (26,8)L2 | (5,4)L2 (5,7)L2 |
| Around UNSW 9ad36163e7ae85d8 | 1472758 A | (20,42)L4 (15,44)L4 (17,40)L2 (17,44)L2 (21,40)L2 (13,43)L2 (13,39)L3 (16,47)L4 (44,35)L3 (30,41)L10 | (43,21)L4 (48,19)L4 (46,23)L2 (46,19)L2 (42,23)L2 (50,20)L2 (50,24)L3 (47,16)L4 (19,28)L3 (33,22)L10 |
| Default 69c9d11a5589ed4a | 1472759 A | (31,31)L4 (27,31)L4 (23,31)L4 (19,31)L4 | (0,0)L4 (4,0)L4 (8,0)L4 (12,0)L4 |
| Schooltime f9d4541e6edea639 | 1472761 A | (56,2)L4 (43,3)L4 (36,3)L4 | (3,2)L4 (16,3)L4 (23,3)L4 |
| Devil b3526b128ae8d4d3 | 1472763 A | (28,5)L4 (28,11)L4 (28,8)L4 | (3,5)L4 (3,11)L4 (3,8)L4 |
| Schooltime 45622213102be5a1 | 1472012 A | (3,2)L4 (16,3)L4 (23,3)L4 | (56,2)L4 (43,3)L4 (36,3)L4 |

[M] 라운드는 원 로그의 0부터 센다. 종료 뒤 이월은 생존 예측이 아니라 표본 분모 고정이다. 아래 `queen/longest/elim`은 실제 종국 상태의 판정 항목이다.

| [M] 경기 | 지도 | 버전 | 상대 | 결과/판정 | 열세 시작 | 우리 여왕 사망 r:원인 |
|---|---|---|---|---|---|---|
| 1472753 | Australia | one5 | Cache me outside | loss/longest | 65 | 162:rammed |
| 1472756 | Stripes | one5 | Cache me outside | loss/elim | 256 | 202:wall |
| 1472757 | Tower Defense | one5 | Cache me outside | loss/longest | 63 | 71:rammed |
| 1472758 | Around UNSW | one5 | Cache me outside | win/longest | — | 232:rammed |
| 1472759 | Default | one5 | Cache me outside | win/longest | — | 483:rammed |
| 1472761 | Schooltime | one5 | Cache me outside | loss/longest | — | alive |
| 1472763 | Devil | one5 | Cache me outside | loss/elim | 33 | 97:rammed |
| 1471457 | Australia | one5 | dev test 1 :P | loss/elim | 62 | 110:rammed |
| 1471460 | Stripes | one5 | dev test 1 :P | loss/elim | 39 | 50:wall |
| 1471461 | Tower Defense | one5 | dev test 1 :P | loss/elim | 61 | 112:rammed |
| 1471462 | Around UNSW | one5 | dev test 1 :P | loss/longest | — | 90:rammed |
| 1471463 | Default | one5 | dev test 1 :P | loss/queen | 122 | 161:rammed |
| 1471465 | Schooltime | one5 | dev test 1 :P | loss/longest | — | alive |
| 1471467 | Devil | one5 | dev test 1 :P | loss/elim | 56 | 76:rammed |
| 1472004 | Australia | one5 | WeHaveQuizzes | loss/longest | — | 223:rammed |
| 1472007 | Stripes | one5 | WeHaveQuizzes | loss/elim | 32 | 92:rammed |
| 1472008 | Tower Defense | one5 | WeHaveQuizzes | loss/queen | 118 | 141:rammed |
| 1472009 | Around UNSW | one5 | WeHaveQuizzes | loss/longest | — | 166:rammed |
| 1472010 | Default | one5 | WeHaveQuizzes | loss/elim | 280 | 104:rammed |
| 1472012 | Schooltime | one5 | WeHaveQuizzes | loss/longest | 93 | alive |
| 1472014 | Devil | one5 | WeHaveQuizzes | win/elim | — | 111:wall |
| 1477039 | Australia | one6 | Cache me outside | loss/longest | — | 152:rammed |
| 1477042 | Stripes | one6 | Cache me outside | loss/elim | 119 | 55:rammed |
| 1477043 | Tower Defense | one6 | Cache me outside | loss/elim | 57 | 92:rammed |
| 1477044 | Around UNSW | one6 | Cache me outside | loss/longest | — | 88:rammed |
| 1477045 | Default | one6 | Cache me outside | loss/elim | 73 | 269:rammed |
| 1477047 | Schooltime | one6 | Cache me outside | loss/longest | — | alive |
| 1477049 | Devil | one6 | Cache me outside | win/elim | — | 17:own body |
| 1474983 | Australia | one6 | WeHaveQuizzes | loss/longest | — | 113:rammed |
| 1474986 | Stripes | one6 | WeHaveQuizzes | loss/elim | 26 | 51:rammed |
| 1474987 | Tower Defense | one6 | WeHaveQuizzes | loss/elim | 70 | 70:rammed |
| 1474988 | Around UNSW | one6 | WeHaveQuizzes | loss/longest | — | 99:rammed |
| 1474989 | Default | one6 | WeHaveQuizzes | win/longest | — | 425:rammed |
| 1474991 | Schooltime | one6 | WeHaveQuizzes | loss/longest | — | alive |
| 1474993 | Devil | one6 | WeHaveQuizzes | loss/elim | 35 | 28:rammed |
| 1480431 | Australia | one7 | Cache me outside | win/queen | — | alive |
| 1480434 | Stripes | one7 | Cache me outside | loss/elim | 184 | 43:rams |
| 1480435 | Tower Defense | one7 | Cache me outside | loss/elim | 67 | 81:rammed |
| 1480436 | Around UNSW | one7 | Cache me outside | win/longest | — | 278:rammed |
| 1480437 | Default | one7 | Cache me outside | loss/elim | 199 | 125:rammed |
| 1480439 | Schooltime | one7 | Cache me outside | win/longest | — | alive |
| 1480441 | Devil | one7 | Cache me outside | loss/elim | 48 | 99:rammed |
| 1479920 | Australia | one7 | WeHaveQuizzes | win/longest | — | 254:rammed |
| 1479923 | Stripes | one7 | WeHaveQuizzes | loss/elim | 27 | 51:wall |
| 1479924 | Tower Defense | one7 | WeHaveQuizzes | loss/elim | 50 | 169:rammed |
| 1479925 | Around UNSW | one7 | WeHaveQuizzes | loss/longest | 35 | 171:rammed |
| 1479926 | Default | one7 | WeHaveQuizzes | loss/elim | 111 | 68:rammed |
| 1479928 | Schooltime | one7 | WeHaveQuizzes | loss/longest | 169 | alive |
| 1479930 | Devil | one7 | WeHaveQuizzes | win/elim | — | 41:wall |
| 1471964 | Devil | one5 | Jingling Munmin | win/elim | — | 83:wall |
| 1471966 | Stripes | one5 | Jingling Munmin | loss/elim | 92 | 219:wall |
| 1471967 | Default | one5 | Jingling Munmin | loss/elim | 156 | 71:rammed |
| 1471968 | Schooltime | one5 | Jingling Munmin | win/longest | — | alive |
| 1473238 | Devil | one5 | tozoman | win/elim | — | 48:rammed |
| 1473239 | Stripes | one5 | tozoman | loss/elim | 86 | 56:rammed |
| 1476179 | Tower Defense | one6 | Maccas | loss/elim | 104 | 285:rams |
| 1476181 | Devil | one6 | Maccas | win/elim | — | alive |
| 1476182 | Australia | one6 | Maccas | win/longest | — | 235:rammed |
| 1478191 | Around UNSW | one6 | f2p | win/longest | — | 66:rammed |
| 1478193 | Schooltime | one6 | f2p | win/longest | — | alive |
| 1478194 | Australia | one6 | f2p | win/longest | — | 117:rammed |

[M] 검증: 원 메타데이터 승자 61판, 독립 원장 스냅샷 244개, 진주 섭취 합계 122개와 일치했다. [validation.json](validation.json).
[C] 기존 계수기는 `o1_scan.scan`, 바이너리 리더는 `label_report.agg.sb.load_replay`, 지형 그래프는 `count_local.Geo`를 import했다. 새 코드는 공간 배정과 공급 관측을 추가한다.
[M] 온라인 기보는 타이머 사건이 없고 지도 TILE 타이머도 0이다. 구조가 일치하는 로컬 파일도 Devil에서는 관측 생성 위치와 맞지 않았다. 따라서 최종 표는 공급 설정을 사용하지 않고 현재 61판의 자연 생성 위치·섭취 후 생성 간격을 다시 센 결과다.
[E] 빠른 칸 추정은 식사·점유·표본량에 좌우된다. 기보 전체를 이용한 사후 지형 설명이며 당시 봇이 알 수 있던 정보량을 뜻하지 않는다. 짧은 거리와 생산칸 최근접 배정도 몸 막힘·id 순서·가속을 반영한 실제 소유권은 아니다.
[M] 공급 구조별 자료: [supply.json](supply.json). 모든 라운드 인구/길이와 기보 경로: [rows.json](rows.json).
[C] 재생성 순서: `python3 -B analyze.py` → `supply.py` → `enrich.py` → `trace.py` → `render_report.py` → `finish.py` (각 스크립트를 저장소 루트에서 전체 상대경로로 실행). 입력 경기는 inventory.json의 목록을 기준으로 보존한다; analyze.py를 재실행하면 새로 도착한 기보가 추가될 수 있다.
[M] `nice -n 10`은 환경에서 우선순위 변경이 거부되어 분석은 기본 우선순위로 실행됐다. 네트워크·봇 실행·컴파일·게시·원본 편집은 하지 않았다.
