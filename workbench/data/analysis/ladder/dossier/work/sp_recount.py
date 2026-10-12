# Scratch (diag-spawn): independent recount of the key rate on every Nth game, written without the
# bookkeeping of sp_tick.py: full snapshots of the board at each round start, plain grid distance with wrap
# (walls and portals ignored). For every round r and every tile whose mirror got a pearl in round r:
# if the tile was empty at round r-1 and a head of the side stood on one of its 4 grid neighbours at r-1,
# did a head of that side stand on the tile at round r (spawn blocked) or was the pearl born?
# Also recounts, for all natural births of rounds 101-300, the share with a focal head on a grid neighbour.
# Usage: python3 data/analysis/ladder/dossier/work/sp_recount.py <every Nth game>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter

step = int(sys.argv[1])
rows = []
for tm, f in (('O', 'data/analysis/ladder/dossier/per-game.jsonl'), ('R', 'data/analysis/ladder/dossier/target/per-game-top1.jsonl')):
    for line in open(f):
        r = json.loads(line)
        if r['relation'] == 'us':
            rows.append((r['layout_key'], tm, r['game'], r['replay'], r['our_side']))
rows.sort()
rows = rows[::step]
tot = Counter()
for key, tm, game, path, focal in rows:
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    w, h = map(int, lines[0].split()[1:3])
    sym = [l.split()[1] for l in lines if l.startswith('SYMMETRY')][0]
    bodies, teams = {}, {}
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]

    def mirror(p):
        return (w - 1 - p[0] if 'y' in sym else p[0], h - 1 - p[1] if 'x' in sym else p[1])

    def around(p):
        x, y = p
        return (((x + 1) % w, y), ((x - 1) % w, y), (x, (y + 1) % h), (x, (y - 1) % h))

    pearls = set()
    drops = 0
    born = []
    prev = None
    rnd, actor, fresh = 0, None, False
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor, fresh = p.i32(0), None, True
            born = []
        elif k == 1:
            actor = p.i32(0)
            if fresh:
                fresh = False
                occ = {}
                heads = [set(), set()]
                for i, b in bodies.items():
                    s = 0 if teams[i] == focal else 1
                    heads[s].add(b[0])
                    for c in b:
                        occ[c] = s
                snap = (occ, set(pearls), heads)
                if prev is not None and rnd <= 300:
                    pocc, ppearl, pheads = prev
                    bs = set(born)
                    for t in bs:
                        if 101 <= rnd:
                            tot[tm + ' births b'] += 1
                            if any(n in heads[0] for n in around(t)):
                                tot[tm + ' births b, focal head on a neighbour'] += 1
                        m = mirror(t)
                        if m == t:
                            continue
                        if m in pocc or m in ppearl:
                            continue
                        for s in (0, 1):
                            if not any(n in pheads[s] for n in around(m)):
                                continue
                            name = tm + ' ' + 'FX'[s]
                            if m in bs:
                                tot[name + ' born'] += 1
                            elif m in heads[s]:
                                tot[name + ' on'] += 1
                            elif m in occ:
                                tot[name + ' other body'] += 1
                            else:
                                tot[name + ' odd'] += 1
                prev = snap
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                if drops:
                    drops -= 1
                else:
                    born.append(c)
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
            a, c = p.i32(0), p.i32(4)
            teams[c] = teams[a] = 'AB'[p.u16(8)]
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(replay.point(x) for x in p.pointer(zz))
        elif k == 11:
            i = p.i32(0)
            drops += (len(bodies[i]) + 1) // 2
            bodies.pop(i)
    tot[tm + ' games'] += 1
for k in sorted(tot):
    print(k, tot[k])
for name in ('O F', 'O X', 'R F', 'R X'):
    on, bo, ob = tot[name + ' on'], tot[name + ' born'], tot[name + ' other body']
    print('%s: head beside an empty tile, countdown 1: steps on %.1f%% (%d of %d)' % (name, 100.0 * on / max(1, on + bo + ob), on, on + bo + ob))
for tm in 'OR':
    print('%s: births in rounds 101-300 with a focal head on a neighbour %.1f%%' % (tm, 100.0 * tot[tm + ' births b, focal head on a neighbour'] / max(1, tot[tm + ' births b'])))
