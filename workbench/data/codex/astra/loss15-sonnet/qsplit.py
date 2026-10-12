"""loss15-sonnet: queen splits that cut her length. Usage (via run2.sh): qsplit.py <minL> <ids...>   (ids from list15.py; 'all' = every one15 game)
Per game: every queen split with length before >= minL, her length after, foes (enemy heads) within 6 at that moment, and what happened to her later (death round or final length), plus the game result."""
import sys, json, glob, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque
from pathlib import Path

minL = int(sys.argv[1])
want = sys.argv[2:]


def gap(W, H, a, b):
    ax, ay, bx, by = a % W, a // W, b % W, b // W
    dx, dy = abs(ax - bx), abs(ay - by)
    return min(dx, W - dx) + min(dy, H - dy)


def run(mp):
    j = json.load(open(mp))
    rp = mp.parent / ('M%d.replay' % j['id'])
    ours = 0 if j['teamAId'] == 1119 else 1
    root = replay.load(rp).root()
    if root.text(1 if ours == 0 else 2).strip() != '21651':
        return None
    G = geometry(root.text(0))
    W, H = G['W'], G['H']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    Q = min(i for i in teams if teams[i] == ours)
    rnd = -1
    out, dead = [], None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
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
            before = len(bodies[Q]) if Q in (par, ch) else 0
            for z, i in enumerate((par, ch)):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
            if before >= minL:
                h = bodies[Q][0]
                foes = sorted((gap(W, H, h, b[0]), len(b)) for i, b in bodies.items() if teams[i] != ours and gap(W, H, h, b[0]) <= 6)
                out.append([rnd, before, len(bodies[Q]), foes[:4]])
        elif k == 11:
            i = p.i32(0)
            if i == Q:
                dead = rnd
            bodies.pop(i)
    fin = len(bodies[Q]) if Q in bodies else 0
    qs = {t: (min(i for i in teams if teams[i] == t)) for t in (0, 1)}
    return j, ours, out, dead, fin


rows = []
for f in sorted(glob.glob('data/online/live-one1/b*/game-*.json') + glob.glob('data/online/smoke/one16-*-old/game-*.json')):
    j = json.load(open(f))
    if 1119 not in (j['teamAId'], j['teamBId']) or (j.get('completedAt') or '') < '2026-10-09T03:50':
        continue
    if want != ['all'] and str(j['id']) not in want:
        continue
    if j['id'] in globals().setdefault('_seen', set()):
        continue
    _seen.add(j['id'])
    mp = Path(f)
    try:
        r = run(mp)
    except Exception as ex:
        print('ERR', j['id'], repr(ex)[:100])
        continue
    if r is None:
        continue
    j, ours, out, dead, fin = r
    win = j['winner'] == 'ab'[ours]
    print('%d %-4s %-15s %-22s Qdead=%s Qfinal=%d  cuts(L>=%d)=%s' % (j['id'], 'WIN' if win else 'LOSS', j['mapName'], (j['teamBName'] if ours == 0 else j['teamAName'])[:22], dead, fin, minL, out))
