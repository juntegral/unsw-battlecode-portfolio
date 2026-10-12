# Scratch (diag-hungry): prints hg_lad output. A cell is ours / rank-1, formed inside a layout and averaged over the
# layouts with equal weight; (k/n) = layouts where rank-1 is the higher. Local m3b7 games are printed beside them
# (ladder layouts and generated maps apart).
# Usage: python3 data/analysis/ladder/dossier/work/hg_lagg.py
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path
from statistics import mean

WORK = 'data/analysis/ladder/dossier/work/'
NF = 17


def load(names):
    lay = defaultdict(dict)
    for nm in names:
        p = Path(WORK + nm)
        if not p.is_file():
            continue
        for line in p.read_text().splitlines():
            j = json.loads(line)
            d = lay[j['layout']]
            for row in j['acc']:
                key = tuple(row[:3])
                v = d.setdefault(key, [0] * NF)
                for z in range(NF):
                    v[z] += row[3 + z]
    return lay


def pick(d, sel):
    v = [0] * NF
    for key, row in d.items():
        if sel(key):
            for z in range(NF):
                v[z] += row[z]
    return v


METRICS = [
    ('tiles from where it stood 10 turns ago, mean', lambda v: v[2] / v[1] if v[1] else None),
    ('... 4 or fewer %', lambda v: 100.0 * v[3] / v[1] if v[1] else None),
    ('head on a tile of its last 12 turns %', lambda v: 100.0 * v[4] / v[0] if v[0] else None),
    ('same step as last turn %', lambda v: 100.0 * v[6] / v[5] if v[5] else None),
    ('tiles seen for the first time per turn', lambda v: v[7] / v[0] if v[0] else None),
    ('... turns with none %', lambda v: 100.0 * v[8] / v[0] if v[0] else None),
    ('unclaimed pearl within 3 %', lambda v: 100.0 * v[9] / v[0] if v[0] else None),
    ('unclaimed pearl 4-6 away %', lambda v: 100.0 * v[10] / v[0] if v[0] else None),
    ('unclaimed pearl 7-12 away %', lambda v: 100.0 * v[11] / v[0] if v[0] else None),
    ('no unclaimed pearl within 12 %', lambda v: 100.0 * v[12] / v[0] if v[0] else None),
    ('meals per 1,000 turns', lambda v: 1000.0 * v[13] / v[0] if v[0] else None),
    ('unclaimed pearl within 12 older than 10 rounds %', lambda v: 100.0 * v[14] / v[0] if v[0] else None),
    ('age of the unclaimed pearl 4-12 away, mean rounds', lambda v: v[16] / v[15] if v[15] else None),
]

GROUPS = [
    ('hungry (26+), all', lambda k: k[0] == 1),
    ('hungry, no pearl in view', lambda k: k[0] == 1 and k[1] == 0),
    ('hungry, pearl in view', lambda k: k[0] == 1 and k[1] == 1),
    ('hungry, no mate in view', lambda k: k[0] == 1 and k[2] == 0),
    ('hungry, 1-2 mates in view', lambda k: k[0] == 1 and k[2] == 1),
    ('hungry, 3+ mates in view', lambda k: k[0] == 1 and k[2] == 2),
    ('hungry, no view, no mate', lambda k: k[0] == 1 and k[1] == 0 and k[2] == 0),
    ('hungry, no view, 3+ mates', lambda k: k[0] == 1 and k[1] == 0 and k[2] == 2),
    ('4-25 rounds, all', lambda k: k[0] == 0),
]


def cell(lays, sel, fn, minturns=200):
    vals = {}
    for lay, d in lays.items():
        v = pick(d, sel)
        if v[0] >= minturns:
            x = fn(v)
            if x is not None:
                vals[lay] = x
    return vals


def main():
    O = load(['hg_lad-O0.jsonl', 'hg_lad-O1.jsonl'])
    R = load(['hg_lad-R0.jsonl', 'hg_lad-R1.jsonl'])
    L = load(['hg_lad-L0.jsonl'])
    LL = {k: v for k, v in L.items() if k.startswith('ladder')}
    LG = {k: v for k, v in L.items() if not k.startswith('ladder')}
    print('layouts ours', len(O), 'rank-1', len(R), 'local ladder', len(LL), 'local generated', len(LG))
    # mix of hungry turns
    print('\n== mix of hungry turns (share of hungry turns %), ours / rank-1 (k/n rank-1 higher) | local ladder | local generated')
    for name, sel in GROUPS[1:8]:
        fn = None
        a = {lay: 100.0 * pick(d, sel)[0] / max(1, pick(d, GROUPS[0][1])[0]) for lay, d in O.items()}
        b = {lay: 100.0 * pick(d, sel)[0] / max(1, pick(d, GROUPS[0][1])[0]) for lay, d in R.items()}
        common = [x for x in a if x in b]
        c = [100.0 * pick(d, sel)[0] / max(1, pick(d, GROUPS[0][1])[0]) for d in LL.values()]
        e = [100.0 * pick(d, sel)[0] / max(1, pick(d, GROUPS[0][1])[0]) for d in LG.values() if pick(d, GROUPS[0][1])[0] >= 200]
        print('  %-28s %5.1f / %5.1f (%d/%d) | %5.1f | %5.1f' % (name, mean(a[x] for x in common), mean(b[x] for x in common), sum(b[x] > a[x] for x in common), len(common), mean(c) if c else -1, mean(e) if e else -1))
    for name, sel in GROUPS:
        print('\n== ' + name)
        for mname, fn in METRICS:
            a = cell(O, sel, fn)
            b = cell(R, sel, fn)
            common = [x for x in a if x in b]
            c = list(cell(LL, sel, fn).values())
            e = list(cell(LG, sel, fn).values())
            if not common:
                continue
            print('  %-52s %6.1f / %6.1f (%d/%d) | %6.1f | %6.1f' % (mname, mean(a[x] for x in common), mean(b[x] for x in common), sum(b[x] > a[x] for x in common), len(common), mean(c) if c else -1, mean(e) if e else -1))


main()
