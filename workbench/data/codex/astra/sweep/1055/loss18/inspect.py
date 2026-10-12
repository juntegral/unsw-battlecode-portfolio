import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
from spawn import read
from count_local import Geo
from collections import Counter
D=Path(__file__).parent
for gid in (1506216,1506217,1506218):
 b=json.loads((D/f'{gid}-base.json').read_text());d=json.loads((D/f'{gid}-detail.json').read_text());q=b['queens']['us'];w=d['w'];h=d['h'];xy=lambda c:(c%w,c//w)
 root=read(Path(f'data/online/smoke/one13-c1-old/M{gid}.replay'))
 raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];g=Geo(w,h,raw)
 death=next(x for x in d['deaths'] if x['id']==q);att=death['actor'];last=[t for t in d['turns'] if t['id']==q][-3:]
 print('\nGAME',gid)
 for t in last:
  occ={c:i for i,bb in t['all'].items() for c in bb}
  print('TURN',t['r'],'queen',xy(t['body'][0]),'directions',t['dirs'],'pearls',list(map(xy,[c for c in t['pearls'] if c in g.window(t['body'][0])])))
  print('neighbors',[(name,k,xy(n),occ.get(n)) for name,(k,n) in zip('NESW',g.moves[t['body'][0]])])
  a=t['all'].get(str(att));print('attacker',list(map(xy,a)) if a else None)
  print('own nearby',[(i,len(bb),list(map(xy,bb))) for i,bb in t['all'].items() if d['teams'][i]==0 and any(c in g.window(t['body'][0]) for c in bb)])
 logs=[];r=-1
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:r=p.i32(0)
  if k==6:
   txt=p.text(0)
   if p.i32(0)==q and r>=last[0]['r']-4:logs.append((r,p.i32(0),txt))
 print('logs',logs)
 print('turn distribution queens',Counter((len(t['body']),len(t['moves'])) for t in d['turns'] if t['id']==q))
 # 7 x 7 cells, wall edges; true state at the start of the queen's own turn.
 rendered=[]
 for t in last:
  hd=t['body'][0];cx,cy=xy(hd);grid=[[' ']*29 for _ in range(15)]
  for dy in range(-3,4):
   for dx in range(-3,4):
    x,y=(cx+dx)%w,(cy+dy)%h;c=y*w+x;ry,rx=2*(dy+3)+1,4*(dx+3)+2
    ch='*' if c in t['pearls'] else '.'
    for i,bb in t['all'].items():
     if c in bb:
      ch=('Q' if int(i)==q else 'X' if int(i)==att else 'A' if d['teams'][i]==0 else 'B') if c==bb[0] else ('q' if int(i)==q else 'x' if int(i)==att else 'a' if d['teams'][i]==0 else 'b')
    grid[ry][rx]=ch
    for dd,(kind,dest) in enumerate(g.moves[c]):
     if not kind:continue
     yy=ry+(-1 if dd==0 else 1 if dd==2 else 0);xx=rx+(2 if dd==1 else -2 if dd==3 else 0)
     grid[yy][xx]='P' if kind==2 else '-' if dd%2==0 else '|'
     if kind==1 and dd%2==0:grid[yy][xx-1]=grid[yy][xx+1]='-'
  rendered.append([f'r{t["r"]} Q{q} {xy(hd)} -> {"".join("NESW"[n] for n in t["dirs"])}'.ljust(30)]+[''.join(row).ljust(30) for row in grid])
 block='\n'.join('  '.join(rows) for rows in zip(*rendered))
 (D/f'{gid}-boards.txt').write_text(block+'\n')
 print(block)
