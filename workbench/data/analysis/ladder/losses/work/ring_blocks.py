# Scratch (queen-ring brief, question 3): how many 6 by 4 blocks a queen could use on the 19 ladder layouts.
# Open block = 24 tiles with no kelp and no portal on any edge between two of them (the outline may touch anything).
# Spawn tiles = tiles on which a natural pearl was ever born in any observed game of the layout (a lower bound).
# strict = open block with no spawn tile; relaxed = open block whose four turn-end free tiles (one of the two mirror
# placements of the cycle) are not spawn tiles. Distance = path steps (portals pass) from a queen's spawn head.
# Reads map-observations.json, rows.jsonl; prints.
import json
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import canonical_edges, edge_id
from collections import defaultdict, deque
from pathlib import Path
from statistics import median

ROOT = Path('data/analysis/ladder')
rows = [json.loads(line) for line in (ROOT / 'rows.jsonl').read_text().splitlines()]
obs = json.loads((ROOT / 'map-observations.json').read_text())
key_of = {str(r['game']): r['map_key'] for r in rows}
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
FREE = (((1, 1), (2, 2), (3, 1), (4, 2)), ((1, 2), (2, 1), (3, 2), (4, 1)))

by = defaultdict(list)
for gid, o in obs.items():
    if gid in key_of:
        by[key_of[gid]].append(o)

tot = dict(layouts=0, strict=0, relaxed=0)
print('layout | cells | games | never-spawn tile share | open blocks | strict | relaxed | tiles inside some strict block | queen spawn to nearest strict block (steps)')
for key in sorted(by):
    group = by[key]
    text = group[0]['text']
    W = H = 0
    raw, queens, seen_team = [], [], set()
    for line in text.splitlines():
        q = line.split()
        if not q:
            continue
        if q[0] == 'MAP':
            W, H = int(q[1]), int(q[2])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
        elif q[0] == 'DRAGON' and q[1] not in seen_team:
            seen_team.add(q[1])
            queens.append((int(q[3]), int(q[4])))
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    spawn = set()
    for o in group:
        for t in o['natural']:
            x, y = t.split(',')
            spawn.add((int(x), int(y)))

    def kind(x, y, d):
        return edges.get(edge_id(W, H, x, y, d), (0, -1))[0]

    def dest(x, y, d):
        e = edge_id(W, H, x, y, d)
        k, pid = edges.get(e, (0, -1))
        if k == 1:
            return None
        if k == 2:
            partner = [z for z in portals[pid] if z != e][0]
            row, px = divmod(partner, W + 1)
            return ((px - (d == 3)) % W, (row // 2 - (d == 0)) % H)
        return ((x + STEP[d][0]) % W, (y + STEP[d][1]) % H)

    n_open = n_strict = n_relaxed = 0
    covered = set()
    for oy in range(H):
        for ox in range(W):
            for bw, bh in ((6, 4), (4, 6)):
                ok = True
                for dy in range(bh):
                    for dx in range(bw):
                        x, y = (ox + dx) % W, (oy + dy) % H
                        if dx + 1 < bw and kind(x, y, 1) != 0:
                            ok = False
                        if dy + 1 < bh and kind(x, y, 2) != 0:
                            ok = False
                if not ok:
                    continue
                n_open += 1
                cells = [((ox + dx) % W, (oy + dy) % H) for dy in range(bh) for dx in range(bw)]
                if not any(c in spawn for c in cells):
                    n_strict += 1
                    covered.update(cells)
                for f in FREE:
                    pts = [((ox + (a if bw == 6 else b)) % W, (oy + (b if bw == 6 else a)) % H) for a, b in f]
                    if not any(c in spawn for c in pts):
                        n_relaxed += 1
                        break
    dists = []
    for qh in queens:
        dist = {qh: 0}
        dq = deque([qh])
        best = None
        while dq:
            c = dq.popleft()
            if c in covered:
                best = dist[c]
                break
            for d in range(4):
                v = dest(c[0], c[1], d)
                if v is not None and v not in dist:
                    dist[v] = dist[c] + 1
                    dq.append(v)
        dists.append(best)
    tot['layouts'] += 1
    tot['strict'] += n_strict > 0
    tot['relaxed'] += n_relaxed > 0
    print('%-22s | %4d | %3d | %.2f | %5d | %5d | %5d | %.2f | %s'
          % (key, W * H, len(group), 1 - len(spawn) / (W * H), n_open, n_strict, n_relaxed, len(covered) / (W * H), dists))
print('layouts with at least one strict block: %d of %d; relaxed: %d of %d' % (tot['strict'], tot['layouts'], tot['relaxed'], tot['layouts']))
