import sys
sys.dont_write_bytecode = True
from pathlib import Path
from collections import deque, Counter
import json
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'data/analysis/ladder/dossier/local'))
from spawn import read
from replay_format import point
from count_local import Geo

def scan(gid):
    root=read(ROOT/f'data/online/smoke/one13-p2-old/M{gid}.replay')
    bodies, teams, raw, fountains = {}, {}, [], set()
    for line in root.text(0).splitlines():
        q=line.split()
        if not q: continue
        if q[0]=='MAP': w,h=map(int,q[1:3])
        if q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1]); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        if q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
        if q[0]=='TILE' and int(q[4])>0: fountains.add(int(q[2])*w+int(q[1]))
    g=Geo(w,h,raw); qs=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    tile=lambda p: point(p)[1]*w+point(p)[0]
    xy=lambda c: [c%w,c//w]
    pearls=set(); eats=[0,0]; turns=[]; deaths=[]; splits=[]; snaps={}; close=[]; rnd=-1; actor=None; cur=None
    def summary():
        return [dict(n=sum(teams[i]==s for i in bodies),q=len(bodies.get(qs[s],[])),long=max([len(b) for i,b in bodies.items() if teams[i]==s],default=0),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),eats=eats[s]) for s in (0,1)]
    def board(c):
        chars={t:('Q' if i==qs[0] else 'K' if i==qs[1] else 'A' if teams[i]==0 else 'B') if k==0 else ('a' if teams[i]==0 else 'b') for i,b in bodies.items() for k,t in enumerate(b)}
        return [''.join(chars.get(((c//w+dy)%h)*w+(c%w+dx)%w,'*' if ((c//w+dy)%h)*w+(c%w+dx)%w in pearls else '+' if ((c//w+dy)%h)*w+(c%w+dx)%w in fountains else '.') for dx in range(-3,4)) for dy in range(-3,4)]
    def endturn():
        if cur is not None:
            cur['end']=xy(bodies[actor][0]) if actor in bodies else None
            cur['endlen']=len(bodies.get(actor,[]))
    def proximity(idx):
        if qs[0] in bodies or qs[1] not in bodies: return
        target=bodies[qs[1]][0]
        # Directed reverse BFS: distance from each ally to their queen, through portals.
        if target not in distances:
            d={target:0}; queue=deque([target])
            while queue:
                c=queue.popleft()
                for t in rev[c]:
                    if t not in d: d[t]=d[c]+1; queue.append(t)
            distances[target]=d
        near=[(distances[target].get(b[0],99999),i) for i,b in bodies.items() if teams[i]==0]
        if near:
            dist,i=min(near)
            if not close or dist<min(z['dist'] for z in close) or (dist<=5 and not any(z['dist']<=5 for z in close)):
                close.append(dict(r=rnd,event=idx,id=i,dist=dist,head=xy(bodies[i][0]),queen=xy(target)))
    rev=[[] for _ in g.adj]
    for c,adj in enumerate(g.adj):
        for t in adj: rev[t].append(c)
    distances={}
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:
            endturn()
            if rnd>=0: snaps[rnd]=summary()
            rnd=p.i32(0);actor=None;cur=None
        elif k==1:
            endturn();actor=p.i32(0)
            cur=dict(r=rnd,event=idx,id=actor,side=teams[actor],L=len(bodies[actor]),head=xy(bodies[actor][0]),steps=[],eat=0)
            if actor in qs:
                cur.update(board=board(bodies[actor][0]),bodies={i:[xy(c) for c in b] for i,b in bodies.items()},pearls=[xy(c) for c in pearls],edges=[(xy(c),g.moves[c]) for c in g.window(bodies[actor][0])])
            turns.append(cur);proximity(idx)
        elif k==4:
            a=p.pointer(0)
            cur['action']=a.u16(0) if a else None
            cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0): pearls.add(c)
            else:
                pearls.remove(c);eats[teams[actor]]+=1;cur['eat']+=1
        elif k==9:
            i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));b=bodies[i]
            if hd!=b[0]:
                if i==actor:cur['steps'].append(xy(hd))
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            proximity(idx)
        elif k==10:
            i,j=p.i32(0),p.i32(4)
            splits.append(dict(r=rnd,parent=i,child=j,before=len(bodies[i])))
            for z,n in enumerate((i,j)): bodies[n]=deque(tile(pt) for pt in p.pointer(z));teams[n]=p.u16(8)
        elif k==11:
            i=p.i32(0);dest=None
            if i==actor and len(cur['steps'])<len(cur.get('dirs',[])):
                dest=g.moves[bodies[i][0]][cur['dirs'][len(cur['steps'])]][1]
            deaths.append(dict(r=rnd,event=idx,id=i,side=teams[i],reason=p.u16(4),actor=actor,L=len(bodies[i]),head=xy(bodies[i][0]),dest=xy(dest) if dest is not None else None,hit=[j for j,b in bodies.items() if dest in b],turn=cur.copy()))
            bodies.pop(i);proximity(idx)
    endturn();snaps[rnd]=summary()
    for s in (0,1):
        st=root.pointer(4).pointer(s)
        assert [snaps[rnd][s][z] for z in ('n','long','total','q')]==[st.i32(o) for o in (0,4,8,12)]
    lead=[r for r,ss in snaps.items() if (ss[0]['q'],ss[0]['long'],ss[0]['total']) >= (ss[1]['q'],ss[1]['long'],ss[1]['total'])]
    data=dict(gid=gid,w=w,h=h,queens=qs,final=snaps[rnd],last=rnd,permanent_behind=max(lead)+1 if lead else 0,death=deaths,turns=turns,splits=splits,snaps=snaps,proximity=close,final_bodies={i:[xy(c) for c in b] for i,b in bodies.items()})
    (OUT/f'{gid}.json').write_text(json.dumps(data))
    print(gid,'final',data['final'],'permanent_behind',data['permanent_behind'],'queen_deaths',[{k:v for k,v in d.items() if k!='turn'} for d in deaths if d['id'] in qs], 'proximity',close)
    print('checkpoints',{r:snaps[r] for r in (0,25,50,100,200,300,400,499) if r in snaps})
    print('Q splits',[s for s in splits if s['parent'] in qs])
    for s,qid in enumerate(qs):
        qt=[t for t in turns if t['id']==qid]
        print('queen',qid,'eats',sum(t['eat'] for t in qt),'last turns',[{k:v for k,v in t.items() if k not in ('bodies','pearls','edges')} for t in qt[-3:]])

for gid in (1512565,1512566,1512568):scan(gid)
