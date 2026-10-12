"""stuck-opus: profile of episodes. Usage (ROOT): python3 -B data/codex/astra/stuck-opus/prof.py <pattern> <rows name> [...]"""
import sys, json
sys.dont_write_bytecode = True
from collections import Counter
from pathlib import Path
HERE = Path('data/codex/astra/stuck-opus')
pat = sys.argv[1]
gs = []
for n in sys.argv[2:]:
    gs += [json.loads(l) for l in (HERE / ('rows-%s.jsonl' % n)).read_text().splitlines()]
print(pat, len(gs), 'games')
for side in (0, 1):
    c = Counter()
    tot = 0
    alive = sum(g['cnt'][side][ro][ph]['n'] for g in gs for ro in range(2) for ph in range(3))
    for g in gs:
        for e in g['eps']:
            if e['p'] != pat or e['side'] != side:
                continue
            n = e['r1'] - e['r0'] + 1
            tot += n
            c['role %s' % ('queen' if e['role'] == 0 else 'other')] += n
            c['L0 %d' % min(e['L0'], 6)] += n
            c['start r%03d' % (e['r0'] // 100 * 100)] += n
            c['pearl<=10 share>.5 %s' % (e['pearl'] > 0.5)] += n
            c['enemy<=6 share>.5 %s' % (e['enemy'] > 0.5)] += n
            c['portal<=2 share>.5 %s' % (e['portal'] > 0.5)] += n
            c['dur %03d+' % (min(n // 50, 6) * 50)] += n
            c['cells %02d+' % (min(e['cells'] // 4, 6) * 4)] += n
    print('side', 'US' if side == 0 else 'THEM', 'flagged', tot, 'of', alive, '= %.1f%%' % (100 * tot / max(alive, 1)))
    for k in sorted(c):
        print('    %-28s %7d %5.1f%% of alive' % (k, c[k], 100 * c[k] / max(alive, 1)))
