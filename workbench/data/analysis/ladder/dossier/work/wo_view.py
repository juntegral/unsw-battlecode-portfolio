"""Scratch (diag-wipeout): replay viewer for one side with few dragons. For rounds r0..r1 prints, per round, every
dragon of ours (id, length, head, the steps it took), the enemy heads within 7 tiles of it, the pearls within 7 tiles,
and the events (eat, split, death). Usage: python3 .../wo_view.py <replay path> <team id> <r0> <r1> [grid]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque
from pathlib import Path


def main():
    path, team, r0, r1 = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    grid = len(sys.argv) > 5
    gid = int(path.stem[1:])
    j = json.loads((path.parent / ('game-%d.json' % gid)).read_text())
    root = replay.load(path).root()
    text = root.text(0)
    lines = text.splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    own = 0 if j['teamAId'] == team else 1
    side = lambda i: 'u' if teams[i] == own else 't'

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    def walls(h):
        return ''.join('NESW'[d] for d in range(4) if edges.get(edge_id(W, H, h[0], h[1], d), (0, -1))[0] == 1)

    print(gid, j['mapName'], W, H, 'we are', 'AB'[own], 'vs', j['team' + 'AB'[1 - own] + 'Name'], 'winner', j['winner'])
    print('starts', ' '.join('%s#%d L%d %s' % (side(i), i, len(b), b[0]) for i, b in bodies.items()))
    pearls = {}
    rnd, actor = -1, None
    moves = {}
    notes = []

    def show():
        if not (r0 <= rnd <= r1):
            return
        nu = sum(1 for i in bodies if side(i) == 'u')
        print('r%d ours %d (len %d) theirs %d (len %d) pearls %d' % (rnd, nu, sum(len(b) for i, b in bodies.items() if side(i) == 'u'),
                                                                   len(bodies) - nu, sum(len(b) for i, b in bodies.items() if side(i) == 't'), len(pearls)))
        for i, b in sorted(bodies.items()):
            if side(i) != 'u':
                continue
            foes = sorted((gap(b[0], bb[0]), z, len(bb), bb[0]) for z, bb in bodies.items() if side(z) == 't' and gap(b[0], bb[0]) <= 7)
            ps = sorted((gap(b[0], c), c) for c in pearls if gap(b[0], c) <= 7)
            mates = sorted((gap(b[0], bb[0]), z, len(bb)) for z, bb in bodies.items() if side(z) == 'u' and z != i and gap(b[0], bb[0]) <= 7)
            print('   #%d L%d at %s walls[%s] moved %s | foes %s | pearls %s | mates %s' % (
                i, len(b), b[0], walls(b[0]), moves.get(i, '-'),
                ' '.join('#%d L%d %s d%d' % (z, L, c, g) for g, z, L, c in foes) or '-',
                ' '.join('%s d%d' % (c, g) for g, c in ps[:6]) or '-',
                ' '.join('#%d L%d d%d' % (z, L, g) for g, z, L in mates) or '-'))
        for n in notes:
            print('   * ' + n)
        if grid and nu:
            xs = [b[0][0] for i, b in bodies.items() if side(i) == 'u']
            ys = [b[0][1] for i, b in bodies.items() if side(i) == 'u']
            x0, x1, y0, y1 = max(0, min(xs) - 8), min(W - 1, max(xs) + 8), max(0, min(ys) - 6), min(H - 1, max(ys) + 6)
            cell = {}
            for i, b in bodies.items():
                for n, c in enumerate(b):
                    cell[c] = ('U' if n == 0 else 'u') if side(i) == 'u' else ('T' if n == 0 else 't')
            for y in range(y0, y1 + 1):
                row = ''
                for x in range(x0, x1 + 1):
                    ch = cell.get((x, y), 'o' if (x, y) in pearls else '.')
                    wl = edges.get(edge_id(W, H, x, y, 1), (0, -1))[0]
                    row += ch + ('|' if wl == 1 else ':' if wl == 2 else ' ')
                und = ''
                for x in range(x0, x1 + 1):
                    wl = edges.get(edge_id(W, H, x, y, 2), (0, -1))[0]
                    und += ('-' if wl == 1 else '~' if wl == 2 else ' ') + ' '
                print('      %2d %s' % (y, row))
                print('         %s' % und)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            show()
            rnd, actor = p.i32(0), None
            moves, notes = {}, []
            if rnd > r1:
                break
        elif k == 1:
            actor = p.i32(0)
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls[c] = rnd
            else:
                born = pearls.pop(c)
                if side(actor) == 'u' or r0 <= rnd <= r1 and any(side(i) == 'u' and gap(b[0], c) <= 7 for i, b in bodies.items()):
                    notes.append('%s#%d eats %s (born r%d)' % (side(actor), actor, c, born))
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                moves[i] = moves.get(i, '') + '>%d,%d' % hd
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if side(parent) == 'u':
                notes.append('split #%d -> #%d L%d + #%d L%d' % (parent, parent, len(bodies[parent]), child, len(bodies[child])))
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies[i]
            if side(i) == 'u' or any(side(z) == 'u' and gap(bb[0], b[0]) <= 7 for z, bb in bodies.items()):
                notes.append('death %s#%d L%d at %s reason %s (actor #%s)' % (side(i), i, len(b), b[0], ('wall', 'own body', 'other body', 'head-on', 'other')[reason], actor))
            bodies.pop(i)
    show()


main()
