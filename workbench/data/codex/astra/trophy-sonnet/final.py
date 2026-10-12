import json
B = '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet/'
R = json.load(open(B + 'rows.json'))
D = {g['gid']: g for g in json.load(open(B + 'trophy.json'))}
V = ['one8', 'one10', 'one11', 'one12', 'one13', 'one14']
print('ver n | all-eats us r25 r35 | r50 (games >=50 rounds) | alive50 | dead<35 | xings<50 | games ended <100')
for v in V:
    L = [g for g in D.values() if g['bot_name'] == v]
    def pe(g, r):
        return sum(1 for e in g['eats'] if e[0] <= r and e[1] == 0)
    m25 = sum(pe(g, 25) for g in L) / len(L)
    m35 = sum(pe(g, 35) for g in L) / len(L)
    L5 = [g for g in L if g['last'] >= 50]
    m50 = sum(pe(g, 50) for g in L5) / len(L5)
    al = [g['snaps']['50'][0][0] for g in L5]
    d35 = sum(sum(1 for d in g['deaths'] if d[1] == 0 and d[0] < 35) for g in L) / len(L)
    x50 = sum(sum(1 for x in g['xings'] if x[1] == 0 and x[0] < 50) for g in L) / len(L)
    print('%-5s %2d | %5.1f %5.1f | %5.1f (n=%d) | %4.1f | %4.1f | %4.1f | %d' % (v, len(L), m25, m35, m50, len(L5), sum(al) / len(al), d35, x50, sum(g['last'] < 100 for g in L)))
print()
print('per-game spread of all-eats r35, sorted, per version')
for v in V:
    print(v, sorted(sum(1 for e in g['eats'] if e[0] <= 35 and e[1] == 0) for g in D.values() if g['bot_name'] == v))
