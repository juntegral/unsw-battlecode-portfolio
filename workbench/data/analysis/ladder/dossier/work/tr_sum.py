"""Scratch (diag-toprams): one line per sample, the same classes as tr_why.py. Samples: our side and each opponent's side of the direct
games (D tags), and each studied team's side of its ladder games (T tags). Non-queen dragons of 2 to 4, rounds 0 to rmax.
Usage: python3 tr_sum.py <D tags> <T tags or -> [rmax]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
ME = 1119
NAMES = {157: 'larp', 306: 'Cutlery', 454: 'aAah', 70: 'chad gdp'}
RM = int(sys.argv[3]) if len(sys.argv) > 3 else 150


def chosen(row):
    f = row.get('first', -1)
    for o in row.get('opt', ()):
        if o[0] == f:
            return o
    return None


def ocls(row, o):
    best = 0
    for e, c in zip(row['near'], o[3]):
        if e[1] <= 4 and c > best:
            best = c
    return best


S = defaultdict(Counter)


def add(gm, want, name):
    k = S[name]
    k['games'] += 1
    for z in gm['turns']:
        if z[0] == want and z[1] <= 1:
            k['all turns'] += z[4]
    for ram in gm['rams']:
        if ram['cross'] and ram['r'] <= RM:
            if ram['ms'] != want:
                k['rammed'] += 1
                if ram['Lv'] <= 4 and not ram['vq']:
                    k['short rammed'] += 1
                    k['v lost'] += ram['Lv']
                    k['v got'] += ram['mv'] + ram['vv']
                    k['v other lost'] += ram['L0']
                    k['v other got'] += ram['mm'] + ram['vm']
                    k['v steps%d' % min(ram['k'], 3)] += 1
            else:
                k['started'] += 1
                k['m lost'] += ram['L0']
                k['m got'] += ram['mm'] + ram['vm']
                k['m other lost'] += ram['Lv']
                k['m other got'] += ram['mv'] + ram['vv']
    mk = gm['marks'].get('100')
    if mk:
        k['g100'] += 1
        k['n100'] += mk[want][0]
    for row in gm['rows']:
        if row['s'] != want or row['q'] or row['r'] > RM or row['L'] > 4 or row.get('lite'):
            continue
        hit = 'hit' in row and gm['rams'][row['hit']]['cross'] == 1 and gm['rams'][row['hit']]['r'] <= RM
        start = max([e[6] for e in row['near'] if e[1] <= 4] or [0])
        if any(e[1] <= 4 and e[3] <= 3 for e in row['near']):
            k['contact'] += 1
            if hit:
                k['contact hit'] += 1
        dead = row.get('dead')
        ch = chosen(row)
        if start >= 3:
            k['answer'] += 1
        if dead == 3:
            k['it rammed'] += 1
            if start >= 3:
                k['answer: rammed'] += 1
            continue
        if dead is not None or ch is None:
            continue
        cc = ocls(row, ch)
        if cc >= 3 and start < 3:
            k['walk-in'] += 1
            who = 'trader' if row['tn'] else 'eating' if ch[1] else 'neither'
            k['walk-in ' + who] += 1
            k['walk-in cls%d' % cc] += 1
            if hit:
                k['walk-in hit'] += 1
                k['walk-in ' + who + ' hit'] += 1
                k['walk-in cls%d hit' % cc] += 1
        elif cc >= 3:
            k['stayed'] += 1
            if hit:
                k['stayed hit'] += 1
        elif start >= 3:
            k['stepped out'] += 1
            if hit:
                k['stepped out hit'] += 1
        elif cc == 1:
            k['pearl-only'] += 1
            if hit:
                k['pearl-only hit'] += 1


for tag in sys.argv[1].split(','):
    for line in Path(W + 'tr_scan-' + tag + '.jsonl').read_text().splitlines():
        if line.strip():
            gm = json.loads(line)
            os_ = 0 if gm['a'] == ME else 1
            opp = NAMES.get(gm['b'] if os_ == 0 else gm['a'])
            add(gm, os_, 'ours v ' + opp)
            add(gm, os_, 'ours v all three')
            add(gm, 1 - os_, opp + ' v ours')
if sys.argv[2] != '-':
    for tag in sys.argv[2].split(','):
        for line in Path(W + 'tr_scan-' + tag + '.jsonl').read_text().splitlines():
            if line.strip():
                gm = json.loads(line)
                for z, t in enumerate((gm['a'], gm['b'])):
                    if t in NAMES:
                        add(gm, z, NAMES[t] + ' ladder')


def r(a, b):
    return '%.2f' % (a / b) if b else '-'


for name in sorted(S):
    k = S[name]
    g = k['games']
    print(name, '| games', g, '| dragons r100 %.1f' % (k['n100'] / max(1, k['g100'])),
          '| rammed /1k turns %.2f, started /1k %.2f' % (1000 * k['rammed'] / k['all turns'], 1000 * k['started'] / k['all turns']),
          '| short rammed a game %.1f (1 step %s, 2 %s, 3+ %s)' % (k['short rammed'] / g, r(k['v steps1'], k['short rammed']), r(k['v steps2'], k['short rammed']), r(k['v steps3'], k['short rammed'])),
          '| contact turns a game %.0f, rammed after %s' % (k['contact'] / g, r(k['contact hit'], k['contact'])),
          '| walk-in a game %.1f, rammed %s (free reach %d: %s; one paid %d: %s)' % (k['walk-in'] / g, r(k['walk-in hit'], k['walk-in']), k['walk-in cls4'], r(k['walk-in cls4 hit'], k['walk-in cls4']), k['walk-in cls3'], r(k['walk-in cls3 hit'], k['walk-in cls3'])),
          '| walk-in by trader %d: %s; eating %d: %s; neither %d: %s' % (k['walk-in trader'], r(k['walk-in trader hit'], k['walk-in trader']), k['walk-in eating'], r(k['walk-in eating hit'], k['walk-in eating']), k['walk-in neither'], r(k['walk-in neither hit'], k['walk-in neither'])),
          '| answer turns a game %.1f: rammed %s, stepped out %s (hit %s), stayed %s (hit %s)' % (k['answer'] / g, r(k['answer: rammed'], k['answer']), r(k['stepped out'], k['answer']), r(k['stepped out hit'], k['stepped out']), r(k['stayed'], k['answer']), r(k['stayed hit'], k['stayed'])),
          '| pearl-only reach %d: %s' % (k['pearl-only'], r(k['pearl-only hit'], k['pearl-only'])),
          '| as victim (short): lost %s regained %s, other side lost %s regained %s' % (r(k['v lost'], k['short rammed']), r(k['v got'], k['short rammed']), r(k['v other lost'], k['short rammed']), r(k['v other got'], k['short rammed'])),
          '| as attacker: lost %s regained %s, other side lost %s regained %s' % (r(k['m lost'], k['started']), r(k['m got'], k['started']), r(k['m other lost'], k['started']), r(k['m other got'], k['started'])))
