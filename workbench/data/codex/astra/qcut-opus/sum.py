"""qcut: classify the queen's 2-cell wait splits in the off arm (debug log). Usage: python3 -B sum.py [arm]"""
import re, sys
from pathlib import Path
from collections import Counter
LOGS = Path('~/.claude/jobs/e2109d93/tmp/qclog')
SITES = {1326: 'exit', 1819: 'act-keep', 1875: 'queen_wait', 1989: 'portal-alt'}
arm = sys.argv[1] if len(sys.argv) > 1 else 'd0'
tot = Counter()
for p in sorted(LOGS.glob('qc_%s__*.log' % arm)):
    c = Counter()
    ex = []
    for line in p.read_text().splitlines():
        m = re.match(r'r(\d+) len(\d+) child(\d+) line(\d+) units(\d+) trail(\d+) head(\d+),(\d+) \|(.*)', line)
        r, L, child, ln, units = (int(m[k]) for k in range(1, 6))
        if ln not in SITES:
            c['other-split'] += 1
            continue
        dirs = [(int(n), int(et), int(o)) for n, et, o in re.findall(r'next(-?\d+),et(-?\d+),own(-?\d+)', m[9])]
        box = all(n < 0 or et > 1 for n, et, o in dirs)
        own = max((o for n, et, o in dirs if o >= 2), default=-1)
        late = 'u>=60' if units >= 60 else 'u<60'
        early = 'r<20' if r < 20 else 'r>=20'
        kind = ('boxed+own' if own >= 2 else 'boxed-noown') if box else 'open'
        c[(SITES[ln], early, late, kind)] += 1
        if r >= 20 and box and own >= 2:
            ex.append('r%d L%d own%d u%d' % (r, L, own, units))
    tot.update(c)
    print(p.stem, dict(c), ex[:6])
print('TOTAL')
for k, v in sorted(tot.items(), key=str):
    print('  ', k, v)
