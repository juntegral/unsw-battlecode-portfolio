import sys,json,gzip
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from count_local import Geo
O=Path('data/codex/astra/sweep/0519/loss2')
out={}
for gid in [1491744,1492091,1492092]:
 a=json.load(gzip.open(O/f'{gid}-turns.json.gz','rt'));s=json.loads((O/f'{gid}-summary.json').read_text());w,h=a['w'],a['h'];g=Geo(w,h,a['raw']);ts=a['turns'];qi=str(s['queens']['us']);eq=str(s['queens']['them']);death=next(d['round'] for d in s['queen_deaths'] if d['side']=='us');res={};cache={}
 def xy(c):return [c%w,c//w]
 def dist(src):
  if src in cache:return cache[src]
  d={src:0};q=deque([src])
  while q:
   c=q.popleft()
   for n in g.adj[c]:
    if n not in d:d[n]=d[c]+1;q.append(n)
  cache[src]=d;return d
 nearest=[];queen_coords=set();post=0
 for t in ts:
  if t['r']<death:continue
  for stage in ['start','end']:
   b=t[stage]
   if qi in b or eq not in b:continue
   post+=1;queen_coords.add(tuple(xy(b[eq][0])));d=dist(b[eq][0])
   for i,v in b.items():
    if a['team'][i]==0:nearest.append((d.get(v[0],99999),t['r'],int(i),xy(v[0]),xy(b[eq][0])))
 res['postdeath_min']=min(nearest) if nearest else None;res['postdeath_states']=post;res['foe_positions']=sorted(queen_coords)
 if gid==1491744:
  t=next(t for t in ts if t['r']==453 and str(t['id'])==qi);res['own_count_at_death_turn']=sum(a['team'][i]==0 for i in t['start']);res['early_split_same_room']=[{k:t[k] for k in ['r','action','splits','start','end']} for t in ts if t['r']==168 and str(t['id'])==qi]
 if gid==1492091:
  t=next(t for t in ts if t['r']==129 and str(t['id'])==qi);res['safe_other_move']={'head':xy(t['start'][qi][0]),'E':[g.moves[t['start'][qi][0]][1][0],xy(g.moves[t['start'][qi][0]][1][1])],'nextE_exits':[(k,xy(c)) for k,c in g.moves[t['start'][qi][0]][1][1]]} if False else {}
 if gid==1492092:
  res['attacker']=[{'r':t['r'],'actor':t['id'],'head':xy(t['start'][str(t['id'])][0]),'L':len(t['start'][str(t['id'])]),'foe922':list(map(xy,t['start'].get('922',[]))),'action':t['action'],'updates':[list(map(xy,u['body'])) for u in t['updates'] if u['id']==922]} for t in ts if 474<=t['r']<=478 and t['id'] in [0,922]]
  res['long_deaths']=[{'r':t['r'],'actor':t['id'],'victim':d['id'],'L':len(d['body']),'reason':d['reason']} for t in ts for d in t['deaths'] if t['r']>=400 and a['team'][str(d['id'])]==0 and len(d['body'])>=15]
  res['end_both']={side:sorted([(int(i),len(v),xy(v[0])) for i,v in ts[-1]['end'].items() if a['team'][i]==side],key=lambda v:-v[1]) for side in [0,1]}
 out[gid]=res;print(gid,json.dumps(res,ensure_ascii=False),flush=True)
(O/'details.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
