import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd(); OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'data/analysis/ladder/dossier'))
from count_dossier import Geo

def show(gid):
 s=json.loads((OUT/f'{gid}.json').read_text());g=s['geometry'];W,H=g['W'],g['H'];geo=Geo(W,H,g['edges']);oq=s['queens']['us'];eq=s['queens']['them'];teams=s.get('teams',{})
 print('\nGAME',gid,'queens',oq,eq,'geometry',W,H)
 qd=next(d for d in s['deaths'] if d['id']==oq); print('Qdeath',qd)
 print('recent turns', [{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in s['qt'][-6:]])
 print('splits',[t for t in s['splits'] if t['id']==oq])
 print('near',min(s['near'],key=lambda x:x['d']) if s['near'] else None,'close',sum(x['d']<=5 for x in s['near']))
 for t in s['qt'][-3:]:
  print('ROUND',t['r'],'HEAD',t['head']);cx,cy=t['head']; grid=[[' ']*15 for _ in range(15)];occ={tuple(p):(int(i),j) for i,b in t['bodies'].items() for j,p in enumerate(b)};pearls=set(map(tuple,t['pearls']))
  for row in range(7):
   for col in range(7):
    x,y=(cx+col-3)%W,(cy+row-3)%H;v='*' if (x,y) in pearls else '.'
    if (x,y) in occ:
     i,j=occ[x,y];v=('Q' if j==0 else 'q') if i==oq else ('K' if j==0 else 'k') if i==eq else ('A' if j==0 else 'a') if teams.get(str(i))==0 else ('E' if j==0 else 'e')
    grid[2*row+1][2*col+1]=v
    for d,(kind,dst) in enumerate(geo.moves[y*W+x]):
     if kind:
      dr,dc=[(-1,0),(0,1),(1,0),(0,-1)][d];grid[2*row+1+dr][2*col+1+dc]='@' if kind==2 else '-' if d%2==0 else '|'
  print('\n'.join(''.join(row) for row in grid))
  print('near bodies',[(i,b) for i,b in t['bodies'].items() if any(geo.visible(y*W+x,cy*W+cx) for x,y in b)])
  print('exits',[(d,kind,(dst%W,dst//W),occ.get((dst%W,dst//W))) for d,(kind,dst) in enumerate(geo.moves[cy*W+cx])])
 print('long deaths',sorted([d for d in s['deaths'] if d['side']=='us' and d['round']>=350],key=lambda x:-x['length'])[:10])
 print('final long',sorted([(i,len(b),b[0]) for i,b in s.get('final_bodies',{}).items() if teams.get(i)==0],key=lambda x:-x[1])[:5])
for gid in (1507918,1507919,1507921):
 s=json.loads((OUT/f'{gid}.json').read_text())
 if 'teams' in s:show(gid)
