"""Scratch (diag-bigmap): what 10 rounds with feeding on buy and cost, inside the same games. A window of 10 rounds
is "on" when our count is 56 or more at its first round (main.cpp 5002-5005) and "off" otherwise. Per window: change
of our longest dragon, of our total length and of our count, our feeders, pearls we eat, and whether one of our
dragons of 10+ was rammed in it. Also the opponents' windows by their own longest, and rounds off per game.
Usage: python3 data/analysis/ladder/dossier/work/bm_win.py [O|L] [min cells]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from statistics import median, mean

WORK = Path('data/analysis/ladder/dossier/work')


def load(src, lo):
    rows = []
    for p in sorted(WORK.glob('bm_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            if g['cells'] > lo:
                rows.append(g)
    rows.sort(key=lambda g: g['gid'])
    return rows


def windows(g, a, b):
    out = []
    rc = dict((row[0], row[1:]) for row in g['rc'])
    for r0 in range(a, b, 10):
        r1 = r0 + 10
        if r1 > g['last']:
            break
        s0, s1 = g['snap'][r0], g['snap'][r1]
        ds = [d for d in g['deaths'] if r0 < d['r'] <= r1]
        eat = [0, 0, 0, 0]
        for r in range(r0 + 1, r1 + 1):
            v = rc.get(r)
            if v:
                eat[0] += v[2]
                eat[1] += v[3]
                eat[2] += v[8]
                eat[3] += v[9]
        out.append(dict(r0=r0, on=s0[0] >= 56, n0=s0[0], dL=s1[2] - s0[2], dT=s1[1] - s0[1], dN=s1[0] - s0[0], L0=s0[2],
                        dLt=s1[6] - s0[6], dTt=s1[5] - s0[5], Lt0=s0[6], nt0=s0[4],
                        fed=sum(1 for d in ds if d['s'] == 0 and d.get('fed')), fedt=sum(1 for d in ds if d['s'] == 1 and d.get('fed')),
                        bigram=sum(1 for d in ds if d['s'] == 0 and d['L'] >= 10 and d['c'] == 'head-on' and d.get('cross') and d.get('role') == 'hit'),
                        bigramt=sum(1 for d in ds if d['s'] == 1 and d['L'] >= 10 and d['c'] == 'head-on' and d.get('cross') and d.get('role') == 'hit'),
                        nat=eat[0], drop=eat[1], natt=eat[2], dropt=eat[3], q=int(s0[3] > 0)))
    return out


def show(name, ws):
    if not ws:
        return
    n = len(ws)
    calm = [w for w in ws if not w['bigram']]
    print('  %-34s windows %4d; per 100 rounds: longest %+6.1f (no 10+ of ours rammed in the window: %+6.1f, %d windows); total %+7.1f; count %+6.1f; feeders %5.1f; natural pearls %6.1f; dropped pearls %6.1f; a 10+ of ours rammed %.2f' % (
        name, n, 10 * mean(w['dL'] for w in ws), 10 * mean(w['dL'] for w in calm) if calm else 0, len(calm), 10 * mean(w['dT'] for w in ws), 10 * mean(w['dN'] for w in ws), 10 * mean(w['fed'] for w in ws), 10 * mean(w['nat'] for w in ws), 10 * mean(w['drop'] for w in ws), 10 * mean(w['bigram'] for w in ws)))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'O'
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
    rows = load(src, lo)
    sets = [('ALL', rows)]
    if src == 'O':
        sets = [('MAIN', [g for g in rows if g['arm'] == 'MAIN']), ('B7+B7Q', [g for g in rows if g['arm'] != 'MAIN'])]
    for name, gs in sets:
        print()
        print('=====', name, len(gs), 'games')
        for a, b in ((200, 300), (300, 400), (400, 490)):
            ws = [w for g in gs for w in windows(g, a, b)]
            print(' rounds %d-%d' % (a, b))
            show('ours, on (56 or more)', [w for w in ws if w['on']])
            show('ours, off, 40 to 55', [w for w in ws if not w['on'] and w['n0'] >= 40])
            show('ours, off, under 40', [w for w in ws if w['n0'] < 40])
            show('ours, off, 40 to 55, queen dead', [w for w in ws if not w['on'] and w['n0'] >= 40 and not w['q']])
            show('ours, off, 40 to 55, queen alive', [w for w in ws if not w['on'] and w['n0'] >= 40 and w['q']])
            n = len(ws)
            print('  theirs: windows %d; per 100 rounds: longest %+.1f; total %+.1f; feeders %.1f; natural %.1f; dropped %.1f; a 10+ of theirs rammed %.2f' % (
                n, 10 * mean(w['dLt'] for w in ws), 10 * mean(w['dTt'] for w in ws), 10 * mean(w['fedt'] for w in ws), 10 * mean(w['natt'] for w in ws), 10 * mean(w['dropt'] for w in ws), 10 * mean(w['bigramt'] for w in ws)))
        off = []
        for g in gs:
            cnt = [x[0] for x in g['snap']]
            o3 = sum(1 for r in range(301, min(400, g['last']) + 1) if cnt[r] < 56)
            o2 = sum(1 for r in range(201, min(300, g['last']) + 1) if cnt[r] < 56)
            off.append((g['gid'], o2, o3, int(g['snap'][min(300, g['last'])][3] > 0)))
        print(' rounds with our count under 56: in r201-300 median %g, mean %.1f; in r301-400 median %g, mean %.1f; games with 50+ such rounds in r301-400: %d of %d; our queen alive at r300 in %d' % (
            median(x[1] for x in off), mean(x[1] for x in off), median(x[2] for x in off), mean(x[2] for x in off), sum(1 for x in off if x[2] >= 50), len(off), sum(x[3] for x in off)))
        print(' rounds under 56 in r301-400, queen dead at r300 only: mean %.1f over %d games' % (mean([x[2] for x in off if not x[3]] or [0]), sum(1 for x in off if not x[3])))


main()
