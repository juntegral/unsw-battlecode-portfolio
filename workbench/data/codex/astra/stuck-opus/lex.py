"""stuck-opus: sampled loop rounds (every 10th round) of ours with the nearest pearl. Usage (ROOT): python3 -B data/codex/astra/stuck-opus/lex.py <rows name> [...]"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from pathlib import Path
from collections import Counter
from ladder_replay import replay
from geom import geometry
HERE = Path('data/codex/astra/stuck-opus')
SM = Path('data/online/smoke')
RUNS = Path.home() / 'meow-redteam/solo/runs'
c = Counter()
shown = Counter()
for n in sys.argv[1:]:
    for l in (HERE / ('rows-%s.jsonl' % n)).read_text().splitlines():
        g = json.loads(l)
        if not g['lex']:
            continue
        rp = SM / (n + '-old') / ('M%s.replay' % g['gid']) if n.startswith('one') else RUNS / n / g['gid'] / 'game.replay'
        G = geometry(replay.load(rp).root().text(0))
        for cat, i, rnd, hx, hy, px, py, fd, age, L in g['lex']:
            depth = G['dead'].get(py * G['W'] + px, 0)
            walls = sum(G['wall'](px, py, d) for d in range(4))
            k = (cat, 'tip' if depth == 1 else 'deeper' if depth > 1 else 'open', 'age<10' if age < 10 else 'age10-49' if age < 50 else 'age50+', 'd<=3' if fd <= 3 else 'd4-12')
            c[k] += 1
            c[(cat, 'ALL')] += 1
            c[(cat, 'L%d' % min(L, 5))] += 1
            c[(cat, 'walls%d' % walls)] += 1
            if shown[(g['key'], cat)] < 2:
                shown[(g['key'], cat)] += 1
                print('%-26s %-16s %-7s id %4d r%3d head (%d,%d) L%d pearl (%d,%d) steps %d age %d depth %d walls %d' % (g['key'], g['map'], cat, i, rnd, hx, hy, L, px, py, fd, age, depth, walls))
print()
for k in sorted(c):
    print(k, c[k])
