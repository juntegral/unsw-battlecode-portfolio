import json, sys, glob, os
from collections import Counter
B = '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet/'
D = json.load(open(B + 'trophy.json'))
V = ['one8', 'one9', 'one10', 'one11', 'one12', 'one13', 'one14', 'one15']
print('gid ver opp res last | us eats r35 by origin n/own/foe | them r35 n/own/foe | r50 us n/own/foe them n/own/foe | pace us n/rnd to min(last,100)')
for g in sorted(D, key=lambda g: (g['bot_name'], g['opp'], g['gid'])):
    if g['bot_name'] not in V:
        continue
    e = g['eats']
    def c(s, r):
        k = Counter(x[3] for x in e if x[0] <= r and x[1] == s)
        return '%d/%d/%d' % (k['n'], k['own'], k['foe'])
    m = min(g['last'], 100)
    print(g['gid'], g['bot_name'], g['opp'][:6], g['result'][0], g['last'], '|', c(0, 35), '|', c(1, 35), '|', c(0, 50), c(1, 50), '|', '%.2f' % (sum(1 for x in e if x[1] == 0 and x[0] <= m and x[3] == 'n') / m), 'oppbot', g.get('bot'))
