"""stuck-opus: wasted-turn detector over replays, both sides. One json row per game (cached by key) into rows-<tag>.jsonl.
Usage (from ROOT): python3 -B data/codex/astra/stuck-opus/detect.py online one14-c1 one13-c1 ...
                   python3 -B data/codex/astra/stuck-opus/detect.py local h2h_mNps_v13 pc_mNps ...
Patterns per dragon (head sampled at every round start):
 a  12-round window with <=6 distinct head cells          a2 30-round window with <=12 distinct head cells
 b  8-round window with <=2 distinct head cells
 c  15-round window: a free path of <=10 steps to a pearl every round, no enemy head within 6 (torus manhattan),
    no eat, and never nearer than at the window start      c0 the same without the "never nearer" clause
 d  20-round window: >=2 mate heads within 3 every round and no eat
 e  death on a wall / own body (and mate body, listed apart) within 3 rounds of the split that made or cut the dragon"""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from geom import geometry
from collections import deque, defaultdict
from pathlib import Path

HERE = Path('data/codex/astra/loss15-sonnet')
SM = Path('data/online/smoke')
RUNS = Path.home() / 'meow-redteam/solo/runs'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
PH = (100, 350)


def phase(r):
    return 0 if r < PH[0] else 1 if r < PH[1] else 2


