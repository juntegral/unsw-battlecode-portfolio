#!/usr/bin/env python3
"""Offline census. Reuses battlecode replay.load and work.bc.load_map; no network or bot writes."""
import sys,json,hashlib,re,csv,os
from pathlib import Path
from collections import Counter,defaultdict,deque
from concurrent.futures import ProcessPoolExecutor
BASE=Path('~/01. Project/개인 프로젝트/battlecode')
SW=Path('~/01. Project/개인 프로젝트/unsw-swarm')
LOOP=Path('~/meow-loop-out')
OUT=SW/'data/analysis'
sys.path[:0]=[str(BASE),str(BASE/'work')]
import replay,bc
NEW={'Australia','Tower Defense','Islands','Around UNSW','Stripes'}
OLD={'Autarky','Default','Devil','Portals','Prisoners Dilemma','Queen Of Spades','Schooltime','Slithery Fight','Trauma','Trophy'}
def norm(s):return s.replace('_',' ')
def inventory():
    records={}; roots=[BASE/'work/nr',SW/'data/online',LOOP]; inv=[]; meta={}; reps={}
    for root in roots:
        files=sorted(p for p in root.rglob('*') if p.is_file()) if root.exists() else []
        for p in files:
            if p.name.startswith('game-') and p.suffix=='.json':
                g=json.loads(p.read_text());gid=str(g['id']);meta[gid]=g
                records.setdefault(gid,{'id':gid,'lists':[]})['metadata']=str(p)
            if p.suffix=='.replay' or p.name.endswith('.replay.gz'):
                m=re.fullmatch(r'M?(\d+)\.replay(?:\.gz)?',p.name)
                if m:reps.setdefault(m[1],[]).append(str(p))
        inv.append({'root':str(root),'exists':root.exists(),'files':len(files),'replays':sum(p.name.endswith(('.replay','.replay.gz')) for p in files),'game_json':sum(p.name.startswith('game-') and p.suffix=='.json' for p in files),'events_gz':sum(p.name.startswith('events-') and p.name.endswith('.gz') for p in files),'paths':[str(p) for p in files]})
    for p in sorted((BASE/'work').glob('nr_*.txt')):
        for line in p.read_text().splitlines():
            a=line.split()
            if len(a)<6:continue
            for game in a[5].split(','):
                parts=game.split(':')
                if len(parts)!=4:continue
                gid,mp,res,has=parts;r=records.setdefault(gid,{'id':gid,'lists':[]})
                r['lists'].append(str(p));r.update(list_map=norm(mp),list_result=res,list_side=a[4],list_opponent=a[2],list_ranked=a[1])
    tasks=[]
    for gid,r in records.items():
        r['replays']=reps.get(gid,[])
        if gid in meta:
            g=meta[gid];r['map']=norm(g['mapName']);r['side']='A' if g['teamAId']==1119 else 'B' if g['teamBId']==1119 else None
            if r['replays'] and r['side']:tasks.append((gid,r['replays'][0],r['side'],g))
        elif r['replays']:
            g=dict(mapName=r['list_map'],winner=r['list_side'] if r['list_result']=='W' else ('B' if r['list_side']=='A' else 'A'),ranked=r['list_ranked']=='R')
            tasks.append((gid,r['replays'][0],r['list_side'],g))
    (OUT/'newmaps-inventory.json').write_text(json.dumps({'roots':inv,'games':list(records.values()),'unmapped_numeric_replays':{k:v for k,v in reps.items() if k not in records}},ensure_ascii=False,indent=2))
    return tasks

