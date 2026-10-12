"""Scratch (diag-longest): replay viewer. python3 lg_view.py <label> <game> <r0> <r1> [side]
Round by round: the side's longest dragon (side 0 = ours), enemy heads within 8, own heads within 6, and every death,
split and pearl eaten within 8 tiles of it."""
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path


def main():
    label, gid, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    fs = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    folder = Path('data/online/smoke') / (label + '-new')
    meta = json.loads((folder / ('game-%d.json' % gid)).read_text())
    own = 'A' if meta['teamAId'] == 1119 else 'B'
    root = replay.load(folder / ('M%d.replay' % gid)).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    bodies, teams = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 0 if 'AB'[int(q[1])] == own else 1
    tile = lambda z: replay.point(z)[1] * w + replay.point(z)[0]
    xy = lambda c: '(%d,%d)' % (c % w, c // w)

    def man(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return min(dx, w - dx) + min(dy, h - dy)

    def cheb(a, b):
        dx = abs(a % w - b % w)
        dy = abs(a // w - b // w)
        return max(min(dx, w - dx), min(dy, h - dy))

    def focus():
        best = -1
        for i, b in bodies.items():
            if teams[i] == fs and (best < 0 or len(b) > len(bodies[best])):
                best = i
        return best

    print(gid, meta['mapName'], w, h, 'ours is', own, 'focus side', fs)
    rnd, actor, used, slen, shead = 0, None, 0, 0, 0
    act = 2
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        show = r0 <= rnd <= r1
        if k == 0:
            rnd, actor = p.i32(0), None
            if r0 <= rnd <= r1:
                f = focus()
                if f >= 0:
                    fh = bodies[f][0]
                    en = sorted((man(fh, b[0]), i, len(b), cheb(fh, b[0])) for i, b in bodies.items() if teams[i] != fs and man(fh, b[0]) <= 8)
                    ow = sorted((man(fh, b[0]), i, len(b)) for i, b in bodies.items() if teams[i] == fs and i != f and man(fh, b[0]) <= 6)
                    ls = sorted((len(b) for i, b in bodies.items() if teams[i] == fs), reverse=True)[:4]
                    lt = sorted((len(b) for i, b in bodies.items() if teams[i] != fs), reverse=True)[:3]
                    print('r%d n %d:%d top4 %s theirs %s | #%d L%d at %s | enemy<=8: %s | own<=6: %s' % (
                        rnd, sum(teams[i] == fs for i in bodies), sum(teams[i] != fs for i in bodies), ls, lt, f, len(bodies[f]), xy(fh),
                        ' '.join('d%d:#%d(L%d%s)' % (e[0], e[1], e[2], '' if e[3] <= 3 else ',unseen') for e in en) or '-',
                        ' '.join('d%d:#%d(L%d)' % o for o in ow) or '-'))
        elif k == 1:
            actor = p.i32(0)
            used, slen, shead = 0, len(bodies[actor]), bodies[actor][0]
            act = 2
        elif k == 4:
            a = p.pointer(0)
            act = min(a.u16(0), 2) if a else 2
        elif k == 3:
            c = tile(p.pointer(0))
            if show and not p.u32(0) and actor is not None and actor in bodies:
                f = focus()
                if f >= 0 and (actor == f or man(bodies[f][0], c) <= 4):
                    print('      eat r%d #%d s%d L%d at %s' % (rnd, actor, teams[actor], len(bodies[actor]), xy(c)))
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(p.pointer(0)), tile(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor:
                    used += 1
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(pt) for pt in p.pointer(z))
            teams[child] = teams[parent]
            if show and slen >= 6:
                print('      split r%d #%d s%d L%d > %d + child #%d L%d' % (rnd, parent, teams[parent], slen, len(bodies[parent]), child, len(bodies[child])))
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            if show:
                f = focus()
                if f >= 0 and (i == f or man(bodies[f][0], b[0]) <= 8 or len(b) >= 8):
                    print('      death r%d #%d s%d L%d %s at %s%s' % (
                        rnd, i, teams[i], len(b), ('wall', 'own body', 'body', 'head-on', 'no action')[min(reason, 4)], xy(b[0]),
                        ' <- mover #%d s%d L%d from %s, %d steps' % (actor, teams[actor], slen, xy(shead), used + 1) if actor != i and actor is not None else ' (own move, order %d)' % act))
            bodies.pop(i)


main()
