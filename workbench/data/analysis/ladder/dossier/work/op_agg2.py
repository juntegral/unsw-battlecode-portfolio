# Scratch (diag-opening): tables from op_scan2-*.jsonl (path contact, parent and child apart, pearls by distance at birth).
# Values are pooled inside a layout, then averaged over layouts with equal weight; "hi/lo/n" counts layouts (rank-1 higher).
# Usage: python3 data/analysis/ladder/dossier/work/op_agg2.py [detail]
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
W = 'data/analysis/ladder/dossier/work/'
FILES = ['op_scan2-O0.jsonl', 'op_scan2-O1.jsonl', 'op_scan2-O2.jsonl', 'op_scan2-O3.jsonl',
         'op_scan2-R0.jsonl', 'op_scan2-R1.jsonl', 'op_scan2-R2.jsonl', 'op_scan2-R3.jsonl']


def load():
    games = []
    for f in FILES:
        with open(W + f) as fh:
            for line in fh:
                if line.strip():
                    games.append(json.loads(line))
    return games


def main():
    games = load()
    detail = len(sys.argv) > 1
    layouts = sorted({g['layout'] for g in games})
    num = defaultdict(lambda: defaultdict(float))
    den = defaultdict(lambda: defaultdict(float))

    def add(name, tag, lay, n, d):
        num[name][(tag, lay)] += n
        den[name][(tag, lay)] += d

    order = []

    def reg(name):
        if name not in order:
            order.append(name)

    for g in games:
        for s, tag in (('u', g['who']), ('t', g['who'] + 'o')):
            sd = g['sides'][s]
            lay = g['layout']
            for nm in ('vc', 'pc6', 'pc3'):
                v = sd[nm]
                reg(nm + ' round (when it comes by 100)')
                if v is not None:
                    add(nm + ' round (when it comes by 100)', tag, lay, v, 1)
                for r in (10, 20, 40):
                    reg('%s by %d %%' % (nm, r))
                    if g['last_round'] >= r:
                        add('%s by %d %%' % (nm, r), tag, lay, 100.0 if v is not None and v <= r else 0.0, 1)
            for kid in sd['kids']:
                for j, lab in ((1, 'end of split round'), (2, '+3'), (3, '+5'), (4, '+10')):
                    if len(kid) > j:
                        reg('parent-child apart %s (both alive)' % lab)
                        reg('one of the pair dead %s %%' % lab)
                        add('one of the pair dead %s %%' % lab, tag, lay, 100.0 if kid[j] < 0 else 0.0, 1)
                        if kid[j] >= 0:
                            add('parent-child apart %s (both alive)' % lab, tag, lay, kid[j], 1)
                            if j >= 3:
                                reg('parent-child within 4 steps %s %%' % lab)
                                add('parent-child within 4 steps %s %%' % lab, tag, lay, 100.0 if kid[j] <= 4 else 0.0, 1)
                                reg('parent-child 12+ steps apart %s %%' % lab)
                                add('parent-child 12+ steps apart %s %%' % lab, tag, lay, 100.0 if kid[j] >= 12 else 0.0, 1)
            tot = sum(v[0] for v in sd['pearls'].values())
            allv = [sum(v[k] for v in sd['pearls'].values()) for k in range(10)]
            groups = [('all', allv)] + [(lab, sd['pearls'].get(b, [0] * 10)) for b, lab in (('a', '0-3'), ('b', '4-7'), ('c', '8-15'), ('d', '16+'))]
            for lab, v in groups:
                pre = 'born r0-60, nearest head %s: ' % lab
                for nm in ('share of births %', 'in view at birth %', 'seen by r100 %', 'rounds to first seen', 'eaten by the side %',
                           'rounds birth to eaten', 'rounds seen to eaten', 'eaten by the other side %', 'eaten in birth round %', 'eaten within 10 rounds %'):
                    reg(pre + nm)
                add(pre + 'share of births %', tag, lay, 100.0 * v[0], tot)
                add(pre + 'in view at birth %', tag, lay, 100.0 * v[1], v[0])
                add(pre + 'seen by r100 %', tag, lay, 100.0 * v[2], v[0])
                add(pre + 'rounds to first seen', tag, lay, v[3], v[2])
                add(pre + 'eaten by the side %', tag, lay, 100.0 * v[4], v[0])
                add(pre + 'rounds birth to eaten', tag, lay, v[5], v[4])
                add(pre + 'rounds seen to eaten', tag, lay, v[6], v[4])
                add(pre + 'eaten by the other side %', tag, lay, 100.0 * v[7], v[0])
                add(pre + 'eaten in birth round %', tag, lay, 100.0 * v[8], v[0])
                add(pre + 'eaten within 10 rounds %', tag, lay, 100.0 * v[9], v[0])
            first = sd['first8']
            reg('starters whose first turn is a split %')
            add('starters whose first turn is a split %', tag, lay, 100.0 * sum(1 for f in first if f[:1] == 'S'), len(first))
            reg('starters with the same first 6 turns as another starter %')
            six = [' '.join(f.split()[:6]) for f in first if len(f.split()) >= 6]
            add('starters with the same first 6 turns as another starter %', tag, lay, 100.0 * sum(1 for f in six if six.count(f) > 1), len(six))
    lines = ['%-66s %8s %8s %8s %8s  %s' % ('metric', 'O', 'R', 'Oopp', 'Ropp', 'hi/lo/n')]
    for name in order:
        val = lambda tag, l: num[name][(tag, l)] / den[name][(tag, l)] if den[name].get((tag, l)) else None
        both = [l for l in layouts if val('O', l) is not None and val('R', l) is not None]
        if not both:
            continue
        mean = lambda tag: (lambda vs: sum(vs) / len(vs) if vs else float('nan'))([val(tag, l) for l in both if val(tag, l) is not None])
        hi = sum(1 for l in both if val('R', l) > val('O', l) + 1e-9)
        lo = sum(1 for l in both if val('R', l) < val('O', l) - 1e-9)
        lines.append('%-66s %8.2f %8.2f %8.2f %8.2f  %d/%d/%d' % (name, mean('O'), mean('R'), mean('Oo'), mean('Ro'), hi, lo, len(both)))
        if detail and (name.startswith('pc6') or name.startswith('vc round') or name.startswith('parent-child apart +5') or name.startswith('parent-child apart +10')
                       or 'all: eaten by the side' in name or 'all: rounds to first seen' in name or 'all: rounds seen to eaten' in name or 'first turn' in name):
            for l in layouts:
                row = ['%8.2f' % val(tag, l) if val(tag, l) is not None else '%8s' % '-' for tag in ('O', 'R', 'Oo', 'Ro')]
                lines.append('    %-62s %s' % (l, ' '.join(row)))
    body = '\n'.join(lines) + '\n'
    Path(OUT + 'op_agg2.txt').write_text(body)
    print(body)


main()
