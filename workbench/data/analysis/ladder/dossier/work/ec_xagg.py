# Scratch (diag-economy): table from ec_x-*.jsonl (fifth pass, every 2nd game): the survey's verdict on the pearl
# step against a plain flood of the same tile (own body free), where another free step has room. Layout means.
# Usage: python3 data/analysis/ladder/dossier/work/ec_xagg.py
import sys, json
from collections import defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
FILES = ('ec_x-O0.jsonl', 'ec_x-O1.jsonl', 'ec_x-R0.jsonl', 'ec_x-R1.jsonl')
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
    # key: ('A', band, L, vnow, vmt, nook, alt, fl, kind, ob, took)
    if k[3] == 2:
        return 'room'
    if k[5]:
        return 'nook'
    if k[4] == 2:
        return V[k[3]] + ', mate-shut'
    if k[9] and k[3] == 0:
        return 'trapped, own tail'
    return V[k[3]] + ', other'


ALT = {-1: 'no other step', 0: 'others trapped', 1: 'other tight', 2: 'other has room'}


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
    F = ('flood trapped', 'flood tight', 'flood room')
    # key: ('A', band, L, vnow, vmt, nook, alt, fl, kind, fc, took)
    table(acc, (0, 1), lambda k: 'survey %s | %s' % (V[k[3]], F[k[9]]) if k[7] == 0 and k[6] == 2 and not k[5] else None,
          'no flag, no nook, another step has room: survey verdict | plain flood of the same pearl tile')
    table(acc, (0, 1), lambda k: 'survey %s%s | %s' % (V[k[3]], ', mate-shut' if k[4] == 2 else '', F[k[9]]) if k[7] == 0 and k[6] == 2 and not k[5] and k[3] < 2 else None,
          'the same, mate-shut apart')


main()
