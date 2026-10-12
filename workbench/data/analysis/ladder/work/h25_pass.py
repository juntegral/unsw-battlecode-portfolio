# Own count (analyst, run 20261007-1500). Bar F42_hunt (saved in state.json at 12:42, before this file existed) and the carried
# bars F38_new_games_2, F39_new_games_2, F38_long_new. One JSON line per selected main or v31 game.
# Selected: every game after battle 1298211, and every full game (last_round 499) that ends with exactly one queen alive.
# qt: per side, per window (0: raw rounds 0-100, 1: 101-200, 2: 201-300, 3: 301+): [queen turn starts, of those on a narrow tile].
# hunt: per side s (s is the lone queen, the other queen died in an earlier event): [turn starts as the only queen,
#   A: of those with a head of the other side of length 4 or less within 6 path steps of her head (kelp and portals respected,
#      dragons ignored), B: with a head of the other side of ANY length within 6 path steps, short head within 2 path steps,
#   any head within 2 path steps, sum of her length over those turn starts, sum of the number of other-side heads within 6,
#   B with a head of length 5 or more only (no short one within 6)].
# qdead: raw round each queen died. stays: [side 0 us 1 them, raw round of the first turn start of a run of turn starts on narrow
#   tiles, turn starts in the run, how it ended (0 back on a wider tile, 1 her death, 2 the game ended)].
# Usage: python3 data/analysis/ladder/work/h25_pass.py <shard 0-3>
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

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    qids = (queens['us'], queens['them'])
    nxt = build_nxt(W, H, raw)
    narrow = set(c for c, out in nxt.items() if len(out) <= 2)
    qdead = dict()
    qt = dict(us=[[0, 0] for _ in range(4)], them=[[0, 0] for _ in range(4)])
    hunt = dict(us=[0] * 8, them=[0] * 8)
    stays = []
    cur = dict()
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
                w = win(rnd)
                isn = qh in narrow
                qt[s][w][0] += 1
                if isn:
                    qt[s][w][1] += 1
                    if s not in cur:
                        cur[s] = [0 if s == 'us' else 1, rnd, 0, 2]
                    cur[s][2] += 1
                elif s in cur:
                    st = cur.pop(s)
                    st[3] = 0
                    stays.append(st)
                if o in qdead:
                    dist = bfs(nxt, qh, 6)
                    s6 = a6 = s2 = a2 = 0
                    for z, bb in bodies.items():
                        if side(z) != o:
                            continue
                        dd = dist.get(bb[0])
                        if dd is None:
                            continue
                        L = len(bb)
                        a6 += 1
                        if L <= 4:
                            s6 += 1
                        if dd <= 2:
                            a2 += 1
                            if L <= 4:
                                s2 += 1
                    t = hunt[s]
                    t[0] += 1
                    t[1] += s6 > 0
                    t[2] += a6 > 0
                    t[3] += s2 > 0
                    t[4] += a2 > 0
                    t[5] += len(body)
                    t[6] += a6
                    t[7] += (a6 > 0 and s6 == 0)
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
                s = side(i)
                qdead[s] = rnd
                if s in cur:
                    st = cur.pop(s)
                    st[3] = 1
                    stays.append(st)
            bodies.pop(i)
    for s in ('us', 'them'):
        if s in cur:
            stays.append(cur.pop(s))
    return dict(game=game, battle=battle, cells=W * H, qdead=qdead, qt=qt, hunt=hunt, stays=stays)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31') and (r['battle'] > 1298211 or (
        r['last_round'] == 499 and r['queens_at_end'] in ('only theirs', 'only ours')))]
    sel = sel[::-1]
    if shard == 0:
        out = open(P + 'h25-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h25-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h25-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h25-shard3.jsonl', 'w')
    else:
        out = open(P + 'h25-shard-test.jsonl', 'w')
        sel = sel[:3]
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
