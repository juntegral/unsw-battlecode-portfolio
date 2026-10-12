import sys,json
from pathlib import Path
from collections import Counter,deque
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/local']
import ladder_replay as lr
from count_local import Geo
O=Path(__file__).parent
for gid in [1513842,1513844,1513845]:
 d=json.loads((O/f'{gid}-detail.json').read_text());s=json.loads((O/f'{gid}-scan.json').read_text());W,H=d['W'],d['H']
 raw=[tuple(map(int,q[1:4])) for q in map(str.split,s['text'].splitlines()) if q[0]=='EDGE'];geo=Geo(W,H,raw)
 comps={};nc=0
 for x in range(W*H):
  if x in comps:continue
  q=deque([x]);comps[x]=nc
  while q:
   a=q.popleft()
   for k,b in geo.moves[a]:
    if k==0 and b not in comps:comps[b]=nc;q.append(b)
  nc+=1
 ts=d['turns'];print('\nGAME',gid,'components',Counter(comps.values()),'portals',sum(k==2 for e,k,p in raw))
 for side in [0,1]:
  t=[t for t in ts if t['side']==side];print('side',side,'components turns',Counter(comps[a['body'][0][1]*W+a['body'][0][0]] for a in t))
  hops=[(a['r'],a['id'],a['L'],a['body'][0],xy) for a in t for i,xy in a['moves'] if comps[a['body'][0][1]*W+a['body'][0][0]]!=comps[xy[1]*W+xy[0]]];print('cross component',len(hops),hops[:6])
  print('r<=100 pearls',sum(a['eats'] for a in t if a['r']<=100),'turns',sum(a['r']<=100 for a in t))
  print('visited<=100',len({tuple(xy) for a in t if a['r']<=100 for i,xy in a['moves']}))
 if gid==1513842:
  print('long260',[{k:t[k] for k in ['r','L','body','dirs','moves','splits','deaths']} for t in ts if t['id']==260 and t['r']>=480]);print('death',[x for x in s['deaths'] if x['round']==491])
  print('queen uniq',Counter(tuple(t['body'][0]) for t in d['qturns'][0]))
  print('stable longest losing',max(int(r) for r,z in s['snapshots'].items() if z['us']['longest']>=z['them']['longest'])+1)
 elif gid==1513845:
  print('queen350+',[{k:t[k] for k in ['r','L','body','dirs','splits']} for t in d['qturns'][0] if 349<=t['r']<=363])
 for side in [0,1]:
  print('qpath minmax',side,[(min(t['body'][0][i] for t in d['qturns'][side]),max(t['body'][0][i] for t in d['qturns'][side])) for i in [0,1]])
 print('outgrown total permanently',max((int(r) for r,z in s['snapshots'].items() if z['us']['total']>=z['them']['total']),default=-1)+1)
 root=lr.replay.load(Path(f'data/online/smoke/one13-k2-old/M{gid}.replay')).root();rnd=0;logs=[]
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:rnd=p.i32(0)
  if k==6:
   txt=p.text(0)
   if (gid==1513842 and ((p.i32(0)==260 and rnd>=480) or (rnd<=100 and ('portal' in txt.lower() or 'scout' in txt.lower())))) or (gid==1513844 and p.i32(0)==0 and rnd>=19) or (gid==1513845 and p.i32(0)==1 and rnd>=349):logs.append([rnd,p.i32(0),txt])
 print('logs',logs)
