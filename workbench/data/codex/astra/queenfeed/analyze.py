import sys
sys.dont_write_bytecode = True
import json, hashlib
from pathlib import Path
from collections import deque, Counter
sys.path.insert(0, 'data/analysis/ladder/dossier/online')
sys.path.insert(0, 'data/analysis/ladder/dossier')
import label_report as lr
from count_dossier import Geo
OUT = Path('data/codex/astra/queenfeed')
LABELS = ['one'+v+'-'+s for s, vs in [('w1','2345'),('d1','1345')] for v in vs]

def scan(label, path, meta):
    root = lr.agg.sb.load_replay(path).root()
    lines = root.text(0).splitlines()
    w,h = map(int, lines[0].split()[1:3])
    bodies,teams,raw = {},{},[]
    own = int(meta['teamAId'] != 1119)
    for line in lines:
        x = line.split()
        if x and x[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque(int(x[4+2*k])*w+int(x[3+2*k]) for k in range(int(x[2])));teams[i]=int(x[1])
        elif x and x[0]=='EDGE': raw.append(tuple(map(int,x[1:4])))
    geo=Geo(w,h,raw)
    queen=min(i for i in bodies if teams[i]==own)
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    start={i:list(b) for i,b in bodies.items()}
    def man(a,b):
        dx,dy=abs(a%w-b%w),abs(a//w-b//w)
        return min(dx,w-dx)+min(dy,h-dy)
    def pos(c): return [c%w,c//w] if c is not None else None
    tile=lambda p:lr.agg.sb.replay_format.point(p)[1]*w+lr.agg.sb.replay_format.point(p)[0]
    rnd,actor=-1,None
    present={};pending=deque();eats=[];births=[];qt=[];snaps={};qpearls=0;deaths=[];splits=[];pearls=[0,0];turnhead=None;actions=[]
    def qstate(detail=False):
        if queen not in bodies:return dict(alive=False, pearls=qpearls)
        hd=bodies[queen][0];mates=[b[0] for i,b in bodies.items() if teams[i]==own and i!=queen]
        ds=[man(hd,c) for c in mates]
        z=dict(alive=True, head=pos(hd), length=len(bodies[queen]), nearest_mate=min(ds,default=None), mates5=sum(d<=5 for d in ds), pearls=qpearls,
               pearl_distance=min((man(hd,c) for c in present),default=None), pearls5=sum(man(hd,c)<=5 for c in present),
               view_pearls=sum(min(abs(hd%w-c%w),w-abs(hd%w-c%w))<=3 and min(abs(hd//w-c//w),h-abs(hd//w-c//w))<=3 for c in present))
        if detail:
            d=geo.bfs([hd]); z['pearl_path']=min((d[c] for c in present if d[c]<65535),default=None)
            z['nearest_pearl']=pos(min(present,key=lambda c:(man(hd,c),c))) if present else None
            z['mate_heads']=[pos(c) for c in mates];z['pearl_tiles']=[pos(c) for c in sorted(present)]
        return z
    def snap():
        return dict(queen=qstate(True), sides=[dict(alive=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),queen_length=len(bodies.get(queens[s],())),pearls=pearls[s]) for s in (own,1-own)])
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0)
        if k not in (0,1,3,4,9,10,11):continue
        p=ev.pointer(0)
        if k==0:
            if rnd in (0,11,12,30,60,100,300):snaps[rnd]=snap()
            rnd,actor=p.i32(0),None
        elif k==1:
            actor=p.i32(0);turnhead=bodies[actor][0]
            if actor==queen:qt.append(dict(round=rnd,**qstate(rnd in (0,11,12,30,60,100))))
        elif k==4 and rnd<=12:
            a=p.pointer(0)
            actions.append([rnd,actor,a.u16(0),list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else []])
        elif k==3:
            cell=tile(p.pointer(0))
            if p.u32(0):
                origin=None
                if pending:
                    c,origin=pending.popleft();assert c==cell
                present[cell]=origin
                if origin is None and rnd<=30:births.append([rnd,cell])
            else:
                origin=present.pop(cell);pearls[teams[actor]]+=1
                if actor==queen:qpearls+=1
                if rnd<=100 or actor==queen:
                    qhd=bodies[queen][0] if queen in bodies else None
                    eats.append(dict(round=rnd,actor=actor,side=int(teams[actor]!=own),queen=actor==queen,cell=pos(cell),origin=origin,
                                     queen_distance=man(qhd,cell) if qhd is not None else None,actor_distance=man(turnhead,cell),
                                     queen_adjacent=qhd is not None and cell in geo.adj[qhd]))
        elif k==9:
            i=p.i32(0);hd,tail=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
            if b[0]!=hd:b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            if parent==queen:splits.append([rnd,len(bodies[parent])])
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
        elif k==11:
            i=p.i32(0)
            if i==queen:deaths.append(dict(round=rnd,reason=p.u16(4),actor=actor,length=len(bodies[i]),state=qstate(True)))
            pending.extend((c,dict(actor=i,side=int(teams[i]!=own),round=rnd)) for j,c in enumerate(bodies[i]) if j%2==0)
            bodies.pop(i)
    last=snap()
    for cp in (12,30,60,100,300):
        if cp>=rnd:snaps[cp]=last
    extra=lr.agg.supplement(root,meta,geo)
    base={'final':dict(last['sides'][0],longest=max((len(b) for i,b in bodies.items() if teams[i]==own),default=0)),
          'their':dict(last['sides'][1],longest=max((len(b) for i,b in bodies.items() if teams[i]!=own),default=0)), 'extra':extra}
    details=lr.scan_details(root,meta,geo,base)
    assert qpearls==details['queen_counts'].get('pearls',0)
    assert pearls[own]==extra['counts'].get('eaten',0)
    for a,b in zip(qt,details['queen_turns']):assert a['round']==b['round'] and a['mates5']==b['mates5'] and a['length']==b['length']
    assert len(qt)==len(details['queen_turns'])
    for s in (0,1):assert last['sides'][s]['total']==meta['scores'+'AB'[(own,1-own)[s]]]
    return dict(label=label,game=meta['id'],map=meta['mapName'],map_id=meta['mapId'],own=own,queen_id=queen,w=w,h=h,
                bots=[root.text(1),root.text(2)],map_hash=hashlib.sha256(root.text(0).encode()).hexdigest(),start=start,last=rnd,
                queen_pearls=qpearls,death=deaths[0] if deaths else None,feeder_eat=extra['counts']['feeder_eat'],
                queen_counts=details['queen_counts'],snaps=snaps,qt=qt,eats=eats,births=births,actions=actions,splits=splits)

if __name__=='__main__':
    for label in LABELS:
        dest=OUT/(label+'.jsonl')
        if dest.exists():continue
        inv=lr.inventory(label,'old');assert len(inv['jobs'])==15,(label,len(inv['jobs']),inv['notes'])
        with dest.open('w') as f:
            for path,meta in inv['jobs']:
                row=scan(label,path,meta);f.write(json.dumps(row,separators=(',',':'))+'\n');f.flush()
        print(label,'done',flush=True)
