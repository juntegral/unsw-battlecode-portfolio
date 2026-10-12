import sys,json
from pathlib import Path
from collections import Counter
from datetime import datetime
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
S=json.loads((P/'summary.json').read_text())
labels=list(S); titles=['one5–WHQ','one5–Cache','one3–WHQ']
rows=[]
def table(title,head,body):
    return title+'\n\n| '+' | '.join(head)+' |\n|'+ '|'.join(['---']*len(head))+'|\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in body)+'\n'
def pair(s,k):return ' / '.join('%.2f'%(c.get(k,0)/s['games']) for c in s['totals'])

intro='''[M] 중반 자연 진주 부족분의 약 60%는 차례 수, 나머지는 차례당 섭취율 차이로 분해된다. 사망률 전체보다 적은 분열·장기 고립이 핵심 관찰이다.
[E] 카드: **없음**. `EAT_FIRST` 강화나 고립 개체의 복귀 규칙을 바로 채택할 근거는 부족하다.
[M/E] 확신: 장부·행동 집계 높음, 점수항의 인과 판정 제한적. 세 표본 각 15판, r101–300.

[M] 아래 쌍은 우리/상대. 판당 평균이며, 모든 경기·양편에서 `L300=L100+자연+아군사체+적사체−사망길이−지불`, `H300=H100+분열−사망` 잔차가 0이다.

'''
body=[]
for text,k in [('길이 r100','L100'),('길이 r300','L300'),('머리 r100','H100'),('머리 r300','H300'),('차례','turns'),('분열','splits'),('사망','deaths'),('자연 진주','eat_n'),('아군 사체 진주','eat_own'),('적 사체 진주','eat_foe'),('사망 길이','deadlen'),('지불 길이','paid')]:body.append([text]+[pair(S[l],k) for l in labels])
report=intro+table('[M] 합계 장부',['판당',*titles],body)
body=[]
for title,l in zip(titles,labels):
    s=S[l];d=s['natural_decomp_per_game']
    total=round((s['totals'][1]['eat_n']-s['totals'][0]['eat_n'])/s['games'],2)
    head=round(d['heads'],2); efficiency=round(total-head,2)
    parts=[round(d['class '+k],2) for k in ('blind','unreachable7','reachable2+')]
    parts.append(round(efficiency-sum(parts),2))
    body.append([title,*['%.2f'%x for x in (head,efficiency,total,*parts)]])
report+=table('[M] 자연 진주 부족분의 정확한 분해',['표본','차례 수','섭취율','합계','섭취율 중 무진주','7걸음 불가','2걸음 이상','인접'],body)
report+='[M] 경기별 대칭 분해: 차례 수 항은 `(T상−T우)×(q상+q우)/2`, 섭취율 항은 `(q상−q우)×(T상+T우)/2`; q는 자연 진주/차례다. 마지막 네 열은 섭취율 항으로 합쳐진다. 표시 반올림 잔차는 섭취율·인접 열에 반영했다. [E] 독립적인 원인·개선 예상량은 아니다.\n\n'
causes=['wall','own body','mate body','foe body','rammed','rams','mate head','stop']
cn=['벽','자기 몸','아군 몸','적 몸','피충돌','공격 충돌','아군 머리','무행동']
body=[]
for c,name in zip(causes,cn):body.append([name]+[' / '.join('%.3f'%(100*s['deaths'][side].get(c,0)/s['totals'][side]['turns']) for side in (0,1)) for s in S.values()])
for name,k in [('합계 사망률','deaths'),('분열률','splits')]:body.append([name]+[' / '.join('%.3f'%(100*x[k]/x['turns']) for x in s['totals']) for s in S.values()])
report+=table('[M] 차례 100회당 사망·분열',['원인',*titles],body)
body=[]
for lb in ['2','3','4','5-9','10+']:body.append([lb]+[' / '.join('%.3f'%(100*s['dead_length_bins'][side].get(lb,0)/s['totals'][side]['turns']) for side in (0,1)) for s in S.values()])
report+=table('[M] 사망 직전 길이별 사망: 전체 차례 100회당',['길이',*titles],body)
body=[]
for title,l in zip(titles,labels):
    s=S[l];G=s['ground']; line=[title]
    for kind in ['pearls','natural','spawn']:
        total=sum(G.get(kind+':'+k,0) for k in ['ours','theirs','tie','none'])
        line.append(' / '.join('%.1f'%(100*G.get(kind+':'+k,0)/total) for k in ['ours','theirs','tie','none']))
    body.append(line)
