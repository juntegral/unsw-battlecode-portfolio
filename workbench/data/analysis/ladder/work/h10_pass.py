# Own count (analyst, run 20261007-0600). One JSON line per main or v31 game.
# reach: per queen side (us = our queen against their heads, them = their queen against our heads), per window (0: raw rounds 0-200, 1: 201+)
#   [queen turns, exposed full, exposed free, exposed full to a head of length 4 or less, exposed free to such a head,
#    queen turns with the other queen dead, exposed full among those].
#   Exposed full = at her turn start an enemy head is within min(12, ceil(L/4) + L - 2) path steps of her head (kelp and portals respected,
#   dragons ignored), L = that enemy length. Exposed free = within ceil(L/4).
# conv: natural pearl births with a head of both sides within 6 tiles (wrapped Manhattan), one side strictly nearer, that were eaten:
#   [nearer side 0 ours 2 theirs, eater side 0 us 1 them, what the nearer side nearest dragon did by its next completed turn
#    (pre = pearl eaten before that turn ended, dead, far, same, near), eater was the nearest dragon of its side at the birth 0/1,
#    eater had made more steps in the eating turn than its free steps 0/1, rounds from birth to meal bin (0, 1, 2, 3 = 3-5, 4 = 6+),
#    window 0 r0-100 1 r101-300 2 r301+, count].
# Usage: python3 data/analysis/ladder/work/h10_pass.py <shard 0-3>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/work/'
D = Path('data/analysis/ladder')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
N = 4
CAP = 12


