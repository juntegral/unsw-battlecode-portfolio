# Scratch (diag-sacrifice): what the deaths by choice buy. One record per game and side with standings at rounds
# 100, 200 and 300, deaths by choice (no valid action with a free cell) by window and how many of them fall with
# the team at 60 dragons or more, natural pearls, splits and turns. Then the comparisons of job 2.
# Usage: python3 data/analysis/ladder/dossier/work/sc_buy.py
import sys, json
from collections import Counter, defaultdict
from statistics import median, mean
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
games = []
for n in range(4):
    for line in Path(W + 'sc_ev-%d.jsonl' % n).read_text().splitlines():
        if line:
            games.append(json.loads(line))


def win(r):
    return 0 if r <= 100 else 1 if r <= 200 else 2 if r <= 300 else 3


recs = []
for g in games:
    for s in 'ut':
        o = 0 if s == 'u' else 4
        st = {}
        for r in ('100', '150', '200', '250', '300'):
            v = g['series'].get(r)
            st[r] = None if v is None else dict(alive=v[o], longest=v[o + 1], total=v[o + 2], queen=v[o + 3],
                                               o_alive=v[4 - o], o_longest=v[5 - o], o_total=v[6 - o], o_queen=v[7 - o])
        free = [0, 0, 0]
        cap = [0, 0, 0]
        gave = [0, 0, 0]
        got = [0, 0, 0]
        boxed = [0, 0, 0]
        first = None
        for d in g['events']:
            if d['side'] != s or d['reason'] != 4 or d['r'] > 300:
                continue
            wn = win(d['r'])
            if d['free'] == 0:
                boxed[wn] += 1
                continue
            free[wn] += 1
            gave[wn] += d['L']
            got[wn] += sum(1 for p in d['p'] if p[0] == s)
            if d['n_side'] + 1 >= 60:
                cap[wn] += 1
            if first is None:
                first = d['r']
        recs.append(dict(game=g['game'], side=s, team='US' if s == 'u' else g['opponent'], rating=g['rating'],
                         layout=g['layout'], cells=g['cells'], last=g['last_round'],
                         won=int(g['result'] == ('win' if s == 'u' else 'loss')), st=st, free=free, cap=cap, gave=gave,
                         got=got, boxed=boxed, first=first, turns=g['turns'][s][:3], splits=g['splits'][s][:3],
                         nat=[g['eats'][s][k].get('n', 0) for k in range(3)],
                         alleat=[sum(g['eats'][s][k].values()) for k in range(3)]))


def med(xs):
    xs = [x for x in xs if x is not None]
    return '%.1f' % median(xs) if xs else '-'


def line(label, rs):
    out = ['%-34s n %3d won %3d' % (label, len(rs), sum(r['won'] for r in rs))]
    for r in ('100', '200', '300'):
        have = [x['st'][r] for x in rs if x['st'][r] is not None]
        out.append('r%s (n %d) q %s long %s alive %s total %s | other side q %s long %s alive %s total %s' % (
            r, len(have), med([h['queen'] for h in have]), med([h['longest'] for h in have]), med([h['alive'] for h in have]),
            med([h['total'] for h in have]), med([h['o_queen'] for h in have]), med([h['o_longest'] for h in have]),
            med([h['o_alive'] for h in have]), med([h['o_total'] for h in have])))
    t = [sum(x['turns'][k] for x in rs) for k in range(3)]
    out.append('per 1,000 turns w0/w1/w2: by choice %s | natural pearls %s | splits %s | given up per game %s, eaten back %s' % (
        '/'.join('%.2f' % (1000 * sum(x['free'][k] for x in rs) / max(t[k], 1)) for k in range(3)),
        '/'.join('%.1f' % (1000 * sum(x['nat'][k] for x in rs) / max(t[k], 1)) for k in range(3)),
        '/'.join('%.1f' % (1000 * sum(x['splits'][k] for x in rs) / max(t[k], 1)) for k in range(3)),
        '/'.join('%.1f' % (sum(x['gave'][k] for x in rs) / max(len(rs), 1)) for k in range(3)),
        '/'.join('%.1f' % (sum(x['got'][k] for x in rs) / max(len(rs), 1)) for k in range(3))))
    print('\n    '.join(out))


them = [r for r in recs if r['side'] == 't']
us = [r for r in recs if r['side'] == 'u']
print('1. Teams rated 2100 and above, their side (the other side is us)')
for name in ('chad gdp', 'Settlers of Battlecode', 'Cache me outside', 'UnderTheC', 'larp stock zi balls', 'dev test 1 :P', 'horse', 'acegi', 'SilverSamurai'):
    line(name, [r for r in them if r['team'] == name])
