"""Ram definitions ported from at_scan.py and at_more.py (TRADE_EVEN on)."""
from collections import deque

CAP = 8
TARGETS = ('shorter', 'same_under_twice', 'twice_or_more')
REACHES = ('free', 'paid')
VIEWS = ('outnumbered', 'not_outnumbered')
RAM_FIELDS = ('ram_added_chances', 'ram_added_taken', 'ram_added_take_rate',
              'ram_twice_count', 'ram_twice_mover_length_sum',
              'ram_twice_victim_length_sum', 'ram_twice_swing_sum',
              'ram_twice_longest_count', 'ram_twice_queen_count',
              'ram_headons_started', 'ram_meeting_net')


def find_heads(g, src, L, s, heads, bodies, side, occ, present):
    free = (L + 3) // 4
    budget = free + L - 2
    d, q, seen = {src: (0, 0)}, deque([src]), {}
    while q:
        c = q.popleft()
        cc, cs = d[c]
        if cs >= CAP:
            continue
        for t in g.adj[c]:
            if occ[t]:
                j = heads.get(t)
                if j is not None and side(j) != s and cc + 1 <= budget:
                    old = seen.get(t)
                    if old is None or (cs + 1, cc + 1) < old:
                        seen[t] = (cs + 1, cc + 1)
                continue
            nc = cc if t in present else cc + 1
            if nc > budget - 1:
                continue
            old = d.get(t)
            if old is not None and old <= (nc, cs + 1):
                continue
            d[t] = (nc, cs + 1)
            if nc == cc:
                q.appendleft(t)
            else:
                q.append(t)
    win = g.window(src)
    ov = ev = lng = 0
    bigs = []
    for c in win:
        j = heads.get(c)
        if j is None or c == src:
            continue
        if side(j) == s:
            ov += 1
            lng += len(bodies[j]) > L
            if sum(z in win for z in bodies[j]) >= 10:
                bigs.append(c)
        else:
            ev += 1
    def gap(a, b):
        dx, dy = abs(a % g.w - b % g.w), abs(a // g.w - b // g.w)
        return min(dx, g.w-dx) + min(dy, g.h-dy)
    return [(heads[t], dist, free, ov, ev,
             sum(z in win for z in bodies[heads[t]]), lng,
             int(any(gap(c, t) <= 6 for c in bigs)))
            for t, (dist, cost) in seen.items()]


def fails(g, r, even=True):
    rnd, L, q, Lt, dist, free, ov, ev, vis, n_own, lng, big, pe = r[0], r[3], r[4], r[7], r[10], r[11], r[12], r[13], r[16], r[17], r[19], r[20], r[24]
    feeding = rnd > g['feed'] or (rnd > 200 and n_own >= 56)
    plain_reach = free + L - 2
    if not q and L <= 10 and dist <= plain_reach and dist <= 8:
        if (vis >= 10 and vis >= L + 4) or big:
            return ()
        if feeding and vis >= 6 and vis * 2 >= L and lng > 0:
            return ()
    f = []
    if q:
        f.append('queen')
    if L > 4:
        f.append('len>4')
    if rnd > g['feed']:
        f.append('feedround')
    if n_own < (1 if g['aggr'] else 8):
        f.append('units')
    if ov + 1 - ev < 1:
        f.append('count')
    cap = n_own >= 59
    need = L if (cap or g['aggr'] or even) else max(5, L + 2)
    if vis < need:
        f.append('size')
    if dist > min(plain_reach, 3 if g['aggr'] else 4):
        f.append('steps')
    return tuple(f)


def H(g, r):
    L = r[3]
    return (not r[4]) and L <= 4 and r[16] >= 2 * L and r[10] <= r[11] + L - 2


def swing(x):
    return (x['mm'] + x['vm'] - x['L0']) - (x['mv'] + x['vv'] - x['Lv'])


def measures(chances, meetings, s, cells, queen300):
    from collections import Counter
    c = Counter()
    g = dict(feed=300 if cells > 600 and queen300 else 400, aggr=cells <= 1200)
    for r in chances:
        if r[1] != s:
            continue
        L, Lt = r[3], r[7]
        target = 'shorter' if Lt < L else 'same_under_twice' if Lt < 2*L else 'twice_or_more'
        reach = 'free' if r[10] <= r[11] else 'paid'
        view = 'outnumbered' if r[12] < r[13] else 'not_outnumbered'
        stem = f'ram_{target}_{reach}_{view}_'
        c[stem+'chances'] += 1
        c[stem+'taken'] += r[22] == 1
        if H(g, r) and fails(g, r):
            c['ram_added_chances'] += 1
            c['ram_added_taken'] += r[22] == 1
    for x in meetings:
        if not x['cross']:
            continue
        c['ram_meeting_net'] += (x['mm'] + x['vm'] - x['L0'] if x['ms'] == s
                                 else x['mv'] + x['vv'] - x['Lv'])
        if x['ms'] != s:
            continue
        c['ram_headons_started'] += 1
        if x['Lv'] >= 2*x['L0']:
            c['ram_twice_count'] += 1
            c['ram_twice_mover_length_sum'] += x['L0']
            c['ram_twice_victim_length_sum'] += x['Lv']
            c['ram_twice_swing_sum'] += swing(x)
            c['ram_twice_longest_count'] += x['mtop']
            c['ram_twice_queen_count'] += x['mq']
    out = {f: c[f] for f in RAM_FIELDS}
    out['ram_added_take_rate'] = c['ram_added_taken']/max(1, c['ram_added_chances'])
    for t in TARGETS:
        for reach in REACHES:
            for view in VIEWS:
                for f in ('chances', 'taken'):
                    name = f'ram_{t}_{reach}_{view}_{f}'
                    out[name] = c[name]
    return out
