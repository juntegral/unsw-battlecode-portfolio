"""Scratch (meow-main07): economy table of local arms on the gx maps (288-1536 cells), games both arms finished.
Usage (repo root): o1_sweeptab.py <baseline arm> <arm>..."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, snap
base, arms = sys.argv[1], sys.argv[2:]
R = {a: {g['folder']: g for g in rows(a) if g['folder'].startswith('gx_')} for a in [base] + arms}
def nat(g, lo, hi):
    return sum(1 for r, s, role, origin, kd, L0 in g['eats'] if s == 0 and origin == 'n' and lo < r <= hi)
print('arm       games  win   nat r1-100  nat r101-150  heads r100  heads r150  len r150  (same games for the baseline in brackets)')
for a in arms:
    common = sorted(set(R[a]) & set(R[base]))
    if not common:
        print('%-9s no common games' % a)
        continue
    t = {x: [0, 0, 0, 0, 0, 0] for x in (a, base)}
    for f in common:
        for x in (a, base):
            g = R[x][f]
            v = t[x]
            v[0] += g['result'] == 'win'
            v[1] += nat(g, 0, 100)
            v[2] += nat(g, 100, 150)
            v[3] += snap(g, 100)[0][0]
            v[4] += snap(g, 150)[0][0]
            v[5] += snap(g, 150)[0][1]
    n = len(common)
    A, B = t[a], t[base]
    print('%-9s %4d  %2d [%2d]  %5d [%5d]  %5d [%5d]  %5.1f [%5.1f]  %5.1f [%5.1f]  %5.1f [%5.1f]' % (
        a, n, A[0], B[0], A[1], B[1], A[2], B[2], A[3] / n, B[3] / n, A[4] / n, B[4] / n, A[5] / n, B[5] / n))
