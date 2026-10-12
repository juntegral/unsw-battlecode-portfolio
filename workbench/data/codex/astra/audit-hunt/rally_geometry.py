import json
from collections import deque
import analyze as a
from concurrent.futures import ProcessPoolExecutor,as_completed

def work(path):
 data=json.loads(path.read_text());out=a.OUT/f"geometry-{data['gid']}.json"
 if out.exists():return
 if not data['candidates']:out.write_text('[]');return
 root=a.load_replay(a.Path(data['path'])).root();lines=[l.split() for l in root.text(0).splitlines()];w,h=map(int,lines[0][1:3]);geo=a.Geo(w,h,[tuple(map(int,l[1:4])) for l in lines if l[0]=='EDGE']);bs={};ts={}
 for q in lines:
  if q[0]=='DRAGON':
   i=len(bs);bs[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));ts[i]=int(q[1])
 own=ts[data['queens'][0]];dec=a.wire_decoder(w,h,2 if own==0 else 1);wanted={(c['r'],c['id']):c for c in data['candidates']};rnd=-1;actor=None;cur=None;rows=[];distance={}
 def finish():
  nonlocal cur
  if not cur:return
  if actor in bs and cur['wire']:
   wire=cur['wire'];cell=wire['cell'];src=bs[actor][0]
   if cell not in distance:distance[cell]=geo.bfs([cell])
   rows.append(dict(gid=data['gid'],version=data['version'],r=rnd,id=actor,source=src,target=cell,path_distance=distance[cell][src],**{k:v for k,v in cur['c'].items() if k not in ('id','r')}))
  cur=None
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:finish();rnd=p.i32(0)
  elif k==1:finish();actor=p.i32(0);c=wanted.get((rnd,actor));cur=dict(c=c,wire=None) if c else None
  elif k==9:
   i=p.i32(0);h1,t1=a.replay.point(p.pointer(0)),a.replay.point(p.pointer(1));hd,tail=h1[1]*w+h1[0],t1[1]*w+t1[0]
   if hd!=bs[i][0]:bs[i].appendleft(hd)
   while len(bs[i])>1 and bs[i][-1]!=tail:bs[i].pop()
  elif k==10:
   par,ch=p.i32(0),p.i32(4)
   for z,i in enumerate((par,ch)):bs[i]=deque(a.replay.point(c)[1]*w+a.replay.point(c)[0] for c in p.pointer(z))
  elif k==11:bs.pop(p.i32(0))
  elif k==12 and cur and p.i32(0)==actor:
   m=dec(p.u64(16))
   if m is not None and m>>63==0:cur['wire']=dict(cell=((m>>44)&127)*w+((m>>37)&127))
 finish();assert len(rows)==len(wanted),(data['gid'],len(rows),len(wanted));out.write_text(json.dumps(rows));return data['gid']
def main():
 paths=list(a.OUT.glob('game-*.json'))
 with ProcessPoolExecutor(max_workers=2) as pool:
  for f in as_completed([pool.submit(work,p) for p in paths]):print(f.result(),flush=True)
if __name__=='__main__':main()
