# Own count (analyst, run 20261007-0400). One JSON line per main or v31 game.
# rams: every cross-team head-on in which the stationary victim is a queen, with the board at her last own turn before it
#   (rammer head and length then, path distance rammer head to her head before and after her last move, her legal single steps,
#   how many of them end farther from the rammer than its free steps, heads of each side within 5 tiles at the ram).
# births: natural pearl births by [hundred of the birth round (0-4), our gap bin, their gap bin, balance] to [eaten by us, by them, never].
#   Gap = wrapped Manhattan distance from the birth tile to the nearest head of that side. Bins 0: 0-3, 1: 4-6, 2: 7-12, 3: 13+.
#   Balance 2 = dragon counts within 10 percent, 1 = within 1.5 times, 0 = neither.
# contested: births within 6 of both sides by [who is nearer 0 ours 1 tie 2 theirs, nearest dragon length 0 ours longer 1 equal 2 theirs longer,
#   balance, window 0 r0-100 1 r101-300 2 r301+] to the same three counts.
# Usage: python3 data/analysis/ladder/work/h4_pass.py <shard 0-3>
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


def gbin(g):
    return 0 if g <= 3 else 1 if g <= 6 else 2 if g <= 12 else 3


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


def study(r):
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

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(min(dx, W - dx), min(dy, H - dy))

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    qids = (queens['us'], queens['them'])
    nxt = None
    snap = dict()
    qdead = dict()
    rams = []
    tile = dict()
    table = defaultdict(lambda: [0, 0, 0])
    ctable = defaultdict(lambda: [0, 0, 0])
    rnd = 0
    actor = None
    indrop = False
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k != 'tileChange':
            indrop = False
        if k == 'roundStart':
            rnd = p.i32(0)
            actor = None
        elif k == 'turnStart':
            actor = p.i32(0)
            if actor in qids and actor in bodies:
                snap[side(actor)] = (rnd, bodies[actor][0], dict((z, (bb[0], len(bb))) for z, bb in bodies.items()), set(c for bb in bodies.values() for c in bb))
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                if indrop:
                    tile[c] = None
                else:
                    bu = (99, 0)
                    bt = (99, 0)
                    nu = 0
                    nt = 0
                    for z, bb in bodies.items():
                        h = bb[0]
                        dx = abs(h[0] - c[0])
                        dy = abs(h[1] - c[1])
                        g = (min(dx, W - dx) + min(dy, H - dy), -len(bb))
                        if teams[z] == ours:
                            nu += 1
                            if g < bu:
                                bu = g
                        else:
                            nt += 1
                            if g < bt:
                                bt = g
                    bal = 0 if (nu == 0 or nt == 0) else 2 if (nu <= 1.1 * nt and nt <= 1.1 * nu) else 1 if (nu <= 1.5 * nt and nt <= 1.5 * nu) else 0
                    key = (min(rnd // 100, 4), gbin(bu[0]), gbin(bt[0]), bal)
                    ckey = None
                    if bu[0] <= 6 and bt[0] <= 6:
                        cmp = 0 if bu[0] < bt[0] else 1 if bu[0] == bt[0] else 2
                        lu = -bu[1]
                        lt = -bt[1]
                        lcmp = 0 if lu > lt else 1 if lu == lt else 2
                        ckey = (cmp, lcmp, bal, 0 if rnd <= 100 else 1 if rnd <= 300 else 2)
                    tile[c] = (key, ckey)
            else:
                kk = tile.pop(c, None)
                if kk is not None and actor in teams:
                    w = 0 if teams[actor] == ours else 1
                    table[kk[0]][w] += 1
                    if kk[1] is not None:
                        ctable[kk[1]][w] += 1
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif k == 'dragonSplit':
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 'dragonDeath':
            i = p.i32(0)
            reason = p.u16(4)
            if reason == 3 and i != actor and i in qids and actor in bodies and side(actor) != side(i):
                s = side(i)
                o = 'them' if s == 'us' else 'us'
                qh1 = bodies[i][0]
                rec = dict(round=rnd, victim=s, qlen=len(bodies[i]), rlen=len(bodies[actor]), other_queen_dead=o in qdead, other_queen_death=qdead.get(o))
                rec['friends5'] = sum(1 for z, bb in bodies.items() if z != i and side(z) == s and gap(bb[0], qh1) <= 5)
                rec['foes5'] = sum(1 for z, bb in bodies.items() if z != actor and side(z) == o and gap(bb[0], qh1) <= 5)
                rec['friends_alive'] = sum(1 for z in bodies if z != i and side(z) == s)
                rec['foes_alive'] = sum(1 for z in bodies if side(z) == o)
                sn = snap.get(s)
                if sn is None:
                    rec['note'] = 'no turn before the ram'
                elif actor not in sn[2]:
                    rec['note'] = 'rammer born after her last turn'
                    rec['same_round'] = sn[0] == rnd
                else:
                    if nxt is None:
                        nxt = build_nxt(W, H, raw)
                    R, L0 = sn[2][actor]
                    qh0 = sn[1]
                    dist = bfs(nxt, R, 14)
                    reach = (L0 + 3) // 4
                    d1 = dist.get(qh1, 99)
                    legal = set(t for t in nxt[qh0] if t not in sn[3])
                    rec['same_round'] = sn[0] == rnd
                    rec['rlen0'] = L0
                    rec['reach'] = reach
                    rec['d0'] = dist.get(qh0, 99)
                    rec['d1'] = d1
                    rec['moved'] = qh0 != qh1
                    rec['legal'] = len(legal)
                    rec['esc_free'] = sum(1 for t in legal if dist.get(t, 99) > reach)
                    rec['esc_actual'] = sum(1 for t in legal if dist.get(t, 99) > max(reach, d1))
                    rec['cheb0'] = cheb(R, qh0)
                    rec['cheb_friend'] = min(cheb(R, hh[0]) for z, hh in sn[2].items() if side(z) == s)
                    rec['foes5_then'] = sum(1 for z, hh in sn[2].items() if side(z) == o and gap(hh[0], qh0) <= 5)
                    rec['friends5_then'] = sum(1 for z, hh in sn[2].items() if z != i and side(z) == s and gap(hh[0], qh0) <= 5)
                rams.append(rec)
            if i in qids:
                qdead[side(i)] = rnd
            bodies.pop(i)
            indrop = True
    for c, kk in tile.items():
        if kk is not None:
            table[kk[0]][2] += 1
            if kk[1] is not None:
                ctable[kk[1]][2] += 1
    return dict(game=game, battle=battle, rams=rams, births=[list(k) + v for k, v in table.items()], contested=[list(k) + v for k, v in ctable.items()])


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h4-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h4-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h4-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h4-shard3.jsonl', 'w')
    else:
        out = open(P + 'h4-shard-test.jsonl', 'w')
        sel = sel[-3:]
    done = 0
    for k, r in enumerate(sel):
        if shard < N and k % N != shard:
            continue
        try:
            rec = study(r)
        except Exception as e:
            rec = dict(game=r['game'], battle=r['battle'], error='%s: %s' % (type(e).__name__, e))
        out.write(json.dumps(rec) + '\n')
        out.flush()
        done += 1
    out.close()
    print('shard', shard, 'games written', done)


main()
