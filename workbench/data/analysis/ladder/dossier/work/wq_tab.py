"""Scratch (diag-whq): fingerprint tables from wq_scan rows. Usage: python3 .../wq_tab.py [R]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q', 'agg8-q2': 'B7Q'}
CL = ('2', '3', '4', '5-9', '10+')
WN = ('0-40', '41-100', '101-200', '201-300', '301-400', '401+')


def load(prefix):
    rows = []
    for p in sorted(WORK.glob(prefix)):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def pd(d):
    return max(0, d['m']['steps'] - (d['m']['L0'] + 3) // 4)


def f1(x):
    return 'NA' if x is None else '%.1f' % x


def metrics(rows, s):
    m = {}
    n = len(rows)
    T = Counter(); E = Counter(); S = Counter(); MV = Counter()
    for g in rows:
        for w, sd, c, z, q, v in g['T']:
            if sd == s:
                T[('c', c)] += v; T[('w', w)] += v; T[('z', w, z)] += v; T['all'] += v; T[('wc', w, c)] += v
                if q:
                    T[('q', w)] += v; T[('qc', c)] += v; T['q'] += v
        for w, sd, c, o, q, v in g['E']:
            if sd == s:
                E[('c', c)] += v; E[('o', o)] += v; E['all'] += v; E[('w', w)] += v; E[('wc', w, c)] += v; E[('co', c, o)] += v
                if q:
                    E[('q', w)] += v; E['q'] += v
        for w, sd, lb, lc, q, v in g['S']:
            if sd == s:
                S['all'] += v; S[('lb', min(lb, 8))] += v; S[('w', w)] += v; S[('lc', min(lc, 4))] += v
                if q:
                    S['q'] += v
        for w, sd, c, k, v in g['MV']:
            if sd == s:
                MV[(c, k)] += v; MV[k] += v
    m['games; turns a game'] = '%d; %.0f' % (n, T['all'] / n)
    m['pearls /1k turns: all'] = f1(1000 * E['all'] / T['all'])
    m['pearls /1k turns at L2; L3; L4; L5-9; L10+'] = '; '.join(f1(1000 * E[('c', c)] / T[('c', c)]) if T[('c', c)] else 'NA' for c in range(5))
    m['share of turns at L2; L3; L4; L5-9; L10+ (%)'] = '; '.join('%.0f' % (100 * T[('c', c)] / T['all']) for c in range(5))
    m['pearls a game: natural; own dead; their dead'] = '; '.join(f1(E[('o', o)] / n) for o in range(3))
    m['L10+ pearls a game: natural; own dead; their dead'] = '; '.join(f1(E[('co', 4, o)] / n) for o in range(3))
    m['pearls /1k turns r0-40; 41-100; 101-200; 201-300; 301-400; 401+'] = '; '.join(f1(1000 * E[('w', w)] / T[('w', w)]) if T[('w', w)] else 'NA' for w in range(6))
    m['splits /1k turns; a game'] = '%.1f; %.1f' % (1000 * S['all'] / T['all'], S['all'] / n)
    m['split at length 4; 5; 6; 7; 8+ (%)'] = '; '.join('%.0f' % (100 * S[('lb', k)] / max(1, S['all'])) for k in (4, 5, 6, 7, 8))
    m['child length 2; 3; 4+ (%)'] = '; '.join('%.0f' % (100 * S[('lc', k)] / max(1, S['all'])) for k in (2, 3, 4))
    m['steps a turn at L2; L3; L4; L5-9; L10+'] = '; '.join('%.2f' % (MV[(c, 'steps')] / T[('c', c)]) if T[('c', c)] else 'NA' for c in range(5))
    m['paid segments /1k turns at L3; L4; L5-9; L10+'] = '; '.join(f1(1000 * MV[(c, 'paid segs')] / T[('c', c)]) if T[('c', c)] else 'NA' for c in range(1, 5))
    m['turns with no step /1k'] = f1(1000 * MV['stay'] / T['all'])
    for cp in (50, 100, 200, 300, 400, 500):
        al = []; lg = []; tot = []; ql = []
        for g in rows:
            st = g['snap'][min(cp, g['last'])] if cp < 500 else g['final']
            al.append(st[s * 4]); tot.append(st[s * 4 + 1]); lg.append(st[s * 4 + 2]); ql.append(st[s * 4 + 3])
        m['r%d: alive; longest; total; queen alive (games), her length alive' % cp] = '%.1f; %.1f; %.0f; %d, %s' % (sum(al) / n, sum(lg) / n, sum(tot) / n, sum(1 for x in ql if x), f1(sum(ql) / max(1, sum(1 for x in ql if x))))
    D = Counter(); DL = Counter()
    for g in rows:
        for d in g['deaths']:
            if d['s'] != s:
                continue
            c = d['c']
            if c == 'head-on':
                c = ('rams an enemy head' if d['role'] == 'mover' else 'rammed by an enemy head') if d['cross'] else 'head-on with a mate'
            elif c == 'other body':
                c = 'body: ' + d.get('hit', 'unknown')
            elif c in ('wall', 'own body'):
                c = c + (' (boxed)' if d.get('free', 1) == 0 else ' (free tile)')
            elif d.get('free', 1) == 0:
                c = c + ' (boxed)'
            D[c] += 1; DL[c] += d['L']
    tot = sum(D.values())
    m['deaths a game; /1k turns; length lost a game'] = '%.1f; %.1f; %.0f' % (tot / n, 1000 * tot / T['all'], sum(DL.values()) / n)
    for c, v in D.most_common():
        m['death: ' + c + ' (a game; mean L)'] = '%.1f; %.1f' % (v / n, DL[c] / v)
    # rams started by side s
    R = [d for g in rows for d in g['deaths'] if d['c'] == 'head-on' and d['role'] == 'hit' and d['cross'] and d['m']['s'] == s]
    nr = max(1, len(R))
    m['rams started a game; r0-100; 101-300; 301+'] = '%.1f; %.1f; %.1f; %.1f' % (len(R) / n, sum(1 for d in R if d['r'] <= 100) / n, sum(1 for d in R if 100 < d['r'] <= 300) / n, sum(1 for d in R if d['r'] > 300) / n)
    m['rammer length at turn start 2; 3; 4; 5+ (%)'] = '; '.join('%.0f' % (100 * sum(1 for d in R if (min(d['m']['L0'], 5) == k)) / nr) for k in (2, 3, 4, 5))
    m['victim length 2; 3; 4; 5-9; 10+ (%)'] = '; '.join('%.0f' % (100 * sum(1 for d in R if (0 if d['L'] <= 2 else 1 if d['L'] == 3 else 2 if d['L'] == 4 else 3 if d['L'] <= 9 else 4) == k) / nr) for k in range(5))
    m['victim shorter; same to under twice; twice or more (%)'] = '; '.join('%.0f' % (100 * sum(1 for d in R if (0 if d['L'] < d['m']['L0'] else 1 if d['L'] < 2 * d['m']['L0'] else 2) == k) / nr) for k in range(3))
    m['ram steps 1; 2; 3; 4+ (%)'] = '; '.join('%.0f' % (100 * sum(1 for d in R if min(d['m']['steps'], 4) == k) / nr) for k in (1, 2, 3, 4))
    m['rams paid (%); segments paid a ram; ate on the way (%)'] = '%.0f; %.2f; %.0f' % (100 * sum(1 for d in R if pd(d) > 0) / nr, sum(pd(d) for d in R) / nr, 100 * sum(1 for d in R if d['m']['ate'] > 0) / nr)
    m['rams from length 3 by steps 1; 2; 3+ (count)'] = '; '.join('%d' % sum(1 for d in R if d['m']['L0'] == 3 and min(d['m']['steps'], 3) == k) for k in (1, 2, 3))
    m['victim is the queen (a game); victim is its side longest and 5+ (a game), mean L'] = '%.2f; %.2f, %s' % (sum(1 for d in R if d['q']) / n, sum(1 for d in R if d['top'] and d['L'] >= 5) / n, f1(sum(d['L'] for d in R if d['top'] and d['L'] >= 5) / max(1, sum(1 for d in R if d['top'] and d['L'] >= 5))))
    m['length a ram: rammer side loses; victim side loses'] = '%.2f; %.2f' % (sum(d['m']['L'] + pd(d) for d in R) / nr, sum(d['L'] for d in R) / nr)
    m['zone of the hit for the rammer: own; middle; theirs (%)'] = '; '.join('%.0f' % (100 * sum(1 for d in R if d['m']['z'] == k) / nr) for k in range(3))
    m['turn zone own; middle; theirs (%) r0-100'] = '; '.join('%.0f' % (100 * sum(T[('z', w, z)] for w in (0, 1)) / max(1, sum(T[('w', w)] for w in (0, 1)))) for z in range(3))
    m['turn zone own; middle; theirs (%) r101-300'] = '; '.join('%.0f' % (100 * sum(T[('z', w, z)] for w in (2, 3)) / max(1, sum(T[('w', w)] for w in (2, 3)))) for z in range(3))
    m['turn zone own; middle; theirs (%) r301+'] = '; '.join('%.0f' % (100 * sum(T[('z', w, z)] for w in (4, 5)) / max(1, sum(T[('w', w)] for w in (4, 5)))) for z in range(3))
    # first 40
    p = defaultdict(list)
    for g in rows:
        cum = 0; sp = 0; firsts = []; fsplit = None
        by = {}
        for row in g['rc']:
            r = row[0]
            e = row[1 + s * 5 + 2] + row[1 + s * 5 + 3]
            for _ in range(e):
                firsts.append(r)
            if row[1 + s * 5 + 1] and fsplit is None:
                fsplit = r
            cum += e; sp += row[1 + s * 5 + 1]
            by[r] = (cum, sp)
        for cp in (10, 20, 30, 40):
            rr = max((r for r in by if r <= cp), default=None)
            p['e%d' % cp].append(by[rr][0] if rr is not None else 0)
            p['s%d' % cp].append(by[rr][1] if rr is not None else 0)
        p['second'].append(firsts[1] if len(firsts) > 1 else 999)
        p['fourth'].append(firsts[3] if len(firsts) > 3 else 999)
        p['fsplit'].append(fsplit if fsplit is not None else 999)
        for cp in (20, 40):
            st = g['snap'][min(cp, g['last'])]
            p['a%d' % cp].append(st[s * 4]); p['t%d' % cp].append(st[s * 4 + 1])
        fx = [d['r'] for d in g['deaths'] if d['c'] == 'head-on' and d.get('cross')]
        p['fx'].append(min(fx) if fx else 999)
    m['pearls eaten by r10; r20; r30; r40 (a game)'] = '; '.join(f1(sum(p['e%d' % cp]) / n) for cp in (10, 20, 30, 40))
    m['splits by r10; r20; r30; r40'] = '; '.join(f1(sum(p['s%d' % cp]) / n) for cp in (10, 20, 30, 40))
    m['alive, total length at r20; r40'] = '%.1f, %.1f; %.1f, %.1f' % (sum(p['a20']) / n, sum(p['t20']) / n, sum(p['a40']) / n, sum(p['t40']) / n)
    m['median round of second pearl; fourth pearl; first split; first cross ram'] = '%s; %s; %s; %s' % (med(p['second']), med(p['fourth']), med(p['fsplit']), med(p['fx']))
    # queen and longest from samples
    q = defaultdict(list)
    for g in rows:
        for smp in g['samples']:
            r = smp[0]; rec = smp[1 + s]
            if rec is None:
                continue
            b = 0 if r <= 100 else 1 if r <= 300 else 2
            q[('n', b)].append(rec['n']); q[('o5', b)].append(rec['o5'] / rec['n']); q[('e5', b)].append(rec['e5'] / rec['n'])
            if 'q' in rec:
                L, z, o5, e5, e3, dist = rec['q']
                q[('qL', b)].append(L); q[('qz', b)].append(z); q[('qo5', b)].append(o5); q[('qe5', b)].append(e5); q[('qd', b)].append(dist); q[('qe3', b)].append(e3)
                q[('qlead', b)].append(rec['top'][5])
            L, z, o5, e5, e3, isq = rec['top']
            if L >= 5:
                q[('tL', b)].append(L); q[('tz', b)].append(z); q[('to5', b)].append(o5); q[('te5', b)].append(e5); q[('te3', b)].append(e3)
    def mean(k):
        return f1(sum(q[k]) / len(q[k])) if q[k] else 'NA'
    def zsh(k):
        return '/'.join('%.0f' % (100 * sum(1 for x in q[k] if x == z) / max(1, len(q[k]))) for z in range(3))
    for b, nm in ((0, 'r0-100'), (1, 'r101-300'), (2, 'r301+')):
        m['queen %s: length; zone own/mid/theirs %%; own heads within 5; enemy heads within 5 (within 3); tiles from start; she is the longest %%' % nm] = '%s; %s; %s; %s (%s); %s; %.0f' % (mean(('qL', b)), zsh(('qz', b)), mean(('qo5', b)), mean(('qe5', b)), mean(('qe3', b)), mean(('qd', b)), 100 * sum(q[('qlead', b)]) / max(1, len(q[('qlead', b)])))
        m['longest (5+) %s: length; zone %%; own heads within 5; enemy heads within 5 (within 3)' % nm] = '%s; %s; %s; %s (%s)' % (mean(('tL', b)), zsh(('tz', b)), mean(('to5', b)), mean(('te5', b)), mean(('te3', b)))
        m['any dragon %s: own heads within 5; enemy heads within 5' % nm] = '%s; %s' % (mean(('o5', b)), mean(('e5', b)))
    m['queen pearls /1k of her turns; her splits a game; pearls a game'] = '%s; %.1f; %.1f' % (f1(1000 * E['q'] / T['q']) if T['q'] else 'NA', S['q'] / n, E['q'] / n)
    # contact turns
    C = Counter()
    for g in rows:
        for w, sd, l0, rel, d0, tq, ttop, isq, oc, v in g['contact']:
            if sd != s or isq:
                continue
            for key in (('all', d0), ('q', d0) if tq else None, ('top', d0) if ttop else None, ('L', min(l0, 4), rel), ('L3d', d0) if l0 == 3 else None, ('L2d', d0) if l0 == 2 else None):
                if key is not None:
                    C[key + ('n',)] += v
                    if oc == 'R':
                        C[key + ('R',)] += v
    def cr(key):
        a, b = C[key + ('R',)], C[key + ('n',)]
        return '%d of %d (%.0f%%)' % (a, b, 100 * a / b) if b else 'NA'
    m['contact turns (nearest enemy head at 1; 2; 3 tiles): rams'] = '; '.join(cr(('all', d)) for d in (1, 2, 3))
    m['... nearest head is the enemy queen, at 1; 2; 3'] = '; '.join(cr(('q', d)) for d in (1, 2, 3))
    m['... nearest head is their longest (5+), at 1; 2; 3'] = '; '.join(cr(('top', d)) for d in (1, 2, 3))
    m['... own length 2, at 1; 2; 3'] = '; '.join(cr(('L2d', d)) for d in (1, 2, 3))
    m['... own length 3, at 1; 2; 3'] = '; '.join(cr(('L3d', d)) for d in (1, 2, 3))
    for L in (2, 3, 4):
        m['... own length %s%s: target shorter; same to under twice; twice or more' % (L, '+' if L == 4 else '')] = '; '.join(cr(('L', L, rel)) for rel in range(3))
    return m


def table(cols):
    names = []
    ms = []
    for title, rows, s in cols:
        mm = metrics(rows, s) if rows else {}
        ms.append(mm)
        for k in mm:
            if k not in names:
                names.append(k)
    print('| measure | ' + ' | '.join(t for t, _, _ in cols) + ' |')
    for k in names:
        print('| ' + k + ' | ' + ' | '.join(mm.get(k, '-') for mm in ms) + ' |')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'O'
    if mode == 'R':
        rows = load('wq_scan-R[0-9].jsonl')
        table([('rank-1', rows, 0), ('rank-1 opponents', rows, 1), ('rank-1 wins: rank-1', [g for g in rows if g['result'] == 'win'], 0)])
        return
    if mode == 'L':
        rows = load('wq_scan-L[0-9].jsonl')
        table([('ours ladder', rows, 0), ('ladder opponents', rows, 1)])
        return
    rows = load('wq_scan-O[0-9].jsonl')
    print('games', len(rows), Counter((ARM[g['src']], g['opp'], g['result']) for g in rows))
    for opp in ('WeHaveQuizzes', 'Big Bobs Bots'):
        cols = []
        for arm in ('MAIN', 'B7', 'B7Q'):
            rs = [g for g in rows if ARM[g['src']] == arm and g['opp'] == opp]
            cols.append((arm + ' ours', rs, 0))
            cols.append((arm + ' ' + opp[:4], rs, 1))
        allr = [g for g in rows if g['opp'] == opp]
        cols.append(('all ' + opp[:4], allr, 1))
        print()
        print('##', opp)
        table(cols)


main()
