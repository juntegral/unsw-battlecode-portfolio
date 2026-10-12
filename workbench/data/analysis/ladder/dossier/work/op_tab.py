# Scratch (diag-opening): the tables of diag-opening.md, from op_scan-*.jsonl and op_scan2-*.jsonl.
# A value is the mean over games inside a layout, then the mean over the layouts of a group (equal weight).
# Cell = ours / rank-1 (layouts where rank-1 is higher, of those that have the value for both).
# Usage: python3 data/analysis/ladder/dossier/work/op_tab.py
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
W = 'data/analysis/ladder/dossier/work/'
F1 = ['op_scan-O0.jsonl', 'op_scan-O1.jsonl', 'op_scan-O2.jsonl', 'op_scan-O3.jsonl',
      'op_scan-R0.jsonl', 'op_scan-R1.jsonl', 'op_scan-R2.jsonl', 'op_scan-R3.jsonl']
F2 = ['op_scan2-O0.jsonl', 'op_scan2-O1.jsonl', 'op_scan2-O2.jsonl', 'op_scan2-O3.jsonl',
      'op_scan2-R0.jsonl', 'op_scan2-R1.jsonl', 'op_scan2-R2.jsonl', 'op_scan2-R3.jsonl']
G4 = ('Default #1', 'Devil #1', 'Maze #1', 'Schooltime #1', 'Schooltime #2', 'Trauma #1', 'weakhold #1')
GL = ('Around UNSW #1', 'Australia #1', 'Autarky #1', 'Prisoners Dilemma #1', 'Prisoners Dilemma #2', 'Slithery Fight #1')
GS = ('Islands #1', 'Portals #1', 'Queen Of Spades #1', 'Stripes #1', 'Tower Defense #1', 'Trophy #1')
WALL = ('Maze #1', 'Trauma #1', 'Tower Defense #1', 'Stripes #1')


def load(files):
    games = []
    for f in files:
        with open(W + f) as fh:
            for line in fh:
                if line.strip():
                    games.append(json.loads(line))
    return games


def ser(sd, name, r, scale=1.0):
    v = sd['series'][name]
    if len(v) <= r or v[r] < 0:
        return None
    return v[r] / scale


def tsum(sd, idx, lb=None, ctx=None, q=None):
    tot = 0
    for key, v in sd['turns'].items():
        a, b, c, d = key.split('|')
        if lb is not None and b not in lb:
            continue
        if ctx is not None and c not in ctx:
            continue
        if q is not None and int(d) != q:
            continue
        tot += v[idx]
    return tot


def ratio(n, d, scale=1.0):
    return scale * n / d if d else None


def qclass(sd, r):
    al, fr = ser(sd, 'alive', r), ser(sd, 'front', r)
    v = sd['series']['qd']
    if al is None or len(v) <= r:
        return None
    qd = v[r]
    if qd < 0:
        return 'dead'
    if al <= 1:
        return 'alone'
    if qd <= 3:
        return 'stays'
    if fr is not None and qd >= fr:
        return 'leads'
    return 'follows'


def pct(flag):
    return None if flag is None else (100.0 if flag else 0.0)