def build_nxt(W, H, raw):
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    nxt = dict()
    for y in range(H):
        for x in range(W):
            out = []
            for d in range(4):
                e = edge_id(W, H, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e]
                    if len(partner) != 1:
                        continue
                    row, px = divmod(partner[0], W + 1)
                    out.append(((px - (d == 3)) % W, (row // 2 - (d == 0)) % H))
                else:
                    out.append(((x + STEP[d][0]) % W, (y + STEP[d][1]) % H))
            nxt[(x, y)] = out
    return nxt


def bfs(nxt, src, limit):
    dist = dict()
    dist[src] = 0
    frontier = [src]
    d = 0
    while frontier and d < limit:
        d += 1
        new = []
        for c in frontier:
            for t in nxt[c]:
                if t not in dist:
                    dist[t] = d
                    new.append(t)
        frontier = new
    return dist


def study(r, has_portals):
    battle, game = r['battle'], r['game']
    folder = Path('data/online/ladder') / str(battle)
    j = json.loads((folder / ('game-%d.json' % game)).read_text())
    root = replay.load(folder / ('M%d.replay' % game)).root()
    text = root.text(0)
    W, H = map(int, text.splitlines()[0].split()[1:3])
    bodies = dict()
    teams = dict()
    raw = []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    ours = 'A' if j['teamAId'] == 1119 else 'B'

    def side(i):
        return 'us' if teams[i] == ours else 'them'

    def gap(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    qids = (queens['us'], queens['them'])
    nxt = build_nxt(W, H, raw)
    qdead = dict()
    reach = dict(us=[[0] * 7, [0] * 7], them=[[0] * 7, [0] * 7])
    pend = dict()
    watch = defaultdict(list)
    conv = defaultdict(int)
    rnd = 0
    actor = None
    tc = 0
    steps = 0
    free_now = 0
    indrop = False

    def turn_end():
        if actor is None or actor not in watch:
            return
        keep = []
        for c in watch.pop(actor):
            pc = pend.get(c)
            if pc is None or pc['nid'] != actor or pc['after'] is not None:
                continue
            if pc['tc'] == tc:
                keep.append(c)
            elif actor in bodies:
                pc['after'] = gap(bodies[actor][0], c)
        if keep:
            watch[actor] = keep

    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k != 'tileChange':
            indrop = False
        if k == 'roundStart':
            turn_end()
            rnd = p.i32(0)
            actor = None
        elif k == 'turnStart':
            turn_end()
            actor = p.i32(0)
            tc += 1
            steps = 0
            if actor in bodies:
                free_now = (len(bodies[actor]) + 3) // 4
                if actor in qids:
                    s = side(actor)
                    o = 'them' if s == 'us' else 'us'
                    rr = reach[s][0 if rnd <= 200 else 1]
                    rr[0] += 1
                    lone = o in qdead
                    if lone:
                        rr[5] += 1
                    qh = bodies[actor][0]
                    foes = [(bb[0], len(bb)) for z, bb in bodies.items() if side(z) == o]
                    if not has_portals:
                        foes = [f for f in foes if gap(f[0], qh) <= CAP]
                    if foes:
                        dist = bfs(nxt, qh, CAP)
                        ef = False
                        er = False
                        sf = False
                        sr = False
                        for h, L in foes:
                            d = dist.get(h)
                            if d is None:
                                continue
                            fr = (L + 3) // 4
                            if d <= min(CAP, fr + L - 2):
                                ef = True
                                if L <= 4:
                                    sf = True
                            if d <= fr:
                                er = True
                                if L <= 4:
                                    sr = True
                        rr[1] += ef
                        rr[2] += er
                        rr[3] += sf
                        rr[4] += sr
                        if lone:
                            rr[6] += ef
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pend.pop(c, None)
                if not indrop:
                    bu = (99, 0)
                    bt = (99, 0)
                    for z, bb in bodies.items():
                        h = bb[0]
                        dx = abs(h[0] - c[0])
                        dy = abs(h[1] - c[1])
                        g = (min(dx, W - dx) + min(dy, H - dy), z)
                        if teams[z] == ours:
                            if g < bu:
                                bu = g
                        elif g < bt:
                            bt = g
                    if bu[0] <= 6 and bt[0] <= 6 and bu[0] != bt[0]:
                        cmp = 0 if bu[0] < bt[0] else 2
                        nid = bu[1] if cmp == 0 else bt[1]
                        pend[c] = dict(cmp=cmp, nid=nid, d0=min(bu[0], bt[0]), nu=bu[1], nt=bt[1], rnd=rnd, tc=tc, after=None)
                        watch[nid].append(c)
            else:
                pc = pend.pop(c, None)
                if pc is not None and actor in teams:
                    w = 0 if teams[actor] == ours else 1
                    a = pc['after']
                    if a is None:
                        st = 'pre'
                    elif a == 'dead':
                        st = 'dead'
                    elif a > pc['d0']:
                        st = 'far'
                    elif a == pc['d0']:
                        st = 'same'
                    else:
                        st = 'near'
                    isn = int(actor == (pc['nu'] if w == 0 else pc['nt']))
                    dt = rnd - pc['rnd']
                    conv[(pc['cmp'], w, st, isn, int(steps > free_now), dt if dt <= 2 else 3 if dt <= 5 else 4, 0 if pc['rnd'] <= 100 else 1 if pc['rnd'] <= 300 else 2)] += 1
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                b.appendleft(h)
                if i == actor:
                    steps += 1
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif k == 'dragonSplit':
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 'dragonDeath':
            i = p.i32(0)
            if i in qids:
                qdead[side(i)] = rnd
            if i in watch:
                for c in watch.pop(i):
                    pc = pend.get(c)
                    if pc is not None and pc['nid'] == i and pc['after'] is None:
                        pc['after'] = 'dead'
            bodies.pop(i)
            indrop = True
    return dict(game=game, battle=battle, reach=reach, conv=[list(k) + [v] for k, v in conv.items()])


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    maps = json.loads((D / 'maps.json').read_text())
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h10-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h10-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h10-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h10-shard3.jsonl', 'w')
    else:
        out = open(P + 'h10-shard-test.jsonl', 'w')
        sel = sel[-6:]
    done = 0
    for k, r in enumerate(sel):
        if shard < N and k % N != shard:
            continue
        m = maps[r['map_key']]
        try:
            rec = study(r, m['portals'] > 0)
        except Exception as e:
            rec = dict(game=r['game'], battle=r['battle'], error='%s: %s' % (type(e).__name__, e))
        out.write(json.dumps(rec) + '\n')
        out.flush()
        done += 1
    out.close()
    print('shard', shard, 'games written', done)


main()
