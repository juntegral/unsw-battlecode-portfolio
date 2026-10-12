# Scratch (diag-economy): tables from ec_bot2-*.jsonl (third pass: the bot's own room verdict for the step onto a
# pearl beside the head, dragons of length 2 and 3). Layout means, equal weight; a layout counts for a rate when
# both teams have MINN turns of the class.
# Usage: python3 data/analysis/ladder/dossier/work/ec_bagg.py <verdict|why|whylen|kind|flag|lay|samples> [bands, default 01]
import sys, json
from collections import defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
FILES = ('ec_bot2-O0.jsonl', 'ec_bot2-O1.jsonl', 'ec_bot2-O2.jsonl', 'ec_bot2-R0.jsonl', 'ec_bot2-R1.jsonl', 'ec_bot2-R2.jsonl')
MINN = 30
V = ('trapped', 'tight', 'room')


def load():
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0]))
    samples = defaultdict(list)
    for f in FILES:
        for line in open(W + f):
            r = json.loads(line)
            a = acc[(r['who'], r['layout'])]
            for row in r['acc']:
                v = a[tuple(row[:-7])]
                for z in range(7):
                    v[z] += row[-7 + z]
            samples[(r['who'], r['layout'])].extend(r['samples'])
    return acc, samples


def why(k):
    # key: ('A', band, L, lead, vnow, tlnow, vmt, tlmt, val, tlal, ns, fl, kind, ob, nf, took)
    if k[4] == 2:
        return 'room' if k[5] else 'room, no way to own tail'
    lab = V[k[4]]
    if k[10] == 0:
        return lab + ': one-tile nook'
    if k[6] == 2:
        return lab + ': mate body (room if timed)'
    if k[6] > k[4]:
        return lab + ': mate body (tight if timed)'
    if k[8] > k[4]:
        return lab + ': short enemy body'
    if k[13]:
        return lab + ': own body at the exit'
    return lab + ': other'


def table(acc, bands, classify, title):
    lays = sorted({k[1] for k in acc})
    labs = sorted({lab for a in acc.values() for k in a if k[0] == 'A' and k[1] in bands for lab in [classify(k)] if lab})
    print(title)
    print('%-38s %6s %6s | %6s %6s %5s | %5s %5s | %5s %5s | %6s %6s | %6s %6s' % (
        'class', 'perkO', 'perkR', 'takeO', 'takeR', 'Rhi', 'dieO', 'dieR', 'splO', 'splR', 'netT_O', 'netT_R', 'netN_O', 'netN_R'))
    for lab in labs:
        perk, take, die, spl, nett, netn = [[], []], [[], []], [[], []], [[], []], [[], []], [[], []]
        hi = both = 0
        pool = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
        for lay in lays:
            row = []
            for wi, who in enumerate('OR'):
                a = acc[(who, lay)]
                T = sum(v[0] for k, v in a.items() if k[1] in bands)
                y = [v for k, v in a.items() if k[0] == 'A' and k[1] in bands and classify(k) == lab and k[-1] == 1]
                n_ = [v for k, v in a.items() if k[0] == 'A' and k[1] in bands and classify(k) == lab and k[-1] == 0]
                ny, nn = sum(v[0] for v in y), sum(v[0] for v in n_)
                row.append((ny, nn, T, sum(v[3] for v in y), sum(v[5] for v in y), sum(v[6] for v in y), sum(v[6] for v in n_)))
                perk[wi].append(1000 * (ny + nn) / T)
                for z, val in enumerate((ny, nn, row[-1][3], row[-1][4], row[-1][5], row[-1][6])):
                    pool[wi][z] += val
            if min(row[0][0] + row[0][1], row[1][0] + row[1][1]) >= MINN:
                both += 1
                for wi in (0, 1):
                    ny, nn, T, dy, sy, fy, fn = row[wi]
                    take[wi].append(100 * ny / (ny + nn))
                    if ny >= 10:
                        die[wi].append(100 * dy / ny)
                        spl[wi].append(100 * sy / ny)
                        nett[wi].append(fy / ny)
                    if nn >= 10:
                        netn[wi].append(fn / nn)
                hi += int(row[1][0] / (row[1][0] + row[1][1]) > row[0][0] / (row[0][0] + row[0][1]))
        m = lambda xs: sum(xs) / len(xs) if xs else float('nan')
        print('%-38s %6.2f %6.2f | %6.1f %6.1f %2d/%2d | %5.1f %5.1f | %5.1f %5.1f | %6.2f %6.2f | %6.2f %6.2f   pooled n %d %d' % (
            lab, m(perk[0]), m(perk[1]), m(take[0]), m(take[1]), hi, both, m(die[0]), m(die[1]), m(spl[0]), m(spl[1]),
            m(nett[0]), m(nett[1]), m(netn[0]), m(netn[1]), pool[0][0] + pool[0][1], pool[1][0] + pool[1][1]))
    print('perk = such turns per 1,000 turns of the bands; take = % that eat on the turn; die = % of takers dead within their')
    print('next 3 turns; spl = % of takers that split on their next turn; net = pearls eaten minus length lost in deaths on')
    print('this and the next 4 own turns, children split off in them included (T took, N did not)')


def main():
    acc, samples = load()
    what = sys.argv[1]
    bands = tuple(int(c) for c in (sys.argv[2] if len(sys.argv) > 2 and what != 'samples' else '01'))
    if what == 'verdict':
        table(acc, bands, lambda k: '%s tail%d' % (V[k[4]], k[5]) if k[11] == 0 else None, 'no flag set: the verdict now, own tail reached')
    elif what == 'why':
        table(acc, bands, lambda k: why(k) if k[11] == 0 else None, 'no flag set: verdict and what shuts the pearl tile')
    elif what == 'whylen':
        table(acc, bands, lambda k: 'L%d %s' % (k[2], why(k)) if k[11] == 0 and k[4] < 2 else None, 'no flag set, by length')
    elif what == 'kind':
        table(acc, bands, lambda k: '%s kind%d' % (why(k), k[12]) if k[11] == 0 and k[4] < 2 else None, 'no flag set, by pearl origin')
    elif what == 'flag':
        table(acc, bands, lambda k: ('zone' if k[11] % 2 else 'pocket/portal' if (k[11] // 2) % 2 else 'enemy head' if (k[11] // 4) % 2 else 'mate head' if k[11] >= 8 else 'none') + ' ' + V[k[4]], 'first flag x verdict')
    elif what == 'lay':
        lays = sorted({k[1] for k in acc})
        for lay in lays:
            out = []
            for who in 'OR':
                a = acc[(who, lay)]
                for grp in (0, 1):
                    sel = [(k, v) for k, v in a.items() if k[0] == 'A' and k[1] in bands and k[11] == 0 and k[4] == 0 and k[10] > 0 and (k[6] == 2) == (grp == 0)]
                    n = sum(v[0] for k, v in sel)
                    y = sum(v[0] for k, v in sel if k[-1] == 1)
                    out.append('%5d %4.0f%%' % (n, 100 * y / n if n else 0))
            print('%-22s O mate-shut %s other trapped %s | R mate-shut %s other trapped %s' % tuple([lay[:22]] + out))
    elif what == 'samples':
        who = sys.argv[2]
        for (w2, lay), rows in sorted(samples.items()):
            if w2 == who:
                for r in rows[:4]:
                    print(lay, r)


main()
