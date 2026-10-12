# Own count (analyst, run 20261007-0900), bars F37_base_rate and F35_hunt (both saved in state.json at 08:16 and 08:22, before this file).
# One JSON line per main or v31 game. At the start of every queen turn (both queens):
# base: per side, per window (0: raw rounds 0-100, 1: 101-200, 2: 201-300, 3: 301+):
#   [queen turns, turns with a body tile of ANOTHER dragon of her team on a tile next to her head, turns with no free tile next to her head,
#    turns with exactly one free tile, turns with another own dragon next to her head and at most one free tile].
#   "Next to her head" follows portals; a kelp edge is not a tile. Free = no dragon body on it.
# lone: per side, per bin of 50 rounds since her opposite number died (bin 0 = the first 50 rounds, capped at 9):
#   [turns as the only queen, turns with an enemy head of length 4 or less within 6 path steps (kelp and portals respected, dragons ignored),
#    sum of own heads (not hers) within 5 tiles wrapped Manhattan, sum of enemy heads within 6 path steps, turns with no own head within 5 tiles,
#    turns with any enemy head within 6 path steps].
# both: the same six numbers over turns when both queens are alive, per window as in base (a base rate for lone).
# qdead: the round each queen died.
# Usage: python3 data/analysis/ladder/work/h18_pass.py <shard 0-3>
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


def win(rnd):
    return 0 if rnd <= 100 else 1 if rnd <= 200 else 2 if rnd <= 300 else 3


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

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    qids = (queens['us'], queens['them'])
    nxt = build_nxt(W, H, raw)
    qdead = dict()
    base = dict(us=[[0] * 5 for _ in range(4)], them=[[0] * 5 for _ in range(4)])
    both = dict(us=[[0] * 6 for _ in range(4)], them=[[0] * 6 for _ in range(4)])
    lone = dict(us=[[0] * 6 for _ in range(10)], them=[[0] * 6 for _ in range(10)])
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
                qh = bodies[actor][0]
                occ = dict()
                own_heads = 0
                foe_heads = []
                for z, bb in bodies.items():
                    for c in bb:
                        occ[c] = z
                    if z == actor:
                        continue
                    if side(z) == s:
                        if gap(bb[0], qh) <= 5:
                            own_heads += 1
                    else:
                        foe_heads.append((bb[0], len(bb)))
                free = 0
                ally = False
                for t in nxt[qh]:
                    z = occ.get(t)
                    if z is None:
                        free += 1
                    elif z != actor and side(z) == s:
                        ally = True
                bb = base[s][win(rnd)]
                bb[0] += 1
                bb[1] += ally
                bb[2] += free == 0
                bb[3] += free == 1
                bb[4] += ally and free <= 1
                dist = bfs(nxt, qh, 6)
                near = 0
                short = False
                for h, L in foe_heads:
                    if h in dist:
                        near += 1
                        if L <= 4:
                            short = True
                if o in qdead:
                    rr = lone[s][min(9, (rnd - qdead[o]) // 50)]
                else:
                    rr = both[s][win(rnd)]
                rr[0] += 1
                rr[1] += short
                rr[2] += own_heads
                rr[3] += near
                rr[4] += own_heads == 0
                rr[5] += near > 0
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
    return dict(game=game, battle=battle, base=base, both=both, lone=lone, qdead=qdead)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h18-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h18-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h18-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h18-shard3.jsonl', 'w')
    else:
        out = open(P + 'h18-shard-test.jsonl', 'w')
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
