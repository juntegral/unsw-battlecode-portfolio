import sys,json
from pathlib import Path
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parent
G=[json.loads(p.read_text()) for p in OUT.glob('game-*.json')]
def opp(g):
 m=g['meta'];s='B' if m['teamAId']==1119 else 'A';return m['team'+s+'Id']
def lower(g):
 m=g['meta'];s='A' if m['teamAId']==1119 else 'B';t='B' if s=='A' else 'A';return m.get('ranked') and m['team'+t+'Elo']<m['team'+s+'Elo']
loss=[g for g in G if opp(g)==133 and g['result']=='loss']; loss.sort(key=lambda g:g['gid'])
print('LOSSES')
for g in loss:
 us=[d for d in g['deaths'] if d[1]==0]; q=next(d for d in g['detail']['deaths'] if d['side']==0 and d['queen']);big=max(us,key=lambda x:x[2]);
 print(g['gid'],g['map'],g['bot'],'end',g['last'],g['ends'],'Q',q['r'],q['L'],q['reason'],'big',big,'stable',g['detail']['decisive_retrospective'])
 print('causes',dict(Counter(d[4] for d in us)),'drops',sum(d[15] for d in us),'enemy ate',sum(d[11] for d in us),'own ate',sum(d[10] for d in us))
 print('fastsplitdeaths',[(d[0],d[4],d[2]) for d in us if 0<=d[7]<=1][:12]);print('snaps',{r:[[s[0],s[1]] for s in sn] for r,sn in g['snaps'].items() if r in ['0','25','50','75','100','150','200','250','300','350','400','450','499']})
print('LOWER')
for g in sorted([g for g in G if lower(g)],key=lambda g:g['gid']):print(g['gid'],g['map'],opp(g),g['result'],g['how'],g['last'],g['ends'][0][:4],g['ends'][1][:4],g['bot'])
print('BYMAP ranked all')
by=defaultdict(list)
for g in G:
 if g['meta'].get('ranked'):by[g['map']].append(g)
for k,gs in sorted(by.items()):print(k,len(gs),[opp(g) for g in gs if g['result']=='loss'],[opp(g) for g in gs if g['result']=='win'])
print('METRICS match loss maps')
mapset={g['map'] for g in loss}
for group,gs in [('133',[g for g in G if opp(g)==133 and g['map'] in mapset]),('WHQ',[g for g in G if g['src']=='one5-w1' and g['map'] in mapset]),('Cache',[g for g in G if g['src']=='one5-c1' and g['map'] in mapset])]:
 c=Counter();d=Counter()
 for g in gs:
  c.update(g['detail']['metrics'][1]);d.update(g['detail']['metrics'][0])
 print(group,len(gs),dict(c),'ours',dict(d))
