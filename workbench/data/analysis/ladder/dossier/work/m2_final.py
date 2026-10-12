"""Scratch (diag-med20): the report tables in one pass, from m2_scan-T3.jsonl, m2_scan-O.jsonl, m2_scan-T1-*.jsonl.
Usage: python3 data/analysis/ladder/dossier/work/m2_final.py"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict, Counter
from itertools import permutations

WORK = Path('data/analysis/ladder/dossier/work')
FILES = ('m2_scan-T3.jsonl', 'm2_scan-O.jsonl', 'm2_scan-T1-0.jsonl', 'm2_scan-T1-1.jsonl')
TOP = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 91: 'SSS', 264: 'ftm', 842: 'horse'}
LAYS = ('Queen Of Spades', 'Maze', 'Default', 'Trauma')
FRESH = ('aAah', 'larp', 'Cutlery', 'chad')
ROWS = ('aAah', 'larp', 'Cutlery', 'chad', 'top opp', 'Cutlery old', 'SSS old', 'ftm old', 'ours all', 'live all', 'B7', 'MAIN', 'ladder opp')
OURS = ('B7Q direct', 'B7Q', 'B7', 'MAIN')


def group(g, side):
    if g['src'] == 'T3':
        return TOP.get(g['team'], '?') if side == 0 else 'top opp'
    if g['src'] == 'T1':
        return (TOP.get(g['team'], '?') + ' old') if side == 0 else 'old opp'
    if g['label'].startswith('top-l'):
        return 'B7Q direct' if side == 0 else 'direct ' + TOP.get(g['oppid'], str(g['oppid']))
    return g['arm'] if side == 0 else 'ladder opp'


def names(g, s):
    grp = group(g, s)
    out = [grp]
    if grp in OURS:
        out.append('ours all')
    if grp in ('B7Q', 'B7Q direct'):
        out.append('live all')
    return out


def mean(v):
    return sum(v) / len(v) if v else float('nan')


def shapley(u, t):
    n = len(u)
    out = [0.0] * n
    perms = list(permutations(range(n)))
    for order in perms:
        cur = list(u)
        base = 1.0
        for x in cur:
            base *= x
        for k in order:
            cur[k] = t[k]
            v = 1.0
            for x in cur:
                v *= x
            out[k] += v - base
            base = v
    return [x / len(perms) for x in out]


def main():
    games, turns, prl = {}, defaultdict(list), defaultdict(list)
    for f in FILES:
        p = WORK / f
        if not p.exists():
            continue
        cur = None
        for line in p.read_text().splitlines():
            if not line:
                continue
            r = json.loads(line)
            if r['k'] == 'g':
                cur = (f, r['g'])
                games[cur] = r
            elif r['k'] == 't':
                turns[cur].append(r)
            else:
                prl[cur].append(r)
    A = defaultdict(lambda: defaultdict(list))     # (layout, group) -> measure -> per game values
    C = defaultdict(Counter)                       # pearl account
    W = defaultdict(Counter)                       # walk
    NG = Counter()
    r0 = Counter()
    for key, g in games.items():
        for s in (0, 1):
            m = g['marks']
            if '20' not in m:
                continue
            a20 = m['20'][s]
            a40 = m.get('40', m['20'])[s]
            qroot = [int(i) for i, v in g['starters'].items() if v[0] == 'q' and v[1] == s]
            row = Counter()
            for p in prl.get(key, ()):
                if p['s'] != s:
                    continue
                for R in (20, 40):
                    if p['r'] <= R:
                        row[('portal' if p['pc'] > 0 else 'plain', R)] += 1
                        row[('q' if p['root'] in qroot else 'o', R)] += 1
            long = g['rounds'] >= 200
            near20 = sum(1 for r in turns.get(key, ()) if r['s'] == s and r['r'] == 20 and 0 <= r['dsn'] <= 3)
            for nm in names(g, s):
                NG[(g['map'], nm)] += 1
                NG[('all', nm)] += 1
                a = A[(g['map'], nm)]
                a['E'].append(a20[2])
                a['E40'].append(a40[2])
                a['E2'].append(a20[11])
                a['D'].append(a20[8])
                a['S'].append(a20[6])
                a['P'].append(a20[7])
                a['al'].append(a20[0])
                a['r0s'].append(sum(1 for sp in g['splits'] if sp[0] == 0 and sp[1] == s))
                for k in (('portal', 20), ('portal', 40), ('plain', 20), ('plain', 40), ('q', 20), ('o', 20)):
                    a[k].append(row[k])
                if long:
                    a['near20'].append(near20)
                c = C[(g['map'], nm)]
                for p in prl.get(key, ()):
                    if p['s'] != s or p['r'] > 20:
                        continue
                    c['all'] += 1
                    c['eater ' + p['ro']] += 1
                    c['v0'] += p['v0']
                    c['born ' + ('r0' if p['born'] == 0 else 'r1-10' if p['born'] <= 10 else 'r11-20')] += 1
                    d = p['down']
                    c['dist ' + ('0-5' if d <= 5 else '6-10' if d <= 10 else '11-15' if d <= 15 else '16+')] += 1
                    c['portal'] += 1 if p['pc'] > 0 else 0
                    c['centre'] += 1 if p['cdt'] < p['cds'] else 0
                    c['enemy'] += 1 if p['den'] < p['down'] else 0
                    c['wall'] += 1 if p['wall'] > 0 else 0
                    c['step2'] += 1 if p['step'] >= 2 else 0
                    c['field'] += 1 if p['cl'] >= 5 else 0
                    c['lag'] += p['r'] - p['fss']
                    c['wait'] += p['r'] - p['born']
                for r in turns.get(key, ()):
                    if r['s'] != s:
                        continue
                    if g['map'] == 'Queen Of Spades' and r['r'] == 0 and r['ro'] == 'o' and r['act'] == 'm':
                        r0[(nm, 'straight' if r['dir'] == r['fc'] else 'turn')] += 1
                    if r['act'] != 'm' or r['dir'] < 0 or r['fc'] < 0 or r['L'] > 4:
                        continue
                    late = r['r'] > 20
                    if late and g['src'] == 'T1':
                        continue
                    w = W[nm]
                    q = r['ro'] == 'q'
                    if late:
                        if not q and r['ps'] > 0:
                            w['late through'] += 1
                        continue
                    blind = r['np'] == 0 and r['nso'] == 0
                    if not q and r['ps'] > 0:
                        w['through'] += 1
                    if not blind:
                        continue
                    if q:
                        w['q blind'] += 1
                        w['q straight'] += int(r['dir'] == r['fc'])
                        continue
                    w['blind'] += 1
                    w['straight'] += int(r['dir'] == r['fc'])
                    w['unseen'] += int(r['du2'] >= 0 and r['du2'] < r['du'])
                    w['fresh'] += r['fresh']
                    w['tnew'] += r['tnew']
                    if r['nmo'] > 0 and 0 <= r['dmo'] <= 6:
                        w['m6'] += 1
                        w['m6 nearer'] += int(r['dma2'] >= 0 and r['dma2'] < r['dma'])
                        if r['dmo'] == 0:
                            w['on'] += 1
                            w['on through'] += int(r['ps'] > 0)
                if g['src'] != 'T1':
                    W[nm]['late games'] += 1

    def lm(grp, k):
        return mean([mean(A[(lay, grp)][k]) for lay in LAYS])

    print('## Table A. Pearls eaten by round 20 (mean of games inside a layout; mean = the four layouts with equal weight)')
    print('| Side (games 25x35 / 48x24 field / 32x32 / 48x24 closed) | 25x35 | 48x24 field | 32x32 | 48x24 closed | mean | times ours | behind a portal r20; r40 | not behind a portal r20; r40 | queen line; other lines r20 | dragon-turns; tiles seen; pearls seen by r20 | all pearls r40 |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|')
    base = lm('ours all', 'E')
    for grp in ROWS:
        if not all(A.get((lay, grp)) for lay in LAYS):
            continue
        print('| %s (%s) | %s | %.2f | %.2f | %.2f; %.2f | %.2f; %.2f | %.2f; %.2f | %.1f; %.0f; %.1f | %.1f |' % (
            grp, ' / '.join(str(NG[(lay, grp)]) for lay in LAYS), ' | '.join('%.2f' % mean(A[(lay, grp)]['E']) for lay in LAYS), lm(grp, 'E'), lm(grp, 'E') / base,
            lm(grp, ('portal', 20)), lm(grp, ('portal', 40)), lm(grp, ('plain', 20)), lm(grp, ('plain', 40)), lm(grp, ('q', 20)), lm(grp, ('o', 20)),
            lm(grp, 'D'), lm(grp, 'S'), lm(grp, 'P'), lm(grp, 'E40')))
    print()
    print('r40 by layout (all pearls; behind a portal):')
    for grp in FRESH + ('ours all', 'live all'):
        print('  %-9s ' % grp + ' | '.join('%s %.1f; %.1f' % (lay[:7], mean(A[(lay, grp)]['E40']), mean(A[(lay, grp)][('portal', 40)])) for lay in LAYS))
    print()
    print('## Table B. The gap at round 20 = theirs - ours, in five parts (Shapley over first-step pearls = turns x tiles/turn x pearls/tile x eaten/seen, inside each layout, then the mean)')
    print('| Their side | against | gap | dragon-turns | tiles seen per dragon-turn | pearls seen per tile seen | eaten per pearl seen | second-step pearls | gap by layout 25x35, 48x24 field, 32x32, 48x24 closed | round-0 splits a game (theirs; ours 0) |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for ours in ('ours all', 'live all'):
        for theirs in FRESH + ('top opp', 'Cutlery old', 'SSS old', 'ftm old'):
            if ours == 'live all' and theirs not in FRESH:
                continue
            tot = [0.0] * 6
            gaps = []
            parts = defaultdict(list)
            for lay in LAYS:
                vu, vt = A[(lay, ours)], A[(lay, theirs)]
                mu = lambda k: mean(vu[k])
                mt = lambda k: mean(vt[k])
                fu = (mu('D'), mu('S') / mu('D'), mu('P') / mu('S'), (mu('E') - mu('E2')) / mu('P') if mu('P') else 0.0)
                ft = (mt('D'), mt('S') / mt('D'), mt('P') / mt('S'), (mt('E') - mt('E2')) / mt('P') if mt('P') else 0.0)
                sh = shapley(fu, ft)
                vals = [mt('E') - mu('E')] + sh + [mt('E2') - mu('E2')]
                assert abs(vals[0] - sum(vals[1:])) < 1e-6
                for k in range(6):
                    tot[k] += vals[k] / 4
                gaps.append('%+.2f' % vals[0])
                parts[lay] = vals
            print('| %s | %s | %+.2f | %+.2f | %+.2f | %+.2f | %+.2f | %+.2f | %s | %.1f |' % ((theirs, ours) + tuple(tot) + (', '.join(gaps), lm(theirs, 'r0s'))))
            if theirs in FRESH and ours == 'ours all':
                print('    by layout (turns, tiles/turn, pearls/tile, eaten/seen, step 2): ' + ' ; '.join('%s %s' % (lay[:7], ' '.join('%+.2f' % x for x in parts[lay][1:])) for lay in LAYS))
    print()
    print('## Table C. Every pearl eaten by round 20, a game: the four fresh top teams (lowest to highest team mean) | ours, all sets')
    cats = (('all', 'all'), ('eater q', 'eaten by the queen'), ('eater o', 'by another starter'), ('eater c', 'by a child'), ('v0', 'in view from a start tile in round 0'),
            ('born r0', 'born in round 0'), ('born r1-10', 'born r1-10'), ('born r11-20', 'born r11-20'), ('dist 0-5', 'path steps from the nearest own start 0-5'), ('dist 6-10', '6-10'),
            ('dist 11-15', '11-15'), ('dist 16+', '16 or more'), ('portal', 'eater or its line had stepped through a portal'), ('centre', 'nearer the centre than its start'),
            ('enemy', 'nearer the enemy starts than its own'), ('wall', 'beside a kelp edge'), ('field', '5 or more spawn tiles in its 5 by 5'), ('step2', 'on a second step'))
    print('| Pearls a game | ' + ' | '.join(LAYS) + ' |')
    print('|---|---|---|---|---|')
    for key, label in cats:
        cells = []
        for lay in LAYS:
            v = [C[(lay, t)][key] / NG[(lay, t)] for t in FRESH]
            cells.append('%.1f-%.1f : %.2f' % (min(v), max(v), C[(lay, 'ours all')][key] / NG[(lay, 'ours all')]))
        print('| %s | %s |' % (label, ' | '.join(cells)))
    for key, label in (('lag', 'rounds from first in view of the side to eaten'), ('wait', 'rounds from born to eaten')):
        cells = []
        for lay in LAYS:
            v = [C[(lay, t)][key] / max(1, C[(lay, t)]['all']) for t in FRESH]
            cells.append('%.1f-%.1f : %.1f' % (min(v), max(v), C[(lay, 'ours all')][key] / max(1, C[(lay, 'ours all')]['all'])))
        print('| %s | %s |' % (label, ' | '.join(cells)))
    cells = []
    for lay in LAYS:
        v = [mean(A[(lay, t)]['near20']) for t in FRESH]
        cells.append('%.1f-%.1f : %.1f' % (min(v), max(v), mean(A[(lay, 'ours all')]['near20'])))
    print('| heads at r20 within 3 steps of a tile that spawns in the next 10 rounds (games of 200+ rounds) | %s |' % ' | '.join(cells))
    print()
    print('## Table D. The walk, rounds 0-20, dragons of length 4 or less')
    print('| Side | blind turns a game (not the queen) | straight ahead % | queen: straight ahead % | ends nearer a tile it has not seen % | new tiles a blind turn: own; team | blind turns with a portal mouth in view within 6 steps, a game; ends nearer % | blind turns on a mouth tile, a game; steps through % | portal steps a game r0-20; r21-40 |')
    print('|---|---|---|---|---|---|---|---|---|')
    for grp in ROWS:
        w = W.get(grp)
        if not w or not w['blind']:
            continue
        n = NG[('all', grp)]
        b = w['blind']
        late = ('%.2f' % (w['late through'] / w['late games'])) if w['late games'] else 'not scanned'
        print('| %s (%d) | %.1f | %.0f | %.0f | %.0f | %.1f; %.1f | %.1f; %.0f | %.2f; %.0f | %.2f; %s |' % (
            grp, n, b / n, 100 * w['straight'] / b, 100 * w['q straight'] / max(1, w['q blind']), 100 * w['unseen'] / b, w['fresh'] / b, w['tnew'] / b,
            w['m6'] / n, 100 * w['m6 nearer'] / max(1, w['m6']), w['on'] / n, 100 * w['on through'] / max(1, w['on']), w['through'] / n, late))
    print()
    print('Round 0 on the 25x35 start, the second starter (straight ahead / other step):', {k: v for k, v in sorted(r0.items()) if k[0] in ROWS})


main()
