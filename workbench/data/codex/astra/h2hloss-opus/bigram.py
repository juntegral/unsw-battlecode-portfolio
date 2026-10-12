"""Long dragons rammed by short ones: victims by length class (5-14, 15+), rammer 2-4, by the distance at the start of the rammer's move.
Exposure = dragon turns of that class (from turns-*.jsonl when present). Usage: bigram.py"""
import json
from collections import Counter
from pathlib import Path
HERE = Path('data/codex/astra/h2hloss-opus')
for arm in ('h2h_mDone11_v8', 'h2h_mDone10_v8', 'h2h_mDone8_v5', 'h2h_mDone11_v5'):
    gs = [json.loads(l) for l in (HERE / ('scan-%s.jsonl' % arm)).read_text().splitlines()]
    tf = HERE / ('turns-%s.jsonl' % arm)
    ex = Counter()
    if tf.exists():
        for l in tf.read_text().splitlines():
            t = json.loads(l)
            for k, v in t['T'].items():
                s, role, lc, ph, pd, foe = k.split('|')
                if role == 'o':
                    ex[(int(s), lc)] += v[0]
    print('== %s (%d games)' % (arm, len(gs)))
    for cls, lo, hi in (('5-14', 5, 14), ('15+', 15, 999), ('30+', 30, 999)):
        for s, nm in ((0, 'NEW'), (1, 'old')):
            rr = [d for g in gs for d in g['deaths'] if d[1] == s and d[4] == 'rammed' and not d[6] and lo <= d[2] <= hi and d[18]]
            sm = [d for d in rr if d[18][0] <= 4]
            gapc = Counter(min(d[18][3], 5) for d in sm)
            rl = Counter(d[18][0] for d in sm)
            allc = sum(d[2] for d in rr)
            print('  victims %-4s %s: rammed %d (length %d); by a rammer of 2-4: %d (length %d), rammer length %s, distance before the move 1:%d 2:%d 3:%d 4:%d 5+:%d; by 5+: %d' % (
                cls, nm, len(rr), allc, len(sm), sum(d[2] for d in sm), dict(sorted(rl.items())), gapc[1], gapc[2], gapc[3], gapc[4], gapc[5], len(rr) - len(sm)))
    if ex:
        print('  exposure, non-queen dragon turns 5-9 / 10+: NEW %d / %d, old %d / %d' % (ex[(0, '5')], ex[(0, '10')], ex[(1, '5')], ex[(1, '10')]))
