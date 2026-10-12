import json, math
from pathlib import Path
from collections import Counter
from statistics import mean
P=Path(__file__).parent
pairs=json.loads((P/'pairs.json').read_text())
gs=[json.loads(p.read_text()) for p in sorted(P.glob('[0-9]*.json'))]
by={l:[g for g in gs if g['src']==l] for l in ['one8-c1','one8-c2','one10-c1']}
checks=[]
for g in gs:
    for s in (0,1):
        residual=g['ends'][s][1]-g['snaps']['0'][s][1]-sum(e[1]==s and e[0]>0 for e in g['eats'])+sum(d[2] for d in g['deaths'] if d[1]==s and d[0]>0)+sum(p[3] for p in g['paids'] if p[1]==s and p[0]>0)
        assert residual==0,(g['gid'],s,residual)
        checks.append([g['gid'],s,residual])
assert len(gs)==len({g['gid'] for g in gs})==45
(P/'validation.json').write_text(json.dumps({'games':len(gs),'ledger_residuals':checks},indent=2))

def firstsplit(v):
    if v is None:return '—'
    return f'r{v[0]} L{v[3]}→{v[5]}+{v[6]}'
def firsteat(v):return f'r{v[0]}({v[3][0]},{v[3][1]})' if v else '—'
lines=['[M] 모든 짝은 우리 A/상대 B, 동일 지도·초기 배치, 서로 다른 시드. `c1→c2`; W/L은 우리 결과. 최초 분기는 이동·분열의 첫 차이이며 진주 생성 차이는 제외한다. 일치 턴은 상대의 연속 개막 턴(r0–30).','',
'|지도|게임 ID c1 / c2|결과|첫 분기 전체/상대 r|상대 일치 턴|상대 첫 분열 c1→c2|상대 첫 진주 c1→c2|우리 r100 진주 c1→c2|',
'|---|---|---|---|---|---|---|---|']
for r in pairs:
    assert r['same_map'] and r['sides']==[0,0]
    a,b=[json.loads((P/f'{i}.json').read_text()) for i in r['ids']]
    assert a['meta']['seed']!=b['meta']['seed']
    d=r['first']['r'];od=r['opponent']['r']
    if d is None:d=35
    if od is None:od=35
    def pairfmt(fn,key):
        x,y=fn(r['a'][key][1]),fn(r['b'][key][1]);return x+'→'+y if x!=y else x+' (같음)'
    lines.append('|'+ '|'.join([r['map'],f"{r['ids'][0]} / {r['ids'][1]}",'/'.join('W' if x=='win' else 'L' for x in r['result']),f'{d}/{od}',str(r['opponent']['matched']),pairfmt(firstsplit,'first_splits'),pairfmt(firsteat,'first_eats'),f"{r['a']['pearls100'][0]}→{r['b']['pearls100'][0]}"] )+'|')
lines+=['','[M] 상대 전 경기 행동. 램/1k=선제 적 머리충돌/상대 턴×1,000; 유료=실제 길이를 지불한 턴 수(무료 다중 이동 제외). Q는 r100/종료 길이. 전달= r301 이후 여왕이 먹은 아군 사망 진주; 의도적 먹이기라는 뜻은 아니다.','',
'|지도|램/1k c1→c2|유료 턴 c1→c2|Q(r100/끝) c1→c2|전달 c1→c2|',
'|---|---|---|---|---|']
for r in pairs:
    vals=[]
    for gid in r['ids']:
        g=json.loads((P/f'{gid}.json').read_text())
        rate=1000*sum(d[1]==1 and d[4]=='rams' for d in g['deaths'])/g['trace']['counts'][1]['turns']
        paid=sum(p[1]==1 for p in g['paids'])
        q=f"{g['snaps'].get('100',g['ends'])[1][3]}/{g['ends'][1][3]}"
        transfer=sum(e[0]>300 and e[1]==1 and e[2]=='q' and e[3]=='own' for e in g['eats'])
        vals.append([f'{rate:.2f}',str(paid),q,str(transfer)])
    lines.append('|'+r['map']+'|'+'|'.join(x+'→'+y for x,y in zip(*vals))+'|')
lines+=['','[M] 세트 합계/평균. 상대 램 길이는 차례 시작 길이.','',
'|지표|one8-c1|one8-c2|one10-c1|','|---|---|---|---|']
metrics=[('우리 승',lambda a:str(sum(g['result']=='win' for g in a))+'/15'),
 ('우리 r100 진주/용 수',lambda a:f"{mean(sum(e[1]==0 for e in g['trace']['eats']) for g in a):.1f}/{mean(g['snaps'].get('100',g['ends'])[0][0] for g in a):.1f}"),
 ('우리/상대 r100 여왕 생존',lambda a:'/'.join(str(sum(g['snaps'].get('100',g['ends'])[s][3]>0 for g in a)) for s in (0,1))),
 ('상대 턴/램/1k',lambda a:f"{sum(g['trace']['counts'][1]['turns'] for g in a)}/{sum(d[1]==1 and d[4]=='rams' for g in a for d in g['deaths'])}/{1000*sum(d[1]==1 and d[4]=='rams' for g in a for d in g['deaths'])/sum(g['trace']['counts'][1]['turns'] for g in a):.2f}"),
 ('상대 램 L2/L3/L4/L5+',lambda a:'/'.join(str(sum(d[1]==1 and d[4]=='rams' and (d[18][0]==L if L<5 else d[18][0]>=5) for g in a for d in g['deaths'])) for L in [2,3,4,5])),
 ('상대 유료 턴/지불 길이',lambda a:f"{sum(p[1]==1 for g in a for p in g['paids'])}/{sum(p[3] for g in a for p in g['paids'] if p[1]==1)}"),
 ('상대 r0–30 분열/여왕 분열',lambda a:f"{sum(v[1]==1 and v[0]<=30 for g in a for v in g['splits'])}/{sum(v[1]==1 and v[0]<=30 and v[5] for g in a for v in g['splits'])}"),
 ('상대 r301+ 행동 없음 사망/여왕 전달',lambda a:f"{sum(d[0]>300 and d[1]==1 and d[4]=='stop' for g in a for d in g['deaths'])}/{sum(e[0]>300 and e[1]==1 and e[2]=='q' and e[3]=='own' for g in a for e in g['eats'])}")]
for title,fn in metrics:lines.append('|'+title+'|'+'|'.join(fn(by[l]) for l in by)+'|')
(P/'tables.md').write_text('\n'.join(lines)+'\n')
print('45 games, 90 ledger checks passed')
