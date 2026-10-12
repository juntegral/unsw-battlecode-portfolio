import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'data/analysis/ladder/dossier/local'))
from count_local import Geo
O=Path(__file__).resolve().parent

def board(g,t):
 w,h=g['w'],g['h'];geo=Geo(w,h,g['edges']);x,y=t['head'];b={int(i):bb for i,bb in t['bodies'].items()};tm=g['teams'];q=g['queens'][0];p=set(t['pearls']);occ={c:('Q' if i==q else 'A' if tm[str(i)]==0 else 'B') if n==0 else ('q' if i==q else 'a' if tm[str(i)]==0 else 'b') for i,bb in b.items() for n,c in enumerate(bb)}
 lines=[]
 for dy in range(-3,4):
  top='';row=''
  for dx in range(-3,4):
   c=((y+dy)%h)*w+(x+dx)%w;edges=geo.moves[c]
   top+='+'+('-' if edges[0][0]==1 else 'P' if edges[0][0]==2 else ' ')
   row+=('|' if edges[3][0]==1 else 'P' if edges[3][0]==2 else ' ')+occ.get(c,'*' if c in p else '.')
  lines.extend([top+'+',row+('|' if edges[1][0]==1 else 'P' if edges[1][0]==2 else ' ')])
 lines.append(''.join('+'+('-' if geo.moves[((y+3)%h)*w+(x+dx)%w][2][0]==1 else ' ') for dx in range(-3,4))+'+')
 visible=[]
 for i,bb in b.items():
  def inview(c):
   dx=abs(c%w-x);dy=abs(c//w-y);return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
  if any(inview(c) for c in bb):visible.append((i,'AB'[tm[str(i)]],len(bb),[bb[0]%w,bb[0]//w],sum(inview(c) for c in bb)))
 return '\n'.join(lines),visible

for gid in (1510787,1510788,1510789):
 g=json.loads((O/f'{gid}.json').read_text());q=g['queens'][0];d=next(d for d in g['deaths'] if d['id']==q);ats=[t for t in g['turns'] if t['id']==q and t['event']<d['event']][-3:]
 print('\nGAME',gid,'DEATH', {k:v for k,v in d.items() if k not in ('bodies','turn')})
 for t in ats:
  print('TURN',{k:v for k,v in t.items() if k not in ('bodies','pearls')});bd,vis=board(g,t);print(bd);print('VISIBLE',vis)
 print('ATTACKER recent', [{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in g['turns'] if t['id']==d['actor'] and d['round']-3<=t['round']<=d['round']])
 print('OUR DEATHS', [{k:v for k,v in dd.items() if k not in ('bodies','turn','body')} for dd in g['deaths'] if dd['side']==0 and (gid!=1510789 or dd['round']>=300 and dd['L']>=12)])
 if gid==1510789:
  print('LAST50', {r:g['snaps'][str(r)] for r in (450,460,470,471,480,490,499)})
  print('LAST TURNS BIG', [{k:v for k,v in t.items() if k not in ('bodies','pearls')} for t in g['turns'] if t['round']==499 and t['L']>=20])
