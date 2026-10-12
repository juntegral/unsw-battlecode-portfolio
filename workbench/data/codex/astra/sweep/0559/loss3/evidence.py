import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
sys.path[:0]=['tools','data/analysis/ladder/dossier']
import ladder_replay as lr
from count_dossier import Geo
P=Path(__file__).resolve().parent
boards=[];summary={}
for gid in (1494961,1494962,1494964):
 d=json.loads((P/f'{gid}-detail.json').read_text());r=json.loads((P/f'{gid}-ledger.json').read_text());w,h=d['w'],d['h'];g=Geo(w,h,d['edges']);q=str(d['queens'][0]);ts=d['all_turns'];teams=d['teams'];xy=lambda c:(c%w,c//w)
 def neighbors(t,i):
  b=t['before'];occ={c:j for j,bb in b.items() for c in bb};hd=b[str(i)][0]
  return [('NESW'[di],kind,xy(dest),occ.get(dest)) for di,(kind,dest) in enumerate(g.moves[hd])]
 def board(t):
  hd=t['before'][q][0];cx,cy=xy(hd);occ={c:(i,k) for i,b in t['before'].items() for k,c in enumerate(b)};lines=[];ids={}
  for yy in range(-3,4):
   y=(cy+yy)%h;line=[];edges=[]
   for xx in range(-3,4):
    x=(cx+xx)%w;c=y*w+x;ii=occ.get(c);ch='*' if c in t['pearls'] else '.'
    if ii:
     i,k=ii;ch=('Q' if i==q else 'A' if teams[i]==0 else 'E') if k==0 else ('q' if i==q else 'a' if teams[i]==0 else 'e');ids[i]=teams[i]
    line.append(ch)
    flags=''.join('NESW'[di] for di,(kind,_) in enumerate(g.moves[c]) if kind==1)
    if flags:edges.append(f'{x},{y}:{flags}')
   lines.append(' '.join(line))
  return lines,ids
 qt=d['queen_turns']
 if gid!=1494962:
  for t in qt[-3:]:
   lines,ids=board(t);boards.append(dict(game=gid,round=t['round'],center=xy(t['before'][q][0]),rows=lines,ids=ids,neighbors=neighbors(t,q)));print('BOARD',gid,t['round'],xy(t['before'][q][0]));print('\n'.join(lines));print('neighbors',neighbors(t,q),'ids',ids)
 if gid==1494964:
  for t in ts:
   if t['id']==40 and t['round'] in (51,52,53):print('CHILD40',t['round'],neighbors(t,40),'Q',neighbors(t,q))
  eq=str(d['queens'][1]);eqt=[t for t in ts if str(t['id'])==eq];print('enemy Q positions',Counter(xy(t['before'][eq][0]) for t in eqt if t['round']>=54));print('enemy component',len([z for z in g.distances(eqt[-1]['before'][eq][0]) if z<65535]))
 if gid==1494961:
  for t in ts:
   if (t['id']==175 and t['round']==285) or (t['id']==168 and 285<=t['round']<=289):print('ATTACK/CHASE',t['round'],t['id'],t['before'].get('0'),neighbors(t,t['id']),t['action'],t['eaten'],t['steps'],'pearls',[(xy(v)) for v in t['pearls'] if v in (20+29*w,21+29*w)])
  t=qt[-1];print('attacker visible previously',[(t['round'],g.visible(t['before'][q][0],t['before']['175'][0])) for t in qt if '175' in t['before']][-10:])
 if gid==1494962:
  econ=json.loads((P/f'{gid}-economy.json').read_text());print('econ keys',econ.keys());print('ledger',econ.get('ledger'))
  # Natural and total consumption by replay turns, with actor identities.
  for side in (0,1):
   tt=[t for t in ts if teams[str(t['id'])]==side and t['round']<=30 and t['id'] not in d['queens']];print('EARLY',side,'turns',len(tt),'eat',sum(t['eaten'] for t in tt),'firsteat',next(((t['round'],t['id']) for t in tt if t['eaten']),None))
  for t in ts:
   if t['id'] in (55,96) and (t['round'] in (80,81,82,103,104)):print('LONG',t['round'],t['id'],t['before'][str(t['id'])],t['action'],t['eaten'])
  print('dead roles',Counter('rammed' if x['cause']=='head-on' and x['actor']!=x['id'] else x['cause'] for x in r['deaths'] if x['side']=='us'))
  print('early ate events',[(x) for x in econ['eats'][:10]])
 summary[str(gid)]={'final':r['final'],'bot':r['bots'],'end_round':r['last_round'],'anomalies':r['anomalies'],'last_not_behind':{k:max((int(rr) for rr,s in r['snapshots'].items() if s['us'][k]>=s['them'][k]),default=-1) for k in ('total','longest','queen_length')}}
(P/'boards.json').write_text(json.dumps(boards,ensure_ascii=False,indent=2));(P/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))

# Early supply access, excluding the isolated queens.
d=json.loads((P/'1494962-detail.json').read_text());g=Geo(d['w'],d['h'],d['edges']);stats={}
for side in (0,1):
 tt=[t for t in d['all_turns'] if d['teams'][str(t['id'])]==side and t['id'] not in d['queens'] and t['round']<=34]
 adjacent=visible=0
 for t in tt:
  head=t['before'][str(t['id'])][0];occupied={c for b in t['before'].values() for c in b};pearls=set(t['pearls'])
  adjacent+=any(kind!=1 and dst in pearls and dst not in occupied for kind,dst in g.moves[head])
  visible+=bool(g.window(head)&pearls)
 stats[side]=dict(nonqueen_turns_r0_34=len(tt),eaten=sum(t['eaten'] for t in tt),free_adjacent_pearl=adjacent,visible_pearl=visible)
(P/'school-early.json').write_text(json.dumps(stats,indent=2))
assert stats[0]['nonqueen_turns_r0_34']==133 and stats[0]['eaten']==0
for q in d['queens']:
 qt=next(t for t in d['all_turns'] if t['id']==q)
 assert sum(v<65535 for v in g.distances(qt['before'][str(q)][0]))==4
print('Early supply / both queen components verified',stats)
