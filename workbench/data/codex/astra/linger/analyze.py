"""Read-only matched replay study. Run with -B; writes only beside this script."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, hashlib
from collections import Counter, defaultdict, deque
from datetime import datetime
sys.path[:0] = ['data/analysis/ladder/dossier/online', 'data/analysis/ladder/dossier/local']
from label_report import inventory
from spawn import read
from replay_format import point
from count_local import Geo
OUT = Path(__file__).resolve().parent
LABELS = ['one1-w1','one1-d1','one2-w1','one3-w1','one3-d1','one4-w1','one4-d1','one5-w1','one5-d1']

def scan(label, path, meta):
    root = read(path)
    assert root.pointer(4).bit(0), 'unfinished replay'
    bodies, teams, raw = {}, {}, []
    for line in root.text(0).splitlines():
        q=line.split()
        if not q: continue
        if q[0]=='MAP': w,h=map(int,q[1:3])
        elif q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
        elif q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1]); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
    own=int(meta['teamAId']!=1119)
    side=lambda i: int(teams[i]!=own)
    queens=[min(i for i in bodies if side(i)==s) for s in (0,1)]
    g=Geo(w,h,raw)
    rev=[[] for _ in g.adj]
    for c,ds in enumerate(g.adj):
        for d in ds: rev[d].append(c)
    cache={}
    def distances(c):
        if c not in cache:
            ds={c:0}; queue=deque([c])
            while queue:
                x=queue.popleft()
                if ds[x]>=12: continue
                for n in rev[x]:
                    if n not in ds: ds[n]=ds[x]+1;queue.append(n)
            cache[c]=ds
        return cache[c]
    def static(a,c): return distances(c).get(a,13)
    def nearby(c):
        occ=set(t for b in bodies.values() for t in b)
        heads={b[0]:i for i,b in bodies.items()}
        out=[4,4]; ds={c:0}; queue=deque([c]); ids={}
        while queue:
            x=queue.popleft()
            if x in heads:
                i=heads[x]; out[side(i)]=min(out[side(i)],ds[x]);ids[i]=ds[x]
                if x!=c: continue
            elif x in occ and x!=c: continue
            if ds[x]==3:continue
            for n in rev[x]:
                if n not in ds: ds[n]=ds[x]+1;queue.append(n)
        return out,ids
    pos=lambda p: (lambda xy: xy[1]*w+xy[0])(point(p))
    present={}; lasteat={}; births=[]; meals=[]; active=defaultdict(list)
    seen=[set(),set()]; eaten_tiles=[set(),set()]
    rnd=-1; actor=None; countdown_events=0; rawcounts=Counter(); natural_eats=[0,0]
    def finish_round():
        for i,recs in list(active.items()):
            for m in recs:
                dt=rnd-m['r']
                if 1<=dt<=8:
                    assert len(m['d'])==dt-1
                    m['d'].append(static(bodies[i][0],m['c']) if i in bodies else -1)
            active[i]=[m for m in recs if rnd-m['r']<8]
            if not active[i]:del active[i]
    for ev in root.pointer(3):
        k=ev.u16(0)
        rawcounts[k]+=1
        if k not in (0,1,2,3,9,10,11):continue
        p=ev.pointer(0)
        if k==0:
            finish_round();rnd=p.i32(0);actor=None
        elif k==1:
            actor=p.i32(0);s=side(actor);window=g.window(bodies[actor][0]);new=window-seen[s]
            discovered=[c for c in window if c in present and present[c]['natural'] and not present[c]['seen'][s]]
            for c in window:
                if c in present:present[c]['seen'][s]=True
            for m in active.get(actor,[]):
                if 1<=rnd-m['r']<=8:
                    m['newtiles']+=len(new)
                    m['discover_far']+=sum(static(c,m['c'])>3 for c in discovered)
                    if new:m['explore_rounds'].append(rnd)
            seen[s].update(window)
        elif k==2:countdown_events+=1
        elif k==3:
            c=pos(p.pointer(0))
            if p.u32(0):
                assert c not in present,('duplicate birth',rnd,c)
                b=dict(r=rnd,c=c,natural=actor is None,seen=[False,False],eat_s=-1,eat_r=-1,eat_i=-1)
                present[c]=b
                if b['natural'] and 0<=rnd<=300:
                    prev=lasteat.get(c)
                    if prev:
                        near,ids=nearby(c)
                        b.update(prev_r=prev['r'],prev_s=prev['s'],prev_i=prev['i'],prev_natural=prev['natural'],near=near,
                                 eater_d=static(bodies[prev['i']][0],c) if prev['i'] in bodies else -1,
                                 eater_free3=ids.get(prev['i'],4),gap=rnd-prev['r'])
                        births.append(b)
                        if 'meal' in prev:
                            m=prev['meal'];m['birth']=len(births)-1
            else:
                assert actor is not None and actor in bodies
                b=present.pop(c);s=side(actor)
                b.update(eat_s=s,eat_r=rnd,eat_i=actor)
                if b['natural']:
                    natural_eats[s]+=1
                    for m in active.get(actor,[]):
                        if 0<rnd-m['r']<=8 and c!=m['c']:
                            m['elsewhere'].append([rnd,c,static(c,m['c']),int(c not in eaten_tiles[s])])
                    eaten_tiles[s].add(c)
                prev=dict(r=rnd,s=s,i=actor,natural=b['natural'])
                if b['natural'] and 0<=rnd<=300:
                    m=dict(r=rnd,s=s,i=actor,c=c,queen=actor==queens[s],d=[],splits=[],newtiles=0,discover_far=0,
                           explore_rounds=[],elsewhere=[],death=-1,birth=-1)
                    meals.append(m);active[actor].append(m);prev['meal']=m
                lasteat[c]=prev
        elif k==9:
            i=p.i32(0);hd=pos(p.pointer(0));tl=pos(p.pointer(1));b=bodies[i]
            if b[0]!=hd:b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
            assert b[-1]==tl,('tail absent',rnd,i)
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            for m in active.get(parent,[]):
                if 0<=rnd-m['r']<=8:m['splits'].append(rnd)
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(pos(t) for t in p.pointer(z));teams[i]=p.u16(8)
        elif k==11:
            i=p.i32(0)
            for m in active.get(i,[]):
                if 0<=rnd-m['r']<=8:m['death']=rnd
            del bodies[i]
    finish_round()
    for b in births:b.pop('seen',None)
    return dict(label=label,gid=meta['id'],map=meta['mapName'],cells=w*h,w=w,h=h,rounds=rnd,
                opp=meta['team'+'AB'[1-own]+'Name'],bot=root.text(1+own),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                countdown_events=countdown_events,rawcounts=rawcounts,natural_eats=natural_eats,births=births,meals=meals)

def main():
    invs=[]
    for label in sys.argv[1:] or LABELS:
        inv=inventory(label,'old');invs.append(dict(label=label,jobs=len(inv['jobs']),notes=inv['notes']))
        for path,meta in inv['jobs']:
            out=OUT/f"g{meta['id']}.json"
            if out.exists():continue
            result=scan(label,path,meta)
            out.write_text(json.dumps(result,separators=(',',':')))
            print(label,meta['id'],len(result['births']),len(result['meals']),flush=True)
    (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),sets=invs),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
