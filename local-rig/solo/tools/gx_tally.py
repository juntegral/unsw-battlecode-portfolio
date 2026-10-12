"""gx_tally.py <arm>... : W/D/L of each arm on the gx maps, by size band; with -v the losses."""
import glob, re, os, sys, collections
args = [a for a in sys.argv[1:] if a != '-v']
cells = {}
for l in open(os.path.expanduser('~/meow-redteam/maps/gx/INDEX.tsv')) if os.path.exists(os.path.expanduser('~/meow-redteam/maps/gx/INDEX.tsv')) else []:
    p = l.rstrip('\n').split('\t')
    if p[0] != 'name':
        cells[p[0][:-4]] = int(p[4])
def band(c):
    return '<=100' if c <= 100 else '<=300' if c <= 300 else '<=1100' if c <= 1100 else '<=4096' if c <= 4096 else '>4096'
for arm in args:
    T = collections.defaultdict(collections.Counter)
    how = collections.Counter()
    for d in sorted(glob.glob(os.path.expanduser('~/meow-redteam/solo/runs/%s/gx_*/' % arm))):
        f = d + 'result.txt'
        if not os.path.exists(f):
            continue
        t = open(f).read()
        n = os.path.basename(d[:-1])
        side = int(n[-1])
        w = re.search(r'winner=(\S+)', t).group(1)
        res = 'W' if w == str(side) else 'D' if w == 'draw' else 'L'
        b = band(cells.get(n.split('-seed')[0], 0))
        T[b][res] += 1
        T['all'][res] += 1
        if res == 'L':
            how[re.search(r'how=(\S+) \(([^)]*)\)', t).group(2).split(',')[0][:22]] += 1
            if '-v' in sys.argv:
                print('  L', n, re.search(r'how=.*', t).group(0)[:80])
    print('%-8s' % arm, ' '.join('%s %d/%d/%d' % (b, T[b]['W'], T[b]['D'], T[b]['L']) for b in ('<=100', '<=300', '<=1100', '<=4096', '>4096', 'all') if T[b]), '| losses by', dict(how))