report+=table('[M] 땅: 최단거리 소유 비율 %, 우리/상대/동점/양편 도달불가',['표본','현재 진주 칸','그중 자연 진주','관측된 자연 발생 칸'],body)
report+='[M] r110부터 r300까지 10라운드 간격, 종료 전 표본의 칸 수를 합산했다. 벽·포털을 반영하고 몸은 제외한 거리다. 땅은 차례·섭취율과 겹치는 관측이므로 장부에 별도로 더하지 않는다. [M] one3에서도 섭취율·고립 격차는 보이지만, 땅 열세까지 같지는 않다.\n\n'
R={};entries={}
for l in labels:
    gs=json.loads((P/(l+'-enrich.json')).read_text());C=Counter();E=Counter()
    for g in gs:
        E.update(g['C'])
        for r in g['d1']:
            reason='leader_zone' if r['zone_model'] else r['reason']
            if reason=='unresolved_score':reason=r['residual_context']
            C[reason]+=1
    R[l]=C;entries[l]=E
body=[]
for name,k in [('미섭취 합계','D1:miss'),('별도: 분열','D1:split'),('별도: 자기 차례 사망','D1:died')]:body.append([name]+[str(S[l]['counts'][0].get(k,0)) for l in labels])
for name,k in [('[M/C] 인접 칸이 포털 너머','portal'),('[E] 리더 진주 구역','leader_zone'),('[M/C] 주머니 상한','pocket'),('[M/C] 적의 한 걸음 도달','enemy_step'),('[E] 꼬리 미도달·공간 부족','room_model'),('[M/C] 여왕 추적 음파','hunter_ping'),('[M] 다른 포털로 이동','chosen_portal'),('[E] 꼬리는 닿지만 협소','tight'),('[M/C] 아군 머리 인접 벌점','ally_head_penalty'),('[E] 여왕 위험 미해결','queen_risk_unknown'),('[E] 나머지 점수 미해결','unresolved')]:body.append([name]+[str(R[l].get(k,0)) for l in labels])
report+=table('[M/E] 인접 진주를 남기고 이동한 차례: 중복 없는 분류',['조건·관측',*titles],body)
report+='[C] `EAT_FIRST`는 영토 차이만 보정한다(6003–6041; 추가 걸음 969–973). 먹이기 금지는 `FEEDER_EAT=true`라 0(69,6005). [E] 공간·구역은 재구성한 조건이지 실행 로그의 최종 원인 판정이 아니다. [C] one3에는 이 보정이 없다.\n\n'
body=[]
for name,keys in [('고립 차례',['solo']),('길이 2~3',['solo L:2','solo L:3']),('분열 후 0~5',['solo age:0-5']),('분열 후 26 이상',['solo age:26+']),('아군 시야 내 현재 진주까지 8+',['solo visible_pearl:8+']),('그 진주에 도달불가/없음',['solo visible_pearl:none']),('관측된 발생 칸까지 8+',['solo spawn:8+']),('발생 칸에 가까워짐',['solo move:closer']),('발생 칸에서 멀어짐',['solo move:farther']),('최근 5라운드 포털 통과',['solo portal_recent']),('확인된 여왕 추적 음파',['solo hunter:True'])]:
    body.append([name]+[' / '.join(str(sum(s['counts'][side].get(k,0) for k in keys)) for side in (0,1)) if name!='확인된 여왕 추적 음파' else str(s['counts'][0].get(keys[0],0)) for s in S.values()])