def metrics():
    m = []
    add = lambda name, fn: m.append((name, fn))
    add('First split: round', lambda g, sd, x: sd['splits'][0][0] if sd['splits'] else None)
    add('First split: length of the parent', lambda g, sd, x: sd['splits'][0][1] if sd['splits'] else None)
    add('Splits by round 10', lambda g, sd, x: sum(1 for s in sd['splits'] if s[0] <= 10) if g['last_round'] >= 10 else None)
    add('Splits by round 60', lambda g, sd, x: sum(1 for s in sd['splits'] if s[0] <= 60) if g['last_round'] >= 60 else None)
    for r in (10, 20, 30):
        add('Path steps from the start, mean of heads, r%d' % r, lambda g, sd, x, r=r: ser(sd, 'meand', r, 10.0))
    for r in (10, 20, 30):
        add('Path steps from the start, farthest head, r%d' % r, lambda g, sd, x, r=r: ser(sd, 'front', r))
    add('Steps per move turn', lambda g, sd, x: ratio(tsum(sd, 2), tsum(sd, 0) - tsum(sd, 1)))
    add('Turns of 2+ steps per 100 turns', lambda g, sd, x: ratio(tsum(sd, 3), tsum(sd, 0), 100))
    add('Paid steps a game r0-60', lambda g, sd, x: float(tsum(sd, 4)) if g['last_round'] >= 60 else None)
    add('Paid steps per 100 turns, nothing in view', lambda g, sd, x: ratio(tsum(sd, 4, ctx=('N',)), tsum(sd, 0, ctx=('N',)), 100))
    add('Free steps beyond the first on offer per 100 turns', lambda g, sd, x: ratio(tsum(sd, 7), tsum(sd, 0), 100))
    add('Free steps beyond the first: used %', lambda g, sd, x: ratio(tsum(sd, 6), tsum(sd, 7), 100))
    for r in (10, 20, 30):
        add('Spread: mean straight distance between heads, r%d' % r, lambda g, sd, x, r=r: ser(sd, 'spread', r, 10.0))
    add('Parent and child apart 5 rounds after a split, path steps', lambda g, sd, x: ratio(sum(k[3] for k in x['kids'] if len(k) > 3 and k[3] >= 0), sum(1 for k in x['kids'] if len(k) > 3 and k[3] >= 0)) if x else None)
    add('First pearl eaten by the side: round', lambda g, sd, x: min([d[2] for d in sd['dragons'] if d[2] is not None], default=None))
    add('Starting dragons fed by round 10 %', lambda g, sd, x: ratio(sum(1 for d in sd['dragons'] if d[0] == 0 and d[2] is not None and d[2] <= 10), sum(1 for d in sd['dragons'] if d[0] == 0), 100) if g['last_round'] >= 10 else None)
    add('Starting dragons fed by round 20 %', lambda g, sd, x: ratio(sum(1 for d in sd['dragons'] if d[0] == 0 and d[2] is not None and d[2] <= 20), sum(1 for d in sd['dragons'] if d[0] == 0), 100) if g['last_round'] >= 20 else None)
    add('Children born r1-40 fed within 10 rounds %', lambda g, sd, x: ratio(sum(1 for d in sd['dragons'] if 0 < d[0] <= 40 and d[2] is not None and d[2] - d[0] <= 10), sum(1 for d in sd['dragons'] if 0 < d[0] <= 40), 100))
    add('Children born r1-40 dead within 10 rounds %', lambda g, sd, x: ratio(sum(1 for d in sd['dragons'] if 0 < d[0] <= 40 and d[3] is not None and d[3] - d[0] <= 10), sum(1 for d in sd['dragons'] if 0 < d[0] <= 40), 100))
    for r in (20, 40):
        add('Board seen by round %d %%' % r, lambda g, sd, x, r=r: ratio(ser(sd, 'seen', r), g['cells'], 100) if ser(sd, 'seen', r) is not None else None)
    for r in (20, 40, 60):
        add('Dragons alive, r%d' % r, lambda g, sd, x, r=r: ser(sd, 'alive', r))
    for r in (20, 60, 100):
        add('Total length, r%d' % r, lambda g, sd, x, r=r: (ser(sd, 'total', r) if r <= 60 else (sd['at100']['total'] if sd['at100'] else None)))
    for r in (20, 60):
        add('Pearls eaten so far, r%d' % r, lambda g, sd, x, r=r: ser(sd, 'eaten', r))
    add('Deaths r0-60', lambda g, sd, x: float(sum(sd['deaths'].values())) if g['last_round'] >= 60 else None)
    for c in ('stays', 'follows', 'leads', 'dead'):
        add('Queen at r20: %s %%' % c, lambda g, sd, x, c=c: pct(None if qclass(sd, 20) is None else qclass(sd, 20) == c))
    for c in ('stays', 'follows', 'leads', 'dead'):
        add('Queen at r40: %s %%' % c, lambda g, sd, x, c=c: pct(None if qclass(sd, 40) is None else qclass(sd, 40) == c))
    add('Queen: path steps from her start, r20', lambda g, sd, x: ser(sd, 'qd', 20))
    add('Queen: length, r20', lambda g, sd, x: ser(sd, 'ql', 20))
    add('Queen: share of the side\'s splits r0-60 %', lambda g, sd, x: ratio(sum(1 for s in sd['splits'] if s[3] == 1), len(sd['splits']), 100))
    add('Queen: pearls eaten r0-60', lambda g, sd, x: float(sum(d[6] for d in sd['dragons'] if d[5] == 1)) if g['last_round'] >= 60 else None)
    add('Enemy head in view: first round (when by 100)', lambda g, sd, x: sd['contact'])
    add('Enemy head within 6 path steps: first round (when by 100)', lambda g, sd, x: x['pc6'] if x else None)
    add('Enemy head within 6 path steps by round 20 %', lambda g, sd, x: pct(x['pc6'] is not None and x['pc6'] <= 20) if x and g['last_round'] >= 20 else None)
    add('Natural pearls born r0-60 eaten by the side by r100 %', lambda g, sd, x: None)
    return m


def main():
    games = load(F1)
    extra = {(x['who'], x['game']): x for x in load(F2)}
    layouts = sorted({g['layout'] for g in games})
    acc = defaultdict(lambda: defaultdict(list))
    pool = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    for g in games:
        x = extra.get((g['who'], g['game']))
        xs = x['sides']['u'] if x else None
        sd = g['sides']['u']
        for name, fn in metrics():
            v = fn(g, sd, xs)
            if v is not None:
                acc[name][(g['who'], g['layout'])].append(v)
        if xs:
            born = sum(v[0] for v in xs['pearls'].values())
            eat = sum(v[4] for v in xs['pearls'].values())
            p = pool['Natural pearls born r0-60 eaten by the side by r100 %'][(g['who'], g['layout'])]
            p[0] += 100.0 * eat
            p[1] += born

    def val(name, who, lay):
        if name in pool:
            p = pool[name].get((who, lay))
            return p[0] / p[1] if p and p[1] else None
        v = acc[name].get((who, lay))
        return sum(v) / len(v) if v else None

    groups = [('all 19', layouts), ('only 4s (7)', G4), ('mixed, longest 4-25 (6)', GL), ('only 2s and 3s (6)', GS),
              ('four closed starts', WALL), ('the other 15', [l for l in layouts if l not in WALL])]
    lines = ['| Measure | ' + ' | '.join(n for n, ls in groups) + ' |', '|---|' + '---|' * len(groups)]
    for name, fn in metrics():
        cells = []
        for gname, ls in groups:
            both = [l for l in ls if val(name, 'O', l) is not None and val(name, 'R', l) is not None]
            if not both:
                cells.append('-')
                continue
            o = sum(val(name, 'O', l) for l in both) / len(both)
            r = sum(val(name, 'R', l) for l in both) / len(both)
            hi = sum(1 for l in both if val(name, 'R', l) > val(name, 'O', l) + 1e-9)
            f = '%.2f' if max(abs(o), abs(r)) < 10 else '%.1f'
            cells.append((f + ' / ' + f + ' (%d/%d)') % (o, r, hi, len(both)))
        lines.append('| ' + name + ' | ' + ' | '.join(cells) + ' |')
    body = '\n'.join(lines) + '\n'
    Path(OUT + 'op_tab.txt').write_text(body)
    print(body)


main()
