"""Scratch (diag-theirqueen): one game's two queens side by side from tq_scan-*.jsonl.
Usage: python3 tq_view.py <game> [every N rounds, default 10] [last K turns of our queen, default 8]"""
import sys
import json
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
F = dict(r=0, head=1, L=2, ds=3, o5=5, ep3n=27, ep5n=31, pd=35, ate=22, end=23, steps=20, act=19, nown=33, nen=34, kc=13)


def main():
    gid = int(sys.argv[1])
    every = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    last = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    g = None
    for t in ('m1', 'm2', 'b1', 'b2', 'q1'):
        for line in (W / ('tq_scan-%s.jsonl' % t)).read_text().splitlines():
            if line.startswith('{"game":%d,' % gid):
                g = json.loads(line)
    w, h = g['w'], g['h']
    xy = lambda c: '(%d,%d)' % (c % w, c // w)
    print(g['game'], g['label'], g['map'], w, h, 'vs', g['opp'], 'win', g['win'], g['decided'], 'R', min(8, (w + h) // 8), 'starts', xy(g['start'][0]), xy(g['start'][1]))
    print('fates', g['fate'][0], g['fate'][1])
    by = [dict((t[0], t) for t in g['recs'][s]) for s in (0, 1)]
    fmt = lambda t: '-' if t is None else '%s L%d d%d own5 %d en5 %d pearl %s own %d' % (xy(t[F['head']]), t[F['L']], t[F['ds']], t[F['o5']], t[F['ep5n']], t[F['pd']], t[F['nown']])
    rounds = sorted(set(list(range(0, g['last'] + 1, every))))
    for r in rounds:
        a, b = by[0].get(r), by[1].get(r)
        if a is None and b is None:
            continue
        print('r%-3d ours %-46s | theirs %s' % (r, fmt(a), fmt(b)))
    print('our last turns:')
    for t in g['recs'][0][-last:]:
        print('  r%d %s -> %s L%d steps %d act %d ate %d d%d own5 %d en3 %d en5 %d kelp %d' % (
            t[0], xy(t[F['head']]), xy(t[F['end']]) if t[F['end']] >= 0 else 'dead', t[F['L']], t[F['steps']], t[F['act']], t[F['ate']], t[F['ds']], t[F['o5']],
            t[F['ep3n']], t[F['ep5n']], t[F['kc']]))


main()
