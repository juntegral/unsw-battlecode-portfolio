import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
text='''최우선 원인: 포털을 건너는 아군이 여왕의 마지막 출구를 막음—직접 패인 1/3판, 별도 여왕 봉쇄 사건까지 2/3판. [M/E]
카드: LIVE-BUT-FAILED — QUEEN_EXIT_STRICT를 여왕이 공유한 출구 예약에도 적용. [C/E]
확신: 사건·분기 누락은 높음, 수정 후 승리 여부는 미검증. [M/C/E]

[M] 실제 출전본은 모두 **21269(one11)**. 아래 수치는 우리/상대 순서, 최종 상태는 **여왕 길이·최장·총길이·생존수**다. ‘굳어진 라운드’는 이후 실제 기보에서 뒤집히지 않은 시점이며 반사실적 승패 보장은 아니다. 1496711은 브리프와 달리 메타데이터 `ranked:false`다.

| 게임 / 상대 / 우리 편 | 결정·최종 상태 [M] | 굳어진 시점 [M] |
|---|---|---|
|1497389 / Cutlery / A / Tower Defense|전멸, r132. **0·0·0·0 / 2·8·80·29**|r42부터 총길이 열세 지속, r77 #3 사망으로 여왕만 남음; r132 확정|
|1497390 / Cutlery / A / Portals|최장, r499. **0·20·43·5 / 0·49·71·8**|상대 여왕 r356 사망으로 최장 비교; r413부터 최장 열세 지속|
|1496711 / Quantify / B / Portals|여왕, r499. **0·17·50·7 / 3·5·11·3**|r49 우리 여왕 사망 이후 여왕 열세 지속|

| 직접 패인 순위: 모두 1/3판 [M/E] | 사건·우리 행동 [M] | 출전 코드의 방어와 실패 조건 [C] |
|---|---|---|
|공동 1: 포털 경유 아군 봉쇄, 1496711|r48 #26이 (14,4)→(13,4), 꼬리가 북쪽 출구를 점유. 같은 라운드 #30의 새끼 #36이 (18,8)→포털→(13,5), 서쪽 마지막 출구 봉쇄. r49 Q#0 L3이 북쪽 #26 몸에 충돌. 적 공격자는 없음.|`QUEEN_EXIT_STRICT:true`, 886–906행: #36 이동 전 여왕이 시야 밖이므로 `queen_seen<0`에서 반환. #26 이동 당시에는 서쪽이 열려 있었음. 자식 분열만 막는 대기 카드로는 후속 포털 이동을 막지 못함.|
|공동 1: 먹이 접근 없는 이동, 1497389|#1·#3 합계 211차례 섭취 0, 분열 0. 진입 가능한 인접 진주가 있던 차례도 0. r42 상대 성장 시작; r77 #11이 #3을 들이받음. Q#1은 r130–132 동진만 가능했고 r132 (26,6)에서 #4 L3의 서쪽 한 걸음에 사망.|`EAT_FIRST:true`, 7838–7842행은 **인접** 진주 조건이라 전부 불성립. 최종 통로는 남북 켈프·서쪽 자기 목: 위협 확대만으로 출구를 만들 수 없음. 먹이까지의 거시 경로 실패를 보장해서 막는 규칙은 없음.|
|공동 1: 후반 수집 감소·분산 성장, 1497390|r400–499 무행동 25/0회, 자연 진주 40/82개. r450–499 자연 진주 8/24개. #807은 r450–499 섭취 3개, #841은 r459–499 5개만 먹음. 최종 우리 길이 **20·11·7·3·2**, 상대 #848 L49. 우리 L≥10 사망은 0: 긴 개체를 잃은 패배가 아님.|`FEED_CAP_ROUND:350`은 56마리 상한 발동만 늦춤. 7326–7328행의 `round>feed_round`는 별개이며 기본 `ENDGAME_ROUND:400`(48행). 3867–3873행은 수집 유지량을 확인하지 않고 먹이기를 허용. 무행동 전부가 이 분기였는지는 미검증.|

[M] 1497390의 별도 여왕 사망: r267 Q#0은 (3,14)에서 포털로 (27,1)에 들어가 진주를 먹었다. 이후 #359 L4가 (26,0)→(26,1)로 이동해 마지막 일반 출구를 막았다. r268 Q는 #399를 분열했고, r269 북쪽 포털로 자기 목 (3,14)에 충돌했다. 적 공격자는 없다. [C] 엄격 보호는 **L>3 또는 분열**이면 빠진다(889–890행); #359는 r267 L4, r268 L5 분열이었다. `QUEEN_PORTAL_LAST:true`의 대안 검사는 `!any_enterable` 긴급 경로 안에만 있다(1592–1616행). [E] 일반 포털 진입 경로에서의 누락 가능성은 있으나 당시 내부 관측·선택 분기는 재실행하지 않았다. 이 사망만으로 최장 패배를 설명하지 않는다.

| 여왕 사후 적 여왕 5걸음 이내 접근 [M] | 적 여왕 위치 [M] |
|---|---|
|1497389: 없음; 남은 우리 개체 0|#0 (6,3), 즉시 경기 종료|
|1497390: 없음; r269–356 모든 상태 변경·차례에서 지형 최단거리 도달 불가|#1은 우리와 다른 연결 성분, 33개 머리 칸을 이동; 마지막 (4,14), 자기 편 #536 몸에 충돌|
|1496711: 없음; r49–499 같은 기준으로 도달 불가|#1은 다른 연결 성분의 29개 머리 칸을 이동; 최종 (30,9)|

[M] 거리는 켈프·포털·토러스 반영 BFS이며 몸은 무시한다. 따라서 두 Portals 판은 `QUEEN_WAR`·`QUEEN_SURE_STEPS:5`로도 지형적으로 접근할 수 없다.

| 카드 / CARDS.md 상태 | 구체 규칙·삽입 위치 [C/E] | 작동·반증 계수 [M/E] |
|---|---|---|
|출구 예약 / **LIVE-BUT-FAILED** 확장|여왕은 이동 후 다음 차례의 유일한 빈 출구를 공유하고, 그 칸을 점유할 아군은 길이·직접 시야와 무관하게 다른 이동 또는 출구를 보존하는 분열을 선택한다. 886–906, 942–967, 1017–1048행 및 `broadcast_leader` 공유부. 기존 `QUEEN_EXIT_KEEP:true`, `QUEEN_EXIT_STRICT:true`; 상수 재설정만으로 구현되지 않음.|두 봉쇄 장면의 마지막 출구 점유 **2→0**, Q의 다음 차례 생존 **0→2**를 확인. 예약 정보가 행동 전에 전달되지 않거나, 대체 행동도 출구를 막으면 반증. 경기 승리와 별도 판정.|
|먹이 접근 실패 / **no card**|인접 섭취 규칙의 범위 밖. `TERRITORY_DECAY:16`은 **BEING BUILT**, 해당 경로를 고치는지는 미확인.|기준 211차례 섭취 0. 경로 선택 원인을 더 확인하기 전 새 상수 제안 없음.|
|후반 성장 분산 / **no card**|이 표본만으로 먹이기 억제의 이득을 입증하지 못함. 폐기된 `RALLY_END_FRESH` 재제안 없음.|자연 섭취·최장 개체로 유입된 드롭·생존 수집자를 함께 재야 함.|

[M] 마지막 세 여왕 차례의 **행동 전 7×7** 판면. 북쪽 위; Q/q=여왕 머리/몸, A/a=아군, B/b=적, X/x=충돌에 관여한 개체, *=진주, .=빈칸. 1496711의 X는 적이 아닌 #26이다. 켈프·포털 경계까지 그린 원본은 [boards.md](boards.md).
'''
for gid in (1497389,1497390,1496711):
 b=json.loads((OUT/f'{gid}-base.json').read_text());d=json.loads((OUT/f'{gid}-detail.json').read_text());qid=b['queens']['us'];death=next(x for x in b['deaths'] if x['id']==qid);atk=death['actor'] if death['actor']!=qid else death['hit'];w,h=d['w'],d['h'];grids=[]
 for t in d['queen']:
  hd=t['start'][0];cx,cy=hd%w,hd//w;occ={c:(int(i),k) for i,bb in t['bodies'].items() for k,c in enumerate(bb)};rows=[f"r{t['round']}({cx},{cy})"]
  for dy in range(-3,4):
   row=''
   for dx in range(-3,4):
    c=((cy+dy)%h)*w+(cx+dx)%w;s='*' if c in t['pearls'] else '.'
    if c in occ:
     i,k=occ[c];s='Q' if i==qid else 'X' if i==atk else 'A' if d['teams'][str(i)]==d['own'] else 'B';s=s.lower() if k else s
    row+=s
   rows.append(row)
  grids.append(rows)
 text+=f'\n[M] {gid}\n```text\n'+'\n'.join('   '.join(s.ljust(15) for s in row) for row in zip(*grids))+'\n```\n'
text+='''
[M] 재현: `analyze.py` → `evidence.py` → `checks.py`. 공용 `ladder_replay.scan`을 가져왔고 최종 상태는 기보 내 결과와 대조 통과; 재구성 이상 항목은 세 판 모두 없음. `*-base.json`, `*-detail.json`, `checks.json`에 원자료·해시·집계를 보존했다. [C] 행 번호는 모두 `data/online/smoke/one11-bot/main.cpp` 기준이다. [E] 정책 점수·메모리·반사실 재실행, CPU, 수정 효과는 미검증. 네트워크·새 대전·봇 수정 없음.
'''
(OUT/'report.md').write_text(text)
print('total whitespace words',len(text.split()))
non_tables='\n'.join(x for x in text.splitlines() if not x.startswith('|'))
print('excluding tables',len(non_tables.split()))
