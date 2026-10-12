# Own count (analyst, run 20261007-1800): reads work/h27-shard0..3.jsonl and rows.jsonl; prints the F42_sight_head numbers.
import json
D = 'data/analysis/ladder/'
rows = dict((json.loads(l)['game'], json.loads(l)) for l in open(D + 'rows.jsonl') if l.strip())
recs = dict()
err = 0
for k in range(4):
    for l in open(D + 'work/h27-shard%d.jsonl' % k):
        x = json.loads(l)
        if 'error' in x:
            err += 1
            continue
        recs[x['game']] = x
print('records', len(recs), 'errors', err)
NAMES = ('0-20', '21-50', '51-100', 'over 100', 'never')


def show(name, games, s):
    a = [[0, 0, 0, 0] for _ in range(5)]
    n = [0, 0, 0, 0]
    per = []
    for g in games:
        v = recs[g]['age'][s]
        for c in range(5):
            for i in range(4):
                a[c][i] += v[c][i]
        for i in range(4):
            n[i] += recs[g]['now'][s][i]
        tot = sum(v[c][0] for c in range(5))
        if tot:
            per.append(v[0][0] / tot)
    T = sum(a[c][0] for c in range(5))
    if not T:
        print('  ', name, 'no turns')
        return
    per.sort()
    print('  ', name, '| games', len(games), 'turns', T, '| her mean length', round(n[3] / T, 1))
    print('      age share:', ', '.join('%s %.3f' % (NAMES[c], a[c][0] / T) for c in range(5)), '| aged 21-100:', round((a[1][0] + a[2][0]) / T, 3))
    print('      nearest head by path steps (6 or less / 7-12 / further), per age class:', ', '.join('%s %.3f/%.3f/%.3f' % (NAMES[c], a[c][1] / max(1, a[c][0]), a[c][2] / max(1, a[c][0]), a[c][3] / max(1, a[c][0])) for c in range(5)))
    print('      all turns within 6:', round(sum(a[c][1] for c in range(5)) / T, 3), '| seen now', n[0], round(n[0] / T, 3), 'with a short seer', n[1], round(n[1] / max(1, n[0]), 3), 'seers per seen turn', round(n[2] / max(1, n[0]), 2),
          '| per game fresh share under 0.2 in', sum(1 for p in per if p < 0.2), ', 0.2-0.8 in', sum(1 for p in per if 0.2 <= p < 0.8), ', 0.8+ in', sum(1 for p in per if p >= 0.8))


for code in ('main', 'v31'):
    full = [g for g in recs if rows[g]['our_code'] == code]
    lost = [g for g in full if rows[g]['queens_at_end'] == 'only theirs' and rows[g]['ended_by'] == 'queen rule']
    flag = [g for g in lost if rows[g]['final']['us']['longest'] > rows[g]['final']['them']['longest']]
    mirror = [g for g in full if rows[g]['queens_at_end'] == 'only ours' and rows[g]['ended_by'] == 'queen rule']
    np_ = [g for g in lost if rows[g]['map'] != 'Portals']
    print('==', code, 'f42_set', len(lost), 'flagged', len(flag), 'mirror', len(mirror))
    show('f42_set without Portals (their lone queen, our heads)', np_, 'them')
    show('flagged without Portals', [g for g in flag if rows[g]['map'] != 'Portals'], 'them')
    show('not flagged without Portals', [g for g in np_ if g not in flag], 'them')
    show('Portals only', [g for g in lost if rows[g]['map'] == 'Portals'], 'them')
    show('f42_set with Portals', lost, 'them')
    show('big layouts', [g for g in np_ if recs[g]['cells'] > 1200], 'them')
    show('small layouts without Portals', [g for g in np_ if recs[g]['cells'] <= 1200], 'them')
    show('mirror (our lone queen, their heads)', mirror, 'us')
    if code == 'main':
        show('half 1 without Portals', [g for g in np_ if rows[g]['time'] < '2026-10-06T14:48:15'], 'them')
        show('half 2 without Portals', [g for g in np_ if rows[g]['time'] >= '2026-10-06T14:48:15'], 'them')
        show('against 1700-1899', [g for g in np_ if rows[g]['opponent_rating'] < 1900], 'them')
        show('against 1900+', [g for g in np_ if rows[g]['opponent_rating'] >= 1900], 'them')
