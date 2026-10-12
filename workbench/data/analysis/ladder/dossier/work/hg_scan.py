# Scratch (diag-hungry): the hungry spells of the local m3b7 games (128 replays, both sides, two seeds).
# A spell turn = a turn of one of our dragons of length 2 or 3, rounds 0-300, 26 rounds or more after its last meal
# or birth (the definition of ec_idle.py). For every spell turn one row with what the dragon had around it and, for
# each step on offer, a rebuild of three of the bot's terms on the true board:
#   T   territory: tiles within 12 steps that the dragon reaches before any enemy head in view and no later than any
#       team mate's head in view (main.cpp 2956-2967), weighted 1 pearl / 0.6 spawning / 0.3 barren / 0.5 never seen
#   dp  steps to the nearest pearl in view that counts as a target (2977-2985: no mate nearer, enemy at most 1 nearer)
#   du  steps to the nearest tile this dragon has never had in its 7 by 7 view (memory starts at its birth)
# Also per game: turns, pearls and deaths by rounds-since-meal bucket and view, both sides (the table of 3b).
# Usage: python3 data/analysis/ladder/dossier/work/hg_scan.py <arm dir under solo/runs> <shard> <shards> [limit]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import defaultdict, deque
from pathlib import Path

RUNS = '~/meow-redteam/solo/runs/'
OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
RAD = 12
INF = 1 << 28


def ib(n):
    return 0 if n <= 3 else 1 if n <= 10 else 2 if n <= 25 else 3 if n <= 60 else 4


def edge_id(w, h, x, y, d):
    return (2 * y * (w + 1) + x if d == 0 else (2 * y + 1) * (w + 1) + (x + 1) % w if d == 1
            else 2 * ((y + 1) % h) * (w + 1) + x if d == 2 else (2 * y + 1) * (w + 1) + x)


