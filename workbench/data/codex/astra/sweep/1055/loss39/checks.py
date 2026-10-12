import sys,json,importlib.util
from pathlib import Path
from collections import Counter,deque
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('cr','data/analysis/ladder/losses/counts/count_replays.py');cr=importlib.util.module_from_spec(s);s.loader.exec_module(cr)
for gid in (1506915,1506149,1506150):
 d=json.loads((P/f'{gid}-detail.json').read_text());b=json.loads((P/f'{gid}-base.json').read_text());w=d['w'];own=d['own'];g=cr.Geometry(w,d['h'],[tuple(map(int,x.split()[1:4])) for x in b['text'].splitlines() if x.startswith('EDGE ')]);q=b['queens']['us']
 print('GAME',gid)
 for metric in ('queen_length','total','pearls'):
  ties=[int(r) for r,ss in b['snapshots'].items() if ss['us'][metric]>=ss['them'][metric]];print('last >=',metric,max(ties))
 if gid==1506915:
  for t in d['focusqueen']:
   if t['round']!=174:continue
   occ={c:int(i) for i,bb in t['bodies'].items() for c in bb};hd=t['start'][0]
   for xy in ((20,6),(20,5),(21,6),(19,6)):
    c=xy[1]*w+xy[0];print('corridor alt',xy,'occupant',occ.get(c),'adj',[(k,(z%w,z//w),occ.get(z)) for k,z in g.moves[c]])
  for i in (1451,1489,1470):
   ts=[t for t in d['turns'] if t['id']==i];print('LONG',i,'firstlast',ts[0]['round'],ts[-1]['round'],'endlen',len(ts[-1]['end']))
   for lo,hi in ((400,410),(411,450),(451,499)):
    aa=[t for t in ts if lo<=t['round']<=hi];print(lo,hi,'turns',len(aa),'eat',sum(t['eats'] for t in aa),'headcells',len(set(c for t in aa for c in t['steps'])),'heads',Counter((t['start'][0]%w,t['start'][0]//w) for t in aa).most_common(4))
  print('late survivors',[(i,len(bb)) for i,bb in d['final'].items() if d['teams'][i]==own and len(bb)>=10])
 if gid==1506150:
  crosses=[];approaches=[]
  for t in d['turns']:
   if t['side']!=own or t['round']>100:continue
   hd=t['start'][0];ps=[(di,k,z) for di,(k,z) in enumerate(g.moves[hd]) if k==2]
   if ps:approaches.append((t['round'],t['id'],len(t['start']),(hd%w,hd//w),t['action']))
   c=hd
   for z in t['steps']:
    if any(k==2 and dst==z for k,dst in g.moves[c]):crosses.append((t['round'],t['id']))
    c=z
  print('portal crossings first100',crosses,'mouthturns',len(approaches),'samples',approaches[:12])
  for r in (20,50,100,318,377,410):
   ss=d['rounds'][str(r)];print('heads',r,[(i,(x[1]%w,x[1]//w),x[0]) for i,x in ss.items() if d['teams'][i]==own or int(i)==b['queens']['them']])
