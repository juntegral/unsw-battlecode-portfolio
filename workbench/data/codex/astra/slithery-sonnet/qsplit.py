"""Our queen splits: by length-before and round bucket; deaths within 3 rounds. Usage: qsplit.py <map>"""
import sys
from collections import Counter
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/slithery-sonnet/')
import table
for m in sys.argv[1:]:
    rows = [r for r in table.rows if r['map'] == m]
    tot = Counter(); dead = Counter()
    for r in rows:
        qd = [d[0] for d in r['deaths'] if d[1] == 0 and d[6]]
        end = qd[0] if qd else 10 ** 9
        for x in r['splits']:
            if x[1] == 0 and x[5] and x[0] <= end:
                L = x[2]
                key = ('L4' if L == 4 else 'L5' if L == 5 else 'L6-11' if L < 12 else 'L12+', 'r<=15' if x[0] <= 15 else 'r16-99' if x[0] < 100 else 'r100+')
                tot[key] += 1
                if 0 <= end - x[0] <= 3:
                    dead[key] += 1
    print(m, 'queen splits (length-before, round bucket): n / followed by her death within 3 rounds')
    for k in sorted(tot):
        print('  ', k, tot[k], dead[k])
