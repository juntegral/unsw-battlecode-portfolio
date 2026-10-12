"""qdeath.py <arm>: our queen's death record, and her length round by round after the enemy queen died (from splits/eats/paids)."""
import sys, json
from pathlib import Path
HERE = Path('data/codex/astra/qdead-opus')
for arm in sys.argv[1:]:
    print('==', arm)
    for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines():
        g = json.loads(l)
        qd = {0: None, 1: None}
        for d in g['deaths']:
            if d[6] and qd[d[1]] is None:
                qd[d[1]] = d
        if qd[1] is None or qd[0] is None or qd[0][0] < qd[1][0]:
            continue
        d = qd[0]
        rf = qd[1][0]
        ev = [('split', s[0], s[2], s[3]) for s in g['splits'] if s[1] == 0 and s[5] and s[0] >= rf]
        ev += [('paid', p[0], p[2], p[3]) for p in g['paids'] if p[1] == 0 and p[6] and p[0] >= rf]
        ev += [('eat-' + e[3], e[0], e[5], 0) for e in g['eats'] if e[1] == 0 and e[2] == 'q' and e[0] >= rf]
        ev.sort(key=lambda e: e[1])
        near = [x for x in g['deaths'] if x[1] == 0 and abs(x[0] - d[0]) <= 3 and not x[6]]
        print(' %s foeQ r%d | ourQ r%d %s L%d free sides %d mates5 %d foes5 %d rammer [L, steps, paid, gap, byqueen] %s | mates dying within 3 rounds %s' % (
            g['folder'][3:], rf, d[0], d[4], d[2], d[5], d[8], d[9], d[18], [(x[0], x[4], x[2]) for x in near]))
        print('    ', ' '.join('%s@%d(L%d%s)' % (e[0], e[1], e[2], '>%d' % e[3] if e[3] else '') for e in ev))
