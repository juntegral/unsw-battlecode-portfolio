"""Scratch (diag-toprams): overlap of the keep-out rule with the attack switches, why a tile was unmarked, the head-on length account,
and replay turns to cite. Usage: python3 tr_misc.py <tags> [rmax] [examples each]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
NAMES = {157: 'larp', 306: 'Cutlery', 454: 'aAah'}
ME = 1119
tags = sys.argv[1].split(',')
RM = int(sys.argv[2]) if len(sys.argv) > 2 else 150
EX = int(sys.argv[3]) if len(sys.argv) > 3 else 3
games = []
for tag in tags:
    for line in Path(W + 'tr_scan-' + tag + '.jsonl').read_text().splitlines():
        if line.strip():
            games.append(json.loads(line))


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


K = Counter()
A = defaultdict(Counter)
ex = defaultdict(list)
for gm in games:
    os_ = 0 if gm['a'] == ME else 1
    opp = NAMES.get(gm['b'] if os_ == 0 else gm['a'])
    w = gm['w']
    mk = gm['marks'].get('150')
    if mk:
        A[opp]['g150'] += 1
        A[opp]['len us'] += mk[os_][1]
        A[opp]['len them'] += mk[1 - os_][1]
        A[opp]['n us'] += mk[os_][0]
        A[opp]['n them'] += mk[1 - os_][0]
    A[opp]['games'] += 1
    for ram in gm['rams']:
        if not ram['cross'] or ram['r'] > RM:
            continue
        by = 'us' if ram['ms'] == os_ else 'them'
        on = 'them' if by == 'us' else 'us'
        A[opp]['rams by ' + by] += 1
        A[opp]['lost ' + by] += ram['L0']
        A[opp]['lost ' + on] += ram['Lv']
        A[opp]['got ' + by] += ram['mm'] + ram['vm']
        A[opp]['got ' + on] += ram['mv'] + ram['vv']
        A[opp]['dead ' + by] += 1
        A[opp]['dead ' + on] += 1
    for row in gm['rows']:
        if row['s'] != os_ or row.get('lite') or row['q'] or row['r'] > RM or row['L'] > 4:
            continue
        if 'hit' not in row:
            continue
        ram = gm['rams'][row['hit']]
        if not ram['cross'] or ram['r'] > RM:
            continue
        ch = chosen(row)
        ne = None
        for e in row['near']:
            if e[0] == ram['mid']:
                ne = e
        pre = bool(ne and ne[15] and not ne[14])
        K['rams on ours with a row'] += 1
        if pre:
            K['switches pre-empt at the last turn'] += 1
        if ch is None or row.get('dead') is not None:
            continue
        tr = row['tn']
        eat = ch[1]
        free = any(not o[5] for o in row['opt'])
        keep = free and not eat and ((tr and ch[5]) or (not tr and ch[5] and not ch[4]))
        if keep:
            K['keep-out avoids'] += 1
            if pre:
                K['keep-out avoids and switches pre-empt'] += 1
        cc = ocls(row, ch)
        if cc >= 3 and not ch[5]:
            why = 'rammer not in view' if not ne or not ne[4] else 'rammer shows fewer parts than its length' if ne[5] < ne[1] else 'other'
            K['truly inside, unmarked: ' + why] += 1
        tag = None
        start = max([e[6] for e in row['near'] if e[1] <= 4] or [0])
        if cc >= 3 and start < 3 and tr and free and not eat and ch[5]:
            tag = 'trader walk-in'
        elif cc >= 3 and start < 3 and not tr and free and not eat and ch[5] and not ch[4]:
            tag = 'paid-ring walk-in'
        elif cc >= 3 and eat and ch[4]:
            tag = 'pearl beside a head'
        if tag and len(ex[tag, opp]) < EX and ne:
            ex[tag, opp].append('%d (%s) r%d: our %d at (%d,%d) steps to (%d,%d), own heads in view %d v %d; their %d at (%d,%d) rams it r%d in %d step(s)' % (
                gm['game'], opp, row['r'], row['L'], row['x'], row['y'], ch[0] % w, ch[0] // w, row['nA'] + 1, row['nE'], ne[1], ne[16], ne[17], ram['r'], ram['k']))
for k in sorted(K):
    print(k, K[k])
for opp in ('larp', 'Cutlery', 'aAah'):
    a = A[opp]
    g = a['games']
    print(opp, 'games', g, '| at r150: dragons %.1f v %.1f, total length %.1f v %.1f' % (a['n us'] / a['g150'], a['n them'] / a['g150'], a['len us'] / a['g150'], a['len them'] / a['g150']),
          '| head-ons a game r0-%d: by us %.1f by them %.1f' % (RM, a['rams by us'] / g, a['rams by them'] / g),
          '| length lost a game us %.1f them %.1f | regained us %.1f them %.1f | net us %.1f them %.1f' % (
              a['lost us'] / g, a['lost them'] / g, a['got us'] / g, a['got them'] / g, (a['lost us'] - a['got us']) / g, (a['lost them'] - a['got them']) / g))
for key in sorted(ex):
    for line in ex[key]:
        print(key[0], '|', line)
