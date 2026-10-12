"""late-opus extras: direct cost of late wait splits, lead-loss deaths split by her length at death."""
import sys, json, os
sys.dont_write_bytecode = True
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from collections import Counter

G = json.load(open('data.json'))['games']


def at(g, arr, r):
    i = r - (g['last'] - len(arr) + 1)
    return arr[i] if 0 <= i < len(arr) else None


def ws(t):
    return t['sp'] == 1 and t.get('mv') == 0 and t.get('La') == t['L'] - 2


print('== games where our queen lived to the end and we lost: cells lost to wait splits from 10+ at r100+ against the final gap')
n = 0
for g in G:
    lost = sum(2 for t in g['turns'] if ws(t) and t['L'] >= 10 and t['r'] >= 100)
    lost300 = sum(2 for t in g['turns'] if ws(t) and t['L'] >= 10 and t['r'] >= 300)
    if lost and g['qfin'] > 0:
        gapf = g['efin'] - g['qfin']
        flip = (not g['win']) and g['qfin'] + lost > g['efin']
        n += flip
        print(' ', g['id'], g['ver'], g['src'], 'win', g['win'], 'qfin', g['qfin'], 'efin', g['efin'], 'lost to wait splits', lost, '(r300+ %d)' % lost300,
              'WOULD FLIP' if flip else '')
print('games that the lost cells alone would flip:', n)

g = [x for x in G if x['id'] == 1530577][0]
print('\n== 1530577', g['ver'], g['src'], g['map'], 'opp', g['opp'], 'win', g['win'], 'qfin', g['qfin'], 'efin', g['efin'], 'our dragons at end', g['n_fin'], 'theirs', g['en_fin'])
for t in g['turns']:
    if t['r'] >= 460:
        print('  r', t['r'], 'L', t['L'], '->', t.get('La'), 'split' if t['sp'] else 'move', 'free', t['f'], 'their queen', t['eq'], 'nearest visible foe gap', t['ng'], 'len', t['nl'])

print('\n== losses from a queen lead at r350, by her length at death')
c = Counter()
for g in G:
    q, e = at(g, g['ql'], 350), at(g, g['el'], 350)
    if q is None or not q > e or g['win']:
        continue
    dl = [d for d in g['deaths'] if d['r'] >= 350]
    if not dl:
        c['alive overtaken'] += 1
        continue
    d = dl[0]
    band = 'died at 2-6' if d['L'] <= 6 else 'died at 7+'
    c[band] += 1
    c[band, d['cause']] += 1
    c[band, 'still longer than their queen at death'] += int(d['L'] > d['eq'])
    c[band, 'mates within 5: 0'] += int(d['mates5'] == 0)
    c[band, 'attacker in her own 7x7 at her last turn'] += int(d.get('qview', 0) == 1)
    tw = sum(1 for t in d['last3'] if t.get('tw') == 1)
    aw = sum(1 for t in d['last3'] if t.get('tw') == -1)
    c[band, 'last3 ' + ('toward' if tw > aw else 'away' if aw > tw else 'level/none')] += 1
    wsn = sum(1 for t in g['turns'] if ws(t) and t['L'] >= 10 and d['r'] - 20 <= t['r'] <= d['r'])
    c[band, 'wait split from 10+ in her last 20 rounds'] += int(wsn > 0)
    shed = [t for t in g['turns'] if t['sp'] and t['r'] >= 350 and t['L'] >= 10 and t.get('La', 99) <= 3]
    c[band, 'shed 10+ -> 2/3 after r350'] += int(bool(shed))
    if d['cause'].startswith('ram'):
        c[band, 'attacker steps %d' % d['att_steps']] += 1
        c[band, 'attacker length <=6'] += int(d['attL'] <= 6)
for k in sorted(c, key=str):
    print('  ', k, c[k])

print('\n== all deaths r350+ while longer than their queen: attacker steps and length (rams only)')
c = Counter()
for g in G:
    for d in g['deaths']:
        if d['r'] >= 350 and d['L'] > d['eq'] and d['cause'].startswith('ram'):
            c['steps', d['att_steps']] += 1
            c['attL', '<=4' if d['attL'] <= 4 else '5-8' if d['attL'] <= 8 else '9+'] += 1
            c['her L', '2-6' if d['L'] <= 6 else '7+'] += 1
for k in sorted(c, key=str):
    print('  ', k, c[k])
