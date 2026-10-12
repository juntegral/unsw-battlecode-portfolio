[M] L≥4 무분열 차례 전수. 아래는 우선순위를 정한 **관측 조건 분류**이며 실행된 return 문의 확정 집계가 아니다. [C] 두 소스의 DEBUG_LOG=false이고 [M] 대상 r0–100의 dragonLog는 0건이다.

|판정 가능한 조건/미확정|Cache|Preyas|코드 위치(one8 / one10)|
|---|---:|---:|---|
|unresolved internal gate or earlier action|774|475|act 1334–1568 / 1348–1579; harvesting_now 1884 / 1905|
|child_has_exit geometry (memory/precedence unknown)|249|135|1897 / 1918; 1930 / 1967|
|CHILD_MIN_ROOM geometry (memory/precedence unknown)|280|145|1897 / 1918; 실제 tail_room 2027 / 2064|
|QS_KEEP_LEN eligible (ring/early-return precedence unknown)|1111|677|1862 / 1883; 상수 150–153 / 153–156|
|child_spans_portal geometry (precedence unknown)|53|31|1901 / 1922; 1941 / 1978|
|portal-adjacent (exception/precedence unknown)|48|55|1905 / 1926; one10 예외 1927|
[C] one8: `QS_KEEP_MIN_UNITS:2`, 포털 예외 없음, `SHORT_EVADE:false`. one10: `QS_KEEP_MIN_UNITS:6`, `SPLIT_PORTAL_OK:true`, `SHORT_EVADE:true`. 따라서 one11 설정을 소급하지 않았다.
[C] 관문 순서(one10:1866–1945): safezone → queen guard → round/length/leader → QH → ring → QS_KEEP → grow round → unit cap → EAT_BEFORE_SPLIT → harvesting → can_split/queen_boot → tail unseen 허용 → child exit/room → child portal span → tail portal. [C] QG_SAFEZONE=false, QH는 QUEEN_AVENGE=8 때문에 qh_watch:2914–2922에서 꺼짐(one8:2877); EAT_BEFORE_SPLIT=false; grow_round는 150/300이고 LC_* 조기전환은 꺼짐. 이들 관문은 r0–100 원인이 아니다.
[E] QS_KEEP 조건은 값으로 확인되지만 그 앞의 ring 또는 hunt/ram 반환이 실제 원인일 수 있다. 나머지 기하 분류는 전체 판면이며 봇의 기억, enter_time, survey 및 사전 반환과 같다고 가정하지 않는다. tail_room 표값은 전체 상태에서 몸을 고정한 거리≤8 BFS이며 코드의 가중 미관측 공간값과 다르다.
|출전 집단·분열 전 길이|우리 횟수|상대 횟수|
|---|---:|---:|
|Cache L4|894|2092|
|Cache L5|171|108|
|Cache L6|154|10|
|Cache L7|58|51|
|Cache L8|39|4|
|Cache L9|5|2|
|Cache L10|4|2|
|Cache L11|2|2|
|Cache L13|2|2|
|Cache L15|2|2|
|Cache L17|2|2|
|Cache L19|2|2|
|Cache L21|2|2|
|Cache L23|2|2|
|Cache L25|2|2|
|Preyas L4|509|881|
|Preyas L5|94|123|
|Preyas L6|77|18|
|Preyas L7|33|10|
|Preyas L8|23|7|
|Preyas L9|6|5|
|Preyas L10|2|3|
|Preyas L11|1|1|
|Preyas L12|0|1|
|Preyas L13|1|0|
|Preyas L14|0|1|
|Preyas L15|1|0|
|Preyas L16|0|1|
|Preyas L17|1|0|
|Preyas L18|0|1|
|Preyas L19|1|0|
|Preyas L20|0|1|
|Preyas L21|1|0|
|Preyas L22|0|1|
|Preyas L23|1|0|
|Preyas L25|1|1|
|집단|L≥4 무분열 우리/상대|전체 분열 우리/상대|
|---|---|---|
|Cache|2515/1891|1341/2285|
|Preyas|1518/747|752/1055|
