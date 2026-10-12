"""Natural pearls we ate by r100 per game: one13 (pc_mDone13) against one14 (pc_mNps), local games against m3base."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, snap
R = {a: {g['folder']: g for g in rows(a)} for a in ('pc_mDone13', 'pc_mNps')}
def nat(g, lo, hi):
    return sum(1 for r, s, role, origin, kd, L0 in g['eats'] if s == 0 and origin == 'n' and lo < r <= hi)
print('%-34s %-22s %-22s' % ('game', 'one13: nat r100, heads, result', 'one14: nat r100, heads, result'))
for f in sorted(set(R['pc_mDone13']) & set(R['pc_mNps'])):
    a, b = R['pc_mDone13'][f], R['pc_mNps'][f]
    print('%-34s %4d %4d %-10s   %4d %4d %-10s' % (f, nat(a, 0, 100), snap(a, 100)[0][0], a['result'], nat(b, 0, 100), snap(b, 100)[0][0], b['result']))
