import json, datetime
rows = [json.loads(l) for l in open("~/01. Project/개인 프로젝트/unsw-swarm/data/online/submissions.jsonl")]
print(len(rows), rows[0]['at'], rows[-1]['at'])
for r in rows:
    t = datetime.datetime.fromisoformat(r['at'].replace('Z', '+00:00')) + datetime.timedelta(hours=9)
    if t < datetime.datetime(2026, 10, 8, 12, 0, tzinfo=datetime.timezone.utc):
        continue
    print(t.strftime('%m-%d %H:%M:%S'), r.get('action'), r.get('id'), r.get('name'), 'prev', r.get('previous'), 'zip', r.get('serverZipMatch'), (r.get('desc') or '')[:70])
