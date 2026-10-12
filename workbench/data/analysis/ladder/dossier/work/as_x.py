"""Scratch (diag-aahsplit): cross-tabs of the split rate over turns of dragons of 4 or longer (as_scan v2 rows).
Usage: python3 as_x.py <tag> <filters,comma> <key> [<key2>]
filters: nq q free boxed nopb pb L4 L5p L5 L68 a<lo>-<hi> r<lo>-<hi> first (first turn at this length) c0 c1 c2 (board size class)
keys: L alive alive2 ea diff tot rt rh ft fh tpd pd ed edt oh since tport hport hd round lng cells percell n3 eats"""
import sys
import json
from collections import Counter
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'
# row: 0 rnd 1 id 2 L 3 alive 4 isq 5 lng 6 fh 7 ft 8 ed 9 edt 10 pd 11 n3 12 oh 13 len_since 14 pearls_since 15 age 16 act 17 n 18 eats 19 died+1
#      20 room_h 21 room_t 22 tpd 23 tport 24 ealive 25 tot 26 hport 27 head-tail distance

KEYS = {
    'L': lambda g, r: min(r[2], 10),
    'alive': lambda g, r: r[3] // 4 * 4,
    'alive2': lambda g, r: r[3] // 2 * 2,
    'alive1': lambda g, r: r[3],
    'ea': lambda g, r: min(r[24], 63) // 8 * 8,
    'diff': lambda g, r: max(-24, min(40, (r[3] - r[24]) // 8 * 8)),
    'sum': lambda g, r: (r[3] + r[24]) // 8 * 8,
    'tot': lambda g, r: min(r[25], 400) // 25 * 25,
    'rt': lambda g, r: r[21] if r[21] < 8 else 8 if r[21] < 12 else 12 if r[21] < 24 else 24,
    'rh': lambda g, r: r[20] if r[20] < 8 else 8 if r[20] < 12 else 12 if r[20] < 24 else 24,
    'ft': lambda g, r: r[7],
    'fh': lambda g, r: r[6],
    'tpd': lambda g, r: r[22],
    'pd': lambda g, r: r[10],
    'ed': lambda g, r: r[8],
    'edt': lambda g, r: r[9],
    'oh': lambda g, r: min(r[12], 5),
    'since': lambda g, r: min(r[13], 6),
    'tport': lambda g, r: r[23],
    'hport': lambda g, r: r[26],
    'hd': lambda g, r: min(r[27], 6),
    'round': lambda g, r: min(r[0], 450) // 50 * 50,
    'lng': lambda g, r: r[5],
    'cells': lambda g, r: 0 if g['w'] * g['h'] <= 700 else 1 if g['w'] * g['h'] <= 1200 else 2,
    'percell': lambda g, r: min(60, g['w'] * g['h'] // max(1, r[3]) // 5 * 5),
    'n3': lambda g, r: min(r[11], 3),
    'eats': lambda g, r: min(r[18], 2),
    'map': lambda g, r: g['map'][:10],
    'steps': lambda g, r: min(r[17], 3),
}


def make_filter(names):
    fs = []
    for n in names:
        if n == 'nq':
            fs.append(lambda g, r: not r[4])
        elif n == 'q':
            fs.append(lambda g, r: r[4])
        elif n == 'free':
            fs.append(lambda g, r: r[6] > 0)
        elif n == 'boxed':
            fs.append(lambda g, r: r[6] == 0)
        elif n == 'nopb':
            fs.append(lambda g, r: r[10] != 1)
        elif n == 'pb':
            fs.append(lambda g, r: r[10] == 1)
        elif n == 'L4':
            fs.append(lambda g, r: r[2] == 4)
        elif n == 'L5p':
            fs.append(lambda g, r: r[2] >= 5)
        elif n == 'L5':
            fs.append(lambda g, r: r[2] == 5)
        elif n == 'L68':
            fs.append(lambda g, r: 6 <= r[2] <= 8)
        elif n == 'first':
            fs.append(lambda g, r: r[13] == 0)
        elif n == 'later':
            fs.append(lambda g, r: r[13] > 0)
        elif n in ('c0', 'c1', 'c2'):
            z = int(n[1])
            fs.append(lambda g, r, z=z: KEYS['cells'](g, r) == z)
        elif n[0] == 'a':
            lo, hi = n[1:].split('-')
            fs.append(lambda g, r, lo=int(lo), hi=int(hi): lo <= r[3] <= hi)
        elif n[0] == 'r':
            lo, hi = n[1:].split('-')
            fs.append(lambda g, r, lo=int(lo), hi=int(hi): lo <= r[0] <= hi)
        elif n[:2] == 'rt':
            fs.append(lambda g, r, lo=int(n[2:]): r[21] >= lo)
        elif n[:2] == 'ft':
            fs.append(lambda g, r, lo=int(n[2:]): r[7] >= lo)
        elif n == 'noport':
            fs.append(lambda g, r: r[23] == 0)
        else:
            print('unknown filter', n)
    return lambda g, r: all(f(g, r) for f in fs)


def main():
    tag = sys.argv[1]
    filt = make_filter([x for x in sys.argv[2].split(',') if x])
    k1 = KEYS[sys.argv[3]]
    k2 = KEYS[sys.argv[4]] if len(sys.argv) > 4 else None
    games = [json.loads(x) for x in Path(WORKREL + 'as_scan-' + tag + '.jsonl').read_text().splitlines() if x]
    c = Counter()
    for g in games:
        for r in g['rows']:
            if len(r) < 28 or not filt(g, r):
                continue
            a = k1(g, r)
            b = k2(g, r) if k2 else 0
            c[a, b, 't'] += 1
            c[a, b, 's'] += int(r[16] >= 2)
    rows = sorted(set(k[0] for k in c), key=lambda v: (str(type(v)), v))
    cols = sorted(set(k[1] for k in c), key=lambda v: (str(type(v)), v))
    print(tag, len(games), 'games; filters', sys.argv[2], '; rows', sys.argv[3], '; cols', sys.argv[4] if k2 else '-', '; cell = splits per 100 turns (turns)')
    print('%10s ' % '' + ' '.join('%14s' % str(b) for b in cols))
    for a in rows:
        print('%10s ' % str(a) + ' '.join(('%6.1f (%5d)' % (100.0 * c[a, b, 's'] / c[a, b, 't'], c[a, b, 't'])) if c[a, b, 't'] else '%14s' % '-' for b in cols))


main()
