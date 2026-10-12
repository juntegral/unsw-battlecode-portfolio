"""shed-sonnet scan: per game, our queen's sheds (split leaving her at 2 from >=4) and per-round queen state. Writes data.json.
Usage (from ROOT): python3 data/codex/astra/shed-sonnet/scan.py"""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque
from pathlib import Path

VER = {}
for line in open('data/online/smoke/versions.tsv'):
    a, b = line.split()
    VER[a] = b
VERS = {k: v for k, v in VER.items() if v in ('one11', 'one12', 'one13', 'one14', 'one15', 'one16')}


def gap(W, H, a, b):
    ax, ay, bx, by = a % W, a // W, b % W, b // W
    dx, dy = abs(ax - bx), abs(ay - by)
    return min(dx, W - dx) + min(dy, H - dy)


def run(mp, j):
    rp = mp.parent / ('M%d.replay' % j['id'])
    ours = 0 if j['teamAId'] == 1119 else 1
    root = replay.load(rp).root()
    bot = root.text(1 if ours == 0 else 2).strip()
    if bot not in VERS:
        return None
    G = geometry(root.text(0))
    W, H = G['W'], G['H']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    Q = min(i for i in teams if teams[i] == ours)
    EQ = min(i for i in teams if teams[i] != ours)
    rnd = -1
    turns = []
    sheds = []
    qdead = None
    eqdead = None
    cur = None

    def snap():
        if Q not in bodies:
            return None
        h = bodies[Q][0]
        foes = sorted((gap(W, H, h, b[0]), len(b), i) for i, b in bodies.items() if teams[i] != ours)
        eqlen = len(bodies[EQ]) if EQ in bodies else 0
        near = foes[0] if foes else (99, 0, -1)
        return dict(r=rnd, ql=len(bodies[Q]), nd=near[0], nl=near[1], n3=sum(1 for f in foes if f[0] <= 3),
                    n6=sum(1 for f in foes if f[0] <= 6), eq=eqlen, split=False,
                    foes6=[(f[0], f[1]) for f in foes if f[0] <= 6][:5])

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            cur = snap()
            if cur:
                turns.append(cur)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            par, ch = p.i32(0), p.i32(4)
            qinv = Q in (par, ch)
            before = len(bodies[Q]) if qinv else 0
            for z, i in enumerate((par, ch)):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
            if qinv:
                if cur:
                    cur['split'] = True
                after = len(bodies[Q])
                child = ch if Q == par else par
                if before >= 4 and after == 2:
                    s = dict(cur) if cur else {}
                    s.update(r=rnd, before=before, child_len=len(bodies[child]), child=child)
                    sheds.append(s)
        elif k == 11:
            i = p.i32(0)
            if i == Q:
                qdead = rnd
            if i == EQ:
                eqdead = rnd
            bodies.pop(i)
    fin = len(bodies[Q]) if Q in bodies else 0
    efin = len(bodies[EQ]) if EQ in bodies else 0
    for s in sheds:
        c = s['child']
        s['child_final'] = len(bodies[c]) if c in bodies else 0
    win = j['winner'] == 'ab'[ours]
    return dict(id=j['id'], ver=VERS[bot], win=win, winner=j['winner'], ours=ours, qdead=qdead, qfin=fin, eqdead=eqdead, eqfin=efin,
                map=j.get('mapName'), turns=turns, sheds=sheds, last=rnd, ranked=bool(j.get('ranked')))


files = sorted(glob.glob('data/online/live-one1/b*/game-*.json')) + sorted(glob.glob('data/online/smoke/one1[1-6]-*-old/game-*.json'))
seen = set()
games = []
skipped = {'team': 0, 'time': 0, 'ver': 0, 'dup': 0, 'err': 0}
for f in files:
    j = json.load(open(f))
    if 1119 not in (j['teamAId'], j['teamBId']) or j.get('status') != 'completed':
        skipped['team'] += 1
        continue
    if '/live-one1/' in f and (j.get('completedAt') or '') < '2026-10-08T21:00':
        skipped['time'] += 1
        continue
    if j['id'] in seen:
        skipped['dup'] += 1
        continue
    seen.add(j['id'])
    try:
        r = run(Path(f), j)
    except Exception as ex:
        print('ERR', j['id'], repr(ex)[:120])
        skipped['err'] += 1
        continue
    if r is None:
        skipped['ver'] += 1
        continue
    r['src'] = f
    games.append(r)
json.dump(dict(games=games, skipped=skipped), open('data/codex/astra/shed-sonnet/data.json', 'w'))
print(len(games), skipped, 'sheds', sum(len(g['sheds']) for g in games))
