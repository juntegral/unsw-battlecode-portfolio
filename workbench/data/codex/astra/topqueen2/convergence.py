import sys,json,time
from pathlib import Path
from collections import deque
from concurrent.futures import ProcessPoolExecutor,as_completed
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import replay
P=Path('data/codex/astra/topqueen2')
def scan(j):
 root=replay.load(Path(j['path'])).root();lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);heads={};teams={};hist={}
 for l in lines:
  q=l.split()
  if q and q[0]=='DRAGON':i=len(heads);heads[i]=(int(q[3]),int(q[4]));teams[i]=int(q[1]);hist[i]=deque(maxlen=4)
 queens=[min(i for i in heads if teams[i]==s) for s in (0,1)]
 def dist(a,b):
  dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return min(dx,w-dx)+min(dy,h-dy)
 rnd=-1;actor=None;out=[]
 for ev in root.pointer(3):
  k=ev.u16(0)
  if k not in (0,1,9,10,11):continue
  p=ev.pointer(0)
  if k==0:rnd=p.i32(0)
  elif k==1:actor=p.i32(0);hist[actor].append((rnd,heads[actor]))
  elif k==9:heads[p.i32(0)]=replay.point(p.pointer(0))
  elif k==10:
   for z,i in enumerate((p.i32(0),p.i32(4))):heads[i]=replay.point(next(iter(p.pointer(z))));teams[i]=p.u16(8);hist.setdefault(i,deque(maxlen=4))
  else:
   i=p.i32(0);reason=p.u16(4)
   if i==queens[teams[i]] and reason==3 and i!=actor and teams[i]!=teams[actor]:
    q=heads[i];near=[a for a,hd in heads.items() if teams[a]==teams[actor] and dist(hd,q)<=5];approach=[];unmeasured=[]
    for a in near:
     old=[(r,x) for r,x in hist[a] if rnd-3<=r<rnd]
     if not old:unmeasured.append(a)
     elif dist(old[0][1],q)>dist(heads[a],q):approach.append(a)
    out.append(dict(gid=j['gid'],r=rnd,side=teams[actor],victim=i,actor=actor,near5=near,approached3=approach,no_previous_turn=unmeasured))
   del heads[i]
 assert len(out)==len(j['kills']),(j['gid'],len(out),len(j['kills']))
 return out
if __name__=='__main__':
 jobs=[]
 for l in (P/'games.jsonl').read_text().splitlines():
  g=json.loads(l)
  if g['kills'] and ((g['version']==10) if '--late' in sys.argv else (g['src']=='top3' or g['version']==9)):jobs.append({k:g[k] for k in ['gid','path','kills']})
 out=json.loads((P/'convergence.json').read_text()) if '--late' in sys.argv else [];start=time.time()
 with ProcessPoolExecutor(max_workers=3) as pool:
  for n,f in enumerate(as_completed([pool.submit(scan,j) for j in jobs])):
   out.extend(f.result())
   if n%30==0:print(n+1,len(jobs),round(time.time()-start),flush=True)
 (P/'convergence.json').write_text(json.dumps(out,indent=2));print('DONE',len(out),round(time.time()-start),flush=True)
