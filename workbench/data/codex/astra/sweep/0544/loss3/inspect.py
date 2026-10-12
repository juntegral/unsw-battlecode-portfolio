import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path[:0]=['tools','data/analysis/ladder/dossier']
import ladder_replay as lr
from count_dossier import Geo
P=Path(__file__).resolve().parent
for g in (1493884,1493886,1493888):
 d=json.loads((P/f'{g}-detail.json').read_text());r=json.loads((P/f'{g}-ledger.json').read_text());w,h=d['w'],d['h'];root=lr.replay.load(f'data/online/smoke/one8-c2-old/M{g}.replay').root();raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];geo=Geo(w,h,raw)
 print('\nGAME',g)
 for t in d.get('long_turns',[]):
  i=str(t['id']);b=t['before'];hd=b[i][0];L=len(b[i]);at=[x['actor'] for x in r['deaths'] if x['id']==t['id'] and x['length']>=10];win=geo.window(hd)
  print('LONG',t['round'],i,'L',L,'head',(hd%w,hd//w),'tail visible',b[i][-1] in win,'act',t['action'],'steps',t['steps'],'nearfoes',[(z,len(bb),(bb[0]%w,bb[0]//w)) for z,bb in b.items() if d['teams'][z]==1 and bb[0] in win], 'attacker',[(z,len(b[str(z)]),(b[str(z)][0]%w,b[str(z)][0]//w)) for z in at if str(z) in b])
 if g==1493886:continue
 for t in d['queen_turns'][-3:]:
  b=t['before'];hd=b['0'][0];grid={c:'.' for c in geo.window(hd)}
  for c in t['pearls']:
   if c in grid:grid[c]='*'
  for i,bb in b.items():
   for k,c in enumerate(bb):
    if c in grid:grid[c]=('Q' if i=='0' else 'A' if d['teams'][i]==0 else 'X') if k==0 else ('q' if i=='0' else 'a' if d['teams'][i]==0 else 'x')
  print('BOARD',t['round'],(hd%w,hd//w),'L',len(b['0']))
  for dy in range(-3,4):print(''.join(grid[((hd//w+dy)%h)*w+(hd%w+dx)%w] for dx in range(-3,4)))
  for dr,(kind,c) in enumerate(geo.moves[hd]):print('NESW'[dr],kind,(c%w,c//w),[(i,bb.index(c)) for i,bb in b.items() if c in bb])
