"""Scratch (diag-australia): aggregate au_ev-*.jsonl. Usage: python3 .../au_agg.py [layout key] [section]"""
import sys, json
from collections import defaultdict, Counter
from pathlib import Path

D = Path('data/analysis/ladder/dossier/work')
games = []
for n in range(4):
    p = D / ('au_ev-%d.jsonl' % n)
    if p.exists():
        with open(p) as f:
            for line in f:
                games.append(json.loads(line))
LAY = sys.argv[1] if len(sys.argv) > 1 else 'Australia #1'
SEC = sys.argv[2] if len(sys.argv) > 2 else 'all'
CAUSES = ('wall', 'own', 'other', 'mover', 'hit', 'noact')


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float('nan')


def f1(x):
    return '%.1f' % x


def f2(x):
    return '%.2f' % x


def curve(gs, title):
    print('==', title, len(gs), 'games')
    print('round | alive u/t | total u/t | longest u/t | 2nd u/t | queen u/t || in the 25 rounds ending here: natural eaten u/t | drops eaten u/t | splits u/t | deaths u/t | of which rammed(hit) u/t | ram as mover u/t')
    for z in range(0, 21):
        r = min(z * 25, 499)
        us, ts = [], []
        for g in gs:
            s = [x for x in g['snaps'] if x[0] == r]
            if s:
                us.append(s[0][1]); ts.append(s[0][2])
        if not us:
            continue
        line = ['%3d' % r] + ['%s/%s' % (f1(mean([u[k] for u in us])), f1(mean([t[k] for t in ts]))) for k in (0, 1, 2, 6, 4)]
        if z > 0:
            b = z - 1
            bu = [g['bins']['u'][b] for g in gs]
            bt = [g['bins']['t'][b] for g in gs]
            for fn in (lambda x: x['en'], lambda x: x['ed'], lambda x: x['sp'], lambda x: sum(x['d'].values()),
                       lambda x: x['d']['hit'], lambda x: x['d']['mover']):
                line.append('%s/%s' % (f1(mean([fn(x) for x in bu])), f1(mean([fn(x) for x in bt]))))
        print(' | '.join(line))


