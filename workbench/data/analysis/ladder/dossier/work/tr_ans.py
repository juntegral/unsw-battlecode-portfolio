"""Scratch (diag-toprams): the answer turn. A non-queen dragon of 2 to 4 starts its turn inside the free-plus-one-paid reach (class 3 or 4)
of an enemy head of 2 to 4 (the threat = the head with the highest class, then the nearest). What it could do, what it did, what followed.
Usage: python3 tr_ans.py <tags> [rmax]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
NAMES = {157: 'larp', 306: 'Cutlery', 454: 'aAah', 70: 'chad', 1119: 'ours'}
ME = 1119
tags = sys.argv[1].split(',')
RM = int(sys.argv[2]) if len(sys.argv) > 2 else 150
games = []
for tag in tags:
    for line in Path(W + 'tr_scan-' + tag + '.jsonl').read_text().splitlines():
        if line.strip():
            games.append(json.loads(line))
COLS = [(opp, who) for opp in (157, 306, 454, 0) for who in ('us', 'them')]


def cols_of(gm, s):
    os_ = 0 if gm['a'] == ME else 1
    opp = gm['b'] if os_ == 0 else gm['a']
    return [(opp, 'us' if s == os_ else 'them'), (0, 'us' if s == os_ else 'them')]


def head(c):
    return ('ours v ' + NAMES.get(c[0], 'all')) if c[1] == 'us' else (NAMES.get(c[0], 'all') + ' v ours')


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


K = defaultdict(Counter)
for gm in games:
    for row in gm['rows']:
        if row.get('lite') or row['q'] or row['r'] > RM or row['L'] > 4:
            continue
        thr = [e for e in row['near'] if e[1] <= 4 and e[6] >= 3]
        if not thr:
            continue
        thr.sort(key=lambda e: (-e[6], e[3]))
        e = thr[0]
        hit = 'hit' in row and gm['rams'][row['hit']]['cross'] == 1 and gm['rams'][row['hit']]['r'] <= RM
        byit = hit and gm['rams'][row['hit']]['mid'] in [x[0] for x in thr]
        edge = row['nA'] + 1 - row['nE']
        ek = 'ahead in view' if edge >= 1 else 'level' if edge == 0 else 'behind by 1' if edge == -1 else 'behind by 2+'
        can_eng = any(x[8] for x in thr)
        can_plain = any(x[9] for x in thr)
        can_now = any(x[14] for x in thr)
        can_new = any(x[15] for x in thr)
        anyreach = any(x[9] or x[10] for x in row['near'] if x[1] <= 4)
        safe = [o for o in row['opt'] if ocls(row, o) < 3]
        dead = row.get('dead')
        ch = chosen(row)
        if dead == 3:
            did = 'rammed'
        elif dead is not None:
            did = 'died otherwise'
        elif ch is None:
            did = 'no step'
        elif ocls(row, ch) >= 3:
            did = 'stayed inside'
        else:
            did = 'stepped out'
        for c in cols_of(gm, row['s']):
            k = K[c]
            k['answer turns'] += 1
            k['a did: ' + did] += 1
            if hit:
                k['a hit before next turn'] += 1
                k['a did: ' + did + ' -> hit'] += 1
            cell = ('can ram a threat (plain reach)' if can_plain else 'can ram only over a pearl' if can_eng else 'cannot ram') + ' / ' + ('step out open' if safe else 'no step out')
            k['b ' + cell] += 1
            k['b ' + cell + ' : ' + did] += 1
            if hit:
                k['b ' + cell + ' : ' + did + ' -> hit'] += 1
            if can_plain or can_eng:
                k['c can ram, ' + ek] += 1
                k['c can ram, ' + ek + ' : ' + did] += 1
                if hit:
                    k['c can ram, ' + ek + ' : hit'] += 1
                if can_now:
                    k['d now-rule says ram'] += 1
                    if did == 'rammed':
                        k['d now-rule says ram: rammed'] += 1
                if can_new and not can_now:
                    k['d switches add'] += 1
                    k['d switches add: ' + did] += 1
                    if hit:
                        k['d switches add: hit'] += 1
                if not can_new and not can_now:
                    k['d switches still no, ' + ek] += 1
                    if hit:
                        k['d switches still no, ' + ek + ' : hit'] += 1
                    if did != 'rammed' and not safe:
                        k['e cornered (no step out, can ram, rules say no)'] += 1
                        if hit:
                            k['e cornered: hit'] += 1
                    if did != 'rammed' and safe:
                        k['e could leave (step out open, can ram, rules say no)'] += 1
                        k['e could leave: ' + did] += 1
                        if hit:
                            k['e could leave: hit'] += 1
                            k['e could leave: ' + did + ' -> hit'] += 1
keys = []
for c in COLS:
    for x in K[c]:
        if x not in keys:
            keys.append(x)
keys.sort()
print('rmax', RM)
print('| row | ' + ' | '.join(head(c) for c in COLS) + ' |')
for x in keys:
    print('| ' + x + ' | ' + ' | '.join(str(K[c].get(x, 0)) for c in COLS) + ' |')
