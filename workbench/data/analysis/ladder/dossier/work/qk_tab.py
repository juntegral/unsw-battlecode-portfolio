"""Scratch (diag-queenkill): the rows of the report tables, from qk_scanf-*.jsonl. Usage: python3 qk_tab.py"""
import json
from collections import Counter
from pathlib import Path
from statistics import median, mean

W = 'data/analysis/ladder/dossier/work/'
GROUPS = (('online', ('m1', 'sr51'), 'ours', 'the two opponents'), ('ladder', ('L0', 'L1', 'L2'), 'ours', 'ladder opponents'),
          ('rank-1', ('T0', 'T1', 'T2'), 'rank-1', 'its opponents'))


def load(tags):
    games = []
    for tag in tags:
        for line in Path(W + 'qk_scanf-' + tag + '.jsonl').read_text().splitlines():
            if line.strip():
                games.append(json.loads(line))
    return games


def fate(q):
    if q is None:
        return 'alive'
    c = q['cause']
    if c == 'rammed':
        return 'ram' if q['enemy'] else 'own side'
    if c == 'she rammed':
        return 'she rammed' if q['enemy'] else 'own side'
    if c == 'another body':
        return 'enemy body' if q.get('enemy') == 1 else 'own side'
    if c in ('wall', 'own body'):
        return c
    return 'split or none'


def sh(values, cuts):
    n = len(values)
    return '; '.join('%.2f' % (sum(1 for v in values if lo <= v <= hi) / n) for lo, hi in cuts) if n else '-'


def first_dead(g):
    a, b = g['qd']
    if a is None and b is None:
        return None
    if a is None:
        return 1
    if b is None:
        return 0
    if a['r'] != b['r']:
        return 0 if a['r'] < b['r'] else 1
    return 0 if a['oq'] > 0 else 1


def by_enemy(q):
    return fate(q) in ('ram', 'she rammed', 'enemy body')


def won(g, s):
    return g['win'] == (1 if s == 0 else 0)


def core(r):
    return not r[4] and r[3] <= 4 and r[16] == 0 and r[9] > 0


def sure(r, cap):
    return not r[4] and r[3] <= cap and r[16] == 0 and r[9] > 0 and r[6] <= 3 and r[17] <= r[6] and not (r[5] and r[3] >= 5)


def flip_class(g, s):
    f = g['final']
    own_q, own_big, her, their_big = (f[3], f[1], f[7], f[5]) if s == 0 else (f[7], f[5], f[3], f[1])
    if won(g, s):
        return 'won'
    if her == 0:
        return 'lost, she died anyway'
    if g['decided'] != 'queen':
        return 'lost on another rule'
    if own_q > 0 or own_big > their_big:
        return 'FLIP'
    return 'open' if their_big == her else 'lost, their longest ahead'


data = [(name, load(tags), a, b) for name, tags, a, b in GROUPS]
m1 = [g for g in data[0][1] if g['label'] == 'agg7-m1']
print('games', [(name, len(gs)) for name, gs, a, b in data], 'm1', len(m1), 'm1 wins', sum(1 for g in m1 if g['win'] == 1),
      'm1 decided on queen length', sum(1 for g in m1 if g['decided'] == 'queen'), 'm1 our queen alive at the end', sum(1 for g in m1 if g['final'][3] > 0))

print('\nFATE | queen of | games | alive at the end | dead by r100; r101-300; later | rammed by an enemy head | she rammed an enemy head | wall; own body | own side body or head | enemy body | illegal split or no action |')
for name, games, a, b in data:
    for s, who in ((0, a), (1, b)):
        qs = [g['qd'][s] for g in games]
        c = Counter(fate(q) for q in qs)
        t = Counter('a' if q is None else 0 if q['r'] <= 100 else 1 if q['r'] <= 300 else 2 for q in qs)
        print('| %s, %s | %d | %d | %d; %d; %d | %d | %d | %d; %d | %d | %d | %d |' % (name, who, len(qs), c['alive'], t[0], t[1], t[2], c['ram'], c['she rammed'],
                                                                                 c['wall'], c['own body'], c['own side'], c['enemy body'], c['split or none']))

