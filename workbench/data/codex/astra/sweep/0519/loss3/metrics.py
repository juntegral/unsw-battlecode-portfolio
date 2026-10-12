import json,sys
from pathlib import Path
from collections import deque
sys.dont_write_bytecode=True
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from count_local import Geo
P=Path(__file__).parent
out={}
for gid in (1492093,1492094,1492095):
 d=json.loads((P/f'{gid}.json').read_text());sn=d['snaps'];w=d['w'];g=Geo(w,d['h'],d['raw'])
 st={'permanent_behind':{key:max((int(r) for r,s in sn.items() if s[0][key]>=s[1][key]),default=-1)+1 for key in ('total','longest')},'near_turns':len(d['near'])}
 if gid==1492093:
  ts=[t for t in d['turns'] if 251<=t['r']<=350 and d['teams'][str(t['i'])]==0]
  st['r251_350']={'turns':len(ts),'L_le3':sum(len(t['start'])<=3 for t in ts),'splits':sum(t.get('action')==1 for t in ts),'natural':[sn['350'][s]['natural']-sn['250'][s]['natural'] for s in (0,1)]}
 if gid==1492094:
  paths=[]
  for n in d['near']:
   if not n['visible']:continue
   t=next(t for t in d['turns'] if (t['r'],t['i'])==(n['r'],n['i']));b=t['bodies'];target=b['1'][0];start=t['start'];occ={c for bb in b.values() for c in bb};free=(len(start)+3)//4
   todo=deque([(start[0],[],len(start),frozenset())]);seen=set();found=None
   while todo:
    c,path,L,eaten=todo.popleft()
    if len(path)>=5 or (len(path)>=free and L<=2):continue
    for k,dest in g.moves[c]:
     if k!=0:continue
     if dest==target:found=path+[dest];break
     if dest in occ or dest not in g.window(start[0]) or dest in path:continue
     eat=dest in t['pearls'] and dest not in eaten;newL=L+eat-(len(path)>=free);key=(dest,len(path)+1,newL)
     if key not in seen:seen.add(key);todo.append((dest,path+[dest],newL,eaten|{dest} if eat else eaten))
    if found:break
   if found:paths.append(dict(r=n['r'],i=n['i'],L=n['L'],path=[(x%w,x//w) for x in found],actual=t['dirs']))
  st['visible_static_clear_affordable_paths']=paths
 out[gid]=st
(P/'metrics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
