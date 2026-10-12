"""Scratch (diag-toprams): meetings of two non-queen dragons of 2 to 4 within 3 steps (rounds 0 to rmax), from tr_scan-*.jsonl.
Also: for every ram on a short dragon, whether the victim could have rammed that head first on its last turn. Usage: python3 tr_meet.py <tags> [rmax]"""
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
OPPS = (157, 306, 454, 0)
K = defaultdict(Counter)
G = Counter()
for gm in games:
    os_ = 0 if gm['a'] == ME else 1
    opp = gm['b'] if os_ == 0 else gm['a']
    for c in (opp, 0):
        G[c] += 1
    rowof = {}
    for row in gm['rows']:
        if 'hit' in row:
            rowof[row['hit']] = row
    for m in gm['meets']:
        if m['r0'] > RM or m['q'][0] or m['q'][1]:
            continue
        for c in (opp, 0):
            k = K[c]
            k['meetings'] += 1
            Lu, Lt = m['L0'][os_], m['L0'][1 - os_]
            pair = 'ours %d v their %d' % (Lu, Lt)
            k['closed to 3 steps by: ' + ('ours' if m['by'] == os_ else 'theirs')] += 1
            f = m['first']
            if f is None:
                fk = 'never in reach'
            else:
                mover = 'ours' if f[1] == os_ else 'theirs'
                eu, et = (f[2], f[3]) if os_ == 0 else (f[3], f[2])
                who = 'both exposed' if eu and et else 'ours exposed' if eu else 'theirs exposed'
                fk = mover + ' moved, ' + who
            k['first in reach: ' + fk] += 1
            end = m['end']
            if end == 'ram':
                ek = 'ours rammed theirs' if m['who'] == os_ else 'theirs rammed ours'
            elif end == 'ram3':
                ek = 'ours rammed by another' if m['who'] == os_ else 'theirs rammed by another'
            elif end == 'out':
                ek = 'ours died ramming another' if m['who'] == os_ else 'theirs died ramming another'
            elif end == 'die':
                ek = 'ours died otherwise' if m['who'] == os_ else 'theirs died otherwise'
            else:
                ek = end
            k['end: ' + ek] += 1
            k['first x end: ' + fk + ' -> ' + ek] += 1
            k['pair: ' + pair] += 1
            k['pair x end: ' + pair + ' -> ' + ek] += 1
            if end == 'ram':
                ram = gm['rams'][m['ri']]
                side = 'ours' if m['who'] == os_ else 'theirs'
                k['ram by ' + side + ': attacker length sum'] += ram['L0']
                k['ram by ' + side + ': victim length sum'] += ram['Lv']
                k['ram by ' + side + ': attacker side regained'] += ram['mm'] + ram['vm']
                k['ram by ' + side + ': victim side regained'] += ram['mv'] + ram['vv']
                k['ram by ' + side + ': n'] += 1
            # the rules on paper, our side
            for who, s in (('ours', os_), ('theirs', 1 - os_)):
                ts = m['ts'][s]
                if ts[1]:
                    k[who + ': had a turn with the other head in engine reach'] += 1
                    k[who + ': had engine reach -> ' + ek] += 1
                if m['fo'][s] >= 0:
                    k[who + ': now-rule says ram at some turn'] += 1
                    k[who + ': now-rule yes -> ' + ek] += 1
                if m['fn'][s] >= 0:
                    k[who + ': switches add a ram turn'] += 1
                    k[who + ': switches add -> ' + ek] += 1
                    if m['fo'][s] < 0 or m['fn'][s] < m['fo'][s]:
                        k[who + ': switches add a ram turn before any now-rule turn'] += 1
                        k[who + ': switches first -> ' + ek] += 1
                        k[who + ': switches first, pair ' + pair + ' -> ' + ek] += 1
    # rams on short non-queen victims: could the victim have rammed that head first on its last turn
    for ri, ram in enumerate(gm['rams']):
        if not ram['cross'] or ram['r'] > RM or ram['Lv'] > 4 or ram['vq']:
            continue
        vs = 1 - ram['ms']
        who = 'on ours' if vs == os_ else 'on theirs'
        row = rowof.get(ri)
        for c in (opp, 0):
            k = K[c]
            k['rams ' + who] += 1
            if row is None or row.get('lite'):
                k['rams ' + who + ': no last turn'] += 1
                continue
            ne = None
            for e in row['near']:
                if e[0] == ram['mid']:
                    ne = e
            if ne is None:
                k['rams ' + who + ': rammer not within 5 at last turn'] += 1
                continue
            if ne[8]:
                k['rams ' + who + ': victim had the rammer in engine reach'] += 1
            if ne[14]:
                k['rams ' + who + ': victim now-rule said ram'] += 1
            if ne[15]:
                k['rams ' + who + ': victim switches say ram'] += 1
                if not ne[14]:
                    k['rams ' + who + ': victim switches say ram, now-rule not'] += 1
                    k['rams ' + who + ': switches only, pair victim %d on rammer %d' % (row['L'], ne[1])] += 1
                    k['rams ' + who + ': switches only, %s' % ('pearl path' if not ne[9] else 'one shorter')] += 1
            if ne[8] and not ne[15]:
                why = 'queen' if row['q'] else 'outnumbered or level' if row['nA'] + 1 - row['nE'] < 1 else 'units' if not (ne[11] or ne[12] or ne[13]) and ne[5] >= row['L'] - 1 else 'parts under L-1' if ne[5] < row['L'] - 1 else 'reach (bot search)'
                k['rams ' + who + ': engine reach but switches say no: ' + why] += 1
keys = []
for c in OPPS:
    for x in K[c]:
        if x not in keys:
            keys.append(x)
keys.sort()
print('rmax', RM, 'games', dict(G))
print('| row | ' + ' | '.join(NAMES.get(c, 'all') for c in OPPS) + ' |')
for x in keys:
    print('| ' + x + ' | ' + ' | '.join(str(K[c].get(x, 0)) for c in OPPS) + ' |')
