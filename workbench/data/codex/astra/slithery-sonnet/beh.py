import sys, statistics as st
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/slithery-sonnet/')
import table
for m in ('Slithery Fight', 'Portals'):
    xs = []; near = 0; n = 0
    for r in table.rows:
        if r['map'] != m or r['result'] != 'loss':
            continue
        b = table.behind(r)
        qd = [d[0] for d in r['deaths'] if d[1] == 0 and d[6]]
        if b in ('never',) or not qd:
            continue
        b = int(b); xs.append(b); n += 1
        if abs(b - qd[0]) <= 25:
            near += 1
    print(m, 'losses', n, 'behind-for-good round median', st.median(xs), 'sorted', sorted(xs), 'within 25 rounds of our first queen death:', near)