def scan(path, our_team):
    root = replay.load(path).root()
    G = geometry(root.text(0))
    W, H, N, nb, pcell, nwall, portals, dead, bodies, teams = (G[k] for k in ('W', 'H', 'N', 'nb', 'pcell', 'nwall', 'portals', 'dead', 'bodies', 'teams'))
    pnear = set(pcell)
    for _ in range(2):
        pnear |= {n for c in pnear for n in nb[c]}
    queens = {t: min(i for i in teams if teams[i] == t) for t in (0, 1)}
    pearls = {}
    dstat = dict(eat=[0, 0], eat_tip=[0, 0], die=[0, 0], stale=0, cells=len(dead), tips=sum(1 for v in dead.values() if v == 1))
    rec = defaultdict(list)
    since, hist, lex = {}, {}, []
    lc = [[{} for _ in range(3)] for _ in range(2)]
    born, died, splitr = {}, {}, {}
    rnd = -1
    actor = None
    use_field = N <= 6000

    def snapshot():
        occ = set()
        for b in bodies.values():
            occ.update(b)
        if use_field:
            dist = {c: 0 for c in pearls}
            fr = list(pearls)
            for dd in range(1, 10):
                nx = []
                for c in fr:
                    for n in nb[c]:
                        if n not in dist and n not in occ:
                            dist[n] = dd
                            nx.append(n)
                fr = nx
                if not fr:
                    break
        stale = [(c % W, c // W) for c, b0 in pearls.items() if c in dead and rnd - b0 >= 10]
        dstat['stale'] += len(stale)
        ids = list(bodies)
        hx = [bodies[i][0] % W for i in ids]
        hy = [bodies[i][0] // W for i in ids]
        tm = [teams[i] for i in ids]
        en = [0] * len(ids)
        mt = [0] * len(ids)
        hw, hh = W // 2, H // 2
        for a in range(len(ids)):
            xa, ya, ta = hx[a], hy[a], tm[a]
            for b in range(a + 1, len(ids)):
                dx = abs(xa - hx[b])
                if dx > hw:
                    dx = W - dx
                if dx > 6:
                    continue
                dy = abs(ya - hy[b])
                if dy > hh:
                    dy = H - dy
                m = dx + dy
                if m > 6:
                    continue
                if ta != tm[b]:
                    en[a] = en[b] = 1
                elif m <= 3:
                    mt[a] += 1
                    mt[b] += 1
        for z, i in enumerate(ids):
            h = bodies[i][0]
            if use_field:
                best = 99
                for n in nb[h]:
                    v = dist.get(n)
                    if v is not None and v + 1 < best:
                        best = v + 1
            else:
                best = 99
                seen = {h}
                fr = [h]
                for dd in range(1, 11):
                    nx = []
                    for c in fr:
                        for n in nb[c]:
                            if n in seen or n in occ:
                                continue
                            if n in pearls:
                                best = dd
                                break
                            seen.add(n)
                            nx.append(n)
                        if best < 99:
                            break
                    if best < 99 or not nx:
                        break
                    fr = nx
            dp = 99
            for px, py in stale:
                dx = abs(hx[z] - px)
                if dx > hw:
                    dx = W - dx
                dy = abs(hy[z] - py)
                if dy > hh:
                    dy = H - dy
                if dx + dy < dp:
                    dp = dx + dy
            # loop class: 30 rounds without an eat on <=12 cells, classified by the nearest pearl on a free path of <=12 steps
            since[i] = (0 if rec[i][-1][5] else since.get(i, 0) + 1) if rec[i] else 0
            hq = hist.setdefault(i, deque(maxlen=30))
            hq.append(h)
            if len(hq) == 30 and since[i] >= 30 and len(set(hq)) <= 12:
                sd = 0 if teams[i] == our_team else 1
                own = set(bodies[i])
                own.discard(bodies[i][1] if len(bodies[i]) > 1 else -1)
                found, fd = -1, 0
                seen = {h}
                fr = [h]
                for dd in range(1, 13):
                    nx = []
                    for c in fr:
                        for n in nb[c]:
                            if n in seen or (n in occ and n not in own):
                                continue
                            if n in pearls:
                                found, fd = n, dd
                                break
                            seen.add(n)
                            nx.append(n)
                        if found >= 0:
                            break
                    if found >= 0 or not nx:
                        break
                    fr = nx
                if found < 0:
                    cat = 'idle'
                elif found in dead:
                    cat = 'deadend'
                elif en[z]:
                    cat = 'enemy'
                else:
                    fx, fy = found % W, found // W
                    cat = 'free'
                    for b in range(len(ids)):
                        if b != z and tm[b] == tm[z]:
                            dx = abs(hx[b] - fx)
                            if dx > hw:
                                dx = W - dx
                            dy = abs(hy[b] - fy)
                            if dy > hh:
                                dy = H - dy
                            if dx + dy <= fd:
                                cat = 'mate'
                                break
                lc[sd][phase(rnd)][cat] = lc[sd][phase(rnd)].get(cat, 0) + 1
                if cat in ('free', 'deadend') and sd == 0 and rnd % 10 == 0:
                    lex.append((cat, i, rnd, h % W, h // W, found % W, found // W, fd, rnd - pearls[found], len(bodies[i])))
            rec[i].append([rnd, h, best, en[z], mt[z], 0, len(bodies[i]), dp])

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            actor = None
            snapshot()
        elif k == 1:
            actor = p.i32(0)
        elif k == 3:
            pt = replay.point(p.pointer(0))
            c = pt[1] * W + pt[0]
            if p.u32(0):
                pearls[c] = rnd
            else:
                pearls.pop(c, None)
                if actor is not None and c in dead and actor in teams:
                    sd = 0 if teams[actor] == our_team else 1
                    dstat['eat'][sd] += 1
                    dstat['eat_tip'][sd] += dead[c] == 1
                if actor is not None and rec[actor] and rec[actor][-1][0] == rnd:
                    rec[actor][-1][5] = 1
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
                teams[i] = p.u16(8)
                splitr[i] = rnd
                if z == 1:
                    born[i] = rnd
        elif k == 11:
            i = p.i32(0)
            died[i] = (rnd, p.u16(4), len(bodies[i]))
            if bodies[i][0] in dead and p.u16(4) in (0, 1):
                dstat['die'][0 if teams[i] == our_team else 1] += 1
            bodies.pop(i)

    pats = ('a', 'an', 'a2', 'a2n', 'b', 'c', 'c0', 'd', 'and', 'a2nd', 'nd')
    win = dict(a=12, an=12, a2=30, a2n=30, b=8, c=15, c0=15, d=20, nd=1)
    # counts[side][role][phase][pattern]; side 0 = us
    cnt = [[[dict.fromkeys(pats + ('n',), 0) for _ in range(3)] for _ in range(2)] for _ in range(2)]
    cntp = [dict.fromkeys(pats, 0) for _ in range(2)]
    eps = []
    for i, rs in rec.items():
        side = 0 if teams[i] == our_team else 1
        role = 0 if i == queens[teams[i]] else 1
        n = len(rs)
        flag = {p: bytearray(n) for p in pats}
        hs = [r[1] for r in rs]
        ate = [0]
        for r in rs:
            ate.append(ate[-1] + r[5])
        for p, lim in (('a', 6), ('a2', 12), ('b', 2)):
            w = win[p]
            f = flag[p]
            fn = flag.get(p + 'n')
            for t in range(w - 1, n):
                if len(set(hs[t - w + 1:t + 1])) <= lim:
                    for u in range(t - w + 1, t + 1):
                        f[u] = 1
                    if fn is not None and ate[t + 1] == ate[t - w + 1]:
                        for u in range(t - w + 1, t + 1):
                            fn[u] = 1
        okc = [1 if (r[2] <= 10 and not r[3] and not r[5]) else 0 for r in rs]
        run = 0
        for t in range(n):
            run = run + 1 if okc[t] else 0
            if run >= 15:
                for u in range(t - 14, t + 1):
                    flag['c0'][u] = 1
                if min(r[2] for r in rs[t - 14:t + 1]) >= rs[t - 14][2]:
                    for u in range(t - 14, t + 1):
                        flag['c'][u] = 1
        run = 0
        for t in range(n):
            run = run + 1 if (rs[t][4] >= 2 and not rs[t][5]) else 0
            if run >= 20:
                for u in range(t - 19, t + 1):
                    flag['d'][u] = 1
        for t in range(n):
            if rs[t][7] <= 4:
                flag['nd'][t] = 1
                flag['and'][t] = flag['an'][t]
                flag['a2nd'][t] = flag['a2n'][t]
        for t in range(n):
            ph = phase(rs[t][0])
            c = cnt[side][role][ph]
            c['n'] += 1
            for p in pats:
                if flag[p][t]:
                    c[p] += 1
                    if rs[t][1] in pnear:
                        cntp[side][p] += 1
        for p in ('a', 'an', 'a2', 'a2n', 'b', 'c', 'c0', 'd'):
            f = flag[p]
            t = 0
            while t < n:
                if f[t]:
                    u = t
                    while u + 1 < n and f[u + 1]:
                        u += 1
                    seg = rs[t:u + 1]
                    eps.append(dict(p=p, id=i, side=side, role=role, r0=seg[0][0], r1=seg[-1][0], L0=seg[0][6], L1=seg[-1][6],
                                    cells=len(set(r[1] for r in seg)), portal=round(sum(r[1] in pnear for r in seg) / len(seg), 2),
                                    pearl=round(sum(r[2] <= 10 for r in seg) / len(seg), 2), enemy=round(sum(r[3] for r in seg) / len(seg), 2),
                                    eats=sum(r[5] for r in seg), dend=round(sum(r[7] <= 4 for r in seg) / len(seg), 2), xy=(seg[0][1] % W, seg[0][1] // W)))
                    t = u + 1
                else:
                    t += 1
    ev_e = []
    for i, (r, reason, L) in died.items():
        if i in splitr and r - splitr[i] <= 3 and reason in (0, 1, 2):
            ev_e.append(dict(id=i, side=0 if teams[i] == our_team else 1, r=r, split=splitr[i], reason=reason, L=L, new=born.get(i) == splitr[i]))
    nsplit = [0, 0]
    for i, r in born.items():
        nsplit[0 if teams[i] == our_team else 1] += 1
    return dict(W=W, H=H, cells=N, portals=len(portals), walls=nwall, last=rnd, botA=root.text(1), botB=root.text(2), cnt=cnt, cntp=cntp,
                eps=eps, e=ev_e, nsplit=nsplit, dstat=dstat, lc=lc, lex=lex)


def jobs(kind, names):
    out = []
    if kind == 'online':
        for label in names:
            folder = SM / (label + '-old')
            for mp in sorted(folder.glob('game-*.json')):
                j = json.loads(mp.read_text())
                rp = folder / ('M%d.replay' % j['id'])
                if not rp.exists() or 1119 not in (j['teamAId'], j['teamBId']):
                    continue
                out.append(('%s/%d' % (label, j['id']), rp, 0 if j['teamAId'] == 1119 else 1,
                            dict(set=label, ver=label.split('-')[0], gid=j['id'], map=j['mapName'], opp=j['teamBName'] if j['teamAId'] == 1119 else j['teamAName'])))
    else:
        for arm in names:
            for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
                if not (folder / 'result.txt').exists() or not (folder / 'game.replay').exists():
                    continue
                m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
                out.append(('%s/%s' % (arm, folder.name), folder / 'game.replay', int(m[3]),
                            dict(set=arm, ver=arm, gid=folder.name, map=m[1], opp='', result=(folder / 'result.txt').read_text().strip())))
    return out


if __name__ == '__main__':
    kind, names = sys.argv[1], sys.argv[2:]
    for name in names:
        cache_path = HERE / ('rows-%s.jsonl' % name)
        done = set()
        if cache_path.exists():
            done = {json.loads(l)['key'] for l in cache_path.read_text().splitlines()}
        with open(cache_path, 'a') as f:
            for key, rp, team, meta in jobs(kind, [name]):
                if key in done:
                    continue
                try:
                    g = scan(rp, team)
                except Exception as ex:
                    print('FAIL', key, repr(ex), flush=True)
                    continue
                g.update(meta)
                g['key'] = key
                f.write(json.dumps(g, separators=(',', ':')) + '\n')
                f.flush()
        print('done', name, flush=True)
