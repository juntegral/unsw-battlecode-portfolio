"""Ledger every 25 rounds for each game: dragons/total/longest/queen per side, pearls eaten by origin, deaths by cause.
Usage: python3 -B data/codex/astra/h2hloss-opus/ledger.py <arm> [loss|win|all] [folder substring]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
arm = sys.argv[1]
which = sys.argv[2] if len(sys.argv) > 2 else 'loss'
sub = sys.argv[3] if len(sys.argv) > 3 else ''
for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines():
    g = json.loads(l)
    if which != 'all' and g['result'] != which:
        continue
    if sub not in g['folder']:
        continue
    print('=== %s %s | %s %s | %s' % (arm, g['folder'], g['result'], g['how'], g['resline']))
    rs = sorted(int(r) for r in g['snaps'])
    eat = defaultdict(Counter)
    for r, s, role, origin, kd, L0 in g['eats']:
        eat[(min((r - 1) // 25 + 1, 99) if r > 0 else 0, s)][origin] += 1
    dth = defaultdict(list)
    for d in g['deaths']:
        dth[((d[0] - 1) // 25 + 1 if d[0] > 0 else 0, d[1])].append(d)
    # behind-for-good round on the deciding measure
    def key(row, s):
        return (row[s][3], row[s][2], row[s][1])
    behind = None
    for r in rs:
        v = g['snaps'][str(r)]
        if key(v, 0) < key(v, 1):
            if behind is None:
                behind = r
        else:
            behind = None
    print('  behind for good (queen, longest, total) from snapshot r%s' % behind)
    print('  r   | new: n tot long q | old: n tot long q | new eats n/own/foe | old eats n/own/foe | new deaths | old deaths')
    for r in rs:
        v = g['snaps'][str(r)]
        b = (r - 1) // 25 + 1 if r > 0 else 0
        def ds(s):
            c = Counter()
            for d in dth[(b, s)]:
                c[d[4]] += 1
            L = sum(d[2] for d in dth[(b, s)])
            big = ['%s%d%s' % (d[4][:4], d[2], 'Q' if d[6] else '') for d in dth[(b, s)] if d[2] >= 6 or d[6]]
            return '%d(L%d) %s %s' % (len(dth[(b, s)]), L, dict(c), big)
        print('  %3d | %2d %3d %3d %2d | %2d %3d %3d %2d | %2d/%2d/%2d | %2d/%2d/%2d | %s | %s' % (
            r, v[0][0], v[0][1], v[0][2], v[0][3], v[1][0], v[1][1], v[1][2], v[1][3],
            eat[(b, 0)]['n'], eat[(b, 0)]['own'], eat[(b, 0)]['foe'], eat[(b, 1)]['n'], eat[(b, 1)]['own'], eat[(b, 1)]['foe'], ds(0), ds(1)))
