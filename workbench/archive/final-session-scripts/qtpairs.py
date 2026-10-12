"""The corridor-mate candidate's pair games so far: for every game folder name present in two or more qt_* arms, the result
lines side by side; plus counts per arm."""
import glob, os, re, collections, time
R = os.path.expanduser('~/meow-redteam/solo/runs/')
print(time.strftime('%H:%M:%S'))
arms = sorted(os.path.basename(d) for d in glob.glob(R + 'qt_*'))
G = collections.defaultdict(dict)
for a in arms:
    n = 0
    for f in glob.glob(R + a + '/*/result.txt'):
        t = open(f).read()
        m = re.search(r'winner=(\S+) how=\S+ \(([^)]*)\) rounds=(\d+) final_lengths=(\S+)', t)
        G[os.path.basename(os.path.dirname(f))][a] = '%s %s r%s %s' % (m.group(1), m.group(2)[:22], m.group(3), m.group(4)) if m else t[:40]
        n += 1
    print(a, n)
for g in sorted(G):
    if len(G[g]) >= 2:
        print(g)
        for a in sorted(G[g]):
            print('   %-10s %s' % (a, G[g][a]))
