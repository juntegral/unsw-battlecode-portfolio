import json
B = '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/trophy-sonnet/'
D = json.load(open(B + 'trophy.json'))
print('ver opp gid | us [count,total,longest,queenLen] at r25 r50 r75')
for g in sorted(D, key=lambda g: (g['bot_name'], g['opp'], g['gid'])):
    if g['bot_name'] not in ('one8', 'one10', 'one11', 'one12', 'one13', 'one14'):
        continue
    s = g['snaps']
    print(g['bot_name'], g['opp'][:6], g['gid'], '|', *[('r%s %s' % (r, s[r][0][:4] if r in s else '-')) for r in ('25', '50', '75')],
          '| th', *[('r%s %s' % (r, s[r][1][:4] if r in s else '-')) for r in ('50',)])
