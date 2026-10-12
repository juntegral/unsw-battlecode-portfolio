import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import Counter
P=Path('data/codex/astra/skku')
def forever(vals):
    out=None
    for r,a,b in reversed(vals):
        if a<b:out=r
        else:break
    return out
for p in sorted(P.glob('15*.json')):
    g=json.loads(p.read_text());s=g['scan'];d=g['detail'];b=g['base'];lo=g['loops']
    print('\nGAME',s['gid'],s['map'],s['result'],s['how'],'bot',s['bot'],'Q',d['queens'])
    print('LEDGER', '; '.join(str(r)+':'+ '/'.join(map(str,a[:4]))+'|'+ '/'.join(map(str,c[:4])) for r,(a,c) in s['snaps'].items() if int(r)%50==0 or int(r)==s['last']))
    es=[0,0];eatround=[]
    for r in range(s['last']+1):
        for e in s['eats']:
            if e[0]==r:es[e[1]]+=1
        eatround.append((r,*es))
    print('EAT cumulative behind',forever(eatround),'r50/100/200/300/end',[(r,a,c) for r,a,c in eatround if r in (50,100,200,300,s['last'])])
    print('MASS behind',forever([(int(r),v['us']['total'],v['them']['total']) for r,v in b['snapshots'].items()]))
    for sd in (0,1):
        sp=[x for x in d['splits'] if x['s']==sd];qt=d['qturn'][sd]
        print('SIDE',sd,'split first100/total',sum(x['r']<100 for x in sp),len(sp),'first',sp[:3])
        tt=[t for t in d['turns'] if t['s']==sd and t['id']!=d['queens'][sd] and t['L']>=4 and t['r']<100]
        print('nonqueen L4+ early split fraction',sum(t['split'] for t in tt),len(tt))
        print('queen splits',[(x['r'],x['L'],x['keep'],x['child']) for x in sp if x['queen']])
        print('queen location unique/home mean/max',len(set(tuple(x['h']) for x in qt)),round(sum(x['home'] for x in qt)/len(qt),2),max(x['home'] for x in qt),'start/end',qt[0]['h'],qt[-1]['h'])
        counts=Counter()
        for role in lo['cnt'][sd]:
            for phase in role:counts.update(phase)
        print('loops counts',dict(counts),'classes',lo['lc'][sd])
        eps=sorted([x for x in lo['eps'] if x['side']==sd and x['p']=='a2n'],key=lambda x:-(x['r1']-x['r0']))
        print('longest noeat loops',eps[:4])
    for qd in (x for x in d['deaths'] if x['id'] in d['queens']):
        print('QDEATH', {k:v for k,v in qd.items() if k not in ('last','body')})
        for last in qd['last']:
            t=next(t for t in d['turns'] if t['r']==last['r'] and t['id']==qd['id'])
            print(' QLAST', {k:v for k,v in last.items() if k not in ('bodies','pearls')},'TURN',t)
    if s['result']=='loss':
        print('large deaths',[(x['r'],x['id'],x['L'],x['reason'],x['actor']) for x in d['deaths'] if x['s']==0 and x['L']>=8][-15:])
