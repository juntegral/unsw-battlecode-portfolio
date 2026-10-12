import json, sys
from collections import Counter
W = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
def centre(g):
    return g['cells'] <= 1000 and (g['w'] >= 2 * g['h'] or g['cells'] <= 700)
for spec in sys.argv[1:]:
    for cls in ('small centre', 'small other', 'big'):
        gs = []
        for nm in spec.split('+'):
            gs += [g for g in map(json.loads, open(W + 'o1_after-%s.jsonl' % nm))]
        gs = [g for g in gs if (cls == 'big') == (g['cells'] > 1200) and (cls == 'big' or centre(g) == (cls == 'small centre'))]
        n = len(gs)
        print('==', spec, cls, n, 'games', sorted({g['map'] for g in gs}))
        for s, nm in ((0, 'ours'), (1, 'theirs')):
            c = Counter()
            for g in gs:
                for r in g['recs']:
                    if r['s'] != s or len(r['d']) < 6:
                        continue
                    fast = 0 <= r['born'] <= 6
                    c['meals'] += 1
                    c['fast'] += fast
                    if not fast:
                        continue
                    b = r['born']
                    dd = r['d'][b - 1] if 1 <= b <= 6 else None
                    if dd is None:
                        continue
                    c['f'] += 1
                    if dd < 0:
                        c['dead'] += 1
                        continue
                    c['alive'] += 1
                    c['at1'] += dd <= 1; c['at2-3'] += 2 <= dd <= 3; c['at4+'] += dd >= 4
                    if dd >= 4:
                        c['left: pearl in view'] += r['pearl'] == 1
                        c['left: enemy head in view'] += r['pearl'] != 1 and r['foe'] == 1
                        c['left: neither'] += r['pearl'] != 1 and r['foe'] != 1
                    if r['next']:
                        c['next same side'] += r['next'][0] == s
                        c['next other side'] += r['next'][0] != s
                        c['next same dragon'] += r['next'][2]
                        if r['next'][0] == s:
                            c['next delay'] += r['next'][1]; c['next n'] += 1; c['next<=1'] += r['next'][1] <= 1
            a = max(1, c['alive'])
            if c['meals']:
                print('  %-6s meals %.1f a game; tile reborn within 6 rounds %.0f%% | eater at that birth (alive %d): within 1 step %.0f%%, 2-3 %.0f%%, 4+ %.0f%% | of the 4+: another pearl in view %.0f%%, enemy head in view %.0f%%, neither %.0f%% | the new pearl: same dragon %.0f%%, eaten by the side within 1 round %.0f%%, mean %.1f rounds, lost to the other side %.0f%%' % (
                    nm, c['meals'] / n, 100 * c['fast'] / c['meals'], c['alive'], 100 * c['at1'] / a, 100 * c['at2-3'] / a, 100 * c['at4+'] / a,
                    100 * c['left: pearl in view'] / max(1, c['at4+']), 100 * c['left: enemy head in view'] / max(1, c['at4+']), 100 * c['left: neither'] / max(1, c['at4+']),
                    100 * c['next same dragon'] / max(1, c['f']), 100 * c['next<=1'] / max(1, c['f']), c['next delay'] / max(1, c['next n']), 100 * c['next other side'] / max(1, c['f'])))