report+=table('[M] 진주·아군 머리가 7×7에 없는 이동 차례',['조건',*titles],body)
body=[]
for name,k in [('직전에도 고립','continuing'),('직전에는 아군이 보임','entry:previous mate view'),('직전에는 진주가 보임, 미섭취','entry:previous pearl view'),('직전 섭취','entry:previous meal'),('새 개체/직전 분열','entry:new/split')]:body.append([name]+[str(entries[l].get(k,0)) for l in labels])
report+=table('[M] 우리 고립 차례로 들어온 경위',['직전 자기 차례',*titles],body)
report+='[M] 장기간 살아남은 짧은 개체가 많다. [C] 땅 점수는 거리 감쇠가 없고(378–380), 먹이 유인은 거리에 따라 줄며(3714,5703–5727), 진주 시야 공유는 꺼져 있다(163). [E] 분산·탐색이 지속되는 설명과 맞지만, 이동을 결정한 항은 확정하지 못했다.\n\n'
moments=[
['머리 격차','1472012 r100→300','머리 5/14→1/60; 길이 14/35→3/289'],
['머리 격차','1472762 r100→300','머리 12/23→0/63; 길이 28/55→0/206'],
['머리 격차 대조','1465493 r100→300','머리 26/56→14/63; 길이 60/129→35/457'],
['인접 미섭취','1472003 r102, #78 L2','(29,14)→(30,14), 진주 (28,14); 재구성 공간 3, 꼬리 미도달 [E]'],
['인접 미섭취','1472752 r124, #61 L2','(10,0)→(9,0), 진주 (11,0); 공간 3, 꼬리 미도달 [E]'],
['인접 미섭취 대조','1465492 r117, #73 L3','(15,0)→(14,0), 진주 (16,0); 공간 1, 꼬리 미도달 [E]'],
['고립','1472004 r101–103, #43 L2','분열 후 47–49; 발생 칸까지 28→29→30걸음'],
['고립','1472758 r105–107, #49 L3','분열 후 82–84; 발생 칸까지 13→14→15걸음'],
['고립 대조','1465498 r101–103, #30 L3','분열 후 100–102; 발생 칸까지 4→5→6걸음'],
]
report+=table('[M] 기보 장면',['발견','경기·라운드','관측'],moments)
report+='[E] 미확인: 정확한 내부 기억·모든 위험/경로 덮어쓰기·수정 후 효과. 새 경기·컴파일·봇 변경은 하지 않았다. [M] 원인×길이 교차표, 거리 정의, 재현·검증은 [evidence.md](evidence.md), 원자료는 이 폴더 JSON에 있다.\n'
(P/'report.md').write_text(report)

