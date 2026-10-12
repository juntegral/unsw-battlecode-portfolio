import json, sys
B = '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet/'
D = {g['gid']: g for g in json.load(open(B + 'trophy.json'))}
for gid in map(int, sys.argv[1:]):
    g = D[gid]
    print('==', gid, g['bot_name'], g['opp'], g['result'], g['last'], 'seat', g['seat'])
    s0 = g['snaps'].get('0')
    print(' snaps keys', sorted(map(int, g['snaps']))[:12], 'r0', s0 and [s0[0][:4], s0[1][:4]])
    print(' rnd | us nat/drop alive len | th nat/drop alive len | usxing')
    for r in range(5, min(g['last'], 100) + 1, 5):
        e = g['eats']
        def c(s):
            n = sum(1 for x in e if x[0] <= r and x[1] == s and x[3] == 'n')
            d = sum(1 for x in e if x[0] <= r and x[1] == s and x[3] != 'n')
            return n, d
        def alive(s):
            a = 1 + sum(1 for x in g['splits'] if x[1] == s and x[0] <= r)
            a -= sum(1 for d in g['deaths'] if d[1] == s and d[0] <= r)
            return a
        xs = sum(1 for x in g['xings'] if x[1] == 0 and x[0] <= r)
        print(' %3d | %3d %3d %3d | %3d %3d %3d | %d' % (r, *c(0), alive(0), *c(1), alive(1), xs))
    print(' splits us:', [(x[0], x[2], x[3], x[4], 'Q' if x[5] else '') for x in g['splits'] if x[1] == 0 and x[0] < 50])
    print(' deaths us<50:', [(d[0], d[2], d[4], 'Q' if d[6] else '') for d in g['deaths'] if d[1] == 0 and d[0] < 50])
    print(' xings us<60:', [(x[0], x[2], x[3], x[4]) for x in g['xings'] if x[1] == 0 and x[0] < 60])
