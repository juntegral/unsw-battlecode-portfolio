import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path('data/analysis/ladder/dossier/local').resolve()))
from count_local import Geo
OUT=Path(__file__).parent
for gid in (1493878,1493879,1493880):
 d=json.loads((OUT/f'{gid}.json').read_text());w,h=d['w'],d['h'];geo=Geo(w,h,d['edges']);q=d['queens'][0];xy=lambda c:(c%w,c//w)
 print('\nGAME',gid,'queens',d['queens'])
 for t in [t for t in d['queen_turns'] if t['id']==q][-3:]:
  hd=t['start'][0];occ={c:('Q' if int(i)==q and n==0 else 'q' if int(i)==q else ('A' if d['teams'][i]==0 else 'E') if n==0 else ('a' if d['teams'][i]==0 else 'e')) for i,b in t['bodies'].items() for n,c in enumerate(b)}
  print('r',t['r'],'head',xy(hd),'action',t.get('action'),'steps',[xy(c) for c in t['steps']])
  for dy in range(-3,4):print(''.join(occ.get(((hd//w+dy)%h)*w+(hd%w+dx)%w,'*' if ((hd//w+dy)%h)*w+(hd%w+dx)%w in t['pearls'] else '.') for dx in range(-3,4)))
  print('neighbors',[(name,kind,xy(dst),occ.get(dst,'.')) for name,(kind,dst) in zip('NESW',geo.moves[hd])])
  visible={i:[len(b),sum(c in geo.window(hd) for c in b),xy(b[0])] for i,b in t['bodies'].items() if any(c in geo.window(hd) for c in b)}
  print('visible',visible)
 print('QUEENDEATH',[(x['r'],x['actor'],x['actor_turn']) for x in d['deaths'] if x['id']==q])
 for lo,hi in [(124,200),(201,300),(301,350),(351,400),(401,499)]:
  for s in (0,1):
   ts=[t for t in d['turns'] if lo<=t['r']<=hi and d['teams'][str(t['id'])]==s]
   print('BAND',lo,hi,s,dict(turns=len(ts),splits=sum(bool(t['split']) for t in ts),natural=sum(e[1]=='spawn' for t in ts for e in t['eat']),dropped=sum(e[1]=='drop' for t in ts for e in t['eat']),steps=sum(len(t['steps']) for t in ts),noeat=sum(not t['eat'] for t in ts)))
 print('LARGE SPLITS',[(t['r'],t['id'],t['L'],t['split'],len(t['end'])) for t in d['turns'] if d['teams'][str(t['id'])]==0 and t['L']>=10 and t['split']])
 for r in [124,167,200,219,250,300,350,375,400,425,450,475,499]:print('STATE',r,d['rounds'][str(r)])
