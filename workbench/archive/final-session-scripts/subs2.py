import json, datetime, collections
rows = [json.loads(l) for l in open("~/01. Project/개인 프로젝트/unsw-swarm/data/online/submissions.jsonl")]
c = collections.Counter()
for r in rows:
    t = datetime.datetime.fromisoformat(r['at'].replace('Z', '+00:00')) + datetime.timedelta(hours=9)
    c[(t.strftime('%m-%d'), r.get('action'))] += 1
for k in sorted(c):
    print(k, c[k])
