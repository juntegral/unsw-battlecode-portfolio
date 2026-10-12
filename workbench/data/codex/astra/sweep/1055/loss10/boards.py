import json,sys
from pathlib import Path
sys.path.insert(0,'tools');import ladder_replay as lr
O=Path('data/codex/astra/sweep/1055/loss10')
text=[]
for gid in (1504148,1504149):
 d=json.loads((O/f'{gid}-details.json').read_text()); W,H=d['W'],d['H'];ed={e:(k,p) for e,k,p in d['edges']};ts=d['selected'][:3];q=1 if gid==1504148 else 0;att=311 if gid==1504148 else 24
 text.append(f'### [M] {gid}: 차례 시작, 중심 Q; r'+', r'.join(str(t['r']) for t in ts))
 arr=[]
 for t in ts:
  cx,cy=t['start'][0];state={int(i):b for i,b in t['state'].items()};ps=set(map(tuple,t['pearls'])); grid=[]
  occ={tuple(c):(i,k) for i,b in state.items() for k,c in enumerate(b)}
  for dy in range(-3,4):
   y=(cy+dy)%H;above='';row=''
   for dx in range(-3,4):
    x=(cx+dx)%W;n=ed.get(lr.edge_id(W,H,x,y,0),(0,-1))[0];w=ed.get(lr.edge_id(W,H,x,y,3),(0,-1))[0]
    above+='+'+('-' if n==1 else 'P' if n==2 else ' ')
    who=occ.get((x,y));ch='*' if (x,y) in ps else '.'
    if who:
     i,k=who;ch=('Q' if k==0 else 'q') if i==q else ('X' if k==0 else 'x') if i==att else ('E' if k==0 else 'e')
    row+=('|' if w==1 else 'P' if w==2 else ' ')+ch
   above+='+';x=(cx+3)%W;east=ed.get(lr.edge_id(W,H,x,y,1),(0,-1))[0];row+=('|' if east==1 else 'P' if east==2 else ' ')
   grid.extend([above,row])
  y=(cy+3)%H;grid.append(''.join('+'+('-' if ed.get(lr.edge_id(W,H,(cx+dx)%W,y,2),(0,-1))[0]==1 else 'P' if ed.get(lr.edge_id(W,H,(cx+dx)%W,y,2),(0,-1))[0]==2 else ' ') for dx in range(-3,4))+'+')
  arr.append(grid)
 text.append('```text\n'+'   '.join(f'r{t["r"]} Q{tuple(t["start"][0])}' for t in ts)+'\n'+'\n'.join('    '.join(a[k] for a in arr) for k in range(15))+'\n```')
text.append('[M] Q/q 우리 여왕 머리/몸, X/x 실제 공격자 머리/몸, E/e 다른 적, * 진주, -/| 켈프, P 포털. 좌→우 x 증가, 위→아래 y 증가; 토러스 좌표. 모든 판면은 7×7칸이다.')
(O/'boards.md').write_text('\n\n'.join(text)+'\n')
