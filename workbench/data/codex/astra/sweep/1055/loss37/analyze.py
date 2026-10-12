import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'data/analysis/ladder/dossier/local'))
from scoreboard import load_replay
from replay_format import point
from count_local import Geo

def scan(gid):
    root = load_replay(ROOT/f'data/online/smoke/one13-q1-old/M{gid}.replay').root()
    w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,edges = {},{},[]
    for line in root.text(0).splitlines():
        p=line.split()
        if p and p[0]=='DRAGON':
            i=len(bodies); teams[i]=int(p[1]); bodies[i]=deque(int(p[4+2*k])*w+int(p[3+2*k]) for k in range(int(p[2])))
        elif p and p[0]=='EDGE': edges.append(tuple(map(int,p[1:4])))
    geo=Geo(w,h,edges)
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    pearls=set(); turns=[]; deaths=[]; splits=[]; snaps={}; rnd=-1; actor=None; cur=None
    eat=[0,0]; paths={}; near=[]; qdead=False
    def xy(c): return [c%w,c//w]
    def state():
        return [dict(alive=sum(teams[i]==s for i in bodies),queen=len(bodies.get(queens[s],())),longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),pearls=eat[s]) for s in (0,1)]
    def frame(): return {str(i):list(b) for i,b in bodies.items()}
    def dist(src):
        if src not in paths:
            ds={src:0}; q=deque([src])
            while q:
                c=q.popleft()
                if ds[c]>=5: continue
                for t in geo.adj[c]:
                    if t not in ds: ds[t]=ds[c]+1; q.append(t)
            paths[src]=ds
        return paths[src]
    def close():
        if cur is not None:
            cur['end']=list(bodies.get(actor,()))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:
            close()
            if rnd>=0: snaps[rnd]=state()
            rnd=p.i32(0); actor=None; cur=None
        elif k==1:
            close(); actor=p.i32(0)
            cur=dict(round=rnd,event=idx,id=actor,side=teams[actor],body=list(bodies[actor]),eats=0,steps=[],deaths=[],units=sum(teams[i]==teams[actor] for i in bodies))
            if actor in queens:
                cur['frame']=frame(); cur['pearls']=sorted(pearls)
            if qdead and queens[1] in bodies and teams[actor]==0:
                ds=dist(bodies[actor][0]); qh=bodies[queens[1]][0]
                if qh in ds: near.append(dict(round=rnd,id=actor,distance=ds[qh],head=xy(bodies[actor][0]),queen=xy(qh)))
            turns.append(cur)
        elif k==4:
            a=p.pointer(0)
            cur['action']=a.u16(0) if a else None
            cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
            fuel=p.pointer(1); cur['timeout']=bool(p.bit(32) or (fuel is not None and fuel.bit(64)))
        elif k==3:
            x,y=point(p.pointer(0)); c=y*w+x
            if p.u32(0): pearls.add(c)
            else: pearls.remove(c); eat[teams[actor]]+=1; cur['eats']+=1
        elif k==9:
            i=p.i32(0); x,y=point(p.pointer(0)); head=y*w+x; x,y=point(p.pointer(1)); tail=y*w+x
            b=bodies[i]
            if b[0]!=head:
                if i==actor: cur['steps'].append(head)
                b.appendleft(head)
            while len(b)>1 and b[-1]!=tail: b.pop()
            assert b[-1]==tail
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            before=len(bodies[parent])
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(y*w+x for x,y in map(point,p.pointer(z))); teams[i]=p.u16(8)
            splits.append(dict(round=rnd,parent=parent,child=child,before=before,after=len(bodies[parent]),childlen=len(bodies[child])))
        elif k==11:
            i=p.i32(0)
            d=dict(round=rnd,event=idx,id=i,side=teams[i],actor=actor,reason=p.u16(4),body=list(bodies[i]),length=len(bodies[i]))
            if i in queens or len(bodies[i])>=8: d['frame']=frame(); d['pearls']=sorted(pearls)
            deaths.append(d); cur['deaths'].append(i); bodies.pop(i)
            if i==queens[0]: qdead=True
    close(); snaps[rnd]=state()
    result=root.pointer(4)
    final=[dict(zip(('alive','longest','total','queen'),(result.pointer(s).i32(o) for o in (0,4,8,12)))) for s in (0,1)]
    assert all(all(snaps[rnd][s][k]==v for k,v in final[s].items()) for s in (0,1))
    out=dict(gid=gid,w=w,h=h,queens=queens,final=final,last_round=rnd,ended_by=result.u16(2),winner=result.u16(6),turns=turns,deaths=deaths,splits=splits,snaps=snaps,near_after_death=near,teams=teams,final_bodies=frame(),edges=edges)
    (OUT/f'{gid}.json').write_text(json.dumps(out,separators=(',',':')))
    print(json.dumps(dict(gid=gid,size=[w,h],queens=queens,final=final,last_round=rnd,qdeaths=[{k:v for k,v in d.items() if k not in ('frame','pearls','body')} for d in deaths if d['id'] in queens],near_count=len(near),near_first=near[:3],checkpoints={r:snaps[r] for r in (0,25,50,100,200,300,400,499) if r in snaps})))

if __name__=='__main__':
    for gid in (1515662,1515664,1515667): scan(gid)
