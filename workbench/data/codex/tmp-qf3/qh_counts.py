#!/usr/bin/env python3
"""Queen-company counts on local runs (our queen only), definitions as in dossier/diag-topqueen.md (tq2_depth, tq2_near, tq2_chase).
Usage: python3 qh_counts.py <arm> [game-dir-name ...]   -> writes rows-<arm>.jsonl beside this script (one line per game).
Tiles = torus Manhattan. Steps = path over open edges and portals, bodies ignored. The enemy queen is not an enemy head.
Close chase = consecutive turns of hers that start with an enemy head within 3 steps."""
import sys
sys.dont_write_bytecode = True
import json
from collections import deque
from pathlib import Path

LOCAL = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/local'
sys.path.insert(0, LOCAL)
from replay_format import load, point
from count_local import Geo

HERE = Path(__file__).resolve().parent
RUNS = Path('~/meow-redteam/solo/runs')
BANDS = ((0, 50), (51, 100), (101, 300), (301, 500))


def band(r):
    return 0 if r <= 50 else 1 if r <= 100 else 2 if r <= 300 else 3


def scan(path, our_side):
    root = load(path).root()
    bodies, teams, raw = {}, {}, []
    w = h = 0
    for line in root.text(0).splitlines():
        q = line.split('#', 1)[0].split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = map(int, q[1:3])
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    g = Geo(w, h, raw)
    ours = lambda i: teams[i] == our_side
    queen = min(i for i in bodies if ours(i))
    foe_queen = min(i for i in bodies if not ours(i))
    home = bodies[queen][0]

    def man(a, c):
        dx, dy = abs(a % w - c % w), abs(a // w - c // w)
        return min(dx, w - dx) + min(dy, h - dy)

    def ball(src, depth):
        d, q = {src: 0}, deque([src])
        while q:
            c = q.popleft()
            if d[c] >= depth:
                continue
            for t in g.adj[c]:
                if t not in d:
                    d[t] = d[c] + 1
                    q.append(t)
        return d

    def free_sides(c):
        occ = set()
        for b in bodies.values():
            occ.update(b)
        return sum(1 for kind, t in g.moves[c] if kind != 1 and t not in occ)

    B = [dict(turns=0, own3=0, own5=0, e3=0, rank_n=0, rank=0.0, dq=0, pearls=0, home=0, len=0, hrank_n=0, hrank=0.0, nm=0,
              alone5=0) for _ in BANDS]
    out = dict(w=w, h=h, cells=w * h, queen=queen, home=[home % w, home // w], chases=[], death=None, snaps={},
               mate_near_hits=0)
    rnd, actor = -1, None
    chase = None
    qturn = None
    last_q = None

    def snapshot():
        own = [len(b) for i, b in bodies.items() if ours(i)]
        foe = [len(b) for i, b in bodies.items() if not ours(i)]
        return dict(own=len(own), total=sum(own), foe=len(foe), foe_total=sum(foe), q=len(bodies.get(queen, ())))

    def close_chase():
        nonlocal chase
        if chase is not None:
            out['chases'].append(chase)
            chase = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            if rnd >= 0:
                out['snaps'][rnd] = snapshot()
            rnd, actor = p.i32(0), None
        elif k == 1:
            actor = p.i32(0)
            if actor != queen:
                continue
            hd = bodies[queen][0]
            a = B[band(rnd)]
            a['turns'] += 1
            a['len'] += len(bodies[queen])
            a['home'] += man(hd, home)
            mates = [b[0] for i, b in bodies.items() if ours(i) and i != queen]
            foes = {b[0]: i for i, b in bodies.items() if not ours(i) and i != foe_queen}
            n3 = sum(1 for m in mates if man(hd, m) <= 3)
            n5 = sum(1 for m in mates if man(hd, m) <= 5)
            a['own3'] += n3
            a['own5'] += n5
            a['alone5'] += int(n5 == 0)
            a['nm'] += min([man(hd, m) for m in mates] + [20])
            if rnd % 4 == 0 and mates:
                dh = man(hd, home)
                far = [man(m, home) for m in mates]
                a['hrank_n'] += 1
                a['hrank'] += (sum(1 for d in far if d > dh) + 0.5 * sum(1 for d in far if d == dh)) / len(far)
            near = ball(hd, 3)
            pursuers = sorted(foes[c] for c in near if c in foes)
            qturn = dict(r=rnd, hd=hd, L=len(bodies[queen]), n5=n5, n3=n3, e3=len(pursuers), free=free_sides(hd))
            last_q = qturn
            if pursuers:
                a['e3'] += 1
                if chase is None:
                    chase = dict(r0=rnd, turns=0, n5=n5, n3=n3, pursuers=[], mate_ram=0, end='lost', at=[hd % w, hd // w])
                chase['turns'] += 1
                chase['r1'] = rnd
                for j in pursuers:
                    if j not in chase['pursuers']:
                        chase['pursuers'].append(j)
            else:
                close_chase()
            if rnd % 4 == 0:
                en = [b[0] for i, b in bodies.items() if not ours(i)]
                if en and mates:
                    dq = min(man(hd, e) for e in en)
                    ds = [min(man(m, e) for e in en) for m in mates]
                    a['rank_n'] += 1
                    a['rank'] += (sum(1 for d in ds if d < dq) + 0.5 * sum(1 for d in ds if d == dq)) / len(ds)
                    a['dq'] += dq
        elif k == 3:
            if not p.bit(0) and actor == queen:
                B[band(rnd)]['pearls'] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = point(p.pointer(0)), point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(c[1] * w + c[0] for c in map(point, p.pointer(z)))
                teams[i] = p.u16(8)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if chase is not None and reason == 3 and i in chase['pursuers'] and actor is not None:
                other_is_mate = ours(actor) and actor != queen if i != actor else False
                if other_is_mate:
                    chase['mate_ram'] += 1
            if i == queen:
                lq = last_q or {}
                if reason == 3 and actor != queen:
                    how = 'rammed'
                elif reason == 3:
                    how = 'into_head'
                elif lq.get('e3', 0) > 0:
                    how = 'boxed'
                else:
                    how = 'dead_end'
                out['death'] = dict(r=rnd, reason=reason, how=how, actor=actor, L=len(bodies[queen]),
                                    at=[bodies[queen][0] % w, bodies[queen][0] // w], n5=lq.get('n5'), n3=lq.get('n3'),
                                    e3=lq.get('e3'), free=lq.get('free'), in_chase=chase is not None,
                                    chase_turns=chase['turns'] if chase else 0)
                if chase is not None:
                    chase['end'] = how
                close_chase()
            bodies.pop(i)
    close_chase()
    out['snaps'][rnd] = snapshot()
    out['rounds'] = rnd
    out['bands'] = B
    result = root.pointer(4)
    out['finished'] = bool(result.bit(0))
    return out


def main():
    arm = sys.argv[1]
    names = sys.argv[2:] or sorted(d.name for d in (RUNS / arm).iterdir() if (d / 'game.replay').exists())
    dest = HERE / ('rows-' + arm + '.jsonl')
    have = {}
    if dest.exists():
        for line in dest.read_text().splitlines():
            r = json.loads(line)
            have[r['game']] = line
    for name in names:
        if name in have:
            continue
        rp = RUNS / arm / name / 'game.replay'
        if not rp.exists() or not (RUNS / arm / name / 'result.txt').exists():
            continue
        side = int(name.rsplit('side', 1)[1])
        try:
            row = scan(rp, side)
        except Exception as e:
            sys.stderr.write('bad %s %r\n' % (name, e))
            continue
        row['game'] = name
        row['arm'] = arm
        row['result'] = (RUNS / arm / name / 'result.txt').read_text().strip()
        have[name] = json.dumps(row, separators=(',', ':'))
        sys.stderr.write('%s ok\n' % name)
    dest.write_text(''.join(have[n] + '\n' for n in sorted(have)))


main()
