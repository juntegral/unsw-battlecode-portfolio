import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
P=Path('data/codex/astra/sweep/0544/loss2');sys.path.insert(0,'data/analysis/ladder/dossier/local')
from replay_format import load
from count_local import Geo
panels=[]
for gid in (1493881,1493882,1493883):
 d=json.loads((P/f'{gid}.json').read_text());w,h=d['w'],d['h'];root=load(f'data/online/smoke/one8-c2-old/M{gid}.replay').root();raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];g=Geo(w,h,raw)
 q=d['queens'][0];ts=[t for t in d['turns'] if t['id']==q][-3:];qd=next(v for v in d['deaths'] if v['id']==q);killer=qd['actor'];pan=[]
 for t in ts:
  hd=t['body'][0];x,y=hd%w,hd//w;occ={c:(int(i),j) for i,b in t['bodies'].items() for j,c in enumerate(b)};rows=[[' ']*15 for _ in range(15)]
  for yy in range(7):
   for xx in range(7):
    c=((y+yy-3)%h)*w+(x+xx-3)%w;i,j=occ.get(c,(-1,-1));ch='.'
    if c in t['pearls']:ch='*'
    if i>=0:ch=('Q' if i==q else 'X' if i==killer else 'A' if d['teams'][str(i)]==0 else 'B') if j==0 else ('q' if i==q else 'x' if i==killer else 'a' if d['teams'][str(i)]==0 else 'b')
    rows[2*yy+1][2*xx+1]=ch
    for direction,(kind,dest) in enumerate(g.moves[c]):
     dy,dx=((-1,0),(0,1),(1,0),(0,-1))[direction]
     if kind:rows[2*yy+1+dy][2*xx+1+dx]='@' if kind==2 else '-' if direction%2==0 else '|'
  pan.append(['r%d (%d,%d)'%(t['r'],x,y)]+[''.join(r) for r in rows])
  if t==ts[-1]:
   print(gid,'lastQ alternatives',[(k,(n%w,n//w),occ.get(n),kind) for k,(kind,n) in enumerate(g.moves[hd])]);print('pearl cells',[(c%w,c//w) for c in t['pearls'] if c in g.window(hd)])
   print('visible heads',[(i,(b[0]%w,b[0]//w),sum(c in g.window(hd) for c in b),len(b)) for i,b in t['bodies'].items() if d['teams'][i]==1 and b[0] in g.window(hd)])
 panels.append('### '+str(gid)+'\n\n```text\n'+'\n'.join('    '.join(p[row].ljust(18) for p in pan) for row in range(16))+'\n```')
(P/'boards.md').write_text('\n\n'.join(panels)+'\n')
