import sys,json,importlib.util
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('prior_analysis','data/codex/astra/sweep/0410/loss1/analyze.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
OUT=Path(__file__).resolve().parent
rows=[]
for gid,att in [(1488846,695),(1488847,312)]:
 x=json.loads((OUT/f'{gid}.json').read_text());ts=json.loads((OUT/f'{gid}-turns.json').read_text());ss=json.loads((OUT/f'{gid}-snapshots.json').read_text());root=a.lr.replay.load(Path(f'data/online/live-one1/b1488845/M{gid}.replay')).root();raw=[tuple(map(int,l.split()[1:])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];w,h=x['dim'];g=a.Geo(w,h,raw)
 qid=x['queens'][0];death=x['qdeaths'][0]['round'];qts=[t for t in ts if t['id']==qid];last=qts[-1];qh=last['start'];ab=last['bodies'][str(att)];end=last['steps'][-1];target=end[1]*w+end[0]
 def distance(src,dest,blocked=set()):
  dist={src:0};queue=deque([src])
  while queue:
   c=queue.popleft()
   if c==dest:return dist[c]
   for z in g.nxt[c]:
    if z>=0 and z not in dist and z not in blocked:dist[z]=dist[c]+1;queue.append(z)
  return None
 seen=[]
 for t in qts:
  b=t['bodies'].get(str(att),[]);hx,hy=t['start'];vis=[c for c in b if min(abs(c%w-hx),w-abs(c%w-hx))<=3 and min(abs(c//w-hy),h-abs(c//w-hy))<=3]
  if vis:seen.append([t['round'],len(b),len(vis),b[0] in vis])
 attack=next(t for t in ts if t['id']==att and t['round']==death)
 row=dict(gid=gid,seen=seen,attacker=attack,shortest_attack_distance=distance(ab[0],target),previous_snapshot=ss[str(death-1)],death_snapshot=ss[str(death)],total_deficit_since=max([int(r) for r,st in ss.items() if st[0]['total']>=st[1]['total']],default=-1)+1,bins=[],last_q_pearls=[[c%w,c//w] for c in last['pearls']],attacker_visible_last=sum(c in [cc for cc in ab if min(abs(cc%w-qh[0]),w-abs(cc%w-qh[0]))<=3 and min(abs(cc//w-qh[1]),h-abs(cc//w-qh[1]))<=3] for c in ab))
 for lo,hi in [(0,49),(50,99),(100,299),(300,death-1),(death,499)]:
  br=[]
  for side in [0,1]:
   sub=[t for t in ts if t['side']==side and lo<=t['round']<=hi];br.append(dict(turns=len(sub),eats=sum(t['eats'] for t in sub),empty_moves=sum(t['eats']==0 and t['action']['kind']==0 for t in sub),splits=sum('split'in t for t in sub)))
  row['bins'].append([lo,hi,br])
 positions=x['enemy_q_positions'];row['enemy_q_bounds']=[min(p[1][0] for p in positions),max(p[1][0] for p in positions),min(p[1][1] for p in positions),max(p[1][1] for p in positions)]
 row['queen_early']=dict(eats=sum(t['eats'] for t in qts if t['round']<=49),splits=sum('split' in t for t in qts if t['round']<=49),empty_moves=sum(t['eats']==0 and t['action']['kind']==0 for t in qts if t['round']<=49))
 rows.append(row)
(OUT/'details.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print(json.dumps([{k:v for k,v in r.items() if k!='last_q_pearls'} for r in rows],ensure_ascii=False,indent=2))