evidence='''[M] midgame 보충 근거. 생성 시각: '''+datetime.now().astimezone().isoformat()+'''.

[M] 읽기 전용 표본은 `data/online/smoke/{one5-w1,one5-c1,one3-w1}-old/`의 메타데이터/기보 각 15쌍이다. 새 대전, 네트워크, 저장소 봇 수정은 없었다. 이번 작업 파일만 `data/codex/astra/midgame/`에 썼다.

[M] `ledger.py`는 기존 `o1_scan.scan`을 import한다. 경계는 r100 종료→r300 종료이며, 조기 종료한 경기는 최종 상태를 유지한다. 각 경기 양편에서 길이·머리 수 항등식을 assert했다. `scan.py`는 기존 `ladder_replay`의 packed reader·canonical edge helper를 import한다. `summarize.py`는 재집계한 차례·자연 섭취 합계를 기존 `o1_mid-{o5,c5,o3}.jsonl`과 대조한다. 45판 모두 일치한다.

[M] 무행동은 replay death reason 4, 벽/자기 몸/다른 몸/머리는 0/1/2/3이다. 다른 몸의 팀과 머리 충돌의 공격자/피격자를 재구성했다. 충돌 시 사망 길이이므로 지불한 이동 비용은 별도 장부다. 무행동을 반드시 먹이기 의도라고 해석하지 않았다.

[M] 분해는 먼저 경기별로 실시한 뒤 15로 나눈다. T=실제 dragon turn 개수, q=자연 진주 수/T. 차례 수 항 + 섭취율 항 = 상대 자연 섭취−우리 자연 섭취. 차례 시작 시 상태를 네 부류(7×7에 진주 없음, 진주는 있지만 점유 칸을 피한 7걸음 내 없음, 최소거리 2~7, 최소거리 1)로 나누고, 각 부류의 자연 섭취/T 차이에 양편 평균 T를 곱했다. 네 부류의 합은 섭취율 항과 같다. 분열·사망 차례도 노출에 포함된다. 진주 기원은 해당 차례의 섭취 사건으로 구분한다.

[M] 땅은 r110,120,…,300 종료 때 현재 진주 칸의 가까운 머리 소속을 센다. 벽과 포털을 통과하는 정적 최단거리이고 몸은 제외한다. 양쪽 모두 도달 불가를 동점에서 분리한다. 표는 모든 칸-시점 가중 합계이고 지도별 평균이 아니다. 조기 종료 이후 새 표본은 추가하지 않는다. `spawn`은 그 시점까지 자연 발생을 실제 관찰한 좌표의 누적 집합이다. 기보에 포함된 지도 TILE 범위는 모두 0이므로 이 필드를 샘 위치로 쓰지 않았다. 한 번도 발생하지 않은 샘을 포함하지 않으며 미래 발생을 선취하지 않는다. 이 때문에 r100/r300의 누적 샘 표본은 같은 좌표 집합이 아니다.

[M] 고립 표본은 차례 시작 시 진주와 아군 머리가 자신의 7×7에 없으며, 그 차례에 섭취·분열·자기 사망이 없는 경우다. age는 부모/자식 모두 마지막 분열 이후 경과다. 현재 진주 거리는 같은 순간 어느 아군의 7×7에라도 있는 진주까지 벽/포털 최단거리, 발생 칸 거리는 자연 발생이 확인되고 그 시점까지 아군이 한 번이라도 본 칸까지의 거리다. 둘 다 공유 가능한 분석자 관측 범위이며 실제 용이 그 정보를 받은 뜻이 아니다. `SHARE_SIGHT=false`다 [C:163]. 출발/도착의 발생 칸 거리를 비교하므로 한 차례 안에 새 발생 칸이 드러난 경우도 거리에 반영된다. `none`은 보이는 목표가 없거나 길이 없는 경우다. 최근 포털 통과와 12차례 재방문도 따로 센다.

[M] `enrich.py`의 진입 경위는 직전 자기 차례의 상태다. '아군이 보였다'가 반드시 자신이 도망갔다는 뜻은 아니다. 아군이 움직이거나 죽어도 고립될 수 있다. 연속 고립은 현 차례 이전의 raw context이며 직전 차례에 뒤늦게 먹은 예도 포함될 수 있다. 적 봇의 음파는 해독하지 않았다. 우리 음파는 기존 `card_42_check` codec을 import했고, 정상 검증을 통과한 생존 적 여왕 좌표 메시지만 hunter로 센다. `broadcast_leader` 2025–2026은 이런 메시지를 qh_on일 때 내보낸다 [C]. 포털 경고가 음파를 대신할 수 있어 hunter=False가 비활성의 증명은 아니다.

[E] 인접 미섭취 원인 표는 최종 점수의 역추적이 아니라 우선순위 있는 관측·조건 분류다. 진주가 하나라도 먹혔으면 성공(다른 진주를 먹은 것도 포함), 자기 사망/분열은 별도다. 리더 구역을 먼저 적용하고, 포털·주머니·적 한 걸음·공간·여왕 위험 미해결·사냥 음파 순으로 분류한다. 잔여는 선택한 포털·협소·아군 머리 벌점·미해결로 나눈다. 동시에 참인 조건을 중복하지 않는다. `one3` 열은 one5의 조건을 대입한 비교이지 EAT_FIRST가 실행됐다는 뜻이 아니다.

[C] EAT_FIRST 6005–6007의 feeder, zone, pocket, dead/closed, threat, risk, enemy-one-step 관문 중 feeder는 FEEDER_EAT=true(69)라 걸리지 않는다. 이 구간에는 feeding_phase도 꺼진다(78=350,173=300,308=0,2445–2448,5592–5594). plain 인접칸만 6003–6007에 들어가며 포털에는 이 보정이 없다. 보정은 WEIGHT_TERRITORY 차이뿐(6031–6041), 강제 섭취가 아니다. 추적 경로 670–673/6092, 분열 855–858, 공격 641–646/702–707이 선택을 덮을 수 있다. 추가 걸음 969–973에도 별도 조건이 있다.

[M/C] 주머니는 개체가 실제로 본 7×7들의 edge 합집합으로 3570–3615를 재현했다. 적 한 걸음과 아군 머리 인접은 차례 시작의 시야·연결로 확인한다(3717–3729,5763–5765). [E] room은 각 개체의 누적 관측 edge/pearl, 현재 시야 내 다른 몸, 자신의 실제 전체 몸으로 3089–3230을 재구성한 모델이다. `SHARE_SIGHT/SYM_INFER=false`를 적용한다. 꼬리 기억이 불완전하거나 포털 경계·사냥의 portal shut에 걸린 경우는 실제 survey와 다를 수 있다. 짧은 몸이 전부 시야에 있으면 1686–1715가 trail을 복원한다. room/dead는 5643–5675, tight는 5651–5661, pocket은 5733–5742에 대응한다. 점수 크기는 missing room당 400, trapped당 5000(386–387)이다. 모델 공간 분류는 실제 '안전했음'을 증명하지 않는다.

[E] leader zone은 그 차례의 검증된 outgoing leader 메시지와 시야에 있는 리더 머리를 사용해 2482–2511을 재구성했다. 메시지가 포털 경고/사냥으로 대체되면 모른다. 위험은 일반 개체에서 map_hits를 돌리지 않고(1677–1679), LONG_SAFETY=false(151)이므로 risk_at=0(4468–4474)이다. 여왕의 위험 ring/ghost/qs_plain 전체는 재현하지 않았다. L≤4 일반 개체의 threat_small은 적 시야 몸 <5와 한 걸음(2617–2621,2667–2668,2692–2694); enemy_step 관측이 이를 포괄한다. 긴 개체의 먼 위협은 미해결 잔여에 남는다. '아군 머리 벌점'/'다른 포털'도 해당 사실을 확인했을 뿐 그 항 하나가 승부를 가른 증명은 아니다.

[E] 카드 없음. 고립 감소를 위해 복귀 경로를 넣는 것은 그 용이 실제로 목표를 알고 있고 그 길이 안전하다는 검증이 필요하다. 누적 아군 관측만으로 이를 허용하면 가용 정보가 아닌 지식을 제안하게 된다. 공간 관문을 약하게 하는 것도 진주 뒤의 사망을 늘릴 수 있으며, 이번 기보만으로 반사실을 검증하지 않았다.

'''
body=[]
for c,name in zip(causes,cn):
    line=[name]
    for s in S.values():
        C=Counter({lb:v for cc,lb,v in s['our_cause_length'] if cc==c})
        line.append(' / '.join(str(C[lb]) for lb in ['2','3','4','5-9','10+']))
    body.append(line)
