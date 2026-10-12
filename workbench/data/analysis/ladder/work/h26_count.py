# Own count (analyst, run 20261007-1800): reads work/h26-shard0..3.jsonl and rows.jsonl; prints the F42_sight and F44_who numbers.
import json
from collections import Counter, defaultdict
D = 'data/analysis/ladder/'
rows = dict((json.loads(l)['game'], json.loads(l)) for l in open(D + 'rows.jsonl') if l.strip())
maps = json.load(open(D + 'maps.json'))
recs = dict()
err = 0
for k in range(4):
    for l in open(D + 'work/h26-shard%d.jsonl' % k):
        x = json.loads(l)
        if 'error' in x:
            err += 1
            continue
        recs[x['game']] = x
print('records', len(recs), 'errors', err, 'full', sum(x['full'] for x in recs.values()))
LAST = 1316833


def wiped(r):
    return r['ended_by'] == 'elimination' and r['final']['us']['alive'] == 0 and r['last_round'] <= 125


def show(name, games, s):
    t = [0] * 7
    per = []
    for g in games:
        v = recs[g]['sight'][s]
        for i in range(7):
            t[i] += v[i]
        if v[0]:
            per.append(v[1] / v[0])
    if not t[0]:
        print('  ', name, 'no turns')
        return
    per.sort()
    print('  ', name, 'games', len(games), 'turns', t[0], 'fresh', t[1], round(t[1] / t[0], 3), 'seen now', round(t[6] / t[0], 3), 'never seen', round(t[4] / t[0], 3),
          '| fresh and head within 6:', t[2], round(t[2] / max(1, t[1]), 3), '(short', round(t[5] / max(1, t[1]), 3), ') | not fresh and within 6:', t[3], round(t[3] / max(1, t[0] - t[1]), 3),
          '| per game fresh share: under 0.2 in', sum(1 for p in per if p < 0.2), '0.2-0.8 in', sum(1 for p in per if 0.2 <= p < 0.8), '0.8+ in', sum(1 for p in per if p >= 0.8))


print('=== F42_sight')
for code in ('main', 'v31'):
    full = [g for g, x in recs.items() if x['full'] and rows[g]['our_code'] == code]
    lost = [g for g in full if rows[g]['queens_at_end'] == 'only theirs' and rows[g]['ended_by'] == 'queen rule']
    flag = [g for g in lost if rows[g]['final']['us']['longest'] > rows[g]['final']['them']['longest']]
    mirror = [g for g in full if rows[g]['queens_at_end'] == 'only ours' and rows[g]['ended_by'] == 'queen rule']
    print(code, 'f42_set', len(lost), 'flagged', len(flag), 'mirror', len(mirror))
    show('f42_set, their lone queen', lost, 'them')
    show('flagged', flag, 'them')
    show('not flagged', [g for g in lost if g not in flag], 'them')
    show('f42_set without Portals', [g for g in lost if rows[g]['map'] != 'Portals'], 'them')
    show('flagged without Portals', [g for g in flag if rows[g]['map'] != 'Portals'], 'them')
    show('Portals only', [g for g in lost if rows[g]['map'] == 'Portals'], 'them')
    show('f42_set big layouts', [g for g in lost if recs[g]['cells'] > 1200], 'them')
    show('f42_set small without Portals', [g for g in lost if recs[g]['cells'] <= 1200 and rows[g]['map'] != 'Portals'], 'them')
    show('mirror, our lone queen (their sight of her)', mirror, 'us')
    show('mirror without Portals', [g for g in mirror if rows[g]['map'] != 'Portals'], 'us')
    if code == 'main':
        show('f42_set half 1', [g for g in lost if rows[g]['time'] < '2026-10-06T14:48:15'], 'them')
        show('f42_set half 2', [g for g in lost if rows[g]['time'] >= '2026-10-06T14:48:15'], 'them')
        for g in sorted(flag):
            v = recs[g]['sight']['them']
            print('      flagged', rows[g]['battle'], g, rows[g]['map_key'], rows[g]['opponent_rating'], 'turns', v[0], 'fresh', v[1], 'fresh+near', v[2], 'stale+near', v[3], 'never', v[4])

print('=== F44_who (head-on meetings between the teams, raw rounds 0-60)')
for code in ('main', 'v31'):
    g_all = [g for g, x in recs.items() if rows[g]['our_code'] == code and x['cells'] <= 1200]
    old = [g for g in g_all if wiped(rows[g]) and rows[g]['battle'] <= LAST]
    newg = [g for g in g_all if wiped(rows[g]) and rows[g]['battle'] > LAST]
    lay = set(rows[g]['map_key'] for g in old)
    other = [g for g in g_all if not wiped(rows[g]) and rows[g]['map_key'] in lay]
    for name, gs in (('the early wipe-outs of the bar', old), ('new early wipe-outs', newg), ('other games on the same layouts', other), ('all small-layout games', g_all)):
        m = [h for g in gs for h in recs[g]['ho']]
        th = [h for h in m if h[1] == 1]
        us = [h for h in m if h[1] == 0]
        zero = sum(1 for g in gs if not recs[g]['ho'])
        print(' ', code, name, 'games', len(gs), 'meetings', len(m), 'mover theirs', len(th), round(len(th) / max(1, len(m)), 3), '| games with none', zero,
              '| their mover length', dict(sorted(Counter(min(h[2], 6) for h in th).items())), 'our victim length', dict(sorted(Counter(min(h[3], 6) for h in th).items())),
              '| our mover length', dict(sorted(Counter(min(h[2], 6) for h in us).items())), 'their victim length', dict(sorted(Counter(min(h[3], 6) for h in us).items())),
              '| victim a queen: ours', sum(h[4] for h in th), 'theirs', sum(h[4] for h in us), '| mover a queen: theirs', sum(h[5] for h in th), 'ours', sum(h[5] for h in us))
    if code == 'main':
        for b, lo, hi in (('1700-1899', 1700, 1900), ('1900-2099', 1900, 2100), ('2100+', 2100, 9999)):
            gs = [g for g in g_all if lo <= rows[g]['opponent_rating'] < hi]
            m = [h for g in gs for h in recs[g]['ho']]
            print('    band', b, 'games', len(gs), 'meetings per game', round(len(m) / max(1, len(gs)), 2), 'mover theirs', round(sum(1 for h in m if h[1] == 1) / max(1, len(m)), 3))
    per = defaultdict(lambda: [0, 0])
    for g in old:
        for h in recs[g]['ho']:
            per[rows[g]['map_key']][h[1]] += 1
    print('   by layout in the wipe-outs [ours mover, theirs mover]', dict(per))
