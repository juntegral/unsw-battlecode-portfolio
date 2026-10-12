import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_local import rows, snap

for arm in sys.argv[1:]:
    print('==', arm)
    for g in rows(arm):
        k = int(g['folder'][-1])
        us = [snap(g, r)[0][0] for r in (5, 10, 15, 20, 25, 30, 40, 50)]
        ours = [d for d in g['deaths'] if d[1] == 0 and d[0] <= 30]
        eats = sum(1 for e in g['eats'] if e[1] == 0 and e[0] <= 30)
        print('%-32s units r5..r50=%s eats<=30=%d deaths<=30=%s last=%s ends=%s' % (
            g['folder'], us, eats, [(d[0], d[2], d[4]) for d in ours][:8], g['last'], [e[:3] for e in g['ends']]))
