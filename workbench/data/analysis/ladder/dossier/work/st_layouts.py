# Scratch (diag-stripes): for every layout, the kelp-closed rooms under 48 tiles (the bot's "pocket"), split into
# loop rooms (a portal edge lies inside the room and leads out), dead-end rooms entered by a portal, dead-end rooms
# entered on foot, sealed rooms; with the share of natural pearl births in each class, and our record.
# Usage: python3 data/analysis/ladder/dossier/work/st_layouts.py [games per layout for the birth count, default 6]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, canonical_edges, edge_id
from collections import Counter, defaultdict, deque
from pathlib import Path

NG = int(sys.argv[1]) if len(sys.argv) > 1 else 6
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
lay = defaultdict(list)
with open('data/analysis/ladder/dossier/per-game.jsonl') as f:
    for line in f:
        r = json.loads(line)
        if r['relation'] == 'us':
            lay[r['layout_key']].append((r['game'], r['replay'], r['our_result'], len(r['all_starting_dragons']['us']),
                                         r['all_starting_dragons']['us'][0]['length']))


def geometry(root):
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    raw = []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    edges = canonical_edges(w, h, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    moves = []
    for y in range(h):
        for x in range(w):
            row = []
            for d in range(4):
                e = edge_id(w, h, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e][0]
                    ry, px = divmod(partner, w + 1)
                    dest = ((ry // 2 - (d == 0)) % h) * w + (px - (d == 3)) % w
                else:
                    dest = ((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w
                row.append((kind, dest))
            moves.append(row)
    comp = [-1] * (w * h)
    size = []
    for c0 in range(w * h):
        if comp[c0] >= 0:
            continue
        n = len(size)
        comp[c0] = n
        q = deque([c0])
        k = 0
        while q:
            c = q.popleft()
            k += 1
            for kind, dest in moves[c]:
                if kind == 0 and comp[dest] < 0:
                    comp[dest] = n
                    q.append(dest)
        size.append(k)
    loop = [0] * len(size)
    door = [0] * len(size)
    for c in range(w * h):
        y, x = divmod(c, w)
        for d in range(4):
            kind, dest = moves[c][d]
            if kind != 2:
                continue
            plain = ((y + STEP[d][1]) % h) * w + (x + STEP[d][0]) % w
            if comp[plain] == comp[c] and comp[dest] != comp[c]:
                loop[comp[c]] = 1
            if comp[dest] != comp[c]:
                door[comp[dest]] += 1
    return w, h, len(portals), comp, size, loop, door


print('layout | size, start | games won | rooms under 48 tiles: loop (sizes) ; dead end by portal (sizes) ; sealed, no portal (sizes) | share of natural births: open area / loop rooms / portal dead ends / sealed (%d games)' % NG)
for key in sorted(lay):
    gs = sorted(lay[key])
    won = sum(g[2] == 'win' for g in gs)
    root = replay.load(Path(gs[0][1])).root()
    w, h, npor, comp, size, loop, door = geometry(root)
    kinds = {}
    for n, s in enumerate(size):
        if s >= 48:
            kinds[n] = 'open'
        elif loop[n]:
            kinds[n] = 'loop'
        elif door[n]:
            kinds[n] = 'dead'
        else:
            kinds[n] = 'sealed'
    births = Counter()
    for g in gs[-NG:]:
        r = replay.load(Path(g[1])).root()
        actor = None
        for ev in r.pointer(3):
            k = ev.u16(0)
            if k == 0:
                actor = None
            elif k == 1:
                actor = ev.pointer(0).i32(0)
            elif k == 3:
                p = ev.pointer(0)
                if p.u32(0) and actor is None:
                    x, y = replay.point(p.pointer(0))
                    births[kinds[comp[y * w + x]]] += 1
    tot = max(1, sum(births.values()))
    desc = []
    for kd in ('loop', 'dead', 'sealed'):
        ss = sorted(size[n] for n in kinds if kinds[n] == kd)
        c = Counter(ss)
        desc.append(', '.join('%dx%d' % (c[s], s) for s in sorted(c)) or '-')
    print('%-22s | %dx%d=%d, %d of L%d, %d portal pairs | %2d %2d | %s ; %s ; %s | %.2f / %.2f / %.2f / %.2f' % (
        key, w, h, w * h, gs[0][3], gs[0][4], npor, len(gs), won, desc[0], desc[1], desc[2],
        births['open'] / tot, births['loop'] / tot, births['dead'] / tot, births['sealed'] / tot))
