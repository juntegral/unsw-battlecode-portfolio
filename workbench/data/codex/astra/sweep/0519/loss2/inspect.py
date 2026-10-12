import sys,json,gzip
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from count_local import Geo
O=Path('data/codex/astra/sweep/0519/loss2')
for gid in [1491744,1492091,1492092]:
 s=json.loads((O/f'{gid}-summary.json').read_text());a=json.load(gzip.open(O/f'{gid}-turns.json.gz','rt'));ts=a['turns'];w,h=a['w'],a['h'];g=Geo(w,h,a['raw']);qid=str(s['queens']['us']);foe=str(s['queens']['them']);qt=[t for t in ts if str(t['id'])==qid];last=qt[-1]['r'];keep=[]
 def xy(c):return (c%w,c//w)
 def board(t):
  b=t['start'];cen=b[qid][0];occ={c:('Q' if i==qid and k==0 else 'q' if i==qid else 'A' if a['team'][i]==0 and k==0 else 'a' if a['team'][i]==0 else 'E' if k==0 else 'e') for i,v in b.items() for k,c in enumerate(v)}
  lines=[]
  for dy in range(-3,4):
   cells=[((cen//w+dy)%h)*w+(cen%w+dx)%w for dx in range(-3,4)]
   lines.append(''.join('+'+('-' if g.moves[c][0][0]==1 else 'P' if g.moves[c][0][0]==2 else ' ') for c in cells)+'+')
   lines.append(''.join(('|' if g.moves[c][3][0]==1 else 'P' if g.moves[c][3][0]==2 else ' ')+occ.get(c,'*' if c in t['pearls'] else '.') for c in cells)+('|' if g.moves[cells[-1]][1][0]==1 else 'P' if g.moves[cells[-1]][1][0]==2 else ' '))
  lines.append(''.join('+'+('-' if g.moves[c][2][0]==1 else 'P' if g.moves[c][2][0]==2 else ' ') for c in cells)+'+')
  return '\n'.join(lines)
 print('\nGAME',gid,w,h)
 for t in qt[-3:]:
  print('ROUND',t['r'],'BODY',list(map(xy,t['start'][qid])),'ACTION',t['action'],'END',list(map(xy,t['end'].get(qid,[]))));print(board(t))
  hd=t['start'][qid][0];print('neighbors',[(d,k,xy(c),[(i,v.index(c)) for i,v in t['start'].items() if c in v]) for d,(k,c) in enumerate(g.moves[hd])])
  print('near',[(i,len(v),xy(v[0])) for i,v in t['start'].items() if v[0] in g.window(hd)])
 for t in ts:
  if last-4<=t['r']<=last+1 and (str(t['id'])==qid or any(str(d['id'])==qid for d in t['deaths']) or (gid==1492092 and (t['id']==922 or any(922 in sp for sp in t['splits'])))):
   keep.append(t);print('EVENT',t['r'],t['id'],t['action'],'eats',t['eats'],'splits',t['splits'],'deaths',t['deaths'])
 if gid!=1492092:
  coords=Counter(xy(t['start'][foe][0]) for t in ts if t['r']>last and foe in t['start']);print('foe postdeath positions',coords)
  print('queen eats/splits',[(t['r'],t['eats'],t['splits'],xy(t['start'][qid][0])) for t in qt if t['eats'] or t['splits']])
 else:
  print('late longest',[(r,sorted([(int(i),len(v)) for i,v in next(t for t in ts if t['r']==r)['start'].items() if a['team'][i]==0],key=lambda z:-z[1])[:6]) for r in [400,450,477,478,479,499]])
 (O/f'{gid}-keyframes.json').write_text(json.dumps({'w':w,'h':h,'team':a['team'],'raw':a['raw'],'turns':keep,'queen_last':qt[-3:]},separators=(',',':')))
