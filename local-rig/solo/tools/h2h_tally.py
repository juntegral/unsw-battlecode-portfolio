"""h2h_tally.py : W/D/L of every head-to-head folder runs/h2h_<arm>_v<opp>/ (the arm is the side named in the game folder)."""
import glob, re, os, collections
for a in sorted(glob.glob(os.path.expanduser('~/meow-redteam/solo/runs/h2h_*'))):
    c = collections.Counter(); how = collections.Counter()
    for d in glob.glob(a + '/*/'):
        f = d + 'result.txt'
        if not os.path.exists(f):
            continue
        t = open(f).read(); side = int(os.path.basename(d[:-1])[-1]); w = re.search(r'winner=(\S+)', t).group(1)
        r = 'W' if w == str(side) else 'D' if w == 'draw' else 'L'
        c[r] += 1; how[(r, re.search(r'how=\S+ \(([^,)]*)', t).group(1)[:14])] += 1
    n = sum(c.values())
    print('%-22s %2d-%d-%2d of %3d  %s' % (os.path.basename(a), c['W'], c['D'], c['L'], n, ' '.join('%s:%s %d' % (k[0], k[1], v) for k, v in sorted(how.items()))))
