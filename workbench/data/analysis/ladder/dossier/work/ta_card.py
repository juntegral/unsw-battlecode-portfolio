"""Scratch (diag-topaah): the card table. A pearl beside the head after round 100 (ta_s4-*.jsonl; columns as ta_s4agg.py).
lone = not the queen, not the side's longest, no own head beside the pearl, no enemy head within 3 tiles, the pearl not through a portal,
       2 or more free tiles beside the head.  feeding = round over 400, or round over 200 with 56+ own dragons (main.cpp 5002-5005)."""
import json
from collections import Counter
from pathlib import Path

WORK = 'data/analysis/ladder/dossier/work/'
TAGS = ('q', 'm', 't', 'a', 'l', 'c1', 'g')


def lone(r):
    return not r[2] and not r[3] and not r[9] and not r[25] and r[14] == 0 and r[18] >= 4 and r[20] >= 2


def feeding(r):
    return r[0] > 400 or (r[0] > 200 and r[7] >= 56)


def phase(r):
    grow = 300 if r[12] <= 1200 else 150
    if feeding(r):
        if r[1] * 2 <= r[4] and r[5] <= 15:
            return '4 feeding, within 15 of longest, pearl within 9' if r[6] <= 9 else '3 feeding, within 15 of longest, pearl farther'
        return '2 feeding, elsewhere'
    return '1 leader round passed' if r[0] > grow else '0 before leader round'


def room(r):
    return '0 nook' if r[10] == 0 else '1 under L+2' if r[10] < r[1] + 2 else '2 L+2 to 3L+7' if r[10] < 3 * r[1] + 8 else '3 3L+8 or more'


def main():
    out = {}
    for tag in TAGS:
        p = Path(WORK + 'ta_s4-' + tag + '.jsonl')
        if not p.exists():
            continue
        gs = [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
        n = len(gs)
        rows = [r for g in gs for r in g['rows']]
        res = {}
        allr = len(rows)
        res['all: taken %'] = (100 * sum(1 for r in rows if r[11] == 0) / max(1, allr), allr)
        res['all: not taken a game'] = ((allr - sum(1 for r in rows if r[11] == 0)) / n, allr)
        ln = [r for r in rows if lone(r)]
        for key, f in (('room', room), ('phase', phase)):
            sub = ln if key == 'room' else [r for r in ln if r[10] >= 3 * r[1] + 8 and r[1] <= 3]
            c, t = Counter(), Counter()
            for r in sub:
                k = f(r)
                c[k] += 1
                t[k] += r[11] == 0
            for k in c:
                res['%s: %s' % (key, k)] = (100 * t[k] / c[k], c[k], (c[k] - t[k]) / n)
        fd = [r for r in rows if feeding(r) and not r[2] and not r[3] and r[10] > 0]
        res['feeding, not queen/longest, not a nook: taken %'] = (100 * sum(1 for r in fd if r[11] == 0) / max(1, len(fd)), len(fd), sum(1 for r in fd if r[11] != 0) / n)
        nf = [r for r in rows if not feeding(r) and not r[2] and not r[3] and r[10] > 0]
        res['not feeding, same: taken %'] = (100 * sum(1 for r in nf if r[11] == 0) / max(1, len(nf)), len(nf), sum(1 for r in nf if r[11] != 0) / n)
        fg = sum(1 for g in gs if any(feeding(r) for r in g['rows']))
        res['games with a feeding-phase row'] = (fg, n)
        out[tag] = (n, res)
    keys = []
    for tag in out:
        for k in out[tag][1]:
            if k not in keys:
                keys.append(k)
    print('%-58s' % 'games' + ''.join('%16s' % ('%s (%d)' % (t, out[t][0])) for t in out))
    for k in sorted(keys):
        line = '%-58s' % k
        for t in out:
            v = out[t][1].get(k)
            if v is None:
                line += '%16s' % '-'
            elif len(v) == 3:
                line += '%16s' % ('%.0f%% n%d m%.1f' % v)
            else:
                line += '%16s' % ('%.1f of %d' % v)
        print(line)
    print('cell = taken % , n turns, m = not taken a game')


main()