print('\nKILLER | queen rammed | n | killer length 2; 3; 4; 5-8; 9+ | steps it walked 1; 2; 3; 4+ | paid a segment before the hit | pearl on the way | in her 7x7 at her last turn | none of her side within 5 | her length 2; 3; 4+ | killer, her length (mean) | by r100; r101-300; later |')
for name, games, a, b in data:
    for s, who in ((0, a), (1, b)):
        rams = [g['qd'][s] for g in games if g['qd'][s] is not None and fate(g['qd'][s]) == 'ram']
        n = len(rams)
        print('| %s, %s | %d | %s | %s | %.2f | %.2f | %.2f | %.2f | %s | %.1f, %.1f | %s | killer is a queen %d, killer 5+ and its side longest %d' % (
            name, who, n, sh([q['kL0'] for q in rams], ((2, 2), (3, 3), (4, 4), (5, 8), (9, 999))), sh([q['k'] for q in rams], ((1, 1), (2, 2), (3, 3), (4, 99))),
            sum(1 for q in rams if q['paid'] > 0) / n, sum(1 for q in rams if q['ate'] > 0) / n, sum(1 for q in rams if q['seen'] >= 0) / n,
            sum(1 for q in rams if q['own5'] == 0) / n, sh([q['L'] for q in rams], ((2, 2), (3, 3), (4, 999))), mean(q['kL0'] for q in rams), mean(q['L'] for q in rams),
            sh([q['r'] for q in rams], ((0, 100), (101, 300), (301, 999))), sum(q['kq'] for q in rams), sum(1 for q in rams if q['ktop'] and q['kL0'] >= 5)))

print('\nFIRST AND WORTH')
for name, games, a, b in data:
    for s, who in ((0, a), (1, b)):
        o = 1 - s
        ks = [g for g in games if first_dead(g) == o and by_enemy(g['qd'][o])]
        out = [g for g in games if first_dead(g) == o]
        rams = [g for g in games if g['qd'][o] is not None and fate(g['qd'][o]) == 'ram']
        al = [g for g in rams if g['qd'][o]['oq'] > 0]
        de = [g for g in rams if g['qd'][o]['oq'] == 0]
        still = [g for g in al if g['final'][3 if s == 0 else 7] > 0]
        no = [g for g in games if g not in rams]
        w = lambda gs: '%d of %d' % (sum(1 for g in gs if won(g, s)), len(gs))
        print('%s, %s: kills the other queen first in %d of %d games, then wins %s (%.2f) | other queen dies first by any cause: wins %s | rams her dead in %d games: own queen alive then, wins %s (still alive at the end %s); own queen dead then, wins %s; no such kill, wins %s | killer length mean %.2f, her length mean %.2f' % (
            name, who, len(ks), len(games), w(ks), sum(1 for g in ks if won(g, s)) / max(1, len(ks)), w(out), len(rams), w(al), w(still), w(de), w(no),
            mean(g['qd'][o]['kL0'] for g in rams) if rams else 0, mean(g['qd'][o]['L'] for g in rams) if rams else 0))
    print('   end state (focus queen alive, other queen alive): focus wins', {k: '%d of %d' % (sum(1 for g in games if (g['final'][3] > 0, g['final'][7] > 0) == k and g['win'] == 1),
                                                                                        sum(1 for g in games if (g['final'][3] > 0, g['final'][7] > 0) == k)) for k in ((True, True), (True, False), (False, True), (False, False))})

print('\nCHANCES | side, at whose queen | all chance turns a game | short, plain, in view: turns, games, taken | free; 1 paid; 2 paid (taken/turns) | by own length 2; 3; 4 | 5 to 8 long within 3 steps | short, pearl needed, in view | refusers did |')
for name, games, a, b in data:
    n = len(games)
    for s, who in ((0, a), (1, b)):
        rows = [(g, r) for g in games for r in g['chs'] if r[1] == s]
        cr = [(g, r) for g, r in rows if core(r)]
        f = lambda sel: '%d/%d' % (sum(r[18] for g, r in sel), len(sel))
        paid = lambda k: [(g, r) for g, r in cr if max(0, r[6] - r[7]) == k]
        mid = [(g, r) for g, r in rows if sure(r, 8) and r[3] >= 5]
        pearl = [(g, r) for g, r in rows if not r[4] and r[3] <= 4 and r[16] > 0 and r[9] > 0]
        did = Counter()
        for g, r in cr:
            if not r[18]:
                did['split' if r[22] else 'died' if r[23] >= 0 else 'away' if r[20] > r[17] else 'closer' if r[20] < r[17] else 'level'] += 1
        print('| %s, %s | %.2f | %d, %d, %s (%.2f) | %s; %s; %s | %s; %s; %s | %s | %s | %s |' % (
            name, who, len(rows) / n, len(cr), len({g['game'] for g, r in cr}), f(cr), sum(r[18] for g, r in cr) / max(1, len(cr)), f(paid(0)), f(paid(1)), f(paid(2)),
            f([x for x in cr if x[1][3] == 2]), f([x for x in cr if x[1][3] == 3]), f([x for x in cr if x[1][3] == 4]), f(mid), f(pearl), dict(did.most_common())))
        if s == 0:
            for key, fn in (('own queen alive', lambda r: r[14] > 0), ('outnumbered in view', lambda r: r[10] + 1 - r[11] < 1), ('another short saw her within 20 rounds', lambda r: 0 <= r[31] <= 20),
                            ('she could hit back', lambda r: r[15] > 0), ('round over 300', lambda r: r[0] > 300), ('her length 5+', lambda r: r[8] >= 5)):
                yes = [x for x in cr if fn(x[1])]
                no = [x for x in cr if not fn(x[1])]
                print('      %s: yes %s, no %s' % (key, f(yes), f(no)))

