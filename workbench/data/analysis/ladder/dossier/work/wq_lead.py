"""Scratch (diag-whq): one replay, the longest dragon of each side every N rounds: id, length, head, own heads within 3, 6, 15
tiles, pearls it ate and own dragons that stopped (died with no order and a free tile) within 6 tiles of it since the last row.
Usage: python3 .../wq_lead.py <replay path> <team id> <from> <to> <every>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path


def main():
    path, team, r0, r1, every = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    gid = int(path.stem[1:])
    j = json.loads((path.parent / ('game-%d.json' % gid)).read_text())
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
    own = 0 if j['teamAId'] == team else 1
    side = lambda i: 0 if teams[i] == own else 1

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def top_of(s):
        best = None
        for i, b in bodies.items():
            if side(i) == s and (best is None or (len(b), -i) > (len(bodies[best]), -best)):
                best = i
        return best

    print(gid, j['mapName'], W, H, 'side 0 = team', team, 'against', j['team' + 'AB'[1 - own] + 'Name'], 'winner', j['winner'])
    rnd, actor = -1, None
    ate = [0, 0]
    stops = [[], []]
    rams = [[], []]
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            if r0 <= rnd <= r1 and rnd % every == 0:
                for s in (0, 1):
                    t = top_of(s)
                    if t is None:
                        continue
                    h = bodies[t][0]
                    ds = [gap(b[0], h) for i, b in bodies.items() if side(i) == s and i != t]
                    es = sorted((gap(b[0], h), len(b)) for i, b in bodies.items() if side(i) != s and gap(b[0], h) <= 6)
                    print('r%d side%d: alive %d total %d | longest #%d L%d at %s | own within 3: %d, 6: %d, 15: %d, mean %.1f | it ate %d | stops near it %s | enemy heads within 6 (tiles, length) %s%s' % (
                        rnd, s, len(ds) + 1, sum(len(b) for i, b in bodies.items() if side(i) == s), t, len(bodies[t]), h,
                        sum(1 for d in ds if d <= 3), sum(1 for d in ds if d <= 6), sum(1 for d in ds if d <= 15), sum(ds) / max(1, len(ds)),
                        ate[s], stops[s], es, (' | longest hit: ' + str(rams[s])) if rams[s] else ''))
                ate = [0, 0]
                stops = [[], []]
                rams = [[], []]
        elif k == 1:
            actor = p.i32(0)
        elif k == 3:
            if not p.u32(0):
                s = side(actor)
                if actor == top_of(s):
                    ate[s] += 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            s = side(i)
            t = top_of(s)
            if reason == 4 and t is not None and t != i:
                d = gap(bodies[i][0], bodies[t][0])
                if d <= 6:
                    stops[s].append('L%d d%d r%d' % (len(bodies[i]), d, rnd))
            if i == t and len(bodies[i]) >= 8:
                rams[s].append('r%d L%d reason %d at %s by #%s' % (rnd, len(bodies[i]), reason, bodies[i][0], actor))
            bodies.pop(i)


main()
