"""Scratch (diag-topqueen): depth rank per arm from tq2_depth-*.jsonl (0.5 = she stands like any of her dragons; lower = nearer
the enemy than her mates). Usage: python3 tq2_depthtab.py"""
import json
from collections import defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
NAMED = (454, 157, 306, 70, 91, 264, 842, 545, 19, 87)


def arm_of(g, s):
    src = g['src']
    t = g['t'][s]
    if src == 'top3':
        return 'f%d' % t if t in NAMED else 'fopp'
    if src == 'top1':
        return 'o%d' % t if t in NAMED else 'oopp'
    lab = {'agg8-q1': 'B7Q', 'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'top-l1': 'L1', 'top-l2': 'L2'}[src]
    if s == 0:
        return lab
    return 'v%d' % t if lab in ('L1', 'L2') else 'x' + lab


A = defaultdict(lambda: [[0, 0.0, 0, 0.0, 0, 0.0] for _ in range(4)])
N = defaultdict(int)
for tag in ('top3-0', 'top3-1', 't306-0', 't91-0', 't264-0', 'q1', 'm1', 'm2', 'm3', 'l1', 'l2'):
    p = W / ('tq2_depth-%s.jsonl' % tag)
    if not p.exists():
        continue
    with open(p) as fh:
        for line in fh:
            if not line.strip():
                continue
            g = json.loads(line)
            for s in (0, 1):
                N[arm_of(g, s)] += 1
                a = A[arm_of(g, s)]
                for b in range(4):
                    for k in range(6):
                        a[b][k] += g['acc'][s][b][k]
print('arm | games | bands r0-50, 51-100, 101-300, 301+: rank among all her side heads | rank among those 4 long or less | her distance to the nearest enemy head / the median of her mates')
for arm in ('f454', 'f70', 'f306', 'f157', 'f91', 'f545', 'f19', 'fopp', 'o306', 'o91', 'o264', 'oopp', 'v157', 'v306', 'v454', 'v87', 'xB7Q', 'xMAIN', 'B7Q', 'L1', 'L2', 'MAIN'):
    a = A.get(arm)
    if a is None:
        continue
    print(arm, '|', N[arm], '|', ' '.join('%.2f' % (a[b][1] / a[b][0]) if a[b][0] else '-' for b in range(4)), '|', ' '.join('%.2f' % (a[b][5] / a[b][4]) if a[b][4] else '-' for b in range(4)), '|',
          ' '.join('%.1f/%.1f' % (a[b][2] / a[b][0], a[b][3] / a[b][0]) if a[b][0] else '-' for b in range(4)))
