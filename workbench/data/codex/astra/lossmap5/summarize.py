import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter
from statistics import mean
from analyze import snapshot

OUT = Path(__file__).resolve().parent
G = [json.loads(l) for l in (OUT/'games.jsonl').read_text().splitlines()]
LABELS = ('one5-w1', 'one5-c1', 'one5-d1')
CAUSE = {'rammed':'피격', 'rams':'선제충돌', 'mate head':'아군머리', 'foe body':'적몸', 'mate body':'아군몸', 'wall':'벽', 'own body':'자기몸', 'stop':'정지/행동실패'}

def dtext(d):
    return f"r{d['round']} {'우리' if d['side']=='us' else '상대'}#{d['id']} L{d['length']} {CAUSE[d['detail']]}" + (f"(행위자#{d['actor']})" if d['reason']==3 else f"({d['other']})" if d['reason']==4 else '')

def pair(g, r):
    s = snapshot(g,r)
    return ' : '.join(f"{s[t]['alive']}/{s[t]['total']}" for t in ('us','them'))

lines = []
def p(x=''):
    lines.append(x)

p('| [M] 분류 | WHQ | Cache | 주 표본 합계 | dev test 1(별도) |')
p('|---|---:|---:|---:|---:|')
for key,title in [('all','전체'),('win','승'),('loss','패'),('a','a: 전멸 또는 r150 머릿수 < 상대 절반'),('b','b: 여왕만'),('c','c: 최장 길이'),('d','d: 기타'),('elim','a 중 전멸')]:
    def count(gs):
        return sum(key=='all' or (g['result']==key if key in ('win','loss') else g['result']=='loss' and g['how']=='elim' if key=='elim' else g['bucket']==key) for g in gs)
    vals=[count([g for g in G if g['label']==label]) for label in LABELS]
    p(f"| {title} | {vals[0]} | {vals[1]} | {vals[0]+vals[1]} | {vals[2]} |")

for label in LABELS:
    p(f'\n[M] {label}: 모든 패배. N/L은 머릿수/총길이, 우리 : 상대. t는 실제 승부 기준의 마지막 동률·우세 라운드. tN은 머릿수 기준.\n')
    p('| 게임·지도·칸 | 묶음 / 최종 결정(우리:상대) | t / tN | t−30 → t−20 → t−10 → t 의 N/L | 직전30r 최대 단일 사망(우리 ; 상대) | t+1 변화·관련 사건 |')
    p('|---|---|---|---|---|---|')
    for g in G:
        if g['label']!=label or g['result']!='loss': continue
        t=g['last_level']; start=max(0,t-30)
        rounds=sorted(set(max(0,t-i) for i in (30,20,10,0)))
        window=[d for d in g['deaths'] if start<d['round']<=t]
        biggest=[]
        for side in ('us','them'):
            ds=[d for d in window if d['side']==side]
            biggest.append(dtext(max(ds,key=lambda d:d['length'])) if ds else '없음')
        event=[dtext(d) for d in g['deaths'] if d['round']==t+1 and (d['queen'] if g['how']=='queen' else d['side']=='us')]
        a,b=snapshot(g,t),snapshot(g,t+1)
        m=g['measure']
        delta=f"{a['us'][m]}:{a['them'][m]}→{b['us'][m]}:{b['them'][m]}"
        if g['how'] in ('queen', 'longest'):
            for sp in g['splits']:
                if sp[0] == t+1 and sp[1] == 0 and (sp[5] if g['how']=='queen' else sp[2]>=a['us'][m]):
                    event.append(f"우리{'여왕' if sp[5] else '용'} 분열 L{sp[2]}→{sp[3]}+{sp[4]}")
        if g['how']=='queen':
            qd=next((d for d in g['deaths'] if d['queen'] and d['side']=='us'), None)
            if qd and qd['round'] != t+1:
                event.append('여왕사망 '+dtext(qd))
        tn=str(g['last_count_level']) if g['last_count_level']>=0 else '시작(r0 전)'
        if g['final']['us']['alive'] >= g['final']['them']['alive']:
            tn += '(끝 동률/우세)'
        p(f"| {g['gid']} {g['map']} {g['cells']} | {g['bucket']} / {g['how']} {g['final']['us'][m]}:{g['final']['them'][m]} | {t} / {tn} | "+' → '.join(f"r{r} {pair(g,r)}" for r in rounds)+f" | {' ; '.join(biggest)} | {delta}"+(' ; '+'; '.join(event) if event else '')+' |')

