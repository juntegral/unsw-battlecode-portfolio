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


DOSSIER = '~/01. Project/\u1100\u1162\u110b\u1175\u11ab \u1111\u1173\u1105\u1169\u110c\u1166\u11a8\u1110\u1173/unsw-swarm/data/analysis/ladder/dossier/'


def r(a, b):
    return '%.2f' % (a / b) if b else '-'


three = Counter()
for nm in ('larp v ours', 'Cutlery v ours', 'aAah v ours'):
    three.update(S[nm])
S['the three v ours'] = three
order = ('aAah ladder', 'chad gdp ladder', 'larp ladder', 'Cutlery ladder', 'ours v all three', 'the three v ours')
rows = []
rows.append(('games', ['%d' % S[c]['games'] for c in order]))
rows.append(('steps into the free-plus-one-paid reach of a head of 2 to 4, a game; rammed after',
             ['%.1f; %s' % (S[c]['walk-in'] / S[c]['games'], r(S[c]['walk-in hit'], S[c]['walk-in'])) for c in order]))
rows.append(('the same step into free reach: rammed after; into the paid ring: rammed after',
             ['%s; %s' % (r(S[c]['walk-in cls4 hit'], S[c]['walk-in cls4']), r(S[c]['walk-in cls3 hit'], S[c]['walk-in cls3'])) for c in order]))
rows.append(('by who steps in, rammed after: a trader by our rule / a dragon eating there / neither',
             ['%s / %s / %s' % (r(S[c]['walk-in trader hit'], S[c]['walk-in trader']), r(S[c]['walk-in eating hit'], S[c]['walk-in eating']), r(S[c]['walk-in neither hit'], S[c]['walk-in neither'])) for c in order]))
rows.append(('turns that begin inside that reach, a game: rams first / steps out / stays (rammed after staying)',
             ['%.1f: %s / %s / %s (%s)' % (S[c]['answer'] / S[c]['games'], r(S[c]['answer: rammed'], S[c]['answer']), r(S[c]['stepped out'], S[c]['answer']), r(S[c]['stayed'], S[c]['answer']), r(S[c]['stayed hit'], S[c]['stayed'])) for c in order]))
rows.append(('a head-on started: length lost, pearls regained in 5 rounds; a short dragon rammed: lost, regained',
             ['%s, %s; %s, %s' % (r(S[c]['m lost'], S[c]['started']), r(S[c]['m got'], S[c]['started']), r(S[c]['v lost'], S[c]['short rammed']), r(S[c]['v got'], S[c]['short rammed'])) for c in order]))
rows.append(('short dragons rammed a game; all dragons rammed, head-ons started per 1,000 turns',
             ['%.1f; %.2f, %.2f' % (S[c]['short rammed'] / S[c]['games'], 1000 * S[c]['rammed'] / S[c]['all turns'], 1000 * S[c]['started'] / S[c]['all turns']) for c in order]))
ladder = '\n'.join('| ' + name + ' | ' + ' | '.join(cells) + ' |' for name, cells in rows)
ngames = 0
for tag in sys.argv[2].split(','):
    for line in Path(W + 'tr_scan-' + tag + '.jsonl').read_text().splitlines():
        if line.strip():
            ngames += 1
text = Path(W + 'tr_report_tpl.txt').read_text()
text = ladder.join(text.split('@@LADDER@@'))
text = ('{:,}'.format(ngames)).join(text.split('@@LGAMES@@'))
text = ('{:,} of {:,} ladder'.format(ngames, ngames)).join(text.split('@@LOK@@'))
text = (chr(96) * 3).join(text.split('~~~'))
print(ladder)
print('lines', len(text.splitlines()))
if len(sys.argv) > 4 and sys.argv[4] == 'write':
    Path(DOSSIER + 'diag-toprams.md').write_text(text)
    print('written')
