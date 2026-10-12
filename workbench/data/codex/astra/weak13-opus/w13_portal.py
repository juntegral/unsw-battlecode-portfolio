"""Portal crossings in r0-99 by side, version and map (reads each replay to r100).
A crossing = a head step over an edge of kind 2. Ours are split: queen, non-queen shorter than 4, non-queen 4 or longer.
Usage (repo root): python3 -B data/codex/astra/weak13-opus/w13_portal.py > data/codex/astra/weak13-opus/portal.txt"""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path

OUT = Path('data/codex/astra/weak13-opus')
SM = Path('data/online/smoke')
VERS = ('one8', 'one10', 'one11', 'one12', 'one13')
folders = [f for f in sorted(SM.glob('one*-old')) if re.match(r'(one\d+)', f.name).group(1) in VERS]
folders += [Path('data/online/live-one1/b1508960'), Path('data/online/live-one1/b1513119'), Path('data/online/live-one1/b1483679')]
BOT = {'21377': 'one13', '21126': 'one8'}
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def run(path, j):
    root = replay.load(path).root()
    lines = root.text(0).splitlines()
    W, H = map(int, lines[0].split()[1:3])
    heads, lens, teams, raw = {}, {}, {}, []
    for line in lines:
        q = line.split()
        if not q:
            continue
        if q[0] == 'DRAGON':
            i = len(heads)
            heads[i] = (int(q[3]), int(q[4]))
            lens[i] = int(q[2])
            teams[i] = int(q[1])
        elif q[0] == 'EDGE':
            raw.append((int(q[1]), int(q[2]), int(q[3])))
    edges = canonical_edges(W, H, raw)
    own = 0 if j['teamAId'] == 1119 else 1
    queen = min(i for i in teams if teams[i] == own)
    c = defaultdict(int)
    rnd = -1
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            if rnd >= 100:
                break
        elif k == 9:
            i = p.i32(0)
            hd = replay.point(p.pointer(0))
            h = heads[i]
            if hd != h:
                plain = False
                for d in range(4):
                    if ((h[0] + STEP[d][0]) % W, (h[1] + STEP[d][1]) % H) == hd and edges.get(edge_id(W, H, h[0], h[1], d), (0, -1))[0] != 2:
                        plain = True
                if not plain:
                    half = 'a' if rnd < 50 else 'b'
                    if teams[i] != own:
                        c['them'] += 1
                    elif i == queen:
                        c['q'] += 1
                    elif lens.get(i, 2) < 4:
                        c['short'] += 1
                    else:
                        c['long'] += 1
                heads[i] = hd
        elif k == 10:
            for z, i in enumerate((p.i32(0), p.i32(4))):
                body = [replay.point(x) for x in p.pointer(z)]
                heads[i] = body[0]
                lens[i] = len(body)
                teams[i] = p.u16(8)
        elif k == 11:
            heads.pop(p.i32(0), None)
    return [root.text(1), root.text(2)][own], c


rows = []
for folder in folders:
    for mp in sorted(folder.glob('game-*.json')):
        j = json.loads(mp.read_text())
        rp = folder / ('M%d.replay' % j['id'])
        if not rp.exists() or 1119 not in (j['teamAId'], j['teamBId']):
            continue
        bot, c = run(rp, j)
        m = re.match(r'(one\d+)', folder.name)
        ver = m.group(1) if m else BOT.get(bot, 'bot' + bot)
        rows.append((folder.name, j['id'], j['mapName'], ver, c['q'], c['short'], c['long'], c['them']))
with open(OUT / 'portal-rows.tsv', 'w') as f:
    f.write('set\tgid\tmap\tver\tq\tshort\tlong\tthem\n')
    for r in rows:
        f.write('\t'.join(map(str, r)) + '\n')
agg = defaultdict(list)
for r in rows:
    agg[r[2], r[3]].append(r)
maps = sorted({r[2] for r in rows})
print('portal crossings r0-99, mean per game: ours short(<4)/long(4+)/queen : theirs (games)')
print('%-16s' % 'map' + ''.join('%-26s' % v for v in VERS))
for m in maps:
    line = '%-16s' % m[:15]
    for v in VERS:
        g = agg[m, v]
        n = len(g)
        line += '%-26s' % ('%.1f/%.1f/%.1f : %.1f (%d)' % (sum(x[5] for x in g) / n, sum(x[6] for x in g) / n, sum(x[4] for x in g) / n,
                                                           sum(x[7] for x in g) / n, n) if g else '-')
    print(line)
