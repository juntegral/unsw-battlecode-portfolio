import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import deque, defaultdict, Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
STEP = ((0,-1),(1,0),(0,1),(-1,0))

def scan(gid):
    root = replay.load(f'data/online/smoke/one13-c1-old/M{gid}.replay').root()
    W,H = map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,raw = {},{},[]
    for line in root.text(0).splitlines():
        q=line.split()
        if q[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2]))); teams[i]=int(q[1])
        if q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
    edges=canonical_edges(W,H,raw); portals=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2:portals[p].append(e)
    def dest(c,d):
        e=edge_id(W,H,*c,d); k,p=edges.get(e,(0,-1))
        if k==1:return None
        if k==2:
            z=next(z for z in portals[p] if z!=e); row,x=divmod(z,W+1)
            return ((x-(d==3))%W,(row//2-(d==0))%H)
        dx,dy=STEP[d];return ((c[0]+dx)%W,(c[1]+dy)%H)
    cache={}
    def distances(src):
        if src not in cache:
            ds={src:0}; qu=deque([src])
            while qu:
                c=qu.popleft()
                if ds[c]>=5:continue
                for d in range(4):
                    n=dest(c,d)
                    if n is not None and n not in ds:ds[n]=ds[c]+1;qu.append(n)
            cache[src]=ds
        return cache[src]
    def board(i):
        h=bodies[i][0]; grid=[]; near={}
        for dy in range(-3,4):
            row=[]
            for dx in range(-3,4):
                c=((h[0]+dx)%W,(h[1]+dy)%H); ch='o' if c in pearls else '.'
                for z,b in bodies.items():
                    if c in b:
                        ch=('Q' if z==i else 'A' if teams[z]==teams[i] else 'E') if c==b[0] else ('q' if z==i else 'a' if teams[z]==teams[i] else 'e')
                        near[z]=dict(team=teams[z],length=len(b),head=b[0])
                walls=''.join('NESW'[d] if edges.get(edge_id(W,H,*c,d),(0,-1))[0]==1 else 'nesw'[d] if edges.get(edge_id(W,H,*c,d),(0,-1))[0]==2 else '' for d in range(4))
                row.append(ch+walls)
            grid.append(row)
        return dict(head=h,body=list(bodies[i]),grid=grid,near=near)
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    rnd=-1;actor=None;turn=None;pearls=set();turns=[];deaths=[];splits=[];snaps={};eaten=[0,0];cross=[0,0];close=[];eq_positions=Counter()
    def snapshot():
        return [dict(n=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),queen=len(bodies.get(queens[s],())),pearls=eaten[s],portals=cross[s]) for s in (0,1)]
    def finish():
        if turn is not None:
            turn['end']=list(bodies.get(actor,()));turns.append(turn)
    def proximity(event):
        if queens[0] in bodies or queens[1] not in bodies:return
        q=bodies[queens[1]][0];eq_positions[q]+=1
        near=[(distances(b[0]).get(q,99),i,b[0]) for i,b in bodies.items() if teams[i]==0]
        if near:
            d,i,h=min(near)
            if d<=5:close.append(dict(r=rnd,event=event,id=i,head=h,q=q,d=d))
    for ix,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            finish();turn=None
            if rnd>=0:snaps[rnd]=snapshot()
            rnd=p.i32(0)
        elif k==1:
            finish();actor=p.i32(0)
            turn=dict(r=rnd,id=actor,team=teams[actor],start=list(bodies[actor]),eats=[],moves=[],actions=[])
            if actor in queens or (gid==1506227 and rnd in (403,406,475,476,477)) or (gid==1506226 and rnd in (119,120,121)):
                turn['board']=board(actor)
            proximity(ix)
        elif k==4:
            a=p.pointer(0)
            turn['actions'].append(dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],data=[a.i32(i) for i in (0,4,8)]))
        elif k==3:
            c=replay.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.discard(c);eaten[teams[actor]]+=1;turn['eats'].append(c)
        elif k==9:
            i=p.i32(0);hd,tl=replay.point(p.pointer(0)),replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                was=b[0]
                isportal=any(edges.get(edge_id(W,H,*was,d),(0,-1))[0]==2 and dest(was,d)==hd for d in range(4))
                cross[teams[i]]+=isportal
                if i==actor:turn['moves'].append(dict(src=was,dst=hd,portal=isportal))
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
            assert b[-1]==tl
            proximity(ix)
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            rec=dict(r=rnd,id=parent,child=child,old=list(bodies[parent]))
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
            rec.update(parent_body=list(bodies[parent]),child_body=list(bodies[child]));splits.append(rec)
            proximity(ix)
        elif k==11:
            i=p.i32(0);rec=dict(r=rnd,id=i,actor=actor,reason=p.u16(4),body=list(bodies[i]),attacker=list(turn['start']),moves=list(turn['moves']))
            if i in queens:rec['board']=board(i)
            deaths.append(rec);bodies.pop(i);proximity(ix)
    finish();snaps[rnd]=snapshot()
    final=root.pointer(4)
    for s in (0,1):
        st=final.pointer(s);ls=[len(b) for i,b in bodies.items() if teams[i]==s]
        assert (len(ls),max(ls,default=0),sum(ls),len(bodies.get(queens[s],())))==tuple(st.i32(j) for j in (0,4,8,12))
    qdiff=[r for r,s in snaps.items() if s[0]['queen']>=s[1]['queen']]
    out=dict(gid=gid,botA=root.text(1),size=[W,H],queens=queens,final=snaps[rnd],final_bodies={i:list(b) for i,b in bodies.items()},teams=teams,snaps=snaps,turns=turns,deaths=deaths,splits=splits,close=close,eq_positions=[[k,v] for k,v in eq_positions.items()],permanent_queen_deficit=max(qdiff)+1 if qdiff else 0)
    (OUT/f'{gid}-detail.json').write_text(json.dumps(out,separators=(',',':')))
    print(gid,'bot',out['botA'],'queens',queens,'final',out['final'],'permanent deficit',out['permanent_queen_deficit'],'qdeaths',[d for d in deaths if d['id'] in queens],'postdeath first close',close[:1],flush=True)

if __name__=='__main__':
    for gid in (1506225,1506226,1506227):scan(gid)
