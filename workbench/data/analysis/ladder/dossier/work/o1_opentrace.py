"""Scratch (job C): print traces. Usage: o1_opentrace.py <set> <map substring> [full]"""
import sys, json
from collections import defaultdict
W = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
spec, mp = sys.argv[1], sys.argv[2]
full = len(sys.argv) > 3
for g in map(json.loads, open(W + 'o1_open-%s.jsonl' % spec)):
    if mp.lower() not in g['map'].lower():
        continue
    w, h = g['w'], g['h']
    print('==', spec, g['gid'], g['map'], '%dx%d' % (w, h), 'v', g['opp'], '| meals ours', g['meals'][0], 'theirs', g['meals'][1])
    by = defaultdict(list)
    for t in g['turns']:
        by[(t[1], t[2])].append(t)
    for (s, i), ts in sorted(by.items()):
        t0 = ts[0]
        x0, y0 = None, None
        def dist(a, b):
            dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
            return min(dx, w - dx) + min(dy, h - dy)
        mv = [t for t in ts if t[6] in ('straight', 'turn', 'portal', 'first')]
        start = (ts[0][12], ts[0][13])
        disp = {r: None for r in (5, 10, 20, 30)}
        for t in ts:
            for r in disp:
                if t[0] <= r:
                    disp[r] = dist(start, (t[12], t[13]))
        eat = [t[0] for t in ts if t[14]]
        print('  %s id %2d %s%s born r%d L%d: turns %d straight %d turn %d portal %s split %s | blind %d | own-new %d side-new %d | from first tile at r5/10/20/30 %s | meals %s' % (
            'ours  ' if s == 0 else 'theirs', i, 'starter' if t0[3] else 'child  ', ' QUEEN' if t0[4] else '', t0[0] - (t0[15] if t0[15] >= 0 else t0[0]), t0[5], len(ts),
            sum(t[6] == 'straight' for t in ts), sum(t[6] == 'turn' for t in ts), [t[0] for t in ts if t[6] == 'portal'], [t[0] for t in ts if t[6] == 'split'],
            sum(1 for t in ts if not t[8]), sum(t[9] for t in ts), sum(t[10] for t in ts), [disp[r] for r in (5, 10, 20, 30)], eat))
        if full:
            print('      ' + ' '.join('%d:%d,%d%s%s' % (t[0], t[12], t[13], {'straight': '', 'turn': 't', 'portal': 'P', 'split': 'S', 'still': '=', 'first': '', 'died': 'X'}[t[6]], '*' if t[14] else ('.' if t[8] else '')) for t in ts))
