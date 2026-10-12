import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,deque
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from count_local import Geo
OUT=Path(__file__).resolve().parent
lines=[]
for gid in (1515662,1515664,1515667):
 d=json.loads((OUT/f'{gid}.json').read_text()); w,h=d['w'],d['h']; geo=Geo(w,h,d['edges']); q=d['queens'][0]; team=d['teams']; qdeath=next(x for x in d['deaths'] if x['id']==q); attacker=qdeath['actor']
 lines+= [f'## {gid} [M]']
 qt=[t for t in d['turns'] if t['id']==q][-3:]
 for t in qt:
  frame=t['frame']; hd=t['body'][0]; cx,cy=hd%w,hd//w; cells={}; ids={}
  for i,b in frame.items():
   for j,c in enumerate(b):
    ch=('Q' if int(i)==q else 'X' if int(i)==attacker else 'A' if team[i]==0 else 'B') if j==0 else ('q' if int(i)==q else 'x' if int(i)==attacker else 'a' if team[i]==0 else 'b')
    cells[c]=ch
   dx=min(abs(b[0]%w-cx),w-abs(b[0]%w-cx));dy=min(abs(b[0]//w-cy),h-abs(b[0]//w-cy))
   if max(dx,dy)<=3: ids[i]=[b[0]%w,b[0]//w,len(b)]
  rows=[]
  for dy in range(-3,4):
   top=''; row=''
   for dx in range(-3,4):
    c=((cy+dy)%h)*w+(cx+dx)%w
    top+='+'+('-' if geo.moves[c][0][0]==1 else 'P' if geo.moves[c][0][0]==2 else ' ')
    row+=('|' if geo.moves[c][3][0]==1 else 'P' if geo.moves[c][3][0]==2 else ' ')+cells.get(c,'*' if c in t['pearls'] else '.')
   rows.extend([top+'+',row+('|' if geo.moves[c][1][0]==1 else 'P' if geo.moves[c][1][0]==2 else ' ')])
  bottom=''
  for dx in range(-3,4):
   c=((cy+3)%h)*w+(cx+dx)%w; bottom+='+'+('-' if geo.moves[c][2][0]==1 else 'P' if geo.moves[c][2][0]==2 else ' ')
  rows.append(bottom+'+')
  lines += [f"r{t['round']} Q=({cx},{cy}), action={''.join('NESW'[v] for v in t['dirs'])}; heads (x,y,L)={ids}",'```',*rows,'```']
  occ={c:i for i,b in frame.items() for c in b}
  lines += [f"Adjacent N/E/S/W (edge, destination, occupant): {[(k,[c%w,c//w],occ.get(c)) for k,c in geo.moves[hd]]}"]
  print(gid,t['round'], 'heads',ids,'adj',[(k,[c%w,c//w],occ.get(c)) for k,c in geo.moves[hd]])
 # Late growth and movement by fixed windows.
 for lo,hi in ((0,49),(50,99),(100,199),(200,299),(300,399),(400,499)):
  ts=[t for t in d['turns'] if lo<=t['round']<=hi]
  lines += [f'{lo}-{hi} '+str([dict(turns=sum(t['side']==s for t in ts),eats=sum(t['eats'] for t in ts if t['side']==s),no_eat_moves=sum(t['side']==s and t['eats']==0 and bool(t['steps']) for t in ts)) for s in (0,1)])]
 lines += ['Last deaths: '+str([{k:v for k,v in z.items() if k not in ('frame','pearls','body')} for z in d['deaths'][-12:]])]
(OUT/'boards-and-counts.md').write_text('\n\n'.join(lines)+'\n')
