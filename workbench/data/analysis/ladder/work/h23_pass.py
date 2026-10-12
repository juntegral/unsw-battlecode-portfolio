# Own count (analyst, run 20261007-1100). Bars F41_first_meal and F41_straight (saved in state.json at 11:06, before this file existed).
# One JSON line per main or v31 game on a layout where each team starts with 2 dragons. Only raw rounds 0-100 are read.
# t0: the first raw round in which a dragon turn starts with a pearl on the board. d0: per side, the smallest path distance (kelp and
#   portals respected, dragons ignored, searched to 60 steps, null if none) from any of its heads to a pearl at that turn start.
# first: per side, raw round of the first pearl eaten (a tile emptied during a turn of one of its dragons), null if none by raw round 100.
# meals50: per side, pearls eaten in raw rounds 0-50.
# dist: at the first turn start of raw rounds 10, 20, 30, 40, 50: [smallest distance ours, smallest distance theirs] (null if none in 60).
# straight: per side, raw rounds 1-50: [dragon turn starts (length 2 or more), of those with no pearl inside the 7 by 7 square around
#   the head (3 columns and 3 rows, wrapped, kelp ignored), of those the turns in which the head moves by one plain step and the step
#   before was a plain step too, of those the turns whose first step keeps the direction of head minus neck].
# Usage: python3 data/analysis/ladder/work/h23_pass.py <shard 0-3>
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


def near(nxt, srcs, pset):
    if not pset or not srcs:
        return None
    seen = set(srcs)
    for c in srcs:
        if c in pset:
            return 0
    frontier = list(srcs)
    d = 0
    while frontier and d < 60:
        d += 1
        new = []
        for c in frontier:
            for t in nxt[c]:
                if t in seen:
                    continue
                if t in pset:
                    return d
                seen.add(t)
                new.append(t)
        frontier = new
    return None


def unit(a, b, W, H):
    dx = (a[0] - b[0]) % W
    dy = (a[1] - b[1]) % H
    if dx == W - 1:
        dx = -1
    if dy == H - 1:
        dy = -1
    if abs(dx) + abs(dy) != 1:
        return None
    return (dx, dy)


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

    nxt = build_nxt(W, H, raw)
    present = set()
    t0 = None
    d0 = dict(us=None, them=None)
    first = dict(us=None, them=None)
    meals50 = dict(us=0, them=0)
    dist = dict()
    straight = dict(us=[0, 0, 0, 0], them=[0, 0, 0, 0])
    pend = None
    actor = None
    rnd = 0

    def both():
        hs = dict(us=[], them=[])
        for z, bb in bodies.items():
            hs[side(z)].append(bb[0])
        return [near(nxt, hs['us'], present), near(nxt, hs['them'], present)]

    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
            actor = None
            pend = None
            if rnd > 100:
                break
        elif k == 'turnStart':
            actor = p.i32(0)
            pend = None
            if t0 is None and present:
                t0 = rnd
                a = both()
                d0 = dict(us=a[0], them=a[1])
            if rnd in (10, 20, 30, 40, 50) and rnd not in dist:
                dist[rnd] = both()
            if actor in bodies and 1 <= rnd <= 50:
                bb = bodies[actor]
                if len(bb) >= 2:
                    s = side(actor)
                    st = straight[s]
                    st[0] += 1
                    h = bb[0]
                    seen = False
                    for c in present:
                        dx = abs(h[0] - c[0])
                        dy = abs(h[1] - c[1])
                        if min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3:
                            seen = True
                            break
                    if not seen:
                        st[1] += 1
                        prev = unit(h, bb[1], W, H)
                        if prev is not None:
                            pend = (actor, h, prev, s)
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
                if actor in teams:
                    s = side(actor)
                    if first[s] is None:
                        first[s] = rnd
                    if rnd <= 50:
                        meals50[s] += 1
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                if pend is not None and pend[0] == i:
                    step = unit(h, pend[1], W, H)
                    if step is not None:
                        st = straight[pend[3]]
                        st[2] += 1
                        st[3] += step == pend[2]
                    pend = None
                b.appendleft(h)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif k == 'dragonSplit':
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            pend = None
        elif k == 'dragonDeath':
            i = p.i32(0)
            bodies.pop(i)
            if pend is not None and pend[0] == i:
                pend = None
    return dict(game=game, battle=battle, t0=t0, d0=d0, first=first, meals50=meals50, dist=dist, straight=straight, last=rnd)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    maps = json.loads((D / 'maps.json').read_text())
    sel = [r for r in rows if r['our_code'] in ('main', 'v31') and maps[r['map_key']]['dragons_at_spawn'] == 2]
    sel = sel[::-1]
    if shard == 0:
        out = open(P + 'h23-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h23-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h23-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h23-shard3.jsonl', 'w')
    else:
        out = open(P + 'h23-shard-test.jsonl', 'w')
        sel = [r for r in sel if r['game'] in (1298212, 1298211, 1298215)]
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
