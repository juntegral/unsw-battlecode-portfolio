"""Offline queen box audit. Run from repository root with python3 -B."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from collections import deque, Counter
import json
from datetime import datetime, timezone, timedelta
sys.path[:0] = ['data/analysis/ladder/dossier/online', 'data/analysis/ladder/dossier/local', 'data/analysis/ladder/dossier/work']
import label_report as lr
from replay_format import load, point
from count_local import Geo, edge_id
import o1_q4

OUT = Path('data/codex/astra/queenbox')
BUILD = {'20850':'one1','20880':'one2','20910':'one3','20941':'one4','20980':'one5'}
CUTS = [('2026-10-08T13:29:00+00:00','one1'),('2026-10-08T14:02:00+00:00','one2'),('2026-10-08T14:36:00+00:00','one3'),('2026-10-08T15:10:00+00:00','one4'),('2026-10-08T15:49:00+00:00','one5')]

def inventory():
    jobs, notes, seen = [], [], set()
    labels = ['one1-w1','one1-d1','one2-w1','one3-w1','one3-d1','one4-w1','one4-d1','one5-w1','one5-d1']
    for label in labels:
        inv = lr.inventory(label, 'old')
        notes.append(dict(label=label, found=len(inv['jobs']), planned=inv['planned'], notes=inv['notes']))
        for path, meta in inv['jobs']:
            if meta['id'] not in seen:
                jobs.append((label, path, meta)); seen.add(meta['id'])
    inv = lr.directory_inventory('live', 'data/online/live-one1/b*')
    notes.append(dict(label='live', found=len(inv['jobs']), notes=inv['notes']))
    for path, meta in inv['jobs']:
        if meta['id'] not in seen:
            jobs.append(('live', path, meta)); seen.add(meta['id'])
    return jobs, notes

def scan(label, path, meta):
    root = load(path).root()
    lines = root.text(0).splitlines()
    w,h = map(int, lines[0].split()[1:3])
    own = int(meta['teamAId'] != 1119)
    bot = root.text(own+1)
    build = BUILD.get(bot)
    if bot and bot not in BUILD:
        return dict(game=meta['id'], excluded='replay bot id outside one1–one5', bot=bot)
    build_source = 'replay bot id'
    if not build:
        if label.startswith('one'):
            build, build_source = label.split('-')[0], 'label'
        else:
            t = meta.get('startedAt') or meta.get('requestedAt')
            if not t:
                return dict(game=meta['id'], excluded='missing bot id and start time')
            ts = datetime.fromisoformat(t.replace('Z','+00:00'))
            build = next((b for c,b in reversed(CUTS) if ts >= datetime.fromisoformat(c)), None)
            build_source = 'start time (not completion time)'
    if not build:
        return dict(game=meta['id'], excluded='before one1', bot=bot)
    bodies,teams,raw = {},{},[]
    for line in lines:
        t=line.split()
        if t[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque(int(t[4+2*k])*w+int(t[3+2*k]) for k in range(int(t[2]))); teams[i]=int(t[1])
        elif t[0]=='EDGE': raw.append(tuple(map(int,t[1:4])))
    geo=Geo(w,h,raw)
    qid=min(i for i in bodies if teams[i]==own)
    occ={c:i for i,b in bodies.items() for c in b}
    children,pearls,seen,known_edges={},set(),set(),set()
    turns,closures,splits=[],[],[]
    rnd,actor=-1,None
    qt=None
    home_closed=False
    death=None

    def xy(c): return [c%w,c//w]
    def man(a,b):
        dx,dy=abs(a%w-b%w),abs(a//w-b//w)
        return min(dx,w-dx)+min(dy,h-dy)
    def nearby():
        if qid not in bodies: return None
        hd=bodies[qid][0]
        ns=[]
        for d,(k,c) in enumerate(geo.moves[hd]):
            i=occ.get(c)
            typ='W' if k==1 else '.' if i is None else 'S' if i==qid else ('C' if i in children else 'A') if teams[i]==own else 'E'
            ns.append(dict(d='NESW'[d],cell=xy(c),kind=typ,id=i,head=i is not None and bodies[i][0]==c,portal=k==2,pearl=c in pearls))
        return ns
    def exits(): return sum(n['kind']=='.' for n in nearby()) if qid in bodies else 0
    def enemy_gap(): return min((man(bodies[qid][0],b[0]) for i,b in bodies.items() if teams[i]!=own),default=None)
    def occ_update(i,body):
        for c in bodies.get(i,()):
            if occ.get(c)==i: occ.pop(c)
        if body is None: bodies.pop(i,None)
        else:
            bodies[i]=deque(body)
            for c in body: occ[c]=i
    def metrics():
        b=list(bodies[qid]); hd=b[0]; L=len(b); view=geo.window(hd)
        blocked={c for c,i in occ.items() if i!=qid and c in view}
        free_at={c:L-k+1 for k,c in enumerate(b)}
        current_pearls=pearls & view
        def edgeknown(c,d): return edge_id(w,h,c%w,c//w,d) in known_edges
        def room(start,known_only=False):
            queue=deque([(start,1,int(start in current_pearls))]); visited={start}; tail=False
            while queue:
                c,steps,eaten=queue.popleft()
                if c==b[-1]: tail=True
                if known_only and (len(visited)>=L+2 or tail): return L+2,True
                for d,(k,n) in enumerate(geo.moves[c]):
                    ek=edgeknown(c,d)
                    if known_only and (not ek or k!=0 or n not in seen): continue
                    if not known_only and ek and k!=0: continue
                    if not ek:
                        dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d]
                        n=((c//w+dy)%h)*w+(c%w+dx)%w
                    if n in visited or n in blocked or steps+1-eaten < free_at.get(n,0): continue
                    visited.add(n);queue.append((n,steps+1,eaten+int(n in current_pearls)))
            return (len(visited) if known_only else sum(1 if c in seen else .5 for c in visited)),tail
        def survives(body,food,depth):
            if not depth:return True
            for k,n in geo.moves[body[0]]:
                if k!=0 or n in body or n in blocked:continue
                nb=[n]+body
                if n not in food: nb.pop()
                if survives(nb,food-{n},depth-1):return True
            return False
        choices=[]
        for d,(k,c) in enumerate(geo.moves[hd]):
            if k!=0 or c in occ:continue
            R,T=room(c); K,_=room(c,True)
            nb=[c]+b
            if c not in current_pearls:nb.pop()
            s1=survives(nb,current_pearls-{c},1)
            s2=survives(nb,current_pearls-{c},2)
            s3=survives(nb,current_pearls-{c},3)
            dead=not T and R<3*L+8
            pen=(6000 if dead or R<L+8 else 0)+(6000+400*(L+2-K) if K<L+2 else 0)
            choices.append(dict(d='NESW'[d],cell=xy(c),pearl=c in current_pearls,room=R,tail=T,known=K,dead=dead,penalty=pen,s1=s1,s2=s2,s3=s3))
        return choices
    def sample(idx):
        nonlocal home_closed
        hd=bodies[qid][0]
        view=geo.window(hd);seen.update(view)
        for c in view:
            for d in range(4):known_edges.add(edge_id(w,h,c%w,c//w,d))
        if not home_closed and rnd<=200 and rnd%2==0:
            vis={hd};queue=deque([hd]);valid=True
            while queue and valid:
                c=queue.popleft()
                for d,(k,n) in enumerate(geo.moves[c]):
                    if edge_id(w,h,c%w,c//w,d) not in known_edges:valid=False;break
                    if k==0 and n not in vis:
                        vis.add(n);queue.append(n)
                        if len(vis)>int(w*h*.5):valid=False;break
            home_closed=valid and len(vis)>=40
        return dict(round=rnd,event=idx,head=xy(hd),length=len(bodies[qid]),neighbors=nearby(),free=exits(),enemy6=enemy_gap(),
                    home_closed=home_closed,gate=w*h>600 or home_closed,choices=metrics(),moves=[],eats=0,action=None,
                    mates=sum(teams[i]==own and i!=qid and man(hd,b[0])<=5 for i,b in bodies.items()))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0)
        if k not in (0,1,3,4,9,10,11):continue
        p=ev.pointer(0)
        if k==0:rnd=p.i32(0);actor=None;qt=None
        elif k==1:
            actor=p.i32(0);qt=None
            if actor==qid:
                qt=sample(idx);turns.append(qt)
        elif k==4 and actor==qid:
            a=p.pointer(0)
            qt['action']=None if a is None else dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else [])
        elif k==3:
            pp=point(p.pointer(0));c=pp[1]*w+pp[0]
            if p.u32(0):pearls.add(c)
            else:
                pearls.discard(c)
                if actor==qid and qt is not None:qt['eats']+=1
        elif k in (9,10,11):
            before=exits();oldns=nearby(); oldhd=xy(bodies[qid][0]) if qid in bodies else None
            if k==9:
                i=p.i32(0);a=point(p.pointer(0));z=point(p.pointer(1));hd=a[1]*w+a[0];tail=z[1]*w+z[0]
                b=deque(bodies[i])
                if b[0]!=hd:
                    if i==qid and qt is not None:qt['moves'].append(xy(hd))
                    b.appendleft(hd)
                while len(b)>1 and b[-1]!=tail:b.pop()
                assert b[-1]==tail
                occ_update(i,b)
            elif k==10:
                i,child=p.i32(0),p.i32(4)
                before_len=len(bodies[i])
                bs=[[point(c)[1]*w+point(c)[0] for c in p.pointer(z)] for z in range(2)]
                occ_update(i,bs[0]);occ_update(child,bs[1]);teams[child]=p.u16(8)
                if i==qid:
                    children[child]=rnd;splits.append(dict(round=rnd,child=child,before=before_len,after=len(bs[0]),child_length=len(bs[1])))
            else:
                i,reason=p.i32(0),p.u16(4)
                if i==qid:
                    death=dict(round=rnd,event=idx,length=len(bodies[i]),reason=reason,actor=actor,free=before,neighbors=oldns,head=oldhd,enemy6=enemy_gap())
                occ_update(i,None)
            if qid in bodies and before>0 and exits()==0:
                closures.append(dict(round=rnd,event=idx,actor=actor,changed=i,kind=k,head=xy(bodies[qid][0]),before_head=oldhd,neighbors=nearby(),before_neighbors=oldns,own_child=i in children,enemy6=enemy_gap()))
            if death:break
    return dict(game=meta['id'],label=label,path=str(path),build=build,build_source=build_source,bot=bot,ranked=meta.get('ranked'),map=meta['mapName'],cells=w*h,width=w,height=h,
                opponent=meta['teamBName'] if own==0 else meta['teamAName'],opponent_id=meta['teamBId'] if own==0 else meta['teamAId'],queen=qid,
                death=death,turns=turns,closures=closures,splits=splits)

def main():
    jobs,notes=inventory()
    (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now(timezone(timedelta(hours=9))).isoformat(),notes=notes),ensure_ascii=False,indent=2))
    cache=OUT/'games.jsonl'
    rows={r['game']:r for r in map(json.loads,cache.read_text().splitlines())} if cache.exists() else {}
    for label,path,meta in jobs:
        if meta['id'] in rows:continue
        row=scan(label,path,meta);rows[meta['id']]=row
        with cache.open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
        print(meta['id'],label,row.get('build'),row.get('death'),flush=True)
    print('games',len(rows),'excluded',sum('excluded' in r for r in rows.values()))

if __name__=='__main__':main()
