import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path.cwd()/'data/analysis/ladder/dossier/local'))
from scoreboard import load_replay
O=Path(__file__).resolve().parent
for gid in (1510787,1510788,1510789):
 g=json.loads((O/f'{gid}.json').read_text());root=load_replay(Path(f'data/online/smoke/one13-c2-old/M{gid}.replay')).root();print('BOT',gid,repr(root.text(1)),repr(root.text(2)))
 q=g['queens'][0]
 for lo,hi in ((0,50),(51,100),(101,200),(201,300),(450,499)):
  ts=[t for t in g['turns'] if t['side']==0 and lo<=t['round']<=hi];qt=[t for t in ts if t['id']==q]
  print('BAND',lo,hi,'turns',len(ts),'eats',sum(t['eats'] for t in ts),'Qturns',len(qt),'Qeat',sum(t['eats'] for t in qt),'Qdistinct',len(set(tuple(t['head']) for t in qt)))
 for r in ([29,30,57,58,94,95,201,202,260,261,262,263] if gid==1510787 else [50,66,72,77,90,91,92,93,138] if gid==1510788 else [220,221,222,450,460,470,471,499]):
  ts=[t for t in g['turns'] if t['id']==q and t['round']==r]
  if ts:
   t=ts[0];print('Q',r,'L',t['L'],'action',t['actionKind'],'dirs',t['dirs'],'head',t['head'],'end',t['end'],'units',sum(g['teams'][str(i)]==0 for i in t['bodies']))
 if gid==1510789:
  for id in (926,1091,1214,1120):
   ts=[t for t in g['turns'] if t['id']==id and 450<=t['round']<=499];spl=[s for s in g['splits'] if s['parent']==id and s['round']>=450];print('LATE',id,'start',(ts[0]['round'],ts[0]['L']),'end',ts[-1]['endL'],'eat',sum(t['eats'] for t in ts),'steps',sum(len(t['steps']) for t in ts),'unique',len(set(tuple(t['head']) for t in ts)),'splits',spl)
   for r in (450,460,470,471,480,490,499):
    t=next((t for t in ts if t['round']==r),None)
    if t:print('pos',id,r,t['head'],t['L'],t['endL'])
  print('LONG SPLITS', [s for s in g['splits'] if s['round']>=400 and s['before']>=20 and g['teams'][str(s['parent'])]==0])
