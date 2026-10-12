import json
rows = [json.loads(l) for l in open("~/01. Project/개인 프로젝트/unsw-swarm/data/online/park/log.jsonl")]
prev = None
print("== active id changes")
for r in rows:
    a = r.get('active')
    if not a:
        continue
    if prev != a['id']:
        print(r['at'][:19], a, 'parked', r.get('parked'))
        prev = a['id']
print("== hourly samples 10-08 12:00 onward (first row each hour)")
seen = set()
for r in rows:
    k = r['at'][:13]
    if r['at'] < '2026-10-08T12' or k in seen:
        continue
    seen.add(k)
    a = r.get('active')
    print(r['at'][:16], a['id'], 'v%s' % a['version'], a['rating'], 'parked', (r.get('parked') or {}).get('id'), (r.get('parked') or {}).get('rating'))
print("== last row", rows[-1])
