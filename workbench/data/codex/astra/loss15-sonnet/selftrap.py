"""count own-turn queen deaths (reason 0 wall / 1 own body / 2 other body) in qexit-opus qdeath-*.jsonl, by version, with f1 (free cells at last turn start)"""
import json, glob
from collections import Counter
c = Counter()
rows = []
for f in glob.glob('data/codex/astra/qexit-opus/qdeath-*.jsonl'):
    for l in open(f):
        d = json.loads(l)
        if 'gid' not in d or 'own_turn' not in d:
            continue
        if (d['gid'], d['r']) in globals().setdefault('_s', set()):
            continue
        _s.add((d['gid'], d['r']))
        c[d.get('ver'), 'all'] += 1
        if d['own_turn']:
            c[d.get('ver'), 'own', d['reason'], 'f1=%s' % d.get('f1')] += 1
            rows.append((d.get('ver'), d['gid'], d['map'], d['r'], d['L'], d['reason'], d.get('f1'), d.get('f0'), d.get('split0'), d.get('opp')))
for k in sorted(c, key=str):
    print(k, c[k])
for r in sorted(rows, key=str):
    print(r)
