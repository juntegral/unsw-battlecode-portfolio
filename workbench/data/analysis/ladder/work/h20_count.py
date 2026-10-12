# Own count (analyst, run 20261007-1000): reads the h20 shards and prints the numbers for bars F38_entry, F38_pearl and F39_supply.
import json
from collections import defaultdict
D = 'data/analysis/ladder/'
rows = dict((r['game'], r) for r in (json.loads(l) for l in open(D + 'rows.jsonl')))
maps = json.load(open(D + 'maps.json'))
recs = []
err = 0
for k in range(4):
    for l in open(D + 'work/h20-shard%d.jsonl' % k):
        x = json.loads(l)
        if 'error' in x:
            err += 1
            print('error', x)
            continue
        recs.append(x)
print('games', len(recs), 'errors', err)


def free(r):
    return not maps[r['map_key']]['queen_spawn_dead_end']


def add(a, b):
    for i, v in enumerate(b):
        a[i] += v


def rt(a, b):
    return round(a / b, 4) if b else None


def entry(sel, wins=(0, 1)):
    out = dict()
    for s in ('us', 'them'):
        e = [0] * 8
        st = [0] * 4
        for x in sel:
            for w in wins:
                add(e, x['entry'][s][w])
                add(st, x['stay'][s][w])
        out[s] = (e, st)
    return out


def show(label, sel, wins=(0, 1)):
    o = entry(sel, wins)
    eu, su = o['us']
    et, stt = o['them']
    ru = rt(eu[2], eu[0])
    rth = rt(et[2], et[0])
    print(label, 'games', len(sel))
    print('   chances us %d them %d | entered us %d (%s) them %d (%s) ratio %s | died in turn %d %d' % (eu[0], et[0], eu[2], ru, et[2], rth, rt(ru, rth) if ru and rth else None, eu[3], et[3]))
    fu = rt(eu[2], eu[1])
    ft = rt(et[2], et[1])
    print('   free narrow neighbour: us %d them %d rate %s %s ratio %s' % (eu[1], et[1], fu, ft, rt(fu, ft) if fu and ft else None))
    print('   entries onto a pearl tile: us %d of %d (%s) them %d of %d (%s); with a pearl on an open neighbour too: us %d them %d' % (eu[4], eu[2], rt(eu[4], eu[2]), et[4], et[2], rt(et[4], et[2]), eu[5], et[5]))
    pu = rt(eu[7], eu[6])
    pt = rt(et[7], et[6])
    print('   pearl on a free narrow neighbour: us %d entered %d (%s) them %d entered %d (%s) ratio %s' % (eu[6], eu[7], pu, et[6], et[7], pt, rt(pu, pt) if pu and pt else None))
    nu = rt(eu[2] - eu[7], eu[1] - eu[6])
    nt = rt(et[2] - et[7], et[1] - et[6])
    print('   no pearl on any free narrow neighbour (free narrow neighbour exists): us %s them %s ratio %s' % (nu, nt, rt(nu, nt) if nu and nt else None))
    print('   stays begun us %d them %d | turns per stay %s %s | stays ending in her death %d (%s) %d (%s) | back out %d %d' % (su[0], stt[0], rt(su[1], su[0]), rt(stt[1], stt[0]), su[2], rt(su[2], su[0]), stt[2], rt(stt[2], stt[0]), su[3], stt[3]))


for code in ('main', 'v31'):
    sel = [x for x in recs if rows[x['game']]['our_code'] == code and free(rows[x['game']])]
    show(code + ' free r0-200', sel)
    show(code + ' free r0-100', sel, (0,))
    show(code + ' free r101-200', sel, (1,))
    show(code + ' free r201+', sel, (2, 3))
    cut = '2026-10-06T14:48:15'
    if code == 'main':
        show('main half 1 r0-200', [x for x in sel if rows[x['game']]['time'] < cut])
        show('main half 2 r0-200', [x for x in sel if rows[x['game']]['time'] >= cut])
        show('main band b r0-200', [x for x in sel if 1700 <= rows[x['game']]['opponent_rating'] < 1900])
        show('main band c r0-200', [x for x in sel if 1900 <= rows[x['game']]['opponent_rating'] < 2100])
    show(code + ' without Portals r0-200', [x for x in sel if rows[x['game']]['map_key'] != 'Portals #1'])
print('--- by layout, both codes, r0-200')
by = defaultdict(list)
for x in recs:
    if free(rows[x['game']]):
        by[rows[x['game']]['map_key']].append(x)
for k in sorted(by):
    o = entry(by[k])
    eu, su = o['us']
    et, stt = o['them']
    print('  %-22s games %3d chances %5d %5d entered %4d %4d rate %s %s | pearl entries %d %d | stays %d %d turns/stay %s %s died %d %d' % (k, len(by[k]), eu[0], et[0], eu[2], et[2], rt(eu[2], eu[0]), rt(et[2], et[0]), eu[4], et[4], su[0], stt[0], rt(su[1], su[0]), rt(stt[1], stt[0]), su[2], stt[2]))
print('--- F39_supply')


def lone(label, sel):
    out = dict()
    for s in ('us', 'them'):
        t = [[0] * 6, [0] * 6]
        for x in sel:
            for ph in (0, 1):
                add(t[ph], x['lone'][s][ph])
        out[s] = t
    print(label, 'games', len(sel))
    for ph, name in ((0, 'before grow_round'), (1, 'from grow_round'), (2, 'both')):
        def g(s):
            t = out[s]
            return [t[0][i] + t[1][i] for i in range(6)] if ph == 2 else t[ph]
        a = g('them')
        b = g('us')
        # a: turns of THEIR lone queen, counts are OUR dragons; b: turns of OUR lone queen, counts are THEIR dragons
        ma = rt(a[1], a[0])
        mb = rt(b[1], b[0])
        sa = rt(a[2], a[1])
        sb = rt(b[2], b[1])
        print('   %-18s their lone turns %6d: our short alive %s, within 12 share %s, any within 12 %s, within 6 per turn %s, all alive %s' % (name, a[0], ma, sa, rt(a[3], a[0]), rt(a[5], a[0]), rt(a[4], a[0])))
        print('   %-18s our lone turns   %6d: their short alive %s, within 12 share %s, any within 12 %s, within 6 per turn %s, all alive %s' % ('', b[0], mb, sb, rt(b[3], b[0]), rt(b[5], b[0]), rt(b[4], b[0])))
        print('   %-18s ratio short alive (ours/theirs) %s ; ratio share within 12 %s ; ratio count within 12 per turn %s' % ('', rt(ma, mb) if ma and mb else None, rt(sa, sb) if sa and sb else None, rt(a[2] / a[0], b[2] / b[0]) if a[0] and b[0] and b[2] else None))


for code in ('main', 'v31'):
    sel = [x for x in recs if rows[x['game']]['our_code'] == code and free(rows[x['game']])]
    lone(code + ' free all endings', sel)
    lone(code + ' free full games', [x for x in sel if rows[x['game']]['last_round'] == 499])
    lone(code + ' free all endings without Portals', [x for x in sel if rows[x['game']]['map_key'] != 'Portals #1'])
    lone(code + ' free big layouts', [x for x in sel if x['cells'] > 1200])
    lone(code + ' free small layouts without Portals', [x for x in sel if x['cells'] <= 1200 and rows[x['game']]['map_key'] != 'Portals #1'])
