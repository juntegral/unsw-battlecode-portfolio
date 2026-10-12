import sys,json,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque
R=Path.cwd();P=R/'data/codex/astra/sweep/1055/loss23';sys.path.insert(0,str(R/'tools'));import ladder_replay as lr
spec=importlib.util.spec_from_file_location('m',R/'data/analysis/ladder/losses/counts/count_replays.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for gid in (1510790,1510791,1510793):
 d=json.loads((P/f'{gid}.json').read_text());ts=json.loads((P/f'{gid}-turns.json').read_text());q=d['queens']['us'];w=d['w'];h=d['h'];teams=d['teams']
 root=lr.replay.load(R/f'data/online/smoke/one13-c2-old/M{gid}.replay').root();raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];g=m.Geometry(w,h,raw)
 def attack(st,enemy,target,pearls):
  body=st[enemy];free=(len(body)+3)//4;blocked={c for i,b in st.items() if i!=enemy for c in b};queue=deque([(body,[],set())])
  while queue:
   b,path,eaten=queue.popleft();dep=len(path)
   if dep>=8 or (dep>=free and len(b)<=2):continue
   for kind,nxt in g.moves[b[0]]:
    if kind==1 or nxt in b or (nxt in blocked and nxt!=target):continue
    path2=path+[nxt]
    if nxt==target:return [[c%w,c//w] for c in path2]
    grow=nxt in pearls and nxt not in eaten;b2=[nxt]+b
    if not grow:b2.pop()
    if dep>=free:b2.pop()
    queue.append((b2,path2,eaten|({nxt} if grow else set())))
  return None
 for t in [t for t in ts if t['id']==q and ((len(t['body'])>2 and len(t['end'])==2) or t['round']==d['qdeath']['round'])]:
  st={int(i):b for i,b in t['state'].items()};head=t['body'][0];pe=set(t['pearls']);out=[]
  occupied={c for b in st.values() for c in b}
  for k,(kind,nxt) in enumerate(g.moves[head]):
   if kind==1 or nxt in occupied:continue
   after=st.copy();after[q]=[nxt]+st[q];after[q]=after[q] if nxt in pe else after[q][:-1]
   paths={i:attack(after,i,nxt,pe-{nxt}) for i in st if teams[str(i)]==1 and g.visible(head,st[i][0])};paths={i:p for i,p in paths.items() if p}
   out.append(dict(direction=k,dest=[nxt%w,nxt//w],attackers=paths))
  print(gid,t['round'],'length',len(t['body']),'legal first steps and static visible-head threats',json.dumps(out))
