import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from collections import Counter,deque,defaultdict
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/weak'
sys.path[:0]=[str(ROOT/'data/analysis/ladder/dossier/work'),str(ROOT/'data/analysis/ladder/dossier/local'),str(ROOT/'data/analysis/ladder/dossier/online')]
import o1_scan,scoreboard,label_report
from count_local import Geo
from ladder_replay import replay,edge_id,canonical_edges
replay.load=scoreboard.load_replay

def extra(path,m):
 root=replay.load(path).root(); lines=root.text(0).splitlines(); w,h=map(int,lines[0].split()[1:3]); bodies={}; teams={}; raw=[]
 for l in lines:
  q=l.split()
  if q and q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2]))); teams[i]=int(q[1])
  elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 own=int(m['teamAId']!=1119); side=lambda i:int(teams[i]!=own)
 queens=[min(i for i in bodies if side(i)==s) for s in (0,1)]
 geo=Geo(w,h,raw); edges=canonical_edges(w,h,raw); portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 def dest(c,d):
  e=edge_id(w,h,*c,d); k,p=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   other=next(z for z in portals[p] if z!=e); row,x=divmod(other,w+1)
   return ((x-(d==3))%w,(row//2-(d==0))%h)
  dx,dy=o1_scan.STEP[d]; return ((c[0]+dx)%w,(c[1]+dy)%h)
 def options(i):
  b=bodies[i]; occ={c for bb in bodies.values() for c in bb}
  return [d for d in range(4) if (dest(b[0],d) is not None and (dest(b[0],d) not in occ or dest(b[0],d)==b[-1]))]
 def snap():
  return [[sum(side(i)==s for i in bodies),sum(len(b) for i,b in bodies.items() if side(i)==s),max((len(b) for i,b in bodies.items() if side(i)==s),default=0),len(bodies.get(queens[s],()))] for s in (0,1)]
 initial=[dict(id=i,side=side(i),length=len(b),head=list(b[0]),degree=len(geo.adj[b[0][1]*w+b[0][0]])) for i,b in bodies.items()]
 rnd=-1; actor=None; turn=None; turns=[]; deaths=[]; splits=[]; rams=[]; allsnaps={}; born={}; lastturn={}; cpu=[]
 def close():
  nonlocal turn
  if turn:
   turn['alive']=turn['id'] in bodies; turn['end_head']=list(bodies[turn['id']][0]) if turn['alive'] else None
   turn['mass_loss']=[turn['mass_before'][s]+(turn['eats'] if s==turn['side'] else 0)-snap()[s][1] for s in (0,1)]
   turns.append(turn); lastturn[turn['id']]=turn; turn=None
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0); p=ev.pointer(0)
  if k==0:
   close()
   if rnd>=0:allsnaps[rnd]=snap()
   rnd=p.i32(0);actor=None
  elif k==1:
   close();actor=p.i32(0); b=bodies[actor]
   turn=dict(r=rnd,id=actor,side=side(actor),L=len(b),head=list(b[0]),queen=actor==queens[side(actor)],moves=0,action=None,dirs=[],timeout=False,exit_dirs=options(actor),eats=0,event=idx,mass_before=[s[1] for s in snap()])
  elif k==4:
   a=p.pointer(0);used=p.pointer(1); turn['action']=a.u16(0) if a else None;turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
   turn['timeout']=p.bit(32) or (used is not None and used.bit(64));turn['cpu']=used.u64(0) if used else None
  elif k==3 and not p.u32(0):turn['eats']+=1
  elif k==9:
   i=p.i32(0); hd,tl=replay.point(p.pointer(0)),replay.point(p.pointer(1)); b=bodies[i]
   if b[0]!=hd:
    b.appendleft(hd)
    if i==actor:turn['moves']+=1
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   parent,child=p.i32(0),p.i32(4)
   for z,i in enumerate((parent,child)):bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
   born[child]=rnd
   splits.append(dict(r=rnd,parent=parent,child=child,side=side(child),L=len(bodies[child]),head=list(bodies[child][0]),exits=options(child),degree=len(geo.adj[bodies[child][0][1]*w+bodies[child][0][0]])))
  elif k==11:
   i=p.i32(0);b=bodies[i]; reason=p.u16(4);s=side(i)
   d=dict(r=rnd,event=idx,id=i,side=s,L=len(b),head=list(b[0]),reason=reason,actor=actor,queen=i==queens[s],age=rnd-born.get(i,rnd),exits=options(i),last_turn=lastturn.get(i),current_turn=dict(turn) if turn and i==actor else None)
   if reason==3 and i!=actor and side(actor)!=s:
    rams.append(dict(r=rnd,side=side(actor),actor=actor,target=i,L=turn['L'],target_L=len(b),queen_target=d['queen'],steps=turn['moves']+1,degree=len(geo.adj[b[0][1]*w+b[0][0]])))
   deaths.append(d);bodies.pop(i)
 close();allsnaps[rnd]=snap()
 us,them=allsnaps[rnd]; assert m['scores'+'AB'[own]]==us[1] and m['scores'+'AB'[1-own]]==them[1],(m['id'],us,them)
 def score(x):return (x[3],x[2],x[1])
 last_not_behind=max((r for r,sn in allsnaps.items() if sn[0][0] and (not sn[1][0] or score(sn[0])>=score(sn[1]))),default=-1)
 metrics=[]
 for s in (0,1):
  ts=[t for t in turns if t['side']==s]; ds=[d for d in deaths if d['side']==s]; rs=[r for r in rams if r['side']==s]
  metrics.append(dict(turns=len(ts),early_turns=sum(t['r']<=50 for t in ts),early_rams=sum(r['r']<=50 for r in rs),rams=len(rs),queen_hits=sum(r['queen_target'] for r in rs),corridor_rams=sum(r['degree']<=2 for r in rs),timeouts=sum(t['timeout'] for t in ts),stationary=sum(t['moves']==0 and t['action']!=1 and t['alive'] for t in ts),wall=sum(d['reason']==0 for d in ds),wall_open=sum(d['reason']==0 and len(d['exits'])>0 for d in ds),splits=len([p for p in splits if p['side']==s]),split_noexit=sum(not p['exits'] for p in splits if p['side']==s)))
 return dict(initial=initial,queens=queens,metrics=metrics,last_not_behind=last_not_behind,decisive_retrospective=min(rnd,last_not_behind+1),deaths=deaths,rams=rams,splits=splits,queen_turns=[t for t in turns if t['queen']],all_snapshots=allsnaps,largest_turn_loss=max(turns,key=lambda t:t['mass_loss'][0]),largest_enemy_turn_loss=max(turns,key=lambda t:t['mass_loss'][1]))

def main():
 jobs=[]
 for mp in sorted((ROOT/'data/online/live-one1').glob('b*/game-*.json')):
  m=json.loads(mp.read_text())
  if m.get('ranked'):jobs.append(('ranked',mp.with_name('M%d.replay'%m['id']),m))
 for label in ('one5-w1','one5-c1'):
  for mp in sorted((ROOT/'data/online/smoke'/f'{label}-old').glob('game-*.json')):
   m=json.loads(mp.read_text());jobs.append((label,mp.with_name('M%d.replay'%m['id']),m))
 for label,rp,m in jobs:
  fp=OUT/f"game-{m['id']}.json"
  if fp.exists():continue
  g=o1_scan.scan(label,rp,m);g['meta']=m;g['detail']=extra(rp,m)
  assert g['result']==('win' if m['winner']=='ab'[int(m['teamAId']!=1119)] else 'loss')
  fp.write_text(json.dumps(g,separators=(',',':'))+'\n')
  print(m['id'],m['mapName'],g['result'],g['how'],flush=True)
 (OUT/'inventory.json').write_text(json.dumps([{'label':l,'path':str(p.relative_to(ROOT)),'id':m['id']} for l,p,m in jobs],indent=2))
if __name__=='__main__':main()
