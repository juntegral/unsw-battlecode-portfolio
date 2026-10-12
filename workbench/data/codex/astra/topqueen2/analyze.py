import sys, ast, types, json, time
from pathlib import Path
from collections import deque, Counter
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import replay
# Load existing geometry without executing tq2_scan's unguarded CLI.
p=Path('data/analysis/ladder/dossier/work/tq2_scan.py')
tree=ast.parse(p.read_text());tree.body=[n for n in tree.body if not(isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='main')]
mod=types.ModuleType('tq2_geometry');exec(compile(tree,str(p),'exec'),mod.__dict__);Geo=mod.Geo
OUT=Path('data/codex/astra/topqueen2')
BOTS={20980:5,21033:6,21086:7,21126:8,21165:9,21200:10}
geos={}
def scan(job):
 root=replay.load(Path(job['path'])).root();meta=json.loads(Path(job['meta']).read_text());ids=job['teams'];bot=[root.text(1),root.text(2)]
 version=None
 if 1119 in ids:
  val=bot[ids.index(1119)];version=BOTS.get(int(val)) if val.isdigit() else None
  if version is None or (version<9 and ids[1-ids.index(1119)] not in (87,952,989)):return None
 lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);bodies={};teams={};raw=[]
 for line in lines:
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 key=(w,h,tuple(sorted(raw)))
 if key not in geos:geos[key]=Geo(w,h,raw)
 geo=geos[key];queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 def xy(c):return [c%w,c//w]
 def dist(a,b):
  dx=abs(a%w-b%w);dy=abs(a//w-b//w);return min(dx,w-dx)+min(dy,h-dy)
 def visible(a,b):
  dx=abs(a%w-b%w);dy=abs(a//w-b//w);return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
 def snap():return [[len(bodies.get(queens[s],[])),sum(teams[i]==s for i in bodies),max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),sum(len(b) for i,b in bodies.items() if teams[i]==s)] for s in (0,1)]
 rnd=-1;actor=None;turn=None;used=0;dirs=[];act=2;present={};expected=deque();deaths=[];kills=[];snaps={};qt=[[],[]];qe=[[],[]];qs=[[],[]];fate=[None,None];lastviews=[None,None];defends=[[],[]];initial=snap();ledger=[[0,0,0],[0,0,0]]
 def close():
  if turn:
   i=turn['id'];s=teams[i];paid=turn['L']+turn['ate']-turn['split']-turn['death']-len(bodies.get(i,[]));assert paid>=0,(job['gid'],rnd,turn,paid)
   ledger[s][2]+=paid
   if i==queens[s]:
    qt[s][-1].update(after=len(bodies.get(i,[])),paid=paid,ate=turn['ate'],steps=used,act=act)
 def openq(i):
  s=teams[i];head=bodies[i][0];mates=[(z,b) for z,b in bodies.items() if teams[z]==s and z!=i];en=[(z,b) for z,b in bodies.items() if teams[z]!=s]
  q=dict(r=rnd,L=len(bodies[i]),head=xy(head),mate=min((dist(head,b[0]) for _,b in mates),default=None),enemy=min((dist(head,b[0]) for _,b in en),default=None),mates5=sum(dist(head,b[0])<=5 for _,b in mates),enemies5=sum(dist(head,b[0])<=5 for _,b in en),edge=min(head%w,w-1-head%w,head//w,h-1-head//w),kelp=geo.kelp[head],component=geo.comp[head],n=len(mates)+1)
  qt[s].append(q);lastviews[s]=(rnd,head,{z:(b[0],len(b)) for z,b in en if visible(head,b[0])})
 for ev in root.pointer(3):
  k=ev.u16(0)
  if k not in (0,1,3,4,9,10,11):continue
  p=ev.pointer(0)
  if k==0:
   close();turn=None
   if rnd>=0 and rnd in (99,199,299,399,499):snaps[rnd]=snap()
   rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);used=0;dirs=[];act=2;turn=dict(id=actor,L=len(bodies[actor]),head=bodies[actor][0],ate=0,split=0,death=0)
   if actor==queens[teams[actor]]:openq(actor)
  elif k==4:
   a=p.pointer(0);act=a.u16(0) if a else 2;dirs=list(a.pointer(0)) if a and act==0 and a.pointer(0) is not None else []
  elif k==3:
   x,y=replay.point(p.pointer(0));c=y*w+x
   if p.u32(0):
    assert c not in present
    if expected:
     cell,d=expected.popleft();assert c==cell;present[c]=d
    else:present[c]=None
   else:
    d=present.pop(c);s=teams[actor];turn['ate']+=1;ledger[s][0]+=1
    if actor==queens[s]:
     e=dict(r=rnd,xy=xy(c),origin='natural' if d is None else 'mate' if d['s']==s else 'enemy')
     if d:e.update(donor=d['id'],death_r=d['r'],donor_L=d['L'],cause=d['cause'],death_xy=d['head'],qdist=d['qdist'],lag=rnd-d['r'])
     qe[s].append(e)
  elif k==9:
   i=p.i32(0);x,y=replay.point(p.pointer(0));hd=y*w+x;x,y=replay.point(p.pointer(1));tl=y*w+x;b=bodies[i]
   if b[0]!=hd:b.appendleft(hd);used+=i==actor
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   parent,child=p.i32(0),p.i32(4);before=len(bodies[parent]);s=teams[parent]
   for z,i in enumerate((parent,child)):bodies[i]=deque(replay.point(pt)[1]*w+replay.point(pt)[0] for pt in p.pointer(z));teams[i]=p.u16(8)
   turn['split']+=len(bodies[child]);assert before==len(bodies[parent])+len(bodies[child])
   if parent==queens[s]:qs[s].append([rnd,before,len(bodies[parent]),len(bodies[child])])
  elif k==11:
   i=p.i32(0);reason=p.u16(4);s=teams[i];b=bodies[i];head=b[0];L=len(b);cause=['wall','self','body','ram','other'][reason]
   if reason==4:cause=['unpaid','illegal_split','no_action'][min(act,2)]
   d=dict(r=rnd,id=i,s=s,L=L,cause=cause,head=xy(head),qdist=dist(head,bodies[queens[s]][0]) if queens[s] in bodies and i!=queens[s] else None)
   deaths.append(d);ledger[s][1]+=L
   if i==actor:turn['death']+=L
   if i==queens[s]:fate[s]=d.copy()
   if reason==3 and i!=actor and teams[actor]!=s:
    a=actor;sa=teams[a];ah=bodies[a][0];aq=queens[sa]
    if i==queens[s]:
     lv=lastviews[s];start_heads=[(z,bb) for z,bb in bodies.items() if teams[z]==sa]
     hit=dict(r=rnd,victim=i,attacker=a,side=sa,L=turn['L'],steps=used+1,free=(turn['L']+3)//4,paid_before=turn['L']+turn['ate']-len(bodies[a]),pearls=turn['ate'],qL=L,own_q_dead=aq not in bodies,head=xy(head),from_xy=xy(turn['head']),view_at_last_qturn=(a in lv[2]) if lv else None,last_qturn=lv[0] if lv else None,near5=sum(dist(head,bb[0])<=5 for z,bb in start_heads),ids5=[z for z,bb in start_heads if dist(head,bb[0])<=5])
     kills.append(hit);fate[s]['ram']=hit
    if aq in bodies and a!=aq and dist(head,bodies[aq][0])<=5:
     defends[sa].append(dict(r=rnd,attacker=a,victim=i,L=turn['L'],q=xy(bodies[aq][0]),d=dist(head,bodies[aq][0])))
   assert not expected
   expected.extend((cell,d) for z,cell in enumerate(b) if z%2==0);del bodies[i]
 close();final=snap();snaps[rnd]=final;assert not expected
 for s in (0,1):
  st=root.pointer(4).pointer(s);assert final[s]==[st.i32(12),st.i32(0),st.i32(4),st.i32(8)],(job['gid'],s,final[s])
  assert initial[s][3]+ledger[s][0]-ledger[s][1]-ledger[s][2]==final[s][3],(job['gid'],s,'ledger')
 res=root.pointer(4);winner=res.u16(6) if res.u16(4)==1 else None
 how='wipe' if min(final[0][1],final[1][1])==0 else 'queen' if final[0][0]!=final[1][0] else 'longest' if final[0][2]!=final[1][2] else 'total' if final[0][3]!=final[1][3] else 'draw'
 scorewin=None if final[0]==final[1] else (0 if tuple([final[0][0],final[0][2],final[0][3]])>tuple([final[1][0],final[1][2],final[1][3]]) else 1)
 if how=='wipe':scorewin=0 if final[0][1] else 1
 assert winner==scorewin,(job['gid'],'winner',winner,scorewin)
 return dict(**job,version=version,bots=bot,map=meta['mapName'],w=w,h=h,queen=queens,final=final,how=how,winner=winner,last=rnd,snaps=snaps,turns=qt,eats=qe,splits=qs,fates=fate,kills=kills,defends=defends,ledger=ledger)

def wrapped(j):
 try:return scan(j),None
 except Exception as e:return None,[j['gid'],repr(e)]
def main():
 from concurrent.futures import ProcessPoolExecutor, as_completed
 jobs=json.loads((OUT/'inventory.json').read_text())['selected'];done=set()
 path=OUT/'games.jsonl'
 if path.exists():
  with path.open() as f:done={json.loads(l)['gid'] for l in f}
 jobs=[j for j in jobs if j['gid'] not in done]
 errors=[];start=time.time()
 with path.open('a') as f, ProcessPoolExecutor(max_workers=3) as pool:
  futures=[pool.submit(wrapped,j) for j in jobs]
  for n,fu in enumerate(as_completed(futures)):
   g,e=fu.result()
   if e:errors.append(e);print('ERROR',e,flush=True)
   if g:f.write(json.dumps(g,separators=(',',':'))+'\n');f.flush()
   if n%10==0:print(n+1,'/',len(jobs),'seconds',round(time.time()-start),flush=True)
 (OUT/'errors.json').write_text(json.dumps(errors,indent=2));print('DONE',round(time.time()-start),len(errors),flush=True)
if __name__=='__main__':main()
