import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,'tools')
from ladder_replay import edge_id
O=Path('data/codex/astra/sweep/1055/loss6')
lines=[]
for gid in (1503502,1503503,1503504):
 j=json.loads((O/f'{gid}-fast.json').read_text());W,H=j['W'],j['H'];edges=dict(j['edges']);q=j['queens'][0];teams=j['teams'];boards=[]
 d=next(d for d in j['deaths'] if d['id']==q);atk=d['actor']
 for z in j['qboards']:
  b=z['bodies'];cx,cy=b[str(q)][0];tiles={tuple(c):'*' for c in z['pearls']}
  for i,body in b.items():
   for k,c in enumerate(body):tiles[tuple(c)]=('Q' if k==0 else 'q') if int(i)==q else ('X' if k==0 else 'x') if int(i)==atk else ('A' if k==0 else 'a') if teams[i]==0 else ('B' if k==0 else 'b')
  out=[list(' '*15) for _ in range(15)]
  for dy in range(-3,4):
   for dx in range(-3,4):
    x,y=(cx+dx)%W,(cy+dy)%H;rr,cc=(dy+3)*2+1,(dx+3)*2+1;out[rr][cc]=tiles.get((x,y),'.')
    for direct,(dr,dc) in enumerate(((-1,0),(0,1),(1,0),(0,-1))):
     k,p=edges.get(edge_id(W,H,x,y,direct),(0,-1))
     if k:out[rr+dr][cc+dc]='P' if k==2 else '-' if dr else '|'
  t=next(t for t in j['turns'] if t['id']==q and t['round']==z['round'])
  boards.append([f"r{z['round']} ({cx},{cy}) {''.join('NESW'[d] for d in t['dirs'])}"]+[''.join(r) for r in out])
 lines += [f'게임 {gid}, 여왕 #{q}, 공격자 #{atk}', '```text']
 lines += ['   '.join(b[r].ljust(23) for b in boards).rstrip() for r in range(16)]
 lines += ['```','']
(O/'boards.md').write_text('\n'.join(lines))
print('\n'.join(lines))
