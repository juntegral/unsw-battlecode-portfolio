"""Offline replay metrics; run python3 -B .../analyze.py. All writes stay here."""
import sys
sys.dont_write_bytecode=True
sys.path[:0]=['data/codex/astra/approach','data/analysis/ladder/dossier/online','data/analysis/ladder/dossier/local']
from scan import Board, replay, edge_id
import label_report as lr
from scoreboard import load_replay
from collections import defaultdict,Counter,deque
from pathlib import Path
from datetime import datetime
from functools import lru_cache
import json,hashlib,csv
OUT=Path(__file__).resolve().parent

def scan(job):
 B=Board(job['path']); own=job['own']; side=lambda i:int(B.teams[i]!=own)
 Q=[min(i for i in B.bodies if side(i)==s) for s in (0,1)]
 def delta(a,b):return ((b[0]-a[0]+B.W//2)%B.W-B.W//2,(b[1]-a[1]+B.H//2)%B.H-B.H//2)
 def man(a,b):return sum(map(abs,delta(a,b)))
 mouths={}
 for e,(k,pid) in B.edges.items():
  if k!=2:continue
  row,x=divmod(e,B.W+1);y=row//2
  mouths[e]=[(x%B.W,y%B.H),((x-(row%2))%B.W,(y-(row%2==0))%B.H)]
 near={c:[e for e,cs in mouths.items() if min(man(c,p) for p in cs)<=2] for c in B.adj}
 rev=defaultdict(list)
 for c,ns in B.adj.items():
  for n in ns:
   if n is not None:rev[n].append(c)
 @lru_cache(maxsize=128)
 def geometric(target):
  ds={target:0};qq=deque([target])
  while qq:
   c=qq.popleft()
   for n in rev[c]:
    if n not in ds:ds[n]=ds[c]+1;qq.append(n)
  return ds
 queen_events=[];event_counts=Counter()
 C=Counter();turns=defaultdict(list);deaths=[];cur=None;detailed=[]
 def close():
  nonlocal cur
  if cur is None:return
  i=cur['i'];s=cur['s'];cur['end']=B.bodies[i][0] if i in B.bodies else None
  C[s,'turns']+=1
  if cur['reach']:
   C[s,'queen_reach']+=1;C[s,'queen_miss']+=not cur['ram']
   if cur['qvisible']:C[s,'queen_visible_reach']+=1;C[s,'queen_visible_miss']+=not cur['ram']
   queen_events.append(cur.copy())
  if cur['adj'] and cur['qnear']:
   C[s,'pearl_nearq']+=1;C[s,'pearl_miss']+=not any(c in cur['ate'] for c in cur['adj'])
  if cur.get('detail'):detailed.append(cur.copy())
  turns[i].append(cur);cur=None
 def freereach(i,target):
  body=tuple(B.bodies[i]);occ={c for z,b in B.bodies.items() if z!=i for c in b};occ.discard(target)
  budget=(len(body)+3)//4
  queue=deque([(body,0,frozenset())]);seen=set()
  while queue:
   bb,d,eaten=queue.popleft()
   if d>=budget:continue
   for n in B.adj[bb[0]]:
    if n is None or n in occ:continue
    eat=n in B.pearls and n not in eaten
    if n in bb:continue
    if n==target:return True
    nb=(n,)+ (bb if eat else bb[:-1]);ne=eaten|{n} if eat else eaten
    key=(nb,ne)
    if key not in seen:seen.add(key);queue.append((nb,d+1,ne))
  return False
 for ev in B.root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0);event_counts[k]+=1
  if k in (0,1):close()
  if cur is not None:
   if k==3 and not p.u32(0):cur['ate'].append(replay.point(p.pointer(0)))
   if k==4:
    a=p.pointer(0);cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else [];cur['action']=a.u16(0)
   if k==9 and p.i32(0)==cur['i']:
    hd=replay.point(p.pointer(0))
    if hd!=B.bodies[cur['i']][0]:cur['steps'].append(hd)
   if k==10 and p.i32(0)==cur['i']:cur['split']=True
   if k==11:
    i=p.i32(0)
    deaths.append(dict(i=i,s=side(i),r=B.rnd,reason=p.u16(4),h=B.bodies[i][0],actor=B.actor))
    if i==Q[1-cur['s']] and p.u16(4)==3 and B.actor==cur['i']:cur['ram']=True
  B.update(k,p)
  if k!=1:continue
  i=B.actor;s=side(i);h=B.bodies[i][0];eq=Q[1-s];qh=B.bodies[eq][0] if eq in B.bodies else None
  vis=qh is not None and B.view(h,qh)
  reach=qh is not None and i!=Q[s] and geometric(qh).get(h,10**9)<=(len(B.bodies[i])+3)//4 and freereach(i,qh)
  adj=[c for c in B.adj[h] if c in B.pearls]
  cur=dict(i=i,s=s,r=B.rnd,L=len(B.bodies[i]),h=h,near=near[h],ate=[],steps=[],dirs=[],split=False,ram=False,qvisible=vis,reach=bool(reach),adj=adj,qnear=qh is not None and man(h,qh)<=3,qh=qh,qL=len(B.bodies[eq]) if qh else None)
  if (job['game']==1477042 and i==6) or (job['game']==1477048 and 14<=B.rnd<=20):
   occ={c for b in B.bodies.values() for c in b};ds=B.flood(h,12,occ-{h})
   cur['detail']=dict(body=list(B.bodies[i]),heads=[(z,len(b),b[0]) for z,b in B.bodies.items() if B.view(h,b[0])],pearls=[(c,ds.get(c)) for c in B.pearls if B.view(h,c)], options=[dict(d=d,dest=n,occupied=[z for z,b in B.bodies.items() if n in b]) for d,n in enumerate(B.adj[h])],bodies={z:list(b) for z,b in B.bodies.items() if any(B.view(h,c) for c in b)})
 close()
 # Maximal portal-mouth/no-eat streaks; union turns avoids double counting nearby mouths.
 portal_runs=[];covered=set()
 for i,ts in turns.items():
  active={}
  def finish(e):
   seq=active.pop(e)
   if len(seq)>=10:
    portal_runs.append(dict(i=i,s=ts[0]['s'],mouth=e,mouth_cells=mouths[e],start=seq[0],end=seq[-1],n=len(seq)))
    covered.update((i,r) for r in seq)
  for t in ts:
   valid=set(t['near']) if not t['ate'] else set()
   for e in list(active):
    if e not in valid or active[e][-1]!=t['r']-1:finish(e)
   for e in valid:active.setdefault(e,[]).append(t['r'])
  for e in list(active):finish(e)
 for i,r in covered:C[side(i),'portal_turns']+=1
 # Parallel adjacent lanes, same straight heading, at most one cell longitudinal stagger.
 byround=defaultdict(dict)
 for i,ts in turns.items():
  for t in ts:
   if 0<=t['r']<=40 and t['end'] and not t['split'] and t['dirs'] and len(set(t['dirs']))==1 and t['steps']:
    d=t['dirs'][0];dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d]
    expect=((t['h'][0]+dx*len(t['steps']))%B.W,(t['h'][1]+dy*len(t['steps']))%B.H)
    if expect==t['end']:byround[t['r']][i]=t
 active={};pairs=[]
 def endpair(key):
  rs=active.pop(key)
  if len(rs)>=4:
   i,j,d=key;dead=[x for x in deaths if x['i'] in (i,j) and rs[-1]<x['r']<=rs[-1]+5]
   pairs.append(dict(i=i,j=j,s=side(i),direction=d,start=rs[0],end=rs[-1],n=len(rs),death=dead))
 for r in range(41):
  ts=byround[r];valid=set()
  for i,t in ts.items():
   d=t['dirs'][0]
   for j,u in ts.items():
    if j<=i or side(j)!=side(i) or u['dirs'][0]!=d:continue
    def parallel(a,b):
     dx,dy=delta(a,b);return abs(dx)==1 and abs(dy)<=1 if d in (0,2) else abs(dy)==1 and abs(dx)<=1
    if parallel(t['h'],u['h']) and parallel(t['end'],u['end']):valid.add((i,j,d))
  for key in list(active):
   if key not in valid:endpair(key)
  for key in valid:active.setdefault(key,[]).append(r)
 for key in list(active):endpair(key)
 for s in (0,1):
  C[s,'parallel_pairs']=len({(p['i'],p['j']) for p in pairs if p['s']==s})
  C[s,'parallel_death']=len({(p['i'],p['j']) for p in pairs if p['s']==s and p['death']})
 for s in (0,1):
  ls=[len(b) for i,b in B.bodies.items() if side(i)==s];st=B.root.pointer(4).pointer(own if s==0 else 1-own)
  assert (len(ls),max(ls,default=0),sum(ls))==(st.i32(0),st.i32(4),st.i32(8))
 return dict(**job,bot=B.root.text(own+1),counts=[dict((k,n) for (z,k),n in C.items() if z==s) for s in (0,1)],portal_runs=portal_runs,pairs=pairs,details=detailed,deaths=deaths,queen_events=queen_events,event_counts=dict(event_counts))

