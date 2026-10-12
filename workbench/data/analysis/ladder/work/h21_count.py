# Own count (analyst, run 20261007-1000): reads the h21 shards and prints the numbers for bar F39_sight.
import json
D = 'data/analysis/ladder/'
rows = dict((r['game'], r) for r in (json.loads(l) for l in open(D + 'rows.jsonl')))
maps = json.load(open(D + 'maps.json'))
recs = []
for k in range(4):
    for l in open(D + 'work/h21-shard%d.jsonl' % k):
        x = json.loads(l)
        if 'error' in x:
            print('error', x)
            continue
        recs.append(x)
print('games', len(recs))


def rt(a, b):
    return round(a / b, 4) if b else None


def show(label, sel):
    print(label, 'games', len(sel))
    for s, name in (('them', 'THEIR lone queen, our dragons'), ('us', 'OUR lone queen, their dragons')):
        t = [0] * 10
        g = 0
        for x in sel:
            if x['sight'][s][0]:
                g += 1
            for i, v in enumerate(x['sight'][s]):
                t[i] += v
        stale = t[0] - t[2]
        print('   %-30s games %3d turns %6d | seen now %s | fresh %s | never seen yet %s | short within 12 per turn: fresh %s stale %s | any within 12: fresh %s stale %s | short alive: fresh %s stale %s' % (
            name, g, t[0], rt(t[1], t[0]), rt(t[2], t[0]), rt(t[9], t[0]), rt(t[3], t[2]), rt(t[4], stale), rt(t[7], t[2]), rt(t[8], stale), rt(t[5], t[2]), rt(t[6], stale)))


for code in ('main', 'v31'):
    base = [x for x in recs if rows[x['game']]['our_code'] == code and not maps[rows[x['game']]['map_key']]['queen_spawn_dead_end']]
    sel = [x for x in base if rows[x['game']]['map_key'] != 'Portals #1']
    show(code + ' free without Portals', sel)
    show(code + ' free with Portals', base)
    show(code + ' big layouts', [x for x in sel if x['cells'] > 1200])
    show(code + ' small layouts', [x for x in sel if x['cells'] <= 1200])
    show(code + ' full games', [x for x in sel if rows[x['game']]['last_round'] == 499])
    if code == 'main':
        show('main 1700-1899', [x for x in sel if 1700 <= rows[x['game']]['opponent_rating'] < 1900])
        show('main 1900-2099', [x for x in sel if 1900 <= rows[x['game']]['opponent_rating'] < 2100])
        show('main 2100+', [x for x in sel if rows[x['game']]['opponent_rating'] >= 2100])
        cut = '2026-10-06T14:48:15'
        show('main half 1', [x for x in sel if rows[x['game']]['time'] < cut])
        show('main half 2', [x for x in sel if rows[x['game']]['time'] >= cut])
