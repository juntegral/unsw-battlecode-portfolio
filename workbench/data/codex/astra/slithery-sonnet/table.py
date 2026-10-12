"""Per-game rows + loss classes. Usage: python3 -I table.py [min_bot_submission]"""
import json, sys
from collections import Counter, defaultdict
D = '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/slithery-sonnet/'
VER = {}
for l in open('~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/versions.tsv'):
    a, b = l.split()
    VER[a] = b
rows = [json.loads(l) for l in open(D + 'scan.jsonl')]
rows = [r for r in rows if int(r['bot']) >= 21269 and r['bot'] in VER]  # one11 and later
seen=set(); _u=[]
for r in rows:
    if r['gid'] in seen: continue
    seen.add(r['gid']); _u.append(r)
rows=_u
RK=json.load(open(D+'rankedflag.json'))
for r in rows: r['ranked']=RK.get(str(r['gid']),[None])[0]
rows.sort(key=lambda r: (r['map'], r['completed']))


def q(sn, r, s):
    v = sn.get(str(r))
    return '-' if v is None else str(v[s][3])


def behind(r):
    """first snapshot round after which (queen, longest, total) of us never reaches theirs again"""
    last_ok = -1
    rs = sorted(int(k) for k in r['snaps'])
    for k in rs:
        v = r['snaps'][str(k)]
        if tuple(v[0][3:4] + v[0][2:3] + v[0][1:2]) >= tuple(v[1][3:4] + v[1][2:3] + v[1][1:2]):
            last_ok = k
    if last_ok == rs[-1]:
        return 'never'
    nxt = [k for k in rs if k > last_ok]
    return str(nxt[0]) if last_ok >= 0 else '0'


def klass(r):
    e = r['ends']
    if r['result'] != 'loss':
        return r['result']
    if r['how'] == 'elim':
        return 'd-wiped'
    uq, tq = e[0][3], e[1][3]
    if uq == 0 and tq > 0:
        return 'a-ourQdead'
    if uq == 0 and tq == 0:
        return 'b-bothQdead'
    if uq > 0 and tq > 0:
        return 'c-bothalive' if r['how'] == 'queen' or True else 'x'
    return 'x-other'


def qdeath(r, s):
    out = [(d[0], d[2], d[4]) for d in r['deaths'] if d[1] == s and d[6]]
    return out


if __name__ == '__main__':
    cls = defaultdict(Counter)
    wl = defaultdict(Counter)
    for r in rows:
        k = klass(r)
        wl[r['map']][r['result']] += 1
        if r['result'] == 'loss':
            cls[r['map']][k] += 1
        e = r['ends']
        us_el = r['elo'][0] if r['teamA'] == 1119 else r['elo'][1]
        th_el = r['elo'][1] if r['teamA'] == 1119 else r['elo'][0]
        sn = r['snaps']
        qd0 = qdeath(r, 0)
        qd1 = qdeath(r, 1)
        print('%s %-14s %-3s %s one%s opp%d(%s) us=%d | %-5s %-12s beh=%-5s end us n%d T%d long%d Q%d | them n%d T%d long%d Q%d | Q us r100/200/300 %s/%s/%s them %s/%s/%s | Qdie us %s them %s | last r%d' % (
            r['gid'], r['map'], 'RK' if r['ranked'] else 'unr', r['completed'][5:16], VER[r['bot']][3:], th_el, r['opp'][:10], us_el, r['result'], k, behind(r),
            e[0][0], e[0][1], e[0][2], e[0][3], e[1][0], e[1][1], e[1][2], e[1][3],
            q(sn, 100, 0), q(sn, 200, 0), q(sn, 300, 0), q(sn, 100, 1), q(sn, 200, 1), q(sn, 300, 1),
            qd0 or '-', qd1 or '-', r['last']))
    print()
    for m in wl:
        print(m, dict(wl[m]), dict(cls[m]))
