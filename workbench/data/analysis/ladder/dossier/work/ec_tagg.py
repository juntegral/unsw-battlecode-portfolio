# Scratch (diag-economy): tables from ec_tight-*.jsonl (the second pass). Layout means, equal weight; a layout
# counts for a rate when both teams have at least MINN turns of the class there.
# Usage: python3 data/analysis/ladder/dossier/work/ec_tagg.py <table> [bands, default 01]
#   cause  : adjacent-pearl turns by why the pearl's tile is cramped (no other flag set)
#   flags  : the same turns by flag (zone, pocket or portal, enemy head, mate head)
#   head   : the same by the room at the dragon's own head (walls only x all bodies)
#   lay    : per layout, the body-cramped classes
#   samples <O|R> <cause prefix> : sample turns for replay reading
import sys, json
from collections import defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
FILES = ('ec_tight-O0.jsonl', 'ec_tight-O1.jsonl', 'ec_tight-O2.jsonl', 'ec_tight-R0.jsonl', 'ec_tight-R1.jsonl', 'ec_tight-R2.jsonl')
MINN = 30


def load():
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0, 0, 0]))
    samples = defaultdict(list)
    for f in FILES:
        for line in open(W + f):
            r = json.loads(line)
            a = acc[(r['who'], r['layout'])]
            for row in r['acc']:
                v = a[tuple(row[:-6])]
                for z in range(6):
                    v[z] += row[-6 + z]
            samples[(r['who'], r['layout'])].extend(r['samples'])
    return acc, samples


def table(acc, bands, classify, title):
    lays = sorted({k[1] for k in acc})
    labs = sorted({lab for a in acc.values() for k in a if k[0] == 'A' and k[1] in bands for lab in [classify(k)] if lab})
    print(title)
    print('%-26s %6s %6s | %6s %6s %5s | %6s %6s | %6s %6s | %6s %6s | %6s %6s' % (
        'class', 'shO', 'shR', 'takeO', 'takeR', 'Rhi', 'dieO', 'dieR', 'netT_O', 'netT_R', 'netN_O', 'netN_R', 'perkO', 'perkR'))
    for lab in labs:
        sh = [[], []]
        take = [[], []]
        die = [[], []]
        nett = [[], []]
        netn = [[], []]
        perk = [[], []]
        hi = both = 0
        for lay in lays:
            row = []
            for wi, who in enumerate('OR'):
                a = acc[(who, lay)]
                T = sum(v[0] for k, v in a.items())
                tot = sum(v[0] for k, v in a.items() if k[0] == 'A' and k[1] in bands)
                y = [v for k, v in a.items() if k[0] == 'A' and k[1] in bands and classify(k) == lab and k[-1] == 1]
                n_ = [v for k, v in a.items() if k[0] == 'A' and k[1] in bands and classify(k) == lab and k[-1] == 0]
                ny, nn = sum(v[0] for v in y), sum(v[0] for v in n_)
                row.append((ny, nn, tot, sum(v[3] for v in y), sum(v[2] - v[4] for v in y), sum(v[2] - v[4] for v in n_), T))
            for wi in (0, 1):
                ny, nn, tot, dy, nty, ntn, T = row[wi]
                sh[wi].append(100 * (ny + nn) / tot if tot else 0)
                perk[wi].append(1000 * (ny + nn) / T)
            if min(row[0][0] + row[0][1], row[1][0] + row[1][1]) >= MINN:
                both += 1
                for wi in (0, 1):
                    ny, nn, tot, dy, nty, ntn, T = row[wi]
                    take[wi].append(100 * ny / (ny + nn))
                    if ny:
                        die[wi].append(100 * dy / ny)
                        nett[wi].append(nty / ny)
                    if nn:
                        netn[wi].append(ntn / nn)
                hi += int(row[1][0] / (row[1][0] + row[1][1]) > row[0][0] / (row[0][0] + row[0][1]))
        m = lambda xs: sum(xs) / len(xs) if xs else float('nan')
        print('%-26s %6.2f %6.2f | %6.1f %6.1f %2d/%2d | %6.1f %6.1f | %6.2f %6.2f | %6.2f %6.2f | %6.2f %6.2f' % (
            lab, m(sh[0]), m(sh[1]), m(take[0]), m(take[1]), hi, both, m(die[0]), m(die[1]), m(nett[0]), m(nett[1]),
            m(netn[0]), m(netn[1]), m(perk[0]), m(perk[1])))
    print('sh = % of adjacent-pearl turns; take = % that eat on the turn; die = % of takers dead within 3 turns; net = pearls')
    print('eaten on this and the next 4 turns minus own length lost by a death in them (T took, N did not); perk = per 1,000 of all turns')


def main():
    acc, samples = load()
    what = sys.argv[1]
    bands = tuple(int(c) for c in (sys.argv[2] if len(sys.argv) > 2 and what != 'samples' else '01'))
    # key: ('A', band, L, lead, cause, hs, box, fl, kind, origin, took)
    if what == 'cause':
        table(acc, bands, lambda k: k[4] if k[7] == 0 else None, 'no flag set, by cause')
        table(acc, bands, lambda k: (k[4][0] + k[4][-1]) + ' L%d' % k[2] if k[7] == 0 else None, 'no flag set, by cause group and length')
        table(acc, bands, lambda k: (k[4][0] + k[4][-1]) + ' kind%d' % k[8] if k[7] == 0 else None, 'no flag set, by cause group and pearl kind')
    elif what == 'flags':
        table(acc, bands, lambda k: 'flag %2d' % k[7], 'all adjacent-pearl turns by flag')
        table(acc, bands, lambda k: ('zone' if k[7] % 2 else 'pocket/portal' if (k[7] // 2) % 2 else 'enemy head' if (k[7] // 4) % 2 else 'mate head' if k[7] >= 8 else 'none') + ' ' + (k[4][0] + k[4][-1] if k[4] != 'F' else 'F'), 'first flag x cause group')
    elif what == 'head':
        table(acc, bands, lambda k: 'hs%d box%d %s' % (k[5], k[6], k[4][0] + k[4][-1] if k[4] != 'F' else 'F') if k[7] == 0 else None, 'no flag set: head room by walls, by all bodies, cause group')
    elif what == 'lay':
        lays = sorted({k[1] for k in acc})
        for lay in lays:
            out = []
            for who in 'OR':
                a = acc[(who, lay)]
                for grp in ('B1', 'B2', 'S1', 'S2'):
                    y = sum(v[0] for k, v in a.items() if k[0] == 'A' and k[1] in bands and k[7] == 0 and k[4][0] + k[4][-1] == grp and k[-1] == 1)
                    n_ = sum(v[0] for k, v in a.items() if k[0] == 'A' and k[1] in bands and k[7] == 0 and k[4][0] + k[4][-1] == grp and k[-1] == 0)
                    out.append('%5d %4.0f%%' % (y + n_, 100 * y / (y + n_) if y + n_ else 0))
            print('%-22s O B1 %s B2 %s S1 %s S2 %s | R B1 %s B2 %s S1 %s S2 %s' % tuple([lay[:22]] + out))
    elif what == 'samples':
        who, pre = sys.argv[2], sys.argv[3]
        for (w2, lay), rows in sorted(samples.items()):
            if w2 == who:
                for r in [r for r in rows if r[8].startswith(pre)][:4]:
                    print(lay, r)


main()
