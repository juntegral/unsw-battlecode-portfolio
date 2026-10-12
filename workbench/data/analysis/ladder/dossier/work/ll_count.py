import sys
sys.dont_write_bytecode=True
import json,time
from pathlib import Path
from collections import Counter,deque,defaultdict
from statistics import mean,quantiles
sys.path.insert(0,str(Path('tools').resolve()))
import ladder_replay as lr
rp=lr.replay
D=Path('data/analysis/ladder/dossier'); WORK=D/'work'
NS=(6,11,16,21,31); BANDS=('2-5','6-10','11-15','16-20','21-30','31-50','51+')
def band(n):
 return next((i for i,b in enumerate((5,10,15,20,30,50)) if n<=b),6)
def jobs():
 out=[];seen=set()
 for label in ('agg7-m1','sr51-bob1','agg7-m2','agg7-m3'):
  folder=Path('data/online/smoke')/(label+'-new')
  for p in sorted(folder.glob('M*.replay')):
   j=json.loads((folder/f'game-{p.stem[1:]}.json').read_text());assert j['id'] not in seen;seen.add(j['id'])
   out.append(('Online',p,'A' if j['teamAId']==1119 else 'B',j['id'],None,label))
 for name,path in [('Ladder',D/'per-game.jsonl'),('Rank1',D/'target/per-game-top1.jsonl')]:
  rows=[json.loads(s) for s in path.read_text().splitlines()];rows=[r for r in rows if r['relation']=='us'];assert len(rows)==(500 if name=='Ladder' else 597)
  for r in rows:out.append((name,Path(r['replay']),r['side'],r['game'],r['final_reconstructed'],'ladder'))
 return out
GEO={}
def geometry(text):
 W,H=map(int,text.splitlines()[0].split()[1:3]); raw=[tuple(map(int,q[1:4])) for line in text.splitlines() if (q:=line.split()) and q[0]=='EDGE']
 key=W,H,tuple(raw)
 if key in GEO:return GEO[key]
 ed=lr.canonical_edges(W,H,raw);port=defaultdict(list)
 for e,(k,p) in ed.items():
  if k==2:port[p].append(e)
 adj=[]
 for c in range(W*H):
  x,y=c%W,c//W;a=[]
  for d,(dx,dy) in enumerate(lr.base.STEP):
   e=lr.edge_id(W,H,x,y,d);k,p=ed.get(e,(0,-1))
   if k==1:continue
   if k==2:
    assert len(port[p])==2;other=next(z for z in port[p] if z!=e);row,xx=divmod(other,W+1);yy=row//2
    a.append(((yy-(d==0))%H)*W+(xx-(d==3))%W)
   else:a.append(((y+dy)%H)*W+(x+dx)%W)
  adj.append(a)
 near=[]
 for c in range(W*H):
  reached={c};front={c}
  for _ in range(3):front={v for u in front for v in adj[u]}-reached;reached.update(front)
  near.append(tuple(reached))
 GEO[key]=(W,H,near);return GEO[key]
