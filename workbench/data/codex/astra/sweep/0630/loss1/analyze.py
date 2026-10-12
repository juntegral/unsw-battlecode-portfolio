import sys, json, ast
sys.dont_write_bytecode = True
from pathlib import Path
from collections import deque, Counter, defaultdict
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work']
import ladder_replay as lr
import o1_scan
geo_source=Path('data/analysis/ladder/dossier/work/tq2_near.py').read_text()
geo_node=next(n for n in ast.parse(geo_source).body if isinstance(n,ast.ClassDef) and n.name=='Geo')
geo_env=dict(canonical_edges=lr.canonical_edges,edge_id=lr.edge_id,defaultdict=defaultdict,deque=deque,
             STEP=((0,-1),(1,0),(0,1),(-1,0)),CAP=8)
exec(compile(ast.Module(body=[geo_node],type_ignores=[]),'tq2_near.py','exec'),geo_env)
Geo=geo_env['Geo']

OUT = Path(__file__).resolve().parent
SRC = Path('data/online/smoke/one11-c1-old')

def scan(gid):
    path = SRC / f'M{gid}.replay'
    meta = json.loads((SRC / f'game-{gid}.json').read_text())
    ledger=o1_scan.scan('one11-c1-old',path,meta)
    (OUT/f'ledger-{gid}.json').write_text(json.dumps(ledger,separators=(',',':')))
    base = lr.scan(path, meta, 'one11-c1-old', set())
    root = lr.replay.load(path).root()
    w,h = map(int, root.text(0).splitlines()[0].split()[1:3])
    b,t,raw = {},{},[]
    for line in root.text(0).splitlines():
        q = line.split()
        if q[0]=='DRAGON':
            i=len(b); b[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2]))); t[i]=int(q[1])
        elif q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    geo=Geo(w,h,raw)
    reverse=[[] for _ in range(w*h)]
    for src,ns in enumerate(geo.nxt):
        for dest in ns:
            if dest>=0:reverse[dest].append(src)
    distance_cache={}
    qs=[base['queens']['us'],base['queens']['them']]
    rnd=-1; actor=None; turn=None; pearls=set(); turns=[]; qturns=[]; splits=[]; post=[]; deaths=[]
    cell=lambda p:p[1]*w+p[0]
    def snap(): return {i:list(bb) for i,bb in b.items()}
    def flush():
        if turn is not None:
            turn['end']=list(b[actor]) if actor in b else None
            turns.append(turn)
    def near():
        if qs[0] in b or qs[1] not in b: return
        target=cell(b[qs[1]][0])
        if target not in distance_cache:
            dist={target:0};queue=deque([target])
            while queue:
                at=queue.popleft()
                for src in reverse[at]:
                    if src not in dist:dist[src]=dist[at]+1;queue.append(src)
            distance_cache[target]=dist
        ns=[(distance_cache[target].get(cell(bb[0]),w*h+1),i,bb[0]) for i,bb in b.items() if t[i]==0]
        if ns:
            d,i,xy=min(ns)
            post.append(dict(r=rnd,event=idx,d=d,id=i,head=xy,qhead=b[qs[1]][0]))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:
            flush();turn=None;actor=None;rnd=p.i32(0)
        elif k==1:
            flush();actor=p.i32(0)
            turn=dict(r=rnd,event=idx,id=actor,side=t[actor],body=list(b[actor]),eats=[],moves=[],action=None)
            if actor in qs:
                turn['state']=snap();turn['pearls']=list(pearls);qturns.append(turn)
            near()
        elif k==4:
            a=p.pointer(0)
            turn['action']=a.u16(0) if a else None
            turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==3:
            xy=lr.replay.point(p.pointer(0))
            if p.u32(0): pearls.add(xy)
            else: pearls.remove(xy);turn['eats'].append(xy)
        elif k==9:
            i=p.i32(0);hd=lr.replay.point(p.pointer(0));tl=lr.replay.point(p.pointer(1))
            bb=b[i]
            if bb[0]!=hd:
                bb.appendleft(hd)
                if i==actor:turn['moves'].append(hd)
            while len(bb)>1 and bb[-1]!=tl:bb.pop()
            assert bb[-1]==tl
            near()
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            sp=dict(r=rnd,parent=parent,child=child,before=len(b[parent]))
            for z,i in enumerate((parent,child)):
                b[i]=deque(lr.replay.point(pt) for pt in p.pointer(z));t[i]=p.u16(8)
            sp.update(after=len(b[parent]),child_len=len(b[child]));splits.append(sp);near()
        elif k==11:
            i=p.i32(0)
            deaths.append(dict(r=rnd,id=i,actor=actor,reason=p.u16(4),state=snap() if i in qs else None))
            b.pop(i);near()
    flush()
    qdead=[d for d in base['deaths'] if d['id'] in qs]
    relevant={d['actor'] for d in qdead}
    result=dict(gid=gid,map=meta['mapName'],w=w,h=h,bot=root.text(1),queens=qs,final=base['final'],
                end_reason=base['end_reason'],last_round=base['last_round'],qdeaths=qdead,
                death_states=[d for d in deaths if d['id'] in qs],
                qturns=qturns,attacker_turns=[tr for tr in turns if tr['id'] in relevant],
                splits=splits,snapshots=base['snapshots'],post_near=post,
                deaths=base['deaths'],eats=base['eats'],teams=t,edges=raw,
                turns=[{k:v for k,v in tr.items() if k not in ('state','pearls')} for tr in turns])
    (OUT/f'{gid}.json').write_text(json.dumps(result,separators=(',',':')))
    compact={k:result[k] for k in ('gid','map','bot','queens','final','end_reason','last_round','qdeaths','eats')}
    compact['last_qturns']=[{k:v for k,v in tr.items() if k not in ('state','pearls')} for tr in qturns if tr['id']==qs[0]][-3:]
    compact['post_min']=min(post,key=lambda r:r['d']) if post else None
    compact['queen_splits']=[sp for sp in splits if sp['parent'] in qs]
    print(json.dumps(compact,ensure_ascii=False))

if __name__=='__main__':
    for gid in (1496845,1496846,1496847):scan(gid)
