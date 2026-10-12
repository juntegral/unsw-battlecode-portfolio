import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier']
from ladder_replay import edge_id,canonical_edges
from count_dossier import Geo
P=Path(__file__).resolve().parent

def draw(x,t):
 W,H=x['summary']['W'],x['summary']['H'];qx,qy=t['h'];edges=canonical_edges(W,H,x['raw']);occ={};teams=x['teams']; attacker=x['summary']['attacker'];q=x['summary']['queens'][1]
 for i,b in t['board']['bodies'].items():
  for k,c in enumerate(b):occ[c]= ('Q' if int(i)==q else 'X' if int(i)==attacker else 'B' if teams[i]==1 else 'A') if k==0 else ('q' if int(i)==q else 'x' if int(i)==attacker else 'b' if teams[i]==1 else 'a')
 pearls=set(t['board']['pearls']);rows=[]
 for dy in range(-3,4):
  yy=(qy+dy)%H;top='';mid=''
  for dx in range(-3,4):
   xx=(qx+dx)%W
   kn=edges.get(edge_id(W,H,xx,yy,0),(0,-1))[0];kw=edges.get(edge_id(W,H,xx,yy,3),(0,-1))[0]
   top+='+'+('─' if kn==1 else 'P' if kn==2 else ' ')
   mid+=('│' if kw==1 else 'P' if kw==2 else ' ')+occ.get(yy*W+xx,'*' if yy*W+xx in pearls else '.')
  ke=edges.get(edge_id(W,H,(qx+3)%W,yy,1),(0,-1))[0]
  rows+=[top+'+',mid+('│' if ke==1 else 'P' if ke==2 else ' ')]
 rows.append(''.join('+'+('─' if edges.get(edge_id(W,H,(qx+dx)%W,(qy+3)%H,2),(0,-1))[0]==1 else 'P' if edges.get(edge_id(W,H,(qx+dx)%W,(qy+3)%H,2),(0,-1))[0]==2 else ' ') for dx in range(-3,4))+'+')
 return rows
if __name__=='__main__':
 for gid in [1514292,1515123,1515125]:
  f=P/f'detail-{gid}.json'
  if not f.exists():continue
  x=json.loads(f.read_text());s=x['summary'];q=s['queens'][1];turns=[t for t in x['turns'] if t['id']==q][-3:]
  print(gid);print('   '.join(f'r{t["r"]} head={t["h"]}'.ljust(24) for t in turns))
  for rows in zip(*(draw(x,t) for t in turns)):print('   '.join(a.ljust(24) for a in rows))
  for t in turns:
   W,H=s['W'],s['H'];hx,hy=t['h'];bb=t['board']['bodies'];vis=[]
   for i,b in bb.items():
    cells=[c for c in b if min(abs(c%W-hx),W-abs(c%W-hx))<=3 and min(abs(c//W-hy),H-abs(c//W-hy))<=3]
    if cells:vis.append([i,len(b),len(cells),[b[0]%W,b[0]//W],b[0] in cells])
   print(t['r'],'visible=',vis)