def geometry(text):
    W,H,tiles,edges=bc.load_map(text);N=W*H;row=2*(W+1)
    portals=defaultdict(set)
    def canon(i):
        y,z=divmod(i,row)
        return (z%W,y%H,0) if z<=W else ((z-W-1)%W,y%H,1)
    types={}
    for i,(t,pid) in edges.items():
        c=canon(i)
        if t:types[c]=t
        if t==2:portals[pid].add(c)
    pairs={}
    for v in portals.values():
        if len(v)==2:
            a,b=v;pairs[a]=b;pairs[b]=a
    def ek(x,y,d):return [(x,y,0),((x+1)%W,y,1),(x,(y+1)%H,0),(x,y,1)][d]
    def step(p,d,noportal=False):
        x,y=p;e=ek(x,y,d);t=types.get(e,0)
        if t==1 or (t==2 and noportal):return None
        if t==2:
            if e not in pairs:return None
            a,b,_=pairs[e]
            return (a,(b-1)%H) if d==0 else ((a-1)%W,b) if d==3 else (a,b)
        return ((x+(d==1)-(d==3))%W,(y+(d==2)-(d==0))%H)
    step.is_portal=lambda p,d: types.get(ek(p[0],p[1],d))==2
    adj=[];pcells=set();corr=set()
    for i in range(N):
        x,y=i%W,i//W;ns=[];ds=[]
        for d in range(4):
            if types.get(ek(x,y,d))==2:pcells.add(i)
            p=step((x,y),d,True)
            if p is not None:ns.append(p[1]*W+p[0]);ds.append(d)
        adj.append(set(ns))
        if len(ds)==2 and abs(ds[0]-ds[1])==2:corr.add(i)
    comp={};sizes={}
    for i in range(N):
        if i in comp:continue
        q=[i];comp[i]=i
        for a in q:
            for b in adj[a]:
                if b not in comp:comp[b]=i;q.append(b)
        sizes[i]=len(q)
    deg=[len(a) for a in adj];q=deque(i for i,d in enumerate(deg) if d<=1);dead=set(q)
    while q:
        a=q.popleft()
        for b in adj[a]:
            if b in dead:continue
            deg[b]-=1
            if deg[b]<=1:dead.add(b);q.append(b)
    near=set(pcells);front=set(pcells)
    for _ in range(2):
        front={b for a in front for b in adj[a]}-near;near|=front
    def tags(p):
        if p is None:return {}
        i=p[1]*W+p[0];size=sizes[comp[i]]
        return dict(pocket=size<=48,pocket_size=size,pocket_id=comp[i],dead_end=i in dead,corridor=i in corr,near_portal=i in near)
    return W,H,step,tags,edges

