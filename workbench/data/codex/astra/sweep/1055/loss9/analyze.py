import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import deque, defaultdict, Counter
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/local']
from ladder_replay import edge_id, canonical_edges
from scoreboard import load_replay
import replay_format as rf
OUT = Path(__file__).parent
JOBS = [(1503514, 'data/online/smoke/one12-p1-old'), (1503515, 'data/online/smoke/one12-p1-old'), (1503326, 'data/online/live-one1/b1503326')]
def scan(gid, folder):
    root = load_replay(Path(folder)/f'M{gid}.replay').root()
    meta = json.loads((Path(folder)/f'game-{gid}.json').read_text())
    own = int(meta['teamAId'] != 1119)
    lines = root.text(0).splitlines()
    w,h = map(int,lines[0].split()[1:3]); bodies={}; teams={}; raw=[]
    for line in lines:
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1]); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
        elif q and q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    queens=[min(i for i in bodies if teams[i]==s) for s in (own,1-own)]
    edges=canonical_edges(w,h,raw); portals=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2: portals[p].append(e)
    def dest(c,d):
        e=edge_id(w,h,*c,d); k,p=edges.get(e,(0,-1))
        if k==1:return None
        if k==2:
            other=next(z for z in portals[p] if z!=e); row,x=divmod(other,w+1); y=row//2
            return ((x-(d==3))%w,(y-(d==0))%h)
        dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d]
        return ((c[0]+dx)%w,(c[1]+dy)%h)
    reverse=defaultdict(list)
    for y in range(h):
        for x in range(w):
            for d in range(4):
                n=dest((x,y),d)
                if n is not None:reverse[n].append((x,y))
    cache={}
    def distances(target):
        if target not in cache:
            dist={target:0}; queue=deque([target])
            while queue:
                c=queue.popleft()
                for n in reverse[c]:
                    if n not in dist:dist[n]=dist[c]+1;queue.append(n)
            cache[target]=dist
        return cache[target]
    pearls=set(); turns=[]; deaths=[]; splits=[]; snaps={}; qt=[]; proximity=[]; eats=[]
    rnd=-1; turn=None; dead=False; minprox=999; qpositions=Counter()
    def state():
        return [dict(n=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),queen=len(bodies.get(queens[z],[]))) for z,s in enumerate((own,1-own))]
    def finish():
        if turn is not None:
            turn['end']=list(bodies.get(turn['id'],[]));turns.append(turn)
    def proximity_check(idx):
        nonlocal minprox
        if not dead or queens[1] not in bodies:return
        target=bodies[queens[1]][0]; ds=distances(target)
        near=sorted((ds.get(b[0],999),i,list(b[0])) for i,b in bodies.items() if teams[i]==own)
        if near and near[0][0]<minprox:
            minprox=near[0][0];proximity.append(dict(r=rnd,event=idx,distance=minprox,ours=near[0][1],head=near[0][2],queen=list(target)))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            finish();turn=None
            if rnd>=0:snaps[rnd]=state()
            rnd=p.i32(0)
            if dead and queens[1] in bodies:qpositions[bodies[queens[1]][0]]+=1
        elif k==1:
            finish();i=p.i32(0)
            turn=dict(r=rnd,event=idx,id=i,side=int(teams[i]!=own),body=list(bodies[i]),dirs=[],steps=[],eats=[])
            if i in queens or (teams[i]==own and len(bodies[i])>=8):
                turn['world']={j:list(b) for j,b in bodies.items()};turn['pearls']=list(pearls)
            if i==queens[0]:qt.append(turn)
        elif k==3:
            c=rf.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:
                pearls.discard(c)
                if turn is not None:turn['eats'].append(c);eats.append([rnd,turn['id'],turn['side'],c])
        elif k==4:
            a=p.pointer(0)
            turn['action']=a.u16(0) if a else None
            turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==9:
            i=p.i32(0);hd,tl=rf.point(p.pointer(0)),rf.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                b.appendleft(hd)
                if turn is not None:turn['steps'].append(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
            assert b[-1]==tl
            proximity_check(idx)
        elif k==10:
            a,c=p.i32(0),p.i32(4); before=list(bodies[a]); units=sum(teams[i]==teams[a] for i in bodies)
            for z,i in enumerate((a,c)):
                bodies[i]=deque(rf.point(t) for t in p.pointer(z));teams[i]=p.u16(8)
            splits.append(dict(r=rnd,parent=a,child=c,before=len(before),after=len(bodies[a]),childlen=len(bodies[c]),units=units))
            proximity_check(idx)
        elif k==11:
            i=p.i32(0)
            deaths.append(dict(r=rnd,event=idx,id=i,side=int(teams[i]!=own),reason=p.u16(4),body=list(bodies[i]),actor=turn['id'] if turn else None,attack=turn,world={j:list(b) for j,b in bodies.items()} if i in queens else None))
            if i==queens[0]:dead=True
            bodies.pop(i);proximity_check(idx)
    finish();snaps[rnd]=state()
    result=dict(gid=gid,meta=meta,bot=[root.text(1),root.text(2)][own],size=[w,h],queens=queens,teams=teams,final=state(),snapshots=snaps,queen_turns=qt,deaths=deaths,splits=splits,proximity=proximity,enemy_queen_positions=[[list(c),n] for c,n in qpositions.most_common()],eats=eats,turns=turns)
    (OUT/f'{gid}-detail.json').write_text(json.dumps(result,separators=(',',':')))
    print(gid,'queens',queens,'bot',result['bot'],'final',result['final'],flush=True)
    print('queen deaths', [{k:d[k] for k in ['r','id','reason','body','actor']} for d in deaths if d['id'] in queens],flush=True)
    print('proximity',proximity,'locations',result['enemy_queen_positions'][:5],flush=True)
if __name__=='__main__':
    for gid,folder in JOBS:scan(gid,folder)