def rams(gs, lo, hi, title):
    ev = [(g, e) for g in gs for e in g['hos'] if e['cross'] and lo <= e['r'] <= hi]
    n = len(gs)
    print('==', title, 'rounds', lo, hi, ':', len(ev), 'cross-team meetings in', n, 'games')
    for ms, name in (('t', 'THEY ram us'), ('u', 'WE ram them')):
        es = [e for g, e in ev if e['ms'] == ms]
        if not es:
            print(name, 'none'); continue
        vs = 'u' if ms == 't' else 't'
        m = len(es)
        print(name, ': %.1f a game (%d). mover len %.2f, victim len %.2f; victim len dist %s' % (
            m / n, m, mean([e['Lm'] for e in es]), mean([e['Lv'] for e in es]),
            dict(sorted(Counter(min(e['Lv'], 8) for e in es).items()))))
        print('   mover len dist', dict(sorted(Counter(min(e['Lm'], 8) for e in es).items())))
        print('   steps to hit: %s ; paid sprint (step > free) %.3f' % (dict(sorted(Counter(min(e['k'], 5) for e in es).items())),
                                                                       mean([int(e['k'] > e['free']) for e in es])))
        kn = [e for e in es if e['dbefore'] is not None and e['dafter'] is not None]
        print('   victim last own move (n=%d): distance to that head before->after: closer %.3f, same %.3f, farther %.3f; head was in its 7x7 view %.3f; it ate on that move %.3f; a pearl beside it afterwards %.3f' % (
            len(kn), mean([int(e['dafter'] < e['dbefore']) for e in kn]), mean([int(e['dafter'] == e['dbefore']) for e in kn]),
            mean([int(e['dafter'] > e['dbefore']) for e in kn]), mean([e['vis'] for e in kn]), mean([int(e['vate'] > 0) for e in kn]),
            mean([e['vpearl'] for e in kn])))
        print('   dafter dist', dict(sorted(Counter(e['dafter'] for e in kn).items())), 'dbefore dist', dict(sorted(Counter(e['dbefore'] for e in kn).items())))
        print('   victim was its side longest %.3f (len>=8: %d); victim was queen %.3f; mover was queen %.3f' % (
            mean([e['vtop'] for e in es]), sum(1 for e in es if e['Lv'] >= 8), mean([e['vq'] for e in es]), mean([e['mq'] for e in es])))
        drop = sum(e['drop'] for e in es)
        em = sum(e['eat'][ms] for e in es)
        evv = sum(e['eat'][vs] for e in es)
        Lm = sum(e['Lm'] for e in es)
        Lv = sum(e['Lv'] for e in es)
        print('   pearls dropped %.2f a meeting; eaten within 15 rounds: mover side %.3f, victim side %.3f' % (drop / m, em / max(1, drop), evv / max(1, drop)))
        print('   length per meeting: mover side loses %.2f gets back %.2f = net %.2f ; victim side loses %.2f gets back %.2f = net %.2f' % (
            Lm / m, em / m, (em - Lm) / m, Lv / m, evv / m, (evv - Lv) / m))
        print('   per game: mover side net %.1f, victim side net %.1f' % ((em - Lm) / n, (evv - Lv) / n))
        print('   heads within 5 steps of the mover start: mover side %.2f, victim side %.2f; mover side more %.3f' % (
            mean([e['near_m'] for e in es]), mean([e['near_v'] for e in es]), mean([int(e['near_m'] > e['near_v']) for e in es])))
        print('   victim had that head adjacent at its own turn start (declined or could not) %.3f' % mean([e['decl'] for e in es]))