def run(task):
    gid,path,ours,meta=task;root=replay.load(path).root();text=root.text(0);W,H,step,tags,edges=geometry(text)
    bodies={};teams={};visited={t:set() for t in 'AB'};qid={};birth={};lastsplit={}
    for l in text.splitlines():
        p=l.split()
        if p and p[0]=='DRAGON':
            did=len(bodies);teams[did]='AB'[int(p[1])];b=deque((int(p[3+2*k]),int(p[4+2*k])) for k in range(int(p[2])));bodies[did]=b;qid.setdefault(teams[did],did);visited[teams[did]].add(b[0])
    snaps={};deaths=[];pearls={};drop=None;rnd=-1;actor=None;actions={};stepsdone=Counter();eats={t:[0]*10 for t in 'AB'};natural={t:[0]*10 for t in 'AB'};cost={t:[0]*10 for t in 'AB'};errors=Counter();portentries=[];splits=[];visat={};suicides=[]
    def snapshot():
        return {t:dict(longest=max([len(b) for d,b in bodies.items() if teams[d]==t] or [0]),total=sum(len(b) for d,b in bodies.items() if teams[d]==t),units=sum(teams[d]==t for d in bodies),queen=len(bodies.get(qid[t],[])),visited=len(visited[t])) for t in 'AB'}
    for ev in root.pointer(3):
        ki=ev.u16(0);kind=replay.EVENT_NAMES[ki] if ki<len(replay.EVENT_NAMES) else '?';pl=ev.pointer(0)
        if drop is not None and not(kind=='tileChange' and pl.bit(0)):drop=None
        if kind=='roundStart':
            rnd=pl.i32(0)
            if rnd in (50,100,200,300,400):snaps[str(rnd)]=snapshot()
            if rnd in (100,200):visat[str(rnd)]={t:sorted(visited[t]) for t in 'AB'}
        elif kind=='turnStart':actor=pl.i32(0)
        elif kind=='dragonAction':
            did=pl.i32(0);a=pl.pointer(0);typ=a.u16(0) if a else -1
            dirs=list(a.pointer(0)) if a and typ==0 and a.pointer(0) else []
            actions[did]=(typ,dirs,pl.bit(32));stepsdone[did]=0
            if typ==2:suicides.append([rnd,did,teams.get(did),len(bodies.get(did,[]))])
        elif kind=='tileChange':
            p=replay.point(pl.pointer(0))
            if pl.bit(0):
                if p in pearls:errors['pearl_overwrite']+=1
                pearls[p]=drop
                if drop is not None:deaths[drop]['dropped']+=1
            else:
                t=teams.get(actor);origin=pearls.pop(p,'missing')
                if rnd>=0 and t:
                    bi=min(9,rnd//50);eats[t][bi]+=1
                    if origin=='missing':errors['eat_origin_missing']+=1
                    elif origin is None:natural[t][bi]+=1
                    else:
                        d=deaths[origin];d['eat_us' if t==ours else 'eat_them']+=1
                        d['consumers'].append([rnd,actor,p])
                        if t==ours:
                            d['eat_us_queen']+=int(actor==qid[t])
                            leader=max((x for x in bodies if teams[x]==t),key=lambda x:(len(bodies[x]),-x),default=None)
                            d['eat_us_longest']+=int(actor==leader)
                else:errors['eat_actor_missing']+=1
        elif kind=='dragonUpdate':
            did=pl.i32(0);h=replay.point(pl.pointer(0));tail=replay.point(pl.pointer(1));b=bodies.setdefault(did,deque());prev=b[0] if b else None
            if prev!=h:
                if prev is not None:
                    dx=min(abs(prev[0]-h[0]),W-abs(prev[0]-h[0]));dy=min(abs(prev[1]-h[1]),H-abs(prev[1]-h[1]))
                    act=actions.get(did,(-1,[],False));j=stepsdone[did]
                    if act[0]==0 and j<len(act[1]) and step(prev,act[1][j])!=h:errors['geometry_step']+=1
                    portal=act[0]==0 and j<len(act[1]) and step.is_portal(prev,act[1][j])
                    if portal:portentries.append(dict(r=rnd,id=did,team=teams.get(did),length=len(b),src=prev,dst=h,**tags(h)))
                b.appendleft(h);stepsdone[did]+=1
            while len(b)>1 and b[-1]!=tail:b.pop()
            if b[-1]!=tail:errors['tail_mismatch']+=1
            if did in teams:visited[teams[did]].add(h)
        elif kind=='dragonSplit':
            pa,ch=pl.i32(0),pl.i32(4);t='AB'[pl.u16(8)];before=len(bodies.get(pa,[]));pb=deque(replay.point(p) for p in pl.pointer(0));cb=deque(replay.point(p) for p in pl.pointer(1))
            if before!=len(pb)+len(cb):errors['split_length']+=1
            bodies[pa]=pb;bodies[ch]=cb;teams[pa]=teams[ch]=t;birth[ch]=rnd;lastsplit[pa]=rnd
            visited[t].add(cb[0]);splits.append(dict(r=rnd,id=pa,child=ch,team=t,parent_length=len(pb),child_length=len(cb),head=cb[0],**tags(cb[0])))
        elif kind=='dragonDeath':
            did=pl.i32(0);reason=pl.u16(4);b=bodies.get(did,deque());h=b[0] if b else None;t=teams.get(did);a=actions.get(did,(-1,[],False));dest=None;hit=None
            if actor==did and a[0]==0 and stepsdone[did]<len(a[1]) and h:
                dest=step(h,a[1][stepsdone[did]])
                for other,ob in bodies.items():
                    if dest in ob:hit=other;break
            cause=['wall','self','body','head-on','invalid'][reason] if reason<5 else 'unknown'
            explicit=a[0]==2 and actor==did
            if explicit:cause='suicide'
            if reason==3 and actor==did and hit is None and deaths and deaths[-1]['r']==rnd and deaths[-1]['actor']==did and deaths[-1]['cause']=='head-on':
                hit=deaths[-1]['id']
            collision_team=teams.get(hit) if hit is not None else teams.get(actor) if actor!=did else None
            d=dict(r=rnd,id=did,team=t,length=len(b),cause=cause,raw_reason=reason,head=h,attempt=dest,actor=actor,hit=hit,collision_team=collision_team,enemy=(collision_team is not None and collision_team!=t),explicit_suicide=explicit,tle=a[2],newborn=rnd-birth.get(did,-100)<=2,split_stub=rnd-lastsplit.get(did,-100)<=2,**tags(h),dropped=0,eat_us=0,eat_them=0,eat_us_queen=0,eat_us_longest=0,consumers=[])
            deaths.append(d);drop=len(deaths)-1;bodies.pop(did,None)
    final=snapshot();snaps['end']=final;res=root.pointer(4);stand={}
    for t,i in [('A',0),('B',1)]:
        s=res.pointer(i);stand[t]=dict(units=s.i32(0),longest=s.i32(4),total=s.i32(8))
        for k,v in stand[t].items():
            if final[t][k]!=v:errors['final_'+k]+=1
    winner='AB'[res.u16(6)] if res.u16(4)==1 else None
    if (meta.get('winner') or '').upper()!=winner:errors['winner_mismatch']+=1
    how='elimination' if any(final[t]['units']==0 for t in 'AB') else next((k for k in ['queen','longest','total'] if final['A'][k]!=final['B'][k]),'tie')
    if how not in ('tie','elimination') and winner!=max('AB',key=lambda t:final[t][how]):errors['adjudication']+=1
    qdeath={t:next((d for d in deaths if d['id']==qid[t]),None) for t in 'AB'}
    for d in deaths:
        expected=(d['length']+1)//2
        if d['dropped']!=expected:errors['drop_count']+=1
        d['uneaten']=d['dropped']-d['eat_us']-d['eat_them']
    mp=norm(meta['mapName']);official=[]
    for p in (BASE/'tune_runs/official127').glob('*.map'):
        txt=p.read_text();mm=re.search(r'^MAP_NAME (.+)$',txt,re.M)
        if mm and norm(mm[1])==mp:
            w,h,_,ed=bc.load_map(txt);official.append(dict(path=str(p),dimensions_match=(w,h)==(W,H),edges_match=ed==edges))
    return dict(id=gid,path=path,map=mp,group='new5' if mp in NEW else 'old10' if mp in OLD else 'other',ours=ours,opponent=meta.get('teamBName' if ours=='A' else 'teamAName',meta.get('list_opponent')),ranked=meta.get('ranked'),series=meta.get('seriesId'),bot_ours=root.text(1 if ours=='A' else 2),bot_theirs=root.text(2 if ours=='A' else 1),width=W,height=H,round_end=rnd,win=winner==ours,winner=winner,how=how,terminated=res.bit(0),end_reason=res.u16(2),snaps=snaps,eats=eats,natural=natural,queen_death=qdeath,deaths=deaths,suicides=suicides,splits=splits,portal_entries=portentries,visited=visat,errors=dict(errors),official=official)

if __name__=='__main__':
    tasks=inventory();print('TASKS',len(tasks),flush=True)
    if '--one' in sys.argv:tasks=tasks[:1]
    with (OUT/('newmaps-one.jsonl' if '--one' in sys.argv else 'newmaps-games.jsonl')).open('w') as f,ProcessPoolExecutor(max_workers=2) as ex:
        for i,g in enumerate(ex.map(run,tasks)):
            f.write(json.dumps(g,ensure_ascii=False)+'\n');f.flush()
            print(i+1,g['id'],g['map'],g['how'],g['errors'],flush=True)
