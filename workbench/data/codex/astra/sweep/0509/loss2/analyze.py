import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/losses/counts')
import ladder_replay as lr
from count_replays import Geometry

OUT = Path(__file__).resolve().parent
JOBS = [(1490643,1490641),(1490644,1490641),(1490796,1490796)]

def run(gid,bid):
    folder=Path(f'data/online/live-one1/b{bid}')
    meta=json.loads((folder/f'game-{gid}.json').read_text())
    path=folder/f'M{gid}.replay'
    base=lr.scan(path,meta,str(folder),set())
    base.pop('intervals')
    (OUT/f'{gid}-scan.json').write_text(json.dumps(base))
    root=lr.replay.load(path).root()
    lines=root.text(0).splitlines()
    w,h=map(int,lines[0].split()[1:3])
    raw=[tuple(map(int,q[1:4])) for q in map(str.split,lines) if q and q[0]=='EDGE']
    geo=Geometry(w,h,raw)
    bodies={};teams={};pearls=set();turns=[];splits=[];near=[];qt=[];r=-1;t=None
    us=base['ours'];qu=base['queens']['us'];qe=base['queens']['them']
    qdeath=next((d['round'] for d in base['deaths'] if d['id']==qu),None)
    for q in map(str.split,lines):
        if q and q[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]='AB'[int(q[1])]
    def cell(p): return p[1]*w+p[0]
    def view(center,p): return geo.visible(cell(center),cell(p))
    def snap():
        return dict(bodies={i:list(b) for i,b in bodies.items()},teams=dict(teams),pearls=sorted(pearls))
    def close():
        if t is not None:
            t['end']=list(bodies[t['id']][0]) if t['id'] in bodies else None
            t['endlen']=len(bodies.get(t['id'],()))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            close();t=None;r=p.i32(0)
        elif k==1:
            close();i=p.i32(0);b=bodies[i]
            t=dict(r=r,id=i,side=teams[i],head=list(b[0]),length=len(b),moves=[],eats=0,action=None)
            turns.append(t)
            if i==qu:
                t['enemies']=[dict(id=z,body=list(bb),visible=sum(view(b[0],pt) for pt in bb)) for z,bb in bodies.items() if teams[z]!=us and any(view(b[0],pt) for pt in bb)]
                if (qdeath is not None and qdeath-2<=r<=qdeath) or r in (0,1,10,50,100,200,300,350,400,450,475,499):
                    qt.append(dict(round=r,event=idx,**snap()))
            if qu not in bodies and qe in bodies and teams[i]==us:
                dist=geo.distances(cell(bodies[qe][0]))[cell(b[0])]
                if dist<=5:
                    near.append(dict(r=r,id=i,length=len(b),distance=dist,head=list(b[0]),queen=list(bodies[qe][0]),visible=view(b[0],bodies[qe][0])))
        elif k==4:
            a=p.pointer(0)
            if t is not None:
                t['action']=dict(kind=a.u16(0),dirs=list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [])
        elif k==3:
            pt=lr.replay.point(p.pointer(0))
            if p.u32(0):pearls.add(pt)
            else:
                pearls.discard(pt)
                if t is not None:t['eats']+=1
        elif k==9:
            i=p.i32(0);hd=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                b.appendleft(hd)
                if t is not None and t['id']==i:t['moves'].append(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif k==10:
            par,ch=p.i32(0),p.i32(4)
            splits.append(dict(r=r,parent=par,child=ch,before=len(bodies[par]),head=list(bodies[par][0])))
            for z,i in enumerate((par,ch)):
                bodies[i]=deque(lr.replay.point(pt) for pt in p.pointer(z));teams[i]='AB'[p.u16(8)]
        elif k==11:bodies.pop(p.i32(0))
    close()
    assert all(t['action'] is not None for t in turns)
    for side in ('us','them'):
        rawside=us if side=='us' else ('B' if us=='A' else 'A')
        assert sum(t['eats'] for t in turns if t['side']==rawside)==base['final'][side]['pearls']
    qturns=[t for t in turns if t['id']==qu]
    ranks=[]
    for rr,ss in base['snapshots'].items():
        a,b=ss['us'],ss['them']
        ranks.append((int(rr),(a['queen_length'],a['longest'],a['total'])<(b['queen_length'],b['longest'],b['total'])))
    turngood=next(rr for rr,lost in ranks if lost and all(v for rrr,v in ranks if rrr>=rr))
    data=dict(gid=gid,w=w,h=h,queens=base['queens'],turngood=turngood,queen_turns=qturns,boards=qt,near=near,splits=splits,turns=turns,final_bodies=snap())
    (OUT/f'{gid}-detail.json').write_text(json.dumps(data))
    print(gid,'turngood',turngood,'queen eats',sum(t['eats'] for t in qturns),'queen positions',Counter(tuple(t['head']) for t in qturns).most_common(8),'near',len(near),'first',near[:2])
    print('queen splits',[s for s in splits if s['parent']==qu])
    print('queen last3',[{k:v for k,v in t.items() if k!='enemies'} for t in qturns[-3:]])
    print('final longest',sorted([(i,len(b),b[0],teams[i]) for i,b in bodies.items()],key=lambda z:-z[1])[:12])

if __name__=='__main__':
    for gid,bid in JOBS:run(gid,bid)