def scan(job):
 name,path,own,gid,expected,label=job;root=rp.load(path).root();text=root.text(0);W,H,near=geometry(text)
 bodies={};sides={};lens=[Counter(),Counter()];heads=[Counter(),Counter()]
 tile=lambda p: (lambda xy:xy[1]*W+xy[0])(rp.point(p))
 for line in text.splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies);b=deque(int(q[4+2*k])*W+int(q[3+2*k]) for k in range(int(q[2])));s=int('AB'[int(q[1])]!=own);bodies[i]=b;sides[i]=s;lens[s][len(b)]+=1;heads[s][b[0]]+=1
 def longest(s):return max(lens[s],default=0)
 def remove_count(c,k):
  c[k]-=1
  if c[k]==0:del c[k]
 def state(s):return dict(alive=sum(lens[s].values()),longest=longest(s),total=sum(k*v for k,v in lens[s].items()))
 turns=Counter();close=Counter();rams=[];snaps={};rnd=0;actor=None;used=paid=0;eat=False;pending=None;turnlen=0
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0)
  if k not in (0,1,3,9,10,11):continue
  p=ev.pointer(0)
  if k==0:
   snaps[rnd]=longest(0);rnd=p.i32(0);actor=None
  elif k==1:
   actor=p.i32(0);used=paid=0;turnlen=len(bodies[actor]);eat=False
   if sides[actor]==0 and turnlen>=6:
    enemynear=any(heads[1].get(c,0) for c in near[bodies[actor][0]])
    for n in NS:
     if turnlen>=n:turns[n]+=1;close[n]+=enemynear
  elif k==3:
   if not p.u32(0):eat=True
  elif k==9:
   i=p.i32(0);b=bodies[i];s=sides[i];old=len(b);hd,tl=tile(p.pointer(0)),tile(p.pointer(1));moved=hd!=b[0]
   remove_count(lens[s],old);remove_count(heads[s],b[0])
   if moved:b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
   lens[s][len(b)]+=1;heads[s][b[0]]+=1
   if i==actor:
    used+=moved;cost=old+int(eat)-len(b);assert cost>=0,(gid,idx,cost);paid+=cost;eat=False
  elif k==10:
   parent,child=p.i32(0),p.i32(4);s=sides[parent];remove_count(lens[s],len(bodies[parent]));remove_count(heads[s],bodies[parent][0])
   for z,i in enumerate((parent,child)):
    b=deque(tile(pt) for pt in p.pointer(z));bodies[i]=b;sides[i]=s;lens[s][len(b)]+=1;heads[s][b[0]]+=1
  elif k==11:
   i,reason=p.i32(0),p.u16(4);b=bodies[i];s=sides[i];L=len(b)
   if reason==3 and i!=actor and s==0 and sides[actor]==1:
    pending=dict(game=gid,label=label,round=rnd,event=idx,dragon=i,length=L,leader=L>=longest(0)-2,own_longest_before=longest(0),rammer=actor,rammer_length=len(bodies[actor]),rammer_start_length=turnlen,steps_walked=used,collision_step=used+1,length_paid=paid)
    assert paid==max(0,used-(turnlen+3)//4),(gid,'paid',paid,used,turnlen)
    rams.append(pending)
   remove_count(lens[s],L);remove_count(heads[s],b[0]);del bodies[i]
   if pending and i==actor:pending['own_longest_after']=longest(0);pending=None
 assert pending is None
 snaps[rnd]=longest(0);final=[state(s) for s in (0,1)]
 for z,t in enumerate('AB'):
  s=int(t!=own);st=root.pointer(4).pointer(z);assert tuple(final[s][k] for k in ('alive','longest','total'))==tuple(st.i32(i) for i in (0,4,8)),(gid,'final')
 if expected:assert all(final[0][k]==expected[k] for k in ('alive','longest','total'))
 for r in rams:r['opponent_final_longest']=final[1]['longest'];r['could_decide']=r['own_longest_after']<final[1]['longest']
 checkpoints={str(c):snaps[c] if c<=rnd else snaps[rnd] for c in (100,200,300,400,500)}
 return dict(set=name,game=gid,label=label,last_round=rnd,turns=dict(turns),near=dict(close),rams=rams,checkpoints=checkpoints,final=final)
def report(rows):
 groups={n:[r for r in rows if r['set']==n] for n in ('Online','Ladder','Rank1')};allr={n:[x for r in rs for x in r['rams']] for n,rs in groups.items()};leaders={n:[x for x in xs if x['leader']] for n,xs in allr.items()}
 lines=['# Leader ram length counts',f'Games: Online {len(groups["Online"])} (agg7-m1 30; sr51-bob1 15; agg7-m2/m3 absent), Ladder 500, Rank1 597 (team 306).','Leader means longest or within 2 segments immediately before the ram; ram counts exclude moving victims and friendly collisions.','Each band cell gives rams by rounds 0–100/101–300/301–500; mean rammer length/walked steps/paid length; possible-deciding count; leader length lost per game.','Walked steps exclude the fatal collision step; possible-deciding means own longest immediately after the ram is below the opponent’s final longest.','', '| Victim length | Online | Ladder | Rank1 |','|---|---|---|---|']
 for i,b in enumerate(BANDS):
  cells=[]
  for name in groups:
   xs=[x for x in leaders[name] if band(x['length'])==i];cs=Counter(0 if x['round']<=100 else 1 if x['round']<=300 else 2 for x in xs)
   avg='/'.join(f'{mean(x[k] for x in xs):.2f}' for k in ('rammer_length','steps_walked','length_paid')) if xs else '—/—/—'
   cells.append('/'.join(str(cs[j]) for j in range(3))+'; '+avg+f'; {sum(x["could_decide"] for x in xs)}; {sum(x["length"] for x in xs)/len(groups[name]):.3f}')
  lines.append('| '+b+' | '+' | '.join(cells)+' |')
 lines+=['', '| Total counts | Online | Ladder | Rank1 |','|---|---:|---:|---:|']
 for desc,fun in [('All enemy rams / length lost',lambda name:f'{len(allr[name])} / {sum(x["length"] for x in allr[name])}'),('Leader rams / length lost',lambda name:f'{len(leaders[name])} / {sum(x["length"] for x in leaders[name])}'),('Leader ram lost length/game',lambda name:f'{sum(x["length"] for x in leaders[name])/len(groups[name]):.3f}')]:lines.append('| '+desc+' | '+' | '.join(fun(n) for n in groups)+' |')
 lines+=['', 'Coverage uses victim length for all enemy-initiated rams; threshold cells give covered lost length/all ram lost length (%); own dragon turns; turns with an enemy head reachable in ≤3 wall/portal-aware steps at turn start.','', '| Minimum length N | Online | Ladder | Rank1 |','|---|---|---|---|']
 for n in NS:
  cells=[]
  for name,rs in groups.items():
   lost=sum(x['length'] for x in allr[name]);covered=sum(x['length'] for x in allr[name] if x['length']>=n)
   cells.append(f'{covered}/{lost} ({100*covered/lost:.2f}%); {sum(r["turns"].get(str(n),r["turns"].get(n,0)) for r in rs)}; {sum(r["near"].get(str(n),r["near"].get(n,0)) for r in rs)}')
  lines.append(f'| {n} | '+' | '.join(cells)+' |')
 lines+=['', '| End-of-round longest: mean; Q1/Q2/Q3 (inclusive quartiles; early endings carried forward) | Online | Ladder | Rank1 |','|---|---|---|---|']
 for c in (100,200,300,400,500):
  cells=[]
  for rs in groups.values():
   vs=[r['checkpoints'][str(c)] for r in rs];qs=quantiles(vs,n=4,method='inclusive');cells.append(f'{mean(vs):.2f}; '+ '/'.join(f'{q:.2f}' for q in qs))
  lines.append(f'| {c} | '+' | '.join(cells)+' |')
 assert len(lines)<=45
 (D/'leader-len.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':
 js=jobs();rows=[];t=time.time()
 with (WORK/'ll_games.jsonl').open('w') as f:
  for ix,j in enumerate(js):
   r=scan(j);rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
   if (ix+1)%25==0:print(f'{ix+1}/{len(js)} {time.time()-t:.1f}s',flush=True)
 report(rows)
 print('Report written; games',len(rows),flush=True)
