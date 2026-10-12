"""one20 candidate's finished games beside one19's same games (result lines)."""
import glob, os, re, time
R = os.path.expanduser('~/meow-redteam/solo/runs/')
print(time.strftime('%H:%M:%S'))
def res(f):
    t = open(f).read()
    m = re.search(r'winner=(\S+) how=\S+ \(([^)]*)\) rounds=(\d+) final_lengths=(\S+)', t)
    return '%s %s r%s %s' % (m.group(1), m.group(2)[:22], m.group(3), m.group(4)) if m else t[:40]
for base, arm in (('nr_mA19', 'nr_mD20'), ('st_mC19', 'st_mD20')):
    A = {os.path.basename(os.path.dirname(f)): res(f) for f in glob.glob(R + base + '/*/result.txt')}
    B = {os.path.basename(os.path.dirname(f)): res(f) for f in glob.glob(R + arm + '/*/result.txt')}
    both = sorted(set(A) & set(B))
    same = sum(A[g] == B[g] for g in both)
    print('%s against %s: %d pairs, %d identical result lines (arm finished %d)' % (arm, base, len(both), same, len(B)))
    for g in both:
        if A[g] != B[g]:
            print('  ', g[:40], '| base:', A[g], '| arm:', B[g])
