"""One line per game the newer version lost: how decided, final (queen, longest, total), round from which it was behind for good
on (queen, longest, total) at the 25-round snapshots, queen deaths, biggest own dragon rammed after r400. Usage: losses.py <arm> ..."""
import sys, json
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
for arm in sys.argv[1:]:
    print('| %s | decided | final queen / longest / total (new:old) | behind for good from | queens (first to die first) | biggest own dragon rammed after r400 |' % arm[5:])
    print('|---|---|---|---|---|---|')
    for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines():
        g = json.loads(l)
        if g['result'] != 'loss':
            continue
        rs = sorted(int(r) for r in g['snaps'])
        behind = None
        for r in rs:
            v = g['snaps'][str(r)]
            a, b = (v[0][3], v[0][2], v[0][1]), (v[1][3], v[1][2], v[1][1])
            if a < b:
                behind = r if behind is None else behind
            else:
                behind = None
        q = ['%s r%d %s L%d%s' % ('NEW' if d[1] == 0 else 'old', d[0], d[4], d[2], (' by L%d' % d[18][0]) if d[4] == 'rammed' and d[18] else '') for d in g['deaths'] if d[6]]
        big = sorted(((d[2], d[0], d[18][0]) for d in g['deaths'] if d[1] == 0 and d[4] == 'rammed' and d[0] > 400 and d[18]), reverse=True)[:1]
        e = g['ends']
        print('| %s | %s r%d | %d:%d / %d:%d / %d:%d | r%s | %s | %s |' % (
            g['folder'][3:].replace('-seed1-side', ' s').split('_9')[0] + ' s' + g['folder'][-1], g['how'], g['last'] + 1, e[0][3], e[1][3], e[0][2], e[1][2], e[0][1], e[1][1],
            behind, '; '.join(q) or 'both alive', ('L%d at r%d by L%d' % big[0]) if big else '-'))
    print()
