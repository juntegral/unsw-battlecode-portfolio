import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from count_local import Geo
P=Path(__file__).parent
for gid in (1492093,1492094,1492095):
 d=json.loads((P/f'{gid}.json').read_text());w,h=d['w'],d['h'];g=Geo(w,h,d['raw']);xy=lambda c:(c%w,c//w)
 print('\nGAME',gid)
 for t in d['qturns'][0][-3:]:
  b=t['bodies'];hd=t['start'][0];occ={c:int(i) for i,bb in b.items() for c in bb}
  print('r',t['r'],'neighbors',[(dr,k,xy(dest),occ.get(dest),d['teams'].get(str(occ.get(dest)))) for dr,(k,dest) in enumerate(g.moves[hd])])
  print('bodies',[(i,'AB'[d['teams'][i]],list(map(xy,bb))) for i,bb in b.items() if any(c in g.window(hd) for c in bb)])
  for y in range(-3,4):
   row=''
   for x in range(-3,4):
    c=((hd//w+y)%h)*w+(hd%w+x)%w
    i=occ.get(c)
    char='*' if c in t['pearls'] else '.'
    if i is not None:char=('Q' if i==d['queens'][0] else 'A' if d['teams'][str(i)]==0 else 'B') if c==b[str(i)][0] else ('q' if i==d['queens'][0] else 'a' if d['teams'][str(i)]==0 else 'b')
    row+=char
   print(row)
  print('local edges',[(xy(c),dr,k) for c in sorted(g.window(hd)) for dr,(k,dest) in enumerate(g.moves[c]) if k])
 if gid==1492093:
  for x in d['deaths']:
   if x['i']==957:print('death957',x)
  print('final long',[(i,len(b),xy(b[0])) for i,b in d['final_bodies'].items() if len(b)>=10])
 if gid==1492094:
  print('near',d['near'])
 if gid==1492095:
  for t in d['turns']:
   if t['r']>=117 and t['i'] in (94,90,99):print('attack',t)