def build_moves(w, h, raw):
    edges = {}
    for e, k, p in raw:
        row, x = divmod(e, w + 1)
        if row % 2 == 0 and x == w:
            continue
        e = 2 * ((row // 2) % h) * (w + 1) + x if row % 2 == 0 else row * (w + 1) + x % w
        if e not in edges or k > edges[e][0]:
            edges[e] = (k, p)
    portals = defaultdict(list)
    for e, (k, p) in edges.items():
        if k == 2:
            portals[p].append(e)
    moves = []
    for y in range(h):
        for x in range(w):
            row = []
            for d, (dx, dy) in enumerate(STEP):
                e = edge_id(w, h, x, y, d)
                k, pid = edges.get(e, (0, -1))
                if k == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                else:
                    dest = ((y + dy) % h) * w + (x + dx) % w
                row.append((k, dest))
            moves.append(row)
    return moves


def scan(path, our, gi, rows_out):
    root = replay.load(Path(path)).root()
    lines = root.text(0).splitlines()
    w = h = 0
    bodies, teams, raw, barren = {}, {}, [], None
    name = ''
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'MAP':
            w, h = int(q[1]), int(q[2])
            barren = bytearray(w * h)
        elif q[0] == 'MAP_NAME':
            name = ' '.join(q[1:])
        elif q[0] == 'TILE':
            if int(q[3]) == 0 and int(q[4]) == 0:
                barren[int(q[2]) * w + int(q[1])] = 1
        elif q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    N = w * h
    moves = build_moves(w, h, raw)
    adj = [[t for k, t in row if k != 1] for row in moves]
    wins = {}

    def win(c):
        v = wins.get(c)
        if v is None:
            y, x = divmod(c, w)
            v = frozenset(((y + dy) % h) * w + (x + dx) % w for dy in range(-3, 4) for dx in range(-3, 4))
            wins[c] = v
        return v

    sd = {i: 0 if teams[i] == our else 1 for i in bodies}
    fed = {i: 0 for i in bodies}
    born = {i: 0 for i in bodies}
    seen = {i: bytearray(N) for i in bodies if sd[i] == 0}
    unseen = {i: set(range(N)) for i in bodies if sd[i] == 0}
    present = set()
    pv = [0] * N
    acc = defaultdict(lambda: [0, 0, 0])
    last = {}
    cur = None
    rnd, actor = 0, None
    alive = [0, 0]
    for i in bodies:
        alive[sd[i]] += 1
    eaten300 = [0, 0]
    deaths = defaultdict(int)

    def analyse(i, b):
        head = b[0]
        L = len(b)
        wn = win(head)
        other = set()
        mates, foes = [], []
        for j, bb in bodies.items():
            if j == i:
                continue
            for t in bb:
                if t in wn:
                    other.add(t)
            if bb[0] in wn:
                (mates if sd[j] == 0 else foes).append(bb[0])
        own = {t: L - off + 1 for off, t in enumerate(b)}
        sn = seen[i]
        # S: tiles within RAD steps of the head, bodies in view shut
        S = {head: 0}
        q = [head]
        for t in q:
            s = S[t]
            if s >= RAD:
                continue
            for nb in adj[t]:
                if nb not in S and nb not in other and nb not in own:
                    S[nb] = s + 1
                    q.append(nb)

        def flood(srcs):
            dist = {m: 0 for m in srcs}
            qq = list(srcs)
            for t in qq:
                s = dist[t]
                for nb in adj[t]:
                    if nb in S and nb not in dist and nb != head:
                        dist[nb] = s + 1
                        qq.append(nb)
            return dist

        ally = flood(mates) if mates else {}
        rival = flood(foes) if foes else {}
        pearls = [t for t in wn if t in present]
        n_t = n_m = n_e = n_w = 0
        best_t = best_m = None
        for p in pearls:
            dm = S.get(p)
            if dm is None:
                n_w += 1
            elif ally.get(p, INF) < dm:
                n_m += 1
                if best_m is None or dm < best_m[0]:
                    best_m = (dm, ally[p])
            elif dm > rival.get(p, INF) + 1:
                n_e += 1
            else:
                n_t += 1
                if best_t is None or dm < best_t[0]:
                    best_t = (dm, p)
        room = -1
        if best_t is not None:
            cap = 3 * L + 9
            st = {best_t[1]}
            qq = [best_t[1]]
            for t in qq:
                if len(st) >= cap:
                    break
                for nb in adj[t]:
                    if nb not in st and nb not in other and nb != head:
                        st.add(nb)
                        qq.append(nb)
            room = min(len(st), cap)
        # nearest never-seen tile: reverse flood from this dragon's unseen set, bodies in view shut
        dests = []
        for d in range(4):
            k, dest = moves[head][d]
            dests.append(None if k == 1 or dest in other or dest in own else (k, dest))
        out = []
        for d in range(4):
            if dests[d] is None:
                out.append(None)
                continue
            k, dest = dests[d]
            st = {dest: 1}
            qq = [dest]
            for t in qq:
                s = st[t]
                for nb in adj[t]:
                    if nb in st or nb in other:
                        continue
                    if nb in own:
                        if s + 1 < own[nb]:
                            continue
                    elif nb not in S:
                        continue
                    st[nb] = s + 1
                    qq.append(nb)
            T = Tc = 0.0
            rm = 0.0
            for x, s in st.items():
                wgt = 0.5 if not sn[x] else 1.0 if x in present else 0.3 if barren[x] else 0.6
                rm += 1.0 if sn[x] else 0.5
                th = rival.get(x, INF)
                share = 1.0 if s < th else 0.5 if s == th else 0.0
                if ally.get(x, INF) < s:
                    share = 0.0
                T += share * wgt
                Tc += share
            dp = -1
            for p in pearls:
                s = st.get(p)
                if s is not None and s <= rival.get(p, INF) + 1 and ally.get(p, INF) >= s:
                    if dp < 0 or s < dp:
                        dp = s
            dun = -1
            for x, s in st.items():
                if not sn[x] and (dun < 0 or s - 1 < dun):
                    dun = s - 1
            out.append([round(T, 1), round(Tc, 1), round(rm, 1), dp, dun, 1 if k == 2 else 0])
        un = unseen[i]
        need = {dests[d][1] for d in range(4) if dests[d] is not None and out[d][4] < 0}
        if un and need:
            dist = {}
            qq = []
            for t in un:
                if t not in other:
                    dist[t] = 0
                    qq.append(t)
            left = len(need)
            for t in qq:
                if left <= 0:
                    break
                s = dist[t]
                if s >= 80:
                    break
                for nb in adj[t]:
                    if nb not in dist and nb not in other:
                        dist[nb] = s + 1
                        qq.append(nb)
                        if nb in need:
                            left -= 1
            for d in range(4):
                if dests[d] is not None and out[d][4] < 0:
                    out[d][4] = dist.get(dests[d][1], -1)
        return dict(g=gi, i=i, r=rnd, L=L, idle=rnd - fed[i], age=rnd - born[i], h=head, np=len(pearls), nm=len(mates), ne=len(foes),
                    nt=n_t, nmn=n_m, nen=n_e, nw=n_w, bt=[best_t[0], room] if best_t else None,
                    bm=list(best_m) if best_m else None, box=len(S) if len(S) < 12 else 12, un=len(un),
                    al=alive[0], dirs=out, path=[], ate=0, died=-1)

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd, actor = p.i32(0), None
            cur = None
        elif k == 1:
            actor = p.i32(0)
            cur = None
            b = bodies.get(actor)
            last.pop(actor, None)
            if b is None or rnd > 300:
                continue
            s = sd[actor]
            if s == 0:
                sn = seen[actor]
                un = unseen[actor]
                for t in win(b[0]):
                    if not sn[t]:
                        sn[t] = 1
                        un.discard(t)
            if len(b) > 3:
                continue
            idle = rnd - fed[actor]
            key = (s, 0 if rnd <= 100 else 1 if rnd <= 200 else 2, ib(idle), 1 if pv[b[0]] else 0)
            v = acc[key]
            v[0] += 1
            last[actor] = v
            if s == 0 and idle >= 26:
                cur = analyse(actor, b)
                rows_out.append(cur)
        elif k == 3:
            t = replay.point(p.pointer(0))
            c = t[1] * w + t[0]
            if p.u32(0):
                present.add(c)
                for z in win(c):
                    pv[z] += 1
            else:
                present.discard(c)
                for z in win(c):
                    pv[z] -= 1
                v = last.get(actor)
                if v is not None:
                    v[1] += 1
                if rnd <= 300:
                    eaten300[sd[actor]] += 1
                if cur is not None:
                    cur['ate'] = 1
                fed[actor] = rnd
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            tl = replay.point(p.pointer(1))
            hd, tl = hd[1] * w + hd[0], tl[1] * w + tl[0]
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if cur is not None and i == actor:
                    cur['path'].append(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            a, c = p.i32(0), p.i32(4)
            sd[c] = sd[a]
            alive[sd[a]] += 1
            for zz, i in enumerate((a, c)):
                bodies[i] = deque(q[1] * w + q[0] for q in (replay.point(x) for x in p.pointer(zz)))
            fed[c] = rnd
            fed[a] = rnd
            born[c] = rnd
            if sd[c] == 0:
                seen[c] = bytearray(N)
                unseen[c] = set(range(N))
        elif k == 11:
            i = p.i32(0)
            v = last.pop(i, None)
            if v is not None:
                v[2] += 1
            if rnd <= 300:
                deaths[(sd[i], p.u16(4), 1 if len(bodies[i]) <= 3 else 0)] += 1
            if cur is not None and i == actor:
                cur['died'] = p.u16(4)
            elif sd[i] == 0:
                for rr in reversed(rows_out):
                    if rr['g'] != gi or rr['r'] < rnd - 1:
                        break
                    if rr['i'] == i and rr['died'] < 0:
                        rr['died'] = 10 + p.u16(4)
                        break
            alive[sd[i]] -= 1
            bodies.pop(i)
            if sd[i] == 0:
                seen.pop(i, None)
                unseen.pop(i, None)
    end = root.pointer(4)
    return dict(w=w, h=h, name=name, rounds=rnd, winner=end.u16(6) if end.u16(4) == 1 else -1, end_reason=end.u16(2),
                eaten300=eaten300, acc=[list(kk) + v for kk, v in sorted(acc.items())],
                deaths=[list(kk) + [v] for kk, v in sorted(deaths.items())])


def save(tag, body):
    if tag == 'm3b7-0':
        Path(OUT + 'hg_scan-m3b7-0.jsonl').write_text(body)
    elif tag == 'm3b7-1':
        Path(OUT + 'hg_scan-m3b7-1.jsonl').write_text(body)
    elif tag == 'm3b7-2':
        Path(OUT + 'hg_scan-m3b7-2.jsonl').write_text(body)
    elif tag == 'm3b7-3':
        Path(OUT + 'hg_scan-m3b7-3.jsonl').write_text(body)
    else:
        Path(OUT + 'hg_scan-test.jsonl').write_text(body)


def main():
    arm, shard, shards = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    games = sorted(d.name for d in Path(RUNS + arm).iterdir() if (d / 'game.replay').is_file())
    todo = [(n, g) for n, g in enumerate(games) if n % shards == shard]
    if limit:
        todo = todo[::max(1, len(todo) // limit)][:limit]
    out, bad = [], []
    for z, (n, g) in enumerate(todo):
        our = int(g.rsplit('side', 1)[1])
        rows = []
        try:
            summ = scan(RUNS + arm + '/' + g + '/game.replay', our, n, rows)
        except Exception as e:
            bad.append((g, repr(e)[:300]))
            continue
        summ.update(game=g, gi=n, our=our)
        out.append(json.dumps(dict(kind='game', **summ), separators=(',', ':')))
        for r in rows:
            out.append(json.dumps(r, separators=(',', ':')))
        print(z + 1, len(todo), g, len(rows), 'bad', len(bad), flush=True)
    save('test' if limit else arm + '-' + str(shard), '\n'.join(out) + '\n')
    print('done', arm, shard, len(todo), 'bad', bad)


main()
