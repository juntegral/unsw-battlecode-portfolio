import sys,json
sys.dont_write_bytecode=True
sys.path[:0]=['data/analysis/ladder/dossier/local','tools']
from pathlib import Path
import scoreboard,ladder_replay as lr
from collections import Counter
O=Path(__file__).resolve().parent
for gid in (1517694,1517697,1517698):
 g=json.loads((O/f'{gid}.json').read_text());root=scoreboard.load_replay(Path(f'data/online/smoke/one14-c1-old/M{gid}.replay')).root();r=-1
 print('GAME',gid,'bots',root.text(1),root.text(2),'W/H',g['w'],g['h'])
 logs=[]
 for ev in root.pointer(3):
  p=ev.pointer(0);kind=ev.u16(0)
  if kind==0:r=p.i32(0)
  if kind==6:
   i=p.i32(0);msg=p.text(0)
   if (gid==1517698 and i==0 and 68<=r<=73) or (gid==1517697 and 299<=r<=305 and 'FEED' in msg):logs.append((r,i,msg))
 print('logs',logs)
 if gid==1517697:
  turns=[t for t in g['qturns'] if t['id']==1 and 70<=t['r']<=304];adj=[];vis=[]
  for t in turns:
   h=t['body'][0];ps=t['pearls'];w=g['w'];hh=g['h'];ds=lambda p:(min(abs(h[0]-p[0]),w-abs(h[0]-p[0])),min(abs(h[1]-p[1]),hh-abs(h[1]-p[1])))
   if any(sum(ds(p))==1 for p in ps):adj.append(t['r'])
   if any(max(ds(p))<=3 for p in ps):vis.append(t['r'])
  print('starvation turns',len(turns),'adjacent pearl turns',len(adj),adj,'visible pearl turns',len(vis))
  print('team r70:304 turns/splits/eats',sum(70<=t['r']<=304 and t['side']==0 for t in g['turns']),sum(70<=s['r']<=304 and g['teams'][str(s['parent'])]==0 for s in g['splits']),sum(len(t['eats']) for t in g['turns'] if 70<=t['r']<=304 and t['side']==0))
 if gid==1517694:
  print('r151:350 max units',max(s['us']['alive'] for r,s in g['snapshots'].items() if 151<=int(r)<=350))
  print('r261:350 our splits/eats',sum(261<=s['r']<=350 and g['teams'][str(s['parent'])]==0 for s in g['splits']),sum(len(t['eats']) for t in g['turns'] if 261<=t['r']<=350 and t['side']==0))
 if gid==1517698:
  print('qentry before r71 seen dest visits',[(t['r'],t['body'][0]) for t in g['qturns'] if t['id']==0 and t['r']<71 and abs(t['body'][0][0]-26)<=3 and abs(t['body'][0][1]-13)<=3])
  print('enemy r73/r499',[(t['r'],t['body'][0],len(t['body'])) for t in g['qturns'] if t['id']==1 and t['r'] in (73,499)])
