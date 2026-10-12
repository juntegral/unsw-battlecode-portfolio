"""qcut pairs table. Usage (from ROOT): python3 -B data/codex/astra/qcut-opus/ana.py"""
import sys, re, filecmp
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/codex/astra/qcut-opus')
from pathlib import Path
from q import one
RUNS = Path.home() / 'meow-redteam/solo/runs'
LOGS = Path('~/.claude/jobs/e2109d93/tmp/qclog')
SITES = {1326, 1819, 1875, 1989}
ARMS = ['d0', 'd60', 'w60', 'w1', 'w60r']


def log(arm, name):
    p = LOGS / ('qc_%s__%s.log' % (arm, name))
    boxed = boxed60 = fired = wait2 = 0
    fires = []
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        m = re.match(r'r(\d+) len(\d+) child(\d+) line(\d+) units(\d+) trail(\d+) head(\d+),(\d+) \|(.*)', line)
        r, L, child, ln, units = (int(m[k]) for k in range(1, 6))
        if ln not in SITES:
            continue
        dirs = re.findall(r'next(-?\d+),et(-?\d+),own(-?\d+)', m[9])
        box = all(int(n) < 0 or int(et) > 1 for n, et, own in dirs)
        own = max(int(o) for n, et, o in dirs)
        wait2 += child == 2
        if box and own >= 2:
            boxed += 1
            boxed60 += units >= 60
        if child != 2:
            fired += 1
            fires.append('r%d:%d-%d' % (r, L, child))
    return boxed, boxed60, fired, wait2, fires


names = sorted({f.name for a in ARMS for f in (RUNS / ('qc_' + a)).glob('*-seed*-side*') if (f / 'result.txt').exists()})
for name in names:
    seat = int(name[-1])
    base_sig = None
    for arm in ARMS:
        f = RUNS / ('qc_' + arm) / name
        if not (f / 'result.txt').exists():
            continue
        g, ql, dead, last = one(f, seat)
        at = lambda r: ql.get(min(r, max(ql)), 0)
        res = (f / 'result.txt').read_text().split()
        win = res[0].split('=')[1]
        sig = repr(sorted(g['snapshots'].items()))
        if arm == 'd0':
            base_sig = sig
        same = 'same' if arm != 'd0' and sig == base_sig else 'DIFF' if arm != 'd0' else ''
        lg = log(arm, name)
        s100 = g['snapshots'][min(100, max(g['snapshots']))]['us']
        print('%-30s %-4s p100 %-3d u100 %-2d qdead %-4s L300 %-3d L400 %-3d end %-3d %s tot %d-%d %-4s %s' % (
            name, arm, s100['pearls'], s100['alive'], dead, at(300), at(400), g['final']['us']['queen_length'], 'WIN ' if int(win) == seat else 'loss',
            g['final']['us']['total'], g['final']['them']['total'], same,
            '' if lg is None else 'waitsplits %d boxedOwn %d (u>=60: %d) cuts %d %s' % (lg[3] + lg[2], lg[0], lg[1], lg[2], ' '.join(lg[4][:6]))))
    print()
