# Own count (analyst, run 20261007-1000), bar F39_sight (saved in state.json at 10:11, before this file).
# One JSON line per main or v31 game. At the start of every turn of a lone queen (her opposite number died in an earlier round), raw round
# 100 or later: sight[s] for the lone queen of side s = [0 turns, 1 turns she is seen now (a head of the other side within 3 columns and
#   3 rows, wrapped, of any tile of her body), 2 turns she is fresh (seen at one of her turn starts in the last 20 rounds, now included),
#   3 sum of the other side's dragons of length 4 or less within 12 path steps at fresh turns, 4 the same sum at stale turns,
#   5 sum of the other side's dragons of length 4 or less alive at fresh turns, 6 the same at stale turns,
#   7 fresh turns with at least one short dragon of the other side within 12 path steps, 8 stale turns with at least one,
#   9 turns she has never been seen since she became the only queen].
# Usage: python3 data/analysis/ladder/work/h21_pass.py <shard 0-3>
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
    sight = dict(us=[0] * 10, them=[0] * 10)
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
                if o in qdead:
                    body = bodies[actor]
                    seen = False
                    heads = []
                    for z, bb in bodies.items():
                        if side(z) != o:
                            continue
                        h = bb[0]
                        heads.append((h, len(bb)))
                        if not seen:
                            for c in body:
                                dx = abs(h[0] - c[0])
                                dy = abs(h[1] - c[1])
                                if min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3:
                                    seen = True
                                    break
                    if seen:
                        last_seen[s] = rnd
                    if rnd >= 100:
                        fresh = s in last_seen and rnd - last_seen[s] <= 20
                        dist = bfs(nxt, body[0], 12)
                        short = 0
                        near = 0
                        for h, L in heads:
                            if L <= 4:
                                short += 1
                                near += h in dist
                        t = sight[s]
                        t[0] += 1
                        t[1] += seen
                        t[2] += fresh
                        t[3 if fresh else 4] += near
                        t[5 if fresh else 6] += short
                        t[7 if fresh else 8] += near > 0
                        t[9] += s not in last_seen
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
    return dict(game=game, battle=battle, cells=W * H, sight=sight, qdead=qdead)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h21-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h21-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h21-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h21-shard3.jsonl', 'w')
    else:
        out = open(P + 'h21-shard-test.jsonl', 'w')
        sel = sel[-4:]
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
