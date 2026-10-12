# Own count (analyst, run 20261007-0500). One JSON line per main or v31 game.
# snaps: [round, our heads, their heads, ours within 2 of a busy tile, theirs] at the start of raw rounds 50, 75, 100, ..., 300.
#   Busy tile = 8 or more natural pearl births in that game. Distance = wrapped Manhattan.
# meet: cross-team head-on meetings [round, mover side u or t, victim head within 2 of a busy tile 0/1, mover length, victim length].
# qrams: head-ons in which the stationary victim is a queen, with the board at her last own turn:
#   legal single steps, and how many of them end beyond the reach of every enemy head within 6 tiles of her head (and the rammer).
#   full reach = ceil(L/4) + L - 2, free reach = ceil(L/4); path distance, kelp and portals respected, dragons ignored.
# portal: on layouts with portals, per side [non-queen dragon turns r0-100, portal steps by non-queens r0-100, queen turns r0-100, queen portal steps r0-100].
# sight: on 2-dragon-start layouts, per side [rounds 1-50 counted, rounds with a pearl inside the 7 by 7 square of one of its heads].
# Usage: python3 data/analysis/ladder/work/h9_pass.py <shard 0-3>
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
MARKS = set([50, 75] + list(range(100, 301, 25)))
NEAR = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3) if abs(dx) + abs(dy) <= 2]


