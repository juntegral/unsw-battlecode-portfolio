"""Scratch (diag-toprams): the cost side. Every turn of a non-queen dragon of 2 to 4 (rounds 0 to rmax) with an enemy head of 2 to 4
within 3 steps at its turn start: where its step ended (class at decision, over heads of 2 to 4), whether a step outside was open,
whether it was rammed before its next turn; then keep-away rules on paper. Usage: python3 tr_rules.py <tags> [rmax]"""
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
    who = 'us' if s == os_ else 'them'
    return [(opp, who), (0, who)]


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
G = Counter()
for gm in games:
    for s in (0, 1):
        for c in cols_of(gm, s):
            G[c] += 1
    for row in gm['rows']:
        if row.get('lite') or row['q'] or row['r'] > RM or row['L'] > 4:
            continue
        hit = 'hit' in row and gm['rams'][row['hit']]['cross'] == 1 and gm['rams'][row['hit']]['r'] <= RM
        hs = hit and gm['rams'][row['hit']]['L0'] <= 4
        small = [e for e in row['near'] if e[1] <= 4]
        d3 = [e for e in small if e[3] <= 3]
        for c in cols_of(gm, row['s']):
            k = K[c]
            k['rows'] += 1
            if hit:
                k['rows hit'] += 1
            if not d3:
                if hit:
                    k['hit without a 2-4 head within 3 at start'] += 1
                continue
            k['contact turns'] += 1
            if hit:
                k['contact hit'] += 1
            dead = row.get('dead')
            if dead == 3:
                k['contact: it rammed'] += 1
                continue
            if dead is not None:
                k['contact: died otherwise'] += 1
                continue
            ch = chosen(row)
            if ch is None:
                k['contact: no step'] += 1
                if hit:
                    k['contact: no step hit'] += 1
                continue
            cc = ocls(row, ch)
            cl = [ocls(row, o) for o in row['opt']]
            k['cls%d' % cc] += 1
            if hit:
                k['cls%d hit' % cc] += 1
            out = row['nA'] + 1 - row['nE'] < 1
            tn = row['tn']
            eat = ch[1]
            # rule Z2: never end inside free reach plus one paid step of a 2-4 head when a step outside is open
            for name, lim in (('Z2', 3), ('Z1', 4)):
                if cc >= lim:
                    safe = [o for o, x in zip(row['opt'], cl) if x < lim]
                    k[name + ' in'] += 1
                    if hit:
                        k[name + ' in hit'] += 1
                    if safe:
                        k[name + ' touched'] += 1
                        if hit:
                            k[name + ' avoided'] += 1
                        if eat and not any(o[1] for o in safe):
                            k[name + ' touched: pearl given up'] += 1
                            if hit:
                                k[name + ' avoided: pearl given up'] += 1
                        if not eat:
                            k[name + ' touched, not eating'] += 1
                            if hit:
                                k[name + ' avoided, not eating'] += 1
                            best = min((o[2] if o[2] >= 0 else 9) for o in safe)
                            cur = ch[2] if ch[2] >= 0 else 9
                            if best > cur:
                                k[name + ' touched, not eating: pearl farther'] += 1
                        if out:
                            k[name + ' touched, outnumbered or level'] += 1
                            if hit:
                                k[name + ' avoided, outnumbered or level'] += 1
                            if not eat:
                                k[name + ' touched, outnumbered or level, not eating'] += 1
                                if hit:
                                    k[name + ' avoided, outnumbered or level, not eating'] += 1
                        if tn:
                            k[name + ' touched, trader'] += 1
                            if hit:
                                k[name + ' avoided, trader'] += 1
                        else:
                            k[name + ' touched, not trader'] += 1
                            if hit:
                                k[name + ' avoided, not trader'] += 1
                            if not eat:
                                k[name + ' touched, not trader, not eating'] += 1
                                if hit:
                                    k[name + ' avoided, not trader, not eating'] += 1
            # the bot's marks: now = one step from a visible head showing under 5 parts; sst = max(1, parts - 1) steps
            if ch[4]:
                k['now-mark chosen'] += 1
                if hit:
                    k['now-mark chosen hit'] += 1
                if any(not o[4] for o in row['opt']):
                    k['now-mark chosen, unmarked open'] += 1
                    k['now-mark chosen, unmarked open: %s' % ('trader' if tn else 'eating' if eat else 'neither')] += 1
                    if hit:
                        k['now-mark chosen, unmarked open: %s hit' % ('trader' if tn else 'eating' if eat else 'neither')] += 1
            if ch[5] and not ch[4]:
                k['sst-mark chosen'] += 1
                if hit:
                    k['sst-mark chosen hit'] += 1
                if any(not o[5] for o in row['opt']):
                    tagk = 'trader' if tn else 'eating' if eat else 'neither'
                    k['sst-mark chosen, unmarked open'] += 1
                    k['sst-mark chosen, unmarked open: ' + tagk] += 1
                    if hit:
                        k['sst-mark chosen, unmarked open hit'] += 1
                        k['sst-mark chosen, unmarked open: ' + tagk + ' hit'] += 1
                    if row['tw'] and not tn:
                        k['sst-mark chosen, unmarked open: trader only with short-by-1'] += 1
            # trader walking at its target
            if tn:
                k['trader turns'] += 1
                if hit:
                    k['trader turns hit'] += 1
                if cc >= 3:
                    k['trader ends in free+1'] += 1
                    if hit:
                        k['trader ends in free+1 hit'] += 1
            else:
                k['non-trader turns'] += 1
                if hit:
                    k['non-trader turns hit'] += 1

keys = []
for c in COLS:
    for x in K[c]:
        if x not in keys:
            keys.append(x)
keys.sort()
print('rmax', RM, 'games', {head(c): G[c] for c in COLS})
print('| row | ' + ' | '.join(head(c) for c in COLS) + ' |')
for x in keys:
    print('| ' + x + ' | ' + ' | '.join(str(K[c].get(x, 0)) for c in COLS) + ' |')
