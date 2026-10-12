[M] 최다 원인: 아군이 여왕의 마지막 출구를 막음—Islands·Maze, 2/3판.
[C/E] 카드: LIVE-BUT-FAILED `QUEEN_EXIT_KEEP:true`를 최종 행동에도 강제하고, 출구 보존에 필요하면 아군 희생을 허용.
[M/C/E] 확신: 사망·봉쇄는 높음; Islands의 후처리 덮어쓰기와 Stripes의 분열 분기 식별은 중간—내부 실행 추적 없음.

[M] 세 기보의 A 봇 문자열은 모두 21200(one10), 상대는 Cache me outside. r은 기보의 0-based 라운드. 최종값은 재구성과 기보 result가 일치했다. [C] 아래 줄 번호는 `data/online/smoke/one10-bot/main.cpp`; 분류 기준은 읽은 CARDS.md다.

| [M] 경기 / 판정 | 최종 A: 여왕/최장/총길이/생존수 | 최종 B | 되돌아오지 않은 판정 열세 |
|---|---|---|---|
| 1492093 Islands / 최장, r499 | 0/26/114/29 | 0/57/185/13 | r247: #1 사망. 상대 #0은 r234 우리 #215의 박치기로 이미 사망 |
| 1492094 Maze / 여왕, r499 | 0/55/121/18 | 60/60/146/22 | r125: #0 사망, 상대 #1 끝까지 생존 |
| 1492095 Stripes / 전멸, r119 | 0/0/0/0 | 0/4/59/26 | r119: #99와 여왕 #1 사망. 상대 #0은 r13 자기 몸 충돌로 사망 |

| 패배를 만든 사건 [M] | 켜진 보호와 놓친 조건 [C], 분기 추정 [E] |
|---|---|
| Islands: r245 #1이 (42,12)로 남하한 뒤 아군 #548이 (42,13)을 막음. r246 여왕은 5→3으로 분열, r247 남쪽 #548의 꼬리에 충돌. 적 공격자 없음. | `QUEEN_EXIT_KEEP:true`(869–1062). #548의 북쪽 (41,12)은 여왕 출구를 보존하지만 자신은 갇힌다. 후속 `POCKET_KEEP_OUT`(640–648, 730–771)은 그런 경로를 거부하고 여왕 출구를 재검사하지 않는다. [E] 이 덮어쓰기가 관측된 동진과 부합한다. |
| Maze: r124 #0이 (18,2)로 들어간 뒤 #86이 (18,1)을 막음. r125 동·서는 벽, 북은 아군, 남은 자기 몸. 남행으로 사망. 적 공격자 없음. | `QUEEN_EXIT_KEEP:true`: #86은 북=자기 몸, 동·남=벽, 서=여왕 출구. `!step(next)`를 제외(992), L3이라 분열 불가(1002); 탐색에도 출구를 남기는 생존 경로가 없다. 비공격적 자진 사망을 후보로 다루지 않는다. |
| Stripes: r118 유일한 우리 용 #1이 L4→L2+#99로 분열. r119 유일한 합법 이동 (18,10)은 보이는 적 #94(L2,18,11)의 한 걸음 사정권. #94가 북행 박치기; #90은 별도로 #99를 두 걸음 박치기로 제거. | `QS_KEEP_LEN:3`은 `unit_count>=QS_KEEP_MIN_UNITS(6)`에서만 일반 분열을 막음(1883–1887); 실제 1마리. [E] 일반 분열 허용과 부합. r119에는 `QUEEN_SAFETY:true`도 대안이 없어 plain fallback(1464), L2라 유료 탈출·분열 불가. 잘린 적 길이 문제가 아니다. |

[M/C] Islands의 후속 최장 열세: 총길이는 r174, 최장은 r209부터 계속 뒤졌다. r151–200 자연 진주 58:114; r251–350은 115:218이며 우리는 4,845차례 중 4,728차례 L≤3, 분열 91회였다. r400 최장 4:50. `board_short()`의 56마리 조건(4765–4770)과 분열 허용(1889)이 작은 용 재생산을 지속시킨다. 유일한 L≥10 사망은 r443 #957(L12), 적 #1112(L3)의 두 걸음 박치기. 끝에 #1082(L16), #1169(L26)는 살아 있었다. [E] 긴 용 하나의 소실보다 축적 지연이 크며, 별도 경제 카드는 내지 않는다.

