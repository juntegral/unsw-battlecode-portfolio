"""Our queen's death in a replay, with her last turns drawn. Usage (from ROOT): qd.py <replay> <own side 0/1> [boards=3] [brief]"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


ALLP = []


def run(path, own, nb=3, brief=False, upto=500):
    del ALLP[:]
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
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
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    queen = min(i for i in bodies if teams[i] == own)

    def ek(c, d):
        return edges.get(edge_id(W, H, c[0], c[1], d), (0, -1))[0]

    def dest(h, d):
        x, y = h
        e = edge_id(W, H, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 1:
            return None
        if kind == 2:
            partner = [z for z in portals[pid] if z != e][0]
            prow, px = divmod(partner, W + 1)
            py = prow // 2
            return ((px - (d == 3)) % W, (py - (d == 0)) % H)
        dx, dy = STEP[d]
        return ((x + dx) % W, (y + dy) % H)

    def occ():
        o = set()
        for bb in bodies.values():
            o.update(bb)
        return o

    def free(h):
        o = occ()
        out = ''
        for d in range(4):
            n = dest(h, d)
            if n is not None and n not in o:
                out += ('nesw' if ek(h, d) == 2 else 'NESW')[d]
        return out

    def room(h, cap=40):
        o = occ() - {h}
        seen = {h}
        qu = deque([h])
        viaportal = 0
        while qu and len(seen) < cap:
            c = qu.popleft()
            for d in range(4):
                if ek(c, d) == 2:
                    viaportal += 1
                    continue
                n = dest(c, d)
                if n is None or n in seen or n in o:
                    continue
                seen.add(n)
                qu.append(n)
        return len(seen) - 1, viaportal

    def board(a):
        h = bodies[a][0]
        out = []
        for dy in range(-3, 4):
            row = ''
            for dx in range(-3, 4):
                c = ((h[0] + dx) % W, (h[1] + dy) % H)
                ch = '.'
                if c in pearls:
                    ch = 'o'
                for z, bb in bodies.items():
                    if c in bb:
                        mine = teams[z] == teams[a]
                        ch = ('H' if z == a else 'M' if mine else 'E') if bb[0] == c else ('b' if z == a else 'm' if mine else 'e')
                wall = ''.join('NESW'[d] if ek(c, d) == 1 else 'nesw'[d] if ek(c, d) == 2 else '' for d in range(4))
                row += '%-6s' % (ch + wall)
            out.append('      ' + row)
        return out

    pearls = {}
    lastp = [None]
    rnd, actor = -1, None
    hist = []
    log = []
    dirs = []
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            if rnd > upto:
                break
        elif k == 1:
            actor = p.i32(0)
            if actor == queen:
                rm = room(bodies[queen][0])
                qh = bodies[queen][0]
                o = {c: z for z, bb in bodies.items() for c in bb}
                ds = ' '.join('%s%s->%s%s' % ('NESW'[d], 'p' if ek(qh, d) == 2 else '', dest(qh, d), ('[%s%d]' % ('own' if o[dest(qh, d)] == queen else 'mate' if teams[o[dest(qh, d)]] == own else 'foe', o[dest(qh, d)])) if dest(qh, d) in o else '') for d in range(4) if ek(qh, d) != 1)
                hist.append(['r%d head %s L%d body %s free %s room(no portal) %d portal-sides %d units %d | %s' % (rnd, qh, len(bodies[queen]), list(bodies[queen]), free(qh) or '-', rm[0], rm[1], sum(1 for z in bodies if teams[z] == own), ds), board(queen), []])
        elif k == 4:
            a = p.pointer(0)
            dirs = list(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else []
            if actor == queen and hist:
                hist[-1][2].append('queen action kind %d dirs %s' % (a.u16(0) if a else -1, ''.join('NESW'[d] for d in dirs)))
            elif hist and teams.get(actor) == own:
                hd = bodies[actor][0]
                qh = bodies[queen][0] if queen in bodies else None
                if qh and max(abs((hd[0] - qh[0] + W // 2) % W - W // 2), abs((hd[1] - qh[1] + H // 2) % H - H // 2)) <= 3:
                    hist[-1][2].append('  mate %d L%d at %s action kind %d dirs %s' % (actor, len(bodies[actor]), hd, a.u16(0) if a else -1, ''.join('NESW'[d] for d in dirs)))
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls[c] = rnd
            else:
                pearls.pop(c, None)
                if actor == queen and hist:
                    hist[-1][2].append('queen eats %s' % (c,))
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                if i == queen:
                    for d in range(4):
                        if ek(b[0], d) == 2 and dest(b[0], d) == hd:
                            seen = {hd}
                            qu = deque([hd])
                            while qu and len(seen) < 40:
                                c = qu.popleft()
                                for e in range(4):
                                    if ek(c, e) == 0:
                                        n = dest(c, e)
                                        if n not in seen:
                                            seen.add(n)
                                            qu.append(n)
                            lastp[0] = (rnd, len(seen))
                            ALLP.append((rnd, len(seen)))
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            Lb = len(bodies[parent])
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            if parent == queen and hist:
                hist[-1][2].append('QUEEN SPLIT L%d -> queen %s child %d %s' % (Lb, list(bodies[parent]), child, list(bodies[child])))
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            if i == queen:
                h = bodies[i][0]
                kd = {0: 'wall', 1: 'own body', 2: 'body', 3: 'head'}.get(reason, 'stop')
                print('%s side%d QUEEN DEAD r%d L%d reason %s (actor %d%s) free-at-death %s | last portal step %s, walled room entered %s cells' % (path[-60:], own, rnd, len(bodies[i]), kd, actor, ' = queen' if actor == queen else '', free(h) or '-', ('r%d' % lastp[0][0]) if lastp[0] else 'never', lastp[0][1] if lastp[0] else '-'))
                if not brief:
                    for head, bd, notes in hist[-nb:]:
                        print('  ' + head)
                        for l in bd:
                            print(l)
                        for n in notes:
                            print('     ' + n)
                return rnd
            bodies.pop(i)
    print('%s side%d queen alive at end L%d' % (path[-60:], own, len(bodies.get(queen, ()))))
    return None


if __name__ == '__main__':
    run(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 3, len(sys.argv) > 4)
