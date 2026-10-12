# Own count (analyst, run 20261007-1200). Bar F38_mouth (saved in state.json at 11:16, before this file existed).
# One JSON line per main or v31 game. stays: one list per stay of a queen on narrow tiles (a run of consecutive turn starts on
# narrow tiles; narrow = two or fewer sides without kelp, a portal side is open, dragons ignored):
#   [side 0 us 1 them, raw round of the first turn start of the stay, turn starts in the stay,
#    how it ended (0 back on a wider tile, 1 her death, 2 the game ended), mouth]
# mouth = null when the queen had no earlier turn start (the stay begins at her first turn), otherwise the board at her last turn
#   start on a wider tile, the turn in which she stepped in:
#   [raw round, neighbour tiles through open sides, of those narrow, wider neighbours with no dragon body on them (any body tile
#    blocks, her own tail included), narrow neighbours with no dragon body on them, 1 if a head of the other side is within 3 columns
#    and 3 rows (wrapped) of her head, 1 if a pearl lies on a free narrow neighbour, 1 if a pearl lies on a free wider neighbour,
#    her length, 1 if a pearl lies inside the 7 by 7 square round her head on a wider tile (any distance, kelp ignored)]
# Usage: python3 data/analysis/ladder/work/h24_pass.py <shard 0-3>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path

P = '~/01. Project/\u1100\u1162\u110b\u1175\u11ab \u1111\u1173\u1105\u1169\u110c\u1166\u11a8\u1110\u1173/unsw-swarm/data/analysis/ladder/work/'
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
    narrow = set(c for c, out in nxt.items() if len(out) <= 2)
    present = set()
    stays = []
    cur = dict()
    lastwide = dict()
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
                body = bodies[actor]
                qh = body[0]
                if qh in narrow:
                    if s not in cur:
                        cur[s] = [0 if s == 'us' else 1, rnd, 0, 2, lastwide.get(s)]
                    cur[s][2] += 1
                else:
                    if s in cur:
                        st = cur.pop(s)
                        st[3] = 0
                        stays.append(st)
                    occ = set()
                    foe = 0
                    for z, bb in bodies.items():
                        occ.update(bb)
                        if side(z) != s and not foe:
                            h = bb[0]
                            dx = abs(h[0] - qh[0])
                            dy = abs(h[1] - qh[1])
                            if min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3:
                                foe = 1
                    nb = nxt[qh]
                    nn = 0
                    fw = 0
                    fn = 0
                    pn = 0
                    pw = 0
                    for t in nb:
                        isn = t in narrow
                        nn += isn
                        if t not in occ:
                            if isn:
                                fn += 1
                                pn |= int(t in present)
                            else:
                                fw += 1
                                pw |= int(t in present)
                    pv = 0
                    for c in present:
                        if c in narrow:
                            continue
                        dx = abs(c[0] - qh[0])
                        dy = abs(c[1] - qh[1])
                        if min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3:
                            pv = 1
                            break
                    lastwide[s] = [rnd, len(nb), nn, fw, fn, foe, pn, pw, len(body), pv]
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
                if s in cur:
                    st = cur.pop(s)
                    st[3] = 1
                    stays.append(st)
            bodies.pop(i)
    for s in ('us', 'them'):
        if s in cur:
            stays.append(cur.pop(s))
    return dict(game=game, battle=battle, cells=W * H, stays=stays)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    sel = [r for r in rows if r['our_code'] in ('main', 'v31')]
    sel = sel[::-1]
    if shard == 0:
        out = open(P + 'h24-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h24-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h24-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h24-shard3.jsonl', 'w')
    else:
        out = open(P + 'h24-shard-test.jsonl', 'w')
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
    print('shard', shard, 'games written', done)


main()
