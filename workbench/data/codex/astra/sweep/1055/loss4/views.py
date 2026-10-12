import json,sys
from pathlib import Path
sys.path.insert(0,'tools')
from ladder_replay import edge_id,canonical_edges
O=Path(__file__).parent
out=[]
for gid in (1501675,1501676):
 r=json.loads((O/f'detail-{gid}.json').read_text());w,h=r['w'],r['h'];edges=canonical_edges(w,h,r['edges']);out.append(f'GAME {gid}')
 def xy(c):return (c%w,c//w)
 q=r['queens'][0];dq=next(d for d in r['deaths'] if d['id']==q);a=dq['actor']
 for t in r['qturns'][0][-3:]:
  head=t['body'][0];x,y=xy(head);board={int(i):b for i,b in t['board'].items()};occ={c:(i,j) for i,b in board.items() for j,c in enumerate(b)}
  out.append(f"r{t['r']} Q{q} {xy(head)} action {t['action']} -> {[xy(c) for c in t['end']]} attacker {a}: {[xy(c) for c in board.get(a,[])]}")
  near={i:[xy(c) for c in b] for i,b in board.items() if any(min(abs(c%w-x),w-abs(c%w-x))<=3 and min(abs(c//w-y),h-abs(c//w-y))<=3 for c in b)}
  out.append('IDs '+str(near))
  for yy in range(y-3,y+4):
   line='';cells=''
   for xx in range(x-3,x+4):
    xx%=w;cy=yy%h;c=cy*w+xx;kn=edges.get(edge_id(w,h,xx,cy,0),(0,-1))[0];kw=edges.get(edge_id(w,h,xx,cy,3),(0,-1))[0]
    line+='+'+('--' if kn==1 else 'PP' if kn==2 else '  ')
    z='*' if c in t['pearls'] else '.'
    if c in occ:
     i,j=occ[c];z=('Q' if j==0 else 'q') if i==q else ('X' if j==0 else 'x') if i==a else ('A' if j==0 else 'a') if r['teams'][str(i)]==0 else ('B' if j==0 else 'b')
    cells+=('|' if kw==1 else 'P' if kw==2 else ' ')+z+' '
   xx=(x+3)%w;ke=edges.get(edge_id(w,h,xx,yy%h,1),(0,-1))[0];out.append(line+'+');out.append(cells+('|' if ke==1 else 'P' if ke==2 else ' '))
  out.append(''.join('+'+('--' if edges.get(edge_id(w,h,xx%w,(y+3)%h,2),(0,-1))[0]==1 else 'PP' if edges.get(edge_id(w,h,xx%w,(y+3)%h,2),(0,-1))[0]==2 else '  ') for xx in range(x-3,x+4))+'+')
 print('\n'.join(out));out=[]