[M] 여왕 사후 접근: Islands·Stripes는 상대 여왕이 먼저 죽어 해당 없음. Maze는 지형·포털 최단거리 ≤5인 우리 차례 24개(r349–481); 최소 2(r467 #900), 따라서 ‘접근 못함’이 아니다. 몸을 장애물로 둔 비포털·시야 내 경로도 r465 #900 4걸음, r473 #942 5걸음, r479 #957 3걸음에서 있었다. 실제 박치기는 하지 않았다. [C/E] `QUEEN_SURE_LEN:64`, `QUEEN_SURE_STEPS:5`에도 `!is_leader()`(3533)가 필요하다. 해당 내부 지도자 상태와 후처리 덮어쓰기는 미확인이라 실패 분기를 단정하지 않는다. BEING BUILT인 QUEEN_WAR를 재제안하지 않는다.

| 순위·설명 판수 | 카드·상태·규칙 | 코드 / 기존 스위치 | 작동·반증 계수 |
|---|---|---|---|
| 1 · 2/3 | LIVE-BUT-FAILED: 모든 후처리 뒤 여왕 출구 보존. 아군이 갇히더라도 보존 경로를 유지; 그런 경로도 없으면 아군 자진 사망으로 출구를 남김. | 640–648, 984–1062. `QUEEN_EXIT_KEEP:true` 이미 켜짐; 수정 필요. | 해당 봉쇄 2→0, 여왕 r247/r125 생존. 반증: 출구 0 유지 또는 희생 뒤에도 같은 사망. |
| 2 · 1/3 | LIVE-BUT-FAILED: 적은 아군 수 때문에 여왕을 L2로 일반 분열시키지 않음. | 153–154, 1883–1887. 후보 `QS_KEEP_MIN_UNITS:0` (`QS_KEEP_LEN:3` 유지). | Stripes r118의 L4→2 일반 분열 1→0, r119 생존. 반증: 비상 분열이 그대로 발생하거나 보존해도 피격. |

[M] 마지막 세 **자기 차례 시작**의 7×7. Q/q=우리 여왕 머리/몸, A/a=아군, B/b=적, *=진주, .=빈칸. 각 중심은 Q. 벽은 -/│, 포털은 =/!; 격자 안 칸은 7×7이며 아래에 중심의 네 방향도 적었다.

**[M] 1492093**

| r245 (42,11) → S | r246 (42,12) → 분열 | r247 (42,12) → S |
|---|---|---|
| <code>+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;.│A&nbsp;.&nbsp;a&nbsp;.&nbsp;.&nbsp;.&nbsp;<br>+-+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;.│.│*&nbsp;.&nbsp;.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+-+-+-+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;q&nbsp;q&nbsp;q&nbsp;q│.&nbsp;.&nbsp;a&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+=+<br>&nbsp;.&nbsp;.│.&nbsp;Q&nbsp;.&nbsp;.&nbsp;A&nbsp;<br>+-+-+-+&nbsp;+-+-+&nbsp;+<br>│*&nbsp;*│.│.│.&nbsp;.│*│<br>+&nbsp;+-+&nbsp;+&nbsp;+&nbsp;+-+-+<br>&nbsp;*│a&nbsp;A&nbsp;.&nbsp;.&nbsp;A&nbsp;.&nbsp;<br>+-+&nbsp;+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>│.&nbsp;.&nbsp;.&nbsp;.│.&nbsp;a&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+-+-+-+-+</code> | <code>+-+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;.│.│*&nbsp;.&nbsp;.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+-+-+-+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;.&nbsp;q&nbsp;q&nbsp;q│.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+=+<br>&nbsp;.&nbsp;.│.&nbsp;q&nbsp;.&nbsp;A&nbsp;a&nbsp;<br>+-+-+-+&nbsp;+-+-+&nbsp;+<br>│*&nbsp;*│.│Q│.&nbsp;.│*│<br>+&nbsp;+-+&nbsp;+&nbsp;+&nbsp;+-+-+<br>&nbsp;*│.&nbsp;a&nbsp;A&nbsp;.&nbsp;a&nbsp;A&nbsp;<br>+-+&nbsp;+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>│.&nbsp;.&nbsp;.&nbsp;.│.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+-+-+-+-+<br>&nbsp;.│.│*│.&nbsp;.│.&nbsp;.│<br>+-+-+-+&nbsp;+-+-+-+</code> | <code>+-+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;.│.│A&nbsp;.&nbsp;.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+-+-+-+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;A&nbsp;a&nbsp;.&nbsp;q│.&nbsp;A&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+=+<br>&nbsp;.&nbsp;.│.&nbsp;q&nbsp;.&nbsp;a&nbsp;.&nbsp;<br>+-+-+-+&nbsp;+-+-+&nbsp;+<br>│*&nbsp;*│.│Q│.&nbsp;.│*│<br>+&nbsp;+-+&nbsp;+&nbsp;+&nbsp;+-+-+<br>&nbsp;*│.&nbsp;.&nbsp;a&nbsp;.&nbsp;.&nbsp;a&nbsp;<br>+-+&nbsp;+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>│.&nbsp;.&nbsp;.&nbsp;A│.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+-+-+-+-+<br>&nbsp;.│.│*│.&nbsp;.│.&nbsp;.│<br>+-+-+-+&nbsp;+-+-+-+</code> |
| N:자기몸, E:빈칸, S:빈칸, W:빈칸 | N:자기몸, E:벽, S:#548, W:벽 | N:자기몸, E:벽, S:#548, W:벽 |

**[M] 1492094**

| r123 (19,3) → W | r124 (18,3) → N | r125 (18,2) → S |
|---|---|---|
| <code>+-+-+-+-+-+-+-+<br>&nbsp;.&nbsp;a&nbsp;a&nbsp;A│.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+-+-+&nbsp;+-+&nbsp;+-+<br>│.│.&nbsp;.&nbsp;.│.!.│*&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+-+&nbsp;+-+-+<br>&nbsp;.│.│.│q&nbsp;.│.&nbsp;.│<br>+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;.&nbsp;.│.&nbsp;Q│.&nbsp;.&nbsp;.&nbsp;<br>+-+&nbsp;+&nbsp;+&nbsp;+-+&nbsp;+&nbsp;+<br>│*│.&nbsp;.│.&nbsp;.│.&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+-+-+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;*│.&nbsp;a&nbsp;a│.│.&nbsp;.&nbsp;<br>+-+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>│.&nbsp;.!.│A│.│.│.&nbsp;<br>+&nbsp;+-+-+&nbsp;+&nbsp;+&nbsp;+-+</code> | <code>+-+-+-+-+-+-+-+<br>&nbsp;.&nbsp;.&nbsp;.&nbsp;a&nbsp;a│.&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+-+-+&nbsp;+-+&nbsp;+<br>&nbsp;.│.│.&nbsp;.&nbsp;A│.!.│<br>+-+&nbsp;+&nbsp;+&nbsp;+-+&nbsp;+-+<br>&nbsp;.&nbsp;.│.│.│.&nbsp;.│.&nbsp;<br>+-+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>│.&nbsp;.&nbsp;.│Q&nbsp;q│.&nbsp;.&nbsp;<br>+&nbsp;+-+&nbsp;+&nbsp;+&nbsp;+-+&nbsp;+<br>│.│*│.&nbsp;.│.&nbsp;.│.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+-+-+&nbsp;+&nbsp;+<br>│*&nbsp;*│.&nbsp;.&nbsp;a│.│.&nbsp;<br>+-+-+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>&nbsp;.│.&nbsp;.!.│a│.│.│<br>+&nbsp;+&nbsp;+-+-+&nbsp;+&nbsp;+&nbsp;+</code> | <code>+-+-+-+&nbsp;+&nbsp;+&nbsp;+-+<br>&nbsp;.&nbsp;*&nbsp;*&nbsp;*&nbsp;.&nbsp;.&nbsp;*&nbsp;<br>+-+-+-+-+-+-+-+<br>&nbsp;.&nbsp;.&nbsp;.&nbsp;.&nbsp;a│.&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+-+-+&nbsp;+-+&nbsp;+<br>&nbsp;.│.│.&nbsp;A&nbsp;a│.!.│<br>+-+&nbsp;+&nbsp;+&nbsp;+-+&nbsp;+-+<br>&nbsp;.&nbsp;.│.│Q│.&nbsp;.│.&nbsp;<br>+-+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+<br>│.&nbsp;.&nbsp;.│q&nbsp;.│.&nbsp;.&nbsp;<br>+&nbsp;+-+&nbsp;+&nbsp;+&nbsp;+-+&nbsp;+<br>│.│*│.&nbsp;.│.&nbsp;.│.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+-+-+&nbsp;+&nbsp;+<br>│*&nbsp;*│.&nbsp;.&nbsp;.│.│.&nbsp;<br>+-+-+-+&nbsp;+&nbsp;+&nbsp;+&nbsp;+</code> |
| N:자기몸, E:벽, S:빈칸, W:빈칸 | N:빈칸, E:자기몸, S:빈칸, W:벽 | N:#86, E:벽, S:자기몸, W:벽 |

**[M] 1492095**

| r117 (19,9) → W | r118 (18,9) → 분열 | r119 (18,9) → S |
|---|---|---|
| <code>+-+-+-+-+&nbsp;+-+-+<br>&nbsp;.&nbsp;.&nbsp;.&nbsp;.&nbsp;B│.&nbsp;.│<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+=+=+&nbsp;+<br>&nbsp;B&nbsp;b&nbsp;b&nbsp;.&nbsp;.│.&nbsp;.│<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+-+-+<br>&nbsp;.!.&nbsp;b&nbsp;B&nbsp;.&nbsp;.&nbsp;.&nbsp;<br>+-+-+-+-+-+-+&nbsp;+<br>│*!*│*&nbsp;Q&nbsp;q&nbsp;q&nbsp;.&nbsp;<br>+&nbsp;+-+&nbsp;+&nbsp;+-+-+&nbsp;+<br>│*&nbsp;*│.&nbsp;.│*│*│.&nbsp;<br>+-+-+&nbsp;+=+=+&nbsp;+&nbsp;+<br>&nbsp;B&nbsp;.&nbsp;.&nbsp;.│*&nbsp;*│.&nbsp;<br>+-+-+-+-+-+-+-+<br>&nbsp;.&nbsp;.&nbsp;b&nbsp;b&nbsp;.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+</code> | <code>+-+-+-+-+-+&nbsp;+-+<br>&nbsp;.&nbsp;B&nbsp;.&nbsp;.&nbsp;B&nbsp;b│.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+=+=+<br>&nbsp;.&nbsp;b&nbsp;.&nbsp;.&nbsp;.&nbsp;.│.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+-+<br>&nbsp;.&nbsp;.!.&nbsp;b&nbsp;b&nbsp;B&nbsp;.&nbsp;<br>+-+-+-+-+-+-+-+<br>&nbsp;.│*!*│Q&nbsp;q&nbsp;q&nbsp;q&nbsp;<br>+&nbsp;+&nbsp;+-+&nbsp;+&nbsp;+-+-+<br>&nbsp;.│*&nbsp;*│.&nbsp;.│*│*│<br>+&nbsp;+-+-+&nbsp;+=+=+&nbsp;+<br>&nbsp;.&nbsp;b&nbsp;B&nbsp;.&nbsp;.│*&nbsp;*│<br>+-+-+-+-+-+-+-+<br>&nbsp;B&nbsp;.&nbsp;.&nbsp;b&nbsp;.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+</code> | <code>+-+-+-+-+-+&nbsp;+-+<br>&nbsp;.&nbsp;b&nbsp;B&nbsp;.&nbsp;b&nbsp;.│B&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+=+=+<br>&nbsp;B&nbsp;.&nbsp;.&nbsp;.&nbsp;B&nbsp;.│.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+-+<br>&nbsp;.&nbsp;.!.&nbsp;.&nbsp;b&nbsp;b&nbsp;B&nbsp;<br>+-+-+-+-+-+-+-+<br>&nbsp;.│*!*│Q&nbsp;q&nbsp;.&nbsp;a&nbsp;<br>+&nbsp;+&nbsp;+-+&nbsp;+&nbsp;+-+-+<br>&nbsp;.│*&nbsp;*│.&nbsp;.│*│*│<br>+&nbsp;+-+-+&nbsp;+=+=+&nbsp;+<br>&nbsp;.&nbsp;.&nbsp;b&nbsp;B&nbsp;.│*&nbsp;*│<br>+-+-+-+-+-+-+-+<br>&nbsp;b&nbsp;B&nbsp;.&nbsp;.&nbsp;.&nbsp;.&nbsp;.&nbsp;<br>+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+&nbsp;+</code> |
| N:벽, E:자기몸, S:빈칸, W:빈칸 | N:벽, E:자기몸, S:빈칸, W:벽 | N:벽, E:자기몸, S:빈칸, W:벽 |

[M] 재현: `python3 -B data/codex/astra/sweep/0519/loss3/analyze.py`; 기존 replay reader를 import했다. [E] 수정 효과·내부 분기·장기 반사실은 미검증; 게임 실행·네트워크·봇 변경 없음. 기록: 2026-10-09 05:27:23 KST.
