"""Fed-queen outcome table. Usage: fedq.py "Slithery Fight" """
import sys
from collections import Counter, defaultdict
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/slithery-sonnet/')
import table
MAP = sys.argv[1]
rows = [r for r in table.rows if r['map'] == MAP]
out = defaultdict(list)
for r in rows:
    sn = r['snaps']
    # max queen length reached at snapshots (25-round resolution) and when first >=15
    qmax = max(sn[k][0][3] for k in sn if int(k) >= 50)
    first15 = min([int(k) for k in sn if int(k) >= 50 and sn[k][0][3] >= 15] or [999])
    qd = [d for d in r['deaths'] if d[1] == 0 and d[6]]
    qs_big_split = [x for x in r['splits'] if x[1] == 0 and x[5] and x[2] >= 8 and x[3] == 2]  # queen with >=8 splits down to 2
    first = qd[0] if qd else None
    key = 'fed(>=15 at snapshot)' if qmax >= 15 else 'unfed'
    out[key].append((r['gid'], r['result'], qmax, first15, (first[0], first[2], first[4]) if first else None, [(x[0], x[2]) for x in qs_big_split]))
for k, v in out.items():
    print(k, len(v), Counter(x[1] for x in v), 'queen died:', sum(1 for x in v if x[4]))
    for x in v:
        print('   ', x)
