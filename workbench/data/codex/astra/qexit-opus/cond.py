"""qexit-opus: how often the QUEEN_ONE_EXIT condition (true board, radius 4) held on her turns, and before her deaths.
cond 1 = she stepped by choice into a cell with one way on and a visible enemy head within 4 of it, no clean other step;
cond 2 = same and another step without that problem existed (the switch would have changed the move)."""
import sys, json
from collections import Counter
games, rows, seen = [], [], set()
for f in sys.argv[1].split(','):
    for l in open(f):
        try:
            d = json.loads(l)
        except Exception:
            continue
        k = ('g', d['game']) if 'game' in d else (d['gid'], d['r'])
        if k in seen:
            continue
        seen.add(k)
        (games if 'game' in d else rows).append(d)
t = [sum(g['stats'][i] for g in games) for i in range(3)]
print('games %d, queen turns %d, cond1 (no clean other step) %d, cond2 (switch would change the move) %d = %.2f per game, %.2f%% of her turns' % (
    len(games), sum(t), t[1], t[2], t[2] / max(1, len(games)), 100.0 * t[2] / max(1, sum(t))))
c = Counter()
for d in rows:
    h = d.get('cond_hist', [])
    f1 = d.get('f1')
    oneway = f1 is not None and f1 <= 1 and not d.get('split1')
    kind = 'one-way death' if oneway else 'other death'
    last3 = h[-4:-1] + h[-1:]
    w = 'cond2 in her last 4 turns' if 2 in h[-4:] else 'cond2 in turns 5-9 before' if 2 in h else 'cond1 only (no clean step)' if 1 in h[-4:] else 'never in her last 9 turns'
    c[(kind, w)] += 1
for k, n in sorted(c.items()):
    print('%3d  %s | %s' % (n, k[0], k[1]))
