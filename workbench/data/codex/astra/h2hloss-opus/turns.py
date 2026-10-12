"""Per-turn pass over every head-to-head replay (side 0 = newer version). One json row per game with counters:
 T[(side, role, lenclass, phase, pearl, foe)] = [turns, turns that ate, pearls eaten]
   role q = queen, o = other; lenclass 2,3,4,5 (5-9), 10 (10+); phase a r1-50, b r51-100, c r101-350, d r351+
   pearl = free-path steps to the nearest pearl at turn start (1, 2, or 9 = none within 2)
   foe = 1 an enemy head inside the 7x7 view, 2 only enemy body inside the view, 0 none
 qlen[side] = queen length per round ('' when dead); qdeath; splits per side by parent length (queen separately)
Usage (repo root): python3 -B data/codex/astra/h2hloss-opus/turns.py [arm ...]"""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from pathlib import Path
RUNS = Path.home() / 'meow-redteam/solo/runs'
HERE = Path('data/codex/astra/h2hloss-opus')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def one(path, k):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in lines:
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * z]), int(q[4 + 2 * z])) for z in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, (kk, p) in edges.items():
        if kk == 2:
            portals[p].append(e)
    tm = sorted(set(teams.values()))
    new = tm[k]

    def side(i):
        return 0 if teams[i] == new else 1
    queens = [min(i for i in bodies if side(i) == s) for s in (0, 1)]
    nb = {}

    def nbrs(c):
        r = nb.get(c)
        if r is None:
            r = []
            for d in range(4):
                e = edge_id(W, H, c[0], c[1], d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    prow, px = divmod(partner, W + 1)
                    py = prow // 2
                    r.append(((px - (d == 3)) % W, (py - (d == 0)) % H))
                else:
                    r.append(((c[0] + STEP[d][0]) % W, (c[1] + STEP[d][1]) % H))
            nb[c] = r
        return r
    occ = Counter()
    headof = {}
    for i, b in bodies.items():
        for c in b:
            occ[c] += 1
    pearls = set()
    T = defaultdict(lambda: [0, 0, 0])
    qlen = [[], []]
    dl = []
    splits = [Counter(), Counter()]
    rnd, actor, cur = -1, None, None

    def close():
        nonlocal cur
        if cur is not None:
            t = T[cur[0]]
            t[0] += 1
            t[1] += 1 if cur[1] else 0
            t[2] += cur[1]
            cur = None
    for ev in root.pointer(3):
        kk = ev.u16(0)
        if kk not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if kk == 0:
            close()
            rnd = p.i32(0)
            for s in (0, 1):
                qlen[s].append(len(bodies[queens[s]]) if queens[s] in bodies else 0)
        elif kk == 1:
            close()
            actor = p.i32(0)
            b = bodies[actor]
            h = b[0]
            s = side(actor)
            L = len(b)
            pd = 9
            n1 = [c for c in nbrs(h) if not occ[c]]
            if any(c in pearls for c in n1):
                pd = 1
            elif any(c2 in pearls and not occ[c2] for c in n1 for c2 in nbrs(c)):
                pd = 2
            foe = 0
            for z, bb in bodies.items():
                if teams[z] == teams[actor]:
                    continue
                for n, c in enumerate(bb):
                    dx = abs(c[0] - h[0]); dx = min(dx, W - dx)
                    dy = abs(c[1] - h[1]); dy = min(dy, H - dy)
                    if dx <= 3 and dy <= 3:
                        if n == 0:
                            foe = 1
                            break
                        foe = 2
                if foe == 1:
                    break
            ph = 'a' if rnd <= 50 else 'b' if rnd <= 100 else 'c' if rnd <= 350 else 'd'
            lc = L if L <= 4 else 5 if L <= 9 else 10
            cur = [(s, 'q' if actor == queens[s] else 'o', lc, ph, pd, foe), 0]
        elif kk == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.discard(c)
                if cur is not None:
                    cur[1] += 1
        elif kk == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                occ[hd] += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif kk == 10:
            pa, ch = p.i32(0), p.i32(4)
            Lb = len(bodies[pa])
            for c in bodies[pa]:
                occ[c] -= 1
            for z, i in enumerate((pa, ch)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = p.u16(8)
                for c in bodies[i]:
                    occ[c] += 1
            sp = side(pa)
            splits[sp][('q' if pa == queens[sp] else 'o') + str(min(Lb, 10)) + ('a' if rnd <= 100 else 'c')] += 1
        elif kk == 11:
            i = p.i32(0)
            s_ = side(i)
            qd = -1
            if queens[s_] in bodies and i != queens[s_]:
                a, b2 = bodies[i][0], bodies[queens[s_]][0]
                dx = abs(a[0] - b2[0]); dy = abs(a[1] - b2[1])
                qd = min(dx, W - dx) + min(dy, H - dy)
            dl.append([rnd, s_, len(bodies[i]), p.u16(4), qd, int(i == actor), int(i == queens[s_]), len(bodies[queens[s_]]) if queens[s_] in bodies else 0])
            for c in bodies[i]:
                occ[c] -= 1
            bodies.pop(i)
    close()
    return dict(T={'|'.join(map(str, kk)): v for kk, v in T.items()}, qlen=qlen, dl=dl, splits=[dict(x) for x in splits], W=W, H=H)


if __name__ == '__main__':
    for arm in sys.argv[1:] or ['h2h_mDone11_v8', 'h2h_mDone10_v8', 'h2h_mDone8_v5', 'h2h_mDone11_v5']:
        cp = HERE / ('turns-%s.jsonl' % arm)
        cache = {}
        if cp.exists():
            for l in cp.read_text().splitlines():
                g = json.loads(l)
                cache[g['folder']] = g
        for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
            if not (folder / 'result.txt').exists() or folder.name in cache:
                continue
            k = int(folder.name[-1])
            g = one(folder / 'game.replay', k)
            g['folder'] = folder.name
            rl = (folder / 'result.txt').read_text()
            g['win'] = int(('winner=%d' % k) in rl)
            cache[folder.name] = g
        with open(cp, 'w') as f:
            for g in cache.values():
                f.write(json.dumps(g, separators=(',', ':')) + '\n')
        print(arm, len(cache))
