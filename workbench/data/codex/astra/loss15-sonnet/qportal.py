"""loss15-sonnet: our queen's portal steps in r0-99. Usage (via run2.sh): qportal.py <gameid> [...]
A portal step = a head move between cells whose torus manhattan gap != 1. Prints rounds of the queen's portal steps, her death, r100 dragons / total, natural pearls eaten r<100."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
sys.path.insert(0, 'data/codex/astra/qexit-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque
from pathlib import Path
import qdeath


def gap(W, H, a, b):
    ax, ay, bx, by = a % W, a // W, b % W, b // W
    dx, dy = abs(ax - bx), abs(ay - by)
    return min(dx, W - dx) + min(dy, H - dy)


for gid in map(int, sys.argv[1:]):
    mp = [Path(f) for f in glob.glob('data/online/live-one1/b*/game-%d.json' % gid) + glob.glob('data/online/smoke/*-old/game-%d.json' % gid)][0]
    j = json.load(open(mp))
    rp = mp.parent / ('M%d.replay' % gid)
    ours = 0 if j['teamAId'] == 1119 else 1
    root = replay.load(rp).root()
    G = geometry(root.text(0))
    W, H = G['W'], G['H']
    bodies = {i: deque(b) for i, b in G['bodies'].items()}
    teams = dict(G['teams'])
    Q = min(i for i in teams if teams[i] == ours)
    rnd, actor = -1, None
    qp, allp = [], 0
    pearls_nat = 0
    snap = None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            if rnd == 99:
                snap = (sum(1 for i in bodies if teams[i] == ours), sum(len(b) for i, b in bodies.items() if teams[i] == ours),
                        sum(1 for i in bodies if teams[i] != ours), sum(len(b) for i, b in bodies.items() if teams[i] != ours))
            rnd = p.i32(0)
            actor = None
        elif k == 1:
            actor = p.i32(0)
        elif k == 3:
            if not p.u32(0) and actor in teams and teams[actor] == ours and rnd < 100:
                pearls_nat += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
            b = bodies[i]
            if b[0] != hd:
                if gap(W, H, b[0], hd) != 1 and rnd < 100 and teams[i] == ours:
                    allp += 1
                    if i == Q:
                        qp.append(rnd)
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
        elif k == 11:
            bodies.pop(p.i32(0))
    print('game %d %s bot %s %s vs %s: queen portal steps r<100 at rounds %s (n=%d); all our dragons portal steps r<100 = %d; r100 us %s dragons / %s total, them %s / %s; eat events (all pearls, incl. dropped) by us r<100 = %d' % (
        gid, j['mapName'], root.text(1 if ours == 0 else 2).strip(), 'WIN' if j['winner'] == 'ab'[ours] else 'LOSS',
        j['teamBName'] if ours == 0 else j['teamAName'], qp, len(qp), allp, *(snap or ('-',) * 4), pearls_nat))
    q = qdeath.scan(rp, ours)
    for d in q['deaths']:
        keys = ['r', 'L', 'reason', 'own_turn', 'their_q_dead', 'att', 'att_free', 'att_paid', 'seen_q', 'seen_mate', 'f0', 'f0a', 'f1', 'f1a', 'split0']
        print('   QUEEN DEAD', {k: d[k] for k in keys if k in d})
    print('   queen alive at end %s len %s' % (q['qalive'], q['qlen']))