def main():
 jobs=[];seen=set();duplicates=[];excluded=[];notes=[]
 for folder in sorted(Path('data/online/smoke').glob('one[56]-*-old')):
  inv=lr.inventory(folder.name[:-4],'old');notes+=inv['notes']
  for path,j in inv['jobs']:
   if j['id'] in seen:duplicates.append(j['id']);continue
   seen.add(j['id']);jobs.append(dict(path=str(path),game=j['id'],own=int(j['teamAId']!=1119),group=folder.name[:-4],map=j['mapName'],opp=j['teamBName'] if j['teamAId']==1119 else j['teamAName']))
 inv=lr.directory_inventory('live','data/online/live-one1/b*');notes+=inv['notes']
 for path,j in inv['jobs']:
  if j['id'] in seen:duplicates.append(j['id']);continue
  if (j.get('startedAt') or '')<'2026-10-08T15:49':continue
  own=int(j['teamAId']!=1119);bot=load_replay(path).root().text(own+1)
  if bot not in ('20980','21033'):excluded.append([j['id'],bot]);continue
  seen.add(j['id']);jobs.append(dict(path=str(path),game=j['id'],own=own,group={'20980':'one5','21033':'one6'}[bot]+'-live',map=j['mapName'],opp=j['teamBName'] if own==0 else j['teamAName']))
 (OUT/'inventory.json').write_text(json.dumps(dict(at=datetime.now().astimezone().isoformat(),jobs=jobs,duplicates=duplicates,excluded=excluded,notes=notes),ensure_ascii=False,indent=2))
 old={}
 with (OUT/'games.jsonl').open('w') as f:
  for n,j in enumerate(jobs):
   row=old.get(j['game']) or scan(j);f.write(json.dumps(row,separators=(',',':'))+'\n');f.flush()
   print(n+1,len(jobs),j['game'],j['group'],flush=True)
if __name__=='__main__':main()
