import json,sys
from pathlib import Path
from collections import deque,Counter
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path('data/analysis/ladder/dossier/local').resolve()))
from count_local import Geo
OUT=Path(__file__).parent
for gid in (1488842,1488844):
 d=json.loads((OUT/f'{gid}-turns.json').read_text());w,h=d['w'],d['h'];g=Geo(w,h,d['edges']);teams={int(k):v for k,v in d['teams'].items()}
 xy=lambda c:(c%w,c//w)
 ts=d['turns'];qt=[t for t in ts if t['id']==0];death=qt[-1]['round']
 print('\nGAME',gid,'size',w,h)
 for t in qt[-6:]:
  print('Q',t['round'],'b',list(map(xy,t['b']['0'])),'dirs',t['dirs'],'step',[(i,xy(c)) for i,c in t['steps']], 'eat',list(map(xy,t['eats'])),'splits',t['splits'],'death',t['deaths'])
  hd=t['b']['0'][0];win=g.window(hd)
  print('near',[(i,teams[int(i)],list(map(xy,b))) for i,b in t['b'].items() if any(c in win for c in b)])
 for t in ts:
  if t['round'] in range(death-1,death+2) and (t['id'] in (0,21,28) or t['deaths']):print('EVENT',t['round'],t['id'],'b',list(map(xy,t['b'].get(str(t['id']),[]))),'dirs',t['dirs'],'steps',[(i,xy(c)) for i,c in t['steps']],'splits',t['splits'],'deaths',t['deaths'])
 cache={}
 def dist(src):
  if src not in cache:
   dd={src:0};q=deque([src])
   while q:
    c=q.popleft()
    for nxt in g.adj[c]:
     if nxt not in dd:dd[nxt]=dd[c]+1;q.append(nxt)
   cache[src]=dd
  return cache[src]
 near=[];minimum=(999,None);eqpos=Counter()
 for t in ts:
  if '0' in t['b'] or '1' not in t['b']:continue
  qb=t['b']['1'][0];eqpos[xy(qb)]+=1
  # Actor decisions: directed paths from our actor to queen through terrain, bodies ignored.
  if teams[t['id']]!=0:continue
  ah=t['b'][str(t['id'])][0];gap=dist(ah).get(qb,9999)
  rec=dict(round=t['round'],id=t['id'],length=len(t['b'][str(t['id'])]),head=xy(ah),queen=xy(qb),gap=gap,dirs=t['dirs'],eats=len(t['eats']))
  if gap<minimum[0]:minimum=(gap,rec)
  if gap<=5:near.append(rec)
 print('NEAR',len(near),'unique',len(set(t['id'] for t in near)),'minimum',minimum,'first',near[:4],'last',near[-4:]);print('enemy queen positions range',min(x for x,y in eqpos),max(x for x,y in eqpos),min(y for x,y in eqpos),max(y for x,y in eqpos),'top',eqpos.most_common(5))
 (OUT/f'{gid}-near.json').write_text(json.dumps(near,indent=2))
 # seven cells per row; tokens carry east and south edge marks to show all interior edges.
 lines=[]
 for t in qt[-3:]:
  hd=t['b']['0'][0];cx,cy=xy(hd);occ={c:(int(i),n) for i,b in t['b'].items() for n,c in enumerate(b)}
  lines.append(f"r{t['round']} 시작, 머리 {xy(hd)}, 행동 {t['dirs']} (0=N,1=E,2=S,3=W)")
  lines.append('```text')
  for dy in range(-3,4):
   cells=[]
   for dx in range(-3,4):
    c=((cy+dy)%h)*w+(cx+dx)%w
    if c in occ:
     i,n=occ[c];ch=('Q' if i==0 else 'K' if i==1 else 'A' if teams[i]==0 else 'E') if n==0 else ('q' if i==0 else 'k' if i==1 else 'a' if teams[i]==0 else 'e')
    else:ch='*' if c in t['pearls'] else '.'
    east,south=g.moves[c][1][0],g.moves[c][2][0]
    cells.append(ch+('|' if east==1 else '>' if east==2 else '.')+('_' if south==1 else 'v' if south==2 else '.'))
   lines.append(' '.join(cells))
  lines.append('```')
 (OUT/f'{gid}-boards.md').write_text('\n'.join(lines)+'\n')
