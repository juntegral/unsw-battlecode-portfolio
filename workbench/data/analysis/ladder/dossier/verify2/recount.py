import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
import json
from pathlib import Path
from collections import Counter, defaultdict
from statistics import mean
OUT = Path('data/analysis/ladder/dossier/verify2')
records = [json.loads(x) for x in Path('data/analysis/ladder/dossier/per-game.jsonl').open()]
games = {r['game']: r for r in records if r['relation'] == 'us' and r['width'] * r['height'] > 1200}

def count(rec):
    path = Path(rec['replay'])
    meta = json.loads((path.parent / ('game-%d.json' % rec['game'])).read_text())
    ours = 0 if meta['teamAId'] == 1119 else 1
    assert meta['team' + 'AB'[ours] + 'Id'] == 1119
    assert rec['our_side'] == 'AB'[ours]
    root = replay.load(path).root()
    bodies, teams = {}, {}
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = [(int(q[3+2*j]), int(q[4+2*j])) for j in range(int(q[2]))]
            teams[i] = int(q[1])
    def side(i): return int(teams[i] != ours)
    def state():
        return [[sum(side(i)==s for i in bodies), sum(len(b) for i,b in bodies.items() if side(i)==s)] for s in (0,1)]
    start, end, counters = {}, {}, Counter()
    rnd, actor = None, None
    collisions = []
    def finish_turn():
        if collisions:
            assert len(collisions)==2 and any(i==actor for i in collisions)
            if len({teams[i] for i in collisions})==2 and 101 <= rnd <= 300:
                counters['meeting',side(actor)] += 1
            collisions.clear()
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0,1,3,9,10,11): continue
        p = ev.pointer(0)
        if k in (0,1): finish_turn()
        if k == 0:
            if rnd is not None: end[rnd] = state()
            rnd, actor = p.i32(0), None
            start[rnd] = state()
        elif k == 1: actor = p.i32(0)
        elif k == 3 and p.u32(0)==0:
            counters['eat',side(actor),rnd] += 1
        elif k == 9:
            i=p.i32(0); hd=replay.point(p.pointer(0)); tl=replay.point(p.pointer(1))
            b=bodies[i]
            if b[0] != hd: b.insert(0,hd)
            while len(b)>1 and b[-1]!=tl: b.pop()
            assert b[-1]==tl
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            counters['split',side(parent),rnd] += 1
            for z,i in enumerate((parent,child)):
                bodies[i] = [replay.point(c) for c in p.pointer(z)]
                teams[i] = p.u16(8)
        elif k == 11:
            i=p.i32(0)
            counters['death',side(i),rnd] += 1
            if p.u16(4)==3: collisions.append(i)
            del bodies[i]
    finish_turn(); end[rnd] = state()
    assert rnd==rec['last_round']
    for s in (0,1):
        st=root.pointer(4).pointer(ours if s==0 else 1-ours)
        assert end[rnd][s]==[st.i32(0),st.i32(8)]
    result=root.pointer(4)
    won=result.u16(4)==1 and result.u16(6)==ours
    draw=result.u16(4)!=1
    assert won==(rec['our_result']=='win') and draw==(rec['our_result']=='draw')
    intervals={}
    for lo,hi in ((101,150),(151,200)):
        observed=[n for n in start if lo<=n<=hi]
        intervals[str(lo)] = {str(s): dict(
            alive_start=mean(start[n][s][0] for n in observed) if observed else None,
            alive_end=mean(end[n][s][0] for n in observed) if observed else None,
            **{name:sum(counters[name,s,n] for n in range(lo,hi+1)) for name in ('eat','split','death')}) for s in (0,1)}
    return dict(game=rec['game'], layout=rec['layout_key'], ours='AB'[ours], won=won, draw=draw,last=rnd,
                intervals=intervals, snaps={str(n):end[n] for n in (100,150,200,300) if n in end},
                meetings=[counters['meeting',s] for s in (0,1)])

out=[]
for n,r in enumerate(sorted(games.values(),key=lambda r:r['game']),1):
    out.append(count(r))
    if n%10==0: print(n,len(games),flush=True)
(OUT/'per-game-recount.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in out))
islands=[r for r in out if r['layout']=='Islands #1']; au=[r for r in out if r['layout']=='Australia #1']
summary={'islands':{},'australia':{},'B':{},'C4':{},'missing150':[r['game'] for r in out if '150' not in r['snaps']], 'draws':[r['game'] for r in out if r['draw']]}
for lo in ('101','151'):
    summary['islands'][lo]={str(s):{k:mean(r['intervals'][lo][str(s)][k] for r in islands if r['intervals'][lo][str(s)][k] is not None) for k in ('split','eat','death','alive_start','alive_end')} for s in (0,1)}
for lay in ['ALL']+sorted({r['layout'] for r in out}):
    rs=[r for r in out if lay=='ALL' or r['layout']==lay]
    summary['B'][lay]=[]
    for full in (True,False):
        sub=[r for r in rs if ((r['intervals']['101']['0']['alive_start'] or 0)>=56)==full]
        summary['B'][lay].append([sum(r['won'] for r in sub),len(sub)])
for n in (100,150,200,300):
    sub=[r for r in au if str(n) in r['snaps']]
    summary['australia'][str(n)]={'n':len(sub),'alive':[mean(r['snaps'][str(n)][s][0] for r in sub) for s in (0,1)],'length':[mean(r['snaps'][str(n)][s][1] for r in sub) for s in (0,1)]}
summary['australia']['meetings']=[mean(r['meetings'][s] for r in au) for s in (0,1)]
for label in ('59+','50-58','<50'):
    sub=[r for r in out if '150' in r['snaps'] and ('59+' if r['snaps']['150'][0][0]>=59 else '50-58' if r['snaps']['150'][0][0]>=50 else '<50')==label]
    summary['C4'][label]=[sum(r['won'] for r in sub),len(sub)]
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
