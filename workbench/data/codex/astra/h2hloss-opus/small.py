"""Small maps (24x12): units/total at r25/50/75/100, rams started by each side in r1-100, queen deaths. Usage: small.py <arm> ..."""
import sys, json
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
for arm in sys.argv[1:]:
    print('==', arm)
    for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines():
        g = json.loads(l)
        if g['cells'] > 300:
            continue
        v = lambda r: g['snaps'].get(str(r), g['snaps'][str(g['last'])])
        u = ' '.join('r%d %d/%d:%d/%d' % (r, v(r)[0][0], v(r)[0][1], v(r)[1][0], v(r)[1][1]) for r in (25, 50, 75, 100))
        rams = [[0, 0, 0], [0, 0, 0]]
        other = [0, 0]
        for d in g['deaths']:
            if d[0] > 100:
                continue
            if d[4] == 'rams':
                rams[d[1]][0] += 1
                rams[d[1]][1] += d[2]
            elif d[4] == 'rammed':
                rams[1 - d[1]][2] += d[2]
            else:
                other[d[1]] += 1
        q = ['%s r%d %s L%d' % ('NEWq' if d[1] == 0 else 'oldq', d[0], d[4], d[2]) for d in g['deaths'] if d[6]]
        nat = [sum(1 for e in g['eats'] if e[1] == s and e[0] <= 50) for s in (0, 1)]
        print(' %-28s %-4s last %3d | units/total new:old %s | eats r1-50 %d:%d | rams started r1-100 new %d (own L%d for L%d) old %d (own L%d for L%d) | other deaths %d:%d | %s' % (
            g['folder'][3:-12] + g['folder'][-2:], g['result'], g['last'], u, nat[0], nat[1], rams[0][0], rams[0][1], rams[0][2], rams[1][0], rams[1][1], rams[1][2], other[0], other[1], '; '.join(q)))
