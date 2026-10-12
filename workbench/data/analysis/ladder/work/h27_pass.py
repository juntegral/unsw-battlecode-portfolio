# Own count (analyst, run 20261007-1800). Bar F42_sight_head (saved in state.json at 18:10, before this file existed).
# One JSON line per main or v31 full game (last_round 499) on a free layout that ends with exactly one queen alive.
# Per side s, where s is the lone queen (the other queen died in an earlier event), her turn starts from raw round 100.
# Seen = a head of the other side within 3 columns and 3 rows (wrapped) of her HEAD (the bot's rule, main.cpp 1482), tested at
# every one of her turn starts from the start of the game. Age = raw rounds since the last seen turn start.
# age: five classes [0-20, 21-50, 51-100, over 100, never seen]; for each class
#      [turn starts, nearest head of the other side within 6 path steps of her head, within 7 to 12, further or no path].
# now: [seen-now turn starts, of those with a seeing head of length 4 or less, sum of seeing heads, sum of her length over all turns]
# Usage: python3 data/analysis/ladder/work/h27_pass.py <shard 0-3>
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

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    qids = (queens['us'], queens['them'])
    nxt = build_nxt(W, H, raw)
    qdead = dict()
    age = dict(us=[[0, 0, 0, 0] for _ in range(5)], them=[[0, 0, 0, 0] for _ in range(5)])
    now = dict(us=[0, 0, 0, 0], them=[0, 0, 0, 0])
    last_seen = dict()
    rnd = 0
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
        elif k == 'turnStart':
            actor = p.i32(0)
            if actor in qids and actor in bodies:
                s = side(actor)
                o = 'them' if s == 'us' else 'us'
                body = bodies[actor]
                qh = body[0]
                seers = 0
                short_seer = 0
                heads = []
                for z, bb in bodies.items():
                    if side(z) != o:
                        continue
                    h = bb[0]
                    heads.append(h)
                    dx = abs(h[0] - qh[0])
                    dy = abs(h[1] - qh[1])
                    if min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3:
                        seers += 1
                        if len(bb) <= 4:
                            short_seer = 1
                if seers:
                    last_seen[s] = rnd
                if o in qdead and rnd >= 100:
                    dist = bfs(nxt, qh, 12)
                    best = 99
                    for h in heads:
                        dd = dist.get(h)
                        if dd is not None and dd < best:
                            best = dd
                    if s not in last_seen:
                        c = 4
                    else:
                        a = rnd - last_seen[s]
                        c = 0 if a <= 20 else 1 if a <= 50 else 2 if a <= 100 else 3
                    t = age[s][c]
                    t[0] += 1
                    t[1 if best <= 6 else 2 if best <= 12 else 3] += 1
                    n = now[s]
                    n[3] += len(body)
                    if seers:
                        n[0] += 1
                        n[1] += short_seer
                        n[2] += seers
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
            if i in qids:
                qdead[side(i)] = rnd
            bodies.pop(i)
    return dict(game=game, battle=battle, cells=W * H, qdead=qdead, age=age, now=now)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    maps = json.loads((D / 'maps.json').read_text())
    sel = [r for r in rows if r['our_code'] in ('main', 'v31') and r['last_round'] == 499 and r['queens_at_end'] in ('only theirs', 'only ours')
           and not maps[r['map_key']]['queen_spawn_dead_end']]
    sel = sel[::-1]
    if shard == 0:
        out = open(P + 'h27-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h27-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h27-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h27-shard3.jsonl', 'w')
    else:
        out = open(P + 'h27-shard-test.jsonl', 'w')
        sel = sel[:2]
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
    print('shard', shard, 'games written', done, 'of', len(sel))


main()
