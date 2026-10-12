"""qmate-opus: boxed-on-own-move queen deaths whose box has a mate wall. Usage (repo root): python3 -B .../pick.py"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/codex/astra/qexit-opus')
sys.path.insert(0, 'data/codex/astra/qmate-opus'); from qcls import cls
from collections import Counter
seen, rows = set(), []
for f in ('qdeath-live.jsonl', 'qdeath-smoke.jsonl'):
    for l in open('data/codex/astra/qexit-opus/' + f):
        d = json.loads(l)
        if 'game' in d or (d['gid'], d['r']) in seen:
            continue
        seen.add((d['gid'], d['r']))
        rows.append(d)
print(len(rows), 'rows; keys', sorted(rows[0].keys()))
c = Counter()
for d in rows:
    if not d['own_turn'] or d.get('f1') != 0:
        continue
    s1 = d.get('start1') or []
    mates = [x for x in s1 if x and x[0] == 'mate']
    k, x = cls(d)
    c[k[:2], bool(mates)] += 1
    if mates:
        print(d['ver'], d['src'], d['gid'], d['map'], 'r', d['r'], 'L', d.get('len'), k[:3], x, '| start1', s1, '| start0', d.get('start0'), '| closers', d.get('closers'), '| f0', d.get('f0'), 'f0a', d.get('f0a'))
print(c)
