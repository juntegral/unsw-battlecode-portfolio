import json, datetime
rows = [json.loads(l) for l in open("~/01. Project/개인 프로젝트/unsw-swarm/data/online/requests.jsonl")]
print(len(rows))
import collections
c = collections.Counter()
for r in rows:
    t = datetime.datetime.fromisoformat(r['at'].replace('Z', '+00:00')) + datetime.timedelta(hours=9)
    c[(t.strftime('%m-%d'), 'ranked' if r.get('ranked') else ('dev' if r.get('dev') else 'normal'))] += 1
for k in sorted(c):
    print(k, c[k])
print('--- ranked requests')
for r in rows:
    if not r.get('ranked'):
        continue
    t = datetime.datetime.fromisoformat(r['at'].replace('Z', '+00:00')) + datetime.timedelta(hours=9)
    print(t.strftime('%m-%d %H:%M'), r['teamId'], r['name'], 'rank', r.get('rank'), 'elo', r.get('elo'), 'status', r.get('status'), 'ids', (r.get('ids') or [None])[0], '-', (r.get('ids') or [None])[-1], 'active', r.get('activeSubmission'), '|', (r.get('purpose') or '')[:90])
print('--- first/last')
print(rows[0]['at'], rows[-1]['at'])
