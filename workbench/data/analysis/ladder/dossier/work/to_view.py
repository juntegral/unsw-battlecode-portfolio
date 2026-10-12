# Scratch (diag-topopen): print the turns of one side (or one dragon) of a replay.
# Usage: python3 to_view.py <replay path> <A|B> <first round> <last round> [dragon id]
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import deque, defaultdict
from pathlib import Path

NAMES = 'NESW'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def main():
    path, mine, r0, r1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    only = int(sys.argv[5]) if len(sys.argv) > 5 else None
    root = replay.load(Path(path)).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    edges = canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)

    def nbrs(c):
        x, y = c
        out = []
        for d in range(4):
            e = edge_id(w, h, x, y, d)
            kind, pid = edges.get(e, (0, -1))
            if kind == 1:
                continue
            if kind == 2:
                partner = [z for z in portals[pid] if z != e][0]
                ry, px = divmod(partner, w + 1)
                out.append((NAMES[d] + '*', ((px - (d == 3)) % w, (ry // 2 - (d == 0)) % h)))
            else:
                out.append((NAMES[d], ((x + STEP[d][0]) % w, (y + STEP[d][1]) % h)))
        return out

    print('size', w, h, 'side', mine, 'queen', min(i for i in bodies if teams[i] == mine))
    present = {}
    rnd, actor, line = 0, None, None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k in (0, 1) and line:
            print(line)
            line = None
        if k == 0:
            rnd, actor = p.i32(0), None
            if rnd > r1:
                break
        elif k == 1:
            actor = p.i32(0)
            if r0 <= rnd <= r1 and teams[actor] == mine and (only is None or actor == only):
                b = bodies[actor]
                occ = {c: i for i, bb in bodies.items() for c in bb}
                heads = {bb[0]: i for i, bb in bodies.items()}
                desc = []
                for nm, c in nbrs(b[0]):
                    what = 'pearl' if c in present else ('body%d' % occ[c]) if c in occ else 'free'
                    around = []
                    for nm2, c2 in nbrs(c):
                        if c2 in heads and heads[c2] != actor:
                            around.append(('mate' if teams[heads[c2]] == mine else 'ENEMY') + str(heads[c2]) + ' head')
                        elif c2 in present:
                            around.append('pearl' + str(c2))
                    desc.append('%s%s %s%s' % (nm, c, what, (' [' + ', '.join(around) + ']') if around else ''))
                line = 'r%d #%d len %d body %s | %s | ' % (rnd, actor, len(b), list(b), ' ; '.join(desc))
        elif k == 4:
            a = p.pointer(0)
            if line is not None:
                kind = a.u16(0) if a else 2
                if kind == 0 and a.pointer(0) is not None:
                    line += 'MOVE ' + ''.join(NAMES[d] for d in a.pointer(0))
                elif kind == 1:
                    line += 'SPLIT'
                else:
                    line += 'NO ACTION'
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present[c] = rnd
            else:
                born = present.pop(c)
                if line is not None:
                    line += ' ate%s(born r%d)' % (c, born)
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
                teams[i] = 'AB'[p.u16(8)]
            if line is not None:
                line += ' child #%d %s' % (child, list(bodies[child]))
        elif k == 11:
            i = p.i32(0)
            if line is not None and i == actor:
                line += ' DIED reason %d' % p.u16(4)
            bodies.pop(i)
    if line:
        print(line)


main()
