import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter
sys.path[:0] = ['tools', 'data/analysis/ladder/losses/counts']
import ladder_replay as lr
from count_replays import Geometry

OUT = Path(__file__).parent
FOLDER = Path('data/online/smoke/one12-p1-old')

def analyze(gid):
    path = FOLDER / f'M{gid}.replay'
    meta = json.loads((FOLDER / f'game-{gid}.json').read_text())
    base = lr.scan(path, meta, str(FOLDER), set())
    root = lr.replay.load(path).root()
    w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,edges = {},{},[]
    for line in root.text(0).splitlines():
        p = line.split()
        if p[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque((int(p[3+2*k]),int(p[4+2*k])) for k in range(int(p[2]))); teams[i]=int(p[1])
        elif p[0]=='EDGE': edges.append(tuple(map(int,p[1:4])))
    geo=Geometry(w,h,edges)
    pearls=set(); turns=[]; qt=[]; splits=[]; nearby=[]; rnd=-1; actor=None; turn=None
    q=base['queens']['us']; eq=base['queens']['them']
    def coord(c): return (c%w,c//w)
    def cell(c): return c[1]*w+c[0]
    def state(): return {i:list(b) for i,b in bodies.items()}
    def check(index):
        if q not in bodies and eq in bodies:
            dist=geo.distances(cell(bodies[eq][0]))
            close=[(i,dist[cell(b[0])]) for i,b in bodies.items() if teams[i]==0 and dist[cell(b[0])]<=5]
            if close: nearby.append(dict(round=rnd,event=index,enemy_head=bodies[eq][0],close=close))
    for index,ev in enumerate(root.pointer(3)):
        kind=lr.replay.EVENT_NAMES[ev.u16(0)]; p=ev.pointer(0)
        if kind=='roundStart': rnd=p.i32(0);actor=None
        elif kind=='turnStart':
            actor=p.i32(0)
            turn=dict(round=rnd,event=index,id=actor,length=len(bodies[actor]),head=bodies[actor][0],eats=0,steps=[],action=None)
            turns.append(turn)
            if actor in (q,eq):
                turn['state']=state(); turn['pearls']=list(pearls); qt.append(turn)
        elif kind=='dragonAction':
            a=p.pointer(0)
            turn['action']=a.u16(0) if a else None
            turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif kind=='tileChange':
            c=lr.replay.point(p.pointer(0))
            if p.u32(0): pearls.add(c)
            else: pearls.discard(c);turn['eats']+=1
        elif kind=='dragonUpdate':
            i=p.i32(0);hd=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
            if hd!=b[0]:
                turn['steps'].append(hd);b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif kind=='dragonSplit':
            parent,child=p.i32(0),p.i32(4)
            split=dict(round=rnd,parent=parent,child=child,before=list(bodies[parent]),units=sum(teams[i]==teams[parent] for i in bodies))
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
            split['after']=list(bodies[parent]);splits.append(split)
        elif kind=='dragonDeath':bodies.pop(p.i32(0))
        if kind in ('turnStart','dragonUpdate','dragonSplit','dragonDeath'):check(index)
    summary={k:base[k] for k in ('gid','map','bots','queens','q_eats','q_splits','final','last_round','end_reason','winner','eats','anomalies')}
    summary['queen_deaths']=[d for d in base['deaths'] if d['id'] in (q,eq)]
    summary['queen_splits']=[s for s in splits if s['parent']==q]
    summary['near_after_death']=dict(events=len(nearby),rounds=len(set(n['round'] for n in nearby)),first=nearby[:1],last=nearby[-1:])
    summary['permanent_queen_deficit']=next((r for r in sorted(base['snapshots']) if all(s['us']['queen_length']<s['them']['queen_length'] for r2,s in base['snapshots'].items() if r2>=r)),None)
    summary['checkpoints']={r:base['snapshots'][r] for r in (0,10,25,50,100,150,200,300,400,499) if r in base['snapshots']}
    summary['our_last_queen_turns']=[{k:v for k,v in t.items() if k not in ('state','pearls')} for t in qt if t['id']==q][-3:]
    for t in qt:
        if t['id']!=q:continue
        t['neighbors']=[dict(direction=d,kind=k,destination=coord(c),occupants=[i for i,b in t['state'].items() if coord(c) in b]) for d,(k,c) in enumerate(geo.moves[cell(t['head'])])]
    data=dict(summary=summary,queen_turns=qt,turns=[{k:v for k,v in t.items() if k not in ('state','pearls')} for t in turns],splits=splits,deaths=base['deaths'],snapshots=base['snapshots'],teams=teams,edges=edges,w=w,h=h,nearby=nearby)
    (OUT/f'{gid}.json').write_text(json.dumps(data,ensure_ascii=False))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

for gid in (1503510,1503512,1503513): analyze(gid)
