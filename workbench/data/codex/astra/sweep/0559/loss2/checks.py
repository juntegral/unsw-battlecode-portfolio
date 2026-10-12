exec(open('data/codex/astra/sweep/0559/loss2/detail.py').read().split('for gid in (')[0])
for gid in (1494957,1494958,1494959):
 b=json.loads((OUT/f'{gid}-base.json').read_text());d=json.loads((OUT/f'{gid}-detail.json').read_text());w,h=d['w'],d['h'];raw=[tuple(map(int,x.split()[1:4])) for x in b['text'].splitlines() if x.startswith('EDGE ')];g=cr.Geometry(w,h,raw)
 print(gid)
 for t in d['queen']:
  hd=t['start'][0];bods={int(i):bb for i,bb in t['bodies'].items()};en=[(i,bb) for i,bb in bods.items() if d['teams'][str(i)]==1];occ={c for bb in bods.values() for c in bb}
  legal=[v for k,v in g.moves[hd] if k!=1 and v not in occ]
  # First-step head attack, then complete shortest paths through empty cells; queens excluded as in map_hits.
  def attack(dest):
   out=[]
   for i,bb in en:
    if i==b['queens']['them']:continue
    queue=deque([(bb[0],0)]);seen={bb[0]}
    while queue:
     c,dd=queue.popleft()
     if c==dest:out.append((i,dd,len(bb)));break
     if dd>=6:continue
     for k,v in g.moves[c]:
      if k!=1 and v not in seen and (v==dest or v not in occ):seen.add(v);queue.append((v,dd+1))
   return out
  print(t['round'],'legal',[((v%w,v//w),attack(v)) for v in legal])
 # count post-queen range of enemy queen by replay turn starts
 qdeath=next(x for x in b['deaths'] if x['id']==b['queens']['us']);tt=[t for t in d['turns'] if t['id']==b['queens']['them'] and t['round']>=qdeath['round']]
 if tt:
  xy=[(t['start'][0]%w,t['start'][0]//w) for t in tt];print('enemyQueenRange',min(x for x,y in xy),max(x for x,y in xy),min(y for x,y in xy),max(y for x,y in xy))
 # initial era no eat movement of original ids
 for i in (b['queens']['us'],2 if gid==1494958 else 3):
  ts=[t for t in d['turns'] if t['id']==i and t['round']<=50];print('early',i,'noeatmove',sum(t['eats']==0 and bool(t['steps']) for t in ts),'total',len(ts))
