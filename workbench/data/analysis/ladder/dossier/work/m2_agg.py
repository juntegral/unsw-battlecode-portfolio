"""Scratch (diag-med20): tables from m2_scan-*.jsonl.
Usage: python3 data/analysis/ladder/dossier/work/m2_agg.py <tab|dec|pearls|walk|first> [round]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict, Counter
from itertools import permutations
from statistics import median

WORK = Path('data/analysis/ladder/dossier/work')
FILES = ('m2_scan-T3.jsonl', 'm2_scan-O.jsonl', 'm2_scan-T1-0.jsonl', 'm2_scan-T1-1.jsonl')
TOP = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 91: 'SSS', 264: 'ftm', 842: 'horse'}
LAYS = ('Queen Of Spades', 'Maze', 'Default', 'Trauma')
SHORT = {'Queen Of Spades': 'QoS 25x35', 'Maze': 'Maze 48x24', 'Default': 'Default 32x32', 'Trauma': 'Trauma 48x24'}
ORDER = ('aAah', 'larp', 'Cutlery', 'chad', 'top opp', 'direct larp', 'direct Cutlery', 'B7Q direct', 'B7Q', 'B7', 'MAIN', 'ours all', 'live all', 'ladder opp',
         'Cutlery old', 'SSS old', 'ftm old', 'old opp')
OURS = ('B7Q direct', 'B7Q', 'B7', 'MAIN')
THEIRS = ('aAah', 'larp', 'Cutlery', 'chad')


def group(g, side):
    if g['src'] == 'T3':
        return TOP.get(g['team'], '?') if side == 0 else 'top opp'
    if g['src'] == 'T1':
        return (TOP.get(g['team'], '?') + ' old') if side == 0 else 'old opp'
    if g['label'].startswith('top-l'):
        return 'B7Q direct' if side == 0 else 'direct ' + TOP.get(g['oppid'], str(g['oppid']))
    return g['arm'] if side == 0 else 'ladder opp'


def load():
    games, turns, pearls = {}, defaultdict(list), defaultdict(list)
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
                pearls[cur].append(r)
    # rows of a game are written after its g row? no: g row first, then rows
    return games, turns, pearls


def mean(v):
    return sum(v) / len(v) if v else float('nan')


def sides(games):
    """yield (key, game, side, group names) ; 'ours all' pools our four sets."""
    for key, g in games.items():
        for s in (0, 1):
            grp = group(g, s)
            yield key, g, s, grp
            if grp in OURS:
                yield key, g, s, 'ours all'
            if grp in ('B7Q', 'B7Q direct'):
                yield key, g, s, 'live all'


def shapley(u, t):
    """u, t: tuples of 4 factors; returns the 4 contributions to prod(t) - prod(u)."""
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


def table(games, R):
    acc = defaultdict(list)
    for key, g, s, grp in sides(games):
        m = g['marks']
        if str(R) not in m or '0' not in m:
            continue
        a = m[str(R)][s]
        a10 = m['10'][s] if '10' in m else a
        a0 = m['0'][s]
        r0s = sum(1 for sp in g['splits'] if sp[0] == 0 and sp[1] == s)
        acc[(g['map'], grp)].append(dict(E=a[2], E10=a10[2], E2=a[11], D=a[8], S=a[6], P=a[7], al0=a0[0], al10=a10[0], al=a[0], ps=a[9], sp=a[4],
                                         de=a[5], ql=a[13], r0s=r0s, tot=a[1], nat=a[3], two=a[10], paid=a[12], won=1 if (g['won'] if s == 0 else (None if g['won'] is None else not g['won'])) else 0))
    return acc


def tab(games, R):
    acc = table(games, R)
    print('Round %d. E pearls eaten, E2 of them on a second step, D dragon-turns, S tiles seen, P pearls seen (distinct), a=S/D, b=P per 100 S, c=E1/P' % R)
    for lay in LAYS:
        print('==', SHORT[lay])
        for grp in ORDER:
            v = acc.get((lay, grp))
            if not v:
                continue
            m = lambda k: mean([x[k] for x in v])
            E1 = m('E') - m('E2')
            print('%-15s n=%3d E10 %5.2f E %5.2f E2 %4.2f | D %6.1f S %6.1f P %5.2f | a %5.2f b %5.2f c %4.2f | alive r0 %4.2f r10 %4.2f r%d %4.2f len %5.1f | r0 splits %4.2f splits %4.2f deaths %4.2f portal steps %4.2f two-step %4.2f paid %4.2f q len %4.2f won %2d'
                  % (grp, len(v), m('E10'), m('E'), m('E2'), m('D'), m('S'), m('P'), m('S') / m('D'), 100 * m('P') / m('S'), E1 / m('P') if m('P') else 0,
                     m('al0'), m('al10'), R, m('al'), m('tot'), m('r0s'), m('sp'), m('de'), m('ps'), m('two'), m('paid'), m('ql'), sum(x['won'] for x in v)))
    print('== mean of the four layouts')
    for grp in ORDER:
        vs = [acc.get((lay, grp)) for lay in LAYS]
        if not all(vs):
            continue
        m = lambda k: mean([mean([x[k] for x in v]) for v in vs])
        print('%-15s n=%3d E10 %5.2f E %5.2f E2 %4.2f | D %6.1f S %6.1f P %5.2f | alive r0 %4.2f r10 %4.2f r%d %4.2f len %5.1f | portal steps %4.2f'
              % (grp, sum(len(v) for v in vs), m('E10'), m('E'), m('E2'), m('D'), m('S'), m('P'), m('al0'), m('al10'), R, m('al'), m('tot'), m('ps')))


def dec(games, R):
    acc = table(games, R)
    print('Round %d. Gap in pearls = theirs - ours, split by Shapley over E1 = D x (S/D) x (P/S) x (E1/P), plus second-step pearls.' % R)
    print('columns: gap | dragon-turns | tiles seen per dragon-turn | pearls seen per tile seen | eaten per pearl seen | second-step pearls ; (r0 = share of the dragon-turn part that is the round-0 split, 1 turn per split)')
    for ours in ('ours all', 'live all'):
        print('--- against', ours)
        for theirs in THEIRS + ('top opp', 'Cutlery old', 'SSS old', 'ftm old', 'ladder opp'):
            tot = [0.0] * 6
            line = []
            ok = 0
            for lay in LAYS:
                vu, vt = acc.get((lay, ours)), acc.get((lay, theirs))
                if not vu or not vt:
                    line.append('%s: NA' % SHORT[lay].split()[0])
                    continue
                ok += 1
                mu = lambda k: mean([x[k] for x in vu])
                mt = lambda k: mean([x[k] for x in vt])
                fu = (mu('D'), mu('S') / mu('D'), mu('P') / mu('S'), (mu('E') - mu('E2')) / mu('P') if mu('P') else 0.0)
                ft = (mt('D'), mt('S') / mt('D'), mt('P') / mt('S'), (mt('E') - mt('E2')) / mt('P') if mt('P') else 0.0)
                sh = shapley(fu, ft)
                e2 = mt('E2') - mu('E2')
                gap = mt('E') - mu('E')
                r0 = (mt('r0s') - mu('r0s'))
                dD = mt('D') - mu('D')
                vals = [gap] + sh + [e2]
                for k in range(6):
                    tot[k] += vals[k]
                line.append('%s: %+5.2f = %+5.2f %+5.2f %+5.2f %+5.2f %+5.2f (r0 %+.2f of dD %+.1f)' % ((SHORT[lay].split()[0],) + tuple(vals) + (r0, dD)))
            if ok == 4:
                print('%-14s MEAN %+5.2f = %+5.2f %+5.2f %+5.2f %+5.2f %+5.2f || ' % ((theirs,) + tuple(x / 4 for x in tot)) + ' | '.join(line))
            else:
                print('%-14s ' % theirs + ' | '.join(line))


def pearls(games, prl, R):
    cnt = defaultdict(Counter)
    ng = Counter()
    lag = defaultdict(list)
    for key, g, s, grp in sides(games):
        ng[(g['map'], grp)] += 1
        c = cnt[(g['map'], grp)]
        for p in prl.get(key, ()):
            if p['s'] != s or p['r'] > R:
                continue
            c['all'] += 1
            c['nat'] += p['nat']
            c['role ' + p['ro']] += 1
            c['gen %d' % min(p['gen'], 2)] += 1
            c['v0'] += p['v0']
            c['born ' + ('r0' if p['born'] == 0 else 'r1-10' if p['born'] <= 10 else 'r11+')] += 1
            d = p['down']
            c['dist ' + ('0-5' if d <= 5 else '6-10' if d <= 10 else '11-15' if d <= 15 else '16+')] += 1
            c['portal'] += 1 if p['pc'] > 0 else 0
            c['centre'] += 1 if p['cdt'] < p['cds'] else 0
            c['enemy side'] += 1 if p['den'] < p['down'] else 0
            c['wall'] += 1 if p['wall'] > 0 else 0
            c['step2'] += 1 if p['step'] >= 2 else 0
            c['cluster 5+'] += 1 if p['cl'] >= 5 else 0
            c['seen before born'] += 0
            lag[(g['map'], grp, 'see')].append(p['r'] - p['fss'])
            lag[(g['map'], grp, 'seed')].append(p['r'] - p['fsd'])
            lag[(g['map'], grp, 'wait')].append(p['r'] - p['born'])
            lag[(g['map'], grp, 'round')].append(p['r'])
    keys = ('all', 'nat', 'role q', 'role o', 'role c', 'gen 2', 'v0', 'born r0', 'born r1-10', 'born r11+', 'dist 0-5', 'dist 6-10', 'dist 11-15', 'dist 16+',
            'portal', 'centre', 'enemy side', 'wall', 'step2', 'cluster 5+')
    print('Pearls eaten by round %d, a game. role: q queen starter, o other starter, c child (gen 2 = grandchild or later); v0 in view from a start tile at round 0;' % R)
    print('dist = path steps from the nearest own start head; portal = eater or its line had stepped through a portal; centre = nearer the centre than its start; cluster 5+ = 5 or more spawn tiles in the 5 by 5')
    for lay in LAYS:
        print('==', SHORT[lay])
        print('%-15s %4s ' % ('', 'n') + ' '.join('%6s' % k[-6:] for k in keys) + '  see>eat med/mean  own see>eat  born>eat  round med')
        for grp in ORDER:
            n = ng.get((lay, grp))
            if not n:
                continue
            c = cnt[(lay, grp)]
            lg = lag.get((lay, grp, 'see'), [])
            extra = ''
            if lg:
                extra = '  %4.1f / %4.1f   %4.1f   %4.1f   %4.1f' % (median(lg), mean(lg), mean(lag[(lay, grp, 'seed')]), mean(lag[(lay, grp, 'wait')]), median(lag[(lay, grp, 'round')]))
            print('%-15s %4d ' % (grp, n) + ' '.join('%6.2f' % (c[k] / n) for k in keys) + extra)


def avail(games, R):
    """natural pearls born by round R within d path steps of the side's nearest start, and the share the side has eaten by R."""
    print('Natural pearls born in rounds 0-%d by path steps from the nearest own start head (a game), from the births list' % R)
    acc = defaultdict(list)
    for key, g, s, grp in sides(games):
        b = [x for x in g['births'] if x[0] <= R]
        acc[(g['map'], grp)].append([sum(1 for x in b if x[2 + s] <= 5), sum(1 for x in b if 5 < x[2 + s] <= 10), sum(1 for x in b if 10 < x[2 + s] <= 15),
                                     sum(1 for x in b if 15 < x[2 + s] <= 20), sum(1 for x in b if x[2 + s] > 20), sum(1 for x in b if x[0] == 0 and x[2 + s] <= 15)])
    for lay in LAYS:
        print('==', SHORT[lay])
        for grp in ORDER:
            v = acc.get((lay, grp))
            if v:
                print('%-15s n=%3d  0-5: %5.2f  6-10: %5.2f  11-15: %5.2f  16-20: %5.2f  21+: %5.2f | at r0 within 15: %5.2f' % ((grp, len(v)) + tuple(mean([x[k] for x in v]) for k in range(6))))


def main():
    mode = sys.argv[1]
    R = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    games, turns, prl = load()
    if mode == 'tab':
        tab(games, R)
    elif mode == 'dec':
        dec(games, R)
    elif mode == 'pearls':
        pearls(games, prl, R)
    elif mode == 'avail':
        avail(games, R)


main()
