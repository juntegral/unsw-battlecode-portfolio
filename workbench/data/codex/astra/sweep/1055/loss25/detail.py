import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,defaultdict,deque
sys.path.insert(0,str(Path('tools').resolve()))
import ladder_replay as lr
O=Path(__file__).parent
for gid in (1508916,1510463,1512747):
 s=json.loads((O/f'{gid}.json').read_text());W,H=map(int,s['text'].splitlines()[0].split()[1:3]);edges=lr.canonical_edges(W,H,[tuple(map(int,l.split()[1:4])) for l in s['text'].splitlines() if l.startswith('EDGE ')]);q=s['queens']['us'];eq=s['queens']['them'];qt=[t for t in s['queen_turns'] if t['id']==q];T=s['allturns']
 print('\nGAME',gid,W,H,'positions',s['enemy_positions']);print('lastq')
 def ek(c,d):return edges.get(lr.edge_id(W,H,*c,d),(0,-1))[0]
 for t in qt[-6:]:
  print('TURN',t['r'],t['head'],'L',t['L'],'end',t['end'],'split',t['split']);print('edges NESW', [ek(t['head'],d) for d in range(4)]);print('local',t['bodies'])
 print('our long final',[(i,len(b),b[:2]) for i,b in s['final_bodies'].items() if s['teams'][i]==s['ours']])
 print('our long deaths',[(d['id'],d['round'],d['length'],d['cause'],d['actor']) for d in s['deaths'] if d['side']=='us' and d['length']>=5])
 if gid==1512747:
  print('attacker', [t for t in T if t['id']==53 and 117<=t['r']<=120]);print('all turns 120',[(t['id'],t['L'],t['head'],t['steps'],t['eats']) for t in T if t['r']==120])
  snaps=s['snapshots'];bad=[int(r) for r,st in snaps.items() if st['us']['longest']>=st['them']['longest']];print('permanent longest lag',max(bad)+1)
  for r in (350,370,390,400,420,430,440,450,460,480,499):print(r,snaps[str(r)])
  print('long turns',[(t['r'],t['id'],t['L'],t['head'],t['eats'],t['split']) for t in T if t['r']>=350 and t['L']>=5 and s['teams'][str(t['id'])]==s['ours']][::10])
  for a,b in ((77,120),(121,300),(301,400),(401,499)):
   ts=[t for t in T if a<=t['r']<=b and s['teams'][str(t['id'])]==s['ours']];print('own window',a,b,'turns',len(ts),'eats',sum(t['eats'] for t in ts),'split',sum(t['split'] for t in ts),'moves',sum(len(t['steps']) for t in ts))
 # exact 7x7 cells with edge walls, 15 character raster
 lines=[]
 for t in qt[-3:]:
  x,y=t['head']; grid=[[' ']*15 for _ in range(15)]
  for yy in range(7):
   for xx in range(7):
    c=((x+xx-3)%W,(y+yy-3)%H);gy,gx=2*yy+1,2*xx+1;grid[gy][gx]=t['board'][yy][xx]
    for d,(dy,dx) in enumerate(((-1,0),(0,1),(1,0),(0,-1))):
     k=ek(c,d)
     if k:grid[gy+dy][gx+dx]='P' if k==2 else ('-' if d%2==0 else '|')
  lines+= [f'r{t["r"]} center={t["head"]} L{t["L"]}', '```text']+[''.join(row) for row in grid]+['```']
 (O/f'boards-{gid}.md').write_text('\n'.join(lines)+'\n')
