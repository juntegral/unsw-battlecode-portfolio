import json, glob, os
B = '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet/'
D = json.load(open(B + 'trophy.json'))
meta = {}
for f in glob.glob('~/01. Project/개인 프로젝트/unsw-swarm/data/online/smoke/*-old/game-*.json') + glob.glob('~/01. Project/개인 프로젝트/unsw-swarm/data/online/live-one1/b*/game-*.json'):
    j = json.load(open(f))
    meta[j['id']] = j
print('opp | ver | gid | completedAt | their elo | res | their: nat50 splits50 xings50 alive50 firstSplit | us: nat50 splits50 xings50 alive50 firstSplit')
for g in sorted(D, key=lambda g: (g['opp'], g['gid'])):
    if g['bot_name'] not in ('one8', 'one9', 'one10', 'one11', 'one12', 'one13', 'one14'):
        continue
    j = meta[g['gid']]
    ours_a = j['teamAId'] == 1119
    te = j['teamBElo'] if ours_a else j['teamAElo']
    e = g['eats']
    def st(s):
        nat = sum(1 for x in e if x[1] == s and x[0] <= 50 and x[3] == 'n')
        sp = [x[0] for x in g['splits'] if x[1] == s]
        sp50 = sum(1 for r in sp if r < 50)
        xn = sum(1 for x in g['xings'] if x[1] == s and x[0] < 50)
        alive = 2 + sum(1 for r in sp if r <= 50) - sum(1 for d in g['deaths'] if d[1] == s and d[0] <= 50)
        return nat, sp50, xn, alive, min(sp, default=-1)
    print(g['opp'][:8], g['bot_name'], g['gid'], j['completedAt'][5:16], te, g['result'][0], '|', *st(1), '|', *st(0))
