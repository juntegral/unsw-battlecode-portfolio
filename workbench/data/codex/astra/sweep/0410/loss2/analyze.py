import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'data/analysis/ladder/dossier/local'),str(ROOT/'data/analysis/ladder/losses/counts')]
import ladder_replay as lr
from scoreboard import load_replay
from count_replays import Geometry
JOBS=[(1485657,'data/online/live-one1/b1485657'),*[(i,'data/online/smoke/one8-k1-old') for i in (1485169,1485170,1485174,1485180)]]

def scan(gid,folder):
    path=ROOT/folder/f'M{gid}.replay'; meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
    message=load_replay(path); root=message.root()
    original=lr.replay.load; lr.replay.load=lambda _:message
    base=lr.scan(path,meta,folder,set()); lr.replay.load=original
    base['intervals']={str(k):v for k,v in base['intervals'].items()}
    (OUT/f'{gid}-ledger.json').write_text(json.dumps(base,separators=(',',':')))
    w,h=map(int,root.text(0).splitlines()[0].split()[1:3]); bodies={}; teams={}; raw=[]
    for line in root.text(0).splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1]); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        elif q and q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    own=int(meta['teamAId']!=1119); side=lambda i:int(teams[i]!=own)
    queens=[min(i for i in bodies if side(i)==s) for s in (0,1)]; geo=Geometry(w,h,raw)
    xy=lambda c:[c%w,c//w]; tile=lambda p:lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
    pearls={}; rnd=-1; cur=None; turns=[]; qturns=[]; qdeaths=[]; snaps={}; nearest=None; close_events=[]
    def snap():
        return [dict(n=sum(side(i)==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if side(i)==s),long=max((len(b) for i,b in bodies.items() if side(i)==s),default=0),q=len(bodies.get(queens[s],())),top=sorted([(i,len(b),xy(b[0])) for i,b in bodies.items() if side(i)==s],key=lambda a:-a[1])[:4]) for s in (0,1)]
    def board(c):
        occ={v:('Q' if i==queens[0] else 'K' if i==queens[1] else 'A' if side(i)==0 else 'E') if j==0 else ('q' if i==queens[0] else 'k' if i==queens[1] else 'a' if side(i)==0 else 'e') for i,b in bodies.items() for j,v in enumerate(b)}
        cells=[((c//w+dy)%h)*w+(c%w+dx)%w for dy in range(-3,4) for dx in range(-3,4)]
        # Seven rows of cells with explicit north/east/south/west kelp masks separately.
        return dict(center=xy(c),rows=[''.join(occ.get(z,'*' if z in pearls else '.') for z in cells[k:k+7]) for k in range(0,49,7)],walls=[''.join(format(sum(1<<d for d,(kind,t) in enumerate(geo.moves[z]) if kind==1),'x') for z in cells[k:k+7]) for k in range(0,49,7)],near=[dict(id=i,s=side(i),L=len(b),head=xy(b[0]),visible_body=[xy(z) for z in b if z in cells]) for i,b in bodies.items() if any(z in cells for z in b)])
    def checknear(ev):
        nonlocal nearest
        if queens[0] in bodies or queens[1] not in bodies:return
        qh=bodies[queens[1]][0]; dist=geo.distances(qh)
        best=min(((dist[b[0]],i,b[0]) for i,b in bodies.items() if side(i)==0),default=None)
        if best and (nearest is None or best[0]<nearest['distance']):
            nearest=dict(round=rnd,event=ev,distance=best[0],id=best[1],L=len(bodies[best[1]]),head=xy(best[2]),enemy_q=xy(qh))
        if best and best[0]<=5 and (not close_events or close_events[-1]['round']!=rnd):
            close_events.append(dict(round=rnd,id=best[1],distance=best[0],head=xy(best[2]),enemy_q=xy(qh)))
    def close():
        if cur is not None:
            cur['end']=xy(bodies[cur['id']][0]) if cur['id'] in bodies else None
            cur['Lend']=len(bodies.get(cur['id'],()))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:
            close()
            if rnd>=0:snaps[rnd]=snap()
            rnd=p.i32(0);cur=None
        elif k==1:
            close(); i=p.i32(0); b=bodies[i]; c=b[0]; occ={z for bb in bodies.values() for z in bb}
            cur=dict(round=rnd,event=idx,id=i,s=side(i),L=len(b),head=xy(c),eats=0,natural=0,steps=[],split=None,dirs=[],free=sum(kind!=1 and dest not in occ for kind,dest in geo.moves[c]))
            if i==queens[side(i)]:
                cur['board']=board(c);cur['body']=[xy(z) for z in b];cur['team_n']=sum(side(z)==side(i) for z in bodies)
                cur['neighbour_pearls']=[xy(dest) for kind,dest in geo.moves[c] if kind!=1 and dest in pearls and dest not in occ]
                qturns.append(cur)
            turns.append(cur)
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0):pearls[c]=cur is None
            else:
                cur['eats']+=1;cur['natural']+=pearls.pop(c)
        elif k==4:
            a=p.pointer(0);cur['action']=a.u16(0) if a else None
            cur['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==9:
            i=p.i32(0);hd,tail=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                b.appendleft(hd)
                if cur and cur['id']==i:cur['steps'].append(xy(hd))
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            checknear(idx)
        elif k==10:
            parent,child=p.i32(0),p.i32(4);cur['split']=[parent,child,len(bodies[parent])]
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
            cur['split'] += [len(bodies[parent]),len(bodies[child])]; checknear(idx)
        elif k==11:
            i=p.i32(0)
            if i in queens:
                qdeaths.append(dict(id=i,s=side(i),round=rnd,reason=p.u16(4),actor=cur['id'],actor_turn=dict(cur),body=[xy(z) for z in bodies[i]],board=board(bodies[i][0])))
            bodies.pop(i);checknear(idx)
    close();snaps[rnd]=snap()
    for s,key in enumerate(('us','them')):
        assert [snaps[rnd][s][v] for v in ('n','total','long','q')]==[base['final'][key][v] for v in ('alive','total','longest','queen_length')]
    behind=lambda ss:(ss[0]['q'],ss[0]['long'],ss[0]['total'])<(ss[1]['q'],ss[1]['long'],ss[1]['total'])
    last_not_behind=max((r for r,ss in snaps.items() if not behind(ss)),default=-1)
    summary=dict(gid=gid,map=meta['mapName'],side='AB'[own],bots=base['bots'],queens=queens,final=snaps[rnd],last=rnd,permanent_behind=last_not_behind+1,qdeaths=qdeaths,nearest=nearest,close_rounds=len(close_events),first_close=close_events[:4],snaps=snaps,qturns=qturns)
    (OUT/f'{gid}-turns.json').write_text(json.dumps(turns,separators=(',',':')))
    (OUT/f'{gid}-evidence.json').write_text(json.dumps(summary,separators=(',',':')))
    print(json.dumps({k:v for k,v in summary.items() if k not in ('snaps','qturns','qdeaths')},ensure_ascii=False),flush=True)
    print('QDEATHS',json.dumps(qdeaths),flush=True)
for gid,folder in JOBS:scan(gid,folder)
