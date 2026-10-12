# Scratch (diag-opening): what follows a big one-way step against a loop-back step when both were free (op_scan5-*.jsonl).
# Pooled inside a layout, then the mean over layouts that have 10+ turns of each kind for that bot (equal weight).
# Usage: python3 data/analysis/ladder/dossier/work/op_agg5.py
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
FILES = ['op_scan5-O0.jsonl', 'op_scan5-O1.jsonl', 'op_scan5-O2.jsonl', 'op_scan5-O3.jsonl',
         'op_scan5-R0.jsonl', 'op_scan5-R1.jsonl', 'op_scan5-R2.jsonl', 'op_scan5-R3.jsonl']


def main():
    acc = defaultdict(lambda: [0] * 5)
    for f in FILES:
        if not Path(W + f).exists():
            print('missing', f)
            continue
        for line in open(W + f):
            if not line.strip():
                continue
            g = json.loads(line)
            for s, tag in (('u', g['who']), ('t', g['who'] + 'o')):
                for key, v in g['sides'][s]['picks'].items():
                    cls, ctx = key.split('|')
                    for c in (ctx, 'all'):
                        a = acc[(tag, g['layout'], cls, c)]
                        for j in range(5):
                            a[j] += v[j]
    layouts = sorted({k[1] for k in acc})
    for ctx in ('all', 'N', 'P'):
        print('== in view:', ctx, '== bot: turns big/way | pearls in 10 rounds big/way | in 20 | dead within 10 % big/way | within 20 % | layouts where big is higher: pearls20, dead20')
        for tag in ('O', 'R', 'Oo', 'Ro'):
            tot = {c: [0] * 5 for c in ('big', 'way')}
            rows = []
            for l in layouts:
                b, w = acc.get((tag, l, 'big', ctx)), acc.get((tag, l, 'way', ctx))
                if b:
                    for j in range(5):
                        tot['big'][j] += b[j]
                if w:
                    for j in range(5):
                        tot['way'][j] += w[j]
                if b and w and b[0] >= 10 and w[0] >= 10:
                    rows.append((l, [b[j] / b[0] for j in range(1, 5)], [w[j] / w[0] for j in range(1, 5)]))
            n = len(rows)
            if not n:
                continue
            mb = [sum(r[1][j] for r in rows) / n for j in range(4)]
            mw = [sum(r[2][j] for r in rows) / n for j in range(4)]
            hi_p = sum(1 for r in rows if r[1][1] > r[2][1])
            hi_d = sum(1 for r in rows if r[1][3] > r[2][3])
            print('%-3s turns %5d/%5d | %.3f/%.3f | %.3f/%.3f | %4.1f/%4.1f | %4.1f/%4.1f | %d and %d of %d   pooled: p20 %.3f/%.3f dead20 %.1f/%.1f' % (
                tag, tot['big'][0], tot['way'][0], mb[0], mw[0], mb[1], mw[1], 100 * mb[2], 100 * mw[2], 100 * mb[3], 100 * mw[3], hi_p, hi_d, n,
                tot['big'][2] / max(1, tot['big'][0]), tot['way'][2] / max(1, tot['way'][0]), 100.0 * tot['big'][4] / max(1, tot['big'][0]), 100.0 * tot['way'][4] / max(1, tot['way'][0])))
            if ctx == 'all' and tag in ('O', 'R'):
                for l, b, w in rows:
                    print('      %-22s p20 %.2f/%.2f dead20 %4.1f/%4.1f' % (l, b[1], w[1], 100 * b[3], 100 * w[3]))


main()
