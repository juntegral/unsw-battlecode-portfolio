import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from count_local import Geo
O=Path(__file__).parent
for gid in (1496858,1496859,1497630):
 d=json.loads((O/f'{gid}.json').read_text());w,h=d['w'],d['h'];qs=d['queens'];teams=d['teams'];g=Geo(w,h,d['edges']);xy=lambda c:(c%w,c//w)
 print('\nGAME',gid,'size',w,h,'Q',qs)
 ownqt=[t for t in d['qturns'] if t['id']==qs[0]]
 for t in ownqt[-3:]:
  B={int(i):b for i,b in t['bodies'].items()};head=t['start'][0];x,y=xy(head);occ={c:i for i,b in B.items() for c in b}
  print('QTURN',t['round'],'L',len(t['start']),'head',xy(head),'action',t['action'],'dirs',t.get('directions'),'steps',[xy(c) for c in t['steps']],'end',list(map(xy,t['end'])))
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    c=((y+dy)%h)*w+(x+dx)%w;i=occ.get(c)
    z='*' if c in t['pearls'] else '.'
    if i is not None:z=('Q' if i==qs[0] else 'K' if i==qs[1] else ('A' if teams[str(i)]==d['own'] else 'E'))+str(i) if B[i][0]==c else ('q' if i==qs[0] else 'a' if teams[str(i)]==d['own'] else 'e')
    row.append(z)
   print(' '.join(row))
  print('neighbors',[(s,kind,xy(c),occ.get(c)) for s,(kind,c) in zip('NESW',g.moves[head])])
  for i,b in B.items():
   if b[0] in g.window(head) and i!=qs[0]:print('visibleHead',i,'own',teams[str(i)]==d['own'],'len',len(b),'head',xy(b[0]),'visibleParts',sum(c in g.window(head) for c in b))
 qdeath=next(x for x in d['deaths'] if x['id']==qs[0]);print('death',qdeath)
 for t in d['turns']:
  if t['id']==qdeath['actor'] and qdeath['round']-2<=t['round']<=qdeath['round']:print('ATTACKER TURN',t['round'],t['id'],list(map(xy,t['start'])),t.get('directions'),list(map(xy,t['steps'])),t['eats'])
 print('births relevant',[b for b in d['births'] if b['child']==qdeath['actor'] or (qdeath['round']-3<=b['round']<=qdeath['round'] and any(c in g.window(ownqt[-1]['start'][0]) for c in b['body']))])
 def score(s):return(s['queen'],s['longest'],s['total'])
 ss=d['snaps'];bad=[int(r) for r,s in ss.items() if score(s[0])>=score(s[1])];print('last nonloss',max(bad,default=-1),'turn permanent',max(bad,default=-1)+1)
 print('long late deaths',[(x['round'],x['id'],len(x['body']),x['actor'],x['reason']) for x in d['deaths'] if x['side']==0 and len(x['body'])>=8 and x['round']>=300])
 print('close count',sum(z['distance']<=5 for z in d['close']),'examples',d['close'][:5],d['close'][-5:])
 for rr in [62,63,159,160,275,350,449,450,451,475,490,496,497,498,499]:
  if str(rr) in ss:print('SNAP',rr,ss[str(rr)])
