"""Scratch (diag-toprams): the bot's own marks on paper. now = tiles one step from a visible head showing under 5 parts (what agg8 charges);
sst = tiles within max(1, parts - 1) steps of it (what SMALL_SPRINT_THREAT adds). Non-queen dragons of 2 to 4, rounds 0 to rmax.
1. How often a marked tile is chosen when an unmarked step is open. 2. Rules on paper: turns changed, rams avoided, own rams lost.
Usage: python3 tr_x.py <tags> [rmax] [examples]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
NAMES = {157: 'larp', 306: 'Cutlery', 454: 'aAah', 70: 'chad', 1119: 'ours'}
ME = 1119
tags = sys.argv[1].split(',')
RM = int(sys.argv[2]) if len(sys.argv) > 2 else 150
EX = int(sys.argv[3]) if len(sys.argv) > 3 else 0
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


def changed(row, rule, trader_key):
    """Would this turn's step be changed by the rule? Returns 0/1."""
    ch = chosen(row)
    if ch is None or row.get('dead') is not None:
        return 0
    tr = row[trader_key]
    eat = ch[1]
    if rule != 'trader, one-step marks' and not any(not o[5] for o in row['opt']):
        return 0
    if rule == 'sst':
        return int(not tr and not eat and ch[5] and not ch[4])
    if rule == 'sst+trader':
        return int(not eat and ((tr and ch[5]) or (not tr and ch[5] and not ch[4])))
    if rule == 'sst+trader+pearl':
        return int((tr and ch[5]) or (not tr and ch[5] and not ch[4]) or (not tr and eat and ch[5]))
    if rule == 'trader, one-step marks':
        return int(not eat and tr and ch[4] and any(not o[4] for o in row['opt']))
    if rule == 'trader only':
        return int(not eat and tr and ch[5])
    if rule == 'sst+trader, outnumbered or level':
        return int(row['nA'] + 1 - row['nE'] < 1 and not eat and ((tr and ch[5]) or (not tr and ch[5] and not ch[4])))
    return 0


RULES = ('sst', 'trader, one-step marks', 'trader only', 'sst+trader', 'sst+trader+pearl', 'sst+trader, outnumbered or level')
K = defaultdict(Counter)
ex = []
for gm in games:
    os_ = 0 if gm['a'] == ME else 1
    byid = defaultdict(dict)
    for row in gm['rows']:
        byid[row['id']][row['r']] = row
    for row in gm['rows']:
        if row.get('lite') or row['q'] or row['r'] > RM or row['L'] > 4:
            continue
        ch = chosen(row)
        hit = 'hit' in row and gm['rams'][row['hit']]['cross'] == 1 and gm['rams'][row['hit']]['r'] <= RM
        for c in cols_of(gm, row['s']):
            k = K[c]
            if ch is not None and row.get('dead') is None and not any(o[1] for o in row['opt']):
                for tk, tname in (('tn', 'agg8'),):
                    who = 'trader' if row[tk] else 'not trader'
                    has_now = any(o[4] for o in row['opt'])
                    has_sst = any(o[5] and not o[4] for o in row['opt'])
                    has_free = any(not o[5] for o in row['opt'])
                    if has_now and has_free:
                        k['1 %s: now-marked and unmarked open, no pearl beside' % who] += 1
                        if ch[4]:
                            k['1 %s: ... chose the now-marked' % who] += 1
                            if hit:
                                k['1 %s: ... chose the now-marked, rammed' % who] += 1
                    if has_sst and has_free:
                        k['1 %s: sst-only-marked and unmarked open, no pearl beside' % who] += 1
                        if ch[5] and not ch[4]:
                            k['1 %s: ... chose the sst-only-marked' % who] += 1
                            if hit:
                                k['1 %s: ... chose the sst-only-marked, rammed' % who] += 1
            for tk, tname in (('tn', 'agg8'), ('tw', 'live')):
                for rule in RULES:
                    if changed(row, rule, tk):
                        k['2 %s %s: turns changed' % (tname, rule)] += 1
                        if hit:
                            k['2 %s %s: rams avoided' % (tname, rule)] += 1
                        if ch[1]:
                            k['2 %s %s: pearl steps among them' % (tname, rule)] += 1
        if EX and row['s'] == os_ and hit and ch is not None and ch[4] and not row['tn'] and not ch[1] and any(not o[4] for o in row['opt']) and len(ex) < EX:
            ram = gm['rams'][row['hit']]
            ex.append((gm['game'], NAMES.get(gm['b'] if os_ == 0 else gm['a']), 'r', row['r'], 'our', row['L'], (row['x'], row['y']), 'to', (ch[0] % gm['w'], ch[0] // gm['w']),
                       'nA', row['nA'], 'nE', row['nE'], 'dp', row['dp'], 'opts[pearl,dp,now,sst]', [(o[0] % gm['w'], o[0] // gm['w'], o[1], o[2], o[4], o[5]) for o in row['opt']],
                       'near[L,d,parts]', [(e[1], e[3], e[5], e[16], e[17]) for e in row['near']], 'rammer', ram['L0'], (ram['sx'], ram['sy']), 'k', ram['k'], 'r', ram['r']))
    for ri, ram in enumerate(gm['rams']):
        if not ram['cross'] or ram['r'] > RM or ram['mq'] or ram['L0'] > 4:
            continue
        prev = byid.get(ram['mid'], {}).get(ram['r'] - 1)
        for c in cols_of(gm, ram['ms']):
            k = K[c]
            k['3 own rams (non-queen 2-4 attacker)'] += 1
            if prev is None or prev.get('lite'):
                k['3 own rams: no contact row the turn before'] += 1
                continue
            for tk, tname in (('tn', 'agg8'), ('tw', 'live')):
                for rule in RULES:
                    if changed(prev, rule, tk):
                        k['3 %s %s: own rams whose turn before is changed' % (tname, rule)] += 1
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
for e in ex:
    print(e)
