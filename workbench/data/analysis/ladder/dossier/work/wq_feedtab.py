"""Scratch (diag-whq): tables from wq_feed rows. Usage: python3 .../wq_feedtab.py [O|R] [class]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q', 'agg8-q2': 'B7Q'}
WN = ('0-100', '101-200', '201-300', '301-400', '401+')


def load(prefix):
    rows = []
    for p in sorted(WORK.glob(prefix)):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def decided(g):
    a, b = g['ends']
    if a[3] == 0 or b[3] == 0:
        return 'E'
    if a[0] != b[0]:
        return 'Q'
    if a[1] != b[1]:
        return 'L'
    return 'T'


def block(rows, title):
    n = len(rows)
    if not n:
        return
    print()
    print('==', title, '| games', n, '| side 0 wins', sum(1 for g in rows if g['result'] == 'win'))
    for s, nm in ((0, 'side0'), (1, 'side1')):
        print(' ', nm)
        # track
        for cp in (100, 200, 250, 300, 350, 400, 450, 475):
            ql = []; tl = []; sl = []; al = []; tot = []
            nr = [0, 0, 0, 0]
            for g in rows:
                tr = [t for t in g['track'] if t[0] == cp]
                if tr:
                    t = tr[0]
                    o = 1 + s * 5
                    ql.append(t[o]); tl.append(t[o + 1]); sl.append(t[o + 2]); al.append(t[o + 3]); tot.append(t[o + 4])
                    for z in range(4):
                        nr[z] += t[11 + s * 4 + z]
            if ql:
                qa = [x for x in ql if x]
                print('    r%d (games still on %d): queen alive %d, her length %.1f | longest %.1f second %.1f alive %.1f total %.0f | longest share of total %.0f%%' % (
                    cp, len(ql), len(qa), sum(qa) / max(1, len(qa)), sum(tl) / len(tl), sum(sl) / len(sl), sum(al) / len(al), sum(tot) / len(tot), 100 * sum(tl) / max(1, sum(tot))))
                print('        the others: mean tiles from the longest %.1f; within 6 tiles %.0f%%; within 15 tiles %.0f%%' % (nr[1] / max(1, nr[0]), 100 * nr[2] / max(1, nr[0]), 100 * nr[3] / max(1, nr[0])))
        e = [g['ends'][s] for g in rows]
        qa = [x[0] for x in e if x[0]]
        print('    end: queen alive %d, her length %.1f | longest %.1f second %.1f alive %.1f total %.0f | longest share %.0f%%' % (
            len(qa), sum(qa) / max(1, len(qa)), sum(x[1] for x in e) / n, sum(x[2] for x in e) / n, sum(x[3] for x in e) / n, sum(x[4] for x in e) / n, 100 * sum(x[1] for x in e) / max(1, sum(x[4] for x in e))))
        E = Counter()
        for g in rows:
            for w, sd, role, origin, v in g['EAT']:
                if sd == s:
                    o = 'natural' if origin == 'n' else 'their dead' if origin == 'e' else 'own stop' if origin == 'stop' else 'own other dead'
                    E[(w, role, o)] += v
                    E[(w, role)] += v
        for role, rn in (('q', 'queen'), ('t', 'longest 5+ (not queen)'), ('o', 'others')):
            print('    pearls a game eaten by %s: ' % rn + '; '.join('%s: %.1f (natural %.1f, own stops %.1f, own other dead %.1f, their dead %.1f)' % (
                WN[w], E[(w, role)] / n, E[(w, role, 'natural')] / n, E[(w, role, 'own stop')] / n, E[(w, role, 'own other dead')] / n, E[(w, role, 'their dead')] / n) for w in range(5)))
        st = [x for g in rows for x in g['STOPS'] if x['s'] == s]
        for w in range(5):
            lo, hi = (0, 101, 201, 301, 401)[w], (100, 200, 300, 400, 999)[w]
            ss = [x for x in st if lo <= x['r'] <= hi]
            if not ss:
                continue
            m = len(ss)
            td = [x['td'] for x in ss if x['td'] is not None]
            print('    stops %s: %.1f a game, mean L %.1f, own count then %.0f | to own longest: beside %.0f%%, 2-3 %.0f%%, 4-6 %.0f%%, farther %.0f%%; longest then %.1f, it is the queen %.0f%% | pearls dropped %.1f a game: eaten by queen %.0f%%, longest %.0f%%, others %.0f%%, within 10 rounds %.0f%% | enemy head within 4: %.0f%%' % (
                WN[w], m / n, sum(x['L'] for x in ss) / m, sum(x['n'] for x in ss) / m,
                100 * sum(1 for d in td if d <= 1) / max(1, len(td)), 100 * sum(1 for d in td if 2 <= d <= 3) / max(1, len(td)),
                100 * sum(1 for d in td if 4 <= d <= 6) / max(1, len(td)), 100 * sum(1 for d in td if d > 6) / max(1, len(td)),
                sum(x['tL'] for x in ss) / m, 100 * sum(x['tq'] for x in ss) / m, sum(x['drop'] for x in ss) / n,
                100 * sum(x['by_q'] for x in ss) / max(1, sum(x['drop'] for x in ss)), 100 * sum(x['by_t'] for x in ss) / max(1, sum(x['drop'] for x in ss)),
                100 * sum(x['by_o'] for x in ss) / max(1, sum(x['drop'] for x in ss)), 100 * sum(x['fast'] for x in ss) / max(1, sum(x['drop'] for x in ss)),
                100 * sum(1 for x in ss if x['e4']) / m))
        for lo, hi, nm in ((201, 300, '201-300'), (301, 400, '301-400'), (401, 999, '401+')):
            ss = [x for x in st if lo <= x['r'] <= hi and 'd2' in x]
            if not ss:
                continue
            m = len(ss)
            d2 = [x['d2'] for x in ss if x['d2'] is not None]
            print('    stops %s (%d): a mate at least twice its length within 1 tile %.0f%%, 2-3 %.0f%%, 4-6 %.0f%%, farther or none %.0f%%; that mate mean L %.1f; pearls eaten by that mate %.0f%%; length of the stopped: 2: %.0f%%, 3: %.0f%%, 4: %.0f%%, 5-9: %.0f%%, 10+: %.0f%%' % (
                nm, m, 100 * sum(1 for d in d2 if d <= 1) / m, 100 * sum(1 for d in d2 if 2 <= d <= 3) / m, 100 * sum(1 for d in d2 if 4 <= d <= 6) / m,
                100 * (m - sum(1 for d in d2 if d <= 6)) / m, sum(x['L2'] for x in ss if x['d2'] is not None and x['d2'] <= 6) / max(1, sum(1 for d in d2 if d <= 6)),
                100 * sum(x['by_n'] for x in ss) / max(1, sum(x['drop'] for x in ss)),
                100 * sum(1 for x in ss if x['L'] == 2) / m, 100 * sum(1 for x in ss if x['L'] == 3) / m, 100 * sum(1 for x in ss if x['L'] == 4) / m,
                100 * sum(1 for x in ss if 5 <= x['L'] <= 9) / m, 100 * sum(1 for x in ss if x['L'] >= 10) / m))
        D = Counter()
        for g in rows:
            for w, sd, kd, fate, v in g['DROP']:
                if sd == s:
                    D[(kd, fate)] += v
        for kd in ('stop', 'boxed', 'rams', 'rammed', 'mate head', 'mate body', 'own move', 'body'):
            dr = D[(kd, 'dropped')]
            if dr:
                print('    dead by %s: %.1f dragons a game, length %.1f, pearls %.1f: own queen %.0f%%, own longest %.0f%%, own others %.0f%%, enemy %.0f%%, left %.0f%%' % (
                    kd, D[(kd, 'dragons')] / n, D[(kd, 'length')] / n, dr / n, 100 * D[(kd, 'own q')] / dr, 100 * D[(kd, 'own t')] / dr, 100 * D[(kd, 'own o')] / dr, 100 * D[(kd, 'enemy')] / dr,
                    100 * (dr - D[(kd, 'own q')] - D[(kd, 'own t')] - D[(kd, 'own o')] - D[(kd, 'enemy')]) / dr))
        B = [x for g in rows for x in g['BIG'] if x['s'] == s]
        bq = [x for x in B if x['q']]
        bt = [x for x in B if not x['q']]
        print('    queen deaths %d in %d games: %s | median round %s' % (len(bq), n, dict(Counter(x['k'] for x in bq)), sorted(x['r'] for x in bq)[len(bq) // 2] if bq else None))
        print('    deaths of a longest dragon of 8+ (not queen) %d (%.2f a game), mean L %.1f: %s; r301+: %d' % (len(bt), len(bt) / n, sum(x['L'] for x in bt) / max(1, len(bt)), dict(Counter(x['k'] for x in bt)), sum(1 for x in bt if x['r'] > 300)))
        bql = [x for x in bq if x['L'] >= 8]
        print('    queen deaths at length 8+: %d, mean L %.1f: %s' % (len(bql), sum(x['L'] for x in bql) / max(1, len(bql)), dict(Counter(x['k'] for x in bql))))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'O'
    klass = sys.argv[2] if len(sys.argv) > 2 else None
    rows = load('wq_feed-%s[0-9].jsonl' % mode)
    if mode != 'O':
        block(rows, mode + ' all')
        block([g for g in rows if g['cells'] > 1200], mode + ' above 1200 cells')
        return
    for opp in ('WeHaveQuizzes', 'Big Bobs Bots'):
        rs = [g for g in rows if g['opp'] == opp]
        if klass == 'big':
            for arm in ('MAIN', 'B7', 'B7Q'):
                block([g for g in rs if ARM[g['src']] == arm and g['cells'] > 1200], '%s %s above 1200 cells' % (opp, arm))
            block([g for g in rs if ARM[g['src']] != 'MAIN' and g['cells'] > 1200], '%s B7 and B7Q above 1200 cells' % opp)
            block([g for g in rs if g['cells'] > 1200], '%s all arms above 1200 cells' % opp)
        elif klass:
            for arm in ('MAIN', 'B7', 'B7Q', 'all'):
                block([g for g in rs if (arm == 'all' or ARM[g['src']] == arm) and g['result'] == 'loss' and decided(g) == klass], '%s %s losses decided by %s' % (opp, arm, klass))
        else:
            for arm in ('MAIN', 'B7', 'B7Q'):
                block([g for g in rs if ARM[g['src']] == arm], opp + ' ' + arm)
            block(rs, opp + ' all arms')


main()
