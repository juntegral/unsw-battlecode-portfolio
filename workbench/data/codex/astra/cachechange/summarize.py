import json, math
from pathlib import Path
from collections import Counter
from statistics import mean
P=Path(__file__).parent
gs=[json.loads(p.read_text()) for p in sorted(P.glob('[0-9]*.json'))]
by={l:{g['map']:g for g in gs if g['src']==l} for l in ['one8-c1','one8-c2','one10-c1']}

def diff(a,b,s=None):
    x=[t for t in a['trace']['turns'] if s is None or t['side']==s]
    y=[t for t in b['trace']['turns'] if s is None or t['side']==s]
    for n,(t,u) in enumerate(zip(x,y)):
        if any(t[k]!=u[k] for k in ['r','id','action','moves','split']):
            return {'r':min(t['r'],u['r']),'matched':n,'a':t,'b':u}
    return {'r':None,'matched':min(len(x),len(y))}

out=[]
for m,a in by['one8-c1'].items():
    if m not in by['one8-c2']:continue
    b=by['one8-c2'][m]
    row=dict(map=m,ids=[a['gid'],b['gid']],result=[a['result'],b['result']],same_map=a['trace']['map_hash']==b['trace']['map_hash'],sides=[a['trace']['side'],b['trace']['side']],first=diff(a,b),opponent=diff(a,b,1),us=diff(a,b,0))
    for k,g in zip(['a','b'],[a,b]):
        row[k]=dict(first_splits=[next((v for v in g['trace']['splits'] if v[1]==s),None) for s in (0,1)],first_eats=[next((v for v in g['trace']['eats'] if v[1]==s),None) for s in (0,1)],pearls100=[sum(v[1]==s for v in g['trace']['eats']) for s in (0,1)],q100=g['snaps'].get('100',g['ends'])[0][3],queen_death=next((d for d in g['deaths'] if d[6] and d[1]==0),None))
    out.append(row)
(P/'pairs.json').write_text(json.dumps(out,indent=2))
for r in out:
    d=r['opponent'];t=d.get('a',{});u=d.get('b',{})
    print(r['map'],r['ids'],r['result'],'map',r['same_map'],'side',r['sides'],'first',r['first']['r'],'opp',d['r'],'same turns',d['matched'],'actor',t.get('id'),u.get('id'),'actions',t.get('action'),u.get('action'),'pearls',t.get('pearls'),u.get('pearls'),'foes',t.get('near_foes'),u.get('near_foes'))
for label,dd in by.items():
    arr=list(dd.values())
    if not arr:continue
    print('\n',label,len(arr),'win',sum(g['result']=='win' for g in arr),'bots',Counter(tuple(g['trace']['bots']) for g in arr))
    for s in (0,1):
        ds=[d for g in arr for d in g['deaths'] if d[1]==s]
        ram=[d for d in ds if d[4]=='rams']
        turns=sum(g['trace']['counts'][s]['turns'] for g in arr)
        paids=[p for g in arr for p in g['paids'] if p[1]==s]
        print('side',s,'turns',turns,'rams',len(ram),'rate',len(ram)*1000/turns,'ram lengths',dict(Counter(d[18][0] for d in ram)),'paid turns',len(paids),'paid rate',len(paids)*1000/turns,'paid seg',sum(p[3] for p in paids))
        print('early deaths',dict(Counter(d[4] for d in ds if d[0]<=100)),'early pearls',sum(sum(e[1]==s for e in g['trace']['eats']) for g in arr),'q100',sum(g['snaps'].get('100',g['ends'])[s][3]>0 for g in arr),'N100',mean(g['snaps'].get('100',g['ends'])[s][0] for g in arr))
        print('splits30',sum(v[1]==s and v[0]<=30 for g in arr for v in g['splits']),'Qsplits30',sum(v[1]==s and v[0]<=30 and v[5] for g in arr for v in g['splits']),'Qend', [g['ends'][s][3] for g in arr])
        print('stop>300',sum(d[0]>300 and d[4]=='stop' for d in ds),'drop>300 recovered Q/top',sum(d[12] for d in ds if d[0]>300 and d[4]=='stop'),'Qpearls>300',sum(e[1]==s and e[0]>300 and e[2]=='q' for g in arr for e in g['eats']))
