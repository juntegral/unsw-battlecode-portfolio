import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, defaultdict, Counter
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from ladder_replay import replay, edge_id, canonical_edges
from o1_scan import scan as ledger_scan

OUT = Path(__file__).resolve().parent
JOBS = [
 (1484435, 'data/online/smoke/one8-c1-old'),
 (1486051, 'data/online/live-one1/b1486051'),
 (1483995, 'data/online/live-one1/b1483995'),
 (1483996, 'data/online/live-one1/b1483995'),
 (1483999, 'data/online/live-one1/b1483995'),
 *[(i, 'data/online/smoke/one8-k1-old') for i in (1485168,1485171,1485172,1485173,1485175,1485176,1485177)]
]
STEP = ((0,-1),(1,0),(0,1),(-1,0))

def scan(gid, folder):
    path = Path(folder)/f'M{gid}.replay'
    meta = json.loads((Path(folder)/f'game-{gid}.json').read_text())
    root = replay.load(path).root()
    base = ledger_scan('win1', path, meta)
    assert meta['teamAId'] == 1119 and base['result'] == 'win'
    W,H = map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,raw = {},{},[]
    for line in root.text(0).splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1])
            bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
        elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
    start=[sum(len(b) for i,b in bodies.items() if teams[i]==s) for s in (0,1)]
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    edges=canonical_edges(W,H,raw); ports=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2:ports[p].append(e)
    def dest(h,d):
        e=edge_id(W,H,*h,d); k,p=edges.get(e,(0,-1))
        if k==1:return None
        if k==2:
            other=next(z for z in ports[p] if z!=e)
            row,x=divmod(other,W+1); y=row//2
            return ((x-(d==3))%W,(y-(d==0))%H)
        dx,dy=STEP[d];return ((h[0]+dx)%W,(h[1]+dy)%H)
    def gap(a,b):
        dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1])
        return min(dx,W-dx)+min(dy,H-dy)
    def visible(a,b):
        dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1])
        return min(dx,W-dx)<=3 and min(dy,H-dy)<=3
    def state():
        return [[sum(teams[i]==s for i in bodies),sum(len(b) for i,b in bodies.items() if teams[i]==s),
                 max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),len(bodies.get(queens[s],()))] for s in (0,1)]
    def exits(h):
        occupied={c for b in bodies.values() for c in b}
        return [c for d in range(4) if (c:=dest(h,d)) is not None and c not in occupied]
    def ram_path(i,target,cap=8):
        bb=tuple(bodies[i]); free=(len(bb)+3)//4
        occupied=set(c for z,b in bodies.items() if z!=i for c in b)
        queue=deque([(bb,(),(),0)]); seen=set()
        while queue:
            body,eaten,path0,paid=queue.popleft()
            n=len(path0)
            if n>=cap:continue
            for d in range(4):
                c=dest(body[0],d)
                if c is None or c in body:continue
                ispaid=n>=free
                if ispaid and len(body)<=2:continue
                if c==target:return dict(steps=n+1,path=path0+(d,),paid=paid+ispaid,pearls=len(eaten))
                if c in occupied:continue
                eat=c in pearls and c not in eaten
                nb=(c,)+body
                if not eat:nb=nb[:-1]
                if ispaid:nb=nb[:-1]
                ne=eaten+(c,) if eat else eaten
                key=(nb,ne,n+1)
                if key not in seen:
                    seen.add(key);queue.append((nb,ne,path0+(d,),paid+ispaid))
        return None

    pearls=set(); snapshots={}; turns=[]; deaths=[]; risks=[]; logs=[]
    rnd=-1;actor=None;t=None;facing={}; qlast={}; last_queen_turn=None
    def close():
        nonlocal t
        if t is None:return
        t['alive']=t['id'] in bodies
        t['end']=list(bodies[t['id']][0]) if t['alive'] else None
        t['endL']=len(bodies[t['id']]) if t['alive'] else 0
        if t['s']==0 and t['id']==queens[0] and t['alive']:
            q=bodies[queens[0]][0]
            near=[]
            for z,b in bodies.items():
                if teams[z]!=1 or gap(q,b[0])>8 or z<t['id']:continue
                if not visible(q,b[0]):continue
                reach=ram_path(z,q,4)
                if reach:near.append(dict(id=z,L=len(b),head=list(b[0]),**reach))
            if near:risks.append(dict(round=t['r'],queenL=t['endL'],head=t['end'],attackers=near))
        turns.append(t);t=None
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            close()
            if rnd>=0:snapshots[rnd]=state()
            rnd=p.i32(0);actor=None
        elif k==1:
            close();actor=p.i32(0);s=teams[actor];b=bodies[actor];h=b[0]
            occ={c for bb in bodies.values() for c in bb}
            adj=[dest(h,d) for d in range(4)]
            adjp=[list(c) for c in adj if c in pearls and c not in occ]
            mate=min(((gap(h,bb[0]),z,bb[0]) for z,bb in bodies.items() if teams[z]==s and z!=actor),default=None)
            t=dict(r=rnd,event=idx,id=actor,s=s,L=len(b),head=list(h),
                   adjp=adjp,free=sum(c is not None and c not in occ for c in adj),
                   directions=[],steps=[],eaten=[],split=False,death=None,
                   prior_dir=facing.get(actor),mate=mate,
                   ownN=sum(teams[z]==s for z in bodies),queenAlive=queens[s] in bodies)
            t['last_exit_choices']=[]
            for z,bb in bodies.items():
                if z==actor or teams[z]!=s or not visible(h,bb[0]):continue
                ee=exits(bb[0])
                wall=any(edges.get(edge_id(W,H,*bb[0],d),(0,-1))[0]==1 for d in range(4))
                if len(ee)==1 and ee[0] in adj and (z==queens[s] or wall):
                    t['last_exit_choices'].append(dict(id=z,queen=z==queens[s],cell=list(ee[0])))
            t['pocket_pearl_choices']=[]
            for c in adj:
                if c is None or c not in pearls or c in occ:continue
                open_edges=[d for d in range(4) if edges.get(edge_id(W,H,*c,d),(0,-1))[0]!=1]
                if len(open_edges)==1 and dest(c,open_edges[0])==h:
                    t['pocket_pearl_choices'].append(list(c))
            if actor in queens:qlast[s]=dict(t)
            if actor==queens[0]:last_queen_turn=dict(t)
        elif k==3:
            c=replay.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:
                assert c in pearls;pearls.remove(c)
                if t:t['eaten'].append(list(c))
        elif k==4:
            a=p.pointer(0)
            if t:
                t['actionKind']=a.u16(0) if a else None
                t['directions']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==6:
            logs.append(dict(round=rnd,id=p.i32(0),text=p.text(0)))
        elif k==9:
            i=p.i32(0);h,tail=replay.point(p.pointer(0)),replay.point(p.pointer(1));b=bodies[i]
            if h!=b[0]:
                b.appendleft(h)
                if t and i==actor:
                    t['steps'].append(list(h))
                    if len(t['steps'])<=len(t['directions']):facing[i]=t['directions'][len(t['steps'])-1]
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif k==10:
            a,ch=p.i32(0),p.i32(4)
            for z,i in enumerate((a,ch)):
                bodies[i]=deque(replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
            if t:t['split']=True
        elif k==11:
            i=p.i32(0);s=teams[i]
            death=dict(round=rnd,event=idx,id=i,side=s,reason=p.u16(4),L=len(bodies[i]),head=list(bodies[i][0]),
                       actor=actor,actorSide=teams.get(actor),actorL0=t['L'] if t else None,
                       stepsTaken=len(t['steps']) if t else None,queen=i==queens[s],state=state(),
                       actorHead=t['head'] if t else None,queenLast=qlast.get(s) if i==queens[s] else None)
            deaths.append(death)
            if t and i==actor:t['death']=p.u16(4)
            del bodies[i]
    close();snapshots[rnd]=state()
    assert state()==[x[:4] for x in base['ends']]
    for s in (0,1):
        eaten=sum(e[1]==s for e in base['eats'])
        dead=sum(d[2] for d in base['deaths'] if d[1]==s)
        paid=sum(d[3] for d in base['paids'] if d[1]==s)
        assert start[s]+eaten-dead-paid==base['ends'][s][1]
    def verdict(st):
        a,b=st
        return (a[0]>0)-(b[0]>0) if not a[0] or not b[0] else ((a[3],a[2],a[1])>(b[3],b[2],b[1]))-((a[3],a[2],a[1])<(b[3],b[2],b[1]))
    ahead=rnd
    for rr in reversed(sorted(snapshots)):
        if verdict(snapshots[rr])!=1:break
        ahead=rr
    own=[x for x in turns if x['s']==0]
    signatures={
        'eat_adj': [x for x in own if x['adjp'] and any(p in x['adjp'] for p in x['eaten'])],
        'miss_adj':[x for x in own if x['adjp'] and not any(p in x['adjp'] for p in x['eaten']) and not x['split']],
        'heading':[x for x in own if x['r']<12 and x['id']>1 and x['directions'] and x['directions'][0]==x['prior_dir']],
        'queen_split':[x for x in own if x['id']==queens[0] and x['split']],
        'idle':[x for x in own if not x['steps'] and not x['eaten'] and not x['split']],
        'sure_queen':[d for d in deaths if d['queen'] and d['side']==1 and d['reason']==3 and d['actorSide']==0 and d['actorL0']<=4],
        'stops':[x for x in own if x['death']==4],
        'queen_exit_kept':[x for x in own if x['steps'] and any(z['queen'] and z['cell'] not in x['steps'] for z in x['last_exit_choices'])],
        'mate_exit_kept':[x for x in own if x['steps'] and any(not z['queen'] and z['cell'] not in x['steps'] for z in x['last_exit_choices'])],
        'pocket_pearl_avoided':[x for x in own if x['steps'] and not x['split'] and x['pocket_pearl_choices'] and not any(c in x['steps'] for c in x['pocket_pearl_choices'])],
    }
    herd=[x for x in own if x['id']==queens[0] and x['mate'] and x['end'] and gap(tuple(x['end']),tuple(x['mate'][2]))<x['mate'][0]]
    signatures['herd_nearer']=herd
    out=dict(gid=gid,path=str(path),meta=meta,bot=base['bot'],queenIds=queens,W=W,H=H,
             ledger=base,states=snapshots,ahead_for_good=ahead,queenDeaths=[d for d in deaths if d['queen']],
             risks=risks,logs=logs,signatureCounts={k:len(v) for k,v in signatures.items()},
             signatureExamples={k:v[:3] for k,v in signatures.items()})
    (OUT/f'{gid}.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
    (OUT/f'{gid}-turns.jsonl').write_text(''.join(json.dumps(t,ensure_ascii=False,separators=(',',':'))+'\n' for t in turns))
    print(json.dumps({k:out[k] for k in ('gid','bot','queenIds','ahead_for_good','signatureCounts')},ensure_ascii=False),flush=True)
    print('END',base['ends'],'QDEATH',[(d['side'],d['round'],d['L'],d['reason'],d['actor'],d['actorL0']) for d in out['queenDeaths']],flush=True)
    return out

if __name__=='__main__':
    allrows=[scan(*j) for j in JOBS]
    (OUT/'summary.json').write_text(json.dumps([dict(gid=r['gid'],bot=r['bot'],ends=r['ledger']['ends'],ahead=r['ahead_for_good'],signatures=r['signatureCounts']) for r in allrows],ensure_ascii=False,indent=2)+'\n')
