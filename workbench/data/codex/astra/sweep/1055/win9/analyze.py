import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/local'),
               str(ROOT/'data/analysis/ladder/dossier/work')]
import scoreboard
import ladder_replay as lr
import o1_scan
from count_local import Geo

JOBS = [(i, 'data/online/live-one1/b1508580') for i in range(1508581,1508585)]
JOBS += [(1512823, 'data/online/live-one1/b1512823')]
JOBS += [(i, 'data/online/smoke/one14-c1-old') for i in
         (1517685,1517688,1517691,1517692,1517695,1517696,1517699)]

def detail(root, meta):
    w,h = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies,teams,raw = {},{},[]
    for line in root.text(0).splitlines():
        q=line.split()
        if q[0]=='DRAGON':
            i=len(bodies);teams[i]=int(q[1])
            bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
    own=int(meta['teamAId']!=1119)
    side=lambda i: int(teams[i]!=own)
    queens=[min(i for i in bodies if side(i)==s) for s in (0,1)]
    g=Geo(w,h,raw)
    coord=lambda c:[c%w,c//w]
    tile=lambda p: lr.replay.point(p)[1]*w+lr.replay.point(p)[0]
    def man(a,b):
        dx,dy=abs(a%w-b%w),abs(a//w-b//w)
        return min(dx,w-dx)+min(dy,h-dy)
    distances={}
    def reach(c):
        if c not in distances:
            seen={c:0};q=deque([c])
            while q:
                a=q.popleft()
                if seen[a]>=3:continue
                for n in g.adj[a]:
                    if n not in seen:seen[n]=seen[a]+1;q.append(n)
            distances[c]=seen
        return distances[c]
    def state():
        return [dict(n=sum(side(i)==s for i in bodies),
                     total=sum(len(b) for i,b in bodies.items() if side(i)==s),
                     longest=max((len(b) for i,b in bodies.items() if side(i)==s),default=0),
                     queen=len(bodies.get(queens[s],()))) for s in (0,1)]
    snaps={};turns=[];qturns=[];rams=[];sonars=[];cur=None
    rnd=-1;actor=None;present=set();seen_by_own=set();steps=0;dirs=[]
    def finish():
        nonlocal cur
        if cur is None:return
        cur['end']=coord(bodies[cur['id']][0]) if cur['id'] in bodies else None
        cur['L1']=len(bodies.get(cur['id'],()))
        cur['steps']=steps;cur['dirs']=dirs
        if cur['side']==0:turns.append(cur)
        if cur['id']==queens[0]:qturns.append(cur)
        cur=None
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            finish()
            if rnd>=0:snaps[rnd]=state()
            rnd=p.i32(0);actor=None
        elif k==1:
            finish();actor=p.i32(0);steps=0;dirs=[]
            b=bodies[actor];occ={c for bb in bodies.values() for c in bb}
            open_cells=[c for c in g.adj[b[0]] if c not in occ or c==b[-1]]
            visible=g.window(b[0]);foes=[i for i,bb in bodies.items() if side(i)!=side(actor)]
            cur=dict(round=rnd,event=idx,id=actor,side=side(actor),L0=len(b),start=coord(b[0]),
                     pearls=0,split=False,open=[coord(c) for c in open_cells],
                     adjacent_pearls=[coord(c) for c in open_cells if c in present],
                     enemies=[dict(id=i,L=len(bodies[i]),head=coord(bodies[i][0]),
                                   visible=bodies[i][0] in visible,
                                   d3=reach(b[0]).get(bodies[i][0],99),man=man(b[0],bodies[i][0]))
                              for i in foes if man(b[0],bodies[i][0])<=8 or bodies[i][0] in reach(b[0])],
                     portals=[],n=sum(side(i)==side(actor) for i in bodies))
            if side(actor)==0:seen_by_own.update(visible)
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0):present.add(c)
            else:
                present.remove(c)
                if cur:cur['pearls']+=1
        elif k==4:
            a=p.pointer(0)
            dirs=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==9:
            i=p.i32(0);hd,tl=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                if i==actor:
                    if steps<len(dirs):
                        ek,dest=g.moves[b[0]][dirs[steps]]
                        assert ek!=1 and dest==hd
                        if ek==2:cur['portals'].append(dict(step=steps+1,start=coord(b[0]),
                            end=coord(hd),exit_previously_seen=hd in seen_by_own))
                    steps+=1
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
            assert b[-1]==tl
        elif k==10:
            if cur:cur['split']=True
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
        elif k==11:
            i=p.i32(0)
            if p.u16(4)==3 and i!=actor:
                rams.append(dict(round=rnd,actor=actor,target=i,side=side(actor),
                    L0=cur['L0'],victim_length=len(bodies[i]),target_queen=i in queens,
                    queen_distance=reach(bodies[queens[0]][0]).get(bodies[i][0],99) if queens[0] in bodies else None,
                    steps=steps+1))
            bodies.pop(i)
        elif k==12:
            sonars.append(dict(round=rnd,event=idx,dwords=p.dwords,pwords=p.pwords,
                               words=[p.u64(8*j) for j in range(p.dwords)]))
    finish();snaps[rnd]=state();final=state()
    for s in (0,1):
        st=root.pointer(4).pointer(own if s==0 else 1-own)
        assert (final[s]['n'],final[s]['longest'],final[s]['total'],final[s]['queen'])==tuple(st.i32(4*j) for j in range(4))
    def key(st):return (int(st['n']>0),st['queen'],st['longest'],st['total'])
    behind=[r for r,s in snaps.items() if key(s[0])<=key(s[1])]
    permanent=max(behind)+1 if behind else min(snaps)
    assert key(final[0])>key(final[1])
    peak=0;half=None
    for r,s in snaps.items():
        peak=max(peak,s[0]['n'])
        if half is None and peak>=4 and s[0]['n']*2<=peak:half=dict(round=r,peak=peak,n=s[0]['n'])
    return dict(queens=queens,final=final,snapshots=snaps,ahead_permanent=permanent,
                halved=half,turns=turns,queen_turns=qturns,rams=rams,sonars=sonars)

def main():
    summary=[]
    for gid,folder in JOBS:
        folder=Path(folder);path=folder/f'M{gid}.replay'
        meta=json.loads((folder/f'game-{gid}.json').read_text())
        message=scoreboard.load_replay(path);root=message.root()
        lr.replay.load=lambda path:message
        base=o1_scan.scan('win9',path,meta);extra=detail(root,meta)
        assert base['result']=='win' and int(base['bot']) in (21377,21497)
        qd=[d for d in base['deaths'] if d[6]]
        near=[(e['d3'],t['round'],e['id'],t['L0'],e['L']) for t in extra['queen_turns'] for e in t['enemies']]
        row=dict(gid=gid,map=meta['mapName'],bot=base['bot'],how=base['how'],last=base['last'],
                 queens=extra['queens'],final=extra['final'],ahead=extra['ahead_permanent'],
                 queen_deaths=qd,halved=extra['halved'],queen_nearest=min(near) if near else None,
                 q_eats=sum(t['pearls'] for t in extra['queen_turns']),
                 q_short=sum(t['L0']==2 for t in extra['queen_turns']),
                 r100=extra['snapshots'].get(100),q_splits=sum(t['split'] for t in extra['queen_turns']))
        summary.append(row)
        (OUT/f'{gid}.json').write_text(json.dumps(dict(base=base,extra=extra),separators=(',',':')))
        print(json.dumps(row,ensure_ascii=False),flush=True)
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
