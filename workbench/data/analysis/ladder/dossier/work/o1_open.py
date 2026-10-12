"""Scratch (diag-one1, job C): rounds 0-30, every dragon of both sides, turn by turn.
Per turn: heading kept / turned / portal step / split / no move; pearl in view; tiles new to this dragon's own view history
and new to its side's; whether a spawn tile (any tile where a natural pearl is born in this game) is in view; head position.
Per side: rounds of the first six meals; tiles and spawn tiles seen by r5..r30.
Usage (repo root): python3 -B data/analysis/ladder/dossier/work/o1_open.py <set>"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from o1_scan import jobs, OUT, STEP
LAST = 30


def scan(label, path, j, team=1119):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    own = 0 if j['teamAId'] == team else 1
    side = lambda i: 0 if teams[i] == own else 1
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    events = list(root.pointer(3))
    # hindsight: spawn tiles
    spawn = set()
    expected = 0
    b2 = {i: len(b) for i, b in bodies.items()}
    for ev in events:
        k = ev.u16(0)
        if k == 3:
            p = ev.pointer(0)
            if p.u32(0):
                if expected:
                    expected -= 1
                else:
                    spawn.add(replay.point(p.pointer(0)))
        elif k == 11:
            pass
    # the pass above does not track deaths; redo exactly below with bodies

    def view(h):
        return [((h[0] + dx) % W, (h[1] + dy) % H) for dx in range(-3, 4) for dy in range(-3, 4)]

    def dest(h, d):
        x, y = h
        e = edge_id(W, H, x, y, d)
        kind, pid = edges.get(e, (0, -1))
        if kind == 1:
            return None, 0
        if kind == 2:
            partner = [z for z in portals[pid] if z != e][0]
            prow, px = divmod(partner, W + 1)
            py = prow // 2
            return ((px - (d == 3)) % W, (py - (d == 0)) % H), 1
        dx, dy = STEP[d]
        return ((x + dx) % W, (y + dy) % H), 0

    def move_dir(a, b):
        for d in range(4):
            t, port = dest(a, d)
            if t == b:
                return d, port
        return -1, 0

    # exact spawn set with deaths tracked
    spawn = set()
    expected = 0
    lens = {i: len(b) for i, b in bodies.items()}
    tmp = {i: deque(b) for i, b in bodies.items()}
    for ev in events:
        k = ev.u16(0)
        if k not in (3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 3:
            if p.u32(0):
                if expected:
                    expected -= 1
                else:
                    spawn.add(replay.point(p.pointer(0)))
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = tmp[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                tmp[i] = deque(replay.point(c) for c in p.pointer(z))
        elif k == 11:
            i = p.i32(0)
            expected = (len(tmp[i]) + 1) // 2
            tmp.pop(i)

    seen_own = {i: set(view(b[0])) for i, b in bodies.items()}
    seen_side = [set(), set()]
    for i, b in bodies.items():
        seen_side[side(i)].update(view(b[0]))
    heading = {}
    for i, b in bodies.items():
        if len(b) > 1:
            heading[i] = move_dir(b[1], b[0])[0]
    born = {i: -1 for i in bodies}
    parent_of = {}
    pearls = set()
    meals = [[], []]
    cover = {}
    turns = []           # [round, side, id, starter 1/0, queen, L, class, port, pearl in view, own new, side new, spawn in view, x, y, ate, age]
    rnd, actor, cur = -1, None, None
    expected = 0

    def close():
        nonlocal cur
        if cur is None:
            return
        i = cur['i']
        if i in bodies:
            h1 = bodies[i][0]
            if cur['split']:
                cls = 'split'
            elif h1 == cur['h0']:
                cls = 'still'
            else:
                d, port = cur['d'], cur['port']
                cls = 'portal' if port else 'straight' if d == cur['head0'] else 'turn' if cur['head0'] >= 0 else 'first'
                heading[i] = cur['dlast']
            v = set(view(h1))
            on = len(v - seen_own[i])
            sn = len(v - seen_side[cur['s']])
            seen_own[i] |= v
            seen_side[cur['s']] |= v
        else:
            cls, on, sn, h1 = 'died', 0, 0, cur['h0']
        turns.append([cur['r'], cur['s'], i, int(born[i] < 0), int(i == queens[cur['s']]), cur['L'], cls, cur['port'], cur['pv'], on, sn, cur['sv'],
                      h1[0], h1[1], cur['ate'], cur['r'] - born[i] if born[i] >= 0 else -1])
        cur = None

    for ev in events:
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            close()
            if rnd >= 0 and rnd % 5 == 0:
                cover[rnd] = [[len(seen_side[s]), len(seen_side[s] & spawn), sum(1 for i in bodies if side(i) == s)] for s in (0, 1)]
            rnd, actor = p.i32(0), None
            if rnd > LAST:
                break
        elif k == 1:
            close()
            actor = p.i32(0)
            s = side(actor)
            h = bodies[actor][0]
            v = view(h)
            cur = dict(i=actor, s=s, r=rnd, L=len(bodies[actor]), h0=h, head0=heading.get(actor, -1), split=0, ate=0, d=-1, port=0, dlast=-1,
                       pv=int(any(c in pearls for c in v)), sv=int(any(c in spawn for c in v)))
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                if expected:
                    expected -= 1
                pearls.add(c)
            else:
                pearls.discard(c)
                if cur is not None:
                    cur['ate'] += 1
                    meals[cur['s']].append(rnd)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                if cur is not None and cur['i'] == i:
                    d, port = move_dir(b[0], hd)
                    if cur['d'] < 0:
                        cur['d'] = d
                    cur['port'] = cur['port'] or port
                    cur['dlast'] = d
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
            born[child] = rnd
            parent_of[child] = parent
            cb = bodies[child]
            seen_own[child] = set(view(cb[0]))
            seen_side[side(child)].update(view(cb[0]))
            heading[child] = move_dir(cb[1], cb[0])[0] if len(cb) > 1 else -1
            if cur is not None and cur['i'] == parent:
                cur['split'] = 1
        elif k == 11:
            i = p.i32(0)
            expected = (len(bodies[i]) + 1) // 2
            bodies.pop(i)
    close()
    return dict(src=label, bot=[root.text(1), root.text(2)][own], gid=j['id'], map=j['mapName'], cells=W * H, w=W, h=H,
                opp=j['team' + 'AB'[1 - own] + 'Name'], spawn=len(spawn), nport=len(portals), meals=[m[:8] for m in meals], cover=cover, turns=turns)


if __name__ == '__main__':
    name = sys.argv[1]
    todo = jobs(name)
    with open(OUT + 'o1_open-%s.jsonl' % name, 'w') as f:
        for label, path, j in todo:
            f.write(json.dumps(scan(label, path, j), separators=(',', ':')) + '\n')
    print('done', name, len(todo))
