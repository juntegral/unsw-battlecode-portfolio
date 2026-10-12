import json, glob
from collections import Counter
ROOT = '~/01. Project/개인 프로젝트/unsw-swarm/'
c = Counter()
rk = {}
for f in glob.glob(ROOT + 'data/online/live-one1/b*/game-*.json') + glob.glob(ROOT + 'data/online/smoke/one1[1-5]-*-old/game-*.json'):
    j = json.load(open(f))
    rk[j['id']] = (j.get('ranked'), f.split('/')[-3] if 'smoke' in f else 'live')
json.dump({str(k): v for k, v in rk.items()}, open(ROOT + 'data/codex/astra/slithery-sonnet/rankedflag.json', 'w'))
D = ROOT + 'data/codex/astra/slithery-sonnet/'
rows = [json.loads(l) for l in open(D + 'scan.jsonl')]
seen = set()
for r in rows:
    if r['gid'] in seen:
        continue
    seen.add(r['gid'])
    c[(r['map'], rk.get(r['gid'], ('?',))[0], r['result'])] += 1
for k in sorted(c, key=str):
    print(k, c[k])
