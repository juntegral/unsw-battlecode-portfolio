import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter, deque, defaultdict
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work']
from ladder_replay import replay, scan as ledger, edge_id, canonical_edges
from o1_scan import scan as oldscan
HERE = Path(__file__).resolve().parent
JOBS = [(1485178,'data/online/smoke/one8-k1-old'),(1485179,'data/online/smoke/one8-k1-old'),(1485487,'data/online/live-one1/b1485486'),(1485488,'data/online/live-one1/b1485486'),(1485483,'data/online/live-one1/b1485483'),(1485484,'data/online/live-one1/b1485483'),(1485485,'data/online/live-one1/b1485483')]

def trace(path, meta):
    root=replay.load(path).root()
    w,h=map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in root.text(0).splitlines():
        z=line.split()
        if z and z[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque((int(z[3+2*k]),int(z[4+2*k])) for k in range(int(z[2])));teams[i]=int(z[1])
        elif z and z[0]=='EDGE':raw.append(tuple(map(int,z[1:4])))
    own=int(meta['teamAId']!=1119)
    side=lambda i: int(teams[i]!=own)
    qs=[min(i for i in bodies if side(i)==s) for s in (0,1)]
    edges=canonical_edges(w,h,raw); portals=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2:portals[p].append(e)
    def dest(c,d):
        e=edge_id(w,h,*c,d);k,p=edges.get(e,(0,-1))
        if k==1:return None
        if k==2:
            other=next(z for z in portals[p] if z!=e);row,x=divmod(other,w+1)
            return ((x-(d==3))%w,(row//2-(d==0))%h)
        dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d];return ((c[0]+dx)%w,(c[1]+dy)%h)
    def gap(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(dx,w-dx)+min(dy,h-dy)
    def view(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
    def bfs(a,target,R,occ=set()):
        q=deque([(a,0)]);seen={a}
        while q:
            c,n=q.popleft()
            if c==target:return n
            if n==R:continue
            for d in range(4):
                z=dest(c,d)
                if z is not None and z not in seen and (z==target or z not in occ):seen.add(z);q.append((z,n+1))
        return 99
    present={}; turns=[]; splits=[]; deaths=[]; risk=[];rnd=-1;actor=None;t=None;heading={}
    def finish():
        nonlocal t
        if t is None:return
        if actor in bodies:
            t['end']=list(bodies[actor][0]);t['endL']=len(bodies[actor]);t['died']=False
        else:t['end']=None;t['endL']=0;t['died']=True
        t['adj_pass']=bool(t['adj_pearls'] and not any(tuple(e) in [tuple(x) for x in t['adj_pearls']] for e in t['eats']))
        if t.get('foe_queen') is not None and t['end'] is not None:t['foe_queen_gap_end']=gap(tuple(t['end']),tuple(t['foe_queen']))
        if t.get('mate') is not None and t['end'] is not None:t['mate_gap_end']=gap(tuple(t['end']),tuple(t['mate']))
        turns.append(t);t=None
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:finish();rnd=p.i32(0);actor=None
        elif k==1:
            finish();actor=p.i32(0);b=bodies[actor];hd=b[0];L=len(b)
            occ={c for bb in bodies.values() for c in bb};mate=min((bb[0] for z,bb in bodies.items() if side(z)==side(actor) and z!=actor),key=lambda c:gap(hd,c),default=None)
            opts=[]
            for d in range(4):
                z=dest(hd,d)
                if z is not None and z not in occ:opts.append((d,z))
            adjp=[list(z) for d,z in opts if z in present and view(hd,z)]
            t=dict(r=rnd,event=idx,id=actor,s=side(actor),L=L,head=list(hd),q=actor==qs[side(actor)],ownN=sum(side(z)==0 for z in bodies),foeN=sum(side(z)==1 for z in bodies),ownQ=len(bodies.get(qs[0],())),foeQ=len(bodies.get(qs[1],())),top=max(len(bb) for z,bb in bodies.items() if side(z)==side(actor)),opts=[[d,list(z)] for d,z in opts],adj_pearls=adjp,eats=[],nat=0,drop=0,dirs=[],steps=[],logs=[],ram=[],split=False,mate=list(mate) if mate is not None else None,mate_gap=gap(hd,mate) if mate is not None else None,own_square=sum(side(z)==side(actor) and view(hd,bb[0]) for z,bb in bodies.items()),enemy_square=sum(side(z)!=side(actor) and view(hd,bb[0]) for z,bb in bodies.items()),heading=heading.get(actor))
            if side(actor)==0:
                t['foe_queen']=list(bodies[qs[1]][0]) if qs[1] in bodies else None
                t['foe_queen_visible']=qs[1] in bodies and view(hd,bodies[qs[1]][0])
            if side(actor)==0 and actor==qs[0]:
                threats=[]
                for z,bb in bodies.items():
                    if side(z)!=1:continue
                    f=(len(bb)+3)//4
                    d=bfs(bb[0],hd,min(12,f+max(0,len(bb)-2)),occ-{hd,bb[0]})
                    if d<99:threats.append(dict(id=z,L=len(bb),steps=d,free=f,visible=view(hd,bb[0]),head=list(bb[0])))
                t['threats']=threats
                if threats:risk.append(dict(r=rnd,L=L,head=list(hd),threats=threats,ownN=t['ownN'],foeN=t['foeN']))
        elif k==3:
            c=replay.point(p.pointer(0))
            if p.u32(0):present[c]=actor is None
            else:
                natural=present.pop(c)
                if t is not None:t['eats'].append(list(c));t['nat']+=natural;t['drop']+=not natural
        elif k==4:
            a=p.pointer(0)
            if t is not None:
                t['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
                t['action']=a.u16(0) if a else None
                if t['dirs']:heading[actor]=t['dirs'][-1]
        elif k==9:
            i=p.i32(0);hd,tail=replay.point(p.pointer(0)),replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                if t is not None and i==actor:t['steps'].append(list(hd))
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif k==10:
            parent,child=p.i32(0),p.i32(4)
            splits.append(dict(r=rnd,id=parent,child=child,s=side(parent),L=len(bodies[parent]),q=parent==qs[side(parent)],N=sum(side(z)==side(parent) for z in bodies)))
            if t is not None:t['split']=True
            for a,i in enumerate((parent,child)):bodies[i]=deque(replay.point(c) for c in p.pointer(a));teams[i]=p.u16(8)
        elif k==11:
            i,reason=p.i32(0),p.u16(4)
            dd=dict(r=rnd,event=idx,id=i,s=side(i),L=len(bodies[i]),q=i==qs[side(i)],reason=reason,actor=actor,head=list(bodies[i][0]))
            if reason==3 and actor!=i:
                dd['ram_start']=dict(t)
                if side(actor)==0:
                    qhd=bodies[qs[0]][0] if qs[0] in bodies else None
                    dd['target_queen_dist']=bfs(qhd,bodies[i][0],3) if qhd is not None else None
                    dd['guard_visible']=qhd is not None and view(tuple(t['head']),qhd) and view(tuple(t['head']),bodies[i][0])
                t['ram'].append(dict(id=i,L=len(bodies[i]),q=dd['q'],s=side(i)))
            deaths.append(dd);bodies.pop(i)
        elif k==2 and t is not None:t['logs'].append(p.text(0))
    finish()
    return dict(qs=qs,botId=int(root.text(1+own)),turns=turns,splits=splits,deaths=deaths,risk=risk)

rows=[]
for gid,folder in JOBS:
    path=Path(folder)/f'M{gid}.replay';meta=json.loads((Path(folder)/f'game-{gid}.json').read_text())
    base=ledger(path,meta,folder,set());old=oldscan('win2',path,meta);tr=trace(path,meta)
    base.pop('intervals',None)
    snapshots=base['snapshots']
    def score(v):return (v['queen_length'],v['longest'],v['total'])
    permanent=max((r for r,s in snapshots.items() if not (s['us']['alive']>0 and (s['them']['alive']==0 or score(s['us'])>score(s['them'])))),default=-1)+1
    assert all(score(s['us'])>score(s['them']) or s['them']['alive']==0 for r,s in snapshots.items() if r>=permanent)
    row=dict(gid=gid,map=meta['mapName'],side=base['ours'],botId=tr['botId'],permanent_lead=permanent,final=base['final'],last=base['last_round'],how=old['how'],base=base,old=old,trace=tr)
    rows.append(row)
    print(gid,meta['mapName'],'oneID',tr['botId'],base['last_round'],old['how'],'final',base['final'],'lead',permanent)
    print('queen deaths',[(d['round'],d['id'],d['cause'],d['actor'],d['length']) for d in base['deaths'] if d['id'] in base['queens'].values()])
    print('q risks',sorted(tr['risk'],key=lambda x:(min(t['steps'] for t in x['threats']),-x['r']))[:3])
    print('logs',sum(len(t['logs']) for t in tr['turns']))
(HERE/'analysis.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n')
