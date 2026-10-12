"""Queen deaths per game (both sides) and every ram aimed at a queen. Usage: python3 -B .../queens.py <arm> ..."""
import sys, json
from collections import Counter
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
for arm in sys.argv[1:]:
    print('==', arm)
    agg = Counter()
    for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines():
        g = json.loads(l)
        out = []
        first = None
        for d in g['deaths']:
            if d[6]:
                who = 'NEWq' if d[1] == 0 else 'oldq'
                ex = d[18]
                txt = '%s r%d %s L%d' % (who, d[0], d[4], d[2])
                if d[4] == 'rammed' and ex:
                    txt += ' by L%d %dst gap%d%s' % (ex[0], ex[1], ex[3], ' (by QUEEN)' if ex[4] else '')
                    agg[(who, 'rammed by L%s' % ('2-4' if ex[0] <= 4 else '5+'))] += 1
                    agg[(who, 'steps %d' % ex[1])] += 1
                else:
                    agg[(who, d[4])] += 1
                txt += ' mates5=%d foes5=%d free=%d' % (d[8], d[9], d[5])
                out.append(txt)
                if first is None:
                    first = who
        agg[('first queen to die', first, g['result'])] += 1
        v = lambda r: g['snaps'].get(str(r), g['snaps'][str(g['last'])])
        print(' %-36s %-4s %-7s | %s' % (g['folder'][3:-6] + g['folder'][-2:], g['result'], g['how'], ' ; '.join(out)))
    for k in sorted(agg, key=str):
        print('   ', k, agg[k])