p('\n[M] Cache: 동일한 체크포인트의 전체 15판. 각 칸은 N/L/Q/X(머릿수/총길이/여왕/최장), 우리 : 상대.\n')
p('| 게임·지도·칸 | 결과·결정 | r100 | r200 | r300 | 종료 N/L/Q/X |')
p('|---|---|---|---|---|---|')
for g in G:
    if g['label']!='one5-c1':continue
    vals=[]
    for r in (100,200,300):
        s=snapshot(g,r)
        vals.append(' : '.join('/'.join(str(s[t][k]) for k in ('alive','total','queen_length','longest')) for t in ('us','them'))+('†' if r>g['last_round'] else ''))
    final=' : '.join('/'.join(str(g['final'][t][k]) for k in ('alive','total','queen_length','longest')) for t in ('us','them'))
    p(f"| {g['gid']} {g['map']} {g['cells']} | {g['result']} {g['how']} | "+' | '.join(vals)+f' | {final} |')
p('\n| [M] Cache 집단 | r | 평균 N 우리:상대 | 평균 L 우리:상대 | 여왕 생존 판 우리:상대 | N≥상대 / L≥상대 판 |')
p('|---|---:|---|---|---|---|')
for result in ('win','loss'):
    gs=[g for g in G if g['label']=='one5-c1' and g['result']==result]
    if not gs:continue
    for r in (100,200,300):
        ss=[snapshot(g,r) for g in gs]
        vals=[' : '.join(f"{mean(s[t][k] for s in ss):.1f}" for t in ('us','them')) for k in ('alive','total')]
        qs=' : '.join(str(sum(s[t]['queen_length']>0 for s in ss)) for t in ('us','them'))
        lead=' / '.join(str(sum(s['us'][k]>=s['them'][k] for s in ss)) for k in ('alive','total'))
        p(f"| {result} ({len(gs)}) | {r} | {' | '.join(vals)} | {qs} | {lead} |")

p('\n| [M] a묶음 r0–150(조기 종료까지) | 분열 우리:상대 | 사망 우리:상대 | 우리 피격/전체 사망 | 우리 자연진주:상대 | r150 N 우리:상대 |')
p('|---|---|---|---|---|---|')
behavior=[]
for g in G:
    if g['bucket']!='a':continue
    end=min(150,g['last_round'])
    sp=[sum(s[0]<=end and s[1]==t for s in g['splits']) for t in (0,1)]
    ds=[sum(d['round']<=end and d['side']==t for d in g['deaths']) for t in ('us','them')]
    ram=sum(d['round']<=end and d['side']=='us' and d['detail']=='rammed' for d in g['deaths'])
    nat=[sum(e[0]<=end and e[1]==t and e[3]=='n' for e in g['ledger_eats']) for t in (0,1)]
    n=[snapshot(g,150)[t]['alive'] for t in ('us','them')]
    behavior.append(dict(gid=g['gid'],label=g['label'],splits=sp,deaths=ds,rammed=ram,natural=nat))
    p(f"| {g['label']} {g['gid']} {g['map']} | {sp[0]}:{sp[1]} | {ds[0]}:{ds[1]} | {ram}/{ds[0]} | {nat[0]}:{nat[1]} | {n[0]}:{n[1]} |")

early=json.loads((OUT/'early_behavior.json').read_text())
p('\n| [M] a묶음 r0–100 이동 행동 | 용 턴 우리:상대 | 미선점 도달가능 진주에 전진하지 않음 우리:상대 | 그중 한 걸음 옆 진주 | 전체 턴 대비 비전진 % 우리:상대 |')
p('|---|---|---|---|---|')
for e in early:
    pairs=[':'.join(map(str,e[k])) for k in ('turns','away','adjacent_away')]
    rates=':'.join(f"{100*a/n:.2f}" for a,n in zip(e['away'],e['turns']))
    p(f"| {e['gid']} {e['map']} | "+' | '.join(pairs)+f' | {rates} |')
(OUT/'tables.md').write_text('\n'.join(lines)+'\n')
(OUT/'behavior.json').write_text(json.dumps(behavior,ensure_ascii=False,indent=2)+'\n')
for label in LABELS:
    gs=[g for g in G if g['label']==label]
    print(label,len(gs),Counter(g['bucket'] for g in gs))
print('behavior',behavior)
