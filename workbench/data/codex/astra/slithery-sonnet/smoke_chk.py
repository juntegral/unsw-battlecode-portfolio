import json
D = '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/slithery-sonnet/'
rows = [json.loads(l) for l in open(D + 'scan.jsonl')]
rk = {r['gid'] for r in rows if r['src'] == 'ranked'}
sm = [r for r in rows if r['src'] != 'ranked']
print(len(sm), sum(1 for r in sm if r['gid'] in rk))
for r in sm:
    print(r['gid'], r['src'], r['map'], r['result'], r['opp'], r['bot'], r['ends'][0][3], r['ends'][1][3], r['how'])
