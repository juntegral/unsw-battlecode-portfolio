"""qexit-opus: for queen deaths by an enemy ram: risk of the cell she chose at her last turn against her other free cells.
risk 2 = inside a visible enemy head's free steps, 1 = inside its paid reach (max 4), 0 = outside; torus distance, walls ignored."""
import sys, json
from collections import Counter
seen = set()
rows = []
for f in sys.argv[1].split(','):
    for l in open(f):
        try:
            d = json.loads(l)
        except Exception:
            continue
        if 'game' in d or (d['gid'], d['r']) in seen:
            continue
        seen.add((d['gid'], d['r']))
        rows.append(d)
c = Counter()
ex = {}
tot = 0
for d in rows:
    if d['own_turn'] or d['att'][0] != 'foe':
        continue
    tot += 1
    o = d.get('opts')
    if o is None:
        c['no history'] += 1
        continue
    dirs = d.get('dirs') or []
    if d.get('split1'):
        key = 'she split on her last turn'
    elif len(dirs) != 1:
        key = 'she moved %d steps' % len(dirs)
    else:
        ch = [x for x in o if x[0] == dirs[0]]
        chosen = ch[0][2] if ch else -9
        alts = [x[2] for x in o if x[1] == 'free' and x[0] != dirs[0]]
        best = min(alts) if alts else None
        vis = 'attacker in her view' if d.get('seen_q') == 1 else 'attacker not in her view'
        key = '%s | chose risk %d | best other free cell: %s' % (vis, chosen, 'none' if best is None else 'risk %d' % best)
        if d.get('att_is_queen'):
            key += ' | attacker = their queen'
    c[key] += 1
    ex.setdefault(key, []).append('%s:r%d' % (d['gid'], d['r']))
print('queen deaths by an enemy ram:', tot, 'of', len(rows), 'queen deaths')
for k, n in c.most_common():
    print('%3d  %s   e.g. %s' % (n, k, ' '.join(ex.get(k, [])[:3])))
