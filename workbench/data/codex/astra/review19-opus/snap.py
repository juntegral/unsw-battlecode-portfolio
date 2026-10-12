import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from collections import Counter
from o1_local import rows, snap

for arm in sys.argv[1:]:
    print('==', arm)
    for g in rows(arm):
        s50, s100, s200 = snap(g, 50), snap(g, 100), snap(g, 200)
        ours = [d for d in g['deaths'] if d[1] == 0]
        kinds = Counter(d[4] for d in ours if d[0] <= 100)
        early2 = sum(1 for d in ours if d[0] <= 100 and d[2] <= 2)
        eats100 = sum(1 for e in g['eats'] if e[1] == 0 and e[0] <= 100)
        print('%-34s u50=%s u100=%s T100=%s oT100=%s u200=%s T200=%s eats100=%d deaths<=100 %s len<=2:%d last=%s ends=%s' % (
            g['folder'], s50[0][0], s100[0][0], s100[0][1], s100[1][1], s200[0][0], s200[0][1], eats100, dict(kinds), early2,
            g['last'], [e[:3] for e in g['ends']]))
