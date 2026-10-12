"""Scratch (diag-australia): read one replay around its head-on meetings.
Usage: python3 .../au_look.py <replay> <our side A|B> <from round> <to round> [max events]
Prints each cross-team head-on with the last turns of both dragons, and a small picture."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


class Geo:
    def __init__(self, w, h, raw):
        self.w, self.h = w, h
        self.edges = canonical_edges(w, h, raw)
        portals = defaultdict(list)
        for e, kp in self.edges.items():
            if kp[0] == 2:
                portals[kp[1]].append(e)
        self.moves = []
        for y in range(h):
            for x in range(w):
                row = []
                for d in range(4):
                    dx, dy = STEP[d]
                    e = edge_id(w, h, x, y, d)
                    kind, pid = self.edges.get(e, (0, -1))
                    if kind == 2:
                        partner = [z for z in portals[pid] if z != e][0]
                        ry, px = divmod(partner, w + 1)
                        dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                    else:
                        dest = ((y + dy) % h) * w + (x + dx) % w
                    row.append((kind, dest))
                self.moves.append(row)


def main():
    path, ours, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    cap = int(sys.argv[5]) if len(sys.argv) > 5 else 8
    root = replay.load(Path(path)).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    xy = lambda c: '(%d,%d)' % (c % w, c // w)
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    g = Geo(w, h, raw)
    side = lambda i: 'us' if teams[i] == ours else 'them'
    present = set()
    hist = defaultdict(lambda: deque(maxlen=4))
    rnd, actor = 0, None
    dirs, used = [], 0
    turn_deaths = []
    shown = 0
    start_head = None
    start_pic = None

    def picture(centre, mark):
        cx, cy = centre % w, centre // w
        occ = {}
        for i, b in bodies.items():
            for n, c in enumerate(b):
                ch = ('U' if n == 0 else 'u') if side(i) == 'us' else ('T' if n == 0 else 't')
                occ[c] = ch
        rows = []
        for dy in range(-5, 6):
            row = ''
            for dx in range(-7, 8):
                c = ((cy + dy) % h) * w + (cx + dx) % w
                ch = occ.get(c, 'o' if c in present else '.')
                if c in mark:
                    ch = mark[c]
                row += ch + ('|' if g.moves[c][1][0] == 1 else ' ')
            rows.append(row)
        return rows

    def finish():
        nonlocal shown
        hs = [d for d in turn_deaths if d['reason'] == 3]
        if len(hs) == 2 and lo <= rnd <= hi and shown < cap:
            m = hs[0] if hs[0]['id'] == actor else hs[1]
            v = hs[1] if hs[0]['id'] == actor else hs[0]
            if m['side'] != v['side']:
                shown += 1
                print('--- r%d: %s dragon %d (len %d) rams %s dragon %d (len %d) at %s; mover asked %d steps, hit on step %d, free steps %d'
                      % (rnd, m['side'], m['id'], m['len'], v['side'], v['id'], v['len'], xy(v['head']), len(dirs), used + 1, (m['len'] + 3) // 4))
                print('    mover last turns  :', ' ; '.join('r%d %s->%s len%d ate%d' % t for t in m['hist']))
                print('    victim last turns :', ' ; '.join('r%d %s->%s len%d ate%d' % t for t in v['hist']))
                for row in start_pic or ():
                    print('      ' + row)
        turn_deaths.clear()

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1):
            finish()
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > hi:
                break
        elif k == 1:
            actor = p.i32(0)
            dirs, used = [], 0
            start_head = bodies[actor][0]
            hist[actor].append([rnd, xy(start_head), xy(start_head), len(bodies[actor]), 0])
            start_pic = picture(start_head, {}) if lo <= rnd <= hi and shown < cap else None
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
        elif k == 3:
            c = tile(replay.point(p.pointer(0)))
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
                if actor in hist and hist[actor]:
                    hist[actor][-1][4] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            moved = b[0] != hd
            if moved:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
            if moved and i == actor:
                used += 1
                hist[i][-1][2] = xy(hd)
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            turn_deaths.append(dict(id=i, side=side(i), reason=reason, len=len(bodies[i]), head=bodies[i][0],
                                    hist=[tuple(t) for t in hist[i]]))
            bodies.pop(i)
    finish()


main()
