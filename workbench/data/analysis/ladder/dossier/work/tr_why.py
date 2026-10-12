"""Scratch (diag-toprams): every turn of a non-queen dragon of 2 to 4 (rounds 0 to rmax) by how it stood to enemy heads of 2 to 4,
and the rams that followed before its next turn. kind: answer = started inside free-plus-one-paid reach (class 3, 4) of a 2-4 head;
walk-in = started outside, its step ended inside; outside = step ended outside. Marks are the bot's own (visible parts).
Usage: python3 tr_why.py <tags> [rmax] [who]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
ME = 1119
tags = sys.argv[1].split(',')
RM = int(sys.argv[2]) if len(sys.argv) > 2 else 150
WHO = sys.argv[3] if len(sys.argv) > 3 else 'us'
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


N = Counter()
H = Counter()
tot = Counter()
for gm in games:
    os_ = 0 if gm['a'] == ME else 1
    want = os_ if WHO == 'us' else 1 - os_
    if WHO.isdigit():
        if int(WHO) not in (gm['a'], gm['b']):
            continue
        want = 0 if gm['a'] == int(WHO) else 1
    if len(sys.argv) > 4 and int(sys.argv[4]) not in (gm['a'], gm['b']):
        continue
    tot['games'] += 1
    for z in gm['turns']:
        if z[0] == want and z[1] <= 1:
            tot['all turns'] += z[4]
    for ram in gm['rams']:
        if ram['cross'] and ram['r'] <= RM:
            tot['rammed' if ram['ms'] != want else 'rams started'] += 1
    seen = set()
    for row in gm['rows']:
        if row['s'] != want or row['q'] or row['r'] > RM or row['L'] > 4:
            continue
        hit = 'hit' in row and gm['rams'][row['hit']]['cross'] == 1 and gm['rams'][row['hit']]['r'] <= RM
        if hit:
            seen.add(row['hit'])
        if row.get('lite'):
            key = ('lite',)
        else:
            start = max([e[6] for e in row['near'] if e[1] <= 4] or [0])
            dead = row.get('dead')
            ch = chosen(row)
            if dead == 3:
                key = ('it rammed',)
            elif dead is not None:
                key = ('died otherwise',)
            elif ch is None:
                key = ('answer' if start >= 3 else 'not inside', 'no step')
            else:
                cc = ocls(row, ch)
                safe = any(ocls(row, o) < 3 for o in row['opt'])
                who = 'trader' if row['tn'] else 'eating' if ch[1] else 'neither'
                mark = 'now-marked' if ch[4] else 'sst-marked' if ch[5] else 'unmarked'
                free = 'unmarked open' if any(not o[5] for o in row['opt']) else 'all marked'
                if cc >= 3:
                    key = ('answer: stayed' if start >= 3 else 'walk-in', who, mark, free if mark != 'unmarked' else ('safe open' if safe else 'no safe'))
                elif start >= 3:
                    key = ('answer: stepped out',)
                else:
                    key = ('outside', 'pearl-only reach' if cc == 1 else 'two paid' if cc == 2 else 'clear')
        N[key] += 1
        tot['turns'] += 1
        if hit:
            H[key] += 1
            tot['hit'] += 1
    for ri, ram in enumerate(gm['rams']):
        if ram['cross'] and ram['r'] <= RM and ram['Lv'] <= 4 and not ram['vq'] and 1 - ram['ms'] == want:
            tot['rams'] += 1
            if ri not in seen:
                tot['rams without a row'] += 1
print(WHO, 'rmax', RM, dict(tot))
agg = Counter()
aggh = Counter()
for key in sorted(N):
    print('%-70s turns %5d  rammed %4d  %.2f' % (' / '.join(key), N[key], H[key], H[key] / N[key]))
    agg[key[0]] += N[key]
    aggh[key[0]] += H[key]
    if key[0] in ('walk-in', 'answer: stayed'):
        agg[key[0] + ' ' + key[1]] += N[key]
        aggh[key[0] + ' ' + key[1]] += H[key]
        agg[key[0] + ' ' + key[2]] += N[key]
        aggh[key[0] + ' ' + key[2]] += H[key]
print('--')
for key in sorted(agg):
    print('%-40s turns %5d  rammed %4d  %.2f' % (key, agg[key], aggh[key], aggh[key] / agg[key]))
