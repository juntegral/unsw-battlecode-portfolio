import json, sys
D = json.load(open('~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet/trophy.json'))
ordr = {'one%d' % i: i for i in range(1, 20)}
want = int(sys.argv[1]) if len(sys.argv) > 1 else 8


def row(g):
    sn = g['snaps']
    eats = g['eats']

    def pe(s, r):
        return sum(1 for e in eats if e[0] <= r and e[1] == s)

    def pn(s, r):
        return sum(1 for e in eats if e[0] <= r and e[1] == s and e[3] == 'n')

    def dr(s, r):
        v = sn.get(str(r))
        return v[s][0] if v else -1

    def tl(s, r):
        v = sn.get(str(r))
        return v[s][1] if v else -1
    sp = [x for x in g['splits'] if x[1] == 0]
    fs = min((x[0] for x in sp), default=-1)
    qs = min((x[0] for x in sp if x[5]), default=-1)
    nsp = sum(1 for x in sp if x[0] < 100)
    dths = [d for d in g['deaths'] if d[1] == 0 and d[0] < 100]
    dtxt = ','.join('%d%s%d' % (d[0], d[4][:2], d[2]) for d in dths)
    xo = sum(1 for x in g['xings'] if x[1] == 0 and x[0] < 100)
    xq = sum(1 for x in g['xings'] if x[1] == 0 and x[0] < 100 and x[3])
    qd = [d[0] for d in g['deaths'] if d[1] == 0 and d[6]]
    return dict(g=g, ver=g['bot_name'], opp=g['opp'][:6], seat=g['seat'], res=g['result'][0] + ('/' + g['how'][0]), last=g['last'],
                pe=[pe(0, r) for r in (25, 50, 100)], pt=[pe(1, r) for r in (25, 50, 100)],
                pn=pn(0, 100), dr=[dr(0, 50), dr(0, 100)], dt=[dr(1, 50), dr(1, 100)], tl=[tl(0, 100), tl(1, 100)],
                fs=fs, qs=qs, nsp=nsp, nd=len(dths), dtxt=dtxt, xo=xo, xq=xq, qd=qd[0] if qd else -1, gid=g['gid'], rk=g['ranked'])


rows = [row(g) for g in D]
rows.sort(key=lambda r: (ordr.get(r['ver'], 99), r['opp'], r['gid']))
print('ver   opp    gid     seat res   last |us25 50 100 nat | th25 50 100 | drg50 100 | thD50 100 | len100 us/th | 1stSp qSp nSp d<100 xing xingQ qDie | deaths')
for r in rows:
    print('%-5s %-6s %-8d %s %-5s %4d |%3d %3d %3d %3d |%3d %3d %3d |%2d %2d |%2d %2d |%3d %3d | %3d %3d %2d %2d %3d %3d %4d | %s' % (
        r['ver'], r['opp'], r['gid'], r['seat'], r['res'], r['last'], *r['pe'], r['pn'], *r['pt'], *r['dr'], *r['dt'], *r['tl'],
        r['fs'], r['qs'], r['nsp'], r['nd'], r['xo'], r['xq'], r['qd'], r['dtxt']))
