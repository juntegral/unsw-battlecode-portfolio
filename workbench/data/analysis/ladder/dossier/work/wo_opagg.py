"""Scratch (diag-wipeout): the first 100 rounds by outcome class. Joins wo_op2 rows to wo_scan rows.
Usage: python3 data/analysis/ladder/dossier/work/wo_opagg.py <O|L|R> [label-prefix]
Classes: OUT = we end with no dragon; KILL = they end with none; REST = neither."""
import sys, json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')


def load(stem, src):
    rows = []
    for p in sorted(WORK.glob(stem + '-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def size(c):
    return '<=700' if c <= 700 else '701-1200' if c <= 1200 else '>1200'


def med(v):
    v = sorted(x for x in v if x is not None)
    return v[len(v) // 2] if v else None


def main():
    src = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else ''
    cls = {}
    for g in load('wo_scan', src):
        cls[g['gid']] = ('OUT' if g['final'][0] == 0 else 'KILL' if g['final'][4] == 0 else 'REST', g['result'])
    rows = [r for r in load('wo_op2', src) if r['src'].startswith(prefix)]
    assert all(r['gid'] in cls for r in rows), 'scan rows missing'
    for sz in ('<=700', '701-1200', '>1200'):
        for c in ('OUT', 'KILL', 'REST'):
            a = [r for r in rows if size(r['cells']) == sz and cls[r['gid']][0] == c]
            if not a:
                continue
            n = len(a)
            print('%s %s %s games %d' % (src, sz, c, n))
            print('   count us/them: ' + ' '.join('r%d %.1f/%.1f' % (r, sum(x['count'].get(str(r), x['count'].get(r, [0, 0]))[0] for x in a) / n,
                                                                    sum(x['count'].get(str(r), x['count'].get(r, [0, 0]))[1] for x in a) / n) for r in (10, 20, 30, 40, 50, 60, 80, 100)))
            print('   seen share us/them: ' + ' '.join('r%d %.2f/%.2f' % (r, sum(x['seen'].get(str(r), [x['cells']] * 2)[0] / x['cells'] for x in a) / n,
                                                                         sum(x['seen'].get(str(r), [x['cells']] * 2)[1] / x['cells'] for x in a) / n) for r in (20, 40, 60, 80)))
            print('   first eat round median us %s them %s | first enemy head in our view median r%s | start gap median %s' % (
                med([x['first_eat'][0] for x in a]), med([x['first_eat'][1] for x in a]), med([x['first_foe'] for x in a]), med([x['start_gap'] for x in a])))
            bo = [sum(x['born'][k] for x in a) / n for k in range(3)]
            au = [sum(x['ate'][0][k] for x in a) / n for k in range(3)]
            at = [sum(x['ate'][1][k] for x in a) / n for k in range(3)]
            print('   natural pearls born by r60 a game: our half %.1f their half %.1f level %.1f | eaten by r80: by us %.1f/%.1f/%.1f, by them %.1f/%.1f/%.1f (our half/their half/level)' % (
                bo[0], bo[1], bo[2], au[0], au[1], au[2], at[0], at[1], at[2]))
            for b in range(5):
                T = [sum(x['B'][b][k] for x in a) for k in range(16)]
                line = '   r%d-%d' % (b * 20, b * 20 + 19 if b < 4 else 100)
                for s, nm in ((0, 'us'), (1, 'them')):
                    t = T[s * 8:s * 8 + 8]
                    line += ' | %s turns %.0f a game, pearl in view %.0f%%, eats/100 turns %.1f, eats/100 in-view turns %.0f, retread %.0f%%, deaths/100 %.2f, splits/100 %.2f, foe in view %.0f%%' % (
                        nm, t[0] / n, 100 * t[1] / max(t[0], 1), 100 * t[2] / max(t[0], 1), 100 * t[2] / max(t[1], 1), 100 * t[4] / max(t[0], 1),
                        100 * t[5] / max(t[0], 1), 100 * t[6] / max(t[0], 1), 100 * t[7] / max(t[0], 1))
                print(line)


main()
