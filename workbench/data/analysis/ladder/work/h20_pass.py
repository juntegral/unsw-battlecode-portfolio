# Own count (analyst, run 20261007-1000), bars F38_entry and F39_supply (saved in state.json at 09:15) and F38_pearl (saved 10:03, before this
# file was run). One JSON line per main or v31 game.
# entry: per side, per window (0: raw rounds 0-100, 1: 101-200, 2: 201-300, 3: 301+). A "chance" is a queen turn that starts on a tile with
#   three or more open sides (open = no kelp on that edge, a portal edge is open, dragons ignored) and has at least one neighbour tile that
#   is narrow (two or fewer open sides). Numbers: [0 chances, 1 chances where a narrow neighbour has no dragon body on it, 2 turns that end
#   with her head on a narrow tile (she is alive), 3 turns in which she died, 4 entries where the narrow tile she ends on held a pearl at the
#   turn start, 5 entries where a pearl lay on a neighbouring OPEN tile (three or more sides, no body) at the turn start,
#   6 chances where a narrow neighbour with no body on it held a pearl, 7 of those the turns that end on a narrow tile].
# stay: per side, per window of the entry: [stays begun (first turn start on a narrow tile after a turn start on an open one, or the spawn),
#   queen turn starts spent on narrow tiles in those stays, stays that end with her death, stays that end with her back on an open tile].
# lone: per side s (the lone queen), per phase (0 before grow_round, 1 from it; grow_round 151 if width*height > 1200 else 301):
#   [turns as the only queen, sum of the OTHER side's dragons of length 4 or less alive, sum of those within 12 path steps of her head
#    (kelp and portals respected, dragons ignored), turns with at least one within 12, sum of the other side's dragons alive,
#    sum of those of length 4 or less within 6 path steps].
# Usage: python3 data/analysis/ladder/work/h20_pass.py <shard 0-3>
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
    grow = 151 if W * H > 1200 else 301
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
    present = set()
    qdead = dict()
    entry = dict(us=[[0] * 8 for _ in range(4)], them=[[0] * 8 for _ in range(4)])
    stay = dict(us=[[0] * 4 for _ in range(4)], them=[[0] * 4 for _ in range(4)])
    lone = dict(us=[[0] * 6 for _ in range(2)], them=[[0] * 6 for _ in range(2)])
    pend = dict()
    cur_stay = dict()
    rnd = 0

    def close(s, died):
        pd = pend.pop(s, None)
        q = queens[s]
        if pd is not None:
            w, pearl_n, pearl_o, freepearl = pd
            e = entry[s][w]
            if died:
                e[3] += 1
            elif bodies[q][0] in narrow:
                e[2] += 1
                e[4] += bodies[q][0] in pearl_n
                e[5] += pearl_o
                e[7] += freepearl
        if died and s in cur_stay:
            stay[s][cur_stay.pop(s)][2] += 1

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
                close(s, False)
                qh = bodies[actor][0]
                w = win(rnd)
                if qh in narrow:
                    if s not in cur_stay:
                        cur_stay[s] = w
                        stay[s][w][0] += 1
                    stay[s][cur_stay[s]][1] += 1
                else:
                    if s in cur_stay:
                        stay[s][cur_stay.pop(s)][3] += 1
                    nn = [t for t in nxt[qh] if t in narrow]
                    if nn:
                        occ = set(c for bb in bodies.values() for c in bb)
                        freen = [t for t in nn if t not in occ]
                        pearl_n = set(t for t in freen if t in present)
                        pearl_o = int(any(t in present and t not in occ and t not in narrow for t in nxt[qh]))
                        e = entry[s][w]
                        e[0] += 1
                        e[1] += bool(freen)
                        e[6] += bool(pearl_n)
                        pend[s] = (w, pearl_n, pearl_o, int(bool(pearl_n)))
                if o in qdead:
                    dist = bfs(nxt, qh, 12)
                    ph = 0 if rnd < grow else 1
                    rr = lone[s][ph]
                    short = 0
                    near = 0
                    alive = 0
                    near6 = 0
                    for z, bb in bodies.items():
                        if side(z) != o:
                            continue
                        alive += 1
                        if len(bb) <= 4:
                            short += 1
                            dd = dist.get(bb[0])
                            if dd is not None:
                                near += 1
                                if dd <= 6:
                                    near6 += 1
                    rr[0] += 1
                    rr[1] += short
                    rr[2] += near
                    rr[3] += near > 0
                    rr[4] += alive
                    rr[5] += near6
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
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
                close(s, True)
                qdead[s] = rnd
            bodies.pop(i)
    for s in ('us', 'them'):
        if s not in qdead:
            close(s, False)
    return dict(game=game, battle=battle, cells=W * H, entry=entry, stay=stay, lone=lone, qdead=qdead)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    if shard == 0:
        out = open(P + 'h20-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h20-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h20-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h20-shard3.jsonl', 'w')
    else:
        out = open(P + 'h20-shard-test.jsonl', 'w')
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
