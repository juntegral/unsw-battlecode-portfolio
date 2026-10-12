# Own count (analyst, run 20261007-1800). Bars F42_sight and F44_who (saved in state.json by run 1500, before this file existed).
# One JSON line per selected main or v31 game.
# Selected: (a) full games (last_round 499) on free layouts that end with exactly one queen alive: whole game read;
#           (b) every game on a layout of 1200 cells or fewer: raw rounds 0-60 only (unless also in a).
# ho: cross-team head-on meetings in raw rounds 0-60: [raw round, mover side (0 us, 1 them), mover length, victim length,
#     1 if the victim is a queen, 1 if the mover is a queen]. Mover = the dragon whose turn it is when the victim dies with
#     engine reason 3 (the victim death comes first, the mover death second).
# sight (set a only): per side s, where s is the lone queen (the other queen died in an earlier event), her turn starts from
#     raw round 100: [turn starts, fresh, fresh and a head of the other side (any length) within 6 path steps of her head,
#     not fresh and such a head within 6, never seen so far, fresh and a head of length 4 or less within 6,
#     seen at this very turn start].
#     Seen = a head of the other side within 3 columns and 3 rows (wrapped) of any tile of her body, tested at every one of
#     her turn starts from the start of the game. Fresh = seen at one of her turn starts in the last 20 rounds (this one counts).
# qdead: raw round each queen died.
# Usage: python3 data/analysis/ladder/work/h26_pass.py <shard 0-3>
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


def study(r, full):
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
    nxt = build_nxt(W, H, raw) if full else None
    qdead = dict()
    sight = dict(us=[0] * 7, them=[0] * 7)
    last_seen = dict()
    ho = []
    rnd = 0
    actor = -1
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
            if rnd > 60 and not full:
                break
        elif k == 'turnStart':
            actor = p.i32(0)
            if full and actor in qids and actor in bodies:
                s = side(actor)
                o = 'them' if s == 'us' else 'us'
                body = bodies[actor]
                qh = body[0]
                seen = False
                for z, bb in bodies.items():
                    if side(z) != o:
                        continue
                    h = bb[0]
                    for c in body:
                        dx = abs(h[0] - c[0])
                        dy = abs(h[1] - c[1])
                        if min(dx, W - dx) <= 3 and min(dy, H - dy) <= 3:
                            seen = True
                            break
                    if seen:
                        break
                if seen:
                    last_seen[s] = rnd
                if o in qdead and rnd >= 100:
                    dist = bfs(nxt, qh, 6)
                    a6 = s6 = 0
                    for z, bb in bodies.items():
                        if side(z) != o:
                            continue
                        if bb[0] in dist:
                            a6 += 1
                            if len(bb) <= 4:
                                s6 += 1
                    fresh = s in last_seen and rnd - last_seen[s] <= 20
                    t = sight[s]
                    t[0] += 1
                    t[1] += fresh
                    t[2] += (fresh and a6 > 0)
                    t[3] += ((not fresh) and a6 > 0)
                    t[4] += s not in last_seen
                    t[5] += (fresh and s6 > 0)
                    t[6] += seen
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
            if rnd <= 60 and reason == 3 and i != actor and actor in bodies and side(actor) != side(i):
                ho.append([rnd, 0 if side(actor) == 'us' else 1, len(bodies[actor]), len(bodies[i]), int(i in qids), int(actor in qids)])
            if i in qids:
                qdead[side(i)] = rnd
            bodies.pop(i)
    return dict(game=game, battle=battle, cells=W * H, full=int(full), qdead=qdead, sight=sight, ho=ho)


def main():
    shard = int(sys.argv[1])
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    maps = json.loads((D / 'maps.json').read_text())
    sel = []
    for r in rows:
        if r['our_code'] not in ('main', 'v31'):
            continue
        m = maps[r['map_key']]
        full = r['last_round'] == 499 and r['queens_at_end'] in ('only theirs', 'only ours') and not m['queen_spawn_dead_end']
        if full or m['width'] * m['height'] <= 1200:
            sel.append((r, full))
    sel = sel[::-1]
    if shard == 0:
        out = open(P + 'h26-shard0.jsonl', 'w')
    elif shard == 1:
        out = open(P + 'h26-shard1.jsonl', 'w')
    elif shard == 2:
        out = open(P + 'h26-shard2.jsonl', 'w')
    elif shard == 3:
        out = open(P + 'h26-shard3.jsonl', 'w')
    else:
        out = open(P + 'h26-shard-test.jsonl', 'w')
        sel = [x for x in sel if x[1]][:2] + sel[:2]
    done = 0
    for k, (r, full) in enumerate(sel):
        if shard < N and k % N != shard:
            continue
        try:
            rec = study(r, full)
        except Exception as e:
            rec = dict(game=r['game'], battle=r['battle'], error='%s: %s' % (type(e).__name__, e))
        out.write(json.dumps(rec) + '\n')
        out.flush()
        done += 1
    out.close()
    print('shard', shard, 'games written', done, 'of', len(sel))


main()