evidence+=table('[M] 우리 사망 원인×길이: 각 셀 L2 / L3 / L4 / L5–9 / L10+ 개체 수',['원인',*titles],body)
body=[]
for cl in ['blind','unreachable7','reachable2+','adjacent']:
    body.append([cl]+[' / '.join('%.2f%%'%(100*e['class:'+cl]/e['turns']) for e in s['counts']) for s in S.values()])
evidence+=table('[M] 시작 상태 부류별 차례 비율',['부류',*titles],body)
body=[]
for cl in ['blind','unreachable7','reachable2+','adjacent']:
    body.append([cl]+[' / '.join('%.2f'%(100*e['nat:'+cl]/e['class:'+cl]) for e in s['counts']) for s in S.values()])
evidence+=table('[M] 해당 부류 차례 100회당 자연 진주',['부류',*titles],body)
evidence+='''[M] 재현 순서(모두 저장소 루트, 쓰기는 이 폴더만):

```sh
nice -n 10 python3 -B data/codex/astra/midgame/ledger.py
nice -n 10 python3 -B data/codex/astra/midgame/scan.py
nice -n 10 python3 -B data/codex/astra/midgame/enrich.py
python3 -B data/codex/astra/midgame/summarize.py
python3 -B data/codex/astra/midgame/render.py
```

[M] ledger/scan은 완성된 행을 재사용한다. 수정 후 재계산하려면 해당 폴더의 출력만 별도 이름으로 옮긴 뒤 실행한다. 기보를 바꾸지 않는다. `*-scan-v2.jsonl`이 최종 집계이며 `summary.json`/`*-enrich.json`과 이 보고서는 이 자료에서 생성한다.
'''
(P/'evidence.md').write_text(evidence)
print('report words excluding tables:',len(' '.join(l for l in report.splitlines() if not l.startswith('|')).split()))