print('\nFUNNEL | side, looking at whose queen | games she is ever seen | first seen (median round) | short sighting turns a game | walk 1-3, out of reach: turns a game, closer; farther | walk 4-6: turns a game, closer; farther | in reach: turns a game, rammed | long dragons in reach: turns a game, rammed | first sighting to killing ram (median rounds) |')
for name, games, a, b in data:
    n = len(games)
    for s, who in ((0, a), (1, b)):
        c = Counter()
        for g in games:
            for x in g['fun']:
                if x[0] == s:
                    cl = 'short' if x[1] <= 4 else 'long'
                    c[(cl, x[2], x[5])] += x[6]
                    c[(cl, x[2], 'all')] += x[6]
                    c[(cl, 'all')] += x[6]
        seen = [g['first_seen'][s] for g in games if g['first_seen'][s] >= 0]
        lat = [g['qd'][1 - s]['r'] - g['first_seen'][s] for g in games if g['qd'][1 - s] is not None and fate(g['qd'][1 - s]) == 'ram' and g['first_seen'][s] >= 0]
        p = lambda cl, db, o: c[(cl, db, o)] / max(1, c[(cl, db, 'all')])
        print('| %s, %s | %d of %d | %s | %.1f | %.2f, %.2f; %.2f | %.2f, %.2f; %.2f | %.2f, %.2f | %.2f, %.2f | %s |' % (
            name, who, len(seen), n, median(seen) if seen else '-', c[('short', 'all')] / n, c[('short', 'N', 'all')] / n, p('short', 'N', 'C'), p('short', 'N', 'F'),
            c[('short', 'M', 'all')] / n, p('short', 'M', 'C'), p('short', 'M', 'F'), c[('short', 'R', 'all')] / n, p('short', 'R', 'T'),
            c[('long', 'R', 'all')] / n, p('long', 'R', 'T'), median(lat) if lat else '-'))

print('\nSWITCH (non-queen, not its side longest when 5+, her head in its 7x7, free way of at most 3 steps inside sprint reach, no portal)')
for name, games, a, b in data:
    for s, who in ((0, a), (1, b)):
        for cap in (4, 8):
            took = 0
            per = {}
            rows = []
            for g in games:
                for r in g['chs']:
                    if r[1] == s and sure(r, cap):
                        if r[18]:
                            took += 1
                        else:
                            per.setdefault(g['game'], g)
                            rows.append((g, r))
            fc = Counter(flip_class(g, s) for g in per.values())
            print('%s, %s, length at most %d: taken %d, refused %d turns in %d games (%.2f taken); own queen alive at the turn %d, dead %d; her length mean %.1f | games: %s' % (
                name, who, cap, took, len(rows), len(per), took / max(1, took + len(rows)), sum(1 for g, r in rows if r[14] > 0), sum(1 for g, r in rows if r[14] == 0),
                mean(r[8] for g, r in rows) if rows else 0, dict(fc.most_common())))
            if s == 0 and cap == 8:
                for g in per.values():
                    if flip_class(g, s) in ('FLIP', 'open'):
                        print('      ', g['game'], g['map'], g['cells'], flip_class(g, s), 'final', g['final'], [(r[0], r[3], r[6], r[8], r[14]) for gg, r in rows if gg is g][:5])
    if name != 'rank-1':
        c = Counter()
        for g in games:
            for r in g['chs']:
                if r[1] != 0 or not sure(r, 8) or r[18]:
                    continue
                if r[3] <= 4:
                    lead = r[5] and r[0] > (150 if g['cells'] > 1200 else 300)
                    why = ('longest of its side after the switch round' if lead else 'round 20 or earlier' if r[0] <= 20 else
                           'our queen dead and round 100 or later (revenge should fire)' if r[14] == 0 and r[0] >= 100 else
                           ('another short saw her within 20 rounds' if 0 <= r[31] <= 20 else 'no other short saw her') +
                           ('; outnumbered in view' if r[10] + 1 - r[11] < 1 else '; her parts under own length' if r[9] < r[3] else '; trade allowed?'))
                    c[('2-4', why)] += 1
                else:
                    c[('5-8', ('after round 300' if r[0] > 300 else 'round 300 or earlier') + ('; her parts 10+' if r[9] >= 10 else '; her parts 6-9' if r[9] >= 6 else '; her parts under 6'))] += 1
        for k, v in sorted(c.items(), key=lambda kv: (kv[0][0], -kv[1])):
            print('      refusal by fitting clause', name, k, v)