line('all 2100+ but chad gdp', [r for r in them if r['rating'] >= 2100 and r['team'] != 'chad gdp'])
print()
print('2. Other teams that die by choice before round 200')
for name in (':3', 'Heartbreaker', 'f2p', 'gdggs', 'Nitronics'):
    line(name, [r for r in them if r['team'] == name])

print()
print('3. Share of deaths by choice up to round 300 that fall with 60 or more of the team alive')
for name in ('chad gdp', ':3', 'f2p', 'Heartbreaker'):
    rs = [r for r in them if r['team'] == name]
    print('  %-14s %s of %s by window; first death by choice, median round %s' % (
        name, '/'.join(str(sum(r['cap'][k] for r in rs)) for k in range(3)), '/'.join(str(sum(r['free'][k] for r in rs)) for k in range(3)),
        med([r['first'] for r in rs])))
rs = us
print('  %-14s %s of %s' % ('US', '/'.join(str(sum(r['cap'][k] for r in rs)) for k in range(3)), '/'.join(str(sum(r['free'][k] for r in rs)) for k in range(3))))

print()
print('4. Games in which the side has 56 or more dragons at round 100 (the board is full for it early)')


def full(r):
    return r['st']['100'] is not None and r['st']['100']['alive'] >= 56


def rate(r):
    t = r['turns'][0] + r['turns'][1]
    return 1000 * (r['free'][0] + r['free'][1]) / t if t else 0


line('theirs, by choice 1+/1k by r200', [r for r in them if full(r) and rate(r) >= 1])
line('theirs, under 1/1k', [r for r in them if full(r) and rate(r) < 1])
line('theirs under 1/1k, rated 2100+', [r for r in them if full(r) and rate(r) < 1 and r['rating'] >= 2100])
line('theirs under 1/1k, below 2100', [r for r in them if full(r) and rate(r) < 1 and r['rating'] < 2100])
line('ours', [r for r in us if full(r)])
print('  inside one layout (their side, 56+ at r100): much = 1 or more deaths by choice per 1,000 turns by r200')
lay = defaultdict(lambda: ([], []))
for r in them:
    if full(r):
        lay[r['layout']][0 if rate(r) >= 1 else 1].append(r)
diffs = defaultdict(list)
for name, (much, little) in sorted(lay.items()):
    if len(much) < 2 or len(little) < 2:
        print('   %-22s much %d little %d (skipped)' % (name, len(much), len(little)))
        continue
    cells = []
    for rr in ('100', '200', '300'):
        for key in ('queen', 'longest', 'alive', 'total'):
            a = [x['st'][rr][key] for x in much if x['st'][rr] is not None]
            b = [x['st'][rr][key] for x in little if x['st'][rr] is not None]
            if a and b:
                diffs[rr, key].append((mean(a) - mean(b), min(len(a), len(b))))
                cells.append('%s %s %.1f/%.1f' % (rr, key, mean(a), mean(b)))
    print('   %-22s much %d (won %d, teams %s) little %d (won %d) | %s' % (name, len(much), sum(x['won'] for x in much),
          ','.join(sorted({x['team'][:8] for x in much})), len(little), sum(x['won'] for x in little), ' '.join(cells)))
print('   weighted mean of the within-layout differences (much minus little):',
      ' '.join('%s %s %+.1f' % (k[0], k[1], sum(d * w for d, w in v) / sum(w for d, w in v)) for k, v in sorted(diffs.items())))

print()
print('5. All games, their side, inside one layout: games with any death by choice by r200 against none (all labels of opponents)')
lay = defaultdict(lambda: ([], []))
for r in them:
    if r['st']['200'] is not None:
        lay[r['layout']][0 if r['free'][0] + r['free'][1] >= 3 else 1].append(r)
diffs = defaultdict(list)
wins = [0, 0, 0, 0]
for name, (much, little) in sorted(lay.items()):
    if len(much) < 2 or len(little) < 2:
        continue
    wins[0] += sum(x['won'] for x in much)
    wins[1] += len(much)
    wins[2] += sum(x['won'] for x in little)
    wins[3] += len(little)
    for rr in ('100', '200', '300'):
        for key in ('queen', 'longest', 'alive', 'total'):
            a = [x['st'][rr][key] for x in much if x['st'][rr] is not None]
            b = [x['st'][rr][key] for x in little if x['st'][rr] is not None]
            if a and b:
                diffs[rr, key].append((mean(a) - mean(b), min(len(a), len(b))))
print('   layouts with both', len(diffs['200', 'queen']), '| much: won %d of %d, little: won %d of %d' % tuple(wins))
print('   weighted mean difference (3 or more deaths by choice by r200, minus fewer):',
      ' '.join('%s %s %+.1f' % (k[0], k[1], sum(d * w for d, w in v) / sum(w for d, w in v)) for k, v in sorted(diffs.items())))
