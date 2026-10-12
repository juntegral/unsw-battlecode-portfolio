import json, sys
from collections import defaultdict
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet')
D = json.load(open('~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet/trophy.json'))
V = ['one5', 'one6', 'one7', 'one8', 'one9', 'one10', 'one11', 'one12', 'one13', 'one14', 'one15']
rows = []
for g in D:
    if g['bot_name'] not in V:
        continue
    eats = g['eats']
    def pe(s, r):
        return sum(1 for e in eats if e[0] <= r and e[1] == s)
    sp = [x for x in g['splits'] if x[1] == 0]
    r = dict(ver=g['bot_name'], opp=g['opp'][:6], gid=g['gid'], last=g['last'], res=g['result'],
             p25=pe(0, 25), p50=pe(0, 50), p100=pe(0, 100), t25=pe(1, 25), t50=pe(1, 50), t100=pe(1, 100),
             nat50=sum(1 for e in eats if e[0] <= 50 and e[1] == 0 and e[3] == 'n'),
             sp25=sum(1 for x in sp if x[0] < 25), sp50=sum(1 for x in sp if x[0] < 50),
             fs=min((x[0] for x in sp), default=99), qs=min((x[0] for x in sp if x[5]), default=99),
             d25=sum(1 for d in g['deaths'] if d[1] == 0 and d[0] < 25), d50=sum(1 for d in g['deaths'] if d[1] == 0 and d[0] < 50),
             td50=sum(1 for d in g['deaths'] if d[1] == 1 and d[0] < 50),
             x50=sum(1 for x in g['xings'] if x[1] == 0 and x[0] < 50), x100=sum(1 for x in g['xings'] if x[1] == 0 and x[0] < 100),
             xt50=sum(1 for x in g['xings'] if x[1] == 1 and x[0] < 50),
             qd=min((d[0] for d in g['deaths'] if d[1] == 0 and d[6]), default=999),
             tqd=min((d[0] for d in g['deaths'] if d[1] == 1 and d[6]), default=999))
    rows.append(r)
json.dump(rows, open('~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet/rows.json', 'w'))
key = lambda r: (V.index(r['ver']))
def show(sel, title):
    print('==', title)
    gs = defaultdict(list)
    for r in rows:
        if sel(r):
            gs[r['ver']].append(r)
    print('ver   n  w | us25 us50 us100 | th25 th50 th100 | nat50 | sp25 sp50 | fs qs | dead25 dead50 thD50 | xing50 xing100 thX50 | endlt100 | qdie<50 theirQdie<50')
    for v in V:
        L = gs.get(v)
        if not L:
            continue
        m = lambda k: sum(r[k] for r in L) / len(L)
        print('%-5s %2d %2d | %4.0f %4.0f %5.0f | %4.0f %4.0f %5.0f | %5.1f | %4.1f %4.1f | %4.1f %4.1f | %5.1f %5.1f %4.1f | %5.1f %5.1f %4.1f | %d | %d %d' % (
            v, len(L), sum(r['res'] == 'win' for r in L), m('p25'), m('p50'), m('p100'), m('t25'), m('t50'), m('t100'), m('nat50'),
            m('sp25'), m('sp50'), m('fs'), m('qs'), m('d25'), m('d50'), m('td50'), m('x50'), m('x100'), m('xt50'),
            sum(r['last'] < 100 for r in L), sum(r['qd'] < 50 for r in L), sum(r['tqd'] < 50 for r in L)))
show(lambda r: True, 'all')
for o in ('Cache', 'Preyas', 'kraken'):
    show(lambda r, o=o: r['opp'].startswith(o), o)
show(lambda r: r['opp'][:5] not in ('Cache', 'Preya', 'krake'), 'others')