def build_nxt(W, H, raw):
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    nxt = dict()
    pnx = dict()
    for y in range(H):
        for x in range(W):
            out = []
            pout = []
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
                    t = ((px - (d == 3)) % W, (row // 2 - (d == 0)) % H)
                    out.append(t)
                    pout.append(t)
                else:
                    out.append(((x + STEP[d][0]) % W, (y + STEP[d][1]) % H))
            nxt[(x, y)] = out
            if pout:
                pnx[(x, y)] = pout
    return nxt, pnx


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


def study(r, two_start, has_portals):
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
    pnx = None
    if has_portals:
        nxt, pnx = build_nxt(W, H, raw)
    births = defaultdict(int)
    present = set()
    held = []
    meet = []
    qrams = []
    snap = dict()
    qdead = dict()
    portal = dict(us=[0, 0, 0, 0], them=[0, 0, 0, 0])
    sight = dict(us=[0, 0], them=[0, 0])
    rnd = 0
    actor = None
    victim = None
    indrop = False
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k != 'tileChange':
            indrop = False
        if k == 'roundStart':
            rnd = p.i32(0)
            actor = None
            victim = None
            if rnd in MARKS:
                held.append((rnd, [bb[0] for z, bb in bodies.items() if teams[z] == ours], [bb[0] for z, bb in bodies.items() if teams[z] != ours]))
            if two_start and 1 <= rnd <= 50:
                for s in ('us', 'them'):
                    heads = [bb[0] for z, bb in bodies.items() if side(z) == s]
                    if heads:
                        sight[s][0] += 1
                        if any(cheb(h, c) <= 3 for h in heads for c in present):
                            sight[s][1] += 1
        elif k == 'turnStart':
            actor = p.i32(0)
            victim = None
            if actor in bodies:
                if actor in qids:
                    snap[side(actor)] = (rnd, bodies[actor][0], dict((z, (bb[0], len(bb))) for z, bb in bodies.items()), set(c for bb in bodies.values() for c in bb))
                if has_portals and rnd <= 100:
                    portal[side(actor)][2 if actor in qids else 0] += 1
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
                if not indrop:
                    births[c] += 1
            else:
                present.discard(c)
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                if has_portals and rnd <= 100:
                    old = b[0]
                    if h in pnx.get(old, ()) and gap(old, h) != 1:
                        portal[side(i)][3 if i in qids else 1] += 1
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
            if reason == 3 and i != actor:
                victim = (i, side(i), bodies[i][0], len(bodies[i]))
                if i in qids and actor in bodies and side(actor) != side(i):
                    s = side(i)
                    o = 'them' if s == 'us' else 'us'
                    rec = dict(round=rnd, victim=s, qlen=len(bodies[i]), rlen=len(bodies[actor]), other_queen_dead=o in qdead)
                    sn = snap.get(s)
                    if sn is None or actor not in sn[2]:
                        rec['board'] = False
                    else:
                        if nxt is None:
                            nxt, pnx = build_nxt(W, H, raw)
                        rec['board'] = True
                        qh0 = sn[1]
                        foes = [(z, hh) for z, hh in sn[2].items() if side(z) == o and (gap(hh[0], qh0) <= 6 or z == actor)]
                        legal = [t for t in nxt[qh0] if t not in sn[3]]
                        full = dict((z, (hh[1] + 3) // 4 + hh[1] - 2) for z, hh in foes)
                        free = dict((z, (hh[1] + 3) // 4) for z, hh in foes)
                        lim = min(40, max(full.values()))
                        n_full = 0
                        n_free = 0
                        n_ram_full = 0
                        n_ram_free = 0
                        for t in legal:
                            dist = bfs(nxt, t, lim)
                            if all(dist.get(hh[0], 99) > min(40, full[z]) for z, hh in foes):
                                n_full += 1
                            if all(dist.get(hh[0], 99) > free[z] for z, hh in foes):
                                n_free += 1
                            dr = dist.get(sn[2][actor][0], 99)
                            if dr > min(40, full[actor]):
                                n_ram_full += 1
                            if dr > free[actor]:
                                n_ram_free += 1
                        rec['legal'] = len(legal)
                        rec['foes6'] = len(foes)
                        rec['safe_full'] = n_full
                        rec['safe_free'] = n_free
                        rec['ram_full'] = n_ram_full
                        rec['ram_free'] = n_ram_free
                        rec['rlen0'] = sn[2][actor][1]
                        rec['maxlen_foe6'] = max(hh[1] for z, hh in foes)
                        rec['friends5_then'] = sum(1 for z, hh in sn[2].items() if z != i and side(z) == s and gap(hh[0], qh0) <= 5)
                    qrams.append(rec)
            elif reason == 3 and i == actor and victim is not None:
                if victim[1] != side(i):
                    meet.append([rnd, side(i)[0], victim[2], len(bodies[i]), victim[3]])
                victim = None
            if i in qids:
                qdead[side(i)] = rnd
            bodies.pop(i)
            indrop = True
    busy8 = set(c for c, n in births.items() if n >= 8)
    zone8 = set(((c[0] + dx) % W, (c[1] + dy) % H) for c in busy8 for dx, dy in NEAR)
    snaps = [[rnd, len(hu), len(ht), sum(1 for h in hu if h in zone8), sum(1 for h in ht if h in zone8)] for rnd, hu, ht in held]
    meet2 = [[m[0], m[1], int(m[2] in zone8), m[3], m[4]] for m in meet]
    return dict(game=game, battle=battle, snaps=snaps, busy8=len(busy8), zone8=len(zone8), meet=meet2, qrams=qrams, portal=portal, sight=sight)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    maps = json.loads((D / 'maps.json').read_text())
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h9-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h9-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h9-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h9-shard3.jsonl', 'w')
    else:
        out = open(P + 'h9-shard-test.jsonl', 'w')
        sel = sel[-10:]
    done = 0
    for k, r in enumerate(sel):
        if shard < N and k % N != shard:
            continue
        m = maps[r['map_key']]
        try:
            rec = study(r, m['dragons_at_spawn'] == 2, m['portals'] > 0)
        except Exception as e:
            rec = dict(game=r['game'], battle=r['battle'], error='%s: %s' % (type(e).__name__, e))
        out.write(json.dumps(rec) + '\n')
        out.flush()
        done += 1
    out.close()
    print('shard', shard, 'games written', done)


main()
