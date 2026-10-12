"""Big maps: longest dragon of each side at r300..end and every death of a dragon of 20+ after r300 (who, cause, rammer length/steps/gap).
Usage: python3 -B data/codex/astra/h2hloss-opus/endgame.py <arm> ..."""
import sys, json
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
tot = {}
for arm in sys.argv[1:]:
    print('==', arm)
    for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines():
        g = json.loads(l)
        if g['last'] < 400:
            continue
        def sn(r):
            v = g['snaps'][str(min(r, g['last']))]
            return '%d:%d' % (v[0][2], v[1][2])
        big = [d for d in g['deaths'] if d[2] >= 20 and d[0] > 300]
        s = ' '.join('%s@r%d %s L%d%s' % ('NEW' if d[1] == 0 else 'old', d[0], d[4], d[2], (' by L%d in %d steps gap %d' % (d[18][0], d[18][1], d[18][3])) if d[4] == 'rammed' and d[18] else '') for d in big)
        print(' %-38s %-4s %-7s longest new:old r300 %s r350 %s r400 %s r425 %s r450 %s r475 %s end %s | %s' % (g['folder'][3:], g['result'], g['how'], sn(300), sn(350), sn(400), sn(425), sn(450), sn(475), sn(499), s))
        for d in big:
            k = (arm, 'NEW' if d[1] == 0 else 'old', d[4])
            tot.setdefault(k, []).append(d[2])
for k in sorted(tot):
    print(k, len(tot[k]), 'sumL', sum(tot[k]), tot[k])
