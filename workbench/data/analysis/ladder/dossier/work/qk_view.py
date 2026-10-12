"""Scratch (diag-queenkill): draw the board around one dragon at the start of its turn, the free path to the enemy queen's head,
and what the dragon did. Own-code recount of a chance row: no Geo class, edges read straight from the map text.
Usage: python3 qk_view.py <replay> <A|B = side of the mover> <round> <dragon id>"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import deque, defaultdict
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
NAME = 'NESW'


def main():
    path, letter, want_round, want_id = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
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

    def go(c, d):
        x, y = c
        e = edge_id(w, h, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 1:
            return None
        if kind == 2:
            partner = [z for z in portals[pid] if z != e][0]
            row, px = divmod(partner, w + 1)
            return ((px - (d == 3)) % w, (row // 2 - (d == 0)) % h)
        return ((x + STEP[d][0]) % w, (y + STEP[d][1]) % h)

    queen = {t: min(i for i in bodies if teams[i] == t) for t in 'AB'}
    pearls = set()
    rnd, shown, actor = 0, False, None
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            if shown:
                break
            rnd = p.i32(0)
        elif k == 1:
            if shown:
                break
            actor = p.i32(0)
            if rnd == want_round and actor == want_id:
                shown = True
                en = 'B' if letter == 'A' else 'A'
                b = bodies[actor]
                L = len(b)
                free = (L + 3) // 4
                qb = bodies.get(queen[en])
                print('round', rnd, 'dragon', actor, 'side', teams[actor], 'length', L, 'free steps', free, 'reach', free + L - 2,
                      '| enemy queen id', queen[en], 'length', len(qb) if qb else 0, 'head', qb[0] if qb else None,
                      '| own queen id', queen[letter], 'length', len(bodies.get(queen[letter], ())))
                occ = {}
                for i, bb in bodies.items():
                    for n, c in enumerate(bb):
                        own = teams[i] == letter
                        occ[c] = ('M' if i == actor else 'O' if own else 'Q' if i == queen[en] else 'E') if n == 0 else ('m' if i == actor else 'o' if own else 'q' if i == queen[en] else 'e')
                hx, hy = b[0]
                for dy in range(-4, 5):
                    print('   ', ' '.join(occ.get(((hx + dx) % w, (hy + dy) % h), '*' if ((hx + dx) % w, (hy + dy) % h) in pearls else '.') for dx in range(-4, 5)))
                if qb:
                    prev = {b[0]: None}
                    dq = deque([b[0]])
                    found = None
                    while dq and found is None:
                        c = dq.popleft()
                        for d in range(4):
                            t = go(c, d)
                            if t is None or t in prev:
                                continue
                            if t == qb[0]:
                                prev[t] = (c, d)
                                found = t
                                break
                            if t in occ:
                                continue
                            prev[t] = (c, d)
                            dq.append(t)
                    if found is None:
                        print('    no free way to her head')
                    else:
                        way = []
                        c = found
                        while prev[c] is not None:
                            c, d = prev[c]
                            way.append(NAME[d])
                        way.reverse()
                        print('    free way to her head:', ''.join(way), 'steps', len(way), 'paid', max(0, len(way) - free), 'in reach' if len(way) <= free + L - 2 else 'out of reach')
        elif k == 4:
            if shown and p.i32(0) == want_id:
                a = p.pointer(0)
                kind = a.u16(0) if a else 2
                dirs = list(a.pointer(0)) if a and kind == 0 and a.pointer(0) is not None else []
                print('    action:', ('move ' + ''.join(NAME[d] for d in dirs)) if kind == 0 else 'split' if kind == 1 else 'none')
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.discard(c)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            i = p.i32(0)
            if shown:
                print('    death in this turn: dragon', i, 'side', teams[i], 'length', len(bodies[i]), 'reason', p.u16(4), '(3 = head-on)', 'QUEEN' if i in queen.values() else '')
            bodies.pop(i)
    if not shown:
        print('turn not found')


main()
