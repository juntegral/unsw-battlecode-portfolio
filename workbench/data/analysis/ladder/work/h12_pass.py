# Own count (analyst, run 20261007-0600, bar F28_queen_step). One JSON line per main or v31 game.
# cases: every queen turn start in raw rounds 0-200 at which the nearest enemy head of length 6 or less is exactly 3 or 4 path steps
#   from her head (kelp and portals respected, dragons ignored; lowest id on ties):
#   [round, queen side u or t, path distance before, result after her turn measured from that same enemy head position
#    (c closer, s same, f farther, d she died in her turn), a legal single step that does not come closer existed 0/1,
#    legal single steps, that enemy length, her length, other queen dead 0/1].
# Usage: python3 data/analysis/ladder/work/h12_pass.py <shard 0-3>
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

    def bfs(src, limit):
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

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    qids = (queens['us'], queens['them'])
    nxt = build_nxt(W, H, raw)
    qdead = set()
    cases = []
    cur = None
    rnd = 0
    actor = None

    def close():
        if cur is not None:
            qi = cur[9]
            if qi in bodies:
                da = cur[10].get(bodies[qi][0], 99)
                cur[3] = 'c' if da < cur[2] else 's' if da == cur[2] else 'f'
            else:
                cur[3] = 'd'
            cases.append(cur[:9])

    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            close()
            cur = None
            rnd = p.i32(0)
            actor = None
        elif k == 'turnStart':
            close()
            cur = None
            actor = p.i32(0)
            if actor in bodies and actor in qids and rnd <= 200:
                s = side(actor)
                o = 'them' if s == 'us' else 'us'
                qh = bodies[actor][0]
                dq = bfs(qh, 4)
                best = None
                for z, bb in bodies.items():
                    if side(z) == o and len(bb) <= 6:
                        d = dq.get(bb[0])
                        if d is not None and (best is None or (d, z) < best[:2]):
                            best = (d, z, bb[0], len(bb))
                if best is not None and best[0] in (3, 4):
                    de = bfs(best[2], 6)
                    occ = set(c for bb in bodies.values() for c in bb)
                    legal = [t2 for t2 in nxt[qh] if t2 not in occ]
                    nonclose = int(any(de.get(t2, 99) >= best[0] for t2 in legal))
                    cur = [rnd, s[0], best[0], '?', nonclose, len(legal), best[3], len(bodies[actor]), int(o in qdead), actor, de]
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
                qdead.add(side(i))
            bodies.pop(i)
    close()
    return dict(game=game, battle=battle, cases=cases)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h12-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h12-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h12-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h12-shard3.jsonl', 'w')
    else:
        out = open(P + 'h12-shard-test.jsonl', 'w')
        sel = sel[-6:]
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
