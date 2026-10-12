import json,sys
from pathlib import Path
from collections import Counter,defaultdict
P=Path(__file__).resolve().parent
G=[json.loads(p.read_text()) for p in P.glob('[0-9]*.json')]
def vals(g,lo,hi,s):
 t=[x for x in g['turns'] if lo<=x['r']<=hi and x['side']==s];e=[x for x in g['eats'] if lo<=x['r']<=hi and x['side']==s];d=[x for x in g['deaths'] if lo<=x['r']<=hi and x['side']==s]
 return dict(nat=sum(x['origin']=='natural' for x in e),corp=sum(x['origin']=='corpse' for x in e),splits=sum(x['split'] for x in t),deaths=len(d),turns=len(t),paid=sum(x['paid'] for x in t),causes=Counter(x['cause'] for x in d))
lines=[]
def put(x):lines.append(x)
for label in ('one8-c2','one10-c1','Cache pooled','one8-p1'):
 games=[g for g in G if g['label']==label or label=='Cache pooled' and '-c' in g['label']];n=len(games)
 if not n:continue
 put('\n'+label+' n='+str(n))
 put('|구간|종료 머리|자연|사체|분열|사망|3걸음 머리|진주 최단 점유 %|먹음/100턴|')
 put('|---|---|---|---|---|---|---|---|---|')
 for lo,hi in [(0,0)]+[(r-9,r) for r in range(10,101,10)]:
  V=[defaultdict(float),defaultdict(float)];C=[Counter(),Counter()]
  for g in games:
   snap=g['snaps'].get(str(hi),g['snaps'][str(max(map(int,g['snaps'])))])
   for s in (0,1):
    a=vals(g,lo,hi,s)
    for k,v in a.items():
     if k=='causes':C[s].update(v)
     else:V[s][k]+=v
    if snap:
     V[s]['heads']+=snap['heads'][s];V[s]['near3']+=snap['near3'][s];V[s]['nearest']+=snap['nearest'][s];V[s]['bearing']+=snap['bearing']
  pair=lambda k:'/'.join(f'{v[k]/n:.1f}' for v in V)
  put('|'+f'{lo}–{hi}|'+ '|'.join(pair(k) for k in ('heads','nat','corp','splits','deaths','near3'))+'|'+'/'.join(f'{100*v["nearest"]/max(1,v["bearing"]):.1f}' for v in V)+'|'+'/'.join(f'{100*(v["nat"]+v["corp"])/max(1,v["turns"]):.1f}' for v in V)+'|')
  put('<!-- death causes '+str([dict(c) for c in C])+' -->')
 sums=[defaultdict(float),defaultdict(float)]
 for g in games:
  for s in (0,1):
   for k,v in vals(g,0,100,s).items():
    if k!='causes':sums[s][k]+=v
 put('TOTAL '+json.dumps(sums))
 put('DEATH '+str([dict(Counter(x['cause'] for g in games for x in g['deaths'] if x['side']==s)) for s in (0,1)]))
 put('GATES '+str(Counter(x['gate'] for g in games for x in g['turns'] if x['side']==0 and x['L']>=4 and not x['split'])))
 put('SPLIT LENGTH '+str([dict(Counter(x['L'] for g in games for x in g['splits'] if x['side']==s)) for s in (0,1)]))
 put('START '+str([sum(g['initial'][s] for g in games)/n for s in (0,1)]))
mapgap=defaultdict(list)
for g in G:mapgap[g['map']].append(g)
put('\nMAPS')
for name,games in sorted(mapgap.items(),key=lambda kv:-sum(vals(g,0,100,1)['nat']+vals(g,0,100,1)['corp']-vals(g,0,100,0)['nat']-vals(g,0,100,0)['corp'] for g in kv[1])/len(kv[1])):
 put(name+' '+str([(g['gid'],sum(x['side']==1 for x in g['eats'])-sum(x['side']==0 for x in g['eats']),[vals(g,0,20,s) for s in (0,1)]) for g in games]))
(P/'tables.txt').write_text('\n'.join(lines))
print('games',len(G))
