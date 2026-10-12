import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local','data/analysis/ladder/dossier']
import scoreboard
from count_dossier import Geo
D=Path(__file__).resolve().parent
for gid,bid in [(1502776,1502774),(1502778,1502774),(1507592,1507592)]:
 g=json.loads((D/f'{gid}.json').read_text());w=g['width'];h=g['height'];root=scoreboard.load_replay(Path(f'data/online/live-one1/b{bid}/M{gid}.replay')).root(); raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];geo=Geo(w,h,raw)
 xy=lambda c:(c%w,c//w)
 print('\nGAME',gid)
 ds=[d for d in g['deaths'] if d['id']==g['queens']['us']]
 if ds:
  dr=ds[0]['round'];att=ds[0]['actor'];print('attacker',att,g['teams'][str(att)])
  for t in g['turns']:
   if dr-2<=t['round']<=dr and t['id']==att:print('attacker turns', {k:t[k] for k in ['round','id','body','length','steps','action','eats']})
  lines=[]
  for t in g['queen_turns'][-3:]:
   b=t['body'];cx,cy=xy(b[0]);occ={c:(int(i),k) for i,bb in t['scene'].items() for k,c in enumerate(bb)}; board=[]
   print('queen',t['round'],xy(b[0]),'foe body',list(map(xy,t['scene'].get(str(att),[]))))
   print('exits',[(d,k,xy(n),occ.get(n)) for d,(k,n) in enumerate(geo.moves[b[0]])])
   for yy in range(cy-3,cy+4):
    line=''
    for xx in range(cx-3,cx+4):
     c=(yy%h)*w+xx%w;i,k=occ.get(c,(-1,-1));ch='.'
     if c in t['pearls']:ch='*'
     if i>=0:
      ch=('Q' if k==0 else 'q') if i==g['queens']['us'] else ('X' if k==0 else 'x') if i==att else ('A' if k==0 else 'a') if g['teams'][str(i)]==g['ours'] else ('E' if k==0 else 'e')
     line+=ch
    board.append(line)
   lines.append(f"r{t['round']} head={xy(b[0])} L={len(b)} action={t['action']}\n"+'\n'.join(board))
  (D/f'boards-{gid}.txt').write_text('\n\n'.join(lines)+'\n');print('\n\n'.join(lines))
 else:
  t=g['queen_turns'][200];print('q200',xy(t['body'][0]),[(k,xy(n)) for k,n in geo.moves[t['body'][0]]])
 print('final long ids',sorted([(len(b),i,xy(b[0])) for i,b in g['final_bodies'].items()],reverse=True)[:6])
 for lo,hi in [(0,100),(101,300),(400,499)]:
  for s in ['A','B']:
   ts=[t for t in g['turns'] if lo<=t['round']<=hi and t['side']==s];print('window',lo,hi,s,'turns',len(ts),'eats',sum(t['eats'] for t in ts),'zero',sum(not t['eats'] for t in ts),'splits',sum(t['split'] is not None for t in ts))
