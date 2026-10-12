import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, hashlib
from collections import Counter,deque
from statistics import mean,median
from datetime import datetime
sys.path[:0]=['data/analysis/ladder/dossier/online','data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/local']
import label_report as lr
import o1_scan
from count_local import Geo
from replay_format import point
OUT=Path('data/codex/astra/worstmaps')
MAPS=['Australia','Tower Defense','Stripes','Around UNSW','Schooltime','Default','Devil']
VERS={'20980':'one5','21033':'one6','21086':'one7'}
CP=[0,10,25,50,100,150,300]

def extra(root,meta):
    lines=[s.split() for s in root.text(0).splitlines() if s.strip()]
    w,h=map(int,lines[0][1:3]); n=w*h; own=int(meta['teamAId']!=1119)
    bodies={}; teams={}; raw=[]; bearing={}
    for q in lines:
        if q[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])));teams[i]=int(int(q[1])!=own)
        elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
        elif q[0]=='TILE' and int(q[4])>0:bearing[int(q[2])*w+int(q[1])]=tuple(map(int,q[3:5]))
    slug=meta['mapName'].lower().replace(' ','_')
    candidates=[Path('maps/online-20260927/devil.map')] if slug=='devil' else [Path('data/local/hunter38/harness/tune_runs/official127')/(slug+'.map')]
    candidates+=list(Path('~/meow-redteam/maps/ladder').glob('ladder_'+slug+'_*.map'))
    g=Geo(w,h,raw)
    for mp in candidates:
        mq=[s.split() for s in mp.read_text().splitlines() if s.strip()]
        mg=Geo(w,h,[tuple(map(int,q[1:4])) for q in mq if q[0]=='EDGE'])
        if g.moves==mg.moves:break
    else:raise AssertionError(('map geometry mismatch',meta['id']))
    bearing={int(q[2])*w+int(q[1]):tuple(map(int,q[3:5])) for q in mq if q[0]=='TILE' and int(q[4])>0}
    sig=hashlib.sha256(json.dumps(g.moves).encode()).hexdigest()[:16]
    emp=json.loads((OUT/'supply.json').read_text()).get(sig) if (OUT/'supply.json').exists() else None
    if emp:
        fast=set(emp['fast'])
        bearing={int(c):(1,1 if int(c) in fast else 10000) for c in emp['births']}
    rates={c:1.0 for c in bearing}

    def bfs(src):
        ds=[n+1]*n;qu=deque(src)
        for c in src:ds[c]=0
        while qu:
            c=qu.popleft()
            for t in g.adj[c]:
                if ds[t]>ds[c]+1:ds[t]=ds[c]+1;qu.append(t)
        return ds
    starts=[[dict(id=i,L=len(b),xy=[b[0]%w,b[0]//w]) for i,b in bodies.items() if teams[i]==s] for s in (0,1)]
    init=[bfs([b[0] for i,b in bodies.items() if teams[i]==s]) for s in (0,1)]
    cross=min(init[0][b[0]] for i,b in bodies.items() if teams[i]==1)
    deg=Counter(sum(k!=1 for k,t in row) for row in g.moves)
    portals=len({p for e,k,p in raw if k==2})
    feat=dict(w=w,h=h,bearing=len(bearing),timers=dict(Counter(f'{a}-{b}' for a,b in bearing.values())),degree=dict(deg),portals=portals,starts=starts,start_distance=cross,map_source=str(mp),fast=sum(hi<=10 for lo,hi in bearing.values()),rate_sum=sum(rates.values()),supply_sig=sig,empirical=bool(emp),gap_summary=emp['gap_summary'] if emp else [],bearing_cells=list(bearing),fast_cells=[c for c,(_,hi) in bearing.items() if hi<=10])
    snaps={};curve={};first_split=[None,None];pearls=[0,0];splits=[0,0];rnd=-1;actor=None
    queen=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    portal_moves=[0,0];low=[0,0];counts=[Counter(),Counter()]
    def snap(spatial=False):
        state=[]
        ds=[bfs([b[0] for i,b in bodies.items() if teams[i]==s]) for s in (0,1)] if spatial else None
        for s in (0,1):
            bb=[b for i,b in bodies.items() if teams[i]==s]
            z=dict(N=len(bb),L=sum(map(len,bb)),Q=len(bodies.get(queen[s],[])),pearls=pearls[s],splits=splits[s])
            if spatial:
                z.update(home=sum(init[s][b[0]]<init[1-s][b[0]] for b in bb),far=sum(init[s][b[0]]>init[1-s][b[0]] for b in bb),neutral=sum(init[s][b[0]]==init[1-s][b[0]] for b in bb),bearing_near=sum(ds[s][c]<ds[1-s][c] for c in bearing),bearing_tie=sum(ds[s][c]==ds[1-s][c] for c in bearing),portal_moves=portal_moves[s],bearing_rate=sum(rates[c] for c in bearing if ds[s][c]<ds[1-s][c]),fast_near=sum(ds[s][c]<ds[1-s][c] for c in bearing if bearing[c][1]<=10))
            state.append(z)
        return state
    def close():
        if rnd>=0:
            curve[rnd]=snap()
            if rnd in CP:snaps[rnd]=snap(True)
    for ev in root.pointer(3):
        k=ev.u16(0)
        if k not in (0,1,3,9,10,11):continue
        p=ev.pointer(0)
        tile=lambda p:point(p)[1]*w+point(p)[0]
        if k==0:close();rnd=p.i32(0);actor=None
        elif k==1:actor=p.i32(0)
        elif k==3:
            if not p.u32(0):pearls[teams[actor]]+=1
        elif k==9:
            i=p.i32(0);hd,tl=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                if any(kind==2 and dest==hd for kind,dest in g.moves[b[0]]):portal_moves[teams[i]]+=1
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
            assert b[-1]==tl
        elif k==10:
            parent,child=p.i32(0),p.i32(4);s=teams[parent];splits[s]+=1
            if first_split[s] is None:first_split[s]=rnd
            for z,i in enumerate((parent,child)):bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=int(p.u16(8)!=own)
        elif k==11:bodies.pop(p.i32(0))
    close()
    final=snap(True)
    for r in CP:
        if r>rnd:snaps[r]=final
    # first sustained 25-round deficit: units at most half, enemy at least four.
    turn=None
    for r in sorted(curve):
        if r>300:break
        rr=range(r,min(r+25,rnd+1))
        if len(rr)>=min(25,rnd-r+1) and all(curve[t][1]['N']>=4 and 2*curve[t][0]['N']<curve[t][1]['N'] for t in rr) and (r+24<=rnd or not curve[rnd][0]['N']):turn=r;break
    return dict(features=feat,spatial=snaps,curve=curve,first_split=first_split,turn=turn)

def main():
    patterns=','.join(['data/online/smoke/one[567]*-old','data/online/live-one1/b*'])
    inv=lr.directory_inventory('worstmaps',patterns)
    inventory=[];rows=[]
    for p,m in inv['jobs']:
        if m['mapName'] not in MAPS:continue
        msg=lr.agg.sb.load_replay(p);root=msg.root();own=int(m['teamAId']!=1119);bid=root.text(1+own)
        if bid not in VERS:continue
        print(m['id'],m['mapName'],VERS[bid],flush=True)
        old=o1_scan.replay.load;o1_scan.replay.load=lambda _:msg
        try:r=o1_scan.scan(VERS[bid],p,m)
        finally:o1_scan.replay.load=old
        r.update(extra(root,m));r['path']=str(p);r['opp_id']=m['team'+'AB'[1-own]+'Id'];r['own_side']='AB'[own]
        rows.append(r);inventory.append(dict(game=m['id'],version=VERS[bid],path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        (OUT/'rows.json').write_text(json.dumps(rows,separators=(',',':')))
    (OUT/'inventory.json').write_text(json.dumps(dict(at=datetime.now().isoformat(),games=inventory,notes=inv['notes'],duplicates=inv['duplicate_ids']),indent=2))
    print('DONE',len(rows),dict(Counter(r['src'] for r in rows)),flush=True)
if __name__=='__main__':main()
