import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
from ladder_replay import replay,canonical_edges,edge_id
from pathlib import Path
P=Path('data/codex/astra/sweep/0444/loss3');a=json.loads((P/'1488841-detail.json').read_text())
r=replay.load('data/online/live-one1/b1488840/M1488841.replay').root();W,H=a['W'],a['H'];edges=canonical_edges(W,H,[tuple(map(int,l.split()[1:])) for l in r.text(0).splitlines() if l.startswith('EDGE ')])
boards=[]
for t in a['queen_turns']:
 if t['i']!=1 or t['r'] not in (135,136,137):continue
 x,y=t['head'];grid={}
 for i,b in t['bodies'].items():
  head,body=('Q','q') if i=='1' else ('T','t') if i=='174' else ('A','a') if a['teams'][i]==0 else ('E','e')
  for k,c in enumerate(b):grid[tuple(c)]=body if k else head
 pearls={tuple(c) for c in t['pearls']};lines=[]
 for dy in range(-3,4):
  row='';tiles=''
  for dx in range(-3,4):
   cx,cy=(x+dx)%W,(y+dy)%H
   n=edges.get(edge_id(W,H,cx,cy,0),(0,-1))[0];west=edges.get(edge_id(W,H,cx,cy,3),(0,-1))[0]
   row+='+'+('-' if n==1 else ':' if n==2 else ' ')
   tiles+=('|' if west==1 else ':' if west==2 else ' ')+grid.get((cx,cy),'*' if (cx,cy) in pearls else '.')
  cx,cy=(x+3)%W,(y+dy)%H;e=edges.get(edge_id(W,H,cx,cy,1),(0,-1))[0]
  lines.extend([row+'+',tiles+('|' if e==1 else ':' if e==2 else ' ')])
 row=''
 for dx in range(-3,4):
  cx,cy=(x+dx)%W,(y+3)%H;s=edges.get(edge_id(W,H,cx,cy,2),(0,-1))[0];row+='+'+('-' if s==1 else ':' if s==2 else ' ')
 lines.append(row+'+');boards.append(lines)
text='r135 (38,1)→W     r136 (37,1)→S     r137 (37,2)→W\n'+'\n'.join('   '.join(b[k] for b in boards) for k in range(15))
(P/'boards.txt').write_text(text+'\n');print(text)
