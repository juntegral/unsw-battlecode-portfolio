import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter,defaultdict
sys.path[:0]=['tools','data/analysis/ladder/dossier']
from ladder_replay import replay,edge_id,canonical_edges
from count_dossier import Geo
OUT=Path(__file__).resolve().parent
JOBS=[(1514288,1514292),(1515123,1515123),(1515123,1515125)]

def analyze(battle,gid):
 folder=Path(f'data/online/live-one1/b{battle}')
 root=replay.load(folder/f'M{gid}.replay').root()
 W,H=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={};teams={};raw=[]
 for line in root.text(0).splitlines():
  q=line.split()
  if q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque(int(q[4+2*k])*W+int(q[3+2*k]) for k in range(int(q[2]))); teams[i]=int(q[1])
  elif q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
 geo=Geo(W,H,raw); edges=canonical_edges(W,H,raw)
 queens=[min(i for i in bodies if teams[i]==s) for s in [0,1]]
 base=json.loads((OUT/f'base-{gid}.json').read_text()); attacker=next(d['actor'] for d in base['deaths'] if d['id']==queens[1])
 def xy(c):return [c%W,c//W]
 def cell(p):x,y=replay.point(p);return y*W+x
 def visible(c,h):return min(abs(c%W-h%W),W-abs(c%W-h%W))<=3 and min(abs(c//W-h//W),H-abs(c//W-h//W))<=3
 def state():return {str(i):[len(b),xy(b[0])] for i,b in bodies.items()}
 def board():return {'bodies':{str(i):list(b) for i,b in bodies.items()},'pearls':sorted(pearls)}
 pearls=set(); rnd=-1;actor=None;turn=None;turns=[];snaps={};splits=[];deaths=[];near=[];qc=[]
 seen=defaultdict(set);firstcross={}; visits=defaultdict(Counter); meals=Counter(); portalturns=[]
 def close():
  nonlocal turn
  if turn is not None:
   turn['end']=xy(bodies[actor][0]) if actor in bodies else None;turn['L1']=len(bodies.get(actor,[]))
   turns.append(turn);turn=None
 def nearq(idx):
  if queens[1] in bodies or queens[0] not in bodies:return
  q=bodies[queens[0]][0]
  if q not in cache:cache[q]=geo.bfs([q])
  cand=[(cache[q][b[0]],i) for i,b in bodies.items() if teams[i]==1]
  if cand:
   dist,i=min(cand)
   if dist<=5:near.append([rnd,idx,i,dist,xy(bodies[i][0]),xy(q)])
 cache={}
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:
   close()
   if rnd>=0:snaps[rnd]=state()
   rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0);h=bodies[actor][0];vs={((h//W+dy)%H)*W+(h%W+dx)%W for dy in range(-3,4) for dx in range(-3,4)};seen[actor]|=vs
   turn=dict(r=rnd,event=idx,id=actor,s=teams[actor],L=len(bodies[actor]),h=xy(h),eat=0,moves=[],portals=[],a=None,dirs=[])
   visits[actor][h]+=1
   if actor==queens[1] or actor==attacker or (gid==1515123 and len(bodies[actor])>=20):
    turn['board']=board()
   if actor==queens[1]: qc.append(turn)
   blind=[d for d,(kind,dest) in enumerate(geo.moves[h]) if kind==2 and dest not in seen[actor]]
   if blind and teams[actor]==1 and len(bodies[actor])<4:
    turn['blind_adj']=blind;portalturns.append(turn)
   nearq(idx)
  elif k==3:
   c=cell(p.pointer(0))
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);turn['eat']+=1;meals[actor]+=1
  elif k==4:
   a=p.pointer(0);turn['a']=a.u16(0) if a else None
   turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
  elif k==9:
   i=p.i32(0);h=cell(p.pointer(0));tail=cell(p.pointer(1));b=bodies[i]
   if b[0]!=h:
    if i==actor:
     d=turn['dirs'][len(turn['moves'])];kind,dest=geo.moves[b[0]][d]
     if kind==2:
      turn['portals'].append([xy(b[0]),xy(h)]);firstcross.setdefault(str(i),rnd)
     turn['moves'].append(xy(h))
    b.appendleft(h)
   while len(b)>1 and b[-1]!=tail:b.pop()
   assert b[-1]==tail
   nearq(idx)
  elif k==10:
   parent,child=p.i32(0),p.i32(4);splits.append([rnd,parent,child,len(bodies[parent])])
   for z,i in enumerate([parent,child]):bodies[i]=deque(cell(c) for c in p.pointer(z));teams[i]=p.u16(8)
  elif k==11:
   i=p.i32(0);deaths.append(dict(r=rnd,id=i,actor=actor,reason=p.u16(4),L=len(bodies[i]),h=xy(bodies[i][0]),event=idx));bodies.pop(i);nearq(idx)
 close();snaps[rnd]=state()
 # First round after which the end-of-round side B never catches side A.
 def vals(st,s):
  ls=[v[0] for i,v in st.items() if teams[int(i)]==s]
  return [st.get(str(queens[s]),[0])[0],max(ls,default=0),sum(ls),len(ls)]
 curves={r:[vals(st,s) for s in [0,1]] for r,st in snaps.items()}
 def permanent(compare):
  bad=[r for r,v in curves.items() if not compare(v)]
  start=max(bad,default=-1)+1
  return start if start<=rnd else None
 final_long={str(s):sorted([(len(b),i,xy(b[0])) for i,b in bodies.items() if teams[i]==s],reverse=True)[:6] for s in [0,1]}
 summary=dict(gid=gid,W=W,H=H,queens=queens,attacker=attacker,final_long=final_long,permanent_total_behind=permanent(lambda v:v[1][2]<v[0][2]),permanent_longest_behind=permanent(lambda v:v[1][1]<v[0][1]),permanent_score_behind=permanent(lambda v:tuple(v[1][:3])<tuple(v[0][:3])),queen_last=[{k:v for k,v in t.items() if k!='board'} for t in qc[-3:]],near_after_death_count=len(near),near_first=near[:3],firstcross=firstcross,meals=dict(meals),longdeaths=[d for d in deaths if d['L']>=15])
 result=dict(summary=summary,teams=teams,turns=turns,curves=curves,snapshots=snaps,splits=splits,deaths=deaths,near=near,raw=raw)
 (OUT/f'detail-{gid}.json').write_text(json.dumps(result,separators=(',',':')))
 print(json.dumps(summary),flush=True)
if __name__=='__main__':
 for b,g in JOBS:analyze(b,g)