def chances(gs, lo, hi, title):
    n = len(gs)
    print('==', title, 'adjacent enemy head at turn start, actor length<=4 / longer; rounds', lo, hi)
    for s, name in (('u', 'ours'), ('t', 'theirs')):
        for z, zn in ((0, 'len<=4'), (1, 'len>=5')):
            opp = took = oppw = decl = turns = 0
            for g in gs:
                for b in range(lo // 25, min(20, hi // 25 + 1)):
                    x = g['bins'][s][b]
                    opp += x['opp'][z]; took += x['took'][z]; oppw += x['oppw'][z]; decl += x['declhit'][z]
                    turns += x['turns']
            print('  %s %s: chances %.1f a game (%d), rammed in %.3f; target met our big-layout size rule in %.3f of chances; not ramming and then rammed by that head before its next turn %.3f' % (
                name, zn, opp / n, opp, took / max(1, opp), oppw / max(1, opp), decl / max(1, opp - took)))


def bigs(gs, title):
    n = len(gs)
    print('==', title, 'deaths of dragons of length 8+ per game by cause')
    for lo, hi in ((101, 300), (301, 499)):
        for s, name in (('u', 'ours'), ('t', 'theirs')):
            c = Counter()
            L = Counter()
            top = 0
            for g in gs:
                for r, sd, ln, cause, tp in g['bigs']:
                    if sd == s and lo <= r <= hi:
                        c[cause] += 1; L[cause] += ln; top += tp
            print('  r%d-%d %s: %s ; length lost %s ; was the longest %.2f' % (lo, hi, name, {k: round(v / n, 2) for k, v in c.items()},
                                                                         {k: round(v / n, 1) for k, v in L.items()}, top / n))


def finals(gs, title):
    print('==', title, 'final standings per game (us alive/total/longest vs them), r300 and r400 longest')
    for g in sorted(gs, key=lambda g: g['game']):
        fu, ft = g['final']['us'], g['final']['them']
        s = {x[0]: x for x in g['snaps']}
        def at(r, k):
            return '%d/%d' % (s[r][1][k], s[r][2][k]) if r in s else 'NA'
        print('  %d %s %-15s r%d | r100 alive %s total %s | r150 %s %s | r200 %s %s | r300 %s %s long %s | r400 %s %s long %s | end %d/%d %d/%d long %d/%d' % (
            g['game'], g['result'], g['ended'], g['last'], at(100, 0), at(100, 1), at(150, 0), at(150, 1), at(200, 0), at(200, 1),
            at(300, 0), at(300, 1), at(300, 2), at(400, 0), at(400, 1), at(400, 2),
            fu['alive'], ft['alive'], fu['total'], ft['total'], fu['longest'], ft['longest']))


def bylayout():
    by = defaultdict(list)
    for g in games:
        by[g['layout']].append(g)
    print('layout | cells | games | won | r101-300 per game: they ram / we ram | their paid-sprint share | net length from meetings they start: them / us | from meetings we start: us / them | our chances len<=4 a game, taken | their chances, taken | alive r300 u/t | longest r300 u/t')
    out = []
    for lay, gs in by.items():
        n = len(gs)
        ev = [e for g in gs for e in g['hos'] if e['cross'] and 101 <= e['r'] <= 300]
        te = [e for e in ev if e['ms'] == 't']
        ue = [e for e in ev if e['ms'] == 'u']
        def net(es, a):
            return sum(e['eat'][a] for e in es) - sum((e['Lm'] if e['ms'] == a else e['Lv']) for e in es)
        opp = {s: sum(g['bins'][s][b]['opp'][0] for g in gs for b in range(4, 12)) for s in 'ut'}
        took = {s: sum(g['bins'][s][b]['took'][0] for g in gs for b in range(4, 12)) for s in 'ut'}
        s300 = [[x for x in g['snaps'] if x[0] == 300] for g in gs]
        s300 = [x[0] for x in s300 if x]
        out.append((len(te) / n, [lay, gs[0]['w'] * gs[0]['h'], n, sum(g['result'] == 'win' for g in gs),
                    '%.1f / %.1f' % (len(te) / n, len(ue) / n), f2(mean([int(e['k'] > e['free']) for e in te])),
                    '%.1f / %.1f' % (net(te, 't') / n, net(te, 'u') / n), '%.1f / %.1f' % (net(ue, 'u') / n, net(ue, 't') / n),
                    '%.1f, %.2f' % (opp['u'] / n, took['u'] / max(1, opp['u'])), '%.1f, %.2f' % (opp['t'] / n, took['t'] / max(1, opp['t'])),
                    '%.0f/%.0f' % (mean([x[1][0] for x in s300]), mean([x[2][0] for x in s300])),
                    '%.0f/%.0f' % (mean([x[1][2] for x in s300]), mean([x[2][2] for x in s300]))]))
    for k, l in sorted(out, key=lambda z: -z[0]):
        print(' | '.join(str(x) for x in l))


gs = [g for g in games if g['layout'] == LAY]
print('games loaded', len(games), 'on', LAY, len(gs))
if SEC in ('all', 'curve'):
    curve(gs, LAY + ' all')
    curve([g for g in gs if g['result'] == 'loss'], LAY + ' losses')
    curve([g for g in gs if g['result'] == 'win'], LAY + ' wins')
if SEC in ('all', 'rams'):
    rams(gs, 0, 100, LAY)
    rams(gs, 101, 300, LAY)
    rams([g for g in gs if g['result'] == 'win'], 101, 300, LAY + ' wins')
    rams(gs, 301, 499, LAY)
if SEC in ('all', 'chances'):
    chances(gs, 0, 99, LAY)
    chances(gs, 100, 299, LAY)
    chances(gs, 300, 499, LAY)
if SEC in ('all', 'bigs'):
    bigs(gs, LAY)
if SEC in ('all', 'finals'):
    finals(gs, LAY)
if SEC in ('all', 'layouts'):
    bylayout()
