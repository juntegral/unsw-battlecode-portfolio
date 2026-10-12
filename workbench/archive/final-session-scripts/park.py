import json, collections
rows = [json.loads(l) for l in open("~/01. Project/개인 프로젝트/unsw-swarm/data/online/park/log.jsonl")]
print(len(rows), rows[0]['at'], rows[-1]['at'])
days = collections.OrderedDict()
for r in rows:
    days.setdefault(r['at'][:10], []).append(r)
for d, rs in days.items():
    ra = [x['active']['rating'] for x in rs if x.get('active')]
    ids = sorted({x['active']['id'] for x in rs if x.get('active')})
    print(d, len(rs), 'first', rs[0]['at'][11:16], rs[0]['active'], 'last', rs[-1]['at'][11:16], rs[-1]['active'], 'min', min(ra), 'max', max(ra), ids)
