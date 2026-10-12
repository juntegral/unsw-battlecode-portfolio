"""Scratch (diag-longest): what the unspent far dragons are worth on the final board. python3 lg_rally.py
Joins lg_far-*.jsonl (positions at round 400) with lg_scan-*.jsonl (results). Estimate = RATE x length of our dragons
that may feed (twice their length at most the longest) and stand further than 15 tiles from it at round 400."""
import json
from pathlib import Path
from statistics import mean, median

WORK = Path('data/analysis/ladder/dossier/work')
ARMS = dict(MAIN=('m1', 'm2', 'm3'), B7=('b1', 'b2'), B7Q=('q1',), LADDER=('L0', 'L1', 'L'))
RATE = 0.2


def load(kind, tags):
    out = []
    for t in tags:
        p = WORK / ('lg_%s-%s.jsonl' % (kind, t))
        if p.exists():
            out += [json.loads(l) for l in p.read_text().splitlines() if l]
    return out


def in_race(g):
    return g['decided'] in ('longest', 'total') or (g['decided'] == 'elimination' and g['qdeath'][0] is not None and g['qdeath'][1] is not None)


def main():
    tot = [0, 0, 0, 0]
    for arm, tags in ARMS.items():
        S = dict((g['game'], g) for g in load('scan', tags))
        F = dict((g['game'], g) for g in load('far', tags))
        rows = []
        for gid, g in sorted(S.items()):
            f = F.get(gid)
            if f is None or g['last'] < 499 or not in_race(g) or g['decided'] == 'elimination':
                continue
            m = f['marks'].get('400')
            if not m or not m[0]:
                continue
            r = m[0]
            mid, far = r[12], r[16]
            near = r[4] + r[8]
            e1 = RATE * mid
            e2 = RATE * (mid + far)
            of, tf = g['final'][0], g['final'][1]
            rows.append((gid, g['map'], (g['opp'] or '')[:3], g['cells'], 'W' if g['win'] else 'L', of, tf, r[0], r[1], r[2], near, mid, far, e1, e2))
        lost = [x for x in rows if x[4] == 'L']
        won = [x for x in rows if x[4] == 'W']
        t1 = sum(1 for x in lost if x[5] + x[13] > x[6])
        t2 = sum(1 for x in lost if x[5] + x[14] > x[6])
        big = [x for x in lost if x[3] > 1200]
        print('== %s: full race games not ended by elimination %d (won %d, lost %d; lost above 1200 cells %d)' % (arm, len(rows), len(won), len(lost), len(big)))
        print('   lost games turned on the final board: with the 16-30 band only %d, with every dragon beyond 15 tiles %d' % (t1, t2))
        tot[0] += len(lost)
        tot[1] += t1
        tot[2] += t2
        tot[3] += len(won)
        for name, V in (('lost', lost), ('won', won)):
            if V:
                print('   %s n%d: at r400 longest %.1f alive %.1f total %.1f; may-feed length within 15: %.1f, 16-30: %.1f, 31+: %.1f; end ours %.1f theirs %.1f' % (
                    name, len(V), mean(x[7] for x in V), mean(x[8] for x in V), mean(x[9] for x in V), mean(x[10] for x in V), mean(x[11] for x in V),
                    mean(x[12] for x in V), mean(x[5] for x in V), mean(x[6] for x in V)))
        for x in (lost if arm != 'LADDER' else []):
            print('     %d %s %s %d: end %d/%d (gap %d); r400 longest %d alive %d total %d; may-feed near %d, 16-30 %d, 31+ %d; estimate +%.0f / +%.0f %s' % (
                x[0], x[1], x[2] or '', x[3], x[5], x[6], x[6] - x[5], x[7], x[8], x[9], x[10], x[11], x[12], x[13], x[14],
                'TURNS' if x[5] + x[13] > x[6] else 'turns with all' if x[5] + x[14] > x[6] else ''))
    print('all arms: lost %d, turned %d (16-30 only) or %d (all beyond 15); won %d' % (tot[0], tot[1], tot[2], tot[3]))


main()
