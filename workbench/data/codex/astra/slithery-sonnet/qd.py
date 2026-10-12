"""Our-queen deaths. Usage: qd.py "Slithery Fight" """
import sys
from collections import Counter
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/slithery-sonnet/')
import table
MAP = sys.argv[1]
rows = [r for r in table.rows if r['map'] == MAP]
print(len(rows), 'games')
ags = Counter()
tot = 0
for r in rows:
    for d in r['deaths']:
        if d[1] == 0 and d[6]:
            tot += 1
            ex = d[18]
            if d[4] == 'rammed' and ex:
                L0, steps, paid, gap, aq = ex
                free = (L0 + 3) // 4
                print('%d %s r%d L%d rammed by L%d steps %d (free %d, paid %d segs) gap %d | mates<=5 %d foes<=5 %d free-sides %d | after-split %s' % (
                    r['gid'], r['result'], d[0], d[2], L0, steps, free, paid, gap, d[8], d[9], d[5], 'y' if d[2] == 2 and r['splits'] and any(x[1] == 0 and x[5] and x[0] >= d[0] - 2 and x[0] <= d[0] for x in r['splits']) else ''))
                ags['rammed'] += 1
            else:
                print('%d %s r%d L%d %s mates<=5 %d foes<=5 %d free-sides %d extra %s' % (r['gid'], r['result'], d[0], d[2], d[4], d[8], d[9], d[5], ex))
                ags[d[4]] += 1
print(tot, 'queen deaths in', len(rows), 'games', dict(ags))
