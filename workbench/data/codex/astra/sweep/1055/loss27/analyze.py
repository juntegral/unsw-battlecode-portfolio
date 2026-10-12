import sys, json, subprocess, runpy, contextlib
from pathlib import Path
from collections import deque
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_scan import scan, replay
sys.path.insert(0, 'data/analysis/ladder/dossier/local')
import scoreboard
replay.load = lambda p: scoreboard.load_replay(Path(p))

OUT = Path(__file__).resolve().parent
JOBS = [(1508962, 'data/online/live-one1/b1508960'),
        (1508963, 'data/online/live-one1/b1508960'),
        (1507913, 'data/online/smoke/one13-p1-old')]

for gid, folder in JOBS:
    folder = Path(folder)
    path = folder / f'M{gid}.replay'
    meta = json.loads((folder / f'game-{gid}.json').read_text())
    cached = OUT/f'{gid}.json'
    base = json.loads(cached.read_text())['ledger'] if cached.exists() else scan('loss27', path, meta)
    root = replay.load(path).root()
    W, H = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies, teams = {}, {}
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3+2*k]), int(q[4+2*k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    own = int(meta['teamAId'] != 1119)
    qs = [min(i for i in bodies if (teams[i] == own) == (s == 0)) for s in (0, 1)]
    def side(i): return int(teams[i] != own)
    def snapshot():
        return [dict(n=sum(side(i)==s for i in bodies), q=len(bodies.get(qs[s], [])),
                     longest=max((len(b) for i,b in bodies.items() if side(i)==s), default=0),
                     total=sum(len(b) for i,b in bodies.items() if side(i)==s),
                     leaders=sorted([(len(b),i,list(b[0])) for i,b in bodies.items() if side(i)==s], reverse=True)[:3]) for s in (0,1)]
    def key(s): return (bool(s['n']), s['q'], s['longest'], s['total'])
    def visible(a,b): return min(abs(a[0]-b[0]),W-abs(a[0]-b[0])) <= 3 and min(abs(a[1]-b[1]),H-abs(a[1]-b[1])) <= 3
    turns, deaths, splits, rounds = [], [], [], {}
    rnd, actor, turn = -1, None, None
    for ev in root.pointer(3):
        k,p = ev.u16(0),ev.pointer(0)
        if k == 0:
            if rnd >= 0: rounds[rnd] = snapshot()
            rnd,actor = p.i32(0),None
        elif k == 1:
            actor = p.i32(0)
            b = bodies[actor]
            turn = dict(r=rnd, id=actor, side=side(actor), L=len(b), head=list(b[0]), path=[], eats=0, action=None)
            if actor in qs:
                turn['near'] = [(i,len(bb),list(bb[0]),sum(visible(c,b[0]) for c in bb)) for i,bb in bodies.items() if i!=actor and visible(bb[0],b[0])]
            turns.append(turn)
        elif k == 3 and not p.u32(0): turn['eats'] += 1
        elif k == 4:
            a = p.pointer(0)
            if a is not None:
                turn['action'] = ''.join('NESW'[d] for d in a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else 'split' if a.u16(0)==1 else 'none'
        elif k == 9:
            i = p.i32(0)
            hd,tl = replay.point(p.pointer(0)),replay.point(p.pointer(1))
            b = bodies[i]
            if hd != b[0]:
                b.appendleft(hd)
                if i==actor: turn['path'].append(list(hd))
            while len(b)>1 and b[-1]!=tl: b.pop()
            assert b[-1]==tl
            if i==actor: turn['endL']=len(b)
        elif k == 10:
            par,child = p.i32(0),p.i32(4)
            oldL = len(bodies[par])
            for z,i in enumerate((par,child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            splits.append(dict(r=rnd, id=par, child=child, before=oldL, keep=len(bodies[par]), childL=len(bodies[child])))
        elif k == 11:
            i = p.i32(0)
            deaths.append(dict(r=rnd, id=i, side=side(i), L=len(bodies[i]), head=list(bodies[i][0]), reason=p.u16(4), attacker=actor, turn=turn.copy(), state=snapshot()))
            bodies.pop(i)
    rounds[rnd] = snapshot()
    for s in (0,1):
        assert [rounds[rnd][s][x] for x in ('n','total','longest','q')] == base['ends'][s][:4]
    behind = None
    for r,st in reversed(list(rounds.items())):
        if key(st[0]) < key(st[1]): behind=r
        else: break
    record=dict(gid=gid, map=meta['mapName'], own='AB'[own], queens=qs, bot=base['bot'], behind=behind,
                final=rounds[rnd], how=base['how'], rounds=rounds, turns=turns, deaths=deaths, splits=splits, ledger=base)
    (OUT/f'{gid}.json').write_text(json.dumps(record))
    print(gid, meta['mapName'], 'side', 'AB'[own], 'queens',qs,'bot',base['bot'],'how',base['how'],'behind',behind,'final',rounds[rnd])
    for d in deaths:
        if d['id'] in qs: print('QDEATH', json.dumps(d))
    for s in splits:
        if s['id']==qs[0]: print('QSPLIT',s)
    qturns=[t for t in turns if t['id']==qs[0]][-3:]
    print('LAST TURNS',qturns)
    if qturns:
        sys.argv=['o1_look.py',str(path),str(gid),str(qs[0]),str(qturns[0]['r']),str(qturns[-1]['r'])]
        with (OUT/f'{gid}-boards.txt').open('w') as out, contextlib.redirect_stdout(out):
            runpy.run_path('data/analysis/ladder/dossier/work/o1_look.py',run_name='__main__')
