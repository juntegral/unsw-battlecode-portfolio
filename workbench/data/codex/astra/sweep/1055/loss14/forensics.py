import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter
sys.path[:0] = ['tools','data/analysis/ladder/dossier/local']
from spawn import read
from replay_format import point
from count_local import Geo
from ladder_replay import canonical_edges, edge_id

OUT=Path(__file__).resolve().parent
for gid,bid in [(1504731,1504730),(1504016,1504016),(1504017,1504016)]:
    ledger=json.loads((OUT/f'{gid}-ledger.json').read_text())
    root=read(Path(f'data/online/live-one1/b{bid}/M{gid}.replay'))
    w,h=map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,raw={},{},[]
    for line in root.text(0).splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1]); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
    geo=Geo(w,h,raw); edges=canonical_edges(w,h,raw)
    uq,tq=ledger['queens']['us'],ledger['queens']['them']
    qdeath=next(d for d in ledger['deaths'] if d['id']==uq)
    involved={uq,qdeath['actor']}
    for d in ledger['deaths']:
        if d['collision'] and d['collision']==qdeath['collision']:involved.add(d['id'])
    rnd=-1;actor=None;pearls=set();turn=None;turns=[];qt=[];split=[];close=[];positions=set();logs=[]
    distances={}; rev=[[] for _ in geo.adj]
    for c,adj in enumerate(geo.adj):
        for dest in adj: rev[dest].append(c)
    def xy(c):return [c%w,c//w]
    def distance_to(c):
        if c not in distances:
            ds={c:0};queue=deque([c])
            while queue:
                p=queue.popleft()
                for n in rev[p]:
                    if n not in ds:ds[n]=ds[p]+1;queue.append(n)
            distances[c]=ds
        return distances[c]
    def proximity(idx):
        if uq in bodies or tq not in bodies:return
        p=bodies[tq][0];positions.add(p);ds=distance_to(p)
        for i,b in bodies.items():
            if teams[i]==1 and ds.get(b[0],999)<=5:
                key=(rnd,i)
                if key not in close_seen:
                    close_seen.add(key);close.append(dict(r=rnd,event=idx,id=i,L=len(b),head=xy(b[0]),queen=xy(p),distance=ds[b[0]]))
    close_seen=set()
    def board(center):
        cx,cy=xy(center);occ={c:('Q' if i==uq and j==0 else 'q' if i==uq else 'K' if i==tq and j==0 else 'B' if teams[i]==1 and j==0 else 'b' if teams[i]==1 else 'A' if j==0 else 'a') for i,b in bodies.items() for j,c in enumerate(b)}
        rows=[]
        for dy in range(-3,4):
            chars='';north=''
            for dx in range(-3,4):
                x,y=(cx+dx)%w,(cy+dy)%h;c=y*w+x
                kn=edges.get(edge_id(w,h,x,y,0),(0,-1))[0];kw=edges.get(edge_id(w,h,x,y,3),(0,-1))[0]
                north+='+'+('-' if kn==1 else 'P' if kn==2 else ' ')
                chars+=('|' if kw==1 else 'P' if kw==2 else ' ')+occ.get(c,'*' if c in pearls else '.')
            rows+=[north+'+',chars+' ']
        rows.append('+'+' +'*7)
        return '\n'.join(rows)
    def finish():
        if turn is not None:
            turn['after']=list(bodies.get(actor,()))
            turns.append(turn)
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            finish();turn=None;rnd=p.i32(0);actor=None
        elif k==1:
            finish();actor=p.i32(0);b=bodies[actor];head=b[0]
            turn=dict(r=rnd,event=idx,id=actor,team=teams[actor],body=list(b),eats=0,steps=[],portals=0,logs=[])
            turn['options']=[dict(d=d,kind=kind,to=xy(dest),owner=next((i for i,bb in bodies.items() if dest in bb),None),pearl=dest in pearls) for d,(kind,dest) in enumerate(geo.moves[head])]
            if actor==uq:
                turn['board']=board(head);turn['near']={i:list(bb) for i,bb in bodies.items() if set(bb)&geo.window(head)}
                turn['units']=sum(teams[i]==1 for i in bodies);qt.append(turn)
            proximity(idx)
        elif k==3:
            c=point(p.pointer(0));c=c[1]*w+c[0]
            if p.u32(0):pearls.add(c)
            else:
                pearls.remove(c)
                if turn:turn['eats']+=1
        elif k==4:
            a=p.pointer(0);act=a.u16(0) if a else 0
            turn['action']=act;turn['dirs']=list(a.pointer(0)) if a and act==0 and a.pointer(0) is not None else []
            turn['child']=a.i32(4) if a and act==1 else None
        elif k==6:
            log=dict(r=rnd,id=p.i32(0),text=p.text(0));logs.append(log)
            if turn:turn['logs'].append(log['text'])
        elif k==9:
            i=p.i32(0);hp=point(p.pointer(0));tp=point(p.pointer(1));hc=hp[1]*w+hp[0];tc=tp[1]*w+tp[0];b=bodies[i]
            if b[0]!=hc:
                if turn and i==actor:
                    step=len(turn['steps']);direction=turn.get('dirs',[])[step] if step<len(turn.get('dirs',[])) else None
                    if direction is not None and geo.moves[b[0]][direction][0]==2:turn['portals']+=1
                    turn['steps'].append(xy(hc))
                b.appendleft(hc)
            while len(b)>1 and b[-1]!=tc:b.pop()
            assert b[-1]==tc
            proximity(idx)
        elif k==10:
            ids=(p.i32(0),p.i32(4));prior=len(bodies[ids[0]])
            for j,i in enumerate(ids):
                bodies[i]=deque(c.i32(4)*w+c.i32(0) for c in p.pointer(j));teams[i]=p.u16(8)
            split.append(dict(r=rnd,id=ids[0],child=ids[1],before=prior,after=len(bodies[ids[0]]),units=sum(teams[i]==1 for i in bodies),body=list(bodies[ids[0]])))
            proximity(idx)
        elif k==11:
            bodies.pop(p.i32(0));proximity(idx)
    finish()
    result=dict(w=w,h=h,queens=[uq,tq],qturns=qt,turns=turns,splits=split,close=close,enemy_queen_postdeath_positions=[xy(c) for c in sorted(positions)],logs=logs)
    (OUT/f'{gid}-details.json').write_text(json.dumps(result,ensure_ascii=False))
    print('\nGAME',gid,'size',w,h,'queen last turns',flush=True)
    for t in qt[-5:]: print({k:v for k,v in t.items() if k not in ('board','near')},flush=True)
    print('q splits',[s for s in split if s['id']==uq],flush=True)
    print('attacker turns',[t for t in turns if t['id'] in involved and abs(t['r']-qdeath['round'])<=3 and t['id']!=uq],flush=True)
    print('postdeath near count',len(close),'first',close[:3],flush=True)
    print('portal crossings A/B', [sum(t['portals'] for t in turns if t['team']==s) for s in (0,1)],flush=True)
