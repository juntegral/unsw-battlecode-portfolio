"""Natural pearls we ate by r100, dragons at r100 and result per game: one11 (lc_mDone11) against one14 (lc_mNps), local, against m3base."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, snap
A, B = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('lc_mDone11', 'lc_mNps')
R = {a: {g['folder']: g for g in rows(a)} for a in (A, B)}
def nat(g, lo, hi):
    return sum(1 for r, s, role, origin, kd, L0 in g['eats'] if s == 0 and origin == 'n' and lo < r <= hi)
print('%-36s %-26s %-26s' % ('game', A + ': nat r100, heads, result', B + ': nat r100, heads, result'))
ta = tb = wa = wb = 0
for f in sorted(set(R[A]) & set(R[B])):
    a, b = R[A][f], R[B][f]
    ta += nat(a, 0, 100); tb += nat(b, 0, 100); wa += a['result'] == 'win'; wb += b['result'] == 'win'
    print('%-36s %4d %4d %-12s   %4d %4d %-12s' % (f, nat(a, 0, 100), snap(a, 100)[0][0], a['result'], nat(b, 0, 100), snap(b, 100)[0][0], b['result']))
print('total nat r100 %d against %d, wins %d against %d' % (ta, tb, wa, wb))
